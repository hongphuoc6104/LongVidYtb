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

DEFAULT_CHANNEL_PILLAR = "Giải Mã Tư Duy Nghiên Cứu, Bản Chất Tri Thức & Luật Ngầm Học Thuật"
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


from scripts.camera_motion import assign_scene_camera_effects, select_semantic_camera_effect  # noqa: F401


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

    # 3. Thumbnail Spec validation (visual_hook + 2-4 uppercase word text_overlay)
    if isinstance(thumb, dict) and thumb:
        vis_hook = str(thumb.get("visual_hook") or "").strip()
        overlay = str(thumb.get("text_overlay") or "").strip()
        if not vis_hook:
            warnings.append("THUMBNAIL_MISSING_VISUAL_HOOK: thumbnail_spec.visual_hook must not be empty")
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "youtube_title": self.youtube_title,
            "thumbnail_spec": {
                "visual_hook": self.visual_hook,
                "text_overlay": self.text_overlay,
                "contrast_pair": self.contrast_pair,
            },
            "channel_pillar": self.channel_pillar,
            "funnel_tier": self.funnel_tier,
            "seo_keywords": list(self.seo_keywords),
        }


@dataclass
class ResearchedSticker:
    id: str
    description: str
    character_ids: List[str]
    anchor_quote: str
    fx: str = "pop"
    x: float = 0.35
    y: float = 0.65
    w: float = 0.35
    z: int = 2
    anchor_quote_en: Optional[str] = None


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

    def __post_init__(self) -> None:
        if self.shot_type not in {"macro_prop", "full_scene", "variation", "white_card", "white_isolated"}:
            raise ValueError(f"Unsupported full-frame shot type: {self.shot_type}")
        if self.shot_type == "variation" and not (self.based_on and self.preserve.strip() and self.change.strip()):
            raise ValueError("A variation requires based_on, preserve, and change")


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
    bg_description: str = ""  # Legacy source compatibility only.
    stickers: List[ResearchedSticker] = field(default_factory=list)
    reused_sticker_ids: List[Tuple[Any, ...]] = field(default_factory=list)  # (sticker_id, anchor_quote, fx, [anchor_quote_en])
    foley_cue: Optional[str] = None
    claim_facts: List[Tuple[str, str, str]] = field(default_factory=list)  # (quote, source_id, fact)
    narration_en: Optional[str] = None
    visual_beats: List[ResearchedVisualBeat] = field(default_factory=list)
    scene_description: str = ""
    tone: Optional[str] = None


@dataclass
class ResearchedTopic:
    topic: str
    audience: str
    goal: str
    video_type: str
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None
    style: str = ""
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
    spinoff_shorts: Optional[List[Dict[str, Any]]] = None
    visual_pacing_profile: Optional[str] = None


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
    cfg_voice = "Adam"
    cfg_speed = 1.22
    cfg_en_voice = "Adam"
    cfg_en_speed = 1.22
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
    if topic.visual_pacing_profile is not None:
        brief['visual_pacing_profile'] = topic.visual_pacing_profile
    if getattr(topic, "spinoff_shorts", None):
        brief["spinoff_shorts"] = list(topic.spinoff_shorts)
    return brief


def compose_full_frame_description(environment: str, figure_action: str) -> str:
    """Combine a setting and visible action without cutout background instructions."""
    environment = re.sub(r'(?i)(?:,?\s*)(?:không có nhân vật(?: nào)?|no characters(?: anywhere)?)\.?$', '', environment.strip())
    figure_action = re.sub(r'(?i)(?:trên|với)\s+nền\s+trắng(?:\s+tinh)?|on\s+(?:a\s+)?(?:pure\s+)?white\s+background', '', figure_action)
    figure_action = re.sub(r'(?i)sticker\s+nghiên\s+cứu|sticker|cut[- ]?out', 'anonymous stick figure', figure_action)
    return f'{environment}. {figure_action}. Render one integrated full-frame composition with figures and props physically grounded in the setting.'


def _legacy_full_frame_description(scene: ResearchedScene) -> str:
    """Convert older background/sticker briefs into one integrated scene image."""
    environment = re.sub(
        r"(?i)(?:,?\s*)(?:không có nhân vật(?: nào)?|no characters(?: anywhere)?)\.?$",
        "",
        (scene.scene_description or scene.bg_description).strip(),
    )
    action = re.sub(r"(?i)sticker\s+nghiên\s+cứu|sticker", "nhân vật người que", scene.action)
    pose_details = []
    for sticker in scene.stickers:
        detail = sticker.description.strip()
        detail = re.sub(
            r"(?i)(?:isolated|cut[- ]?out)\s+(?:on|against)\s+(?:a\s+)?(?:pure\s+|solid\s+)?white\s+(?:background|backdrop)",
            "",
            detail,
        )
        detail = re.sub(
            r"(?i)(?:trên|với)\s+nền\s+trắng(?:\s+tinh)?",
            "",
            detail,
        )
        detail = re.sub(r"(?i)sticker\s+nghiên\s+cứu|sticker|cut[- ]?out", "nhân vật người que", detail)
        if detail:
            pose_details.append(detail)

    details = " ".join(part for part in (environment, scene.setting, action, *pose_details) if part)
    return (
        f"{details}. Compose one cohesive full-frame illustration. "
        "Characters and props belong naturally in the same physical environment; "
        "do not isolate a foreground figure, add a sticker border, or use a white cutout backdrop."
    )


def _phrase_anchors(text: str, count: int) -> List[Tuple[str, int]]:
    """Split narration into ordered, exact-word anchors for legacy scene briefs."""
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
    """Create full-frame beats from legacy scene briefs using opening/body hold targets."""
    opening_seconds = max(0.0, min(scene.duration, 15.0 - elapsed))
    body_seconds = max(0.0, scene.duration - opening_seconds)
    count = max(1, math.ceil(opening_seconds / 1.5) + math.ceil(body_seconds / 2.5))
    vi_anchors = _phrase_anchors(scene.narration, count)
    en_anchors = _phrase_anchors(scene.narration_en, len(vi_anchors)) if scene.narration_en else []
    if en_anchors and len(en_anchors) < len(vi_anchors):
        vi_anchors = vi_anchors[:len(en_anchors)]
    base_description = _legacy_full_frame_description(scene)
    beats = []
    for index, (quote, occurrence) in enumerate(vi_anchors):
        image_id = f"{scene.scene_id}_I{index + 1}"
        focus_kind = (
            "punch_in" if (index == 0 and scene.scene_id == "SC01") or "!" in quote
            else "cut"
        )
        variation = index > 0
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
            effect="punch_in" if focus_kind == "punch_in" else ("fade" if variation else "cut"),
            based_on=f"{scene.scene_id}_I{index}" if variation else None,
            preserve=(
                f"Keep the same setting ({scene.setting}), character design, and surrounding props."
                if variation else ""
            ),
            change=(
                f"Shift the full-frame emphasis to this next narrated action or object: {quote}."
                if variation else "Establish the complete scene and its opening action."
            ),
        ))
    return beats




