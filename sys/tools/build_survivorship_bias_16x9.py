#!/usr/bin/env python3
"""Build and validate the Schema 3.0 production blueprint for survivorship-bias-16x9."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content.research_story_architect import (  # noqa: E402
    DEFAULT_CHANNEL_PILLAR,
    DEFAULT_P_TAIL_LAST,
    DEFAULT_P_TAIL_PARA,
    NOMINAL_SPEECH_RATE,
    PackagingSpec,
    ResearchedBeat,
    ResearchedScene,
    ResearchedTopic,
    build_brief_v3,
    build_content_v3,
    check_conversational_spoken_facts,
    check_packaging_and_localization,
    compute_brief_hash,
    generate_script_json,
    serialize_brief_json,
    validate_production_bundle,
)
from explainer_contract import (  # noqa: E402
    validate_clearance_and_labels,
    validate_explanations,
    validate_human_editorial,
    validate_short,
)
from flow_prompts import compile as compile_flow_prompt  # noqa: E402
from script_cadence_checker import (  # noqa: E402
    ScriptCadenceChecker,
    count_syllables,
    extract_pauses,
)
from script_diversity_linter import clean_sentence, lint_script  # noqa: E402
from scripts.story_plan import estimates  # noqa: E402
from visual_style import CAST_APPEARANCE, DEFAULT_OUTFIT, STYLE_DESCRIPTION  # noqa: E402
from vn_text_normalizer import detect_unnormalized_tokens, normalize_for_tts  # noqa: E402

# 12 scenes covering the 8-stage narrative arc and 4 macro cognitive phases:
# Phase 1 (lived_friction: hook, lead_in): SC01, SC02, SC03
# Phase 2 (empirical_conflict: problem, causal_mechanism): SC04, SC05, SC06
# Phase 3 (structural_model: explanation, counter_argument): SC07, SC08, SC09
# Phase 4 (actionable_resolution: takeaway, closing): SC10, SC11, SC12

STORY_SCENES: List[Dict[str, Any]] = [
    {
        "scene_id": "SC01",
        "title": "Cái bẫy của những công thức thành công",
        "purpose": "Mở bài bằng cú tát nhận thức: mọi lời khuyên thành công trên mạng đều đang giấu nhẹm một nửa sự thật",
        "setting": "Flat warm paper-cream (#F8F0DC) 2D orthographic bedroom stage.",
        "narrative_phase": "hook",
        "tone": "narrative_warm",
        "requirements": ["R01"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Mọi lời khuyên thành công",
                "still_life|Flat 2D orthographic card on a warm paper-cream (#F8F0DC) field: a golden trophy cup shining on a pedestal beside a stack of self-help books.",
                "thành công",
                "golden trophy cup shining on a pedestal",
                "context",
            ),
            (
                "trên mạng đều đang giấu nhẹm",
                "still_life|Flat 2D orthographic card on an apricot-peach (#F2B88B) field: a heavy black stage curtain pulled halfway across a bright screen with a red lock.",
                "giấu nhẹm",
                "heavy black stage curtain pulled halfway across",
                "comparison",
            ),
            (
                "bạn một nửa sự thật. Đi làm",
                "visual_diagram|Flat 2D orthographic card on a stark pure-white (#FFFFFF) canvas: a round pie chart sliced in half with one bright yellow half and one pitch-black hidden half.",
                "một nửa sự thật",
                "round pie chart sliced in half",
                "quantity",
                [
                    {"text": "MỘT NỬA SỰ THẬT", "placement": "above round pie chart", "object": "round pie chart"},
                ],
            ),
            (
                "cả tháng lương vừa nhận",
                "still_life|Flat 2D close-up on a warm paper-cream (#F8F0DC) field: a paper monthly payslip envelope stamped with a small green paycheck number.",
                "tháng lương",
                "paper monthly payslip envelope",
                "context",
            ),
            (
                "đã hết, tối nằm lướt điện",
                "full_scene|Flat 2D side-on orthographic bedroom on a slate-navy (#2E4361) night stage: the white-head doodle stickman in a casual cerulean blue shirt (#3B82C4) lies on a flat bed holding a smartphone.",
                "lướt điện",
                "lies on a flat bed holding a smartphone",
                "context",
            ),
            (
                "thoại, bạn liên tục thấy",
                "still_life|Flat 2D close-up on an apricot-peach (#F2B88B) field: a bright vertical smartphone feed scrolling through three video frames with gold coins.",
                "liên tục thấy",
                "bright vertical smartphone feed scrolling",
                "context",
            ),
            (
                "người trạc tuổi mình khoe",
                "full_scene|Flat 2D orthographic frame on a warm paper-cream (#F8F0DC) field: a young presenter white-head doodle stickman in a dark blazer and star badge points to a luxury car.",
                "người trạc tuổi",
                "young presenter white-head doodle stickman in a dark blazer",
                "context",
            ),
            (
                "tự do tài chính, nghỉ việc",
                "still_life|Flat 2D close-up on a pale ice-blue (#CBE0E0) field: an office lanyard badge tossed into a small wire bin beside a golden beach umbrella icon.",
                "nghỉ việc",
                "office lanyard badge tossed into a small wire bin",
                "cause_effect",
                [
                    {"text": "TỰ DO TÀI CHÍNH", "placement": "above golden beach umbrella icon", "object": "golden beach umbrella icon"},
                ],
            ),
            (
                "ra làm riêng kiếm hàng trăm",
                "still_life|Flat 2D orthographic close-up on a soft sage-green (#93A88C) field: three thick stacks of green banknotes tied with crisp paper bands.",
                "kiếm hàng trăm",
                "three thick stacks of green banknotes",
                "quantity",
            ),
            (
                "triệu. Họ chỉ ra từng bước",
                "visual_diagram|Flat 2D orthographic diagram on a stark pure-white (#FFFFFF) canvas: three numbered staircase blocks rising left to right toward a gold star.",
                "từng bước",
                "three numbered staircase blocks",
                "progression",
            ),
            (
                "rõ ràng: đọc cuốn sách này, áp dụng công thức kia,",
                "still_life|Flat 2D close-up on a warm paper-cream (#F8F0DC) field: a yellow guidebook open beside a three-step recipe card with green checkmarks.",
                "đọc cuốn sách này",
                "yellow guidebook open beside a three-step recipe card",
                "context",
                [
                    {"text": "CÔNG THỨC ĐỔI ĐỜI", "placement": "above three-step recipe card", "object": "three-step recipe card"},
                ],
            ),
            (
                "dám bước ra khỏi vùng an toàn là đổi đời.",
                "full_scene|Flat 2D orthographic stage on a pale ice-blue (#CBE0E0) field: the white-head doodle stickman in a cerulean blue shirt (#3B82C4) steps across a dashed circle line toward a rising sun.",
                "khỏi vùng an toàn",
                "steps across a dashed circle line",
                "progression",
            ),
        ],
    },
    {
        "scene_id": "SC02",
        "title": "Làm đúng từng chữ nhưng vẫn mất trắng",
        "purpose": "Khắc họa cú sốc thực tế khi làm y hệt từng gạch đầu dòng của người thành công nhưng vẫn mất sạch vốn vì bẫy nhận thức",
        "setting": "Flat apricot-peach (#F2B88B) 2D orthographic small shop stage.",
        "narrative_phase": "lead_in",
        "tone": "narrative_warm",
        "requirements": ["R02"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Bạn tin thật. Bạn gom góp tiền tiết kiệm,",
                "still_life|Flat 2D close-up on an apricot-peach (#F2B88B) field: a pink ceramic piggy bank cracked open beside a neat stack of saved banknotes.",
                "tiền tiết kiệm",
                "pink ceramic piggy bank cracked open",
                "quantity",
                [
                    {"text": "TIỀN TIẾT KIỆM", "placement": "above pink ceramic piggy bank", "object": "pink ceramic piggy bank"},
                ],
            ),
            (
                "thức khuya dậy sớm,",
                "full_scene|Flat 2D orthographic desk on a slate-navy (#2E4361) night stage: the white-head doodle stickman in a cerulean blue shirt (#3B82C4) writes notes beside a twin-bell clock showing four o'clock.",
                "thức khuya dậy sớm",
                "twin-bell clock showing four o'clock",
                "context",
            ),
            (
                "làm y hệt từng gạch đầu dòng họ dạy.",
                "still_life|Flat 2D close-up on a stark pure-white (#FFFFFF) canvas: a clipboard sheet with four bold black bullet lines and four green checkmarks.",
                "từng gạch đầu dòng",
                "clipboard sheet with four bold black bullet lines",
                "progression",
            ),
            (
                "Nhưng chỉ vài tháng sau, tiền vốn bốc hơi sạch,",
                "still_life|Flat 2D orthographic frame on an apricot-peach (#F2B88B) field: an open metal cash box completely empty with three white smoke puffs rising.",
                "tiền vốn bốc hơi sạch",
                "open metal cash box completely empty",
                "cause_effect",
                [
                    {"text": "VỐN BỐC HƠI", "placement": "above open metal cash box", "object": "open metal cash box"},
                ],
            ),
            (
                "còn bạn ngồi tự dằn vặt: Sao người ta",
                "full_scene|Flat 2D orthographic storefront on a pale ice-blue (#CBE0E0) field: the white-head doodle stickman in a cerulean blue shirt (#3B82C4) slumps on a wooden stool beside a closed shutter.",
                "tự dằn vặt",
                "slumps on a wooden stool beside a closed shutter",
                "cause_effect",
            ),
            (
                "làm được mà mình lại thua? Sự thật là bạn không hề kém cỏi.",
                "white_card|Flat 2D orthographic card on a warm paper-cream (#F8F0DC) field: a red rubber stamp reading not your fault crossed over a broken ruler.",
                "không hề kém cỏi",
                "red rubber stamp reading not your fault",
                "context",
            ),
            (
                "Bạn vừa bước chân vào cái bẫy tinh vi nhất của bộ não:",
                "still_life|Flat 2D orthographic close-up on a warm paper-cream (#F8F0DC) field: a heavy toothed steel bear trap wide open with a shiny gold coin on the center plate.",
                "cái bẫy tinh vi nhất",
                "heavy toothed steel bear trap",
                "structure",
            ),
            (
                "Chỉ nhìn thấy một người thắng cuộc đứng dưới ánh đèn,",
                "full_scene|Flat 2D orthographic stage on a slate-navy (#2E4361) field: one presenter white-head doodle stickman in a dark blazer stands on a high podium inside a yellow spotlight cone.",
                "đứng dưới ánh đèn",
                "stands on a high podium inside a yellow spotlight cone",
                "comparison",
                [
                    {"text": "KẺ THẮNG CUỘC", "placement": "above high podium", "object": "high podium"},
                ],
            ),
            (
                "mà mù tịt trước hàng nghìn người làm y hệt nhưng đã chìm nghỉm.",
                "visual_diagram|Flat 2D orthographic diagram on a pale ice-blue (#CBE0E0) field: a dark underwater trench filled with dozens of sunken paper boats resting silently on the seabed.",
                "đã chìm nghỉm",
                "dozens of sunken paper boats resting silently on the seabed",
                "comparison",
                [
                    {"text": "NGHĨA ĐỊA VÔ HÌNH", "placement": "above sunken paper boats", "object": "sunken paper boats"},
                ],
            ),
        ],
    },
    {
        "scene_id": "SC03",
        "title": "Cơ chế cái phễu lọc vô hình của mạng xã hội",
        "purpose": "Giải thích cách thuật toán và truyền thông lọc lấy 1 người may mắn nhất và xóa sổ 999 người thất bại khỏi tầm mắt",
        "setting": "Flat pale ice-blue (#CBE0E0) 2D orthographic media studio stage.",
        "narrative_phase": "lead_in",
        "tone": "reflective_slow",
        "requirements": ["R03"],
        "source_ids": ["SRC02"],
        "claim_facts": [
            [
                "Họ lặng lẽ đóng cửa, đi xin việc lại và chẳng bao giờ lên mạng kể chuyện mình vừa thất bại.",
                "SRC02",
                "Nghĩa địa vô hình của người thất bại luôn bị truyền thông bỏ qua.",
            ],
        ],
        "rows": [
            (
                "Vì sao những công thức đó nghe lúc nào cũng hợp lý?",
                "still_life|Flat 2D orthographic card on a warm paper-cream (#F8F0DC) field: a golden loudspeaker emitting neat musical notes beside a green balance scale locked level.",
                "lúc nào cũng hợp lý",
                "golden loudspeaker emitting neat musical notes",
                "context",
            ),
            (
                "Hãy nhìn cách thông tin đến với mắt bạn.",
                "visual_diagram|Flat 2D orthographic diagram on a stark pure-white (#FFFFFF) canvas: a wide wire mesh strainer gate blocking ninety-nine grey dots while letting one gold star pass through to an eye icon.",
                "đến với mắt bạn",
                "letting one gold star pass through to an eye icon",
                "structure",
                [
                    {"text": "BỘ LỌC THÔNG TIN", "placement": "above wire mesh strainer gate", "object": "wire mesh strainer gate"},
                ],
            ),
            (
                "Một người đánh cược thành công sẽ lập kênh truyền thông,",
                "full_scene|Flat 2D orthographic studio on an apricot-peach (#F2B88B) field: a winner white-head doodle stickman in a dark blazer holds a golden dice cube in front of a camera on a tripod.",
                "lập kênh truyền thông",
                "camera on a tripod",
                "cause_effect",
            ),
            (
                "viết sách, lên sóng chia sẻ bí quyết mỗi ngày.",
                "still_life|Flat 2D orthographic close-up on a warm paper-cream (#F8F0DC) field: a studio condenser microphone beside a stack of printed bestseller books with a bold crown cover.",
                "viết sách, lên sóng",
                "studio condenser microphone beside a stack of printed bestseller books",
                "context",
                [
                    {"text": "BÍ QUYẾT THÀNH CÔNG", "placement": "on printed bestseller books", "object": "printed bestseller books"},
                ],
            ),
            (
                "Còn chín trăm chín mươi chín người",
                "visual_diagram|Flat 2D orthographic grid on a pale ice-blue (#CBE0E0) field: a large tally board marked with red cross strokes for nine hundred ninety-nine grey squares.",
                "chín trăm chín mươi chín",
                "nine hundred ninety-nine grey squares",
                "quantity",
                [
                    {"text": "CHÍN TRĂM CHÍN MƯƠI CHÍN", "placement": "above large tally board", "object": "large tally board"},
                ],
            ),
            (
                "làm theo đúng cách đó mà sạt nghiệp?",
                "still_life|Flat 2D close-up on an apricot-peach (#F2B88B) field: an upturned empty wooden cash drawer beside a torn recipe checklist.",
                "mà sạt nghiệp",
                "upturned empty wooden cash drawer",
                "cause_effect",
            ),
            (
                "Họ lặng lẽ đóng cửa, đi xin việc lại",
                "full_scene|Flat 2D orthographic street on a soft sage-green (#93A88C) field: the white-head doodle stickman in a casual cerulean blue shirt (#3B82C4) locks a wooden shop door hung with a closed sign.",
                "lặng lẽ đóng cửa",
                "locks a wooden shop door hung with a closed sign",
                "context",
                [
                    {"text": "ĐÓNG CỬA", "placement": "on wooden shop door", "object": "wooden shop door"},
                ],
            ),
            (
                "và chẳng bao giờ lên mạng kể chuyện mình vừa thất bại.",
                "still_life|Flat 2D close-up on a slate-navy (#2E4361) field: an unplugged studio microphone lying sideways next to a smartphone switched off with a black screen.",
                "chẳng bao giờ lên mạng",
                "unplugged studio microphone lying sideways",
                "context",
            ),
            (
                "Thuật toán gom đúng một người may mắn nhất đặt trước mắt bạn,",
                "still_life|Flat 2D orthographic close-up on a warm paper-cream (#F8F0DC) field: a giant mechanical claw arm holding up one glowing golden trophy directly in front of eyeglasses.",
                "một người may mắn nhất",
                "giant mechanical claw arm holding up one glowing golden trophy",
                "structure",
            ),
            (
                "khiến não bạn tưởng nhầm tỷ lệ thắng là một trăm phần trăm.",
                "white_card|Flat 2D orthographic card on a stark pure-white (#FFFFFF) canvas: a bold gauge meter pointing straight at a green one hundred percent mark.",
                "một trăm phần trăm",
                "pointing straight at a green one hundred percent mark",
                "quantity",
                [
                    {"text": "MỘT TRĂM PHẦN TRĂM", "placement": "above bold gauge meter", "object": "bold gauge meter"},
                ],
            ),
        ],
    },
    {
        "scene_id": "SC04",
        "title": "Giải phẫu Thiên kiến Kẻ Sống Sót & Ảo giác Nhân - Quả",
        "purpose": "Định nghĩa Thiên kiến Kẻ Sống Sót và bóc tách sai lầm đánh tráo nguyên nhân với kết quả qua ví dụ dậy lúc 4 giờ sáng",
        "setting": "Flat warm paper-cream (#F8F0DC) 2D orthographic lecture board stage.",
        "narrative_phase": "problem",
        "tone": "analytical_crisp",
        "requirements": ["R04"],
        "source_ids": ["SRC02"],
        "claim_facts": [],
        "rows": [
            (
                "Khoa học nhận thức gọi hiện tượng này",
                "still_life|Flat 2D orthographic display board on a warm paper-cream (#F8F0DC) field: an open cognitive science textbook beside a magnifying lens.",
                "Khoa học nhận thức",
                "open cognitive science textbook beside a magnifying lens",
                "context",
            ),
            (
                "là Thiên kiến Kẻ Sống Sót. Cái bẫy nguy hiểm nhất",
                "still_life|Flat 2D orthographic display board on a warm paper-cream (#F8F0DC) field: a bold black wooden frame containing a single gold star above a dashed line and nine faded grey tokens below.",
                "Thiên kiến Kẻ Sống Sót",
                "single gold star above a dashed line",
                "grouping",
                [
                    {"text": "THIÊN KIẾN KẺ SỐNG SÓT", "placement": "above bold black wooden frame", "object": "bold black wooden frame"},
                ],
            ),
            (
                "của nó là đánh tráo nguyên nhân và kết quả.",
                "visual_diagram|Flat 2D orthographic diagram on a stark pure-white (#FFFFFF) canvas: two rectangular wooden blocks labeled cause and effect with a red double arrow swapping their positions.",
                "nguyên nhân và kết quả",
                "two rectangular wooden blocks labeled cause and effect",
                "cause_effect",
                [
                    {"text": "NGUYÊN NHÂN VÀ KẾT QUẢ", "placement": "above two rectangular wooden blocks", "object": "two rectangular wooden blocks"},
                ],
            ),
            (
                "Thấy một tỷ phú hay dậy lúc bốn giờ sáng,",
                "full_scene|Flat 2D orthographic balcony on a pale ice-blue (#CBE0E0) dawn stage: a billionaire white-head doodle stickman wearing a sharp dark blazer stands beside a wall clock pointing at four o'clock.",
                "dậy lúc bốn giờ sáng",
                "wall clock pointing at four o'clock",
                "quantity",
                [
                    {"text": "BỐN GIỜ SÁNG", "placement": "below wall clock", "object": "wall clock"},
                ],
            ),
            (
                "ta vội tin rằng dậy sớm là bí quyết làm giàu.",
                "visual_diagram|Flat 2D orthographic equation card on a warm paper-cream (#F8F0DC) field: an alarm clock icon linked by a bold equals sign to a heavy sack of gold coins.",
                "bí quyết làm giàu",
                "alarm clock icon linked by a bold equals sign to a heavy sack of gold coins",
                "cause_effect",
            ),
            (
                "Mà quên mất ngoài kia có hàng triệu người lao động",
                "full_scene|Flat 2D orthographic street on a slate-navy (#2E4361) pre-dawn stage: a hard-working white-head doodle stickman in a cerulean blue shirt (#3B82C4) and conical bamboo hat pushes a heavy street cart.",
                "hàng triệu người lao động",
                "pushes a heavy street cart",
                "comparison",
            ),
            (
                "cũng dậy từ bốn giờ sáng mỗi ngày",
                "still_life|Flat 2D close-up on an apricot-peach (#F2B88B) field: a battered metal alarm clock ringing at four o'clock beside a pair of worn work gloves.",
                "bốn giờ sáng mỗi ngày",
                "battered metal alarm clock ringing at four o'clock",
                "quantity",
            ),
            (
                "nhưng cả đời vẫn chật vật.",
                "still_life|Flat 2D close-up on a pale ice-blue (#CBE0E0) field: a small tin coin bowl holding only three copper coins beside a stack of utility bills.",
                "vẫn chật vật",
                "small tin coin bowl holding only three copper coins",
                "comparison",
            ),
            (
                "Khi chỉ nhìn vào kẻ thắng, bạn không phân biệt được",
                "full_scene|Flat 2D orthographic stage on a warm paper-cream (#F8F0DC) field: the white-head doodle stickman in a cerulean blue shirt (#3B82C4) squints through a magnifying glass at a bright trophy.",
                "nhìn vào kẻ thắng",
                "squints through a magnifying glass at a bright trophy",
                "context",
            ),
            (
                "đâu là nguyên nhân giúp họ thắng,",
                "still_life|Flat 2D orthographic close-up on a soft sage-green (#93A88C) field: a heavy brass master key resting on a velvet cushion.",
                "nguyên nhân giúp họ thắng",
                "heavy brass master key",
                "comparison",
                [
                    {"text": "NGUYÊN NHÂN THẬT", "placement": "above heavy brass master key", "object": "heavy brass master key"},
                ],
            ),
            (
                "đâu chỉ là thói quen ngẫu nhiên.",
                "still_life|Flat 2D orthographic close-up on a warm paper-cream (#F8F0DC) field: two tumbling white dice cubes beside a porcelain teacup.",
                "thói quen ngẫu nhiên",
                "two tumbling white dice cubes",
                "comparison",
                [
                    {"text": "THÓI QUEN NGẪU NHIÊN", "placement": "above two tumbling white dice cubes", "object": "two tumbling white dice cubes"},
                ],
            ),
        ],
    },
    {
        "scene_id": "SC05",
        "title": "Bài toán máy bay ném bom năm 1943 (Phần 1: Sai lầm của trực giác)",
        "purpose": "Kể bài toán lịch sử năm 1943 của quân đội Mỹ và sai lầm trực giác khi đòi bọc thép vào những chỗ thủng nhiều đạn nhất",
        "setting": "Flat soft sage-green (#93A88C) 2D orthographic 1943 airfield hangar.",
        "narrative_phase": "causal_mechanism",
        "tone": "analytical_crisp",
        "requirements": ["R05"],
        "source_ids": ["SRC01"],
        "claim_facts": [
            [
                "Khi kiểm tra những chiếc máy bay sống sót trở về căn cứ, họ thấy phần cánh và thân chi chít lỗ đạn, trong khi động cơ và buồng lái lại trắng trơn, nguyên vẹn.",
                "SRC01",
                "Thống kê ban đầu chỉ ghi nhận dữ liệu từ những máy bay sống sót.",
            ],
        ],
        "rows": [
            (
                "Ngay cả những bộ óc dày dạn nhất cũng từng sập cái bẫy này.",
                "full_scene|Flat 2D orthographic war room on a soft sage-green (#93A88C) stage: two general white-head doodle stickmen wearing olive military uniforms with gold shoulder stars point sticks at a strategy table.",
                "bộ óc dày dạn nhất",
                "olive military uniforms with gold shoulder stars",
                "context",
            ),
            (
                "Năm một nghìn chín trăm bốn mươi ba, quân đội Mỹ",
                "still_life|Flat 2D orthographic military file on a warm paper-cream (#F8F0DC) field: an archival folder stamped with an army star emblem and a calendar sheet.",
                "quân đội Mỹ",
                "archival folder stamped with an army star emblem",
                "context",
            ),
            (
                "tìm cách bọc thép bảo vệ phi đội máy bay ném bom.",
                "still_life|Flat 2D orthographic blueprint on a pale ice-blue (#CBE0E0) field: a vintage propeller bomber plane silhouette next to a heavy grey steel armor plate.",
                "bọc thép bảo vệ",
                "heavy grey steel armor plate",
                "context",
                [
                    {"text": "PHI ĐỘI NÉM BOM", "placement": "above vintage propeller bomber plane", "object": "vintage propeller bomber plane"},
                ],
            ),
            (
                "Khi kiểm tra những chiếc máy bay sống sót trở về căn cứ,",
                "still_life|Flat 2D orthographic airfield on a warm paper-cream (#F8F0DC) field: a twin-engine propeller bomber parked on a runway strip with landing wheels down.",
                "trở về căn cứ",
                "twin-engine propeller bomber parked on a runway strip",
                "context",
            ),
            (
                "họ thấy phần cánh và thân chi chít lỗ đạn,",
                "visual_diagram|Flat 2D top-down orthographic bomber diagram on a stark pure-white (#FFFFFF) canvas: the wide wings and tail fuselage covered with clusters of bright red bullet-hole dots.",
                "chi chít lỗ đạn",
                "clusters of bright red bullet-hole dots",
                "quantity",
                [
                    {"text": "CÁNH CHI CHÍT ĐẠN", "placement": "above wide wings", "object": "wide wings"},
                ],
            ),
            (
                "trong khi động cơ và buồng lái lại trắng trơn, nguyên vẹn.",
                "cutaway_detail|Flat 2D orthographic close-up on a pale ice-blue (#CBE0E0) field: the front cockpit glass and twin propeller engine nacelles completely clean and unblemished.",
                "trắng trơn, nguyên vẹn",
                "completely clean and unblemished",
                "comparison",
                [
                    {"text": "ĐỘNG CƠ NGUYÊN VẸN", "placement": "above twin propeller engine nacelles", "object": "twin propeller engine nacelles"},
                ],
            ),
            (
                "Các tướng lĩnh lập tức kết luận:",
                "full_scene|Flat 2D orthographic briefing board on a soft sage-green (#93A88C) field: a general white-head doodle stickman in an olive military uniform and officer cap taps a wooden pointer on the wing diagram.",
                "tướng lĩnh lập tức kết luận",
                "taps a wooden pointer on the wing diagram",
                "cause_effect",
            ),
            (
                "chỗ nào thủng nhiều nhất",
                "still_life|Flat 2D close-up on an apricot-peach (#F2B88B) field: a metal wing panel perforated with twelve jagged black bullet holes circled in thick red marker.",
                "thủng nhiều nhất",
                "perforated with twelve jagged black bullet holes",
                "quantity",
            ),
            (
                "thì bọc thép dày vào chỗ đó!",
                "still_life|Flat 2D orthographic close-up on a warm paper-cream (#F8F0DC) field: a heavy bolted steel plate being clamped directly over the perforated wing panel.",
                "bọc thép dày",
                "heavy bolted steel plate",
                "cause_effect",
                [
                    {"text": "BỌC THÉP VÀO CÁNH?", "placement": "above heavy bolted steel plate", "object": "heavy bolted steel plate"},
                ],
            ),
        ],
    },
    {
        "scene_id": "SC06",
        "title": "Bài toán máy bay năm 1943 (Phần 2: Cú lật ngược của Abraham Wald)",
        "purpose": "Tái hiện cú lật ngược lịch sử của nhà toán học Abraham Wald: chỗ trắng trơn không một vết xước mới là tử huyệt cần bọc thép",
        "setting": "Flat warm paper-cream (#F8F0DC) 2D orthographic mathematician study room.",
        "narrative_phase": "causal_mechanism",
        "tone": "analytical_crisp",
        "requirements": ["R06"],
        "source_ids": ["SRC01"],
        "claim_facts": [
            [
                "Những chiếc máy bay bị bắn trúng động cơ và buồng lái hiện đang ở đâu?",
                "SRC01",
                "Những chiếc máy bay trúng đạn vào động cơ và buồng lái không thể quay về.",
            ],
            [
                "Chỗ trắng trơn không một vết xước mới là tử huyệt cần bọc thép.",
                "SRC01",
                "Cần bọc thép vào vị trí máy bay không có lỗ đạn.",
            ],
        ],
        "rows": [
            (
                "Nhưng nhà toán học A-bờ-ra-ham Oan đã ngăn quyết định đó lại",
                "full_scene|Flat 2D orthographic chalkboard on a warm paper-cream (#F8F0DC) stage: mathematician Abraham Wald as a white-head doodle stickman wearing round glasses and a brown tweed vest raises one open palm.",
                "ngăn quyết định đó lại",
                "raises one open palm",
                "context",
            ),
            (
                "bằng một câu hỏi lạnh người:",
                "still_life|Flat 2D orthographic close-up on a pale ice-blue (#CBE0E0) field: a white chalk stick drawing a giant sharp question mark on a dark slate board.",
                "câu hỏi lạnh người",
                "giant sharp question mark on a dark slate board",
                "context",
            ),
            (
                "Những chiếc máy bay bị bắn trúng động cơ và buồng lái",
                "white_card|Flat 2D orthographic card on a stark pure-white (#FFFFFF) canvas: a dashed outline of a missing bomber plane with a red target ring over the cockpit and engine.",
                "động cơ và buồng lái",
                "red target ring over the cockpit and engine",
                "context",
                [
                    {"text": "TRÚNG ĐẠN TỬ HUYỆT", "placement": "above dashed outline of a missing bomber plane", "object": "dashed outline of a missing bomber plane"},
                ],
            ),
            (
                "hiện đang ở đâu? Chúng không có mặt trong nhà chứa,",
                "still_life|Flat 2D orthographic hangar floor on a pale ice-blue (#CBE0E0) field: an empty parking bay painted with white boundary lines.",
                "không có mặt trong nhà chứa",
                "empty parking bay painted with white boundary lines",
                "context",
            ),
            (
                "vì chỉ cần dính đạn vào đó là máy bay đã nổ tung",
                "still_life|Flat 2D orthographic sky frame on an apricot-peach (#F2B88B) field: a bomber silhouette struck on its nose engine with a jagged orange starburst flame.",
                "máy bay đã nổ tung",
                "jagged orange starburst flame",
                "cause_effect",
            ),
            (
                "và nằm dưới đáy biển rồi.",
                "environment|Flat 2D orthographic ocean floor on a slate-navy (#2E4361) deep-sea stage: a sunken propeller bomber resting on sandy seabed rocks as a dark horizon symbol of missing data.",
                "nằm dưới đáy biển",
                "sunken propeller bomber resting on sandy seabed rocks",
                "cause_effect",
                [
                    {"text": "CHÌM DƯỚI ĐÁY BIỂN", "placement": "above sunken propeller bomber", "object": "sunken propeller bomber"},
                ],
            ),
            (
                "Những lỗ đạn chi chít trên cánh không phải là điểm yếu —",
                "visual_diagram|Flat 2D orthographic wing diagram on a warm paper-cream (#F8F0DC) field: red bullet-hole dots on the outer wings crossed out with a bold green shield icon.",
                "không phải là điểm yếu",
                "red bullet-hole dots on the outer wings crossed out with a bold green shield icon",
                "comparison",
            ),
            (
                "đó là bằng chứng cho thấy",
                "still_life|Flat 2D close-up on a soft sage-green (#93A88C) field: a green survivor stamp pressed onto an aircraft inspection logbook.",
                "bằng chứng cho thấy",
                "green survivor stamp pressed onto an aircraft inspection logbook",
                "context",
            ),
            (
                "bị bắn vào đó vẫn sống sót bay về được.",
                "still_life|Flat 2D orthographic sky frame on a pale ice-blue (#CBE0E0) field: a perforated wing bomber flying steadily home toward a green airfield beacon.",
                "sống sót bay về được",
                "flying steadily home toward a green airfield beacon",
                "cause_effect",
            ),
            (
                "Chỗ trắng trơn không một vết xước mới là tử huyệt cần bọc thép.",
                "visual_diagram|Flat 2D top-down bomber diagram on a stark pure-white (#FFFFFF) canvas: heavy blue steel armor plates bolted tightly around the clean white cockpit and twin engines.",
                "tử huyệt cần bọc thép",
                "heavy blue steel armor plates bolted tightly around the clean white cockpit",
                "structure",
                [
                    {"text": "BỌC THÉP TỬ HUYỆT", "placement": "above clean white cockpit", "object": "clean white cockpit"},
                ],
            ),
        ],
    },
    {
        "scene_id": "SC07",
        "title": "Đâu là vết đạn ở cánh, đâu là động cơ sống còn ngoài đời thực?",
        "purpose": "Liên hệ trực tiếp bài toán máy bay với đời thực: trang trí quán, chạy quảng cáo chỉ là vết đạn ở cánh; mặt bằng nhà, vốn chịu lỗ 2 năm mới là động cơ",
        "setting": "Flat apricot-peach (#F2B88B) 2D orthographic storefront comparison stage.",
        "narrative_phase": "explanation",
        "tone": "analytical_crisp",
        "requirements": ["R07"],
        "source_ids": ["SRC01", "SRC02"],
        "claim_facts": [],
        "rows": [
            (
                "Quay lại những câu chuyện thành công bạn xem mỗi ngày.",
                "full_scene|Flat 2D orthographic living room on a warm paper-cream (#F8F0DC) field: the white-head doodle stickman in a casual cerulean blue shirt (#3B82C4) holds up a tablet showing a smiling shop owner.",
                "câu chuyện thành công",
                "tablet showing a smiling shop owner",
                "context",
            ),
            (
                "Khi bắt chước cách họ trang trí cửa hàng,",
                "still_life|Flat 2D orthographic close-up on an apricot-peach (#F2B88B) field: a potted monstera plant beside a decorative neon cafe sign and a wooden menu board.",
                "trang trí cửa hàng",
                "potted monstera plant beside a decorative neon cafe sign",
                "context",
            ),
            (
                "cách chạy quảng cáo hay thói quen sinh hoạt,",
                "still_life|Flat 2D orthographic close-up on a pale ice-blue (#CBE0E0) field: a megaphone icon next to a morning daily schedule checklist.",
                "chạy quảng cáo",
                "megaphone icon next to a morning daily schedule checklist",
                "context",
            ),
            (
                "bạn chỉ đang chắp vá vào những vết đạn vô hại trên cánh.",
                "visual_diagram|Flat 2D orthographic diagram on a warm paper-cream (#F8F0DC) field: small adhesive bandages stuck over outer airplane wing holes labeled surface habits.",
                "vết đạn vô hại trên cánh",
                "small adhesive bandages stuck over outer airplane wing holes",
                "comparison",
                [
                    {"text": "BỀ NỔI VÔ HẠI", "placement": "above outer airplane wing holes", "object": "outer airplane wing holes"},
                ],
            ),
            (
                "Còn phần động cơ thực sự giúp họ sống sót",
                "cutaway_detail|Flat 2D orthographic cutaway on a soft sage-green (#93A88C) field: a massive armored turbine engine core glowing inside the center of a business shop.",
                "phần động cơ thực sự",
                "massive armored turbine engine core",
                "structure",
                [
                    {"text": "ĐỘNG CƠ SỐNG CÒN", "placement": "above massive armored turbine engine core", "object": "massive armored turbine engine core"},
                ],
            ),
            (
                "qua giai đoạn khốc liệt nhất —",
                "still_life|Flat 2D orthographic frame on a slate-navy (#2E4361) field: a sturdy brick shop standing firm under heavy rain clouds and lightning bolts.",
                "giai đoạn khốc liệt nhất",
                "sturdy brick shop standing firm under heavy rain clouds",
                "context",
            ),
            (
                "như việc họ có sẵn mặt bằng của gia đình,",
                "still_life|Flat 2D orthographic close-up on a warm paper-cream (#F8F0DC) field: a red land ownership certificate stamped zero rent resting beside a golden house key.",
                "mặt bằng của gia đình",
                "red land ownership certificate stamped zero rent",
                "context",
                [
                    {"text": "MẶT BẰNG NHÀ CÓ SẴN", "placement": "above red land ownership certificate", "object": "red land ownership certificate"},
                ],
            ),
            (
                "có nguồn vốn nhàn rỗi chịu lỗ được hai năm,",
                "still_life|Flat 2D orthographic close-up on a pale ice-blue (#CBE0E0) field: a heavy green iron safe vault next to a two-year wall calendar shield.",
                "chịu lỗ được hai năm",
                "heavy green iron safe vault next to a two-year wall calendar shield",
                "quantity",
                [
                    {"text": "VỐN ĐỆM HAI NĂM", "placement": "above heavy green iron safe vault", "object": "heavy green iron safe vault"},
                ],
            ),
            (
                "hay vào thị trường lúc chưa ai cạnh tranh —",
                "full_scene|Flat 2D orthographic field on a soft sage-green (#93A88C) stage: a pioneer white-head doodle stickman in a dark blazer plants a flag on an open hill long before other stalls arrive.",
                "chưa ai cạnh tranh",
                "plants a flag on an open hill",
                "context",
            ),
            (
                "thì không bao giờ hiện lên trên màn hình.",
                "still_life|Flat 2D orthographic close-up on a slate-navy (#2E4361) field: a bright smartphone frame showing only a trophy while the heavy vault stays hidden behind the back cover.",
                "không bao giờ hiện lên",
                "hidden behind the back cover",
                "comparison",
            ),
        ],
    },
    {
        "scene_id": "SC08",
        "title": "Phản biện 2 chiều: Khi nào nên học người thành công, khi nào là thuốc độc?",
        "purpose": "Phân định rõ ranh giới: kỹ năng có quy tắc cố định (viết mã, sửa máy, thể thao) thì sao chép được; cuộc chơi biến số (kinh doanh, đầu tư) mà sao chép nguyên xi là mua lại vé số độc đắc",
        "setting": "Flat stark pure-white (#FFFFFF) 2D orthographic comparison board.",
        "narrative_phase": "counter_argument",
        "tone": "analytical_crisp",
        "requirements": ["R08"],
        "source_ids": ["SRC02"],
        "claim_facts": [],
        "rows": [
            (
                "Vậy chẳng lẽ học hỏi người thành công luôn là sai lầm?",
                "full_scene|Flat 2D orthographic frame on a warm paper-cream (#F8F0DC) field: the white-head doodle stickman in a casual cerulean blue shirt (#3B82C4) holds two road signs pointing toward fixed rules and random gambles.",
                "luôn là sai lầm",
                "holds two road signs",
                "comparison",
            ),
            (
                "Câu trả lời là không hẳn.",
                "white_card|Flat 2D orthographic card on a stark pure-white (#FFFFFF) canvas: a balanced two-pan brass scale separating deterministic rules from uncertain probability.",
                "không hẳn",
                "balanced two-pan brass scale",
                "comparison",
            ),
            (
                "Nếu bạn học một kỹ năng có quy tắc cố định —",
                "still_life|Flat 2D orthographic close-up on a warm paper-cream (#F8F0DC) field: a steel vernier caliper ruler resting beside a precision compass and square.",
                "quy tắc cố định",
                "steel vernier caliper ruler",
                "structure",
                [
                    {"text": "QUY TẮC CỐ ĐỊNH", "placement": "above steel vernier caliper ruler", "object": "steel vernier caliper ruler"},
                ],
            ),
            (
                "như cách viết một đoạn mã, cách sửa một cái máy,",
                "still_life|Flat 2D orthographic close-up on a pale ice-blue (#CBE0E0) field: a clean computer monitor displaying bracket lines of code beside a steel wrench.",
                "viết một đoạn mã",
                "clean computer monitor displaying bracket lines of code",
                "context",
            ),
            (
                "hay cách rèn luyện sức khỏe —",
                "full_scene|Flat 2D orthographic gym floor on a soft sage-green (#93A88C) field: the white-head doodle stickman in a cerulean blue shirt (#3B82C4) lifts a pair of black iron dumbbells.",
                "rèn luyện sức khỏe",
                "lifts a pair of black iron dumbbells",
                "context",
            ),
            (
                "thì làm đúng phương pháp sẽ ra kết quả.",
                "visual_diagram|Flat 2D orthographic flow card on a warm paper-cream (#F8F0DC) field: input box A plus step box B leading straight to guaranteed result box C.",
                "ra kết quả",
                "leading straight to guaranteed result box C",
                "cause_effect",
            ),
            (
                "Nhưng trong những cuộc chơi đầy biến số",
                "still_life|Flat 2D orthographic close-up on an apricot-peach (#F2B88B) field: a spinning roulette wheel beside three tumbling dice cubes.",
                "đầy biến số",
                "spinning roulette wheel beside three tumbling dice cubes",
                "context",
                [
                    {"text": "CUỘC CHƠI BIẾN SỐ", "placement": "above spinning roulette wheel", "object": "spinning roulette wheel"},
                ],
            ),
            (
                "như kinh doanh, đầu tư hay nhảy việc,",
                "still_life|Flat 2D orthographic close-up on a pale ice-blue (#CBE0E0) field: a jagged stock market chart next to a crossroads signboard in gusty wind.",
                "kinh doanh, đầu tư",
                "jagged stock market chart",
                "context",
            ),
            (
                "việc sao chép nguyên xi công thức của một người thắng cuộc",
                "full_scene|Flat 2D orthographic desk on a warm paper-cream (#F8F0DC) field: the white-head doodle stickman in a cerulean blue shirt (#3B82C4) traces over a winner's old map using carbon paper.",
                "sao chép nguyên xi",
                "traces over a winner's old map using carbon paper",
                "context",
            ),
            (
                "chẳng khác nào mua lại dãy số của người vừa trúng độc đắc.",
                "still_life|Flat 2D orthographic close-up on a pale ice-blue (#CBE0E0) field: yesterday's crumpled lottery ticket stamped expired with six circled numbers.",
                "vừa trúng độc đắc",
                "yesterday's crumpled lottery ticket stamped expired",
                "comparison",
                [
                    {"text": "VÉ SỐ ĐÃ XỔ", "placement": "above yesterday's crumpled lottery ticket", "object": "yesterday's crumpled lottery ticket"},
                ],
            ),
        ],
    },
    {
        "scene_id": "SC09",
        "title": "Vũ khí Tư duy Trừ Lùi (Tri thức tiêu cực)",
        "purpose": "Giới thiệu phương pháp Tri Thức Tiêu Cực (Tư duy Trừ Lùi) của Charlie Munger và ẩn dụ kỳ thủ cờ vua loại bỏ nước cờ tự sát",
        "setting": "Flat soft sage-green (#93A88C) 2D orthographic chess study room.",
        "narrative_phase": "explanation",
        "tone": "reflective_slow",
        "requirements": ["R09"],
        "source_ids": ["SRC02", "SRC03"],
        "claim_facts": [
            [
                "sử dụng phương pháp Tri Thức Tiêu Cực — hay hiểu đơn giản là Tư duy Trừ Lùi.",
                "SRC02",
                "Tri thức tiêu cực tập trung vào việc loại bỏ sai lầm.",
            ],
            [
                "mà nhờ kiên quyết loại bỏ những nước cờ tự sát.",
                "SRC03",
                "Nguyên lý nghịch đảo giúp tránh xa những cái chết ngu ngốc.",
            ],
        ],
        "rows": [
            (
                "Để không bị đánh lừa, nhà đầu tư huyền thoại Sạc-li Mân-gơ",
                "full_scene|Flat 2D orthographic library study on a warm paper-cream (#F8F0DC) stage: investor Charlie Munger as a white-head doodle stickman wearing thick glasses and a classic dark vest holds open an almanac book.",
                "nhà đầu tư huyền thoại",
                "wearing thick glasses and a classic dark vest holds open an almanac book",
                "context",
            ),
            (
                "sử dụng phương pháp Tri Thức Tiêu Cực —",
                "white_card|Flat 2D orthographic title card on a stark pure-white (#FFFFFF) canvas: a bold black minus sign inside a shield clearing away three red hazard triangles.",
                "Tri Thức Tiêu Cực",
                "bold black minus sign inside a shield",
                "structure",
                [
                    {"text": "TRI THỨC TIÊU CỰC", "placement": "above bold black minus sign", "object": "bold black minus sign"},
                ],
            ),
            (
                "hay hiểu đơn giản là Tư duy Trừ Lùi.",
                "visual_diagram|Flat 2D orthographic diagram on a warm paper-cream (#F8F0DC) field: a black eraser wiping away three red error blocks to leave a clean safe path.",
                "Tư duy Trừ Lùi",
                "black eraser wiping away three red error blocks",
                "structure",
                [
                    {"text": "TƯ DUY TRỪ LÙI", "placement": "above black eraser", "object": "black eraser"},
                ],
            ),
            (
                "Chúng ta rất khó biết chính xác làm gì",
                "still_life|Flat 2D orthographic frame on a pale ice-blue (#CBE0E0) field: a brass compass spinning uncertainly in thick white mist.",
                "khó biết chính xác",
                "brass compass spinning uncertainly",
                "context",
            ),
            (
                "để chắc chắn thành công rực rỡ,",
                "still_life|Flat 2D orthographic frame on a warm paper-cream (#F8F0DC) field: a distant mountain peak wrapped in cloud layers with three winding trails.",
                "thành công rực rỡ",
                "distant mountain peak wrapped in cloud layers",
                "comparison",
            ),
            (
                "nhưng lại có thể biết cực kỳ rõ",
                "still_life|Flat 2D close-up on a soft sage-green (#93A88C) field: a high-beam spotlight illuminating a sharp hazard map with crystal clarity.",
                "biết cực kỳ rõ",
                "high-beam spotlight illuminating a sharp hazard map",
                "comparison",
            ),
            (
                "làm gì chắc chắn sẽ dẫn đến thất bại.",
                "still_life|Flat 2D orthographic close-up on an apricot-peach (#F2B88B) field: a bright red cliff-edge warning sign with a black arrow pointing away from a deep pit.",
                "dẫn đến thất bại",
                "bright red cliff-edge warning sign",
                "comparison",
                [
                    {"text": "TRÁNH HỐ SÂU THẤT BẠI", "placement": "above bright red cliff-edge warning sign", "object": "bright red cliff-edge warning sign"},
                ],
            ),
            (
                "Một kỳ thủ cờ vua chiến thắng không phải nhờ đi",
                "full_scene|Flat 2D orthographic table on a soft sage-green (#93A88C) stage: the white-head doodle stickman in a cerulean blue shirt (#3B82C4) leans calmly over a flat 2D chessboard.",
                "kỳ thủ cờ vua",
                "leans calmly over a flat 2D chessboard",
                "context",
            ),
            (
                "những nước cờ thần thánh, mà nhờ kiên quyết loại bỏ",
                "still_life|Flat 2D close-up on a warm paper-cream (#F8F0DC) field: a glowing golden chess knight piece crossed out beside a red marker.",
                "nước cờ thần thánh",
                "glowing golden chess knight piece crossed out",
                "comparison",
            ),
            (
                "những nước cờ tự sát.",
                "visual_diagram|Flat 2D orthographic chessboard diagram on a stark pure-white (#FFFFFF) canvas: three red crosses marked over blunder squares while a white king stands safe.",
                "nước cờ tự sát",
                "three red crosses marked over blunder squares",
                "cause_effect",
                [
                    {"text": "BỎ NƯỚC CỜ TỰ SÁT", "placement": "above three red crosses", "object": "three red crosses"},
                ],
            ),
        ],
    },
    {
        "scene_id": "SC10",
        "title": "Quy tắc 1: Đi tìm dữ liệu dưới đáy biển trước khi nhìn lên sân khấu",
        "purpose": "Hướng dẫn thực hành Bước 1: Chủ động khảo sát những người vừa bỏ cuộc trong ngành để tìm đá ngầm và chi phí ẩn",
        "setting": "Flat pale ice-blue (#CBE0E0) 2D orthographic research desk stage.",
        "narrative_phase": "takeaway",
        "tone": "analytical_crisp",
        "requirements": ["R10"],
        "source_ids": ["SRC01", "SRC02"],
        "claim_facts": [],
        "rows": [
            (
                "Trước bất kỳ quyết định lớn nào về tiền bạc hay sự nghiệp,",
                "full_scene|Flat 2D orthographic crossroads on a warm paper-cream (#F8F0DC) stage: the white-head doodle stickman in a casual cerulean blue shirt (#3B82C4) pauses calmly holding a checklist board.",
                "quyết định lớn",
                "pauses calmly holding a checklist board",
                "context",
            ),
            (
                "bạn hãy áp dụng ngay hai bước lọc.",
                "visual_diagram|Flat 2D orthographic card on a stark pure-white (#FFFFFF) canvas: two numbered horizontal filter gates labeled step one and step two.",
                "hai bước lọc",
                "two numbered horizontal filter gates",
                "structure",
                [
                    {"text": "HAI BƯỚC LỌC AN TOÀN", "placement": "above two numbered horizontal filter gates", "object": "two numbered horizontal filter gates"},
                ],
            ),
            (
                "Bước thứ nhất: Chủ động đi tìm dữ liệu bị khuất.",
                "full_scene|Flat 2D orthographic dock on a pale ice-blue (#CBE0E0) stage: the white-head doodle stickman in a cerulean blue shirt (#3B82C4) shines a yellow flashlight beam down into dark water.",
                "dữ liệu bị khuất",
                "shines a yellow flashlight beam down into dark water",
                "context",
                [
                    {"text": "TÌM DỮ LIỆU BỊ KHUẤT", "placement": "above yellow flashlight beam", "object": "yellow flashlight beam"},
                ],
            ),
            (
                "Khi thấy một nghề đang sốt hay một mô hình",
                "still_life|Flat 2D orthographic close-up on an apricot-peach (#F2B88B) field: a glittering storefront banner with golden sparkles and a long queue rope.",
                "nghề đang sốt",
                "glittering storefront banner with golden sparkles",
                "context",
            ),
            (
                "kinh doanh hào nhoáng, đừng hỏi ai đã làm giàu từ nó.",
                "still_life|Flat 2D close-up on a warm paper-cream (#F8F0DC) field: a golden trophy icon stamped with a bold red stop circle.",
                "ai đã làm giàu",
                "golden trophy icon stamped with a bold red stop circle",
                "comparison",
            ),
            (
                "Hãy gõ tìm xem những người vừa bỏ cuộc trong ngành đó",
                "still_life|Flat 2D orthographic close-up on a pale ice-blue (#CBE0E0) field: a search bar on a notebook page looking up shop liquidation and closure lessons.",
                "những người vừa bỏ cuộc",
                "search bar on a notebook page looking up shop liquidation",
                "context",
                [
                    {"text": "HỒ SƠ THANH LÝ", "placement": "above notebook page", "object": "notebook page"},
                ],
            ),
            (
                "đã vấp phải tảng đá ngầm nào,",
                "still_life|Flat 2D orthographic waterline view on a slate-navy (#2E4361) field: a sharp black underwater reef rock lurking right beneath calm surface waves.",
                "tảng đá ngầm",
                "sharp black underwater reef rock",
                "cause_effect",
                [
                    {"text": "TẢNG ĐÁ NGẦM", "placement": "above sharp black underwater reef rock", "object": "sharp black underwater reef rock"},
                ],
            ),
            (
                "chi phí ẩn là gì, và vì sao họ phải dừng cuộc chơi.",
                "still_life|Flat 2D orthographic close-up on a warm paper-cream (#F8F0DC) field: an open ledger folder revealing three red stamps for rent hike, spoiled inventory, and hidden fees.",
                "chi phí ẩn",
                "open ledger folder revealing three red stamps",
                "cause_effect",
                [
                    {"text": "CHI PHÍ ẨN", "placement": "above open ledger folder", "object": "open ledger folder"},
                ],
            ),
        ],
    },
    {
        "scene_id": "SC11",
        "title": "Quy tắc 2: Bọc thép cho động cơ của chính mình",
        "purpose": "Hướng dẫn thực hành Bước 2: Bọc thép vào tử huyệt tài chính cá nhân (không vay lãi cao, không tất tay, giữ quỹ dự phòng 6 tháng)",
        "setting": "Flat warm paper-cream (#F8F0DC) 2D orthographic personal finance desk.",
        "narrative_phase": "takeaway",
        "tone": "narrative_warm",
        "requirements": ["R11"],
        "source_ids": ["SRC03"],
        "claim_facts": [
            [
                "Và luôn giữ lại một khoản dự phòng đủ sống tối thiểu sáu tháng",
                "SRC03",
                "Biên độ an toàn bảo vệ con người trước biến cố bất ngờ.",
            ],
        ],
        "rows": [
            (
                "Bước thứ hai: Bọc thép vào tử huyệt của bạn",
                "full_scene|Flat 2D orthographic workshop on a soft sage-green (#93A88C) stage: the white-head doodle stickman in a casual cerulean blue shirt (#3B82C4) bolts a blue steel armor shield onto a savings chest.",
                "Bọc thép vào tử huyệt",
                "bolts a blue steel armor shield onto a savings chest",
                "structure",
                [
                    {"text": "BỌC THÉP TỬ HUYỆT", "placement": "on blue steel armor shield", "object": "blue steel armor shield"},
                ],
            ),
            (
                "trước khi nghĩ tới lợi nhuận.",
                "still_life|Flat 2D close-up on a warm paper-cream (#F8F0DC) field: a heavy iron padlock locked tight in front of a gold coin jar.",
                "nghĩ tới lợi nhuận",
                "heavy iron padlock locked tight in front of a gold coin jar",
                "progression",
            ),
            (
                "Hãy gạch bỏ ngay những sai lầm",
                "still_life|Flat 2D close-up on a stark pure-white (#FFFFFF) canvas: a thick red marker striking through three fatal financial blunder cards.",
                "gạch bỏ ngay",
                "thick red marker striking through three fatal financial blunder cards",
                "grouping",
            ),
            (
                "có thể hạ gục bạn chỉ sau một cú sẩy chân:",
                "still_life|Flat 2D orthographic close-up on an apricot-peach (#F2B88B) field: a cracked wooden plank bridge over a deep chasm marked with a warning triangle.",
                "một cú sẩy chân",
                "cracked wooden plank bridge over a deep chasm",
                "cause_effect",
            ),
            (
                "Không dùng tiền vay lãi cao",
                "still_life|Flat 2D orthographic close-up on an apricot-peach (#F2B88B) field: a loan contract chained to a heavy black iron ball crossed out with a bold red X.",
                "tiền vay lãi cao",
                "loan contract chained to a heavy black iron ball",
                "cause_effect",
                [
                    {"text": "KHÔNG VAY LÃI CAO", "placement": "above loan contract", "object": "loan contract"},
                ],
            ),
            (
                "để thử nghiệm một lĩnh vực mình mới nghe tên;",
                "full_scene|Flat 2D orthographic frame on a warm paper-cream (#F8F0DC) field: the white-head doodle stickman in a cerulean blue shirt (#3B82C4) refuses a mystery box labeled unknown trend.",
                "mới nghe tên",
                "refuses a mystery box labeled unknown trend",
                "context",
            ),
            (
                "Không dồn toàn bộ tiền tiết kiệm vào một cửa duy nhất;",
                "visual_diagram|Flat 2D orthographic diagram on a pale ice-blue (#CBE0E0) field: three separate woven baskets holding white eggs instead of one fragile basket on a narrow ledge.",
                "một cửa duy nhất",
                "three separate woven baskets holding white eggs",
                "grouping",
                [
                    {"text": "KHÔNG DỒN MỘT CỬA", "placement": "above three separate woven baskets", "object": "three separate woven baskets"},
                ],
            ),
            (
                "Và luôn giữ lại một khoản dự phòng đủ sống tối thiểu sáu tháng",
                "still_life|Flat 2D orthographic close-up on a soft sage-green (#93A88C) field: a locked glass reserve jar filled with gold coins standing beside a six-month desk calendar.",
                "tối thiểu sáu tháng",
                "six-month desk calendar",
                "quantity",
                [
                    {"text": "DỰ PHÒNG SÁU THÁNG", "placement": "above six-month desk calendar", "object": "six-month desk calendar"},
                ],
            ),
            (
                "để dù dự án có thất bại,",
                "still_life|Flat 2D orthographic frame on an apricot-peach (#F2B88B) field: a small paper project boat tipping over in rain beside a sturdy orange lifeboat.",
                "dự án có thất bại",
                "small paper project boat tipping over",
                "cause_effect",
            ),
            (
                "cuộc sống của bạn vẫn không bị đánh chìm.",
                "full_scene|Flat 2D orthographic calm harbor on a warm paper-cream (#F8F0DC) stage: the white-head doodle stickman in a cerulean blue shirt (#3B82C4) stands dry and steady on a solid stone pier beside a lifeboat.",
                "không bị đánh chìm",
                "stands dry and steady on a solid stone pier beside a lifeboat",
                "cause_effect",
            ),
        ],
    },
    {
        "scene_id": "SC12",
        "title": "Khép vòng lặp: Ánh nhìn tỉnh táo trước màn hình",
        "purpose": "Khép lại vòng lặp mở bài: tối nay mở điện thoại lên với đôi mắt tỉnh táo, nhìn xuống đáy biển và bảo vệ kỹ động cơ trước khi cất cánh",
        "setting": "Flat warm paper-cream (#F8F0DC) 2D orthographic morning balcony stage.",
        "narrative_phase": "closing",
        "tone": "reflective_slow",
        "requirements": ["R12"],
        "source_ids": ["SRC01", "SRC03"],
        "claim_facts": [],
        "rows": [
            (
                "Tối nay khi mở điện thoại lên,",
                "full_scene|Flat 2D orthographic bedroom on a slate-navy (#2E4361) night stage: the white-head doodle stickman in a casual cerulean blue shirt (#3B82C4) sits upright on the bed holding a smartphone calmly.",
                "mở điện thoại lên",
                "holding a smartphone calmly",
                "context",
            ),
            (
                "những câu chuyện đổi đời hào nhoáng",
                "still_life|Flat 2D close-up on an apricot-peach (#F2B88B) field: a smartphone screen displaying a glittering golden crown and a luxury sports car icon.",
                "đổi đời hào nhoáng",
                "glittering golden crown and a luxury sports car icon",
                "context",
            ),
            (
                "vẫn sẽ tiếp tục lướt qua trước mắt bạn.",
                "still_life|Flat 2D close-up on a pale ice-blue (#CBE0E0) field: three horizontal video cards sliding across a glass screen.",
                "lướt qua trước mắt",
                "three horizontal video cards sliding across a glass screen",
                "progression",
            ),
            (
                "Nhưng giờ đây, bạn đã có một đôi mắt khác",
                "full_scene|Flat 2D orthographic close-up on a warm paper-cream (#F8F0DC) field: the white-head doodle stickman in a cerulean blue shirt (#3B82C4) adjusts clear blue X-ray spectacles on the round white head.",
                "một đôi mắt khác",
                "adjusts clear blue X-ray spectacles",
                "context",
                [
                    {"text": "GÓC NHÌN TỈNH TÁO", "placement": "above clear blue X-ray spectacles", "object": "clear blue X-ray spectacles"},
                ],
            ),
            (
                "để nhìn xuyên qua ánh đèn sân khấu.",
                "visual_diagram|Flat 2D orthographic diagram on a pale ice-blue (#CBE0E0) field: a yellow stage spotlight cone made transparent to reveal the hidden support pillars underneath.",
                "ánh đèn sân khấu",
                "yellow stage spotlight cone made transparent",
                "structure",
            ),
            (
                "Đừng mải mê đếm những vết đạn trên cánh của kẻ thắng cuộc.",
                "still_life|Flat 2D orthographic close-up on a warm paper-cream (#F8F0DC) field: an airplane wing with red dots pushed aside by a clean white hand-drawn arrow.",
                "vết đạn trên cánh",
                "airplane wing with red dots",
                "comparison",
            ),
            (
                "Hãy nhìn xuống những chiếc máy bay đã chìm dưới đáy biển,",
                "visual_diagram|Flat 2D orthographic chart on a slate-navy (#2E4361) field: a diver periscope scanning sunken bomber outlines on the ocean floor to map safe coordinates.",
                "chìm dưới đáy biển",
                "sunken bomber outlines on the ocean floor",
                "context",
                [
                    {"text": "NHÌN XUỐNG ĐÁY BIỂN", "placement": "above sunken bomber outlines", "object": "sunken bomber outlines"},
                ],
            ),
            (
                "bảo vệ thật kỹ động cơ của mình,",
                "still_life|Flat 2D orthographic close-up on a soft sage-green (#93A88C) field: a twin-propeller aircraft engine wrapped in solid blue steel armor plates with a green ready light.",
                "bảo vệ thật kỹ động cơ",
                "twin-propeller aircraft engine wrapped in solid blue steel armor plates",
                "structure",
                [
                    {"text": "BẢO VỆ ĐỘNG CƠ", "placement": "above twin-propeller aircraft engine", "object": "twin-propeller aircraft engine"},
                ],
            ),
            (
                "rồi hãy vững vàng cất cánh.",
                "full_scene|Flat 2D orthographic runway on a warm paper-cream (#F8F0DC) sunrise stage: the white-head doodle stickman in a cerulean blue shirt (#3B82C4) pilots an armored propeller plane climbing steadily into a clear sky.",
                "vững vàng cất cánh",
                "pilots an armored propeller plane climbing steadily into a clear sky",
                "progression",
            ),
        ],
    },
]


def build_human_editorial() -> Dict[str, Any]:
    return {
        "editorial_stance": (
            "Thành công bền vững trong các cuộc chơi nhiều biến số không đến từ việc sao chép thói quen bề nổi của kẻ thắng cuộc, "
            "mà đến từ Tư duy Trừ Lùi (Tri Thức Tiêu Cực): khảo sát dữ liệu dưới đáy biển của những người bỏ cuộc và bọc thép cho tử huyệt tài chính cá nhân."
        ),
        "topic_dilemmas": [
            "Mâu thuẫn giữa những công thức đổi đời nghe cực kỳ hợp lý trên mạng xã hội với thực tế hàng nghìn người làm y hệt nhưng mất trắng vốn liếng.",
            "Ảo giác nhân quả khi nhìn vào một người thắng cuộc đứng dưới ánh đèn mà bỏ quên những lợi thế ngầm như mặt bằng gia đình hay nguồn vốn chịu lỗ hai năm.",
        ],
        "author_raw_input": (
            "Giải mã Thiên kiến Kẻ Sống Sót (Survivorship Bias) từ trải nghiệm thực tế của người trẻ Việt Nam đi làm lương vừa nhận đã hết, "
            "lướt mạng thấy người trạc tuổi khoe tự do tài chính rồi gom tiết kiệm làm theo và mất trắng. Kết nối mượt mà sang bài toán máy bay ném bom năm 1943 "
            "của Abraham Wald, phản biện hai chiều khi nào nên học người thành công (kỹ năng quy tắc cố định vs cuộc chơi biến số), và đúc kết phương pháp Tư duy Trừ Lùi "
            "của Charlie Munger thành 2 bước lọc thực chiến."
        ),
        "dynamic_questions": [
            "Làm sao phân biệt được đâu là vết đạn vô hại trên cánh, đâu là phần động cơ sống còn nhưng bị giấu kín trong các câu chuyện khởi nghiệp?",
            "Khi nào việc học theo người thành công mang lại kết quả thật, và khi nào nó chẳng khác gì mua lại tờ vé số đã xổ của người vừa trúng độc đắc?",
            "Trước một quyết định lớn về tiền bạc hay sự nghiệp, hai bước lọc Tư duy Trừ Lùi nào giúp bạn không bị đánh chìm?",
        ],
        "expanded_content_ideas": [
            {
                "angle_type": "analysis",
                "idea_summary": "Cơ chế bộ lọc vô hình của thuật toán mạng xã hội và bài toán máy bay năm 1943 của Abraham Wald làm méo mó nhận thức xác suất.",
                "narrative_integration": "Triển khai xuyên suốt SC01 đến SC06 từ cú sốc mất vốn ngoài đời thực sang nhà chứa máy bay năm 1943 và đáy biển dữ liệu bị khuất.",
            },
            {
                "angle_type": "commentary",
                "idea_summary": "Phản biện hai chiều giữa kỹ năng có quy tắc cố định (viết mã, sửa máy, rèn luyện sức khỏe) và cuộc chơi đầy biến số (kinh doanh, đầu tư, nhảy việc).",
                "narrative_integration": "Triển khai tại SC07 và SC08 giúp người xem không rơi vào cực đoan phủ nhận sạch trơn việc học hỏi.",
            },
            {
                "angle_type": "evaluation",
                "idea_summary": "Vũ khí Tri Thức Tiêu Cực (Tư duy Trừ Lùi) của Charlie Munger và 2 quy tắc bọc thép tử huyệt trước khi cất cánh.",
                "narrative_integration": "Triển khai tại SC09 đến SC12 với ẩn dụ bàn cờ vua và hai bước lọc thực tế.",
            },
        ],
    }


def build_topic() -> ResearchedTopic:
    scenes: List[ResearchedScene] = []
    total_scenes = len(STORY_SCENES)

    for idx, sc_spec in enumerate(STORY_SCENES, 1):
        scene_id = sc_spec["scene_id"]
        title = sc_spec["title"]
        purpose = sc_spec["purpose"]
        setting = sc_spec["setting"]
        narrative_phase = sc_spec["narrative_phase"]
        tone = sc_spec["tone"]
        rows: List[Tuple[Any, ...]] = sc_spec["rows"]

        narration = " ".join(r[0].strip() for r in rows)
        visuals: List[ResearchedBeat] = []

        for beat_idx, row in enumerate(rows, 1):
            quote, spec, src_term, vis_term, relation = row[:5]
            visible_text = list(row[5]) if len(row) > 5 else []
            shot_type, raw_desc = spec.split("|", 1)
            shot_type = shot_type.strip()
            raw_desc = raw_desc.strip()

            based_on = None
            preserve = ""
            change = raw_desc

            is_char_free = shot_type in ("still_life", "environment") or (
                shot_type in ("white_card", "white_isolated", "visual_diagram", "cutaway_detail", "concept_metaphor", "macro_prop")
                and not any(
                    k in raw_desc.lower()
                    for k in ("stickman", "doodle", "student", "learner", "person", "people", "human", "figure", "researcher", "scientist", "participant", "librarian")
                )
            )
            beat_char_ids = [] if is_char_free else ["CH01"]
            has_character = not is_char_free

            has_own_bg = any(w in raw_desc.lower() for w in ("field", "canvas", "background", "stage", "bedroom"))
            full_desc = raw_desc if (shot_type in ("white_card", "visual_diagram") or has_own_bg) else f"{raw_desc} Setting: {setting}"

            explanation = {
                "quote": quote,
                "relation": relation,
                "source_terms": [src_term],
                "visual_terms": [vis_term],
            }

            visuals.append(
                ResearchedBeat(
                    image_id=f"{scene_id}_I{beat_idx}",
                    description=full_desc,
                    anchor_quote=quote,
                    reason="Show the concrete object, comparison, or action at its spoken anchor.",
                    character_ids=beat_char_ids,
                    visible_text=visible_text,
                    effect="cut",
                    based_on=based_on,
                    preserve=preserve,
                    change=change,
                    shot_type=shot_type,
                    allow_expression_shift=None,
                    has_character=has_character,
                    explanation=explanation,
                )
            )

        is_last = idx == total_scenes
        p_tail = DEFAULT_P_TAIL_LAST if is_last else DEFAULT_P_TAIL_PARA
        pause_sec, _, _ = extract_pauses(narration)
        syl = count_syllables(narration, lang="vi")
        duration = round(pause_sec + (syl / NOMINAL_SPEECH_RATE) + p_tail, 2)

        scenes.append(
            ResearchedScene(
                scene_id=scene_id,
                title=title,
                purpose=purpose,
                duration=duration,
                narration=narration,
                requirements=list(sc_spec["requirements"]),
                source_ids=list(sc_spec["source_ids"]),
                character_ids=["CH01"],
                action=rows[0][1].split("|", 1)[1].strip(),
                setting=setting,
                camera="Narration-led full-frame compositions",
                visual_beats=visuals,
                claim_facts=list(sc_spec["claim_facts"]),
                tone=tone,
                narrative_phase=narrative_phase,
            )
        )

    sources = [
        {
            "id": "SRC01",
            "title": "A Method of Estimating Plane Vulnerability Based on Damage of Returning Aircraft",
            "reference": "Abraham Wald (1943). Statistical Research Group, Columbia University. CRC 432.",
            "facts": [
                "Những chiếc máy bay trúng đạn vào động cơ và buồng lái không thể quay về.",
                "Cần bọc thép vào vị trí máy bay không có lỗ đạn.",
                "Thống kê ban đầu chỉ ghi nhận dữ liệu từ những máy bay sống sót.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Fooled by Randomness: The Hidden Role of Chance in Life and in the Markets",
            "reference": "Nassim Nicholas Taleb (2001). Random House. ISBN: 978-0812975215.",
            "facts": [
                "Nghĩa địa vô hình của người thất bại luôn bị truyền thông bỏ qua.",
                "Tri thức tiêu cực tập trung vào việc loại bỏ sai lầm.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Poor Charlie's Almanack: The Wit and Wisdom of Charles T. Munger",
            "reference": "Peter D. Kaufman (2005). Donning Company Publishers. ISBN: 978-1578643035.",
            "facts": [
                "Nguyên lý nghịch đảo giúp tránh xa những cái chết ngu ngốc.",
                "Biên độ an toàn bảo vệ con người trước biến cố bất ngờ.",
            ],
        },
    ]

    required_points = [
        {"id": sc["requirements"][0], "text": sc["purpose"]}
        for sc in STORY_SCENES
    ]

    visual_hook = (
        "Raw freehand 2D Vietnamese indie doodle on a flat slate-navy (#2E4361) stage: "
        "a white-head doodle stickman in a casual cerulean blue shirt (#3B82C4) looks up at one golden trophy inside a bright yellow spotlight cone "
        "while standing above a deep ocean trench filled with sunken propeller bomber planes"
    )
    text_overlay = "BẪY NGƯỜI SỐNG SÓT"
    contrast_pair = "Ánh đèn kẻ thắng cuộc vs. Đáy biển người thất bại"
    thumbnail_prompt = (
        f"16:9 YouTube thumbnail poster in raw freehand 2D Vietnamese indie doodle style on a flat slate-navy (#2E4361) stage "
        f"with bold pitch-black (#000000) marker contours and 100% flat MS-Paint paint-bucket fills. "
        f"Focal subject: {visual_hook}. Contrast: {contrast_pair}. "
        f"Top-center bold hand-drawn golden-yellow (#FACC15) uppercase Vietnamese lettering '{text_overlay}' with thick pitch-black (#000000) marker outline, zero drop shadow."
    )

    packaging = PackagingSpec(
        youtube_title="Bẫy Người Sống Sót: Sao Chép Thành Công Là Vô Nghĩa",
        visual_hook=visual_hook,
        text_overlay=text_overlay,
        contrast_pair=contrast_pair,
        channel_pillar=DEFAULT_CHANNEL_PILLAR,
        funnel_tier="tier_1_broad",
        seo_keywords=[
            "bẫy người sống sót",
            "thiên kiến kẻ sống sót",
            "survivorship bias",
            "abraham wald máy bay 1943",
            "tư duy trừ lùi",
            "tri thức tiêu cực",
            "charlie munger",
            "tư duy phản biện",
        ],
        thumbnail_prompt=thumbnail_prompt,
        layout_mode="integrated_poster",
        typography_style="Bold hand-drawn golden-yellow (#FACC15) uppercase poster lettering with thick pitch-black (#000000) marker outline",
    )

    total_est = sum(s.duration for s in scenes)
    min_dur = round(max(180.0, total_est * 0.80), 1)
    max_dur = round(total_est * 1.25, 1)

    return ResearchedTopic(
        topic="Thiên Kiến Kẻ Sống Sót (Survivorship Bias) & Vũ Khí Tư Duy Trừ Lùi",
        audience="Người trẻ đi làm, người khởi nghiệp, nhà đầu tư cá nhân và người quan tâm đến phương pháp luận tư duy nhận thức tại Việt Nam",
        goal="Giải mã cái bẫy của những công thức thành công qua Thiên kiến Kẻ Sống Sót, bài toán máy bay ném bom năm 1943 của Abraham Wald, phản biện ranh giới học hỏi, và áp dụng 2 bước lọc Tư duy Trừ Lùi của Charlie Munger.",
        video_type="research_explainer",
        min_duration=min_dur,
        max_duration=max_dur,
        style=STYLE_DESCRIPTION,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        subtitles=False,
        voice="VietNarrator",
        speed=1.0,
        visual_pacing_profile="full_frame_v1",
        conversational_facts=True,
        sources=sources,
        required_points=required_points,
        characters=[
            {
                "id": "CH01",
                "name": "Nhân vật người que đầu tròn trắng doodle 2D",
                "appearance": CAST_APPEARANCE,
                "outfit": DEFAULT_OUTFIT,
            }
        ],
        scenes=scenes,
        packaging=packaging,
        human_editorial=build_human_editorial(),
    )


def export_package(output_dir: Path, topic: ResearchedTopic) -> Dict[str, Any]:
    if any(
        (output_dir / name).exists()
        for name in ("revisions", "execution-control.json", "brief-current.json", "integrity.json", "workflow.json")
    ):
        raise ValueError(f"ACTIVE_JOB_DESTINATION: {output_dir} already contains active job files")

    output_dir.mkdir(parents=True, exist_ok=True)
    brief_data = build_brief_v3(topic, system_root=SYS_DIR)
    brief_data["enforce_phonetic_gate"] = True

    brief_hash = compute_brief_hash(brief_data)
    content_data = build_content_v3(topic, brief_data, brief_hash, brief_revision=1)
    content_data["enforce_phonetic_gate"] = True

    for sc_spec, sc_dict in zip(topic.scenes, content_data["scenes"], strict=True):
        for beat_spec, img_dict in zip(sc_spec.visual_beats, sc_dict["images"], strict=True):
            if beat_spec.explanation is not None:
                img_dict["explanation"] = dict(beat_spec.explanation)
            if beat_spec.has_character is not None:
                img_dict["has_character"] = bool(beat_spec.has_character)
            if beat_spec.shot_type == "full_scene":
                img_dict["shot_type"] = "full_scene"
                img_dict["based_on"] = None
                img_dict["preserve"] = ""
                img_dict["change"] = beat_spec.change
                img_dict.pop("allow_expression_shift", None)

    # Compile-check all 1.7.0 Flow prompts
    compile_errors: List[str] = []
    for sc_dict in content_data["scenes"]:
        for img_dict in sc_dict["images"]:
            try:
                compile_flow_prompt(
                    "NanoBanana2Lite",
                    "scene",
                    {
                        "description": img_dict["description"],
                        "aspect_ratio": "16:9",
                        "allowed_text": img_dict.get("visible_text", []),
                        "shot_type": img_dict["shot_type"],
                        "has_character": bool(img_dict.get("has_character", False)),
                        "character_free": not bool(img_dict.get("has_character", False)),
                    },
                    version="1.7.0",
                )
            except Exception as exc:
                compile_errors.append(f"{img_dict['id']}: {exc}")

    outline_data = {"outline": content_data["outline"]}
    script_data = generate_script_json(topic)

    checker = ScriptCadenceChecker(
        nominal_rate=NOMINAL_SPEECH_RATE,
        max_sentence_syllables=None,
        max_clause_syllables=None,
        max_dramatic_pauses=4,
        forbid_opening_pause=True,
        max_opening_hook_syllables=18,
    )
    cadence_report = checker.check_scenes(script_data)

    claim_facts = {clean_sentence(f) for src in brief_data.get("sources", []) for f in src.get("facts", [])}
    claim_facts.update(clean_sentence(c.get("fact", "")) for c in content_data.get("claims", []) if c.get("fact"))
    claim_facts.update(clean_sentence(c.get("quote", "")) for c in content_data.get("claims", []) if c.get("quote"))

    diversity_report = lint_script(
        content_data["scenes"],
        corpus_dir=SYS_DIR / "exports",
        claim_facts=claim_facts,
        topic_title=brief_data.get("topic", ""),
        enforce_rhythm_variance=True,
        characters=content_data.get("characters"),
        style=content_data.get("style"),
        enforce_breathing_room=True,
    )

    valid_contracts, contract_errors = validate_production_bundle(
        system_root=SYS_DIR,
        brief_data=brief_data,
        content_data=content_data,
        brief_revision=1,
    )

    packaging_warnings = check_packaging_and_localization(
        brief_data,
        scenes=topic.scenes,
        check_opening_hook=True,
    )
    spoken_fact_warnings = check_conversational_spoken_facts(brief_data.get("sources", []), max_syllables=20)
    editorial_errors = validate_human_editorial(brief_data)
    short_errors = validate_short(brief_data)
    explanation_errors = validate_explanations(content_data)
    clearance_errors = validate_clearance_and_labels(content_data)
    plan_estimates = estimates(brief_data, content_data)

    phonetic_issues = []
    for sc in content_data["scenes"]:
        norm_text = normalize_for_tts(sc["narration"])
        unnorm = detect_unnormalized_tokens(norm_text)
        if unnorm:
            phonetic_issues.append({"scene_id": sc["id"], "tokens": unnorm})
        if re.search(r"\d", sc["narration"]):
            phonetic_issues.append({"scene_id": sc["id"], "raw_digits": re.findall(r"\d+", sc["narration"])})

    brief_file = output_dir / "brief.json"
    content_file = output_dir / "content.json"
    outline_file = output_dir / "outline.json"
    script_file = output_dir / "script.json"
    cadence_file = output_dir / "cadence_report.json"

    brief_file.write_text(serialize_brief_json(brief_data), encoding="utf-8")
    content_file.write_text(json.dumps(content_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    outline_file.write_text(json.dumps(outline_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    script_file.write_text(json.dumps(script_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    cadence_file.write_text(json.dumps(cadence_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "output_dir": str(output_dir),
        "brief_file": str(brief_file),
        "content_file": str(content_file),
        "outline_file": str(outline_file),
        "script_file": str(script_file),
        "cadence_file": str(cadence_file),
        "brief_hash": brief_hash,
        "valid_contracts": valid_contracts,
        "contract_errors": contract_errors,
        "compile_errors": compile_errors,
        "packaging_warnings": packaging_warnings,
        "spoken_fact_warnings": spoken_fact_warnings,
        "editorial_errors": editorial_errors,
        "short_errors": short_errors,
        "explanation_errors": explanation_errors,
        "clearance_errors": clearance_errors,
        "estimate_warnings": plan_estimates["warnings"],
        "phonetic_issues": phonetic_issues,
        "cadence_report": cadence_report,
        "diversity_report": diversity_report,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build survivorship-bias-16x9 Schema 3.0 blueprint.")
    parser.add_argument(
        "--out",
        "--output-dir",
        dest="out",
        type=Path,
        action="append",
        help="Output directory (can be specified multiple times)",
    )
    args = parser.parse_args()
    targets = args.out or [
        Path("/tmp/survivorship-bias-16x9-blueprint"),
    ]

    topic = build_topic()
    all_ok = True
    for target in targets:
        res = export_package(target, topic)
        summary = {
            "output_dir": res["output_dir"],
            "brief_hash": res["brief_hash"],
            "valid_contracts": res["valid_contracts"],
            "contract_errors": res["contract_errors"],
            "compile_errors": res["compile_errors"],
            "packaging_warnings": res["packaging_warnings"],
            "spoken_fact_warnings": res["spoken_fact_warnings"],
            "editorial_errors": res["editorial_errors"],
            "short_errors": res["short_errors"],
            "explanation_errors": res["explanation_errors"],
            "clearance_errors": res["clearance_errors"],
            "estimate_warnings": res["estimate_warnings"],
            "phonetic_issues": res["phonetic_issues"],
            "cadence_status": res["cadence_report"]["status"],
            "cadence_warnings_count": res["cadence_report"]["warnings_count"],
            "total_duration": res["cadence_report"]["total_duration"],
            "total_syllables": res["cadence_report"]["total_actual_syllables"],
            "diversity_status": res["diversity_report"]["status"],
            "diversity_violations": res["diversity_report"]["violations"],
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        if (
            not res["valid_contracts"]
            or res["contract_errors"]
            or res["compile_errors"]
            or res["packaging_warnings"]
            or res["spoken_fact_warnings"]
            or res["editorial_errors"]
            or res["short_errors"]
            or res["explanation_errors"]
            or res["clearance_errors"]
            or res["estimate_warnings"]
            or res["phonetic_issues"]
            or res["cadence_report"]["status"] != "PASS"
            or res["diversity_report"]["status"] != "PASS"
        ):
            all_ok = False
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
