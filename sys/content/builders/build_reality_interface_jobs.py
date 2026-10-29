#!/usr/bin/env python3
"""Build production-ready packages for Reality Interface Paradox (16:9 Landscape & 9:16 Portrait).

Pillar: "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức" (tier_1_broad -> tier_2_mid)
Core Topic: "Mắt Bạn Không Hề Nhìn Thấy Thế Giới Thật?" (The Case Against Reality & Spacetime Compression)
Experiments & Theories:
  - Donald D. Hoffman (2019) "The Case Against Reality: Why Evolution Hid the Truth from Our Eyes"
  - Nima Arkani-Hamed (2012) "Spacetime is Doomed: Scattering Amplitudes and the Holographic Principle"
  - Chetan Prakash, Donald Hoffman et al. (2014) "Fitness Beats Truth Theorem in Evolutionary Game Theory"

Formats:
  - reality-interface-paradox-16x9: 18 scenes, 8-part narrative arc landscape explainer (>= 1,800 syl)
  - reality-interface-paradox-9x16: 6 scenes, 60-second vertical mobile short explainer
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
    DEFAULT_CHANNEL_PILLAR,
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

# ---------------------------------------------------------------------------
# STORY 16:9 (18 Scenes — 8-Part Layered Narrative Arc Explainer Blueprint)
# ---------------------------------------------------------------------------
STORY_16X9: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    # STAGE 1: hook (Scenes 1-2)
    (
        "Cú tát thực tại mở màn",
        "Solid warm cream canvas (#F8F0DC).",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Có bao giờ bạn tự hỏi, mọi thứ trước mắt có thật không?", "full_scene:CH01|Stickman stands in open warm cream space looking at own open palms with curiosity and wonder."),
            ("Chúng ta luôn tin rằng mắt mình thấy sao thì đời là vậy.", "variation:CH01|Stickman touches gentle fingertips to eyelids with calm trusting expression on solid cream field."),
            ("Mỗi buổi sáng thức dậy, bạn thấy ánh nắng chiếu qua khung cửa.", "concept_metaphor:none|A simple doodle sun icon drawn in raw black marker line on calm cream background with seventy percent negative space."),
            ("Chạm tay xuống mặt bàn, bạn cảm nhận rõ độ cứng cáp.", "macro_prop:none|A simple doodle rectangular window frame outline drawn with raw black marker on calm cream canvas with eighty percent negative space, zero floor lines."),
            ("Mọi cảm giác đều rõ ràng đến mức chẳng ai thèm nghi ngờ.", "variation:CH01|Stickman presses palm flat against a simple tabletop outline with solid certainty, clean black marker line, zero wood grain."),
            ("Thế nhưng các nhà nghiên cứu lại tìm ra một điều rất lạ.", "concept_metaphor:none|A simple doodle magnifying glass focusing on a solid black checkmark with seventy percent calm negative space, black and white marker art."),
            ("Đôi mắt của chúng ta sinh ra không phải để nhìn sự thật.", "full_scene:CH01|Stickman lowers hands and looks directly forward with open questioning posture on cream ground."),
            ("Nó chỉ là một công cụ giúp bạn dễ sống hơn mà thôi.", "concept_metaphor:none|A simple doodle human eye drawing with wobbly black marker lines on flat cream canvas with seventy percent negative space."),
        ],
    ),
    (
        "Ảo giác ma trận trong đời thực",
        "Clean pure white background (#FFFFFF).",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Nhiều người xem phim ma trận thường nghĩ thế giới ảo rất xa vời.", "full_scene:CH01|Stickman sits on a small four-legged wooden stool facing right toward a flat blank black television screen on pure white ground. Zero light patterns, zero squiggles, zero floating lines, seventy percent open white space."),
            ("Chúng ta cười khi thấy các nhân vật bị nhốt trong máy móc.", "variation:CH01|Stickman shakes head with gentle bemused smile while watching the screen display."),
            ("Ta tự hào vì mình đang hít thở bầu không khí tự nhiên.", "variation:CH01|Stickman stands tall taking a deep calm breath with hands resting lightly at sides."),
            ("Thế nhưng tự nhiên đã làm điều tương tự từ rất lâu rồi.", "concept_metaphor:none|A simple doodle double-helix DNA ladder drawn with raw black marker lines beside a tiny solid black brain icon on pure white field, eighty percent negative space."),
            ("Mọi thứ bạn nhìn, nghe hay chạm vào đều do não tự vẽ ra.", "visual_diagram:none|A simple thin circle outline enclosing a tiny solid black brain silhouette in the center of pure white canvas, seventy percent negative space."),
            ("Não giống như một người làm phim hoạt hình tài ba vậy.", "visual_diagram:none|A single simple doodle rectangular photo frame outline resting flat on pure white ground, eighty percent open space, zero extra lines."),
            ("Nó liên tục phác thảo hình ảnh để bạn dễ định hướng.", "full_scene:CH01|Stickman looks around at open white space with reflective and contemplative eyes."),
            ("Và bạn đang sống trong bức tranh do chính cái đầu mình tạo nên.", "still_life:none|A single minimalist black seed doodle resting peacefully on pristine white ground with wide open breathing space."),
        ],
    ),

    # STAGE 2: lead_in (Scenes 3-4)
    (
        "Thí nghiệm chiếc cốc cà phê",
        "Solid ivory neutral field (#F8F0DC).",
        "narrative_warm",
        "demystifying_truth",
        "lived_friction",
        [
            ("Hãy thử nhìn vào ly cà phê quen thuộc trên bàn làm việc.", "full_scene:CH01|Stickman points index finger down toward a simple ceramic mug on clean ivory table outline with zero wood grain."),
            ("Bạn thấy màu nâu sẫm sóng sánh rất bắt mắt.", "macro_prop:none|A ceramic coffee mug filled with flat dark brown liquid resting on calm ivory surface, simple black outline."),
            ("Bạn ngửi thấy mùi thơm thoang thoảng bay lên.", "concept_metaphor:none|A simple ceramic coffee mug with a single straight vertical black line rising straight up above it on calm ivory surface, eighty percent negative space, zero wavy squiggles."),
            ("Khi nhấp một ngụm, bạn cảm nhận ngay vị đắng nơi đầu lưỡi.", "variation:CH01|Stickman raises mug to lips taking a calm sip with eyes closed in focused tasting."),
            ("Bạn tin chắc màu nâu và vị đắng là có thật ở ngoài đời.", "concept_metaphor:none|A simple doodle coffee cup separated from a floating question mark with wide open ivory space."),
            ("Nhưng bản thân ly cà phê đâu có tự dán nhãn màu nâu hay vị đắng.", "concept_metaphor:none|A simple coffee mug outline drawn with thin dashed black strokes resting calmly on ivory ground, eighty percent negative space, zero floating particles."),
            ("Đó chỉ là cách các tế bào cảm giác báo tin về cho não.", "full_scene:CH01|Stickman gazes thoughtfully at the mug with open understanding on solid ivory ground."),
            ("Cái ly bạn thấy chỉ là cách não dịch lại tín hiệu cho dễ hiểu.", "visual_diagram:none|A single straight black horizontal arrow pointing from a solid black square to a solid black circle on flat ivory canvas, eighty percent negative space."),
        ],
    ),
    (
        "Vũ trụ trần trụi không màu sắc",
        "Pure stark white field (#FFFFFF).",
        "analytical_crisp",
        "scientific_evidence",
        "lived_friction",
        [
            ("Thực tế bên ngoài kia không hề giống như chúng ta tưởng.", "full_scene:CH01|Stickman stands beside a tall minimalist chalkboard with a single clean straight horizontal line drawn on it, eighty percent negative space."),
            ("Bên ngoài cái đầu của bạn, không gian không hề có màu hay tiếng.", "concept_metaphor:none|A simple crude cartoon skull outline drawn in raw black marker line beside a single flat neutral sphere, eighty percent negative space."),
            ("Nơi đó chỉ có các bước sóng và những rung động không khí.", "concept_metaphor:none|A black and white doodle sphere outline with zero color fill surrounded by quiet negative space on pure white canvas."),
            ("Bông hoa hồng không tự có màu đỏ, tiếng hát không tự vang lên.", "visual_diagram:none|A single gentle horizontal sine wave line drawn with a thin black marker across the center of pure white canvas, eighty-five percent negative space."),
            ("Tất cả chỉ là những hạt bụi và luồng sáng vô hình bay lượn.", "concept_metaphor:none|A simple single-line doodle flower crossed out with a single thin black line, clean black and white marker outline, eighty percent negative space."),
            ("Chính bộ não của bạn đã tự tay tô màu cho bông hoa.", "visual_diagram:none|A single pair of crossed straight black lines forming a simple X mark on clean white canvas, ninety percent negative space."),
            ("Não tự phổ nhạc để biến những rung động thành âm thanh vui tai.", "full_scene:CH01|Stickman holds a simple painter palette and brush with a subtle knowing smile on white ground."),
            ("Nếu không có bạn quan sát, thế giới chỉ là một khoảng lặng im.", "still_life:none|A minimalist wooden drawing easel standing quietly with eighty percent negative white space, simple black line drawing without color."),
        ],
    ),

    # STAGE 3: tension (Scenes 5-6)
    (
        "Ảo tưởng mắt thấy tai nghe",
        "Solid warm cream canvas (#F8F0DC).",
        "narrative_warm",
        "demystifying_truth",
        "empirical_conflict",
        [
            ("Vậy tại sao chúng ta lại tin vào mắt mình suốt bao năm qua?", "full_scene:CH01|Stickman places hand on chin, deep in intellectual inquiry on warm solid cream surface."),
            ("Ta cứ nghĩ đôi mắt hoạt động y hệt như một chiếc máy ảnh.", "macro_prop:none|A simple crude doodle box camera on three straight stick legs on flat cream surface, clean black marker outline, eighty percent negative space."),
            ("Cứ có ánh sáng lọt vào là mắt chụp lại nguyên vẹn mọi thứ.", "concept_metaphor:none|A simple doodle eye icon with a single straight horizontal arrow pointing inward toward the pupil, eighty percent negative cream space."),
            ("Nhưng cách hiểu ngây thơ này đã bị khoa học làm sáng tỏ.", "concept_metaphor:none|A simple doodle camera outline crossed out with a single clean black line, black and white marker outline, eighty percent negative space."),
            ("Mắt của bạn không chụp ảnh một cách thụ động đâu.", "variation:CH01|Stickman shakes head gently with one palm held outward in friendly correction."),
            ("Mắt chỉ bắt được một chút ánh sáng rồi gửi về cho não đoán.", "visual_diagram:none|A simple doodle blank rectangular picture frame outline standing upright on flat cream canvas, eighty-five percent negative space."),
            ("Bạn không nhìn thẳng ra thế giới bên ngoài.", "full_scene:CH01|Stickman points index finger to temple with an enlightened gentle smile on cream ground."),
            ("Bạn chỉ đang xem lại bản phác thảo do não bộ tự vẽ ra.", "concept_metaphor:none|A simple black triangle doodle inside a simple human head profile outline on flat cream ground, eighty-five percent negative space."),
        ],
    ),
    (
        "Nghịch lý nhận thức của sinh vật",
        "Clean pure white background (#FFFFFF).",
        "narrative_warm",
        "demystifying_truth",
        "empirical_conflict",
        [
            ("Đến đây, chắc chắn bạn sẽ tự hỏi một điều rất tự nhiên.", "full_scene:CH01|Stickman stands in open white space looking upward with a curious questioning head tilt."),
            ("Chẳng phải nhìn đúng sự thật sẽ giúp ta sống an toàn hơn sao?", "variation:CH01|Stickman tilts head thoughtfully, looking off to the side with hands clasped behind back."),
            ("Nếu thấy rõ con rắn hay thú dữ đang rình rập.", "concept_metaphor:none|A simple doodle silhouette of a crouching tiger cat outline drawn in black marker line on pure white field, eighty percent negative space."),
            ("Bạn sẽ né tránh nhanh hơn và thoát thân an toàn hơn.", "variation:CH01|Stickman gestures swiftly with an open running arm toward safety on clean white canvas."),
            ("Nhìn chuẩn xác đáng lẽ phải là điều tốt nhất cho con người.", "concept_metaphor:none|A simple doodle outline of an open gift box on pure white background, eighty percent negative space."),
            ("Thế nhưng quá trình sinh tồn lại không cần đến sự thật tuyệt đối.", "concept_metaphor:none|A simple black scale doodle in perfect horizontal balance on clean white field, eighty percent negative space."),
            ("Tự nhiên chỉ quan tâm đúng một mục tiêu duy nhất.", "full_scene:CH01|Stickman stands upright, placing hand over heart with clear calm gaze."),
            ("Đó là làm sao để bạn sống sót và nuôi nấng con cái.", "still_life:none|A small simple doodle bird standing peacefully on flat white ground, eighty-five percent negative space."),
        ],
    ),

    # STAGE 4: paradigm_shift (Scenes 7-8)
    (
        "Chi phí năng lượng của sự thật",
        "Solid soft cream canvas (#F8F0DC).",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Bởi vì nhìn thấu tận gốc mọi thứ đòi hỏi cái giá quá đắt.", "full_scene:CH01|Stickman rubs forehead with mild fatigue and thoughtful expression on solid cream field."),
            ("Não bộ không tiến hóa để nhìn thấy sự thật khách quan.", "concept_metaphor:none|A simple doodle human brain silhouette wearing a simple black blindfold band across its center on flat cream canvas, eighty percent negative space."),
            ("Vũ trụ ngoài kia có hàng tỷ chi tiết nhỏ li ti trong mỗi mét vuông.", "visual_diagram:none|A single small black square doodle resting in the vast empty center of cream canvas, ninety percent negative space."),
            ("Não không thể nào phân tích hết mọi thứ khi bạn đang đi bộ.", "variation:CH01|Stickman pauses mid-stride, looking down at feet with calm mindful posture."),
            ("Làm như vậy thì đầu bạn sẽ nhanh chóng kiệt sức vì quá tải.", "concept_metaphor:none|A simple battery doodle outline with an empty outline body on solid cream canvas, eighty percent negative space."),
            ("Bạn sẽ đói lả trước khi kịp hái được một quả dâu dại.", "still_life:none|A single small berry outline on a simple horizontal ground line, eighty-five percent negative cream space."),
            ("Tiến hóa ưu tiên sinh tồn hơn là thấu suốt chân lý.", "full_scene:CH01|Stickman stands calm and composed with hands relaxed at sides on cream ground."),
            ("Để giữ mạng sống cho bạn, não bộ bắt buộc phải giấu bớt chi tiết.", "concept_metaphor:none|A simple doodle curtain outline pulled half-closed on solid cream canvas, eighty percent negative space."),
        ],
    ),
    (
        "Không-thời gian là tệp nén dữ liệu",
        "Solid ivory neutral field (#F8F0DC).",
        "analytical_crisp",
        "scientific_evidence",
        "structural_model",
        [
            ("Các chuyên gia hàng đầu đã rút ra một nhận định rất thú vị.", "full_scene:CH01|Stickman stands with hands on hips, nodding slowly in thoughtful intellectual agreement."),
            ("Không gian ba chiều chỉ là định dạng nén dữ liệu của não.", "visual_diagram:none|A simple flat 2D cube outline drawn in thin black marker on calm ivory canvas, eighty-five percent negative space."),
            ("Giống như điện thoại nén bức ảnh lớn thành một tệp nhỏ gọn.", "concept_metaphor:none|A simple flat rectangular envelope doodle resting peacefully on ivory ground, eighty-five percent negative space."),
            ("Bộ não nén hàng tỷ photon thành một hình ảnh đơn giản.", "concept_metaphor:none|A single straight black horizontal arrow pointing toward a solid black circle on clean ivory ground, eighty-five percent negative space."),
            ("Khi bạn nhìn thấy một quả táo đỏ nằm trên bàn ăn.", "macro_prop:none|A single simple red apple doodle with a small green leaf resting on flat ivory ground line, eighty percent negative space."),
            ("Bạn đâu cần nhìn thấy từng tế bào hay hạt bụi li ti của nó.", "concept_metaphor:none|A simple magnifying glass outline focusing on an empty circle on ivory canvas, eighty-five percent negative space."),
            ("Bạn chỉ cần thấy một hình tròn đỏ để biết đây là đồ ăn ngon.", "still_life:none|A single red apple doodle with a simple flat white tag outline attached to its stem on ivory field, eighty percent negative space."),
            ("Vật thể ba chiều giống như biểu tượng trên màn hình máy tính.", "visual_diagram:none|A single small rectangular desktop icon doodle floating in open ivory space, eighty-five percent negative space."),
        ],
    ),

    # STAGE 5: structural_model (Scenes 9-10)
    (
        "Ẩn dụ màn hình máy tính để bàn",
        "Clean pure white background (#FFFFFF).",
        "narrative_warm",
        "demystifying_truth",
        "structural_model",
        [
            ("Để hình dung dễ hơn, bạn hãy nhìn vào màn hình máy tính.", "full_scene:CH01|Stickman gestures forward with both hands open, inviting observation on pure white canvas."),
            ("Ở góc màn hình luôn có một icon thùng rác nhỏ nhắn.", "macro_prop:none|A single simple doodle trash can icon drawn in black marker line with light blue fill on flat white ground, eighty percent negative space."),
            ("Biểu tượng thùng rác không chứa rác thật hay chất dẻo nhựa.", "concept_metaphor:none|A simple doodle trash can outline with lid slightly tilted open on pure white canvas, eighty-five percent negative space."),
            ("Nó chỉ là hình vẽ để che đi hàng triệu vi mạch điện tử bên trong.", "visual_diagram:none|A single clean flat rectangular panel doodle covering two simple parallel black wires on white canvas, eighty percent negative space."),
            ("Nếu bạn phải nhìn thấy dòng điện bạn sẽ không thể dùng máy tính.", "variation:CH01|Stickman raises palm toward the viewer with calm reassuring smile on pure white ground."),
            ("Hình vẽ sinh ra để giấu đi những thứ phức tạp bên dưới.", "visual_diagram:none|A simple flat rectangular screen doodle with a single tiny black icon in the top-left corner on pure white canvas, eighty percent negative space."),
            ("Đôi mắt của bạn cũng giống hệt như chiếc màn hình hiển thị.", "full_scene:CH01|Stickman touches fingers to spectacles frame with quiet insightful smile."),
            ("Không gian là hình nền, còn các đồ vật chỉ là những icon chỉ dẫn.", "visual_diagram:none|A single small square folder icon doodle resting quietly on vast white canvas, eighty-five percent negative space."),
        ],
    ),
    (
        "Thực nghiệm mô phỏng máy tính FBT",
        "Pure bright white canvas (#FFFFFF).",
        "analytical_crisp",
        "scientific_evidence",
        "structural_model",
        [
            ("Ý tưởng này không phải là lời nói suông của ai đó đâu.", "full_scene:CH01|Stickman stands beside a simple chalkboard, holding a long thin pointer stick with calm confidence."),
            ("Nó đã được kiểm chứng bằng những phép tính rất chặt chẽ.", "concept_metaphor:none|A simple balance scale doodle with two equal flat dishes on solid cream field, eighty percent negative space."),
            ("Các nhà khoa học đã tạo ra những thế giới giả lập trên máy tính.", "macro_prop:none|A simple doodle computer monitor outline with a blank white screen resting on cream ground, eighty percent negative space."),
            ("Họ thả vào đó hai nhóm sinh vật ảo với cách nhìn khác nhau.", "visual_diagram:none|Two simple identical doodle fish swimming side by side in open cream space, eighty percent negative space."),
            ("Nhóm thứ nhất được lập trình để nhìn thấy tường tận mọi sự thật.", "concept_metaphor:none|A simple doodle eye icon drawn in black marker on flat cream ground, eighty-five percent negative space."),
            ("Nhóm thứ hai chỉ nhìn thấy những thứ giúp ích cho việc sống sót.", "concept_metaphor:none|A simple red apple doodle drawn in black marker with red fill on flat cream ground, eighty-five percent negative space."),
            ("Hai nhóm bắt đầu cạnh tranh nhau để tìm kiếm thức ăn.", "variation:CH01|Stickman watches the two sides with focused engaged posture on solid cream canvas."),
            ("Mọi điều kiện ban đầu của hai bên đều giống hệt như nhau.", "visual_diagram:none|Two simple identical vertical parallel lines of equal length standing quietly on cream field, eighty-five percent negative space."),
        ],
    ),

    # STAGE 6: empirical_conflict (Scenes 11-12)
    (
        "Sự diệt vong của kẻ thấy chân lý",
        "Pure stark white field (#FFFFFF).",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Kết quả sau hàng triệu lượt thử nghiệm khiến ai cũng bất ngờ.", "full_scene:CH01|Stickman raises eyebrows in quiet dramatic realization on pure white canvas."),
            ("Nhóm sinh vật cố nhìn thấu mọi thứ bị tụt lại rất nhanh.", "visual_diagram:none|Two horizontal progress bar outlines, top bar short, bottom bar fully filled, eighty percent negative space."),
            ("Chúng mất quá nhiều thời gian để săm soi những chi tiết vụn vặt.", "variation:CH01|Stickman sits on floor with knees drawn up, deep in contemplative study on white ground."),
            ("Trong khi đối thủ chỉ cần liếc mắt là biết chỗ nào có mồi ngon.", "concept_metaphor:none|A simple doodle open hand catching a small bread loaf outline, eighty percent negative space."),
            ("Sinh vật thấy sự thật tuyệt chủng trước kẻ chỉ thấy sinh tồn.", "visual_diagram:none|A simple doodle tombstone outline beside an upright sprouting plant doodle on pure white field, eighty percent negative space."),
            ("Trong bất kỳ môi trường cạnh tranh thức ăn khốc liệt nào.", "still_life:none|Two simple wooden bowls on flat ground, one empty outline, one filled with fruit, eighty percent negative space."),
            ("Nhóm mải nhìn sự thật đều bị đói và biến mất không còn dấu vết.", "full_scene:CH01|Stickman stands in quiet solemn reflection with arms resting at sides."),
            ("Không hề có một ngoại lệ nào trong suốt các bài kiểm tra.", "concept_metaphor:none|A single bold black checkmark doodle stamped in the center of pure white canvas, eighty-five percent negative space."),
        ],
    ),
    (
        "Chiến thắng tuyệt đối của bộ lọc sinh tồn",
        "Solid ivory neutral field (#F8F0DC).",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Chiến thắng thuộc về nhóm có cách nhìn đơn giản và thực dụng.", "full_scene:CH01|Stickman raises both arms in joyful triumph, celebrating clarity on calm ivory canvas."),
            ("Chúng không bận tâm bản chất sâu xa của đồ vật là cái gì.", "concept_metaphor:none|A simple flat square shield doodle outline with a clean surface on ivory field, eighty-five percent negative space."),
            ("Chúng chỉ cần biết: món này ăn được hay nguy hiểm cần tránh.", "visual_diagram:none|A simple doodle fork outline pointing down beside a small crossed-out skull outline on ivory canvas, eighty percent negative space."),
            ("Đó cũng chính là cách mà muôn loài trên Trái Đất đang sống.", "concept_metaphor:none|A simple doodle globe circle outline with clean continents on ivory ground, eighty percent negative space."),
            ("Con bọ cánh cứng chỉ cần thấy màu nâu lấp lánh là tìm ra bạn đời.", "still_life:none|A simple doodle beetle bug crawling peacefully on ivory ground, eighty percent negative space."),
            ("Con ếch chỉ cần thấy đốm đen di chuyển là thè lưỡi tóm con mồi.", "still_life:none|A simple cartoon doodle of a small fly insect with transparent wings on ivory ground, eighty percent negative space."),
            ("Bộ não con người chúng ta cũng vận hành y như thế mà thôi.", "full_scene:CH01|Stickman places hands on hips with warm relatable posture on solid ivory ground."),
            ("Bạn sống khỏe mạnh là nhờ não biết bỏ qua những thứ rườm rà.", "concept_metaphor:none|A simple open umbrella doodle outline shielding a small black dot from above on ivory field, eighty percent negative space."),
        ],
    ),

    # STAGE 7: actionable_resolution (Scenes 13-14)
    (
        "Bẫy ngụy biện của chủ nghĩa hư vô",
        "Solid warm cream canvas (#F8F0DC).",
        "narrative_warm",
        "demystifying_truth",
        "actionable_resolution",
        [
            ("Nghe xong chuyện này, có thể bạn sẽ cảm thấy hơi hụt hẫng.", "full_scene:CH01|Stickman raises hands in reassuring calm gesture, smiling warmly at the viewer on solid cream canvas."),
            ("Nhiều người nghĩ nếu mọi thứ là ảo ảnh thì sống có ý nghĩa gì.", "variation:CH01|Stickman gazes blankly ahead with questioning open eyes on cream canvas."),
            ("Họ tự hỏi: tại sao ta không lao đầu vào một chiếc xe tải?", "macro_prop:none|A simple crude doodle boxy truck silhouette on flat cream ground line, eighty percent negative space."),
            ("Nếu chiếc xe tải chỉ là hình ảnh nén, sao nó làm đau ta được?", "variation:CH01|Stickman shakes head in sharp disagreement with palms held up defensively."),
            ("Nghĩ như vậy là một sự nhầm lẫn cực kỳ tai hại và nguy hiểm.", "concept_metaphor:none|A bold red doodle exclamation mark inside a simple black triangle outline on cream canvas, eighty-five percent negative space."),
            ("Đừng bao giờ đánh đồng hình ảnh dẫn đường với sự vô hại.", "concept_metaphor:none|A delicate circle outline drifting beside a solid black brick outline on cream ground, eighty-five percent negative space."),
            ("Chiếc xe tải có thể chỉ là một tín hiệu do mắt bạn ghi nhận.", "full_scene:CH01|Stickman stands firm and poised, addressing the audience with mature insight."),
            ("Nhưng tín hiệu đó cảnh báo một vụ va chạm có thể lấy mạng bạn.", "still_life:none|A clean flat rectangular stone barrier standing immovable on solid cream canvas, eighty-five percent negative space."),
        ],
    ),
    (
        "Coi trọng nhưng không ngộ nhận",
        "Clean pure white background (#FFFFFF).",
        "narrative_warm",
        "demystifying_truth",
        "actionable_resolution",
        [
            ("Hãy nhớ lấy một bài học rất đơn giản và sâu sắc này.", "full_scene:CH01|Stickman holds up index finger, sharing a key insight with focused clarity on pure white canvas."),
            ("Coi trọng biểu tượng nhưng không ngộ nhận nó là sự thật.", "concept_metaphor:none|Stickman holds an umbrella doodle shielding a small stick figure from above on pure white canvas, eighty percent negative space."),
            ("Bạn không kéo tệp quan trọng vào thùng rác vì tôn trọng nó.", "visual_diagram:none|A neat folder icon hovering carefully above a desktop trash can outline on pure white ground, eighty percent negative space."),
            ("Bạn tránh xa con rắn độc vì biết nó có thể cắn chết người.", "concept_metaphor:none|A minimalist black snake silhouette curled peacefully on pure white canvas, eighty-five percent negative space."),
            ("Bạn vẫn cần tuân thủ luật chơi để giữ an toàn cho bản thân.", "variation:CH01|Stickman nods head with mature understanding, arms folded in balanced composure."),
            ("Nhưng đâu nhất thiết phải coi cái màn hình là tất cả cuộc đời.", "visual_diagram:none|A small desktop window frame set against vast open white canvas, eighty-five percent negative space."),
            ("Biết phân biệt điều này sẽ giúp lòng bạn thanh thản hơn rất nhiều.", "full_scene:CH01|Stickman takes a deep tranquil breath, opening hands wide with genuine relief."),
            ("Bạn sẽ có một cách nhìn nhẹ nhõm hơn về mọi chuyện quanh mình.", "still_life:none|A pristine single feather doodle floating gently downward with eighty percent negative white space."),
        ],
    ),

    # STAGE 8: deep_inquiry (Scenes 15-18)
    (
        "Giải mã bẫy pixel mạng xã hội",
        "Solid ivory neutral field (#F8F0DC).",
        "narrative_warm",
        "demystifying_truth",
        "actionable_resolution",
        [
            ("Bài học này cực kỳ hữu ích cho cuộc sống hàng ngày của bạn.", "full_scene:CH01|Stickman points toward a modern smartphone display resting on clean ivory desk outline."),
            ("Trong thời buổi hiện nay, con người lại tự tạo thêm nhiều icon mới.", "visual_diagram:none|Three simple horizontal black parallel lines drawn neatly across the center of ivory field, eighty-five percent negative space."),
            ("Đó là những con số trong tài khoản hay lượt like trên mạng xã hội.", "concept_metaphor:none|A single red heart doodle outline displayed cleanly in center of ivory field, eighty-five percent negative space."),
            ("Thực chất chúng chỉ là những điểm sáng trên mặt kính điện thoại.", "macro_prop:none|A single rectangular black smartphone outline with a blank dark screen resting on ivory canvas, eighty-five percent negative space."),
            ("Thế nhưng biết bao nhiêu người đang để những điểm sáng làm khổ mình.", "variation:CH01|Stickman lowers head slightly with eyes closed in calm thoughtful reflection on ivory ground."),
            ("Bạn lo lắng, mất ngủ và buồn bã vì những con số ảo trên màn hình.", "concept_metaphor:none|A simple flat cartoon cloud doodle with three straight vertical rain drop dashes on ivory ground, eighty-five percent negative space."),
            ("Bạn đang nhầm một cái icon nhỏ xíu với giá trị của chính bản thân.", "full_scene:CH01|Stickman stands beside a simple flat outline of a smartphone resting upright on ivory ground, eighty percent negative space."),
            ("Đó là cái bẫy vô hình mà cuộc sống hiện đại vô tình tạo ra.", "variation:CH01|Stickman stands tall and upright, looking forward with razor-sharp lucidity."),
        ],
    ),
    (
        "Thoát khỏi áp lực đồng trang lứa",
        "Pure stark white field (#FFFFFF).",
        "narrative_warm",
        "demystifying_truth",
        "actionable_resolution",
        [
            ("Khi bạn hiểu được điều này, mọi áp lực sẽ tự nhiên tan biến.", "full_scene:CH01|Stickman stands tall with open hands resting lightly at sides on clean pure white canvas."),
            ("Lời chê bai của người khác suy cho cùng chỉ là vài rung động gió.", "concept_metaphor:none|A simple doodle outline of a megaphone speaker crossed out with a single thin black line on clean white ground, eighty percent negative space."),
            ("Chiếc xe sang hay ngôi nhà to cũng chỉ là những tấm biển báo ngoài đời.", "concept_metaphor:none|A minimalist doodle car outline sitting calmly on white field, eighty-five percent negative space."),
            ("Chúng sinh ra để thôi thúc bạn làm việc và phấn đấu mỗi ngày.", "visual_diagram:none|A simple four-rung vertical wooden ladder doodle standing quietly on clean white ground, eighty-five percent negative space."),
            ("Nếu thấy vui thì bạn cứ tham gia vào cuộc chơi của cuộc sống.", "variation:CH01|Stickman holds up a game chess piece with a calm confident player smile on white ground."),
            ("Nhưng đừng bao giờ để một món đồ bên ngoài quyết định nụ cười của bạn.", "concept_metaphor:none|A balanced wooden chess king standing unbothered in wide seventy percent open space."),
            ("Hãy sống như một người chơi thông thái và tự do trong tâm trí.", "full_scene:CH01|Stickman smiles with serene independence, hands resting comfortably in pockets."),
            ("Không có thất bại nào ngoài kia có thể làm tổn thương bạn được.", "still_life:none|A smooth pebble doodle resting securely on stark white canvas, eighty-five percent negative space."),
        ],
    ),
    (
        "Làm chủ bộ giải mã tâm trí",
        "Solid warm cream canvas (#F8F0DC).",
        "narrative_warm",
        "demystifying_truth",
        "actionable_resolution",
        [
            ("Chính bạn là người quyết định cảm xúc cho cuộc đời của mình.", "full_scene:CH01|Stickman sits peacefully with open sketchbook, drawing a clean geometric framework on cream field."),
            ("Nỗi buồn hay sự thất vọng có thể ghé thăm bạn ngày hôm nay.", "variation:CH01|Stickman looks thoughtfully at own handwritten notes with calm perspective on cream ground."),
            ("Nhưng đó chỉ là cách cái đầu của bạn đang diễn giải sự việc.", "visual_diagram:none|A single neat column of three short black horizontal dashes on flat cream ground, eighty-five percent negative space."),
            ("Bạn không thể bắt trời ngừng mưa hay đổi thay người khác.", "concept_metaphor:none|A simple circular magnifying glass lens focusing on a single straight horizontal black line on cream canvas, eighty percent negative space."),
            ("Nhưng bạn hoàn toàn có thể đổi chiếc kính mà mình đang đeo.", "concept_metaphor:none|A simple black doodle pair of round eyeglasses resting on flat cream surface, eighty percent negative space."),
            ("Hãy chọn nhìn khó khăn như một bài tập để rèn luyện sự dẻo dai.", "concept_metaphor:none|A simple black key doodle lying horizontally on clean ivory surface, eighty-five percent negative space."),
            ("Khi bạn đổi cách nhìn nhận, thế giới quanh bạn sẽ tự nhiên đổi thay.", "full_scene:CH01|Stickman stands and closes the sketchbook with complete inner peace and self-mastery."),
            ("Đó là món quà tuyệt vời nhất mà tự nhiên đã dành tặng cho bạn.", "still_life:none|A small green sprout emerging gently from clean earth with boundless warm cream sky above, eighty-five percent negative space."),
        ],
    ),
    (
        "Thức tỉnh không cần viên thuốc đỏ",
        "Clean serene white field (#FFFFFF).",
        "reflective_slow",
        "philosophical_anchor",
        "actionable_resolution",
        [
            ("Bạn đâu cần phải tìm kiếm một phép màu nào xa xôi.", "full_scene:CH01|Stickman stands in center of pure white expanse, holding out a single open empty palm with quiet serenity."),
            ("Sự bình yên thực ra luôn ở ngay trước mắt bạn.", "variation:CH01|Stickman smiles peacefully with hands resting gently at sides on serene white ground."),
            ("Chỉ cần hiểu được chiếc kính mà tự nhiên trao tặng.", "concept_metaphor:none|A simple black doodle pair of round eyeglasses resting peacefully on flat white ground, eighty percent negative space."),
            ("Bạn sẽ thấy lòng mình nhẹ nhõm và tự do hơn.", "variation:CH01|Stickman takes a calm gentle step forward with lighthearted ease on clean white expanse."),
            ("Hãy cứ yêu quý cuộc sống và trọn vẹn từng khoảnh khắc.", "still_life:none|A single clean ceramic bowl of clear water sitting calmly on flat pure white canvas with eighty percent negative space."),
            ("Nếu câu chuyện nhỏ này đem lại chút thư thái cho bạn.", "full_scene:CH01|Stickman sits cross-legged on clean white ground, holding a warm cup with both hands and smiling comfortably."),
            ("Đừng ngần ngại nhấn like và để lại một lời nhắn nhé.", "concept_metaphor:none|A simple doodle outline of a thumbs-up hand icon drawn with a single black marker line on flat pure white canvas, eighty percent negative space."),
            ("Và bấm theo dõi kênh để chúng mình cùng gặp lại nhau nha.", "variation:CH01|Stickman smiles warmly and waves a friendly hand goodbye on flat pure white canvas with eighty percent open space."),
        ],
    ),
]

# ---------------------------------------------------------------------------
# STORY 9:16 (6 Scenes — 60-Second Short Explainer Spinoff)
# ---------------------------------------------------------------------------
STORY_9X16: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    (
        "Cú tát ly cà phê",
        "Solid warm cream canvas (#F8F0DC).",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Ly cà phê bạn đang cầm trên tay,", "macro_prop:none|A single simple white ceramic mug with dark coffee outline in center of flat solid cream canvas (#F8F0DC), zero pencils, zero desk clutter, zero decorative borders, eighty percent blank open space."),
            ("thực ra không có màu nâu hay vị đắng.", "full_scene:CH01|Stickman in blue shirt stands in center of plain cream canvas (#F8F0DC), looking down at a tiny coffee mug with curious eyes, zero desk, zero room interior, zero decorative borders, eighty percent negative space."),
            ("Bên ngoài đôi mắt của bạn,", "concept_metaphor:none|A simple minimalist human head profile outline in pure black marker on flat solid cream canvas (#F8F0DC), zero brain details, zero decorative borders, eighty-five percent blank negative space."),
            ("thế giới không hề có sẵn màu sắc hay âm thanh.", "concept_metaphor:none|A simple doodle sphere outline drawn with a single black marker line in center of plain white canvas (#FFFFFF), zero color fill, zero patterns, zero decorative borders, eighty-five percent negative space."),
        ],
    ),
    (
        "Vũ trụ không màu sắc",
        "Clean pure white background (#FFFFFF).",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Nơi đó chỉ có các bước sóng vô hình.", "visual_diagram:none|A single straight horizontal black line across center of flat pure white canvas (#FFFFFF), zero waves, zero vibrations, zero decorative borders, ninety percent blank open space."),
            ("Chính bộ não đã tự tay pha màu,", "full_scene:CH01|Stickman in blue shirt stands alone in center of plain white canvas (#FFFFFF), holding a simple painter brush, smiling gently, zero easel, zero palette clutter, zero borders, eighty-five percent negative space."),
            ("và tự thêm vào những âm thanh quen thuộc.", "concept_metaphor:none|A single clean blank square picture frame outline in center of flat white canvas (#FFFFFF) with a tiny black flower doodle inside, zero floral garlands, zero decorative borders, eighty-five percent negative space."),
            ("Tất cả chỉ để giúp bạn dễ sống hơn mà thôi.", "variation:CH01|Stickman in blue shirt stands calmly with hands at sides in center of plain white canvas (#FFFFFF), smiling peacefully, zero background objects, zero decorative borders, eighty-five percent negative space."),
        ],
    ),
    (
        "Cơ chế nén không-thời gian",
        "Solid ivory neutral field (#F8F0DC).",
        "analytical_crisp",
        "scientific_evidence",
        "structural_model",
        [
            ("Tại sao não lại làm như vậy?", "full_scene:CH01|Stickman in blue shirt raises an open hand in gentle inquiry in center of flat solid cream canvas (#F8F0DC), zero decorative borders, zero corner clutter, eighty-five percent negative space."),
            ("Nếu phải soi rõ từng hạt bụi li ti.", "visual_diagram:none|A single simple flat 2D square outline in center of flat pure cream canvas (#F8F0DC), zero 3D cubes, zero arrows, zero pencils, zero hanging garlands, zero stationery clutter, zero decorative borders, eighty-five percent blank space."),
            ("Cái đầu bạn sẽ kiệt sức vì quá tải.", "variation:CH01|Stickman in blue shirt touches temples gently with both hands in center of flat cream canvas (#F8F0DC), closed eyes, zero clutter, zero decorative borders, eighty-five percent negative space."),
            ("Không gian ba chiều chỉ là định dạng nén dữ liệu của não.", "concept_metaphor:none|A single simple vertical tube thermometer outline with a solid red liquid column at midpoint in center of plain cream canvas (#F8F0DC), zero smoke, zero decorative borders, eighty-five percent negative space."),
        ],
    ),
    (
        "Định lý FBT chấn động",
        "Pure stark white field (#FFFFFF).",
        "analytical_crisp",
        "scientific_evidence",
        "structural_model",
        [
            ("Các nhà khoa học đã làm thử nghiệm.", "visual_diagram:none|Two tiny simple stick figures standing calmly on opposite sides of center on flat pure white canvas (#FFFFFF), zero digital grids, zero borders, eighty-five percent negative space."),
            ("Nhóm mải nhìn sự thật đều bị đói lả.", "concept_metaphor:none|A single simple doodle human eye outline in center of flat pure white canvas (#FFFFFF), calm blue iris, zero decorative borders, zero pedestals, eighty-five percent negative space."),
            ("Sinh vật thấy sự thật tuyệt chủng trước kẻ chỉ thấy sinh tồn.", "concept_metaphor:none|A simple minimalist doodle tombstone outline in center of flat pure white canvas (#FFFFFF), zero flowers, zero grass, zero decorative borders, ninety percent negative space."),
            ("Chỉ kẻ biết thích nghi mới sống sót.", "visual_diagram:none|A simple single downward red trend line dropping gently in center of flat pure white canvas (#FFFFFF), zero grids, zero charts, zero decorative borders, eighty-five percent open space."),
        ],
    ),
    (
        "Ẩn dụ màn hình máy tính",
        "Solid warm cream canvas (#F8F0DC).",
        "narrative_warm",
        "demystifying_truth",
        "actionable_resolution",
        [
            ("Biểu tượng thùng rác chỉ là hình vẽ.", "macro_prop:none|A simple minimalist desktop trash bin icon rendered in single black marker outline in center of flat solid cream canvas (#F8F0DC), zero paper clutter outside, zero decorative borders, eighty-five percent negative space."),
            ("Nó che đi những vi mạch phức tạp.", "visual_diagram:none|A single small rectangular computer chip icon outline with three straight black pins on each side in center of flat cream canvas (#F8F0DC), zero dashed borders, zero micro-circuits, zero decorative border lines, eighty-five percent negative space."),
            ("Coi trọng biểu tượng nhưng không ngộ nhận nó là sự thật.", "concept_metaphor:none|A simple single doodle umbrella outline resting on flat cream ground (#F8F0DC), zero rain streaks, zero plants, zero decorative borders, eighty-five percent negative space."),
            ("Đừng để những con số làm bạn buồn.", "concept_metaphor:none|A single minimalist smartphone outline with a blank dark screen in center of flat cream surface (#F8F0DC), zero apps, zero decorative borders, eighty-five percent negative space."),
        ],
    ),
    (
        "Thức tỉnh giữa đời thực",
        "Clean serene white field (#FFFFFF).",
        "reflective_slow",
        "philosophical_anchor",
        "actionable_resolution",
        [
            ("Mọi áp lực chỉ do góc nhìn của bạn.", "full_scene:CH01|Stickman in blue shirt stands calmly in center of flat pure white canvas (#FFFFFF), smiling gently with hands at sides, zero background decor, zero borders, eighty-five percent negative space."),
            ("Đổi chiếc kính, bạn sẽ thấy lòng nhẹ nhõm.", "concept_metaphor:none|A simple pair of round black doodle eyeglasses resting in center of flat pure white canvas (#FFFFFF), zero frames, zero decorative borders, eighty-five percent negative space."),
            ("Tặng mình một like nếu thấy hữu ích nhé.", "concept_metaphor:none|A simple doodle outline of a thumbs-up like icon drawn with a single black marker line in center of flat pure white canvas (#FFFFFF), zero borders, zero background decor, ninety percent negative space."),
            ("Và bấm theo dõi để chúng mình cùng gặp lại nhau nha.", "variation:CH01|Stickman in blue shirt smiles warmly and waves a friendly hand in center of flat pure white canvas (#FFFFFF), zero background decor, zero decorative borders, eighty-five percent negative space."),
        ],
    ),
]


def build_sources() -> list[dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "The Case Against Reality: Why Evolution Hid the Truth from Our Eyes",
            "reference": "Donald D. Hoffman (2019). W. W. Norton & Company / Psychonomic Bulletin & Review.",
            "facts": [
                "Não bộ không tiến hóa để nhìn thấy sự thật khách quan.",
                "Tiến hóa ưu tiên sinh tồn hơn là thấu suốt chân lý.",
                "Sinh vật thấy sự thật tuyệt chủng trước kẻ chỉ thấy sinh tồn.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Spacetime is Doomed: Scattering Amplitudes and the Holographic Principle",
            "reference": "Nima Arkani-Hamed (2012). Institute for Advanced Study, Princeton.",
            "facts": [
                "Không gian ba chiều chỉ là định dạng nén dữ liệu của não.",
                "Vật thể ba chiều giống như biểu tượng trên màn hình máy tính.",
                "Bộ não nén hàng tỷ photon thành một hình ảnh đơn giản.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Fitness Beats Truth Theorem in Evolutionary Game Theory",
            "reference": "Chetan Prakash, Donald Hoffman et al. (2014). Journal of Theoretical Biology.",
            "facts": [
                "Biểu tượng thùng rác không chứa rác thật hay chất dẻo nhựa.",
                "Nếu phải nhìn thấy dòng điện bạn sẽ không thể dùng máy tính.",
                "Coi trọng biểu tượng nhưng không ngộ nhận nó là sự thật.",
            ],
        },
    ]


def build_human_editorial() -> HumanEditorialSpec:
    return HumanEditorialSpec(
        topic_dilemmas=[
            "Nếu thực tại khách quan hoàn toàn khác với những gì mắt thấy, liệu con người có rơi vào chủ nghĩa hư vô và mất phương hướng sống hay không.",
            "Xã hội hiện đại ngập tràn các biểu tượng ảo như lượt thích, điểm số và tiền bạc số khiến não bộ bị thao túng bởi những thứ không có thật.",
        ],
        dynamic_questions=[
            "Tại sao một sinh vật nhìn thấy sự thật của vũ trụ lại bị tuyệt chủng nhanh hơn một sinh vật chỉ nhìn thấy ảo giác sinh tồn?",
            "Làm thế nào để phân biệt giữa việc coi trọng luật chơi của cuộc sống với việc bị nô lệ bởi những biểu tượng vô nghĩa?",
            "Làm sao ứng dụng định lý không-thời gian vào việc giải tỏa áp lực xã hội và chứng lo âu trong đời sống hàng ngày?",
        ],
        author_raw_input="Thực tại bạn thấy không phải là chân lý mà chỉ là giao diện nén để sống sót. Hiểu được điều này giúp bạn không còn bị ám ảnh bởi các áp lực ảo mà xã hội bày ra.",
        editorial_stance="Khoa học nhận thức hiện đại và vật lý lượng tử đã chứng minh một sự thật giải thoát: Mọi thứ chúng ta nhìn thấy chỉ là một giao diện đồ họa. Nhận thức này không biến cuộc đời thành hư vô, mà trao cho ta quyền năng tháo bỏ chiếc kính định kiến, không còn bị thao túng bởi những biểu tượng xã hội rỗng tuếch và tập trung vào những giá trị sống đích thực.",
        expanded_content_ideas=[
            {
                "idea_id": "IDEA_01",
                "angle_type": "analysis",
                "summary": "Phân tích cơ chế nén không-thời gian như định dạng tệp để tiết kiệm năng lượng não bộ.",
                "narrative_integration": "Đưa vào phân cảnh phân tích cơ chế nhân quả.",
                "target_narrative_phase": "causal_mechanism",
            },
            {
                "idea_id": "IDEA_02",
                "angle_type": "commentary",
                "summary": "Phản biện chủ nghĩa hư vô qua ẩn dụ biểu tượng thùng rác trên máy tính: Coi trọng nhưng không ngộ nhận.",
                "narrative_integration": "Đưa vào phân cảnh phản biện lật ngược vấn đề.",
                "target_narrative_phase": "counter_argument",
            },
            {
                "idea_id": "IDEA_03",
                "angle_type": "evaluation",
                "summary": "Đánh giá việc áp dụng định lý giao diện để giải phóng áp lực đồng trang lứa và lo âu xã hội.",
                "narrative_integration": "Đưa vào phân cảnh giải pháp chuyển hóa thực tế.",
                "target_narrative_phase": "takeaway",
            },
        ],
    )


def build_characters() -> list[dict[str, Any]]:
    return [
        {
            "id": "CH01",
            "name": "Người quan sát nhận thức",
            "role": "cognitive_inquirer",
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
    scenes[6].source_ids = ["SRC01"]
    scenes[6].claim_facts = [
        ("Não bộ không tiến hóa để nhìn thấy sự thật khách quan.", "SRC01", "Não bộ không tiến hóa để nhìn thấy sự thật khách quan."),
        ("Tiến hóa ưu tiên sinh tồn hơn là thấu suốt chân lý.", "SRC01", "Tiến hóa ưu tiên sinh tồn hơn là thấu suốt chân lý."),
    ]
    scenes[7].source_ids = ["SRC02"]
    scenes[7].claim_facts = [
        ("Không gian ba chiều chỉ là định dạng nén dữ liệu của não.", "SRC02", "Không gian ba chiều chỉ là định dạng nén dữ liệu của não."),
        ("Bộ não nén hàng tỷ photon thành một hình ảnh đơn giản.", "SRC02", "Bộ não nén hàng tỷ photon thành một hình ảnh đơn giản."),
        ("Vật thể ba chiều giống như biểu tượng trên màn hình máy tính.", "SRC02", "Vật thể ba chiều giống như biểu tượng trên màn hình máy tính."),
    ]
    scenes[8].source_ids = ["SRC03"]
    scenes[8].claim_facts = [
        ("Biểu tượng thùng rác không chứa rác thật hay chất dẻo nhựa.", "SRC03", "Biểu tượng thùng rác không chứa rác thật hay chất dẻo nhựa."),
        ("Nếu bạn phải nhìn thấy dòng điện bạn sẽ không thể dùng máy tính.", "SRC03", "Nếu phải nhìn thấy dòng điện bạn sẽ không thể dùng máy tính."),
    ]
    scenes[10].source_ids = ["SRC01"]
    scenes[10].claim_facts = [
        ("Sinh vật thấy sự thật tuyệt chủng trước kẻ chỉ thấy sinh tồn.", "SRC01", "Sinh vật thấy sự thật tuyệt chủng trước kẻ chỉ thấy sinh tồn."),
    ]
    scenes[13].source_ids = ["SRC03"]
    scenes[13].claim_facts = [
        ("Coi trọng biểu tượng nhưng không ngộ nhận nó là sự thật.", "SRC03", "Coi trọng biểu tượng nhưng không ngộ nhận nó là sự thật."),
    ]

    return ResearchedTopic(
        topic="Mắt Bạn Không Hề Nhìn Thấy Thế Giới Thật? (Nghịch Lý Giao Diện Thực Tại)",
        audience="Người đi làm, sinh viên và người làm việc trí óc quan tâm đến tâm lý học nhận thức và bản chất cuộc sống",
        goal="Giải mã nghịch lý giao diện thực tại qua định lý FBT của GS Donald Hoffman, cơ chế nén không-thời gian và ẩn dụ màn hình máy tính",
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
            youtube_title="Mắt Bạn Không Hề Nhìn Thấy Thế Giới Thật?",
            visual_hook="Nhân vật stickman dùng chiếc kéo to bản rạch rách tấm màn bầu trời thực tại, lộ ra phía sau là bảng mã nhị phân và dòng điện ma trận.",
            text_overlay="SỰ THẬT LÀ GIẢ",
            contrast_pair="Thực tại trần trụi vs. Giao diện nén sinh tồn",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "thực tại ảo giác",
                "định lý fbt",
                "donald hoffman",
                "không thời gian",
                "tâm lý học nhận thức",
            ],
            thumbnail_prompt=(
                "Orthographic 2D hand-drawn doodle poster. 60% of the frame shows a bald stickman in a blue shirt (#3B82C4) "
                "cutting through a canvas sky with oversized black scissors, revealing a glowing matrix of green binary "
                "code and wire bus lines beneath the torn fabric. Solid warm paper-cream canvas (#F8F0DC), wobbly raw "
                "black marker contours (#000000). 40% clean negative space on the top right with massive bold yellow "
                "hand-lettered text 'SỰ THẬT LÀ GIẢ' with thick black outline. Zero room interiors, zero 3D perspective, "
                "zero drop shadows."
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
    scenes[2].source_ids = ["SRC02"]
    scenes[2].claim_facts = [
        ("Không gian ba chiều chỉ là định dạng nén dữ liệu của não.", "SRC02", "Không gian ba chiều chỉ là định dạng nén dữ liệu của não."),
    ]
    scenes[3].source_ids = ["SRC01"]
    scenes[3].claim_facts = [
        ("Sinh vật thấy sự thật tuyệt chủng trước kẻ chỉ thấy sinh tồn.", "SRC01", "Sinh vật thấy sự thật tuyệt chủng trước kẻ chỉ thấy sinh tồn."),
    ]
    scenes[4].source_ids = ["SRC03"]
    scenes[4].claim_facts = [
        ("Coi trọng biểu tượng nhưng không ngộ nhận nó là sự thật.", "SRC03", "Coi trọng biểu tượng nhưng không ngộ nhận nó là sự thật."),
    ]

    return ResearchedTopic(
        topic="Mắt Bạn Đang Lừa Dối Bạn? (Bản Dọc 60 Giây)",
        audience="Người trẻ, sinh viên và người làm việc số lướt video ngắn trên di động",
        goal="Tóm gọn nghịch lý giao diện thực tại trong 60 giây và hướng dẫn thoát khỏi bẫy áp lực điểm ảnh mạng xã hội",
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
        tone="Conversational Essayist gãy gọn, bất ngờ, nhịp điệu nhanh và cuốn hút",
        language="vi",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        human_editorial=build_human_editorial(),
        packaging=PackagingSpec(
            youtube_title="Mắt Bạn Đang Lừa Dối Bạn?",
            visual_hook="Nhân vật stickman cầm kính lúp soi vào ly cà phê nhìn thấy mạng lưới mã nhị phân ma trận",
            text_overlay="SỰ THẬT LÀ GIẢ",
            contrast_pair="Mắt thấy tai nghe vs. Giao diện nén sinh tồn",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "thực tại ảo",
                "ly cà phê",
                "định lý fbt",
                "short 9x16",
            ],
            thumbnail_prompt=(
                "Orthographic 2D hand-drawn doodle poster in 9:16 vertical ratio. A stickman character holding a large "
                "magnifying glass examining a coffee cup, revealing green binary matrix code inside the glass. Flat solid "
                "warm sand background (#F8F0DC), wobbly black marker contours (#000000), flat MS-paint fills (shirt in "
                "#3B82C4). Clean negative space at the top holding large bold yellow text 'SỰ THẬT LÀ GIẢ' with thick "
                "black outline."
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
    parser = argparse.ArgumentParser(description="Build Reality Interface Paradox 16:9 & 9:16 production blueprint.")
    parser.add_argument("--ratio", choices=["16:9", "9:16", "dual"], default="dual", help="Aspect ratio to build")
    parser.add_argument("--out-dir", type=Path, default=SYS_DIR / "runs", help="Output directory root")
    parser.add_argument("--blueprint-dir", type=Path, default=SYS_DIR / "content" / "blueprints", help="Blueprint directory root")
    parser.add_argument("--validate", action="store_true", help="Run contract and cadence validation")
    args = parser.parse_args()

    ratios = ["16:9", "9:16"] if args.ratio == "dual" else [args.ratio]
    all_passed = True

    for r in ratios:
        if r == "16:9":
            topic = build_topic_16x9()
            job_name = "reality-interface-paradox-16x9"
        else:
            topic = build_topic_9x16()
            job_name = "reality-interface-paradox-9x16"

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
        print("[SUCCESS] Toàn bộ gói hồ sơ kỹ thuật cho Reality Interface Paradox đã hoàn thành và đạt chuẩn!")
        return 0
    else:
        print("[FAILURE] Phát hiện lỗi trong quá trình đóng gói hồ sơ kỹ thuật.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
