"""Read an existing Flow page without reloading, generation, cookie changes or guard injection."""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import sys
import urllib.error
from pathlib import Path

import websockets

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from flow_cdp.cdp_direct_client import get_flow_target


async def inspect(port: int, output: Path, reuse_first: bool = False, open_media_menu: bool = False) -> dict:
    target = get_flow_target(port)
    output.mkdir(parents=True, exist_ok=True)
    async with websockets.connect(target['webSocketDebuggerUrl'], max_size=32 * 1024 * 1024) as ws:
        async def call(key: int, method: str, params: dict) -> dict:
            await ws.send(json.dumps({'id': key, 'method': method, 'params': params}))
            async with asyncio.timeout(15):
                while True:
                    reply = json.loads(await ws.recv())
                    if reply.get('id') == key:
                        if reply.get('error'):
                            raise RuntimeError(str(reply['error']))
                        if reply['result'].get('exceptionDetails'):
                            raise RuntimeError('FLOW_UI_ACTION_FAILED: ' + reply['result']['exceptionDetails'].get('text', 'script exception'))
                        return reply['result']

        if open_media_menu or reuse_first:
            async with asyncio.timeout(35):
                while True:
                    ready = await call(12, 'Runtime.evaluate', {'expression': 'Boolean(document.querySelector(\'button[aria-label="Add media menu"]\'))', 'returnByValue': True})
                    if ready['result'].get('value'):
                        break
                    await asyncio.sleep(0.5)
        if open_media_menu:
            await call(11, 'Runtime.evaluate', {'expression': 'document.querySelector(\'button[aria-label="Add media menu"]\').click()'})
        if reuse_first:
            await call(10, 'Runtime.evaluate', {'expression': "document.querySelector('button[aria-label=\"Reuse prompt\"]').click()"})
        snapshot = await call(1, 'Runtime.evaluate', {
            'expression': "JSON.stringify({url:location.href,text:document.body.innerText,editors:[...document.querySelectorAll('textarea,[contenteditable=true]')].filter(x=>x.getBoundingClientRect().width>0&&getComputedStyle(x).visibility!=='hidden').map(x=>x.value||x.innerText),images:[...document.querySelectorAll('img')].map(x=>({src:x.currentSrc,alt:x.alt,width:x.width,height:x.height})),inputs:[...document.querySelectorAll('input')].map(x=>({type:x.type,accept:x.accept})),buttons:[...document.querySelectorAll('button')].map(x=>({text:x.innerText,label:x.getAttribute('aria-label')}))})",
            'returnByValue': True,
        })
        state = json.loads(snapshot['result']['value'])
        screenshot = await call(2, 'Page.captureScreenshot', {'format': 'png'})
        (output / 'page.png').write_bytes(base64.b64decode(screenshot['data']))
        state.update(port=port, generation_submitted=False, navigation_performed=False)
        (output / 'page.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
        return state


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--open-media-menu', action='store_true', help='Open the existing Add media menu without uploading or generating.')
    parser.add_argument('--reuse-first', action='store_true', help='Populate the composer from the first visible Reuse prompt button, without generating.')
    args = parser.parse_args()
    try:
        state = asyncio.run(inspect(args.port, args.out, args.reuse_first, args.open_media_menu))
    except (OSError, urllib.error.URLError, RuntimeError) as exc:
        print(json.dumps({'status': 'blocked', 'generation_submitted': False, 'reason': str(exc)}))
        raise SystemExit(2) from exc
    print(json.dumps({'url': state['url'], 'inputs': state['inputs'], 'buttons': state['buttons'][-25:],
                      'editors': [x[:300] for x in state['editors']], 'images': [{**x, 'src': x['src'][:180]} for x in state['images'][:4]], 'text': state['text'][:1500], 'output': str(args.out.resolve())}, ensure_ascii=False))


if __name__ == '__main__':
    main()
