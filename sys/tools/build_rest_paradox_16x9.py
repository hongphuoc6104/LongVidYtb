#!/usr/bin/env python3
"""Build and validate the Schema 3.0 production blueprint for rest-paradox-16x9."""
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
    build_thumbnail_poster_prompt,
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
        "title": "Mở mắt đã bật màn hình",
        "purpose": "Mở bài bằng cú tát sự thật về việc lướt video ngắn lúc nghỉ ngơi bắt não phải tăng ca",
        "setting": "Flat warm paper-cream (#F8F0DC) 2D orthographic bedroom stage.",
        "narrative_phase": "hook",
        "tone": "narrative_warm",
        "requirements": ["R01"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Bạn tưởng lướt là nghỉ.",
                "white_card|Raw freehand 2D doodle on a solid flat warm paper-cream (#F8F0DC) field: the white-head doodle stickman lies motionless on a flat rectangle bed holding a phone under a resting body label while above the round white head a pink cartoon brain with thin black stick legs lifts heavy barbells on a moving belt.",
                "là nghỉ",
                "resting body",
                "comparison",
                [
                    {"text": "THÂN ĐANG NGHỈ", "placement": "above resting body", "object": "resting body"},
                    {"text": "NÃO TĂNG CA", "placement": "above pink cartoon brain", "object": "pink cartoon brain"},
                ],
            ),
            (
                "Thật ra, não bạn",
                "cutaway_detail|Flat 2D front close-up of the oversized pure-white (#FFFFFF) round head of the doodle stickman on a pillow: low-set black dot eyes look at a phone while an inner-head thought window inside the upper white head shows a miniature stickman pulling a red emergency alarm lever (!).",
                "não bạn",
                "inner-head thought window",
                "structure",
            ),
            (
                "đang làm thêm giờ.",
                "concept_metaphor|Flat 2D doodle on a solid apricot-peach (#F2B88B) field: a tired red cartoon brain (#D9534F) wearing a yellow hard hat hammers an overtime work desk right on top of the stickman's round white head while sweat drops fly.",
                "thêm giờ",
                "overtime work desk",
                "cause_effect",
                [
                    {"text": "TĂNG CA", "placement": "above overtime work desk", "object": "overtime work desk"},
                ],
            ),
            (
                "Sáng vừa mở mắt,",
                "full_scene|Flat 2D side-on orthographic bedroom with a pale ice-blue (#CBE0E0) wall and a crooked square sunrise window: the white-head doodle stickman lies under a flat blanket opening one sleepy dot eye while one long black wire arm reaches for a vibrating smartphone.",
                "mở mắt",
                "vibrating smartphone",
                "context",
            ),
            (
                "tay đã mò điện thoại.",
                "variation|The white-head doodle stickman props up on one flat pillow grabbing the smartphone with a round white circle hand and pulling the screen right in front of two tired dot eyes.",
                "điện thoại",
                "grabbing the smartphone",
                "context",
            ),
            (
                "Lướt hết video ngắn,",
                "concept_metaphor|Flat 2D side view on a warm paper-cream (#F8F0DC) field: the white-head doodle stickman holds the phone close while a barrage of hand-drawn black arrows shoots from rapid short video clips on the screen straight into the stickman's wide dot eyes.",
                "video ngắn",
                "short video clips",
                "progression",
            ),
            (
                "lại qua tóm tắt phim.",
                "white_card|Raw freehand 2D doodle on a solid flat apricot-peach (#F2B88B) canvas: the white-head doodle stickman with dizzy spiral eyes stands trapped inside a circular loop of hand-drawn black arrows connecting a vertical phone card and a fast-forward film reel card.",
                "tóm tắt phim",
                "film reel card",
                "grouping",
                [
                    {"text": "VIDEO NGẮN", "placement": "below vertical phone card", "object": "vertical phone card"},
                    {"text": "TÓM TẮT PHIM", "placement": "below film reel card", "object": "film reel card"},
                ],
            ),
            (
                "Mắt còn díp lại.",
                "full_scene|Flat 2D front close-up of the white-head doodle stickman sitting on the flat bed edge on a warm paper-cream (#F8F0DC) stage: drooping half-closed eyelids with dark under-eye bags, a big crooked yawn, and a dizzy scribble coil above the round white head.",
                "mắt còn",
                "drooping half-closed eyelids",
                "context",
            ),
            (
                "Ngón cái vẫn lướt.",
                "variation|The white-head doodle stickman keeps both eyes shut in U-shapes while the black wire arm holds the phone up and the white cartoon thumb flicks upward with fast black motion lines; expression shift.",
                "ngón cái",
                "cartoon thumb flicks upward",
                "context",
            ),
            (
                "Chưa kịp đánh răng,",
                "concept_metaphor|Flat 2D doodle on a soft sage-green (#93A88C) field: the white-head doodle stickman lies flat on the bed scrolling the phone while an overhead thought cloud shows an untouched toothbrush and cup crossed out with a bold red X and question mark (?).",
                "đánh răng",
                "untouched toothbrush",
                "context",
            ),
            (
                "đã xem xong chục video.",
                "cutaway_detail|Flat 2D front close-up on a warm paper-cream (#F8F0DC) field: the oversized round white head of the doodle stickman is drawn like a transparent jar crammed full of ten jumbled miniature video frames with black smoke squiggles rising from the top of the head.",
                "chục video",
                "ten jumbled miniature video frames",
                "quantity",
            ),
        ],
    },
    {
        "scene_id": "SC02",
        "title": "Dòng âm thanh lấp kín mọi khoảng trống",
        "purpose": "Neo cảm xúc với thói quen bật video ngắn và truyện lồng tiếng từ bàn ăn tới lúc đi ngủ",
        "setting": "Flat warm paper-cream (#F8F0DC) 2D front-on dining table stage.",
        "narrative_phase": "lead_in",
        "tone": "narrative_warm",
        "requirements": ["R02"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Bưng chén cơm lên,",
                "full_scene|Flat 2D front-on orthographic view on a warm paper-cream (#F8F0DC) background: the white-head doodle stickman in a flat cerulean-blue (#3B82C4) shirt sits behind a single horizontal brown table line holding a white rice bowl with a question mark (?) above the head.",
                "chén cơm",
                "white rice bowl",
                "context",
            ),
            (
                "phải dựng điện thoại trước mặt mới ăn nổi.",
                "variation|The white-head doodle stickman props a smartphone against a water glass right in front of the rice bowl, leaning forward with wide dot eyes glued to the screen while poking chopsticks against the cheek; expression shift.",
                "dựng điện thoại",
                "props a smartphone",
                "context",
            ),
            (
                "Ngồi học, ngồi làm,",
                "full_scene|Flat 2D front-on stage on a soft sage-green (#93A88C) background: the white-head doodle stickman sits at a flat brown desk typing on a crooked freehand laptop while a white earbud sticks out of the round white head emitting black sound wave squiggles.",
                "ngồi học",
                "crooked freehand laptop",
                "context",
            ),
            (
                "tai vẫn nghe truyện lồng tiếng Trung.",
                "cutaway_detail|Flat 2D front close-up of the stickman's oversized pure-white (#FFFFFF) round head: two earbuds on the sides fire dense streams of black sound-wave arrows straight into the transparent upper head where a pink cartoon brain spins dizzily.",
                "lồng tiếng",
                "streams of black sound-wave arrows",
                "cause_effect",
            ),
            (
                "Vô nhà vệ sinh cũng cầm theo.",
                "visual_diagram|Raw freehand 2D 3-stage horizontal progression from left to right on a flat warm paper-cream (#F8F0DC) field connected by dashed black arrows (--->): the white-head doodle stickman eating with the phone, working with earbuds, and sitting behind a simple bathroom door holding the phone up.",
                "nhà vệ sinh",
                "bathroom door",
                "progression",
                [
                    {"text": "LÚC ĂN", "placement": "above first stickman", "object": "eating with the phone"},
                    {"text": "LÚC NGHỈ", "placement": "above third stickman", "object": "bathroom door"},
                ],
            ),
            (
                "Không có là thấy thiếu thiếu.",
                "concept_metaphor|Flat 2D doodle on a solid apricot-peach (#F2B88B) field: the white-head doodle stickman stands jittering with sweat drops and empty black wire hands patting pockets while a dashed thought cloud above the head shows a missing phone silhouette with a big question mark (?).",
                "thiếu thiếu",
                "missing phone silhouette",
                "context",
            ),
            (
                "Tối lên giường đi ngủ,",
                "full_scene|Flat 2D night bedroom stage with a solid slate-navy (#2E4361) wall and a small four-pane crescent-moon window: the white-head doodle stickman lies under a flat blue blanket (#4B6584) with a bright smartphone still playing on the pillow beside the round white head.",
                "đi ngủ",
                "lies under a flat blue blanket",
                "context",
            ),
            (
                "vẫn mở một video chạy nền.",
                "variation|The white-head doodle stickman closes both eyes in U-shapes pretending to sleep while jagged black sound-wave lines from the phone speaker on the pillow crawl directly into the round white head; expression shift.",
                "chạy nền",
                "jagged black sound-wave lines",
                "context",
            ),
            (
                "Tính ra cả ngày,",
                "white_card|Raw freehand 2D doodle on a solid apricot-peach (#F2B88B) field: a single large lopsided twenty-four-hour clock face drawn in bold black marker ink completely packed with looping play triangles and sound waves.",
                "cả ngày",
                "twenty-four-hour clock face",
                "structure",
            ),
            (
                "đầu mình chưa được yên lấy một phút.",
                "cutaway_detail|Flat 2D night bedroom (#2E4361) inner-head cutaway matching the Xấu Vê Nờ t=288s layout: the white-head doodle stickman lies awake on the pillow with tired dot eyes while a glowing cloud window inside the upper white round head shows a miniature stickman sitting knees-to-chest covering both ears.",
                "một phút",
                "miniature stickman sitting knees-to-chest",
                "structure",
            ),
        ],
    },
    {
        "scene_id": "SC03",
        "title": "Nỗi sợ ba mươi giây tĩnh lặng",
        "purpose": "Chỉ ra cảm giác bồn chồn khi thiếu kích thích âm thanh và hình ảnh dù chỉ vài chục giây",
        "setting": "Flat dusty-blue 2D work desk background.",
        "narrative_phase": "lived_friction",
        "tone": "reflective_slow",
        "requirements": ["R03"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Thử tắt hết âm thanh ba mươi giây xem.",
                "still_life|A simple 2D stopwatch showing thirty seconds beside a face-down smartphone on a flat desk.",
                "ba mươi giây",
                "thirty seconds",
                "quantity",
            ),
            (
                "Thấy trống trống liền.",
                "full_scene|The young person sits at a flat work desk staring uneasily at the silent room.",
                "trống trống",
                "staring uneasily",
                "context",
            ),
            (
                "Tay ngứa ngáy đi tìm điện thoại.",
                "variation|The young person taps fingers restlessly near the face-down phone; expression shift.",
                "ngứa ngáy",
                "taps fingers restlessly",
                "context",
            ),
            (
                "Mình hay gọi vậy là xả hơi.",
                "white_card|Two contrasting labels comparing perceived relaxation and actual sensory flooding on pure white.",
                "xả hơi",
                "perceived relaxation",
                "comparison",
                [
                    {"text": "TƯỞNG LÀ XẢ HƠI", "placement": "left column header", "object": "left column"},
                    {"text": "SỢ KHOẢNG LẶNG", "placement": "right column header", "object": "right column"},
                ],
            ),
            (
                "Nói thật, mình đang sợ yên lặng.",
                "still_life|A heavy headphones icon pressing down over a quiet thought bubble on the flat desk.",
                "yên lặng",
                "quiet thought bubble",
                "cause_effect",
            ),
            (
                "Mà xem càng nhiều,",
                "full_scene|The young person picks up the phone again with slumped shoulders at the work desk.",
                "càng nhiều",
                "picks up the phone",
                "context",
            ),
            (
                "đầu lại càng lờ đờ.",
                "variation|The young person rests their chin on one hand with exhausted eyes while the clip plays.",
                "lờ đờ",
                "exhausted eyes",
                "context",
            ),
            (
                "Vậy sao nằm im xem điện thoại",
                "still_life|A flat battery gauge dropping to one red bar beside an open video app.",
                "nằm im",
                "battery gauge",
                "comparison",
            ),
            (
                "lại mệt hơn cả đi làm?",
                "white_card|A resting chair icon weighed down by a heavy media overload block on pure white.",
                "mệt hơn",
                "heavy media overload block",
                "cause_effect",
            ),
        ],
    },
    {
        "scene_id": "SC04",
        "title": "Ngộ nhận về bộ não đứng yên",
        "purpose": "Lật tẩy hiểu lầm rằng ngừng làm việc tay chân là não tự động được nghỉ ngơi",
        "setting": "Flat sage-green 2D lounge chair background.",
        "narrative_phase": "problem",
        "tone": "analytical_crisp",
        "requirements": ["R04"],
        "source_ids": ["SRC01"],
        "claim_facts": [
            (
                "Người nằm yên, nhưng não vẫn đốt năng lượng gần như lúc làm việc.",
                "SRC01",
                "Người nằm yên, nhưng não vẫn đốt năng lượng gần như lúc làm việc.",
            )
        ],
        "rows": [
            (
                "Mình hiểu sai chữ nghỉ ngơi.",
                "white_card|A crossed-out equals sign between a lying body icon and a switched-off brain icon on pure white.",
                "nghỉ ngơi",
                "crossed-out equals sign",
                "comparison",
                [
                    {"text": "NGỪNG TAY CHÂN", "placement": "below lying body", "object": "lying body"},
                    {"text": "NÃO TỰ TẮT?", "placement": "below brain icon", "object": "brain icon"},
                ],
            ),
            (
                "Cứ tưởng người nằm im trên nệm",
                "environment|A simple 2D lounge chair with a soft cushion on a flat sage-green background.",
                "nằm im",
                "lounge chair",
                "context",
            ),
            (
                "thì não cũng tắt máy theo.",
                "full_scene|The young person reclines on the lounge chair holding a smartphone above their chest.",
                "tắt máy",
                "reclines on the lounge chair",
                "context",
            ),
            (
                "Không phải đâu.",
                "variation|The young person frowns slightly as a bright alert indicator appears above their head.",
                "không phải",
                "alert indicator",
                "context",
            ),
            (
                "Người nằm yên,",
                "still_life|A stationary pair of shoes resting beside an active energy meter on the floor.",
                "nằm yên",
                "stationary pair of shoes",
                "comparison",
            ),
            (
                "nhưng não vẫn đốt năng lượng gần như lúc làm việc.",
                "visual_diagram|Simple 2D energy distribution diagram showing a small brain icon drawing a wide stream of fuel bars on pure white.",
                "năng lượng",
                "fuel bars",
                "quantity",
                [
                    {"text": "CƠ THỂ NGHỈ", "placement": "left side", "object": "body gauge"},
                    {"text": "NÃO ĐỐT NĂNG LƯỢNG", "placement": "right side", "object": "fuel bars"},
                ],
            ),
            (
                "Não không có nút tắt như bóng đèn.",
                "still_life|A simple 2D light switch beside a continuously humming circuit board on a flat surface.",
                "bóng đèn",
                "light switch",
                "comparison",
            ),
            (
                "Nó chỉ đổi qua việc khác.",
                "full_scene|The young person looks between a closed laptop and an inward thought diagram beside the chair.",
                "việc khác",
                "closed laptop",
                "progression",
            ),
            (
                "Tự dọn nhà bên trong.",
                "variation|The young person points toward the inward maintenance cycle schematic beside the chair.",
                "dọn nhà",
                "maintenance cycle schematic",
                "structure",
            ),
        ],
    },
    {
        "scene_id": "SC05",
        "title": "Mạng lưới dọn rác âm thầm của não",
        "purpose": "Giải phẫu cơ chế mạng lưới chế độ mặc định giúp não tự dọn dẹp và sắp xếp ký ức khi thẩn thơ",
        "setting": "Flat warm-sand 2D neural studio background.",
        "narrative_phase": "causal_mechanism",
        "tone": "analytical_crisp",
        "requirements": ["R05"],
        "source_ids": ["SRC01"],
        "claim_facts": [
            (
                "Nó chỉ chạy khi bạn không xem gì, không nghe gì.",
                "SRC01",
                "Nó chỉ chạy khi bạn không xem gì, không nghe gì.",
            ),
            (
                "Lúc yên tĩnh, não sắp xếp lại ký ức và dọn bớt rác trong ngày.",
                "SRC01",
                "Lúc yên tĩnh, não sắp xếp lại ký ức và dọn bớt rác trong ngày.",
            ),
        ],
        "rows": [
            (
                "Giới khoa học gọi nó là mạng lưới mặc định.",
                "full_scene|A simple 2D neuroscientist stands beside a brain network board on a flat warm-sand background.",
                "mạng lưới mặc định",
                "brain network board",
                "context",
            ),
            (
                "Kiểu như chế độ dọn nhà của não.",
                "variation|The neuroscientist traces connected nodes across the 2D brain diagram with a wooden pointer.",
                "chế độ dọn nhà",
                "connected nodes",
                "structure",
            ),
            (
                "Nó chỉ chạy khi bạn",
                "visual_diagram|Simple 2D toggle diagram showing external input turning off so the internal cleanup network turns on.",
                "chỉ chạy",
                "internal cleanup network",
                "cause_effect",
                [
                    {"text": "NGỪNG KÍCH THÍCH", "placement": "top switch", "object": "top switch"},
                    {"text": "BẬT CHẾ ĐỘ DỌN DẸP", "placement": "bottom network", "object": "bottom network"},
                ],
            ),
            (
                "không xem gì, không nghe gì.",
                "still_life|An unplugged audio jack resting beside a calm organizing tray on a flat table.",
                "không nghe gì",
                "unplugged audio jack",
                "cause_effect",
            ),
            (
                "Giống thư viện lúc đóng cửa.",
                "environment|A quiet 2D library room with closed doors and neat bookshelves on a flat warm-sand background.",
                "thư viện",
                "library room",
                "context",
            ),
            (
                "Khách về hết,",
                "still_life|A closed sign hanging on the library door beside an empty reception desk.",
                "về hết",
                "closed sign",
                "context",
            ),
            (
                "cô thủ thư mới đi cất sách.",
                "full_scene|A simple 2D librarian collects scattered note cards from a reading table and sorts them onto shelves.",
                "cất sách",
                "collects scattered note cards",
                "progression",
            ),
            (
                "Lúc yên tĩnh, não sắp xếp lại ký ức",
                "variation|The librarian places labeled memory folders neatly into indexed shelf slots.",
                "ký ức",
                "labeled memory folders",
                "grouping",
            ),
            (
                "và dọn bớt rác trong ngày.",
                "white_card|A clean sorted shelf on the left contrasted with a swept trash bin of noise scraps on pure white.",
                "dọn bớt rác",
                "trash bin of noise scraps",
                "comparison",
                [
                    {"text": "LƯU KÝ ỨC", "placement": "below sorted shelf", "object": "sorted shelf"},
                    {"text": "DỌN RÁC TIN", "placement": "below trash bin", "object": "trash bin"},
                ],
            ),
        ],
    },
    {
        "scene_id": "SC06",
        "title": "Cơn lũ dữ liệu khóa chặt đội dọn rác",
        "purpose": "Giải thích vì sao việc mở video và âm thanh liên tục ngăn cản não tự phục hồi",
        "setting": "Flat slate-blue 2D library hall background.",
        "narrative_phase": "causal_mechanism",
        "tone": "analytical_crisp",
        "requirements": ["R06"],
        "source_ids": ["SRC02"],
        "claim_facts": [
            (
                "Lướt liên tục lúc rảnh làm não không có lúc nào tự hồi phục.",
                "SRC02",
                "Lướt liên tục lúc rảnh làm não không có lúc nào tự hồi phục.",
            )
        ],
        "rows": [
            (
                "Mà nếu vừa ăn vừa xem,",
                "full_scene|The young person sits in the library hall holding both a spoon and a smartphone streaming clips.",
                "vừa ăn vừa xem",
                "spoon and a smartphone",
                "context",
            ),
            (
                "đi vệ sinh vẫn đeo tai nghe thì sao?",
                "variation|The young person keeps earbuds in while more paper flyers pour onto the table.",
                "tai nghe",
                "keeps earbuds in",
                "cause_effect",
            ),
            (
                "Là mình mở cửa thư viện cả ngày lẫn đêm.",
                "environment|Wide 2D library doors propped open with crates of unsorted flyers spilling across the floor.",
                "mở cửa",
                "doors propped open",
                "cause_effect",
            ),
            (
                "Khách cứ ùa vô liên tục.",
                "still_life|A conveyor belt dumping colorful video cards and audio reels onto an overflowing desk.",
                "ùa vô",
                "conveyor belt dumping",
                "quantity",
            ),
            (
                "Cô thủ thư đâu có rảnh mà dọn.",
                "full_scene|The 2D librarian stands trapped behind a towering pile of unsorted media cards.",
                "thủ thư",
                "towering pile of unsorted media cards",
                "cause_effect",
            ),
            (
                "Cứ phải tiếp khách mới hoài.",
                "variation|The librarian frantically catches incoming flyers with both hands; expression shift.",
                "khách mới",
                "catches incoming flyers",
                "context",
            ),
            (
                "Lướt liên tục lúc rảnh",
                "visual_diagram|A 2D padlock clamping shut over the brain cleanup mechanism while a video feed arrow pushes inward on pure white.",
                "lúc rảnh",
                "padlock clamping shut",
                "cause_effect",
                [
                    {"text": "NẠP VIDEO LIÊN TỤC", "placement": "above feed arrow", "object": "feed arrow"},
                    {"text": "KHÓA TỰ PHỤC HỒI", "placement": "below padlock", "object": "padlock"},
                ],
            ),
            (
                "làm não không có lúc nào tự hồi phục.",
                "still_life|A jammed wooden ratchet mechanism buried under tangled film strips on a flat table.",
                "hồi phục",
                "jammed wooden ratchet",
                "cause_effect",
            ),
            (
                "Rác cứ chất đống, ngày này qua ngày khác.",
                "white_card|A mountain of unsorted media icons pressing down on a tiny brain silhouette on pure white.",
                "chất đống",
                "mountain of unsorted media icons",
                "quantity",
            ),
        ],
    },
    {
        "scene_id": "SC07",
        "title": "Chi phí chuyển đổi ngữ cảnh mỗi ba mươi giây",
        "purpose": "Mô hình hóa chi phí năng lượng khi não phải nhảy qua hàng chục bối cảnh và cảm xúc trái ngược",
        "setting": "Flat cream-white 2D observation lab background.",
        "narrative_phase": "explanation",
        "tone": "analytical_crisp",
        "requirements": ["R07"],
        "source_ids": ["SRC02"],
        "claim_facts": [
            (
                "Mỗi lần nhảy cảnh, não phải bẻ lái và tốn thêm sức.",
                "SRC02",
                "Mỗi lần nhảy cảnh, não phải bẻ lái và tốn thêm sức.",
            ),
            (
                "Phần chú ý cũ còn vương lại, làm đầu mình lùng bùng.",
                "SRC02",
                "Phần chú ý cũ còn vương lại, làm đầu mình lùng bùng.",
            ),
        ],
        "rows": [
            (
                "Còn một cái mệt nữa.",
                "still_life|A 2D fuel tank gauge dropping rapidly beside three mismatched video frames on a lab bench.",
                "cái mệt",
                "fuel tank gauge",
                "cause_effect",
            ),
            (
                "Đó là nhảy cảnh liên tục.",
                "white_card|A zigzagging arrow jumping across four disconnected topic boxes on pure white.",
                "nhảy cảnh",
                "zigzagging arrow",
                "structure",
                [
                    {"text": "ĐỔI NGỮ CẢNH", "placement": "above zigzagging arrow", "object": "zigzagging arrow"},
                    {"text": "HAO NĂNG LƯỢNG", "placement": "below topic boxes", "object": "topic boxes"},
                ],
            ),
            (
                "Mấy nhà nghiên cứu về sự chú ý ở Mỹ đã đo được chuyện này.",
                "full_scene|A simple 2D attention researcher points at a multi-track switching board in the flat lab.",
                "sự chú ý",
                "attention researcher",
                "context",
            ),
            (
                "Mỗi lần nhảy cảnh,",
                "variation|The researcher flips three heavy lever switches in rapid succession on the board.",
                "mỗi lần",
                "flips three heavy lever switches",
                "cause_effect",
            ),
            (
                "não phải bẻ lái và tốn thêm sức.",
                "visual_diagram|Simple 2D chart showing each topic switch triggering a sharp downward step in an attention battery bar.",
                "bẻ lái",
                "attention battery bar",
                "quantity",
            ),
            (
                "Giây trước xem tai nạn.",
                "still_life|A flat screen card showing an urgent warning siren icon beside a tense exclamation mark.",
                "tai nạn",
                "warning siren icon",
                "context",
            ),
            (
                "Giây sau xem hài.",
                "still_life|A second screen card showing a laughing mask icon colliding with the previous siren card.",
                "xem hài",
                "laughing mask icon",
                "comparison",
            ),
            (
                "Giây sau nữa là phim trinh thám.",
                "full_scene|The young person sits before three rapidly spinning emotion masks in the observation lab.",
                "trinh thám",
                "spinning emotion masks",
                "progression",
            ),
            (
                "Phần chú ý cũ còn vương lại,",
                "variation|The young person tries to read a clean page while faint ghost icons from earlier clips overlap the page.",
                "vương lại",
                "faint ghost icons",
                "cause_effect",
            ),
            (
                "làm đầu mình lùng bùng.",
                "white_card|Overlapping transparent film layers turning a clear center circle into a muddy dark blotch on pure white.",
                "lùng bùng",
                "muddy dark blotch",
                "cause_effect",
                [
                    {"text": "CẶN CHÚ Ý", "placement": "above film layers", "object": "film layers"},
                    {"text": "TƯ DUY MỜ ĐỤC", "placement": "below dark blotch", "object": "dark blotch"},
                ],
            ),
        ],
    },
    {
        "scene_id": "SC08",
        "title": "Thí nghiệm căn phòng trống mười lăm phút",
        "purpose": "Chứng minh con người sợ ở một mình với suy nghĩ tới mức thà tự bấm nút chịu điện giật",
        "setting": "Flat cool-gray 2D experiment room background.",
        "narrative_phase": "explanation",
        "tone": "analytical_crisp",
        "requirements": ["R08"],
        "source_ids": ["SRC03"],
        "claim_facts": [
            (
                "Cứ ba người đàn ông thì hai người tự bấm, chỉ để khỏi ngồi yên mười lăm phút.",
                "SRC03",
                "Cứ ba người đàn ông thì hai người tự bấm, chỉ để khỏi ngồi yên mười lăm phút.",
            )
        ],
        "rows": [
            (
                "Mà mệt vậy đó,",
                "still_life|A tired hand resting beside a warm smartphone on a plain wooden table.",
                "mệt vậy",
                "tired hand",
                "context",
            ),
            (
                "sao mình vẫn mở từ sáng tới đêm?",
                "white_card|A circular loop arrow connecting a morning sun icon and a night moon icon around a phone on pure white.",
                "sáng tới đêm",
                "circular loop arrow",
                "progression",
            ),
            (
                "Có một thí nghiệm ở Mỹ,",
                "environment|A bare 2D experiment room with a single chair and a small table on a flat cool-gray background.",
                "thí nghiệm",
                "bare 2D experiment room",
                "context",
            ),
            (
                "cho người ta ngồi một mình trong phòng trống.",
                "full_scene|A simple 2D participant sits alone at the bare table with no phone and no book.",
                "phòng trống",
                "sits alone at the bare table",
                "context",
            ),
            (
                "Không điện thoại, không làm gì hết.",
                "variation|The participant looks at the empty tabletop and shifts uncomfortably in the chair.",
                "không làm gì",
                "empty tabletop",
                "context",
            ),
            (
                "Trên bàn chỉ có một cái hộp,",
                "still_life|A small 2D metal box with a red button and a tiny lightning bolt symbol on the table.",
                "cái hộp",
                "small 2D metal box",
                "context",
            ),
            (
                "bấm vô là bị điện giật nhẹ.",
                "visual_diagram|Simple 2D diagram comparing a fifteen-minute quiet timer with a shock button box on pure white.",
                "điện giật",
                "shock button box",
                "comparison",
                [
                    {"text": "IM LẶNG MƯỜI LĂM PHÚT", "placement": "below quiet timer", "object": "quiet timer"},
                    {"text": "BẤM NÚT ĐIỆN GIẬT", "placement": "below shock button", "object": "shock button"},
                ],
            ),
            (
                "Trước đó ai cũng nói thà trả tiền chứ không bấm.",
                "full_scene|The participant shakes their head firmly while pointing away from the shock box.",
                "không bấm",
                "shakes their head",
                "context",
            ),
            (
                "Vậy mà ngồi một lúc là bắt đầu bồn chồn.",
                "variation|The participant stares at the ticking wall clock as sweat drops appear; expression shift.",
                "bồn chồn",
                "ticking wall clock",
                "context",
            ),
            (
                "Cứ ba người đàn ông thì hai người tự bấm,",
                "still_life|A cartoon hand pressing the red shock button beside a small lightning spark on the table.",
                "tự bấm",
                "red shock button",
                "cause_effect",
            ),
            (
                "chỉ để khỏi ngồi yên mười lăm phút.",
                "still_life|A fifteen-minute wall timer ticking beside the pressed red button box on the table.",
                "mười lăm phút",
                "fifteen-minute wall timer",
                "quantity",
            ),
        ],
    },
    {
        "scene_id": "SC09",
        "title": "Khi nào giải trí thực sự giúp bạn hồi sức?",
        "purpose": "Phản biện hai chiều để phân biệt giải trí có điểm dừng với việc dùng tạp âm gây tê nhận thức",
        "setting": "Flat soft-ochre 2D living room background.",
        "narrative_phase": "counter_argument",
        "tone": "reflective_slow",
        "requirements": ["R09"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Vậy xem phim là xấu hả?",
                "white_card|A balance scale weighing a single movie ticket against an endless scroll reel on pure white.",
                "xấu hả",
                "balance scale",
                "comparison",
            ),
            (
                "Cũng không hẳn đâu.",
                "full_scene|The young person sits calmly in a flat soft-ochre living room holding a single storybook.",
                "không hẳn",
                "holding a single storybook",
                "context",
            ),
            (
                "Xem một bộ phim tới hết,",
                "variation|The young person watches a single complete story arc on a television screen with relaxed shoulders.",
                "tới hết",
                "single complete story arc",
                "structure",
            ),
            (
                "xong tắt máy, vậy là nghỉ thật.",
                "still_life|A clean single-line story curve ending at a clear finish flag on a flat board.",
                "nghỉ thật",
                "clear finish flag",
                "progression",
            ),
            (
                "Cái mệt là kiểu mở cho có tiếng,",
                "visual_diagram|Two side-by-side 2D panels comparing a single bounded story arc and an infinite fragmented feed on pure white.",
                "có tiếng",
                "single bounded story arc",
                "comparison",
                [
                    {"text": "CÓ ĐIỂM DỪNG", "placement": "above left panel", "object": "left panel"},
                    {"text": "TRƯỢT VÔ TẬN", "placement": "above right panel", "object": "right panel"},
                ],
            ),
            (
                "không xem mà cũng không tắt.",
                "still_life|A smartphone pouring endless mini-clips into an overflowing hopper on a table.",
                "không tắt",
                "overflowing hopper",
                "cause_effect",
            ),
            (
                "Vừa làm bài, vừa để giọng kể truyện rì rầm bên tai,",
                "full_scene|The young person tries to write at a desk while an audio speaker blasts dialogue into their ear.",
                "rì rầm",
                "audio speaker blasts",
                "cause_effect",
            ),
            (
                "thật ra mình đâu có nghe.",
                "variation|The young person stares blankly at a half-written sentence with a confused frown.",
                "đâu có nghe",
                "half-written sentence",
                "context",
            ),
            (
                "Mình chỉ cần nó lấp khoảng trống,",
                "white_card|A smartphone disguised as the experiment shock box emitting soft musical notes on pure white.",
                "khoảng trống",
                "experiment shock box",
                "comparison",
            ),
            (
                "để khỏi phải thấy chán.",
                "still_life|A quiet empty chair beside a turned-off speaker in soft light.",
                "thấy chán",
                "turned-off speaker",
                "context",
            ),
        ],
    },
    {
        "scene_id": "SC10",
        "title": "Ăn thì ăn thôi",
        "purpose": "Đúc kết nguyên tắc không ghép kèm màn hình vào các hoạt động sinh hoạt cơ bản",
        "setting": "Flat mint-cream 2D kitchen table background.",
        "narrative_phase": "takeaway",
        "tone": "analytical_crisp",
        "requirements": ["R10"],
        "source_ids": ["SRC01"],
        "claim_facts": [],
        "rows": [
            (
                "Muốn đầu óc nhẹ lại,",
                "white_card|A clear brain icon emerging from a parted gray fog cloud on pure white.",
                "nhẹ lại",
                "gray fog cloud",
                "cause_effect",
            ),
            (
                "đâu cần vứt điện thoại.",
                "still_life|A smartphone placed neatly inside a dedicated charging tray on a flat counter.",
                "điện thoại",
                "dedicated charging tray",
                "context",
            ),
            (
                "Cách đầu tiên dễ ợt.",
                "visual_diagram|Simple 2D diagram separating a meal bowl icon and a phone icon into two distinct boxes on pure white.",
                "dễ ợt",
                "two distinct boxes",
                "grouping",
                [
                    {"text": "ĂN RA ĂN", "placement": "below meal bowl", "object": "meal bowl"},
                    {"text": "XEM RA XEM", "placement": "below phone icon", "object": "phone icon"},
                ],
            ),
            (
                "Ăn thì ăn thôi.",
                "full_scene|The young person sits at a flat mint-cream kitchen table enjoying a warm meal without a phone.",
                "ăn thôi",
                "enjoying a warm meal",
                "context",
            ),
            (
                "Vào nhà vệ sinh thì để điện thoại ở ngoài.",
                "variation|The young person leaves the smartphone on the table before walking toward the doorway.",
                "ở ngoài",
                "leaves the smartphone on the table",
                "context",
            ),
            (
                "Đi ngủ thì để máy xa giường một chút.",
                "still_life|A smartphone resting on a distant desk across from a clean pillow.",
                "xa giường",
                "distant desk",
                "structure",
            ),
            (
                "Đừng bắt não vừa nhai cơm,",
                "white_card|A brain icon juggling a rice bowl and a movie reel simultaneously with red strain lines on pure white.",
                "nhai cơm",
                "rice bowl",
                "cause_effect",
            ),
            (
                "vừa nuốt thêm một tập phim tóm tắt.",
                "still_life|A closed tablet cover resting peacefully beside a teacup on the kitchen table.",
                "nuốt thêm",
                "closed tablet cover",
                "context",
            ),
        ],
    },
    {
        "scene_id": "SC11",
        "title": "Mười phút ngó trời ngó mây",
        "purpose": "Hướng dẫn thực hành khoảng nghỉ trắng không âm thanh để kích hoạt mạng lưới tự phục hồi",
        "setting": "Flat pale-amber 2D window balcony background.",
        "narrative_phase": "takeaway",
        "tone": "narrative_warm",
        "requirements": ["R11"],
        "source_ids": ["SRC01"],
        "claim_facts": [],
        "rows": [
            (
                "Cách thứ hai là chừa ra một khoảng nghỉ trống.",
                "white_card|A clean white rectangular frame labeled as a blank rest block between two work blocks on pure white.",
                "nghỉ trống",
                "blank rest block",
                "structure",
                [
                    {"text": "LÀM VIỆC SÂU", "placement": "left block", "object": "left block"},
                    {"text": "NGHỈ TRẮNG", "placement": "center block", "object": "center block"},
                ],
            ),
            (
                "Học hay làm xong một tiếng,",
                "still_life|A closed notebook and resting pen beside a warm cup of water on a balcony ledge.",
                "một tiếng",
                "closed notebook",
                "context",
            ),
            (
                "tháo tai nghe ra mười phút.",
                "full_scene|The young person stands by a flat pale-amber balcony window removing both wireless earbuds.",
                "tháo tai nghe",
                "removing both wireless earbuds",
                "context",
            ),
            (
                "Đừng mở mạng xã hội.",
                "variation|The young person places the earbuds into their case and looks out at the open sky.",
                "mạng xã hội",
                "places the earbuds into their case",
                "context",
            ),
            (
                "Ngồi ngó trời ngó mây.",
                "environment|A calm 2D view of open sky and distant rooftops from the balcony on a flat pale-amber background.",
                "ngó mây",
                "open sky",
                "context",
            ),
            (
                "Lúc đầu hơi khó chịu, kệ nó.",
                "still_life|A small sand hourglass with the top grains beginning to fall smoothly on the balcony rail.",
                "khó chịu",
                "sand hourglass",
                "progression",
            ),
            (
                "Một lát sau, cô thủ thư sẽ bắt tay vào dọn.",
                "full_scene|The 2D librarian calmly sweeps away paper scraps and aligns memory books on a clean shelf.",
                "thủ thư",
                "librarian calmly sweeps",
                "cause_effect",
            ),
            (
                "Mấy ý rời rạc tự nhiên khớp lại với nhau.",
                "visual_diagram|Three scattered modular idea tiles clicking together into a single clear radiant beacon icon on pure white.",
                "khớp lại",
                "idea tiles clicking together",
                "structure",
            ),
        ],
    },
    {
        "scene_id": "SC12",
        "title": "Sáng mai, nằm yên một phút",
        "purpose": "Khép vòng lặp với cảnh thức dậy buổi sáng và thông điệp bảo vệ khoảng lặng cho tâm trí",
        "setting": "Flat warm-cream 2D bedroom background.",
        "narrative_phase": "closing",
        "tone": "reflective_slow",
        "requirements": ["R12"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Sáng mai mở mắt,",
                "environment|A tidy 2D bedroom in gentle morning light with the phone resting far on a desk.",
                "sáng mai",
                "gentle morning light",
                "context",
            ),
            (
                "thử nằm yên một phút rồi hẵng cầm điện thoại.",
                "still_life|A quiet smartphone lying untouched on a wooden desk beside a glass of water.",
                "nằm yên",
                "quiet smartphone",
                "context",
            ),
            (
                "Bạn mệt không phải vì làm quá nhiều.",
                "white_card|Two simple gauges showing moderate work load versus overflowing background noise on pure white.",
                "quá nhiều",
                "overflowing background noise",
                "comparison",
                [
                    {"text": "VIỆC LÀM VỪA ĐỦ", "placement": "below left gauge", "object": "left gauge"},
                    {"text": "QUÁ TẢI TẠP ÂM", "placement": "below right gauge", "object": "right gauge"},
                ],
            ),
            (
                "Mà vì đầu chưa bao giờ được yên,",
                "full_scene|The young person sits up in bed stretching calmly with a clear, rested expression.",
                "được yên",
                "stretching calmly",
                "context",
            ),
            (
                "để tự dọn dẹp sau một ngày dài.",
                "still_life|A neatly ordered bookshelf icon beside a calm morning teacup on the bedside table.",
                "dọn dẹp",
                "ordered bookshelf icon",
                "structure",
            ),
            (
                "Tối nay, thử tắt cái video chạy nền bên gối.",
                "variation|The young person reaches over and switches off a small bedside speaker with a gentle smile; expression shift.",
                "bên gối",
                "switches off a small bedside speaker",
                "context",
            ),
            (
                "Coi như cho cô thủ thư trong đầu bạn được làm việc.",
                "still_life|An open bedroom window letting in a clean breeze beside a silent resting cup.",
                "cô thủ thư",
                "open bedroom window",
                "context",
            ),
        ],
    },
]


