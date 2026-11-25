"""Turnkey `/run-workflow` orchestrator: parallel Short V4 spec creation + sequential safe-IP render.

Args (passed via `Args`):
    channels: list[str] or wave selector string ("open", "wave_0", "wave_1", ...). Default: "open".
    items: optional explicit list of {"channel": str, "topic": str}.
    count_per_channel: int (default 1 when channels is used).
    mode: "viral_fast_loop_short" (16 beats, default) or "serialized_detail_short" (20 beats).
    render: bool (default False; when True, runs sequential `./vp short` via `pipeline()`).
"""

import json
from pathlib import Path

ROOT = Path(WORKSPACES[0]) if WORKSPACES else Path.cwd()
SPEC_SCHEMA = {
    "type": "object",
    "properties": {
        "channel_id": {"type": "string"},
        "job_id": {"type": "string"},
        "title": {"type": "string"},
        "spec_path": {"type": "string"},
        "ready": {"type": "boolean"},
        "summary": {"type": "string"},
    },
    "required": ["channel_id", "job_id", "title", "spec_path", "ready", "summary"],
}
RENDER_SCHEMA = {
    "type": "object",
    "properties": {
        "channel_id": {"type": "string"},
        "job_id": {"type": "string"},
        "mp4_path": {"type": "string"},
        "rendered": {"type": "boolean"},
        "notes": {"type": "string"},
    },
    "required": ["channel_id", "job_id", "mp4_path", "rendered", "notes"],
}


def _resolve_tasks(raw_args: dict) -> list[dict]:
    explicit_items = raw_args.get("items") or []
    mode = str(raw_args.get("mode") or "viral_fast_loop_short")
    if explicit_items:
        return [
            {
                "channel": str(item["channel"]),
                "topic": str(item.get("topic") or "").strip(),
                "mode": str(item.get("mode") or mode),
                "slot": idx + 1,
            }
            for idx, item in enumerate(explicit_items)
        ]

    lc_path = ROOT / "sys" / "channels" / "fleet_lifecycle.json"
    lc = json.loads(lc_path.read_text(encoding="utf-8")) if lc_path.is_file() else {}
    ch_map = lc.get("channels") or {}
    waves = lc.get("waves") or {}

    raw_channels = raw_args.get("channels", "open")
    if isinstance(raw_channels, str):
        sel = raw_channels.strip().lower().replace("-", "_")
        if sel == "open":
            selected = [cid for cid, e in ch_map.items() if e.get("state") in ("ACTIVE", "CANARY")]
        elif sel in waves:
            selected = list(waves[sel])
        elif sel in ch_map:
            selected = [sel]
        else:
            selected = ["su_ke_lai"]
    elif isinstance(raw_channels, list):
        selected = [str(c).strip() for c in raw_channels if str(c).strip()]
    else:
        selected = ["su_ke_lai"]

    count = max(1, min(int(raw_args.get("count_per_channel", 1) or 1), 6))
    tasks = []
    for cid in selected:
        for slot in range(1, count + 1):
            tasks.append({"channel": cid, "topic": "", "mode": mode, "slot": slot})
    return tasks


def _build_spec_prompt(task: dict) -> str:
    cid = task["channel"]
    mode = task["mode"]
    slot = task["slot"]
    topic_line = f'Required topic: "{task["topic"]}"' if task["topic"] else "Select a fresh, unproduced high-curiosity topic fitting the channel's niche."
    return (
        f"Author Short V4 spec #{slot} for `{cid}`\n\n"
        f"1. Read `sys/channels/{cid}/playbook/{{overview.md,content.md,visual.md,pacing.md}}` (or run `./vp playbook {cid} --pillar all`).\n"
        "2. Also follow `.agents/skills/vp-content-studio/SKILL.md` and `.agents/skills/vp-visual-fx/SKILL.md`.\n"
        f"3. {topic_line}\n"
        f"4. Scaffold via `./vp scaffold-short --channel {cid} --topic \"<TITLE_UNDER_55_CHARS>\" --mode {mode}`.\n"
        "5. Replace any placeholder copy in the generated `short_spec.json` with verified facts (no fabricated metrics, Beat 0 <= 18 syllables, 0 `[pause:...]` in Beat 0, banner <= 4 UPPERCASE words, natural close question + channel bridge in final 15%, zero 'like/share/subscribe', strictly positive visual framing matching the channel visual style).\n"
        "6. Validate via `PYTHONPATH=sys sys/.venv/bin/python -c \"from short_engine.archetype_packs import validate_v4_short_spec; import json; print(validate_v4_short_spec(json.load(open('<SPEC_PATH>'))))\"` (must return `[]`).\n"
        "7. Return `ready: true` only after validation passes cleanly."
    )


def _build_render_prompt(spec: dict) -> str:
    cid = spec["channel_id"]
    spec_path = spec["spec_path"]
    return (
        f"Render 2K Short MP4 for `{cid}` (`{spec['job_id']}`)\n\n"
        "Obey `.agents/skills/vp-flow-cdp/SKILL.md`, `.agents/skills/vp-colab-bridge/SKILL.md`, and `.agents/rules/gpu-headless-chrome.md`.\n"
        f"1. Run `./vp short --spec {spec_path} --visual-mode hybrid_2k --render-mode single_pass`.\n"
        "2. Verify output MP4 via `ffprobe` (`1440x2560` @ `30fps`, `-11.0 LUFS / -1.0 dBTP` WAV, watermark `W-w-36:H-h-36`) and inspect sample frames.\n"
        "3. Verify clean teardown: `./pipeline flow status` (`listening_count == 0`) and `./pipeline colab pool-status`.\n"
        "4. Return rendered file path and verification notes."
    )


raw = dict(args or {})
tasks = _resolve_tasks(raw)
render_enabled = bool(raw.get("render", False))

phase("1. Parallel Spec & Linter Authoring")
log(f"Dispatching {len(tasks)} parallel Short V4 spec agent(s) (render={render_enabled})...")
spec_results = await parallel(
    tasks,
    lambda t: agent(
        _build_spec_prompt(t),
        schema=SPEC_SCHEMA,
        role=f"Spec {t['channel']} #{t['slot']}",
    ),
)

for r in spec_results:
    log(f"  - [{r['channel_id']}] ready={r['ready']} title={r['title']!r} -> {r['spec_path']}")

render_results = []
if render_enabled:
    ready_specs = [r for r in spec_results if r.get("ready") and r.get("spec_path")]
    phase("2. Sequential Safe-IP Flow & Colab T4 Render")
    log(f"Running {len(ready_specs)} render job(s) sequentially via pipeline() to respect Flow IP & GPU caps...")
    render_results = await pipeline(
        ready_specs,
        lambda s: agent(
            _build_render_prompt(s),
            schema=RENDER_SCHEMA,
            role=f"Render {s['channel_id']} ({s['job_id']})",
        ),
    )
    for rr in render_results:
        log(f"  - [{rr['channel_id']}] rendered={rr['rendered']} mp4={rr['mp4_path']}")

print(json.dumps({"specs": spec_results, "renders": render_results}, ensure_ascii=False, indent=2))
