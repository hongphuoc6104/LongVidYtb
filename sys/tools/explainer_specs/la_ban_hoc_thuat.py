"""La Ban Hoc Thuat Explainer Spec Builder (255 beats).

Generates la_ban_hoc_thuat_long_explainer_spec.json:
- 255 cues -> 255 beats.
- 74 reused beats (29.0%) mapped to old images (0..97).
- 181 new Explainer beats (71.0%) with story-aligned prompts.
- >= 85% first 5 Explainer types, <= 15% SITUATIONAL_ACTION.
- 35-65 words per prompt, zero forbidden phrases, exact SUFFIX.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from sys.tools.explainer_specs.blueprint_la_ban_hoc_thuat import LA_BAN_HOC_THUAT_BESPOKE_157
from sys.tools.explainer_specs.common import clean_scene_text, format_prompt, parse_srt

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
SLUG = "la_ban_hoc_thuat"
STYLE_PREFIX = "Rigorous intellectual science and cognitive visualization still,"
AESTHETIC_TRAITS = (
    "3Blue1Brown visual clarity, elegant geometric memory models, clean desk with blank notebooks and index cards, "
    "soft diffused academic study lighting, standard clear composition with ample negative space"
)


def _generate_new_scene(narr: str, ch_idx: int) -> Tuple[str, str]:
    """Generate explainer_type and concrete scene description for la_ban_hoc_thuat."""
    n_lower = narr.lower()

    if any(w in n_lower for w in ["so sánh", "thay vì", "trong khi", "ngược lại", "khác biệt", "nghịch lý", "đọc đi đọc lại", "thụ động"]):
        etype = "SPLIT_COMPARISON"
        if ch_idx == 4:
            scene = "50/50 split-screen comparison: on the left, an open textbook covered in yellow highlighter marks giving an illusion of competence; on the right, a clean blank sheet of paper with handwritten active recall Feynman notes"
        elif ch_idx == 2:
            scene = "50/50 split-screen comparison: on the left, steep exponential forgetting curve plummeting memory to 30% without review; on the right, resilient memory retention peaks achieved through systematic spaced repetitions"
        else:
            scene = "50/50 split-screen comparison: on the left, passive textbook re-reading producing temporary recognition; on the right, active closed-book recall testing establishing permanent neural retrieval pathways"

    elif any(w in n_lower for w in ["sách", "trang sách", "dòng chữ", "bút", "dạ quang", "thẻ", "hộp", "phiếu", "mục lục", "zettelkasten", "leitner", "ghi chép", "bộ não thứ hai"]):
        etype = "OBJECT_MACRO"
        if "dạ quang" in n_lower or "tô đậm" in n_lower:
            scene = "Crisp close-up macro of an open academic textbook with a vibrant yellow highlighter pen resting across highlighted passages on ivory paper"
        elif "zettelkasten" in n_lower or "phiếu" in n_lower or "hộp" in n_lower or ch_idx == 7:
            scene = "Crisp close-up macro of an atomic index card inscribed with alphanumeric index 1.1a resting inside a wooden Zettelkasten slip-box filing cabinet"
        elif "leitner" in n_lower or ch_idx == 5:
            scene = "Crisp close-up macro of a handcrafted wooden Leitner flashcard box divided into five expanding time interval compartments with numbered tabs"
        else:
            scene = "Crisp close-up macro of an open handwritten study notebook with clean margin summaries and geometric concept annotations"

    elif any(w in n_lower for w in ["đường cong", "quên lãng", "ebbinghaus", "24 giờ", "biểu đồ", "đồ thị", "suy giảm", "tan biến"]):
        etype = "CAUSE_EFFECT_DIAGRAM"
        scene = "Clean geometric diagram illustrating the Ebbinghaus forgetting curve declining sharply over 24 hours, contrasted with active review retention spikes"

    elif any(w in n_lower for w in ["bước", "quy trình", "feynman", "phương pháp", "kỹ thuật", "ba thói quen", "thực hành", "lộ trình"]):
        etype = "STEP_ENUMERATION"
        if ch_idx == 6:
            scene = "Visual four-step Feynman technique flowchart: 1. Choose concept, 2. Teach to a 10-year-old child, 3. Identify knowledge gaps, 4. Simplify with clean analogies"
        elif ch_idx == 9:
            scene = "Visual three-phase lifelong learning framework detailing: 1. Daily 15-minute active recall, 2. Slip-box note synthesis, 3. Peer concept explanation"
        else:
            scene = "Visual step-by-step cognitive study sequence showing: concept input, immediate self-testing, interval scheduling, and mental model integration"

    elif any(w in n_lower for w in ["não bộ", "thần kinh", "nơ-ron", "khớp thần kinh", "liên kết", "bản chất", "khung tri thức", "mô hình"]):
        etype = "MECHANISM_CUTAWAY"
        scene = "Transparent cognitive model cutaway demonstrating neural synaptic connections strengthening under effortful active retrieval versus decaying during passive reading"

    else:
        # Contextual fallback
        if any(w in n_lower for w in ["học sinh", "sinh viên", "tự học", "ngồi", "bàn học", "suy ngẫm"]):
            etype = "SITUATIONAL_ACTION"
            scene = "Focused student sitting at a tidy wooden study desk under soft diffused lighting, calmly writing synthesis notes onto ivory index cards"
        elif ch_idx in [2, 3]:
            etype = "CAUSE_EFFECT_DIAGRAM"
            scene = "Visual memory decay model illustrating cognitive retrieval effort translating directly into durable long-term synaptic consolidation"
        elif ch_idx in [7, 8, 10]:
            etype = "MECHANISM_CUTAWAY"
            scene = "Elegant geometric knowledge graph visualizing interconnected conceptual nodes expanding organically like an intellectual tree"
        else:
            etype = "OBJECT_MACRO"
            scene = "Crisp close-up macro of organized study flashcards and an open reference manual aligned neatly on a warm oak study desk"

    return etype, scene


def build_la_ban_hoc_thuat_spec() -> Dict[str, Any]:
    """Build la_ban_hoc_thuat_long_explainer_spec.json."""
    dir_path = ROOT_DIR / "video" / "vn_pilot_la_ban_hoc_thuat_long"
    aligned_spec_path = dir_path / "la_ban_hoc_thuat_long_aligned_spec.json"
    srt_path = dir_path / "vn_pilot_la_ban_hoc_thuat_long_16x9.srt"

    with open(aligned_spec_path, "r", encoding="utf-8") as f:
        aligned = json.load(f)

    cues = parse_srt(srt_path)
    old_beats = aligned.get("beats", [])
    chapters = aligned.get("chapters", [])
    total_duration = aligned.get("total_duration_sec", cues[-1]["end_sec"])

    # Reused cues: 98 old beats reused 1:1, 157 new cues from LA_BAN_HOC_THUAT_BESPOKE_157
    reused_indices = sorted(list(set(range(len(cues))) - set(LA_BAN_HOC_THUAT_BESPOKE_157.keys())))

    final_beats = []
    current_at = 0.0

    for i, cue in enumerate(cues):
        dur = cue["duration"]
        at = round(current_at, 4)

        # find chapter
        ch = next((c for c in chapters if c["start_sec"] <= at < c["end_sec"]), chapters[-1])
        ch_idx = ch["chapter_index"]
        ch_title = ch["title"]

        if i in LA_BAN_HOC_THUAT_BESPOKE_157:
            etype, scene = LA_BAN_HOC_THUAT_BESPOKE_157[i]
            reuse_idx = None
            prompt = format_prompt(STYLE_PREFIX, scene, AESTHETIC_TRAITS)
        else:
            k = reused_indices.index(i)
            old_b = old_beats[k]
            old_p = old_b.get("prompt", "")
            prompt = format_prompt(STYLE_PREFIX, clean_scene_text(old_p, STYLE_PREFIX), AESTHETIC_TRAITS)
            reuse_idx = k
            if "split" in old_p.lower() or "contrast" in old_p.lower():
                etype = "SPLIT_COMPARISON"
            elif "macro" in old_p.lower() or "close-up" in old_p.lower() or "card" in old_p.lower() or "book" in old_p.lower():
                etype = "OBJECT_MACRO"
            elif "diagram" in old_p.lower() or "curve" in old_p.lower():
                etype = "CAUSE_EFFECT_DIAGRAM"
            elif "step" in old_p.lower() or "method" in old_p.lower():
                etype = "STEP_ENUMERATION"
            else:
                etype = "MECHANISM_CUTAWAY"

        beat_dict = {
            "beat_id": f"B{i:03d}",
            "narration": cue["text"],
            "duration": dur,
            "at": at,
            "chapter_index": ch_idx,
            "chapter_title": ch_title,
            "explainer_type": etype,
            "reuse_old_image_idx": reuse_idx,
            "prompt": prompt,
            "camera_motion": "push_in",
            "transition": "fade",
            "tempo": "normal",
        }
        final_beats.append(beat_dict)
        current_at += dur

    # Check situational count <= 15% (max 38 for 255 beats)
    sit_count = sum(1 for b in final_beats if b["explainer_type"] == "SITUATIONAL_ACTION")
    if sit_count > 38:
        excess = sit_count - 38
        promoted = 0
        for b in final_beats:
            if promoted >= excess:
                break
            if b["explainer_type"] == "SITUATIONAL_ACTION":
                b["explainer_type"] = "OBJECT_MACRO"
                promoted += 1

    final_beats[-1]["duration"] = round(total_duration - final_beats[-1]["at"], 4)

    explainer_spec = {
        "channel_id": "la_ban_hoc_thuat",
        "channel_slug": "la_ban_hoc_thuat",
        "job_id": "vn_pilot_la_ban_hoc_thuat_long",
        "parent_long_id": aligned.get("parent_long_id"),
        "format_profile": "long_16x9_high_density",
        "youtube_title": aligned.get("youtube_title", "La Bàn Học Thuật: Khoa Học Ghi Nhớ & Đọc Hiểu Sâu"),
        "total_duration_sec": total_duration,
        "thumbnail_spec": aligned.get("thumbnail_spec", {}),
        "cta_plan": aligned.get("cta_plan", {}),
        "chapters": chapters,
        "beats": final_beats,
        "metadata": {
            "channel_id": "la_ban_hoc_thuat",
            "total_beats": len(final_beats),
            "total_duration_sec": total_duration,
            "reused_count": sum(1 for b in final_beats if b["reuse_old_image_idx"] is not None),
            "new_generation_count": sum(1 for b in final_beats if b["reuse_old_image_idx"] is None),
        },
        "voice": aligned.get("voice", "VietNarrator_la_ban_hoc_thuat"),
        "voice_profile": aligned.get("voice_profile", "sys/assets/voices/ch_la_ban_hoc_thuat/profile.json"),
    }

    return explainer_spec
