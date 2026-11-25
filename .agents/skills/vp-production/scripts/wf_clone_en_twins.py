"""Turnkey `/run-workflow` orchestrator: parallel VN -> EN twin localization + sequential render.

Args (passed via `Args`):
    spec_paths: list[str] of existing Vietnamese `short_spec.json` files to adapt into their EN twins.
    render: bool (default False; when True, runs sequential `./vp short` via `pipeline()`).
"""

import json
from pathlib import Path

ROOT = Path(WORKSPACES[0]) if WORKSPACES else Path.cwd()
CLONE_SCHEMA = {
    "type": "object",
    "properties": {
        "source_spec": {"type": "string"},
        "en_channel_id": {"type": "string"},
        "en_spec_path": {"type": "string"},
        "en_title": {"type": "string"},
        "ready": {"type": "boolean"},
        "notes": {"type": "string"},
    },
    "required": ["source_spec", "en_channel_id", "en_spec_path", "en_title", "ready", "notes"],
}
RENDER_SCHEMA = {
    "type": "object",
    "properties": {
        "en_channel_id": {"type": "string"},
        "en_spec_path": {"type": "string"},
        "mp4_path": {"type": "string"},
        "rendered": {"type": "boolean"},
    },
    "required": ["en_channel_id", "en_spec_path", "mp4_path", "rendered"],
}


def _build_clone_prompt(spec_path: str) -> str:
    return (
        f"Adapt VN Short spec `{spec_path}` to its EN twin\n\n"
        f"1. Run `./vp clone-en --spec {spec_path}` to scaffold the twin English spec onto `sys/runs/<en_job_id>/short_spec.json`.\n"
        "2. Read the target EN twin channel's 3-pillar playbook `sys/channels/<en_cid>/playbook/{overview.md,content.md,visual.md,pacing.md}`.\n"
        "3. Localize into natural native spoken American English (NOT robotic translation): crisp curiosity `youtube_title <= 55` chars (zero `Part 1`/`Ep 1`), Beat 0 hook <= 18 words with 0 `[pause:...]` tags, spell out digits/units in `beats[].tts_text`, uppercase banner <= 4 words, natural A/B close question.\n"
        "4. Validate via `validate_v4_short_spec` (`[]`) and confirm visual prompts match `.agents/skills/vp-visual-fx/SKILL.md`.\n"
        "5. Return the verified EN spec path and title."
    )


raw = dict(args or {})
spec_paths = [str(p).strip() for p in (raw.get("spec_paths") or []) if str(p).strip()]
render_enabled = bool(raw.get("render", False))

if not spec_paths:
    raise ValueError("Provide non-empty `spec_paths` list in workflow Args (e.g. ['sys/runs/.../short_spec.json']).")

phase("1. Parallel VN -> EN Native Localization")
log(f"Localizing {len(spec_paths)} VN Short spec(s) onto symmetric EN twin channels...")
cloned = await parallel(
    spec_paths,
    lambda sp: agent(
        _build_clone_prompt(sp),
        schema=CLONE_SCHEMA,
        role=f"Clone EN {Path(sp).parent.name}",
    ),
)

for item in cloned:
    log(f"  - [{item['en_channel_id']}] ready={item['ready']} title={item['en_title']!r} -> {item['en_spec_path']}")

rendered = []
if render_enabled:
    ready_items = [c for c in cloned if c.get("ready") and c.get("en_spec_path")]
    phase("2. Sequential EN Short Render")
    log(f"Rendering {len(ready_items)} EN Short(s) sequentially via pipeline()...")
    rendered = await pipeline(
        ready_items,
        lambda c: agent(
            f"Render EN Short `{c['en_channel_id']}`\n\n"
            f"Run `./vp short --spec {c['en_spec_path']} --visual-mode hybrid_2k --render-mode single_pass`, verify `ffprobe` + teardown (`./pipeline flow status`, `./pipeline colab pool-status`), and return the final MP4 path.",
            schema=RENDER_SCHEMA,
            role=f"Render {c['en_channel_id']}",
        ),
    )

print(json.dumps({"cloned": cloned, "renders": rendered}, ensure_ascii=False, indent=2))
