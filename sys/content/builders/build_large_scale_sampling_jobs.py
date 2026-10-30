#!/usr/bin/env python3
"""Build production-ready packages for Large-Scale Sampling & Error Control.

Pillar: "Hướng Dẫn Nghiên Cứu Khoa Học Cho Người Mới" (research_guide, tier_1_broad)
Core Topic: "Bí Mật 400 Người Đại Diện Triệu Dân (Cách Viện Nghiên Cứu Lấy Mẫu Không Tốn Sức)"
Metaphor: "Nồi súp khổng lồ & Muôi nếm" (Stratified Sampling + Quality/Error Control)

Formats:
  - large-scale-sampling-9x16: 19 scenes, vertical mobile explainer (~108s, kinetic typography)
  - large-scale-sampling-16x9: 16 scenes, 5-act narrative arc landscape explainer (~7 min)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List

ROOT_DIR = Path(__file__).resolve().parents[3]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content.research_story_architect import (
    CAST_APPEARANCE,
    DEFAULT_OUTFIT,
    HumanEditorialSpec,
    PackagingSpec,
    ResearchedScene,
    ResearchedTopic,
    build_scenes_from_story_rows,
    write_production_package,
)
from content.research_story_architect import (
    CURRENT_STYLE_DESCRIPTION as STYLE_DESCRIPTION,
)

CHANNEL_PILLAR_RESEARCH_GUIDE = "Hướng Dẫn Nghiên Cứu Khoa Học Cho Người Mới"

SETTINGS_9X16 = [
    "Solid warm cream canvas (#F8F0DC).",
    "Clean pure white background (#FFFFFF).",
    "Solid ivory neutral field (#F8F0DC).",
    "Clean stark white surface (#FFFFFF).",
    "Solid soft cream canvas (#F8F0DC).",
    "Pure white diagram canvas (#FFFFFF).",
    "Solid warm cream field (#F8F0DC).",
    "Clean pure white backdrop (#FFFFFF).",
    "Solid ivory concept surface (#F8F0DC).",
    "Clean white graphic field (#FFFFFF).",
    "Solid soft cream background (#F8F0DC).",
    "Pure white explainer canvas (#FFFFFF).",
    "Solid warm cream ground (#F8F0DC).",
    "Clean stark white backdrop (#FFFFFF).",
    "Solid ivory neutral canvas (#F8F0DC).",
    "Pure white concept field (#FFFFFF).",
    "Solid soft cream surface (#F8F0DC).",
    "Clean pure white workspace (#FFFFFF).",
    "Solid warm cream backdrop (#F8F0DC).",
]

SETTINGS_16X9 = [
    "Solid warm cream canvas (#F8F0DC).",
    "Clean pure white background (#FFFFFF).",
    "Solid ivory neutral field (#F8F0DC).",
    "Clean stark white surface (#FFFFFF).",
    "Solid soft cream canvas (#F8F0DC).",
    "Pure white diagram canvas (#FFFFFF).",
    "Solid warm cream field (#F8F0DC).",
    "Clean pure white backdrop (#FFFFFF).",
    "Solid ivory concept surface (#F8F0DC).",
    "Clean white graphic field (#FFFFFF).",
    "Solid soft cream background (#F8F0DC).",
    "Pure white explainer canvas (#FFFFFF).",
    "Solid warm cream ground (#F8F0DC).",
    "Clean stark white backdrop (#FFFFFF).",
    "Solid ivory neutral canvas (#F8F0DC).",
    "Pure white concept field (#FFFFFF).",
]

# ---------------------------------------------------------------------------
# STORY 9:16 (19 Scenes — High Velocity Mobile Spinoff Blueprint)
# ---------------------------------------------------------------------------
STORY_9X16: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    # STAGE 1: hook (Scenes 1-3)
    (
        "Nghịch lý 400 người và 2 triệu dân",
        SETTINGS_9X16[0],
        "narrative_warm",
        "counter_intuitive_shift",
        "hook",
        [
            ("Chỉ cần bốn trăm người, là đại diện được cho cả triệu dân.", "full_scene:CH01|Stickman stands beside a giant number '2.000.000' and a tiny cluster labeled '400' on flat warm cream canvas."),
            ("Bạn có tin điều này không?", "variation:CH01|Stickman leans forward with wide curious eyes pointing index finger to the floating question mark on cream field."),
        ],
    ),
    (
        "Sự thật của các Viện nghiên cứu",
        SETTINGS_9X16[1],
        "narrative_warm",
        "gentle_lived_friction",
        "hook",
        [
            ("Nghe như đùa đúng không?", "full_scene:CH01|Stickman with hands raised in wide comic surprise on open white canvas."),
            ("Nhưng các Viện nghiên cứu làm đúng như vậy mỗi ngày.", "variation:CH01|Stickman nods knowingly as a crisp marker arrow connects the 400 group to the 2.000.000 label on white ground."),
        ],
    ),
    (
        "Ẩn dụ chiếc nồi súp",
        SETTINGS_9X16[2],
        "narrative_warm",
        "gentle_lived_friction",
        "hook",
        [
            ("Bí mật nằm ở một chiếc nồi súp.", "concept_metaphor:none|A giant steaming soup pot outline drawn with thick black marker, twice the height of stickman, on flat ivory neutral canvas, seventy percent negative space."),
        ],
    ),

    # STAGE 2: problem (Scenes 4-7)
    (
        "Quy tắc một muôi canh",
        SETTINGS_9X16[3],
        "analytical_crisp",
        "mechanistic_dissection",
        "problem",
        [
            ("Nấu một nồi súp một nghìn lít, không ai húp hết cả nồi mới biết mặn nhạt.", "full_scene:CH01|Stickman stands beside the huge pot holding a small soup ladle on stark white surface."),
            ("Bạn chỉ cần nếm đúng một muôi.", "variation:CH01|Stickman tastes a small sip from the ladle with a calm satisfied nod on white field."),
        ],
    ),
    (
        "Cái bẫy hớt váng dầu",
        SETTINGS_9X16[4],
        "analytical_crisp",
        "mechanistic_dissection",
        "problem",
        [
            ("Nhưng nếu bạn chỉ hớt lớp váng dầu trên mặt, bạn sẽ thấy toàn mỡ ngấy.", "full_scene:CH01|Stickman makes a disgusted face while skimming only yellow greasy film floating on top of the soup pot on soft cream canvas."),
        ],
    ),
    (
        "Sai lầm Google Form Facebook",
        SETTINGS_9X16[5],
        "analytical_crisp",
        "mechanistic_dissection",
        "problem",
        [
            ("Đó chính là sai lầm của sinh viên: Gửi link khảo sát vào mấy nhóm bạn bè trên Facebook.", "full_scene:CH01|Stickman sits hunched with laptop sending a survey link into crowded chat bubbles, crossed out with a bold red marker stroke."),
        ],
    ),
    (
        "Mẫu số liệu bị lệch",
        SETTINGS_9X16[6],
        "analytical_crisp",
        "mechanistic_dissection",
        "problem",
        [
            ("Số liệu đó chỉ đại diện cho nhóm bạn thân của bạn, không đại diện cho sinh viên toàn quốc.", "white_card:none|A white card displaying tags 'TOÀN BẠN CÙNG PHÒNG' and 'TOÀN BẠN CÙNG KHOA' vibrating with a bold red warning stamp 'MẪU BỊ LỆCH'."),
        ],
    ),

    # STAGE 3: causal_mechanism (Scenes 8-10)
    (
        "Khuấy đều và múc phân tầng",
        SETTINGS_9X16[7],
        "analytical_crisp",
        "scientific_evidence",
        "causal_mechanism",
        [
            ("Còn các Viện nghiên cứu làm gì?", "full_scene:CH01|Stickman pauses with marker pen in hand, looking focused on pure white backdrop."),
            ("Họ khuấy đều và múc phân tầng.", "variation:CH01|Stickman plunges a long ladle deep to the pot bottom, creating swirling ripples and lifting soup evenly on white canvas."),
        ],
    ),
    (
        "Ba tầng sinh viên trong một muôi",
        SETTINGS_9X16[8],
        "analytical_crisp",
        "scientific_evidence",
        "causal_mechanism",
        [
            ("Trong một muôi súp, họ gom đủ: Sinh viên kỹ thuật, sinh viên kinh tế và sinh viên y dược.", "visual_diagram:none|A three-tier horizontal stratified diagram showing 'KINH TẾ', 'KỸ THUẬT', 'Y DƯỢC' balanced with three neat black arrows on ivory field."),
        ],
    ),
    (
        "Phân bổ vùng miền đồng đều",
        SETTINGS_9X16[9],
        "analytical_crisp",
        "scientific_evidence",
        "causal_mechanism",
        [
            ("Họ chia đều theo vùng miền: Bắc, Trung, Nam, trường công và trường tư.", "visual_diagram:none|A minimalist outline map of Vietnam divided into North, Central, and South regions with balanced sample dot clusters on white ground."),
        ],
    ),

    # STAGE 4: explanation (Scenes 11-13)
    (
        "Cán cân 400 và sai số năm phần trăm",
        SETTINGS_9X16[10],
        "analytical_crisp",
        "demystifying_truth",
        "explanation",
        [
            ("Chỉ cần bốn trăm người được chọn ngẫu nhiên chuẩn chỉ, sai số chỉ dưới năm phần trăm.", "concept_metaphor:none|A balanced scale with 400 verified units perfectly leveling with 2.000.000 population, marked with a clean 'SAI SỐ < 5%' badge."),
        ],
    ),
    (
        "Giám sát định vị GPS",
        SETTINGS_9X16[11],
        "analytical_crisp",
        "demystifying_truth",
        "explanation",
        [
            ("Đặc biệt, họ không dùng Google Form vô danh.", "full_scene:CH01|Stickman shakes head waving away a blank question form on white explainer canvas."),
            ("Họ dùng phần mềm có định vị G-P-S.", "variation:CH01|A field surveyor stickman holds a digital tablet displaying satellite GPS signal waves and live coordinates on white canvas."),
        ],
    ),
    (
        "Thùng rác bẫy thời gian",
        SETTINGS_9X16[12],
        "analytical_crisp",
        "demystifying_truth",
        "explanation",
        [
            ("Ai làm khảo sát dưới một phút là hệ thống tự động loại bỏ vì nghi ngờ tích bừa.", "visual_diagram:none|A hasty 30-second survey sheet with rapid random checkmarks dropping straight into an open black marker trash bin on warm cream ground."),
        ],
    ),

    # STAGE 5: counter_argument (Scenes 14-15)
    (
        "Kiểm tra chéo mười phần trăm",
        SETTINGS_9X16[13],
        "analytical_crisp",
        "counter_intuitive_shift",
        "counter_argument",
        [
            ("Họ còn gọi điện ngẫu nhiên mười phần trăm số phiếu để kiểm tra xem có ai khai khống hay không.", "full_scene:CH01|A supervisor stickman sits at a desk with phone handset, auditing answers with a bold 'KIỂM TRA CHÉO 10%' rubber stamp on stark white backdrop."),
        ],
    ),
    (
        "Áp lực nguồn lực sinh viên",
        SETTINGS_9X16[14],
        "reflective_slow",
        "gentle_lived_friction",
        "counter_argument",
        [
            ("Vậy sinh viên lấy đâu ra tiền và công nghệ để làm quy trình khủng như thế này?", "full_scene:CH01|Stickman clasps head with both hands looking bewildered beside an empty overturned wallet and hourglass on ivory canvas."),
        ],
    ),

    # STAGE 6: takeaway (Scenes 16-19)
    (
        "Kho báu dữ liệu thứ cấp",
        SETTINGS_9X16[15],
        "analytical_crisp",
        "empowering_resolution",
        "takeaway",
        [
            ("Đừng lo, đây là vũ khí bí mật cho bạn: Dữ liệu thứ cấp.", "concept_metaphor:none|A treasure chest drawn in clean black marker opening with radiant light beams, revealing two labeled file binders: 'GSO' and 'WORLD BANK' on white concept field."),
        ],
    ),
    (
        "Tải dữ liệu mở miễn phí",
        SETTINGS_9X16[16],
        "analytical_crisp",
        "empowering_resolution",
        "takeaway",
        [
            ("Tổng cục Thống kê và World Bank đã khảo sát sẵn hàng triệu người và công khai miễn phí.", "full_scene:CH01|Stickman sits at desk with laptop displaying a verified spreadsheet download progress bar reaching 100% with a relaxed smile on soft cream surface."),
        ],
    ),
    (
        "Điểm tối đa trước hội đồng",
        SETTINGS_9X16[17],
        "analytical_crisp",
        "empowering_resolution",
        "takeaway",
        [
            ("Bạn chỉ cần tải về, làm sạch và phân tích.", "full_scene:CH01|Stickman points index finger to clean spreadsheet rows with confident smile on clean white workspace."),
            ("Hội đồng sẽ chấm điểm tối đa vì số liệu chuẩn quốc gia.", "variation:CH01|Stickman presents a clean bar chart to nodding committee professors who raise an 'A+' score placard with approval."),
        ],
    ),
    (
        "Lời khuyên đúc kết và theo dõi",
        SETTINGS_9X16[18],
        "narrative_warm",
        "empowering_resolution",
        "takeaway",
        [
            ("Đừng tự làm khó mình bằng cách đi phát phiếu dạo.", "full_scene:CH01|Stickman shakes head gently with calm enlightened expression on warm cream backdrop."),
            ("Bấm theo dõi kênh để nhận link kho dữ liệu xịn này nhé!", "variation:CH01|Stickman winks with a friendly thumbs-up pointing directly toward a marker-sketched follow button with seventy percent open space."),
        ],
    ),
]


# ---------------------------------------------------------------------------
# STORY 16:9 (16 Scenes — 5-Act Deep Explainer Narrative Arc)
# ---------------------------------------------------------------------------
STORY_16X9: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    # ACT 1: Hook & Mathematical Paradox (Scenes 1-3)
    (
        "Nghịch lý con số bão hòa",
        SETTINGS_16X9[0],
        "narrative_warm",
        "counter_intuitive_shift",
        "hook",
        [
            ("Khảo sát bốn trăm người, là đại diện được cho cả triệu dân.", "full_scene:CH01|Stickman stands between two massive numbers '400' and '2.000.000' on flat warm cream canvas with an inquisitive tilt of the head."),
            ("Bạn có tin điều vô lý này không?", "variation:CH01|Stickman leans forward with wide curious eyes looking at the floating question mark on cream field."),
            ("Nhiều người nghĩ rằng dân số càng lớn thì mẫu càng phải khủng khiếp.", "variation:CH01|Stickman sketches a rapidly growing crowd of stick figures with expanding dashed circles on cream field."),
            ("Đó là hiểu lầm phổ biến nhất trong nghiên cứu khoa học.", "concept_metaphor:none|A simple doodle question mark enclosed in a large black circle, seventy-five percent negative space on cream canvas."),
            ("Toán học chứng minh rằng sai số giảm theo quy luật bão hòa rất nhanh.", "visual_diagram:none|A curved graph line dropping steeply from 10% to 5% error at n=400, then flattening completely across the horizontal axis."),
            ("Vượt qua ngưỡng bốn trăm người, độ chính xác tăng thêm không đáng kể.", "still_life:none|A small clean balance scale doodle centered on flat cream canvas with eighty percent breathing space."),
        ],
    ),
    (
        "Định luật lợi ích cận biên giảm dần",
        SETTINGS_16X9[1],
        "analytical_crisp",
        "mechanistic_dissection",
        "hook",
        [
            ("Từ một trăm lên bốn trăm mẫu, sai số giảm hơn một nửa.", "visual_diagram:none|A comparison bar showing error drop from 10% down to 5% with clear downward black arrows on white field."),
            ("Nhưng từ bốn trăm lên mười nghìn mẫu, sai số chỉ giảm thêm chưa đầy một phần trăm.", "variation:CH01|Stickman examines a long thin graph bar showing minuscule error drop of less than one percent."),
            ("Trong khi đó, kinh phí và thời gian của bạn phải tăng gấp hai mươi lăm lần.", "full_scene:CH01|Stickman staggers under an enormous stack of paper surveys with sweating forehead on white canvas."),
            ("Các Viện nghiên cứu dừng lại ở bốn trăm mẫu vì họ hiểu rõ bài toán hiệu quả.", "variation:CH01|Stickman folds arms calmly with a knowing smile beside a neat clipboard labeled 'N = 400'."),
        ],
    ),
    (
        "Chiếc nồi súp một nghìn lít",
        SETTINGS_16X9[2],
        "narrative_warm",
        "gentle_lived_friction",
        "hook",
        [
            ("Nhà vật lý Richard Feynman từng đưa ra một ví dụ rất giản dị.", "full_scene:CH01|Stickman gestures respectfully toward a chalk-style sketch portrait on ivory ground."),
            ("Muốn biết nồi súp một nghìn lít mặn hay nhạt, bạn không cần húp hết cả nồi.", "concept_metaphor:none|A giant cooking pot outline steaming gently on ivory canvas, seventy percent negative space."),
            ("Bạn chỉ cần nếm đúng một muôi canh nhỏ.", "full_scene:CH01|Stickman holds a single soup ladle up to mouth with a smile on flat ivory background."),
            ("Nhưng điều kiện tiên quyết là: Nồi súp phải được khuấy thật đều.", "variation:CH01|Stickman grasps the ladle with both hands, ready to stir deep into the pot."),
        ],
    ),

    # ACT 2: Sampling Bias & The Stratified Solution (Scenes 4-7)
    (
        "Cái bẫy hớt váng và Google Form",
        SETTINGS_16X9[3],
        "analytical_crisp",
        "mechanistic_dissection",
        "problem",
        [
            ("Nếu bạn chỉ hớt lớp nước trên mặt, bạn sẽ nếm phải toàn váng mỡ.", "full_scene:CH01|Stickman skims only the surface grease of the soup pot with a frown of dissatisfaction on white surface."),
            ("Đây là sai lầm kinh điển của sinh viên khi làm nghiên cứu.", "variation:CH01|Stickman drops hands with an apologetic shrug on white field."),
            ("Bạn lập một cái Google Form rồi gửi vào năm mươi nhóm bạn bè trên mạng xã hội.", "full_scene:CH01|Stickman sits with laptop blasting survey links into floating social media chat icons."),
            ("Người điền phiếu toàn là bạn cùng lớp, cùng sở thích và cùng thói quen sinh hoạt.", "visual_diagram:none|A cluster of identical smiling student icons enclosed in a tight circle labeled 'BẠN THÂN' on white ground."),
            ("Trong thống kê, đó gọi là lấy mẫu tiện lợi và hoàn toàn bị lệch.", "white_card:none|A crisp white card with red stamped text 'LẤY MẪU TIỆN LỢI - VÔ GIÁ TRỊ VỚI QUẦN THỂ' on stark white canvas."),
        ],
    ),
    (
        "Khuấy đều và lấy mẫu phân tầng",
        SETTINGS_16X9[4],
        "analytical_crisp",
        "scientific_evidence",
        "causal_mechanism",
        [
            ("Để muôi súp có giá trị đại diện, người đầu bếp phải khuấy từ đáy lên mặt.", "full_scene:CH01|Stickman stirs the ladle deep into the soup pot, creating concentric swirling fluid lines on soft cream field."),
            ("Các nhà khoa học gọi kỹ thuật này là lấy mẫu phân tầng.", "visual_diagram:none|A clean diagram illustrating stratified layers with vertical and horizontal alignment brackets."),
            ("Quần thể sinh viên được chia thành các nhóm con độc lập và không chồng lấn.", "full_scene:CH01|Stickman points index finger to three distinct horizontal shelves labeled 'KHỐI NGÀNH', 'VÙNG MIỀN', 'LOẠI HÌNH'."),
            ("Mỗi nhóm con sẽ được rút mẫu ngẫu nhiên theo đúng tỷ lệ thực tế ngoài đời.", "variation:CH01|Stickman pulls sample dots proportionally from each shelf with calm precision."),
        ],
    ),
    (
        "Mô hình lát cắt đa ngành",
        SETTINGS_16X9[5],
        "analytical_crisp",
        "scientific_evidence",
        "causal_mechanism",
        [
            ("Ví dụ, một muôi súp sinh viên chuẩn mực phải có đủ ba thành phần.", "full_scene:CH01|Stickman presents a clear glass container showing three distinct neat layers on white diagram canvas."),
            ("Tầng một là sinh viên khối ngành kinh tế và xã hội.", "visual_diagram:none|A blue-tinted (#3B82C4) rectangular layer marked with a mortarboard and book icon."),
            ("Tầng hai là sinh viên khối kỹ thuật và công nghệ thông tin.", "full_scene:CH01|Stickman points to a green-tinted (#93A88C) rectangular layer marked with a cogwheel and circuit icon."),
            ("Tầng ba là sinh viên khối y dược và sức khỏe.", "visual_diagram:none|A coral-tinted (#F2B88B) rectangular layer marked with a medical cross and stethoscope icon."),
            ("Mỗi tầng đóng góp số lượng phiếu tương ứng với quy mô thực của trường.", "concept_metaphor:none|A small balance scale doodle in equilibrium, eighty percent negative space on white ground."),
        ],
    ),
    (
        "Lấy mẫu cụm nhiều giai đoạn",
        SETTINGS_16X9[6],
        "analytical_crisp",
        "scientific_evidence",
        "causal_mechanism",
        [
            ("Không ai có thể đi đến từng trường trong số sáu trăm trường đại học cả nước.", "full_scene:CH01|Stickman looks overwhelmed facing a vast grid of school building outlines on warm cream canvas."),
            ("Giải pháp tiết kiệm nhất là lấy mẫu cụm nhiều giai đoạn.", "full_scene:CH01|Stickman draws a branching tree structure on cream field with confident black marker strokes."),
            ("Giai đoạn một: Bốc thăm ngẫu nhiên năm tỉnh thành đại diện cho ba miền.", "visual_diagram:none|A minimalist Vietnam map outline highlighting five random dot clusters on cream background."),
            ("Giai đoạn hai: Trong mỗi tỉnh, bốc thăm ngẫu nhiên hai trường công và một trường tư.", "variation:CH01|Stickman circles two solid school squares and one outlined square on the province tree."),
            ("Giai đoạn ba: Chọn ngẫu nhiên sinh viên theo mã số sinh viên từ phòng đào tạo.", "visual_diagram:none|A random number generator icon picking five student ID numbers from a digital list."),
        ],
    ),

    # ACT 3: The 4-Tier Defensive Firewall Against Bad Data (Scenes 8-11)
    (
        "Tầng phòng thủ một: Thử nghiệm sơ bộ",
        SETTINGS_16X9[7],
        "analytical_crisp",
        "mechanistic_dissection",
        "explanation",
        [
            ("Một bộ câu hỏi dù được viết kỹ đến đâu cũng luôn chứa lỗi tiềm ẩn.", "full_scene:CH01|Stickman examines a long printed questionnaire with magnifying glass on pure white backdrop."),
            ("Tầng phòng thủ đầu tiên là nếm thử trước ba mươi bát.", "concept_metaphor:none|A row of thirty small test cups lined up neatly on white canvas, seventy-five percent open space."),
            ("Họ tiến hành khảo sát thử nghiệm trên một nhóm nhỏ từ ba mươi đến năm mươi người.", "full_scene:CH01|Stickman sits across a table interviewing a respondent with attentive posture."),
            ("Bước này giúp phát hiện ngay những câu hỏi dùng từ mơ hồ hoặc gây hiểu lầm.", "white_card:none|A white card showing a confusing sentence marked with red question marks and rewritten cleanly underneath."),
        ],
    ),
    (
        "Tầng phòng thủ hai: Bẫy câu hỏi đảo",
        SETTINGS_16X9[8],
        "analytical_crisp",
        "demystifying_truth",
        "explanation",
        [
            ("Nhiều người điền phiếu khảo sát chỉ để cho xong chuyện bằng cách tích toàn điểm năm.", "full_scene:CH01|Stickman mimics a bored respondent tapping straight down a vertical line of checkboxes without reading."),
            ("Để bóc trần điều này, nhà nghiên cứu cài các bẫy câu hỏi đảo ngược.", "concept_metaphor:none|A simple doodle outline of a harmless-looking box with a playful spring trap trigger on ivory surface."),
            ("Ví dụ, câu số năm hỏi: Tôi luôn cảm thấy tràn đầy năng lượng khi đến trường.", "full_scene:CH01|Stickman points to a white card displaying sentence 'CÂU 5: TÔI LUÔN TRÀN ĐẦY NĂNG LƯỢNG'."),
            ("Đến câu hai mươi hỏi: Tôi thường xuyên kiệt sức và muốn bỏ học mỗi sáng.", "white_card:none|White card displaying sentence 'CÂU 20: TÔI THƯỜNG XUYÊN KIỆT SỨC VÀ MUỐN BỎ HỌC'."),
            ("Nếu ai tích hoàn toàn đồng ý ở cả hai câu, hệ thống sẽ tự động gạch bỏ toàn bộ phiếu.", "variation:CH01|Stickman stamps a bold red cross stroke across the contradictory survey sheet with trash bin icon."),
        ],
    ),
    (
        "Tầng phòng thủ ba: Giám sát tọa độ và thời gian",
        SETTINGS_16X9[9],
        "analytical_crisp",
        "demystifying_truth",
        "explanation",
        [
            ("Khảo sát chuyên nghiệp không bao giờ giao việc rồi phó mặc cho số phận.", "full_scene:CH01|Stickman shakes head firmly, standing tall in center of white graphic field."),
            ("Người khảo sát thực địa được trang bị máy tính bảng có phần mềm chuyên dụng.", "full_scene:CH01|A field surveyor stickman holds a digital tablet displaying live interactive survey fields on white ground."),
            ("Phần mềm tự động ghi nhận tọa độ định vị vệ tinh tại thời điểm phỏng vấn.", "visual_diagram:none|A simple GPS satellite icon beaming a clean signal triangle down to a pinpointed campus coordinate."),
            ("Hệ thống đo chính xác thời gian hoàn thành từng phần của bảng hỏi.", "visual_diagram:none|A digital stopwatch timer showing minimum required duration bar of fifteen minutes."),
            ("Bất kỳ phiếu nào làm quá nhanh đều bị hủy bỏ vì vi phạm quy chuẩn.", "concept_metaphor:none|A stopwatch icon crossed out beside a red warning exclamation mark on white field."),
        ],
    ),
    (
        "Tầng phòng thủ bốn: Kiểm tra chéo độc lập",
        SETTINGS_16X9[10],
        "analytical_crisp",
        "demystifying_truth",
        "explanation",
        [
            ("Tầng phòng thủ cuối cùng là đội ngũ giám sát độc lập.", "full_scene:CH01|Stickman wears headphones at a workstation with a verified call log sheet on soft cream background."),
            ("Họ bốc ngẫu nhiên mười phần trăm số phiếu đã thu thập để gọi điện phúc tra.", "visual_diagram:none|A pie chart with a highlighted 10% slice pointing to a telephone icon on cream ground."),
            ("Giám sát viên sẽ hỏi lại ba câu ngẫu nhiên trong bài để đối chiếu câu trả lời.", "full_scene:CH01|Stickman speaks pleasantly into headset microphone while checking off matching bullet items."),
            ("Nếu phát hiện điều tra viên tự điền khống, toàn bộ lô khảo sát đó sẽ bị hủy ngay.", "concept_metaphor:none|A neat folder of survey forms stamped with 'HỦY BỎ DO KHAI KHỐNG' in crisp marker lettering."),
        ],
    ),

    # ACT 4: The Intelligent Escape Hatch for Students (Scenes 12-14)
    (
        "Ảo tưởng tài chính của sinh viên",
        SETTINGS_16X9[11],
        "reflective_slow",
        "gentle_lived_friction",
        "counter_argument",
        [
            ("Một quy trình lấy mẫu và thẩm định dữ liệu nghiêm ngặt tốn hàng trăm triệu đồng.", "full_scene:CH01|Stickman looks in awe at a tall stack of funding grants and equipment invoices on pure white canvas."),
            ("Bạn cần một đội ngũ cộng tác viên điều tra được đào tạo bài bản và trả thù lao đàng hoàng.", "visual_diagram:none|A small team of three stick figures carrying clipboards and ID badges walking in unison on white field."),
            ("Sinh viên chúng ta lấy đâu ra kinh phí và thời gian như vậy trong ba tháng?", "variation:CH01|Stickman turns empty pockets inside out with a funny helpless shrug on white canvas."),
            ("Cố gắng làm toàn quốc bằng sức mình chỉ dẫn bạn đến số liệu giả mạo.", "still_life:none|A single crumpled survey sheet lying abandoned on flat white ground with eighty percent open space."),
        ],
    ),
    (
        "Đứng trên vai người khổng lồ",
        SETTINGS_16X9[12],
        "analytical_crisp",
        "empowering_resolution",
        "takeaway",
        [
            ("Nhưng bạn không cần phải tuyệt vọng vì có một con đường sáng rực.", "full_scene:CH01|Stickman points toward a bright open doorway on warm cream ground."),
            ("Đó là khai thác nguồn dữ liệu thứ cấp đã được kiểm định quốc gia.", "concept_metaphor:none|An open digital vault icon overflowing with neat data spreadsheets on cream canvas, seventy percent open space."),
            ("Các cơ quan nhà nước và tổ chức quốc tế đã làm toàn bộ công đoạn thu mẫu cho bạn.", "full_scene:CH01|Stickman sits comfortably in an office chair typing with ease on a laptop keyboard."),
            ("Họ đã bỏ ra hàng tỷ đồng để làm sạch và hoàn thiện số liệu khoa học nhất.", "white_card:none|White card with logos of General Statistics Office and World Bank stamped in crisp clean line art."),
        ],
    ),
    (
        "Kho dữ liệu triệu dân miễn phí",
        SETTINGS_16X9[13],
        "analytical_crisp",
        "empowering_resolution",
        "takeaway",
        [
            ("Bạn có thể truy cập website Tổng cục Thống kê để tải bộ dữ liệu khảo sát mức sống dân cư.", "full_scene:CH01|Stickman navigates a browser screen showing official data repository tables with download icons on stark white backdrop."),
            ("Ngân hàng Thế giới cung cấp hoàn toàn miễn phí dữ liệu giáo dục và việc làm toàn cầu.", "visual_diagram:none|A world map graphic with radiating download lines connecting to student laptops across the globe."),
            ("Bạn chỉ cần tải file dữ liệu về, đặt câu hỏi nghiên cứu mới và chạy mô hình phân tích.", "full_scene:CH01|Stickman reviews an elegant regression analysis scatter plot on computer screen with focused pride."),
            ("Khi ra hội đồng, thầy cô sẽ khen ngợi bạn vì biết sử dụng nguồn dữ liệu mẫu mực.", "variation:CH01|Stickman stands confidently presenting data before nodding professors who applaud with wide smiles."),
        ],
    ),

    # ACT 5: Summary & Strategic Takeaway (Scenes 15-16)
    (
        "Ba nguyên tắc sống còn khi chọn mẫu",
        SETTINGS_16X9[14],
        "analytical_crisp",
        "empowering_resolution",
        "takeaway",
        [
            ("Để khép lại, hãy luôn khắc ghi ba nguyên tắc sống còn khi làm nghiên cứu.", "full_scene:CH01|Stickman points index finger to three bold numbered bullet points drawn on ivory neutral canvas."),
            ("Nguyên tắc một: Cỡ mẫu không quan trọng bằng cách thức chọn mẫu.", "white_card:none|A white card with bold marker text: '1. CÁCH CHỌN MẪU > SỐ LƯỢNG MẪU'."),
            ("Nguyên tắc hai: Làm sơ cấp thì chọn phạm vi thật hẹp và lấy số liệu thật.", "full_scene:CH01|Stickman points index finger firmly to the second rule on ivory ground."),
            ("Nguyên tắc ba: Muốn làm vĩ mô, hãy đứng trên vai dữ liệu thứ cấp có sẵn.", "white_card:none|A white card with bold marker text: '3. DIỆN RỘNG: KHAI THÁC DỮ LIỆU THỨ CẤP'."),
        ],
    ),
    (
        "Lời kết và chuyển giao hành động",
        SETTINGS_16X9[15],
        "narrative_warm",
        "empowering_resolution",
        "takeaway",
        [
            ("Khoa học chân chính bắt đầu từ sự trung thực với từng con số nhỏ.", "full_scene:CH01|Stickman stands tall with hand over heart, displaying a warm sincere expression on white concept field."),
            ("Đừng bao giờ để sự tham lam quy mô làm hỏng đi công trình tâm huyết của bạn.", "variation:CH01|Stickman offers a friendly thumbs-up with seventy percent open negative space."),
            ("Nếu bạn muốn nhận tài liệu hướng dẫn khai thác kho dữ liệu mở, hãy để lại bình luận bên dưới.", "full_scene:CH01|Stickman points downward toward the comment section with an inviting welcoming smile."),
            ("Bấm đăng ký kênh để cùng nhau giải mã những bài học nghiên cứu khoa học tiếp theo nhé!", "still_life:none|A clean doodle bell notification icon ringing beside a neat subscribe button, eighty percent negative space."),
        ],
    ),
]


def build_sources() -> list[dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "Sampling Techniques (3rd Edition)",
            "reference": "William G. Cochran (1977). John Wiley & Sons.",
            "facts": [
                "Chỉ cần bốn trăm người là đại diện cho cả triệu dân.",
                "Lấy mẫu phân tầng giúp số liệu chính xác hơn nhiều.",
                "Khảo sát trên mạng xã hội khiến mẫu bị lệch nghiêm trọng.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Research Design: Qualitative, Quantitative, and Mixed Methods Approaches",
            "reference": "John W. Creswell (2014). SAGE Publications.",
            "facts": [
                "Thử nghiệm trước giúp loại bỏ những câu hỏi mơ hồ.",
                "Dữ liệu thứ cấp có sẵn là cứu cánh cho đề tài lớn.",
                "Bẫy câu hỏi đảo bóc trần người điền tích bừa rất nhanh.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Six Easy Pieces: Essentials of Physics Explained by Its Most Brilliant Teacher",
            "reference": "Richard P. Feynman (1995). Basic Books.",
            "facts": [
                "Khoa học thực sự là giải thích việc lớn bằng điều giản dị.",
                "Nếm một muôi canh đại diện cho cả nồi súp khi khuấy đều.",
                "Làm trọn vẹn một việc nhỏ tốt hơn bỏ dở việc lớn.",
            ],
        },
    ]


def build_human_editorial() -> HumanEditorialSpec:
    return HumanEditorialSpec(
        topic_dilemmas=[
            "Người mới làm nghiên cứu lầm tưởng rằng dân số hàng triệu người thì bắt buộc phải khảo sát hàng chục nghìn phiếu, dẫn đến bế tắc và ngụy tạo số liệu.",
            "Lấy mẫu thuận tiện trên Facebook rồi tuyên bố là đại diện sinh viên toàn quốc khiến hội đồng đánh trượt vì vi phạm phương pháp luận căn bản.",
        ],
        dynamic_questions=[
            "Tại sao chỉ 400 người lại có thể đại diện chính xác cho 2 triệu dân cả nước?",
            "Làm thế nào để lấy mẫu diện rộng mà không cần ngân sách hàng trăm triệu đồng?",
            "Các Viện nghiên cứu cài bẫy bóc trần người điền khảo sát tích bừa như thế nào?",
        ],
        author_raw_input="Đừng cố gắng tự đi phát phiếu dạo toàn quốc bằng sức sinh viên. Hãy hiểu bản chất lấy mẫu phân tầng và đứng trên vai dữ liệu thứ cấp quốc gia.",
        editorial_stance="Quy mô mẫu lớn không bù đắp được cho phương pháp lấy mẫu sai. Khoa học trọng chất lượng và sự trung thực của mẫu hơn số lượng thô.",
        expanded_content_ideas=[
            {
                "idea_id": "IDEA_01",
                "angle_type": "analysis",
                "summary": "Giải mã toán học về đường cong sai số bão hòa tại n=400 qua định luật lợi ích cận biên giảm dần.",
                "narrative_integration": "Đưa vào phân cảnh nghịch lý bão hòa con số.",
                "target_narrative_phase": "hook",
            },
            {
                "idea_id": "IDEA_02",
                "angle_type": "commentary",
                "summary": "Mô phỏng 4 tầng phòng thủ chống số liệu rác của các dự án lớn: Pilot test, bẫy câu hỏi đảo, GPS và kiểm tra chéo 10%.",
                "narrative_integration": "Đưa vào phân cảnh hệ thống phòng thủ 4 tầng.",
                "target_narrative_phase": "explanation",
            },
            {
                "idea_id": "IDEA_03",
                "angle_type": "evaluation",
                "summary": "Hướng dẫn khai thác kho dữ liệu mở thứ cấp của Tổng cục Thống kê và World Bank như lối thoát cho sinh viên làm đề tài vĩ mô.",
                "narrative_integration": "Đưa vào phân cảnh đứng trên vai người khổng lồ.",
                "target_narrative_phase": "takeaway",
            },
        ],
    )


def build_characters() -> list[dict[str, Any]]:
    return [
        {
            "id": "CH01",
            "name": "Người que nghiên cứu",
            "role": "researcher",
            "appearance": CAST_APPEARANCE,
            "outfit": DEFAULT_OUTFIT,
        }
    ]


def build_topic_9x16() -> ResearchedTopic:
    story_tuples = [(title, setting, rows) for title, setting, _, _, _, rows in STORY_9X16]
    scenes = build_scenes_from_story_rows(story_tuples, character_id="CH01")
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = STORY_9X16[i][2]
        sc.spoken_style = STORY_9X16[i][3]
        sc.narrative_phase = STORY_9X16[i][4]

    # Assign source claims for 9x16 scenes
    scenes[0].source_ids = ["SRC01"]
    scenes[0].claim_facts = [
        ("Chỉ cần bốn trăm người, là đại diện được cho cả triệu dân.", "SRC01", "Chỉ cần bốn trăm người là đại diện cho cả triệu dân."),
    ]
    scenes[3].source_ids = ["SRC03"]
    scenes[3].claim_facts = [
        ("Nấu một nồi súp một nghìn lít, không ai húp hết cả nồi mới biết mặn nhạt.", "SRC03", "Nếm một muôi canh đại diện cho cả nồi súp khi khuấy đều."),
    ]
    scenes[5].source_ids = ["SRC01"]
    scenes[5].claim_facts = [
        ("Đó chính là sai lầm của sinh viên: Gửi link khảo sát vào mấy nhóm bạn bè trên Facebook.", "SRC01", "Khảo sát trên mạng xã hội khiến mẫu bị lệch nghiêm trọng."),
    ]
    scenes[7].source_ids = ["SRC01"]
    scenes[7].claim_facts = [
        ("Họ khuấy đều và múc phân tầng.", "SRC01", "Lấy mẫu phân tầng giúp số liệu chính xác hơn nhiều."),
    ]
    scenes[10].source_ids = ["SRC01"]
    scenes[10].claim_facts = [
        ("Chỉ cần bốn trăm người được chọn ngẫu nhiên chuẩn chỉ, sai số chỉ dưới năm phần trăm.", "SRC01", "Chỉ cần bốn trăm người là đại diện cho cả triệu dân."),
    ]
    scenes[13].source_ids = ["SRC02"]
    scenes[13].claim_facts = [
        ("Họ còn gọi điện ngẫu nhiên mười phần trăm số phiếu để kiểm tra xem có ai khai khống hay không.", "SRC02", "Bẫy câu hỏi đảo bóc trần người điền tích bừa rất nhanh."),
    ]
    scenes[15].source_ids = ["SRC02"]
    scenes[15].claim_facts = [
        ("Đừng lo, đây là vũ khí bí mật cho bạn: Dữ liệu thứ cấp.", "SRC02", "Dữ liệu thứ cấp có sẵn là cứu cánh cho đề tài lớn."),
    ]

    return ResearchedTopic(
        topic="Bí Mật 400 Người Đại Diện Cả Triệu Dân (Bản Dọc)",
        audience="Sinh viên đại học, học viên cao học và người mới bước vào nghiên cứu khoa học lướt video ngắn trên di động",
        goal="Giải thích bí mật khảo sát 400 người đại diện 2 triệu dân qua phép ẩn dụ nồi súp khổng lồ, kỹ thuật lấy mẫu phân tầng và lối thoát dữ liệu thứ cấp",
        video_type="research_explainer",
        min_duration=85.0,
        max_duration=145.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=build_sources(),
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _, _, _, _) in enumerate(STORY_9X16, 1)],
        characters=build_characters(),
        scenes=scenes,
        tone="Conversational Essayist dồn dập, gần gũi, bóc trần lầm tưởng",
        language="vi",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        human_editorial=build_human_editorial(),
        packaging=PackagingSpec(
            youtube_title="Bí Mật 400 Người Đại Diện Triệu Dân",
            visual_hook="Stickman đứng cạnh con số khổng lồ 2.000.000 và nhóm nhỏ 400 người, dấu hỏi cam nổi bật trên nền kem phẳng.",
            text_overlay="ĐẠI DIỆN TRIỆU DÂN",
            contrast_pair="Khảo sát bừa bãi bế tắc vs Lấy mẫu phân tầng chuẩn mực",
            channel_pillar=CHANNEL_PILLAR_RESEARCH_GUIDE,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "cách tính cỡ mẫu nckh",
                "lấy mẫu phân tầng",
                "bí mật nghiên cứu khoa học",
                "dữ liệu thứ cấp",
                "sai số mẫu khảo sát",
                "gso vhlss world bank",
            ],
            thumbnail_prompt=(
                "Orthographic 2D hand-drawn doodle poster. A minimalist bald circle-head stickman in solid "
                "cerulean-blue T-shirt (#3B82C4) standing between a giant number '2.000.000' and a tiny group '400'. "
                "Clean unshaded warm paper-cream canvas (#F8F0DC), bold wobbly black marker contours (#000000). "
                "Top shows big hand-lettered text 'ĐẠI DIỆN TRIỆU DÂN'. Zero 3D perspective, zero floor lines, "
                "zero room background, zero drop shadows, over 60% clean empty space."
            ),
        ),
    )


def build_topic_16x9() -> ResearchedTopic:
    story_tuples = [(title, setting, rows) for title, setting, _, _, _, rows in STORY_16X9]
    scenes = build_scenes_from_story_rows(story_tuples, character_id="CH01")
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = STORY_16X9[i][2]
        sc.spoken_style = STORY_16X9[i][3]
        sc.narrative_phase = STORY_16X9[i][4]

    # Assign source claims for 16x9 scenes
    scenes[0].source_ids = ["SRC01"]
    scenes[0].claim_facts = [
        ("Khảo sát bốn trăm người, là đại diện được cho cả triệu dân.", "SRC01", "Chỉ cần bốn trăm người là đại diện cho cả triệu dân."),
    ]
    scenes[2].source_ids = ["SRC03"]
    scenes[2].claim_facts = [
        ("Muốn biết nồi súp một nghìn lít mặn hay nhạt, bạn không cần húp hết cả nồi.", "SRC03", "Nếm một muôi canh đại diện cho cả nồi súp khi khuấy đều."),
    ]
    scenes[3].source_ids = ["SRC01"]
    scenes[3].claim_facts = [
        ("Trong thống kê, đó gọi là lấy mẫu tiện lợi và hoàn toàn bị lệch.", "SRC01", "Khảo sát trên mạng xã hội khiến mẫu bị lệch nghiêm trọng."),
    ]
    scenes[4].source_ids = ["SRC01"]
    scenes[4].claim_facts = [
        ("Các nhà khoa học gọi kỹ thuật này là lấy mẫu phân tầng.", "SRC01", "Lấy mẫu phân tầng giúp số liệu chính xác hơn nhiều."),
    ]
    scenes[7].source_ids = ["SRC02"]
    scenes[7].claim_facts = [
        ("Tầng phòng thủ đầu tiên là nếm thử trước ba mươi bát.", "SRC02", "Thử nghiệm trước giúp loại bỏ những câu hỏi mơ hồ."),
    ]
    scenes[8].source_ids = ["SRC02"]
    scenes[8].claim_facts = [
        ("Để bóc trần điều này, nhà nghiên cứu cài các bẫy câu hỏi đảo ngược.", "SRC02", "Bẫy câu hỏi đảo bóc trần người điền tích bừa rất nhanh."),
    ]
    scenes[12].source_ids = ["SRC02"]
    scenes[12].claim_facts = [
        ("Đó là khai thác nguồn dữ liệu thứ cấp đã được kiểm định quốc gia.", "SRC02", "Dữ liệu thứ cấp có sẵn là cứu cánh cho đề tài lớn."),
    ]

    return ResearchedTopic(
        topic="Bí Mật 400 Người Đại Diện Cả Triệu Dân: Cách Viện Nghiên Cứu Lấy Mẫu Không Tốn Sức",
        audience="Sinh viên đại học, học viên cao học, nghiên cứu viên và người làm khoa học",
        goal="Giải mã toán học và quy trình kỹ thuật lấy mẫu diện rộng cấp Viện/Bộ, mô hình phân tầng, 4 tầng phòng thủ chống số liệu rác và cách khai thác kho dữ liệu thứ cấp quốc gia",
        video_type="research_explainer",
        min_duration=360.0,
        max_duration=480.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        sources=build_sources(),
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _, _, _, _) in enumerate(STORY_16X9, 1)],
        characters=build_characters(),
        scenes=scenes,
        tone="Conversational Essayist điềm đạm, ấm áp, sâu sắc, lôi cuốn",
        language="vi",
        subtitles=False,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        human_editorial=build_human_editorial(),
        packaging=PackagingSpec(
            youtube_title="Bí Mật 400 Người Đại Diện Triệu Dân",
            visual_hook="Stickman đứng giữa hai con số 400 và 2.000.000, đồ thị sai số bão hòa và nồi súp khổng lồ trên nền kem phẳng.",
            text_overlay="ĐẠI DIỆN TRIỆU DÂN",
            contrast_pair="Khảo sát bừa bãi bế tắc vs Lấy mẫu phân tầng chuẩn mực",
            channel_pillar=CHANNEL_PILLAR_RESEARCH_GUIDE,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "cách tính cỡ mẫu nckh",
                "lấy mẫu phân tầng",
                "bí mật nghiên cứu khoa học",
                "dữ liệu thứ cấp",
                "sai số mẫu khảo sát",
                "gso vhlss world bank",
            ],
            thumbnail_prompt=(
                "Orthographic 2D hand-drawn doodle poster. A minimalist bald circle-head stickman in solid "
                "cerulean-blue T-shirt (#3B82C4) standing between a giant number '2.000.000' and a tiny group '400'. "
                "Clean unshaded warm paper-cream canvas (#F8F0DC), bold wobbly black marker contours (#000000). "
                "Top shows big hand-lettered text 'ĐẠI DIỆN TRIỆU DÂN'. Zero 3D perspective, zero floor lines, "
                "zero room background, zero drop shadows, over 60% clean empty space."
            ),
        ),
    )


def count_total_beats(scenes: List[ResearchedScene]) -> int:
    return sum(len(sc.visual_beats) for sc in scenes)


def export_package(topic: ResearchedTopic, out_dir: Path) -> dict[str, Any]:
    result = write_production_package(out_dir, topic, allow_active=True)
    draft_dir = out_dir / "draft"
    draft_dir.mkdir(parents=True, exist_ok=True)
    outline_data = {
        "outline": [
            {
                "scene_id": sc.scene_id,
                "purpose": sc.purpose,
                "requirements": list(sc.requirements),
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            }
            for sc in topic.scenes
        ]
    }
    (draft_dir / "outline.json").write_text(json.dumps(outline_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    content_text = (out_dir / "content.json").read_text(encoding="utf-8")
    (draft_dir / "content.json").write_text(content_text, encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Large-Scale Sampling 16:9 & 9:16 production blueprint.")
    parser.add_argument("--ratio", choices=["16:9", "9:16", "dual"], default="dual", help="Aspect ratio to build")
    parser.add_argument("--out-dir", type=Path, default=SYS_DIR / "runs", help="Output directory root")
    parser.add_argument("--blueprint-dir", type=Path, default=SYS_DIR / "content" / "blueprints", help="Blueprint directory root")
    args = parser.parse_args()

    ratios = ["16:9", "9:16"] if args.ratio == "dual" else [args.ratio]
    all_passed = True

    for r in ratios:
        if r == "16:9":
            topic = build_topic_16x9()
            job_name = "large-scale-sampling-16x9"
        else:
            topic = build_topic_9x16()
            job_name = "large-scale-sampling-9x16"

        targets = [args.out_dir / job_name]
        if args.blueprint_dir:
            targets.append(args.blueprint_dir / job_name)

        print("\n========================================================")
        print(f"[*] ĐANG XÂY DỰNG BỘ HỒ SƠ: {job_name} ({r})")
        print(f"    - Số phân cảnh: {len(topic.scenes)}")
        print(f"    - Tổng visual beats: {count_total_beats(topic.scenes)}")
        print(f"    - Visual Pacing: {topic.visual_pacing_profile}")

        for target_dir in targets:
            target_dir.mkdir(parents=True, exist_ok=True)
            res = export_package(topic, target_dir)
            print(f"  [+] Đã xuất gói tại: {target_dir}")
            print(f"      - brief.json: {res['brief_file']}")
            print(f"      - content.json: {res['content_file']}")
            print(f"      - script.json: {res['script_file']}")
            print(f"      - cadence_report.json: {res['cadence_file']}")
            print(f"      - SHA256: {res['brief_hash']}")

            cadence = res.get("cadence_report", {})
            print(f"  [*] Âm học: {cadence.get('total_duration', 0.0):.1f}s | "
                  f"Âm tiết: {cadence.get('total_actual_syllables')}/{cadence.get('total_target_syllables')} | "
                  f"Max drift: {cadence.get('max_drift', 0.0):.2f}s | Cảnh báo: {cadence.get('warnings_count', 0)}")

            if not res["valid_contracts"]:
                all_passed = False
                print(f"  [FAIL] Lỗi hợp đồng tại {target_dir}:")
                for err in res["contract_errors"]:
                    print(f"    - {err}")
            else:
                print("  [PASS] 100% HỢP LỆ theo Hợp đồng Schema 3.0 & Cadence Checker")

            diversity = res.get("diversity_report", {})
            if diversity.get("violations"):
                print("  [WARN] Phát hiện vi phạm diversity:")
                for v in diversity["violations"]:
                    print(f"    - {v}")

    print("\n========================================================")
    if all_passed:
        print("[SUCCESS] Toàn bộ gói hồ sơ kỹ thuật cho Large-Scale Sampling đã hoàn thành và đạt chuẩn!")
        return 0
    else:
        print("[FAILURE] Phát hiện lỗi trong quá trình đóng gói hồ sơ kỹ thuật.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
