#!/usr/bin/env python3
"""Build the enriched, bilingual (Vietnamese-first) Master Competitor Benchmark Catalog."""

import json
import os
from pathlib import Path

BASE_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f")
SPECS_DIR = BASE_DIR / "style_proofs/specs"
REFS_DIR = BASE_DIR / "competitor_refs"
CATALOG_FILE = BASE_DIR / "style_proofs_benchmark_catalog.md"

CHANNEL_META_VI = {
    "en-first-principles": {
        "title_vi": "Nguyên Lý Gốc, Vật Lý & Nghịch Lý Khoa Học",
        "scene_vi": "Phá vỡ giới hạn: Bóc tách một nghịch lý vật lý tưởng như bất khả thi về chân lý nguyên bản; một con đường bứt phá dốc đứng vượt qua lực ma sát hấp dẫn.",
        "styles_vi": {
            "style_1": {
                "name_vi": "Bản Vẽ Kỹ Thuật Blueprint Prussian Blue (Ảnh Mẫu Của Bạn)",
                "aesthetic_vi": "Nền giấy vẽ xanh Prussian đậm (#0A3663) có vân thớ giấy sần; nét mực trắng tinh khiết (#FFFFFF) vẽ quỹ đạo hạt gia tốc và cung compa cyan (#38BDF8); một chiếc xe cổ điển màu vàng mù tạt (#E5A93C) leo dốc bứt phá ngược trọng lực. Tỷ lệ tương phản cực cao, bố cục toán học uy nghiêm.",
                "reason_vi": "Là chuẩn mực thẩm mỹ tối thượng mà bạn vừa gửi: vừa đậm tính học thuật, vừa có tính dẫn dắt thị giác mạnh mẽ, xóa tan hoàn toàn cảm giác sticker rẻ tiền.",
            },
            "style_2": {
                "name_vi": "Veritasium — Phòng Thí Nghiệm Plasma Điện Ảnh",
                "aesthetic_vi": "Không gian buồng gia tốc hạt ngầm trong bóng tối (chiaroscuro); chùm plasma xanh dương rực rỡ chiếu xuyên qua màn sương mù thể tích (volumetric mist); bóng lưng nhà vật lý thực nghiệm phản chiếu trên nền bê tông ướt.",
                "reason_vi": "Mang lại cảm giác kỳ vĩ, bí ẩn và tầm vóc của những thí nghiệm khoa học đột phá hàng đầu thế giới của Veritasium (16M subs).",
            },
            "style_3": {
                "name_vi": "PolyMatter — Tài Liệu Điều Tra & Tia Quét Laser Đỏ",
                "aesthetic_vi": "Mặt bàn đá slate xám than (#1E222A) với tài liệu phân tích phân lớp; mô hình thử nghiệm bị cắt ngang bởi tia quét laser đỏ neon (#FF1744) và các vòng tròn chuẩn độ quang học holographic.",
                "reason_vi": "Thẩm mỹ đồ họa báo chí điều tra hiện đại, sắc lạnh, biểu đạt tính chính xác và tư duy mổ xẻ vấn đề đa chiều.",
            },
            "style_4": {
                "name_vi": "Primer — Sa Bàn Mô Phỏng 3D Soft Clay & Gỗ Mịn",
                "aesthetic_vi": "Sa bàn diorama studio ấm áp; dốc trượt gỗ sồi mô phỏng thế năng và gia tốc; nhân vật Blue Blob tròn trịa dễ thương lái xe đồ chơi bằng vật liệu đất sét polymer mềm mịn dưới ánh sáng ambient dịu mắt.",
                "reason_vi": "Dễ tiếp cận, trực quan hóa các phương trình vật lý và toán học phức tạp thành câu chuyện sinh động, gần gũi như kênh Primer.",
            },
        },
    },
    "en-scale-and-bone": {
        "title_vi": "Động Vật Học, Giải Phẫu Tiến Hóa & Sinh Vật Tiền Sử",
        "scene_vi": "Sinh tồn khốc liệt: Một chú rồng Komodo sơ sinh dùng móng vuốt bám chặt vào thân cây cổ thụ phủ rêu, dồn lực leo lên cao để thoát khỏi kẻ săn mồi mặt đất.",
        "styles_vi": {
            "style_1": {
                "name_vi": "TierZoo — Giao Diện Game Nhập Vai Retro RPG HUD",
                "aesthetic_vi": "Mô hình 3D rồng Komodo con trong rừng rậm nhiệt đới; bảng chỉ số RPG HUD retro phát sáng neon (INT, PWR, DEF, MBL, HP) lơ lửng với dải phân hạng tier rực rỡ; ánh sáng neon hắt phản xạ ambient lên vảy ướt và vỏ cây.",
                "reason_vi": "Biến thế giới động vật thành một tựa game sinh tồn lôi cuốn, tạo sự hào hứng tột độ cho khán giả trẻ tuổi theo chuẩn TierZoo (3.4M subs).",
            },
            "style_2": {
                "name_vi": "PBS Eons — Nghệ Thuật Cổ Sinh Hoàng Hôn Điện Ảnh",
                "aesthetic_vi": "3D Paleo-Art góc máy ngước nhìn hùng vĩ; ánh nắng hoàng hôn ngược (golden-hour rim light) vàng rực viền quanh lớp vảy sừng sần sùi của bò sát cổ sinh; nền sương khói và bụi tro núi lửa bay lơ lửng.",
                "reason_vi": "Đậm chất phim tài liệu khoa học tự nhiên điện ảnh, tái hiện chân thực bầu không khí tiền sử nguyên sơ như PBS Eons (2.8M subs).",
            },
            "style_3": {
                "name_vi": "BBC Earth — Quay Macro Điện Ảnh Siêu Thực (8K Cinema)",
                "aesthetic_vi": "Ống kính macro cinema 100mm f/2.8 xóa phông bơ mượt; rõ từng mảng vảy sừng tí hon và móng vuốt cong đen tuyền găm vào vỏ lim ướt; ánh sáng ban mai xuyên tán lá lấp lánh hạt sương.",
                "reason_vi": "Đỉnh cao của nhiếp ảnh tự nhiên hoang dã, phô diễn vẻ đẹp cơ khí sinh học hoàn mỹ của tạo hóa theo chuẩn BBC Earth (14M subs).",
            },
            "style_4": {
                "name_vi": "Moth Light Media — Màu Bột Gouache & Mực Sepia Bảo Tàng",
                "aesthetic_vi": "Tranh bột màu gouache dày dặn kết hợp nét bút ngòi sắt sepia trên nền giấy vellum ngà cổ; tiêu bản cắt lớp giải phẫu xương sọ và cơ hàm vận động của loài bò sát với tông màu đất nung và khoáng chất.",
                "reason_vi": "Phong cách học giả bảo tàng lịch sử tự nhiên cổ điển, mang chiều sâu tri thức uyên bác và tính lưu trữ thời gian.",
            },
        },
    },
    "en-pocket-cosmos": {
        "title_vi": "Vật Lý Thiên Văn & Quy Mô Vũ Trụ",
        "scene_vi": "Bên bờ chân trời sự kiện: Ánh sáng từ các ngôi sao xa xăm bị uốn cong quanh một hố đen siêu khối lượng, phơi bày cơ học thiên thể và quy mô khổng lồ của vũ trụ.",
        "styles_vi": {
            "style_1": {
                "name_vi": "Melodysheep — Vũ Trụ Siêu Thực Phát Quang (Cosmic Hyper-Realism)",
                "aesthetic_vi": "Hố đen với đĩa bồi tụ phát quang rực rỡ vàng-trắng và cyan; bụi tinh vân tím than và xanh lơ sâu thẳm; chùm sáng bị bẻ cong thành vòng cầu photon khép kín hoàn mỹ trên nền chân không đen tuyền.",
                "reason_vi": "Tạo cảm giác choáng ngợp trước quy mô vĩ đại của không-thời gian, gợi mở trí tưởng tượng đỉnh cao chuẩn Melodysheep (3M subs).",
            },
            "style_2": {
                "name_vi": "Astrum — Nhiếp Ảnh Thiên Văn Chân Thực Trong Chân Không",
                "aesthetic_vi": "Nhiếp ảnh chân thực trong chân không không lọc; ánh sáng sao gay gắt đổ bóng đen đặc; bộ đồ phi hành gia chi tiết khoa học; quang sai Doppler quang phổ và quỹ đạo laser hấp dẫn uốn cong tự nhiên.",
                "reason_vi": "Tính khoa học hàn lâm chính xác, lạnh lùng và trung thực như những bức ảnh chụp từ kính viễn vọng không gian James Webb.",
            },
            "style_3": {
                "name_vi": "SEA — Vực Thẳm U Tối Tĩnh Lặng (Deep Space Void)",
                "aesthetic_vi": "Hơn 80% khung hình là bóng tối chân không tĩnh mịch tuyệt đối; một trạm thăm dò đơn độc phát ra viền sáng xanh lạnh mong manh, đối diện sự trống rỗng vô tận của vũ trụ.",
                "reason_vi": "Khơi gợi nỗi sợ hiện sinh và sự tò mò triết học trước sự cô đơn của loài người giữa đại dương ngân hà.",
            },
            "style_4": {
                "name_vi": "Blueprint Cơ Học Thiên Thể (Mẫu Prussian Blue Của Bạn)",
                "aesthetic_vi": "Bản vẽ kỹ thuật xanh Prussian (#0D2F54); nét phấn trắng tinh xảo phác họa cơ học thiên thể và quỹ đạo photon uốn lượn; 1 điểm nhấn vàng photon duy nhất; khoảng không thở thoáng đạt >75%.",
                "reason_vi": "Hình học hóa các định luật hấp dẫn của Einstein thành một sơ đồ kiến trúc tuyệt đẹp, lịch lãm và dễ hiểu.",
            },
        },
    },
    "en-deep-time-strata": {
        "title_vi": "Địa Chất Học & Lịch Sử Hình Thành Trái Đất",
        "scene_vi": "Trái Đất sơ khai: Các mảng kiến tạo va chạm xô lệch, dòng magma rực lửa tuôn trào qua đới đứt gãy để lộ hàng tỷ năm lịch sử địa tầng lắng đọng.",
        "styles_vi": {
            "style_1": {
                "name_vi": "History of the Earth — Mặt Cắt Địa Chất 3D Xuyên Thạch Quyển",
                "aesthetic_vi": "Mặt cắt địa chất 3D sâu vào lòng đất; buồng magma phát sáng đỏ rực (#FF4500); các tầng đá phiến/granite chân thực; ánh sáng ngầm volumetric kịch tính chiếu rọi các lớp trầm tích.",
                "reason_vi": "Trực quan hóa cấu trúc ẩn giấu dưới lòng đất với độ chi tiết điện ảnh hùng vĩ chuẩn History of the Earth (1.4M subs).",
            },
            "style_2": {
                "name_vi": "PBS Eons — Đại Hồng Hoang Tiền Sử Núi Lửa",
                "aesthetic_vi": "Phong cảnh Trái Đất nguyên thủy sơ khai u tối hùng vĩ; núi lửa phun trào cột khói bụi khổng lồ dưới bầu trời dông bão có sét núi lửa; ánh mặt trời cam máu xuyên qua sương mù lưu huỳnh.",
                "reason_vi": "Tái hiện thời khắc Trái Đất vừa hình thành đầy bạo liệt, mang đậm tính sử thi tự nhiên.",
            },
            "style_3": {
                "name_vi": "Blueprint Đứt Gãy Kiến Tạo (Mẫu Prussian Blue Của Bạn)",
                "aesthetic_vi": "Bản vẽ kỹ thuật Blueprint xanh Prussian (#0B192C) thanh thoát; nét compa trắng (#F8FAFC) và cyan (#38BDF8) mô tả sơ đồ khối kiến tạo mảng, đới đứt gãy, vòng lan truyền sóng địa chấn và dòng đối lưu manti.",
                "reason_vi": "Chuyển hóa các hiện tượng địa chất phức tạp thành bản vẽ kỹ thuật kiến trúc tinh tế, sáng sủa và chuẩn mực học thuật.",
            },
            "style_4": {
                "name_vi": "Stefan Milo — Tranh Thạch Bản Địa Tầng Bảo Tàng Thế Kỷ 19",
                "aesthetic_vi": "Tranh in thạch bản và màu nước địa tầng cổ điển trên giấy vellum ngà (#F7F2E7); nét bút chấm mực sepia tỉ mỉ các lớp trầm tích đá vôi xen lẫn tiêu bản hóa thạch cúc đá (ammonite) và bọ ba thùy.",
                "reason_vi": "Vẻ đẹp hoài cổ của những cuốn sổ tay khảo sát địa chất thế kỷ trước, tạo niềm tin cậy tuyệt đối về mặt lịch sử khoa học.",
            },
        },
    },
    "en-inside-vessel": {
        "title_vi": "Sinh Lý Học Tế Bào & Cơ Chế Y Học Lâm Sàng",
        "scene_vi": "Hành trình nội tế bào: Một dòng máu cuộn chảy qua van tim động mạch chủ, các tế bào hồng cầu co giãn vượt qua áp lực mao mạch dưới kính hiển vi vi mô.",
        "styles_vi": {
            "style_1": {
                "name_vi": "Nucleus Medical — Mô Phỏng 3D Vi Mô Y Khoa Chuyên Sâu",
                "aesthetic_vi": "Mô phỏng 3D y khoa siêu chi tiết với tán xạ dưới bề mặt (subsurface scattering); tế bào hồng cầu lõm hai mặt trôi trong lòng vi mạch đỏ sẫm (#1A0507); ánh sáng xuyên thấu màng tế bào chân thực.",
                "reason_vi": "Chuẩn mực đồ họa của các viện y học và bệnh viện hàng đầu thế giới, mang lại độ chính xác giải phẫu tuyệt đối.",
            },
            "style_2": {
                "name_vi": "Hashem Al-Ghaili — Tế Bào Thần Kinh Huỳnh Quang Neon",
                "aesthetic_vi": "Mạng nơ-ron phát sáng huỳnh quang sinh học trên nền đen hắc diện thạch (#05070B); sợi thần kinh neon cyan (#00F0FF) và tím thạch anh; xung điện phát sáng rực rỡ tại các khe synap.",
                "reason_vi": "Biến cơ chế truyền tin sinh học thành một bữa tiệc thị giác hiện đại, công nghệ cao và kích thích thị giác mạnh mẽ.",
            },
            "style_3": {
                "name_vi": "Vintage Gray's Anatomy — Tranh Khắc Kim Loại Cổ Điển",
                "aesthetic_vi": "Tranh khắc kim loại giải phẫu kinh điển thế kỷ 19 của Henry Vandyke Carter trên giấy vellum kem ấm (#F7F2E7); nét khắc chéo tỉ mỉ (cross-hatching) với mực nâu sắt và vệt màu nước crimson nhạt.",
                "reason_vi": "Phong cách kinh điển vượt thời gian của y văn thế giới, toát lên sự tôn nghiêm và tinh hoa y học truyền thống.",
            },
            "style_4": {
                "name_vi": "Blueprint Cơ Học Van Tim (Mẫu Prussian Blue Của Bạn)",
                "aesthetic_vi": "Bản vẽ kỹ thuật xanh Prussian (#133E68); nét phấn trắng (#FFFFFF) phác họa cơ học van tim động mạch chủ; một điểm nhấn màu vàng nghệ (#F5B027) biểu thị vectơ áp lực và vận tốc dòng chảy huyết động học.",
                "reason_vi": "Giải thích cơ thể người như một cỗ máy cơ khí sinh học hoàn hảo, sáng rõ và không gây cảm giác phản cảm cho người xem sợ máu.",
            },
        },
    },
    "en-macro-gears": {
        "title_vi": "Kinh Tế Vĩ Mô, Chuỗi Cung Ứng & Hạ Tầng Công Nghiệp",
        "scene_vi": "Mạch máu kinh tế: Cảng biển container tự động hóa hoạt động suốt đêm, mạng lưới logistics kết nối trạm biến áp cao thế và tàu chở hàng khổng lồ luân chuyển hàng hóa toàn cầu.",
        "styles_vi": {
            "style_1": {
                "name_vi": "Practical Engineering — Sa Bàn 3D Isometric Hạ Tầng",
                "aesthetic_vi": "Mô hình sa bàn 3D isometric trạm biến áp cao thế và container logistics trên bàn thí nghiệm kỹ thuật; chất liệu thép mạ kẽm, sứ cách điện và ray cẩu thực tế dưới ánh sáng lab sắc sảo.",
                "reason_vi": "Giúp người xem hiểu ngay cơ chế vận hành của những công trình hạ tầng phức tạp nhất theo chuẩn Practical Engineering (4.2M subs).",
            },
            "style_2": {
                "name_vi": "Economics Explained — Báo Chí Tài Chính Trên Đá Slate Tối",
                "aesthetic_vi": "Cảng hạ tầng và container trên bệ đá obsidian sẫm màu (#0F172A); tia laser đỏ/vàng quét ngang thể hiện định giá tư bản, chu kỳ kinh tế và dòng luân chuyển vốn toàn cầu.",
                "reason_vi": "Tạo phong thái quyền lực, sắc sảo của báo chí tài chính quốc tế như Economics Explained (2.6M subs).",
            },
            "style_3": {
                "name_vi": "Blueprint Chuỗi Cung Ứng Toàn Cầu (Mẫu Prussian Blue Của Bạn)",
                "aesthetic_vi": "Chuỗi cung ứng container & trạm điện vẽ nét trắng phấn trên nền xanh Prussian (#133E68) với điểm nhấn độc nhất container màu vàng nghệ (#F5B027) theo đúng mẫu chuẩn của bạn.",
                "reason_vi": "Thể hiện mạng lưới thương mại quốc tế dưới dạng một sơ đồ kỹ thuật thanh lịch, mạch lạc và đậm chất chiến lược.",
            },
            "style_4": {
                "name_vi": "Visual Capitalist — Infographic Phân Tầng Dữ Liệu",
                "aesthetic_vi": "Infographic phân tầng dữ liệu hạ tầng công nghiệp; màu teal thép (#1B4965) và đất nung (#D97706) tương phản cao trên nền giấy ngà ấm; phân tách dòng vốn và chuỗi cung ứng rõ ràng.",
                "reason_vi": "Khả năng truyền đạt dữ liệu trực quan cực nhanh, cuốn hút người xem từ giây đầu tiên như Visual Capitalist.",
            },
        },
    },
    "en-fine-print": {
        "title_vi": "Luật Tiêu Dùng, Bẫy Hợp Đồng & Kẽ Hở Pháp Lý",
        "scene_vi": "Soi xét hợp đồng: Một chiếc kính lúp phóng to điều khoản miễn trừ trách nhiệm nhỏ li ti bị chôn vùi trong hợp đồng tín dụng, một con dấu đỏ cảnh báo bẫy phạt tài chính bất lợi.",
        "styles_vi": {
            "style_1": {
                "name_vi": "Forensic Macro — Tài Liệu Pháp Y & Con Dấu Đỏ Niêm Phong",
                "aesthetic_vi": "Cận cảnh macro tài liệu hợp đồng tiêu dùng trên giấy parchment kem nhăn; con dấu mực đỏ weathered seal; kính lúp vintage bằng đồng khúc xạ dòng điều khoản bẫy; dấu vân tay pháp y mờ ở mép viền.",
                "reason_vi": "Mang lại cảm giác chân thật và căng thẳng của một cuộc điều tra vạch trần chiêu trò lừa dối người tiêu dùng.",
            },
            "style_2": {
                "name_vi": "LegalEagle — Điện Ảnh Phòng Xử Án Kịch Tính Noir",
                "aesthetic_vi": "Ánh sáng điện ảnh rèm chớp tạo bóng đổ sọc ngựa vằn gắt gao lên mặt bàn luật sư gỗ mahogany tối; búa thẩm phán đồng thau bóng bẩy nằm giữa luồng sáng; kệ sách luật mờ bokeh hậu cảnh.",
                "reason_vi": "Tái hiện không khí uy nghiêm và kịch tính của các phiên tòa đỉnh cao như LegalEagle (3.3M subs).",
            },
            "style_3": {
                "name_vi": "Blueprint Ma Trận Điều Khoản Hợp Đồng (Mẫu Prussian Blue)",
                "aesthetic_vi": "Phong cách blueprint xanh Prussian bám sát mẫu người dùng; các đường drafting trắng tinh xảo biểu diễn lưu đồ ma trận điều khoản hợp đồng; điểm nhấn nút phạt tài chính màu vàng rực (#FFC107).",
                "reason_vi": "Biến mớ bòng bong văn bản luật thành một sơ đồ kiến trúc mạch lạc, giúp người xem nhìn thấy ngay kẽ hở chí mạng.",
            },
            "style_4": {
                "name_vi": "CNBC Make It — Đồ Họa Cắt Dán Báo Chí Điều Tra",
                "aesthetic_vi": "Đồ họa phóng sự điều tra cắt dán (mixed-media collage); các lớp tài liệu hợp đồng xé rách; kẹp bulldog kim loại sáng bóng; vệt highlight neon vàng (#FFE600) gạch chéo phần nội dung bẫy.",
                "reason_vi": "Năng động, hiện đại và rất trực quan, mang đậm ngôn ngữ phóng sự tài chính thực chiến của CNBC.",
            },
        },
    },
    "en-crowd-strings": {
        "title_vi": "Tâm Lý Đám Đông, Thao Túng Xã Hội & Hiệu Ứng Lan Truyền",
        "scene_vi": "Lực lượng vô hình: Một đám đông vô diện đồng loạt bước đi theo một nhịp điệu bị thao túng bởi những sợi dây rối từ bóng tối; một cá nhân bừng tỉnh cắt đứt dây liên kết.",
        "styles_vi": {
            "style_1": {
                "name_vi": "Academy of Ideas — Tranh Khắc Gỗ Chính Luận Cổ Điển",
                "aesthetic_vi": "Khắc gỗ chính luận tương phản chiaroscuro cực độ; đoàn người bóng đen vô diện bước đều tăm tắp dưới chóp nón ánh sáng gắt của ngọn đèn đường cổ; vệt bóng đổ hatched kéo dài trên nền đá.",
                "reason_vi": "Mang chiều sâu triết học và tâm lý học xã hội u tối, cảnh tỉnh người xem như Academy of Ideas (2M subs).",
            },
            "style_2": {
                "name_vi": "Fern — Cắt Dán Tài Liệu Báo Chí Điều Tra Tối Màu",
                "aesthetic_vi": "Ống kính camera giám sát khổng lồ rọi xuống từ vùng tối graphite; những sợi dây rối thao túng màu đỏ thắm (#D90429) kết nối thẳng vào các bóng người cắt dán phân tầng xã hội.",
                "reason_vi": "Khắc họa trực quan các cơ chế thao túng truyền thông ngầm theo phong cách tài liệu điều tra giật gân của Fern.",
            },
            "style_3": {
                "name_vi": "Vox — Đồ Họa Vector Hình Học Chuyển Động Hiện Đại",
                "aesthetic_vi": "Kim tự tháp phân tầng xã hội bằng hình học phẳng sắc cạnh; biểu tượng đám đông đồng bộ ở tầng dưới bị định hướng bởi dòng vector vàng neon từ đỉnh chóp quyền lực trên nền xanh cobalt (#0B192C).",
                "reason_vi": "Đồ họa vector báo chí thời thượng, sắc bén, kích thích tư duy phân tích của khán giả đại chúng.",
            },
            "style_4": {
                "name_vi": "Blueprint Ma Trận Xã Hội Học (Mẫu Prussian Blue Của Bạn)",
                "aesthetic_vi": "Sơ đồ blueprint xanh Prussian thể hiện mạng lưới liên kết đám đông bằng nét phấn trắng; nổi bật với 1 node cá nhân nổi loạn màu vàng neon (#FAFF00) cắt đứt dây liên kết và bứt phá ra ngoài.",
                "reason_vi": "Thể hiện tâm lý bầy đàn như một mạng lưới thuật toán xã hội học, tinh tế và đầy tri thức.",
            },
        },
    },
    "en-cold-case-ink": {
        "title_vi": "Kỳ Án Lịch Sử, Giải Mã Tài Liệu Mật & Điều Tra Hình Sự",
        "scene_vi": "Hiện trường bí ẩn: Một ngọn đèn đường cổ đơn độc chiếu sáng chiếc xe hơi bỏ hoang trên con đường nhựa ướt sương đêm; những dải băng cảnh báo và vệt quỹ đạo di chuyển của kẻ đào tẩu.",
        "styles_vi": {
            "style_1": {
                "name_vi": "LEMMiNO — Sa Bàn 3D Noir Điện Ảnh (Volumetric Diorama)",
                "aesthetic_vi": "Sa bàn 3D điện ảnh u tối; mặt đường nhựa và đá ướt sau mưa phản chiếu ánh nước; sương mù thể tích cuộn xoáy; duy nhất 1 ngọn đèn đường cổ điển rọi luồng sáng vàng hổ phách xuống hiện trường chiếc xe cổ 1940s.",
                "reason_vi": "Đạt chuẩn phong cách điều tra trinh thám thượng thừa, lạnh lùng và cuốn hút không thể rời mắt của LEMMiNO (5.6M subs).",
            },
            "style_2": {
                "name_vi": "Bedtime Stories — Tranh Than Chì & Mực Tàu Ủ Rũ",
                "aesthetic_vi": "Tranh than chì và mực tàu ủ rũ trên giấy cổ ẩm mốc; bóng đen mờ ảo rợn gáy; vệt loang mực thô ráp; ánh sáng chiaroscuro tương phản cao tạo cảm giác tâm lý bí ẩn rùng rợn.",
                "reason_vi": "Tạo ra bầu không khí u ám, huyền bí và ám ảnh tâm lý cực kỳ đặc trưng của Bedtime Stories.",
            },
            "style_3": {
                "name_vi": "Johnny Harris — Bảng Ghim Manh Mối Điều Tra (Dossier Pinboard)",
                "aesthetic_vi": "Bảng điều tra án mạng trên nền bảng bần / hồ sơ vụ án; mạng lưới chỉ đỏ căng nối các manh mối; ảnh tư liệu đen trắng cũ kỹ; tài liệu mật đóng dấu bị bôi đen kiểm duyệt cùng ghi chú khẩn.",
                "reason_vi": "Đưa người xem nhập vai vào vị trí của một thám tử đang xâu chuỗi những manh mối tưởng như rời rạc.",
            },
            "style_4": {
                "name_vi": "Blueprint Quỹ Đạo Hiện Trường Pháp Y (Mẫu Prussian Blue)",
                "aesthetic_vi": "Bản vẽ kỹ thuật xanh Prussian; nét vẽ kỹ thuật trắng sắc lạnh; chuyên viên pháp y cầm compa vạch cung đường quỹ đạo đối tượng đào tẩu với điểm nhấn màu vàng mù tạt tối giản; khoảng trống âm >75%.",
                "reason_vi": "Phân tích hiện trường vụ án dưới góc nhìn khoa học hình sự và toán học quỹ đạo, chuyên nghiệp và đầy sức thuyết phục.",
            },
        },
    },
    "en-choke-point": {
        "title_vi": "Địa Chính Trị Eo Biển Hàng Hải & Điểm Nghẽn Chiến Lược",
        "scene_vi": "Cổ chai sinh tử: Một đoàn tàu chở dầu siêu trọng luồn qua eo biển hẹp hiểm trở, hai bên bờ là hệ thống radar và khẩu đội phòng thủ bờ biển theo dõi từng chuyển động.",
        "styles_vi": {
            "style_1": {
                "name_vi": "RealLifeLore — Bản Đồ Vệ Tinh & Vector Dạ Quang Phát Sáng",
                "aesthetic_vi": "Phối hợp ảnh vệ tinh địa hình quang học độ phân giải cao với hệ thống vector dạ quang — luồng hải hành xanh cyan rực (#00F0FF); biên giới lãnh thổ dạ quang đỏ thẫm và mũi tên bao vây chiến lược hướng vào cổ chai eo biển.",
                "reason_vi": "Trực quan hóa tức thì tầm quan trọng địa chiến lược của các eo biển then chốt toàn cầu chuẩn RealLifeLore (7.6M subs).",
            },
            "style_2": {
                "name_vi": "CaspianReport — Bàn Tròn Chiến Lược & Vệt Dầu Loang",
                "aesthetic_vi": "Không khí phòng tác chiến tối mật (War Room); mặt đá phiến than chì (#12161A); đèn rọi hội tụ (chiaroscuro) cô đọng trên bản đồ eo biển Malacca/Hormuz; vệt dầu loang đen bóng lấp lánh phản quang.",
                "reason_vi": "Đậm chất phân tích địa chính trị hàn lâm, sâu sắc và đầy sức nặng của CaspianReport.",
            },
            "style_3": {
                "name_vi": "Hải Đồ Quân Sự Blueprint (Mẫu Prussian Blue Của Bạn)",
                "aesthetic_vi": "Hải đồ hàng hải quân sự trên giấy sần xanh đậm Prussian (#133E68); nét vẽ phấn trắng kỹ thuật (#FFFFFF); vòng cung tầm bắn tên lửa phòng thủ; điểm nhấn vàng nghệ (#F5B027) duy nhất cho tàu hàng.",
                "reason_vi": "Chuyển hóa bài toán địa chính trị quân sự thành một bản thiết kế chiến lược hải quân sắc bén, sang trọng.",
            },
            "style_4": {
                "name_vi": "PolyMatter — Sa Bàn Địa Hình Cảng Biển Isometric",
                "aesthetic_vi": "Sa bàn địa hình hạ tầng cảng biển nước sâu dạng isometric tối giản trên nền đá phiến sẫm (#1E232A); tháp cẩu container hình học; dải băng vector luồng logistics màu cyan cùng khối container màu pastel nhã nhặn.",
                "reason_vi": "Hiện đại, thanh lịch, làm nổi bật hạ tầng giao thương hàng hải toàn cầu.",
            },
        },
    },
    "en-root-and-canopy": {
        "title_vi": "Thực Vật Học, Mạng Lưới Nấm Ngầm & Sinh Thái Rừng Già",
        "scene_vi": "Mạng internet của rừng: Một chồi cây non đâm rễ vào lòng đất mùn rừng già, gặp gỡ và kết nối với hàng triệu sợi nấm ngầm phát quang trao đổi chất dinh dưỡng.",
        "styles_vi": {
            "style_1": {
                "name_vi": "In Defense of Plants — Tranh Màu Nước Tiêu Bản Cổ Điển",
                "aesthetic_vi": "Tranh minh họa thực vật học thế kỷ 18 trên giấy dệt vân hạt thô màu kem ấm (#F5EFE1); nét mực cổ điển; vệt loang màu nước tự nhiên (sap green #3F5E38, raw umber #5C4033); rễ củ mao dẫn ăn sâu dưới lòng đất.",
                "reason_vi": "Mang vẻ đẹp di sản của các cuộc thám hiểm thực vật học hoàng gia, trang nhã và chuẩn xác khoa học.",
            },
            "style_2": {
                "name_vi": "BBC Earth — Điện Ảnh Tán Rừng Nhiệt Đới Mù Sương",
                "aesthetic_vi": "Góc máy ngước nhìn rễ bạnh vè khổng lồ của đại thụ vươn lên màn sương rừng nhiệt đới; luồng nắng sớm xiên qua tán lá (god rays); rêu phong ẩm ướt bám trên vỏ cây; giọt sương mai phản chiếu lấp lánh.",
                "reason_vi": "Đưa người xem đắm chìm vào hơi thở sống động của rừng nguyên sinh theo chuẩn phim tài liệu The Green Planet của BBC Earth.",
            },
            "style_3": {
                "name_vi": "Mossy Earth — Mô Phỏng 3D Mạng Lưới Nấm Ngầm Phát Quang",
                "aesthetic_vi": "Mô phỏng 3D vi mô dưới lòng đất mùn tối (#0A0C0E); hàng ngàn sợi nấm ngầm mycorrhizae phát quang sinh học neon cyan & cốm huỳnh quang quấn chặt chóp rễ cây, trao đổi luồng photon năng lượng.",
                "reason_vi": "Lột tả được kỳ quan 'Wood Wide Web' ngầm dưới lòng đất mà mắt thường không bao giờ nhìn thấy được.",
            },
            "style_4": {
                "name_vi": "Blueprint Kiến Trúc Cây Rừng (Mẫu Prussian Blue Của Bạn)",
                "aesthetic_vi": "Bản vẽ kỹ thuật Prussian Blue (#133E68) với nét phấn trắng (#FFFFFF) mổ xẻ cơ chế mao dẫn hút nước của mạch rây/mạch gỗ xylem ngược trọng lực; điểm nhấn giọt nước và lá non vàng nghệ (#F5B027) & xanh cốm.",
                "reason_vi": "Minh họa cây đại thụ như một kỳ quan kỹ thuật thủy lực của thiên nhiên, cực kỳ sáng rõ và trí tuệ.",
            },
        },
    },
    "en-spawn-to-apex": {
        "title_vi": "Sinh Thái Côn Trùng, Biến Thái Hoàn Toàn & Thế Giới Vi Mô",
        "scene_vi": "Kỳ quan vi mô: Một giọt sương đọng trên mắt kép chuồn chuồn phản chiếu ánh bình minh, bóc tách cấu trúc cơ sinh học đòn bẩy bật nhảy siêu thanh của côn trùng.",
        "styles_vi": {
            "style_1": {
                "name_vi": "Deep Look — Quay Phim Ultra-Macro Hiển Vi Siêu Chi Tiết",
                "aesthetic_vi": "Kỹ thuật quay ultra-macro bằng probe lens chuyên dụng trên nền tối hữu cơ (#0B0F19); hàng ngàn thấu kính ommatidia lục giác óng ánh đa sắc (ngọc bích, vàng hổ phách, ngọc lam) trên mắt kép chuồn chuồn.",
                "reason_vi": "Mở ra một thế giới côn trùng sống động, kỳ vĩ như những cỗ máy tương lai chuẩn Deep Look (PBS - 2.1M subs).",
            },
            "style_2": {
                "name_vi": "SEM Scientific — Kính Hiển Vi Điện Tử Quét Phủ Màu Neon",
                "aesthetic_vi": "Ảnh chụp hiển vi điện tử quét SEM phóng đại 5,000x với kỹ thuật phối màu giả neon sinh học (cyan điện #00F0FF, tím magenta #D946EF); các tầng vi vảy cánh bướm xếp lớp như ngói lợp khúc xạ nano.",
                "reason_vi": "Mang lại sự kinh ngạc tuyệt đối về cấu trúc vật liệu nano tự nhiên, đậm tính công nghệ tương lai.",
            },
            "style_3": {
                "name_vi": "Naturalist Gouache — Tranh Tiêu Bản Côn Trùng Bảo Tàng",
                "aesthetic_vi": "Tranh tiêu bản côn trùng màu bột bảo tàng cổ điển trên giấy ngà cổ (#F6F1E3); mẫu bọ cánh cứng óng ánh kim loại (Chrysina resplendens) với lớp vỏ kitin xanh lục bảo phản chiếu ánh đồng, gắn kim ghim đồng vintage.",
                "reason_vi": "Vẻ đẹp sang trọng, cổ điển của các phòng trưng bày mẫu vật hoàng gia châu Âu.",
            },
            "style_4": {
                "name_vi": "Blueprint Cơ Sinh Học Động Lực (Mẫu Prussian Blue Của Bạn)",
                "aesthetic_vi": "Bản vẽ kỹ thuật blueprint xanh Prussian (#0F2942); sơ đồ động lực học cơ sinh học nét trắng bone-white (#F8FAFC) và cyan (#38BDF8) bóc tách cơ cấu đòn bẩy đàn hồi nén đệm resilin phóng nhảy của bọ chét.",
                "reason_vi": "Phân tích côn trùng dưới lăng kính kỹ thuật cơ khí chính xác, mạch lạc và độc đáo.",
            },
        },
    },
    "en-second-arrow": {
        "title_vi": "Chủ Nghĩa Khắc Kỷ Stoicism & Thiền Triết Học",
        "scene_vi": "Hóa giải nỗi đau: Đứng trước mũi tên nghịch cảnh bắn tới, người thực hành Stoic dùng bàn tay cẩm thạch hóa giải tổn thương, giữ vững sự an nhiên tuyệt đối (Ataraxia).",
        "styles_vi": {
            "style_1": {
                "name_vi": "Daily Stoic — Tượng Cẩm Thạch La Mã Ánh Sáng Caravaggio",
                "aesthetic_vi": "Tượng cẩm thạch bán thân Marcus Aurelius / Seneca dưới chùm sáng Caravaggio xuyên thấu bóng tối obsidian; bàn tay đá cẩm thạch bình thản bẻ gãy mũi tên gỗ ngay trước ngực (triệt tiêu 'mũi tên thứ hai' của đau khổ).",
                "reason_vi": "Khắc họa ý chí sắt đá và nội tâm bất biến trước phong ba bão táp của cuộc đời chuẩn Daily Stoic (2M subs).",
            },
            "style_2": {
                "name_vi": "Pursuit of Wonder — Thủy Mặc Thiền Tông Sumi-e",
                "aesthetic_vi": "Tranh thủy mặc Sumi-e trên giấy washi dâu tằm; cành tùng cổ thụ bám rễ vách đá granite; mũi tên mực đen phóng qua màn sương nhưng đi xuyên qua không gian trống rỗng, tan biến thành giọt nước vô hại.",
                "reason_vi": "Thể hiện sự buông bỏ, hòa tan chấp niệm và tâm tĩnh lặng như nước theo triết lý Thiền tông phương Đông.",
            },
            "style_3": {
                "name_vi": "Einzelgänger — Tối Giản Hiện Đại & Tĩnh Lặng Độc Hành",
                "aesthetic_vi": "Bóng người cô độc đứng ngắm mặt biển phẳng lặng mù sương dưới bầu trời hoàng hôn xám khói; dưới chân là cây cung đã tháo dây và mũi tên nằm yên vô hại trên đá; hơn 60% không gian âm tĩnh mịch.",
                "reason_vi": "Mang lại sự đồng cảm sâu sắc cho những ai đang tìm kiếm sự bình yên và tự do nội tâm giữa thế giới ồn ào.",
            },
            "style_4": {
                "name_vi": "Stoic Citadel Blueprint (Mẫu Prussian Blue Của Bạn)",
                "aesthetic_vi": "Bản vẽ kỹ thuật xanh Prussian; sơ đồ các tầng thành lũy đồng tâm của 'Inner Citadel' bảo vệ tâm trí; mũi tên hỗn loạn bên ngoài vỡ tan khi va vào tường thành; ngọn nến vàng nghệ (#F5B027) cháy sáng vĩnh cửu tại tâm điện.",
                "reason_vi": "Hình tượng hóa 'Thành Trì Nội Tâm' của Marcus Aurelius thành một kiến trúc bất khả xâm phạm, cực kỳ thanh lịch.",
            },
        },
    },
    "en-bamboo-marble": {
        "title_vi": "Triết Học Đông Phương, Đạo Giáo & Bài Học Nhân Sinh",
        "scene_vi": "Đạo của tự nhiên: Rừng tre uốn mình theo bão lớn mà không gãy (Vô Vi), dòng nước luồn lách qua ghềnh đá, chén trà gốm mộc nứt rạn được hàn gắn bằng chỉ vàng Kintsugi.",
        "styles_vi": {
            "style_1": {
                "name_vi": "Philosophies for Life — Tranh Khắc Gỗ Ukiyo-e Truyền Thống",
                "aesthetic_vi": "Tranh khắc gỗ thời kỳ Edo trên giấy washi có vân sợi xơ; rừng tre xanh uốn mình uyển chuyển trong bão gió mà không gãy; bên dưới là sóng cuộn gợn nét mực sumi truyền thống uốn quanh đá cuội.",
                "reason_vi": "Tái hiện trọn vẹn tinh hoa triết lý Đạo giáo qua ngôn ngữ mỹ thuật truyền thống đỉnh cao của Nhật Bản và Á Đông.",
            },
            "style_2": {
                "name_vi": "Aperture — Tranh Than Chì Điện Ảnh U Hoài (Charcoal Noir)",
                "aesthetic_vi": "Tranh than chì điện ảnh u hoài, hạt giấy thô ráp, ánh sáng chiaroscuro tương phản; phố mưa đêm phản chiếu vệt đèn vàng ấm; bóng người măng-tô trầm tư tìm kiếm ý nghĩa cuộc đời trong sương mờ.",
                "reason_vi": "Gợi cảm xúc triết học hiện sinh phương Tây, sâu lắng và day dứt như Aperture (2.8M subs).",
            },
            "style_3": {
                "name_vi": "The Art of Improvement — Gốm Kintsugi Hàn Gắn Bằng Vàng",
                "aesthetic_vi": "Chén gốm thô mộc rạn nứt được hàn gắn tỉ mỉ bằng chỉ vàng óng ả (#D4AF37) trên nền đá mộc ướt sương; một chiếc lá tre xanh rơi khẽ bên cạnh; tia nắng komorebi rọi chéo tĩnh tại.",
                "reason_vi": "Tôn vinh vẻ đẹp của sự bất toàn và quá trình chữa lành nội tâm qua thẩm mỹ Wabi-Sabi tinh tế.",
            },
            "style_4": {
                "name_vi": "Blueprint Hình Học Triết Học (Mẫu Prussian Blue Của Bạn)",
                "aesthetic_vi": "Nền xanh đậm Prussian Blue (#133E68) vân vải mỹ thuật; nét vẽ trắng phấn kỹ thuật sắc sảo; học giả đo compa trên đường xoắn ốc tỷ lệ vàng; vòng lặp nhân quả nét trắng với điểm nhấn vàng nghệ rực rỡ tại tâm điểm.",
                "reason_vi": "Hòa quyện triết học Đông phương với toán học hình học phương Tây, sang trọng và giàu trí tuệ.",
            },
        },
    },
    "en-kindred-sketch": {
        "title_vi": "Tâm Lý Học Mối Quan Hệ, Thuyết Gắn Bó & Sự Thấu Cảm",
        "scene_vi": "Cầu nối tâm hồn: Hai người ngồi đối diện nhau trong không gian ấm áp, khoảng cách tâm lý thu hẹp lại khi họ thấu hiểu được phong cách gắn bó của nhau.",
        "styles_vi": {
            "style_1": {
                "name_vi": "The School of Life — Tranh Màu Bột Triết Học Ấm Áp (Gouache)",
                "aesthetic_vi": "Tranh minh họa màu bột phong cách triết học phương Tây ấm áp; bảng màu terracotta (#C8644A), chàm indigo và vàng mù tạt; chiều sâu nội tâm qua ánh mắt biết lắng nghe và không gian đối thoại ấm cúng.",
                "reason_vi": "Đậm chất nhân văn, trị liệu tâm lý và giàu lòng trắc ẩn chuẩn The School of Life (9.3M subs).",
            },
            "style_2": {
                "name_vi": "Psych2Go — Màu Nước Phấn Tiên Dịu Nhẹ Chữa Lành",
                "aesthetic_vi": "Phong cách màu nước phấn tiên (soft pastel) dịu nhẹ; nét vẽ bo tròn ấm áp, nhân vật chibi hiền hòa; bảng màu hoàng hôn êm dịu (sunset peach, lavender, chamomile honey), tạo cảm giác an toàn và được vỗ về.",
                "reason_vi": "Tạo sự an tâm tuyệt đối cho khán giả đang tổn thương tâm lý như Psych2Go (12.8M subs).",
            },
            "style_3": {
                "name_vi": "Cinema Therapy — Khung Hình Điện Ảnh 35mm Sâu Lắng",
                "aesthetic_vi": "Khung hình điện ảnh 35mm sâu lắng; kỹ thuật chiếu sáng chiaroscuro với ánh sáng vàng mật ong (#E5A93C) viền quanh chủ thể trên nền tối; khoảnh khắc hai bàn tay khẽ chạm nhau vượt qua khoảng cách vô hình.",
                "reason_vi": "Ghi lại những khoảnh khắc cảm xúc tinh tế nhất của con người qua lăng kính điện ảnh.",
            },
            "style_4": {
                "name_vi": "Blueprint Động Lực Gắn Bó (Mẫu Prussian Blue Của Bạn)",
                "aesthetic_vi": "Nền xanh Prussian có vân giấy mỹ thuật (#133E68); nét vẽ phấn trắng kỹ thuật (#FFFFFF) mô phỏng quỹ đạo và trục gắn bó tâm lý; điểm xuyết duy nhất sợi chỉ đỏ (#E63946) kết nối hai trái tim.",
                "reason_vi": "Bản vẽ khoa học giải phẫu tâm lý tình cảm, vừa hiện đại vừa giàu chất thơ.",
            },
        },
    },
    "en-lazy-brain": {
        "title_vi": "Thần Kinh Học Thói Quen, Dopamine & Khả Năng Tập Trung",
        "scene_vi": "Cuộc chiến não bộ: Vỏ não trước trán (Prefrontal Cortex) nỗ lực điều khiển vô lăng lý trí vượt qua vòng xoáy cám dỗ dopamine tức thì của hệ viền (Limbic System).",
        "styles_vi": {
            "style_1": {
                "name_vi": "Mạng Nơ-ron Phát Quang Neon (Synaptic Circuit Neon Glow)",
                "aesthetic_vi": "Nền đen obsidian 3D sâu thẳm (#050811); mô hình bán trong suốt não bộ phát sáng huỳnh quang; mạng lưới nơ-ron phát xung điện cyan (#06B6D4) và magenta (#EC4899); dòng dẫn truyền dopamine vàng hổ phách rực rỡ.",
                "reason_vi": "Giải mã các phản ứng hóa sinh não bộ dưới dạng đồ họa khoa học viễn tưởng siêu cuốn hút.",
            },
            "style_2": {
                "name_vi": "MinutePhysics / Chalkboard — Sơ Đồ Bảng Đen Thần Kinh Học",
                "aesthetic_vi": "Mặt bảng đen đá phiến cổ điển (#1E232A) với vết bụi phấn tự nhiên; nét phấn trắng (#F8FAFC) và vàng tươi (#FDE047) phác thảo sơ đồ vòng lặp thói quen tròn (Cue - Routine - Reward) tương phản cao.",
                "reason_vi": "Trực quan, dễ hiểu như một bài giảng thú vị của giáo sư tâm huyết trên MinutePhysics.",
            },
            "style_3": {
                "name_vi": "Improvement Pill — Vector Chuyển Động Leo Thang Vô Tận",
                "aesthetic_vi": "Phong cách đồ họa vector báo chí trên nền xám tối giản (#F1F5F9); hình tượng người đàn ông silhouette đen leo trên cầu thang hình học M.C. Escher vô tận hướng về đỉnh vàng kỷ luật; khối sao nhãng rơi rụng bên dưới.",
                "reason_vi": "Biểu tượng ẩn dụ mạnh mẽ về hành trình rèn luyện kỷ luật bản thân của Improvement Pill (3.4M subs).",
            },
            "style_4": {
                "name_vi": "Blueprint Điều Hướng Não Bộ (Mẫu Prussian Blue Của Bạn)",
                "aesthetic_vi": "Phong cách kiến trúc Prussian blue theo mẫu người dùng gửi (#11446F); nét mực kỹ thuật trắng thanh thoát vẽ sơ đồ mạch điều hướng não bộ; cung tròn compa và nút điều hướng vàng mustard (#E5A93C).",
                "reason_vi": "Xem não bộ như một cỗ máy điều hướng tinh vi, mang lại sự sáng rõ tuyệt đối cho người xem.",
            },
        },
    },
    "en-career-leverage": {
        "title_vi": "Đòn Bẩy Sự Nghiệp, Đàm Phán Lương & Game Theory Công Sở",
        "scene_vi": "Thế cờ công sở: Trong căn phòng kính penthouse nhìn ra thành phố, một chuyên gia cấp cao dịch chuyển quân cờ King mạ vàng trên bàn đàm phán, chuyển hóa năng lực thành đòn bẩy thăng tiến.",
        "styles_vi": {
            "style_1": {
                "name_vi": "HBR — Nhiếp Ảnh Báo Chí Kinh Doanh Cấp Cao (Executive Editorial)",
                "aesthetic_vi": "Bàn làm việc executive gỗ sồi Châu Âu; ánh sáng cửa sổ kính penthouse rực rỡ; hồ sơ KPI da sang trọng; bút máy đen viền vàng; chiều sâu quang học chuẩn báo chí kinh doanh HBR (3.8M subs).",
                "reason_vi": "Toát lên đẳng cấp, quyền lực và sự tự tin của những nhà lãnh đạo hàng đầu.",
            },
            "style_2": {
                "name_vi": "WSJ Explains — Đồ Họa Bậc Thang Tài Chính Sắc Bén",
                "aesthetic_vi": "Biểu đồ bậc thang thăng tiến màu xanh lục rừng WSJ (#1B4D3E) và than chì; 2 nhân vật silhouette thanh lịch đối thoại đàm phán lương trên đỉnh nấc thang; bố cục infographic sắc bén.",
                "reason_vi": "Phong cách đồ họa tài chính sắc sảo, thực dụng và đầy uy quyền của Wall Street Journal (5.3M subs).",
            },
            "style_3": {
                "name_vi": "Alex Hormozi — Vector Tương Phản Năng Lượng Cao (High-Impact)",
                "aesthetic_vi": "Nền đen obsidian (#0A0A0A); đòn bẩy thép cơ học nâng tảng đá vàng khổng lồ; tia năng lượng và vệt gia tốc vàng neon chói lọi; tương phản cực gắt đầy bứt phá.",
                "reason_vi": "Truyền tải năng lượng hành động bùng nổ, dứt khoát chuẩn phong cách Alex Hormozi (3.1M subs).",
            },
            "style_4": {
                "name_vi": "Blueprint Game Theory Công Sở (Mẫu Prussian Blue Của Bạn)",
                "aesthetic_vi": "Nền xanh Prussian (#154360) với lưới kỹ thuật và cung compa; sơ đồ cây quyết định đàm phán lương và nước đi cờ vua công sở; quân cờ King vương miện mạ vàng Canary rực rỡ.",
                "reason_vi": "Xem các cuộc đàm phán sự nghiệp như một ván cờ chiến thuật tinh vi, lịch lãm và sâu sắc.",
            },
        },
    },
    "en-wallet-anatomy": {
        "title_vi": "Tâm Lý Định Giá, Cơ Chế Tài Chính Cá Nhân & Tiền Tệ",
        "scene_vi": "Cơ chế đồng tiền: Một chiếc ví bung mở để lộ các van điều tiết dòng thu nhập, các ống dẫn phân bổ vào quỹ khẩn cấp, tài khoản đầu tư sinh lãi kép.",
        "styles_vi": {
            "style_1": {
                "name_vi": "PBS Two Cents — Đồ Họa Cắt Giấy 2D Thân Thiện (Paper-Cut)",
                "aesthetic_vi": "Chiếc ví da bung mở ở khu vực trung tâm; các dải tiền tệ giấy cắt đa lớp và đồng xu vàng uốn lượn tuôn trào theo hình vòng cung đầy sức sống trên nền giấy kem ấm áp (#FAF6EE).",
                "reason_vi": "Gần gũi, hóm hỉnh và biến chủ đề tài chính khô khan thành câu chuyện thú vị theo chuẩn PBS Two Cents.",
            },
            "style_2": {
                "name_vi": "Graham Stephan — Tương Phản Sang Trọng Thẻ Đen & Tiền Vàng",
                "aesthetic_vi": "Thẻ đen kim loại góc nghiêng sang trọng lơ lửng dưới chùm đèn spotlight rọi từ trên xuống; bên cạnh là cọc tiền xu vàng nguyên khối phản chiếu ánh sáng sắc lẹm trên nền đá than chì tối.",
                "reason_vi": "Tạo sức hút mãnh liệt về sự thịnh vượng tài chính cá nhân như Graham Stephan (4.5M subs).",
            },
            "style_3": {
                "name_vi": "Humphrey Yang — Bảng Trắng Sketch Marker Tối Giản",
                "aesthetic_vi": "Nét vẽ tay marker đen dứt khoát trên bảng trắng (#FFFFFF); hình hũ tiết kiệm, quỹ dự phòng liên kết với đường cong lãi kép đang vươn lên bằng các bậc thang đồng xu xanh ngọc lục bảo (#10B981).",
                "reason_vi": "Cực kỳ ngắn gọn, trực diện, xóa tan sự ngần ngại tài chính cho người mới bắt đầu.",
            },
            "style_4": {
                "name_vi": "Blueprint Cơ Chế Chiếc Ví (Mẫu Prussian Blue Của Bạn)",
                "aesthetic_vi": "Sơ đồ mặt cắt kỹ thuật cấu trúc ví tiền và các kênh luân chuyển thu nhập bằng nét chalk CAD trắng trên nền xanh Prussian; tâm điểm hội tụ là đồng xu vàng phát sáng rực rỡ.",
                "reason_vi": "Minh họa tài chính cá nhân như một sơ đồ giải phẫu dòng chảy tiền tệ hoàn chỉnh, logic và đẹp mắt.",
            },
        },
    },
}


