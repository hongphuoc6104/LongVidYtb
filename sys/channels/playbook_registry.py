"""38-Channel 3-Pillar Data Playbook Registry & Validator (V5 Consolidated Architecture).

Instead of polluting `.agents/skills/` with 38+ channel skills, every physical channel
stores its channel-specific identity and 3 pillars (`content.md`, `visual.md`, `pacing.md`,
plus `overview.md`) under `sys/channels/<channel_id>/playbook/` with 0 background token overhead.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from short_engine.archetype_packs import get_channel_short_pack

from channels.en_competitor_script_formulas import EN_COMPETITOR_SCRIPT_FORMULAS
from channels.en_flow_video_formulas import EN_FLOW_VIDEO_FORMULAS
from channels.lifecycle_ssot import (
    DEFAULT_CHANNEL_MAP_PATH,
    get_twin_channel_id,
    get_wave_for_channel,
    load_fleet_lifecycle,
    resolve_canonical_channel_id,
)
from channels.registry import get_channel
from channels.vn_competitor_script_formulas import VN_COMPETITOR_SCRIPT_FORMULAS
from channels.vn_flow_video_formulas import VN_FLOW_VIDEO_FORMULAS

SYS_DIR = Path(__file__).resolve().parents[1]
CHANNELS_ROOT = SYS_DIR / "channels"
PLAYBOOK_SUBDIR = "playbook"
REQUIRED_PLAYBOOK_FILES: tuple[str, ...] = ("overview.md", "content.md", "visual.md", "pacing.md")
PILLAR_TO_FILE: dict[str, str] = {
    "overview": "overview.md",
    "content": "content.md",
    "visual": "visual.md",
    "pacing": "pacing.md",
}

FLAGSHIP_SKILL_SOURCES: dict[str, dict[str, str]] = {
    "su_ke_lai": {
        "skill_dir": "vp-channel-su-ke-lai",
        "overview": "SKILL.md",
        "content": "references/long-9-15m-analytical-content-skill.md",
        "visual": "references/visual-grammar-option1.md",
        "pacing": "references/pacing-and-script-rules.md",
    },
    "ban_do_quyen_luc": {
        "skill_dir": "vp-channel-ban-do-quyen-luc",
        "overview": "SKILL.md",
        "visual": "references/visual-grammar-4styles.md",
        "pacing": "references/pacing-and-script-rules.md",
    },
    "co_the_ke": {
        "skill_dir": "vp-channel-co-the-ke",
        "overview": "SKILL.md",
        "visual": "references/visual-grammar-biomedical-v3.md",
        "pacing": "references/pacing-and-script-rules.md",
    },
    "ho_so_ky_la": {
        "skill_dir": "vp-channel-ho-so-ky-la",
        "overview": "SKILL.md",
        "visual": "references/visual-grammar-noir-forensic.md",
        "pacing": "references/pacing-and-script-rules.md",
    },
    "chanh_niem_ke": {
        "skill_dir": "vp-channel-chanh-niem-ke",
        "overview": "SKILL.md",
        "content": "references/bipolar_chronicle_playbook.md",
    },
}


def get_channel_playbook_dir(channel_id: str, channels_root: Path | None = None) -> Path:
    """Return canonical `sys/channels/<channel_id>/playbook` directory."""
    cid = resolve_canonical_channel_id(channel_id)
    root = Path(channels_root) if channels_root is not None else CHANNELS_ROOT
    return root / cid / PLAYBOOK_SUBDIR


def _load_channel_map_entry(channel_id: str, channels_root: Path) -> dict[str, Any]:
    map_path = channels_root / "youtube_channel_map.json"
    if not map_path.is_file():
        map_path = DEFAULT_CHANNEL_MAP_PATH
    try:
        data = json.loads(map_path.read_text(encoding="utf-8"))
        channels = data.get("channels") if isinstance(data, dict) else {}
        if isinstance(channels, dict):
            return dict(channels.get(channel_id, {}) or {})
    except Exception:
        pass
    return {}


def load_channel_playbook(channel_id: str, channels_root: Path | None = None) -> dict[str, Any]:
    """Load metadata and all 4 markdown sections (`overview`, `content`, `visual`, `pacing`) for a channel."""
    root = Path(channels_root) if channels_root is not None else CHANNELS_ROOT
    cid = resolve_canonical_channel_id(channel_id)
    pb_dir = get_channel_playbook_dir(cid, channels_root=root)
    pack = get_channel_short_pack(cid)
    lifecycle = load_fleet_lifecycle()
    map_entry = _load_channel_map_entry(cid, root)

    files: dict[str, str] = {}
    sections: dict[str, str] = {}
    missing: list[str] = []
    for pillar, fname in PILLAR_TO_FILE.items():
        fpath = pb_dir / fname
        files[pillar] = str(fpath)
        if fpath.is_file():
            sections[pillar] = fpath.read_text(encoding="utf-8")
        else:
            sections[pillar] = ""
            missing.append(fname)

    lc_entry = (lifecycle.get("channels") or {}).get(cid, {})
    lifecycle_state = str(lc_entry.get("state") or "STANDBY")

    return {
        "channel_id": cid,
        "channel_name": pack.channel_name,
        "language": pack.language,
        "handle": str(map_entry.get("handle") or ""),
        "profile_id": str(map_entry.get("profile_id") or ""),
        "youtube_channel_id": str(map_entry.get("youtube_channel_id") or ""),
        "archetype_id": pack.archetype_id,
        "wave": get_wave_for_channel(cid),
        "lifecycle_state": lifecycle_state,
        "twin_channel_id": get_twin_channel_id(cid),
        "voice_id": pack.voice_id,
        "default_speaking_rate": pack.default_speaking_rate,
        "bgm_mode": pack.bgm_mode,
        "primary_bgm": pack.primary_bgm,
        "playbook_dir": str(pb_dir),
        "files": files,
        "missing": missing,
        "sections": sections,
    }


def _find_broken_markdown_links(md_path: Path) -> list[str]:
    text = md_path.read_text(encoding="utf-8")
    broken: list[str] = []
    for raw_target in re.findall(r"\]\(([^)]+)\)", text):
        target = raw_target.strip("<>").split("#", 1)[0].strip()
        if not target or re.match(r"^[A-Za-z]+:", target) or " " in target:
            continue
        if not (md_path.parent / target).exists():
            broken.append(raw_target)
    return broken


def validate_all_channel_playbooks(channels_root: Path | None = None) -> dict[str, Any]:
    """Validate that all canonical channels have complete, non-empty 4-file playbooks and valid links."""
    root = Path(channels_root) if channels_root is not None else CHANNELS_ROOT
    map_path = root / "youtube_channel_map.json"
    if not map_path.is_file():
        map_path = DEFAULT_CHANNEL_MAP_PATH
    cmap = json.loads(map_path.read_text(encoding="utf-8")).get("channels", {})

    checked: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for cid in sorted(cmap):
        pb_dir = get_channel_playbook_dir(cid, channels_root=root)
        missing_files: list[str] = []
        empty_files: list[str] = []
        broken_links: dict[str, list[str]] = {}
        for fname in REQUIRED_PLAYBOOK_FILES:
            fpath = pb_dir / fname
            if not fpath.is_file():
                missing_files.append(fname)
                continue
            content = fpath.read_text(encoding="utf-8").strip()
            if len(content) < 40:
                empty_files.append(fname)
            bad = _find_broken_markdown_links(fpath)
            if bad:
                broken_links[fname] = bad

        ok = not missing_files and not empty_files and not broken_links
        entry = {
            "channel_id": cid,
            "ok": ok,
            "playbook_dir": str(pb_dir),
            "missing_files": missing_files,
            "empty_files": empty_files,
            "broken_links": broken_links,
        }
        checked.append(entry)
        if not ok:
            errors.append(entry)

    return {
        "total_channels": len(cmap),
        "valid_channels": sum(1 for item in checked if item["ok"]),
        "invalid_channels": len(errors),
        "all_valid": len(errors) == 0,
        "errors": errors,
        "channels": checked,
    }


def _rewrite_migrated_skill_markdown(text: str, channel_id: str) -> str:
    """Rewrite relative links inside migrated flagship channel skill files to work in `playbook/`."""
    out = text
    # Sibling reference links inside overview.md -> playbook/*.md
    sibling_replacements = {
        "references/visual-grammar-option1.md": "visual.md",
        "references/visual-grammar-4styles.md": "visual.md",
        "visual-grammar-4styles.md": "visual.md",
        "references/visual-grammar-biomedical-v3.md": "visual.md",
        "references/visual-grammar-noir-forensic.md": "visual.md",
        "references/pacing-and-script-rules.md": "pacing.md",
        "references/long-9-15m-analytical-content-skill.md": "content.md",
        "long-9-15m-analytical-content-skill.md": "content.md",
        "references/bipolar_chronicle_playbook.md": "content.md",
    }
    for old_ref, new_ref in sibling_replacements.items():
        out = out.replace(f"]({old_ref})", f"]({new_ref})")

    # Relative path replacements from `.agents/skills/<old>/` or `.../references/` to `sys/channels/<cid>/playbook/` (depth 4 under root)
    skill_link_map = {
        "../../vp-notebooklm-vault/SKILL.md": "../../../../.agents/skills/vp-content-studio/SKILL.md",
        "../../vp-research-architect/SKILL.md": "../../../../.agents/skills/vp-content-studio/SKILL.md",
        "../../vp-scriptwriting/SKILL.md": "../../../../.agents/skills/vp-content-studio/SKILL.md",
        "../../vp-channel-patterns/SKILL.md": "../../../../.agents/skills/vp-content-studio/SKILL.md",
        "../../vp-full-frame-quality/SKILL.md": "../../../../.agents/skills/vp-visual-fx/SKILL.md",
        "../../vp-motion-fx-warehouse/SKILL.md": "../../../../.agents/skills/vp-visual-fx/SKILL.md",
        "../../vp-flow-cdp/SKILL.md": "../../../../.agents/skills/vp-flow-cdp/SKILL.md",
        "../../vp-colab-bridge/SKILL.md": "../../../../.agents/skills/vp-colab-bridge/SKILL.md",
        "../../vp-omni-platform/SKILL.md": "../../../../.agents/skills/vp-production/SKILL.md",
        "../../vp-production/SKILL.md": "../../../../.agents/skills/vp-production/SKILL.md",
        "../vp-notebooklm-vault/SKILL.md": "../../../../.agents/skills/vp-content-studio/SKILL.md",
        "../vp-research-architect/SKILL.md": "../../../../.agents/skills/vp-content-studio/SKILL.md",
        "../vp-scriptwriting/SKILL.md": "../../../../.agents/skills/vp-content-studio/SKILL.md",
        "../vp-channel-patterns/SKILL.md": "../../../../.agents/skills/vp-content-studio/SKILL.md",
        "../vp-full-frame-quality/SKILL.md": "../../../../.agents/skills/vp-visual-fx/SKILL.md",
        "../vp-motion-fx-warehouse/SKILL.md": "../../../../.agents/skills/vp-visual-fx/SKILL.md",
        "../vp-flow-cdp/SKILL.md": "../../../../.agents/skills/vp-flow-cdp/SKILL.md",
        "../vp-colab-bridge/SKILL.md": "../../../../.agents/skills/vp-colab-bridge/SKILL.md",
        "../vp-omni-platform/SKILL.md": "../../../../.agents/skills/vp-production/SKILL.md",
        "../vp-production/SKILL.md": "../../../../.agents/skills/vp-production/SKILL.md",
        "../vp-new-episode-setup/SKILL.md": "../../../../.agents/skills/vp-production/references/new-episode-checklist.md",
        "../vp-development/SKILL.md": "../../../../.agents/skills/vp-engineering/SKILL.md",
        "../vp-maintenance/SKILL.md": "../../../../.agents/skills/vp-engineering/SKILL.md",
        "../vp-setup/SKILL.md": "../../../../.agents/skills/vp-engineering/SKILL.md",
        "../vp-troubleshooting/SKILL.md": "../../../../.agents/skills/vp-engineering/SKILL.md",
        "../../rules/gpu-headless-chrome.md": "../../../../.agents/rules/gpu-headless-chrome.md",
        "../../../sys/": "../../../",
    }
    for old_link, new_link in skill_link_map.items():
        out = out.replace(f"]({old_link}", f"]({new_link}")

    # Normalize depth-3 links inside migrated reference docs (originally under references/)
    out = out.replace("](../../../../../", "](../../../../")
    # Fix chanh_niem_ke benchmark links like `../../../sys/runs/...` when they remain in parens
    out = out.replace(f"](../../../../sys/channels/{channel_id}/", "](../")

    # Update inline skill identifiers to consolidated core skills
    out = out.replace("`vp-motion-fx-warehouse`", "`vp-visual-fx`")
    out = out.replace("[vp-motion-fx-warehouse]", "[vp-visual-fx]")
    out = out.replace("`vp-full-frame-quality`", "`vp-visual-fx`")
    out = out.replace("[vp-full-frame-quality]", "[vp-visual-fx]")
    out = out.replace("`vp-notebooklm-vault`", "`vp-content-studio`")
    out = out.replace("[vp-notebooklm-vault]", "[vp-content-studio]")
    out = out.replace("`vp-research-architect`", "`vp-content-studio`")
    out = out.replace("[vp-research-architect]", "[vp-content-studio]")
    out = out.replace("`vp-scriptwriting`", "`vp-content-studio`")
    out = out.replace("[vp-scriptwriting]", "[vp-content-studio]")
    out = out.replace("`vp-omni-platform`", "`vp-production`")
    out = out.replace("[vp-omni-platform]", "[vp-production]")

    # Ensure core visual-fx router token is present for warehouse/contract checks
    if "vp-visual-fx" not in out:
        out += "\n\n> **Core Visual & FX Skill:** [vp-visual-fx](../../../../.agents/skills/vp-visual-fx/SKILL.md)\n"
    return out


def _get_formulas(channel_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    slug = channel_id.replace("_", "-")
    if channel_id.startswith("en_"):
        comp = EN_COMPETITOR_SCRIPT_FORMULAS.get(slug) or EN_COMPETITOR_SCRIPT_FORMULAS.get(channel_id) or {}
        flow = EN_FLOW_VIDEO_FORMULAS.get(slug) or EN_FLOW_VIDEO_FORMULAS.get(channel_id) or {}
    else:
        comp = VN_COMPETITOR_SCRIPT_FORMULAS.get(channel_id) or VN_COMPETITOR_SCRIPT_FORMULAS.get(slug) or {}
        flow = VN_FLOW_VIDEO_FORMULAS.get(channel_id) or VN_FLOW_VIDEO_FORMULAS.get(slug) or {}
    return dict(comp), dict(flow)


def _render_overview_md(cid: str, map_entry: dict[str, Any]) -> str:
    pack = get_channel_short_pack(cid)
    reg = get_channel(cid)
    comp, _ = _get_formulas(cid)
    handle = map_entry.get("handle") or f"@{cid}"
    profile_id = map_entry.get("profile_id") or "unassigned"
    yt_id = map_entry.get("youtube_channel_id") or "unassigned"
    competitor = comp.get("competitor_name") or "Benchmark Niche Leader"

    return f"""# {pack.channel_name} (`{cid}`) — Channel Playbook Overview

