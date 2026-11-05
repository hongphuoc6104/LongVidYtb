#!/usr/bin/env python3
"""Build and validate Batch 3 packages for tui_tien:
1. sys/runs/tui-tien-batch3-9x16/
2. sys/runs/tui-tien-batch3-16x9/
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sys"))

from channels.registry import channel_cast, channel_profile_stamp, get_channel


def build_tui_tien_9x16():
    job_id = "tui-tien-batch3-9x16"
    ch = get_channel("tui_tien")

    brief = {
        "schema_version": "3.0",
        "topic": "Ly Cà Phê 45 Nghìn Ngồi 5 Tiếng: Chủ Quán Lời Nhờ Đâu?",
        "audience": "Sinh viên, người mới đi làm thu nhập 7-20 triệu",
        "goal": "Giải phẫu cơ cấu định phí biến phí quán cà phê và hiệu ứng mồi câu đám đông rồi chuyển phễu sang video dài",
        "video_type": "research_guide",
        "duration": {
            "min_seconds": 40.0,
            "max_seconds": 55.0
        },
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Nghịch lý ly cà phê 45k ngồi cắm sạc laptop 5 tiếng"},
            {"id": "R02", "text": "Bóc tách biến phí thực tế của nguyên liệu và tiền điện"},
            {"id": "R03", "text": "Bản chất định phí tiền thuê mặt bằng và máy điều hòa"},
            {"id": "R04", "text": "Hiệu ứng mồi câu uy tín tự nhiên kéo khách mua mang đi"},
            {"id": "R05", "text": "Đỉnh cao trào bỏ lửng và chuyển phễu sang video dài"}
        ],
        "language": "vi",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "9:16",
        "format_profile": "short_9x16",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Cost Structure and Break-Even Dynamics in Modern Coffee Retail",
                "reference": "Vietnam F&B Industry Report (2024). Operational Economics of Independent Cafes.",
                "facts": [
                    "Giá vốn nguyên liệu cà phê chỉ chiếm khoảng 12% đến 15% giá bán lẻ một ly nước."
                ]
            }
        ],
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
                "Bóc tách con số rõ ràng bằng tiền Việt giúp người xem hiểu ngay bài toán kinh tế quán cà phê"
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Không đòi hỏi kiến thức kế toán hay tài chính chuyên sâu.",
            "pacing": "Gãy gọn, tính nhẩm từng bước dứt khoát, hình ảnh trực quan trên nền giấy kẻ ô.",
            "speech_rates": {
                "vi": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.1,
                    "source": "Acoustic calibrated cadence"
                }
            }
        },
        "packaging": {
            "youtube_title": "Ly Cà Phê 45k Ngồi 5 Tiếng: Chủ Quán Lời Nhờ Đâu?",
            "thumbnail_spec": {
                "visual_hook": "Người que đeo kính tròn cầm đồng xu vàng đứng cạnh ly cà phê đá 45 nghìn và chiếc đồng hồ chạy năm tiếng",
                "text_overlay": "NGỒI 5 TIẾNG LỜI ĐÂU",
                "contrast_pair": "Khách ngồi lì 5 tiếng vs Lợi nhuận bí mật của chủ quán",
                "thumbnail_prompt": "Simple 2D doodle stickman with round glasses holding a gold coin (#F2C14E) next to a tall iced coffee glass labeled '45.000 Đ' and a hand-drawn desk clock showing 5 hours. Warm grid-paper canvas (#FAF6E9 with faint #E3DCC8 square grid), wobbly black marker outlines (#1F1F1F), flat fills in money green (#2F9E5B) and loss red (#D64545). Bold hand-lettered text in upper third: 'NGỒI 5 TIẾNG LỜI ĐÂU'. Orthographic 2D, >=60% empty grid space, no 3D, no gradients.",
                "layout_mode": "split_contrast"
            },
            "editorial_stance": {
                "myth_debunked": "Khách gọi một ly cà phê ngồi làm việc cả buổi là kẻ phá đám làm quán lỗ tiền điện.",
                "why_generic_advice_fails": "Tư duy đuổi khéo khách chỉ làm quán vắng hoe như chùa bà đanh và mất sạch khách vãng lai.",
                "channel_verdict": "Thực chất quán cà phê không sống nhờ tiền nước mà bán không gian làm việc và tận dụng bạn làm mồi câu đám đông.",
                "tradeoff_or_blindspot": "Chấp nhận khách ngồi lâu tốn thêm vài trăm đồng tiền điện nhưng đổi lại hiệu ứng quán đông đúc thu hút khách mang đi."
            },
            "actionable_value": {
                "core_mechanism": "Phân bổ định phí mặt bằng trên dòng khách vãng lai và biến khách ngồi làm việc thành mồi câu uy tín tự nhiên.",
                "practical_rule_of_thumb": "Quy tắc mồi câu đám đông: Quán có ba bàn sáng đèn laptop luôn hút khách vãng lai gấp bốn lần quán trống trơn.",
                "real_world_scenario": "Chủ quán sẵn sàng mời thêm nước lọc cho khách ngồi làm việc vì mỗi giờ ngồi lại làm tăng xác suất gọi thêm đĩa bánh ngọt."
            }
        },
        "youtube_title": "Ly Cà Phê 45k Ngồi 5 Tiếng: Chủ Quán Lời Nhờ Đâu?",
        "thumbnail_spec": {
            "visual_hook": "Người que đeo kính tròn cầm đồng xu vàng đứng cạnh ly cà phê đá 45 nghìn và chiếc đồng hồ chạy năm tiếng",
            "text_overlay": "NGỒI 5 TIẾNG LỜI ĐÂU",
            "contrast_pair": "Khách ngồi lì 5 tiếng vs Lợi nhuận bí mật của chủ quán",
            "thumbnail_prompt": "Simple 2D doodle stickman with round glasses holding a gold coin (#F2C14E) next to a tall iced coffee glass labeled '45.000 Đ' and a hand-drawn desk clock showing 5 hours. Warm grid-paper canvas (#FAF6E9 with faint #E3DCC8 square grid), wobbly black marker outlines (#1F1F1F), flat fills in money green (#2F9E5B) and loss red (#D64545). Bold hand-lettered text in upper third: 'NGỒI 5 TIẾNG LỜI ĐÂU'. Orthographic 2D, >=60% empty grid space, no 3D, no gradients.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Tiền và kinh tế đời sống",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": [
            "tui tien",
            "kinh te quan ca phe",
            "tai chinh",
            "kinh doanh",
            "fnb",
            "shorts",
            "learnontiktok",
            "kinhte"
        ],
        "parent_long_id": "tui-tien-batch3-16x9",
        "cta_plan": {
            "cliffhanger_peak": "Vậy công thức định giá ly nước bốn mươi lăm ngàn đồng chia cho mặt bằng thế nào?",
            "bridge": "Bảng tính chi tiết từng khoản lãi lỗ mình để ở video dài trên YouTube nhé.",
            "close": "Lần sau đi cà phê bạn nhớ quan sát dòng người trước khi chọn quán nhé.",
            "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
        },
        "channel_profile": channel_profile_stamp("tui_tien"),
        "engagement": {
            "cta_voice": "Mê con số",
            "bridge_templates": [
                "Bảng tính đủ từng khoản mình để ở video dài trên YouTube."
            ],
            "close_templates": [
                "Lưu lại, lần sau tính nhẩm trước khi quẹt thẻ."
            ],
            "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
            "banned_cta_phrases": [
                "đừng quên like",
                "nhấn chuông",
                "bấm chuông",
                "like share",
                "like và share",
                "like, share",
                "subscribe",
                "đăng ký kênh",
                "ấn theo dõi ngay",
                "bấm theo dõi ngay",
                "hãy like",
                "nhớ like",
                "để ủng hộ kênh"
            ]
        },
        "editorial_stance": {
            "myth_debunked": "Khách gọi một ly cà phê ngồi làm việc cả buổi là kẻ phá đám làm quán lỗ tiền điện.",
            "why_generic_advice_fails": "Tư duy đuổi khéo khách chỉ làm quán vắng hoe như chùa bà đanh và mất sạch khách vãng lai.",
            "channel_verdict": "Thực chất quán cà phê không sống nhờ tiền nước mà bán không gian làm việc và tận dụng bạn làm mồi câu đám đông.",
            "tradeoff_or_blindspot": "Chấp nhận khách ngồi lâu tốn thêm vài trăm đồng tiền điện nhưng đổi lại hiệu ứng quán đông đúc thu hút khách mang đi."
        },
        "actionable_value": {
            "core_mechanism": "Phân bổ định phí mặt bằng trên dòng khách vãng lai và biến khách ngồi làm việc thành mồi câu uy tín tự nhiên.",
            "practical_rule_of_thumb": "Quy tắc mồi câu đám đông: Quán có ba bàn sáng đèn laptop luôn hút khách vãng lai gấp bốn lần quán trống trơn.",
            "real_world_scenario": "Chủ quán sẵn sàng mời thêm nước lọc cho khách ngồi làm việc vì mỗi giờ ngồi lại làm tăng xác suất gọi thêm đĩa bánh ngọt."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {
                "scene_id": "SC01",
                "purpose": "Triển khai bước 1: nêu nghịch lý khách ngồi lì năm tiếng với ly nước 45k",
                "requirements": ["R01"],
                "transition": "Tiếp tục theo trình tự bóc tách con số"
            },
            {
                "scene_id": "SC02",
                "purpose": "Triển khai bước 2: tính nhẩm biến phí nguyên liệu và tiền điện",
                "requirements": ["R02"],
                "transition": "Tiếp tục theo trình tự bóc tách con số"
            },
            {
                "scene_id": "SC03",
                "purpose": "Triển khai bước 3: giải mã bản chất định phí mặt bằng không đổi",
                "requirements": ["R03"],
                "transition": "Tiếp tục theo trình tự bóc tách con số"
            },
            {
                "scene_id": "SC04",
                "purpose": "Triển khai bước 4: phân tích hiệu ứng mồi câu kéo khách mua mang đi",
                "requirements": ["R04"],
                "transition": "Tiếp tục theo trình tự bóc tách con số"
            },
            {
                "scene_id": "SC05",
                "purpose": "Triển khai bước 5: đỉnh cao trào bỏ lửng và chuyển phễu sang video dài",
                "requirements": ["R05"],
                "transition": "Tiếp tục theo trình tự bóc tách con số"
            }
        ]
    }

    competitor = {
        "channel_id": "tui_tien",
        "job_id": job_id,
        "topic": brief["topic"],
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Sitcom Tài Chính",
                    "top_performing_videos": [
                        {
                            "title": "Ngồi quán cafe 8 tiếng tốn bao nhiêu tiền điện của chủ?",
                            "views": "1.1M views",
                            "hook_technique": "Cắm đồng hồ đo điện trực tiếp vào cục sạc laptop để xem số tiền nhảy.",
                            "pacing_structure": "Thử nghiệm thực tế -> Tính tiền điện lẻ -> So sánh với doanh thu ly nước.",
                            "retention_driver": "Con số giật mình khi cắm sạc cả ngày chỉ tốn chưa tới một nghìn đồng."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Dùng phép tính quy đổi thành tiền đồng cụ thể dễ nhớ.",
                        "Lật ngược suy nghĩ thông thường rằng chủ quán ghét khách ngồi lâu."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 17,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Ly cà phê 45k bên cạnh đồng hồ 5 tiếng đối lập với nụ cười niềm nở của chủ quán.",
                "counter_intuitive_truth_slap": "Khách ngồi làm việc cả buổi không làm quán lỗ, mà đang là nhân viên tiếp thị đắc lực nhất của quán."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Tái hiện cảm giác áy náy khi gọi một ly nước mà ngồi cả buổi."},
                {"phase": "cost_breakdown", "purpose": "Bóc tách biến phí: 6 nghìn nguyên liệu và chưa tới 1 nghìn tiền điện."},
                {"phase": "fixed_cost_reality", "purpose": "Chỉ ra tiền thuê nhà và máy lạnh là chi phí cố định không đổi."},
                {"phase": "social_proof_verdict", "purpose": "Khách ngồi đông đúc tạo phông nền uy tín kéo khách mang đi."},
                {"phase": "cliffhanger_spinoff", "purpose": "Mở ra câu hỏi cơ cấu định giá đầy đủ trên video dài YouTube."}
            ]
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Tiền và kinh tế đời sống",
            "myth_debunked": brief["editorial_stance"]["myth_debunked"],
            "channel_verdict": brief["editorial_stance"]["channel_verdict"],
            "actionable_rule_of_thumb": brief["actionable_value"]["practical_rule_of_thumb"]
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": brief["cta_plan"]["cliffhanger_peak"],
            "bridge": brief["cta_plan"]["bridge"],
            "close": brief["cta_plan"]["close"],
            "endcard_text": brief["cta_plan"]["endcard_text"]
        }
    }

    # 5 scenes calibrated to ~165 words total
    scenes_data = [
        {
            "id": "SC01",
            "title": "Nghịch lý ly cà phê bốn mươi lăm nghìn",
            "purpose": "Triển khai bước 1: nêu nghịch lý khách ngồi lì năm tiếng với ly nước 45k",
            "action": "The stickman with glasses sits at coffee shop table with iced coffee and laptop, clock showing 5 hours.",
            "setting": "2D cafe table with laptop and iced coffee glass on warm grid-paper canvas #FAF6E9.",
            "camera": "Semantic camera: establishing mid shot focusing on iced coffee price tag and laptop charger",
            "narration": "Gọi ly cà phê bốn mươi lăm nghìn, ngồi cắm sạc laptop suốt năm tiếng. Bạn nghĩ chủ quán đang nhăn nhó chịu lỗ vì tiền điện?",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "layers": [],
            "tone": "narrative_warm",
            "narrative_phase": "hook",
            "narrative_situation": "hook_shock",
            "beats": [
                {
                    "id": "SC01_B1",
                    "image_id": "SC01_I1",
                    "purpose": "Mở màn ly cà phê 45k",
                    "anchor": {"vi": {"quote": "Gọi ly cà phê bốn mươi lăm nghìn,", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "burst",
                    "narrative_situation": "hook_shock",
                    "camera_intent": "establish",
                    "shot_type": "full_scene"
                },
                {
                    "id": "SC01_B2",
                    "image_id": "SC01_I2",
                    "purpose": "Cắm sạc laptop suốt năm tiếng",
                    "anchor": {"vi": {"quote": "ngồi cắm sạc laptop suốt năm tiếng.", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "burst",
                    "narrative_situation": "hook_shock",
                    "camera_intent": "focus",
                    "shot_type": "full_scene"
                },
                {
                    "id": "SC01_B3",
                    "image_id": "SC01_I3",
                    "purpose": "Tưởng tượng chủ quán nhăn nhó khó chịu",
                    "anchor": {"vi": {"quote": "Bạn nghĩ chủ quán đang nhăn nhó chịu lỗ", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "camera_intent": "reaction",
                    "shot_type": "concept_metaphor"
                },
                {
                    "id": "SC01_B4",
                    "image_id": "SC01_I4",
                    "purpose": "Nghi vấn chịu lỗ vì tiền điện",
                    "anchor": {"vi": {"quote": "vì tiền điện?", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "camera_intent": "contrast",
                    "shot_type": "cutaway_detail"
                }
            ],
            "images": [
                {
                    "id": "SC01_I1",
                    "description": "Simple 2D doodle stickman with round glasses wearing flat coin-gold T-shirt (#F2C14E) and navy trousers (#24364F), sitting at a small wooden table beside a tall iced coffee glass labeled '45.000 Đ', warm grid-paper background (#FAF6E9 with faint #E3DCC8 grid), wobbly #1F1F1F marker lines, >=60% negative space.",
                    "character_ids": ["CH01"],
                    "preserve": "stickman with round glasses, coin-gold T-shirt, navy trousers, warm grid-paper canvas",
                    "change": "stickman sits beside 45.000 Đ coffee glass",
                    "reason": "Narration-locked full-frame beat SC01_I1",
                    "visible_text": [{"text": "45.000 Đ", "placement": "upper_third", "object": "tag"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "narrative_situation": "hook_shock",
                    "emphasis_text": "45.000 Đ",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Ice cubes clink gently in the iced coffee glass with price tag fluttering slightly, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I2",
                    "description": "The doodle stickman typing diligently on a laptop plugged into a wall outlet, while an oversized hand-drawn clock on the wall ticks from 1:00 to 6:00 (5 hours), flat grid-paper canvas (#FAF6E9), ink navy (#24364F) linework.",
                    "character_ids": ["CH01"],
                    "preserve": "stickman with glasses, coin-gold T-shirt, navy trousers, grid-paper canvas",
                    "change": "stickman types on plugged-in laptop beside a 5-hour clock",
                    "reason": "Narration-locked full-frame beat SC01_I2",
                    "visible_text": [{"text": "5 TIẾNG", "placement": "upper_third", "object": "clock"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "narrative_situation": "hook_shock",
                    "emphasis_text": "5 TIẾNG",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The clock hands spin smoothly showing five hours passing in seconds, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I3",
                    "description": "A comical doodle cafe owner behind a counter frowning with steam blowing from ears, looking at a negative profit chart with red arrows dipping down on flat grid-paper background (#FAF6E9), flat fills in loss red (#D64545).",
                    "character_ids": ["CH01"],
                    "preserve": "grid-paper canvas #FAF6E9, wobbly black marker contours",
                    "change": "frowning cafe owner comic caricature",
                    "reason": "Narration-locked full-frame beat SC01_I3",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "emphasis_text": None,
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": False,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Puffs of comic steam rise from the cafe owner's ears above the counter, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I4",
                    "description": "Close-up doodle of an electric wall socket with electric spark zaps jumping out, labeled 'ĐIỆN CHÙA?' with a large hand-drawn red question mark, flat warm grid-paper background (#FAF6E9), >=60% empty space.",
                    "character_ids": ["CH01"],
                    "preserve": "grid-paper canvas #FAF6E9, minimalist doodle style",
                    "change": "electric socket with question mark",
                    "reason": "Narration-locked full-frame beat SC01_I4",
                    "visible_text": [{"text": "ĐIỆN CHÙA?", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "cutaway_detail",
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "emphasis_text": "ĐIỆN CHÙA?",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": False,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Tiny electric doodle sparks flash around the wall plug, silent visual storytelling, no talking, no lip movement"
                }
            ]
        },
        {
            "id": "SC02",
            "title": "Bóc tách biến phí thực tế",
            "purpose": "Triển khai bước 2: tính nhẩm biến phí nguyên liệu và tiền điện",
            "action": "The stickman pulls out a pencil and writes calculations on the grid notebook.",
            "setting": "Hand-drawn ledger ledger worksheet on flat warm grid-paper canvas #FAF6E9.",
            "camera": "Semantic camera: mid shot panning to handwritten calculation ledger",
            "narration": "Tính nhẩm xem nào. Tiền hạt cà phê và sữa chỉ tốn sáu nghìn đồng. Máy tính bạn cắm nguồn suốt buổi tiêu thụ chưa tới một nghìn tiền điện.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "layers": [],
            "tone": "narrative_warm",
            "narrative_phase": "conflict",
            "narrative_situation": "story_action",
            "beats": [
                {
                    "id": "SC02_B1",
                    "image_id": "SC02_I1",
                    "purpose": "Mở sổ tay đặt bút tính nhẩm",
                    "anchor": {"vi": {"quote": "Tính nhẩm xem nào.", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "story_action",
                    "camera_intent": "action",
                    "shot_type": "full_scene"
                },
                {
                    "id": "SC02_B2",
                    "image_id": "SC02_I2",
                    "purpose": "Giá vốn nguyên liệu chỉ sáu nghìn đồng",
                    "anchor": {"vi": {"quote": "Tiền hạt cà phê và sữa chỉ tốn sáu nghìn đồng.", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "story_action",
                    "camera_intent": "focus",
                    "shot_type": "cutaway_detail"
                },
                {
                    "id": "SC02_B3",
                    "image_id": "SC02_I3",
                    "purpose": "Máy tính cắm nguồn suốt buổi",
                    "anchor": {"vi": {"quote": "Máy tính bạn cắm nguồn suốt buổi", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "story_action",
                    "camera_intent": "action",
                    "shot_type": "full_scene"
                },
                {
                    "id": "SC02_B4",
                    "image_id": "SC02_I4",
                    "purpose": "Tiền điện chưa tới một nghìn đồng",
                    "anchor": {"vi": {"quote": "tiêu thụ chưa tới một nghìn tiền điện.", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "story_action",
                    "camera_intent": "contrast",
                    "shot_type": "concept_metaphor"
                }
            ],
            "images": [
                {
                    "id": "SC02_I1",
                    "description": "The stickman with round glasses holding a sharp pencil over a neat handwritten column labeled 'CHI PHÍ THỰC TẾ', smiling warmly on warm grid-paper background (#FAF6E9 with faint grid), coin-gold (#F2C14E) shirt.",
                    "character_ids": ["CH01"],
                    "preserve": "stickman with glasses, coin-gold T-shirt, navy trousers, grid-paper canvas",
                    "change": "stickman prepares to calculate costs with pencil",
                    "reason": "Narration-locked full-frame beat SC02_I1",
                    "visible_text": [{"text": "TÍNH NHẨM", "placement": "upper_third", "object": "notebook"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "story_action",
                    "emphasis_text": "TÍNH NHẨM",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The stickman taps his pencil on the ledger line ready to write, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I2",
                    "description": "Doodle breakdown diagram showing a few roasted coffee beans and a tiny milk tin next to a price tag showing '6.000 Đ', drawn with clean wobbly marker lines on warm grid-paper (#FAF6E9).",
                    "character_ids": ["CH01"],
                    "preserve": "grid-paper canvas #FAF6E9, wobbly black marker style",
                    "change": "coffee beans and milk tin labeled 6.000 Đ",
                    "reason": "Narration-locked full-frame beat SC02_I2",
                    "visible_text": [{"text": "NGUYÊN LIỆU: 6K", "placement": "upper_third", "object": "price"}],
                    "kind": "scene",
                    "shot_type": "cutaway_detail",
                    "tempo": "fast",
                    "narrative_situation": "story_action",
                    "emphasis_text": "NGUYÊN LIỆU: 6K",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": False,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The 6.000 Đ tag drops down beside the coffee bean sketch with a slight bounce, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I3",
                    "description": "The stickman sitting beside his laptop showing battery meter at 100%, a subtle green energy flow arrow running along the charger cord, warm grid-paper background (#FAF6E9).",
                    "character_ids": ["CH01"],
                    "preserve": "stickman with glasses, coin-gold T-shirt, navy trousers, grid-paper canvas",
                    "change": "stickman calmly working at fully charged laptop",
                    "reason": "Narration-locked full-frame beat SC02_I3",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "story_action",
                    "emphasis_text": None,
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. A green power indicator pulses gently along the charger cord into the laptop, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I4",
                    "description": "A single tiny 1.000 Đ copper coin standing proudly next to an electricity power meter showing '0.3 kWh', showing the negligible cost of laptop charging, on warm grid-paper canvas (#FAF6E9).",
                    "character_ids": ["CH01"],
                    "preserve": "grid-paper canvas #FAF6E9, flat coin-gold color #F2C14E",
                    "change": "single 1.000 Đ coin beside power meter",
                    "reason": "Narration-locked full-frame beat SC02_I4",
                    "visible_text": [{"text": "TIỀN ĐIỆN: < 1K", "placement": "upper_third", "object": "cost"}],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "narrative_situation": "story_action",
                    "emphasis_text": "TIỀN ĐIỆN: < 1K",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": False,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The tiny coin glints once with a golden star sparkle, silent visual storytelling, no talking, no lip movement"
                }
            ]
        },
        {
            "id": "SC03",
            "title": "Bản chất của định phí mặt bằng",
            "purpose": "Triển khai bước 3: giải mã bản chất định phí mặt bằng không đổi",
            "action": "Illustration of fixed monthly overhead that runs regardless of guest count.",
            "setting": "Cafe storefront diagram on warm grid-paper canvas #FAF6E9.",
            "camera": "Semantic camera: wide shot showing storefront building and overhead costs",
            "narration": "Dù bạn có ngồi hay không, chủ quán vẫn phải trả tiền thuê nhà. Máy lạnh vẫn phải phà hơi mát cả ngày cho cả phòng.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "layers": [],
            "tone": "narrative_warm",
            "narrative_phase": "resolution",
            "narrative_situation": "mechanism_step",
            "beats": [
                {
                    "id": "SC03_B1",
                    "image_id": "SC03_I1",
                    "purpose": "Chủ quán vẫn phải trả tiền thuê nhà",
                    "anchor": {"vi": {"quote": "Dù bạn có ngồi hay không,", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "establish",
                    "shot_type": "concept_metaphor"
                },
                {
                    "id": "SC03_B2",
                    "image_id": "SC03_I2",
                    "purpose": "Hóa đơn tiền thuê nhà cố định nặng nề",
                    "anchor": {"vi": {"quote": "chủ quán vẫn phải trả tiền thuê nhà.", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "focus",
                    "shot_type": "visual_diagram"
                },
                {
                    "id": "SC03_B3",
                    "image_id": "SC03_I3",
                    "purpose": "Máy lạnh vẫn phải phà hơi mát",
                    "anchor": {"vi": {"quote": "Máy lạnh vẫn phải phà hơi mát", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "action",
                    "shot_type": "full_scene"
                },
                {
                    "id": "SC03_B4",
                    "image_id": "SC03_I4",
                    "purpose": "Làm mát cả ngày cho cả phòng",
                    "anchor": {"vi": {"quote": "cả ngày cho cả phòng.", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "contrast",
                    "shot_type": "concept_metaphor"
                }
            ],
            "images": [
                {
                    "id": "SC03_I1",
                    "description": "Doodle view of a 2D coffee shop storefront with glass windows and outdoor awning, a large monthly calendar labeled 'TIỀN THUÊ NHÀ' stamped on the roof, warm grid-paper background (#FAF6E9).",
                    "character_ids": ["CH01"],
                    "preserve": "grid-paper canvas #FAF6E9, wobbly black outlines, no 3D",
                    "change": "cafe storefront with rent calendar on roof",
                    "reason": "Narration-locked full-frame beat SC03_I1",
                    "visible_text": [{"text": "MẶT BẰNG CỐ ĐỊNH", "placement": "upper_third", "object": "building"}],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "emphasis_text": "MẶT BẰNG CỐ ĐỊNH",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": False,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. A rent stamp slams down firmly onto the storefront calendar roof, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I2",
                    "description": "A tall hand-drawn bar chart comparing Fixed Rent (massive red bar labeled 'ĐỊNH PHÍ 50 TRIỆU') against Variable Cost (tiny green bar labeled 'BIẾN PHÍ 6K'), on flat warm grid-paper canvas (#FAF6E9).",
                    "character_ids": ["CH01"],
                    "preserve": "grid-paper canvas #FAF6E9, money green #2F9E5B, loss red #D64545",
                    "change": "bar chart comparing huge fixed rent vs tiny variable cost",
                    "reason": "Narration-locked full-frame beat SC03_I2",
                    "visible_text": [{"text": "ĐỊNH PHÍ VS BIẾN PHÍ", "placement": "upper_third", "object": "chart"}],
                    "kind": "scene",
                    "shot_type": "visual_diagram",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "emphasis_text": "ĐỊNH PHÍ VS BIẾN PHÍ",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": False,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The red fixed rent bar rises rapidly while the tiny green bar stays almost flat, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I3",
                    "description": "A ceiling air conditioner unit blowing gentle wavy cool-air lines over empty tables and chairs in the cafe, on warm grid-paper canvas (#FAF6E9), pale ice-blue accents.",
                    "character_ids": ["CH01"],
                    "preserve": "grid-paper canvas #FAF6E9, clean marker line art",
                    "change": "ceiling AC unit blowing cool air over tables",
                    "reason": "Narration-locked full-frame beat SC03_I3",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "emphasis_text": None,
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": False,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Cool breeze doodle waves drift smoothly down from the AC unit across the floor, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I4",
                    "description": "The stickman with round glasses standing in the cafe showing that the cool air covers everyone equally whether 1 person or 10 people are sitting, holding a coin-gold gauge labeled 'CÙNG MỘT CHI PHÍ' on grid paper (#FAF6E9).",
                    "character_ids": ["CH01"],
                    "preserve": "stickman with glasses, coin-gold T-shirt, navy trousers, grid-paper canvas",
                    "change": "stickman points to constant AC operating cost",
                    "reason": "Narration-locked full-frame beat SC03_I4",
                    "visible_text": [{"text": "CHI PHÍ KHÔNG ĐỔI", "placement": "upper_third", "object": "gauge"}],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "emphasis_text": "CHI PHÍ KHÔNG ĐỔI",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The stickman nods as the gauge needle stays fixed right in the center, silent visual storytelling, no talking, no lip movement"
                }
            ]
        },
        {
            "id": "SC04",
            "title": "Hiệu ứng chim mồi đám đông",
            "purpose": "Triển khai bước 4: phân tích hiệu ứng mồi câu kéo khách mua mang đi",
            "action": "Editorial analysis of social proof in FnB and customer magnet dynamics.",
            "setting": "Street view outside cafe showing busy crowd vs empty cafe contrast on grid paper #FAF6E9.",
            "camera": "Semantic camera: slow thoughtful panning showing customer magnet effect",
            "narration": "Bạn chính là mồi câu đắt giá nhất của quán. Chỗ vắng tanh không ai vào. Khách thấy bạn ngồi làm việc mới an tâm tạt vào mua mang đi.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "layers": [],
            "tone": "narrative_warm",
            "narrative_phase": "resolution",
            "narrative_situation": "editorial_commentary",
            "beats": [
                {
                    "id": "SC04_B1",
                    "image_id": "SC04_I1",
                    "purpose": "Bạn chính là mồi câu đắt giá nhất",
                    "anchor": {"vi": {"quote": "Bạn chính là mồi câu đắt giá nhất của quán.", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "reflection",
                    "shot_type": "full_scene"
                },
                {
                    "id": "SC04_B2",
                    "image_id": "SC04_I2",
                    "purpose": "Quán vắng tanh không ai ghé",
                    "anchor": {"vi": {"quote": "Chỗ vắng tanh không ai vào.", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "contrast",
                    "shot_type": "concept_metaphor"
                },
                {
                    "id": "SC04_B3",
                    "image_id": "SC04_I3",
                    "purpose": "Người qua đường thấy đông đúc mới an tâm",
                    "anchor": {"vi": {"quote": "Khách thấy bạn ngồi làm việc", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "action",
                    "shot_type": "full_scene"
                },
                {
                    "id": "SC04_B4",
                    "image_id": "SC04_I4",
                    "purpose": "Khách ghé mua mang đi đem lại lợi nhuận cao",
                    "anchor": {"vi": {"quote": "mới an tâm tạt vào mua mang đi.", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "focus",
                    "shot_type": "full_scene"
                }
            ],
            "images": [
                {
                    "id": "SC04_I1",
                    "description": "The stickman with round glasses sitting by the glass window holding a glowing gold magnet that attracts smiling pedestrian figures toward the cafe entrance, warm grid-paper background (#FAF6E9), coin-gold (#F2C14E) shirt.",
                    "character_ids": ["CH01"],
                    "preserve": "stickman with glasses, coin-gold T-shirt, navy trousers, grid-paper canvas",
                    "change": "stickman holds symbolic magnet attracting pedestrian crowd",
                    "reason": "Narration-locked full-frame beat SC04_I1",
                    "visible_text": [{"text": "MỒI CÂU NIỀM TIN", "placement": "upper_third", "object": "magnet"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "emphasis_text": "MỒI CÂU NIỀM TIN",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Golden magnetic attraction waves ripple outward from the stickman through the cafe window, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I2",
                    "description": "Contrast illustration of an empty, gloomy doodle coffee shop with tumbleweed blowing across the doorway and passersby glancing with suspicious eyes, on warm grid-paper (#FAF6E9).",
                    "character_ids": ["CH01"],
                    "preserve": "grid-paper canvas #FAF6E9, clean marker lines",
                    "change": "empty deserted cafe with tumbleweed",
                    "reason": "Narration-locked full-frame beat SC04_I2",
                    "visible_text": [{"text": "VẮNG TANH = ĐÁNG NGỜ", "placement": "upper_third", "object": "sign"}],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "emphasis_text": "VẮNG TANH = ĐÁNG NGỜ",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": False,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. A doodle tumbleweed slowly rolls past the empty entrance, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I3",
                    "description": "Pedestrians on the sidewalk looking through the clear glass window, seeing 3 stickmen with laptops working happily under warm yellow lighting, smiling in reassurance on warm grid-paper canvas (#FAF6E9).",
                    "character_ids": ["CH01"],
                    "preserve": "grid-paper canvas #FAF6E9, wobbly black marker linework",
                    "change": "pedestrians looking in with smiles of approval",
                    "reason": "Narration-locked full-frame beat SC04_I3",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "emphasis_text": None,
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Pedestrians pause outside the window and turn toward the cafe entrance, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I4",
                    "description": "A line of happy customers at the take-away counter picking up paper cups of coffee in 30 seconds, a cash register ringing with money green (+45K, +45K, +45K) floating badges on grid paper (#FAF6E9).",
                    "character_ids": ["CH01"],
                    "preserve": "grid-paper canvas #FAF6E9, money green fills #2F9E5B",
                    "change": "take-away counter ringing up quick sales",
                    "reason": "Narration-locked full-frame beat SC04_I4",
                    "visible_text": [{"text": "+45K TAKE AWAY", "placement": "upper_third", "object": "register"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "emphasis_text": "+45K TAKE AWAY",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": False,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Takeaway coffee cups slide across the counter as cash register drawer pops open, silent visual storytelling, no talking, no lip movement"
                }
            ]
        },
        {
            "id": "SC05",
            "title": "Đỉnh cao trào và lời kết",
            "purpose": "Triển khai bước 5: đỉnh cao trào bỏ lửng và chuyển phễu sang video dài",
            "action": "Open loop on unit economics and call to action to long format breakdown on YouTube.",
            "setting": "Closing branded ledger board on warm grid-paper background #FAF6E9.",
            "camera": "Semantic camera: focus on open ledger transitioning into YouTube CTA endcard",
            "narration": "Vậy công thức định giá ly nước bốn mươi lăm ngàn đồng chia cho mặt bằng thế nào? Bảng tính chi tiết từng khoản lãi lỗ mình để ở video dài trên YouTube nhé. Lần sau đi cà phê bạn nhớ quan sát dòng người trước khi chọn quán nhé.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "layers": [],
            "tone": "narrative_warm",
            "narrative_phase": "outro",
            "narrative_situation": "cliffhanger_peak",
            "beats": [
                {
                    "id": "SC05_B1",
                    "image_id": "SC05_I1",
                    "purpose": "Nêu câu hỏi lửng về công thức định giá ly nước 45k",
                    "anchor": {"vi": {"quote": "Vậy công thức định giá ly nước bốn mươi lăm ngàn đồng", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "cliffhanger_peak",
                    "camera_intent": "focus",
                    "shot_type": "full_scene"
                },
                {
                    "id": "SC05_B2",
                    "image_id": "SC05_I2",
                    "purpose": "Phân chia mặt bằng thế nào",
                    "anchor": {"vi": {"quote": "chia cho mặt bằng thế nào?", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "cliffhanger_peak",
                    "camera_intent": "action",
                    "shot_type": "concept_metaphor"
                },
                {
                    "id": "SC05_B3",
                    "image_id": "SC05_I3",
                    "purpose": "Cầu nối phễu sang video dài trên YouTube",
                    "anchor": {"vi": {"quote": "Bảng tính chi tiết từng khoản lãi lỗ mình để ở video dài trên YouTube nhé.", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "hold",
                    "narrative_situation": "cta_bridge",
                    "camera_intent": "establish",
                    "shot_type": "full_scene"
                },
                {
                    "id": "SC05_B4",
                    "image_id": "SC05_I4",
                    "purpose": "Lời kết và endcard thương hiệu",
                    "anchor": {"vi": {"quote": "Lần sau đi cà phê bạn nhớ quan sát dòng người trước khi chọn quán nhé.", "occurrence": 1}},
                    "effect": "hold",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "hold",
                    "narrative_situation": "cta_close",
                    "camera_intent": "hold",
                    "shot_type": "full_scene",
                    "is_endcard": True
                }
            ],
            "images": [
                {
                    "id": "SC05_I1",
                    "description": "The stickman with round glasses holding a pie chart sliced into ingredients, rent, labor, and profit margins, with a big question mark hovering above the profit slice on warm grid-paper (#FAF6E9).",
                    "character_ids": ["CH01"],
                    "preserve": "stickman with glasses, coin-gold T-shirt, navy trousers, grid-paper canvas",
                    "change": "stickman displays cost breakdown pie chart",
                    "reason": "Narration-locked full-frame beat SC05_I1",
                    "visible_text": [{"text": "BÓC TÁCH 45K", "placement": "upper_third", "object": "chart"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "cliffhanger_peak",
                    "emphasis_text": "BÓC TÁCH 45K",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The pie chart segments pulse gently highlighting the question mark, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I2",
                    "description": "A hand-drawn ledger notebook showing rows of detailed calculations with green checkmarks beside rent and staff payroll formulas on warm grid-paper (#FAF6E9), clean wobbly marker art.",
                    "character_ids": ["CH01"],
                    "preserve": "grid-paper canvas #FAF6E9, clean marker linework",
                    "change": "ledger notebook with detailed formula breakdown",
                    "reason": "Narration-locked full-frame beat SC05_I2",
                    "visible_text": [{"text": "BẢNG TÍNH LÃI LỖ", "placement": "upper_third", "object": "ledger"}],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "narrative_situation": "cliffhanger_peak",
                    "emphasis_text": "BẢNG TÍNH LÃI LỖ",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": False,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. A ledger bookmark slides into place with a neat snap, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I3",
                    "description": "The stickman with round glasses pointing a pencil toward a hand-drawn YouTube window showing 'TÚI TIỀN BIẾT NÓI - BẢN ĐẦY ĐỦ', with a green play button on warm grid-paper background (#FAF6E9).",
                    "character_ids": ["CH01"],
                    "preserve": "stickman with glasses, coin-gold T-shirt, navy trousers, grid-paper canvas",
                    "change": "stickman points pencil to YouTube video card",
                    "reason": "Narration-locked full-frame beat SC05_I3",
                    "visible_text": [{"text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE", "placement": "upper_third", "object": "banner"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "hold",
                    "narrative_situation": "cta_bridge",
                    "emphasis_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The YouTube frame expands smoothly as the stickman smiles and points, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I4",
                    "description": "Endcard frame: The stickman with round glasses smiling and holding up a gold coin (#F2C14E) beside large bold hand-lettered text centered: 'TÚI TIỀN BIẾT NÓI' with 'BẢN ĐẦY ĐỦ TRÊN YOUTUBE', on warm grid-paper (#FAF6E9).",
                    "character_ids": ["CH01"],
                    "preserve": "stickman with glasses, coin-gold T-shirt, navy trousers, grid-paper canvas",
                    "change": "endcard closing frame with channel branding",
                    "reason": "Narration-locked full-frame beat SC05_I4",
                    "visible_text": [{"text": "TÚI TIỀN BIẾT NÓI", "placement": "upper_third", "object": "logo"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "hold",
                    "narrative_situation": "cta_close",
                    "emphasis_text": "TÚI TIỀN BIẾT NÓI",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The stickman flips the gold coin once into the air and catches it as the frame holds solid, silent visual storytelling, no talking, no lip movement"
                }
            ]
        }
    ]

    content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": "",
        "topic": brief["topic"],
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": brief["required_points"],
        "characters": [channel_cast("tui_tien", "CH01")],
        "scenes": scenes_data,
        "coverage": [
            {"requirement_id": "R01", "scene_id": "SC01", "quote": "Gọi ly cà phê bốn mươi lăm nghìn, ngồi cắm sạc laptop"},
            {"requirement_id": "R02", "scene_id": "SC02", "quote": "Tính nhẩm xem nào. Tiền hạt cà phê và sữa"},
            {"requirement_id": "R03", "scene_id": "SC03", "quote": "Dù bạn có ngồi hay không, chủ quán vẫn phải trả tiền thuê nhà"},
            {"requirement_id": "R04", "scene_id": "SC04", "quote": "Bạn chính là mồi câu đắt giá nhất của quán"},
            {"requirement_id": "R05", "scene_id": "SC05", "quote": "Vậy công thức định giá ly nước bốn mươi lăm ngàn đồng chia cho mặt bằng"}
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC02",
                "quote": "Tiền hạt cà phê và sữa chỉ tốn sáu nghìn đồng.",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Giá vốn nguyên liệu cà phê chỉ chiếm khoảng 12% đến 15% giá bán lẻ một ly nước."
            }
        ],
        "revision_response": "Initial comprehensive schema-valid generation",
        "open_questions": []
    }

    job_dir = ROOT / "sys" / "runs" / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    brief_path = job_dir / "brief.json"
    brief_bytes = json.dumps(brief, indent=2, ensure_ascii=False).encode("utf-8")
    brief_path.write_bytes(brief_bytes)
    content["brief_hash"] = hashlib.sha256(brief_bytes).hexdigest()

    (job_dir / "content.json").write_text(json.dumps(content, indent=2, ensure_ascii=False))
    (job_dir / "outline.json").write_text(json.dumps(outline, indent=2, ensure_ascii=False))
    (job_dir / "competitor_research.json").write_text(json.dumps(competitor, indent=2, ensure_ascii=False))
    print(f"Generated {job_id}")


if __name__ == "__main__":
    build_tui_tien_9x16()
