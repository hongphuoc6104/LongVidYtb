"""
Batch 2 Topic Blueprint and Story Rows for Channel: ua_sao_vay
Niche: Khoa Học Đời Sống, Thí Nghiệm & Bóc Trần Ngụy Khoa Học ("Ủa Sao Vậy?")
Topic: Giải Mã 6 Lời Đồn Về Cơ Thể: Quy Tắc 5 Giây Thức Ăn Rơi Có Thật Không?
"""

from typing import Any, Dict, List, Tuple

CHANNEL_ID = "ua_sao_vay"
CHANNEL_SLUG = "ua-sao-vay"

LONG_TOPIC = "Giải Mã 6 Lời Đồn Về Cơ Thể: Quy Tắc 5 Giây Thức Ăn Rơi Có Thật Không?"
SHORT_TOPIC = "Quy Tắc 5 Giây Thức Ăn Rơi Xuống Đất: Sự Thật Hay Trò Đùa?"
LONG_AUDIENCE = "Mọi người yêu thích khoa học đời sống, tò mò về cơ chế sinh học thường ngày"
SHORT_AUDIENCE = "Khán giả trẻ hay tin vào những mẹo vặt truyền miệng trong đời sống"

LONG_GOAL = "Bóc trần 6 ngụy khoa học phổ biến về cơ thể người và quy tắc 5 giây dưới góc nhìn vi sinh học thực nghiệm"
SHORT_GOAL = "Thực nghiệm tốc độ bám dính vi khuẩn dưới 1 giây và dẫn dắt người xem vào video dài bóc trần 5 ngụy khoa học còn lại"

LONG_EDITORIAL_STANCE = {
    "myth_debunked": "Thức ăn rơi xuống sàn nhặt lên trong năm giây vẫn sạch sẽ và an toàn tuyệt đối.",
    "why_generic_advice_fails": "Nhiều người truyền tai nhau quy tắc năm giây như một mẹo vặt dân gian vô hại mà không biết vi khuẩn bám dính tính bằng mili-giây.",
    "channel_verdict": "Sự thật mất lòng là vi khuẩn không có đồng hồ bấm giờ và việc ăn thức ăn rơi sàn chỉ là trò chơi xúc xắc với hệ miễn dịch.",
    "tradeoff_or_blindspot": "Bỏ một mẩu đồ ăn bẩn có thể gây tiếc rẻ vài nghìn đồng nhưng bảo vệ bạn khỏi nguy cơ nhiễm khuẩn đường ruột cấp tính.",
}

LONG_ACTIONABLE_VALUE = {
    "core_mechanism": "Cơ chế bám dính vi sinh vật phụ thuộc vào độ ẩm bề mặt chứ không phụ thuộc vào thời gian tiếp xúc.",
    "practical_rule_of_thumb": "Quy tắc độ ẩm thực nghiệm: bất kỳ thức ăn ướt nào chạm sàn đều phải vứt bỏ ngay lập tức.",
    "real_world_scenario": "Một bạn trẻ làm rơi lát dưa hấu xuống nền gạch đã dứt khoát bỏ sọt rác thay vì lau chùi rồi ăn tiếp.",
}

SHORT_EDITORIAL_STANCE = {
    "myth_debunked": "Quy tắc năm giây giúp đồ ăn rơi xuống đất không kịp bị nhiễm vi khuẩn.",
    "why_generic_advice_fails": "Lời đồn dân gian tạo cảm giác an tâm giả tạo khiến bạn nuốt hàng triệu vi khuẩn vào bụng.",
    "channel_verdict": "Sự thật mất lòng là vi khuẩn bám dính ngay lập tức trong một phần trăm giây đầu tiên tiếp xúc.",
    "tradeoff_or_blindspot": "Vứt mẩu thức ăn rơi sàn tạo cảm giác lãng phí nhưng giữ cho bạn khỏe mạnh dài lâu.",
}

SHORT_ACTIONABLE_VALUE = {
    "core_mechanism": "Lực mao dẫn của chất lỏng kéo vi khuẩn bám chặt vào thực phẩm ngay thời khắc va chạm.",
    "practical_rule_of_thumb": "Quy tắc nhặt rác: thức ăn rơi xuống sàn nhà công cộng luôn được coi là nguồn lây nhiễm.",
    "real_world_scenario": "Dứt khoát bỏ miếng xúc xích rơi sàn bếp dù vừa lau nhà xong để bảo vệ sức khỏe cả nhà.",
}

LONG_SOURCES = [
    {
        "id": "SRC01",
        "title": "Nghiên Cứu Vi Sinh Học Về Tốc Độ Lây Nhiễm Bề Mặt",
        "reference": "Đại Học Rutgers (2016). Khảo Sát Tốc Độ Bám Dính Của Vi Khuẩn Enterobacter Lên Bề Mặt Thực Phẩm.",
        "facts": [
            "Vi khuẩn có thể bám dính vào thực phẩm ẩm ướt trong thời gian dưới một trăm mili-giây.",
            "Bề mặt thảm có tỷ lệ truyền vi khuẩn thấp hơn sàn gạch men và thép không gỉ.",
        ],
    }
]

SHORT_SOURCES = [
    {
        "id": "SRC01",
        "title": "Thực Nghiệm Tốc Độ Lây Nhiễm Vi Sinh",
        "reference": "Đại Học Rutgers (2016). Báo Cáo Thực Nghiệm Bám Dính Bề Mặt.",
        "facts": [
            "Vi khuẩn lây nhiễm ngay thời điểm va chạm mà không cần đợi đủ năm giây.",
        ],
    }
]

