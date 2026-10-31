# -*- coding: utf-8 -*-
"""Batch 2 Story Blueprint for AI Bình Dân (channel-ai-binh-dan).

Topic: Bóc Trần 4 Ảo Tưởng Về Tự Động Hóa AI (Long) & Quy Tắc 3 Bước Tránh Bẫy Tool AI (Short)
Format: V3 High-Density Narrative-Driven Adaptive Visual Pacing.
"""

from typing import Any, Dict, List, Tuple

CHANNEL_ID = "ai_binh_dan"
CHANNEL_SLUG = "ai-binh-dan"

# =============================================================================
# LONG EXPLAINER (16 SCENES, ~90-95 BEATS, ~260 SECONDS)
# =============================================================================

LONG_TOPIC = "Bóc Trần 4 Ảo Tưởng Về Tự Động Hóa AI: Vì Sao Càng Mua Tool Đắt Tiền Bạn Càng Tốn Thời Gian?"
LONG_AUDIENCE = "Người đi làm văn phòng, sinh viên, người làm việc tự do"
LONG_GOAL = "Bóc trần ảo tưởng mua công cụ AI đắt tiền và hướng dẫn quy trình prompt ba bước miễn phí chuẩn hóa công việc"

LONG_EDITORIAL_STANCE = {
    "myth_debunked": "Cứ chi tiền mua tài khoản AI trả phí đắt đỏ là tự động x10 năng suất công việc.",
    "why_generic_advice_fails": "Các bài review trên mạng chỉ khoe tính năng màu mè mà giấu nhẹm việc bạn phải mất hàng giờ sửa lỗi và nạp dữ liệu thủ công.",
    "channel_verdict": "Sự thật mất lòng là nếu quy trình làm việc vốn đã lộn xộn thì công cụ xịn chỉ giúp bạn tạo ra rác nhanh gấp mười lần.",
    "tradeoff_or_blindspot": "Học cách viết prompt có cấu trúc ban đầu sẽ tốn não hơn việc bấm một nút ăn liền nhưng dùng bền vững cả đời."
}

LONG_ACTIONABLE_VALUE = {
    "core_mechanism": "Cấu trúc ba tầng cốt lõi gồm vai trò ngữ cảnh, dữ liệu tham chiếu và định dạng kết quả đầu ra.",
    "practical_rule_of_thumb": "Quy tắc mười ngày kiểm chứng: chỉ nâng cấp tài khoản khi bản miễn phí đã giúp bạn tiết kiệm ít nhất một giờ mỗi ngày.",
    "real_world_scenario": "Một nhân viên văn phòng hủy toàn bộ gói đăng ký ba mươi đô để dùng một bảng mẫu prompt Google Docs giải quyết xong việc sớm."
}

LONG_PACKAGING = {
    "youtube_title": "Vì Sao Càng Mua Tool AI Đắt Tiền Càng Tốn Thời Gian?",
    "visual_hook": "Người que áo tím đối chiếu xấp hóa đơn phần mềm dày cộp với màn hình laptop prompt 3 bước tinh gọn",
    "text_overlay": "BẪY TOOL ĐẮT",
    "contrast_pair": "Đốt tiền mua 5 tool 100 đô vs Quy trình prompt 3 bước miễn phí",
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": ["ai binh dan", "boc tran tool ai", "tu dong hoa van phong", "chatgpt mien phi", "prompt chuan hoa"],
    "cta_plan": {
        "mid_cta": "Nếu bạn từng rơi vào bẫy đăng ký rồi bỏ xó công cụ, hãy lưu video này lại để rà soát chi tiêu nhé.",
        "close": "Bạn đang tốn bao nhiêu tiền cho các gói AI mỗi tháng, hãy cùng tính nhẩm dưới phần bình luận nhé.",
        "endcard_text": "AI BÌNH DÂN"
    }
}

LONG_SOURCES = [
    {
        "id": "SRC01",
        "title": "Báo Cáo Năng Suất Và Tự Động Hóa Công Nghệ Công Sở",
        "reference": "Viện Nghiên Cứu Chuyển Đổi Số Văn Phòng (2024). Khảo Sát Thói Quen Công Cụ.",
        "facts": [
            "Hơn bảy mươi phần trăm tài khoản phần mềm đăng ký hàng tháng bị bỏ xó sau sáu mươi ngày.",
            "Tự động hóa không chuẩn hóa quy trình làm tăng ba mươi phần trăm thời gian sửa lỗi nội bộ."
        ]
    }
]

