#!/usr/bin/env python3
"""Build Brief Revision 7, Content Revision 8, and Images Revision 11 for survivorship-bias-16x9.

High-Stakes Analytical Explainer (Phân Tích Thực Chiến) Framework:
1. Opening Hook (0–12s): "Tại sao những người chăm chỉ nhất... thường lại là những người bế tắc và nghèo nhất?"
2. Mechanism Layer 1: False Correlation (Mối tương quan giả - dậy sớm/đọc sách là vết đạn ở cánh; động cơ thật là vốn ngầm, đòn bẩy, quan hệ)
3. Mechanism Layer 2: The Data Trap (Abraham Wald 1943 trong 15-20s - toàn bộ nghĩa địa kẻ thất bại bị xóa sổ)
4. Mechanism Layer 3: Thực tế 1 - Trường học & Công sở (Cày cuốc 16h là công cụ giá rẻ nếu thiếu đòn bẩy)
5. Mechanism Layer 3: Thực tế 2 - Xã hội & Khởi nghiệp (Ảo tưởng dám liều mới giàu của kẻ trúng số)
6. Actionable Value: Bộ lọc 1 - Bộ lọc Nghĩa địa (Hỏi bao nhiêu người làm y hệt mà thất bại)
7. Actionable Value: Bộ lọc 2 - Bọc giáp Động cơ (Bọc giáp năng lực lõi và quỹ dự phòng tài chính 6-12 tháng)
8. Actionable Value: Bộ lọc 3 - Tư duy Trừ Lùi của Charlie Munger (Loại bỏ 3 việc chắc chắn dẫn đến phá sản)
9. Climax: Giữ mạng sống trước khi cất cánh (Bọc giáp tử huyệt, sống sót qua giông bão)
10. Outro: Bàn nước đàm đạo, TikTok Live kết nối chiều sâu, CTA thả tim/bình luận/follow
"""
import hashlib
import json
import logging
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content_contract import validate_brief, validate_content
from tools.script_diversity_linter import lint_script

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("build_analytical_v9")

RUN_DIR = SYS_DIR / "runs/survivorship-bias-16x9"
SRC_IMAGES_DIR = RUN_DIR / "revisions/images/8_with_outro"
OUT_IMAGES_DIR = RUN_DIR / "revisions/images/11_analytical"

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
            "Muốn thành công, trước hết phải tìm cách không bị thất bại.",
            "Tránh xa những quyết định dẫn đến thảm họa thay vì tìm kiếm sự xuất sắc."
        ]
    }
]

REQUIRED_POINTS = [
    {
        "id": "R01",
        "text": "Mở màn chấn động: Nghịch lý người chăm chỉ nhất thường bế tắc nhất, 90% sao chép thói quen người thành công bị kiệt sức và bóc tách lỗi ngụy biện bòn rút công sức."
    },
    {
        "id": "R02",
        "text": "Bóc tách cơ chế tầng 1 - Mối tương quan giả: Dậy sớm, tập gym chỉ là vết đạn vô hại ở cánh; động cơ cứu mạng thật sự là vốn ngầm, quan hệ và thời thế bị giấu kín."
    },
    {
        "id": "R03",
        "text": "Bóc tách cơ chế tầng 2 - Chiếc bẫy dữ liệu sống sót của Abraham Wald 1943: Truyền thông chỉ lấy dữ liệu từ kẻ sống sót, toàn bộ nghĩa địa của kẻ thất bại đã bị xóa sổ."
    },
    {
        "id": "R04",
        "text": "Bài toán thực tế 1 - Trường học và công sở: Cày cuốc 16 tiếng biến bạn thành công cụ giá rẻ nếu không có đòn bẩy và phương pháp đúng."
    },
    {
        "id": "R05",
        "text": "Bài toán thực tế 2 - Xã hội và khởi nghiệp: Ảo tưởng dám liều mới giàu và sự thật về hàng ngàn người dám liều sạt nghiệp biến mất trong im lặng."
    },
    {
        "id": "R06",
        "text": "Giá trị thực chiến - Bộ lọc 1 (Bộ lọc Nghĩa địa): Trước khi nghe lời khuyên, hãy hỏi có bao nhiêu người làm y hệt mà vẫn thất bại thảm hại."
    },
    {
        "id": "R07",
        "text": "Giá trị thực chiến - Bộ lọc 2 (Bọc giáp Động cơ): Bọc giáp cho năng lực lõi và quỹ dự phòng tài chính khẩn cấp trước khi bọc giáp cho thói quen bề nổi."
    },
    {
        "id": "R08",
        "text": "Giá trị thực chiến - Bộ lọc 3 (Tư duy Trừ Lùi của Charlie Munger): Loại bỏ 3 việc chắc chắn dẫn đến cái chết và phá sản trước khi nghĩ đến thành công."
    },
    {
        "id": "R09",
        "text": "Đòn kết liễu đanh thép: Dừng sao chép mù quáng, nhìn thấu nghĩa địa dưới đáy biển để bọc giáp cho tử huyệt và giữ mạng sống trước khi cất cánh."
    },
    {
        "id": "R10",
        "text": "Đoạn kết tri ân nhận thức người nghe, mời tham gia các buổi Live đàm đạo chiều sâu trên TikTok, kêu gọi thả tim, chia sẻ vết đạn và theo dõi kênh."
    }
]

