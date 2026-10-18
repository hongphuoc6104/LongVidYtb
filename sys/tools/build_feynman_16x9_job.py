#!/usr/bin/env python3
"""Build the production-ready full_frame_v1 package for feynman-jargon-trap-16x9."""
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
    PackagingSpec,
    ResearchedTopic,
    build_scenes_from_story_rows,
    write_production_package,
)
from visual_style import CAST_APPEARANCE, DEFAULT_OUTFIT, STYLE_DESCRIPTION

STORY: list[tuple[str, str, list[tuple[str, str]]]] = [
    (
        "Cú giật mở đầu",
        "A Vietnamese student desk at night, yellow desk lamp, cold coffee cup, open laptop.",
        [
            ("Bạn nhét từ hoa mỹ để bài viết trông thông minh hơn?", "full_scene|A student sits at a wooden desk at night highlighting a simple word on an open laptop screen."),
            ("Rất có thể bạn đang tự hại mình.", "variation|The student looks tense as the laptop screen glares; the surrounding room stays dimly lit."),
            ("Sự thật hoàn toàn ngược lại.", "macro_prop|Close view of a dictionary search panel showing lengthy multi-syllable substitute terms."),
            ("Càng cố tỏ ra uyên bác, lập luận càng mất điểm.", "white_card|An ornate oversized speech balloon floats beside a tiny solid foundation block on pure white."),
        ],
    ),
    (
        "Đêm khuya và từ điển đồng nghĩa",
        "A student desk littered with drafts, sticky notes, and a digital clock showing 2 AM.",
        [
            ("Đêm khuya trước hạn nộp bài luận.", "full_scene|A student types anxiously at a desk piled with papers and sticky notes under a dim desk lamp."),
            ("Trên màn hình, bạn mở sẵn từ điển từ đồng nghĩa.", "macro_prop|Close view of laptop screen where ordinary words are systematically replaced by thesaurus entries."),
            ("Mỗi chữ đơn giản đều bị thay bằng thuật ngữ đa âm tiết.", "variation|The text on the screen swells into long paragraphs packed with abstract academic terminology."),
            ("Cảm giác học thuật dâng lên rất nhanh.", "variation|The student sits back with a confident smile, looking at the dense screen of academic text."),
            ("Trang viết trông thật chuyên nghiệp.", "white_card|A shiny gold seal with the words ACADEMIC PROSE stamped onto a sheet of paper on pure white."),
        ],
    ),
    (
        "Sự mơ hồ được ngụy trang",
        "A conceptual workspace where text paragraphs turn into dense visual fog.",
        [
            ("Nhưng đoạn văn càng dài, ý tưởng cốt lõi càng mờ mịt.", "full_scene|A page of dense academic prose begins dissolving into thick grey fog that obscures the underlying diagram."),
            ("Bạn tạm thấy yên tâm.", "variation|The student rests a hand on the keyboard, relieved that the page count is satisfied."),
            ("Bởi lớp vỏ ngôn từ đã che đi sự mơ hồ trong lập luận.", "macro_prop|A magnifying glass inspects the printed lines, revealing convoluted decorative spirals instead of clean arrows."),
            ("Nhưng chính bạn cũng bắt đầu lạc lối.", "variation|The student rubs their forehead in confusion, struggling to parse the logic of their own drafted paragraph."),
        ],
    ),
    (
        "Cái bẫy ảo giác uyên bác",
        "A minimalist white study space with academic symbols.",
        [
            ("Đây là cái bẫy quen thuộc của người mới làm nghiên cứu.", "full_scene|A student stands in an academic library, surrounded by towering bookshelves holding heavy reference volumes."),
            ("Ảo giác uyên bác.", "white_card|A ceremonial academic cap sits atop an ornate cardboard facade on pure white background."),
            ("Ta nhầm lẫn giữa việc dùng từ khó với việc thực sự hiểu sâu.", "variation|The cardboard facade slides away to reveal an empty wooden scaffold behind it; eyebrows tense with uncertainty."),
            ("Hai điều này hoàn toàn khác nhau.", "variation|Two divergent colored tracks branch apart on the clean floor."),
            ("[pause:500ms]", "macro_prop|A red ink marker draws a sharp decisive question mark beside the word ILLUSION on clean paper."),
        ],
    ),
    (
        "Thực nghiệm của Oppenheimer",
        "A clean cognitive psychology research room, white demonstration board.",
        [
            ("Vào năm hai nghìn không trăm linh sáu.", "full_scene|A bright university research corridor with academic posters and quiet experimental testing rooms."),
            ("Nhà tâm lý học Daniel Oppenheimer đã làm một thực nghiệm nổi tiếng.", "variation|Psychologist Daniel Oppenheimer stands calmly by a demonstration board displaying sample research essays."),
            ("Ông muốn đo lường xem:", "variation|Oppenheimer points to a diagrammatic evaluation scale on the board."),
            ("từ ngữ ảnh hưởng thế nào đến cách người đọc đánh giá bạn.", "macro_prop|A close view of a laboratory survey sheet measuring perceived author intelligence on a numeric scale."),
        ],
    ),
    (
        "Hai phiên bản văn bản",
        "An experimental evaluation room with two separate reading desks.",
        [
            ("Ông lấy các bài luận mẫu với lập luận chuẩn xác.", "full_scene|Two identical folders of research essays are laid out on a clean testing desk before two evaluators."),
            ("Một nhóm người đọc bản gốc với câu từ sáng rõ.", "variation|The left reader inspects clean, concise text with straightforward arguments."),
            ("Nhóm còn lại đọc bản bị thay bằng các từ đồng nghĩa dài dòng nhất.", "variation|The right reader frowns at the same essay padded with elaborate, multi-syllable synonyms."),
            ("Ý nghĩa gốc", "macro_prop|A magnifying glass centers on the core logical statement shared identically between the two drafts."),
            ("được giữ nguyên tuyệt đối.", "variation|Two matching green checkmarks glow beside both sample paragraphs."),
        ],
    ),
    (
        "Nghịch lý đánh giá",
        "A laboratory scoring board showing experimental data.",
        [
            ("Nội dung hai bài hoàn toàn giống nhau.", "white_card|Two identical blue puzzle pieces placed side by side on pure white background."),
            ("Chỉ khác lớp vỏ ngôn từ.", "variation|One puzzle piece is wrapped in simple brown paper; the other is smothered in heavy ornamental ribbon."),
            ("Nhưng kết quả thật bất ngờ.", "full_scene|A large bar chart is revealed in the laboratory: the simple text bar towers high while the complex text bar stays low."),
            ("Bài viết dùng từ ngữ đao to búa lớn bị đánh giá kém thông minh hơn hẳn.", "variation|Evaluators shake their heads skeptically over the thesaurus-padded essay on the table."),
            ("Tác giả viết giản dị lại được tin tưởng hơn.", "macro_prop|A rating form marked with a high credibility score beside the concise essay."),
        ],
    ),
    (
        "Cơ chế trôi chảy nhận thức",
        "A diagrammatic view of cognitive processing and brain mechanisms.",
        [
            ("Tại sao lại như vậy?", "full_scene|A thinker in a modern cognitive science lab looking up at a dynamic brain imaging display."),
            ("Bộ não con người vận hành dựa trên cơ chế trôi chảy nhận thức.", "white_card|A stylized diagram of a brain with smooth synchronized gears rotating easily on pure white."),
            ("Khi câu từ rườm rà,", "variation|Text blocks shaped like jagged obstacles drop into the cognitive pipeline."),
            ("não người đọc phải tốn nhiều năng lượng để giải mã.", "variation|The gears grind to a halt under the heavy text blocks, causing friction sparks."),
            ("Quá trình tiếp nhận bị tắc nghẽn liên tục.", "macro_prop|A cognitive energy gauge needle dropping sharply from green into the red zone."),
        ],
    ),
    (
        "Sự đề phòng tâm lý",
        "An academic review committee room with evaluators.",
        [
            ("Sự khó nhọc đó tạo ra cảm giác đề phòng.", "full_scene|A thoughtful evaluator leans back, viewing a jargony page with a critical and guarded squint."),
            ("Người đọc cảm thấy tác giả đang cố tình che giấu sự thiếu hụt.", "variation|The evaluator taps their pen impatiently on an obscure paragraph that requires three re-readings."),
            ("Khi phải đọc lại nhiều lần,", "variation|The evaluator turns the confusing page back and forth in frustration."),
            ("sự thuyết phục sẽ biến mất.", "variation|The reader sets down the paper with a sigh, unimpressed by the convoluted phrasing."),
            ("Lập luận sắc bén không cần núp bóng từ ngữ. [pause:500ms]", "white_card|A sharp polished geometric diamond rests solidly without any decorative padding on pure white."),
        ],
    ),
    (
        "Bài học con chim của Feynman",
        "A sunlit forest path with tall trees, quiet nature.",
        [
            ("Nhà vật lý Richard Feynman từng kể lại một bài học sâu sắc từ cha mình.", "full_scene|A young Feynman walks alongside his father under towering green trees in a peaceful forest."),
            ("Chuyện xảy ra", "variation|The camera tracks deeper into the sunlit woodland path."),
            ("trong một buổi đi dạo dưới tán rừng.", "variation|A small brown bird perches on a branch ahead, preening its feathers in morning sunlight."),
            ("Một đứa trẻ hàng xóm chỉ vào con chim", "variation|A neighbor boy runs up excitedly, pointing proudly up toward the tree branch."),
            ("và khoe tên gọi của nó.", "variation|The neighbor boy recites a long Latin species name with a smug expression."),
        ],
    ),
    (
        "Biết tên không bằng hiểu sự vật",
        "A nature observation clearing in the forest.",
        [
            ("Con chim đó có tên bằng tiếng Anh, tiếng Trung, hay tiếng Latinh.", "white_card|A detailed drawing of the bird surrounded by floating name tags in three different languages."),
            ("Bạn có thể thuộc lòng mọi cái tên đó.", "variation|The neighbor boy recites the names with a smug expression, looking satisfied with his memorization."),
            ("Nhưng bạn vẫn chưa biết gì về con chim cả.", "variation|The floating name tags fall away leaving only the living bird pecking at tree bark."),
            ("Nó sống ở đâu?", "variation|The camera tracks the bird hopping between tree branches in the canopy."),
            ("Nó rỉa lông ra sao, và kiếm ăn thế nào?", "macro_prop|Close view of the bird using its beak to clean its feathers and hunt insects beneath the bark."),
        ],
    ),
    (
        "Bản chất và chiếc nhãn dán",
        "An analytical study room with notebook sketches.",
        [
            ("Feynman nhận ra sự khác biệt sống còn.", "full_scene|Young Feynman takes notes in a sketchbook, drawing the bird's actual behavior rather than writing names."),
            ("Biết tên một khái niệm rất khác với việc hiểu bản chất.", "white_card|Two contrasting panels on white: left panel shows a word label; right panel shows dynamic motion arrows."),
            ("Thuật ngữ chỉ là cái nhãn dán bên ngoài.", "macro_prop|A hand peels away a printed decorative label from a mechanical clockwork device."),
            ("Quy luật vận động bên dưới mới là tri thức thực sự.", "variation|The inner brass gears of the device turn with precision, visible and unadorned."),
        ],
    ),
    (
        "Cơ chế phòng vệ tâm lý",
        "A university seminar room, student presentation podium.",
        [
            ("Vậy tại sao trong học thuật,", "full_scene|A student stands nervously at a seminar podium in a tiered university lecture hall."),
            ("người ta lại thích dùng từ ngữ khó hiểu?", "variation|The student gazes anxiously at the row of waiting professors."),
            ("Đó là cơ chế phòng vệ tâm lý.", "variation|The student raises a large metal shield emblazoned with abstract academic buzzwords."),
            ("Khi chưa nắm chắc vấn đề, người viết sợ bị coi là nông cạn.", "variation|The student grips the edges of the shield tightly, visibly anxious about being questioned."),
            ("Họ lấy chữ nghĩa làm tấm khiên che chắn.", "macro_prop|Close view of the shield surface showing interlocking academic terms acting as protective armor plates."),
        ],
    ),
    (
        "Bức tường khoảng cách giả tạo",
        "A defense presentation room facing an expert committee.",
        [
            ("Lớp áo giáp thuật ngữ dựng lên một bức tường khoảng cách.", "full_scene|A brittle brick wall of jargon separates the presenter from the attentive committee members."),
            ("Nó biến một ý niệm giản đơn thành điều gì đó bí hiểm.", "variation|The presenter peeks nervously over the top of the jargon wall toward the professors."),
            ("Nhưng trước người có chuyên môn, bức tường đó rất dễ sụp đổ.", "variation|An experienced committee professor calmly taps a loose brick at the base of the jargon wall."),
            ("Chỉ một câu hỏi xoáy", "macro_prop|A professor's index finger points firmly at an unsupported claim on the slide."),
            ("sẽ làm lộ rõ tất cả. [pause:500ms]", "white_card|The jargon wall crumbles to dust, revealing whether a solid conceptual foundation exists beneath."),
        ],
    ),
    (
        "Bước 1: Khái niệm cốt lõi",
        "A bright daytime desk, morning sunlight, clean wooden surface.",
        [
            ("Để làm chủ bài viết, hãy áp dụng kỹ thuật chuyển ngữ Feynman.", "full_scene|The learner sits upright at a sunny desk with clear workspace and renewed resolve."),
            ("Bước đầu tiên: chọn ra khái niệm hóc búa nhất trong nghiên cứu.", "variation|The learner scans a research manuscript and pinpoints the single most difficult concept."),
            ("Đặt nó lên bàn mổ xẻ.", "variation|The learner slides a clean white sheet of paper into the center of the desk."),
            ("Viết thẳng tên khái niệm", "macro_prop|A black ink fountain pen writes the title of the core concept at the top of a blank sheet."),
            ("lên đầu trang giấy trắng.", "variation|The learner steps back slightly, looking directly at the isolated single concept on paper."),
        ],
    ),
    (
        "Bước 2: Thử thách đứa trẻ 10 tuổi",
        "A friendly study corner with a child listener.",
        [
            ("Bước thứ hai: giải thích lại điều đó cho một đứa trẻ mười tuổi.", "full_scene|The learner sits across from an inquisitive ten-year-old child with curious, attentive eyes."),
            ("Quy tắc bất di bất dịch: cấm dùng từ chuyên môn.", "macro_prop|A red wooden STOP sign icon blocks a complex formula card, replaced by a simple common apple."),
            ("Hãy dùng những từ ngữ đời thường nhất.", "variation|The learner smiles and explains using everyday kitchen and playground examples; the child nods in comprehension."),
            ("Nếu không thể diễn đạt giản dị,", "variation|The learner gestures simply with both hands open in front of the child."),
            ("tức là bạn chưa hiểu sâu.", "white_card|A child-drawn stick figure smiling beside a clear, simple diagram on pure white."),
        ],
    ),
    (
        "Bước 3: Khoanh tròn điểm nghẽn",
        "The learner's review desk with draft pages.",
        [
            ("Bước thứ ba: khoanh tròn những chỗ bạn bị khựng lại.", "macro_prop|A red pencil firmly circles an awkward, overcomplicated sentence on the handwritten draft."),
            ("Điểm nào bạn buộc phải viện đến từ hoa mỹ,", "variation|The learner frowns at the red-circled sentence with tense eyebrows."),
            ("chính là nơi tư duy bị đứt gãy.", "white_card|A drawing of a stone bridge missing a critical arch stone right in the center on pure white."),
            ("Đừng lướt qua nó.", "variation|A red warning flag is planted beside the missing arch stone on the bridge drawing."),
            ("Hãy mở lại tài liệu gốc và lấp đầy lỗ hổng đó.", "full_scene|The learner reopens the primary textbook, reading the specific foundational proof to bridge the gap."),
        ],
    ),
    (
        "Bước 4: Phép ẩn dụ tương đồng",
        "A visual explanation board with comparative diagrams.",
        [
            ("Bước thứ tư: tạo ra một phép so sánh tương đồng.", "full_scene|A dual whiteboard shows liquid viscosity compared side by side with a rush-hour traffic jam."),
            ("Ví dụ: giải thích độ nhớt chất lỏng", "variation|The learner draws a beaker with thick honey flowing slowly downward."),
            ("như dòng xe kẹt cứng giờ cao điểm.", "macro_prop|Cute cartoon cars inching bumper to bumper beside a slow-flowing syrup droplet."),
            ("Một hình ảnh giản dị", "variation|The child and learner both smile as the concept clicks into place instantly."),
            ("có sức thuyết phục hơn mười dòng định nghĩa trừu tượng.", "white_card|The simple traffic icon outweighs a stack of ten abstract textbooks on a balance scale."),
        ],
    ),
    (
        "Tờ giấy trắng và sự sáng rõ",
        "A bright thesis defense hall, confident presenter.",
        [
            ("Trước khi lên bục bảo vệ, hãy thử quy tắc tờ giấy trắng.", "full_scene|The presenter stands confidently before the committee, holding only a clean one-page outline with three clear bullet points."),
            ("Nếu tóm gọn được luận điểm bằng câu từ bình dị,", "variation|The presenter speaks calmly with open gestures, making direct eye contact with the evaluators."),
            ("bạn sẽ hoàn toàn tự tin.", "variation|Close view of the presenter smiling with composed, steady authority."),
            ("Đỉnh cao của nghiên cứu là làm cho điều phức tạp trở nên sáng rõ.", "variation|The committee members nod approvingly with pleased expressions at the clean presentation."),
            ("Hãy viết để người khác hiểu,", "variation|The audience listens with engaged attention, nodding along to each logical point."),
            ("đừng viết để chứng tỏ bản thân.", "white_card|Final full-frame title card in bold black marker: TRI THỨC THẬT SỰ LÀ SỰ SÁNG RÕ on clean ivory white."),
        ],
    ),
]


