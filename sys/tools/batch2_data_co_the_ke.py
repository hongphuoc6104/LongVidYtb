# -*- coding: utf-8 -*-
"""Batch 2 Story Blueprint for Cơ Thể Kể (channel-co-the-ke).

Topic: Sự Thật Về Cơn Nghiện Đường (Long) & Cơn Thèm Đồ Ngọt Khi Căng Thẳng (Short)
Format: V3 High-Density Narrative-Driven Adaptive Visual Pacing.
"""

from typing import Any, Dict, List, Tuple

CHANNEL_ID = "co_the_ke"
CHANNEL_SLUG = "co-the-ke"

# =============================================================================
# LONG EXPLAINER (16 SCENES, ~94 BEATS, ~265 SECONDS)
# =============================================================================

LONG_TOPIC = "Sự Thật Về Cơn Nghiện Đường: Não Bộ Bị Đánh Lừa Ra Sao Khi Bạn Tưởng Mình Chỉ Đang Căng Thẳng?"
LONG_AUDIENCE = "Dân văn phòng, người hay mệt mỏi vào buổi chiều, người muốn cải thiện sức khỏe"
LONG_GOAL = "Giải mã cơ chế sinh học đằng sau cơn nghiện ngọt và bài test hai mươi phút giúp cắt cơn thèm đường"

LONG_EDITORIAL_STANCE = {
    "myth_debunked": "Bạn thèm ngọt đơn thuần là do cơ thể thiếu năng lượng và cần bổ sung calo gấp.",
    "why_generic_advice_fails": "Lời khuyên dùng ý chí sắt đá để kiêng đường luôn thất bại vì cơ chế sinh học mạnh hơn ý chí gấp bội phần.",
    "channel_verdict": "Sự thật mất lòng là đường tinh luyện hoạt động hệt như một chất gây nghiện hợp pháp thao túng hạch tưởng thưởng.",
    "tradeoff_or_blindspot": "Cắt giảm đường trong ba ngày đầu sẽ tạo ra cảm giác bồn chồn khó chịu nhưng sau đó cơ thể sẽ hồi sinh."
}

LONG_ACTIONABLE_VALUE = {
    "core_mechanism": "Vòng lặp dopamine spike kết hợp với cú sụt giảm đường huyết phản vệ do hormone insulin tiết ra quá mức.",
    "practical_rule_of_thumb": "Quy tắc trì hoãn hai mươi phút: khi cơn thèm đường ập đến, hãy uống một cốc nước ấm và đi bộ nhẹ nhàng.",
    "real_world_scenario": "Thay thế ly trà sữa ba giờ chiều bằng một nắm hạt điều và một cốc nước lọc ấm giúp tỉnh táo tới tối."
}

LONG_PACKAGING = {
    "youtube_title": "Vì Sao Bạn Càng Căng Thẳng Não Càng Thèm Ngọt?",
    "visual_hook": "Bác sĩ người que soi kính hiển vi thấy não bộ và dạ dày đang tranh cãi kịch liệt về một viên đường khổng lồ",
    "text_overlay": "NGHIỆN ĐƯỜNG",
    "contrast_pair": "Ý chí kiêng cữ mù quáng vs Hiểu đúng cơ chế sinh học hạch não",
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": ["co the ke", "nghien duong", "giai ma co the", "suc khoe van phong", "dopamine"],
    "cta_plan": {
        "mid_cta": "Nếu bạn thường xuyên bị buồn ngủ gục sau bữa trưa, hãy lưu lại video để đối chiếu chế độ ăn nhé.",
        "close": "Cơn thèm ngọt quật ngã bạn mạnh nhất vào khung giờ nào, chia sẻ cho Cơ Thể Kể biết nhé.",
        "endcard_text": "CƠ THỂ KỂ"
    }
}

LONG_SOURCES = [
    {
        "id": "SRC01",
        "title": "Nghiên Cứu Cơ Chế Tưởng Thưởng Não Bộ Với Carbohydrate Tinh Chế",
        "reference": "Tạp Chí Thần Kinh Học Lâm Sàng (2024). Khảo Sát Thói Quen Tiêu Thụ Đường.",
        "facts": [
            "Đường tinh luyện kích hoạt vùng nhân vòng não bộ tương tự như các chất kích thích.",
            "Cơn hạ đường huyết phản ứng xuất hiện trung bình chín mươi phút sau khi nạp đồ ngọt."
        ]
    }
]

