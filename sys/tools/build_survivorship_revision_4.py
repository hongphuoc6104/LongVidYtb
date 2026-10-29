#!/usr/bin/env python3
"""Build Brief and Content Revision 4 for survivorship-bias-16x9.

9 Scenes, ~560 words, strictly complying with:
- User feedback on script, tone, pacing, and visual storytelling
- 2D Indie Doodle visual contract (1.7.0 handdrawn_2d_explainer)
- Anti-slop: zero 3D clipart, expressive stickman interactions
"""
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"
RUN_DIR = SYS_DIR / "runs/survivorship-bias-16x9"

BRIEFS_DIR = RUN_DIR / "briefs"
CONTENT_REV_DIR = RUN_DIR / "revisions/content/4"
DRAFT_DIR = RUN_DIR / "draft"

BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
CONTENT_REV_DIR.mkdir(parents=True, exist_ok=True)
DRAFT_DIR.mkdir(parents=True, exist_ok=True)

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

STICKMAN_APPEARANCE = (
    "Iconic 2D Vietnamese indie webcomic doodle stickman (Nguệch Ngoạc / Vẽ Vời / Xấu Vê Nờ style): "
    "oversized slightly lopsided hand-drawn pure-white (#FFFFFF) bald circle head with bold pitch-black (#000000) "
    "marker outline, tiny solid-black dot eyes placed low on the face leaving a large open upper forehead/cranium, "
    "minimal single-stroke eyebrows and mouth, no nose or ears, thin single-line solid-black wire/stick arms "
    "(single black stroke with zero arm thickness) ending in small round white circle hands"
)

STICKMAN_OUTFIT = (
    "Unshaded 100% flat MS-Paint paint-bucket solid cerulean-blue (#3B82C4) simple pill/rectangular T-shirt torso "
    "and simple flat slate-gray (#8C857B) straight trousers or single-line black stick legs, with zero clothing "
    "folds, zero collar details, and zero shading gradients"
)

