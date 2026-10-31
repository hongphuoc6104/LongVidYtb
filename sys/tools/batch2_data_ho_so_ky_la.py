# -*- coding: utf-8 -*-
"""Batch 2 Story Blueprint for Hồ Sơ Kỳ Lạ (channel-ho-so-ky-la).

Topic: Bí Ẩn Đèo Dyatlov (Long) & Nghịch Lý Cởi Đồ Lúc Chết Cóng (Short)
Format: V3 High-Density Narrative-Driven Adaptive Visual Pacing.
"""

from typing import Any, Dict, List, Tuple

CHANNEL_ID = "ho_so_ky_la"
CHANNEL_SLUG = "ho-so-ky-la"

# =============================================================================
# LONG EXPLAINER (16 SCENES, ~94 BEATS, ~265 SECONDS)
# =============================================================================

LONG_TOPIC = "Bí Ẩn Đèo Dyatlov: Bóc Trần 5 Giả Thuyết Hoang Đường Dưới Lăng Kính Vật Lý Hiện Đại"
LONG_AUDIENCE = "Khán giả yêu thích khám phá bí ẩn lịch sử, khoa học điều tra pháp y, tâm lý sinh tồn"
LONG_GOAL = "Giải mã toàn bộ vụ án đèo Dyatlov năm 1959 bằng mô phỏng vật lý tuyết lở và cơ chế sinh học hạ thân nhiệt"

LONG_EDITORIAL_STANCE = {
    "myth_debunked": "Chín nhà leo núi bị sát hại bởi người ngoài hành tinh, quái vật tuyết Yeti hoặc vũ khí bí mật của quân đội.",
    "why_generic_advice_fails": "Các kênh giật gân chỉ bám vào chi tiết rùng rợn để câu view mà phớt lờ các dữ liệu khí tượng và địa chất thực tế.",
    "channel_verdict": "Sự thật mất lòng là không có quái vật nào cả, chính sức mạnh tàn khốc của tự nhiên kết hợp với phản xạ sinh tồn sai lầm đã cướp đi sinh mạng của họ.",
    "tradeoff_or_blindspot": "Khoa học hiện đại đã giải thích được chín mươi phần trăm nhưng sự hoảng loạn tâm lý trong đêm tối vẫn là bí ẩn mãi mãi."
}

LONG_ACTIONABLE_VALUE = {
    "core_mechanism": "Cơ chế tuyết lở dạng phiến trễ kết hợp với phản xạ cởi đồ nghịch nhiệt khi các mao mạch ngoại vi giãn nở đột ngột.",
    "practical_rule_of_thumb": "Quy tắc sinh tồn mùa đông: không bao giờ cởi bỏ lớp giữ nhiệt dù cảm thấy nóng bừng khi nhiệt độ môi trường đang âm độ.",
    "real_world_scenario": "Đội cứu hộ vùng núi cao luôn trang bị cảm biến định vị nhiệt độ lõi để ngăn nạn nhân tự tháo trang phục."
}

LONG_PACKAGING = {
    "youtube_title": "Giải Mã Đèo Dyatlov: Sự Thật Đằng Sau 5 Giả Thuyết Hoang Đường",
    "visual_hook": "Thám tử người que cầm đèn pin rọi vào căn lều bị rách toạc giữa bão tuyết âm ba mươi độ trên sườn núi Ural",
    "text_overlay": "BÍ ẨN DYATLOV",
    "contrast_pair": "Thuyết âm mưu quái vật hoang đường vs Mô phỏng vật lý tuyết lở hiện đại",
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": ["ho so ky la", "deo dyatlov", "bi an lich su", "tuyet lo", "phap y"],
    "cta_plan": {
        "mid_cta": "Nếu bạn là người đam mê các vụ án hóc búa nhất lịch sử, hãy lưu lại video để rà soát chứng cứ nhé.",
        "close": "Giả thuyết nào về đèo Dyatlov từng khiến bạn ám ảnh nhất, hãy để lại lời bình cho Hồ Sơ Kỳ Lạ nhé.",
        "endcard_text": "HỒ SƠ KỲ LẠ"
    }
}

LONG_SOURCES = [
    {
        "id": "SRC01",
        "title": "Báo Cáo Nghiên Cứu Mô Phỏng Tuyết Lở Đèo Dyatlov",
        "reference": "Viện Công Nghệ Liên Bang Thụy Sĩ EPFL (2021). Tạp Chí Môi Trường Trái Đất.",
        "facts": [
            "Mô phỏng máy tính chứng minh một phiến tuyết dày nén chặt có thể gây chấn thương ngực tương đương tai nạn xe hơi.",
            "Nhiệt độ cơ thể khi tụt dưới ba mươi độ C gây ảo giác nóng bực khiến nạn nhân tự cởi quần áo."
        ]
    }
]

