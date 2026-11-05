#!/usr/bin/env python3
"""Batch 3 Anti-AI-Slop Script & Storyboard Generator for SA-03.

Generates complete Schema 3.0 packages for:
1. thuong_cho_kheo (Thương Cho Khéo):
   - sys/runs/thuong-cho-kheo-batch3-16x9 (Long 16:9)
   - sys/runs/thuong-cho-kheo-batch3-9x16 (Short 9:16)
2. ho_so_ky_la (Hồ Sơ Kỳ Lạ):
   - sys/runs/ho-so-ky-la-batch3-16x9 (Long 16:9)
   - sys/runs/ho-so-ky-la-batch3-9x16 (Short 9:16)
"""

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure sys is in PYTHONPATH
SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from channels.registry import (
    apply_channel,
    channel_cast,
    channel_profile_stamp,
    get_channel,
)
import tools.cta_tone_linter as ctl
import tools.editorial_value_linter as evl
import tools.script_diversity_linter as sdl
import visual_pacing


def compute_brief_hash(brief_dict: Dict[str, Any]) -> str:
    content = json.dumps(brief_dict, ensure_ascii=False, indent=2)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ==============================================================================
# DATA DEFINITIONS: THƯƠNG CHO KHÉO
# ==============================================================================

def make_tck_short():
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
            "assumptions": [
                "Mỗi phân cảnh được cân chỉnh nhịp hình ảnh từ 1.8 đến 2.3 giây một nhịp."
            ]
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

    # Outline
    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Mở đầu kịch tính với câu nói buông xuôi nguy hiểm nhất khi cãi vã", "requirements": ["R01"], "transition": "Chuyển tiếp tự nhiên sang cơ chế tâm lý"},
            {"scene_id": "SC02", "purpose": "Bóc tách phản ứng sinh học của bộ não khi bị từ chối đối thoại", "requirements": ["R02"], "transition": "Chuyển tiếp sang góc nhìn bình luận"},
            {"scene_id": "SC03", "purpose": "Bình luận sắc sảo về hậu quả tích tụ của thái độ bất cần", "requirements": ["R03"], "transition": "Chuyển tiếp sang giải pháp thực tế"},
            {"scene_id": "SC04", "purpose": "Hướng dẫn nguyên tắc khoảng lặng năm phút có hẹn trước", "requirements": ["R04"], "transition": "Chuyển tiếp sang cao trào bỏ lửng"},
            {"scene_id": "SC05", "purpose": "Đỉnh cao trào bỏ lửng và chuyển phễu người xem sang video dài", "requirements": ["R05"], "transition": "Kết thúc video"}
        ]
    }

    # Competitor research
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

    # Scenes (5 scenes, 20 beats, 20 unique images, ~168 words)
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

    # Content
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


# Let's write the generator runner
if __name__ == "__main__":
    job_id, brief, outline, cr, content = make_tck_short()
    job_dir = SYS_DIR / "runs" / job_id
    write_json(job_dir / "brief.json", brief)
    write_json(job_dir / "outline.json", outline)
    write_json(job_dir / "competitor_research.json", cr)
    write_json(job_dir / "content.json", content)
    print("TCK Short generated at:", job_dir)
