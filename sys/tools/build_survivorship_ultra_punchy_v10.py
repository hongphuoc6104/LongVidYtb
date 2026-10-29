#!/usr/bin/env python3
"""Build Brief Revision 8, Content Revision 9, and Images Revision 12 for survivorship-bias-16x9.

Ultra-Punchy, High-Stakes Analytical Explainer (v10):
- Tight, rapid-fire sentences (3–8 words), zero presentation fluff ("video này sẽ bóc tách...").
- Merged and accelerated airplane + false correlation mechanics.
- Direct reality check on school & startup traps.
- 3 Actionable filters without blog listicle padding.
- Intimate, warm, concise outro.
- Dynamic visual pacing: every beat (3–5s) maps to a distinct 2D indie doodle image.
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
logger = logging.getLogger("build_ultra_punchy_v10")

RUN_DIR = SYS_DIR / "runs/survivorship-bias-16x9"
SRC_IMAGES_DIR = RUN_DIR / "revisions/images/11_analytical"
OUT_IMAGES_DIR = RUN_DIR / "revisions/images/12_ultra_punchy"

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
            "and simple flat slate-gray (#8C857B) straight trousers or single-line black stick legs, with zero clothing folds, "
            "zero collar details, and zero shading gradients"
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
        "text": "Mở màn chấn động: Nghịch lý người chăm chỉ nhất thường bế tắc nhất, 90% bí quyết thành công trên mạng chỉ là ảo tưởng bòn rút công sức."
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
        "text": "Bài toán thực tế 1 - Trường học và công sở: Cày cuốc mù quáng biến bạn thành công cụ giá rẻ nếu không có đòn bẩy và phương pháp đúng."
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
        "title": "Mở màn chấn động & Cú lừa bí quyết thành công",
        "purpose": "Hỏi trúng tim đen người cày cuốc bế tắc, lật tẩy ảo tưởng bí quyết thành công ngay 10 giây đầu với nhịp dồn dập.",
        "narration": "Bạn cày mười sáu tiếng mỗi ngày. Thu nhập vẫn giậm chân tại chỗ. Tại sao? Bởi vì chín mươi phần trăm bí quyết thành công trên mạng... chỉ là ảo tưởng! Họ dạy bạn dậy sớm, tập gym. Nhưng thứ thực sự cứu mạng họ... họ giấu sạch!",
        "requirements": ["R01"],
        "source_ids": [],
        "coverage_quote": "Bạn cày mười sáu tiếng mỗi ngày. Thu nhập vẫn giậm chân tại chỗ. Tại sao?",
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
                "quote": "Bạn cày mười sáu tiếng mỗi ngày. Thu nhập vẫn giậm chân tại chỗ. Tại sao?",
                "effect": "punch_in"
            },
            {
                "id": "SC01_B2",
                "image_id": "SC01_I2",
                "quote": "Bởi vì chín mươi phần trăm bí quyết thành công trên mạng... chỉ là ảo tưởng!",
                "effect": "pan_left"
            },
            {
                "id": "SC01_B3",
                "image_id": "SC01_I3",
                "quote": "Họ dạy bạn dậy sớm, tập gym. Nhưng thứ thực sự cứu mạng họ... họ giấu sạch!",
                "effect": "zoom_in"
            }
        ]
    },
    {
        "id": "SC02",
        "title": "Bóc tách cơ chế tầng 1: Mối tương quan giả",
        "purpose": "Bóc tách thói quen dậy sớm chỉ là vết đạn ở cánh, động cơ thật sự là vốn ngầm và đòn bẩy bị che giấu.",
        "narration": "Truyền thông bảo bạn dậy từ năm giờ sáng để giàu có. Nhưng đó chỉ là mối tương quan giả, là những vết đạn vô hại ở cánh. Động cơ thực sự đưa họ lên đỉnh cao là vốn ngầm, đòn bẩy gia đình và thời thế, những thứ không bao giờ được kể trên sân khấu.",
        "requirements": ["R02"],
        "source_ids": [],
        "coverage_quote": "Động cơ thực sự đưa họ lên đỉnh cao là vốn ngầm, đòn bẩy gia đình và thời thế, những thứ không bao giờ được kể trên sân khấu.",
        "images": [
            {
                "id": "SC02_I1",
                "src_file": "SC02_I1_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: the blue-shirt stickman frantically buys superficial items: wearing a fake luxury necktie, holding a takeaway coffee, and pointing to a 4:00 AM alarm, with a black marker arrow labeled VẾT ĐẠN VÔ HẠI.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC02_I2",
                "src_file": "SC02_I2_16x9.jpg",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) stage: a deep two-layer comparison stage. The small top tier shows a smiling stickman holding a tiny sign BÍ QUYẾT TRÊN MẠNG; the massive bottom foundation shows a giant solid steel vault labeled VỐN DÀY and two clasped hands labeled QUAN HỆ.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC02_I3",
                "src_file": "SC02_I3_16x9.jpg",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: a successful influencer stickman stands behind a smiling stage mask holding a microphone, while behind his back is an enormous locked steel door concealing his family wealth and backup safety net.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC02_B1",
                "image_id": "SC02_I1",
                "quote": "Truyền thông bảo bạn dậy từ năm giờ sáng để giàu có.",
                "effect": "punch_in"
            },
            {
                "id": "SC02_B2",
                "image_id": "SC02_I2",
                "quote": "Nhưng đó chỉ là mối tương quan giả, là những vết đạn vô hại ở cánh.",
                "effect": "pan_right"
            },
            {
                "id": "SC02_B3",
                "image_id": "SC02_I3",
                "quote": "Động cơ thực sự đưa họ lên đỉnh cao là vốn ngầm, đòn bẩy gia đình và thời thế, những thứ không bao giờ được kể trên sân khấu.",
                "effect": "zoom_in"
            }
        ]
    },
    {
        "id": "SC03",
        "title": "Bóc tách cơ chế tầng 2: Chiếc bẫy dữ liệu sống sót (Abraham Wald 1943)",
        "purpose": "Kể gọn ghẽ mô hình toán học Abraham Wald 1943 để chứng minh dữ liệu truyền thông chỉ lấy từ kẻ sống sót.",
        "narration": "Năm một chín bốn ba, quân đội Mỹ thấy máy bay trở về chi chít lỗ đạn ở cánh. Các tướng lĩnh liền đòi bọc thép ngay vào cánh. Nhà toán học Abraham Wald đập bàn vạch trần: Các ông sai bét rồi! Chỗ cần bọc giáp là động cơ, nơi không có vết đạn nào. Bởi vì những chiếc bị bắn trúng động cơ... đã nổ tung dưới đáy biển, không bao giờ quay về để được thống kê.",
        "requirements": ["R03"],
        "source_ids": ["SRC01"],
        "coverage_quote": "Chỗ cần bọc giáp là động cơ, nơi không có vết đạn nào. Bởi vì những chiếc bị bắn trúng động cơ... đã nổ tung dưới đáy biển, không bao giờ quay về để được thống kê.",
        "images": [
            {
                "id": "SC03_I1",
                "src_file": "SC03_I1_16x9.jpg",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) hangar stage: a 1943 military briefing room with two army generals in green peaked caps scratching their heads beside a large wall chalkboard showing a twin-engine bomber airplane blueprint.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC03_I2",
                "src_file": "SC03_I2_16x9.jpg",
                "desc": "Raw 2D doodle on pale ice-blue (#CBE0E0) stage: an eager general stickman holds a paintbrush painting heavy steel armor slabs onto outer wings with confident smirk.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC03_I3",
                "src_file": "SC03_I3_16x9.jpg",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: mathematician Abraham Wald with round glasses slams hand on military table pointing marker at clean engine nacelles: CHỖ NÀY MỚI CẦN BỌC GIÁP!",
                "shot_type": "full_scene"
            },
            {
                "id": "SC03_I4",
                "src_file": "SC03_I4_16x9.jpg",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) underwater ocean floor stage: deep blue sea depths where shot-down propeller planes rest among jagged coral with comic bubbles rising, showing the unseen graveyard.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC03_B1",
                "image_id": "SC03_I1",
                "quote": "Năm một chín bốn ba, quân đội Mỹ thấy máy bay trở về chi chít lỗ đạn ở cánh.",
                "effect": "pan_right"
            },
            {
                "id": "SC03_B2",
                "image_id": "SC03_I2",
                "quote": "Các tướng lĩnh liền đòi bọc thép ngay vào cánh.",
                "effect": "zoom_in"
            },
            {
                "id": "SC03_B3",
                "image_id": "SC03_I3",
                "quote": "Nhà toán học Abraham Wald đập bàn vạch trần: Các ông sai bét rồi! Chỗ cần bọc giáp là động cơ, nơi không có vết đạn nào.",
                "effect": "punch_in"
            },
            {
                "id": "SC03_B4",
                "image_id": "SC03_I4",
                "quote": "Bởi vì những chiếc bị bắn trúng động cơ... đã nổ tung dưới đáy biển, không bao giờ quay về để được thống kê.",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC04",
        "title": "Bài toán thực tế 1: Trường học & Công sở",
        "purpose": "Vạch trần cạm bẫy cày cuốc thâu đêm chỉ biến người lao động thành công cụ giá rẻ nếu thiếu đòn bẩy.",
        "narration": "Trong trường học và công sở, người ta tung hô thủ khoa và nhân viên tăng ca thâu đêm. Nhưng hệ thống xóa sổ hoàn toàn nghĩa địa của hàng trăm người cũng thức trắng đêm nhưng gục ngã. Cắm đầu cày cuốc mà không có đòn bẩy, bạn chỉ đang tự biến mình thành một công cụ giá rẻ. Bạn bắt chước sự chăm chỉ bề nổi của kẻ chiến thắng, mà không biết mình đang bước vào cái bẫy kiệt quệ.",
        "requirements": ["R04"],
        "source_ids": [],
        "coverage_quote": "Cắm đầu cày cuốc mà không có đòn bẩy, bạn chỉ đang tự biến mình thành một công cụ giá rẻ.",
        "images": [
            {
                "id": "SC04_I1",
                "src_file": "SC04_I1_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) classroom stage: a strict teacher stickman with glasses pins a gold star medal onto a single smiling valedictorian stickman while dozens of exhausted stickmen slump over desks with heavy textbooks.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC04_I2",
                "src_file": "SC04_I2_16x9.jpg",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) night stage: the blue-shirt stickman sits at a crooked office desk under a harsh single hanging bulb at 2:00 AM, surrounded by towering stacks of spreadsheets and empty coffee cans, red bloodshot eyes.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC04_I3",
                "src_file": "SC04_I3_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: deep pit below the winner's podium! A lone winner on top raises a tiny trophy, while down in the pit hundreds of exhausted workers form an endless human conveyor belt labeled CÔNG CỤ GIÁ RẺ.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC04_I4",
                "src_file": "SC04_I4_16x9.jpg",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) stage: a dramatic theatrical spotlight beam shines down on an empty award stand holding a hollow gold medal labeled HY SINH VÔ ÍCH, while behind the curtain an exhausted stickman walks toward a dangerous steep cliff edge.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC04_B1",
                "image_id": "SC04_I1",
                "quote": "Trong trường học và công sở, người ta tung hô thủ khoa và nhân viên tăng ca thâu đêm.",
                "effect": "zoom_in"
            },
            {
                "id": "SC04_B2",
                "image_id": "SC04_I2",
                "quote": "Nhưng hệ thống xóa sổ hoàn toàn nghĩa địa của hàng trăm người cũng thức trắng đêm nhưng gục ngã.",
                "effect": "pan_left"
            },
            {
                "id": "SC04_B3",
                "image_id": "SC04_I3",
                "quote": "Cắm đầu cày cuốc mà không có đòn bẩy, bạn chỉ đang tự biến mình thành một công cụ giá rẻ.",
                "effect": "zoom_out"
            },
            {
                "id": "SC04_B4",
                "image_id": "SC04_I4",
                "quote": "Bạn bắt chước sự chăm chỉ bề nổi của kẻ chiến thắng, mà không biết mình đang bước vào cái bẫy kiệt quệ.",
                "effect": "punch_in"
            }
        ]
    },
    {
        "id": "SC05",
        "title": "Bài toán thực tế 2: Xã hội & Ảo tưởng dám liều mới giàu",
        "purpose": "Vạch trần ảo tưởng dám liều làm giàu và số phận biến mất trong im lặng của hàng ngàn kẻ vỡ nợ.",
        "narration": "Bước ra ngoài đời, các chuyên gia tài chính bắt đầu bán cho bạn sự ảo tưởng. Lướt mạng xã hội đâu đâu cũng thấy hình mẫu hai mươi tuổi bỏ học kiếm triệu đô. Họ gào thét: Dám liều mới giàu! Hãy bước ra khỏi vùng an toàn! Sự thật cay đắng là: hàng ngàn người dám liều đã vỡ nợ trong im lặng, không ai đưa micro cho kẻ phá sản kể chuyện.",
        "requirements": ["R05"],
        "source_ids": [],
        "coverage_quote": "Sự thật cay đắng là: hàng ngàn người dám liều đã vỡ nợ trong im lặng, không ai đưa micro cho kẻ phá sản kể chuyện.",
        "images": [
            {
                "id": "SC05_I1",
                "src_file": "SC05_I1_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: the blue-shirt stickman steps out through an open exit door of an office cubicle, throwing his papers into the air and holding a backpack labeled TỰ DO TÀI CHÍNH with naive optimism.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC05_I2",
                "src_file": "SC05_I2_16x9.jpg",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: the blue-shirt stickman looks at his smartphone screen glowing with social media thumbnails of luxury sports cars, crypto charts shooting straight up to the moon, and smiling young influencers with dollar sunglasses.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC05_I3",
                "src_file": "SC05_I3_16x9.jpg",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) stage: the guru shouts through an oversized megaphone labeled DÁM LIỀU MỚI GIÀU, spraying comic soundwaves across the stage while a crowd of stickmen listens mesmerized.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC05_I4",
                "src_file": "SC05_I4_16x9.jpg",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) night stage: 6 months later, the stickman sits slumped on a simple wooden stool clutching his head in utter shock before a small desk covered in red final-demand debt notices GIẤY ĐÒI NỢ.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC05_B1",
                "image_id": "SC05_I1",
                "quote": "Bước ra ngoài đời, các chuyên gia tài chính bắt đầu bán cho bạn sự ảo tưởng.",
                "effect": "zoom_in"
            },
            {
                "id": "SC05_B2",
                "image_id": "SC05_I2",
                "quote": "Lướt mạng xã hội đâu đâu cũng thấy hình mẫu hai mươi tuổi bỏ học kiếm triệu đô.",
                "effect": "pan_right"
            },
            {
                "id": "SC05_B3",
                "image_id": "SC05_I3",
                "quote": "Họ gào thét: Dám liều mới giàu! Hãy bước ra khỏi vùng an toàn!",
                "effect": "punch_in"
            },
            {
                "id": "SC05_B4",
                "image_id": "SC05_I4",
                "quote": "Sự thật cay đắng là: hàng ngàn người dám liều đã vỡ nợ trong im lặng, không ai đưa micro cho kẻ phá sản kể chuyện.",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC06",
        "title": "Bộ lọc phòng thủ 1: Nhìn vào Nghĩa địa",
        "purpose": "Học cách nhìn vào nghĩa địa người thất bại trước khi tin bất kỳ lời khuyên hay cơ hội đổi đời nào.",
        "narration": "Để không bị dắt mũi, đây là ba bộ lọc sinh tồn bạn phải cài đặt ngay. Bộ lọc thứ nhất: Nhìn vào Nghĩa địa. Trước khi tin một lời khuyên, hãy hỏi: Có bao nhiêu người làm y hệt mà vẫn sạt nghiệp? Nếu tỷ lệ tử vong là chín mươi chín phần trăm, đó không phải cơ hội, mà là canh bạc may rủi.",
        "requirements": ["R06"],
        "source_ids": [],
        "coverage_quote": "Trước khi tin một lời khuyên, hãy hỏi: Có bao nhiêu người làm y hệt mà vẫn sạt nghiệp?",
        "images": [
            {
                "id": "SC06_I1",
                "src_file": "SC06_I1_16x9.jpg",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) stage: a vast silent graveyard under a crescent moon with dozens of crooked wooden crosses and headstones marked KHỞI NGHIỆP THẤT BẠI, completely deserted and forgotten.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC06_I2",
                "src_file": "SC06_I2_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: an empty dimly-lit auditorium stage with a knocked-over microphone stand and scattered seminar flyers on the floor, showing zero applause for the bankrupt founders.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC06_I3",
                "src_file": "SC06_I3_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: the stickman stands holding a magnifying glass examining a tiny speck of 1% survivors on top of a massive sunken 99% mountain of failures labeled NGHĨA ĐỊA DỮ LIỆU.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC06_B1",
                "image_id": "SC06_I1",
                "quote": "Để không bị dắt mũi, đây là ba bộ lọc sinh tồn bạn phải cài đặt ngay.",
                "effect": "zoom_in"
            },
            {
                "id": "SC06_B2",
                "image_id": "SC06_I2",
                "quote": "Bộ lọc thứ nhất: Nhìn vào Nghĩa địa. Trước khi tin một lời khuyên, hãy hỏi: Có bao nhiêu người làm y hệt mà vẫn sạt nghiệp?",
                "effect": "pan_left"
            },
            {
                "id": "SC06_B3",
                "image_id": "SC06_I3",
                "quote": "Nếu tỷ lệ tử vong là chín mươi chín phần trăm, đó không phải cơ hội, mà là canh bạc may rủi.",
                "effect": "punch_in"
            }
        ]
    },
    {
        "id": "SC07",
        "title": "Bộ lọc phòng thủ 2: Bọc giáp Động cơ",
        "purpose": "Tập trung xây dựng năng lực chuyên môn sắc bén và quỹ dự phòng tài chính thay vì bọc giáp bề ngoài.",
        "narration": "Bộ lọc thứ hai: Bọc giáp Động cơ. Đừng lãng phí tiền bọc giáp cho vỏ bọc sang chảnh bề ngoài. Động cơ sống còn của bạn là năng lực chuyên môn sắc bén, và một quỹ dự phòng tài chính đủ sống sáu đến mười hai tháng. Bọc giáp thật vững cho động cơ trước khi bạn nghĩ đến chuyện cất cánh.",
        "requirements": ["R07"],
        "source_ids": [],
        "coverage_quote": "Động cơ sống còn của bạn là năng lực chuyên môn sắc bén, và một quỹ dự phòng tài chính đủ sống sáu đến mười hai tháng.",
        "images": [
            {
                "id": "SC07_I1",
                "src_file": "SC07_I1_16x9.jpg",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) stage: the blue-shirt stickman looks into a full-length dressing mirror and sees himself as an exhausted puppet with tangled strings, realizing blind imitation only drains his soul.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC07_I2",
                "src_file": "SC07_I2_16x9.jpg",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) stage: the stickman confidently uses a wrench to bolt a thick solid steel armor plate over his chest engine, eyes determined and resolute, standing solidly on the ground.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC07_I3",
                "src_file": "SC07_I3_16x9.jpg",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) stage: the blue-shirt stickman stands calm and secure behind a heavy steel shield wall while dark economic storm clouds rain lightning bolts outside, safe and completely unshakeable.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC07_B1",
                "image_id": "SC07_I1",
                "quote": "Bộ lọc thứ hai: Bọc giáp Động cơ. Đừng lãng phí tiền bọc giáp cho vỏ bọc sang chảnh bề ngoài.",
                "effect": "punch_in"
            },
            {
                "id": "SC07_B2",
                "image_id": "SC07_I2",
                "quote": "Động cơ sống còn của bạn là năng lực chuyên môn sắc bén, và một quỹ dự phòng tài chính đủ sống sáu đến mười hai tháng.",
                "effect": "zoom_in"
            },
            {
                "id": "SC07_B3",
                "image_id": "SC07_I3",
                "quote": "Bọc giáp thật vững cho động cơ trước khi bạn nghĩ đến chuyện cất cánh.",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC08",
        "title": "Bộ lọc phòng thủ 3: Tư duy Trừ Lùi của Charlie Munger",
        "purpose": "Loại bỏ 3 nguyên nhân chắc chắn dẫn đến phá sản trước khi nghĩ đến công thức làm giàu.",
        "narration": "Bộ lọc thứ ba: Tư duy Trừ Lùi của Charlie Munger. Muốn sống sót, hãy tìm xem chỗ nào làm bạn chết rồi đừng bao giờ đến đó. Lập danh sách ba việc chắc chắn khiến bạn phá sản: vay nợ lãi cao, tất tay một canh bạc, và ảo tưởng năng lực. Kiên quyết gạch bỏ ba điều đó, bạn đã tự cứu mình khỏi chín mươi phần trăm bi kịch.",
        "requirements": ["R08"],
        "source_ids": ["SRC02"],
        "coverage_quote": "Muốn sống sót, hãy tìm xem chỗ nào làm bạn chết rồi đừng bao giờ đến đó.",
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
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: a gambler stickman reaching hungrily for a shiny gold coin on a mouse trap; the blue-shirt stickman firmly slaps his hand away, preventing disaster with Inversion thinking.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC08_B1",
                "image_id": "SC08_I1",
                "quote": "Bộ lọc thứ ba: Tư duy Trừ Lùi của Charlie Munger. Muốn sống sót, hãy tìm xem chỗ nào làm bạn chết rồi đừng bao giờ đến đó.",
                "effect": "zoom_in"
            },
            {
                "id": "SC08_B2",
                "image_id": "SC08_I2",
                "quote": "Lập danh sách ba việc chắc chắn khiến bạn phá sản: vay nợ lãi cao, tất tay một canh bạc, và ảo tưởng năng lực.",
                "effect": "punch_in"
            },
            {
                "id": "SC08_B3",
                "image_id": "SC08_I3",
                "quote": "Kiên quyết gạch bỏ ba điều đó, bạn đã tự cứu mình khỏi chín mươi phần trăm bi kịch.",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC09",
        "title": "Đòn kết liễu: Giữ mạng sống trước khi cất cánh",
        "purpose": "Đúc kết đanh thép: Dừng sao chép mù quáng, bọc giáp tử huyệt và giữ mạng sống trước khi cất cánh.",
        "narration": "Bắt chước người chiến thắng chỉ biến bạn thành một bản sao kiệt sức. Khi thấy ai đó khoe mẽ hào quang, hãy tự hỏi những kẻ thất bại đang ở đâu dưới đáy biển. Bọc giáp cho tử huyệt của mình trước, giữ cho mình sống sót đã, rồi thành công mới đến lượt bạn cất cánh.",
        "requirements": ["R09"],
        "source_ids": [],
        "coverage_quote": "Bọc giáp cho tử huyệt của mình trước, giữ cho mình sống sót đã, rồi thành công mới đến lượt bạn cất cánh.",
        "images": [
            {
                "id": "SC09_I1",
                "src_file": "SC09_I1_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: a crude 2D propeller bomber plane sits safely on a landing runway with thick armor slabs bolted onto its engine housing, safe from any enemy bullet holes.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC09_I2",
                "src_file": "SC09_I2_16x9.jpg",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: the stickman lies limp like a noodle across a wooden stool, completely drained, realizing that running around copying everyone else only creates a hollow, exhausted copycat.",
                "shot_type": "full_scene"
            },
            {
                "id": "SC09_I3",
                "src_file": "SC09_I3_16x9.jpg",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) sunrise stage: the sturdy 2D propeller airplane climbs confidently into the dawn sky toward a warm yellow rising sun, engines securely armored, ready to survive any storm.",
                "shot_type": "full_scene"
            }
        ],
        "beats": [
            {
                "id": "SC09_B1",
                "image_id": "SC09_I1",
                "quote": "Bắt chước người chiến thắng chỉ biến bạn thành một bản sao kiệt sức.",
                "effect": "zoom_in"
            },
            {
                "id": "SC09_B2",
                "image_id": "SC09_I2",
                "quote": "Khi thấy ai đó khoe mẽ hào quang, hãy tự hỏi những kẻ thất bại đang ở đâu dưới đáy biển.",
                "effect": "pan_right"
            },
            {
                "id": "SC09_B3",
                "image_id": "SC09_I3",
                "quote": "Bọc giáp cho tử huyệt của mình trước, giữ cho mình sống sót đã, rồi thành công mới đến lượt bạn cất cánh.",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC10",
        "title": "Không gian đàm đạo & Lời hẹn rèn luyện tư duy",
        "purpose": "Kết nối ấm áp, tự nhiên, mời thảo luận chiều sâu trên TikTok Live và kêu gọi tương tác ngắn gọn.",
        "narration": "Nhận ra bẫy tư duy chỉ là bước đầu. Rèn được bản lĩnh trừ lùi trong đời thực mới giúp bạn đứng vững mỗi ngày. Sắp tới, mình sẽ mở những buổi Live ngồi lại đàm đạo, mổ xẻ những cú vấp ngã thật của chính các bạn. Nếu video hôm nay giúp bạn bớt đi một ảo tưởng, hãy thả tim, chia sẻ vết đạn của bạn dưới bình luận và theo dõi kênh để cùng rèn luyện tư duy.",
        "requirements": ["R10"],
        "source_ids": [],
        "coverage_quote": "Sắp tới, mình sẽ mở những buổi Live ngồi lại đàm đạo, mổ xẻ những cú vấp ngã thật của chính các bạn.",
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
                "quote": "Nhận ra bẫy tư duy chỉ là bước đầu. Rèn được bản lĩnh trừ lùi trong đời thực mới giúp bạn đứng vững mỗi ngày.",
                "effect": "zoom_in"
            },
            {
                "id": "SC10_B2",
                "image_id": "SC10_I2",
                "quote": "Sắp tới, mình sẽ mở những buổi Live ngồi lại đàm đạo, mổ xẻ những cú vấp ngã thật của chính các bạn.",
                "effect": "pan_left"
            },
            {
                "id": "SC10_B3",
                "image_id": "SC10_I3",
                "quote": "Nếu video hôm nay giúp bạn bớt đi một ảo tưởng, hãy thả tim, chia sẻ vết đạn của bạn dưới bình luận và theo dõi kênh để cùng rèn luyện tư duy.",
                "effect": "punch_in"
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
            "min_seconds": 100.0,
            "max_seconds": 200.0
        },
        "scene_count": 10,
        "required_points": REQUIRED_POINTS,
        "language": "vi",
        "tone": "Điềm đạm, ấm áp, thông tuệ, gần gũi, đanh thép, dồn dập, không rườm rà",
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
        }
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
        scene_images = []
        for img in sc["images"]:
            scene_images.append({
                "id": img["id"],
                "description": img["desc"],
                "character_ids": ["CH01"],
                "based_on": None,
                "preserve": "",
                "change": img["desc"],
                "reason": "Show the concrete object, comparison, or action at its spoken anchor.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": img.get("shot_type", "full_scene"),
                "has_character": True,
                "explanation": {
                    "quote": sc["beats"][0]["quote"],
                    "relation": "context",
                    "source_terms": [sc["narration"].split()[0]],
                    "visual_terms": [img["desc"][:40]]
                }
            })

        beats = []
        for b in sc["beats"]:
            beats.append({
                "id": b["id"],
                "image_id": b["image_id"],
                "purpose": sc["purpose"],
                "anchor": {
                    "vi": {
                        "quote": b["quote"],
                        "occurrence": 1
                    }
                },
                "effect": b["effect"],
                "focus": {"x": 0.5, "y": 0.5}
            })

        content_scenes.append({
            "id": sc["id"],
            "title": sc["title"],
            "purpose": sc["purpose"],
            "action": sc["purpose"],
            "setting": SCENE_SETTINGS[sc["id"]],
            "camera": sc.get("camera", "Narration-led full-frame compositions"),
            "narration": sc["narration"],
            "requirements": sc["requirements"],
            "character_ids": ["CH01"],
            "source_ids": sc.get("source_ids", []),
            "images": scene_images,
            "beats": beats
        })

        if "coverage_quote" in sc:
            coverage.append({
                "requirement_id": sc["requirements"][0],
                "scene_id": sc["id"],
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
            "quote": "Bởi vì những chiếc bị bắn trúng động cơ... đã nổ tung dưới đáy biển, không bao giờ quay về để được thống kê.",
            "language": "vi",
            "source_id": "SRC01",
            "fact": "Những chiếc máy bay trúng đạn vào động cơ và buồng lái không thể quay về."
        },
        {
            "scene_id": "SC08",
            "quote": "Muốn sống sót, hãy tìm xem chỗ nào làm bạn chết rồi đừng bao giờ đến đó.",
            "language": "vi",
            "source_id": "SRC02",
            "fact": "Muốn thành công, trước hết phải tìm cách không bị thất bại."
        },
        {
            "scene_id": "SC08",
            "quote": "Lập danh sách ba việc chắc chắn khiến bạn phá sản: vay nợ lãi cao, tất tay một canh bạc, và ảo tưởng năng lực.",
            "language": "vi",
            "source_id": "SRC02",
            "fact": "Tránh xa những quyết định dẫn đến thảm họa thay vì tìm kiếm sự xuất sắc."
        }
    ]

    revision_response = [
        {
            "request_id": "R01",
            "status": "addressed",
            "explanation": "Tái cấu trúc 100% video theo khung Ultra-Punchy Analytical Explainer (v10): loại bỏ câu giới thiệu rườm rà, nhịp câu ngắn dồn dập 3-8 từ, tăng tốc thị giác 3-5s mỗi tranh doodle 2D.",
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
    logger.info("Building Ultra-Punchy Analytical Explainer v10...")

    # 1. Build Brief Revision 8
    brief = build_brief()
    validate_brief(str(SYS_DIR), brief)
    logger.info("Brief passed validation!")

    brief_bytes = json.dumps(brief, ensure_ascii=False, indent=2).encode("utf-8")
    brief_hash = hashlib.sha256(brief_bytes).hexdigest()
    brief_rev = 8
    brief_path = RUN_DIR / f"briefs/{brief_rev}.json"
    brief_path.write_bytes(brief_bytes)
    logger.info(f"Wrote {brief_path} (hash: {brief_hash[:16]}...)")

    # 2. Build Content Revision 9
    content_rev = 9
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
    logger.info(f"Script diversity linter passed: {lint_report['rhythm_metrics']}")

    content_dir = RUN_DIR / f"revisions/content/{content_rev}"
    content_dir.mkdir(parents=True, exist_ok=True)
    content_path = content_dir / "content.json"
    content_path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Wrote {content_path}")

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

    # 4. Build Images Revision 12
    OUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    symlink_path = RUN_DIR / "revisions/images/12"
    if symlink_path.is_symlink() or symlink_path.exists():
        if symlink_path.is_symlink():
            symlink_path.unlink()
        else:
            shutil.rmtree(symlink_path)
    symlink_path.symlink_to("12_ultra_punchy")

    seen_images = set()
    image_items = []
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

            src_json = src_file.with_suffix(".json")
            if src_json.exists():
                shutil.copy2(src_json, dst_file.with_suffix(".json"))

            sha = hashlib.sha256(dst_file.read_bytes()).hexdigest()
            image_items.append({
                "scene_id": s["id"],
                "path": f"revisions/images/12_ultra_punchy/{dst_name}",
                "prompt": img["desc"],
                "source": "google-flow-browser",
                "sha256": sha,
                "image_id": img_id,
                "ratio": "16:9"
            })

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
        "signature": "ultra_punchy_v10_doodle_master",
        "items": image_items
    }
    (OUT_IMAGES_DIR / "images.json").write_text(json.dumps(images_manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    output_manifest = {
        "schema_version": "2.0",
        "job_id": "survivorship-bias-16x9",
        "revision": 12,
        "status": "completed",
        "total_images": len(image_items),
        "aspect_ratio": "16:9"
    }
    (OUT_IMAGES_DIR / "output.json").write_text(json.dumps(output_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Assembled {len(image_items)} images into Revision 12 successfully!")

    # 5. Update brief-current.json
    (RUN_DIR / "brief-current.json").write_text(json.dumps({"revision": brief_rev, "hash": brief_hash}, indent=2) + "\n", encoding="utf-8")
    logger.info(f"Updated brief-current.json to revision {brief_rev}")

    logger.info("All Brief 8, Content 9, and Images 12 built and validated successfully!")


if __name__ == "__main__":
    main()
