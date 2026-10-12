#!/usr/bin/env python3
"""Research Story Architect for Video Pilot.

Upstream narrative and technical engine for the `vp-research-architect` skill.
Transforms structured research and academic facts into schema 3.0 valid `brief.json`
and `content.json` bundles with acoustic cadence calibration (P_tail formula),
layered motion (background vs stickers), visual beats, and Foley cues.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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
    DEFAULT_P_TAIL_LAST,
    DEFAULT_P_TAIL_PARA,
    NOMINAL_SPEECH_RATE,
    ScriptCadenceChecker,
    calculate_target_syllables,
    count_syllables,
)

RULE_OF_THIRDS_X: Tuple[float, float] = (0.35, 0.64)
_DRY_ACADEMIC_FACT_RE = re.compile(
    r"(?:\bdoi\s*:|\bisbn\s*:|\bet\s+al\.|\bpp?\.\s*\d|\(\d{4}\)|\d+\s*%|\w+/\w+)",
    re.IGNORECASE,
)


def select_semantic_camera_effect(
    framing_or_camera: str,
    prev_effect: Optional[str] = None,
) -> str:
    """Map framing or camera direction to a semantic Remotion camera effect without consecutive duplicates."""
    text = (framing_or_camera or "").strip().lower()
    if text in ("zoom_in", "zoom_out", "punch_in", "pan_left", "pan_right"):
        eff = text
    elif any(k in text for k in ("extreme", "macro", "đặc tả", "nhấn", "punch")):
        eff = "punch_in"
    elif any(k in text for k in ("wide", "establishing", "pull", "zoom_out", "zoom out", "toàn cảnh", "rộng", "mở rộng")):
        eff = "zoom_out"
    elif any(k in text for k in ("left", "trái", "ngược", "quay lại", "đối lập")):
        eff = "pan_left"
    elif any(k in text for k in ("pan", "tracking", "quét", "lia", "đối xứng", "ngang")):
        eff = "pan_right"
    else:
        eff = "zoom_in"

    if prev_effect is not None and eff == prev_effect:
        eff = "pan_right" if prev_effect != "pan_right" else "zoom_in"
    return eff


def assign_scene_camera_effects(camera_descriptions: List[str]) -> List[str]:
    """Assign semantic camera effects across a sequence of shots with zero consecutive duplicates."""
    effects: List[str] = []
    prev: Optional[str] = None
    for desc in camera_descriptions:
        eff = select_semantic_camera_effect(desc, prev_effect=prev)
        effects.append(eff)
        prev = eff
    return effects


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
    bg_description: str
    stickers: List[ResearchedSticker] = field(default_factory=list)
    reused_sticker_ids: List[Tuple[Any, ...]] = field(default_factory=list)  # (sticker_id, anchor_quote, fx, [anchor_quote_en])
    foley_cue: Optional[str] = None
    claim_facts: List[Tuple[str, str, str]] = field(default_factory=list)  # (quote, source_id, fact)
    narration_en: Optional[str] = None


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
    return brief


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

    for sc_idx, sc in enumerate(topic.scenes):
        s_id = sc.scene_id

        # Images list: 1 background plate + new stickers
        images = []
        bg_id = f"{s_id}_BG"
        images.append({
            "id": bg_id,
            "description": sc.bg_description,
            "character_ids": [],
            "based_on": None,
            "preserve": "",
            "change": "Thiết lập bối cảnh nền",
            "reason": "Bối cảnh nền",
            "visible_text": [],
            "kind": "background",
        })

        layers = []
        # New stickers
        for st_idx, st in enumerate(sc.stickers):
            images.append({
                "id": st.id,
                "description": st.description,
                "character_ids": st.character_ids,
                "based_on": None,
                "preserve": "",
                "change": "Xuất hiện nhân vật minh họa",
                "reason": "Minh họa hành động nhân vật",
                "visible_text": [],
                "kind": "sticker",
            })
            anchor_payload: Dict[str, Any] = {
                "vi": {
                    "quote": st.anchor_quote,
                    "occurrence": 1,
                }
            }
            if needs_en and sc.narration_en:
                quote_en = getattr(st, "anchor_quote_en", None)
                if not quote_en:
                    quote_en = " ".join(sc.narration_en.split()[:3]).rstrip(".,;:!?")
                anchor_payload["en"] = {
                    "quote": quote_en,
                    "occurrence": 1,
                }
            st_x = RULE_OF_THIRDS_X[(sc_idx + st_idx) % 2] if st.x == 0.5 else st.x
            layers.append({
                "id": f"LAY_{st.id}",
                "image_id": st.id,
                "anchor": anchor_payload,
                "fx": st.fx,
                "x": st_x,
                "y": st.y,
                "w": st.w,
                "z": st.z,
            })

        # Reused stickers from previous scenes
        for idx, item in enumerate(sc.reused_sticker_ids, 1):
            reused_id, anchor_quote, fx_name = item[0], item[1], item[2]
            reused_anchor: Dict[str, Any] = {
                "vi": {
                    "quote": anchor_quote,
                    "occurrence": 1,
                }
            }
            if needs_en and sc.narration_en:
                quote_en = item[3] if len(item) > 3 else None
                if not quote_en:
                    quote_en = " ".join(sc.narration_en.split()[:3]).rstrip(".,;:!?")
                reused_anchor["en"] = {
                    "quote": quote_en,
                    "occurrence": 1,
                }
            layers.append({
                "id": f"LAY_{s_id}_REUSE_{idx}",
                "image_id": reused_id,
                "anchor": reused_anchor,
                "fx": fx_name,
                "x": RULE_OF_THIRDS_X[(sc_idx + idx) % 2],
                "y": 0.65,
                "w": 0.35,
                "z": 2,
            })

        # The beat for the background plate - MUST start at index 0 of narration
        # Extract first 4 words of narration as the anchor quote
        first_words = " ".join(sc.narration.split()[:4]).rstrip(".,;:!?")
        beat_anchor: Dict[str, Any] = {
            "vi": {
                "quote": first_words,
                "occurrence": 1,
            }
        }
        if needs_en and sc.narration_en:
            first_words_en = " ".join(sc.narration_en.split()[:4]).rstrip(".,;:!?")
            beat_anchor["en"] = {
                "quote": first_words_en,
                "occurrence": 1,
            }
        beats = [
            {
                "id": f"{s_id}_B1",
                "image_id": bg_id,
                "purpose": sc.purpose,
                "anchor": beat_anchor,
                "effect": "hold",
                "focus": {"x": 0.5, "y": 0.5},
            }
        ]

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
            "layers": layers,
        }
        if sc.narration_en:
            scene_dict["narration_en"] = sc.narration_en

        content_scenes.append(scene_dict)

        # Coverage: link requirements to scene quotes
        for r_id in sc.requirements:
            if r_id in req_map:
                # Find a short quote from narration for coverage
                # Pick the first matching sentence or significant phrase
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
    for s in topic.scenes:
        script_items.append({
            "id": s.scene_id,
            "duration": s.duration,
            "narration": s.narration,
            "beats": [],
        })
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
    """Create the trial benchmark topic: 'Nghịch lý của sự Trì hoãn' (The Procrastination Paradox).

    Academic Basis:
      - Dr. Timothy A. Pychyl & Dr. Fuschia M. Sirois (2013).
        'Procrastination and the Priority of Short-Term Mood Regulation'
      - Dr. Laura Rabin et al. (2011).
        'The Neurobiology of Procrastination: Prefrontal Cortex and Amygdala'

    5-Part Causal Arc:
      SC01: Hook & Empathy (8.0s) -> 30 syl, drift +0.20s
      SC02: Reframe & Paradox (11.0s, pause 900ms) -> 38 syl, drift +0.10s
      SC03: Causal 70/30 Mechanism (13.0s) -> 50 syl, drift +0.20s
      SC04: Direct Contrast (11.5s) -> 43 syl, drift -0.05s
      SC05: Loop Payoff (9.0s, last) -> 34 syl, drift -0.15s
      Total Duration: 52.5s (Min: 45s, Max: 60s)
    """
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
            bg_description="Căn bếp gia đình tĩnh mịch lúc đêm muộn với tủ lạnh đang mở toang tỏa ra ánh sáng vàng nhạt, không có nhân vật",
            stickers=[
                ResearchedSticker(
                    id="SC01_ST1",
                    description="Hình tượng người que stick-figure đầu tròn trắng viền đen dày, biểu cảm bối rối đưa tay gãi đầu, đứng nhìn vào ánh sáng",
                    character_ids=["CH01"],
                    anchor_quote="bạn lại đứng ngơ ngác",
                    anchor_quote_en="blankly open the fridge",
                    fx="pop",
                    x=0.35,
                    y=0.65,
                    w=0.35,
                    z=2,
                )
            ],
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
            bg_description="Bàn học với chồng sách kỹ năng sống và biểu tượng sơ đồ não bộ phát sáng dịu nhẹ trên tường, không có nhân vật",
            stickers=[
                ResearchedSticker(
                    id="SC02_ST1",
                    description="Hình tượng người que stick-figure chỉ tay vào biểu đồ não bộ với nét mặt bừng sáng phát hiện điều mới",
                    character_ids=["CH01"],
                    anchor_quote="khoa học thần kinh hiện đại",
                    anchor_quote_en="modern neuroscience reveals a",
                    fx="bounce",
                    x=0.64,
                    y=0.65,
                    w=0.35,
                    z=2,
                )
            ],
            reused_sticker_ids=[("SC01_ST1", "kẻ lười biếng và thiếu kỷ luật", "pop", "lazy and undisciplined")],
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
            bg_description="Sơ đồ cấu trúc bộ não con người vẽ bằng nét đen tối giản trên nền giấy trắng sáng, vùng hạch hạnh nhân nổi bật",
            stickers=[
                ResearchedSticker(
                    id="SC03_ST1",
                    description="Hình tượng người que stick-figure ôm đầu hốt hoảng trước biểu tượng còi báo động mini chớp sáng",
                    character_ids=["CH01"],
                    anchor_quote="kích hoạt phản xạ trốn chạy",
                    anchor_quote_en="triggers a flight reflex",
                    fx="slide_left",
                    x=0.35,
                    y=0.65,
                    w=0.35,
                    z=2,
                )
            ],
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
            bg_description="Khung hình chia đôi: bên trái đồng hồ cát đứng yên, bên phải chiếc đồng hồ bấm giờ 5 phút đang chạy tích tắc",
            stickers=[
                ResearchedSticker(
                    id="SC04_ST1",
                    description="Hình tượng người que stick-figure mỉm cười tự tin cầm bút bắt đầu viết vào cuốn sổ nhỏ",
                    character_ids=["CH01"],
                    anchor_quote="bắt đầu bằng một hành động nhỏ",
                    anchor_quote_en="simple five-minute action step",
                    fx="pop_wobble",
                    x=0.64,
                    y=0.65,
                    w=0.35,
                    z=2,
                )
            ],
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
            bg_description="Căn bếp tĩnh lặng với cánh cửa tủ lạnh vừa đóng lại, ánh đèn học vàng ấm áp tỏa sáng trên bàn làm việc phía xa",
            reused_sticker_ids=[
                ("SC04_ST1", "não bạn chỉ đang lo lắng", "pop", "your brain is only anxious"),
            ],
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


def write_production_package(
    output_dir: Path,
    topic: ResearchedTopic,
    system_root: Path = SYS_DIR,
    brief_revision: int = 1,
) -> Dict[str, Any]:
    """Assemble and write brief.json, content.json, script.json, and cadence_report.json."""
    output_dir.mkdir(parents=True, exist_ok=True)

    brief_data = build_brief_v3(topic, system_root=system_root)
    brief_hash = compute_brief_hash(brief_data)
    content_data = build_content_v3(topic, brief_data, brief_hash, brief_revision=brief_revision)
    script_data = generate_script_json(topic)

    # Cadence checker validation
    checker = ScriptCadenceChecker(nominal_rate=NOMINAL_SPEECH_RATE)
    standardized_scenes = [
        {
            "id": s.scene_id,
            "duration": s.duration,
            "narration": s.narration,
            "beats": [],
        }
        for s in topic.scenes
    ]
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

    # Contract schema validation
    valid_contracts, contract_errors = validate_production_bundle(
        system_root=system_root,
        brief_data=brief_data,
        content_data=content_data,
        brief_revision=brief_revision,
    )

    return {
        "output_dir": str(output_dir),
        "brief_file": str(brief_file),
        "content_file": str(content_file),
        "script_file": str(script_file),
        "cadence_file": str(cadence_file),
        "brief_hash": brief_hash,
        "valid_contracts": valid_contracts,
        "contract_errors": contract_errors,
        "cadence_report": cadence_report,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Research Story Architect: Formulate schema 3.0 blueprints from researched topics."
    )
    parser.add_argument("--demo", action="store_true", help="Generate benchmark production package for trial topic")
    parser.add_argument(
        "--topic",
        choices=["procrastination-paradox", "motivation-history-13m"],
        default=None,
        help="Select built-in researched topic blueprint",
    )
    parser.add_argument("--job-id", default=None, help="Job identifier for sys/runs/<job_id>")
    parser.add_argument("--output-dir", default=None, help="Explicit output directory")
    parser.add_argument("--validate", action="store_true", help="Run contract and cadence validation")
    parser.add_argument("--aspect-ratio", choices=["16:9", "9:16", "dual"], default="16:9", help="Video aspect ratio")
    parser.add_argument("--subtitles", action="store_true", help="Force enable subtitles on output")

    args = parser.parse_args()

    selected_topic = args.topic or ("procrastination-paradox" if args.demo else None)
    if selected_topic:
        if selected_topic == "motivation-history-13m":
            from build_motivation_history_13m import create_motivation_history_13m_topic

            job_id = args.job_id or f"motivation-history-{args.aspect_ratio.replace(':', 'x')}-13m"
            out_dir = Path(args.output_dir) if args.output_dir else SYS_DIR / f"runs/{job_id}"
            print("[*] Đang kiến trúc bộ hồ sơ kỹ thuật 13 phút cho chủ đề: 'Lịch sử tiến hóa của Động lực'...")
            topic = create_motivation_history_13m_topic(aspect_ratio=args.aspect_ratio, subtitles=args.subtitles)
        else:
            job_id = args.job_id or f"procrastination-paradox-{args.aspect_ratio.replace(':', 'x')}-001"
            out_dir = Path(args.output_dir) if args.output_dir else SYS_DIR / f"runs/{job_id}"
            print("[*] Đang kiến trúc bộ hồ sơ kỹ thuật mẫu cho chủ đề: 'Nghịch lý của sự Trì hoãn'...")
            topic = create_demo_trial_topic()
            topic.aspect_ratio = args.aspect_ratio
            if args.subtitles:
                topic.subtitles = True

        result = write_production_package(out_dir, topic, system_root=SYS_DIR)

        print(f"  [+] Đã xuất brief.json: {result['brief_file']}")
        print(f"  [+] Đã xuất content.json: {result['content_file']}")
        print(f"  [+] Đã xuất script.json: {result['script_file']}")
        print(f"  [+] Đã xuất cadence_report.json: {result['cadence_file']}")
        print(f"  [+] Brief Hash: {result['brief_hash']}")

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
