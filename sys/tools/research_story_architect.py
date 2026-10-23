#!/usr/bin/env python3
"""Research Story Architect for Video Pilot.

Upstream narrative, packaging, localization, and technical engine for the `vp-research-architect` skill.
Transforms structured research and academic facts into schema 3.0 valid `brief.json`
and `content.json` bundles with:
  - Packaging & SEO Contract (`youtube_title` <= 55 chars, `thumbnail_spec` 2-4 uppercase words, `channel_pillar` lock)
  - 3-Tier Academic Research Funnel (`tier_1_broad`, `tier_2_mid`, `tier_3_conversion`) & Anti-Dilution Guard
  - Mandatory Vietnamese Cultural Localization in the first 60s (`SC01-SC02` / `CH01`)
  - Short-Form Spin-off Blueprint (`long_16x9` + 2-3 standalone `short_9x16` packages)
  - Acoustic cadence calibration (P_tail formula, zero pause in SC01, opening hook <= 18 syllables)
  - Narration-anchored full-frame scene images and in-place `based_on` variations
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
venv_py = SYS_DIR / ".venv/bin/python"
if __name__ == "__main__" and venv_py.is_file() and Path(sys.executable).resolve() != venv_py.resolve():
    os.execv(str(venv_py), [str(venv_py), str(Path(__file__).resolve())] + sys.argv[1:])

if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))
if str(SYS_DIR / "tools") not in sys.path:
    sys.path.insert(0, str(SYS_DIR / "tools"))

from script_cadence_checker import (  # noqa: E402
    DEFAULT_MAX_OPENING_HOOK_SYLLABLES,
    DEFAULT_P_TAIL_LAST,
    DEFAULT_P_TAIL_PARA,
    NOMINAL_SPEECH_RATE,
    ScriptCadenceChecker,
    calculate_target_syllables,
    count_syllables,
    extract_pauses,
    split_sentences,
)
from visual_style import CAST_APPEARANCE, DEFAULT_OUTFIT, STYLE_DESCRIPTION

STYLE_VERSION = "1.7.0"

DEFAULT_CHANNEL_PILLAR = "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức"
ALLOWED_FUNNEL_TIERS: Tuple[str, str, str] = ("tier_1_broad", "tier_2_mid", "tier_3_conversion")
MAX_YOUTUBE_TITLE_CHARS = 55
HARD_MAX_YOUTUBE_TITLE_CHARS = 65

_DRY_ACADEMIC_FACT_RE = re.compile(
    r"(?:\bdoi\s*:|\bisbn\s*:|\bet\s+al\.|\bpp?\.\s*\d|\(\d{4}\)|\d+\s*%|\w+/\w+)",
    re.IGNORECASE,
)

# Off-pillar office-tip keywords that dilute the academic research audience
_BANNED_OFF_PILLAR_RE = re.compile(
    r"(?:\bmẹo\s+excel\b|\bhàm\s+excel\b|\blàm\s+slide\s+4\s+tiếng\b|\blàm\s+slide\s+nhanh\b|\btình\s+huống\s+(?:của\s+)?bạn\s+na\b|\btình\s+huống\s+của\s+na\b)",
    re.IGNORECASE,
)

# Foreign historical / anthropological jargon forbidden in the first 60s (SC01) before Vietnamese localization
_FOREIGN_OPENING_JARGON_RE = re.compile(
    r"\b(?:sumer|edubba|mesopotamia|lưỡng\s+hà|kalahari|ju/'hoansi|giu-hoan-si|hadza|nhà\s+máy\s+phổ|quân\s+sự\s+phổ)\b",
    re.IGNORECASE,
)

# Self-answering title pattern (gives away the answer in the title instead of creating a Curiosity Gap)
_SELF_ANSWERING_TITLE_RE = re.compile(
    r"(?:\blà\s+do\b|\blà\s+bởi\s+vì\b|\bcâu\s+trả\s+lời\s+là\b)",
    re.IGNORECASE,
)

# AI-slop thumbnail visual clichés (generic stock AI imagery that kills CTR)
_THUMBNAIL_AI_SLOP_RE = re.compile(
    r"\b(?:neon\s+brain|exploding\s+brain|glowing\s+galaxy\s+brain|binary\s+code\s+rain|matrix\s+0101|"
    r"cyborg\s+hand|robot\s+shaking\s+hands|generic\s+gear\s+head|floating\s+hologram\s+screen|"
    r"não\s+phát\s+sáng\s+neon|não\s+nổ\s+tung|mưa\s+mã\s+nhị\s+phân)\b",
    re.IGNORECASE,
)

# 8-Stage Invisible Narrative Arc for YouTube Explainer Storytelling
NARRATIVE_ARC_8_STAGES: Tuple[str, ...] = (
    "hook",              # 1. Mở bài (Truth-Slap / Đời thực)
    "lead_in",           # 2. Phần dẫn (Neo cảm xúc & Bối cảnh)
    "problem",           # 3. Phần vấn đề (Mâu thuẫn nhận thức)
    "causal_mechanism",  # 4. Phần nhân quả (Cơ chế gốc rễ)
    "explanation",       # 5. Phần giải thích (Mô hình hóa trực quan)
    "counter_argument",  # 6. Phần phản biện (Lật ngược giả định / Giới hạn)
    "takeaway",          # 7. Phần nội dung rút ra (Đúc kết nguyên lý)
    "closing",           # 8. Phần kết bài (Khép vòng lặp mở bài)
)

MAX_CONSECUTIVE_VARIATION_BEATS = 2


from scripts.camera_motion import assign_scene_camera_effects, select_semantic_camera_effect  # noqa: F401


def infer_editorial_section(index: int, total: int, title: str = "", narration: str = "") -> str:
    """Infer the 8-part editorial narrative stage from scene position and semantic cues."""
    combined = f"{title} {narration}".casefold()
    if index <= 1:
        return "hook"
    if index == total and total >= 3:
        return "closing"
    if re.search(r"\b(?:phản biện|ngược lại|tuy nhiên|nhưng nếu nhìn kỹ|giới hạn|ngoại lệ|mặt trái)\b", combined):
        if index >= max(3, (total * 3) // 5):
            return "counter_argument"
    if re.search(r"\b(?:rút ra|nguyên lý|quy tắc|bài học|cốt lõi nằm ở|ma trận|khung tư duy)\b", combined):
        if index >= max(3, (total * 3) // 5):
            return "takeaway"

    if total <= 0:
        return "explanation"
    if total == len(NARRATIVE_ARC_8_STAGES):
        return NARRATIVE_ARC_8_STAGES[max(0, min(len(NARRATIVE_ARC_8_STAGES) - 1, index - 1))]
    stage_idx = min(
        len(NARRATIVE_ARC_8_STAGES) - 1,
        max(0, int(((index - 1) * len(NARRATIVE_ARC_8_STAGES)) / max(1, total))),
    )
    return NARRATIVE_ARC_8_STAGES[stage_idx]


def split_long_sentence_into_beat_clauses(sentence: str, max_words: int = 14) -> List[str]:
    """Split a long spoken sentence into 2 natural visual beat clauses at punctuation or discourse Pivot markers
    so visuals never freeze on a single frame for > 4 seconds.
    """
    cleaned = sentence.strip()
    words = cleaned.split()
    if len(words) <= max_words:
        return [cleaned]

    # Try splitting on natural internal punctuation or Vietnamese discourse pivots near the middle
    pivot_re = re.compile(
        r"(?:[,;–—]\s+|\s+(?:nhưng|mà|để rồi|trong khi|thay vì|khiến cho|dẫn đến|bởi vì|nhờ đó|ngược lại)\s+)",
        re.IGNORECASE,
    )
    mid_char = len(cleaned) // 2
    best_split: Optional[Tuple[int, str, str]] = None
    for m in pivot_re.finditer(cleaned):
        left = cleaned[: m.start()].strip()
        right = cleaned[m.start() :].lstrip(",;–— ").strip()
        if len(left.split()) >= 4 and len(right.split()) >= 4:
            dist = abs(m.start() - mid_char)
            if best_split is None or dist < best_split[0]:
                best_split = (dist, left, right)
    if best_split is not None:
        return [best_split[1], best_split[2]]
    return [cleaned]


def build_thumbnail_poster_prompt(
    visual_hook: str,
    text_overlay: str,
    contrast_pair: str = "",
    style_tone: str = "Warm editorial 2D hand-drawn illustration on textured cream paper (#F5F2EB) with bold charcoal ink",
) -> str:
    """Compile an Integrated Poster Thumbnail Prompt where 1 iconic visual metaphor occupies 60% of the frame
    and bold golden-yellow typography (#FACC15) with thick charcoal outline is natively integrated in 40% clean negative space.
    """
    hook_clean = visual_hook.strip().rstrip(".")
    overlay_clean = text_overlay.strip().upper()
    contrast_note = f" Visual contrast tension: {contrast_pair.strip().rstrip('.')}." if contrast_pair.strip() else ""
    return (
        f"YouTube 16:9 high-CTR integrated poster thumbnail. {style_tone}. "
        f"Rule of thirds composition: 60% of the frame features ONE striking focal metaphor ({hook_clean}), "
        f"leaving 40% clean uncluttered negative space.{contrast_note} "
        f"Natively integrated into the negative space is giant, bold, hand-crafted uppercase poster typography "
        f"reading \"{overlay_clean}\" in vibrant golden-yellow (#FACC15) with a heavy charcoal-black ink outline "
        f"and subtle warm drop shadow, matching the exact brush texture and lighting of the artwork. "
        f"No cheap rectangular text boxes, no cluttered tiny details, maximum 2 focal elements."
    )


def check_conversational_spoken_facts(
    sources: List[Dict[str, Any]],
    max_syllables: int = 22,
) -> List[str]:
    """Audit brief sources[].facts against the Conversational Spoken Fact Protocol (ERR-20261011-03)."""
    warnings: List[str] = []
    for src in sources:
        src_id = src.get("id", "SRC")
        for fact in src.get("facts", []):
            fact_str = str(fact)
            syl = count_syllables(fact_str, lang="vi")
            if syl > max_syllables:
                warnings.append(
                    f"{src_id}: Fact exceeds {max_syllables} spoken syllables ({syl} syl): {fact_str}"
                )
            if _DRY_ACADEMIC_FACT_RE.search(fact_str):
                warnings.append(
                    f"{src_id}: Fact contains dry academic notation instead of spoken Vietnamese: {fact_str}"
                )
    return warnings


def check_packaging_and_localization(
    brief_data: Dict[str, Any],
    scenes: Optional[List[Any]] = None,
    max_title_chars: int = MAX_YOUTUBE_TITLE_CHARS,
    check_opening_hook: bool = False,
) -> List[str]:
    """Audit Packaging & SEO Contract (Bẫy 3) and Vietnamese Cultural Localization in First 60s (Bẫy 4)."""
    warnings: List[str] = []
    pkg = brief_data.get("packaging") or {}
    yt_title = str(brief_data.get("youtube_title") or pkg.get("youtube_title") or "").strip()
    thumb = brief_data.get("thumbnail_spec") or pkg.get("thumbnail_spec") or {}
    pillar = str(brief_data.get("channel_pillar") or pkg.get("channel_pillar") or "").strip()
    tier = brief_data.get("funnel_tier") or pkg.get("funnel_tier")
    topic_str = str(brief_data.get("topic") or "")

    # 1. Anti-Dilution Guard: block office tips (Excel, 4-hour slides, Na's English skits)
    for field_name, text_val in (("topic", topic_str), ("youtube_title", yt_title), ("channel_pillar", pillar)):
        if _BANNED_OFF_PILLAR_RE.search(text_val):
            warnings.append(
                f"OFF_PILLAR_DILUTION ({field_name}): Contains banned office-tip keyword (Excel/Slide/Na): {text_val}"
            )

    # 2. YouTube Title validation (<= 55 chars recommended, Curiosity Gap, not self-answering)
    if yt_title:
        if len(yt_title) > max_title_chars:
            warnings.append(
                f"YOUTUBE_TITLE_TOO_LONG: youtube_title is {len(yt_title)} chars (must be <= {max_title_chars} chars): '{yt_title}'"
            )
        if _SELF_ANSWERING_TITLE_RE.search(yt_title):
            warnings.append(
                f"YOUTUBE_TITLE_SELF_ANSWERING: youtube_title answers its own question instead of creating a Curiosity Gap: '{yt_title}'"
            )

    # 3. Thumbnail Spec validation (visual_hook + 2-4 uppercase word text_overlay + anti-AI-slop check)
    if isinstance(thumb, dict) and thumb:
        vis_hook = str(thumb.get("visual_hook") or "").strip()
        overlay = str(thumb.get("text_overlay") or "").strip()
        thumb_prompt = str(thumb.get("thumbnail_prompt") or "").strip()
        if not vis_hook:
            warnings.append("THUMBNAIL_MISSING_VISUAL_HOOK: thumbnail_spec.visual_hook must not be empty")
        elif _THUMBNAIL_AI_SLOP_RE.search(vis_hook) or _THUMBNAIL_AI_SLOP_RE.search(thumb_prompt):
            warnings.append(
                f"THUMBNAIL_AI_SLOP_CLICHE: thumbnail_spec contains generic AI cliché (neon brain/matrix/cyborg): '{vis_hook}'"
            )
        if overlay:
            overlay_words = [w for w in re.split(r"\s+", overlay) if w]
            if not (2 <= len(overlay_words) <= 5):
                warnings.append(
                    f"THUMBNAIL_OVERLAY_WORD_COUNT: text_overlay '{overlay}' has {len(overlay_words)} words (must be 2-4 words)"
                )
            alpha_chars = [c for c in overlay if c.isalpha()]
            if alpha_chars and not all(c.isupper() for c in alpha_chars):
                warnings.append(
                    f"THUMBNAIL_OVERLAY_NOT_UPPERCASE: text_overlay '{overlay}' must be uppercase"
                )
        else:
            warnings.append("THUMBNAIL_MISSING_TEXT_OVERLAY: thumbnail_spec.text_overlay is required")

    # 4. Funnel tier check
    if tier is not None and tier not in ALLOWED_FUNNEL_TIERS:
        warnings.append(
            f"INVALID_FUNNEL_TIER: funnel_tier '{tier}' must be one of {ALLOWED_FUNNEL_TIERS}"
        )

    # 5. Vietnamese Cultural Localization & Opening Scene (SC01) checks
    if scenes:
        first_sc = scenes[0]
        first_narr = (
            first_sc.narration
            if hasattr(first_sc, "narration")
            else str(first_sc.get("narration") or "")
        )
        m_foreign = _FOREIGN_OPENING_JARGON_RE.search(first_narr)
        if m_foreign:
            warnings.append(
                f"OPENING_NOT_LOCALIZED_VN: SC01 introduces foreign/ancient term '{m_foreign.group(0)}' in the first 60s instead of a relatable Vietnamese context"
            )
        if check_opening_hook:
            pause_sec, pauses, _ = extract_pauses(first_narr)
            if pauses:
                warnings.append(
                    f"OPENING_SCENE_PAUSE_FORBIDDEN: SC01 contains {len(pauses)} pause tag(s) ({pause_sec:.2f}s); zero [pause:...] allowed in first 15s"
                )
            sents = split_sentences(first_narr)
            if sents:
                first_syl = count_syllables(sents[0], lang="vi")
                if first_syl > DEFAULT_MAX_OPENING_HOOK_SYLLABLES:
                    warnings.append(
                        f"OPENING_HOOK_TOO_LONG: SC01 first sentence has {first_syl} syllables (must be <= {DEFAULT_MAX_OPENING_HOOK_SYLLABLES})"
                    )

    return warnings


@dataclass
class PackagingSpec:
    youtube_title: str
    visual_hook: str
    text_overlay: str
    contrast_pair: str = "Học vẹt cơ học vs. Tư duy bản chất Q1"
    channel_pillar: str = DEFAULT_CHANNEL_PILLAR
    funnel_tier: str = "tier_1_broad"
    seo_keywords: List[str] = field(default_factory=list)
    thumbnail_prompt: Optional[str] = None
    layout_mode: Optional[str] = None
    typography_style: Optional[str] = None

    def compile_poster_prompt(self) -> str:
        """Return explicit thumbnail_prompt or compile an integrated poster prompt with large yellow typography."""
        if self.thumbnail_prompt:
            return self.thumbnail_prompt
        return build_thumbnail_poster_prompt(
            visual_hook=self.visual_hook,
            text_overlay=self.text_overlay,
            contrast_pair=self.contrast_pair,
        )

    def to_dict(self) -> Dict[str, Any]:
        thumb_dict: Dict[str, Any] = {
            "visual_hook": self.visual_hook,
            "text_overlay": self.text_overlay,
            "contrast_pair": self.contrast_pair,
        }
        if self.thumbnail_prompt is not None:
            thumb_dict["thumbnail_prompt"] = self.thumbnail_prompt
        if self.layout_mode is not None:
            thumb_dict["layout_mode"] = self.layout_mode
        if self.typography_style is not None:
            thumb_dict["typography_style"] = self.typography_style
        return {
            "youtube_title": self.youtube_title,
            "thumbnail_spec": thumb_dict,
            "channel_pillar": self.channel_pillar,
            "funnel_tier": self.funnel_tier,
            "seo_keywords": list(self.seo_keywords),
        }


@dataclass
class HumanEditorialSpec:
    """Anti-AI-Slop Human Editorial Co-Creation block with dynamic topic-specific questions and expanded in-video ideas."""

    topic_dilemmas: List[str]
    dynamic_questions: List[str]
    author_raw_input: Optional[str] = None
    editorial_stance: Optional[str] = None
    expanded_content_ideas: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "topic_dilemmas": list(self.topic_dilemmas),
            "dynamic_questions": list(self.dynamic_questions),
        }
        if self.author_raw_input is not None:
            payload["author_raw_input"] = self.author_raw_input
        if self.editorial_stance is not None:
            payload["editorial_stance"] = self.editorial_stance
        if self.expanded_content_ideas:
            payload["expanded_content_ideas"] = [dict(item) for item in self.expanded_content_ideas]
        return payload


@dataclass
class ResearchedBeat:
    """One complete full-frame image and its narration-anchored beat."""

    image_id: str
    description: str
    anchor_quote: str
    reason: str
    character_ids: List[str] = field(default_factory=list)
    anchor_quote_en: Optional[str] = None
    anchor_occurrence: int = 1
    anchor_occurrence_en: int = 1
    effect: str = "cut"
    focus_x: float = 0.5
    focus_y: float = 0.5
    based_on: Optional[str] = None
    preserve: str = ""
    change: str = "Show the described full-frame scene."
    visible_text: List[Dict[str, str]] = field(default_factory=list)
    shot_type: str = "full_scene"
    allow_expression_shift: Optional[bool] = None
    has_character: Optional[bool] = None
    explanation: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        allowed_shots = {
            "macro_prop",
            "full_scene",
            "variation",
            "white_card",
            "white_isolated",
            "still_life",
            "environment",
            "concept_metaphor",
            "visual_diagram",
            "cutaway_detail",
        }
        if self.shot_type not in allowed_shots:
            raise ValueError(f"Unsupported full-frame shot type: {self.shot_type}")
        if self.shot_type in {"still_life", "environment", "visual_diagram", "cutaway_detail"} and not self.character_ids:
            self.character_ids = []
        if self.shot_type == "variation" and not (self.based_on and self.preserve.strip() and self.change.strip()):
            raise ValueError("A variation requires based_on, preserve, and change")
        from flow_prompts import find_visual_cliche
        from flow_prompts.compiler import find_laziness_pattern
        for field_name, text in [("description", self.description), ("preserve", self.preserve), ("change", self.change)]:
            if text:
                cliche = find_visual_cliche(text)
                if cliche:
                    raise ValueError(f"FLOW_CLICHE_FORBIDDEN in {self.image_id} {field_name}: contains banned {cliche}")
                laziness = find_laziness_pattern(text)
                if laziness:
                    name, token = laziness
                    raise ValueError(f"LAZY_VISUAL_ACTION_FORBIDDEN in {self.image_id} {field_name}: contains banned {name} ({token!r})")
        for vt in self.visible_text:
            if isinstance(vt, str):
                cliche = find_visual_cliche(vt)
                if cliche:
                    raise ValueError(f"FLOW_CLICHE_FORBIDDEN in {self.image_id} visible_text: contains banned {cliche}")
                laziness = find_laziness_pattern(vt)
                if laziness:
                    name, token = laziness
                    raise ValueError(f"LAZY_VISUAL_ACTION_FORBIDDEN in {self.image_id} visible_text: contains banned {name} ({token!r})")
            elif isinstance(vt, dict):
                for subf in ("text", "placement", "object"):
                    subval = vt.get(subf)
                    if subval and isinstance(subval, str):
                        cliche = find_visual_cliche(subval)
                        if cliche:
                            raise ValueError(f"FLOW_CLICHE_FORBIDDEN in {self.image_id} visible_text.{subf}: contains banned {cliche}")
                        laziness = find_laziness_pattern(subval)
                        if laziness:
                            name, token = laziness
                            raise ValueError(f"LAZY_VISUAL_ACTION_FORBIDDEN in {self.image_id} visible_text.{subf}: contains banned {name} ({token!r})")


# Read compatibility for authored briefs and older builder imports.
ResearchedVisualBeat = ResearchedBeat


@dataclass
class ResearchedScene:
    scene_id: str
    title: str
    purpose: str
    duration: float
    narration: str
    requirements: List[str]
    source_ids: List[str]
    character_ids: List[str]
    action: str
    setting: str
    camera: str
    bg_description: str = ""
    foley_cue: Optional[str] = None
    claim_facts: List[Tuple[str, str, str]] = field(default_factory=list)  # (quote, source_id, fact)
    narration_en: Optional[str] = None
    visual_beats: List[ResearchedVisualBeat] = field(default_factory=list)
    scene_description: str = ""
    tone: Optional[str] = None
    narrative_phase: Optional[str] = None

    def __post_init__(self) -> None:
        from flow_prompts import find_visual_cliche
        from flow_prompts.compiler import find_laziness_pattern
        for field_name, text in [("setting", self.setting), ("action", self.action), ("bg_description", self.bg_description), ("scene_description", self.scene_description)]:
            if text:
                cliche = find_visual_cliche(text)
                if cliche:
                    raise ValueError(f"FLOW_CLICHE_FORBIDDEN in {self.scene_id} {field_name}: contains banned {cliche}")
                laziness = find_laziness_pattern(text)
                if laziness:
                    name, token = laziness
                    raise ValueError(f"LAZY_VISUAL_ACTION_FORBIDDEN in {self.scene_id} {field_name}: contains banned {name} ({token!r})")


@dataclass
class ResearchedTopic:
    topic: str
    audience: str
    goal: str
    video_type: str
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None
    style: str = STYLE_DESCRIPTION
    aspect_ratio: str = "16:9"
    sources: List[Dict[str, Any]] = field(default_factory=list)
    required_points: List[Dict[str, str]] = field(default_factory=list)
    characters: List[Dict[str, str]] = field(default_factory=list)
    scenes: List[ResearchedScene] = field(default_factory=list)
    tone: str = "Điềm đạm, ấm áp, thông tuệ, gần gũi"
    language: str = "vi"
    subtitles: Optional[bool] = None
    voice: Optional[str] = None
    speed: Optional[float] = None
    format_profile: Optional[str] = None
    conversational_facts: Optional[bool] = None
    packaging: Optional[PackagingSpec] = None
    human_editorial: Optional[Any] = None
    spinoff_shorts: Optional[List[Dict[str, Any]]] = None
    visual_pacing_profile: Optional[str] = None
    enable_sound_design: Optional[bool] = None


def serialize_brief_json(brief_dict: Dict[str, Any]) -> str:
    """Serialize brief dictionary identically to Video Pilot's write() function."""
    return json.dumps(brief_dict, ensure_ascii=False, indent=2)


def compute_brief_hash(brief_dict: Dict[str, Any]) -> str:
    """Compute deterministic SHA-256 hash matching Video Pilot digest(brief_file)."""
    return hashlib.sha256(serialize_brief_json(brief_dict).encode("utf-8")).hexdigest()


def calculate_proportional_durations(
    total_duration: float,
    scene_count: int = 5,
) -> List[float]:
    """Calculate scene duration budgets for conversational narrative arcs.

    For the standard 5-part conversational arc (Hook -> Reframe -> Causal 70/30 -> Contrast -> Loop Payoff),
    allocates according to empirical ratios (14%, 20%, 32%, 20%, 14%).
    For other scene counts, allocates an even distribution reconciling rounding differences.
    """
    if scene_count <= 0:
        raise ValueError("scene_count must be positive")
    if total_duration <= 0:
        raise ValueError("total_duration must be positive")

    if scene_count == 5:
        ratios = [0.14, 0.20, 32 / 100.0, 0.20, 0.14]
    else:
        ratios = [1.0 / scene_count] * scene_count

    raw_durations = [round(total_duration * r, 1) for r in ratios]
    diff = round(total_duration - sum(raw_durations), 1)
    if abs(diff) > 0.01:
        max_idx = raw_durations.index(max(raw_durations))
        raw_durations[max_idx] = round(raw_durations[max_idx] + diff, 1)

    return raw_durations


def calculate_scene_syllable_budget(
    duration: float,
    is_last: bool = False,
    pause_seconds: float = 0.0,
    nominal_rate: float = NOMINAL_SPEECH_RATE,
) -> int:
    """Calculate target syllables for a scene using the acoustic dead-air formula."""
    return calculate_target_syllables(
        duration=duration,
        is_last=is_last,
        pause_seconds=pause_seconds,
        nominal_rate=nominal_rate,
        p_tail_para=DEFAULT_P_TAIL_PARA,
        p_tail_last=DEFAULT_P_TAIL_LAST,
    )


def build_brief_v3(topic: ResearchedTopic, system_root: Optional[Path] = None) -> Dict[str, Any]:
    """Build schema 3.0 compliant brief dictionary."""
    clean_sources = []
    for s in topic.sources:
        clean_sources.append({
            "id": s["id"],
            "title": s["title"],
            "reference": s["reference"],
            "facts": list(s["facts"]),
        })

    lang = getattr(topic, "language", "vi")
    cfg_voice = "VietNarrator"
    cfg_speed = 1.0
    cfg_en_voice = "VietNarrator"
    cfg_en_speed = 1.0
    root_dir = system_root or SYS_DIR
    cfg_path = root_dir / "config.json"
    if cfg_path.is_file():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            colab_tts = cfg.get("colab_tts", {})
            if colab_tts.get("enabled") and colab_tts.get("voices", {}).get("vi"):
                vi_prof_path = root_dir / colab_tts["voices"]["vi"]
                if vi_prof_path.is_file():
                    vi_prof = json.loads(vi_prof_path.read_text(encoding="utf-8"))
                    cfg_voice = vi_prof.get("voice", cfg_voice)
                cfg_speed = float(colab_tts.get("vi_speed", cfg_speed))
            else:
                cfg_voice = cfg.get("tts_voice", cfg_voice)
                cfg_speed = float(cfg.get("tts_speed", cfg_speed))
            cfg_en_voice = cfg.get("en_voice", cfg_en_voice)
            cfg_en_speed = float(cfg.get("en_speed", cfg_en_speed))
        except Exception:
            pass

    if getattr(topic, "voice", None):
        if lang == "en":
            cfg_en_voice = str(topic.voice)
        else:
            cfg_voice = str(topic.voice)
    if getattr(topic, "speed", None) is not None:
        if lang == "en":
            cfg_en_speed = float(topic.speed)
        else:
            cfg_speed = float(topic.speed)

    if topic.aspect_ratio == "dual":
        outputs = [
            {
                "aspect_ratio": "9:16",
                "language": lang,
                "subtitles": True,
                "voice": cfg_voice if lang == "vi" else cfg_en_voice,
                "speed": cfg_speed if lang == "vi" else cfg_en_speed,
            },
            {
                "aspect_ratio": "16:9",
                "language": "en" if lang == "en" or any(s.narration_en for s in topic.scenes) else lang,
                "subtitles": False,
                "voice": cfg_en_voice if ("en" if lang == "en" or any(s.narration_en for s in topic.scenes) else lang) == "en" else cfg_voice,
                "speed": cfg_en_speed if ("en" if lang == "en" or any(s.narration_en for s in topic.scenes) else lang) == "en" else cfg_speed,
            },
        ]
    else:
        sub_val = topic.subtitles if getattr(topic, "subtitles", None) is not None else (topic.aspect_ratio == "9:16")
        outputs = [
            {
                "aspect_ratio": topic.aspect_ratio,
                "language": lang,
                "subtitles": bool(sub_val),
                "voice": cfg_voice if lang == "vi" else cfg_en_voice,
                "speed": cfg_speed if lang == "vi" else cfg_en_speed,
            }
        ]

    from format_profiles import default_text_style, resolve_format_profile

    resolved_profile = resolve_format_profile({
        "aspect_ratio": topic.aspect_ratio,
        "format_profile": getattr(topic, "format_profile", None),
    })
    duration_val = (
        {"min_seconds": topic.min_duration, "max_seconds": topic.max_duration}
        if topic.min_duration is not None and topic.max_duration is not None
        else None
    )

    brief = {
        "schema_version": "3.0",
        "topic": topic.topic,
        "audience": topic.audience,
        "goal": topic.goal,
        "video_type": topic.video_type,
        "duration": duration_val,
        "scene_count": len(topic.scenes),
        "required_points": [{"id": r["id"], "text": r["text"]} for r in topic.required_points],
        "language": lang,
        "tone": topic.tone,
        "style": topic.style,
        "aspect_ratio": topic.aspect_ratio,
        "format_profile": resolved_profile,
        "facts_required": bool(len(clean_sources) > 0),
        "sources": clean_sources,
        "outputs": outputs,
        "planning": {
            "success_criteria": [topic.goal],
            "avoid": ["Tránh lối diễn đạt giáo điều, sáo rỗng hoặc thuật ngữ hàn lâm không giải thích."],
            "prior_knowledge": "Không đòi hỏi kiến thức chuyên sâu từ trước.",
            "pacing": "Theo lời dẫn tự nhiên Conversational Essayist, cân chỉnh triệt tiêu dead-air.",
            "domain_requirements": [],
            "assumptions": ["Mỗi phân cảnh được cân chỉnh theo công thức âm học P_tail và dung sai drift <= 0.3s."],
            "text_style": default_text_style(topic.aspect_ratio),
            "speech_rates": {
                "vi": {
                    "units_per_second": NOMINAL_SPEECH_RATE,
                    "uncertainty": 0.15,
                    "source": "Acoustic calibrated cadence",
                },
                "en": {
                    "units_per_second": 2.5,
                    "uncertainty": 0.25,
                    "source": "Estimated English reading rate",
                },
            },
        },
    }
    if getattr(topic, "conversational_facts", None) is not None:
        brief["conversational_facts"] = bool(topic.conversational_facts)
    if getattr(topic, "packaging", None) is not None:
        pkg_dict = topic.packaging.to_dict() if hasattr(topic.packaging, "to_dict") else dict(topic.packaging)
        brief["packaging"] = pkg_dict
        brief["youtube_title"] = pkg_dict["youtube_title"]
        brief["thumbnail_spec"] = pkg_dict["thumbnail_spec"]
        brief["channel_pillar"] = pkg_dict["channel_pillar"]
        brief["funnel_tier"] = pkg_dict["funnel_tier"]
        if pkg_dict.get("seo_keywords"):
            brief["seo_keywords"] = list(pkg_dict["seo_keywords"])
    if getattr(topic, "human_editorial", None) is not None:
        he_val = topic.human_editorial
        brief["human_editorial"] = he_val.to_dict() if hasattr(he_val, "to_dict") else dict(he_val)
    if topic.visual_pacing_profile is not None:
        brief['visual_pacing_profile'] = topic.visual_pacing_profile
    if getattr(topic, "enable_sound_design", None) is not None:
        brief["enable_sound_design"] = bool(topic.enable_sound_design)
    if getattr(topic, "spinoff_shorts", None):
        brief["spinoff_shorts"] = list(topic.spinoff_shorts)
    return brief


def compose_full_frame_description(environment: str, figure_action: str) -> str:
    """Combine a setting and visible action into a complete full-frame scene description."""
    return f"{environment.strip().rstrip('.')}. {figure_action.strip().rstrip('.')}. Render one integrated full-frame composition with figures and props physically grounded in the setting."


def _phrase_anchors(text: str, count: int) -> List[Tuple[str, int]]:
    """Split narration into ordered, exact-word anchors for scene briefs."""
    tokens = [match for match in re.finditer(r"\S+", text) if not match.group().lower().startswith("[pause:")]
    if not tokens:
        raise ValueError("A full-frame visual beat needs narration text")
    count = max(1, min(count, len(tokens)))
    anchors: List[Tuple[str, int]] = []
    last_end = -1
    for index in range(count):
        target_offset = round(index * len(text) / count)
        target = next(
            (token_index for token_index, token in enumerate(tokens) if token.start() >= target_offset),
            len(tokens) - 1,
        )
        selected = None
        for start in range(target, len(tokens)):
            end = min(start + 1, len(tokens) - 1)
            quote = text[tokens[start].start():tokens[end].end()]
            if "[pause:" in quote.lower():
                quote = tokens[start].group()
            position = text.find(quote, last_end + 1)
            if position <= last_end:
                continue
            occurrence = 0
            cursor = 0
            while True:
                found = text.find(quote, cursor)
                if found < 0 or found > position:
                    break
                occurrence += 1
                if found == position:
                    break
                cursor = found + len(quote)
            if occurrence:
                selected = (quote, occurrence, position)
                break
        if selected is None:
            break
        quote, occurrence, position = selected
        anchors.append((quote, occurrence))
        last_end = position + len(quote) - 1
    return anchors


def _default_full_frame_beats(scene: ResearchedScene, elapsed: float) -> List[ResearchedVisualBeat]:
    """Create full-frame beats from scene briefs using opening/body hold targets and a max-2 variation streak cap."""
    opening_seconds = max(0.0, min(scene.duration, 15.0 - elapsed))
    body_seconds = max(0.0, scene.duration - opening_seconds)
    count = max(1, math.ceil(opening_seconds / 1.5) + math.ceil(body_seconds / 2.5))
    vi_anchors = _phrase_anchors(scene.narration, count)
    en_anchors = _phrase_anchors(scene.narration_en, len(vi_anchors)) if scene.narration_en else []
    if en_anchors and len(en_anchors) < len(vi_anchors):
        vi_anchors = vi_anchors[:len(en_anchors)]
    base_description = scene.scene_description or compose_full_frame_description(scene.setting, scene.action)
    beats = []
    variation_streak = 0
    for index, (quote, occurrence) in enumerate(vi_anchors):
        image_id = f"{scene.scene_id}_I{index + 1}"
        focus_kind = (
            "punch_in" if re.search(r"\d|\b(giờ|phút|lần|tầng|số|năm)\b", quote, re.I)
            else "cut"
        )
        # Cap consecutive variations at MAX_CONSECUTIVE_VARIATION_BEATS (2) to prevent static room boredom
        is_variation = index > 0 and variation_streak < MAX_CONSECUTIVE_VARIATION_BEATS
        if is_variation:
            variation_streak += 1
            shot_type = "variation"
        else:
            variation_streak = 0
            shot_type = "full_scene" if index == 0 else "macro_prop"
        description = (
            f"{base_description} Visual focus: {quote}. "
            "Keep the character and props physically integrated in the complete scene; do not render the phrase as lettering."
        )
        beats.append(ResearchedVisualBeat(
            image_id=image_id,
            description=description,
            anchor_quote=quote,
            anchor_occurrence=occurrence,
            anchor_quote_en=en_anchors[index][0] if en_anchors else None,
            anchor_occurrence_en=en_anchors[index][1] if en_anchors else 1,
            reason="Full-frame visual beat tied to a concrete narration phrase.",
            character_ids=list(scene.character_ids),
            effect=focus_kind if not is_variation else ("cut" if focus_kind == "punch_in" else "fade"),
            based_on=f"{scene.scene_id}_I{index}" if is_variation else None,
            preserve=(
                f"Keep the same setting ({scene.setting}), character design, and surrounding props."
                if is_variation else ""
            ),
            change=(
                f"Shift the full-frame emphasis to this next narrated action or object: {quote}."
                if is_variation else (
                    "Establish the complete scene and its opening action."
                    if index == 0 else f"Cut to a fresh focal angle emphasizing: {quote}."
                )
            ),
            shot_type=shot_type,
        ))
    return beats




def _infer_scene_tone(index: int, total: int, title: str, narration: str) -> str:
    """Modulate voice tone dynamically from dramatic/cognitive intent rather than flat 20/60/20 slicing."""
    combined = f"{title} {narration}".casefold()
    if index <= max(1, total // 5):
        return "narrative_warm"
    if index > total - max(1, total // 5):
        return "reflective_slow"
    if re.search(r"\?|tại sao|nhưng|nghịch lý|tưởng rằng|ảo giác|sụp đổ|thật sự|khựng lại", combined):
        return "reflective_slow" if "?" in title or "tại sao" in combined or "sụp đổ" in combined else "narrative_warm"
    return "analytical_crisp"


def _select_best_coverage_quote(narration: str, req_text: str) -> str:
    """Pick the sentence in narration with highest lexical overlap with req_text, falling back to first sentence."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", narration) if s.strip()]
    if not sentences:
        return narration[:30].strip()
    req_tokens = {w for w in re.findall(r"\w+", (req_text or "").casefold()) if len(w) > 2}
    if req_tokens:
        best_sent = max(
            sentences,
            key=lambda s: sum(1 for w in req_tokens if w in s.casefold()),
        )
        if sum(1 for w in req_tokens if w in best_sent.casefold()) > 0:
            cleaned = best_sent.rstrip(".!?").strip()
            if cleaned and cleaned in narration:
                return cleaned
            if best_sent in narration:
                return best_sent
    first = narration.split(".")[0].strip()
    return first if first in narration else narration[:30].strip()


_HUMAN_ACTOR_KEYWORDS_RE = re.compile(
    r"\b(?:student|learner|figure|stick-figure|stick_figure|person|human|hand(?!-drawn)|hands|finger|fingers|researcher|"
    r"traveler|mountaineer|psychologist|psychologists|lecturer|audience|committee|character|actor|people|"
    r"nhân vật|người|sinh viên|giảng viên|nhà nghiên cứu|lữ hành|bàn tay|ngón tay)\b",
    re.IGNORECASE,
)


_GENERAL_STOPWORDS = {
    "là", "và", "của", "cho", "với", "trong", "trên", "dưới", "khi", "mà", "để", "như", "rằng",
    "thì", "bị", "được", "này", "đó", "kia", "ấy", "lại", "cũng", "đã", "đang", "sẽ", "chỉ",
    "vẫn", "rất", "quá", "lắm", "hãy", "phải", "nào", "gì", "sao", "ai", "đâu", "nhiều", "ít",
    "thêm", "bớt", "ra", "vào", "lên", "xuống", "về", "từ", "đến", "qua", "bởi", "tại", "theo",
    "nếu", "nhưng", "thế", "vậy", "thực sự", "hoàn toàn", "chính", "mình", "bạn", "họ", "chúng ta",
    "tôi", "rồi", "ngay", "luôn", "chưa", "tự", "do", "vì", "ở", "đây", "càng", "khiến", "làm",
    "the", "and", "or", "of", "to", "in", "on", "at", "by", "for", "with", "about", "against",
    "between", "into", "through", "during", "before", "after", "above", "below", "from", "up",
    "down", "out", "off", "over", "under", "again", "further", "then", "once",
}



def extract_sentence_semantic_elements(sentence: str) -> Dict[str, Any]:
    """Dynamically extract verbs, nouns, quantities, and comparative structures from any narration sentence.
    Follows General Dynamic Reasoning Invariant: operates strictly via language structure without hardcoded topic templates.
    """
    text = sentence.strip()
    # 1. Quantities / metrics
    numbers = re.findall(
        r"(?:\d+(?:[.,]\d+)?%?|\b(?:bảy mươi|năm mươi|hai mươi|mười|một trăm|năm trăm|hàng trăm|trăm|một nghìn|nghìn|hàng nghìn|hàng triệu|hai|ba|bốn|năm|sáu|bảy|tám|chín)\s*(?:phần trăm|giờ|phút|từ|bài|người|sinh viên)?\b)",
        text,
        re.IGNORECASE,
    )
    # 2. Key Vietnamese/English active verbs
    action_verbs = re.findall(
        r"(?:\b(?:bắt đầu|phá vỡ|đánh bại|thú nhận|khảo sát|phỏng vấn|đối xử|đặt tên|leo|đứng|nở rộng|"
        r"bóp nghẹt|nhìn thấy|mở ra|thì thầm|gõ|xóa|xuất hiện|tiến lên|chuyển|vượt quá|nhận ra|"
        r"vận chuyển|sụt giảm|tạo thành|khóa|đè bẹp|"
        r"shatters|crushes|climbs|tears|ignites|throws|plants|types|confesses|expands|breaks|stamps|tilts)\b)",
        text,
        re.IGNORECASE,
    )
    # 3. Contrast / comparison markers
    contrast_markers = re.findall(
        r"(?:\b(?:càng\b.*?\bcàng|nhưng|ngược lại|đánh bại|thay vì|hơn|kém|khác|đối nghịch|vs|>|<)\b)",
        text,
        re.IGNORECASE,
    )

    # 4. Dynamic linguistic extraction for nouns and conceptual entities (general across any domain)
    nouns: List[str] = []
    # Phrases following classifiers / markers
    classifier_pats = [
        r"\b(?:các|những|mỗi|từng|chiếc|cái|con|bức|tờ|bản|cuộc|sự|nỗi|mối|hạt|khối|khoảng|vùng|mô|tế bào|hệ|đoàn|quân|cửa|sông|dòng)\s+([a-zA-ZÀ-ỹ0-9_]+(?:\s+[a-zA-ZÀ-ỹ0-9_]+)?)\b",
        r"\b([a-zA-ZÀ-ỹ0-9_]+(?:\s+[a-zA-ZÀ-ỹ0-9_]+)?)\s+(?:của|trong|trên|dưới|về)\b",
    ]
    for pat in classifier_pats:
        for m in re.finditer(pat, text, re.IGNORECASE):
            chunk = m.group(1).strip()
            subwords = chunk.split()
            valid_sub = [w for w in subwords if w.lower() not in _GENERAL_STOPWORDS]
            if valid_sub:
                val = " ".join(valid_sub)
                if len(val) >= 3 and val.lower() not in _GENERAL_STOPWORDS:
                    nouns.append(val)

    # Capitalized phrases (Proper nouns or mid-sentence topics)
    tokens = text.split()
    for tok in tokens[1:]:
        clean = re.sub(r"[^\wÀ-ỹ]", "", tok)
        if clean and clean[0].isupper() and clean.lower() not in _GENERAL_STOPWORDS:
            nouns.append(clean)

    # Content word n-grams (not in stopwords, length >= 3)
    words = re.findall(r"[a-zA-ZÀ-ỹ0-9_]+", text)
    for i, w in enumerate(words):
        if w.lower() not in _GENERAL_STOPWORDS and len(w) >= 3 and not w.isdigit():
            if i + 1 < len(words):
                w2 = words[i + 1]
                if w2.lower() not in _GENERAL_STOPWORDS and len(w2) >= 3 and not w2.isdigit():
                    phrase = f"{w} {w2}"
                    if phrase not in nouns:
                        nouns.append(phrase)
            if w not in nouns and not any(w in n for n in nouns):
                nouns.append(w)

    # Deduplicate while preserving order
    seen = set()
    cleaned_nouns: List[str] = []
    for n in nouns:
        n_low = n.lower()
        if n_low not in seen:
            seen.add(n_low)
            cleaned_nouns.append(n)

    return {
        "text": text,
        "metrics": numbers,
        "verbs": action_verbs,
        "nouns": cleaned_nouns,
        "contrasts": contrast_markers,
    }


def derive_see_say_visual_action(
    sentence: str,
    shot_type: str = "full_scene",
    setting: str = "",
    character_id: str = "",
) -> str:
    """Dynamically derive an authentic 2D explainer visual action from any spoken sentence on the fly.
    Grounded directly in real-world people, animals, objects, experiments, and everyday situations.
    Zero abstract void or cookie-cutter fallback templates.
    """
    sem = extract_sentence_semantic_elements(sentence)
    noun_label = ", ".join(sem["nouns"][:2]) if sem["nouns"] else "narrated subject"
    metric_label = sem["metrics"][0] if sem["metrics"] else ""
    contrast_label = sem["contrasts"][0] if sem["contrasts"] else ""

    if shot_type == "visual_diagram":
        if metric_label:
            return f"Hand-drawn analytical breakdown displaying exact figures for {noun_label} labeled {metric_label} on uncluttered paper."
        elif contrast_label or "đánh bại" in sentence.lower():
            return f"Hand-drawn side-by-side comparison contrasting two distinct physical states of {noun_label} on uncluttered paper."
        else:
            return f"Hand-drawn structural overview mapping the direct physical relationships of {noun_label} on clean paper."

    elif shot_type == "concept_metaphor":
        if any(w in sentence.lower() for w in ("sợ", "bế tắc", "nguy hiểm", "xiềng xích", "khó")):
            return f"Hand-drawn tangible physical interaction showing resistance and tension applied to {noun_label} on solid ground."
        elif any(w in sentence.lower() for w in ("nở rộng", "lớn", "mênh mông", "biển", "núi")):
            return f"Hand-drawn expansive landscape showing physical boundaries extending outward around {noun_label} in natural daylight."
        else:
            return f"Hand-drawn tangible physical object illustrating the working dynamics of {noun_label} in an everyday setting."

    elif shot_type == "cutaway_detail":
        return f"Hand-drawn cross-section revealing the internal components and mechanisms of {noun_label} with precise line work."

    elif shot_type == "variation":
        return f"A person continues the physical task, handling {noun_label} while adjusting posture and focus."

    else:  # full_scene
        return f"A person in everyday attire actively works with {noun_label}, demonstrating the physical action in the scene."


def validate_see_say_alignment(sentence: str, visual_desc: str) -> bool:
    """Verify lexical or conceptual connection between spoken sentence and visual prompt.
    Performs dynamic linguistic token overlap and semantic checking without a static concept map.
    Returns True when visual elements bind to sentence metrics, key entities, or concepts.
    Returns False when the visual prompt is completely disconnected from the spoken sentence.
    """
    if not sentence or not visual_desc or not sentence.strip() or not visual_desc.strip():
        return False
    s_low = sentence.lower()
    v_low = visual_desc.lower()

    # 1. Direct lexical token overlap (words >= 4 chars, not digits, not stopwords)
    words = re.findall(r"[a-zA-ZÀ-ỹ0-9_]+", s_low)
    for w in words:
        if len(w) >= 4 and not w.isdigit() and w not in _GENERAL_STOPWORDS and re.search(r"\b" + re.escape(w) + r"\b", v_low):
            return True

    # 2. Transliterated / unaccented token overlap for Vietnamese terms
    import unicodedata
    s_unaccent = "".join(c for c in unicodedata.normalize("NFD", s_low) if unicodedata.category(c) != "Mn")
    v_unaccent = "".join(c for c in unicodedata.normalize("NFD", v_low) if unicodedata.category(c) != "Mn")
    words_unaccent = re.findall(r"[a-zA-Z0-9_]+", s_unaccent)
    for w in words_unaccent:
        if len(w) >= 4 and not w.isdigit() and w not in _GENERAL_STOPWORDS and re.search(r"\b" + re.escape(w) + r"\b", v_unaccent):
            return True

    # 3. Dynamic semantic checking using extracted semantic elements
    sem = extract_sentence_semantic_elements(sentence)
    for noun in sem.get("nouns", []):
        n_clean = noun.lower().strip()
        n_unaccent = "".join(c for c in unicodedata.normalize("NFD", n_clean) if unicodedata.category(c) != "Mn")
        for chunk in (n_clean, n_unaccent):
            for part in chunk.split():
                if len(part) >= 4 and not part.isdigit() and part not in _GENERAL_STOPWORDS and re.search(r"\b" + re.escape(part) + r"\b", v_low):
                    return True

    # Semantic alignment for contrast structures with shared comparative intent
    contrast_markers = sem.get("contrasts", [])
    if contrast_markers:
        has_visual_contrast = bool(re.search(r"\b(?:comparison|contrasting|versus|vs|opposing|weighing more than|weigh|greater than|balance|scale)\b", v_low))
        if has_visual_contrast:
            s_numbers = re.findall(r"\b\d+\b", s_low)
            v_numbers = re.findall(r"\b\d+\b", v_low)
            if s_numbers and any(n in v_numbers for n in s_numbers):
                return True
            for w in words:
                if len(w) >= 3 and not w.isdigit() and w not in _GENERAL_STOPWORDS and w in v_low:
                    return True

    # Dynamic metric unit alignment (e.g. 500 từ / words, 1000 giờ / hours)
    metric_unit_pairs = [
        (r"\b\d+\s*từ\b", r"\b\d+\s*words?\b"),
        (r"\b\d+\s*giờ\b", r"\b\d+\s*hours?\b"),
        (r"\b\d+\s*phút\b", r"\b\d+\s*minutes?\b"),
        (r"\b\d+\s*người\b", r"\b\d+\s*people\b"),
        (r"\b\d+\s*%\b", r"\b\d+\s*%\b"),
        (r"\b\d+\s*phần trăm\b", r"\b\d+\s*percent\b"),
    ]
    for s_pat, v_pat in metric_unit_pairs:
        s_m = re.search(s_pat, s_low)
        v_m = re.search(v_pat, v_low)
        if s_m and v_m:
            return True

    return False


def build_scenes_from_story_rows(
    story_rows: Any,
    character_id: str = "",
    nominal_rate: float = NOMINAL_SPEECH_RATE,
    characters: Optional[Any] = None,
    visual_contract: str = "1.7.0",
) -> List[ResearchedScene]:
    """Flash-agent friendly builder: converts story rows into fully anchored, cadence-calibrated
    ResearchedScene objects with dynamic contextual character resolution and action progression.
    Supports 3-tuple (title, setting, rows), 4-tuple, 5-tuple, and 6-tuple story rows.
    """
    from flow_prompts import find_visual_cliche
    from flow_prompts.compiler import find_laziness_pattern

    built_scenes: List[ResearchedScene] = []
    total = len(story_rows)
    for index, item in enumerate(story_rows, 1):
        scene_id = f"SC{index:02d}"
        scene_char_id = character_id
        scene_tone = None
        scene_phase = None
        if len(item) == 3:
            title, setting, rows = item
        elif len(item) == 4 and isinstance(item[2], list):
            title, setting, rows, scene_char_id = item
        elif len(item) == 4 and isinstance(item[3], list):
            title, setting, scene_tone, rows = item
        elif len(item) == 5 and isinstance(item[4], list):
            title, setting, scene_tone, scene_phase, rows = item
        elif len(item) == 6 and isinstance(item[5], list):
            title, setting, scene_tone, _spoken_style, scene_phase, rows = item
        else:
            title, setting = item[0], item[1]
            rows = item[-1]

        cliche = find_visual_cliche(setting)
        if cliche:
            raise ValueError(f"FLOW_CLICHE_FORBIDDEN in {scene_id} setting: contains banned {cliche}")
        laziness = find_laziness_pattern(setting, version=visual_contract)
        if laziness:
            name, token = laziness
            raise ValueError(f"LAZY_VISUAL_ACTION_FORBIDDEN in {scene_id} setting: contains banned {name} ({token!r})")

        # Dynamically infer primary scene character if declared in row specs
        inferred_scene_char = None
        for _, spec in rows:
            raw_shot = spec.partition("|")[0].strip()
            if ":" in raw_shot:
                _, _, c_part = raw_shot.partition(":")
                c_part = c_part.strip()
                if c_part and c_part.lower() not in ("none", "no_char", "character_free", "free", "empty"):
                    chars = [c.strip() for c in c_part.split(",") if c.strip()]
                    if chars:
                        inferred_scene_char = chars[0]
                        break
        if inferred_scene_char and scene_char_id == "CH01":
            scene_char_id = inferred_scene_char

        narration = " ".join(sent.strip() for sent, _ in rows if sent.strip())
        beats: List[ResearchedBeat] = []
        base_id: Optional[str] = None
        seen_quotes: Dict[str, int] = {}
        variation_streak = 0
        for beat_idx, (sentence, spec) in enumerate(rows, 1):
            raw_shot, _, action_desc = spec.partition("|")
            raw_shot = raw_shot.strip()
            action_desc = action_desc.strip() or spec.strip()

            if ":" in raw_shot:
                shot_type, _, char_part = raw_shot.partition(":")
                shot_type = shot_type.strip() or "full_scene"
                char_part = char_part.strip()
                if char_part.lower() in ("none", "no_char", "character_free", "free", "empty"):
                    explicit_chars: List[str] = []
                    has_explicit_chars = True
                else:
                    explicit_chars = [c.strip() for c in char_part.split(",") if c.strip()]
                    has_explicit_chars = True
            else:
                shot_type = raw_shot or "full_scene"
                explicit_chars = []
                has_explicit_chars = False

            # Cap consecutive variations at MAX_CONSECUTIVE_VARIATION_BEATS (2)
            if shot_type == "variation":
                if variation_streak >= MAX_CONSECUTIVE_VARIATION_BEATS:
                    shot_type = "full_scene"
                    variation_streak = 0
                else:
                    variation_streak += 1
            else:
                variation_streak = 0

            image_id = f"{scene_id}_I{beat_idx}"
            quote = sentence.strip()

            # Dynamic See-Say synthesis when action_desc is not specified
            if not action_desc or action_desc == raw_shot or action_desc == shot_type:
                action_desc = derive_see_say_visual_action(
                    quote, shot_type=shot_type, setting=setting, character_id=scene_char_id
                )

            cliche = find_visual_cliche(action_desc) or find_visual_cliche(spec)
            if cliche:
                raise ValueError(f"FLOW_CLICHE_FORBIDDEN in {image_id} visual action: contains banned {cliche}")
            laziness = find_laziness_pattern(action_desc, version=visual_contract) or find_laziness_pattern(spec, version=visual_contract)
            if laziness:
                name, token = laziness
                raise ValueError(f"LAZY_VISUAL_ACTION_FORBIDDEN in {image_id} visual action: contains banned {name} ({token!r})")

            seen_quotes[quote] = seen_quotes.get(quote, 0) + 1
            if shot_type == "full_scene":
                base_id = image_id
            based_on = (base_id or f"{scene_id}_I{max(1, beat_idx - 1)}") if shot_type == "variation" else None

            has_expression_shift = bool(
                re.search(
                    r"\b(?:smile|smiles|smiling|grin|grins|grinning|frown|frowns|clench|clenches|cower|cowers|relaxes|relaxed|laugh|laughs|tears|sweat|dread|resilience|joy|paralyzed|overwhelmed|shaking|expression shift|facial shift|thay đổi biểu cảm|chuyển biểu cảm)\b",
                    action_desc,
                    re.I,
                )
            )
            preserve = (
                f"Keep the exact camera angle, room geometry and props in {setting}. "
                "Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift."
                if based_on else ""
            )
            desc = f"{setting} {action_desc}".strip()
            cliche = find_visual_cliche(desc)
            if cliche:
                raise ValueError(f"FLOW_CLICHE_FORBIDDEN in {image_id} description: contains banned {cliche}")
            laziness = find_laziness_pattern(desc, version=visual_contract)
            if laziness:
                name, token = laziness
                raise ValueError(f"LAZY_VISUAL_ACTION_FORBIDDEN in {image_id} description: contains banned {name} ({token!r})")

            if has_explicit_chars:
                beat_char_ids = list(explicit_chars)
            else:
                if shot_type in ("still_life", "environment", "visual_diagram", "cutaway_detail"):
                    beat_char_ids = []
                elif shot_type in ("full_scene", "variation"):
                    beat_char_ids = [scene_char_id] if scene_char_id else []
                elif shot_type in ("concept_metaphor", "macro_prop", "white_card", "white_isolated"):
                    if _HUMAN_ACTOR_KEYWORDS_RE.search(action_desc):
                        beat_char_ids = [scene_char_id] if scene_char_id else []
                    else:
                        beat_char_ids = []

            beats.append(ResearchedBeat(
                image_id=image_id,
                description=desc,
                anchor_quote=quote,
                anchor_occurrence=seen_quotes[quote],
                reason="Narration-locked full-frame beat.",
                character_ids=beat_char_ids,
                effect="cut",
                based_on=based_on,
                preserve=preserve,
                change=action_desc,
                shot_type=shot_type,
                allow_expression_shift=True if has_expression_shift and shot_type == "variation" else None,
            ))

        scene_char_ids: List[str] = []
        for b in beats:
            for cid in b.character_ids:
                if cid and cid not in scene_char_ids:
                    scene_char_ids.append(cid)
        if not scene_char_ids and scene_char_id:
            scene_char_ids = [scene_char_id]

        is_last = index == total
        p_tail = DEFAULT_P_TAIL_LAST if is_last else DEFAULT_P_TAIL_PARA
        pause_sec, _, _ = extract_pauses(narration)
        syl = count_syllables(narration, lang="vi")
        duration = round(pause_sec + (syl / nominal_rate) + p_tail, 2)
        tone = scene_tone or _infer_scene_tone(index, total, title, narration)
        resolved_phase = scene_phase or infer_editorial_section(index, total, title, narration)
        first_action = rows[0][1].partition("|")[2].strip() if rows else title
        built_scenes.append(ResearchedScene(
            scene_id=scene_id,
            title=title,
            purpose=f"Triển khai bước {index}: {title.lower()}",
            duration=duration,
            narration=narration,
            requirements=[],
            source_ids=[],
            character_ids=scene_char_ids,
            action=first_action or title,
            setting=setting,
            camera="Semantic full-frame sequence",
            visual_beats=beats,
            tone=tone,
            narrative_phase=resolved_phase,
        ))
    return built_scenes


def build_content_v3(
    topic: ResearchedTopic,
    brief_data: Dict[str, Any],
    brief_hash: str,
    brief_revision: int = 1,
) -> Dict[str, Any]:
    """Build schema 3.0 compliant content dictionary."""
    content_scenes = []
    coverage = []
    claims = []
    req_map = {r["id"]: r["text"] for r in topic.required_points}
    brief_langs = [x["language"] for x in brief_data.get("outputs", [])]
    brief_langs = list(dict.fromkeys(brief_langs)) or [brief_data.get("language", "vi")]
    needs_en = "en" in brief_langs
    elapsed = 0.0

    from flow_prompts import find_visual_cliche
    from flow_prompts.compiler import find_laziness_pattern

    if topic.style:
        cliche = find_visual_cliche(topic.style)
        if cliche:
            raise ValueError(f"FLOW_CLICHE_FORBIDDEN in topic style: contains banned {cliche}")
        laziness = find_laziness_pattern(topic.style)
        if laziness:
            name, token = laziness
            raise ValueError(f"LAZY_VISUAL_ACTION_FORBIDDEN in topic style: contains banned {name} ({token!r})")
    for ch in topic.characters:
        for f in ("appearance", "outfit", "name"):
            val = ch.get(f) if isinstance(ch, dict) else getattr(ch, f, None)
            if val and isinstance(val, str):
                cliche = find_visual_cliche(val)
                if cliche:
                    ch_id = ch.get("id") if isinstance(ch, dict) else getattr(ch, "id", "character")
                    raise ValueError(f"FLOW_CLICHE_FORBIDDEN in character {ch_id} {f}: contains banned {cliche}")
                laziness = find_laziness_pattern(val)
                if laziness:
                    ch_id = ch.get("id") if isinstance(ch, dict) else getattr(ch, "id", "character")
                    raise ValueError(f"LAZY_VISUAL_ACTION_FORBIDDEN in character {ch_id} {f}: contains banned {name} ({token!r})")

    for sc in topic.scenes:
        s_id = sc.scene_id
        for f in ("setting", "action", "bg_description", "scene_description"):
            val = getattr(sc, f, None) if not isinstance(sc, dict) else sc.get(f)
            if val and isinstance(val, str):
                cliche = find_visual_cliche(val)
                if cliche:
                    raise ValueError(f"FLOW_CLICHE_FORBIDDEN in {s_id} {f}: contains banned {cliche}")
                laziness = find_laziness_pattern(val)
                if laziness:
                    name, token = laziness
                    raise ValueError(f"LAZY_VISUAL_ACTION_FORBIDDEN in {s_id} {f}: contains banned {name} ({token!r})")

        visual_beats = sc.visual_beats or _default_full_frame_beats(sc, elapsed)
        images: List[Dict[str, Any]] = []
        beats: List[Dict[str, Any]] = []
        for beat_idx, visual in enumerate(visual_beats, 1):
            if not visual.anchor_quote.strip():
                raise ValueError(f"{s_id}/{visual.image_id}: visual beat needs a narration anchor")
            if visual.based_on and not visual.preserve.strip():
                raise ValueError(f"{s_id}/{visual.image_id}: based_on needs a preserve description")
            if not visual.change.strip():
                raise ValueError(f"{s_id}/{visual.image_id}: visual beat needs a change description")
            for field_name, val in [("description", visual.description), ("preserve", visual.preserve), ("change", visual.change)]:
                if val:
                    cliche = find_visual_cliche(val)
                    if cliche:
                        raise ValueError(f"FLOW_CLICHE_FORBIDDEN in {s_id}/{visual.image_id} {field_name}: contains banned {cliche}")
                    laziness = find_laziness_pattern(val)
                    if laziness:
                        name, token = laziness
                        raise ValueError(f"LAZY_VISUAL_ACTION_FORBIDDEN in {s_id}/{visual.image_id} {field_name}: contains banned {name} ({token!r})")
            for vt in getattr(visual, "visible_text", []):
                if isinstance(vt, str):
                    cliche = find_visual_cliche(vt)
                    if cliche:
                        raise ValueError(f"FLOW_CLICHE_FORBIDDEN in {s_id}/{visual.image_id} visible_text: contains banned {cliche}")
                    laziness = find_laziness_pattern(vt)
                    if laziness:
                        name, token = laziness
                        raise ValueError(f"LAZY_VISUAL_ACTION_FORBIDDEN in {s_id}/{visual.image_id} visible_text: contains banned {name} ({token!r})")
                elif isinstance(vt, dict):
                    for subf in ("text", "placement", "object"):
                        subval = vt.get(subf)
                        if subval and isinstance(subval, str):
                            cliche = find_visual_cliche(subval)
                            if cliche:
                                raise ValueError(f"FLOW_CLICHE_FORBIDDEN in {s_id}/{visual.image_id} visible_text.{subf}: contains banned {cliche}")
                            laziness = find_laziness_pattern(subval)
                            if laziness:
                                name, token = laziness
                                raise ValueError(f"LAZY_VISUAL_ACTION_FORBIDDEN in {s_id}/{visual.image_id} visible_text.{subf}: contains banned {name} ({token!r})")

            effective_shot = "variation" if visual.based_on else visual.shot_type
            if effective_shot in ("still_life", "environment", "visual_diagram", "cutaway_detail") and not visual.character_ids:
                resolved_character_ids = []
            else:
                resolved_character_ids = list(
                    visual.character_ids if visual.character_ids is not None else sc.character_ids
                )
            image_entry: Dict[str, Any] = {
                "id": visual.image_id,
                "description": visual.description,
                "character_ids": resolved_character_ids,
                "based_on": visual.based_on,
                "preserve": visual.preserve,
                "change": visual.change,
                "reason": visual.reason,
                "visible_text": list(visual.visible_text),
                "kind": "scene",
                "shot_type": effective_shot,
            }
            if getattr(visual, "allow_expression_shift", None) is not None:
                image_entry["allow_expression_shift"] = bool(visual.allow_expression_shift)
            image_entry["has_character"] = visual.has_character if visual.has_character is not None else bool(resolved_character_ids)
            if visual.explanation is not None:
                image_entry["explanation"] = dict(visual.explanation)
            else:
                import re
                quote_text = visual.anchor_quote
                desc_text = visual.description
                quote_numbers = re.findall(r'\b\d+(?:[.,]\d+)?\b', quote_text)
                for num in quote_numbers:
                    if num not in desc_text and not any(num in str(vt) for vt in visual.visible_text):
                        desc_text = f"{desc_text} [{num}]"
                        image_entry["description"] = desc_text
                quote_words = [w.strip(".,;:!?\"'()") for w in quote_text.split() if len(w.strip(".,;:!?\"'()")) >= 2]
                src_term = quote_words[0] if quote_words else quote_text[:4]
                desc_words = [w.strip(".,;:!?\"'()") for w in desc_text.split() if len(w.strip(".,;:!?\"'()")) >= 2]
                vis_term = desc_words[0] if desc_words else desc_text[:4]
                rel = "quantity" if quote_numbers else "context"
                image_entry["explanation"] = {
                    "quote": quote_text,
                    "relation": rel,
                    "source_terms": [src_term],
                    "visual_terms": [vis_term],
                }
            images.append(image_entry)
            anchor_payload: Dict[str, Any] = {
                "vi": {
                    "quote": visual.anchor_quote,
                    "occurrence": visual.anchor_occurrence,
                }
            }
            if needs_en and sc.narration_en:
                quote_en = visual.anchor_quote_en
                if not quote_en:
                    if beat_idx != 1:
                        raise ValueError(
                            f"{s_id}/{visual.image_id}: English visual beat needs anchor_quote_en"
                        )
                    quote_en = " ".join(sc.narration_en.split()[:4]).rstrip(".,;:!?")
                anchor_payload["en"] = {
                    "quote": quote_en,
                    "occurrence": visual.anchor_occurrence_en,
                }
            safe_fx = round(min(0.65, max(0.35, float(visual.focus_x))), 2) if visual.focus_x != 0.5 else 0.5
            safe_fy = round(min(0.58, max(0.35, float(visual.focus_y))), 2) if visual.focus_y != 0.5 else 0.5
            beats.append({
                "id": f"{s_id}_B{beat_idx}",
                "image_id": visual.image_id,
                "purpose": sc.purpose,
                "anchor": anchor_payload,
                "effect": visual.effect,
                "focus": {"x": safe_fx, "y": safe_fy},
            })

        from scripts.visual_quality import apply_room_continuity
        apply_room_continuity(images)
        previous_effect = None
        for idx, (beat, image) in enumerate(zip(beats, images, strict=True)):
            if beat['effect'] in ('auto', 'cut', 'fade'):
                beat['effect'] = select_semantic_camera_effect(
                    image['description'] + ' ' + sc.camera,
                    previous_effect,
                    beat_index=idx,
                    shot_type=image.get("shot_type"),
                    narrative_phase=getattr(sc, "narrative_phase", None),
                )
            previous_effect = beat['effect']

        scene_dict = {
            "id": s_id,
            "title": sc.title,
            "purpose": sc.purpose,
            "action": sc.action,
            "setting": sc.setting,
            "camera": sc.camera,
            "narration": sc.narration,
            "requirements": list(sc.requirements),
            "character_ids": list(sc.character_ids),
            "source_ids": list(sc.source_ids),
            "images": images,
            "beats": beats,
            "layers": [],
        }
        if sc.foley_cue:
            scene_dict["foley_cue"] = sc.foley_cue
        if getattr(sc, "tone", None):
            scene_dict["tone"] = sc.tone
        if getattr(sc, "narrative_phase", None):
            scene_dict["narrative_phase"] = sc.narrative_phase
        if sc.narration_en:
            scene_dict["narration_en"] = sc.narration_en

        content_scenes.append(scene_dict)
        elapsed += sc.duration

        # Coverage: link requirements to scene quotes using semantic overlap
        for r_id in sc.requirements:
            if r_id in req_map:
                quote_cand = _select_best_coverage_quote(sc.narration, req_map[r_id])
                cov_entry = {
                    "requirement_id": r_id,
                    "scene_id": s_id,
                    "quote": quote_cand,
                }
                if needs_en and sc.narration_en:
                    quote_en_cand = _select_best_coverage_quote(sc.narration_en, req_map[r_id])
                    cov_entry["quote_en"] = quote_en_cand
                coverage.append(cov_entry)

        # Claims: link facts to source and scene
        for quote, src_id, fact_text in sc.claim_facts:
            claims.append({
                "scene_id": s_id,
                "quote": quote,
                "language": "vi",
                "source_id": src_id,
                "fact": fact_text,
            })

    outline = [
        {
            "scene_id": s.scene_id,
            "purpose": s.purpose,
            "requirements": list(s.requirements),
            "transition": "Tiếp tục theo trình tự diễn biến nội dung",
        }
        for s in topic.scenes
    ]

    content = {
        "schema_version": "3.0",
        "brief_revision": brief_revision,
        "brief_hash": brief_hash,
        "topic": brief_data["topic"],
        "duration": brief_data["duration"],
        "style": brief_data["style"],
        "required_points": [r["text"] for r in topic.required_points],
        "characters": [
            {
                "id": c["id"],
                "name": c["name"],
                "appearance": c["appearance"],
                "outfit": c["outfit"],
            }
            for c in topic.characters
        ],
        "scenes": content_scenes,
        "coverage": coverage,
        "outline": outline,
        "claims": claims,
        "revision_response": [],
        "open_questions": [],
    }
    return content


def generate_script_json(topic: ResearchedTopic) -> List[Dict[str, Any]]:
    """Generate standardized script array for cadence checker."""
    script_items = []
    elapsed = 0.0
    for s in topic.scenes:
        visuals = s.visual_beats or _default_full_frame_beats(s, elapsed)
        script_items.append({
            "id": s.scene_id,
            "duration": s.duration,
            "narration": s.narration,
            "beats": [{"image_id": beat.image_id, "anchor_quote": beat.anchor_quote} for beat in visuals],
        })
        elapsed += s.duration
    return script_items


def validate_production_bundle(
    system_root: Path,
    brief_data: Dict[str, Any],
    content_data: Dict[str, Any],
    brief_revision: int = 1,
) -> Tuple[bool, List[str]]:
    """Validate brief and content against official contracts and cadence checker."""
    from content_contract import ContractError, validate_brief, validate_content

    errors = []
    # 1. Validate Brief
    try:
        validate_brief(system_root, brief_data)
    except ContractError as ce:
        errors.append(f"validate_brief error: {ce}")
    except Exception as ex:
        errors.append(f"validate_brief unexpected exception: {ex}")

    # 2. Validate Content
    bhash = content_data["brief_hash"]
    try:
        validate_content(system_root, brief_data, brief_revision, bhash, content_data)
    except ContractError as ce:
        errors.append(f"validate_content error: {ce}")
    except Exception as ex:
        errors.append(f"validate_content unexpected exception: {ex}")

    return len(errors) == 0, errors


def _make_five_part_scene_list(specs: List[Tuple[str, str, float, str, str, List[str], List[str], str, str, str, str, List[Tuple[str, str, str]]]]) -> List[ResearchedScene]:
    """Helper to construct 5-part ResearchedScene lists concisely without boilerplate."""
    scenes: List[ResearchedScene] = []
    for sc_id, title, dur, narr_vi, narr_en, reqs, srcs, action, setting, cam, foley, claims in specs:
        scenes.append(ResearchedScene(
            scene_id=sc_id,
            title=title,
            purpose=title,
            duration=dur,
            narration=narr_vi,
            narration_en=narr_en,
            requirements=reqs,
            source_ids=srcs,
            character_ids=["CH01"],
            action=action,
            setting=setting,
            camera=cam,
            scene_description=compose_full_frame_description(setting, action),
            foley_cue=foley,
            claim_facts=claims,
        ))
    return scenes


def create_demo_trial_topic() -> ResearchedTopic:
    """Create the trial benchmark topic: 'Nghịch lý của sự Trì hoãn' (The Procrastination Paradox)."""
    sources = [
        {
            "id": "SRC01",
            "title": "Procrastination and the Priority of Short-Term Mood Regulation",
            "reference": "Dr. Timothy A. Pychyl & Dr. Fuschia M. Sirois (2013). Social and Personality Psychology Compass, 7(2), 115-127. DOI: 10.1111/spc3.12011",
            "facts": [
                "Trì hoãn thực chất là né tránh căng thẳng, không phải vì lười biếng.",
                "Hạch hạnh nhân xem áp lực công việc là mối đe dọa sinh tồn trực tiếp.",
                "Bộ não luôn ưu tiên cảm giác an tâm tức thì hơn tương lai xa.",
            ],
        },
        {
            "id": "SRC02",
            "title": "The Neurobiology of Procrastination: Prefrontal Cortex and Amygdala Interaction",
            "reference": "Dr. Laura Rabin et al. (2011). Journal of Clinical and Experimental Neuropsychology, 33(3), 344-356. DOI: 10.1080/13803395.2010.518597",
            "facts": [
                "Vỏ não lý trí dễ bị cảm xúc lấn át khi đối diện quá tải.",
                "Quy tắc 5 phút giúp hạ thấp nỗi sợ và bắt đầu dễ dàng.",
            ],
        },
    ]
    required_points = [
        {"id": "R01", "text": "Khoảnh khắc mở tủ lạnh lúc nửa đêm"},
        {"id": "R02", "text": "Nghịch lý: không phải lười biếng mà là điều hòa cảm xúc"},
        {"id": "R03", "text": "Hạch hạnh nhân và cơ chế phản ứng trước mối đe dọa"},
        {"id": "R04", "text": "Đối lập giữa người cầu toàn và quy tắc hành động 5 phút"},
        {"id": "R05", "text": "Khép vòng lặp và thông điệp thấu hiểu bản thân"},
    ]
    characters = [{
        "id": "CH01",
        "name": "Nhân vật người que trải nghiệm",
        "appearance": CAST_APPEARANCE,
        "outfit": DEFAULT_OUTFIT,
    }]
    scenes = _make_five_part_scene_list([
        ("SC01", "Khoảnh khắc mở tủ lạnh lúc nửa đêm", 8.0,
         "Đúng mười một giờ ba mươi đêm ngay trước hạn chót, bạn lại đứng ngơ ngác mở tủ lạnh lần thứ tư dù bụng thực sự không hề thấy đói.",
         "Right at eleven thirty at night before deadline, you blankly open the fridge again, although you are not hungry.",
         ["R01"], [], "Nhân vật người que đứng ngơ ngác trước cánh cửa tủ lạnh mở sáng lúc nửa đêm",
         "Căn bếp gia đình tĩnh mịch đêm khuya với ánh sáng vàng nhạt từ tủ lạnh", "Trung cảnh ngang tầm mắt",
         "Click cửa tủ lạnh mở nhẹ nhàng", []),
        ("SC02", "Nghịch lý: không phải lười biếng mà là điều hòa cảm xúc", 11.0,
         "Những cuốn sách dạy thành công ngoài kia vẫn thường chỉ trích bạn là kẻ lười biếng và thiếu kỷ luật. [pause:900ms] Nhưng khoa học thần kinh hiện đại đã chứng minh một nghịch lý hoàn toàn ngược lại.",
         "Popular self-help bestsellers blame you for being lazy and undisciplined. [pause:900ms] Yet modern neuroscience reveals a completely opposite paradox.",
         ["R02"], ["SRC01"], "Nhân vật người que nhìn chồng sách tự lực rồi quay sang biểu đồ não bộ ngạc nhiên",
         "Phòng học với chồng sách kỹ năng sống và sơ đồ não bộ phát sáng trên bảng", "Toàn cảnh góc rộng",
         "Tiếng lật sách soàn soạt",
         [("khoa học thần kinh hiện đại đã chứng minh một nghịch lý hoàn toàn ngược lại", "SRC01", "Trì hoãn thực chất là né tránh căng thẳng, không phải vì lười biếng.")]),
        ("SC03", "Hạch hạnh nhân và cơ chế phản ứng trước mối đe dọa", 13.0,
         "Thực nghiệm thần kinh phát hiện ra rằng: hạch hạnh nhân trong não bộ xem bản báo cáo đầy áp lực như một mối đe dọa sinh tồn. Để bảo vệ bạn khỏi cảm giác căng thẳng tột cùng, nó lập tức kích hoạt phản xạ trốn chạy quen thuộc.",
         "Modern brain experiments discovered that the human amygdala treats a stressful report as an existential threat. To shield you from intense anxiety, it triggers a flight reflex.",
         ["R03"], ["SRC01"], "Nhân vật người que hốt hoảng trước sơ đồ vùng hạch hạnh nhân phát sáng cảnh báo",
         "Phòng thí nghiệm thần kinh với mô hình não bộ làm nổi bật vùng hạch hạnh nhân", "Cận cảnh vùng hạch hạnh nhân",
         "Âm thanh nhịp tim đập",
         [("hạch hạnh nhân trong não bộ xem bản báo cáo đầy áp lực như một mối đe dọa sinh tồn", "SRC01", "Hạch hạnh nhân xem áp lực công việc là mối đe dọa sinh tồn trực tiếp.")]),
        ("SC04", "Đối lập giữa người cầu toàn và quy tắc hành động 5 phút", 11.5,
         "Người cầu toàn luôn chờ đợi cảm hứng hoàn hảo để làm việc, và rồi bị tê liệt. Trong khi đó, người khôn ngoan chỉ bắt đầu bằng một hành động nhỏ kéo dài vỏn vẹn năm phút để đánh lừa bộ não.",
         "Perfectionists always wait for inspiration and stay paralyzed. Meanwhile, smart thinkers begin with a simple five-minute action step that easily outsmarts the brain.",
         ["R04"], ["SRC02"], "Nhân vật người que tự tin bấm đồng hồ hẹn giờ năm phút và bắt đầu viết",
         "Bàn làm việc đặt đồng hồ bấm giờ năm phút cạnh cuốn sổ ghi chú mở sẵn", "Trung cảnh đối sánh",
         "Tiếng tích tắc đồng hồ 5 phút",
         [("vỏn vẹn năm phút để đánh lừa bộ não", "SRC02", "Quy tắc 5 phút giúp hạ thấp nỗi sợ và bắt đầu dễ dàng.")]),
        ("SC05", "Khép vòng lặp và thông điệp thấu hiểu bản thân", 9.0,
         "Lần tới khi bạn muốn mở tủ lạnh lúc nửa đêm, hãy mỉm cười và nhớ rằng: bạn không hề lười biếng, mà não bạn chỉ đang lo lắng và cần được vỗ về.",
         "Next time you want to open that fridge door late at night, smile and remember: you are not lazy, your brain is only anxious and needs care.",
         ["R05"], ["SRC01"], "Nhân vật người que đóng nhẹ cửa tủ lạnh và mỉm cười thư thái quay về bàn làm việc",
         "Căn bếp ấm áp với ánh đèn bàn học tỏa sáng dịu nhẹ phía xa", "Trung cảnh mở rộng",
         "Tiếng đóng tủ lạnh êm ái", []),
    ])
    return ResearchedTopic(
        topic="Nghịch lý của sự Trì hoãn: Vì sao não bộ đông cứng trước deadline?",
        audience="Người đi làm và sinh viên thường xuyên trì hoãn công việc quan trọng",
        goal="Hiểu cơ chế né tránh căng thẳng của hạch hạnh nhân và áp dụng quy tắc 5 phút",
        video_type="science",
        min_duration=45.0,
        max_duration=60.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="16:9",
        sources=sources,
        required_points=required_points,
        characters=characters,
        scenes=scenes,
    )


def create_academic_research_paradox_topic(
    aspect_ratio: str = "9:16",
    subtitles: Optional[bool] = None,
) -> ResearchedTopic:
    """Create the canonical Academic Research & Knowledge Decoding blueprint (Tier 1 & Tier 2 Funnel)."""
    sources = [
        {
            "id": "SRC01",
            "title": "The Critical Importance of Retrieval for Learning",
            "reference": "Dr. Jeffrey D. Karpicke & Dr. Henry L. Roediger (2008). Science, 319(5865), 966-968. DOI: 10.1126/science.1152408",
            "facts": [
                "Đọc lại giáo trình nhiều lần chỉ tạo ra ảo giác hiểu bài.",
                "Não bộ chỉ thực sự nắm bản chất khi tự truy xuất thông tin.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Genre Analysis: English in Academic and Research Settings (CARS Model)",
            "reference": "Dr. John M. Swales (1990). Cambridge University Press. ISBN: 978-0521338134",
            "facts": [
                "Bài báo quốc tế bắt đầu từ khoảng trống tri thức chứ không phải Word.",
                "Hội đồng bảo vệ luôn soi khoảng trống nghiên cứu trong hai phút đầu.",
            ],
        },
    ]
    required_points = [
        {"id": "R01", "text": "Ảo giác năng lực khi tô màu kín giáo trình và mở Word lúc hai giờ sáng"},
        {"id": "R02", "text": "Sai lầm mở Word gõ ngay chương một thay vì xác định chuỗi quyết định Q1"},
        {"id": "R03", "text": "Cơ chế nhận diện mặt chữ giả tạo và chuỗi câu hỏi đến khoảng trống tri thức"},
        {"id": "R04", "text": "Đối lập giữa sao chép tài liệu rời rạc và ma trận khoảng trống nghiên cứu"},
        {"id": "R05", "text": "Làm chủ một trăm hai mươi giây đầu trước hội đồng bảo vệ khóa luận"},
    ]
    characters = [{
        "id": "CH01",
        "name": "Nhân vật người que nghiên cứu",
        "appearance": CAST_APPEARANCE,
        "outfit": DEFAULT_OUTFIT,
    }]
    scenes = _make_five_part_scene_list([
        ("SC01", "Ảo giác năng lực khi tô màu kín giáo trình và mở Word lúc hai giờ sáng", 8.0,
         "Đọc lại giáo trình năm lần chỉ tạo ra ảo giác rằng bạn hiểu bài. Hai giờ sáng trước hạn nộp bài, bạn vẫn nhìn trang Word trắng tinh.",
         "Rereading your textbook five times only creates an illusion of competence. At two in the morning before thesis deadline, you still stare at a blank Word page.",
         ["R01"], ["SRC01"], "Nhân vật người que ngồi trước màn hình soạn thảo trống rỗng và cuốn giáo trình tô kín màu vàng",
         "Bàn học sinh viên Việt Nam lúc hai giờ sáng với đèn bàn vàng ấm", "Cận cảnh đẩy nhanh vào màn hình",
         "Tiếng bút dạ quang gạch nhanh",
         [("Đọc lại giáo trình năm lần chỉ tạo ra ảo giác rằng bạn hiểu bài", "SRC01", "Đọc lại giáo trình nhiều lần chỉ tạo ra ảo giác hiểu bài.")]),
        ("SC02", "Sai lầm mở Word gõ ngay chương một thay vì xác định chuỗi quyết định Q1", 11.0,
         "Tám mươi phần trăm sinh viên làm khóa luận đều mở Word gõ ngay từ trang đầu tiên. [pause:900ms] Nhưng các giáo sư quốc tế khẳng định, bài báo khoa học không bao giờ bắt đầu ở đó.",
         "Eighty percent of students start research by opening Word and typing page one. [pause:900ms] Yet international professors confirm a scientific paper never begins there.",
         ["R02"], ["SRC02"], "Nhân vật người que dùng bút đỏ gạch chéo biểu tượng trang soạn thảo trống trước sơ đồ chuỗi nghiên cứu",
         "Phòng hướng dẫn nghiên cứu với bảng sơ đồ chuỗi từ Câu hỏi đến Khoảng trống tri thức", "Toàn cảnh góc rộng",
         "Tiếng gạch bút dứt khoát",
         [("bài báo khoa học không bao giờ bắt đầu ở đó", "SRC02", "Bài báo quốc tế bắt đầu từ khoảng trống tri thức chứ không phải Word.")]),
        ("SC03", "Cơ chế nhận diện mặt chữ giả tạo và chuỗi câu hỏi đến khoảng trống tri thức", 13.0,
         "Khi bạn chép lại lý thuyết cũ, não bộ chỉ nhận diện mặt chữ quen thuộc, chứ chưa hề tư duy. Nghiên cứu chuẩn quốc tế luôn đi từ câu hỏi cốt lõi, soi vào khoảng trống tri thức. Từ đó, họ mới chọn phương pháp đo đạc.",
         "When you copy old theories, your brain merely recognizes familiar words without thinking. International research always moves from a core question to a knowledge gap before choosing methods.",
         ["R03"], ["SRC01", "SRC02"], "Nhân vật người que cầm kính lúp soi trực tiếp vào tầng Khoảng trống tri thức trên sơ đồ",
         "Thư viện nghiên cứu với bảng sơ đồ phân cấp nguồn tài liệu và chuỗi tiến trình khoa học", "Đẩy cận cảnh vào điểm giao cắt",
         "Tiếng kính lúp khóa mục tiêu",
         [("não bộ chỉ nhận diện mặt chữ quen thuộc, chứ chưa hề tư duy", "SRC01", "Não bộ chỉ thực sự nắm bản chất khi tự truy xuất thông tin.")]),
        ("SC04", "Đối lập giữa sao chép tài liệu rời rạc và ma trận khoảng trống nghiên cứu", 11.5,
         "Người học vẹt bị nhấn chìm giữa ba mươi bài báo rời rạc, vì cố tóm tắt từng trang một. Ngược lại, người hiểu bản chất lập ma trận đối chiếu, để tìm ra đúng lỗ hổng mà giới học thuật bỏ sót.",
         "Rote learners drown in thirty scattered papers by summarizing every page. Conversely, deep thinkers build a comparison matrix to pinpoint the exact gap scholars missed.",
         ["R04"], ["SRC02"], "Nhân vật người que tự tin chỉ cây bút vào ô giao cắt phát sáng trên bảng Ma trận Khoảng trống",
         "Phòng làm việc học thuật với bảng Ma trận Khoảng trống Nghiên cứu kẻ ô ngăn nắp", "Lia ngang từ trái sang phải",
         "Tiếng kẻ bảng nhịp nhàng", []),
        ("SC05", "Làm chủ một trăm hai mươi giây đầu trước hội đồng bảo vệ khóa luận", 9.0,
         "Khi nắm vững khoảng trống tri thức trước lúc mở Word, bạn làm chủ phòng bảo vệ. Một trăm hai mươi giây đầu tiên trước hội đồng khóa luận luôn nằm trọn trong tay bạn.",
         "When you master the research gap before opening Word, you completely command the first one hundred twenty seconds before your thesis defense committee.",
         ["R05"], ["SRC02"], "Nhân vật người que đứng tự tin trước bục bảo vệ khóa luận với sơ đồ chuỗi nghiên cứu phía sau",
         "Phòng bảo vệ khóa luận đại học tại Việt Nam với đồng hồ 120 giây và màn chiếu", "Trung cảnh mở rộng",
         "Tiếng gõ bút đồng thuận của hội đồng",
         [("Một trăm hai mươi giây đầu tiên trước hội đồng khóa luận", "SRC02", "Hội đồng bảo vệ luôn soi khoảng trống nghiên cứu trong hai phút đầu.")]),
    ])
    use_subs = True if subtitles is None and aspect_ratio == "9:16" else bool(subtitles)
    use_speed = 1.0
    return ResearchedTopic(
        topic="Nghịch lý Tri thức và Ảo giác Năng lực: Giải phẫu cơ chế nhận thức khiến việc đọc lại giáo trình thụ động làm tê liệt tư duy nghiên cứu chuẩn Q1",
        audience="Sinh viên, học viên cao học và người tự học tại Việt Nam muốn hiểu bản chất tri thức và quy trình nghiên cứu",
        goal="Phá vỡ ảo giác năng lực khi học vẹt, chuyển sang chuỗi Question -> Gap -> Method -> Evidence và làm chủ 120s đầu phòng bảo vệ",
        video_type="science",
        min_duration=45.0,
        max_duration=60.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio=aspect_ratio,
        sources=sources,
        required_points=required_points,
        characters=characters,
        scenes=scenes,
        tone="Điềm đạm, sắc sảo, thông tuệ, chạm trúng tâm lý học thuật",
        language="vi",
        subtitles=use_subs,
        voice="VietNarrator",
        speed=use_speed,
        conversational_facts=True,
        packaging=PackagingSpec(
            youtube_title="Ảo Giác Năng Lực: Vì Sao Đọc Lại Sách Làm Não Tê Liệt?",
            visual_hook="Nhân vật người que cầm bút đỏ gạch chéo biểu tượng trang soạn thảo trống trước sơ đồ chuỗi Question -> Gap",
            text_overlay="BIẾT TÍNH ≠ HIỂU!",
            contrast_pair="Mở Word gõ ngay vs. Ma trận Khoảng trống Q1",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=["ảo giác năng lực", "tư duy nghiên cứu khoa học", "cách đọc bài báo Q1", "bảo vệ khóa luận tốt nghiệp"],
        ),
    )


def build_short_spinoff_topics(
    parent_topic: ResearchedTopic,
    max_spinoffs: int = 3,
) -> List[ResearchedTopic]:
    """Generate 2-3 standalone short_9x16 spin-off topics (45-60s, 5 scenes, subtitles=True, speed=1.0)
    from a researched dossier, each with its own independent Counter-Intuitive Hook <= 18 syllables.
    """
    spinoff_1 = create_academic_research_paradox_topic(aspect_ratio="9:16", subtitles=True)
    chars = list(spinoff_1.characters)

    sources_t2 = [
        {
            "id": "SRC01",
            "title": "The Elaboration Likelihood Model of Persuasion in Academic Evaluation",
            "reference": "Dr. Richard E. Petty & Dr. John T. Cacioppo (1986). Advances in Experimental Social Psychology, 19, 123-205.",
            "facts": [
                "Hội đồng bảo vệ định hình phán quyết ngay trong hai phút đầu tiên.",
                "Giám khảo luôn lật trang tài liệu tham khảo trước khi nghe bạn nói.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Genre Analysis: English in Academic and Research Settings (CARS Model)",
            "reference": "Dr. John M. Swales (1990). Cambridge University Press. ISBN: 978-0521338134",
            "facts": [
                "Đọc lại định nghĩa giáo trình làm mất điểm ngay từ mở bài.",
                "Cấu trúc phản biện ba bước giúp làm chủ câu hỏi tính mới.",
            ],
        },
    ]
    req_t2 = [
        {"id": "R01", "text": "Cửa sổ một trăm hai mươi giây đầu tiên khi bước lên bục bảo vệ khóa luận"},
        {"id": "R02", "text": "Hành động đầu tiên của giám khảo là lật trang danh mục tài liệu tham khảo"},
        {"id": "R03", "text": "Sai lầm đốt năm phút đầu đọc lại định nghĩa và trả lời tính mới bằng số liệu rời rạc"},
        {"id": "R04", "text": "Đối lập giữa liệt kê số liệu lan man và cấu trúc phản biện ba bước sắc bén"},
        {"id": "R05", "text": "Khép vòng lặp làm chủ hoàn toàn phòng bảo vệ khóa luận ngay từ hai phút đầu"},
    ]
    scenes_t2 = _make_five_part_scene_list([
        ("SC01", req_t2[0]["text"], 8.0,
         "Hội đồng bảo vệ định hình phán quyết ngay trong hai phút đầu tiên. Khi bạn bước lên bục thuyết trình, đồng hồ tâm lý đã bắt đầu đếm ngược.",
         "Defense committees form their verdict within the first two minutes. When you step up to the podium, the psychological clock starts ticking.",
         ["R01"], ["SRC01"], "Nhân vật người que đứng trên bục bảo vệ đối diện bàn hội đồng và đồng hồ 120 giây",
         "Phòng bảo vệ khóa luận đại học tại Việt Nam với đồng hồ đếm ngược 120 giây", "Đẩy cận cảnh vào đồng hồ 120 giây",
         "Tiếng đồng hồ tích tắc",
         [("Hội đồng bảo vệ định hình phán quyết ngay trong hai phút đầu tiên", "SRC01", "Hội đồng bảo vệ định hình phán quyết ngay trong hai phút đầu tiên.")]),
        ("SC02", req_t2[1]["text"], 11.0,
         "Tám mươi phần trăm sinh viên tưởng thầy cô đang chăm chú đọc màn chiếu mở đầu. [pause:900ms] Thực tế trong phòng bảo vệ, giám khảo luôn lật trang tài liệu tham khảo trước khi nghe bạn nói.",
         "Eighty percent of students think professors are reading the opening slide. [pause:900ms] In reality, examiners flip straight to the reference list before listening.",
         ["R02"], ["SRC01"], "Nhân vật người que soi kính lúp vào trang Danh mục tài liệu tham khảo ở cuối cuốn khóa luận",
         "Bàn hội đồng với cuốn khóa luận mở sẵn ở trang Danh mục tài liệu tham khảo", "Toàn cảnh lật về trang cuối",
         "Tiếng lật giấy nhanh",
         [("giám khảo luôn lật trang tài liệu tham khảo trước khi nghe bạn nói", "SRC01", "Giám khảo luôn lật trang tài liệu tham khảo trước khi nghe bạn nói.")]),
        ("SC03", req_t2[2]["text"], 13.0,
         "Đọc lại định nghĩa giáo trình làm mất điểm ngay từ mở bài. Khi hội đồng hỏi đề tài này có gì mới, nhiều bạn lại cuống cuồng đọc hàng loạt bảng số liệu. Nhưng số liệu dày đặc kia không bao giờ thay thế được khoảng trống nghiên cứu.",
         "Reading textbook definitions loses points right from the opening. When asked what is new, many students frantically recite raw data tables. Yet numbers never replace a clear research gap.",
         ["R03"], ["SRC02"], "Nhân vật người que gạch chéo khung trình chiếu định nghĩa dài dòng và bảng số liệu hỗn độn",
         "Phòng thuyết trình với bảng cảnh báo hai lỗi mở bài kinh điển trên bục bảo vệ", "Cận cảnh tấm bảng lỗi",
         "Tiếng còi cảnh báo nhẹ",
         [("Đọc lại định nghĩa giáo trình làm mất điểm ngay từ mở bài", "SRC02", "Đọc lại định nghĩa giáo trình làm mất điểm ngay từ mở bài.")]),
        ("SC04", req_t2[3]["text"], 11.5,
         "Người lúng túng chỉ liệt kê mình đã chạy bao nhiêu mẫu khảo sát. Ngược lại, cấu trúc phản biện ba bước giúp làm chủ câu hỏi tính mới. Hãy nêu rõ người trước làm gì, bỏ ngỏ gì, và bạn đo đạc ra sao.",
         "Confused speakers only list how many samples they surveyed. Conversely, a three-step rebuttal structure commands the novelty question. State what prior work did, what gap remained, and how your method solves it.",
         ["R04"], ["SRC02"], "Nhân vật người que chỉ tay vào sơ đồ 3 khối mũi tên phản biện rõ nét",
         "Bảng sơ đồ Cấu trúc Phản biện 3 Bước: Đã biết -> Lỗ hổng bỏ ngỏ -> Giải pháp đo đạc", "Lia ngang sang sơ đồ 3 bước",
         "Tiếng khóa mục tiêu sắc gọn",
         [("cấu trúc phản biện ba bước giúp làm chủ câu hỏi tính mới", "SRC02", "Cấu trúc phản biện ba bước giúp làm chủ câu hỏi tính mới.")]),
        ("SC05", req_t2[4]["text"], 9.0,
         "Khi mở màn trực diện bằng khoảng trống tri thức, bạn sẽ thuyết phục trọn vẹn hội đồng. Một trăm hai mươi giây đầu tiên trên bục bảo vệ giờ nằm trọn trong tay bạn.",
         "When you open directly with a clear research gap and top-tier sources, you win over the entire committee within the first one hundred twenty seconds.",
         ["R05"], ["SRC01"], "Nhân vật người que mỉm cười tự tin trên bục bảo vệ khi đồng hồ 120 giây sáng đèn xanh",
         "Phòng bảo vệ khóa luận sáng rõ với sự đồng thuận của hội đồng", "Trung cảnh mở rộng",
         "Tiếng gõ bút đồng thuận", []),
    ])
    spinoff_2 = ResearchedTopic(
        topic=f"{parent_topic.topic} — Spin-off: Tâm lý Hội đồng Bảo vệ trong 120 Giây Đầu",
        audience=parent_topic.audience,
        goal="Giải mã tâm lý hội đồng bảo vệ khóa luận trong 120 giây đầu và áp dụng cấu trúc phản biện 3 bước",
        video_type="science",
        min_duration=45.0,
        max_duration=60.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=sources_t2,
        required_points=req_t2,
        characters=chars,
        scenes=scenes_t2,
        tone="Sắc sảo, kịch tính, chạm đúng tâm lý phòng bảo vệ",
        language="vi",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        packaging=PackagingSpec(
            youtube_title="Tâm Lý Hội Đồng: Cửa Sổ 120 Giây Định Đoạt Khóa Luận",
            visual_hook="Đồng hồ 120 giây phía trên bàn Hội đồng khi nhân vật người que mở trang Tài liệu tham khảo",
            text_overlay="120 GIÂY ĐẦU!",
            contrast_pair="Đọc lại lý thuyết vs. Phản biện 3 bước",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_2_mid",
            seo_keywords=["bảo vệ khóa luận tốt nghiệp", "tâm lý hội đồng bảo vệ", "cách trả lời phản biện khóa luận"],
        ),
    )

    sources_t3 = [
        {
            "id": "SRC01",
            "title": "Cognitive Load During Problem Solving",
            "reference": "Dr. John Sweller (1988). Cognitive Science, 12(2), 257-285. DOI: 10.1207/s15516709cog1202_4",
            "facts": [
                "Đọc ba mươi bài báo rời rạc làm quá tải bộ nhớ làm việc.",
                "Ma trận đối chiếu giúp gom mảnh ghép thành khoảng trống nghiên cứu.",
            ],
        },
        {
            "id": "SRC02",
            "title": "The Craft of Research",
            "reference": "Wayne C. Booth, Gregory G. Colomb & Joseph M. Williams (2016). University of Chicago Press. ISBN: 978-0226239736",
            "facts": [
                "Dùng trí tuệ nhân tạo viết hộ tổng quan luôn lộ lỗi sáo rỗng.",
                "Hãy dùng công cụ để phản biện chéo lý thuyết và tìm bằng chứng.",
            ],
        },
    ]
    req_t3 = [
        {"id": "R01", "text": "Cơn bão thông tin khi tải hàng chục bài báo Q1 về máy nhưng không biết đọc từ đâu"},
        {"id": "R02", "text": "Sai lầm nhờ công cụ viết hộ tổng quan tài liệu khiến hội đồng phát hiện ngay"},
        {"id": "R03", "text": "Cơ chế gom 30 bài báo rời rạc thành Ma trận Khoảng trống Nghiên cứu"},
        {"id": "R04", "text": "Đối lập giữa tóm tắt từng bài rời rạc và phản biện chéo tìm lỗ hổng phương pháp"},
        {"id": "R05", "text": "Làm chủ vũ khí tư duy học thuật để biến dữ liệu phân mảnh thành đề tài xuất sắc"},
    ]
    scenes_t3 = _make_five_part_scene_list([
        ("SC01", req_t3[0]["text"], 8.0,
         "Tải ba mươi bài báo quốc tế chẳng giúp bạn có đề tài mới. Đêm khuya mở thư mục tài liệu, não bạn tê liệt vì quá tải.",
         "Downloading thirty international papers does not give you a new thesis topic. Late at night facing a flooded folder, your brain immediately freezes from overload.",
         ["R01"], ["SRC01"], "Nhân vật người que choáng váng giữa hàng chục tập tài liệu bài báo xếp chồng quanh bàn học",
         "Bàn làm việc sinh viên Việt Nam đêm khuya với màn hình mở hàng chục bài báo khoa học", "Đẩy cận cảnh nhanh vào chồng tài liệu",
         "Tiếng thông báo tải file dồn dập",
         [("Đêm khuya mở thư mục tài liệu, não bạn tê liệt vì quá tải", "SRC01", "Đọc ba mươi bài báo rời rạc làm quá tải bộ nhớ làm việc.")]),
        ("SC02", req_t3[1]["text"], 11.0,
         "Nhiều bạn hoảng loạn liền yêu cầu công cụ trí tuệ nhân tạo viết hộ mục tổng quan. [pause:900ms] Nhưng trên thực tế, hội đồng bảo vệ luôn nhận ra ngay văn phong liệt kê sáo rỗng.",
         "Many panicked students ask artificial intelligence to write their literature review. [pause:900ms] Yet defense committees immediately spot hollow summaries lacking critical debate.",
         ["R02"], ["SRC02"], "Nhân vật người que gạch chéo đoạn văn tổng quan liệt kê rời rạc bị đóng dấu cảnh báo",
         "Phòng học với sơ đồ đối sánh văn bản liệt kê bề mặt và mạng lưới phản biện học thuật", "Toàn cảnh đối chiếu",
         "Tiếng đóng dấu cảnh báo",
         [("hội đồng bảo vệ luôn nhận ra ngay văn phong liệt kê sáo rỗng", "SRC02", "Dùng trí tuệ nhân tạo viết hộ tổng quan luôn lộ lỗi sáo rỗng.")]),
        ("SC03", req_t3[2]["text"], 13.0,
         "Thay vì bảo máy viết hộ, hãy biến ba mươi bài báo kia thành một ma trận khoảng trống nghiên cứu. Bạn yêu cầu hệ thống bóc tách từng bài theo bốn cột, gồm câu hỏi và phương pháp. Cuối cùng là dữ liệu, và giới hạn chưa giải quyết.",
         "Instead of asking it to write for you, turn thirty papers into a research gap matrix. Extract each paper across four columns: question, method, evidence, and unsolved limits.",
         ["R03"], ["SRC01", "SRC02"], "Nhân vật người que sắp xếp các thẻ dữ liệu vào bảng Ma trận 4 cột rõ nét",
         "Phòng nghiên cứu với bảng Ma trận Khoảng trống Nghiên cứu 4 cột phát sáng", "Cận cảnh theo từng cột ma trận",
         "Tiếng các ô dữ liệu khớp vào bảng",
         [("hãy biến ba mươi bài báo kia thành một ma trận khoảng trống nghiên cứu", "SRC01", "Ma trận đối chiếu giúp gom mảnh ghép thành khoảng trống nghiên cứu.")]),
        ("SC04", req_t3[3]["text"], 11.5,
         "Người nghiệp dư chỉ tóm tắt từng bài riêng lẻ, nên mãi dậm chân tại chỗ trong mớ hỗn độn. Ngược lại, nhà nghiên cứu dùng trí tuệ nhân tạo để phản biện chéo các trường phái, và khoanh vùng lỗ hổng phương pháp.",
         "Amateurs summarize papers one by one and stay stuck. Conversely, researchers use deep analysis to cross-examine schools of thought and isolate methodological gaps.",
         ["R04"], ["SRC02"], "Nhân vật người que nâng mảnh ghép trung tâm tại giao điểm ba vòng tròn lý thuyết",
         "Không gian đồ họa đối sánh các tờ ghi chú rời rạc với sơ đồ giao thoa ba vòng tròn lý thuyết", "Lia ngang từ trái sang phải",
         "Tiếng tia sáng hội tụ",
         [("phản biện chéo các trường phái, và khoanh vùng lỗ hổng phương pháp", "SRC02", "Hãy dùng công cụ để phản biện chéo lý thuyết và tìm bằng chứng.")]),
        ("SC05", req_t3[4]["text"], 9.0,
         "Khi biến cơn bão thông tin thành ma trận khoảng trống rõ ràng, bế tắc sẽ tan biến. Ba mươi bài báo kia trở thành bệ phóng vững chắc cho công trình của bạn.",
         "When you transform an information storm into a clear gap matrix, those thirty papers become a solid launchpad for your own original research.",
         ["R05"], ["SRC01"], "Nhân vật người que đứng tự tin trước bảng Ma trận Khoảng trống Nghiên cứu hoàn chỉnh",
         "Bàn làm việc học thuật ngăn nắp với màn hình lớn hiển thị Ma trận Khoảng trống hoàn chỉnh", "Trung cảnh mở rộng",
         "Âm thanh hoàn tất ấm áp", []),
    ])
    spinoff_3 = ResearchedTopic(
        topic=f"{parent_topic.topic} — Spin-off: Ma trận Khoảng trống Nghiên cứu (Research Gap Matrix)",
        audience=parent_topic.audience,
        goal="Biến 30 bài báo Q1 rời rạc thành Ma trận Khoảng trống Nghiên cứu và dùng AI phản biện chéo lý thuyết thay vì viết hộ",
        video_type="science",
        min_duration=45.0,
        max_duration=60.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=sources_t3,
        required_points=req_t3,
        characters=chars,
        scenes=scenes_t3,
        tone="Sắc bén, thực chiến, chuẩn mực học thuật Q1",
        language="vi",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        packaging=PackagingSpec(
            youtube_title="Ma Trận Research Gap: Đọc 30 Bài Báo Q1 Không Quá Tải",
            visual_hook="Nhân vật người que dùng kính lúp kiểm tra Bảng Ma trận Khoảng trống Nghiên cứu 4 cột giữa các bài PDF rời rạc",
            text_overlay="ĐỪNG BẢO AI VIẾT HỘ!",
            contrast_pair="Viết hộ sáo rỗng vs. Phản biện chéo Q1",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_3_conversion",
            seo_keywords=["ma trận khoảng trống nghiên cứu", "research gap matrix", "cách đọc bài báo Q1", "AI cho nghiên cứu khoa học"],
        ),
    )
    return [spinoff_1, spinoff_2, spinoff_3][: max(1, max_spinoffs)]


def write_production_package(
    output_dir: Path,
    topic: ResearchedTopic,
    system_root: Path = SYS_DIR,
    brief_revision: int = 1,
    include_spinoffs: bool = False,
    omni_plan: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Assemble and write brief.json, content.json, script.json, cadence_report.json, and optional short_9x16 spin-offs."""
    if any((output_dir / name).exists() for name in ('revisions', 'execution-control.json', 'brief-current.json', 'integrity.json')):
        raise ValueError('ACTIVE_JOB_DESTINATION: export a blueprint and use official pilot author/revision operations')
    output_dir.mkdir(parents=True, exist_ok=True)

    spinoff_packages: List[Dict[str, Any]] = []
    if include_spinoffs:
        spinoff_topics = build_short_spinoff_topics(topic, max_spinoffs=3)
        topic.spinoff_shorts = [
            {
                "id": f"SPINOFF_{idx:02d}",
                "hook_title": st.packaging.youtube_title if st.packaging else st.topic[:55],
                "opening_hook": split_sentences(st.scenes[0].narration)[0],
                "format_profile": "short_9x16",
                "scene_count": len(st.scenes),
            }
            for idx, st in enumerate(spinoff_topics, 1)
        ]

    brief_data = build_brief_v3(topic, system_root=system_root)
    if omni_plan is not None:
        brief_data.update(omni_platform=True, reframe_mode=True, spinoff_shorts=omni_plan['spinoff_shorts'])
        if 'social_copy' in omni_plan:
            brief_data['social_copy'] = omni_plan['social_copy']
    brief_hash = compute_brief_hash(brief_data)
    content_data = build_content_v3(topic, brief_data, brief_hash, brief_revision=brief_revision)
    if omni_plan is not None:
        from omni_platform import short_plans
        short_plans(brief_data, content_data)
    script_data = generate_script_json(topic)

    checker = ScriptCadenceChecker(nominal_rate=NOMINAL_SPEECH_RATE)
    cadence_report = checker.check_scenes(script_data)
    from tools.script_diversity_linter import clean_sentence, lint_script
    _claim_facts = {clean_sentence(f) for src in brief_data.get("sources", []) for f in src.get("facts", [])}
    _claim_facts.update(clean_sentence(c.get("fact", "")) for c in content_data.get("claims", []) if c.get("fact"))
    _claim_facts.update(clean_sentence(c.get("quote", "")) for c in content_data.get("claims", []) if c.get("quote"))
    diversity_report = lint_script(content_data["scenes"], claim_facts=_claim_facts, topic_title=brief_data.get("topic", ""))

    def _write_if_changed(path: Path, text: str) -> None:
        if path.is_file() and path.read_text(encoding="utf-8") == text:
            return
        path.write_text(text, encoding="utf-8")

    brief_file = output_dir / "brief.json"
    content_file = output_dir / "content.json"
    script_file = output_dir / "script.json"
    cadence_file = output_dir / "cadence_report.json"

    script_json_str = json.dumps(script_data, indent=2, ensure_ascii=False) + "\n"
    _write_if_changed(brief_file, serialize_brief_json(brief_data))
    _write_if_changed(content_file, json.dumps(content_data, indent=2, ensure_ascii=False) + "\n")
    _write_if_changed(script_file, script_json_str)
    if len(topic.scenes) == 48:
        _write_if_changed(output_dir / "script_13m_48scenes.json", script_json_str)
    _write_if_changed(cadence_file, json.dumps(cadence_report, indent=2, ensure_ascii=False) + "\n")

    if include_spinoffs:
        spinoffs_root = output_dir / "spinoff_shorts"
        for idx, st in enumerate(build_short_spinoff_topics(topic, max_spinoffs=3), 1):
            sp_dir = spinoffs_root / f"spinoff_{idx:02d}_short_9x16"
            sp_res = write_production_package(sp_dir, st, system_root=system_root, brief_revision=1, include_spinoffs=False)
            spinoff_packages.append(sp_res)

    valid_contracts, contract_errors = validate_production_bundle(
        system_root=system_root,
        brief_data=brief_data,
        content_data=content_data,
        brief_revision=brief_revision,
    )

    packaging_warnings = check_packaging_and_localization(brief_data, scenes=topic.scenes)

    return {
        "output_dir": str(output_dir),
        "brief_file": str(brief_file),
        "content_file": str(content_file),
        "script_file": str(script_file),
        "cadence_file": str(cadence_file),
        "brief_hash": brief_hash,
        "valid_contracts": valid_contracts,
        "contract_errors": contract_errors,
        "packaging_warnings": packaging_warnings,
        "cadence_report": cadence_report,
        "diversity_report": diversity_report,
        "spinoff_packages": spinoff_packages,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Research Story Architect: Formulate schema 3.0 blueprints from researched topics."
    )
    parser.add_argument("--demo", action="store_true", help="Generate benchmark production package for trial topic")
    parser.add_argument(
        "--topic",
        choices=["procrastination-paradox", "academic-paradox-q1"],
        default=None,
        help="Select built-in researched topic blueprint",
    )
    parser.add_argument("--job-id", default=None, help="Job identifier for sys/runs/<job_id>")
    parser.add_argument("--output-dir", default=None, help="Explicit output directory")
    parser.add_argument("--validate", action="store_true", help="Run contract and cadence validation")
    parser.add_argument("--aspect-ratio", choices=["16:9", "9:16", "dual"], default="16:9", help="Video aspect ratio")
    parser.add_argument("--subtitles", action="store_true", help="Force enable subtitles on output")
    parser.add_argument("--omni-plan", help="Authored standalone short references JSON; enables shared-image omni-platform outputs")
    parser.add_argument("--spinoff-shorts", action="store_true", help="Also generate standalone short_9x16 spin-off packages")

    args = parser.parse_args()

    selected_topic = args.topic or ("procrastination-paradox" if args.demo else None)
    if selected_topic:
        if selected_topic == "academic-paradox-q1":
            job_id = args.job_id or f"academic-paradox-q1-{args.aspect_ratio.replace(':', 'x')}"
            out_dir = Path(args.output_dir) if args.output_dir else SYS_DIR / f"runs/{job_id}"
            print("[*] Đang kiến trúc bộ hồ sơ kỹ thuật ngách Tư Duy Nghiên Cứu Q1: 'Nghịch lý Tri thức & Ảo giác Năng lực'...")
            topic = create_academic_research_paradox_topic(aspect_ratio=args.aspect_ratio, subtitles=args.subtitles or None)
        else:
            job_id = args.job_id or f"procrastination-paradox-{args.aspect_ratio.replace(':', 'x')}-001"
            out_dir = Path(args.output_dir) if args.output_dir else SYS_DIR / f"runs/{job_id}"
            print("[*] Đang kiến trúc bộ hồ sơ kỹ thuật mẫu cho chủ đề: 'Nghịch lý của sự Trì hoãn'...")
            topic = create_demo_trial_topic()
            topic.aspect_ratio = args.aspect_ratio
            if args.subtitles:
                topic.subtitles = True

        result = write_production_package(
            out_dir,
            topic,
            system_root=SYS_DIR,
            include_spinoffs=args.spinoff_shorts,
            omni_plan=json.loads(Path(args.omni_plan).read_text()) if args.omni_plan else None,
        )

        print(f"  [+] Đã xuất brief.json: {result['brief_file']}")
        print(f"  [+] Đã xuất content.json: {result['content_file']}")
        print(f"  [+] Đã xuất script.json: {result['script_file']}")
        print(f"  [+] Đã xuất cadence_report.json: {result['cadence_file']}")
        print(f"  [+] Brief Hash: {result['brief_hash']}")
        if result.get("spinoff_packages"):
            print(f"  [+] Đã xuất {len(result['spinoff_packages'])} gói Spin-off short_9x16 độc lập tại: {out_dir / 'spinoff_shorts'}")

        cadence = result["cadence_report"]
        print("\n[*] Kết quả kiểm tra âm học (Script Cadence Checker):")
        print(f"    - Tổng thời lượng: {cadence['total_duration']:.1f}s")
        print(f"    - Tổng âm tiết: {cadence['total_actual_syllables']}/{cadence['total_target_syllables']} (target)")
        print(f"    - Độ lệch tối đa (Max Drift): {cadence['max_drift']:.2f}s (Ngưỡng an toàn: <= 0.3s)")
        print(f"    - Cảnh báo: {cadence['warnings_count']}")
        print(f"    - Trạng thái âm học: [{cadence['status']}]")

        if result["valid_contracts"]:
            print("  [PASS] Xác thực hợp đồng Schema 3.0 (validate_brief & validate_content): 100% HỢP LỆ.")
        else:
            print("  [FAIL] Lỗi xác thực hợp đồng:")
            for err in result["contract_errors"]:
                print(f"    - {err}")
            return 1

        if cadence["warnings_count"] > 0:
            print("  [WARN] Phát hiện cảnh báo âm học:")
            for sc in cadence.get("scenes", []):
                for w in sc.get("warnings", []):
                    print(f"    - {sc['scene_id']}: {w}")
            return 1

        print("\n★ BỘ HỒ SƠ KỸ THUẬT ĐẦU VÀO ĐÃ ĐƯỢC ĐÓNG GÓI VÀ XÁC THỰC HOÀN TOÀN! ★")
        return 0

    print("Vui lòng cung cấp cờ --demo hoặc --topic. Xem --help.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