LONG_STORY_ROWS: List[Tuple[str, str, str, str, List[Tuple[str, Any]]]] = [
    (
        "Cơn thèm đường lúc ba giờ chiều",
        "A quiet office workspace on pure white background.",
        "narrative_warm",
        "lived_friction",
        [
            ("Cứ khoảng ba giờ chiều, mắt bạn bắt đầu díp lại và đầu óc đặc quánh.", [
                {"spec": "full_scene:CH01|The office worker rests heavy head on the desk beside a glowing computer monitor.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "BA GIỜ CHIỀU"},
                {"spec": "macro_prop:none|A desk clock with hands pointing exactly to 15:00 on pure white canvas.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "MỆT MỎI"},
            ]),
            ("Trong đầu bạn lúc này chỉ lóe lên một mệnh lệnh duy nhất: phải uống trà sữa.", [
                {"spec": "concept_metaphor:CH01|A giant cup of iced milk tea with black boba pearls floats above the worker head.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "MỆNH LỆNH NÃO"},
                {"spec": "still_life:none|A hand-drawn milk tea cup with condensation droplets and striped straw.", "tempo": "fast", "narrative_situation": "hook_shock", "emphasis_text": "TRÀ SỮA"},
            ]),
            ("Bạn tự nhủ chỉ uống nốt hôm nay thôi để lấy lại tinh thần làm việc.", [
                {"spec": "full_scene:CH01|The worker taps delivery app order button on smartphone with guilty expression.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "NỐT HÔM NAY"},
                {"spec": "visual_diagram:none|A calendar showing the same excuse repeated across Monday, Tuesday, and Wednesday.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "LẶP LẠI"},
            ]),
        ]
    ),
    (
        "Cảm giác sảng khoái đánh lừa",
        "A biological laboratory examination space on white canvas.",
        "analytical_crisp",
        "lived_friction",
        [
            ("Ngay ngụm đầu tiên trôi qua cuống họng, một luồng sóng khoan khoái dâng lên.", [
                {"spec": "full_scene:CH01|The worker takes a sip with eyes closed in blissful relief on white background.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "KHOAN KHOÁI"},
                {"spec": "concept_metaphor:none|A bright electrical pulse traveling down a clean spinal nerve column.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "XUNG THẦN KINH"},
            ]),
            ("Bạn cảm thấy tỉnh táo tức thì, sự uể oải biến mất như có phép màu.", [
                {"spec": "full_scene:CH01|The worker sits upright smiling brightly typing fast on the keyboard.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "TỈNH TỨC THÌ"},
                {"spec": "visual_diagram:none|A battery indicator jumping instantly from red ten percent to solid green ninety percent.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "HỒI SỨC ẢO"},
            ]),
            ("Nhưng thực chất, điều kỳ diệu này chỉ là một trò lừa thị giác của hệ thần kinh.", [
                {"spec": "concept_metaphor:CH01|A friendly cartoon brain character behind a magician top hat pulling out a sugar cube.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "CÚ LỪA NÃO BỘ"},
                {"spec": "macro_prop:none|A hand-drawn sugar cube with sparkling deceitful glints on pure white canvas.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "VIÊN ĐƯỜNG"},
            ]),
        ]
    ),
    (
        "Cú sốc hạ đường huyết phản vệ",
        "A medical monitoring room with graph lines on white canvas.",
        "analytical_crisp",
        "lived_friction",
        [
            ("Chỉ khoảng một tiếng sau, mức năng lượng của bạn đột ngột rơi tự do.", [
                {"spec": "full_scene:CH01|The worker slumps back into office chair looking even more drained than before.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "RƠI TỰ DO"},
                {"spec": "visual_diagram:none|A steep rollercoaster chart plunging sharply downward after a brief peak.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "SỤT DỐC"},
            ]),
            ("Đầu óc lại mụ mẫm, tay chân run rẩy và cơn đói cồn cào ập tới dữ dội hơn.", [
                {"spec": "full_scene:CH01|The stickman holds trembling hands examining slight tremor in fingertips.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "RUN TAY"},
                {"spec": "concept_metaphor:CH01|The cartoon stomach character grumbles angrily holding an empty bowl.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐÓI CỒN CÀO"},
            ]),
            ("Khoa học gọi hiện tượng này là cú sốc hạ đường huyết phản vệ trong cơ thể.", [
                {"spec": "visual_diagram:none|Medical typography card reading HẠ ĐƯỜNG HUYẾT PHẢN VỆ with red warning border.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "HẠ ĐƯỜNG HUYẾT"},
                {"spec": "still_life:none|A stylized blood vessel showing tiny glucose particles vanishing rapidly.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "MẤT ĐƯỜNG"},
            ]),
        ]
    ),
    (
        "Vòng xoáy nghiện ngập vô tận",
        "An analytical medical space on clean white canvas.",
        "analytical_crisp",
        "lived_friction",
        [
            ("Để thoát khỏi cơn mệt mỏi, phản xạ tự nhiên của bạn là tìm thêm đồ ngọt.", [
                {"spec": "full_scene:CH01|The worker reaches into desk drawer grabbing a chocolate candy bar.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TÌM ĐỒ NGỌT"},
                {"spec": "concept_metaphor:none|A circular mouse maze with a sugar cube placed right at the starting line.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "MÊ CUNG"},
            ]),
            ("Bạn nạp thêm bánh kẹo, đường lại tăng vọt rồi lại sụt giảm không phanh.", [
                {"spec": "visual_diagram:none|A continuous sawtooth wave showing repetitive sharp spikes and deep crashes.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "VÒNG LẶP RĂNG CƯA"},
                {"spec": "concept_metaphor:CH01|The stickman running on a spiral staircase that goes round and round endlessly.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "XOẮN ỐC"},
            ]),
            ("Vô tình, bạn biến cơ thể thành một cỗ máy nghiện đường mà không hề hay biết.", [
                {"spec": "full_scene:CH01|The worker looks at reflection in mirror with realization of being trapped.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "MÁY NGHIỆN ĐƯỜNG"},
                {"spec": "macro_prop:none|A stylized padlock shaped like a sugar crystal on pure white canvas.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BỊ KHÓA CHẶT"},
            ]),
        ]
    ),
    (
        "Bóc tách cơ chế hạch tưởng thưởng não",
        "A neuroscience diagram laboratory on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Bên trong bộ não, đường kích hoạt vùng nhân vòng giải phóng dopamine ồ ạt.", [
                {"spec": "full_scene:CH01|Doctor stickman points pointer to a clear 2D side-view brain diagram.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "VÙNG NHÂN VÒNG"},
                {"spec": "visual_diagram:none|A hand-drawn brain map highlighting the nucleus accumbens in bold flat blue.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "DOPAMINE PHUN TRÀO"},
            ]),
            ("Mức độ kích hoạt này mạnh mẽ không thua kém các chất kích thích gây nghiện.", [
                {"spec": "concept_metaphor:none|A chemical receptor keyhole being flooded by bright dopamine keys.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "KÍCH HOẠT MẠNH"},
                {"spec": "visual_diagram:none|A comparative bar chart showing sugar dopamine response equal to potent stimulants.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CHẤT GÂY NGHIỆN"},
            ]),
            ("Bộ não nguyên thủy ghi nhận rằng đây là nguồn calo hiếm và ra lệnh tích trữ.", [
                {"spec": "full_scene:CH01|Cartoon prehistoric stickman forager holding ripe berries in excitement.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "BẢN NĂNG CỔ XƯA"},
                {"spec": "concept_metaphor:none|A warehouse inside the body locking up fat energy stores.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "TÍCH TRỮ"},
            ]),
        ]
    ),
    (
        "Lời bình sắc bén: Sự thật mất lòng",
        "A direct discussion space with clean bold markers on white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Sự thật mất lòng là, các tập đoàn thực phẩm đã thiết kế đồ ngọt để bạn không thể dừng lại.", [
                {"spec": "full_scene:CH01|Doctor stickman crosses arms delivering a serious and frank commentary.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "SỰ THẬT MẤT LÒNG"},
                {"spec": "concept_metaphor:none|A laboratory flask blending sugar, fat, and salt under a targeted laser.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐIỂM HẠNH PHÚC"},
            ]),
            ("Đánh giá công bằng thì, đổ lỗi cho sự thiếu ý chí là một cái bẫy tâm lý tàn nhẫn.", [
                {"spec": "full_scene:CH01|The stickman points finger straight forward defending the viewer with warmth.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐÁNH GIÁ CÔNG BẰNG"},
                {"spec": "visual_diagram:none|A hand-drawn sign with a red cross over the word Ý CHÍ, replaced by CƠ CHẾ SINH HỌC.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "CÁI BẪY Ý CHÍ"},
            ]),
            ("Đừng nghe lời khuyên kiềm chế mù quáng khi nội tiết tố bên trong đang gào thét đòi ăn.", [
                {"spec": "concept_metaphor:CH01|The stickman shields ears from loud screaming horn icons labeled HORMONE.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "HORMONE GÀO THÉT"},
                {"spec": "macro_prop:none|A megaphone emitting sound waves representing biological chemical signals.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "TÍN HIỆU SINH HỌC"},
            ]),
        ]
    ),
    (
        "Điểm dừng rà soát thói quen và Mid-CTA",
        "A peaceful sunny room with tea mug on white background.",
        "narrative_warm",
        "structural_model",
        [
            ("Hãy nhìn lại thực đơn ăn uống trong tuần qua của bạn một cách trung thực.", [
                {"spec": "full_scene:CH01|The stickman sits reviewing a weekly food diary notebook with a pencil.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "NHÌN LẠI THỰC ĐƠN"},
                {"spec": "still_life:none|A notepad with items like Trà sữa, Bánh ngọt, Cà phê sữa đá listed neatly.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "SỔ TAY"},
            ]),
            ("Nếu bạn thường xuyên bị buồn ngủ gục sau bữa trưa, hãy lưu lại video để đối chiếu chế độ ăn nhé.", [
                {"spec": "full_scene:CH01|The stickman smiles kindly gesturing toward the save bookmark icon.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LƯU VIDEO ĐỐI CHIẾU"},
                {"spec": "macro_prop:none|A clean bookmark emblem with a small smiling face drawn in black marker.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "LƯU LẠI"},
            ]),
            ("Bây giờ, chúng ta sẽ bóc tách cơ chế tụy tạng và giải pháp cắt cơn nghiện.", [
                {"spec": "concept_metaphor:CH01|Doctor stickman unfurls an anatomical chart of the pancreas on white board.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CƠ CHẾ TỤY TẠNG"},
                {"spec": "visual_diagram:none|A friendly hand-drawn pancreas character ready with an insulin spray nozzle.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "TUYẾN TỤY"},
            ]),
        ]
    ),
    (
        "Vai trò của tụy tạng và hormone Insulin",
        "An anatomical science visual space on white background.",
        "analytical_crisp",
        "structural_model",
        [
            ("Mỗi khi bạn nạp lượng lớn đường lỏng, lượng glucose trong máu tăng vọt như núi lửa.", [
                {"spec": "full_scene:CH01|Doctor stickman monitors a rapidly rising red mercury column in a glass tube.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐƯỜNG MÁU TĂNG VỌT"},
                {"spec": "visual_diagram:none|A blood capillary overflowing with sharp red glucose hexagon shapes.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "NGẬP ĐƯỜNG"},
            ]),
            ("Tụy tạng hốt hoảng bơm một lượng khổng lồ insulin để dập tắt mối đe dọa này.", [
                {"spec": "concept_metaphor:CH01|Cartoon pancreas character dressed as a firefighter spraying insulin foam.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "BƠM INSULIN"},
                {"spec": "still_life:none|A fire extinguisher labeled INSULIN spraying clouds of white calming foam.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "DẬP LỬA"},
            ]),
            ("Insulin quét sạch đường ra khỏi máu và nhét vội vã vào các tế bào mỡ tích trữ.", [
                {"spec": "full_scene:CH01|Insulin characters rapidly pack sugar cubes into giant storage barrels.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "TÍCH VÀO MỠ"},
                {"spec": "concept_metaphor:none|A stylized adipocyte fat cell bulging as it absorbs extra fuel packages.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "TẾ BÀO MỠ"},
            ]),
        ]
    ),
    (
        "Hiện tượng đường huyết lao dốc không phanh",
        "A biological laboratory examination space on white canvas.",
        "analytical_crisp",
        "structural_model",
        [
            ("Chính vì insulin tiết ra quá đà, lượng đường huyết bị tụt xuống thấp hơn mức bình thường.", [
                {"spec": "full_scene:CH01|The stickman watches a line graph dip well below the baseline into a danger zone.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TỤT DƯỚI ĐÁY"},
                {"spec": "visual_diagram:none|A graph showing baseline level at 100, plunging down to 50 in sharp descent.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "DƯỚI CHUẨN"},
            ]),
            ("Não bộ bị thiếu hụt nhiên liệu lập tức gửi tín hiệu báo động khẩn cấp khắp cơ thể.", [
                {"spec": "concept_metaphor:CH01|A flashing red alarm siren rotating atop the cartoon brain character.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "BÁO ĐỘNG KHẨN"},
                {"spec": "macro_prop:none|A hand-drawn emergency siren with sharp sound waves expanding outward.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "THIẾU NHIÊN LIỆU"},
            ]),
            ("Nó phát ra mệnh lệnh đói cồn cào để buộc bạn phải tiếp tục ăn đồ ngọt ngay.", [
                {"spec": "full_scene:CH01|The worker clutches stomach with an urgent hungry expression on white background.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "BUỘC PHẢI ĂN"},
                {"spec": "concept_metaphor:none|A hand puppet brain pulling puppet strings attached to the worker hands.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "RỐI DÂY"},
            ]),
        ]
    ),
    (
        "Nghịch lý giữa no và đói",
        "A clear studio desk with contrast cards on white canvas.",
        "narrative_warm",
        "structural_model",
        [
            ("Nghịch lý nằm ở chỗ: cơ thể bạn vừa nạp thừa calo nhưng não bộ lại thấy chết đói.", [
                {"spec": "full_scene:CH01|The stickman stands between a pile of food on left and an empty brain battery on right.", "tempo": "normal", "narrative_situation": "before_after_contrast", "emphasis_text": "NGHỊCH LÝ NẰM Ở"},
                {"spec": "visual_diagram:none|A split comparison: 500 Calories Consumed on one side vs Brain Starving on the other.", "tempo": "normal", "narrative_situation": "before_after_contrast", "emphasis_text": "THỪA CALO NÃO ĐÓI"},
            ]),
            ("Bạn tích mỡ ở vòng bụng trong khi năng lượng làm việc lại hoàn toàn cạn kiệt.", [
                {"spec": "full_scene:CH01|The worker looks down at waistline tape measure with an informative frown.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "TÍCH MỠ BỤNG"},
                {"spec": "concept_metaphor:none|A fuel tank with a heavy locked safe on top but zero gas running to the engine.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CẠN NĂNG LƯỢNG"},
            ]),
            ("Hiểu được cơ chế này là chìa khóa giúp bạn ngừng tự dằn vặt bản thân mỗi ngày.", [
                {"spec": "concept_metaphor:CH01|The worker unlocks a heavy metal padlock around the chest using a golden key.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "NGỪNG DẰN VẶT"},
                {"spec": "macro_prop:none|An open shiny padlock indicating freedom from guilt on pure white canvas.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TỰ DO"},
            ]),
        ]
    ),
    (
        "Thí nghiệm lâm sàng: Bài test 20 phút",
        "A clean kitchen counter space on pure white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Cơn thèm đường do dopamine thúc đẩy thực chất chỉ kéo dài tối đa hai mươi phút.", [
                {"spec": "full_scene:CH01|Doctor stickman points to a digital timer counting down from 20:00 to 00:00.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CHỈ HAI MƯƠI PHÚT"},
                {"spec": "visual_diagram:none|A bell curve showing craving intensity peaking at minute 7 and dropping to zero at minute 20.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CƠN SÓNG TẠM THỜI"},
            ]),
            ("Nếu bạn vượt qua được đỉnh sóng này, não bộ sẽ tự động chuyển sang chế độ đốt mỡ.", [
                {"spec": "concept_metaphor:CH01|The stickman surfs calmly over the crest of an ocean wave onto a safe shore.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "VƯỢT ĐỈNH SÓNG"},
                {"spec": "visual_diagram:none|Metabolic switch toggling from Sugar Burning Mode to Fat Burning Mode.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "ĐỐT MỠ"},
            ]),
            ("Bạn sẽ thấy cơn cồn cào biến mất hoàn toàn và sự tập trung quay trở lại rõ rệt.", [
                {"spec": "full_scene:CH01|The worker opens eyes widely with clear calm focus looking at clean notes.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TẬP TRUNG LẠI"},
                {"spec": "macro_prop:none|A crystal clear magnifying lens focusing sharp light onto a single point.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "SÁNG RÕ"},
            ]),
        ]
    ),
    (
        "Bình luận về cái giá phải trả",
        "An open studio reflection corner on pure white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Cái giá phải trả khi cắt giảm đường trong ba ngày đầu là cảm giác cáu gắt và bức bối.", [
                {"spec": "full_scene:CH01|The stickman stands with furrowed brow acknowledging the discomfort honestly.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "CÁI GIÁ PHẢI TRẢ"},
                {"spec": "concept_metaphor:none|A small storm cloud with mild lightning hovering briefly above the desk.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "CÁU GẮT BA NGÀY"},
            ]),
            ("Điểm mù của nhiều người là bỏ cuộc ngay ngày thứ hai vì tưởng cơ thể bị suy nhược.", [
                {"spec": "full_scene:CH01|The stickman points to Day 2 on a calendar marked with a warning question badge.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐIỂM MÙ NGÀY THỨ HAI"},
                {"spec": "visual_diagram:none|A path showing people turning back right before the finish line banner.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "BỎ CUỘC SỚM"},
            ]),
            ("Nhìn thẳng vào thực tế thì, đó chỉ là triệu chứng cai nghiện tạm thời khi não quen ăn ngọt.", [
                {"spec": "concept_metaphor:CH01|The worker steadily walks forward stepping out from the storm cloud into sunshine.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "NHÌN VÀO THỰC TẾ"},
                {"spec": "macro_prop:none|A sunrise silhouette with golden rays spreading across flat white background.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "TRIỆU CHỨNG CAI"},
            ]),
        ]
    ),
    (
        "Quy tắc ngón tay cái: Ba bước cắt cơn thèm",
        "A healthy morning pantry space on pure white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Khi cơn thèm ngọt ập đến, hãy thực hiện ngay quy tắc ba bước đánh lừa cảm giác.", [
                {"spec": "full_scene:CH01|Doctor stickman displays three clear fingers outlining the rescue steps.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "QUY TẮC BA BƯỚC"},
                {"spec": "visual_diagram:none|Three sequential action icons: Water Glass, Movement Walk, Handful Nuts.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "BA BƯỚC CỨU CÁNH"},
            ]),
            ("Bước một: Uống chậm rãi một cốc nước lọc ấm để lấp đầy thể tích dạ dày.", [
                {"spec": "full_scene:CH01|The worker sips from a steaming glass mug of warm clean water.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "UỐNG NƯỚC ẤM"},
                {"spec": "macro_prop:none|A tall glass with warm steam wafting upward drawn in crisp black ink.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "CỐC NƯỚC LỌC"},
            ]),
            ("Bước hai: Đứng dậy đi bộ nhẹ nhàng năm phút để kích thích cơ bắp tiêu thụ đường tồn dư.", [
                {"spec": "full_scene:CH01|The worker steps briskly along an open hallway pathway with relaxed shoulders.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "ĐI BỘ NĂM PHÚT"},
                {"spec": "concept_metaphor:none|A pair of sneakers leaving light trail footprints on pure white canvas.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "VẬN ĐỘNG"},
            ]),
        ]
    ),
    (
        "Chiến lược thay thế thông minh: Hạt và Đạm",
        "A tidy kitchen counter with snack jars on white canvas.",
        "analytical_crisp",
        "actionable_resolution",
        [
            ("Bước ba: Thay thế đồ ngọt tinh chế bằng một nắm hạt điều hoặc hạnh nhân giàu chất béo tốt.", [
                {"spec": "full_scene:CH01|The stickman holds a small ceramic bowl containing mixed roasted cashews.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "THAY BẰNG HẠT"},
                {"spec": "still_life:none|A handful of golden cashew nuts and almonds drawn in flat warm colors.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CHẤT BÉO TỐT"},
            ]),
            ("Chất béo và đạm lành mạnh giải phóng năng lượng từ từ, giữ đường huyết ổn định suốt buổi chiều.", [
                {"spec": "visual_diagram:none|A smooth flat green line of steady energy contrasted against a spiky red sugar line.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "NĂNG LƯỢNG BỀN"},
                {"spec": "concept_metaphor:CH01|A steady solid brick foundation supporting a calm working desk.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "ĐƯỜNG HUYẾT ÊM"},
            ]),
            ("Bạn sẽ làm việc năng suất liên tục tới tận bữa tối mà không một lần ngáp vặt.", [
                {"spec": "full_scene:CH01|The worker finishes tasks efficiently packing bag with cheerful satisfaction.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "HẾT NGÁP VẶT"},
                {"spec": "macro_prop:none|A completed daily to-do checklist with all five boxes checked off in green.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "XONG VIỆC"},
            ]),
        ]
    ),
    (
        "Kế hoạch thực hành ngay chiều nay",
        "A modern office breakroom table on pure white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Chiều nay khi cơn thèm đường xuất hiện, bạn đừng tự trách hay vội vàng nhịn nhục.", [
                {"spec": "full_scene:CH01|The worker stands calmly beside office snack corner with clear perspective.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐỪNG TỰ TRÁCH"},
                {"spec": "concept_metaphor:none|A gentle shield deflecting negative self-critical speech bubbles.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "THẤU HIỂU"},
            ]),
            ("Hãy bật đồng hồ bấm giờ hai mươi phút và nhâm nhi một ly trà hoa cúc thanh nhiệt.", [
                {"spec": "full_scene:CH01|The worker taps smartphone timer to twenty minutes holding water bottle.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "BẬT HẸN GIỜ"},
                {"spec": "macro_prop:none|A digital countdown timer at 20:00 with a pulsing green indicator.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "HAI MƯƠI PHÚT"},
            ]),
            ("Bạn sẽ kinh ngạc khi thấy cơ thể tự chữa lành và cơn thèm tan biến như bọt xà phòng.", [
                {"spec": "full_scene:CH01|The stickman smiles with deep relief as small bubbles float away into air.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TAN BIẾN"},
                {"spec": "macro_prop:none|A soap bubble popping cleanly into tiny sparkles on pure white canvas.", "tempo": "fast", "narrative_situation": "story_action", "emphasis_text": "TỰ CHỮA LÀNH"},
            ]),
        ]
    ),
    (
        "Tổng kết và kêu gọi chia sẻ",
        "A peaceful sunny consultation desk on pure white canvas.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Cơ thể bạn luôn biết cách cân bằng nếu bạn cung cấp đúng loại nhiên liệu nó cần.", [
                {"spec": "full_scene:CH01|Doctor stickman stands beside a thriving green potted plant on pure white canvas.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CƠ THỂ CÂN BẰNG"},
                {"spec": "concept_metaphor:none|A balanced golden mobile sculpture turning gracefully in equilibrium.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "ĐÚNG NHIÊN LIỆU"},
            ]),
            ("Yêu thương bản thân bắt đầu từ việc hiểu rõ từng phản ứng hóa học bên trong tế bào.", [
                {"spec": "full_scene:CH01|The stickman places hand over heart with gentle warm smile on white background.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "YÊU THƯƠNG BẢN THÂN"},
                {"spec": "macro_prop:none|A clean glowing heart outline with a microscopic cell nucleus at its core.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "TỪ TẾ BÀO"},
            ]),
            ("Cơn thèm ngọt quật ngã bạn mạnh nhất vào khung giờ nào, chia sẻ cho Cơ Thể Kể biết nhé.", [
                {"spec": "full_scene:CH01|Doctor stickman waves friendly hand inviting conversation in comments.", "tempo": "normal", "narrative_situation": "mechanism_step", "emphasis_text": "CHIA SẺ NHÉ"},
                {"spec": "white_card:none|Channel endcard illustration on flat canvas with channel mascot and clear text CƠ THỂ KỂ.", "tempo": "slow", "narrative_situation": "mechanism_step", "is_endcard": True},
            ]),
        ]
    ),
]

# =============================================================================
# SHORT SPIN-OFF (5 SCENES, ~19 BEATS, ~43 SECONDS, CLIFFHANGER FUNNEL)
# =============================================================================

SHORT_TOPIC = "Vì Sao Càng Căng Thẳng Não Càng Thèm Đồ Ngọt Điên Cuồng?"
SHORT_AUDIENCE = "Dân văn phòng, người hay thèm trà sữa ăn vặt mỗi khi áp lực công việc"
SHORT_GOAL = "Giải mã cơn thèm ngọt khi stress và cắt phễu ở câu hỏi đỉnh cao trào về cú sập đường huyết phản ứng"

SHORT_EDITORIAL_STANCE = {
    "myth_debunked": "Bạn thèm ngọt đơn thuần là do cơ thể thiếu năng lượng và cần bổ sung calo gấp.",
    "why_generic_advice_fails": "Lời khuyên dùng ý chí sắt đá để kiêng đường luôn thất bại vì cơ chế sinh học mạnh hơn ý chí gấp bội.",
    "channel_verdict": "Sự thật mất lòng là đường tinh luyện hoạt động hệt như một chất gây nghiện hợp pháp.",
    "tradeoff_or_blindspot": "Cắt giảm đường trong ba ngày đầu sẽ tạo ra cảm giác bồn chồn khó chịu nhưng sau đó cơ thể hồi sinh."
}

SHORT_ACTIONABLE_VALUE = {
    "core_mechanism": "Vòng lặp dopamine spike kết hợp với cú sụt giảm đường huyết phản vệ do hormone insulin tiết ra quá mức.",
    "practical_rule_of_thumb": "Quy tắc trì hoãn hai mươi phút: khi cơn thèm đường ập đến, hãy uống một cốc nước ấm và đi bộ.",
    "real_world_scenario": "Thay thế ly trà sữa ba giờ chiều bằng một cốc nước lọc ấm và nắm hạt điều giúp tỉnh táo tới tối."
}

SHORT_PACKAGING = {
    "youtube_title": "Vì Sao Căng Thẳng Lại Thèm Ngọt Điên Cuồng?",
    "visual_hook": "Người que ôm đầu căng thẳng trước đống tài liệu, mắt nhìn chằm chằm ly trà sữa khổng lồ",
    "text_overlay": "THÈM NGỌT KHI STRESS",
    "contrast_pair": "Ăn ngọt giải tỏa tức thì vs Cú sốc sụt đường huyết sau 1 tiếng",
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": ["co the ke", "them ngot", "stress", "shorts"],
    "cta_plan": {
        "cliffhanger_peak": "Đúng lúc bạn nghĩ ly nước ngọt đã cứu vớt sự tỉnh táo thì cơn bão insulin ngầm đang đánh sập toàn bộ đường huyết của bạn ra sao?",
        "bridge": "Xem video bản dài bên dưới để lấy bài test hai mươi phút nhé.",
        "close": "Lưu lại ngay để cứu vớt buổi chiều làm việc bạn nhé.",
        "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"
    }
}

SHORT_SOURCES = [
    {
        "id": "SRC01",
        "title": "Nghiên Cứu Cơ Chế Tưởng Thưởng Não Bộ Với Carbohydrate Tinh Chế",
        "reference": "Tạp Chí Thần Kinh Học Lâm Sàng (2024). Khảo Sát Thói Quen Tiêu Thụ Đường.",
        "facts": [
            "Đường tinh luyện kích hoạt vùng nhân vòng não bộ tương tự như các chất kích thích."
        ]
    }
]

SHORT_STORY_ROWS: List[Tuple[str, str, str, str, List[Tuple[str, Any]]]] = [
    (
        "Mở màn đánh trúng nỗi đau văn phòng",
        "A busy office desk with laptop on white canvas.",
        "narrative_warm",
        "hook",
        [
            ("Càng căng thẳng vì áp lực công việc, bạn lại càng thèm đồ ngọt đến phát điên.", [
                {"spec": "full_scene:CH01|The office worker clutches temples in acute stress while staring at a giant cupcake on desk.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "CÀNG CĂNG THẲNG"},
                {"spec": "macro_prop:none|A giant frosted cupcake with thick sprinkles rendered in bold doodle ink.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "THÈM PHÁT ĐIÊN"},
            ]),
            ("Đó hoàn toàn không phải vì dạ dày bạn đang đói calo.", [
                {"spec": "visual_diagram:none|A hand-drawn stomach icon showing fully green satisfied fuel bar on white canvas.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "DẠ DÀY KHÔNG ĐÓI"},
                {"spec": "concept_metaphor:CH01|The worker shakes head looking at the full stomach fuel gauge.", "tempo": "burst", "narrative_situation": "hook_shock", "emphasis_text": "KHÔNG THIẾU CALO"},
            ]),
        ]
    ),
    (
        "Bóc trần sự thật ngược đời về hóc-môn",
        "A clear medical demonstration space on clean white canvas.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Sự thật mất lòng là, hormone căng thẳng cortisol đang trực tiếp tống tiền bộ não bạn.", [
                {"spec": "full_scene:CH01|Doctor stickman points to an aggressive cartoon hormone character demanding sugar.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "SỰ THẬT MẤT LÒNG"},
                {"spec": "concept_metaphor:none|A tiny cartoon cortisol bandit demanding sugar bags in exchange for temporary peace.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "TỐNG TIỀN NÃO"},
            ]),
            ("Nó ép não phải kích hoạt hạch tưởng thưởng bằng một liều dopamine cấp tốc từ đường tinh luyện.", [
                {"spec": "visual_diagram:none|A chemical syringe labeled DOPAMINE injecting directly into a reward circuit chart.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "LIỀU DOPAMINE"},
                {"spec": "full_scene:CH01|The worker gulps down sweet milk tea feeling instant artificial relief.", "tempo": "fast", "narrative_situation": "before_after_contrast", "emphasis_text": "SẢNG KHOÁI ẢO"},
            ]),
        ]
    ),
    (
        "Lời bình sắc lẹm và cái bẫy sinh học",
        "An analytical discussion studio on white background.",
        "analytical_crisp",
        "structural_model",
        [
            ("Đánh giá công bằng thì, việc uống trà sữa lúc này chỉ giống như dập tắt đám cháy bằng xăng.", [
                {"spec": "full_scene:CH01|Doctor stickman looks straight into camera speaking with honest earnest conviction.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "ĐÁNH GIÁ CÔNG BẰNG"},
                {"spec": "concept_metaphor:none|A hand pouring a gas canister labeled ĐƯỜNG onto a small smoldering fire labeled STRESS.", "tempo": "slow", "narrative_situation": "editorial_commentary", "emphasis_text": "CHỮA CHÁY BẰNG XĂNG"},
            ]),
            ("Bạn cảm thấy tỉnh táo được ba mươi phút đầu, nhưng ngay sau đó là thảm họa rơi tự do.", [
                {"spec": "visual_diagram:none|A line graph showing 30 minutes of high peak followed by a precipitous drop below zero.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "BA MƯƠI PHÚT"},
                {"spec": "still_life:none|A flat battery indicator flashing dark red warning bars on pure white canvas.", "tempo": "fast", "narrative_situation": "mechanism_step", "emphasis_text": "THẢM HỌA SỤT ĐƯỜNG"},
            ]),
        ]
    ),
    (
        "Đỉnh cao trào bỏ lửng (Cliffhanger Peak)",
        "A dramatic examination chamber on white background.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Tụy tạng lập tức hoảng loạn bơm một lượng khổng lồ insulin để dọn dẹp lượng đường dư thừa.", [
                {"spec": "full_scene:CH01|Cartoon pancreas firefighter furiously pumping a large red chemical pump on screen.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "TỤY HOẢNG LOẠN"},
                {"spec": "macro_prop:none|A massive wave of insulin chemical symbols sweeping away all glucose dots.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "CƠN BÃO INSULIN"},
            ]),
            ("Đúng lúc bạn nghĩ ly nước ngọt đã cứu vớt sự tỉnh táo thì cơn bão insulin ngầm đang đánh sập toàn bộ đường huyết của bạn ra sao?", [
                {"spec": "concept_metaphor:CH01|The worker stands frozen as the ground beneath gives way into a sudden open chasm.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "ĐÁNH SẬP ĐƯỜNG HUYẾT"},
                {"spec": "macro_prop:none|A giant question mark poised over an electrocardiogram flatline display.", "tempo": "fast", "narrative_situation": "cliffhanger_peak", "emphasis_text": "HẬU QUẢ LÀ GÌ?"},
            ]),
        ]
    ),
    (
        "Chuyển phễu sang bản Full và Close CTA",
        "A bright tidy morning medical desk on pure white background.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Xem video bản dài bên dưới để lấy bài test hai mươi phút nhé.", [
                {"spec": "full_scene:CH01|Doctor stickman points down enthusiastically toward the linked video preview bar.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "XEM BẢN DÀI"},
                {"spec": "visual_diagram:none|A clean directional arrow pointing down to the related full explainer thumbnail.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "BẤM DƯỚI ĐÂY"},
            ]),
            ("Lưu lại ngay để cứu vớt buổi chiều làm việc bạn nhé.", [
                {"spec": "full_scene:CH01|Doctor stickman smiles warmly holding up a clean bottle of warm water with friendly wave.", "tempo": "normal", "narrative_situation": "cta_bridge", "emphasis_text": "LƯU LẠI NGAY"},
            ]),
        ]
    ),
]