LONG_PACKAGING = {
    "youtube_title": "Giải Mã 6 Lời Đồn Cơ Thể: Quy Tắc 5 Giây Có Thật Không?",
    "visual_hook": "Người que cầm kính hiển vi soi mẩu xúc xích rơi sàn thấy hàng triệu vi khuẩn nhảy múa bám dính",
    "text_overlay": "SỰ THẬT 5 GIÂY",
    "contrast_pair": "Ảo tưởng phủi bụi ăn tiếp vs Thực tế vi khuẩn bám dính trong 0.1 giây",
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": [
        "ua sao vay",
        "quy tac 5 giay",
        "khoa hoc thuong thuc",
        "loi don co the",
        "vi sinh vat",
    ],
    "cta_plan": {
        "mid_cta": "Nếu bạn từng nhặt đồ ăn rơi sàn lên rồi thổi phù một cái ăn tiếp, hãy lưu video này lại nhé.",
        "close": "Bạn từng tin vào lời đồn nào nhất trong sáu điều trên, hãy chia sẻ trải nghiệm dưới bình luận nhé.",
        "endcard_text": "ỦA SAO VẬY?",
    },
}

SHORT_PACKAGING = {
    "youtube_title": "Quy Tắc 5 Giây Thức Ăn Rơi: Sự Thật Hay Trò Đùa?",
    "visual_hook": "Người que cúi xuống nhặt mẩu bánh mì rơi sàn nhưng kính lúp phóng to vi khuẩn bu kín",
    "text_overlay": "5 GIÂY THẬT KHÔNG?",
    "contrast_pair": "Đếm ngược 5 giây dân gian vs Vi khuẩn bám dính ngay tích tắc 0.1 giây",
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": [
        "ua sao vay",
        "quy tac 5 giay",
        "khoa hoc vui",
        "shorts",
    ],
    "cta_plan": {
        "cliffhanger_peak": "Đúng lúc bạn nghĩ sàn nhà vừa lau bằng nước tẩy là sạch thì bí mật vi khuẩn kháng thuốc ẩn nấp ra sao?",
        "bridge": "Xem video bản dài bên dưới để bóc trần 5 ngụy khoa học về cơ thể nhé.",
        "close": "Lưu lại ngay để bảo vệ đường tiêu hóa của cả gia đình bạn nhé.",
        "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
    },
}

