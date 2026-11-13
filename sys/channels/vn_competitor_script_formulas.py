"""Reusable Competitor-Derived Script, Sentence Pairing, Acoustic Pause, and Transition Formulas
for all 20 Vietnamese Video Pilot channels.
"""

from __future__ import annotations

from typing import Any, Dict

VN_COMPETITOR_SCRIPT_FORMULAS: Dict[str, Dict[str, Any]] = {
    # --------------------------------------------------------------------------
    # Tier-A (0-9 views)
    # --------------------------------------------------------------------------
    "tui_tien": {
        "channel_id": "tui_tien",
        "channel_slug": "tui-tien",
        "niche": "Tiền và kinh tế đời sống (Consumer Economics & Behavioral Pricing)",
        "competitor_name": "Two Cents PBS / WSJ Consumer Economics / Tài Chính & Kinh Doanh",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:03.2s] 'Một ly trà sữa 50 nghìn trên tay bạn...' [pause 0.28s] -> "
                "[00:03.5-00:07.8s] 'thực chất chi phí trà, sữa và trân châu chỉ tốn chưa tới 4 nghìn đồng.' [pause 0.42s] -> "
                "[00:08.2-00:13.1s] 'Vậy 46 nghìn còn lại đã biến đi đâu mất?' [pause 0.48s] -> "
                "[00:13.6-00:20.0s] 'Mặt bằng, nhân viên, bao bì... và đặc biệt là phí nhượng quyền thương hiệu âm thầm rút sạch túi tiền của bạn.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức bóc tách dòng tiền 5 bước: (1) Nêu món đồ quen thuộc và mức giá niêm yết ('Một ly trà sữa 50 nghìn...') -> "
                "(2) Cú sốc chi phí nguyên liệu thực tế ('thực chất chỉ tốn chưa tới 4 nghìn') -> "
                "(3) Câu hỏi truy vết dòng tiền thất thoát ('Vậy 46 nghìn còn lại biến đi đâu?') -> "
                "(4) Liệt kê chi phí chìm vô hình ('Mặt bằng, thương hiệu, chiết khấu app giao hàng...') -> "
                "(5) Đòn bẩy hành động bảo vệ ví tiền ('Hiểu rõ giá gốc để không bao giờ bị bẫy giá chi phối')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc đĩnh đạc, tính toán nhanh 148 WPM: Micro-pause 0.22s sau mệnh đề giá bán; "
                "beat-pause 0.38s sau khi lật tẩy giá vốn; dramatic-pause 0.45s sau câu hỏi tu từ để người xem giật mình nhẩm lại chi tiêu; "
                "pause 0.30s trước kết luận đòn bẩy tài chính."
            ),
            "transition_and_camera_formula_vi": (
                "Supersampled 2x zoompan mượt mà kết hợp chuyển cảnh xfade 0.28s: smoothright khi lia dọc hóa đơn thanh toán, "
                "smoothleft khi quay lại ví tiền, smoothup khi nâng tầm mắt vào bảng chi phí, và fade mềm khi chuyển bối cảnh studio sản phẩm."
            ),
        },
    },
    "banh_rang": {
        "channel_id": "banh_rang",
        "channel_slug": "banh-rang",
        "niche": "Kinh tế vĩ mô, lạm phát, lãi suất và chuỗi cung ứng toàn cầu (Macroeconomics & Industrial Logistics)",
        "competitor_name": "Practical Engineering / Wendover Productions",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:04.5s] 'Cục Dự trữ Liên bang Mỹ vừa tăng lãi suất thêm 0.25 phần trăm.' [pause 0.32s] -> "
                "[00:04.8-00:09.2s] 'Tưởng chừng xa vời, nhưng đúng ba tháng sau...' [pause 0.38s] -> "
                "[00:09.6-00:14.8s] 'bát phở đầu ngõ nhà bạn âm thầm tăng giá thêm 5 nghìn đồng.' [pause 0.50s] -> "
                "[00:15.3-00:20.0s] 'Bánh răng khổng lồ nào đã truyền lực từ Washington về tận căn bếp Việt?'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức chuỗi truyền động vĩ mô 5 bước: (1) Quyết sách tài chính quốc tế xa xôi ('Fed nâng lãi suất...') -> "
                "(2) Khoảng trễ thời gian phản ứng ('Ba tháng sau...') -> "
                "(3) Tác động trực tiếp đến bữa ăn người xem ('bát phở đầu ngõ tăng giá 5 nghìn') -> "
                "(4) Câu hỏi truy nguyên cơ chế truyền lực ('Bánh răng nào đã truyền động lực này?') -> "
                "(5) Bóc tách mắt xích tỷ giá - nhập khẩu - chi phí đẩy ('Đồng USD mạnh lên đội giá phân bón và xăng dầu')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc đĩnh đạc, khúc chiết, chuẩn mực kỹ sư hạ tầng 144 WPM: Micro-pause 0.22s sau số liệu vĩ mô; "
                "beat-pause 0.38s sau khi nêu tác động vi mô đời thường; dramatic-pause 0.45s sau câu hỏi bánh răng truyền lực; "
                "pause 0.32s giữa các mắt xích nhân quả."
            ),
            "transition_and_camera_formula_vi": (
                "Supersampled 2x zoompan không giật kết hợp xfade 0.28s: smoothleft lia dọc dây chuyền container cảng biển, "
                "smoothup theo tháp cẩu gantry, smoothdown khi hạ thấp xuống mặt đường dân sinh, và fade mềm chuyển đổi giữa bản đồ chuỗi cung ứng và hiện trường."
            ),
        },
    },
    "luat_doi_thuong": {
        "channel_id": "luat_doi_thuong",
        "channel_slug": "luat-doi-thuong",
        "niche": "Pháp lý dân sự bình dân: hợp đồng, thuê nhà, lao động, vay mượn (Civil Law & Consumer Contracts)",
        "competitor_name": "LegalEagle / CNBC Make It / Luật Sư X",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:03.8s] 'Ký vào hợp đồng thuê nhà mà không đọc dòng này...' [pause 0.26s] -> "
                "[00:04.1-00:08.5s] 'bạn vừa vô tình tặng trắng hai tháng tiền cọc cho chủ nhà.' [pause 0.40s] -> "
                "[00:08.9-00:13.8s] 'Pháp luật dân sự quy định rất rõ về điều khoản bất khả kháng.' [pause 0.35s] -> "
                "[00:14.2-00:20.0s] 'Nhưng tại sao 90 phần trăm người đi thuê vẫn ngậm đắng nuốt cay chịu mất tiền?'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức giải mã bẫy pháp lý 5 bước: (1) Cảnh báo hành vi ký kết chủ quan ('Ký mà không đọc kỹ...') -> "
                "(2) Hậu quả thiệt hại tài chính nhãn tiền ('mất trắng tiền cọc') -> "
                "(3) Viện dẫn căn cứ pháp lý bảo vệ ('Điều luật quy định rõ...') -> "
                "(4) Câu hỏi lật tẩy bẫy chữ nghĩa ('Tại sao người thuê vẫn chịu thiệt?') -> "
                "(5) Thao tác hợp đồng thực chiến để tự bảo vệ ('Thêm đúng một câu này trước khi đặt bút ký')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc chắc chắn, đanh thép, tin cậy của luật sư tư vấn 142 WPM: Micro-pause 0.22s sau mệnh đề điều kiện; "
                "beat-pause 0.38s sau khi chỉ rõ thiệt hại; dramatic-pause 0.45s sau câu hỏi tu từ truy vấn trách nhiệm; "
                "pause 0.30s trước điều khoản chốt hạ."
            ),
            "transition_and_camera_formula_vi": (
                "Zoompan mượt mà kết hợp xfade 0.28s: smoothdown lia dọc theo trang giấy hợp đồng, "
                "smoothleft/smoothright quét qua dòng chữ được bôi vàng, và fade tĩnh lặng khi chuyển sang góc cận cảnh con dấu sáp và cân công lý."
            ),
        },
    },
    "la_ban_hoc_thuat": {
        "channel_id": "la_ban_hoc_thuat",
        "channel_slug": "la-ban-hoc-thuat",
        "niche": "Phương pháp tự học sâu, tư duy phản biện & nghiên cứu khoa học (Deep Learning & Critical Research)",
        "competitor_name": "Veritasium / 3Blue1Brown / Spiderum",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:04.0s] 'Bạn đọc một cuốn sách ba trăm trang trong hai ngày...' [pause 0.25s] -> "
                "[00:04.3-00:08.6s] 'nhưng một tuần sau, bạn hầu như không nhớ được ý cốt lõi nào.' [pause 0.42s] -> "
                "[00:09.0-00:13.5s] 'Não bộ của bạn không hề bị đãng trí hay kém thông minh.' [pause 0.36s] -> "
                "[00:13.9-00:20.0s] 'Nó chỉ đang từ chối lưu trữ những dữ liệu không được kích hoạt bằng tư duy phản biện.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức phương pháp học sâu 5 bước: (1) Hiện tượng học nhanh quên nhanh ('Đọc hết cuốn sách trong hai ngày...') -> "
                "(2) Nghịch lý trắng tay sau một tuần ('nhưng không nhớ nổi ý cốt lõi') -> "
                "(3) Minh oan cho năng lực não bộ ('Não bạn không hề kém cỏi') -> "
                "(4) Vạch trần cơ chế thụ động ('Nó chỉ từ chối dữ liệu không phản biện') -> "
                "(5) Giao thức tự học Feynman thực chiến ('Giải thích lại vấn đề cho một đứa trẻ 10 tuổi hiểu')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc truyền cảm hứng, khúc chiết, chuẩn mực học giả 143 WPM: Micro-pause 0.22s sau mệnh đề trải nghiệm; "
                "beat-pause 0.38s sau khi chỉ ra sự lãng phí thời gian; dramatic-pause 0.45s sau câu hỏi phá vỡ định kiến tự ti; "
                "pause 0.32s trước nguyên lý Feynman."
            ),
            "transition_and_camera_formula_vi": (
                "Zoompan 2x mượt mà kết hợp xfade 0.28s: smoothleft khi quét qua trang sách dày, "
                "smoothup khi nâng tầm sang sơ đồ tư duy, smoothdown khi chỉ vào trang giấy ghi chú thực hành, và fade nhẹ vào thí nghiệm quang học."
            ),
        },
    },
    "luat_ngam": {
        "channel_id": "luat_ngam",
        "channel_slug": "luat-ngam",
        "niche": "Tâm lý xã hội, hiệu ứng bầy đàn và nghệ thuật đàm phán (Social Psychology & System Dynamics)",
        "competitor_name": "Fern TV / Academy of Ideas / CDTeam",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:04.2s] 'Bước vào một nhà hàng đông nghẹt người xếp hàng...' [pause 0.28s] -> "
                "[00:04.5-00:08.9s] 'não bạn tự động kết luận: đồ ăn ở đây chắc chắn rất ngon.' [pause 0.40s] -> "
                "[00:09.3-00:13.8s] 'Nhưng sự thật là: 30 người đầu tiên xếp hàng...' [pause 0.38s] -> "
                "[00:14.2-00:20.0s] 'chỉ đang nhìn nhau và cùng hành động theo một hiệu ứng bầy đàn vô thức.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức giải mã bẫy tâm lý xã hội 5 bước: (1) Tình huống đời thường kích hoạt phản xạ bầy đàn ('Thấy hàng người xếp hàng dài...') -> "
                "(2) Kết luận vội vã vô thức ('Não tự nhủ nơi này ắt hẳn rất tốt') -> "
                "(3) Lật tẩy sự thật đằng sau đám đông ('30 người đầu chỉ đang nhìn nhau') -> "
                "(4) Câu hỏi bóc tách đòn bẩy thao túng ('Ai đang giật dây những con rối hành vi?') -> "
                "(5) Nguyên tắc đứng ngoài bầy đàn ('Tự hỏi mục tiêu thực sự của mình trước khi bước theo')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc điềm tĩnh, trầm ấm, bí ẩn kiểu phim tài liệu điều tra 140 WPM: Micro-pause 0.22s sau tình huống quan sát; "
                "beat-pause 0.38s sau suy nghĩ ngây thơ; dramatic-pause 0.45s sau đòn lật tẩy đám đông; pause 0.30s trước quy luật ngầm chốt lại."
            ),
            "transition_and_camera_formula_vi": (
                "Zoompan mượt mà không snap 1-frame kết hợp xfade 0.28s: smoothdown từ góc nhìn sa bàn trên cao xuống dòng người, "
                "smoothleft theo bước chân di chuyển, smoothup quét qua hệ thống đèn chiếu, và fade mềm khi chuyển vào căn phòng điều khiển."
            ),
        },
    },

    # --------------------------------------------------------------------------
    # Tier-B (0-7 views)
    # --------------------------------------------------------------------------
    "ua_sao_vay": {
        "channel_id": "ua_sao_vay",
        "channel_slug": "ua-sao-vay",
        "niche": "Sự thật bất ngờ, khoa học gây tò mò & vật lý đời thường (Everyday Curiosities & Cross-Section Physics)",
        "competitor_name": "Veritasium / Zack D. Films",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:03.2s] 'Ủa sao bấm bút bi lại phát ra tiếng cách cách?' [pause 0.22s] -> "
                "[00:03.5-00:07.8s] 'Ẩn bên trong thân nhựa rẻ tiền là một cỗ máy cơ khí thu nhỏ' [pause 0.35s] -> "
                "[00:08.2-00:12.6s] 'với rãnh xoay cam dẫn hướng cực kỳ tinh xảo.' [pause 0.45s] -> "
                "[00:13.1-00:20.0s] 'Nếu không có góc nghiêng 45 độ này, ngòi bút sẽ vĩnh viễn thụt lùi vào trong mỗi khi bạn chạm giấy!'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức tò mò bất ngờ 5 bước: (1) Bật thốt câu hỏi ngớ ngẩn nhưng gây nghiện ('Ủa sao bấm bút lại kêu cách cách?') -> "
                "(2) Phóng to lát cắt cơ học bên trong ('Bên trong là cỗ máy cam thu nhỏ') -> "
                "(3) Bóc tách chi tiết kỹ thuật cốt lõi ('Rãnh xoay định hướng góc 45 độ') -> "
                "(4) Giả định nếu cơ chế biến mất ('Nếu thiếu nó, ngòi bút lập tức thụt lùi') -> "
                "(5) Cảm thán trí tuệ ẩn sau vật phẩm bình dân ('Một phát minh thiên tài trên đầu ngón tay bạn')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc nhanh, dồn dập, tò mò, hào hứng 152 WPM: Micro-pause 0.18s ngay sau câu hỏi 'Ủa sao vậy?'; "
                "beat-pause 0.32s sau khi mở lát cắt 3D; dramatic-pause 0.42s trước khi giải thích hậu quả thiếu cơ chế; "
                "pause 0.25s kết lại cảm giác kinh ngạc."
            ),
            "transition_and_camera_formula_vi": (
                "Zoompan bổ nhào cực nhanh vào mặt cắt cơ khí 3D kết hợp xfade 0.28s: smoothup khi lò xo nén lại, "
                "smoothdown khi ngòi bút nhô ra, smoothright theo rãnh xoay cam, và fade sáng khi hoàn thành chu trình cơ học."
            ),
        },
    },
    "dia_com": {
        "channel_id": "dia_com",
        "channel_slug": "dia-com",
        "niche": "Hóa học ẩm thực, an toàn thực phẩm và nhiệt động học căn bếp (Culinary Chemistry & Food Science)",
        "competitor_name": "America's Test Kitchen / Modernist Cuisine",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:03.6s] 'Tại sao rán thịt bò thì thơm ngào ngạt...' [pause 0.26s] -> "
                "[00:03.9-00:08.2s] 'nhưng nếu đem luộc, mùi vị lại nhạt nhòa đến vậy?' [pause 0.40s] -> "
                "[00:08.6-00:13.5s] 'Bí mật nằm ở phản ứng Maillard chỉ bùng nổ ở nhiệt độ trên 140 độ C.' [pause 0.46s] -> "
                "[00:14.0-00:20.0s] 'Nước sôi chỉ tới 100 độ, khóa chặt hàng trăm phân tử hương thơm không cho bung tỏa.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức hóa học ẩm thực 5 bước: (1) So sánh đối nghịch quen thuộc trong bếp ('Rán thịt thì thơm nức vs luộc thì nhạt nhòa') -> "
                "(2) Đặt câu hỏi truy tìm phản ứng hóa học ('Tại sao nhiệt độ lại quyết định mùi hương?') -> "
                "(3) Hé lộ tên phản ứng và ngưỡng kích hoạt ('Phản ứng Maillard bùng nổ trên 140 độ C') -> "
                "(4) Giải thích lý do thất bại ở phương pháp cũ ('Nước sôi 100 độ kìm hãm phân tử hương') -> "
                "(5) Mẹo nấu ăn khoa học áp dụng ngay ('Thấm khô mặt thịt trước khi áp chảo nóng')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc ấm áp, sinh động, chuẩn mực khoa học đời sống 145 WPM: Micro-pause 0.22s sau mệnh đề so sánh; "
                "beat-pause 0.38s sau khi đặt câu hỏi hương vị; dramatic-pause 0.45s khi nhắc đến phản ứng Maillard; "
                "pause 0.30s trước mẹo vặt căn bếp."
            ),
            "transition_and_camera_formula_vi": (
                "Chuyển động probe lens macro siêu cận cảnh kết hợp xfade 0.28s: smoothright trượt dọc thớ thịt xèo xèo, "
                "smoothup theo làn khói thơm bốc lên, smoothdown vào bề mặt chảo gang, và fade mềm sang cấu trúc phân tử mô phỏng."
            ),
        },
    },
    "vu_tru_ti_hon": {
        "channel_id": "vu_tru_ti_hon",
        "channel_slug": "vu-tru-ti-hon",
        "niche": "Thiên văn học, vật lý lượng tử và không-thời gian (Astrophysics & Deep Space)",
        "competitor_name": "Melodysheep / Astrum",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:04.2s] 'Nếu bạn nén toàn bộ Trái Đất lại bằng kích thước một hạt đậu phộng...' [pause 0.35s] -> "
                "[00:04.6-00:09.5s] 'nó sẽ lập tức sụp đổ thành một lỗ đen thực sự.' [pause 0.48s] -> "
                "[00:10.0-00:14.8s] 'Trọng lực ở bề mặt hạt đậu lúc này mạnh đến mức...' [pause 0.40s] -> "
                "[00:15.2-00:20.0s] 'ngay cả một tia sáng cũng vĩnh viễn không thể nào đào thoát.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức kỳ vĩ vũ trụ 5 bước: (1) Ẩn dụ quy mô choáng ngợp ('Nén Trái Đất bằng hạt đậu...') -> "
                "(2) Bước chuyển pha vật lý kỳ dị ('sụp đổ thành lỗ đen thực sự') -> "
                "(3) Mô tả lực hấp dẫn tột cùng ('Trọng lực bề mặt mạnh đến mức...') -> "
                "(4) Giới hạn vật lý bất khả xâm phạm ('ngay cả ánh sáng cũng bị giam cầm') -> "
                "(5) Bài học chiêm nghiệm về không gian và bản ngã ('Bạn đang đứng trên một hạt bụi lơ lửng giữa hư vô')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc trầm hùng, sâu lắng, đậm chất điện ảnh IMAX 134 WPM: Micro-pause 0.25s sau ẩn dụ hạt đậu; "
                "beat-pause 0.42s sau khi hố đen hình thành; dramatic-pause 0.50s sau ranh giới chân trời sự kiện; "
                "pause 0.35s trước câu kết triết lý không gian."
            ),
            "transition_and_camera_formula_vi": (
                "Supersampled 2x zoompan trôi dạt vũ trụ không trọng lực kết hợp xfade 0.28s: smoothleft trượt theo vành đai bồi tụ rực sáng, "
                "smoothup vút qua bóng tối chân trời sự kiện, smoothdown theo tia plasma năng lượng, và fade hòa tan vào nền trời đêm đen thẳm."
            ),
        },
    },
    "chanh_niem_ke": {
        "channel_id": "chanh_niem_ke",
        "channel_slug": "chanh-niem-ke",
        "niche": "Triết lý Phật giáo ứng dụng, Chánh niệm & nghệ thuật buông bỏ (Applied Mindfulness & Zen Philosophy)",
        "competitor_name": "Pursuit of Wonder / Aperture",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:04.5s] 'Càng cố nắm chặt một nắm cát trong lòng bàn tay...' [pause 0.38s] -> "
                "[00:04.9-00:09.2s] 'từng hạt cát càng len qua kẽ ngón tay rơi xuống đất.' [pause 0.45s] -> "
                "[00:09.7-00:14.6s] 'Tâm trí bạn đối với những muộn phiền cũng hệt như vậy.' [pause 0.40s] -> "
                "[00:15.0-00:20.0s] 'Bình yên không đến khi bạn cố kiểm soát tất cả, mà đến khi bạn học cách mở rộng bàn tay.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức chánh niệm chữa lành 5 bước: (1) Ẩn dụ xúc giác tự nhiên quen thuộc ('Càng nắm chặt cát trong lòng tay...') -> "
                "(2) Quy luật vật lý hiển nhiên ('cát càng lọt qua kẽ tay') -> "
                "(3) So chiếu vào tâm thức con người ('Tâm trí bạn với phiền não cũng thế') -> "
                "(4) Nghịch lý của sự cố chấp ('Càng cố kiểm soát càng kiệt sức') -> "
                "(5) Bài học buông xả thảnh thơi ('Mở rộng bàn tay để đón nhận sự an yên')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc trầm ấm, tĩnh tại, an yên, chữa lành 132 WPM: Micro-pause 0.25s sau mệnh đề hình ảnh; "
                "beat-pause 0.42s sau quy luật cát rơi; dramatic-pause 0.50s sau câu soi chiếu nội tâm; "
                "pause 0.38s trước lời nhắn nhủ buông xả."
            ),
            "transition_and_camera_formula_vi": (
                "Chuyển động anamorphic 35mm tĩnh lặng, chậm rãi kết hợp xfade 0.28s: smoothleft lia dọc hiên chùa mưa bay, "
                "smoothdown nhìn giọt nước đọng trên lá sen, smoothup theo làn khói trầm thanh tịnh, và fade mềm mại vào ánh hoàng hôn ấm áp."
            ),
        },
    },
    "minh_triet_song": {
        "channel_id": "minh_triet_song",
        "channel_slug": "minh-triet-song",
        "niche": "Minh triết Phương Đông & Chủ nghĩa Khắc kỷ (Eastern Philosophy & Stoicism)",
        "competitor_name": "Einzelgänger / Daily Stoic",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:04.0s] 'Người khác đối xử tệ với bạn là bài toán của họ...' [pause 0.30s] -> "
                "[00:04.3-00:08.8s] 'nhưng bạn phản ứng lại ra sao lại là tư cách của bạn.' [pause 0.45s] -> "
                "[00:09.3-00:14.2s] 'Marcus Aurelius từng nhắc nhở chính mình mỗi sớm mai:' [pause 0.38s] -> "
                "[00:14.6-00:20.0s] 'Đừng bao giờ lãng phí một giây giận dữ với những thứ nằm ngoài tầm kiểm soát của bạn.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức khắc kỷ bản lĩnh 5 bước: (1) Phân định ranh giới trách nhiệm người khác ('Họ tệ bạc là chuyện của họ...') -> "
                "(2) Xác lập chủ quyền phản ứng của bản thân ('cách bạn đáp lại là tư cách của bạn') -> "
                "(3) Viện dẫn trí tuệ triết gia cổ đại ('Marcus Aurelius tự dặn lòng...') -> "
                "(4) Nguyên tắc vòng tròn kiểm soát ('Không lãng phí năng lượng vào điều bất khả kháng') -> "
                "(5) Lời hiệu triệu giữ tâm bất biến ('Giữ vững nội lực như bức tường đá trước sóng biển')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc đĩnh đạc, dứt khoát, điềm tĩnh, đầy nội lực 138 WPM: Micro-pause 0.22s sau mệnh đề tha nhân; "
                "beat-pause 0.40s sau khẳng định tư cách; dramatic-pause 0.45s khi nêu danh triết gia; "
                "pause 0.32s trước nguyên tắc hành động."
            ),
            "transition_and_camera_formula_vi": (
                "Supersampled 2x zoompan phong cách chiaroscuro uy nghiêm kết hợp xfade 0.28s: push_in vào gương mặt tượng đá La Mã, "
                "smoothleft lướt qua rặng thông gió núi, smoothdown theo vết khắc trên phiến đá, và fade đĩnh đạc vào ánh bình minh."
            ),
        },
    },

    # --------------------------------------------------------------------------
    # Tier-C (High-Short / Low-Long Documentary)
    # --------------------------------------------------------------------------
    "co_the_ke": {
        "channel_id": "co_the_ke",
        "channel_slug": "co-the-ke",
        "niche": "Sức khỏe, tế bào sinh học và giải phẫu 3D (Human Physiology & Medical 3D)",
        "competitor_name": "Nucleus Medical Media / Zack D. Films",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:03.5s] 'Mỗi đêm khi bạn chìm vào giấc ngủ say...' [pause 0.25s] -> "
                "[00:03.8-00:08.2s] 'hàng triệu tế bào thần kinh đệm bắt đầu mở van xả lũ.' [pause 0.40s] -> "
                "[00:08.6-00:13.5s] 'Chúng bơm dịch não tủy rửa trôi các mảng bám độc hại' [pause 0.35s] -> "
                "[00:13.9-00:20.0s] 'được tích tụ suốt mười sáu tiếng làm việc căng thẳng trong ngày của bạn.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức nhân hóa giải phẫu 5 bước: (1) Thời điểm cơ thể chuyển trạng thái ('Khi bạn ngủ say...') -> "
                "(2) Hoạt động âm thầm của đội ngũ tế bào ('tế bào thần kinh mở van xả lũ') -> "
                "(3) Nhiệm vụ sinh học sống còn ('Bơm dịch não tủy quét sạch mảng độc') -> "
                "(4) Cảnh báo hậu quả nếu gián đoạn ('Thức khuya khiến rác độc tích tụ gây suy giảm trí nhớ') -> "
                "(5) Lời khuyên yêu thương cơ thể ('Hãy đi ngủ đúng giờ để não bộ được dọn rác')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc sinh động, khoa học, gần gũi, ấm áp 142 WPM: Micro-pause 0.22s sau mệnh đề đêm khuya; "
                "beat-pause 0.38s sau khi kích hoạt van xả lũ; dramatic-pause 0.42s sau khi nêu mảng bám độc hại; "
                "pause 0.30s trước lời dặn bảo vệ sức khỏe."
            ),
            "transition_and_camera_formula_vi": (
                "Camera nội soi 3D trôi bồng bềnh trong khoang tế bào kết hợp xfade 0.28s: smoothright theo dòng chảy dịch não tủy, "
                "smoothdown khi lọt qua khe mao mạch, smoothup hướng về tế bào nơ-ron, và fade mềm mại sang nhịp thở êm đềm."
            ),
        },
    },
    "su_ke_lai": {
        "channel_id": "su_ke_lai",
        "channel_slug": "su-ke-lai",
        "niche": "Lịch sử Việt Nam và thế giới qua góc nhìn điện ảnh sử thi 35mm (35mm Historical Live-Action Docudrama)",
        "competitor_name": "Kingdom of Heaven / Ridley Scott Historical Cinema / Epic History Docudrama",
        "voice": "VietNarrator",
        "voice_id": "VietNarrator_su_ke_lai",
        "fast_cutting_visual_sub_beat_rule": {
            "core_zero_filler_sentences": 120,
            "visual_sub_beats_per_sentence": 2,
            "total_visual_beats": 240,
            "target_duration_range": "~9m15s-9m45s",
            "avg_seconds_per_image": 2.35,
            "rule_vi": (
                "Nhịp cắt dựng nhanh V3: 120 câu cốt lõi không chữ thừa (zero-filler) x 2 sub-beat hình ảnh/câu "
                "= 240 visual beats trong ~9m15s-9m45s, trung bình ~2.35s/ảnh."
            ),
        },
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:04.2s] 'Năm 938, trước hàng trăm chiến thuyền Nam Hán hung hãn...' [pause 0.35s] -> "
                "[00:04.6-00:09.5s] 'Ngô Quyền không hề đem quân ra nghênh chiến trực diện.' [pause 0.45s] -> "
                "[00:10.0-00:14.5s] 'Ông kiên nhẫn chờ đợi con nước thủy triều sông Bạch Đằng rút xuống...' [pause 0.38s] -> "
                "[00:14.9-00:20.0s] 'để bãi cọc nhọn bọc sắt dưới đáy sông làm nhiệm vụ lịch sử của chúng.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức kịch tính lịch sử 5 bước (120 câu zero-filler x 2 visual sub-beats = 240 beats over ~9m15s-9m45s, avg ~2.35s/image): "
                "(1) Mốc thời gian và tương quan lực lượng áp đảo ('Năm 938, hạm đội giặc hung hãn...') -> "
                "(2) Quyết định chiến thuật bất ngờ ('Ngô Quyền không đối đầu trực diện') -> "
                "(3) Yếu tố thiên thời địa lợi ('Kiên nhẫn chờ nước thủy triều rút') -> "
                "(4) Đòn phục kích chí mạng ('Bãi cọc sắt nhô lên khóa chặt chiến thuyền') -> "
                "(5) Ý nghĩa bước ngoặt độc lập ngàn năm ('Mở ra kỷ nguyên tự chủ muôn đời cho non sông')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc hào hùng, điện ảnh, trầm bổng kịch tính khóa V3 (VietNarrator_su_ke_lai) tốc độ hiệu dụng 1.30x "
                "(1.12x base OmniVoice synthesis + atempo=1.161 WSOLA + 0.06s inter-beat gap), "
                "Studio Presence EQ (highpass=f=80,equalizer=f=180:t=q:w=1.1:g=1.2,equalizer=f=3200:t=q:w=1.0:g=2.2,"
                "equalizer=f=6500:t=q:w=1.2:g=1.5,lowpass=f=15000), master -11.0 LUFS / -1.0 dBTP: "
                "120 câu cốt lõi zero-filler x 2 visual sub-beats = 240 visual beats trong ~9m15s-9m45s (trung bình ~2.35s/ảnh)."
            ),
            "transition_and_camera_formula_vi": (
                "Hệ hình ảnh 35mm Historical Live-Action Docudrama khóa V3 (su_ke_lai_35mm_live_action_v3) "
                "xuất 2K 2560x1440@30fps static Lanczos kết hợp xfade=fade:duration=0.24: 120 câu x 2 sub-beat hình ảnh "
                "(240 beats, ~2.35s/ảnh), quay phim 35mm Kodak Vision3 500T ánh đuốc chiaroscuro, giáp vảy Đại Việt & Tống, bùn ẩm và sương sông."
            ),
        },
    },
    "ho_so_ky_la": {
        "channel_id": "ho_so_ky_la",
        "channel_slug": "ho-so-ky-la",
        "niche": "Bí ẩn, hồ sơ kỳ lạ và giám định pháp y (Forensic Mysteries & Unsolved Archives)",
        "competitor_name": "LEMMiNO / Fern",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:03.8s] 'Tại căn phòng khóa trái cửa từ bên trong...' [pause 0.30s] -> "
                "[00:04.1-00:08.5s] 'toàn bộ đồ đạc quý giá vẫn còn nguyên vẹn trên bàn.' [pause 0.42s] -> "
                "[00:08.9-00:13.6s] 'Chỉ có một điều duy nhất biến mất không dấu vết:' [pause 0.50s] -> "
                "[00:14.1-00:20.0s] 'chính là người đàn ông vừa bước vào phòng mười phút trước đó.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức hồ sơ trinh thám noir 5 bước: (1) Thiết lập hiện trường kín kỳ lạ ('Căn phòng khóa trái từ bên trong...') -> "
                "(2) Chi tiết loại trừ giả thuyết thông thường ('Đồ đạc nguyên vẹn không dấu hiệu trộm cắp') -> "
                "(3) Điểm bất thường cốt lõi ('Chỉ có một điều duy nhất biến mất') -> "
                "(4) Cú sốc nạn nhân bốc hơi ('Người đàn ông biến mất không tăm tích') -> "
                "(5) Mở tập hồ sơ giải mã từng manh mối ('Sau đây là những sự thật bị che giấu suốt 30 năm')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc lạnh lùng, hồi hộp, chậm rãi, cuốn hút 134 WPM: Micro-pause 0.25s sau bối cảnh phòng kín; "
                "beat-pause 0.42s sau chi tiết đồ vật; dramatic-pause 0.52s trước nút thắt nạn nhân biến mất; "
                "pause 0.35s trước khi lật mở hồ sơ bằng chứng."
            ),
            "transition_and_camera_formula_vi": (
                "Chuyển động máy quay noir chậm rãi trong ánh sáng mờ kết hợp xfade 0.28s: smoothdown lia từ trần nhà xuống ổ khóa bên trong, "
                "smoothleft quét qua sợi dây bằng chứng màu đỏ, smoothright bám theo dấu vân tay, và fade tối vào màn sương bí ẩn."
            ),
        },
    },
    "ban_do_quyen_luc": {
        "channel_id": "ban_do_quyen_luc",
        "channel_slug": "ban-do-quyen-luc",
        "niche": "Địa chính trị, kinh tế tài nguyên và hải trình chiến lược (Geopolitics & Strategic Chokepoints)",
        "competitor_name": "RealLifeLore / Johnny Harris",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:04.2s] 'Eo biển Malacca chỉ hẹp vỏn vẹn một phẩy năm hải lý...' [pause 0.28s] -> "
                "[00:04.5-00:09.2s] 'nhưng là yết hầu lưu chuyển một phần tư lượng dầu mỏ toàn cầu.' [pause 0.45s] -> "
                "[00:09.7-00:14.5s] 'Chỉ cần một sự cố làm tắc nghẽn khe hẹp này...' [pause 0.38s] -> "
                "[00:14.9-00:20.0s] 'nền kinh tế của hàng chục siêu cường sẽ lập tức rơi vào khủng hoảng năng lượng.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức địa chính trị yết hầu 5 bước: (1) Kích thước địa lý nhỏ bé bất ngờ ('Eo biển chỉ hẹp 1.5 hải lý...') -> "
                "(2) Tỷ trọng tài nguyên vận chuyển khổng lồ ('gánh một phần tư lượng dầu toàn cầu') -> "
                "(3) Rủi ro tắc nghẽn dây chuyền ('Chỉ cần một sự cố làm nghẽn dòng chảy') -> "
                "(4) Hệ lụy khủng hoảng toàn cầu ('Kinh tế các siêu cường lập tức ngưng trệ') -> "
                "(5) Kết luận quy luật quyền lực địa lý ('Ai nắm giữ điểm nghẽn, người đó nắm quyền điều phối thế giới')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc khẩn trương, chiến lược, tầm nhìn bao quát 148 WPM: Micro-pause 0.22s sau số liệu hải lý; "
                "beat-pause 0.38s sau tỷ trọng dầu mỏ; dramatic-pause 0.45s khi đặt tình huống tắc nghẽn; "
                "pause 0.30s trước kết luận đòn bẩy địa chính trị."
            ),
            "transition_and_camera_formula_vi": (
                "Supersampled 2x zoompan từ vệ tinh quỹ đạo lao xuống eo biển kết hợp xfade 0.28s: smoothright quét theo luồng hàng hải rực sáng, "
                "smoothup nhìn bao quát toàn bộ bán đảo, smoothdown bám sát đoàn tàu chở dầu, và fade sắc nét vào bản đồ tài nguyên."
            ),
        },
    },
    "loi_sang_soi": {
        "channel_id": "loi_sang_soi",
        "channel_slug": "loi-sang-soi",
        "niche": "Dụ ngôn Kinh Thánh, lịch sử văn minh & bài học nhân văn (Biblical Parables & Classical Civilization)",
        "competitor_name": "BibleProject / Caravaggio Chiaroscuro",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:04.0s] 'Người con thứ gom hết gia tài rồi rời bỏ quê hương...' [pause 0.30s] -> "
                "[00:04.3-00:08.6s] 'để rồi khi trắng tay, anh ta chỉ ước được làm người làm công của cha.' [pause 0.45s] -> "
                "[00:09.1-00:14.0s] 'Nhưng khi từ đằng xa thấy bóng con trở về...' [pause 0.40s] -> "
                "[00:14.4-00:20.0s] 'người cha già không một lời trách móc, mà dang rộng đôi tay ôm lấy đứa con lưu lạc.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức dụ ngôn nhân văn 5 bước: (1) Hành vi lầm lỡ và sa ngã ('Người con gom hết gia tài rời đi...') -> "
                "(2) Hậu quả tận cùng và sự hối hận ('trắng tay chỉ ước làm người làm công') -> "
                "(3) Khoảnh khắc tương phùng xúc động ('Thấy bóng con từ đằng xa...') -> "
                "(4) Phá vỡ phản xạ trừng phạt thông thường ('Không một lời quở trách, dang tay ôm chặt') -> "
                "(5) Đúc kết bài học tha thứ và ánh sáng hy vọng ('Tình yêu thương đích thực luôn lớn hơn mọi lỗi lầm')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc ấm áp, truyền cảm, lắng đọng, bao dung 135 WPM: Micro-pause 0.25s sau hành động ra đi; "
                "beat-pause 0.40s sau nỗi ân hận trắng tay; dramatic-pause 0.48s trước cái ôm của người cha; "
                "pause 0.35s để bài học yêu thương thấm sâu vào tâm hồn."
            ),
            "transition_and_camera_formula_vi": (
                "Chuyển động máy quay chiaroscuro ngập tràn ánh sáng vàng hổ phách kết hợp xfade 0.28s: smoothleft lia dọc con đường làng cổ xưa, "
                "smoothdown nhìn đôi bàn chân lấm bụi, smoothup hướng lên vòm trời chiều ấm áp, và fade trang trọng vào bức họa sơn dầu cổ điển."
            ),
        },
    },

    # --------------------------------------------------------------------------
    # Tier-D (Psychology, Career, AI, Night Fables)
    # --------------------------------------------------------------------------
    "nao_luoi": {
        "channel_id": "nao_luoi",
        "channel_slug": "nao-luoi",
        "niche": "Khoa học thần kinh về Dopamine, thói quen & sự tập trung (Neuroscience of Habits & Dopamine)",
        "competitor_name": "Kurzgesagt Habit Science / Huberman Lab / The Paint Explainer",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:03.2s] 'Bạn nghĩ rằng mình lười biếng và thiếu ý chí?' [pause 0.25s] -> "
                "[00:03.5-00:08.0s] 'Thực chất não bạn chỉ đang thực thi đúng cơ chế hóa sinh:' [pause 0.38s] -> "
                "[00:08.4-00:13.2s] 'mỗi lần lướt video ngắn, một lượng dopamine rẻ tiền được bơm xối xả.' [pause 0.45s] -> "
                "[00:13.7-00:20.0s] 'Các thụ thể bị bão hòa, khiến việc đọc sách hay học tập bỗng trở nên nhàm chán đến cùng cực.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức thần kinh học thói quen Huberman 5 bước: (1) Xóa bỏ mặc cảm tự trách bản thân ('Bạn tưởng mình lười biếng thiếu ý chí?') -> "
                "(2) Quy chuẩn hóa cơ chế hóa sinh thần kinh ('Não chỉ đang vận hành phản xạ thụ thể') -> "
                "(3) Tác nhân dopamine giá rẻ ('Lướt video ngắn kích hoạt dopamine ồ ạt') -> "
                "(4) Hậu quả chai lì ngưỡng kích thích ('Thụ thể giảm độ nhạy khiến việc học thành cực hình') -> "
                "(5) Giao thức thiết lập lại mạch tập trung ('Quy tắc 90 giây cai nghiện kích thích để não lấy lại thăng bằng')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc sắc bén, dí dỏm, thông thái, khích lệ 144 WPM: Micro-pause 0.22s sau câu hỏi trúng tim đen; "
                "beat-pause 0.38s sau khi lật ngược nguyên nhân sinh học; dramatic-pause 0.45s sau hiện tượng bão hòa thụ thể; "
                "pause 0.30s trước giải pháp 90 giây."
            ),
            "transition_and_camera_formula_vi": (
                "Supersampled 2x zoompan mượt mà kết hợp xfade 0.28s: smoothup hướng lên thùy trán đang phát sáng, "
                "smoothleft lia dọc đường truyền tín hiệu synap, smoothdown hạ xuống màn hình điện thoại, và fade mềm mại khi chuyển cảnh đời thường."
            ),
        },
    },
    "thuong_cho_kheo": {
        "channel_id": "thuong_cho_kheo",
        "channel_slug": "thuong-cho-kheo",
        "niche": "Tâm lý tình cảm, giao tiếp trắc ẩn & gắn kết con người (Compassionate Relationships & Attachment Psychology)",
        "competitor_name": "The School of Life / Cinema Therapy",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:03.5s] 'Khi người kia bỗng nhiên im lặng và rút lui...' [pause 0.28s] -> "
                "[00:03.8-00:08.5s] 'ta thường nghĩ họ không còn yêu thương hay quan tâm mình nữa.' [pause 0.42s] -> "
                "[00:08.9-00:13.6s] 'Nhưng trong tâm lý học gắn kết, sự im lặng ấy...' [pause 0.38s] -> "
                "[00:14.0-00:20.0s] 'thực chất là tiếng kêu cứu của một hệ thần kinh đang bị quá tải vì nỗi sợ tổn thương.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức giao tiếp trắc ẩn The School of Life 5 bước: (1) Hiện tượng rạn nứt giao tiếp ('Khi đối phương bỗng dưng im lặng...') -> "
                "(2) Phán đoán sai lầm bản năng ('Ta nghĩ họ đã hết yêu mình') -> "
                "(3) Bóc tách cơ chế phòng vệ tâm lý ('Thực chất là phản xạ rút lui vì sợ tổn thương') -> "
                "(4) Lời giải thích dưới góc nhìn gắn kết ('Hệ thần kinh đang quá tải vì sợ bị từ chối') -> "
                "(5) Cầu nối hàn gắn bằng sự an toàn ('Thay vì tra vấn, hãy tạo cho họ một khoảng lặng bình yên')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc thủ thỉ, ấm áp, đồng cảm sâu sắc 136 WPM: Micro-pause 0.22s sau hiện tượng im lặng; "
                "beat-pause 0.38s sau diễn giải tiêu cực; dramatic-pause 0.48s sau khi lật mở nguyên nhân tổn thương; "
                "pause 0.32s trước giải pháp chữa lành mối quan hệ."
            ),
            "transition_and_camera_formula_vi": (
                "Chuyển động 35mm ấm áp nhẹ nhàng trên nền ánh đèn vàng kết hợp xfade 0.28s: smoothleft đổi góc nhìn giữa hai người ngồi bên bàn trà, "
                "smoothdown nhìn tách trà bốc khói, smoothup nhìn ánh mắt đồng cảm, và fade mềm mại chuyển cảnh."
            ),
        },
    },
    "nghe_song_sot": {
        "channel_id": "nghe_song_sot",
        "channel_slug": "nghe-song-sot",
        "niche": "Chiến lược sự nghiệp, đòn bẩy công sở & thích nghi thời đại AI (Workplace Leverage & Career Strategy)",
        "competitor_name": "Wall Street Journal / Harvard Business Review / Casgains",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:03.5s] 'Chăm chỉ làm việc thêm giờ mỗi ngày...' [pause 0.24s] -> "
                "[00:03.8-00:08.2s] 'chưa bao giờ là chìa khóa giúp bạn thăng tiến hay tăng lương.' [pause 0.40s] -> "
                "[00:08.6-00:13.5s] 'Thước đo duy nhất quyết định mức đãi ngộ của công ty dành cho bạn:' [pause 0.42s] -> "
                "[00:14.0-00:20.0s] 'chính là chi phí và thời gian họ phải bỏ ra để tìm người thay thế bạn.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức đòn bẩy sự nghiệp Wall Street Journal 5 bước: (1) Đập tan ảo tưởng chăm chỉ thụ động ('Làm thêm giờ không giúp bạn tăng lương') -> "
                "(2) Phơi bày sự thật thị trường lao động ('Công ty trả lương theo chi phí thay thế') -> "
                "(3) Định nghĩa đòn bẩy cá nhân cốt lõi ('Trở thành người nắm giữ mắt xích trọng yếu') -> "
                "(4) Câu hỏi chiến lược định vị bản thân ('Nếu bạn nghỉ việc ngày mai, hệ thống có rối loạn?') -> "
                "(5) Kế hoạch xây dựng giá trị độc bản ('Nâng cấp năng lực giải quyết vấn đề phức tạp thay vì bán sức lao động')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc đĩnh đạc, thực chiến, dứt khoát, chuyên nghiệp 146 WPM: Micro-pause 0.20s sau mệnh đề làm thêm giờ; "
                "beat-pause 0.38s sau khi bác bỏ quan niệm cũ; dramatic-pause 0.45s trước khi đưa ra thước đo chi phí thay thế; "
                "pause 0.30s trước lời khuyên hành động."
            ),
            "transition_and_camera_formula_vi": (
                "Supersampled 2x zoompan kiến trúc phòng họp kính hiện đại kết hợp xfade 0.28s: smoothleft lia qua bàn đàm phán, "
                "smoothup nhìn tầm view tòa nhà chọc trời, smoothdown hạ xuống bàn cờ chiến lược, và fade sắc nét vào sơ đồ đòn bẩy."
            ),
        },
    },
    "ai_binh_dan": {
        "channel_id": "ai_binh_dan",
        "channel_slug": "ai-binh-dan",
        "niche": "Công nghệ AI ứng dụng, tự động hóa & năng suất làm việc (Applied AI & Everyday Productivity)",
        "competitor_name": "Jeff Su / Fireship / Matt Wolfe",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:03.2s] 'Bạn đang mất hai tiếng để làm báo cáo này mỗi tuần?' [pause 0.22s] -> "
                "[00:03.5-00:07.8s] 'Chỉ với một câu lệnh gồm ba thành phần chuẩn chỉnh...' [pause 0.35s] -> "
                "[00:08.2-00:13.0s] 'AI sẽ hoàn thành toàn bộ bảng số liệu sạch đẹp trong đúng bốn mươi giây.' [pause 0.45s] -> "
                "[00:13.5-00:20.0s] 'Không cần học lập trình phức tạp, đây là công thức copy dùng ngay cho dân văn phòng.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức năng suất AI thực chiến 5 bước: (1) Nêu nỗi đau tốn thời gian quen thuộc ('Mất 2 tiếng làm báo cáo tuần...') -> "
                "(2) Giải pháp đòn bẩy tức thì ('Một câu lệnh chuẩn chỉnh 3 phần') -> "
                "(3) Kết quả choáng ngợp với số liệu đo lường ('Xong toàn bộ bảng biểu trong 40 giây') -> "
                "(4) Phá bỏ rào cản kỹ thuật ('Không cần biết code cao siêu') -> "
                "(5) Lời kêu gọi hành động mì ăn liền ('Lưu lại công thức để áp dụng ngay ngày mai')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc hào hứng, nhanh nhẹn, rõ ràng, thực dụng 150 WPM: Micro-pause 0.18s sau câu hỏi thời gian lãng phí; "
                "beat-pause 0.32s sau khi nêu đòn bẩy câu lệnh; dramatic-pause 0.42s sau kết quả 40 giây; "
                "pause 0.25s trước lời tặng công thức thực chiến."
            ),
            "transition_and_camera_formula_vi": (
                "Zoompan mượt mà trên giao diện dark-mode và bàn phím cơ kết hợp xfade 0.28s: smoothright trượt dọc câu prompt mẫu, "
                "smoothup nhìn bảng kết quả phân tích tự động, smoothdown lia tay gõ phím, và fade sáng sang bảng tóm tắt 3 bước."
            ),
        },
    },
    "tam_tinh_dem": {
        "channel_id": "tam_tinh_dem",
        "channel_slug": "tam-tinh-dem",
        "niche": "Truyện ngụ ngôn tĩnh thức, nhân quả & chiêm nghiệm chữa lành (Nocturnal Mindfulness & Soul-Healing Fables)",
        "competitor_name": "Pursuit of Wonder / Studio Ghibli Nocturnal",
        "voice": "VietNarrator",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": (
                "[00:00-00:04.2s] 'Đêm đã khuya, hãy gác lại mọi lo toan ngoài ngưỡng cửa...' [pause 0.35s] -> "
                "[00:04.6-00:09.5s] 'Ngày hôm nay bạn đã cố gắng hết sức mình rồi.' [pause 0.48s] -> "
                "[00:10.0-00:14.6s] 'Như dòng sông sau một ngày chảy xiết qua ghềnh đá...' [pause 0.40s] -> "
                "[00:15.0-00:20.0s] 'giờ đây nó tìm về với biển hồ tĩnh lặng, để mặt nước phẳng lặng soi bóng những vì sao.'"
            ),
            "sentence_structure_formula_vi": (
                "Công thức ngụ ngôn đêm vỗ về 5 bước: (1) Lời nhắn nhủ buông bỏ áp lực ngày dài ('Đêm đã khuya, hãy gác lại âu lo...') -> "
                "(2) Sự công nhận và an ủi nỗ lực ('Bạn đã cố gắng hết sức hôm nay rồi') -> "
                "(3) Ẩn dụ thiên nhiên vỗ về ('Như dòng sông sau ghềnh đá tìm về biển hồ') -> "
                "(4) Hình ảnh mặt nước phẳng lặng soi bóng sao ('Lắng đọng tâm trí để thấy bình an') -> "
                "(5) Lời chúc giấc ngủ tròn đầy hy vọng ('Nhắm mắt lại, ngày mai sẽ là một khởi đầu dịu dàng')."
            ),
            "pause_and_cadence_formula_vi": (
                "Nhịp đọc thủ thỉ, êm dịu, ấm áp, ru êm giấc ngủ 128 WPM: Micro-pause 0.28s sau lời gọi đêm khuya; "
                "beat-pause 0.45s sau lời vỗ về nỗ lực; dramatic-pause 0.52s sau ẩn dụ dòng sông; "
                "pause 0.40s dẫn vào giấc ngủ bình yên."
            ),
            "transition_and_camera_formula_vi": (
                "Chuyển động máy quay bồng bềnh không trọng lực giữa đêm sao Studio Ghibli kết hợp xfade 0.28s: smoothleft trượt trên mặt hồ lấp lánh ánh trăng, "
                "smoothdown nhìn ánh đèn lồng vàng ấm, smoothup hướng về bầu trời sao thênh thang, và fade dần vào màn đêm êm ái."
            ),
        },
    },
}


def get_vn_competitor_script_formula(channel_id_or_slug: str) -> Dict[str, Any]:
    """Retrieve competitor script formula for a Vietnamese channel.

    Supports both underscore (`tui_tien`) and hyphen (`tui-tien`) lookup keys.
    """
    key = channel_id_or_slug.strip().lower()
    underscore_key = key.replace("-", "_")
    hyphen_key = key.replace("_", "-")

    if underscore_key in VN_COMPETITOR_SCRIPT_FORMULAS:
        return VN_COMPETITOR_SCRIPT_FORMULAS[underscore_key]

    for formula in VN_COMPETITOR_SCRIPT_FORMULAS.values():
        if formula.get("channel_slug") == hyphen_key or formula.get("channel_id") == underscore_key:
            return formula

    return VN_COMPETITOR_SCRIPT_FORMULAS["tui_tien"]


__all__ = [
    "VN_COMPETITOR_SCRIPT_FORMULAS",
    "get_vn_competitor_script_formula",
]
