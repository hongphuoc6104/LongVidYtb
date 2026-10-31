#!/usr/bin/env python3
"""Editorial Value, Opinion Stance, Cliffhanger Funnel & Narrative Pacing Linter (V3).

Enforces the 4 mandatory quality pillars for new Video Pilot batches:
1. Anti-Generic & Opinionated Editorial Stance:
   - Requires explicit `editorial_stance` in `brief.json` (myth debunked, sharp verdict,
     why conventional advice fails, and honest tradeoff/blindspot).
   - Verifies spoken narration contains genuine evaluative/opinionated commentary
     and rejects hollow textbook/self-help clichés.
2. Concrete Viewer Value (`actionable_value`):
   - Requires `core_mechanism`, `practical_rule_of_thumb`, and concrete real-world scenario.
3. Short-to-Long Peak Cliffhanger Funnel (`short_9x16`):
   - Front-loads the juiciest hook & sharp commentary in the first 70% of runtime,
     escalates to the peak twist (`cliffhanger_peak`), and bridges to the full Long video
     (`parent_long_id`) right at the climax.
4. Narrative-Driven Adaptive Visual Pacing (`audit_narrative_visual_density`):
   - Enforces high unique Flow image density (~2.2–3.5s/img on Long, ~1.8–2.6s/img on Short),
     zero lazy zoom reuse, and situation-matched tempo transitions.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from visual_pacing import NARRATIVE_SITUATION_TEMPO_MAP, audit_narrative_visual_density  # noqa: E402

HOLLOW_CLICHE_PATTERNS: tuple[str, ...] = (
    r"chúng ta cần phải cố gắng",
    r"điều này rất quan trọng đối với mỗi người",
    r"tùy thuộc vào hoàn cảnh của mỗi người",
    r"hãy luôn giữ tinh thần tích cực",
    r"như chúng ta đã biết",
    r"tóm lại việc này vừa có lợi vừa có hại",
)

EDITORIAL_OPINION_MARKERS: tuple[str, ...] = (
    "sự thật mất lòng",
    "đừng nghe lời khuyên",
    "sai lầm lớn nhất",
    "điểm mù",
    "góc nhìn thẳng thắn",
    "nhìn thẳng vào thực tế",
    "đánh giá công bằng",
    "cái bẫy",
    "ngược đời ở chỗ",
    "nghịch lý nằm ở",
    "thứ ít ai nói với bạn",
    "đừng vội tin",
    "cái giá phải trả",
    "nói thẳng ra",
    "thực chất",
    "bản chất thật sự",
)


def lint_editorial_and_narrative_quality(
    brief: dict[str, Any],
    content: dict[str, Any],
    estimated_duration_sec: float | None = None,
) -> dict[str, Any]:
    """Run full V3 audit for editorial commentary, viewer value, cliffhanger funnel, and visual pacing."""
    errors: list[str] = []
    warnings: list[str] = []

    format_profile = brief.get("format_profile") or (
        "long_16x9" if brief.get("aspect_ratio") == "16:9" else "short_9x16"
    )
    is_short = format_profile == "short_9x16"
    is_long = format_profile == "long_16x9"

    # 1. Check editorial_stance in brief.json
    editorial = brief.get("editorial_stance") or brief.get("packaging", {}).get("editorial_stance")
    if not isinstance(editorial, dict):
        errors.append(
            "MISSING_EDITORIAL_STANCE: brief.json must declare 'editorial_stance' dict with "
            "'myth_debunked', 'channel_verdict', 'why_generic_advice_fails', and 'tradeoff_or_blindspot'"
        )
    else:
        for req_key in ("myth_debunked", "channel_verdict", "why_generic_advice_fails", "tradeoff_or_blindspot"):
            val = str(editorial.get(req_key) or "").strip()
            if len(val.split()) < 5:
                errors.append(
                    f"WEAK_EDITORIAL_STANCE: editorial_stance.{req_key} must be a concrete statement (>= 5 words)"
                )

    # 2. Check actionable_value in brief.json
    val_spec = brief.get("actionable_value") or brief.get("packaging", {}).get("actionable_value")
    if not isinstance(val_spec, dict):
        errors.append(
            "MISSING_ACTIONABLE_VALUE: brief.json must declare 'actionable_value' dict with "
            "'core_mechanism', 'practical_rule_of_thumb', and 'real_world_scenario'"
        )
    else:
        for req_key in ("core_mechanism", "practical_rule_of_thumb", "real_world_scenario"):
            val = str(val_spec.get(req_key) or "").strip()
            if len(val.split()) < 5:
                errors.append(
                    f"WEAK_ACTIONABLE_VALUE: actionable_value.{req_key} must be concrete (>= 5 words)"
                )

    # 3. Check spoken narration for editorial commentary, hollow clichés, and narrative situations
    scenes = content.get("scenes", [])
    full_narration = " ".join(str(sc.get("narration") or "") for sc in scenes).lower()

    for pat in HOLLOW_CLICHE_PATTERNS:
        if re.search(pat, full_narration):
            errors.append(f"HOLLOW_GENERIC_CLICHE: narration contains generic filler matching '{pat}'")

    matched_markers = [m for m in EDITORIAL_OPINION_MARKERS if m in full_narration]
    editorial_scenes = [
        sc.get("id")
        for sc in scenes
        if (sc.get("narrative_situation") or sc.get("narrative_role")) == "editorial_commentary"
        or any(b.get("narrative_situation") == "editorial_commentary" for b in sc.get("beats", []))
    ]
    min_ed_scenes = 1 if is_short else 2
    if len(editorial_scenes) < min_ed_scenes and len(matched_markers) < 2:
        errors.append(
            f"INSUFFICIENT_EDITORIAL_COMMENTARY: expected >= {min_ed_scenes} scene(s) with "
            "narrative_situation='editorial_commentary' (or >= 2 explicit evaluative commentary markers in narration)"
        )

    # 4. Check Short-to-Long Peak Cliffhanger Funnel on short_9x16
    if is_short:
        cta_plan = brief.get("cta_plan") or brief.get("packaging", {}).get("cta_plan") or {}
        cliffhanger = str(cta_plan.get("cliffhanger_peak") or "").strip()
        if len(cliffhanger.split()) < 6:
            errors.append(
                "MISSING_SHORT_CLIFFHANGER_PEAK: short_9x16 brief['cta_plan'] must declare 'cliffhanger_peak' "
                "(>= 6 words describing the peak twist/open loop right before inviting viewers to the full video)"
            )
        if scenes:
            first_sit = scenes[0].get("narrative_situation") or scenes[0].get("narrative_role") or ""
            if first_sit and first_sit not in ("hook_shock", "before_after_contrast", "rapid_examples"):
                warnings.append(
                    f"SHORT_OPENING_SITUATION: SC01 uses '{first_sit}'; recommended 'hook_shock' for immediate magnet"
                )

    # 5. Check Narrative-Driven Adaptive Visual Density
    pacing_errors = audit_narrative_visual_density(brief, content, estimated_duration_sec=estimated_duration_sec)
    errors.extend(pacing_errors)

    # Summarize narrative situation distribution
    sit_counts: dict[str, int] = {}
    for sc in scenes:
        sc_sit = sc.get("narrative_situation") or sc.get("narrative_role")
        if sc_sit:
            sit_counts[sc_sit] = sit_counts.get(sc_sit, 0) + 1
        for b in sc.get("beats", []):
            b_sit = b.get("narrative_situation")
            if b_sit:
                sit_counts[b_sit] = sit_counts.get(b_sit, 0) + 1

    all_beats = [b for sc in scenes for b in sc.get("beats", [])]
    uniq_imgs = {b.get("image_id") for b in all_beats if b.get("image_id")}
    total_words = sum(len(str(sc.get("narration") or "").split()) for sc in scenes)
    est_dur = estimated_duration_sec or max(25.0, total_words / 3.8)

    return {
        "passed": len(errors) == 0,
        "format_profile": format_profile,
        "scenes_count": len(scenes),
        "beats_count": len(all_beats),
        "unique_images_count": len(uniq_imgs),
        "estimated_duration_sec": round(est_dur, 1),
        "avg_unique_image_hold_sec": round(est_dur / max(1, len(uniq_imgs)), 2),
        "editorial_scenes": editorial_scenes,
        "opinion_markers_found": matched_markers,
        "narrative_situations": sit_counts,
        "supported_situations": list(NARRATIVE_SITUATION_TEMPO_MAP.keys()),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit Editorial Stance, Viewer Value, Short Cliffhanger Funnel & Narrative Visual Pacing."
    )
    parser.add_argument("target", help="Job directory or brief.json path")
    parser.add_argument("--content", help="Optional explicit path to content.json")
    parser.add_argument("--duration", type=float, default=None, help="Optional measured WAV duration in seconds")
    args = parser.parse_args()

    target_path = Path(args.target).resolve()
    if target_path.is_dir():
        brief_file = target_path / "brief.json"
        content_file = target_path / "content.json"
        audio_file = target_path / "revisions/audio/1/output.json"
    else:
        brief_file = target_path
        content_file = Path(args.content).resolve() if args.content else target_path.parent / "content.json"
        audio_file = target_path.parent / "revisions/audio/1/output.json"

    if not brief_file.is_file() or not content_file.is_file():
        print(f"Error: Missing brief.json or content.json in {target_path}", file=sys.stderr)
        sys.exit(2)

    brief_data = json.loads(brief_file.read_text(encoding="utf-8"))
    content_data = json.loads(content_file.read_text(encoding="utf-8"))

    dur = args.duration
    if dur is None and audio_file.is_file():
        try:
            a_data = json.loads(audio_file.read_text(encoding="utf-8"))
            dur = float(a_data.get("payload", a_data).get("duration", 0.0)) or None
        except Exception:
            pass

    report = lint_editorial_and_narrative_quality(brief_data, content_data, estimated_duration_sec=dur)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["passed"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