SCENES_DATA = [
    {
        "id": "SC01",
        "title": "Cái bẫy của việc bắt chước",
        "purpose": "Mở bài bằng cú tát nhận thức và tương phản thị giác cực mạnh: bắt chước người giỏi nhất là cách nhanh nhất để kiệt sức và bế tắc",
        "narration": "Bắt chước người giỏi nhất là cách nhanh nhất để bạn kiệt sức và bế tắc. Từ khi còn ngồi trên ghế nhà trường cho đến lúc bước chân ra ngoài xã hội, chúng ta đều bị nhồi nhét một ảo tưởng: chỉ cần làm y hệt người thành công, bạn sẽ thành công.",
        "setting": "Flat warm paper-cream (#F8F0DC) and apricot-peach (#F2B88B) 2D orthographic comic stage.",
        "beats": [
            {
                "id": "SC01_I1",
                "quote": "Bắt chước người giỏi nhất là cách nhanh nhất để bạn kiệt sức và bế tắc.",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: dramatic comic contrast! On the left, the white-head stickman in blue shirt (#3B82C4) collapses completely face-down onto a pile of crumpled papers and heavy books, tongue out, dizzy spiral eyes, cartoon sweat drops spraying. On the right, a giant flashy podium where another stickman raises a gleaming golden trophy with confetti raining down. Instant contrast between burnout and glory.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC01_I2",
                "quote": "Từ khi còn ngồi trên ghế nhà trường cho đến lúc bước chân ra ngoài xã hội,",
                "desc": "Raw 2D doodle on pale ice-blue (#CBE0E0) stage: a split horizontal conveyor journey. On the left side, a school classroom with a blackboard marked HỌC SINH GIỎI; on the right side, a corporate glass office building. The blue-shirt stickman marches forward carrying an oversized heavy backpack, staring ahead with naive wide round eyes.",
                "shot_type": "full_scene",
                "effect": "pan_right"
            },
            {
                "id": "SC01_I3",
                "quote": "chúng ta đều bị nhồi nhét một ảo tưởng: chỉ cần làm y hệt người thành công, bạn sẽ thành công.",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: the blue-shirt stickman stares mesmerized with starry eyes at an enormous flashy roadside billboard. On the billboard, a smiling doodle stickman in a tuxedo steps out of a luxury sports car with a giant comic speech bubble: LÀM Y HỆT TÔI ĐI!",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC02",
        "title": "Ảo tưởng thủ khoa trong trường học",
        "purpose": "Khắc họa thực tế cày cuốc học tập thâu đêm theo lịch thủ khoa nhưng nhận về điểm lẹt đẹt và cơ thể suy nhược",
        "narration": "Trong trường học, người ta tôn vinh thủ khoa. Thầy cô bảo bạn nhìn vào lịch học của họ: thức khuya, dậy sớm, giải hàng nghìn bài tập. Bạn cắm đầu làm theo, bỏ ngủ, nhịn ăn, nhưng điểm số vẫn lẹt đẹt, còn cơ thể thì suy nhược.",
        "setting": "Flat warm paper-cream (#F8F0DC) and slate-navy (#2E4361) 2D orthographic study stage.",
        "beats": [
            {
                "id": "SC02_I1",
                "quote": "Trong trường học, người ta tôn vinh thủ khoa. Thầy cô bảo bạn nhìn vào lịch học của họ:",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) classroom stage: a strict teacher stickman with round spectacles points a wooden stick at a shining valedictorian stickman wearing a golden laurel wreath, while the blue-shirt stickman in the front row stares nervously.",
                "shot_type": "full_scene",
                "effect": "pan_right"
            },
            {
                "id": "SC02_I2",
                "quote": "thức khuya, dậy sớm, giải hàng nghìn bài tập. Bạn cắm đầu làm theo,",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) night stage: the blue-shirt stickman sits at a crooked wooden study desk at 3:00 AM, giant alarm clock clattering, head steaming with exhaustion, dark circles under his eyes, buried beneath towering zigzag piles of math exercise books.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC02_I3",
                "quote": "bỏ ngủ, nhịn ăn, nhưng điểm số vẫn lẹt đẹt, còn cơ thể thì suy nhược.",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: the stickman lies limp like a noodle across the floor, fainting with spiral dizzy eyes and an ice pack on head, holding a crumpled exam paper stamped with a big red score 4.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC03",
        "title": "Nghĩa địa sau lưng kẻ thắng cuộc",
        "purpose": "Bóc trần bản chất: nhà trường chỉ thưởng cho người về đích đầu tiên, xóa sổ hàng trăm người kiệt sức; bạn chỉ thấy kẻ sống sót",
        "narration": "Tại sao? Vì nhà trường chỉ trao thưởng cho một người về đích đầu tiên, chứ không ai phỏng vấn hàng trăm học sinh khác cũng thức đêm, cũng cày cuốc y hệt, nhưng trượt vỏ chuối vì kiệt sức, hoặc đơn giản là không có thiên phú bẩm sinh. Bạn chỉ được nhìn thấy kẻ sống sót.",
        "setting": "Flat pale ice-blue (#CBE0E0) and slate-navy (#2E4361) 2D orthographic podium stage.",
        "beats": [
            {
                "id": "SC03_I1",
                "quote": "Tại sao? Vì nhà trường chỉ trao thưởng cho một người về đích đầu tiên,",
                "desc": "Raw 2D doodle on pale ice-blue (#CBE0E0) stage: a single victorious stickman smiles proudly on the highest championship podium holding a giant gold cup, while golden confetti drifts through the air.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC03_I2",
                "quote": "chứ không ai phỏng vấn hàng trăm học sinh khác cũng thức đêm, cũng cày cuốc y hệt, nhưng trượt vỏ chuối vì kiệt sức,",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: deep pit below the winner's podium! A crowd of dozens of tired doodle stickmen with X-eyes and dizzy sweat drops are tumbled in a ditch beside banana peels and torn exercise notebooks, completely out of sight.",
                "shot_type": "full_scene",
                "effect": "pan_right"
            },
            {
                "id": "SC03_I3",
                "quote": "hoặc đơn giản là không có thiên phú bẩm sinh. Bạn chỉ được nhìn thấy kẻ sống sót.",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) stage: a dramatic theatrical spotlight beam shines down brightly on the single lone survivor standing tall, while 90% of the stage is in total black silhouette filled with shadowy fallen stickmen.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC04",
        "title": "Bước ra ngoài đời & Cú lừa triệu đô",
        "purpose": "Khắc họa cạm bẫy ngoài đời không có đáp án mẫu, mạng xã hội tràn ngập hình mẫu 20 tuổi triệu đô khuyên liều lĩnh thoát vùng an toàn",
        "narration": "Bước ra ngoài đời, cái bẫy này còn tàn khốc gấp mười lần. Ngoài xã hội không có đáp án mẫu, cũng chẳng ai phát đề thi cho bạn. Lướt điện thoại đâu đâu cũng thấy những tấm gương đổi đời: hai mươi tuổi kiếm triệu đô, bỏ học làm chủ, nhảy việc nhân năm lần lương. Họ mở khóa học, viết sách, ra rả dạy đời: Dám liều mới giàu! Hãy bước ra khỏi vùng an toàn!",
        "setting": "Flat warm paper-cream (#F8F0DC) and apricot-peach (#F2B88B) 2D orthographic city street stage.",
        "beats": [
            {
                "id": "SC04_I1",
                "quote": "Bước ra ngoài đời, cái bẫy này còn tàn khốc gấp mười lần. Ngoài xã hội không có đáp án mẫu, cũng chẳng ai phát đề thi cho bạn.",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: the blue-shirt stickman steps out through the school gates into a bustling chaotic concrete maze with confusing road signs pointing in four opposite directions and floating question marks.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC04_I2",
                "quote": "Lướt điện thoại đâu đâu cũng thấy những tấm gương đổi đời: hai mươi tuổi kiếm triệu đô, bỏ học làm chủ, nhảy việc nhân năm lần lương.",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: the blue-shirt stickman looks at his smartphone screen as giant comic popup notifications explode outwards: 20 TUỔI TRIỆU ĐÔ, BỎ HỌC LÀM CHỦ, X5 LƯƠNG with flying money bills.",
                "shot_type": "full_scene",
                "effect": "pan_right"
            },
            {
                "id": "SC04_I3",
                "quote": "Họ mở khóa học, viết sách, ra rả dạy đời:",
                "desc": "Raw 2D doodle on pale ice-blue (#CBE0E0) stage: a flamboyant online guru stickman wearing sunglasses stands on an elevated stage behind a wooden lectern, holding up a thick bestselling book with a big red stamp KHÓA HỌC LÀM GIÀU.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC04_I4",
                "quote": "Dám liều mới giàu! Hãy bước ra khỏi vùng an toàn!",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) stage: the guru shouts through an oversized megaphone with a massive speech bubble: DÁM LIỀU MỚI GIÀU! In front of him, the gullible blue-shirt stickman gets pumped up, rolling up his sleeves ready to leap off a ledge.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC05",
        "title": "Cú vấp ngã & Nghĩa địa của những người im lặng",
        "purpose": "Khắc họa cú sốc nghỉ việc lao theo đam mê rồi trắng tay; bóc trần sự thật cay đắng: kẻ thất bại biến mất trong im lặng, không có micro hay sách báo",
        "narration": "Bạn nghe bùi tai, nộp đơn nghỉ việc cái rụp, dốc sạch tiền tiết kiệm lao theo đam mê. Và chỉ nửa năm sau, bạn trắng tay, ôm đống nợ và tự dằn vặt: Sao người ta làm được mà mình lại toang? Bạn không hề kém cỏi. Sự thật cay đắng là: những người dám liều mà sạt nghiệp, họ đã biến mất trong im lặng. Họ làm gì có micro, chẳng có sân khấu nào mời họ, và dĩ nhiên không ai rảnh để in sách kể về những kẻ thất bại.",
        "setting": "Flat warm paper-cream (#F8F0DC) and slate-navy (#2E4361) 2D orthographic room stage.",
        "beats": [
            {
                "id": "SC05_I1",
                "quote": "Bạn nghe bùi tai, nộp đơn nghỉ việc cái rụp, dốc sạch tiền tiết kiệm lao theo đam mê.",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) office stage: the enthusiastic stickman slams a resignation paper titled ĐƠN NGHỈ VIỆC onto his office desk, grinning broadly while carrying a cardboard box of personal belongings.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC05_I2",
                "quote": "Và chỉ nửa năm sau, bạn trắng tay, ôm đống nợ và tự dằn vặt: Sao người ta làm được mà mình lại toang?",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) night stage: 6 months later, the stickman sits slumped on the floor of a barren room, holding an empty turned-out wallet with moths flying out, surrounded by a mountain of red bills stamped NỢ.",
                "shot_type": "full_scene",
                "effect": "pan_left"
            },
            {
                "id": "SC05_I3",
                "quote": "Bạn không hề kém cỏi. Sự thật cay đắng là: những người dám liều mà sạt nghiệp, họ đã biến mất trong im lặng.",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) stage: a vast silent graveyard under a crescent moon, dotted with dozens of simple wooden cross markers where bankrupt stickmen sit silently in the dark with head in knees.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            },
            {
                "id": "SC05_I4",
                "quote": "Họ làm gì có micro, chẳng có sân khấu nào mời họ, và dĩ nhiên không ai rảnh để in sách kể về những kẻ thất bại.",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: an empty dimly-lit auditorium stage with a lone cold microphone on a stand, its cable unplugged on the wooden floor, with zero audience and zero book in sight.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            }
        ]
    },
    {
        "id": "SC06",
        "title": "Cú đập bàn của Abraham Wald năm 1943",
        "purpose": "Kể sinh động bài toán lịch sử 1943 của không quân Mỹ và cú đập bàn của Abraham Wald: chỗ không có vết đạn mới là tử huyệt",
        "narration": "Năm một nghìn chín trăm bốn mươi ba, quân đội Mỹ đau đầu tìm cách bọc giáp cho máy bay ném bom. Nhìn những chiếc máy bay bay về chi chít lỗ đạn ở cánh và thân, các tướng lĩnh phán ngay: Thủng ở đâu, bọc thép dày vào đó! Đúng lúc ấy, nhà toán học A-bờ-ra-ham Oan đập bàn can lại: Các ông sai bét rồi! Chỗ cần bọc giáp nhất chính là động cơ, nơi chẳng có vết đạn nào cả!",
        "setting": "Flat soft sage-green (#93A88C) and apricot-peach (#F2B88B) 2D orthographic military hangar stage.",
        "beats": [
            {
                "id": "SC06_I1",
                "quote": "Năm một nghìn chín trăm bốn mươi ba, quân đội Mỹ đau đầu tìm cách bọc giáp cho máy bay ném bom.",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) hangar stage: a 1943 military briefing room with two army generals in green peaked caps scratching their heads beside a large wall chalkboard showing a twin-engine bomber airplane blueprint.",
                "shot_type": "full_scene",
                "effect": "pan_right"
            },
            {
                "id": "SC06_I2",
                "quote": "Nhìn những chiếc máy bay bay về chi chít lỗ đạn ở cánh và thân,",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: a crude 2D propeller bomber plane sits on the runway, its wide wings and fuselage covered in dozens of prominent red marker bullet hole dots.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC06_I3",
                "quote": "các tướng lĩnh phán ngay: Thủng ở đâu, bọc thép dày vào đó!",
                "desc": "Raw 2D doodle on pale ice-blue (#CBE0E0) stage: an eager general stickman holds a paintbrush and a heavy metal plate, trying to bolt heavy steel armor plates right onto the bullet-riddled outer wings of the plane.",
                "shot_type": "full_scene",
                "effect": "pan_left"
            },
            {
                "id": "SC06_I4",
                "quote": "Đúng lúc ấy, nhà toán học A-bờ-ra-ham Oan đập bàn can lại: Các ông sai bét rồi! Chỗ cần bọc giáp nhất chính là động cơ, nơi chẳng có vết đạn nào cả!",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: mathematician Abraham Wald with round glasses slams his hand down onto the drafting table, holding a black ruler pointing firmly at the clean, undamaged engines of the aircraft blueprint with an exclamation mark.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            }
        ]
    },
    {
        "id": "SC07",
        "title": "Vết đạn ở cánh vs Động cơ sống còn ngoài đời",
        "purpose": "Bóc tách vết đạn vô hại ở cánh vs động cơ sống còn ngoài đời thực (vốn dự phòng, quan hệ, thời thế)",
        "narration": "Vì sao lại thế? Vì những chiếc bị bắn thủng động cơ đã nổ tung dưới đáy biển, làm gì có cơ hội lết về căn cứ để các ông đếm đạn? Áp vào đời thực cũng y như vậy. Khi bạn bắt chước cách người thành công ăn mặc, dậy sớm hay phát ngôn, bạn chỉ đang chăm chăm bọc giáp vào những vết đạn vô hại ở cánh. Còn thứ thực sự giúp họ sống sót, như vốn dự phòng dày cộp, quan hệ ngầm hay thời thế, họ giấu nhẹm đi hoặc chính họ cũng chẳng nhận ra.",
        "setting": "Flat slate-navy (#2E4361) and warm paper-cream (#F8F0DC) 2D orthographic comparison stage.",
        "beats": [
            {
                "id": "SC07_I1",
                "quote": "Vì sao lại thế? Vì những chiếc bị bắn thủng động cơ đã nổ tung dưới đáy biển, làm gì có cơ hội lết về căn cứ để các ông đếm đạn?",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) underwater ocean floor stage: deep blue sea depths where a destroyed bomber plane with shattered smoking engines rests on the seabed surrounded by small cartoon rising bubbles.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            },
            {
                "id": "SC07_I2",
                "quote": "Áp vào đời thực cũng y như vậy. Khi bạn bắt chước cách người thành công ăn mặc, dậy sớm hay phát ngôn, bạn chỉ đang chăm chăm bọc giáp vào những vết đạn vô hại ở cánh.",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: the blue-shirt stickman frantically buys superficial items: wearing a fake luxury necktie, holding a takeaway coffee, and pointing to a 4:00 AM alarm, with a black marker arrow labeled VẾT ĐẠN VÔ HẠI.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC07_I3",
                "quote": "Còn thứ thực sự giúp họ sống sót, như vốn dự phòng dày cộp, quan hệ ngầm hay thời thế,",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) stage: a deep two-layer comparison stage. The small top tier shows a smiling stickman holding a tiny sign BÍ QUYẾT TRÊN MẠNG; the massive bottom foundation shows a giant solid steel vault labeled VỐN DÀY and two clasped hands labeled QUAN HỆ.",
                "shot_type": "full_scene",
                "effect": "pan_right"
            },
            {
                "id": "SC07_I4",
                "quote": "họ giấu nhẹm đi hoặc chính họ cũng chẳng nhận ra.",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: a successful influencer stickman stands behind a smiling stage mask holding a microphone, while behind his back is an enormous locked steel door concealing his family wealth and backup safety net.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            }
        ]
    },
    {
        "id": "SC08",
        "title": "Tư duy Trừ Lùi của Charlie Munger",
        "purpose": "Giới thiệu vũ khí Tư duy Trừ Lùi của Charlie Munger: không nhảy xuống vực, loại bỏ những việc chắc chắn dẫn đến thất bại",
        "narration": "Huyền thoại đầu tư Sạc-li Mân-gơ từng nói: Muốn đến đích, việc đầu tiên là đừng tự nhảy xuống vực. Đó là Tư duy Trừ Lùi. Người đời thường mù quáng đi tìm công thức để thành công, nhưng kẻ khôn ngoan lại lập danh sách những việc chắc chắn dẫn đến cái chết, để tránh xa. Đừng hỏi làm sao để kiếm triệu đô sau một đêm. Hãy hỏi: làm thế nào để dù thị trường có sập, bản thân vẫn không phá sản.",
        "setting": "Flat warm paper-cream (#F8F0DC) and soft sage-green (#93A88C) 2D orthographic strategy stage.",
        "beats": [
            {
                "id": "SC08_I1",
                "quote": "Huyền thoại đầu tư Sạc-li Mân-gơ từng nói: Muốn đến đích, việc đầu tiên là đừng tự nhảy xuống vực. Đó là Tư duy Trừ Lùi.",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: an elderly wise stickman with round glasses (Charlie Munger) points with a walking stick at a sharp cliff edge where a large red skull sign warns: ĐỪNG NHẢY XUỐNG VỰC!",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC08_I2",
                "quote": "Người đời thường mù quáng đi tìm công thức để thành công, nhưng kẻ khôn ngoan lại lập danh sách những việc chắc chắn dẫn đến cái chết, để tránh xa.",
                "desc": "Raw 2D doodle on pale ice-blue (#CBE0E0) stage: a giant wooden checklist board on which the stickman crosses out fatal traps with bold red X marks: VAY LÃI CAO (crossed out), TẤT TAY MỘT CỬA (crossed out), ẢO TƯỞNG LÀM GIÀU (crossed out).",
                "shot_type": "full_scene",
                "effect": "pan_left"
            },
            {
                "id": "SC08_I3",
                "quote": "Đừng hỏi làm sao để kiếm triệu đô sau một đêm.",
                "desc": "Raw 2D doodle on apricot-peach (#F2B88B) stage: a gambler stickman reaching hungrily for a shiny gold pot perched precariously over a deep pit, with a giant red warning question mark hovering above.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC08_I4",
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
        "purpose": "Đòn kết liễu đanh thép, sâu cay: tự hỏi kẻ thất bại đang ở đâu dưới đáy biển, bọc giáp cho tử huyệt trước khi cất cánh",
        "narration": "Bắt chước người chiến thắng chỉ biến bạn thành một bản sao mệt mỏi. Lần tới, khi thấy ai đó khoe mẽ hào quang rực rỡ, đừng vội cắm đầu làm theo. Hãy tự hỏi: những kẻ làm y hệt họ mà thất bại, giờ đang nằm ở đâu dưới đáy biển? Bọc giáp cho tử huyệt của mình trước, giữ cho mình sống sót đã, rồi thành công mới chịu đến lượt bạn.",
        "setting": "Flat slate-navy (#2E4361) and warm paper-cream (#F8F0DC) 2D orthographic takeoff stage.",
        "beats": [
            {
                "id": "SC09_I1",
                "quote": "Bắt chước người chiến thắng chỉ biến bạn thành một bản sao mệt mỏi.",
                "desc": "Raw 2D doodle on slate-navy (#2E4361) stage: the blue-shirt stickman looks into a full-length dressing mirror and sees himself as an exhausted puppet with tangled strings, realizing blind imitation only drains his soul.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC09_I2",
                "quote": "Lần tới, khi thấy ai đó khoe mẽ hào quang rực rỡ, đừng vội cắm đầu làm theo. Hãy tự hỏi: những kẻ làm y hệt họ mà thất bại, giờ đang nằm ở đâu dưới đáy biển?",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) stage: the stickman stands holding a magnifying glass, looking past a glowing TV screen showing an influencer, peering down into the deep blue ocean where sunken airplanes rest peacefully.",
                "shot_type": "full_scene",
                "effect": "pan_right"
            },
            {
                "id": "SC09_I3",
                "quote": "Bọc giáp cho tử huyệt của mình trước, giữ cho mình sống sót đã,",
                "desc": "Raw 2D doodle on soft sage-green (#93A88C) stage: the stickman confidently uses a wrench to bolt a thick solid steel armor plate over his chest engine, eyes determined and resolute, standing solidly on the ground.",
                "shot_type": "full_scene",
                "effect": "punch_in"
            },
            {
                "id": "SC09_I4",
                "quote": "rồi thành công mới chịu đến lượt bạn.",
                "desc": "Raw 2D doodle on warm paper-cream (#F8F0DC) sunrise stage: the sturdy 2D propeller airplane with gleaming armored engines takes off smoothly into the bright open sky, soaring high above the clouds toward the morning sun.",
                "shot_type": "full_scene",
                "effect": "zoom_out"
            }
        ]
    }
]

