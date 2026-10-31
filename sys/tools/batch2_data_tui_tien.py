"""
Batch 2 Topic Blueprint and Story Rows for Channel: tui_tien
Niche: Quản Lý Tài Chính Cá Nhân, Tâm Lý Học Tiền Bạc & Đầu Tư Thông Minh
Topic: Bẫy Mua Trước Trả Sau (BNPL): Ảo Tưởng Giàu Sang Đốt Cháy Ví Tiền
"""

from typing import Any, Dict, List, Tuple

CHANNEL_ID = "tui_tien"
CHANNEL_SLUG = "tui-tien"

LONG_TOPIC = "Bẫy Mua Trước Trả Sau: Ảo Tưởng Giàu Sang Đang Đốt Cháy Ví Tiền Của Bạn"
SHORT_TOPIC = "Vì Sao Mua Trước Trả Sau Khiến Bạn Nghèo Đi Mà Không Biết?"
LONG_AUDIENCE = "Người trẻ đi làm, dân văn phòng hay mua sắm online trên sàn thương mại điện tử"
SHORT_AUDIENCE = "Gen Z và nhân viên văn phòng nghiện chốt đơn trả góp không lãi suất"

LONG_GOAL = "Bóc trần cái bẫy tâm lý tách rời nỗi đau thanh toán của mô hình BNPL và hướng dẫn quy tắc 72 giờ phong tỏa ví tiền"
SHORT_GOAL = "Cảnh báo cơ chế ảo giác giàu sang của dịch vụ mua trước trả sau và dẫn dắt người xem vào video dài bằng câu hỏi then chốt"

LONG_EDITORIAL_STANCE = {
    "myth_debunked": "Mua trước trả sau không lãi suất là đòn bẩy tài chính thông minh giúp tối ưu dòng tiền nhàn rỗi.",
    "why_generic_advice_fails": "Các ứng dụng tài chính luôn quảng cáo lãi suất không phần trăm nhưng cố tình giấu nhẹm phí phạt trễ hạn cắt cổ và bẫy chi tiêu bốc đồng.",
    "channel_verdict": "Sự thật mất lòng là nếu bạn không đủ tiền mặt mua đứt một món đồ tiêu sản thì bạn hoàn toàn không có khả năng chi trả cho nó.",
    "tradeoff_or_blindspot": "Tự tay thanh toán bằng tiền mặt tạo ra nỗi đau ví tiền nhưng lại là tấm khiên bảo vệ tương lai tài chính vững chắc nhất.",
}

LONG_ACTIONABLE_VALUE = {
    "core_mechanism": "Cơ chế tách rời nỗi đau thanh toán làm tê liệt phản xạ hối tiếc và quy tắc lãi mẹ đẻ lãi con từ phí phạt ẩn.",
    "practical_rule_of_thumb": "Quy tắc bảy mươi hai giờ: chuyển toàn bộ món hàng trả góp vào danh sách chờ và tự hỏi ba câu kiểm tra khả năng tài chính.",
    "real_world_scenario": "Một bạn trẻ hủy toàn bộ tính năng trả sau trên ba app mua sắm để thoát khỏi vòng xoáy nợ thẻ mỗi kỳ lương về.",
}

SHORT_EDITORIAL_STANCE = {
    "myth_debunked": "Mua trước trả sau chia nhỏ số tiền chỉ vài trăm nghìn mỗi tháng là cách mua sắm tiện lợi và không tốn kém.",
    "why_generic_advice_fails": "Lời khuyên tận dụng trả góp không đồng chỉ khiến bạn rơi vào bẫy tâm lý mua nhiều hơn năm mươi phần trăm nhu cầu thực.",
    "channel_verdict": "Sự thật mất lòng là các công ty trả sau không kiếm tiền từ người kỷ luật mà kiếm tiền từ những lần bạn lỡ hạn thanh toán.",
    "tradeoff_or_blindspot": "Cắt bỏ các hạn mức tín dụng trả sau tạo cảm giác gò bó ban đầu nhưng giữ cho bạn tự do tài chính trọn đời.",
}

SHORT_ACTIONABLE_VALUE = {
    "core_mechanism": "Hiệu ứng tê liệt nỗi đau tiền mặt khiến não bộ lầm tưởng mình đang sở hữu món hàng miễn phí.",
    "practical_rule_of_thumb": "Quy tắc mua đứt hai lần: nếu ví tiền không đủ mua hai cái cùng lúc thì tuyệt đối không bấm nút chốt đơn.",
    "real_world_scenario": "Chuyển chiếc tai nghe hai triệu khỏi giỏ hàng trả sau để tiết kiệm đủ tiền mặt sau hai tháng làm việc.",
}

LONG_SOURCES = [
    {
        "id": "SRC01",
        "title": "Báo Cáo Nghiên Cứu Hành Vi Người Tiêu Dùng Và Tín Dụng Trả Sau",
        "reference": "Cục Bảo Vệ Tài Chính Người Tiêu Dùng CFPB (2023). Tác Động Của Mô Hình Mua Trước Trả Sau Đến Giới Trẻ.",
        "facts": [
            "Người dùng dịch vụ mua trước trả sau có xu hướng chi tiêu nhiều hơn bốn mươi lăm phần trăm so với dùng tiền mặt.",
            "Gần một phần ba người dùng trẻ từng bị phạt phí trễ hạn hoặc ghi nhận nợ xấu trên hệ thống chấm điểm tín dụng.",
        ],
    }
]

