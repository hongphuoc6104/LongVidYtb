"""Parallel canonical TTS requests with assembly/mastering exclusively on Colab."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import threading
import time
from typing import Callable

from .client import Client
from .protocol import file_hash, stamp


def request_shards(request: dict, scenes_per_shard: int = 4) -> list[dict]:
    """Preserve every sentence, language span, pause and hook while remapping item indices."""
    scene_ids = list(dict.fromkeys(part['scene_id'] for part in request['segments']))
    shards = []
    for offset in range(0, len(scene_ids), scenes_per_shard):
        wanted = set(scene_ids[offset:offset + scenes_per_shard])
        shard = copy.deepcopy(request)
        for key in ('assemble', 'assembly_settings', 'support_files', 'request_id', 'pause_plan'):
            shard.pop(key, None)
        for key in ('segments', 'english', 'secondary'):
            shard[key] = [part for part in shard.get(key, []) if part['scene_id'] in wanted]
        shard['spinoff_hooks'] = shard.get('spinoff_hooks', []) if offset == 0 else []
        indexes = set()
        for part in shard['segments'] + shard['secondary']:
            indexes.update(part['items'])
        indexes.update(part['item'] for part in shard['english'] + shard['spinoff_hooks'])
        indexes = sorted(indexes)
        remap = {old: new for new, old in enumerate(indexes)}
        shard['items'] = [shard['items'][i] for i in indexes]
        for part in shard['segments'] + shard['secondary']:
            part['items'] = [remap[i] for i in part['items']]
        for part in shard['english'] + shard['spinoff_hooks']:
            part['item'] = remap[part['item']]
        identity = copy.deepcopy(shard)
        for profile in identity['profiles'].values():
            profile.pop('local_wav', None)
        shard['request_id'] = stamp(identity)
        shards.append(shard)
    return shards


def prepare_assembly(request: dict, results: list[dict], folder: Path) -> dict:
    """Copy validated bytes/metadata for upload; no waveform processing on the desktop."""
    folder.mkdir(parents=True, exist_ok=True)
    assembled = copy.deepcopy(request)
    parts, english, secondary, hooks, spans, batches = [], [], [], [], [], []
    result_meta = None
    files = []

    def copy_part(part: dict, source: Path, prefix: str, index: int) -> dict:
        result = copy.deepcopy(part)
        path = source / part['path']
        if Path(part['path']).name != part['path'] or not path.is_file():
            raise ValueError('Invalid shard output path')
        target = f'{prefix}-{index:04d}.wav'
        dest = folder / target
        shutil.copyfile(path, dest)
        files.append({'name': target, 'target': target, 'local_path': str(dest), 'sha256': file_hash(dest)})
        result['path'] = target
        return result

    def metadata(name: str, data: dict) -> None:
        path = folder / ('prepared-' + name)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        files.append({'name': path.name, 'target': name, 'local_path': str(path), 'sha256': file_hash(path)})

    for item in sorted(results, key=lambda item: item['index']):
        source = Path(item['out'])
        meta = json.loads((source / 'tts-result.json').read_text())
        result_meta = result_meta or copy.deepcopy(meta)
        start = len(parts)
        parts.extend(copy_part(part, source, 'segment', start + i)
                     for i, part in enumerate(meta['segments']))
        start = len(hooks)
        hooks.extend(copy_part(part, source, 'spinoff-hook', start + i)
                     for i, part in enumerate(meta.get('spinoff_hooks', [])))
        spans.extend(meta.get('english_spans', []))
        batches.extend(meta.get('batches', []))
        for name, key, dest, prefix in [('en-result.json', 'scenes', english, 'en-segment'),
                                         ('secondary-result.json', 'segments', secondary, 'secondary')]:
            path = source / name
            if path.is_file():
                extra = json.loads(path.read_text())
                start = len(dest)
                dest.extend(copy_part(part, source, prefix, start + i) for i, part in enumerate(extra[key]))
    if result_meta is None or [(x['scene_id'], x['text']) for x in parts] != [
            (x['scene_id'], x['text']) for x in request['segments']]:
        raise ValueError('Parallel synthesis changed sentence order')
    result_meta.update(segments=parts, english_spans=spans, batches=batches,
                       spinoff_hooks=hooks, shard_requests=[item['request_id'] for item in results])
    metadata('tts-result.json', result_meta)
    if english:
        metadata('en-result.json', {'voice': request['profiles']['en']['voice'],
                                    'engine': 'colab-omnivoice', 'scenes': english})
    if secondary:
        metadata('secondary-result.json', {'segments': secondary})
    assembled['prepared_audio'] = files
    identity = copy.deepcopy(assembled)
    identity.pop('request_id', None)
    for profile in identity['profiles'].values():
        profile.pop('local_wav', None)
    for key in ('support_files', 'prepared_audio'):
        for record in identity.get(key, []):
            record.pop('local_path', None)
    assembled['request_id'] = stamp(identity)
    return assembled


def synthesize(root: Path, cfg: dict, request: dict, out: Path, cache: Path,
               before_submit: Callable | None = None) -> None:
    """Production entry shared by explicit-output jobs; retain durable shard caches on failure."""
    from . import accounts
    from .pool_manager import ColabPoolDispatcher, ColabPoolManager

    options = cfg['colab_tts']
    max_workers = max(1, int(options.get('max_workers', 3)))
    selection = options.get('management_session', {})
    exact = selection.get('runtime_bindings', {}).get('colab') or options.get('account') not in ('auto', 'auto-idle')
    shards = request_shards(request, max(1, int(options.get('scenes_per_shard', 4))))
    if exact or not options.get('parallel', True) or len(shards) <= 1 or max_workers == 1:
        Client(root, cfg).synthesize(request, out, cache, before_submit=before_submit)
        return
    candidates = accounts.select_pool(max_accounts=max_workers, role='tts')
    if selection.get('pool'):
        candidates = [account for account in candidates if 'colab:' + account in selection['pool']]
    if len(candidates) < 2:
        Client(root, cfg).synthesize(request, out, cache, before_submit=before_submit)
        return
    manager = ColabPoolManager(accounts_config=[{'id': name, 'role': 'tts'} for name in candidates])
    lock = threading.Lock()
    owners = []
    started = time.monotonic()

    def run(worker, task):
        shard_cfg = copy.deepcopy(cfg)
        shard_cfg['colab_tts'].update(account=worker.account_id, session=worker.session_name)
        shard_cfg['colab_tts']['_session_explicit'] = True
        dest = out / 'shards' / str(task['index'])
        dest.mkdir(parents=True, exist_ok=True)
        with lock:
            owners.append(worker.account_id)
        client = Client(root, shard_cfg)
        client.synthesize(task['request'], dest, cache / 'shards' / str(task['index']), before_submit=before_submit)
        return {**task, 'out': str(dest), 'account': client.account, 'session': client.session,
                'request_id': task['request']['request_id']}

    tasks = [{'index': index, 'request': shard} for index, shard in enumerate(shards)]
    results = ColabPoolDispatcher(manager).dispatch_all(tasks, run, max_concurrency=max_workers, role='tts')
    prepared = prepare_assembly(request, results, out / 'prepared')
    from account_budget import Budgets
    budgets = Budgets(cfg['colab_tts'].get('management_store'))
    ordered_results = sorted(results, key=lambda r: (0 if r['account'] in owners else 1, r['index']))
    chosen = next(
        (
            r for r in ordered_results
            if not budgets.snapshot('colab:' + r['account'])['blocks'].get('colab')
        ),
        ordered_results[0],
    )
    collector_cfg = copy.deepcopy(cfg)
    collector_cfg['colab_tts'].update(account=chosen['account'], session=chosen['session'], _session_explicit=True)
    Client(root, collector_cfg).synthesize(prepared, out, cache / 'assembly', before_submit=before_submit)
    (out / 'parallel-dispatch.json').write_text(json.dumps({
        'version': 1, 'shards': len(shards), 'accounts': sorted(set(owners)),
        'elapsed_seconds': time.monotonic() - started, 'assembly_location': 'colab',
        'source_request_id': request['request_id'], 'assembly_request_id': prepared['request_id'],
    }, indent=2))
