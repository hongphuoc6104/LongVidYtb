"""Turnkey `/run-workflow` orchestrator: Series-First Discovery -> Parallel Episode Scripts -> Batch Render Later.

Designs one cohesive multi-episode Series blueprint first (sweet spot `3–5` Shorts,
configurable up to `15` for major arcs; defaults to `serialized_detail_short` `20` beats),
writes all episode `short_spec.json` files in parallel from that shared blueprint (`render=False`
by default so the user reviews scripts first), and optionally batch-renders sequentially via `pipeline()`.

Args (passed via `Args`):
    channel: target channel ID (default: active channel from `fleet_lifecycle.json`).
    series_topic: optional big campaign/arc idea; empty = discover best unproduced Series arc.
    episodes: `"auto_3_5"` (AI picks 3, 4, or 5 Shorts to fit the story arc) or int `2..15`.
    existing_series_id: optional existing series ID from `multi_series_*.json` or `series_plans/*.json`
        to author only its missing/unscripted episodes.
    mode: `"serialized_detail_short"` (20 beats, default) or `"viral_fast_loop_short"` (16 beats).
    render: bool (default `False`; when `True`, runs sequential `./vp short` via `pipeline()`).
"""

import json
from pathlib import Path

ROOT = Path(WORKSPACES[0]) if WORKSPACES else Path.cwd()

SERIES_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "channel_id": {"type": "string"},
        "series_id": {"type": "string"},
        "series_title": {"type": "string"},
        "historical_span": {"type": "string"},
        "plan_path": {"type": "string"},
        "episode_count": {"type": "integer"},
        "shared_facts": {"type": "array", "items": {"type": "string"}},
        "episodes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "series_order": {"type": "integer"},
                    "episode_code": {"type": "string"},
                    "job_id": {"type": "string"},
                    "youtube_title": {"type": "string"},
                    "thumbnail_text": {"type": "string"},
                    "beat_0_hook": {"type": "string"},
                    "central_paradox": {"type": "string"},
                    "five_act_summary": {"type": "string"},
                    "next_episode_bridge": {"type": "string"},
                    "debate_option_a": {"type": "string"},
                    "debate_option_b": {"type": "string"},
                    "debate_question": {"type": "string"},
                },
                "required": [
                    "series_order",
                    "episode_code",
                    "job_id",
                    "youtube_title",
                    "thumbnail_text",
                    "beat_0_hook",
                    "central_paradox",
                    "five_act_summary",
                    "next_episode_bridge",
                    "debate_option_a",
                    "debate_option_b",
                    "debate_question",
                ],
            },
        },
    },
    "required": [
        "channel_id",
        "series_id",
        "series_title",
        "historical_span",
        "plan_path",
        "episode_count",
        "shared_facts",
        "episodes",
    ],
}