SHORT_SOURCES = [
    {
        "id": "SRC01",
        "title": "Nghiên Cứu Tâm Lý Học Kinh Tế Về Nỗi Đau Thanh Toán",
        "reference": "Đại Học MIT (2022). Tác Động Của Giao Dịch Không Tiền Mặt Đến Quyết Định Tiêu Dùng.",
        "facts": [
            "Tách rời thời điểm nhận hàng và thời điểm trả tiền làm suy giảm sáu mươi phần trăm phản xạ phòng thủ của não.",
        ],
    }
]

LONG_PACKAGING = {
    "youtube_title": "Bẫy Mua Trước Trả Sau: Ảo Tưởng Giàu Sang Đốt Cháy Ví Tiền",
    "visual_hook": "Người que cầm chiếc điện thoại mới tinh nhưng chân bị xích vào hóa đơn nợ trả góp khổng lồ",
    "text_overlay": "BẪY TRẢ SAU",
    "contrast_pair": "Ảo giác chỉ trả 200k/tháng vs Núi nợ tích tụ bóp nghẹt lương tháng",
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": [
        "tui tien",
        "mua truoc tra sau",
        "bnpl",
        "bay tai chinh",
        "quan ly tai chinh ca nhan",
    ],
    "cta_plan": {
        "mid_cta": "Nếu bạn từng bất ngờ vì tổng số tiền trả góp hàng tháng vượt quá nửa tháng lương, hãy lưu video này lại nhé.",
        "close": "Bạn đang trích bao nhiêu phần trăm lương cho trả góp, hãy cùng tính nhẩm dưới phần bình luận nhé.",
        "endcard_text": "TÚI TIỀN",
    },
}

SHORT_PACKAGING = {
    "youtube_title": "Vì Sao Mua Trước Trả Sau Khiến Bạn Nghèo Đi Không Biết?",
    "visual_hook": "Người que bấm nút mua trả sau nở nụ cười sung sướng nhưng ví tiền phía sau bốc cháy",
    "text_overlay": "NGHÈO KHÔNG BIẾT",
    "contrast_pair": "Cảm giác chốt đơn không mất tiền vs Núi phí phạt trễ hạn chực chờ",
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": [
        "tui tien",
        "mua truoc tra sau",
        "meo tai chinh",
        "shorts",
    ],
    "cta_plan": {
        "cliffhanger_peak": "Đúng lúc bạn nghĩ mình quản lý nợ hoàn hảo thì chỉ một cú trễ hạn hai ngày sẽ kích hoạt bẫy phí phạt ra sao?",
        "bridge": "Xem video bản dài bên dưới để lấy quy tắc 72 giờ khóa chặt ví tiền nhé.",
        "close": "Lưu lại ngay để bảo vệ đồng lương mồ hôi nước mắt bạn nhé.",
        "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
    },
}