def build_scenes_from_story_rows(
    story_rows: List[Tuple[str, str, List[Tuple[str, str]]]],
    character_id: str = "CH01",
    nominal_rate: float = NOMINAL_SPEECH_RATE,
) -> List[ResearchedScene]:
    """Flash-agent friendly builder: converts (title, setting, [(sentence, "shot_type|visual_action")]) rows
    into fully anchored, cadence-calibrated ResearchedScene objects without manual coordinate or offset math.
    """
    built_scenes: List[ResearchedScene] = []
    total = len(story_rows)
    for index, (title, setting, rows) in enumerate(story_rows, 1):
        scene_id = f"SC{index:02d}"
        narration = " ".join(sent.strip() for sent, _ in rows if sent.strip())
        beats: List[ResearchedBeat] = []
        base_id: Optional[str] = None
        seen_quotes: Dict[str, int] = {}
        for beat_idx, (sentence, spec) in enumerate(rows, 1):
            shot_type, _, action_desc = spec.partition("|")
            shot_type = shot_type.strip() or "full_scene"
            action_desc = action_desc.strip() or spec.strip()
            image_id = f"{scene_id}_I{beat_idx}"
            quote = sentence.strip()
            seen_quotes[quote] = seen_quotes.get(quote, 0) + 1
            if shot_type == "full_scene" and base_id is None:
                base_id = image_id
            based_on = (base_id or f"{scene_id}_I{max(1, beat_idx - 1)}") if shot_type == "variation" else None
            preserve = (
                f"Keep the exact camera angle, room geometry and props from {based_on} in {setting}. "
                "Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift."
                if based_on else ""
            )
            row_effect = (
                "hold" if shot_type == "white_card"
                else ("punch_in" if (index == 1 and beat_idx == 1) or "!" in quote else "cut")
            )
            beats.append(ResearchedBeat(
                image_id=image_id,
                description=f"{setting} {action_desc}",
                anchor_quote=quote,
                anchor_occurrence=seen_quotes[quote],
                reason="Narration-locked full-frame beat.",
                character_ids=[character_id],
                effect=row_effect,
                based_on=based_on,
                preserve=preserve,
                change=action_desc,
                shot_type=shot_type,
            ))
        is_last = index == total
        p_tail = DEFAULT_P_TAIL_LAST if is_last else DEFAULT_P_TAIL_PARA
        pause_sec, _, _ = extract_pauses(narration)
        syl = count_syllables(narration, lang="vi")
        duration = round(pause_sec + (syl / nominal_rate) + p_tail, 2)
        tone = "narrative_warm" if index <= max(1, total // 5) else ("reflective_slow" if index > total - max(1, total // 5) else "analytical_crisp")
        built_scenes.append(ResearchedScene(
            scene_id=scene_id,
            title=title,
            purpose=f"Triển khai bước {index}: {title.lower()}",
            duration=duration,
            narration=narration,
            requirements=[],
            source_ids=[],
            character_ids=[character_id],
            action=rows[0][1].partition("|")[2].strip() if rows else title,
            setting=setting,
            camera="Semantic full-frame sequence",
            visual_beats=beats,
            tone=tone,
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

    for sc in topic.scenes:
        s_id = sc.scene_id

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

            images.append({
                "id": visual.image_id,
                "description": visual.description,
                "character_ids": list(visual.character_ids or sc.character_ids),
                "based_on": visual.based_on,
                "preserve": visual.preserve,
                "change": visual.change,
                "reason": visual.reason,
                "visible_text": list(visual.visible_text),
                "kind": "scene",
                "shot_type": "variation" if visual.based_on else visual.shot_type,
            })
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
        for beat, image in zip(beats, images, strict=True):
            if image.get('shot_type') == 'white_card' and beat['effect'] in ('auto', 'cut', 'fade', 'hold'):
                beat['effect'] = 'hold'
            elif beat['effect'] in ('auto', 'cut', 'fade'):
                beat['effect'] = select_semantic_camera_effect(image['description'] + ' ' + sc.camera, previous_effect)
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
        if sc.narration_en:
            scene_dict["narration_en"] = sc.narration_en

        content_scenes.append(scene_dict)
        elapsed += sc.duration

        # Coverage: link requirements to scene quotes
        for r_id in sc.requirements:
            if r_id in req_map:
                quote_cand = sc.narration.split(".")[0].strip()
                if quote_cand not in sc.narration:
                    quote_cand = sc.narration[:30].strip()
                cov_entry = {
                    "requirement_id": r_id,
                    "scene_id": s_id,
                    "quote": quote_cand,
                }
                if needs_en and sc.narration_en:
                    quote_en_cand = sc.narration_en.split(".")[0].strip()
                    if quote_en_cand not in sc.narration_en:
                        quote_en_cand = sc.narration_en[:30].strip()
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

    characters = [
        {
            "id": "CH01",
            "name": "Nhân vật người que trải nghiệm",
            "appearance": "Hình tượng stick-figure tối giản, đầu tròn trắng viền đen dày, mắt chấm oval, thân nét mực mảnh",
            "outfit": "Áo thun nét vẽ đen đơn giản trên nền sáng",
        }
    ]

    scenes = [
        ResearchedScene(
            scene_id="SC01",
            title="Khoảnh khắc mở tủ lạnh nửa đêm",
            purpose="Khoảnh khắc mở tủ lạnh lúc nửa đêm",
            duration=8.0,
            narration="Đúng mười một giờ ba mươi đêm ngay trước hạn chót, bạn lại đứng ngơ ngác mở tủ lạnh lần thứ tư dù bụng thực sự không hề thấy đói.",
            narration_en="Right at eleven thirty at night before deadline, you blankly open the fridge again, although you are not hungry.",
            requirements=["R01"],
            source_ids=[],
            character_ids=["CH01"],
            action="Người que đứng trước tủ lạnh mở sáng loáng lúc nửa đêm",
            setting="Căn bếp gia đình tĩnh mịch đêm khuya với ánh sáng từ cánh cửa tủ lạnh",
            camera="Trung cảnh ngang tầm mắt, góc nhìn trực diện",
            scene_description=compose_full_frame_description("Căn bếp gia đình tĩnh mịch lúc đêm muộn với tủ lạnh đang mở toang tỏa ra ánh sáng vàng nhạt, không có nhân vật", "Hình tượng người que stick-figure đầu tròn trắng viền đen dày, biểu cảm bối rối đưa tay gãi đầu, đứng nhìn vào ánh sáng"),
            foley_cue="Click cửa tủ lạnh mở nhẹ nhàng, tiếng vo ve máy nén đêm khuya",
            claim_facts=[],
        ),
        ResearchedScene(
            scene_id="SC02",
            title="Nghịch lý sách tự lực và khoa học thần kinh",
            purpose="Nghịch lý: không phải lười biếng mà là điều hòa cảm xúc",
            duration=11.0,
            narration="Những cuốn sách dạy thành công ngoài kia vẫn thường chỉ trích bạn là kẻ lười biếng và thiếu kỷ luật. [pause:900ms] Nhưng khoa học thần kinh hiện đại đã chứng minh một nghịch lý hoàn toàn ngược lại.",
            narration_en="Popular self-help bestsellers blame you for being lazy and undisciplined. [pause:900ms] Yet modern neuroscience reveals a completely opposite paradox.",
            requirements=["R02"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Người que nhìn chồng sách tự lực rồi quay sang biểu đồ não bộ ngạc nhiên",
            setting="Không gian tối giản phân chia giữa cuốn sách và biểu tượng não bộ phát sáng",
            camera="Toàn cảnh góc rộng",
            scene_description=compose_full_frame_description("Bàn học với chồng sách kỹ năng sống và biểu tượng sơ đồ não bộ phát sáng dịu nhẹ trên tường, không có nhân vật", "Hình tượng người que stick-figure chỉ tay vào biểu đồ não bộ với nét mặt bừng sáng phát hiện điều mới"),
            foley_cue="Tiếng lật sách soàn soạt, sau đó là khoảng lặng sau pause",
            claim_facts=[
                (
                    "khoa học thần kinh hiện đại đã chứng minh một nghịch lý hoàn toàn ngược lại",
                    "SRC01",
                    "Trì hoãn thực chất là né tránh căng thẳng, không phải vì lười biếng.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC03",
            title="Cơ chế hạch hạnh nhân kích hoạt phản xạ sinh tồn",
            purpose="Hạch hạnh nhân và cơ chế phản ứng trước mối đe dọa",
            duration=13.0,
            narration="Thực nghiệm thần kinh phát hiện ra rằng: hạch hạnh nhân trong não bộ xem bản báo cáo đầy áp lực như một mối đe dọa sinh tồn. Để bảo vệ bạn khỏi cảm giác căng thẳng tột cùng, nó lập tức kích hoạt phản xạ trốn chạy quen thuộc.",
            narration_en="Modern brain experiments discovered that the human amygdala treats a stressful report as an existential threat. To shield you from intense anxiety, it triggers a flight reflex.",
            requirements=["R03"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Hạch hạnh nhân phát sáng còi báo động trước bản báo cáo deadline",
            setting="Minh họa sơ đồ não bộ với vùng hạch hạnh nhân nổi bật màu cam cảnh báo",
            camera="Cận cảnh vùng hạch hạnh nhân",
            scene_description=compose_full_frame_description("Sơ đồ cấu trúc bộ não con người vẽ bằng nét đen tối giản trên nền giấy trắng sáng, vùng hạch hạnh nhân nổi bật", "Hình tượng người que stick-figure ôm đầu hốt hoảng trước biểu tượng còi báo động mini chớp sáng"),
            foley_cue="Âm thanh nhịp tim đập thình thịch, tiếng còi báo động tần số thấp",
            claim_facts=[
                (
                    "hạch hạnh nhân trong não bộ xem bản báo cáo đầy áp lực như một mối đe dọa sinh tồn",
                    "SRC01",
                    "Hạch hạnh nhân xem áp lực công việc là mối đe dọa sinh tồn trực tiếp.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC04",
            title="Đối lập người cầu toàn và quy tắc năm phút",
            purpose="Đối lập giữa người cầu toàn và quy tắc hành động 5 phút",
            duration=11.5,
            narration="Người cầu toàn luôn chờ đợi cảm hứng hoàn hảo để làm việc, và rồi bị tê liệt. Trong khi đó, người khôn ngoan chỉ bắt đầu bằng một hành động nhỏ kéo dài vỏn vẹn năm phút để đánh lừa bộ não.",
            narration_en="Perfectionists always wait for inspiration and stay paralyzed. Meanwhile, smart thinkers begin with a simple five-minute action step that easily outsmarts the brain.",
            requirements=["R04"],
            source_ids=["SRC02"],
            character_ids=["CH01"],
            action="Hai nửa khung hình so sánh người chờ cảm hứng và người chia nhỏ 5 phút",
            setting="Bàn làm việc chia đôi với hai trạng thái tâm lý đối lập",
            camera="Trung cảnh đối xứng hai bên",
            scene_description=compose_full_frame_description("Bàn làm việc tối giản đặt chiếc đồng hồ cát đứng yên ở góc trái và đồng hồ bấm giờ năm phút ở góc phải", "Hình tượng người que stick-figure mỉm cười tự tin cầm bút bắt đầu viết vào cuốn sổ nhỏ"),
            foley_cue="Tiếng tích tắc đồng hồ nhịp nhàng 5 phút, tiếng ngòi bút chạm giấy",
            claim_facts=[
                (
                    "vỏn vẹn năm phút để đánh lừa bộ não",
                    "SRC02",
                    "Quy tắc 5 phút giúp hạ thấp nỗi sợ và bắt đầu dễ dàng.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC05",
            title="Khép vòng lặp và thông điệp thấu hiểu",
            purpose="Khép vòng lặp và thông điệp thấu hiểu bản thân",
            duration=9.0,
            narration="Lần tới khi bạn muốn mở tủ lạnh lúc nửa đêm, hãy mỉm cười và nhớ rằng: bạn không hề lười biếng, mà não bạn chỉ đang lo lắng và cần được vỗ về.",
            narration_en="Next time you want to open that fridge door late at night, smile and remember: you are not lazy, your brain is only anxious and needs care.",
            requirements=["R05"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Người que đóng nhẹ cửa tủ lạnh, mỉm cười thư thái trở lại bàn làm việc",
            setting="Căn bếp ấm áp trở về không gian tĩnh lặng bình yên",
            camera="Trung cảnh rộng dần ra",
            scene_description=compose_full_frame_description("Căn bếp tĩnh lặng với cánh cửa tủ lạnh vừa đóng lại, ánh đèn học vàng ấm áp tỏa sáng trên bàn làm việc phía xa", "Người que đóng nhẹ cửa tủ lạnh, mỉm cười thư thái trở lại bàn làm việc"),
            foley_cue="Tiếng đóng tủ lạnh êm ái 'cạch', tiếng thở phào nhẹ nhõm, nốt nhạc piano dịu dàng",
            claim_facts=[],
        ),
    ]

    return ResearchedTopic(
        topic="Nghịch lý của sự Trì hoãn: Vì sao não bộ đông cứng trước deadline?",
        audience="Người đi làm và sinh viên thường xuyên trì hoãn công việc quan trọng",
        goal="Hiểu cơ chế né tránh căng thẳng của hạch hạnh nhân và áp dụng quy tắc 5 phút",
        video_type="science",
        min_duration=45.0,
        max_duration=60.0,
        style="Minh hoạ biên tập 2D, phong cách Ink Explainer stick-figure tối giản, nét viền đen dày, nền sáng tương phản, không chữ trong ảnh.",
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
    """Create the canonical Academic Research & Knowledge Decoding blueprint (Tier 1 & Tier 2 Funnel).

    Follows up directly on the channel's 22.1K & 16.8K viral videos ('Nghịch lý tri thức' & 'Bài báo không bắt đầu ở Word'):
      - SC01 (8.0s): Counter-Intuitive Hook <= 18 syllables, 0 pauses, Vietnamese thesis/exam night context (29 syl)
      - SC02 (11.0s, 1 pause 900ms): Reframe opening Word vs Q1 research sequence (38 syl)
      - SC03 (13.0s): Causal 70/30 mechanism (Illusion of Competence + Academic Pyramid / Gap Matrix) (49 syl)
      - SC04 (11.5s): Direct Contrast (Mechanical copying at x=0.35 vs Q1 Gap Matrix at x=0.64) (43 syl)
      - SC05 (9.0s): Loop closure before the 120-second thesis defense committee (35 syl)
    """
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

    characters = [
        {
            "id": "CH01",
            "name": "Nhân vật người que nghiên cứu",
            "appearance": "Hình tượng người que đầu tròn trắng viền đen dày khép kín, mắt oval tối giản, tạo hình thống nhất trong các ảnh toàn khung",
            "outfit": "Áo sơ mi học thuật tối giản nét mực đen trên nền trắng tách lớp",
        }
    ]

    scenes = [
        ResearchedScene(
            scene_id="SC01",
            title="Cú tát sự thật: Ảo giác năng lực lúc hai giờ sáng",
            purpose="Ảo giác năng lực khi tô màu kín giáo trình và mở Word lúc hai giờ sáng",
            duration=8.0,
            narration="Đọc lại giáo trình năm lần, chỉ tạo ra ảo giác rằng bạn hiểu bài. Hai giờ sáng trước hạn nộp bài, bạn vẫn nhìn trang Word trắng tinh.",
            narration_en="Rereading your textbook five times only creates an illusion of competence. At two in the morning before thesis deadline, you still stare at a blank Word page.",
            requirements=["R01"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Sticker Nghiên Cứu ngồi trước trang Word trắng tinh và chồng giáo trình tô bút dạ quang kín chữ",
            setting="Bàn học sinh viên Việt Nam lúc hai giờ sáng với đèn bàn vàng ấm và chồng đề cương khóa luận",
            camera="Cận cảnh nhấn mạnh rồi đẩy nhanh vào màn hình",
            scene_description=compose_full_frame_description("Sơ đồ Editorial Graphic đối chiếu trang giáo trình phủ kín vệt bút dạ quang với màn hình soạn thảo trống rỗng trên bàn học đêm khuya, không có nhân vật", "Hình tượng Sticker Nghiên Cứu đầu tròn trắng viền đen dày khép kín, hai tay ôm đầu hoang mang trước chồng sách dày trên nền trắng tinh"),
            foley_cue="Tiếng bút dạ quang gạch nhanh trên giấy, tiếng đồng hồ điểm hai giờ sáng",
            claim_facts=[
                (
                    "Đọc lại giáo trình năm lần, chỉ tạo ra ảo giác rằng bạn hiểu bài",
                    "SRC01",
                    "Đọc lại giáo trình nhiều lần chỉ tạo ra ảo giác hiểu bài.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC02",
            title="Nghịch lý mở Word gõ ngay và góc nhìn hội đồng Q1",
            purpose="Sai lầm mở Word gõ ngay chương một thay vì xác định chuỗi quyết định Q1",
            duration=11.0,
            narration="Tám mươi phần trăm sinh viên làm khóa luận, bằng cách mở Word gõ ngay từ trang đầu. [pause:900ms] Nhưng các giáo sư quốc tế khẳng định, bài báo khoa học không bao giờ bắt đầu ở đó.",
            narration_en="Eighty percent of students start research by opening Word and typing page one. [pause:900ms] Yet international professors confirm a scientific paper never begins there.",
            requirements=["R02"],
            source_ids=["SRC02"],
            character_ids=["CH01"],
            action="Sticker Nghiên Cứu dùng bút đỏ gạch chéo biểu tượng mở Word gõ ngay",
            setting="Bảng sơ đồ học thuật phân tách thói quen gõ chữ cơ học và tư duy nghiên cứu chuẩn quốc tế",
            camera="Toàn cảnh góc rộng mở ra sơ đồ",
            scene_description=compose_full_frame_description("Sơ đồ Editorial Graphic sắc nét hiển thị chuỗi mũi tên quyết định từ Câu hỏi nghiên cứu đến Khoảng trống tri thức và Bằng chứng, không có nhân vật", "Hình tượng Sticker Nghiên Cứu đầu tròn trắng viền đen dày cầm bút đỏ gạch chéo tấm thẻ trang giấy trắng trên nền trắng đồng nhất"),
            foley_cue="Tiếng còi báo lỗi nhẹ, tiếp nối bằng tiếng gạch bút dứt khoát sau nhịp ngắt",
            claim_facts=[
                (
                    "bài báo khoa học không bao giờ bắt đầu ở đó",
                    "SRC02",
                    "Bài báo quốc tế bắt đầu từ khoảng trống tri thức chứ không phải Word.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC03",
            title="Giải phẫu chuỗi quyết định Q1 và Tháp Học Thuật",
            purpose="Cơ chế nhận diện mặt chữ giả tạo và chuỗi câu hỏi đến khoảng trống tri thức",
            duration=13.0,
            narration="Khi bạn chép lại lý thuyết cũ, não bộ chỉ nhận diện mặt chữ quen thuộc, chứ chưa hề tư duy. Nghiên cứu chuẩn quốc tế luôn đi từ câu hỏi cốt lõi, soi vào khoảng trống tri thức. Từ đó, họ mới chọn phương pháp đo đạc.",
            narration_en="When you copy old theories, your brain merely recognizes familiar words without thinking. International research always moves from a core question to a knowledge gap before choosing methods.",
            requirements=["R03"],
            source_ids=["SRC01", "SRC02"],
            character_ids=["CH01"],
            action="Sticker Nghiên Cứu cầm kính lúp soi trực tiếp vào tầng Khoảng trống tri thức trên Tháp Học Thuật",
            setting="Sơ đồ Tháp Học Thuật 9 tầng kết hợp chuỗi tiến trình nghiên cứu khoa học",
            camera="Đẩy cận cảnh vào điểm giao cắt khoảng trống nghiên cứu",
            scene_description=compose_full_frame_description("Đồ họa Editorial Graphic vẽ Tháp Học Thuật phân cấp 9 nguồn tài liệu và sơ đồ chuỗi tiến trình nghiên cứu khoa học rõ nét, không có nhân vật", "Hình tượng Sticker Nghiên Cứu đầu tròn trắng viền đen dày cầm chiếc kính lúp lớn soi tập trung vào khe hở sơ đồ trên nền trắng"),
            foley_cue="Tiếng kính lúp phóng đại 'whoosh', tiếng khóa mục tiêu sắc nét",
            claim_facts=[
                (
                    "não bộ chỉ nhận diện mặt chữ quen thuộc, chứ chưa hề tư duy",
                    "SRC01",
                    "Não bộ chỉ thực sự nắm bản chất khi tự truy xuất thông tin.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC04",
            title="Đối lập sao chép rời rạc và Ma trận Khoảng trống Nghiên cứu",
            purpose="Đối lập giữa sao chép tài liệu rời rạc và ma trận khoảng trống nghiên cứu",
            duration=11.5,
            narration="Người học vẹt bị nhấn chìm giữa ba mươi bài báo rời rạc, vì cố tóm tắt từng trang một. Ngược lại, người hiểu bản chất lập ma trận đối chiếu, để tìm ra đúng lỗ hổng mà giới học thuật bỏ sót.",
            narration_en="Rote learners drown in thirty scattered papers by summarizing every page. Conversely, deep thinkers build a comparison matrix to pinpoint the exact gap scholars missed.",
            requirements=["R04"],
            source_ids=["SRC02"],
            character_ids=["CH01"],
            action="Đặt đối xứng nhân vật ngợp trong bão tài liệu ở bên trái và nhân vật chỉ tay vào Ma trận Khoảng trống ở bên phải",
            setting="Bố cục đồ họa biên tập đối sánh cơn bão thông tin và bảng Ma trận Khoảng trống Nghiên cứu",
            camera="Lia ngang từ góc trái hỗn loạn sang góc phải cấu trúc",
            scene_description=compose_full_frame_description("Bảng Ma trận Khoảng trống Nghiên cứu kẻ ô ngăn nắp với điểm giao phát sáng nổi bật trên nền giấy biên tập, không có nhân vật", "Hình tượng Sticker Nghiên Cứu đầu tròn trắng viền đen dày đứng thẳng tự tin chỉ cây bút vào ô giao cắt của bảng ma trận trên nền trắng"),
            foley_cue="Tiếng giấy bay xào xạc chuyển sang tiếng kẻ bảng nhịp nhàng",
            claim_facts=[],
        ),
        ResearchedScene(
            scene_id="SC05",
            title="Làm chủ 120 giây đầu trước Hội đồng Bảo vệ",
            purpose="Làm chủ một trăm hai mươi giây đầu trước hội đồng bảo vệ khóa luận",
            duration=9.0,
            narration="Khi nắm vững khoảng trống tri thức trước lúc mở Word, bạn sẽ làm chủ phòng bảo vệ. Một trăm hai mươi giây đầu tiên trước hội đồng khóa luận, nằm trọn trong tay bạn.",
            narration_en="When you master the research gap before opening Word, you completely command the first one hundred twenty seconds before your thesis defense committee.",
            requirements=["R05"],
            source_ids=["SRC02"],
            character_ids=["CH01"],
            action="Sticker Nghiên Cứu đứng tự tin trước bục bảo vệ khóa luận với sơ đồ chuỗi nghiên cứu tỏa sáng phía sau",
            setting="Phòng bảo vệ khóa luận trang trọng với đồng hồ 120 giây và sơ đồ nghiên cứu chuẩn mực",
            camera="Trung cảnh mở rộng tôn vinh tư thế tự tin",
            scene_description=compose_full_frame_description("Bục thuyết trình phòng bảo vệ khóa luận với màn chiếu hiển thị sơ đồ khoảng trống nghiên cứu rõ nét, không có nhân vật", "Sticker Nghiên Cứu đứng tự tin trước bục bảo vệ khóa luận với sơ đồ chuỗi nghiên cứu tỏa sáng phía sau"),
            foley_cue="Tiếng gõ bút đồng thuận của hội đồng, âm hưởng piano trầm ấm kết thúc",
            claim_facts=[
                (
                    "Một trăm hai mươi giây đầu tiên trước hội đồng khóa luận",
                    "SRC02",
                    "Hội đồng bảo vệ luôn soi khoảng trống nghiên cứu trong hai phút đầu.",
                )
            ],
        ),
    ]

    use_subs = True if subtitles is None and aspect_ratio == "9:16" else bool(subtitles)
    use_speed = 1.26 if aspect_ratio == "9:16" else 1.22

    return ResearchedTopic(
        topic="Nghịch lý Tri thức và Ảo giác Năng lực: Giải phẫu cơ chế nhận thức khiến việc đọc lại giáo trình thụ động và mở Word gõ ngay làm tê liệt tư duy nghiên cứu khoa học chuẩn Q1",
        audience="Sinh viên, học viên cao học, kỹ sư và người tự học tại Việt Nam muốn hiểu bản chất tri thức và làm chủ quy trình nghiên cứu chuẩn quốc tế",
        goal="Phá vỡ ảo giác năng lực khi học vẹt, chuyển từ thói quen mở Word gõ ngay sang chuỗi quyết định Question -> Gap -> Method -> Evidence và làm chủ 120s đầu phòng bảo vệ",
        video_type="science",
        min_duration=45.0,
        max_duration=60.0,
        style="Minh hoạ Editorial Graphic 2D toàn khung, nhân vật người que viền đen dày tương tác vật lý với Sơ đồ Tháp Học Thuật trong cùng một bố cục; không tách sticker, không chữ thừa trong ảnh.",
        aspect_ratio=aspect_ratio,
        sources=sources,
        required_points=required_points,
        characters=characters,
        scenes=scenes,
        tone="Điềm đạm, sắc sảo, thông tuệ, chạm trúng tâm lý học thuật",
        language="vi",
        subtitles=use_subs,
        voice="Adam",
        speed=use_speed,
        conversational_facts=True,
        packaging=PackagingSpec(
            youtube_title="Ảo Giác Năng Lực: Vì Sao Đọc Lại Sách Làm Não Tê Liệt?",
            visual_hook="Nhân vật người que cầm bút đỏ gạch chéo biểu tượng mở Word ngay trước Sơ đồ Tháp Học Thuật và chuỗi Question -> Gap",
            text_overlay="BIẾT TÍNH ≠ HIỂU!",
            contrast_pair="Mở Word gõ ngay vs. Ma trận Khoảng trống Q1",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "ảo giác năng lực",
                "tư duy nghiên cứu khoa học",
                "cách đọc bài báo Q1",
                "bảo vệ khóa luận tốt nghiệp",
                "ma trận khoảng trống nghiên cứu",
            ],
        ),
    )


def build_short_spinoff_topics(
    parent_topic: ResearchedTopic,
    max_spinoffs: int = 3,
) -> List[ResearchedTopic]:
    """Generate 2-3 standalone short_9x16 spin-off topics (45-60s, 5 scenes, subtitles=True, speed=1.26)
    from a researched dossier, each with its own independent Counter-Intuitive Hook <= 18 syllables.
    Never raw-cuts middle chapters (CH02..CH08) of a 16:9 video.
    """
    spinoff_templates = [
        create_academic_research_paradox_topic(aspect_ratio="9:16", subtitles=True),
    ]

    # Spin-off #2: Tier 2 Mid Funnel (120-Second Thesis Defense Committee Psychology)
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
    chars_t2 = [
        {
            "id": "CH01",
            "name": "Nhân vật người que nghiên cứu",
            "appearance": "Hình tượng người que đầu tròn trắng viền đen dày khép kín, mắt oval tối giản, tạo hình thống nhất trong các ảnh toàn khung",
            "outfit": "Áo sơ mi học thuật tối giản nét mực đen trên nền trắng tách lớp",
        }
    ]
    scenes_t2 = [
        ResearchedScene(
            scene_id="SC01",
            title="Cửa sổ 120 giây định đoạt trên bục bảo vệ khóa luận",
            purpose="Cửa sổ một trăm hai mươi giây đầu tiên khi bước lên bục bảo vệ khóa luận",
            duration=8.0,
            narration="Hội đồng bảo vệ định hình phán quyết ngay trong hai phút đầu tiên. Khi bạn bước lên bục thuyết trình, đồng hồ tâm lý đã bắt đầu đếm ngược.",
            narration_en="Defense committees form their verdict within the first two minutes. When you step up to the podium, the psychological clock starts ticking.",
            requirements=["R01"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Sticker Nghiên Cứu đứng trên bục bảo vệ đối diện bàn hội đồng và đồng hồ 120 giây",
            setting="Phòng bảo vệ khóa luận đại học tại Việt Nam với đồng hồ đếm ngược 120 giây",
            camera="Đẩy cận cảnh vào đồng hồ 120 giây và ánh mắt hội đồng",
            scene_description=compose_full_frame_description("Đồ họa Editorial Graphic vẽ bàn hội đồng bảo vệ khóa luận và đồng hồ 120 giây phát sáng trên nền tối tương phản, không có nhân vật", "Hình tượng Sticker Nghiên Cứu đầu tròn trắng viền đen dày khép kín, đứng thẳng nắm tập khóa luận trước bục thuyết trình trên nền trắng"),
            foley_cue="Tiếng đồng hồ tích tắc dồn dập 120 giây",
            claim_facts=[
                (
                    "Hội đồng bảo vệ định hình phán quyết ngay trong hai phút đầu tiên",
                    "SRC01",
                    "Hội đồng bảo vệ định hình phán quyết ngay trong hai phút đầu tiên.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC02",
            title="Bí mật trang giấy hội đồng lật xem đầu tiên",
            purpose="Hành động đầu tiên của giám khảo là lật trang danh mục tài liệu tham khảo",
            duration=11.0,
            narration="Tám mươi phần trăm sinh viên tưởng thầy cô, đang chăm chú đọc màn chiếu mở đầu. [pause:900ms] Thực tế trong phòng bảo vệ, giám khảo luôn lật trang tài liệu tham khảo trước khi nghe bạn nói.",
            narration_en="Eighty percent of students think professors are reading the opening slide. [pause:900ms] In reality, examiners flip straight to the reference list before listening.",
            requirements=["R02"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Sticker Nghiên Cứu chỉ kính lúp vào trang Danh mục tài liệu tham khảo ở cuối cuốn khóa luận",
            setting="Sơ đồ X-quang cuốn khóa luận làm nổi bật trang Tài liệu tham khảo",
            camera="Toàn cảnh lật ngược cuốn khóa luận về trang cuối",
            scene_description=compose_full_frame_description("Sơ đồ Editorial Graphic hiển thị cuốn khóa luận mở sẵn ở trang Danh mục tài liệu tham khảo với dấu kiểm định nguồn Q1, không có nhân vật", "Hình tượng Sticker Nghiên Cứu đầu tròn trắng viền đen dày cầm kính lúp soi vào trang tài liệu tham khảo trên nền trắng"),
            foley_cue="Tiếng lật giấy nhanh về cuối sách, nhịp dừng 900ms",
            claim_facts=[
                (
                    "giám khảo luôn lật trang tài liệu tham khảo trước khi nghe bạn nói",
                    "SRC01",
                    "Giám khảo luôn lật trang tài liệu tham khảo trước khi nghe bạn nói.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC03",
            title="Sai lầm đọc lại định nghĩa và trả lời bằng số liệu rời rạc",
            purpose="Sai lầm đốt năm phút đầu đọc lại định nghĩa và trả lời tính mới bằng số liệu rời rạc",
            duration=13.0,
            narration="Đọc lại định nghĩa giáo trình làm mất điểm ngay từ mở bài. Khi hội đồng hỏi đề tài này có gì mới, nhiều bạn lại cuống cuồng đọc hàng loạt bảng số liệu. Nhưng số liệu dày đặc kia, không bao giờ thay thế được khoảng trống nghiên cứu.",
            narration_en="Reading textbook definitions loses points right from the opening. When asked what is new, many students frantically recite raw data tables. Yet numbers never replace a clear research gap.",
            requirements=["R03"],
            source_ids=["SRC02"],
            character_ids=["CH01"],
            action="Sticker Nghiên Cứu gạch chéo slide định nghĩa dài dòng và bảng số liệu hỗn độn",
            setting="Sơ đồ cảnh báo hai lỗi chí mạng trên bục bảo vệ khóa luận",
            camera="Cận cảnh tấm bảng lỗi thuyết trình bị gạch đỏ",
            scene_description=compose_full_frame_description("Đồ họa Editorial Graphic vẽ khung trình chiếu chật kín định nghĩa sách giáo khoa bị gạch đỏ cảnh báo, không có nhân vật", "Hình tượng Sticker Nghiên Cứu đầu tròn trắng viền đen dày cầm bút đỏ gạch chéo tấm thẻ định nghĩa cũ trên nền trắng"),
            foley_cue="Tiếng còi cảnh báo nhẹ và tiếng gạch bút",
            claim_facts=[
                (
                    "Đọc lại định nghĩa giáo trình làm mất điểm ngay từ mở bài",
                    "SRC02",
                    "Đọc lại định nghĩa giáo trình làm mất điểm ngay từ mở bài.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC04",
            title="Đối lập liệt kê lan man và Cấu trúc Phản biện 3 Bước",
            purpose="Đối lập giữa liệt kê số liệu lan man và cấu trúc phản biện ba bước sắc bén",
            duration=11.5,
            narration="Người lúng túng chỉ liệt kê mình đã chạy bao nhiêu mẫu khảo sát. Ngược lại, cấu trúc phản biện ba bước giúp làm chủ câu hỏi tính mới. Hãy nêu rõ người trước làm gì, bỏ ngỏ gì, và bạn đo đạc ra sao.",
            narration_en="Confused speakers only list how many samples they surveyed. Conversely, a three-step rebuttal structure commands the novelty question. State what prior work did, what gap remained, and how your method solves it.",
            requirements=["R04"],
            source_ids=["SRC02"],
            character_ids=["CH01"],
            action="Đặt đối xứng nhân vật lúng túng bên trái và nhân vật chỉ vào Sơ đồ 3 Bước bên phải",
            setting="Sơ đồ Cấu trúc Phản biện 3 Bước: Đã biết -> Lỗ hổng bỏ ngỏ -> Giải pháp đo đạc",
            camera="Lia ngang sang Sơ đồ 3 Bước phát sáng",
            scene_description=compose_full_frame_description("Sơ đồ Editorial Graphic 3 khối mũi tên sắc nét: Công trình trước -> Khoảng trống bỏ ngỏ -> Phương pháp giải quyết mới, không có nhân vật", "Hình tượng Sticker Nghiên Cứu đầu tròn trắng viền đen dày tự tin chỉ tay vào sơ đồ 3 bước trên nền trắng"),
            foley_cue="Tiếng ba nhịp khóa mục tiêu sắc gọn",
            claim_facts=[
                (
                    "cấu trúc phản biện ba bước giúp làm chủ câu hỏi tính mới",
                    "SRC02",
                    "Cấu trúc phản biện ba bước giúp làm chủ câu hỏi tính mới.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC05",
            title="Khép vòng lặp: Làm chủ 120 giây đầu trước Hội đồng",
            purpose="Khép vòng lặp làm chủ hoàn toàn phòng bảo vệ khóa luận ngay từ hai phút đầu",
            duration=9.0,
            narration="Khi mở màn trực diện bằng khoảng trống tri thức, bạn sẽ thuyết phục trọn vẹn hội đồng. Một trăm hai mươi giây đầu tiên trên bục bảo vệ, giờ nằm trọn trong tay bạn.",
            narration_en="When you open directly with a clear research gap and top-tier sources, you win over the entire committee within the first one hundred twenty seconds.",
            requirements=["R05"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Sticker Nghiên Cứu mỉm cười tự tin trên bục bảo vệ khi đồng hồ 120 giây chuyển sang ánh sáng xanh đồng thuận",
            setting="Phòng bảo vệ khóa luận khép lại vòng lặp với sự tán thưởng của hội đồng",
            camera="Trung cảnh mở rộng tôn vinh người thuyết trình",
            scene_description=compose_full_frame_description("Phòng bảo vệ khóa luận sáng rõ với sơ đồ 3 bước phản biện trên màn chiếu và đồng hồ 120 giây hoàn tất, không có nhân vật", "Sticker Nghiên Cứu mỉm cười tự tin trên bục bảo vệ khi đồng hồ 120 giây chuyển sang ánh sáng xanh đồng thuận"),
            foley_cue="Tiếng gõ bút đồng thuận, âm nhạc kết thúc đĩnh đạc",
            claim_facts=[],
        ),
    ]
    spinoff_t2 = ResearchedTopic(
        topic=f"{parent_topic.topic} — Spin-off: Tâm lý Hội đồng Bảo vệ trong 120 Giây Đầu",
        audience=parent_topic.audience,
        goal="Giải mã tâm lý hội đồng bảo vệ khóa luận trong 120 giây đầu và áp dụng cấu trúc phản biện 3 bước",
        video_type="science",
        min_duration=45.0,
        max_duration=60.0,
        style="Minh hoạ Editorial Graphic 2D toàn khung, nhân vật người que tương tác trực tiếp với Sơ đồ 3 Bước Phản Biện trong cùng bối cảnh, khung dọc 9:16.",
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=sources_t2,
        required_points=req_t2,
        characters=chars_t2,
        scenes=scenes_t2,
        tone="Sắc sảo, kịch tính, chạm đúng tâm lý phòng bảo vệ",
        language="vi",
        subtitles=True,
        voice="Adam",
        speed=1.26,
        conversational_facts=True,
        packaging=PackagingSpec(
            youtube_title="Tâm Lý Hội Đồng: Cửa Sổ 120 Giây Định Đoạt Khóa Luận",
            visual_hook="Đồng hồ 120 giây phía trên bàn Hội đồng khi nhân vật người que mở trang Tài liệu tham khảo",
            text_overlay="120 GIÂY ĐẦU!",
            contrast_pair="Đọc lại lý thuyết vs. Phản biện 3 bước",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_2_mid",
            seo_keywords=[
                "bảo vệ khóa luận tốt nghiệp",
                "tâm lý hội đồng bảo vệ",
                "đề tài này có gì mới",
                "cách trả lời phản biện khóa luận",
                "tư duy nghiên cứu khoa học",
            ],
        ),
    )
    spinoff_templates.append(spinoff_t2)

    # Spin-off #2: Tier 3 Conversion Funnel (AI for Deep Research / Research Gap Matrix)
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
    chars_t3 = [
        {
            "id": "CH01",
            "name": "Nhân vật người que nghiên cứu",
            "appearance": "Hình tượng người que đầu tròn trắng viền đen dày khép kín, mắt oval tối giản, tạo hình thống nhất trong các ảnh toàn khung",
            "outfit": "Áo sơ mi học thuật tối giản nét mực đen trên nền trắng tách lớp",
        }
    ]
    scenes_t3 = [
        ResearchedScene(
            scene_id="SC01",
            title="Cơn bão thông tin trước ba mươi bài báo quốc tế",
            purpose="Cơn bão thông tin khi tải hàng chục bài báo Q1 về máy nhưng không biết đọc từ đâu",
            duration=8.0,
            narration="Tải ba mươi bài báo quốc tế, chẳng giúp bạn có đề tài mới. Đêm khuya mở thư mục tài liệu, não bạn tê liệt vì quá tải.",
            narration_en="Downloading thirty international papers does not give you a new thesis topic. Late at night facing a flooded folder, your brain immediately freezes from overload.",
            requirements=["R01"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Sticker Nghiên Cứu choáng váng giữa hàng chục tập tài liệu PDF bay quanh bàn học",
            setting="Bàn làm việc sinh viên Việt Nam đêm khuya với màn hình mở hàng chục tab bài báo khoa học",
            camera="Đẩy cận cảnh nhanh vào chồng tài liệu phân mảnh",
            scene_description=compose_full_frame_description("Đồ họa Editorial Graphic vẽ hàng chục thẻ bài báo khoa học xếp chồng hỗn loạn tạo thành cơn bão thông tin trên nền tối tương phản, không có nhân vật", "Hình tượng Sticker Nghiên Cứu đầu tròn trắng viền đen dày khép kín, hai tay đỡ chồng tài liệu cao ngất với biểu cảm quá tải trên nền trắng"),
            foley_cue="Tiếng thông báo tải file dồn dập, tiếng gió xoáy nhẹ",
            claim_facts=[
                (
                    "Đêm khuya mở thư mục tài liệu, não bạn tê liệt vì quá tải",
                    "SRC01",
                    "Đọc ba mươi bài báo rời rạc làm quá tải bộ nhớ làm việc.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC02",
            title="Vì sao dùng AI viết hộ luôn bị phát hiện ở mục Tổng quan",
            purpose="Sai lầm nhờ công cụ viết hộ tổng quan tài liệu khiến hội đồng phát hiện ngay",
            duration=11.0,
            narration="Nhiều bạn hoảng loạn liền yêu cầu công cụ trí tuệ nhân tạo, viết hộ mục tổng quan. [pause:900ms] Nhưng hội đồng bảo vệ luôn nhận ra ngay, văn phong liệt kê sáo rỗng thiếu trục phản biện.",
            narration_en="Many panicked students ask artificial intelligence to write their literature review. [pause:900ms] Yet defense committees immediately spot hollow summaries lacking critical debate.",
            requirements=["R02"],
            source_ids=["SRC02"],
            character_ids=["CH01"],
            action="Sticker Nghiên Cứu gạch chéo đoạn văn tổng quan liệt kê rời rạc bị đóng dấu cảnh báo đỏ",
            setting="Sơ đồ so sánh văn bản liệt kê bề mặt và cấu trúc phản biện học thuật",
            camera="Toàn cảnh đối chiếu",
            scene_description=compose_full_frame_description("Sơ đồ Editorial Graphic hiển thị các khối văn bản liệt kê rời rạc bị gạch đỏ đối diện cấu trúc mạng lưới phản biện lý thuyết, không có nhân vật", "Hình tượng Sticker Nghiên Cứu đầu tròn trắng viền đen dày cầm kính lúp soi vào vết nứt trên tờ văn bản mẫu trên nền trắng"),
            foley_cue="Tiếng còi cảnh báo nhẹ, nhịp dừng 900ms rồi tiếng đóng dấu",
            claim_facts=[
                (
                    "Nhưng hội đồng bảo vệ luôn nhận ra ngay, văn phong liệt kê sáo rỗng",
                    "SRC02",
                    "Dùng trí tuệ nhân tạo viết hộ tổng quan luôn lộ lỗi sáo rỗng.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC03",
            title="Cơ chế gom 30 bài báo thành Ma trận Khoảng trống Nghiên cứu",
            purpose="Cơ chế gom 30 bài báo rời rạc thành Ma trận Khoảng trống Nghiên cứu",
            duration=13.0,
            narration="Thay vì bảo máy viết hộ, hãy biến ba mươi bài báo kia, thành một ma trận khoảng trống nghiên cứu. Bạn yêu cầu hệ thống bóc tách từng bài theo bốn cột, gồm câu hỏi và phương pháp. Cuối cùng là dữ liệu, và giới hạn chưa giải quyết.",
            narration_en="Instead of asking it to write for you, turn thirty papers into a research gap matrix. Extract each paper across four columns: question, method, evidence, and unsolved limits.",
            requirements=["R03"],
            source_ids=["SRC01", "SRC02"],
            character_ids=["CH01"],
            action="Sticker Nghiên Cứu sắp xếp các mảnh dữ liệu vào bảng Ma trận 4 cột Question - Gap - Method - Evidence",
            setting="Bảng Ma trận Khoảng trống Nghiên cứu 4 cột phát sáng rõ nét",
            camera="Cận cảnh theo từng cột của ma trận",
            scene_description=compose_full_frame_description("Bảng đồ họa Editorial Graphic 4 cột biểu diễn chuỗi Câu hỏi, Khoảng trống, Phương pháp và Bằng chứng với các nút liên kết sắc nét, không có nhân vật", "Hình tượng Sticker Nghiên Cứu đầu tròn trắng viền đen dày cầm thước chỉ vào cột giới hạn chưa giải quyết trên nền trắng"),
            foley_cue="Tiếng các ô dữ liệu khớp vào bảng ma trận 'click' gọn gàng",
            claim_facts=[
                (
                    "hãy biến ba mươi bài báo kia, thành một ma trận khoảng trống nghiên cứu",
                    "SRC01",
                    "Ma trận đối chiếu giúp gom mảnh ghép thành khoảng trống nghiên cứu.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC04",
            title="Tương phản tóm tắt thụ động và phản biện chéo lý thuyết",
            purpose="Đối lập giữa tóm tắt từng bài rời rạc và phản biện chéo tìm lỗ hổng phương pháp",
            duration=11.5,
            narration="Người nghiệp dư chỉ tóm tắt từng bài riêng lẻ, nên mãi dậm chân tại chỗ trong mớ hỗn độn. Ngược lại, nhà nghiên cứu dùng trí tuệ nhân tạo để phản biện chéo các trường phái, và khoanh vùng lỗ hổng phương pháp.",
            narration_en="Amateurs summarize papers one by one and stay stuck. Conversely, researchers use deep analysis to cross-examine schools of thought and isolate methodological gaps.",
            requirements=["R04"],
            source_ids=["SRC02"],
            character_ids=["CH01"],
            action="Đặt đối xứng nhân vật tóm tắt rời rạc ở bên trái và nhân vật soi giao điểm phản biện chéo ở bên phải",
            setting="Đồ họa đối sánh hai cấp độ khai thác tài liệu khoa học",
            camera="Lia ngang từ trái sang phải",
            scene_description=compose_full_frame_description("Đồ họa Editorial Graphic đối chiếu các tờ ghi chú rời rạc bên trái với sơ đồ giao thoa ba vòng tròn lý thuyết phát sáng bên phải, không có nhân vật", "Hình tượng Sticker Nghiên Cứu đầu tròn trắng viền đen dày mỉm cười nâng mảnh ghép trung tâm tỏa sáng trên nền trắng"),
            foley_cue="Tiếng tia sáng hội tụ tại tâm sơ đồ giao thoa",
            claim_facts=[
                (
                    "phản biện chéo các trường phái, và khoanh vùng lỗ hổng phương pháp",
                    "SRC02",
                    "Hãy dùng công cụ để phản biện chéo lý thuyết và tìm bằng chứng.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC05",
            title="Khép vòng lặp: Vũ khí tư duy làm chủ tri thức",
            purpose="Làm chủ vũ khí tư duy học thuật để biến dữ liệu phân mảnh thành đề tài xuất sắc",
            duration=9.0,
            narration="Khi biến cơn bão thông tin thành ma trận khoảng trống rõ ràng, bế tắc sẽ tan biến. Ba mươi bài báo kia trở thành bệ phóng vững chắc, cho công trình của bạn.",
            narration_en="When you transform an information storm into a clear gap matrix, those thirty papers become a solid launchpad for your own original research.",
            requirements=["R05"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Sticker Nghiên Cứu đứng trên đỉnh Tháp Học Thuật nhìn toàn cảnh ma trận nghiên cứu hoàn chỉnh",
            setting="Bàn học sáng rõ với bảng Ma trận Khoảng trống Nghiên cứu hoàn chỉnh trên màn hình lớn",
            camera="Trung cảnh mở rộng",
            scene_description=compose_full_frame_description("Bàn làm việc học thuật ngăn nắp với màn hình hiển thị Ma trận Khoảng trống Nghiên cứu hoàn chỉnh và Tháp Học Thuật vững chãi, không có nhân vật", "Sticker Nghiên Cứu đứng trên đỉnh Tháp Học Thuật nhìn toàn cảnh ma trận nghiên cứu hoàn chỉnh"),
            foley_cue="Âm thanh hoàn tất ấm áp, nốt nhạc kết thúc truyền cảm hứng",
            claim_facts=[],
        ),
    ]

    spinoff_2 = ResearchedTopic(
        topic=f"{parent_topic.topic} — Spin-off: Ma trận Khoảng trống Nghiên cứu (Research Gap Matrix)",
        audience=parent_topic.audience,
        goal="Biến 30 bài báo Q1 rời rạc thành Ma trận Khoảng trống Nghiên cứu và dùng AI phản biện chéo lý thuyết thay vì viết hộ",
        video_type="science",
        min_duration=45.0,
        max_duration=60.0,
        style="Minh hoạ Editorial Graphic 2D toàn khung, nhân vật người que làm việc trực tiếp với Bảng Ma trận Khoảng trống Nghiên cứu trong cùng bố cục, khung dọc 9:16.",
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=sources_t3,
        required_points=req_t3,
        characters=chars_t3,
        scenes=scenes_t3,
        tone="Sắc bén, thực chiến, chuẩn mực học thuật Q1",
        language="vi",
        subtitles=True,
        voice="Adam",
        speed=1.26,
        conversational_facts=True,
        packaging=PackagingSpec(
            youtube_title="Ma Trận Research Gap: Đọc 30 Bài Báo Q1 Không Quá Tải",
            visual_hook="Nhân vật người que dùng kính lúp kiểm tra Bảng Ma trận Khoảng trống Nghiên cứu 4 cột giữa các bài PDF rời rạc",
            text_overlay="ĐỪNG BẢO AI VIẾT HỘ!",
            contrast_pair="Viết hộ sáo rỗng vs. Phản biện chéo Q1",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_3_conversion",
            seo_keywords=[
                "ma trận khoảng trống nghiên cứu",
                "research gap matrix",
                "cách đọc bài báo Q1",
                "tổng quan tài liệu luận văn",
                "AI cho nghiên cứu khoa học",
            ],
        ),
    )
    spinoff_templates.append(spinoff_2)
    return spinoff_templates[: max(1, max_spinoffs)]


def write_production_package(
    output_dir: Path,
    topic: ResearchedTopic,
    system_root: Path = SYS_DIR,
    brief_revision: int = 1,
    include_spinoffs: bool = False,
    omni_plan: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Assemble and write brief.json, content.json, script.json, cadence_report.json, and optional short_9x16 spin-offs."""
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

    # Cadence checker validation
    checker = ScriptCadenceChecker(nominal_rate=NOMINAL_SPEECH_RATE)
    standardized_scenes = script_data
    cadence_report = checker.check_scenes(standardized_scenes)

    # Write files to disk with identical serialization to Video Pilot (idempotent mtime)
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

    # Contract schema validation
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
        "spinoff_packages": spinoff_packages,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Research Story Architect: Formulate schema 3.0 blueprints from researched topics."
    )
    parser.add_argument("--demo", action="store_true", help="Generate benchmark production package for trial topic")
    parser.add_argument(
        "--topic",
        choices=["procrastination-paradox", "motivation-history-13m", "academic-paradox-q1", "academic-research-13m"],
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
        if selected_topic == "motivation-history-13m":
            from build_motivation_history_13m import create_motivation_history_13m_topic

            job_id = args.job_id or f"motivation-history-{args.aspect_ratio.replace(':', 'x')}-13m"
            out_dir = Path(args.output_dir) if args.output_dir else SYS_DIR / f"runs/{job_id}"
            print("[*] Đang kiến trúc bộ hồ sơ kỹ thuật 13 phút cho chủ đề: 'Lịch sử tiến hóa của Động lực'...")
            topic = create_motivation_history_13m_topic(aspect_ratio=args.aspect_ratio, subtitles=args.subtitles)
        elif selected_topic == "academic-research-13m":
            from build_academic_research_paradox_13m import build_multi_chapter_bundle as build_academic_bundle
            from build_academic_research_paradox_13m import create_academic_research_13m_topic

            job_id = args.job_id or f"academic-research-paradox-{args.aspect_ratio.replace(':', 'x')}-13m"
            out_dir = Path(args.output_dir) if args.output_dir else SYS_DIR / f"runs/{job_id}"
            print("[*] Đang kiến trúc bộ hồ sơ 13 phút (8 chương / 48 cảnh) ngách Tư Duy Nghiên Cứu Q1...")
            topic = create_academic_research_13m_topic(aspect_ratio=args.aspect_ratio, subtitles=args.subtitles)
            if args.aspect_ratio == "16:9":
                bundle_dir = SYS_DIR / "exports/academic_research_paradox_bundle"
                build_academic_bundle(bundle_dir, topic)
        elif selected_topic == "academic-paradox-q1":
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

        result = write_production_package(out_dir, topic, system_root=SYS_DIR, include_spinoffs=args.spinoff_shorts, omni_plan=json.loads(Path(args.omni_plan).read_text()) if args.omni_plan else None)

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