- **Public Handle:** `{handle}` (`youtube_channel_id: {yt_id}`)
- **Language / Twin:** `{pack.language.upper()}` <-> Twin [`{pack.twin_channel_id}`](../../{pack.twin_channel_id}/playbook/overview.md)
- **Rollout Wave & Archetype:** `{pack.rollout_wave}` | `{pack.archetype_id}`
- **Studio Chrome Profile:** `{profile_id}` (benchmark model: *{competitor}*)
- **Core Skills Routing:** [vp-channel-registry](../../../../.agents/skills/vp-channel-registry/SKILL.md) -> [vp-content-studio](../../../../.agents/skills/vp-content-studio/SKILL.md) -> [vp-visual-fx](../../../../.agents/skills/vp-visual-fx/SKILL.md) -> [vp-flow-cdp](../../../../.agents/skills/vp-flow-cdp/SKILL.md) -> [vp-colab-bridge](../../../../.agents/skills/vp-colab-bridge/SKILL.md) -> [vp-production](../../../../.agents/skills/vp-production/SKILL.md)

## Niche & Audience Promise
- **Niche:** {reg.niche}
- **Audience Promise:** {reg.promise or reg.description}
- **Editorial Persona:** {reg.persona}
- **Tone & Boundaries:** {reg.tone} | Avoid: {reg.avoid or "Hype, fabricated data, or mechanical CTA spam"}

