"""Author a research-backed landscape acceptance package without provider calls."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tools.research_story_architect import (
    PackagingSpec,
    ResearchedBeat,
    ResearchedScene,
    ResearchedTopic,
    write_production_package,
)
from visual_style import CAST_APPEARANCE, DEFAULT_OUTFIT, STYLE_DESCRIPTION

# Each row is an authored narration unit and a visible action, not an automatic
# subdivision of a generic background prompt. Text is never painted implicitly.
STORY: list[tuple[str, str, list[tuple[str, str]]]] = [   (   'Trang sách vàng',
        'A student desk under green lamp light.',
        [   (   'Trang sách vàng kín, đầu bạn vẫn trống.',
                'still_life|An open textbook covered in dense yellow highlighting under lamp light.'),
            ('Bạn gạch thêm một dòng.', 'full_scene|A student draws one more yellow line at the desk.'),
            (   'Rồi khép giáo trình lại.',
                'variation|The same frustrated student closes the textbook, eyebrows tense and mouth uncertain; no '
                'smile.'),
            ('Ngòi bút dừng lơ lửng.', 'still_life|A black pen resting motionless beside a blank sheet of paper.'),
            ('Chỉ còn trang giấy trắng.', 'full_scene|The student holds a pen over an untouched sheet.'),
            ('Bạn định viết gì?', 'variation|The pen hesitates above the sheet; the student looks puzzled.'),
            ('Định nghĩa vừa đọc biến mất.', 'white_card|A blank paper icon beside a closed textbook icon on white.'),
            (   'Mở sách, mọi câu lại quen.',
                'full_scene|The student reopens the highlighted textbook and recognizes the page.'),
            (   'Chuyện gì vừa xảy ra giữa hai lần mở sách?',
                'variation|The student looks from the familiar textbook to the blank sheet.')]),
    (   'Câu hỏi giữa giảng đường',
        'A lecture hall in soft daylight.',
        [   (   'Trong lớp, bạn nhận ra ngay lời giải trên bảng.',
                'environment|A quiet lecture hall with chalk diagrams on a blackboard in soft light.'),
            (   'Đến lượt đứng lên, câu đầu tiên lại mắc kẹt.',
                'full_scene|A student stands uncertainly before a blank board in the lecture hall.'),
            (   'Cả lớp im lặng, chiếc bút vẫn nằm trong tay.',
                'variation|The student holds a marker motionless before the silent hall.'),
            (   'Trang sách quen thuộc không còn ở trước mắt bạn.',
                'still_life|A closed textbook resting alone on a wooden lecture hall chair.'),
            (   'Điều biến mất có thể chính là chiếc nạng gợi ý.',
                'full_scene|The student looks at the blank board without the familiar prompt.'),
            (   'Nhận ra lời giải khác với tự dựng lại nó.',
                'variation|The student steps back as two conceptual paths appear before the board.'),
            (   'Muốn phân biệt, ta cần một phép so sánh công bằng.',
                'white_card|Two contrasting learning paths comparing passive cue and independent reconstruction on '
                'white.')]),
    (   'Hai lối học',
        'An experimental classroom in morning light.',
        [   (   'Hai nhóm cùng bắt đầu bằng một đoạn văn ngắn.',
                'environment|An empty divided classroom with identical study tables under morning light.'),
            (   'Nhóm bên trái có thêm lượt đọc lại tài liệu.',
                'full_scene|The left study group rereads matching prose sheets at their table.'),
            (   'Nhóm bên phải tự nhớ lại, khi trang giấy đã khuất.',
                'variation|The right study group writes from memory with reference sheets covered.'),
            (   'Câu hỏi không phải ai thấy việc học dễ hơn.',
                'still_life|Two matching paper sheets resting side by side on a clean wooden table.'),
            (   'Ta muốn biết điều gì còn lại sau khi chờ.',
                'still_life|A desk clock ticking steadily beside an empty recall answer sheet.'),
            (   'Nếu kiểm tra ngay, kết quả có thể đánh lừa bạn.',
                'full_scene|Students observe early testing trays under overhead classroom light.'),
            (   'Khoảng cách thời gian sẽ làm hai đường tách ra.',
                'white_card|Two colored diverging trajectories along a clean timeline on pure white.')]),
    (   'Mốc kiểm tra',
        'A laboratory room under neutral lighting.',
        [   (   'Lần kiểm tra diễn ra sau năm phút, hai ngày, hoặc một tuần.',
                'environment|A quiet laboratory room with three testing stations along a wall under neutral lighting.'),
            (   'Cùng một cách học được nhìn qua những cửa sổ khác nhau.',
                'full_scene|A researcher inspects three observation stations in the laboratory.'),
            (   'Chiếc đồng hồ không chỉ làm dài thêm buổi chờ.',
                'variation|The researcher pauses beside a large timing apparatus on the bench.'),
            (   'Nó đổi câu hỏi từ vừa nhìn thấy sang còn nhớ gì.',
                'still_life|A covered prose sheet resting beside three wooden recall tokens on a tray.'),
            (   'Bài kiểm tra ngắn hạn chưa nói hết chuyện dài hạn.',
                'full_scene|A learner compares two experimental timelines at the lab bench.'),
            (   'Một người có thể thắng ở mốc này, thua ở mốc khác.',
                'variation|The learner marks two different outcome points along the testing timeline.'),
            (   'Bởi vậy, cảm giác trôi chảy cần được kiểm tra lại.',
                'white_card|A smooth track meeting a separate verification checkpoint on pure white.')]),
    (   'Lợi thế trước mắt',
        'An experiment room under overhead lighting.',
        [   (   'Sau năm phút, nhóm đọc lại nhớ tốt hơn nhóm tự kiểm tra.',
                'still_life|Two unequal stacks of recall sheets resting beside an early five-minute timer.'),
            (   'Đây là đoạn kết mà cảm giác dễ chịu muốn giữ lại.',
                'full_scene|A learner smiles and points at the taller initial stack in the room.'),
            (   'Vừa đọc xong, hình dáng câu chữ vẫn còn rất gần.',
                'variation|The learner reviews the freshly highlighted sheet with apparent ease.'),
            (   'Một bài kiểm tra ngay có thể ghi nhận lợi thế ấy.',
                'still_life|An immediate testing tray holding completed sheets under an overhead spotlight.'),
            (   'Nhưng đề thi thật thường không nằm ngay cuối trang.',
                'environment|A long quiet corridor leading toward distant examination doors in soft light.'),
            (   'Bạn phải mang kiến thức đi qua một khoảng thời gian.',
                'full_scene|The learner walks down the corridor carrying an idea token.'),
            (   'Phép so sánh vì thế chưa thể dừng ở đây.',
                'variation|The learner continues past the early gate toward later testing rooms.')]),
    (   'Đổi ngôi sau trì hoãn',
        'A laboratory wall under soft light.',
        [   (   'Ở các lần kiểm tra muộn, nhóm từng tự kiểm tra nhớ tốt hơn.',
                'still_life|Two delayed-testing recall stacks showing the retrieval stack taller beside a one-week '
                'timer.'),
            (   'Thứ hạng đổi chỗ, dù đoạn văn ban đầu vẫn giống nhau.',
                'white_card|Two comparative bar columns reversing their heights between early and delayed retention on '
                'white.'),
            (   'Đường dễ đi lúc học không đảm bảo lợi thế về sau.',
                'full_scene|A learner observes the reversed result wall with surprise under soft laboratory light.'),
            (   'Đường phải tự tìm lại có thể giúp ở lần nhớ kế tiếp.',
                'variation|The learner traces the upward delayed trajectory with renewed focus.'),
            (   'Đừng biến kết quả này thành lời cấm mọi lượt đọc lại.',
                'still_life|A study sheet and a self-test sheet resting side by side as complementary tools.'),
            (   'Thí nghiệm đang so sánh những điều kiện cụ thể của nó.',
                'full_scene|The learner inspects experimental boundary conditions displayed on the lab wall.'),
            (   'Nó đủ để hỏi lại cách ta đánh giá buổi học.',
                'variation|The learner thoughtfully re-evaluates a learning progress gauge.')]),
    (   'Tự tin và kết quả',
        'A testing booth under cool light.',
        [   (   'Đọc lại còn làm người học tự tin hơn vào khả năng nhớ.',
                'still_life|A confidence meter dial pointing high beside a stack of reread study sheets.'),
            (   'Chiếc kim tự tin và chồng câu trả lời không luôn đi cùng.',
                'white_card|A high confidence dial placed beside a low delayed recall stack on pure white.'),
            (   'Một cảm giác rất thật vẫn có thể là thước đo lệch.',
                'still_life|A tilted wooden measurement ruler resting beside an experimental score tray.'),
            (   'Bạn không bịa ra sự quen thuộc của trang sách.',
                'full_scene|A student looks at a familiar textbook page inside the testing booth.'),
            (   'Vấn đề nằm ở điều bạn suy ra từ cảm giác đó.',
                'variation|The student pauses thoughtfully while looking at an uncertain prediction gauge.'),
            (   'Từ quen mắt đến nhớ được còn có một bước chưa thử.',
                'full_scene|The student points at a gap between recognition and independent retrieval.'),
            (   'Ta cần nhìn rõ bước bị bỏ qua trong lần tự nhớ ấy.',
                'white_card|A magnifying glass highlighting a missing cognitive stepping stone on white.')]),
    (   'Tấm bản đồ',
        'A foggy map landscape at twilight.',
        [   (   'Trên bản đồ có sẵn, mọi ngã rẽ trông rất rõ.',
                'still_life|A detailed illustrated parchment map showing distinct branching trails at twilight.'),
            (   'Khi bản đồ bị che, bạn phải tự chọn đường đi.',
                'full_scene|A traveler stands at a foggy trail fork holding a covered map.'),
            (   'Biết nhìn tuyến đường không đồng nghĩa nhớ từng chỗ rẽ.',
                'variation|The traveler hesitates at the junction, looking between two mist-covered paths.'),
            (   'Một khúc cua quên mất đủ làm hành trình đứt đoạn.',
                'environment|A desolate misty crossroads where trail footprints vanish into thick fog.'),
            (   'Đây là hình dung cho khác biệt giữa hai nhiệm vụ.',
                'white_card|Two paired icons: an open map route and a blank reconstruction path on pure white.'),
            (   'Nó không phải ảnh chụp một vùng não đang hoạt động.',
                'full_scene|The traveler studies the landscape illustration with a clear reflective posture.'),
            (   'Ẩn dụ giúp ta thấy chỗ cần kiểm tra.',
                'variation|The traveler holds a lantern high to illuminate the critical junction ahead.')]),
    (   'Chiếc cầu thiếu nhịp',
        'A bridge landscape in clear morning light.',
        [   (   'Bạn nhìn cây cầu hoàn chỉnh và hiểu cách nó nối bờ.',
                'environment|A wooden bridge spanning a ravine in clear morning light with quiet water below.'),
            (   'Tự dựng cầu lại buộc bạn đặt từng nhịp đúng chỗ.',
                'full_scene|A builder places timber planks along the bridge deck in morning light.'),
            (   'Một thanh còn thiếu làm lộ ra phần chưa chắc chắn.',
                'variation|The builder pauses and discovers a visible missing plank in the bridge center.'),
            (   'Nhìn lâu thêm vào cầu không tự chứng minh bạn dựng được.',
                'still_life|A missing bridge plank gap framed against morning light without figures.'),
            (   'Hai việc có thể cùng cần, nhưng kiểm tra khác nhau.',
                'white_card|An observation eye icon beside assembly tools on pure white.'),
            (   'Câu hỏi tốt chỉ đúng vào nhịp cầu đang thiếu.',
                'full_scene|The builder examines the exact missing joint with measuring tools.'),
            (   'Nó nhỏ hơn lời phán xét rằng bạn chẳng hiểu gì.',
                'variation|The builder smiles calmly, recognizing that most of the bridge structure remains sound.')]),
    (   'Cánh cửa gợi ý',
        'A memory warehouse under dim ambient lighting.',
        [   (   'Một câu hỏi đưa sẵn từ khóa giống cánh cửa mở.',
                'environment|A wide architectural warehouse aisle lined with drawers under dim ambient lighting.'),
            (   'Bạn có thể bước theo lối đó mà ít phải tự tìm.',
                'full_scene|A learner walks down an open illuminated warehouse corridor.'),
            (   'Khi đổi cách hỏi, cánh cửa quen có thể không còn.',
                'variation|The learner stops as a familiar doorway ahead closes slowly.'),
            (   'Lúc ấy, điều cần thử là đường đi tới ý chính.',
                'still_life|An antique brass lantern resting on an unlabeled wooden storage chest.'),
            (   'Nhà kho này chỉ là ẩn dụ để thấy nhiệm vụ.',
                'white_card|A transparent architectural conceptual model of storage compartments on pure white.'),
            (   'Ta không gán mỗi chiếc ngăn cho một vùng não riêng.',
                'full_scene|The learner inspects interconnected drawers without anatomical labels.'),
            (   'Đừng biến một bức hình dễ nhớ thành bằng chứng sinh học.',
                'variation|The learner steps back, viewing the warehouse model as an analytical tool.')]),
    (   'Một lỗi hữu ích',
        'A workshop model bench under warm light.',
        [   (   'Trong xưởng, chỗ cầu bị hở cho người thợ một thông tin.',
                'environment|A quiet craft workshop with miniature wooden models on benches under warm light.'),
            (   'Nó cho biết thanh nào chưa được đặt đúng vị trí.',
                'full_scene|A craftsperson examines a bridge model joint on the workshop bench.'),
            (   'Một câu trả lời thiếu cũng có thể chỉ rõ lỗ hổng.',
                'variation|The craftsperson points directly at the unfastened joint with precision.'),
            (   'Điều hữu ích là khoảng trống cụ thể, không phải cảm giác thua.',
                'still_life|A wooden bridge model joint glowing under a workbench lamp with tools nearby.'),
            (   'Nếu chỉ nhìn điểm tổng, bạn có thể bỏ qua chi tiết đó.',
                'white_card|A large uncalibrated gauge contrasting with a single highlighted connector joint on '
                'white.'),
            (   'Nếu chỉ đọc lại mọi thứ, bạn lại mất dấu chỗ cần sửa.',
                'full_scene|The craftsperson sets aside repetitive blueprint sheets to focus on the model.'),
            (   'Độ chính xác của câu hỏi sẽ quyết định bước tiếp theo.',
                'variation|The craftsperson aligns a small repair tool with the exposed joint.')]),
    (   'Giới hạn bằng chứng',
        'An evidence gallery under focused spotlights.',
        [   (   'Thí nghiệm dùng đoạn văn, với điều kiện được thiết kế.',
                'environment|A quiet museum evidence gallery with bounded display cases under focused spotlights.'),
            (   'Nó không hứa mọi môn học đều tăng đúng một mức.',
                'full_scene|A researcher examines two distinct experimental display cases in the gallery.'),
            (   'Cũng không cho ta một con số mất trí nhớ chung cho mọi người.',
                'variation|The researcher views different recall data columns without a single universal scale.'),
            (   'Từ kết quả ấy, ta rút ra một câu hỏi có ích.',
                'still_life|An open scientific journal page and an illuminated magnifying glass in a display.'),
            (   'Buổi học đang luyện nhìn đáp án hay tự gọi lại ý?',
                'white_card|Two contrasting study icons: a visible answer sheet vs a mental recall arrow on white.'),
            (   'Câu hỏi này cụ thể hơn lời khuyên phải cố thêm.',
                'full_scene|The researcher gestures toward the focused question display on the gallery wall.'),
            (   'Nó cũng mở đường cho cách đọc tài liệu khó.',
                'variation|The researcher walks toward the gallery exit leading to an open study room.')]),
    (   'Bài báo khó',
        'A reading room in morning sunlight.',
        [   (   'Bạn đọc một bài báo, gật đầu qua từng đoạn lập luận.',
                'environment|A bright university reading room with empty study tables in morning sunlight.'),
            (   'Những từ quen thuộc khiến trang giấy có vẻ rất dễ hiểu.',
                'full_scene|A reader sits at a table highlighting sentences in an academic journal.'),
            (   'Nhưng vấn đề nghiên cứu và kết luận chưa chắc đã nối được.',
                'variation|The reader pauses and frowns as a missing link appears in the causal argument.'),
            (   'Đổi sang kể lại câu hỏi sẽ làm rõ điều còn thiếu.',
                'still_life|An open printed journal paper beside a notepad with a drawn question mark.'),
            (   'Đích đến không phải chép lại tên từng mục của bài.',
                'white_card|A copied outline table contrasting with an active causal explanation sketch on white.'),
            (   'Điều cần có là quan hệ giữa dữ liệu và kết luận.',
                'full_scene|The reader draws arrows connecting evidence notes to the study conclusion.'),
            (   'Một sơ đồ ngắn có thể làm lộ đoạn nối còn mơ hồ.',
                'variation|The reader spots one weak dashed arrow in the emerging causal diagram.')]),
    (   'Câu hỏi phản biện',
        'A defense room under warm interior light.',
        [   (   'Trước hội đồng, câu hỏi thường đổi cách diễn đạt quen thuộc.',
                'environment|A formal university defense room with an empty presentation podium in warm light.'),
            (   'Người trình bày cần nối lý do với lựa chọn phương pháp.',
                'full_scene|A presenter stands before the committee explaining a methodological chart.'),
            (   'Nhớ nguyên đoạn văn chưa chắc giúp giải thích mối nối ấy.',
                'variation|The presenter turns to the slide diagram to explain the core justification.'),
            (   'Một lời giải thích bằng lời riêng cho thấy chỗ đang vướng.',
                'still_life|A handwritten defense note sheet with arrows linking questions to methods.'),
            (   'Đó là lúc việc chuẩn bị có thể chuyển từ thuộc sang hiểu.',
                'white_card|A circular recitation loop breaking open into a forward reasoning path on white.'),
            (   'Phòng bảo vệ chỉ là tình huống ứng dụng để tự thử.',
                'full_scene|The presenter listens thoughtfully to a committee question.'),
            (   'Nghiên cứu vừa nêu không trực tiếp đo kết quả bảo vệ.',
                'variation|The presenter nods calmly, keeping the evidence boundary in perspective.')]),
    (   'Chọn một phép thử',
        'A campus cafe in afternoon sunlight.',
        [   (   'Bạn có thể bắt đầu nhỏ, ngay với một ý vừa đọc.',
                'environment|A sunlit campus cafe corner with empty wooden tables in afternoon light.'),
            (   'Thử kể lại cho người đối diện, khi tài liệu đã khép.',
                'full_scene|A student explains a concept to a friend across a small cafe table.'),
            (   'Nếu lời giải thích đứt, giữ lại đúng câu hỏi đó.',
                'variation|The student stops and sketches a question mark on a small paper napkin.'),
            (   'Đừng kéo cả chương sách vào một lượt kiểm tra đầu tiên.',
                'still_life|A ceramic coffee cup beside a single small concept card on the wooden table.'),
            (   'Một phạm vi nhỏ giúp bạn nhìn rõ lỗi đang ở đâu.',
                'white_card|A minimal magnifying circle isolating one focused concept node on pure white.'),
            (   'Rồi mở nguồn để đối chiếu, không đoán rằng mình đã đúng.',
                'full_scene|The student reopens the reference book to check the exact definition.'),
            (   'Lượt thử này tạo ra thông tin cho lần học kế tiếp.',
                'variation|The student jots down the verified correction on the small card.')]),
    (   'Trở lại bàn học',
        'A student desk under evening lamplight.',
        [   (   'Cuốn sách vẫn ở đó, nhưng câu hỏi của bạn đã khác.',
                'environment|A quiet student desk with an illuminated green lamp in the evening.'),
            (   'Bạn không hỏi mình đã nhìn trang này bao nhiêu lần.',
                'full_scene|A student pushes away a pile of repeated highlighting notes.'),
            (   'Bạn hỏi mình có giải thích được ý chính khi không nhìn.',
                'variation|The student looks at an empty sheet, preparing to test independent recall.'),
            (   'Chỗ bí giờ có địa chỉ, thay vì chỉ là nỗi lo.',
                'still_life|A handwritten diagram on paper with one circled question under desk lamplight.'),
            (   'Mở sách để sửa đúng chỗ ấy, rồi thử lại vào hôm sau.',
                'white_card|A corrected concept node connected to a next-day practice icon on pure white.'),
            (   'Cảm giác quen thuộc vẫn có ích, nhưng chưa đủ kết luận.',
                'full_scene|The student opens the book specifically to verify the circled item.'),
            (   'Đầu bạn cần một đường đi, không chỉ một trang vàng.',
                'variation|The student completes the sketch, satisfied with the reconstructed path.')]),
    (   'Tài liệu vẫn cần',
        'A university desk under window light.',
        [   (   'Tự nhớ không thay thế việc đọc kỹ một lập luận mới.',
                'environment|A bright university study room with a large wooden desk under morning window light.'),
            (   'Bạn vẫn cần xem bằng chứng và điều kiện của kết luận.',
                'full_scene|A student carefully examines an empirical evidence section in a research paper.'),
            (   'Cần giải bài, thử ví dụ và trao đổi khi mắc lại.',
                'variation|Two students discuss a difficult problem step over a shared notebook.'),
            (   'Tờ giấy chỉ giúp bạn lộ ra chỗ cần làm tiếp.',
                'still_life|A printed research article with a pencil resting across margin notes under window light.'),
            (   'Một bài kiểm tra ngắn không chứng minh bạn hiểu mọi thứ.',
                'white_card|A small checked self-test sheet beside an extensive unfinished research map on white.'),
            (   'Hãy dùng nó cùng những việc học cần cho môn đó.',
                'full_scene|The student integrates active recall sheets with textbook problems.'),
            (   'Giữ câu hỏi mở, rồi tiếp tục đối chiếu với bằng chứng.',
                'variation|The student flips back to the original reference to verify remaining doubts.')]),
    (   'Trở lại trang vàng',
        'The original student desk under lamp light.',
        [   (   'Quay lại cuốn sách vàng kín ở đầu câu chuyện này.',
                'still_life|The original densely highlighted textbook lying closed under the green desk lamp.'),
            (   'Bạn vẫn có thể dùng bút vàng để đánh dấu đoạn quan trọng.',
                'full_scene|The student highlights one single essential sentence in the textbook.'),
            (   'Nhưng sau đó hãy dành chỗ cho một tờ giấy trắng.',
                'variation|The student places a clean blank sheet of paper beside the book.'),
            (   'Đóng sách, viết điều còn nhớ và khoanh điều chưa rõ.',
                'still_life|A blank sheet of paper and a black pen waiting beside the closed textbook.'),
            (   'Mở ra, sửa một lỗi bằng cây bút màu khác.',
                'full_scene|The student writes in black ink and circles an uncertain term in red.'),
            (   'Ngày mai quay lại, thử trả lời trước khi nhìn sách.',
                'variation|The student closes the book and sets an answer card ready for tomorrow.'),
            (   'Lần này bạn có dấu vết của việc tự mình làm được.',
                'white_card|Two draft sheets showing an initial question followed by a verified answer on white.')]),
    (   'Một câu hỏi mang theo',
        'A study desk in morning sunlight.',
        [   (   'Trước khi rời bàn, hãy chọn một câu hỏi để mang theo.',
                'environment|A clean and tidy study desk in morning sunlight with an open window.'),
            (   'Khi không có tài liệu trước mặt, mình giải thích được gì?',
                'white_card|A closed book, a question card and a small explanation sketch on pure white.'),
            (   'Bạn không cần biến mọi buổi học thành một kỳ thi.',
                'full_scene|A student relaxed in a chair reviews a single handwritten card.'),
            (   'Chỉ cần thêm một lượt thử có thể đối chiếu được.',
                'variation|The student checks the card answer against the reference page.'),
            (   'Một ý viết ra, một chỗ bí khoanh lại để sửa.',
                'still_life|A small index card with one clear idea and one circled question in morning light.'),
            (   'Tờ giấy đó có thể chỉ hướng cho buổi học tiếp.',
                'full_scene|The student places the index card neatly on top of the next study book.'),
            (   'Giờ hãy gấp sách, rồi thử viết câu đầu tiên của bạn.',
                'variation|The student closes the textbook with a calm confident posture, picking up a pen.')])]

def _closing_resolution_beat(
    scene_id: str,
    beat_number: int,
    setting: str,
    last_quote: str,
    last_spec: str,
    previous_id: str,
) -> ResearchedBeat:
    """Create a context-aware closing beat for the final half-clause without mechanical hand-focus clones."""
    words = last_quote.split()
    tail = ' '.join(words[len(words) // 2 + 1:])
    last_shot, base_desc = last_spec.split('|', 1)
    lowered = f"{base_desc} {setting}".casefold()
    if last_shot == 'white_card' or any(k in lowered for k in ('diagram', 'arrow', 'timeline', 'path', 'chart', 'gauge')):
        shot_type = 'white_card'
        description = f'Clean schematic synthesis of {base_desc[0].lower() + base_desc[1:]} on pure white.'
        based_on = None
        preserve = ''
        change = 'Isolate the core structural comparison as the spoken clause resolves.'
    elif any(k in lowered for k in ('bridge', 'landscape', 'corridor', 'gallery', 'hall', 'classroom', 'cafe')):
        shot_type = 'variation'
        description = f'Wide spatial resolution in {setting}: {base_desc}'
        based_on = previous_id
        preserve = 'Keep the exact room, camera, furniture, clothing and existing props.'
        change = 'Hold on the wider spatial consequence as the spoken clause concludes.'
    else:
        shot_type = 'macro_prop'
        description = f'Close detail on the key artifact in {setting}: {base_desc}'
        based_on = None
        preserve = ''
        change = 'Shift to a close inspection of the key artifact as the clause resolves.'
    is_char_free = shot_type in ('still_life', 'environment') or (
        shot_type.startswith('white_') and not any(k in description.lower() for k in ('student', 'learner', 'person', 'people', 'human', 'figure'))
    )
    beat_char_ids = [] if is_char_free else ['CH01']
    return ResearchedBeat(
        image_id=f'{scene_id}_I{beat_number}',
        anchor_quote=tail,
        description=description,
        reason='Resolve the final clause with a context-matched visual beat.',
        character_ids=beat_char_ids,
        shot_type=shot_type,
        based_on=based_on,
        preserve=preserve,
        change=change,
        effect='cut',
    )


def build_topic() -> ResearchedTopic:
    scenes: list[ResearchedScene] = []
    for index, (title, setting, rows) in enumerate(STORY, 1):
        scene_id = f'SC{index:02d}'
        narration = ' '.join(row[0] for row in rows)
        visuals: list[ResearchedBeat] = []
        for number, (quote, spec) in enumerate(rows, 1):
            shot_type, description = spec.split('|', 1)
            previous = visuals[-1].image_id if shot_type == 'variation' else None
            is_char_free = shot_type in ('still_life', 'environment') or (
                shot_type.startswith('white_') and not any(k in description.lower() for k in ('student', 'learner', 'person', 'people', 'human', 'figure'))
            )
            beat_char_ids = [] if is_char_free else ['CH01']
            visuals.append(ResearchedBeat(
                image_id=f'{scene_id}_I{number}', anchor_quote=quote,
                description=f'{description} Setting: {setting}' if not shot_type.startswith('white_') else description,
                reason='Show the concrete object or action at its spoken anchor.',
                character_ids=beat_char_ids, shot_type=shot_type, based_on=previous,
                preserve='Keep the exact room, camera, furniture, clothing and existing props.' if previous else '',
                change=description, effect='cut',
            ))
        if index > 1:
            quote, spec = rows[-1]
            visuals.append(_closing_resolution_beat(
                scene_id=scene_id,
                beat_number=len(visuals) + 1,
                setting=setting,
                last_quote=quote,
                last_spec=spec,
                previous_id=visuals[-1].image_id,
            ))
        scenes.append(ResearchedScene(
            scene_id=scene_id, title=title, purpose=title,
            duration=round(len(narration.split()) / 4.0 + (.35 if index == len(STORY) else .7), 2),
            narration=narration, requirements=[f'R{index:02d}'], source_ids=['SRC01'] if index in (3, 4, 5, 6, 7, 12) else [],
            character_ids=['CH01'], action=rows[0][1].split('|', 1)[1], setting=setting,
            camera='Narration-led full-frame compositions', bg_description='', visual_beats=visuals,
            claim_facts=[(rows[0][0], 'SRC01', 'Tự kiểm tra có thể giúp ghi nhớ lâu hơn đọc lại.')] if index == 6 else [],
        ))
    return ResearchedTopic(
        topic='Ảo giác hiểu bài khi đọc lại và cách kiểm tra bằng tờ giấy trắng',
        audience='Sinh viên và người tự học tại Việt Nam', goal='Phân biệt cảm giác quen thuộc với khả năng tự nhớ, qua bằng chứng và một phép thử nhỏ.',
        video_type='research_explainer', aspect_ratio='16:9', format_profile='long_16x9',
        min_duration=300., max_duration=480., scenes=scenes, subtitles=False, voice='VietNarrator', speed=1.0,
        visual_pacing_profile='full_frame_v1',
        style=STYLE_DESCRIPTION,
        characters=[{'id': 'CH01', 'name': 'Người học', 'appearance': CAST_APPEARANCE, 'outfit': DEFAULT_OUTFIT}],
        required_points=[{'id': f'R{i:02d}', 'text': title} for i, (title, _, _) in enumerate(STORY, 1)],
        sources=[{
            'id': 'SRC01', 'title': 'Test-Enhanced Learning: Taking Memory Tests Improves Long-Term Retention',
            'reference': 'Roediger & Karpicke (2006), Psychological Science 17(3), 249–255. https://doi.org/10.1111/j.1467-9280.2006.01693.x; accessed 2026-10-16.',
            'facts': ['Tự kiểm tra có thể giúp ghi nhớ lâu hơn đọc lại.'],
        }],
        conversational_facts=True,
        packaging=PackagingSpec(youtube_title='Đọc Rất Chăm, Vì Sao Gấp Sách Lại Quên?',
                               visual_hook='An open highlighted textbook beside a blank recall sheet.',
                               text_overlay='HIỂU THẬT CHƯA', contrast_pair='Trang sách quen mắt và tờ giấy tự nhớ'),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', '--output-dir', dest='out', type=Path, required=True)
    args = parser.parse_args()
    result = write_production_package(args.out, build_topic())
    import json
    print(json.dumps({key: result[key] for key in (
        'brief_file', 'content_file', 'valid_contracts', 'contract_errors', 'packaging_warnings',
    )}, ensure_ascii=False, indent=2))
    if not result['valid_contracts'] or result['cadence_report']['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
