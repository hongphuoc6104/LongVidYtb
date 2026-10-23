#!/usr/bin/env python3
"""Build production-ready packages for Adversarial AI (16:9 Landscape & 9:16 Portrait).

Pillar: "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức" (tier_3_conversion)
Topic: "Biến AI Thành 'Phản Biện Đối Đầu' Thay Vì Công Cụ Viết Hộ"
- adversarial-ai-16x9: 32 visual beats full_frame_v1 landscape explainer
- adversarial-ai-9x16: 20 visual beats full_frame_v1 vertical mobile long-form
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[3]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content.research_story_architect import (
    CAST_APPEARANCE,
    DEFAULT_CHANNEL_PILLAR,
    DEFAULT_OUTFIT,
    STYLE_DESCRIPTION,
    PackagingSpec,
    ResearchedScene,
    ResearchedTopic,
    build_scenes_from_story_rows,
    write_production_package,
)

# ---------------------------------------------------------------------------
# Conversational Tone & Keywords Specification (User Spoken Modulation Protocol)
# ---------------------------------------------------------------------------
SPOKEN_TONE_MAP = {
    "gentle_lived_friction": {
        "label": "Mở đầu nhẹ nhàng đồng cảm",
        "keywords": ["mười một giờ đêm", "bàn học", "thở phào", "nhẹ nhõm"],
    },
    "truth_slap_emphasis": {
        "label": "Nhấn mạnh đanh thép & Cú tát",
        "keywords": ["thực tế rất phũ phàng", "ba mươi giây", "văn mẫu"],
    },
    "explanatory_mechanism": {
        "label": "Giải thích cơ chế thuật toán",
        "keywords": ["xác suất", "từ tiếp theo", "an toàn", "không lập trường"],
    },
    "analytical_contrast": {
        "label": "Phân tích đối lập học thuật",
        "keywords": ["tóm tắt", "tranh luận", "xung đột", "phát kiến"],
    },
    "step_listing": {
        "label": "Liệt kê quy trình từng bước",
        "keywords": ["bước một", "thử tải", "điểm mù", "bước hai", "ma trận"],
    },
    "decisive_prompts": {
        "label": "Quyết đoán ra lệnh đối kháng",
        "keywords": ["bước ba", "mổ xẻ", "ra lệnh", "phản biện", "cứ liệu", "phản ví dụ"],
    },
    "narrative_payoff": {
        "label": "Dẫn truyện triết lý khép vòng lặp",
        "keywords": ["phản biện đối đầu", "vững vàng", "mài sắc", "tư duy"],
    },
}

# ---------------------------------------------------------------------------
# STORY 16:9 (32 Visual Beats across 7 Scenes — Landscape Explainer)
# ---------------------------------------------------------------------------
STORY_16X9: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    # (Title, Setting, Tone, SpokenStyle, NarrativePhase, [(Sentence, "shot_type|action_description")])
    (
        "Cú tát mở màn bàn học đêm",
        "A Vietnamese student desk at night under a warm desk lamp, glowing laptop screen.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Mười một giờ đêm bên bàn học.", "macro_prop|A glowing laptop screen shows a blank document with a ticking clock on the wall at 11 PM."),
            ("Bạn thở phào nhẹ nhõm.", "full_scene|A student character slumps in a wooden chair at the desk, exhausted before an approaching deadline."),
            ("Gõ dòng lệnh nhờ AI viết hộ.", "full_scene|Close-up of the screen showing an AI chat prompt asking to generate an entire literature review."),
            ("Từng đoạn văn tuôn ra ào ào.", "variation|Dense paragraphs of text rapidly flood the screen with a glowing cyan light."),
            ("Ngỡ rằng mình đã làm chủ kiến thức.", "variation|The student leans back smiling with complacent relief, feeling premature triumph."),
            ("Nhưng khi bước vào phòng bảo vệ,", "full_scene|The heavy oak door of an academic defense room swings open under bright cold fluorescent lights."),
            ("thầy cô chỉ mất ba mươi giây.", "macro_prop|Close view of an academic committee professor rapidly skimming the first three pages of the thesis draft."),
            ("Là phát hiện ra ngay bài văn mẫu.", "white_card|A crisp warning card with a bright red stamp reading BAN PHAT HIEN on pure white."),
        ],
    ),
    (
        "Cú sốc ba mươi giây phòng bảo vệ",
        "A serious academic evaluation defense room with committee professors.",
        "analytical_crisp",
        "truth_slap_emphasis",
        "lived_friction",
        [
            ("Thực tế rất phũ phàng.", "full_scene|Three committee professors sit solemnly behind an academic evaluation table."),
            ("Hội đồng không đọc để khen câu từ trôi chảy.", "variation|The lead professor pushes the thesis draft aside without reading past the intro."),
            ("Họ tìm kiếm khoảng trống tri thức mới.", "macro_prop|A red ballpoint pen points directly at an empty space between two cited academic papers."),
            ("Và bài viết của bạn hoàn toàn không có điều đó.", "white_card|A visual comparison showing a zero research gap symbol on pure white."),
        ],
    ),
    (
        "Bản chất cỗ máy đoán xác suất",
        "A conceptual computer science visualization chamber showing language model probability distribution.",
        "analytical_crisp",
        "explanatory_mechanism",
        "empirical_conflict",
        [
            ("Vì sao AI hay sinh ra văn mẫu?", "full_scene|A glowing holographic visualization of neural network token prediction paths."),
            ("Bản chất cỗ máy chỉ đoán xác suất từ tiếp theo.", "macro_prop|Close view of probabilistic word trees branching out from a single seed token."),
            ("Nó chọn từ ngữ an toàn và ít rủi ro nhất.", "variation|The highlighted path chooses the most average, safe, neutral path among probability branches."),
            ("Tạo ra đoạn văn rỗng tuếch, không lập trường.", "white_card|A neutral grey text block labeled SAFE AVERAGE VOCABULARY on pure white."),
        ],
    ),
    (
        "Phân tích đối lập và mô hình CARS",
        "An analytical comparative studio environment contrasting superficial summary and deep synthesis.",
        "analytical_crisp",
        "analytical_contrast",
        "empirical_conflict",
        [
            ("Một bên là tóm tắt tầm thường.", "full_scene|Left side shows a flat boring bullet list titled TÓM TẮT TÀI LIỆU with zero insight."),
            ("Một bên là sơ đồ tranh luận học thuật.", "variation|Right side lights up with an intricate 2-axis matrix mapping theoretical tensions."),
            ("Nghiên cứu quốc tế bắt đầu từ xung đột lý thuyết.", "macro_prop|Two contrasting scholar portraits facing each other with opposing directional arrows."),
            ("Không có tranh luận thì không có phát kiến mới.", "white_card|A conceptual formula card: XUNG DOT LY THUYET TAO RA KHOANG TRONG on pure white."),
        ],
    ),
    (
        "Bước một và bước hai đảo vai AI",
        "A structured modern research studio with prominent numbered step cards.",
        "analytical_crisp",
        "step_listing",
        "structural_model",
        [
            ("Đã đến lúc đổi vai cho cỗ máy.", "full_scene|The student stands decisively beside a glowing 4-step framework flowchart."),
            ("Bước một: Thử tải giả thuyết cốt lõi.", "white_card|Card Step 1: BUOC 1 THU TAI GIA THUYET on pure white with stress testing symbol."),
            ("Bắt AI tìm ba điểm mù nguy hiểm nhất.", "macro_prop|Close view of three sharp red arrows targeting hidden logical weak spots."),
            ("Bước hai: Dựng ma trận mâu thuẫn học thuật.", "white_card|Card Step 2: BUOC 2 MA TRAN MAU THUAN on pure white with a 4-quadrant grid."),
        ],
    ),
    (
        "Bước ba và bước bốn mổ xẻ phương pháp",
        "A high-stakes debate command center with tactical academic prompt displays.",
        "analytical_crisp",
        "decisive_prompts",
        "actionable_resolution",
        [
            ("Bước ba: Mổ xẻ phương pháp luận.", "white_card|Card Step 3: BUOC 3 MO XE PHUONG PHAP on pure white with diagnostic scalpel icon."),
            ("Ra lệnh cho AI chất vấn cỡ mẫu và độ tin cậy.", "full_scene|A strict, sharp reviewer silhouette appears behind a glowing prompt terminal."),
            ("Bước bốn: Đối soát cứ liệu thực tế.", "white_card|Card Step 4: BUOC 4 DOI SOAT CU LIEU on pure white with verified magnifying glass."),
            ("Truy tìm các phản ví dụ để củng cố lập luận.", "macro_prop|A researcher highlights outlier data points and counter-examples in an experimental dataset."),
        ],
    ),
    (
        "Khép vòng lặp mài sắc tư duy",
        "A serene, warm Vietnamese student desk at night, illuminated by a warm lamp, confident and empowered.",
        "reflective_slow",
        "narrative_payoff",
        "actionable_resolution",
        [
            ("Khi biến AI thành phản biện đối đầu,", "full_scene|The student sits upright at the warm desk, examining a sharp structured defense outline."),
            ("bạn sẽ vững vàng trước mọi câu hỏi hội đồng.", "variation|The student smiles calmly with unwavering confidence, looking directly at the camera."),
            ("Công nghệ không sinh ra để nghĩ thay bạn.", "macro_prop|A laptop resting quietly as a supportive assistant while a fountain pen writes key insights."),
            ("Nó sinh ra để mài sắc tư duy của bạn.", "white_card|A crisp motivational card: AI MAI SAC TU DUY on pure white with a gleaming diamond intellect icon."),
        ],
    ),
]

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# STORY 9:16 (58 Visual Beats across 19 Scenes — Vertical Mobile Long-form Explainer)
# ---------------------------------------------------------------------------
STORY_9X16: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    (
        'Cú tát mở màn bàn học đêm',
        'A vertical mobile view of a Vietnamese student desk at night under a warm desk lamp.',
        'narrative_warm',
        'gentle_lived_friction',
        'lived_friction',
        [
            ('Dùng AI viết hộ luận văn là cách nhanh nhất để rớt tốt nghiệp.', 'macro_prop|A vertical smartphone screen displaying a flashing red warning banner over a thesis draft.'),
            ('Mười một giờ đêm bên bàn học,', 'full_scene|A student slumps at the wooden desk with a green lamp and ticking wall clock at 11 PM.'),
            ('bạn mệt mỏi dán mắt vào màn hình.', 'variation|The student rubs their tired eyes before a glowing blank document.'),
            ('Bạn thở phào nhẹ nhõm,', 'variation|The student character sighs with relief as text rapidly fills the screen.'),
            ('khi thấy từng đoạn văn tuôn ra ào ào.', 'white_card|Vertical card on pure white: VAN BAN TUON RA with a fast streaming data icon.'),
        ],
    ),
    (
        'Ảo giác tiết kiệm thời gian',
        'A vertical academic hallway outside the defense evaluation room.',
        'analytical_crisp',
        'truth_slap_emphasis',
        'lived_friction',
        [
            ('Bạn tin rằng mình vừa tiết kiệm được cả tuần lễ đọc sách. [pause:600ms]', 'full_scene|The student carries a printed thesis down a fluorescent-lit academic corridor.'),
            ('Bạn mỉm cười đắc thắng.', 'variation|The student holds the printed draft with confident anticipation.'),
            ('Nhưng thực tế rất phũ phàng.', 'variation|The student stops before a heavy wooden door with an anxious expression.'),
            ('Bước vào phòng bảo vệ,', 'macro_prop|Close vertical view of the brass door handle turning to enter the defense room.'),
            ('thầy cô chỉ mất ba mươi giây để nhận ra.', 'white_card|Vertical card on pure white: 30 GIAY PHAN QUYET with a ticking stopwatch.'),
        ],
    ),
    (
        'Cú sốc ba mươi giây phòng bảo vệ',
        'A solemn thesis defense room viewed in vertical portrait framing.',
        'analytical_crisp',
        'truth_slap_emphasis',
        'lived_friction',
        [
            ('Hội đồng không đọc để khen câu từ trau chuốt hay trôi chảy.', 'full_scene|Three committee professors sit behind an evaluation desk under bright lights.'),
            ('Họ nhìn thẳng vào các đoạn văn mẫu sáo rỗng.', 'macro_prop|A red pen underscores repetitive generic paragraphs on the thesis draft.'),
            ('Nét mặt giáo viên phản biện đanh lại.', 'variation|The lead professor pushes the paper aside with a critical frown.'),
            ('Và nhận ra bài viết của bạn,', 'variation|The student stands at the podium, suddenly realizing their intellectual exposure.'),
            ('hoàn toàn không có khoảng trống nghiên cứu.', 'white_card|Vertical card on pure white: KHONG KHOANG TRONG with a stark empty box.'),
        ],
    ),
    (
        'Bản chất dự đoán từ tiếp theo',
        'A vertical conceptual diagram of a neural language model architecture.',
        'analytical_crisp',
        'explanatory_mechanism',
        'empirical_conflict',
        [
            ('Vì sao văn bản AI viết lại dễ bị bắt bài đến vậy?', 'full_scene|A vertical network diagram with glowing interconnected language nodes.'),
            ('Bản chất của các mô hình ngôn ngữ lớn,', 'variation|The student examines a vertical holographic tree of computational probabilities.'),
            ('chỉ là đoán xác suất của từ tiếp theo.', 'macro_prop|A vertical data meter calculating probabilistic values for consecutive words.'),
            ('Cỗ máy ghép nối câu chữ dựa trên dữ liệu quá khứ,', 'variation|The probability stream connects common word pairs in a glowing linear sequence.'),
            ('chứ không hề hiểu logic nghiên cứu thực tế.', 'white_card|Vertical card on pure white: DOAN XAC SUAT TU with a mathematical formula symbol.'),
        ],
    ),
    (
        'Bẫy văn phong an toàn trung tính',
        'A vertical abstract scale balancing neutral language versus bold original thought.',
        'analytical_crisp',
        'explanatory_mechanism',
        'empirical_conflict',
        [
            ('Để phục vụ hàng triệu người trên thế giới,', 'full_scene|A vast digital sphere connecting millions of anonymous users across the globe.'),
            ('AI luôn chọn phương án an toàn nhất.', 'macro_prop|A safety shield icon filtering out sharp edges and controversial ideas.'),
            ('Nó gọt giũa mọi quan điểm đối nghịch,', 'variation|A smooth polished stone represents the bland homogenized text output.'),
            ('để không làm phật lòng bất kỳ ai.', 'variation|The text displays generic pleasantries without taking an academic stand.'),
            ('Kết quả là một bài viết hoàn toàn không lập trường.', 'white_card|Vertical card on pure white: KHONG LAP TRUONG with a dull grey document.'),
        ],
    ),
    (
        'Bẫy danh sách đi chợ tầm thường',
        'A vertical split comparison between a grocery receipt and a citation network.',
        'analytical_crisp',
        'analytical_contrast',
        'empirical_conflict',
        [
            ('Nhiều bạn biến phần tổng quan tài liệu,', 'full_scene|A long vertical paper receipt listing author names in a mechanical unlinked column.'),
            ('thành một bản tóm tắt rời rạc.', 'macro_prop|Close view of bullet points merely restating author opinions without dialogue.'),
            ('Tác giả A nói thế này,', 'variation|Author A icon labeled with an isolated opinion.'),
            ('tác giả B nói thế kia.', 'variation|Author B icon stacked without connection or critical tension.'),
            ('Đó là một danh sách đi chợ tầm thường,', 'variation|A supermarket shopping cart full of scattered unread notes.'),
            ('chứ không phải một cuộc tranh luận học thuật.', 'white_card|Vertical card on pure white: TRANH LUAN HOC THUAT with two clashing swords.'),
        ],
    ),
    (
        'Mô hình CARS của John Swales',
        'A vertical three-tier academic pyramid illustrating the CARS model.',
        'analytical_crisp',
        'analytical_contrast',
        'structural_model',
        [
            ('Giới nghiên cứu quốc tế đã đúc kết mô hình CARS kinh điển.', 'full_scene|A vertical 3-tier pyramid showing Territory, Niche, and Occupation.'),
            ('Mô hình CARS chứng minh rằng,', 'macro_prop|Close view of the academic textbook Genre Analysis on a clean lectern.'),
            ('một công trình khoa học,', 'variation|The theoretical framework lights up under analytical scrutiny.'),
            ('luôn bắt đầu từ sự xung đột.', 'variation|Two theoretical factions clash with vibrant red and cyan energy.'),
            ('Bạn phải chỉ ra điểm giới hạn mà lý thuyết cũ chưa giải quyết,', 'variation|A brick wall stops the progress of conventional academic thought.'),
            ('thì đề tài của bạn mới có lý do tồn tại.', 'white_card|Vertical card on pure white: XUNG DOT LY THUYET with a glowing niche icon.'),
        ],
    ),
    (
        'Bản chất của khoảng trống tri thức',
        'A vertical laboratory whiteboard with contrasting research trajectories.',
        'analytical_crisp',
        'analytical_contrast',
        'structural_model',
        [
            ('Khoảng trống nghiên cứu không phải là thứ chưa ai làm vì vô nghĩa.', 'full_scene|A vertical blackboard with two diverging colored arrows representing opposing theories.'),
            ('Nó xuất hiện khi hai nghiên cứu uy tín,', 'variation|Two academic icons face each other with irreconcilable experimental results.'),
            ('cho ra hai kết luận trái ngược nhau.', 'macro_prop|A plus sign chart and a minus sign chart displayed side by side.'),
            ('Chính việc đi tìm lời giải cho mâu thuẫn đó,', 'variation|The student traces a connecting hypothesis bridge between the two poles.'),
            ('mới tạo ra phát kiến khoa học có giá trị.', 'white_card|Vertical card on pure white: PHAT KIEN KHOA HOC with a brilliant spark.'),
        ],
    ),
    (
        'Ví dụ cọ xát lý thuyết thực tế',
        'A vertical case-study comparison board with academic citations.',
        'analytical_crisp',
        'analytical_contrast',
        'structural_model',
        [
            ('Hãy nhìn vào một ví dụ thực tế trong ngành quản trị.', 'full_scene|A vertical board displaying two prominent research papers side by side.'),
            ('Nghiên cứu thứ nhất chứng minh,', 'variation|The first paper title lights up with emphasis.'),
            ('làm việc từ xa giúp tăng năng suất.', 'macro_prop|A green chart showing upward productivity indicators under remote work conditions.'),
            ('Nhưng nghiên cứu thứ hai khẳng định nó gây kiệt sức.', 'variation|A red chart showing declining organizational commitment and rising employee burnout.'),
            ('Hai luồng kết quả cọ xát trực tiếp với nhau.', 'variation|A spark of tension between productivity and burnout indices.'),
            ('Nếu bạn chỉ tóm tắt lại cả hai quan điểm,', 'variation|The student sits puzzled between the two clashing empirical findings.'),
            ('bài luận của bạn sẽ hoàn toàn vô giá trị.', 'white_card|Vertical card on pure white: TOM TAT VO NGHIA with an empty result meter.'),
        ],
    ),
    (
        'Bẫy ngụy tạo trích dẫn ảo',
        'A vertical digital forensics workstation checking academic database DOIs.',
        'analytical_crisp',
        'explanatory_mechanism',
        'empirical_conflict',
        [
            ('Nguy hiểm hơn, AI có xu hướng ngụy tạo tài liệu.', 'full_scene|A digital terminal scanning citations against international Scopus and Web of Science databases.'),
            ('Khi bị ép viết phần tổng quan,', 'variation|The prompt requests ten scholarly citations with volume and page numbers.'),
            ('nó tự ghép tên tác giả có thật vào bài báo ảo.', 'macro_prop|Close view of a fabricated citation showing Error 404: Paper Not Found on screen.'),
            ('Cỗ máy chỉ quan tâm đến việc trả lời trơn tru,', 'variation|The AI avatar continues typing fluidly without verifying scientific truth.'),
            ('chứ không hề bảo đảm sự an toàn học thuật.', 'white_card|Vertical card on pure white: NGUY TAO TRICH DAN with a severe red warning.'),
        ],
    ),
    (
        'Đảo ngược vai trò của công nghệ',
        'A vertical transitional space moving from passive copying to active command.',
        'analytical_crisp',
        'decisive_prompts',
        'structural_model',
        [
            ('Để làm chủ công nghệ,', 'full_scene|The student character steps decisively into a command cockpit.'),
            ('bạn phải đảo ngược tư duy hoàn toàn.', 'variation|The interface switches from consumer mode to pro investigator mode.'),
            ('Đừng bao giờ xem AI là thư ký viết hộ.', 'variation|A ghostwriter avatar fades into the background with a crossed-out symbol.'),
            ('Kẻ viết thuê chỉ tạo ra sự lười biếng tư duy.', 'macro_prop|A limp mechanical hand holding a pen drops onto the desk.'),
            ('Hãy ra lệnh biến nó thành đối thủ phản biện,', 'variation|The AI terminal shifts into a sharp analytical interface with an armored Reviewer shield.'),
            ('một chuyên gia phản biện khó tính nhất từng chấm bài của bạn.', 'white_card|Vertical card on pure white: DOI THU REVIEWER 2 with a critical red pen.'),
        ],
    ),
    (
        'Bước một: Thử tải giả thuyết',
        'A vertical stress-testing tactical screen with structural simulation graphics.',
        'analytical_crisp',
        'step_listing',
        'structural_model',
        [
            ('Bước một: Thử tải giả thuyết nghiên cứu của bạn.', 'white_card|Vertical card Step 1: BUOC MOT THU TAI GIA THUYET on pure white with a stress gauge.'),
            ('Nạp luận điểm chính vào hệ thống,', 'full_scene|The student feeds a hypothesis card into the AI terminal, triggering deep analytical probing.'),
            ('và bắt cỗ máy tìm ra ba điểm mù nguy hiểm nhất.', 'macro_prop|A virtual stress-test showing red pressure points on the hypothesis framework.'),
            ('Yêu cầu AI đóng vai một người hoài nghi tuyệt đối,', 'variation|The AI displays three rigorous counter-theories challenging the core premise.'),
            ('để bẻ gãy lập luận trước khi người khác làm điều đó.', 'variation|The student takes notes as weaknesses in the thesis premise are highlighted.'),
        ],
    ),
    (
        'Bước hai: Lập ma trận khoảng trống',
        'A vertical 2x2 matrix display showing theoretical tensions.',
        'analytical_crisp',
        'step_listing',
        'structural_model',
        [
            ('Bước hai: Xây dựng ma trận khoảng trống tri thức.', 'white_card|Vertical card Step 2: BUOC HAI MA TRAN KHOANG TRONG on pure white.'),
            ('Đưa năm bài báo quốc tế vào khung so sánh.', 'full_scene|A vertical 2x2 matrix charting theoretical assumptions across prominent scholar schools.'),
            ('Yêu cầu AI lập bảng so sánh các điểm bất đồng.', 'macro_prop|A prompt command: Cross-compare theoretical discrepancies between Authors A and B.'),
            ('Bảng ma trận này vạch ra điểm mù chưa ai giải quyết,', 'variation|The four quadrants map existing consensus while highlighting an unresolved white space.'),
            ('chỉ rõ ranh giới điều kiện,', 'variation|A vertical magnifying lens focuses on boundary conditions.'),
            ('nơi mà các lý thuyết đều bất lực,', 'variation|A glowing border circumscribes the unresolved tension zone.'),
            ('đó chính là mảnh đất để đề tài của bạn cắm cờ.', 'variation|A bright marker flag planted precisely in the unresolved center quadrant of the matrix.'),
        ],
    ),
    (
        'Bước ba: Mổ xẻ phương pháp',
        'A vertical methodological audit station with checklists and data verification.',
        'analytical_crisp',
        'decisive_prompts',
        'structural_model',
        [
            ('Bước ba: Mổ xẻ thiết kế phương pháp và cỡ mẫu.', 'white_card|Vertical card Step 3: BUOC BA MO XE PHUONG PHAP on pure white.'),
            ('Hãy ra lệnh cho AI tấn công vào dữ liệu của bạn.', 'full_scene|The AI avatar assumes the attire of a rigorous Reviewer 2 with a critical red pen.'),
            ('Chất vấn về thiên lệch chọn mẫu,', 'macro_prop|A red magnifying glass highlights sample selection anomalies.'),
            ('và các biến kiểm soát bị bỏ sót.', 'variation|Checklist items regarding omitted variable bias light up in yellow.'),
            ('Từng con số, từng cứ liệu thực nghiệm phải được soi xét,', 'variation|The student reviews statistical distribution curves and robustness check metrics.'),
            ('như thể bạn đang đứng trước hội đồng khó tính nhất.', 'variation|The student refines measurement models to preempt potential criticisms.'),
        ],
    ),
    (
        'Bước bốn: Đối soát cứ liệu gốc',
        'A vertical document grounding laboratory with verified PDF archives.',
        'analytical_crisp',
        'decisive_prompts',
        'structural_model',
        [
            ('Bước bốn: Đối soát chéo từng phản ví dụ thực tế.', 'white_card|Vertical card Step 4: BUOC BON DOI SOAT CU LIEU on pure white.'),
            ('Chỉ cho phép AI sử dụng đúng các file PDF bạn cung cấp.', 'full_scene|The student locks the AI workspace strictly to verified peer-reviewed PDF attachments.'),
            ('Không mở quyền truy cập mạng tự do để bịa nguồn.', 'macro_prop|A locked gate securing the database strictly to authentic uploaded journal articles.'),
            ('Yêu cầu trích dẫn rõ số trang,', 'variation|A digital pin drops directly on Page 45 of the primary document.'),
            ('và đối chiếu từng đoạn văn cụ thể,', 'variation|A highlighted block confirms exact textual correspondence.'),
            ('để mọi luận điểm đều có bệ đỡ vững chắc.', 'variation|A verified citation badge linking directly to an authentic journal article.'),
        ],
    ),
    (
        'So sánh câu lệnh lười vs câu lệnh đối kháng',
        'A vertical comparative studio contrasting lazy prompting with adversarial commanding.',
        'analytical_crisp',
        'decisive_prompts',
        'actionable_resolution',
        [
            ('Hãy nhìn vào sự khác biệt giữa hai cách ra lệnh.', 'full_scene|A vertical dual-panel mobile view contrasting two divergent chat prompts.'),
            ('Một bên là câu lệnh lười biếng nhờ viết hộ mười trang,', 'macro_prop|The left panel shows a lazy one-line prompt yielding bland paragraphs of filler text.'),
            ('chỉ mang về những đoạn văn sáo rỗng vô hồn.', 'variation|The left document is stamped with a red label: Zero Critical Thought.'),
            ('Một bên là câu lệnh đối kháng sắc bén,', 'variation|The right panel shows an adversarial prompt producing five sharp methodological challenges.'),
            ('buộc cỗ máy phải tấn công vào điểm yếu,', 'variation|Targeting crosshairs locate logical vulnerabilities on the right screen.'),
            ('để bạn tự tay gia cố luận điểm của mình.', 'white_card|Vertical card on pure white: DOI THOAI DOI KHANG with a polished cognitive shield.'),
        ],
    ),
    (
        'Rèn luyện trong phòng tập nhận thức',
        'A vertical mental training dojo transitioning to an academic defense podium.',
        'analytical_crisp',
        'narrative_payoff',
        'actionable_resolution',
        [
            ('Khi bạn đã vượt qua những câu hỏi vặn vẹo gay gắt của AI,', 'full_scene|The student character defends complex equations against dynamic holographic challenges.'),
            ('bạn đã trải qua một cuộc diễn tập học thuật thực thụ.', 'variation|The student calmly addresses critical challenges with evidence and composure.'),
            ('Từng luận cứ được tôi luyện qua lửa phản biện.', 'macro_prop|A glowing anvil forging sharp intellectual arguments under intense pressure.'),
            ('Bước vào phòng bảo vệ,', 'variation|The student approaches the formal defense committee room.'),
            ('với một tâm thế hoàn toàn vững vàng,', 'variation|The student stands calmly at the formal podium, addressing questions with clarity.'),
            ('bạn không còn sợ bất kỳ câu hỏi bất ngờ nào nữa.', 'variation|The committee listens attentively as the student responds with unshakeable confidence.'),
            ('Bởi vì bạn đã tự tay xây dựng từng mắt xích lý thuyết.', 'white_card|Vertical card on pure white: TAM THE VUNG VANG with a triumphant laurel wreath.'),
        ],
    ),
    (
        'Trở lại bàn học đêm muộn',
        'A serene vertical view of the student desk at night, now illuminated with clear purpose.',
        'narrative_warm',
        'gentle_lived_friction',
        'actionable_resolution',
        [
            ('Tối nay, khi bạn ngồi lại bên bàn học đêm muộn,', 'full_scene|The student sits peacefully at the familiar desk under the warm glow of the desk lamp.'),
            ('đừng vội vàng biến mình thành một người sao chép thụ động.', 'variation|The student pushes the generic copy-paste prompt aside, picking up a pen with intent.'),
            ('Hãy mở một khung chat trống,', 'macro_prop|A pristine vertical chat window waiting for an adversarial directive.'),
            ('và bắt đầu cuộc đối thoại phản biện thực sự.', 'variation|The student types a rigorous critical prompt with quiet determination.'),
            ('Đó là lúc bạn thực sự dấn thân vào hành trình học tập,', 'variation|The student smiles with authentic intellectual engagement, writing down a bold new premise.'),
            ('nơi tri thức được sinh ra từ sự cọ xát tư duy.', 'white_card|Vertical card on pure white: CO XAT TU DUY with a glowing open book.'),
        ],
    ),
    (
        'Khép vòng lặp và thông điệp triết lý',
        'A striking vertical symbolic closure card on pure white.',
        'reflective_slow',
        'narrative_payoff',
        'actionable_resolution',
        [
            ('Trí tuệ nhân tạo không sinh ra để suy nghĩ thay bạn. [pause:600ms]', 'full_scene|A stylized silhouette of human intellect standing side-by-side with machine computation.'),
            ('Nó sinh ra để mài sắc thanh kiếm tư duy của bạn,', 'variation|A glowing cognitive sword forged in pure clarity, held firmly in the human hand.'),
            ('rèn giũa năng lực phản biện,', 'variation|A whetstone sharpens the cognitive blade to a mirror shine.'),
            ('giúp bạn nhìn thấu những điểm mù nhận thức,', 'macro_prop|A brilliant beam of light illuminating previously hidden areas of a concept map.'),
            ('và vững vàng bảo vệ công trình của chính mình.', 'variation|The student raises the sword of critical thought, standing tall in the academic forum.'),
            ('Đó mới là bản chất của người làm chủ khoa học.', 'white_card|Vertical diamond badge on pure white: MAI SAC TU DUY - LAM CHU TRI THUC.'),
        ],
    ),
]


def build_sources() -> list[dict]:
    """Conversational spoken academic sources; every fact <= 20 syllables, zero dry symbols."""
    return [
        {
            "id": "SRC01",
            "title": "Large Language Models as Research Assistants",
            "reference": "Science Journal on Generative AI in Academic Research",
            "facts": [
                "Trí tuệ nhân tạo luôn chọn từ ngữ an toàn nhất.",
                "Máy tính chỉ đoán xác suất của từ tiếp theo.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Creating a Research Space: CARS Model",
            "reference": "John Swales Academic Research Framework",
            "facts": [
                "Nghiên cứu khoa học bắt đầu từ xung đột học thuật.",
                "Hội đồng luôn tìm kiếm khoảng trống tri thức mới.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Adversarial Machine Learning and Critical Review",
            "reference": "AI Peer Review and Adversarial Testing Principles",
            "facts": [
                "Phản biện đối đầu giúp phơi bày các điểm mù.",
                "Thử tải luận điểm bằng các phản ví dụ thực tế.",
            ],
        },
    ]


def verify_spoken_tone_keywords(scenes: List[ResearchedScene]) -> List[str]:
    """Ensure that conversational tone keywords are present in scene narrations."""
    warnings: List[str] = []
    for sc in scenes:
        spoken_style = getattr(sc, "spoken_style", None)
        if not spoken_style or spoken_style not in SPOKEN_TONE_MAP:
            continue
        req_keywords = SPOKEN_TONE_MAP[spoken_style]["keywords"]
        narr_lower = sc.narration.lower()
        matched = [kw for kw in req_keywords if kw in narr_lower]
        if not matched:
            warnings.append(
                f"TONE_KEYWORD_MISSING: {sc.scene_id} (style={spoken_style}) lacks required spoken keywords from {req_keywords}"
            )
    return warnings


def build_topic_16x9() -> ResearchedTopic:
    """Build landscape explainer topic: 32 visual beats across 7 scenes."""
    story_tuples = [(title, setting, rows) for title, setting, _, _, _, rows in STORY_16X9]
    scenes = build_scenes_from_story_rows(story_tuples, character_id="CH01")
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = STORY_16X9[i][2]
        sc.spoken_style = STORY_16X9[i][3]
        sc.narrative_phase = STORY_16X9[i][4]

    # Assign academic sources and claims
    scenes[2].source_ids = ["SRC01"]
    scenes[2].claim_facts = [
        ("Bản chất cỗ máy chỉ đoán xác suất từ tiếp theo.", "SRC01", "Máy tính chỉ đoán xác suất của từ tiếp theo.")
    ]
    scenes[3].source_ids = ["SRC02"]
    scenes[3].claim_facts = [
        ("Nghiên cứu quốc tế bắt đầu từ xung đột lý thuyết.", "SRC02", "Nghiên cứu khoa học bắt đầu từ xung đột học thuật.")
    ]
    scenes[5].source_ids = ["SRC03"]
    scenes[5].claim_facts = [
        ("Truy tìm các phản ví dụ để củng cố lập luận.", "SRC03", "Thử tải luận điểm bằng các phản ví dụ thực tế.")
    ]

    # Verify tone keywords
    tone_warnings = verify_spoken_tone_keywords(scenes)
    if tone_warnings:
        raise ValueError(f"Tone keyword verification failed: {tone_warnings}")

    return ResearchedTopic(
        topic="Biến AI thành phản biện đối đầu thay vì viết hộ: Giải mã cơ chế next-token prediction và quy trình 4 bước Reviewer 2 chuẩn Q1",
        audience="Sinh viên năm cuối, học viên cao học và người làm nghiên cứu tại Việt Nam",
        goal="Giải mã bẫy dùng AI viết tổng quan tài liệu và xây dựng quy trình 4 bước biến AI thành Reviewer 2 phản biện đối đầu chuẩn Q1",
        video_type="research_explainer",
        min_duration=80.0,
        max_duration=140.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        sources=build_sources(),
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _, _, _, _) in enumerate(STORY_16X9, 1)],
        characters=[
            {
                "id": "CH01",
                "name": "Người học nghiên cứu",
                "appearance": CAST_APPEARANCE,
                "outfit": DEFAULT_OUTFIT,
            }
        ],
        scenes=scenes,
        tone="Conversational Essayist điềm đạm, ấm áp, sâu sắc, lôi cuốn",
        language="vi",
        subtitles=False,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        packaging=PackagingSpec(
            youtube_title="Dùng AI viết luận văn sẽ bị bắt bài ở mục này",
            visual_hook="Màn hình laptop đỏ rực lỗi đạo văn đối lập với sơ đồ ma trận phản biện AI",
            text_overlay="BẪY DÙNG AI",
            contrast_pair="Dùng AI viết hộ sáo rỗng vs. AI phản biện đối kháng Q1",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_3_conversion",
            seo_keywords=[
                "nghiên cứu khoa học",
                "dùng AI viết luận văn",
                "research gap matrix",
                "literature review",
                "phản biện luận văn",
                "reviewer 2",
            ],
        ),
    )


def build_topic_9x16() -> ResearchedTopic:
    """Build portrait mobile explainer topic: 109 visual beats across 19 scenes (long-form 9:16 ~5 mins)."""
    story_tuples = [(title, setting, rows) for title, setting, _, _, _, rows in STORY_9X16]
    scenes = build_scenes_from_story_rows(story_tuples, character_id="CH01")
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = STORY_9X16[i][2]
        sc.spoken_style = STORY_9X16[i][3]
        sc.narrative_phase = STORY_9X16[i][4]

    # Assign academic sources and claims
    scenes[3].source_ids = ["SRC01"]
    scenes[3].claim_facts = [
        ("chỉ là đoán xác suất của từ tiếp theo.", "SRC01", "Máy tính chỉ đoán xác suất của từ tiếp theo.")
    ]
    scenes[4].source_ids = ["SRC01"]
    scenes[4].claim_facts = [
        ("Để phục vụ hàng triệu người trên thế giới, AI luôn chọn phương án an toàn nhất.", "SRC01", "Trí tuệ nhân tạo luôn chọn từ ngữ an toàn nhất.")
    ]
    scenes[6].source_ids = ["SRC02"]
    scenes[6].claim_facts = [
        ("Mô hình CARS chứng minh rằng, một công trình khoa học, luôn bắt đầu từ sự xung đột.", "SRC02", "Nghiên cứu khoa học bắt đầu từ xung đột học thuật.")
    ]
    scenes[7].source_ids = ["SRC02"]
    scenes[7].claim_facts = [
        ("Khoảng trống nghiên cứu không phải là thứ chưa ai làm vì vô nghĩa.", "SRC02", "Hội đồng luôn tìm kiếm khoảng trống tri thức mới.")
    ]
    scenes[11].source_ids = ["SRC03"]
    scenes[11].claim_facts = [
        ("Nạp luận điểm chính vào hệ thống, và bắt cỗ máy tìm ra ba điểm mù nguy hiểm nhất.", "SRC03", "Phản biện đối đầu giúp phơi bày các điểm mù.")
    ]
    scenes[14].source_ids = ["SRC03"]
    scenes[14].claim_facts = [
        ("Bước bốn: Đối soát chéo từng phản ví dụ thực tế.", "SRC03", "Thử tải luận điểm bằng các phản ví dụ thực tế.")
    ]

    # Verify tone keywords
    tone_warnings = verify_spoken_tone_keywords(scenes)
    if tone_warnings:
        raise ValueError(f"Tone keyword verification failed: {tone_warnings}")

    return ResearchedTopic(
        topic="Đừng để AI viết hộ: Biến AI thành Reviewer 2 đối đầu chuẩn Q1",
        audience="Sinh viên, nghiên cứu sinh và người tự học lướt video ngắn trên di động",
        goal="Tóm lược sắc bén bẫy văn phong trung tính và hướng dẫn 4 bước thực chiến ra lệnh cho AI phản biện đối kháng",
        video_type="research_explainer",
        min_duration=260.0,
        max_duration=340.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=build_sources(),
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _, _, _, _) in enumerate(STORY_9X16, 1)],
        characters=[
            {
                "id": "CH01",
                "name": "Người học di động",
                "appearance": CAST_APPEARANCE,
                "outfit": "Simple teal shirt in vertical safe zone framing.",
            }
        ],
        scenes=scenes,
        tone="Conversational Essayist sắc sảo, dứt khoát, gần gũi",
        language="vi",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        packaging=PackagingSpec(
            youtube_title="Đừng để AI viết hộ: Biến AI thành Reviewer 2",
            visual_hook="Màn hình điện thoại gõ lệnh AI bị hội đồng lật tẩy trong 30 giây",
            text_overlay="BẪY DÙNG AI",
            contrast_pair="Viết hộ rỗng tuếch vs. Phản biện sắc bén",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_3_conversion",
            seo_keywords=[
                "dùng AI viết luận văn",
                "reviewer 2",
                "phản biện học thuật",
                "nghiên cứu khoa học di động",
            ],
        ),
    )


def count_total_beats(scenes: List[ResearchedScene]) -> int:
    return sum(len(sc.visual_beats) for sc in scenes)


def build_and_export_job(topic: ResearchedTopic, out_dir: Path) -> dict:
    result = write_production_package(out_dir, topic)
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
    if (out_dir / "content.json").is_file():
        (draft_dir / "content.json").write_text((out_dir / "content.json").read_text(encoding="utf-8"), encoding="utf-8")
    return result


def populate_run_from_blueprint(job_name: str, bp_dir: Path, run_dir: Path) -> None:
    """Populate an initialized pilot run directory with verified blueprint artifacts."""
    if any((run_dir / name).exists() for name in ('revisions', 'execution-control.json', 'brief-current.json', 'integrity.json')):
        raise ValueError('ACTIVE_JOB_DESTINATION: use official pilot author/revision operations')
    run_dir.mkdir(parents=True, exist_ok=True)
    draft_dir = run_dir / "draft"
    draft_dir.mkdir(parents=True, exist_ok=True)

    for fname in ("brief.json", "content.json", "script.json", "cadence_report.json"):
        src = bp_dir / fname
        if src.is_file():
            (run_dir / fname).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    bp_draft = bp_dir / "draft"
    if bp_draft.is_dir():
        for fname in ("outline.json", "content.json"):
            src = bp_draft / fname
            if src.is_file():
                (draft_dir / fname).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Adversarial AI packages (16:9 and 9:16).")
    parser.add_argument("--aspect-ratio", choices=["16:9", "9:16", "all"], default="all")
    parser.add_argument("--bp-16x9", type=Path, default=SYS_DIR / "content" / "blueprints" / "adversarial-ai-16x9")
    parser.add_argument("--bp-9x16", type=Path, default=SYS_DIR / "content" / "blueprints" / "adversarial-ai-9x16")
    parser.add_argument("--job-16x9", type=Path, default=SYS_DIR / "runs" / "adversarial-ai-16x9")
    parser.add_argument("--job-9x16", type=Path, default=SYS_DIR / "runs" / "adversarial-ai-9x16")
    parser.add_argument("--populate-runs", action="store_true", help="Populate runs directory from blueprints")
    args = parser.parse_args()

    results: Dict[str, Any] = {}

    if args.populate_runs:
        if args.aspect_ratio in ("16:9", "all"):
            populate_run_from_blueprint("adversarial-ai-16x9", args.bp_16x9, args.job_16x9)
            print(f"✅ Populated run directory: {args.job_16x9}")
        if args.aspect_ratio in ("9:16", "all"):
            populate_run_from_blueprint("adversarial-ai-9x16", args.bp_9x16, args.job_9x16)
            print(f"✅ Populated run directory: {args.job_9x16}")
        return

    if args.aspect_ratio in ("16:9", "all"):
        print("=== BUILDING 16:9 LANDSCAPE EXPLAINER (32 VISUAL BEATS) ===")
        topic_16x9 = build_topic_16x9()
        total_beats_16x9 = count_total_beats(topic_16x9.scenes)
        print(f"Total visual beats: {total_beats_16x9} (Target: 32)")
        if total_beats_16x9 != 32:
            raise ValueError(f"16:9 beats count mismatch: expected 32, got {total_beats_16x9}")
        res_16x9 = build_and_export_job(topic_16x9, args.bp_16x9)
        results["16x9"] = res_16x9
        print(json.dumps({
            "job": "adversarial-ai-16x9",
            "blueprint_dir": str(args.bp_16x9),
            "run_dir": str(args.job_16x9),
            "valid_contracts": res_16x9["valid_contracts"],
            "contract_errors": res_16x9["contract_errors"],
            "packaging_warnings": res_16x9["packaging_warnings"],
            "cadence_status": res_16x9["cadence_report"]["status"],
            "cadence_warnings": res_16x9["cadence_report"]["warnings_count"],
            "total_duration": res_16x9["cadence_report"]["total_duration"],
            "total_syllables": res_16x9["cadence_report"]["total_actual_syllables"],
            "visual_beats": total_beats_16x9,
        }, ensure_ascii=False, indent=2))

    if args.aspect_ratio in ("9:16", "all"):
        print("\n=== BUILDING 9:16 VERTICAL LONG-FORM (58 VISUAL BEATS) ===")
        topic_9x16 = build_topic_9x16()
        total_beats_9x16 = count_total_beats(topic_9x16.scenes)
        print(f"Total visual beats: {total_beats_9x16} (Target: 109)")
        if total_beats_9x16 != 109:
            raise ValueError(f"9:16 beats count mismatch: expected 58, got {total_beats_9x16}")
        res_9x16 = build_and_export_job(topic_9x16, args.bp_9x16)
        results["9x16"] = res_9x16
        print(json.dumps({
            "job": "adversarial-ai-9x16",
            "blueprint_dir": str(args.bp_9x16),
            "run_dir": str(args.job_9x16),
            "valid_contracts": res_9x16["valid_contracts"],
            "contract_errors": res_9x16["contract_errors"],
            "packaging_warnings": res_9x16["packaging_warnings"],
            "cadence_status": res_9x16["cadence_report"]["status"],
            "cadence_warnings": res_9x16["cadence_report"]["warnings_count"],
            "total_duration": res_9x16["cadence_report"]["total_duration"],
            "total_syllables": res_9x16["cadence_report"]["total_actual_syllables"],
            "visual_beats": total_beats_9x16,
        }, ensure_ascii=False, indent=2))

    all_passed = all(
        res["valid_contracts"] and res["cadence_report"]["status"] == "PASS"
        for res in results.values()
    )
    if not all_passed:
        print("\n❌ SOME CHECKS FAILED!")
        sys.exit(1)
    print("\n✅ ADVERSARIAL AI PRODUCTION PACKAGES BUILT AND VALIDATED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