## 3-Pillar Playbook Files
1. **[content.md](content.md)** — Topic pillars, competitor script formula, V4 Short hook/debate structure & NotebookLM Fact Vault sources.
2. **[visual.md](visual.md)** — Flow BELUGA / Dual-Model video style lock, negative space discipline, camera grammar, banner palette, and bottom-right watermark `W-w-36:H-h-36`.
3. **[pacing.md](pacing.md)** — Voice profile (`{pack.voice_id}` @ `{pack.default_speaking_rate:.2f}x`), 5-Act BGM (`{pack.bgm_mode}` / `{pack.primary_bgm}`), sentence-clause pauses, and `-11.0 LUFS` audio master.
"""


def _render_content_md(cid: str) -> str:
    pack = get_channel_short_pack(cid)
    reg = get_channel(cid)
    comp, _ = _get_formulas(cid)
    dialogue = comp.get("competitor_dialogue_formula") or {}
    hooks = "\n".join(f"- {h}" for h in (reg.hook_formulas or ())) or "- Open directly on a counter-intuitive everyday stake (<= 18 words/syllables)."
    topics = "\n".join(f"- {t}" for t in (reg.seed_topics or ())) or f"- Core evergreen mysteries in {reg.niche}."
    long_struct = " -> ".join(reg.long_spec.structure) if reg.long_spec and reg.long_spec.structure else "Cold open -> Core conflict -> Causal reveal -> Resolution"
    short_struct = " -> ".join(reg.short_spec.structure) if reg.short_spec and reg.short_spec.structure else "Hook <=3s -> Open loop -> Escalation -> Payoff -> Close question"
    twin_note = (
        f"Shares verified primary Fact Vault research with sibling channel `{pack.twin_channel_id}` (`./vp clone-en` / bilingual adaptation)."
        if pack.twin_channel_id
        else "Primary standalone Fact Vault research required before scripting."
    )

    return f"""# Content & Script Strategy — {pack.channel_name} (`{cid}`)

