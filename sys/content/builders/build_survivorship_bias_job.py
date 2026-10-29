#!/usr/bin/env python3
"""Build production-ready package for Survivorship Bias (16:9 Landscape Explainer — 3-4 mins).

Pillar: "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức" (tier_1_broad)
Topic: "Bẫy Người Sống Sót (Survivorship Bias) và Bản Chất Tri Thức Tiêu Cực (Via Negativa)"
Target Duration: 3 - 4 minutes (10 scenes, 40 visual beats, deep narrative arc)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[3]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content.research_story_architect import (
    CAST_APPEARANCE,
    CURRENT_STYLE_DESCRIPTION,
    DEFAULT_CHANNEL_PILLAR,
    PackagingSpec,
    ResearchedTopic,
    build_scenes_from_story_rows,
    write_production_package,
)

# ---------------------------------------------------------------------------
# STORY 16:9 (10 Scenes — 10-Part Invisible Deep Narrative Arc Landscape Explainer)
# (title, setting, tone, spoken_style, narrative_phase, rows)
# ---------------------------------------------------------------------------
STORY_16X9: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    (
        "Cú tát mở màn quán trà sữa đông khách",
        "A bustling street lined with coffee shops.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Quán cà phê đông khách đang lừa dối mắt bạn.", "full_scene:CH01|Young entrepreneur on sidewalk staring at a packed brightly lit bubble tea shop with energetic queues."),
            ("Bạn thấy người ta nườm nượp khách vào ra, tiền đếm mỏi tay mỗi tối.", "full_scene:CH02|Busy barista in clean apron rapidly prepares drinks behind a crowded wooden cafe counter."),
            ("Bạn gom hết tiền tích góp nhiều năm, vay mượn thêm ngân hàng để làm một quán y hệt.", "full_scene:CH01|Entrepreneur sits at simple wooden desk signing a bank loan document beside opened ceramic coin bank."),
            ("Nhưng không ai nói cho bạn biết, chiếc bẫy tử thần đã giương sẵn ngay trước cửa.", "concept_metaphor:none|A clean hand-drawn chalkboard showing an open steel bear trap labeled BẪY NHẬN THỨC on stark white ground."),
        ],
    ),
    (
        "Cơn sốt ảo ảnh và tiền vốn bốc hơi",
        "A dark storefront under streetlamp glare.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Chỉ sau ba tháng, tiền thuê mặt bằng và chi phí vận hành bòn rút sạch vốn liếng.", "visual_diagram:none|A clean downward bar chart in bold terracotta ink showing capital dropping steeply to zero."),
            ("Tấm biển sang nhượng gấp xuất hiện trên cửa kính, mang theo khoản nợ hàng trăm triệu đồng.", "full_scene:CH01|The young entrepreneur stands dejectedly on dark sidewalk facing a taped paper sign reading SANG QUÁN."),
            ("Nỗi đau lớn nhất không phải mất tiền, mà là cảm giác tự dằn vặt vì sao mình thất bại.", "full_scene:CH01|Entrepreneur sits alone on a single wooden stool inside the empty retail space with bowed head."),
            ("Sự thật tàn nhẫn là: bạn không hề kém cỏi, bạn chỉ vừa bị một ảo giác quang học đánh lừa.", "concept_metaphor:none|A hand-drawn pair of thick glasses projecting a shimmering golden illusion on a bare brick wall."),
        ],
    ),
    (
        "Bề nổi mạng xã hội và nghĩa địa thông tin vô hình",
        "A glowing phone screen in dark bedroom.",
        "narrative_warm",
        "ironic_exposure",
        "empirical_conflict",
        [
            ("Mỗi ngày mở mạng xã hội, bạn chỉ thấy toàn bài phỏng vấn các doanh nhân thành đạt.", "full_scene:CH01|Young person reclines in dark room, illuminated solely by glowing smartphone screen showing confident speakers."),
            ("Người ta liên tục khoe doanh thu tiền tỷ và chia sẻ các công thức làm giàu cấp tốc.", "visual_diagram:none|Smartphone screen mockup displaying bold green upward revenue graphs and glittering coin badges."),
            ("Nhưng trên đời này, tuyệt đối không có ai lập kênh mạng xã hội để kể về việc mình vừa vỡ nợ.", "concept_metaphor:none|A microphone and video camera sitting abandoned on an empty desk under cold moonlight."),
            ("Hàng nghìn người sạt nghiệp âm thầm rời đi, tạo thành một nghĩa địa thông tin vô hình.", "environment:none|A vast quiet landscape at dusk with rows of simple weathered wooden markers under a pale twilight sky."),
        ],
    ),
    (
        "Giải phẫu thiên kiến kẻ sống sót",
        "An empty auditorium with lone spotlight beam.",
        "analytical_crisp",
        "demystifying_truth",
        "structural_model",
        [
            ("Trong khoa học nhận thức, đây được gọi là Thiên kiến Kẻ Sống Sót.", "visual_diagram:none|Bold charcoal typography title card: THIÊN KIẾN KẺ SỐNG SÓT framed by a rectangular border on ivory ground."),
            ("Khi chỉ quan sát những người còn trụ lại trên sân khấu,", "full_scene:CH03|A single smiling motivational speaker standing proudly under a bright theatrical spotlight on wooden stage."),
            ("chúng ta sẽ nhầm tưởng thói quen hay sự chăm chỉ của họ là nguyên nhân thành công.", "concept_metaphor:none|A magnifying glass focusing on shiny polished shoes while ignoring the complex scaffolding supporting the stage."),
            ("Mà hoàn toàn mù tịt trước việc: hàng vạn người làm y hệt như thế đã biến mất dưới đáy sâu.", "concept_metaphor:none|A hand-drawn cross-section showing shimmering white foam on water surface above deep dark riverbed stones."),
        ],
    ),
    (
        "Bài toán máy bay ném bom năm 1943",
        "A 1943 military hangar with chalkboards.",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Năm 1943, các tướng lĩnh không quân Mỹ tìm cách giảm thiểu thiệt hại cho phi đội máy bay.", "full_scene:CH04|A military general and statistician Abraham Wald examine technical blueprints on a wooden table inside an airbase hangar."),
            ("Họ nhận thấy vết đạn bắn dày đặc ở phần cánh và thân máy bay sống sót trở về.", "visual_diagram:none|Technical blueprint of a bomber aircraft marked with dense red dots concentrated across fuselage and wings."),
            ("Giới chỉ huy quân sự lập tức ra lệnh bọc thêm các tấm thép nặng vào cánh và thân.", "full_scene:CH04|The military commander points decisively with a wooden pointer to the red-dotted wings on the hanging blueprint."),
            ("Nhưng nhà toán học Abraham Wald đã bước tới và chặn đứng quyết định tự sát đó lại.", "full_scene:CH05|Statistician Abraham Wald raises a hand calmly, holding a fountain pen with an intense analytical gaze."),
        ],
    ),
    (
        "Cú lật logic: Nhìn vào thứ vô hình",
        "A pure ivory background with clean analytical layout.",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Wald đặt ra một câu hỏi sắc bén: Những chiếc máy bay bị bắn vào buồng lái và động cơ đang ở đâu?", "visual_diagram:none|Clean split diagram showing a falling shadowed airplane smoking over ocean versus a landing plane in hangar."),
            ("Chúng đã nổ tung trên bầu trời và chìm sâu dưới đáy biển, không bao giờ có thể quay về.", "environment:none|A vast quiet open sea under twilight with gentle ripples and cold gray horizon."),
            ("Những chiếc trở về được, chính là vì chúng bị bắn vào những vị trí không gây chết người.", "visual_diagram:none|Technical diagram highlighting the non-lethal wing zones in calm sage green on clean white paper."),
            ("Nơi thực sự cần bọc giáp không phải nơi có vết đạn, mà chính là những vị trí hoàn toàn nguyên vẹn.", "macro_prop:none|Close-up of aircraft blueprint where pristine untouched cockpit and engines glow in vivid amber warning outlines."),
        ],
    ),
    (
        "Cái giá đắt của việc bắt chước kẻ thắng cuộc",
        "A minimalist studio with split comparison cards.",
        "analytical_crisp",
        "ironic_exposure",
        "empirical_conflict",
        [
            ("Hãy nhìn lại quán cà phê đông khách: bạn đang chỉ chăm chăm bắt chước các vết đạn vô hại của họ.", "concept_metaphor:CH01|Young entrepreneur paints colorful patterns on a wooden wall while foundation underneath shows deep hairline cracks."),
            ("Bạn bắt chước cách trang trí, công thức pha chế hay chiến dịch quảng cáo rầm rộ trên mạng.", "macro_prop:none|A trendy glass of milk tea with colorful toppings beside a stack of marketing discount flyers."),
            ("Nhưng bạn không biết họ sống sót là nhờ mặt bằng nhà không tốn tiền thuê, hay nguồn vốn dày chịu lỗ hai năm đầu.", "visual_diagram:none|Contrast card showing: CHI PHÍ MẶT BẰNG BẰNG KHÔNG paired with DỰ PHÒNG VỐN HAI NĂM in clean charcoal boxes."),
            ("Bắt chước kẻ sống sót mà không biết tử huyệt của kẻ thất bại, là con đường nhanh nhất dẫn đến phá sản.", "concept_metaphor:none|A stick figure blindly following glowing footprints straight toward a steep cliff edge on ivory paper."),
        ],
    ),
    (
        "Vũ khí Via Negativa: Tư duy trừ lùi",
        "A quiet minimalist wooden work desk.",
        "narrative_warm",
        "philosophical_anchor",
        "actionable_resolution",
        [
            ("Để thoát khỏi cái bẫy này, nhà đầu tư Charlie Munger dùng phương pháp: Tri Thức Tiêu Cực.", "visual_diagram:none|Bold minimalist title card: VIA NEGATIVA - TRI THỨC TIÊU CỰC drawn in disciplined charcoal ink on clean ivory paper."),
            ("Bản chất của trí tuệ thực sự không phải là làm thêm những điều vĩ đại,", "concept_metaphor:none|A pair of hands gently brushing away unnecessary golden dust to reveal a solid stone foundation."),
            ("mà là kiên quyết trừ đi những sai lầm chết người đã hạ gục người khác.", "macro_prop:CH01|Hand holds a crisp black pen crossing out red bullet points on a clean wooden clipboard checklist."),
            ("Muốn trở thành người chiến thắng, nguyên tắc số một là bạn phải sống sót qua mọi cơn bão.", "concept_metaphor:none|A sturdy small sailboat navigating safely past jagged hidden rocks under storm clouds on clean paper."),
        ],
    ),
    (
        "Bộ lọc ba tầng sinh tử trước khi ra quyết định",
        "A clean workspace with three layered glass panels.",
        "narrative_warm",
        "tactical_actionable",
        "actionable_resolution",
        [
            ("Trước khi bắt đầu bất kỳ dự án kinh doanh nào, hãy đưa nó qua ba tầng lọc sinh tử.", "visual_diagram:none|Three neat rectangular glass filter plates stacked vertically in sharp orthographic perspective on ivory field."),
            ("Tầng một: Tuyệt đối không dùng nợ vay quá khả năng chi trả khi chưa có dòng tiền thực tế.", "visual_diagram:none|First glass panel marked in red: TẦNG MỘT - KHÔNG NỢ ĐÒN BẨY QUÁ TAY with warning symbol."),
            ("Tầng hai: Luôn giữ biên độ an toàn, có quỹ dự phòng sống sót ít nhất một năm nếu dự án mất trắng.", "concept_metaphor:none|A sturdy hand-drawn suspension bridge with double steel cables and a thick safety net strung securely underneath."),
            ("Tầng ba: Nghiên cứu kỹ lưỡng các vụ sập tiệm trong ngành, để lập danh sách những việc cấm kỵ không bao giờ được chạm vào.", "macro_prop:CH01|Entrepreneur reviews a detailed notebook labeled HỒ SƠ TỬ HUYỆT with crisp red struck-through bullet lines."),
        ],
    ),
    (
        "Khép lại vòng lặp và làm chủ cuộc chơi",
        "A peaceful street corner in early morning light.",
        "narrative_warm",
        "philosophical_anchor",
        "actionable_resolution",
        [
            ("Người khôn ngoan không tìm kiếm bí quyết trên đỉnh vinh quang của kẻ thắng cuộc.", "environment:none|A calm street corner at dawn, soft morning sunlight filtering through tree leaves onto clean asphalt sidewalks."),
            ("Họ cúi xuống quan sát những vết tích đổ vỡ dưới đáy vực sâu để không bao giờ bước chân vào đó.", "full_scene:CH01|Young entrepreneur walks calmly past quiet storefronts with hands relaxed in pockets and steady forward gaze."),
            ("Khi bạn loại bỏ được tất cả những nguyên nhân dẫn đến thất bại, thành công sẽ là hệ quả tự nhiên.", "full_scene:CH01|Entrepreneur pauses on street corner, looking ahead with a calm, discerning smile in golden morning light."),
            ("Lần tới khi đứng trước một cơ hội làm giàu hào nhoáng, hãy tự hỏi: Đâu là những câu chuyện đổ vỡ chưa từng được cất lời?", "concept_metaphor:none|A single clean magnifying glass on open white sketchpad, revealing faint intricate geometric contours below the surface."),
        ],
    ),
]


def build_sources() -> list[dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "A Method of Estimating Plane Vulnerability Based on Damage of Returning Aircraft",
            "reference": "Abraham Wald (1943). Statistical Research Group, Columbia University. CRC 432.",
            "facts": [
                "Máy bay bị bắn vào động cơ đã không thể quay về căn cứ.",
                "Cần bọc giáp vào vị trí máy bay không có lỗ đạn.",
                "Thống kê chỉ ghi nhận dữ liệu từ những máy bay sống sót.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Fooled by Randomness: The Hidden Role of Chance in Life and in the Markets",
            "reference": "Nassim Nicholas Taleb (2001). Random House. ISBN: 978-0812975215.",
            "facts": [
                "Nghĩa địa vô hình của người thất bại bị lãng quên.",
                "Tri thức tiêu cực tập trung vào việc loại bỏ sai lầm.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Poor Charlie's Almanack: The Wit and Wisdom of Charles T. Munger",
            "reference": "Peter D. Kaufman (2005). Donning Company Publishers. ISBN: 978-1578643035.",
            "facts": [
                "Nguyên lý nghịch đảo giúp tránh xa những cái chết ngu ngốc.",
                "Biên độ an toàn bảo vệ con người trước biến cố bất ngờ.",
            ],
        },
    ]


def build_characters() -> list[dict[str, Any]]:
    return [
        {
            "id": "CH01",
            "name": "Nhân vật người trẻ khởi nghiệp",
            "role": "young_entrepreneur",
            "appearance": CAST_APPEARANCE,
            "outfit": "Simple charcoal-rimmed round glasses, earthy slate blue crewneck sweater with comfortable turned-up sleeves.",
        },
        {
            "id": "CH02",
            "name": "Nhân viên pha chế cà phê",
            "role": "busy_barista",
            "appearance": CAST_APPEARANCE,
            "outfit": "Muted terracotta apron over clean ivory shirt, energetic posture behind wooden cafe counter.",
        },
        {
            "id": "CH03",
            "name": "Diễn giả truyền cảm hứng",
            "role": "charismatic_speaker",
            "appearance": CAST_APPEARANCE,
            "outfit": "Sharp charcoal blazer over crisp white shirt, confident stance under theatrical stage lighting.",
        },
        {
            "id": "CH04",
            "name": "Tướng lĩnh không quân Mỹ",
            "role": "military_general",
            "appearance": CAST_APPEARANCE,
            "outfit": "Classic olive drab military uniform with shoulder badges and authoritative posture.",
        },
        {
            "id": "CH05",
            "name": "Nhà toán học Abraham Wald",
            "role": "statistician_abraham_wald",
            "appearance": CAST_APPEARANCE,
            "outfit": "Vintage 1940s tweed vest over white collared shirt, holding fountain pen with deep thoughtful expression.",
        },
    ]


def build_topic_16x9() -> ResearchedTopic:
    story_tuples = [(title, setting, rows) for title, setting, _, _, _, rows in STORY_16X9]
    scenes = build_scenes_from_story_rows(story_tuples, character_id="CH01")
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = STORY_16X9[i][2]
        sc.spoken_style = STORY_16X9[i][3]
        sc.narrative_phase = STORY_16X9[i][4]

    # Assign source claims for validation
    scenes[2].source_ids = ["SRC02"]
    scenes[2].claim_facts = [
        ("Hàng nghìn người sạt nghiệp âm thầm rời đi, tạo thành một nghĩa địa thông tin vô hình.", "SRC02", "Nghĩa địa vô hình của người thất bại bị lãng quên."),
    ]
    scenes[4].source_ids = ["SRC01"]
    scenes[4].claim_facts = [
        ("Năm 1943, các tướng lĩnh không quân Mỹ tìm cách giảm thiểu thiệt hại cho phi đội máy bay.", "SRC01", "Thống kê chỉ ghi nhận dữ liệu từ những máy bay sống sót."),
        ("Nhưng nhà toán học Abraham Wald đã bước tới và chặn đứng quyết định tự sát đó lại.", "SRC01", "Cần bọc giáp vào vị trí máy bay không có lỗ đạn."),
    ]
    scenes[5].source_ids = ["SRC01"]
    scenes[5].claim_facts = [
        ("Wald đặt ra một câu hỏi sắc bén: Những chiếc máy bay bị bắn vào buồng lái và động cơ đang ở đâu?", "SRC01", "Máy bay bị bắn vào động cơ đã không thể quay về căn cứ."),
        ("Nơi thực sự cần bọc giáp không phải nơi có vết đạn, mà chính là những vị trí hoàn toàn nguyên vẹn.", "SRC01", "Cần bọc giáp vào vị trí máy bay không có lỗ đạn."),
    ]
    scenes[7].source_ids = ["SRC02", "SRC03"]
    scenes[7].claim_facts = [
        ("Để thoát khỏi cái bẫy này, nhà đầu tư Charlie Munger dùng phương pháp: Tri Thức Tiêu Cực.", "SRC02", "Tri thức tiêu cực tập trung vào việc loại bỏ sai lầm."),
    ]
    scenes[8].source_ids = ["SRC03"]
    scenes[8].claim_facts = [
        ("Tầng hai: Luôn giữ biên độ an toàn, có quỹ dự phòng sống sót ít nhất một năm nếu dự án mất trắng.", "SRC03", "Biên độ an toàn bảo vệ con người trước biến cố bất ngờ."),
    ]

    return ResearchedTopic(
        topic="Bẫy Người Sống Sót (Survivorship Bias) và Bản Chất Tri Thức Tiêu Cực (Via Negativa)",
        audience="Người trẻ khởi nghiệp, người đi làm, nhà đầu tư cá nhân và những ai quan tâm đến phương pháp luận tư duy phản biện",
        goal="Giải mã ảo giác sao chép người thành công qua bài toán máy bay ném bom Abraham Wald và trao công cụ bộ lọc 3 tầng Via Negativa",
        video_type="research_explainer",
        min_duration=180.0,
        max_duration=240.0,
        style=CURRENT_STYLE_DESCRIPTION,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        sources=build_sources(),
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _, _, _, _) in enumerate(STORY_16X9, 1)],
        characters=build_characters(),
        scenes=scenes,
        tone="Conversational Essayist điềm đạm, sắc sảo, phản trực giác, giải phẫu bản chất nhận thức",
        language="vi",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        packaging=PackagingSpec(
            youtube_title="Bẫy Người Sống Sót: Sao Chép Thành Công Là Vô Nghĩa",
            visual_hook="Nhân vật người que đứng trước tấm biển SANG QUÁN trong khi xa xa một quán đông khách sáng đèn",
            text_overlay="BẮT CHƯỚC SAI LẦM",
            contrast_pair="Bề nổi hào nhoáng người sống sót vs. Nghĩa địa vô hình kẻ thất bại",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "bẫy người sống sót",
                "survivorship bias",
                "tri thức tiêu cực",
                "via negativa",
                "abraham wald máy bay",
                "bộ lọc 3 tầng ra quyết định",
                "tư duy phản biện",
                "bài học khởi nghiệp",
                "charlie munger inversion",
            ],
        ),
        human_editorial={
            "editorial_stance": "Thành công không đến từ việc bắt chước thói quen của người thắng cuộc, mà đến từ việc nhận diện và tránh xa những tử huyệt chết người.",
            "topic_dilemmas": [
                "Mâu thuẫn giữa việc nhìn thấy quán xá đông khách tưởng dễ ăn và thực tế 90% cơ sở kinh doanh đóng cửa trong âm thầm.",
                "Bề nổi hào nhoáng trên mạng xã hội khiến con người khao khát đi đường tắt và học theo các công thức làm giàu vô căn cứ.",
            ],
            "author_raw_input": "Tình huống thực tế tại Việt Nam: mở quán cà phê, trà sữa theo trào lưu, vay vốn làm theo rồi sang quán sau vài tháng vì chỉ thấy bề nổi hào nhoáng và muốn đi đường tắt. Giải pháp: tri thức tiêu cực Via Negativa gồm bộ lọc 3 tầng sinh tử (không nợ đòn bẩy quá tay, giữ biên độ an toàn 1 năm, nghiên cứu tử huyệt phá sản).",
            "dynamic_questions": [
                "Dấu hiệu rõ nhất của việc một người đang sao chép bề nổi của kẻ sống sót là gì?",
                "Làm thế nào để phân biệt giữa việc học hỏi kỹ năng thực tế với việc sập bẫy ảo giác thành công?",
            ],
            "expanded_content_ideas": [
                {
                    "angle_type": "analysis",
                    "idea_summary": "Phân tích cơ chế nghĩa địa vô hình: người thất bại không có tiếng nói trên mạng xã hội, dẫn đến việc dữ liệu thu nhận bị méo mó 100%.",
                    "narrative_integration": "Triển khai ở Scene 02, 03 và 07 bóc tách thực tế mở quán cà phê và so sánh vết đạn vô hại.",
                },
                {
                    "angle_type": "evaluation",
                    "idea_summary": "Ứng dụng Via Negativa: Bộ lọc 3 tầng sinh tử gồm cắt nợ đòn bẩy, biên độ an toàn 12 tháng, và nghiên cứu hồ sơ tử huyệt.",
                    "narrative_integration": "Triển khai ở Scene 08, 09 và 10 đúc kết bài học thực hành cụ thể mang lại lợi ích thiết thực.",
                },
            ],
        },
    )


def count_total_beats(scenes: list[Any]) -> int:
    return sum(len(sc.visual_beats) for sc in scenes)


def export_package(topic: ResearchedTopic, out_dir: Path) -> dict[str, Any]:
    result = write_production_package(out_dir, topic)
    draft_dir = out_dir / "draft"
    draft_dir.mkdir(parents=True, exist_ok=True)
    outline_data = {
        "outline": [
            {
                "scene_id": sc.scene_id,
                "purpose": sc.purpose,
                "requirements": list(sc.requirements),
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            }
            for sc in topic.scenes
        ]
    }
    (draft_dir / "outline.json").write_text(
        __import__("json").dumps(outline_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    content_text = (out_dir / "content.json").read_text(encoding="utf-8")
    (draft_dir / "content.json").write_text(content_text, encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Build survivorship bias explainer package.")
    parser.add_argument("--job-id", default="survivorship-bias-16x9", help="Job identifier")
    args = parser.parse_args()

    topic = build_topic_16x9()
    output_dir = SYS_DIR / "runs" / args.job_id
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[*] Đang xây dựng hồ sơ kỹ thuật cho: {args.job_id} (16:9)...")
    print(f"    - Số phân cảnh: {len(topic.scenes)}")
    print(f"    - Tổng visual beats: {count_total_beats(topic.scenes)}")

    res = export_package(topic, output_dir)
    print(f"✅ Đã tạo thành công hồ sơ sản xuất tại {output_dir}")
    print(f"   Brief:   {res['brief_file']}")
    print(f"   Content: {res['content_file']}")


if __name__ == "__main__":
    main()
