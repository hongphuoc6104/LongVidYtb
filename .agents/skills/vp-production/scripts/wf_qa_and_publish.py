"""Turnkey `/run-workflow` orchestrator: 3-angle parallel QA council + optional Studio publish.

Args (passed via `Args`):
    channel: str channel ID (e.g. "su_ke_lai", "ban_do_quyen_luc").
    job_dir: str path to rendered deliverables directory (e.g. "video/<job_id>").
    spec_path: str optional path to `short_spec.json` / `content.json`.
    auto_publish: bool (default False; when True and all 3 angles pass, triggers `./vp publish`).
"""

import json

QA_SCHEMA = {
    "type": "object",
    "properties": {
        "angle": {"type": "string"},
        "passed": {"type": "boolean"},
        "findings": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["angle", "passed", "findings"],
}
PUBLISH_SCHEMA = {
    "type": "object",
    "properties": {
        "published": {"type": "boolean"},
        "video_url": {"type": "string"},
        "notes": {"type": "string"},
    },
    "required": ["published", "video_url", "notes"],
}

ANGLES = [
    {
        "angle": "Fact & Script Gate",
        "instructions": (
            "Audit fact grounding, Beat 0 <= 18 syllables with 0 pause tags, zero canned AI fillers, "
            "zero forbidden CTAs ('like/share/subscribe'), and final-15% debate ending + channel bridge."
        ),
    },
    {
        "angle": "Media & Technical Gate",
        "instructions": (
            "Inspect real deliverables via ffprobe, audio ebur128 (-11.0 LUFS / <= -1.0 dBTP), "
            "frame inspection (clean edges, bottom-right watermark W-w-36:H-h-36, >= 132px subtitles), and thumbnail < 2MB."
        ),
    },
    {
        "angle": "Packaging & Debate Loop Gate",
        "instructions": (
            "Check channel 3-pillar playbook alignment, youtube_title <= 55 chars (zero P1/P2 prefix on Shorts), "
            ".srt captions presence, and mirrored 2-choice creator pinned comment."
        ),
    },
]

raw = dict(args or {})
channel = str(raw.get("channel") or "").strip()
job_dir = str(raw.get("job_dir") or "").strip()
spec_path = str(raw.get("spec_path") or "").strip()
auto_publish = bool(raw.get("auto_publish", False))

if not channel or not job_dir:
    raise ValueError("Provide `channel` and `job_dir` in workflow Args.")

phase("1. Parallel 3-Angle QA Council")
log(f"Running 3 independent QA reviewers for channel={channel}, job_dir={job_dir}...")
verdicts = await parallel(
    ANGLES,
    lambda a: agent(
        f"QA [{a['angle']}] for `{channel}`\n\n"
        f"Target outputs: `job_dir={job_dir}`, `spec_path={spec_path or '(check job dir)'}`.\n"
        f"1. Read `sys/channels/{channel}/playbook/{{overview.md,content.md,visual.md,pacing.md}}`.\n"
        f"2. Perform this audit strictly: {a['instructions']}\n"
        "3. Report `passed: true` ONLY when verified directly on real files/tool output.",
        schema=QA_SCHEMA,
        role=a["angle"],
    ),
)

all_passed = all(v.get("passed") for v in verdicts)
for v in verdicts:
    log(f"  - [{v['angle']}] passed={v['passed']} findings={v['findings']}")

publish_result = None
if all_passed and auto_publish:
    phase("2. YouTube Studio CDP Publish")
    publish_result = await agent(
        f"Publish `{channel}` deliverables in `{job_dir}`\n\n"
        "Read `.agents/skills/vp-production/references/new-episode-checklist.md` and `.agents/rules/gpu-headless-chrome.md`.\n"
        f"Publish via `./vp publish --channel {channel}` with custom thumbnail (<2MB), subtitles, pinned creator comment, and verify after page reload.",
        schema=PUBLISH_SCHEMA,
        role=f"Publish {channel}",
    )
    log(f"Publish result: {publish_result}")
else:
    phase("2. QA Summary")
    log(f"all_passed={all_passed} auto_publish={auto_publish}; skipping publish step.")

print(json.dumps({"all_passed": all_passed, "verdicts": verdicts, "publish": publish_result}, ensure_ascii=False, indent=2))