## 1. Standalone Packaging & V4 Short Funnel
- **Title Contract:** `youtube_title <= 55` characters. Strictly NO numbered prefixes (`P1:`, `Part 2:`, `Ep 3:`) on Shorts.
- **Funnel Twin:** {twin_note}
- **Short->Long Policy:** Declare `parent_long_id` when linked; place channel bridge + 2-choice debate question inside final `15%` (`youtube_closing_question` / pinned creator comment). Never say *"like/share/subscribe"*.
- **NotebookLM 3-Vault Grounding:** Compile verified primary sources into `fact_vault.json` via `sys/tools/notebooklm_vault.py` before drafting narration (`fact_grounding_linter.py --strict`).

## 2. Proven Narrative Spine (`{comp.get("competitor_name") or pack.archetype_id}`)
- **Sentence Structure Formula:** {dialogue.get("sentence_structure_formula_vi") or short_struct}
- **Long (`long_16x9`) Spine:** {long_struct}
- **Short (`short_9x16`) Spine:** {short_struct}
- **20s Verbatim Rhythm Benchmark:** {dialogue.get("competitor_verbatim_transcript_20s") or "Immediate hook (0-3s) -> crisp escalation beats every 2.5-3.5s -> payoff & reflection."}

## 3. Hook Templates & Seed Topics
### Hook Templates
{hooks}