EPISODE_SPEC_SCHEMA = {
    "type": "object",
    "properties": {
        "channel_id": {"type": "string"},
        "series_id": {"type": "string"},
        "series_order": {"type": "integer"},
        "job_id": {"type": "string"},
        "title": {"type": "string"},
        "spec_path": {"type": "string"},
        "ready": {"type": "boolean"},
        "summary": {"type": "string"},
    },
    "required": ["channel_id", "series_id", "series_order", "job_id", "title", "spec_path", "ready", "summary"],
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


def _resolve_channel(raw_args: dict) -> str:
    ch = str(raw_args.get("channel") or "").strip().lower().replace("-", "_")
    if ch and ch != "auto":
        return ch
    lc_path = ROOT / "sys" / "channels" / "fleet_lifecycle.json"
    if lc_path.is_file():
        lc = json.loads(lc_path.read_text(encoding="utf-8"))
        for cid, entry in (lc.get("channels") or {}).items():
            if isinstance(entry, dict) and entry.get("state") == "ACTIVE":
                return cid
    return "su_ke_lai"


def _resolve_episode_directive(raw_ep) -> str:
    if raw_ep is None or str(raw_ep).strip().lower() in ("", "auto", "auto_3_5"):
        return (
            "Choose the tightest sweet-spot count of `3`, `4`, or `5` episodes "
            "that fits the story arc cleanly without stretching filler or rushing twists."
        )
    try:
        n = max(2, min(int(raw_ep), 15))
        return f"Design EXACTLY `{n}` tightly connected non-redundant episodes (`series_order` 1..{n})."
    except (TypeError, ValueError):
        return "Choose `3`, `4`, or `5` episodes that fit the story arc cleanly."


def _build_series_plan_prompt(
    channel_id: str,
    series_topic: str,
    episode_directive: str,
    existing_series_id: str,
    mode: str,
) -> str:
    existing_note = (
        f"PRIORITY EXISTING SERIES: Inspect `sys/channels/{channel_id}/multi_series_*.json` and `sys/channels/{channel_id}/series_plans/` "
        f"for `existing_series_id = '{existing_series_id}'`. Plan ONLY its missing/unscripted episodes into the Series Plan.\n"
        if existing_series_id
        else (
            f"Series Topic Directive: \"{series_topic}\"\n"
            if series_topic
            else (
                "No fixed series topic given — audit existing `video/`, `sys/runs/`, and any `multi_series_*.json` on disk, "
                "pick the highest-potential unproduced multi-part Series/campaign fitting this channel's niche & winning viral pillars, "
                "and make sure zero episode duplicates an already-produced video.\n"
            )
        )
    )
    beat_desc = "20 beats (~95–105s, 5 Acts × 4 beats)" if mode == "serialized_detail_short" else "16 beats (~54–72s)"
    return (
        f"Phase 1 — Series Architect & Primary Fact Grounding for `{channel_id}`\n\n"
        f"1. Read `sys/channels/{channel_id}/playbook/{{overview.md,content.md,visual.md,pacing.md}}` (or `./vp playbook {channel_id} --pillar all`).\n"
        "2. Read `.agents/skills/vp-content-studio/SKILL.md` for 3-Vault grounding (`report_only_claims` quarantined).\n"
        f"3. {existing_note}"
        f"4. Episode sizing rule: {episode_directive} Target format: `{mode}` ({beat_desc}).\n"
        "5. Critical V4 Standalone-in-Series rules:\n"
        "   - Every episode MUST form one cohesive overarching story/campaign arc (cause -> mechanism -> turning point -> aftermath), "
        "with subtle narrative bridges (`next_episode_bridge` at Beat 18) WITHOUT spoiling viewer comprehension on cold Shorts feeds.\n"
        "   - Strictly FORBID `P1`, `P2`, `Part 1`, `Tập 1`, `Phần 2` prefixes in `youtube_title` (`<= 55` chars)! Each title must stand alone as an irresistible curiosity hook.\n"
        "   - `thumbnail_text`: 2–4 UPPERCASE words per episode.\n"
        "   - `beat_0_hook`: <= 18 syllables, ZERO `[pause:...]` tags, immediate human/strategic paradox.\n"
        "   - Every episode gets distinct primary facts, zero beat-for-beat overlap, and a 2-choice A/B `debate_question`.\n"
        f"6. Save the finalized Series Plan JSON to `sys/channels/{channel_id}/series_plans/<series_id>.json` AND return the matching structured output (`plan_path`, `episodes`, etc.)."
    )


def _build_episode_prompt(channel_id: str, plan: dict, ep: dict, mode: str) -> str:
    total = int(plan.get("episode_count") or len(plan.get("episodes") or []))
    facts_text = "\n".join(f"  - {f}" for f in (plan.get("shared_facts") or []))
    sibling_titles = "\n".join(
        f"  - Ep {e['series_order']}/{total}: {e['youtube_title']}"
        for e in (plan.get("episodes") or [])
    )
    lang = "en" if channel_id.startswith("en_") else "vi"
    extra_norm_check = (
        "6. For Vietnamese narration, run `detect_unnormalized_tokens` on every `beats[].tts_text` so zero raw digits/Latin shortcuts remain.\n"
        if lang == "vi"
        else "6. Ensure spoken `tts_text` spells out numbers in words cleanly (zero raw digits).\n"
    )
    return (
        f"Phase 2 — Author Episode {ep['series_order']}/{total} of Series `{plan['series_title']}` (`{channel_id}`)\n\n"
        f"1. Read `sys/channels/{channel_id}/playbook/{{content.md,visual.md,pacing.md}}`, `{plan['plan_path']}`, `.agents/skills/vp-content-studio/SKILL.md`, and `.agents/skills/vp-visual-fx/SKILL.md`.\n"
        "2. Series Arc Context (avoid overlapping with sibling episodes):\n"
        f"{sibling_titles}\n"
        "   Shared verified facts:\n"
        f"{facts_text}\n"
        f"3. Your assigned episode (`{ep['episode_code']}` — `order {ep['series_order']}/{total}`):\n"
        f"   - `job_id`: `{ep['job_id']}`\n"
        f"   - `youtube_title`: `{ep['youtube_title']}` (<= 55 chars, NO P1/P2)\n"
        f"   - `thumbnail_text`: `{ep['thumbnail_text']}`\n"
        f"   - `beat_0_hook`: `{ep['beat_0_hook']}`\n"
        f"   - `central_paradox`: {ep['central_paradox']}\n"
        f"   - `five_act_summary`: {ep['five_act_summary']}\n"
        f"   - `next_episode_bridge` (weave subtly at ~85–90% e.g. B18): {ep['next_episode_bridge']}\n"
        f"   - `debate_question` (Beat 19 + pinned comment): {ep['debate_question']}\n"
        "4. Scaffold via CLI (preserving Series grouping & placing episode directly in `video/<job_id>/`):\n"
        f"   `./vp scaffold-short --channel {channel_id} --topic \"{ep['youtube_title']}\" --mode {mode} "
        f"--job-id {ep['job_id']} --hook \"{ep['beat_0_hook']}\" --option-a \"{ep['debate_option_a']}\" --option-b \"{ep['debate_option_b']}\" "
        f"--series-id {plan['series_id']} --series-title \"{plan['series_title']}\" --series-order {ep['series_order']} --series-total {total} "
        f"--out video/{ep['job_id']}/short_spec.json`\n"
        f"5. Replace all template placeholder lines in `video/{ep['job_id']}/short_spec.json` with verified story-driven 5-Act beats "
        "(zero placeholders, Act 4 silence vacuum `B12 [pause:550ms]`, `<= 4`-word uppercase `heroic_banner` headlines >= 132px, Clear-Air visual prompts matching channel style, `asset_mode_override` 12 `flow_video` + 8 `2k_native_kenburns` in 20-beat mode).\n"
        f"{extra_norm_check}"
        "7. Validate `validate_v4_short_spec(spec) == []` and return `ready: true` with `spec_path`."
    )


def _build_render_prompt(ep_res: dict) -> str:
    return (
        f"Phase 3 — Render 2K Short MP4 for Series `{ep_res['series_id']}` Episode #{ep_res['series_order']} (`{ep_res['job_id']}`)\n\n"
        "Obey `.agents/skills/vp-flow-cdp/SKILL.md`, `.agents/skills/vp-colab-bridge/SKILL.md`, and `.agents/rules/gpu-headless-chrome.md`.\n"
        f"1. Run `./vp short --spec {ep_res['spec_path']} --visual-mode hybrid_2k --render-mode single_pass`.\n"
        "2. Verify output MP4 via `ffprobe` (`1440x2560@30fps`, `-11.0 LUFS / -1.0 dBTP`, bottom-right logo `W-w-36:H-h-36`) and inspect sample frames.\n"
        "3. Verify clean teardown: `./pipeline flow status` (`listening_count == 0`) and `./pipeline colab pool-status`.\n"
        "4. Return rendered file path."
    )


raw = dict(args or {})
channel_id = _resolve_channel(raw)
series_topic = str(raw.get("series_topic") or raw.get("topic") or "").strip()
existing_series_id = str(raw.get("existing_series_id") or "").strip()
episode_directive = _resolve_episode_directive(raw.get("episodes"))
mode = str(raw.get("mode") or "serialized_detail_short").strip()
if mode not in ("serialized_detail_short", "viral_fast_loop_short"):
    mode = "serialized_detail_short"
render_enabled = bool(raw.get("render", False))

phase("1. Series Discovery, Fact Vault & Episode Arc Blueprint")
log(f"Planning Series for `{channel_id}` (mode={mode}, render={render_enabled})...")
series_plan = await agent(
    _build_series_plan_prompt(channel_id, series_topic, episode_directive, existing_series_id, mode),
    schema=SERIES_PLAN_SCHEMA,
    role=f"Series Architect {channel_id}",
)
episodes = list(series_plan.get("episodes") or [])
log(f"Series Blueprint ready: {series_plan['series_title']!r} ({len(episodes)} episodes) -> {series_plan['plan_path']}")

phase("2. Parallel Series Episode Script Authoring & V4 Linter Gate")
log(f"Authoring {len(episodes)} linked Short spec(s) in parallel...")
episode_specs = await parallel(
    episodes,
    lambda ep: agent(
        _build_episode_prompt(channel_id, series_plan, ep, mode),
        schema=EPISODE_SPEC_SCHEMA,
        role=f"Ep {ep['series_order']}/{len(episodes)} {channel_id}",
    ),
)

for r in episode_specs:
    log(f"  - [Ep {r['series_order']}] ready={r['ready']} title={r['title']!r} -> {r['spec_path']}")

render_results = []
if render_enabled:
    ready_specs = sorted(
        [r for r in episode_specs if r.get("ready") and r.get("spec_path")],
        key=lambda x: int(x.get("series_order") or 0),
    )
    phase("3. Sequential Safe-IP Flow & Colab T4 Series Batch Render")
    log(f"Rendering {len(ready_specs)} Series episode(s) sequentially via pipeline()...")
    render_results = await pipeline(
        ready_specs,
        lambda s: agent(
            _build_render_prompt(s),
            schema=RENDER_SCHEMA,
            role=f"Render Ep {s['series_order']} ({s['job_id']})",
        ),
    )
    for rr in render_results:
        log(f"  - [{rr['job_id']}] rendered={rr['rendered']} mp4={rr['mp4_path']}")

print(
    json.dumps(
        {
            "series_plan": {
                "channel_id": series_plan["channel_id"],
                "series_id": series_plan["series_id"],
                "series_title": series_plan["series_title"],
                "plan_path": series_plan["plan_path"],
                "episode_count": len(episodes),
            },
            "episodes": episode_specs,
            "renders": render_results,
        },
        ensure_ascii=False,
        indent=2,
    )
)
