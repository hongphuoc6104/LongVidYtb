#!/usr/bin/env python3
"""Build production-ready packages for Stress Trap Paradox (16:9 Landscape & 9:16 Portrait).

Pillar: "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức" (tier_1_broad)
Core Topic: "Càng Cố 'Xả Stress', Não Bạn Càng Bị Hút Cạn? (Nghịch Lý Chai Sạn Kích Thích)"
Experiments & Theories:
  - James Olds & Peter Milner (1954): Electrical stimulation in brain reward circuits of rats
  - Roy A. Wise (2004) & Nora Volkow (2011): Dopamine wanting vs liking, D2 receptor downregulation
  - Anna Lembke (2021) "Dopamine Nation": Pleasure-pain balance and high-friction dopamine reset

Formats:
  - stress-trap-paradox-16x9: 18 scenes, 8-part narrative arc landscape explainer (>= 1,800 syl)
  - stress-trap-paradox-9x16: 6 scenes, 60-second vertical mobile short explainer
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
# Each spoken sentence is <= 20 syllables.
# Abstract cards (white_card, concept_metaphor, visual_diagram) max 2 in a row.
# Tone in {narrative_warm, analytical_crisp, reflective_slow}.
# Syllables >= 1800 across 18 scenes (~105 syl / scene).
# ---------------------------------------------------------------------------
STORY_16X9: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    # STAGE 1: hook (Scenes 1-2)
    (
        "Cú tát chiếc điện thoại đêm khuya",
        "Solid warm cream canvas (#F8F0DC).",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Bạn không hề lướt điện thoại để thư giãn.", "full_scene:CH01|Stickman lies on mattress holding flat phone with quiet gaze on pure cream canvas with 85% negative space."),
            ("Mỗi buổi tối khi công việc khép lại.", "concept_metaphor:none|A small square digital desk clock showing 23:00 drawn in thin black line on clean cream canvas."),
            ("Bạn leo lên giường với mong muốn xả hơi.", "variation:CH01|Stickman pulls up simple blanket and rests head on flat pillow on clean cream canvas."),
            ("Bạn tự nhủ chỉ xem vài đoạn phim ngắn thôi.", "still_life:none|A plain small flat pillow resting alone in wide empty space on clean cream canvas."),
            ("Một thước phim vui lướt qua ngón tay bạn.", "variation:CH01|Stickman taps flat phone screen lightly, smiling faintly on solid clean cream canvas."),
            ("Cảm giác dễ chịu lập tức ùa tới.", "macro_prop:none|A flat minimalist rectangular glass smartphone sitting silent and dark on solid warm cream canvas."),
            ("Bạn mỉm cười và tiếp tục chạm vào màn hình.", "variation:CH01|Stickman smiles softly with relaxed shoulders on solid clean cream canvas."),
            ("Bạn tin rằng não mình đang được nghỉ ngơi.", "full_scene:CH01|Stickman gazes at flat phone rectangle with relaxed posture on solid clean cream canvas."),
            ("Nhưng thực chất một cái bẫy đã sập xuống.", "still_life:none|A simple minimalist steel wire loop resting silently on paper-cream floor with wide space."),
            ("Tâm trí bạn bắt đầu bị cuốn vào guồng quay mới.", "concept_metaphor:none|A tiny solitary ceramic teacup drawn in thin black line on clean cream canvas."),
        ],
    ),
    (
        "Vòng xoáy năm phút thành hai giờ sáng",
        "Clean pure white background (#FFFFFF).",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Thời gian bắt đầu trôi đi không dấu vết.", "full_scene:CH01|Stickman sits slightly propped up against wall swiping phone continuously with steady rhythm."),
            ("Từ năm phút ban đầu biến thành ba mươi phút.", "concept_metaphor:none|A small plain square digital clock showing numbers zero zero three zero on cream canvas."),
            ("Rồi kim đồng hồ chỉ đúng hai giờ sáng.", "still_life:none|A simple hand-drawn analog clock showing two o'clock on flat clean white canvas with 85% negative space."),
            ("Bạn đã lướt qua hàng trăm mẩu tin ngắn.", "variation:CH01|Stickman blinks rapidly while fingers continue flicking upward over the glass screen."),
            ("Bạn không còn nhớ nội dung đầu tiên là gì.", "full_scene:CH01|Stickman pauses swipe gesture, staring forward into open cream space with empty eyes."),
            ("Ngón tay vẫn tiếp tục vuốt theo quán tính.", "macro_prop:none|A close view of stickman thumb hovering over flat phone edge in pure black marker outline on white."),
            ("Một vòng lặp vô hình giam giữ tâm trí bạn.", "visual_diagram:none|A simple straight horizontal black divider line centered on solid cream ground with wide margins."),
            ("Mỗi mẩu video đều hứa hẹn một điều thú vị.", "concept_metaphor:none|A simple question mark doodle hovering over a small black rectangle on flat white canvas."),
            ("Càng lướt bạn lại càng không thể dừng lại.", "full_scene:CH01|Stickman clutches flat phone with two hands, staring quietly with fixed motionless posture on white canvas."),
            ("Căn phòng tối dần và mắt bạn mỏi nhừ.", "still_life:none|A single clear glass cup drawn in thin black marker outline on pure white canvas."),
        ],
    ),

    # STAGE 2: lead_in (Scenes 3-4)
    (
        "Cảm giác trống rỗng và não kiệt quệ",
        "Solid ivory neutral field (#F8F0DC).",
        "analytical_crisp",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Khi bạn buông điện thoại xuống đệm.", "full_scene:CH01|Stickman places phone face down on blanket and rubs tired eyes with open palms."),
            ("Cảm giác đầu tiên không phải là sảng khoái.", "concept_metaphor:none|A plain flat mattress with simple unwrinkled sheet resting peacefully in wide clean ivory field."),
            ("Đôi mắt bạn cay xè vì ánh sáng xanh.", "macro_prop:none|A simple folded pair of spectacles drawn in thin black outline on white surface."),
            ("Đầu bạn thì nặng trĩu và mỏi nhừ.", "variation:CH01|Stickman presses two index fingers gently against temples with furrowed brow on white field."),
            ("Lồng ngực bạn dâng lên một nỗi bất an lạ kỳ.", "concept_metaphor:none|A single dry fallen leaf resting motionless on clear white negative space without clutter."),
            ("Đó là cảm giác trống rỗng và tội lỗi mơ hồ.", "full_scene:CH01|Stickman curls knees up slightly on mattress, looking into empty space with reflective eyes."),
            ("Bạn đã tiêu tốn ba tiếng đồng hồ quý giá.", "macro_prop:none|A minimalist pocket watch drawn in pure black marker outline on white surface."),
            ("Đầu óc lúc này trống rỗng, không muốn nghĩ ngợi gì nữa.", "variation:CH01|Stickman leans head back against wall with vacant expression and completely limp hands."),
            ("Bạn thấy người mệt lả đi, chẳng còn chút sức lực nào.", "visual_diagram:none|A single vertical tick mark etched in black marker centered on stark white canvas with wide margins."),
            ("Càng cố nằm nghỉ, bạn lại càng thấy mệt mỏi hơn.", "still_life:none|A solitary white pillow resting on pristine flat canvas with seventy percent breathing space."),
        ],
    ),
    (
        "Ảo tưởng về hành vi thư giãn xả stress",
        "Pure stark white field (#FFFFFF).",
        "analytical_crisp",
        "demystifying_truth",
        "empirical_conflict",
        [
            ("Tại sao hành động không tốn sức lại làm ta kiệt quệ?", "full_scene:CH01|Stickman stands in open ivory space gesturing with questioning hands in philosophical inquiry."),
            ("Chúng ta ngỡ rằng ngồi yên là đang nghỉ ngơi.", "variation:CH01|Stickman sits on a simple unshaded chair drawn in black line with arms crossed on ivory ground."),
            ("Bạn không chạy bộ và không giải toán phức tạp.", "concept_metaphor:none|A simple running shoe drawn in thin black line outline on clean white canvas."),
            ("Bạn chỉ nằm lướt nhẹ trên màn hình phẳng.", "macro_prop:none|A simple flat smartphone rectangle with a curved black arrow on solid ivory surface."),
            ("Đúng là chân tay bạn được nằm yên thật.", "concept_metaphor:none|A simple pair of loose stickman wire arms resting flat on pure stark white field."),
            ("Nhưng trong đầu bạn, mọi thứ vẫn đang quay cuồng.", "full_scene:CH01|Stickman presses fingertips firmly to temples with closed strained eyes on pure stark white field."),
            ("Não bạn thực ra đang phải làm việc cật lực.", "visual_diagram:none|A simple clean black outline silhouette of a resting head on stark white canvas."),
            ("Nó phải liên tục lọc các luồng thông tin rời rạc.", "concept_metaphor:none|A tiny ceramic vessel drawn in thin black line resting on flat ivory ground."),
            ("Cứ mỗi video lướt qua, mắt lại phải nhìn, đầu lại phải xử lý.", "variation:CH01|Stickman turns head swiftly from left to right as if dodging invisible projectiles."),
            ("Thế thì đâu phải nghỉ ngơi, rõ ràng là mình đang tự vắt kiệt mình.", "full_scene:CH01|Stickman rests forehead down flat on bare table outline with arms wrapped over head."),
        ],
    ),

    # STAGE 3: problem (Scenes 5-6)
    (
        "Thí nghiệm con chuột và chiếc cần gạt",
        "Solid warm cream canvas (#F8F0DC).",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Năm một chín năm tư, có một thí nghiệm rất nổi tiếng.", "full_scene:CH01|Stickman stands beside a simple plain table outline drawn in black line on white."),
            ("Các nhà khoa học gắn một nút bấm nhỏ vào đầu con chuột.", "visual_diagram:none|A simple hand-drawn brain outline with a single line pointer drawn in black marker on white."),
            ("Nút bấm này được nối với một chiếc cần gạt nhỏ.", "macro_prop:none|A minimalist steel lever attached to a metal box outline in thin black line on white."),
            ("Mỗi khi con chuột ấn chân vào chiếc cần.", "full_scene:CH01|Stickman leans forward observing a tiny mouse silhouette touching a metal switch."),
            ("Mỗi lần chạm vào cần gạt, nó sẽ nhận được một kích thích nhỏ.", "visual_diagram:none|A single straight black wire connecting two simple plain circular dots on clean white canvas."),
            ("Ban đầu người ta nghĩ đây là vùng thỏa mãn.", "concept_metaphor:none|A simple circle with a plus sign drawn in black marker on clean cream canvas."),
            ("Họ muốn xem liệu con chuột có thích cảm giác đó không.", "variation:CH01|Stickman stands upright holding an open clip-board with focused scientific gaze."),
            ("Con vật lập tức thay đổi hành vi kỳ lạ.", "macro_prop:none|A simple observation bowl outline drawn in thin black marker on white."),
            ("Và phản ứng của nó khiến mọi người sững sờ.", "full_scene:CH01|Stickman observes a simple transparent glass box outline with solemn eyes on white ground."),
            ("Và họ phát hiện ra một điều rất bất ngờ.", "still_life:none|A clean open notebook with two simple horizontal lines on white canvas."),
        ],
    ),
    (
        "Chiếc cần gạt tự hủy hai nghìn lần mỗi giờ",
        "Clean pure white background (#FFFFFF).",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Con chuột bắt đầu nhấn cần gạt liên tục.", "full_scene:CH01|Stickman watches a small agile mouse pressing a metal lever repeatedly with urgency."),
            ("Nó bấm tới hai nghìn lần trong mỗi giờ.", "still_life:none|A tiny crude cartoon rat pressing a simple black lever repeatedly on white background."),
            ("Nó từ chối ăn những mẩu bánh thơm ngon.", "macro_prop:none|A simple empty bowl drawn in black outline beside the lever on clean canvas."),
            ("Nó phớt lờ cả máng nước dù đang khát khô.", "full_scene:CH01|Stickman points toward an untouched water dropper beside the frantic animal."),
            ("Người ta thử đặt một vật cản gây đau đớn.", "visual_diagram:none|A single solid straight black boundary line cutting cleanly across flat white paper ground."),
            ("Nhưng con chuột vẫn bước qua để bấm cần.", "variation:CH01|Stickman shakes head in solemn disbelief, arms held steady at sides on cream canvas."),
            ("Dù bị đau, con chuột vẫn cố lết tới để bấm tiếp.", "concept_metaphor:none|A single plain wooden stick resting firmly upright against eighty percent white background."),
            ("Nó bấm liên tục cho đến khi kiệt sức ngã gục.", "still_life:none|The metal lever sitting completely still and untouched under clean white canvas."),
            ("Cơn thèm bấm cần đã át đi cả cảm giác đói khát tự nhiên.", "full_scene:CH01|Stickman steps back slowly with solemn empathetic expression on clean white ground."),
            ("Nhìn lại, ta thấy mình lướt điện thoại cũng y hệt như vậy.", "still_life:none|A single dried autumn leaf resting quietly on immaculate paper floor."),
        ],
    ),

    # STAGE 4: causal_mechanism (Scenes 7-9)
    (
        "Cú lật bản chất Dopamine là khao khát",
        "Solid ivory neutral field (#F8F0DC).",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Về sau, người ta mới hiểu rõ chuyện gì đã xảy ra.", "full_scene:CH01|Stickman unrolls a large clean scroll outline across white backdrop with calm poise."),
            ("Nút bấm đó không hề chạm vào cảm giác thỏa mãn.", "concept_metaphor:none|A simple hand-drawn empty plate with a fork beside it on solid ivory neutral field."),
            ("Con chuột không hề cảm thấy hạnh phúc hay no đủ.", "variation:CH01|Stickman shakes head gently with clear demystifying posture on pristine white."),
            ("Nút bấm đó kích hoạt đúng một chất gọi là dopamine.", "visual_diagram:none|A single clean straight black arrow pointing forward across eighty percent empty field."),
            ("Dopamine không phải là phần thưởng của sự thỏa mãn.", "concept_metaphor:none|A single curved black arrow chasing its own tail in a circle on ivory neutral field."),
            ("Chất này không tạo ra niềm vui, nó chỉ gây cảm giác thèm muốn.", "full_scene:CH01|Stickman extends an open reaching hand toward an abstract light point on white ground."),
            ("Nó tạo ra sự tò mò và cảm giác muốn xem tiếp.", "concept_metaphor:none|A dynamic arrow stretching perpetually toward an unreachable shimmering target dot."),
            ("Nó thôi thúc hành động nhưng không mang lại niềm vui.", "variation:CH01|Stickman lowers outstretched palm, looking down at empty fingers with deep realization."),
            ("Thế nên bạn cứ bị cuốn đi, muốn xem mãi không dừng được.", "visual_diagram:none|A simple straight vertical column outline centered on pristine white canvas."),
            ("Và cái cảm giác thỏa mãn thực sự không bao giờ tới.", "still_life:none|A simple wooden compass with needle spinning without settling on pristine white field."),
        ],
    ),
    (
        "Dopamine không mang lại cảm giác thỏa mãn",
        "Pure stark white field (#FFFFFF).",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Hãy phân biệt rõ giữa cảm giác muốn và niềm vui thực sự.", "full_scene:CH01|Stickman stands in center dividing ivory space with two open balanced palms."),
            ("Đầu óc chúng ta chia hai cảm giác này rất rạch ròi.", "visual_diagram:none|Two distinct parallel vertical tracks: left labeled KHAO KHÁT, right labeled TẬN HƯỞNG."),
            ("Cảm giác nôn nóng muốn xem tiếp do dopamine thúc đẩy.", "concept_metaphor:none|A simple tiny flame icon drawn in single black marker stroke on ivory canvas."),
            ("Nó khiến bạn sốt ruột muốn bấm vào cái tiếp theo.", "variation:CH01|Stickman leans forward with eager posture, looking toward next invisible horizon."),
            ("Còn niềm vui bình yên thực sự lại cần điều khác.", "full_scene:CH01|Stickman points toward a calm serene blue circle outline hovering peacefully in space."),
            ("Niềm vui êm dịu, nhẹ nhõm đến từ một cơ chế hoàn toàn khác.", "visual_diagram:none|Two small identical black squares placed side by side with wide empty space on white field."),
            ("Khi bạn lướt mạng, mắt bạn liên tục nhận những đợt rung hồi hộp.", "macro_prop:none|A single flat dark smartphone screen resting flat on stark white canvas with zero emission."),
            ("Cảm giác bình yên trong tâm trí hoàn toàn bị bỏ quên.", "still_life:none|An empty ceramic bowl sitting alone with eighty percent open space on white field."),
            ("Càng xem nhiều, bạn lại càng thấy thiếu thốn.", "variation:CH01|Stickman presses hand against chest, breathing slowly with reflective insight."),
            ("Chính vì thế, đêm nào buông máy bạn cũng thấy hụt hẫng.", "still_life:none|An empty ceramic bowl resting quietly in center of frame with seventy percent breathing space."),
        ],
    ),
    (
        "Phân tử lừa dối và động lực truy cầu",
        "Solid warm cream canvas (#F8F0DC).",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Chiếc điện thoại thông minh chính là chiếc cần gạt.", "full_scene:CH01|Stickman holds smartphone vertically, side by side with a miniature laboratory lever."),
            ("Mỗi cái vuốt ngón tay là một lần nhấn cần.", "concept_metaphor:none|A minimalist phone screen with swipe gesture transforming into an old mechanical lever pull."),
            ("Các đoạn video được xếp đặt hệt như máy quay số.", "visual_diagram:none|A plain vertical card divided into three empty rectangular sections on white ground."),
            ("Bạn không biết video tiếp theo sẽ có gì hay.", "full_scene:CH01|Stickman tilts head with curious expression, glancing into flat mobile screen."),
            ("Chính sự bất ngờ đó khiến đầu óc bạn bị kích thích mạnh nhất.", "visual_diagram:none|A spiked fluctuating line graph leaping upward unpredictably against zero baseline."),
            ("Bạn luôn tin rằng điều thú vị đang chờ phía trước.", "concept_metaphor:none|A simple closed box doodle with a question mark above it on solid warm cream canvas."),
            ("Bạn tự nhủ chỉ cần vuốt thêm một cái nữa thôi.", "macro_prop:none|A clean minimal graphic showing a single curved upward arrow labeled VUỐT TIẾP."),
            ("Bạn bị cuốn vào chiếc máy lúc nào không hay.", "variation:CH01|Stickman looks up from device with sudden shock of awareness in clear eyes."),
            ("Các ứng dụng được thiết kế rất khéo để giữ chân bạn.", "concept_metaphor:none|A clean minimalist silhouette of a resting hand on ivory paper background."),
            ("Và chúng ta cứ thế dán mắt vào màn hình lúc nào không hay.", "full_scene:CH01|Stickman stands tall looking forward with sudden deep insight and self-awareness."),
        ],
    ),

    # STAGE 5: explanation (Scenes 10-12)
    (
        "Cơ chế suy giảm thụ thể Dopamine D2",
        "Clean pure white background (#FFFFFF).",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Nhưng đổi lại, cơ thể chúng ta phải chịu một cái giá rất lớn.", "full_scene:CH01|Stickman stands beside a tall explanatory balance scale on solid warm cream canvas."),
            ("Đầu óc con người rất sợ bị quá tải.", "concept_metaphor:none|A delicate seesaw scale tilting violently to one side under sudden heavy weight block."),
            ("Khi các luồng hình ảnh ập đến quá nhanh và dồn dập.", "visual_diagram:none|A simple clear glass cup with plain water surface resting on clean white ground."),
            ("Não coi đó là một sự căng thẳng quá mức.", "full_scene:CH01|Stickman shields eyes with one wire arm from visual clutter on clean white background."),
            ("Để tự bảo vệ, não tự động giảm bớt độ nhạy cảm.", "visual_diagram:none|A single plain horizontal bar resting firmly closed on clean cream ground."),
            ("Hiện tượng này khiến bạn dần bị chai lì cảm xúc.", "concept_metaphor:none|A simple closed wooden door panel drawn in thin black line on white background."),
            ("Khả năng cảm nhận niềm vui đơn giản bị thu hẹp.", "macro_prop:none|A clean minimal brass latch resting in horizontal locked position on smooth wood."),
            ("Đầu óc bạn bắt đầu trở nên trơ lì trước mọi thứ.", "variation:CH01|Stickman inspects a locked wooden doorway with thoughtful analytical focus on cream."),
            ("Lần sau, bạn lại phải lướt nhiều hơn thì mới thấy bớt chán.", "visual_diagram:none|A clean vertical measuring line with two level marks on pure white background."),
            ("Và niềm hứng khởi giản dị cứ thế tan biến mất.", "still_life:none|A dry smooth river stone resting peacefully on warm paper-cream floor with wide margin."),
        ],
    ),
    (
        "Vực thẳm của đường đáy baseline cảm xúc",
        "Solid ivory neutral field (#F8F0DC).",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Độ nhạy cảm xúc của bạn giảm đi từng ngày.", "full_scene:CH01|Stickman walks slowly across stark white ground with hands deep in pockets."),
            ("Bình thường, tâm trí ai cũng có một điểm tựa an lành.", "visual_diagram:none|A steady horizontal dotted black line labeled VẠCH CHUẨN TỰ NHIÊN running across white."),
            ("Mức độ này giúp ta an yên dù chỉ ngồi tĩnh lặng.", "concept_metaphor:none|A gentle leaf floating calmly on still water surface with eighty percent white void."),
            ("Nhưng sau hàng giờ lướt những video vô bổ.", "full_scene:CH01|Stickman stops in tracks, looking down at a steep downward canyon in the floor."),
            ("Ngưỡng vui vẻ tự nhiên của bạn bị kéo tụt xuống rất thấp.", "visual_diagram:none|A downward plunging red arrow penetrating deep below the dotted equilibrium level."),
            ("Khi buông điện thoại ra, bạn rơi vào hẫng hụt.", "macro_prop:none|A single empty dark phone screen resting flat on ivory canvas with eighty percent negative space."),
            ("Những việc bình thường bỗng trở nên nhàm chán lạ kỳ.", "macro_prop:none|An open paper notebook and pencil sitting lonely under harsh white light."),
            ("Đọc vài trang sách cũng thấy sốt ruột không yên.", "variation:CH01|Stickman glances toward an open paper book with restless and distracted expression."),
            ("Cảm giác bứt rứt và bồn chồn cứ thế dâng lên.", "concept_metaphor:none|A solitary small stone resting silently in the center of pristine white canvas."),
            ("Cảm giác đó xuất hiện ngay khi bạn vừa rời mắt khỏi màn hình.", "full_scene:CH01|Stickman stands in open space, holding own wrists with quiet empathetic awareness."),
        ],
    ),
    (
        "Nghịch lý chiếc bập bênh khoái cảm nỗi đau",
        "Pure stark white field (#FFFFFF).",
        "analytical_crisp",
        "demystifying_truth",
        "empirical_conflict",
        [
            ("Cảm xúc của chúng ta hoạt động giống như một chiếc bập bênh.", "full_scene:CH01|Stickman gestures toward a large minimalist seesaw balanced precisely in center."),
            ("Niềm vui và nỗi buồn luôn đi liền với nhau.", "visual_diagram:none|A simple seesaw outline drawn in black marker line on pure stark white field."),
            ("Khi bạn nhấn mạnh vào bên vui vẻ bằng những video ngắn.", "macro_prop:none|A flat black smartphone dropping onto left side of a simple seesaw on white field."),
            ("Não lập tức kéo cảm xúc chùng xuống để cân bằng.", "visual_diagram:none|Small heavy counterweights labeled ĐỐI KHÁNG jumping onto the opposing scale arm."),
            ("Khi bạn buông điện thoại, niềm vui đó biến mất ngay.", "full_scene:CH01|Stickman steps back as the phone weight vanishes into thin air on ivory ground."),
            ("Chỉ còn lại cảm giác nặng nề đè xuống tâm trí.", "concept_metaphor:none|A small solid black weight circle landing softly on the right side of seesaw on white field."),
            ("Đầu óc bạn lệch hẳn về phía mệt mỏi và âu lo.", "variation:CH01|Stickman looks solemnly at the steeply tilted beam with analytical understanding."),
            ("Đó là lý do bạn thấy kiệt sức sau khi tưởng mình đang thư giãn.", "concept_metaphor:none|A simple seesaw tilted down sharply on the right side on pure stark white field."),
            ("Bạn không hề nạp thêm năng lượng nào cho cơ thể.", "full_scene:CH01|Stickman spreads hands wide, showing completely empty palms to the viewer."),
            ("Thực chất bạn đang tiêu trước năng lượng của ngày hôm sau.", "still_life:none|An antique brass balance scale resting motionless in wide negative space."),
        ],
    ),

    # STAGE 6: counter_argument (Scenes 13-14)
    (
        "Bẫy cai nghiện bằng kỷ luật sắt cực đoan",
        "Solid warm cream canvas (#F8F0DC).",
        "reflective_slow",
        "critical_rebuttal",
        "actionable_resolution",
        [
            ("Nhiều người nhận ra điều này và cố ép mình kiềm chế.", "full_scene:CH01|Stickman stands firm with arms folded and jaw set in resolute self-discipline."),
            ("Nhiều người thử ép mình nhịn dùng điện thoại hoàn toàn.", "still_life:none|A simple closed padlock doodle drawn in thick black marker on solid warm cream canvas."),
            ("Họ cất điện thoại vào ngăn kéo và cố chịu đựng.", "macro_prop:none|A simple wooden desk drawer slightly closed with a phone hidden inside."),
            ("Họ coi việc lướt mạng như một tội lỗi lớn.", "full_scene:CH01|Stickman stands tall with clenched fists and resolute stance in wide stark white space."),
            ("Nhưng cách làm quá khắc nghiệt này thường không bền.", "concept_metaphor:none|A brittle glass rod snapping cleanly in half under excessive bending force."),
            ("Nhưng sức kiên nhẫn của con người chỉ có hạn thôi.", "visual_diagram:none|A small water vessel slowly leaking droplets until completely empty on white surface."),
            ("Càng gồng mình nhịn, cơn thèm lại càng dữ dội.", "variation:CH01|Stickman drops arms and sighs softly with honest acknowledgement of exhaustion."),
            ("Để rồi vài ngày sau, bạn lại xem nhiều hơn trước.", "macro_prop:none|An open padlock lying next to a simple flat black phone on solid warm cream canvas."),
            ("Bạn tự trách mình yếu đuối và không có quyết tâm.", "full_scene:CH01|Stickman sits on floor with head down, reflecting with quiet honesty on white ground."),
            ("Nhưng sai lầm nằm ở cách làm chưa đúng.", "concept_metaphor:none|A simple black arrow bouncing off a solid vertical obstacle on warm cream canvas."),
        ],
    ),
    (
        "Sự thất bại của các mẹo vặt nông cạn",
        "Clean pure white background (#FFFFFF).",
        "reflective_slow",
        "critical_rebuttal",
        "actionable_resolution",
        [
            ("Những mẹo vặt đơn giản thường không giải quyết được gốc rễ.", "full_scene:CH01|Stickman stands beside a clean blank whiteboard outline on pure white canvas."),
            ("Xóa ứng dụng ba ngày rồi lại tải lại lúc nửa đêm.", "macro_prop:none|A flat dark smartphone screen showing a single plain prompt dot on white surface."),
            ("Cài hẹn giờ lướt web rồi tự tay bấm bỏ qua.", "concept_metaphor:none|A small desktop timer ringing with an oversized snooze finger pressing down."),
            ("Vấn đề không nằm ở chiếc điện thoại.", "full_scene:CH01|Stickman holds up a simple dark smartphone, examining it with objective clarity."),
            ("Vấn đề là đầu óc bạn đang tìm kiếm sự giải tỏa.", "visual_diagram:none|A simple empty ceramic cup resting on clean white table with wide breathing room."),
            ("Bạn không thể ép một đầu óc đang mệt mỏi ngồi yên.", "variation:CH01|Stickman sits cross-legged for a second then opens eyes with honest restless smile."),
            ("Càng ép buộc, tâm trí càng tìm đường bung ra.", "macro_prop:none|A simple ceramic bowl outline drawn in thin black line resting on clean white table with wide breathing room."),
            ("Thay vì tự trách mình hay cắn răng chịu đựng.", "full_scene:CH01|Stickman stands tall, brushing hands clean and pointing upward with clarity."),
            ("Hãy nhẹ nhàng thay đổi những gì bạn tiếp nhận mỗi tối.", "concept_metaphor:none|A simple clear glass of pure water sitting beside an open book on clean desk."),
            ("Đó là lúc sự kiên nhẫn phát huy tác dụng.", "still_life:none|A clear glass flask holding pure water catching gentle ambient daylight on cream."),
        ],
    ),

    # STAGE 7: takeaway (Scenes 15-17)
    (
        "Nguyên lý Dopamine ma sát cao",
        "Solid ivory neutral field (#F8F0DC).",
        "reflective_slow",
        "actionable_resolution",
        "actionable_resolution",
        [
            ("Bí quyết ở đây là: hãy chọn những niềm vui cần chút công sức ban đầu.", "full_scene:CH01|Stickman points toward two clean open paths drawn in thin black line on white canvas."),
            ("Kích thích dễ dãi đến ngay lập tức mà không cần nỗ lực.", "concept_metaphor:none|A simple single small round button icon drawn in black marker on ivory field."),
            ("Nó giống như đồ ăn vặt, ăn thì ngon nhưng người lại mệt.", "macro_prop:none|A small mound of refined sugar cubes beside an empty nutritional energy bar."),
            ("Những niềm vui lành mạnh đòi hỏi bạn bỏ ra chút công sức.", "full_scene:CH01|Stickman points toward a sturdy hiking trail ascending gently on white ground."),
            ("Đó là sự sảng khoái sau khi bạn đi bộ nhẹ nhàng.", "variation:CH01|Stickman ties shoelaces on a pair of minimalist walking shoes with purposeful calm."),
            ("Đó là sự nhẹ nhõm khi bạn đọc xong một chương sách hay.", "macro_prop:none|A thick open hardcover book with crisp black text resting peacefully on desk."),
            ("Cứ bỏ chút công sức ra trước, cảm giác nhẹ nhõm sẽ tự đến sau.", "visual_diagram:none|A simple straight black line pointing from a notebook to an open door on white canvas."),
            ("Tâm trí bạn sẽ cảm nhận được sự nhẹ nhõm trọn vẹn.", "still_life:none|A single smooth river pebble resting quietly on flat untextured ivory canvas with eighty percent negative space. Zero decor, zero clutter."),
            ("Thứ niềm vui này không để lại cảm giác rã rời sau đó.", "full_scene:CH01|Stickman stands upright with hands resting gently behind back with serene presence."),
            ("Nó bồi đắp lại sự an yên từ sâu bên trong.", "concept_metaphor:none|A solid granite brick resting firmly at the foundation of an architectural arch."),
        ],
    ),
    (
        "Bồi đắp lại thụ thể bằng nỗ lực trí tuệ",
        "Pure stark white field (#FFFFFF).",
        "reflective_slow",
        "actionable_resolution",
        "actionable_resolution",
        [
            ("Khi bạn chịu khó vượt qua cảm giác lười biếng ban đầu.", "full_scene:CH01|Stickman sits at a clean wooden desk with a notebook and pen ready on ivory canvas."),
            ("Đầu óc bạn sẽ dần lấy lại sự sáng suốt vốn có.", "visual_diagram:none|A simple single-line window frame swinging gently open toward the morning sky."),
            ("Mười phút đầu đọc sách bao giờ cũng thấy hơi buồn ngủ.", "variation:CH01|Stickman stifles a small yawn while keeping eyes focused calmly on paper page."),
            ("Thói quen lướt điện thoại vẫn còn vương vấn trong đầu.", "concept_metaphor:none|A single clean pencil resting straight on top of a fresh blank notebook page."),
            ("Nhưng nếu bạn kiên nhẫn vượt qua mười phút đầu tiên đó.", "full_scene:CH01|Stickman leans forward, turning a fresh paper page with firm steady fingers."),
            ("Sự tập trung và tĩnh lặng sẽ tự nhiên tìm về.", "still_life:none|A single clean paper bookmark resting quietly between two flat pages on clean white ground."),
            ("Não bộ bắt đầu thả lỏng và thở phào nhẹ nhõm.", "visual_diagram:none|A single horizontal smooth stroke drawn in black ink across clean white canvas."),
            ("Bạn cảm nhận lại niềm vui mộc mạc của những trang sách.", "variation:CH01|Stickman writes smoothly with fluid pen strokes, completely immersed in focused flow."),
            ("Cảm giác thảnh thơi và dễ chịu lan tỏa khắp người.", "macro_prop:none|A simple ceramic tea cup with gentle fragrant steam curling upward on desk."),
            ("Bạn đang làm chủ lại buổi tối và giấc ngủ của chính mình.", "full_scene:CH01|Stickman pauses pen, looking up with peaceful satisfied expression and calm eyes."),
        ],
    ),
    (
        "Ba bước thiết lập không gian sạch",
        "Solid warm cream canvas (#F8F0DC).",
        "reflective_slow",
        "actionable_resolution",
        "actionable_resolution",
        [
            ("Cách đơn giản nhất là sắp xếp lại góc ngủ của bạn.", "full_scene:CH01|Stickman gestures simply with three open fingers on clean pure white canvas."),
            ("Bước một: Cắm sạc điện thoại ở bên ngoài phòng ngủ.", "macro_prop:none|A minimalist phone charger plugged into an outlet in a hallway outside bedroom door."),
            ("Chiếc giường chỉ dành cho sự nghỉ ngơi và giấc ngủ êm.", "concept_metaphor:none|A simple minimalist bed silhouette under a soft crescent moon on peaceful white ground."),
            ("Bước hai: Chuyển màn hình điện thoại sang màu xám.", "full_scene:CH01|Stickman holds up smartphone, tapping screen to toggle monochrome palette."),
            ("Màn hình bớt rực rỡ, cảm giác thèm lướt sẽ giảm đi rất nhiều.", "visual_diagram:none|A smartphone display shifting from vibrant colors to calm pure monochrome gray."),
            ("Màn hình xám không còn thôi thúc ngón tay bạn nữa.", "still_life:none|A simple flat phone lying screen-down on a wooden bedside table on cream canvas."),
            ("Bước ba: Thay chiếc điện thoại bằng một cuốn sách giấy.", "variation:CH01|Stickman places a single paper book on wooden bedside stool with gentle closure."),
            ("Từng trang giấy sẽ nhẹ nhàng ru bạn ngủ tự nhiên.", "concept_metaphor:none|A gentle bookmark ribbon resting between two smooth cream paper pages."),
            ("Bạn không cần phải tự ép mình quá mức.", "full_scene:CH01|Stickman stands in open white space with open welcoming hands and peaceful mind."),
            ("Chỉ cần một chút khoảng cách là bạn đã ngủ ngon hơn.", "still_life:none|A clean wooden desk bathed in calm evening twilight with eighty percent negative space."),
        ],
    ),

    # STAGE 8: closing (Scene 18)
    (
        "Đóng vòng lặp thức tỉnh giấc ngủ sâu",
        "Clean serene white field (#FFFFFF).",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Đêm nay khi ngả lưng xuống chiếc giường êm ái.", "full_scene:CH01|Stickman lies down comfortably on mattress, pulling soft blanket up to chest."),
            ("Hãy nhớ bạn hoàn toàn có thể chọn cách nghỉ ngơi tốt hơn.", "still_life:none|A simple bedside candle outline drawn in thin black line resting on clean serene white field."),
            ("Bạn có quyền buông điện thoại xuống bất cứ lúc nào.", "variation:CH01|Stickman closes eyes with serene relaxed brow on soft flat pillow in quiet room."),
            ("Tắt chiếc điện thoại và để nó ra xa chiếc giường.", "macro_prop:none|A smartphone sitting dark and completely silent on a distant table outside door."),
            ("Trả lại cho đôi mắt bóng tối dịu dàng.", "full_scene:CH01|Stickman lies completely at rest under soft ambient starlight filtering through window."),
            ("Để cho tâm trí bạn thực sự được nghỉ ngơi.", "concept_metaphor:none|A simple single-line rectangle window showing a quiet night sky with a crescent moon on white field."),
            ("Một giấc ngủ bình yên đang đón chờ bạn.", "visual_diagram:none|A simple straight horizontal black line resting silently at the lower third of white field."),
            ("Hơi thở chậm rãi đưa bạn vào giấc mộng đẹp.", "variation:CH01|Stickman sleeps peacefully, chest rising and falling in slow steady natural breath."),
            ("Và ngày mai bạn sẽ thức dậy tràn đầy năng lượng.", "full_scene:CH01|Stickman opens eyes gently as golden morning sun begins to wash over the room."),
            ("Một buổi sáng tỉnh táo và nhẹ nhõm đang đợi bạn.", "still_life:none|A glass of fresh water and morning sunlight beginning to touch the wooden windowsill."),
            ("Nếu thước phim này mang lại cho bạn chút bình yên.", "variation:CH01|Stickman with soft gentle smile looking forward on flat untextured ivory canvas with eighty percent negative space."),
            ("Bạn có thể bấm like và nhấn theo dõi kênh nhé.", "still_life:none|A minimalist hand-drawn thumbs-up outline and a small bell icon drawn in raw black marker line on flat untextured ivory canvas with eighty percent negative space. Zero decor, zero clutter."),
            ("Cảm ơn bạn đã lắng nghe, và chúc bạn ngủ thật ngon.", "still_life:none|A single small hand-drawn crescent moon resting peacefully at the upper corner of flat untextured ivory canvas with eighty-five percent negative space."),
        ],
    ),
]


# ---------------------------------------------------------------------------
# STORY 9:16 (6 Scenes — 60-Second Vertical Mobile Explainer Blueprint)
# ---------------------------------------------------------------------------
STORY_9X16: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    (
        "Cú tát lướt điện thoại hai giờ sáng",
        "Solid warm cream canvas (#F8F0DC).",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Càng lướt mạng, bạn càng mệt mỏi.", "full_scene:CH01|Stickman sits curled up holding flat phone outline on solid warm cream canvas."),
            ("Bạn định xem năm phút rồi ngủ.", "concept_metaphor:none|A small square digital bedside clock showing 00:30 on solid warm cream canvas."),
            ("Nhưng ngẩng lên đã hai giờ sáng.", "still_life:none|A simple hand-drawn analog clock showing late midnight hour on solid warm cream canvas."),
            ("Bạn ngỡ mình đang thư giãn.", "variation:CH01|Stickman stares blankly at screen with tired shoulders and heavy eyes."),
            ("Thực ra đầu óc đang bị vắt kiệt.", "full_scene:CH01|Stickman looks forward with sudden realization under dark vertical framing."),
        ],
    ),
    (
        "Não kiệt quệ sau khi xả stress",
        "Clean pure white background (#FFFFFF).",
        "analytical_crisp",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Buông máy xuống, mắt bạn cay xè.", "full_scene:CH01|Stickman rubs tired eyes with both hands on clean stark white background."),
            ("Lồng ngực dâng lên nỗi trống trải.", "concept_metaphor:none|A solitary smooth pebble resting motionless at base of vertical white void."),
            ("Lướt mạng không mang lại bình yên.", "macro_prop:none|A flat dark smartphone screen resting silent on clean white field with eighty percent negative space."),
            ("Nó rút cạn năng lượng của bạn.", "visual_diagram:none|A simple single vertical line dividing vertical format on clean white canvas."),
        ],
    ),
    (
        "Thí nghiệm chuột nhấn cần gạt tự hủy",
        "Pure stark white field (#FFFFFF).",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Năm một chín năm tư, có một thí nghiệm.", "full_scene:CH01|Stickman stands beside a tall laboratory lever on white canvas."),
            ("Họ gắn một nút bấm nhỏ vào đầu con chuột.", "visual_diagram:none|A simple cross-section outline of animal brain with slender probe placed inside."),
            ("Con chuột nhấn cần hai nghìn lần mỗi giờ.", "still_life:none|A tiny crude cartoon rat pressing a simple black lever on flat pure white canvas."),
            ("Nó bỏ đói cơ thể cho đến khi kiệt sức ngã gục.", "concept_metaphor:none|The metal lever standing motionless under ninety percent vertical space."),
            ("Nó thèm bấm cần hơn cả ăn uống.", "macro_prop:none|A close vertical view of a metal lever untouched on stark white floor."),
        ],
    ),
    (
        "Dopamine chỉ là sự thèm muốn vô tận",
        "Solid ivory neutral field (#F8F0DC).",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Nút bấm không mang lại niềm vui.", "full_scene:CH01|Stickman shakes head gently, pointing to a brain diagram on ivory."),
            ("Nó chỉ kích thích cảm giác muốn xem tiếp.", "visual_diagram:none|A single straight vertical black line running down center of stark white space."),
            ("Nó không giúp bạn hạnh phúc.", "macro_prop:none|An empty plate drawn in thin black outline on cream canvas with eighty percent negative space."),
            ("Nó chỉ thôi thúc bạn bấm thêm một lần nữa.", "macro_prop:none|A stickman thumb hovering restlessly over a vertical phone screen."),
        ],
    ),
    (
        "Cái giá đắt của kích thích rẻ tiền",
        "Solid warm cream canvas (#F8F0DC).",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Đầu óc bạn dần bị chai lì với mọi niềm vui.", "full_scene:CH01|Stickman sits slumped on wooden chair with limp arms on warm cream canvas."),
            ("Ngưỡng vui vẻ tự nhiên của bạn bị kéo tụt xuống rất thấp.", "visual_diagram:none|A vertical plummeting red arrow piercing far below dotted baseline."),
            ("Khiến cho mọi phút giây yên tĩnh bỗng thành bứt rứt.", "concept_metaphor:none|A seesaw heavily tilted downward toward pain side on cream."),
            ("Càng tìm niềm vui dễ, bạn càng kiệt sức.", "still_life:none|An empty white ceramic cup resting quietly on solid warm cream canvas."),
            ("Sự trống rỗng bám lấy bạn mỗi đêm.", "variation:CH01|Stickman presses hand against chest, breathing slowly with reflective insight on cream."),
        ],
    ),
    (
        "Đổi sang niềm vui có ma sát tư duy",
        "Solid warm cream canvas (#F8F0DC).",
        "reflective_slow",
        "actionable_resolution",
        "actionable_resolution",
        [
            ("Đêm nay hãy để điện thoại ngoài phòng ngủ.", "full_scene:CH01|Stickman places phone outside door on solid warm cream canvas."),
            ("Thay video ngắn bằng mười trang sách.", "macro_prop:none|A clean open paper book outline drawn in black marker on solid warm cream canvas with eighty percent negative space."),
            ("Những niềm vui cần chút công sức mới giúp bạn thư thái thật sự.", "macro_prop:none|A single clean closed notebook with bookmark ribbon on flat cream canvas with eighty percent negative space."),
            ("Nếu thấy hữu ích, bạn bấm like và theo dõi nhé.", "still_life:none|A simple hand-drawn thumbs-up outline and small bell icon in pitch-black marker on solid warm cream canvas with eighty percent negative space. Zero decor, zero clutter."),
            ("Chúc bạn ngủ thật ngon giấc.", "full_scene:CH01|Stickman rests head peacefully on pillow, sleeping soundly on solid warm cream canvas with vast negative space."),
        ],
    ),
]


def build_sources() -> list[dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "Positive Reinforcement Produced by Electrical Stimulation of Septal Area",
            "reference": "James Olds & Peter Milner (1954). Journal of Comparative and Physiological Psychology.",
            "facts": [
                "Chuột tự nhấn cần gạt hai nghìn lần mỗi giờ.",
                "Chuột bỏ đói đến kiệt sức chỉ để nhận kích thích.",
                "Kích thích điện tạo ra sự khao khát chứ không thỏa mãn.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Dopamine, Wants and Desires & Dopamine D2 Receptor Availability",
            "reference": "Roy A. Wise (2004). Nature Reviews Neuroscience / Nora Volkow et al. (2011).",
            "facts": [
                "Dopamine là phân tử của sự mong đợi và truy cầu.",
                "Kích thích liên tục làm não giảm thụ thể tiếp nhận.",
                "Đường đáy dopamine sụt giảm gây cảm giác trống rỗng.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Dopamine Nation: Finding Balance in the Age of Indulgence",
            "reference": "Anna Lembke (2021). Dutton / Penguin Random House.",
            "facts": [
                "Khoái cảm không ma sát luôn dẫn đến nỗi đau bù trừ.",
                "Hoạt động nỗ lực có ma sát giúp nâng cao đường chuẩn.",
                "Não bộ chỉ phục hồi khi ngắt kết nối kích thích rẻ tiền.",
            ],
        },
    ]


def build_human_editorial() -> HumanEditorialSpec:
    return HumanEditorialSpec(
        topic_dilemmas=[
            "Con người hiện đại lầm tưởng xem video ngắn và lướt mạng xã hội là hành vi nghỉ ngơi phục hồi, nhưng thực chất là quá trình ép não bộ làm việc tăng ca trong trạng thái kích thích nhân tạo.",
            "Các trào lưu cai nghiện dopamine cực đoan thường thất bại sau vài ngày vì cố áp dụng kỷ luật sắt thay vì hiểu bản chất cân bằng thần kinh học.",
        ],
        dynamic_questions=[
            "Tại sao một hành động hoàn toàn không tốn sức như vuốt màn hình lại có thể khiến não bộ cạn kiệt năng lượng nhanh hơn cả việc đọc sách hay chạy bộ?",
            "Làm thế nào để phân biệt giữa niềm vui đích thực mang lại sự an yên với sự khao khát mù quáng do dopamine kích thích?",
            "Bằng cách nào một người đi làm bận rộn có thể tái hiệu chuẩn lại độ nhạy của não bộ mà không cần phải bỏ lên núi hay vứt bỏ điện thoại?",
        ],
        author_raw_input="Lướt mạng ban đêm không phải là xả stress, đó là hành vi tự ngược đãi vỏ não. Bạn không thiếu ý chí, mà não bạn đang bị kẹt trong chiếc bẫy cần gạt của con chuột thí nghiệm. Để thực sự hồi phục, bạn cần dopamine có ma sát thay vì dopamine miễn phí.",
        editorial_stance="Khoa học thần kinh đã chứng minh một chân lý trớ trêu: Càng tìm kiếm sự thư giãn không ma sát, bạn càng lún sâu vào hố đen lo âu và kiệt quệ. Con đường duy nhất để giải phóng bản thân không phải là trừng phạt bản thân bằng kỷ luật khắc nghiệt, mà là thấu suốt bản chất của dopamine để chủ động chọn những niềm vui có ma sát — nơi nỗ lực tư duy chính là liều thuốc chữa lành sâu sắc nhất.",
        expanded_content_ideas=[
            {
                "idea_id": "IDEA_01",
                "angle_type": "analysis",
                "summary": "Phân tích thí nghiệm chuột Olds-Milner và cơ chế khao khát muốn có khác hoàn toàn với sự thỏa mãn tận hưởng.",
                "narrative_integration": "Đưa vào phân cảnh phân tích cơ chế nhân quả.",
                "target_narrative_phase": "causal_mechanism",
            },
            {
                "idea_id": "IDEA_02",
                "angle_type": "commentary",
                "summary": "Phản biện phong trào cai nghiện mạng xã hội nửa vời và lật tẩy bẫy dopamine rẻ tiền không ma sát.",
                "narrative_integration": "Đưa vào phân cảnh phản biện lật ngược vấn đề.",
                "target_narrative_phase": "counter_argument",
            },
            {
                "idea_id": "IDEA_03",
                "angle_type": "evaluation",
                "summary": "Đánh giá hiệu quả của khung Dopamine Ma Sát Cao trong việc phục hồi năng lượng tinh thần cho người làm việc trí óc.",
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
    scenes[4].source_ids = ["SRC01"]
    scenes[4].claim_facts = [
        ("Năm một chín năm tư, có một thí nghiệm rất nổi tiếng.", "SRC01", "Kích thích điện tạo ra sự khao khát chứ không thỏa mãn."),
    ]
    scenes[5].source_ids = ["SRC01"]
    scenes[5].claim_facts = [
        ("Nó bấm tới hai nghìn lần trong mỗi giờ.", "SRC01", "Chuột tự nhấn cần gạt hai nghìn lần mỗi giờ."),
        ("Cơn thèm bấm cần đã át đi cả cảm giác đói khát tự nhiên.", "SRC01", "Chuột bỏ đói đến kiệt sức chỉ để nhận kích thích."),
    ]
    scenes[6].source_ids = ["SRC01", "SRC02"]
    scenes[6].claim_facts = [
        ("Dopamine không phải là phần thưởng của sự thỏa mãn.", "SRC01", "Kích thích điện tạo ra sự khao khát chứ không thỏa mãn."),
        ("Chất này không tạo ra niềm vui, nó chỉ gây cảm giác thèm muốn.", "SRC02", "Dopamine là phân tử của sự mong đợi và truy cầu."),
    ]
    scenes[9].source_ids = ["SRC02"]
    scenes[9].claim_facts = [
        ("Để tự bảo vệ, não tự động giảm bớt độ nhạy cảm.", "SRC02", "Kích thích liên tục làm não giảm thụ thể tiếp nhận."),
    ]
    scenes[10].source_ids = ["SRC02"]
    scenes[10].claim_facts = [
        ("Ngưỡng vui vẻ tự nhiên của bạn bị kéo tụt xuống rất thấp.", "SRC02", "Đường đáy dopamine sụt giảm gây cảm giác trống rỗng."),
    ]
    scenes[11].source_ids = ["SRC03"]
    scenes[11].claim_facts = [
        ("Não lập tức kéo cảm xúc chùng xuống để cân bằng.", "SRC03", "Khoái cảm không ma sát luôn dẫn đến nỗi đau bù trừ."),
    ]
    scenes[14].source_ids = ["SRC03"]
    scenes[14].claim_facts = [
        ("Những niềm vui lành mạnh đòi hỏi bạn bỏ ra chút công sức.", "SRC03", "Hoạt động nỗ lực có ma sát giúp nâng cao đường chuẩn."),
        ("Kích thích dễ dãi đến ngay lập tức mà không cần nỗ lực.", "SRC03", "Não bộ chỉ phục hồi khi ngắt kết nối kích thích rẻ tiền."),
    ]

    return ResearchedTopic(
        topic="Càng Cố 'Xả Stress', Não Bạn Càng Bị Hút Cạn? (Nghịch Lý Chai Sạn Kích Thích)",
        audience="Người đi làm, sinh viên và người làm việc số thường xuyên bị kiệt sức, lướt điện thoại đêm và rơi vào bẫy mệt mỏi mạn tính",
        goal="Giải mã nghịch lý chai sạn kích thích qua thí nghiệm chuột nhấn cần gạt Olds-Milner, cơ chế suy giảm thụ thể Dopamine D2 và khung tái hiệu chỉnh baseline bằng hành vi ma sát cao",
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
            youtube_title="Càng Cố 'Xả Stress', Não Bạn Càng Bị Hút Cạn?",
            visual_hook="Nhân vật stickman nằm trên giường trùm chăn, hai tay cầm điện thoại phát sáng, nhưng từ lồng ngực nối một sợi dây dẫn năng lượng bị hút cạn vào màn hình, bên cạnh là bóng con chuột thí nghiệm đang bấm cần gạt.",
            text_overlay="BẪY XẢ STRESS",
            contrast_pair="Lướt mạng xả stress vs. Não bộ bị hút cạn",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "bẫy xả stress",
                "nghịch lý dopamine",
                "thí nghiệm con chuột",
                "dopamine ma sát cao",
                "tâm lý học nhận thức",
            ],
            thumbnail_prompt=(
                "Orthographic 2D hand-drawn doodle poster. 60% of the frame shows a bald stickman in a blue shirt (#3B82C4) "
                "lying on a flat mattress holding an oversized black rectangle phone, with a simple black wire draining "
                "an empty battery icon from his chest. Beside the bed is a simple cartoon rat pressing a mechanical "
                "lever. Solid clean warm paper-cream canvas (#F8F0DC), wobbly raw black marker contours (#000000). 40% clean "
                "negative space on the top right with bold yellow hand-lettered text 'BẪY XẢ STRESS' with thick black "
                "outline. Zero room interiors, zero 3D perspective, zero glow, zero decorative frames, zero drop shadows."
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
    scenes[2].source_ids = ["SRC01"]
    scenes[2].claim_facts = [
        ("Con chuột nhấn cần hai nghìn lần mỗi giờ.", "SRC01", "Chuột tự nhấn cần gạt hai nghìn lần mỗi giờ."),
        ("Nó bỏ đói cơ thể cho đến khi kiệt sức ngã gục.", "SRC01", "Chuột bỏ đói đến kiệt sức chỉ để nhận kích thích."),
    ]
    scenes[3].source_ids = ["SRC02"]
    scenes[3].claim_facts = [
        ("Nó chỉ kích thích cảm giác muốn xem tiếp.", "SRC02", "Dopamine là phân tử của sự mong đợi và truy cầu."),
    ]
    scenes[4].source_ids = ["SRC02", "SRC03"]
    scenes[4].claim_facts = [
        ("Đầu óc bạn dần bị chai lì với mọi niềm vui.", "SRC02", "Kích thích liên tục làm não giảm thụ thể tiếp nhận."),
        ("Ngưỡng vui vẻ tự nhiên của bạn bị kéo tụt xuống rất thấp.", "SRC02", "Đường đáy dopamine sụt giảm gây cảm giác trống rỗng."),
        ("Khiến cho mọi phút giây yên tĩnh bỗng thành bứt rứt.", "SRC03", "Khoái cảm không ma sát luôn dẫn đến nỗi đau bù trừ."),
    ]
    scenes[5].source_ids = ["SRC03"]
    scenes[5].claim_facts = [
        ("Những niềm vui cần chút công sức mới giúp bạn thư thái thật sự.", "SRC03", "Hoạt động nỗ lực có ma sát giúp nâng cao đường chuẩn."),
    ]

    return ResearchedTopic(
        topic="Bẫy Xả Stress: Càng Lướt Mạng Càng Kiệt Sức? (Bản Dọc 60 Giây)",
        audience="Người trẻ, sinh viên và người làm việc số lướt video ngắn trên di động",
        goal="Tóm gọn nghịch lý chai sạn kích thích trong 60 giây qua thí nghiệm con chuột và chỉ ra cơ chế dopamine ma sát cao để phục hồi năng lượng",
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
            youtube_title="Càng Cố Xả Stress Não Càng Kiệt Sức?",
            visual_hook="Người que nằm co quắp trên nệm, tay bấm điện thoại sáng rực trong bóng tối, biểu tượng pin cạn đỏ lòm hiện trên đầu.",
            text_overlay="BẪY XẢ STRESS",
            contrast_pair="Giải trí thư giãn vs. Kiệt quệ thần kinh",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "bẫy xả stress",
                "video ngắn hại não",
                "dopamine ma sát cao",
                "kiệt sức vì lướt mạng",
            ],
            thumbnail_prompt=(
                "Orthographic 2D vertical hand-drawn doodle poster. 60% frame shows a stickman in a blue shirt curled up on a thin floor "
                "mattress holding a simple black rectangle phone, with an empty red battery icon floating above his head. "
                "Solid clean warm paper-cream canvas (#F8F0DC), wobbly raw black marker contours (#000000). 40% clean negative space at the top "
                "with large yellow text 'BẪY XẢ STRESS' with thick black outline. Zero room interiors, zero 3D perspective, zero glow, zero drop shadows."
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
    parser = argparse.ArgumentParser(description="Build Stress Trap Paradox 16:9 & 9:16 production blueprint.")
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
            job_name = "stress-trap-paradox-16x9"
        else:
            topic = build_topic_9x16()
            job_name = "stress-trap-paradox-9x16"

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
        print("[SUCCESS] Toàn bộ gói hồ sơ kỹ thuật cho Stress Trap Paradox đã hoàn thành và đạt chuẩn!")
        return 0
    else:
        print("[FAILURE] Phát hiện lỗi trong quá trình đóng gói hồ sơ kỹ thuật.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
