"""Author a research-backed landscape acceptance package without provider calls."""
from __future__ import annotations

import argparse
from pathlib import Path

from tools.research_story_architect import (
    PackagingSpec,
    ResearchedBeat,
    ResearchedScene,
    ResearchedTopic,
    write_production_package,
)

# Each row is an authored narration unit and a visible action, not an automatic
# subdivision of a generic background prompt. Text is never painted implicitly.
STORY: list[tuple[str, str, list[tuple[str, str]]]] = [
    ('Trang sách vàng', 'A Vietnamese student desk at night, green lamp, yellow highlighter, blue textbook.', [
        ('Trang sách vàng kín, đầu bạn vẫn trống.', 'macro_prop|An open textbook covered in dense yellow highlighting.'),
        ('Bạn gạch thêm một dòng.', 'full_scene|A student draws one more yellow line at the desk.'),
        ('Rồi gấp cuốn sách lại.', 'variation|The same student closes the textbook.'),
        ('Cầm cây bút lên.', 'macro_prop|Close view of a hand lifting a black pen.'),
        ('Đặt xuống tờ giấy trắng.', 'full_scene|The student holds a pen over an untouched sheet.'),
        ('Bạn định viết gì?', 'variation|The pen hesitates above the sheet; the student looks puzzled.'),
        ('Định nghĩa vừa đọc biến mất.', 'white_card|A blank paper icon beside a closed textbook icon on white.'),
        ('Mở sách, mọi câu lại quen.', 'full_scene|The student reopens the highlighted textbook and recognizes the page.'),
        ('Chuyện gì vừa xảy ra giữa hai lần mở sách?', 'variation|The student looks from the familiar textbook to the blank sheet.'),
    ]),
    ('Hai thao tác', 'The same desk in morning light, textbook on left, blank sheet on right.', [
        ('Hãy đặt cuốn sách sang bên trái bàn học của bạn.', 'full_scene|A student slides the textbook to the left side of the desk.'),
        ('Bên phải là tờ giấy chưa có một dòng nào.', 'macro_prop|Close view of the untouched sheet on the right side.'),
        ('Khi nhìn bên trái, mắt bạn có sẵn câu trả lời.', 'full_scene|The student reads with an index finger following a printed line.'),
        ('Chỉ cần nhận ra câu đó, bạn có thể gật đầu.', 'variation|The student nods while following the same printed line.'),
        ('Nhưng nhìn sang phải, bạn phải tự viết từng ý.', 'full_scene|The student turns toward the blank sheet with a pen.'),
        ('Không có dòng chữ nào trên giấy để dẫn đường.', 'macro_prop|The pen tip hangs above the completely blank sheet.'),
        ('Hai thao tác này cần được kiểm tra bằng hai cách.', 'white_card|An open book icon and a pen writing icon, clearly separated on white.'),
    ]),
    ('Câu trả lời có sẵn', 'A study desk with one printed worked example and an empty exercise page.', [
        ('Bạn nhìn lời giải, từng bước đều có vẻ hợp lý.', 'full_scene|The student studies a neatly worked example on a printed page.'),
        ('Ngón tay trượt xuống, từ dòng đầu đến dòng cuối.', 'macro_prop|A finger moves down successive lines of a worked example.'),
        ('Thử che phần bên dưới bằng một tấm bìa nhỏ.', 'full_scene|The student covers the lower half of the example with a card.'),
        ('Bây giờ hãy tự viết bước tiếp theo ra giấy.', 'variation|The student tries to write the hidden next step.'),
        ('Nếu bút dừng lại, đánh dấu đúng vị trí đó.', 'macro_prop|A pen draws a small circle beside the unfinished step.'),
        ('Dấu tròn chỉ chỗ cần học, không phải điểm số.', 'white_card|An unfinished route with one clearly circled missing section on white.'),
        ('Bạn vừa có một câu hỏi cụ thể để quay lại.', 'full_scene|The student points to the circled missing step before reopening the example.'),
    ]),
    ('Đo bằng tờ giấy', 'A quiet study table, closed book, pen and an ordinary blank notebook.', [
        ('Chọn một đoạn ngắn trong bài bạn đang phải học.', 'full_scene|The student selects a short section of a textbook.'),
        ('Đọc hết đoạn đó, rồi đóng sách bằng chính tay mình.', 'variation|The student closes the textbook after reading the selected section.'),
        ('Viết ba ý chính, dùng những từ bạn thường nói.', 'macro_prop|A hand draws three simple bullet marks on a notebook page.'),
        ('Đừng cố chép nguyên câu chữ đã nằm trong sách.', 'full_scene|The closed book remains aside while the student writes independently.'),
        ('Nếu chỉ nhớ một ý, cứ để hai dòng trống.', 'macro_prop|One bullet contains a simple sketch; the next two lines remain empty.'),
        ('Những dòng trống giúp bạn nhìn thấy phần còn thiếu.', 'white_card|Three horizontal rows with the last two visibly empty on white.'),
        ('Giữ tờ giấy lại để đối chiếu sau khi đọc.', 'full_scene|The student puts the recall sheet beside the closed textbook.'),
    ]),
    ('Không nhìn trộm', 'The same study table, textbook closed beyond arm reach, notebook in front.', [
        ('Bạn có thể muốn hé sách ngay khi vừa bí.', 'full_scene|The student reaches toward the closed book while holding a pen.'),
        ('Thử dời cuốn sách ra xa thêm một gang tay.', 'variation|The student pushes the closed book farther away.'),
        ('Cho mình một lượt viết trước khi xem câu trả lời.', 'full_scene|The student returns to writing with the book out of reach.'),
        ('Ghi cả những điều bạn còn đang phân vân xuống.', 'macro_prop|A hand draws a question mark beside an uncertain notebook sketch.'),
        ('Sau đó mới mở sách, tìm đúng đoạn cần so.', 'full_scene|The student opens the book beside the uncertain sketch.'),
        ('Dùng màu khác sửa phần sai trên tờ giấy cũ.', 'macro_prop|A red pen corrects one part of the existing black sketch.'),
        ('Bạn sẽ thấy mình đã bỏ sót chi tiết nào.', 'full_scene|The student compares the original black sketch with the red correction.'),
    ]),
    ('Nhớ hay chỉ quen', 'A desk with a highlighted textbook and a handwritten recall sheet.', [
        ('Một trang sách quen mắt có thể khiến bạn yên tâm.', 'full_scene|The student smiles while looking at a familiar highlighted page.'),
        ('Nhưng tờ giấy bên cạnh đặt ra câu hỏi khác.', 'macro_prop|The handwritten recall sheet sits next to the highlighted page.'),
        ('Khi chữ in biến mất, bạn tự dựng lại được gì?', 'full_scene|The student covers the textbook and inspects the recall sheet.'),
        ('Hãy nhìn các mũi tên bạn vừa vẽ trên giấy.', 'macro_prop|Three hand-drawn boxes connected by two arrows.'),
        ('Mũi tên nào bạn chưa giải thích được bằng lời?', 'variation|A pen points to one unexplained arrow between boxes.'),
        ('Khoanh nó lại, viết một câu hỏi ngay bên cạnh.', 'macro_prop|A hand circles that arrow and adds a small question mark.'),
        ('Buổi học tiếp theo có thể bắt đầu từ chỗ đó.', 'full_scene|The student places the circled-arrow page on top of tomorrow study materials.'),
    ]),
    ('Thử với một khái niệm', 'A student desk with three simple cards representing question, evidence and conclusion.', [
        ('Ví dụ bạn vừa đọc về bằng chứng trong nghiên cứu.', 'full_scene|The student reads an illustrated page about observations and conclusions.'),
        ('Đóng tài liệu, vẽ ba ô trên một tờ giấy.', 'macro_prop|A hand draws three empty boxes after closing the document.'),
        ('Ô đầu là điều bạn đang muốn tìm câu trả lời.', 'full_scene|The student puts a question-mark card into the first box.'),
        ('Ô giữa chứa điều đã quan sát hoặc đo được.', 'macro_prop|A ruler and observation dots appear inside the middle box.'),
        ('Ô cuối là nhận xét bạn rút ra từ đó.', 'full_scene|The student places a conclusion card in the last box.'),
        ('Bây giờ nối các ô, giải thích từng mũi tên.', 'variation|The student connects the three boxes and points along each arrow.'),
        ('Bạn đang thử dựng lập luận bằng chính tay mình.', 'full_scene|The student explains the completed three-box diagram to an empty chair.'),
    ]),
    ('Mũi tên còn thiếu', 'The same desk with the three-box diagram and a pencil eraser.', [
        ('Giả sử bạn vẽ được ba ô nhưng chưa nối được.', 'macro_prop|Three boxes remain disconnected on the notebook page.'),
        ('Đừng vội mở sách để chép toàn bộ sơ đồ mới.', 'full_scene|The student pauses before opening a reference book.'),
        ('Hãy chỉ vào đúng hai ô đang bị tách rời.', 'macro_prop|A finger points between two disconnected boxes.'),
        ('Bạn cần biết quan sát nào hỗ trợ cho nhận xét.', 'white_card|Observation dots on one side and a conclusion card on the other.'),
        ('Viết câu hỏi đó, rồi tìm đoạn giải thích tương ứng.', 'full_scene|The student searches the textbook with one specific question beside it.'),
        ('Đọc xong, đóng sách và thử nối lại một lần.', 'variation|The student closes the book and draws the missing arrow.'),
        ('Lần này bạn kiểm tra đúng mắt xích vừa bị thiếu.', 'macro_prop|The newly drawn arrow fills the previously empty gap.'),
    ]),
    ('Một bài nghiên cứu', 'A clean university classroom desk with two groups of paper cards and books.', [
        ('Các nhà nghiên cứu đã so sánh hai cách học này.', 'full_scene|Two groups of student desks have the same prose passage.'),
        ('Một nhóm đọc lại, nhóm kia thử nhớ sau khi đọc.', 'full_scene|One student rereads while another writes with the passage closed.'),
        ('Ở bài kiểm tra trễ, nhóm tự nhớ giữ lại nhiều hơn.', 'white_card|Two plain recall sheets after a calendar page turn; one contains more recalled marks.'),
        ('Kết quả này xuất hiện với các đoạn văn trong thí nghiệm.', 'macro_prop|A prose passage beside a small laboratory clipboard, without invented numbers.'),
        ('Nó không có nghĩa mọi môn học đều giống hệt nhau.', 'full_scene|Different textbooks and a mathematics exercise sit around the experiment sheet.'),
        ('Cũng không có nghĩa bạn nên bỏ phần đọc tài liệu.', 'variation|A student opens a textbook before attempting a recall sheet.'),
        ('Điều đáng thử là thêm lượt tự nhớ sau khi đọc.', 'full_scene|The student places a short recall sheet after the reading material.'),
    ]),
    ('Khi kiểm tra ngay', 'A classroom table with an open passage, a closed passage and a small clock.', [
        ('Có một chi tiết cần giữ lại khi đọc kết quả.', 'macro_prop|A hand marks one specific part of a research summary.'),
        ('Bài kiểm tra ngay có thể khác bài kiểm tra trễ.', 'white_card|Two clock icons separated by a calendar page on white.'),
        ('Trong nghiên cứu ấy, đọc lại có lợi ở mốc rất gần.', 'full_scene|A student reviews a passage beside a clock indicating a short interval.'),
        ('Nhưng lợi thế đổi chiều khi kiểm tra sau một khoảng.', 'full_scene|A calendar turns before students complete recall sheets.'),
        ('Vì vậy đừng chỉ nhìn tờ giấy ngay cuối buổi.', 'macro_prop|A hand places today recall sheet into a folder.'),
        ('Hãy hẹn một lượt kiểm tra nữa vào hôm sau.', 'full_scene|The student places a recall card beside tomorrow calendar square.'),
        ('Bạn sẽ có thêm một phép đo thay vì phỏng đoán.', 'variation|The student puts two dated recall sheets side by side.'),
    ]),
    ('Lịch thử của bạn', 'A Vietnamese student room in daylight, paper calendar and a small study notebook.', [
        ('Bạn có thể bắt đầu với một đoạn tài liệu nhỏ.', 'full_scene|A student selects a short section from an ordinary textbook.'),
        ('Đọc kỹ, gấp lại, rồi viết điều mình còn nhớ.', 'variation|The student closes the section and writes in a notebook.'),
        ('Mở ra đối chiếu, sửa bằng một cây bút màu khác.', 'macro_prop|A red pen corrects a black-ink recall sheet beside the open book.'),
        ('Cuối trang ghi một câu hỏi vẫn làm bạn mắc lại.', 'macro_prop|A hand draws one question mark at the bottom of the notebook page.'),
        ('Hôm sau, trả lời câu ấy trước khi mở tài liệu.', 'full_scene|Morning light falls on the student answering the saved question with the book closed.'),
        ('Rồi mới kiểm tra xem câu trả lời đã đủ chưa.', 'variation|The student compares the new answer with the textbook.'),
        ('Đây là lịch thử cá nhân, bạn có thể điều chỉnh.', 'full_scene|The student moves a paper study card to another calendar square.'),
    ]),
    ('Sai ở đâu', 'A study desk with a recall notebook, black pen, red pen and reference book.', [
        ('Khi sửa bài, đừng chỉ chấm một dấu đúng hoặc sai.', 'macro_prop|A recall sheet shows a tick and a cross beside unfinished ideas.'),
        ('Chỉ rõ mình thiếu khái niệm, thiếu bước hay nhầm quan hệ.', 'white_card|Three simple icons: an empty box, a missing stair and a reversed arrow.'),
        ('Thiếu khái niệm, quay lại đúng đoạn định nghĩa trong sách.', 'full_scene|The student locates one definition in the reference book.'),
        ('Thiếu bước, viết lại thao tác nằm giữa hai dòng đó.', 'macro_prop|A pen inserts a missing middle step between two existing steps.'),
        ('Nhầm quan hệ, thử đổi chiều mũi tên rồi giải thích.', 'macro_prop|A hand erases a reversed arrow and redraws its direction.'),
        ('Mỗi loại lỗi cần một câu hỏi sửa khác nhau.', 'full_scene|The student sorts three error cards beside three matching question cards.'),
        ('Ghi đủ cụ thể để lần sau bạn biết kiểm tra gì.', 'variation|The student adds a small repair checklist to the notebook.'),
    ]),
    ('Đừng chỉ học câu chữ', 'A university desk with a small jar, pebbles and a hand-drawn diagram.', [
        ('Một câu định nghĩa thuộc lòng vẫn cần được thử bằng ví dụ.', 'full_scene|A student puts a definition card next to a concrete object.'),
        ('Hãy nghĩ ra một trường hợp mà khái niệm áp dụng được.', 'variation|The student draws a simple example in the notebook.'),
        ('Rồi tìm trường hợp gần giống nhưng lại không phù hợp.', 'macro_prop|A hand sketches a similar example with one visibly different condition.'),
        ('Đặt hai ví dụ cạnh nhau, khoanh chi tiết tạo khác biệt.', 'macro_prop|The student circles the differing condition between the two sketches.'),
        ('Nếu chưa chỉ được, viết câu hỏi đó vào sổ.', 'full_scene|The student writes a question beside the circled condition.'),
        ('Sau đó đối chiếu với tài liệu hoặc hỏi người hướng dẫn.', 'full_scene|A student shows the specific example page to a teacher at a desk.'),
        ('Bạn đang kiểm tra cách dùng, bên cạnh việc nhớ tên gọi.', 'white_card|A name tag icon beside a hand applying an idea to an object.'),
    ]),
    ('Đổi cách hỏi', 'A quiet desk with three question cards, textbook closed at the corner.', [
        ('Thay vì hỏi mình đã đọc hết bao nhiêu trang rồi.', 'full_scene|The student looks at a tall stack of read textbook pages.'),
        ('Hãy chọn một ý và thử giải thích bằng lời riêng.', 'variation|The student turns one idea into a small spoken explanation sketch.'),
        ('Thay vì đếm số dòng đã được tô bằng bút vàng.', 'macro_prop|A highlighted page is placed aside without counting lines.'),
        ('Hãy đếm những câu hỏi bạn trả lời khi sách đóng.', 'macro_prop|A closed book beside three question cards with simple check marks.'),
        ('Thay vì chỉ nhìn thời gian ngồi trước bàn học.', 'full_scene|The student turns from a desk clock toward the recall notebook.'),
        ('Hãy nhìn một chỗ bí đã được sửa cho rõ hơn.', 'macro_prop|A previously circled missing arrow now has a clear correction.'),
        ('Các con số vẫn có ích khi gắn với việc cụ thể.', 'white_card|A clock, page stack and repaired diagram connected to concrete study actions.'),
    ]),
    ('Một lượt học thật', 'The original student desk, lamp now off, textbook and a clean notebook.', [
        ('Bây giờ bạn có thể thử ngay với trang đang mở.', 'full_scene|The student places a clean notebook beside the open textbook.'),
        ('Chọn một đoạn mà bạn nghĩ mình đã hiểu khá rõ.', 'macro_prop|A finger brackets a small section on the page.'),
        ('Đọc xong, đóng sách và đặt bút vào tờ giấy.', 'full_scene|The student closes the book and starts the recall sheet.'),
        ('Viết điều chính yếu, thêm một ví dụ do bạn tự nghĩ.', 'variation|The student adds a simple original example under the recalled idea.'),
        ('Khoanh đúng chỗ còn bí trước khi nhìn lại câu trả lời.', 'macro_prop|A pen circles the unfinished part before the textbook is reopened.'),
        ('Đối chiếu, sửa lỗi, rồi cất tờ giấy cho lượt sau.', 'full_scene|The student corrects the page and stores it in a small folder.'),
        ('Bạn có một sản phẩm nhỏ để kiểm tra lại ngày mai.', 'variation|The student places the folder next to tomorrow study card.'),
    ]),
    ('Khi quá khó', 'A desk with one long chapter, several blank sheets and a simple ruler.', [
        ('Nếu cả trang khiến bạn không viết được một ý nào.', 'full_scene|The student faces a long textbook page and an empty recall sheet.'),
        ('Hãy giảm phần cần học xuống còn một đoạn ngắn hơn.', 'macro_prop|A ruler isolates a much smaller section of the page.'),
        ('Bạn cũng có thể nhìn một câu hỏi gợi ý cụ thể.', 'full_scene|The student places one small question card beside the notebook.'),
        ('Thử trả lời, rồi kiểm tra với tài liệu ngay sau đó.', 'variation|The student writes an answer and then opens the reference section.'),
        ('Đừng để một câu đoán sai nằm nguyên mà không đối chiếu.', 'macro_prop|A red correction replaces an unverified answer on the recall sheet.'),
        ('Khi làm được đoạn ngắn, bạn mới ghép thêm phần tiếp.', 'full_scene|The student places two completed small section cards together.'),
        ('Điều chỉnh độ khó để vẫn có thể học và sửa.', 'white_card|A hand adjusts the number of small study cards in a manageable stack.'),
    ]),
    ('Tài liệu vẫn cần', 'A university desk with a printed paper, notebook, references and a pencil.', [
        ('Tự nhớ không thay thế việc đọc kỹ một lập luận mới.', 'full_scene|The student carefully reads a new research argument before writing.'),
        ('Bạn vẫn cần xem bằng chứng và điều kiện của kết luận.', 'macro_prop|A finger connects observation notes to a qualified conclusion on the paper.'),
        ('Cần giải bài, thử ví dụ và trao đổi khi mắc lại.', 'full_scene|Two students discuss one concrete exercise with a shared notebook.'),
        ('Tờ giấy chỉ giúp bạn lộ ra chỗ cần làm tiếp.', 'macro_prop|A recall sheet reveals one circled question among completed sections.'),
        ('Một bài kiểm tra ngắn không chứng minh bạn hiểu mọi thứ.', 'white_card|A small checked recall card next to a much larger unfinished map.'),
        ('Hãy dùng nó cùng những việc học cần cho môn đó.', 'full_scene|The student combines textbook reading, an exercise and recall notes.'),
        ('Giữ câu hỏi mở, rồi tiếp tục đối chiếu với bằng chứng.', 'variation|The student follows a saved question back to the reference paper.'),
    ]),
    ('Trở lại trang vàng', 'The original Vietnamese desk at night, yellow highlighter, textbook and corrected recall sheet.', [
        ('Quay lại cuốn sách vàng kín ở đầu câu chuyện này.', 'macro_prop|The original densely highlighted textbook lies under the green lamp.'),
        ('Bạn vẫn có thể dùng bút vàng để đánh dấu đoạn quan trọng.', 'full_scene|The student highlights one carefully selected passage.'),
        ('Nhưng sau đó hãy dành chỗ cho một tờ giấy trắng.', 'variation|The student moves a blank sheet next to the highlighted book.'),
        ('Đóng sách, viết điều còn nhớ và khoanh điều chưa rõ.', 'full_scene|The student writes independently and circles one uncertain item.'),
        ('Mở ra, sửa một lỗi bằng cây bút màu khác.', 'macro_prop|A red pen corrects the circled uncertainty on the black-ink sheet.'),
        ('Ngày mai quay lại, thử trả lời trước khi nhìn sách.', 'full_scene|Morning light returns as the student answers the saved question.'),
        ('Lần này bạn có dấu vết của việc tự mình làm được.', 'macro_prop|Two recall sheets show an unfinished sketch followed by its corrected version.'),
    ]),
    ('Một câu hỏi mang theo', 'A clean study desk in morning light, closed textbook and one completed recall sheet.', [
        ('Trước khi rời bàn, hãy chọn một câu hỏi để mang theo.', 'full_scene|The student selects one small question card before leaving the desk.'),
        ('Khi không có tài liệu trước mặt, mình giải thích được gì?', 'white_card|A closed book, a question card and a small explanation sketch on pure white.'),
        ('Bạn không cần biến mọi buổi học thành một kỳ thi.', 'full_scene|The student casually reviews a small card in a relaxed study room.'),
        ('Chỉ cần thêm một lượt thử có thể đối chiếu được.', 'variation|The student checks the small answer against the reference page.'),
        ('Một ý viết ra, một chỗ bí khoanh lại để sửa.', 'macro_prop|One handwritten idea and one circled question on a small sheet.'),
        ('Tờ giấy đó có thể chỉ hướng cho buổi học tiếp.', 'full_scene|The student places the small sheet on top of the next study book.'),
        ('Giờ hãy gấp sách, rồi thử viết câu đầu tiên của bạn.', 'full_scene|The student closes the textbook and confidently begins a fresh sheet.'),
    ]),
]


