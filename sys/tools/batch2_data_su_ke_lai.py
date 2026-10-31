# -*- coding: utf-8 -*-
"""Batch 2 Story Blueprint for Sử Kể Lại (channel-su-ke-lai).

Topic: Điện Biên Phủ 1954 Đổi Phương Án Tác Chiến (Long) & Quyết Định Kéo Pháo Ra (Short)
Format: V3 High-Density Narrative-Driven Adaptive Visual Pacing.
"""

from typing import Any, Dict, List, Tuple

CHANNEL_ID = "su_ke_lai"
CHANNEL_SLUG = "su-ke-lai"

# =============================================================================
# LONG EXPLAINER (16 SCENES, ~94 BEATS, ~265 SECONDS)
# =============================================================================

LONG_TOPIC = "Chiến Dịch Điện Biên Phủ 1954: Can Đổi Lịch Sử Từ 'Đánh Nhanh Thắng Nhanh' Sang 'Đánh Chắc Tiến Chắc'"
LONG_AUDIENCE = "Khán giả yêu lịch sử, chiến lược quân sự, người tìm kiếm bài học lãnh đạo và ra quyết định"
LONG_GOAL = "Mổ xẻ quyết định thay đổi phương châm tác chiến lịch sử của Đại tướng Võ Nguyên Giáp và bài học dũng cảm thay đổi chiến lược"

LONG_EDITORIAL_STANCE = {
    "myth_debunked": "Chiến thắng Điện Biên Phủ là nhờ quân ta áp dụng chiến thuật biển người lấy số lượng đè chất lượng.",
    "why_generic_advice_fails": "Nhiều tài liệu phương Tây cố tình biện minh cho thất bại bằng cách che giấu sự vượt trội về nghệ thuật tác chiến và hậu cần của ta.",
    "channel_verdict": "Sự thật mất lòng là nếu ngày đó vội vã đánh nhanh theo quán tính, quân đội ta có thể đã chịu tổn thất không thể gượng dậy.",
    "tradeoff_or_blindspot": "Quyết định kéo pháo ra đòi hỏi sự chịu đựng gian khổ tột cùng của hàng vạn chiến sĩ nhưng đã bảo toàn được toàn bộ lực lượng tinh nhuệ."
}

LONG_ACTIONABLE_VALUE = {
    "core_mechanism": "Cơ chế quản trị rủi ro chiến lược: khi dữ liệu thực địa không còn phù hợp với kế hoạch ban đầu, phải dũng cảm hủy bỏ để tái thiết kế.",
    "practical_rule_of_thumb": "Quy tắc kiểm chứng thực địa: không bao giờ phát động tổng lực khi chưa có phương án xử lý vũ khí áp đảo của đối phương.",
    "real_world_scenario": "Một nhà lãnh đạo hủy bỏ đợt tung sản phẩm trị giá hàng triệu đô vào phút chót khi phát hiện lỗ hổng chuỗi cung ứng."
}

LONG_PACKAGING = {
    "youtube_title": "Điện Biên Phủ 1954: Quyết Định Khó Khăn Nhất Của Tướng Giáp",
    "visual_hook": "Đại tướng người que đứng trầm ngâm bên ngọn đèn dầu soi bản đồ thung lũng Mường Thanh dày đặc hầm ngầm",
    "text_overlay": "QUYẾT ĐỊNH LỊCH SỬ",
    "contrast_pair": "Đánh nhanh liều lĩnh vs Đánh chắc tiến chắc vĩ đại",
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": ["su ke lai", "dien bien phu", "tuong giap", "lich su viet nam", "chien thuat"],
    "cta_plan": {
        "mid_cta": "Nếu bạn trân trọng những trang sử hào hùng đầy trí tuệ của dân tộc, hãy lưu lại video để xem lại nhé.",
        "close": "Chi tiết chiến thuật nào tại Điện Biên Phủ khiến bạn khâm phục nhất, hãy để lại lời bình cho Sử Kể Lại nhé.",
        "endcard_text": "SỬ KỂ LẠI"
    }
}

LONG_SOURCES = [
    {
        "id": "SRC01",
        "title": "Hồ Sơ Tổng Kết Chiến Dịch Điện Biên Phủ 1954",
        "reference": "Viện Lịch Sử Quân Sự Việt Nam (2024). Bộ Quốc Phòng.",
        "facts": [
            "Tập đoàn cứ điểm Điện Biên Phủ gồm bốn mươi chín cứ điểm kiên cố chia thành ba phân khu liên hoàn.",
            "Quyết định kéo pháo ra được đưa ra chỉ mười một tiếng trước giờ nổ súng dự kiến ban đầu."
        ]
    }
]