SCENE_SPECS = [
    {
        "id": "SC01",
        "title": "Mở màn chấn động & Lỗi ngụy biện bòn rút công sức",
        "purpose": "Đặt câu hỏi trúng tim đen người chăm chỉ nhưng bế tắc, tạo độ tương phản gay gắt và hứa hẹn giá trị bóc tách bẫy tư duy để không bao giờ bị dắt mũi.",
        "narration": "Tại sao những người chăm chỉ nhất thường lại là những người bế tắc và nghèo nhất? Cày cuốc mười sáu tiếng mỗi ngày nhưng thu nhập vẫn giậm chân tại chỗ; chín mươi phần trăm những ai mù quáng sao chép thói quen của người thành công chỉ nhận về kiệt sức hoặc vỡ nợ. Video này sẽ bóc tách cho bạn một lỗi ngụy biện logic đang âm thầm bòn rút công sức của bạn mỗi ngày, và cách cài đặt lại Bộ lọc tư duy để không bao giờ bị dắt mũi nữa.",
        "requirements": ["R01"],
        "source_ids": [],
        "coverage_quote": "Tại sao những người chăm chỉ nhất thường lại là những người bế tắc và nghèo nhất?",
        "images": [
            {
                "id": "SC01_I1",
                "src_file": "SC01_I1_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: dramatic comic contrast! On the left, the white-head stickman in blue shirt (#3B82C4) collapses completely face-down onto a pile of crumpled papers and heavy books, tongue out, dizzy spiral eyes, cartoon sweat drops spraying. On the right, a giant flashy podium where another stickman raises a gleaming golden trophy with confetti raining down. Instant contrast between burnout and glory.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC01_I2",
                "src_file": "SC01_I2_16x9.jpg",
                "desc": "Raw 2D doodle on pale ice-blue (#CBE0E0) stage: a split horizontal conveyor journey. On the left side, a school classroom with a blackboard marked HỌC SINH GIỎI; on the right side, a corporate glass office building. The blue-shirt stickman marches forward carrying an oversized heavy backpack, staring ahead with naive wide round eyes.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC01_I3",
                "src_file": "SC01_I3_16x9.jpg",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: the blue-shirt stickman stares mesmerized with starry eyes at an enormous flashy roadside billboard. On the billboard, a smiling doodle stickman in a tuxedo steps out of a luxury sports car with a giant comic speech bubble: LÀM Y HỆT TÔI ĐI!",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC01_B1",
                "image_id": "SC01_I1",
                "quote": "Tại sao những người chăm chỉ nhất thường lại là những người bế tắc và nghèo nhất?",
                "effect": "punch_in"
            },
            {
                "id": "SC01_B2",
                "image_id": "SC01_I2",
                "quote": "Cày cuốc mười sáu tiếng mỗi ngày nhưng thu nhập vẫn giậm chân tại chỗ;",
                "effect": "pan_left"
            },
            {
                "id": "SC01_B3",
                "image_id": "SC01_I2",
                "quote": "chín mươi phần trăm những ai mù quáng sao chép thói quen của người thành công chỉ nhận về kiệt sức hoặc vỡ nợ.",
                "effect": "zoom_in"
            },
            {
                "id": "SC01_B4",
                "image_id": "SC01_I3",
                "quote": "Video này sẽ bóc tách cho bạn một lỗi ngụy biện logic đang âm thầm bòn rút công sức của bạn mỗi ngày, và cách cài đặt lại Bộ lọc tư duy để không bao giờ bị dắt mũi nữa.",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC02",
        "title": "Bóc tách cơ chế tầng 1: Mối tương quan giả",
        "purpose": "Bóc tách thói quen dậy sớm, đọc sách chỉ là vết đạn ở cánh, còn động cơ sống còn là vốn ngầm và đòn bẩy bị che giấu.",
        "narration": "Khi thấy một người giàu có, truyền thông thường tung hô: họ dậy từ năm giờ sáng, tập gym, đọc sách mỗi ngày. Nhưng đó chỉ là mối tương quan giả. Dậy sớm hay đọc sách chỉ là những vết đạn vô hại ở cánh. Thứ thực sự cứu mạng và đưa họ lên đỉnh cao là động cơ: vốn tự có, đòn bẩy gia đình, quan hệ ngầm hay thời thế, những thứ họ giấu nhẹm đi và không bao giờ kể trong các buổi diễn thuyết.",
        "requirements": ["R02"],
        "source_ids": [],
        "coverage_quote": "Thứ thực sự cứu mạng và đưa họ lên đỉnh cao là động cơ: vốn tự có, đòn bẩy gia đình, quan hệ ngầm hay thời thế,",
        "images": [
            {
                "id": "SC02_I1",
                "src_file": "SC07_I2_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: the blue-shirt stickman frantically buys superficial items: wearing a fake luxury necktie, holding a takeaway coffee, and pointing to a 4:00 AM alarm, with a black marker arrow labeled VẾT ĐẠN VÔ HẠI.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC02_I2",
                "src_file": "SC07_I3_16x9.jpg",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) stage: a deep two-layer comparison stage. The small top tier shows a smiling stickman holding a tiny sign BÍ QUYẾT TRÊN MẠNG; the massive bottom foundation shows a giant solid steel vault labeled VỐN DÀY and two clasped hands labeled QUAN HỆ.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC02_I3",
                "src_file": "SC07_I4_16x9.jpg",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: a successful influencer stickman stands behind a smiling stage mask holding a microphone, while behind his back is an enormous locked steel door concealing his family wealth and backup safety net.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC02_B1",
                "image_id": "SC02_I1",
                "quote": "Khi thấy một người giàu có, truyền thông thường tung hô: họ dậy từ năm giờ sáng, tập gym, đọc sách mỗi ngày.",
                "effect": "punch_in"
            },
            {
                "id": "SC02_B2",
                "image_id": "SC02_I2",
                "quote": "Nhưng đó chỉ là mối tương quan giả. Dậy sớm hay đọc sách chỉ là những vết đạn vô hại ở cánh.",
                "effect": "pan_right"
            },
            {
                "id": "SC02_B3",
                "image_id": "SC02_I3",
                "quote": "Thứ thực sự cứu mạng và đưa họ lên đỉnh cao là động cơ: vốn tự có, đòn bẩy gia đình, quan hệ ngầm hay thời thế,",
                "effect": "zoom_in"
            },
            {
                "id": "SC02_B4",
                "image_id": "SC02_I3",
                "quote": "những thứ họ giấu nhẹm đi và không bao giờ kể trong các buổi diễn thuyết.",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC03",
        "title": "Bóc tách cơ chế tầng 2: Chiếc bẫy dữ liệu sống sót (Abraham Wald 1943)",
        "purpose": "Dùng mô hình toán học Abraham Wald 1943 trong 15-20s chứng minh dữ liệu truyền thông chỉ lấy từ kẻ sống sót, toàn bộ nghĩa địa đã bị xóa sổ.",
        "narration": "Cơ chế này bắt nguồn từ một bài toán quân sự năm một chín bốn ba. Thấy máy bay trở về chi chít lỗ đạn ở cánh, các tướng lĩnh đòi bọc thép ngay vào cánh. Nhà toán học A-bra-ham Uôn đập bàn vạch trần: Các ông sai bét rồi! Chỗ cần bọc giáp là động cơ, nơi không có vết đạn nào. Bởi những chiếc trúng đạn vào động cơ đã nổ tung dưới đáy biển, không bao giờ quay về để được thống kê. Truyền thông hôm nay cũng vậy, bạn chỉ được nghe tiếng nói từ những kẻ may mắn sống sót.",
        "requirements": ["R03"],
        "source_ids": ["SRC01"],
        "coverage_quote": "Chỗ cần bọc giáp là động cơ, nơi không có vết đạn nào. Bởi những chiếc trúng đạn vào động cơ đã nổ tung dưới đáy biển, không bao giờ quay về để được thống kê.",
        "images": [
            {
                "id": "SC03_I1",
                "src_file": "SC06_I1_16x9.jpg",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) hangar stage: a 1943 military briefing room with two army generals in green peaked caps scratching their heads beside a large wall chalkboard showing a twin-engine bomber airplane blueprint.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC03_I2",
                "src_file": "SC06_I3_16x9.jpg",
                "desc": "Raw 2D doodle on pale ice-blue (#CBE0E0) stage: an eager general stickman holds a paintbrush and a heavy metal plate, trying to bolt heavy steel armor plates right onto the bullet-riddled outer wings of the plane.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC03_I3",
                "src_file": "SC06_I4_16x9.jpg",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: mathematician Abraham Wald with round glasses slams his hand down onto the drafting table, holding a black ruler pointing firmly at the clean, undamaged engines of the aircraft blueprint with an exclamation mark.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC03_I4",
                "src_file": "SC07_I1_16x9.jpg",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) underwater ocean floor stage: deep blue sea depths where a destroyed bomber plane with shattered smoking engines rests on the seabed surrounded by small cartoon rising bubbles.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC03_B1",
                "image_id": "SC03_I1",
                "quote": "Cơ chế này bắt nguồn từ một bài toán quân sự năm một chín bốn ba.",
                "effect": "punch_in"
            },
            {
                "id": "SC03_B2",
                "image_id": "SC03_I2",
                "quote": "Thấy máy bay trở về chi chít lỗ đạn ở cánh, các tướng lĩnh đòi bọc thép ngay vào cánh.",
                "effect": "pan_left"
            },
            {
                "id": "SC03_B3",
                "image_id": "SC03_I3",
                "quote": "Nhà toán học A-bra-ham Uôn đập bàn vạch trần: Các ông sai bét rồi! Chỗ cần bọc giáp là động cơ, nơi không có vết đạn nào.",
                "effect": "punch_in"
            },
            {
                "id": "SC03_B4",
                "image_id": "SC03_I4",
                "quote": "Bởi những chiếc trúng đạn vào động cơ đã nổ tung dưới đáy biển, không bao giờ quay về để được thống kê.",
                "effect": "zoom_in"
            },
            {
                "id": "SC03_B5",
                "image_id": "SC03_I4",
                "quote": "Truyền thông hôm nay cũng vậy, bạn chỉ được nghe tiếng nói từ những kẻ may mắn sống sót.",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC04",
        "title": "Bài toán thực tế 1: Trường học & Công sở",
        "purpose": "Phơi bày thực tế cày cuốc thâu đêm chỉ biến thành công cụ giá rẻ nếu không có đòn bẩy và phương pháp đúng đắn.",
        "narration": "Áp vào thực tế, cái bẫy này đang bòn rút bạn ra sao? Trong trường học và công sở, người ta ca ngợi thủ khoa và nhân viên tăng ca thâu đêm. Nhưng hệ thống chỉ tôn vinh người về đích đầu tiên, xóa sổ hàng trăm người cũng thức trắng đêm nhưng kiệt sức gục ngã. Nếu không có đòn bẩy và phương pháp đúng đắn, tăng ca cật lực thâu đêm chỉ biến bạn thành một công cụ giá rẻ. Bạn cắm đầu bắt chước sự chăm chỉ bề nổi của kẻ đứng trên bục vinh quang, mà không hề biết bản thân đang lao thẳng vào cái chết kiệt quệ.",
        "requirements": ["R04"],
        "source_ids": [],
        "coverage_quote": "Nếu không có đòn bẩy và phương pháp đúng đắn, tăng ca cật lực thâu đêm chỉ biến bạn thành một công cụ giá rẻ.",
        "images": [
            {
                "id": "SC04_I1",
                "src_file": "SC02_I1_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) classroom stage: a strict teacher stickman with round spectacles points a wooden stick at a shining valedictorian stickman wearing a golden laurel wreath, while the blue-shirt stickman in the front row stares nervously.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC04_I2",
                "src_file": "SC02_I2_16x9.jpg",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) night stage: the blue-shirt stickman sits at a crooked wooden study desk at 3:00 AM, giant alarm clock clattering, head steaming with exhaustion, dark circles under his eyes, buried beneath towering zigzag piles of math exercise books.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC04_I3",
                "src_file": "SC03_I2_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: deep pit below the winner's podium! A crowd of dozens of tired doodle stickmen with X-eyes and dizzy sweat drops are tumbled in a ditch beside banana peels and torn exercise notebooks, completely out of sight.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC04_I4",
                "src_file": "SC03_I3_16x9.jpg",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) stage: a dramatic theatrical spotlight beam shines down brightly on the single lone survivor standing tall, while 90% of the stage is in total black silhouette filled with shadowy fallen stickmen.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC04_B1",
                "image_id": "SC04_I1",
                "quote": "Áp vào thực tế, cái bẫy này đang bòn rút bạn ra sao?",
                "effect": "punch_in"
            },
            {
                "id": "SC04_B2",
                "image_id": "SC04_I1",
                "quote": "Trong trường học và công sở, người ta ca ngợi thủ khoa và nhân viên tăng ca thâu đêm.",
                "effect": "pan_left"
            },
            {
                "id": "SC04_B3",
                "image_id": "SC04_I2",
                "quote": "Nhưng hệ thống chỉ tôn vinh người về đích đầu tiên, xóa sổ hàng trăm người cũng thức trắng đêm nhưng kiệt sức gục ngã.",
                "effect": "pan_right"
            },
            {
                "id": "SC04_B4",
                "image_id": "SC04_I3",
                "quote": "Nếu không có đòn bẩy và phương pháp đúng đắn, tăng ca cật lực thâu đêm chỉ biến bạn thành một công cụ giá rẻ.",
                "effect": "zoom_in"
            },
            {
                "id": "SC04_B5",
                "image_id": "SC04_I4",
                "quote": "Bạn cắm đầu bắt chước sự chăm chỉ bề nổi của kẻ đứng trên bục vinh quang, mà không hề biết bản thân đang lao thẳng vào cái chết kiệt quệ.",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC05",
        "title": "Bài toán thực tế 2: Xã hội & Ảo tưởng dám liều mới giàu",
        "purpose": "Vạch trần các lời khuyên dạy làm giàu liều lĩnh là bán sự ảo tưởng của kẻ trúng số, hàng ngàn người sạt nghiệp biến mất trong im lặng.",
        "narration": "Bước ra ngoài đời không có đáp án mẫu, các chuyên gia tài chính bắt đầu bán cho bạn sự ảo tưởng. Lướt mạng xã hội đâu đâu cũng thấy hình mẫu hai mươi tuổi kiếm triệu đô, bỏ học làm giàu. Họ mở lớp dạy đời: Dám liều mới giàu! Hãy bước ra khỏi vùng an toàn! Nhiều người nghe bùi tai, nộp đơn nghỉ việc rồi trắng tay ôm nợ. Sự thật cay đắng là: những kẻ dám liều mà sạt nghiệp đã biến mất trong im lặng, không có micro, không có sân khấu nào chào đón họ.",
        "requirements": ["R05"],
        "source_ids": [],
        "coverage_quote": "Sự thật cay đắng là: những kẻ dám liều mà sạt nghiệp đã biến mất trong im lặng, không có micro, không có sân khấu nào chào đón họ.",
        "images": [
            {
                "id": "SC05_I1",
                "src_file": "SC04_I1_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: the blue-shirt stickman steps out through the school gates into a bustling chaotic concrete maze with confusing road signs pointing in four opposite directions and floating question marks.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC05_I2",
                "src_file": "SC04_I2_16x9.jpg",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: the blue-shirt stickman looks at his smartphone screen as giant comic popup notifications explode outwards: 20 TUỔI TRIỆU ĐÔ, BỎ HỌC LÀM CHỦ, X5 LƯƠNG with flying money bills.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC05_I3",
                "src_file": "SC04_I4_16x9.jpg",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) stage: the guru shouts through an oversized megaphone with a massive speech bubble: DÁM LIỀU MỚI GIÀU! In front of him, the gullible blue-shirt stickman gets pumped up, rolling up his sleeves ready to leap off a ledge.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC05_I4",
                "src_file": "SC05_I2_16x9.jpg",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) night stage: 6 months later, the stickman sits slumped on the floor of a barren room, holding an empty turned-out wallet with moths flying out, surrounded by a mountain of red bills stamped NỢ.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC05_B1",
                "image_id": "SC05_I1",
                "quote": "Bước ra ngoài đời không có đáp án mẫu, các chuyên gia tài chính bắt đầu bán cho bạn sự ảo tưởng.",
                "effect": "pan_left"
            },
            {
                "id": "SC05_B2",
                "image_id": "SC05_I2",
                "quote": "Lướt mạng xã hội đâu đâu cũng thấy hình mẫu hai mươi tuổi kiếm triệu đô, bỏ học làm giàu.",
                "effect": "punch_in"
            },
            {
                "id": "SC05_B3",
                "image_id": "SC05_I3",
                "quote": "Họ mở lớp dạy đời: Dám liều mới giàu! Hãy bước ra khỏi vùng an toàn! Nhiều người nghe bùi tai, nộp đơn nghỉ việc rồi trắng tay ôm nợ.",
                "effect": "zoom_in"
            },
            {
                "id": "SC05_B4",
                "image_id": "SC05_I4",
                "quote": "Sự thật cay đắng là: những kẻ dám liều mà sạt nghiệp đã biến mất trong im lặng, không có micro, không có sân khấu nào chào đón họ.",
                "effect": "punch_in"
            }
        ]
    },
    {
        "id": "SC06",
        "title": "Bộ lọc phòng thủ 1: Bộ lọc Nghĩa địa",
        "purpose": "Trao lợi ích thực chiến 1: trước khi tin lời khuyên, hãy hỏi có bao nhiêu người làm y hệt mà thất bại, nhìn nghĩa địa trước khi nhìn bục vinh quang.",
        "narration": "Để không bị dắt mũi, đây là ba bộ lọc tư duy bạn phải cài đặt ngay hôm nay. Bộ lọc thứ nhất: Bộ lọc Nghĩa địa. Trước khi tin bất kỳ lời khuyên hay bí quyết đổi đời nào, hãy dừng lại và hỏi: Có bao nhiêu người đã làm y hệt cách này mà vẫn thất bại thảm hại? Hãy nhìn vào nghĩa địa của những kẻ sạt nghiệp trước khi nhìn vào bục vinh quang. Nếu tỷ lệ tử vong là chín mươi chín phần trăm, đó không phải cơ hội, mà là trò cò quay may rủi.",
        "requirements": ["R06"],
        "source_ids": [],
        "coverage_quote": "Hãy nhìn vào nghĩa địa của những kẻ sạt nghiệp trước khi nhìn vào bục vinh quang.",
        "images": [
            {
                "id": "SC06_I1",
                "src_file": "SC05_I3_16x9.jpg",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) stage: a vast silent graveyard under a crescent moon, dotted with dozens of simple wooden cross markers where bankrupt stickmen sit silently in the dark with head in knees.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC06_I2",
                "src_file": "SC05_I4_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: an empty dimly-lit auditorium stage with a lone cold microphone on a stand, its cable unplugged on the wooden floor, with zero audience and zero book in sight.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC06_I3",
                "src_file": "SC09_I2_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: the stickman stands holding a magnifying glass, looking past a glowing TV screen showing an influencer, peering down into the deep blue ocean where sunken airplanes rest peacefully.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC06_B1",
                "image_id": "SC06_I1",
                "quote": "Để không bị dắt mũi, đây là ba bộ lọc tư duy bạn phải cài đặt ngay hôm nay. Bộ lọc thứ nhất: Bộ lọc Nghĩa địa.",
                "effect": "punch_in"
            },
            {
                "id": "SC06_B2",
                "image_id": "SC06_I2",
                "quote": "Trước khi tin bất kỳ lời khuyên hay bí quyết đổi đời nào, hãy dừng lại và hỏi: Có bao nhiêu người đã làm y hệt cách này mà vẫn thất bại thảm hại?",
                "effect": "pan_left"
            },
            {
                "id": "SC06_B3",
                "image_id": "SC06_I3",
                "quote": "Hãy nhìn vào nghĩa địa của những kẻ sạt nghiệp trước khi nhìn vào bục vinh quang.",
                "effect": "zoom_in"
            },
            {
                "id": "SC06_B4",
                "image_id": "SC06_I3",
                "quote": "Nếu tỷ lệ tử vong là chín mươi chín phần trăm, đó không phải cơ hội, mà là trò cò quay may rủi.",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC07",
        "title": "Bộ lọc phòng thủ 2: Bọc giáp Động cơ",
        "purpose": "Trao lợi ích thực chiến 2: bọc giáp cho năng lực lõi và quỹ dự phòng tài chính 6-12 tháng trước khi bọc giáp cho thói quen bề nổi.",
        "narration": "Bộ lọc thứ hai: Bọc giáp Động cơ. Đừng tiếp tục bọc giáp cho những vết đạn vô hại ở cánh như mua đồ hiệu hay giả lập cuộc sống sang chảnh. Động cơ sống còn của bạn là gì? Đó là năng lực chuyên môn không thể thay thế, và một quỹ dự phòng tài chính đủ sống ít nhất sáu đến mười hai tháng. Bọc giáp thật vững cho động cơ trước khi bạn nghĩ đến chuyện cất cánh, để dù thị trường có rung lắc, bạn vẫn an toàn đứng vững.",
        "requirements": ["R07"],
        "source_ids": [],
        "coverage_quote": "Đó là năng lực chuyên môn không thể thay thế, và một quỹ dự phòng tài chính đủ sống ít nhất sáu đến mười hai tháng.",
        "images": [
            {
                "id": "SC07_I1",
                "src_file": "SC09_I1_16x9.jpg",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) stage: the blue-shirt stickman looks into a full-length dressing mirror and sees himself as an exhausted puppet with tangled strings, realizing blind imitation only drains his soul.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC07_I2",
                "src_file": "SC09_I3_16x9.jpg",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) stage: the stickman confidently uses a wrench to bolt a thick solid steel armor plate over his chest engine, eyes determined and resolute, standing solidly on the ground.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC07_I3",
                "src_file": "SC08_I4_16x9.jpg",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) stage: the blue-shirt stickman stands calm and secure behind a heavy steel shield wall while dark economic storm clouds rain lightning bolts outside, safe and completely unshakeable.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC07_B1",
                "image_id": "SC07_I1",
                "quote": "Bộ lọc thứ hai: Bọc giáp Động cơ. Đừng tiếp tục bọc giáp cho những vết đạn vô hại ở cánh như mua đồ hiệu hay giả lập cuộc sống sang chảnh.",
                "effect": "punch_in"
            },
            {
                "id": "SC07_B2",
                "image_id": "SC07_I2",
                "quote": "Động cơ sống còn của bạn là gì?",
                "effect": "pan_right"
            },
            {
                "id": "SC07_B3",
                "image_id": "SC07_I2",
                "quote": "Đó là năng lực chuyên môn không thể thay thế, và một quỹ dự phòng tài chính đủ sống ít nhất sáu đến mười hai tháng.",
                "effect": "zoom_in"
            },
            {
                "id": "SC07_B4",
                "image_id": "SC07_I3",
                "quote": "Bọc giáp thật vững cho động cơ trước khi bạn nghĩ đến chuyện cất cánh, để dù thị trường có rung lắc, bạn vẫn an toàn đứng vững.",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC08",
        "title": "Bộ lọc phòng thủ 3: Tư duy Trừ Lùi của Charlie Munger",
        "purpose": "Trao lợi ích thực chiến 3: loại bỏ 3 việc chắc chắn dẫn đến cái chết/phá sản trước khi nghĩ đến thành công.",
        "narration": "Bộ lọc thứ ba: Tư duy Trừ Lùi của huyền thoại Chác-li Măng-gơ. Ông từng nói: Muốn đến đích an toàn, việc đầu tiên là tìm xem nơi nào sẽ làm bạn chết, rồi đừng bao giờ đến đó. Thay vì đi tìm công thức làm giàu sau một đêm, hãy lập danh sách ba việc chắc chắn khiến bạn phá sản: vay nợ lãi cao, tất tay một canh bạc, và ảo tưởng năng lực. Kiên quyết loại bỏ ba điều đó, bạn đã tự cứu mình khỏi chín mươi phần trăm bi kịch của người đời.",
        "requirements": ["R08"],
        "source_ids": ["SRC02"],
        "coverage_quote": "Muốn đến đích an toàn, việc đầu tiên là tìm xem nơi nào sẽ làm bạn chết, rồi đừng bao giờ đến đó.",
        "images": [
            {
                "id": "SC08_I1",
                "src_file": "SC08_I1_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: an elderly wise stickman with round glasses (Charlie Munger) points with a walking stick at a sharp cliff edge where a large red skull sign warns: ĐỪNG NHẢY XUỐNG VỰC!",
                "shot_type": "full_scene"
            },
            {
                "id": "SC08_I2",
                "src_file": "SC08_I2_16x9.jpg",
                "desc": "Raw 2D doodle on pale ice-blue (#CBE0E0) stage: a giant wooden checklist board on which the stickman crosses out fatal traps with bold red X marks: VAY LÃI CAO (crossed out), TẤT TAY MỘT CỬA (crossed out), ẢO TƯỞNG LÀM GIÀU (crossed out).",
                "shot_type": "full_scene"
            },
            {
                "id": "SC08_I3",
                "src_file": "SC08_I3_16x9.jpg",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: a gambler stickman reaching hungrily for a shiny gold pot perched precariously over a deep pit, with a giant red warning question mark hovering above.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC08_B1",
                "image_id": "SC08_I1",
                "quote": "Bộ lọc thứ ba: Tư duy Trừ Lùi của huyền thoại Chác-li Măng-gơ.",
                "effect": "punch_in"
            },
            {
                "id": "SC08_B2",
                "image_id": "SC08_I1",
                "quote": "Ông từng nói: Muốn đến đích an toàn, việc đầu tiên là tìm xem nơi nào sẽ làm bạn chết, rồi đừng bao giờ đến đó.",
                "effect": "pan_left"
            },
            {
                "id": "SC08_B3",
                "image_id": "SC08_I2",
                "quote": "Thay vì đi tìm công thức làm giàu sau một đêm, hãy lập danh sách ba việc chắc chắn khiến bạn phá sản: vay nợ lãi cao, tất tay một canh bạc, và ảo tưởng năng lực.",
                "effect": "zoom_in"
            },
            {
                "id": "SC08_B4",
                "image_id": "SC08_I3",
                "quote": "Kiên quyết loại bỏ ba điều đó, bạn đã tự cứu mình khỏi chín mươi phần trăm bi kịch của người đời.",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC09",
        "title": "Đòn kết liễu: Giữ mạng sống trước khi cất cánh",
        "purpose": "Đòn kết liễu đanh thép: dừng sao chép mù quáng, nhìn thấu nghĩa địa dưới đáy biển để bọc giáp tử huyệt, sống sót trước khi thành công.",
        "narration": "Bắt chước người chiến thắng chỉ biến bạn thành một bản sao mệt mỏi. Lần tới, khi thấy ai đó khoe mẽ hào quang rực rỡ, đừng vội cắm đầu làm theo. Hãy tự hỏi những kẻ thất bại đang ở đâu dưới đáy biển. Bọc giáp cho tử huyệt của mình trước, giữ cho mình sống sót đã, rồi thành công mới thực sự đến lượt bạn cất cánh.",
        "requirements": ["R09"],
        "source_ids": ["SRC01"],
        "coverage_quote": "Bọc giáp cho tử huyệt của mình trước, giữ cho mình sống sót đã, rồi thành công mới thực sự đến lượt bạn cất cánh.",
        "images": [
            {
                "id": "SC09_I1",
                "src_file": "SC01_I1_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: a crude 2D propeller bomber plane sits on the runway, its wide wings and fuselage covered in dozens of prominent red marker bullet hole dots.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC09_I2",
                "src_file": "SC02_I3_16x9.jpg",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: the stickman lies limp like a noodle across the wooden desk, face flat on a crumpled paper marked 4/10 with big red question marks floating above his head, body trembling with fatigue.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC09_I3",
                "src_file": "SC09_I4_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) sunrise stage: the sturdy 2D propeller airplane with gleaming armored engines takes off smoothly into the bright open sky, soaring high above the clouds toward the morning sun.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC09_B1",
                "image_id": "SC09_I1",
                "quote": "Bắt chước người chiến thắng chỉ biến bạn thành một bản sao mệt mỏi.",
                "effect": "punch_in"
            },
            {
                "id": "SC09_B2",
                "image_id": "SC09_I2",
                "quote": "Lần tới, khi thấy ai đó khoe mẽ hào quang rực rỡ, đừng vội cắm đầu làm theo.",
                "effect": "pan_left"
            },
            {
                "id": "SC09_B3",
                "image_id": "SC09_I2",
                "quote": "Hãy tự hỏi những kẻ thất bại đang ở đâu dưới đáy biển.",
                "effect": "zoom_in"
            },
            {
                "id": "SC09_B4",
                "image_id": "SC09_I3",
                "quote": "Bọc giáp cho tử huyệt của mình trước, giữ cho mình sống sót đã, rồi thành công mới thực sự đến lượt bạn cất cánh.",
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
        "images": [
            {
                "id": "SC10_I1",
                "src_file": "SC10_I1_16x9.jpg",
                "desc": "Raw 2D Vietnamese indie doodle explainer illustration on a warm paper-cream (#F8F0DC) stage with bold unpolished black marker contours (#000000). The white bald circle-head stickman in a solid cerulean-blue (#3B82C4) shirt sits comfortably behind a simple rustic wooden table, leaning forward with a warm, thoughtful smile, holding a steaming ceramic mug. Above hangs a single gentle doodle ceiling bulb glowing with soft hand-drawn rays. Intimate, calm, intellectual atmosphere.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC10_I2",
                "src_file": "SC10_I2_16x9.jpg",
                "desc": "Raw 2D Vietnamese indie doodle explainer illustration on a pale ice-blue (#CBE0E0) stage with crooked black contours (#000000). The stickman speaks calmly into a classic vintage desktop broadcast microphone. Surrounding the stage are multiple friendly doodle stickmen avatars appearing in round speech bubbles with question marks and bold exclamation marks, showing an engaging live community roundtable discussion. No flashy neon UI, purely organic conversational doodle setting.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC10_I3",
                "src_file": "SC10_I3_16x9.jpg",
                "desc": "Raw 2D Vietnamese indie doodle explainer illustration on a soft sage-green (#93A88C) stage with loose black marker lines (#000000). The blue-shirt stickman waves one hand warmly in a friendly farewell gesture while holding a small notebook in the other. Beside him are three clean hand-drawn doodle accent icons: a warm crimson-red heart (#EF4444), a small thought comment bubble, and a minimal bookmark ribbon. Clean, respectful, memorable closure.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC10_B1",
                "image_id": "SC10_I1",
                "quote": "Nếu bạn đã kiên nhẫn đồng hành cùng mình đến tận giây phút này, có lẽ bạn cũng nhận ra: nhận diện được thiên kiến chỉ là bước đầu.",
                "effect": "punch_in"
            },
            {
                "id": "SC10_B2",
                "image_id": "SC10_I1",
                "quote": "Rèn được bản lĩnh trừ lùi trong đời thực mới là thứ cần mài giũa mỗi ngày.",
                "effect": "zoom_in"
            },
            {
                "id": "SC10_B3",
                "image_id": "SC10_I2",
                "quote": "Dạo gần đây, TikTok đang khuyến khích chúng mình mở những không gian phát trực tiếp.",
                "effect": "pan_left"
            },
            {
                "id": "SC10_B4",
                "image_id": "SC10_I2",
                "quote": "Sắp tới, mình sẽ có những buổi Live ngồi lại cùng bạn, mổ xẻ những góc khuất và những cú vấp ngã chưa từng được kể trong công việc lẫn cuộc sống của chính các bạn.",
                "effect": "zoom_in"
            },
            {
                "id": "SC10_B5",
                "image_id": "SC10_I3",
                "quote": "Nếu góc nhìn hôm nay giúp bạn bớt đi một ảo tưởng, hãy thả một tim, để lại câu chuyện về vết đạn bạn từng nếm trải dưới phần bình luận, và theo dõi kênh để cùng rèn luyện tư duy mỗi ngày.",
                "effect": "pan_right"
            },
            {
                "id": "SC10_B6",
                "image_id": "SC10_I3",
                "quote": "Hẹn gặp bạn trong buổi Live đàm đạo gần nhất.",
                "effect": "zoom_out"
            }
        ]
    }
]


def build_brief() -> dict:
    return {
        "schema_version": "3.0",
        "topic": "Bẫy Người Sống Sót (Survivorship Bias) & Tư Duy Trừ Lùi",
        "audience": "Người trẻ đi làm, người khởi nghiệp, người bước từ trường lớp ra xã hội tại Việt Nam",
        "goal": "Phân tích thực chiến lỗi ngụy biện Bẫy Người Sống Sót từ nghịch lý người chăm chỉ nhất thường bế tắc nhất, bóc tách mối tương quan giả, chiếc bẫy dữ liệu của Abraham Wald 1943, hai bài toán thực tế công sở/khởi nghiệp và trao 3 bộ lọc phòng thủ thực chiến cùng Tư duy Trừ Lùi của Charlie Munger.",
        "video_type": "research_explainer",
        "duration": {
            "min_seconds": 120.0,
            "max_seconds": 240.0
        },
        "scene_count": 10,
        "required_points": REQUIRED_POINTS,
        "language": "vi",
        "tone": "Điềm đạm, ấm áp, thông tuệ, gần gũi, đanh thép, không lê thê",
        "style": STYLE_170,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": SOURCES,
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "vi",
                "subtitles": False,
                "voice": "VietNarrator",
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Bóc tách bản chất thực chiến Bẫy Người Sống Sót bằng nghịch lý người chăm chỉ mở màn, giải mã mối tương quan giả, mô hình toán học Abraham Wald 1943, bài toán trường học/khởi nghiệp và trao 3 bộ lọc phòng thủ cùng Tư duy Trừ Lùi."
            ],
            "avoid": [
                "Tránh lối diễn đạt giáo điều, sáo rỗng hoặc thuật ngữ hàn lâm không giải thích.",
                "Tránh clipart 3D/vector mượt mà của AI; dùng 100% hình vẽ doodle thủ công Nguệch Ngoạc / Vẽ Vời."
            ],
            "prior_knowledge": "Không đòi hỏi kiến thức chuyên sâu từ trước.",
            "pacing": "Nhịp nói dồn dập, sắc bén, Conversational Essayist, triệt tiêu dead-air.",
            "domain_requirements": [],
            "assumptions": [
                "Mỗi phân cảnh được cân chỉnh theo công thức âm học P_tail và dung sai drift <= 0.3s."
            ],
            "text_style": {
                "font": "sans-serif rõ nét, cùng kiểu và độ đậm xuyên suốt",
                "color": "#172033",
                "outline": "nền sáng tương phản",
                "size": "dễ đọc trên màn hình ngang (khung 16:9)",
                "placement": "cách mép ít nhất 10%; bố cục ngang thoáng, không ép lề dọc điện thoại"
            },
            "speech_rates": {
                "vi": {
                    "units_per_second": 4.0,
                    "uncertainty": 0.15,
                    "source": "Acoustic calibrated cadence"
                },
                "en": {
                    "units_per_second": 3.2,
                    "uncertainty": 0.15,
                    "source": "Acoustic calibrated cadence"
                }
            }
        },
        "conversational_facts": True,
        "packaging": {
            "youtube_title": "Bẫy Người Sống Sót: Sao Chép Thành Công Là Vô Nghĩa",
            "thumbnail_spec": {
                "visual_hook": "Raw freehand 2D Vietnamese indie doodle on a flat slate-navy (#2E4361) stage: a white-head doodle stickman in a casual cerulean blue shirt (#3B82C4) looks up at one golden trophy inside a bright yellow spotlight cone while standing above a deep ocean trench filled with sunken propeller bomber planes",
                "text_overlay": "BẪY NGƯỜI SỐNG SÓT",
                "contrast_pair": "Ánh đèn kẻ thắng cuộc vs. Đáy biển người thất bại",
                "thumbnail_prompt": "16:9 YouTube thumbnail poster in raw freehand 2D Vietnamese indie doodle style on a flat slate-navy (#2E4361) stage with bold pitch-black (#000000) marker contours and 100% flat MS-Paint paint-bucket fills. Focal subject: Raw freehand 2D Vietnamese indie doodle on a flat slate-navy (#2E4361) stage: a white-head doodle stickman in a casual cerulean blue shirt (#3B82C4) looks up at one golden trophy inside a bright yellow spotlight cone while standing above a deep ocean trench filled with sunken propeller bomber planes. Contrast: Ánh đèn kẻ thắng cuộc vs. Đáy biển người thất bại. Top-center bold hand-drawn golden-yellow (#FACC15) uppercase Vietnamese lettering 'BẪY NGƯỜI SỐNG SÓT' with thick pitch-black (#000000) marker outline, zero drop shadow.",
                "layout_mode": "integrated_poster",
                "typography_style": "Bold hand-drawn golden-yellow (#FACC15) uppercase poster lettering with thick pitch-black (#000000) marker outline"
            },
            "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": [
                "bẫy người sống sót",
                "thiên kiến kẻ sống sót",
                "survivorship bias",
                "abraham wald máy bay 1943",
                "tư duy trừ lùi",
                "tri thức tiêu cực",
                "charlie munger",
                "tư duy phản biện"
            ]
        },
        "youtube_title": "Bẫy Người Sống Sót: Sao Chép Thành Công Là Vô Nghĩa",
        "thumbnail_spec": {
            "visual_hook": "Raw freehand 2D Vietnamese indie doodle on a flat slate-navy (#2E4361) stage: a white-head doodle stickman in a casual cerulean blue shirt (#3B82C4) looks up at one golden trophy inside a bright yellow spotlight cone while standing above a deep ocean trench filled with sunken propeller bomber planes",
            "text_overlay": "BẪY NGƯỜI SỐNG SÓT",
            "contrast_pair": "Ánh đèn kẻ thắng cuộc vs. Đáy biển người thất bại",
            "thumbnail_prompt": "16:9 YouTube thumbnail poster in raw freehand 2D Vietnamese indie doodle style on a flat slate-navy (#2E4361) stage with bold pitch-black (#000000) marker contours and 100% flat MS-Paint paint-bucket fills. Focal subject: Raw freehand 2D Vietnamese indie doodle on a flat slate-navy (#2E4361) stage: a white-head doodle stickman in a casual cerulean blue shirt (#3B82C4) looks up at one golden trophy inside a bright yellow spotlight cone while standing above a deep ocean trench filled with sunken propeller bomber planes. Contrast: Ánh đèn kẻ thắng cuộc vs. Đáy biển người thất bại. Top-center bold hand-drawn golden-yellow (#FACC15) uppercase Vietnamese lettering 'BẪY NGƯỜI SỐNG SÓT' with thick pitch-black (#000000) marker outline, zero drop shadow.",
            "layout_mode": "integrated_poster",
            "typography_style": "Bold hand-drawn golden-yellow (#FACC15) uppercase poster lettering with thick pitch-black (#000000) marker outline"
        },
        "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": [
            "bẫy người sống sót",
            "thiên kiến kẻ sống sót",
            "survivorship bias",
            "abraham wald máy bay 1943",
            "tư duy trừ lùi",
            "tri thức tiêu cực",
            "charlie munger",
            "tư duy phản biện"
        ],
        "human_editorial": {
            "editorial_stance": "Thành công bền vững trong các cuộc chơi nhiều biến số không đến từ việc sao chép thói quen bề nổi của kẻ thắng cuộc, mà đến từ Tư duy Trừ Lùi (Tri Thức Tiêu Cực): khảo sát dữ liệu dưới đáy biển của những người bỏ cuộc và bọc thép cho tử huyệt tài chính cá nhân.",
            "topic_dilemmas": [
                "Mâu thuẫn giữa những công thức đổi đời hào nhoáng trên mạng xã hội với thực tế hàng nghìn người cày cuốc y hệt nhưng mất trắng vốn liếng.",
                "Ảo giác nhân quả khi nhìn vào một người thắng cuộc đứng dưới ánh đèn mà bỏ quên nghĩa địa của những kẻ thất bại trong im lặng."
            ],
            "author_raw_input": "Bóc tách thực chiến Bẫy Người Sống Sót từ câu hỏi mở màn chấn động, phân tích mối tương quan giả, bẫy dữ liệu Abraham Wald 1943, bài toán trường học và khởi nghiệp, cùng 3 bộ lọc phòng thủ thực chiến.",
            "dynamic_questions": [
                "Vì sao người chăm chỉ nhất thường lại là người nghèo và bế tắc nhất?",
                "Đâu là vết đạn vô hại ở cánh, đâu là động cơ sống còn ngoài đời thực?",
                "Làm sao cài đặt 3 bộ lọc phòng thủ để không bao giờ bị dắt mũi?"
            ],
            "expanded_content_ideas": [
                {
                    "angle_type": "commentary",
                    "idea_summary": "Mở màn chấn động với nghịch lý người chăm chỉ và bóc tách lỗi ngụy biện bòn rút công sức.",
                    "narrative_integration": "Triển khai tại SC01 và SC02."
                },
                {
                    "angle_type": "analysis",
                    "idea_summary": "Bóc tách bẫy dữ liệu Abraham Wald 1943 và 2 bài toán thực tế công sở, khởi nghiệp.",
                    "narrative_integration": "Triển khai tại SC03 đến SC05."
                },
                {
                    "angle_type": "evaluation",
                    "idea_summary": "Bộ 3 bộ lọc phòng thủ thực chiến và Tư duy Trừ Lùi của Charlie Munger.",
                    "narrative_integration": "Triển khai tại SC06 đến SC10."
                }
            ]
        },
        "visual_pacing_profile": "full_frame_v1",
        "enforce_phonetic_gate": True
    }


SCENE_SETTINGS = {
    "SC01": "Flat warm paper-cream (#F8F0DC) and apricot-peach (#F2B88B) 2D orthographic comic stage.",
    "SC02": "Flat warm paper-cream (#F8F0DC) and apricot-peach (#F2B88B) 2D orthographic comparison stage.",
    "SC03": "Flat soft sage-green (#93A88C) and slate-navy (#2E4361) 2D orthographic military and ocean stage.",
    "SC04": "Flat warm paper-cream (#F8F0DC) and slate-navy (#2E4361) 2D orthographic study stage.",
    "SC05": "Flat warm paper-cream (#F8F0DC) and apricot-peach (#F2B88B) 2D orthographic city street stage.",
    "SC06": "Flat slate-navy (#2E4361) and warm paper-cream (#F8F0DC) 2D orthographic graveyard stage.",
    "SC07": "Flat slate-navy (#2E4361) and soft sage-green (#93A88C) 2D orthographic armor stage.",
    "SC08": "Flat warm paper-cream (#F8F0DC) and pale ice-blue (#CBE0E0) 2D orthographic strategy stage.",
    "SC09": "Flat warm paper-cream (#F8F0DC) and apricot-peach (#F2B88B) 2D orthographic takeoff stage.",
    "SC10": "Flat warm paper-cream (#F8F0DC), pale ice-blue (#CBE0E0), and soft sage-green (#93A88C) 2D orthographic studio stage."
}


def build_content(brief_rev: int, brief_hash: str, brief: dict) -> dict:
    content_scenes = []
    coverage = []

    for sc in SCENE_SPECS:
        sc_id = sc["id"]
        narration = sc["narration"]
        reqs = sc["requirements"]
        src_ids = sc["source_ids"]

        images = []
        for img in sc["images"]:
            images.append({
                "id": img["id"],
                "description": img["desc"],
                "character_ids": ["CH01"],
                "based_on": None,
                "preserve": "",
                "change": img["desc"],
                "reason": "Show the concrete object, comparison, or action at its spoken anchor.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": img["shot_type"],
                "has_character": True,
                "explanation": {
                    "quote": sc["coverage_quote"],
                    "relation": "context",
                    "source_terms": [sc["coverage_quote"].split()[-1].strip(".,!?:;")],
                    "visual_terms": [img["desc"][:40]]
                }
            })

        beats = []
        for b in sc["beats"]:
            quote = b["quote"]
            assert quote in narration, f"Quote {quote!r} not found in narration of {sc_id}"
            beats.append({
                "id": b["id"],
                "image_id": b["image_id"],
                "purpose": sc["purpose"],
                "anchor": {
                    "vi": {
                        "quote": quote,
                        "occurrence": 1
                    }
                },
                "effect": b["effect"],
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
            "scene_id": "SC03",
            "quote": "Chỗ cần bọc giáp là động cơ, nơi không có vết đạn nào.",
            "language": "vi",
            "source_id": "SRC01",
            "fact": "Cần bọc thép vào vị trí máy bay không có lỗ đạn."
        },
        {
            "scene_id": "SC03",
            "quote": "Bởi những chiếc trúng đạn vào động cơ đã nổ tung dưới đáy biển, không bao giờ quay về để được thống kê.",
            "language": "vi",
            "source_id": "SRC01",
            "fact": "Những chiếc máy bay trúng đạn vào động cơ và buồng lái không thể quay về."
        },
        {
            "scene_id": "SC08",
            "quote": "Muốn đến đích an toàn, việc đầu tiên là tìm xem nơi nào sẽ làm bạn chết, rồi đừng bao giờ đến đó.",
            "language": "vi",
            "source_id": "SRC02",
            "fact": "Muốn thành công, trước hết phải tìm cách không bị thất bại."
        },
        {
            "scene_id": "SC08",
            "quote": "lập danh sách ba việc chắc chắn khiến bạn phá sản: vay nợ lãi cao, tất tay một canh bạc, và ảo tưởng năng lực.",
            "language": "vi",
            "source_id": "SRC02",
            "fact": "Tránh xa những quyết định dẫn đến thảm họa thay vì tìm kiếm sự xuất sắc."
        }
    ]

    revision_response = [
        {
            "request_id": "R01",
            "status": "addressed",
            "explanation": "Tái cấu trúc 100% video theo khung High-Stakes Analytical Explainer (Phân Tích Thực Chiến), mở màn bằng nghịch lý người chăm chỉ bế tắc nhất, bóc tách mối tương quan giả, bẫy dữ liệu Abraham Wald 1943 và 3 bộ lọc phòng thủ thực chiến.",
            "scene_ids": ["SC01", "SC02", "SC03", "SC04", "SC05", "SC06", "SC07", "SC08", "SC09", "SC10"]
        }
    ]

    return {
        "schema_version": "3.0",
        "brief_revision": brief_rev,
        "brief_hash": brief_hash,
        "topic": brief["topic"],
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [r["text"] for r in brief["required_points"]],
        "characters": CHARACTERS,
        "scenes": content_scenes,
        "coverage": coverage,
        "outline": outline,
        "claims": claims,
        "revision_response": revision_response,
        "open_questions": []
    }


def main():
    logger.info("Building Analytical Explainer v9...")

    # 1. Build Brief Revision 7
    brief = build_brief()
    validate_brief(str(SYS_DIR), brief)
    logger.info("Brief passed validation!")

    brief_bytes = json.dumps(brief, ensure_ascii=False, indent=2).encode("utf-8")
    brief_hash = hashlib.sha256(brief_bytes).hexdigest()
    brief_rev = 7
    brief_path = RUN_DIR / f"briefs/{brief_rev}.json"
    brief_path.write_bytes(brief_bytes)
    logger.info(f"Wrote {brief_path} (hash: {brief_hash[:16]}...)")

    # 2. Build Content Revision 8
    content = build_content(brief_rev, brief_hash, brief)
    validate_content(str(SYS_DIR), brief, brief_rev, brief_hash, content)
    logger.info("Content passed contract validation!")

    # 3. Lint Script Diversity
    lint_report = lint_script(content["scenes"], characters=CHARACTERS, style=STYLE_170)
    logger.info(f"Script diversity linter violations: {len(lint_report.get('violations', []))}")
    if lint_report.get("violations"):
        for v in lint_report["violations"]:
            logger.error(f"Linter violation: {v}")
        raise ValueError(f"Script diversity linter failed with {len(lint_report['violations'])} violations!")
    logger.info("Script diversity linter passed with flying colors!")

    content_dir = RUN_DIR / "revisions/content/8"
    content_dir.mkdir(parents=True, exist_ok=True)
    content_path = content_dir / "content.json"
    content_path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Wrote {content_path}")

    # Also write outline.json and script.json for pipeline consistency
    outline = {
        "schema_version": "2.0",
        "scenes": [
            {
                "id": s["id"],
                "title": s["title"],
                "purpose": s["purpose"],
                "requirements": s["requirements"]
            }
            for s in content["scenes"]
        ]
    }
    (content_dir / "outline.json").write_text(json.dumps(outline, ensure_ascii=False, indent=2), encoding="utf-8")

    script = {
        "schema_version": "2.0",
        "scenes": [
            {
                "id": s["id"],
                "narration": s["narration"]
            }
            for s in content["scenes"]
        ]
    }
    (content_dir / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")

    # 4. Assemble Images Revision 11
    logger.info(f"Assembling Images Revision 11 in {OUT_IMAGES_DIR}...")
    OUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    image_items = []
    seen_images = set()
    for s in SCENE_SPECS:
        for img in s["images"]:
            img_id = img["id"]
            if img_id in seen_images:
                continue
            seen_images.add(img_id)
            dst_name = f"{img_id}_16x9.jpg"
            src_file = SRC_IMAGES_DIR / img["src_file"]
            dst_file = OUT_IMAGES_DIR / dst_name
            if not src_file.exists():
                raise FileNotFoundError(f"Missing source image: {src_file}")
            shutil.copy2(src_file, dst_file)

            # Copy sidecar json if exists
            src_json = src_file.with_suffix(".json")
            if src_json.exists():
                shutil.copy2(src_json, dst_file.with_suffix(".json"))

            # Calculate sha256
            sha = hashlib.sha256(dst_file.read_bytes()).hexdigest()
            image_items.append({
                "scene_id": s["id"],
                "path": f"revisions/images/11_analytical/{dst_name}",
                "prompt": img["desc"],
                "source": "google-flow-browser",
                "sha256": sha,
                "image_id": img_id,
                "ratio": "16:9"
            })

    # Also copy THUMBNAIL_16x9.jpg
    thumb_src = SRC_IMAGES_DIR / "THUMBNAIL_16x9.jpg"
    thumb_dst = OUT_IMAGES_DIR / "THUMBNAIL_16x9.jpg"
    if thumb_src.exists():
        shutil.copy2(thumb_src, thumb_dst)
        thumb_json = thumb_src.with_suffix(".json")
        if thumb_json.exists():
            shutil.copy2(thumb_json, thumb_dst.with_suffix(".json"))

    images_manifest = {
        "schema_version": "2.0",
        "checkpoint": "final",
        "content_hash": hashlib.sha256(json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8")).hexdigest(),
        "signature": "analytical_v9_doodle_master",
        "items": image_items
    }
    (OUT_IMAGES_DIR / "images.json").write_text(json.dumps(images_manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    output_manifest = {
        "schema_version": "2.0",
        "job_id": "survivorship-bias-16x9",
        "revision": 11,
        "status": "completed",
        "total_images": len(image_items),
        "aspect_ratio": "16:9"
    }
    (OUT_IMAGES_DIR / "output.json").write_text(json.dumps(output_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Assembled {len(image_items)} images into Revision 11 successfully!")

    # 5. Update brief-current.json
    (RUN_DIR / "brief-current.json").write_text(json.dumps({"revision": brief_rev, "hash": brief_hash}, indent=2) + "\n", encoding="utf-8")
    logger.info(f"Updated brief-current.json to revision {brief_rev}")

    logger.info("All Brief, Content, and Images revisions built successfully!")


if __name__ == "__main__":
    main()
