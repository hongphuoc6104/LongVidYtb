#!/usr/bin/env python3
"""Build and validate Batch 3 packages for vu_tru_ti_hon (Vũ Trụ Tí Hon).

Jobs generated:
- sys/runs/vu-tru-ti-hon-batch3-16x9 (Long 16:9)
- sys/runs/vu-tru-ti-hon-batch3-9x16 (Short 9:16 spin-off)

Artifacts per job:
- competitor_research.json
- brief.json
- outline.json
- content.json
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

TOOLS_DIR = SYS_DIR / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from channels.registry import apply_channel, channel_cast, channel_profile_stamp, get_channel
from content.research_story_architect import compute_brief_hash
from tools.cta_tone_linter import count_syllables_whitespace, lint_cta
from tools.editorial_value_linter import lint_editorial_and_narrative_quality
from tools.script_diversity_linter import check_ai_cliche_phrases, check_intra_video_repetitions, lint_script
from visual_pacing import audit_narrative_visual_density


# Common Channel Visual Specifications
CHANNEL_ID = "vu_tru_ti_hon"
ch = get_channel(CHANNEL_ID)

CH01_DEF = {
    "id": "CH01",
    "name": "Người kể chuyện bầu trời đêm theo tinh thần Feynman đầy tò mò",
    "appearance": "Adorable compact spherical robotic space-probe mascot Tí Hon with a glowing cyan visor eye and tiny thruster wings floating beside vibrant geometric planets. Seamless white and polished gold chassis plating with glowing pulsar-cyan optic lens visor, no human clothes.",
    "outfit": "Seamless white and polished gold chassis plating with glowing pulsar-cyan optic lens visor, no human clothes",
}

PRESERVE_VECTOR_STYLE = (
    "crisp rounded vector shapes on deep cosmic indigo canvas #0B1026, vibrant geometric celestial palette "
    "(#4CC9F0, #FF6B6B, #FFD166, #7209B7), robotic probe mascot Tí Hon with glowing cyan visor eye, "
    "zero black outlines, zero 3D, zero gradients"
)

MOTION_SUFFIX = "silent visual storytelling, no talking, no lip movement"


def make_image_obj(
    img_id: str,
    desc: str,
    change: str,
    narr_quote: str,
    situation: str,
    tempo: str,
    emphasis_text: str | None = None,
    shot_type: str = "full_scene",
    motion_action: str = "",
) -> Dict[str, Any]:
    vis_text = []
    if emphasis_text:
        vis_text.append({
            "text": emphasis_text,
            "placement": "upper_third",
            "object": "emphasis",
        })

    m_prompt = (
        f"Smooth 2D geometric space vector explainer animation in Kurzgesagt style. {motion_action.strip()} "
        f"transitioning smoothly into the next frame, {MOTION_SUFFIX}"
    )

    return {
        "id": img_id,
        "description": desc,
        "character_ids": ["CH01"],
        "based_on": None,
        "preserve": PRESERVE_VECTOR_STYLE,
        "change": change,
        "reason": f"Narration-locked full-frame beat {img_id}.",
        "visible_text": vis_text,
        "kind": "scene",
        "shot_type": shot_type,
        "tempo": tempo,
        "narrative_situation": situation,
        "emphasis_text": emphasis_text or "",
        "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
        "has_character": True,
        "explanation": {
            "quote": narr_quote[:35],
            "relation": "context",
            "source_terms": ["vũ trụ", "ánh sáng"],
            "visual_terms": ["vector", "mascot", "stars"],
        },
        "motion_prompt": m_prompt,
    }


def make_beat_obj(
    beat_id: str,
    img_id: str,
    purpose: str,
    narr_quote: str,
    situation: str,
    tempo: str,
    effect: str = "cut",
    is_endcard: bool = False,
    camera_intent: str = "reveal",
) -> Dict[str, Any]:
    b: Dict[str, Any] = {
        "id": beat_id,
        "image_id": img_id,
        "purpose": purpose,
        "anchor": {
            "vi": {
                "quote": narr_quote,
                "occurrence": 1,
            }
        },
        "effect": effect,
        "focus": {"x": 0.5, "y": 0.5 if is_endcard else 0.0},
        "tempo": tempo,
        "narrative_situation": situation,
        "camera_intent": camera_intent,
    }
    if is_endcard:
        b["is_endcard"] = True
    return b


def build_short_9x16() -> tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    job_id = "vu-tru-ti-hon-batch3-9x16"
    parent_long_id = "vu-tru-ti-hon-batch3-16x9"
    topic = "Có Hàng Tỷ Ngôi Sao Nhưng Vì Sao Bầu Trời Đêm Vẫn Tối Đen?"
    youtube_title = "Có Hàng Tỷ Ngôi Sao Nhưng Bầu Trời Đêm Vẫn Tối Đen?"  # 51 chars <= 55

    # 1. Competitor Research
    cr = {
        "channel_id": CHANNEL_ID,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Kurzgesagt – In a Nutshell",
                    "top_performing_videos": [
                        {
                            "title": "Why The Night Sky Is Dark (Olbers' Paradox)",
                            "views": "14M views",
                            "hook_technique": "Đặt câu hỏi phản trực giác: nếu vũ trụ vô tận các ngôi sao, tại sao bầu trời đêm lại đen ngòm?",
                            "pacing_structure": "Mô hình rừng cây vô tận -> Tốc độ ánh sáng hữu hạn -> Sự giãn nở của không-thời gian.",
                            "retention_driver": "Cảm giác khai sáng khi nhận ra màn đêm chính là bằng chứng cho sự khởi đầu của vũ trụ.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Dùng ẩn dụ thị giác Feynman: khu rừng cây bạt ngàn che khuất tầm nhìn.",
                        "Đồ họa vector không gian rực rỡ trên nền canvas xanh chàm huyền bí.",
                    ],
                },
                {
                    "channel_name": "MinutePhysics",
                    "top_performing_videos": [
                        {
                            "title": "Why is it Dark at Night?",
                            "views": "7.8M views",
                            "hook_technique": "Phác họa hình học vỏ cầu chứng minh tổng năng lượng ánh sáng không hề suy giảm theo khoảng cách.",
                            "pacing_structure": "Bác bỏ giả thuyết bụi vũ trụ -> Giới thiệu tuổi hữu hạn của vũ trụ -> Bức xạ nền vi ba.",
                            "retention_driver": "Cách giải thích ngắn gọn, súc tích, đập tan các ngộ nhận trực giác.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Nhịp giải thích nhanh, chuyển cảnh dứt khoát mỗi khi đưa ra một bằng chứng vật lý.",
                        "Đưa ra cú lật bàn ấn tượng: bầu trời thực chất đang rực sáng trong bước sóng vi ba.",
                    ],
                },
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Vòm trời ngập tràn vô số thiên hà rực rỡ đối lập với đôi mắt nhìn vào màn đêm đen sâu thẳm.",
                "counter_intuitive_truth_slap": "Màn đêm không phải khoảng trống im lìm mà là bằng chứng sống cho thấy vũ trụ có ngày sinh ra.",
            },
            "narrative_progression_arc": [
                {
                    "phase": "lived_friction",
                    "purpose": "Đặt câu hỏi ngây thơ chạm tới bản chất thực tại về màn đêm đen.",
                },
                {
                    "phase": "empirical_conflict",
                    "purpose": "Ẩn dụ rừng cây vô tận của Heinrich Olbers bóc tách nghịch lý hình học.",
                },
                {
                    "phase": "structural_model",
                    "purpose": "Hé lộ hai chìa khóa vật lý: tuổi đời hữu hạn và vũ trụ giãn nở.",
                },
                {
                    "phase": "actionable_resolution",
                    "purpose": "Đỉnh cao trào bỏ lửng về tương lai vũ trụ và chuyển phễu sang bản đầy đủ.",
                },
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Sequential daisy-chain linking Start Frame to End Frame across all cosmic vector scenes.",
            },
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
            "myth_debunked": "Bầu trời đêm tối đen vì các ngôi sao ở quá xa hoặc bụi không gian che khuất hết ánh sáng.",
            "channel_verdict": "Màn đêm đen thực chất là bằng chứng sống động nhất cho thấy vũ trụ có điểm khởi đầu hữu hạn và không gian đang không ngừng giãn nở.",
            "actionable_rule_of_thumb": "Mô hình khu rừng cây Feynman: muốn thấy khoảng trống giữa rừng rậm rạp thì khu rừng phải có ranh giới hoặc cây cối vừa mới được gieo trồng.",
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "Nhưng nếu vũ trụ tiếp tục giãn nở, bầu trời tương lai sẽ biến mất hoàn toàn?",
            "bridge": "Hành trình giải mã trọn vẹn được robot Tí Hon kể trên kênh Vũ Trụ Tí Hon.",
            "close": "Lưu video lại để ngắm sao đêm nay. Bí ẩn vũ trụ nào làm bạn tò mò nhất?",
            "endcard_text": "VŨ TRỤ TÍ HON",
        },
    }

    # 2. Brief
    raw_brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": "Người yêu khoa học vũ trụ, sinh viên và khán giả tò mò về các câu hỏi lớn của thực tại",
        "goal": "Giải thích nghịch lý Olbers một cách trực quan, bóc trần ngộ nhận về màn đêm và dẫn phễu về video dài 16:9",
        "video_type": "explainer",
        "duration": {
            "min_seconds": 40.0,
            "max_seconds": 55.0,
        },
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Cú sốc nghịch lý bầu trời đêm rực sáng"},
            {"id": "R02", "text": "Giả thuyết rừng cây vô tận của Heinrich Olbers"},
            {"id": "R03", "text": "Lời giải vũ trụ hữu hạn và ánh sáng chưa kịp tới"},
            {"id": "R04", "text": "Cơ chế không gian giãn nở kéo dãn sóng ánh sáng"},
            {"id": "R05", "text": "Đỉnh cao trào bỏ lửng và chuyển phễu sang bản dài"},
        ],
        "language": "vi",
        "tone": "Kinh ngạc, giàu hình ảnh ẩn dụ, chuẩn xác vật lý nhưng bình dị",
        "style": ch.visual.style_description,
        "aspect_ratio": "9:16",
        "format_profile": "short_9x16",
        "parent_long_id": parent_long_id,
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Olbers' Paradox and the Finite Age of the Universe",
                "reference": "Harrison, E. (1987). Darkness at Night: A Riddle of the Universe. Harvard University Press.",
                "facts": [
                    "Vũ trụ có tuổi đời khoảng 13.8 tỷ năm.",
                    "Hiệu ứng Doppler và sự giãn nở không gian kéo dãn ánh sáng thành bức xạ vi ba.",
                ],
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "9:16",
                "language": "vi",
                "subtitles": True,
                "voice": "VietNarrator",
                "speed": 1.0,
            }
        ],
        "planning": {
            "success_criteria": [
                "Giải thích nghịch lý Olbers trong 5 cảnh chặt chẽ",
                "Visual density cao với 20 ảnh vector độc bản cho 20 beats",
                "Thời lượng giữ ảnh trung bình <= 2.3 giây (~170 từ)",
            ],
            "avoid": [
                "Không dùng công thức toán phức tạp làm nản lòng người xem",
                "Không dùng các câu từ sáo rỗng hay văn mẫu AI",
            ],
            "prior_knowledge": "Không đòi hỏi kiến thức chuyên sâu.",
            "pacing": "Nhanh, dồn dập ở phần mở đầu và chậm lại ở phần bình luận thị giác.",
            "domain_requirements": ["Tuân thủ phong cách hình học Kurzgesagt và mascot Tí Hon"],
            "assumptions": ["Mỗi beat có thời lượng phù hợp với ngữ điệu tự nhiên của VietNarrator"],
            "text_style": {
                "font": "geometric sans-serif",
                "color": "#4CC9F0",
                "outline": "none",
                "size": "rõ nét trên màn hình dọc",
                "placement": "upper_third",
            },
            "speech_rates": {
                "vi": {"units_per_second": 3.8, "uncertainty": 0.15, "source": "Calibrated VietNarrator"},
                "en": {"units_per_second": 2.5, "uncertainty": 0.25, "source": "Estimated English"},
            },
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Robot thám hiểm Tí Hon bay giữa bầu trời đêm sâu thẳm tỏa ánh sáng xanh cyan đối lập với vô số vì sao hình học rực rỡ",
                "text_overlay": "SAO ĐÊM TỐI ĐEN",
                "contrast_pair": "Hàng tỷ ngôi sao rực rỡ vs Bầu trời đêm đen đặc",
                "thumbnail_prompt": (
                    "Luminous Kurzgesagt-inspired 2D flat geometric space vector illustration on deep cosmic indigo canvas #0B1026. "
                    "The adorable spherical robotic space-probe mascot Tí Hon with glowing cyan visor eye floats in awe. "
                    "In the upper third, large bold hand-lettered text reads 'SAO ĐÊM TỐI ĐEN'. Radiant geometric stars and nebulae "
                    "in pulsar cyan #4CC9F0, supernova coral #FF6B6B, starlight gold #FFD166, and nebula violet #7209B7 against deep space. "
                    "Orthographic 2D, at least 60% negative space, zero 3D, zero gradients, crisp rounded shapes."
                ),
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": [
                "vutrutihon",
                "thienvanhoc",
                "vatly",
                "khoahocvutru",
                "kienthuc",
                "olbersparadox",
                "nghichlyolbers",
                "shorts",
            ],
            "cta_plan": {
                "cliffhanger_peak": "Nhưng nếu vũ trụ tiếp tục giãn nở, bầu trời tương lai sẽ biến mất hoàn toàn?",
                "bridge": "Hành trình giải mã trọn vẹn được robot Tí Hon kể trên kênh Vũ Trụ Tí Hon.",
                "close": "Lưu video lại để ngắm sao đêm nay. Bí ẩn vũ trụ nào làm bạn tò mò nhất?",
                "endcard_text": "VŨ TRỤ TÍ HON",
            },
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Robot thám hiểm Tí Hon bay giữa bầu trời đêm sâu thẳm tỏa ánh sáng xanh cyan đối lập với vô số vì sao hình học rực rỡ",
            "text_overlay": "SAO ĐÊM TỐI ĐEN",
            "contrast_pair": "Hàng tỷ ngôi sao rực rỡ vs Bầu trời đêm đen đặc",
            "thumbnail_prompt": (
                "Luminous Kurzgesagt-inspired 2D flat geometric space vector illustration on deep cosmic indigo canvas #0B1026. "
                "The adorable spherical robotic space-probe mascot Tí Hon with glowing cyan visor eye floats in awe. "
                "In the upper third, large bold hand-lettered text reads 'SAO ĐÊM TỐI ĐEN'. Radiant geometric stars and nebulae "
                "in pulsar cyan #4CC9F0, supernova coral #FF6B6B, starlight gold #FFD166, and nebula violet #7209B7 against deep space. "
                "Orthographic 2D, at least 60% negative space, zero 3D, zero gradients, crisp rounded shapes."
            ),
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": [
            "vutrutihon",
            "thienvanhoc",
            "vatly",
            "khoahocvutru",
            "kienthuc",
            "olbersparadox",
            "nghichlyolbers",
            "shorts",
        ],
        "cta_plan": {
            "cliffhanger_peak": "Nhưng nếu vũ trụ tiếp tục giãn nở, bầu trời tương lai sẽ biến mất hoàn toàn?",
            "bridge": "Hành trình giải mã trọn vẹn được robot Tí Hon kể trên kênh Vũ Trụ Tí Hon.",
            "close": "Lưu video lại để ngắm sao đêm nay. Bí ẩn vũ trụ nào làm bạn tò mò nhất?",
            "endcard_text": "VŨ TRỤ TÍ HON",
        },
        "editorial_stance": {
            "myth_debunked": "Bầu trời đêm tối đen vì khoảng cách giữa các ngôi sao quá xa hoặc bụi không gian che khuất hết ánh sáng.",
            "channel_verdict": "Màn đêm thực chất là bằng chứng sống động nhất cho thấy vũ trụ có điểm khởi đầu hữu hạn và không gian đang không ngừng giãn nở.",
            "why_generic_advice_fails": "Cách giải thích thông thường đổ lỗi cho bụi vũ trụ phạm sai lầm nghiêm trọng về định luật nhiệt động lực học vì bụi bị đốt nóng sẽ tự phát sáng.",
            "tradeoff_or_blindspot": "Chấp nhận vũ trụ giãn nở đồng nghĩa thừa nhận một tương lai xa xôi khi mọi thiên hà xa xăm trôi khỏi tầm mắt và bầu trời đêm sẽ hoàn toàn nguội lạnh.",
        },
        "actionable_value": {
            "core_mechanism": "Hai yếu tố triệt tiêu nghịch lý Olbers gồm tuổi hữu hạn mười bốn tỷ năm của vũ trụ và hiệu ứng dịch chuyển đỏ kéo dãn sóng ánh sáng khả kiến thành vi ba vô hình.",
            "practical_rule_of_thumb": "Mô hình khu rừng cây Feynman: muốn thấy khoảng trống giữa rừng cây rậm rạp thì khu rừng phải có ranh giới hoặc cây cối vừa mới được gieo trồng chưa lâu.",
            "real_world_scenario": "Ngước nhìn bầu trời đêm mùa hạ, nhận diện màn đêm đen không phải là khoảng trống chết chóc mà là tấm màn che của bức xạ nền vi ba từ thuở sơ khai.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }
    brief = apply_channel(raw_brief, CHANNEL_ID)

    # 3. Outline
    outline = {
        "outline": [
            {
                "scene_id": "SC01",
                "purpose": "Triển khai bước 1: cú sốc nghịch lý bầu trời đêm rực sáng",
                "requirements": ["R01"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
            {
                "scene_id": "SC02",
                "purpose": "Triển khai bước 2: giả thuyết rừng cây vô tận của Heinrich Olbers",
                "requirements": ["R02"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
            {
                "scene_id": "SC03",
                "purpose": "Triển khai bước 3: lời giải vũ trụ hữu hạn và ánh sáng chưa kịp tới",
                "requirements": ["R03"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
            {
                "scene_id": "SC04",
                "purpose": "Triển khai bước 4: cơ chế không gian giãn nở kéo dãn sóng ánh sáng",
                "requirements": ["R04"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
            {
                "scene_id": "SC05",
                "purpose": "Triển khai bước 5: đỉnh cao trào bỏ lửng và chuyển phễu sang bản dài",
                "requirements": ["R05"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
        ]
    }

    # 4. Content Scenes and Beats (20 beats, 20 unique images, exactly 170 words)
    scenes: List[Dict[str, Any]] = [
        # Scene 1: Hook Shock (4 beats, 4 images, 28 words)
        {
            "id": "SC01",
            "title": "Cú sốc nghịch lý bầu trời đêm rực sáng",
            "purpose": "Triển khai bước 1: cú sốc nghịch lý bầu trời đêm rực sáng",
            "action": "Robot Tí Hon bay lơ lửng ngước nhìn vòm trời đêm đầy sao lấp lánh rồi phóng to mô hình hình học tia sáng.",
            "setting": "Không gian vũ trụ sâu thẳm màu xanh chàm #0B1026 với các vì sao hình học rực rỡ và dải ngân hà vector.",
            "camera": "Mở rộng góc nhìn toàn cảnh từ Trái Đất hướng về vô tận các vì sao.",
            "narration": "Nếu vũ trụ chứa trăm tỷ thiên hà, sao màn đêm lại tối đen? Theo hình học, mắt bạn nhìn hướng nào cũng chạm vào một ngôi sao rực sáng.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "narrative_situation": "hook_shock",
            "narrative_phase": "hook",
            "tone": "Kinh ngạc, dồn dập",
            "layers": [],
            "beats": [
                make_beat_obj(
                    "SC01_B1", "SC01_I1", "Cú sốc số lượng thiên hà khổng lồ",
                    "Nếu vũ trụ chứa trăm tỷ thiên hà,", "hook_shock", "burst"
                ),
                make_beat_obj(
                    "SC01_B2", "SC01_I2", "Câu hỏi phản trực giác về màn đêm đen",
                    "sao màn đêm lại tối đen?", "hook_shock", "fast"
                ),
                make_beat_obj(
                    "SC01_B3", "SC01_I3", "Lập luận hình học cơ bản của các tia nhìn",
                    "Theo hình học,", "hook_shock", "burst"
                ),
                make_beat_obj(
                    "SC01_B4", "SC01_I4", "Tia nhìn bắt buộc chạm vào ngôi sao rực rỡ",
                    "mắt bạn nhìn hướng nào cũng chạm vào một ngôi sao rực sáng.", "hook_shock", "fast"
                ),
            ],
            "images": [
                make_image_obj(
                    "SC01_I1",
                    "The adorable spherical robotic space-probe Tí Hon with a glowing pulsar-cyan visor eye floats in awe on a deep cosmic indigo canvas #0B1026, surrounded by hundreds of colorful geometric galaxies and glowing celestial nebulae.",
                    "Tí Hon hovers beside radiant geometric galaxies and sparkling star clusters",
                    "Nếu vũ trụ chứa trăm tỷ thiên hà,", "hook_shock", "burst",
                    emphasis_text="BẦU TRỜI TỐI ĐEN",
                    motion_action="Tí Hon turns smoothly toward the cosmic expanse as radiant geometric spiral galaxies pulse with vibrant cyan and gold light,",
                ),
                make_image_obj(
                    "SC01_I2",
                    "Mascot probe Tí Hon looking up in curiosity at a pitch-black cosmic void contrasting with a cluster of bright geometric stars on deep indigo canvas #0B1026, orthographic 2D vector style.",
                    "Tí Hon tilts its visor eye upward toward an intriguing empty dark sector of space",
                    "sao màn đêm lại tối đen?", "hook_shock", "fast",
                    motion_action="Tí Hon pulses its visor eye with glowing cyan light while scanning the dark cosmic sector,",
                ),
                make_image_obj(
                    "SC01_I3",
                    "A clean geometric vector diagram showing visual sightlines extending outward from an observer icon toward spherical stars on deep cosmic indigo background #0B1026.",
                    "Crisp vector sightline rays expand outward through concentric geometric star shells",
                    "Theo hình học,", "hook_shock", "burst",
                    motion_action="Geometric sightline rays beam outward through concentric circular orbital rings,",
                ),
                make_image_obj(
                    "SC01_I4",
                    "Mascot probe Tí Hon floating beside a brilliant golden geometric star #FFD166 whose warm vector rays illuminate every sightline in the frame without any shadow.",
                    "Every sightline terminates at the surface of a radiant golden star disk",
                    "mắt bạn nhìn hướng nào cũng chạm vào một ngôi sao rực sáng.", "hook_shock", "fast",
                    motion_action="The golden star glows brightly with expanding vector rings as Tí Hon raises its miniature wings,",
                ),
            ],
        },

        # Scene 2: Olbers Model (4 beats, 4 images, 30 words)
        {
            "id": "SC02",
            "title": "Giả thuyết rừng cây vô tận của Heinrich Olbers",
            "purpose": "Triển khai bước 2: giả thuyết rừng cây vô tận của Heinrich Olbers",
            "action": "Mascot Tí Hon chiếu lăng kính vector biến không gian thành một khu rừng cây hình học bạt ngàn.",
            "setting": "Khu rừng hình học ẩn dụ với các thân cây vector màu chàm đậm và lá cây dạ quang phát sáng.",
            "camera": "Góc nhìn phối cảnh người đi trong rừng cây rậm rạp.",
            "narration": "Năm 1823, Olbers ví không gian như khu rừng vô tận. Đi giữa ngàn cây rậm rạp, bạn chỉ thấy thân gỗ chắn kín tầm mắt không còn kẽ hở.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "narrative_situation": "before_after_contrast",
            "narrative_phase": "empirical_conflict",
            "tone": "Trực quan, giải thích ẩn dụ",
            "layers": [],
            "beats": [
                make_beat_obj(
                    "SC02_B1", "SC02_I1", "Nhà thiên văn Heinrich Olbers nêu nghịch lý",
                    "Năm 1823, Olbers ví không gian", "before_after_contrast", "fast"
                ),
                make_beat_obj(
                    "SC02_B2", "SC02_I2", "Ẩn dụ khu rừng cây bạt ngàn vô tận",
                    "như khu rừng vô tận.", "before_after_contrast", "normal"
                ),
                make_beat_obj(
                    "SC02_B3", "SC02_I3", "Trải nghiệm đi giữa ngàn cây rậm rạp",
                    "Đi giữa ngàn cây rậm rạp,", "before_after_contrast", "fast"
                ),
                make_beat_obj(
                    "SC02_B4", "SC02_I4", "Thân gỗ chắn kín tầm nhìn không còn khoảng trống",
                    "bạn chỉ thấy thân gỗ chắn kín tầm mắt không còn kẽ hở.", "before_after_contrast", "normal"
                ),
            ],
            "images": [
                make_image_obj(
                    "SC02_I1",
                    "Mascot Tí Hon projecting a luminous holographic scroll showing astronomer Heinrich Olbers' portrait in crisp flat vector lines on deep indigo canvas #0B1026.",
                    "Tí Hon projects a glowing cyan holographic timeline marker for year 1823",
                    "Năm 1823, Olbers ví không gian", "before_after_contrast", "fast",
                    motion_action="Tí Hon hovers forward as a holographic year 1823 badge manifests with gentle rotational glow,",
                ),
                make_image_obj(
                    "SC02_I2",
                    "A stylized 2D geometric forest of stylized flat tree trunks in deep violet #7209B7 and pulsar cyan #4CC9F0 spreading into infinity on dark canvas #0B1026, mascot Tí Hon flying above.",
                    "Geometric stylized tree trunks multiply across an infinite orthographic grid",
                    "như khu rừng vô tận.", "before_after_contrast", "normal",
                    emphasis_text="RỪNG CÂY VÔ TẬN",
                    motion_action="Rows of geometric tree trunks pan gently sideways revealing layered depth across the indigo plane,",
                ),
                make_image_obj(
                    "SC02_I3",
                    "First-person orthographic perspective standing inside the dense geometric forest, where vibrant tree trunks overlap seamlessly, Tí Hon guiding with cyan headlight beam.",
                    "Dense tree trunks overlap tightly in the foreground and background",
                    "Đi giữa ngàn cây rậm rạp,", "before_after_contrast", "fast",
                    motion_action="The camera glides forward through overlapping geometric tree trunks with crisp parallax motion,",
                ),
                make_image_obj(
                    "SC02_I4",
                    "A solid wall of overlapping tree trunks leaving zero empty space in the visual field, symbolizing blocked sightlines, flat 2D vector style on #0B1026 background.",
                    "Zero gap remains as overlapping vector tree trunks completely block the horizon",
                    "bạn chỉ thấy thân gỗ chắn kín tầm mắt không còn kẽ hở.", "before_after_contrast", "normal",
                    motion_action="The tree trunks lock into a solid geometric pattern leaving zero gaps across the frame,",
                ),
            ],
        },

        # Scene 3: Editorial Commentary (4 beats, 4 images, 32 words)
        {
            "id": "SC03",
            "title": "Lời giải vũ trụ hữu hạn và ánh sáng chưa kịp tới",
            "purpose": "Triển khai bước 3: lời giải vũ trụ hữu hạn và ánh sáng chưa kịp tới",
            "action": "Tí Hon dừng lại giữa không gian, mở ra cánh cổng thời gian hiển thị điểm bắt đầu Big Bang.",
            "setting": "Mô hình bong bóng không-thời gian hình học với đồng hồ đếm ngược từ Big Bang trên nền #0B1026.",
            "camera": "Quay chậm tĩnh tại tập trung vào sự suy ngẫm của mascot.",
            "narration": "Lời giải thật bất ngờ: vũ trụ không hề tồn tại vĩnh hằng. Không gian khởi đầu mười bốn tỷ năm trước, nên ánh sáng phương xa chưa kịp tới Trái Đất.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "narrative_situation": "editorial_commentary",
            "narrative_phase": "structural_model",
            "tone": "Sâu sắc, kinh ngạc, trầm lắng",
            "layers": [],
            "beats": [
                make_beat_obj(
                    "SC03_B1", "SC03_I1", "Cú lật mở tư duy về bản chất vũ trụ",
                    "Lời giải thật bất ngờ:", "editorial_commentary", "slow"
                ),
                make_beat_obj(
                    "SC03_B2", "SC03_I2", "Bác bỏ quan niệm vũ trụ vĩnh hằng",
                    "vũ trụ không hề tồn tại vĩnh hằng.", "editorial_commentary", "slow"
                ),
                make_beat_obj(
                    "SC03_B3", "SC03_I3", "Cột mốc mười bốn tỷ năm Big Bang",
                    "Không gian khởi đầu mười bốn tỷ năm trước,", "editorial_commentary", "normal"
                ),
                make_beat_obj(
                    "SC03_B4", "SC03_I4", "Ánh sáng phương xa chưa đủ thời gian tới nơi",
                    "nên ánh sáng phương xa chưa kịp tới Trái Đất.", "editorial_commentary", "slow"
                ),
            ],
            "images": [
                make_image_obj(
                    "SC03_I1",
                    "Mascot Tí Hon in deep contemplation, floating in front of an expanding geometric bubble of light on solid deep cosmic indigo #0B1026, orthographic flat vector art.",
                    "Tí Hon pauses in quiet contemplation before a glowing cosmic time portal",
                    "Lời giải thật bất ngờ:", "editorial_commentary", "slow",
                    motion_action="Tí Hon tilts gently with thruster wings hovering as a soft ripple of pulsar-cyan light radiates outwards,",
                ),
                make_image_obj(
                    "SC03_I2",
                    "A minimalist geometric hourglass shattered into glowing vector stardust, symbolizing the finite nature of cosmic time, flat 2D Kurzgesagt aesthetic.",
                    "A stylized vector hourglass dissolves into radiant starlight gold particles",
                    "vũ trụ không hề tồn tại vĩnh hằng.", "editorial_commentary", "slow",
                    emphasis_text="VŨ TRỤ HỮU HẠN",
                    motion_action="The geometric hourglass softly dissolves into glowing golden sparks floating across the dark canvas,",
                ),
                make_image_obj(
                    "SC03_I3",
                    "A radiant singularity point bursting into an expanding geometric sphere labeled 13.8 billion years on deep indigo canvas #0B1026, mascot Tí Hon observing from the side.",
                    "A compact singularity expands into colorful concentric celestial rings",
                    "Không gian khởi đầu mười bốn tỷ năm trước,", "editorial_commentary", "normal",
                    motion_action="Concentric rings of supernova coral #FF6B6B and cyan #4CC9F0 pulse outward from the singularity point,",
                ),
                make_image_obj(
                    "SC03_I4",
                    "A beam of light represented as discrete golden vector arrows traveling toward Earth icon, stopped at a distant cosmic horizon boundary line on #0B1026 background.",
                    "Golden vector photon packets travel along a path still far from reaching Earth",
                    "nên ánh sáng phương xa chưa kịp tới Trái Đất.", "editorial_commentary", "slow",
                    motion_action="A stream of glowing golden photons glides smoothly along a dotted vector trajectory line,",
                ),
            ],
        },

        # Scene 4: Mechanism Step (4 beats, 4 images, 28 words)
        {
            "id": "SC04",
            "title": "Cơ chế không gian giãn nở kéo dãn sóng ánh sáng",
            "purpose": "Triển khai bước 4: cơ chế không gian giãn nở kéo dãn sóng ánh sáng",
            "action": "Tí Hon kéo dãn một tấm lưới không-thời gian hình học, làm sóng ánh sáng chuyển từ vàng sang đỏ và hồng ngoại.",
            "setting": "Lưới tọa độ vũ trụ co giãn với các bước sóng hình sin màu sắc rực rỡ trên nền #0B1026.",
            "camera": "Cận cảnh vào bước sóng ánh sáng bị kéo dài.",
            "narration": "Mặt khác, không gian đang giãn nở cực nhanh. Ánh sáng bị kéo dãn thành hồng ngoại, biến màn đêm thành vòm sóng vi ba mắt không thấy.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "narrative_situation": "mechanism_step",
            "narrative_phase": "causal_mechanism",
            "tone": "Khoa học, sống động, giàu cơ chế",
            "layers": [],
            "beats": [
                make_beat_obj(
                    "SC04_B1", "SC04_I1", "Tốc độ giãn nở vũ trụ chóng mặt",
                    "Mặt khác, không gian đang giãn nở cực nhanh.", "mechanism_step", "normal"
                ),
                make_beat_obj(
                    "SC04_B2", "SC04_I2", "Sóng ánh sáng bị kéo dãn thành tia hồng ngoại",
                    "Ánh sáng bị kéo dãn thành hồng ngoại,", "mechanism_step", "fast"
                ),
                make_beat_obj(
                    "SC04_B3", "SC04_I3", "Bầu trời thực ra rực sáng trong phổ vi ba",
                    "biến màn đêm thành vòm sóng vi ba", "mechanism_step", "normal"
                ),
                make_beat_obj(
                    "SC04_B4", "SC04_I4", "Giới hạn sinh học của đôi mắt người",
                    "mắt không thấy.", "mechanism_step", "fast"
                ),
            ],
            "images": [
                make_image_obj(
                    "SC04_I1",
                    "Mascot Tí Hon pulling a flexible glowing cyan coordinate spacetime grid #4CC9F0, demonstrating cosmic expansion on deep indigo canvas #0B1026.",
                    "Tí Hon demonstrates the stretching spacetime grid with expanding coordinate squares",
                    "Mặt khác, không gian đang giãn nở cực nhanh.", "mechanism_step", "normal",
                    motion_action="The cyan vector grid smoothly expands outwards in all directions with fluid geometric motion,",
                ),
                make_image_obj(
                    "SC04_I2",
                    "A vibrant sine wave transitioning from compressed starlight gold #FFD166 to elongated deep coral red #FF6B6B waves, symbolizing cosmological redshift.",
                    "Sine wave crests stretch wider apart as the wave transitions from gold to coral red",
                    "Ánh sáng bị kéo dãn thành hồng ngoại,", "mechanism_step", "fast",
                    motion_action="The golden sine wave stretches dynamically into a wide coral-red wavelength across the screen,",
                ),
                make_image_obj(
                    "SC04_I3",
                    "The entire night sky transformed into an intricate glowing geometric mosaic of Cosmic Microwave Background heat map colors on #0B1026 canvas, Tí Hon floating in the center.",
                    "A full-frame radiant geometric CMB thermal mosaic illuminates the entire sky",
                    "biến màn đêm thành vòm sóng vi ba", "mechanism_step", "normal",
                    emphasis_text="DỊCH CHUYỂN ĐỎ",
                    motion_action="The dark sky illuminates with soft pulsing micro-geometric tiles of cyan, violet and coral,",
                ),
                make_image_obj(
                    "SC04_I4",
                    "A stylized human eye graphic with vector optical lenses, showing visible light passing through while microwave wavelengths wash harmlessly around it on deep indigo #0B1026.",
                    "Stylized vector eye diagram showing invisible long wavelengths bypassing sensory receptors",
                    "mắt không thấy.", "mechanism_step", "fast",
                    motion_action="Long gentle vector waves glide harmlessly past the sleek geometric eye silhouette,",
                ),
            ],
        },

        # Scene 5: Peak Cliffhanger & CTA (4 beats, 4 images, 52 words)
        {
            "id": "SC05",
            "title": "Đỉnh cao trào bỏ lửng và chuyển phễu sang bản dài",
            "purpose": "Triển khai bước 5: đỉnh cao trào bỏ lửng và chuyển phễu sang bản dài",
            "action": "Tí Hon chỉ tay vào bản đồ vũ trụ tương lai và mời gọi người xem cùng bước vào hành trình bản dài.",
            "setting": "Cổng thông tin vũ trụ tương lai rực rỡ với logo kênh Vũ Trụ Tí Hon trên nền #0B1026.",
            "camera": "Lùi dần về góc nhìn toàn cảnh với endcard nổi bật.",
            "narration": "Nhưng nếu vũ trụ tiếp tục giãn nở, bầu trời tương lai sẽ biến mất hoàn toàn? Hành trình giải mã trọn vẹn được robot Tí Hon kể trên kênh Vũ Trụ Tí Hon. Lưu video lại để ngắm sao đêm nay. Bí ẩn vũ trụ nào làm bạn tò mò nhất?",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "narrative_situation": "cliffhanger_peak",
            "narrative_phase": "actionable_resolution",
            "tone": "Hào hứng, kích thích tò mò, gắn kết",
            "layers": [],
            "beats": [
                make_beat_obj(
                    "SC05_B1", "SC05_I1", "Câu hỏi đỉnh cao trào về tương lai vũ trụ",
                    "Nhưng nếu vũ trụ tiếp tục giãn nở,", "cliffhanger_peak", "fast"
                ),
                make_beat_obj(
                    "SC05_B2", "SC05_I2", "Bầu trời đêm tương lai biến mất hoàn toàn",
                    "bầu trời tương lai sẽ biến mất hoàn toàn?", "cliffhanger_peak", "fast"
                ),
                make_beat_obj(
                    "SC05_B3", "SC05_I3", "Cầu nối phễu dẫn sang video dài 16:9",
                    "Hành trình giải mã trọn vẹn được robot Tí Hon kể trên kênh Vũ Trụ Tí Hon.", "cta_bridge", "normal"
                ),
                make_beat_obj(
                    "SC05_B4", "SC05_I4", "Lời chào kết thúc và câu hỏi thảo luận",
                    "Lưu video lại để ngắm sao đêm nay. Bí ẩn vũ trụ nào làm bạn tò mò nhất?", "cta_close", "hold",
                    effect="hold", is_endcard=True
                ),
            ],
            "images": [
                make_image_obj(
                    "SC05_I1",
                    "Mascot Tí Hon looking ahead toward an enigmatic cosmic horizon where distant galaxies are slowly fading beyond reach, on deep cosmic indigo #0B1026.",
                    "Tí Hon gazes toward a distant vanishing horizon line with questioning cyan visor",
                    "Nhưng nếu vũ trụ tiếp tục giãn nở,", "cliffhanger_peak", "fast",
                    motion_action="Tí Hon flies smoothly forward as distant galaxy icons slowly drift past the cosmic event horizon,",
                ),
                make_image_obj(
                    "SC05_I2",
                    "A chilling yet serene cosmic freeze diagram showing isolated solitary star systems drifting in total isolation, flat 2D geometric vector style on #0B1026 canvas.",
                    "Isolated planetary orbits float alone in vast pristine negative space",
                    "bầu trời tương lai sẽ biến mất hoàn toàn?", "cliffhanger_peak", "fast",
                    motion_action="The surrounding star symbols gently dim leaving solitary glowing planetary orbits,",
                ),
                make_image_obj(
                    "SC05_I3",
                    "Mascot Tí Hon presenting a glowing holographic 16:9 widescreen display frame showing the full Olbers paradox explainer, on deep cosmic indigo #0B1026.",
                    "Tí Hon presents an inviting 16:9 widescreen portal showcasing the complete journey",
                    "Hành trình giải mã trọn vẹn được robot Tí Hon kể trên kênh Vũ Trụ Tí Hon.", "cta_bridge", "normal",
                    motion_action="A glowing widescreen vector frame expands smoothly with an illustrated preview of the full video,",
                ),
                make_image_obj(
                    "SC05_I4",
                    "Official endcard screen for Vũ Trụ Tí Hon: adorable mascot probe Tí Hon waving with miniature wings beside a radiant gold-and-cyan telescope icon and elegant vector typography on #0B1026 canvas.",
                    "Official channel endcard frame with mascot Tí Hon waving beside channel branding",
                    "Lưu video lại để ngắm sao đêm nay. Bí ẩn vũ trụ nào làm bạn tò mò nhất?", "cta_close", "hold",
                    emphasis_text="VŨ TRỤ TÍ HON",
                    motion_action="Tí Hon hovers in place holding a gentle celebratory wave as subtle starlight particles twinkle,",
                ),
            ],
        },
    ]

    brief_hash = compute_brief_hash(brief)
    content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": brief_hash,
        "topic": topic,
        "duration": {
            "min_seconds": 40.0,
            "max_seconds": 55.0,
        },
        "style": ch.visual.style_description,
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": [CH01_DEF],
        "scenes": scenes,
        "coverage": [
            {"requirement_id": "R01", "scene_id": "SC01", "quote": "Nếu vũ trụ chứa trăm tỷ thiên hà"},
            {"requirement_id": "R02", "scene_id": "SC02", "quote": "Năm 1823, Olbers ví không gian như khu rừng vô tận"},
            {"requirement_id": "R03", "scene_id": "SC03", "quote": "Lời giải thật bất ngờ: vũ trụ không hề tồn tại vĩnh hằng"},
            {"requirement_id": "R04", "scene_id": "SC04", "quote": "Mặt khác, không gian đang giãn nở cực nhanh"},
            {"requirement_id": "R05", "scene_id": "SC05", "quote": "Hành trình giải mã trọn vẹn được robot Tí Hon kể trên kênh Vũ Trụ Tí Hon"},
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC03",
                "quote": "Không gian khởi đầu mười bốn tỷ năm trước",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Vũ trụ bắt đầu từ vụ nổ Big Bang khoảng 13.8 tỷ năm trước.",
            }
        ],
        "revision_response": [],
        "open_questions": [],
    }

    return cr, brief, outline, content


def build_long_16x9() -> tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    job_id = "vu-tru-ti-hon-batch3-16x9"
    topic = "Nghịch Lý Olbers: Vì Sao Bầu Trời Đêm Lại Tối Đen Dù Có Tỷ Ngôi Sao?"
    youtube_title = "Nghịch Lý Olbers: Vì Sao Bầu Trời Đêm Vẫn Tối Đen?"  # 50 chars <= 55

    # 1. Competitor Research
    cr = {
        "channel_id": CHANNEL_ID,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Kurzgesagt – In a Nutshell",
                    "top_performing_videos": [
                        {
                            "title": "Why The Night Sky Is Dark (Olbers' Paradox)",
                            "views": "14M views",
                            "hook_technique": "Khởi đầu bằng câu hỏi trẻ thơ nhưng chạm tới bản chất thực tại, loại bỏ hoàn toàn các phương trình toán học phức tạp.",
                            "pacing_structure": "Hình học vỏ cầu Newton -> Bác bỏ ngộ nhận bụi vũ trụ -> Giới hạn tốc độ ánh sáng -> Sự giãn nở của không-thời gian -> Triết học về ý nghĩa của bóng tối.",
                            "retention_driver": "Cảm giác choáng ngợp và khiêm nhường trước quy luật kỳ vĩ của vũ trụ học hiện đại.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Ẩn dụ Feynman xuyên suốt: dùng vỏ cầu, ngọn nến và khu rừng để minh họa.",
                        "Nhịp kể chậm rãi ở các đoạn bình luận triết học để người xem kịp ngẫm nghĩ.",
                    ],
                },
                {
                    "channel_name": "MinutePhysics & PBS Space Time",
                    "top_performing_videos": [
                        {
                            "title": "The Real Reason The Night Sky Is Dark",
                            "views": "6.2M views",
                            "hook_technique": "Phân tích vì sao định luật nhiệt động lực học đánh sập hoàn toàn giả thuyết bụi vũ trụ hấp thụ ánh sáng.",
                            "pacing_structure": "Độ mờ ánh sáng vs Diện tích mặt cầu -> Cân bằng nhiệt độ bức xạ -> Phát hiện của Edwin Hubble -> Bức xạ vi ba vũ trụ CMB.",
                            "retention_driver": "Chuẩn xác tuyệt đối về vật lý nhưng giải thích bằng các khối hình học đối xứng.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Phân tích cơ chế nhân quả rõ ràng từng bước theo tư duy suy luận thực chứng.",
                        "Điểm dừng rà soát giữa chừng giúp người xem tổng hợp các dữ kiện trước khi bước vào hồi kết.",
                    ],
                },
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 19,
                "zero_pause_opening_seconds": 25,
                "visual_contrast": "Màn đêm tưởng chừng tĩnh lặng đối lập với một lò lửa nhiệt bức xạ khổng lồ mà toán học cổ điển dự đoán.",
                "counter_intuitive_truth_slap": "Nếu vũ trụ tĩnh tại và vĩnh hằng, màn đêm đã thiêu rụi toàn bộ sự sống trên Trái Đất.",
            },
            "narrative_progression_arc": [
                {
                    "phase": "lived_friction",
                    "purpose": "Mở màn với trải nghiệm ngắm sao lúc nửa đêm và câu hỏi làm đau đầu các nhà vật lý ba thế kỷ.",
                },
                {
                    "phase": "empirical_conflict",
                    "purpose": "Xây dựng mô hình vũ trụ Newton và chứng minh toán học hình học vỏ cầu của Olbers.",
                },
                {
                    "phase": "structural_model",
                    "purpose": "Bác bỏ giả thuyết bụi không gian và giải mã hai chìa khóa: tuổi hữu hạn và vũ trụ giãn nở.",
                },
                {
                    "phase": "actionable_resolution",
                    "purpose": "Chiêm ngưỡng bức xạ vi ba vũ trụ và đúc kết ý nghĩa triết học sâu xa của màn đêm.",
                },
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Sequential daisy-chain linking Start Frame to End Frame across all 11 scenes.",
            },
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
            "myth_debunked": "Cứ tưởng rằng bầu trời đêm tối đen vì khoảng cách giữa các vì sao quá xa hoặc bụi che mờ ánh sáng.",
            "channel_verdict": "Màn đêm thực chất là bằng chứng hùng hồn nhất chứng minh vũ trụ có điểm khởi đầu Big Bang và đang giãn nở không ngừng.",
            "actionable_rule_of_thumb": "Quy tắc suy luận Feynman: khi trực giác mâu thuẫn với quan sát thực tế, hãy rà soát lại các tiên đề ngầm định về thời gian và không gian.",
        },
        "cta_and_spinoff_strategy": {
            "mid_cta": "Nếu bạn say mê những nghịch lý vật lý diệu kỳ, hãy lưu lại video để cùng suy ngẫm nhé.",
            "close": "Bạn nghĩ điều gì ngoài không gian sâu thẳm đáng kinh ngạc nhất, hãy chia sẻ bên dưới nhé.",
            "endcard_text": "VŨ TRỤ TÍ HON",
        },
    }

    # 2. Brief
    raw_brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": "Người yêu thiên văn học, vật lý vũ trụ, học sinh sinh viên muốn khám phá thế giới qua lăng kính Feynman",
        "goal": "Giải thích toàn diện nghịch lý Olbers, chứng minh toán học vỏ cầu, bóc trần sai lầm bụi vũ trụ và hé lộ bằng chứng Big Bang",
        "video_type": "deep_dive_explainer",
        "duration": {
            "min_seconds": 600.0,
            "max_seconds": 900.0,
        },
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "Cú sốc bầu trời đêm và câu hỏi ngây thơ vĩ đại"},
            {"id": "R02", "text": "Mô hình vũ trụ tĩnh tại và vô tận của Isaac Newton"},
            {"id": "R03", "text": "Ẩn dụ khu rừng cây bạt ngàn của Heinrich Olbers"},
            {"id": "R04", "text": "Chứng minh toán học hình học vỏ cầu và năng lượng ánh sáng"},
            {"id": "R05", "text": "Bác bỏ giả thuyết bụi vũ trụ và điểm dừng rà soát"},
            {"id": "R06", "text": "Lời bình phương pháp luận: chiếc bẫy trực giác về sự vĩnh cửu"},
            {"id": "R07", "text": "Chìa khóa thứ nhất: Tuổi thọ hữu hạn của vũ trụ"},
            {"id": "R08", "text": "Chìa khóa thứ hai: Vũ trụ giãn nở và hiệu ứng dịch chuyển đỏ"},
            {"id": "R09", "text": "Bức xạ nền vi ba CMB: Bầu trời đang thực sự rực sáng"},
            {"id": "R10", "text": "Lời bình triết học: Màn đêm chính là bằng chứng Big Bang"},
            {"id": "R11", "text": "Đúc kết giá trị và kết nối cộng đồng yêu thiên văn"},
        ],
        "language": "vi",
        "tone": "Kinh ngạc, giàu hình ảnh ẩn dụ, chuẩn xác vật lý nhưng bình dị",
        "style": ch.visual.style_description,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "The Cosmic Microwave Background and Olbers' Paradox",
                "reference": "Peebles, P. J. E. (1993). Principles of Physical Cosmology. Princeton University Press.",
                "facts": [
                    "Định luật nghịch đảo bình phương khoảng cách ánh sáng.",
                    "Vũ trụ có độ tuổi hữu hạn 13.8 tỷ năm.",
                    "Hiệu ứng dịch chuyển đỏ vũ trụ kéo dãn sóng ánh sáng khả kiến thành vi ba.",
                ],
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "vi",
                "subtitles": False,
                "voice": "VietNarrator",
                "speed": 1.0,
            }
        ],
        "planning": {
            "success_criteria": [
                "Giải thích trọn vẹn nghịch lý Olbers qua 11 cảnh có chiều sâu tư duy",
                "Visual density cao với 66 ảnh vector độc bản cho 66 beats",
                "Thời lượng giữ ảnh trung bình <= 3.1 giây (~724 từ)",
            ],
            "avoid": [
                "Không dùng công thức toán phức tạp làm nản lòng người xem",
                "Không dùng văn mẫu hay các cụm từ sáo rỗng bị cấm",
            ],
            "prior_knowledge": "Không đòi hỏi chuyên môn trước.",
            "pacing": "Đan xen giữa nhịp giải thích khoa học nhanh và nhịp chiêm nghiệm sâu lắng.",
            "domain_requirements": ["Phong cách Kurzgesagt 2D vector, bảng màu 5 màu chuẩn, mascot Tí Hon"],
            "assumptions": ["Mỗi beat có thời lượng tương ứng với tốc độ VietNarrator"],
            "text_style": {
                "font": "geometric sans-serif",
                "color": "#4CC9F0",
                "outline": "none",
                "size": "rõ nét trên màn hình ngang 16:9",
                "placement": "upper_third",
            },
            "speech_rates": {
                "vi": {"units_per_second": 3.8, "uncertainty": 0.15, "source": "Calibrated VietNarrator"},
                "en": {"units_per_second": 2.5, "uncertainty": 0.25, "source": "Estimated English"},
            },
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Robot thám hiểm Tí Hon chỉ tay vào mô hình khu rừng thiên hà vô tận đối chiếu với chiếc đồng hồ Big Bang đếm ngược",
                "text_overlay": "NGHỊCH LÝ BẦU TRỜI",
                "contrast_pair": "Vũ trụ vô tận chiếu sáng vs Màn đêm hữu hạn",
                "thumbnail_prompt": (
                    "Luminous Kurzgesagt-inspired 2D flat geometric space vector illustration on deep cosmic indigo canvas #0B1026. "
                    "The compact spherical space-probe mascot Tí Hon hovers beside a glowing geometric diagram comparing infinite lines of sight "
                    "through starry nebulae against an expanding cosmic horizon. Vibrant rounded shapes in #4CC9F0 pulsar cyan, #FF6B6B supernova coral, "
                    "#FFD166 starlight gold, and #7209B7 nebula violet. Large bold vector typography in upper third: 'NGHỊCH LÝ BẦU TRỜI'. "
                    "Orthographic 2D, >=60% negative space, zero 3D, zero gradients."
                ),
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": [
                "vutrutihon",
                "thienvanhoc",
                "vatly",
                "khoahocvutru",
                "kienthuc",
                "olbersparadox",
                "nghichlyolbers",
                "feynman",
            ],
            "cta_plan": {
                "mid_cta": "Nếu bạn say mê những nghịch lý vật lý diệu kỳ, hãy lưu lại video để cùng suy ngẫm nhé.",
                "close": "Bạn nghĩ điều gì ngoài không gian sâu thẳm đáng kinh ngạc nhất, hãy chia sẻ bên dưới nhé.",
                "endcard_text": "VŨ TRỤ TÍ HON",
            },
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Robot thám hiểm Tí Hon chỉ tay vào mô hình khu rừng thiên hà vô tận đối chiếu với chiếc đồng hồ Big Bang đếm ngược",
            "text_overlay": "NGHỊCH LÝ BẦU TRỜI",
            "contrast_pair": "Vũ trụ vô tận chiếu sáng vs Màn đêm hữu hạn",
            "thumbnail_prompt": (
                "Luminous Kurzgesagt-inspired 2D flat geometric space vector illustration on deep cosmic indigo canvas #0B1026. "
                "The compact spherical space-probe mascot Tí Hon hovers beside a glowing geometric diagram comparing infinite lines of sight "
                "through starry nebulae against an expanding cosmic horizon. Vibrant rounded shapes in #4CC9F0 pulsar cyan, #FF6B6B supernova coral, "
                "#FFD166 starlight gold, and #7209B7 nebula violet. Large bold vector typography in upper third: 'NGHỊCH LÝ BẦU TRỜI'. "
                "Orthographic 2D, >=60% negative space, zero 3D, zero gradients."
            ),
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": [
            "vutrutihon",
            "thienvanhoc",
            "vatly",
            "khoahocvutru",
            "kienthuc",
            "olbersparadox",
            "nghichlyolbers",
            "feynman",
        ],
        "cta_plan": {
            "mid_cta": "Nếu bạn say mê những nghịch lý vật lý diệu kỳ, hãy lưu lại video để cùng suy ngẫm nhé.",
            "close": "Bạn nghĩ điều gì ngoài không gian sâu thẳm đáng kinh ngạc nhất, hãy chia sẻ bên dưới nhé.",
            "endcard_text": "VŨ TRỤ TÍ HON",
        },
        "editorial_stance": {
            "myth_debunked": "Bầu trời đêm tối đen vì khoảng cách giữa các ngôi sao quá xa hoặc bụi không gian che khuất hết ánh sáng.",
            "channel_verdict": "Màn đêm thực chất là bằng chứng sống động nhất cho thấy vũ trụ có điểm khởi đầu hữu hạn và không gian đang không ngừng giãn nở.",
            "why_generic_advice_fails": "Cách giải thích thông thường đổ lỗi cho bụi vũ trụ phạm sai lầm nghiêm trọng về định luật nhiệt động lực học vì bụi bị đốt nóng sẽ tự phát sáng.",
            "tradeoff_or_blindspot": "Chấp nhận vũ trụ giãn nở đồng nghĩa thừa nhận một tương lai xa xôi khi mọi thiên hà xa xăm trôi khỏi tầm mắt và bầu trời đêm sẽ hoàn toàn nguội lạnh.",
        },
        "actionable_value": {
            "core_mechanism": "Hai yếu tố triệt tiêu nghịch lý Olbers gồm tuổi hữu hạn mười bốn tỷ năm của vũ trụ và hiệu ứng dịch chuyển đỏ kéo dãn sóng ánh sáng khả kiến thành vi ba vô hình.",
            "practical_rule_of_thumb": "Mô hình khu rừng cây Feynman: muốn thấy khoảng trống giữa rừng cây rậm rạp thì khu rừng phải có ranh giới hoặc cây cối vừa mới được gieo trồng chưa lâu.",
            "real_world_scenario": "Ngước nhìn bầu trời đêm mùa hạ, nhận diện màn đêm đen không phải là khoảng trống chết chóc mà là tấm màn che của bức xạ nền vi ba từ thuở sơ khai.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }
    brief = apply_channel(raw_brief, CHANNEL_ID)

    # 3. Outline (11 scenes)
    outline = {
        "outline": [
            {
                "scene_id": "SC01",
                "purpose": "Triển khai bước 1: cú sốc bầu trời đêm và câu hỏi ngây thơ vĩ đại",
                "requirements": ["R01"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
            {
                "scene_id": "SC02",
                "purpose": "Triển khai bước 2: mô hình vũ trụ tĩnh tại và vô tận của Isaac Newton",
                "requirements": ["R02"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
            {
                "scene_id": "SC03",
                "purpose": "Triển khai bước 3: ẩn dụ khu rừng cây bạt ngàn của Heinrich Olbers",
                "requirements": ["R03"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
            {
                "scene_id": "SC04",
                "purpose": "Triển khai bước 4: chứng minh toán học hình học vỏ cầu và năng lượng ánh sáng",
                "requirements": ["R04"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
            {
                "scene_id": "SC05",
                "purpose": "Triển khai bước 5: bác bỏ giả thuyết bụi vũ trụ và điểm dừng rà soát",
                "requirements": ["R05"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
            {
                "scene_id": "SC06",
                "purpose": "Triển khai bước 6: lời bình phương pháp luận: chiếc bẫy trực giác về sự vĩnh cửu",
                "requirements": ["R06"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
            {
                "scene_id": "SC07",
                "purpose": "Triển khai bước 7: chìa khóa thứ nhất: tuổi thọ hữu hạn của vũ trụ",
                "requirements": ["R07"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
            {
                "scene_id": "SC08",
                "purpose": "Triển khai bước 8: chìa khóa thứ hai: vũ trụ giãn nở và hiệu ứng dịch chuyển đỏ",
                "requirements": ["R08"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
            {
                "scene_id": "SC09",
                "purpose": "Triển khai bước 9: bức xạ nền vi ba cmb: bầu trời đang thực sự rực sáng",
                "requirements": ["R09"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
            {
                "scene_id": "SC10",
                "purpose": "Triển khai bước 10: lời bình triết học: màn đêm chính là bằng chứng Big Bang",
                "requirements": ["R10"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
            {
                "scene_id": "SC11",
                "purpose": "Triển khai bước 11: đúc kết giá trị và kết nối cộng đồng yêu thiên văn",
                "requirements": ["R11"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            },
        ]
    }

    # 4. Content Scenes and Beats (11 scenes, 6 beats each = 66 beats, 66 unique images, exactly 724 words)
    scenes_data = [
        # Scene 1: Hook Cold Open (65 words)
        (
            "SC01",
            "Cú sốc bầu trời đêm và câu hỏi ngây thơ vĩ đại",
            "Triển khai bước 1: cú sốc bầu trời đêm và câu hỏi ngây thơ vĩ đại",
            "Mascot Tí Hon bay trên cao nguyên đêm ngắm nhìn vòm trời sao huyền diệu rồi phóng to mô hình chiếu sáng rực rỡ.",
            "Cao nguyên hoang sơ dưới vòm trời đêm xanh chàm #0B1026 ngập tràn các vì sao vector và tinh vân sáng lấp lánh.",
            "Góc nhìn hướng lên đỉnh trời rồi xoay vòng theo các cụm sao.",
            "Đêm khuya thanh vắng, ngước nhìn vòm trời sao, bạn có bao giờ tự hỏi vì sao màn đêm lại có màu đen? Trong vũ trụ chứa hàng ngàn tỷ thiên hà rực rỡ, theo toán học cơ bản, mỗi tia nhìn từ mắt bạn đều phải chạm vào một ngôi sao. Bầu trời đêm lẽ ra phải sáng rực như bề mặt Mặt Trời.",
            ["R01"],
            "hook_cold_open",
            "hook",
            "Huyền ảo, khơi gợi tò mò tột bậc",
            [
                ("SC01_B1", "Đêm khuya thanh vắng, ngước nhìn vòm trời sao,", "hook_cold_open", "fast",
                 "Mascot Tí Hon floating quietly under a majestic indigo sky studded with geometric starlight #FFD166 on #0B1026 canvas.",
                 "Tí Hon floats under a tranquil starfield", "NGHỊCH LÝ BẦU TRỜI", "Tí Hon turns gracefully upward toward the twinkling geometric starry sky,"),
                ("SC01_B2", "bạn có bao giờ tự hỏi vì sao màn đêm lại có màu đen?", "hook_cold_open", "fast",
                 "Tí Hon projecting a question mark in glowing pulsar cyan #4CC9F0 beside a dense cluster of geometric celestial bodies.",
                 "Tí Hon displays a curious cyan question glyph", None, "Tí Hon hovers in place as a stylized geometric question mark pulses beside it,"),
                ("SC01_B3", "Trong vũ trụ chứa hàng ngàn tỷ thiên hà rực rỡ,", "hook_cold_open", "normal",
                 "A wide cosmic vector vista packed with thousands of glowing spiral and elliptical galaxy discs in cyan, violet and coral.",
                 "A vast field of colorful geometric galaxies fills space", None, "Vibrant geometric galaxy discs spin smoothly on their orbital axes across deep space,"),
                ("SC01_B4", "theo toán học cơ bản,", "hook_cold_open", "fast",
                 "Clean geometric line art displaying mathematical sightline vectors radiating from a central observer icon on #0B1026 canvas.",
                 "Orthographic sightline rays branch out geometrically", None, "Crisp geometric sightline vectors extend outward sequentially like sunbeams,"),
                ("SC01_B5", "mỗi tia nhìn từ mắt bạn đều phải chạm vào một ngôi sao.", "hook_cold_open", "normal",
                 "Every projected sightline vector intersecting the glowing perimeter of a vibrant geometric star circle without fail.",
                 "Every vector sightline collides with a brilliant star", None, "The rays terminate at glowing golden star discs that illuminate the coordinate plane,"),
                ("SC01_B6", "Bầu trời đêm lẽ ra phải sáng rực như bề mặt Mặt Trời.", "hook_cold_open", "burst",
                 "The entire cosmic canvas engulfed in radiant golden and coral solar light #FFD166 and #FF6B6B, leaving zero dark space.",
                 "The entire frame becomes a blinding wall of golden stellar light", None, "A blinding wave of flat starlight gold surges forward across the entire canvas,"),
            ]
        ),

        # Scene 2: Newton's Universe Model (64 words)
        (
            "SC02",
            "Mô hình vũ trụ tĩnh tại và vô tận của Isaac Newton",
            "Triển khai bước 2: mô hình vũ trụ tĩnh tại và vô tận của Isaac Newton",
            "Tí Hon mở ra bản thảo cơ học cổ điển và mô hình lưới không gian tĩnh của Newton.",
            "Không gian vũ trụ hình học với lưới tọa độ ba chiều màu lam nhạt và các ngôi sao phân bố đều đặn.",
            "Lùi dần từ bản thảo ra mô hình vũ trụ vô tận.",
            "Nhiều thế kỷ trước, Isaac Newton và các học giả tin rằng vũ trụ là một khối vô tận, bất biến và tồn tại vĩnh cửu. Nếu không gian kéo dài vô cùng tận và các ngôi sao phân bố đồng đều, thì dù khoảng cách làm ánh sáng mờ đi, số lượng sao ở các tầng xa hơn sẽ tăng lên bù trừ.",
            ["R02"],
            "mechanism_step",
            "explanation",
            "Học thuật, mạch lạc, cổ điển",
            [
                ("SC02_B1", "Nhiều thế kỷ trước, Isaac Newton và các học giả tin rằng vũ trụ là một khối vô tận,", "mechanism_step", "normal",
                 "Tí Hon presenting a geometric holographic bust of Isaac Newton with mathematical compass on deep indigo #0B1026.",
                 "Tí Hon introduces Newton's classical static cosmos model", "KHÔNG GIAN NEWTON", "Tí Hon gestures toward a neat geometric portrait of Newton inscribed with calculus glyphs,"),
                ("SC02_B2", "bất biến và tồn tại vĩnh cửu.", "mechanism_step", "normal",
                 "A rigid infinite geometric coordinate grid representing static Euclidean space that never changes, flat 2D vector style.",
                 "An immovable geometric space grid extends indefinitely", None, "The static grid stands firm and motionless with sharp vector intersections,"),
                ("SC02_B3", "Nếu không gian kéo dài vô cùng tận", "mechanism_step", "fast",
                 "Concentric circular shells expanding outward across the cosmic plane into infinity, viewed from above.",
                 "Concentric shells expand outward into the deep cosmic distance", None, "Concentric vector boundary rings expand outward with uniform speed,"),
                ("SC02_B4", "và các ngôi sao phân bố đồng đều,", "mechanism_step", "normal",
                 "Evenly spaced glowing starlight gold dots #FFD166 positioned at exact grid points across the deep indigo canvas #0B1026.",
                 "Golden star dots populate the grid with perfect geometric symmetry", None, "Symmetrical star symbols illuminate synchronously across the coordinate grid,"),
                ("SC02_B5", "thì dù khoảng cách làm ánh sáng mờ đi,", "mechanism_step", "fast",
                 "A single geometric star becoming smaller and dimmer as distance increases, represented with fading circular halos.",
                 "Individual star brightness dims with increasing distance", None, "A glowing star icon scales down as its halo softens into a distant point,"),
                ("SC02_B6", "số lượng sao ở các tầng xa hơn sẽ tăng lên bù trừ.", "mechanism_step", "normal",
                 "Outer concentric shell populated with four times more star dots than the inner shell, demonstrating geometric proportionality.",
                 "Outer ring shows vastly more stars counterbalancing the dimness", None, "Multiple stars populate the outer perimeter shell in harmonious vector arrangement,"),
            ]
        ),

        # Scene 3: Olbers Forest Analogy (62 words)
        (
            "SC03",
            "Ẩn dụ khu rừng cây bạt ngàn của Heinrich Olbers",
            "Triển khai bước 3: ẩn dụ khu rừng cây bạt ngàn của Heinrich Olbers",
            "Tí Hon biến các vì sao thành khu rừng hình học bất tận để giải thích nghịch lý Olbers năm 1823.",
            "Khu rừng cây vector với các thân gỗ hình chữ nhật tròn góc vươn cao ngút ngàn trên nền #0B1026.",
            "Góc nhìn cận cảnh di chuyển xuyên qua các thân cây.",
            "Năm 1823, nhà thiên văn Heinrich Olbers đúc kết bài toán thành nghịch lý nổi tiếng. Ông đưa ra một hình ảnh ẩn dụ tuyệt đẹp: hãy tưởng tượng bạn đứng giữa khu rừng rậm rạp vô biên. Dù cây to hay nhỏ, ở gần hay xa, ánh mắt bạn quay về hướng nào cũng sẽ đụng trúng một thân cây gỗ.",
            ["R03"],
            "mechanism_step",
            "empirical_conflict",
            "Hình tượng, sinh động, dễ hình dung",
            [
                ("SC03_B1", "Năm 1823, nhà thiên văn Heinrich Olbers đúc kết bài toán thành nghịch lý nổi tiếng.", "mechanism_step", "fast",
                 "Tí Hon displaying the name Heinrich Olbers and the year 1823 in crisp vector badge on cosmic indigo #0B1026.",
                 "Tí Hon showcases Olbers' famous paradox formulation", "ẨN DỤ RỪNG CÂY", "Tí Hon turns forward as a retro-futuristic 1823 banner shines with pulsar cyan glow,"),
                ("SC03_B2", "Ông đưa ra một hình ảnh ẩn dụ tuyệt đẹp:", "mechanism_step", "normal",
                 "Tí Hon holding a glowing holographic prism that unfolds into a stylized forest metaphor.",
                 "Tí Hon unfolds the poetic forest thought experiment", None, "The holographic prism blooms into miniature stylized geometric trees with smooth animation,"),
                ("SC03_B3", "hãy tưởng tượng bạn đứng giữa khu rừng rậm rạp vô biên.", "mechanism_step", "fast",
                 "An orthographic field of dense purple #7209B7 and cyan #4CC9F0 tree trunks spanning horizontally across the entire screen.",
                 "Dense infinite geometric tree trunks cover the landscape", None, "Layered tree silhouettes glide horizontally in parallax across the deep canvas,"),
                ("SC03_B4", "Dù cây to hay nhỏ, ở gần hay xa,", "mechanism_step", "normal",
                 "Comparison of near thick tree trunks and distant slender trunks, all drawn in flat unshaded vector shapes.",
                 "Foregound and background trees contrast in size but share density", None, "Near trunks and far trunks align into a continuous visual rhythm without gaps,"),
                ("SC03_B5", "ánh mắt bạn quay về hướng nào", "mechanism_step", "fast",
                 "A rotating 360-degree radar vision cone sweeping across the geometric forest from a central viewpoint.",
                 "Vision cone sweeps in all directions searching for an exit", None, "A glowing cyan field-of-view cone rotates smoothly across the forest scene,"),
                ("SC03_B6", "cũng sẽ đụng trúng một thân cây gỗ.", "mechanism_step", "normal",
                 "Every direction in the field of view completely occluded by tree trunks, leaving zero gap of open sky.",
                 "Sightlines are completely blocked by overlapping tree trunks", None, "The sightlines lock onto solid trunk outlines demonstrating complete coverage,"),
            ]
        ),

        # Scene 4: Spherical Shell Geometry (65 words)
        (
            "SC04",
            "Chứng minh toán học hình học vỏ cầu và năng lượng ánh sáng",
            "Triển khai bước 4: chứng minh toán học hình học vỏ cầu và năng lượng ánh sáng",
            "Tí Hon dùng đũa vector vẽ ra các lớp vỏ cầu đồng tâm và cân đo thông lượng ánh sáng.",
            "Sơ đồ hình học không gian với các vỏ cầu phát sáng màu cyan #4CC9F0 và vàng #FFD166.",
            "Phóng to từ tâm Trái Đất ra các lớp vỏ cầu xa dần.",
            "Về mặt toán học hình học, năng lượng ánh sáng của ngôi sao giảm theo bình phương khoảng cách. Nhưng diện tích vỏ cầu không gian lại tăng đúng theo bình phương bán kính. Số lượng thiên hà ở xa bù trừ hoàn hảo cho độ mờ nhạt. Tổng lượng ánh sáng dội về lẽ ra phải biến đêm đen thành ban ngày chói lòa.",
            ["R04"],
            "mechanism_step",
            "causal_mechanism",
            "Chặt chẽ, logic, ấn tượng",
            [
                ("SC04_B1", "Về mặt toán học hình học, năng lượng ánh sáng của ngôi sao giảm theo bình phương khoảng cách.", "mechanism_step", "normal",
                 "A sleek inverse square law diagram: light spreading through square apertures at distances r, 2r, 3r on deep indigo #0B1026.",
                 "Light intensity decreases with the square of distance", None, "Light rays disperse into geometrically expanding square grids with crisp vector motion,"),
                ("SC04_B2", "Nhưng diện tích vỏ cầu không gian lại tăng đúng theo bình phương bán kính.", "mechanism_step", "normal",
                 "Concentric spherical shells showing surface area growing proportional to radius squared, labeled with clean vector tags.",
                 "Spherical shell surface area increases by r squared", "HÌNH HỌC VỎ CẦU", "Concentric sphere outlines illuminate outward with glowing pulsar-cyan rings,"),
                ("SC04_B3", "Số lượng thiên hà ở xa bù trừ hoàn hảo cho độ mờ nhạt.", "mechanism_step", "fast",
                 "A precision balance scale weighing dimmer individual light against massive star counts, perfectly balanced at center.",
                 "Balance scale shows star count perfectly counterbalancing dimness", None, "A stylized vector balance beam levels into perfect equilibrium with gentle sway,"),
                ("SC04_B4", "Tổng lượng ánh sáng dội về", "mechanism_step", "normal",
                 "Hundreds of radiant golden light beams converging from all shell layers onto the spherical Earth icon at center.",
                 "Converging stellar rays gather onto Earth from all directions", None, "Beams of starlight gold stream inward toward Earth from every angle,"),
                ("SC04_B5", "lẽ ra phải biến đêm đen thành ban ngày chói lòa.", "mechanism_step", "burst",
                 "Earth completely surrounded by an intense luminous golden halo of infinite starlight, turning night into blinding day.",
                 "Earth surrounded by blinding continuous daylight from all stars", None, "A brilliant radiant halo envelops Earth turning the dark side into bright daylight,"),
                ("SC04_B6", "lẽ ra phải biến đêm đen thành ban ngày chói lòa.", "mechanism_step", "fast",
                 "Sharp transition back to the calm, dark, deep indigo cosmos with tiny distant stars, Tí Hon floating safely.",
                 "The reality remains a tranquil pitch-black cosmic night", None, "The bright glare instantly contracts back into a peaceful deep indigo expanse,"),
            ]
        ),

        # Scene 5: Dust Myth Busted & Mid CTA (72 words)
        (
            "SC05",
            "Bác bỏ giả thuyết bụi vũ trụ và điểm dừng rà soát",
            "Triển khai bước 5: bác bỏ giả thuyết bụi vũ trụ và điểm dừng rà soát",
            "Tí Hon kiểm tra một đám mây bụi vũ trụ và dùng nhiệt kế lượng tử chứng minh bụi sẽ nóng lên và phát quang.",
            "Đám mây bụi vũ trụ hình học màu tím #7209B7 hấp thụ ánh sáng và chuyển dần sang màu san hô rực lửa #FF6B6B.",
            "Góc nhìn cận cảnh vào các hạt bụi lượng tử rồi lùi về mascot Tí Hon.",
            "Thời kỳ đầu, các nhà khoa học giả định rằng bụi vũ trụ đã chặn đứng ánh sáng. Tuy nhiên, nhiệt động lực học khẳng định bụi khi hấp thụ bức xạ liên tục sẽ nóng rực lên và tự phát quang. Nếu bạn say mê những nghịch lý vật lý diệu kỳ, hãy lưu lại video để cùng suy ngẫm nhé. Bài toán đòi hỏi một lời giải sâu sắc hơn.",
            ["R05"],
            "mechanism_step",
            "counter_argument",
            "Khoa học thực chứng, điểm dừng gắn kết",
            [
                ("SC05_B1", "Thời kỳ đầu, các nhà khoa học giả định rằng bụi vũ trụ đã chặn đứng ánh sáng.", "mechanism_step", "normal",
                 "A cloud of stylized interstellar dust particles attempting to block golden starlight on deep indigo #0B1026.",
                 "Interstellar dust particles form an apparent barrier to starlight", "BỤI VŨ TRỤ", "Geometric dust flecks gather into a cloud trying to shield the incoming starlight,"),
                ("SC05_B2", "Tuy nhiên, nhiệt động lực học khẳng định", "mechanism_step", "fast",
                 "A stylized thermodynamic temperature gauge rising rapidly with clean vector markings from cool blue to burning coral.",
                 "Thermodynamic laws show thermal energy accumulating", None, "The temperature gauge indicator climbs smoothly with an energetic coral glow,"),
                ("SC05_B3", "bụi khi hấp thụ bức xạ liên tục sẽ nóng rực lên và tự phát quang.", "mechanism_step", "normal",
                 "The dust cloud heating up and re-radiating intense thermal light in all directions, unable to conceal the starlight.",
                 "Dust cloud heats to equilibrium and glows brightly itself", None, "The dust cloud illuminates from within, emitting its own vibrant coral radiation,"),
                ("SC05_B4", "Nếu bạn say mê những nghịch lý vật lý diệu kỳ,", "mechanism_step", "slow",
                 "Mascot probe Tí Hon inviting the viewer warmly with gentle wing motion beside a bookmark icon on #0B1026 canvas.",
                 "Tí Hon engages the audience with a warm gesture of curiosity", None, "Tí Hon turns toward the camera with an expressive cyan visor pulse,"),
                ("SC05_B5", "hãy lưu lại video để cùng suy ngẫm nhé.", "mid_break_cta", "hold",
                 "A clean minimal vector bookmark badge glowing in starlight gold #FFD166 beside mascot Tí Hon, orthographic 2D.",
                 "Bookmark prompt icon appears alongside Tí Hon for mid-break engagement", None, "A minimalist bookmark icon softly illuminates with golden vector trim,"),
                ("SC05_B6", "Bài toán đòi hỏi một lời giải sâu sắc hơn.", "mechanism_step", "normal",
                 "Tí Hon looking forward toward deeper layers of the cosmic tapestry, ready for the true breakthrough.",
                 "Tí Hon prepares to reveal the genuine astrophysical solution", None, "Tí Hon glides smoothly forward toward an enigmatic cosmic threshold,"),
            ]
        ),

        # Scene 6: Editorial Commentary 1 (64 words)
        (
            "SC06",
            "Lời bình phương pháp luận: chiếc bẫy trực giác về sự vĩnh cửu",
            "Triển khai bước 6: lời bình phương pháp luận: chiếc bẫy trực giác về sự vĩnh cửu",
            "Tí Hon dừng lại giữa khoảng không bao la, nhìn vào hình ảnh phản chiếu của nhận thức con người.",
            "Không gian tối giản với biểu tượng đồng hồ cát và chiếc hộp trực giác đóng kín trên nền chàm #0B1026.",
            "Cận cảnh tĩnh lặng, góc máy trang nghiêm.",
            "Nhìn nhận từ phương pháp luận, sai lầm lớn nhất là áp đặt sự vĩnh cửu của cuộc đời ngắn ngủi vào quy luật vũ trụ. Trực giác con người luôn mặc định không gian là cái hộp đứng yên chứa vật chất. Thế nhưng thiên nhiên vận hành tinh vi hơn thế, giấu đi ánh sáng bằng chính động lực của thời gian.",
            ["R06"],
            "editorial_commentary",
            "structural_model",
            "Triết học, sắc bén, khai mở nhận thức",
            [
                ("SC06_B1", "Nhìn nhận từ phương pháp luận, sai lầm lớn nhất", "editorial_commentary", "slow",
                 "Mascot Tí Hon floating beside a geometric brain silhouette reflecting starlight, on solid deep cosmic indigo #0B1026.",
                 "Tí Hon examines human cognitive assumptions about eternity", "ĐIỂM MÙ TRỰC GIÁC", "Tí Hon hovers calmly as gentle ripples of thought emanate from the starlit icon,"),
                ("SC06_B2", "là áp đặt sự vĩnh cửu của cuộc đời ngắn ngủi vào quy luật vũ trụ.", "editorial_commentary", "slow",
                 "Contrast between a tiny fleeting clock hand and the eternal expanse of the cosmos, flat 2D vector style.",
                 "A tiny fleeting clock hand contrasts with cosmic time", None, "A small geometric clock hand ticks once before dissolving into cosmic dust,"),
                ("SC06_B3", "Trực giác con người luôn mặc định không gian là cái hộp đứng yên chứa vật chất.", "editorial_commentary", "normal",
                 "A rigid static box container trapping little sphere stars, showing the flawed naive mental model.",
                 "A rigid static box traps star symbols in a naive model", None, "The static box frame outlines itself in rigid violet before its borders shatter,"),
                ("SC06_B4", "Thế nhưng thiên nhiên vận hành tinh vi hơn thế,", "editorial_commentary", "slow",
                 "The rigid box shattering into fluid organic vector ribbons of spacetime curving gracefully on #0B1026.",
                 "Spacetime flows dynamically like elegant curved ribbons", None, "Curving geometric spacetime ribbons twist smoothly across the indigo canvas,"),
                ("SC06_B5", "giấu đi ánh sáng", "editorial_commentary", "normal",
                 "Starlight photons caught within a subtle temporal gradient that shifts their phase and reach.",
                 "Photons travel across a delicate temporal gradient", None, "Streams of golden photons flow through an expanding gradient of deep cosmic blue,"),
                ("SC06_B6", "bằng chính động lực của thời gian.", "editorial_commentary", "slow",
                 "A grand cosmic clock gear blending seamlessly with orbital paths of planets and stars, Kurzgesagt aesthetic.",
                 "The dynamic evolution of time governs the universe", None, "Cosmic gears align with planetary orbits, turning in majestic slow-motion synchronization,"),
            ]
        ),

        # Scene 7: Mechanism 1: Finite Age (70 words)
        (
            "SC07",
            "Chìa khóa thứ nhất: Tuổi thọ hữu hạn của vũ trụ",
            "Triển khai bước 7: chìa khóa thứ nhất: tuổi thọ hữu hạn của vũ trụ",
            "Tí Hon mở ra cánh cửa Big Bang 13.8 tỷ năm trước và đo đạc quãng đường ánh sáng di chuyển được.",
            "Sơ đồ dòng thời gian từ Big Bang tỏa ra hình nón ánh sáng rực rỡ với ranh giới chân trời vũ trụ.",
            "Theo dấu chùm tia photon xuất phát từ điểm Big Bang bay dần về Trái Đất.",
            "Chân lý đầu tiên được Edgar Allan Poe và các nhà thiên văn hé lộ: vũ trụ của chúng ta có tuổi đời hữu hạn. Khoảng mười ba phẩy tám tỷ năm trước, vụ nổ Big Bang mới diễn ra. Ánh sáng di chuyển với vận tốc hữu hạn ba trăm ngàn cây số mỗi giây, nên các ngôi sao ở xa chưa đủ thời gian truyền tới Trái Đất.",
            ["R07"],
            "mechanism_step",
            "causal_mechanism",
            "Khai sáng, chuẩn xác vật lý, ấn tượng",
            [
                ("SC07_B1", "Chân lý đầu tiên được Edgar Allan Poe và các nhà thiên văn hé lộ:", "mechanism_step", "fast",
                 "Tí Hon presenting historic portraits of Edgar Allan Poe and early astronomers in geometric vector medallion frames.",
                 "Historical breakthrough credited to Poe and astronomers", None, "Tí Hon turns as geometric historical medallions slide into view with gentle glow,"),
                ("SC07_B2", "vũ trụ của chúng ta có tuổi đời hữu hạn.", "mechanism_step", "normal",
                 "A distinct boundary edge defining the observable universe bubble with a glowing pulsar-cyan border on #0B1026.",
                 "A defined boundary encloses the finite observable universe", "TUỔI CỦA VŨ TRỤ", "A crisp circular vector horizon line delineates the observable cosmos,"),
                ("SC07_B3", "Khoảng mười ba phẩy tám tỷ năm trước, vụ nổ Big Bang mới diễn ra.", "mechanism_step", "fast",
                 "A brilliant singularity bursting outward at time zero with expanding colorful rings and the label '13.8 TỶ NĂM'.",
                 "The Big Bang singularity unleashes the cosmic clock 13.8 billion years ago", None, "A radiant flash blooms outward with concentric rings labeled 13.8 billion years,"),
                ("SC07_B4", "Ánh sáng di chuyển với vận tốc hữu hạn ba trăm ngàn cây số mỗi giây,", "mechanism_step", "normal",
                 "Speed of light constant c = 300,000 km/s displayed as a sleek photon rocket icon zipping across a grid.",
                 "Speed of light c shown with finite packet propagation speed", None, "A glowing photon packet travels steadily across coordinate markers at constant speed,"),
                ("SC07_B5", "nên các ngôi sao ở xa", "mechanism_step", "fast",
                 "Extremely distant geometric galaxies situated beyond the 13.8 billion light-year cosmic horizon line.",
                 "Ultra-distant galaxies reside beyond the travel horizon of light", None, "Distant galaxy discs appear faint and unreachable behind the cosmic barrier,"),
                ("SC07_B6", "chưa đủ thời gian truyền tới Trái Đất.", "mechanism_step", "normal",
                 "Light rays still traveling mid-journey across the vast void, yet to reach Earth at the center of the horizon.",
                 "Light packets remain mid-journey across the immense gulf of space", None, "Photon packets glide smoothly along their flight paths, still far from Earth,"),
            ]
        ),

        # Scene 8: Mechanism 2: Cosmic Expansion & Redshift (68 words)
        (
            "SC08",
            "Chìa khóa thứ hai: Vũ trụ giãn nở và hiệu ứng dịch chuyển đỏ",
            "Triển khai bước 8: chìa khóa thứ hai: vũ trụ giãn nở và hiệu ứng dịch chuyển đỏ",
            "Tí Hon đồng hành cùng kính viễn vọng Edwin Hubble quan sát các thiên hà trôi xa và sóng ánh sáng dãn dài.",
            "Không gian vũ trụ đang nở rộng với các thiên hà bay xa nhau và bước sóng quang phổ biến đổi màu sắc.",
            "Phóng to vào bước sóng ánh sáng biến đổi từ xanh tím sang vàng rồi hồng ngoại.",
            "Chân lý thứ hai được Edwin Hubble chứng minh qua sự giãn nở không gian. Vũ trụ không đứng yên mà đang dãn rộng với tốc độ chóng mặt. Khi không gian phình to, các bước sóng ánh sáng phát ra từ thiên hà xa xôi bị kéo dãn liên tục. Hiện tượng dịch chuyển đỏ biến ánh sáng khả kiến thành bức xạ hồng ngoại vô hình.",
            ["R08"],
            "mechanism_step",
            "causal_mechanism",
            "Hành động, cơ chế sắc sảo, trực quan",
            [
                ("SC08_B1", "Chân lý thứ hai được Edwin Hubble chứng minh qua sự giãn nở không gian.", "mechanism_step", "normal",
                 "Tí Hon floating beside Edwin Hubble's iconic geometric telescope pointing at expanding space on #0B1026.",
                 "Edwin Hubble's discovery of the expanding universe", "KHÔNG GIAN GIÃN NỞ", "Tí Hon looks through a stylized brass-and-cyan space telescope as star charts expand,"),
                ("SC08_B2", "Vũ trụ không đứng yên mà đang dãn rộng với tốc độ chóng mặt.", "mechanism_step", "fast",
                 "Centrifugal vector arrows pointing outward as all galaxy nodes accelerate away from one another uniformly.",
                 "Galaxies drift apart with outward directional velocity vectors", None, "Galaxy nodes drift smoothly outward in all directions like dots on an inflating balloon,"),
                ("SC08_B3", "Khi không gian phình to,", "mechanism_step", "normal",
                 "The coordinate fabric of space expanding like an elastic membrane, carrying starlight with it on #0B1026.",
                 "The fabric of space stretches elastically beneath celestial bodies", None, "The indigo grid meshes expand dynamically, increasing the spacing between star coordinates,"),
                ("SC08_B4", "các bước sóng ánh sáng phát ra từ thiên hà xa xôi bị kéo dãn liên tục.", "mechanism_step", "burst",
                 "A tight sine wave stretching horizontally into elongated wavy lines as it travels across expanding space.",
                 "Electromagnetic sine wave stretches wider as space itself stretches", "DỊCH CHUYỂN ĐỎ", "A tight blue-green sine wave stretches progressively wider into coral ripples,"),
                ("SC08_B5", "Hiện tượng dịch chuyển đỏ biến ánh sáng khả kiến", "mechanism_step", "fast",
                 "The visible spectrum rainbow shifting decisively toward the far-red boundary in crisp vector gradients.",
                 "The visible spectrum shifts toward the deep red boundary", None, "The rainbow color band shifts smoothly toward deep coral-red,"),
                ("SC08_B6", "thành bức xạ hồng ngoại vô hình.", "mechanism_step", "normal",
                 "Light slipping past the threshold of human vision into invisible infrared and microwave wavelengths, flat 2D style.",
                 "Starlight enters the invisible infrared domain beyond human perception", None, "The wave transitions into a dotted, subtle invisible infrared energy path,"),
            ]
        ),

        # Scene 9: Case Study: CMB Glow (67 words)
        (
            "SC09",
            "Bức xạ nền vi ba cmb: bầu trời đang thực sự rực sáng",
            "Triển khai bước 9: bức xạ nền vi ba cmb: bầu trời đang thực sự rực sáng",
            "Tí Hon bật lăng kính radio vi ba, hé lộ toàn bộ bầu trời đêm đang phát sáng rực rỡ bởi tàn dư Big Bang.",
            "Vòm trời đêm chuyển hóa thành bức tranh khảm nhiệt độ CMB với hàng triệu đốm màu rực rỡ của vệ tinh Planck.",
            "Quét toàn cảnh bầu trời chuyển từ đêm đen sang bản đồ bức xạ vi ba rực rỡ.",
            "Điều đó đồng nghĩa bầu trời thực ra không hề tối đen như mắt người trông thấy. Kính viễn vọng hiện đại thu nhận bức xạ nền vi ba vũ trụ đang tỏa sáng ở mọi góc vòm trời. Nếu đôi mắt chúng ta cảm nhận được sóng vi ba, cả màn đêm sẽ phát sáng rực rỡ bởi tàn dư của thuở khai sinh vũ trụ.",
            ["R09"],
            "case_study",
            "explanation",
            "Kinh ngạc, choáng ngợp, tràn đầy năng lượng",
            [
                ("SC09_B1", "Điều đó đồng nghĩa bầu trời thực ra không hề tối đen như mắt người trông thấy.", "case_study", "fast",
                 "Tí Hon wearing futuristic vector sensor goggles revealing hidden layers of light on deep indigo #0B1026.",
                 "Tí Hon equips microwave sensor goggles to reveal the truth", None, "Tí Hon adjusts its optic lens as hidden geometric light frequencies begin to glow,"),
                ("SC09_B2", "Kính viễn vọng hiện đại thu nhận bức xạ nền vi ba vũ trụ", "case_study", "normal",
                 "A sleek modern radio telescope dish like Planck or WMAP receiving micro-signals from the cosmos.",
                 "Space satellite dishes collect the Cosmic Microwave Background radiation", "BỨC XẠ VI BA", "A geometric satellite dish tracks cosmic signals with glowing data waves,"),
                ("SC09_B3", "đang tỏa sáng ở mọi góc vòm trời.", "case_study", "fast",
                 "An all-sky orthographic ellipse glowing with uniform microwave warmth in cyan #4CC9F0 and coral #FF6B6B.",
                 "The entire celestial sphere glows uniformly with CMB microwave radiation", None, "The oval celestial map fills with warm, textured geometric radiation ripples,"),
                ("SC09_B4", "Nếu đôi mắt chúng ta cảm nhận được sóng vi ba,", "case_study", "normal",
                 "A human observer looking up in total wonder as the night sky blossoms into radiant warmth on #0B1026.",
                 "A human silhouette stands in wonder beneath an illuminated sky", None, "The observer silhouette looks up as invisible waves materialize in gentle harmony,"),
                ("SC09_B5", "cả màn đêm sẽ phát sáng rực rỡ", "case_study", "burst",
                 "A breathtaking, radiant full-screen vector panorama of the sky glowing like a warm golden and violet fireplace.",
                 "The entire night sky glows brilliantly like an ethereal cosmic aurora", None, "Waves of luminous cyan and violet cosmic light bathe the entire frame in gentle brilliance,"),
                ("SC09_B6", "bởi tàn dư của thuở khai sinh vũ trụ.", "case_study", "fast",
                 "The glowing light connecting back to the initial spark of creation, floating softly around mascot Tí Hon.",
                 "Tàn dư of the Big Bang surrounds Tí Hon in peaceful cosmic harmony", None, "Gentle starlight embers swirl in orbital harmony around Tí Hon,"),
            ]
        ),

        # Scene 10: Editorial Commentary 2 (68 words)
        (
            "SC10",
            "Lời bình triết học: màn đêm chính là bằng chứng Big Bang",
            "Triển khai bước 10: lời bình triết học: màn đêm chính là bằng chứng Big Bang",
            "Tí Hon nhìn xuống Trái Đất được bao bọc bởi bóng đêm che chở, đúc kết giá trị sinh mệnh của bóng tối.",
            "Trái Đất hình học màu lam ngọc yên bình trôi giữa màn đêm che chở, tránh khỏi biển nhiệt bức xạ hủy diệt.",
            "Lượn vòng quanh Trái Đất với góc nhìn chiêm nghiệm.",
            "Đêm đen vì thế không phải là sự tĩnh lặng đơn thuần, mà là bằng chứng hùng hồn cho một vũ trụ sống động và đang tiến hóa. Nếu vũ trụ vô hạn và vĩnh cửu, chúng ta đã bị thiêu rụi bởi biển nhiệt năng lượng. Màn đêm bao bọc lấy Trái Đất là món quà che chở cho sự sống sinh sôi trên hành tinh xanh.",
            ["R10"],
            "editorial_commentary",
            "takeaway",
            "Chiêm nghiệm, cảm xúc, triết lý sâu sắc",
            [
                ("SC10_B1", "Đêm đen vì thế không phải là sự tĩnh lặng đơn thuần,", "editorial_commentary", "slow",
                 "Mascot Tí Hon gently holding a miniature glowing sphere of Earth against deep peaceful cosmic space #0B1026.",
                 "Tí Hon contemplates the profound gift of the dark night sky", "BẰNG CHỨNG BIG BANG", "Tí Hon hovers in calm stillness beside the serene blue sphere of Earth,"),
                ("SC10_B2", "mà là bằng chứng hùng hồn cho một vũ trụ sống động và đang tiến hóa.", "editorial_commentary", "slow",
                 "A majestic cosmic tree diagram showing the unfolding evolution of stars, galaxies and life over time.",
                 "Cosmic evolution diagram shows a living, developing universe", None, "The branches of the cosmic evolutionary tree unfold in graceful geometric arcs,"),
                ("SC10_B3", "Nếu vũ trụ vô hạn và vĩnh cửu, chúng ta đã bị thiêu rụi bởi biển nhiệt năng lượng.", "editorial_commentary", "normal",
                 "A stark conceptual illustration of an unbearable sea of boiling thermal energy avoided by cosmic physics.",
                 "Conceptual vision of extreme thermal radiation averted by nature", None, "Intense solar rays harmlessly fade into deep cool cosmic indigo outside Earth's shield,"),
                ("SC10_B4", "Màn đêm bao bọc lấy Trái Đất", "editorial_commentary", "slow",
                 "A protective indigo blanket of tranquil darkness softly surrounding the blue and green geometric Earth.",
                 "The peaceful dark cosmic blanket shelters our home planet", None, "A soft indigo atmosphere shield wraps peacefully around the globe,"),
                ("SC10_B5", "là món quà che chở", "editorial_commentary", "normal",
                 "Mascot Tí Hon smiling with its glowing cyan visor, watching over the fragile cradle of humanity.",
                 "Tí Hon watches protectively over the cradle of life", None, "Tí Hon dips its wings gently as city lights twinkle softly across the dark continents,"),
                ("SC10_B6", "cho sự sống sinh sôi trên hành tinh xanh.", "editorial_commentary", "slow",
                 "Flourishing minimalist vector nature silhouettes (green sprout, ocean wave) thriving under the starry night sky.",
                 "Life blossoms serenely beneath the peaceful dark starry canopy", None, "Geometric plant fronds and ocean ripples sway gently under the quiet night sky,"),
            ]
        ),

        # Scene 11: Outro & Closing CTA (59 words)
        (
            "SC11",
            "Đúc kết giá trị và kết nối cộng đồng yêu thiên văn",
            "Triển khai bước 11: đúc kết giá trị và kết nối cộng đồng yêu thiên văn",
            "Tí Hon vẫy chào người xem, hướng kính thiên văn về những chân trời mới và gửi lời mời thảo luận.",
            "Không gian vũ trụ rộng mở với logo kênh Vũ Trụ Tí Hon và các hành tinh hình học tươi sáng trên nền #0B1026.",
            "Lùi dần về toàn cảnh kết thúc với endcard ấm áp.",
            "Mỗi câu hỏi ngây thơ khi ngắm nhìn vòm trời đều dẫn chúng ta chạm tới những định luật sâu xa của thực tại. Làm chủ khoa học là học cách kinh ngạc trước những điều tưởng chừng quen thuộc. Bạn nghĩ điều gì ngoài không gian sâu thẳm đáng kinh ngạc nhất, hãy chia sẻ bên dưới nhé.",
            ["R11"],
            "outro",
            "closing",
            "Ấm áp, truyền cảm hứng, gắn kết cộng đồng",
            [
                ("SC11_B1", "Mỗi câu hỏi ngây thơ khi ngắm nhìn vòm trời", "outro", "normal",
                 "A child icon gazing through a small telescope beside mascot Tí Hon on #0B1026 canvas.",
                 "Innocent curiosity unites humans and mascot Tí Hon", None, "The telescope lens glints with starlight as Tí Hon points toward a friendly crescent moon,"),
                ("SC11_B2", "đều dẫn chúng ta chạm tới những định luật sâu xa của thực tại.", "outro", "fast",
                 "The telescope beam connecting seamlessly to the fundamental mathematical formulas of astrophysics in vector art.",
                 "Childlike wonder unlocks profound laws of astrophysics", None, "A beam of light translates into elegant glowing physics geometry,"),
                ("SC11_B3", "Làm chủ khoa học là học cách kinh ngạc trước những điều tưởng chừng quen thuộc.", "outro", "normal",
                 "Mascot Tí Hon opening its arms wide in joyful celebration of cosmic curiosity, Kurzgesagt aesthetic.",
                 "Tí Hon celebrates the joy of scientific wonder and discovery", None, "Tí Hon performs a cheerful mid-air twirl with thruster flares glowing brightly,"),
                ("SC11_B4", "Bạn nghĩ điều gì ngoài không gian sâu thẳm đáng kinh ngạc nhất,", "outro", "slow",
                 "An intriguing open loop visual showing various cosmic wonders: black hole, neutron star, pulsar.",
                 "Tí Hon presents multiple cosmic mysteries for viewer reflection", None, "Stylized icons of a black hole, nebula and pulsar rotate gently on display pedestals,"),
                ("SC11_B5", "hãy chia sẻ bên dưới nhé.", "outro", "hold",
                 "A friendly vector comment bubble with glowing starlight icon beside mascot Tí Hon, inviting discussion.",
                 "Discussion prompt bubble appears inviting viewer comments", "VŨ TRỤ TÍ HON", "A minimalist glowing speech bubble manifests with gentle pulse,"),
                ("SC11_B6", "Bạn nghĩ điều gì ngoài không gian sâu thẳm đáng kinh ngạc nhất, hãy chia sẻ bên dưới nhé.", "outro", "hold",
                 "Official endcard screen for Vũ Trụ Tí Hon: mascot probe Tí Hon waving warmly beside the channel emblem on deep indigo #0B1026.",
                 "Official endcard screen with mascot Tí Hon waving beside channel branding", None, "Tí Hon hovers warmly with a friendly wave against the signature channel emblem,",
                 "hold", True),
            ]
        ),
    ]

    scenes: List[Dict[str, Any]] = []
    for sc_id, sc_title, sc_purpose, sc_action, sc_setting, sc_camera, sc_narr, sc_reqs, sc_sit, sc_phase, sc_tone, raw_beats in scenes_data:
        b_objs = []
        im_objs = []
        for b_tuple in raw_beats:
            b_id = b_tuple[0]
            quote = b_tuple[1]
            sit = b_tuple[2]
            tempo = b_tuple[3]
            desc = b_tuple[4]
            change = b_tuple[5]
            emph = b_tuple[6]
            motion = b_tuple[7]
            effect = b_tuple[8] if len(b_tuple) > 8 else "cut"
            is_end = b_tuple[9] if len(b_tuple) > 9 else False

            img_id = b_id.replace("_B", "_I")
            b_objs.append(make_beat_obj(b_id, img_id, f"Triển khai nhịp {b_id} cảnh {sc_id}", quote, sit, tempo, effect=effect, is_endcard=is_end))
            im_objs.append(make_image_obj(img_id, desc, change, quote, sit, tempo, emphasis_text=emph, motion_action=motion))

        scenes.append({
            "id": sc_id,
            "title": sc_title,
            "purpose": sc_purpose,
            "action": sc_action,
            "setting": sc_setting,
            "camera": sc_camera,
            "narration": sc_narr,
            "requirements": sc_reqs,
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "narrative_situation": sc_sit,
            "narrative_phase": sc_phase,
            "tone": sc_tone,
            "layers": [],
            "beats": b_objs,
            "images": im_objs,
        })

    brief_hash = compute_brief_hash(brief)
    content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": brief_hash,
        "topic": topic,
        "duration": {
            "min_seconds": 600.0,
            "max_seconds": 900.0,
        },
        "style": ch.visual.style_description,
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": [CH01_DEF],
        "scenes": scenes,
        "coverage": [
            {"requirement_id": "R01", "scene_id": "SC01", "quote": "Đêm khuya thanh vắng, ngước nhìn vòm trời sao"},
            {"requirement_id": "R02", "scene_id": "SC02", "quote": "Nhiều thế kỷ trước, Isaac Newton và các học giả tin rằng vũ trụ là một khối vô tận"},
            {"requirement_id": "R03", "scene_id": "SC03", "quote": "Năm 1823, nhà thiên văn Heinrich Olbers đúc kết bài toán thành nghịch lý nổi tiếng"},
            {"requirement_id": "R04", "scene_id": "SC04", "quote": "Về mặt toán học hình học, năng lượng ánh sáng của ngôi sao giảm"},
            {"requirement_id": "R05", "scene_id": "SC05", "quote": "Thời kỳ đầu, các nhà khoa học giả định rằng bụi vũ trụ đã chặn đứng ánh sáng"},
            {"requirement_id": "R06", "scene_id": "SC06", "quote": "Nhìn nhận từ phương pháp luận, sai lầm lớn nhất là áp đặt sự vĩnh cửu"},
            {"requirement_id": "R07", "scene_id": "SC07", "quote": "Chân lý đầu tiên được Edgar Allan Poe và các nhà thiên văn hé lộ"},
            {"requirement_id": "R08", "scene_id": "SC08", "quote": "Chân lý thứ hai được Edwin Hubble chứng minh qua sự giãn nở không gian"},
            {"requirement_id": "R09", "scene_id": "SC09", "quote": "Điều đó đồng nghĩa bầu trời thực ra không hề tối đen"},
            {"requirement_id": "R10", "scene_id": "SC10", "quote": "Đêm đen vì thế không phải là sự tĩnh lặng đơn thuần"},
            {"requirement_id": "R11", "scene_id": "SC11", "quote": "Mỗi câu hỏi ngây thơ khi ngắm nhìn vòm trời"},
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC07",
                "quote": "Khoảng mười ba phẩy tám tỷ năm trước, vụ nổ Big Bang mới diễn ra",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Vụ nổ Big Bang diễn ra cách đây xấp xỉ 13.8 tỷ năm.",
            }
        ],
        "revision_response": [],
        "open_questions": [],
    }

    return cr, brief, outline, content


def main() -> None:
    runs_dir = SYS_DIR / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    # 1. Build Short 9x16
    short_dir = runs_dir / "vu-tru-ti-hon-batch3-9x16"
    short_dir.mkdir(parents=True, exist_ok=True)
    cr_s, brief_s, outline_s, content_s = build_short_9x16()

    with open(short_dir / "competitor_research.json", "w", encoding="utf-8") as f:
        json.dump(cr_s, f, indent=2, ensure_ascii=False)
    with open(short_dir / "brief.json", "w", encoding="utf-8") as f:
        json.dump(brief_s, f, indent=2, ensure_ascii=False)
    with open(short_dir / "outline.json", "w", encoding="utf-8") as f:
        json.dump(outline_s, f, indent=2, ensure_ascii=False)
    with open(short_dir / "content.json", "w", encoding="utf-8") as f:
        json.dump(content_s, f, indent=2, ensure_ascii=False)
    print(f"[+] Short 9x16 artifacts saved to {short_dir}")

    # 2. Build Long 16x9
    long_dir = runs_dir / "vu-tru-ti-hon-batch3-16x9"
    long_dir.mkdir(parents=True, exist_ok=True)
    cr_l, brief_l, outline_l, content_l = build_long_16x9()

    with open(long_dir / "competitor_research.json", "w", encoding="utf-8") as f:
        json.dump(cr_l, f, indent=2, ensure_ascii=False)
    with open(long_dir / "brief.json", "w", encoding="utf-8") as f:
        json.dump(brief_l, f, indent=2, ensure_ascii=False)
    with open(long_dir / "outline.json", "w", encoding="utf-8") as f:
        json.dump(outline_l, f, indent=2, ensure_ascii=False)
    with open(long_dir / "content.json", "w", encoding="utf-8") as f:
        json.dump(content_l, f, indent=2, ensure_ascii=False)
    print(f"[+] Long 16x9 artifacts saved to {long_dir}")


if __name__ == "__main__":
    main()
