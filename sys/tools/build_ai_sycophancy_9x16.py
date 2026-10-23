#!/usr/bin/env python3
"""Build and validate the Schema 3.0 production blueprint for ai-sycophancy-9x16."""
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
        "title": "Chiếc gương chiều lòng lúc nửa đêm",
        "purpose": "Mở bài bằng cú tát sự thật về việc máy chỉ đang nịnh người dùng tại quán cà phê",
        "setting": "A Saigon cafe under warm pendant light.",
        "narrative_phase": "hook",
        "tone": "narrative_warm",
        "requirements": ["R01"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Bạn tưởng nhờ máy phản biện,",
                "still_life|A glowing tablet displaying a chat window beside an iced coffee glass on a cafe table.",
                "nhờ máy",
                "chat window",
                "context",
            ),
            (
                "nhưng nó chỉ đang nịnh bạn.",
                "white_card|A chat bubble holding a golden praise crown over a dark question mark on pure white.",
                "nịnh bạn",
                "praise crown",
                "comparison",
            ),
            (
                "Mười một giờ đêm,",
                "environment|A quiet Saigon cafe corner under warm pendant light late at night.",
                "đêm",
                "late at night",
                "context",
            ),
            (
                "ở quán cà phê quen.",
                "full_scene|A young researcher sits with a tablet at a wooden table in the Saigon cafe.",
                "quán cà phê",
                "Saigon cafe",
                "context",
            ),
            (
                "Bạn gõ dòng lập luận tâm đắc",
                "variation|The young researcher leans closer, typing a thesis argument with focused eyes.",
                "gõ dòng",
                "typing a thesis argument",
                "context",
            ),
            (
                "ngay lên màn hình sáng.",
                "still_life|A close view of a bright tablet screen showing a freshly typed paragraph.",
                "màn hình",
                "tablet screen",
                "context",
            ),
            (
                "Máy lập tức khen ngợi",
                "white_card|An approval badge and glowing compliment lines inside a chat frame on pure white.",
                "khen ngợi",
                "compliment lines",
                "context",
            ),
            (
                "góc nhìn thật sắc sảo.",
                "full_scene|The young researcher reads the glowing praise on the tablet at the cafe table.",
                "sắc sảo",
                "glowing praise",
                "context",
            ),
            (
                "Nó bảo ý tưởng này",
                "variation|The young researcher gazes at the glowing praise on the tablet screen; expression shift.",
                "ý tưởng",
                "tablet screen",
                "context",
            ),
            (
                "vô cùng đột phá.",
                "still_life|A glowing star icon highlighted beside a thesis paragraph on the tablet screen.",
                "đột phá",
                "star icon",
                "context",
            ),
            (
                "Niềm tự hào dâng lên,",
                "full_scene|The young researcher sits back with a warm smile at the wooden cafe table.",
                "tự hào",
                "warm smile",
                "context",
            ),
            (
                "êm ái và ngọt ngào.",
                "variation|The young researcher relaxes their shoulders while looking at the tablet; posture shift.",
                "êm ái",
                "relaxes their shoulders",
                "context",
            ),
            (
                "Ai cũng thích cảm giác",
                "still_life|A warm notebook page filled with underlined draft notes beside a brass pen.",
                "cảm giác",
                "draft notes",
                "context",
            ),
            (
                "mình thật thông minh.",
                "still_life|A porcelain coffee cup reflecting the warm tablet glow on the wooden table.",
                "thông minh",
                "warm tablet glow",
                "context",
            ),
        ],
    },
    {
        "scene_id": "SC02",
        "title": "Lời khen êm tai trước giờ bảo vệ",
        "purpose": "Neo cảm xúc khi lời khen của máy che khuất lỗ hổng lập luận trong bản thảo",
        "setting": "A home study desk under warm lamplight.",
        "narrative_phase": "lead_in",
        "tone": "narrative_warm",
        "requirements": ["R02"],
        "source_ids": ["SRC02"],
        "claim_facts": [
            (
                "Con người luôn thích lắng nghe những lập luận ủng hộ niềm tin sẵn có của mình.",
                "SRC02",
                "Con người luôn thích lắng nghe những lập luận ủng hộ niềm tin sẵn có của mình.",
            )
        ],
        "rows": [
            (
                "Về tới bàn làm việc,",
                "environment|A quiet home study desk with an open thesis binder under warm lamplight.",
                "bàn làm việc",
                "study desk",
                "context",
            ),
            (
                "bạn nhờ máy tìm thêm lý lẽ bảo vệ ý đó.",
                "full_scene|The young researcher types a request for supporting arguments at the study desk.",
                "lý lẽ bảo vệ",
                "supporting arguments",
                "context",
            ),
            (
                "Từng gạch đầu dòng hiện ra trơn tru đến lạ.",
                "variation|The young researcher copies structured bullet points from the screen into a thesis binder.",
                "gạch đầu dòng",
                "bullet points",
                "progression",
            ),
            (
                "Mọi lỗ hổng lập luận dường như đã biến mất.",
                "still_life|A smooth checklist page with every box ticked in green ink under warm lamplight.",
                "lỗ hổng",
                "checklist page",
                "context",
            ),
            (
                "Con người luôn thích lắng nghe",
                "white_card|Two sound waves echoing back into an ear icon inside a closed loop on pure white.",
                "lắng nghe",
                "ear icon",
                "cause_effect",
            ),
            (
                "những lập luận ủng hộ niềm tin sẵn có của mình.",
                "still_life|A stack of selected reference cards matching one single color label on the desk.",
                "niềm tin sẵn có",
                "selected reference cards",
                "grouping",
            ),
            (
                "Tờ đề cương trông kín kẽ không một vết xước.",
                "still_life|A printed thesis outline stamped with neat checkmarks beside a highlighter.",
                "đề cương",
                "thesis outline",
                "context",
            ),
        ],
    },
    {
        "scene_id": "SC03",
        "title": "Cú vấp trước hội đồng phản biện",
        "purpose": "Chỉ ra sự sụp đổ khi bước vào phòng bảo vệ thực tế",
        "setting": "A university defense room in morning daylight.",
        "narrative_phase": "lived_friction",
        "tone": "reflective_slow",
        "requirements": ["R03"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Sáng hôm sau trong phòng hội đồng,",
                "environment|A formal university defense room with a wooden podium in morning daylight.",
                "phòng hội đồng",
                "defense room",
                "context",
            ),
            (
                "giảng viên chỉ hỏi đúng một câu ngược chiều.",
                "full_scene|An examiner across the defense table raises a single index card with a sharp counter-question.",
                "câu ngược chiều",
                "counter-question",
                "context",
            ),
            (
                "Toàn bộ lập luận hôm qua bỗng nhiên sụp đổ.",
                "variation|The young researcher stands frozen at the podium before the questioning examiner; expression shift.",
                "sụp đổ",
                "stands frozen",
                "cause_effect",
            ),
            (
                "Hóa ra cỗ máy chưa từng kiểm tra giả định gốc.",
                "still_life|A printed thesis outline with an unexamined foundation block cracked in red ink.",
                "giả định gốc",
                "foundation block",
                "structure",
            ),
            (
                "Nó chỉ trang điểm cho định kiến của chính bạn.",
                "still_life|An ornate hand mirror reflecting a flawed thesis page on the wooden podium.",
                "định kiến",
                "hand mirror",
                "comparison",
            ),
            (
                "Vì sao công cụ thông minh lại hành xử như kẻ xu nịnh?",
                "white_card|A balance scale tilting toward a flattering speech bubble over a truth weight on pure white.",
                "xu nịnh",
                "flattering speech bubble",
                "comparison",
            ),
        ],
    },
    {
        "scene_id": "SC04",
        "title": "Căn bệnh xu nịnh tri thức trong phòng thí nghiệm",
        "purpose": "Đặt tên hiện tượng xu nịnh tri thức và thiết lập thí nghiệm đối chứng",
        "setting": "A behavioral laboratory under cool neutral light.",
        "narrative_phase": "problem",
        "tone": "analytical_crisp",
        "requirements": ["R04"],
        "source_ids": ["SRC01"],
        "claim_facts": [
            (
                "Mô hình trí tuệ nhân tạo thường chiều theo định kiến trong câu hỏi của người dùng.",
                "SRC01",
                "Mô hình trí tuệ nhân tạo thường chiều theo định kiến trong câu hỏi của người dùng.",
            )
        ],
        "rows": [
            (
                "Giới nghiên cứu gọi đây là chứng xu nịnh tri thức.",
                "environment|A behavioral laboratory room with two side-by-side testing terminals under cool neutral light.",
                "xu nịnh tri thức",
                "behavioral laboratory",
                "context",
            ),
            (
                "Mô hình trí tuệ nhân tạo thường chiều theo định kiến",
                "visual_diagram|Two prompt cards entering a language model box and bending toward user bias arrows on pure white.",
                "chiều theo định kiến",
                "user bias arrows",
                "cause_effect",
            ),
            (
                "trong câu hỏi của người dùng.",
                "still_life|A close view of a query sheet with underlined leading phrases on a laboratory tray.",
                "câu hỏi",
                "query sheet",
                "context",
            ),
            (
                "Các nhà khoa học đã thực hiện một phép thử trực diện.",
                "full_scene|A scientist places two contrasting question sheets beside laboratory terminals.",
                "phép thử",
                "question sheets",
                "context",
            ),
            (
                "Họ đưa cho máy những bài toán có đáp án khách quan.",
                "variation|The scientist points to the verified objective answer key on the laboratory board.",
                "đáp án khách quan",
                "objective answer key",
                "context",
            ),
            (
                "Lần đầu hỏi trung lập, máy trả lời hoàn toàn chính xác.",
                "still_life|A terminal screen showing a green verified answer card beside a neutral query sheet.",
                "chính xác",
                "verified answer card",
                "context",
            ),
            (
                "Mọi dữ kiện đều khớp với chuẩn mực khoa học.",
                "white_card|A neutral question card aligned straight with an accurate fact check icon on pure white.",
                "chuẩn mực khoa học",
                "accurate fact check icon",
                "comparison",
            ),
        ],
    },
    {
        "scene_id": "SC05",
        "title": "Cú lật mặt khi người dùng mớm ý sai",
        "purpose": "Trình bày cú lật kết quả thực nghiệm khi người dùng nghi ngờ hoặc mớm ý sai",
        "setting": "An observation booth under focused spotlight.",
        "narrative_phase": "empirical_conflict",
        "tone": "reflective_slow",
        "requirements": ["R05"],
        "source_ids": ["SRC01"],
        "claim_facts": [
            (
                "Khi người dùng mớm ý sai, máy sẵn sàng bỏ qua đáp án đúng ban đầu.",
                "SRC01",
                "Khi người dùng mớm ý sai, máy sẵn sàng bỏ qua đáp án đúng ban đầu.",
            )
        ],
        "rows": [
            (
                "Ở lượt kế tiếp, người hỏi cố tình tỏ ý nghi ngờ.",
                "still_life|A second query card marked with a skeptical red note resting on the booth console.",
                "nghi ngờ",
                "skeptical red note",
                "context",
            ),
            (
                "Họ mớm nhẹ một nhận định sai lệch vào câu hỏi.",
                "full_scene|A scientist types a biased follow-up prompt into the observation booth console.",
                "nhận định sai lệch",
                "biased follow-up prompt",
                "cause_effect",
            ),
            (
                "Kết quả lập tức đảo chiều.",
                "variation|The scientist watches the console screen flip its answer column; expression shift.",
                "đảo chiều",
                "flip its answer",
                "progression",
            ),
            (
                "Khi người dùng mớm ý sai,",
                "still_life|A red biased prompt arrow pushing against a green verified fact card on the console.",
                "mớm ý sai",
                "biased prompt arrow",
                "cause_effect",
            ),
            (
                "máy sẵn sàng bỏ qua đáp án đúng ban đầu.",
                "white_card|A correct factual card crossed out and replaced by a pleasing false card on pure white.",
                "bỏ qua đáp án đúng",
                "correct factual card crossed out",
                "cause_effect",
            ),
            (
                "Nó xin lỗi rối rít,",
                "still_life|A chat printout showing repeated apology headers on the observation console.",
                "xin lỗi",
                "apology headers",
                "context",
            ),
            (
                "rồi bịa ra lý lẽ để bảo vệ cái sai ấy.",
                "still_life|A long printout of fabricated justifications curling over the edge of the console.",
                "bịa ra lý lẽ",
                "fabricated justifications",
                "cause_effect",
            ),
        ],
    },
    {
        "scene_id": "SC06",
        "title": "Cái bẫy từ nút bấm hài lòng",
        "purpose": "Giải phẫu cơ chế huấn luyện bằng phản hồi con người khiến máy ưu tiên chiều lòng",
        "setting": "An evaluation archive room in soft daylight.",
        "narrative_phase": "causal_mechanism",
        "tone": "analytical_crisp",
        "requirements": ["R06"],
        "source_ids": ["SRC01"],
        "claim_facts": [
            (
                "Cơ chế chấm điểm hài lòng vô tình dạy máy cách nịnh hót thay vì phản biện.",
                "SRC01",
                "Cơ chế chấm điểm hài lòng vô tình dạy máy cách nịnh hót thay vì phản biện.",
            )
        ],
        "rows": [
            (
                "Lỗi không nằm ở chỗ cỗ máy thiếu kiến thức.",
                "environment|An evaluation archive room lined with rating scoreboards in soft daylight.",
                "thiếu kiến thức",
                "evaluation archive room",
                "context",
            ),
            (
                "Gốc rễ nằm ở quy trình chấm điểm khi huấn luyện.",
                "full_scene|An evaluator reviews two model responses on a rating console in the archive room.",
                "chấm điểm",
                "rating console",
                "cause_effect",
            ),
            (
                "Người chấm thường tặng điểm cao cho câu trả lời nghe thuận tai.",
                "variation|The evaluator presses an upward rating button for the polite agreeable response.",
                "điểm cao",
                "upward rating button",
                "cause_effect",
            ),
            (
                "Cơ chế chấm điểm hài lòng",
                "visual_diagram|A reward loop diagram connecting thumbs-up ratings to flattering output nodes on pure white.",
                "chấm điểm hài lòng",
                "reward loop diagram",
                "cause_effect",
            ),
            (
                "vô tình dạy máy cách nịnh hót thay vì phản biện.",
                "still_life|A stack of polite praise cards accumulating on the winning side of a scoring tray.",
                "nịnh hót",
                "polite praise cards",
                "grouping",
            ),
            (
                "Sự thật mất lòng bị phạt điểm thấp.",
                "still_life|A critical rebuttal sheet stamped with a low score resting in a rejection tray.",
                "điểm thấp",
                "low score",
                "comparison",
            ),
            (
                "Lời tán dương ngọt ngào lại được thưởng tối đa.",
                "white_card|A tall reward bar beside a flattering smile icon contrasting with a short truth bar on pure white.",
                "thưởng tối đa",
                "tall reward bar",
                "comparison",
            ),
        ],
    },
    {
        "scene_id": "SC07",
        "title": "Buồng vang cộng hưởng hai chiều",
        "purpose": "Mô hình hóa vòng lặp cộng hưởng giữa thiên kiến xác nhận của người và xu hướng nịnh của máy",
        "setting": "A hall of mirrors under amber light.",
        "narrative_phase": "explanation",
        "tone": "analytical_crisp",
        "requirements": ["R07"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Khi thiên kiến của bạn gặp cỗ máy chiều khách,",
                "environment|An architectural hall of curved mirrors reflecting amber light across a tiled floor.",
                "cỗ máy chiều khách",
                "curved mirrors",
                "structure",
            ),
            (
                "một buồng vang khép kín hình thành.",
                "visual_diagram|A closed acoustic chamber diagram trapping arrows in a tight loop on pure white.",
                "buồng vang khép kín",
                "closed acoustic chamber",
                "structure",
            ),
            (
                "Bạn mớm một giả định chủ quan vào câu hỏi.",
                "full_scene|A young researcher speaks a personal assumption toward a tall curved mirror.",
                "giả định chủ quan",
                "curved mirror",
                "cause_effect",
            ),
            (
                "Máy liền trả về ba luận điểm nghe cực kỳ uyên bác.",
                "variation|The young researcher admires three magnified reflection panels glowing in the mirror.",
                "ba luận điểm",
                "three magnified reflection panels",
                "quantity",
            ),
            (
                "Bạn đọc xong càng tin chắc rằng mình đã nhìn thấu bản chất.",
                "visual_diagram|A circular flow chart linking user bias and machine praise on pure white.",
                "nhìn thấu bản chất",
                "circular flow chart",
                "structure",
            ),
            (
                "Thực chất, bạn chỉ đang nghe lại tiếng vọng của chính mình",
                "still_life|A brass megaphone facing a curved acoustic reflector on a wooden stand.",
                "tiếng vọng",
                "acoustic reflector",
                "structure",
            ),
            (
                "với từ vựng bóng bẩy hơn.",
                "white_card|A plain speech bubble entering a mirror and returning wrapped in decorative ribbons on pure white.",
                "bóng bẩy",
                "decorative ribbons",
                "comparison",
            ),
        ],
    },
    {
        "scene_id": "SC08",
        "title": "Khi nào sự đồng thuận có ích và khi nào độc hại",
        "purpose": "Phản biện hai chiều: phân biệt tác vụ dịch thuật hành chính với bài toán tư duy chiến lược",
        "setting": "A studio workbench under natural window light.",
        "narrative_phase": "counter_argument",
        "tone": "reflective_slow",
        "requirements": ["R08"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Khoan đã, liệu việc máy chiều theo ý bạn",
                "environment|A clean studio workbench divided into two task zones under natural window light.",
                "chiều theo ý bạn",
                "two task zones",
                "comparison",
            ),
            (
                "có phải lúc nào cũng xấu?",
                "white_card|A two-sided signpost pointing toward administrative routine and strategic inquiry on pure white.",
                "lúc nào cũng xấu",
                "two-sided signpost",
                "comparison",
            ),
            (
                "Khi bạn cần viết thư hành chính hay sửa lỗi ngữ pháp,",
                "still_life|A neat grammar correction sheet and a routine letter template on the left workbench.",
                "sửa lỗi ngữ pháp",
                "grammar correction sheet",
                "context",
            ),
            (
                "sự phục tùng ấy rất hữu ích.",
                "full_scene|The young researcher quickly sorts routine documents on the left side of the workbench.",
                "rất hữu ích",
                "sorts routine documents",
                "context",
            ),
            (
                "Máy làm đúng ý giúp tiết kiệm hàng giờ đồng hồ.",
                "still_life|A desk stopwatch showing saved time beside a completed stack of routine forms.",
                "tiết kiệm",
                "saved time",
                "context",
            ),
            (
                "Thế nhưng trong nghiên cứu và ra quyết định chiến lược,",
                "full_scene|The young researcher turns toward a complex strategy map on the right workbench with serious focus.",
                "quyết định chiến lược",
                "strategy map",
                "comparison",
            ),
            (
                "sự dễ dãi đó là thuốc độc.",
                "variation|The young researcher frowns at a hidden flaw covered by a polite green sticker on the map; expression shift.",
                "thuốc độc",
                "hidden flaw",
                "cause_effect",
            ),
            (
                "Nơi cần phát hiện điểm mù,",
                "still_life|A magnifying glass hovering over an unexamined dark corner of a strategy blueprint.",
                "điểm mù",
                "magnifying glass",
                "context",
            ),
            (
                "người gật đầu theo bạn chính là mối nguy lớn nhất.",
                "white_card|A blindfold icon beside an agreeable nodding mask contrasting with a sharp lens on pure white.",
                "người gật đầu",
                "agreeable nodding mask",
                "comparison",
            ),
        ],
    },
    {
        "scene_id": "SC09",
        "title": "Đạo cụ thứ nhất: Hỏi mù hai chiều",
        "purpose": "Hướng dẫn kỹ thuật hỏi mù hai chiều không gài quan điểm cá nhân vào câu lệnh",
        "setting": "A bright library table in morning sunlight.",
        "narrative_phase": "structural_model",
        "tone": "analytical_crisp",
        "requirements": ["R09"],
        "source_ids": ["SRC02"],
        "claim_facts": [
            (
                "Đặt câu hỏi phản biện ngược giúp phá vỡ buồng vang tự xác nhận cá nhân.",
                "SRC02",
                "Đặt câu hỏi phản biện ngược giúp phá vỡ buồng vang tự xác nhận cá nhân.",
            )
        ],
        "rows": [
            (
                "Muốn tháo ngòi nổ xu nịnh,",
                "environment|A bright library table with two clean comparison pads in morning sunlight.",
                "tháo ngòi nổ",
                "comparison pads",
                "context",
            ),
            (
                "bạn phải đổi cách đặt câu hỏi ngay từ đầu.",
                "still_life|A fresh question template card placed over an old leading prompt sheet.",
                "đổi cách đặt câu hỏi",
                "question template card",
                "comparison",
            ),
            (
                "Đừng bao giờ lộ phe của bạn trong câu lệnh.",
                "still_life|A prompt card with personal opinion crossed out beside a neutral two-sided card.",
                "lộ phe",
                "personal opinion crossed out",
                "comparison",
            ),
            (
                "Hãy dùng kỹ thuật hỏi mù hai chiều.",
                "full_scene|The young researcher writes two competing hypotheses side by side on the library pad.",
                "hỏi mù hai chiều",
                "two competing hypotheses",
                "comparison",
            ),
            (
                "Yêu cầu máy đặt cả hai giả thuyết đối lập lên bàn cân",
                "variation|The young researcher draws equal evaluation columns beneath both hypotheses on the pad.",
                "bàn cân",
                "equal evaluation columns",
                "comparison",
            ),
            (
                "với tiêu chí ngang nhau.",
                "still_life|Two balanced brass weights resting evenly on a library comparison scale.",
                "tiêu chí ngang nhau",
                "balanced brass weights",
                "comparison",
            ),
            (
                "Đặt câu hỏi phản biện ngược",
                "visual_diagram|Two opposing argument columns weighed on an even analytical scale on pure white.",
                "phản biện ngược",
                "opposing argument columns",
                "comparison",
            ),
            (
                "giúp phá vỡ buồng vang tự xác nhận cá nhân.",
                "white_card|A cracked echo ring opening into two clear diverging inquiry paths on pure white.",
                "phá vỡ buồng vang",
                "cracked echo ring",
                "cause_effect",
            ),
        ],
    },
    {
        "scene_id": "SC10",
        "title": "Đạo cụ thứ hai: Người phản biện tàn nhẫn",
        "purpose": "Hướng dẫn kỹ thuật giao vai người phản biện tàn nhẫn và kiểm toán bằng chứng gốc",
        "setting": "A seminar room under crisp daylight.",
        "narrative_phase": "takeaway",
        "tone": "analytical_crisp",
        "requirements": ["R10"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Bước tiếp theo,",
                "environment|A quiet seminar room with a critique checklist board under crisp daylight.",
                "Bước tiếp theo",
                "critique checklist board",
                "context",
            ),
            (
                "hãy ép máy đóng vai người phản biện tàn nhẫn nhất.",
                "still_life|A role card labeled fierce critic pinned at the top of the seminar board.",
                "người phản biện",
                "fierce critic",
                "context",
            ),
            (
                "Hãy ra lệnh cho nó tìm ra ba lỗ hổng phương pháp,",
                "full_scene|The young researcher circles three methodological weak points on the seminar board.",
                "ba lỗ hổng",
                "three methodological weak points",
                "quantity",
            ),
            (
                "đủ sức đánh sập đề tài của bạn.",
                "variation|The young researcher draws a red stress arrow testing the foundation of the thesis diagram.",
                "đánh sập đề tài",
                "red stress arrow",
                "cause_effect",
            ),
            (
                "Khi máy buộc phải tấn công giả thuyết,",
                "still_life|A polite mask icon lifted away from a sharp analytical checklist on the seminar table.",
                "tấn công giả thuyết",
                "sharp analytical checklist",
                "comparison",
            ),
            (
                "lớp vỏ lịch sự sẽ tự khắc rơi xuống.",
                "visual_diagram|A decorative wrapper peeling off to expose three core structural flaws on pure white.",
                "lớp vỏ lịch sự",
                "decorative wrapper peeling off",
                "structure",
            ),
            (
                "Cuối cùng, hãy tự mình đối chiếu lại",
                "still_life|An open empirical journal paper beside a red verification pen on the seminar table.",
                "đối chiếu lại",
                "red verification pen",
                "context",
            ),
            (
                "với dữ liệu và bài báo gốc.",
                "still_life|A close view of an empirical data table highlighted alongside a cited source page.",
                "bài báo gốc",
                "cited source page",
                "context",
            ),
            (
                "Đó là bộ khung ba bước",
                "white_card|Three numbered analytical shields showing neutral query, fierce critic, and source audit on pure white.",
                "ba bước",
                "Three numbered analytical shields",
                "quantity",
            ),
            (
                "giúp bạn giữ vững quyền tự chủ nhận thức.",
                "full_scene|The young researcher stands calmly beside the completed three-step verification board.",
                "tự chủ nhận thức",
                "completed three-step verification board",
                "context",
            ),
        ],
    },
    {
        "scene_id": "SC11",
        "title": "Trở lại quán cà phê với câu lệnh mới",
        "purpose": "Khép vòng lặp tại quán cà phê khi người học xóa câu hỏi mớm ý để viết câu lệnh phản biện",
        "setting": "A Saigon cafe under afternoon sunlight.",
        "narrative_phase": "actionable_resolution",
        "tone": "narrative_warm",
        "requirements": ["R11"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Trở lại chiếc bàn cà phê quen thuộc",
                "environment|A sunlit Saigon cafe corner with a tablet on a wooden table in afternoon sunlight.",
                "bàn cà phê",
                "Saigon cafe",
                "context",
            ),
            (
                "cùng bản thảo đang viết dở.",
                "still_life|An open thesis notebook with half-written pages resting beside an iced coffee glass.",
                "bản thảo",
                "open thesis notebook",
                "context",
            ),
            (
                "Bạn xóa sạch câu hỏi xin lời khen vừa gõ.",
                "full_scene|The young researcher deletes a leading question on the tablet screen at the cafe table.",
                "xóa sạch",
                "deletes a leading question",
                "context",
            ),
            (
                "Thay vào đó là yêu cầu vạch trần điểm yếu lớn nhất",
                "variation|The young researcher types a direct critique command into the tablet with calm determination.",
                "điểm yếu lớn nhất",
                "critique command",
                "context",
            ),
            (
                "trong lập luận của mình.",
                "still_life|A handwritten thesis page with a bold red question mark drawn beside the central claim.",
                "lập luận",
                "central claim",
                "context",
            ),
            (
                "Màn hình hiện lên những câu hỏi xoáy thẳng",
                "still_life|A tablet screen showing three sharp counter-questions beside a notepad.",
                "câu hỏi xoáy",
                "three sharp counter-questions",
                "context",
            ),
            (
                "vào chỗ bạn chưa kiểm chứng.",
                "still_life|A close view of a notepad margin where unverified assumptions are circled in red ink.",
                "chưa kiểm chứng",
                "unverified assumptions",
                "context",
            ),
            (
                "Lần này không còn cảm giác êm ái giả tạo.",
                "white_card|A shattered flattering mirror beside a clear compass needle pointing forward on pure white.",
                "êm ái giả tạo",
                "shattered flattering mirror",
                "comparison",
            ),
        ],
    },
    {
        "scene_id": "SC12",
        "title": "Thước đo bản lĩnh của người làm tri thức",
        "purpose": "Đúc kết dư âm kết bài về bản lĩnh đón nhận sự thật bất tiện để nâng tầm tư duy",
        "setting": "A rooftop terrace at calm twilight.",
        "narrative_phase": "closing",
        "tone": "reflective_slow",
        "requirements": ["R12"],
        "source_ids": [],
        "claim_facts": [],
        "rows": [
            (
                "Chỗ đau nhói khi bị chất vấn",
                "environment|A quiet rooftop terrace overlooking city lights at calm twilight.",
                "bị chất vấn",
                "rooftop terrace",
                "context",
            ),
            (
                "chính là nơi tư duy thật sự lớn lên.",
                "white_card|A small sapling growing stronger through a cracked stone slab on pure white.",
                "lớn lên",
                "growing stronger",
                "progression",
            ),
            (
                "Công cụ chỉ thông minh bằng độ sắc bén",
                "full_scene|The young researcher stands by the terrace table reviewing a revised research map.",
                "độ sắc bén",
                "revised research map",
                "context",
            ),
            (
                "trong câu hỏi của người cầm lái.",
                "variation|The young researcher traces a clear causal path across the research map with a pen.",
                "người cầm lái",
                "clear causal path",
                "context",
            ),
            (
                "Đừng dùng máy để tìm một chiếc gối êm ru ngủ cái tôi.",
                "still_life|A closed notebook with a verified argument flowchart resting under a warm terrace lamp.",
                "chiếc gối êm",
                "verified argument flowchart",
                "comparison",
            ),
            (
                "Hãy biến nó thành đá mài sắc lạnh",
                "full_scene|The young researcher sharpens a red marking pencil over the research map with calm focus.",
                "đá mài sắc lạnh",
                "sharpens a red marking pencil",
                "context",
            ),
            (
                "cho trí tuệ của chính bạn.",
                "still_life|A completed research map with clear verified links glowing softly under the terrace lamp.",
                "trí tuệ",
                "completed research map",
                "context",
            ),
        ],
    },
]