def build_human_editorial() -> Dict[str, Any]:
    return {
        "topic_dilemmas": [
            "Con người tìm đến video ngắn, tóm tắt phim và truyện lồng tiếng để xả hơi sau giờ làm, nhưng chính dòng kích thích liên tục này lại khóa chặt cơ chế tự dọn rác của não bộ.",
            "Thói quen bật âm thanh và màn hình phủ kín từ lúc mở mắt, lúc ăn, lúc đi vệ sinh tới lúc ngủ biến việc giải trí thành phản xạ trốn chạy khoảng lặng.",
            "Ranh giới mong manh giữa việc thưởng thức một nội dung giải trí có điểm dừng và việc dùng tạp âm số liên tục để gây tê cảm giác trống rỗng.",
        ],
        "dynamic_questions": [
            "Theo quan sát thực tế của bạn, chuỗi thói quen mở màn hình và âm thanh liên tục trong ngày đang diễn ra cụ thể như thế nào từ sáng tới đêm?",
            "Nếu có người cho rằng vừa ăn hay vừa làm việc vừa nghe tóm tắt phim giúp tận dụng thời gian và đỡ chán, bạn sẽ phản biện ra sao về cái giá phải trả của sự chú ý?",
            "Đâu là những ranh giới thực hành đơn giản nhất để cắt đứt phản xạ mở điện thoại vô thức mà không cần cực đoan từ bỏ hoàn toàn công nghệ?",
        ],
        "author_raw_input": (
            "Sáng dậy mở mắt ra đã mở video ngắn, lướt tiktok, lướt facebook, youtube, xem review phim, "
            "xem các audio lồng tiếng trung quốc, lúc ăn cũng mở, lúc ngủ cũng mở, lúc làm việc cũng mở, "
            "đi vào nhà vệ sinh vẫn mở, đến nỗi đi học đi làm cũng mở lên."
        ),
        "editorial_stance": (
            "Cảm giác kiệt sức thời hiện đại không chỉ đến từ áp lực công việc mà đến từ việc ta lấp kín mọi khoảng trống "
            "sinh hoạt từ lúc mở mắt, ăn uống, vệ sinh đến lúc ngủ bằng video ngắn, review phim và audio lồng tiếng; "
            "chính việc tước đoạt hoàn toàn sự tĩnh lặng đã khóa chặt mạng lưới chế độ mặc định của não và biến giải trí thành ca làm việc phụ nặng nề."
        ),
        "expanded_content_ideas": [
            {
                "idea_id": "IDEA_01",
                "angle_type": "analysis",
                "idea_summary": (
                    "Phân tích vòng lặp lấp đầy cảm giác từ sáng tới đêm: khi mắt và tai bị chiếm dụng liên tục trong lúc ăn, "
                    "đi vệ sinh, đi học và đi ngủ, mạng lưới chế độ mặc định không có nổi vài phút ngừng kích thích để dọn rác thông tin."
                ),
                "narrative_integration": (
                    "Đặt ngay ở cảnh mở đầu và phần dẫn để người xem thấy chính thói quen sáng mở mắt lướt video, trưa ăn cơm xem review phim, "
                    "tối bật audio lồng tiếng đi ngủ của mình, sau đó nối thẳng vào ẩn dụ người thủ thư bị kẹt giữa cơn lũ dữ liệu."
                ),
                "target_narrative_phase": "causal_mechanism",
            },
            {
                "idea_id": "IDEA_02",
                "angle_type": "commentary",
                "idea_summary": (
                    "Bình luận phản biện về sự khác biệt giữa giải trí chủ động có điểm dừng và việc bật truyện lồng tiếng hay video chạy nền "
                    "như một liều thuốc gây tê để trốn tránh ba mươi giây tĩnh lặng."
                ),
                "narrative_integration": (
                    "Kết nối thí nghiệm căn phòng trống của Đại học Virginia với chặng phản biện để giải thích vì sao ta thà chịu quá tải "
                    "tạp âm còn hơn ngồi yên với suy nghĩ của chính mình."
                ),
                "target_narrative_phase": "counter_argument",
            },
            {
                "idea_id": "IDEA_03",
                "angle_type": "evaluation",
                "idea_summary": (
                    "Đánh giá giải pháp thực tế qua quy tắc tách rời đơn nhiệm (ăn ra ăn, ngủ ra ngủ, đi vệ sinh để máy bên ngoài) "
                    "và mười phút nghỉ trắng tháo tai nghe để trả lại quyền dọn dẹp cho não bộ."
                ),
                "narrative_integration": (
                    "Triển khai cụ thể ở hai cảnh nội dung rút ra và khép lại vòng lặp bằng khoảnh khắc thức dậy buổi sáng không chạm tay ngay vào màn hình."
                ),
                "target_narrative_phase": "takeaway",
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
        base_id = None
        variation_streak = 0

        for beat_idx, row in enumerate(rows, 1):
            quote, spec, src_term, vis_term, relation = row[:5]
            visible_text = list(row[5]) if len(row) > 5 else []
            shot_type, raw_desc = spec.split("|", 1)
            shot_type = shot_type.strip()
            raw_desc = raw_desc.strip()

            if shot_type == "full_scene":
                base_id = f"{scene_id}_I{beat_idx}"
                variation_streak = 0
                based_on = None
                preserve = ""
                change = raw_desc
            elif shot_type == "variation":
                variation_streak += 1
                based_on = base_id
                preserve = (
                    f"Keep the exact 2D composition, camera angle, flat background and character design in {setting} "
                    "Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift."
                )
                change = raw_desc
            else:
                variation_streak = 0
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
            allow_shift = True if ("expression shift" in raw_desc.lower() and shot_type == "variation") else None

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
                    allow_expression_shift=allow_shift,
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
            "title": "A Default Mode of Brain Function",
            "reference": "Marcus E. Raichle et al. (2001). Proceedings of the National Academy of Sciences (PNAS), 98(2), 676–682.",
            "facts": [
                "Người nằm yên, nhưng não vẫn đốt năng lượng gần như lúc làm việc.",
                "Nó chỉ chạy khi bạn không xem gì, không nghe gì.",
                "Lúc yên tĩnh, não sắp xếp lại ký ức và dọn bớt rác trong ngày.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Attention Span: A Groundbreaking Way to Restore Balance, Happiness and Productivity",
            "reference": "Gloria Mark (2023) & Sophie Leroy (2009), Organization Science / University of California, Irvine.",
            "facts": [
                "Lướt liên tục lúc rảnh làm não không có lúc nào tự hồi phục.",
                "Mỗi lần nhảy cảnh, não phải bẻ lái và tốn thêm sức.",
                "Phần chú ý cũ còn vương lại, làm đầu mình lùng bùng.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Just Think: The Challenges of the Disengaged Mind",
            "reference": "Timothy D. Wilson et al. (2014). Science, 345(6192), 75–77. University of Virginia.",
            "facts": [
                "Cứ ba người đàn ông thì hai người tự bấm, chỉ để khỏi ngồi yên mười lăm phút.",
            ],
        },
    ]

    required_points = [
        {"id": sc["requirements"][0], "text": sc["purpose"]}
        for sc in STORY_SCENES
    ]

    visual_hook = (
        "A 2D cartoon person lying motionless under a blanket with a smartphone, "
        "while above their head an exhausted cartoon brain sprints full speed on a spinning track "
        "buried under floating video and audio icons"
    )
    text_overlay = "NGHỈ MÀ MỆT HƠN"
    contrast_pair = "Cơ thể nằm nghỉ vs. Bộ não tăng ca"
    thumbnail_prompt = build_thumbnail_poster_prompt(
        visual_hook=visual_hook,
        text_overlay=text_overlay,
        contrast_pair=contrast_pair,
    )

    packaging = PackagingSpec(
        youtube_title="Vì Sao Nằm Lướt Điện Thoại Nghỉ Ngơi Lại Mệt Hơn?",
        visual_hook=visual_hook,
        text_overlay=text_overlay,
        contrast_pair=contrast_pair,
        channel_pillar=DEFAULT_CHANNEL_PILLAR,
        funnel_tier="tier_1_broad",
        seo_keywords=[
            "nghịch lý nghỉ ngơi",
            "vì sao lướt điện thoại lại mệt",
            "mạng lưới chế độ mặc định",
            "quá tải thông tin video ngắn",
            "tư duy nhận thức và sự chú ý",
        ],
        thumbnail_prompt=thumbnail_prompt,
        layout_mode="integrated_poster",
        typography_style="Bold hand-crafted golden-yellow (#FACC15) uppercase poster lettering with heavy charcoal outline",
    )

    total_est = sum(s.duration for s in scenes)
    min_dur = round(max(150.0, total_est * 0.80), 1)
    max_dur = round(total_est * 1.25, 1)

    return ResearchedTopic(
        topic="Nghịch Lý Nghỉ Ngơi: Vì Sao Mở Điện Thoại Lấp Đầy Mọi Khoảng Trống Lại Làm Não Kiệt Sức?",
        audience="Người trẻ đi học, đi làm và người lao động trí óc tại Việt Nam",
        goal="Giải mã cơ chế mạng lưới chế độ mặc định và chi phí chuyển đổi ngữ cảnh khiến việc bật video ngắn hay truyện lồng tiếng liên tục lúc rảnh làm não kiệt quệ, đồng thời áp dụng quy tắc tách rời đơn nhiệm và mười phút nghỉ trắng.",
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

    outline_data = {"outline": content_data["outline"]}
    script_data = generate_script_json(topic)

    checker = ScriptCadenceChecker(
        nominal_rate=NOMINAL_SPEECH_RATE,
        max_sentence_syllables=25,
        max_clause_syllables=18,
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
    parser = argparse.ArgumentParser(description="Build rest-paradox-16x9 Schema 3.0 blueprint.")
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
        Path("/tmp/rest-paradox-16x9-blueprint"),
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
            "rhythm_metrics": res["diversity_report"]["rhythm_metrics"],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        if (
            not res["valid_contracts"]
            or res["packaging_warnings"]
            or res["spoken_fact_warnings"]
            or res["editorial_errors"]
            or res["short_errors"]
            or res["explanation_errors"]
            or res["clearance_errors"]
            or res["estimate_warnings"]
            or res["phonetic_issues"]
            or res["cadence_report"]["status"] != "PASS"
            or res["cadence_report"]["warnings_count"] != 0
            or res["diversity_report"]["status"] != "PASS"
        ):
            all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
