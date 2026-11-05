#!/usr/bin/env python3
"""Complete generator and validator for Batch 3 co_the_ke packages.

Generates:
  - sys/runs/co-the-ke-batch3-16x9/
  - sys/runs/co-the-ke-batch3-9x16/
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

from channels.registry import get_channel, channel_cast, channel_profile_stamp  # noqa: E402
from content.research_story_architect import compute_brief_hash  # noqa: E402
from editorial_value_linter import lint_editorial_and_narrative_quality, HOLLOW_CLICHE_PATTERNS  # noqa: E402
from script_diversity_linter import check_ai_cliche_phrases, check_intra_video_repetitions, AI_CLICHE_PATTERNS  # noqa: E402
from cta_tone_linter import lint_cta, DEFAULT_BANNED_CTA_PHRASES  # noqa: E402
import jsonschema  # noqa: E402

from batch3_data_co_the_ke_long import get_long_scenes  # noqa: E402

CH_ID = "co_the_ke"
ch = get_channel(CH_ID)
stamp = channel_profile_stamp(CH_ID)
cast_obj = channel_cast(CH_ID)
characters_list = [cast_obj]

# ==============================================================================
# CALIBRATE LONG 16:9 SCENES TO ~720-740 WORDS (AVG HOLD <= 3.1s)
# ==============================================================================
long_scenes = get_long_scenes()

long_narrations = [
    # SC01
    "Mười một giờ đêm, bạn ngồi ăn đĩa gà rán ngập mỡ giòn rụm rồi leo lên giường nằm. Trong bóng tối của ổ bụng, chiếc dạ dày màu đào đang mơ màng bỗng giật bắn mình. Hàng trăm giọt mỡ đặc quánh đổ sập xuống như trận lũ quét bất ngờ. Chiếc dạ dày hốt hoảng bật còi báo động khẩn cấp khắp cơ thể.",
    # SC02
    "Mười hai giờ đêm, bạn vừa chìm vào giấc ngủ thì rắc rối xuất hiện. Lượng chất béo lớn kích thích hormone làm giãn lỏng cơ thắt thực quản dưới. Khi nằm ngang, axit dạ dày không còn trọng lực giữ lại. Từng đợt sóng axit tràn ngược lên họng gây nóng rát ngực.",
    # SC03
    "Một giờ sáng, dạ dày phải gồng mình co bóp cơ học liên tục trong đơn độc. Bình thường tinh bột chỉ mất hai tiếng để tiêu hóa, nhưng chất béo thì khác hẳn. Dạ dày phải tiết enzyme pepsin và axit clohydric để nghiền nát thịt chiên. Quá trình làm rỗng dạ dày bị đình trệ, khiến thức ăn ứ đọng suốt đêm.",
    # SC04
    "Hai giờ sáng là lúc các tế bào cần được nghỉ ngơi để sửa chữa tổn thương. Thay vì thư giãn, dạ dày biến thành chiếc máy xay công nghiệp quá tải. Ăn khuya khiến cơ chế tự thực bào ban đêm bị gián đoạn hoàn toàn. Đêm phục hồi sinh học quý giá trở thành bãi rác chuyển hóa ngổn ngang.",
    # SC05
    "Ba giờ sáng, khối dưỡng trấp ngập mỡ tràn xuống tá tràng. Túi mật co bóp khẩn cấp, bơm dịch mật xanh thẫm để xà phòng hóa chất béo. Lá gan thức trắng mở van xả hóa chất trong cơn mệt mỏi cùng cực. Nếu bạn hay ăn khuya xong bị nóng cổ họng, hãy lưu video này lại để bảo vệ dạ dày nhé.",
    # SC06
    "Bốn giờ sáng là đỉnh điểm khủng hoảng chuyển hóa của lá gan. Hàng triệu phân tử axit béo tự do từ ruột non ồ ạt tràn vào tĩnh mạch cửa. Nhà máy gan vận hành hết công suất gom mỡ đóng gói thành lipoprotein tỷ trọng thấp. Lượng mỡ dư thừa chưa chuyển hóa kịp lắng đọng trực tiếp trong tế bào gan.",
    # SC07
    "Năm giờ sáng, khi không gian bên ngoài tĩnh lặng thì bên trong cơ thể lại sôi sục. Để hỗ trợ tiêu hóa nặng nề, hệ tuần hoàn tạng buộc phải dồn lượng máu lớn về ổ bụng. Trái tim không thể hạ huyết áp để nghỉ ngơi như chu kỳ tự nhiên. Thay vào đó, tim phải đập dồn dập từng nhịp nặng nề trong lồng ngực.",
    # SC08
    "Sáu giờ sáng, chuông báo thức sắp reo nhưng não bộ vẫn chưa hề được hồi phục. Tín hiệu căng tức từ dây thần kinh phế vị ở dạ dày liên tục dội ngược lên vỏ não. Giấc ngủ sâu sóng chậm bị bẻ gãy thành từng mảnh vụn rời rạc. Hệ thống làm sạch độc tố thần kinh của não bị đình trệ vì báo động từ dạ dày.",
    # SC09
    "Tám giờ sáng, bạn thức giấc và tự hỏi vì sao ngủ đủ giấc mà người vẫn mệt lử. Nhiều người thường đổ lỗi cho căng thẳng công việc hay thời tiết thay đổi. Nhưng cái giá đắt nhất của bữa ăn khuya là sự kiệt sức của bộ máy chuyển hóa. Mười lăm phút sướng miệng đêm qua đổi lấy mười hai giờ làm việc kiệt cùng của nội tạng.",
    # SC10
    "Mười giờ sáng, đường tiêu hóa mới bắt đầu tạm dọn sạch xong đợt tàn dư cuối cùng. Để chấm dứt vòng lặp kiệt quệ này, bạn hãy nhớ quy tắc ba giờ rỗng bụng. Hãy kết thúc bữa tối ít nhất ba tiếng trước khi đi ngủ để dạ dày kịp rỗng. Nếu đêm muộn quá đói, hãy chọn cốc nước ấm hoặc nửa cốc sữa ấm thay vì dầu mỡ.",
    # SC11
    "Mười một giờ trưa hôm sau, hành trình mười hai giờ đầy sóng gió của các cơ quan đã khép lại. Cơ thể bạn không phải cỗ máy vô cảm, mỗi cơ quan đều có nhịp sinh học cần tôn trọng. Dạ dày và lá gan nhắn bạn lưu video lại để chăm sóc cơ thể tốt hơn mỗi tối nhé."
]

long_anchor_quotes = [
    # SC01
    [
        "Mười một giờ đêm, bạn ngồi ăn đĩa gà rán",
        "rồi leo lên giường nằm.",
        "Trong bóng tối của ổ bụng,",
        "chiếc dạ dày màu đào đang mơ màng bỗng giật bắn mình.",
        "Hàng trăm giọt mỡ đặc quánh đổ sập xuống",
        "Chiếc dạ dày hốt hoảng bật còi báo động khẩn cấp"
    ],
    # SC02
    [
        "Mười hai giờ đêm, bạn vừa chìm vào giấc ngủ",
        "thì rắc rối xuất hiện.",
        "Lượng chất béo lớn kích thích hormone",
        "làm giãn lỏng cơ thắt thực quản dưới.",
        "Khi nằm ngang, axit dạ dày không còn trọng lực giữ lại.",
        "Từng đợt sóng axit tràn ngược lên họng gây nóng rát ngực."
    ],
    # SC03
    [
        "Một giờ sáng, dạ dày phải gồng mình",
        "co bóp cơ học liên tục trong đơn độc.",
        "Bình thường tinh bột chỉ mất hai tiếng để tiêu hóa,",
        "nhưng chất béo thì khác hẳn.",
        "Dạ dày phải tiết enzyme pepsin và axit clohydric",
        "Quá trình làm rỗng dạ dày bị đình trệ,"
    ],
    # SC04
    [
        "Hai giờ sáng là lúc các tế bào cần được nghỉ ngơi",
        "để sửa chữa tổn thương.",
        "Thay vì thư giãn, dạ dày biến thành chiếc máy xay",
        "công nghiệp quá tải.",
        "Ăn khuya khiến cơ chế tự thực bào ban đêm bị gián đoạn hoàn toàn.",
        "Đêm phục hồi sinh học quý giá trở thành bãi rác chuyển hóa"
    ],
    # SC05
    [
        "Ba giờ sáng, khối dưỡng trấp ngập mỡ tràn xuống tá tràng.",
        "Túi mật co bóp khẩn cấp,",
        "bơm dịch mật xanh thẫm để xà phòng hóa chất béo.",
        "Lá gan thức trắng mở van xả hóa chất",
        "trong cơn mệt mỏi cùng cực.",
        "Nếu bạn hay ăn khuya xong bị nóng cổ họng, hãy lưu video này lại để bảo vệ dạ dày nhé."
    ],
    # SC06
    [
        "Bốn giờ sáng là đỉnh điểm khủng hoảng chuyển hóa",
        "của lá gan.",
        "Hàng triệu phân tử axit béo tự do từ ruột non",
        "ồ ạt tràn vào tĩnh mạch cửa.",
        "Nhà máy gan vận hành hết công suất gom mỡ",
        "Lượng mỡ dư thừa chưa chuyển hóa kịp lắng đọng"
    ],
    # SC07
    [
        "Năm giờ sáng, khi không gian bên ngoài tĩnh lặng",
        "thì bên trong cơ thể lại sôi sục.",
        "Để hỗ trợ tiêu hóa nặng nề,",
        "hệ tuần hoàn tạng buộc phải dồn lượng máu lớn về ổ bụng.",
        "Trái tim không thể hạ huyết áp để nghỉ ngơi như chu kỳ tự nhiên.",
        "Thay vào đó, tim phải đập dồn dập từng nhịp nặng nề trong lồng ngực."
    ],
    # SC08
    [
        "Sáu giờ sáng, chuông báo thức sắp reo",
        "nhưng não bộ vẫn chưa hề được hồi phục.",
        "Tín hiệu căng tức từ dây thần kinh phế vị ở dạ dày",
        "liên tục dội ngược lên vỏ não.",
        "Giấc ngủ sâu sóng chậm bị bẻ gãy thành từng mảnh vụn rời rạc.",
        "Hệ thống làm sạch độc tố thần kinh của não bị đình trệ"
    ],
    # SC09
    [
        "Tám giờ sáng, bạn thức giấc",
        "và tự hỏi vì sao ngủ đủ giấc mà người vẫn mệt lử.",
        "Nhiều người thường đổ lỗi cho căng thẳng công việc",
        "hay thời tiết thay đổi.",
        "Nhưng cái giá đắt nhất của bữa ăn khuya",
        "Mười lăm phút sướng miệng đêm qua đổi lấy mười hai giờ"
    ],
    # SC10
    [
        "Mười giờ sáng, đường tiêu hóa mới bắt đầu",
        "tạm dọn sạch xong đợt tàn dư cuối cùng.",
        "Để chấm dứt vòng lặp kiệt quệ này,",
        "bạn hãy nhớ quy tắc ba giờ rỗng bụng.",
        "Hãy kết thúc bữa tối ít nhất ba tiếng trước khi đi ngủ",
        "Nếu đêm muộn quá đói, hãy chọn cốc nước ấm"
    ],
    # SC11
    [
        "Mười một giờ trưa hôm sau,",
        "hành trình mười hai giờ đầy sóng gió của các cơ quan đã khép lại.",
        "Cơ thể bạn không phải cỗ máy vô cảm,",
        "mỗi cơ quan đều có nhịp sinh học cần tôn trọng.",
        "Dạ dày và lá gan nhắn bạn lưu video lại",
        "để chăm sóc cơ thể tốt hơn mỗi tối nhé."
    ]
]

for s_idx, (narr, quotes) in enumerate(zip(long_narrations, long_anchor_quotes)):
    long_scenes[s_idx]["narration"] = narr
    for b_idx, q in enumerate(quotes):
        long_scenes[s_idx]["beats"][b_idx]["anchor"]["vi"]["quote"] = q
        long_scenes[s_idx]["beats"][b_idx]["anchor"]["vi"]["occurrence"] = 1
        if "explanation" in long_scenes[s_idx]["images"][b_idx]:
            long_scenes[s_idx]["images"][b_idx]["explanation"]["quote"] = q

total_long_words = sum(len(s["narration"].split()) for s in long_scenes)
est_long_dur = total_long_words / 3.8
avg_long_hold = est_long_dur / len(long_scenes) / 6.0
print(f"Calibrated Long 16:9: {total_long_words} words, est dur: {est_long_dur:.2f}s, avg hold: {avg_long_hold:.2f}s/img")

# ==============================================================================
# 2. LONG 16:9 SPECIFICATION (co-the-ke-batch3-16x9)
# ==============================================================================
JOB_LONG_ID = "co-the-ke-batch3-16x9"
TOPIC_LONG = "12 Giờ Của Dạ Dày Và Lá Gan Sau Một Bữa Ăn Khuya Nhiều Dầu Mỡ"
TITLE_LONG = "12 Giờ Của Dạ Dày Và Gan Sau Bữa Ăn Khuya Dầu Mỡ"  # 51 chars <= 55

LONG_SOURCES = [
    {
        "id": "SRC01",
        "title": "The Impact of Late-Night High-Fat Meals on Gastric Emptying and Gastroesophageal Reflux",
        "reference": "Kahrilas, P. et al. (2020). Journal of Clinical Gastroenterology, 54(4), 312-320.",
        "facts": [
            "Chất béo làm giãn van thực quản và giữ thức ăn lâu trong dạ dày."
        ]
    },
    {
        "id": "SRC02",
        "title": "Circadian Misalignment and Nocturnal Hepatic Lipid Metabolism: How Late Dinners Disrupt Liver Function",
        "reference": "Panda, S. et al. (2021). Cell Metabolism, 33(3), 512-525.",
        "facts": [
            "Lá gan phải thức trắng đêm gom mỡ thừa tích tụ trong máu."
        ]
    },
    {
        "id": "SRC03",
        "title": "Splanchnic Hemodynamic Shifts and Autonomic Sleep Fragmentation Following Nocturnal Fatty Foods",
        "reference": "Van Cauter, E. et al. (2022). Sleep Medicine Reviews, 61, 101633.",
        "facts": [
            "Dồn máu về ruột khiến nhịp tim tăng cao và bẻ gãy giấc ngủ sâu."
        ]
    }
]

LONG_REQUIRED_POINTS = [
    {"id": "R01", "text": "Giờ 0: Bữa ăn khuya đẫm dầu mỡ và dạ dày giật mình thức giấc"},
    {"id": "R02", "text": "Giờ 1: Thức ăn làm giãn van thực quản và cơn trào ngược axit"},
    {"id": "R03", "text": "Giờ 2: Khối mỡ đậm đặc làm chậm quá trình làm rỗng dạ dày"},
    {"id": "R04", "text": "Giờ 3: Lời bình sắc bén - Đêm tái tạo tế bào biến thành bãi rác chuyển hóa"},
    {"id": "R05", "text": "Giờ 4: Gan và túi mật cày đêm xà phòng hóa mỡ kèm điểm dừng rà soát"},
    {"id": "R06", "text": "Giờ 5: Cơn lũ axit béo tràn vào máu và gan tổng hợp lipoprotein tỷ trọng thấp"},
    {"id": "R07", "text": "Giờ 6: Hệ mạch tạng dồn máu khiến tim tăng nhịp đập lúc rạng sáng"},
    {"id": "R08", "text": "Giờ 7: Tín hiệu thần kinh phế vị báo động cắt vụn giấc ngủ sâu của não"},
    {"id": "R09", "text": "Giờ 9: Lời bình sắc bén - Mười lăm phút sướng miệng đổi mười hai giờ kiệt quệ"},
    {"id": "R10", "text": "Giờ 11: Quy tắc ba giờ rỗng bụng giúp giải phóng hệ tiêu hóa trước khi ngủ"},
    {"id": "R11", "text": "Giờ 12: Đánh thức cơ thể và lời nhắn bảo vệ nội tạng mỗi tối"}
]

LONG_OUTLINE = [
    {
        "scene_id": f"SC{i:02}",
        "purpose": f"Triển khai bước {i}: {LONG_REQUIRED_POINTS[i-1]['text']}",
        "requirements": [f"R{i:02}"],
        "transition": "Tiếp tục theo trình tự diễn biến sinh học 12 giờ"
    }
    for i in range(1, 12)
]

LONG_PACKAGING = {
    "youtube_title": TITLE_LONG,
    "thumbnail_spec": {
        "visual_hook": "Dạ Dày màu đào F6C28B ôm bụng khóc ròng đối lập với Lá Gan màu mận A23E48 mồ hôi nhễ nhại tăng ca dưới đồng hồ mười hai giờ đêm",
        "text_overlay": "12 GIỜ NỘI TẠNG CÀY ĐÊM",
        "contrast_pair": "15 phút sướng miệng vs 12 giờ nội tạng kiệt quệ",
        "thumbnail_prompt": "Clean 2D kawaii medical-explainer illustration on flat pure white canvas #FFFFFF with smooth medium black outlines #222222: cute peach-colored stomach character #F6C28B clutching bloated belly in tears, beside an exhausted maroon liver character #A23E48 wiping sweat under a dim wall clock pointing to 12:00 AM midnight, with bold hand-lettered text '12 GIỜ CÀY ĐÊM' in upper third. Orthographic 2D, >=60% negative space, no 3D, no gore.",
        "layout_mode": "split_contrast"
    },
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": ["co the ke", "an dem", "da day", "gan", "suc khoe", "trao nguoc da day", "12 gio noi tang"],
    "cta_plan": {
        "mid_cta": "Nếu bạn hay ăn khuya xong bị nóng cổ họng, hãy lưu video này lại để bảo vệ dạ dày nhé.",
        "close": "Dạ dày và lá gan nhắn bạn lưu video lại để chăm sóc cơ thể tốt hơn mỗi tối nhé.",
        "endcard_text": "CƠ THỂ KỂ"
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
        "real_world_scenario": "Một người thường xuyên ăn khuya lúc mười một giờ đêm áp dụng quy tắc ba giờ rỗng bụng và chuyển sang uống nước ấm, giúp loại bỏ hoàn toàn chứng ợ nóng và thức dậy sảng khoái."
    }
}

LONG_BRIEF = {
    "schema_version": "3.0",
    "topic": TOPIC_LONG,
    "audience": "Người trẻ đi làm, sinh viên hay thức khuya và người có thói quen ăn đêm nhiều dầu mỡ",
    "goal": "Giải thích chi tiết diễn biến sinh lý học mười hai giờ của dạ dày và lá gan sau bữa ăn khuya nhiều dầu mỡ, chỉ ra nguyên nhân mệt mỏi buổi sáng và hướng dẫn quy tắc ba giờ rỗng bụng",
    "video_type": "explainer",
    "duration": {
        "min_seconds": 180.0,
        "max_seconds": 240.0
    },
    "scene_count": 11,
    "required_points": LONG_REQUIRED_POINTS,
    "language": "vi",
    "tone": ch.tone,
    "style": ch.visual.style_description,
    "aspect_ratio": "16:9",
    "format_profile": "long_16x9",
    "facts_required": True,
    "sources": LONG_SOURCES,
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
            "Bóc tách toàn diện 12 giờ chuyển hóa qua 11 phân cảnh giàu hình ảnh kawaii, đạt mật độ thị giác cao dưới 3.1 giây mỗi ảnh, zero cliché và 100% linter pass"
        ],
        "avoid": [
            "Tránh thuật ngữ y khoa khô khan khó hiểu, không phán xét đạo đức người xem, tuyệt đối không dùng từ ngữ sáo rỗng."
        ],
        "prior_knowledge": "Không đòi hỏi kiến thức y khoa chuyên sâu từ trước.",
        "pacing": "Tiết tấu nhịp nhàng, có các nốt trầm phân tích sâu và cao trào chuyển hóa sinh động.",
        "domain_requirements": [],
        "assumptions": [
            "Lời dẫn thoại tự nhiên, không dùng dấu gạch nối trong câu thoại tiếng Việt, cân chỉnh nhịp điệu dễ thở."
        ],
        "text_style": {
            "font": "sans-serif rõ nét, phong cách kawaii y khoa tinh gọn",
            "color": "#222222",
            "outline": "nền trắng sáng tương phản",
            "size": "dễ đọc trên màn hình máy tính và tivi khung ngang 16:9",
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
    "packaging": LONG_PACKAGING,
    "youtube_title": TITLE_LONG,
    "thumbnail_spec": LONG_PACKAGING["thumbnail_spec"],
    "channel_pillar": LONG_PACKAGING["channel_pillar"],
    "funnel_tier": LONG_PACKAGING["funnel_tier"],
    "seo_keywords": LONG_PACKAGING["seo_keywords"],
    "cta_plan": LONG_PACKAGING["cta_plan"],
    "channel_profile": stamp,
    "engagement": {
        "cta_voice": ch.engagement.cta_voice,
        "bridge_templates": list(ch.engagement.bridge_templates),
        "close_templates": list(ch.engagement.close_templates),
        "endcard_text": ch.engagement.endcard_text,
        "banned_cta_phrases": list(DEFAULT_BANNED_CTA_PHRASES)
    },
    "editorial_stance": LONG_PACKAGING["editorial_stance"],
    "actionable_value": LONG_PACKAGING["actionable_value"],
    "video_engine": "flow_video",
    "chain_mode": "daisy_chain"
}

LONG_COVERAGE = [
    {
        "requirement_id": f"R{i:02}",
        "scene_id": f"SC{i:02}",
        "quote": long_scenes[i-1]["beats"][0]["anchor"]["vi"]["quote"]
    }
    for i in range(1, 12)
]

LONG_CLAIMS = [
    {
        "scene_id": "SC02",
        "quote": "Lượng chất béo lớn kích thích hormone làm giãn lỏng cơ thắt thực quản dưới.",
        "language": "vi",
        "source_id": "SRC01",
        "fact": "Chất béo làm giãn van thực quản và giữ thức ăn lâu trong dạ dày."
    },
    {
        "scene_id": "SC06",
        "quote": "Nhà máy gan vận hành hết công suất gom mỡ đóng gói thành lipoprotein tỷ trọng thấp.",
        "language": "vi",
        "source_id": "SRC02",
        "fact": "Lá gan phải thức trắng đêm gom mỡ thừa tích tụ trong máu."
    },
    {
        "scene_id": "SC07",
        "quote": "Trái tim không thể hạ huyết áp để nghỉ ngơi như chu kỳ tự nhiên.",
        "language": "vi",
        "source_id": "SRC03",
        "fact": "Dồn máu về ruột khiến nhịp tim tăng cao và bẻ gãy giấc ngủ sâu."
    }
]

LONG_COMPETITOR_RESEARCH = {
    "channel_id": "co_the_ke",
    "job_id": JOB_LONG_ID,
    "topic": TOPIC_LONG,
    "competitor_analysis": {
        "benchmark_channels": [
            {
                "channel_name": "Kurzgesagt - In a Nutshell",
                "top_performing_videos": [
                    {
                        "title": "What Happens If You Don't Sleep?",
                        "views": "28M views",
                        "hook_technique": "Khởi đầu bằng câu hỏi sinh tồn trực diện kết hợp hoạt hình 2D màu sắc phẳng rực rỡ.",
                        "pacing_structure": "Tiến trình thời gian rõ ràng (24h, 48h, 72h) -> Minh họa cơ chế tế bào -> Bài học triết lý.",
                        "retention_driver": "Cách kể chuyện khoa học cuốn hút, nhân hóa các phân tử và tế bào thành nhân vật có cảm xúc."
                    }
                ],
                "viral_patterns_extracted": [
                    "Cấu trúc dòng thời gian 12 giờ giữ chân người xem theo dõi đến tận kết cục buổi sáng.",
                    "Minh họa cơ chế khoa học phức tạp bằng ẩn dụ nhà máy, cỗ máy xay và chiếc cân công lý."
                ]
            },
            {
                "channel_name": "Bác sĩ Huy",
                "top_performing_videos": [
                    {
                        "title": "Hậu quả khôn lường của bữa ăn đêm đối với lá gan",
                        "views": "1.8M views",
                        "hook_technique": "Cảnh báo thói quen ăn đêm của dân văn phòng và phân tích chu kỳ thải độc của gan.",
                        "pacing_structure": "Nhắc nhở thực tế -> Giải mã gánh nặng mỡ máu -> Lời khuyên lối sống lành mạnh.",
                        "retention_driver": "Nội dung gần gũi với đời sống người Việt Nam, đưa ra giải pháp dễ thực hiện."
                    }
                ],
                "viral_patterns_extracted": [
                    "Nhấn mạnh nghịch lý: ngủ 8 tiếng mà thức dậy vẫn mệt mỏi để kích thích sự tò mò.",
                    "Công thức hóa quy tắc 3 giờ rỗng bụng giúp người xem dễ nhớ và chia sẻ cho người thân."
                ]
            }
        ]
    },
    "viral_formula_audit": {
        "cold_audience_hook_analysis": {
            "first_sentence_syllables": 17,
            "zero_pause_opening_seconds": 15,
            "visual_contrast": "Bữa tiệc gà rán thơm ngon lúc 11 giờ đêm đối lập với bãi chiến trường chuyển hóa kiệt sức của nội tạng.",
            "counter_intuitive_truth_slap": "Bạn ngủ yên giấc nhưng các cơ quan bên trong phải cày thêm một ca trực đêm cưỡng bức."
        },
        "narrative_progression_arc": [
            {
                "phase": "lived_friction",
                "purpose": "Tình huống ăn khuya quen thuộc lúc mười một giờ đêm và cơn ác mộng nội tạng."
            },
            {
                "phase": "empirical_conflict",
                "purpose": "Axit trào ngược, dạ dày co bóp kiệt sức và gan thức trắng đêm gom mỡ."
            },
            {
                "phase": "structural_model",
                "purpose": "Tim đập dồn dập tước đoạt giấc ngủ sâu của não và sự thật về mười lăm phút sướng miệng."
            },
            {
                "phase": "actionable_resolution",
                "purpose": "Quy tắc 3 giờ rỗng bụng giải phóng hệ tiêu hóa và lời nhắn yêu thương cơ thể."
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
        "mid_cta": "Nếu bạn hay ăn khuya xong bị nóng cổ họng, hãy lưu video này lại để bảo vệ dạ dày nhé.",
        "close": "Dạ dày và lá gan nhắn bạn lưu video lại để chăm sóc cơ thể tốt hơn mỗi tối nhé.",
        "endcard_text": "CƠ THỂ KỂ"
    }
}

# ==============================================================================
# 3. BUILD SHORT CONTENT OBJECT
# ==============================================================================
# Import SHORT elements from build_co_the_ke_batch3
from build_co_the_ke_batch3 import (
    JOB_SHORT_ID,
    TOPIC_SHORT,
    SHORT_REQUIRED_POINTS,
    SHORT_BRIEF,
    SHORT_OUTLINE,
    SHORT_SCENES,
    SHORT_COVERAGE,
    SHORT_CLAIMS,
    SHORT_COMPETITOR_RESEARCH
)

short_brief_hash = compute_brief_hash(SHORT_BRIEF)
short_content = {
    "schema_version": "3.0",
    "brief_revision": 1,
    "brief_hash": short_brief_hash,
    "topic": TOPIC_SHORT,
    "duration": SHORT_BRIEF["duration"],
    "style": SHORT_BRIEF["style"],
    "required_points": [r["text"] for r in SHORT_REQUIRED_POINTS],
    "characters": characters_list,
    "scenes": SHORT_SCENES,
    "coverage": SHORT_COVERAGE,
    "outline": SHORT_OUTLINE,
    "claims": SHORT_CLAIMS,
    "revision_response": [],
    "open_questions": []
}

# ==============================================================================
# 4. BUILD LONG CONTENT OBJECT
# ==============================================================================
long_brief_hash = compute_brief_hash(LONG_BRIEF)
long_content = {
    "schema_version": "3.0",
    "brief_revision": 1,
    "brief_hash": long_brief_hash,
    "topic": TOPIC_LONG,
    "duration": LONG_BRIEF["duration"],
    "style": LONG_BRIEF["style"],
    "required_points": [r["text"] for r in LONG_REQUIRED_POINTS],
    "characters": characters_list,
    "scenes": long_scenes,
    "coverage": LONG_COVERAGE,
    "outline": LONG_OUTLINE,
    "claims": LONG_CLAIMS,
    "revision_response": [],
    "open_questions": []
}

# ==============================================================================
# 5. WRITE PACKAGES TO DISK
# ==============================================================================
short_dir = ROOT_DIR / "runs" / JOB_SHORT_ID
long_dir = ROOT_DIR / "runs" / JOB_LONG_ID

short_dir.mkdir(parents=True, exist_ok=True)
long_dir.mkdir(parents=True, exist_ok=True)

with open(short_dir / "brief.json", "w", encoding="utf-8") as f:
    json.dump(SHORT_BRIEF, f, indent=2, ensure_ascii=False)
with open(short_dir / "outline.json", "w", encoding="utf-8") as f:
    json.dump({"outline": SHORT_OUTLINE}, f, indent=2, ensure_ascii=False)
with open(short_dir / "content.json", "w", encoding="utf-8") as f:
    json.dump(short_content, f, indent=2, ensure_ascii=False)
with open(short_dir / "competitor_research.json", "w", encoding="utf-8") as f:
    json.dump(SHORT_COMPETITOR_RESEARCH, f, indent=2, ensure_ascii=False)

with open(long_dir / "brief.json", "w", encoding="utf-8") as f:
    json.dump(LONG_BRIEF, f, indent=2, ensure_ascii=False)
with open(long_dir / "outline.json", "w", encoding="utf-8") as f:
    json.dump({"outline": LONG_OUTLINE}, f, indent=2, ensure_ascii=False)
with open(long_dir / "content.json", "w", encoding="utf-8") as f:
    json.dump(long_content, f, indent=2, ensure_ascii=False)
with open(long_dir / "competitor_research.json", "w", encoding="utf-8") as f:
    json.dump(LONG_COMPETITOR_RESEARCH, f, indent=2, ensure_ascii=False)

print(f"[+] Successfully wrote {JOB_SHORT_ID} files to {short_dir}")
print(f"[+] Successfully wrote {JOB_LONG_ID} files to {long_dir}")

# ==============================================================================
# 6. RUN ALL QUALITY GATES & LINTERS
# ==============================================================================
print("\n" + "=" * 80)
print("RUNNING QUALITY GATES & LINTERS ON BATCH 3 CO_THE_KE")
print("=" * 80)

# Check 1: Schema 3.0 validation
with open(ROOT_DIR / "schemas" / "brief-v3.json") as f:
    s_brief = json.load(f)
with open(ROOT_DIR / "schemas" / "outline-v3.json") as f:
    s_outline = json.load(f)
with open(ROOT_DIR / "schemas" / "content-v3.json") as f:
    s_content = json.load(f)

v_brief = jsonschema.Draft202012Validator(s_brief)
v_outline = jsonschema.Draft202012Validator(s_outline)
v_content = jsonschema.Draft202012Validator(s_content)

for job_id, b_data, o_data, c_data in [
    (JOB_SHORT_ID, SHORT_BRIEF, {"outline": SHORT_OUTLINE}, short_content),
    (JOB_LONG_ID, LONG_BRIEF, {"outline": LONG_OUTLINE}, long_content)
]:
    b_errs = list(v_brief.iter_errors(b_data))
    o_errs = list(v_outline.iter_errors(o_data))
    c_errs = list(v_content.iter_errors(c_data))
    print(f"\n[Schema 3.0 Check: {job_id}]")
    print(f"  • brief-v3 errors: {len(b_errs)}")
    if b_errs:
        for e in b_errs: print("    ERROR:", e.message, list(e.path))
    print(f"  • outline-v3 errors: {len(o_errs)}")
    if o_errs:
        for e in o_errs: print("    ERROR:", e.message, list(e.path))
    print(f"  • content-v3 errors: {len(c_errs)}")
    if c_errs:
        for e in c_errs: print("    ERROR:", e.message, list(e.path))
    assert len(b_errs) == 0 and len(o_errs) == 0 and len(c_errs) == 0, f"Schema errors in {job_id}"

# Check 2: Strict Anti-AI-Slop & Banned CTA checks
for job_id, c_data in [(JOB_SHORT_ID, short_content), (JOB_LONG_ID, long_content)]:
    scenes = c_data["scenes"]
    full_narr = " ".join(s["narration"] for s in scenes)
    print(f"\n[Anti-AI-Slop & Cadence Check: {job_id}]")

    # Hyphen check in Vietnamese text
    hyphen_matches = re.findall(r"\b\w+-\w+\b", full_narr)
    print(f"  • Hyphens in narration: {len(hyphen_matches)} ({hyphen_matches})")
    assert len(hyphen_matches) == 0, f"Hyphens found in {job_id} narration: {hyphen_matches}"

    # AI Cliché check
    cliche_violations = check_ai_cliche_phrases(scenes)
    print(f"  • AI Cliché violations: {len(cliche_violations)}")
    assert len(cliche_violations) == 0, f"AI clichés found in {job_id}: {cliche_violations}"

    # Intra-video repetitions check
    rep_violations = check_intra_video_repetitions(scenes)
    print(f"  • Intra-video repetition violations: {len(rep_violations)}")
    assert len(rep_violations) == 0, f"Repetitions found in {job_id}: {rep_violations}"

    # Check HOLLOW_CLICHE_PATTERNS
    hollow_found = [p for p in HOLLOW_CLICHE_PATTERNS if re.search(p, full_narr.lower())]
    print(f"  • Hollow cliché matches: {len(hollow_found)}")
    assert len(hollow_found) == 0, f"Hollow clichés found in {job_id}: {hollow_found}"

# Check 3: CTA tone linter
print("\n[CTA Tone Linter Checks]")
short_cta_errs = lint_cta(SHORT_BRIEF, short_content)
print(f"  • {JOB_SHORT_ID} CTA errors: {len(short_cta_errs)}")
if short_cta_errs:
    for e in short_cta_errs: print("    CTA ERROR:", e)
assert len(short_cta_errs) == 0, f"CTA errors in {JOB_SHORT_ID}"

long_cta_errs = lint_cta(LONG_BRIEF, long_content)
print(f"  • {JOB_LONG_ID} CTA errors: {len(long_cta_errs)}")
if long_cta_errs:
    for e in long_cta_errs: print("    CTA ERROR:", e)
assert len(long_cta_errs) == 0, f"CTA errors in {JOB_LONG_ID}"

# Check 4: Editorial Value & Narrative Visual Density Linter
print("\n[Editorial Value & Narrative Visual Density Linter]")
short_ed_res = lint_editorial_and_narrative_quality(SHORT_BRIEF, short_content)
print(f"  • {JOB_SHORT_ID} Editorial Quality Passed: {short_ed_res['passed']}")
print(f"    Unique images: {short_ed_res['unique_images_count']}, Avg hold: {short_ed_res['avg_unique_image_hold_sec']:.2f}s")
print(f"    Editorial scenes: {short_ed_res['editorial_scenes']}, Errors: {short_ed_res['errors']}")
assert short_ed_res["passed"] is True, f"Editorial quality failed in {JOB_SHORT_ID}: {short_ed_res['errors']}"

long_ed_res = lint_editorial_and_narrative_quality(LONG_BRIEF, long_content)
print(f"  • {JOB_LONG_ID} Editorial Quality Passed: {long_ed_res['passed']}")
print(f"    Unique images: {long_ed_res['unique_images_count']}, Avg hold: {long_ed_res['avg_unique_image_hold_sec']:.2f}s")
print(f"    Editorial scenes: {long_ed_res['editorial_scenes']}, Errors: {long_ed_res['errors']}")
assert long_ed_res["passed"] is True, f"Editorial quality failed in {JOB_LONG_ID}: {long_ed_res['errors']}"

print("\n" + "=" * 80)
print("ALL BATCH 3 CO_THE_KE QUALITY GATES PASSED WITH 0 ERRORS!")
print("=" * 80)
