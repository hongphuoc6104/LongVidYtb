"""Reusable Competitor-Derived Script, Sentence Pairing, Acoustic Pause, and Transition Formulas
for all 18 English Video Pilot channels.
"""

from __future__ import annotations

from typing import Any, Dict

EN_COMPETITOR_SCRIPT_FORMULAS: Dict[str, Dict[str, Any]] = {
    "en-first-principles": {
        "channel_slug": "en-first-principles",
        "niche": "Mô hình tư duy & Nghịch lý Vật lý (Mental Models & Physics Paradoxes)",
        "competitor_name": "Veritasium",
        "voice": "en-US-ChristopherNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00-00:04.8s] 'If I apply a force down on this side of the wheel, I create a torque.' [pause 0.45s] -> [00:05.3-00:10.2s] 'Now torque is force times the distance from the rotating axis, you could call it r.' [pause 0.40s] -> [00:10.6-00:15.0s] 'So torque is the force applied times the radius away from the turning axis.' [pause 0.60s] -> [00:15.6-00:17.4s] 'Now what's the direction of that torque?' [pause 0.44s] -> [00:17.8-00:20.0s] 'Well, we actually use a right-hand rule to define this.'",
            "sentence_structure_formula_vi": "Công thức 5 bước Veritasium: (1) Mệnh đề điều kiện thực nghiệm ('Hang a heavy spinning wheel...') -> (2) Phá vỡ trực giác thông thường ('Instead of crashing down, it floats...') -> (3) Câu hỏi tu từ ngắn 5-7 chữ ('Now, why doesn't it fall?') -> (4) Giải nghĩa nhân quả bằng từ chỉ hướng ('Because downward gravity pulls the axle...') -> (5) Quy luật tỷ lệ & kết cục tất yếu ('The faster it spins... until friction wins').",
            "pause_and_cadence_formula_vi": "Nhịp đọc 145 WPM có biến thiên: Nghỉ ngắn 0.22s (micro-pause) sau mệnh đề điều kiện; nghỉ 0.42s (beat-pause) sau câu nghịch lý và sau câu hỏi tu từ để người xem kịp tự hỏi; nghỉ 0.32s giữa các mệnh đề giải thích cơ chế.",
            "transition_and_camera_formula_vi": "Supersampled 2x zoompan không giật (loại bỏ hoàn toàn snap 1-frame của zoom_out), kết hợp chuyển cảnh xfade mượt 0.28s: smoothleft khi lia ngang theo trục, smoothup/smoothdown khi theo phương trọng lực, và fade/dissolve mềm khi đổi góc cận cảnh ổ bi.",
        },
    },
    "en-scale-and-bone": {
        "channel_slug": "en-scale-and-bone",
        "niche": "Động vật học & Tiến hóa Vòng đời (Zoology & Animal Life-Cycle Evolution)",
        "competitor_name": "BBC Earth / PBS Eons",
        "voice": "en-GB-RyanNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00.0-00:05.5s] [Subtle alpine wind whistling over rugged mountain peaks] -> [00:05.5-00:13.3s] 'Meadows that only a few weeks ago were buried beneath the snow are now full of life.' [pause 0.40s] -> [00:13.9-00:20.0s] [Cinematic orchestral swell with rapid wing-hum of feeding pollinator]",
            "sentence_structure_formula_vi": "Công thức phim tài liệu động vật hoang dã BBC Earth: (1) Khởi sinh mỏng manh từ tự nhiên ('High on an alpine ridge, an egg cracks...') -> (2) Bước vào thế giới khốc liệt ('a fragile chick enters a brutal world') -> (3) Nuôi dưỡng bản năng săn mồi ('Fed on fresh prey by its mother...') -> (4) Câu hỏi tu từ về bản lĩnh sống còn ('how does this tiny fledgling survive here?') -> (5) Thử thách đôi cánh non ('It exercises growing wings against the gale...') -> (6) Rèn giũa móng vuốt sắc nhọn ('diving clumsily to strike its first target') -> (7) Đôi cánh trưởng thành đón luồng nhiệt đối lưu ('Soon, massive two-meter wings catch the thermal...') -> (8) Đăng quang chúa tể bầu trời ('and an apex hunter rules alpine skies').",
            "pause_and_cadence_formula_vi": "Nhịp đọc tài liệu tự nhiên BBC kinh điển ~135 WPM: Nghỉ ngắn 0.22s sau mệnh đề định vị tổ đại bàng; beat-pause 0.38s sau khi chim non chào đời; dramatic-pause 0.45s sau câu hỏi tu từ để người xem cảm nhận sự khắc nghiệt của thiên nhiên; pause 0.30s trước câu kết đỉnh cao của kẻ săn mồi tối thượng.",
            "transition_and_camera_formula_vi": "Chuyển động máy quay telephoto và flycam mượt mà (push_in, pan_right, tilt_down, zoom_out) kết hợp hiệu ứng xfade 0.28s (smoothleft khi lia theo sườn núi, smoothup/smoothdown theo đường bay chao liệng, và fade nhẹ khi chuyển giai đoạn vòng đời).",
        },
    },
    "en-pocket-cosmos": {
        "channel_slug": "en-pocket-cosmos",
        "niche": "Vật lý Thiên văn & Không gian sâu (Astrophysics & Deep Space)",
        "competitor_name": "Melodysheep / Astrum",
        "voice": "en-US-ChristopherNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00.5-00:03.5s] '...with clouds made of metal.' [pause 0.40s] -> [00:04.5-00:08.5s] 'Zombie worlds, born from the ashes of dead ones.' [pause 0.45s] -> [00:09.5-00:15.5s] 'And hundreds of billions more are waiting for us in our galaxy alone.' [pause 0.50s] -> [00:16.5-00:20.0s] 'These worlds will give us a...'",
            "sentence_structure_formula_vi": "Công thức thiên văn vũ trụ Melodysheep: (1) Mở đầu bằng quy mô vũ trụ kỳ vĩ ('Beyond the quiet edge of our solar cradle...') -> (2) Hiện thực ngoài sức tưởng tượng ('lurk rogue worlds veiled in emerald storms') -> (3) Khổng lồ khí nóng rực ('Colossal sapphire giants orbit blisteringly close—') -> (4) Câu hỏi tu từ về sự sống ('yet could alien life withstand these skies?') -> (5) Vành đai băng thể tích đổ bóng ('Vast iridescent rings cast shadows across magma—') -> (6) Trọng lực kiến tạo mặt trăng ('while gravity sculpts moons from drifting ice') -> (7) Hàng trăm tỷ ẩn số ('Hundreds of billions drift in silence alone—') -> (8) Đích đến của văn minh ('waiting for our eyes to find them').",
            "pause_and_cadence_formula_vi": "Nhịp đọc thiên văn điện ảnh trầm hùng ~132 WPM: Nghỉ 0.22s sau mệnh đề định vị không gian sâu; beat-pause 0.38s sau miêu tả bão ngọc bích; dramatic-pause 0.45s sau câu hỏi tu từ triết học về sự sống; pause 0.30s trước lời mời gọi khám phá tương lai.",
            "transition_and_camera_formula_vi": "Supersampled 2x zoompan mô phỏng camera viễn vọng không gian James Webb bay lượn (push_in, pan_right, zoom_out, tilt_up), kết hợp chuyển cảnh xfade 0.28s (fade, smoothleft, smoothright, smoothup, smoothdown) tạo cảm giác trôi dạt êm ái giữa các vì sao.",
        },
    },
    "en-deep-time-strata": {
        "channel_slug": "en-deep-time-strata",
        "niche": "Địa chất học & Lịch sử Trái Đất cổ đại (Geology & Deep Earth History)",
        "competitor_name": "History of the Earth",
        "voice": "en-GB-RyanNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:07.5-00:11.8s] 'The early Earth, when the atmosphere prevented sunlight from reaching the surface.' [pause 0.50s] -> [00:14.5-00:20.0s] 'Primitive life was about to emerge underground, in the cave of a geyser.'",
            "sentence_structure_formula_vi": "Công thức địa chất cổ sinh History of the Earth: (1) Mở đầu bằng niên đại cổ xưa ('Four billion years ago on primordial Earth—') -> (2) Khung cảnh nguyên thủy khốc liệt ('a boiling magma ocean churned beneath black skies') -> (3) Mưa axit dội xuống vỏ địa chất ('Torrential rains slammed into cooling basalt crust—') -> (4) Câu hỏi tu từ về nguồn cội sự sống ('yet how could living chemistry ignite here?') -> (5) Miệng phun thủy nhiệt bơm khoáng chất ('Deep hydrothermal vents pumped scalding minerals—') -> (6) Tia sét núi lửa kích hoạt mã hữu cơ ('as volcanic lightning sparked organic molecules into motion') -> (7) Cố định trong vi bọt đá bazan ('Trapped within microscopic porous stone chambers—') -> (8) Khởi sinh mầm sống đầu tiên ('the first spark of life was born').",
            "pause_and_cadence_formula_vi": "Nhịp đọc trầm hùng, cổ kính ~130 WPM: Nghỉ 0.22s sau mốc thời gian 4 tỷ năm; beat-pause 0.38s sau miêu tả biển nham thạch; dramatic-pause 0.45s sau câu hỏi tu từ mở ra bí ẩn sự sống nguyên thủy; pause 0.30s trước kết luận đắt giá về nguồn gốc muôn loài.",
            "transition_and_camera_formula_vi": "Chuyển động máy quay mô phỏng flycam khảo sát địa chất (push_in, tilt_down, pan_right, zoom_out) kết hợp chuyển cảnh xfade 0.28s (smoothdown theo dòng dung nham chảy, smoothleft qua rặng núi bazan, fade hòa tan sương khói lưu huỳnh).",
        },
    },
    "en-inside-vessel": {
        "channel_slug": "en-inside-vessel",
        "niche": "Sinh lý học & Giải phẫu Y khoa 3D (Human Physiology & Medical 3D)",
        "competitor_name": "Nucleus Medical Media",
        "voice": "en-US-EricNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00.0-00:06.0s] [Rhythmic pulsating arterial heartbeat with fluid rush] -> [00:06.0-00:12.5s] 'Inside the human vascular stream, millions of erythrocytes surge every second.' [pause 0.35s] -> [00:13.0-00:18.2s] 'They squeeze through microscopic capillaries thinner than a human hair.' [pause 0.40s] -> [00:18.5-00:20.0s] [Fluid swirl into micro-circulation]",
            "sentence_structure_formula_vi": "Công thức giải phẫu y khoa 3D Nucleus Medical: (1) Bước vào không gian nội soi vi mô ('Step inside a living human artery—') -> (2) Dòng chảy tế bào mãnh liệt ('where millions of red cells surge in plasma') -> (3) Vận chuyển dưỡng khí sinh tồn ('Packed with oxygen from the lungs—') -> (4) Câu hỏi tu từ về giới hạn sinh học ('how do they survive such crushing pressure?') -> (5) Cấu trúc cơ học linh hoạt uốn dẻo ('Their flexible biconcave discs bend with ease—') -> (6) Lách qua mao mạch siêu hẹp ('gliding through capillaries narrower than a single hair') -> (7) Nhịp tim 70 lần mỗi phút điều áp ('Driven by seventy rhythmic heartbeats every minute—') -> (8) Động mạch duy trì sự sống ('this silent river keeps you alive').",
            "pause_and_cadence_formula_vi": "Nhịp đọc y khoa khoa học, chuẩn xác ~140 WPM: Nghỉ 0.22s sau lời dẫn nội soi; beat-pause 0.38s sau khi chứng kiến tế bào hồng cầu; dramatic-pause 0.45s sau câu hỏi về cơ chế chịu áp lực vi mô; pause 0.30s trước kết luận đắt giá về dòng chảy duy trì sinh mệnh.",
            "transition_and_camera_formula_vi": "Chuyển động camera nội soi 3D trôi bồng bềnh dọc theo lòng mạch (push_in, pan_left, zoom_out, tilt_up), kết hợp xfade 0.28s (smoothright theo chiều dòng chảy máu, smoothdown khi lọt qua mao mạch, fade mềm qua màng nội mô).",
        },
    },
    "en-macro-gears": {
        "channel_slug": "en-macro-gears",
        "niche": "Kinh tế vĩ mô, Cảng biển & Kỹ thuật Hạ tầng (Macroeconomics & Engineering)",
        "competitor_name": "Practical Engineering / Wendover",
        "voice": "en-US-ChristopherNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00-00:05.5s] '...seventeen-thousand-mile, twenty-seven-thousand-kilometer voyage from America to Asia, and back.' [pause 0.50s] -> [00:06.0-00:13.1s] 'This is, in the context of today's ocean shipping industry, a rather unremarkable journey on a rather unremarkable ship.' [pause 0.94s] -> [00:14.0-00:17.8s] 'Just fifteen years ago though, the Maersk Essex would have been truly extraordinary.' [pause 0.18s] -> [00:18.0-00:20.0s] 'It measures four football fields long.'",
            "sentence_structure_formula_vi": "Công thức 5 bước Wendover / Practical Engineering: (1) Số liệu khoảng cách / quy mô choáng ngợp ('A seventeen-thousand-mile voyage...') -> (2) Đóng khung nghịch lý hiện đại ('is now completely routine...') -> (3) Đòn bẩy đối chiếu lịch sử / kỳ tích kỹ thuật ('Yet this massive container ship was once deemed impossible...') -> (4) Mô tả kích thước và tải trọng vật lý ('Stretching four football fields long, she carries...') -> (5) Kết luận mang tính hệ thống hạ tầng vĩ mô ('anchoring the fragile gears of global trade').",
            "pause_and_cadence_formula_vi": "Nhịp đọc trầm ấm đĩnh đạc ~145 WPM: Nghỉ ngắn 0.22s sau mệnh đề quy mô; nghỉ 0.38s sau khi hạ thấp tính chất sự việc ('routine'); nghỉ 0.42s trước khi đưa ra kích thước khổng lồ; nghỉ 0.25-0.35s giữa các chi tiết máy và kết cấu.",
            "transition_and_camera_formula_vi": "Chuyển động zoompan mượt mà không snap 1-frame; chuyển cảnh xfade 0.28s: fade khi chuyển từ vi mô sang vĩ mô, smoothleft/smoothright khi quét theo chiều dài thân tàu, smoothup/smoothdown khi lia cần cẩu gantry và cống đập.",
        },
    },
    "en-fine-print": {
        "channel_slug": "en-fine-print",
        "niche": "Luật Tiêu dùng & Điều khoản Hợp đồng ẩn (Consumer Law & Hidden Contracts)",
        "competitor_name": "CNBC Make It / LegalEagle",
        "voice": "en-US-RogerNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00-00:03.5s] '...hundred dollar a year service, because that's the value of the data you're providing.' [pause 0.16s] -> [00:03.5-00:09.0s] 'If they use ten percent of that data, they're going to be the most valuable company ever.' [pause 0.41s] -> [00:09.0-00:11.5s] 'It was about taking your information.' [pause 0.15s] -> [00:11.5-00:17.0s] 'Companies that you've never heard of claim to have about fifteen hundred points of data on the average American citizen.' [pause 0.15s] -> [00:17.0-00:20.0s] 'Is it hard to go through it and actually find specific details?'",
            "sentence_structure_formula_vi": "Công thức 5 bước LegalEagle / CNBC: (1) Hành vi tưởng chừng vô hại ('Clicking I Agree seems harmless...') -> (2) Đòn lật tẩy bất ngờ ('until you realize what was signed...') -> (3) Bằng chứng số liệu giám sát quy mô lớn ('Fifteen hundred data points packaged and sold...') -> (4) Câu hỏi tu từ truy vấn trách nhiệm ('Who actually owns that sensitive information?') -> (5) Vạch trần bẫy pháp lý trong điều khoản chi tiết ('Hidden deep inside section fourteen... long before you read the fine print').",
            "pause_and_cadence_formula_vi": "Nhịp đọc đĩnh đạc giọng luật sư điều tra ~142 WPM: Nghỉ ngắn 0.22s sau mệnh đề điều kiện; nghỉ 0.38s sau khi lật tẩy kỳ vọng; nghỉ 0.45s sau câu hỏi tu từ để khán giả tự vấn; nghỉ 0.25-0.35s giữa các điều khoản pháp lý.",
            "transition_and_camera_formula_vi": "Zoompan mượt mà không snap 1-frame; chuyển cảnh xfade 0.28s: fade khi chuyển sang hồ sơ, smoothdown khi quét theo trang giấy in, smoothleft/smoothright khi quét dòng chữ bôi vàng highlighter quang học.",
        },
    },
    "en-crowd-strings": {
        "channel_slug": "en-crowd-strings",
        "niche": "Tâm lý Đám đông & Phóng sự Điều tra 3D (Mass Psychology & 3D Documentary)",
        "competitor_name": "Fern / Academy of Ideas",
        "voice": "en-US-SteffanNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00-00:04.5s] 'Hundreds of thousands of troops would need to reach the front as quickly as possible.' [pause 0.28s] -> [00:04.8-00:08.5s] 'How could Russia stop them while trying to overwhelm its targets?' [pause 0.35s] -> [00:08.8-00:11.5s] 'And how would the Baltics fight back?' [pause 0.40s] -> [00:11.9-00:14.5s] 'This is how it could all play out.' [pause 0.50s] -> [00:15.0-00:20.0s] [Split-flap mechanical flip and kinetic afterburners engage]",
            "sentence_structure_formula_vi": "Công thức 5 bước Fern TV: (1) Thiết lập quy mô đám đông hoặc quân sự khổng lồ ('Hundreds of thousands move...') -> (2) Định hình hệ thống ngầm điều phối ('coordinated by invisible digital systems...') -> (3) Câu hỏi tu từ kép phá vỡ ảo tưởng kiểm soát cá nhân ('Yet who pulls these levers? Could populations be steered?') -> (4) Hé lộ cơ chế kỹ thuật bên trong trung tâm chỉ huy ('Inside subterranean command bunkers, autonomous systems track...') -> (5) Câu kết mang tính biểu tượng khẳng định quy luật ('This is how the crowd strings pull').",
            "pause_and_cadence_formula_vi": "Nhịp đọc điện ảnh kịch tính ~140 WPM: Nghỉ ngắn 0.22s sau mệnh đề hành động; nghỉ 0.38s sau khi định hình hệ thống; nghỉ 0.42s sau câu hỏi tu từ để tạo độ căng thẳng; nghỉ 0.25-0.35s giữa các chi tiết máy móc và bảng cơ học.",
            "transition_and_camera_formula_vi": "Zoompan mượt mà không snap 1-frame; chuyển cảnh xfade 0.28s: fade khi vào không gian ngầm, smoothdown/smoothup khi lia qua radar và bảng split-flap, smoothleft/smoothright khi drone lướt qua rặng núi.",
        },
    },
    "en-cold-case-ink": {
        "channel_slug": "en-cold-case-ink",
        "niche": "Hồ sơ Bí ẩn & Trinh thám Hình sự (Forensic Mysteries & Unsolved Archives)",
        "competitor_name": "LEMMiNO",
        "voice": "en-GB-RyanNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00-00:03.5s] '...when an upstairs tenant named John Reeves headed out for work.' [pause 1.50s] -> [00:05.0-00:11.5s] 'Upon reaching the first floor landing, Reeves encountered the body of a woman lying upon her back in a pool of blood.' [pause 2.50s] -> [00:14.0-00:17.5s] 'Horrified by the sight, he stumbled down to the street below in search for help.' [pause 0.50s] -> [00:18.0-00:20.0s] 'At four forty-five in the morning, the mystery began.'",
            "sentence_structure_formula_vi": "Công thức 5 bước LEMMiNO: (1) Mốc thời gian và không gian lịch sử cụ thể ('Before dawn in Victorian London...') -> (2) Hành động đời thường của người chứng kiến ('a resident stepped into the silent alley...') -> (3) Phát hiện rùng rợn phá vỡ sự tĩnh lặng ('On the landing lay an unmoving silhouette...') -> (4) Câu hỏi tu từ truy vấn dấu vết biến mất ('Who vanished so cleanly into the fog?') -> (5) Tổng kết điều tra pháp y và sự bế tắc của các manh mối ('red thread ties five separate crime scenes... yet the shadow remains forever unsolved').",
            "pause_and_cadence_formula_vi": "Nhịp đọc trầm mặc lạnh lùng phong cách noir điều tra Anh quốc ~135 WPM: Nghỉ ngắn 0.22s sau mệnh đề thời gian; nghỉ 0.38s sau hành động bước đi; nghỉ sâu 0.45s sau câu hỏi tu từ để âm thanh sương đêm vang vọng; nghỉ 0.25-0.35s giữa các chứng cứ pháp y.",
            "transition_and_camera_formula_vi": "Zoompan mượt mà không snap 1-frame; chuyển cảnh xfade 0.28s: fade khi chuyển góc sa bàn 3D, smoothdown khi lia từ mái nhà xuống ngõ hẻm, smoothleft/smoothright khi quét theo sợi chỉ đỏ trên bản đồ Whitechapel.",
        },
    },
    "en-choke-point": {
        "channel_slug": "en-choke-point",
        "niche": "Địa chính trị Hàng hải & Bản đồ Vệ tinh Quỹ đạo (Maritime Geopolitics)",
        "competitor_name": "RealLifeLore",
        "voice": "en-US-ChristopherNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00-00:05.0s] 'At any single time, there are around fifty thousand merchant vessels carrying as much as six million containers...' [pause 0.18s] -> [00:05.2-00:11.0s] '...full of cargo and goods all across the world's oceans and between all the world's continents.' [pause 0.99s] -> [00:12.0-00:20.0s] 'These networks and streams of ships that you see moving in lines across the world's surface here are the literal arteries that power the beating heart of the global economy.'",
            "sentence_structure_formula_vi": "Công thức 5 bước RealLifeLore: (1) Số liệu khổng lồ về đội tàu thương mại trên đại dương ('Fifty thousand vessels traverse open oceans...') -> (2) Quy mô container hàng hoá khổng lồ ('carrying six million containers right now...') -> (3) Nút thắt cổ chai địa lý ngặt nghèo ('Yet ninety percent must squeeze through narrow straits...') -> (4) Câu hỏi khủng hoảng chuỗi cung ứng toàn cầu ('What happens when one canal shuts down?') -> (5) Bản đồ động mạch thương mại và kết luận địa chính trị tối thượng ('a single blockage strangles trillions in trade... Whoever controls these choke points commands the world').",
            "pause_and_cadence_formula_vi": "Nhịp đọc khẩn trương kịch tính địa chính trị ~150 WPM: Nghỉ ngắn 0.22s sau mệnh đề quy mô; nghỉ 0.38s sau khi chốt số lượng container; nghỉ 0.42s sau câu hỏi giả định khủng hoảng; nghỉ 0.25-0.35s giữa các chi tiết hải trình.",
            "transition_and_camera_formula_vi": "Zoompan mượt mà không snap 1-frame; chuyển cảnh xfade 0.28s: fade khi chuyển góc nhìn vệ tinh quỹ đạo, smoothdown/smoothup khi lia dọc kênh đào Suez, smoothleft/smoothright khi quét theo luồng hàng hải eo biển Hormuz và Malacca.",
        },
    },
    "en-root-and-canopy": {
        "channel_slug": "en-root-and-canopy",
        "niche": "Thực vật học & Hệ sinh thái Rừng (Botany & Forest Ecology)",
        "competitor_name": "BBC Earth (The Green Planet)",
        "voice": "en-GB-RyanNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00-00:04.2s] 'Dramatic behavior... because to our eyes, it happens so slowly.' [pause 0.51s] -> [00:04.7-00:10.8s] 'But if time is compressed, and you shift perspective to the plant's point of view,' [pause 0.35s] -> [00:11.1-00:13.5s] 'their world comes spectacularly to life.' [pause 0.97s] -> [00:14.5-00:20.0s] 'The events in this woodland can build to a view of half a year in less than a minute.'",
            "sentence_structure_formula_vi": "Công thức 5 bước BBC Earth / Sir David Attenborough: (1) Mở đầu bằng nghịch lý thị giác vi mô ('Deep beneath the silent forest floor...') -> (2) Chuyển động tiềm ẩn của mạng lưới ('a vast fungal network quietly breathes') -> (3) Đột phá độ ẩm đánh thức sự sống ('Morning moisture awakens dormant moss...') -> (4) Gia tốc sinh trưởng quang hợp ('and young ferns uncurl toward filtered light') -> (5) Vũ khí sinh tồn & cộng sinh tán rừng ('Carnivorous sundews glisten... uniting the entire forest into one organism').",
            "pause_and_cadence_formula_vi": "Nhịp đọc trầm ấm, thư thái 142 WPM chuẩn tài liệu BBC: Nghỉ ngắn 0.22s sau mệnh đề thiết lập vị trí; nghỉ 0.35s sau cụm danh từ sinh học; nghỉ 0.40s trước bước ngoặt quang hợp; và nghỉ 0.30s ở câu kết để âm hưởng nhạc giao hưởng ngân vang.",
            "transition_and_camera_formula_vi": "Chuyển động máy quay mượt mà không giật (tilt_down len vào lòng đất, push_in sát tơ nấm, tilt_up vươn theo chồi dương xỉ và cành hoa), kết hợp chuyển cảnh xfade tự nhiên (fade, smoothleft, smoothright, smoothup, smoothdown).",
        },
    },
    "en-spawn-to-apex": {
        "channel_slug": "en-spawn-to-apex",
        "niche": "Vi sinh học & Vòng đời Côn trùng theo Thời gian (Chronological Insect Life-Cycle)",
        "competitor_name": "Deep Look PBS",
        "voice": "en-US-AndrewNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00-00:02.4s] 'Pill bugs... Roly-polies... Potato bugs...' [pause 0.96s] -> [00:03.4-00:07.5s] 'Whatever you want to call them, somehow there's something less creepy about these guys' [pause 0.22s] -> [00:07.7-00:11.8s] 'than other insects. More lovable, or something.' [pause 0.40s] -> [00:12.2-00:15.5s] 'Maybe it's the way they roll into a perfect little armored sphere.' [pause 0.30s] -> [00:15.8-00:20.0s] 'Or maybe it's because they aren't actually insects at all.'",
            "sentence_structure_formula_vi": "Công thức 5 giai đoạn vòng đời sinh học Deep Look PBS: (1) Trứng phôi thai siêu vi mô ('Clustered beneath a dew-covered leaf...') -> (2) Nhịp tim phôi thai hé lộ sự sống ('tiny translucent eggs harbor microscopic life') -> (3) Khoảnh khắc ấu trùng cắn vỏ nở ('Suddenly, a hungry hatchling cracks its shell...') -> (4) Bản năng săn mồi sơ sinh ('stepping into the open world to hunt') -> (5) Lột xác chitin, đóng kén nhộng và hóa thân thành kẻ săn mồi đỉnh cao ('Splitting its rigid armor... an undisputed master of the forest canopy').",
            "pause_and_cadence_formula_vi": "Nhịp đọc truyền cảm hứng, tốc độ 145 WPM của phim tài liệu khoa học PBS: Nghỉ 0.22s sau mệnh đề mở cảnh; nghỉ 0.35s sau quan sát tế bào; nghỉ 0.40s sau bước ngoặt nở vỏ; và nghỉ 0.30s sau khi xòe càng săn mồi đỉnh cao.",
            "transition_and_camera_formula_vi": "Chuỗi chuyển cảnh macro quang học liền mạch: fade mở đầu trên cụm trứng, smoothleft lia sang nhịp tim phôi, smoothright bám theo ấu trùng nở, smoothup hướng lên giai đoạn săn mồi, smoothdown theo vết lột xác và fade kết thúc trên dáng đứng uy dũng của kẻ săn mồi.",
        },
    },
    "en-second-arrow": {
        "channel_slug": "en-second-arrow",
        "niche": "Triết học Khắc kỷ & Cổ điển (Stoicism & Classical Philosophy)",
        "competitor_name": "Einzelgänger / Daily Stoic",
        "voice": "",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00-00:03.3s] 'And yet, despite all this, what do you see in those eyes?' [pause 0.20s] -> [00:03.5-00:05.9s] 'Not despair, not defeat,' [pause 0.50s] -> [00:06.5-00:10.2s] 'but something far more remarkable: an unshakable calm,' [pause 0.38s] -> [00:10.6-00:14.5s] 'a quiet dignity that refuses to be broken.' [pause 1.57s] -> [00:16.1-00:20.0s] 'It's as if these marble figures, frozen in time, hold a secret—a lesson in how to endure.'",
            "sentence_structure_formula_vi": "Công thức 5 bước Khắc kỷ Einzelgänger / Daily Stoic: (1) Cú đánh bất ngờ của số phận ('Life strikes us with unexpected pain...') -> (2) Hiện thực khách quan mũi tên thứ nhất ('a sudden arrow pierces our shoulder') -> (3) Phân định ranh giới nỗi đau thể xác ('Yet the wound itself brings only injury') -> (4) Câu hỏi tu từ cốt lõi ('why does our mind turn it into agony?') -> (5) Mũi tên thứ hai tự tạo & Bản lĩnh Marcus Aurelius ('Because our anger forges a second arrow... disarming the second arrow before it strikes').",
            "pause_and_cadence_formula_vi": "Nhịp đọc suy tư sâu lắng 143 WPM với quãng nghỉ có chủ đích: Nghỉ ngắn 0.22s sau mệnh đề nhát tên đầu; nghỉ 0.42s sau phân định vết thương; nghỉ sâu 0.45s sau câu hỏi tu từ để tâm trí tự soi chiếu; nghỉ 0.38s trước khi đưa ra tấm gương Marcus Aurelius.",
            "transition_and_camera_formula_vi": "Chuyển động máy quay phong cách chiaroscuro Caravaggio uy nghiêm: push_in vào mũi tên trúng bia đá, zoom_out nhìn bão táp La Mã, push_in cận cảnh tượng đồng Seneca, tilt_up đe rèn sắt, pan_right tượng cẩm thạch dưới mưa, và fade vào bình minh quang đãng trên thềm đền cổ.",
        },
    },
    "en-bamboo-marble": {
        "channel_slug": "en-bamboo-marble",
        "niche": "Triết học Phương Đông & Chiêm nghiệm Sống (Eastern Philosophy & Life Lessons)",
        "competitor_name": "Pursuit of Wonder / Aperture",
        "voice": "",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00-00:05.8s] 'Most of us, on some level, are chasing this feeling of peace.' [pause 0.40s] -> [00:06.2-00:10.5s] 'We seek out expensive therapists, read self-help books, listen to happiness gurus.' [pause 0.50s] -> [00:11.0-00:16.5s] 'Searching for answers that will hopefully make us better, more tranquil human beings.' [pause 0.65s] -> [00:17.1-00:20.0s] 'But what if it's simpler than all that?'",
            "sentence_structure_formula_vi": "Công thức 5 nhịp tự sự Đạo giáo Pursuit of Wonder / Aperture: (1) Nỗi mệt mỏi khi cưỡng lại tự nhiên ('We exhaust ourselves battling life's quiet current...') -> (2) Ảo tưởng kiểm soát qua các quy tắc cứng nhắc ('searching endlessly for peace in rigid routines') -> (3) Đổ vỡ của nỗ lực áp đặt ('Yet true peace cannot be conquered by force') -> (4) Câu hỏi tu từ buông bỏ ('what if surrender is the secret?') -> (5) Ẩn dụ tre uốn mình & nước xẻ đá ('Bamboo weathers violent typhoons... finding unshakeable calm').",
            "pause_and_cadence_formula_vi": "Nhịp điệu tự sự chiêm nghiệm 141 WPM: Nghỉ 0.22s sau mệnh đề mệt mỏi; nghỉ 0.38s sau thói quen cứng nhắc; nghỉ sâu 0.45s sau câu hỏi bước ngoặt ('what if surrender is the secret?'); nghỉ 0.35s sau ẩn dụ nước mềm xuyên đá cứng.",
            "transition_and_camera_formula_vi": "Chuyển động máy quay anamorphic 35mm hoài niệm: push_in trong gian trà thất Kyoto tĩnh lặng, smoothleft dưới mái hiên chùa mưa rơi, smoothup xuyên qua rừng tre uốn gió, smoothdown trên suối nước đá cuội, và fade trầm tĩnh vào hoàng hôn.",
        },
    },
    "en-kindred-sketch": {
        "channel_slug": "en-kindred-sketch",
        "niche": "Tâm lý Tình cảm & Gắn kết (Relationships & Attachment Psychology)",
        "competitor_name": "Cinema Therapy / The School of Life",
        "voice": "en-US-JennyNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00-00:03.2s] 'Wait, what was it, a phone interview? Wow.' [pause 0.36s] -> [00:03.6-00:08.3s] 'Miranda Priestly is famous for being unpredictable.' [pause 0.28s] -> [00:08.6-00:11.8s] 'Okay Doug, how is it that you know who she is and I didn't?' [pause 0.21s] -> [00:12.0-00:15.5s] 'I'm actually a girl... Well, that would explain so much.' [pause 0.35s] -> [00:15.8-00:20.0s] 'Look, seriously, Miranda Priestly is a huge deal. A million girls would kill for that.'",
            "sentence_structure_formula_vi": "Công thức đối thoại tâm lý mối quan hệ: (1) Bối cảnh căng thẳng gần gũi ('When someone you love...') -> (2) Phán đoán sai lầm trực giác ('we assume they don't care') -> (3) Đảo chiều tâm lý giật mình ('Instead, silence is a scream of fear') -> (4) Câu hỏi tu từ cốt lõi ('Why do we attack when we want affection?') -> (5) Cơ chế phòng vệ vô thức ('nervous system perceives rejection as danger') -> (6) Đóng sập cánh cửa giao tiếp ('slamming down walls') -> (7) Phủ định phương pháp sai ('Closeness doesn't return by battering the door') -> (8) Đích đến gắn kết an toàn ('when you build safety together').",
            "pause_and_cadence_formula_vi": "Nhịp đọc trầm ấm, thấu cảm ~138 WPM: Micro-pause 0.22s sau mệnh đề điều kiện mở đầu; beat-pause 0.38s sau phán đoán; dramatic-pause 0.45s sau câu hỏi tu từ để người xem tự nhìn nhận bản thân; pause 0.30s trước kết luận đắt giá.",
            "transition_and_camera_formula_vi": "Chuyển động máy quay cận cảnh nhẹ nhàng (push_in, pan_left, tilt_up) tái hiện không gian ăn tối thân mật, kết hợp hiệu ứng xfade 0.28s (smoothleft khi đổi góc nhìn giữa hai người, smoothup/smoothdown khi đổi trạng thái cảm xúc, và fade khi mở đầu/kết thúc).",
        },
    },
    "en-lazy-brain": {
        "channel_slug": "en-lazy-brain",
        "niche": "Thần kinh học Dopamine, Thói quen & Sự tập trung (Neuroscience of Habits)",
        "competitor_name": "Kurzgesagt / Huberman Lab",
        "voice": "en-US-AndrewNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00-00:03.0s] 'As you know that after eating, you will feel good.' [pause 0.50s] -> [00:03.5-00:07.5s] 'In other words, it makes the activity of eating pleasurable and memorable,' [pause 0.55s] -> [00:08.0-00:11.5s] 'so you would want to do it again and again whenever you feel hungry.' [pause 0.85s] -> [00:12.4-00:15.4s] 'The brain consists of billions of neurons or nerve cells,' [pause 0.51s] -> [00:15.9-00:20.0s] 'which communicate via neurotransmitters across microscopic synapses.'",
            "sentence_structure_formula_vi": "Công thức thần kinh học hành vi Huberman: (1) Trừ khử ảo tưởng thiếu ý chí ('You think you lack willpower') -> (2) Quy chuẩn hóa sinh khách quan ('brain is executing chemistry') -> (3) Xung đột dopamine giá rẻ ('Every cheap dopamine spike trains neurons') -> (4) Hệ quả lệch ngưỡng phần thưởng ('demand more reward for less work') -> (5) Câu hỏi tu từ cảm giác kháng cự ('Why does real effort feel so painful?') -> (6) Cơ chế điều hòa giảm thụ thể ('flooded receptors dial down sensitivity') -> (7) Giao thức hành động vi mô ('Wait ninety seconds before giving in') -> (8) Đích đến phục hồi mạch tập trung ('focus circuits instantly recover').",
            "pause_and_cadence_formula_vi": "Nhịp đọc khoa học đĩnh đạc ~142 WPM: Micro-pause 0.22s sau mệnh đề điều kiện; beat-pause 0.38s sau khi lật ngược nguyên nhân sinh học; dramatic-pause 0.45s sau câu hỏi tu từ để kích thích nhận thức; pause 0.30s trước kết luận đòn bẩy.",
            "transition_and_camera_formula_vi": "Supersampled 2x zoompan kết hợp chuyển cảnh xfade mượt 0.28s (smoothup khi hướng lên thùy trán, smoothleft/smoothright khi quét dọc mạng lưới synap nơ-ron, và fade mềm khi chuyển giữa mô phỏng 3D sinh học và cảnh hành động thực tế).",
        },
    },
    "en-career-leverage": {
        "channel_slug": "en-career-leverage",
        "niche": "Chiến lược Sự nghiệp & Đàm phán (Workplace Strategy & Leverage)",
        "competitor_name": "Wall Street Journal / HBR",
        "voice": "en-US-EricNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00-00:02.5s] 'a fraction of its peak value.' [pause 0.26s] -> [00:02.8-00:09.5s] 'WeWork, co-founded by Adam Neumann, specialized in leasing shared work spaces in metropolitan areas around the world.' [pause 0.40s] -> [00:09.9-00:16.8s] 'We are a company that builds communities. Our main thing that we do is curate and create culture.' [pause 0.38s] -> [00:17.2-00:20.0s] 'WeWork was founded in 2010 right in the wake of the financial crisis.'",
            "sentence_structure_formula_vi": "Công thức đàm phán đòn bẩy Wall Street Journal: (1) Mệnh đề tiên đề quyền lực ('In executive salary talks, leverage is silent') -> (2) Phá vỡ định kiến chăm chỉ ('and hard work rarely earns it') -> (3) Bản chất thị trường phi đối xứng ('comes from rare, irreplaceable market alternatives') -> (4) Câu hỏi tu từ bất công đãi ngộ ('Why do top performers still get underpaid?') -> (5) Cơ chế định giá chi phí thay thế ('companies pay for replacement cost, not effort') -> (6) Nắm giữ mắt xích trọng yếu ('When you control a critical bottleneck, you dictate terms') -> (7) Lá bài tẩy tối thượng ('The ultimate negotiating power is walking away') -> (8) Đích đến hành động chủ động ('Build your leverage before you sit down').",
            "pause_and_cadence_formula_vi": "Nhịp đọc đĩnh đạc, dứt khoát của chuyên gia tài chính ~152 WPM: Micro-pause 0.22s sau mệnh đề điều kiện; beat-pause 0.38s sau khi lật tẩy ảo tưởng chăm chỉ; dramatic-pause 0.45s sau câu hỏi nghịch lý đãi ngộ; pause 0.30s trước câu kết luận chiến lược.",
            "transition_and_camera_formula_vi": "Supersampled 2x zoompan kết hợp xfade 0.28s (smoothleft khi chuyển đổi góc đối thoại trong phòng họp kính, smoothup khi nâng tầm quy mô tòa nhà Manhattan, và fade đĩnh đạc khi chuyển phân cảnh dữ liệu).",
        },
    },
    "en-wallet-anatomy": {
        "channel_slug": "en-wallet-anatomy",
        "niche": "Tâm lý Định giá & Tài chính Tiêu dùng (Behavioral Pricing & Consumer Finance)",
        "competitor_name": "Two Cents PBS / WSJ",
        "voice": "en-US-AndrewNeural",
        "competitor_dialogue_formula": {
            "competitor_verbatim_transcript_20s": "[00:00-00:03.5s] 'in categories like store cleanliness and item availability.' [pause 0.28s] -> [00:03.8-00:08.0s] 'But there is another key tactic grocers use to aid their low-cost images:' [pause 0.42s] -> [00:08.4-00:13.5s] 'Known Value Items. These are staple household products whose prices people often remember.' [pause 0.48s] -> [00:14.0-00:20.0s] 'As Aldi has expanded across the country, other grocers have reduced their prices in response on basic goods.'",
            "sentence_structure_formula_vi": "Công thức kinh tế học tiêu dùng Two Cents: (1) Cảnh báo ma trận không gian bán lẻ ('Supermarket layouts are psychological traps') -> (2) Mục đích thao túng vô hình ('designed to hijack your spending') -> (3) Chiêu thức mồi nhử giá rẻ ('Grocers slash prices on milk and eggs') -> (4) Câu hỏi tu từ về dòng tiền rò rỉ ('So how do they still drain your paycheck?') -> (5) Cơ chế bố trí ngang tầm mắt ('By placing high-margin snacks right at eye-level') -> (6) Bẫy giá chim mồi ('Decoy pricing tricks you into buying premium items') -> (7) Giao thức tự vệ người tiêu dùng ('Shop only with a written perimeter list') -> (8) Đích đến an toàn tài chính ('and protect your hard-earned cash').",
            "pause_and_cadence_formula_vi": "Nhịp đọc phân tích sắc sảo, gần gũi ~148 WPM: Micro-pause 0.22s sau mệnh đề điều kiện; beat-pause 0.38s sau khi lật tẩy chiến thuật mồi nhử; dramatic-pause 0.45s sau câu hỏi tu từ để người xem hồi tưởng trải nghiệm bị hớ; pause 0.30s trước giải pháp tiết kiệm.",
            "transition_and_camera_formula_vi": "Supersampled 2x zoompan kết hợp xfade 0.28s (smoothright khi trượt dọc dãy kệ hàng, smoothleft khi quay lại giỏ hàng, smoothup khi nâng tầm mắt lên kệ đồ cao cấp, và fade khi chuyển cảnh studio chụp sản phẩm).",
        },
    },
}
