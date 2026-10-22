#!/usr/bin/env python3
"""Build production-ready packages for The Collector's Fallacy (16:9 and 9:16 long-form).

Pillar: "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức" (tier_1_broad)
- collectors-fallacy-16x9: 18 scenes full_frame_v1 landscape explainer
- collectors-fallacy-9x16: 12 scenes full_frame_v1 vertical mobile long-form
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tools.research_story_architect import (
    DEFAULT_CHANNEL_PILLAR,
    PackagingSpec,
    ResearchedTopic,
    build_scenes_from_story_rows,
    write_production_package,
)
from visual_style import CAST_APPEARANCE, DEFAULT_OUTFIT
from visual_style import LEGACY_HANDDRAWN_STYLE_DESCRIPTION as STYLE_DESCRIPTION

# ---------------------------------------------------------------------------
# STORY 16:9 (18 Scenes — Widescreen Explainer, 6 Beats / Scene, Max <= 2.8s)
# ---------------------------------------------------------------------------
STORY_16X9: list[tuple[str, str, list[tuple[str, str]]]] = [
    (
        "Cú tát mở màn",
        "A Vietnamese student desk at night, blue laptop screen, warm desk lamp, ticking clock.",
        [
            ("Tải hàng trăm cuốn sách chỉ tạo ra ảo giác học tập.", "macro_prop|A hand clicks a bright blue Download button on a glowing screen."),
            ("Bạn bấm nút lưu tệp.", "full_scene|A student sits at a wooden desk at night as a large PDF file drops into a desktop folder."),
            ("Thanh tiến trình chạy nhanh.", "macro_prop|Close view of the download progress bar racing forward."),
            ("Một trăm phần trăm hoàn tất.", "variation|The student watches the green download bar hit completion; eyebrows relax with premature satisfaction."),
            ("Não bạn thở phào nhẹ nhõm.", "variation|The student leans back in the desk chair, smiling complacently."),
            ("Ngỡ rằng mình vừa nạp thêm tri thức.", "white_card|A shiny full hard drive icon stamped with false victory laurels on pure white."),
        ],
    ),
    (
        "Nghĩa địa thư mục",
        "A digital workspace view showing cluttered folder hierarchies and neglected files.",
        [
            ("Cảm giác an tâm đó dâng lên rất nhanh.", "full_scene|The student desk surrounded by open folder windows titled TÀI LIỆU QUAN TRỌNG and SÁCH HAY."),
            ("Nhưng cuốn sách đó,", "macro_prop|Close view of a folder containing hundreds of PDF files with creation dates from three years ago."),
            ("bạn có mở ra đọc không?", "variation|The mouse cursor hovers over the file title without double-clicking."),
            ("Rất có thể là không bao giờ.", "variation|The student hesitates, ignores the file, and closes the laptop lid."),
            ("Những tệp tài liệu nằm im lìm trong ổ cứng.", "variation|The closed laptop rests in the dark room, silently accumulating digital dust."),
            ("Biến máy tính của bạn thành một nghĩa địa kỹ thuật số.", "white_card|A minimalist tombstone icon inscribed with UNREAD PDF on pure white."),
        ],
    ),
    (
        "Vòng lặp thu gom",
        "A bustling digital communication background with online study groups and file shares.",
        [
            ("Chúng ta gia nhập hàng chục hội nhóm học thuật.", "full_scene|The student scrolling rapidly through social groups sharing massive Google Drive links."),
            ("Thấy ai chia sẻ tài liệu là bấm lưu ngay.", "macro_prop|A hand rapidly bookmarking links and saving cloud drives without reading a single page."),
            ("Dung lượng ổ cứng đỏ rực.", "macro_prop|A storage bar turns bright warning red at five hundred gigabytes used."),
            ("Nhưng khi bước vào phòng thi,", "full_scene|The student stands alone before a blank classroom exam desk under cold fluorescent lights."),
            ("cầm chiếc bút trên tay,", "macro_prop|Close view of a trembling cartoon hand holding a black pen over a blank exam paper."),
            ("đầu bạn vẫn hoàn toàn trống rỗng.", "variation|The student clutches the pen with a stunned, empty expression; eyebrows tense."),
        ],
    ),
    (
        "Định danh căn bệnh",
        "A conceptual psychology study space with diagnostic charts and research books.",
        [
            ("Hiện tượng này không hề mới.", "full_scene|A cognitive researcher in a minimalist office reviewing historical learning behavior charts."),
            ("Nó có một tên gọi khoa học chính thức.", "variation|The researcher points a pen toward an academic diagnosis board."),
            ("Ảo tưởng của người thu gom.", "white_card|Bold minimalist title card: THE COLLECTORS FALLACY with a balanced cognitive scale on pure white."),
            ("Đây là cái bẫy nhận thức kinh điển.", "variation|Two diverging paths: one leading to deep synthesis, the other trapped in an endless downloading circle."),
            ("Khiến bạn lầm tưởng việc sở hữu file", "macro_prop|A hand holding an external hard drive beside an empty conceptual outline sheet."),
            ("đồng nghĩa với việc đã hiểu bài. [pause:600ms]", "variation|The researcher underlines the stark divide between physical possession and mental mastery."),
        ],
    ),
    (
        "Cơn sốt Dopamine giả",
        "A neural pathway illustration room showing neurochemical reactions.",
        [
            ("Tại sao hành động bấm tải về lại gây nghiện đến vậy?", "full_scene|A student at a glowing desk with translucent neural networks visualizing brain activity."),
            ("Bởi vì nút bấm đó kích hoạt một phần thưởng tức thì.", "macro_prop|Close view of an index finger pressing the mouse button; a bright spark radiates from the switch."),
            ("Khoảnh khắc tệp được lưu vào máy,", "variation|The bright spark travels along neural pathways into the brains reward center."),
            ("não bạn tự phóng ra một liều dopamine giả.", "white_card|A chemical dopamine molecule glowing vibrantly above a computer mouse on pure white."),
            ("Bạn cảm thấy hưng phấn.", "variation|The student smiles with vibrant energy as if a major task was just conquered."),
            ("Và tự mãn như một người chiến thắng trước khi bắt đầu.", "variation|The student sits back in triumph, celebrating an accomplishment that never happened."),
        ],
    ),
    (
        "Bản năng săn mồi thời đồ đá",
        "A dual conceptual environment contrasting ancient wilderness and modern study room.",
        [
            ("Bộ não của chúng ta tiến hóa từ thời săn bắt hái lượm.", "full_scene|Split background: left side shows an ancient gatherer; right side shows a modern student."),
            ("Tích trữ tài nguyên từng là điều kiện sống còn.", "variation|The ancient gatherer hoards wild fruits into a woven basket with a satisfied smile."),
            ("Ngày nay, ta không còn tìm kiếm trong rừng.", "variation|The modern student sits comfortably in an ergonomic desk chair."),
            ("Nhưng hành vi tích trữ vẫn giữ nguyên vẹn.", "variation|The student drags dozens of ebook icons into a local drive."),
            ("Chiếc ổ cứng trở thành hang chứa thức ăn thời hiện đại.", "white_card|A cartoon cave filled with glowing data disks and unopened books on pure white."),
            ("Bạn ngỡ rằng mình đã chuẩn bị chu đáo.", "macro_prop|Close view of hands gripping a loaded hard drive as if it were a precious treasure trove."),
            ("Nhưng đầu óc vẫn chưa hề tiếp thu.", "variation|A soft translucent bubble wraps around the student, shielding them from the hard reality of learning."),
        ],
    ),
    (
        "Sự lười biếng tinh vi",
        "An analytical balance room measuring mental effort and cognitive energy.",
        [
            ("Tải một tài liệu chỉ mất đúng ba giây.", "full_scene|A digital timer counting down rapidly: three, two, one second."),
            ("Nhưng để đọc và thẩm thấu nó,", "macro_prop|A thick research monograph with dense analytical text requiring intensive focus."),
            ("bạn cần nhiều tuần vật lộn nghiêm túc.", "full_scene|The student struggling patiently with notes, highlighter and scratch paper at the desk."),
            ("Bộ não sinh học luôn có xu hướng tiết kiệm calo.", "white_card|An energy meter comparing negligible click exertion against massive deep reading expenditure on pure white."),
            ("Nó chọn con đường dễ nhất,", "variation|The brain silhouette chooses the effortless shortcut button over the steep mountain path."),
            ("để đánh lừa cảm xúc của chính bạn.", "variation|The student looks into a decorative hand mirror that reflects an illusion of expertise."),
        ],
    ),
    (
        "Thực nghiệm lưu trữ",
        "A controlled experimental laboratory with two matched study groups.",
        [
            ("Các nhà khoa học nhận thức đã tiến hành một thử nghiệm đối đầu.", "full_scene|A laboratory observation room with two student subjects seated at separate testing desks."),
            ("Nhóm thứ nhất được cấp cả kho tài liệu trực tuyến.", "variation|The student on the left sits before three glowing monitors displaying endless online repositories."),
            ("Hàng ngàn bài viết sẵn sàng trong tầm tay.", "macro_prop|Close view of infinite browser tabs loading dense scientific papers."),
            ("Nhóm thứ hai chỉ được cầm duy nhất một bài báo in trên giấy.", "variation|The student on the right receives a single four-page printed paper with no internet access."),
            ("Cả hai nhóm có một tuần chuẩn bị.", "macro_prop|A laboratory calendar turning past seven days alongside an objective evaluation timer."),
            ("Đồng hồ đếm ngược từng ngày.", "macro_prop|Close view of an experimental timer ticking steadily."),
            ("Và không ai được mang tài liệu vào phòng thi.", "white_card|A warning sign showing books and laptops crossed out before an examination door on pure white."),
            ("Phép thử sẽ làm hai lối học tách rời. [pause:600ms]", "variation|Two colored runners approach separate timing gates under laboratory inspection."),
        ],
    ),
    (
        "Cú lật bất ngờ",
        "An academic evaluation room showing comparative test performance.",
        [
            ("Kết quả sau một tuần khiến tất cả kinh ngạc.", "full_scene|The researcher displays the final comparative test scoring board in the laboratory."),
            ("Nhóm sở hữu thư viện khổng lồ đạt điểm kém hơn hẳn.", "variation|The bar chart for the digital hoarding group lags far behind at the low bottom tier."),
            ("Họ tốn quá nhiều thời gian để tìm kiếm và phân loại tệp.", "variation|The hoarder looks exhausted, surrounded by hundreds of downloaded bookmarks with zero recall."),
            ("Họ không còn năng lượng để đọc sâu.", "macro_prop|A tired hand closing an unread PDF on a glowing screen."),
            ("Tâm trí kiệt quệ trước kỳ thi.", "variation|The hoarder rests their head on the desk in cognitive fatigue."),
            ("Trong khi nhóm đọc một bài duy nhất lại thấu hiểu bản chất.", "variation|The single-paper reader smiles calmly, drawing clear structural concept maps on the board."),
            ("Sự dư thừa thông tin đã bóp nghẹt tư duy chiều sâu.", "white_card|An overflowing information funnel choking and blocking knowledge output on pure white."),
            ("Càng ôm đồm nhiều, đầu óc càng phân tán.", "variation|Scattered floating document icons shatter the clarity of the hoarders central focus."),
        ],
    ),
    (
        "Hội chứng Tsundoku",
        "A peaceful Japanese-inspired library space transitioning into digital clutter.",
        [
            ("Người Nhật có một từ rất hay để mô tả căn bệnh này.", "full_scene|A quiet wooden bookshelf aesthetic where books are stacked neatly from floor to ceiling."),
            ("Đó là Tsundoku.", "macro_prop|Close-up of elegant typography displaying the word TSUNDOKU beside an unread book spine."),
            ("Hiện tượng mua sách về nhưng chỉ để ngắm, không hề đọc.", "variation|A reader places a fresh book on a towering unread pile, admiring the neat stack without opening page one."),
            ("Trong thế giới số, căn bệnh này nhân lên gấp ngàn lần.", "variation|The physical book stack morphs seamlessly into hundreds of gigabytes of unread cloud folders."),
            ("Việc lưu trữ tệp hoàn toàn miễn phí và không tốn chỗ.", "white_card|An infinite cloud storage icon absorbing thousands of unread files effortlessly on pure white."),
            ("Càng dễ tích trữ, ta càng dễ sa lầy.", "variation|The student stands ankle-deep in an endless digital sea of unopened PDF icons."),
        ],
    ),
    (
        "File chết trong ổ cứng",
        "A moody student room lit only by the cold pulsing light of an external drive.",
        [
            ("Nhưng hãy nhớ một chân lý đơn giản này.", "full_scene|The student sits at the desk, looking directly at an external hard drive glowing in the dark."),
            ("Kiến thức không thể tự truyền qua cổng USB vào đầu bạn.", "white_card|A cartoon stick figure plugging a USB cable directly into its ear with an error buzzer on pure white."),
            ("Mắt bạn phải đọc kỹ từng trang sách.", "macro_prop|Close view of eyes scanning line by line across a focused paragraph of text."),
            ("Não bạn phải tự dựng lại sơ đồ logic.", "full_scene|The student actively sketching relational arrows between core ideas in a physical notebook."),
            ("Nếu bạn không chịu làm điều đó,", "macro_prop|Close view of cold metallic hard drive casing reflecting the dim desk lamp."),
            ("gigabyte tài liệu kia mãi chỉ là những hạt electron vô tri.", "variation|The student gazes at the drive lights, realizing the stark divide between storage and wisdom."),
        ],
    ),
    (
        "Bài học từ Niklas Luhmann",
        "A classic mid-century German scholar study with wooden slip-box cabinets.",
        [
            ("Nhà xã hội học Niklas Luhmann từng xuất bản hơn bảy mươi cuốn sách.", "full_scene|A scholar standing beside a compact wooden slip-box cabinet with neat small drawers."),
            ("Ông không bao giờ tích trữ tài liệu bừa bãi.", "variation|Luhmann slides open one drawer, revealing thousands of small handwritten index cards."),
            ("Phương pháp của ông được cả thế giới ngưỡng mộ.", "variation|Luhmann stands thoughtfully holding an index card."),
            ("Hệ thống hộp ghi chú Zettelkasten.", "white_card|A minimalist diagram of interconnected index cards forming a decentralized neural net on pure white."),
            ("Mỗi khi đọc một bài viết,", "macro_prop|A fountain pen resting on an open book beside clean blank note cards."),
            ("ông ghi lại bài học bằng ngôn từ của chính mình.", "macro_prop|A fountain pen writing a concise one-sentence core insight on an index card."),
            ("Ông chỉ giữ lại những ý tưởng đã được tiêu hóa.", "variation|Luhmann files the handwritten card into its exact logical coordinate in the cabinet."),
            ("Chuyển hóa thông tin thô thành tư duy sống động.", "variation|The card network lights up with golden links connecting disparate intellectual domains."),
        ],
    ),
    (
        "Chiếc phễu xử lý tri thức",
        "A conceptual diagrammatic laboratory showing the four-tier knowledge engine.",
        [
            ("Một tri thức thực sự bắt buộc phải đi qua chiếc phễu bốn tầng.", "full_scene|A glowing vertical four-tier processing funnel apparatus standing in the analytical room."),
            ("Thu nạp, Tiêu hóa, Tổng hợp, và Tái tạo.", "white_card|Four labeled tiers on pure white: 1. Thu nap -> 2. Tieu hoa -> 3. Tong hop -> 4. Tai tao."),
            ("Hành động bấm nút tải về", "variation|A tiny glowing dot enters the very top rim of the funnel apparatus."),
            ("mới chỉ dừng ở cửa ngõ ban đầu.", "macro_prop|Close view showing ninety-five percent of the processing pipeline completely empty below the rim."),
            ("Nó chưa hề chạm tới bất kỳ khâu tiêu hóa nào.", "variation|The student observes the empty processing chamber, realizing the full scope of the gap."),
            ("Muốn biến thành của mình, bạn phải xử lý nó. [pause:600ms]", "white_card|A cogwheel mechanism grinding raw data into pure crystalline insight on pure white."),
        ],
    ),
    (
        "Quy tắc: Đọc một, trả một",
        "A focused student workspace applying clean minimalist digital hygiene.",
        [
            ("Vậy làm sao để phá vỡ ảo tưởng tai hại này?", "full_scene|The student sits determinedly at the desk, opening the computer desktop for a cleanup."),
            ("Hãy áp dụng ngay quy tắc: Đọc một, trả một.", "white_card|Bold action rule card: DOC 1 TRA 1 with two balanced arrows on pure white."),
            ("Trước khi tải thêm một tài liệu mới.", "macro_prop|A hand hovering over a download link, pausing consciously."),
            ("Hãy xóa đi một tệp cũ trong máy.", "full_scene|The student drags an unread downloaded folder decisively into the trash bin icon."),
            ("Hoặc viết ra ba gạch đầu dòng tóm tắt bài vừa đọc.", "macro_prop|A pen neatly writes three bullet points summarizing a recent article in a notebook."),
            ("Chặn đứng dòng chảy tích trữ vô tội vạ.", "variation|A clean digital dam gate shuts firmly, keeping the workspace clutter-free."),
        ],
    ),
    (
        "Bài kiểm tra tờ giấy trắng",
        "A minimalist testing desk with a single blank sheet of paper and a black pen.",
        [
            ("Muốn biết bạn đã thực sự hiểu hay chưa?", "full_scene|The student closes the laptop completely and pushes it aside on the desk."),
            ("Hãy làm bài kiểm tra bằng một tờ giấy trắng.", "macro_prop|A fresh, pristine blank white sheet of paper rests under the warm desk lamp."),
            ("Đóng mọi tài liệu lại.", "variation|All books, browser tabs and notes are cleanly pushed out of sight."),
            ("Tự tay vẽ lại sơ đồ bằng từ ngữ của chính bạn.", "full_scene|The student draws a simple concept diagram and writes clear sentences without looking at references."),
            ("Nếu bạn không thể viết ra một cách trơn tru,", "variation|The pen hesitates above an unclear point, instantly exposing a genuine knowledge gap."),
            ("bạn chưa hề hiểu nó.", "white_card|A crisp question on white: TU GIAI THICH DUOC CHUA? with a definitive green checkmark."),
        ],
    ),
    (
        "Chiến lược ăn kiêng thông tin",
        "A serene minimalist study room with abundant natural light.",
        [
            ("Hãy đặt não bạn vào chế độ ăn kiêng thông tin.", "full_scene|A tranquil library room with only two selected study articles neatly placed on the table."),
            ("Mỗi tuần, chỉ chọn tối đa hai tài liệu trọng tâm.", "white_card|A calendar highlighting exactly two focused study dates with minimal book icons on pure white."),
            ("Đọc thật chậm, ghi chép thật kỹ.", "full_scene|The student annotates a paper with deep, unhurried contemplation under soft lighting."),
            ("Và thảo luận cùng bạn bè.", "variation|Two students engaged in a thoughtful academic discussion over open handwritten notebooks."),
            ("Một bài báo được tiêu hóa trọn vẹn,", "macro_prop|A well-worn paper with margin notes, underlines and critical reflections."),
            ("quý hơn một ổ cứng đầy ắp tệp chết.", "variation|The student holds up the single annotated paper with confidence and intellectual clarity."),
        ],
    ),
    (
        "Từ thủ thư sang người học",
        "An empowering transformation space from dark archival maze to expansive horizon.",
        [
            ("Đã đến lúc bạn ngừng làm người thủ thư cho chiếc ổ cứng.", "full_scene|The student steps out of a dark, dusty storage vault filled with locked filing cabinets."),
            ("Hãy trở thành một nhà nghiên cứu đúng nghĩa.", "variation|The student emerges into a bright, modern architectural study space overlooking the city."),
            ("Sức mạnh của bạn không nằm ở số lượng file bạn tích trữ.", "macro_prop|A closed external hard drive resting quietly as a mere auxiliary tool on the side."),
            ("Nó nằm ở khả năng kết nối các ý tưởng.", "full_scene|Interconnected glowing conceptual networks light up clearly behind the thinking student."),
            ("Và vận dụng tri thức vào thực tiễn cuộc sống.", "variation|The student confidently maps solutions onto a large whiteboard."),
            ("Đó mới là tài sản học thuật đích thực.", "white_card|A glowing lightbulb symbol forged inside a solid diamond foundation on pure white."),
        ],
    ),
    (
        "Khép lại vòng lặp",
        "A Vietnamese student desk at night under a warm desk lamp, serene and focused.",
        [
            ("Tối nay, khi chuẩn bị bấm tải thêm một cuốn sách,", "full_scene|The student at the familiar desk under the warm yellow lamp, looking at a download prompt."),
            ("hãy dừng ngón tay lại một giây.", "macro_prop|The students finger lifts off the mouse button with deliberate calm."),
            ("Tự hỏi bản thân: Mình tải vì muốn học,", "variation|The student looks up thoughtfully into the warm light of the desk lamp."),
            ("hay chỉ muốn mua một liều dopamine tạm thời?", "variation|A fleeting illusory dopamine sparkle fades away, leaving calm mental clarity."),
            ("Tắt máy tính đi.", "full_scene|The student shuts down the computer monitor, letting the room settle into peaceful focus."),
            ("Mở một cuốn sách cũ ra, và bắt đầu đọc trang đầu tiên.", "full_scene|The student opens an existing book on the desk, smiles calmly, and turns to page one under the warm lamp."),
        ],
    ),
]

# ---------------------------------------------------------------------------
# STORY 9:16 (12 Scenes — Vertical Mobile Long-form Safe Zone, 5 Beats / Scene)
# ---------------------------------------------------------------------------
STORY_9X16: list[tuple[str, str, list[tuple[str, str]]]] = [
    (
        "Cú tát mở màn dọc",
        "A vertical mobile frame of a Vietnamese student desk at night under a lamp.",
        [
            ("Tải hàng trăm cuốn sách chỉ tạo ra ảo giác học tập.", "macro_prop|A vertical close-up of a thumb repeatedly tapping the Save Bookmark button on a mobile feed."),
            ("Bạn lướt thấy tài liệu hay.", "full_scene|A vertical view of a student scrolling through academic posts on a phone in a dimly lit room."),
            ("Bấm lưu vào máy ngay lập tức.", "variation|The screen flashes with a quick notification: Saved to Collection."),
            ("Não bạn thở phào nhẹ nhõm.", "variation|The student smiles with instant relief, locking the phone screen."),
            ("Tưởng rằng mình đã nắm trọn kiến thức.", "white_card|A phone outline showing a giant SAVED checkmark over an empty brain on pure white."),
        ],
    ),
    (
        "Nghĩa địa thư mục xem sau",
        "A vertical mobile screen interface showing neglected bookmarks.",
        [
            ("Nhưng bạn có bao giờ mở lại mục xem sau không?", "macro_prop|A vertical screen view scrolling through a backlog of hundreds of saved posts dated two years ago."),
            ("Hàng trăm bài viết quan trọng nằm im lìm.", "full_scene|The student stares at the overwhelming list of saved links, feeling sudden mental weight."),
            ("Bạn lưu để yên tâm,", "variation|The student taps through endless saved titles with a lingering sense of guilt."),
            ("chứ không lưu để học.", "white_card|A lock icon securing thousands of unread articles on pure white."),
            ("Mục xem sau đã biến thành nghĩa địa tri thức.", "variation|The student sighs and closes the collection list without clicking a single post."),
        ],
    ),
    (
        "Định danh Collector Fallacy",
        "A vertical analytical study space with clean conceptual graphics.",
        [
            ("Tâm lý học gọi đây là Ảo tưởng Người thu gom.", "white_card|Vertical card on white: THE COLLECTORS FALLACY with a minimalist cognitive scale."),
            ("Collectors Fallacy.", "full_scene|The student stands in front of a vertical infographic separating Sở hữu from Hiểu biết."),
            ("Nó là một cái bẫy tinh vi.", "macro_prop|A hand holding a mobile phone next to a blank notebook."),
            ("Khiến ta ngộ nhận rằng,", "variation|The phone screen illuminates the students face with bright icons."),
            ("sở hữu dữ liệu là đã có tri thức. [pause:450ms]", "white_card|A stark cross mark dividing a data file icon from true comprehension on pure white."),
        ],
    ),
    (
        "Dopamine giả từ nút lưu",
        "A vertical graphic representation of neural mechanisms.",
        [
            ("Tại sao nút lưu lại gây nghiện đến vậy?", "full_scene|A student holding a phone while an artistic neural network glows in the background."),
            ("Khoảnh khắc bạn bấm tải về,", "macro_prop|Close view of the thumb pressing Download on the touchscreen."),
            ("não bạn đã tự thưởng một liều dopamine giả.", "white_card|A dopamine molecule pulsing with a brief green spark on pure white."),
            ("Cảm giác thỏa mãn ập đến rất nhanh.", "variation|The student leans back on the chair, savoring a premature victory."),
            ("Trước khi bạn kịp đọc dòng đầu tiên.", "variation|The phone screen dims while the unread article sits untouched."),
        ],
    ),
    (
        "Ba giây so với ba tuần",
        "A vertical comparison chart measuring effort versus time.",
        [
            ("Lưu một bài viết mất đúng ba giây.", "macro_prop|A digital timer counting down: 00:03 seconds on a smartphone."),
            ("Nhưng để thấu hiểu nó,", "full_scene|The student seated at a clean table studying a printed document with deep focus."),
            ("bạn cần nhiều ngày nghiền ngẫm.", "variation|The student takes margin notes with deliberate analytical care."),
            ("Não bộ chọn con đường dễ nhất để tự lừa dối.", "white_card|A path splitting into a zero-effort shortcut and a steep climb on pure white."),
            ("Bạn bận rộn tích trữ để trốn tránh việc học thật. [pause:450ms]", "variation|The student pauses, recognizing the unconscious avoidance habit."),
        ],
    ),
    (
        "Thực nghiệm Thư viện và một bài",
        "A vertical laboratory observation setting.",
        [
            ("Khoa học nhận thức đã chứng minh nghịch lý này.", "full_scene|A clean lab split vertically into two test subject profiles."),
            ("Người có cả nghìn tài liệu", "variation|The hoarder student drowned in endless digital folder icons."),
            ("lại làm bài kém hơn người chỉ giữ một bài duy nhất.", "white_card|A vertical bar chart: 1000 Unread Files vs 1 Deep Article on pure white."),
            ("Họ kiệt sức vì sắp xếp tệp.", "variation|The hoarder student rubs exhausted eyes before an empty exam desk."),
            ("Còn người kia tập trung hấp thụ trọn vẹn bản chất.", "variation|The focused student calmly explains the core principle on a vertical blackboard."),
        ],
    ),
    (
        "Căn bệnh Tsundoku thời số hóa",
        "A vertical aesthetic room blending books and cloud data.",
        [
            ("Người Nhật gọi thói quen tích sách không đọc là Tsundoku.", "macro_prop|A neat vertical stack of physical books beside a glowing cloud storage icon."),
            ("Thời đại số biến chúng ta thành những kẻ tích trữ rác dữ liệu.", "full_scene|The student surrounded by floating PDF thumbnails and unread cloud notifications."),
            ("Tệp trong máy không thể tự ngấm vào đầu bạn.", "white_card|A smartphone with Bluetooth waves failing to connect to a human head on pure white."),
            ("Chừng nào chưa đọc,", "macro_prop|A thumb hovering indecisively over hundreds of unread bookmarks."),
            ("nó chỉ là con số không tròn trĩnh.", "variation|The student lowers the phone, acknowledging the illusion."),
        ],
    ),
    (
        "Bốn tầng phễu tri thức",
        "A vertical conceptual diagram of knowledge synthesis.",
        [
            ("Tri thức thật sự cần đi qua bốn tầng phễu.", "white_card|A 4-tier vertical funnel on pure white: Thu nap -> Tieu hoa -> Tong hop -> Tai tao."),
            ("Thu nạp, Tiêu hóa, Tổng hợp, và Tái tạo.", "full_scene|The student stands beside the vertical funnel diagram examining each processing stage."),
            ("Bấm lưu chỉ là bước khởi đầu.", "macro_prop|A tiny dot entering the top layer while the lower three layers remain empty."),
            ("Nếu không tiêu hóa,", "variation|The student points to the blank processing chamber below."),
            ("mọi tài liệu đều trở nên vô nghĩa. [pause:450ms]", "white_card|A warning badge on pure white: DỮ LIỆU CHẾT NẾU KHÔNG TIÊU HÓA."),
        ],
    ),
    (
        "Quy tắc Đọc một trả một",
        "A vertical view of desk action and digital hygiene.",
        [
            ("Muốn cai nghiện lưu trữ? Hãy áp dụng quy tắc: Đọc một, trả một.", "white_card|Bold vertical card: QUY TAC DOC 1 TRA 1 on pure white."),
            ("Trước khi tải thêm tệp mới, hãy xóa bớt một tệp cũ.", "full_scene|The student swipes to delete an old unread bookmark from the phone library."),
            ("Hoặc tự viết ra ba câu tóm tắt điều bạn vừa học được.", "macro_prop|A pen jotting three concise bullet points on a vertical paper notepad."),
            ("Bắt não phải làm việc", "variation|The student pauses to actively recall the core concept."),
            ("trước khi tích lũy thêm.", "variation|The student looks satisfied after recording the actual learning notes."),
        ],
    ),
    (
        "Quy tắc Tờ giấy trắng",
        "A vertical close view of an analog desk test.",
        [
            ("Bài kiểm tra sự thật là một tờ giấy trắng.", "macro_prop|A single blank white index card placed squarely on the desk."),
            ("Cất điện thoại đi.", "full_scene|The student turns the phone face down and pushes it away."),
            ("Tự giải thích khái niệm vừa học bằng ngôn từ của chính bạn.", "variation|The student draws a simple concept flowchart on the paper card."),
            ("Nếu mắc kẹt ở đâu,", "macro_prop|Close-up of the pen hovering above an uncompleted diagram branch."),
            ("bạn biết mình phải đọc lại từ đó.", "white_card|A question on pure white: CON NHO GI KHI KHONG NHIN MAY?"),
        ],
    ),
    (
        "Người học không phải người gác kho",
        "A vertical empowering scene of mental agility.",
        [
            ("Đừng làm người gác kho cho hàng nghìn tệp dữ liệu.", "full_scene|The student sets down a heavy box of storage drives with a sense of relief."),
            ("Hãy là người tiêu hóa và kiến tạo tri thức.", "variation|The student stands upright, surrounded by sharp, glowing insight diagrams."),
            ("Giá trị của bạn nằm ở tư duy đọng lại trong đầu.", "macro_prop|Close view of clean handwritten notes connecting two major concepts."),
            ("Nó là sự sắc bén khi đối thoại.", "variation|The student points with confidence to a structured concept on the board."),
            ("Chứ không nằm ở dung lượng ổ cứng bạn đang có.", "white_card|A solid brain icon outshining a heavy hard drive icon on pure white."),
        ],
    ),
    (
        "Khép lại: Đọc trang đầu tiên",
        "A peaceful vertical shot of a student study corner at night.",
        [
            ("Lần tới khi chuẩn bị bấm nút lưu,", "macro_prop|A thumb pauses above the Bookmark icon on the phone screen."),
            ("hãy dừng lại một nhịp.", "variation|The student pauses thoughtfully before the glowing screen."),
            ("Tự hỏi bản thân: Mình đang học thật, hay chỉ đang lừa dối chính mình?", "variation|The student looks away from the phone into the quiet room."),
            ("Đóng điện thoại lại.", "full_scene|The student puts the phone into a drawer and turns to the desk."),
            ("Và mở trang sách đầu tiên ra đọc ngay bây giờ.", "full_scene|The student sits down peacefully, reading the first sentence of an open book under the warm light."),
        ],
    ),
]


def build_sources() -> list[dict]:
    return [
        {
            "id": "SRC01",
            "title": "The Critical Importance of Retrieval for Learning",
            "reference": "Dr. Jeffrey D. Karpicke & Dr. Henry L. Roediger (2008). Science, 319(5865), 966-968.",
            "facts": [
                "Tải tài liệu chỉ tạo ra ảo giác hiểu bài.",
                "Não bộ chỉ ghi nhớ sâu khi tự mình truy xuất.",
            ],
        },
        {
            "id": "SRC02",
            "title": "The Collector's Fallacy and the Illusion of Competence",
            "reference": "Tiago Forte & Sönke Ahrens (2017). How to Take Smart Notes.",
            "facts": [
                "Lưu trữ tài liệu không đồng nghĩa với tiếp thu.",
                "Thông tin chưa qua xử lý chỉ là dữ liệu chết.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Dopamine and Anticipatory Reward Mechanisms in Information Seeking",
            "reference": "Dr. Robert M. Sapolsky (2017). Behave: The Biology of Humans at Our Best and Worst.",
            "facts": [
                "Nút tải về kích hoạt dopamine săn mồi tức thì.",
                "Bộ não luôn chọn con đường ít tốn năng lượng.",
            ],
        },
    ]


def build_topic_16x9() -> ResearchedTopic:
    scenes = build_scenes_from_story_rows(STORY_16X9, character_id="CH01")
    for idx, sc in enumerate(scenes, 1):
        sc.requirements = [f"R{idx:02d}"]
        if idx in (4, 10, 11):
            sc.source_ids = ["SRC02"]
        elif idx in (5, 6, 7):
            sc.source_ids = ["SRC03"]
        elif idx in (8, 9, 15):
            sc.source_ids = ["SRC01"]

    scenes[3].claim_facts = [
        ("Khiến bạn lầm tưởng việc sở hữu file", "SRC02", "Lưu trữ tài liệu không đồng nghĩa với tiếp thu.")
    ]
    scenes[4].claim_facts = [
        ("Bởi vì nút bấm đó kích hoạt một phần thưởng tức thì.", "SRC03", "Nút tải về kích hoạt dopamine săn mồi tức thì.")
    ]
    scenes[7].claim_facts = [
        ("Các nhà khoa học nhận thức đã tiến hành một thử nghiệm đối đầu.", "SRC01", "Tải tài liệu chỉ tạo ra ảo giác hiểu bài.")
    ]

    return ResearchedTopic(
        topic="Ảo Tưởng Sở Hữu Tri Thức (The Collector's Fallacy): Giải mã cơ chế tải hàng gigabyte tài liệu tạo dopamine giả khiến não lầm tưởng sở hữu file đồng nghĩa với tiếp thu",
        audience="Sinh viên, học viên cao học và người tự học tại Việt Nam mắc kẹt trong thói quen tích trữ tài liệu",
        goal="Phá vỡ ảo tưởng người thu gom, chuyển hóa từ người gác kho kỹ thuật số sang bộ máy tiêu hóa tri thức qua quy tắc Đọc 1 trả 1 và bài test tờ giấy trắng",
        video_type="research_explainer",
        min_duration=360.0,
        max_duration=480.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        sources=build_sources(),
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _) in enumerate(STORY_16X9, 1)],
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
            youtube_title="Tải hàng trăm cuốn sách chỉ là ảo giác học",
            visual_hook="Bàn học đêm với màn hình tràn ngập file PDF và ổ cứng đỏ rực dung lượng đối lập với trang giấy trắng",
            text_overlay="LƯU ĐẦY KHÔNG ĐỌC",
            contrast_pair="Tải về tích trữ vs. Tiêu hóa tri thức",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "the collectors fallacy",
                "ảo tưởng sở hữu tri thức",
                "tsundoku kỹ thuật số",
                "cách đọc sách hiệu quả",
                "phương pháp zettelkasten",
            ],
        ),
    )


def build_topic_9x16() -> ResearchedTopic:
    scenes = build_scenes_from_story_rows(STORY_9X16, character_id="CH01")
    for idx, sc in enumerate(scenes, 1):
        sc.requirements = [f"R{idx:02d}"]
        if idx in (3, 7):
            sc.source_ids = ["SRC02"]
        elif idx in (4, 5):
            sc.source_ids = ["SRC03"]
        elif idx in (6, 10):
            sc.source_ids = ["SRC01"]

    scenes[2].claim_facts = [
        ("sở hữu dữ liệu là đã có tri thức.", "SRC02", "Lưu trữ tài liệu không đồng nghĩa với tiếp thu.")
    ]
    scenes[3].claim_facts = [
        ("não bạn đã tự thưởng một liều dopamine giả.", "SRC03", "Nút tải về kích hoạt dopamine săn mồi tức thì.")
    ]
    scenes[5].claim_facts = [
        ("Khoa học nhận thức đã chứng minh nghịch lý này.", "SRC01", "Tải tài liệu chỉ tạo ra ảo giác hiểu bài.")
    ]

    return ResearchedTopic(
        topic="Ảo Tưởng Sở Hữu Tri Thức (The Collector's Fallacy — Bản Dọc Safe Zone)",
        audience="Sinh viên, người tự học và nghiên cứu sinh lướt video di động",
        goal="Tóm lược sắc bén cơ chế dopamine giả khi lưu bài trên điện thoại và áp dụng 2 quy tắc thực chiến giải thoát khỏi đống rác dữ liệu",
        video_type="research_explainer",
        min_duration=240.0,
        max_duration=330.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=build_sources(),
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _) in enumerate(STORY_9X16, 1)],
        characters=[
            {
                "id": "CH01",
                "name": "Người học di động",
                "appearance": CAST_APPEARANCE,
                "outfit": "Simple teal shirt in vertical safe zone framing.",
            }
        ],
        scenes=scenes,
        tone="Conversational Essayist sắc sảo, gần gũi, thực chiến",
        language="vi",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        packaging=PackagingSpec(
            youtube_title="Lưu Đầy Ổ Cứng: Căn Bệnh Ảo Tưởng Tri Thức",
            visual_hook="Màn hình điện thoại hiển thị hàng trăm bài viết lưu vào mục Xem Sau chưa từng mở lại",
            text_overlay="LƯU ĐẦY KHÔNG ĐỌC",
            contrast_pair="Bấm nút lưu vs. Đọc trang đầu",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "the collectors fallacy",
                "ảo tưởng sở hữu tri thức",
                "bẫy lưu bài xem sau",
                "cách đọc sách thực chiến",
            ],
        ),
    )


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Build The Collector's Fallacy packages (16:9 and 9:16).")
    parser.add_argument("--job-16x9", type=Path, default=SYS_DIR / "blueprints" / "collectors-fallacy-16x9")
    parser.add_argument("--job-9x16", type=Path, default=SYS_DIR / "blueprints" / "collectors-fallacy-9x16")
    args = parser.parse_args()

    print("=== BUILDING 16:9 LANDSCAPE EXPLAINER ===")
    topic_16x9 = build_topic_16x9()
    res_16x9 = build_and_export_job(topic_16x9, args.job_16x9)
    print(json.dumps({
        "job": "collectors-fallacy-16x9",
        "output_dir": str(args.job_16x9),
        "valid_contracts": res_16x9["valid_contracts"],
        "contract_errors": res_16x9["contract_errors"],
        "packaging_warnings": res_16x9["packaging_warnings"],
        "cadence_status": res_16x9["cadence_report"]["status"],
        "cadence_warnings": res_16x9["cadence_report"]["warnings_count"],
        "total_duration": res_16x9["cadence_report"]["total_duration"],
        "total_syllables": res_16x9["cadence_report"]["total_actual_syllables"],
    }, ensure_ascii=False, indent=2))

    print("\n=== BUILDING 9:16 VERTICAL LONG-FORM ===")
    topic_9x16 = build_topic_9x16()
    res_9x16 = build_and_export_job(topic_9x16, args.job_9x16)
    print(json.dumps({
        "job": "collectors-fallacy-9x16",
        "output_dir": str(args.job_9x16),
        "valid_contracts": res_9x16["valid_contracts"],
        "contract_errors": res_9x16["contract_errors"],
        "packaging_warnings": res_9x16["packaging_warnings"],
        "cadence_status": res_9x16["cadence_report"]["status"],
        "cadence_warnings": res_9x16["cadence_report"]["warnings_count"],
        "total_duration": res_9x16["cadence_report"]["total_duration"],
        "total_syllables": res_9x16["cadence_report"]["total_actual_syllables"],
    }, ensure_ascii=False, indent=2))

    success = (
        res_16x9["valid_contracts"]
        and res_16x9["cadence_report"]["status"] == "PASS"
        and res_9x16["valid_contracts"]
        and res_9x16["cadence_report"]["status"] == "PASS"
    )
    if not success:
        sys.exit(1)
    print("\n✅ BOTH JOBS BUILT AND VALIDATED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
