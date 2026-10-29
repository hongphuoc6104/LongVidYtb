#!/usr/bin/env python3
"""Build brief 3 and content revision 3 for survivorship-bias-16x9 from the approved v3 script.

Each scene is declared as narration plus an ordered list of (anchor_quote, image_ref) beats.
``image_ref`` is either a v2 image id (reused from revisions/images/5_full_doodle) or a dict
describing a NEW full-frame doodle image that must be generated through Flow CDP.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs/survivorship-bias-16x9"
SRC_CONTENT = RUN / "revisions/content/2/content.json"
OUT_CONTENT_DIR = RUN / "revisions/content/3"
REUSE_MAP_PATH = OUT_CONTENT_DIR / "image_reuse_map.json"

CH = "the white-head doodle stickman in a casual cerulean blue shirt (#3B82C4)"
GATES = (
    "teenage Bill Gates drawn as a white-head doodle stickman with large square black-rimmed "
    "glasses and a cerulean blue shirt (#3B82C4)"
)


def new(desc: str, shot: str, has_char: bool = False, text: list[dict[str, str]] | None = None,
        chars: list[str] | None = None) -> dict[str, Any]:
    return {"desc": desc, "shot": shot, "has_char": has_char, "text": text or [], "chars": chars or []}


SCENES: list[dict[str, Any]] = [
    {
        "id": "SC01",
        "title": "Cú tát đầu tiên",
        "purpose": "Mở bài bằng nghịch lý: bắt chước người thành công là cách nhanh nhất để trắng tay, qua nửa câu chuyện bị giấu của Bill Gates",
        "narration": (
            "Bắt chước người thành công là cách nhanh nhất để bạn trắng tay. "
            "Bạn nghe chuyện Bin Ghết bỏ học Ha-vớt rồi thành tỷ phú. "
            "Nghe xong, bạn tin rằng bằng cấp là thứ vô dụng. "
            "Nhưng không ai kể nốt nửa còn lại: năm mười ba tuổi, Bin Ghết đã được ngồi trước máy tính, "
            "thứ mà cả thế giới lúc đó chưa mấy ai được chạm vào. Bố ông là luật sư có tiếng. "
            "Mẹ ông ngồi cùng ban điều hành một quỹ từ thiện lớn với Chủ tịch Ai-bi-em, "
            "và nhiều người cho rằng mối quen biết đó đã mở đường cho bản hợp đồng làm nên Mai-crô-xốp."
        ),
        "beats": [
            ("Bắt chước người thành công", new(f"Flat 2D orthographic stage on a warm paper-cream (#F8F0DC) field: {CH} copies the exact victory pose of a trophy-holding winner stickman in a dark blazer standing beside him.", "full_scene", True, chars=["CH01"])),
            ("để bạn trắng tay", new("Flat 2D orthographic close-up on an apricot-peach (#F2B88B) field: an empty brown leather wallet turned inside out with two small moths fluttering out.", "still_life")),
            ("Bạn nghe chuyện Bin Ghết", new(f"Flat 2D orthographic frame on a pale ice-blue (#CBE0E0) field: {GATES}, now a young adult, walks out through an old brick university gate carrying a backpack.", "full_scene", True)),
            ("rồi thành tỷ phú", new("Flat 2D orthographic frame on a soft sage-green (#93A88C) field: a young white-head doodle stickman with large square black-rimmed glasses stands on top of a tall pile of gold coins.", "full_scene", True)),
            ("bằng cấp là thứ vô dụng", new("Flat 2D orthographic close-up on a warm paper-cream (#F8F0DC) field: a rolled university diploma with a red ribbon being dropped into a small wire trash bin.", "still_life")),
            ("Nhưng không ai kể nốt nửa còn lại", new("Flat 2D orthographic card on a stark pure-white (#FFFFFF) canvas: an open storybook torn down the middle, its right half hidden behind a heavy black curtain.", "visual_diagram")),
            ("năm mười ba tuổi", new(f"Flat 2D side-on orthographic school computer room on a warm paper-cream (#F8F0DC) stage: {GATES}, a 13-year-old boy, types on a bulky 1968 teletype terminal with a paper roll feeding out.", "full_scene", True)),
            ("thứ mà cả thế giới", new("Flat 2D orthographic diagram on a slate-navy (#2E4361) field: a flat world map where only one single tiny yellow computer dot is lit and every other region stays dark.", "visual_diagram")),
            ("Bố ông là luật sư có tiếng", new("Flat 2D orthographic office on a pale ice-blue (#CBE0E0) field: a tall respected lawyer white-head doodle stickman in a dark grey suit holds a briefcase beside a brass scale of justice.", "full_scene", True)),
            ("Mẹ ông ngồi cùng ban điều hành", new("Flat 2D side-on orthographic charity boardroom on a warm paper-cream (#F8F0DC) stage: a mother white-head doodle stickman with a short bob hairstyle and a red dress sits at a long table beside a grey-haired corporate chairman stickman in a navy suit.", "full_scene", True)),
            ("mối quen biết đó", new("Flat 2D orthographic close-up on an apricot-peach (#F2B88B) field: a friendly handshake between a woman's white circle hand with a red sleeve and a man's white circle hand with a navy suit sleeve, a small mainframe computer cabinet behind them.", "cutaway_detail")),
            ("bản hợp đồng làm nên Mai-crô-xốp", new("Flat 2D orthographic close-up on a soft sage-green (#93A88C) field: a signed paper contract with a fountain pen resting beside a blue floppy disk.", "still_life")),
        ],
    },
    {
        "id": "SC02",
        "title": "Ngay cạnh nhà bạn",
        "purpose": "Kéo nghịch lý về đời thực Việt Nam: quán cà phê đầu ngõ, làm y hệt rồi treo biển sang nhượng vì không thấy lợi thế ngầm; gọi tên Bẫy Người Sống Sót",
        "narration": (
            "Bin Ghết không bỏ học để đi tìm may mắn. Ông bỏ học khi đã cầm sẵn tấm vé trong tay. "
            "Chuyện này không chỉ xảy ra ở Mỹ. Đầu ngõ có quán cà phê đông nghịt, bạn dốc tiền tiết kiệm làm y hệt, "
            "từ bảng hiệu đến ly nước. Sáu tháng sau, bạn treo biển sang nhượng. "
            "Bạn không biết mặt bằng kia là nhà của họ, không mất một đồng tiền thuê. "
            "Và sau lưng họ là một khoản tiền đủ gồng lỗ cả năm. "
            "Bạn không thua vì kém. Bạn thua vì chỉ được xem một nửa câu chuyện. "
            "Cái bẫy đó có tên: Bẫy Người Sống Sót. Hiểu nó, bạn sẽ biết lúc nào nên học người khác, "
            "và lúc nào phải dừng tay trước khi mất tiền."
        ),
        "beats": [
            ("Bin Ghết không bỏ học", new("Flat 2D orthographic frame on a pale ice-blue (#CBE0E0) field: a young white-head doodle stickman with large square black-rimmed glasses walks calmly out of a university gate, not looking at a spinning lucky dice beside the road.", "full_scene", True)),
            ("cầm sẵn tấm vé trong tay", new("Flat 2D orthographic close-up on a warm paper-cream (#F8F0DC) field: a white circle hand firmly holding one bright golden admission ticket.", "cutaway_detail")),
            ("Chuyện này không chỉ xảy ra ở Mỹ", new("Flat 2D orthographic diagram on a stark pure-white (#FFFFFF) canvas: a simple flat world map with a dashed black arrow arcing from North America to Vietnam.", "visual_diagram")),
            ("Đầu ngõ có quán cà phê đông nghịt", new("Flat 2D front-on orthographic Vietnamese alley on a warm paper-cream (#F8F0DC) stage: a busy small coffee shop with low plastic stools packed with many white-head doodle stickman customers.", "environment")),
            ("bạn dốc tiền tiết kiệm", "SC02_I1"),
            ("từ bảng hiệu đến ly nước", "SC07_I2"),
            ("bạn treo biển sang nhượng", new(f"Flat 2D front-on orthographic shuttered coffee shop on a slate-navy (#2E4361) evening stage: {CH} hangs a hand-written sign on the closed metal shutter.", "full_scene", True, text=[{"text": "SANG NHƯỢNG", "placement": "center of the hanging sign", "object": "sign"}], chars=["CH01"])),
            ("mặt bằng kia là nhà của họ", new("Flat 2D front-on orthographic Vietnamese tube house on a soft sage-green (#93A88C) field: a busy coffee shop on the ground floor while a family waters plants on the balcony upstairs of the same house.", "environment", True)),
            ("sau lưng họ là một khoản tiền", new("Flat 2D orthographic frame on an apricot-peach (#F2B88B) field: a relaxed coffee shop owner white-head doodle stickman in an apron stands in front of a huge hidden stack of green banknote bundles behind him.", "full_scene", True)),
            ("Bạn không thua vì kém", "SC02_I6"),
            ("chỉ được xem một nửa câu chuyện", "SC01_I3"),
            ("Cái bẫy đó có tên", "SC02_I7"),
            ("lúc nào phải dừng tay", new(f"Flat 2D orthographic frame on a pale ice-blue (#CBE0E0) field: {CH} raises one hand in a firm stop gesture at the edge of a dashed line, a red stop circle beside him.", "full_scene", True, chars=["CH01"])),
        ],
    },
    {
        "id": "SC03",
        "title": "Vì sao bạn chỉ thấy người thắng",
        "purpose": "Giải thích cách thuật toán và truyền thông lọc lấy 1 người thắng và xóa 999 người thất bại khỏi tầm mắt",
        "narration": (
            "Cứ một nghìn người mở quán, một người thành công sẽ lên mạng chia sẻ bí quyết, ra khóa học, viết sách. "
            "Chín trăm chín mươi chín người còn lại thì sao? Họ lặng lẽ đóng cửa, đi làm thuê lại, "
            "và chẳng ai quay video kể chuyện mình vừa mất trắng. "
            "Thuật toán chỉ đẩy lên màn hình người duy nhất còn đứng. "
            "Não bạn nhìn vào đó và tưởng rằng ai làm cũng thắng."
        ),
        "beats": [
            ("Cứ một nghìn người mở quán", "SC03_I2"),
            ("một người thành công sẽ lên mạng", "SC03_I3"),
            ("ra khóa học, viết sách", "SC03_I4"),
            ("Chín trăm chín mươi chín người", "SC03_I5"),
            ("Họ lặng lẽ đóng cửa", "SC03_I7"),
            ("đi làm thuê lại", "SC03_I6"),
            ("chẳng ai quay video", "SC03_I8"),
            ("Thuật toán chỉ đẩy lên màn hình", "SC03_I9"),
            ("Não bạn nhìn vào đó", "SC02_I8"),
            ("ai làm cũng thắng", "SC03_I10"),
        ],
    },
    {
        "id": "SC04",
        "title": "Đánh tráo nguyên nhân",
        "purpose": "Bóc tách sai lầm nhầm thói quen thành nguyên nhân qua ví dụ dậy lúc 4 giờ sáng",
        "narration": (
            "Cái nguy hiểm nhất của bẫy này: nó khiến ta nhầm thói quen thành nguyên nhân. "
            "Tỷ phú dậy lúc bốn giờ sáng, ta tin dậy sớm làm nên giàu có. "
            "Nhưng người bán bánh mì, chị lao công, anh công nhân ca đêm cũng dậy lúc bốn giờ sáng, mỗi ngày, suốt nhiều năm. "
            "Họ vẫn chật vật. Dậy sớm không sai. Nó chỉ không phải lý do người kia giàu."
        ),
        "beats": [
            ("Cái nguy hiểm nhất của bẫy này", "SC04_I1"),
            ("nhầm thói quen thành nguyên nhân", "SC04_I3"),
            ("Tỷ phú dậy lúc bốn giờ sáng", "SC04_I4"),
            ("ta tin dậy sớm làm nên giàu có", "SC04_I5"),
            ("Nhưng người bán bánh mì", "SC04_I6"),
            ("anh công nhân ca đêm", "SC04_I7"),
            ("Họ vẫn chật vật", "SC04_I8"),
            ("Dậy sớm không sai", "SC04_I9"),
            ("Nó chỉ không phải lý do", "SC04_I11"),
        ],
    },
    {
        "id": "SC05",
        "title": "Năm 1943, những chiếc máy bay trở về",
        "purpose": "Kể bài toán năm 1943 của quân đội Mỹ và trực giác sai khi đòi bọc thép chỗ thủng nhiều nhất",
        "narration": (
            "Ngay cả những bộ óc giỏi nhất cũng từng rơi vào bẫy này. "
            "Năm một nghìn chín trăm bốn mươi ba, quân đội Mỹ muốn bọc thêm thép cho máy bay ném bom. "
            "Họ kiểm tra những chiếc bay về và thấy cánh, thân chi chít lỗ đạn. "
            "Còn động cơ và buồng lái gần như nguyên vẹn. "
            "Kết luận được đưa ra ngay: chỗ nào thủng nhiều, bọc thép chỗ đó."
        ),
        "beats": [
            ("Ngay cả những bộ óc", "SC05_I1"),
            ("Năm một nghìn chín trăm", "SC05_I2"),
            ("quân đội Mỹ muốn bọc thêm thép", "SC05_I3"),
            ("Họ kiểm tra những chiếc bay về", "SC05_I4"),
            ("cánh, thân chi chít lỗ đạn", "SC05_I5"),
            ("Còn động cơ và buồng lái", "SC05_I6"),
            ("Kết luận được đưa ra ngay", "SC05_I7"),
            ("chỗ nào thủng nhiều", "SC05_I8"),
            ("bọc thép chỗ đó", "SC05_I9"),
        ],
    },
    {
        "id": "SC06",
        "title": "Câu hỏi của Abraham Wald",
        "purpose": "Cú lật ngược của Abraham Wald: chỗ sạch trơn không một vết xước mới là chỗ chết người",
        "narration": (
            "Nhà thống kê A-bờ-ra-ham Oan chặn quyết định đó bằng đúng một câu hỏi: "
            "những chiếc bị bắn vào động cơ đang ở đâu? Chúng không có mặt ở sân bay. Chúng đã rơi xuống biển. "
            "Lỗ đạn trên cánh không phải điểm yếu. Đó là bằng chứng máy bay bị bắn vào đó vẫn bay về được. "
            "Chỗ sạch trơn không một vết xước, mới là chỗ chết người."
        ),
        "beats": [
            ("Nhà thống kê", "SC06_I1"),
            ("bằng đúng một câu hỏi", "SC06_I2"),
            ("những chiếc bị bắn vào động cơ", "SC06_I5"),
            ("đang ở đâu", "SC06_I3"),
            ("Chúng không có mặt ở sân bay", "SC06_I4"),
            ("Chúng đã rơi xuống biển", "SC06_I6"),
            ("Lỗ đạn trên cánh", "SC06_I7"),
            ("Đó là bằng chứng", "SC06_I8"),
            ("vẫn bay về được", "SC06_I9"),
            ("Chỗ sạch trơn", "SC06_I10"),
        ],
    },
    {
        "id": "SC07",
        "title": "Vết đạn và động cơ của đời bạn",
        "purpose": "Liên hệ máy bay với đời thực: bảng hiệu, trang trí là vết đạn; mặt bằng, vốn, quan hệ, thời điểm là động cơ; Bill Gates cũng vậy",
        "narration": (
            "Quay lại quán cà phê đầu ngõ. Bảng hiệu, cách trang trí, công thức pha chế, đó là vết đạn trên cánh. "
            "Ai cũng thấy, ai cũng chép được, và chúng không quyết định sống chết. "
            "Động cơ thật là thứ không ai quay lên mạng: mặt bằng không tốn tiền thuê, vốn đủ gồng hai năm, "
            "mối quan hệ, hay đơn giản là vào thị trường lúc chưa ai làm. "
            "Bin Ghết cũng vậy. Bỏ học là vết đạn. "
            "Máy tính năm mười ba tuổi và cái bắt tay với Ai-bi-em mới là động cơ."
        ),
        "beats": [
            ("Quay lại quán cà phê đầu ngõ", new("Flat 2D front-on orthographic Vietnamese alley on a pale ice-blue (#CBE0E0) stage: the same busy small coffee shop seen again, with red dashed bullet-hole marks drawn over its signboard and decorations.", "environment")),
            ("Bảng hiệu, cách trang trí", "SC07_I2"),
            ("đó là vết đạn trên cánh", "SC07_I4"),
            ("Ai cũng thấy, ai cũng chép được", new("Flat 2D front-on orthographic street on a warm paper-cream (#F8F0DC) field: a row of four identical copycat coffee shops side by side with the same awning and the same signboard shape.", "environment")),
            ("Động cơ thật", "SC07_I5"),
            ("không ai quay lên mạng", "SC07_I10"),
            ("mặt bằng không tốn tiền thuê", "SC07_I7"),
            ("vốn đủ gồng hai năm", "SC07_I8"),
            ("mối quan hệ", new("Flat 2D orthographic diagram on a soft sage-green (#93A88C) field: five white-head doodle stickmen in different shirts linked by bold black lines into a small network, two of them shaking hands in the center.", "visual_diagram", True)),
            ("vào thị trường lúc chưa ai làm", "SC07_I9"),
            ("Bỏ học là vết đạn", new("Flat 2D top-down orthographic bomber wing on a stark pure-white (#FFFFFF) canvas: a rolled university diploma pinned onto the outer wing among small red bullet-hole dots.", "visual_diagram")),
            ("Máy tính năm mười ba tuổi", new("Flat 2D orthographic cutaway on a slate-navy (#2E4361) field: a heavy blue steel-armored aircraft engine opened to reveal a bulky 1968 teletype terminal and a handshake icon glowing yellow inside its core.", "visual_diagram")),
        ],
    },
    {
        "id": "SC08",
        "title": "Vậy có nên học người giỏi không?",
        "purpose": "Phân định ranh giới: kỹ năng luật chơi cố định thì học được; cuộc chơi may rủi mà chép nguyên công thức là mua lại vé số đã trúng",
        "narration": (
            "Vậy học người thành công là sai? Không hẳn. "
            "Với những việc có luật chơi cố định như viết code, sửa xe, tập thể hình, làm đúng phương pháp thì sẽ có kết quả. "
            "Nhưng trong kinh doanh, đầu tư hay nhảy việc, nơi may rủi chiếm phần lớn, "
            "chép nguyên công thức của người thắng chẳng khác gì mua lại tờ vé số vừa trúng độc đắc."
        ),
        "beats": [
            ("Vậy học người thành công", "SC08_I1"),
            ("Không hẳn", "SC08_I2"),
            ("luật chơi cố định", "SC08_I3"),
            ("viết code, sửa xe", "SC08_I4"),
            ("tập thể hình", "SC08_I5"),
            ("làm đúng phương pháp", "SC08_I6"),
            ("Nhưng trong kinh doanh", "SC08_I8"),
            ("nơi may rủi", "SC08_I7"),
            ("chép nguyên công thức", "SC08_I9"),
            ("tờ vé số", "SC08_I10"),
        ],
    },
    {
        "id": "SC09",
        "title": "Tư duy trừ lùi",
        "purpose": "Giới thiệu Tư duy Trừ Lùi của Charlie Munger và ẩn dụ người chơi cờ tránh nước tự sát",
        "narration": (
            "Sạc-li Mân-gơ, người cộng sự hơn bốn mươi năm của Oa-ren Bắp-phết, có một cách nghĩ ngược đời: "
            "đừng hỏi làm gì để thắng, hãy hỏi làm gì chắc chắn thua, rồi tránh xa nó. "
            "Người chơi cờ giỏi không thắng nhờ nước đi thiên tài. Họ thắng vì không đi nước tự sát."
        ),
        "beats": [
            ("Sạc-li Mân-gơ", "SC09_I1"),
            ("người cộng sự hơn bốn mươi năm", new("Flat 2D side-on orthographic office on a warm paper-cream (#F8F0DC) stage: two elderly investor white-head doodle stickmen, one with thick black glasses and a grey suit, one with a red tie, sit side by side at one long wooden desk reading reports.", "full_scene", True)),
            ("cách nghĩ ngược đời", "SC09_I2"),
            ("đừng hỏi làm gì để thắng", "SC09_I5"),
            ("làm gì chắc chắn thua", "SC09_I6"),
            ("rồi tránh xa nó", "SC09_I7"),
            ("Người chơi cờ giỏi", "SC09_I8"),
            ("nước đi thiên tài", "SC09_I9"),
            ("không đi nước tự sát", "SC09_I10"),
        ],
    },
    {
        "id": "SC10",
        "title": "Bước một: hỏi người đã thua",
        "purpose": "Thực hành Bước 1: tìm những người đã bỏ cuộc để thấy đá ngầm và chi phí ẩn",
        "narration": (
            "Trước mọi quyết định lớn về tiền hay sự nghiệp, hãy làm hai bước. "
            "Bước một: đừng hỏi ai đã giàu lên từ nó. Hãy tìm những người đã bỏ cuộc. "
            "Họ vấp ở đâu, chi phí ẩn là gì, và vì sao họ phải dừng lại. "
            "Đó chính là những chiếc máy bay dưới đáy biển."
        ),
        "beats": [
            ("Trước mọi quyết định lớn", "SC10_I1"),
            ("hãy làm hai bước", "SC10_I2"),
            ("đừng hỏi ai đã giàu lên", "SC10_I5"),
            ("Hãy tìm những người đã bỏ cuộc", "SC10_I6"),
            ("Họ vấp ở đâu", "SC10_I7"),
            ("chi phí ẩn là gì", "SC10_I8"),
            ("vì sao họ phải dừng lại", "SC10_I3"),
            ("những chiếc máy bay dưới đáy biển", "SC06_I6"),
        ],
    },
    {
        "id": "SC11",
        "title": "Bước hai: bọc thép cho động cơ của mình",
        "purpose": "Thực hành Bước 2: bảo vệ chỗ chết người (không vay lãi cao, không dồn một cửa, giữ quỹ sáu tháng)",
        "narration": (
            "Bước hai: bảo vệ chỗ chết người trước khi nghĩ đến lợi nhuận. "
            "Không vay lãi cao để thử một thứ mình mới nghe tên. Không dồn hết tiền vào một cửa. "
            "Và luôn giữ lại khoản đủ sống sáu tháng. Để nếu có rơi, bạn vẫn còn đứng dậy được."
        ),
        "beats": [
            ("Bước hai", "SC11_I1"),
            ("trước khi nghĩ đến lợi nhuận", "SC11_I2"),
            ("Không vay lãi cao", "SC11_I5"),
            ("mình mới nghe tên", "SC11_I6"),
            ("Không dồn hết tiền", "SC11_I7"),
            ("luôn giữ lại khoản", "SC11_I8"),
            ("Để nếu có rơi", "SC11_I9"),
            ("vẫn còn đứng dậy được", "SC11_I10"),
        ],
    },
    {
        "id": "SC12",
        "title": "Khép vòng lặp",
        "purpose": "Khép vòng: trước khi tin chuyện đổi đời, hỏi những người làm y hệt mà thất bại đang ở đâu; bọc thép động cơ rồi hẵng cất cánh",
        "narration": (
            "Tối nay mở điện thoại, bạn vẫn sẽ thấy những câu chuyện đổi đời. "
            "Lần này, trước khi tin, hãy hỏi một câu: những người làm y hệt mà thất bại, họ đang ở đâu? "
            "Đừng đếm vết đạn trên cánh người khác. "
            "Hãy nhìn xuống đáy biển, bọc thép cho động cơ của mình, rồi hẵng cất cánh."
        ),
        "beats": [
            ("Tối nay mở điện thoại", "SC12_I1"),
            ("những câu chuyện đổi đời", "SC12_I2"),
            ("Lần này, trước khi tin", "SC12_I4"),
            ("những người làm y hệt mà thất bại", "SC02_I9"),
            ("họ đang ở đâu", "SC12_I5"),
            ("Đừng đếm vết đạn", "SC12_I6"),
            ("Hãy nhìn xuống đáy biển", "SC12_I7"),
            ("bọc thép cho động cơ", "SC12_I8"),
            ("rồi hẵng cất cánh", "SC12_I9"),
        ],
    },
]

EFFECTS = ["zoom_in", "hold", "pan_right", "zoom_out", "hold", "pan_left", "zoom_in", "hold", "punch_in", "zoom_out"]

GATES_SOURCE = {
    "id": "SRC04",
    "title": "Hard Drive: Bill Gates and the Making of the Microsoft Empire",
    "reference": "James Wallace & Jim Erickson (1992). John Wiley & Sons. ISBN: 978-0471568865.",
    "facts": [
        "Năm 1968, trường Lakeside cho học sinh dùng máy Teletype nối với máy tính chia sẻ thời gian; Bill Gates khi đó mười ba tuổi.",
        "Cha Bill Gates là luật sư William H. Gates Sr.; mẹ Mary Gates ngồi trong ban điều hành United Way cùng Chủ tịch IBM John Opel.",
    ],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_brief() -> tuple[dict[str, Any], Path]:
    brief = json.loads((RUN / "briefs/2.json").read_text(encoding="utf-8"))
    brief["duration"] = {"min_seconds": 200.0, "max_seconds": 330.0}
    brief["scene_count"] = len(SCENES)
    brief["required_points"] = [
        {"id": f"R{idx:02d}", "text": sc["purpose"]} for idx, sc in enumerate(SCENES, start=1)
    ]
    if not any(s.get("id") == "SRC04" for s in brief.get("sources", [])):
        brief.setdefault("sources", []).append(GATES_SOURCE)
    path = RUN / "briefs/3.json"
    path.write_text(json.dumps(brief, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return brief, path


def occurrence_of(narration: str, quote: str, cursor: int) -> tuple[int, int]:
    pos = narration.find(quote, cursor)
    if pos < 0:
        raise ValueError(f"Anchor not found in order: {quote!r}")
    occ = narration.count(quote, 0, pos) + 1
    return occ, pos + len(quote)


def build_content(brief: dict[str, Any], brief_path: Path) -> None:
    src = json.loads(SRC_CONTENT.read_text(encoding="utf-8"))
    old_images = {img["id"]: img for sc in src["scenes"] for img in sc["images"]}
    old_scenes = {sc["id"]: sc for sc in src["scenes"]}
    content = copy.deepcopy(src)
    content["brief_revision"] = 3
    content["brief_hash"] = sha(brief_path)
    content["duration"] = brief["duration"]
    content["required_points"] = brief["required_points"]
    reuse_map: dict[str, str] = {}
    new_specs: dict[str, dict[str, Any]] = {}
    scenes_out = []
    for idx, spec in enumerate(SCENES, start=1):
        base = copy.deepcopy(old_scenes[spec["id"]])
        narration = spec["narration"]
        images, beats = [], []
        cursor = 0
        for b_idx, (quote, ref) in enumerate(spec["beats"], start=1):
            occ, cursor = occurrence_of(narration, quote, cursor)
            image_id = f"{spec['id']}_I{b_idx}"
            if isinstance(ref, str):
                img = copy.deepcopy(old_images[ref])
                reuse_map[image_id] = ref
            else:
                img = {
                    "description": ref["desc"],
                    "character_ids": ref["chars"],
                    "preserve": "",
                    "change": ref["desc"],
                    "reason": "Show the concrete object, comparison, or action at its spoken anchor.",
                    "visible_text": ref["text"],
                    "kind": "scene",
                    "shot_type": ref["shot"],
                    "has_character": ref["has_char"],
                }
                new_specs[image_id] = ref
            img["id"] = image_id
            img["based_on"] = None
            img["kind"] = "scene"
            img["explanation"] = {
                "quote": quote,
                "relation": "context",
                "source_terms": [quote],
                "visual_terms": [img["description"].split(": ", 1)[-1][:80]],
            }
            images.append(img)
            beats.append({
                "id": f"{spec['id']}_B{b_idx}",
                "image_id": image_id,
                "purpose": spec["purpose"],
                "anchor": {"vi": {"quote": quote, "occurrence": occ}},
                "effect": EFFECTS[(b_idx - 1 + idx) % len(EFFECTS)],
                "focus": {"x": 0.5, "y": 0.5},
            })
        base.update({
            "title": spec["title"],
            "purpose": spec["purpose"],
            "narration": narration,
            "requirements": [f"R{idx:02d}"],
            "images": images,
            "beats": beats,
            "action": images[0]["description"],
        })
        if spec["id"] in ("SC01", "SC02", "SC07"):
            base["source_ids"] = sorted(set(base.get("source_ids", [])) | {"SRC04"})
        scenes_out.append(base)
    content["scenes"] = scenes_out
    content["coverage"] = [
        {"requirement_id": f"R{i:02d}", "scene_id": sc["id"], "quote": sc["narration"].split(". ")[0].rstrip(".")}
        for i, sc in enumerate(SCENES, start=1)
    ]
    content["outline"] = [
        {"scene_id": sc["id"], "purpose": sc["purpose"], "requirements": [f"R{i:02d}"],
         "transition": "Tiếp tục theo trình tự diễn biến nội dung"}
        for i, sc in enumerate(SCENES, start=1)
    ]
    content["claims"] = [
        {"scene_id": "SC01", "quote": "năm mười ba tuổi, Bin Ghết đã được ngồi trước máy tính", "language": "vi",
         "source_id": "SRC04", "fact": GATES_SOURCE["facts"][0]},
        {"scene_id": "SC01", "quote": "Mẹ ông ngồi cùng ban điều hành một quỹ từ thiện lớn với Chủ tịch Ai-bi-em", "language": "vi",
         "source_id": "SRC04", "fact": GATES_SOURCE["facts"][1]},
        {"scene_id": "SC03", "quote": "Họ lặng lẽ đóng cửa, đi làm thuê lại, và chẳng ai quay video kể chuyện mình vừa mất trắng.",
         "language": "vi", "source_id": "SRC02", "fact": "Nghĩa địa vô hình của người thất bại luôn bị truyền thông bỏ qua."},
        {"scene_id": "SC05", "quote": "Họ kiểm tra những chiếc bay về và thấy cánh, thân chi chít lỗ đạn.", "language": "vi",
         "source_id": "SRC01", "fact": "Thống kê ban đầu chỉ ghi nhận dữ liệu từ những máy bay sống sót."},
        {"scene_id": "SC06", "quote": "những chiếc bị bắn vào động cơ đang ở đâu?", "language": "vi",
         "source_id": "SRC01", "fact": "Những chiếc máy bay trúng đạn vào động cơ và buồng lái không thể quay về."},
        {"scene_id": "SC06", "quote": "Chỗ sạch trơn không một vết xước, mới là chỗ chết người.", "language": "vi",
         "source_id": "SRC01", "fact": "Cần bọc thép vào vị trí máy bay không có lỗ đạn."},
        {"scene_id": "SC09", "quote": "đừng hỏi làm gì để thắng, hãy hỏi làm gì chắc chắn thua, rồi tránh xa nó.", "language": "vi",
         "source_id": "SRC03", "fact": "Nguyên lý nghịch đảo giúp tránh xa những cái chết ngu ngốc."},
        {"scene_id": "SC11", "quote": "Và luôn giữ lại khoản đủ sống sáu tháng.", "language": "vi",
         "source_id": "SRC03", "fact": "Biên độ an toàn bảo vệ con người trước biến cố bất ngờ."},
    ]
    for cl in content["claims"]:
        scene = next(s for s in scenes_out if s["id"] == cl["scene_id"])
        if cl["quote"] not in scene["narration"]:
            raise ValueError(f"Claim quote missing: {cl['quote']}")
    content["revision_response"] = [
        "Revision 3: new approved v3 script (12 scenes) with Bill Gates hidden-advantage hook and Vietnamese coffee-shop slice of life; reused approved doodle frames where meaning matches."
    ]
    OUT_CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_CONTENT_DIR / "content.json").write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REUSE_MAP_PATH.write_text(json.dumps({"reuse": reuse_map, "new": sorted(new_specs)}, indent=2) + "\n", encoding="utf-8")
    print(f"content: {len(scenes_out)} scenes, {sum(len(s['images']) for s in scenes_out)} images, "
          f"reused={len(reuse_map)}, new={len(new_specs)}")


def main() -> None:
    brief, brief_path = build_brief()
    build_content(brief, brief_path)
    (RUN / "brief-current.json").write_text(
        json.dumps({"revision": 3, "hash": sha(brief_path)}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