LONG_STORY_ROWS: List[Tuple[str, str, str, str, List[Tuple[str, Any]]]] = [
    (
        "Bức tranh Điện Biên Phủ đầu năm 1954",
        "A historical command tent with mountain map on white canvas.",
        "narrative_warm",
        "lived_friction",
        [
            ("Tháng một năm 1954, thung lũng Mường Thanh biến thành một pháo đài khổng lồ bất khả xâm phạm.", [
                {"spec": "full_scene:CH01|Historian stickman with terracotta scarf points marker to a detailed military valley map.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "THÁNG MỘT 1954"},
                {"spec": "concept_metaphor:none|A hand-drawn map of Muong Thanh valley surrounded by high jagged mountain peaks.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "THUNG LŨNG MƯỜNG THANH"},
            ]),
            ("Quân viễn chinh Pháp xây dựng bốn mươi chín cứ điểm liên hoàn với hầm ngầm kiên cố và sân bay hiện đại.", [
                {"spec": "visual_diagram:none|A tactical layout showing forty-nine fortified bunker strongpoints linked by trenches.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "BỐN MƯƠI CHÍN CỨ ĐIỂM"},
                {"spec": "still_life:none|Heavy concrete bunker model with barbed wire entanglements drawn in clean ink.", "tempo": "fast", "narrative_situation": "hook_shock", "emphasis_text": "HẦM NGẦM KIÊN CỐ"},
            ]),
            ("Các tướng lĩnh phương Tây tự tin tuyên bố đây là một cỗ máy nghiền nát mọi đợt tấn công.", [
                {"spec": "full_scene:CH01|French commander stickman stands confidently holding field glasses pointing to the hills.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TỰ TIN TUYÊN BỐ"},
                {"spec": "macro_prop:none|A brass military general badge stamped with an arrogant golden laurel wreath.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "CỐ MA NGUY HIỂM"},
            ]),
        ]
    ),
    (
        "Phương án ban đầu: Đánh nhanh thắng nhanh",
        "A wartime field briefing table under canvas canopy on white background.",
        "analytical_crisp",
        "lived_friction",
        [
            ("Ban đầu, kế hoạch được vạch ra là dồn toàn lực đánh nhanh thắng nhanh trong ba ngày đêm.", [
                {"spec": "full_scene:CH01|Military officers deliberate around a map table pointing swift offensive arrows.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "ĐÁNH NHANH THẮNG NHANH"},
                {"spec": "visual_diagram:none|Three lightning bolt arrows piercing straight through the enemy central sector.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "BA NGÀY BA ĐÊM"},
            ]),
            ("Mục tiêu là chọc thủng trận địa trước khi đối phương kịp củng cố thêm công sự và tiếp viện.", [
                {"spec": "concept_metaphor:none|A sharp spear tip attempting to shatter a thick concrete defense wall.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CHỌC THỦNG PHÒNG TUYẾN"},
                {"spec": "still_life:none|An hourglass running fast indicating urgency to strike before reinforcements land.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CHẠY ĐUA THỜI GIAN"},
            ]),
            ("Toàn quân hừng hực khí thế, pháo nặng đã kéo vào trận địa sẵn sàng chờ lệnh phát hỏa.", [
                {"spec": "full_scene:CH01|Heroic soldiers pulling heavy artillery cannon uphill with thick rope harnesses.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "HỪNG HỰC KHÍ THẾ"},
                {"spec": "macro_prop:none|A heavy howitzer artillery barrel camouflaged with mountain tree branches.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "PHÁO LÊN TRẬN ĐỊA"},
            ]),
        ]
    ),
    (
        "Những đêm mất ngủ của Đại tướng",
        "A quiet nocturnal bamboo hut with oil lamp on white canvas.",
        "narrative_warm",
        "lived_friction",
        [
            ("Nhưng tại lán chỉ huy Nà Tấu, Đại tướng Võ Nguyên Giáp trăn trở suốt nhiều đêm trắng.", [
                {"spec": "full_scene:CH01|General stickman sits alone under a small kerosene lamp pacing the wooden floor.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "ĐÊM TRẮNG NÀ TẤU"},
                {"spec": "still_life:none|A warm flickering kerosene oil lamp illuminating a hand-annotated field map.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "NGỌN ĐÈN DẦU"},
            ]),
            ("Các tin tức trinh sát báo về cho thấy địch đã tăng viện xe tăng, pháo binh và mở rộng dây kẽm gai.", [
                {"spec": "concept_metaphor:CH01|The General reviews handwritten reconnaissance intelligence dispatches.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐỊCH TĂNG VIỆN"},
                {"spec": "visual_diagram:none|A map showing new barbed wire density doubled around central command bunkers.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "DÂY THÉP GAI DÀY"},
            ]),
            ("Cứ điểm không còn ở trạng thái lâm thời mà đã biến thành pháo đài thép kiên cố vô cùng.", [
                {"spec": "full_scene:CH01|The General looks through field glass seeing newly fortified tank bunkers.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "PHÁO ĐÀI THÉP"},
                {"spec": "macro_prop:none|A heavy tank silhouette embedded inside a deep reinforced earthen revetment.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "XE TĂNG BẢO VỆ"},
            ]),
        ]
    ),
    (
        "Lời dặn dò của Chủ tịch Hồ Chí Minh",
        "A historical meeting room memory sketch on clean white canvas.",
        "narrative_warm",
        "lived_friction",
        [
            ("Trong tâm trí vị tướng trẻ lúc bấy giờ luôn vang vọng lời căn dặn trước khi ra trận.", [
                {"spec": "full_scene:CH01|Uncle Ho stickman speaks with warmth and solemn resolve to the young General.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "LỜI DẶN RA TRẬN"},
                {"spec": "concept_metaphor:none|Two friendly hands clasping firmly in deep mutual trust on white background.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "LÒNG TIN NƠI TƯỚNG"},
            ]),
            ("Chủ tịch Hồ Chí Minh đã dặn dò: Trận này rất quan trọng, chắc thắng mới đánh, không chắc thắng không đánh.", [
                {"spec": "visual_diagram:none|A golden scroll bearing bold calligraphy: CHẮC THẮNG MỚI ĐÁNH, KHÔNG CHẮC THẮNG KHÔNG ĐÁNH.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CHẮC THẮNG MỚI ĐÁNH"},
                {"spec": "still_life:none|An open notebook with handwritten quote preserved with delicate care.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "KHÔNG ĐÁNH MÙ QUÁNG"},
            ]),
            ("Nếu mạo hiểm đánh nhanh, quân ta có nguy cơ phơi mình trước hỏa lực pháo và không quân đối phương.", [
                {"spec": "full_scene:CH01|The General imagines open terrain exposed to heavy enemy air bombardment.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "NGUY CƠ PHƠI MÌNH"},
                {"spec": "visual_diagram:none|Tactical vulnerability map showing infantry lines exposed in flat open valley.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "HỎA LỰC PHÁO"},
            ]),
        ]
    ),
    (
        "Mười một tiếng trước giờ nổ súng",
        "A tense morning command conference room on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Sáng ngày hai mươi sáu tháng một, chỉ mười một tiếng trước khi pháo lệnh dự kiến mở màn.", [
                {"spec": "full_scene:CH01|Artillery commanders sit around conference table in heavy anticipation.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "MƯỜI MỘT TIẾNG"},
                {"spec": "macro_prop:none|A military pocket watch counting down to the planned sunset zero hour.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "GIỜ NỔ SÚNG"},
            ]),
            ("Tổng tư lệnh triệu tập cuộc họp Đảng ủy mặt trận lịch sử.", [
                {"spec": "full_scene:CH01|The General stands upright at head of table with firm resolute bearing.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HỌP ĐẢNG ỦY MẶT TRẬN"},
                {"spec": "concept_metaphor:none|A solemn conference table bathed in crisp morning mountain sunlight.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CUỘC HỌP LỊCH SỬ"},
            ]),
            ("Ông đặt câu hỏi thẳng thắn: Liệu chúng ta có nắm chắc một trăm phần trăm chiến thắng hay không?", [
                {"spec": "concept_metaphor:CH01|The General looks into eyes of each commander awaiting genuine assessments.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CÓ NẮM CHẮC THẮNG?"},
                {"spec": "visual_diagram:none|A percentage scale hovering between Uncertain Gamble and Absolute Guarantee.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "MỘT TRĂM PHẦN TRĂM"},
            ]),
        ]
    ),
    (
        "Lời bình sắc bén: Sự thật mất lòng",
        "A stark historical reflection room on clean white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Sự thật mất lòng là, thay đổi một quyết định khi tất cả đã sẵn sàng đòi hỏi bản lĩnh phi thường.", [
                {"spec": "full_scene:CH01|Historian stickman delivers a solemn thoughtful analysis to camera.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "SỰ THẬT MẤT LÒNG"},
                {"spec": "concept_metaphor:none|A massive steam locomotive being safely braked inches before an unseen broken bridge.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "PHANH LẠI ĐÚNG LÚC"},
            ]),
            ("Đánh giá công bằng thì, cái bẫy lớn nhất của người chỉ huy là sự thỏa hiệp vì sợ bị chê là do dự.", [
                {"spec": "full_scene:CH01|The General stands alone resisting peer momentum to protect soldier lives.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐÁNH GIÁ CÔNG BẰNG"},
                {"spec": "visual_diagram:none|A split scale separating Fear of Looking Hesitant from Moral Responsibility for Lives.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "CÁI BẪY THỎA HIỆP"},
            ]),
            ("Đừng nghe luận điệu nông nổi khi xương máu của hàng vạn đồng đội phụ thuộc vào quyết định của bạn.", [
                {"spec": "concept_metaphor:CH01|The General gently touches a soldier shoulder with profound brotherly care.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "XƯƠNG MÁU ĐỒNG ĐỘI"},
                {"spec": "macro_prop:none|A brass helmet decorated with young green leaves on pure white background.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "BẢO TOÀN LỰC LƯỢNG"},
            ]),
        ]
    ),
    (
        "Điểm dừng lịch sử và Mid-CTA",
        "A quiet mountain ridge overview under open sky on white canvas.",
        "narrative_warm",
        "structural_model",
        [
            ("Khoảnh khắc ấy đã đi vào giáo trình của các học viện quân sự danh giá nhất thế giới.", [
                {"spec": "full_scene:CH01|Historian stickman stands beside an open military textbook on podium.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HỌC VIỆN QUÂN SỰ"},
                {"spec": "still_life:none|A pair of vintage military binoculars resting beside a topographical map.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ỐNG NHÒM QUÂN SỰ"},
            ]),
            ("Nếu bạn trân trọng những trang sử hào hùng đầy trí tuệ của dân tộc, hãy lưu lại video để xem lại nhé.", [
                {"spec": "full_scene:CH01|The historian gestures with warm respect toward the save bookmark ribbon.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LƯU LẠI XEM LẠI"},
                {"spec": "macro_prop:none|A red bookmark ribbon embossed with a golden five-pointed star emblem.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LƯU VIDEO"},
            ]),
            ("Bây giờ, chúng ta sẽ chứng kiến mệnh lệnh kéo pháo ra đầy đau đớn nhưng thiên tài.", [
                {"spec": "concept_metaphor:CH01|The General signs the redeployment order with decisive deliberate ink.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "MỆNH LỆNH THIÊN TÀI"},
                {"spec": "visual_diagram:none|Tactical transition arrows shifting from Red Direct Assault to Blue Encircling Siege.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CHUYỂN PHƯƠNG CHÂM"},
            ]),
        ]
    ),
    (
        "Quyết định khó khăn nhất trong cuộc đời",
        "A historical command conference room concluding on white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Vượt qua mọi áp lực, Đại tướng kết luận: Hoãn nổ súng, chuyển sang đánh chắc tiến chắc.", [
                {"spec": "full_scene:CH01|The General raises hand firmly announcing the historic change of strategy.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐÁNH CHẮC TIẾN CHẮC"},
                {"spec": "visual_diagram:none|A banner unfurling with the bold doctrine: ĐÁNH CHẮC TIẾN CHẮC on white canvas.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HOÃN NỔ SÚNG"},
            ]),
            ("Ông yêu cầu các đơn vị lui về điểm tập kết và kéo toàn bộ pháo ra khỏi trận địa.", [
                {"spec": "full_scene:CH01|Artillery commanders saluting in disciplined acceptance of the master order.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "RÚT VỀ TẬP KẾT"},
                {"spec": "concept_metaphor:none|A reverse tactical maneuver arrow pulling forces back into safe defensive cover.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "LÙI MỘT BƯỚC"},
            ]),
            ("Đây được Đại tướng gọi là quyết định khó khăn nhất trong suốt cuộc đời cầm quân của mình.", [
                {"spec": "full_scene:CH01|The General gazes into the distance with profound moral conviction and weight.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "QUYẾT ĐỊNH KHÓ KHĂN NHẤT"},
                {"spec": "macro_prop:none|A bronze quill pen resting beside an open memoir volume on white canvas.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TRANG HỒI KÝ"},
            ]),
        ]
    ),
    (
        "Hành trình kéo pháo ra đẫm mồ hôi và máu",
        "A rugged mountain pass under heavy rain on white canvas.",
        "narrative_warm",
        "structural_model",
        [
            ("Kéo pháo vào đã gian nan tột cùng, kéo pháo ra dốc đứng càng hiểm nguy gấp bội phần.", [
                {"spec": "full_scene:CH01|Artillerymen straining every muscle holding heavy ropes on muddy slope.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KÉO PHÁO RA"},
                {"spec": "visual_diagram:none|A steep sixty-degree incline profile showing heavy weight threatening to roll backward.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "DỐC ĐỨNG HIỂM NGUY"},
            ]),
            ("Dưới mưa phùn lầy lội và bom đạn bắn phá, chiến sĩ ta dùng chèn gỗ và cả thân mình giữ pháo.", [
                {"spec": "full_scene:CH01|Heroic soldier stickman jams a wooden wedge under the artillery wheel in crisis.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "CHÈN GỖ GIỮ PHÁO"},
                {"spec": "concept_metaphor:none|A heroic figure standing firm as a mountain pillar supporting the nation artillery.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "THÂN MÌNH GIỮ PHÁO"},
            ]),
            ("Tấm gương anh hùng Tô Vĩnh Diện lấy thân chèn bánh pháo đã trở thành biểu tượng bất tử.", [
                {"spec": "full_scene:CH01|The historian stickman bows head in deep reverence before a memorial flame.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TÔ VĨNH DIỆN"},
                {"spec": "macro_prop:none|A wooden wheel wedge glowing with an eternal golden aura of sacrifice.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "BIỂU TƯỢNG BẤT TỬ"},
            ]),
        ]
    ),
    (
        "Chuẩn bị kỹ lưỡng: Kỳ tích hậu cần xe đạp thồ",
        "A jungle mountain supply trail on clean white canvas.",
        "narrative_warm",
        "structural_model",
        [
            ("Hai tháng hoãn binh là khoảng thời gian quân dân ta kiến tạo kỳ tích hậu cần vô tiền khoáng hậu.", [
                {"spec": "full_scene:CH01|Civilian porters pushing reinforced bicycles loaded high with grain sacks.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KỲ TÍCH HẬU CẦN"},
                {"spec": "visual_diagram:none|Supply flow route tracing hundreds of kilometers from rear provinces to front lines.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HAI THÁNG HOÃN BINH"},
            ]),
            ("Hơn hai vạn chiếc xe đạp thồ vượt đèo lội suối, mỗi xe tải tới ba trăm kilôgam lương thực.", [
                {"spec": "concept_metaphor:CH01|The stickman pushes a bicycle modified with bamboo handle extensions.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "XE ĐẠP THỒ"},
                {"spec": "macro_prop:none|A vintage bicycle sketch showing bamboo reinforcement frame and heavy pack.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "BA TRĂM KILÔGAM"},
            ]),
            ("Người Pháp không thể ngờ những chiếc xe đạp thô sơ lại đánh bại hoàn toàn đội máy bay vận tải tối tân.", [
                {"spec": "full_scene:CH01|The historian compares a simple bicycle with a cargo transport airplane.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "ĐÁNH BẠI KHÔNG VẬN"},
                {"spec": "visual_diagram:none|Graphic comparing Steady Bicycle Convoy against Grounded Weather-Bound Air Fleet.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "Ý CHÍ CON NGƯỜI"},
            ]),
        ]
    ),
    (
        "Chiến thuật vây lấn từng bước bằng giao thông hào",
        "A subterranean trench engineering diagram on white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Thay vì xung phong trên mặt đất, ta đào một mạng lưới giao thông hào dài hàng trăm kilômét.", [
                {"spec": "full_scene:CH01|Soldiers digging trenches with shovels under earth roof camouflage.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "MẠNG LƯỚI CHIẾN HÀO"},
                {"spec": "visual_diagram:none|Concentric trench lines tightening slowly around enemy central command bunker.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "TRĂM KILÔMÉT"},
            ]),
            ("Chiến hào như chiếc thòng lọng siết chặt từng ngày, bóp nghẹt sân bay và cắt đứt mọi tiếp tế.", [
                {"spec": "concept_metaphor:CH01|The researcher demonstrates trench lines closing around an airfield runway.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "SIẾT CHẶT VÒNG VÂY"},
                {"spec": "visual_diagram:none|Airfield runway crossed out in red ink as trenches advance across tarmac.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "CẮT TIẾP TẾ"},
            ]),
            ("Pháo binh được đặt trong hầm ngầm kiên cố trên sườn núi, ngắm bắn thẳng vào lòng chảo an toàn.", [
                {"spec": "full_scene:CH01|Artillery placed inside reinforced mountain cave firing directly into valley.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "PHÁO ĐẶT TRONG HẦM"},
                {"spec": "macro_prop:none|A cross-section sketch of a mountain bunker artillery embrasure looking down.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "BẮN THẲNG"},
            ]),
        ]
    ),
    (
        "Bình luận về tư duy chiến lược linh hoạt",
        "A strategic decision study room on clean white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Điểm mù của nhiều nhà quản trị là bám chặt lấy kế hoạch cũ vì tiếc công sức đã bỏ ra.", [
                {"spec": "full_scene:CH01|The historian speaks directly to camera pointing to a discarded rigid plan.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐIỂM MÙ QUẢN TRỊ"},
                {"spec": "concept_metaphor:none|A heavy stone weight pulling an outdated binder down into deep water.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "BẪY CHI PHÍ CHÌM"},
            ]),
            ("Cái giá phải trả cho sự cố chấp mù quáng là thất bại thảm hại khi hoàn cảnh đã thay đổi.", [
                {"spec": "full_scene:CH01|The historian walks past ruins of a fortress that failed to adapt to gunpowder.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "CÁI GIÁ CỐ CHẤP"},
                {"spec": "visual_diagram:none|A pathway showing Rigid Obstinacy leading straight off an unexpected cliff.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "CẢNH BÁO CHIẾN LƯỢC"},
            ]),
            ("Nhìn thẳng vào thực tế thì, dũng cảm lùi lại một bước để tái thiết lập thế cờ mới là đỉnh cao trí tuệ.", [
                {"spec": "concept_metaphor:CH01|A chess player calmly moving king one step backward to deliver checkmate.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "LÙI ĐỂ THẮNG LỚN"},
                {"spec": "macro_prop:none|A golden chess king piece standing victorious on clean white canvas.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐỈNH CAO TRÍ TUỆ"},
            ]),
        ]
    ),
    (
        "Quy tắc ngón tay cái: Ba bài học lãnh đạo",
        "A modern leadership reflection table on white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Từ bài học Điện Biên Phủ, chúng ta đúc kết quy tắc ba bước xử lý rủi ro chiến lược.", [
                {"spec": "full_scene:CH01|The historian writes three golden rules onto a presentation blackboard.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BA BÀI HỌC LÃNH ĐẠO"},
                {"spec": "visual_diagram:none|Three executive pillars: Tôn Trọng Dữ Liệu, Dũng Cảm Thay Đổi, Bảo Toàn Nguồn Lực.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "QUY TẮC VÀNG"},
            ]),
            ("Bước một: Luôn kiểm tra lại giả định ban đầu khi thực địa xuất hiện biến số mới.", [
                {"spec": "full_scene:CH01|The leader stickman compares theoretical blueprint with real-world sensor logs.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "KIỂM TRA GIẢ ĐỊNH"},
                {"spec": "still_life:none|A magnifying glass examining new data entries highlighted in red marker.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "BIẾN SỐ THỰC TẾ"},
            ]),
            ("Bước hai: Dám nhận trách nhiệm hủy bỏ kế hoạch cũ dù tập thể đang hừng hực quán tính.", [
                {"spec": "concept_metaphor:CH01|A strong captain standing at helm steering away from a submerged reef.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "DÁM NHẬN TRÁCH NHIỆM"},
                {"spec": "visual_diagram:none|A leadership vector steering a collective formation safely into winning position.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "BẢN LĨNH CHỈ HUY"},
            ]),
        ]
    ),
    (
        "Chiến lược kiểm soát chi phí chìm",
        "A clear management desk with audit cards on pure white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Bước ba: Tuyệt đối không tiếc rẻ mồ hôi tâm huyết trước đó nếu tiếp tục sẽ dẫn tới thảm kịch.", [
                {"spec": "full_scene:CH01|The researcher cuts a cord labeled SUNK COST with clean sharp shears.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KHÔNG TIẾC CHI PHÍ CHÌM"},
                {"spec": "macro_prop:none|A heavy lead weight detached from a balloon letting it rise freely.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CẮT BỎ GÁNH NẶNG"},
            ]),
            ("Thà tốn thêm hai tháng chuẩn bị để nắm chắc thắng lợi còn hơn liều mạng trong ba ngày rồi ôm hận.", [
                {"spec": "concept_metaphor:CH01|The stickman patiently sharpens an axe against a whetstone before cutting tree.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "MÀI RÌU BÉN"},
                {"spec": "visual_diagram:none|Timeline comparison: 2 Months Preparation = Guaranteed Victory vs 3 Days Rush = Catastrophe.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "THẮNG LỢI VỮNG CHẮC"},
            ]),
            ("Sự kiên nhẫn và kỷ luật thép chính là vũ khí tối thượng của người chiến thắng.", [
                {"spec": "full_scene:CH01|The historian salutes with quiet pride beside a completed strategy roadmap.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "VŨ KHÍ TỐI THƯỢNG"},
                {"spec": "macro_prop:none|A gleaming brass shield embossed with words KIÊN NHẪN VÀ KỶ LUẬT.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "KỶ LUẬT THÉP"},
            ]),
        ]
    ),
    (
        "Bài test 30 giây rà soát quyết định cá nhân",
        "A peaceful personal study desk on pure white background.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Trong công việc hôm nay, bạn có đang theo đuổi một mục tiêu liều lĩnh nào không?", [
                {"spec": "full_scene:CH01|The stickman sits reflecting with pen in hand beside an active project plan.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BÀI TEST 30 GIÂY"},
                {"spec": "visual_diagram:none|A self-audit checklist asking: Có đang đánh nhanh thắng nhanh trong mơ hồ?", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TỰ HỎI BẢN THÂN"},
            ]),
            ("Hãy dừng lại ba mươi giây và tự vấn: nếu chưa nắm chắc thắng, bạn có dám kéo pháo ra không?", [
                {"spec": "concept_metaphor:CH01|The stickman places hand on chest considering the courage to pause.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "CÓ DÁM KÉO PHÁO RA?"},
                {"spec": "visual_diagram:none|A split fork in road: Liều lĩnh mù quáng vs Dừng lại chuẩn bị chắc thắng.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "DŨNG CẢM LÙI BƯỚC"},
            ]),
            ("Dám dừng lại đúng lúc để củng cố lực lượng chính là bước ngoặt của mọi thành công vĩ đại.", [
                {"spec": "full_scene:CH01|The stickman looks upward with bright confident smile as sunrise breaks.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "BƯỚC NGOẶT VĨ ĐẠI"},
                {"spec": "macro_prop:none|A golden compass needle settling steadily on True North direction.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "ĐÚNG HƯỚNG"},
            ]),
        ]
    ),
    (
        "Khép lại khúc tráng ca Điện Biên",
        "A magnificent mountain ridge under victorious golden sunrise on white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Ngày bảy tháng năm năm 1954, lá cờ Quyết chiến Quyết thắng tung bay trên nóc hầm De Castries.", [
                {"spec": "full_scene:CH01|The red flag with golden star waves proudly atop the captured enemy command bunker.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CỜ BAY NÓC HẦM"},
                {"spec": "concept_metaphor:none|A glorious red victory flag fluttering against crisp bright mountain sky.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BẢY THÁNG NĂM 1954"},
            ]),
            ("Khúc tráng ca Điện Biên Phủ mãi là bài học vô giá về bản lĩnh và trí tuệ Việt Nam.", [
                {"spec": "full_scene:CH01|The historian stickman stands proudly with hand on chest in eternal tribute.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TRÍ TUỆ VIỆT NAM"},
                {"spec": "macro_prop:none|A carved stone monument inscribed with the golden word ĐIỆN BIÊN PHỦ.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BÀI HỌC VÔ GIÁ"},
            ]),
            ("Chi tiết chiến thuật nào tại Điện Biên Phủ khiến bạn khâm phục nhất, hãy để lại lời bình cho Sử Kể Lại nhé.", [
                {"spec": "full_scene:CH01|The historian gives a respectful bow inviting thoughts in comments with warmth.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LỜI BÌNH CỦA BẠN"},
                {"spec": "white_card:none|Channel endcard illustration on flat canvas with channel mascot and clear text SỬ KỂ LẠI.", "tempo": "slow", "narrative_situation": "mechanism_step", "is_endcard": True},
            ]),
        ]
    ),
]

# =============================================================================
# SHORT SPIN-OFF (5 SCENES, ~23 BEATS, ~43 SECONDS, CLIFFHANGER FUNNEL)
# =============================================================================

SHORT_TOPIC = "Quyết Định Đau Đớn Nhất Của Tướng Giáp: Vì Sao Phải Kéo Pháo Ra Dù Đã Sẵn Sàng Bắn?"
SHORT_AUDIENCE = "Khán giả yêu lịch sử chiến thuật, sinh viên và người tìm kiếm bài học lãnh đạo"
SHORT_GOAL = "Giải mã khoảnh khắc chuyển phương châm tác chiến lịch sử và cắt phễu ở đỉnh cao trào về nguy cơ đánh nhanh"

SHORT_EDITORIAL_STANCE = {
    "myth_debunked": "Chiến thắng Điện Biên Phủ là nhờ quân ta áp dụng chiến thuật biển người lấy số lượng đè chất lượng.",
    "why_generic_advice_fails": "Nhiều tài liệu phương Tây cố tình biện minh cho thất bại bằng cách che giấu sự vượt trội về nghệ thuật tác chiến của ta.",
    "channel_verdict": "Sự thật mất lòng là nếu ngày đó vội vã đánh nhanh theo quán tính, quân đội ta có thể đã chịu tổn thất không thể gượng dậy.",
    "tradeoff_or_blindspot": "Quyết định kéo pháo ra đòi hỏi sự chịu đựng gian khổ tột cùng của hàng vạn chiến sĩ nhưng đã bảo toàn lực lượng."
}

SHORT_ACTIONABLE_VALUE = {
    "core_mechanism": "Cơ chế quản trị rủi ro chiến lược: khi dữ liệu thực địa không còn phù hợp, phải dũng cảm hủy bỏ để tái thiết kế.",
    "practical_rule_of_thumb": "Quy tắc kiểm chứng thực địa: không bao giờ phát động tổng lực khi chưa có phương án xử lý vũ khí áp đảo đối phương.",
    "real_world_scenario": "Một nhà lãnh đạo hủy bỏ đợt tung sản phẩm trị giá hàng triệu đô vào phút chót khi phát hiện lỗ hổng chuỗi cung ứng."
}

SHORT_PACKAGING = {
    "youtube_title": "Vì Sao Tướng Giáp Quyết Định Kéo Pháo Ra?",
    "visual_hook": "Tướng Giáp người que đứng suy tư bên ngọn đèn dầu giữa bản đồ Mường Thanh dày đặc cứ điểm",
    "text_overlay": "KÉO PHÁO RA",
    "contrast_pair": "Đánh nhanh liều lĩnh vs Kéo pháo chắc thắng",
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": ["su ke lai", "dien bien phu", "tuong giap", "shorts"],
    "cta_plan": {
        "cliffhanger_peak": "Đúng lúc các chỉ huy đều hừng hực khí thế muốn nổ súng ngay thì bức tranh thực địa nào đã chỉ ra nguy cơ quân ta bị tiêu diệt hoàn toàn trong ba ngày?",
        "bridge": "Xem video bản dài bên dưới để theo dõi toàn bộ chiến dịch nhé.",
        "close": "Lưu lại ngay để cùng tự hào về lịch sử dân tộc bạn nhé.",
        "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
    }
}

SHORT_SOURCES = [
    {
        "id": "SRC01",
        "title": "Hồ Sơ Tổng Kết Chiến Dịch Điện Biên Phủ 1954",
        "reference": "Viện Lịch Sử Quân Sự Việt Nam (2024). Bộ Quốc Phòng.",
        "facts": [
            "Quyết định kéo pháo ra được đưa ra chỉ mười một tiếng trước giờ nổ súng dự kiến ban đầu."
        ]
    }
]

SHORT_STORY_ROWS: List[Tuple[str, str, str, str, List[Tuple[str, Any]]]] = [
    (
        "Mở màn kịch tính trước giờ nổ súng",
        "A historical command tent at dawn on white canvas.",
        "narrative_warm",
        "hook",
        [
            ("Chỉ mười một tiếng trước giờ phát hỏa Điện Biên Phủ, Đại tướng Võ Nguyên Giáp ra một mệnh lệnh gây sốc.", [
                {"spec": "full_scene:CH01|The General raises hand firmly announcing urgent redeployment orders in command tent.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "MƯỜI MỘT TIẾNG"},
                {"spec": "macro_prop:none|A military field clock showing the ticking countdown to planned zero hour.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "MỆNH LỆNH GÂY SỐC"},
                {"spec": "concept_metaphor:none|A battlefield artillery cannon suddenly halted inches before pulling firing lanyard.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "HOÃN NỔ SÚNG"},
            ]),
            ("Toàn quân lập tức dừng tấn công và kéo toàn bộ trọng pháo ra khỏi trận địa.", [
                {"spec": "visual_diagram:none|A tactical retreat vector drawing heavy artillery symbols back into mountain caves.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "KÉO PHÁO RA"},
                {"spec": "still_life:none|Heavy rope harnesses and wooden wheel wedges lying on muddy trench ground.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "LÙI QUÂN"},
            ]),
        ]
    ),
    (
        "Bóc trần sự thật về phương án đánh nhanh",
        "A strategic war room briefing table on clean white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Sự thật mất lòng là, nếu giữ nguyên phương án đánh nhanh thắng nhanh trong ba ngày đêm.", [
                {"spec": "full_scene:CH01|Historian stickman points pointer to a tactical map showing vulnerable assault lines.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "SỰ THẬT MẤT LÒNG"},
                {"spec": "concept_metaphor:none|Three direct assault arrows getting shattered against a reinforced steel defense line.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "BA NGÀY ĐÊM"},
                {"spec": "visual_diagram:none|A split scale separating Theoretical 3-Day Assault from Real Concrete Bunker Resistance.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "ẢO TƯỞNG TỐC CHIẾN"},
            ]),
            ("Quân đội ta có thể đã phơi mình trước hỏa lực bom đạn và xe tăng áp đảo của địch.", [
                {"spec": "visual_diagram:none|Tactical vulnerability zone showing exposed infantry in flat open basin terrain.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "PHƠI MÌNH TRƯỚC HỎA LỰC"},
                {"spec": "full_scene:CH01|The General reviews reconnaissance photos of newly landed enemy tank divisions.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "HỎA LỰC ÁP ĐẢO"},
            ]),
        ]
    ),
    (
        "Lời bình sắc lẹm về bản lĩnh người cầm quân",
        "A solemn historical reflection chamber on white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Đánh giá công bằng thì, việc kéo pháo ra đòi hỏi lòng dũng cảm gấp trăm lần việc phát lệnh xung phong.", [
                {"spec": "full_scene:CH01|Historian stickman speaks with profound conviction and deep emotion to camera.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐÁNH GIÁ CÔNG BẰNG"},
                {"spec": "concept_metaphor:none|A commander heart of steel weighed against the lives of tens of thousands of brothers.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "LÒNG DŨNG CẢM PHI THƯỜNG"},
                {"spec": "macro_prop:none|A bronze balance scale holding a single commander pen balanced against thousands of lives.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "BẢN LĨNH TƯỚNG"},
            ]),
            ("Người chỉ huy thiên tài là người dám lùi lại một bước để nắm chắc phần thắng vĩ đại.", [
                {"spec": "visual_diagram:none|A chess maneuver graphic showing king stepping backward to set up inevitable checkmate.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "LÙI ĐỂ CHẮC THẮNG"},
                {"spec": "still_life:none|An open leather map case containing compass and field orders stamped ĐÁNH CHẮC.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "THẮNG LỢI VĨ ĐẠI"},
            ]),
        ]
    ),
    (
        "Đỉnh cao trào bỏ lửng (Cliffhanger Peak)",
        "A dramatic nocturnal reconnaissance post on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Đại tướng đã thức trắng suốt nhiều đêm theo dõi từng chuyến bay tiếp tế của không quân Pháp.", [
                {"spec": "full_scene:CH01|The General watches distant aircraft landing lights through a mountain observation slit.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "THỨC TRẮNG NHIỀU ĐÊM"},
                {"spec": "macro_prop:none|A kerosene lamp burning low on a table stacked high with urgent reconnaissance cables.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "BÁO CÁO MẬT"},
                {"spec": "still_life:none|A pair of night field glasses resting beside a marked tactical map.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "QUAN SÁT TỪNG MỖI"},
            ]),
            ("Đúng lúc các chỉ huy đều hừng hực khí thế muốn nổ súng ngay thì bức tranh thực địa nào đã chỉ ra nguy cơ quân ta bị tiêu diệt hoàn toàn trong ba ngày?", [
                {"spec": "concept_metaphor:CH01|The General stands poised over the map as a giant warning question mark illuminates the valley.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "NGUY CƠ TIÊU DIỆT"},
                {"spec": "macro_prop:none|A giant question mark symbol hovering over the fortified Muong Thanh basin.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "SỰ THẬT KINH HOÀNG"},
            ]),
        ]
    ),
    (
        "Chuyển phễu sang bản Full và Close CTA",
        "A peaceful sunny mountain ridge overlooking Dien Bien valley on white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Xem video bản dài bên dưới để theo dõi toàn bộ chiến dịch nhé.", [
                {"spec": "full_scene:CH01|Historian stickman points down with respectful hand toward the full documentary link.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "XEM BẢN DÀI"},
                {"spec": "visual_diagram:none|A clean directional arrow pointing down to the related Dien Bien Phu full video badge.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "BẤM DƯỚI ĐÂY"},
            ]),
            ("Lưu lại ngay để cùng tự hào về lịch sử dân tộc bạn nhé.", [
                {"spec": "full_scene:CH01|The historian places hand over heart with proud smile beside channel badge on white canvas.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "LƯU LẠI NGAY"},
            ]),
        ]
    ),
]