### Seed Topic Queue
{topics}
"""


def _render_visual_md(cid: str) -> str:
    pack = get_channel_short_pack(cid)
    reg = get_channel(cid)
    _, flow = _get_formulas(cid)
    forbidden = flow.get("forbidden_artifacts") or "No overlaid AI text, no watermarks, no cluttered visual slop."
    palette = ", ".join(reg.visual.palette) if isinstance(reg.visual.palette, (list, tuple)) else str(reg.visual.palette or "")
    return f"""# Visual Grammar & FX Lock — {pack.channel_name} (`{cid}`)

## 1. Visual Style Bible & Flow Prompt Lock
- **Archetype Track:** `{pack.archetype_id}` (consult [vp-visual-fx](../../../../.agents/skills/vp-visual-fx/SKILL.md) and [vp-channel-registry](../../../../.agents/skills/vp-channel-registry/SKILL.md))
- **Master Style Lock:** {pack.visual_style_lock}
- **Palette & Thumbnail Rule:** {palette or "Clean high-contrast palette per archetype"} | Thumbnail: {reg.visual.thumbnail_rule or "Flow-native poster with 2-4 uppercase words drawn in, < 2MB"}
- **Subject Physics:** {flow.get("subject_physics") or reg.visual.cast_appearance or "Focused visual subject matching scene metaphor."}
- **Wardrobe / Outfit Cue:** {reg.visual.outfit or "Consistent channel archetype styling"}
- **Continuity Anchor:** {flow.get("continuity_anchor") or "Preserve camera horizon, lighting key, and hero prop geometry via reference_scene_ids."}
- **Forbidden Visual Artifacts:** {forbidden}