LONG_STORY_ROWS = [
    (
        "Cảm giác chiến thắng khi chốt đơn 0 đồng",
        "A bustling online shopping interface on crisp white canvas.",
        "narrative_warm",
        "curiosity_hook",
        [
            ("Chỉ cần một cú chạm màn hình, món đồ hiệu sang chảnh đã sẵn sàng giao tới tận cửa nhà bạn.", [
                {"spec": "full_scene:CH01|The stickman taps smartphone screen with joyful radiant expression.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "MỘT CÚ CHẠM"},
                {"spec": "macro_prop:none|A gleaming luxury delivery box wrapped in silk ribbon on white ground.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "GIAO TẬN CỬA"},
            ]),
            ("Tài khoản ngân hàng của bạn không hề trừ một đồng nào, ví tiền vẫn nguyên vẹn như chưa từng mua.", [
                {"spec": "full_scene:CH01|Stickman checks digital bank balance showing untouched savings number.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "KHÔNG TRỪ MỘT ĐỒNG"},
                {"spec": "visual_diagram:none|A bank balance display reading ZERO DOLLARS DEDUCTED with green checkmark.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "VÍ VẪN NGUYÊN VẸN"},
            ]),
            ("Cảm giác sung sướng tột độ đó chính là miếng pho mát thơm ngon trong chiếc bẫy chuột tài chính mang tên BNPL.", [
                {"spec": "concept_metaphor:CH01|A tasty slice of cheese resting upon a polished steel spring mousetrap.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "MIẾNG PHO MÁT"},
                {"spec": "visual_diagram:none|A bold typography banner reading BẪY MUA TRƯỚC TRẢ SAU on pure white canvas.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "CHIẾC BẪY CHUỘT"},
            ]),
        ]
    ),
    (
        "Bóc trần sự bùng nổ của dịch vụ mua trước trả sau",
        "A modern fintech commerce research hall on clean white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Khắp các sàn thương mại điện tử hôm nay, nút thanh toán trả sau xuất hiện ngập tràn mời gọi.", [
                {"spec": "full_scene:CH01|Fintech researcher points to a massive online checkout screen full of BNPL badges.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "NGẬP TRÀN MỜI GỌI"},
                {"spec": "visual_diagram:none|A smartphone display showing prominent Buy Now Pay Later buttons highlighted in neon.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "SÀN THƯƠNG MẠI"},
            ]),
            ("Chia nhỏ món đồ năm triệu thành năm kỳ trả góp, mỗi kỳ chỉ một triệu đồng nghe có vẻ vô hại.", [
                {"spec": "concept_metaphor:CH01|Stickman slices a large payment block into five tiny manageable slices.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CHIA NHỎ NĂM KỲ"},
                {"spec": "visual_diagram:none|Payment decomposition graphic: 5 Million broken into 1 Million monthly steps.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "NGHE VÔ HẠI"},
            ]),
            ("Báo cáo của Cục Quản Lý Tài Chính CFPB cho thấy người dùng BNPL chi tiêu vượt trội bốn mươi lăm phần trăm.", [
                {"spec": "full_scene:CH01|The analyst presents a statistical growth chart comparing spending habits.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "BỐN MƯƠI LĂM PHẦN TRĂM"},
                {"spec": "visual_diagram:none|A comparative bar chart showing Cash Shoppers versus BNPL Users spending volume.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "BÁO CÁO CFPB"},
            ]),
        ]
    ),
    (
        "Tâm lý học thần kinh: Nỗi đau thanh toán bị vô hiệu hóa",
        "A neuroscience cognitive psychology laboratory on clean white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Khi bạn rút tiền mặt trong ví ra đếm, não bộ sẽ gửi tín hiệu cảnh báo đau đớn thực thể.", [
                {"spec": "full_scene:CH01|Stickman grimaces slightly while handing crisp physical banknotes over a counter.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "NỖI ĐAU ĐẾM TIỀN"},
                {"spec": "still_life:none|A fan of physical banknotes leaving an open leather wallet on white table.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "TIỀN MẶT RỜI VÍ"},
            ]),
            ("Giáo sư George Loewenstein tại Đại học Carnegie Mellon gọi hiện tượng này là Pain of Paying.", [
                {"spec": "concept_metaphor:CH01|The scientist highlights the brain insula region registering financial loss pain.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "PAIN OF PAYING"},
                {"spec": "visual_diagram:none|A neural diagram showing the insula brain region activating during cash payments.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "VÙNG ĐAU VÍ TIỀN"},
            ]),
            ("Mô hình trả sau đã xảo quyệt chặt đứt mối liên kết giữa việc hưởng thụ và nỗi đau trả tiền.", [
                {"spec": "full_scene:CH01|A sharp cleaver cuts the rope connecting immediate pleasure to future bill.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "CHẶT ĐỨT MỐI LIÊN KẾT"},
                {"spec": "visual_diagram:none|Broken link graphic separating Immediate Dopamine from Delayed Invoice.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "VÔ HIỆU HÓA PHÒNG THỦ"},
            ]),
        ]
    ),
    (
        "Ảo giác vi mô: Căn bệnh ung thư tài chính ngầm",
        "A microscopic debt analysis board on pure white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Bởi vì mỗi khoản trừ nợ định kỳ chỉ vài chục đến vài trăm nghìn, bạn thấy nó quá nhỏ bé.", [
                {"spec": "full_scene:CH01|Stickman looks casually at tiny bill slips thinking they are completely harmless.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "QUÁ NHỎ BÉ"},
                {"spec": "visual_diagram:none|Scattered tiny payment slips of 150k, 200k, and 300k on white background.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ẢO GIÁC VI MÔ"},
            ]),
            ("Một chiếc áo thun hai trăm nghìn, một đôi giày ba trăm nghìn, một bữa ăn sang bốn trăm nghìn.", [
                {"spec": "concept_metaphor:CH01|Stickman stacks three shopping boxes casually onto an arm balance.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "NHIỀU MÓN LẺ"},
                {"spec": "still_life:none|A stylish polo shirt, running sneakers, and gourmet restaurant ticket grouped together.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "CHI TIÊU RẢI RÁC"},
            ]),
            ("Khi cộng dồn mười khoản trả sau lại, chúng biến thành một con quái vật nuốt chửng toàn bộ tiền lương.", [
                {"spec": "full_scene:CH01|Stickman recoils in shock as small slips merge into a gigantic invoice monster.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "QUÁI VẬT HÓA ĐƠN"},
                {"spec": "visual_diagram:none|Summation arrow showing 10 small payments merging into a crushing monthly total.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "NUỐT CHỬNG LƯƠNG"},
            ]),
        ]
    ),
    (
        "Khuất tất đằng sau lời hứa không phần trăm lãi suất",
        "A forensic financial statement auditing desk on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Bạn nghĩ các công ty công nghệ mở dịch vụ mua trước trả sau miễn phí để làm từ thiện ư?", [
                {"spec": "full_scene:CH01|Analyst stickman holds a magnifying glass over a deceptive marketing poster.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "LÀM TỪ THIỆN Ư?"},
                {"spec": "visual_diagram:none|A shiny gift box with a hidden microscopic contractual hook attached.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "LỜI HỨA LÃI 0%"},
            ]),
            ("Nguồn thu khổng lồ của họ đến từ hai túi: phí chiết khấu từ người bán và phí phạt trễ hạn từ bạn.", [
                {"spec": "concept_metaphor:CH01|The fintech company taps two separate coin channels flowing steadily into vault.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HAI NGUỒN THU"},
                {"spec": "visual_diagram:none|Revenue flow diagram: Merchant Discount Fee plus Consumer Late Penalty Fees.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "PHÍ PHẠT TRỄ HẠN"},
            ]),
            ("Chỉ cần bạn quên thanh toán đúng hạn một ngày, mức phí phạt và lãi suất phạt có thể lên tới ba mươi phần trăm.", [
                {"spec": "full_scene:CH01|A sudden red penalty stamp slams down onto an overdue payment notification.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "LÃI PHẠT CẮT CỔ"},
                {"spec": "macro_prop:none|A heavy red stamp printing LATE PENALTY FEE onto a calendar date.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "QUÊN MỘT NGÀY"},
            ]),
        ]
    ),
    (
        "Góc nhìn trực diện: Sự thật cay đắng về khả năng chi trả",
        "A stark reality check discussion chamber on clean white canvas.",
        "analytical_crisp",
        "editorial_commentary",
        [
            ("Sự thật mất lòng là, nếu bạn phải chia nhỏ sáu đợt thanh toán cho một đôi giày, bạn vốn dĩ chưa thể sở hữu nó.", [
                {"spec": "full_scene:CH01|Financial mentor delivers a blunt unvarnished truth directly to camera.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "SỰ THẬT MẤT LÒNG"},
                {"spec": "concept_metaphor:none|A luxury shoe balanced on a rickety three-legged stool that collapses immediately.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "KHÔNG ĐỦ TIỀN MUA"},
            ]),
            ("Đánh giá công bằng thì, việc mua trả sau cho tiêu sản chỉ là cách bạn vay mượn tương lai để mua sĩ diện hiện tại.", [
                {"spec": "full_scene:CH01|Stickman parades in fancy outfit while a dark shadow of future debt trails behind.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐÁNH GIÁ CÔNG BẰNG"},
                {"spec": "visual_diagram:none|A stark comparison between Solid Wealth Ownership and Fragile Debt Vanity.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "VAY MƯỢN TƯƠNG LAI"},
            ]),
            ("Bạn đang bán rẻ sự tự do và an toàn tài chính của tháng sau chỉ để nhận lấy vài phút thỏa mãn hão huyền.", [
                {"spec": "concept_metaphor:CH01|Stickman trades a pouch of golden future freedom for a fleeting burst of bubbles.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "BÁN RẺ TỰ DO"},
                {"spec": "macro_prop:none|A fragile soap bubble bursting in midair beside an empty financial vault.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "THỎA MÃN HÃO HUYỀN"},
            ]),
        ]
    ),
    (
        "Vết nhơ điểm tín dụng và hậu quả khôn lường",
        "A formal credit rating bureau archive on clean white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Nhiều người trẻ ngây thơ nghĩ rằng vài trăm nghìn nợ app mua sắm không ai thèm để ý truy thu.", [
                {"spec": "full_scene:CH01|Stickman shrugs dismissively discarding a tiny overdue payment reminder letter.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "NGÂY THƠ CHỦ QUAN"},
                {"spec": "visual_diagram:none|A small payment slip thrown into wastebasket while a database records it in red.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TRUY THU TÍN DỤNG"},
            ]),
            ("Thực tế là các công ty BNPL đều đã liên kết dữ liệu với Trung tâm Thông tin Tín dụng Quốc gia CIC.", [
                {"spec": "concept_metaphor:CH01|The analyst displays a central database server recording national credit scores.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "DỮ LIỆU CIC"},
                {"spec": "visual_diagram:none|A centralized financial server network lighting up credit history records.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TRUNG TÂM CIC"},
            ]),
            ("Một món nợ quá hạn một trăm nghìn bị bỏ quên có thể khóa chặt cánh cửa vay mua nhà mua xe của bạn sau này.", [
                {"spec": "full_scene:CH01|Stickman attempts to push open a bank loan door but finds it locked by a red padlock.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "KHÓA CỬA VAY VỐN"},
                {"spec": "macro_prop:none|A heavy steel bank vault door securely padlocked with a red BAD CREDIT tag.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "HẬU QUẢ DÀI LÂU"},
            ]),
        ]
    ),
    (
        "Khoảnh khắc kết nối và đồng hành cùng kênh",
        "A supportive personal financial coaching lounge on clean white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Bảo vệ ví tiền và tương lai tự chủ tài chính là hành trình cần sự tỉnh táo và hiểu biết sâu sắc.", [
                {"spec": "full_scene:CH01|Financial mentor smiles warmly holding a clear roadmap to debt-free living.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TỰ CHỦ TÀI CHÍNH"},
                {"spec": "visual_diagram:none|A solid brick foundation of savings supporting a thriving green money tree.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BẢO VỆ VÍ TIỀN"},
            ]),
            ("Nếu bạn từng bất ngờ vì tổng số tiền trả góp hàng tháng vượt quá nửa tháng lương, hãy lưu video này lại nhé.", [
                {"spec": "full_scene:CH01|The host gestures with gentle care toward a bookmark ribbon icon.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LƯU LẠI RÀ SOÁT"},
                {"spec": "macro_prop:none|A bookmark ribbon embossed with a gold coin symbol on clean white canvas.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "GIỮ GÌN TIỀN LƯƠNG"},
            ]),
            ("Ngay sau đây, chúng ta sẽ mở khóa chiến lược ba bước phong tỏa bẫy chi tiêu trả sau vĩnh viễn.", [
                {"spec": "concept_metaphor:CH01|The stickman points eagerly toward a golden key unlocking financial peace.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "PHONG TỎA BẪY NỢ"},
                {"spec": "visual_diagram:none|A triple-layer defense shield locking out reckless consumer credit offers.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "BA BƯỚC THỰC CHIẾN"},
            ]),
        ]
    ),
    (
        "Quy tắc ngón tay cái: Công thức mua đứt hai lần",
        "A smart consumer evaluation desk on pure white background.",
        "analytical_crisp",
        "structural_model",
        [
            ("Để không bao giờ rơi vào bẫy chi tiêu quá tay, hãy áp dụng quy tắc vàng Mua Đứt Hai Lần.", [
                {"spec": "full_scene:CH01|The instructor presents a crisp golden guideline board titled MUA ĐỨT HAI LẦN.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "MUA ĐỨT HAI LẦN"},
                {"spec": "visual_diagram:none|Two identical shopping boxes stacked on one scale matched by liquid cash reserves on other.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "QUY TẮC VÀNG"},
            ]),
            ("Nếu trong tài khoản thanh khoản của bạn không đủ tiền mua đứt hai món đó cùng một lúc, bạn chưa đủ tiền mua.", [
                {"spec": "concept_metaphor:CH01|Stickman checks cash reserve verifying double the price of desired item.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐỦ TIỀN MUA HAI MÓN"},
                {"spec": "still_life:none|A price tag of 2 million sitting next to a liquid bank balance of 4 million plus.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BẢO CHỨNG TÀI CHÍNH"},
            ]),
            ("Nguyên tắc này giúp bạn giữ lại một lớp đệm an toàn dự phòng cho những rủi ro bất ngờ của cuộc sống.", [
                {"spec": "full_scene:CH01|Stickman stands securely behind a sturdy shock-absorber emergency fund cushion.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "LỚP ĐỆM DỰ PHÒNG"},
                {"spec": "macro_prop:none|A reinforced steel emergency safety box resting peacefully on white ground.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "AN TOÀN BẤT NGỜ"},
            ]),
        ]
    ),
    (
        "Quy trình trì hoãn 72 giờ trước khi chốt đơn",
        "A mindful consumer patience laboratory on white canvas.",
        "narrative_warm",
        "structural_model",
        [
            ("Cơn nghiện mua sắm online thực chất chỉ là một cơn sốt dopamine ngắn hạn kéo dài trong vài tiếng.", [
                {"spec": "full_scene:CH01|Stickman observes a dopamine chemical chart spiking rapidly and then falling flat.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CƠN SỐT DOPAMINE"},
                {"spec": "visual_diagram:none|A hormonal pleasure curve shooting upward at checkout and crashing after 2 hours.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "SỐNG ẢO NGẮN HẠN"},
            ]),
            ("Bất cứ khi nào bạn muốn bấm nút trả sau, hãy bắt buộc bản thân chuyển món hàng vào danh sách yêu thích và chờ ba ngày.", [
                {"spec": "concept_metaphor:CH01|Stickman calmly moves an item from Shopping Cart into 72-Hour Waiting Queue.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "DANH SÁCH CHỜ 72H"},
                {"spec": "still_life:none|A 72-hour sand hourglass steadily draining grains of sand on white desk.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CHỜ BA NGÀY"},
            ]),
            ("Tám mươi phần trăm trường hợp sau bảy mươi hai giờ, cơn sốt hạ nhiệt và bạn sẽ thấy món đồ đó hoàn toàn vô bổ.", [
                {"spec": "full_scene:CH01|Stickman smiles with clear head and quietly deletes the unnecessary cart item.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "CƠN SỐT HẠ NHIỆT"},
                {"spec": "macro_prop:none|A digital trash bin cleanly emptying out discarded impulsive shopping desires.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TIẾT KIỆM HÀNG TRIỆU"},
            ]),
        ]
    ),
    (
        "Thao tác kỹ thuật: Khóa toàn bộ tính năng trả sau",
        "A digital smartphone settings control interface on white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Đừng dựa vào ý chí tự giác mong manh, hãy dùng hàng rào công nghệ để tự vệ trước cám dỗ.", [
                {"spec": "full_scene:CH01|Stickman opens smartphone app settings with determined purposeful focus.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HÀNG RÀO CÔNG NGHỆ"},
                {"spec": "visual_diagram:none|A toggle switch flipping from ON green to OFF gray titled BUY NOW PAY LATER.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TẮT CÁM DỖ"},
            ]),
            ("Mở ngay ứng dụng mua sắm trực tuyến, vào phần cài đặt thanh toán và gạt tắt hạn mức ví trả sau.", [
                {"spec": "full_scene:CH01|Stickman taps the deactivate button on the consumer credit line setting.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "GẠT TẮT HẠN MỨC"},
                {"spec": "visual_diagram:none|Step-by-step visual arrows: Cài Đặt -> Phương Thức Thanh Toán -> Tắt Ví Trả Sau.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "BA THAO TÁC"},
            ]),
            ("Việc tạo ra rào cản thao tác sẽ buộc não bộ phải thức tỉnh trước khi một quyết định chi tiêu bốc đồng xảy ra.", [
                {"spec": "concept_metaphor:CH01|Stickman places a physical speed bump on a fast consumer checkout track.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "GỜ GIẢM TỐC TÂM LÝ"},
                {"spec": "macro_prop:none|A yellow warning speed bump placed firmly on a digital payment pipeline.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "BUỘC NÃO THỨC TỈNH"},
            ]),
        ]
    ),
    (
        "Bình luận về giá trị của đồng tiền mồ hôi nước mắt",
        "A reflective personal wealth study room on clean white canvas.",
        "narrative_warm",
        "editorial_commentary",
        [
            ("Nhìn thẳng vào thực tế thì, sự giàu có đích thực không nằm ở số lượng túi đồ hiệu bạn mang về nhà.", [
                {"spec": "full_scene:CH01|Financial mentor speaks with mature conviction leaning toward camera.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "NHÌN THẲNG VÀO THỰC TẾ"},
                {"spec": "visual_diagram:none|A scale comparing a mountain of consumer shopping bags against a peaceful sleep pillow.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "GIÀU CÓ ĐÍCH THỰC"},
            ]),
            ("Nó nằm ở cảm giác thanh thản khi đêm về ngủ ngon giấc mà không phải giật mình lo nghĩ khoản nợ tháng tới.", [
                {"spec": "full_scene:CH01|Stickman sleeps peacefully in bed under warm golden moonlight with clear conscience.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "NGỦ NGON GIẤC"},
                {"spec": "concept_metaphor:none|A golden crescent moon resting serenely over an unburdened tranquil home.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "KHÔNG LO TRẢ NỢ"},
            ]),
            ("Mỗi đồng tiền bạn giữ lại hôm nay chính là một phiếu bầu cho sự tự do và độc lập của bạn trong tương lai.", [
                {"spec": "concept_metaphor:CH01|Stickman drops a gold coin into an open ballot box labeled TỰ DO TÀI CHÍNH.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "PHIẾU BẦU TỰ DO"},
                {"spec": "macro_prop:none|A gleaming gold coin dropping into a crystal clear savings vase on white canvas.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐỘC LẬP TƯƠNG LAI"},
            ]),
        ]
    ),
    (
        "Xây dựng tài khoản tiết kiệm phục vụ đam mê",
        "A purposeful financial planning station on crisp white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Thay vì trả góp sau khi mua, hãy lật ngược quy trình: trả góp trước cho ước mơ của bạn.", [
                {"spec": "full_scene:CH01|Stickman flips an hourglass upside down demonstrating reverse savings logic.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LẬT NGƯỢC QUY TRÌNH"},
                {"spec": "visual_diagram:none|A circular process: Tiết Kiệm Tích Lũy -> Đủ Tiền Mặt -> Mua Hưởng Thụ Trọn Vẹn.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TRẢ GÓP TRƯỚC"},
            ]),
            ("Mở một tài khoản tiết kiệm riêng đặt tên là Quỹ Thưởng Bản Thân và tự động trích tiền lẻ vào đó mỗi tuần.", [
                {"spec": "concept_metaphor:CH01|Stickman labels a digital sub-account with bold title QUỸ THƯỞNG BẢN THÂN.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "QUỸ THƯỞNG BẢN THÂN"},
                {"spec": "still_life:none|A dedicated glass jar labeled DÀNH CHO ĐAM MÊ filled with crisp folded notes.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "TRÍCH TIỀN MỖI TUẦN"},
            ]),
            ("Cảm giác cầm tiền mặt tích lũy đi mua món đồ mình mong ước suốt sáu tháng ngọt ngào gấp trăm lần trả góp nợ nần.", [
                {"spec": "full_scene:CH01|Stickman holds up desired gadget with pure triumphant pride and zero anxiety.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TỰ HÀO TRỌN VẸN"},
                {"spec": "macro_prop:none|A golden trophy silhouette standing beside fully paid consumer purchase receipt.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "NGỌT NGÀO GẤP TRĂM"},
            ]),
        ]
    ),
    (
        "Kế hoạch hành động 3 bước dọn sạch nợ trả sau",
        "A systematic debt elimination strategy room on white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Nếu hiện tại bạn đang có vài khoản trả sau dang dở, hãy thực hiện ngay kế hoạch ba bước xử lý nợ.", [
                {"spec": "full_scene:CH01|Stickman writes a clear debt elimination roadmap onto a crisp whiteboard.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KẾ HOẠCH BA BƯỚC"},
                {"spec": "visual_diagram:none|Three sequential tactical pillars: Kiểm Kê Tổng Nợ, Tất Toán Khoản Nhỏ, Khóa Vĩnh Viễn Ví.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "DỌN SẠCH NỢ"},
            ]),
            ("Bước một: Liệt kê toàn bộ các khoản phải trả ra giấy để nhìn thấy rõ bức tranh tổng thể.", [
                {"spec": "full_scene:CH01|Stickman compiles an honest spreadsheet table listing every pending installment.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "LIỆT KÊ RA GIẤY"},
                {"spec": "visual_diagram:none|An audit spreadsheet showing Channel, Remaining Balance, and Due Date columns.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "BỨC TRANH TỔNG THỂ"},
            ]),
            ("Bước hai: Dồn tiền tất toán dứt điểm từng khoản một theo phương pháp quả cầu tuyết tài chính.", [
                {"spec": "concept_metaphor:CH01|Stickman rolls a small clean snowball that grows smoothly knocking down debt pins.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "QUẢ CẦU TUYẾT"},
                {"spec": "visual_diagram:none|Snowball diagram showing cleared small balances creating momentum to crush larger debts.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TẤT TOÁN DỨT ĐIỂM"},
            ]),
        ]
    ),
    (
        "Bài test 1 phút kiểm tra độ nghiện mua sắm",
        "A personal financial honesty mirror room on pure white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Trước khi kết thúc video, hãy tự kiểm tra xem mình có đang là con mồi của các sàn thương mại điện tử không.", [
                {"spec": "full_scene:CH01|Stickman points toward a simple one-minute financial self-diagnostic test.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BÀI TEST 1 PHÚT"},
                {"spec": "visual_diagram:none|A three-item diagnostic questionnaire: Mua vì buồn chán? Hay trả góp? Cuối tháng hụt tiền?", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TỰ SOI LẠI MÌNH"},
            ]),
            ("Nếu bạn trả lời có cho ít nhất hai câu, đã đến lúc phải cài đặt lại tư duy tài chính của mình.", [
                {"spec": "concept_metaphor:CH01|Stickman presses a green RESET button restoring balance to an overloaded wallet.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "CÀI ĐẶT LẠI TƯ DUY"},
                {"spec": "visual_diagram:none|System reset progress bar reaching 100% restoring healthy financial habits.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "TỈNH TÁO KỊP THỜI"},
            ]),
            ("Tự do tài chính bắt đầu từ dũng khí nói không với những ham muốn nhất thời và bốc đồng.", [
                {"spec": "full_scene:CH01|Stickman raises hand in firm confident refusal before a barrage of flash sales.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "DŨNG KHÍ NÓI KHÔNG"},
                {"spec": "macro_prop:none|A golden shield emblazoned with words TỰ CHỦ VÀ TỰ DO trên nền trắng.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "BẢN LĨNH TÀI CHÍNH"},
            ]),
        ]
    ),
    (
        "Lời kết và chiếc cầu nối cho người muốn làm chủ ví tiền",
        "A peaceful prosperous financial studio on pure white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Tiền bạc là công cụ phục vụ cuộc sống, đừng biến mình thành nô lệ cho những thuật toán mua sắm trả sau.", [
                {"spec": "full_scene:CH01|Financial mentor smiles warmly standing upright in calm dignified posture.", "tempo": "fast", "narrative_situation": "editorial_commentary", "emphasis_text": "LÀM CHỦ CÔNG CỤ"},
                {"spec": "visual_diagram:none|A broken debt chain freeing a stickman who walks toward sunny financial horizon.", "tempo": "fast", "narrative_situation": "editorial_commentary", "emphasis_text": "KHÔNG LÀM NÔ LỆ"},
            ]),
            ("Bạn đang trích bao nhiêu phần trăm lương cho trả góp, hãy cùng tính nhẩm dưới phần bình luận nhé.", [
                {"spec": "full_scene:CH01|The host gestures with friendly encouragement toward conversational comments below.", "tempo": "normal", "narrative_situation": "editorial_commentary", "emphasis_text": "TÍNH NHẨM BÌNH LUẬN"},
                {"spec": "macro_prop:none|A friendly speech bubble containing a percent symbol beside a wallet.", "tempo": "normal", "narrative_situation": "editorial_commentary", "emphasis_text": "CHIA SẺ KINH NGHIỆM"},
            ]),
            ("Hãy cùng nhau chia sẻ câu chuyện để giúp cộng đồng xây dựng thói quen tài chính an toàn và lành mạnh nhé.", [
                {"spec": "full_scene:CH01|Stickman waves hand warmly greeting a supportive community of smart savers.", "tempo": "normal", "narrative_situation": "editorial_commentary", "emphasis_text": "CỘNG ĐỒNG AN TOÀN"},
                {"spec": "visual_diagram:none|A circular group of happy stickmen holding hands around a solid gold coin.", "tempo": "normal", "narrative_situation": "editorial_commentary", "emphasis_text": "TÀI CHÍNH LÀNH MẠNH"},
            ]),
        ]
    ),
]

SHORT_STORY_ROWS = [
    (
        "Khoảnh khắc chốt đơn 0 đồng đầy mê hoặc",
        "A fast-paced smartphone checkout screen on clean white canvas.",
        "narrative_warm",
        "curiosity_hook",
        [
            ("Chốt đơn món đồ bạc triệu mà ví tiền không hề vơi đi một xu nào?", [
                {"spec": "full_scene:CH01|Stickman taps phone checkout with ecstatic grin seeing zero balance deduction.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "CHỐT ĐƠN 0 ĐỒNG"},
                {"spec": "visual_diagram:none|A smartphone display with green Buy Now Pay Later button flashing brightly.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "VÍ KHÔNG VƠI"},
            ]),
            ("Tại sao tính năng Mua Trước Trả Sau lại khiến bạn chi tiêu nhiều hơn bốn mươi phần trăm?", [
                {"spec": "full_scene:CH01|Stickman holds up multiple shopping bags looking slightly bewildered at scale.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "CHI NHIỀU HƠN 40%"},
                {"spec": "still_life:none|A cluster of trendy brand shopping bags piling up beside a sleek phone.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "NGHIỆN MUA SẮM"},
                {"spec": "concept_metaphor:none|A tempting shiny golden cheese wedge placed over a small metal spring trap.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "MIẾNG PHO MÁT"},
            ]),
        ]
    ),
    (
        "Khoa học thần kinh về việc tê liệt nỗi đau trả tiền",
        "A neurofinance research laboratory diagram on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Khi đếm tiền mặt, trung khu xử lý đau đớn trong não sẽ lập tức kích hoạt báo động.", [
                {"spec": "full_scene:CH01|Neuroscientist points to the insula brain region flashing red on cash counting.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "BÁO ĐỘNG ĐAU ĐỚN"},
                {"spec": "visual_diagram:none|A brain insula scan lighting up with a warning siren symbol for cash payments.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "VÙNG ĐAU VÍ TIỀN"},
            ]),
            ("Nhưng mô hình trả sau đã vô hiệu hóa hoàn toàn tín hiệu phòng vệ tự nhiên này.", [
                {"spec": "concept_metaphor:CH01|Stickman shows an open scissors cutting the connection between item and payment.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "VÔ HIỆU HÓA PHÒNG VỆ"},
                {"spec": "visual_diagram:none|Split contrast: Cash creates Instant Hesitation vs BNPL creates Zero Resistance.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "CHẶT ĐỨT CẢNH BÁO"},
                {"spec": "still_life:none|A physical banknote cut neatly in two parts on clean white table.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "MẤT PHẢN XẠ"},
            ]),
        ]
    ),
    (
        "Bản chất kiếm tiền từ phí phạt trễ hạn",
        "A corporate fintech balance sheet analysis room on white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Các app trả sau không mở dịch vụ miễn phí để làm việc thiện cho người tiêu dùng.", [
                {"spec": "full_scene:CH01|Stickman points to an unmasked corporate balance sheet with sharp red arrows.", "tempo": "fast", "narrative_situation": "editorial_commentary", "emphasis_text": "KHÔNG LÀM VIỆC THIỆN"},
                {"spec": "visual_diagram:none|A corporate vault receiving massive revenue streams marked PENALTY FEES.", "tempo": "fast", "narrative_situation": "editorial_commentary", "emphasis_text": "BẢN CHẤT LỢI NHUẬN"},
            ]),
            ("Họ kiếm hàng tỷ đồng từ những lần bạn đãng trí trễ hạn với mức phí phạt ba mươi phần trăm.", [
                {"spec": "concept_metaphor:CH01|A giant red penalty gavel strikes down on an overdue invoice slip.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "PHÍ PHẠT 30%"},
                {"spec": "visual_diagram:none|An exponential penalty curve multiplying an initial small debt into a heavy bill.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "LÃI PHẠT CHỒNG CHẤT"},
                {"spec": "macro_prop:none|A heavy red stamp printing LATE FEE onto a customer statement.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "BẪY PHÍ PHẠT"},
            ]),
        ]
    ),
    (
        "Đỉnh cao trào bỏ lửng và câu hỏi then chốt",
        "A dramatic high-stakes financial crossroads on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Càng chia nhỏ kỳ trả góp, bạn càng lún sâu vào ảo giác mình đang giàu có hơn thực tế.", [
                {"spec": "full_scene:CH01|Stickman walks proudly wearing fancy apparel while credit score drops below.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "ẢO GIÁC GIÀU CÓ"},
                {"spec": "visual_diagram:none|A visual graph showing Illusion of Wealth diverging sharply from Real Savings.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "LÚN SÂU VÀO NỢ"},
            ]),
            ("Chỉ cần một kỳ lương chậm, toàn bộ hệ thống trả nợ sẽ sụp đổ như quân cờ domino.", [
                {"spec": "concept_metaphor:CH01|Stickman watches a long line of domino bricks toppling consecutively.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "SỤP ĐỔ DOMINO"},
                {"spec": "visual_diagram:none|Toppling domino line labeled Payday Delay -> Late Fee -> Bad Credit.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "SỰ CỐ CHẬM LƯƠNG"},
                {"spec": "still_life:none|A single delayed paycheck slip surrounded by urgent collection notices.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "RỦI RO THỰC TẾ"},
            ]),
            ("Đúng lúc bạn nghĩ mình quản lý nợ hoàn hảo thì chỉ một cú trễ hạn hai ngày sẽ kích hoạt bẫy phí phạt ra sao?", [
                {"spec": "concept_metaphor:CH01|Stickman stands before a branching crossroads with a giant question mark.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "KÍCH HOẠT BẪY PHẠT"},
                {"spec": "visual_diagram:none|A red question mark hovering above a locked bank credit evaluation vault.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "LỜI CẢNH BÁO"},
            ]),
        ]
    ),
    (
        "Chuyển phễu sang bản Full và Close CTA",
        "A clean inspiring financial freedom study on pure white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Xem video bản dài bên dưới để lấy quy tắc 72 giờ khóa chặt ví tiền nhé.", [
                {"spec": "full_scene:CH01|Stickman points enthusiastically down toward the linked video preview card.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "XEM BẢN DÀI"},
                {"spec": "visual_diagram:none|A bold directional arrow pointing down to the related full-length video badge.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "QUY TẮC 72 GIỜ"},
            ]),
            ("Lưu lại ngay để bảo vệ đồng lương mồ hôi nước mắt bạn nhé.", [
                {"spec": "full_scene:CH01|Stickman smiles warmly waving hand beside channel emblem on white canvas.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "LƯU LẠI BẢO VỆ"},
                {"spec": "macro_prop:none|A glowing golden shield protecting a leather wallet on pure white canvas.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "BẢO VỆ ĐỒNG LƯƠNG"},
            ]),
        ]
    ),
]
