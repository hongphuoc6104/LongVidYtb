#!/usr/bin/env python3
"""Build and validate Batch 3 packages for nao_luoi:
1. sys/runs/nao-luoi-batch3-9x16/
2. sys/runs/nao-luoi-batch3-16x9/
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sys"))

from channels.registry import channel_cast, channel_profile_stamp, get_channel


def build_nao_luoi_9x16():
    job_id = "nao-luoi-batch3-9x16"
    ch = get_channel("nao_luoi")

    # Brief
    brief = {
        "schema_version": "3.0",
        "topic": "Vì Sao Càng Gặp Việc Gấp Não Bạn Càng Bắt Đi Dọn Phòng?",
        "audience": "Gen Z và người đi làm 18-30 tuổi, hay tự hỏi về bản thân",
        "goal": "Giải thích hiệu ứng Zeigarnik và cơ chế trì hoãn tích cực khi gặp deadline rồi chuyển phễu sang video dài",
        "video_type": "research_guide",
        "duration": {
            "min_seconds": 40.0,
            "max_seconds": 55.0
        },
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Hành vi kỳ lạ dọn dẹp nhà cửa khi sắp tới giờ nộp bài"},
            {"id": "R02", "text": "Cảm giác hoàn thành giả tạo và cái bẫy trì hoãn tích cực"},
            {"id": "R03", "text": "Khám phá của Bluma Zeigarnik về sức căng nhận thức từ việc dang dở"},
            {"id": "R04", "text": "Bản chất trốn tránh cảm xúc bất an thay vì lười biếng"},
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
                "title": "On Finished and Unfinished Tasks",
                "reference": "Zeigarnik, B. (1927). Das Behalten erledigter und unerledigter Handlungen. Psychologische Forschung, 9, 1-85.",
                "facts": [
                    "Các nhiệm vụ chưa hoàn thành tạo ra sức căng nhận thức kéo dài trong trí nhớ làm việc."
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
                "Giải thích cơ chế tâm lý Zeigarnik tự nhiên không giáo điều và dẫn dắt người xem sang video phân tích dài"
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Không đòi hỏi thuật ngữ tâm lý học phức tạp.",
            "pacing": "Nhanh, dồn dập ở mở màn, lắng đọng ở bình luận phản biện, dứt khoát ở kêu gọi hành động.",
            "speech_rates": {
                "vi": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.1,
                    "source": "Acoustic calibrated cadence"
                }
            }
        },
        "packaging": {
            "youtube_title": "Vì Sao Việc Càng Gấp Não Lại Bắt Đi Dọn Nhà?",
            "thumbnail_spec": {
                "visual_hook": "Người que đầu trọc ôm cây chổi đứng hoảng hốt trước đồng hồ deadline rực lửa và đống việc nhà",
                "text_overlay": "CẬN DEADLINE DỌN NHÀ",
                "contrast_pair": "Deadline cận kề vs Cơn nghiện dọn dẹp",
                "thumbnail_prompt": "Iconic 2D Vietnamese indie webcomic doodle stickman in flat cerulean-blue T-shirt (#3B82C4) and slate-gray trousers, holding a straw broom with wide frantic dot eyes in front of a burning alarm clock showing 'DEADLINE' on warm paper-cream background (#F8F0DC). Bold hand-lettered text in upper third: 'CẬN DEADLINE DỌN NHÀ'. Flat 2D orthographic canvas, over 60% negative space, no 3D, no gradients.",
                "layout_mode": "split_contrast"
            },
            "editorial_stance": {
                "myth_debunked": "Dọn dẹp bàn làm việc là bước chuẩn bị nghiêm túc để bắt đầu làm việc hiệu quả.",
                "why_generic_advice_fails": "Lời khuyên ép bản thân kỷ luật thép chỉ làm tăng thêm áp lực cảm xúc khiến não càng muốn bỏ trốn.",
                "channel_verdict": "Thực chất não bạn không hề chăm chỉ mà đang chọn dọn dẹp như một lối thoát an toàn để trốn việc khó.",
                "tradeoff_or_blindspot": "Lau dọn đem lại cảm giác hoàn thành giả tạo trong mười lăm phút nhưng deadline thực tế vẫn đứng nguyên một chỗ."
            },
            "actionable_value": {
                "core_mechanism": "Đóng vòng lặp nhận thức Zeigarnik bằng hành động siêu nhỏ để giải tỏa sức căng tâm lý.",
                "practical_rule_of_thumb": "Quy tắc mở đầu hai phút: Chỉ cần mở tài liệu và viết đúng một câu đầu tiên để kích hoạt quán tính làm việc.",
                "real_world_scenario": "Thay vì đứng dậy lau sạch cái bàn, hãy mở máy tính và đặt đồng hồ hai phút gõ khung sườn bài báo cáo."
            }
        },
        "youtube_title": "Vì Sao Việc Càng Gấp Não Lại Bắt Đi Dọn Nhà?",
        "thumbnail_spec": {
            "visual_hook": "Người que đầu trọc ôm cây chổi đứng hoảng hốt trước đồng hồ deadline rực lửa và đống việc nhà",
            "text_overlay": "CẬN DEADLINE DỌN NHÀ",
            "contrast_pair": "Deadline cận kề vs Cơn nghiện dọn dẹp",
            "thumbnail_prompt": "Iconic 2D Vietnamese indie webcomic doodle stickman in flat cerulean-blue T-shirt (#3B82C4) and slate-gray trousers, holding a straw broom with wide frantic dot eyes in front of a burning alarm clock showing 'DEADLINE' on warm paper-cream background (#F8F0DC). Bold hand-lettered text in upper third: 'CẬN DEADLINE DỌN NHÀ'. Flat 2D orthographic canvas, over 60% negative space, no 3D, no gradients.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Tâm lý và hành vi đời thường",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": [
            "nao luoi",
            "zeigarnik",
            "tri hoan",
            "tam ly hoc",
            "cận deadline",
            "shorts",
            "genz",
            "learnontiktok",
            "tamly"
        ],
        "parent_long_id": "nao-luoi-batch3-16x9",
        "cta_plan": {
            "cliffhanger_peak": "Làm thế nào để lừa ngược lại bộ não hoàn thành dự án đúng hạn?",
            "bridge": "Vì sao não lại đòi dọn dẹp kiểu này, bản dài mình mổ xẻ trên YouTube Não Lười nhé.",
            "close": "Gửi cho đứa bạn hay thức khuya dọn nhà trước giờ nộp bài đi bạn nhé.",
            "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
        },
        "channel_profile": channel_profile_stamp("nao_luoi"),
        "engagement": {
            "cta_voice": "Bạn thân hơi cà khịa",
            "bridge_templates": [
                "Vì sao não lại đòi lại thời gian kiểu này? Bản dài mình mổ xẻ trên YouTube Não Lười."
            ],
            "close_templates": [
                "Gửi cho đứa bạn hay thức khuya chung với bạn đi."
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
            "myth_debunked": "Dọn dẹp bàn làm việc là bước chuẩn bị nghiêm túc để bắt đầu làm việc hiệu quả.",
            "why_generic_advice_fails": "Lời khuyên ép bản thân kỷ luật thép chỉ làm tăng thêm áp lực cảm xúc khiến não càng muốn bỏ trốn.",
            "channel_verdict": "Thực chất não bạn không hề chăm chỉ mà đang chọn dọn dẹp như một lối thoát an toàn để trốn việc khó.",
            "tradeoff_or_blindspot": "Lau dọn đem lại cảm giác hoàn thành giả tạo trong mười lăm phút nhưng deadline thực tế vẫn đứng nguyên một chỗ."
        },
        "actionable_value": {
            "core_mechanism": "Đóng vòng lặp nhận thức Zeigarnik bằng hành động siêu nhỏ để giải tỏa sức căng tâm lý.",
            "practical_rule_of_thumb": "Quy tắc mở đầu hai phút: Chỉ cần mở tài liệu và viết đúng một câu đầu tiên để kích hoạt quán tính làm việc.",
            "real_world_scenario": "Thay vì đứng dậy lau sạch cái bàn, hãy mở máy tính và đặt đồng hồ hai phút gõ khung sườn bài báo cáo."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {
                "scene_id": "SC01",
                "purpose": "Triển khai bước 1: hành vi dọn dẹp bất ngờ khi cận deadline",
                "requirements": ["R01"],
                "transition": "Tiếp tục theo trình tự diễn biến tâm lý"
            },
            {
                "scene_id": "SC02",
                "purpose": "Triển khai bước 2: cái bẫy hoàn thành giả tạo xoa dịu tội lỗi",
                "requirements": ["R02"],
                "transition": "Tiếp tục theo trình tự diễn biến tâm lý"
            },
            {
                "scene_id": "SC03",
                "purpose": "Triển khai bước 3: giải mã cơ chế khoa học hiệu ứng Zeigarnik",
                "requirements": ["R03"],
                "transition": "Tiếp tục theo trình tự diễn biến tâm lý"
            },
            {
                "scene_id": "SC04",
                "purpose": "Triển khai bước 4: bình luận phản biện về sự trốn tránh cảm xúc",
                "requirements": ["R04"],
                "transition": "Tiếp tục theo trình tự diễn biến tâm lý"
            },
            {
                "scene_id": "SC05",
                "purpose": "Triển khai bước 5: đỉnh cao trào bỏ lửng và chuyển đổi phễu sang video dài",
                "requirements": ["R05"],
                "transition": "Tiếp tục theo trình tự diễn biến tâm lý"
            }
        ]
    }

    competitor = {
        "channel_id": "nao_luoi",
        "job_id": job_id,
        "topic": brief["topic"],
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Psych2Go Vietnam",
                    "top_performing_videos": [
                        {
                            "title": "Vì sao bạn luôn dọn phòng trước ngày thi cử?",
                            "views": "850K views",
                            "hook_technique": "Đặt người xem vào tình huống quen thuộc lúc 11 giờ đêm cầm cây chổi.",
                            "pacing_structure": "Tình huống đời thường -> Tên gọi hiệu ứng tâm lý -> Lời khuyên nhẹ nhàng.",
                            "retention_driver": "Sự đồng cảm không phán xét giúp người xem thấy mình trong nhân vật hoạt hình."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Gọi tên chính xác cảm xúc tội lỗi nhưng vẫn thích thú khi lau dọn.",
                        "Giải thích bằng cơ chế sinh học dopamine thay vì phán xét đạo đức lười biếng."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Màn hình laptop mở sẵn trang trắng đối lập với cây chổi và đống quần áo giặt sạch.",
                "counter_intuitive_truth_slap": "Bạn không hề chăm chỉ khi dọn phòng, bạn chỉ đang tìm một chỗ trốn an toàn cho cảm xúc bất an."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Tái hiện cảm giác bỗng dưng muốn lau sạch từng cánh quạt lúc nửa đêm."},
                {"phase": "counter_intuitive_reveal", "purpose": "Vạch trần cảm giác năng suất giả tạo từ việc dọn dẹp."},
                {"phase": "scientific_mechanism", "purpose": "Giới thiệu nghiên cứu của Zeigarnik về áp lực nhận thức."},
                {"phase": "editorial_verdict", "purpose": "Khẳng định đây là cơ chế phòng vệ tâm lý trốn tránh cảm xúc."},
                {"phase": "cliffhanger_spinoff", "purpose": "Mở ra nút thắt cách đảo ngược hiệu ứng để hoàn thành bài tập trên video dài."}
            ]
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Tâm lý và hành vi đời thường",
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
            "title": "Cơn thèm dọn nhà lúc nửa đêm",
            "purpose": "Triển khai bước 1: hành vi dọn dẹp bất ngờ khi cận deadline",
            "action": "The stickman in cerulean-blue T-shirt sits in front of a laptop with deadline alert, suddenly staring with wide dot eyes at a dusty desk fan.",
            "setting": "Minimalist 2D bedroom study corner with desk and fan on warm paper-cream canvas #F8F0DC.",
            "camera": "Semantic camera: establishing wide shot transitioning into rapid focus on dust and broom",
            "narration": "Mười một giờ đêm, mai nộp báo cáo. Bạn bỗng thấy chiếc quạt bàn bám bụi dày. Bạn bật dậy lau từng cánh rồi mang quần áo đi giặt.",
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
                    "purpose": "Mở màn áp lực giờ chót lúc nửa đêm",
                    "anchor": {"vi": {"quote": "Mười một giờ đêm, mai nộp báo cáo.", "occurrence": 1}},
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
                    "purpose": "Sự chú ý bị phân tán vào vật thể bám bụi",
                    "anchor": {"vi": {"quote": "Bạn bỗng thấy chiếc quạt bàn bám bụi dày.", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "burst",
                    "narrative_situation": "hook_shock",
                    "camera_intent": "focus",
                    "shot_type": "cutaway_detail"
                },
                {
                    "id": "SC01_B3",
                    "image_id": "SC01_I3",
                    "purpose": "Hành động hăng say lau chùi chiếc quạt",
                    "anchor": {"vi": {"quote": "Bạn bật dậy lau từng cánh", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "camera_intent": "action",
                    "shot_type": "full_scene"
                },
                {
                    "id": "SC01_B4",
                    "image_id": "SC01_I4",
                    "purpose": "Lôi việc nhà ra làm liên tục để né tránh bàn làm việc",
                    "anchor": {"vi": {"quote": "rồi mang quần áo đi giặt.", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "camera_intent": "action",
                    "shot_type": "full_scene"
                }
            ],
            "images": [
                {
                    "id": "SC01_I1",
                    "description": "Iconic 2D Vietnamese indie webcomic doodle stickman in flat cerulean-blue T-shirt (#3B82C4) and slate-gray trousers (#8C857B) sitting at a small desk staring in stress at a glowing laptop with 'DEADLINE 23:59' stamped on screen, warm paper-cream background (#F8F0DC), wobbly #000000 marker line art, >=60% negative space, no 3D.",
                    "character_ids": ["CH01"],
                    "preserve": "bald white circle head stickman, cerulean-blue T-shirt, slate-gray trousers, paper-cream canvas",
                    "change": "stickman stares nervously at laptop deadline",
                    "reason": "Narration-locked full-frame beat SC01_I1",
                    "visible_text": [{"text": "CẬN DEADLINE", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "narrative_situation": "hook_shock",
                    "emphasis_text": "CẬN DEADLINE",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The doodle stickman sweats at the desk before quickly snapping his head around to notice a dusty electric fan on the floor, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I2",
                    "description": "Close-up doodle view of an old desk fan with thick wobbly black marker dust flakes clinging to wire grill and fan blades, rendered in flat warm paper-cream canvas (#F8F0DC) with hand-drawn wavy lines showing grime, >=60% negative space, zero shading.",
                    "character_ids": ["CH01"],
                    "preserve": "clean paper-cream canvas #F8F0DC, wobbly #000000 marker linework",
                    "change": "camera zooms into dusty electric fan blades",
                    "reason": "Narration-locked full-frame beat SC01_I2",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "cutaway_detail",
                    "tempo": "burst",
                    "narrative_situation": "hook_shock",
                    "emphasis_text": None,
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": False,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. A hand-drawn magnifying highlight pulses over the thick dust on the fan blades, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I3",
                    "description": "The 2D doodle stickman in cerulean-blue T-shirt (#3B82C4) enthusiastically scrubs each blade of the detached fan cage with a yellow rag, grinning with wide energetic dot eyes, sparkles popping around the fan, flat warm paper-cream background (#F8F0DC), zero 3D.",
                    "character_ids": ["CH01"],
                    "preserve": "bald white circle head stickman, cerulean-blue T-shirt, slate-gray trousers, paper-cream canvas",
                    "change": "stickman wipes fan blades energetically",
                    "reason": "Narration-locked full-frame beat SC01_I3",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "emphasis_text": None,
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The stickman briskly wipes the fan cage from left to right with tiny doodle sweat drops flying off, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I4",
                    "description": "The same 2D doodle stickman in cerulean-blue T-shirt (#3B82C4) carrying a towering laundry basket overflowing with colorful clothes, bustling happily away from his computer desk toward a washing machine, warm paper-cream background (#F8F0DC), wobbly black marker contours.",
                    "character_ids": ["CH01"],
                    "preserve": "bald white circle head stickman, cerulean-blue T-shirt, slate-gray trousers, paper-cream canvas",
                    "change": "stickman carries large laundry basket away from desk",
                    "reason": "Narration-locked full-frame beat SC01_I4",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "emphasis_text": None,
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The stickman hurries across the room balancing the tall pile of clothes as the laptop in the background sits forgotten, silent visual storytelling, no talking, no lip movement"
                }
            ]
        },
        {
            "id": "SC02",
            "title": "Cái bẫy trì hoãn tích cực",
            "purpose": "Triển khai bước 2: cái bẫy hoàn thành giả tạo xoa dịu tội lỗi",
            "action": "The stickman stands proudly admiring a sparkling tidy room, but glances nervously back at the unwritten assignment.",
            "setting": "Clean tidy doodle room with sparkling clean surfaces on warm paper-cream canvas #F8F0DC.",
            "camera": "Semantic camera: mid shot of smug expression shifting into uneasy wide shot of empty notebook",
            "narration": "Phòng sạch bóng làm bạn tưởng mình đang chăm chỉ. Nhưng đây chỉ là cách trốn tránh nỗi sợ thất bại trước bài vở đang dang dở.",
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
                    "purpose": "Hài lòng trước căn phòng sạch bóng",
                    "anchor": {"vi": {"quote": "Phòng sạch bóng", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "story_action",
                    "camera_intent": "focus",
                    "shot_type": "full_scene"
                },
                {
                    "id": "SC02_B2",
                    "image_id": "SC02_I2",
                    "purpose": "Cảm giác bản thân đã làm việc chăm chỉ",
                    "anchor": {"vi": {"quote": "làm bạn tưởng mình đang chăm chỉ.", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "story_action",
                    "camera_intent": "action",
                    "shot_type": "full_scene"
                },
                {
                    "id": "SC02_B3",
                    "image_id": "SC02_I3",
                    "purpose": "Bản chất là trốn tránh nỗi sợ thất bại",
                    "anchor": {"vi": {"quote": "Nhưng đây chỉ là cách trốn tránh nỗi sợ thất bại", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "story_action",
                    "camera_intent": "reaction",
                    "shot_type": "full_scene"
                },
                {
                    "id": "SC02_B4",
                    "image_id": "SC02_I4",
                    "purpose": "Bài vở chính vẫn dang dở trắng trơn",
                    "anchor": {"vi": {"quote": "trước bài vở đang dang dở.", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "story_action",
                    "camera_intent": "contrast",
                    "shot_type": "cutaway_detail"
                }
            ],
            "images": [
                {
                    "id": "SC02_I1",
                    "description": "The 2D doodle stickman in cerulean-blue T-shirt (#3B82C4) stands with hands on hips, smiling smugly amidst gleaming floorboards and neatly stacked shelves, surrounded by hand-drawn twinkle starbursts on paper-cream canvas (#F8F0DC).",
                    "character_ids": ["CH01"],
                    "preserve": "bald white circle head stickman, cerulean-blue T-shirt, slate-gray trousers, paper-cream canvas",
                    "change": "stickman smiles proudly at sparkling clean room",
                    "reason": "Narration-locked full-frame beat SC02_I1",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "story_action",
                    "emphasis_text": None,
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The stickman nods in satisfaction as comic twinkle marks shimmer across the clean furniture, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I2",
                    "description": "The doodle stickman in cerulean-blue T-shirt holds up a green badge labeled 'CHĂM CHỈ' with an angelic halo floating above his bald head, pretending to be ultra-productive on flat paper-cream canvas (#F8F0DC), wobbly black lines.",
                    "character_ids": ["CH01"],
                    "preserve": "bald white circle head stickman, cerulean-blue T-shirt, slate-gray trousers, paper-cream canvas",
                    "change": "stickman displays self-awarded medal with fake halo",
                    "reason": "Narration-locked full-frame beat SC02_I2",
                    "visible_text": [{"text": "CHĂM CHỈ GIẢ TẠO", "placement": "upper_third", "object": "badge"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "story_action",
                    "emphasis_text": "CHĂM CHỈ GIẢ TẠO",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The halo flickers and tilts crookedly as the stickman's confident grin begins to waver, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I3",
                    "description": "The stickman in cerulean-blue T-shirt looks sheepishly over his shoulder, a shadowy monster silhouette representing 'NỖI SỢ PHÁN XÉT' looming behind his computer chair on paper-cream background (#F8F0DC).",
                    "character_ids": ["CH01"],
                    "preserve": "bald white circle head stickman, cerulean-blue T-shirt, slate-gray trousers, paper-cream canvas",
                    "change": "stickman looks nervous as shadow of fear looms",
                    "reason": "Narration-locked full-frame beat SC02_I3",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "story_action",
                    "emphasis_text": None,
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The stickman pulls his shoulders up anxiously as the dark doodle shadow extends toward his desk, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I4",
                    "description": "Top-down doodle view of a blank white sheet of paper on the desk with only 'BÁO CÁO' written at the top and a blinking cursor at 0 words, with a large hand-drawn red question mark, flat paper-cream canvas (#F8F0DC).",
                    "character_ids": ["CH01"],
                    "preserve": "clean paper-cream canvas #F8F0DC, wobbly marker style",
                    "change": "camera shows empty document with 0 words",
                    "reason": "Narration-locked full-frame beat SC02_I4",
                    "visible_text": [{"text": "0 TỪ", "placement": "upper_third", "object": "status"}],
                    "kind": "scene",
                    "shot_type": "cutaway_detail",
                    "tempo": "normal",
                    "narrative_situation": "story_action",
                    "emphasis_text": "0 TỪ",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": False,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. A hand-drawn red cursor blinks steadily beside the blank line on the document, silent visual storytelling, no talking, no lip movement"
                }
            ]
        },
        {
            "id": "SC03",
            "title": "Cơ chế vòng lặp Zeigarnik",
            "purpose": "Triển khai bước 3: giải mã cơ chế khoa học hiệu ứng Zeigarnik",
            "action": "Illustration of psychologist Bluma Zeigarnik and open cognitive loops causing tension.",
            "setting": "Metaphorical psychology lab on flat warm paper-cream canvas #F8F0DC.",
            "camera": "Semantic camera: historical reference panning into mental tension diagram",
            "narration": "Bluma Zeigarnik phát hiện não người luôn bị ám ảnh bởi việc chưa xong. Nhiệm vụ quá khó làm não hoảng sợ nên nó tìm việc nhà gom chút dopamine.",
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
                    "purpose": "Giới thiệu nghiên cứu của Bluma Zeigarnik",
                    "anchor": {"vi": {"quote": "Bluma Zeigarnik phát hiện", "occurrence": 1}},
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
                    "purpose": "Não luôn bị ám ảnh bởi việc chưa hoàn thành",
                    "anchor": {"vi": {"quote": "não người luôn bị ám ảnh bởi việc chưa xong.", "occurrence": 1}},
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
                    "purpose": "Nhiệm vụ khó làm não bộ sợ hãi áp lực",
                    "anchor": {"vi": {"quote": "Nhiệm vụ quá khó làm não hoảng sợ", "occurrence": 1}},
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
                    "purpose": "Tìm việc nhà đơn giản để gom dopamine tức thì",
                    "anchor": {"vi": {"quote": "nên nó tìm việc nhà gom chút dopamine.", "occurrence": 1}},
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
                    "description": "A retro 1927 cafe setting sketched in wobbly black lines, a doodle waiter carrying unpaid order slips clearly visible in mind bubbles, next to a notebook labeled 'ZEIGARNIK 1927' on paper-cream canvas (#F8F0DC), >=60% negative space.",
                    "character_ids": ["CH01"],
                    "preserve": "paper-cream canvas #F8F0DC, wobbly marker line style, no 3D",
                    "change": "retro doodle illustration of 1927 waiter memory test",
                    "reason": "Narration-locked full-frame beat SC03_I1",
                    "visible_text": [{"text": "ZEIGARNIK 1927", "placement": "upper_third", "object": "notebook"}],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "emphasis_text": "ZEIGARNIK 1927",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": False,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Order receipts flutter in the air before neatly sticking to an open notepad, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I2",
                    "description": "A large hand-drawn circular open loop with glowing warning sparks at the unfinished gap, representing an open cognitive loop in memory, drawn with bold marker lines on flat paper-cream canvas (#F8F0DC).",
                    "character_ids": ["CH01"],
                    "preserve": "paper-cream canvas #F8F0DC, bold marker style, zero shading",
                    "change": "visual diagram of open cognitive tension loop",
                    "reason": "Narration-locked full-frame beat SC03_I2",
                    "visible_text": [{"text": "VÒNG LẶP CHƯA XONG", "placement": "upper_third", "object": "diagram"}],
                    "kind": "scene",
                    "shot_type": "visual_diagram",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "emphasis_text": "VÒNG LẶP CHƯA XONG",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": False,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The circular doodle loop pulses with electrical crackles around the open gap, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I3",
                    "description": "The stickman in cerulean-blue T-shirt (#3B82C4) cowering behind his hands as a giant jagged boulder labeled 'BÁO CÁO QUÁ KHÓ' rolls toward him on flat paper-cream canvas (#F8F0DC).",
                    "character_ids": ["CH01"],
                    "preserve": "bald white circle head stickman, cerulean-blue T-shirt, slate-gray trousers, paper-cream canvas",
                    "change": "stickman cowers before giant complex task boulder",
                    "reason": "Narration-locked full-frame beat SC03_I3",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "emphasis_text": None,
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The stickman leaps aside as the boulder rolls past, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I4",
                    "description": "The stickman joyfully catching small golden glowing candy candies labeled 'DOPAMINE' falling from a neatly swept pile of dust on flat paper-cream background (#F8F0DC), wobbly line art.",
                    "character_ids": ["CH01"],
                    "preserve": "bald white circle head stickman, cerulean-blue T-shirt, slate-gray trousers, paper-cream canvas",
                    "change": "stickman collects quick dopamine candies from easy chore",
                    "reason": "Narration-locked full-frame beat SC03_I4",
                    "visible_text": [{"text": "DOPAMINE NHANH", "placement": "upper_third", "object": "reward"}],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "emphasis_text": "DOPAMINE NHANH",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Golden star candies drop into the stickman's outstretched hands with cheerful bounce, silent visual storytelling, no talking, no lip movement"
                }
            ]
        },
        {
            "id": "SC04",
            "title": "Bản chất của sự trốn tránh",
            "purpose": "Triển khai bước 4: bình luận phản biện về sự trốn tránh cảm xúc",
            "action": "Editorial reflection exposing the truth about emotional avoidance versus physical tiredness.",
            "setting": "Thoughtful minimalist doodle space with metaphoric balance scales on paper-cream canvas #F8F0DC.",
            "camera": "Semantic camera: slow steady frame zooming gently into stickman reflective posture",
            "narration": "Dọn dẹp chỉ là chỗ trốn an toàn. Bạn thà mệt mỏi thể xác còn hơn ngồi đối diện với sức ép tâm lý từ trang viết trắng trơn.",
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
                    "purpose": "Dọn dẹp chỉ là chỗ trốn an toàn cho tâm lý",
                    "anchor": {"vi": {"quote": "Dọn dẹp chỉ là chỗ trốn an toàn.", "occurrence": 1}},
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
                    "purpose": "Chỗ trốn cảm xúc trước trách nhiệm",
                    "anchor": {"vi": {"quote": "Bạn thà mệt mỏi thể xác", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "focus",
                    "shot_type": "concept_metaphor"
                },
                {
                    "id": "SC04_B3",
                    "image_id": "SC04_I3",
                    "purpose": "Chấp nhận mệt mỏi thể xác để trốn áp lực trí óc",
                    "anchor": {"vi": {"quote": "còn hơn ngồi đối diện", "occurrence": 1}},
                    "effect": "none",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "contrast",
                    "shot_type": "concept_metaphor"
                },
                {
                    "id": "SC04_B4",
                    "image_id": "SC04_I4",
                    "purpose": "Sức ép tâm lý khủng khiếp từ trang giấy trắng",
                    "anchor": {"vi": {"quote": "với sức ép tâm lý từ trang viết trắng trơn.", "occurrence": 1}},
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
                    "description": "The 2D doodle stickman in cerulean-blue T-shirt (#3B82C4) sitting on an overturned bucket, chin resting on hand thoughtfully, looking at his clean floor with a calm reflective expression, warm paper-cream canvas (#F8F0DC), >=60% negative space.",
                    "character_ids": ["CH01"],
                    "preserve": "bald white circle head stickman, cerulean-blue T-shirt, slate-gray trousers, paper-cream canvas",
                    "change": "stickman sits thoughtfully resting chin on hand",
                    "reason": "Narration-locked full-frame beat SC04_I1",
                    "visible_text": [{"text": "NÉ TRÁNH CẢM XÚC", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "emphasis_text": "NÉ TRÁNH CẢM XÚC",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The stickman sighs softly and taps his finger against his chin in quiet self-realization, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I2",
                    "description": "A symbolic small doodle fortress built out of cardboard boxes, brooms, and laundry racks where the stickman hides safely from an incoming deadline mail envelope, warm paper-cream background (#F8F0DC).",
                    "character_ids": ["CH01"],
                    "preserve": "paper-cream canvas #F8F0DC, wobbly marker art",
                    "change": "stickman hides in a chore fortress",
                    "reason": "Narration-locked full-frame beat SC04_I2",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "emphasis_text": None,
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The mail envelope gently hovers outside the cardboard chore bunker, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I3",
                    "description": "A doodle balance scale: on the left pan, a heavy dumbbell representing sweaty physical chores; on the right pan, a single sheet of paper that weighs down heavily with intense cognitive stress, on paper-cream canvas (#F8F0DC).",
                    "character_ids": ["CH01"],
                    "preserve": "paper-cream canvas #F8F0DC, clean minimalist style",
                    "change": "balance scale comparing physical exhaustion vs mental dread",
                    "reason": "Narration-locked full-frame beat SC04_I3",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "emphasis_text": None,
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": False,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The balance scale tilts back and forth before steadying on the heavy stress side, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I4",
                    "description": "The stickman in cerulean-blue T-shirt sits upright at the desk, facing the glaring white laptop screen bravely with determined dot eyes, hands poised over the keyboard on paper-cream background (#F8F0DC).",
                    "character_ids": ["CH01"],
                    "preserve": "bald white circle head stickman, cerulean-blue T-shirt, slate-gray trousers, paper-cream canvas",
                    "change": "stickman sits at desk ready to face the blank page",
                    "reason": "Narration-locked full-frame beat SC04_I4",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "emphasis_text": None,
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The stickman squares his shoulders and raises his wire hands toward the keyboard, silent visual storytelling, no talking, no lip movement"
                }
            ]
        },
        {
            "id": "SC05",
            "title": "Đỉnh cao trào và chuyển đổi phễu",
            "purpose": "Triển khai bước 5: đỉnh cao trào bỏ lửng và chuyển đổi phễu sang video dài",
            "action": "Cliffhanger peak hook transitioning to clear bridge CTA and memorable closing endcard.",
            "setting": "Minimalist closing doodle canvas with channel branding on paper-cream background #F8F0DC.",
            "camera": "Semantic camera: dynamic zoom into secret strategy transitioning to branded endcard hold",
            "narration": "Làm thế nào để lừa ngược lại bộ não hoàn thành dự án đúng hạn? Vì sao não lại đòi dọn dẹp kiểu này, bản dài mình mổ xẻ trên YouTube Não Lười nhé. Gửi cho đứa bạn hay thức khuya dọn nhà trước giờ nộp bài đi bạn nhé.",
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
                    "purpose": "Đặt câu hỏi bỏ lửng về cách lừa ngược lại bộ não",
                    "anchor": {"vi": {"quote": "Làm thế nào để lừa ngược lại bộ não", "occurrence": 1}},
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
                    "purpose": "Hoàn thành dự án đúng hạn",
                    "anchor": {"vi": {"quote": "hoàn thành dự án đúng hạn?", "occurrence": 1}},
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
                    "purpose": "Cầu nối chuyển phễu sang video dài YouTube",
                    "anchor": {"vi": {"quote": "Vì sao não lại đòi dọn dẹp kiểu này, bản dài mình mổ xẻ trên YouTube Não Lười nhé.", "occurrence": 1}},
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
                    "purpose": "Lời kêu gọi chia sẻ và endcard cố định",
                    "anchor": {"vi": {"quote": "Gửi cho đứa bạn hay thức khuya dọn nhà trước giờ nộp bài đi bạn nhé.", "occurrence": 1}},
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
                    "description": "The stickman in cerulean-blue T-shirt (#3B82C4) tapping his temple with a clever wink, surrounded by swirling doodle question marks turning into bright glowing sparks and checkmarks on flat paper-cream canvas (#F8F0DC).",
                    "character_ids": ["CH01"],
                    "preserve": "bald white circle head stickman, cerulean-blue T-shirt, slate-gray trousers, paper-cream canvas",
                    "change": "stickman winks and taps temple cleverly",
                    "reason": "Narration-locked full-frame beat SC05_I1",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "cliffhanger_peak",
                    "emphasis_text": None,
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Bright hand-drawn exclamation marks and sparks flash on above the stickman head with radiating lines, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I2",
                    "description": "The stickman driving a funny whimsical doodle locomotive engine made of mechanical dials and calendars, chugging forward rapidly with completed project checkmarks flying from the chimney on paper-cream background (#F8F0DC).",
                    "character_ids": ["CH01"],
                    "preserve": "bald white circle head stickman, cerulean-blue T-shirt, slate-gray trousers, paper-cream canvas",
                    "change": "stickman operates whimsical progress engine",
                    "reason": "Narration-locked full-frame beat SC05_I2",
                    "visible_text": [{"text": "CỖ MÁY TIẾN ĐỘ", "placement": "upper_third", "object": "locomotive"}],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "narrative_situation": "cliffhanger_peak",
                    "emphasis_text": "CỖ MÁY TIẾN ĐỘ",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The doodle train chugs vigorously from left to right as checkmark steam puffs rise, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I3",
                    "description": "The stickman in cerulean-blue T-shirt pointing a friendly wire arm toward a large YouTube play window displaying 'BẢN PHÂN TÍCH ĐẦY ĐỦ - NÃO LƯỜI' on warm paper-cream canvas (#F8F0DC), clean marker lines.",
                    "character_ids": ["CH01"],
                    "preserve": "bald white circle head stickman, cerulean-blue T-shirt, slate-gray trousers, paper-cream canvas",
                    "change": "stickman points to YouTube video card",
                    "reason": "Narration-locked full-frame beat SC05_I3",
                    "visible_text": [{"text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE", "placement": "upper_third", "object": "banner"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "hold",
                    "narrative_situation": "cta_bridge",
                    "emphasis_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The YouTube window gently scales up as the stickman smiles and points, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I4",
                    "description": "Endcard frame: The 2D doodle stickman in cerulean-blue T-shirt waving a warm goodbye beside a friend holding a phone. Large bold hand-lettered text centered: 'NÃO LƯỜI' with 'BẢN ĐẦY ĐỦ TRÊN YOUTUBE', warm paper-cream background (#F8F0DC), zero gradients.",
                    "character_ids": ["CH01"],
                    "preserve": "bald white circle head stickman, cerulean-blue T-shirt, slate-gray trousers, paper-cream canvas",
                    "change": "endcard closing scene with channel name and share invite",
                    "reason": "Narration-locked full-frame beat SC05_I4",
                    "visible_text": [{"text": "NÃO LƯỜI", "placement": "upper_third", "object": "logo"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "hold",
                    "narrative_situation": "cta_close",
                    "emphasis_text": "NÃO LƯỜI",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The stickman gives a small cheerful wave as the frame holds rock solid, silent visual storytelling, no talking, no lip movement"
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
        "characters": [channel_cast("nao_luoi", "CH01")],
        "scenes": scenes_data,
        "coverage": [
            {"requirement_id": "R01", "scene_id": "SC01", "quote": "Mười một giờ đêm, mai nộp báo cáo"},
            {"requirement_id": "R02", "scene_id": "SC02", "quote": "Phòng sạch bóng làm bạn tưởng mình đang chăm chỉ"},
            {"requirement_id": "R03", "scene_id": "SC03", "quote": "Bluma Zeigarnik phát hiện não người luôn bị ám ảnh bởi việc chưa xong"},
            {"requirement_id": "R04", "scene_id": "SC04", "quote": "Dọn dẹp chỉ là chỗ trốn an toàn"},
            {"requirement_id": "R05", "scene_id": "SC05", "quote": "Làm thế nào để lừa ngược lại bộ não hoàn thành dự án đúng hạn"}
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC03",
                "quote": "Bluma Zeigarnik phát hiện não người luôn bị ám ảnh bởi việc chưa xong.",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Các nhiệm vụ chưa hoàn thành tạo ra sức căng nhận thức kéo dài trong trí nhớ làm việc."
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
    build_nao_luoi_9x16()
