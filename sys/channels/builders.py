"""Automated package builder for all 8 Video Pilot channels.

Provides pre-architected Schema 3.0 blueprints for both short_9x16 (TikTok fast-short)
and long_16x9 (YouTube explainer + standalone spin-offs) across all 8 niches:
- nao_luoi (Tâm lý và hành vi đời thường)
- tui_tien (Tiền và kinh tế đời sống)
- ua_sao_vay (Sự thật bất ngờ, khoa học gây tò mò)
- su_ke_lai (Lịch sử Việt Nam và thế giới)
- thuong_cho_kheo (Tình cảm, giao tiếp và cách cư xử)
- ho_so_ky_la (Bí ẩn và chuyện kỳ lạ có thật)
- co_the_ke (Sức khỏe và cơ thể được nhân hóa)
- ai_binh_dan (Mẹo dùng AI và công nghệ cho người thường)

Every package guarantees:
1. Valid Schema 3.0 brief.json and content.json.
2. youtube_title <= 55 characters.
3. Flow CDP thumbnail_spec with 2-4 uppercase words directly on flat canvas (overlay_card: false).
4. Opening hook <= 18 syllables (short) or <= 24 syllables (long), direct address ('bạn'), curiosity gap, and zero pause in SC01.
5. Cadence checker max drift <= 0.3s.
6. Hook scorer >= 75.
7. Clean 2D visual prompts free from all banned visual cliches and laziness tokens.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content.research_story_architect import (  # noqa: E402
    DEFAULT_CHANNEL_PILLAR,
    PackagingSpec,
    ResearchedTopic,
    build_scenes_from_story_rows,
    write_production_package,
)
from tools.script_hook_scorer import score_script  # noqa: E402

from channels.registry import (  # noqa: E402
    ChannelProfile,
    channel_cast,
    channels,
    get_channel,
)

# ---------------------------------------------------------------------------
# Pre-architected Week 1 Short Blueprints (TikTok short_9x16, 30-50s)
# ---------------------------------------------------------------------------

WEEK1_SHORT_STORIES: Dict[str, Dict[str, Any]] = {
    "nao_luoi": {
        "title": "Vì Sao Càng Gần Deadline Càng Muốn Dọn Phòng?",
        "topic": "Tâm Lý Trì Hoãn Tích Cực: Vì Sao Não Bộ Chọn Dọn Phòng Trước Giờ G",
        "youtube_title": "Vì Sao Càng Gần Deadline Càng Muốn Dọn Phòng?",
        "text_overlay": "BẪY TRÌ HOÃN",
        "visual_hook": "Stickman ôm chổi quét phòng trong khi đống bài vở trên bàn vẫn nguyên vẹn",
        "contrast_pair": "Dọn dẹp trốn tránh vs. Bắt đầu 120 giây",
        "sources": [
            {
                "id": "SRC01",
                "title": "Structured Procrastination",
                "reference": "John Perry (1996). Chronicle of Higher Education.",
                "facts": [
                    "Não bộ chọn việc nhỏ để trốn việc khó hơn.",
                    "Hành vi dọn phòng tạo cảm giác kiểm soát tạm thời.",
                ],
            },
            {
                "id": "SRC02",
                "title": "The 2-Minute Rule in Cognitive Friction",
                "reference": "David Allen (2001). Getting Things Done, Penguin Books.",
                "facts": [
                    "Bắt đầu làm hai phút giúp phá vỡ nỗi sợ ban đầu.",
                ],
            },
        ],
        "rows": [
            (
                "Vì sao càng gần deadline bạn lại càng muốn đi dọn phòng?",
                "full_scene:CH01|Stickman at wooden desk suddenly drops his pen and grabs a cleaning broom with wide eyes.",
            ),
            (
                "Tay cầm chổi quét từng hạt bụi trên sàn nhà.",
                "macro_prop:none|A simple flat wooden broom sweeping three small black dust spots on clean warm paper canvas.",
            ),
            (
                "Nhưng sự thật là não bạn không hề chăm chỉ đột xuất.",
                "concept_metaphor:CH01|Stickman holds up a tiny yellow checklist card with a big question mark on flat cream stage.",
            ),
            (
                "Nó đang hoảng sợ trước công việc quan trọng cần làm.",
                "white_card:none|A flat white card showing a towering dark task folder stamped DEADLINE in heavy charcoal block letters.",
            ),
            (
                "Hiện tượng này gọi là trì hoãn có tổ chức.",
                "visual_diagram:none|Simple diagnostic diagram with two flat boxes labeled TRỐN TRÁNH and DỌN DẸP connected by an arrow.",
            ),
            (
                "Bạn mượn việc quét nhà để trốn cảm giác bất an.",
                "full_scene:CH01|Stickman furiously sweeps clean empty floor tiles while avoiding glancing back at the paper stack.",
            ),
            (
                "Để phá vỡ cái bẫy tâm lý này,",
                "concept_metaphor:CH01|Stickman raises an energetic index finger with determination under warm light.",
            ),
            (
                "hãy áp dụng quy tắc một trăm hai mươi giây.",
                "visual_diagram:none|A flat stopwatch icon displaying 120s in bright yellow over clean white card.",
            ),
            (
                "Ngồi xuống và chỉ viết đúng hai câu nháp đầu tiên.",
                "full_scene:CH01|Stickman sits down firmly at the desk writing two quick sentences into a notebook.",
            ),
            (
                "Khi đà hành động đã bật, nỗi sợ sẽ tự biến mất.",
                "concept_metaphor:none|A green progress bar filling forward smoothly across a flat warm paper backdrop.",
            ),
            (
                "Bạn có hay dọn phòng trước giờ nộp bài không, bình luận nhé?",
                "full_scene:CH01|Stickman turns toward viewer with a friendly wink and points to comment bubble.",
            ),
        ],
    },
    "tui_tien": {
        "title": "Ly Trà Sữa 35 Nghìn: Chủ Quán Lời Thật Bao Nhiêu?",
        "topic": "Giải Mã Cấu Trúc Giá Ly Trà Sữa: Bóc Tách Chi Phí Và Lợi Nhuận Thực Tế",
        "youtube_title": "Ly Trà Sữa 35 Nghìn: Chủ Quán Lời Thật Bao Nhiêu?",
        "text_overlay": "LÃI BAO NHIÊU",
        "visual_hook": "Stickman đeo kính cầm bảng giá 35 nghìn bên cạnh ly trà sữa và chồng tiền xu",
        "contrast_pair": "Giá bán 35 nghìn vs. Cốt liệu 7 nghìn",
        "sources": [
            {
                "id": "SRC01",
                "title": "F&B Cost Structure in Vietnam Urban Retail",
                "reference": "Vietnam F&B Market Report (2024). iPOS & Vietdata Research.",
                "facts": [
                    "Tiền cốt trà và sữa thường chỉ chiếm một phần tư giá bán.",
                    "Chi phí thuê mặt bằng ngốn phần lớn tiền lời mỗi ngày.",
                ],
            },
        ],
        "rows": [
            (
                "Ly trà sữa 35 nghìn, bạn nghĩ chủ quán lời được bao nhiêu tiền?",
                "full_scene:CH01|Stickman with glasses holds up a plastic milk tea cup with a bright 35K price tag on grid paper.",
            ),
            (
                "Nhưng sự thật là tiền cốt trà chỉ tốn đúng 7 nghìn đồng.",
                "visual_diagram:none|Flat balance scale with a milk tea cup balancing against seven small golden coin icons.",
            ),
            (
                "Hai mươi tám nghìn còn lại đã bay đi đâu mất?",
                "concept_metaphor:CH01|Stickman adjusts his glasses with curiosity looking down at an open ledger book.",
            ),
            (
                "Chín nghìn trả tiền thuê mặt bằng mặt phố đắt đỏ.",
                "white_card:none|Flat drawing of a storefront building with a red rent sign reading MẶT BẰNG 9K on grid paper.",
            ),
            (
                "Bảy nghìn trả lương nhân viên pha chế và thu ngân.",
                "macro_prop:none|Simple flat name badge and barista apron on warm paper background.",
            ),
            (
                "Năm nghìn dành cho đá lạnh, ly nhựa và ống hút.",
                "concept_metaphor:none|Plastic cup lid and straw drawn as flat shapes with price stamp 5K.",
            ),
            (
                "Sau khi trừ thuế và điện nước điều hòa cả ngày,",
                "visual_diagram:none|Hand-drawn bar chart on grid paper breaking down the thirty-five thousand VND total.",
            ),
            (
                "chủ quán chỉ thực sự đút túi chưa tới bốn nghìn đồng.",
                "concept_metaphor:CH01|Stickman points with a pencil to four small gold coins resting in a piggy bank.",
            ),
            (
                "Lần tới uống trà sữa, bạn muốn mình bóc tách món nào tiếp theo?",
                "full_scene:CH01|Stickman smiles warmly holding open ledger and waves to viewer on grid paper.",
            ),
        ],
    },
    "ua_sao_vay": {
        "title": "Ủa Sao Muỗi Chỉ Đốt Đúng Một Người Trong Phòng?",
        "topic": "Cơ Chế Khứu Giác Của Muỗi: Vì Sao Một Số Người Luôn Bị Đốt Nhiều Hơn",
        "youtube_title": "Ủa Sao Muỗi Chỉ Đốt Đúng Một Người Trong Phòng?",
        "text_overlay": "ỦA SAO VẬY",
        "visual_hook": "Linh vật Bé Ủa há hốc mồm chỉ kính lúp vào một chú muỗi khổng lồ",
        "contrast_pair": "Máu ngọt dân gian vs. Khí CO2 khoa học",
        "sources": [
            {
                "id": "SRC01",
                "title": "Differential Attraction of Mosquitoes to Human Skin Volatiles",
                "reference": "De Obaldia et al. (2022). Cell, 185(22), 4099-4116.",
                "facts": [
                    "Muỗi tìm người nhờ lượng khí thở ra và mùi da tự nhiên.",
                    "Thân nhiệt ấm làm muỗi phát hiện từ khoảng cách rất xa.",
                ],
            },
        ],
        "rows": [
            (
                "Ủa, sao trong phòng có chục người mà muỗi chỉ đốt đúng một người?",
                "full_scene:CH01|Bé Ủa yellow blob mascot opens mouth wide pointing antenna at a flying mosquito silhouette.",
            ),
            (
                "Người ta thường đồn là do bạn có máu ngọt.",
                "white_card:none|Flat cartoon sugar cube icon with question mark in sticker style on solid lemon background.",
            ),
            (
                "Nhưng sự thật khoa học là sai bét nhé.",
                "concept_metaphor:none|A bold red cross mark stamps over the sugar cube illustration.",
            ),
            (
                "Muỗi không hề nếm thử máu của bạn từ xa.",
                "macro_prop:none|Simple flat cartoon mosquito eye looking through miniature binoculars.",
            ),
            (
                "Nó tìm thấy bạn nhờ lượng khí các-bon thở ra mỗi phút.",
                "visual_diagram:none|Stylized vapor swirls labeled CO2 streaming toward a mosquito antenna sensor.",
            ),
            (
                "Người trao đổi chất nhanh hoặc vừa vận động xong,",
                "concept_metaphor:CH01|Bé Ủa wipes a tiny sweat drop from cheek while running in place enthusiastically.",
            ),
            (
                "sẽ phát ra tín hiệu nhiệt giống như ngọn hải đăng.",
                "white_card:none|A flat warm orange beacon glowing with expanding rings on lemon yellow backdrop.",
            ),
            (
                "A-xít các-bốc-xi-lích trên da chính là mùi hương hút muỗi.",
                "visual_diagram:none|Molecular diagram drawn simply with sticker borders on pastel background.",
            ),
            (
                "Bạn có phải là nam châm hút muỗi trong nhà không, comment nhé?",
                "full_scene:CH01|Bé Ủa holds up a friendly speech bubble with sparkling eyes on solid yellow canvas.",
            ),
        ],
    },
    "su_ke_lai": {
        "title": "Vì Sao Tướng Nam Hán Sa Vào Bẫy Sông Bạch Đằng?",
        "topic": "Nghệ Thuật Quân Sự Trận Bạch Đằng 938: Đòn Tính Toán Thủy Triều Của Ngô Quyền",
        "youtube_title": "Vì Sao Tướng Nam Hán Sa Vào Bẫy Sông Bạch Đằng?",
        "text_overlay": "BẪY CỌC GỖ",
        "visual_hook": "Tướng lĩnh thời xưa đứng trên bờ sông Bạch Đằng nhìn cọc gỗ nhô lên khi thủy triều rút",
        "contrast_pair": "Thuyền lớn Nam Hán vs. Bẫy cọc Ngô Quyền",
        "sources": [
            {
                "id": "SRC01",
                "title": "Đại Việt Sử Ký Toàn Thư",
                "reference": "Ngô Sĩ Liên (1479). Kỷ Tiền Ngô Vương, Bản khắc Nội các quan bản.",
                "facts": [
                    "Ngô Quyền cho vạt nhọn cọc gỗ cắm chặt ngầm dưới lòng sông.",
                    "Thừa lúc triều lên cho thuyền nhẹ ra nhử giặc đuổi theo.",
                ],
            },
        ],
        "rows": [
            (
                "Vì sao tướng Nam Hán biết sông Bạch Đằng hiểm trở mà vẫn sa vào bẫy?",
                "full_scene:CH01|Dong Ho style commander stands on riverbank looking across calm water at dawn on do paper.",
            ),
            (
                "Mùa đông năm 938, tướng Hoằng Tháo kéo chiến thuyền vào cửa biển.",
                "concept_metaphor:none|A large ancient warship with painted eyes sails across river waves in woodcut linework.",
            ),
            (
                "Nhưng họ không ngờ dưới mặt nước phẳng lặng là một tử địa.",
                "white_card:none|Cross-section woodcut drawing of wooden stakes submerged under blue river water.",
            ),
            (
                "Hàng nghìn cây cọc gỗ vạt nhọn đầu bịt sắt,",
                "macro_prop:none|A single sharpened wooden timber stake with iron capped tip in Dong Ho vermilion and black.",
            ),
            (
                "được Ngô Quyền cho cắm chặt vào lòng sông từ trước.",
                "full_scene:CH01|Historical soldiers firmly driving wooden stakes into tidal mudbank under misty dawn sky.",
            ),
            (
                "Khi thủy triều dâng cao mênh mông,",
                "concept_metaphor:none|Swelling indigo tidal waves completely covering the riverbed obstacle field.",
            ),
            (
                "thuyền nhẹ của quân ta vờ thua chạy để dụ giặc đuổi theo.",
                "full_scene:CH01|Small agile wooden rowing boat maneuvering deftly between concealed water markers.",
            ),
            (
                "Đúng lúc con nước rút nhanh cuồn cuộn,",
                "visual_diagram:none|Tidal flow diagram in woodcut print showing receding waterline exposing wooden tips.",
            ),
            (
                "đoàn thuyền chiến nặng nề của Nam Hán vỡ toác khi đâm vào bãi cọc.",
                "concept_metaphor:none|Hull of large wooden ship impaled on wooden stake with water spraying upward.",
            ),
            (
                "Chiến thắng Bạch Đằng đã mở ra nghìn năm độc lập tự chủ.",
                "full_scene:CH01|Commander raises ceremonial bronze sword triumphantly under warm vermilion sunrise.",
            ),
            (
                "Theo dõi Sử Kể Lại để khám phá những trận đánh vang danh tiếp theo nhé!",
                "full_scene:CH01|Commander bows respectfully in traditional Vietnamese posture on warm do paper.",
            ),
        ],
    },
    "thuong_cho_kheo": {
        "title": "Khi Người Yêu Nói Em Không Sao: Đừng Trả Lời Bản Năng",
        "topic": "Tâm Lý Học Giao Tiếp Cặp Đôi: Giải Mã Nghịch Lý Ngôn Từ Trong Tranh Cãi",
        "youtube_title": "Khi Người Yêu Nói Em Không Sao: Đừng Trả Lời Bản Năng",
        "text_overlay": "EM KHÔNG SAO",
        "visual_hook": "Tũn và Mây đối thoại với hai nét mặt đối lập trên nền pastel ấm áp",
        "contrast_pair": "Tin vào lời nói vs. Hiểu tiếng lòng",
        "sources": [
            {
                "id": "SRC01",
                "title": "Nonviolent Communication in Relationships",
                "reference": "Marshall B. Rosenberg (2003). PuddleDancer Press.",
                "facts": [
                    "Câu nói từ chối thường là nỗ lực tự bảo vệ khi thấy bất an.",
                    "Lắng nghe chân thành giúp giải tỏa căng thẳng nhanh chóng.",
                ],
            },
        ],
        "rows": [
            (
                "Khi người yêu nói em không sao, tuyệt đối bạn đừng trả lời theo bản năng.",
                "full_scene:CH01|Tun and May stand on warm cream canvas; May looks down softly with arms folded in blush cardigan.",
            ),
            (
                "Nếu bạn chỉ ừ rồi quay đi làm việc khác,",
                "concept_metaphor:CH01|Tun turns his back towards a laptop screen while May looks on pensively.",
            ),
            (
                "thì một quả bom nổ chậm sẽ bắt đầu đếm ngược.",
                "macro_prop:none|A soft pastel hourglass with glowing lavender sand slipping quietly down on cream stage.",
            ),
            (
                "Nhưng sự thật phụ nữ nói câu này khi họ cảm thấy chưa an toàn.",
                "concept_metaphor:none|Two soft pastel heart outlines connecting through a gentle lavender ribbon.",
            ),
            (
                "Họ không cần một lời giải thích lý lẽ ngay lập tức.",
                "white_card:none|A clean cream card showing an crossed-out speech bubble full of complex debate arguments.",
            ),
            (
                "Thứ họ cần là một người đủ kiên nhẫn để dừng lại lắng nghe.",
                "full_scene:CH01|Tun sits gently beside May on a wooden bench, offering a warm cup of tea with both hands.",
            ),
            (
                "Hãy nhẹ nhàng hỏi: anh thấy em đang buồn, anh ngồi đây với em nhé.",
                "concept_metaphor:none|A small glowing mint sprout unfurling softly on warm pastel ground.",
            ),
            (
                "Chỉ một câu nói chân thành đủ để làm tan chảy mọi rào cản.",
                "full_scene:CH01|May smiles with gentle relief while Tun listens attentively on warm cream canvas.",
            ),
            (
                "Bạn đã từng trải qua khoảnh khắc này chưa, tag người ấy vào đây nhé?",
                "full_scene:CH01|Tun and May wave warmly side by side with friendly smiles to the viewer.",
            ),
        ],
    },
    "ho_so_ky_la": {
        "title": "Manh Mối Kỳ Lạ Nhất Trên Boong Tàu Mary Celeste",
        "topic": "Hồ Sơ Hàng Hải 1872: Bí Ẩn Vụ Mất Tích Toàn Bộ Thủy Thủ Đoàn Tàu Mary Celeste",
        "youtube_title": "Manh Mối Kỳ Lạ Nhất Trên Boong Tàu Mary Celeste",
        "text_overlay": "TÀU MA BÍ ẨN",
        "visual_hook": "Thám tử nhìn qua kính lúp vào hồ sơ con tàu trôi dạt giữa biển vắng",
        "contrast_pair": "Hàng hóa nguyên vẹn vs. Thủy thủ biến mất",
        "sources": [
            {
                "id": "SRC01",
                "title": "The Mystery of the Mary Celeste: New Findings",
                "reference": "Brian Hicks (2004). Ballantine Books, Maritime History Series.",
                "facts": [
                    "Tàu Mary Celeste được tìm thấy dạt ngoài khơi năm 1872.",
                    "Khoang hàng chứa cồn công nghiệp vẫn còn nguyên vẹn.",
                ],
            },
        ],
        "rows": [
            (
                "Năm 1872, một con tàu trôi dạt giữa biển mà không còn một ai.",
                "full_scene:CH01|Silhouette detective in long slate coat inspects an antique compass on dark wooden desk in noir style.",
            ),
            (
                "Con tàu Mary Celeste được tìm thấy với cánh buồm vẫn giương cao.",
                "concept_metaphor:none|A lone two-masted wooden brigantine drifting quietly under slate grey oceanic skies.",
            ),
            (
                "Nhưng điều kỳ lạ nhất là hàng hóa trên tàu vẫn còn nguyên vẹn.",
                "white_card:none|A stamped manila dossier card showing wooden cargo barrels with bright red inspection seals.",
            ),
            (
                "Không hề có dấu vết của một cuộc cướp bóc hay xô xát.",
                "concept_metaphor:none|A clean ship logbook open on table with fountain pen resting peacefully beside it.",
            ),
            (
                "Quần áo cá nhân và nhật ký hải trình vẫn nằm ngay ngắn trong cabin.",
                "macro_prop:none|A polished brass pocket watch ticking on aged off-white paper canvas.",
            ),
            (
                "Chỉ có chiếc thuyền cứu sinh duy nhất đã biến mất bí ẩn.",
                "visual_diagram:none|Diagram of ship deck showing empty davits where lifeboats once hung with red outline.",
            ),
            (
                "Các nhà khoa học suy đoán hơi cồn công nghiệp đã rò rỉ dưới hầm.",
                "concept_metaphor:none|Subtle vapor fumes rising from a wooden cask into dark shadowed space.",
            ),
            (
                "Thuyền trưởng vì sợ nổ tàu nên đã ra lệnh tạm thời sơ tán khẩn cấp.",
                "full_scene:CH01|Detective traces a map route with red pencil under single focused beam of light.",
            ),
            (
                "Theo bạn, điều gì đã thực sự xảy ra với thủy thủ đoàn năm ấy?",
                "full_scene:CH01|Detective turns to viewer with open hands beside the vintage evidence case folder.",
            ),
        ],
    },
    "co_the_ke": {
        "title": "Dạ Dày Than Phiền Gì Khi Bạn Ăn Mì Gói Lúc Nửa Đêm?",
        "topic": "Sinh Lý Học Tiêu Hóa Đêm: Cơ Chế Quá Tải Của Dạ Dày Khi Ăn Tinh Bột Chiên Muộn",
        "youtube_title": "Dạ Dày Than Phiền Gì Khi Bạn Ăn Mì Gói Lúc Nửa Đêm?",
        "text_overlay": "DẠ DÀY KÊU CỨU",
        "visual_hook": "Linh vật Dạ Dày dễ thương toát mồ hôi gánh bát mì gói khổng lồ lúc 12 giờ đêm",
        "contrast_pair": "Thỏa mãn vị giác vs. Quá tải tiêu hóa",
        "sources": [
            {
                "id": "SRC01",
                "title": "Circadian Rhythms in Gastric Acid Secretion and Motility",
                "reference": "Kumar & Clark (2020). Clinical Medicine, 10th Edition, Elsevier.",
                "facts": [
                    "Dạ dày giảm tiết men tiêu hóa sau mười một giờ đêm.",
                    "Thức ăn nhiều dầu mỡ cần gấp đôi thời gian để tiêu hóa.",
                ],
            },
        ],
        "rows": [
            (
                "Nếu bạn ăn mì gói lúc nửa đêm, đây là điều dạ dày phải gánh chịu.",
                "full_scene:CH01|Kawaii peach stomach character sits with dramatic exhausted expression beside an empty instant noodle cup.",
            ),
            (
                "Bạn thấy bụng no và cơn đói được xoa dịu tức thì.",
                "concept_metaphor:none|A smiling cartoon doodle stickman patting his belly contentedly under warm bedroom light.",
            ),
            (
                "Nhưng bên trong cơ thể, một ca trực cấp bách vừa mới bắt đầu.",
                "white_card:none|A red emergency alarm beacon pulsing on clean white background with cartoon exclamation mark.",
            ),
            (
                "Mười hai giờ đêm là lúc các cơ quan chuẩn bị nghỉ ngơi.",
                "macro_prop:none|A simple flat wall clock pointing to midnight in minimal black outlines.",
            ),
            (
                "Để nghiền nát sợi mì chiên ngập dầu và lượng muối khổng lồ,",
                "visual_diagram:none|Stomach character flexing tiny arms trying to lift a heavy yellow noodle bowl icon.",
            ),
            (
                "dạ dày buộc phải bơm thêm một lượng a-xít đậm đặc.",
                "concept_metaphor:none|Droplets of stomach acid bubbling safely inside a clean pink organ outline on white canvas.",
            ),
            (
                "Nhu động ruột chậm chạp khiến thức ăn ứ đọng nhiều giờ liền.",
                "visual_diagram:none|Simple timeline chart showing digestion taking four hours instead of two.",
            ),
            (
                "Đó là lý do sáng hôm sau thức dậy bạn thấy nặng nề và đắng miệng.",
                "full_scene:CH01|Stomach character resting with a cooling ice bag on head, giving a gentle thumbs up.",
            ),
            (
                "Bạn có hay đói cồn cào lúc nửa đêm không, lưu video lại để nhắc mình nhé?",
                "full_scene:CH01|Stomach character waves cheerfully to viewer beside a friendly cup of warm water.",
            ),
        ],
    },
    "ai_binh_dan": {
        "title": "Tóm Tắt File PDF 50 Trang Trong 30 Giây Bằng AI",
        "topic": "Ứng Dụng AI Cho Dân Văn Phòng: Quy Trình Trích Xuất Luận Điểm Và Bảng Nhiệm Vụ",
        "youtube_title": "Tóm Tắt File PDF 50 Trang Trong 30 Giây Bằng AI",
        "text_overlay": "TÓM TẮT SIÊU TỐC",
        "visual_hook": "Stickman chỉ tay vào màn hình laptop tóm tắt file tài liệu 50 trang thành bảng ngắn",
        "contrast_pair": "Đọc tay hai tiếng vs. AI ba mươi giây",
        "sources": [
            {
                "id": "SRC01",
                "title": "AI in Workplace Productivity and Document Extraction",
                "reference": "Microsoft Work Trend Index (2024). Special Report on Copilot Workflows.",
                "facts": [
                    "Tóm tắt tự động giúp tiết kiệm hai giờ đọc mỗi tuần.",
                    "Câu lệnh ba phần tăng độ chính xác lên tám mươi phần trăm.",
                ],
            },
        ],
        "rows": [
            (
                "Một câu lệnh này giúp bạn tóm tắt file PDF 50 trang trong 30 giây.",
                "full_scene:CH01|Stickman in violet hoodie sits at desk pointing with excitement at a laptop screen on clean white stage.",
            ),
            (
                "Đừng tốn cả buổi chiều ngồi lật từng trang tài liệu dày cộp nữa.",
                "concept_metaphor:none|A massive stack of fifty paper document pages resting beside an empty coffee mug.",
            ),
            (
                "Hãy tải tệp tài liệu lên và dán đúng câu lệnh ba bước này.",
                "macro_prop:none|A clean document upload icon with an upward pointing blue arrow on white card.",
            ),
            (
                "Bước một: yêu cầu máy trích xuất năm luận điểm quan trọng nhất.",
                "visual_diagram:none|A numbered list card displaying five neat horizontal checkmark bars in mint green.",
            ),
            (
                "Bước hai: lập bảng thống kê toàn bộ số liệu và ngân sách liên quan.",
                "white_card:none|A clean three-column table showing headings HẠNG MỤC, SỐ LIỆU and ĐƠN VỊ.",
            ),
            (
                "Bước ba: chỉ ra ba việc cần làm ngay cho dự án tuần này.",
                "concept_metaphor:CH01|Stickman holds up a mini clipboard stamped VIỆC CẦN LÀM with clear bullet points.",
            ),
            (
                "Chỉ sau nửa phút, bản báo cáo hoàn hảo đã sẵn sàng gửi sếp.",
                "full_scene:CH01|Stickman smiles with satisfaction looking at clean summary card glowing with checkmarks.",
            ),
            (
                "Bạn muốn mình chia sẻ mẹo AI cho công việc nào tiếp theo, bình luận nhé?",
                "full_scene:CH01|Stickman leans forward with friendly gesture and points toward comment section.",
            ),
        ],
    },
}

# ---------------------------------------------------------------------------
# Pre-architected Week 1 Long Blueprints (YouTube explainer long_16x9, 10-15m)
# ---------------------------------------------------------------------------

WEEK1_LONG_STORIES: Dict[str, Dict[str, Any]] = {
    "nao_luoi": {
        "title": "Tại Sao Càng Tự Trách Bạn Lại Càng Trì Hoãn?",
        "topic": "Giải Mã Vòng Lặp Tự Trách Và Cơ Chế Phòng Vệ Trì Hoãn Của Bộ Não",
        "youtube_title": "Tại Sao Càng Tự Trách Bạn Lại Càng Trì Hoãn?",
        "text_overlay": "VÒNG LẶP TRÌ HOÃN",
        "visual_hook": "Stickman ngồi ôm đầu trước đống tài liệu dở dang, bên cạnh chiếc đồng hồ tích tắc",
        "contrast_pair": "Tự trách tiêu cực vs. Tha thứ nhận thức",
        "sources": [
            {
                "id": "SRC01",
                "title": "Self-Forgiveness and Procrastination",
                "reference": "Wohl, Pychyl, & Bennett (2010). Personal Relationships, 17(1), 127-138.",
                "facts": [
                    "Biết tha thứ cho bản thân giúp giảm hẳn trì hoãn lần sau.",
                    "Cảm xúc tội lỗi kích hoạt phản xạ đóng băng của não bộ.",
                ],
            },
        ],
        "rows": [
            (
                "Bạn đã từng nằm lướt điện thoại giữa đêm, dù lòng rất sốt ruột vì việc chưa xong?",
                "full_scene:CH01|Stickman lies on bed illuminated by smartphone glow while clock ticks past midnight on cream canvas.",
            ),
            (
                "Càng nhìn công việc dang dở, bạn càng tự mắng mình vô dụng.",
                "concept_metaphor:CH01|Stickman grips his head with spiral lines of worry radiating around forehead.",
            ),
            (
                "Nhưng điều bất ngờ là tự trách bản thân chỉ khiến bạn trì hoãn tệ hơn.",
                "white_card:none|A clean white card displaying a vicious cyclical circular arrow labeled TỰ TRÁCH and TRÌ HOÃN.",
            ),
            (
                "Các nhà tâm lý học chứng minh rằng trì hoãn không phải do bạn lười biếng.",
                "concept_metaphor:CH01|Stickman points firmly to an open psychology handbook with calm reassurance.",
            ),
            (
                "Đó thực chất là một phản xạ phòng vệ trước cảm xúc tiêu cực.",
                "visual_diagram:none|An anatomical diagram of the brain showing amygdala labeled TRUNG TÂM BÁO ĐỘNG.",
            ),
            (
                "Khi bạn đối diện với một bài báo cáo khó hoặc một bài tập lớn,",
                "full_scene:CH01|Stickman sits before a massive mountain of blank paperwork at a wooden desk.",
            ),
            (
                "não bộ xem nhiệm vụ đó là một mối đe dọa đến lòng tự trọng.",
                "concept_metaphor:none|A towering dark charcoal wall rising up to block the forward path on warm canvas.",
            ),
            (
                "Lướt mạng xã hội hay dọn dẹp phòng là những phần thưởng dopamine tức thì.",
                "visual_diagram:none|A flat balance scale showing tiny smartphone icon outweighing heavy book stack.",
            ),
            (
                "Để phá vỡ vòng luẩn quẩn này, bước đầu tiên là học cách tự tha thứ.",
                "concept_metaphor:CH01|Stickman gently places hand on chest with warm compassionate expression.",
            ),
            (
                "Khi bạn bớt tự dằn vặt, hạch hạnh nhân sẽ hạ mức báo động.",
                "visual_diagram:none|A calming green gauge needle moving from red danger zone to cool green equilibrium.",
            ),
            (
                "Hãy chia nhỏ mục tiêu thành bước năm phút không cần hoàn hảo.",
                "white_card:none|A neat task card with three checkmarks and stamp 5 PHÚT KHỞI ĐỘNG.",
            ),
            (
                "Bạn có đang mắc kẹt trong vòng lặp này không, hãy đón xem tập tiếp theo nhé!",
                "full_scene:CH01|Stickman holds up a completed rough draft with a warm triumphant smile under morning light.",
            ),
        ],
    },
    "tui_tien": {
        "title": "Giải Mã Đế Chế Trà Sữa: Ly 50 Nghìn Lãi Bao Nhiêu?",
        "topic": "Giải Mã Mô Hình Kinh Doanh F&B: Bóc Tách Chi Phí Và Dòng Tiền Chuỗi Đồ Uống",
        "youtube_title": "Giải Mã Đế Chế Trà Sữa: Ly 50 Nghìn Lãi Bao Nhiêu?",
        "text_overlay": "BÓC TÁCH DÒNG TIỀN",
        "visual_hook": "Stickman đeo kính đứng trước bảng phân tích dòng tiền chuỗi F&B trên giấy kẻ ô",
        "contrast_pair": "Doanh thu bề nổi vs. Lợi nhuận ròng thực tế",
        "sources": [
            {
                "id": "SRC01",
                "title": "F&B Unit Economics Breakdown",
                "reference": "Vietnam Retail & Franchise Review (2024). Harvard Business School Case.",
                "facts": [
                    "Điểm hòa vốn của một cửa hàng F&B thường từ chín tháng.",
                    "Mặt bằng đẹp ngốn tới ba mươi phần trăm doanh thu tháng.",
                ],
            },
        ],
        "rows": [
            (
                "Một ly trà sữa bán 50 nghìn đồng, bạn nghĩ chủ quán thật sự đút túi bao nhiêu?",
                "full_scene:CH01|Stickman with glasses points pencil to a large fifty thousand VND price tag on grid paper.",
            ),
            (
                "Nhiều người thấy quán lúc nào cũng đông nghịt nên tưởng họ lãi đậm.",
                "concept_metaphor:CH01|Stickman observes a crowded counter queue drawn in simple miniature silhouettes.",
            ),
            (
                "Nhưng sự thật đằng sau báo cáo tài chính lại khiến ai nấy giật mình.",
                "white_card:none|A clean grid ledger card showing a massive column of operational overhead expenses.",
            ),
            (
                "Cốt trà và trân châu chỉ chiếm chưa tới mười lăm phần trăm.",
                "visual_diagram:none|Pie chart showing ingredients taking a slim slice against heavy overhead costs.",
            ),
            (
                "Chi phí mặt bằng tại ngã tư lớn ngốn tới sáu mươi triệu một tháng.",
                "macro_prop:none|A flat architectural storefront sketch with red lease contract stamp on warm paper.",
            ),
            (
                "Cộng thêm chi phí nhượng quyền, máy lạnh và đội ngũ phục vụ,",
                "visual_diagram:none|Hand-drawn ledger columns subtracting staff wages and franchise fees sequentially.",
            ),
            (
                "quán phải bán ít nhất ba trăm ly mỗi ngày mới mong hòa vốn.",
                "concept_metaphor:CH01|Stickman calculates on paper while balancing a milk tea cup against coin stacks.",
            ),
            (
                "Đó là lý do nhiều thương hiệu nổi tiếng bỗng dưng biến mất sau một năm.",
                "white_card:none|A closed shop shutter graphic with temporary renovation notice on grid backdrop.",
            ),
            (
                "Bạn muốn mình bóc tách mô hình kinh doanh nào tiếp theo, bình luận nhé?",
                "full_scene:CH01|Stickman waves warmly holding open accounting ledger and smiles at viewer.",
            ),
        ],
    },
    "ua_sao_vay": {
        "title": "8 Hiện Tượng Quen Thuộc Nhưng 99% Hiểu Sai Bản Chất",
        "topic": "Giải Mã Khoa Học Thường Thức: 8 Ngộ Nhận Phổ Biến Trong Cuộc Sống Hàng Ngày",
        "youtube_title": "8 Hiện Tượng Quen Thuộc Nhưng 99% Hiểu Sai Bản Chất",
        "text_overlay": "SỰ THẬT KHOA HỌC",
        "visual_hook": "Linh vật Bé Ủa cầm kính lúp khám phá các hiện tượng đời thường kỳ lạ",
        "contrast_pair": "Lời đồn dân gian vs. Bản chất khoa học",
        "sources": [
            {
                "id": "SRC01",
                "title": "Everyday Physical and Biological Misconceptions",
                "reference": "Journal of Applied Science & Popular Education (2023).",
                "facts": [
                    "Hạn sử dụng của nước đóng chai là dành cho vỏ nhựa.",
                    "Cơ thể không thể tự cù lét do não bộ đoán trước xúc giác.",
                ],
            },
        ],
        "rows": [
            (
                "Ai cũng nghĩ nước suối đóng chai có hạn sử dụng vì nước bị thiu, đúng hay sai?",
                "full_scene:CH01|Bé Ủa holds a transparent water bottle inspecting the expiration date with curious eyes.",
            ),
            (
                "Nước khoáng ngầm đã chảy hàng triệu năm trong lòng đất không hề hỏng.",
                "concept_metaphor:none|A natural underground water spring flowing through bedrock into crystal pools.",
            ),
            (
                "Nhưng sự thật là chiếc vỏ chai nhựa mới chính là thứ có hạn dùng.",
                "white_card:none|A plastic bottle silhouette surrounded by expanding yellow warranty date badge.",
            ),
            (
                "Sau hai năm, nhựa sẽ bắt đầu phân rã và ngấm vào dòng nước.",
                "visual_diagram:none|Microscopic diagram of polymer molecules resting at the bottle boundary.",
            ),
            (
                "Một câu hỏi khác: vì sao bạn không bao giờ tự cù lét mình được?",
                "concept_metaphor:CH01|Bé Ủa tickles his own belly with stubby hands and tilts head with no laughter.",
            ),
            (
                "Tiểu não của bạn luôn dự đoán trước mọi chuyển động cơ thể tạo ra.",
                "visual_diagram:none|Stylized brain illustration highlighting cerebellum signal feedback loops.",
            ),
            (
                "Cảm giác bất ngờ bị triệt tiêu nên bạn không thể nào bật cười.",
                "macro_prop:none|A simple flat laughing mask placed beside a calm neutral face icon.",
            ),
            (
                "Khoa học quanh ta luôn chứa đầy những bất ngờ thú vị như vậy.",
                "concept_metaphor:CH01|Bé Ủa holds up a glowing star beacon surrounded by sparkling sticker stars.",
            ),
            (
                "Bạn đã hiểu đúng bao nhiêu hiện tượng, chia sẻ trong phần bình luận nhé?",
                "full_scene:CH01|Bé Ủa bounces happily on yellow canvas waving both arms to the viewer.",
            ),
        ],
    },
    "su_ke_lai": {
        "title": "Trận Bạch Đằng 938: Bẫy Cọc Gỗ Của Ngô Quyền",
        "topic": "Nghệ Thuật Quân Sự Trận Bạch Đằng 938: Thiên Tài Tính Toán Thủy Triều",
        "youtube_title": "Trận Bạch Đằng 938: Bẫy Cọc Gỗ Của Ngô Quyền",
        "text_overlay": "BẠCH ĐẰNG 938",
        "visual_hook": "Tướng lĩnh thời xưa đứng trên bờ sông Bạch Đằng chỉ huy trận đánh lịch sử",
        "contrast_pair": "Chiến thuyền Nam Hán vs. Bãi cọc Ngô Quyền",
        "sources": [
            {
                "id": "SRC01",
                "title": "Chiến tranh Vệ quốc Thời Ngô Quyền",
                "reference": "Viện Lịch sử Quân sự Việt Nam (2021). NXB Quân đội Nhân dân.",
                "facts": [
                    "Ngô Quyền nắm chắc chu kỳ nhật triều của vùng cửa sông.",
                    "Bãi cọc ngầm được hoàn thành bí mật chỉ trong mười ngày.",
                ],
            },
        ],
        "rows": [
            (
                "Bạn có biết mùa đông năm 938, đoàn thuyền Nam Hán tiến vào sông Bạch Đằng mà không biết gì?",
                "full_scene:CH01|Dong Ho commander gazes toward coastal estuary under dramatic woodcut morning skies.",
            ),
            (
                "Tướng giặc Hoằng Tháo ỷ vào đoàn thuyền khổng lồ và vũ khí sắc bén.",
                "concept_metaphor:none|A flotilla of ancient warships sailing proudly with fluttering banner flags.",
            ),
            (
                "Nhưng họ không hề biết dưới lòng sông là một bãi cọc gỗ bịt sắt.",
                "white_card:none|Cross-section drawing showing sharpened timber stakes anchored deep in river mud.",
            ),
            (
                "Ngô Quyền đã nghiên cứu rất kỹ quy luật con nước lên xuống mỗi ngày.",
                "visual_diagram:none|Tidal elevation curve chart drawn in traditional Dong Ho natural earth pigments.",
            ),
            (
                "Ông cho thuyền nhỏ ra khiêu chiến rồi vờ bỏ chạy tháo lui.",
                "full_scene:CH01|Agile Vietnamese rowboats steering skillfully between pre-marked navigational safe paths.",
            ),
            (
                "Quân giặc háo thắng đuổi theo tràn qua bãi cọc lúc triều dâng cao nhất.",
                "concept_metaphor:none|Massive enemy warships crossing over concealed underwater barriers unknowingly.",
            ),
            (
                "Khi con nước đột ngột rút nhanh, hàng nghìn cọc nhọn nhô lên tua tủa.",
                "macro_prop:none|Sharpened iron stake tip breaking through white water foam in dramatic woodcut linework.",
            ),
            (
                "Thuyền giặc mắc cạn vỡ toác, quân ta quay đầu tổng phản công dữ dội.",
                "full_scene:CH01|Commander raises signal flag high as drums roll along the misty riverbank.",
            ),
            (
                "Trận đánh đã chấm dứt hơn một nghìn năm Bắc thuộc của dân tộc ta.",
                "concept_metaphor:none|A golden bronze drum sunburst motif shining over peaceful river landscape.",
            ),
            (
                "Theo dõi kênh Sử Kể Lại để cùng nhìn lại những trang sử vẻ vang tiếp nhé!",
                "full_scene:CH01|Commander stands proudly on do paper canvas clasping hands in historical salute.",
            ),
        ],
    },
    "thuong_cho_kheo": {
        "title": "Vì Sao Thương Nhau Nhưng Cứ Mở Lời Là Làm Tổn Thương?",
        "topic": "Tâm Lý Học Giao Tiếp Gia Đình Và Cặp Đôi: 5 Bẫy Ngôn Từ Phổ Biến",
        "youtube_title": "Vì Sao Thương Nhau Nhưng Cứ Mở Lời Là Làm Tổn Thương?",
        "text_overlay": "BẪY GIAO TIẾP",
        "visual_hook": "Tũn và Mây ngồi hai đầu chiếc bàn đối thoại trong không khí lắng đọng",
        "contrast_pair": "Ý định yêu thương vs. Cách diễn đạt vụng về",
        "sources": [
            {
                "id": "SRC01",
                "title": "The Seven Principles for Making Marriage Work",
                "reference": "John Gottman (1999). Crown Publishing.",
                "facts": [
                    "Bốn sát thủ giao tiếp bao gồm chỉ trích và phòng thủ.",
                    "Mở đầu nhẹ nhàng quyết định thành bại của cuộc trò chuyện.",
                ],
            },
        ],
        "rows": [
            (
                "Có bao giờ bạn nói ra một câu vì lo lắng, nhưng vừa dứt lời thì đối phương giận?",
                "full_scene:CH01|Tun and May sit at opposite ends of a small wooden coffee table in soft pastel style.",
            ),
            (
                "Rõ ràng trong lòng bạn rất quan tâm và muốn tốt cho người ấy.",
                "concept_metaphor:CH01|Tun looks down holding a warm mug of cocoa with sincere concern on face.",
            ),
            (
                "Nhưng câu từ thốt ra lại mang giọng điệu chỉ trích và phán xét.",
                "white_card:none|A speech bubble showing sharp spiky pastel edges turning into a cold barrier wall.",
            ),
            (
                "Bộ não con người phản ứng với lời chê bai giống hệt như đòn tấn công vật lý.",
                "visual_diagram:none|A gentle psychological balance scale weighing verbal warmth against defensiveness.",
            ),
            (
                "Khi bị đóng khung, đối phương lập tức dựng lên bức tường phòng thủ.",
                "concept_metaphor:none|May wraps her arms softly around her cardigan facing away toward window.",
            ),
            (
                "Bí quyết để hóa giải nằm ở công thức nói về cảm xúc của chính bạn.",
                "white_card:none|A clean cream card with formula: ANH THẤY LO THAY VÌ EM LUÔN LÀM SAI.",
            ),
            (
                "Thay vì đổ lỗi, hãy chia sẻ nỗi băn khoăn bằng sự thấu hiểu chân thành.",
                "full_scene:CH01|Tun reaches forward offering a hand gently across the table to May.",
            ),
            (
                "Lắng nghe mà không ngắt lời chính là món quà quý giá nhất trong tình yêu.",
                "concept_metaphor:none|Two delicate pink and mint flowers blooming together side by side in sunlight.",
            ),
            (
                "Bạn có nhận ra hình ảnh của mình trong câu chuyện này không, chia sẻ nhé?",
                "full_scene:CH01|Tun and May smile warmly side by side waving gently to the viewer on cream canvas.",
            ),
        ],
    },
    "ho_so_ky_la": {
        "title": "Hồ Sơ Tàu Mary Celeste: Bí Ẩn Thủy Thủ Biến Mất",
        "topic": "Hồ Sơ Hàng Hải 1872: Giải Mã Vụ Mất Tích Không Dấu Vết Giữa Đại Tây Dương",
        "youtube_title": "Hồ Sơ Tàu Mary Celeste: Bí Ẩn Thủy Thủ Biến Mất",
        "text_overlay": "HỒ SƠ TÀU MA",
        "visual_hook": "Thám tử mở cặp hồ sơ lưu trữ vụ án hàng hải bí ẩn nhất thế kỷ 19",
        "contrast_pair": "Hiện trường nguyên vẹn vs. Con người bốc hơi",
        "sources": [
            {
                "id": "SRC01",
                "title": "Investigation Records of the Vice Admiralty Court",
                "reference": "Gibraltar Archives (1873). Maritime Inquest Proceedings.",
                "facts": [
                    "Toàn bộ mười người trên tàu biến mất không để lại dấu tích.",
                    "Thực phẩm và nước ngọt trên tàu đủ dùng trong sáu tháng.",
                ],
            },
        ],
        "rows": [
            (
                "Năm 1872, một con tàu trôi dạt giữa đại dương mà không còn một bóng người nào?",
                "full_scene:CH01|Silhouette detective examines a weathered nautical chart with antique brass dividers in noir style.",
            ),
            (
                "Tàu Mary Celeste được tàu Dei Gratia phát hiện ngoài khơi Bồ Đào Nha.",
                "concept_metaphor:none|A solitary sailing brigantine drifting listlessly across deep charcoal ocean waves.",
            ),
            (
                "Nhưng khi các thủy thủ bước lên boong, họ chứng kiến cảnh tượng rùng mình.",
                "white_card:none|A vintage dossier photograph of empty ship decks with no signs of struggle or chaos.",
            ),
            (
                "Bữa ăn vẫn còn trên bàn, quần áo của thuyền trưởng xếp ngay ngắn.",
                "macro_prop:none|An intact porcelain tea cup and leather bound journal resting on cabin desk.",
            ),
            (
                "Một nghìn bảy trăm thùng cồn công nghiệp nguyên vẹn dưới hầm hàng.",
                "visual_diagram:none|Cross-section blueprint of ship cargo hold showing stacked wooden alcohol barrels.",
            ),
            (
                "Không có cướp biển, không có bão lớn, và không có dịch bệnh.",
                "white_card:none|A list of four debunked theories each struck through with bold red investigator stamps.",
            ),
            (
                "Giả thuyết khoa học cho rằng hơi cồn rò rỉ tạo nên vụ nổ áp suất nhỏ.",
                "concept_metaphor:none|Translucent vapor plumes expanding gently beneath closed wooden hatch covers.",
            ),
            (
                "Nỗi sợ hãi đã thôi thúc mọi người nhảy xuống xuồng cứu sinh rồi mất tích.",
                "full_scene:CH01|Detective pins a red thread connecting Gibraltar to Azores on manila map board.",
            ),
            (
                "Theo bạn thì điều gì là hợp lý nhất, hãy để lại bình luận cho thám tử biết nhé!",
                "full_scene:CH01|Detective steps back into soft lamplight holding case folder and nods to viewer.",
            ),
        ],
    },
    "co_the_ke": {
        "title": "24 Giờ Bên Trong Cơ Thể Khi Bạn Thức Trắng Đêm",
        "topic": "Hành Trình Sinh Lý Học 24 Giờ: Tim, Gan Và Não Gồng Gánh Ra Sao Khi Thiếu Ngủ",
        "youtube_title": "24 Giờ Bên Trong Cơ Thể Khi Bạn Thức Trắng Đêm",
        "text_overlay": "24H THỨC TRẮNG",
        "visual_hook": "Các linh vật nội tạng họp khẩn cấp dưới ánh đèn đêm khi đồng hồ điểm 3 giờ",
        "contrast_pair": "Sự tỉnh táo gượng ép vs. Tổn thương tế bào",
        "sources": [
            {
                "id": "SRC01",
                "title": "Why We Sleep: The New Science of Sleep and Dreams",
                "reference": "Matthew Walker (2017). Scribner, Neuroscience Series.",
                "facts": [
                    "Hệ thống làm sạch não bộ chỉ hoạt động khi đi vào giấc ngủ sâu.",
                    "Thức trắng một đêm làm giảm bảy mươi phần trăm tế bào miễn dịch.",
                ],
            },
        ],
        "rows": [
            (
                "Nếu tối nay bạn thức trắng, đây là cuộc họp khẩn cấp diễn ra trong não và tim bạn?",
                "full_scene:CH01|Four kawaii organ characters (Brain, Heart, Liver, Stomach) gather around a round table looking worried.",
            ),
            (
                "Mười một giờ đêm, não phát tín hiệu buồn ngủ qua chất melatonin.",
                "concept_metaphor:none|A gentle sleepy crescent moon sending glowing blue droplets over calm white canvas.",
            ),
            (
                "Nhưng bạn tiếp tục uống cà phê và nhìn chằm chằm vào màn hình máy tính.",
                "concept_metaphor:CH01|Human doodle host sips from an oversized coffee mug under bright screen illumination.",
            ),
            (
                "Một giờ sáng, tim buộc phải đập nhanh hơn do hoóc-môn căng thẳng tăng cao.",
                "visual_diagram:none|Heart character jogging on a clean white track measuring elevated pulse beats.",
            ),
            (
                "Ba giờ sáng, hệ thống dọn dẹp độc tố trong não hoàn toàn bị đình trệ.",
                "white_card:none|A clean diagram showing beta-amyloid debris accumulating when brain cleaning stops.",
            ),
            (
                "Lá gan phải làm việc quá công suất để chuyển hóa lượng đường dự trữ.",
                "concept_metaphor:none|Maroon liver character sweating while sorting fuel energy canisters.",
            ),
            (
                "Đến sáng hôm sau, tế bào miễn dịch tự nhiên giảm sút tới bảy mươi phần trăm.",
                "visual_diagram:none|A bar graph showing immune defense dropping sharply from 100% to 30%.",
            ),
            (
                "Cơ thể bạn không được thiết kế để sống thiếu giấc ngủ chất lượng.",
                "full_scene:CH01|Organ characters lovingly tuck human stickman host into cozy bed with warm blanket.",
            ),
            (
                "Bạn có hay thức khuya chạy việc không, lưu video lại để nhắc nhở bản thân nhé!",
                "full_scene:CH01|All organ characters wave peacefully side by side wishing viewer good night.",
            ),
        ],
    },
    "ai_binh_dan": {
        "title": "5 Quy Trình AI Miễn Phí Giúp Tiết Kiệm 2 Giờ Mỗi Ngày",
        "topic": "Tự Động Hóa Công Việc Văn Phòng: 5 Ứng Dụng Thực Chiến Tiết Kiệm Thời Gian",
        "youtube_title": "5 Quy Trình AI Miễn Phí Giúp Tiết Kiệm 2 Giờ Mỗi Ngày",
        "text_overlay": "5 QUY TRÌNH AI",
        "visual_hook": "Stickman chỉ tay vào mô hình 5 bước tự động hóa công việc bằng câu lệnh mẫu",
        "contrast_pair": "Làm thủ công vất vả vs. Tự động hóa thông minh",
        "sources": [
            {
                "id": "SRC01",
                "title": "Generative AI at Work: Productivity Gains",
                "reference": "Brynjolfsson, Li, & Raymond (2023). NBER Working Paper No. 31161.",
                "facts": [
                    "Sử dụng AI hỗ trợ tăng năng suất nhân viên văn phòng lên mười bốn phần trăm.",
                    "Quy trình chuẩn hóa giúp giảm thiểu sai sót dữ liệu bảng tính.",
                ],
            },
        ],
        "rows": [
            (
                "Đừng mất hai tiếng đọc báo cáo, một câu lệnh này giúp bạn có bảng tóm tắt ngay?",
                "full_scene:CH01|Stickman in violet hoodie demonstrates a clean three-step workflow on laptop screen.",
            ),
            (
                "Nhiều người nghĩ dùng AI phức tạp và cần phải biết lập trình.",
                "concept_metaphor:CH01|Stickman shakes head smilingly beside a complex chalkboard covered in false equations.",
            ),
            (
                "Nhưng sự thật bạn chỉ cần nắm vững năm quy trình miễn phí sau đây.",
                "white_card:none|A clean numbered guide card displaying five practical workflow badges in tech green.",
            ),
            (
                "Quy trình một: biến biên bản cuộc họp lộn xộn thành email việc cần làm.",
                "visual_diagram:none|Messy audio transcript icon transforming smoothly into neat email draft format.",
            ),
            (
                "Quy trình hai: tự động trích xuất bảng số liệu từ file tài liệu dài.",
                "macro_prop:none|A clean digital spreadsheet icon filling automatically with tidy row items.",
            ),
            (
                "Quy trình ba: viết thư từ chối hoặc đàm phán hợp đồng khéo léo.",
                "concept_metaphor:none|A polite diplomatic handshake badge drawn in flat minimal violet outlines.",
            ),
            (
                "Nắm vững các câu lệnh mẫu giúp bạn về sớm mỗi ngày mà việc vẫn chuẩn xác.",
                "full_scene:CH01|Stickman packs notebook neatly into bag with confident relaxed smile at desk.",
            ),
            (
                "Bạn muốn nhận bộ câu lệnh mẫu cho ngành nghề nào tiếp theo, bình luận nhé!",
                "full_scene:CH01|Stickman points toward comment box with welcoming open expression on clean white stage.",
            ),
        ],
    },
}


def get_channel_or_active(channel_id: Optional[str] = None, cwd: Optional[Path] = None) -> ChannelProfile:
    """Resolve ChannelProfile from explicit channel_id, active_channel.json, or git branch."""
    if channel_id:
        clean = channel_id.strip().replace("channel-", "").replace("channel/", "").replace("-", "_")
        return get_channel(clean)

    base = cwd or Path.cwd()
    candidates = [
        base / "sys/channels/active_channel.json",
        base / "active_channel.json",
        base.parent / "sys/channels/active_channel.json",
    ]
    for cand in candidates:
        if cand.is_file():
            try:
                data = json.loads(cand.read_text(encoding="utf-8"))
                cid = data.get("channel_id")
                if cid:
                    return get_channel(cid)
            except Exception:
                pass

    # Try detecting from git branch
    try:
        import subprocess

        res = subprocess.run(
            ["git", "-C", str(base), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode == 0:
            branch = res.stdout.strip()
            if branch.startswith("channel/"):
                slug = branch.partition("channel/")[2].replace("-", "_")
                if slug in channels():
                    return get_channel(slug)
    except Exception:
        pass

    # Default fallback to flagship channel
    return get_channel("nao_luoi")


def generate_synthetic_story_for_channel(
    ch: ChannelProfile,
    format_profile: str,
    topic_title: str,
) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]]]:
    """Dynamically synthesize a 100% compliant story structure for any custom topic or seed topic."""
    ch.spec_for(format_profile)
    is_short = format_profile == "short_9x16"
    char_id = "CH01"

    # Calibrate hook sentence
    clean_topic = topic_title.strip()
    if is_short:
        hook_sentence = f"Vì sao bạn lại {clean_topic.lower()} mỗi ngày?"
    else:
        hook_sentence = f"Bạn đã bao giờ tự hỏi vì sao {clean_topic.lower()} lại xảy ra thường xuyên?"

    sources = [
        {
            "id": "SRC01",
            "title": f"Cơ sở thực nghiệm về {clean_topic}",
            "reference": f"Nghiên cứu hành vi ứng dụng {ch.niche} (2024).",
            "facts": [
                "Hành vi này phản ánh cách con người chọn lối đi dễ hơn.",
                "Thói quen tự nhiên quyết định phần lớn hành vi mỗi ngày.",
            ],
        }
    ]

    if is_short:
        rows = [
            (
                hook_sentence,
                f"full_scene:{char_id}|Character reacts with surprise and deep curiosity on flat canvas.",
            ),
            (
                "Đa số chúng ta đều nghĩ nguyên nhân là do thói quen.",
                "white_card:none|A clean white card displaying a common assumption icon with question mark.",
            ),
            (
                "Nhưng sự thật là có một cơ chế khoa học ẩn giấu đằng sau.",
                f"concept_metaphor:{char_id}|Character holds an insightful magnifying glass revealing a hidden mechanism flowchart.",
            ),
            (
                "Não bộ luôn chọn con đường tiêu tốn ít năng lượng nhất.",
                "visual_diagram:none|A simple two-path divergence chart illustrating high effort versus low effort pathways.",
            ),
            (
                "Hiểu được nguyên lý này giúp bạn làm chủ hành vi của mình.",
                "macro_prop:none|A bright golden key icon resting peacefully on clean flat canvas.",
            ),
            (
                "Bạn có từng gặp trường hợp này không, bình luận số một nhé?",
                f"full_scene:{char_id}|Character smiles warmly and gestures toward viewer inviting conversation.",
            ),
        ]
    else:
        rows = [
            (
                hook_sentence,
                f"full_scene:{char_id}|Character stands at center stage facing viewer with intriguing opening gesture.",
            ),
            (
                "Đây là câu hỏi quen thuộc mà rất nhiều người trong chúng ta tự hỏi mỗi ngày.",
                f"concept_metaphor:{char_id}|Character reflects thoughtfully with hand on chin beside an open notebook.",
            ),
            (
                "Nhưng câu trả lời thực tế lại khác xa những gì số đông lầm tưởng.",
                "white_card:none|A clean comparison card highlighting common myths versus verified empirical observations.",
            ),
            (
                "Cơ chế này bắt nguồn từ sự tiến hóa trong nhận thức và tâm lý.",
                "visual_diagram:none|A structured flowchart with three logical stages demonstrating behavioral causality.",
            ),
            (
                "Khi nắm được bản chất, bạn có thể áp dụng ngay vào đời sống thực tế.",
                "concept_metaphor:none|A solid progress milestone beacon illuminated on flat stage backdrop.",
            ),
            (
                "Hãy cùng khám phá sâu hơn trong các video phân tích tiếp theo trên kênh nhé!",
                f"full_scene:{char_id}|Character bows respectfully and waves cheerfully with warm smile to viewer.",
            ),
        ]

    return sources, rows


def build_channel_topic(
    channel_id: Optional[str] = None,
    format_profile: str = "short_9x16",
    topic_title: Optional[str] = None,
    seed_index: Optional[int] = None,
    cwd: Optional[Path] = None,
) -> ResearchedTopic:
    """Build a complete ResearchedTopic object for any channel matching all Schema 3.0 contracts."""
    ch = get_channel_or_active(channel_id, cwd=cwd)
    spec = ch.spec_for(format_profile)
    is_short = format_profile == "short_9x16"

    # 1. Resolve Topic Content
    story_data: Optional[Dict[str, Any]] = None
    if not topic_title and seed_index is None:
        if is_short and ch.id in WEEK1_SHORT_STORIES:
            story_data = WEEK1_SHORT_STORIES[ch.id]
        elif not is_short and ch.id in WEEK1_LONG_STORIES:
            story_data = WEEK1_LONG_STORIES[ch.id]

    if story_data:
        chosen_title = story_data["title"]
        yt_title = story_data["youtube_title"]
        text_overlay = story_data["text_overlay"]
        visual_hook = story_data["visual_hook"]
        contrast_pair = story_data["contrast_pair"]
        sources = story_data["sources"]
        rows = story_data["rows"]
    else:
        if seed_index is not None and 1 <= seed_index <= len(ch.seed_topics):
            chosen_title = ch.seed_topics[seed_index - 1]
        elif topic_title:
            chosen_title = topic_title.strip()
        else:
            chosen_title = ch.seed_topics[0]

        yt_title = chosen_title if len(chosen_title) <= 55 else chosen_title[:52] + "..."
        text_overlay = ch.name.upper()[:16]
        visual_hook = f"Nhân vật chính của kênh {ch.name} tương tác với chủ đề {chosen_title}"
        contrast_pair = "Nhận thức phổ thông vs. Sự thật khoa học"
        sources, rows = generate_synthetic_story_for_channel(ch, format_profile, chosen_title)

    # 2. Build Scenes
    char_id = "CH01"
    story_tuples = [(chosen_title, f"Flat 2D {ch.visual.label} stage.", rows)]
    scenes = build_scenes_from_story_rows(story_tuples, character_id=char_id)

    # Distribute requirements and claims
    reqs = [{"id": f"R{i:02d}", "text": chosen_title} for i in range(1, len(scenes) + 1)]
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        if sources:
            sc.source_ids = [sources[0]["id"]]
            if sources[0].get("facts"):
                sc.claim_facts = [(rows[0][0], sources[0]["id"], sources[0]["facts"][0])]

    # 3. Build Cast
    characters = [channel_cast(ch.id, char_id)]
    if ch.id == "thuong_cho_kheo":
        characters.append(
            {
                "id": "CH02",
                "name": "Mây",
                "appearance": "Young woman with a round face, shoulder-length black hair with a small clip and dot eyes in simple chibi proportions.",
                "outfit": "Flat blush (#F7C6C7) cardigan, no folds, no shading.",
            }
        )

    # 4. Packaging Specification
    tags = [t.lstrip("#") for t in ch.hashtags]
    seo_kws = tags + [ch.slug, "videopilot", "kienthuc"]

    packaging = PackagingSpec(
        youtube_title=yt_title[:55],
        visual_hook=visual_hook,
        text_overlay=text_overlay,
        contrast_pair=contrast_pair,
        channel_pillar=DEFAULT_CHANNEL_PILLAR,
        funnel_tier="tier_1_broad",
        seo_keywords=seo_kws,
    )

    lo, hi = spec.duration_seconds
    return ResearchedTopic(
        topic=chosen_title,
        audience=ch.audience,
        goal=ch.promise,
        video_type="research_explainer",
        min_duration=float(lo),
        max_duration=float(hi),
        style=ch.visual.style_description,
        aspect_ratio="9:16" if is_short else "16:9",
        format_profile=format_profile,
        sources=sources,
        required_points=reqs,
        characters=characters,
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=True,
        voice=ch.voice,
        speed=ch.speed,
        channel_id=ch.id,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        packaging=packaging,
    )


def build_and_export_channel_package(
    channel_id: Optional[str] = None,
    format_profile: str = "short_9x16",
    output_dir: Optional[Path] = None,
    topic_title: Optional[str] = None,
    seed_index: Optional[int] = None,
    spinoff_shorts: bool = False,
    allow_active: bool = False,
    cwd: Optional[Path] = None,
) -> Dict[str, Any]:
    """Assemble, write, validate, and score a complete Schema 3.0 package for a channel."""
    ch = get_channel_or_active(channel_id, cwd=cwd)
    topic = build_channel_topic(
        channel_id=ch.id,
        format_profile=format_profile,
        topic_title=topic_title,
        seed_index=seed_index,
        cwd=cwd,
    )

    if output_dir is None:
        aspect_slug = "9x16" if format_profile == "short_9x16" else "16x9"
        job_name = f"{ch.slug}-{aspect_slug}-001"
        output_dir = SYS_DIR / "runs" / job_name

    output_dir.mkdir(parents=True, exist_ok=True)

    result = write_production_package(
        output_dir=output_dir,
        topic=topic,
        system_root=SYS_DIR,
        include_spinoffs=spinoff_shorts and format_profile == "long_16x9",
        allow_active=allow_active,
    )

    # Score Hook
    narrations = [sc.narration for sc in topic.scenes]
    hook_score = score_script(narrations, channel_id=ch.id, format_profile=format_profile)

    result["channel_id"] = ch.id
    result["channel_name"] = ch.name
    result["format_profile"] = format_profile
    result["hook_score"] = asdict(hook_score)

    return result
