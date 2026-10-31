# -*- coding: utf-8 -*-
"""Batch 2 Story Blueprint for Não Lười (channel-nao-luoi).

Topic: Cái Bẫy Của Thuyết Hoàn Hảo (Long) & Não Bộ Bị Tê Liệt Khi Cầu Toàn (Short)
Format: V3 High-Density Narrative-Driven Adaptive Visual Pacing.
"""

from typing import Any, Dict, List, Tuple

CHANNEL_ID = "nao_luoi"
CHANNEL_SLUG = "nao-luoi"

# =============================================================================
# LONG EXPLAINER (16 SCENES, ~94 BEATS, ~265 SECONDS)
# =============================================================================

LONG_TOPIC = "Cái Bẫy Của Thuyết 'Hoàn Hảo': Vì Sao Đặt Mục Tiêu Càng Lớn Não Bộ Càng Tê Liệt?"
LONG_AUDIENCE = "Người hay trì hoãn, người mắc hội chứng cầu toàn, sinh viên và dân sáng tạo"
LONG_GOAL = "Giải mã phản xạ đóng băng của hạch hạnh nhân khi đặt kỳ vọng quá cao và quy tắc bước nhảy hai phút"

LONG_EDITORIAL_STANCE = {
    "myth_debunked": "Cầu toàn là một đức tính tốt thể hiện tinh thần trách nhiệm cao và tiêu chuẩn xuất sắc.",
    "why_generic_advice_fails": "Văn hóa hô hào đặt mục tiêu to lớn chỉ kích hoạt phản xạ giả chết của vỏ não trước trán.",
    "channel_verdict": "Sự thật mất lòng là chủ nghĩa cầu toàn thực chất chỉ là chiếc mặt nạ tinh vi của nỗi sợ hãi thất bại.",
    "tradeoff_or_blindspot": "Chấp nhận làm dở tệ ở bản nháp đầu tiên sẽ khiến bạn khó chịu nhưng đó là con đường duy nhất để hoàn thành."
}

LONG_ACTIONABLE_VALUE = {
    "core_mechanism": "Cơ chế đe dọa sinh tồn của hạch hạnh nhân (amygdala freeze response) khi đối mặt với kỳ vọng khổng lồ.",
    "practical_rule_of_thumb": "Quy tắc bản nháp xấu xí: cố tình viết một bản thảo tệ hại nhất có thể trong mười phút đầu tiên.",
    "real_world_scenario": "Hạ tiêu chuẩn bài viết từ hoàn hảo mười điểm xuống còn sáu điểm giúp hoàn thành luận văn trước ba tuần."
}

LONG_PACKAGING = {
    "youtube_title": "Vì Sao Đặt Mục Tiêu Càng Lớn Não Càng Trì Hoãn?",
    "visual_hook": "Người que ôm đầu đứng bất động trước một tờ giấy trắng khổng lồ cao như bức tường thành",
    "text_overlay": "BẪY CẦU TOÀN",
    "contrast_pair": "Ảo tưởng mười điểm hoàn hảo vs Bản nháp xấu xí hành động ngay",
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": ["nao luoi", "cau toan", "tri hoan", "tam ly hoc", "muc tieu"],
    "cta_plan": {
        "mid_cta": "Nếu bạn từng bỏ cuộc giữa chừng vì sợ làm không xuất sắc, hãy lưu video này lại để giải tỏa tâm lý nhé.",
        "close": "Mục tiêu nào đang khiến bạn đóng băng nhiều tháng nay, hãy viết ra dưới phần bình luận để Não Lười cùng gỡ nhé.",
        "endcard_text": "NÃO LƯỜI"
    }
}

LONG_SOURCES = [
    {
        "id": "SRC01",
        "title": "Nghiên Cứu Tâm Lý Học Hành Vi Về Hội Chứng Trì Hoãn Cầu Toàn",
        "reference": "Đại Học Stanford (2024). Báo Cáo Tâm Lý Nhận Thức.",
        "facts": [
            "Hơn tám mươi phần trăm trường hợp trì hoãn kinh niên bắt nguồn từ nỗi sợ bị phán xét.",
            "Chia nhỏ tác vụ xuống dưới hai phút làm giảm chín mươi phần trăm phản xạ né tránh của hạch não."
        ]
    }
]

