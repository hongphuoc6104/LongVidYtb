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
        "title": "Nghịch lý nằm xả hơi sau giờ làm",
        "purpose": "Mở bài bằng tình huống đi làm về nằm lướt điện thoại xả hơi nhưng lúc bỏ máy xuống đầu óc lại nặng trịch hơn",
        "setting": "Flat warm paper-cream (#F8F0DC) 2D orthographic bedroom stage.",
        "narrative_phase": "hook",
        "tone": "narrative_warm",
        "requirements": ["R01"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Đi làm về mệt rã rời, bạn",
                "full_scene|Flat 2D side-on orthographic bedroom doorway on a warm paper-cream (#F8F0DC) stage: the white-head doodle stickman trudges in carrying a crooked black shoulder bag with droopy hunched posture, sweat drops, and a red empty-battery gauge above the round white head.",
                "mệt rã rời",
                "droopy hunched posture",
                "context",
            ),
            (
                "nằm vật ra giường để xả",
                "variation|The white-head doodle stickman drops the shoulder bag onto the floor and flops face-down across a flat rectangular bed mattress; expression shift.",
                "nằm vật",
                "flops face-down across a flat rectangular bed",
                "context",
            ),
            (
                "hơi một chút. Tay cầm điện",
                "macro_prop|Flat 2D close-up on an apricot-peach (#F2B88B) field: the white-head doodle stickman's thin black wire arm and round white circle hand hold up a bright smartphone screen right above the flat pillow.",
                "cầm điện",
                "bright smartphone screen",
                "context",
            ),
            (
                "thoại định lướt mười lăm",
                "concept_metaphor|Raw freehand 2D doodle on a warm paper-cream (#F8F0DC) field: the white-head doodle stickman lies smiling calmly with a speech cloud above the round white head showing a tiny clock face marked with a small fifteen-minute slice.",
                "mười lăm",
                "fifteen-minute slice",
                "quantity",
                [
                    {"text": "MƯỜI LĂM PHÚT", "placement": "above tiny clock face", "object": "tiny clock face"},
                ],
            ),
            (
                "phút, mà ngoảnh đi ngoảnh",
                "full_scene|Flat 2D side-on orthographic bedroom on a pale ice-blue (#CBE0E0) wall: the white-head doodle stickman lies on the bed staring wide-eyed at the phone while the white circle thumb flicks upward with stacked black speed arcs.",
                "ngoảnh đi",
                "stacked black speed arcs",
                "progression",
            ),
            (
                "lại đã trôi vèo hai tiếng.",
                "white_card|Raw freehand 2D doodle on a solid slate-navy (#2E4361) night canvas: the white-head doodle stickman lies in the exact same spot under a giant lopsided wall clock spinning rapidly with curved black motion lines into late night.",
                "hai tiếng",
                "lopsided wall clock",
                "quantity",
                [
                    {"text": "HAI TIẾNG TRÔI QUA", "placement": "above lopsided wall clock", "object": "lopsided wall clock"},
                ],
            ),
            (
                "Kỳ lạ ở chỗ, cả buổi tối",
                "concept_metaphor|Flat 2D doodle on a soft sage-green (#93A88C) field: the white-head doodle stickman scratches the round white head with a big black question mark (?) beside a crescent moon and stars.",
                "buổi tối",
                "crescent moon",
                "context",
            ),
            (
                "cơ thể nằm bất động, chẳng",
                "full_scene|Flat 2D top-down orthographic view on a warm paper-cream (#F8F0DC) stage: the white-head doodle stickman lies completely stiff and motionless like a flat plank on the rectangular mattress.",
                "nằm bất động",
                "lies completely stiff and motionless",
                "comparison",
            ),
            (
                "tốn một giọt mồ hôi. Vậy mà",
                "macro_prop|Flat 2D doodle close-up on a pale ice-blue (#CBE0E0) field: the stickman's two thin black stick legs rest under a neat flat blanket beside untouched indoor slippers and a dry towel with a green check mark.",
                "mồ hôi",
                "dry towel",
                "comparison",
            ),
            (
                "lúc bỏ máy xuống, hai mắt bỗng cay xè,",
                "cutaway_detail|Flat 2D front close-up on a warm paper-cream (#F8F0DC) stage: the white-head doodle stickman stares up from the pillow with wide bloodshot tired eyes, dark under-eye bags, and jagged red dry-eye zigzags.",
                "cay xè",
                "jagged red dry-eye zigzags",
                "cause_effect",
            ),
            (
                "đầu óc lại nặng trịch hơn cả lúc chưa nằm.",
                "concept_metaphor|Raw freehand 2D doodle on a solid apricot-peach (#F2B88B) field: a giant flat black iron weight presses straight down onto the round white head of the doodle stickman on the pillow.",
                "nặng trịch",
                "giant flat black iron weight",
                "cause_effect",
                [
                    {"text": "ĐẦU NẶNG TRỊCH", "placement": "on giant flat black iron weight", "object": "giant flat black iron weight"},
                ],
            ),
        ],
    },
    {
        "scene_id": "SC02",
        "title": "Cái lưng được nghỉ nhưng bộ não chạy nước rút",
        "purpose": "Giải thích trực diện nghịch lý nghỉ ngơi khi cơ thể nằm êm nhưng bộ não bị ép nhảy qua hàng chục cảm xúc trái ngược và sợ sự im lặng",
        "setting": "Flat apricot-peach (#F2B88B) 2D orthographic indoor stage.",
        "narrative_phase": "lead_in",
        "tone": "narrative_warm",
        "requirements": ["R02"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Thật ra thứ được nghỉ lúc đó chỉ là cái lưng của bạn,",
                "full_scene|Flat 2D side-on orthographic view on a warm paper-cream (#F8F0DC) stage: the white-head doodle stickman reclines flat on a soft mattress with a bold green check mark pointing at the relaxed flat back.",
                "cái lưng",
                "relaxed flat back",
                "comparison",
                [
                    {"text": "LƯNG ĐƯỢC NGHỈ", "placement": "below relaxed flat back", "object": "relaxed flat back"},
                ],
            ),
            (
                "chứ không phải bộ não.",
                "cutaway_detail|Flat 2D front close-up on an apricot-peach (#F2B88B) field: an open window inside the upper pure-white (#FFFFFF) round head of the doodle stickman reveals a miniature stickman sprinting frantically inside a spinning wheel with sweat drops.",
                "bộ não",
                "miniature stickman sprinting frantically",
                "comparison",
                [
                    {"text": "NÃO CHẠY NƯỚC RÚT", "placement": "above open window", "object": "miniature stickman sprinting frantically"},
                ],
            ),
            (
                "Chỉ trong vài phút, đầu bạn bị ép nhảy qua",
                "concept_metaphor|Flat 2D side view on a warm paper-cream (#F8F0DC) field: a smartphone in the white-head doodle stickman's hand fires a chaotic volley of crooked multicolor lightning arrows straight into the stickman's wide dot eyes.",
                "nhảy qua",
                "chaotic volley of crooked multicolor lightning arrows",
                "cause_effect",
            ),
            (
                "hàng chục câu chuyện trái ngược nhau.",
                "visual_diagram|Raw freehand 2D doodle on a soft sage-green (#93A88C) canvas: the white-head doodle stickman with dizzy spiral eyes stands surrounded by a spinning ring of mismatched square cards showing a laughing cat, a house fire, a teardrop, and a boiling pot.",
                "câu chuyện",
                "spinning ring of mismatched square cards",
                "grouping",
            ),
            (
                "Giây trước vừa bật cười vì một đoạn hài ngắn,",
                "full_scene|Flat 2D front close-up on a warm paper-cream (#F8F0DC) stage: the white-head doodle stickman holds up the phone laughing with a big open D-shaped mouth and cheerful yellow stars around the head.",
                "bật cười",
                "laughing with a big open D-shaped mouth",
                "context",
            ),
            (
                "giây sau đã căng thẳng xem người lạ cãi vã.",
                "variation|The white-head doodle stickman suddenly tenses up with furrowed angry-worried eyebrows, sweat drops, and a clenched zigzag mouth as two red megaphones clash above the phone screen; expression shift.",
                "cãi vã",
                "two red megaphones clash",
                "cause_effect",
            ),
            (
                "Thậm chí lúc bưng bát cơm",
                "full_scene|Flat 2D front-on orthographic dining view on an apricot-peach (#F2B88B) stage: the white-head doodle stickman sits behind a flat brown table line holding chopsticks and a rice bowl while staring glued to a smartphone propped against a cup.",
                "bát cơm",
                "rice bowl",
                "context",
            ),
            (
                "hay nhắm mắt đi ngủ, máy vẫn chạy.",
                "full_scene|Flat 2D night bedroom stage with a solid slate-navy (#2E4361) wall and a small crescent-moon window: the white-head doodle stickman lies under a flat blue blanket (#4B6584) with both eyes shut.",
                "đi ngủ",
                "lies under a flat blue blanket",
                "context",
            ),
            (
                "Ta bật tiếng rì rầm bên gối chỉ vì sợ sự im lặng.",
                "cutaway_detail|Flat 2D night bedroom (#2E4361) close-up: the white-head doodle stickman lies with eyes shut on the pillow while a bright smartphone right beside the ear emits jagged black sound-wave squiggles pushing back an empty dark silence cloud.",
                "rì rầm",
                "jagged black sound-wave squiggles",
                "cause_effect",
            ),
        ],
    },
    {
        "scene_id": "SC03",
        "title": "Nỗi sợ ba mươi giây tĩnh lặng",
        "purpose": "Chỉ ra cảm giác bồn chồn khi thiếu kích thích âm thanh và hình ảnh dù chỉ vài chục giây",
        "setting": "Flat pale ice-blue (#CBE0E0) 2D desk stage.",
        "narrative_phase": "lived_friction",
        "tone": "reflective_slow",
        "requirements": ["R03"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Bạn thử tắt sạch âm thanh trong ba mươi giây xem sao.",
                "still_life|Raw freehand 2D marker illustration on a pale ice-blue (#CBE0E0) field: a flat round mechanical stopwatch with a bold thirty-second dial slice sits beside a face-down black smartphone on a flat brown desk line.",
                "ba mươi giây",
                "thirty-second dial",
                "quantity",
                [{"text": "BA MƯƠI GIÂY", "placement": "above flat round mechanical stopwatch", "object": "flat round mechanical stopwatch"}],
            ),
            (
                "Không gian bỗng trống trải lạ thường.",
                "environment|Raw freehand 2D marker illustration on a pale ice-blue (#CBE0E0) field: a wide flat 2D desk stage with a muted speaker badge crossed out in red above a quiet bare wall boundary.",
                "trống trải",
                "quiet bare wall",
                "context",
            ),
            (
                "Bàn tay lập tức ngứa ngáy,",
                "full_scene|Flat 2D front-on orthographic view on a pale ice-blue (#CBE0E0) stage: the white-head doodle stickman sits behind a flat wooden desk line looking sideways with wide uneasy dot eyes while jittery black vibration lines shake around both round white circle hands.",
                "ngứa ngáy",
                "jittery black vibration lines",
                "cause_effect",
            ),
            (
                "tự động mò tìm chiếc điện thoại trên mặt bàn.",
                "variation|The white-head doodle stickman reaches one thin black wire arm across the desk line to grab the face-down black smartphone with a tense wavy mouth; expression shift.",
                "điện thoại",
                "face-down black smartphone",
                "progression",
            ),
            (
                "Ta quen gọi thói quen đó là giải trí cuối ngày.",
                "white_card|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: a flat paper tag decorated with cheerful party confetti partially peels back to reveal jagged black noise scribbles underneath.",
                "giải trí",
                "cheerful party confetti",
                "comparison",
                [{"text": "VỎ BỌC GIẢI TRÍ", "placement": "above flat paper tag", "object": "flat paper tag"}],
            ),
            (
                "Thực chất ta đang trốn chạy khoảng lặng.",
                "still_life|Raw freehand 2D marker illustration on a warm paper-cream (#F8F0DC) field: a giant pair of heavy black over-ear headphones slams down onto a calm white speech cloud on a flat tabletop.",
                "khoảng lặng",
                "calm white speech cloud",
                "cause_effect",
                [{"text": "TRỐN KHOẢNG LẶNG", "placement": "above heavy black over-ear headphones", "object": "heavy black over-ear headphones"}],
            ),
            (
                "Nhưng càng nhồi thêm tiếng nói và hình ảnh vào đầu,",
                "full_scene|Flat 2D side-on orthographic desk view on a pale ice-blue (#CBE0E0) stage: the white-head doodle stickman hunches close to a bright upright phone screen as a dense barrage of tiny play triangles and musical notes shoots at the round white head.",
                "nhồi thêm",
                "dense barrage of tiny play triangles",
                "quantity",
            ),
            (
                "tâm trí bạn lại càng đờ đẫn.",
                "variation|The white-head doodle stickman slumps forward propping the round white head on one white circle hand with droopy half-shut eyelids and spiral daze lines above; expression shift.",
                "đờ đẫn",
                "droopy half-shut eyelids",
                "cause_effect",
            ),
            (
                "Vậy sao nằm êm trên nệm lại mệt hơn cả ca làm?",
                "visual_diagram|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: two flat horizontal comparison bars where a desk briefcase icon shows half green charge while a flat mattress with a lit phone screen shows a draining red battery bar.",
                "mệt hơn",
                "draining red battery bar",
                "comparison",
                [{"text": "ĐI LÀM CÒN PIN", "placement": "above desk briefcase icon", "object": "desk briefcase icon"}, {"text": "NẰM XEM CẠN SẠCH", "placement": "below draining red battery bar", "object": "draining red battery bar"}],
            ),
        ],
    },
    {
        "scene_id": "SC04",
        "title": "Ngộ nhận về bộ não đứng yên",
        "purpose": "Lật tẩy hiểu lầm rằng ngừng làm việc tay chân là não tự động được nghỉ ngơi",
        "setting": "Flat sage-green (#93A88C) 2D lounge chair stage.",
        "narrative_phase": "problem",
        "tone": "analytical_crisp",
        "requirements": ["R04"],
        "source_ids": ["SRC01"],
        "claim_facts": [["Người nằm yên, nhưng não vẫn đốt năng lượng gần như lúc làm việc.", "SRC01", "Người nằm yên, nhưng não vẫn đốt năng lượng gần như lúc làm việc."]],
        "rows": [
            (
                "Câu trả lời nằm ở một ngộ nhận rất quen thuộc.",
                "white_card|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: a flat sleeping pillow icon and a powered-off brain icon linked by an equals sign struck through with a bold red cross.",
                "ngộ nhận",
                "bold red cross",
                "comparison",
                [{"text": "NẰM NGHỈ", "placement": "below flat sleeping pillow icon", "object": "flat sleeping pillow icon"}, {"text": "NÃO TỰ TẮT?", "placement": "below powered-off brain icon", "object": "powered-off brain icon"}],
            ),
            (
                "Ta cứ tưởng hễ tay chân ngừng làm,",
                "still_life|Raw freehand 2D marker illustration on a sage-green (#93A88C) field: a pair of neatly parked indoor slippers rests beside a flat cushioned lounge chair on a black floor line.",
                "tay chân",
                "parked indoor slippers",
                "comparison",
            ),
            (
                "đặt lưng xuống ghế êm là đầu óc tự tắt nguồn.",
                "full_scene|Flat 2D side-on orthographic view on a sage-green (#93A88C) stage: the white-head doodle stickman reclines comfortably on a flat padded lounge chair with eyes closed and a tiny dashed off-button bubble floating above the head.",
                "ghế êm",
                "padded lounge chair",
                "context",
            ),
            (
                "Sự thật hoàn toàn ngược lại. Người nằm yên,",
                "variation|The white-head doodle stickman opens both tiny dot eyes wide as the dashed bubble pops and a bright red exclamation triangle appears above the round white head; expression shift.",
                "ngược lại",
                "red exclamation triangle",
                "comparison",
            ),
            (
                "nhưng não vẫn đốt năng lượng gần như lúc làm việc.",
                "visual_diagram|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: a flat side-by-side meter board where a resting chair gauge sits at one low bar while a brain outline burns five blazing orange fuel bars.",
                "đốt năng lượng",
                "blazing orange fuel bars",
                "quantity",
                [{"text": "THÂN XÁC NGHỈ", "placement": "below resting chair gauge", "object": "resting chair gauge"}, {"text": "NÃO ĐỐT NĂNG LƯỢNG", "placement": "below blazing orange fuel bars", "object": "blazing orange fuel bars"}],
            ),
            (
                "Bộ não không có công tắc tắt phụp như chiếc đèn trần.",
                "still_life|Raw freehand 2D marker illustration on a warm paper-cream (#F8F0DC) field: a plastic wall toggle switch marked with a red cross sits beside an always-on humming control box with steady green pulse lines.",
                "công tắc",
                "plastic wall toggle switch",
                "comparison",
            ),
            (
                "Nó chẳng bao giờ ngừng chạy.",
                "still_life|Raw freehand 2D marker illustration on a pale ice-blue (#CBE0E0) field: a flat square monitor frame displays a bright green continuous looping wave across the screen without any stop button.",
                "ngừng chạy",
                "continuous looping wave",
                "structure",
            ),
            (
                "Khi bạn buông việc bên ngoài, nó liền đổi sang ca trực khác.",
                "full_scene|Flat 2D front-on orthographic view on a sage-green (#93A88C) stage: the white-head doodle stickman sits in the lounge chair pushing aside a shut notebook computer on a small side table while looking upward.",
                "buông việc",
                "shut notebook computer",
                "progression",
            ),
            (
                "Đó là lúc não âm thầm tổng vệ sinh từ bên trong.",
                "variation|The white-head doodle stickman smiles calmly and points one round white circle hand at a neat thought cloud above the head containing a crossed broom and dustpan; expression shift.",
                "tổng vệ sinh",
                "crossed broom and dustpan",
                "structure",
            ),
        ],
    },
    {
        "scene_id": "SC05",
        "title": "Mạng lưới dọn rác âm thầm của não",
        "purpose": "Giải phẫu cơ chế mạng lưới chế độ mặc định giúp não tự dọn dẹp và sắp xếp ký ức khi thẩn thơ",
        "setting": "Flat warm paper-cream (#F8F0DC) 2D library stage.",
        "narrative_phase": "causal_mechanism",
        "tone": "analytical_crisp",
        "requirements": ["R05"],
        "source_ids": ["SRC01"],
        "claim_facts": [["Nó chỉ chạy khi bạn không xem gì, không nghe gì.", "SRC01", "Nó chỉ chạy khi bạn không xem gì, không nghe gì."], ["Lúc yên tĩnh, não sắp xếp lại ký ức và dọn bớt rác trong ngày.", "SRC01", "Lúc yên tĩnh, não sắp xếp lại ký ức và dọn bớt rác trong ngày."]],
        "rows": [
            (
                "Khoa học gọi ca trực này là mạng lưới chế độ mặc định.",
                "visual_diagram|Raw freehand 2D marker illustration on a warm paper-cream (#F8F0DC) field: a flat brain outline linking five bright yellow connected star nodes with bold black marker lines.",
                "mạng lưới",
                "connected star nodes",
                "structure",
                [{"text": "CHẾ ĐỘ MẶC ĐỊNH", "placement": "above flat brain outline", "object": "flat brain outline"}],
            ),
            (
                "Nó chỉ chạy khi bạn không xem gì, không nghe gì.",
                "still_life|Raw freehand 2D marker illustration on a pale ice-blue (#CBE0E0) field: a darkened smartphone lies screen-down beside unplugged black earphones on a clean flat wooden tabletop.",
                "không nghe gì",
                "unplugged black earphones",
                "cause_effect",
            ),
            (
                "Mọi cổng nhận tin phải khép lại.",
                "white_card|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: a lowered metal shutter closes over an external input slot while a green internal broom badge lights up beside it.",
                "khép lại",
                "lowered metal shutter",
                "cause_effect",
                [{"text": "ĐÓNG CỔNG NHẬN TIN", "placement": "above lowered metal shutter", "object": "lowered metal shutter"}, {"text": "BẬT DỌN DẸP", "placement": "below green internal broom badge", "object": "green internal broom badge"}],
            ),
            (
                "Cơ chế này giống hệt một thư viện sau giờ đóng cửa.",
                "environment|Raw freehand 2D marker illustration on a warm paper-cream (#F8F0DC) field: quiet flat 2D wooden library doors latched shut with a hanging sign beside tall orderly bookshelves on the library stage.",
                "thư viện",
                "wooden library doors",
                "comparison",
                [{"text": "ĐÃ ĐÓNG CỬA", "placement": "on hanging sign", "object": "hanging sign"}],
            ),
            (
                "Khách tra cứu ra về hết,",
                "full_scene|Flat 2D front-on orthographic view on a warm paper-cream (#F8F0DC) library stage: the white-head doodle stickman wearing crooked round glasses stands beside a vacant reading desk pushing a rolling book cart.",
                "ra về hết",
                "vacant reading desk",
                "context",
            ),
            (
                "người trực đêm mới đẩy xe đi gom từng chồng sách lẻ.",
                "variation|The white-head doodle stickman wearing crooked round glasses gathers stacks of loose paper folders from the desk onto the rolling book cart with a calm focused mouth; expression shift.",
                "chồng sách",
                "stacks of loose paper folders",
                "progression",
            ),
            (
                "Lúc yên tĩnh, não sắp xếp lại ký ức",
                "visual_diagram|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: neat blue labeled memory binders slide into indexed wooden shelf slots in clean alphabetical order.",
                "ký ức",
                "labeled memory binders",
                "grouping",
                [{"text": "HỒ SƠ KÝ ỨC", "placement": "above labeled memory binders", "object": "labeled memory binders"}],
            ),
            (
                "và dọn bớt rác trong ngày.",
                "still_life|Raw freehand 2D marker illustration on a sage-green (#93A88C) field: a small broom sweeps crumpled paper scraps and tangled tape snippets into a flat black wire wastebasket.",
                "dọn bớt rác",
                "wire wastebasket",
                "cause_effect",
                [{"text": "DỌN RÁC TRONG NGÀY", "placement": "above wire wastebasket", "object": "wire wastebasket"}],
            ),
            (
                "Nhờ vậy, tâm trí bạn mới lấy lại khoảng trống quang đãng.",
                "full_scene|Flat 2D wide orthographic view on a warm paper-cream (#F8F0DC) library stage: the white-head doodle stickman wearing crooked round glasses stands smiling beside spotless aligned bookshelves under three cheerful yellow stars.",
                "quang đãng",
                "spotless aligned bookshelves",
                "cause_effect",
            ),
        ],
    },
    {
        "scene_id": "SC06",
        "title": "Cơn lũ dữ liệu khóa chặt đội dọn rác",
        "purpose": "Giải thích vì sao việc mở màn hình và âm thanh liên tục ngăn cản não tự phục hồi",
        "setting": "Flat slate-navy (#2E4361) 2D archive hall stage.",
        "narrative_phase": "causal_mechanism",
        "tone": "analytical_crisp",
        "requirements": ["R06"],
        "source_ids": ["SRC02"],
        "claim_facts": [["Lướt liên tục lúc rảnh làm não không có lúc nào tự hồi phục.", "SRC02", "Lướt liên tục lúc rảnh làm não không có lúc nào tự hồi phục."]],
        "rows": [
            (
                "Nhưng nếu bữa trưa bạn vừa nhai vừa nhìn màn hình,",
                "still_life|Raw freehand 2D marker illustration on a slate-navy (#2E4361) field: a steaming soup bowl with a metal spoon sits right beside a propped-up bright smartphone playing fast moving shapes on a flat table.",
                "bữa trưa",
                "steaming soup bowl",
                "context",
            ),
            (
                "đi vệ sinh hai tai vẫn gắn tai nghe thì sao?",
                "still_life|Raw freehand 2D marker illustration on a pale ice-blue (#CBE0E0) field: a pair of white wireless earbuds pulsing with jagged black sound zigzags hangs on a bathroom door handle.",
                "tai nghe",
                "white wireless earbuds",
                "cause_effect",
            ),
            (
                "Lúc đó, bạn đang mở toang cổng thư viện suốt ngày đêm.",
                "environment|Raw freehand 2D marker illustration on a slate-navy (#2E4361) field: tall flat 2D archive double doors wedged wide open with heavy wooden blocks while crates of loose paper flyers spill across the floor stage.",
                "mở toang",
                "archive double doors wedged wide open",
                "cause_effect",
            ),
            (
                "Luồng tin mới cứ thế ùa vào dồn dập.",
                "still_life|Raw freehand 2D marker illustration on a warm apricot-peach (#F2B88B) field: a wide black tilted chute dumping heaps of loud megaphone cards and bright picture slips onto an overflowing desk.",
                "ùa vào",
                "tilted chute dumping",
                "quantity",
            ),
            (
                "Đội dọn dẹp bị khóa chặt tay.",
                "full_scene|Flat 2D front-on orthographic view on a slate-navy (#2E4361) archive hall stage: the white-head doodle stickman wearing crooked round glasses stands buried waist-deep in unsorted paper slips with a broom pinned down.",
                "khóa chặt",
                "buried waist-deep",
                "cause_effect",
            ),
            (
                "Họ chỉ kịp đứng đỡ từng đợt tờ rơi ném tới tấp.",
                "variation|The white-head doodle stickman wearing crooked round glasses scrambles with dizzy spiral eyes and sweat drops to catch incoming paper flyers with both round white circle hands; expression shift.",
                "tờ rơi",
                "incoming paper flyers",
                "cause_effect",
            ),
            (
                "Lướt liên tục lúc rảnh",
                "visual_diagram|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: a bold red feed arrow pushes inward against a heavy iron padlock clamped shut over a green broom cleanup badge.",
                "lúc rảnh",
                "heavy iron padlock",
                "cause_effect",
                [{"text": "NẠP TIN LIÊN TỤC", "placement": "above bold red feed arrow", "object": "bold red feed arrow"}, {"text": "KHÓA TỰ PHỤC HỒI", "placement": "below heavy iron padlock", "object": "heavy iron padlock"}],
            ),
            (
                "làm não không có lúc nào tự hồi phục.",
                "full_scene|Flat 2D side-on orthographic archive hall view on a slate-navy (#2E4361) stage: the white-head doodle stickman wearing crooked round glasses slumps exhausted on the floor beside a toppled book cart under an empty red battery icon.",
                "hồi phục",
                "empty red battery icon",
                "cause_effect",
            ),
            (
                "Rác thông tin cứ thế chất chồng qua từng đêm.",
                "white_card|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: a towering mountain of crumpled paper scraps and noisy speaker badges presses down on a small flat brain outline.",
                "chất chồng",
                "towering mountain of crumpled paper",
                "quantity",
                [{"text": "RÁC CHẤT ĐỐNG", "placement": "above towering mountain of crumpled paper", "object": "towering mountain of crumpled paper"}],
            ),
        ],
    },
    {
        "scene_id": "SC07",
        "title": "Chi phí chuyển đổi ngữ cảnh mỗi ba mươi giây",
        "purpose": "Mô hình hóa chi phí năng lượng khi não phải nhảy qua hàng chục bối cảnh và cảm xúc trái ngược",
        "setting": "Flat apricot-peach (#F2B88B) 2D study bench stage.",
        "narrative_phase": "explanation",
        "tone": "analytical_crisp",
        "requirements": ["R07"],
        "source_ids": ["SRC02"],
        "claim_facts": [["Mỗi lần nhảy cảnh, não phải bẻ lái và tốn thêm sức.", "SRC02", "Mỗi lần nhảy cảnh, não phải bẻ lái và tốn thêm sức."], ["Phần chú ý cũ còn vương lại, làm đầu óc bạn lùng bùng.", "SRC02", "Phần chú ý cũ còn vương lại, làm đầu óc bạn lùng bùng."]],
        "rows": [
            (
                "Chưa hết, còn khoản phí đổi cảnh.",
                "still_life|Raw freehand 2D marker illustration on a flat apricot-peach (#F2B88B) field: a red battery meter dropping sharply beside three mismatched clip cards on a flat wooden study bench.",
                "phí đổi cảnh",
                "red battery meter",
                "cause_effect",
            ),
            (
                "Khi đo sự chú ý của con người,",
                "visual_diagram|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: a crooked black zigzag arrow leaping across four disconnected topic boxes above a draining fuel bar.",
                "sự chú ý",
                "draining fuel bar",
                "structure",
                [{"text": "ĐỔI NGỮ CẢNH", "placement": "above crooked black zigzag arrow", "object": "crooked black zigzag arrow"}, {"text": "HAO NĂNG LƯỢNG", "placement": "below draining fuel bar", "object": "draining fuel bar"}],
            ),
            (
                "giới tâm lý học ở Mỹ chỉ ra một cái bẫy.",
                "full_scene|Flat 2D front-on orthographic view on an apricot-peach (#F2B88B) stage: the white-head doodle stickman in a flat blue (#3B82C4) shirt holds a wooden pointer toward a wall chart of jagged switching tracks behind a study bench.",
                "cái bẫy",
                "jagged switching tracks",
                "context",
            ),
            (
                "Mỗi lần nhảy cảnh, não phải bẻ lái và tốn thêm sức.",
                "variation|The white-head doodle stickman grips a heavy black steering wheel mounted on the study bench and yanks it hard to the left with flying sweat drops; expression shift.",
                "bẻ lái",
                "heavy black steering wheel",
                "cause_effect",
            ),
            (
                "Vừa xem một vụ va chạm giao thông,",
                "still_life|Raw freehand 2D marker illustration on a warm paper-cream (#F8F0DC) field: a vertical phone screen showing two bumped toy cars and a flashing red siren icon beside a thirty-second stopwatch.",
                "va chạm giao thông",
                "flashing red siren icon",
                "context",
            ),
            (
                "ba mươi giây sau bạn đã lướt sang đoạn hài.",
                "still_life|Raw freehand 2D marker illustration on a pale ice-blue (#CBE0E0) field: a thirty-second timer ticking beside a vertical phone screen displaying a laughing comedy mask and a yellow banana peel.",
                "ba mươi giây",
                "thirty-second timer",
                "progression",
            ),
            (
                "Mắt chưa kịp nghỉ đã nhảy qua chuyện phá án.",
                "full_scene|Flat 2D front-on orthographic view on a slate-navy (#2E4361) stage: the white-head doodle stickman in a flat blue (#3B82C4) shirt sits stiffly at the study bench before a phone screen showing a magnifying glass and yellow tape.",
                "phá án",
                "magnifying glass",
                "progression",
            ),
            (
                "Bộ não chẳng kịp đạp phanh.",
                "variation|On the slate-navy (#2E4361) stage, the white-head doodle stickman leans back with dizzy spiral eyes and a wavy mouth as red skid marks streak across the study bench; expression shift.",
                "đạp phanh",
                "red skid marks",
                "cause_effect",
            ),
            (
                "Phần chú ý cũ còn vương lại,",
                "still_life|Raw freehand 2D marker illustration on a warm paper-cream (#F8F0DC) field: faint overlapping ink stamps of a siren, a comedy mask, and a magnifying glass smudging across a clean notebook page.",
                "vương lại",
                "faint overlapping ink stamps",
                "cause_effect",
            ),
            (
                "làm đầu óc bạn lùng bùng.",
                "white_card|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: three tangled transparent film strips piling into a muddy dark ink blotch in the center.",
                "lùng bùng",
                "muddy dark ink blotch",
                "cause_effect",
                [{"text": "CẶN CHÚ Ý", "placement": "above three tangled transparent film strips", "object": "three tangled transparent film strips"}, {"text": "ĐẦU ÓC MỜ ĐỤC", "placement": "below muddy dark ink blotch", "object": "muddy dark ink blotch"}],
            ),
        ],
    },
    {
        "scene_id": "SC08",
        "title": "Thí nghiệm căn phòng trống mười lăm phút",
        "purpose": "Chứng minh con người sợ ở một mình với suy nghĩ tới mức thà tự bấm nút chịu điện giật",
        "setting": "Flat pale ice-blue (#CBE0E0) 2D bare room stage.",
        "narrative_phase": "explanation",
        "tone": "analytical_crisp",
        "requirements": ["R08"],
        "source_ids": ["SRC03"],
        "claim_facts": [["Cứ ba người đàn ông thì hai người tự bấm, chỉ để khỏi ngồi yên mười lăm phút.", "SRC03", "Cứ ba người đàn ông thì hai người tự bấm, chỉ để khỏi ngồi yên mười lăm phút."]],
        "rows": [
            (
                "Biết là mệt, sao ta vẫn mở máy từ sáng tới đêm?",
                "still_life|Raw freehand 2D marker illustration on a warm paper-cream (#F8F0DC) field: a glowing vertical smartphone linked by a circular black loop arrow between a morning sun icon and a crescent moon icon.",
                "sáng tới đêm",
                "circular black loop arrow",
                "progression",
            ),
            (
                "Tại một trường đại học ở Mỹ,",
                "environment|Raw freehand 2D marker illustration on a pale ice-blue (#CBE0E0) stage: a stark quiet boundary room with one plain wooden chair, one bare table, and a wall timer.",
                "đại học ở mỹ",
                "bare table",
                "context",
            ),
            (
                "người ta được mời ngồi riêng trong phòng trống.",
                "full_scene|Flat 2D front-on orthographic view on a pale ice-blue (#CBE0E0) stage: the white-head doodle stickman in a flat blue (#3B82C4) shirt sits upright alone on a wooden chair behind a bare table.",
                "phòng trống",
                "sits upright alone on a wooden chair",
                "context",
            ),
            (
                "Không điện thoại, không sách vở.",
                "still_life|Raw freehand 2D marker illustration on a warm paper-cream (#F8F0DC) field: a smartphone icon and an open notebook icon each crossed out with bold red marker strokes.",
                "sách vở",
                "open notebook icon",
                "grouping",
            ),
            (
                "Trên bàn chỉ đặt chiếc hộp gây điện giật nhẹ khi bấm.",
                "still_life|Raw freehand 2D marker illustration on a flat apricot-peach (#F2B88B) field: a small gray metal box with a big red push button and a yellow lightning bolt emblem on a flat tabletop.",
                "điện giật nhẹ",
                "yellow lightning bolt emblem",
                "cause_effect",
                [{"text": "HỘP ĐIỆN GIẬT", "placement": "below small gray metal box", "object": "small gray metal box"}],
            ),
            (
                "Trước đó, ai cũng thề thà mất tiền chứ không bấm.",
                "full_scene|Flat 2D front-on orthographic view on a pale ice-blue (#CBE0E0) stage: the white-head doodle stickman in a flat blue (#3B82C4) shirt waves both round white circle hands in refusal away from the red button box beside a paper banknote.",
                "mất tiền",
                "paper banknote",
                "comparison",
            ),
            (
                "Vậy mà mới im ắng vài phút, tay chân đã bứt rứt.",
                "variation|The white-head doodle stickman hunches forward with twitching wire legs, sweat drops, and jittery black motion lines beside a ticking wall clock; expression shift.",
                "bứt rứt",
                "jittery black motion lines",
                "cause_effect",
            ),
            (
                "Cứ ba người đàn ông thì hai người tự bấm,",
                "visual_diagram|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: three simple blue T-shirt icons in a row where two T-shirt icons have bold red lightning sparks and pressed red buttons underneath.",
                "tự bấm",
                "pressed red buttons",
                "quantity",
                [{"text": "HAI PHẦN BA BẤM", "placement": "above three simple blue T-shirt icons", "object": "three simple blue T-shirt icons"}],
            ),
            (
                "chỉ để khỏi ngồi yên mười lăm phút.",
                "still_life|Raw freehand 2D marker illustration on a pale ice-blue (#CBE0E0) field: a round fifteen-minute wall timer beside the pressed red button box crackling with a tiny yellow spark.",
                "mười lăm phút",
                "fifteen-minute wall timer",
                "quantity",
                [{"text": "MƯỜI LĂM PHÚT", "placement": "above round fifteen-minute wall timer", "object": "round fifteen-minute wall timer"}],
            ),
            (
                "Ta thà chịu đau còn hơn đối diện suy nghĩ ngổn ngang.",
                "full_scene|Flat 2D front-on orthographic view on a slate-navy (#2E4361) stage: the white-head doodle stickman in a flat blue (#3B82C4) shirt pokes the red shock button with one round white circle hand while a tangled black scribble cloud floats overhead.",
                "ngổn ngang",
                "tangled black scribble cloud",
                "comparison",
            ),
        ],
    },
    {
        "scene_id": "SC09",
        "title": "Khi nào giải trí thực sự giúp bạn hồi sức?",
        "purpose": "Phản biện hai chiều để phân biệt giải trí có điểm dừng với việc dùng tạp âm gây tê nhận thức",
        "setting": "Flat sage-green (#93A88C) 2D living room stage.",
        "narrative_phase": "counter_argument",
        "tone": "reflective_slow",
        "requirements": ["R09"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Vậy chẳng lẽ giải trí trên màn hình luôn có hại?",
                "still_life|Raw freehand 2D marker illustration on a warm paper-cream (#F8F0DC) field: a brass balance scale weighing one single cinema ticket stub on the left pan against a tangled scroll ribbon on the right pan.",
                "giải trí",
                "cinema ticket stub",
                "comparison",
            ),
            (
                "Câu trả lời là không hẳn vậy.",
                "full_scene|Flat 2D front-on orthographic view on a sage-green (#93A88C) living room stage: the white-head doodle stickman in a flat blue (#3B82C4) shirt sits relaxed on a flat rectangular sofa holding one remote.",
                "không hẳn",
                "sits relaxed on a flat rectangular sofa",
                "context",
            ),
            (
                "Khi bạn chọn một bộ phim hay để xem trọn vẹn,",
                "variation|The white-head doodle stickman watches a flat television frame showing a sailboat reaching an island flag with a calm gentle smile; expression shift.",
                "bộ phim hay",
                "flat television frame",
                "structure",
            ),
            (
                "hết phim rồi tắt màn hình, đó chính là nghỉ thật.",
                "still_life|Raw freehand 2D marker illustration on a sage-green (#93A88C) field: a dark switched-off television screen beside a neat green check mark and a resting remote on a flat cabinet.",
                "tắt màn hình",
                "dark switched-off television screen",
                "progression",
                [{"text": "CÓ ĐIỂM DỪNG", "placement": "above dark switched-off television screen", "object": "dark switched-off television screen"}],
            ),
            (
                "Thứ bào mòn bạn là kiểu mở nền.",
                "visual_diagram|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: two side-by-side rectangular cards comparing a bounded arc with a finish flag on the left card and a looping arrow track on the right card.",
                "mở nền",
                "looping arrow track",
                "comparison",
                [{"text": "XEM TRỌN VẸN", "placement": "above bounded arc", "object": "bounded arc"}, {"text": "CHẠY NỀN VÔ TẬN", "placement": "above looping arrow track", "object": "looping arrow track"}],
            ),
            (
                "Tay trượt dài miên man, hoặc bật tiếng cho đỡ trống.",
                "still_life|Raw freehand 2D marker illustration on a flat apricot-peach (#F2B88B) field: an upright smartphone spewing a tall messy stack of tiny clip cards and jagged sound waves across a coffee table.",
                "bật tiếng",
                "jagged sound waves",
                "cause_effect",
            ),
            (
                "Lúc làm việc mà bên tai vẫn văng vẳng chuyện kể,",
                "full_scene|Flat 2D front-on orthographic view on a sage-green (#93A88C) living room stage: the white-head doodle stickman in a flat blue (#3B82C4) shirt bends over an open notebook with a pen while a small desktop speaker blasts black squiggle waves.",
                "làm việc",
                "open notebook with a pen",
                "cause_effect",
            ),
            (
                "thực chất bạn chẳng nghe lọt chữ nào.",
                "variation|The white-head doodle stickman freezes with blank dot eyes and a crooked frown above a crossed-out line on the notebook as speech bubbles bounce off the round white head; expression shift.",
                "chẳng nghe lọt",
                "bounce off the round white head",
                "cause_effect",
            ),
            (
                "Ta chỉ mượn tạp âm giống chiếc hộp kia,",
                "white_card|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: a glowing smartphone nested inside the gray red-button shock box emitting crooked musical notes and lightning sparks.",
                "chiếc hộp kia",
                "red-button shock box",
                "comparison",
            ),
            (
                "làm tê đi cảm giác buồn chán.",
                "still_life|Raw freehand 2D marker illustration on a pale ice-blue (#CBE0E0) field: a heavy pair of black headphones clamped tightly over a pale cloud bubble on a quiet wooden table.",
                "buồn chán",
                "pale cloud bubble",
                "cause_effect",
            ),
        ],
    },
    {
        "scene_id": "SC10",
        "title": "Ăn ra ăn, ngủ ra ngủ",
        "purpose": "Đúc kết nguyên tắc không ghép kèm màn hình vào các hoạt động sinh hoạt cơ bản",
        "setting": "Flat warm paper-cream (#F8F0DC) 2D dining stage.",
        "narrative_phase": "takeaway",
        "tone": "analytical_crisp",
        "requirements": ["R10"],
        "source_ids": ["SRC01"],
        "claim_facts": [],
        "rows": [
            (
                "Muốn đầu óc nhẹ lại, bạn đâu cần vứt điện thoại.",
                "still_life|Raw freehand 2D marker illustration on a warm paper-cream (#F8F0DC) field: a dark silent smartphone resting neatly inside a small flat wooden tray.",
                "điện thoại",
                "silent smartphone",
                "context",
            ),
            (
                "Quy tắc đầu tiên rất đơn giản.",
                "visual_diagram|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: two separate rectangular boxes divided by a bold vertical black line, placing a steaming rice bowl on the left and a silent phone icon on the right.",
                "quy tắc",
                "two separate rectangular boxes",
                "grouping",
                [{"text": "ĂN RA ĂN", "placement": "below steaming rice bowl", "object": "steaming rice bowl"}, {"text": "XEM RA XEM", "placement": "below silent phone icon", "object": "silent phone icon"}],
            ),
            (
                "Lúc ăn chỉ tập trung ăn.",
                "full_scene|Flat 2D front-on orthographic dining stage on a warm paper-cream (#F8F0DC) background: the white-head doodle stickman sits calmly at a flat brown table holding chopsticks and enjoying a warm rice bowl with zero screens nearby.",
                "tập trung ăn",
                "enjoying a warm rice bowl",
                "context",
            ),
            (
                "Bước vào nhà vệ sinh thì để máy ở ngoài.",
                "variation|The white-head doodle stickman leaves the smartphone flat on the dining table and walks empty-handed toward a simple rectangular doorway on the right; expression shift.",
                "để máy ở ngoài",
                "leaves the smartphone flat on the dining table",
                "context",
            ),
            (
                "Trước khi ngủ, bạn đặt điện thoại sang bàn phía xa.",
                "still_life|Raw freehand 2D marker illustration on a slate-navy (#2E4361) night field: a dark smartphone resting on a distant wooden desk across from a clean white pillow.",
                "bàn phía xa",
                "distant wooden desk",
                "structure",
            ),
            (
                "Đừng bắt bộ não vừa nhai cơm,",
                "concept_metaphor|Raw freehand 2D doodle on an apricot-peach (#F2B88B) field: above the white-head doodle stickman's round white head, an overloaded red cartoon brain (#D9534F) sweats with strain marks while lifting a heavy rice bowl.",
                "nhai cơm",
                "heavy rice bowl",
                "cause_effect",
            ),
            (
                "vừa phải nuốt thêm một bản tóm tắt phim.",
                "still_life|Raw freehand 2D marker illustration on a warm paper-cream (#F8F0DC) field: a clapperboard and tangled film strip crossed out with a bold red X beside a clean porcelain spoon.",
                "tóm tắt phim",
                "clapperboard and tangled film strip",
                "cause_effect",
            ),
            (
                "Những quãng ngắt nhỏ ấy giúp tâm trí kịp thở nhẹ nhàng.",
                "environment|Raw freehand 2D marker illustration on a soft sage-green (#93A88C) dining stage: a quiet flat tabletop with a single warm ceramic teacup sending up three gentle steam lines.",
                "thở nhẹ nhàng",
                "three gentle steam lines",
                "cause_effect",
            ),
        ],
    },
    {
        "scene_id": "SC11",
        "title": "Mười phút thả lỏng nhìn mây trời",
        "purpose": "Hướng dẫn thực hành khoảng nghỉ trắng không âm thanh để kích hoạt mạng lưới tự phục hồi",
        "setting": "Flat apricot-peach (#F2B88B) 2D open balcony stage.",
        "narrative_phase": "takeaway",
        "tone": "narrative_warm",
        "requirements": ["R11"],
        "source_ids": ["SRC01"],
        "claim_facts": [],
        "rows": [
            (
                "Cách thứ hai là chừa ra một khoảng nghỉ trắng.",
                "visual_diagram|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: three horizontal schedule blocks in a row where a clean white blank block sits between two blue work blocks.",
                "khoảng nghỉ trắng",
                "clean white blank block",
                "structure",
                [{"text": "LÀM VIỆC SÂU", "placement": "above blue work blocks", "object": "blue work blocks"}, {"text": "NGHỈ TRẮNG", "placement": "above clean white blank block", "object": "clean white blank block"}],
            ),
            (
                "Sau mỗi giờ học hay làm việc,",
                "still_life|Raw freehand 2D marker illustration on a warm paper-cream (#F8F0DC) field: a closed paper notebook with a black pen resting across its cover beside a cup of warm water.",
                "làm việc",
                "closed paper notebook",
                "context",
            ),
            (
                "bạn hãy tháo tai nghe mười phút.",
                "full_scene|Flat 2D side-on orthographic open balcony stage on an apricot-peach (#F2B88B) background: the white-head doodle stickman stands beside a black balcony railing using both round white circle hands to lift wireless earbuds away from the head.",
                "tháo tai nghe",
                "lift wireless earbuds away",
                "context",
            ),
            (
                "Đừng vội mở mạng xã hội.",
                "variation|The white-head doodle stickman snaps the wireless earbuds shut inside a small round case and leaves a dark smartphone face-down on a low stool; expression shift.",
                "mạng xã hội",
                "leaves a dark smartphone face-down",
                "context",
            ),
            (
                "Cứ đứng tựa lan can nhìn bầu trời.",
                "environment|Raw freehand 2D marker illustration on a pale ice-blue (#CBE0E0) open balcony stage: a simple horizontal black railing facing a wide open sky with two drifting white clouds and flat rooftops.",
                "nhìn bầu trời",
                "wide open sky",
                "context",
            ),
            (
                "Vài phút đầu có thể hơi bồn chồn,",
                "still_life|Raw freehand 2D marker illustration on a flat apricot-peach (#F2B88B) field: a small glass sand hourglass with wobbly black marker outlines as the top sand grains start trickling down.",
                "vài phút đầu",
                "sand hourglass",
                "progression",
            ),
            (
                "nhưng cảm giác bức bối đó qua nhanh.",
                "full_scene|Flat 2D front-on orthographic open balcony stage on an apricot-peach (#F2B88B) background: the white-head doodle stickman leans relaxed elbows on the black railing with calm U-shaped eyes as a gentle breeze line curls past.",
                "qua nhanh",
                "gentle breeze line",
                "progression",
            ),
            (
                "Tiếng ồn vừa dứt, đội dọn dẹp trong đầu liền vào ca.",
                "cutaway_detail|Flat 2D front close-up on a warm paper-cream (#F8F0DC) field: an open cranium window inside the upper pure-white (#FFFFFF) round head of the doodle stickman shows a miniature pure-white (#FFFFFF) circle-head doodle stickman in a blue (#3B82C4) shirt sweeping scraps away and aligning folders on a shelf.",
                "đội dọn dẹp",
                "sweeping scraps away",
                "cause_effect",
            ),
            (
                "Những ý tưởng rời rạc bỗng tự khớp lại thật gọn gàng.",
                "visual_diagram|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: three scattered rectangular note cards connected by wobbly black marker arrows snapping cleanly into one aligned horizontal row.",
                "khớp lại",
                "snapping cleanly into one aligned horizontal row",
                "structure",
            ),
        ],
    },
    {
        "scene_id": "SC12",
        "title": "Sáng mai, nằm yên một phút",
        "purpose": "Khép vòng lặp với cảnh thức dậy buổi sáng và thông điệp bảo vệ khoảng lặng cho tâm trí",
        "setting": "Flat pale ice-blue (#CBE0E0) 2D morning room stage.",
        "narrative_phase": "closing",
        "tone": "reflective_slow",
        "requirements": ["R12"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Sáng mai thức dậy, bạn thử nằm yên một phút",
                "environment|Raw freehand 2D marker illustration on a pale ice-blue (#CBE0E0) morning room stage: a bright rectangular bedroom window above a neat flat mattress with a dark phone resting far away on a desk.",
                "sáng mai",
                "morning room stage",
                "context",
            ),
            (
                "trước khi chạm tay vào màn hình.",
                "still_life|Raw freehand 2D marker illustration on a warm paper-cream (#F8F0DC) field: a silent dark smartphone lying untouched on a flat wooden tabletop beside a clear glass of water.",
                "màn hình",
                "silent dark smartphone",
                "context",
            ),
            (
                "Bạn mệt chẳng phải vì làm quá sức.",
                "white_card|Raw freehand 2D marker illustration on a pure white (#FFFFFF) field: two simple vertical meter bars side by side showing a calm half-filled green work bar on the left and a red overflowing noise bar on the right.",
                "quá sức",
                "red overflowing noise bar",
                "comparison",
                [{"text": "VIỆC LÀM VỪA ĐỦ", "placement": "below green work bar", "object": "green work bar"}, {"text": "QUÁ TẢI TẠP ÂM", "placement": "below red overflowing noise bar", "object": "red overflowing noise bar"}],
            ),
            (
                "Đầu bạn nặng trịch suốt ngày dài,",
                "full_scene|Flat 2D side-on orthographic morning room stage on a pale ice-blue (#CBE0E0) background: the white-head doodle stickman sits sluggishly on the edge of the flat bed holding a heavy drooping round white head with dark under-eye lines.",
                "nặng trịch",
                "heavy drooping round white head",
                "cause_effect",
            ),
            (
                "vì bộ não thiếu hẳn phút yên ắng để tự thu dọn.",
                "still_life|Raw freehand 2D marker illustration on a soft sage-green (#93A88C) field: a neat row of upright sorted memory folders standing calmly beside a warm morning teacup.",
                "tự thu dọn",
                "upright sorted memory folders",
                "structure",
            ),
            (
                "Tối nay, bạn hãy tắt tiếng phát rì rầm bên gối.",
                "full_scene|Flat 2D night bedroom stage on a slate-navy (#2E4361) background: the white-head doodle stickman lies calmly under a flat blue blanket (#3B82C4) reaching one round white circle hand over to switch off a smartphone beside the pillow.",
                "rì rầm bên gối",
                "switch off a smartphone beside the pillow",
                "cause_effect",
            ),
            (
                "Đừng sợ căn phòng im tiếng.",
                "variation|On the slate-navy (#2E4361) night bedroom stage, the white-head doodle stickman rests both eyes shut in peaceful U-shaped curves on the white pillow beside the dark silent smartphone under a small crescent-moon window; expression shift.",
                "im tiếng",
                "dark silent smartphone",
                "context",
            ),
            (
                "Cho tâm trí một khoảng lặng, bạn mới nghỉ ngơi trọn vẹn.",
                "environment|Raw freehand 2D marker illustration on a pale ice-blue (#CBE0E0) morning room stage: an open bedroom window letting three gentle breeze lines curl into a quiet sunny room above a neatly made flat bed.",
                "khoảng lặng",
                "open bedroom window",
                "cause_effect",
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
                    "Keep the exact 2D composition, camera angle, flat background color and character design from the parent base frame. "
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
                "Phần chú ý cũ còn vương lại, làm đầu óc bạn lùng bùng.",
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

    visual_hook = "Raw freehand 2D Vietnamese indie doodle on a flat slate-navy (#2E4361) night stage: the white-head doodle stickman lies motionless under a flat blue blanket (#3B82C4) holding up a glowing smartphone, while an open cranium cutaway above the pure-white (#FFFFFF) round head shows a miniature stickman sprinting exhausted with sweat drops inside a spinning wheel"
    text_overlay = "NGHỈ MÀ MỆT HƠN"
    contrast_pair = "Cơ thể nằm nghỉ vs. Bộ não tăng ca"
    thumbnail_prompt = (
        f"16:9 YouTube thumbnail poster in raw freehand 2D Vietnamese indie doodle style on a flat slate-navy (#2E4361) stage "
        f"with bold pitch-black (#000000) marker contours and 100% flat MS-Paint paint-bucket fills. "
        f"Focal subject: {visual_hook}. Contrast: {contrast_pair}. "
        f"Top-center bold hand-drawn golden-yellow (#FACC15) uppercase Vietnamese lettering '{text_overlay}' with thick pitch-black (#000000) marker outline, zero drop shadow."
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
        typography_style="Bold hand-drawn golden-yellow (#FACC15) uppercase poster lettering with thick pitch-black (#000000) marker outline",
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
            if int(sc_spec.scene_id[2:]) >= 3 and beat_spec.shot_type == "full_scene":
                img_dict["shot_type"] = "full_scene"
                img_dict["based_on"] = None
                img_dict["preserve"] = ""
                img_dict["change"] = beat_spec.change
                img_dict.pop("allow_expression_shift", None)

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
