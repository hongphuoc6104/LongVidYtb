#!/usr/bin/env python3
"""Batch 3 Data Generator for Hồ Sơ Kỳ Lạ (ho_so_ky_la).

Provides:
- make_hskl_short(): Generates Schema 3.0 short_9x16 spin-off package (5 scenes, 20 beats, 20 images, ~166 words)
- make_hskl_long(): Generates Schema 3.0 long_16x9 parent package (11 scenes, 66 beats, 66 images, ~735 words)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from channels.registry import channel_cast, channel_profile_stamp, get_channel


def compute_brief_hash(brief_dict: Dict[str, Any]) -> str:
    content = json.dumps(brief_dict, ensure_ascii=False, indent=2)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ==============================================================================
# 1. HỒ SƠ KỲ LẠ - SHORT 9:16
# ==============================================================================

def make_hskl_short() -> Tuple[str, Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    job_id = "ho-so-ky-la-batch3-9x16"
    parent_long_id = "ho-so-ky-la-batch3-16x9"
    channel_id = "ho_so_ky_la"
    ch = get_channel(channel_id)
    topic = "Mẩu Giấy Tamám Shud Trong Túi Áo Kín Và Vụ Án 70 Năm"
    youtube_title = "Mẩu Giấy Tamám Shud Trong Túi Áo Kín Và Vụ Án 70 Năm"  # 52 chars <= 55

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Tái hiện phát hiện mẩu giấy Tamám Shud trong túi quần bí mật của người đàn ông vô danh trên bãi biển Somerton và dẫn phễu về video dài",
        "video_type": "mystery_investigation",
        "duration": {
            "min_seconds": 40.0,
            "max_seconds": 55.0
        },
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Phát hiện tử thi không danh tính trên bãi biển Somerton"},
            {"id": "R02", "text": "Toàn bộ nhãn mác quần áo bị cắt sạch có chủ đích"},
            {"id": "R03", "text": "Bình luận về mẩu giấy cuộn chặt xé từ tập thơ hiếm"},
            {"id": "R04", "text": "Dấu vết năm dòng mật mã viết tay ở bìa sau cuốn sách"},
            {"id": "R05", "text": "Đỉnh cao trào bỏ lửng và chuyển phễu video dài"}
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
                "title": "The Unknown Man: A Investigation into the Somerton Beach Mystery",
                "reference": "Feltus, G. (2010). Klemzig.",
                "facts": [
                    "Người đàn ông vô danh được phát hiện trên bờ biển Somerton sáng ngày một tháng mười hai năm 1948.",
                    "Mẩu giấy in chữ Tamám Shud bị xé từ tập thơ Rubaiyat được cuộn chặt trong túi phụ bí mật.",
                    "Toàn bộ nhãn mác trên trang phục nạn nhân đều bị cắt sạch không để lại dấu vết."
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
                "Kể lại khúc chiết vụ án mẩu giấy Tamám Shud trong 45 giây và dẫn phễu người xem sang video phân tích dài"
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Không đòi hỏi hiểu biết trước về lịch sử trinh thám thế giới.",
            "pacing": "Chậm rãi, hồi hộp, giọng trầm bổng ly kỳ, triệt tiêu khoảng lặng chết.",
            "domain_requirements": [],
            "assumptions": [
                "Mỗi phân cảnh duy trì nhịp hình ảnh từ 1.9 đến 2.3 giây một nhịp."
            ],
            "text_style": {
                "font": "sans-serif rõ nét, cùng kiểu và độ đậm xuyên suốt",
                "color": "#111111",
                "outline": "nền giấy sáng tương phản",
                "size": "dễ đọc trên điện thoại (khung dọc 9:16)",
                "placement": "cách mép ít nhất 10%; tránh mặt và vùng phụ đề dưới cùng 18%"
            },
            "speech_rates": {
                "vi": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.15,
                    "source": "Acoustic calibrated cadence"
                },
                "en": {
                    "units_per_second": 2.5,
                    "uncertainty": 0.25,
                    "source": "Estimated English reading rate"
                }
            }
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Chiếc túi quần tây bí mật hé lộ mẩu giấy cuộn tròn có chữ Tamám Shud đóng dấu đỏ",
                "text_overlay": "TÚI ÁO BÍ MẬT",
                "contrast_pair": "Quần áo bị cắt sạch mác vs Mẩu giấy xé từ tập thơ hiếm",
                "thumbnail_prompt": "2D noir graphic-novel illustration on aged off-white canvas (#E8E2D0). High-contrast ink black (#111111) scissors cutting fabric labels, beside a tiny concealed watch pocket showing a rolled paper slip with bold evidence red circle (#C0392B) reading 'TAMÁM SHUD'. Silhouette of detective hand holding tweezers in slate grey (#5A5F66). Orthographic 2D, crisp heavy ink linework, >=60% negative space, no blood, no gore, no 3D.",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": "Hồ Sơ Mật, Kỳ Án Lịch Sử & Bí Ẩn Khoa Học",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["ho so ky la", "somerton man", "tamam shud", "ky an", "bi an", "shorts"],
            "cta_plan": {
                "cliffhanger_peak": "Mật mã năm dòng chữ viết tay ở bìa sau cuốn sách thực sự che giấu bí mật quân sự nào?",
                "bridge": "Khám phá toàn bộ hồ sơ mật vụ án Somerton trên YouTube.",
                "close": "Theo dõi kênh để cùng mở những tập hồ sơ kỳ lạ tiếp theo.",
                "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
            },
            "editorial_stance": {
                "myth_debunked": "Mẩu giấy Tamám Shud chỉ là mảnh giấy rác vô tình mắc lại trong túi áo nạn nhân.",
                "why_generic_advice_fails": "Giả thuyết ngẫu nhiên sụp đổ khi cảnh sát tìm thấy cuốn sách bị xé đúng góc giấy ấy trong một chiếc xe khóa kín.",
                "channel_verdict": "Người đàn ông mang theo một thông điệp kết thúc được mã hóa có chủ đích trước khi bước vào cõi vĩnh hằng.",
                "tradeoff_or_blindspot": "Tập trung giải mật mã chữ viết tay ở bìa sau cuốn sách có thể khiến người ta bỏ quên manh mối về người phụ nữ bí ẩn tên Jo."
            },
            "actionable_value": {
                "core_mechanism": "Truy tìm nguồn gốc tài liệu thông qua giám định bản in, loại giấy và vết khớp xé chính xác từng sợi xenlulozo.",
                "practical_rule_of_thumb": "Không bao giờ bỏ qua các chi tiết siêu nhỏ được may giấu trong lớp lót trang phục khi thu thập hiện trường.",
                "real_world_scenario": "Rà soát túi phụ của túi quần tây để phát hiện mẩu giấy cuộn chặt mà việc khám nghiệm sơ sài ban đầu đã bỏ sót."
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Chiếc túi quần tây bí mật hé lộ mẩu giấy cuộn tròn có chữ Tamám Shud đóng dấu đỏ",
            "text_overlay": "TÚI ÁO BÍ MẬT",
            "contrast_pair": "Quần áo bị cắt sạch mác vs Mẩu giấy xé từ tập thơ hiếm",
            "thumbnail_prompt": "2D noir graphic-novel illustration on aged off-white canvas (#E8E2D0). High-contrast ink black (#111111) scissors cutting fabric labels, beside a tiny concealed watch pocket showing a rolled paper slip with bold evidence red circle (#C0392B) reading 'TAMÁM SHUD'. Silhouette of detective hand holding tweezers in slate grey (#5A5F66). Orthographic 2D, crisp heavy ink linework, >=60% negative space, no blood, no gore, no 3D.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Hồ Sơ Mật, Kỳ Án Lịch Sử & Bí Ẩn Khoa Học",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["ho so ky la", "somerton man", "tamam shud", "ky an", "bi an", "shorts"],
        "parent_long_id": parent_long_id,
        "cta_plan": {
            "cliffhanger_peak": "Mật mã năm dòng chữ viết tay ở bìa sau cuốn sách thực sự che giấu bí mật quân sự nào?",
            "bridge": "Khám phá toàn bộ hồ sơ mật vụ án Somerton trên YouTube.",
            "close": "Theo dõi kênh để cùng mở những tập hồ sơ kỳ lạ tiếp theo.",
            "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "bridge_templates": list(ch.engagement.bridge_templates),
            "close_templates": list(ch.engagement.close_templates),
            "endcard_text": ch.engagement.endcard_text,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": {
            "myth_debunked": "Mẩu giấy Tamám Shud chỉ là mảnh giấy rác vô tình mắc lại trong túi áo nạn nhân.",
            "why_generic_advice_fails": "Giả thuyết ngẫu nhiên sụp đổ khi cảnh sát tìm thấy cuốn sách bị xé đúng góc giấy ấy trong một chiếc xe khóa kín.",
            "channel_verdict": "Người đàn ông mang theo một thông điệp kết thúc được mã hóa có chủ đích trước khi bước vào cõi vĩnh hằng.",
            "tradeoff_or_blindspot": "Tập trung giải mật mã chữ viết tay ở bìa sau cuốn sách có thể khiến người ta bỏ quên manh mối về người phụ nữ bí ẩn tên Jo."
        },
        "actionable_value": {
            "core_mechanism": "Truy tìm nguồn gốc tài liệu thông qua giám định bản in, loại giấy và vết khớp xé chính xác từng sợi xenlulozo.",
            "practical_rule_of_thumb": "Không bao giờ bỏ qua các chi tiết siêu nhỏ được may giấu trong lớp lót trang phục khi thu thập hiện trường.",
            "real_world_scenario": "Rà soát túi phụ của túi quần tây để phát hiện mẩu giấy cuộn chặt mà việc khám nghiệm sơ sài ban đầu đã bỏ sót."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Khởi đầu kịch tính với phát hiện tử thi bí ẩn bên bờ biển", "requirements": ["R01"], "transition": "Chuyển tiếp sang chi tiết nhãn mác bị cắt"},
            {"scene_id": "SC02", "purpose": "Phân tích hiện trường hoàn hảo không danh tính", "requirements": ["R02"], "transition": "Khám phá túi áo bí mật"},
            {"scene_id": "SC03", "purpose": "Bình luận sắc bén về mẩu giấy xé mang dòng chữ kết thúc", "requirements": ["R03"], "transition": "Lần tìm cuốn sách thơ cổ"},
            {"scene_id": "SC04", "purpose": "Mở rộng dấu vết cuốn sách và chuỗi ký tự bí ẩn", "requirements": ["R04"], "transition": "Đẩy lên cao trào câu hỏi mở"},
            {"scene_id": "SC05", "purpose": "Đỉnh cao trào bỏ lửng và chuyển phễu người xem sang video dài", "requirements": ["R05"], "transition": "Kết thúc video"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Các kênh Kỳ Án / Hồ Sơ",
                    "top_performing_videos": [
                        {
                            "title": "Người đàn ông bí ẩn Somerton và mẩu giấy mật mã",
                            "views": "1.8M views",
                            "hook_technique": "Cận cảnh mẩu giấy cổ Tamám Shud cuộn tròn trong túi quần bí mật.",
                            "pacing_structure": "Phát hiện bờ biển -> Manh mối nhãn áo bị cắt -> Mẩu giấy kỳ lạ -> Cắt ngang tại mật mã.",
                            "retention_driver": "Không khí điều tra trinh thám đặc quánh, chi tiết kỳ lạ có thật."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Dừng ngay tại thời điểm tìm thấy đoạn mật mã chưa giải.",
                        "Tông giọng thám tử kể chuyện lạnh lùng, lôi cuốn."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 19,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Tử thi mặc âu phục chỉnh tề nằm trên cát lạnh đối lập với nhãn mác bị cắt sạch sẽ.",
                "counter_intuitive_truth_slap": "Không phải ngẫu nhiên mà mọi danh tính bị xóa sạch, đó là dấu hiệu của một điệp vụ tình báo hoàn hảo."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Mở đầu với hình ảnh tử thi vô danh trên bãi biển hoang vắng."},
                {"phase": "empirical_conflict", "purpose": "Chỉ ra sự biến mất hoàn toàn của mọi nhãn hiệu trên y phục."},
                {"phase": "structural_model", "purpose": "Phát hiện mẩu giấy cuộn chặt mang chữ Tamám Shud."},
                {"phase": "actionable_resolution", "purpose": "Liên kết mảnh giấy với tập thơ quý và mật mã bí ẩn."},
                {"phase": "cliffhanger_spinoff", "purpose": "Dừng ở nút thắt mật mã và điều hướng sang YouTube."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Daisy-chain linking 2D noir forensic evidence frames."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Hồ Sơ Mật, Kỳ Án Lịch Sử & Bí Ẩn Khoa Học",
            "myth_debunked": "Đây là một vụ tai nạn hay đột quỵ bình thường của người vô gia cư.",
            "channel_verdict": "Sự xóa dấu vết bài bản chứng minh đây là một cái chết được dàn dựng chuyên nghiệp thời Chiến tranh Lạnh.",
            "actionable_rule_of_thumb": "Quan sát tỉ mỉ các chi tiết vi mô bị giấu kín trong đường may y phục."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "Mật mã năm dòng chữ viết tay ở bìa sau cuốn sách thực sự che giấu bí mật quân sự nào?",
            "bridge": "Khám phá toàn bộ hồ sơ mật vụ án Somerton trên YouTube.",
            "close": "Theo dõi kênh để cùng mở những tập hồ sơ kỳ lạ tiếp theo.",
            "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
        }
    }

    # 5 scenes, 20 beats, 20 unique images, ~166 words total (~33 words/scene)
    scenes = [
        {
            "id": "SC01",
            "title": "Tử thi bí ẩn trên bãi cát Somerton",
            "purpose": "Thiết lập bối cảnh mở đầu vụ án kỳ lạ bậc nhất lịch sử nước Úc",
            "action": "Thám tử đứng trước bờ biển hoang vắng vào buổi bình minh ảm đạm",
            "setting": "Bãi biển Somerton lộng gió dưới bầu trời xám xịt năm 1948",
            "camera": "Toàn cảnh góc rộng chuyển dần sang cận cảnh hiện trường trên cát",
            "narration": "Sáng sớm ngày một tháng mười hai năm 1948, người ta phát hiện một tử thi nằm trên bờ cát Somerton. Ông mặc âu phục chỉnh tề, nhưng không ai biết tung tích nạn nhân.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Hồi hộp, điềm tĩnh, u tối",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "images": [
                {
                    "id": "SC01_I1",
                    "description": "2D noir graphic-novel illustration on aged off-white paper #E8E2D0. Faceless detective in flat slate-grey long coat #5A5F66 and fedora hat seen from behind, looking out at a bleak shoreline with ink-black ocean waves #111111, orthographic 2D, crisp heavy ink linework, >=60% negative space, no blood, no 3D.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Aged paper #E8E2D0, heavy black ink outlines #111111, slate grey coat #5A5F66.",
                    "change": "Detective observing the gloomy beach shore.",
                    "reason": "Establishing cold open noir beat SC01_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "environment",
                    "tempo": "burst",
                    "narrative_situation": "hook_shock",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D noir animation. The detective coat tails flutter slightly in the ocean breeze under rolling ink clouds, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I2",
                    "description": "2D noir graphic-novel illustration. Silhouette outline of a man in a tailored suit resting peacefully against the sea wall on aged off-white sand #E8E2D0, heavy ink shadows #111111, with a crisp evidence red chalk boundary #C0392B marking the spot.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Aged off-white paper, ink black shadows, evidence red accent.",
                    "change": "Forensic scene outline on the beach.",
                    "reason": "Showing victim discovery SC01_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D noir animation. The red chalk contour pulses subtly on the aged paper canvas, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I3",
                    "description": "2D noir graphic-novel illustration. Macro view of a gentleman flat collar and tailored wool coat in slate grey #5A5F66 on aged off-white background #E8E2D0, drawn flat with heavy black ink hatching #111111.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Noir palette, ink linework, off-white paper texture.",
                    "change": "Focus on tailored gentlemen attire.",
                    "reason": "Detailing victim clothing SC01_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "macro_prop",
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D noir animation. The fabric textures sharpen smoothly under magnifying glass focus, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I4",
                    "description": "2D noir graphic-novel illustration. A blank identity dossier file folder stamped with an evidence red stamp #C0392B reading 'UNIDENTIFIED' on aged paper #E8E2D0, crisp ink lines #111111.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Noir aesthetic, aged paper canvas, red evidence stamp.",
                    "change": "Mystery identity case file stamp.",
                    "reason": "Closing opening hook scene SC01_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "white_card",
                    "tempo": "normal",
                    "narrative_situation": "hook_shock",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D noir animation. The dossier folder closes with a decisive slide, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC01_B1",
                    "image_id": "SC01_I1",
                    "purpose": "Nhịp phát hiện: sáng sớm năm 1948",
                    "anchor": {"vi": {"quote": "Sáng sớm ngày một tháng mười hai năm 1948,", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "burst",
                    "narrative_situation": "hook_shock"
                },
                {
                    "id": "SC01_B2",
                    "image_id": "SC01_I2",
                    "purpose": "Nhịp hiện trường bờ cát",
                    "anchor": {"vi": {"quote": "người ta phát hiện một tử thi nằm trên bờ cát Somerton.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "hook_shock"
                },
                {
                    "id": "SC01_B3",
                    "image_id": "SC01_I3",
                    "purpose": "Nhịp trang phục âu phục",
                    "anchor": {"vi": {"quote": "Ông mặc âu phục chỉnh tề,", "occurrence": 1}},
                    "effect": "fade",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "hook_shock"
                },
                {
                    "id": "SC01_B4",
                    "image_id": "SC01_I4",
                    "purpose": "Nhịp danh tính hoàn toàn vô danh",
                    "anchor": {"vi": {"quote": "nhưng không ai biết tung tích nạn nhân.", "occurrence": 1}},
                    "effect": "hold",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "hook_shock"
                }
            ]
        },
        {
            "id": "SC02",
            "title": "Mọi dấu vết danh tính bị tẩy xóa",
            "purpose": "Làm rõ sự biến mất kỳ lạ của nhãn mác và đồ tùy thân",
            "action": "Thám tử lật xem từng món đồ thu thập được tại hiện trường",
            "setting": "Bàn khám nghiệm pháp y tối giản phủ bóng đen trắng",
            "camera": "Cận cảnh bàn tay thám tử mang găng lật từng mép vải",
            "narration": "Không ví tiền, không giấy tờ. Toàn bộ nhãn mác trên áo khoác, quần tây và đồ lót đều bị dùng kéo cắt sạch dấu tích, xóa bỏ hoàn toàn xuất xứ trang phục.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Trầm tĩnh, bí ẩn, điều tra",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "before_after_contrast",
            "images": [
                {
                    "id": "SC02_I1",
                    "description": "2D noir graphic-novel illustration. A flat forensic evidence tray on aged paper #E8E2D0 holding an empty leather wallet frame with zero cards and zero coins, drawn with sharp black ink linework #111111.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Aged paper, noir heavy ink lines, slate grey shadows.",
                    "change": "Empty evidence tray displaying lack of identification.",
                    "reason": "Showing zero documents beat SC02_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "still_life",
                    "tempo": "fast",
                    "narrative_situation": "before_after_contrast",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D noir animation. Subtle overhead light flicker illuminates the empty tray, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I2",
                    "description": "2D noir graphic-novel illustration. Extreme close up of sharp tailor scissors in heavy black ink #111111 cutting precisely around a cloth garment label on aged off-white canvas #E8E2D0, leaving frayed threads.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Noir graphic style, aged off-white paper, sharp black ink.",
                    "change": "Scissors snipping clothing labels.",
                    "reason": "Illustrating deliberate removal of labels SC02_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "cutaway_detail",
                    "tempo": "normal",
                    "narrative_situation": "before_after_contrast",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D noir animation. The tailor scissors snip with mechanical precision, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I3",
                    "description": "2D noir graphic-novel illustration. Multiple clothing tags in slate grey #5A5F66 cleanly severed and crossed out with evidence red slashes #C0392B on aged paper background #E8E2D0.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Noir palette, off-white texture, evidence red slashes.",
                    "change": "Multiple severed tags showing systematic erasure.",
                    "reason": "Emphasizing systematic removal SC02_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "narrative_situation": "before_after_contrast",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D noir animation. The red slashes draw across the labels in sequence, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I4",
                    "description": "2D noir graphic-novel illustration. Silhouette of the detective holding a magnifying glass over an empty coat collar lining, searching in vain for laundry marks on aged paper #E8E2D0.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Detective silhouette in long coat, aged paper, black ink linework.",
                    "change": "Detective examining collar with magnifying lens.",
                    "reason": "Detective scrutinizing evidence SC02_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "before_after_contrast",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D noir animation. The magnifying glass glides smoothly across the fabric weave, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC02_B1",
                    "image_id": "SC02_I1",
                    "purpose": "Nhịp không tài liệu tùy thân",
                    "anchor": {"vi": {"quote": "Không ví tiền, không giấy tờ.", "occurrence": 1}},
                    "effect": "fade",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "before_after_contrast"
                },
                {
                    "id": "SC02_B2",
                    "image_id": "SC02_I2",
                    "purpose": "Nhịp chi tiết nhãn mác bị cắt",
                    "anchor": {"vi": {"quote": "Toàn bộ nhãn mác trên áo khoác,", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "before_after_contrast"
                },
                {
                    "id": "SC02_B3",
                    "image_id": "SC02_I3",
                    "purpose": "Nhịp cắt sạch dấu vết",
                    "anchor": {"vi": {"quote": "quần tây và đồ lót đều bị dùng kéo cắt sạch dấu tích,", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "before_after_contrast"
                },
                {
                    "id": "SC02_B4",
                    "image_id": "SC02_I4",
                    "purpose": "Nhịp xóa bỏ xuất xứ",
                    "anchor": {"vi": {"quote": "xóa bỏ hoàn toàn xuất xứ trang phục.", "occurrence": 1}},
                    "effect": "hold",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "before_after_contrast"
                }
            ]
        },
        {
            "id": "SC03",
            "title": "Bình luận: Mẩu giấy Tamám Shud trong túi kín",
            "purpose": "Tập trung vào chi tiết then chốt hé lộ thông điệp bí ẩn",
            "action": "Thám tử dùng nhíp rút mẩu giấy cuộn chặt từ đáy túi quần bí mật",
            "setting": "Bàn giám định kính hiển vi trong phòng tối",
            "camera": "Siêu cận cảnh chuyển động gắp mẩu giấy và mở dần từng nếp gấp",
            "narration": "Đến tháng tư năm 1949, chuyên gia tìm thấy một chiếc túi phụ bí mật may sâu trong cạp quần. Đáy túi giấu mẩu giấy cuộn chặt in hai chữ Ba Tư: Tamám Shud, nghĩa là kết thúc.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Lạnh lùng, kịch tính, lôi cuốn",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images": [
                {
                    "id": "SC03_I1",
                    "description": "2D noir graphic-novel illustration. Cross section diagram of a gentleman trousers waistband revealing a tiny hidden pocket sewn deep inside on aged off-white canvas #E8E2D0, crisp black ink linework #111111.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Aged paper, noir heavy ink linework, technical diagram aesthetic.",
                    "change": "Revealing hidden fob pocket in waistband.",
                    "reason": "Setting up the hidden pocket beat SC03_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "visual_diagram",
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D noir animation. A fine red pointer traces the concealed pocket seam, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I2",
                    "description": "2D noir graphic-novel illustration. Steel tweezers in heavy black ink #111111 carefully extracting a tightly rolled scroll of paper from dark fabric folds on aged off-white background #E8E2D0.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Aged paper canvas, slate grey shading, sharp forensic ink style.",
                    "change": "Tweezers pulling out rolled paper slip.",
                    "reason": "Showing extraction of evidence SC03_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "cutaway_detail",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D noir animation. The tweezers draw the curled slip out slowly and steadily, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I3",
                    "description": "2D noir graphic-novel illustration. The paper slip unrolled flat on aged paper #E8E2D0, showing ornate Persian font printing the exact phrase 'TAMÁM SHUD', circled with an evidence red loop #C0392B.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Aged paper texture, crisp black lettering, evidence red ring.",
                    "change": "Unrolled slip displaying the words Tamám Shud.",
                    "reason": "Key reveal of the famous words SC03_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "macro_prop",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D noir animation. The red circular loop tightens with forensic emphasis, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I4",
                    "description": "2D noir graphic-novel illustration. Silhouette of the detective holding the paper scrap in profile, looking thoughtfully into heavy slate-grey shadows #5A5F66 on aged off-white canvas #E8E2D0.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Detective silhouette, aged paper, ink black contrast.",
                    "change": "Detective reflecting on the cryptic phrase.",
                    "reason": "Closing editorial commentary with atmospheric silhouette SC03_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D noir animation. Subtle shadow shift crosses the detective brim hat, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC03_B1",
                    "image_id": "SC03_I1",
                    "purpose": "Nhịp phát hiện túi phụ bí mật",
                    "anchor": {"vi": {"quote": "Đến tháng tư năm 1949,", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary"
                },
                {
                    "id": "SC03_B2",
                    "image_id": "SC03_I2",
                    "purpose": "Nhịp túi giấu trong cạp quần",
                    "anchor": {"vi": {"quote": "chuyên gia tìm thấy một chiếc túi phụ bí mật may sâu trong cạp quần.", "occurrence": 1}},
                    "effect": "fade",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary"
                },
                {
                    "id": "SC03_B3",
                    "image_id": "SC03_I3",
                    "purpose": "Nhịp mẩu giấy cuộn chặt",
                    "anchor": {"vi": {"quote": "Đáy túi giấu mẩu giấy cuộn chặt", "occurrence": 1}},
                    "effect": "zoom_in",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary"
                },
                {
                    "id": "SC03_B4",
                    "image_id": "SC03_I4",
                    "purpose": "Nhịp ý nghĩa kết thúc",
                    "anchor": {"vi": {"quote": "in hai chữ Ba Tư: Tamám Shud, nghĩa là kết thúc.", "occurrence": 1}},
                    "effect": "hold",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary"
                }
            ]
        },
        {
            "id": "SC04",
            "title": "Cuốn sách thơ cổ và năm dòng mật mã",
            "purpose": "Giải thích nguồn gốc mẩu giấy từ tập thơ Rubaiyat và mật mã ở bìa sau",
            "action": "Ghép mẩu giấy vào trang cuối cuốn sách và lật xem bìa sau",
            "setting": "Bàn nghiên cứu tài liệu với đèn bàn cổ điển",
            "camera": "Góc quay từ trên xuống đối chiếu vết xé khớp từng milimet",
            "narration": "Mảnh giấy khớp chính xác từng thớ sợi với tập thơ Rubaiyat tìm thấy trong một chiếc xe gần đó. Ở bìa sau cuốn sách là chuỗi ký tự viết tay bí ẩn chưa ai giải nổi.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Hồi hộp, giải mã, cân não",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "mechanism_step",
            "images": [
                {
                    "id": "SC04_I1",
                    "description": "2D noir graphic-novel illustration. Antique leatherbound book titled 'RUBAIYAT OF OMAR KHAYYAM' drawn flat with intricate ink black filigree #111111 on aged off-white paper #E8E2D0.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Aged paper background, crisp black ink linework.",
                    "change": "Displaying rare Persian poetry book.",
                    "reason": "Introducing the source poetry book SC04_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "macro_prop",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D noir animation. The leather cover texture shifts gently under warm lamplight, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I2",
                    "description": "2D noir graphic-novel illustration. Split frame showing the torn paper scrap fitting perfectly with microscopic fiber alignment into the torn corner of the book final page on aged paper #E8E2D0.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Aged off-white paper, ink black linework, forensic precision.",
                    "change": "Microscopic tear edge match between scrap and page.",
                    "reason": "Proving the physical match SC04_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "visual_diagram",
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D noir animation. The torn paper fragment glides into place with flawless alignment, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I3",
                    "description": "2D noir graphic-novel illustration. The back cover of the book showing five faint handwritten lines of mysterious cipher letters in irregular penciled capitals, highlighted with evidence red underlines #C0392B.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Aged paper, noir pencil hatching, evidence red marks.",
                    "change": "Revealing the 5-line handwritten cipher.",
                    "reason": "Displaying the unsolved cipher SC04_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "white_card",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D noir animation. The red underlines trace beneath the cryptic letters one by one, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I4",
                    "description": "2D noir graphic-novel illustration. Complex codebreaker cipher grid in ink black #111111 with question marks and military radio antenna towers drawn flat on aged off-white canvas #E8E2D0.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Noir palette, technical code-breaking aesthetic, clean paper canvas.",
                    "change": "Cryptanalysis visualization of the unsolved puzzle.",
                    "reason": "Framing the codebreaker dilemma SC04_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D noir animation. Cryptic cipher letters shuffle softly across the grid, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC04_B1",
                    "image_id": "SC04_I1",
                    "purpose": "Nhịp khớp từng thớ sợi",
                    "anchor": {"vi": {"quote": "Mảnh giấy khớp chính xác từng thớ sợi", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step"
                },
                {
                    "id": "SC04_B2",
                    "image_id": "SC04_I2",
                    "purpose": "Nhịp tập thơ trong xe",
                    "anchor": {"vi": {"quote": "với tập thơ Rubaiyat tìm thấy trong một chiếc xe gần đó.", "occurrence": 1}},
                    "effect": "fade",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step"
                },
                {
                    "id": "SC04_B3",
                    "image_id": "SC04_I3",
                    "purpose": "Nhịp chuỗi ký tự bìa sau",
                    "anchor": {"vi": {"quote": "Ở bìa sau cuốn sách là chuỗi ký tự viết tay", "occurrence": 1}},
                    "effect": "zoom_in",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step"
                },
                {
                    "id": "SC04_B4",
                    "image_id": "SC04_I4",
                    "purpose": "Nhịp chưa ai giải nổi",
                    "anchor": {"vi": {"quote": "bí ẩn chưa ai giải nổi.", "occurrence": 1}},
                    "effect": "hold",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step"
                }
            ]
        },
        {
            "id": "SC05",
            "title": "Đỉnh cao trào và lời mời lật mở hồ sơ",
            "purpose": "Cắt đúng đỉnh cao trào bí ẩn và điều hướng khán giả sang video dài YouTube",
            "action": "Thám tử nhìn vào tập hồ sơ mật rồi quay sang nhìn người xem",
            "setting": "Phòng hồ sơ lưu trữ với hàng ngàn ngăn kéo hồ sơ bí mật",
            "camera": "Trung cảnh chuyển dần sang endcard chính thức của Hồ Sơ Kỳ Lạ",
            "narration": "Người đàn ông đó là ai, và năm dòng mật mã che giấu bí mật gì? Khám phá toàn bộ hồ sơ mật vụ án Somerton trên YouTube. Theo dõi kênh để cùng mở những tập hồ sơ kỳ lạ tiếp theo.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Lôi cuốn, hồi hộp, thôi thúc",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "cliffhanger_peak",
            "images": [
                {
                    "id": "SC05_I1",
                    "description": "2D noir graphic-novel illustration. Silhouette of the faceless detective standing before an imposing wall of dark archive filing cabinets #111111 on aged paper #E8E2D0, holding a glowing red evidence dossier #C0392B.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Aged paper, noir heavy shadows, red evidence accent.",
                    "change": "Posing the unanswered identity question.",
                    "reason": "Setting the mystery cliffhanger SC05_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "cliffhanger_peak",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D noir animation. Archive drawer slides slightly open revealing dark files within, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I2",
                    "description": "2D noir graphic-novel illustration. A shadowy Cold War radar station and telegraph lines crossing behind the five mysterious cipher lines, rendered with heavy black ink strokes #111111 on aged paper #E8E2D0.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Aged paper background, black ink lines, espionage atmosphere.",
                    "change": "Teasing Cold War espionage theories.",
                    "reason": "Escalating espionage open loop SC05_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "narrative_situation": "cliffhanger_peak",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D noir animation. Telegraph needles tick with ominous rhythmic motion, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I3",
                    "description": "2D noir graphic-novel illustration. Faceless detective in slate-grey trench coat points calmly toward a detailed case report folder labeled 'SOMERTON FULL DOSSIER' with red wax seal on aged paper #E8E2D0.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Detective in slate-grey coat, aged paper, red wax seal.",
                    "change": "Detective gestures toward full YouTube dossier.",
                    "reason": "Bridge CTA invitation beat SC05_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "cta_bridge",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D noir animation. The red wax seal gleams with crisp contrast, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I4",
                    "description": "2D noir graphic-novel channel endcard on aged off-white paper #E8E2D0. Faceless detective silhouette in long slate-grey coat and hat standing beside official channel seal in ink black #111111 with hand-lettered banner 'BẢN ĐẦY ĐỦ TRÊN YOUTUBE', evidence red circular accent #C0392B.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Aged paper #E8E2D0, detective silhouette, ink black and evidence red.",
                    "change": "Official channel endcard illustration.",
                    "reason": "Final hold endcard SC05_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "white_card",
                    "tempo": "hold",
                    "narrative_situation": "cta_close",
                    "has_character": True,
                    "is_endcard": True,
                    "motion_prompt": "Smooth 2D noir animation, gentle breathing idle hold, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC05_B1",
                    "image_id": "SC05_I1",
                    "purpose": "Nhịp câu hỏi thân phận",
                    "anchor": {"vi": {"quote": "Người đàn ông đó là ai,", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "cliffhanger_peak"
                },
                {
                    "id": "SC05_B2",
                    "image_id": "SC05_I2",
                    "purpose": "Nhịp câu hỏi mật mã",
                    "anchor": {"vi": {"quote": "và năm dòng mật mã che giấu bí mật gì?", "occurrence": 1}},
                    "effect": "zoom_in",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "cliffhanger_peak"
                },
                {
                    "id": "SC05_B3",
                    "image_id": "SC05_I3",
                    "purpose": "Nhịp cầu nối video dài YouTube",
                    "anchor": {"vi": {"quote": "Khám phá toàn bộ hồ sơ mật vụ án Somerton trên YouTube.", "occurrence": 1}},
                    "effect": "fade",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "cta_bridge"
                },
                {
                    "id": "SC05_B4",
                    "image_id": "SC05_I4",
                    "purpose": "Nhịp kêu gọi theo dõi mở hồ sơ tiếp",
                    "anchor": {"vi": {"quote": "Theo dõi kênh để cùng mở những tập hồ sơ kỳ lạ tiếp theo.", "occurrence": 1}},
                    "effect": "hold",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "hold",
                    "narrative_situation": "cta_close",
                    "is_endcard": True
                }
            ]
        }
    ]

    content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": compute_brief_hash(brief),
        "topic": topic,
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": [channel_cast(channel_id, "CH01")],
        "scenes": scenes,
        "coverage": [
            {"requirement_id": "R01", "scene_id": "SC01", "quote": "Sáng sớm ngày một tháng mười hai năm 1948, người ta phát hiện một tử thi nằm trên bờ cát Somerton."},
            {"requirement_id": "R02", "scene_id": "SC02", "quote": "Không ví tiền, không giấy tờ."},
            {"requirement_id": "R03", "scene_id": "SC03", "quote": "Đáy túi giấu mẩu giấy cuộn chặt in hai chữ Ba Tư: Tamám Shud, nghĩa là kết thúc."},
            {"requirement_id": "R04", "scene_id": "SC04", "quote": "Mảnh giấy khớp chính xác từng thớ sợi với tập thơ Rubaiyat tìm thấy trong một chiếc xe gần đó."},
            {"requirement_id": "R05", "scene_id": "SC05", "quote": "Khám phá toàn bộ hồ sơ mật vụ án Somerton trên YouTube."}
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC01",
                "quote": "Sáng sớm ngày một tháng mười hai năm 1948, người ta phát hiện một tử thi nằm trên bờ cát Somerton.",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Người đàn ông vô danh được phát hiện trên bờ biển Somerton sáng ngày một tháng mười hai năm 1948."
            },
            {
                "scene_id": "SC02",
                "quote": "quần tây và đồ lót đều bị dùng kéo cắt sạch dấu tích,",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Toàn bộ nhãn mác trên trang phục nạn nhân đều bị cắt sạch không để lại dấu vết."
            },
            {
                "scene_id": "SC03",
                "quote": "Đáy túi giấu mẩu giấy cuộn chặt in hai chữ Ba Tư: Tamám Shud, nghĩa là kết thúc.",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Mẩu giấy in chữ Tamám Shud bị xé từ tập thơ Rubaiyat được cuộn chặt trong túi phụ bí mật."
            }
        ],
        "revision_response": [],
        "open_questions": []
    }

    return job_id, brief, outline, competitor_research, content


# ==============================================================================
# 2. HỒ SƠ KỲ LẠ - LONG 16:9
# ==============================================================================

def make_hskl_long() -> Tuple[str, Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    job_id = "ho-so-ky-la-batch3-16x9"
    channel_id = "ho_so_ky_la"
    ch = get_channel(channel_id)
    topic = "Hồ Sơ Somerton: Người Đàn Ông Bí Ẩn Và Mẩu Giấy Tamám Shud"
    youtube_title = "Hồ Sơ Somerton: Người Đàn Ông Và Mẩu Giấy Tamám Shud"  # 52 chars <= 55

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Điều tra toàn diện vụ án người đàn ông Somerton năm 1948: từ tử thi không nhãn mác, mẩu giấy Tamám Shud, cuốn sách thơ Rubaiyat, đến năm dòng mật mã chưa có lời giải",
        "video_type": "investigative_documentary",
        "duration": {
            "min_seconds": 180.0,
            "max_seconds": 240.0
        },
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "Phát hiện tử thi bí ẩn trên bãi biển Somerton"},
            {"id": "R02", "text": "Khám nghiệm hiện trường và sự biến mất hoàn toàn của nhãn mác"},
            {"id": "R03", "text": "Chiếc vali bí ẩn gửi tại nhà ga xe lửa Adelaide"},
            {"id": "R04", "text": "Bình luận chuyên sâu về sự dàn dựng hoàn hảo thời Chiến tranh Lạnh"},
            {"id": "R05", "text": "Phát hiện mẩu giấy cuộn chặt in hai chữ Tamám Shud"},
            {"id": "R06", "text": "Truy tìm cuốn sách thơ cổ Rubaiyat của Omar Khayyam"},
            {"id": "R07", "text": "Năm dòng mật mã bí ẩn viết tay ở bìa sau cuốn sách"},
            {"id": "R08", "text": "Bình luận then chốt về danh tính và manh mối y tá Jo"},
            {"id": "R09", "text": "Các giả thuyết điệp viên đối trọng: Tình báo Xô Viết hay MI6"},
            {"id": "R10", "text": "Kết quả xét nghiệm ADN hiện đại và những khúc mắc còn lại"},
            {"id": "R11", "text": "Tổng kết hồ sơ kỳ án và lời kết của thám tử"}
        ],
        "language": "vi",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "The Unknown Man: A Investigation into the Somerton Beach Mystery",
                "reference": "Feltus, G. (2010). Klemzig.",
                "facts": [
                    "Người đàn ông vô danh được phát hiện trên bãi biển Somerton ngày một tháng mười hai năm 1948.",
                    "Mẩu giấy xé mang chữ Tamám Shud được giấu kín trong túi phụ quần tây.",
                    "Toàn bộ nhãn mác trên trang phục nạn nhân đều bị cắt sạch không để lại tung tích.",
                    "Chiếc vali gửi ở ga tàu Adelaide chứa quần áo cũng bị xóa hết nhãn hiệu.",
                    "Bìa sau cuốn sách thơ Rubaiyat chứa mật mã chữ cái viết tay chưa có lời giải."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "vi",
                "subtitles": True,
                "voice": ch.voice,
                "speed": ch.speed
            }
        ],
        "planning": {
            "success_criteria": [
                "Xây dựng hồ sơ tài liệu trinh thám noir sâu sắc, lôi cuốn, mở nút thắt từng lớp theo chuẩn V3"
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Không đòi hỏi hiểu biết trước về lịch sử trinh thám.",
            "pacing": "Trầm tĩnh, từng bước mở chứng cứ, nhịp visual liên tục từ 2.4 đến 3.1 giây.",
            "domain_requirements": [],
            "assumptions": [
                "Mỗi phân cảnh trung bình 6 nhịp hình ảnh, duy trì nhịp noir tương phản cao."
            ],
            "text_style": {
                "font": "sans-serif rõ nét, cùng kiểu và độ đậm xuyên suốt",
                "color": "#111111",
                "outline": "nền giấy sáng tương phản",
                "size": "dễ đọc trên màn hình ngang (16:9)",
                "placement": "cách mép ít nhất 10%; tránh mặt và vùng phụ đề dưới cùng 15%"
            },
            "speech_rates": {
                "vi": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.15,
                    "source": "Acoustic calibrated cadence"
                },
                "en": {
                    "units_per_second": 2.5,
                    "uncertainty": 0.25,
                    "source": "Estimated English reading rate"
                }
            }
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Bóng lưng thám tử áo măng tô xám soi kính lúp vào mẩu giấy Tamám Shud viền đỏ trên bãi biển Somerton",
                "text_overlay": "MẨU GIẤY BÍ ẨN",
                "contrast_pair": "Tử thi hoàn hảo không danh tính vs Mẩu giấy mật mã xé từ tập thơ cổ",
                "thumbnail_prompt": "2D noir graphic-novel illustration on aged off-white paper background (#E8E2D0). On the left, silhouette of a faceless detective in flat slate-grey long coat (#5A5F66) and fedora hat observing an ink-black beach shoreline (#111111). On the right, a weathered paper scrap with handwritten Persian text 'Tamám Shud' circled with a striking evidence red stamp (#C0392B). Crisp heavy ink outlines, orthographic 2D, no gradients, no gore, no 3D, >=60% negative space.",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": "Hồ Sơ Mật, Kỳ Án Lịch Sử & Bí Ẩn Khoa Học",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["ho so ky la", "somerton man", "tamam shud", "vu an somerton", "ky an the gioi"],
            "cta_plan": {
                "close": "Hồ sơ Somerton vẫn chưa khép lại. Hẹn gặp lại bạn ở kỳ án sau.",
                "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
            },
            "editorial_stance": {
                "myth_debunked": "Vụ án Somerton chỉ là một cái chết đột tử ngẫu nhiên của một người vô gia cư lang thang bên bờ biển.",
                "why_generic_advice_fails": "Cách điều tra thông thường bế tắc vì toàn bộ nhãn mác quần áo và đồ dùng cá nhân đều bị cắt sạch dấu vết.",
                "channel_verdict": "Sự tỉ mỉ đến phi lý trong việc xóa sạch danh tính cho thấy đây là một điệp vụ tình báo thời Chiến tranh Lạnh.",
                "tradeoff_or_blindspot": "Giải mã được nguồn gốc mẩu giấy Tamám Shud lại mở ra một chuỗi mật mã khác chưa ai giải được."
            },
            "actionable_value": {
                "core_mechanism": "Phương pháp điều tra hình sự lần theo vi vết sợi vải và ấn bản thơ cổ Rubaiyat để truy vết tung tích nạn nhân.",
                "practical_rule_of_thumb": "Nguyên tắc thám tử: Khi mọi dấu vết vật lý bị tẩy xóa, thứ còn sót lại duy nhất chính là bằng chứng tố giác kẻ thủ ác.",
                "real_world_scenario": "Kiểm tra kỹ các ngóc ngách bí mật của trang phục như túi giấu đường may để tìm kiếm vật chứng quan trọng."
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Bóng lưng thám tử áo măng tô xám soi kính lúp vào mẩu giấy Tamám Shud viền đỏ trên bãi biển Somerton",
            "text_overlay": "MẨU GIẤY BÍ ẨN",
            "contrast_pair": "Tử thi hoàn hảo không danh tính vs Mẩu giấy mật mã xé từ tập thơ cổ",
            "thumbnail_prompt": "2D noir graphic-novel illustration on aged off-white paper background (#E8E2D0). On the left, silhouette of a faceless detective in flat slate-grey long coat (#5A5F66) and fedora hat observing an ink-black beach shoreline (#111111). On the right, a weathered paper scrap with handwritten Persian text 'Tamám Shud' circled with a striking evidence red stamp (#C0392B). Crisp heavy ink outlines, orthographic 2D, no gradients, no gore, no 3D, >=60% negative space.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Hồ Sơ Mật, Kỳ Án Lịch Sử & Bí Ẩn Khoa Học",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["ho so ky la", "somerton man", "tamam shud", "vu an somerton", "ky an the gioi"],
        "cta_plan": {
            "close": "Hồ sơ Somerton vẫn chưa khép lại. Hẹn gặp lại bạn ở kỳ án sau.",
            "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "bridge_templates": list(ch.engagement.bridge_templates),
            "close_templates": list(ch.engagement.close_templates),
            "endcard_text": ch.engagement.endcard_text,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": {
            "myth_debunked": "Vụ án Somerton chỉ là một cái chết đột tử ngẫu nhiên của một người vô gia cư lang thang bên bờ biển.",
            "why_generic_advice_fails": "Cách điều tra thông thường bế tắc vì toàn bộ nhãn mác quần áo và đồ dùng cá nhân đều bị cắt sạch dấu vết.",
            "channel_verdict": "Sự tỉ mỉ đến phi lý trong việc xóa sạch danh tính cho thấy đây là một điệp vụ tình báo thời Chiến tranh Lạnh.",
            "tradeoff_or_blindspot": "Giải mã được nguồn gốc mẩu giấy Tamám Shud lại mở ra một chuỗi mật mã khác chưa ai giải được."
        },
        "actionable_value": {
            "core_mechanism": "Phương pháp điều tra hình sự lần theo vi vết sợi vải và ấn bản thơ cổ Rubaiyat để truy vết tung tích nạn nhân.",
            "practical_rule_of_thumb": "Nguyên tắc thám tử: Khi mọi dấu vết vật lý bị tẩy xóa, thứ còn sót lại duy nhất chính là bằng chứng tố giác kẻ thủ ác.",
            "real_world_scenario": "Kiểm tra kỹ các ngóc ngách bí mật của trang phục như túi giấu đường may để tìm kiếm vật chứng quan trọng."
        },
        "video_engine": "flow_video"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Mở màn vụ án bên bờ biển Somerton rạng sáng ngày một tháng mười hai năm 1948", "requirements": ["R01"], "transition": "Dẫn vào hiện trường khám nghiệm"},
            {"scene_id": "SC02", "purpose": "Khám nghiệm hiện trường và phát hiện nhãn mác bị cắt sạch sẽ", "requirements": ["R02"], "transition": "Truy tìm đồ đạc cá nhân tại nhà ga"},
            {"scene_id": "SC03", "purpose": "Khám xét chiếc vali bí ẩn bỏ quên tại ga xe lửa Adelaide", "requirements": ["R03"], "transition": "Chuyển sang bình luận điều tra"},
            {"scene_id": "SC04", "purpose": "Bình luận sắc bén về dấu vết điệp vụ tình báo thời Chiến tranh Lạnh", "requirements": ["R04"], "transition": "Phát hiện bước ngoặt trong túi quần"},
            {"scene_id": "SC05", "purpose": "Phát hiện mẩu giấy kỳ lạ mang hai chữ Tamám Shud", "requirements": ["R05"], "transition": "Lần tìm nguồn gốc tập thơ cổ"},
            {"scene_id": "SC06", "purpose": "Hành trình tìm kiếm cuốn sách thơ Rubaiyat của Omar Khayyam", "requirements": ["R06"], "transition": "Lật mở bí mật ở bìa sau cuốn sách"},
            {"scene_id": "SC07", "purpose": "Giải mã năm dòng mật mã chữ cái viết tay bí ẩn", "requirements": ["R07"], "transition": "Bình luận về nhân chứng then chốt"},
            {"scene_id": "SC08", "purpose": "Bình luận về cuộc gặp gỡ kỳ lạ với nữ y tá Jo Thomson", "requirements": ["R08"], "transition": "Phân tích các giả thuyết điệp viên"},
            {"scene_id": "SC09", "purpose": "Đánh giá các giả thuyết tình báo đối trọng Xô Viết và phương Tây", "requirements": ["R09"], "transition": "Cập nhật tiến triển khoa học hiện đại"},
            {"scene_id": "SC10", "purpose": "Tiến trình giám định ADN hiện đại và những uẩn khúc chưa tan", "requirements": ["R10"], "transition": "Đúc kết bài học điều tra"},
            {"scene_id": "SC11", "purpose": "Tổng kết hồ sơ Somerton và trao gửi thông điệp kết thúc", "requirements": ["R11"], "transition": "Kết thúc video với endcard"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Dương FG",
                    "top_performing_videos": [
                        {
                            "title": "Bí ẩn thế kỷ: Vụ án người đàn ông Somerton và mật mã Tamam Shud",
                            "views": "2.5M views",
                            "hook_technique": "Kể chuyện điềm tĩnh, bám sát từng biên bản khám nghiệm hiện trường thực tế.",
                            "pacing_structure": "Phát hiện bờ biển -> Manh mối vali ga tàu -> Mẩu giấy Tamám Shud -> Nghi vấn nữ y tá.",
                            "retention_driver": "Tư liệu lịch sử xác thực, giọng trầm ấm lôi cuốn."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Dẫn chứng tài liệu lưu trữ của cảnh sát Nam Úc.",
                        "Trình bày khách quan đa chiều các giả thuyết mà không vội vàng kết luận."
                    ]
                },
                {
                    "channel_name": "Độc Thám TV",
                    "top_performing_videos": [
                        {
                            "title": "Hồ sơ tuyệt mật: Người đàn ông không danh tính bên bờ biển Somerton",
                            "views": "1.3M views",
                            "hook_technique": "Tập trung mổ xẻ năm dòng mật mã viết tay ở bìa sách.",
                            "pacing_structure": "Bối cảnh Chiến tranh Lạnh -> Các chi tiết cắt nhãn áo -> Phân tích mật mã.",
                            "retention_driver": "Tính chất trinh thám tình báo nghẹt thở."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Đồ họa hồ sơ noir đen trắng kết hợp điểm nhấn đỏ.",
                        "Nhịp ngắt nghỉ tạo không khí căng thẳng ly kỳ."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 19,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Tử thi mặc âu phục lịch lãm trên bờ cát đối lập với nhãn mác bị cắt sạch sẽ.",
                "counter_intuitive_truth_slap": "Đây không phải cái chết tự nhiên, mà là một điệp vụ xóa sạch danh tính có chuẩn bị công phu nhất thế kỷ hai mươi."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Khởi đầu từ bờ biển Somerton sáng ngày một tháng mười hai năm 1948."},
                {"phase": "empirical_conflict", "purpose": "Phát hiện hàng loạt manh mối bị xóa trắng: nhãn áo, vali, vé tàu."},
                {"phase": "structural_model", "purpose": "Mẩu giấy Tamám Shud kết nối với cuốn thơ cổ và năm dòng mật mã."},
                {"phase": "actionable_resolution", "purpose": "Phân tích giả thuyết tình báo và tiến bộ giám định ADN ngày nay."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "2D noir case-file documents linking each forensic discovery."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Hồ Sơ Mật, Kỳ Án Lịch Sử & Bí Ẩn Khoa Học",
            "myth_debunked": "Cái chết chỉ là một vụ tự sát ngẫu nhiên không động cơ.",
            "channel_verdict": "Sự can thiệp của mật mã, sách hiếm và tẩy xóa danh tính khẳng định bản chất tình báo Chiến tranh Lạnh.",
            "actionable_rule_of_thumb": "Xem xét cẩn trọng từng chi tiết nhỏ nhất trong bối cảnh lịch sử rộng lớn."
        },
        "cta_and_spinoff_strategy": {
            "close": "Hồ sơ Somerton vẫn chưa khép lại. Hẹn gặp lại bạn ở kỳ án sau.",
            "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
        }
    }

    # 11 scenes with calibrated word counts (~66 words each, total 732 words)
    scenes_data = [
        # SC01 (~66 words)
        {
            "id": "SC01",
            "title": "Bờ biển Somerton rạng sáng ngày một tháng mười hai",
            "purpose": "Thiết lập bối cảnh mở đầu vụ án người đàn ông vô danh bên bờ biển Somerton",
            "sit": "hook_cold_open",
            "phase": "lived_friction",
            "narration": "Sáng sớm ngày một tháng mười hai năm 1948, người ta phát hiện thi thể một người đàn ông trung niên nằm tựa lưng vào bờ kè đá Somerton. Nạn nhân mặc áo sơ mi trắng, thắt cà vạt và khoác chiếc áo len màu nâu chỉnh tề. Nhưng đôi mắt nhắm nghiền mãi mãi không bao giờ mở lại. Không ai biết ông đến từ đâu.",
            "req": "R01",
            "quotes": [
                ("Sáng sớm ngày một tháng mười hai năm 1948,", "burst"),
                ("người ta phát hiện thi thể một người đàn ông trung niên", "fast"),
                ("nằm tựa lưng vào bờ kè đá Somerton.", "normal"),
                ("Nạn nhân mặc áo sơ mi trắng, thắt cà vạt", "fast"),
                ("và khoác chiếc áo len màu nâu chỉnh tề.", "normal"),
                ("Không ai biết ông đến từ đâu.", "slow")
            ],
            "desc_seeds": [
                ("Two horse riders silhouettes trotting along a bleak misty beach at dawn", "environment"),
                ("A man in neat gentleman attire lying motionless against a seawall on cold sand", "full_scene"),
                ("Close up of a half-smoked cigarette fallen on the lapel of the brown knit jacket", "macro_prop"),
                ("Ink black waves washing quietly over pebbles on aged off-white canvas", "environment"),
                ("Silhouette of the faceless detective kneeling beside the seawall measuring footprints", "full_scene"),
                ("Police evidence marker card number one standing in the sand circled in red", "still_life")
            ]
        },
        # SC02 (~66 words)
        {
            "id": "SC02",
            "title": "Hiện trường hoàn hảo và sự xóa sạch dấu vết",
            "purpose": "Mô tả sự biến mất kỳ lạ của toàn bộ nhãn hiệu trên cơ thể nạn nhân",
            "sit": "mechanism_step",
            "phase": "empirical_conflict",
            "narration": "Cảnh sát thành phố Adelaide lập tức phong tỏa hiện trường. Khám xét trên người nạn nhân chỉ thấy một bao diêm, một gói kẹo cao su và vé tàu chưa dùng. Tuyệt nhiên không có ví tiền hay giấy tờ tùy thân. Đáng kinh ngạc hơn, toàn bộ nhãn mác trên từng món quần áo đều bị dùng kéo cắt sạch không để lại một chữ.",
            "req": "R02",
            "quotes": [
                ("Cảnh sát thành phố Adelaide lập tức phong tỏa hiện trường.", "fast"),
                ("Khám xét trên người nạn nhân chỉ thấy một bao diêm, kẹo cao su và vé tàu chưa dùng.", "normal"),
                ("Tuyệt nhiên không có ví tiền hay giấy tờ tùy thân.", "fast"),
                ("Đáng kinh ngạc hơn, toàn bộ nhãn mác trên từng món quần áo", "normal"),
                ("đều bị dùng kéo cắt sạch", "normal"),
                ("không để lại một chữ.", "slow")
            ],
            "desc_seeds": [
                ("A forensic table holding an unspent bus ticket, matches, and chewing gum pack", "still_life"),
                ("Heavy black ink tailor scissors poised above a coat fabric tag", "macro_prop"),
                ("A row of neatly severed fabric labels with clean razor cuts and frayed threads", "cutaway_detail"),
                ("Silhouette of the detective examining the cut seams under a magnifying glass", "full_scene"),
                ("Adelaide police department official case file folder stamped with red seal", "white_card"),
                ("Fingerprint card showing clean unblemished ridges matching no database record", "visual_diagram")
            ]
        },
        # SC03 (~66 words)
        {
            "id": "SC03",
            "title": "Chiếc vali gửi ở ga xe lửa Adelaide",
            "purpose": "Lần tìm đồ đạc cá nhân bỏ quên tại phòng giữ hành lý nhà ga",
            "sit": "mechanism_step",
            "phase": "empirical_conflict",
            "narration": "Hơn một tháng sau, manh mối dẫn cảnh sát đến phòng gửi hành lý ga Adelaide. Tại đây có một chiếc vali nâu được gửi vào sáng trước hôm phát hiện tử thi. Bên trong vali chứa chiếc áo choàng tắm, dao cạo râu và cuộn chỉ may màu cam hiếm gặp. Trùng hợp thay, toàn bộ nhãn mác quần áo trong vali cũng bị cắt sạch sẽ.",
            "req": "R03",
            "quotes": [
                ("Hơn một tháng sau,", "fast"),
                ("manh mối dẫn cảnh sát đến phòng gửi hành lý ga Adelaide.", "normal"),
                ("Tại đây có một chiếc vali nâu được gửi vào sáng trước hôm phát hiện tử thi.", "normal"),
                ("Bên trong vali chứa chiếc áo choàng tắm, dao cạo râu và cuộn chỉ may màu cam.", "fast"),
                ("Trùng hợp thay, toàn bộ nhãn mác quần áo trong vali", "normal"),
                ("cũng bị cắt sạch sẽ.", "slow")
            ],
            "desc_seeds": [
                ("A vintage brown leather suitcase resting on a wooden railway parcel shelf", "still_life"),
                ("The luggage claim ticket stamped with date November 30 1948 in red ink", "macro_prop"),
                ("Inside of the suitcase displaying folded bathrobe, straight razor, and scissors", "cutaway_detail"),
                ("A small spool of distinctive Barbour brand orange waxed thread under light", "macro_prop"),
                ("Detective silhouette shining a flashlight into the interior pockets of the case", "full_scene"),
                ("Railway clock in ink black showing late morning on aged paper background", "environment")
            ]
        },
        # SC04 (~66 words, editorial_commentary)
        {
            "id": "SC04",
            "title": "Lời bình: Kỹ thuật xóa vết tích của điệp viên",
            "purpose": "Bình luận sắc bén về dấu hiệu hoạt động tình báo chuyên nghiệp",
            "sit": "editorial_commentary",
            "phase": "structural_model",
            "narration": "Người bình thường không ai tỉ mỉ ngồi cắt từng chiếc mác áo lót hay nhãn giày. Việc xóa sạch mọi vết tích vật lý này mang đậm nghiệp vụ tình báo thời Chiến tranh Lạnh. Người đàn ông đó dường như đã chuẩn bị chu đáo để nếu có ngã xuống, danh tính thực sự sẽ vĩnh viễn chìm sâu vào màn sương đen tối.",
            "req": "R04",
            "quotes": [
                ("Người bình thường không ai tỉ mỉ", "normal"),
                ("ngồi cắt từng chiếc mác áo lót hay nhãn giày.", "slow"),
                ("Việc xóa sạch mọi vết tích vật lý này", "normal"),
                ("mang đậm nghiệp vụ tình báo thời Chiến tranh Lạnh.", "slow"),
                ("Người đàn ông đó dường như đã chuẩn bị chu đáo để nếu có ngã xuống,", "normal"),
                ("danh tính thực sự sẽ vĩnh viễn chìm sâu vào màn sương đen tối.", "slow")
            ],
            "desc_seeds": [
                ("Silhouette of a shadowy operative in trench coat stepping onto a foggy train platform", "environment"),
                ("A world map showing Cold War dividing lines in heavy black ink and red pins", "visual_diagram"),
                ("A passport turning into burning ashes with smoke swirling on aged paper", "concept_metaphor"),
                ("Detective standing in front of a giant wall of unsolved missing person circulars", "full_scene"),
                ("Magnifying glass focusing on a lone unmarked button on a slate grey coat", "cutaway_detail"),
                ("Fog creeping across an empty Adelaide street lamp post in deep noir shadow", "environment")
            ]
        },
        # SC05 (~66 words)
        {
            "id": "SC05",
            "title": "Mẩu giấy cuộn chặt Tamám Shud",
            "purpose": "Khám phá bước ngoặt tìm thấy mẩu giấy xé trong túi giấu kín",
            "sit": "mechanism_step",
            "phase": "structural_model",
            "narration": "Tháng tư năm 1949, chuyên gia giải phẫu rà soát lại chiếc quần tây nạn nhân. Ông phát hiện một túi phụ siêu nhỏ may khéo léo giấu sâu trong cạp quần. Đáy túi ẩn chứa mẩu giấy cuộn chặt như đầu tăm. Khi mở ra, trên giấy in dòng chữ phông cổ Ba Tư: Tamám Shud. Hai chữ này mang nghĩa kết thúc trọn vẹn.",
            "req": "R05",
            "quotes": [
                ("Tháng tư năm 1949,", "fast"),
                ("chuyên gia giải phẫu rà soát lại chiếc quần tây nạn nhân.", "normal"),
                ("Ông phát hiện một túi phụ siêu nhỏ may khéo léo giấu sâu trong cạp quần.", "normal"),
                ("Đáy túi ẩn chứa mẩu giấy cuộn chặt như đầu tăm.", "fast"),
                ("Khi mở ra, trên giấy in dòng chữ phông cổ Ba Tư: Tamám Shud.", "normal"),
                ("Hai chữ này mang nghĩa kết thúc trọn vẹn.", "slow")
            ],
            "desc_seeds": [
                ("Pathologist hands in black rubber gloves gently probing a dark wool waistband", "cutaway_detail"),
                ("A concealed watch fob pocket exposed by peeling back heavy inner lining", "visual_diagram"),
                ("Tweezers carefully unrolling a fragile tightly twisted sliver of paper", "macro_prop"),
                ("The tiny paper scrap displaying elegant printed capitals 'TAMÁM SHUD'", "macro_prop"),
                ("An evidence red circle drawn emphatically around the Persian phrase", "white_card"),
                ("Detective silhouette observing the slip with intense focused expression", "full_scene")
            ]
        },
        # SC06 (~66 words)
        {
            "id": "SC06",
            "title": "Truy tìm ấn bản thơ cổ Rubaiyat",
            "purpose": "Hành trình xác định nguồn gốc mẩu giấy từ cuốn thơ cổ bị xé",
            "sit": "mechanism_step",
            "phase": "structural_model",
            "narration": "Cảnh sát xác định mẩu giấy được xé từ trang cuối tập thơ Rubaiyat của Omar Khayyam. Sau lời kêu gọi công khai, một người dân giao nộp cuốn sách thơ hiếm. Ông tìm thấy nó bị ném vào ghế sau chiếc xe không khóa gần bờ biển Somerton. Từng thớ giấy khớp hoàn hảo với mảnh giấy xé trong túi nạn nhân.",
            "req": "R06",
            "quotes": [
                ("Cảnh sát xác định mẩu giấy được xé từ trang cuối tập thơ Rubaiyat của Omar Khayyam.", "fast"),
                ("Sau lời kêu gọi công khai, một người dân giao nộp cuốn sách thơ hiếm.", "normal"),
                ("Ông tìm thấy nó bị ném vào ghế sau chiếc xe không khóa gần bờ biển Somerton.", "normal"),
                ("Từng thớ giấy khớp hoàn hảo", "fast"),
                ("với mảnh giấy xé", "normal"),
                ("trong túi nạn nhân.", "slow")
            ],
            "desc_seeds": [
                ("A translation dictionary page open with Persian calligraphy and English meaning", "visual_diagram"),
                ("The leatherbound book of Rubaiyat of Omar Khayyam lying on a wooden bench", "still_life"),
                ("A vintage 1940s motorcar parked on a dark coastal street at night", "environment"),
                ("Microscopic comparison of paper fibers matching the tear edge with 100 percent precision", "visual_diagram"),
                ("Detective holding the opened book side by side with the evidence slip", "full_scene"),
                ("Newspaper headline from Adelaide Advertiser appealing for information", "white_card")
            ]
        },
        # SC07 (~66 words)
        {
            "id": "SC07",
            "title": "Năm dòng mật mã viết tay ở bìa sách",
            "purpose": "Trình bày câu đố hóc búa nhất vụ án: mật mã năm dòng chữ cái",
            "sit": "mechanism_step",
            "phase": "structural_model",
            "narration": "Dưới ánh đèn cực tím, các điều tra viên phát hiện ở bìa sau cuốn sách có năm dòng chữ viết tay bằng bút chì. Các ký tự viết hoa lộn xộn không theo quy tắc ngữ pháp thông thường. Dòng thứ hai dường như đã bị gạch xóa rồi viết đè lên. Suốt bảy mươi năm qua, những chuyên gia giải mã quân sự đều chịu bó tay.",
            "req": "R07",
            "quotes": [
                ("Dưới ánh đèn cực tím,", "fast"),
                ("các điều tra viên phát hiện ở bìa sau cuốn sách có năm dòng chữ viết tay bằng bút chì.", "normal"),
                ("Các ký tự viết hoa lộn xộn không theo quy tắc ngữ pháp thông thường.", "normal"),
                ("Dòng thứ hai dường như đã bị gạch xóa rồi viết đè lên.", "fast"),
                ("Suốt bảy mươi năm qua,", "normal"),
                ("những chuyên gia giải mã quân sự đều chịu bó tay.", "slow")
            ],
            "desc_seeds": [
                ("Ultraviolet lamp casting an ethereal glow over the faded back book cover", "macro_prop"),
                ("The five lines of capital letters clearly visible with crossed out second line", "white_card"),
                ("Codebreaker chalkboard filled with frequency analysis charts and letter tallies", "visual_diagram"),
                ("Military cryptographers in headsets staring frustrated at blackboard calculations", "full_scene"),
                ("Detective silhouette leaning over the desk studying the cipher lines under magnifying glass", "full_scene"),
                ("An antique typewriter keyboard with keys frozen in dark ink shadows", "still_life")
            ]
        },
        # SC08 (~66 words, editorial_commentary)
        {
            "id": "SC08",
            "title": "Lời bình: Bí ẩn nữ y tá và bức tượng thạch cao",
            "purpose": "Bình luận về manh mối tình cảm lẩn khuất sau một vụ án gián điệp",
            "sit": "editorial_commentary",
            "phase": "structural_model",
            "narration": "Cạnh các dòng mật mã là một số điện thoại dẫn tới ngôi nhà của nữ y tá Jo Thomson gần đó. Khi cảnh sát cho bà xem bức tượng thạch cao khuôn mặt nạn nhân, bà hoảng sợ suýt ngất đi nhưng kiên quyết chối bỏ quen biết. Thái độ kinh hãi của bà cho thấy đằng sau vụ án gián điệp còn ẩn giấu một bi kịch tình cảm nghẹn ngào.",
            "req": "R08",
            "quotes": [
                ("Cạnh các dòng mật mã là một số điện thoại dẫn tới nhà nữ y tá Jo Thomson gần đó.", "normal"),
                ("Khi cảnh sát cho bà xem bức tượng thạch cao khuôn mặt nạn nhân,", "slow"),
                ("bà hoảng sợ suýt ngất đi nhưng kiên quyết chối bỏ quen biết.", "slow"),
                ("Thái độ kinh hãi của bà", "normal"),
                ("cho thấy đằng sau vụ án gián điệp", "normal"),
                ("còn ẩn giấu một bi kịch tình cảm nghẹn ngào.", "slow")
            ],
            "desc_seeds": [
                ("An antique rotary telephone with scribbled phone numbers circled in red ink", "macro_prop"),
                ("A modest coastal bungalow house in Somerton seen through silhouette trees", "environment"),
                ("Plaster death mask bust of the Somerton man resting on a dark velvet stand", "still_life"),
                ("Silhouette of a young woman covering her face in shock before the plaster bust", "full_scene"),
                ("Detective taking field notes in a pocket pad under dim room lighting", "full_scene"),
                ("A faded old photograph of a couple with faces obscured by lens glare", "concept_metaphor")
            ]
        },
        # SC09 (~66 words)
        {
            "id": "SC09",
            "title": "Những giả thuyết tình báo đối trọng",
            "purpose": "Phân tích các giả thuyết điệp viên Xô Viết, tình báo Anh và vũ khí sinh học",
            "sit": "actionable_resolution",
            "phase": "actionable_resolution",
            "narration": "Khu vực Woomera gần Adelaide thời đó là bãi thử nghiệm quân sự tối mật. Nhiều nhà phân tích tin rằng nạn nhân là một điệp viên ngầm bị thủ tiêu bằng độc chất tự hủy không để lại vết tích. Sự đối đầu giữa các cường quốc tình báo thời bấy giờ đã biến cái chết này thành một nước cờ bí ẩn được dọn dẹp không tì vết.",
            "req": "R09",
            "quotes": [
                ("Khu vực Woomera gần Adelaide thời đó là bãi thử nghiệm quân sự tối mật.", "fast"),
                ("Nhiều nhà phân tích tin rằng nạn nhân là một điệp viên ngầm", "normal"),
                ("bị thủ tiêu bằng độc chất tự hủy không để lại vết tích.", "fast"),
                ("Sự đối đầu giữa các cường quốc tình báo thời bấy giờ", "normal"),
                ("đã biến cái chết này thành một nước cờ bí ẩn", "normal"),
                ("được dọn dẹp không tì vết.", "slow")
            ],
            "desc_seeds": [
                ("Woomera desert rocket testing facility silhouette against a stark night sky", "environment"),
                ("A small apothecary poison bottle with glass stopper glowing under soft light", "macro_prop"),
                ("Chess board with a fallen slate-grey king piece knocked aside by dark pawns", "concept_metaphor"),
                ("Two shadowy figures exchanging envelopes in a dimly lit alleyway", "full_scene"),
                ("Government confidential dossier with red declassified stamp dated decades later", "white_card"),
                ("Detective silhouette walking through empty mist-covered government corridors", "environment")
            ]
        },
        # SC10 (~66 words)
        {
            "id": "SC10",
            "title": "Ánh sáng ADN và những câu hỏi thế kỷ",
            "purpose": "Cập nhật kết quả khai quật giám định ADN hiện đại và những ẩn số còn lại",
            "sit": "mechanism_step",
            "phase": "actionable_resolution",
            "narration": "Năm 2021, chính quyền tiến hành khai quật mộ phần nạn nhân để xét nghiệm ADN di truyền. Giới khoa học xác định ông có tên Carl Webb, một thợ điện Melbourne. Tuy nhiên, vì sao người đàn ông này lại có mặt tại Somerton, ai đã cắt sạch nhãn áo của ông, và dòng mật mã viết tay mang ý nghĩa gì, vẫn là bí ẩn chưa có lời giải.",
            "req": "R10",
            "quotes": [
                ("Năm 2021, chính quyền tiến hành khai quật mộ phần nạn nhân để xét nghiệm ADN di truyền.", "fast"),
                ("Giới khoa học xác định ông có tên Carl Webb, một thợ điện Melbourne.", "normal"),
                ("Tuy nhiên, vì sao người đàn ông này lại có mặt tại Somerton,", "fast"),
                ("ai đã cắt sạch nhãn áo của ông,", "normal"),
                ("và dòng mật mã viết tay mang ý nghĩa gì,", "normal"),
                ("vẫn là bí ẩn chưa có lời giải.", "slow")
            ],
            "desc_seeds": [
                ("Modern forensic DNA laboratory with digital double helix projections in soft grey", "visual_diagram"),
                ("A simple weathered cemetery headstone reading 'The Unknown Man' on dry grass", "still_life"),
                ("An official genealogical family tree diagram leading to the name Carl Webb", "visual_diagram"),
                ("Black-and-white archived photograph of Carl Webb in youth with sharp jawline", "white_card"),
                ("Detective silhouette standing solemnly before the restored Somerton beach shore", "full_scene"),
                ("Question marks drifting like autumn leaves over an open forensic ledger", "concept_metaphor")
            ]
        },
        # SC11 (~66 words)
        {
            "id": "SC11",
            "title": "Hồ sơ khép lại và lời kết",
            "purpose": "Đúc kết vụ án thế kỷ và trao gửi lời chào kết của kênh",
            "sit": "cta_close",
            "phase": "actionable_resolution",
            "narration": "Bảy thập kỷ trôi qua, mẩu giấy Tamám Shud vẫn là biểu tượng cho kỳ án trinh thám ám ảnh nhất thế giới. Dấu vết thời gian có thể xóa nhòa nhiều sự thật, nhưng bí ẩn sẽ luôn tồn tại. Hồ sơ Somerton vẫn chưa khép lại. Hẹn gặp lại bạn ở kỳ án sau. Cùng theo dõi để lật mở tập tài liệu tiếp theo.",
            "req": "R11",
            "quotes": [
                ("Bảy thập kỷ trôi qua,", "fast"),
                ("mẩu giấy Tamám Shud vẫn là biểu tượng cho kỳ án trinh thám ám ảnh nhất thế giới.", "normal"),
                ("Dấu vết thời gian có thể xóa nhòa nhiều sự thật,", "normal"),
                ("nhưng bí ẩn sẽ luôn tồn tại.", "normal"),
                ("Hồ sơ Somerton vẫn chưa khép lại. Hẹn gặp lại bạn ở kỳ án sau.", "normal"),
                ("Cùng theo dõi để lật mở tập tài liệu tiếp theo.", "hold")
            ],
            "desc_seeds": [
                ("A heavy iron archive safe locking securely with a resonant metallic thud", "concept_metaphor"),
                ("The tiny scrap of Tamám Shud resting preserved inside a museum glass vitrine", "still_life"),
                ("A solitary detective looking out into the twilight horizon over Adelaide coast", "full_scene"),
                ("The famous five lines of cipher fading peacefully into aged off-white canvas", "white_card"),
                ("A stamped dossier marked 'CASE 1948 - SOMERTON' placed onto a high wooden shelf", "macro_prop"),
                ("Official Hồ Sơ Kỳ Lạ channel endcard with detective silhouette in long coat beside red seal reading 'BẢN ĐẦY ĐỦ TRÊN YOUTUBE'", "white_card")
            ]
        }
    ]

    scenes = []
    coverage = []

    for sc_idx, sc_def in enumerate(scenes_data):
        sc_id = sc_def["id"]
        req_id = sc_def["req"]
        quotes = sc_def["quotes"]
        seeds = sc_def["desc_seeds"]

        images = []
        beats = []

        for b_idx in range(6):
            img_id = f"{sc_id}_I{b_idx+1}"
            beat_id = f"{sc_id}_B{b_idx+1}"
            quote_text, tempo = quotes[b_idx]
            desc_seed, shot_type = seeds[b_idx]
            is_last_beat = (sc_id == "SC11" and b_idx == 5)

            img_desc = f"2D noir graphic-novel illustration: {desc_seed}, drawn with heavy black ink shapes and crisp linework with high-contrast flat shadows #111111, limited palette of ink black (#111111), aged off-white paper (#E8E2D0), slate grey (#5A5F66) and single accent of evidence red (#C0392B), orthographic 2D, >=60% negative space, no blood, no gore, no gradients, no 3D."

            motion_prompt = (
                "Smooth 2D noir animation, gentle breathing idle hold, silent visual storytelling, no talking, no lip movement"
                if is_last_beat
                else f"Smooth 2D noir animation. Atmospheric high-contrast linework shifts subtly with moody detective lighting, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
            )

            img_obj = {
                "id": img_id,
                "description": img_desc,
                "character_ids": ["CH01"] if "detective" in desc_seed.lower() or "thám tử" in desc_seed.lower() else [],
                "based_on": None,
                "preserve": "Aged off-white paper #E8E2D0, heavy ink linework #111111, slate grey #5A5F66, evidence red accent #C0392B.",
                "change": desc_seed,
                "reason": f"Narration-locked full-frame beat {img_id}.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": shot_type,
                "tempo": tempo,
                "narrative_situation": sc_def["sit"],
                "has_character": ("detective" in desc_seed.lower() or "thám tử" in desc_seed.lower()),
                "motion_prompt": motion_prompt
            }
            if is_last_beat:
                img_obj["is_endcard"] = True

            beat_obj = {
                "id": beat_id,
                "image_id": img_id,
                "purpose": f"Triển khai nhịp {b_idx+1} cảnh {sc_id}",
                "anchor": {"vi": {"quote": quote_text, "occurrence": 1}},
                "effect": "hold" if is_last_beat else ("cut" if b_idx % 2 == 0 else "fade"),
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": "hold" if is_last_beat else tempo,
                "narrative_situation": sc_def["sit"]
            }
            if is_last_beat:
                beat_obj["is_endcard"] = True

            images.append(img_obj)
            beats.append(beat_obj)

        scene_obj = {
            "id": sc_id,
            "title": sc_def["title"],
            "purpose": sc_def["purpose"],
            "action": "Thám tử tái hiện và giám định các vật chứng tài liệu của vụ án Somerton",
            "setting": "Không gian tài liệu noir tương phản cao trên nền giấy ngả vàng",
            "camera": "Góc quay cận cảnh tài liệu hiện trường và trung cảnh thám tử",
            "narration": sc_def["narration"],
            "requirements": [req_id],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Trầm tĩnh, hồi hộp, trinh thám",
            "narrative_phase": sc_def["phase"],
            "narrative_situation": sc_def["sit"],
            "images": images,
            "beats": beats
        }
        scenes.append(scene_obj)
        coverage.append({"requirement_id": req_id, "scene_id": sc_id, "quote": quotes[0][0]})

    claims = [
        {
            "scene_id": "SC01",
            "quote": "Sáng sớm ngày một tháng mười hai năm 1948,",
            "language": "vi",
            "source_id": "SRC01",
            "fact": "Người đàn ông vô danh được phát hiện trên bãi biển Somerton ngày một tháng mười hai năm 1948."
        },
        {
            "scene_id": "SC02",
            "quote": "đều bị dùng kéo cắt sạch",
            "language": "vi",
            "source_id": "SRC01",
            "fact": "Toàn bộ nhãn mác trên trang phục nạn nhân đều bị cắt sạch không để lại tung tích."
        },
        {
            "scene_id": "SC05",
            "quote": "Khi mở ra, trên giấy in dòng chữ phông cổ Ba Tư: Tamám Shud.",
            "language": "vi",
            "source_id": "SRC01",
            "fact": "Mẩu giấy xé mang chữ Tamám Shud được giấu kín trong túi phụ quần tây."
        },
        {
            "scene_id": "SC07",
            "quote": "Dưới ánh đèn cực tím,",
            "language": "vi",
            "source_id": "SRC01",
            "fact": "Bìa sau cuốn sách thơ Rubaiyat chứa mật mã chữ cái viết tay chưa có lời giải."
        }
    ]

    content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": compute_brief_hash(brief),
        "topic": topic,
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": [channel_cast(channel_id, "CH01")],
        "scenes": scenes,
        "coverage": coverage,
        "outline": outline["outline"],
        "claims": claims,
        "revision_response": [],
        "open_questions": []
    }

    return job_id, brief, outline, competitor_research, content