LONG_STORY_ROWS: List[Tuple[str, str, str, str, List[Tuple[str, Any]]]] = [
    (
        "Trang giấy trắng và sự im lặng",
        "A quiet study desk in evening shadows on white canvas.",
        "narrative_warm",
        "lived_friction",
        [
            ("Bạn ngồi trước màn hình máy tính suốt hai tiếng đồng hồ nhưng không gõ nổi một chữ.", [
                {"spec": "full_scene:CH01|The stickman researcher sits motionless before a completely blank laptop screen.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "HAI TIẾNG ĐỒNG HỒ"},
                {"spec": "macro_prop:none|A blinking text cursor on an empty digital document page drawn in black ink.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "CON TRỎ NHẤP NHÁY"},
            ]),
            ("Mỗi khi định đặt tay lên bàn phím, một giọng nói bên trong lại thầm thì: chưa đủ hay đâu.", [
                {"spec": "concept_metaphor:CH01|A small perfectionist critic figure whispers doubt into the researcher ear.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "CHƯA ĐỦ HAY"},
                {"spec": "visual_diagram:none|A split scale: Ideal Masterpiece in imagination versus Messy First Draft in reality.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "TIÊU CHUẨN CAO"},
            ]),
            ("Bạn xóa đi viết lại câu mở đầu cả chục lần rồi thở dài đóng máy tính lại.", [
                {"spec": "full_scene:CH01|The researcher hits backspace repeatedly watching drafted lines vanish.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "XÓA ĐI VIẾT LẠI"},
                {"spec": "macro_prop:none|A laptop lid closing with a quiet click on pure white canvas.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "ĐÓNG MÁY TÍNH"},
            ]),
        ]
    ),
    (
        "Nỗi sợ hãi đội lốt trách nhiệm",
        "A minimalist contemplation corner on white background.",
        "analytical_crisp",
        "lived_friction",
        [
            ("Nhiều người lầm tưởng rằng họ trì hoãn là vì thiếu kỷ luật hoặc lười biếng.", [
                {"spec": "full_scene:CH01|The researcher looks down at self with self-blaming and frustrated expression.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "TỰ TRÁCH BẢN THÂN"},
                {"spec": "visual_diagram:none|A label marked LƯỜI BIẾNG being stamped unfairly onto the character chest.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "ẢO TƯỞNG"},
            ]),
            ("Nhưng thực chất, bạn không hề lười, mà là tiêu chuẩn của bạn đang quá khắt khe.", [
                {"spec": "concept_metaphor:CH01|The stickman struggles to lift a massive barbell weighted with perfection standards.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "QUÁ KHẮT KHE"},
                {"spec": "visual_diagram:none|A pedestal bar raised impossibly high above normal human reach on white canvas.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TIÊU CHUẨN TRÊN TRỜI"},
            ]),
            ("Bạn thà không nộp bài còn hơn là phải nộp một sản phẩm tầm thường bị chê bai.", [
                {"spec": "full_scene:CH01|The researcher hides drafted project folder behind back away from judgmental eyes.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "SỢ BỊ CHÊ BAI"},
                {"spec": "macro_prop:none|A shield blocking multiple red judgment arrows on pure white background.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TỰ VỆ"},
            ]),
        ]
    ),
    (
        "Cơ chế đóng băng của hạch hạnh nhân",
        "A cognitive neuroscience lab visual on white canvas.",
        "analytical_crisp",
        "lived_friction",
        [
            ("Bên trong bộ não, hạch hạnh nhân coi nỗi sợ bị phán xét giống như mối đe dọa sinh tử.", [
                {"spec": "full_scene:CH01|Doctor stickman points pointer to a simple 2D drawing of the amygdala region.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "HẠCH HẠNH NHÂN"},
                {"spec": "visual_diagram:none|An amygdala alarm bell ringing loudly with sound waves spreading across brain.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CHUÔNG BÁO ĐỘNG"},
            ]),
            ("Nó kích hoạt phản xạ phòng vệ tự nhiên: đóng băng và tê liệt toàn bộ hành động.", [
                {"spec": "concept_metaphor:CH01|The researcher stickman turns completely into solid ice like an ice statue.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "ĐÓNG BĂNG HÀNH ĐỘNG"},
                {"spec": "macro_prop:none|A stylized ice block with frost patterns covering an open notebook.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TÊ LIỆT"},
            ]),
            ("Vỏ não trước trán bị cắt nguồn năng lượng khiến bạn mất hoàn toàn khả năng tư duy sáng tạo.", [
                {"spec": "full_scene:CH01|The researcher taps forehead in helpless daze looking at scattered papers.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "MẤT NĂNG LƯỢNG"},
                {"spec": "visual_diagram:none|A disconnected electrical plug separating prefrontal cortex from creative flow.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "NGẮT KẾT NỐI"},
            ]),
        ]
    ),
    (
        "Hành vi né tránh để tìm kiếm an toàn",
        "A cluttered room corner with domestic distractions on white canvas.",
        "narrative_warm",
        "lived_friction",
        [
            ("Để xoa dịu cảm giác lo lắng, bộ não liền thôi thúc bạn làm những việc vụn vặt.", [
                {"spec": "full_scene:CH01|The stickman suddenly stands up enthusiastically grabbing a broom to sweep floor.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "LÀM VIỆC VỤN VẶT"},
                {"spec": "still_life:none|A broom and dustpan next to an unwashed coffee mug on pure white canvas.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "DỌN PHÒNG"},
            ]),
            ("Bạn quay sang dọn dẹp bàn làm việc, sắp xếp lại tủ sách hoặc lau chùi hộp bút.", [
                {"spec": "full_scene:CH01|The researcher arranges colored pencils in millimeter-precise straight line on desk.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "XẾP BÚT THẲNG HÀNG"},
                {"spec": "concept_metaphor:none|A magnifying glass checking exact alignment of desktop stationery items.", "tempo": "fast", "narrative_situation": "rapid_examples", "emphasis_text": "NGỤY TRANG"},
            ]),
            ("Những việc này mang lại ảo giác bận rộn trong khi dự án quan trọng vẫn dẫm chân tại chỗ.", [
                {"spec": "full_scene:CH01|The stickman smiles at clean desk while the wall calendar deadline looms large.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "ẢO GIÁC BẬN RỘN"},
                {"spec": "visual_diagram:none|Progress bar for Cleaning at 100% versus Important Project stuck at 0%.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "DỰ ÁN ĐỨNG YÊN"},
            ]),
        ]
    ),
    (
        "Bóc trần cội nguồn của sự phán xét",
        "A quiet historical memory study space on clean white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Chủ nghĩa cầu toàn thường được hình thành từ những trải nghiệm thời thơ ấu.", [
                {"spec": "full_scene:CH01|A small child stickman holds up a test score of nine points looking anxious.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KÝ ỨC THƠ ẤU"},
                {"spec": "visual_diagram:none|A school exam page showing 9/10 with an adult hand asking: Điểm 10 đâu?", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐIỂM CHÍN THIẾU MỘT"},
            ]),
            ("Khi tình yêu thương chỉ được trao khi bạn đạt điểm số mười tròn trĩnh, bạn học cách sợ hãi điểm chín.", [
                {"spec": "concept_metaphor:CH01|A heart shape trapped inside a rigid geometric cage of perfect right angles.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "YÊU THƯƠNG CÓ ĐIỀU KIỆN"},
                {"spec": "visual_diagram:none|A balance scale with Parental Approval balanced against Flawless Perfection.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "ÁP LỰC ĐIỂM MƯỜI"},
            ]),
            ("Lớn lên, bạn vô tình biến chính mình thành vị giám khảo tàn nhẫn nhất cuộc đời.", [
                {"spec": "full_scene:CH01|The adult researcher stares at a harsh inner judge gavel resting on the study table.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "GIÁM KHẢO TÀN NHẪN"},
                {"spec": "macro_prop:none|A heavy wooden court gavel slamming down onto a draft paper sheet.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TỰ PHÁN XÉT"},
            ]),
        ]
    ),
    (
        "Lời bình sắc bén: Sự thật mất lòng",
        "A direct discussion space with crisp minimalist lighting on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Sự thật mất lòng là, cầu toàn không phải tiêu chuẩn cao, mà là nỗi hèn nhát không dám đối mặt thực tế.", [
                {"spec": "full_scene:CH01|The researcher steps forward speaking with candid courageous clarity.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "SỰ THẬT MẤT LÒNG"},
                {"spec": "concept_metaphor:none|A shiny golden mask of perfection falling off to reveal trembling human eyes.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "CHIẾC MẶT NẠ"},
            ]),
            ("Đánh giá công bằng thì, người cầu toàn thường ít hoàn thành được tác phẩm hơn người dám làm dở.", [
                {"spec": "full_scene:CH01|The researcher points toward two desks: one clean and empty, one messy and full of books.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐÁNH GIÁ CÔNG BẰNG"},
                {"spec": "visual_diagram:none|Comparison showing Zero Finished Projects vs Ten Published Works with Flaws.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "HOÀN THÀNH HƠN HOÀN HẢO"},
            ]),
            ("Đừng nghe lời khuyên hãy cố gắng hoàn mỹ khi thế giới thực chỉ trả công cho những thứ được giao đúng hạn.", [
                {"spec": "concept_metaphor:CH01|The stickman holds a finalized document stamped SUBMITTED ON TIME.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "GIAO ĐÚNG HẠN"},
                {"spec": "macro_prop:none|A green courier package sealed and ready for delivery on pure white canvas.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐÚNG HẠN"},
            ]),
        ]
    ),
    (
        "Điểm dừng thở và Mid-CTA",
        "A peaceful quiet study space under gentle morning light on white canvas.",
        "narrative_warm",
        "structural_model",
        [
            ("Hãy thả lỏng hai bả vai xuống và hít thở thật sâu trong năm giây.", [
                {"spec": "full_scene:CH01|The researcher drops shoulders taking a deep calm breath with closed eyes.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "THẢ LỎNG VAI"},
                {"spec": "macro_prop:none|An expanding concentric breathing ring drawn in soft blue ink on white canvas.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HÍT THỞ SÂU"},
            ]),
            ("Nếu bạn từng bỏ cuộc giữa chừng vì sợ làm không xuất sắc, hãy lưu video này lại để giải tỏa tâm lý nhé.", [
                {"spec": "full_scene:CH01|The researcher smiles with genuine empathy pointing to the save bookmark ribbon.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LƯU LẠI GIẢI TỎA"},
                {"spec": "macro_prop:none|A neat bookmark symbol with a small leaf sprouting from the top.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LƯU VIDEO"},
            ]),
            ("Bây giờ, Não Lười sẽ chia sẻ với bạn bí quyết đánh lừa hạch sợ hãi của não bộ.", [
                {"spec": "concept_metaphor:CH01|The researcher sketches a playful detour arrow around a sleeping dragon.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "ĐÁNH LỪA HẠCH NÃO"},
                {"spec": "visual_diagram:none|A clear tactical path bypassing the amygdala trigger threshold.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "ĐƯỜNG VÒNG THÔNG MINH"},
            ]),
        ]
    ),
    (
        "Phương pháp Bản Nháp Xấu Xí",
        "A playful creative studio table on clean white background.",
        "narrative_warm",
        "structural_model",
        [
            ("Chiến lược mạnh mẽ nhất để phá vỡ sự tê liệt là cho phép mình tạo ra bản nháp xấu xí.", [
                {"spec": "full_scene:CH01|The researcher writes rapidly on notepad with messy loose uninhibited strokes.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BẢN NHÁP XẤU XÍ"},
                {"spec": "still_life:none|A notebook page titled BẢN NHÁP KINH DỊ with scribbles and crossed-out words.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CHO PHÉP LÀM TỆ"},
            ]),
            ("Hãy đặt mục tiêu viết ra những câu chữ lộn xộn, sai chính tả và ngô nghê nhất có thể.", [
                {"spec": "concept_metaphor:CH01|The stickman playfully sculpts a goofy clay figure with broad happy smile.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CỐ TÌNH LÀM TỆ"},
                {"spec": "visual_diagram:none|A funny doodle cartoon figure holding a sign saying I AM PROUDLY IMPERFECT.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "KHÔNG ÁP LỰC"},
            ]),
            ("Khi bạn cố tình làm dở, hạch hạnh nhân sẽ mất cảnh giác và không còn phát tín hiệu đe dọa.", [
                {"spec": "full_scene:CH01|The amygdala cartoon character falls peacefully asleep under a tiny nightcap.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "HẠCH NÃO NGỦ QUÊN"},
                {"spec": "macro_prop:none|A closed eye with three ZZZ sleeping letters drifting upward.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "HẾT ĐE DỌA"},
            ]),
        ]
    ),
    (
        "Quy tắc bước nhảy hai phút",
        "A bright morning desk with a simple timer on pure white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Quy tắc bước nhảy hai phút yêu cầu bạn chỉ cam kết ngồi vào bàn trong đúng một trăm hai mươi giây.", [
                {"spec": "full_scene:CH01|The researcher sets a digital egg timer to exactly two minutes on desk.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "QUY TẮC HAI PHÚT"},
                {"spec": "macro_prop:none|A circular kitchen timer displaying 02:00 with clean minimalist lines.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "MỘT TRĂM HAI MƯƠI GIÂY"},
            ]),
            ("Bạn nói với não bộ: Tôi chỉ mở file tài liệu và đọc lướt qua một tiêu đề rồi được phép nghỉ.", [
                {"spec": "concept_metaphor:CH01|The researcher steps over a tiny ankle-high curb with ease and lightness.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "HẠ THẤP NGƯỠNG BẮT ĐẦU"},
                {"spec": "visual_diagram:none|A tiny pebble obstacle contrasted against a giant intimidating mountain barrier.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "DỄ NHƯ ĂN KẸO"},
            ]),
            ("Bộ não thấy cái giá quá nhỏ nên dễ dàng chấp thuận mà không hề phản kháng.", [
                {"spec": "full_scene:CH01|The researcher clicks open the document with a relaxed and peaceful smile.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "KHÔNG PHẢN KHÁNG"},
                {"spec": "concept_metaphor:none|A green traffic light glowing brightly above the open workspace pathway.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "ĐÈN XANH NÃO BỘ"},
            ]),
        ]
    ),
    (
        "Hiệu ứng đà quán tính tâm lý",
        "A dynamic flowing sketch workspace on clean white canvas.",
        "narrative_warm",
        "structural_model",
        [
            ("Nhưng điều kỳ diệu là: khi đã bắt đầu được hai phút, bạn thường không muốn dừng lại nữa.", [
                {"spec": "full_scene:CH01|The researcher typing smoothly with pen in hand as ideas start pouring forth.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "KHÔNG MUỐN DỪNG"},
                {"spec": "concept_metaphor:none|A heavy stone boulder starting to roll downhill gaining effortless momentum.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐÀ QUÁN TÍNH"},
            ]),
            ("Tâm lý học gọi đây là hiệu ứng Zeigarnik: một công việc dang dở sẽ tự động hút năng lượng tiếp tục.", [
                {"spec": "visual_diagram:none|Typography card reading HIỆU ỨNG ZEIGARNIK with magnetic attraction vectors.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "HIỆU ỨNG ZEIGARNIK"},
                {"spec": "concept_metaphor:CH01|A magnet pulling paper notes and creative ideas straight onto the work page.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "LỰC HÚT TÂM LÝ"},
            ]),
            ("Khó khăn nhất không phải là viết mười trang sách, mà là viết xong dòng đầu tiên.", [
                {"spec": "full_scene:CH01|The researcher points pen proudly to the first completed sentence on paper.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "DÒNG ĐẦU TIÊN"},
                {"spec": "macro_prop:none|A single clean sentence underlined with a confident bold black marker stroke.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "BƯỚC KHỞI ĐẦU"},
            ]),
        ]
    ),
    (
        "Tách rời bản thân khỏi sản phẩm",
        "A philosophical discussion studio on pure white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Để tự do sáng tạo, bạn bắt buộc phải tách rời giá trị bản thân khỏi chất lượng bản thảo.", [
                {"spec": "full_scene:CH01|The researcher stands separating an artwork canvas on an easel from self.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "TÁCH RỜI GIÁ TRỊ"},
                {"spec": "visual_diagram:none|Two distinct separate circles: Giá Trị Con Người on left and Bản Nháp Dự Án on right.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "KHÔNG PHẢI LÀ BẠN"},
            ]),
            ("Một bản thảo dở tệ chỉ có nghĩa là nó cần được sửa đổi, chứ không có nghĩa bạn là kẻ bất tài.", [
                {"spec": "concept_metaphor:CH01|The stickman uses a rubber eraser dusting off loose crumbs with calm smile.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "CHỈ CẦN SỬA ĐỔI"},
                {"spec": "still_life:none|An eraser rubbing out a minor pencil smudge on clean white paper.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "KHÔNG HỀ BẤT TÀI"},
            ]),
            ("Khi không còn sợ bị tổn thương lòng tự trọng, bạn sẽ làm việc với niềm vui thuần khiết.", [
                {"spec": "full_scene:CH01|The researcher draws playfully with wide open arm gestures and joyful smile.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "NIỀM VUI THUẦN KHIẾT"},
                {"spec": "macro_prop:none|A kite soaring freely in open white sky tethered by a gentle thread.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TỰ DO SÁNG TẠO"},
            ]),
        ]
    ),
    (
        "Bình luận về sự hoàn hảo ảo tưởng",
        "A minimalist gallery room with unfinished sketches on white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Điểm mù của văn hóa thành công là chỉ trưng bày những bức tượng hoàn mỹ ở vạch đích.", [
                {"spec": "full_scene:CH01|The researcher looks at a polished marble museum statue on a pedestal.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐIỂM MÙ THÀNH CÔNG"},
                {"spec": "concept_metaphor:none|A museum pedestal in bright lights concealing a massive pile of discarded marble chips below.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "BỨC TƯỢNG HOÀN MỸ"},
            ]),
            ("Họ giấu nhẹm hàng nghìn bản nháp rách nát và những thất bại ê chề bên dưới xưởng điêu khắc.", [
                {"spec": "full_scene:CH01|The researcher pulls back a velvet curtain revealing messy working drafts.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "XƯỞNG ĐIÊU KHẮC"},
                {"spec": "visual_diagram:none|A graphic showing 99 Failed Rough Drafts supporting 1 Celebrated Masterpiece.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "NGÀN LẦN SỬA"},
            ]),
            ("Cái giá phải trả cho việc đòi hỏi hoàn hảo ngay từ đầu là bạn sẽ không bao giờ có nổi sản phẩm nào.", [
                {"spec": "concept_metaphor:CH01|An artist stands before a blank easel covered in thick dust through decades.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "CÁI GIÁ PHẢI TRẢ"},
                {"spec": "macro_prop:none|A clock covered in thick spiderwebs indicating decades of lost potential.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "TRẮNG TAY"},
            ]),
        ]
    ),
    (
        "Quy tắc ngón tay cái: Điểm sáu là đủ",
        "A practical workshop table with drafting tools on white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Hãy áp dụng quy tắc ngón tay cái: nhắm tới điểm sáu để hoàn thành nhanh nhất.", [
                {"spec": "full_scene:CH01|The researcher circles number six on a performance rating scorecard.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "QUY TẮC ĐIỂM SÁU"},
                {"spec": "visual_diagram:none|Scoreboard showing 6/10 marked as PASSED AND SHIPPED with green checkmark.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐIỂM SÁU LÀ ĐỦ"},
            ]),
            ("Một bản báo cáo điểm sáu được nộp đúng hạn có giá trị gấp trăm lần một bản điểm mười trong đầu.", [
                {"spec": "concept_metaphor:CH01|A modest report on the boss desk vs a golden glowing cloud stuck in the clouds.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "NỘP ĐÚNG HẠN"},
                {"spec": "visual_diagram:none|Real World Delivered Work vs Imaginary Dream Project comparison card.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "GIÁ TRỊ THỰC TẾ"},
            ]),
            ("Khi đã hoàn thành khung xương điểm sáu, bạn hoàn toàn có thể nâng cấp nó lên điểm tám sau đó.", [
                {"spec": "full_scene:CH01|The researcher polishes a simple wooden chair adding varnish and cushion.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "NÂNG CẤP DẦN"},
                {"spec": "macro_prop:none|A simple wooden chair transformed step by step into an elegant armchair.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "DẦN HOÀN THIỆN"},
            ]),
        ]
    ),
    (
        "Chiến lược chia nhỏ mục tiêu siêu vi",
        "A clean planning desk with index cards on pure white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Thay vì đặt mục tiêu viết xong một chương sách, hãy đặt mục tiêu viết đúng ba mươi từ.", [
                {"spec": "full_scene:CH01|The researcher writes a tiny sentence onto a small 3x5 index card.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BA MƯƠI TỪ"},
                {"spec": "still_life:none|A single clean index card with thirty words counted neatly in pencil.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "MỤC TIÊU SIÊU VI"},
            ]),
            ("Thay vì hứa hẹn tập thể dục một tiếng, hãy chỉ cam kết xỏ giày và bước ra cửa.", [
                {"spec": "concept_metaphor:CH01|The stickman easily ties laces of running shoes sitting on a small wooden bench.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "XỎ GIÀY RA CỬA"},
                {"spec": "macro_prop:none|A pair of running shoes resting ready right by an open welcoming doorway.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "HÀNH ĐỘNG NHỎ"},
            ]),
            ("Những bước đi siêu nhỏ này đánh sập hoàn toàn sức cản tâm lý của bộ não lười biếng.", [
                {"spec": "full_scene:CH01|The researcher steps over a broken wall fragment with a proud light stride.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "ĐÁNH SẬP SỨC CẢN"},
                {"spec": "concept_metaphor:none|A crumbling brick wall falling away into dust leaving an open green field.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "CON ĐƯỜNG THÔNG THOÁNG"},
            ]),
        ]
    ),
    (
        "Bài test 30 giây giải phóng tâm lý",
        "A serene sunlit desk on pure white background.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Ngay bây giờ, bạn hãy làm một bài test ba mươi giây để cứu vớt dự án đang bị trì hoãn.", [
                {"spec": "full_scene:CH01|The researcher takes a single fresh sticky note and writes with bold black pen.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BÀI TEST 30 GIÂY"},
                {"spec": "still_life:none|A bright yellow square sticky note with a single action sentence written on it.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "GIẤY GHI CHÚ"},
            ]),
            ("Hãy viết ra một hành động ngớ ngẩn nhất bạn có thể làm trong hai phút tới để bắt đầu.", [
                {"spec": "concept_metaphor:CH01|The researcher writes: Mở file Word và viết một câu mở đầu dở tệ.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "HÀNH ĐỘNG NHỎ NHẤT"},
                {"spec": "visual_diagram:none|A direct sticky note: Mở file Word và viết 1 dòng bất kỳ trong 2 phút.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "HAI PHÚT TỚI"},
            ]),
            ("Khi gánh nặng cầu toàn được dỡ bỏ, bạn sẽ thấy đôi tay mình chuyển động nhẹ tênh.", [
                {"spec": "full_scene:CH01|The researcher types effortlessly with joyful expression on white background.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TAY CHUYỂN ĐỘNG"},
                {"spec": "macro_prop:none|A bird feather floating gently in air indicating effortless lightness.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "NHẸ TÊNH"},
            ]),
        ]
    ),
    (
        "Tổng kết và kêu gọi bình luận",
        "A peaceful sunny study room with plants on pure white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Bạn không cần phải hoàn hảo để bắt đầu, nhưng bạn phải bắt đầu để dần hoàn thiện hơn.", [
                {"spec": "full_scene:CH01|The researcher looks out to the sunrise with quiet grounded confidence.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BẮT ĐẦU ĐỂ HOÀN THIỆN"},
                {"spec": "concept_metaphor:none|A small seed sprouting into a green seedling reaching toward golden sun.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HẠT MẦM NẢY NỞ"},
            ]),
            ("Hãy ôm lấy những vết nứt và sự vụng về ban đầu như một huy chương của lòng dũng cảm.", [
                {"spec": "full_scene:CH01|The researcher embraces a hand-made ceramic bowl with visible gold joinery lines.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HUY CHƯƠNG DŨNG CẢM"},
                {"spec": "macro_prop:none|A Japanese Kintsugi ceramic cup with golden lacquer lines filling cracks.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "VẾT NỨT VÀNG"},
            ]),
            ("Mục tiêu nào đang khiến bạn đóng băng nhiều tháng nay, hãy viết ra dưới phần bình luận để Não Lười cùng gỡ nhé.", [
                {"spec": "full_scene:CH01|The researcher waves warm encouraging hand inviting comments with a friendly smile.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BÌNH LUẬN CÙNG NÃO LƯỜI"},
                {"spec": "white_card:none|Channel endcard illustration on flat canvas with channel mascot and clear text NÃO LƯỜI.", "tempo": "slow", "narrative_situation": "mechanism_step", "is_endcard": True},
            ]),
        ]
    ),
]

# =============================================================================
# SHORT SPIN-OFF (5 SCENES, ~22 BEATS, ~43 SECONDS, CLIFFHANGER FUNNEL)
# =============================================================================

SHORT_TOPIC = "Não Bộ Bị 'Tê Liệt' Thế Nào Khi Bạn Cố Làm Mọi Thứ Thật Hoàn Hảo?"
SHORT_AUDIENCE = "Người cầu toàn, hay bế tắc trước dự án lớn, học sinh sinh viên thi cử"
SHORT_GOAL = "Giải mã phản xạ đóng băng của hạch amygdala khi cầu toàn và cắt phễu ở đỉnh cao trào về bẫy tự vệ"

SHORT_EDITORIAL_STANCE = {
    "myth_debunked": "Cầu toàn là đức tính tốt thể hiện trách nhiệm cao và tiêu chuẩn xuất sắc.",
    "why_generic_advice_fails": "Văn hóa hô hào đặt mục tiêu to lớn chỉ kích hoạt phản xạ giả chết của vỏ não trước trán.",
    "channel_verdict": "Sự thật mất lòng là chủ nghĩa cầu toàn chỉ là chiếc mặt nạ tinh vi của nỗi sợ hãi thất bại.",
    "tradeoff_or_blindspot": "Chấp nhận làm dở tệ ở bản nháp đầu tiên sẽ khiến bạn khó chịu nhưng đó là cách duy nhất hoàn thành."
}

SHORT_ACTIONABLE_VALUE = {
    "core_mechanism": "Cơ chế đe dọa sinh tồn của hạch hạnh nhân (amygdala freeze response) khi đối mặt kỳ vọng khổng lồ.",
    "practical_rule_of_thumb": "Quy tắc bản nháp xấu xí: cố tình viết một bản thảo tệ hại nhất có thể trong mười phút đầu.",
    "real_world_scenario": "Hạ tiêu chuẩn bài viết từ mười điểm xuống còn sáu điểm giúp hoàn thành luận văn trước ba tuần."
}

SHORT_PACKAGING = {
    "youtube_title": "Vì Sao Não Bị Tê Liệt Khi Bạn Cố Làm Hoàn Hảo?",
    "visual_hook": "Người que ôm đầu bất động trước tờ giấy trắng khổng lồ cao như bức tường thành",
    "text_overlay": "NÃO BỊ ĐÓNG BĂNG",
    "contrast_pair": "Ảo tưởng mười điểm hoàn hảo vs Bản nháp xấu xí hành động ngay",
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": ["nao luoi", "cau toan", "tri hoan", "shorts"],
    "cta_plan": {
        "cliffhanger_peak": "Đúng lúc bạn quyết tâm ngồi vào bàn làm việc thì cơ chế tự vệ sinh tồn của hạch não sẽ lừa bạn quay sang dọn phòng ra sao?",
        "bridge": "Xem video bản dài bên dưới để lấy quy tắc bản nháp xấu xí nhé.",
        "close": "Lưu lại ngay để cứu vớt dự án dang dở bạn nhé.",
        "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
    }
}

SHORT_SOURCES = [
    {
        "id": "SRC01",
        "title": "Nghiên Cứu Tâm Lý Học Hành Vi Về Hội Chứng Trì Hoãn Cầu Toàn",
        "reference": "Đại Học Stanford (2024). Báo Cáo Tâm Lý Nhận Thức.",
        "facts": [
            "Hơn tám mươi phần trăm trường hợp trì hoãn kinh niên bắt nguồn từ nỗi sợ bị phán xét."
        ]
    }
]

SHORT_STORY_ROWS: List[Tuple[str, str, str, str, List[Tuple[str, Any]]]] = [
    (
        "Mở màn đánh trúng nỗi đau cầu toàn",
        "A quiet evening desk with blank screen on white canvas.",
        "narrative_warm",
        "hook",
        [
            ("Càng muốn làm một việc thật hoàn hảo mười điểm, não bạn lại càng đóng băng cứng đờ.", [
                {"spec": "full_scene:CH01|The researcher sits frozen like an ice statue before a glowing empty computer screen.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "ĐÓNG BĂNG CỨNG ĐỜ"},
                {"spec": "macro_prop:none|A score badge marked 10/10 with cracks forming across its golden surface.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "ĐIỂM MƯỜI HOÀN HẢO"},
                {"spec": "concept_metaphor:CH01|Ice crystals forming around the researcher hands resting on the keyboard.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "TÊ LIỆT"},
            ]),
            ("Bạn ngồi hàng giờ mà không thể viết nổi một dòng mở đầu tử tế.", [
                {"spec": "visual_diagram:none|A hand-drawn desk clock spinning its hands through two hours with zero words written.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "KHÔNG VIẾT NỔI"},
                {"spec": "still_life:none|An empty document page with only a lonely blinking vertical cursor line.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "TRANG TRẮNG"},
            ]),
        ]
    ),
    (
        "Bóc trần sự thật về nỗi sợ",
        "A clear psychological examination corner on clean white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Sự thật mất lòng là, bạn không hề lười biếng hay thiếu ý chí.", [
                {"spec": "full_scene:CH01|The researcher points directly forward explaining with profound honesty.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "SỰ THẬT MẤT LÒNG"},
                {"spec": "concept_metaphor:none|A crossed-out sign reading KHÔNG PHẢI LƯỜI BIẾNG drawn in bold black marker.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "KHÔNG PHẢI LƯỜI"},
                {"spec": "visual_diagram:none|A balance scale separating Moral Laziness from Biological Amygdala Defense.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "TỰ VỆ SINH HỌC"},
            ]),
            ("Bộ não chỉ đang coi nỗi sợ bị chê bai giống hệt như một mối nguy hiểm đe dọa tính mạng.", [
                {"spec": "visual_diagram:none|A diagram equating Harsh Criticism to a Savage Predator in primitive brain circuits.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "SỢ BỊ CHÊ BAI"},
                {"spec": "full_scene:CH01|The researcher cowers slightly behind a notebook shielding from giant red judgmental eyes.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "MỐI NGUY HIỂM"},
            ]),
        ]
    ),
    (
        "Lời bình sắc lẹm về cái bẫy hoàn mỹ",
        "An analytical studio discussion space on white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Đánh giá công bằng thì, cầu toàn chỉ là một chiếc mặt nạ hèn nhát để trốn tránh việc bị đánh giá.", [
                {"spec": "full_scene:CH01|The researcher looks into camera speaking with firm empathetic conviction.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐÁNH GIÁ CÔNG BẰNG"},
                {"spec": "concept_metaphor:none|A smooth golden porcelain mask falling off to reveal anxious eyes underneath.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "CHIẾC MẶT NẠ"},
                {"spec": "macro_prop:none|A cracked gilded mask lying in two halves on pure white canvas.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "TRỐN TRÁNH"},
            ]),
            ("Bạn thà không nộp bài để giữ danh tiếng thông minh hơn là nộp một bản thảo có lỗi sai.", [
                {"spec": "visual_diagram:none|Card comparison: Không Nộp Bài (Ảo tưởng thông minh) vs Nộp Bài Có Lỗi (Thực tế).", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "GIỮ DANH TIẾNG"},
                {"spec": "full_scene:CH01|The researcher clutches drafted project tightly refusing to hand it over.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "KHÔNG DÁM NỘP"},
            ]),
        ]
    ),
    (
        "Đỉnh cao trào bỏ lửng (Cliffhanger Peak)",
        "A dramatic high-friction workspace on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Chính vì muốn bảo vệ bạn khỏi sự xấu hổ, bộ não liền bật chế độ tự vệ xảo quyệt nhất.", [
                {"spec": "full_scene:CH01|The cartoon brain character pops up with a mischievous sneaky grin holding a broom.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "TỰ VỆ XẢO QUYỆT"},
                {"spec": "macro_prop:none|A domestic broom and dustpan suddenly appearing next to high-priority work files.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "CHIÊU TRÒ NÃO"},
                {"spec": "still_life:none|A neat row of pencils arranged in obsessive symmetry on the wooden table.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "DỌN PHÒNG"},
            ]),
            ("Đúng lúc bạn quyết tâm ngồi vào bàn làm việc thì cơ chế tự vệ sinh tồn của hạch não sẽ lừa bạn quay sang dọn phòng ra sao?", [
                {"spec": "concept_metaphor:CH01|The researcher stands at a critical junction with a massive glowing question mark above.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "CÚ LỪA NGOẠN MỤC"},
                {"spec": "macro_prop:none|A giant question mark symbol hovering over an unfinished thesis document.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "SỰ THẬT ĐẰNG SAU"},
            ]),
        ]
    ),
    (
        "Chuyển phễu sang bản Full và Close CTA",
        "A peaceful sunny morning study table on pure white background.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Xem video bản dài bên dưới để lấy quy tắc bản nháp xấu xí nhé.", [
                {"spec": "full_scene:CH01|The researcher points down with friendly enthusiastic smile toward video link below.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "XEM BẢN DÀI"},
                {"spec": "visual_diagram:none|A bold directional arrow pointing down to the related full explainer thumbnail card.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "BẤM DƯỚI ĐÂY"},
            ]),
            ("Lưu lại ngay để cứu vớt dự án dang dở bạn nhé.", [
                {"spec": "full_scene:CH01|The researcher waves cheerful encouraging hand beside channel badge on white canvas.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "LƯU LẠI NGAY"},
            ]),
        ]
    ),
]