LONG_STORY_ROWS: List[Tuple[str, str, str, str, List[Tuple[str, Any]]]] = [
    (
        "Đêm định mệnh trên núi Ural",
        "A snowy mountain ridge at dusk on pure white canvas.",
        "narrative_warm",
        "lived_friction",
        [
            ("Tháng hai năm 1959, chín nhà leo núi dạn dày kinh nghiệm tiến vào dãy Ural băng giá.", [
                {"spec": "full_scene:CH01|Detective stickman in slate-grey coat opens a heavy dossier folder labeled HỒ SƠ 1959.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "THÁNG HAI 1959"},
                {"spec": "concept_metaphor:none|A hand-drawn map of the snowy Ural mountains with a red hiking route trail.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "DÃY NÚI URAL"},
            ]),
            ("Họ dựng lều trên sườn núi Kholat Syakhl, nơi người bản địa gọi là Ngọn Núi Chết.", [
                {"spec": "full_scene:CH01|A single sturdy canvas tent pitched on a steep white slope under swirling snowflakes.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "NGỌN NÚI CHẾT"},
                {"spec": "still_life:none|A hand-drawn canvas tent with glowing lamp light inside against pitch-black mountain air.", "tempo": "fast", "narrative_situation": "hook_shock", "emphasis_text": "DỰNG LỀU"},
            ]),
            ("Đó cũng là đêm cuối cùng người ta nhìn thấy cả chín người còn sống sót.", [
                {"spec": "concept_metaphor:CH01|The detective looks somberly at nine small flickering candle flames on snow.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "ĐÊM CUỐI CÙNG"},
                {"spec": "visual_diagram:none|Nine silhouette portrait frames fading gently on flat white background.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "MẤT TÍCH"},
            ]),
        ]
    ),
    (
        "Hiện trường rách toạc dị thường",
        "A frozen forensic tent site on clean white canvas.",
        "analytical_crisp",
        "lived_friction",
        [
            ("Nhiều tuần sau, đội cứu hộ tìm thấy căn lều bị rách toạc một mảng lớn từ bên trong.", [
                {"spec": "full_scene:CH01|The detective shines flashlight beam inspecting severe slash marks on canvas tent wall.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "RÁCH TỪ BÊN TRONG"},
                {"spec": "macro_prop:none|A close-up sketch of jagged knife cuts slicing through thick green canvas fabric.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "VẾT DAO RẠCH"},
            ]),
            ("Mọi đồ đạc, giày ấm và áo khoác dày vẫn còn nằm nguyên vẹn tại chỗ.", [
                {"spec": "still_life:none|Neat rows of warm fur boots and heavy winter coats resting untouched inside tent.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "ĐỒ ĐẠC NGUYÊN VẸN"},
                {"spec": "concept_metaphor:CH01|The detective ponders beside a pair of empty boots in deep puzzlement.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "BỎ LẠI GIÀY ÁO"},
            ]),
            ("Chín người đã vội vã tháo chạy ra bão tuyết âm ba mươi độ chỉ với đôi tất mỏng.", [
                {"spec": "full_scene:CH01|Faint footprint tracks in deep snow leading away down the mountain slope.", "tempo": "fast", "narrative_situation": "lived_friction", "emphasis_text": "ÂM BA MƯƠI ĐỘ"},
                {"spec": "macro_prop:none|Bare sock footprints preserved in hardened crusty white snow.", "tempo": "fast", "narrative_situation": "lived_friction", "emphasis_text": "CHÂN TRẦN"},
            ]),
        ]
    ),
    (
        "Những thi thể không còn nguyên vẹn",
        "A forensic investigation table on white canvas.",
        "analytical_crisp",
        "lived_friction",
        [
            ("Cách căn lều một dặm, các thi thể lần lượt được phát hiện trong tư thế kỳ lạ.", [
                {"spec": "full_scene:CH01|The detective reviews forensic location sketches pinned to a standing blackboard.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "MỘT DẶM ĐƯỜNG"},
                {"spec": "visual_diagram:none|A topographical slope chart showing where bodies were discovered across forest edge.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "SƠ ĐỒ HIỆN TRƯỜNG"},
            ]),
            ("Một số người chỉ mặc đồ lót, trong khi những người khác mang chấn thương ngực nghiêm trọng.", [
                {"spec": "concept_metaphor:CH01|A medical x-ray card showing crushed rib cage with no external skin wounds.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "GÃY XƯƠNG SƯỜN"},
                {"spec": "visual_diagram:none|Forensic inspection notes highlighting zero external bruises despite internal fractures.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KHÔNG VẾT BẦM"},
            ]),
            ("Kỳ lạ hơn, trên thi thể không hề có bất kỳ dấu vết bầm dập hay xô xát nào bên ngoài.", [
                {"spec": "full_scene:CH01|The detective shakes head scrutinizing autopsy reports with magnifying glass.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KHÔNG VẾT ĐÁNH"},
                {"spec": "still_life:none|A magnifying glass resting over a clean forensic evidence report paper.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BÍ ẨN TỘT CÙNG"},
            ]),
        ]
    ),
    (
        "Làn sóng giả thuyết hoang đường",
        "A newspaper archive wall on clean white background.",
        "analytical_crisp",
        "lived_friction",
        [
            ("Suốt sáu thập kỷ, hàng loạt thuyết âm mưu giật gân đã được thêu dệt nên.", [
                {"spec": "full_scene:CH01|The detective walks past wall covered in sensational yellow tabloid headlines.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "SÁU THẬP KỶ"},
                {"spec": "macro_prop:none|Newspaper headlines flashing words like NGƯỜI NGOÀI HÀNH TINH and QUÁI VẬT.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "THUYẾT ÂM MƯU"},
            ]),
            ("Người thì khẳng định họ bị quái vật tuyết tấn công, kẻ lại đồn vũ khí bí mật thử nghiệm.", [
                {"spec": "concept_metaphor:none|A silhouette of a mythical yeti creature fading into blowing mountain snow.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "QUÁI VẬT TUYẾT"},
                {"spec": "visual_diagram:none|A split card showing Alien Flying Saucer on left and Secret Rocket Missile on right.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "TÊN LỬA BÍ MẬT"},
            ]),
            ("Những câu chuyện kỳ quặc chỉ làm lu mờ đi sự thật khoa học đang chờ được hé mở.", [
                {"spec": "full_scene:CH01|The detective brushes away exaggerated sensational clippings revealing a clean map.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "GẠT BỎ ĐỒN ĐOÁN"},
                {"spec": "concept_metaphor:none|A thick cloud of sensational fog clearing away under bright white analytical light.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "SỰ THẬT KHOA HỌC"},
            ]),
        ]
    ),
    (
        "Bác bỏ giả thuyết tuyết lở truyền thống",
        "A geological slope testing laboratory on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Các nhà điều tra ban đầu từng bác bỏ tuyết lở vì độ dốc sườn núi quá thoai thoải.", [
                {"spec": "full_scene:CH01|The detective measures a gentle mountain angle using an inclinometer instrument.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "DỐC THOAI THOẢI"},
                {"spec": "visual_diagram:none|A geometric diagram showing slope angle at only twenty-three degrees.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HAI MƯƠI BA ĐỘ"},
            ]),
            ("Hiện trường cũng không có dấu vết của một trận lở tuyết khổng lồ quét qua sườn đồi.", [
                {"spec": "concept_metaphor:CH01|The detective looks across smooth undisturbed snow fields under cold sky.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KHÔNG DẤU VẾT LỞ"},
                {"spec": "still_life:none|A neat undisturbed snow surface showing zero boulder debris or path gouges.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TUYẾT BÌNH THƯỜNG"},
            ]),
            ("Điều này khiến giới nghiên cứu bế tắc và đẩy vụ án vào vòng huyền bí không lời giải.", [
                {"spec": "full_scene:CH01|The detective closes the thick case folder with a contemplative expression.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BẾ TẮC NĂM THÁNG"},
                {"spec": "macro_prop:none|A massive interrogation question mark stamping the front of the case archive.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CHƯA CÓ LỜI GIẢI"},
            ]),
        ]
    ),
    (
        "Lời bình sắc bén: Sự thật mất lòng",
        "A sharp analytical room with blackboard notes on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Sự thật mất lòng là, con người luôn thích những lời giải kỳ quái hơn sự thật tự nhiên đơn giản.", [
                {"spec": "full_scene:CH01|The detective steps forward speaking directly to camera with keen insight.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "SỰ THẬT MẤT LÒNG"},
                {"spec": "concept_metaphor:none|A shiny fiction novel covering up an open textbook of physics equations.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "THÍCH KỲ QUÁI"},
            ]),
            ("Đánh giá công bằng thì, cái bẫy lớn nhất là đánh giá thấp sức mạnh khắc nghiệt của băng giá.", [
                {"spec": "full_scene:CH01|The detective points to an ice crystal diagram drawn on blackboard.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐÁNH GIÁ CÔNG BẰNG"},
                {"spec": "visual_diagram:none|A thermometer dropping below freezing with the bold caption SỨC MẠNH BĂNG GIÁ.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "CÁI BẪY CHỦ QUAN"},
            ]),
            ("Đừng nghe lời đồn quái vật hoang đường khi các quy luật vật lý đã giải mã trọn vẹn thảm kịch.", [
                {"spec": "concept_metaphor:CH01|The detective discards a sensational magazine while holding a physics simulation sheet.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "QUY LUẬT VẬT LÝ"},
                {"spec": "macro_prop:none|An open scientific research journal displaying aerodynamic wind flow calculations.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "KHOA HỌC THỰC CHỨNG"},
            ]),
        ]
    ),
    (
        "Điểm dừng hồ sơ và Mid-CTA",
        "A warm study lamp corner with steaming coffee on white canvas.",
        "narrative_warm",
        "structural_model",
        [
            ("Vụ án này là lời nhắc nhở sinh tử về sự nguy hiểm khôn lường của thiên nhiên.", [
                {"spec": "full_scene:CH01|The detective sits pensively beside a steaming mug under warm lamp light.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LỜI NHẮC SINH TỬ"},
                {"spec": "still_life:none|A brass pocket compass resting atop a detailed mountain expedition map.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LA BÀN"},
            ]),
            ("Nếu bạn là người đam mê các vụ án hóc búa nhất lịch sử, hãy lưu lại video để rà soát chứng cứ nhé.", [
                {"spec": "full_scene:CH01|The detective gestures with a warm friendly nod toward the bookmark save icon.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LƯU LẠI RÀ SOÁT"},
                {"spec": "macro_prop:none|A clean ribbon bookmark drawn with crisp detective hat emblem on white background.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LƯU VIDEO"},
            ]),
            ("Bây giờ, chúng ta sẽ mở ra lời giải mang tính đột phá từ các nhà khoa học Thụy Sĩ.", [
                {"spec": "concept_metaphor:CH01|The detective unrolls a high-tech computer simulation printout across desk.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "LỜI GIẢI ĐỘT PHÁ"},
                {"spec": "visual_diagram:none|A computer-aided simulation mesh showing snow stress distribution on mountain slope.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "MÔ PHỎNG MÁY TÍNH"},
            ]),
        ]
    ),
    (
        "Nghiên cứu đột phá của viện EPFL năm 2021",
        "A modern physics research lab on clean white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Năm 2021, nhóm chuyên gia viện EPFL đã tái hiện chính xác điều kiện đêm định mệnh.", [
                {"spec": "full_scene:CH01|The detective examines a high-precision digital 3D model of the mountain ridge.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TÁI HIỆN ĐÊM ĐỊNH MỆNH"},
                {"spec": "visual_diagram:none|A digital topographical wireframe of Kholat Syakhl slope rendered in clean lineart.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "MÔ HÌNH 3D"},
            ]),
            ("Họ phát hiện một cơ chế lở tuyết rất đặc biệt mang tên tuyết lở dạng phiến trễ.", [
                {"spec": "concept_metaphor:CH01|The detective points to a dense solid sheet of snow resting on a fragile sugar-like base.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "TUYẾT LỞ DẠNG PHIẾN"},
                {"spec": "visual_diagram:none|Cross-section of snow pack showing hard top slab over weak crumbly depth hoar layer.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "LỚP NỀN YẾU"},
            ]),
            ("Việc đoàn leo núi đào một gờ tuyết để chắn gió đã vô tình kích hoạt quả bom nổ chậm.", [
                {"spec": "full_scene:CH01|Cartoon mountaineer stickman shoveling a shelf cut into the slope to pitch tent.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "ĐÀO GỜ CHẮN GIÓ"},
                {"spec": "concept_metaphor:none|A small crack propagating silently across a solid horizontal snow slab.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "KÍCH HOẠT NỔ CHẬM"},
            ]),
        ]
    ),
    (
        "Cơ chế tuyết lở dạng phiến trễ",
        "A mechanical impact testing setup on white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Gió mạnh dồn thêm tuyết dày lên trên phiến băng suốt nhiều giờ trong đêm.", [
                {"spec": "full_scene:CH01|Strong howling wind vectors driving dense snow drifts onto the upper mountain ledge.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "GIÓ DỒN TUYẾT DÀY"},
                {"spec": "visual_diagram:none|A force vector diagram showing progressive weight accumulation on the unstable slab.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "GIA TĂNG TRỌNG LỰNG"},
            ]),
            ("Đến nửa đêm, toàn bộ tảng tuyết đặc như bê tông trượt xuống đè bẹp căn lều.", [
                {"spec": "concept_metaphor:CH01|A massive solid snow block collapsing straight downward onto tent frame.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "SẬP LỀU ĐÊM KHUYA"},
                {"spec": "macro_prop:none|A heavy stone-like block of hard packed snow crushing flexible tent poles.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "ĐẶC NHƯ BÊ TÔNG"},
            ]),
            ("Sức nặng kinh hoàng này giải thích chính xác các vết nứt xương sườn của các nạn nhân.", [
                {"spec": "full_scene:CH01|The detective compares car crash test data with forensic autopsy measurements.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "SỨC NẶNG KINH HOÀNG"},
                {"spec": "visual_diagram:none|Impact chart showing compression force matching blunt traumatic car impact.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "GIẢI MÃ CHẤN THƯƠNG"},
            ]),
        ]
    ),
    (
        "Vì sao họ phải rạch lều tháo chạy",
        "A nocturnal snowstorm survival scene on clean white canvas.",
        "narrative_warm",
        "structural_model",
        [
            ("Bị tuyết nén chặt cửa chính, họ buộc phải dùng dao rạch vách lều để thoát ra ngoài.", [
                {"spec": "full_scene:CH01|A hand rapidly slashes tent canvas with pocket knife as snow spills inside.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "RẠCH LỀU THOÁT RA"},
                {"spec": "concept_metaphor:none|A knife blade slicing through trapped darkness toward the stormy white outdoors.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "LỐI THOÁT KHẨN CẤP"},
            ]),
            ("Trong bóng tối mịt mùng và bão tuyết gầm rú, họ lo sợ một đợt sạt lở thứ hai ập đến.", [
                {"spec": "full_scene:CH01|Mountaineers struggle forward through howling white storm gusts holding each other.", "tempo": "normal", "narrative_situation": "story_action", "emphasis_text": "BÃO TUYẾT GẦM RÚ"},
                {"spec": "concept_metaphor:none|Massive swirling vortex of snowflakes obscuring all ground references.", "tempo": "normal", "narrative_situation": "story_action", "emphasis_text": "SỢ ĐỢT LỞ THỨ HAI"},
            ]),
            ("Họ dìu những người bị thương chạy vội xuống khu rừng phía dưới để tìm nơi trú ẩn.", [
                {"spec": "full_scene:CH01|The mountaineers support an injured comrade descending toward a distant tree line.", "tempo": "normal", "narrative_situation": "story_action", "emphasis_text": "DÌU NHAU XUỐNG RỪNG"},
                {"spec": "visual_diagram:none|A clean directional arrow pointing from high exposed ridge down to sheltering forest.", "tempo": "normal", "narrative_situation": "story_action", "emphasis_text": "TÌM CHỖ TRÚ"},
            ]),
        ]
    ),
    (
        "Nghịch lý cởi đồ trong giá rét",
        "A biological temperature study room on white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Nhưng điều gây hoang mang nhất cho các nhà điều tra là vì sao có người tự cởi bỏ quần áo.", [
                {"spec": "full_scene:CH01|The detective points to medical research chart on severe hypothermia.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "NGHỊCH LÝ CỞI ĐỒ"},
                {"spec": "visual_diagram:none|A medical diagram titled PARADOXICAL UNDRESSING with a human thermal outline.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "TỰ CỞI ÁO QUẦN"},
            ]),
            ("Y học hiện đại giải thích rằng đây là hội chứng cởi đồ nghịch nhiệt khi sắp chết cóng.", [
                {"spec": "concept_metaphor:CH01|A freezing stickman in snow suddenly imagines being engulfed by warm gentle waves.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "ẢO GIÁC NÓNG BỰC"},
                {"spec": "visual_diagram:none|Thermoregulation chart showing blood vessels dilating suddenly near cardiac failure.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "DÃN MAO MẠCH"},
            ]),
            ("Khi cơ thể kiệt sức, các mao mạch ngoại vi dãn nở đột ngột gây ảo giác nóng bừng như thiêu đốt.", [
                {"spec": "full_scene:CH01|The freezing stickman instinctively unbuttons shirt feeling an overwhelming false fever.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "NÓNG NHƯ THIÊU"},
                {"spec": "macro_prop:none|A thermometer spiking falsely with warm red waves before dropping to absolute zero.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CƠ CHẾ PHẢN VỆ"},
            ]),
        ]
    ),
    (
        "Bình luận về điểm mù của tâm lý sinh tồn",
        "A quiet contemplative evidence chamber on clean white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Điểm mù lớn nhất khi đối mặt với tử thần là những mệnh lệnh sai lầm của bộ não hoảng loạn.", [
                {"spec": "full_scene:CH01|The detective speaks with deep reflection holding a small pocket lantern.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐIỂM MÙ LỚN NHẤT"},
                {"spec": "concept_metaphor:none|A small lantern shining steady light through wild raging blizzard gusts.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "NÃO BỘ HOẢNG LOẠN"},
            ]),
            ("Cái giá phải trả cho một giây lơ là trước sự thịnh nộ của bão tuyết là sự trừng phạt nghiệt ngã nhất.", [
                {"spec": "full_scene:CH01|The detective gazes toward the quiet snow mountain ridge with deep solemnity.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "CÁI GIÁ PHẢI TRẢ"},
                {"spec": "visual_diagram:none|A memorial marker standing tall against a vast serene white snowy expanse.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "QUY LUẬT TỰ NHIÊN"},
            ]),
            ("Nhìn thẳng vào thực tế thì, sự dũng cảm và tinh thần đồng đội của họ xứng đáng được tôn vinh.", [
                {"spec": "concept_metaphor:CH01|Nine stickmen standing side by side holding hands in eternal solidarity.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "TINH THẦN ĐỒNG ĐỘI"},
                {"spec": "macro_prop:none|Nine glowing friendship lanterns standing together against cold darkness.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "XỨNG ĐÁNG TÔN VINH"},
            ]),
        ]
    ),
    (
        "Quy tắc ngón tay cái: Sinh tồn vùng băng giá",
        "A survival training classroom on clean white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Từ thảm kịch Dyatlov, các chuyên gia đúc kết quy tắc sinh tồn sống còn trong giá rét.", [
                {"spec": "full_scene:CH01|The detective points marker to a survival checklist board labeled QUY TẮC BĂNG GIÁ.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "QUY TẮC SINH TỒN"},
                {"spec": "visual_diagram:none|A bulleted survival guideline card with three bold winter survival rules.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BÀI HỌC ĐẮT GIÁ"},
            ]),
            ("Tuyệt đối không trút bỏ lớp trang phục giữ ấm dù bạn có cảm thấy nóng bực đến mức nào.", [
                {"spec": "full_scene:CH01|The stickman zips heavy parkas collar securely tight against icy winds.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "KHÔNG CỞI ÁO ẤM"},
                {"spec": "macro_prop:none|A heavy winter parka jacket with a solid locked zipper emblem.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "KHÓA KÉO CHẶT"},
            ]),
            ("Đó là ảo giác tử thần trước khi ngưng tim, hãy cuộn tròn người và bảo vệ phần ngực.", [
                {"spec": "concept_metaphor:CH01|The stickman assumes a tight fetal survival tuck preserving vital core warmth.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "BẢO VỆ PHẦN NGỰC"},
                {"spec": "visual_diagram:none|A human body heat distribution graphic showing critical organs concentrated in core.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "GIỮ NHIỆT LÕI"},
            ]),
        ]
    ),
    (
        "Cách chọn vị trí hạ trại an toàn",
        "An outdoor mountain expedition planning table on white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Khi cắm trại trên sườn đồi phủ tuyết, không bao giờ đào sâu tạo thành vách đứng.", [
                {"spec": "full_scene:CH01|The detective demonstrates safe vs dangerous tent pitching on a table model.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CHỌN NƠI HẠ TRẠI"},
                {"spec": "visual_diagram:none|Side-by-side comparison: Vách đứng nguy hiểm (Sai) vs Sườn thoải tự nhiên (Đúng).", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KHÔNG ĐÀO VÁCH ĐỨNG"},
            ]),
            ("Luôn kiểm tra tầng tuyết xốp bên dưới trước khi dựng cọc neo giữ lều trại.", [
                {"spec": "concept_metaphor:CH01|The stickman inserts a snow probe rod deep into the snowpack checking density.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "KIỂM TRA NỀN TUYẾT"},
                {"spec": "still_life:none|A marked avalanche probe rod showing measurement depth hash marks in black ink.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "ĐO ĐỘ NÉN"},
            ]),
            ("Một sự cẩn trọng nhỏ trong chuẩn bị sẽ cứu vớt mạng sống của cả đoàn thám hiểm.", [
                {"spec": "full_scene:CH01|The detective gives a firm nod of reassurance beside a safe mountain campsite.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "CẨN TRỌNG TỐI ĐA"},
                {"spec": "macro_prop:none|A sturdy safety anchor peg firmly rooted into rock beneath snow.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "AN TOÀN TUYỆT ĐỐI"},
            ]),
        ]
    ),
    (
        "Bài học 30 giây rà soát rủi ro",
        "A peaceful quiet forensic library desk on white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Trước mỗi chuyến hành trình vào thiên nhiên hoang dã, hãy làm bài test ba mươi giây.", [
                {"spec": "full_scene:CH01|The detective prepares a small emergency survival tin box on the wooden desk.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BÀI TEST 30 GIÂY"},
                {"spec": "visual_diagram:none|A three-item checklist: Đường Thoát Khẩn, Thiết Bị Báo Nhiệt, Đèn Định Vị.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "RÀ SOÁT RỦI RO"},
            ]),
            ("Hãy tự hỏi: bạn đã có phương án thoát hiểm khẩn cấp nếu căn lều bị phá hủy chưa?", [
                {"spec": "concept_metaphor:CH01|The stickman reflects thoughtfully checking a backup survival foil blanket.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "PHƯƠNG ÁN THOÁT HIỂM"},
                {"spec": "visual_diagram:none|A primary shelter icon with a clear secondary backup emergency arrow.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "KẾ HOẠCH DỰ PHÒNG"},
            ]),
            ("Sự chuẩn bị kỹ lưỡng là ranh giới mong manh giữa một chuyến đi tuyệt vời và thảm kịch.", [
                {"spec": "full_scene:CH01|The detective closes survival pack securely with a confident steady look.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "RANH GIỚI SINH TỬ"},
                {"spec": "macro_prop:none|A gleaming silver emergency survival foil blanket folded neatly in half.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "CHUẨN BỊ KỸ"},
            ]),
        ]
    ),
    (
        "Khép lại hồ sơ và kết nối người xem",
        "A solemn evening detective study desk on pure white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Bí ẩn đèo Dyatlov cuối cùng đã được khoa học vén màn sau hơn sáu mươi năm u tối.", [
                {"spec": "full_scene:CH01|The detective ties a red archive ribbon around the finalized case file folder.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KHÉP LẠI HỒ SƠ"},
                {"spec": "concept_metaphor:none|A bright beam of morning sunlight illuminating an old historic case archive.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "VÉN MÀN BÍ ẨN"},
            ]),
            ("Sự thật luôn nằm ở những quy luật tự nhiên nếu chúng ta kiên nhẫn kiếm tìm bằng lý trí.", [
                {"spec": "full_scene:CH01|The detective stands calmly holding a leather notebook looking outward with clarity.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LÝ TRÍ KHOA HỌC"},
                {"spec": "macro_prop:none|An illuminated antique microscope resting on solid mahogany desk on white canvas.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KIÊN NHẪN TÌM KIẾM"},
            ]),
            ("Giả thuyết nào về đèo Dyatlov từng khiến bạn ám ảnh nhất, hãy để lại lời bình cho Hồ Sơ Kỳ Lạ nhé.", [
                {"spec": "full_scene:CH01|The detective tips brim of slate-grey hat with a respectful nod to the audience.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LỜI BÌNH CỦA BẠN"},
                {"spec": "white_card:none|Channel endcard illustration on flat canvas with channel mascot and clear text HỒ SƠ KỲ LẠ.", "tempo": "slow", "narrative_situation": "mechanism_step", "is_endcard": True},
            ]),
        ]
    ),
]

# =============================================================================
# SHORT SPIN-OFF (5 SCENES, ~19 BEATS, ~43 SECONDS, CLIFFHANGER FUNNEL)
# =============================================================================

SHORT_TOPIC = "Vì Sao 9 Nạn Nhân Đèo Dyatlov Lại Tự Cởi Hết Quần Áo Dưới Trời Âm 30 Độ?"
SHORT_AUDIENCE = "Khán giả tò mò về bí ẩn lịch sử, pháp y hiện đại và tâm lý sinh tồn mùa đông"
SHORT_GOAL = "Giải mã hiện tượng cởi đồ nghịch nhiệt và cắt phễu ở đỉnh cao trào về bí ẩn vết chấn thương ép ngực"

SHORT_EDITORIAL_STANCE = {
    "myth_debunked": "Chín nhà leo núi bị quái vật tuyết hoặc người ngoài hành tinh lột đồ tra tấn.",
    "why_generic_advice_fails": "Các kênh giật gân chỉ bám vào chi tiết rùng rợn để câu view mà phớt lờ các dữ liệu khí tượng và địa chất thực tế.",
    "channel_verdict": "Sự thật mất lòng là không có quái vật nào cả, chính sức mạnh tàn khốc của tự nhiên đã cướp đi sinh mạng của họ.",
    "tradeoff_or_blindspot": "Khoa học hiện đại đã giải thích được chín mươi phần trăm nhưng sự hoảng loạn tâm lý trong đêm tối vẫn là bí ẩn."
}

SHORT_ACTIONABLE_VALUE = {
    "core_mechanism": "Cơ chế tuyết lở dạng phiến trễ kết hợp với phản xạ cởi đồ nghịch nhiệt khi các mao mạch ngoại vi giãn nở đột ngột.",
    "practical_rule_of_thumb": "Quy tắc sinh tồn mùa đông: không bao giờ cởi bỏ lớp giữ nhiệt dù cảm thấy nóng bừng khi nhiệt độ môi trường âm.",
    "real_world_scenario": "Đội cứu hộ vùng núi cao luôn trang bị cảm biến định vị nhiệt độ lõi để ngăn nạn nhân tự tháo trang phục."
}

SHORT_PACKAGING = {
    "youtube_title": "Vì Sao Nạn Nhân Đèo Dyatlov Tự Cởi Quần Áo Dưới Trời Âm 30 Độ?",
    "visual_hook": "Thám tử rọi đèn pin vào căn lều bị rạch toạc giữa bão tuyết âm 30 độ",
    "text_overlay": "BÍ ẨN CỞI ĐỒ",
    "contrast_pair": "Quái vật tấn công vs Hội chứng cởi đồ nghịch nhiệt",
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": ["ho so ky la", "dyatlov", "bi an", "shorts"],
    "cta_plan": {
        "cliffhanger_peak": "Đúng lúc các nhà điều tra bế tắc nhất thì phát hiện rùng mình về các vết thương ép ngực không có dấu vết bầm tím bên ngoài đã hé lộ sự thật kinh hoàng gì?",
        "bridge": "Xem video bản dài bên dưới để mở toàn bộ hồ sơ vụ án nhé.",
        "close": "Lưu lại ngay để cùng khám phá các vụ án tiếp theo bạn nhé.",
        "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
    }
}

SHORT_SOURCES = [
    {
        "id": "SRC01",
        "title": "Báo Cáo Nghiên Cứu Mô Phỏng Tuyết Lở Đèo Dyatlov",
        "reference": "Viện Công Nghệ Liên Bang Thụy Sĩ EPFL (2021). Tạp Chí Môi Trường Trái Đất.",
        "facts": [
            "Mô phỏng máy tính chứng minh một phiến tuyết dày nén chặt có thể gây chấn thương ngực tương đương tai nạn xe hơi."
        ]
    }
]

SHORT_STORY_ROWS: List[Tuple[str, str, str, str, List[Tuple[str, Any]]]] = [
    (
        "Mở màn rùng rợn tại hiện trường",
        "A frozen snow slope at night on white canvas.",
        "narrative_warm",
        "hook",
        [
            ("Năm 1959, chín nhà leo núi trên đèo Dyatlov đã làm một điều không ai giải thích nổi.", [
                {"spec": "full_scene:CH01|The detective shines bright beam onto a frozen hiking tent buried in deep snow.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "ĐIỀU KHÔNG THỂ GIẢI THÍCH"},
                {"spec": "macro_prop:none|A hand-drawn calendar page for 1959 circled in blood-red marker on white canvas.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "NĂM 1959"},
            ]),
            ("Giữa cơn bão tuyết âm ba mươi độ, họ rạch lều tháo chạy và tự cởi bỏ toàn bộ quần áo ấm.", [
                {"spec": "visual_diagram:none|A thermometer reading minus thirty degrees beside discarded winter boot icons.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "ÂM BA MƯƠI ĐỘ"},
                {"spec": "concept_metaphor:CH01|The detective uncovers a pair of frozen socks lying abandoned on ice crust.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "TỰ CỞI ĐỒ"},
                {"spec": "still_life:none|A flashlight resting on frozen crust reflecting sharp white glare.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "BỎ CHẠY"},
            ]),
        ]
    ),
    (
        "Bóc trần giả thuyết quái vật",
        "A forensic archive study space on clean white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Sự thật mất lòng là, không có người ngoài hành tinh hay quái vật tuyết nào lột đồ của họ cả.", [
                {"spec": "full_scene:CH01|The detective shakes head firmly crossing out dramatic comic book monster sketches.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "SỰ THẬT MẤT LÒNG"},
                {"spec": "concept_metaphor:none|A mythical yeti footprint revealed to be an ordinary wind-carved snow drift.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "KHÔNG CÓ QUÁI VẬT"},
            ]),
            ("Thủ phạm thật sự chính là một phản xạ sinh học chết người mang tên cởi đồ nghịch nhiệt.", [
                {"spec": "visual_diagram:none|Medical typography card reading NGHỊCH LÝ CỞI ĐỒ NGHỊCH NHIỆT in bold black marker.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "CỞI ĐỒ NGHỊCH NHIỆT"},
                {"spec": "full_scene:CH01|The detective points to an anatomical chart of blood vessels under severe freeze.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "PHẢN XẠ SINH HỌC"},
                {"spec": "concept_metaphor:none|A thermal imaging card showing rapid heat escape from core to extremities.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "THOÁT NHIỆT"},
            ]),
        ]
    ),
    (
        "Lời bình sắc bén về ảo giác tử thần",
        "A biological examination laboratory on white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Đánh giá công bằng thì, khi cơ thể sắp bị đóng băng, các mao mạch ngoại vi đột ngột giãn nở.", [
                {"spec": "full_scene:CH01|The detective speaks with solemn authority examining a vascular micro-slide.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐÁNH GIÁ CÔNG BẰNG"},
                {"spec": "concept_metaphor:none|A network of capillary veins widening rapidly releasing a rush of warm blood.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "MAO MẠCH GIÃN NỞ"},
            ]),
            ("Nó đánh lừa não bộ bằng một cơn sốt nóng bực giả tạo, khiến nạn nhân hoảng loạn xé toạc lớp áo ấm.", [
                {"spec": "visual_diagram:none|A dual-column medical card showing False Fever Sensation on top versus Actual Freezing Core below.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CƠN SỐT GIẢ TẠO"},
                {"spec": "still_life:none|A frozen watch frozen at midnight next to a button torn from a winter coat.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "XÉ TOẠC ÁO ẤM"},
                {"spec": "concept_metaphor:CH01|The detective measures ice crystallization patterns on fabric weave.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "ĐÓNG BĂNG"},
            ]),
        ]
    ),
    (
        "Đỉnh cao trào bỏ lửng (Cliffhanger Peak)",
        "A dark mystery crime investigation room on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Nhưng điều kỳ dị nhất vẫn chưa dừng lại ở đó.", [
                {"spec": "full_scene:CH01|The detective pauses dramatically holding a confidential red folder in air.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "ĐIỀU KỲ DỊ NHẤT"},
                {"spec": "macro_prop:none|A heavy red wax seal with an exclamation mark ready to be broken open.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "CHƯA DỪNG LẠI"},
            ]),
            ("Đúng lúc các nhà điều tra bế tắc nhất thì phát hiện rùng mình về các vết thương ép ngực không có dấu vết bầm tím bên ngoài đã hé lộ sự thật kinh hoàng gì?", [
                {"spec": "concept_metaphor:CH01|The detective holds up an autopsy x-ray with massive chest fractures before a spotlight.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "KHÔNG VẾT BẦM TÍM"},
                {"spec": "macro_prop:none|A giant question mark hovering over a cracked rib cage medical diagram.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "SỰ THẬT KINH HOÀNG"},
                {"spec": "still_life:none|An archival red wax seal stamped with top-secret classification insignia on white canvas.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "HỒ SƠ MẬT"},
            ]),
        ]
    ),
    (
        "Chuyển phễu sang bản Full và Close CTA",
        "A peaceful sunny investigation office on pure white background.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Xem video bản dài bên dưới để mở toàn bộ hồ sơ vụ án nhé.", [
                {"spec": "full_scene:CH01|The detective points down with hand toward the full episode link below.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "XEM BẢN DÀI"},
                {"spec": "visual_diagram:none|A bold directional arrow pointing down to the related Dyatlov full case link.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "BẤM DƯỚI ĐÂY"},
            ]),
            ("Lưu lại ngay để cùng khám phá các vụ án tiếp theo bạn nhé.", [
                {"spec": "full_scene:CH01|The detective tips hat with a subtle friendly smile beside channel badge on white canvas.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "LƯU LẠI NGAY"},
            ]),
        ]
    ),
]