def build_topic() -> ResearchedTopic:
    scenes = build_scenes_from_story_rows(STORY)
    for idx, sc in enumerate(scenes, 1):
        sc.requirements = [f"R{idx:02d}"]
        if idx in (5, 6, 7, 8, 9):
            sc.source_ids = ["SRC01"]
        elif idx in (10, 11, 12):
            sc.source_ids = ["SRC02"]

    scenes[4].claim_facts = [
        ("Nhà tâm lý học Daniel Oppenheimer đã làm một thực nghiệm nổi tiếng.", "SRC01", "Dùng từ phức tạp làm giảm độ trôi chảy nhận thức.")
    ]
    scenes[11].claim_facts = [
        ("Biết tên một khái niệm rất khác với việc hiểu bản chất.", "SRC02", "Biết tên một khái niệm khác với hiểu bản chất.")
    ]

    return ResearchedTopic(
        topic="Kỹ Thuật Feynman & Cái Bẫy Thuật Ngữ Hàn Lâm",
        audience="Sinh viên và người tự học tại Việt Nam",
        goal="Giải mã hiệu ứng trôi chảy nhận thức và kỹ thuật dịch thuật Feynman giúp loại bỏ ngôn từ phòng vệ trong bài nghiên cứu.",
        video_type="research_explainer",
        aspect_ratio="16:9",
        format_profile="long_16x9",
        min_duration=200.0,
        max_duration=480.0,
        scenes=scenes,
        subtitles=False,
        voice="VietNarrator",
        speed=1.0,
        visual_pacing_profile="full_frame_v1",
        style=STYLE_DESCRIPTION,
        characters=[{
            "id": "CH01",
            "name": "Người học",
            "appearance": CAST_APPEARANCE,
            "outfit": DEFAULT_OUTFIT,
        }],
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _) in enumerate(STORY, 1)],
        sources=[
            {
                "id": "SRC01",
                "title": "Consequences of Erudite Vernacular Utilized Irrespective of Necessity",
                "reference": "Oppenheimer (2006), Applied Cognitive Psychology 20(2), 139–156.",
                "facts": ["Dùng từ phức tạp làm giảm độ trôi chảy nhận thức."],
            },
            {
                "id": "SRC02",
                "title": "Surely You Are Joking Mr Feynman",
                "reference": "Feynman (1985), W. W. Norton & Company.",
                "facts": ["Biết tên một khái niệm khác với hiểu bản chất."],
            },
        ],
        conversational_facts=True,
        packaging=PackagingSpec(
            youtube_title="Càng Dùng Từ Phức Tạp, Bạn Càng Bị Đánh Giá Thấp!",
            visual_hook="A balance scale: one side has heavy verbose dictionaries smoking away weightlessly, the other side has a single glowing crystal of clear insight tilting the scale.",
            text_overlay="BẪY THUẬT NGỮ",
            contrast_pair="Thuật ngữ phòng vệ vs. Tri thức sáng rõ",
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", "--output-dir", dest="out", type=Path, default=SYS_DIR / "blueprints" / "feynman-jargon-trap-16x9")
    args = parser.parse_args()

    topic = build_topic()
    out_dir = args.out
    result = write_production_package(out_dir, topic)

    # Generate matching draft outline
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

    # Copy generated content.json to draft/content.json if not present
    if (out_dir / "content.json").is_file():
        (draft_dir / "content.json").write_text((out_dir / "content.json").read_text(encoding="utf-8"), encoding="utf-8")

    print(json.dumps({
        "output_dir": str(out_dir),
        "valid_contracts": result["valid_contracts"],
        "contract_errors": result["contract_errors"],
        "packaging_warnings": result["packaging_warnings"],
        "cadence_status": result["cadence_report"]["status"],
        "cadence_warnings": result["cadence_report"]["warnings_count"],
        "total_duration": result["cadence_report"]["total_duration"],
        "total_actual_syllables": result["cadence_report"]["total_actual_syllables"],
    }, ensure_ascii=False, indent=2))

    if not result["valid_contracts"] or result["cadence_report"]["status"] != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