def build_topic() -> ResearchedTopic:
    scenes: list[ResearchedScene] = []
    for index, (title, setting, rows) in enumerate(STORY, 1):
        scene_id = f'SC{index:02d}'
        narration = ' '.join(row[0] for row in rows)
        visuals: list[ResearchedBeat] = []
        for number, (quote, spec) in enumerate(rows, 1):
            shot_type, description = spec.split('|', 1)
            previous = visuals[-1].image_id if shot_type == 'variation' else None
            visuals.append(ResearchedBeat(
                image_id=f'{scene_id}_I{number}', anchor_quote=quote,
                description=f'{description} Setting: {setting}' if not shot_type.startswith('white_') else description,
                reason='Show the concrete object or action at its spoken anchor.',
                character_ids=['CH01'], shot_type=shot_type, based_on=previous,
                preserve='Keep the exact room, camera, furniture, clothing and existing props.' if previous else '',
                change=description, effect='cut',
            ))
        if index > 1:
            quote, spec = rows[-1]
            words = quote.split()
            tail = ' '.join(words[len(words) // 2 + 1:])
            visuals.append(ResearchedBeat(
                image_id=f'{scene_id}_I{len(visuals) + 1}', anchor_quote=tail,
                description=f'{spec.split("|", 1)[1]} Focus on the hands and the study object already named. Setting: {setting}',
                reason='Show the final concrete action as the spoken clause resolves.',
                character_ids=['CH01'], shot_type='macro_prop', change='Use a close view of the named action.',
            ))
        scenes.append(ResearchedScene(
            scene_id=scene_id, title=title, purpose=title,
            duration=round(len(narration.split()) / 4.0 + (.35 if index == len(STORY) else .7), 2),
            narration=narration, requirements=[f'R{index:02d}'], source_ids=['SRC01'] if index in (9, 10) else [],
            character_ids=['CH01'], action=rows[0][1].split('|', 1)[1], setting=setting,
            camera='Narration-led full-frame compositions', bg_description='', visual_beats=visuals,
            claim_facts=[(rows[2][0], 'SRC01', 'Tự kiểm tra có thể giúp ghi nhớ lâu hơn đọc lại.')] if index == 9 else [],
        ))
    return ResearchedTopic(
        topic='Ảo giác hiểu bài khi đọc lại và cách kiểm tra bằng tờ giấy trắng',
        audience='Sinh viên và người tự học tại Việt Nam', goal='Thử một lượt nhớ lại, đối chiếu và sửa lỗi cụ thể.',
        video_type='research_explainer', aspect_ratio='16:9', format_profile='long_16x9',
        min_duration=300., max_duration=480., scenes=scenes, subtitles=True, voice='Adam', speed=1.0,
        visual_pacing_profile='full_frame_v1',
        style='Hand-drawn 2D marker illustration, anonymous round-headed stick figures, flat muted teal and yellow. Complete integrated scenes; white cards use pure white. No unrequested lettering.',
        characters=[{'id': 'CH01', 'name': 'Người học', 'appearance': 'Anonymous round white head with a thick black outline, expressive dot eyes and thin black stick limbs.', 'outfit': 'Simple teal shirt.'}],
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
    parser.add_argument('--out', type=Path, required=True)
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