def build_catalog():
    spec_files = sorted(SPECS_DIR.glob("*.json"))
    lines = []

    lines.append("# Danh Mục Đối Chiếu Phong Cách Kênh Đối Thủ Thực Tế (18 Kênh Tiếng Anh — 4 Phong Cách / Kênh)\n")
    lines.append("> [!IMPORTANT]")
    lines.append("> **HƯỚNG DẪN DUYỆT & LỰA CHỌN PHONG CÁCH (TIẾNG VIỆT ĐẦY ĐỦ)**:")
    lines.append("> - Bảng danh mục dưới đây đã được **dịch nghĩa và thuyết minh 100% bằng Tiếng Việt** chi tiết từng phong cách để bạn dễ dàng đọc và đánh giá.")
    lines.append("> - Mỗi kênh đều đính kèm **ảnh thumbnail thật tải trực tiếp từ các kênh triệu view thế giới** trong thư viện tham chiếu.")
    lines.append("> - Phong cách **Prussian Blue Editorial Technical Blueprint** (kỹ sư compa vẽ quỹ đạo trắng trên nền xanh đậm Prussian với xe vàng leo dốc) từ ảnh mẫu bạn vừa cung cấp đã được tích hợp thành **Style chuẩn** cho các kênh khoa học, kỹ thuật, tư duy và chiến lược.")
    lines.append("> - Tất cả 4 phong cách trên từng kênh đều có **bối cảnh giàu chi tiết, ánh sáng điện ảnh, chất liệu thật** — loại bỏ triệt để phong cách sticker/người que trên khoảng trắng rỗng cũ.")
    lines.append("> - Bạn chỉ cần duyệt qua các kênh và chốt phong cách bạn thích nhất (Ví dụ: `en-first-principles: Style 1 (Blueprint)`, `en-scale-and-bone: Style 1 (TierZoo RPG)`, v.v.).\n")
    lines.append("---\n")

    for idx, sf in enumerate(spec_files, 1):
        try:
            with open(sf, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        ch_slug = data.get("channel", sf.stem)
        niche_en = data.get("niche", "")
        styles = data.get("styles", {})

        meta = CHANNEL_META_VI.get(ch_slug, {})
        title_vi = meta.get("title_vi", niche_en)
        scene_vi = meta.get("scene_vi", data.get("scene_description", ""))

        lines.append(f"## {idx}. `{ch_slug}` — {title_vi}\n")
        lines.append(f"*(Tên gốc: {niche_en})*\n")
        if scene_vi:
            lines.append(f"**📖 Bối cảnh cảnh mẫu (Ý nghĩa nội dung)**: *{scene_vi}*\n")

        # Competitor images
        c_ref_dir = REFS_DIR / ch_slug
        ref_imgs = []
        if c_ref_dir.is_dir():
            for ext in ("*.webp", "*.jpg", "*.png"):
                ref_imgs.extend(list(c_ref_dir.glob(ext)))

        video_thumbs = [img for img in ref_imgs if not img.name.endswith("_UC.jpg") and "_UC" not in img.stem]
        if not video_thumbs:
            video_thumbs = ref_imgs

        if video_thumbs:
            lines.append("### 📸 Ảnh Thật Tham Chiếu Từ Kênh Đối Thủ (YouTube Thực Tế):\n")
            lines.append("````carousel")
            display_thumbs = video_thumbs[:4]
            for i, img in enumerate(display_thumbs):
                comp_name = img.stem.split("_")[0].capitalize()
                lines.append(f"![Ảnh thật đối thủ: {comp_name}]({img.resolve()})")
                if i < len(display_thumbs) - 1:
                    lines.append("<!-- slide -->")
            lines.append("````\n")

        # Table with Vietnamese descriptions
        lines.append("### 🎨 Bảng Đánh Giá 4 Phong Cách Đề Xuất Dành Riêng Cho Kênh:\n")
        lines.append("| Phong cách | Kênh Đối Thủ Tham Chiếu | Mô Tả Thẩm Mỹ & Màu Sắc (Tiếng Việt) | Lý Do Phù Hợp Với Kênh |")
        lines.append("| :--- | :--- | :--- | :--- |")

        styles_meta = meta.get("styles_vi", {})
        for sk, sdata in styles.items():
            smeta = styles_meta.get(sk, {})
            name_vi = smeta.get("name_vi", sdata.get("style_name", sk))
            comp = sdata.get("competitor", "")
            aesthetic_vi = smeta.get("aesthetic_vi", sdata.get("prompt", "")[:120] + "...")
            reason_vi = smeta.get("reason_vi", sdata.get("reason", "Phù hợp với ngôn ngữ thị giác của ngách"))

            lines.append(f"| **{sk.upper()}**: {name_vi} | **{comp}** | {aesthetic_vi} | *{reason_vi}* |")

        # Detail block with prompt and Vietnamese translation
        lines.append("\n<details>")
        lines.append(f"<summary>🔍 Bấm để xem chi tiết Prompt tiếng Anh & Hướng dẫn kỹ thuật 4 phong cách của kênh {ch_slug}</summary>\n")
        for sk, sdata in styles.items():
            smeta = styles_meta.get(sk, {})
            name_vi = smeta.get("name_vi", sdata.get("style_name", sk))
            prompt_en = sdata.get("prompt", "")
            lines.append(f"#### {sk.upper()}: {name_vi}\n")
            lines.append(f"- **Kênh đối thủ mẫu**: {sdata.get('competitor', '')}")
            lines.append(f"- **Thẩm mỹ chủ đạo**: {smeta.get('aesthetic_vi', '')}")
            lines.append(f"- **Prompt tạo ảnh (Flow CDP SSOT)**:\n```text\n{prompt_en}\n```\n")
        lines.append("</details>\n")
        lines.append("---\n")

    catalog_content = "\n".join(lines)
    CATALOG_FILE.write_text(catalog_content, encoding="utf-8")
    print(f"Successfully generated bilingual master catalog: {len(catalog_content)} chars to {CATALOG_FILE}")


if __name__ == "__main__":
    build_catalog()
