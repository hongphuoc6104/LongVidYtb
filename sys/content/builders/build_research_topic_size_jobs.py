#!/usr/bin/env python3
"""Build production-ready packages for Research Topic Size / Onion Peeling Technique.

Pillar: "Hướng Dẫn Nghiên Cứu Khoa Học Cho Người Mới" (research_guide, tier_1_broad)
Core Topic: "Đừng Chọn Đề Tài NCKH Quá Lớn (Nghệ Thuật Bóp Nhỏ Đề Tài Bằng Kỹ Thuật Gọt Củ Hành)"
Academic foundations:
  - Wayne C. Booth, Gregory G. Colomb & Joseph M. Williams (2008). The Craft of Research.
  - John W. Creswell (2014). Research Design: Qualitative, Quantitative, and Mixed Methods Approaches.
  - Derek J. de Solla Price (1963). Little Science, Big Science.

Formats:
  - research-topic-size-16x9: 16 scenes, 8-part narrative arc landscape explainer (>= 1,800 syl)
  - research-topic-size-9x16: 6 scenes, 60-second vertical mobile short explainer (45-65s)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List

ROOT_DIR = Path(__file__).resolve().parents[3]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content.research_story_architect import (
    CAST_APPEARANCE,
    DEFAULT_OUTFIT,
    HumanEditorialSpec,
    PackagingSpec,
    ResearchedScene,
    ResearchedTopic,
    build_scenes_from_story_rows,
    write_production_package,
)
from content.research_story_architect import (
    CURRENT_STYLE_DESCRIPTION as STYLE_DESCRIPTION,
)

CHANNEL_PILLAR_RESEARCH_GUIDE = "Hướng Dẫn Nghiên Cứu Khoa Học Cho Người Mới"

# ---------------------------------------------------------------------------
# STORY 16:9 (16 Scenes — 8-Part Layered Narrative Arc Explainer Blueprint)
# ---------------------------------------------------------------------------
STORY_16X9: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    # STAGE 1: hook (Scenes 1-2)
    (
        "Cú tát đề tài vĩ mô",
        "Solid warm cream canvas (#F8F0DC).",
        "narrative_warm",
        "gentle_lived_friction",
        "hook",
        [
            ("Tên đề tài nghiên cứu quá rộng sẽ bị thầy cô gạch ngay.", "full_scene:CH01|Stickman staggers under an oversized round grey rock prop with shaking knees on flat warm cream canvas."),
            ("Khi mới bắt đầu làm nghiên cứu, ai cũng thích những chuyện đao to búa lớn.", "variation:CH01|Stickman looks up at the heavy grey rock with wide hopeful eyes."),
            ("Bạn muốn tìm giải pháp cho cả nền kinh tế, hay cứu vãn môi trường toàn cầu.", "concept_metaphor:none|A simple doodle globe outline marked with a large question mark on cream ground, seventy percent negative space."),
            ("Nghe thì rất oách, nhưng thực tế là bạn đang tự đào hố chôn mình.", "variation:CH01|Stickman drops hands to knees breathing heavily beside the stationary rock outline."),
            ("Càng ôm đồm vĩ mô, bạn càng nhanh rơi vào ngõ cụt và kiệt sức.", "concept_metaphor:none|A simple doodle balance scale tipping sharply under a heavy dark block on cream canvas, eighty percent negative space."),
            ("Chỉ sau vài ngày, bạn sẽ hoàn toàn lạc lối trong mớ bòng bong dữ liệu.", "full_scene:CH01|Stickman stands in open space looking down at empty palms with puzzled expression."),
            ("Một câu hỏi quá rộng sẽ nuốt chửng toàn bộ thời gian quý báu của bạn.", "visual_diagram:none|A wide black circle outline expanding outward across the cream field with thin radiating arrows, seventy percent negative space."),
            ("Bạn không có đủ kinh phí hay nhân lực để chứng minh điều to lớn đó.", "variation:CH01|Stickman shakes head with gentle sigh in open cream space."),
            ("Bộ não của bạn sẽ bị quá tải trước biển thông tin khổng lồ.", "concept_metaphor:none|A simple doodle outline of an open notebook with empty blank pages on flat cream canvas, eighty percent negative space."),
            ("Bí quyết của nhà nghiên cứu giỏi là làm ngược lại hoàn toàn.", "still_life:none|A single small black pebble doodle resting centered on flat cream ground with wide open breathing space."),
        ],
    ),
    (
        "Ảo tưởng người hùng ban đầu",
        "Clean pure white background (#FFFFFF).",
        "narrative_warm",
        "gentle_lived_friction",
        "hook",
        [
            ("Lần đầu làm nghiên cứu, ai cũng thích những tên đề tài thật dài.", "full_scene:CH01|Stickman unrolls a long paper scroll reaching down to the floor, displaying a confident proud grin."),
            ("Càng nhiều từ chuyên môn, bạn càng thấy bài viết của mình quan trọng.", "variation:CH01|Stickman holds up the long scroll pointing proudly at dense rows of marker text lines."),
            ("Đó là một ảo giác rất ngọt ngào.", "concept_metaphor:none|A simple doodle crown outline floating above an abstract question mark on pure white ground, eighty percent negative space."),
            ("Bạn tưởng mình đang chuẩn bị tạo ra một cuộc cách mạng.", "full_scene:CH01|Stickman stands tall with chest out and hands on hips in open white space."),
            ("Nhưng trong mắt hội đồng, đó chỉ là sự ngây thơ.", "visual_diagram:none|A single straight horizontal black line separating a tiny star icon from a solid black cross mark, eighty percent open space."),
            ("Họ không cần một bài diễn văn truyền cảm hứng.", "concept_metaphor:none|A simple doodle megaphone outline with a thin black diagonal strike line across it on clean white field."),
            ("Họ cần một phép đo cụ thể mà bạn có thể làm được.", "full_scene:CH01|Stickman holds a small wooden ruler upright between both palms on solid white canvas."),
            ("Một câu hỏi hẹp và sâu luôn đánh bại một ý tưởng mênh mông.", "variation:CH01|Stickman taps the ruler gently against palm with confident expression."),
            ("Tính khả thi mới là thước đo thực sự của bản đề cương.", "concept_metaphor:none|A simple doodle caliper measuring a tiny cylinder on pure white field, eighty percent negative space."),
            ("Không thể đo lường thì không thể nghiên cứu.", "still_life:none|A single minimalist black ruler doodle resting flat on solid white ground with wide open breathing space."),
        ],
    ),

    # STAGE 2: lead_in (Scenes 3-4)
    (
        "Cú va đập vòng đề cương",
        "Solid ivory neutral field (#F8F0DC).",
        "narrative_warm",
        "demystifying_truth",
        "lead_in",
        [
            ("Nhưng chỉ sau một tuần, thực tế sẽ tạt cho bạn một gáo nước lạnh.", "full_scene:CH01|Stickman stands holding the paper scroll as a bold red marker stroke slashes across the text."),
            ("Giáo viên hướng dẫn sẽ gạch bỏ ngay từ vòng đề cương.", "variation:CH01|Stickman scratches bald head with puzzled eyebrows looking down at the red strike mark."),
            ("Lời phê thường rất ngắn: Quá rộng, không thể thực hiện.", "white_card:none|A clean white card displaying simple hand-lettered Vietnamese words 'QUÁ RỘNG' in bold black ink, seventy percent negative space."),
            ("Cảm giác lúc đó giống như bị dội một gáo nước lạnh.", "full_scene:CH01|Stickman droops shoulders looking down at the floor with slight comic sweat drop."),
            ("Bạn bực bội vì nghĩ thầy cô không hiểu tham vọng của mình.", "variation:CH01|Stickman folds arms across blue shirt with slight pout looking sideways."),
            ("Nhưng thầy cô đã thấy trước ngõ cụt mà bạn chưa nhìn ra.", "concept_metaphor:none|A simple doodle pathway terminating at a solid black wall on ivory canvas, seventy-five percent negative space."),
            ("Một đề tài vĩ mô sẽ dẫn bạn vào ngõ cụt không lối thoát.", "visual_diagram:none|Two converging black lines pinching down to a closed point with zero exit on ivory background."),
            ("Càng cố chấp bảo vệ, bạn càng lún sâu vào bế tắc.", "variation:CH01|Stickman shakes head gently with reflective calm expression."),
            ("Nhận ra giới hạn sớm sẽ giúp bạn tiết kiệm nhiều tháng trời.", "concept_metaphor:none|A simple doodle clock icon with hands pointing upward on flat ivory ground, eighty percent negative space."),
            ("Biết dừng lại lúc này chính là điều may mắn.", "still_life:none|A single clean question mark doodle resting flat on solid ivory field with eighty percent breathing space."),
        ],
    ),
    (
        "Bế tắc vì biển dữ liệu",
        "Pure stark white field (#FFFFFF).",
        "reflective_slow",
        "demystifying_truth",
        "lead_in",
        [
            ("Đề tài càng lớn, bạn càng không biết phải bắt đầu từ đâu.", "full_scene:CH01|Stickman sits flat on the white canvas facing a giant black question mark prop."),
            ("Bạn cần khảo sát mười nghìn người để lấy mẫu.", "concept_metaphor:none|A sprawling cluster of tiny dot silhouettes shrinking into infinity on white ground, eighty percent negative space."),
            ("Nhưng bạn chỉ có đúng hai bàn tay trắng.", "macro_prop:none|Two open empty palm outlines drawn in raw black marker line centered on stark white field with wide negative space."),
            ("Bạn không có kinh phí để đi khắp các tỉnh thành.", "concept_metaphor:none|A simple doodle empty wallet outline with zero coins resting on stark white canvas, seventy percent negative space."),
            ("Bạn cũng không có quyền tiếp cận các cơ sở dữ liệu kín.", "concept_metaphor:none|A simple doodle padlock icon securing a small blank box on white background, seventy-five percent negative space."),
            ("Thời gian làm bài tốt nghiệp chỉ vỏn vẹn ba tháng.", "visual_diagram:none|A simple horizontal timeline bar divided into three equal segments marked 'THÁNG 1', 'THÁNG 2', 'THÁNG 3' in neat lettering."),
            ("Biển dữ liệu mênh mông sẽ nhấn chìm bạn trước ngày nộp bài.", "full_scene:CH01|Stickman raises both hands trying to keep balance amid open white space."),
            ("Mỗi ngày trôi qua trong hoang mang và lo âu tột cùng.", "variation:CH01|Stickman puts hand to forehead with weary comic sigh in open white field."),
            ("Sự bất lực xuất hiện khi bạn gánh vác việc quá sức mình.", "concept_metaphor:none|A simple doodle broken line between a tiny anchor outline and a floating leaf on white canvas, eighty percent negative space."),
            ("Đừng tự biến mình thành nạn nhân của sự tham lam.", "still_life:none|A single small black pebble doodle resting in center of vast white canvas with eighty percent negative space."),
        ],
    ),

    # STAGE 3: problem (Scenes 5-6)
    (
        "Bẫy phát minh lại bánh xe",
        "Solid soft cream canvas (#F8F0DC).",
        "analytical_crisp",
        "mechanistic_dissection",
        "problem",
        [
            ("Nhiều người tưởng nghiên cứu là phải phát minh ra điều chưa ai từng nghĩ.", "full_scene:CH01|Stickman bends over a large circular wheel outline drawn on cream ground, trying to redraw the exact same circle."),
            ("Họ sợ đề tài của mình bị chê là tầm thường.", "variation:CH01|Stickman pauses with marker pen in hand, looking anxious and hesitant."),
            ("Đây là cái bẫy tâm lý phổ biến nhất của người mới.", "concept_metaphor:none|A simple doodle circular arrow chasing its own tail in a closed loop on soft cream background, seventy percent open space."),
            ("Khoa học thực sự không vận hành theo cách giật gân như vậy.", "full_scene:CH01|Stickman stands upright and shakes head gently with calm enlightened expression."),
            ("Các nhà bác học cũng bắt đầu từ những phép thử rất nhỏ.", "concept_metaphor:none|A tiny test tube outline drawn with clean black marker beside a small ruler on cream field, eighty percent negative space."),
            ("Phát minh lại bánh xe chỉ làm bạn mất thời gian vô ích.", "visual_diagram:none|A circular wheel icon crossed out with a neat diagonal stroke beside a straight onward arrow on cream canvas."),
            ("Bạn không cần chứng minh lại những định luật đã có từ lâu.", "variation:CH01|Stickman folds arms calmly, looking at the crossed-out wheel."),
            ("Giá trị của một nghiên cứu nằm ở tính khả thi.", "full_scene:CH01|Stickman taps index finger against the side of head with knowing smile."),
            ("Một phát hiện nhỏ nhưng chính xác vẫn có chỗ đứng riêng.", "concept_metaphor:none|A simple doodle checkmark inside a small clean circle on soft cream field, eighty percent negative space."),
            ("Làm được trọn vẹn một việc nhỏ tốt hơn bỏ dở việc lớn.", "white_card:none|A minimalist white card with two unequal boxes: a small solid black box marked 'XONG' and a huge dashed box marked 'BỎ DỞ'."),
        ],
    ),
    (
        "Bức tường tri thức nhân loại",
        "Solid warm cream canvas (#F8F0DC).",
        "reflective_slow",
        "mechanistic_dissection",
        "problem",
        [
            ("Thực ra, tri thức nhân loại giống như một bức tường đã xây rất cao.", "full_scene:CH01|Stickman stands gazing up at a tall wall of grey bricks stretching upward on warm cream canvas."),
            ("Hàng triệu nhà khoa học đi trước đã đóng góp từng viên gạch.", "concept_metaphor:none|A neat grid of stacked grey brick outlines forming a sturdy wall on cream field, seventy percent negative space."),
            ("Bức tường ấy vững chắc nhờ sự tích lũy qua hàng trăm năm.", "variation:CH01|Stickman gently touches the smooth surface of the brick wall with respectful curiosity."),
            ("Không ai một mình xây nên cả tòa lâu đài đồ sộ.", "concept_metaphor:none|A massive castle silhouette crossed out with thin dashed lines on cream canvas, eighty percent negative space."),
            ("Nhìn kỹ vào bức tường, bạn sẽ thấy những lỗ khuyết rất nhỏ.", "full_scene:CH01|Stickman leans forward pointing index finger at a single missing brick slot in the wall."),
            ("Đó là những chỗ mà người đi trước chưa kịp kiểm tra.", "macro_prop:none|Close-up outline of a rectangular empty brick slot in the masonry wall on cream field, eighty percent negative space."),
            ("Có thể họ chưa kịp đo đạc ở một đối tượng đặc thù.", "variation:CH01|Stickman inspects the slot edges with careful focused eyes."),
            ("Đó chính là nơi đề tài của bạn nên hướng vào.", "full_scene:CH01|Stickman steps back with eyes shining, gesturing toward the empty slot."),
            ("Bạn chỉ cần bổ sung đúng khoảng trống bị bỏ quên ấy.", "concept_metaphor:none|A small clean rectangular patch hovering right above the missing brick slot on cream canvas."),
            ("Một khe hở nhỏ cũng đủ tạo nên một công trình giá trị.", "still_life:none|A single clean brick silhouette resting on flat cream ground with wide open breathing space."),
        ],
    ),

    # STAGE 4: causal_mechanism (Scenes 7-8)
    (
        "Viên gạch nhỏ của bạn",
        "Clean pure white background (#FFFFFF).",
        "analytical_crisp",
        "scientific_evidence",
        "causal_mechanism",
        [
            ("Việc của bạn không phải xây tường mới, mà là đặt thêm một viên gạch.", "full_scene:CH01|Stickman holds a small solid blue brick (#3B82C4) with both hands, lifting it gently toward the wall slot."),
            ("Một viên gạch nhỏ nhưng vừa khít với chỗ trống trên tường.", "variation:CH01|Stickman carefully slides the blue brick into the empty masonry slot on the wall."),
            ("Viên gạch vừa vặn sẽ làm bức tường vững chắc hơn.", "visual_diagram:none|A wall section diagram showing the blue brick perfectly aligned with surrounding grey bricks, arrows pointing inward."),
            ("Trong giới khoa học, người ta gọi đó là đóng góp tích lũy.", "concept_metaphor:none|A neat upward staircase formed by small brick steps on white field, seventy-five percent negative space."),
            ("Không ai chê một viên gạch là quá nhỏ bé.", "full_scene:CH01|Stickman stands back dusting hands together with satisfied comic expression."),
            ("Họ chỉ chê những viên gạch nứt vỡ hoặc đặt sai vị trí.", "concept_metaphor:none|A cracked crooked brick shape beside a neat solid brick on white canvas, eighty percent negative space."),
            ("Nếu bạn gọt đề tài vừa sức, dữ liệu của bạn sẽ rất chắc.", "variation:CH01|Stickman gives a firm nodding gesture beside the blue brick."),
            ("Một câu hỏi nghiên cứu hẹp giúp viên gạch của bạn rắn chắc.", "full_scene:CH01|Stickman knocks gently on the newly placed brick with knuckles, confirming solid bond."),
            ("Kết quả bạn đưa ra sẽ không ai có thể bắt bẻ được.", "visual_diagram:none|A clean checkmark symbol stamped on the center of the blue brick outline on white ground."),
            ("Bạn hoàn toàn có thể tự hào về phần việc nhỏ ấy.", "still_life:none|A neat blue brick icon centered on solid white canvas with generous eighty percent negative space."),
        ],
    ),
    (
        "Quy luật bớt tham để sống",
        "Solid ivory neutral field (#F8F0DC).",
        "analytical_crisp",
        "scientific_evidence",
        "causal_mechanism",
        [
            ("Bớt tham lại, bài nghiên cứu của bạn mới có đường sống.", "full_scene:CH01|Stickman drops the giant grey rock onto the floor and picks up a tiny smooth pebble on open palm."),
            ("Khi thu nhỏ phạm vi, bạn kiểm soát được toàn bộ biến số.", "variation:CH01|Stickman holds the tiny pebble up to eye level, examining its clean edges closely."),
            ("Bạn biết rõ mình cần thu thập bao nhiêu mẫu khảo sát.", "visual_diagram:none|A neat checklist box showing a clean green checkmark beside a targeted number 'N = 100' on ivory field."),
            ("Bạn biết rõ công cụ nào đo lường chính xác nhất.", "concept_metaphor:none|A simple doodle calibrated caliper measuring a small cylinder on ivory background, seventy-five percent negative space."),
            ("Dữ liệu thu về sẽ sạch sẽ và không bị nhiễu.", "visual_diagram:none|Two parallel straight black lines running smoothly without stray squiggles on ivory ground, eighty percent open space."),
            ("Bạn sẽ không bị ngợp giữa hàng tá tài liệu mâu thuẫn nhau.", "variation:CH01|Stickman stands in calm uncluttered stance looking forward."),
            ("Thầy cô chấm bài sẽ nhìn thấy ngay phương pháp mạch lạc.", "full_scene:CH01|Stickman gestures confidently toward a clean two-step diagram on ivory canvas."),
            ("Một bài báo gọn gàng luôn được đánh giá cao hơn bản thảo lan man.", "white_card:none|A comparison card showing a slender crisp manuscript with high grade mark beside a bloated untidy stack."),
            ("Sự tập trung chính là vũ khí mạnh nhất của người nghiên cứu.", "concept_metaphor:none|A sharp focused beam icon highlighting a single point on ivory field, eighty percent negative space."),
            ("Bớt tham không phải lười, mà là sự khôn ngoan.", "still_life:none|A single polished black pebble resting flat on ivory ground with eighty percent breathing space."),
        ],
    ),

    # STAGE 5: explanation (Scenes 9-10)
    (
        "Ba vòng tròn gọt củ hành",
        "Pure stark white field (#FFFFFF).",
        "analytical_crisp",
        "demystifying_truth",
        "explanation",
        [
            ("Để gọt một đề tài to thành nhỏ, hãy dùng quy tắc ba vòng tròn.", "full_scene:CH01|Stickman points index finger toward three concentric black circular outlines drawn on white canvas."),
            ("Kỹ thuật này giống hệt như bóc từng lớp vỏ của củ hành tây.", "concept_metaphor:none|A simple doodle onion outline with three distinct layered rings drawn with wobbly black marker lines, seventy percent negative space."),
            ("Mỗi lần bóc một lớp, bài toán lại hiện ra rõ ràng hơn.", "visual_diagram:none|Three concentric circles labeled with hand-drawn marker text: outer 'LĨNH VỰC', middle 'ĐỐI TƯỢNG', inner 'HÀNH VI'."),
            ("Vòng tròn ngoài cùng là lĩnh vực chung rất rộng.", "full_scene:CH01|Stickman rests hand on the outer large circle rim looking attentive."),
            ("Vòng tròn ở giữa là nhóm người cụ thể bạn tiếp cận được.", "variation:CH01|Stickman steps inside the middle circle outline, gesturing toward the interior."),
            ("Vòng tròn trong cùng là một hành vi đo đạc chính xác.", "full_scene:CH01|Stickman stands in the very center circle, pointing straight down at feet."),
            ("Bằng cách này, mọi đề tài khổng lồ đều bị thu nhỏ.", "visual_diagram:none|A straight inward arrow pointing from outer ring to the tiny core center on white background."),
            ("Bạn sẽ không còn cảm giác mơ hồ hay mông lung nữa.", "variation:CH01|Stickman smiles with clarity, looking at the focused center dot."),
            ("Mỗi bước đi đều có đích đến rõ ràng trước mắt.", "concept_metaphor:none|A straight line connecting two distinct circular nodes on pure white field, eighty percent open space."),
            ("Hãy cùng đi qua từng lớp vỏ ngay bây giờ.", "full_scene:CH01|Stickman waves hand invitingly toward the diagram with friendly posture."),
        ],
    ),
    (
        "Vòng một: Thu hẹp đối tượng",
        "Solid soft cream canvas (#F8F0DC).",
        "analytical_crisp",
        "demystifying_truth",
        "explanation",
        [
            ("Thay vì nghiên cứu giới trẻ cả nước, hãy chọn sinh viên trường bạn.", "full_scene:CH01|Stickman crosses out a huge map outline and points firmly to a small student icon wearing a mortarboard."),
            ("Nhiều bạn ghi trong đề cương: Khảo sát thanh niên toàn quốc.", "white_card:none|A white card with crossed-out text 'THANH NIÊN TOÀN QUỐC' in red ink beside green checkmark text 'SINH VIÊN NĂM NHẤT TRƯỜNG TÔI'."),
            ("Nhưng bạn lấy đâu ra tiền để đi từ Bắc vào Nam?", "full_scene:CH01|Stickman spreads both arms with questioning comic shrug on solid cream field."),
            ("Thu hẹp đối tượng không hề làm giảm giá trị bài viết.", "concept_metaphor:none|A simple doodle target circle with an arrow striking right at the bullseye on cream canvas, seventy-five percent negative space."),
            ("Khoa học cần mẫu khảo sát thật và có thể xác minh.", "visual_diagram:none|A neat data table diagram showing verified student IDs and survey timestamps on cream background."),
            ("Sinh viên trong ký túc xá là nguồn dữ liệu ngay trước mắt bạn.", "full_scene:CH01|Stickman points index finger toward a simple door outline with sign 'KÝ TÚC XÁ'."),
            ("Bạn có thể gặp họ hàng ngày để hỏi sâu hơn.", "variation:CH01|Stickman holds a small clipboard taking notes with thoughtful friendly expression."),
            ("Bạn dễ dàng kiểm chứng lại nếu có dữ liệu bất thường.", "concept_metaphor:none|A simple magnifying glass outline focusing on a single verified table row on cream canvas."),
            ("Mẫu khảo sát gần gũi giúp bài nghiên cứu đáng tin cậy hơn.", "full_scene:CH01|Stickman nods with confidence holding the verified survey sheet."),
            ("Khả thi trong tầm tay chính là tiêu chuẩn vàng.", "still_life:none|A single small clipboard icon drawn in crisp black marker resting on cream canvas with eighty percent negative space."),
        ],
    ),

    # STAGE 6: counter_argument (Scenes 11-12)
    (
        "Vòng hai: Khóa chặt hành vi",
        "Solid warm cream canvas (#F8F0DC).",
        "analytical_crisp",
        "counter_intuitive_shift",
        "counter_argument",
        [
            ("Thay vì sức khỏe tinh thần, hãy đo giờ đi ngủ và thời gian lướt mạng.", "full_scene:CH01|Stickman points from an abstract fuzzy cloud symbol to a clear clock icon showing 23:00 beside a smartphone outline."),
            ("Khái niệm sức khỏe tinh thần quá trừu tượng và khó nắm bắt.", "concept_metaphor:none|A vague cloud outline marked with multiple question marks on cream field, seventy-five percent negative space."),
            ("Mỗi người hiểu từ này theo một nghĩa khác nhau.", "visual_diagram:none|Three diverged dashed arrows splitting from one word 'TINH THẦN' on cream canvas."),
            ("Nhưng giờ đi ngủ và số phút dùng điện thoại thì đo được ngay.", "full_scene:CH01|Stickman taps the side of a simple smartphone outline showing a clean screen timer."),
            ("Bạn chỉ cần chụp màn hình tính năng thời gian sử dụng.", "macro_prop:none|Close-up outline of a phone screen showing digital clock digits '23:30' with high contrast charcoal marker on cream background."),
            ("Con số khách quan không biết nói dối.", "visual_diagram:none|A clear bar chart with two solid columns labeled 'LƯỚT MẠNG' and 'NGỦ MUỘN' on cream canvas."),
            ("Bạn không cần đoán mò cảm xúc của đối tượng nữa.", "variation:CH01|Stickman smiles with relief looking at the objective bar chart."),
            ("Khóa chặt hành vi giúp loại bỏ các tranh cãi mơ hồ.", "full_scene:CH01|Stickman gives a solid thumbs-up gesture beside the clean bar chart."),
            ("Mọi kết luận của bạn đều dựa trên con số thực tế.", "concept_metaphor:none|A simple digital counter icon ticking up to a solid confirmed sum on cream field."),
            ("Đó là cách biến ý tưởng chung thành biến số đo được.", "still_life:none|A simple doodle hourglass outline with sand settled neatly in the lower bulb on cream ground."),
        ],
    ),
    (
        "Vòng ba: Thước đo thực tế",
        "Clean pure white background (#FFFFFF).",
        "analytical_crisp",
        "counter_intuitive_shift",
        "counter_argument",
        [
            ("Bài toán bây giờ vừa vặn trong tay, làm xong gọn gàng trong ba tháng.", "full_scene:CH01|Stickman holds a single neat sheet of paper with a crisp green checkmark in the center."),
            ("Một số người sẽ lo rằng đề tài này trông quá giản dị.", "variation:CH01|Stickman tilts head with slight thoughtful eyebrow raise, looking at the neat paper."),
            ("Họ hỏi: Liệu một đề tài nhỏ như vậy có đủ để tốt nghiệp không?", "full_scene:CH01|Stickman points index finger forward with confident calm smile."),
            ("Câu trả lời là hoàn toàn đủ, thậm chí còn đạt điểm cao.", "white_card:none|A clean white card displaying a bold grade 'A' stamped in crisp black marker on white field, seventy-five percent open space."),
            ("Hội đồng luôn đánh giá cao số liệu trung thực và chặt chẽ.", "visual_diagram:none|A neat flowchart connecting 'CÂU HỎI HẸP' -> 'SỐ LIỆU THẬT' -> 'KẾT LUẬN CHẮC' with clean black arrows."),
            ("Họ không cần những lời hứa to tát nhưng vô căn cứ.", "concept_metaphor:none|A hollow balloon popping with a tiny burst line on white canvas, eighty percent negative space."),
            ("Một nghiên cứu trung thực ở góc nhỏ giá trị hơn ngàn lời sáo rỗng.", "variation:CH01|Stickman stands tall with calm professional posture."),
            ("Bạn chứng minh được một mắt xích nhỏ bằng chứng cứ thép.", "full_scene:CH01|Stickman presses both hands together with solid certainty on white ground."),
            ("Thầy cô sẽ thấy bạn hiểu rất sâu phương pháp làm việc.", "concept_metaphor:none|A neat solid star icon resting beside the paper draft on white canvas."),
            ("Đó mới là tinh thần chân chính của khoa học thực nghiệm.", "still_life:none|A small iron link doodle drawn with thick black marker resting centered on white canvas with eighty percent negative space."),
        ],
    ),

    # STAGE 7: takeaway (Scenes 13-14)
    (
        "Bước một: Gọt sạch chữ thừa",
        "Solid ivory neutral field (#F8F0DC).",
        "analytical_crisp",
        "empowering_resolution",
        "takeaway",
        [
            ("Bước một: Viết tên đề tài ra giấy, gạch hết những từ đao to búa lớn.", "full_scene:CH01|Stickman stands beside a large text line on ivory canvas, striking red marker lines through long flowery words."),
            ("Hãy bỏ ngay những từ như: Toàn diện, giải pháp vĩ mô, hay cứu cánh.", "white_card:none|A white card showing words 'TOÀN DIỆN', 'VĨ MÔ', 'CỨU CÁNH' each crossed out with clean black strikethrough strokes."),
            ("Những từ đó chỉ làm rối mắt và che giấu sự mơ hồ.", "concept_metaphor:none|A simple doodle magnifying glass clearing away a patch of wavy scribble lines on ivory field."),
            ("Tên đề tài chuẩn cần ngắn gọn, rõ ràng và mộc mạc.", "full_scene:CH01|Stickman writes a short crisp four-word title on ivory canvas with black marker."),
            ("Đọc lên là người nghe hiểu ngay bạn đang làm gì.", "variation:CH01|Stickman steps back with hands on hips, nodding in approval at the short title."),
            ("Không cần dùng từ hoa mỹ để chứng tỏ mình thông minh.", "visual_diagram:none|A comparison of two text lines: a tangled twenty-word sentence vs a clean five-word title."),
            ("Từ ngữ càng đơn giản thì ý tưởng càng sáng rõ.", "variation:CH01|Stickman points index finger to the clean title with clear smile."),
            ("Sự rõ ràng là đỉnh cao của sự thông suốt.", "full_scene:CH01|Stickman points index finger directly to the short clean title line."),
            ("Bạn giúp người đọc nắm bắt vấn đề chỉ sau ba giây.", "concept_metaphor:none|A simple doodle digital timer showing '00:03' on ivory ground, eighty percent open space."),
            ("Gọt chữ thừa chính là bước đầu tiên để cứu đề tài.", "still_life:none|A single black pencil doodle resting flat beside a clean eraser mark on ivory background."),
        ],
    ),
    (
        "Bước hai: Khung ba biến số",
        "Pure stark white field (#FFFFFF).",
        "analytical_crisp",
        "empowering_resolution",
        "takeaway",
        [
            ("Bước hai: Chỉ giữ lại đúng một nhóm người, một thói quen và một thước đo.", "full_scene:CH01|Stickman points to three aligned square boxes drawn with bold black marker on white field."),
            ("Khung này giúp bạn không bao giờ bị lạc lối.", "visual_diagram:none|Three neat squares labeled in simple uppercase marker: 'AI?' -> 'LÀM GÌ?' -> 'ĐO BẰNG GÌ?'."),
            ("Ô thứ nhất: Sinh viên năm nhất trường bạn.", "full_scene:CH01|Stickman taps the first box with hand, a student icon appears inside."),
            ("Ô thứ hai: Thói quen lướt điện thoại sau mười một giờ đêm.", "variation:CH01|Stickman points to the second box, a phone and clock icon appear inside."),
            ("Ô thứ ba: Điểm số trung bình môn của học kỳ vừa rồi.", "full_scene:CH01|Stickman points to the third box, a grade sheet icon appears inside."),
            ("Ba mảnh ghép này khớp lại thành một câu hỏi hoàn chỉnh.", "visual_diagram:none|Three boxes connecting together with horizontal line brackets on flat white field."),
            ("Bạn dễ dàng giải thích đề tài cho bất kỳ ai nghe.", "variation:CH01|Stickman smiles with open friendly posture on white ground."),
            ("Bạn có thấy mọi thứ trở nên cực kỳ dễ thở không?", "full_scene:CH01|Stickman smiles warmly with open arms in open white space."),
            ("Bạn biết chính xác ngày mai mình cần phải làm gì.", "concept_metaphor:none|A simple doodle sunrise icon drawn with three minimalist black lines on white canvas."),
            ("Đây chính là công thức giúp hàng nghìn sinh viên qua môn.", "still_life:none|Three neat black square outline frames sitting side by side on white canvas with seventy-five percent negative space."),
        ],
    ),

    # STAGE 8: closing (Scenes 15-16)
    (
        "Bước ba: Thử thách hai mươi tư giờ",
        "Solid soft cream canvas (#F8F0DC).",
        "reflective_slow",
        "philosophical_closure",
        "closing",
        [
            ("Bước ba: Lên mạng tìm xem có ai từng đo việc này ở nước khác chưa.", "full_scene:CH01|Stickman holds a small magnifying glass looking toward a clean document outline on cream field."),
            ("Chắc chắn đã có người từng làm một nghiên cứu tương tự.", "concept_metaphor:none|A neat document stack outline with a small globe icon in the corner on cream canvas, eighty percent negative space."),
            ("Đừng hoảng sợ khi thấy người ta đã làm trước mình.", "full_scene:CH01|Stickman shakes head gently with calm confident expression."),
            ("Ngược lại, đó là một tin rất đáng mừng.", "variation:CH01|Stickman smiles and points index finger upward with cheerful enthusiasm."),
            ("Bạn có thể mượn ngay thang đo chuẩn mà họ đã kiểm định.", "visual_diagram:none|A straight horizontal arrow transferring a questionnaire checklist from one page outline to another."),
            ("Bạn không phải mất công nghĩ ra bảng hỏi từ đầu.", "variation:CH01|Stickman gives a relieved smile holding the questionnaire sheet."),
            ("Việc của bạn chỉ là lặp lại phép đo đó tại Việt Nam.", "full_scene:CH01|Stickman holds up the adapted questionnaire with confident stance on cream canvas."),
            ("Đó hoàn toàn là một đóng góp học thuật hợp lệ.", "concept_metaphor:none|A clean stamp imprint showing 'HỢP LỆ' in solid black ink beside the questionnaire on cream ground."),
            ("Hội đồng sẽ đánh giá cao sự am hiểu tài liệu của bạn.", "visual_diagram:none|A simple upward green trend line beside the stamped document on cream canvas."),
            ("Bạn tiết kiệm được ít nhất hai tháng mày mò vô ích.", "still_life:none|A simple doodle calendar outline with pages flipping forward quickly on soft cream canvas."),
        ],
    ),
    (
        "Khép vòng lặp và thông điệp cốt lõi",
        "Solid warm cream canvas (#F8F0DC).",
        "reflective_slow",
        "philosophical_closure",
        "closing",
        [
            ("Nghiên cứu giỏi không phải làm việc lớn, mà là giải quyết dứt điểm một việc nhỏ.", "full_scene:CH01|Stickman stands tall and calm in center of canvas, holding the small blue brick (#3B82C4) high with steady hand."),
            ("Đừng cố giải cứu thế giới bằng một bản đề cương ba mươi trang sáo rỗng.", "variation:CH01|Stickman looks directly forward with warm reassuring smile on flat warm cream ground."),
            ("Hãy bắt đầu bằng một câu hỏi cụ thể mà bạn đếm được bằng tay.", "macro_prop:none|A single open palm outline holding a small bright pebble with calm breathing room, eighty percent negative space."),
            ("Khi bóp nhỏ đề tài, áp lực biến mất và con đường phía trước sẽ sáng tỏ.", "concept_metaphor:none|A single straight clean path stretching toward the horizon on warm cream field with seventy-five percent open space."),
            ("Bạn sẽ hoàn thành khóa luận đúng hạn mà không phải thức trắng kiệt sức.", "full_scene:CH01|Stickman smiles warmly with hands relaxed at sides in wide open cream space."),
            ("Khoa học thực sự là một hành trình từng bước giản dị và vững chắc.", "visual_diagram:none|A neat horizontal three-step milestone progression connected by dashed arrows across the canvas."),
            ("Nếu những chia sẻ này giúp bạn thấy nhẹ nhõm hơn, hãy thả một tim ủng hộ mình nhé.", "concept_metaphor:none|A simple warm apricot-peach doodle heart icon (#F2B88B) drawn with unpolished black marker ink beside stickman, eighty percent negative space."),
            ("Bấm theo dõi kênh để không bỏ lỡ những bài gỡ rối nghiên cứu tiếp theo.", "full_scene:CH01|Stickman points index finger with friendly warm smile toward a minimalist notification bell icon on warm cream canvas."),
            ("Chúc bạn sớm hoàn thành xuất sắc bản đề tài của riêng mình.", "variation:CH01|Stickman raises hand in a friendly gentle wave toward viewer on warm cream canvas."),
            ("Bớt tham lại, và bắt tay vào gọt giũa đề tài ngay hôm nay nhé.", "still_life:none|A single smooth blue brick icon resting peacefully centered on warm cream field with eighty percent negative space."),
        ],
    ),
]

# ---------------------------------------------------------------------------
# STORY 9:16 (6 Scenes — 60-Second Mobile Explainer Blueprint)
# ---------------------------------------------------------------------------
STORY_9X16: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    (
        "Cú tát đề tài vĩ mô",
        "Solid warm cream canvas (#F8F0DC).",
        "narrative_warm",
        "gentle_lived_friction",
        "hook",
        [
            ("Tên đề tài nghiên cứu quá rộng sẽ bị thầy cô gạch ngay.", "full_scene:CH01|Stickman staggers under an oversized round grey rock prop with shaking knees on flat warm cream canvas."),
            ("Muốn giải cứu thế giới, bạn đang tự hại mình.", "variation:CH01|Stickman looks up at the heavy grey rock with wide hopeful eyes on warm cream canvas."),
            ("Không tiền, không dữ liệu, bạn bế tắc ngay.", "concept_metaphor:none|A simple doodle globe outline marked with a large question mark on cream ground, seventy percent negative space."),
            ("Càng ôm đồm, bạn càng cầm chắc thất bại.", "full_scene:CH01|Stickman drops hands to knees breathing heavily beside the rock outline on cream canvas."),
        ],
    ),
    (
        "Cú gạch đề cương",
        "Clean pure white background (#FFFFFF).",
        "narrative_warm",
        "demystifying_truth",
        "lead_in",
        [
            ("Chỉ sau một tuần, giáo viên sẽ gạch bỏ ngay.", "full_scene:CH01|Stickman stands holding paper scroll as a bold red marker stroke slashes across the text on white canvas."),
            ("Lời phê ngắn gọn: Quá rộng, không thể làm.", "white_card:none|A clean white card displaying simple hand-lettered text 'QUÁ RỘNG' in bold black ink on white field, seventy percent negative space."),
            ("Bạn không có tiền bạc hay thời gian vô tận.", "variation:CH01|Stickman spreads both hands with questioning comic shrug on solid white field."),
            ("Biển dữ liệu lớn sẽ nhấn chìm bạn ngay.", "concept_metaphor:none|A sprawling cluster of tiny dot silhouettes shrinking into distance on white ground, eighty percent negative space."),
        ],
    ),
    (
        "Bức tường tri thức",
        "Solid soft cream canvas (#F8F0DC).",
        "analytical_crisp",
        "mechanistic_dissection",
        "problem",
        [
            ("Khoa học không cần bạn phát minh lại bánh xe.", "full_scene:CH01|Stickman crosses out a circular wheel outline with clean black marker on soft cream canvas."),
            ("Tri thức giống như một bức tường đã rất cao.", "concept_metaphor:none|A neat grid of stacked grey brick outlines forming a sturdy wall on cream field, seventy-five percent negative space."),
            ("Việc của bạn là đặt thêm một viên gạch nhỏ.", "full_scene:CH01|Stickman holds a small solid blue brick (#3B82C4) with both hands, lifting it gently toward wall slot."),
            ("Làm trọn việc nhỏ tốt hơn bỏ dở việc to.", "still_life:none|A single clean blue brick silhouette resting flat on soft cream ground with eighty percent breathing space."),
        ],
    ),
    (
        "Ba câu hỏi gọt củ hành",
        "Pure stark white field (#FFFFFF).",
        "analytical_crisp",
        "demystifying_truth",
        "explanation",
        [
            ("Hãy bóp nhỏ đề tài bằng ba câu hỏi then chốt.", "full_scene:CH01|Stickman points index finger toward three concentric black circular outlines drawn on white canvas."),
            ("Nghiên cứu ai? Hãy chọn sinh viên trường bạn.", "variation:CH01|Stickman steps inside middle circle outline, gesturing toward interior."),
            ("Đừng chọn thanh niên toàn quốc xa vời.", "concept_metaphor:none|A simple doodle student icon wearing a mortarboard centered on clean white canvas, seventy-five percent negative space."),
            ("Mẫu gần gũi giúp dữ liệu rất chắc chắn.", "visual_diagram:none|A straight inward arrow pointing from outer ring to the focused center dot on white background."),
        ],
    ),
    (
        "Khóa chặt hành vi và thước đo",
        "Solid ivory neutral field (#F8F0DC).",
        "analytical_crisp",
        "counter_intuitive_shift",
        "counter_argument",
        [
            ("Đo cái gì? Đổi khái niệm thành hành vi cụ thể.", "full_scene:CH01|Stickman points from a fuzzy cloud symbol to a clear clock icon showing 23:00 on ivory canvas."),
            ("Thay vì sức khỏe tinh thần, hãy đo giờ ngủ.", "concept_metaphor:none|A simple doodle clock icon beside a smartphone screen timer on ivory canvas, seventy-five percent negative space."),
            ("Số phút lướt điện thoại là thước đo khách quan.", "visual_diagram:none|A clear bar chart with two solid columns on ivory canvas, seventy percent open space."),
            ("Bài toán bây giờ làm gọn trong ba tháng.", "full_scene:CH01|Stickman holds a single neat sheet of paper with a crisp green checkmark on ivory field."),
        ],
    ),
    (
        "Bớt tham lại để thành công",
        "Clean serene white field (#FFFFFF).",
        "reflective_slow",
        "philosophical_closure",
        "closing",
        [
            ("Bớt tham lại, đề tài mới có cơ hội sống.", "full_scene:CH01|Stickman stands tall and calm in center of canvas, holding the small blue brick high with steady hand."),
            ("Làm trọn một việc nhỏ là đủ để qua môn.", "variation:CH01|Stickman smiles with peaceful clarity holding a completed paper draft marked with a neat checkmark."),
            ("Thả tim ủng hộ nếu thấy nhẹ nhõm hơn bạn nhé.", "concept_metaphor:none|A simple warm apricot-peach doodle heart icon (#F2B88B) drawn with unpolished black marker ink beside stickman, eighty percent negative space."),
            ("Bấm theo dõi để cùng gỡ rối đề tài tiếp theo.", "full_scene:CH01|Stickman raises hand in a friendly gentle wave toward viewer beside a minimalist doodle bell icon on clean white canvas."),
        ],
    ),
]


def build_sources() -> list[dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "The Craft of Research",
            "reference": "Wayne C. Booth, Gregory G. Colomb & Joseph M. Williams (2008). University of Chicago Press.",
            "facts": [
                "Một đề tài tốt bắt đầu từ một câu hỏi rất hẹp.",
                "Càng thu nhỏ phạm vi bạn càng dễ tìm thấy câu trả lời.",
                "Người mới thường nhầm giữa chủ đề lớn và câu hỏi nghiên cứu.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Research Design: Qualitative, Quantitative, and Mixed Methods Approaches",
            "reference": "John W. Creswell (2014). SAGE Publications.",
            "facts": [
                "Đề tài khả thi cần biến số đo lường được trong thực tế.",
                "Thu hẹp không gian giúp bạn thu thập dữ liệu chắc chắn hơn.",
                "Ba tháng chỉ đủ để giải quyết một mối liên hệ cụ thể.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Little Science, Big Science",
            "reference": "Derek J. de Solla Price (1963). Columbia University Press.",
            "facts": [
                "Khoa học tiến lên nhờ tích lũy từng viên gạch nhỏ.",
                "Không ai đòi hỏi một bài báo phải thay đổi cả thế giới.",
                "Giải quyết dứt điểm một điểm nhỏ có giá trị hơn ôm đồm việc lớn.",
            ],
        },
    ]


def build_human_editorial() -> HumanEditorialSpec:
    return HumanEditorialSpec(
        topic_dilemmas=[
            "Người mới làm nghiên cứu luôn mang tâm lý muốn giải quyết một vấn đề xã hội vĩ mô, dẫn đến đề cương bị từ chối hoặc bế tắc vì không thể thu thập dữ liệu.",
            "Ảo tưởng rằng đề tài càng lớn thì bài báo càng giá trị, trong khi bản chất khoa học là đóng góp tích lũy từng viên gạch nhỏ.",
        ],
        dynamic_questions=[
            "Tại sao một đề tài nghe rất hay và thời sự lại có tỷ lệ thất bại cao nhất?",
            "Khoa học thực sự vận hành như thế nào: phát minh lại bánh xe hay vặn chặt một con ốc?",
            "Làm thế nào để bóc tách một ý tưởng khổng lồ thành ba biến số đo lường được trong ba tháng?",
        ],
        author_raw_input="Đừng bắt đầu nghiên cứu bằng tham vọng giải cứu nhân loại. Hãy bắt đầu bằng một câu hỏi cụ thể mà bạn có thể đếm được bằng tay.",
        editorial_stance="Khoa học không cần bạn làm người hùng một đêm. Khoa học cần những phép đo chính xác và trung thực ở một lát cắt cực nhỏ.",
        expanded_content_ideas=[
            {
                "idea_id": "IDEA_01",
                "angle_type": "analysis",
                "summary": "Bóc tách nguyên nhân khiến người mới thích chọn đề tài vĩ mô vì nhầm lẫn giữa tầm quan trọng xã hội và tính khả thi khoa học.",
                "narrative_integration": "Đưa vào phân cảnh phân tích bẫy phát minh lại bánh xe.",
                "target_narrative_phase": "problem",
            },
            {
                "idea_id": "IDEA_02",
                "angle_type": "commentary",
                "summary": "Phản biện ngộ nhận nghiên cứu phải đột phá thay đổi cả thế giới qua ẩn dụ bức tường tri thức và viên gạch nhỏ.",
                "narrative_integration": "Đưa vào phân cảnh phản biện lật ngược vấn đề.",
                "target_narrative_phase": "counter_argument",
            },
            {
                "idea_id": "IDEA_03",
                "angle_type": "evaluation",
                "summary": "Đánh giá hiệu quả của kỹ thuật gọt củ hành giúp sinh viên hoàn thành bài báo trong ba tháng với nguồn lực hạn chế.",
                "narrative_integration": "Đưa vào phân cảnh đúc kết khung hành động.",
                "target_narrative_phase": "takeaway",
            },
        ],
    )


def build_characters() -> list[dict[str, Any]]:
    return [
        {
            "id": "CH01",
            "name": "Người mới làm nghiên cứu",
            "role": "researcher",
            "appearance": CAST_APPEARANCE,
            "outfit": DEFAULT_OUTFIT,
        }
    ]


def build_topic_16x9() -> ResearchedTopic:
    story_tuples = [(title, setting, rows) for title, setting, _, _, _, rows in STORY_16X9]
    scenes = build_scenes_from_story_rows(story_tuples, character_id="CH01")
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = STORY_16X9[i][2]
        sc.spoken_style = STORY_16X9[i][3]
        sc.narrative_phase = STORY_16X9[i][4]

    # Assign source claims for 16x9 scenes
    scenes[1].source_ids = ["SRC01"]
    scenes[1].claim_facts = [
        ("Lần đầu làm nghiên cứu, ai cũng thích những tên đề tài thật dài.", "SRC01", "Người mới thường nhầm giữa chủ đề lớn và câu hỏi nghiên cứu."),
    ]
    scenes[3].source_ids = ["SRC02"]
    scenes[3].claim_facts = [
        ("Thời gian làm bài tốt nghiệp chỉ vỏn vẹn ba tháng.", "SRC02", "Ba tháng chỉ đủ để giải quyết một mối liên hệ cụ thể."),
    ]
    scenes[4].source_ids = ["SRC03"]
    scenes[4].claim_facts = [
        ("Làm được trọn vẹn một việc nhỏ tốt hơn bỏ dở việc lớn.", "SRC03", "Giải quyết dứt điểm một điểm nhỏ có giá trị hơn ôm đồm việc lớn."),
    ]
    scenes[5].source_ids = ["SRC03"]
    scenes[5].claim_facts = [
        ("Hàng triệu nhà khoa học đi trước đã đóng góp từng viên gạch.", "SRC03", "Khoa học tiến lên nhờ tích lũy từng viên gạch nhỏ."),
    ]
    scenes[6].source_ids = ["SRC03"]
    scenes[6].claim_facts = [
        ("Việc của bạn không phải xây tường mới, mà là đặt thêm một viên gạch.", "SRC03", "Không ai đòi hỏi một bài báo phải thay đổi cả thế giới."),
    ]
    scenes[7].source_ids = ["SRC01"]
    scenes[7].claim_facts = [
        ("Khi thu nhỏ phạm vi, bạn kiểm soát được toàn bộ biến số.", "SRC01", "Càng thu nhỏ phạm vi bạn càng dễ tìm thấy câu trả lời."),
    ]
    scenes[9].source_ids = ["SRC02"]
    scenes[9].claim_facts = [
        ("Thay vì nghiên cứu giới trẻ cả nước, hãy chọn sinh viên trường bạn.", "SRC02", "Thu hẹp không gian giúp bạn thu thập dữ liệu chắc chắn hơn."),
    ]
    scenes[10].source_ids = ["SRC02"]
    scenes[10].claim_facts = [
        ("Đó là cách biến ý tưởng chung thành biến số đo được.", "SRC02", "Đề tài khả thi cần biến số đo lường được trong thực tế."),
    ]
    scenes[15].source_ids = ["SRC01"]
    scenes[15].claim_facts = [
        ("Hãy bắt đầu bằng một câu hỏi cụ thể mà bạn đếm được bằng tay.", "SRC01", "Một đề tài tốt bắt đầu từ một câu hỏi rất hẹp."),
    ]

    return ResearchedTopic(
        topic="Đừng Chọn Đề Tài NCKH Quá Lớn (Nghệ Thuật Bóp Nhỏ Đề Tài Bằng Kỹ Thuật Gọt Củ Hành)",
        audience="Sinh viên đại học, học viên cao học và người mới bước vào nghiên cứu khoa học đang loay hoay chọn đề tài hoặc bị giảng viên bác bỏ đề cương",
        goal="Giải tỏa áp lực vĩ mô, bóc trần sai lầm muốn giải quyết cả thế giới, hướng dẫn kỹ thuật bóc tách biến số gọt củ hành để định hình một câu hỏi nghiên cứu khả thi trong ba tháng",
        video_type="research_explainer",
        min_duration=420.0,
        max_duration=540.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        sources=build_sources(),
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _, _, _, _) in enumerate(STORY_16X9, 1)],
        characters=build_characters(),
        scenes=scenes,
        tone="Conversational Essayist điềm đạm, ấm áp, sâu sắc, lôi cuốn",
        language="vi",
        subtitles=False,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        human_editorial=build_human_editorial(),
        packaging=PackagingSpec(
            youtube_title="Đừng Chọn Đề Tài NCKH Quá Lớn",
            visual_hook="Stickman gập người ôm tảng đá xám to quá sức trên nền kem phẳng, chữ BỚT THAM LẠI nổi bật.",
            text_overlay="BỚT THAM LẠI",
            contrast_pair="Đề tài to đùng bế tắc vs Câu hỏi nhỏ giải quyết được",
            channel_pillar=CHANNEL_PILLAR_RESEARCH_GUIDE,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "cách chọn đề tài nckh",
                "nghiên cứu khoa học cho người mới",
                "thu hẹp đề tài nghiên cứu",
                "câu hỏi nghiên cứu",
                "research question",
                "kỹ thuật gọt củ hành",
            ],
            thumbnail_prompt=(
                "Orthographic 2D hand-drawn doodle poster. A minimalist bald circle-head stickman in solid "
                "cerulean-blue T-shirt (#3B82C4) staggering under an oversized grey rock prop. Clean unshaded "
                "warm paper-cream canvas (#F8F0DC), bold wobbly black marker contours (#000000). Top right "
                "shows big hand-lettered text 'BỚT THAM LẠI'. Zero 3D perspective, zero floor lines, zero room "
                "background, zero drop shadows, over 60% clean empty space."
            ),
        ),
    )


def build_topic_9x16() -> ResearchedTopic:
    story_tuples = [(title, setting, rows) for title, setting, _, _, _, rows in STORY_9X16]
    scenes = build_scenes_from_story_rows(story_tuples, character_id="CH01")
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = STORY_9X16[i][2]
        sc.spoken_style = STORY_9X16[i][3]
        sc.narrative_phase = STORY_9X16[i][4]

    # Assign source claims for 9x16 scenes
    scenes[1].source_ids = ["SRC01"]
    scenes[1].claim_facts = [
        ("Lời phê ngắn gọn: Quá rộng, không thể làm.", "SRC01", "Một đề tài tốt bắt đầu từ một câu hỏi rất hẹp."),
    ]
    scenes[2].source_ids = ["SRC03"]
    scenes[2].claim_facts = [
        ("Việc của bạn là đặt thêm một viên gạch nhỏ.", "SRC03", "Khoa học tiến lên nhờ tích lũy từng viên gạch nhỏ."),
    ]
    scenes[3].source_ids = ["SRC02"]
    scenes[3].claim_facts = [
        ("Mẫu gần gũi giúp dữ liệu rất chắc chắn.", "SRC02", "Thu hẹp không gian giúp bạn thu thập dữ liệu chắc chắn hơn."),
    ]
    scenes[4].source_ids = ["SRC02"]
    scenes[4].claim_facts = [
        ("Bài toán bây giờ làm gọn trong ba tháng.", "SRC02", "Ba tháng chỉ đủ để giải quyết một mối liên hệ cụ thể."),
    ]

    return ResearchedTopic(
        topic="Đừng Chọn Đề Tài NCKH Quá Lớn (Bản Dọc 60 Giây)",
        audience="Sinh viên đại học, học viên cao học và người mới bước vào nghiên cứu khoa học lướt video ngắn trên di động",
        goal="Tóm gọn kỹ thuật gọt củ hành trong 60 giây và hướng dẫn bóp nhỏ đề tài NCKH khả thi trong ba tháng",
        video_type="research_explainer",
        min_duration=45.0,
        max_duration=65.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=build_sources(),
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _, _, _, _) in enumerate(STORY_9X16, 1)],
        characters=build_characters(),
        scenes=scenes,
        tone="Conversational Essayist gãy gọn, gần gũi, nhịp điệu nhanh và cuốn hút",
        language="vi",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        human_editorial=build_human_editorial(),
        packaging=PackagingSpec(
            youtube_title="Đừng Chọn Đề Tài NCKH Quá Lớn",
            visual_hook="Stickman gập người ôm tảng đá xám to quá sức trên nền kem phẳng, chữ BỚT THAM LẠI nổi bật.",
            text_overlay="BỚT THAM LẠI",
            contrast_pair="Đề tài to đùng bế tắc vs Câu hỏi nhỏ giải quyết được",
            channel_pillar=CHANNEL_PILLAR_RESEARCH_GUIDE,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "cách chọn đề tài nckh",
                "thu hẹp đề tài nghiên cứu",
                "kỹ thuật gọt củ hành",
                "short 9x16",
            ],
            thumbnail_prompt=(
                "Orthographic 2D hand-drawn doodle poster in 9:16 vertical ratio. A minimalist bald circle-head stickman in "
                "solid cerulean-blue T-shirt (#3B82C4) staggering under an oversized grey rock prop. Clean unshaded warm "
                "paper-cream canvas (#F8F0DC), bold wobbly black marker contours (#000000). Top center shows big hand-lettered "
                "text 'BỚT THAM LẠI'. Zero 3D perspective, zero floor lines, zero room background, zero drop shadows, over "
                "60% clean empty space."
            ),
        ),
    )


def count_total_beats(scenes: List[ResearchedScene]) -> int:
    return sum(len(sc.visual_beats) for sc in scenes)


def export_package(topic: ResearchedTopic, out_dir: Path) -> dict[str, Any]:
    result = write_production_package(out_dir, topic, allow_active=True)
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
    content_text = (out_dir / "content.json").read_text(encoding="utf-8")
    (draft_dir / "content.json").write_text(content_text, encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Research Topic Size 16:9 & 9:16 production blueprint.")
    parser.add_argument("--ratio", choices=["16:9", "9:16", "dual"], default="dual", help="Aspect ratio to build")
    parser.add_argument("--out-dir", type=Path, default=SYS_DIR / "runs", help="Output directory root")
    parser.add_argument("--blueprint-dir", type=Path, default=SYS_DIR / "content" / "blueprints", help="Blueprint directory root")
    args = parser.parse_args()

    ratios = ["16:9", "9:16"] if args.ratio == "dual" else [args.ratio]
    all_passed = True

    for r in ratios:
        if r == "16:9":
            topic = build_topic_16x9()
            job_name = "research-topic-size-16x9"
        else:
            topic = build_topic_9x16()
            job_name = "research-topic-size-9x16"

        targets = [args.out_dir / job_name]
        if args.blueprint_dir:
            targets.append(args.blueprint_dir / job_name)

        print("\n========================================================")
        print(f"[*] ĐANG XÂY DỰNG BỘ HỒ SƠ: {job_name} ({r})")
        print(f"    - Số phân cảnh: {len(topic.scenes)}")
        print(f"    - Tổng visual beats: {count_total_beats(topic.scenes)}")
        print(f"    - Visual Pacing: {topic.visual_pacing_profile}")

        for target_dir in targets:
            target_dir.mkdir(parents=True, exist_ok=True)
            res = export_package(topic, target_dir)
            print(f"  [+] Đã xuất gói tại: {target_dir}")
            print(f"      - brief.json: {res['brief_file']}")
            print(f"      - content.json: {res['content_file']}")
            print(f"      - script.json: {res['script_file']}")
            print(f"      - cadence_report.json: {res['cadence_file']}")
            print(f"      - SHA256: {res['brief_hash']}")

            cadence = res.get("cadence_report", {})
            print(f"  [*] Âm học: {cadence.get('total_duration', 0.0):.1f}s | "
                  f"Âm tiết: {cadence.get('total_actual_syllables')}/{cadence.get('total_target_syllables')} | "
                  f"Max drift: {cadence.get('max_drift', 0.0):.2f}s | Cảnh báo: {cadence.get('warnings_count', 0)}")

            if not res["valid_contracts"]:
                all_passed = False
                print(f"  [FAIL] Lỗi hợp đồng tại {target_dir}:")
                for err in res["contract_errors"]:
                    print(f"    - {err}")
            else:
                print("  [PASS] 100% HỢP LỆ theo Hợp đồng Schema 3.0 & Cadence Checker")

            diversity = res.get("diversity_report", {})
            if diversity.get("violations"):
                print("  [WARN] Phát hiện vi phạm diversity:")
                for v in diversity["violations"]:
                    print(f"    - {v}")

    print("\n========================================================")
    if all_passed:
        print("[SUCCESS] Toàn bộ gói hồ sơ kỹ thuật cho Research Topic Size đã hoàn thành và đạt chuẩn!")
        return 0
    else:
        print("[FAILURE] Phát hiện lỗi trong quá trình đóng gói hồ sơ kỹ thuật.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
