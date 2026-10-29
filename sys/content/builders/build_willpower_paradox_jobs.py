#!/usr/bin/env python3
"""Build production-ready packages for Willpower Paradox & Brain Drain (16:9 Landscape & 9:16 Portrait).

Pillar: "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức" (tier_1_broad -> tier_2_mid)
Core Topic: "Vì Sao Bạn Càng Cố Tập Trung Càng Trì Hoãn?" (Paradox of Willpower & Choice Architecture / Brain Drain)
Experiments:
  - Adrian F. Ward et al. (2017) "Brain Drain: The Mere Presence of One's Own Smartphone Reduces Available Cognitive Capacity"
  - Anne N. Thorndike et al. (2012) "Choice Architecture and Environmental Friction in Habit Disruption"

Formats:
  - willpower-paradox-16x9: 8 scenes, 74 visual beats, 8-part narrative arc landscape explainer
  - willpower-paradox-9x16: 6 scenes, 25 visual beats, 60-second vertical mobile short explainer
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
# STORY 16:9 (18 Scenes — 18-Part Layered Narrative Arc Explainer Blueprint)
# (title, setting, tone, spoken_style, narrative_phase, rows)
# ---------------------------------------------------------------------------
STORY_16X9: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    (
        "Cú tát ý chí mở màn",
        "Solid warm cream canvas (#F8F0DC).",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Càng cố dùng ý chí để tập trung, bạn lại càng dễ sụp đổ.", "full_scene:CH01|Stickman sits on a simple wooden chair with arms tightly folded, grimacing with tense effort on solid cream ground with 70% negative space."),
            ("Bạn tự trói chặt mình vào chiếc ghế gỗ.", "variation:CH01|Stickman struggles as a single thick brown rope coils lightly around own waist and chair on clean cream background."),
            ("Bạn tự cấm bản thân, tuyệt đối không chạm vào mạng xã hội.", "concept_metaphor:none|A smartphone icon struck through with a single bold red prohibition line on solid cream field with clean bold unadorned black text reading 'CẤM MẠNG XÃ HỘI'. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero confetti. 70% negative space."),
            ("Hai bàn tay bạn nắm chặt đến mức run rẩy.", "variation:CH01|Stickman clenches both small white hands into tight trembling fists with determined furrowed brow."),
            ("Nhưng bạn càng gồng ép, cơn thèm lướt mạng càng trỗi dậy mãnh liệt.", "full_scene:CH01|Stickman sits in simple chair gripping armrests tightly with desperate strained expression, white head with small wobbly tension lines facing a browser outline. Clean bold unadorned black hand-lettered text reading 'CÀNG GỒNG CÀNG THÈM' floating freely on solid warm cream canvas with 75% negative space. Strictly zero coiled springs, zero lightning, zero red sparks, zero room interiors, zero walls, zero floor lines."),
            ("Sau ba mươi phút giằng co căng thẳng, đầu bạn trống rỗng hoàn toàn.", "full_scene:CH01|Stickman slumps shoulders in chair with dizziness spiral lines floating over bald head on open cream field."),
            ("Và ngón tay, lại vô thức bấm mở ứng dụng giải trí.", "macro_prop:none|A single sleek hand hovering over a stylized blue browser icon on pure cream backdrop."),
            ("Nỗ lực tập trung tan thành mây khói ngay từ vạch xuất phát.", "still_life:none|A small minimalist sandglass with all sand fallen to bottom on clean ivory ground with 70% negative space."),
        ],
    ),
    (
        "Vòng xoáy tội lỗi và một tab vô hại",
        "Clean pure white background (#FFFFFF).",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Bạn tức giận xóa sạch các ứng dụng trên điện thoại.", "full_scene:CH01|Stickman firmly slides a smartphone icon into a small wire trash bin on pure white ground."),
            ("Bạn tự nhủ hôm nay sẽ làm việc nghiêm túc suốt buổi chiều.", "variation:CH01|Stickman raises open hand in confident personal pledge on stark white field with 65% negative space."),
            ("Thế nhưng khi vừa ngồi vào máy tính, ngón tay bạn lại ngập ngừng.", "variation:CH01|Stickman sits before a minimalist gray keyboard, index finger hovering hesitantly above keys."),
            ("Bạn nghĩ bụng chỉ mở thêm đúng một tab tra cứu để xem tài liệu.", "macro_prop:none|A single clean browser tab header titled TÀI LIỆU with a tiny magnifying glass on white background."),
            ("Đúng một trang mạng thôi, sẽ không mất quá nhiều thời gian.", "concept_metaphor:none|Clean bold unadorned black hand-lettered text reading 'ĐÚNG MỘT TAB' floating freely on pure white canvas beside a minimalist browser tab icon. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero sparkles, zero squiggles, zero confetti, zero ribbons, zero floor lines. 75% negative space."),
            ("Mười phút sau, bạn đã trôi dạt sang một diễn đàn giải trí.", "full_scene:CH01|Stickman sits with cheek resting on palm, dazed eyes looking upward as time slips away."),
            ("Cảm giác tội lỗi và thất vọng lập tức bóp nghẹt lồng ngực bạn.", "variation:CH01|Stickman presses both hands to chest with remorseful expression on clean white ground."),
            ("Bạn nhận ra mình vừa lãng phí thêm nửa ngày quý giá.", "still_life:none|A minimalist analog clock dial showing hands advanced by half a day on pure white field."),
        ],
    ),
    (
        "Ảo tưởng về kỷ luật sắt",
        "Solid ivory neutral field (#F8F0DC).",
        "analytical_crisp",
        "demystifying_truth",
        "empirical_conflict",
        [
            ("Hầu hết mọi người đều tự trách mình lười biếng và hèn kém.", "full_scene:CH01|Stickman points index finger at own chest with self-critical gaze on wide solid ivory ground."),
            ("Bạn lao vào tìm kiếm những cuốn sách dạy kỷ luật thép.", "variation:CH01|Stickman holds a single thick gray book labeled KỶ LUẬT THÉP with high expectations."),
            ("Bạn bắt bản thân ngồi bất động bốn tiếng mỗi ngày như một cỗ máy.", "full_scene:CH01|Stickman sits unnaturally stiff and motionless like a stone statue before a single notebook on solid ivory field. A tiny hand-drawn wind-up key is sketched in black marker on stickman back. Clean bold unadorned black hand-lettered text reading 'BẤT ĐỘNG 4 TIẾNG' floats freely above. Strictly zero retro robots, zero toy figures, zero pocket watches, zero room interiors. 75% negative space."),
            ("Đó là sai lầm phổ biến nhất trong thế giới hiện đại.", "concept_metaphor:none|Clean bold unadorned black hand-lettered text reading 'SAI LẦM Ý CHÍ' floating freely on solid ivory field with a simple bold red exclamation mark. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero sparkles, zero squiggles, zero confetti, zero ribbons, zero floor lines. 75% negative space."),
            ("Bạn đang coi ý chí như một nguồn năng lượng vô tận không bao giờ cạn.", "full_scene:CH01|Stickman stands in open ivory space puffing chest proudly and flexing thin doodle stick arms with an exaggerated overly confident smile on bare ivory canvas. Clean bold unadorned black hand-lettered text reading 'Ý CHÍ VÔ HẠN?' floats freely beside a simple black question mark symbol. Strictly zero battery icons, zero shiny gold infinity symbols, zero lightning bolts, zero sparkles, zero room clutter. 75% negative space."),
            ("Thế nhưng, cơ thể chúng ta lại không vận hành như một cỗ máy.", "variation:CH01|Stickman lowers hands with thoughtful reflective gaze, shaking head gently on open ivory space with 70% negative space."),
            ("Ý chí thực chất là một nguồn tài nguyên sinh học cực kỳ mong manh.", "concept_metaphor:none|A small single hand-drawn candle with tiny warm yellow flame centered on 100% solid flat warm cream canvas (#F8F0DC). Clean bold unadorned black text reading 'Ý CHÍ MONG MANH' floating freely. Strictly zero tables, zero wooden surfaces, zero two-tone floors, zero drop shadows. 80% negative space."),
        ],
    ),
    (
        "Thí nghiệm đĩa bánh quy và củ cải đỏ",
        "Pure stark white field (#FFFFFF).",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Để thấy rõ điều này, hãy nhìn vào một thí nghiệm kinh điển với đĩa bánh quy.", "full_scene:CH01|Stickman stands on bare white field gesturing invite with open palm toward center ground with 75% negative space."),
            ("Họ mời những người tham gia bước vào một không gian ngát hương thơm.", "variation:CH01|Stickman steps forward with curious expression, nostrils sensing aroma on pure white field."),
            ("Trên chiếc đĩa giữa bàn là những chiếc bánh quy sô-cô-la vừa mới nướng.", "macro_prop:none|A pristine white porcelain plate holding three golden baked chocolate chip cookies on clean white background."),
            ("Cạnh đĩa bánh thơm lừng là một bát củ cải đỏ sống đắng ngắt.", "macro_prop:none|A simple ceramic bowl holding two raw red radishes with leafy greens on stark white field."),
            ("Nhóm thứ nhất được thoải mái thưởng thức những chiếc bánh quy ấm nóng.", "full_scene:CH01|Stickman smiles happily holding a chocolate cookie near mouth on clear white field."),
            ("Trong khi nhóm thứ hai bị ép phải ăn củ cải đỏ, và tuyệt đối không chạm vào bánh.", "concept_metaphor:none|A visual scale where golden chocolate cookies easily tip against raw bitter radishes on white ground."),
            ("Những người nhóm hai phải gồng mình nuốt từng miếng củ cải trong thèm thuồng.", "full_scene:CH01|Stickman swallows raw radish with visible effort, hands clenched tightly behind back on pure white ground."),
        ],
    ),
    (
        "Thử thách câu đố hình học bất khả thi",
        "Flat solid cream surface (#F8F0DC).",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Ngay sau bữa ăn thử thách, cả hai nhóm cùng làm một nhiệm vụ tiếp theo.", "full_scene:CH01|Stickman sits calmly before a single sheet of paper with a black pencil in hand on cream ground."),
            ("Ban tổ chức phát cho mỗi sinh viên một câu đố vẽ hình học phức tạp.", "macro_prop:none|A single clean drawing sheet showing an intricate geometric maze figure outlined in sharp black."),
            ("Điểm mấu chốt là câu đố này được thiết kế để không thể giải được.", "concept_metaphor:none|Clean bold unadorned black hand-lettered text reading 'THỬ THÁCH BẤT KHẢ THI' floating freely on flat cream surface above an intricate geometric maze figure outlined in sharp black. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero sparkles, zero squiggles, zero confetti, zero ribbons, zero floor lines. 70% negative space."),
            ("Mục đích thực sự là đo lường thời gian kiên trì của mỗi người.", "still_life:none|A minimalist analog stopwatch with tick marks measuring elapsed minutes on flat cream ground."),
            ("Nhóm được ăn bánh quy vui vẻ ngồi giải đố suốt gần hai mươi phút.", "full_scene:CH01|Stickman sits comfortably tracing lines with focused and cheerful persistence."),
            ("Trong khi nhóm chỉ được ăn rau củ buông bút bỏ cuộc chỉ sau tám phút ngắn ngủi.", "variation:CH01|Stickman sets pencil down on paper with heavy sigh of mental exhaustion on cream field."),
            ("Họ cạn kiệt kiên nhẫn nhanh gấp đôi nhóm đầu tiên.", "visual_diagram:none|Two clean minimalist vertical bar pillars beside an analog timer dial: Cookie group reaching 19 minutes beside Radish group reaching only 8 minutes on bare cream ground. Clean bold unadorned black hand-lettered text reading 'THỜI GIAN KIÊN TRÌ' floating freely above. Strictly zero card borders, zero boxes, zero floating stars, zero squiggles, zero confetti. 70% negative space."),
        ],
    ),
    (
        "Bản chất cạn kiệt năng lượng bản ngã",
        "Clean solid white canvas (#FFFFFF).",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Tại sao những người phải kiềm chế lại đầu hàng nhanh đến như vậy?", "full_scene:CH01|Stickman tilts head with open questioning palms on pure white minimalist ground."),
            ("Hành động nhịn thèm đĩa bánh quy đã vắt kiệt bình ắc quy ý chí của họ.", "full_scene:CH01|Stickman slumps forward sitting on bare white ground with drooped head and tired expression. Beside stickman floats a simple minimalist vertical level gauge outlined in clean black ink, dropped to zero with clean bold unadorned black hand-lettered text reading 'CẠN KIỆT'. Strictly zero green 3D batteries, zero hazard triangles, zero warning symbols, zero room interiors. 75% negative space."),
            ("Khái niệm cạn kiệt bản ngã ra đời từ chính thực nghiệm kinh điển này.", "full_scene:CH01|Stickman sits slumped forward exhausted with head resting on knees on solid white canvas. Directly above stickman, clean bold unadorned black hand-lettered text reading 'CẠN KIỆT BẢN NGÃ' floats freely on the bare field. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero sparkles, zero squiggles, zero confetti, zero ribbons, zero floor lines. 70% negative space."),
            ("Mỗi lần bạn cưỡng lại một cơn cám dỗ, năng lượng tinh thần sẽ hao hụt dần.", "concept_metaphor:none|A single clean stickman hand gently pushing away a simple white plate on bare white ground. Beside it, clean bold unadorned black hand-lettered text reading 'MỖI LẦN CƯỠNG LẠI' floats freely on pure white canvas with 75% negative space. Strictly zero assembly lines, zero donuts, zero game controllers, zero barrier clutter, zero arrows."),
            ("Khi bình năng lượng đó rơi xuống đáy, não bộ lập tức tê liệt.", "full_scene:CH01|Stickman slumps forward in sitting pose with empty hands resting on lap on white canvas."),
            ("Bạn không thể đòi hỏi một cục pin đã cạn tiếp tục phát sáng rực rỡ.", "concept_metaphor:none|A simple doodle flashlight icon with an extinguished light beam outlined in black ink on clean pure white backdrop with 75% negative space. Strictly zero 3D batteries, zero glowing effects."),
        ],
    ),
    (
        "Sự hiện diện thầm lặng của chiếc điện thoại",
        "Solid ivory tone backdrop (#F8F0DC).",
        "narrative_warm",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Bi kịch chưa dừng lại ở việc gồng mình cưỡng lại miếng ăn ngon.", "full_scene:CH01|Stickman walks forward with thoughtful expression across wide solid ivory field."),
            ("Trong cuộc sống hiện đại, có một kẻ thù nguy hiểm hơn đĩa bánh quy gấp nhiều lần.", "variation:CH01|Stickman halts steps, looking downward with solemn focus on flat ivory canvas."),
            ("Đó chính là chiếc điện thoại thông minh đang nằm ngay trước mắt bạn.", "macro_prop:none|A single black smartphone lying flat on ivory surface with glossy glass reflection."),
            ("Hầu hết chúng ta đều nghĩ rằng, chỉ cần tắt chuông và úp mặt máy xuống bàn là xong.", "macro_prop:none|The smartphone lies face down with a small slashed speaker icon floating above it."),
            ("Thế nhưng, chỉ cần chiếc máy còn nằm đó, tâm trí bạn vẫn không tài nào yên được.", "full_scene:CH01|Stickman sits at simple desk with head turned away from smartphone, but small restless tension lines float near temples on solid ivory backdrop with clean bold unadorned black text reading 'KHÔNG THỂ YÊN TÂM'. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero confetti. 75% negative space."),
            ("Sự hiện diện vật lý của điện thoại âm thầm bòn rút tâm trí bạn từng giây.", "concept_metaphor:none|Faint ripple waves radiating outward from smartphone silhouette into empty ivory space."),
        ],
    ),
    (
        "Quy trình thử nghiệm ba nhóm đối chứng",
        "Minimal pure white space (#FFFFFF).",
        "analytical_crisp",
        "scientific_evidence",
        "structural_model",
        [
            ("Các nhà nghiên cứu tại Đại học Texas, từng bóc trần điều này qua một phép thử rất đơn giản.", "full_scene:CH01|Stickman stands beside clean bold unadorned black hand-lettered text reading 'ĐẠI HỌC TEXAS' floating freely on pure white ground beside a minimalist seal emblem. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero confetti. 75% negative space."),
            ("Hơn năm trăm sinh viên được mời tham gia hai bài kiểm tra tư duy phức tạp.", "visual_diagram:none|A clean 3-part column diagram on pure white canvas showing groups A, B, and C with equal student icons."),
            ("Các nhà nghiên cứu chia ngẫu nhiên họ thành ba nhóm hoàn toàn riêng biệt.", "full_scene:CH01|Stickman gestures to three separate path markers labeled A, B, and C on white floor."),
            ("Nhóm thứ nhất đặt điện thoại úp mặt ngay góc bàn làm việc.", "macro_prop:none|A minimalist black smartphone placed face down on 100% pure white flat canvas (#FFFFFF) with 75% negative space. Clean bold unadorned black text reading 'ÚP MẶT ĐIỆN THOẠI' floating freely. Strictly zero desks, zero wooden table corners, zero furniture, zero floor lines."),
            ("Nhóm thứ hai cất điện thoại nằm sâu trong túi quần hoặc túi xách.", "full_scene:CH01|Stickman slides smartphone deep into trouser pocket before taking seat on white canvas."),
            ("Và nhóm thứ ba phải cất thiết bị sang một phòng tách biệt.", "concept_metaphor:none|A closed wooden door symbol with smartphone silhouette placed on the far outer side."),
            ("Tất cả máy đều ở chế độ im lặng tuyệt đối và không hề rung.", "concept_metaphor:none|A minimalist slashed speaker icon and silenced bell outlined in clean black ink on pure white canvas, with clean bold unadorned black text reading 'TẮT CHUÔNG VÀ RUNG' floating beside. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero confetti. 75% negative space."),
        ],
    ),
    (
        "Địa chấn dữ liệu cạn kiệt nhận thức",
        "Solid warm sand canvas (#F8F0DC).",
        "analytical_crisp",
        "scientific_evidence",
        "structural_model",
        [
            ("Và khi chấm điểm các bài kiểm tra, những con số đã nói lên tất cả.", "full_scene:CH01|Stickman holds up a single test score sheet with wide-eyed astonished expression on solid cream field with 70% negative space."),
            ("Nhóm đặt máy tại phòng bên cạnh đạt điểm số cao vượt trội ở mọi bài thi.", "visual_diagram:none|A tall vibrant green bar chart reaching 85% score for Other Room group on solid cream background."),
            ("Trong khi nhóm đặt điện thoại trên bàn có điểm số tụt dốc thảm hại.", "full_scene:CH01|Stickman stares dismayed at a short low exam score card on cream field."),
            ("Khả năng ghi nhớ và năng lực tư duy của họ giảm sút gần bốn mươi phần trăm.", "concept_metaphor:none|Clean bold unadorned black hand-lettered text reading 'GIẢM 40% NHẬN THỨC' floating freely on solid warm sand field with a simple bold downward arrow. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero sparkles, zero squiggles, zero confetti, zero ribbons, zero floor lines. 75% negative space."),
            ("Đáng kinh ngạc là không một sinh viên nào chạm tay vào chiếc máy.", "full_scene:CH01|Stickman sits with hands firmly folded on lap without touching anything on cream surface."),
            ("Chỉ cần điện thoại nằm trong tầm mắt, não bộ đã tự động suy giảm công suất.", "concept_metaphor:none|A clean minimalist horizontal capacity meter bar outlined in black ink draining down to empty red on solid warm sand canvas, with clean bold unadorned black text reading 'BỘ NHỚ LÀM VIỆC' floating cleanly above. Strictly zero anatomical brains, zero card borders, zero boxes, zero banners, zero stars, zero squiggles, zero confetti. 75% negative space."),
        ],
    ),
    (
        "Cuộc chiến ngầm trong vỏ não trước trán",
        "Pristine white flat ground (#FFFFFF).",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Tại sao chỉ nhìn thấy chiếc điện thoại lại khiến bạn kiệt sức đến thế?", "full_scene:CH01|Stickman touches temples with both hands in deep reflective inquiry on white ground."),
            ("Câu trả lời nằm ở cơ chế ức chế chủ động sâu bên trong bộ não.", "full_scene:CH01|Stickman sits upright in deep calm focus with index finger gently touching own temple on pure white ground. Clean bold unadorned black hand-lettered text reading 'ỨC CHẾ CHỦ ĐỘNG' floats freely beside. Strictly zero anatomical brains, zero cross-sections, zero card borders, zero boxes, zero banners, zero floating stars, zero confetti. 70% negative space."),
            ("Vùng vỏ não trước trán là nơi chịu trách nhiệm tư duy logic và kiểm soát hành vi.", "concept_metaphor:none|Clean bold unadorned black hand-lettered text reading 'VỎ NÃO TRƯỚC TRÁN' floating freely on pure white flat ground above two clean minimalist control dials outlined in black ink. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero sparkles, zero squiggles, zero confetti, zero ribbons, zero floor lines. 75% negative space."),
            ("Khi điện thoại nằm trước mắt, tiềm thức liên tục gửi tín hiệu thôi thúc cầm máy lên.", "concept_metaphor:none|A simple dashed impulse arrow pointing from a smartphone outline toward stickman on 100% uniform pure white flat canvas (#FFFFFF). Clean bold unadorned black text reading 'THÔI THÚC NGẦM' floating freely. Strictly zero horizon lines, zero two-tone background, zero floor lines. 80% negative space."),
            ("Để giữ bạn tập trung vào trang tài liệu, vỏ não phải gồng mình đạp phanh liên tục.", "concept_metaphor:none|A simple doodle brake shoe clamped against an outline wheel with small friction marks on white field with 75% negative space."),
            ("Chiếc phanh đó đốt cháy năng lượng glucose như một động cơ chạy hết công suất.", "concept_metaphor:none|A clean fuel gauge needle dropping toward empty 'E' mark outlined in black ink on white canvas with 75% negative space."),
            ("Bạn mệt mỏi không phải vì làm việc khó, mà vì não bộ vừa trải qua một cuộc nội chiến.", "full_scene:CH01|Stickman slumps gently on chair, wiping forehead with tired but enlightened realization."),
        ],
    ),
    (
        "Cơ chế máy đánh bạc trong túi quần",
        "Solid cream open field (#F8F0DC).",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Đằng sau sự thôi thúc mãnh liệt đó là một cạm bẫy thiết kế tinh vi.", "full_scene:CH01|Stickman peers cautiously around a stylized corner at a gleaming device symbol on cream ground."),
            ("Các nền tảng số hoạt động chính xác như một cỗ máy đánh bạc trong sòng bài.", "concept_metaphor:none|Three simple hand-drawn square outline boxes containing black question marks '? ? ?' on solid flat cream canvas (#F8F0DC). Clean bold unadorned black text reading 'MÁY ĐÁNH BẠC' floating freely above. Strictly zero slot machine bodies, zero casino levers, zero reels, zero wall colors, zero room lines. 80% negative space."),
            ("Đằng sau màn hình là cơ chế phần thưởng biến thiên ngẫu nhiên.", "concept_metaphor:none|Clean bold unadorned black hand-lettered text reading 'PHẦN THƯỞNG BIẾN THIÊN' floating freely on solid cream open field beside three simple black question mark symbols. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero sparkles, zero squiggles, zero confetti, zero ribbons, zero floor lines. 75% negative space."),
            ("Mỗi khi mở điện thoại, bạn không bao giờ biết mình sẽ nhận được tin nhắn hay thông báo gì.", "macro_prop:none|A smartphone screen showing three unopened notification gift envelopes with question marks."),
            ("Chính sự bất định đó đã kích hoạt chất dẫn truyền dopamine tăng vọt.", "visual_diagram:none|A dopamine molecular spike chart shooting upward in sharp green trajectory on cream ground."),
            ("Bộ não hồi hộp vì kỳ vọng phần thưởng, chứ không phải vì bản thân phần thưởng đó.", "full_scene:CH01|Stickman gazes upward with anticipatory sparkle in eyes surrounded by 65% open cream space."),
        ],
    ),
    (
        "Vô tận cuộn lướt và bẫy dopamine hồi hộp",
        "Clean bright white backdrop (#FFFFFF).",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Tính năng cuộn vô tận chính là chiếc cần gạt máy đánh bạc thế kỷ mới.", "concept_metaphor:none|A single simple black marker arrow curling smoothly downward on pure stark white canvas (#FFFFFF). Clean bold unadorned black hand-lettered text reading 'VÒNG LẶP VÔ TẬN' floating freely beside. Strictly zero 3D ribbons, zero spiral rolls, zero shiny shading. 80% negative space."),
            ("Bạn gạt màn hình một lần, một phần thưởng hình ảnh ngẫu nhiên lại hiện ra.", "macro_prop:none|A single finger flicking a glass screen surface upward, creating a fresh card reveal."),
            ("Bộ não của chúng ta tiến hóa qua hàng triệu năm, để săn tìm những bất ngờ sinh tồn.", "full_scene:CH01|Stickman in primitive explorer pose scanning distant horizon with hand above brow on white field."),
            ("Làm sao một mẩu ý chí nhỏ bé, có thể chiến thắng hàng nghìn kỹ sư phần mềm hàng đầu?", "concept_metaphor:none|Stickman standing in simple profile looking up at a single floating smartphone outline with clean bold unadorned black hand-lettered text reading 'THU HÚT CHÚ Ý' on stark pure white canvas (#FFFFFF). Strictly zero skyscrapers, zero buildings, zero magnets, zero brains, zero bicycles, zero fences, zero bushes, zero grass. 80% negative space."),
            ("Bạn tự trách bản thân yếu đuối, nhưng thực tế bạn đang chiến đấu trong một cuộc chơi bất công.", "full_scene:CH01|Stickman lowers head with sympathetic hand over heart on pure white canvas."),
            ("Cố gắng chống cự bằng sự gồng ép chỉ khiến bạn thất bại ê chề hơn.", "variation:CH01|Stickman drops small wooden shield onto white ground with calm release of futile strain."),
        ],
    ),
    (
        "Ảo tưởng đoạn tuyệt công nghệ cực đoan",
        "Flat solid ivory backdrop (#F8F0DC).",
        "reflective_slow",
        "rational_empathy",
        "structural_model",
        [
            ("Nhiều người quyết định vứt bỏ điện thoại vào ngăn tủ khóa chặt.", "full_scene:CH01|Stickman turns a heavy brass key in a solid wooden lockbox on flat ivory backdrop."),
            ("Họ tự cô lập mình khỏi thế giới số để mong tìm lại sự bình yên tuyệt đối.", "variation:CH01|Stickman sits cross-legged trying to meditate while fidgeting nervously on ivory surface."),
            ("Nhưng giải pháp cực đoan đó hầu như luôn đổ vỡ chỉ sau hai mươi bốn giờ.", "still_life:none|A minimalist calendar page showing day 1 crossed out with day 2 torn in half on ivory ground."),
            ("Bạn vẫn phải nhận tin nhắn công việc khẩn cấp từ đối tác và đồng nghiệp.", "macro_prop:none|A clean ivory envelope stamped with red word KHẨN CẤP floating in calm negative space."),
            ("Bạn cần mã xác thực ngân hàng để thanh toán các giao dịch quan trọng.", "macro_prop:none|Crisp black numerals reading '8 4 2 9 1 0' floating freely on flat ivory field with a small phone outline. Strictly zero card borders, zero boxes, zero corner tape. 75% negative space."),
            ("Cắt đứt hoàn toàn chỉ tạo ra nỗi sợ hãi bỏ lỡ thông tin kinh hoàng.", "concept_metaphor:none|A clean minimalist doodle alarm clock bell outlined in black ink with two tiny vibration marks on flat solid ivory backdrop (#F8F0DC). Clean bold unadorned black hand-lettered text reading 'CĂNG THẲNG' floating freely beside. Strictly zero tangled knots, zero thread balls, zero lightning bolts. 80% negative space."),
            ("Nỗi lo âu đó lại quay ngược trở lại, bòn rút sự tập trung của bạn gấp bội phần.", "full_scene:CH01|Stickman paces back and forth with furrowed brow and clasped hands on ivory field."),
        ],
    ),
    (
        "Nghiên cứu căn tin của nhà khoa học hành vi",
        "Clean open white ground (#FFFFFF).",
        "analytical_crisp",
        "scientific_evidence",
        "actionable_resolution",
        [
            ("Vậy lối thoát thực sự nằm ở đâu nếu gồng mình hay đoạn tuyệt đều vô dụng?", "full_scene:CH01|Stickman spreads both hands in calm inquiry, looking forward on pure white open ground."),
            ("Lời giải đến từ một câu chuyện có thật tại căn tin bệnh viện Boston.", "concept_metaphor:none|Clean bold unadorned black hand-lettered text reading 'THỰC NGHIỆM CĂN TIN BOSTON' floating freely on clean open white ground beside an elegant minimalist hospital cross icon. Strictly zero banner borders, zero cards, zero boxes, zero corner tape, zero floating stars, zero confetti, zero ribbons. 75% negative space."),
            ("Thay vì dán khẩu hiệu kêu gọi mọi người ngừng uống nước ngọt có ga.", "concept_metaphor:none|A single red soda can with a bold diagonal red prohibition slash through it on clean white ground. Clean bold unadorned black text reading 'CẤM NƯỚC NGỌT' floats freely above. Strictly zero banners, zero paper scrolls, zero ribbons, zero cards, zero stars, zero confetti. 75% negative space."),
            ("Bà chỉ đơn giản xếp thêm những chai nước mát lành vào ngay tầm mắt người mua.", "macro_prop:none|Three clear transparent glass water bottles arranged neatly at center eye level on white canvas."),
            ("Còn những lon nước ngọt nhiều đường được chuyển xuống tầng kệ thấp hơn và xa hơn.", "macro_prop:none|Two simple minimalist red soda cans drawn in clean black marker ink placed in the far lower corner on 100% pristine solid white canvas (#FFFFFF). Clean bold unadorned black hand-lettered text reading 'RỜI KHỎI TẦM MẮT' floating cleanly above. Strictly zero grass tufts, zero dirt specks, zero dots, zero floor textures. 85% negative space."),
            ("Không hề có một lời khuyên bảo hay cấm đoán nào được đưa ra.", "full_scene:CH01|Stickman stands beside the display observing with folded arms and peaceful smile."),
        ],
    ),
    (
        "Nghịch lý kiến trúc môi trường",
        "Solid warm cream surface (#F8F0DC).",
        "analytical_crisp",
        "demystifying_truth",
        "actionable_resolution",
        [
            ("Kết quả thực tế đã làm kinh ngạc tất cả các chuyên gia y tế công cộng.", "full_scene:CH01|Stickman points with wide smile to a clear upward sales graph on cream surface."),
            ("Doanh số nước ngọt tự động giảm mạnh mười hai phần trăm sau vài tuần.", "visual_diagram:none|A downward green arrow showing soda consumption falling 12 percent on clean cream field."),
            ("Trong khi lượng người chọn uống nước tinh khiết đóng chai tăng hơn hai mươi lăm phần trăm.", "macro_prop:none|A tall glass bottle filled with clear water with light reflection on ivory canvas."),
            ("Hành vi con người thay đổi ngoạn mục mà không cần tốn một giọt ý chí nào.", "concept_metaphor:none|Clean bold unadorned black hand-lettered text reading 'HÀNH VI TỰ ĐỘNG THAY ĐỔI' floating freely on solid warm cream surface above a simple effortless forward arrow. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero sparkles, zero squiggles, zero confetti, zero ribbons, zero floor lines. 75% negative space."),
            ("Đó chính là sức mạnh tối thượng của kiến trúc môi trường vật lý.", "concept_metaphor:none|A balanced scale where physical architecture easily outweighs heavy willpower strain block."),
            ("Khi bạn tăng ma sát cho thói quen xấu, hành vi sai trái sẽ tự động biến mất.", "concept_metaphor:none|Stickman placing a smartphone into a simple clean wooden lockbox on solid warm cream surface (#F8F0DC). Clean bold unadorned black hand-lettered text reading 'TĂNG MA SÁT HÀNH VI' floating freely above. Strictly zero construction barricades, zero road blocks, zero chains, zero padlocks, zero floating popups, zero signposts, zero mazes. 75% negative space."),
            ("Thay đổi không gian bên ngoài luôn dễ dàng hơn gồng ép bên trong nội tâm.", "full_scene:CH01|Stickman stands confidently adjusting a minimalist physical organizer with peaceful mastery."),
        ],
    ),
    (
        "Khoảng trễ nhận thức ba mươi giây",
        "Minimalist pure white canvas (#FFFFFF).",
        "narrative_warm",
        "tactical_actionable",
        "actionable_resolution",
        [
            ("Từ phát hiện này, bạn có thể áp dụng ngay vũ khí thực chiến thứ nhất.", "full_scene:CH01|Stickman holds up index finger presenting rule number one with clear confident smile."),
            ("Đó là nguyên tắc khoảng trễ nhận thức ba mươi giây trước khi chuyển hướng.", "concept_metaphor:none|A clean minimalist analog stopwatch outlined in black marker with needle at 30 seconds on clean white canvas. Beside it, clean bold unadorned black hand-lettered text reading 'KHOẢNG TRỄ 30 GIÂY' floats freely on the bare field. Strictly zero postcard frames, zero boxes, zero double borders, zero banners, zero ribbons, zero corner tape, zero floating stars, zero sparkles, zero squiggles, zero confetti. 70% negative space."),
            ("Mỗi khi tay bạn ngứa ngáy muốn mở một tab mới hoặc cầm điện thoại lên.", "full_scene:CH01|Stickman sits before a simple table, right hand pausing consciously mid-air above desk surface."),
            ("Hãy dừng lại đúng ba mươi giây và cầm bút viết câu hỏi cần tìm ra giấy.", "macro_prop:CH01|A single hand writing a clear question onto a white notepad using a sharp black ink pen."),
            ("Đặt ngòi bút xuống trang giấy trắng tạo nên một lực cản vật lý cực kỳ đắt giá.", "concept_metaphor:none|A bold single straight horizontal black marker line separating stickman on left from a smartphone icon on right on minimalist pure white canvas (#FFFFFF). Clean bold unadorned black hand-lettered text reading 'KHOẢNG TRỄ' floating freely. Strictly zero concentric ripples, zero glowing circles, zero sparkle stars, zero floral bursts. 80% negative space."),
            ("Ba mươi giây ngắn ngủi đó, đủ để vỏ não lý trí kịp thời bừng tỉnh và can thiệp.", "concept_metaphor:none|A clean glowing consciousness spark outlined in black marker with soft yellow fill on pure white canvas. Clean bold unadorned black hand-lettered text reading 'LÝ TRÍ CAN THIỆP' floats freely beside. Strictly zero anatomical brains, zero circuit lines, zero card borders, zero boxes, zero stars, zero confetti. 70% negative space."),
            ("Đa phần các cơn thèm muốn bốc đồng sẽ tự động tan biến ngay trước mắt bạn.", "full_scene:CH01|Stickman exhales with relaxed shoulders, putting down pen as impulse vanishes safely."),
        ],
    ),
    (
        "Vùng chân không chín mươi phút buổi sáng",
        "Solid ivory paper texture (#F8F0DC).",
        "narrative_warm",
        "tactical_actionable",
        "actionable_resolution",
        [
            ("Vũ khí thứ hai mang tính quyết định là vùng chân không chín mươi phút.", "full_scene:CH01|Stickman presents two open fingers presenting rule number two with serene calm posture."),
            ("Mỗi sáng khi thức dậy, hãy đem chiếc điện thoại cất vào tủ ở phòng khách.", "variation:CH01|Stickman places smartphone into a wooden cabinet compartment on clean ivory surface."),
            ("Đóng chặt cánh cửa tủ gỗ và bước về bàn làm việc chỉ với cuốn sổ tay.", "variation:CH01|Stickman shuts the cabinet door firmly with a gentle decisive click sound."),
            ("Đúng chín mươi phút đầu ngày là vùng an toàn tuyệt đối không thiết bị số.", "concept_metaphor:none|A simple minimalist rising sun arc beside a clean analog clock dial outlined in black marker on solid ivory paper field. Floating beside it, clean bold unadorned black hand-lettered text reading 'VÙNG CHÂN KHÔNG 90 PHÚT'. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero sparkles, zero squiggles, zero confetti, zero ribbons, zero floor lines. 75% negative space."),
            ("Khoảng cách vật lý giữa hai căn phòng giải phóng toàn bộ áp lực ức chế.", "concept_metaphor:none|A single thin vertical black line dividing solid ivory paper texture (#F8F0DC) into two clean halves: left side shows a small smartphone icon, right side shows stickman sitting peacefully writing. Clean bold unadorned black hand-lettered text reading 'VÙNG AN TOÀN' floating freely. Strictly zero furniture, zero beds, zero nightstands, zero lamps, zero clocks, zero wall outlets, zero room clutter. 75% negative space."),
            ("Bạn không cần phải dùng ý chí để chống lại chiếc điện thoại đang ở phòng bên.", "full_scene:CH01|Stickman sits comfortably writing key manuscript notes in total peaceful flow on ivory ground."),
            ("Não bộ có thể dồn trọn vẹn dung lượng, để giải quyết bài toán khó nhất trong ngày.", "concept_metaphor:none|Stickman smiling with calm folded arms beside a simple vertical battery meter filled to 100% outlined in clean black ink on solid ivory paper texture (#F8F0DC). Clean bold unadorned black hand-lettered text reading '100% NĂNG LƯỢNG' floating cleanly above. Strictly zero anatomical brains, zero electrical wires, zero alligator clips, zero explosion stars, zero lightning bolts. 75% negative space."),
        ],
    ),
    (
        "Từ kẻ chịu trận sang kiến trúc sư không gian",
        "Clean serene white field (#FFFFFF).",
        "reflective_slow",
        "philosophical_anchor",
        "actionable_resolution",
        [
            ("Ý chí của bạn sinh ra, không phải để làm bia đỡ đạn cho các cạm bẫy công nghệ.", "full_scene:CH01|Stickman stands tall and upright, gazing forward with dignified calm on pure white field."),
            ("Nó là ngọn lửa nhỏ cần được che chắn cẩn thận trước những cơn gió bão.", "concept_metaphor:none|A small simple hand-drawn candle with gentle warm yellow flame centered on clean serene white field (#FFFFFF). Clean bold unadorned black hand-lettered text reading 'NGỌN LỬA Ý CHÍ' floating freely beside. Strictly zero hurricane lanterns, zero wind spirals, zero leaves, zero dry twigs, zero grass. 80% negative space."),
            ("Đừng cố gắng trở thành một người hùng chịu trận cô độc và kiệt quệ.", "variation:CH01|Stickman shakes head gently, letting go of a heavy iron shield onto pure white ground."),
            ("Hãy là một kiến trúc sư thông minh biết thiết kế không gian làm việc của mình.", "concept_metaphor:none|Clean bold unadorned black hand-lettered text reading 'KIẾN TRÚC SƯ KHÔNG GIAN' floating freely on clean serene white field beside a simple architect drafting triangle ruler. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero sparkles, zero squiggles, zero confetti, zero ribbons, zero floor lines. 75% negative space."),
            ("Tạo ra ma sát vật lý cho cám dỗ, và mở rộng đường đi cho sự tập trung sâu.", "concept_metaphor:none|Stickman walking peacefully forward between two simple straight parallel black marker lines on clean serene white field (#FFFFFF). Clean bold unadorned black hand-lettered text reading 'THIẾT KẾ KHÔNG GIAN' floating cleanly above. Strictly zero Roman pillars, zero columns, zero 3D perspective roads, zero technical measurement arrows, zero drafting grids. 75% negative space."),
            ("Làm chủ không gian xung quanh, bạn sẽ làm chủ hoàn toàn tâm trí mình.", "full_scene:CH01|Stickman smiles with peaceful clarity, hands resting lightly at side with 70% negative white space."),
            ("Nếu thấy video hữu ích, hãy bấm thích để ủng hộ kênh nhé.", "concept_metaphor:none|A clean minimalist doodle thumbs-up icon outlined in black marker with warm yellow fill floating freely on pure white canvas (#FFFFFF) beside clean bold unadorned black hand-lettered text reading 'THÍCH VIDEO'. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero sparkles, zero confetti, zero ribbons, zero floor lines. 80% negative space."),
            ("Và đừng quên nhấn đăng ký, để đón xem các góc nhìn tư duy tiếp theo.", "full_scene:CH01|Stickman smiling warmly with open hand gesturing toward a minimalist black bell notification icon on pure white canvas (#FFFFFF) with clean bold unadorned black hand-lettered text reading 'ĐĂNG KÝ KÊNH'. Strictly zero room clutter, zero walls, zero floor lines. 75% negative space."),
            ("Cảm ơn bạn đã đồng hành, chúc bạn làm chủ không gian của mình!", "full_scene:CH01|Stickman smiling warmly with two small wire hands waving gentle goodbye on bare pure white canvas (#FFFFFF) with 75% negative space. Strictly zero room interiors, zero furniture, zero floor lines."),
        ],
    ),
]

# ---------------------------------------------------------------------------
# STORY 9:16 (6 Scenes — 60-Second Short Explainer Spinoff)
# (title, setting, tone, spoken_style, narrative_phase, rows)
# ---------------------------------------------------------------------------
STORY_9X16: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    (
        "Cú tát kỷ luật sắt",
        "Solid warm cream canvas (#F8F0DC).",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Bạn càng cố dùng kỷ luật sắt, bạn càng nhanh bỏ cuộc.", "full_scene:CH01|Stickman wearing a simple headband sits with furrowed brow and clenched fists on solid cream ground with 70% negative space. Clean bold unadorned black hand-lettered text reading 'KỶ LUẬT THÉP' floating freely. Strictly zero room interiors, zero walls, zero floor lines, zero furniture."),
            ("Gồng mình ép bản thân tập trung.", "variation:CH01|Stickman presses both small white hands against temples with intense strain on clean cream background with 70% negative space."),
            ("Để rồi nhận lại sự kiệt sức.", "concept_metaphor:none|A small single candle flame flickering faintly before burning out on solid warm cream canvas with 75% negative space. Strictly zero room interiors, zero walls, zero clutter."),
        ],
    ),
    (
        "Bẫy lướt web vô thức",
        "Clean pure white background (#FFFFFF).",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Xóa ứng dụng trên máy, trưa lại mở mạng lướt tiếp.", "full_scene:CH01|Stickman sitting on flat white ground secretly holds a computer mouse, glancing guiltily sideways at a tiny screen outline on clean white canvas with 70% negative space. Strictly zero bedroom interior, zero dark room, zero bed, zero walls, zero floor lines."),
            ("Mở thêm một tab tra cứu,", "macro_prop:none|A single clean browser tab header titled TÀI LIỆU with a tiny magnifying glass on stark white backdrop with 75% negative space."),
            ("mười phút sau đã thấy mình ngồi đọc tin giật gân.", "concept_metaphor:none|Clean bold unadorned black hand-lettered text reading 'TIN GIẬT GÂN' floating freely on pure white canvas beside a minimalist browser tab icon. Strictly zero swirling paper tornados, zero room interiors, zero dark lighting, zero bed, zero stars, zero confetti, zero floor lines. 75% negative space."),
        ],
    ),
    (
        "Thực nghiệm hút cạn năng lượng",
        "Solid ivory neutral field (#F8F0DC).",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Đại học Texas đã chứng minh một sự thật bất ngờ.", "concept_metaphor:none|Clean bold unadorned black hand-lettered text reading 'ĐẠI HỌC TEXAS' floating freely on solid ivory field with a minimalist academic seal icon. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero confetti. 75% negative space."),
            ("Để điện thoại trên bàn rút cạn bộ nhớ làm việc.", "macro_prop:none|A black smartphone lying flat on ivory surface emitting subtle concentric ripple waves with 70% negative space."),
            ("Kể cả khi bạn đã tắt nguồn úp mặt máy.", "still_life:none|The black smartphone lies completely face-down on flat ivory surface with a small silent power indicator symbol with 75% negative space."),
            ("Não bạn vẫn phải gồng mình,", "full_scene:CH01|Stickman sits on solid ivory field with arms folded, gritting teeth with resolute strain on bare ivory canvas with 70% negative space."),
            ("để chống lại sự cám dỗ.", "variation:CH01|Stickman turns head away from the phone silhouette with determined frown on solid ivory ground with 70% negative space."),
        ],
    ),
    (
        "Cạn kiệt vỏ não trước trán",
        "Clean solid white canvas (#FFFFFF).",
        "analytical_crisp",
        "mechanistic_dissection",
        "empirical_conflict",
        [
            ("Ý chí con người là hữu hạn.", "concept_metaphor:none|Clean bold unadorned black hand-lettered text reading 'Ý CHÍ HỮU HẠN' floating freely on pure white canvas beside a small fading spark icon. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero sparkles, zero confetti, zero ribbons. 75% negative space."),
            ("Não bộ phải liên tục bật cơ chế ức chế chủ động.", "full_scene:CH01|Stickman touches index finger to temple with thoughtful focused expression on clean white ground with clean bold unadorned black text reading 'ỨC CHẾ CHỦ ĐỘNG' floating beside head. Strictly zero anatomical brains, zero room interiors, zero walls, zero clutter. 70% negative space."),
            ("Bạn càng gồng ép kìm nén,", "variation:CH01|Stickman presses both hands to forehead with tense grimacing expression on clean white canvas with 70% negative space."),
            ("vùng vỏ não trước trán càng nhanh sập nguồn.", "concept_metaphor:none|A clean horizontal battery outline dropping to a single empty red line with a small exclamation symbol on stark white backdrop. Strictly zero room interiors, zero 3D shading. 75% negative space."),
            ("Và khiến bạn sa ngã gấp đôi.", "full_scene:CH01|Stickman slumps forward sitting on bare white ground with drooped shoulders and exhausted sigh on pure white field with 70% negative space."),
        ],
    ),
    (
        "Ma sát hành vi ba mươi giây",
        "Solid warm cream surface (#F8F0DC).",
        "narrative_warm",
        "tactical_actionable",
        "actionable_resolution",
        [
            ("Thay đổi cách sắp đặt vật lý,", "concept_metaphor:none|A minimalist balance scale tipping favorably toward physical environment icons rather than heavy strain on solid warm cream canvas with 70% negative space."),
            ("hiệu quả hơn gồng ép ý chí.", "concept_metaphor:none|A simple curved barrier line guiding an arrow smoothly past a temptation dot on warm cream background with 75% negative space."),
            ("Tăng ma sát môi trường làm giảm thói quen xấu.", "concept_metaphor:none|Clean bold unadorned black hand-lettered text reading 'TĂNG MA SÁT' floating freely on solid warm cream surface beside a simple rough textured obstacle icon. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero sparkles, zero checkmarks, zero confetti. 75% negative space."),
            ("Cầm bút viết ra giấy câu bạn cần tìm trước khi mở tab mới.", "macro_prop:CH01|Stickman wire hand holding a simple black pen writing on a clean white paper page on 100% solid flat warm cream surface (#F8F0DC). Clean bold unadorned black text reading 'VIẾT RA GIẤY' floating cleanly. Strictly zero dark table corners, zero furniture, zero room clutter. 80% negative space."),
            ("Tạo khoảng trễ ba mươi giây,", "concept_metaphor:none|A minimalist analog stopwatch with needle paused at thirty seconds beside clean bold unadorned black hand-lettered text reading 'KHOẢNG TRỄ 30 GIÂY' on solid warm cream surface with 75% negative space. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero confetti."),
            ("để cắt đứt cơn nghiện vô thức.", "full_scene:CH01|Stickman smiles with quiet calm relief on bare cream canvas with 70% negative space. Strictly zero room interiors, zero walls, zero floor lines."),
        ],
    ),
    (
        "Vùng chân không chín mươi phút",
        "Clean serene white field (#FFFFFF).",
        "reflective_slow",
        "tactical_actionable",
        "actionable_resolution",
        [
            ("Cất máy sang phòng khác đúng chín mươi phút buổi sáng.", "full_scene:CH01|Stickman places smartphone inside a simple wooden cabinet door on flat white ground with 70% negative space. Strictly zero bedroom interior, zero clutter."),
            ("Đừng làm anh hùng chịu trận.", "concept_metaphor:none|Clean bold unadorned black hand-lettered text reading 'ĐỪNG LÀM ANH HÙNG' floating freely on stark white field with a small crossed-out cape icon. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero sparkles, zero confetti, zero ribbons. 75% negative space."),
            ("Hãy làm kiến trúc sư cho bàn làm việc của bạn.", "full_scene:CH01|Stickman smiles with peaceful clarity, folding hands gently on flat white field with 70% open negative space. Strictly zero room interiors, zero walls, zero floor lines, zero clutter."),
            ("Bấm theo dõi kênh để làm chủ sự tập trung mỗi ngày nhé!", "full_scene:CH01|Stickman smiles warmly with friendly expression, holding a small clean notification bell with unadorned bold black text reading 'THEO DÕI KÊNH' floating freely on stark white field with 75% open negative space. Strictly zero card borders, zero boxes, zero banners, zero corner tape, zero floating stars, zero sparkles, zero confetti, zero room interiors, zero walls, zero floor lines, zero clutter."),
        ],
    ),
]


def build_sources() -> list[dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "Brain Drain: The Mere Presence of One's Own Smartphone Reduces Available Cognitive Capacity",
            "reference": "Adrian F. Ward, Kristen Duke, Ayelet Gneezy & Maarten W. Bos (2017). Journal of the Association for Consumer Research.",
            "facts": [
                "Để điện thoại trên bàn rút cạn bộ nhớ làm việc.",
                "Não bộ phải kích hoạt ức chế chủ động liên tục.",
                "Để điện thoại trong tầm mắt rút cạn bộ nhớ làm việc.",
                "Não bộ phải liên tục kích hoạt cơ chế ức chế chủ động.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Choice Architecture and Environmental Friction in Habit Disruption",
            "reference": "Anne N. Thorndike et al. (2012). American Journal of Public Health.",
            "facts": [
                "Tăng ma sát môi trường làm giảm thói quen xấu.",
                "Thay đổi cách sắp đặt vật lý hiệu quả hơn gồng ép ý chí.",
                "Thay đổi cách sắp đặt không gian hiệu quả hơn gồng ép ý chí.",
                "Tăng ma sát môi trường vật lý làm giảm hành vi xấu tự động.",
                "Thay đổi không gian bên ngoài luôn dễ dàng hơn gồng ép bên trong nội tâm.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Ego Depletion: Is the Active Self a Limited Resource?",
            "reference": "Roy F. Baumeister et al. (1998). Journal of Personality and Social Psychology.",
            "facts": [
                "Cố gồng mình cưỡng lại cám dỗ làm cạn kiệt ý chí.",
                "Người kiềm chế ăn bánh quy bỏ cuộc giải đố nhanh gấp đôi.",
            ],
        },
        {
            "id": "SRC04",
            "title": "Variable Ratio Schedule and Dopamine Anticipation",
            "reference": "Robert Sapolsky & B.F. Skinner on Variable Ratio Reinforcement Schedules.",
            "facts": [
                "Kích thích biến thiên ngẫu nhiên kích hoạt giải phóng dopamine cực đại.",
                "Bộ não hồi hộp vì kỳ vọng phần thưởng chứ không phải bản thân phần thưởng.",
            ],
        },
    ]


def build_human_editorial() -> HumanEditorialSpec:
    return HumanEditorialSpec(
        topic_dilemmas=[
            "Càng cố gắng gồng ép ý chí để chống lại cám dỗ số, con người càng nhanh kiệt sức và sa vào trì hoãn nặng nề hơn.",
            "Không thể đoạn tuyệt cực đoan với điện thoại và máy tính trong môi trường làm việc số hiện đại.",
        ],
        dynamic_questions=[
            "Tại sao việc cố gắng không nhìn vào điện thoại lại khiến não bộ mệt mỏi ngang với việc giải một bài toán khó?",
            "Vì sao các trào lưu kỷ luật sắt hay dopamine detox cực đoan hầu như luôn thất bại sau vài ngày?",
            "Làm thế nào để thiết lập rào cản hành vi mà không cần phải gồng ép ý chí mỗi phút giây?",
        ],
        author_raw_input="Ý chí chỉ là tài nguyên hữu hạn. Người thông minh không gồng mình chống lại cám dỗ mà thiết kế môi trường để cám dỗ không xuất hiện trước mắt.",
        editorial_stance="Nguyên nhân khiến người ta thất bại khi cai nghiện mạng xã hội không phải vì thiếu ý chí hay lười biếng. Não bộ con người tiến hóa để phản ứng với kích thích cận kề. Khi điện thoại nằm trong tầm mắt hoặc trình duyệt chỉ cách 1 cú click chuột, cơ chế ức chế chủ động phải làm việc liên tục ở tầng tiềm thức, âm thầm đốt cạn dung lượng bộ nhớ làm việc. Gồng ép ý chí thô là chiến lược tệ nhất vì ý chí là nguồn tài nguyên sinh học cực kỳ dễ cạn kiệt.",
        expanded_content_ideas=[
            {
                "idea_id": "IDEA_01",
                "angle_type": "analysis",
                "summary": "Phân tích cơ chế não cạn kiệt nhận thức khi có kích thích cận kề.",
                "narrative_integration": "Đưa vào phân cảnh phân tích cơ chế nhân quả và thí nghiệm đối chứng.",
                "target_narrative_phase": "causal_mechanism",
            },
            {
                "idea_id": "IDEA_02",
                "angle_type": "commentary",
                "summary": "Phản biện trào lưu kỷ luật sắt và dopamine detox cực đoan.",
                "narrative_integration": "Đưa vào phân cảnh phản biện lật ngược vấn đề.",
                "target_narrative_phase": "counter_argument",
            },
            {
                "idea_id": "IDEA_03",
                "angle_type": "evaluation",
                "summary": "Đánh giá hiệu quả của khoảng trễ nhận thức 30 giây và vùng chân không 90 phút.",
                "narrative_integration": "Đưa vào phân cảnh giải pháp chuyển hóa thực tế.",
                "target_narrative_phase": "takeaway",
            },
        ],
    )


def build_characters() -> list[dict[str, Any]]:
    return [
        {
            "id": "CH01",
            "name": "Người làm việc trí óc",
            "role": "knowledge_worker",
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
    scenes[3].source_ids = ["SRC03"]
    scenes[3].claim_facts = [
        ("Trong khi nhóm thứ hai bị ép phải ăn củ cải đỏ, và tuyệt đối không chạm vào bánh.", "SRC03", "Cố gồng mình cưỡng lại cám dỗ làm cạn kiệt ý chí."),
    ]
    scenes[4].source_ids = ["SRC03"]
    scenes[4].claim_facts = [
        ("Trong khi nhóm chỉ được ăn rau củ buông bút bỏ cuộc chỉ sau tám phút ngắn ngủi.", "SRC03", "Người kiềm chế ăn bánh quy bỏ cuộc giải đố nhanh gấp đôi."),
    ]
    scenes[7].source_ids = ["SRC01"]
    scenes[7].claim_facts = [
        ("Các nhà nghiên cứu chia ngẫu nhiên họ thành ba nhóm hoàn toàn riêng biệt.", "SRC01", "Để điện thoại trong tầm mắt rút cạn bộ nhớ làm việc."),
    ]
    scenes[9].source_ids = ["SRC01"]
    scenes[9].claim_facts = [
        ("Câu trả lời nằm ở cơ chế ức chế chủ động sâu bên trong bộ não.", "SRC01", "Não bộ phải liên tục kích hoạt cơ chế ức chế chủ động."),
    ]
    scenes[10].source_ids = ["SRC04"]
    scenes[10].claim_facts = [
        ("Đằng sau màn hình là cơ chế phần thưởng biến thiên ngẫu nhiên.", "SRC04", "Kích thích biến thiên ngẫu nhiên kích hoạt giải phóng dopamine cực đại."),
        ("Bộ não hồi hộp vì kỳ vọng phần thưởng, chứ không phải vì bản thân phần thưởng đó.", "SRC04", "Bộ não hồi hộp vì kỳ vọng phần thưởng chứ không phải bản thân phần thưởng."),
    ]
    scenes[14].source_ids = ["SRC02"]
    scenes[14].claim_facts = [
        ("Khi bạn tăng ma sát cho thói quen xấu, hành vi sai trái sẽ tự động biến mất.", "SRC02", "Tăng ma sát môi trường vật lý làm giảm hành vi xấu tự động."),
        ("Thay đổi không gian bên ngoài luôn dễ dàng hơn gồng ép bên trong nội tâm.", "SRC02", "Thay đổi cách sắp đặt không gian hiệu quả hơn gồng ép ý chí."),
    ]

    return ResearchedTopic(
        topic="Nghịch Lý Ý Chí: Vì Sao Bạn Càng Cố Tập Trung Càng Trì Hoãn?",
        audience="Người đi làm, sinh viên và người làm việc trí óc thường xuyên bị xao nhãng bởi cám dỗ số",
        goal="Giải mã nghịch lý ý chí qua thí nghiệm bánh quy Baumeister, Brain Drain và cỗ máy dopamine",
        video_type="research_explainer",
        min_duration=400.0,
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
            youtube_title="Vì Sao Bạn Càng Cố Tập Trung Càng Trì Hoãn?",
            visual_hook="Nhân vật stickman tự lấy dây thừng trói chặt mình vào ghế trước bàn làm việc với vẻ mặt căng thẳng tột độ, nhưng bàn tay sau lưng vẫn lén lút bấm chuột mở trình duyệt web.",
            text_overlay="Ý CHÍ LÀ BẪY",
            contrast_pair="Gồng ép ý chí thô vs. Kiến trúc môi trường",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "nghịch lý ý chí",
                "brain drain",
                "cạn kiệt nhận thức",
                "cách tập trung làm việc",
                "choice architecture",
            ],
            thumbnail_prompt=(
                "Orthographic 2D hand-drawn doodle poster. 60% of the frame shows a stickman character tied to an "
                "office chair with heavy rope looking intensely disciplined on solid warm cream canvas (#F8F0DC), "
                "while his right hand behind his back is secretly holding a computer mouse clicking on a glowing "
                "browser icon. Flat solid warm sand background (#F8F0DC), wobbly black marker contours (#000000), "
                "flat MS-paint fills (shirt in #3B82C4, rope in #F2B88B). 40% clean negative space on the top right "
                "holding large bold yellow hand-lettered text 'Ý CHÍ LÀ BẪY' with thick black outline. Zero room "
                "interiors, zero walls, zero floor lines, zero decorative clutter. No 3D shadows, no dark vignette."
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
        ("Để điện thoại trên bàn rút cạn bộ nhớ làm việc.", "SRC01", "Để điện thoại trên bàn rút cạn bộ nhớ làm việc."),
    ]
    scenes[3].source_ids = ["SRC01"]
    scenes[3].claim_facts = [
        ("Não bộ phải liên tục bật cơ chế ức chế chủ động.", "SRC01", "Não bộ phải kích hoạt ức chế chủ động liên tục."),
    ]
    scenes[4].source_ids = ["SRC02"]
    scenes[4].claim_facts = [
        ("Thay đổi cách sắp đặt vật lý, hiệu quả hơn gồng ép ý chí.", "SRC02", "Thay đổi cách sắp đặt vật lý hiệu quả hơn gồng ép ý chí."),
        ("Tăng ma sát môi trường làm giảm thói quen xấu.", "SRC02", "Tăng ma sát môi trường làm giảm thói quen xấu."),
    ]

    return ResearchedTopic(
        topic="Vì Sao Càng Cố Kỷ Luật Càng Dễ Bỏ Cuộc? (Bản Dọc 60 Giây)",
        audience="Người trẻ, sinh viên và người làm việc số lướt video ngắn trên di động",
        goal="Tóm gọn nghịch lý ý chí trong 60 giây và hướng dẫn khoảng trễ 30 giây cùng vùng chân không 90 phút",
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
            youtube_title="Vì Sao Càng Cố Kỷ Luật Càng Dễ Bỏ Cuộc?",
            visual_hook="Nhân vật stickman đeo băng rôn Kỷ Luật Thép với khuôn mặt căng thẳng nhìn màn hình máy tính",
            text_overlay="Ý CHÍ LÀ BẪY",
            contrast_pair="Kỷ luật thép vs. Ma sát hành vi",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "kỷ luật sắt",
                "nghịch lý ý chí",
                "brain drain",
                "trì hoãn",
                "short 9x16",
            ],
            thumbnail_prompt=(
                "Orthographic 2D hand-drawn doodle poster in 9:16 vertical ratio. A stickman character wearing a "
                "disciplined headband staring intensely on solid warm cream canvas (#F8F0DC), with battery charge "
                "meter above head depleting to red. Flat solid warm sand background (#F8F0DC), wobbly black marker contours "
                "(#000000), flat MS-paint fills (shirt in #3B82C4). Clean negative space at the top holding large bold "
                "yellow text 'Ý CHÍ LÀ BẪY' with thick black outline. Strictly zero room interiors, zero walls, zero floor lines, "
                "zero decorative clutter. No 3D shadows, no dark vignette."
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
    parser = argparse.ArgumentParser(description="Build Willpower Paradox 16:9 & 9:16 production blueprint.")
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
            job_name = "willpower-paradox-16x9"
        else:
            topic = build_topic_9x16()
            job_name = "willpower-paradox-9x16"

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
        print("[SUCCESS] Toàn bộ gói hồ sơ kỹ thuật cho Willpower Paradox đã hoàn thành và đạt chuẩn!")
        return 0
    else:
        print("[FAILURE] Phát hiện lỗi trong quá trình đóng gói hồ sơ kỹ thuật.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