LONG_STORY_ROWS = [
    (
        "Mẩu bánh rơi sàn và phản xạ 5 giây",
        "A bright sunny kitchen dining area on clean white canvas.",
        "narrative_warm",
        "curiosity_hook",
        [
            ("Một mẩu bánh mì thơm phức trượt khỏi tay bạn và rơi thẳng xuống nền gạch nhà bếp.", [
                {"spec": "full_scene:CH01|The stickman accidentally drops a slice of bread down toward floor tile.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "TRƯỢT TAY RƠI SÀN"},
                {"spec": "macro_prop:none|A golden toasted bread slice tumbling through midair toward clean floor.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "NỀN GẠCH NHÀ BẾP"},
            ]),
            ("Rất nhanh như một phản xạ tự nhiên, bạn cúi xuống nhặt lên, đếm thầm chưa tới năm giây.", [
                {"spec": "full_scene:CH01|Stickman swiftly bends down scooping up bread slice with triumphant smile.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CHƯA TỚI 5 GIÂY"},
                {"spec": "visual_diagram:none|A digital countdown timer stopping boldly at 00:03 seconds on white canvas.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "PHẢN XẠ NHANH"},
            ]),
            ("Bạn phủi nhẹ một cái rồi bỏ vào miệng, tin rằng vi khuẩn chưa kịp thức giấc bò lên thức ăn.", [
                {"spec": "concept_metaphor:CH01|Stickman blows a puff of breath across bread slice believing it cleans germ.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "THỔI PHỦI VỘI VÃ"},
                {"spec": "visual_diagram:none|Comparison graphic: Folk Legend of 5 Seconds versus Microscopic Reality.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "VI KHUẨN KỊP BÒ?"},
            ]),
        ]
    ),
    (
        "Thí nghiệm thực tế của Đại học Rutgers",
        "A high precision microbiology research lab on clean white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Giáo sư Donald Schaffner tại Đại học Rutgers đã tiến hành gần hai ngàn phép đo vi sinh học.", [
                {"spec": "full_scene:CH01|Microbiologist stickman in lab coat inspects petri dishes under UV lamp.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HAI NGÀN PHÉP ĐO"},
                {"spec": "visual_diagram:none|Petri dish array grid displaying various food types tested across contact times.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐẠI HỌC RUTGERS"},
            ]),
            ("Họ thả dưa hấu, bánh mì và kẹo dẻo xuống các bề mặt gạch men, gỗ, thảm và inox.", [
                {"spec": "concept_metaphor:CH01|Stickman tests different food items onto four distinct floor test panels.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BỐN BỀ MẶT THỬ NGHIỆM"},
                {"spec": "still_life:none|Watermelon slice, bread crust, and gummy candy arranged beside test tiles.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "DƯA HẤU VÀ BÁNH MÌ"},
            ]),
            ("Kết quả chấn động: vi khuẩn lây nhiễm ngay tức khắc trong thời gian dưới một phần trăm giây.", [
                {"spec": "full_scene:CH01|Scientist gasps pointing to digital counter reading 0.01s infection onset.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "0.01 GIÂY"},
                {"spec": "visual_diagram:none|Millisecond timeline showing instantaneous bacterial transfer at moment of impact.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "LÂY NHIỄM TỨC KHẮC"},
            ]),
        ]
    ),
    (
        "Yếu tố quyết định: Độ ẩm chứ không phải thời gian",
        "A fluid mechanics and surface science room on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Vi khuẩn không có chân để chạy đua theo thời gian, chúng di chuyển nhờ lực mao dẫn chất lỏng.", [
                {"spec": "full_scene:CH01|Stickman demonstrates liquid surface tension dragging microbes effortlessly.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "LỰC MAO DẪN CHẤT LỎNG"},
                {"spec": "visual_diagram:none|Capillary action diagram showing liquid bridge pulling bacteria across gap.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CƠ CHẾ DI CHUYỂN"},
            ]),
            ("Những món ăn có bề mặt ẩm ướt như dưa hấu hay thịt nguội sẽ hút trọn ổ vi khuẩn ngay khi chạm sàn.", [
                {"spec": "concept_metaphor:CH01|A juicy watermelon slice acts like a sponge soaking up microbial ink dots.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HÚT TRỌN Ổ VI KHUẨN"},
                {"spec": "visual_diagram:none|Moisture comparison chart: Wet Watermelon vs Dry Cracker bacterial transfer rate.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐỘ ẨM QUYẾT ĐỊNH"},
            ]),
            ("Trong khi đó bánh quy khô cứng có tỷ lệ nhiễm vi sinh thấp hơn nhưng tuyệt đối không phải là vô trùng.", [
                {"spec": "full_scene:CH01|Stickman examines a dry cracker showing small colony count under microscope.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "KHÔNG PHẢI VÔ TRÙNG"},
                {"spec": "macro_prop:none|A dry cracker showing microscopic bacterial clusters attached to crumbs.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "BÁNH QUY KHÔ"},
            ]),
        ]
    ),
    (
        "Nghịch lý mặt thảm: Tại sao sàn gạch lại bẩn hơn?",
        "A surface physics laboratory desk on clean white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Một phát hiện bất ngờ khác từ thí nghiệm là sàn thảm lại truyền ít vi khuẩn hơn gạch men bóng loáng.", [
                {"spec": "full_scene:CH01|Stickman holds up a soft carpet square comparing it with a ceramic tile.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "NGHỊCH LÝ MẶT THẢM"},
                {"spec": "visual_diagram:none|Comparison graphic: Ceramic Tile High Transfer vs Deep Carpet Fiber Retention.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ÍT HƠN GẠCH MEN"},
            ]),
            ("Cấu trúc sợi thảm xốp giữ các hạt vi sinh vật sâu bên dưới thay vì để chúng tiếp xúc bề mặt thực phẩm.", [
                {"spec": "concept_metaphor:CH01|Stickman parts fiber strands showing dust trapped deep in carpet base.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "GIỮ SÂU BÊN DƯỚI"},
                {"spec": "still_life:none|A cross-section illustration of woven carpet fibers holding particles at bottom.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "CẤU TRÚC SỢI XỐP"},
            ]),
            ("Ngược lại mặt gạch men bằng phẳng tạo điều kiện cho toàn bộ diện tích đồ ăn áp sát ổ vi khuẩn.", [
                {"spec": "full_scene:CH01|Stickman shows full surface contact area flat against smooth tile plane.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "ÁP SÁT TOÀN BỘ"},
                {"spec": "visual_diagram:none|Surface contact area comparison showing 100% tile contact vs 15% carpet contact.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "TIẾP XÚC TỐI ĐA"},
            ]),
        ]
    ),
    (
        "Lời đồn số hai: Bẻ khớp ngón tay gây viêm khớp?",
        "An orthopedic medical demonstration clinic on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Nhiều người thường bị nhắc nhở không được bẻ khớp tay vì sợ sau này sẽ bị thoái hóa và run tay.", [
                {"spec": "full_scene:CH01|Stickman flexes knuckles producing a loud comic CRACK sound bubble.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "BẺ KHỚP TAY"},
                {"spec": "visual_diagram:none|An anatomical hand bone joint model showing cartilage spacing on white canvas.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "NỖI SỢ THOÁI HÓA"},
            ]),
            ("Tiếng rắc quen thuộc thực chất là do bọt khí gas trong dịch khớp bị vỡ khi khoảng cách xương giãn nở.", [
                {"spec": "concept_metaphor:CH01|Stickman demonstrates tiny nitrogen bubbles popping safely in synovial fluid.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BỌT KHÍ VỠ"},
                {"spec": "visual_diagram:none|Joint capsule diagram: Vacuum expansion -> Cavitation Bubble -> Harmless Pop.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BONG BÓNG KHÍ GAS"},
            ]),
            ("Bác sĩ Donald Unger đã tự bẻ khớp ngón tay trái suốt sáu mươi năm và chứng minh hai bàn tay hoàn toàn khỏe mạnh như nhau.", [
                {"spec": "full_scene:CH01|Dr Unger stickman displays two identical healthy hands winning Nobel Prize.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "BÁC SĨ DONALD UNGER"},
                {"spec": "macro_prop:none|An Ig Nobel medal sitting beside two identical X-ray hand scans on white canvas.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "SÁU MƯƠI NĂM THỬ NGHIỆM"},
            ]),
        ]
    ),
    (
        "Góc nhìn trực diện: Đừng xem thường vi trùng mắt thường không thấy",
        "A thoughtful hygiene philosophy consultation room on white canvas.",
        "analytical_crisp",
        "editorial_commentary",
        [
            ("Sự thật mất lòng là, việc tin vào quy tắc năm giây chỉ là cách não bộ tự lừa dối để đỡ tiếc đồ ăn.", [
                {"spec": "full_scene:CH01|Scientist delivers an uncompromising hygiene reality check to camera.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "SỰ THẬT MẤT LÒNG"},
                {"spec": "concept_metaphor:none|A blindfold placed over eyes while stepping near an invisible puddle of germs.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "TỰ LỪA DỐI BẢN THÂN"},
            ]),
            ("Đánh giá công bằng thì, hệ miễn dịch có thể chịu đựng được một vài vi khuẩn nhưng không phải là bất khả chiến bại.", [
                {"spec": "full_scene:CH01|Stickman stands behind a translucent immune shield showing microscopic cracks.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐÁNH GIÁ CÔNG BẰNG"},
                {"spec": "visual_diagram:none|A balance weighing Short-Term Snack Craving against Food Poisoning Medical Bills.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "GIỚI HẠN MIỄN DỊCH"},
            ]),
            ("Chỉ cần một bào tử vi khuẩn Salmonella hay tụ cầu vàng là đủ khiến bạn phải nhập viện cấp cứu.", [
                {"spec": "concept_metaphor:CH01|A single toxic red spore bursting causing emergency hospital alert lights.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "MẦM BỆNH SALMONELLA"},
                {"spec": "macro_prop:none|A clinical emergency medical warning sign stamped DANGER CONTAMINATION.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "NGUY HIỂM NHẬP VIỆN"},
            ]),
        ]
    ),
    (
        "Lời đồn số ba: Uống tám cốc nước mỗi ngày là bắt buộc?",
        "A hydration physiology research desk on clean white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Lời khuyên kinh điển uống đúng hai lít nước hay tám cốc mỗi ngày thực chất bắt nguồn từ một hiểu lầm năm 1945.", [
                {"spec": "full_scene:CH01|Stickman examines a vintage 1945 medical nutrition report document.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HIỂU LẦM NĂM 1945"},
                {"spec": "visual_diagram:none|Eight glasses of water lined up in a neat row crossed with an asterisk clarification.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TÁM CỐC MỖI NGÀY"},
            ]),
            ("Báo cáo ban đầu nêu rõ phần lớn lượng nước đó đã có sẵn trong canh, sữa, trái cây và rau củ quả bạn ăn.", [
                {"spec": "concept_metaphor:CH01|Stickman shows fresh watermelon, soup bowl, and oranges rich in natural water.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CÓ SẴN TRONG THỨC ĂN"},
                {"spec": "visual_diagram:none|Dietary hydration breakdown: 40% from Food Content and 60% from Direct Drinking.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CANH VÀ TRÁI CÂY"},
            ]),
            ("Cơ thể người có cơ chế báo khát cực kỳ tinh vi, bạn chỉ cần uống khi cảm thấy khát chứ không cần ép buộc thận làm việc quá tải.", [
                {"spec": "full_scene:CH01|Stickman sips water naturally listening to the internal biological thirst signal.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "LẮNG NGHE CƠ THỂ"},
                {"spec": "macro_prop:none|A clear glass tumbler filled with refreshing pure water on white background.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "UỐNG KHI THỰC SỰ KHÁT"},
            ]),
        ]
    ),
    (
        "Khoảnh khắc kết nối và đồng hành cùng kênh",
        "A curious cozy popular science study lounge on clean white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Khoa học thường thức giúp chúng ta sống khỏe mạnh hơn bằng sự hiểu biết thay vì những nỗi sợ vô căn cứ.", [
                {"spec": "full_scene:CH01|Science explainer stickman smiles warmly holding open a guidebook titled HIỂU BIẾT ĐÚNG.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KHOA HỌC THƯỜNG THỨC"},
                {"spec": "visual_diagram:none|A golden key turning in an iron lock dispelling a dark cloud of superstition.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HIỂU BIẾT ĐỂ SỐNG KHỎE"},
            ]),
            ("Nếu bạn từng nhặt đồ ăn rơi sàn lên rồi thổi phù một cái ăn tiếp, hãy lưu video này lại nhé.", [
                {"spec": "full_scene:CH01|The host gestures with gentle humor toward a bookmark ribbon emblem.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LƯU LẠI NHẮC NHỞ"},
                {"spec": "macro_prop:none|A colorful bookmark ribbon resting beside a miniature microscope figurine.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "THÓI QUEN NHÀ BẾP"},
            ]),
            ("Tiếp theo đây, chúng ta sẽ lật tẩy ba lời đồn kinh điển về giấc ngủ và não bộ người.", [
                {"spec": "concept_metaphor:CH01|The stickman points eagerly toward three mystery question doors on white canvas.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "BA LỜI ĐỒN KINH ĐIỂN"},
                {"spec": "visual_diagram:none|Three numbered doors revealing brain, sleep, and vision scientific icons.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "KHÁM PHÁ NÃO BỘ"},
            ]),
        ]
    ),
    (
        "Lời đồn số bốn: Đọc sách trong bóng tối làm hỏng mắt?",
        "An ophthalmology vision research room on clean white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Tuổi thơ của ai cũng từng bị người lớn cảnh báo: Đừng bao giờ đọc sách trong bóng tối kẻo bị cận thị mù lòa.", [
                {"spec": "full_scene:CH01|Stickman reads an open book under dim moonlight with parent pointing warning finger.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐỌC SÁCH TRONG TỐI"},
                {"spec": "visual_diagram:none|An anatomical eye cross-section showing cornea, lens, and retina projection.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LỜI DẶN TUỔI THƠ"},
            ]),
            ("Khoa học nhãn khoa khẳng định: Ánh sáng yếu chỉ làm cơ mắt mỏi tạm thời chứ không làm biến dạng nhãn cầu vĩnh viễn.", [
                {"spec": "concept_metaphor:CH01|Stickman demonstrates ciliary eye muscle contracting temporarily without damage.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "MỎI MẮT TẠM THỜI"},
                {"spec": "visual_diagram:none|Eye muscle diagram showing temporary fatigue vs permanent structural elongation.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KHÔNG GÂY CẬN THỊ"},
            ]),
            ("Thủ phạm thực sự gây bùng nổ cận thị ở trẻ em là thiếu ánh sáng mặt trời tự nhiên ngoài trời và nhìn gần quá lâu.", [
                {"spec": "full_scene:CH01|Stickman steps outside into warm bright natural sunshine smiling brightly.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "THIẾU NẮNG MẶT TRỜI"},
                {"spec": "macro_prop:none|A glowing sun emblem radiating broad spectrum natural daylight outdoors.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "ÁNH SÁNG TỰ NHIÊN"},
            ]),
        ]
    ),
    (
        "Lời đồn số năm: Chúng ta chỉ dùng mười phần trăm não bộ?",
        "A clinical neuroscience cognitive architecture studio on white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Các bộ phim điện ảnh khoa học viễn tưởng luôn rao giảng rằng con người chỉ khai thác mười phần trăm tiềm năng não.", [
                {"spec": "full_scene:CH01|Stickman watches a fictional Hollywood movie poster showing 10% brain myth.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "MƯỜI PHẦN TRĂM NÃO"},
                {"spec": "visual_diagram:none|A fictional brain gauge lit up only one-tenth with 90% in total darkness.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ẢO TƯỞNG ĐIỆN ẢNH"},
            ]),
            ("Kỹ thuật chụp cộng hưởng từ chức năng fMRI chứng minh toàn bộ các vùng não đều hoạt động liên tục suốt ngày đêm.", [
                {"spec": "concept_metaphor:CH01|Neuroscientist demonstrates fMRI brain scan active across all lobes simultaneously.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HOẠT ĐỘNG TOÀN BỘ"},
                {"spec": "visual_diagram:none|fMRI functional scan showing neural activity distributed across sensory, motor, and cognitive zones.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CHỤP fMRI"},
            ]),
            ("Ngay cả khi bạn đang ngủ say, não bộ vẫn tiêu tốn hai mươi phần trăm tổng năng lượng cơ thể để xử lý ký ức.", [
                {"spec": "full_scene:CH01|Stickman sleeps peacefully while brain engine processes memories efficiently.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "XỬ LÝ KÝ ỨC KHI NGỦ"},
                {"spec": "macro_prop:none|A biological battery icon showing constant 20% metabolic consumption by brain.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "20% NĂNG LƯỢNG"},
            ]),
        ]
    ),
    (
        "Lời đồn số sáu: Ăn đêm làm tăng cân gấp đôi ban ngày?",
        "A nutritional metabolic rate evaluation center on white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Nhiều người tin rằng một bát cơm ăn sau tám giờ tối sẽ tự động biến thành mỡ thừa tích tụ vào bụng.", [
                {"spec": "full_scene:CH01|Stickman looks nervously at a steaming rice bowl past eight in evening.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĂN ĐÊM TĂNG CÂN?"},
                {"spec": "visual_diagram:none|A clock face at 20:00 pointing warning red hand at a dinner bowl.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "SAU TÁM GIỜ TỐI"},
            ]),
            ("Định luật nhiệt động lực học khẳng định: Lượng calo là lượng calo, bất kể bạn nạp vào buổi sáng hay nửa đêm.", [
                {"spec": "concept_metaphor:CH01|Nutritionist weighs a calorie block showing identical weight morning and night.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "ĐỊNH LUẬT CALO"},
                {"spec": "visual_diagram:none|Caloric energy balance equation: Total Calories In versus Total Calories Out.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "NHIỆT ĐỘNG LỰC HỌC"},
            ]),
            ("Lý do ăn đêm khiến bạn tăng cân là vì chúng ta hay ăn vặt vô thức đồ ngọt và đồ chiên rán trước màn hình tivi.", [
                {"spec": "full_scene:CH01|Stickman watches television mindlessly munching potato chips in darkness.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "ĂN VẶT VÔ THỨC"},
                {"spec": "macro_prop:none|A packet of snacks beside a glowing television screen on clean white canvas.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "MỚ CHIÊN RÁN"},
            ]),
        ]
    ),
    (
        "Bình luận về tư duy phản biện trong chăm sóc sức khỏe",
        "A critical thinking science evaluation room on clean white canvas.",
        "narrative_warm",
        "editorial_commentary",
        [
            ("Nhìn thẳng vào thực tế thì, con người rất thích tin vào những câu chuyện truyền miệng ly kỳ hơn sự thật khô khan.", [
                {"spec": "full_scene:CH01|Scientist speaks with engaging thoughtfulness leaning forward to camera.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "NHÌN THẲNG VÀO THỰC TẾ"},
                {"spec": "visual_diagram:none|A scale separating Catchy Folk Myths from Rigorous Scientific Controlled Studies.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "TƯ DUY PHẢN BIỆN"},
            ]),
            ("Sự lười kiểm chứng thông tin khiến chúng ta dễ dàng áp dụng những mẹo vặt phản khoa học vào đời sống mỗi ngày.", [
                {"spec": "full_scene:CH01|Stickman walks past a library archive choosing an unverified rumor pamphlet instead.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "LƯỜI KIỂM CHỨNG"},
                {"spec": "concept_metaphor:none|A compass needle pulled astray by a false metallic rumor magnet on white paper.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "MẸO PHẢN KHOA HỌC"},
            ]),
            ("Trang bị tư duy phản biện dựa trên thực nghiệm khoa học chính là liều vắc-xin tốt nhất cho sức khỏe gia đình bạn.", [
                {"spec": "concept_metaphor:CH01|Stickman holds a gleaming scientific microscope shielding a healthy happy family.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "VẮC-XIN TRI THỨC"},
                {"spec": "macro_prop:none|A glowing crystal microscope resting triumphantly on a stack of verified science papers.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "BẢO VỆ GIA ĐÌNH"},
            ]),
        ]
    ),
    (
        "Quy tắc ngón tay cái xử lý đồ ăn rơi",
        "A practical kitchen food safety inspection station on white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Để bảo vệ sức khỏe hệ tiêu hóa, hãy ghi nhớ quy tắc xử lý ba bước cực kỳ đơn giản này.", [
                {"spec": "full_scene:CH01|Stickman writes three clean food safety guidelines onto kitchen board.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "QUY TẮC BA BƯỚC"},
                {"spec": "visual_diagram:none|Three kitchen safety pillars: Đánh Giá Độ Ẩm, Nhận Diện Bề Mặt, Dứt Khoát Bỏ Rác.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "XỬ LÝ ĐỒ ĂN RƠI"},
            ]),
            ("Bước một: Nếu thức ăn có bề mặt ẩm ướt hoặc rơi ở nơi công cộng, hãy bỏ sọt rác không chút do dự.", [
                {"spec": "full_scene:CH01|Stickman calmly tosses dropped moist melon into waste bin without regret.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "BỎ SỌT RÁC NGAY"},
                {"spec": "visual_diagram:none|Moist Food Icon with direct arrow leading to Covered Clean Waste Bin.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "ĐỒ ĂN ẨM ƯỚT"},
            ]),
            ("Bước hai: Với đồ khô rơi trên sàn nhà riêng vừa lau sạch, bạn có thể rửa lại bằng nước sôi hoặc gọt bỏ lớp vỏ ngoài.", [
                {"spec": "concept_metaphor:CH01|Stickman rinses a firm apple under boiling hot tap water on kitchen sink.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "RỬA NƯỚC SÔI"},
                {"spec": "macro_prop:none|A paring knife slicing away the outer peel of a dropped fruit cleanly.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "GỌT BỎ LỚP VỎ"},
            ]),
        ]
    ),
    (
        "Kế hoạch hành động bảo vệ vệ sinh nhà bếp",
        "A clean hygienic kitchen maintenance zone on white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Nhiều người nghĩ bồn cầu là nơi bẩn nhất, nhưng thực tế miếng bọt biển rửa bát chứa lượng vi khuẩn gấp hai trăm ngàn lần.", [
                {"spec": "full_scene:CH01|Stickman points to a yellow dishwashing sponge under ultraviolet inspection.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "MIẾNG BỌT BIỂN RỬA BÁT"},
                {"spec": "visual_diagram:none|Microbial count comparison: Kitchen Sponge 200,000x denser than Toilet Seat.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "GẤP 200 NGÀN LẦN"},
            ]),
            ("Hãy thay miếng rửa bát định kỳ hai tuần một lần và quay nó trong lò vi sóng một phút để khử trùng.", [
                {"spec": "concept_metaphor:CH01|Stickman places a damp sponge into microwave setting timer to sixty seconds.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "KHỬ TRÙNG VI SÓNG"},
                {"spec": "still_life:none|A clean fresh yellow sponge steaming lightly after microwave heat sterilization.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "MỘT PHÚT KHỬ TRÙNG"},
            ]),
            ("Vệ sinh mặt bếp và thớt thái đồ chín riêng biệt sẽ chặn đứng chín mươi phần trăm nguy cơ ngộ độc thức ăn.", [
                {"spec": "full_scene:CH01|Stickman prepares food using two distinctly colored cutting boards for raw and cooked.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "THỚT CHÍN THỚT SỐNG"},
                {"spec": "macro_prop:none|Two cutting boards: Green for Vegetables and Red for Raw Meats side by side.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "CHẶN ĐỨNG NGỘ ĐỘC"},
            ]),
        ]
    ),
    (
        "Bài test 30 giây rà soát thói quen ăn uống",
        "A healthy lifestyle self-audit room on pure white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Hãy dành ra ba mươi giây để tự điểm lại xem bản thân và người thân trong nhà đang mắc phải thói quen nào.", [
                {"spec": "full_scene:CH01|Stickman holds a self-checklist reviewing daily domestic hygiene habits.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BÀI TEST 30 GIÂY"},
                {"spec": "visual_diagram:none|Checklist showing: Ăn đồ rơi sàn? Dùng chung thớt? Không thay miếng rửa bát?", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐIỂM LẠI THÓI QUEN"},
            ]),
            ("Thay đổi một thói quen nhỏ hôm nay sẽ mang lại sự an tâm và sức khỏe dồi dào cho cả tổ ấm dài lâu.", [
                {"spec": "concept_metaphor:CH01|Stickman plants a small green sprout that grows into a protective health canopy.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "THÓI QUEN NHỎ"},
                {"spec": "visual_diagram:none|A small daily hygiene habit multiplying into lifelong immune protection on white paper.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "SỨC KHỎE DỒI DÀO"},
            ]),
            ("Sự hiểu biết khoa học đúng đắn chính là món quà quý giá nhất bạn có thể trao tặng cho những người thân yêu.", [
                {"spec": "full_scene:CH01|Stickman presents a glowing ribbon-wrapped science gift box to family.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "MÓN QUÀ TRI THỨC"},
                {"spec": "macro_prop:none|A golden gift box radiating warm sparkles of knowledge across clean white canvas.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TRAO TẶNG NGƯỜI THÂN"},
            ]),
        ]
    ),
    (
        "Lời kết và chiếc cầu nối cho cộng đồng yêu khoa học",
        "An inspiring open science discovery studio on pure white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Thế giới tự nhiên luôn ẩn chứa những sự thật bất ngờ đằng sau những hiện tượng tưởng chừng quen thuộc.", [
                {"spec": "full_scene:CH01|Science explainer stickman smiles warmly standing before an open cosmos map.", "tempo": "fast", "narrative_situation": "editorial_commentary", "emphasis_text": "SỰ THẬT BẤT NGỜ"},
                {"spec": "visual_diagram:none|A sparkling magnifying glass revealing wonders of everyday science on white paper.", "tempo": "fast", "narrative_situation": "editorial_commentary", "emphasis_text": "THẾ GIỚI TỰ NHIÊN"},
            ]),
            ("Bạn từng tin vào lời đồn nào nhất trong sáu điều trên, hãy chia sẻ trải nghiệm dưới bình luận nhé.", [
                {"spec": "full_scene:CH01|The host gestures with friendly warmth toward conversational comments below.", "tempo": "normal", "narrative_situation": "editorial_commentary", "emphasis_text": "CHIA SẺ DƯỚI BÌNH LUẬN"},
                {"spec": "macro_prop:none|A speech dialogue box displaying an animated question mark with smiling face.", "tempo": "normal", "narrative_situation": "editorial_commentary", "emphasis_text": "CÙNG THẢO LUẬN"},
            ]),
            ("Đừng ngần ngại để lại câu hỏi về những hiện tượng kỳ lạ để chúng ta cùng giải mã trong tập tiếp theo nhé.", [
                {"spec": "full_scene:CH01|Stickman waves hand enthusiastically greeting viewers until next episode.", "tempo": "normal", "narrative_situation": "editorial_commentary", "emphasis_text": "HẸN GẶP TẬP TIẾP THEO"},
                {"spec": "visual_diagram:none|An open book of curious phenomena waiting for viewer input on clean white canvas.", "tempo": "normal", "narrative_situation": "editorial_commentary", "emphasis_text": "ỦA SAO VẬY?"},
            ]),
        ]
    ),
]

SHORT_STORY_ROWS = [
    (
        "Mẩu thức ăn rơi sàn và câu thần chú 5 giây",
        "A bright kitchen food drop scene on pure white canvas.",
        "narrative_warm",
        "curiosity_hook",
        [
            ("Vừa làm rơi miếng xúc xích xuống đất, bạn liền nhặt lên và hô to Chưa tới năm giây?", [
                {"spec": "full_scene:CH01|Stickman snatches sausage slice off tile shouting the five second rule.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "CHƯA TỚI 5 GIÂY"},
                {"spec": "visual_diagram:none|A comic speech bubble shouting NĂM GIÂY VẪN SẠCH over dropped sausage.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "CÂU THẦN CHÚ"},
            ]),
            ("Liệu vi khuẩn có thực sự đứng im chờ bạn đếm hết năm giây mới chịu nhảy vào đồ ăn?", [
                {"spec": "full_scene:CH01|Stickman holds dropped food squinting at invisible microbes with suspicion.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "ĐỨNG IM CHỜ BẠN?"},
                {"spec": "still_life:none|A stop-timer counting down seconds next to dropped food on white ground.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "VI KHUẨN BẤM GIỜ?"},
                {"spec": "concept_metaphor:none|A tiny cartoon bacteria holding a wristwatch waiting patiently to jump.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "TRÒ HỀ DÂN GIAN"},
            ]),
        ]
    ),
    (
        "Thực nghiệm vi sinh học đo bằng mili-giây",
        "A microbiology laboratory analysis chamber on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Thực nghiệm của Đại học Rutgers chứng minh: Vi khuẩn bám dính ngay trong 0.01 giây đầu tiên.", [
                {"spec": "full_scene:CH01|Microbiologist points to digital millisecond counter reading 0.01 seconds.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "0.01 GIÂY ĐẦU TIÊN"},
                {"spec": "visual_diagram:none|High speed camera diagram showing bacterial jump at initial point of contact.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "BÁM DÍNH TỨC KHẮC"},
            ]),
            ("Chúng không cần chạy bộ, mà lợi dụng độ ẩm chất lỏng để trượt thẳng vào bề mặt thức ăn.", [
                {"spec": "concept_metaphor:CH01|Stickman demonstrates liquid moisture sliding germs across boundary.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "LỢI DỤNG ĐỘ ẨM"},
                {"spec": "visual_diagram:none|Microscopic liquid layer pulling colonies into food pore spaces instantly.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "TRƯỢT VÀO THỨC ĂN"},
                {"spec": "still_life:none|A wet food droplet showing microscopic bacterial migration under lens.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "LÂY NHIỄM CẤP TỐC"},
            ]),
        ]
    ),
    (
        "Bản chất nguy hiểm của thói quen thổi bụi",
        "A microbiology hazard demonstration station on white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Hành động thổi phù một cái chỉ làm tăng thêm nước bọt và vi khuẩn từ khoang miệng của bạn.", [
                {"spec": "full_scene:CH01|Stickman blows breath on snack sending tiny droplet aerosol spray forward.", "tempo": "fast", "narrative_situation": "editorial_commentary", "emphasis_text": "THỔI PHỦI VÔ NGHĨA"},
                {"spec": "visual_diagram:none|Aerosol spray graphic adding oral saliva droplets on top of floor dust.", "tempo": "fast", "narrative_situation": "editorial_commentary", "emphasis_text": "THÊM NƯỚC BỌT"},
            ]),
            ("Một nền nhà bếp trông có vẻ sáng bóng thực chất chứa hàng vạn bào tử nấm mốc và vi khuẩn E coli.", [
                {"spec": "concept_metaphor:CH01|A UV light reveals dense hidden bacterial colony patterns across clean floor.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "HÀNG VẠN BÀO TỬ"},
                {"spec": "visual_diagram:none|UV fluorescence showing invisible bacterial colonies flourishing on glossy tile.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "VI KHUẨN E COLI"},
                {"spec": "macro_prop:none|A clinical petri dish cultured from a single kitchen tile swab test.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "Ổ KHUẨN VÔ HÌNH"},
            ]),
        ]
    ),
    (
        "Đỉnh cao trào bỏ lửng và câu hỏi then chốt",
        "A dramatic high-stakes kitchen mystery spotlight on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Chỉ cần một lần bất cẩn nhặt ăn đồ bẩn, độc tố vi khuẩn có thể đánh sập hệ tiêu hóa của bạn.", [
                {"spec": "full_scene:CH01|Stickman clutches stomach in sudden acute gastrointestinal distress.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "ĐÁNH SẬP TIÊU HÓA"},
                {"spec": "visual_diagram:none|An acute bacterial stomach pain symptom diagram on clean white canvas.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "NGUY CƠ NGỘ ĐỘC"},
            ]),
            ("Thảm sàn nhà hay sàn gạch bóng loáng, đâu mới là môi trường nuôi cấy mầm bệnh nguy hiểm hơn?", [
                {"spec": "concept_metaphor:CH01|Stickman compares a tile swatch against carpet swatch in dramatic lighting.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "THẢM HAY GẠCH BẨN HƠN?"},
                {"spec": "visual_diagram:none|A dual challenge scale: Ceramic Tile vs Carpet Fiber contamination dynamics.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "MÔI TRƯỜNG NGUY HIỂM"},
                {"spec": "still_life:none|Two swab samples labeled Surface A and Surface B awaiting laboratory culture.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "MẦM BỆNH ẨN NẤP"},
            ]),
            ("Đúng lúc bạn nghĩ sàn nhà vừa lau bằng nước tẩy là sạch thì bí mật vi khuẩn kháng thuốc ẩn nấp ra sao?", [
                {"spec": "concept_metaphor:CH01|Stickman stands before a locked laboratory chamber with a giant glowing question mark.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "VI KHUẨN KHÁNG THUỐC"},
                {"spec": "visual_diagram:none|A giant red question mark hovering above chemical disinfectant bottle.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "BÍ MẬT KINH HOÀNG"},
            ]),
        ]
    ),
    (
        "Chuyển phễu sang bản Full và Close CTA",
        "A bright inspiring science explainer studio on clean white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Xem video bản dài bên dưới để bóc trần 5 ngụy khoa học về cơ thể nhé.", [
                {"spec": "full_scene:CH01|Stickman points enthusiastically down toward the linked video preview card.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "XEM BẢN DÀI"},
                {"spec": "visual_diagram:none|A bold directional arrow pointing down to the related full-length video badge.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "5 NGỤY KHOA HỌC"},
            ]),
            ("Lưu lại ngay để bảo vệ đường tiêu hóa của cả gia đình bạn nhé.", [
                {"spec": "full_scene:CH01|Stickman smiles warmly waving hand beside channel emblem on white canvas.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "LƯU LẠI BẢO VỆ"},
                {"spec": "macro_prop:none|A glowing green shield protecting a healthy family on pure white background.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "BẢO VỆ TIÊU HÓA"},
            ]),
        ]
    ),
]