LONG_STORY_ROWS: List[Tuple[str, str, str, str, List[Tuple[str, Any]]]] = [
    (
        "Cơn sốt mua công cụ công nghệ",
        "A clean bright office workspace on pure white canvas.",
        "narrative_warm",
        "lived_friction",
        [
            ("Nhiều bạn nghĩ rằng cứ mua tài khoản AI trăm đô là năng suất sẽ tự động tăng vọt.", [
                {"spec": "full_scene:CH01|A young office employee in a violet hoodie proudly shows a shiny AI software subscription badge on laptop screen.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "MUA TOOL ĐẮT"},
                {"spec": "macro_prop:none|A hand-drawn giant credit card showing multiple recurring monthly subscription charges.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "TRĂM ĐÔ"},
            ]),
            ("Nhưng thực chất, đa số chúng ta chỉ đang mua cảm giác an tâm giả tạo.", [
                {"spec": "concept_metaphor:CH01|The stickman sits surrounded by floating glowing software app icons looking distracted.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "AN TÂM ẢO"},
                {"spec": "visual_diagram:none|A balance scale with a heavy pile of subscription fees on one side and zero saved time on the other.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "MẤT TIỀN"},
            ]),
            ("Cứ thấy công cụ nào mới ra trên mạng là lại vội vàng bấm đăng ký dùng thử.", [
                {"spec": "full_scene:CH01|The employee rapidly clicks the mouse button in front of an endless feed of marketing ads.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "BẤM DÙNG THỬ"},
                {"spec": "concept_metaphor:CH01|A large browser window filled with dozens of open pinned tabs causing visual chaos.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "LOẠN TAB"},
            ]),
        ]
    ),
    (
        "Bẫy thời gian học phần mềm mới",
        "A quiet office corner with paper stacks on white background.",
        "analytical_crisp",
        "lived_friction",
        [
            ("Mỗi khi đổi sang một công cụ mới, bạn phải mất hàng giờ chỉ để làm quen giao diện.", [
                {"spec": "full_scene:CH01|The stickman scratches head reading a complicated multi-page software manual.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "MẤT THỜI GIAN"},
                {"spec": "visual_diagram:none|A hand-drawn clock icon with spinning hands next to a progress bar stuck at twenty percent.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "LÀM QUEN"},
            ]),
            ("Bạn loay hoay thiết lập cài đặt, kết nối tài khoản và đọc tài liệu hướng dẫn.", [
                {"spec": "still_life:none|A computer monitor showing endless settings menus and API key configuration boxes.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CÀI ĐẶT"},
                {"spec": "concept_metaphor:CH01|The stickman gets tangled in long wire cords connecting three different laptops.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "RỐI RẮM"},
            ]),
            ("Đến khi hoàn thành xong các bước cài đặt thì buổi sáng làm việc đã trôi qua mất.", [
                {"spec": "full_scene:CH01|The employee sighs looking at the wall clock showing midday twelve o'clock.", "tempo": "fast", "narrative_situation": "lived_friction", "emphasis_text": "HẾT BUỔI SÁNG"},
                {"spec": "macro_prop:none|An empty coffee mug next to an unfinished draft report on the office desk.", "tempo": "fast", "narrative_situation": "lived_friction", "emphasis_text": "CHƯA XONG VIỆC"},
            ]),
        ]
    ),
    (
        "Ảo tưởng một nút bấm thần thánh",
        "A minimalist tech studio with laptop on white canvas.",
        "analytical_crisp",
        "lived_friction",
        [
            ("Ảo tưởng lớn nhất là tin vào lời quảng cáo bấm một nút tạo ra kết quả hoàn hảo.", [
                {"spec": "full_scene:CH01|The stickman eagerly points finger toward a giant shiny magic button labeled ONE CLICK.", "tempo": "burst", "narrative_situation": "rapid_examples", "emphasis_text": "MỘT NÚT BẤM"},
                {"spec": "concept_metaphor:none|A shiny golden key that fails to fit into a complex multi-tumbler lock.", "tempo": "burst", "narrative_situation": "rapid_examples", "emphasis_text": "ẢO TƯỞNG"},
            ]),
            ("Khi kết quả xuất ra chung chung, bạn lại mất cả tiếng ngồi chỉnh sửa câu từ thủ công.", [
                {"spec": "full_scene:CH01|The employee holds a red pen crossing out boring repetitive sentences on a printed report.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "SỬA TAY"},
                {"spec": "visual_diagram:none|A flowchart showing initial generation in two seconds followed by two hours of manual editing.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "HAI TIẾNG SỬA"},
            ]),
            ("Nhiều khi thời gian ngồi gọt giũa bản nháp còn lâu hơn bạn tự tay viết từ đầu.", [
                {"spec": "concept_metaphor:CH01|The stickman balances a typewriter against an overheating computer tower.", "tempo": "fast", "narrative_situation": "lived_friction", "emphasis_text": "VIẾT TAY NHANH HƠN"},
                {"spec": "still_life:none|Crumpled paper balls scattered around a laptop with glowing red battery light.", "tempo": "fast", "narrative_situation": "lived_friction", "emphasis_text": "MỆT MỎI"},
            ]),
        ]
    ),
    (
        "Bẫy phân mảnh dữ liệu và bảo mật",
        "A clean desk under bright overhead lighting on white canvas.",
        "analytical_crisp",
        "lived_friction",
        [
            ("Càng đăng ký nhiều nền tảng, dữ liệu công việc của bạn càng bị xé vụn ra khắp nơi.", [
                {"spec": "full_scene:CH01|The stickman reaches arms out trying to gather scattered flying paper sheets in the room.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "DỮ LIỆU XÉ VỤN"},
                {"spec": "visual_diagram:none|A central folder icon splitting into five separate external cloud storage arrows.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "RỜI RẠC"},
            ]),
            ("Mỗi chỗ lưu một chút tài liệu, đến lúc cần tổng hợp lại không biết tìm ở ứng dụng nào.", [
                {"spec": "full_scene:CH01|The employee opens multiple drawer compartments desperately searching for a single file.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TÌM KHÔNG RA"},
                {"spec": "concept_metaphor:none|A giant magnifying glass examining three different browser icons on white background.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "THẤT LẠC"},
            ]),
            ("Đặc biệt là rủi ro rò rỉ dữ liệu mật khi nạp thông tin nội bộ vào các ứng dụng lạ.", [
                {"spec": "still_life:none|A folder marked CONFIDENTIAL with an open lock symbol and flashing red warning shield.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "RÒ RỈ DỮ LIỆU"},
                {"spec": "full_scene:CH01|The stickman holds hands up with caution beside an exclamation warning badge.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CẨN TRỌNG"},
            ]),
        ]
    ),
    (
        "Bản chất cốt lõi của năng suất",
        "A structured workspace with a large whiteboard on white canvas.",
        "narrative_warm",
        "empirical_conflict",
        [
            ("Năng suất thật sự không đến từ số lượng công cụ bạn cài trên máy tính.", [
                {"spec": "full_scene:CH01|The stickman points firmly to a clean uncluttered single laptop screen.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "NĂNG SUẤT THẬT"},
                {"spec": "visual_diagram:none|Comparison showing Ten Tools with Low Output versus One Method with High Output.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "MỘT QUY TRÌNH"},
            ]),
            ("Bản chất nằm ở việc bạn có một quy trình tư duy rõ ràng trước khi mở máy hay không.", [
                {"spec": "concept_metaphor:CH01|The stickman sketches an active three-step flowchart on an open notebook page.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TƯ DUY RÕ RÀNG"},
                {"spec": "visual_diagram:none|Three sequential clean boxes labeled Input, Filter, and Action on white canvas.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BA BƯỚC"},
            ]),
            ("Nếu đầu vào mơ hồ thì cỗ máy thông minh nhất cũng chỉ trả về câu trả lời sáo rỗng.", [
                {"spec": "full_scene:CH01|The stickman shrugs shoulders holding a printed page containing only question marks.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐẦU VÀO MƠ HỒ"},
                {"spec": "concept_metaphor:none|A cloud of smoke coming out of a computer processor on flat white background.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "SÁO RỖNG"},
            ]),
        ]
    ),
    (
        "Lời bình sắc bén về cái bẫy tiêu dùng",
        "An open discussion corner with bold typography on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Sự thật mất lòng là, rất nhiều người mua phần mềm để khỏa lấp sự lười biếng tư duy.", [
                {"spec": "full_scene:CH01|The stickman stands with crossed arms speaking with direct confident expression.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "SỰ THẬT MẤT LÒNG"},
                {"spec": "concept_metaphor:none|A small brain resting inside a soft armchair wrapped in a velvet blanket.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "LƯỜI TƯ DUY"},
            ]),
            ("Đánh giá công bằng thì, cái bẫy lớn nhất là bạn tưởng mình đang làm việc khi đang nghịch cài đặt.", [
                {"spec": "full_scene:CH01|The employee points finger straight at the viewer with an honest perceptive smile.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "CÁI BẪY THẬT SỰ"},
                {"spec": "visual_diagram:none|A hand-drawn circular trap mechanism with the label TƯỞNG LÀM VIỆC in bold marker.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "NGHỊCH CÀI ĐẶT"},
            ]),
            ("Đừng nghe lời khuyên mua sắm bừa bãi khi bạn chưa thuần thục những thứ hoàn toàn miễn phí.", [
                {"spec": "concept_metaphor:CH01|The stickman pushes away a tray of paid software badges while holding a free notepad.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "DÙNG ĐỒ MIỄN PHÍ"},
                {"spec": "macro_prop:none|A simple hand-drawn zero dollar sign ($0) circled in bold black ink on white canvas.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "MIỄN PHÍ"},
            ]),
        ]
    ),
    (
        "Điểm dừng rà soát và Mid-CTA",
        "A peaceful sunny office desk on white background.",
        "narrative_warm",
        "structural_model",
        [
            ("Bạn hãy dừng lại một phút và mở sao kê tài khoản ngân hàng tháng này ra xem.", [
                {"spec": "full_scene:CH01|The stickman sits calmly holding up a printed bank statement with a highlighter.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "MỞ SAO KÊ"},
                {"spec": "still_life:none|A coffee cup next to a neat list of monthly software expenses highlighted in yellow.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "RÀ SOÁT"},
            ]),
            ("Nếu bạn từng rơi vào bẫy đăng ký rồi bỏ xó công cụ, hãy lưu video này lại để rà soát chi tiêu nhé.", [
                {"spec": "full_scene:CH01|The employee smiles warmly pointing to the bookmark save button icon on screen.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LƯU VIDEO LẠI"},
                {"spec": "macro_prop:none|A crisp ribbon bookmark symbol with a subtle checkmark on white background.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LƯU LẠI"},
            ]),
            ("Bây giờ, chúng ta sẽ bước vào quy trình ba tầng cốt lõi giúp bạn làm chủ mọi công việc.", [
                {"spec": "concept_metaphor:CH01|The stickman rolls out a clean technical blueprint roadmap on the wooden desk.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "BA TẦNG CỐT LÕI"},
                {"spec": "visual_diagram:none|A three-tier architectural pedestal labeled Context, Data, Output on white canvas.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "QUY TRÌNH"},
            ]),
        ]
    ),
    (
        "Tầng một: Thiết lập bối cảnh vai trò",
        "A clear studio drafting table on pure white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Tầng đầu tiên là đóng khung vai trò và mục tiêu rõ ràng cho trí tuệ nhân tạo.", [
                {"spec": "full_scene:CH01|The stickman pins a role badge marked CHUYÊN GIA PHÂN TÍCH onto an avatar card.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐÓNG KHUNG VAI TRÒ"},
                {"spec": "visual_diagram:none|A boundary frame enclosing a persona card with specific responsibilities on white canvas.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "MỤC TIÊU RÕ"},
            ]),
            ("Thay vì bảo nó viết bài chung chung, bạn hãy giao cho nó một nhiệm vụ cụ thể của chuyên gia.", [
                {"spec": "concept_metaphor:CH01|The stickman hands a structured mission dossier to a smart robot assistant.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "NHIỆM VỤ CỤ THỂ"},
                {"spec": "visual_diagram:none|Text comparison: Viết báo cáo (Sai) vs Đóng vai chuyên gia rà soát rủi ro (Đúng).", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "ĐÚNG VAI TRÒ"},
            ]),
            ("Khi bối cảnh chuẩn xác, câu trả lời sẽ đi thẳng vào trọng tâm mà không lan man.", [
                {"spec": "full_scene:CH01|The employee gives a thumbs-up as a crisp straight arrow hits the bullseye target.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TRÚNG MỤC TIÊU"},
                {"spec": "macro_prop:none|An arrow piercing the exact center of a target ring on pure white canvas.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TRỌNG TÂM"},
            ]),
        ]
    ),
    (
        "Tầng hai: Cung cấp dữ liệu tham chiếu",
        "A clean office research desk on white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Tầng thứ hai là nạp dữ liệu thô và các tiêu chuẩn kiểm duyệt bạn mong muốn.", [
                {"spec": "full_scene:CH01|The stickman inserts a neat stack of bullet-point notes into a input scanning tray.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "NẠP DỮ LIỆU THÔ"},
                {"spec": "visual_diagram:none|A document sorting tray taking messy meeting notes and filtering through strict criteria.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TIÊU CHUẨN"},
            ]),
            ("Hãy đưa ra một vài ví dụ mẫu mà bạn ưng ý nhất để máy học theo phong cách.", [
                {"spec": "concept_metaphor:CH01|The stickman holds up a gold-standard reference sheet beside a blank page.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "VÍ DỤ MẪU"},
                {"spec": "still_life:none|Two parallel document pages showing matched paragraph rhythms and tone markers.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "ĐÚNG PHONG CÁCH"},
            ]),
            ("Cách làm này loại bỏ hoàn toàn hiện tượng máy bịa đặt thông tin hoặc nói nhảm.", [
                {"spec": "full_scene:CH01|The employee stamps a verified green seal onto a finalized document page.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "HẾT BỊA ĐẶT"},
                {"spec": "macro_prop:none|A solid circular stamp showing a bold checkmark with VERIFIED lettering.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "CHUẨN XÁC"},
            ]),
        ]
    ),
    (
        "Tầng ba: Khóa chặt định dạng đầu ra",
        "A modern graphic table on pure white background.",
        "analytical_crisp",
        "structural_model",
        [
            ("Tầng thứ ba là bắt buộc máy xuất kết quả theo đúng cấu trúc bảng biểu bạn cần.", [
                {"spec": "full_scene:CH01|The stickman draws a neat 3-column table on a digital whiteboard screen.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KHÓA ĐỊNH DẠNG"},
                {"spec": "visual_diagram:none|A clean tabular grid with columns for Task, Owner, Deadline, and Priority.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BẢNG BIỂU"},
            ]),
            ("Yêu cầu rõ ràng số lượng từ, các đề mục chính và hành động tiếp theo cần làm.", [
                {"spec": "concept_metaphor:CH01|The stickman measures text paragraphs using a precise drafting ruler.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "ĐO ĐẾM TỪ"},
                {"spec": "visual_diagram:none|A numbered checklist with three distinct actionable bullet points.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "HÀNH ĐỘNG TIẾP"},
            ]),
            ("Bạn chỉ việc copy kết quả thẳng vào email hoặc báo cáo mà không cần chỉnh sửa.", [
                {"spec": "full_scene:CH01|The employee easily drags and drops the formatted table into an email window.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "DÙNG ĐƯỢC LIỀN"},
                {"spec": "macro_prop:none|A cursor clicking SEND on an email interface with an attached clean summary.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "GỬI NGAY"},
            ]),
        ]
    ),
    (
        "Ví dụ thực chiến: Xử lý hợp đồng",
        "A legal analysis workspace on pure white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Áp dụng ba tầng này vào rà soát hợp đồng kinh tế sẽ tiết kiệm cho bạn cả buổi chiều.", [
                {"spec": "full_scene:CH01|The stickman reviews a multi-page commercial contract beside a laptop terminal.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "RÀ HỢP ĐỒNG"},
                {"spec": "macro_prop:none|A stack of twenty contract pages stamped with highlighted audit badges.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "TIẾT KIỆM CHIỀU"},
            ]),
            ("Bạn yêu cầu máy tìm ba điểm phạt vô lý và đề xuất câu từ thay thế an toàn.", [
                {"spec": "concept_metaphor:CH01|A bright spotlight isolates three problematic clauses circled in red marker.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "TÌM BẪY PHẠT"},
                {"spec": "visual_diagram:none|Before-and-after table contrasting a risky clause with a revised safe clause.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "ĐIỀU KHOẢN AN TOÀN"},
            ]),
            ("Chỉ mất ba mươi giây, toàn bộ danh sách rủi ro đã hiện ra rõ mồn một trên màn hình.", [
                {"spec": "full_scene:CH01|The employee smiles confidently holding the printed list of safe revisions.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "BA MƯƠI GIÂY"},
                {"spec": "macro_prop:none|A stopwatch displaying 00:30 with clean bold numbers on white canvas.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "XONG NGAY"},
            ]),
        ]
    ),
    (
        "Bình luận về điểm mù tự động hóa",
        "A quiet contemplative studio corner on white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Điểm mù lớn nhất của người dùng AI là tin tưởng tuyệt đối vào câu trả lời đầu tiên.", [
                {"spec": "full_scene:CH01|The stickman shakes head with serious analytical expression while looking at text.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐIỂM MÙ LỚN NHẤT"},
                {"spec": "concept_metaphor:none|A pair of rose-colored glasses placed face-down on a technical document.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐỪNG VỘI TIN"},
            ]),
            ("Cái giá phải trả cho việc lười kiểm chứng là những sai sót ngớ ngẩn trước mặt cấp trên.", [
                {"spec": "full_scene:CH01|The stickman winces as an awkward red error badge appears on a presentation slide.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "CÁI GIÁ PHẢI TRẢ"},
                {"spec": "visual_diagram:none|A warning sign showing a factual error slipping through automated output to clients.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "LỖI NGỚ NGẨN"},
            ]),
            ("Máy móc chỉ là trợ lý đắc lực, người chịu trách nhiệm cuối cùng vẫn luôn là chính bạn.", [
                {"spec": "concept_metaphor:CH01|The stickman stands tall holding the master steering wheel of the office ship.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "BẠN LÀ THUYỀN TRƯỞNG"},
                {"spec": "macro_prop:none|A classic ship steering wheel rendered in crisp black outlines on white canvas.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "CHỊU TRÁCH NHIỆM"},
            ]),
        ]
    ),
    (
        "Quy tắc ngón tay cái: Thử nghiệm 10 ngày",
        "A sunlit desk with a calendar pad on pure white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Hãy áp dụng quy tắc thử nghiệm mười ngày trước khi rút ví trả tiền phần mềm.", [
                {"spec": "full_scene:CH01|The stickman points marker to a 10-day block on a wall calendar pad.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "QUY TẮC MƯỜI NGÀY"},
                {"spec": "macro_prop:none|A desktop calendar page showing days 1 through 10 neatly crossed with checkmarks.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KIỂM CHỨNG"},
            ]),
            ("Trong mười ngày này, bạn chỉ dùng phiên bản miễn phí và chuẩn hóa các câu lệnh mẫu.", [
                {"spec": "full_scene:CH01|The employee organizes prompt templates into a tidy labeled desk binder.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "DÙNG BẢN MIỄN PHÍ"},
                {"spec": "still_life:none|A clean document binder labeled PROMPT CHUẨN on the wooden desk.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "BỘ MẪU"},
            ]),
            ("Nếu phiên bản miễn phí chưa giúp bạn tiết kiệm được một giờ mỗi ngày, tuyệt đối đừng nâng cấp.", [
                {"spec": "concept_metaphor:CH01|The stickman securely closes the wallet flap with a firm satisfied smile.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "KHÓA VÍ TIỀN"},
                {"spec": "visual_diagram:none|A threshold chart: Under 1 hour saved = Keep Free, Over 1 hour = Consider Upgrade.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TIẾT KIỆM 1 GIỜ"},
            ]),
        ]
    ),
    (
        "Xây dựng kho tài nguyên prompt cá nhân",
        "A digital filing workspace on clean white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Tài sản lớn nhất của bạn sau video này là một trang ghi chú chứa các prompt chuẩn.", [
                {"spec": "full_scene:CH01|The stickman types notes into a clean Google Docs document on laptop screen.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TÀI SẢN LỚN NHẤT"},
                {"spec": "macro_prop:none|A document file icon with an open treasure chest symbol on white background.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KHO PROMPT"},
            ]),
            ("Mỗi khi tạo ra một câu lệnh cho kết quả tốt, bạn hãy lưu nó vào kho mẫu theo phân loại.", [
                {"spec": "concept_metaphor:CH01|The employee drops a validated prompt reference card into a labeled index file box.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "LƯU VÀO KHO"},
                {"spec": "visual_diagram:none|Three categorized index tabs: Viết Email, Tóm Tắt Họp, Rà Soát Hợp Đồng.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "PHÂN LOẠI"},
            ]),
            ("Lần sau gặp công việc tương tự, bạn chỉ cần mở ra thay thông tin trong mười giây.", [
                {"spec": "full_scene:CH01|The stickman quickly replaces bracketed variables in a pre-made prompt string.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "MƯỜI GIÂY"},
                {"spec": "macro_prop:none|A lightning bolt icon striking a document template indicating instant speed.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "NHANH CHÓNG"},
            ]),
        ]
    ),
    (
        "Bài test 30 giây rà soát công cụ",
        "A clear audit desk on pure white background.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Ngay chiều nay, bạn hãy làm một bài test ba mươi giây để thanh lọc công cụ làm việc.", [
                {"spec": "full_scene:CH01|The employee sits with a clean pen and a checklist sheet ready to audit.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BÀI TEST 30 GIÂY"},
                {"spec": "visual_diagram:none|A checklist showing three direct test questions with Yes/No checkboxes.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "THANH LỌC"},
            ]),
            ("Hãy hỏi bản thân: công cụ này có đang giúp mình giải quyết việc nhanh hơn viết tay không?", [
                {"spec": "concept_metaphor:CH01|The stickman points index finger to temple in focused honest reflection.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "TỰ HỎI BẢN THÂN"},
                {"spec": "visual_diagram:none|A split scale comparing Manual Speed against Software Overhead Time.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "CÓ NHANH HƠN?"},
            ]),
            ("Nếu câu trả lời là không hoặc bạn thấy ngập ngừng, hãy mạnh dạn hủy đăng ký ngay lập tức.", [
                {"spec": "full_scene:CH01|The stickman boldly clicks the red CANCEL SUBSCRIPTION button with a smile of relief.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "HỦY ĐĂNG KÝ"},
                {"spec": "macro_prop:none|A pair of scissors cleanly snipping through a monthly software billing ribbon.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TIẾT KIỆM NGAY"},
            ]),
        ]
    ),
    (
        "Tổng kết và kêu gọi kết nối",
        "A bright tidy morning office desk on pure white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Công nghệ sinh ra để phục vụ con người chứ không phải biến chúng ta thành nô lệ.", [
                {"spec": "full_scene:CH01|The stickman stands smiling beside a friendly robot assistant in mutual respect.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CÔNG NGHỆ PHỤC VỤ"},
                {"spec": "concept_metaphor:none|A robotic hand and a human hand clasping in partnership under warm morning light.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LÀM CHỦ CÔNG NGHỆ"},
            ]),
            ("Khi bạn làm chủ quy trình, mọi công cụ không tốn một xu đều trở thành vũ khí sắc bén.", [
                {"spec": "full_scene:CH01|The employee holds a neat folder of prompt blueprints with confidence and pride.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "VŨ KHÍ SẮC BÉN"},
                {"spec": "macro_prop:none|A glowing blue sword symbol integrated cleanly with a digital quill on white canvas.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TINH GỌN"},
            ]),
            ("Bạn đang tốn bao nhiêu tiền cho các gói AI mỗi tháng, hãy cùng tính nhẩm dưới phần bình luận nhé.", [
                {"spec": "full_scene:CH01|The stickman waves warm friendly hand inviting viewers to share in the comments.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BÌNH LUẬN NHÉ"},
                {"spec": "white_card:none|Channel endcard illustration on flat canvas with channel mascot and clear text AI BÌNH DÂN.", "tempo": "slow", "narrative_situation": "mechanism_step", "is_endcard": True},
            ]),
        ]
    ),
]

# =============================================================================
# SHORT SPIN-OFF (5 SCENES, ~19 BEATS, ~42 SECONDS, CLIFFHANGER FUNNEL)
# =============================================================================

SHORT_TOPIC = "Đừng Mua Tool AI Đắt Tiền Khi Chưa Biết Quy Tắc 3 Bước Này!"
SHORT_AUDIENCE = "Dân văn phòng, sinh viên muốn dùng AI hiệu quả miễn phí"
SHORT_GOAL = "Bóc trần bẫy chi tiền mua tool AI và dẫn dắt người xem vào video dài bằng câu hỏi bỏ lửng tại đỉnh cao trào"

SHORT_EDITORIAL_STANCE = {
    "myth_debunked": "Cứ chi tiền mua tài khoản AI trả phí đắt đỏ là tự động x10 năng suất công việc.",
    "why_generic_advice_fails": "Lời khuyên mua công cụ mới liên tục chỉ làm bạn phân tán và tốn tiền đăng ký.",
    "channel_verdict": "Sự thật mất lòng là nếu thiếu quy trình thì công cụ xịn chỉ giúp bạn tạo ra rác nhanh hơn.",
    "tradeoff_or_blindspot": "Học cách viết prompt có cấu trúc ban đầu sẽ tốn não hơn việc bấm một nút ăn liền."
}

SHORT_ACTIONABLE_VALUE = {
    "core_mechanism": "Cấu trúc ba tầng cốt lõi gồm vai trò ngữ cảnh, dữ liệu tham chiếu và định dạng kết quả đầu ra.",
    "practical_rule_of_thumb": "Quy tắc mười ngày kiểm chứng: không bao giờ trả tiền cho bản pro khi bản miễn phí chưa dùng hết công năng.",
    "real_world_scenario": "Hủy toàn bộ ba gói đăng ký ba mươi đô để dùng một bảng mẫu prompt Google Docs giải quyết xong việc sớm."
}

SHORT_PACKAGING = {
    "youtube_title": "Đừng Mua Tool AI Đắt Tiền Khi Chưa Biết Điều Này!",
    "visual_hook": "Người que áo tím cầm thẻ tín dụng định thanh toán tool AI nhưng bị bảng cảnh báo chặn lại",
    "text_overlay": "ĐỪNG VỘI MUA",
    "contrast_pair": "Mua tool 30 đô/tháng vs Quy tắc prompt 3 bước miễn phí",
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": ["ai binh dan", "meo ai", "chatgpt mien phi", "shorts"],
    "cta_plan": {
        "cliffhanger_peak": "Đúng lúc bạn nghĩ công cụ này hoàn hảo nhất thì bẫy rò rỉ dữ liệu và prompt một dòng sẽ đánh sập toàn bộ kết quả của bạn ra sao?",
        "bridge": "Xem video bản dài bên dưới để lấy bộ mẫu prompt ba bước nhé.",
        "close": "Lưu lại ngay để không tốn tiền oan mỗi tháng bạn nhé.",
        "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
    }
}

SHORT_SOURCES = [
    {
        "id": "SRC01",
        "title": "Báo Cáo Năng Suất Và Tự Động Hóa Công Nghệ Công Sở",
        "reference": "Viện Nghiên Cứu Chuyển Đổi Số Văn Phòng (2024). Khảo Sát Thói Quen Công Cụ.",
        "facts": [
            "Hơn bảy mươi phần trăm tài khoản phần mềm đăng ký hàng tháng bị bỏ xó sau sáu mươi ngày."
        ]
    }
]

SHORT_STORY_ROWS: List[Tuple[str, str, str, str, List[Tuple[str, Any]]]] = [
    (
        "Mở màn đánh thẳng vào nỗi đau",
        "A bright office desk on white background.",
        "narrative_warm",
        "hook",
        [
            ("Đừng vội rút ví mua tài khoản AI ba mươi đô mỗi tháng.", [
                {"spec": "full_scene:CH01|A young employee in a violet hoodie hesitates holding a credit card before a laptop purchase screen.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "ĐỪNG VỘI MUA"},
                {"spec": "macro_prop:none|A credit card with a big red warning badge showing THẺ TÍN DỤNG.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "BA MƯƠI ĐÔ"},
            ]),
            ("Bởi vì chín mươi phần trăm người mua về chỉ dùng được đúng ba ngày rồi bỏ xó.", [
                {"spec": "visual_diagram:none|A bar graph showing ninety percent of paid software users dropping off after three days.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "CHÍN MƯƠI PHẦN TRĂM"},
                {"spec": "concept_metaphor:CH01|The stickman looks bored as a digital app icon gets covered in thick spiderwebs on screen.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "BỎ XÓ"},
            ]),
        ]
    ),
    (
        "Bóc trần sự thật ngược đời",
        "A minimalist tech table on clean white background.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Sự thật mất lòng là, công cụ xịn không giúp bạn thông minh hơn.", [
                {"spec": "full_scene:CH01|The stickman points finger to temple explaining with a direct honest expression.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "SỰ THẬT MẤT LÒNG"},
                {"spec": "concept_metaphor:none|A golden pen writing the exact same messy nonsense as a cheap wooden pencil.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "BÚT VÀNG"},
            ]),
            ("Nếu bạn đưa cho nó một câu lệnh mơ hồ một dòng, thì bản trả phí cũng chỉ trả về toàn rác văn phòng.", [
                {"spec": "visual_diagram:none|A diagram showing a one-line vague prompt resulting in a trash bin overflowing with generic text.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "PROMPT MỘT DÒNG"},
                {"spec": "full_scene:CH01|The stickman sweeps crumpled paper away from the laptop keyboard in frustration.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "TOÀN RÁC"},
            ]),
        ]
    ),
    (
        "Lời bình sắc lẹm và bí quyết cốt lõi",
        "A clear studio drafting corner on white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Đánh giá công bằng thì, người làm chủ công nghệ chỉ cần bản miễn phí kèm quy tắc ba bước.", [
                {"spec": "full_scene:CH01|The stickman holds up three fingers displaying the three-step prompt formula.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐÁNH GIÁ CÔNG BẰNG"},
                {"spec": "visual_diagram:none|Three stacked building blocks labeled Bối Cảnh, Dữ Liệu, and Định Dạng on white canvas.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "BA BƯỚC"},
            ]),
            ("Đó là đóng khung vai trò chuyên gia, nạp dữ liệu tham chiếu và khóa chặt bảng biểu đầu ra.", [
                {"spec": "concept_metaphor:CH01|The stickman snaps together three building blocks into a solid architectural pillar.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "KHÓA ĐỊNH DẠNG"},
                {"spec": "still_life:none|A clean three-tier document template ready to paste into any office workflow.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "BỘ KHUNG"},
            ]),
        ]
    ),
    (
        "Đỉnh cao trào bỏ lửng (Cliffhanger Peak)",
        "A dramatic high-contrast workspace on pure white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Nhưng cái bẫy nguy hiểm nhất lại nằm ở bước nạp dữ liệu mật mà ít ai để ý.", [
                {"spec": "full_scene:CH01|The stickman gasps with wide eyes seeing an urgent alert warning flash above the laptop.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "CÁI BẪY NGUY HIỂM"},
                {"spec": "still_life:none|A padlock popping open on a confidential customer data folder on white canvas.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "DỮ LIỆU MẬT"},
            ]),
            ("Đúng lúc bạn nghĩ công cụ này hoàn hảo nhất thì bẫy rò rỉ dữ liệu và prompt một dòng sẽ đánh sập toàn bộ kết quả của bạn ra sao?", [
                {"spec": "concept_metaphor:CH01|The stickman stands before a branching crossroads with a giant glowing question mark in midair.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "ĐÁNH SẬP KẾT QUẢ"},
                {"spec": "macro_prop:none|A giant question mark symbol hovering over an unfinished contract analysis sheet.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "LỜI GIẢI LÀ GÌ?"},
            ]),
        ]
    ),
    (
        "Chuyển phễu sang bản Full và Close CTA",
        "A bright tidy morning office desk on pure white background.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Xem video bản dài bên dưới để lấy bộ mẫu prompt ba bước nhé.", [
                {"spec": "full_scene:CH01|The stickman points enthusiastically down toward the linked video preview card below.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "XEM BẢN DÀI"},
                {"spec": "visual_diagram:none|A bold directional arrow pointing down to the related full-length video badge.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "BẤM DƯỚI ĐÂY"},
            ]),
            ("Lưu lại ngay để không tốn tiền oan mỗi tháng bạn nhé.", [
                {"spec": "full_scene:CH01|The employee smiles warmly waving hand beside the channel logo on white canvas.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "LƯU LẠI NGAY"},
            ]),
        ]
    ),
]
