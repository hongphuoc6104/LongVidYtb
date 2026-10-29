#!/usr/bin/env python3
"""Build Brief Revision 6, Content Revision 7, and Images Revision 10 for survivorship-bias-16x9.

Implements 'Cách 2: Kể trọn vẹn điển tích mở màn (Anecdote-First Inversion)':
- Scene 1: Abraham Wald & 1943 Airplane story (full paradox reveal in opening)
- Scene 2: Analogy bridge to everyday life & copycat trap
- Scene 3 & 4: School & valedictorian burnout and graveyard of the uncelebrated
- Scene 5 & 6: Society & startup debt trap and graveyard of the silent
- Scene 7 & 8: Charlie Munger & Inversion thinking (Tư duy Trừ Lùi)
- Scene 9: Punchy conclusion (armor vital engines, failures under the sea)
- Scene 10: Outro (intimate desk reflection & TikTok live invitation)
"""
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pilot import Pilot, read, write
from content_contract import validate_brief, validate_content
from tools.script_diversity_linter import lint_script

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("build_v8")

RUN_DIR = SYS_DIR / "runs/survivorship-bias-16x9"
SRC_IMAGES_DIR = RUN_DIR / "revisions/images/9_retention_hook"
OUT_IMAGES_DIR = RUN_DIR / "revisions/images/10_anecdote_first"

STYLE_170 = (
    "Hand-drawn 2D Vietnamese indie doodle explainer illustration (raw freehand MS-Paint / Flash webcomic aesthetic). "
    "Use clear black outer contours (#000000) with visible unpolished hand-drawn wobble, slightly crooked freehand lines "
    "drawn without a ruler, imperfect corner joints, and uniform marker stroke weight across both foreground and background "
    "(strictly forbid lighter background linework, Bezier curve smoothing, sleek rounded vector icons, or geometric perfection). "
    "Fill all shapes with 100% unshaded flat MS-Paint paint-bucket solid hex colors: warm paper-cream (#F8F0DC), muted apricot-peach "
    "(#F2B88B), soft sage-green (#93A88C), pale ice-blue (#CBE0E0), flat night slate-navy (#2E4361), or stark pure white (#FFFFFF). "
    "Strictly 2D front-on or side-on orthographic flat paper-cutout staging; never use 3/4 isometric furniture perspective, two-tone "
    "bevel shading, floating black oval drop shadows, floor cast shadows, glowing lamp light cones, warm sepia AI color grading, "
    "gradients, photorealism, or 3D rendering. Draw a complete scene image."
)

CHARACTERS = [
    {
        "id": "CH01",
        "name": "Nhân vật người que đầu tròn trắng doodle 2D",
        "appearance": (
            "Iconic 2D Vietnamese indie webcomic doodle stickman (Nguệch Ngoạc / Vẽ Vời / Xấu Vê Nờ style): "
            "oversized slightly lopsided hand-drawn pure-white (#FFFFFF) bald circle head with bold pitch-black (#000000) "
            "marker outline, tiny solid-black dot eyes placed low on the face leaving a large open upper forehead/cranium, "
            "minimal single-stroke eyebrows and mouth, no nose or ears, thin single-line solid-black wire/stick arms "
            "(single black stroke with zero arm thickness) ending in small round white circle hands"
        ),
        "outfit": (
            "Unshaded 100% flat MS-Paint paint-bucket solid cerulean-blue (#3B82C4) simple pill/rectangular T-shirt torso "
            "and simple flat slate-gray (#8C857B) straight trousers or single-line black stick legs, with zero clothing "
            "folds, zero collar details, and zero shading gradients"
        )
    }
]

SOURCES = [
    {
        "id": "SRC01",
        "title": "A Method of Estimating Plane Vulnerability Based on Damage of Returning Aircraft",
        "reference": "Abraham Wald (1943). Statistical Research Group, Columbia University. CRC 432.",
        "facts": [
            "Những chiếc máy bay trúng đạn vào động cơ và buồng lái không thể quay về.",
            "Cần bọc thép vào vị trí máy bay không có lỗ đạn.",
            "Thống kê ban đầu chỉ ghi nhận dữ liệu từ những máy bay sống sót."
        ]
    },
    {
        "id": "SRC02",
        "title": "Poor Charlie's Almanack: The Wit and Wisdom of Charles T. Munger",
        "reference": "Charles T. Munger (2005). Invert, always invert: Turn a situation or problem upside down.",
        "facts": [
            "Tư duy đảo ngược: Muốn thành công, trước hết phải tìm cách không thất bại.",
            "Tránh xa những quyết định dẫn đến thảm họa thay vì tìm kiếm sự xuất sắc phi thực tế."
        ]
    }
]

REQUIRED_POINTS = [
    {
        "id": "R01",
        "text": "Ví dụ lịch sử 1943 của không quân Mỹ và cú đập bàn của Abraham Wald: chỗ cần bọc giáp nhất chính là động cơ không có vết đạn."
    },
    {
        "id": "R02",
        "text": "Cái bẫy quân sự 80 năm lặp lại mỗi ngày khi mù quáng sao chép thói quen của người chiến thắng."
    },
    {
        "id": "R03",
        "text": "Trong trường học, người ta tôn vinh thủ khoa và áp lực cày cuốc thâu đêm nhưng điểm số vẫn lẹt đẹt, cơ thể suy nhược."
    },
    {
        "id": "R04",
        "text": "Bản chất trường học chỉ thưởng cho người về đích đầu tiên, xóa sổ hàng trăm người kiệt sức; bạn chỉ thấy kẻ sống sót."
    },
    {
        "id": "R05",
        "text": "Bước ra ngoài đời không có đáp án mẫu, mạng xã hội tràn ngập hình mẫu 20 tuổi triệu đô khuyên liều lĩnh thoát vùng an toàn."
    },
    {
        "id": "R06",
        "text": "Nghỉ việc lao theo đam mê rồi trắng tay ôm nợ; sự thật là những kẻ sạt nghiệp đã biến mất trong im lặng, không có micro hay sách báo."
    },
    {
        "id": "R07",
        "text": "Bóc tách vết đạn vô hại ở cánh vs động cơ sống còn ngoài đời thực (vốn dự phòng dày cộp, quan hệ ngầm, thời thế)."
    },
    {
        "id": "R08",
        "text": "Vũ khí Tư duy Trừ Lùi của Charlie Munger: không tự nhảy xuống vực, loại bỏ những việc chắc chắn dẫn đến thất bại."
    },
    {
        "id": "R09",
        "text": "Đòn kết liễu đanh thép: Tự hỏi kẻ thất bại đang ở đâu dưới đáy biển, bọc giáp cho tử huyệt của mình trước khi nghĩ đến thành công."
    },
    {
        "id": "R10",
        "text": "Đoạn kết tri ân nhận thức người nghe, mời tham gia các buổi Live đàm đạo chiều sâu trên TikTok, kêu gọi thả tim, chia sẻ vết đạn và theo dõi kênh."
    }
]

