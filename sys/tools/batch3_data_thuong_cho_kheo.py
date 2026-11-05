#!/usr/bin/env python3
"""Batch 3 Data Generator for Thương Cho Khéo (thuong_cho_kheo).

Provides:
- make_tck_short(): Generates Schema 3.0 short_9x16 spin-off package (5 scenes, 20 beats, 20 images)
- make_tck_long(): Generates Schema 3.0 long_16x9 parent package (11 scenes, 66 beats, 66 images, ~725 words)
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
# 1. THƯƠNG CHO KHÉO - SHORT 9:16
# ==============================================================================

def make_tck_short() -> Tuple[str, Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    job_id = "thuong-cho-kheo-batch3-9x16"
    parent_long_id = "thuong-cho-kheo-batch3-16x9"
    channel_id = "thuong_cho_kheo"
    ch = get_channel(channel_id)
    topic = "Đừng Nói Câu Này Khi Đang Giận Nếu Không Muốn Chia Tay"
    youtube_title = "Đừng Nói Câu Này Khi Đang Giận Nếu Không Muốn Chia Tay"

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Bóc trần tác hại hủy hoại của câu nói bất cần khi giận dữ và hướng dẫn khoảng lặng có hẹn trước để hóa giải cãi vã",
        "video_type": "relationship_communication",
        "duration": {
            "min_seconds": 40.0,
            "max_seconds": 55.0
        },
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Cú sốc lời nói buông xuôi trong cơn nóng giận"},
            {"id": "R02", "text": "Cơ chế tâm lý phía sau nỗi sợ bị chối từ"},
            {"id": "R03", "text": "Bình luận sắc bén về cái bẫy bất cần"},
            {"id": "R04", "text": "Giải pháp khoảng lặng có hẹn trước trong năm phút"},
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
                "title": "The Seven Principles for Making Marriage Work",
                "reference": "Gottman, J. M., & Silver, N. (2015). Harmony Books.",
                "facts": [
                    "Bốn phản xạ nguy hại làm tổn thương mối quan hệ: Chỉ trích, Phòng thủ, Khinh miệt và Chiến tranh lạnh.",
                    "Lời nói phủ nhận cảm xúc kích hoạt phản xạ tự vệ sinh học trong não bộ."
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
                "Giúp người xem nhận diện câu nói sát thương khi cãi vã và áp dụng nguyên tắc khoảng lặng năm phút có hẹn trước"
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Không đòi hỏi kiến thức tâm lý chuyên sâu.",
            "pacing": "Tâm sự nhẹ nhàng nhưng dứt khoát, triệt tiêu dead-air.",
            "domain_requirements": [],
            "assumptions": [
                "Mỗi phân cảnh được cân chỉnh nhịp hình ảnh từ 1.8 đến 2.3 giây một nhịp."
            ],
            "text_style": {
                "font": "sans-serif rõ nét, cùng kiểu và độ đậm xuyên suốt",
                "color": "#5B4636",
                "outline": "nền sáng tương phản",
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
                "visual_hook": "Tũn và Mây đứng đối diện nhau với biểu cảm tổn thương bên bóng thoại nứt vỡ",
                "text_overlay": "ĐỪNG NÓI CÂU NÀY",
                "contrast_pair": "Câu nói buông xuôi cay đắng vs Khoảng lặng thấu cảm năm phút",
                "thumbnail_prompt": "Soft 2D pastel line-art illustration on flat solid cream canvas (#FFF8F0). Tũn in flat mint (#BDE0C6) hoodie looking startled with hand over mouth, Mây in blush (#F7C6C7) cardigan turning away with teardrop dot eyes. Between them, a jagged broken speech bubble outlined in thin warm-brown (#5B4636). Large bold hand-lettered text in upper third: 'ĐỪNG NÓI CÂU NÀY'. Simple chibi proportions, orthographic 2D, >=60% negative space, no gradients, no 3D.",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": "Giao Tiếp Thấu Cảm & Trí Tuệ Cảm Xúc",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["thuong cho kheo", "cai nhau", "tam ly tinh yeu", "giao tiep", "shorts"],
            "cta_plan": {
                "cliffhanger_peak": "Làm thế nào để hóa giải thói quen buông lời cay đắng khi sự kiên nhẫn đã chạm đáy?",
                "bridge": "Xem trọn bộ giải mã tâm lý và cách nói khéo trên YouTube nhé.",
                "close": "Lưu video lại để áp dụng khi đối thoại cùng người ấy bạn nhé.",
                "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
            },
            "editorial_stance": {
                "myth_debunked": "Nói hết suy nghĩ thật trong lúc giận dữ là thẳng thắn giúp giải tỏa mâu thuẫn đôi lứa.",
                "why_generic_advice_fails": "Lời khuyên nhịn đi khiến cảm xúc dồn nén đến khi nổ tung bằng một câu nói cắt đứt tình cảm.",
                "channel_verdict": "Một lời thốt ra trong cơn giận có thể hủy hoại niềm tin được vun đắp suốt nhiều năm tháng.",
                "tradeoff_or_blindspot": "Im lặng mười giây để điều hòa nhịp thở khó hơn cãi tay đôi nhưng bảo vệ được người mình thương."
            },
            "actionable_value": {
                "core_mechanism": "Cơn giận đẩy não vào trạng thái tự vệ cực đoan khiến lời nói biến thành vũ khí sát thương trực diện.",
                "practical_rule_of_thumb": "Tuyệt đối không dùng câu buông xuôi em muốn nghĩ sao thì nghĩ khi cãi vã.",
                "real_world_scenario": "Khi người yêu trách móc hãy xin năm phút bình tâm thay vì nói lời bất cần."
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Tũn và Mây đứng đối diện nhau với biểu cảm tổn thương bên bóng thoại nứt vỡ",
            "text_overlay": "ĐỪNG NÓI CÂU NÀY",
            "contrast_pair": "Câu nói buông xuôi cay đắng vs Khoảng lặng thấu cảm năm phút",
            "thumbnail_prompt": "Soft 2D pastel line-art illustration on flat solid cream canvas (#FFF8F0). Tũn in flat mint (#BDE0C6) hoodie looking startled with hand over mouth, Mây in blush (#F7C6C7) cardigan turning away with teardrop dot eyes. Between them, a jagged broken speech bubble outlined in thin warm-brown (#5B4636). Large bold hand-lettered text in upper third: 'ĐỪNG NÓI CÂU NÀY'. Simple chibi proportions, orthographic 2D, >=60% negative space, no gradients, no 3D.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Giao Tiếp Thấu Cảm & Trí Tuệ Cảm Xúc",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["thuong cho kheo", "cai nhau", "tam ly tinh yeu", "giao tiep", "shorts"],
        "parent_long_id": parent_long_id,
        "cta_plan": {
            "cliffhanger_peak": "Làm thế nào để hóa giải thói quen buông lời cay đắng khi sự kiên nhẫn đã chạm đáy?",
            "bridge": "Xem trọn bộ giải mã tâm lý và cách nói khéo trên YouTube nhé.",
            "close": "Lưu video lại để áp dụng khi đối thoại cùng người ấy bạn nhé.",
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
            "myth_debunked": "Nói hết suy nghĩ thật trong lúc giận dữ là thẳng thắn giúp giải tỏa mâu thuẫn đôi lứa.",
            "why_generic_advice_fails": "Lời khuyên nhịn đi khiến cảm xúc dồn nén đến khi nổ tung bằng một câu nói cắt đứt tình cảm.",
            "channel_verdict": "Một lời thốt ra trong cơn giận có thể hủy hoại niềm tin được vun đắp suốt nhiều năm tháng.",
            "tradeoff_or_blindspot": "Im lặng mười giây để điều hòa nhịp thở khó hơn cãi tay đôi nhưng bảo vệ được người mình thương."
        },
        "actionable_value": {
            "core_mechanism": "Cơn giận đẩy não vào trạng thái tự vệ cực đoan khiến lời nói biến thành vũ khí sát thương trực diện.",
            "practical_rule_of_thumb": "Tuyệt đối không dùng câu buông xuôi em muốn nghĩ sao thì nghĩ khi cãi vã.",
            "real_world_scenario": "Khi người yêu trách móc hãy xin năm phút bình tâm thay vì nói lời bất cần."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Mở đầu kịch tính với câu nói buông xuôi nguy hiểm nhất khi cãi vã", "requirements": ["R01"], "transition": "Chuyển tiếp tự nhiên sang cơ chế tâm lý"},
            {"scene_id": "SC02", "purpose": "Bóc tách phản ứng sinh học của bộ não khi bị từ chối đối thoại", "requirements": ["R02"], "transition": "Chuyển tiếp sang góc nhìn bình luận"},
            {"scene_id": "SC03", "purpose": "Bình luận sắc sảo về hậu quả tích tụ của thái độ bất cần", "requirements": ["R03"], "transition": "Chuyển tiếp sang giải pháp thực tế"},
            {"scene_id": "SC04", "purpose": "Hướng dẫn nguyên tắc khoảng lặng năm phút có hẹn trước", "requirements": ["R04"], "transition": "Chuyển tiếp sang cao trào bỏ lửng"},
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
                    "channel_name": "Giác Minh Luật",
                    "top_performing_videos": [
                        {
                            "title": "Khi người ta im lặng là lúc tình cảm đang cạn dần",
                            "views": "1.5M views",
                            "hook_technique": "Đặt câu hỏi trúng nỗi đau người trẻ khi đối diện sự im lặng.",
                            "pacing_structure": "Tình huống đời thường -> Phân tích nỗi sợ -> Lời khuyên ấm áp.",
                            "retention_driver": "Ngôn ngữ gần gũi, chạm đúng tâm trạng người đang tổn thương."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Dùng ẩn dụ đời thường ví lời nói bất cần như nhát dao vô hình.",
                        "Nhịp kể chậm rãi, chân thành tạo cảm giác đồng cảm sâu sắc."
                    ]
                },
                {
                    "channel_name": "Hồng Trân (Naiverosie)",
                    "top_performing_videos": [
                        {
                            "title": "3 câu nói hủy hoại mối quan hệ nhanh hơn bạn nghĩ",
                            "views": "980k views",
                            "hook_technique": "Chỉ thẳng câu nói quen thuộc ai cũng từng lỡ miệng.",
                            "pacing_structure": "Trích dẫn câu nói sai -> Phân tích tâm lý đối phương -> Câu nói thay thế.",
                            "retention_driver": "Cách sửa câu chữ thực tế áp dụng được ngay."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "So sánh hai phản ứng đối lập cùng một tình huống.",
                        "Tập trung vào cách giao tiếp phi bạo lực."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Tũn buông xuôi lạnh nhạt đối lập với Mây ấm ức rơi nước mắt.",
                "counter_intuitive_truth_slap": "Đối phương không giận vì bạn sai, mà họ hoảng loạn vì bạn tỏ ra không còn cần họ."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Mở đầu với câu nói sát thương kinh điển lúc nóng giận."},
                {"phase": "empirical_conflict", "purpose": "Chỉ ra cảm giác bị bỏ rơi kích hoạt cơn thịnh nộ."},
                {"phase": "structural_model", "purpose": "Bình luận về bức tường vô hình ngăn cách hai người."},
                {"phase": "actionable_resolution", "purpose": "Khoảng lặng năm phút có hẹn trước cứu vãn cuộc đối thoại."},
                {"phase": "cliffhanger_spinoff", "purpose": "Tạo vòng lặp mở về cách xử lý khi bị công kích và dẫn phễu."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Daisy-chain linking pastel frames between Tũn and Mây."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Giao Tiếp Thấu Cảm & Trí Tuệ Cảm Xúc",
            "myth_debunked": "Cứ nói hết cho bõ tức rồi tính sau.",
            "channel_verdict": "Một lời buông xuôi lúc nóng giận có thể phá tan niềm tin xây dựng nhiều năm.",
            "actionable_rule_of_thumb": "Xin năm phút bình tâm thay vì thốt ra lời bất cần."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "Làm thế nào để hóa giải thói quen buông lời cay đắng khi sự kiên nhẫn đã chạm đáy?",
            "bridge": "Xem trọn bộ giải mã tâm lý và cách nói khéo trên YouTube nhé.",
            "close": "Lưu video lại để áp dụng khi đối thoại cùng người ấy bạn nhé.",
            "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
        }
    }

    # 5 scenes, 20 beats, 20 unique images, 164 words
    scenes = [
        {
            "id": "SC01",
            "title": "Cú sốc câu nói buông xuôi",
            "purpose": "Cảnh báo nguy cơ tan vỡ từ câu nói bất cần khi cãi vã",
            "action": "Tũn và Mây đứng đối diện nhau trong không khí căng thẳng",
            "setting": "Phòng khách tối giản ấm áp trên nền giấy kem",
            "camera": "Góc quay thẳng trung cảnh ghi lại biểu cảm hai nhân vật",
            "narration": "Cãi nhau to đến mấy cũng đừng bao giờ nói em muốn nghĩ sao thì nghĩ. Câu nói này như gáo nước lạnh dập tắt mọi cơ hội đối thoại.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Cảnh báo, nghiêm túc",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "images": [
                {
                    "id": "SC01_I1",
                    "description": "Soft 2D pastel line-art illustration of Tũn and Mây facing each other with tense upset expressions on a solid cream canvas #FFF8F0. Tũn wears a flat mint #BDE0C6 hoodie and Mây wears a flat blush #F7C6C7 cardigan with smooth warm-brown outlines #5B4636, simple chibi proportions.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Soft 2D pastel style, solid cream canvas #FFF8F0, warm-brown outlines #5B4636, Tũn and Mây chibi duo.",
                    "change": "Initial tense confrontational stance between Tũn and Mây.",
                    "reason": "Establishing opening friction beat SC01_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "narrative_situation": "hook_shock",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D pastel animation. Tũn turns slightly sideways looking frustrated as small tension sparkles flicker in the air, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I2",
                    "description": "Soft 2D pastel line-art illustration. Tũn throws both hands up in an uncaring dismissive shrug while Mây stands frozen in shock with wide dot eyes on flat cream canvas #FFF8F0, smooth thin outlines #5B4636.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Pastel palette, cream canvas, Tũn in mint hoodie and Mây in blush cardigan.",
                    "change": "Tũn displays dismissive body language.",
                    "reason": "Visualizing the uncaring gesture SC01_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "variation",
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D pastel animation. Tũn lowers his hands in apathy as Mây clutches her cardigan tightly, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I3",
                    "description": "Soft 2D pastel line-art illustration. A cold splash of icy lavender #CDB4DB water suddenly materializes between Tũn and Mây, dousing the warm atmosphere on flat cream canvas #FFF8F0.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Cream background, chibi characters, soft warm-brown linework.",
                    "change": "Metaphorical icy splash separating the duo.",
                    "reason": "Depicting the cold shutdown metaphor SC01_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D pastel animation. The icy lavender wave splashes gently across the middle space, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I4",
                    "description": "Soft 2D pastel line-art illustration. A heavy pastel stone wall drops smoothly down between Tũn and Mây, severing visual contact on flat cream canvas #FFF8F0, warm-brown outlines #5B4636.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Pastel palette, cream canvas, clean linework.",
                    "change": "Dividing barrier completely blocks dialogue.",
                    "reason": "Closing the opening hook scene SC01_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "environment",
                    "tempo": "normal",
                    "narrative_situation": "hook_shock",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D pastel animation. Dust settles as the pastel barrier locks into place, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC01_B1",
                    "image_id": "SC01_I1",
                    "purpose": "Nhịp mở đầu: xung đột bùng nổ",
                    "anchor": {"vi": {"quote": "Cãi nhau to đến mấy", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "burst",
                    "narrative_situation": "hook_shock"
                },
                {
                    "id": "SC01_B2",
                    "image_id": "SC01_I2",
                    "purpose": "Nhịp cao trào: câu nói bất cần",
                    "anchor": {"vi": {"quote": "cũng đừng bao giờ nói em muốn nghĩ sao thì nghĩ.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "hook_shock"
                },
                {
                    "id": "SC01_B3",
                    "image_id": "SC01_I3",
                    "purpose": "Nhịp ẩn dụ: gáo nước lạnh",
                    "anchor": {"vi": {"quote": "Câu nói này như gáo nước lạnh", "occurrence": 1}},
                    "effect": "fade",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "hook_shock"
                },
                {
                    "id": "SC01_B4",
                    "image_id": "SC01_I4",
                    "purpose": "Nhịp kết cảnh: đóng băng cơ hội",
                    "anchor": {"vi": {"quote": "dập tắt mọi cơ hội đối thoại.", "occurrence": 1}},
                    "effect": "hold",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "hook_shock"
                }
            ]
        },
        {
            "id": "SC02",
            "title": "Bản chất nỗi sợ bị từ chối",
            "purpose": "Giải thích phản ứng hoảng loạn của tâm lý khi gặp sự buông xuôi",
            "action": "Minh họa tâm lý học và biểu cảm bất an của Mây",
            "setting": "Không gian trừu tượng với các biểu tượng cảm xúc pastel",
            "camera": "Cận cảnh chuyển dần sang trung cảnh đối chiếu",
            "narration": "Bộ não xem thái độ này là tín hiệu bị từ chối phũ phàng. Người ấy không tức giận vì bạn sai, mà họ hoảng sợ vì bạn không còn quan tâm.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Phân tích, thấu cảm",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "before_after_contrast",
            "images": [
                {
                    "id": "SC02_I1",
                    "description": "Soft 2D pastel line-art illustration. A cute brain diagram in blush pink #F7C6C7 with a glowing red-orange alarm bell ringing softly on flat solid cream canvas #FFF8F0, warm-brown outlines #5B4636.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Cream background, pastel tones, warm-brown linework.",
                    "change": "Scientific brain icon sensing danger signals.",
                    "reason": "Illustrating emotional rejection alarm SC02_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "visual_diagram",
                    "tempo": "fast",
                    "narrative_situation": "before_after_contrast",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D pastel animation. The cute brain icon pulses with gentle soundwave ripples, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I2",
                    "description": "Soft 2D pastel line-art illustration. Mây clutches her chest with trembling dot eyes on cream canvas #FFF8F0 as a small pastel heart puzzle piece next to her hairline shows a delicate crack.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Mây in blush cardigan, cream background, warm-brown line art.",
                    "change": "Mây showing genuine vulnerable emotional pain.",
                    "reason": "Portraying inner distress SC02_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "before_after_contrast",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D pastel animation. Mây lowers her head slightly as a tear accent glints softly on her cheek, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I3",
                    "description": "Soft 2D pastel line-art illustration. A contrast split frame: on one side a spiky angry mask, on the other side a trembling vulnerable face feeling abandoned, drawn in lavender #CDB4DB and butter #FFF1B5 on cream canvas.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Pastel aesthetic, warm-brown outlines, clean flat composition.",
                    "change": "Contrasting anger surface with underlying fear of abandonment.",
                    "reason": "Exposing the hidden motive SC02_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "narrative_situation": "before_after_contrast",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D pastel animation. The spiky angry mask slides aside to reveal the fragile inner face, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I4",
                    "description": "Soft 2D pastel line-art illustration. Tũn turns his back walking away into empty cream space as Mây reaches out a small hand, leaving a poignant distance between them, smooth warm-brown outlines #5B4636.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Tũn and Mây designs, mint and blush outfits, cream canvas.",
                    "change": "Physical manifestation of abandonment.",
                    "reason": "Conveying loneliness beat SC02_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "before_after_contrast",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D pastel animation. Tũn continues walking away as gentle dust motes drift across the gap, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC02_B1",
                    "image_id": "SC02_I1",
                    "purpose": "Nhịp tín hiệu não bộ",
                    "anchor": {"vi": {"quote": "Bộ não xem thái độ này là tín hiệu bị từ chối phũ phàng.", "occurrence": 1}},
                    "effect": "fade",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "before_after_contrast"
                },
                {
                    "id": "SC02_B2",
                    "image_id": "SC02_I2",
                    "purpose": "Nhịp cảm xúc: không phải giận vì sai",
                    "anchor": {"vi": {"quote": "Người ấy không tức giận vì bạn sai,", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "before_after_contrast"
                },
                {
                    "id": "SC02_B3",
                    "image_id": "SC02_I3",
                    "purpose": "Nhịp hé lộ nỗi hoảng sợ",
                    "anchor": {"vi": {"quote": "mà họ hoảng sợ", "occurrence": 1}},
                    "effect": "zoom_in",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "before_after_contrast"
                },
                {
                    "id": "SC02_B4",
                    "image_id": "SC02_I4",
                    "purpose": "Nhịp mất kết nối",
                    "anchor": {"vi": {"quote": "vì bạn không còn quan tâm.", "occurrence": 1}},
                    "effect": "hold",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "before_after_contrast"
                }
            ]
        },
        {
            "id": "SC03",
            "title": "Bình luận về cái bẫy bất cần",
            "purpose": "Đưa ra lời bình sâu sắc về nguy cơ rạn nứt lâu dài từ sự bất cần",
            "action": "Minh họa khoảng cách lớn dần qua chiếc bàn trà",
            "setting": "Góc phòng với chiếc bàn nhỏ và hai tách trà nguội lạnh",
            "camera": "Toàn cảnh tĩnh nhấn mạnh sự trống vắng",
            "narration": "Khi bạn buông xuôi, bạn biến một bất đồng nhỏ thành bức tường lớn. Càng tỏ ra bất cần, vết nứt niềm tin càng sâu và khó hàn gắn.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Chiêm nghiệm, cảnh tỉnh",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images": [
                {
                    "id": "SC03_I1",
                    "description": "Soft 2D pastel line-art illustration. Tũn and Mây sit at opposite ends of a long wooden bench on cream canvas #FFF8F0, between them a tiny untied knot of mint and blush ribbon.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Pastel aesthetic, cream background, warm-brown outlines.",
                    "change": "Sitting apart with initial small dispute.",
                    "reason": "Setting up editorial scene SC03_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D pastel animation. The bench stretches slightly longer as the characters sit in quiet contemplation, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I2",
                    "description": "Soft 2D pastel line-art illustration. The tiny untied ribbon frays into multiple fragile threads, expanding into a wide rift on the cream floor #FFF8F0, thin warm-brown outlines #5B4636.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Cream canvas, soft palette, delicate line art.",
                    "change": "Visual magnification of escalating emotional distance.",
                    "reason": "Showing escalation beat SC03_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D pastel animation. The delicate threads drift apart like gentle dandelion seeds, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I3",
                    "description": "Soft 2D pastel line-art illustration. Tũn folds his arms looking down while Mây gazes at the floor with folded hands on cream canvas #FFF8F0, two distinct thought clouds drifting without touching.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Tũn and Mây characters, mint and blush clothing, warm-brown outlines.",
                    "change": "Both characters trapped in their isolated thoughts.",
                    "reason": "Demonstrating uncommunicated thoughts SC03_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D pastel animation. The thought clouds swirl softly above their heads, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I4",
                    "description": "Soft 2D pastel line-art illustration. A delicate ceramic teacup resting on a saucer with a thin hairline crack filled with gold-butter hue #FFF1B5 on cream canvas #FFF8F0, warm-brown outlines #5B4636.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Cream canvas, minimal aesthetic, warm-brown linework.",
                    "change": "Kintsugi metaphor for fragile cracked trust.",
                    "reason": "Closing editorial commentary with a poignant image SC03_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "still_life",
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D pastel animation. A gentle warm glint sparkles on the golden repair line, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC03_B1",
                    "image_id": "SC03_I1",
                    "purpose": "Nhịp buông xuôi rạn nứt",
                    "anchor": {"vi": {"quote": "Khi bạn buông xuôi,", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary"
                },
                {
                    "id": "SC03_B2",
                    "image_id": "SC03_I2",
                    "purpose": "Nhịp bức tường ngăn cách",
                    "anchor": {"vi": {"quote": "bạn biến một bất đồng nhỏ thành bức tường lớn.", "occurrence": 1}},
                    "effect": "fade",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary"
                },
                {
                    "id": "SC03_B3",
                    "image_id": "SC03_I3",
                    "purpose": "Nhịp vết nứt niềm tin",
                    "anchor": {"vi": {"quote": "Càng tỏ ra bất cần,", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary"
                },
                {
                    "id": "SC03_B4",
                    "image_id": "SC03_I4",
                    "purpose": "Nhịp khó hàn gắn",
                    "anchor": {"vi": {"quote": "vết nứt niềm tin càng sâu và khó hàn gắn.", "occurrence": 1}},
                    "effect": "hold",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary"
                }
            ]
        },
        {
            "id": "SC04",
            "title": "Khoảng lặng năm phút có hẹn trước",
            "purpose": "Hướng dẫn hành động cụ thể để hạ nhiệt cơn giận mà không làm đối phương tổn thương",
            "action": "Tũn hít thở sâu và chân thành hẹn giờ nói chuyện lại",
            "setting": "Không gian dịu mát với ánh sáng pastel mint và blush hòa quyện",
            "camera": "Cận cảnh bàn tay và biểu cảm dịu lại của hai nhân vật",
            "narration": "Hãy hít sâu và nói cho anh xin năm phút bình tâm lại. Một khoảng lặng có hẹn trước sẽ dập tắt ngọn lửa giận dữ trong tích tắc.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Hướng dẫn, ấm áp, thực tế",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "mechanism_step",
            "images": [
                {
                    "id": "SC04_I1",
                    "description": "Soft 2D pastel line-art illustration. Tũn places a gentle hand on his chest taking a calm deep breath with eyes closed on cream canvas #FFF8F0, mint hoodie #BDE0C6, warm-brown outlines #5B4636.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Tũn character, mint hoodie, pastel style, cream canvas.",
                    "change": "Tũn regulating his breathing consciously.",
                    "reason": "Demonstrating deep breath step SC04_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D pastel animation. Tũn inhales and exhales gently as soft calm waves ripple around him, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I2",
                    "description": "Soft 2D pastel line-art illustration. Tũn holds up a cute miniature pastel hourglass with mint sand, looking at Mây with sincere gentle dot eyes on cream canvas #FFF8F0.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Tũn and Mây characters, pastel palette, clean warm-brown linework.",
                    "change": "Tũn proposes a 5-minute pause with hourglass prop.",
                    "reason": "Offering the calm pause gesture SC04_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "variation",
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D pastel animation. The mint sand trickles gracefully through the hourglass, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I3",
                    "description": "Soft 2D pastel line-art illustration. A soothing mint-green bubble with a soft glowing 5-minute timer surrounds both Tũn and Mây, cooling down the tension on cream canvas #FFF8F0.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Cream background, chibi characters, mint and blush palette.",
                    "change": "Protective calm bubble encapsulates both characters.",
                    "reason": "Visualizing planned pause effect SC04_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D pastel animation. The soothing bubble glows with soft pulses of mint light, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I4",
                    "description": "Soft 2D pastel line-art illustration. Tiny fiery flame sparks dissolve gently into soft soothing butter-yellow #FFF1B5 and lavender #CDB4DB sparkles on cream canvas #FFF8F0.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "Pastel aesthetic, warm-brown outlines, clean negative space.",
                    "change": "Anger extinguishing into peaceful sparkles.",
                    "reason": "Showing anger dissolving SC04_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "cutaway_detail",
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "has_character": False,
                    "motion_prompt": "Smooth 2D pastel animation. The sparkles swirl slowly and dissolve peacefully, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC04_B1",
                    "image_id": "SC04_I1",
                    "purpose": "Nhịp hít thở sâu",
                    "anchor": {"vi": {"quote": "Hãy hít sâu và nói cho anh xin năm phút bình tâm lại.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step"
                },
                {
                    "id": "SC04_B2",
                    "image_id": "SC04_I2",
                    "purpose": "Nhịp hẹn giờ chân thành",
                    "anchor": {"vi": {"quote": "Một khoảng lặng có hẹn trước", "occurrence": 1}},
                    "effect": "fade",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step"
                },
                {
                    "id": "SC04_B3",
                    "image_id": "SC04_I3",
                    "purpose": "Nhịp làm mát không khí",
                    "anchor": {"vi": {"quote": "sẽ dập tắt ngọn lửa", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step"
                },
                {
                    "id": "SC04_B4",
                    "image_id": "SC04_I4",
                    "purpose": "Nhịp tan biến cơn giận",
                    "anchor": {"vi": {"quote": "giận dữ trong tích tắc.", "occurrence": 1}},
                    "effect": "hold",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step"
                }
            ]
        },
        {
            "id": "SC05",
            "title": "Đỉnh cao trào và lời mời kết nối",
            "purpose": "Đặt ra câu hỏi cao trào mở và dẫn phễu sang video dài trên YouTube",
            "action": "Tũn và Mây làm hòa, hướng mắt ấm áp về phía người xem",
            "setting": "Góc phòng ngập tràn ánh sáng pastel dịu ngọt",
            "camera": "Trung cảnh chuyển dần sang endcard chính thức",
            "narration": "Nhưng khi đối phương liên tục công kích, bạn nên nói gì để giữ hòa khí? Xem trọn bộ giải mã tâm lý và cách nói khéo trên YouTube nhé. Lưu video lại để áp dụng khi đối thoại cùng người ấy bạn nhé.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Ấm áp, truyền cảm hứng, mời gọi",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "cliffhanger_peak",
            "images": [
                {
                    "id": "SC05_I1",
                    "description": "Soft 2D pastel line-art illustration. Mây turns with an inquisitive expression while Tũn listens attentively, surrounded by question mark accents in butter yellow #FFF1B5 on cream canvas #FFF8F0.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Tũn and Mây characters, pastel outfits, clean outlines.",
                    "change": "Posing the deeper cliffhanger question.",
                    "reason": "Setting the cliffhanger beat SC05_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "cliffhanger_peak",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D pastel animation. Mây tilts her head inquisitively as soft sparkles accent her hair clip, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I2",
                    "description": "Soft 2D pastel line-art illustration. Tũn holds up a glowing pastel shield of empathy in mint #BDE0C6 and blush #F7C6C7 that gently absorbs sharp words on cream canvas #FFF8F0.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Cream background, pastel tones, warm-brown outlines.",
                    "change": "Empathy shield deflecting personal attacks.",
                    "reason": "Teasing the full-length solution SC05_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "narrative_situation": "cliffhanger_peak",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D pastel animation. The empathy shield radiates a comforting warm glow, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I3",
                    "description": "Soft 2D pastel line-art illustration. Tũn and Mây sit beside each other smiling gently, holding warm cups of tea together in harmony on cream canvas #FFF8F0, smooth warm-brown outlines #5B4636.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Tũn and Mây duo, mint and blush clothes, warm-brown lines.",
                    "change": "Harmonious reconciliation posture inviting long-form exploration.",
                    "reason": "Delivering bridge CTA beat SC05_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "cta_bridge",
                    "has_character": True,
                    "motion_prompt": "Smooth 2D pastel animation. Tũn and Mây smile warmly and gesture toward the viewer, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I4",
                    "description": "Soft 2D pastel channel endcard on solid cream canvas #FFF8F0. Tũn and Mây stand smiling side by side waving hands with simple cute heart sparkles. Clean hand-lettered pastel banner reads 'BẢN ĐẦY ĐỦ TRÊN YOUTUBE', warm-brown outlines #5B4636.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "Cream canvas #FFF8F0, Tũn in mint and Mây in blush, warm-brown lines #5B4636.",
                    "change": "Official channel endcard illustration.",
                    "reason": "Final hold endcard SC05_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "white_card",
                    "tempo": "hold",
                    "narrative_situation": "cta_close",
                    "has_character": True,
                    "is_endcard": True,
                    "motion_prompt": "Smooth 2D pastel animation, gentle breathing idle hold, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC05_B1",
                    "image_id": "SC05_I1",
                    "purpose": "Nhịp cao trào bỏ lửng",
                    "anchor": {"vi": {"quote": "Nhưng khi đối phương liên tục công kích,", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "cliffhanger_peak"
                },
                {
                    "id": "SC05_B2",
                    "image_id": "SC05_I2",
                    "purpose": "Nhịp mở rộng vấn đề",
                    "anchor": {"vi": {"quote": "bạn nên nói gì để giữ hòa khí?", "occurrence": 1}},
                    "effect": "zoom_in",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "cliffhanger_peak"
                },
                {
                    "id": "SC05_B3",
                    "image_id": "SC05_I3",
                    "purpose": "Nhịp cầu nối video dài",
                    "anchor": {"vi": {"quote": "Xem trọn bộ giải mã tâm lý và cách nói khéo trên YouTube nhé.", "occurrence": 1}},
                    "effect": "fade",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "cta_bridge"
                },
                {
                    "id": "SC05_B4",
                    "image_id": "SC05_I4",
                    "purpose": "Nhịp kết video kêu gọi lưu lại",
                    "anchor": {"vi": {"quote": "Lưu video lại để áp dụng khi đối thoại cùng người ấy bạn nhé.", "occurrence": 1}},
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
            {"requirement_id": "R01", "scene_id": "SC01", "quote": "Cãi nhau to đến mấy cũng đừng bao giờ nói em muốn nghĩ sao thì nghĩ."},
            {"requirement_id": "R02", "scene_id": "SC02", "quote": "Bộ não xem thái độ này là tín hiệu bị từ chối phũ phàng."},
            {"requirement_id": "R03", "scene_id": "SC03", "quote": "Khi bạn buông xuôi, bạn biến một bất đồng nhỏ thành bức tường lớn."},
            {"requirement_id": "R04", "scene_id": "SC04", "quote": "Hãy hít sâu và nói cho anh xin năm phút bình tâm lại."},
            {"requirement_id": "R05", "scene_id": "SC05", "quote": "Xem trọn bộ giải mã tâm lý và cách nói khéo trên YouTube nhé."}
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC01",
                "quote": "Câu nói này như gáo nước lạnh dập tắt mọi cơ hội đối thoại.",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Bốn phản xạ nguy hại làm tổn thương mối quan hệ: Chỉ trích, Phòng thủ, Khinh miệt và Chiến tranh lạnh."
            },
            {
                "scene_id": "SC02",
                "quote": "Bộ não xem thái độ này là tín hiệu bị từ chối phũ phàng.",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Lời nói phủ nhận cảm xúc kích hoạt phản xạ tự vệ sinh học trong não bộ."
            }
        ],
        "revision_response": [],
        "open_questions": []
    }

    return job_id, brief, outline, competitor_research, content


# ==============================================================================
# 2. THƯƠNG CHO KHÉO - LONG 16:9
# ==============================================================================

def make_tck_long() -> Tuple[str, Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    job_id = "thuong-cho-kheo-batch3-16x9"
    channel_id = "thuong_cho_kheo"
    ch = get_channel(channel_id)
    topic = "Hiệu Ứng Phòng Thủ Nhận Thức: 3 Câu Nói Khiến Cãi Vã Tệ Hơn"
    youtube_title = "Hiệu Ứng Phòng Thủ: 3 Câu Nói Khiến Cãi Vã Bùng Nổ"  # 49 chars <= 55

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Phân tích cơ chế tâm lý của hiệu ứng phòng thủ nhận thức và hướng dẫn cách chuyển đổi 3 câu nói sát thương thành lời đối thoại thấu cảm",
        "video_type": "deep_dive_explainer",
        "duration": {
            "min_seconds": 180.0,
            "max_seconds": 240.0
        },
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "Nghịch lý càng ra sức giải thích càng cãi nhau to"},
            {"id": "R02", "text": "Cơ chế sinh học của hiệu ứng phòng thủ nhận thức"},
            {"id": "R03", "text": "Bẫy tâm lý khi chiếc khiên tự vệ biến thành vũ khí"},
            {"id": "R04", "text": "Bình luận sắc sảo về việc đúng sai trong tình yêu"},
            {"id": "R05", "text": "Giải mã câu nói độc hại thứ nhất: Em luôn luôn thế"},
            {"id": "R06", "text": "Giải mã câu nói độc hại thứ hai: Anh đã bảo rồi mà"},
            {"id": "R07", "text": "Giải mã câu nói độc hại thứ ba: Tùy, muốn sao cũng được"},
            {"id": "R08", "text": "Bình luận cốt lõi: Nguy cơ xói mòn lòng trắc ẩn"},
            {"id": "R09", "text": "Công thức đối thoại ba bước chuyển nguy thành an"},
            {"id": "R10", "text": "Thực hành phản hồi thấu cảm trong tình huống thực tế"},
            {"id": "R11", "text": "Tổng kết quy tắc vàng và lời nhắn gửi cuối video"}
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
                "title": "The Seven Principles for Making Marriage Work",
                "reference": "Gottman, J. M., & Silver, N. (2015). Harmony Books.",
                "facts": [
                    "Bốn phản xạ nguy hại làm tổn thương mối quan hệ: Chỉ trích, Phòng thủ, Khinh miệt và Chiến tranh lạnh.",
                    "Phản ứng phòng thủ xuất hiện khi đối phương cảm thấy bị đe dọa lòng tự trọng.",
                    "Giao tiếp bất bạo động khuyến khích mô tả hành vi thay vì phán xét nhân cách."
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
                "Giúp người xem hiểu rõ hiệu ứng phòng thủ nhận thức và làm chủ 3 bước giao tiếp thấu cảm hạ nhiệt tranh cãi"
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Không đòi hỏi nền tảng tâm lý học nâng cao.",
            "pacing": "Tâm tình sâu lắng, nhịp ngắt nghỉ tự nhiên, triệt tiêu khoảng lặng chết.",
            "domain_requirements": [],
            "assumptions": [
                "Mỗi phân cảnh trung bình 6 nhịp hình ảnh, giữ nhịp visual liên tục từ 2.4 đến 3.1 giây một ảnh."
            ],
            "text_style": {
                "font": "sans-serif rõ nét, cùng kiểu và độ đậm xuyên suốt",
                "color": "#5B4636",
                "outline": "nền sáng tương phản",
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
                "visual_hook": "Tũn và Mây quay lưng với biểu cảm đối lập cạnh ba chiếc hộp lời nói rực lửa bị gạch chéo",
                "text_overlay": "3 CÂU NÓI CẤM",
                "contrast_pair": "Phản xạ tự vệ chỉ trích vs Lắng nghe xác nhận cảm xúc",
                "thumbnail_prompt": "Soft 2D pastel line-art illustration of Tũn and Mây facing away from each other on a solid cream canvas (#FFF8F0). Tũn in flat mint hoodie (#BDE0C6) looks stressed with sweat drop, Mây in blush cardigan (#F7C6C7) looks hurt with crossed arms. Between them, three harsh speech bubbles crossed with soft brown lines (#5B4636). Large bold hand-lettered text in upper third: '3 CÂU NÓI CẤM'. Orthographic 2D, minimal palette, >=60% negative space, no gradients, no 3D.",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": "Giao Tiếp Thấu Cảm & Trí Tuệ Cảm Xúc",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["thuong cho kheo", "phong thu nhan thuc", "tam ly hoc tinh yeu", "cai nhau", "giao tiep"],
            "cta_plan": {
                "close": "Hãy lắng nghe để thấu hiểu người bạn thương mỗi ngày bạn nhé.",
                "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
            },
            "editorial_stance": {
                "myth_debunked": "Khi tranh cãi chỉ cần nói lý lẽ thuyết phục là đối phương sẽ nhận sai và bình tâm lại.",
                "why_generic_advice_fails": "Lời khuyên bình tĩnh chung chung không ngăn được phản xạ tự vệ sinh học của não bộ khi cảm thấy bị tấn công.",
                "channel_verdict": "Khi bộ não kích hoạt phòng thủ nhận thức, mọi lý lẽ đúng đắn đều bị diễn dịch thành đòn công kích cá nhân.",
                "tradeoff_or_blindspot": "Hạ cái tôi để công nhận cảm xúc đối phương tốn sức chịu đựng ban đầu nhưng cứu vãn mối quan hệ dài lâu."
            },
            "actionable_value": {
                "core_mechanism": "Kích hoạt hạch hạnh nhân gây phản ứng chiến hay biến khiến khả năng tiếp nhận logic tạm thời tê liệt.",
                "practical_rule_of_thumb": "Nguyên tắc ba giây lùi lại: Công nhận cảm xúc trước khi giải thích nguyên nhân bằng cấu trúc Tôi Cảm Thấy.",
                "real_world_scenario": "Khi người yêu bực bội vì đến muộn, thay vì bao biện lý do tắc đường hãy ôm và xin lỗi vì để họ chờ."
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Tũn và Mây quay lưng với biểu cảm đối lập cạnh ba chiếc hộp lời nói rực lửa bị gạch chéo",
            "text_overlay": "3 CÂU NÓI CẤM",
            "contrast_pair": "Phản xạ tự vệ chỉ trích vs Lắng nghe xác nhận cảm xúc",
            "thumbnail_prompt": "Soft 2D pastel line-art illustration of Tũn and Mây facing away from each other on a solid cream canvas (#FFF8F0). Tũn in flat mint hoodie (#BDE0C6) looks stressed with sweat drop, Mây in blush cardigan (#F7C6C7) looks hurt with crossed arms. Between them, three harsh speech bubbles crossed with soft brown lines (#5B4636). Large bold hand-lettered text in upper third: '3 CÂU NÓI CẤM'. Orthographic 2D, minimal palette, >=60% negative space, no gradients, no 3D.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Giao Tiếp Thấu Cảm & Trí Tuệ Cảm Xúc",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["thuong cho kheo", "phong thu nhan thuc", "tam ly hoc tinh yeu", "cai nhau", "giao tiep"],
        "cta_plan": {
            "close": "Hãy lắng nghe để thấu hiểu người bạn thương mỗi ngày bạn nhé.",
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
            "myth_debunked": "Khi tranh cãi chỉ cần nói lý lẽ thuyết phục là đối phương sẽ nhận sai và bình tâm lại.",
            "why_generic_advice_fails": "Lời khuyên bình tĩnh chung chung không ngăn được phản xạ tự vệ sinh học của não bộ khi cảm thấy bị tấn công.",
            "channel_verdict": "Khi bộ não kích hoạt phòng thủ nhận thức, mọi lý lẽ đúng đắn đều bị diễn dịch thành đòn công kích cá nhân.",
            "tradeoff_or_blindspot": "Hạ cái tôi để công nhận cảm xúc đối phương tốn sức chịu đựng ban đầu nhưng cứu vãn mối quan hệ dài lâu."
        },
        "actionable_value": {
            "core_mechanism": "Kích hoạt hạch hạnh nhân gây phản ứng chiến hay biến khiến khả năng tiếp nhận logic tạm thời tê liệt.",
            "practical_rule_of_thumb": "Nguyên tắc ba giây lùi lại: Công nhận cảm xúc trước khi giải thích nguyên nhân bằng cấu trúc Tôi Cảm Thấy.",
            "real_world_scenario": "Khi người yêu bực bội vì đến muộn, thay vì bao biện lý do tắc đường hãy ôm và xin lỗi vì để họ chờ."
        },
        "video_engine": "flow_video"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Khởi đầu câu chuyện với nghịch lý càng giải thích càng xung đột gay gắt", "requirements": ["R01"], "transition": "Dẫn dắt vào cơ chế thần kinh học"},
            {"scene_id": "SC02", "purpose": "Giải mã cơ chế sinh học của hiệu ứng phòng thủ nhận thức", "requirements": ["R02"], "transition": "Phân tích tác hại khi tấm khiên hóa thành vũ khí"},
            {"scene_id": "SC03", "purpose": "Vạch trần cái bẫy bảo vệ bản ngã biến tình yêu thành chiến trường", "requirements": ["R03"], "transition": "Đưa ra lời bình luận chuyên sâu"},
            {"scene_id": "SC04", "purpose": "Bình luận sắc sảo về sự vô nghĩa của việc thắng thua giữa hai người yêu nhau", "requirements": ["R04"], "transition": "Bắt đầu mổ xẻ câu nói sát thương thứ nhất"},
            {"scene_id": "SC05", "purpose": "Mổ xẻ câu nói nguy hại thứ nhất: Em luôn luôn thế", "requirements": ["R05"], "transition": "Chuyển tiếp sang câu nói độc hại thứ hai"},
            {"scene_id": "SC06", "purpose": "Mổ xẻ câu nói nguy hại thứ hai: Anh đã bảo rồi mà", "requirements": ["R06"], "transition": "Chuyển tiếp sang câu nói độc hại thứ ba"},
            {"scene_id": "SC07", "purpose": "Mổ xẻ câu nói nguy hại thứ ba: Tùy, muốn sao cũng được", "requirements": ["R07"], "transition": "Bình luận chuyển giao sang giải pháp"},
            {"scene_id": "SC08", "purpose": "Bình luận cốt lõi về sự xói mòn cảm xúc thấu cảm", "requirements": ["R08"], "transition": "Giới thiệu khung giải pháp chuyển hóa"},
            {"scene_id": "SC09", "purpose": "Trình bày công thức đối thoại ba bước thấu cảm", "requirements": ["R09"], "transition": "Ứng dụng vào tình huống cụ thể"},
            {"scene_id": "SC10", "purpose": "Thực hành phản hồi mẫu trong tình huống mâu thuẫn điển hình", "requirements": ["R10"], "transition": "Đúc kết thông điệp trọn vẹn"},
            {"scene_id": "SC11", "purpose": "Tổng kết quy tắc vàng và trao gửi lời kết ấm áp", "requirements": ["R11"], "transition": "Kết thúc video với endcard"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Tuệ An / Cửa Sổ Tình Yêu",
                    "top_performing_videos": [
                        {
                            "title": "Nghệ thuật giao tiếp giúp vợ chồng không bao giờ cãi vã",
                            "views": "2.1M views",
                            "hook_technique": "Phân tích tâm lý sâu sắc từ những mẩu chuyện đời sống gần gũi.",
                            "pacing_structure": "Tình huống va chạm -> Phân tích tâm lý gốc rễ -> Phương pháp hóa giải bằng thấu cảm.",
                            "retention_driver": "Giọng văn ấm áp, điềm đạm, không giáo điều."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Phân loại các phản ứng tâm lý thành mô hình dễ hiểu.",
                        "Nhấn mạnh vào việc lắng nghe không phán xét."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 19,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Hai người yêu nhau nhưng bị ngăn cách bởi chiếc khiên tự vệ sắc nhọn.",
                "counter_intuitive_truth_slap": "Càng nỗ lực chứng minh mình đúng bằng lý lẽ, bạn càng đẩy người mình thương ra xa."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Mở đầu chân thực về cảnh cãi vã bế tắc quen thuộc."},
                {"phase": "empirical_conflict", "purpose": "Bóc tách nguyên lý khoa học của hiệu ứng phòng thủ nhận thức."},
                {"phase": "structural_model", "purpose": "Mổ xẻ từng câu nói sai và tác động tâm lý tương ứng."},
                {"phase": "actionable_resolution", "purpose": "Cung cấp công thức đối thoại ba bước cụ thể dễ nhớ."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Continuous pastel flow linking Tũn and Mây interactions."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Giao Tiếp Thấu Cảm & Trí Tuệ Cảm Xúc",
            "myth_debunked": "Cứ nói lý lẽ rõ ràng là giải quyết được tranh cãi.",
            "channel_verdict": "Trong mối quan hệ, kết nối cảm xúc luôn đi trước logic phân tích.",
            "actionable_rule_of_thumb": "Lùi lại ba giây, gọi tên cảm xúc đối phương trước khi giải thích lý do."
        },
        "cta_and_spinoff_strategy": {
            "close": "Hãy lắng nghe để thấu hiểu người bạn thương mỗi ngày bạn nhé.",
            "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
        }
    }

    # 11 scenes with calibrated word counts (~65 words each, total 722 words)
    scenes_data = [
        # SC01 (~65 words)
        {
            "id": "SC01",
            "title": "Nghịch lý càng giải thích càng bùng nổ",
            "purpose": "Khởi đầu câu chuyện với nghịch lý quen thuộc trong các cuộc tranh cãi đôi lứa",
            "sit": "hook_cold_open",
            "phase": "lived_friction",
            "narration": "Có bao giờ bạn rơi vào tình huống khó xử này chưa. Bạn chỉ muốn nhẹ nhàng phân tích để người ấy hiểu đúng sự thật khách quan. Bạn mang hết bằng chứng và lý lẽ mạch lạc ra giải thích. Nhưng vừa mở lời phân bua, ngọn lửa tranh cãi lại bùng lên dữ dội hơn bao giờ hết. Càng cố nói lý, đối phương lại càng giận dữ.",
            "req": "R01",
            "quotes": [
                ("Có bao giờ bạn rơi vào tình huống khó xử này chưa.", "burst"),
                ("Bạn chỉ muốn nhẹ nhàng phân tích", "fast"),
                ("để người ấy hiểu đúng sự thật khách quan.", "normal"),
                ("Bạn mang hết bằng chứng và lý lẽ mạch lạc ra giải thích.", "normal"),
                ("Nhưng vừa mở lời phân bua,", "fast"),
                ("ngọn lửa tranh cãi lại bùng lên dữ dội hơn bao giờ hết.", "normal")
            ],
            "desc_seeds": [
                ("Tũn and Mây sitting together under warm cozy lamp light on cream canvas", "full_scene"),
                ("Tũn gesturing with open hands trying to explain logically", "variation"),
                ("A neat notebook showing structured points on a small wooden table", "macro_prop"),
                ("Mây furrowing eyebrows as the logical words feel like sharp arrows", "full_scene"),
                ("A sudden burst of fiery pastel orange sparks erupting between them", "concept_metaphor"),
                ("Both characters turning away in exhaustion under muted pastel shadows", "full_scene")
            ]
        },
        # SC02 (~66 words)
        {
            "id": "SC02",
            "title": "Bản chất hiệu ứng phòng thủ nhận thức",
            "purpose": "Giải mã cơ chế sinh học khi hạch hạnh nhân kích hoạt trạng thái tự vệ",
            "sit": "mechanism_step",
            "phase": "empirical_conflict",
            "narration": "Các nhà tâm lý học gọi hiện tượng này là hiệu ứng phòng thủ nhận thức. Khi bị đối phương chất vấn hoặc chỉ trích, bộ não con người lập tức kích hoạt hạch hạnh nhân. Trung tâm cảm xúc này xem những lời nhận xét như một mối đe dọa sinh tồn thực sự. Nó phát tín hiệu báo động khẩn cấp và đẩy cơ thể vào trạng thái chiến đấu phòng vệ.",
            "req": "R02",
            "quotes": [
                ("Các nhà tâm lý học gọi hiện tượng này", "fast"),
                ("là hiệu ứng phòng thủ nhận thức.", "normal"),
                ("Khi bị đối phương chất vấn hoặc chỉ trích,", "normal"),
                ("bộ não con người lập tức kích hoạt hạch hạnh nhân.", "fast"),
                ("Trung tâm cảm xúc này xem những lời nhận xét", "normal"),
                ("như một mối đe dọa sinh tồn thực sự.", "slow")
            ],
            "desc_seeds": [
                ("A whimsical pastel textbook opening to a soft diagram of the human mind", "concept_metaphor"),
                ("A cute glowing brain icon in blush and mint with a tiny protective helmet", "visual_diagram"),
                ("Mây raising a gentle questioning finger on flat cream canvas", "full_scene"),
                ("The amygdala region of the brain glowing with an emergency amber light", "visual_diagram"),
                ("A tiny cartoon shield springing up automatically before Tũn chest", "concept_metaphor"),
                ("Primitive stick figure facing a shadow beast in ancient cave art style", "still_life")
            ]
        },
        # SC03 (~65 words)
        {
            "id": "SC03",
            "title": "Khi tấm khiên biến thành mũi tên",
            "purpose": "Phân tích vì sao nỗ lực tự vệ lại vô tình biến thành đòn tấn công ngược lại",
            "sit": "empirical_conflict",
            "phase": "empirical_conflict",
            "narration": "Trong trạng thái căng thẳng tột độ đó, toàn bộ vùng vỏ não trước trán tiếp nhận logic tạm thời bị phong tỏa. Bản năng sinh tồn ra lệnh cho chúng ta phải dựng lên một tấm khiên kiên cố để bảo vệ bản ngã. Nhưng điều trớ trêu là, chiếc khiên tự vệ ấy lại mang đầy gai nhọn, biến từng câu phân bua thành những mũi tên phản công sắc lẹm.",
            "req": "R03",
            "quotes": [
                ("Trong trạng thái căng thẳng tột độ đó,", "fast"),
                ("toàn bộ vùng vỏ não trước trán tiếp nhận logic tạm thời bị phong tỏa.", "normal"),
                ("Bản năng sinh tồn ra lệnh cho chúng ta", "normal"),
                ("phải dựng lên một tấm khiên kiên cố để bảo vệ bản ngã.", "fast"),
                ("Nhưng điều trớ trêu là, chiếc khiên tự vệ ấy lại mang đầy gai nhọn,", "normal"),
                ("biến từng câu phân bua thành những mũi tên phản công sắc lẹm.", "slow")
            ],
            "desc_seeds": [
                ("The logical thinking gears of a pastel clockwork mechanism freezing with frost", "concept_metaphor"),
                ("Tũn standing rigid behind an oversized mint pastel tower shield", "full_scene"),
                ("A row of spiky defensive wooden barriers popping up around Tũn", "variation"),
                ("The surface of the mint shield reflecting words back as sharp flying quills", "concept_metaphor"),
                ("Mây holding her hands up to protect herself from the verbal barrage", "full_scene"),
                ("The quiet living room filling with jagged pastel brown tension lines", "environment")
            ]
        },
        # SC04 (~66 words, editorial_commentary)
        {
            "id": "SC04",
            "title": "Lời bình: Thắng lý lẽ nhưng thua tình yêu",
            "purpose": "Bình luận triết lý về sự vô nghĩa của việc phân định thắng thua",
            "sit": "editorial_commentary",
            "phase": "structural_model",
            "narration": "Nhiều người bước vào cuộc tranh luận với tâm thế của một luật sư trước vành móng ngựa. Họ muốn thu thập mọi luận cứ để ép người kia phải nhận thua. Nhưng tình yêu chưa bao giờ là phòng xử án. Chứng minh mình hoàn toàn vô tội bằng lý lẽ lạnh lùng chỉ cho thấy bạn coi trọng sự hiếu thắng cá nhân hơn cảm xúc người thương.",
            "req": "R04",
            "quotes": [
                ("Nhiều người bước vào cuộc tranh luận", "normal"),
                ("với tâm thế của một luật sư trước vành móng ngựa.", "slow"),
                ("Họ muốn thu thập mọi luận cứ để ép người kia phải nhận thua.", "normal"),
                ("Nhưng tình yêu chưa bao giờ là phòng xử án.", "slow"),
                ("Chứng minh mình hoàn toàn vô tội bằng lý lẽ lạnh lùng", "normal"),
                ("chỉ cho thấy bạn coi trọng sự hiếu thắng cá nhân hơn cảm xúc người thương.", "slow")
            ],
            "desc_seeds": [
                ("Tũn in a playful miniature judge wig holding an oversized wooden gavel", "concept_metaphor"),
                ("A grand courtroom bench made of warm pastel toy blocks on cream background", "still_life"),
                ("A heart scale tipping heavily toward an empty stone weight on the other side", "concept_metaphor"),
                ("Tũn pointing at a neat list of legalistic points while Mây turns away silently", "full_scene"),
                ("A warm glowing heart badge fading into chilly lavender frost", "cutaway_detail"),
                ("Tũn and Mây sitting back to back with a wide silent canyon between them", "full_scene")
            ]
        },
        # SC05 (~66 words)
        {
            "id": "SC05",
            "title": "Câu nói sát thương 1: Em luôn luôn thế",
            "purpose": "Mổ xẻ tác hại của từ ngữ mang tính khái quát hóa cực đoan",
            "sit": "mechanism_step",
            "phase": "structural_model",
            "narration": "Câu nói độc hại đầu tiên thường gặp là em luôn luôn như vậy. Hai chữ luôn luôn mang tính quy chụp tuyệt đối, phủ nhận toàn bộ cố gắng của người ấy trong quá khứ. Khi nghe câu này, đối phương cảm thấy mình bị đóng đinh vào một chiếc nhãn tiêu cực. Mọi cánh cửa muốn lắng nghe và sửa đổi lập tức sập lại hoàn toàn.",
            "req": "R05",
            "quotes": [
                ("Câu nói độc hại đầu tiên thường gặp", "fast"),
                ("là em luôn luôn như vậy.", "normal"),
                ("Hai chữ luôn luôn mang tính quy chụp tuyệt đối,", "normal"),
                ("phủ nhận toàn bộ cố gắng của người ấy trong quá khứ.", "normal"),
                ("Khi nghe câu này, đối phương cảm thấy mình bị đóng đinh vào một chiếc nhãn tiêu cực.", "fast"),
                ("Mọi cánh cửa muốn lắng nghe và sửa đổi lập tức sập lại hoàn toàn.", "slow")
            ],
            "desc_seeds": [
                ("A large red-crossed stamp hanging above the words 'LUÔN LUÔN' on cream canvas", "concept_metaphor"),
                ("Tũn gesturing with an accusing finger toward Mây with furrowed brow", "full_scene"),
                ("A blackboard with dozens of positive chalk stars being erased with one stroke", "concept_metaphor"),
                ("A heavy grey label sticker sticking to Mây shoulder with sad face icon", "cutaway_detail"),
                ("Mây looking at the sticky label with drooping shoulders and teary eyes", "full_scene"),
                ("A tiny plant with wilting pastel leaves losing its morning dew", "still_life")
            ]
        },
        # SC06 (~66 words)
        {
            "id": "SC06",
            "title": "Câu nói sát thương 2: Anh đã bảo rồi mà",
            "purpose": "Phân tích cảm giác bị hạ thấp và phán xét từ thái độ thượng đẳng",
            "sit": "mechanism_step",
            "phase": "structural_model",
            "narration": "Câu nói thứ hai tàn nhẫn không kém là anh đã bảo rồi mà có chịu nghe đâu. Khi đối phương đang đau khổ hay hoang mang vì mắc lỗi, câu nói này giáng xuống như một sự trừng phạt. Nó tạo ra một khoảng cách quyền lực bất bình đẳng, đẩy người bạn yêu thương vào vị thế của một đứa trẻ ngốc nghếch cần được răn dạy.",
            "req": "R06",
            "quotes": [
                ("Câu nói thứ hai tàn nhẫn không kém", "fast"),
                ("là anh đã bảo rồi mà có chịu nghe đâu.", "normal"),
                ("Khi đối phương đang đau khổ hay hoang mang vì mắc lỗi,", "normal"),
                ("câu nói này giáng xuống như một sự trừng phạt.", "fast"),
                ("Nó tạo ra một khoảng cách quyền lực bất bình đẳng,", "normal"),
                ("đẩy người bạn yêu thương vào vị thế của một đứa trẻ ngốc nghếch cần được răn dạy.", "slow")
            ],
            "desc_seeds": [
                ("A second red-crossed banner reading 'ANH ĐÃ BẢO RỒI MÀ' in warm-brown ink", "concept_metaphor"),
                ("Mây kneeling beside a spilled cardboard box looking troubled", "full_scene"),
                ("Tũn standing tall with folded arms looking down with self-righteous expression", "full_scene"),
                ("A heavy wooden pointer tapping sternly on an empty lesson chart", "still_life"),
                ("A tiny shrinking figure of Mây standing on a lowering podium", "concept_metaphor"),
                ("The delicate balance of equal partnership swaying unsteadily on cream canvas", "visual_diagram")
            ]
        },
        # SC07 (~66 words)
        {
            "id": "SC07",
            "title": "Câu nói sát thương 3: Tùy, muốn sao cũng được",
            "purpose": "Vạch trần bản chất buông xuôi và sự khinh miệt gián tiếp",
            "sit": "mechanism_step",
            "phase": "structural_model",
            "narration": "Và câu nói có sức công phá nguy hiểm nhất chính là tùy, muốn sao cũng được. Đằng sau sự thờ ơ lạnh lùng này là sự cự tuyệt đối thoại hoàn toàn. Nó phát đi một tín hiệu ngầm rằng bạn đã hết kiên nhẫn và không còn tha thiết vun đắp. Sự im lặng bất cần này gây tổn thương sâu sắc hơn vạn lời trách móc công khai.",
            "req": "R07",
            "quotes": [
                ("Và câu nói có sức công phá nguy hiểm nhất", "fast"),
                ("chính là tùy, muốn sao cũng được.", "normal"),
                ("Đằng sau sự thờ ơ lạnh lùng này", "slow"),
                ("là sự cự tuyệt đối thoại hoàn toàn.", "normal"),
                ("Nó phát đi một tín hiệu ngầm rằng bạn đã hết kiên nhẫn và không còn tha thiết vun đắp.", "fast"),
                ("Sự im lặng bất cần này gây tổn thương sâu sắc hơn vạn lời trách móc công khai.", "slow")
            ],
            "desc_seeds": [
                ("A third crossed-out card reading 'TÙY, MUỐN SAO CŨNG ĐƯỢC' crumbling into dust", "concept_metaphor"),
                ("Tũn looking out the window with a detached empty profile", "full_scene"),
                ("A phone screen with an unanswered call dissolving into pale lavender mist", "macro_prop"),
                ("A cold stone bridge suddenly retracting, cutting off the connecting path", "concept_metaphor"),
                ("Mây standing at the edge of the broken pathway holding an empty lantern", "full_scene"),
                ("A thick glass wall appearing silently between the two seated partners", "environment")
            ]
        },
        # SC08 (~66 words, editorial_commentary)
        {
            "id": "SC08",
            "title": "Lời bình: Cái giá của sự bất cần",
            "purpose": "Bình luận sâu sắc về sự xói mòn tình cảm âm thầm qua từng lần buông lời bất cần",
            "sit": "editorial_commentary",
            "phase": "structural_model",
            "narration": "Mỗi lần thốt ra một lời cay đắng là một lần bạn rút đi một viên gạch nâng đỡ tổ ấm chung. Sự tổn thương tích tụ âm thầm qua năm tháng sẽ bào mòn lòng trắc ẩn giữa hai con người. Đến khi niềm tin cạn kiệt, dù bạn có hối hận van xin thì tình cảm cũng đã hóa thành một vùng đất cằn cỗi hoang tàn.",
            "req": "R08",
            "quotes": [
                ("Mỗi lần thốt ra một lời cay đắng", "normal"),
                ("là một lần bạn rút đi một viên gạch nâng đỡ tổ ấm chung.", "slow"),
                ("Sự tổn thương tích tụ âm thầm qua năm tháng", "slow"),
                ("sẽ bào mòn lòng trắc ẩn giữa hai con người.", "normal"),
                ("Đến khi niềm tin cạn kiệt, dù bạn có hối hận van xin", "normal"),
                ("thì tình cảm cũng đã hóa thành một vùng đất cằn cỗi hoang tàn.", "slow")
            ],
            "desc_seeds": [
                ("A hand gently removing a pastel building block from the base of a cozy home", "concept_metaphor"),
                ("The small pastel house leaning precariously on flat cream canvas #FFF8F0", "still_life"),
                ("A fragile ceramic heart showing fine hairline spiderweb cracks filled with gold", "macro_prop"),
                ("Mây touching the ceramic heart with quiet sadness in soft ambient light", "full_scene"),
                ("Tũn standing on the far side looking with deep regret at the cracked heart", "full_scene"),
                ("Two gentle warm-brown hands reaching toward each other across the space", "concept_metaphor")
            ]
        },
        # SC09 (~66 words)
        {
            "id": "SC09",
            "title": "Công thức đối thoại ba bước thấu cảm",
            "purpose": "Trình bày cấu trúc giao tiếp 3 bước hóa giải phản xạ phòng thủ",
            "sit": "actionable_resolution",
            "phase": "actionable_resolution",
            "narration": "Để hóa giải triệt để hiệu ứng phòng thủ, người trưởng thành áp dụng công thức ba bước vàng. Bước một là chủ động dừng lại ba giây để điều hòa hơi thở. Bước hai là gọi tên và công nhận cảm xúc hiện tại của đối phương. Và bước ba là chuyển đổi góc nhìn, cùng nhau hướng tới giải pháp mang tính xây dựng chung.",
            "req": "R09",
            "quotes": [
                ("Để hóa giải triệt để hiệu ứng phòng thủ,", "fast"),
                ("người trưởng thành áp dụng công thức ba bước vàng.", "normal"),
                ("Bước một là chủ động dừng lại ba giây để điều hòa hơi thở.", "normal"),
                ("Bước hai là gọi tên và công nhận", "fast"),
                ("cảm xúc hiện tại của đối phương.", "normal"),
                ("Và bước ba là chuyển đổi góc nhìn, cùng nhau hướng tới giải pháp mang tính xây dựng chung.", "normal")
            ],
            "desc_seeds": [
                ("A beautiful three-tier pastel staircase blueprint glowing on cream canvas", "visual_diagram"),
                ("Step 1 card: A calm pocket watch showing 3 seconds with a serene breath wave", "concept_metaphor"),
                ("Step 2 card: Two hands gently cradling an emotional heart symbol with warmth", "concept_metaphor"),
                ("Step 3 card: Two gears fitting smoothly together with a bright lightbulb", "visual_diagram"),
                ("Tũn holding the three-step guide with an inspired calm smile", "full_scene"),
                ("Mây stepping closer with relieved expression as tension softens", "full_scene")
            ]
        },
        # SC10 (~66 words)
        {
            "id": "SC10",
            "title": "Thực hành phản hồi thấu cảm",
            "purpose": "Minh họa tình huống đối thoại thực tế áp dụng quy tắc",
            "sit": "mechanism_step",
            "phase": "actionable_resolution",
            "narration": "Thay vì cáu gắt trách móc sao em vô lý vậy, hãy bình tĩnh nói anh hiểu em đang rất buồn phiền vì sự việc này. Một lời lắng nghe thấu cảm sẽ lập tức tháo ngòi cơn bốc hỏa của đối phương. Khi cảm giác an toàn được khôi phục, hai bạn sẽ dễ dàng tìm ra tiếng nói chung trong mọi khúc mắc.",
            "req": "R10",
            "quotes": [
                ("Thay vì cáu gắt trách móc sao em vô lý vậy,", "fast"),
                ("hãy bình tĩnh nói anh hiểu em đang rất buồn phiền vì sự việc này.", "normal"),
                ("Một lời lắng nghe thấu cảm", "fast"),
                ("sẽ lập tức tháo ngòi cơn bốc hỏa của đối phương.", "normal"),
                ("Khi cảm giác an toàn được khôi phục,", "normal"),
                ("hai bạn sẽ dễ dàng tìm ra tiếng nói chung trong mọi khúc mắc.", "normal")
            ],
            "desc_seeds": [
                ("A sharp red speech bubble saying 'VÔ LÝ' dissolving into thin air", "concept_metaphor"),
                ("Tũn stepping forward with open posture and warm gentle smile", "full_scene"),
                ("Tũn and Mây sharing a tender warm hug on solid cream background #FFF8F0", "full_scene"),
                ("A soft wave of mint and blush light washing away remaining grey dust motes", "concept_metaphor"),
                ("Mây resting her head comfortably on Tũn shoulder with peaceful dot eyes", "full_scene"),
                ("Tũn and Mây standing side by side looking at a shared sunrise horizon", "environment")
            ]
        },
        # SC11 (~67 words)
        {
            "id": "SC11",
            "title": "Quy tắc vàng và lời kết",
            "purpose": "Đúc kết thông điệp cốt lõi và gửi trao lời kết ấm áp",
            "sit": "cta_close",
            "phase": "actionable_resolution",
            "narration": "Trong hành trình yêu đương, chiến thắng lớn nhất là nắm tay nhau vượt qua sóng gió chứ không phải đè bẹp cái tôi của người kia. Tình cảm bền lâu được tạo dựng từ sự kiên nhẫn thấu suốt. Hãy lắng nghe để thấu hiểu người bạn thương mỗi ngày bạn nhé. Thương Cho Khéo luôn đồng hành trên con đường vun đắp hạnh phúc của bạn.",
            "req": "R11",
            "quotes": [
                ("Trong hành trình yêu đương,", "fast"),
                ("chiến thắng lớn nhất là nắm tay nhau vượt qua sóng gió", "normal"),
                ("chứ không phải đè bẹp cái tôi của người kia.", "normal"),
                ("Tình cảm bền lâu được tạo dựng từ sự kiên nhẫn thấu suốt.", "normal"),
                ("Hãy lắng nghe để thấu hiểu người bạn thương mỗi ngày bạn nhé.", "normal"),
                ("Thương Cho Khéo luôn đồng hành trên con đường vun đắp hạnh phúc của bạn.", "hold")
            ],
            "desc_seeds": [
                ("A golden pastel trophy turning into a warm cup of cocoa shared between two hands", "concept_metaphor"),
                ("Tũn and Mây walking hand in hand under a gentle pastel umbrella in the rain", "full_scene"),
                ("The rain clearing as a soft warm rainbow connects two sides of cream canvas", "environment"),
                ("Tũn and Mây sitting together on a bench looking warmly at the camera", "full_scene"),
                ("Close up of their linked hands with soft heart sparkle accents", "cutaway_detail"),
                ("Official Thương Cho Khéo channel endcard with Tũn and Mây smiling and waving on cream canvas with text 'BẢN ĐẦY ĐỦ TRÊN YOUTUBE'", "white_card")
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

            img_desc = f"Soft 2D pastel line-art illustration: {desc_seed}, drawn with smooth thin warm-brown outlines #5B4636, flat unshaded fills in blush pink #F7C6C7, lavender #CDB4DB, mint #BDE0C6 and butter #FFF1B5 on flat solid cream canvas #FFF8F0, simple chibi proportions, orthographic 2D, >=60% negative space, no gradients, no 3D."

            motion_prompt = (
                "Smooth 2D pastel animation, gentle breathing idle hold, silent visual storytelling, no talking, no lip movement"
                if is_last_beat
                else f"Smooth 2D pastel animation. Characters move with subtle gentle gestures matching the emotional tone, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
            )

            img_obj = {
                "id": img_id,
                "description": img_desc,
                "character_ids": ["CH01"] if "Tũn" in desc_seed or "Mây" in desc_seed else [],
                "based_on": None,
                "preserve": "Cream canvas #FFF8F0, warm-brown linework #5B4636, soft pastel palette.",
                "change": desc_seed,
                "reason": f"Narration-locked full-frame beat {img_id}.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": shot_type,
                "tempo": tempo,
                "narrative_situation": sc_def["sit"],
                "has_character": ("Tũn" in desc_seed or "Mây" in desc_seed),
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
            "action": "Tũn và Mây diễn xuất qua các hành động đối thoại và minh họa tâm lý",
            "setting": "Không gian phòng khách và thế giới nội tâm tối giản trên nền kem",
            "camera": "Góc quay thẳng chính diện trung cảnh và cận cảnh biểu cảm",
            "narration": sc_def["narration"],
            "requirements": [req_id],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Tâm sự, ấm áp, thấu hiểu",
            "narrative_phase": sc_def["phase"],
            "narrative_situation": sc_def["sit"],
            "images": images,
            "beats": beats
        }
        scenes.append(scene_obj)
        coverage.append({"requirement_id": req_id, "scene_id": sc_id, "quote": quotes[0][0]})

    claims = [
        {
            "scene_id": "SC02",
            "quote": "Các nhà tâm lý học gọi hiện tượng này là hiệu ứng phòng thủ nhận thức.",
            "language": "vi",
            "source_id": "SRC01",
            "fact": "Phản ứng phòng thủ xuất hiện khi đối phương cảm thấy bị đe dọa lòng tự trọng."
        },
        {
            "scene_id": "SC05",
            "quote": "Câu nói độc hại đầu tiên thường gặp là em luôn luôn như vậy.",
            "language": "vi",
            "source_id": "SRC01",
            "fact": "Bốn phản xạ nguy hại làm tổn thương mối quan hệ: Chỉ trích, Phòng thủ, Khinh miệt và Chiến tranh lạnh."
        },
        {
            "scene_id": "SC09",
            "quote": "Để hóa giải triệt để hiệu ứng phòng thủ, người trưởng thành áp dụng công thức ba bước vàng.",
            "language": "vi",
            "source_id": "SRC01",
            "fact": "Giao tiếp bất bạo động khuyến khích mô tả hành vi thay vì phán xét nhân cách."
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