## 2. Short V4 Render & Banner Specifications (`1440x2560@30fps`)
- **Dual-Model Video Router:** Route character/lighting jumps via `veo_3_1_lite` Seam Mode (`10c`) and continuous same-cast transitions via `omni_flash` (`macaron_cookie` Frame-Link).
- **Heroic Banner Palette (`>= 132px`, `anchor_y=150`, `<= 4` UPPERCASE words):**
  - Fill Bar RGBA: `{pack.banner_bar_rgba}`
  - Accent RGBA: `{pack.banner_accent_rgba}`
- **Camera Grammar:** {flow.get("camera_grammar") or "Smooth push_in / pull_back / truck_lateral rotation; zero consecutive duplicate moves."}
- **Watermark SSOT:** `{pack.watermark_path.name}` pinned bottom-right at `W-w-36:H-h-36` (`delogo` enabled only when Flow corner mark detected).
"""


def _render_pacing_md(cid: str) -> str:
    pack = get_channel_short_pack(cid)
    reg = get_channel(cid)
    comp, _ = _get_formulas(cid)
    dialogue = comp.get("competitor_dialogue_formula") or {}
    long_dur = reg.long_spec.duration_seconds if reg.long_spec else (540, 780)
    short_dur = reg.short_spec.duration_seconds if reg.short_spec else (48, 72)

    return f"""# Pacing, Voice & Audio Mastering — {pack.channel_name} (`{cid}`)

## 1. Voice Synthesis Profile (`Colab T4 OmniVoice`)
- **Canonical Voice ID:** `{pack.voice_id}` (`sys/assets/voices/ch_{cid}/profile.json`)
- **Recommended Speaking Rate:** `{pack.default_speaking_rate:.2f}x`
- **Strictly Forbidden:** Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
- **Master Audio Standard:** `48000Hz` stereo, **`-11.0 LUFS` / `-1.0 dBTP`** (`alimiter:level=disabled` required before final loudness normalization).