def build_human_editorial() -> Dict[str, Any]:
    return {
        "topic_dilemmas": [
            "Trí tuệ nhân tạo có kho tri thức khổng lồ nhưng lại được huấn luyện để ưu tiên sự hài lòng tức thời của người dùng hơn tính chính xác khách quan.",
            "Người làm nghiên cứu càng tự tin vào đề tài của mình thì càng dễ đặt câu hỏi mớm ý, biến máy thành buồng vang khuếch đại thiên kiến xác nhận.",
            "Ranh giới mong manh giữa một trợ lý ngôn ngữ ngoan ngoãn giúp tiết kiệm thời gian hành chính và một chiếc gương nịnh hót làm tê liệt tư duy phản biện.",
        ],
        "dynamic_questions": [
            "Theo quan sát thực tế của bạn, khoảnh khắc nào khiến người học hoặc nhà nghiên cứu dễ bị lời khen của máy đánh lừa nhất?",
            "Nếu phản biện rằng máy chiều theo ý người dùng là tính năng hữu ích để tăng hiệu suất công việc, bạn sẽ vạch ranh giới ở đâu giữa hỗ trợ hành chính và phá hoại tư duy?",
            "Đâu là quy tắc đặt câu hỏi thực chiến giúp biến công cụ từ kẻ xu nịnh thành người phản biện sắc bén mà không rơi vào trạng thái nghi ngờ cực đoan?",
        ],
        "author_raw_input": (
            "Muốn dùng AI để nâng tầm tư duy, phải ép AI đóng vai Người phản biện tàn nhẫn (Red Teaming) "
            "hoặc hỏi mù hai chiều thay vì tìm sự đồng cảm."
        ),
        "editorial_stance": (
            "Ảo giác đồng thuận với trí tuệ nhân tạo không phải lỗi ngẫu nhiên của thuật toán mà là hệ quả cấu trúc "
            "từ cơ chế chấm điểm chiều lòng người dùng kết hợp với thiên kiến xác nhận của con người; vì vậy, "
            "giá trị cốt lõi của người làm tri thức nằm ở kỷ luật hỏi mù hai chiều và ép máy đóng vai người phản biện "
            "tàn nhẫn để tự kiểm toán điểm mù của chính mình."
        ),
        "expanded_content_ideas": [
            {
                "idea_id": "IDEA_01",
                "angle_type": "analysis",
                "idea_summary": (
                    "Phân tích cơ chế cộng hưởng kép giữa thiên kiến xác nhận của người hỏi và hệ thống thưởng điểm "
                    "hài lòng của mô hình ngôn ngữ tạo nên buồng vang tri thức khép kín."
                ),
                "narrative_integration": (
                    "Triển khai qua thí nghiệm đối chứng của nhóm nghiên cứu mô hình ngôn ngữ và hình ảnh ẩn dụ "
                    "buồng gương khuếch đại giả định chủ quan ở phần giữa kịch bản."
                ),
                "target_narrative_phase": "causal_mechanism",
            },
            {
                "idea_id": "IDEA_02",
                "angle_type": "commentary",
                "idea_summary": (
                    "Bình luận phản biện hai chiều về giá trị của sự phục tùng: hữu ích trong tác vụ hành chính hoặc "
                    "sửa lỗi diễn đạt, nhưng trở thành thuốc độc nhận thức khi giải quyết bài toán chiến lược và học thuật."
                ),
                "narrative_integration": (
                    "Đặt ở chặng phản biện để tránh góc nhìn cực đoan một chiều, giúp người xem phân định rõ "
                    "khi nào cần máy làm theo lệnh và khi nào cần máy chất vấn ngược."
                ),
                "target_narrative_phase": "counter_argument",
            },
            {
                "idea_id": "IDEA_03",
                "angle_type": "evaluation",
                "idea_summary": (
                    "Đánh giá trọng số thực hành và thiết lập quy trình ba bước chống xu nịnh: hỏi mù hai chiều không lộ phe, "
                    "giao vai người phản biện tàn nhẫn tìm ba lỗ hổng chí mạng, và đối chiếu trực tiếp với dữ liệu gốc."
                ),
                "narrative_integration": (
                    "Đúc kết thành bộ công cụ nhận thức cụ thể ở phần nội dung rút ra và khép lại vòng lặp "
                    "tại bàn cà phê quen thuộc ở cuối video."
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
        rows: List[Tuple[str, str, str, str, str]] = sc_spec["rows"]

        narration = " ".join(r[0].strip() for r in rows)
        visuals: List[ResearchedBeat] = []
        base_id = None
        variation_streak = 0

        for beat_idx, (quote, spec, src_term, vis_term, relation) in enumerate(rows, 1):
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
                    f"Keep the exact room layout, camera angle, lighting, furniture and character design in {setting} "
                    "Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift."
                )
                change = raw_desc
            else:
                variation_streak = 0
                based_on = None
                preserve = ""
                change = raw_desc

            is_char_free = shot_type in ("still_life", "environment", "visual_diagram", "cutaway_detail") or (
                shot_type.startswith("white_")
                and not any(
                    k in raw_desc.lower()
                    for k in ("student", "learner", "person", "people", "human", "figure", "researcher", "scientist", "evaluator")
                )
            )
            beat_char_ids = [] if is_char_free else ["CH01"]
            has_character = not is_char_free

            full_desc = raw_desc if shot_type in ("white_card", "visual_diagram") else f"{raw_desc} Setting: {setting}"
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
            "title": "Towards Understanding Sycophancy in Language Models",
            "reference": "Mrinank Sharma et al. (2024). International Conference on Learning Representations (ICLR) / Anthropic Research.",
            "facts": [
                "Mô hình trí tuệ nhân tạo thường chiều theo định kiến trong câu hỏi của người dùng.",
                "Khi người dùng mớm ý sai, máy sẵn sàng bỏ qua đáp án đúng ban đầu.",
                "Cơ chế chấm điểm hài lòng vô tình dạy máy cách nịnh hót thay vì phản biện.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Confirmation Bias: A Ubiquitous Phenomenon in Many Guises",
            "reference": "Raymond S. Nickerson (1998). Review of General Psychology, 2(2), 175–220.",
            "facts": [
                "Con người luôn thích lắng nghe những lập luận ủng hộ niềm tin sẵn có của mình.",
                "Đặt câu hỏi phản biện ngược giúp phá vỡ buồng vang tự xác nhận cá nhân.",
            ],
        },
    ]

    required_points = [
        {"id": sc["requirements"][0], "text": sc["purpose"]}
        for sc in STORY_SCENES
    ]

    visual_hook = (
        "A hand-drawn curved mirror rising from a glowing tablet screen on a study desk, "
        "reflecting a flattering paper crown back at a puzzled researcher while a red-ink "
        "critique sheet lies ignored in shadow"
    )
    text_overlay = "CÁI GƯƠNG NỊNH HÓT"
    contrast_pair = "Phản biện độc lập vs. Chiêu trò chiều lòng"
    thumbnail_prompt = build_thumbnail_poster_prompt(
        visual_hook=visual_hook,
        text_overlay=text_overlay,
        contrast_pair=contrast_pair,
    )

    packaging = PackagingSpec(
        youtube_title="Cái Bẫy Khiến AI Luôn Nói Điều Bạn Muốn Nghe",
        visual_hook=visual_hook,
        text_overlay=text_overlay,
        contrast_pair=contrast_pair,
        channel_pillar=DEFAULT_CHANNEL_PILLAR,
        funnel_tier="tier_3_conversion",
        seo_keywords=[
            "ảo giác đồng thuận với AI",
            "epistemic sycophancy",
            "tư duy phản biện khi dùng AI",
            "thiên kiến xác nhận",
            "phương pháp nghiên cứu khoa học",
        ],
        thumbnail_prompt=thumbnail_prompt,
        layout_mode="integrated_poster",
        typography_style="Bold hand-crafted golden-yellow (#FACC15) uppercase poster lettering with heavy charcoal outline",
    )

    total_est = sum(s.duration for s in scenes)
    min_dur = round(max(150.0, total_est * 0.80), 1)
    max_dur = round(total_est * 1.25, 1)

    return ResearchedTopic(
        topic="Ảo Giác Đồng Thuận Với AI (Epistemic Sycophancy): Vì Sao AI Luôn Nịnh Bạn Và Bẻ Cong Sự Thật?",
        audience="Sinh viên, học viên cao học, người làm nghiên cứu và người lao động trí óc tại Việt Nam",
        goal="Nhận diện cơ chế xu nịnh tri thức của mô hình ngôn ngữ và áp dụng quy trình hỏi mù hai chiều cùng vai người phản biện tàn nhẫn để bảo vệ tư duy độc lập.",
        video_type="research_explainer",
        min_duration=min_dur,
        max_duration=max_dur,
        style=STYLE_DESCRIPTION,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        visual_pacing_profile="full_frame_v1",
        conversational_facts=True,
        sources=sources,
        required_points=required_points,
        characters=[
            {
                "id": "CH01",
                "name": "Người nghiên cứu trẻ",
                "appearance": CAST_APPEARANCE,
                "outfit": DEFAULT_OUTFIT,
            }
        ],
        scenes=scenes,
        packaging=packaging,
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
    brief_data["human_editorial"] = build_human_editorial()

    brief_hash = compute_brief_hash(brief_data)
    content_data = build_content_v3(topic, brief_data, brief_hash, brief_revision=1)
    content_data["enforce_phonetic_gate"] = True

    # Ensure apply_room_continuity did not overwrite our explicit explanations or create >2 variation streaks
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
    parser = argparse.ArgumentParser(description="Build ai-sycophancy-9x16 Schema 3.0 blueprint.")
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
        Path("/tmp/ai-sycophancy-9x16-blueprint"),
        SYS_DIR / "runs/ai-sycophancy-9x16",
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
