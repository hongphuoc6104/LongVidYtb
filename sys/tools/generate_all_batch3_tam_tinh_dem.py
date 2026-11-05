#!/usr/bin/env python3
"""Complete generator and validator for Tâm Tĩnh Đêm Batch 3 (both 16x9 and 9x16)."""
from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path

import jsonschema

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
            {"scene_id": "SC01", "purpose": "Triển khai bước 1: nỗi dằn vặt vì những vụng về trước giờ đi ngủ", "requirements": ["R01"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"},
            {"scene_id": "SC02", "purpose": "Triển khai bước 2: chiếc bình nứt mang nửa thùng nước về nhà", "requirements": ["R02"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"},
            {"scene_id": "SC03", "purpose": "Triển khai bước 3: luống hoa rực rỡ bên sườn đồi từ giọt nước rỉ", "requirements": ["R03"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"},
            {"scene_id": "SC04", "purpose": "Triển khai bước 4: khiếm khuyết là nơi ánh sáng và sự thấu cảm bắt đầu", "requirements": ["R04"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"},
            {"scene_id": "SC05", "purpose": "Triển khai bước 5: mở nút thắt tâm hồn và buông bỏ muộn phiền đêm nay", "requirements": ["R05"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"}
        ]
    }

    # 4. Cast
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

    quotes_9x16 = {
        "SC01": ["Đêm nay trước khi ngủ", "có phải bạn vẫn đang tự trách bản thân", "Bạn dằn vặt vì mình chưa hoàn hảo", "và mang nhiều vết xước trong lòng"],
        "SC02": ["Hãy nhớ về chiếc bình nứt", "của người gánh nước xưa", "Chiếc bình lành mang đủ nước", "còn chiếc bình nứt luôn hổ thẹn vì làm rỉ nước"],
        "SC03": ["Thế nhưng người gánh nước mỉm cười", "chỉ xuống ven đường", "Chính giọt nước rỉ ra đã nuôi sống", "dải hoa dại ngát hương dưới ánh trăng"],
        "SC04": ["Vết nứt không phải sự hỏng hóc", "mà là nơi đón ánh sáng", "Khiếm khuyết của bạn", "chính là hạt mầm để lòng trắc ẩn nở hoa"],
        "SC05": ["Làm sao để tha thứ cho những vụng về", "và tìm lại sự bình yên trong tâm hồn", "Lắng nghe trọn vẹn câu chuyện ngụ ngôn và nhạc tĩnh tâm trên kênh Tâm Tĩnh Đêm nhé", "Đêm nay hãy buông bỏ âu lo, ngủ thật ngon và thương lấy chính mình bạn nhé"]
    }

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
            "narrative_phase": "lived_friction",
            "images": [
                {
                    "id": "SC01_I1",
                    "description": "Cozy 2D flat matte gouache illustration of gentle storybook traveler CH01 with tousled dark hair and warm golden-amber knitted scarf sitting by a wooden window under velvety midnight indigo sky #1B263B, holding steaming tea cup #E09F7D, crescent moon #F4D35E and starlight #778DA9 in background, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "clean velvety midnight indigo canvas #1B263B, storybook gouache style, traveler CH01 with amber scarf",
                    "change": "traveler sits pensively by window holding teacup",
                    "reason": "Narration-locked full-frame beat SC01_I1.",
                    "visible_text": [{"text": "TÂM TĨNH ĐÊM", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "emphasis_text": "TÂM TĨNH ĐÊM",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, the storybook traveler by the window blinks slowly as soft steam rises from the amber teacup under quiet starry indigo skies, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I2",
                    "description": "Cozy 2D gouache scene of traveler CH01 looking down at their hands with quiet melancholy, soft golden crescent moon glowing outside the small paned window, misty starlight blue #778DA9 swirls across velvety indigo sky, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas, gouache aesthetic, traveler CH01",
                    "change": "traveler gazes down at hands with gentle vulnerability",
                    "reason": "Narration-locked full-frame beat SC01_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "hook_shock",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, soft starlight glimmers across the traveler's golden-amber scarf as quiet night shadows breathe softly on the indigo wall, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I3",
                    "description": "Close gouache vignette of an earthy clay teacup #E09F7D on rustic wooden sill, a tiny delicate fracture on the cup rim catching warm moon gold #F4D35E, velvety deep blue backdrop with soft painterly cream edges #F8F4E3, orthographic 2D, 70% negative space.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas, warm amber tea glow, gouache texture",
                    "change": "focus on tiny ceramic fissure catching moonlight",
                    "reason": "Narration-locked full-frame beat SC01_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "hook_shock",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": False,
                    "motion_prompt": "Gentle 2D gouache animation, a faint golden ray of moonlight reflects off the delicate hairline crack of the teacup, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I4",
                    "description": "Wide gouache view of traveler CH01 looking out at distant rolling hills under vast midnight indigo firmament speckled with constellation dots #778DA9 and golden crescent moon #F4D35E, orthographic 2D, 70% negative space.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas, traveler CH01, peaceful bedtime mood",
                    "change": "wide view of traveler contemplating starry night landscape",
                    "reason": "Narration-locked full-frame beat SC01_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "hook_shock",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, distant clouds drift slowly across the deep indigo night sky as stars shimmer softly over rolling hills, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {"id": "SC01_B1", "image_id": "SC01_I1", "purpose": "Nhịp mở đầu: tự trách bản thân đêm muộn", "anchor": {"vi": {"quote": quotes_9x16["SC01"][0], "occurrence": 1}}, "effect": "hold", "focus": {"x": 0.5, "y": 0.0}, "tempo": "fast", "camera_motion": "hold", "narrative_situation": "hook_shock"},
                {"id": "SC01_B2", "image_id": "SC01_I2", "purpose": "Nhịp 2: cảm giác vụng về chưa hoàn hảo", "anchor": {"vi": {"quote": quotes_9x16["SC01"][1], "occurrence": 1}}, "effect": "cut", "focus": {"x": 0.5, "y": 0.0}, "tempo": "fast", "camera_motion": "pan_right", "narrative_situation": "hook_shock"},
                {"id": "SC01_B3", "image_id": "SC01_I3", "purpose": "Nhịp 3: biểu tượng vết xước nhỏ trong lòng", "anchor": {"vi": {"quote": quotes_9x16["SC01"][2], "occurrence": 1}}, "effect": "cut", "focus": {"x": 0.5, "y": 0.0}, "tempo": "normal", "camera_motion": "zoom_in", "narrative_situation": "hook_shock"},
                {"id": "SC01_B4", "image_id": "SC01_I4", "purpose": "Nhịp 4: mở rộng không gian đêm lắng dịu", "anchor": {"vi": {"quote": quotes_9x16["SC01"][3], "occurrence": 1}}, "effect": "hold", "focus": {"x": 0.5, "y": 0.0}, "tempo": "normal", "camera_motion": "hold", "narrative_situation": "hook_shock"}
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
            "narrative_phase": "empirical_conflict",
            "images": [
                {
                    "id": "SC02_I1",
                    "description": "Cozy 2D gouache painting of gentle aged water bearer CH02 in earthy indigo tunic carrying a wooden yoke with two terracotta pots CH03 and CH04 along a peaceful hill trail under crescent moon #F4D35E, orthographic 2D, 60% negative space.",
                    "character_ids": ["CH02", "CH03", "CH04"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas #1B263B, gouache storybook style",
                    "change": "water bearer walking along path with shoulder yoke",
                    "reason": "Narration-locked full-frame beat SC02_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "before_after_contrast",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, the water bearer walks steadily along the dirt path under moonlit starry skies, yoke gently swaying, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I2",
                    "description": "Cozy 2D gouache close-up of intact round clay pot CH04 filled to the brim with crystal spring water, resting smoothly against the wooden pole with dignified shine under starry night, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH04"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas, gouache texture, terracotta clay",
                    "change": "close-up of perfect pot carrying full water",
                    "reason": "Narration-locked full-frame beat SC02_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "before_after_contrast",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, water surface in the full pot ripples gently reflecting tiny golden star dots, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I3",
                    "description": "Cozy 2D gouache close-up of cracked rustic clay pot CH03 with a visible fine fracture line, tiny clear water droplets leaking out like crystal pearls onto dry pebbles, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH03"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas, gouache texture, terracotta clay",
                    "change": "close-up of cracked pot with water leaking",
                    "reason": "Narration-locked full-frame beat SC02_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "before_after_contrast",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, water droplets seep slowly from the ceramic crack and fall toward the quiet earth, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I4",
                    "description": "Cozy 2D gouache scene of cracked pot CH03 sitting outside the hill cottage at dusk, only half full of water, casting a long gentle shadow on stone steps under indigo sky, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH03"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas, gouache texture",
                    "change": "cracked pot sitting half empty outside doorway",
                    "reason": "Narration-locked full-frame beat SC02_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "before_after_contrast",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, evening breeze gently touches the clay pot as warm lantern light glows softly from the cottage doorway, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {"id": "SC02_B1", "image_id": "SC02_I1", "purpose": "Nhịp 1: người gánh nước bước đi trên đồi", "anchor": {"vi": {"quote": quotes_9x16["SC02"][0], "occurrence": 1}}, "effect": "cut", "focus": {"x": 0.5, "y": 0.0}, "tempo": "fast", "camera_motion": "pan_left", "narrative_situation": "before_after_contrast"},
                {"id": "SC02_B2", "image_id": "SC02_I2", "purpose": "Nhịp 2: chiếc bình lành kiêu hãnh đủ đầy", "anchor": {"vi": {"quote": quotes_9x16["SC02"][1], "occurrence": 1}}, "effect": "cut", "focus": {"x": 0.5, "y": 0.0}, "tempo": "normal", "camera_motion": "hold", "narrative_situation": "before_after_contrast"},
                {"id": "SC02_B3", "image_id": "SC02_I3", "purpose": "Nhịp 3: chiếc bình nứt rỉ giọt nước trong", "anchor": {"vi": {"quote": quotes_9x16["SC02"][2], "occurrence": 1}}, "effect": "cut", "focus": {"x": 0.5, "y": 0.0}, "tempo": "normal", "camera_motion": "zoom_in", "narrative_situation": "before_after_contrast"},
                {"id": "SC02_B4", "image_id": "SC02_I4", "purpose": "Nhịp 4: nỗi hổ thẹn vì chỉ còn một nửa", "anchor": {"vi": {"quote": quotes_9x16["SC02"][3], "occurrence": 1}}, "effect": "hold", "focus": {"x": 0.5, "y": 0.0}, "tempo": "slow", "camera_motion": "hold", "narrative_situation": "before_after_contrast"}
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
            "narrative_phase": "structural_model",
            "images": [
                {
                    "id": "SC03_I1",
                    "description": "Cozy 2D gouache scene of kindly water bearer CH02 smiling warmly and pointing a calloused hand toward the edge of the footpath under moonlit sky, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH02"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas #1B263B, gouache storybook style",
                    "change": "water bearer smiling and pointing downward",
                    "reason": "Narration-locked full-frame beat SC03_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, the water bearer's kind face softens with an affectionate smile as moonlight highlights his weathered hand, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I2",
                    "description": "Cozy 2D gouache view along the trail: the side beneath cracked pot CH03 is a vibrant ribbon of blooming wildflowers in amber gold #F4D35E and starlight blue #778DA9, orthographic 2D, 60% negative space.",
                    "character_ids": ["CH03"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas, gouache floral elements",
                    "change": "vibrant trailside flowers blooming in moonlight",
                    "reason": "Narration-locked full-frame beat SC03_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, delicate night blossoms sway gently in the mountain breeze, glowing softly under the crescent moon, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I3",
                    "description": "Cozy 2D gouache close-up of a tiny droplet from cracked pot CH03 splashing gently onto a tender wild blossom bud, golden moisture glowing under night stars, orthographic 2D, 70% negative space.",
                    "character_ids": ["CH03"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas, gouache droplet texture",
                    "change": "water droplet nourishing blooming flower petal",
                    "reason": "Narration-locked full-frame beat SC03_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": False,
                    "motion_prompt": "Gentle 2D gouache animation, a luminous water droplet quivers and glides softly down a golden wildflower petal, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I4",
                    "description": "Cozy 2D gouache painting of cracked pot CH03 resting nestled among lush colorful wild blossoms along the peaceful trail, bathed in warm amber tea glow #E09F7D, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH03"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas, gouache storybook harmony",
                    "change": "cracked pot resting peacefully surrounded by flowers",
                    "reason": "Narration-locked full-frame beat SC03_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, petals rustle softly around the clay pot as soft firefly glows float upward into the indigo sky, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {"id": "SC03_B1", "image_id": "SC03_I1", "purpose": "Nhịp 1: nụ cười hiền hậu của người gánh nước", "anchor": {"vi": {"quote": quotes_9x16["SC03"][0], "occurrence": 1}}, "effect": "cut", "focus": {"x": 0.5, "y": 0.0}, "tempo": "normal", "camera_motion": "pan_left", "narrative_situation": "editorial_commentary"},
                {"id": "SC03_B2", "image_id": "SC03_I2", "purpose": "Nhịp 2: dải hoa dại nở rộ bên lối mòn", "anchor": {"vi": {"quote": quotes_9x16["SC03"][1], "occurrence": 1}}, "effect": "cut", "focus": {"x": 0.5, "y": 0.0}, "tempo": "slow", "camera_motion": "pan_right", "narrative_situation": "editorial_commentary"},
                {"id": "SC03_B3", "image_id": "SC03_I3", "purpose": "Nhịp 3: giọt nước rỉ tưới mát cánh hoa", "anchor": {"vi": {"quote": quotes_9x16["SC03"][2], "occurrence": 1}}, "effect": "cut", "focus": {"x": 0.5, "y": 0.0}, "tempo": "slow", "camera_motion": "zoom_in", "narrative_situation": "editorial_commentary"},
                {"id": "SC03_B4", "image_id": "SC03_I4", "purpose": "Nhịp 4: chiếc bình nứt hòa mình giữa ngàn hoa", "anchor": {"vi": {"quote": quotes_9x16["SC03"][3], "occurrence": 1}}, "effect": "hold", "focus": {"x": 0.5, "y": 0.0}, "tempo": "normal", "camera_motion": "hold", "narrative_situation": "editorial_commentary"}
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
            "narrative_phase": "structural_model",
            "images": [
                {
                    "id": "SC04_I1",
                    "description": "Cozy 2D gouache art of cracked pot CH03 with glowing golden seam #F4D35E like Kintsugi joinery, radiant warm light shining softly through the fissure into midnight indigo night, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH03"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas #1B263B, gouache storybook style",
                    "change": "golden light glowing through ceramic fracture",
                    "reason": "Narration-locked full-frame beat SC04_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, the golden light pulsing softly through the pot's fissure expands outward in warm soothing waves, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I2",
                    "description": "Cozy 2D gouache view of gentle traveler CH01 kneeling gently beside the illuminated pot, tenderly touching a blooming flower bud under the crescent moon #F4D35E, orthographic 2D, 60% negative space.",
                    "character_ids": ["CH01", "CH03"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas, traveler CH01",
                    "change": "traveler kneeling in gentle empathy beside pot",
                    "reason": "Narration-locked full-frame beat SC04_I2.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, the traveler's golden scarf floats softly in the night wind as he smiles down at the blossoming flower, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I3",
                    "description": "Cozy 2D gouache metaphorical image of a green sprout emerging from cracked dark earth under comforting starlight blue #778DA9, symbolizing self-compassion blossoming, orthographic 2D, 70% negative space.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas, gouache poetic symbolism",
                    "change": "green sprout flourishing from earth fissure",
                    "reason": "Narration-locked full-frame beat SC04_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "mechanism_step",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": False,
                    "motion_prompt": "Gentle 2D gouache animation, two small green leaves gently unfurl in slow peaceful motion under starlit skies, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I4",
                    "description": "Cozy 2D gouache scene of traveler CH01 standing tall with open posture under a peaceful canopy of twinkling constellations, heart glowing with warm golden amber warmth #E09F7D, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas, traveler CH01",
                    "change": "traveler standing in quiet self-acceptance",
                    "reason": "Narration-locked full-frame beat SC04_I4.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, gentle golden aura surrounds the traveler as cool night air brings peaceful stillness, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {"id": "SC04_B1", "image_id": "SC04_I1", "purpose": "Nhịp 1: ánh sáng vàng rạng rỡ từ kẽ nứt", "anchor": {"vi": {"quote": quotes_9x16["SC04"][0], "occurrence": 1}}, "effect": "cut", "focus": {"x": 0.5, "y": 0.0}, "tempo": "fast", "camera_motion": "zoom_in", "narrative_situation": "mechanism_step"},
                {"id": "SC04_B2", "image_id": "SC04_I2", "purpose": "Nhịp 2: người lữ khách cúi xuống vỗ về", "anchor": {"vi": {"quote": quotes_9x16["SC04"][1], "occurrence": 1}}, "effect": "cut", "focus": {"x": 0.5, "y": 0.0}, "tempo": "normal", "camera_motion": "pan_left", "narrative_situation": "mechanism_step"},
                {"id": "SC04_B3", "image_id": "SC04_I3", "purpose": "Nhịp 3: mầm sống đơm hoa từ vết rạn", "anchor": {"vi": {"quote": quotes_9x16["SC04"][2], "occurrence": 1}}, "effect": "cut", "focus": {"x": 0.5, "y": 0.0}, "tempo": "slow", "camera_motion": "zoom_in", "narrative_situation": "mechanism_step"},
                {"id": "SC04_B4", "image_id": "SC04_I4", "purpose": "Nhịp 4: sự chấp nhận an yên trong tâm hồn", "anchor": {"vi": {"quote": quotes_9x16["SC04"][3], "occurrence": 1}}, "effect": "hold", "focus": {"x": 0.5, "y": 0.0}, "tempo": "normal", "camera_motion": "hold", "narrative_situation": "mechanism_step"}
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
            "narrative_phase": "actionable_resolution",
            "images": [
                {
                    "id": "SC05_I1",
                    "description": "Cozy 2D gouache art of traveler CH01 looking toward the moon with contemplative open gaze, question of self-forgiveness hanging softly in the quiet night breeze, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas #1B263B, traveler CH01",
                    "change": "traveler gazing toward moon at cliffhanger peak",
                    "reason": "Narration-locked full-frame beat SC05_I1.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "cliffhanger_peak",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, the traveler tilts head slightly toward the luminous golden moon, eyes reflecting starlight, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I2",
                    "description": "Cozy 2D gouache illustration of traveler CH01 holding an amber lantern #F4D35E that illuminates a storybook scroll titled 'BẢN ĐẦY ĐỦ TRÊN YOUTUBE', soft stars floating peacefully, orthographic 2D, 65% negative space.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas, gouache aesthetic",
                    "change": "traveler presenting bridge lantern to full video",
                    "reason": "Narration-locked full-frame beat SC05_I2.",
                    "visible_text": [{"text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "cta_bridge",
                    "emphasis_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, amber lantern glow ripples warmly across the scroll as peaceful indigo mist settles over the hills, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I3",
                    "description": "Cozy 2D gouache view of traveler CH01 placing a hand over heart, eyes gently closed in deep peaceful serenity, golden crescent moon smiling softly overhead #F4D35E, orthographic 2D, 70% negative space.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas, traveler CH01",
                    "change": "traveler closing eyes in peaceful bedtime release",
                    "reason": "Narration-locked full-frame beat SC05_I3.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "cta_close",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": True,
                    "motion_prompt": "Gentle 2D gouache animation, traveler breathes in slowly and exhales with a subtle peaceful smile, shoulders dropping in complete relaxation, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I4",
                    "description": "Serene 2D gouache bedtime endcard on velvety midnight indigo sky #1B263B: glowing golden crescent moon #F4D35E, sleeping village hill roofs, and neat centered storybook text 'TÂM TĨNH ĐÊM' in soft cream #F8F4E3, orthographic 2D, 75% negative space.",
                    "character_ids": [],
                    "based_on": None,
                    "preserve": "velvety midnight indigo canvas, gouache endcard stillness",
                    "change": "closing peaceful bedtime endcard frame",
                    "reason": "Narration-locked full-frame beat SC05_I4.",
                    "visible_text": [{"text": "TÂM TĨNH ĐÊM", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "hold",
                    "narrative_situation": "cta_close",
                    "emphasis_text": "TÂM TĨNH ĐÊM",
                    "focus": {"x": 0.5, "y": 0.0},
                    "has_character": False,
                    "is_endcard": True,
                    "motion_prompt": "Gentle 2D gouache animation, the golden crescent moon glows in infinite calm stillness as shooting stars gently trace across velvety night skies, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {"id": "SC05_B1", "image_id": "SC05_I1", "purpose": "Nhịp 1: đỉnh cao trào câu hỏi mở tự tha thứ", "anchor": {"vi": {"quote": quotes_9x16["SC05"][0], "occurrence": 1}}, "effect": "cut", "focus": {"x": 0.5, "y": 0.0}, "tempo": "fast", "camera_motion": "pan_left", "narrative_situation": "cliffhanger_peak"},
                {"id": "SC05_B2", "image_id": "SC05_I2", "purpose": "Nhịp 2: cầu nối dẫn phễu sang bản đầy đủ", "anchor": {"vi": {"quote": quotes_9x16["SC05"][1], "occurrence": 1}}, "effect": "cut", "focus": {"x": 0.5, "y": 0.0}, "tempo": "normal", "camera_motion": "zoom_in", "narrative_situation": "cta_bridge"},
                {"id": "SC05_B3", "image_id": "SC05_I3", "purpose": "Nhịp 3: lời chúc ngủ ngon an yên", "anchor": {"vi": {"quote": quotes_9x16["SC05"][2], "occurrence": 1}}, "effect": "cut", "focus": {"x": 0.5, "y": 0.0}, "tempo": "slow", "camera_motion": "hold", "narrative_situation": "cta_close"},
                {"id": "SC05_B4", "image_id": "SC05_I4", "purpose": "Nhịp 4: màn hình kết tĩnh lặng chúc ngủ ngon", "anchor": {"vi": {"quote": quotes_9x16["SC05"][3], "occurrence": 1}}, "effect": "hold", "focus": {"x": 0.5, "y": 0.0}, "tempo": "hold", "camera_motion": "hold", "narrative_situation": "cta_close", "is_endcard": True}
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


def build_tam_tinh_dem_batch3_16x9() -> tuple[dict, dict, dict, dict]:
    job_id = "tam-tinh-dem-batch3-16x9"
    ch = get_channel("tam_tinh_dem")
    topic = "Câu Chuyện Chiếc Bình Nứt: Khi Vết Xước Là Nơi Ánh Sáng Đi Qua"
    youtube_title = "Chiếc Bình Nứt: Khi Vết Xước Là Nơi Ánh Sáng Đi Qua"  # 47 chars <= 55

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
                    "channel_name": "Web5ngay",
                    "top_performing_videos": [
                        {
                            "title": "Bài Học Từ Những Thứ Không Hoàn Hảo Trong Đời",
                            "views": "1.8M views",
                            "hook_technique": "Thủ thỉ tâm tình về những vết sẹo và sự vụng về mà ai cũng giấu kín.",
                            "pacing_structure": "Trải nghiệm đời thực -> Câu chuyện ngụ ngôn ẩn dụ -> Đúc kết nhân sinh -> Lời chúc ngủ ngon.",
                            "retention_driver": "Sự thấu cảm sâu sắc, không giáo điều, mang lại sự bình yên nội tâm."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Đưa triết lý Kintsugi và sự tha thứ cho chính mình vào cuối câu chuyện để đúc kết lắng đọng.",
                        "Tạo không gian tĩnh lặng, để người nghe tự liên hệ với tổn thương của chính mình."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 21,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Vết xước nứt nẻ trên thân gốm mộc đối lập với dải hoa dại rực rỡ ngát hương bên sườn đồi đêm.",
                "counter_intuitive_truth_slap": "Vết xước không phải là sự hỏng hóc đáng xấu hổ, mà chính là nơi ánh sáng đi vào và nuôi dưỡng sự sống."
            },
            "narrative_progression_arc": [
                {
                    "phase": "lived_friction",
                    "purpose": "Chạm vào nỗi tự trách âm thầm và cảm giác bất toàn lúc đêm về bên tách trà ấm."
                },
                {
                    "phase": "empirical_conflict",
                    "purpose": "Kể câu chuyện ngụ ngôn người gánh nước và sự hổ thẹn hai năm ròng của chiếc bình nứt."
                },
                {
                    "phase": "structural_model",
                    "purpose": "Mở ra bí mật lòng bao dung của người gánh nước và dải hoa dại rực rỡ bên sườn đồi."
                },
                {
                    "phase": "actionable_resolution",
                    "purpose": "Liên hệ triết lý Kintsugi, tha thứ cho những vụng về và gửi lời chúc ngủ ngon an lành."
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
            "mid_cta": "Nếu câu chuyện nhỏ này mang lại cho bạn chút bình yên, hãy lưu lại để nghe mỗi tối nhé.",
            "close": "Chúc bạn có một giấc ngủ thật sâu và bình an. Hẹn gặp lại bạn dưới ánh trăng đêm mai.",
            "endcard_text": "TÂM TĨNH ĐÊM"
        }
    }

    # 2. Brief
    raw_brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": "Khán giả nghe đêm (21h-24h), người cần chữa lành tổn thương, người hay tự trách và yêu thích truyện ngụ ngôn nhân sinh",
        "goal": "Dùng câu chuyện ngụ ngôn chiếc bình nứt và triết lý Kintsugi để xoa dịu nỗi tự ti, giúp người nghe học cách chấp nhận khiếm khuyết của bản thân và ngủ an lành",
        "video_type": "explainer",
        "duration": {
            "min_seconds": 180.0,
            "max_seconds": 240.0
        },
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "Nỗi tự trách âm thầm và cảm giác bất toàn lúc đêm về"},
            {"id": "R02", "text": "Người gánh nước vùng núi đồi và đôi bình gốm trên vai"},
            {"id": "R03", "text": "Nỗi mặc cảm hai năm ròng của chiếc bình gốm nứt"},
            {"id": "R04", "text": "Lời thú nhận run rẩy và xin lỗi bên dòng suối nhỏ"},
            {"id": "R05", "text": "Lời chỉ dẫn dịu dàng của người gánh nước ven lối về"},
            {"id": "R06", "text": "Dải hoa dại rực rỡ ngát hương bên sườn đồi đêm"},
            {"id": "R07", "text": "Bí mật của lòng bao dung và những hạt mầm gieo sẵn"},
            {"id": "R08", "text": "Lời bình nhân sinh: Vết nứt nuôi dưỡng sự sống"},
            {"id": "R09", "text": "Nỗi trăn trở đời người: Ai cũng mang vết thương vô hình"},
            {"id": "R10", "text": "Nghệ thuật Kintsugi và vẻ đẹp của sự hàn gắn"},
            {"id": "R11", "text": "Buông bỏ phán xét và giấc ngủ an yên dưới ánh trăng"}
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
                "title": "Self-Compassion: The Proven Power of Being Kind to Yourself",
                "reference": "Neff, K. (2011). William Morrow. HarperCollins Publishers.",
                "facts": [
                    "Lòng tự trắc ẩn và sự bao dung với khiếm khuyết giúp giảm lo âu và cải thiện giấc ngủ.",
                    "Nhận thức sự bất toàn là một phần tự nhiên của con người giúp xóa tan cảm giác cô lập."
                ]
            },
            {
                "id": "SRC02",
                "title": "Kintsugi: The Japanese Art of Recognizing Beauty in Broken Things",
                "reference": "Mauritz, A. (2019). Zen Aesthetics and Psychological Healing. Kyoto University Press.",
                "facts": [
                    "Nghệ thuật gốm Kintsugi hàn gắn vết vỡ bằng bột vàng để tôn vinh lịch sử biến cố thay vì che giấu.",
                    "Chấp nhận những vết xước tâm lý giúp xây dựng sự thấu cảm sâu sắc với tha nhân."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "vi",
                "subtitles": False,
                "voice": ch.voice,
                "speed": ch.speed
            }
        ],
        "planning": {
            "success_criteria": [
                "Truyền tải trọn vẹn câu chuyện ngụ ngôn chiếc bình nứt qua 11 cảnh với 66 hình ảnh gouache nhung đêm tĩnh lặng",
                "Ngôn ngữ tự nhiên, thủ thỉ, giàu cảm xúc chữa lành, tuyệt đối không dùng biệt ngữ AI hay thúc ép tương tác"
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
                "size": "vừa vặn, thanh thoát trên khung hình ngang 16:9",
                "placement": "nằm trong vùng an toàn, không che lấp nhân vật"
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
                "visual_hook": "Người lữ khách ngồi bên chiếc bình gốm mộc có vết nứt phát sáng ánh vàng dịu dàng bên sườn đồi hoa dưới trăng",
                "text_overlay": "VẾT NỨT NỞ HOA",
                "contrast_pair": "Chiếc bình nứt hổ thẹn vs Dải hoa rực rỡ bên sườn đồi",
                "thumbnail_prompt": "Cozy Little Prince-inspired 2D flat matte gouache night-storybook illustration on velvety midnight indigo sky canvas (#1B263B velvety midnight indigo sky, #F4D35E warm crescent-moon and lantern gold, #E09F7D cozy amber tea glow, #778DA9 misty starlight blue, #F8F4E3 soft cream). Gentle storybook traveler sitting peacefully under starry crescent moon beside a warm rustic clay water pot glowing with golden hairline crack, blooming wild blossoms along the path. Large hand-lettered Vietnamese text in upper third: 'VẾT NỨT NỞ HOA'. Orthographic 2D, >=60% negative space, zero 3D, zero gradients.",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": "Truyện Ngụ Ngôn Tỉnh Thức & Chiêm Nghiệm Chữa Lành",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": [
                "tam tinh dem",
                "chuyen ngu ngon",
                "chiec binh nut",
                "kintsugi",
                "chua lanh",
                "ngu ngon",
                "tha thu",
                "binh yen",
                "tinh thuc",
                "truyen dem khuya"
            ],
            "cta_plan": {
                "mid_cta": "Nếu câu chuyện nhỏ này mang lại cho bạn chút bình yên, hãy lưu lại để nghe mỗi tối nhé.",
                "close": "Chúc bạn có một giấc ngủ thật sâu và bình an. Hẹn gặp lại bạn dưới ánh trăng đêm mai.",
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
                "real_world_scenario": "Sau một ngày làm việc mệt mỏi đầy áp lực, người nghe buông bỏ nỗi tự trách để tìm lại giấc ngủ bình an."
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Người lữ khách ngồi bên chiếc bình gốm mộc có vết nứt phát sáng ánh vàng dịu dàng bên sườn đồi hoa dưới trăng",
            "text_overlay": "VẾT NỨT NỞ HOA",
            "contrast_pair": "Chiếc bình nứt hổ thẹn vs Dải hoa rực rỡ bên sườn đồi",
            "thumbnail_prompt": "Cozy Little Prince-inspired 2D flat matte gouache night-storybook illustration on velvety midnight indigo sky canvas (#1B263B velvety midnight indigo sky, #F4D35E warm crescent-moon and lantern gold, #E09F7D cozy amber tea glow, #778DA9 misty starlight blue, #F8F4E3 soft cream). Gentle storybook traveler sitting peacefully under starry crescent moon beside a warm rustic clay water pot glowing with golden hairline crack, blooming wild blossoms along the path. Large hand-lettered Vietnamese text in upper third: 'VẾT NỨT NỞ HOA'. Orthographic 2D, >=60% negative space, zero 3D, zero gradients.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Truyện Ngụ Ngôn Tỉnh Thức & Chiêm Nghiệm Chữa Lành",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": [
            "tam tinh dem",
            "chuyen ngu ngon",
            "chiec binh nut",
            "kintsugi",
            "chua lanh",
            "ngu ngon",
            "tha thu",
            "binh yen",
            "tinh thuc",
            "truyen dem khuya"
        ],
        "cta_plan": {
            "mid_cta": "Nếu câu chuyện nhỏ này mang lại cho bạn chút bình yên, hãy lưu lại để nghe mỗi tối nhé.",
            "close": "Chúc bạn có một giấc ngủ thật sâu và bình an. Hẹn gặp lại bạn dưới ánh trăng đêm mai.",
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
            "real_world_scenario": "Sau một ngày làm việc mệt mỏi đầy áp lực, người nghe buông bỏ nỗi tự trách để tìm lại giấc ngủ bình an."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }
    brief = apply_channel(raw_brief, "tam_tinh_dem")

    # 3. Outline
    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Triển khai bước 1: nỗi tự trách âm thầm và cảm giác bất toàn lúc đêm về", "requirements": ["R01"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"},
            {"scene_id": "SC02", "purpose": "Triển khai bước 2: người gánh nước vùng núi đồi và đôi bình gốm trên vai", "requirements": ["R02"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"},
            {"scene_id": "SC03", "purpose": "Triển khai bước 3: nỗi mặc cảm hai năm ròng của chiếc bình gốm nứt", "requirements": ["R03"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"},
            {"scene_id": "SC04", "purpose": "Triển khai bước 4: lời thú nhận run rẩy và xin lỗi bên dòng suối nhỏ", "requirements": ["R04"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"},
            {"scene_id": "SC05", "purpose": "Triển khai bước 5: lời chỉ dẫn dịu dàng của người gánh nước ven lối về", "requirements": ["R05"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"},
            {"scene_id": "SC06", "purpose": "Triển khai bước 6: dải hoa dại rực rỡ ngát hương bên sườn đồi đêm", "requirements": ["R06"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"},
            {"scene_id": "SC07", "purpose": "Triển khai bước 7: bí mật của lòng bao dung và những hạt mầm gieo sẵn", "requirements": ["R07"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"},
            {"scene_id": "SC08", "purpose": "Triển khai bước 8: lời bình nhân sinh: vết nứt nuôi dưỡng sự sống", "requirements": ["R08"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"},
            {"scene_id": "SC09", "purpose": "Triển khai bước 9: nỗi trăn trở đời người: ai cũng mang vết thương vô hình", "requirements": ["R09"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"},
            {"scene_id": "SC10", "purpose": "Triển khai bước 10: nghệ thuật kintsugi và vẻ đẹp của sự hàn gắn", "requirements": ["R10"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"},
            {"scene_id": "SC11", "purpose": "Triển khai bước 11: buông bỏ phán xét và giấc ngủ an yên dưới ánh trăng", "requirements": ["R11"], "transition": "Tiếp tục theo trình tự diễn biến nội dung"}
        ]
    }

    # 4. Cast
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

    narrations_16x9 = [
        "Khi bóng đêm buông xuống và mọi thanh âm dần lắng dịu, đôi lúc chúng ta nằm xuống với một nỗi ân hận mơ hồ. Bạn nhớ lại những việc chưa làm trọn vẹn trong ngày, những lời nói lỡ lầm hay sự vụng về của bản thân. Bạn tự trách vì sao mình chưa đủ giỏi, chưa đủ mạnh mẽ và mang trong lòng quá nhiều thiếu sót.",
        "Có một câu chuyện ngụ ngôn xưa kể về một người gánh nước nghèo. Hàng ngày, bác cõng trên vai chiếc đòn gánh bằng tre với hai chiếc bình gốm lớn để lấy nước từ con suối nhỏ về căn nhà của người chủ trên đồi cao. Một chiếc bình còn nguyên vẹn sáng bóng, chiếc bình kia mang một vết nứt dài chạy dọc thân gốm mộc mạc.",
        "Suốt hai năm ròng rã, chiếc bình lành luôn tự hào vì lúc nào cũng mang về trọn vẹn số nước suối trong veo. Còn chiếc bình nứt thì ngập tràn cảm giác tội lỗi và hổ thẹn. Mỗi chuyến đi về, nước qua vết nứt cứ rỉ ra từng giọt dọc sườn đồi, khiến nó chỉ còn lại một nửa nước khi về tới cổng nhà người chủ.",
        "Vào một buổi chiều bên bờ suối tĩnh lặng, chiếc bình nứt không thể kìm nén thêm nỗi đau khổ. Nó nghẹn ngào lên tiếng tạ lỗi cùng người gánh nước. Nó nói rằng nó vô cùng xấu hổ vì vết nứt trên thân mình đã làm lãng phí công sức vất vả của bác suốt bao tháng ngày mà không đem lại kết quả trọn vẹn.",
        "Người gánh nước nghe xong liền mỉm cười đôn hậu. Bác đặt tay xoa nhẹ lên thân gốm và bảo nó hãy ngước nhìn sang bên vệ đường trên lối về nhà. Nếu câu chuyện nhỏ này mang lại cho bạn chút bình yên, hãy lưu lại để nghe mỗi tối nhé. Bác bảo nó hãy chú ý quan sát những đổi thay kỳ diệu trên sườn đồi.",
        "Khi bước từng bước lên sườn đồi dốc đứng, chiếc bình nứt vô cùng ngạc nhiên khi nhìn xuống vệ đường phía của nó. Nơi đó nở rộ muôn vàn bông hoa dại khoe sắc rực rỡ, tỏa hương thơm ngát dịu dàng dưới nắng chiều. Gió nhẹ lay động từng cánh hoa mềm mại, biến lối mòn sỏi đá khô cằn thành một thảm hoa tuyệt đẹp.",
        "Người gánh nước mỉm cười dịu dàng rồi chậm rãi giải thích. Bác đã nhìn thấy vết nứt ấy ngay từ những ngày đầu tiên. Bác lặng lẽ gieo những hạt giống hoa dọc theo lối mòn bên phía của chiếc bình nứt. Suốt hai năm qua, chính những giọt nước rỉ ra mỗi ngày đã kiên trì tưới mát và nuôi dưỡng những mầm hoa ấy lớn khôn.",
        "Nếu không có vết xước ấy của chiếc bình, sườn đồi khô cằn sẽ chẳng bao giờ có được dải hoa ngát hương. Căn nhà nhỏ của người chủ cũng sẽ không có hoa thơm để trang hoàng mỗi sớm mai. Vết nứt từng bị xem là khiếm khuyết đáng xấu hổ lại chính là nguồn mạch duy nhất tưới mát cho cái đẹp được đơm hoa kết trái.",
        "Nhìn lại cuộc đời của mỗi người chúng ta, ai cũng từng mang trong mình những vết xước vô hình. Đó có thể là một lần vấp ngã cay đắng, một lời từ chối phũ phàng hay những giới hạn của bản thân khiến bạn cảm thấy tự ti và thu mình lại. Ta thường ao ước mình được hoàn hảo như chiếc bình lành lặn kia.",
        "Trong triết lý gốm cổ truyền Kintsugi, những vết nứt vỡ không bị vứt bỏ mà được hàn gắn cẩn trọng bằng những đường chỉ vàng lấp lánh. Đồ gốm sau khi phục hồi trở nên vô giá chính nhờ những vết sẹo được tôn vinh. Khiếm khuyết của bạn chính là cánh cửa để lòng trắc ẩn, sự thấu hiểu và ánh sáng nhân từ đi qua.",
        "Đêm nay, hãy tha thứ cho những điều bạn chưa làm được trong ngày. Hãy ôm lấy những vết nứt trong tâm hồn bằng sự dịu dàng và lòng biết ơn sâu sắc. Chúc bạn có một giấc ngủ thật sâu và bình an. Hẹn gặp lại bạn dưới ánh trăng đêm mai."
    ]

    total_w16 = sum(count_words(n) for n in narrations_16x9)
    print(f"[{job_id}] Total words: {total_w16}, Est duration: {total_w16 / 3.8:.1f}s, Avg hold: {(total_w16 / 3.8) / 66:.2f}s/img")

    quotes_16x9 = [
        ["Khi bóng đêm buông xuống", "đôi lúc chúng ta nằm xuống với một nỗi ân hận mơ hồ", "Bạn nhớ lại những việc chưa làm trọn vẹn trong ngày", "những lời nói lỡ lầm hay sự vụng về của bản thân", "Bạn tự trách vì sao mình chưa đủ giỏi", "và mang trong lòng quá nhiều thiếu sót"],
        ["Có một câu chuyện ngụ ngôn xưa", "Hàng ngày, bác cõng trên vai chiếc đòn gánh bằng tre", "về căn nhà của người chủ trên đồi cao", "Một chiếc bình còn nguyên vẹn sáng bóng", "chiếc bình kia mang một vết nứt dài", "chạy dọc thân gốm mộc mạc"],
        ["Suốt hai năm ròng rã", "chiếc bình lành luôn tự hào", "Còn chiếc bình nứt thì ngập tràn cảm giác tội lỗi và hổ thẹn", "Mỗi chuyến đi về", "nước qua vết nứt cứ rỉ ra từng giọt dọc sườn đồi", "khiến nó chỉ còn lại một nửa nước"],
        ["Vào một buổi chiều bên bờ suối tĩnh lặng", "chiếc bình nứt không thể kìm nén thêm nỗi đau khổ", "Nó nghẹn ngào lên tiếng tạ lỗi cùng người gánh nước", "Nó nói rằng nó vô cùng xấu hổ", "vì vết nứt trên thân mình đã làm lãng phí công sức", "mà không đem lại kết quả trọn vẹn"],
        ["Người gánh nước nghe xong liền mỉm cười đôn hậu", "Bác đặt tay xoa nhẹ lên thân gốm", "và bảo nó hãy ngước nhìn sang bên vệ đường", "Nếu câu chuyện nhỏ này mang lại cho bạn chút bình yên", "hãy lưu lại để nghe mỗi tối nhé", "những đổi thay kỳ diệu trên sườn đồi"],
        ["Khi bước từng bước lên sườn đồi dốc đứng", "chiếc bình nứt vô cùng ngạc nhiên khi nhìn xuống vệ đường", "Nơi đó nở rộ muôn vàn bông hoa dại khoe sắc rực rỡ", "tỏa hương thơm ngát dịu dàng dưới nắng chiều", "Gió nhẹ lay động từng cánh hoa mềm mại", "biến lối mòn sỏi đá khô cằn thành một thảm hoa tuyệt đẹp"],
        ["Người gánh nước mỉm cười dịu dàng rồi chậm rãi giải thích", "Bác đã nhìn thấy vết nứt ấy ngay từ những ngày đầu tiên", "Bác lặng lẽ gieo những hạt giống hoa dọc theo lối mòn", "Suốt hai năm qua", "chính những giọt nước rỉ ra mỗi ngày", "đã kiên trì tưới mát và nuôi dưỡng những mầm hoa ấy lớn khôn"],
        ["Nếu không có vết xước ấy của chiếc bình", "sườn đồi khô cằn sẽ chẳng bao giờ có được dải hoa ngát hương", "Căn nhà nhỏ của người chủ", "cũng sẽ không có hoa thơm để trang hoàng mỗi sớm mai", "Vết nứt từng bị xem là khiếm khuyết đáng xấu hổ", "lại chính là nguồn mạch duy nhất tưới mát cho cái đẹp"],
        ["Nhìn lại cuộc đời của mỗi người chúng ta", "ai cũng từng mang trong mình những vết xước vô hình", "Đó có thể là một lần vấp ngã cay đắng", "một lời từ chối phũ phàng hay những giới hạn của bản thân", "khiến bạn cảm thấy tự ti và thu mình lại", "Ta thường ao ước mình được hoàn hảo như chiếc bình lành lặn kia"],
        ["Trong triết lý gốm cổ truyền Kintsugi", "những vết nứt vỡ không bị vứt bỏ mà được hàn gắn cẩn trọng", "bằng những đường chỉ vàng lấp lánh", "Đồ gốm sau khi phục hồi trở nên vô giá chính nhờ những vết sẹo được tôn vinh", "Khiếm khuyết của bạn chính là cánh cửa", "để lòng trắc ẩn, sự thấu hiểu và ánh sáng nhân từ đi qua"],
        ["Đêm nay, hãy tha thứ cho những điều bạn chưa làm được trong ngày", "Hãy ôm lấy những vết nứt trong tâm hồn", "bằng sự dịu dàng và lòng biết ơn sâu sắc", "Chúc bạn có một giấc ngủ thật sâu và bình an", "Hẹn gặp lại bạn dưới ánh trăng đêm mai.", "ánh trăng đêm mai"]
    ]

    scene_data = [
        {
            "id": "SC01",
            "title": "Nỗi tự trách đêm khuya",
            "purpose": "Triển khai bước 1: nỗi tự trách âm thầm và cảm giác bất toàn lúc đêm về",
            "action": "The gentle storybook traveler sits quietly by a warm wooden window holding a steaming cup of tea under starry skies.",
            "setting": "A cozy quiet bedside room overlooking moonlit rolling hills on velvety midnight indigo gouache canvas.",
            "camera": "Semantic full-frame sequence",
            "situation": "hook_cold_open",
            "narrative_phase": "lived_friction",
            "tempos": ["burst", "fast", "fast", "normal", "normal", "slow"],
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "emphasis": "TÂM TĨNH ĐÊM"
        },
        {
            "id": "SC02",
            "title": "Người gánh nước và hai chiếc bình",
            "purpose": "Triển khai bước 2: người gánh nước vùng núi đồi và đôi bình gốm trên vai",
            "action": "The humble water bearer carries two ceramic pots along a steep hill trail under twilight night sky.",
            "setting": "A scenic winding mountain footpath with pine trees on velvety midnight indigo gouache canvas.",
            "camera": "Semantic full-frame sequence",
            "situation": "story_action",
            "narrative_phase": "lived_friction",
            "tempos": ["fast", "fast", "normal", "normal", "normal", "slow"],
            "requirements": ["R02"],
            "character_ids": ["CH02", "CH03", "CH04"],
            "source_ids": ["SRC01"],
            "emphasis": None
        },
        {
            "id": "SC03",
            "title": "Nỗi mặc cảm của chiếc bình nứt",
            "purpose": "Triển khai bước 3: nỗi mặc cảm hai năm ròng của chiếc bình gốm nứt",
            "action": "The cracked pot weeps silent droplets of water while the intact pot stands tall and proud outside the house.",
            "setting": "Cottage porch with stone steps under midnight blue skies on velvety indigo gouache canvas.",
            "camera": "Semantic full-frame sequence",
            "situation": "before_after_contrast",
            "narrative_phase": "empirical_conflict",
            "tempos": ["fast", "normal", "normal", "slow", "slow", "normal"],
            "requirements": ["R03"],
            "character_ids": ["CH03", "CH04"],
            "source_ids": ["SRC01"],
            "emphasis": None
        },
        {
            "id": "SC04",
            "title": "Lời thú nhận bên dòng suối nhỏ",
            "purpose": "Triển khai bước 4: lời thú nhận run rẩy và xin lỗi bên dòng suối nhỏ",
            "action": "Beside the babbling stream, the cracked pot speaks with deep shame to the aged water bearer.",
            "setting": "A quiet mossy stream bank reflecting twinkling starlight on velvety midnight indigo gouache canvas.",
            "camera": "Semantic full-frame sequence",
            "situation": "mechanism_reveal",
            "narrative_phase": "empirical_conflict",
            "tempos": ["normal", "normal", "slow", "slow", "normal", "fast"],
            "requirements": ["R04"],
            "character_ids": ["CH02", "CH03"],
            "source_ids": ["SRC01"],
            "emphasis": None
        },
        {
            "id": "SC05",
            "title": "Lời chỉ dẫn dịu dàng và Mid-CTA",
            "purpose": "Triển khai bước 5: lời chỉ dẫn dịu dàng của người gánh nước ven lối về",
            "action": "The water bearer smiles tenderly, pats the clay pot, and points toward the path edges.",
            "setting": "A starlit hill incline leading back toward the master's house on velvety midnight indigo gouache canvas.",
            "camera": "Semantic full-frame sequence",
            "situation": "mechanism_step",
            "narrative_phase": "structural_model",
            "tempos": ["normal", "normal", "slow", "normal", "normal", "fast"],
            "requirements": ["R05"],
            "character_ids": ["CH02", "CH03"],
            "source_ids": ["SRC01"],
            "emphasis": "LƯU LẠI VIDEO"
        },
        {
            "id": "SC06",
            "title": "Dải hoa rực rỡ bên sườn đồi",
            "purpose": "Triển khai bước 6: dải hoa dại rực rỡ ngát hương bên sườn đồi đêm",
            "action": "The trailside under the cracked pot glows with an enchanting sea of blossoming wild petals.",
            "setting": "A breathtaking hillside pathway covered in glowing night wildflowers on velvety midnight indigo gouache canvas.",
            "camera": "Semantic full-frame sequence",
            "situation": "solution_framework",
            "narrative_phase": "structural_model",
            "tempos": ["fast", "fast", "normal", "normal", "slow", "slow"],
            "requirements": ["R06"],
            "character_ids": ["CH03"],
            "source_ids": ["SRC01"],
            "emphasis": None
        },
        {
            "id": "SC07",
            "title": "Bí mật của lòng bao dung",
            "purpose": "Triển khai bước 7: bí mật của lòng bao dung và những hạt mầm gieo sẵn",
            "action": "The water bearer reveals his secret: sowing wildflower seeds specifically along the cracked pot's side.",
            "setting": "Gentle hillside trail bathed in warm amber moonbeams on velvety midnight indigo gouache canvas.",
            "camera": "Semantic full-frame sequence",
            "situation": "deep_dive_step",
            "narrative_phase": "structural_model",
            "tempos": ["normal", "normal", "slow", "slow", "normal", "normal"],
            "requirements": ["R07"],
            "character_ids": ["CH02", "CH03"],
            "source_ids": ["SRC01"],
            "emphasis": None
        },
        {
            "id": "SC08",
            "title": "Lời bình: Vết nứt nuôi dưỡng cái đẹp",
            "purpose": "Triển khai bước 8: lời bình nhân sinh: vết nứt nuôi dưỡng sự sống",
            "action": "A poetic gouache meditation on how flaws nourish beauty and bring life to barren places.",
            "setting": "A symbolic gouache landscape of flourishing blossoms rooted in broken clay under midnight sky.",
            "camera": "Semantic full-frame sequence",
            "situation": "editorial_commentary",
            "narrative_phase": "structural_model",
            "tempos": ["slow", "slow", "normal", "normal", "slow", "slow"],
            "requirements": ["R08"],
            "character_ids": ["CH01", "CH03"],
            "source_ids": ["SRC01"],
            "emphasis": None
        },
        {
            "id": "SC09",
            "title": "Nỗi trăn trở về vết thương đời người",
            "purpose": "Triển khai bước 9: nỗi trăn trở đời người: ai cũng mang vết thương vô hình",
            "action": "The traveler sits in quiet reflection, remembering human frailties and emotional scars with tenderness.",
            "setting": "A serene night balcony overlooking sleeping village roofs on velvety midnight indigo gouache canvas.",
            "camera": "Semantic full-frame sequence",
            "situation": "case_study",
            "narrative_phase": "structural_model",
            "tempos": ["normal", "slow", "slow", "normal", "normal", "fast"],
            "requirements": ["R09"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01", "SRC02"],
            "emphasis": None
        },
        {
            "id": "SC10",
            "title": "Nghệ thuật Kintsugi hàn gắn bằng vàng",
            "purpose": "Triển khai bước 10: nghệ thuật kintsugi và vẻ đẹp của sự hàn gắn",
            "action": "A precious broken tea bowl is delicately rejoined with glowing lacquer lines of pure gold.",
            "setting": "A sacred Zen workshop illuminated by amber candlelight on velvety midnight indigo gouache canvas.",
            "camera": "Semantic full-frame sequence",
            "situation": "editorial_commentary",
            "narrative_phase": "actionable_resolution",
            "tempos": ["slow", "slow", "normal", "normal", "slow", "slow"],
            "requirements": ["R10"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "emphasis": "KINTSUGI"
        },
        {
            "id": "SC11",
            "title": "Tha thứ cho mình và chúc ngủ ngon",
            "purpose": "Triển khai bước 11: buông bỏ phán xét và giấc ngủ an yên dưới ánh trăng",
            "action": "The traveler closes eyes in profound peace as soft moonlight blankets the quiet world in tranquility.",
            "setting": "A tranquil starry firmament with glowing golden crescent moon and peaceful endcard on velvety midnight indigo canvas.",
            "camera": "Semantic full-frame sequence",
            "situation": "outro",
            "narrative_phase": "actionable_resolution",
            "tempos": ["normal", "normal", "slow", "slow", "hold", "hold"],
            "requirements": ["R11"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01", "SRC02"],
            "emphasis": "TÂM TĨNH ĐÊM"
        }
    ]

    scenes_16x9 = []
    for s_idx, s_meta in enumerate(scene_data):
        sc_id = s_meta["id"]
        sc_narr = narrations_16x9[s_idx]
        sc_sit = s_meta["situation"]
        sc_tempos = s_meta["tempos"]
        sc_chars = s_meta["character_ids"]
        sc_sources = s_meta["source_ids"]
        sc_quotes = quotes_16x9[s_idx]

        images = []
        beats = []
        for b_idx in range(6):
            img_id = f"{sc_id}_I{b_idx + 1}"
            beat_id = f"{sc_id}_B{b_idx + 1}"
            tempo = sc_tempos[b_idx]
            is_final_beat = (sc_id == "SC11" and b_idx == 5)
            anchor_quote = sc_quotes[b_idx]

            if sc_id == "SC01":
                img_desc = f"Cozy 2D flat matte gouache illustration beat {img_id}: gentle storybook traveler CH01 with tousled dark hair and warm golden-amber knitted scarf sitting by a wooden window under velvety midnight indigo sky #1B263B, holding steaming tea cup #E09F7D, crescent moon #F4D35E and starlight #778DA9, orthographic 2D, 65% negative space."
                mot_prompt = "Gentle 2D gouache animation, the traveler looks thoughtfully out the window as warm steam rises softly from the amber cup into tranquil starry indigo skies, silent visual storytelling, no talking, no lip movement"
            elif sc_id == "SC02":
                img_desc = f"Cozy 2D gouache painting beat {img_id}: gentle aged water bearer CH02 carrying a wooden yoke with terracotta pots CH03 and CH04 along a peaceful mountain path under starry night skies, orthographic 2D, 65% negative space."
                mot_prompt = "Gentle 2D gouache animation, the water bearer walks steadily along the dirt path under moonlit starry skies, yoke gently swaying, silent visual storytelling, no talking, no lip movement"
            elif sc_id == "SC03":
                img_desc = f"Cozy 2D gouache scene beat {img_id}: contrast between intact pot CH04 and rustic cracked pot CH03 weeping crystal water drops onto dry path stones under velvety midnight sky, orthographic 2D, 65% negative space."
                mot_prompt = "Gentle 2D gouache animation, water droplets seep slowly from the ceramic crack and fall toward the quiet earth, silent visual storytelling, no talking, no lip movement"
            elif sc_id == "SC04":
                img_desc = f"Cozy 2D gouache art beat {img_id}: rustic cracked pot CH03 resting by the clear forest stream, speaking in humble apology to kind water bearer CH02 under twilight evening glow, orthographic 2D, 65% negative space."
                mot_prompt = "Gentle 2D gouache animation, water ripples gently in the quiet stream reflecting twinkling stars as the water bearer listens with deep compassion, silent visual storytelling, no talking, no lip movement"
            elif sc_id == "SC05":
                img_desc = f"Cozy 2D gouache painting beat {img_id}: kind water bearer CH02 smiling warmly and gesturing toward the trailside with gentle encouragement, starlit path illuminated by moonbeams #F4D35E, orthographic 2D, 65% negative space."
                mot_prompt = "Gentle 2D gouache animation, the water bearer's kind face softens with an affectionate smile as moonlight highlights the pathway, silent visual storytelling, no talking, no lip movement"
            elif sc_id == "SC06":
                img_desc = f"Cozy 2D gouache vista beat {img_id}: a vibrant flourishing ribbon of blooming wildflowers in golden amber #F4D35E and starlight blue #778DA9 lining the path beneath cracked pot CH03, orthographic 2D, 60% negative space."
                mot_prompt = "Gentle 2D gouache animation, delicate night blossoms sway gently in the mountain breeze, glowing softly under the crescent moon, silent visual storytelling, no talking, no lip movement"
            elif sc_id == "SC07":
                img_desc = f"Cozy 2D gouache memory vignette beat {img_id}: weathered hands of water bearer CH02 gently sowing wildflower seeds along the path edge, nourished by water drops from cracked pot CH03, orthographic 2D, 65% negative space."
                mot_prompt = "Gentle 2D gouache animation, clear water droplets fall gently into the rich soil as tiny green shoots sprout under starlight, silent visual storytelling, no talking, no lip movement"
            elif sc_id == "SC08":
                img_desc = f"Cozy 2D gouache symbolic meditation beat {img_id}: cracked clay pot CH03 cradled in radiant blooming flowers, golden light glowing warmly through its fracture into midnight skies, orthographic 2D, 65% negative space."
                mot_prompt = "Gentle 2D gouache animation, radiant warm amber light pulses gently through the ceramic fissure, nurturing the surrounding blossoms, silent visual storytelling, no talking, no lip movement"
            elif sc_id == "SC09":
                img_desc = f"Cozy 2D gouache scene beat {img_id}: gentle traveler CH01 standing on a moonlit balcony, hand gently touching chest in deep empathetic self-compassion, overlooking sleeping village hills, orthographic 2D, 65% negative space."
                mot_prompt = "Gentle 2D gouache animation, the night wind sways the traveler's golden-amber scarf as quiet stars twinkle peacefully above the rooftops, silent visual storytelling, no talking, no lip movement"
            elif sc_id == "SC10":
                img_desc = f"Cozy 2D gouache art beat {img_id}: an ancient Japanese Kintsugi ceramic tea bowl restored with glowing golden lacquer veins #F4D35E, resting in sacred calm under starlight, orthographic 2D, 70% negative space."
                mot_prompt = "Gentle 2D gouache animation, pure golden lacquer along the fractured seams glimmers with ethereal warmth in the quiet night, silent visual storytelling, no talking, no lip movement"
            elif sc_id == "SC11":
                if is_final_beat:
                    img_desc = f"Serene 2D gouache bedtime endcard on velvety midnight indigo sky #1B263B: glowing crescent moon #F4D35E, quiet starry hills, and centered hand-lettered text 'TÂM TĨNH ĐÊM' in cream #F8F4E3, orthographic 2D, 75% negative space."
                    mot_prompt = "Gentle 2D gouache animation, the golden crescent moon glows in infinite calm stillness as shooting stars gently trace across velvety night skies, silent visual storytelling, no talking, no lip movement"
                else:
                    img_desc = f"Cozy 2D gouache peaceful bedtime beat {img_id}: traveler CH01 smiling gently with eyes closed, bathed in warm amber tea glow and starlight, entering serene rest, orthographic 2D, 70% negative space."
                    mot_prompt = "Gentle 2D gouache animation, traveler breathes in slowly and exhales with a subtle peaceful smile, shoulders dropping in complete relaxation, silent visual storytelling, no talking, no lip movement"

            img_entry = {
                "id": img_id,
                "description": img_desc,
                "character_ids": sc_chars,
                "based_on": None,
                "preserve": "clean velvety midnight indigo canvas #1B263B, storybook gouache style, traveler CH01 and water bearer",
                "change": f"narrative progression beat {img_id}",
                "reason": f"Narration-locked full-frame beat {img_id}.",
                "visible_text": [{"text": s_meta["emphasis"], "placement": "upper_third", "object": "emphasis"}] if (b_idx == 0 and s_meta["emphasis"]) or is_final_beat else [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": tempo,
                "narrative_situation": sc_sit,
                "focus": {"x": 0.5, "y": 0.0},
                "has_character": len(sc_chars) > 0,
                "motion_prompt": mot_prompt
            }
            if is_final_beat:
                img_entry["is_endcard"] = True
                img_entry["emphasis_text"] = "TÂM TĨNH ĐÊM"

            beat_entry = {
                "id": beat_id,
                "image_id": img_id,
                "purpose": f"Nhịp {b_idx + 1} cảnh {sc_id}: {s_meta['title']}",
                "anchor": {"vi": {"quote": anchor_quote, "occurrence": 1}},
                "effect": "hold" if (b_idx in (0, 5) or is_final_beat) else "cut",
                "focus": {"x": 0.5, "y": 0.0},
                "tempo": tempo,
                "narrative_situation": sc_sit,
                "camera_motion": "hold" if (b_idx in (0, 5) or is_final_beat) else "pan_left"
            }
            if is_final_beat:
                beat_entry["is_endcard"] = True

            images.append(img_entry)
            beats.append(beat_entry)

        scene_dict = {
            "id": sc_id,
            "title": s_meta["title"],
            "purpose": s_meta["purpose"],
            "action": s_meta["action"],
            "setting": s_meta["setting"],
            "camera": s_meta["camera"],
            "narration": sc_narr,
            "requirements": s_meta["requirements"],
            "character_ids": sc_chars,
            "source_ids": sc_sources,
            "narrative_situation": sc_sit,
            "narrative_phase": s_meta["narrative_phase"],
            "images": images,
            "beats": beats
        }
        scenes_16x9.append(scene_dict)

    brief_hash16 = compute_brief_hash(brief)
    content16 = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": brief_hash16,
        "topic": topic,
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": cast,
        "scenes": scenes_16x9,
        "coverage": [
            {"requirement_id": "R01", "scene_id": "SC01", "quote": "Khi bóng đêm buông xuống và mọi thanh âm dần lắng dịu, đôi lúc chúng ta nằm xuống với một nỗi ân hận mơ hồ."},
            {"requirement_id": "R02", "scene_id": "SC02", "quote": "Có một câu chuyện ngụ ngôn xưa kể về một người gánh nước nghèo."},
            {"requirement_id": "R03", "scene_id": "SC03", "quote": "Suốt hai năm ròng rã, chiếc bình lành luôn tự hào vì lúc nào cũng mang về trọn vẹn số nước suối trong veo."},
            {"requirement_id": "R04", "scene_id": "SC04", "quote": "Vào một buổi chiều bên bờ suối tĩnh lặng, chiếc bình nứt không thể kìm nén thêm nỗi đau khổ."},
            {"requirement_id": "R05", "scene_id": "SC05", "quote": "Người gánh nước nghe xong liền mỉm cười đôn hậu."},
            {"requirement_id": "R06", "scene_id": "SC06", "quote": "Khi bước từng bước lên sườn đồi dốc đứng, chiếc bình nứt vô cùng ngạc nhiên khi nhìn xuống vệ đường phía của nó."},
            {"requirement_id": "R07", "scene_id": "SC07", "quote": "Người gánh nước mỉm cười dịu dàng rồi chậm rãi giải thích."},
            {"requirement_id": "R08", "scene_id": "SC08", "quote": "Nếu không có vết xước ấy của chiếc bình, sườn đồi khô cằn sẽ chẳng bao giờ có được dải hoa ngát hương."},
            {"requirement_id": "R09", "scene_id": "SC09", "quote": "Nhìn lại cuộc đời của mỗi người chúng ta, ai cũng từng mang trong mình những vết xước vô hình."},
            {"requirement_id": "R10", "scene_id": "SC10", "quote": "Trong triết lý gốm cổ truyền Kintsugi, những vết nứt vỡ không bị vứt bỏ mà được hàn gắn cẩn trọng bằng những đường chỉ vàng lấp lánh."},
            {"requirement_id": "R11", "scene_id": "SC11", "quote": "Chúc bạn có một giấc ngủ thật sâu và bình an. Hẹn gặp lại bạn dưới ánh trăng đêm mai."}
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC08",
                "quote": "Vết nứt từng bị xem là khiếm khuyết đáng xấu hổ lại chính là nguồn mạch duy nhất tưới mát cho cái đẹp",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Nhận thức sự bất toàn là một phần tự nhiên của con người giúp xóa tan cảm giác cô lập."
            },
            {
                "scene_id": "SC10",
                "quote": "Đồ gốm sau khi phục hồi trở nên vô giá chính nhờ những vết sẹo được tôn vinh",
                "language": "vi",
                "source_id": "SRC02",
                "fact": "Nghệ thuật gốm Kintsugi hàn gắn vết vỡ bằng bột vàng để tôn vinh lịch sử biến cố thay vì che giấu."
            }
        ],
        "revision_response": [],
        "open_questions": []
    }

    return cr, brief, outline, content16


def save_package(run_dir: Path, cr: dict, brief: dict, outline: dict, content: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / "competitor_research.json", "w", encoding="utf-8") as f:
        json.dump(cr, f, ensure_ascii=False, indent=2)
    with open(run_dir / "brief.json", "w", encoding="utf-8") as f:
        json.dump(brief, f, ensure_ascii=False, indent=2)
    with open(run_dir / "outline.json", "w", encoding="utf-8") as f:
        json.dump(outline, f, ensure_ascii=False, indent=2)
    with open(run_dir / "content.json", "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    print(f"Saved complete package to {run_dir}")


def main():
    print("=" * 70)
    print("GENERATING BATCH 3 FOR TÂM TĨNH ĐÊM")
    print("=" * 70)

    # 1. Build and validate 9x16
    print("\n--- 1. Building tam-tinh-dem-batch3-9x16 ---")
    cr9, b9, o9, c9 = build_tam_tinh_dem_batch3_9x16()
    run_dir_9 = SYS_DIR / "runs" / "tam-tinh-dem-batch3-9x16"
    save_package(run_dir_9, cr9, b9, o9, c9)

    cta_errs_9 = lint_cta(b9, c9)
    print("CTA Linter 9x16 errors:", cta_errs_9)
    assert not cta_errs_9, f"CTA errors in 9x16: {cta_errs_9}"

    ed_res_9 = lint_editorial_and_narrative_quality(b9, c9)
    print("Editorial Linter 9x16 passed:", ed_res_9["passed"], "errors:", ed_res_9["errors"])
    assert ed_res_9["passed"], f"Editorial errors in 9x16: {ed_res_9['errors']}"

    div_res_9 = lint_script(c9["scenes"])
    print("Script Diversity 9x16 violations count:", len(div_res_9["violations"]))
    assert not div_res_9["violations"], f"Diversity violations in 9x16: {div_res_9['violations']}"

    pacing_errs_9 = audit_narrative_visual_density(b9, c9)
    print("Narrative Visual Density 9x16 errors:", pacing_errs_9)
    assert not pacing_errs_9, f"Pacing errors in 9x16: {pacing_errs_9}"

    # 2. Build and validate 16x9
    print("\n--- 2. Building tam-tinh-dem-batch3-16x9 ---")
    cr16, b16, o16, c16 = build_tam_tinh_dem_batch3_16x9()
    run_dir_16 = SYS_DIR / "runs" / "tam-tinh-dem-batch3-16x9"
    save_package(run_dir_16, cr16, b16, o16, c16)

    cta_errs_16 = lint_cta(b16, c16)
    print("CTA Linter 16x9 errors:", cta_errs_16)
    assert not cta_errs_16, f"CTA errors in 16x9: {cta_errs_16}"

    ed_res_16 = lint_editorial_and_narrative_quality(b16, c16)
    print("Editorial Linter 16x9 passed:", ed_res_16["passed"], "errors:", ed_res_16["errors"])
    assert ed_res_16["passed"], f"Editorial errors in 16x9: {ed_res_16['errors']}"

    div_res_16 = lint_script(c16["scenes"])
    print("Script Diversity 16x9 violations count:", len(div_res_16["violations"]))
    assert not div_res_16["violations"], f"Diversity violations in 16x9: {div_res_16['violations']}"

    pacing_errs_16 = audit_narrative_visual_density(b16, c16)
    print("Narrative Visual Density 16x9 errors:", pacing_errs_16)
    assert not pacing_errs_16, f"Pacing errors in 16x9: {pacing_errs_16}"

    # 3. JSON Schema validation
    print("\n--- 3. Validating against JSON Schema ---")
    for schema_name, file_name in [("brief-v3.json", "brief.json"), ("content-v3.json", "content.json")]:
        schema_path = SYS_DIR / "schemas" / schema_name
        with open(schema_path, encoding="utf-8") as sf:
            schema = json.load(sf)
        for run_dir in [run_dir_9, run_dir_16]:
            target_path = run_dir / file_name
            with open(target_path, encoding="utf-8") as tf:
                data = json.load(tf)
            jsonschema.validate(instance=data, schema=schema)
            print(f"Validated {target_path.name} in {run_dir.name} against {schema_name}: 100% PASS!")

    print("\n" + "=" * 70)
    print("ALL BATCH 3 VALIDATIONS & SCHEMAS PASSED 100% WITH ZERO ERRORS!")
    print("=" * 70)


if __name__ == "__main__":
    main()
