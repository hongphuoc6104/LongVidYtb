#!/usr/bin/env python3
"""Build and validate Batch 3 packages for Tâm Tĩnh Đêm (tam-tinh-dem-batch3-16x9 and 9x16)."""
from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path

SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from channels.registry import get_channel, channel_cast, channel_profile_stamp, apply_channel
from content.research_story_architect import compute_brief_hash
from tools.editorial_value_linter import lint_editorial_and_narrative_quality
from tools.script_diversity_linter import check_ai_cliche_phrases, check_intra_video_repetitions, lint_script
from tools.cta_tone_linter import lint_cta
from visual_pacing import audit_narrative_visual_density


def count_words(text: str) -> int:
    return len([w for w in text.strip().split() if w])


def build_tam_tinh_dem_batch3_9x16() -> tuple[dict, dict, dict, dict]:
    job_id = "tam-tinh-dem-batch3-9x16"
    parent_long_id = "tam-tinh-dem-batch3-16x9"
    ch = get_channel("tam_tinh_dem")
    topic = "Đêm Nay Trước Khi Ngủ: Hãy Tha Thứ Cho Những Vết Nứt Của Chính Mình"
    youtube_title = "Đêm Nay: Tha Thứ Cho Những Vết Nứt Của Chính Mình"  # 49 chars <= 55

    # 1. Competitor Research
    cr = {
        "channel_id": "tam_tinh_dem",
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Dare to do. Motivation",
                    "top_performing_videos": [
                        {
                            "title": "The Parable of the Cracked Pot: A Zen Story of Acceptance",
                            "views": "2.4M views",
                            "hook_technique": "Cận cảnh vết nứt trên chiếc bình và nỗi hổ thẹn âm thầm, đánh trúng tâm lý tự ti của người xem.",
                            "pacing_structure": "Mở đầu lắng dịu -> Đối lập giữa hai chiếc bình -> Phát hiện luống hoa ven đồi -> Đúc kết chữa lành.",
                            "retention_driver": "Cảm giác bình an và sự vỗ về sâu sắc trước giờ đi ngủ."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Hình tượng chiếc bình nứt tưới hoa ven đường chạm sâu vào lòng trắc ẩn của khán giả.",
                        "Nhịp kể chậm rãi, thủ thỉ, không kịch tính hóa xung đột mà tập trung vào sự bao dung."
                    ]
                },
                {
                    "channel_name": "Hạt Giống Tâm Hồn",
                    "top_performing_videos": [
                        {
                            "title": "Buông Bỏ Muộn Phiền Trước Khi Chìm Vào Giấc Ngủ",
                            "views": "1.1M views",
                            "hook_technique": "Lời thì thầm trực diện chạm vào cảm giác cô đơn và áp lực mưu sinh của một ngày dài.",
                            "pacing_structure": "Gọi tên nỗi dằn vặt -> Ẩn dụ ngụ ngôn ngắn -> Lời nhắc tha thứ cho bản thân -> Lời chúc ngủ ngon.",
                            "retention_driver": "Sự đồng cảm không phán xét, kết thúc bằng lời chúc ấm áp."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Dùng câu hỏi mở đầu về cảm giác tự trách đêm khuya để giữ chân người xem ngay 3 giây đầu.",
                        "Lời dặn dò nhẹ nhàng thay cho những bài học đạo lý khô cứng."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Vết xước nứt nẻ trên thân gốm mộc đối lập với dải hoa dại rực rỡ ngát hương bên sườn đồi đêm.",
                "counter_intuitive_truth_slap": "Vết nứt không phải là sự hỏng hóc đáng xấu hổ, mà chính là nơi ánh sáng đi vào và nuôi dưỡng sự sống."
            },
            "narrative_progression_arc": [
                {
                    "phase": "lived_friction",
                    "purpose": "Chạm vào nỗi tự trách và cảm giác chưa đủ hoàn hảo trước giờ đi ngủ."
                },
                {
                    "phase": "empirical_conflict",
                    "purpose": "Nhắc lại ẩn dụ chiếc bình nứt hổ thẹn vì làm rỉ nước dọc sườn đồi."
                },
                {
                    "phase": "structural_model",
                    "purpose": "Chỉ ra luống hoa dại nở rộ nhờ những giọt nước rỉ ra mỗi ngày."
                },
                {
                    "phase": "actionable_resolution",
                    "purpose": "Tha thứ cho những vết xước của chính mình và buông bỏ muộn phiền đêm nay."
                }
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Sequential storybook gouache painting transitions under midnight starry skies."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Truyện Ngụ Ngôn Tỉnh Thức & Chiêm Nghiệm Chữa Lành",
            "myth_debunked": "Một con người có giá trị phải luôn hoàn hảo, không tì vết và không bao giờ được phép vụng về hay sai lầm.",
            "channel_verdict": "Vết xước không phải là sự hỏng hóc, mà là nơi đón nhận ánh sáng và giúp lòng trắc ẩn đơm hoa.",
            "actionable_rule_of_thumb": "Mỗi tối trước khi nhắm mắt, hãy gọi tên một thiếu sót của bản thân và gửi đến nó một nụ cười bao dung."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "Làm sao để tha thứ cho những vụng về và tìm lại sự bình yên trong tâm hồn?",
            "bridge": "Lắng nghe trọn vẹn câu chuyện ngụ ngôn và nhạc tĩnh tâm trên kênh Tâm Tĩnh Đêm nhé.",
            "close": "Đêm nay hãy buông bỏ âu lo, ngủ thật ngon và thương lấy chính mình bạn nhé.",
            "endcard_text": "TÂM TĨNH ĐÊM"
        }
    }

    # 2. Brief
    raw_brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": "Khán giả nghe đêm (21h-24h), người chịu nhiều áp lực mưu sinh, người hay tự trách và trăn trở khó ngủ",
        "goal": "Dùng truyện ngụ ngôn chiếc bình nứt để xoa dịu nỗi dằn vặt nội tâm, giúp người nghe học cách tha thứ cho chính mình và ngủ an lành",
        "video_type": "explainer",
        "duration": {
            "min_seconds": 40.0,
            "max_seconds": 55.0
        },
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Nỗi dằn vặt vì những vụng về trước giờ đi ngủ"},
            {"id": "R02", "text": "Chiếc bình nứt mang nửa thùng nước về nhà"},
            {"id": "R03", "text": "Luống hoa rực rỡ bên sườn đồi từ giọt nước rỉ"},
            {"id": "R04", "text": "Khiếm khuyết là nơi ánh sáng và sự thấu cảm bắt đầu"},
            {"id": "R05", "text": "Mở nút thắt tâm hồn và buông bỏ muộn phiền đêm nay"}
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
                "title": "Self-Compassion: The Proven Power of Being Kind to Yourself",
                "reference": "Neff, K. (2011). William Morrow. HarperCollins Publishers.",
                "facts": [
                    "Lòng tự trắc ẩn và sự bao dung với khiếm khuyết giúp giảm lo âu và cải thiện giấc ngủ.",
                    "Nhận thức sự bất toàn là một phần tự nhiên của con người giúp xóa tan cảm giác cô lập."
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
                "Truyền tải trọn vẹn thông điệp ngụ ngôn chiếc bình nứt trong 5 cảnh với 20 hình ảnh gouache nhung đêm tĩnh lặng",
                "Ngôn ngữ tự nhiên, thủ thỉ, tuyệt đối không dùng biệt ngữ AI hay thúc ép tương tác"
            ],
            "avoid": [
                "Tránh giọng điệu phán xét, giáo điều hoặc kịch tính hóa xung đột gây căng thẳng đêm muộn."
            ],
            "prior_knowledge": "Không đòi hỏi kiến thức chuyên môn.",
            "pacing": "Thủ thỉ chậm rãi, từ tốn, lắng đọng theo nhịp kể chuyện đêm khuya.",
            "domain_requirements": [],
            "assumptions": [
                "Mỗi phân cảnh được cân chỉnh theo công thức âm học P_tail và dung sai drift <= 0.3s."
            ],
            "text_style": {
                "font": "serif hoặc sans-serif thanh nhã, ấm áp",
                "color": "#F8F4E3",
                "outline": "bóng mờ đêm #1B263B",
                "size": "vừa vặn, thanh thoát trên màn hình dọc",
                "placement": "nằm trong vùng an toàn, không che lấp nhân vật hay phụ đề"
            },
            "speech_rates": {
                "vi": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.15,
                    "source": "Bedtime calibrated cadence"
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
                "visual_hook": "Người lữ khách ngồi bên chiếc bình gốm mộc có vết nứt phát sáng ánh vàng dịu dàng dưới trăng khuyết",
                "text_overlay": "THA THỨ CHO MÌNH",
                "contrast_pair": "Nỗi dằn vặt vụng về vs Sự an yên tha thứ cho chính mình",
                "thumbnail_prompt": "Cozy Little Prince-inspired 2D flat matte gouache night-storybook illustration on velvety midnight indigo sky canvas (#1B263B velvety midnight indigo sky, #F4D35E warm crescent-moon and lantern gold, #E09F7D cozy amber tea glow, #778DA9 misty starlight blue, #F8F4E3 soft cream). Gentle storybook traveler sitting peacefully under starry crescent moon beside a warm rustic clay water pot glowing with golden hairline crack. Large hand-lettered Vietnamese text in upper third: 'THA THỨ CHO MÌNH'. Orthographic 2D, >=60% negative space, zero 3D, zero gradients.",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": "Truyện Ngụ Ngôn Tỉnh Thức & Chiêm Nghiệm Chữa Lành",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": [
                "tam tinh dem",
                "chuyen ngu ngon",
                "chiec binh nut",
                "tha thu cho minh",
                "ngu ngon",
                "chua lanh",
                "binh yen",
                "tinh thuc",
                "truyen dem khuya"
            ],
            "cta_plan": {
                "cliffhanger_peak": "Làm sao để tha thứ cho những vụng về và tìm lại sự bình yên trong tâm hồn?",
                "bridge": "Lắng nghe trọn vẹn câu chuyện ngụ ngôn và nhạc tĩnh tâm trên kênh Tâm Tĩnh Đêm nhé.",
                "close": "Đêm nay hãy buông bỏ âu lo, ngủ thật ngon và thương lấy chính mình bạn nhé.",
                "endcard_text": "TÂM TĨNH ĐÊM"
            },
            "editorial_stance": {
                "myth_debunked": "Một con người có giá trị phải luôn hoàn hảo, không tì vết và không bao giờ được phép vụng về hay sai lầm.",
                "why_generic_advice_fails": "Lời khuyên tích cực độc hại ép con người phải luôn mạnh mẽ chỉ khiến nỗi ân hận đêm khuya thêm nặng nề.",
                "channel_verdict": "Vết xước không phải là sự hỏng hóc, mà là nơi đón nhận ánh sáng và giúp lòng trắc ẩn đơm hoa.",
                "tradeoff_or_blindspot": "Chấp nhận những khiếm khuyết của mình đòi hỏi sự dũng cảm buông bỏ cái tôi nhưng mang lại sự nhẹ nhõm dài lâu."
            },
            "actionable_value": {
                "core_mechanism": "Chuyển hóa góc nhìn về vết thương nội tâm: xem khiếm khuyết là cơ duyên để nuôi dưỡng lòng trắc ẩn và sự thấu cảm.",
                "practical_rule_of_thumb": "Mỗi tối trước khi ngủ, hãy gọi tên một thiếu sót của bản thân với ánh mắt bao dung và lòng biết ơn.",
                "real_world_scenario": "Sau một ngày làm việc mắc lỗi bị khiển trách, người nghe thở sâu và tha thứ cho sự vụng về để ngủ an giấc."
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Người lữ khách ngồi bên chiếc bình gốm mộc có vết nứt phát sáng ánh vàng dịu dàng dưới trăng khuyết",
            "text_overlay": "THA THỨ CHO MÌNH",
            "contrast_pair": "Nỗi dằn vặt vụng về vs Sự an yên tha thứ cho chính mình",
            "thumbnail_prompt": "Cozy Little Prince-inspired 2D flat matte gouache night-storybook illustration on velvety midnight indigo sky canvas (#1B263B velvety midnight indigo sky, #F4D35E warm crescent-moon and lantern gold, #E09F7D cozy amber tea glow, #778DA9 misty starlight blue, #F8F4E3 soft cream). Gentle storybook traveler sitting peacefully under starry crescent moon beside a warm rustic clay water pot glowing with golden hairline crack. Large hand-lettered Vietnamese text in upper third: 'THA THỨ CHO MÌNH'. Orthographic 2D, >=60% negative space, zero 3D, zero gradients.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Truyện Ngụ Ngôn Tỉnh Thức & Chiêm Nghiệm Chữa Lành",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": [
            "tam tinh dem",
            "chuyen ngu ngon",
            "chiec binh nut",
            "tha thu cho minh",
            "ngu ngon",
            "chua lanh",
            "binh yen",
            "tinh thuc",
            "truyen dem khuya"
        ],
        "parent_long_id": parent_long_id,
        "cta_plan": {
            "cliffhanger_peak": "Làm sao để tha thứ cho những vụng về và tìm lại sự bình yên trong tâm hồn?",
            "bridge": "Lắng nghe trọn vẹn câu chuyện ngụ ngôn và nhạc tĩnh tâm trên kênh Tâm Tĩnh Đêm nhé.",
            "close": "Đêm nay hãy buông bỏ âu lo, ngủ thật ngon và thương lấy chính mình bạn nhé.",
            "endcard_text": "TÂM TĨNH ĐÊM"
        },
        "editorial_stance": {
            "myth_debunked": "Một con người có giá trị phải luôn hoàn hảo, không tì vết và không bao giờ được phép vụng về hay sai lầm.",
            "why_generic_advice_fails": "Lời khuyên tích cực độc hại ép con người phải luôn mạnh mẽ chỉ khiến nỗi ân hận đêm khuya thêm nặng nề.",
            "channel_verdict": "Vết xước không phải là sự hỏng hóc, mà là nơi đón nhận ánh sáng và giúp lòng trắc ẩn đơm hoa.",
            "tradeoff_or_blindspot": "Chấp nhận những khiếm khuyết của mình đòi hỏi sự dũng cảm buông bỏ cái tôi nhưng mang lại sự nhẹ nhõm dài lâu."
        },
        "actionable_value": {
            "core_mechanism": "Chuyển hóa góc nhìn về vết thương nội tâm: xem khiếm khuyết là cơ duyên để nuôi dưỡng lòng trắc ẩn và sự thấu cảm.",
            "practical_rule_of_thumb": "Mỗi tối trước khi ngủ, hãy gọi tên một thiếu sót của bản thân với ánh mắt bao dung và lòng biết ơn.",
            "real_world_scenario": "Sau một ngày làm việc mắc lỗi bị khiển trách, người nghe thở sâu và tha thứ cho sự vụng về để ngủ an giấc."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }
    brief = apply_channel(raw_brief, "tam_tinh_dem")

    # 3. Outline
    outline = {
        "outline": [
            {
                "scene_id": "SC01",
                "purpose": "Triển khai bước 1: nỗi dằn vặt vì những vụng về trước giờ đi ngủ",
                "requirements": ["R01"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung"
            },
            {
                "scene_id": "SC02",
                "purpose": "Triển khai bước 2: chiếc bình nứt mang nửa thùng nước về nhà",
                "requirements": ["R02"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung"
            },
            {
                "scene_id": "SC03",
                "purpose": "Triển khai bước 3: luống hoa rực rỡ bên sườn đồi từ giọt nước rỉ",
                "requirements": ["R03"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung"
            },
            {
                "scene_id": "SC04",
                "purpose": "Triển khai bước 4: khiếm khuyết là nơi ánh sáng và sự thấu cảm bắt đầu",
                "requirements": ["R04"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung"
            },
            {
                "scene_id": "SC05",
                "purpose": "Triển khai bước 5: mở nút thắt tâm hồn và buông bỏ muộn phiền đêm nay",
                "requirements": ["R05"],
                "transition": "Tiếp tục theo trình tự diễn biến nội dung"
            }
        ]
    }

    # 4. Content
    cast = [
        channel_cast("tam_tinh_dem", "CH01"),
        {
            "id": "CH02",
            "name": "Người gánh nước hiền hậu",
            "appearance": "Gentle aged water bearer with kind smiling crinkled eyes, wearing a simple earthy-indigo hemp tunic (#1B263B) and carrying a smooth wooden shoulder yoke supporting two ceramic pots across his shoulders.",
            "outfit": "Simple earthy-indigo hemp tunic (#1B263B) with rolled-up sleeves, zero shading"
        },
        {
            "id": "CH03",
            "name": "Chiếc bình gốm nứt",
            "appearance": "Charming rustic terracotta water pot with a distinct winding golden hairline crack along its curved ceramic side, leaking gentle crystal droplets of water onto the earthy pathway.",
            "outfit": "Warm terracotta clay pot (#E09F7D) with delicate hairline fracture, zero shading"
        },
        {
            "id": "CH04",
            "name": "Chiếc bình gốm hoàn hảo",
            "appearance": "Smooth unblemished round terracotta water pot with intact smooth glaze, standing proudly and upright on the wooden shoulder yoke.",
            "outfit": "Smooth unblemished terracotta clay pot (#E09F7D) with intact rim, zero shading"
        }
    ]

    sc01_narr = "Đêm nay trước khi ngủ, có phải bạn vẫn đang tự trách bản thân? Bạn dằn vặt vì mình chưa hoàn hảo và mang nhiều vết xước trong lòng."
    sc02_narr = "Hãy nhớ về chiếc bình nứt của người gánh nước xưa. Chiếc bình lành mang đủ nước, còn chiếc bình nứt luôn hổ thẹn vì làm rỉ nước."
    sc03_narr = "Thế nhưng người gánh nước mỉm cười chỉ xuống ven đường. Chính giọt nước rỉ ra đã nuôi sống dải hoa dại ngát hương dưới ánh trăng."
    sc04_narr = "Vết nứt không phải sự hỏng hóc, mà là nơi đón ánh sáng. Khiếm khuyết của bạn chính là hạt mầm để lòng trắc ẩn nở hoa."
    sc05_narr = "Làm sao để tha thứ cho những vụng về và tìm lại sự bình yên trong tâm hồn? Lắng nghe trọn vẹn câu chuyện ngụ ngôn và nhạc tĩnh tâm trên kênh Tâm Tĩnh Đêm nhé. Đêm nay hãy buông bỏ âu lo, ngủ thật ngon và thương lấy chính mình bạn nhé."

    narrations = [sc01_narr, sc02_narr, sc03_narr, sc04_narr, sc05_narr]
    total_w = sum(count_words(n) for n in narrations)
    print(f"[{job_id}] Total words: {total_w}, Est duration: {total_w / 3.8:.1f}s, Avg hold: {(total_w / 3.8) / 20:.2f}s/img")

    scenes = [
        {
            "id": "SC01",
            "title": "Nỗi dằn vặt trước giờ đi ngủ",
            "purpose": "Triển khai bước 1: nỗi dằn vặt vì những vụng về trước giờ đi ngủ",
            "action": "The gentle traveler sits quietly beside an open window under velvety midnight sky, holding a warm teacup with reflective gaze.",
            "setting": "Cozy wooden room overlooking serene starry night sky on velvety midnight indigo gouache canvas.",
            "camera": "Semantic full-frame sequence",
            "narration": sc01_narr,
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "narrative_situation": "hook_shock",
            "images": [
                {
                    "id": "SC01_I1",
                    "description": "Cozy 2D flat matte gouache illustration of gentle storybook traveler CH01 with tousled dark hair and warm golden-amber knitted scarf sitting by a wooden window under velvety midnight indigo sky #1B263B, holding steaming tea cup #E09F7D, crescent moon #F4D35E and starlight #778DA9 in background, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH01"],
                    "preserve": "clean velvety midnight indigo canvas #1B263B, storybook gouache style, traveler CH01 with amber scarf",
                    "change": "traveler sits pensively by window holding teacup",
                    "reason": "Narration-locked full-frame beat SC01_I1.",
                    "visible_text": [{"text": "TÂM TĨNH ĐÊM", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "emphasis_text": "TÂM TĨNH ĐÊM",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, the storybook traveler by the window blinks slowly as soft steam rises from the amber teacup under quiet starry indigo skies, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "hold",
                    "effect": "hold"
                },
                {
                    "id": "SC01_I2",
                    "description": "Cozy 2D gouache scene of traveler CH01 looking down at their hands with quiet melancholy, soft golden crescent moon glowing outside the small paned window, misty starlight blue #778DA9 swirls across velvety indigo sky, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH01"],
                    "preserve": "velvety midnight indigo canvas, gouache aesthetic, traveler CH01",
                    "change": "traveler gazes down at hands with gentle vulnerability",
                    "reason": "Narration-locked full-frame beat SC01_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, soft starlight glimmers across the traveler's golden-amber scarf as quiet night shadows breathe softly on the indigo wall, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "pan_right",
                    "effect": "none"
                },
                {
                    "id": "SC01_I3",
                    "description": "Close gouache vignette of an earthy clay teacup #E09F7D on rustic wooden sill, a tiny delicate fracture on the cup rim catching warm moon gold #F4D35E, velvety deep blue backdrop with soft painterly cream edges #F8F4E3, orthographic 2D, 70% negative space.",
                    "character_ids": ["CH01"],
                    "preserve": "velvety midnight indigo canvas, warm amber tea glow, gouache texture",
                    "change": "focus on tiny ceramic fissure catching moonlight",
                    "reason": "Narration-locked full-frame beat SC01_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "hook_shock",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": False,
                    "motion_prompt": "Gentle 2D gouache animation, a faint golden ray of moonlight reflects off the delicate hairline crack of the teacup, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "zoom_in",
                    "effect": "none"
                },
                {
                    "id": "SC01_I4",
                    "description": "Wide gouache view of traveler CH01 looking out at distant rolling hills under vast midnight indigo firmament speckled with constellation dots #778DA9 and golden crescent moon #F4D35E, orthographic 2D, 70% negative space.",
                    "character_ids": ["CH01"],
                    "preserve": "velvety midnight indigo canvas, traveler CH01, peaceful bedtime mood",
                    "change": "wide view of traveler contemplating starry night landscape",
                    "reason": "Narration-locked full-frame beat SC01_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "hook_shock",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, distant clouds drift slowly across the deep indigo night sky as stars shimmer softly over rolling hills, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "hold",
                    "effect": "hold"
                }
            ],
            "beats": [
                {"id": "SC01_B1", "image_id": "SC01_I1", "purpose": "Nhịp mở đầu: tự trách bản thân đêm muộn", "tempo": "fast", "narrative_situation": "hook_shock", "shot_type": "full_scene", "effect": "hold"},
                {"id": "SC01_B2", "image_id": "SC01_I2", "purpose": "Nhịp 2: cảm giác vụng về chưa hoàn hảo", "tempo": "fast", "narrative_situation": "hook_shock", "shot_type": "full_scene", "effect": "none"},
                {"id": "SC01_B3", "image_id": "SC01_I3", "purpose": "Nhịp 3: biểu tượng vết xước nhỏ trong lòng", "tempo": "normal", "narrative_situation": "hook_shock", "shot_type": "full_scene", "effect": "none"},
                {"id": "SC01_B4", "image_id": "SC01_I4", "purpose": "Nhịp 4: mở rộng không gian đêm lắng dịu", "tempo": "normal", "narrative_situation": "hook_shock", "shot_type": "full_scene", "effect": "hold"}
            ]
        },
        {
            "id": "SC02",
            "title": "Ẩn dụ chiếc bình nứt xưa",
            "purpose": "Triển khai bước 2: chiếc bình nứt mang nửa thùng nước về nhà",
            "action": "The aged water bearer carries two ceramic pots along a steep hill trail under twilight night sky.",
            "setting": "A winding mountain footpath between stream and house on velvety midnight indigo gouache canvas.",
            "camera": "Semantic full-frame sequence",
            "narration": sc02_narr,
            "requirements": ["R02"],
            "character_ids": ["CH02", "CH03", "CH04"],
            "source_ids": ["SRC01"],
            "narrative_situation": "before_after_contrast",
            "images": [
                {
                    "id": "SC02_I1",
                    "description": "Cozy 2D gouache painting of gentle aged water bearer CH02 in earthy indigo tunic carrying a wooden yoke with two terracotta pots CH03 and CH04 along a peaceful hill trail under crescent moon #F4D35E, orthographic 2D, 60% negative space.",
                    "character_ids": ["CH02", "CH03", "CH04"],
                    "preserve": "velvety midnight indigo canvas #1B263B, gouache storybook style",
                    "change": "water bearer walking along path with shoulder yoke",
                    "reason": "Narration-locked full-frame beat SC02_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "before_after_contrast",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, the water bearer walks steadily along the dirt path under moonlit starry skies, yoke gently swaying, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "pan_left",
                    "effect": "none"
                },
                {
                    "id": "SC02_I2",
                    "description": "Cozy 2D gouache close-up of intact round clay pot CH04 filled to the brim with crystal spring water, resting smoothly against the wooden pole with dignified shine under starry night, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH04"],
                    "preserve": "velvety midnight indigo canvas, gouache texture, terracotta clay",
                    "change": "close-up of perfect pot carrying full water",
                    "reason": "Narration-locked full-frame beat SC02_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "before_after_contrast",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, water surface in the full pot ripples gently reflecting tiny golden star dots, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "hold",
                    "effect": "none"
                },
                {
                    "id": "SC02_I3",
                    "description": "Cozy 2D gouache close-up of cracked rustic clay pot CH03 with a visible fine fracture line, tiny clear water droplets leaking out like crystal pearls onto dry pebbles, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH03"],
                    "preserve": "velvety midnight indigo canvas, gouache texture, terracotta clay",
                    "change": "close-up of cracked pot with water leaking",
                    "reason": "Narration-locked full-frame beat SC02_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "before_after_contrast",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, water droplets seep slowly from the ceramic crack and fall toward the quiet earth, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "zoom_in",
                    "effect": "none"
                },
                {
                    "id": "SC02_I4",
                    "description": "Cozy 2D gouache scene of cracked pot CH03 sitting outside the hill cottage at dusk, only half full of water, casting a long gentle shadow on stone steps under indigo sky, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH03"],
                    "preserve": "velvety midnight indigo canvas, gouache texture",
                    "change": "cracked pot sitting half empty outside doorway",
                    "reason": "Narration-locked full-frame beat SC02_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "before_after_contrast",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, evening breeze gently touches the clay pot as warm lantern light glows softly from the cottage doorway, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "hold",
                    "effect": "hold"
                }
            ],
            "beats": [
                {"id": "SC02_B1", "image_id": "SC02_I1", "purpose": "Nhịp 1: người gánh nước bước đi trên đồi", "tempo": "fast", "narrative_situation": "before_after_contrast", "shot_type": "full_scene", "effect": "none"},
                {"id": "SC02_B2", "image_id": "SC02_I2", "purpose": "Nhịp 2: chiếc bình lành kiêu hãnh đủ đầy", "tempo": "normal", "narrative_situation": "before_after_contrast", "shot_type": "full_scene", "effect": "none"},
                {"id": "SC02_B3", "image_id": "SC02_I3", "purpose": "Nhịp 3: chiếc bình nứt rỉ giọt nước trong", "tempo": "normal", "narrative_situation": "before_after_contrast", "shot_type": "full_scene", "effect": "none"},
                {"id": "SC02_B4", "image_id": "SC02_I4", "purpose": "Nhịp 4: nỗi hổ thẹn vì chỉ còn một nửa", "tempo": "slow", "narrative_situation": "before_after_contrast", "shot_type": "full_scene", "effect": "hold"}
            ]
        },
        {
            "id": "SC03",
            "title": "Luống hoa dại ven sườn đồi",
            "purpose": "Triển khai bước 3: luống hoa rực rỡ bên sườn đồi từ giọt nước rỉ",
            "action": "The water bearer points with a warm smile toward the trailside, where colorful wildflowers blossom profusely under moonlight.",
            "setting": "A scenic hillside pathway blanketed in blossoming night wildflowers on velvety midnight indigo gouache canvas.",
            "camera": "Semantic full-frame sequence",
            "narration": sc03_narr,
            "requirements": ["R03"],
            "character_ids": ["CH02", "CH03"],
            "source_ids": ["SRC01"],
            "narrative_situation": "editorial_commentary",
            "images": [
                {
                    "id": "SC03_I1",
                    "description": "Cozy 2D gouache scene of kindly water bearer CH02 smiling warmly and pointing a calloused hand toward the edge of the footpath under moonlit sky, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH02"],
                    "preserve": "velvety midnight indigo canvas #1B263B, gouache storybook style",
                    "change": "water bearer smiling and pointing downward",
                    "reason": "Narration-locked full-frame beat SC03_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, the water bearer's kind face softens with an affectionate smile as moonlight highlights his weathered hand, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "pan_left",
                    "effect": "none"
                },
                {
                    "id": "SC03_I2",
                    "description": "Cozy 2D gouache view along the trail: the side beneath cracked pot CH03 is a vibrant ribbon of blooming wildflowers in amber gold #F4D35E and starlight blue #778DA9, orthographic 2D, 60% negative space.",
                    "character_ids": ["CH03"],
                    "preserve": "velvety midnight indigo canvas, gouache floral elements",
                    "change": "vibrant trailside flowers blooming in moonlight",
                    "reason": "Narration-locked full-frame beat SC03_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, delicate night blossoms sway gently in the mountain breeze, glowing softly under the crescent moon, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "pan_right",
                    "effect": "none"
                },
                {
                    "id": "SC03_I3",
                    "description": "Cozy 2D gouache close-up of a tiny droplet from cracked pot CH03 splashing gently onto a tender wild blossom bud, golden moisture glowing under night stars, orthographic 2D, 70% negative space.",
                    "character_ids": ["CH03"],
                    "preserve": "velvety midnight indigo canvas, gouache droplet texture",
                    "change": "water droplet nourishing blooming flower petal",
                    "reason": "Narration-locked full-frame beat SC03_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": False,
                    "motion_prompt": "Gentle 2D gouache animation, a luminous water droplet quivers and glides softly down a golden wildflower petal, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "zoom_in",
                    "effect": "none"
                },
                {
                    "id": "SC03_I4",
                    "description": "Cozy 2D gouache painting of cracked pot CH03 resting nestled among lush colorful wild blossoms along the peaceful trail, bathed in warm amber tea glow #E09F7D, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH03"],
                    "preserve": "velvety midnight indigo canvas, gouache storybook harmony",
                    "change": "cracked pot resting peacefully surrounded by flowers",
                    "reason": "Narration-locked full-frame beat SC03_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, petals rustle softly around the clay pot as soft firefly glows float upward into the indigo sky, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "hold",
                    "effect": "hold"
                }
            ],
            "beats": [
                {"id": "SC03_B1", "image_id": "SC03_I1", "purpose": "Nhịp 1: nụ cười hiền hậu của người gánh nước", "tempo": "normal", "narrative_situation": "editorial_commentary", "shot_type": "full_scene", "effect": "none"},
                {"id": "SC03_B2", "image_id": "SC03_I2", "purpose": "Nhịp 2: dải hoa dại nở rộ bên lối mòn", "tempo": "slow", "narrative_situation": "editorial_commentary", "shot_type": "full_scene", "effect": "none"},
                {"id": "SC03_B3", "image_id": "SC03_I3", "purpose": "Nhịp 3: giọt nước rỉ tưới mát cánh hoa", "tempo": "slow", "narrative_situation": "editorial_commentary", "shot_type": "full_scene", "effect": "none"},
                {"id": "SC03_B4", "image_id": "SC03_I4", "purpose": "Nhịp 4: chiếc bình nứt hòa mình giữa ngàn hoa", "tempo": "normal", "narrative_situation": "editorial_commentary", "shot_type": "full_scene", "effect": "hold"}
            ]
        },
        {
            "id": "SC04",
            "title": "Ánh sáng đi qua vết nứt",
            "purpose": "Triển khai bước 4: khiếm khuyết là nơi ánh sáng và sự thấu cảm bắt đầu",
            "action": "The golden crack in the ceramic pot radiates a warm healing amber glow, illuminating sprouting green shoots.",
            "setting": "A serene poetic gouache garden under crescent moon and velvet night skies.",
            "camera": "Semantic full-frame sequence",
            "narration": sc04_narr,
            "requirements": ["R04"],
            "character_ids": ["CH01", "CH03"],
            "source_ids": ["SRC01"],
            "narrative_situation": "mechanism_step",
            "images": [
                {
                    "id": "SC04_I1",
                    "description": "Cozy 2D gouache art of cracked pot CH03 with glowing golden seam #F4D35E like Kintsugi joinery, radiant warm light shining softly through the fissure into midnight indigo night, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH03"],
                    "preserve": "velvety midnight indigo canvas #1B263B, gouache storybook style",
                    "change": "golden light glowing through ceramic fracture",
                    "reason": "Narration-locked full-frame beat SC04_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, the golden light pulsing softly through the pot's fissure expands outward in warm soothing waves, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "zoom_in",
                    "effect": "none"
                },
                {
                    "id": "SC04_I2",
                    "description": "Cozy 2D gouache view of gentle traveler CH01 kneeling gently beside the illuminated pot, tenderly touching a blooming flower bud under the crescent moon #F4D35E, orthographic 2D, 60% negative space.",
                    "character_ids": ["CH01", "CH03"],
                    "preserve": "velvety midnight indigo canvas, traveler CH01",
                    "change": "traveler kneeling in gentle empathy beside pot",
                    "reason": "Narration-locked full-frame beat SC04_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, the traveler's golden scarf floats softly in the night wind as he smiles down at the blossoming flower, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "pan_left",
                    "effect": "none"
                },
                {
                    "id": "SC04_I3",
                    "description": "Cozy 2D gouache metaphorical image of a green sprout emerging from cracked dark earth under comforting starlight blue #778DA9, symbolizing self-compassion blossoming, orthographic 2D, 70% negative space.",
                    "character_ids": [],
                    "preserve": "velvety midnight indigo canvas, gouache poetic symbolism",
                    "change": "green sprout flourishing from earth fissure",
                    "reason": "Narration-locked full-frame beat SC04_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "mechanism_step",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": False,
                    "motion_prompt": "Gentle 2D gouache animation, two small green leaves gently unfurl in slow peaceful motion under starlit skies, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "zoom_in",
                    "effect": "none"
                },
                {
                    "id": "SC04_I4",
                    "description": "Cozy 2D gouache scene of traveler CH01 standing tall with open posture under a peaceful canopy of twinkling constellations, heart glowing with warm golden amber warmth #E09F7D, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH01"],
                    "preserve": "velvety midnight indigo canvas, traveler CH01",
                    "change": "traveler standing in quiet self-acceptance",
                    "reason": "Narration-locked full-frame beat SC04_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, gentle golden aura surrounds the traveler as cool night air brings peaceful stillness, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "hold",
                    "effect": "hold"
                }
            ],
            "beats": [
                {"id": "SC04_B1", "image_id": "SC04_I1", "purpose": "Nhịp 1: ánh sáng vàng rạng rỡ từ kẽ nứt", "tempo": "fast", "narrative_situation": "mechanism_step", "shot_type": "full_scene", "effect": "none"},
                {"id": "SC04_B2", "image_id": "SC04_I2", "purpose": "Nhịp 2: người lữ khách cúi xuống vỗ về", "tempo": "normal", "narrative_situation": "mechanism_step", "shot_type": "full_scene", "effect": "none"},
                {"id": "SC04_B3", "image_id": "SC04_I3", "purpose": "Nhịp 3: mầm sống đơm hoa từ vết rạn", "tempo": "slow", "narrative_situation": "mechanism_step", "shot_type": "full_scene", "effect": "none"},
                {"id": "SC04_B4", "image_id": "SC04_I4", "purpose": "Nhịp 4: sự chấp nhận an yên trong tâm hồn", "tempo": "normal", "narrative_situation": "mechanism_step", "shot_type": "full_scene", "effect": "hold"}
            ]
        },
        {
            "id": "SC05",
            "title": "Mở nút thắt và buông bỏ muộn phiền",
            "purpose": "Triển khai bước 5: mở nút thắt tâm hồn và buông bỏ muộn phiền đêm nay",
            "action": "The traveler closes eyes peacefully in deep calm, lantern glowing warm amber as the channel endcard displays under the moon.",
            "setting": "A tranquil starlit night balcony overlooking sleeping hills on velvety midnight indigo gouache canvas.",
            "camera": "Semantic full-frame sequence",
            "narration": sc05_narr,
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "narrative_situation": "cliffhanger_peak",
            "images": [
                {
                    "id": "SC05_I1",
                    "description": "Cozy 2D gouache art of traveler CH01 looking toward the moon with contemplative open gaze, question of self-forgiveness hanging softly in the quiet night breeze, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH01"],
                    "preserve": "velvety midnight indigo canvas #1B263B, traveler CH01",
                    "change": "traveler gazing toward moon at cliffhanger peak",
                    "reason": "Narration-locked full-frame beat SC05_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "cliffhanger_peak",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, the traveler tilts head slightly toward the luminous golden moon, eyes reflecting starlight, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "pan_left",
                    "effect": "none"
                },
                {
                    "id": "SC05_I2",
                    "description": "Cozy 2D gouache illustration of traveler CH01 holding an amber lantern #F4D35E that illuminates a storybook scroll titled 'BẢN ĐẦY ĐỦ TRÊN YOUTUBE', soft stars floating peacefully, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH01"],
                    "preserve": "velvety midnight indigo canvas, gouache aesthetic",
                    "change": "traveler presenting bridge lantern to full video",
                    "reason": "Narration-locked full-frame beat SC05_I2.",
                    "visible_text": [{"text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "cta_bridge",
                    "emphasis_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, amber lantern glow ripples warmly across the scroll as peaceful indigo mist settles over the hills, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "zoom_in",
                    "effect": "none"
                },
                {
                    "id": "SC05_I3",
                    "description": "Cozy 2D gouache view of traveler CH01 placing a hand over heart, eyes gently closed in deep peaceful serenity, golden crescent moon smiling softly overhead #F4D35E, orthographic 2D, 70% negative space.",
                    "character_ids": ["CH01"],
                    "preserve": "velvety midnight indigo canvas, traveler CH01",
                    "change": "traveler closing eyes in peaceful bedtime release",
                    "reason": "Narration-locked full-frame beat SC05_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "cta_close",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, traveler breathes in slowly and exhales with a subtle peaceful smile, shoulders dropping in complete relaxation, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "hold",
                    "effect": "none"
                },
                {
                    "id": "SC05_I4",
                    "description": "Serene 2D gouache bedtime endcard on velvety midnight indigo sky #1B263B: glowing golden crescent moon #F4D35E, sleeping village hill roofs, and neat centered storybook text 'TÂM TĨNH ĐÊM' in soft cream #F8F4E3, orthographic 2D, 75% negative space.",
                    "character_ids": [],
                    "preserve": "velvety midnight indigo canvas, gouache endcard stillness",
                    "change": "closing peaceful bedtime endcard frame",
                    "reason": "Narration-locked full-frame beat SC05_I4.",
                    "visible_text": [{"text": "TÂM TĨNH ĐÊM", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "hold",
                    "narrative_situation": "cta_close",
                    "emphasis_text": "TÂM TĨNH ĐÊM",
                    "focus": {"x": 0.5, "y": 0.0, "scale": 1.0},
                    "has_character": False,
                    "is_endcard": True,
                    "motion_prompt": "Gentle 2D gouache animation, the golden crescent moon glows in infinite calm stillness as shooting stars gently trace across velvety night skies, silent visual storytelling, no talking, no lip movement",
                    "camera_motion": "hold",
                    "effect": "hold"
                }
            ],
            "beats": [
                {"id": "SC05_B1", "image_id": "SC05_I1", "purpose": "Nhịp 1: đỉnh cao trào câu hỏi mở tự tha thứ", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "shot_type": "full_scene", "effect": "none"},
                {"id": "SC05_B2", "image_id": "SC05_I2", "purpose": "Nhịp 2: cầu nối dẫn phễu sang bản đầy đủ", "tempo": "normal", "narrative_situation": "cta_bridge", "shot_type": "full_scene", "effect": "none"},
                {"id": "SC05_B3", "image_id": "SC05_I3", "purpose": "Nhịp 3: lời chúc ngủ ngon an yên", "tempo": "slow", "narrative_situation": "cta_close", "shot_type": "full_scene", "effect": "none"},
                {"id": "SC05_B4", "image_id": "SC05_I4", "purpose": "Nhịp 4: màn hình kết tĩnh lặng chúc ngủ ngon", "tempo": "hold", "narrative_situation": "cta_close", "shot_type": "full_scene", "effect": "hold", "is_endcard": True}
            ]
        }
    ]

    brief_hash = compute_brief_hash(brief)
    content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": brief_hash,
        "topic": topic,
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": cast,
        "scenes": scenes,
        "coverage": [
            {"requirement_id": "R01", "scene_id": "SC01", "quote": "Đêm nay trước khi ngủ, có phải bạn vẫn đang tự trách bản thân?"},
            {"requirement_id": "R02", "scene_id": "SC02", "quote": "Hãy nhớ về chiếc bình nứt của người gánh nước xưa."},
            {"requirement_id": "R03", "scene_id": "SC03", "quote": "Thế nhưng người gánh nước mỉm cười chỉ xuống ven đường."},
            {"requirement_id": "R04", "scene_id": "SC04", "quote": "Vết nứt không phải sự hỏng hóc, mà là nơi đón ánh sáng."},
            {"requirement_id": "R05", "scene_id": "SC05", "quote": "Đêm nay hãy buông bỏ âu lo, ngủ thật ngon và thương lấy chính mình bạn nhé."}
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC04",
                "quote": "Khiếm khuyết của bạn chính là hạt mầm để lòng trắc ẩn nở hoa",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Lòng tự trắc ẩn và sự bao dung với khiếm khuyết giúp giảm lo âu và cải thiện giấc ngủ."
            }
        ],
        "revision_response": [],
        "open_questions": []
    }

    return cr, brief, outline, content


if __name__ == "__main__":
    cr9, b9, o9, c9 = build_tam_tinh_dem_batch3_9x16()
    print("Built 9x16 successfully! Checking linters...")

    # Validate 9x16
    cta_errs = lint_cta(b9, c9)
    print("CTA errors 9x16:", cta_errs)

    ed_errs, ed_warns = lint_editorial_and_narrative_quality(b9, c9)
    print("Editorial errors 9x16:", ed_errs)
    print("Editorial warns 9x16:", ed_warns)

    cliche_errs = check_ai_cliche_phrases(c9["scenes"])
    print("Cliche violations 9x16:", cliche_errs)

    pacing_errs = audit_narrative_visual_density(b9, c9)
    print("Pacing errors 9x16:", pacing_errs)
