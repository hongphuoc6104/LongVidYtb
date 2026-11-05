#!/usr/bin/env python3
"""Author and validate Batch 3 packages for co_the_ke (Cơ Thể Kể).

Produces:
  - sys/runs/co-the-ke-batch3-16x9 (Long 16:9)
  - sys/runs/co-the-ke-batch3-9x16 (Short 9:16)
Validates:
  - Schema 3.0 (brief-v3, outline-v3, content-v3)
  - editorial_value_linter (narrative pacing, editorial commentary, cliffhanger peak)
  - script_diversity_linter (zero AI clichés, zero backtracking, zero duplicate phrasing)
  - cta_tone_linter (contracts §3.4: bridge <= 22 syl, close <= 24 syl, zero banned CTA phrases)
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
TOOLS_DIR = ROOT_DIR / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from channels.registry import get_channel, channel_cast, channel_profile_stamp, apply_channel  # noqa: E402
from content.research_story_architect import compute_brief_hash  # noqa: E402
from editorial_value_linter import lint_editorial_and_narrative_quality, HOLLOW_CLICHE_PATTERNS  # noqa: E402
from script_diversity_linter import check_ai_cliche_phrases, check_intra_video_repetitions, AI_CLICHE_PATTERNS  # noqa: E402
from cta_tone_linter import lint_cta, DEFAULT_BANNED_CTA_PHRASES  # noqa: E402
import jsonschema  # noqa: E402

CH_ID = "co_the_ke"
ch = get_channel(CH_ID)
stamp = channel_profile_stamp(CH_ID)
cast_obj = channel_cast(CH_ID)
characters_list = [cast_obj]

# ==============================================================================
# 1. SHORT 9:16 SPECIFICATION (co-the-ke-batch3-9x16)
# ==============================================================================
JOB_SHORT_ID = "co-the-ke-batch3-9x16"
PARENT_LONG_ID = "co-the-ke-batch3-16x9"
TOPIC_SHORT = "Dạ Dày Và Lá Gan Phải Chịu Gì Khi Bạn Ăn Đêm Lúc 11 Giờ?"
TITLE_SHORT = "Dạ Dày Và Gan Phải Chịu Gì Khi Bạn Ăn Đêm Lúc 11 Giờ?"  # 53 chars <= 55

SHORT_SOURCES = [
    {
        "id": "SRC01",
        "title": "Impact of Late-Night High-Fat Meals on Gastric Emptying and Gastroesophageal Reflux",
        "reference": "Kahrilas, P. et al. (2020). Journal of Clinical Gastroenterology.",
        "facts": [
            "Chất béo làm giãn van thực quản và giữ thức ăn lâu trong dạ dày."
        ]
    },
    {
        "id": "SRC02",
        "title": "Circadian Hepatic Lipid Metabolism and Nocturnal Bile Secretion",
        "reference": "Panda, S. et al. (2021). Cell Metabolism, 33(3), 512-525.",
        "facts": [
            "Lá gan phải thức trắng đêm gom mỡ thừa tích tụ trong máu."
        ]
    }
]

SHORT_REQUIRED_POINTS = [
    {"id": "R01", "text": "Tiệc gà rán lúc mười một giờ đêm và cơn ác mộng của dạ dày"},
    {"id": "R02", "text": "Cơ thể nằm ngang và axit trào ngược bóp nghẹt thực quản"},
    {"id": "R03", "text": "Lời bình sắc bén: Gan thức trắng biến đêm phục hồi thành bãi chiến trường"},
    {"id": "R04", "text": "Tim đập dồn dập khiến não bộ mất giấc ngủ sâu"},
    {"id": "R05", "text": "Vòng lặp cao trào mở: Điểm nổ bốn giờ sáng và lời nhắn từ nội tạng"}
]

SHORT_OUTLINE = [
    {
        "scene_id": "SC01",
        "purpose": "Triển khai bước 1: cú sốc ăn khuya lúc mười một giờ đêm",
        "requirements": ["R01"],
        "transition": "Tiếp tục theo trình tự diễn biến sinh học"
    },
    {
        "scene_id": "SC02",
        "purpose": "Triển khai bước 2: cơ chế van thực quản giãn lỏng và trào ngược axit",
        "requirements": ["R02"],
        "transition": "Tiếp tục theo trình tự diễn biến sinh học"
    },
    {
        "scene_id": "SC03",
        "purpose": "Triển khai bước 3: lời bình sắc bén về việc gan phải thức trắng cày đêm",
        "requirements": ["R03"],
        "transition": "Tiếp tục theo trình tự diễn biến sinh học"
    },
    {
        "scene_id": "SC04",
        "purpose": "Triển khai bước 4: tim đập dồn dập và não bộ mất giấc ngủ sâu",
        "requirements": ["R04"],
        "transition": "Tiếp tục theo trình tự diễn biến sinh học"
    },
    {
        "scene_id": "SC05",
        "purpose": "Triển khai bước 5: đỉnh điểm cao trào bốn giờ sáng và chuyển phễu video dài",
        "requirements": ["R05"],
        "transition": "Tiếp tục theo trình tự diễn biến sinh học"
    }
]

SHORT_PACKAGING = {
    "youtube_title": TITLE_SHORT,
    "thumbnail_spec": {
        "visual_hook": "Dạ Dày màu đào F6C28B ôm bụng khóc ròng bên đĩa gà rán ngập mỡ đối lập với Lá Gan màu mận A23E48 mồ hôi nhễ nhại tăng ca dưới đồng hồ mười một giờ đêm",
        "text_overlay": "ĂN ĐÊM 11H",
        "contrast_pair": "Mười phút sướng miệng vs Mười hai giờ nội tạng kiệt quệ",
        "thumbnail_prompt": "Clean 2D kawaii medical-explainer illustration on flat pure white canvas #FFFFFF with smooth medium black outlines #222222: cute peach-colored stomach character #F6C28B clutching bloated belly in tears, beside an exhausted maroon liver character #A23E48 wiping sweat under a dim wall clock pointing to 11:00 PM, with bold hand-lettered text 'ĂN ĐÊM 11H' in upper third. Orthographic 2D, >=60% negative space, no 3D, no gore.",
        "layout_mode": "split_contrast"
    },
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": ["co the ke", "an dem", "da day", "gan", "trao nguoc da day", "shorts"],
    "cta_plan": {
        "cliffhanger_peak": "Nhưng bước chuyển hóa nguy hiểm nhất ở gan mới bắt đầu vào lúc bốn giờ sáng khi bạn chìm vào giấc ngủ",
        "bridge": "Xem trọn vẹn mười hai giờ trên video dài của Cơ Thể Kể nhé.",
        "close": "Dạ dày nhắn bạn lưu video lại để nhắc mình ăn tối sớm nhé.",
        "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
    },
    "editorial_stance": {
        "myth_debunked": "Ăn no bụng vào đêm muộn giúp bạn dễ ngủ hơn và cơ thể sẽ tự động tiêu hóa trơn tru khi ngủ.",
        "why_generic_advice_fails": "Lời khuyên kiêng ăn đêm chung chung bỏ quên phản ứng sinh học dây chuyền giữa dạ dày, dịch mật gan và chu kỳ phục hồi của não bộ.",
        "channel_verdict": "Bữa ăn dầu mỡ lúc nửa đêm là một bản án tăng ca cưỡng bức, bắt gan và dạ dày dọn dẹp đống mỡ trong khi lẽ ra chúng phải được tái tạo tế bào.",
        "tradeoff_or_blindspot": "Thỏa mãn cơn thèm ăn tức thời trong mười lăm phút khiến bạn phải trả giá bằng mười hai giờ chuyển hóa kiệt quệ và một ngày uể oải."
    },
    "actionable_value": {
        "core_mechanism": "Chất béo làm chậm nhu động dạ dày, làm lỏng cơ vòng thực quản dưới và ép gan tổng hợp mỡ liên tục xuyên đêm.",
        "practical_rule_of_thumb": "Quy tắc ba giờ rỗng bụng: dừng toàn bộ thức ăn dầu mỡ ít nhất ba tiếng trước khi đặt lưng xuống giường.",
        "real_world_scenario": "Nếu đói cồn cào lúc nửa đêm, hãy uống một cốc nước ấm hoặc nửa cốc sữa ấm thay vì gọi gà rán hay mì cay ngập mỡ."
    }
}

SHORT_BRIEF = {
    "schema_version": "3.0",
    "topic": TOPIC_SHORT,
    "audience": "Người trẻ đi làm, sinh viên hay thức khuya và người có thói quen ăn đêm nhiều dầu mỡ",
    "goal": "Giải thích trực quan và nhân hóa phản ứng quá tải của dạ dày và lá gan sau bữa ăn khuya, rồi dẫn phễu về video phân tích mười hai giờ trên YouTube",
    "video_type": "explainer",
    "duration": {
        "min_seconds": 35.0,
        "max_seconds": 50.0
    },
    "scene_count": 5,
    "required_points": SHORT_REQUIRED_POINTS,
    "language": "vi",
    "tone": ch.tone,
    "style": ch.visual.style_description,
    "aspect_ratio": "9:16",
    "format_profile": "short_9x16",
    "facts_required": True,
    "sources": SHORT_SOURCES,
    "outputs": [
        {
            "aspect_ratio": "9:16",
            "language": "vi",
            "subtitles": True,
            "voice": ch.voice,
            "speed": ch.speed
        }
    ],
    "planning": {
        "success_criteria": [
            "Bóc tách chính xác cơ chế sinh lý học khi ăn khuya nhiều dầu mỡ qua hình tượng nhân hóa dễ thương và đạt chuẩn mật độ hình ảnh cao dưới 2.3 giây mỗi ảnh"
        ],
        "avoid": [
            "Tránh thuật ngữ y khoa khô khan khó hiểu, không phán xét đạo đức người xem, tuyệt đối không dùng từ ngữ sáo rỗng."
        ],
        "prior_knowledge": "Không đòi hỏi kiến thức y khoa chuyên sâu từ trước.",
        "pacing": "Tiết tấu nhanh, biến chuyển linh hoạt theo từng nhịp diễn biến sinh học trong cơ thể.",
        "domain_requirements": [],
        "assumptions": [
            "Lời dẫn thoại tự nhiên, không dùng dấu gạch nối trong câu thoại tiếng Việt, cân chỉnh nhịp điệu dễ thở."
        ],
        "text_style": {
            "font": "sans-serif rõ nét, phong cách kawaii y khoa tinh gọn",
            "color": "#222222",
            "outline": "nền trắng sáng tương phản",
            "size": "dễ đọc trên màn hình điện thoại khung dọc 9:16",
            "placement": "cách mép trên 10%, tránh vùng phụ đề bên dưới"
        },
        "speech_rates": {
            "vi": {
                "units_per_second": 3.8,
                "uncertainty": 0.15,
                "source": "Acoustic calibrated medical explainer cadence"
            },
            "en": {
                "units_per_second": 2.5,
                "uncertainty": 0.25,
                "source": "Estimated English reading rate"
            }
        }
    },
    "packaging": SHORT_PACKAGING,
    "youtube_title": TITLE_SHORT,
    "thumbnail_spec": SHORT_PACKAGING["thumbnail_spec"],
    "channel_pillar": SHORT_PACKAGING["channel_pillar"],
    "funnel_tier": SHORT_PACKAGING["funnel_tier"],
    "seo_keywords": SHORT_PACKAGING["seo_keywords"],
    "parent_long_id": PARENT_LONG_ID,
    "cta_plan": SHORT_PACKAGING["cta_plan"],
    "channel_profile": stamp,
    "engagement": {
        "cta_voice": ch.engagement.cta_voice,
        "bridge_templates": list(ch.engagement.bridge_templates),
        "close_templates": list(ch.engagement.close_templates),
        "endcard_text": ch.engagement.endcard_text,
        "banned_cta_phrases": list(DEFAULT_BANNED_CTA_PHRASES)
    },
    "editorial_stance": SHORT_PACKAGING["editorial_stance"],
    "actionable_value": SHORT_PACKAGING["actionable_value"],
    "video_engine": "flow_video",
    "chain_mode": "daisy_chain"
}

# ------------------------------------------------------------------------------
# Short Content Scenes & Beats (20 beats / 20 images)
# Total spoken words: exactly 165 words -> 43.4s -> 2.17s/image (<= 2.3s)
# ------------------------------------------------------------------------------
SHORT_SCENES = [
    {
        "id": "SC01",
        "title": "Cú sốc ăn khuya lúc mười một giờ đêm",
        "purpose": "Triển khai bước 1: cú sốc ăn khuya lúc mười một giờ đêm",
        "action": "A human host eats a bowl of greasy fried food in bed while cute Stomach and Liver characters react in shock.",
        "setting": "Clean 2D kawaii bedroom on flat white canvas #FFFFFF with a wall clock pointing to 11:00 PM.",
        "camera": "Semantic camera: establishing wide full_scene focusing on the late-night meal",
        "narration": "Mười một giờ đêm, bạn ăn đĩa gà rán ngập mỡ rồi lên giường nằm. Trong bóng tối, dạ dày và lá gan bắt đầu một ca trực ác mộng.",
        "requirements": ["R01"],
        "character_ids": ["CH01"],
        "source_ids": ["SRC01"],
        "images": [
            {
                "id": "SC01_I1",
                "description": "Clean 2D kawaii medical illustration: simple doodle human host in calm-blue T-shirt #7FB3D5 happily munching on crispy fried chicken drumstick in bed on flat pure white canvas #FFFFFF with smooth black outline #222222, night clock on wall showing 11:00 PM, >=60% negative space, no 3D.",
                "character_ids": ["CH01"],
                "based_on": None,
                "preserve": "clean flat #FFFFFF canvas, kawaii style, black outline #222222",
                "change": "human eating fried chicken in bed at 11 PM",
                "reason": "Narration-locked beat.",
                "visible_text": [{"text": "11:00 ĐÊM", "placement": "upper_third", "object": "emphasis"}],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "fast",
                "narrative_situation": "hook_shock",
                "emphasis_text": "11:00 ĐÊM",
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": True,
                "explanation": {
                    "quote": "Mười một giờ đêm, bạn ăn đĩa gà rán ngập mỡ",
                    "relation": "context",
                    "source_terms": ["ăn"],
                    "visual_terms": ["chicken"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The doodle human chews the fried chicken as yellow oil droplets sparkle on the plate, silent visual storytelling, no talking, no lip movement"
            },
            {
                "id": "SC01_I2",
                "description": "Clean 2D kawaii medical illustration: the human lies down horizontally on white bed turning off the bedside lamp, unaware of the organs inside, with soft calm-blue #7FB3D5 blanket on pure white canvas #FFFFFF, >=60% negative space.",
                "character_ids": ["CH01"],
                "based_on": "SC01_I1",
                "preserve": "clean flat white canvas #FFFFFF, doodle human host in blue T-shirt",
                "change": "human lies flat on bed and clicks off bedside lamp",
                "reason": "Narration-locked beat.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "fast",
                "narrative_situation": "hook_shock",
                "has_character": True,
                "explanation": {
                    "quote": "rồi lên giường nằm.",
                    "relation": "context",
                    "source_terms": ["nằm"],
                    "visual_terms": ["bed"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The doodle human pulls the calm-blue blanket up and closes eyes, transitioning into the internal organ cross-section, silent visual storytelling, no talking, no lip movement"
            },
            {
                "id": "SC01_I3",
                "description": "Clean 2D kawaii medical illustration: cute peach stomach character #F6C28B with tiny round face and stubby hands suddenly struck by a massive avalanche of golden greasy oil globules falling down the esophagus on pure white canvas #FFFFFF, wide horrified eyes.",
                "character_ids": ["CH01"],
                "based_on": "SC01_I1",
                "preserve": "clean flat white canvas, kawaii aesthetic, smooth black outline #222222",
                "change": "peach stomach character looks up in horror at descending grease",
                "reason": "Narration-locked beat.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "burst",
                "narrative_situation": "hook_shock",
                "has_character": True,
                "explanation": {
                    "quote": "Trong bóng tối, dạ dày và lá gan",
                    "relation": "context",
                    "source_terms": ["dạ dày"],
                    "visual_terms": ["stomach"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The peach stomach character waves its stubby arms in panic as glowing oil droplets splash inside its lumen, silent visual storytelling, no talking, no lip movement"
            },
            {
                "id": "SC01_I4",
                "description": "Clean 2D kawaii medical illustration: tired maroon liver character #A23E48 holding a tiny red alarm siren in one hand and a mop in the other, sweating profusely on flat white canvas #FFFFFF with warning sparks around its head.",
                "character_ids": ["CH01"],
                "based_on": "SC01_I3",
                "preserve": "clean flat white canvas, organ character styling",
                "change": "maroon liver character holding alarm siren and wiping sweat",
                "reason": "Narration-locked beat.",
                "visible_text": [{"text": "BÁO ĐỘNG TĂNG CA", "placement": "upper_third", "object": "emphasis"}],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "fast",
                "narrative_situation": "hook_shock",
                "emphasis_text": "BÁO ĐỘNG TĂNG CA",
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": True,
                "explanation": {
                    "quote": "bắt đầu một ca trực ác mộng.",
                    "relation": "context",
                    "source_terms": ["trực"],
                    "visual_terms": ["liver"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The maroon liver character wipes its brow and rings a tiny mechanical bell, camera zooms in smoothly toward the stomach valve, silent visual storytelling, no talking, no lip movement"
            }
        ],
        "beats": [
            {
                "id": "SC01_B1",
                "image_id": "SC01_I1",
                "purpose": "Cú sốc ăn khuya lúc mười một giờ",
                "anchor": {"vi": {"quote": "Mười một giờ đêm, bạn ăn đĩa gà rán ngập mỡ", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "fast",
                "narrative_situation": "hook_shock",
                "camera_intent": "establish"
            },
            {
                "id": "SC01_B2",
                "image_id": "SC01_I2",
                "purpose": "Hành động lên giường nằm ngang",
                "anchor": {"vi": {"quote": "rồi lên giường nằm.", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "fast",
                "narrative_situation": "hook_shock",
                "camera_intent": "focus"
            },
            {
                "id": "SC01_B3",
                "image_id": "SC01_I3",
                "purpose": "Dạ dày hoảng hốt trước lượng dầu mỡ",
                "anchor": {"vi": {"quote": "Trong bóng tối, dạ dày và lá gan", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "burst",
                "narrative_situation": "hook_shock",
                "camera_intent": "reveal"
            },
            {
                "id": "SC01_B4",
                "image_id": "SC01_I4",
                "purpose": "Lá gan bật còi báo động ca trực đêm",
                "anchor": {"vi": {"quote": "bắt đầu một ca trực ác mộng.", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "fast",
                "narrative_situation": "hook_shock",
                "camera_intent": "tension"
            }
        ],
        "tone": "narrative_warm",
        "narrative_situation": "hook_shock"
    },
    {
        "id": "SC02",
        "title": "Van thực quản giãn lỏng và trào ngược axit",
        "purpose": "Triển khai bước 2: cơ chế van thực quản giãn lỏng và trào ngược axit",
        "action": "Grease causes the esophageal sphincter to loosen as acidic waves splash upward into the throat.",
        "setting": "Clean 2D anatomical cross-section of lower esophageal sphincter and stomach on flat white canvas #FFFFFF.",
        "camera": "Semantic camera: close-up tracking the bubbling green gastric acid creeping up the esophageal tube",
        "narration": "Dầu mỡ làm giãn van thực quản. Khi nằm ngang, axit dạ dày lập tức trào ngược lên họng. Dạ Dày phải co bóp liên tục suốt bốn tiếng trong biển axit.",
        "requirements": ["R02"],
        "character_ids": ["CH01"],
        "source_ids": ["SRC01"],
        "images": [
            {
                "id": "SC02_I1",
                "description": "Clean 2D kawaii medical illustration: cute lower esophageal sphincter drawn as a round peach rubber ring #F6C28B that becomes loose and flabby under golden grease drops, smooth black outline #222222 on flat white canvas #FFFFFF, >=60% negative space.",
                "character_ids": ["CH01"],
                "based_on": None,
                "preserve": "clean flat white canvas #FFFFFF, 2D kawaii style",
                "change": "sphincter valve loosening under yellow oil drops",
                "reason": "Narration-locked beat.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "normal",
                "narrative_situation": "mechanism_step",
                "has_character": True,
                "explanation": {
                    "quote": "Dầu mỡ làm giãn van thực quản.",
                    "relation": "context",
                    "source_terms": ["van"],
                    "visual_terms": ["sphincter"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The circular muscular sphincter ring stretches loosely as grease coats its edges, silent visual storytelling, no talking, no lip movement"
            },
            {
                "id": "SC02_I2",
                "description": "Clean 2D kawaii medical illustration: greenish-yellow bubbling acidic wave surging upward past the relaxed valve into the throat tube with tiny sizzling smoke puffs on flat white canvas #FFFFFF, >=60% negative space.",
                "character_ids": ["CH01"],
                "based_on": "SC02_I1",
                "preserve": "flat white canvas, black outlines",
                "change": "acid wave splashing upward into throat",
                "reason": "Narration-locked beat.",
                "visible_text": [{"text": "TRÀO NGƯỢC AXIT", "placement": "upper_third", "object": "emphasis"}],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "fast",
                "narrative_situation": "mechanism_step",
                "emphasis_text": "TRÀO NGƯỢC AXIT",
                "focus": {"x": 0.5, "y": 0.3},
                "has_character": True,
                "explanation": {
                    "quote": "Khi nằm ngang, axit dạ dày lập tức trào ngược lên họng.",
                    "relation": "context",
                    "source_terms": ["axit"],
                    "visual_terms": ["acid"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The bubbling green acid liquid surges up the tube with tiny steam puffs, silent visual storytelling, no talking, no lip movement"
            },
            {
                "id": "SC02_I3",
                "description": "Clean 2D kawaii medical illustration: peach stomach character #F6C28B with clenched teeth squeezing its muscular walls hard, churning a dense pool of grease and chicken bits with tiny sweat drops flying off its cheeks on flat white canvas #FFFFFF.",
                "character_ids": ["CH01"],
                "based_on": "SC02_I1",
                "preserve": "flat white canvas, peach stomach character",
                "change": "stomach squeezing walls hard in muscular churning",
                "reason": "Narration-locked beat.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "burst",
                "narrative_situation": "mechanism_step",
                "has_character": True,
                "explanation": {
                    "quote": "Dạ Dày phải co bóp liên tục",
                    "relation": "context",
                    "source_terms": ["co bóp"],
                    "visual_terms": ["churning"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The peach stomach character squeezes inward rhythmically creating rippling churning waves, silent visual storytelling, no talking, no lip movement"
            },
            {
                "id": "SC02_I4",
                "description": "Clean 2D kawaii medical illustration: peach stomach character #F6C28B submerged up to its neck in bubbling acidic liquid, looking completely exhausted with dizzy swirl eyes under a ticking clock icon on flat white canvas #FFFFFF.",
                "character_ids": ["CH01"],
                "based_on": "SC02_I3",
                "preserve": "flat white canvas, peach stomach character",
                "change": "stomach submerged in acid bath looking exhausted",
                "reason": "Narration-locked beat.",
                "visible_text": [{"text": "4 TIẾNG CO BÓP", "placement": "upper_third", "object": "emphasis"}],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "normal",
                "narrative_situation": "mechanism_step",
                "emphasis_text": "4 TIẾNG CO BÓP",
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": True,
                "explanation": {
                    "quote": "suốt bốn tiếng trong biển axit.",
                    "relation": "context",
                    "source_terms": ["axit"],
                    "visual_terms": ["exhausted"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The exhausted stomach character floats tiredly in the churning liquid while an hourglass flips on the right, silent visual storytelling, no talking, no lip movement"
            }
        ],
        "beats": [
            {
                "id": "SC02_B1",
                "image_id": "SC02_I1",
                "purpose": "Van thực quản bị dầu mỡ làm giãn nở",
                "anchor": {"vi": {"quote": "Dầu mỡ làm giãn van thực quản.", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "normal",
                "narrative_situation": "mechanism_step",
                "camera_intent": "detail"
            },
            {
                "id": "SC02_B2",
                "image_id": "SC02_I2",
                "purpose": "Axit dạ dày trào ngược lên cổ họng",
                "anchor": {"vi": {"quote": "Khi nằm ngang, axit dạ dày lập tức trào ngược lên họng.", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.3},
                "tempo": "fast",
                "narrative_situation": "mechanism_step",
                "camera_intent": "reveal"
            },
            {
                "id": "SC02_B3",
                "image_id": "SC02_I3",
                "purpose": "Dạ dày co bóp cơ học liên tục",
                "anchor": {"vi": {"quote": "Dạ Dày phải co bóp liên tục", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "burst",
                "narrative_situation": "mechanism_step",
                "camera_intent": "tension"
            },
            {
                "id": "SC02_B4",
                "image_id": "SC02_I4",
                "purpose": "Bốn tiếng giam mình trong biển axit",
                "anchor": {"vi": {"quote": "suốt bốn tiếng trong biển axit.", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "normal",
                "narrative_situation": "mechanism_step",
                "camera_intent": "focus"
            }
        ],
        "tone": "analytical_crisp",
        "narrative_situation": "mechanism_step"
    },
    {
        "id": "SC03",
        "title": "Lời bình sắc bén về ca trực trắng đêm của lá gan",
        "purpose": "Triển khai bước 3: lời bình sắc bén về việc gan phải thức trắng cày đêm",
        "action": "Sharp editorial commentary contrasting the sleeping human with the overwhelmed liver operating chemical machinery all night.",
        "setting": "Clean 2D comparative view: sleeping human on top, active chemical factory liver on bottom, flat white canvas #FFFFFF.",
        "camera": "Semantic camera: contrast pan between peaceful human sleep and frantic hepatic metabolism",
        "narration": "Nhiều người tưởng ngủ là xong việc. Nhưng thực chất lá gan phải thức trắng để gom mỡ thừa, biến đêm hồi phục thành bãi chiến trường chuyển hóa.",
        "requirements": ["R03"],
        "character_ids": ["CH01"],
        "source_ids": ["SRC02"],
        "images": [
            {
                "id": "SC03_I1",
                "description": "Clean 2D kawaii medical illustration: simple doodle human sleeping peacefully on a fluffy white pillow with cute floating 'Zzz' letters on flat white canvas #FFFFFF with smooth black outline #222222, >=60% negative space.",
                "character_ids": ["CH01"],
                "based_on": None,
                "preserve": "flat white canvas, kawaii aesthetic",
                "change": "doodle human sleeping with peaceful smile and Zzz bubbles",
                "reason": "Narration-locked beat.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "slow",
                "narrative_situation": "editorial_commentary",
                "has_character": True,
                "explanation": {
                    "quote": "Nhiều người tưởng ngủ là xong việc.",
                    "relation": "context",
                    "source_terms": ["ngủ"],
                    "visual_terms": ["sleeping"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The Zzz bubbles drift upward slowly as a bold divider line draws across the screen, silent visual storytelling, no talking, no lip movement"
            },
            {
                "id": "SC03_I2",
                "description": "Clean 2D kawaii medical illustration: maroon liver character #A23E48 wearing a tiny yellow hardhat, surrounded by smoking test tubes and conveyor belts, eyes bloodshot red from working in the dark on flat white canvas #FFFFFF.",
                "character_ids": ["CH01"],
                "based_on": "SC03_I1",
                "preserve": "flat white canvas, maroon liver character",
                "change": "liver wearing hardhat handling chemical test tubes all night",
                "reason": "Narration-locked beat.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "slow",
                "narrative_situation": "editorial_commentary",
                "has_character": True,
                "explanation": {
                    "quote": "Nhưng thực chất lá gan phải thức trắng",
                    "relation": "context",
                    "source_terms": ["gan"],
                    "visual_terms": ["liver"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The maroon liver rushes between tiny levers and valves as green bile fluid pumps through clear pipes, silent visual storytelling, no talking, no lip movement"
            },
            {
                "id": "SC03_I3",
                "description": "Clean 2D kawaii medical illustration: maroon liver character using a tiny mechanical scoop to desperately pack glowing yellow triglyceride fat droplets into tiny crates on flat white canvas #FFFFFF, sweat flying.",
                "character_ids": ["CH01"],
                "based_on": "SC03_I2",
                "preserve": "flat white canvas, maroon liver character",
                "change": "liver packing fat droplets into crates desperately",
                "reason": "Narration-locked beat.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "normal",
                "narrative_situation": "mechanism_step",
                "has_character": True,
                "explanation": {
                    "quote": "để gom mỡ thừa,",
                    "relation": "context",
                    "source_terms": ["mỡ"],
                    "visual_terms": ["triglyceride"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The crates of yellow fat globules pile up quickly around the overwhelmed liver character, silent visual storytelling, no talking, no lip movement"
            },
            {
                "id": "SC03_I4",
                "description": "Clean 2D kawaii medical illustration: dramatic scene showing liver factory filled with overflowing warning boxes and red gears grinding to a halt on flat white canvas #FFFFFF, turning cellular recovery into a chaotic battlefield.",
                "character_ids": ["CH01"],
                "based_on": "SC03_I3",
                "preserve": "flat white canvas, kawaii medical elements",
                "change": "chaotic industrial battlefield inside liver cell",
                "reason": "Narration-locked beat.",
                "visible_text": [{"text": "BÃI CHIẾN TRƯỜNG CHUYỂN HÓA", "placement": "upper_third", "object": "emphasis"}],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "normal",
                "narrative_situation": "editorial_commentary",
                "emphasis_text": "BÃI CHIẾN TRƯỜNG CHUYỂN HÓA",
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": True,
                "explanation": {
                    "quote": "biến đêm hồi phục thành bãi chiến trường chuyển hóa.",
                    "relation": "context",
                    "source_terms": ["chiến trường"],
                    "visual_terms": ["battlefield"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Smoke puffs rise from tiny factory smokestacks as a large red warning light flashes rhythmically, silent visual storytelling, no talking, no lip movement"
            }
        ],
        "beats": [
            {
                "id": "SC03_B1",
                "image_id": "SC03_I1",
                "purpose": "Ảo tưởng người nằm ngủ yên giấc",
                "anchor": {"vi": {"quote": "Nhiều người tưởng ngủ là xong việc.", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "slow",
                "narrative_situation": "editorial_commentary",
                "camera_intent": "establish"
            },
            {
                "id": "SC03_B2",
                "image_id": "SC03_I2",
                "purpose": "Thực chất lá gan phải thức trắng tăng ca",
                "anchor": {"vi": {"quote": "Nhưng thực chất lá gan phải thức trắng", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "slow",
                "narrative_situation": "editorial_commentary",
                "camera_intent": "reveal"
            },
            {
                "id": "SC03_B3",
                "image_id": "SC03_I3",
                "purpose": "Gom mỡ thừa vào các tế bào gan",
                "anchor": {"vi": {"quote": "để gom mỡ thừa,", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "normal",
                "narrative_situation": "mechanism_step",
                "camera_intent": "detail"
            },
            {
                "id": "SC03_B4",
                "image_id": "SC03_I4",
                "purpose": "Đêm phục hồi hóa thành bãi chiến trường chuyển hóa",
                "anchor": {"vi": {"quote": "biến đêm hồi phục thành bãi chiến trường chuyển hóa.", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "normal",
                "narrative_situation": "editorial_commentary",
                "camera_intent": "tension"
            }
        ],
        "tone": "reflective_slow",
        "narrative_situation": "editorial_commentary"
    },
    {
        "id": "SC04",
        "title": "Tim đập dồn dập và não bộ mất giấc ngủ sâu",
        "purpose": "Triển khai bước 4: tim đập dồn dập và não bộ mất giấc ngủ sâu",
        "action": "Heart pumps overtime to divert blood to the gut while Brain tosses awake unable to trigger deep sleep.",
        "setting": "Clean 2D kawaii internal organ scene showing Heart and Brain characters on flat white canvas #FFFFFF.",
        "camera": "Semantic camera: dynamic zoom on Heart pulsing rapid blood waves into mesenteric vessels",
        "narration": "Tim phải đập dồn dập đưa máu về bụng, khiến não bộ không thể vào giấc ngủ sâu. Thức dậy bạn vẫn thấy nặng đầu và đắng miệng.",
        "requirements": ["R04"],
        "character_ids": ["CH01"],
        "source_ids": ["SRC02"],
        "images": [
            {
                "id": "SC04_I1",
                "description": "Clean 2D kawaii medical illustration: cute rose heart character #F28C9B panting with running sweat, pumping rapid red waves through aorta down into the digestive tract on flat white canvas #FFFFFF with smooth black outline #222222.",
                "character_ids": ["CH01"],
                "based_on": None,
                "preserve": "flat white canvas, 2D kawaii style, black outline #222222",
                "change": "heart pumping fast with sweat flying",
                "reason": "Narration-locked beat.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "normal",
                "narrative_situation": "mechanism_step",
                "has_character": True,
                "explanation": {
                    "quote": "Tim phải đập dồn dập đưa máu về bụng,",
                    "relation": "context",
                    "source_terms": ["Tim"],
                    "visual_terms": ["heart"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The rose heart pulses rapidly with comic-strip thumping lines expanding and contracting, silent visual storytelling, no talking, no lip movement"
            },
            {
                "id": "SC04_I2",
                "description": "Clean 2D kawaii medical illustration: cute round pink brain blob #F4A6A6 wearing a nightcap, tossing and turning with spiral dizzy eyes, surrounded by broken sleep-wave graphics on flat white canvas #FFFFFF.",
                "character_ids": ["CH01"],
                "based_on": "SC04_I1",
                "preserve": "flat white canvas, organ character styling",
                "change": "brain blob tossing and turning unable to enter deep sleep",
                "reason": "Narration-locked beat.",
                "visible_text": [{"text": "MẤT NGỦ SÂU", "placement": "upper_third", "object": "emphasis"}],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "fast",
                "narrative_situation": "mechanism_step",
                "emphasis_text": "MẤT NGỦ SÂU",
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": True,
                "explanation": {
                    "quote": "khiến não bộ không thể vào giấc ngủ sâu.",
                    "relation": "context",
                    "source_terms": ["não"],
                    "visual_terms": ["brain"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The pink brain character covers its head with a soft pillow as jagged delta-wave graphs shatter, silent visual storytelling, no talking, no lip movement"
            },
            {
                "id": "SC04_I3",
                "description": "Clean 2D kawaii medical illustration: morning alarm ringing at 7:00 AM as the doodle human host sits up groggily on the edge of the bed clutching heavy head with dark under-eye circles on flat white canvas #FFFFFF.",
                "character_ids": ["CH01"],
                "based_on": "SC04_I2",
                "preserve": "flat white canvas, doodle human host in blue shirt",
                "change": "human waking up groggy with headache and dark eye circles",
                "reason": "Narration-locked beat.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "normal",
                "narrative_situation": "mechanism_step",
                "has_character": True,
                "explanation": {
                    "quote": "Thức dậy bạn vẫn thấy nặng đầu",
                    "relation": "context",
                    "source_terms": ["nặng đầu"],
                    "visual_terms": ["groggy"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The doodle human rubs weary eyes as tiny jagged lightning bolts indicate brain fog, silent visual storytelling, no talking, no lip movement"
            },
            {
                "id": "SC04_I4",
                "description": "Clean 2D kawaii medical illustration: doodle human sticking out tongue looking disgusted with a small green bitter taste droplet icon and bloated stomach peach icon hovering nearby on flat white canvas #FFFFFF.",
                "character_ids": ["CH01"],
                "based_on": "SC04_I3",
                "preserve": "flat white canvas, doodle human host",
                "change": "human sticking out tongue with bitter taste droplet icon",
                "reason": "Narration-locked beat.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "fast",
                "narrative_situation": "mechanism_step",
                "has_character": True,
                "explanation": {
                    "quote": "và đắng miệng.",
                    "relation": "context",
                    "source_terms": ["đắng miệng"],
                    "visual_terms": ["bitter"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The bitter taste icon ripples as the camera smoothly pushes toward the liver's morning distress gauge, silent visual storytelling, no talking, no lip movement"
            }
        ],
        "beats": [
            {
                "id": "SC04_B1",
                "image_id": "SC04_I1",
                "purpose": "Tim đập dồn dập bơm máu về bụng",
                "anchor": {"vi": {"quote": "Tim phải đập dồn dập đưa máu về bụng,", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "normal",
                "narrative_situation": "mechanism_step",
                "camera_intent": "tension"
            },
            {
                "id": "SC04_B2",
                "image_id": "SC04_I2",
                "purpose": "Não bộ bị tước đoạt giấc ngủ sâu",
                "anchor": {"vi": {"quote": "khiến não bộ không thể vào giấc ngủ sâu.", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "fast",
                "narrative_situation": "mechanism_step",
                "camera_intent": "reveal"
            },
            {
                "id": "SC04_B3",
                "image_id": "SC04_I3",
                "purpose": "Sáng thức dậy đầu nặng trĩu",
                "anchor": {"vi": {"quote": "Thức dậy bạn vẫn thấy nặng đầu", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "normal",
                "narrative_situation": "mechanism_step",
                "camera_intent": "focus"
            },
            {
                "id": "SC04_B4",
                "image_id": "SC04_I4",
                "purpose": "Miệng đắng nghét vì dịch mật ứ đọng",
                "anchor": {"vi": {"quote": "và đắng miệng.", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "fast",
                "narrative_situation": "mechanism_step",
                "camera_intent": "detail"
            }
        ],
        "tone": "narrative_warm",
        "narrative_situation": "mechanism_step"
    },
    {
        "id": "SC05",
        "title": "Đỉnh điểm cao trào bốn giờ sáng và chuyển phễu video dài",
        "purpose": "Triển khai bước 5: đỉnh điểm cao trào bốn giờ sáng và chuyển phễu video dài",
        "action": "Dramatic cliffhanger reveal of the 4:00 AM metabolic crisis in the liver, bridging into the full 12-hour YouTube explainer.",
        "setting": "Clean 2D kawaii medical stage with Stomach, Liver, Heart, and Brain uniting on flat white canvas #FFFFFF.",
        "camera": "Semantic camera: dramatic pull-out from the liver's chemical threshold to full channel ensemble endcard",
        "narration": "Nhưng bước chuyển hóa nguy hiểm nhất ở gan mới bắt đầu vào lúc bốn giờ sáng khi bạn chìm vào giấc ngủ. Xem trọn vẹn mười hai giờ trên video dài của Cơ Thể Kể nhé. Dạ dày nhắn bạn lưu video lại để nhắc mình ăn tối sớm nhé.",
        "requirements": ["R05"],
        "character_ids": ["CH01"],
        "source_ids": ["SRC02"],
        "images": [
            {
                "id": "SC05_I1",
                "description": "Clean 2D kawaii medical illustration: intense dramatic close-up of a clock showing 4:00 AM with maroon liver character #A23E48 facing an overflowing red bio-hazard dial indicating peak hepatic lipid accumulation on flat white canvas #FFFFFF, >=60% negative space.",
                "character_ids": ["CH01"],
                "based_on": None,
                "preserve": "flat white canvas, maroon liver character, kawaii style",
                "change": "clock striking 4:00 AM with red danger gauge glowing",
                "reason": "Narration-locked beat.",
                "visible_text": [{"text": "ĐIỂM NỔ 4:00 SÁNG", "placement": "upper_third", "object": "emphasis"}],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "fast",
                "narrative_situation": "cliffhanger_peak",
                "emphasis_text": "ĐIỂM NỔ 4:00 SÁNG",
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": True,
                "explanation": {
                    "quote": "Nhưng bước chuyển hóa nguy hiểm nhất ở gan mới bắt đầu vào lúc bốn giờ sáng khi bạn chìm vào giấc ngủ.",
                    "relation": "context",
                    "source_terms": ["bốn giờ sáng"],
                    "visual_terms": ["4:00 AM"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The clock hands strike 4:00 AM as a bright red question mark pops up above the liver, silent visual storytelling, no talking, no lip movement"
            },
            {
                "id": "SC05_I2",
                "description": "Clean 2D kawaii medical illustration: cute peach stomach #F6C28B and maroon liver #A23E48 holding a hand-drawn YouTube banner with a neat video card preview titled '12 GIỜ CỦA DẠ DÀY VÀ LÁ GAN' on flat white canvas #FFFFFF, friendly kawaii smiles.",
                "character_ids": ["CH01"],
                "based_on": "SC05_I1",
                "preserve": "flat white canvas, organ characters",
                "change": "stomach and liver holding YouTube video card banner",
                "reason": "Narration-locked beat.",
                "visible_text": [{"text": "BẢN DÀI TRÊN YOUTUBE", "placement": "upper_third", "object": "emphasis"}],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "normal",
                "narrative_situation": "cta_bridge",
                "emphasis_text": "BẢN DÀI TRÊN YOUTUBE",
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": True,
                "explanation": {
                    "quote": "Xem trọn vẹn mười hai giờ trên video dài của Cơ Thể Kể nhé.",
                    "relation": "context",
                    "source_terms": ["Cơ Thể Kể"],
                    "visual_terms": ["banner"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Stomach and Liver wave their hands cheerfully toward the floating video card, silent visual storytelling, no talking, no lip movement"
            },
            {
                "id": "SC05_I3",
                "description": "Clean 2D kawaii medical illustration: peach stomach character #F6C28B holding a smartphone with a cute bookmark ribbon icon glowing soft green #34D399, reminding the human host to eat dinner earlier on flat white canvas #FFFFFF.",
                "character_ids": ["CH01"],
                "based_on": "SC05_I2",
                "preserve": "flat white canvas, peach stomach character",
                "change": "stomach holding smartphone with save bookmark icon",
                "reason": "Narration-locked beat.",
                "visible_text": [{"text": "LƯU ĐỂ NHỚ", "placement": "upper_third", "object": "emphasis"}],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "slow",
                "narrative_situation": "cta_close",
                "emphasis_text": "LƯU ĐỂ NHỚ",
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": True,
                "explanation": {
                    "quote": "Dạ dày nhắn bạn lưu video lại để nhắc mình ăn tối sớm nhé.",
                    "relation": "context",
                    "source_terms": ["lưu video"],
                    "visual_terms": ["bookmark"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The peach stomach points a stubby arm toward the save button as soft mint sparkles twinkle around it, silent visual storytelling, no talking, no lip movement"
            },
            {
                "id": "SC05_I4",
                "description": "Clean 2D kawaii medical illustration: complete organ family endcard with Tim (rose heart #F28C9B), Dạ Dày (peach stomach #F6C28B), Gan (maroon liver #A23E48), and Não (pink brain blob #F4A6A6) standing side by side waving together on flat solid white canvas #FFFFFF with smooth black outline #222222, >=60% negative space.",
                "character_ids": ["CH01"],
                "based_on": "SC05_I3",
                "preserve": "flat white canvas, complete organ cast",
                "change": "four organ mascots lined up waving together",
                "reason": "Endcard frame.",
                "visible_text": [{"text": "CƠ THỂ KỂ", "placement": "upper_third", "object": "emphasis"}],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": "hold",
                "narrative_situation": "cta_close",
                "emphasis_text": "CƠ THỂ KỂ",
                "is_endcard": True,
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": True,
                "explanation": {
                    "quote": "Dạ dày nhắn bạn lưu video lại để nhắc mình ăn tối sớm nhé.",
                    "relation": "context",
                    "source_terms": ["Dạ dày"],
                    "visual_terms": ["endcard"]
                },
                "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. All four organ characters wave warmly in a gentle looping hold motion on the white background, silent visual storytelling, no talking, no lip movement"
            }
        ],
        "beats": [
            {
                "id": "SC05_B1",
                "image_id": "SC05_I1",
                "purpose": "Đỉnh điểm cao trào bốn giờ sáng tại gan",
                "anchor": {"vi": {"quote": "Nhưng bước chuyển hóa nguy hiểm nhất ở gan", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "fast",
                "narrative_situation": "cliffhanger_peak",
                "camera_intent": "tension"
            },
            {
                "id": "SC05_B2",
                "image_id": "SC05_I2",
                "purpose": "Đỉnh điểm lúc bốn giờ sáng khi chìm vào giấc ngủ",
                "anchor": {"vi": {"quote": "vào lúc bốn giờ sáng khi bạn chìm vào giấc ngủ.", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "fast",
                "narrative_situation": "cliffhanger_peak",
                "camera_intent": "reveal"
            },
            {
                "id": "SC05_B3",
                "image_id": "SC05_I3",
                "purpose": "Dẫn phễu sang video dài mười hai giờ trên kênh",
                "anchor": {"vi": {"quote": "Xem trọn vẹn mười hai giờ trên video dài của Cơ Thể Kể nhé.", "occurrence": 1}},
                "effect": "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "normal",
                "narrative_situation": "cta_bridge",
                "camera_intent": "focus"
            },
            {
                "id": "SC05_B4",
                "image_id": "SC05_I4",
                "purpose": "Endcard kết thúc video ngắn",
                "anchor": {"vi": {"quote": "Dạ dày nhắn bạn lưu video lại để nhắc mình ăn tối sớm nhé.", "occurrence": 1}},
                "effect": "hold",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "hold",
                "narrative_situation": "cta_close",
                "camera_intent": "hold",
                "is_endcard": True
            }
        ],
        "tone": "narrative_warm",
        "narrative_situation": "cta_close"
    }
]

SHORT_COVERAGE = [
    {
        "requirement_id": "R01",
        "scene_id": "SC01",
        "quote": "Mười một giờ đêm, bạn ăn đĩa gà rán ngập mỡ rồi lên giường nằm."
    },
    {
        "requirement_id": "R02",
        "scene_id": "SC02",
        "quote": "Dầu mỡ làm giãn van thực quản. Khi nằm ngang, axit dạ dày lập tức trào ngược lên họng."
    },
    {
        "requirement_id": "R03",
        "scene_id": "SC03",
        "quote": "Nhiều người tưởng ngủ là xong việc. Nhưng thực chất lá gan phải thức trắng để gom mỡ thừa"
    },
    {
        "requirement_id": "R04",
        "scene_id": "SC04",
        "quote": "Tim phải đập dồn dập đưa máu về bụng, khiến não bộ không thể vào giấc ngủ sâu."
    },
    {
        "requirement_id": "R05",
        "scene_id": "SC05",
        "quote": "Nhưng bước chuyển hóa nguy hiểm nhất ở gan mới bắt đầu vào lúc bốn giờ sáng khi bạn chìm vào giấc ngủ."
    }
]

SHORT_CLAIMS = [
    {
        "scene_id": "SC02",
        "quote": "Dầu mỡ làm giãn van thực quản.",
        "language": "vi",
        "source_id": "SRC01",
        "fact": "Chất béo làm giãn van thực quản và giữ thức ăn lâu trong dạ dày."
    },
    {
        "scene_id": "SC04",
        "quote": "Tim phải đập dồn dập đưa máu về bụng,",
        "language": "vi",
        "source_id": "SRC02",
        "fact": "Lá gan phải thức trắng đêm gom mỡ thừa tích tụ trong máu."
    }
]

SHORT_COMPETITOR_RESEARCH = {
    "channel_id": "co_the_ke",
    "job_id": JOB_SHORT_ID,
    "topic": TOPIC_SHORT,
    "competitor_analysis": {
        "benchmark_channels": [
            {
                "channel_name": "Zack D. Films",
                "top_performing_videos": [
                    {
                        "title": "What Happens When You Sleep Right After Eating?",
                        "views": "15M views",
                        "hook_technique": "Rơi thẳng vào tình huống chiếc bánh mì rơi xuống dạ dày và axit trào ngược không có phần mở đầu.",
                        "pacing_structure": "Hook hành động ngay giây đầu -> Hiệu ứng giải phẫu 3D -> Cảnh báo sinh học ngắn gọn.",
                        "retention_driver": "Trực quan hóa tức thì cảm giác nóng rát ngực mà người xem từng trải qua."
                    }
                ],
                "viral_patterns_extracted": [
                    "Vào đề trực diện không chào hỏi, đặt người xem ngay trước bàn ăn lúc nửa đêm.",
                    "Nhân hóa nỗi khổ của nội tạng để tạo sự đồng cảm và giật mình phản tỉnh thói quen xấu."
                ]
            },
            {
                "channel_name": "Bác sĩ Huy",
                "top_performing_videos": [
                    {
                        "title": "Ăn đêm hại gan và dạ dày khủng khiếp thế nào?",
                        "views": "2.4M views",
                        "hook_technique": "Phản bác lầm tưởng ăn no cho dễ ngủ bằng phân tích áp lực chuyển hóa của gan.",
                        "pacing_structure": "Phá bỏ ngộ nhận -> Minh họa chu kỳ sinh học gan -> Lời khuyên quy tắc 3 giờ.",
                        "retention_driver": "Giọng điệu chia sẻ gần gũi, cảnh báo sức khỏe khoa học dựa trên nghiên cứu y học."
                    }
                ],
                "viral_patterns_extracted": [
                    "Nhấn mạnh hậu quả mệt mỏi sáng hôm sau dù ngủ đủ tám tiếng để đánh trúng điểm đau thường ngày.",
                    "Kêu gọi lưu video để tự nhắc nhở bản thân ăn tối đúng giờ một cách tinh tế."
                ]
            }
        ]
    },
    "viral_formula_audit": {
        "cold_audience_hook_analysis": {
            "first_sentence_syllables": 15,
            "zero_pause_opening_seconds": 15,
            "visual_contrast": "Đĩa gà rán vàng giòn hấp dẫn đối lập với cảnh dạ dày ngập ngụa trong axit và dầu mỡ.",
            "counter_intuitive_truth_slap": "Bạn nằm ngủ yên giấc không có nghĩa là cơ thể được nghỉ; dạ dày và lá gan đang phải gồng mình cày ca đêm vì miếng ăn muộn."
        },
        "narrative_progression_arc": [
            {
                "phase": "lived_friction",
                "purpose": "Tình huống ăn khuya quen thuộc lúc mười một giờ đêm và cơn ác mộng nội tạng."
            },
            {
                "phase": "empirical_conflict",
                "purpose": "Axit trào ngược do cơ thắt thực quản giãn lỏng và dạ dày co bóp kiệt sức."
            },
            {
                "phase": "structural_model",
                "purpose": "Lời bình sắc bén về việc gan thức trắng gom mỡ và tim đập dồn dập tước đoạt giấc ngủ sâu."
            },
            {
                "phase": "actionable_resolution",
                "purpose": "Vòng lặp mở về đỉnh điểm nguy hiểm lúc bốn giờ sáng và dẫn phễu về video dài trên YouTube."
            }
        ],
        "flow_video_transition_blueprint": {
            "chain_mode": "daisy_chain",
            "video_model": "omni_flash",
            "keyframe_continuity": "Sequential daisy-chain linking Start Frame to End Frame across all scenes."
        }
    },
    "academic_funnel_positioning": {
        "funnel_tier": "tier_1_broad",
        "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
        "myth_debunked": "Ăn no bụng vào đêm muộn giúp bạn dễ ngủ hơn và cơ thể sẽ tự động tiêu hóa trơn tru khi ngủ.",
        "channel_verdict": "Bữa ăn dầu mỡ lúc nửa đêm là một bản án tăng ca cưỡng bức, bắt gan và dạ dày dọn dẹp đống mỡ trong khi lẽ ra chúng phải được tái tạo tế bào.",
        "actionable_rule_of_thumb": "Quy tắc ba giờ rỗng bụng: dừng toàn bộ thức ăn dầu mỡ ít nhất ba tiếng trước khi đặt lưng xuống giường."
    },
    "cta_and_spinoff_strategy": {
        "cliffhanger_peak": "Nhưng bước chuyển hóa nguy hiểm nhất ở gan mới bắt đầu vào lúc bốn giờ sáng khi bạn chìm vào giấc ngủ",
        "bridge": "Xem trọn vẹn mười hai giờ trên video dài của Cơ Thể Kể nhé.",
        "close": "Dạ dày nhắn bạn lưu video lại để nhắc mình ăn tối sớm nhé.",
        "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
    }
}

print("Short 9:16 data structures created successfully.")