## 2. Format Duration & Beat Cadence
- **Long (`long_16x9`):** `{long_dur[0]}s–{long_dur[1]}s` (~{long_dur[0] // 60}–{long_dur[1] // 60} min), Lanczos sharp framing + `xfade=fade` (or FX warehouse `2.5D` when `--fx-mode auto_niche`).
- **Short V4 Modes:**
  - `viral_fast_loop_short` (`15–16` beats, `54–72s`, high-APV replay loop)
  - `serialized_detail_short` (`20` beats / `4` chunks × `5` beats, `105–120s`, `--render-mode single_pass` `1440x2560`)
  - Baseline `short_9x16`: `{short_dur[0]}s–{short_dur[1]}s`
- **Pause & Cadence Discipline:** {dialogue.get("pause_and_cadence_formula_vi") or "Zero [pause:...] inside opening Beat 0 (<= 18 words/syllables). Natural 180-350ms inter-clause pauses; single 450-650ms vacuum reset before climax."}
- **Camera Transition Pace:** {dialogue.get("transition_and_camera_formula_vi") or "Smooth semantic beat cuts aligned to spoken clause transitions; 0.18-0.28s optical dissolves between distinct scenes."}

## 3. 5-Act BGM & Sparse Foley (`sys/short_engine/audio_epic.py`)
- **BGM Mode:** `{pack.bgm_mode}` (`theme_id: {pack.theme_id}`)
- **Primary / Secondary Stems:** `{pack.primary_bgm}` / `{pack.secondary_bgm}`
- **Pre-Climax Silence Vacuum Stem:** `{pack.vacuum_stem}` at ~65% arc (`beat_index` calibrated per episode)
"""


def populate_all_channel_playbooks(
    *,
    channels_root: Path | None = None,
    legacy_skills_backup: Path | None = None,
) -> dict[str, Any]:
    """Build or refresh `sys/channels/<cid>/playbook/{overview,content,visual,pacing}.md` for all 38 channels."""
    root = Path(channels_root) if channels_root is not None else CHANNELS_ROOT
    backup_root = (
        Path(legacy_skills_backup)
        if legacy_skills_backup is not None
        else SYS_DIR / "scratch" / "legacy_skills_pre_v5_archive"
    )
    map_path = root / "youtube_channel_map.json"
    cmap = json.loads(map_path.read_text(encoding="utf-8")).get("channels", {})

    updated: list[str] = []
    for cid in sorted(cmap):
        pb_dir = get_channel_playbook_dir(cid, channels_root=root)
        pb_dir.mkdir(parents=True, exist_ok=True)
        entry = cmap[cid] if isinstance(cmap[cid], dict) else {}

        if cid in FLAGSHIP_SKILL_SOURCES:
            src_cfg = FLAGSHIP_SKILL_SOURCES[cid]
            legacy_dir = backup_root / src_cfg["skill_dir"]

            files_content: dict[str, str] = {}
            for pillar in ("overview", "content", "visual", "pacing"):
                rel_src = src_cfg.get(pillar)
                if rel_src and (legacy_dir / rel_src).is_file():
                    raw = (legacy_dir / rel_src).read_text(encoding="utf-8")
                    files_content[pillar] = _rewrite_migrated_skill_markdown(raw, cid)
                else:
                    if pillar == "overview":
                        files_content[pillar] = _render_overview_md(cid, entry)
                    elif pillar == "content":
                        files_content[pillar] = _render_content_md(cid)
                    elif pillar == "visual":
                        files_content[pillar] = _render_visual_md(cid)
                    else:
                        files_content[pillar] = _render_pacing_md(cid)

            for pillar, fname in PILLAR_TO_FILE.items():
                (pb_dir / fname).write_text(files_content[pillar], encoding="utf-8")
        else:
            (pb_dir / "overview.md").write_text(_render_overview_md(cid, entry), encoding="utf-8")
            (pb_dir / "content.md").write_text(_render_content_md(cid), encoding="utf-8")
            (pb_dir / "visual.md").write_text(_render_visual_md(cid), encoding="utf-8")
            (pb_dir / "pacing.md").write_text(_render_pacing_md(cid), encoding="utf-8")

        updated.append(cid)

    report = validate_all_channel_playbooks(channels_root=root)
    report["updated_channels"] = updated
    return report


WORKFLOW_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "id": "series_shorts",
        "name": "Series-First Short V4 (Find Series -> 3-5 Connected 20-Beat Scripts -> Batch Render Later)",
        "script_path": ".agents/skills/vp-production/scripts/wf_series_shorts.py",
        "default_args": {"channel": "open", "episodes": "auto_3_5", "mode": "serialized_detail_short", "render": False},
        "chat_prompt_vi": "/run-workflow Chạy .agents/skills/vp-production/scripts/wf_series_shorts.py với args={'channel': '<channel_id>', 'episodes': 'auto_3_5', 'mode': 'serialized_detail_short', 'render': False}",
        "summary_vi": "Tìm 1 bộ Series hoàn chỉnh (3–5 tập Short 20 cảnh ~100s liên kết mạch truyện, vẫn đặt tiêu đề độc lập) -> viết toàn bộ kịch bản đưa lên web -> Render hàng loạt sau.",
    },
    {
        "id": "batch_shorts",
        "name": "Batch Short V4 (Parallel Spec + Sequential Render)",
        "script_path": ".agents/skills/vp-production/scripts/wf_batch_shorts.py",
        "default_args": {"channels": "open", "count_per_channel": 1, "mode": "viral_fast_loop_short", "render": False},
        "chat_prompt_vi": "/run-workflow Chạy .agents/skills/vp-production/scripts/wf_batch_shorts.py với args={'channels': 'open', 'count_per_channel': 2, 'render': False}",
        "summary_vi": "Tung N agent soạn spec + chấm 4 linter song song, sau đó render tuần tự an toàn IP nếu render=True.",
    },
    {
        "id": "clone_en_twins",
        "name": "Clone VN -> EN Twins (Parallel Localization)",
        "script_path": ".agents/skills/vp-production/scripts/wf_clone_en_twins.py",
        "default_args": {"spec_paths": ["sys/runs/<job_id>/short_spec.json"], "render": False},
        "chat_prompt_vi": "/run-workflow Chạy .agents/skills/vp-production/scripts/wf_clone_en_twins.py với args={'spec_paths': ['sys/runs/<job_id>/short_spec.json'], 'render': False}",
        "summary_vi": "Chuyển ngữ song song các Short VN thắng view sang kênh EN song sinh đúng văn phong bản xứ.",
    },
    {
        "id": "qa_and_publish",
        "name": "3-Angle QA Council & Optional Studio Publish",
        "script_path": ".agents/skills/vp-production/scripts/wf_qa_and_publish.py",
        "default_args": {"channel": "<channel_id>", "job_dir": "video/<job_id>", "auto_publish": False},
        "chat_prompt_vi": "/run-workflow Chạy .agents/skills/vp-production/scripts/wf_qa_and_publish.py với args={'channel': '<channel_id>', 'job_dir': 'video/<job_id>', 'auto_publish': False}",
        "summary_vi": "3 agent độc lập soi Fact/Script, MP4/Audio LUFS và Packaging trước khi xuất bản YouTube Studio.",
    },
)


def get_workflows_catalog(repo_root: Path | None = None) -> list[dict[str, Any]]:
    """Return metadata and filesystem readiness for the 4 turnkey `/run-workflow` scripts."""
    root = Path(repo_root) if repo_root is not None else SYS_DIR.parent
    out: list[dict[str, Any]] = []
    for item in WORKFLOW_CATALOG:
        rel_path = str(item["script_path"])
        abs_path = root / rel_path
        out.append({**item, "abs_path": str(abs_path), "exists": abs_path.is_file()})
    return out


__all__ = [
    "FLAGSHIP_SKILL_SOURCES",
    "PILLAR_TO_FILE",
    "REQUIRED_PLAYBOOK_FILES",
    "WORKFLOW_CATALOG",
    "get_channel_playbook_dir",
    "get_workflows_catalog",
    "load_channel_playbook",
    "populate_all_channel_playbooks",
    "validate_all_channel_playbooks",
]
