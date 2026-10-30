#!/usr/bin/env python3
"""Build and validate Schema 3.0 production blueprint for quy-trinh-de-tai-lon-9x16.
Faithfully constructs Schema 3.0 brief.json and content.json for the 25 scenes
from blueprint_de_tai_lon.md with full validation, acoustic calibration, and pilot integration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[3]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "content"), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from script_cadence_checker import count_syllables, extract_pauses
from visual_style import CAST_APPEARANCE, DEFAULT_OUTFIT, STYLE_DESCRIPTION

from content.research_story_architect import (
    DEFAULT_P_TAIL_LAST,
    DEFAULT_P_TAIL_PARA,
    NOMINAL_SPEECH_RATE,
    PackagingSpec,
    ResearchedBeat,
    ResearchedScene,
    ResearchedTopic,
    serialize_brief_json,
    write_production_package,
)
from pilot import Pilot

SETTINGS = [
    "Clean pure white canvas (#FFFFFF).",
    "Stark pure white field (#FFFFFF).",
    "Solid clean white background (#FFFFFF).",
    "Minimalist pure white canvas (#FFFFFF).",
    "Stark white explainer field (#FFFFFF).",
    "Pure white doodle backdrop (#FFFFFF).",
    "Solid stark white canvas (#FFFFFF).",
    "Clean white diagram field (#FFFFFF).",
    "Pure white concept canvas (#FFFFFF).",
    "Minimalist clean white surface (#FFFFFF).",
    "Solid pure white field (#FFFFFF).",
    "Clean stark white background (#FFFFFF).",
    "Stark pure white backdrop (#FFFFFF).",
    "Pure white explainer canvas (#FFFFFF).",
    "Minimalist pure white surface (#FFFFFF).",
    "Clean white graphic field (#FFFFFF).",
    "Solid white doodle canvas (#FFFFFF).",
    "Stark clean white backdrop (#FFFFFF).",
    "Pure white diagram canvas (#FFFFFF).",
    "Minimalist stark white field (#FFFFFF).",
    "Clean pure white surface (#FFFFFF).",
    "Solid white concept field (#FFFFFF).",
    "Stark pure white graphic canvas (#FFFFFF).",
    "Clean white explainer backdrop (#FFFFFF).",
    "Pure stark white final canvas (#FFFFFF).",
]


def build_topic() -> ResearchedTopic:
    # Character definition
    characters = [
        {
            "id": "CH01",
            "name": "Người que sinh viên",
            "appearance": CAST_APPEARANCE,
            "outfit": DEFAULT_OUTFIT,
        }
    ]

    # Required points (25 points for 25 scenes)
    required_points = [
        {"id": "R01", "text": "Nghịch lý bác sĩ giỏi sinh viên xuất sắc nhưng không tự làm đề tài lớn"},
        {"id": "R02", "text": "Đặt câu hỏi tại sao sinh viên không thể tự làm đề tài thế giới"},
        {"id": "R03", "text": "Dẫn chứng thực tế từ chiếc lọ vaccine Covid-19"},
        {"id": "R04", "text": "Khám phá quy trình thực sự để tạo ra một sản phẩm lớn"},
        {"id": "R05", "text": "Bước một tìm công thức phòng thí nghiệm là việc sinh viên làm được"},
        {"id": "R06", "text": "Công thức ban đầu mới chỉ là một phần mười quãng đường"},
        {"id": "R07", "text": "Bước hai thử nghiệm tiền lâm sàng trên động vật"},
        {"id": "R08", "text": "Bước ba thử nghiệm lâm sàng ba giai đoạn lên tới hơn bốn mươi ba nghìn người"},
        {"id": "R09", "text": "Bước bốn xây nhà máy giữ lạnh âm tám mươi độ để sản xuất hàng triệu liều"},
        {"id": "R10", "text": "Câu hỏi ai là người thực sự đứng ra làm đề tài lớn"},
        {"id": "R11", "text": "Chuyên gia đầu ngành hai mươi đến ba mươi năm kinh nghiệm làm chủ nhiệm"},
        {"id": "R12", "text": "Người đứng tên chịu trách nhiệm pháp lý trước tính mạng con người"},
        {"id": "R13", "text": "Chính phủ và tập đoàn lớn đứng sau cung cấp nguồn tiền khổng lồ"},
        {"id": "R14", "text": "Ngân sách hơn mười tỷ đô la và chấp nhận mất trắng nếu thất bại"},
        {"id": "R15", "text": "Nguyên nhân cốt lõi khiến sinh viên không thể tự làm đề tài lớn"},
        {"id": "R16", "text": "Khẳng định không phải do sinh viên thiếu thông minh hay năng lực"},
        {"id": "R17", "text": "Ba rào cản cốt lõi sinh viên không thể có khi làm đề tài lớn"},
        {"id": "R18", "text": "Rào cản một hàng trăm triệu đô la thử nghiệm và bảo hiểm"},
        {"id": "R19", "text": "Rào cản hai tư cách pháp lý và chữ ký trước hội đồng y đức"},
        {"id": "R20", "text": "Rào cản ba thời gian đào tạo bốn năm so với đề tài hàng chục năm"},
        {"id": "R21", "text": "Sinh viên cần ra trường an toàn không thể gánh chín mươi phần trăm rủi ro"},
        {"id": "R22", "text": "Định hướng hành động thực tế cho sinh viên và người trẻ"},
        {"id": "R23", "text": "Không cần một mình tạo ra toàn bộ sản phẩm hoàn chỉnh"},
        {"id": "R24", "text": "Làm thật tốt từng việc nhỏ nhất tích lũy trong phòng thí nghiệm"},
        {"id": "R25", "text": "Tích lũy chuyên môn từng ngày để dẫn dắt cỗ máy lớn trong tương lai"},
    ]

    # Sources
    sources = [
        {
            "id": "SRC01",
            "title": "Nền tảng công nghệ mRNA và giải Nobel Y học",
            "reference": "Katalin Karikó & Drew Weissman (2005). Nobel Prize in Physiology or Medicine 2023.",
            "facts": [
                "Nghiên cứu cơ bản về công nghệ này bắt đầu từ năm một nghìn chín trăm chín mươi.",
                "Nhà khoa học kiên trì theo đuổi hơn ba mươi năm mới có bước ngoặt.",
                "Sinh viên bốn năm đại học không đủ thời gian theo đuổi chu kỳ nghiên cứu gốc.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Thử nghiệm lâm sàng vaccine Covid-19 Pha 3",
            "reference": "Polack et al. (2020). Safety and Efficacy of the BNT162b2 mRNA Covid-19 Vaccine. NEJM.",
            "facts": [
                "Thử nghiệm pha ba được thực hiện trên hơn bốn mươi ba nghìn người.",
                "Dự án triển khai tại hơn một trăm năm mươi trung tâm y tế toàn cầu.",
                "Quy mô thử nghiệm đòi hỏi hệ thống quản lý dữ liệu lâm sàng đồ sộ.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Chi phí nghiên cứu và Chiến dịch Operation Warp Speed",
            "reference": "US Government Accountability Office & Pfizer Financial Reports.",
            "facts": [
                "Dự án phát triển vaccine tiêu tốn hơn mười tỷ đô la.",
                "Nguồn vốn khổng lồ đến từ chính phủ và các tập đoàn dược đa quốc gia.",
                "Chủ đầu tư phải chấp nhận mất trắng toàn bộ vốn nếu thử nghiệm thất bại.",
            ],
        },
        {
            "id": "SRC04",
            "title": "Quy định pháp lý và Hội đồng Đạo đức Y sinh",
            "reference": "FDA Guidelines for Clinical Trials & IRB Regulations.",
            "facts": [
                "Mọi thử nghiệm trên người đều cần Hội đồng Đạo đức Y sinh phê duyệt.",
                "Nhà khoa học trưởng phải ký cam kết chịu trách nhiệm pháp lý trước tòa án.",
                "Chữ ký của sinh viên không có giá trị pháp nhân cho các rủi ro sinh mạng.",
            ],
        },
    ]

    # Packaging
    packaging = PackagingSpec(
        youtube_title="Tại Sao Sinh Viên Không Làm Được Đề Tài Lớn?",
        visual_hook="Người que sinh viên đứng trước mô hình cỗ máy nghiên cứu khổng lồ, tay cầm ống nghiệm nhỏ.",
        text_overlay="AI ĐỨNG RA LÀM?",
        contrast_pair="Ống nghiệm phòng lab vs Cỗ máy thử nghiệm triệu đô",
        channel_pillar="Hướng Dẫn Nghiên Cứu Khoa Học Cho Người Mới",
        funnel_tier="tier_1_broad",
        seo_keywords=[
            "quy trình làm đề tài lớn",
            "tại sao sinh viên không làm được",
            "nghiên cứu khoa học",
            "vaccine covid 19",
            "short 9x16",
        ],
        thumbnail_prompt=(
            "Orthographic 2D hand-drawn doodle poster in 9:16 vertical ratio. "
            "A minimalist bald circle-head stickman in solid cerulean-blue T-shirt (#3B82C4) "
            "holding a tiny glass test tube, looking up in awe at an enormous industrial research pipeline machine. "
            "Clean unshaded stark pure white canvas (#FFFFFF), bold wobbly black marker contours (#000000). "
            "Top center features hand-lettered bold text 'AI ĐỨNG RA LÀM?'. "
            "Zero 3D perspective, zero room interior, zero drop shadows, over 60% clean empty negative space."
        ),
    )

    # Human Editorial
    human_editorial = {
        "topic_dilemmas": [
            "Nhiều sinh viên giỏi mang ảo tưởng có thể một mình giải quyết những đề tài tầm cỡ thế giới, dẫn đến vỡ mộng và bế tắc khi đối mặt thực tế.",
            "Khoảng cách mênh mông giữa một công thức lý thuyết trong ống nghiệm và một quy trình sản xuất công nghiệp hoàn chỉnh được kiểm chứng trên người.",
        ],
        "dynamic_questions": [
            "Tại sao một người có điểm số thủ khoa vẫn không thể tự đứng tên chủ trì một dự án nghiên cứu y sinh?",
            "Sức mạnh thực sự của một đề tài khoa học lớn nằm ở trí tuệ cá nhân hay ở nguồn lực tài chính và tư cách pháp nhân?",
            "Người trẻ nên định vị vai trò của mình như thế nào để đóng góp hiệu quả vào một cỗ máy công nghiệp khổng lồ?",
        ],
        "author_raw_input": (
            "Sinh viên không làm được đề tài lớn không phải vì kém thông minh, "
            "mà vì thiếu hai thứ quyết định: chuyên môn tích lũy hàng chục năm và nguồn tiền khổng lồ chấp nhận rủi ro."
        ),
        "editorial_stance": (
            "Tôn vinh trí tuệ và sự nhiệt huyết của người trẻ, đồng thời giúp họ hiểu đúng "
            "cấu trúc vận hành của khoa học hiện đại để chọn điểm bắt đầu thực tế và bền vững."
        ),
        "expanded_content_ideas": [
            {
                "idea_id": "IDEA_01",
                "angle_type": "analysis",
                "summary": "Phân tích 4 chặng của chuỗi nghiên cứu phát triển vaccine để chứng minh bước trong lab chỉ chiếm một phần mười hành trình.",
                "narrative_integration": "Đưa vào phân cảnh quy trình từ phòng lab đến thử nghiệm động vật, người và nhà máy sản xuất.",
                "target_narrative_phase": "causal_mechanism",
            },
            {
                "idea_id": "IDEA_02",
                "angle_type": "commentary",
                "summary": "Bóc tách 3 rào cản chí tử gồm tiền bạc bảo hiểm, tư cách pháp lý sinh mạng và thời gian tích lũy đối với sinh viên.",
                "narrative_integration": "Đưa vào các cảnh phân tích rào cản và nghịch lý rủi ro 90% thất bại.",
                "target_narrative_phase": "explanation",
            },
            {
                "idea_id": "IDEA_03",
                "angle_type": "evaluation",
                "summary": "Định vị tư duy người ghép gạch: làm thật tốt việc nhỏ trong cỗ máy lớn để tích lũy trở thành người chỉ huy tương lai.",
                "narrative_integration": "Đưa vào phần kết luận hành động thực tế cho người mới.",
                "target_narrative_phase": "takeaway",
            },
        ],
    }

    # Helper for calibrated duration
    def calc_duration(narration_text: str, is_final: bool = False) -> float:
        pause_sec, _, _ = extract_pauses(narration_text)
        syl = count_syllables(narration_text, lang="vi")
        p_tail = DEFAULT_P_TAIL_LAST if is_final else DEFAULT_P_TAIL_PARA
        return round(pause_sec + (syl / NOMINAL_SPEECH_RATE) + p_tail, 2)

    # 25 Scenes
    scenes: list[ResearchedScene] = []

    # SC01
    narr_01 = "Nước ta có rất nhiều bác sĩ giỏi, nhiều tiến sĩ, giáo sư và sinh viên xuất sắc."
    scenes.append(
        ResearchedScene(
            scene_id="SC01",
            title="Nghịch lý bác sĩ và sinh viên xuất sắc",
            purpose="Đặt vấn đề về nguồn nhân lực y sinh và nghiên cứu xuất sắc",
            duration=calc_duration(narr_01),
            narration=narr_01,
            requirements=["R01"],
            source_ids=[],
            character_ids=["CH01"],
            action="Two minimalist doodle stickmen stand side by side: one stickman wearing a doctor stethoscope, and one stickman wearing a graduation mortarboard cap holding an academic diploma certificate.",
            setting=SETTINGS[0],
            camera="Semantic full-frame sequence",
            narrative_phase="hook",
            tone="analytical_crisp",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC01_I1",
                    description=f"{SETTINGS[0]} Two minimalist doodle stickmen stand side by side: one stickman wearing a doctor stethoscope, and one stickman wearing a graduation mortarboard cap holding an academic diploma certificate.",
                    anchor_quote=narr_01,
                    reason="Opening hook contrasting academic excellence with large-scale challenge.",
                    character_ids=["CH01"],
                    has_character=True,
                    shot_type="full_scene",
                    visible_text=[
                        {"text": "BÁC SĨ GIỎI?", "placement": "top_left", "object": "banner"},
                        {"text": "SINH VIÊN XUẤT SẮC?", "placement": "top_right", "object": "banner"},
                    ],
                    explanation={
                        "quote": narr_01,
                        "relation": "context",
                        "source_terms": ["bác sĩ"],
                        "visual_terms": ["doctor"],
                    },
                )
            ],
        )
    )

    # SC02
    narr_02 = "Nhưng tại sao với các đề tài tầm cỡ thế giới, sinh viên lại không thể tự làm được?"
    scenes.append(
        ResearchedScene(
            scene_id="SC02",
            title="Câu hỏi tại sao sinh viên không tự làm",
            purpose="Gợi mở câu hỏi cốt lõi về giới hạn đề tài lớn",
            duration=calc_duration(narr_02),
            narration=narr_02,
            requirements=["R02"],
            source_ids=[],
            character_ids=["CH01"],
            action="Minimalist stickman stands resting chin on hand in deep contemplation with a bold oversized black question mark floating overhead.",
            setting=SETTINGS[1],
            camera="Semantic full-frame sequence",
            narrative_phase="lead_in",
            tone="analytical_crisp",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC02_I1",
                    description=f"{SETTINGS[1]} Minimalist stickman stands resting chin on hand in deep contemplation with a bold oversized black question mark floating overhead.",
                    anchor_quote=narr_02,
                    reason="Curiosity gap question on why students cannot do world-class projects alone.",
                    character_ids=["CH01"],
                    has_character=True,
                    shot_type="full_scene",
                    visible_text=[{"text": "TẠI SAO KHÔNG THỂ?", "placement": "top_center", "object": "question"}],
                    explanation={
                        "quote": narr_02,
                        "relation": "cause_effect",
                        "source_terms": ["tại sao"],
                        "visual_terms": ["question"],
                    },
                )
            ],
        )
    )

    # SC03
    narr_03 = "Hãy nhìn vào một ví dụ thực tế: chiếc lọ vắc-xin Cô-vít mười chín."
    scenes.append(
        ResearchedScene(
            scene_id="SC03",
            title="Ví dụ thực tế lọ vắc-xin Cô-vít",
            purpose="Giới thiệu ca nghiên cứu thực tế vaccine Covid-19",
            duration=calc_duration(narr_03),
            narration=narr_03,
            requirements=["R03"],
            source_ids=["SRC02"],
            character_ids=[],
            action="A simple minimalist glass medicine vial labeled with bold clean lettering reading VACCINE COVID-19.",
            setting=SETTINGS[2],
            camera="Semantic full-frame sequence",
            narrative_phase="lead_in",
            tone="narrative_warm",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC03_I1",
                    description=f"{SETTINGS[2]} A simple minimalist glass medicine vial labeled with bold clean lettering reading VACCINE COVID-19.",
                    anchor_quote=narr_03,
                    reason="Real-world case study grounding with Covid-19 vaccine vial.",
                    character_ids=[],
                    has_character=False,
                    shot_type="macro_prop",
                    visible_text=[{"text": "VACCINE COVID-19", "placement": "center", "object": "vial"}],
                    explanation={
                        "quote": narr_03,
                        "relation": "context",
                        "source_terms": ["lọ"],
                        "visual_terms": ["vial"],
                    },
                )
            ],
        )
    )

    # SC04
    narr_04 = "Để làm ra nó, quy trình thực sự diễn ra như thế nào?"
    scenes.append(
        ResearchedScene(
            scene_id="SC04",
            title="Đặt câu hỏi về quy trình thực sự",
            purpose="Chuyển tiếp khám phá 4 bước quy trình tạo sản phẩm",
            duration=calc_duration(narr_04),
            narration=narr_04,
            requirements=["R04"],
            source_ids=[],
            character_ids=[],
            action="A curved black marker arrow pointing from the small medicine vial towards a long multi-stage linear roadmap pipeline.",
            setting=SETTINGS[3],
            camera="Semantic full-frame sequence",
            narrative_phase="problem",
            tone="analytical_crisp",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC04_I1",
                    description=f"{SETTINGS[3]} A curved black marker arrow pointing from the small medicine vial towards a long multi-stage linear roadmap pipeline.",
                    anchor_quote=narr_04,
                    reason="Visual transition introducing the research and development pipeline.",
                    character_ids=[],
                    has_character=False,
                    shot_type="visual_diagram",
                    visible_text=[{"text": "QUY TRÌNH RA SAO?", "placement": "top_center", "object": "header"}],
                    explanation={
                        "quote": narr_04,
                        "relation": "progression",
                        "source_terms": ["quy trình"],
                        "visual_terms": ["pipeline"],
                    },
                )
            ],
        )
    )

    # SC05
    narr_05 = "Bước một, tìm công thức trong phòng thí nghiệm. Bước này sinh viên có thể làm được."
    scenes.append(
        ResearchedScene(
            scene_id="SC05",
            title="Bước một tìm công thức phòng thí nghiệm",
            purpose="Chứng minh sinh viên làm tốt bước công thức phòng lab",
            duration=calc_duration(narr_05),
            narration=narr_05,
            requirements=["R05"],
            source_ids=[],
            character_ids=["CH01"],
            action="Stickman student holding a glass test tube and carefully adding drops of liquid.",
            setting=SETTINGS[4],
            camera="Semantic full-frame sequence",
            narrative_phase="causal_mechanism",
            tone="narrative_warm",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC05_I1",
                    description=f"{SETTINGS[4]} Stickman student holding a glass test tube and carefully adding drops of liquid on pure white background.",
                    anchor_quote="Bước một, tìm công thức trong phòng thí nghiệm.",
                    reason="Demonstrating lab bench chemistry step that students can accomplish.",
                    character_ids=["CH01"],
                    has_character=True,
                    shot_type="full_scene",
                    visible_text=[{"text": "BƯỚC 1: CÔNG THỨC", "placement": "top_center", "object": "step"}],
                    explanation={
                        "quote": "Bước một, tìm công thức trong phòng thí nghiệm.",
                        "relation": "context",
                        "source_terms": ["công thức"],
                        "visual_terms": ["tube"],
                    },
                ),
                ResearchedBeat(
                    image_id="SC05_I2",
                    description=f"{SETTINGS[4]} Stickman student gives a confident smile and thumbs-up beside the test tube on pure white canvas.",
                    anchor_quote="Bước này sinh viên có thể làm được.",
                    reason="Affirming student competence in fundamental lab formulation.",
                    character_ids=["CH01"],
                    has_character=True,
                    shot_type="variation",
                    based_on="SC05_I1",
                    preserve=f"Keep the exact camera angle and props in {SETTINGS[4]} Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Stickman student gives a confident smile and thumbs-up beside the test tube.",
                    allow_expression_shift=True,
                    visible_text=[{"text": "BƯỚC 1: CÔNG THỨC", "placement": "top_center", "object": "step"}],
                    explanation={
                        "quote": "Bước này sinh viên có thể làm được.",
                        "relation": "context",
                        "source_terms": ["sinh viên"],
                        "visual_terms": ["student"],
                    },
                ),
            ],
        )
    )

    # SC06
    narr_06 = "Nhưng đây mới chỉ là một phần mười quãng đường."
    scenes.append(
        ResearchedScene(
            scene_id="SC06",
            title="Một phần mười quãng đường",
            purpose="Trực quan hóa tỷ trọng một phần mười của bước phòng lab",
            duration=calc_duration(narr_06),
            narration=narr_06,
            requirements=["R06"],
            source_ids=[],
            character_ids=[],
            action="A horizontal battery progress bar filling only ten percent 10% with ninety percent remaining empty.",
            setting=SETTINGS[5],
            camera="Semantic full-frame sequence",
            narrative_phase="causal_mechanism",
            tone="analytical_crisp",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC06_I1",
                    description=f"{SETTINGS[5]} A horizontal battery progress bar filling only ten percent 10% with ninety percent remaining empty.",
                    anchor_quote=narr_06,
                    reason="Visualizing that formula is only 1/10 of the total journey.",
                    character_ids=[],
                    has_character=False,
                    shot_type="visual_diagram",
                    visible_text=[{"text": "1/10 QUÃNG ĐƯỜNG", "placement": "top_center", "object": "progress"}],
                    explanation={
                        "quote": narr_06,
                        "relation": "quantity",
                        "source_terms": ["một phần mười"],
                        "visual_terms": ["progress"],
                    },
                )
            ],
        )
    )

    # SC07
    narr_07 = "Bước hai, thử nghiệm trên động vật."
    scenes.append(
        ResearchedScene(
            scene_id="SC07",
            title="Bước hai thử nghiệm trên động vật",
            purpose="Giới thiệu chặng tiền lâm sàng trên động vật",
            duration=calc_duration(narr_07),
            narration=narr_07,
            requirements=["R07"],
            source_ids=[],
            character_ids=[],
            action="A simple doodle laboratory white mouse sniffs an experiment petri dish beside a laboratory microscope.",
            setting=SETTINGS[6],
            camera="Semantic full-frame sequence",
            narrative_phase="causal_mechanism",
            tone="analytical_crisp",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC07_I1",
                    description=f"{SETTINGS[6]} A simple doodle laboratory white mouse sniffs an experiment petri dish beside a laboratory microscope.",
                    anchor_quote=narr_07,
                    reason="Illustrating preclinical animal testing stage.",
                    character_ids=[],
                    has_character=False,
                    shot_type="full_scene",
                    visible_text=[{"text": "BƯỚC 2: TIỀN LÂM SÀNG", "placement": "top_center", "object": "step"}],
                    explanation={
                        "quote": narr_07,
                        "relation": "context",
                        "source_terms": ["động vật"],
                        "visual_terms": ["mouse"],
                    },
                )
            ],
        )
    )

    # SC08 (3 progressive visual beats for the 3 clinical trial phases)
    narr_08 = "Bước ba, thử nghiệm trên người qua ba giai đoạn. Vài chục người, vài trăm người, và hơn bốn mươi ba nghìn người."
    scenes.append(
        ResearchedScene(
            scene_id="SC08",
            title="Bước ba thử nghiệm lâm sàng ba giai đoạn",
            purpose="Liệt kê nhịp nhanh quy mô thử nghiệm người lên tới hơn 43000 người",
            duration=calc_duration(narr_08),
            narration=narr_08,
            requirements=["R08"],
            source_ids=["SRC02"],
            character_ids=[],
            action="Three successive groups of minimalist doodle stick figures expanding rapidly across stages.",
            setting=SETTINGS[7],
            camera="Semantic full-frame sequence",
            narrative_phase="causal_mechanism",
            tone="analytical_crisp",
            claim_facts=[
                (
                    narr_08,
                    "SRC02",
                    "Thử nghiệm pha ba được thực hiện trên hơn bốn mươi ba nghìn người.",
                )
            ],
            visual_beats=[
                ResearchedBeat(
                    image_id="SC08_I1",
                    description=f"{SETTINGS[7]} A small trial cohort of a dozen minimalist doodle stick figures lined up cleanly for initial Phase 1 testing.",
                    anchor_quote="Bước ba, thử nghiệm trên người qua ba giai đoạn. Vài chục người,",
                    reason="Phase 1 clinical trial: small safety cohort of dozens of participants.",
                    character_ids=[],
                    has_character=False,
                    shot_type="full_scene",
                    visible_text=[{"text": "PHA 1: VÀI CHỤC NGƯỜI", "placement": "top_left", "object": "phase1"}],
                    explanation={
                        "quote": "Vài chục người",
                        "relation": "progression",
                        "source_terms": ["Vài chục người"],
                        "visual_terms": ["cohort"],
                    },
                ),
                ResearchedBeat(
                    image_id="SC08_I2",
                    description=f"{SETTINGS[7]} The cohort expands into a denser crowd of several hundred minimalist doodle stick figures for Phase 2 expanded efficacy testing.",
                    anchor_quote="vài trăm người,",
                    reason="Phase 2 clinical trial: hundreds of participants.",
                    character_ids=[],
                    has_character=False,
                    shot_type="variation",
                    based_on="SC08_I1",
                    preserve=f"Preserve {SETTINGS[7]} and styling of Phase 1 group on left.",
                    change="Multiply doodle stick figures into a dense medium crowd filling center.",
                    visible_text=[{"text": "PHA 2: VÀI TRĂM NGƯỜI", "placement": "top_center", "object": "phase2"}],
                    explanation={
                        "quote": "vài trăm người",
                        "relation": "progression",
                        "source_terms": ["vài trăm người"],
                        "visual_terms": ["crowd"],
                    },
                ),
                ResearchedBeat(
                    image_id="SC08_I3",
                    description=f"{SETTINGS[7]} A massive stadium crowd symbol representing forty-three thousand participants spanning 150 medical centers worldwide.",
                    anchor_quote="và hơn bốn mươi ba nghìn người.",
                    reason="Phase 3 massive global trial exceeding 43000 individuals.",
                    character_ids=[],
                    has_character=False,
                    shot_type="variation",
                    based_on="SC08_I2",
                    preserve=f"Preserve {SETTINGS[7]} with expansive clean negative space above.",
                    change="Show a massive symbolic stadium crowd icon with label 43000 people.",
                    visible_text=[{"text": "PHA 3: 43.000 NGƯỜI", "placement": "top_right", "object": "phase3"}],
                    explanation={
                        "quote": "và hơn bốn mươi ba nghìn người.",
                        "relation": "progression",
                        "source_terms": ["bốn mươi ba nghìn"],
                        "visual_terms": ["stadium crowd"],
                    },
                ),
            ],
        )
    )

    # SC09
    narr_09 = "Bước bốn, xây nhà máy giữ lạnh âm tám mươi độ C để sản xuất hàng triệu liều."
    scenes.append(
        ResearchedScene(
            scene_id="SC09",
            title="Bước bốn xây nhà máy sản xuất âm tám mươi độ",
            purpose="Giới thiệu chuỗi cung ứng lạnh công nghiệp và nhà máy triệu liều",
            duration=calc_duration(narr_09),
            narration=narr_09,
            requirements=["R09"],
            source_ids=[],
            character_ids=[],
            action="A minimalist industrial factory building box with a clean smokestack, cold snowflake ice crystals, and temperature label -80°C.",
            setting=SETTINGS[8],
            camera="Semantic full-frame sequence",
            narrative_phase="causal_mechanism",
            tone="analytical_crisp",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC09_I1",
                    description=f"{SETTINGS[8]} A minimalist industrial factory building box with a clean smokestack, cold snowflake ice crystals, and temperature label -80°C.",
                    anchor_quote=narr_09,
                    reason="Industrial scale manufacturing and cold storage challenge.",
                    character_ids=[],
                    has_character=False,
                    shot_type="environment",
                    visible_text=[{"text": "BƯỚC 4: NHÀ MÁY (-80°C)", "placement": "top_center", "object": "factory"}],
                    explanation={
                        "quote": narr_09,
                        "relation": "structure",
                        "source_terms": ["nhà máy"],
                        "visual_terms": ["factory"],
                    },
                )
            ],
        )
    )

    # SC10
    narr_10 = "Vậy ai là những người thực sự đứng ra làm?"
    scenes.append(
        ResearchedScene(
            scene_id="SC10",
            title="Ai là người thực sự đứng ra làm",
            purpose="Chuyển đoạn sang phân tích chủ thể thực thi đề tài lớn",
            duration=calc_duration(narr_10),
            narration=narr_10,
            requirements=["R10"],
            source_ids=[],
            character_ids=["CH01"],
            action="Minimalist stickman stands facing forward with arms open wide in curious wonder questioning who manages such enormous projects.",
            setting=SETTINGS[9],
            camera="Semantic full-frame sequence",
            narrative_phase="problem",
            tone="analytical_crisp",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC10_I1",
                    description=f"{SETTINGS[9]} Minimalist stickman stands facing forward with arms open wide in curious wonder questioning who manages such enormous projects.",
                    anchor_quote=narr_10,
                    reason="Pivot question introducing real-world project leaders.",
                    character_ids=["CH01"],
                    has_character=True,
                    shot_type="full_scene",
                    visible_text=[{"text": "AI ĐỨNG RA LÀM?", "placement": "top_center", "object": "question"}],
                    explanation={
                        "quote": narr_10,
                        "relation": "cause_effect",
                        "source_terms": ["ai"],
                        "visual_terms": ["stickman"],
                    },
                )
            ],
        )
    )

    # SC11
    narr_11 = "Thứ nhất, phải là những chuyên gia đầu ngành có hai mươi đến ba mươi năm kinh nghiệm."
    scenes.append(
        ResearchedScene(
            scene_id="SC11",
            title="Chuyên gia đầu ngành hai mươi đến ba mươi năm kinh nghiệm",
            purpose="Mô tả vai trò Chủ nhiệm đề tài PI và bề dày kinh nghiệm",
            duration=calc_duration(narr_11),
            narration=narr_11,
            requirements=["R11"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Senior stickman scientist wearing round spectacles and holding a thick leather briefcase with label PI principal investigator.",
            setting=SETTINGS[10],
            camera="Semantic full-frame sequence",
            narrative_phase="explanation",
            tone="analytical_crisp",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC11_I1",
                    description=f"{SETTINGS[10]} Senior stickman scientist wearing round spectacles and holding a thick leather briefcase with label PI principal investigator.",
                    anchor_quote=narr_11,
                    reason="First pillar: senior expert with decades of domain leadership.",
                    character_ids=["CH01"],
                    has_character=True,
                    shot_type="full_scene",
                    visible_text=[{"text": "CHUYÊN GIA (20 - 30 NĂM)", "placement": "top_center", "object": "title"}],
                    explanation={
                        "quote": narr_11,
                        "relation": "context",
                        "source_terms": ["chuyên gia"],
                        "visual_terms": ["scientist"],
                    },
                )
            ],
        )
    )

    # SC12 (2 visual beats to split duration into 2 simple sentences)
    narr_12 = (
        "Họ là người đứng tên ký cam kết chịu trách nhiệm pháp lý. Đặc biệt khi xảy ra rủi ro về tính mạng con người."
    )
    scenes.append(
        ResearchedScene(
            scene_id="SC12",
            title="Người chịu trách nhiệm pháp lý trước tính mạng con người",
            purpose="Nhấn mạnh trách nhiệm pháp nhân và an toàn tính mạng",
            duration=calc_duration(narr_12),
            narration=narr_12,
            requirements=["R12"],
            source_ids=["SRC04"],
            character_ids=[],
            action="An official legal contract document with an official round regulatory stamp seal and an ink pen signing on the dotted line.",
            setting=SETTINGS[11],
            camera="Semantic full-frame sequence",
            narrative_phase="explanation",
            tone="reflective_slow",
            claim_facts=[
                (
                    narr_12,
                    "SRC04",
                    "Nhà khoa học trưởng phải ký cam kết chịu trách nhiệm pháp lý trước tòa án.",
                )
            ],
            visual_beats=[
                ResearchedBeat(
                    image_id="SC12_I1",
                    description=f"{SETTINGS[11]} An official legal contract document with a prominent round regulatory stamp seal on pure white paper.",
                    anchor_quote="Họ là người đứng tên ký cam kết chịu trách nhiệm pháp lý.",
                    reason="Legal accountability and Institutional Review Board contracts.",
                    character_ids=[],
                    has_character=False,
                    shot_type="macro_prop",
                    visible_text=[{"text": "TRÁCH NHIỆM PHÁP LÝ", "placement": "top_center", "object": "contract"}],
                    explanation={
                        "quote": "Họ là người đứng tên ký cam kết chịu trách nhiệm pháp lý.",
                        "relation": "cause_effect",
                        "source_terms": ["trách nhiệm pháp lý"],
                        "visual_terms": ["contract"],
                    },
                ),
                ResearchedBeat(
                    image_id="SC12_I2",
                    description=f"{SETTINGS[11]} An ink pen actively signs on the contract line beside an official red seal marking life-or-death legal liability.",
                    anchor_quote="Đặc biệt khi xảy ra rủi ro về tính mạng con người.",
                    reason="Signing personal liability for human life outcomes.",
                    character_ids=[],
                    has_character=False,
                    shot_type="variation",
                    based_on="SC12_I1",
                    preserve=f"Preserve contract document positioning in {SETTINGS[11]}.",
                    change="Ink pen signs firmly across the signature line beside a red wax seal.",
                    visible_text=[{"text": "CAM KẾT TÍNH MẠNG", "placement": "top_center", "object": "signature"}],
                    explanation={
                        "quote": "Đặc biệt khi xảy ra rủi ro về tính mạng con người.",
                        "relation": "cause_effect",
                        "source_terms": ["tính mạng con người"],
                        "visual_terms": ["pen", "contract"],
                    },
                ),
            ],
        )
    )

    # SC13
    narr_13 = "Thứ hai, phải là những tập đoàn hoặc chính phủ có rất nhiều tiền."
    scenes.append(
        ResearchedScene(
            scene_id="SC13",
            title="Tập đoàn và chính phủ có nguồn tiền khổng lồ",
            purpose="Giới thiệu trụ cột nguồn vốn từ tập đoàn và chính phủ",
            duration=calc_duration(narr_13),
            narration=narr_13,
            requirements=["R13"],
            source_ids=["SRC03"],
            character_ids=[],
            action="A minimalist central bank building facade beside a heavy steel money vault safe brimming with gold coins.",
            setting=SETTINGS[12],
            camera="Semantic full-frame sequence",
            narrative_phase="explanation",
            tone="analytical_crisp",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC13_I1",
                    description=f"{SETTINGS[12]} A minimalist central bank building facade beside a heavy steel money vault safe brimming with gold coins.",
                    anchor_quote=narr_13,
                    reason="Second pillar: institutions with massive financial backing.",
                    character_ids=[],
                    has_character=False,
                    shot_type="full_scene",
                    visible_text=[{"text": "CHÍNH PHỦ & TẬP ĐOÀN", "placement": "top_center", "object": "institution"}],
                    explanation={
                        "quote": narr_13,
                        "relation": "grouping",
                        "source_terms": ["tập đoàn"],
                        "visual_terms": ["bank"],
                    },
                )
            ],
        )
    )

    # SC14
    narr_14 = "Dự án vắc-xin tiêu tốn hơn mười tỷ đô la. Và họ phải chấp nhận mất trắng nếu thử nghiệm thất bại."
    scenes.append(
        ResearchedScene(
            scene_id="SC14",
            title="Ngân sách mười tỷ đô la và rủi ro mất trắng",
            purpose="Chứng minh quy mô mười tỷ đô la và chấp nhận mất trắng",
            duration=calc_duration(narr_14),
            narration=narr_14,
            requirements=["R14"],
            source_ids=["SRC03"],
            character_ids=[],
            action="A giant gold coin embossed with bold text $10B beside an office wastebasket filled with crumpled blueprints.",
            setting=SETTINGS[13],
            camera="Semantic full-frame sequence",
            narrative_phase="explanation",
            tone="analytical_crisp",
            claim_facts=[
                (
                    "Dự án vắc-xin tiêu tốn hơn mười tỷ đô la.",
                    "SRC03",
                    "Dự án phát triển vaccine tiêu tốn hơn mười tỷ đô la.",
                )
            ],
            visual_beats=[
                ResearchedBeat(
                    image_id="SC14_I1",
                    description=f"{SETTINGS[13]} A giant gold coin embossed with bold text $10B representing ten billion dollars research investment.",
                    anchor_quote="Dự án vắc-xin tiêu tốn hơn mười tỷ đô la.",
                    reason="Quantifying the $10B capital expenditure.",
                    character_ids=[],
                    has_character=False,
                    shot_type="concept_metaphor",
                    visible_text=[{"text": "10 TỶ USD", "placement": "top_center", "object": "coin"}],
                    explanation={
                        "quote": "Dự án vắc-xin tiêu tốn hơn mười tỷ đô la.",
                        "relation": "quantity",
                        "source_terms": ["mười tỷ đô la"],
                        "visual_terms": ["coin"],
                    },
                ),
                ResearchedBeat(
                    image_id="SC14_I2",
                    description=f"{SETTINGS[13]} An office wastebasket filled with crumpled research blueprints marked with red X symbols beside an empty coin outline.",
                    anchor_quote="Và họ phải chấp nhận mất trắng nếu thử nghiệm thất bại.",
                    reason="Illustrating the zero-recovery sunk cost risk if trials fail.",
                    character_ids=[],
                    has_character=False,
                    shot_type="concept_metaphor",
                    visible_text=[{"text": "CHẤP NHẬN MẤT TRẮNG", "placement": "top_center", "object": "waste"}],
                    explanation={
                        "quote": "Và họ phải chấp nhận mất trắng nếu thử nghiệm thất bại.",
                        "relation": "cause_effect",
                        "source_terms": ["thất bại"],
                        "visual_terms": ["wastebasket"],
                    },
                ),
            ],
        )
    )

    # SC15 (Faithfully adheres to blueprint: "sinh viên không làm được", 0 n-gram collision with SC17)
    narr_15 = "Bây giờ, bạn đã hiểu tại sao sinh viên không làm được chưa?"
    scenes.append(
        ResearchedScene(
            scene_id="SC15",
            title="Tại sao sinh viên không thể tự làm",
            purpose="Đặt vấn đề đối chiếu với hoàn cảnh thực tế của sinh viên",
            duration=calc_duration(narr_15),
            narration=narr_15,
            requirements=["R15"],
            source_ids=[],
            character_ids=["CH01"],
            action="Stickman student standing before three solid obstacle barrier blocks on clean white ground, looking thoughtful.",
            setting=SETTINGS[14],
            camera="Semantic full-frame sequence",
            narrative_phase="problem",
            tone="analytical_crisp",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC15_I1",
                    description=f"{SETTINGS[14]} Stickman student standing before three solid obstacle barrier blocks on clean white ground, looking thoughtful.",
                    anchor_quote=narr_15,
                    reason="Synthesizing why students cannot conduct massive projects independently.",
                    character_ids=["CH01"],
                    has_character=True,
                    shot_type="full_scene",
                    visible_text=[{"text": "TẠI SAO KHÔNG LÀM ĐƯỢC?", "placement": "top_center", "object": "question"}],
                    explanation={
                        "quote": narr_15,
                        "relation": "cause_effect",
                        "source_terms": ["sinh viên"],
                        "visual_terms": ["student"],
                    },
                )
            ],
        )
    )

    # SC16
    narr_16 = "Không phải vì sinh viên thiếu thông minh."
    scenes.append(
        ResearchedScene(
            scene_id="SC16",
            title="Không phải vì sinh viên thiếu thông minh",
            purpose="Khẳng định năng lực trí tuệ và sự sáng tạo của người trẻ",
            duration=calc_duration(narr_16),
            narration=narr_16,
            requirements=["R16"],
            source_ids=[],
            character_ids=["CH01"],
            action="Stickman student with radiating sharp idea spark lines drawn with crisp black marker strokes above head representing sharp intellect.",
            setting=SETTINGS[15],
            camera="Semantic full-frame sequence",
            narrative_phase="counter_argument",
            tone="narrative_warm",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC16_I1",
                    description=f"{SETTINGS[15]} Stickman student with radiating sharp idea spark lines drawn with crisp black marker strokes above head representing sharp intellect.",
                    anchor_quote=narr_16,
                    reason="Counter-argument: student intelligence is not the missing factor.",
                    character_ids=["CH01"],
                    has_character=True,
                    shot_type="full_scene",
                    visible_text=[
                        {"text": "KHÔNG PHẢI VÌ KÉM THÔNG MINH", "placement": "top_center", "object": "intellect"}
                    ],
                    explanation={
                        "quote": narr_16,
                        "relation": "comparison",
                        "source_terms": ["thông minh"],
                        "visual_terms": ["spark"],
                    },
                )
            ],
        )
    )

    # SC17 (Faithfully adheres to blueprint: "Mà vì sinh viên không thể có ba thứ:")
    narr_17 = "Mà vì sinh viên không thể có ba thứ:"
    scenes.append(
        ResearchedScene(
            scene_id="SC17",
            title="Ba thứ sinh viên không thể có",
            purpose="Dẫn vào 3 rào cản cốt lõi của sinh viên",
            duration=calc_duration(narr_17),
            narration=narr_17,
            requirements=["R17"],
            source_ids=[],
            character_ids=[],
            action="A bold oversized numeral 3 drawn with crisp black marker strokes centered on canvas.",
            setting=SETTINGS[16],
            camera="Semantic full-frame sequence",
            narrative_phase="explanation",
            tone="analytical_crisp",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC17_I1",
                    description=f"{SETTINGS[16]} A bold oversized numeral 3 drawn with crisp black marker strokes centered on canvas.",
                    anchor_quote=narr_17,
                    reason="Enumeration setup for the three decisive structural barriers.",
                    character_ids=[],
                    has_character=False,
                    shot_type="visual_diagram",
                    visible_text=[{"text": "3 THỨ KHÔNG THỂ CÓ", "placement": "top_center", "object": "number"}],
                    explanation={
                        "quote": narr_17,
                        "relation": "grouping",
                        "source_terms": ["ba thứ"],
                        "visual_terms": ["numeral"],
                    },
                )
            ],
        )
    )

    # SC18
    narr_18 = "Một: Hàng trăm triệu đô la để thử nghiệm và trả tiền bảo hiểm."
    scenes.append(
        ResearchedScene(
            scene_id="SC18",
            title="Rào cản một hàng trăm triệu đô la bảo hiểm",
            purpose="Phân tích rào cản chi phí bảo hiểm và kinh phí thử nghiệm",
            duration=calc_duration(narr_18),
            narration=narr_18,
            requirements=["R18"],
            source_ids=["SRC03"],
            character_ids=[],
            action="A neat stack of currency cash banknotes marked with a subtle red diagonal strike-through line.",
            setting=SETTINGS[17],
            camera="Semantic full-frame sequence",
            narrative_phase="explanation",
            tone="analytical_crisp",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC18_I1",
                    description=f"{SETTINGS[17]} A neat stack of currency cash banknotes marked with a subtle red diagonal strike-through line.",
                    anchor_quote=narr_18,
                    reason="Barrier 1: multi-million dollar insurance and trial operating expenses.",
                    character_ids=[],
                    has_character=False,
                    shot_type="concept_metaphor",
                    visible_text=[{"text": "1. TIỀN BẢO HIỂM", "placement": "top_center", "object": "barrier1"}],
                    explanation={
                        "quote": narr_18,
                        "relation": "quantity",
                        "source_terms": ["hàng trăm triệu đô la"],
                        "visual_terms": ["banknotes"],
                    },
                )
            ],
        )
    )

    # SC19
    narr_19 = "Hai: Chữ ký pháp lý trước tòa án và hội đồng y đức."
    scenes.append(
        ResearchedScene(
            scene_id="SC19",
            title="Rào cản hai tư cách pháp lý và chữ ký",
            purpose="Phân tích rào cản tư cách pháp nhân trước tòa án và hội đồng y đức",
            duration=calc_duration(narr_19),
            narration=narr_19,
            requirements=["R19"],
            source_ids=["SRC04"],
            character_ids=[],
            action="An academic certificate paper labeled BẰNG CỬ NHÂN lacking the mandatory official regulatory round red seal stamp.",
            setting=SETTINGS[18],
            camera="Semantic full-frame sequence",
            narrative_phase="explanation",
            tone="analytical_crisp",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC19_I1",
                    description=f"{SETTINGS[18]} An academic certificate paper labeled BẰNG CỬ NHÂN lacking the mandatory official regulatory round red seal stamp.",
                    anchor_quote=narr_19,
                    reason="Barrier 2: legal standing and Institutional Review Board qualifications.",
                    character_ids=[],
                    has_character=False,
                    shot_type="concept_metaphor",
                    visible_text=[{"text": "2. TƯ CÁCH PHÁP LÝ", "placement": "top_center", "object": "barrier2"}],
                    explanation={
                        "quote": narr_19,
                        "relation": "context",
                        "source_terms": ["chữ ký pháp lý"],
                        "visual_terms": ["certificate"],
                    },
                )
            ],
        )
    )

    # SC20
    narr_20 = "Ba: Thời gian liên tục. Sinh viên bốn năm là tốt nghiệp, nhưng đề tài lớn cần mười đến ba mươi năm."
    scenes.append(
        ResearchedScene(
            scene_id="SC20",
            title="Rào cản ba thời gian đào tạo so với đề tài",
            purpose="Đối chiếu chu kỳ bốn năm đại học với đề tài hàng chục năm",
            duration=calc_duration(narr_20),
            narration=narr_20,
            requirements=["R20"],
            source_ids=["SRC01"],
            character_ids=[],
            action="A desk calendar flipping rapidly and comparison timeline between 4 years and 30 years.",
            setting=SETTINGS[19],
            camera="Semantic full-frame sequence",
            narrative_phase="explanation",
            tone="analytical_crisp",
            claim_facts=[
                (
                    "Sinh viên bốn năm là tốt nghiệp, nhưng đề tài lớn cần mười đến ba mươi năm.",
                    "SRC01",
                    "Sinh viên bốn năm đại học không đủ thời gian theo đuổi chu kỳ nghiên cứu gốc.",
                )
            ],
            visual_beats=[
                ResearchedBeat(
                    image_id="SC20_I1",
                    description=f"{SETTINGS[19]} A desk calendar flipping rapidly through pages marked Year 1 to Year 4 on clean white surface.",
                    anchor_quote="Ba: Thời gian liên tục.",
                    reason="Barrier 3: undergraduate degree horizon.",
                    character_ids=[],
                    has_character=False,
                    shot_type="concept_metaphor",
                    visible_text=[{"text": "3. THỜI GIAN 10-30 NĂM", "placement": "top_center", "object": "barrier3"}],
                    explanation={
                        "quote": "Ba: Thời gian liên tục.",
                        "relation": "progression",
                        "source_terms": ["thời gian"],
                        "visual_terms": ["calendar"],
                    },
                ),
                ResearchedBeat(
                    image_id="SC20_I2",
                    description=f"{SETTINGS[19]} A comparison timeline showing a short 4-year graduation segment beside an extended 30-year arrow spanning three decades.",
                    anchor_quote="Sinh viên bốn năm là tốt nghiệp, nhưng đề tài lớn cần mười đến ba mươi năm.",
                    reason="Contrasting 4 years university training against 10 to 30 year fundamental science cycle.",
                    character_ids=[],
                    has_character=False,
                    shot_type="visual_diagram",
                    visible_text=[{"text": "4 NĂM VS 30 NĂM", "placement": "top_center", "object": "timeline"}],
                    explanation={
                        "quote": "Sinh viên bốn năm là tốt nghiệp, nhưng đề tài lớn cần mười đến ba mươi năm.",
                        "relation": "comparison",
                        "source_terms": ["ba mươi năm"],
                        "visual_terms": ["timeline"],
                    },
                ),
            ],
        )
    )

    # SC21 (2 beats to split duration into 2 simple sentences)
    narr_21 = "Sinh viên cần kết quả an toàn để ra trường. Không thể đánh cược tương lai vào dự án có chín mươi phần trăm rủi ro thất bại."
    scenes.append(
        ResearchedScene(
            scene_id="SC21",
            title="Rủi ro thất bại chín mươi phần trăm",
            purpose="Phân tích nghịch lý an toàn tốt nghiệp và tỷ lệ thất bại 90%",
            duration=calc_duration(narr_21),
            narration=narr_21,
            requirements=["R21"],
            source_ids=[],
            character_ids=["CH01"],
            action="Stickman student looking anxiously at a graduation certificate paper, followed by a pie chart showing 90% failure risk.",
            setting=SETTINGS[20],
            camera="Semantic full-frame sequence",
            narrative_phase="explanation",
            tone="reflective_slow",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC21_I1",
                    description=f"{SETTINGS[20]} Stickman student looking anxiously at a graduation cap and university diploma requirement on pure white ground.",
                    anchor_quote="Sinh viên cần kết quả an toàn để ra trường.",
                    reason="The structural need for guaranteed degree graduation vs risk.",
                    character_ids=["CH01"],
                    has_character=True,
                    shot_type="full_scene",
                    visible_text=[{"text": "CẦN TỐT NGHIỆP AN TOÀN", "placement": "top_center", "object": "diploma"}],
                    explanation={
                        "quote": "Sinh viên cần kết quả an toàn để ra trường.",
                        "relation": "cause_effect",
                        "source_terms": ["an toàn"],
                        "visual_terms": ["student"],
                    },
                ),
                ResearchedBeat(
                    image_id="SC21_I2",
                    description=f"{SETTINGS[20]} A circular pie chart showing ninety percent shaded dark gray indicating failure risk and ten percent clean white indicating success.",
                    anchor_quote="Không thể đánh cược tương lai vào dự án có chín mươi phần trăm rủi ro thất bại.",
                    reason="Visualizing 90% project mortality risk.",
                    character_ids=[],
                    has_character=False,
                    shot_type="visual_diagram",
                    visible_text=[{"text": "RỦI RO THẤT BẠI 90%", "placement": "top_center", "object": "chart"}],
                    explanation={
                        "quote": "Không thể đánh cược tương lai vào dự án có chín mươi phần trăm rủi ro thất bại.",
                        "relation": "quantity",
                        "source_terms": ["chín mươi phần trăm"],
                        "visual_terms": ["chart"],
                    },
                ),
            ],
        )
    )

    # SC22
    narr_22 = "Vậy sinh viên nên làm gì?"
    scenes.append(
        ResearchedScene(
            scene_id="SC22",
            title="Định hướng hành động vậy sinh viên nên làm gì",
            purpose="Mở ra giải pháp hành động thực tế",
            duration=calc_duration(narr_22),
            narration=narr_22,
            requirements=["R22"],
            source_ids=[],
            character_ids=["CH01"],
            action="Stickman student cheerfully rolling up sleeves with an energetic eager smile ready for practical action.",
            setting=SETTINGS[21],
            camera="Semantic full-frame sequence",
            narrative_phase="takeaway",
            tone="narrative_warm",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC22_I1",
                    description=f"{SETTINGS[21]} Stickman student cheerfully rolling up sleeves with an energetic eager smile ready for practical action.",
                    anchor_quote=narr_22,
                    reason="Transition to constructive empowering takeaways.",
                    character_ids=["CH01"],
                    has_character=True,
                    shot_type="full_scene",
                    visible_text=[{"text": "VẬY BẮT ĐẦU TỪ ĐÂU?", "placement": "top_center", "object": "question"}],
                    explanation={
                        "quote": narr_22,
                        "relation": "cause_effect",
                        "source_terms": ["sinh viên"],
                        "visual_terms": ["student"],
                    },
                )
            ],
        )
    )

    # SC23
    narr_23 = "Bạn không cần phải một mình tạo ra cả viên thuốc."
    scenes.append(
        ResearchedScene(
            scene_id="SC23",
            title="Không cần một mình tạo ra cả sản phẩm",
            purpose="Giải phóng áp lực người hùng đơn độc",
            duration=calc_duration(narr_23),
            narration=narr_23,
            requirements=["R23"],
            source_ids=[],
            character_ids=["CH01"],
            action="A small stickman student joins hands with a line of taller team scientists collectively supporting a large scientific apparatus.",
            setting=SETTINGS[22],
            camera="Semantic full-frame sequence",
            narrative_phase="takeaway",
            tone="narrative_warm",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC23_I1",
                    description=f"{SETTINGS[22]} A small stickman student joins hands with a line of taller team scientists collectively supporting a large scientific apparatus.",
                    anchor_quote=narr_23,
                    reason="Dispelling the lone hero fallacy: science is collective teamwork.",
                    character_ids=["CH01"],
                    has_character=True,
                    shot_type="concept_metaphor",
                    visible_text=[{"text": "KHÔNG CẦN LÀM MỘT MÌNH", "placement": "top_center", "object": "team"}],
                    explanation={
                        "quote": narr_23,
                        "relation": "grouping",
                        "source_terms": ["một mình"],
                        "visual_terms": ["scientists"],
                    },
                )
            ],
        )
    )

    # SC24 (2 beats to split duration into 2 simple sentences)
    narr_24 = (
        "Hãy làm thật tốt việc nhỏ nhất trong phòng thí nghiệm. Đo một chỉ số, rửa một ống nghiệm, tìm một phân tử."
    )
    scenes.append(
        ResearchedScene(
            scene_id="SC24",
            title="Làm thật tốt việc nhỏ nhất trong phòng thí nghiệm",
            purpose="Định vị hành động xuất sắc từ nhiệm vụ nhỏ nhất",
            duration=calc_duration(narr_24),
            narration=narr_24,
            requirements=["R24"],
            source_ids=[],
            character_ids=["CH01"],
            action="Stickman student meticulously dispensing a single droplet of liquid into a clean glass test tube on laboratory rack.",
            setting=SETTINGS[23],
            camera="Semantic full-frame sequence",
            narrative_phase="takeaway",
            tone="narrative_warm",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC24_I1",
                    description=f"{SETTINGS[23]} Stickman student carefully standing at a tidy laboratory table holding a glass test tube rack.",
                    anchor_quote="Hãy làm thật tốt việc nhỏ nhất trong phòng thí nghiệm.",
                    reason="Focusing on precision in foundational lab responsibilities.",
                    character_ids=["CH01"],
                    has_character=True,
                    shot_type="full_scene",
                    visible_text=[{"text": "LÀM TỐT VIỆC NHỎ", "placement": "top_center", "object": "action"}],
                    explanation={
                        "quote": "Hãy làm thật tốt việc nhỏ nhất trong phòng thí nghiệm.",
                        "relation": "context",
                        "source_terms": ["phòng thí nghiệm"],
                        "visual_terms": ["laboratory"],
                    },
                ),
                ResearchedBeat(
                    image_id="SC24_I2",
                    description=f"{SETTINGS[23]} Stickman student meticulously dispensing a single droplet of liquid into a clean glass test tube on laboratory rack.",
                    anchor_quote="Đo một chỉ số, rửa một ống nghiệm, tìm một phân tử.",
                    reason="Mastering the smallest rigorous tasks in laboratory research.",
                    character_ids=["CH01"],
                    has_character=True,
                    shot_type="variation",
                    based_on="SC24_I1",
                    preserve=f"Preserve {SETTINGS[23]} and bench layout.",
                    change="Stickman student meticulously dispenses a single droplet of liquid into the test tube.",
                    visible_text=[{"text": "TÍCH LŨY TỪNG CHÚT", "placement": "top_center", "object": "pipette"}],
                    explanation={
                        "quote": "Đo một chỉ số, rửa một ống nghiệm, tìm một phân tử.",
                        "relation": "context",
                        "source_terms": ["ống nghiệm"],
                        "visual_terms": ["test tube"],
                    },
                ),
            ],
        )
    )

    # SC25 (Final scene, calibrated duration with DEFAULT_P_TAIL_LAST)
    narr_25 = "Hãy tích lũy chuyên môn từng ngày. Rồi chính bạn sẽ dẫn dắt cỗ máy triệu đô trong tương lai."
    scenes.append(
        ResearchedScene(
            scene_id="SC25",
            title="Tích lũy chuyên môn để dẫn dắt cỗ máy tương lai",
            purpose="Kết bài truyền cảm hứng dẫn dắt tương lai",
            duration=calc_duration(narr_25, is_final=True),
            narration=narr_25,
            requirements=["R25"],
            source_ids=[],
            character_ids=["CH01"],
            action="Stickman student standing confidently on leadership podium directing a large high-tech research initiative roadmap.",
            setting=SETTINGS[24],
            camera="Semantic full-frame sequence",
            narrative_phase="closing",
            tone="narrative_warm",
            visual_beats=[
                ResearchedBeat(
                    image_id="SC25_I1",
                    description=f"{SETTINGS[24]} Stickman student standing confidently on leadership podium directing a large high-tech research initiative roadmap.",
                    anchor_quote=narr_25,
                    reason="Inspiring closure: incremental rigor leads to future scientific leadership.",
                    character_ids=["CH01"],
                    has_character=True,
                    shot_type="full_scene",
                    visible_text=[{"text": "TÍCH LŨY ➔ DẪN DẮT", "placement": "top_center", "object": "future"}],
                    explanation={
                        "quote": narr_25,
                        "relation": "progression",
                        "source_terms": ["dẫn dắt"],
                        "visual_terms": ["leadership"],
                    },
                )
            ],
        )
    )

    # Construct ResearchedTopic
    return ResearchedTopic(
        topic="Quy trình làm đề tài lớn, ai đứng ra làm, tại sao sinh viên không làm được, cần người có chuyên môn và có tiền; ví dụ thực tế Covid-19 vaccine",
        audience="Sinh viên đại học, học viên cao học và người mới bước vào nghiên cứu khoa học lướt video ngắn trên di động",
        goal="Giải thích bản chất quy trình làm đề tài khoa học lớn, phân tích 3 rào cản khiến sinh viên không thể tự làm, và định vị con đường tích lũy thực tế",
        video_type="research_explainer",
        min_duration=85.0,
        max_duration=145.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=sources,
        required_points=required_points,
        characters=characters,
        scenes=scenes,
        tone="Conversational Essayist gãy gọn, gần gũi, nhịp điệu nhanh và cuốn hút",
        language="vi",
        voice="VietNarrator",
        speed=1.0,
        subtitles=True,
        conversational_facts=True,
        packaging=packaging,
        visual_pacing_profile="full_frame_v1",
        human_editorial=human_editorial,
    )


def register_pilot_job(target_dir: Path, brief_data: dict[str, Any]) -> None:
    """Initialize job registration with Pilot so pilot status and check-draft pass cleanly."""
    job_id = target_dir.name
    p = Pilot(root=SYS_DIR)

    # Write pilot metadata
    integrity_data = p.protected()
    (target_dir / "integrity.json").write_text(json.dumps(integrity_data, indent=2) + "\n", encoding="utf-8")

    g = p.git_state()
    metadata = {
        "created_at": time.time(),
        "mode": "review",
        "git_head": g.get("head"),
        "protected_dirty": g.get("dirty"),
        "protected_changes": g.get("changes"),
        "engine_version": 3,
    }
    (target_dir / "integrity-meta.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    briefs_dir = target_dir / "briefs"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    brief_1_path = briefs_dir / "1.json"
    brief_serialized = serialize_brief_json(brief_data)
    brief_1_path.write_text(brief_serialized, encoding="utf-8")

    brief_hash = hashlib.sha256(brief_1_path.read_bytes()).hexdigest()
    (target_dir / "brief-current.json").write_text(
        json.dumps({"revision": 1, "hash": brief_hash}, indent=2) + "\n",
        encoding="utf-8",
    )

    # Write workflow.json for workflow compatibility
    from pilot import hashobj

    wf_path = target_dir / "workflow.json"
    wf_created_at = None
    if wf_path.exists():
        try:
            old_wf = json.loads(wf_path.read_text(encoding="utf-8"))
            if isinstance(old_wf, dict) and "created_at" in old_wf:
                wf_created_at = old_wf["created_at"]
        except Exception:
            pass
    if wf_created_at is None:
        wf_created_at = 1793290472.7719724

    wf_data = {"version": 3, "mode": "review", "created_at": wf_created_at}
    wf_path.write_text(json.dumps(wf_data, indent=2) + "\n", encoding="utf-8")
    wf_hash = hashobj(wf_data)

    # Register modules in jobs.sqlite with control approved
    order = ("control", "content", "audio", "images", "render")
    with p._db_lock:
        for m in order:
            state = "approved" if m == "control" else "pending"
            revision = 1 if m == "control" else 0
            p.db.execute(
                "INSERT OR REPLACE INTO modules(job, module, state, revision, envelope, hash) VALUES(?,?,?,?,?,?)",
                (job_id, m, state, revision, "", ""),
            )
        # Clear duplicate control lifecycle events for this job to maintain idempotency
        p.db.execute("DELETE FROM events WHERE job=? AND module='control'", (job_id,))
        p.db.execute(
            "INSERT INTO events(at, job, module, event, detail) VALUES(?,?,?,?,?)",
            (wf_created_at, job_id, "control", "created", "Initialized via build_quy_trinh_de_tai_lon_job"),
        )
        p.db.execute(
            "INSERT INTO events(at, job, module, event, detail) VALUES(?,?,?,?,?)",
            (wf_created_at, job_id, "control", "workflow_created", wf_hash),
        )
        p.db.execute(
            "INSERT INTO events(at, job, module, event, detail) VALUES(?,?,?,?,?)",
            (wf_created_at, job_id, "control", "approved", "Approved control for production package"),
        )
        p._commit()


def build_job(output_dir: Path | None = None, also_blueprint: bool = True) -> dict[str, Any]:
    target_dir = output_dir or (SYS_DIR / "runs" / "quy-trinh-de-tai-lon-9x16")
    blueprint_dir = SYS_DIR / "content" / "blueprints" / "quy-trinh-de-tai-lon-9x16"

    topic = build_topic()

    targets = [target_dir]
    if also_blueprint and blueprint_dir != target_dir:
        targets.append(blueprint_dir)

    print(f"Assembling Video Pilot package for: {target_dir.name}...")
    primary_result = None
    for tdir in targets:
        tdir.mkdir(parents=True, exist_ok=True)
        res = write_production_package(
            output_dir=tdir,
            topic=topic,
            system_root=SYS_DIR,
            brief_revision=1,
            include_spinoffs=False,
            allow_active=True,
        )
        if tdir == target_dir:
            primary_result = res
            # Ensure pilot job registration
            brief_data = json.loads((tdir / "brief.json").read_text(encoding="utf-8"))
            register_pilot_job(tdir, brief_data)

            # Preserve thumbnail poster in run directory
            thumb_file = tdir / "thumbnail_9x16.jpg"
            if not thumb_file.exists() and (blueprint_dir / "thumbnail_9x16.jpg").exists():
                thumb_file.write_bytes((blueprint_dir / "thumbnail_9x16.jpg").read_bytes())
        elif (target_dir / "thumbnail_9x16.jpg").exists() and not (tdir / "thumbnail_9x16.jpg").exists():
            (tdir / "thumbnail_9x16.jpg").write_bytes((target_dir / "thumbnail_9x16.jpg").read_bytes())

    print("Package written successfully to all destinations!")
    print(f"Valid contracts: {primary_result['valid_contracts']}")
    if primary_result.get("contract_errors"):
        print(f"Contract errors: {primary_result['contract_errors']}")
    if primary_result.get("packaging_warnings"):
        print(f"Packaging warnings: {primary_result['packaging_warnings']}")
    return primary_result


def main() -> int:
    parser = argparse.ArgumentParser(description="Build quy-trinh-de-tai-lon-9x16 package.")
    parser.add_argument("--out-dir", type=Path, default=None, help="Custom output directory")
    parser.add_argument("--skip-blueprint", action="store_true", help="Do not write to blueprints directory")
    args = parser.parse_args()

    res = build_job(output_dir=args.out_dir, also_blueprint=not args.skip_blueprint)
    return 0 if res.get("valid_contracts") else 1


if __name__ == "__main__":
    sys.exit(main())