SCENE_SPECS = [
    {
        "id": "SC01",
        "title": "Điển tích máy bay 1943 & Cú đập bàn của Abraham Wald",
        "purpose": "Kể trọn vẹn điển tích mở màn: chiếc máy bay đầy vết đạn đánh lừa quân đội Mỹ, cú đập bàn của Abraham Wald vạch trần chân lý bọc giáp động cơ vì máy bay rơi xuống biển không bao giờ trở về.",
        "narration": "Năm một chín bốn ba, quân đội Mỹ tìm cách bọc giáp cho máy bay ném bom. Thấy máy bay bay về chi chít lỗ đạn ở cánh, các tướng lĩnh phán ngay: Thủng ở đâu, bọc thép dày vào đó! Nhà toán học A-bra-ham Uôn đập bàn can lại: Các ông sai bét rồi! Chỗ cần bọc giáp nhất chính là động cơ, nơi chẳng có vết đạn nào. Bởi những chiếc bị bắn thủng động cơ đã nổ tung dưới đáy biển, làm gì có cơ hội quay về căn cứ.",
        "requirements": ["R01"],
        "source_ids": ["SRC01"],
        "coverage_quote": "Nhà toán học A-bra-ham Uôn đập bàn can lại: Các ông sai bét rồi! Chỗ cần bọc giáp nhất chính là động cơ, nơi chẳng có vết đạn nào.",
        "beats": [
            {
                "id": "SC01_I1",
                "src_file": "SC06_I1_16x9.jpg",
                "quote": "Năm một chín bốn ba, quân đội Mỹ tìm cách bọc giáp cho máy bay ném bom.",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) hangar stage: a 1943 military briefing room with two army generals in green peaked caps scratching their heads beside a large wall chalkboard showing a twin-engine bomber airplane blueprint.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC01_I2",
                "src_file": "SC06_I3_16x9.jpg",
                "quote": "Thấy máy bay bay về chi chít lỗ đạn ở cánh, các tướng lĩnh phán ngay: Thủng ở đâu, bọc thép dày vào đó!",
                "desc": "Raw 2D doodle on pale ice-blue (#CBE0E0) stage: an eager general stickman holds a paintbrush and a heavy metal plate, trying to bolt heavy steel armor plates right onto the bullet-riddled outer wings of the plane.",
                "shot_type": "full_scene",
                "effect": "pan_left"
            },
            {
                "id": "SC01_I3",
                "src_file": "SC06_I4_16x9.jpg",
                "quote": "Nhà toán học A-bra-ham Uôn đập bàn can lại: Các ông sai bét rồi! Chỗ cần bọc giáp nhất chính là động cơ, nơi chẳng có vết đạn nào.",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: mathematician Abraham Wald with round glasses slams his hand down onto the drafting table, holding a black ruler pointing firmly at the clean, undamaged engines of the aircraft blueprint with an exclamation mark.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC01_I4",
                "src_file": "SC07_I1_16x9.jpg",
                "quote": "Bởi những chiếc bị bắn thủng động cơ đã nổ tung dưới đáy biển, làm gì có cơ hội quay về căn cứ.",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) underwater ocean floor stage: deep blue sea depths where a destroyed bomber plane with shattered smoking engines rests on the seabed surrounded by small cartoon rising bubbles.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC02",
        "title": "Cầu nối đời thực & Cái bẫy quân sự 80 năm",
        "purpose": "Nối điển tích quân sự sang đời thực: ảo tưởng mù quáng bắt chước người chiến thắng, nhìn vết đạn vô hại thay vì động cơ sống còn.",
        "narration": "Cái bẫy quân sự tám mươi năm trước đang lặp lại mỗi ngày quanh bạn. Từ trường lớp ra ngoài đời, ai cũng bị gieo rắc một ảo tưởng: cứ làm y hệt người chiến thắng thì sẽ đổi đời. Nhưng thực chất, bạn chỉ đang nhìn vào những chiếc máy bay may mắn sống sót, rồi cắm đầu bọc giáp cho những vết đạn vô hại ở cánh.",
        "requirements": ["R02"],
        "source_ids": [],
        "coverage_quote": "Cái bẫy quân sự tám mươi năm trước đang lặp lại mỗi ngày quanh bạn.",
        "beats": [
            {
                "id": "SC02_I1",
                "src_file": "SC01_I1_16x9.jpg",
                "quote": "Cái bẫy quân sự tám mươi năm trước đang lặp lại mỗi ngày quanh bạn.",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: a crude 2D propeller bomber plane sits on the runway, its wide wings and fuselage covered in dozens of prominent red marker bullet hole dots.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC02_I2",
                "src_file": "SC01_I3_16x9.jpg",
                "quote": "Từ trường lớp ra ngoài đời, ai cũng bị gieo rắc một ảo tưởng: cứ làm y hệt người chiến thắng thì sẽ đổi đời.",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: the blue-shirt stickman stares mesmerized with starry eyes at an enormous flashy roadside billboard. On the billboard, a smiling doodle stickman in a tuxedo steps out of a luxury sports car with a giant comic speech bubble: LÀM Y HỆT TÔI ĐI!",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            },
            {
                "id": "SC02_I3",
                "src_file": "SC07_I2_16x9.jpg",
                "quote": "Nhưng thực chất, bạn chỉ đang nhìn vào những chiếc máy bay may mắn sống sót, rồi cắm đầu bọc giáp cho những vết đạn vô hại ở cánh.",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: the blue-shirt stickman frantically buys superficial items: wearing a fake luxury necktie, holding a takeaway coffee, and pointing to a 4:00 AM alarm, with a black marker arrow labeled VẾT ĐẠN VÔ HẠI.",
                "shot_type": "full_scene",
                "effect": "pan_right"
            }
        ]
    },
    {
        "id": "SC03",
        "title": "Ảo tưởng thủ khoa & Cày cuốc thâu đêm",
        "purpose": "Phơi bày thực trạng trong trường học: tôn sùng thủ khoa, bắt chước cày đêm nhưng kiệt sức và bế tắc.",
        "narration": "Trong trường học, người ta tôn sùng thủ khoa như một vị thần. Báo đài tung hô bí quyết học mười sáu tiếng một ngày, thức khuya, dậy sớm, giải hàng nghìn bài tập. Bạn cắm đầu làm theo, bỏ ngủ, nhịn ăn, nhưng điểm số vẫn lẹt đẹt, còn cơ thể thì suy nhược.",
        "requirements": ["R03"],
        "source_ids": [],
        "coverage_quote": "bỏ ngủ, nhịn ăn, nhưng điểm số vẫn lẹt đẹt, còn cơ thể thì suy nhược.",
        "beats": [
            {
                "id": "SC03_I1",
                "src_file": "SC02_I1_16x9.jpg",
                "quote": "Trong trường học, người ta tôn sùng thủ khoa như một vị thần. Báo đài tung hô bí quyết học mười sáu tiếng một ngày,",
                "desc": "Raw 2D doodle on pale ice-blue (#CBE0E0) stage: a smiling valedictorian stickman stands on a high wooden podium holding a giant test paper stamped with a bright red score 100/100, wearing a red champion ribbon.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC03_I2",
                "src_file": "SC02_I2_16x9.jpg",
                "quote": "thức khuya, dậy sớm, giải hàng nghìn bài tập. Bạn cắm đầu làm theo,",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) night stage: the blue-shirt stickman sits at a crooked wooden study desk at 3:00 AM, giant alarm clock clattering, head steaming with exhaustion, dark circles under his eyes, buried beneath towering zigzag piles of math exercise books.",
                "shot_type": "full_scene",
                "effect": "pan_left"
            },
            {
                "id": "SC03_I3",
                "src_file": "SC02_I3_16x9.jpg",
                "quote": "bỏ ngủ, nhịn ăn, nhưng điểm số vẫn lẹt đẹt, còn cơ thể thì suy nhược.",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: the stickman lies limp like a noodle across the wooden desk, face flat on a crumpled paper marked 4/10 with big red question marks floating above his head, body trembling with fatigue.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC04",
        "title": "Bản chất trường học & Nghĩa địa sau lưng kẻ thắng",
        "purpose": "Lật tẩy bản chất trường học chỉ thưởng cho một người về đích đầu tiên, xóa sổ hàng trăm người kiệt sức.",
        "narration": "Bản chất trường học chỉ trao phần thưởng cho một người về đích đầu tiên. Không một ai phỏng vấn hàng trăm học sinh khác cũng thức đêm, cũng cày cuốc y hệt, nhưng trượt vỏ chuối vì kiệt sức, hoặc đơn giản là không có thiên phú bẩm sinh. Bạn chỉ được nhìn thấy kẻ sống sót.",
        "requirements": ["R04"],
        "source_ids": [],
        "coverage_quote": "Bản chất trường học chỉ trao phần thưởng cho một người về đích đầu tiên.",
        "beats": [
            {
                "id": "SC04_I1",
                "src_file": "SC03_I1_16x9.jpg",
                "quote": "Bản chất trường học chỉ trao phần thưởng cho một người về đích đầu tiên.",
                "desc": "Raw 2D doodle on pale ice-blue (#CBE0E0) stage: a single victorious stickman smiles proudly on the highest championship podium holding a giant gold cup, while golden confetti drifts through the air.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC04_I2",
                "src_file": "SC03_I2_16x9.jpg",
                "quote": "Không một ai phỏng vấn hàng trăm học sinh khác cũng thức đêm, cũng cày cuốc y hệt, nhưng trượt vỏ chuối vì kiệt sức,",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: deep pit below the winner's podium! A crowd of dozens of tired doodle stickmen with X-eyes and dizzy sweat drops are tumbled in a ditch beside banana peels and torn exercise notebooks, completely out of sight.",
                "shot_type": "full_scene",
                "effect": "pan_right"
            },
            {
                "id": "SC04_I3",
                "src_file": "SC03_I3_16x9.jpg",
                "quote": "hoặc đơn giản là không có thiên phú bẩm sinh. Bạn chỉ được nhìn thấy kẻ sống sót.",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) stage: a dramatic theatrical spotlight beam shines down brightly on the single lone survivor standing tall, while 90% of the stage is in total black silhouette filled with shadowy fallen stickmen.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC05",
        "title": "Bước ra ngoài đời & Cú lừa triệu đô",
        "purpose": "Chuyển cảnh ra xã hội: không có đáp án mẫu, mạng xã hội tung hô thần tượng làm giàu liều lĩnh.",
        "narration": "Bước ra ngoài đời, cái bẫy này còn tàn khốc gấp mười lần. Ngoài xã hội không có đáp án mẫu, cũng chẳng ai phát đề thi cho bạn. Lướt điện thoại đâu đâu cũng thấy những tấm gương đổi đời: hai mươi tuổi kiếm triệu đô, bỏ học làm chủ, nhảy việc nhân năm lần lương. Họ mở khóa học, viết sách, ra rả dạy đời: Dám liều mới giàu! Hãy bước ra khỏi vùng an toàn!",
        "requirements": ["R05"],
        "source_ids": [],
        "coverage_quote": "Lướt điện thoại đâu đâu cũng thấy những tấm gương đổi đời: hai mươi tuổi kiếm triệu đô, bỏ học làm chủ, nhảy việc nhân năm lần lương.",
        "beats": [
            {
                "id": "SC05_I1",
                "src_file": "SC04_I1_16x9.jpg",
                "quote": "Bước ra ngoài đời, cái bẫy này còn tàn khốc gấp mười lần. Ngoài xã hội không có đáp án mẫu, cũng chẳng ai phát đề thi cho bạn.",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: the blue-shirt stickman steps out through the school gates into a bustling chaotic concrete maze with confusing road signs pointing in four opposite directions and floating question marks.",
                "shot_type": "full_scene",
                "effect": "pan_left"
            },
            {
                "id": "SC05_I2",
                "src_file": "SC04_I2_16x9.jpg",
                "quote": "Lướt điện thoại đâu đâu cũng thấy những tấm gương đổi đời: hai mươi tuổi kiếm triệu đô, bỏ học làm chủ, nhảy việc nhân năm lần lương.",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: the blue-shirt stickman looks at his smartphone screen as giant comic popup notifications explode outwards: 20 TUỔI TRIỆU ĐÔ, BỎ HỌC LÀM CHỦ, X5 LƯƠNG with flying money bills.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC05_I3",
                "src_file": "SC04_I3_16x9.jpg",
                "quote": "Họ mở khóa học, viết sách, ra rả dạy đời:",
                "desc": "Raw 2D doodle on pale ice-blue (#CBE0E0) stage: a flamboyant online guru stickman wearing sunglasses stands on an elevated stage behind a wooden lectern, holding up a thick bestselling book with a big red stamp KHÓA HỌC LÀM GIÀU.",
                "shot_type": "full_scene",
                "effect": "pan_right"
            },
            {
                "id": "SC05_I4",
                "src_file": "SC04_I4_16x9.jpg",
                "quote": "Dám liều mới giàu! Hãy bước ra khỏi vùng an toàn!",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) stage: the guru shouts through an oversized megaphone with a massive speech bubble: DÁM LIỀU MỚI GIÀU! In front of him, the gullible blue-shirt stickman gets pumped up, rolling up his sleeves ready to leap off a ledge.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC06",
        "title": "Cú vấp ngã & Nghĩa địa của những người im lặng",
        "purpose": "Cú vấp ngã thực tế: sạt nghiệp ôm nợ và sự thật về nghĩa địa vô hình không có micro hay sách báo.",
        "narration": "Bạn nghe bùi tai, nộp đơn nghỉ việc cái rụp, dốc sạch tiền tiết kiệm lao theo đam mê. Và chỉ nửa năm sau, bạn trắng tay, ôm đống nợ và tự dằn vặt: Sao người ta làm được mà mình lại toang? Bạn không hề kém cỏi. Sự thật cay đắng là: những người dám liều mà sạt nghiệp, họ đã biến mất trong im lặng. Họ làm gì có micro, chẳng có sân khấu nào mời họ, và dĩ nhiên không ai rảnh để in sách kể về những kẻ thất bại.",
        "requirements": ["R06"],
        "source_ids": [],
        "coverage_quote": "Và chỉ nửa năm sau, bạn trắng tay, ôm đống nợ và tự dằn vặt: Sao người ta làm được mà mình lại toang?",
        "beats": [
            {
                "id": "SC06_I1",
                "src_file": "SC05_I1_16x9.jpg",
                "quote": "Bạn nghe bùi tai, nộp đơn nghỉ việc cái rụp, dốc sạch tiền tiết kiệm lao theo đam mê.",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) office stage: the enthusiastic stickman slams a resignation paper titled ĐƠN NGHỈ VIỆC onto his office desk, grinning broadly while carrying a cardboard box of personal belongings.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC06_I2",
                "src_file": "SC05_I2_16x9.jpg",
                "quote": "Và chỉ nửa năm sau, bạn trắng tay, ôm đống nợ và tự dằn vặt: Sao người ta làm được mà mình lại toang?",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) night stage: 6 months later, the stickman sits slumped on the floor of a barren room, holding an empty turned-out wallet with moths flying out, surrounded by a mountain of red bills stamped NỢ.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            },
            {
                "id": "SC06_I3",
                "src_file": "SC05_I3_16x9.jpg",
                "quote": "Bạn không hề kém cỏi. Sự thật cay đắng là: những người dám liều mà sạt nghiệp, họ đã biến mất trong im lặng.",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) stage: a vast silent graveyard under a crescent moon, dotted with dozens of simple wooden cross markers where bankrupt stickmen sit silently in the dark with head in knees.",
                "shot_type": "full_scene",
                "effect": "pan_left"
            },
            {
                "id": "SC06_I4",
                "src_file": "SC05_I4_16x9.jpg",
                "quote": "Họ làm gì có micro, chẳng có sân khấu nào mời họ, và dĩ nhiên không ai rảnh để in sách kể về những kẻ thất bại.",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: an empty dimly-lit auditorium stage with a lone cold microphone on a stand, its cable unplugged on the wooden floor, with zero audience and zero book in sight.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            }
        ]
    },
    {
        "id": "SC07",
        "title": "Động cơ sống còn & Vũ khí Tư duy Trừ Lùi",
        "purpose": "Bóc tách động cơ thật sự giúp sống sót ngoài đời và giới thiệu vũ khí Tư duy Trừ Lùi của Charlie Munger.",
        "narration": "Thứ thực sự giúp người thành công sống sót, như vốn dự phòng dày cộp, quan hệ ngầm hay thời thế, họ giấu nhẹm đi hoặc chính họ cũng chẳng nhận ra. Muốn tồn tại vững vàng, bạn cần đổi góc nhìn. Huyền thoại đầu tư Chác-li Măng-gơ từng nhắc nhở: Muốn đến đích an toàn, việc đầu tiên là đừng tự nhảy xuống vực. Đó chính là Tư duy Trừ Lùi.",
        "requirements": ["R07"],
        "source_ids": ["SRC02"],
        "coverage_quote": "Thứ thực sự giúp người thành công sống sót, như vốn dự phòng dày cộp, quan hệ ngầm hay thời thế,",
        "beats": [
            {
                "id": "SC07_I1",
                "src_file": "SC07_I3_16x9.jpg",
                "quote": "Thứ thực sự giúp người thành công sống sót, như vốn dự phòng dày cộp, quan hệ ngầm hay thời thế,",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) stage: a deep two-layer comparison stage. The small top tier shows a smiling stickman holding a tiny sign BÍ QUYẾT TRÊN MẠNG; the massive bottom foundation shows a giant solid steel vault labeled VỐN DÀY and two clasped hands labeled QUAN HỆ.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC07_I2",
                "src_file": "SC07_I4_16x9.jpg",
                "quote": "họ giấu nhẹm đi hoặc chính họ cũng chẳng nhận ra. Muốn tồn tại vững vàng, bạn cần đổi góc nhìn.",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: a successful influencer stickman stands behind a smiling stage mask holding a microphone, while behind his back is an enormous locked steel door concealing his family wealth and backup safety net.",
                "shot_type": "full_scene",
                "effect": "pan_right"
            },
            {
                "id": "SC07_I3",
                "src_file": "SC08_I1_16x9.jpg",
                "quote": "Huyền thoại đầu tư Chác-li Măng-gơ từng nhắc nhở: Muốn đến đích an toàn, việc đầu tiên là đừng tự nhảy xuống vực. Đó chính là Tư duy Trừ Lùi.",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: an elderly wise stickman with round glasses (Charlie Munger) points with a walking stick at a sharp cliff edge where a large red skull sign warns: ĐỪNG NHẢY XUỐNG VỰC!",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC08",
        "title": "Lập danh sách tử huyệt & Phòng thủ kiên cố",
        "purpose": "Áp dụng Tư duy Trừ Lùi: lập danh sách những điều gây thất bại để tránh xa, giữ mạng trước khi nghĩ làm giàu.",
        "narration": "Người đời thường mù quáng đi tìm công thức để thành công, nhưng kẻ khôn ngoan lại lập danh sách những việc chắc chắn dẫn đến cái chết, để tránh xa. Đừng hỏi làm sao để kiếm triệu đô sau một đêm. Hãy hỏi: làm thế nào để dù thị trường có sập, bản thân vẫn không phá sản.",
        "requirements": ["R08"],
        "source_ids": ["SRC02"],
        "coverage_quote": "Người đời thường mù quáng đi tìm công thức để thành công, nhưng kẻ khôn ngoan lại lập danh sách những việc chắc chắn dẫn đến cái chết, để tránh xa.",
        "beats": [
            {
                "id": "SC08_I1",
                "src_file": "SC08_I2_16x9.jpg",
                "quote": "Người đời thường mù quáng đi tìm công thức để thành công, nhưng kẻ khôn ngoan lại lập danh sách những việc chắc chắn dẫn đến cái chết, để tránh xa.",
                "desc": "Raw 2D doodle on pale ice-blue (#CBE0E0) stage: a giant wooden checklist board on which the stickman crosses out fatal traps with bold red X marks: VAY LÃI CAO (crossed out), TẤT TAY MỘT CỬA (crossed out), ẢO TƯỞNG LÀM GIÀU (crossed out).",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC08_I2",
                "src_file": "SC08_I3_16x9.jpg",
                "quote": "Đừng hỏi làm sao để kiếm triệu đô sau một đêm.",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: a gambler stickman reaching hungrily for a shiny gold pot perched precariously over a deep pit, with a giant red warning question mark hovering above.",
                "shot_type": "full_scene",
                "effect": "pan_left"
            },
            {
                "id": "SC08_I3",
                "src_file": "SC08_I4_16x9.jpg",
                "quote": "Hãy hỏi: làm thế nào để dù thị trường có sập, bản thân vẫn không phá sản.",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) stage: the blue-shirt stickman stands calm and secure behind a heavy steel shield wall while dark economic storm clouds rain lightning bolts outside, safe and completely unshakeable.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC09",
        "title": "Đòn kết liễu: Giữ mạng sống trước khi cất cánh",
        "purpose": "Đòn kết liễu đanh thép: dừng sao chép vô bổ, tự hỏi những kẻ thất bại đang ở đâu dưới đáy biển, bọc giáp cho tử huyệt.",
        "narration": "Bắt chước người chiến thắng chỉ biến bạn thành một bản sao mệt mỏi. Lần tới, khi thấy ai đó khoe mẽ hào quang rực rỡ, đừng vội cắm đầu làm theo. Hãy tự hỏi: những kẻ làm y hệt họ mà thất bại, giờ đang nằm ở đâu dưới đáy biển? Bọc giáp cho tử huyệt của mình trước, giữ cho mình sống sót đã, rồi thành công mới chịu đến lượt bạn.",
        "requirements": ["R09"],
        "source_ids": ["SRC01"],
        "coverage_quote": "Hãy tự hỏi: những kẻ làm y hệt họ mà thất bại, giờ đang nằm ở đâu dưới đáy biển?",
        "beats": [
            {
                "id": "SC09_I1",
                "src_file": "SC09_I1_16x9.jpg",
                "quote": "Bắt chước người chiến thắng chỉ biến bạn thành một bản sao mệt mỏi.",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) stage: the blue-shirt stickman looks into a full-length dressing mirror and sees himself as an exhausted puppet with tangled strings, realizing blind imitation only drains his soul.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC09_I2",
                "src_file": "SC09_I2_16x9.jpg",
                "quote": "Lần tới, khi thấy ai đó khoe mẽ hào quang rực rỡ, đừng vội cắm đầu làm theo. Hãy tự hỏi: những kẻ làm y hệt họ mà thất bại, giờ đang nằm ở đâu dưới đáy biển?",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: the stickman stands holding a magnifying glass, looking past a glowing TV screen showing an influencer, peering down into the deep blue ocean where sunken airplanes rest peacefully.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            },
            {
                "id": "SC09_I3",
                "src_file": "SC09_I3_16x9.jpg",
                "quote": "Bọc giáp cho tử huyệt của mình trước, giữ cho mình sống sót đã,",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) stage: the stickman confidently uses a wrench to bolt a thick solid steel armor plate over his chest engine, eyes determined and resolute, standing solidly on the ground.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC09_I4",
                "src_file": "SC09_I4_16x9.jpg",
                "quote": "rồi thành công mới chịu đến lượt bạn.",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) sunrise stage: the sturdy 2D propeller airplane with gleaming armored engines takes off smoothly into the bright open sky, soaring high above the clouds toward the morning sun.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC10",
        "title": "Không gian đàm đạo & Lời hẹn từ bản chất",
        "purpose": "Đoạn kết tri ân nhận thức người nghe, mời tham gia các buổi Live đàm đạo chiều sâu trên TikTok, kêu gọi thả tim, chia sẻ vết đạn và theo dõi kênh.",
        "narration": "Nếu bạn đã kiên nhẫn đồng hành cùng mình đến tận giây phút này, có lẽ bạn cũng nhận ra: nhận diện được thiên kiến chỉ là bước đầu. Rèn được bản lĩnh trừ lùi trong đời thực mới là thứ cần mài giũa mỗi ngày. Dạo gần đây, TikTok đang khuyến khích chúng mình mở những không gian phát trực tiếp. Sắp tới, mình sẽ có những buổi Live ngồi lại cùng bạn, mổ xẻ những góc khuất và những cú vấp ngã chưa từng được kể trong công việc lẫn cuộc sống của chính các bạn. Nếu góc nhìn hôm nay giúp bạn bớt đi một ảo tưởng, hãy thả một tim, để lại câu chuyện về vết đạn bạn từng nếm trải dưới phần bình luận, và theo dõi kênh để cùng rèn luyện tư duy mỗi ngày. Hẹn gặp bạn trong buổi Live đàm đạo gần nhất.",
        "requirements": ["R10"],
        "source_ids": [],
        "coverage_quote": "Dạo gần đây, TikTok đang khuyến khích chúng mình mở những không gian phát trực tiếp.",
        "beats": [
            {
                "id": "SC10_I1",
                "src_file": "SC10_I1_16x9.jpg",
                "quote": "Nếu bạn đã kiên nhẫn đồng hành cùng mình đến tận giây phút này, có lẽ bạn cũng nhận ra: nhận diện được thiên kiến chỉ là bước đầu. Rèn được bản lĩnh trừ lùi trong đời thực mới là thứ cần mài giũa mỗi ngày.",
                "desc": "Raw 2D Vietnamese indie doodle explainer illustration on a warm paper-cream (#F8F0DC) stage with bold unpolished black marker contours (#000000). The white bald circle-head stickman in a solid cerulean-blue (#3B82C4) shirt sits comfortably behind a simple rustic wooden table, leaning forward with a warm, thoughtful smile, holding a steaming ceramic mug. Above hangs a single gentle doodle ceiling bulb glowing with soft hand-drawn rays. Intimate, calm, intellectual atmosphere.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC10_I2",
                "src_file": "SC10_I2_16x9.jpg",
                "quote": "Dạo gần đây, TikTok đang khuyến khích chúng mình mở những không gian phát trực tiếp. Sắp tới, mình sẽ có những buổi Live ngồi lại cùng bạn, mổ xẻ những góc khuất và những cú vấp ngã chưa từng được kể trong công việc lẫn cuộc sống của chính các bạn.",
                "desc": "Raw 2D Vietnamese indie doodle explainer illustration on a pale ice-blue (#CBE0E0) stage with crooked black contours (#000000). The stickman speaks calmly into a classic vintage desktop broadcast microphone. Surrounding the stage are multiple friendly doodle stickmen avatars appearing in round speech bubbles with question marks and bold exclamation marks, showing an engaging live community roundtable discussion. No flashy neon UI, purely organic conversational doodle setting.",
                "shot_type": "full_scene",
                "effect": "pan_left"
            },
            {
                "id": "SC10_I3",
                "src_file": "SC10_I3_16x9.jpg",
                "quote": "Nếu góc nhìn hôm nay giúp bạn bớt đi một ảo tưởng, hãy thả một tim, để lại câu chuyện về vết đạn bạn từng nếm trải dưới phần bình luận, và theo dõi kênh để cùng rèn luyện tư duy mỗi ngày. Hẹn gặp bạn trong buổi Live đàm đạo gần nhất.",
                "desc": "Raw 2D Vietnamese indie doodle explainer illustration on a soft sage-green (#93A88C) stage with loose black marker lines (#000000). The blue-shirt stickman waves one hand warmly in a friendly farewell gesture while holding a small notebook in the other. Beside him are three clean hand-drawn doodle accent icons: a warm crimson-red heart (#EF4444), a small thought comment bubble, and a minimal bookmark ribbon. Clean, respectful, memorable closure.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            }
        ]
    }
]


SCENE_SETTINGS = {
    "SC01": "Flat soft sage-green (#93A88C) and apricot-peach (#F2B88B) 2D orthographic military hangar stage.",
    "SC02": "Flat warm paper-cream (#F8F0DC) and apricot-peach (#F2B88B) 2D orthographic comic stage.",
    "SC03": "Flat warm paper-cream (#F8F0DC) and slate-navy (#2E4361) 2D orthographic study stage.",
    "SC04": "Flat pale ice-blue (#CBE0E0) and slate-navy (#2E4361) 2D orthographic podium stage.",
    "SC05": "Flat warm paper-cream (#F8F0DC) and apricot-peach (#F2B88B) 2D orthographic city street stage.",
    "SC06": "Flat warm paper-cream (#F8F0DC) and slate-navy (#2E4361) 2D orthographic room stage.",
    "SC07": "Flat soft sage-green (#93A88C) and apricot-peach (#F2B88B) 2D orthographic comparison stage.",
    "SC08": "Flat warm paper-cream (#F8F0DC) and soft sage-green (#93A88C) 2D orthographic strategy stage.",
    "SC09": "Flat slate-navy (#2E4361) and warm paper-cream (#F8F0DC) 2D orthographic takeoff stage.",
    "SC10": "Flat warm paper-cream (#F8F0DC), pale ice-blue (#CBE0E0), and soft sage-green (#93A88C) 2D orthographic studio stage."
}


def main():
    logger.info("Starting build for survivorship-bias-16x9 Revision 8 / Anecdote-First Inversion...")

    # 1. Build Brief 6
    brief_data = json.loads((RUN_DIR / "briefs/5.json").read_text(encoding="utf-8"))
    brief_data["goal"] = "Giải mã Thiên kiến Kẻ Sống Sót bằng điển tích máy bay ném bom 1943 của Abraham Wald ngay mở màn, bóc tách áp lực bắt chước thủ khoa trong trường học và cú vấp ngã ngoài xã hội, rồi trao vũ khí Tư duy Trừ Lùi của Charlie Munger để bọc giáp cho tử huyệt trước khi cất cánh."
    brief_data["required_points"] = REQUIRED_POINTS
    brief_data["sources"] = SOURCES
    brief_data["human_editorial"]["author_raw_input"] = "Kể trọn vẹn điển tích mở màn máy bay 1943 của Abraham Wald (Anecdote-First Inversion), sau đó nối cầu nối đời thực sang trường học và xã hội, và đúc kết bằng Tư duy Trừ Lùi của Charlie Munger."
    brief_data["human_editorial"]["expanded_content_ideas"] = [
        {
            "angle_type": "commentary",
            "idea_summary": "Điển tích máy bay 1943 của Abraham Wald mở màn và chân lý bọc giáp động cơ.",
            "narrative_integration": "Triển khai tại SC01 và SC02."
        },
        {
            "angle_type": "analysis",
            "idea_summary": "Bóc trần ảo tưởng trường học và mạng xã hội: chỉ tôn vinh kẻ sống sót duy nhất.",
            "narrative_integration": "Triển khai tại SC03 đến SC06."
        },
        {
            "angle_type": "evaluation",
            "idea_summary": "Vũ khí Tư duy Trừ Lùi của Charlie Munger và đòn kết liễu đanh thép.",
            "narrative_integration": "Triển khai tại SC07 đến SC10."
        }
    ]
    brief_data["enforce_phonetic_gate"] = True

    validate_brief(SYS_DIR, brief_data)
    brief_file = RUN_DIR / "briefs/6.json"
    brief_text = json.dumps(brief_data, indent=2, ensure_ascii=False) + "\n"
    brief_file.write_text(brief_text, encoding="utf-8")
    brief_hash = hashlib.sha256(brief_text.encode("utf-8")).hexdigest()
    logger.info(f"Brief 6 written successfully (hash={brief_hash[:8]}...)")

    # Update brief-current.json
    brief_cur = {
        "revision": 6,
        "hash": brief_hash
    }
    (RUN_DIR / "brief-current.json").write_text(json.dumps(brief_cur, indent=2) + "\n", encoding="utf-8")
    logger.info("Updated brief-current.json to revision 6")

    # 2. Build Content Revision 7
    content_scenes = []
    coverage = []

    for sc in SCENE_SPECS:
        sc_id = sc["id"]
        narration = sc["narration"]
        reqs = sc["requirements"]
        src_ids = sc["source_ids"]

        images = []
        beats = []
        for idx, b in enumerate(sc["beats"]):
            img_id = b["id"]
            quote = b["quote"]
            desc = b["desc"]
            shot_type = b["shot_type"]
            effect = b["effect"]

            assert quote in narration, f"Quote {quote!r} not found in narration of {sc_id}"

            images.append({
                "id": img_id,
                "description": desc,
                "character_ids": ["CH01"],
                "based_on": None,
                "preserve": "",
                "change": desc,
                "reason": "Show the concrete object, comparison, or action at its spoken anchor.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": shot_type,
                "has_character": True,
                "explanation": {
                    "quote": quote,
                    "relation": "context",
                    "source_terms": [quote.split()[-1].strip(".,!?:;")],
                    "visual_terms": [desc[:40]]
                }
            })

            beats.append({
                "id": img_id.replace("_I", "_B"),
                "image_id": img_id,
                "purpose": sc["purpose"],
                "anchor": {
                    "vi": {
                        "quote": quote,
                        "occurrence": 1
                    }
                },
                "effect": effect,
                "focus": {
                    "x": 0.5,
                    "y": 0.5
                }
            })

        content_scenes.append({
            "id": sc_id,
            "title": sc["title"],
            "purpose": sc["purpose"],
            "action": sc["purpose"],
            "setting": SCENE_SETTINGS[sc_id],
            "camera": "Narration-led full-frame compositions",
            "narration": narration,
            "requirements": reqs,
            "character_ids": ["CH01"],
            "source_ids": src_ids,
            "images": images,
            "beats": beats
        })

        for req_id in reqs:
            coverage.append({
                "requirement_id": req_id,
                "scene_id": sc_id,
                "quote": sc["coverage_quote"]
            })

    outline = [
        {
            "scene_id": sc["id"],
            "purpose": sc["purpose"],
            "requirements": sc["requirements"],
            "transition": "Kết thúc video." if sc["id"] == "SC10" else "Cắt thẳng nhịp nhàng chuyển cảnh."
        }
        for sc in SCENE_SPECS
    ]

    claims = [
        {
            "scene_id": "SC01",
            "quote": "Chỗ cần bọc giáp nhất chính là động cơ, nơi chẳng có vết đạn nào.",
            "language": "vi",
            "source_id": "SRC01",
            "fact": "Cần bọc thép vào vị trí máy bay không có lỗ đạn."
        },
        {
            "scene_id": "SC01",
            "quote": "Bởi những chiếc bị bắn thủng động cơ đã nổ tung dưới đáy biển, làm gì có cơ hội quay về căn cứ.",
            "language": "vi",
            "source_id": "SRC01",
            "fact": "Những chiếc máy bay trúng đạn vào động cơ và buồng lái không thể quay về."
        },
        {
            "scene_id": "SC07",
            "quote": "Muốn đến đích an toàn, việc đầu tiên là đừng tự nhảy xuống vực. Đó chính là Tư duy Trừ Lùi.",
            "language": "vi",
            "source_id": "SRC02",
            "fact": "Tư duy đảo ngược: Muốn thành công, trước hết phải tìm cách không thất bại."
        },
        {
            "scene_id": "SC08",
            "quote": "kẻ khôn ngoan lại lập danh sách những việc chắc chắn dẫn đến cái chết, để tránh xa.",
            "language": "vi",
            "source_id": "SRC02",
            "fact": "Tránh xa những quyết định dẫn đến thảm họa thay vì tìm kiếm sự xuất sắc phi thực tế."
        }
    ]

    revision_response = [
        {
            "request_id": "R01",
            "status": "addressed",
            "explanation": "Tái cấu trúc video theo Cách 2: Kể trọn vẹn điển tích mở màn (Anecdote-First Inversion), nối mượt mà từ máy bay 1943 sang trường học, xã hội và Tư duy Trừ Lùi.",
            "scene_ids": ["SC01", "SC02"]
        }
    ]

    content_data = {
        "schema_version": "3.0",
        "brief_revision": 6,
        "brief_hash": brief_hash,
        "topic": brief_data["topic"],
        "duration": brief_data["duration"],
        "style": brief_data["style"],
        "required_points": [r["text"] for r in REQUIRED_POINTS],
        "characters": CHARACTERS,
        "scenes": content_scenes,
        "coverage": coverage,
        "outline": outline,
        "claims": claims,
        "revision_response": revision_response,
        "open_questions": []
    }

    # Validate content against Schema 3.0 & contracts
    validate_content(SYS_DIR, brief_data, 6, brief_hash, content_data)
    logger.info("validate_content passed successfully!")

    # Lint with script_diversity_linter
    lint_report = lint_script(content_scenes, characters=CHARACTERS, style=STYLE_170)
    logger.info(f"Script diversity linter violations: {len(lint_report.get('violations', []))}")
    if lint_report.get("violations"):
        for v in lint_report["violations"]:
            logger.error(f"Linter violation: {v}")
        raise ValueError("Script diversity linter failed!")

    content_rev_dir = RUN_DIR / "revisions/content/7"
    content_rev_dir.mkdir(parents=True, exist_ok=True)
    content_file = content_rev_dir / "content.json"
    content_text = json.dumps(content_data, indent=2, ensure_ascii=False) + "\n"
    content_file.write_text(content_text, encoding="utf-8")
    logger.info(f"Content 7 written to {content_file}")

    # Copy to draft/content.json
    (RUN_DIR / "draft/content.json").write_text(content_text, encoding="utf-8")

    # 3. Build Images Revision 10 (reusing 34 images + thumbnail)
    OUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    image_items = []

    for sc in SCENE_SPECS:
        sc_id = sc["id"]
        for b in sc["beats"]:
            new_id = b["id"]
            src_file_name = b["src_file"]
            src_jpg = SRC_IMAGES_DIR / src_file_name
            src_json = SRC_IMAGES_DIR / src_file_name.replace(".jpg", ".json")

            dst_jpg_name = f"{new_id}_16x9.jpg"
            dst_json_name = f"{new_id}_16x9.json"
            dst_jpg = OUT_IMAGES_DIR / dst_jpg_name
            dst_json = OUT_IMAGES_DIR / dst_json_name

            shutil.copy2(src_jpg, dst_jpg)
            if src_json.exists():
                sidecar_data = json.loads(src_json.read_text(encoding="utf-8"))
                sidecar_data["image_id"] = new_id
                sidecar_data["scene_id"] = sc_id
                sidecar_data["file_path"] = f"revisions/images/10_anecdote_first/{dst_jpg_name}"
                dst_json.write_text(json.dumps(sidecar_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            else:
                sidecar_data = {
                    "image_id": new_id,
                    "scene_id": sc_id,
                    "file_path": f"revisions/images/10_anecdote_first/{dst_jpg_name}",
                    "prompt": b["desc"]
                }
                dst_json.write_text(json.dumps(sidecar_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

            img_hash = hashlib.sha256(dst_jpg.read_bytes()).hexdigest()
            image_items.append({
                "image_id": new_id,
                "scene_id": sc_id,
                "path": f"revisions/images/10_anecdote_first/{dst_jpg_name}",
                "prompt": b["desc"],
                "source": "reused_from_revision_9",
                "actual_prompt": b["desc"],
                "sha256": img_hash,
                "ratio": "16:9",
                "forge_id": "verified_2d_doodle",
                "profile_id": "profile_1"
            })

    # Add Thumbnail
    thumb_src_jpg = SRC_IMAGES_DIR / "THUMBNAIL_16x9.jpg"
    thumb_dst_jpg = OUT_IMAGES_DIR / "THUMBNAIL_16x9.jpg"
    shutil.copy2(thumb_src_jpg, thumb_dst_jpg)
    thumb_src_json = SRC_IMAGES_DIR / "THUMBNAIL_16x9.json"
    thumb_dst_json = OUT_IMAGES_DIR / "THUMBNAIL_16x9.json"
    if thumb_src_json.exists():
        shutil.copy2(thumb_src_json, thumb_dst_json)
    thumb_hash = hashlib.sha256(thumb_dst_jpg.read_bytes()).hexdigest()
    image_items.append({
        "image_id": "THUMBNAIL",
        "scene_id": "THUMBNAIL",
        "path": "revisions/images/10_anecdote_first/THUMBNAIL_16x9.jpg",
        "prompt": "THUMBNAIL 16x9",
        "source": "reused_from_revision_9",
        "actual_prompt": "THUMBNAIL 16x9",
        "sha256": thumb_hash,
        "ratio": "16:9",
        "forge_id": "verified_2d_doodle",
        "profile_id": "profile_1"
    })

    images_manifest = {
        "schema_version": "1.0",
        "checkpoint": "10_anecdote_first",
        "content_hash": hashlib.sha256(content_text.encode("utf-8")).hexdigest(),
        "signature": "verified_reused_indie_doodles",
        "items": image_items
    }
    (OUT_IMAGES_DIR / "images.json").write_text(json.dumps(images_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    images_output = {
        "schema_version": "1.0",
        "job_id": "survivorship-bias-16x9",
        "module": "images",
        "revision": 10,
        "input_versions": {
            "content": hashlib.sha256(content_text.encode("utf-8")).hexdigest()
        },
        "payload": {
            "images": [it["path"] for it in image_items if it["image_id"] != "THUMBNAIL"],
            "thumbnail": "revisions/images/10_anecdote_first/THUMBNAIL_16x9.jpg"
        }
    }
    (OUT_IMAGES_DIR / "output.json").write_text(json.dumps(images_output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info(f"Built images manifest with {len(image_items)} items")

    # Symlink revisions/images/10 -> 10_anecdote_first
    symlink_path = RUN_DIR / "revisions/images/10"
    if symlink_path.is_symlink() or symlink_path.exists():
        symlink_path.unlink()
    symlink_path.symlink_to("10_anecdote_first")
    logger.info("Symlinked revisions/images/10 -> 10_anecdote_first")

    # Run Pilot checks
    p = Pilot(str(SYS_DIR))
    pilot_res = p.checks("survivorship-bias-16x9", "content", content_data)
    logger.info(f"Pilot checks for content returned: {pilot_res}")

    logger.info("Build completed successfully!")


if __name__ == "__main__":
    main()