def build():
    print("Building Brief 4...")
    brief_data = {
        "schema_version": "3.0",
        "topic": "Bẫy Người Sống Sót (Survivorship Bias) & Tư Duy Trừ Lùi",
        "audience": "Người trẻ đi làm, người khởi nghiệp, người bước từ trường lớp ra xã hội tại Việt Nam",
        "goal": "Giải mã Thiên kiến Kẻ Sống Sót từ áp lực bắt chước thủ khoa trong trường học đến cú ngã vỡ mộng ngoài xã hội, tái hiện bài toán máy bay ném bom năm 1943 của Abraham Wald, và trao vũ khí Tư duy Trừ Lùi của Charlie Munger để bọc giáp cho tử huyệt trước khi cất cánh.",
        "video_type": "research_explainer",
        "duration": {
            "min_seconds": 120.0,
            "max_seconds": 180.0
        },
        "scene_count": 9,
        "required_points": [
            {"id": "R01", "text": "Mở bài bằng cú tát nhận thức: Bắt chước người giỏi nhất là cách nhanh nhất để bạn kiệt sức và bế tắc, từ trường học ra xã hội."},
            {"id": "R02", "text": "Trong trường học, người ta tôn vinh thủ khoa và áp lực cày cuốc thâu đêm nhưng điểm số vẫn lẹt đẹt, cơ thể suy nhược."},
            {"id": "R03", "text": "Bản chất trường học chỉ thưởng cho người về đích đầu tiên, xóa sổ hàng trăm người kiệt sức; bạn chỉ thấy kẻ sống sót."},
            {"id": "R04", "text": "Bước ra ngoài đời không có đáp án mẫu, mạng xã hội tràn ngập hình mẫu 20 tuổi triệu đô khuyên liều lĩnh thoát vùng an toàn."},
            {"id": "R05", "text": "Nghỉ việc lao theo đam mê rồi trắng tay ôm nợ; sự thật là những kẻ sạt nghiệp đã biến mất trong im lặng, không có micro hay sách báo."},
            {"id": "R06", "text": "Ví dụ lịch sử 1943 của không quân Mỹ và cú đập bàn của Abraham Wald: chỗ cần bọc giáp nhất chính là động cơ không có vết đạn."},
            {"id": "R07", "text": "Bóc tách vết đạn vô hại ở cánh vs động cơ sống còn ngoài đời thực (vốn dự phòng dày cộp, quan hệ ngầm, thời thế)."},
            {"id": "R08", "text": "Vũ khí Tư duy Trừ Lùi của Charlie Munger: không tự nhảy xuống vực, loại bỏ những việc chắc chắn dẫn đến thất bại."},
            {"id": "R09", "text": "Đòn kết liễu đanh thép: Tự hỏi kẻ thất bại đang ở đâu dưới đáy biển, bọc giáp cho tử huyệt của mình trước khi nghĩ đến thành công."}
        ],
        "language": "vi",
        "tone": "Điềm đạm, ấm áp, thông tuệ, gần gũi, đanh thép, không lê thê",
        "style": STYLE_170,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": [
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
                "title": "Fooled by Randomness: The Hidden Role of Chance in Life and in the Markets",
                "reference": "Nassim Nicholas Taleb (2001). Random House. ISBN: 978-0812975215.",
                "facts": [
                    "Nghĩa địa vô hình của người thất bại luôn bị truyền thông bỏ qua.",
                    "Tri thức tiêu cực tập trung vào việc loại bỏ sai lầm."
                ]
            },
            {
                "id": "SRC03",
                "title": "Poor Charlie's Almanack: The Wit and Wisdom of Charles T. Munger",
                "reference": "Peter D. Kaufman (2005). Donning Company Publishers. ISBN: 978-1578643035.",
                "facts": [
                    "Nguyên lý nghịch đảo giúp tránh xa những cái chết ngu ngốc.",
                    "Biên độ an toàn bảo vệ con người trước biến cố bất ngờ."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "vi",
                "subtitles": True,
                "voice": "VietNarrator",
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Giải mã Thiên kiến Kẻ Sống Sót từ trường học ra xã hội, bài toán máy bay ném bom 1943 của Abraham Wald, và vũ khí Tư duy Trừ Lùi của Charlie Munger với lời văn sắc bén, đanh thép, không lê thê."
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
            "author_raw_input": "Giải mã Thiên kiến Kẻ Sống Sót (Survivorship Bias) từ hành trình người giỏi trong trường lớp ra ngoài xã hội. Giữ vững ví dụ máy bay năm 1943 của Abraham Wald và Tư duy Trừ Lùi của Charlie Munger bằng ngôn ngữ nói đời thường, sắc bén, đanh thép, không lê thê.",
            "dynamic_questions": [
                "Vì sao làm đúng từng gạch đầu dòng của người thành công lại dẫn đến phá sản?",
                "Đâu là vết đạn vô hại ở cánh, đâu là động cơ sống còn ngoài đời thực?",
                "Tại sao người khôn ngoan lại lập danh sách những việc dẫn đến cái chết để tránh xa thay vì tìm công thức làm giàu?"
            ],
            "expanded_content_ideas": [
                {
                    "angle_type": "analysis",
                    "idea_summary": "Bóc trần ảo tưởng trường học và mạng xã hội: chỉ tôn vinh kẻ sống sót duy nhất.",
                    "narrative_integration": "Triển khai xuyên suốt SC01 đến SC05."
                },
                {
                    "angle_type": "commentary",
                    "idea_summary": "Ví dụ Abraham Wald 1943 và liên hệ vết đạn vô hại ở cánh vs động cơ sống còn.",
                    "narrative_integration": "Triển khai tại SC06 và SC07."
                },
                {
                    "angle_type": "evaluation",
                    "idea_summary": "Vũ khí Tư duy Trừ Lùi của Charlie Munger và đòn kết liễu đanh thép.",
                    "narrative_integration": "Triển khai tại SC08 và SC09."
                }
            ]
        },
        "visual_pacing_profile": "full_frame_v1",
        "enforce_phonetic_gate": True
    }

    brief_path = BRIEFS_DIR / "4.json"
    brief_text = json.dumps(brief_data, indent=2, ensure_ascii=False) + "\n"
    brief_path.write_text(brief_text, encoding="utf-8")
    brief_hash = hashlib.sha256(brief_text.encode("utf-8")).hexdigest()
    print(f"Brief 4 written: {brief_path} (hash: {brief_hash[:8]}...)")

    # Update brief-current.json
    brief_cur = {
        "revision": 4,
        "hash": brief_hash
    }
    (RUN_DIR / "brief-current.json").write_text(json.dumps(brief_cur, indent=2) + "\n", encoding="utf-8")

    print("Building Content Revision 4...")
    scenes = []
    for sc_data in SCENES_DATA:
        sc_id = sc_data["id"]
        narration = sc_data["narration"]
        images = []
        beats = []
        for b in sc_data["beats"]:
            img_id = b["id"]
            quote = b["quote"]
            desc = b["desc"]
            shot_type = b["shot_type"]
            effect = b["effect"]

            assert quote in narration, f"Quote {quote!r} not in narration of {sc_id}"

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
                    "source_terms": [quote.split()[-1]],
                    "visual_terms": [desc[:40]]
                }
            })

            beats.append({
                "id": img_id.replace("_I", "_B"),
                "image_id": img_id,
                "purpose": sc_data["purpose"],
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

        scenes.append({
            "id": sc_id,
            "title": sc_data["title"],
            "purpose": sc_data["purpose"],
            "action": sc_data["beats"][0]["desc"],
            "setting": sc_data["setting"],
            "camera": "Narration-led full-frame compositions",
            "narration": narration,
            "requirements": [f"R{int(sc_id[-2:]):02d}"],
            "character_ids": ["CH01"],
            "source_ids": [],
            "images": images,
            "beats": beats
        })

    content_data = {
        "schema_version": "3.0",
        "brief_revision": 4,
        "brief_hash": brief_hash,
        "topic": brief_data["topic"],
        "duration": brief_data["duration"],
        "style": STYLE_170,
        "required_points": [rp["text"] for rp in brief_data["required_points"]],
        "characters": [
            {
                "id": "CH01",
                "name": "Nhân vật người que đầu tròn trắng doodle 2D",
                "appearance": STICKMAN_APPEARANCE,
                "outfit": STICKMAN_OUTFIT
            }
        ],
        "scenes": scenes,
        "coverage": {
            "requirements": {f"R{i+1:02d}": f"SC{i+1:02d}" for i in range(len(scenes))},
            "sources": {}
        },
        "outline": [
            {"id": sc["id"], "title": sc["title"], "purpose": sc["purpose"]}
            for sc in scenes
        ],
        "claims": [],
        "revision_response": "Tái thiết kế toàn bộ 9 cảnh theo chuẩn văn nói đanh thép, phản biện sắc bén, khử AI Slop trong tạo hình.",
        "open_questions": [],
        "enforce_phonetic_gate": True
    }

    content_text = json.dumps(content_data, indent=2, ensure_ascii=False) + "\n"
    content_file = CONTENT_REV_DIR / "content.json"
    content_file.write_text(content_text, encoding="utf-8")
    print(f"Content 4 written: {content_file} ({len(scenes)} scenes)")

    # Update draft files
    draft_content_file = DRAFT_DIR / "content.json"
    draft_content_file.write_text(content_text, encoding="utf-8")
    
    draft_outline = {
        "schema_version": "3.0",
        "brief_revision": 4,
        "brief_hash": brief_hash,
        "topic": brief_data["topic"],
        "scenes": content_data["outline"]
    }
    (DRAFT_DIR / "outline.json").write_text(json.dumps(draft_outline, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Draft updated successfully.")

if __name__ == "__main__":
    build()
