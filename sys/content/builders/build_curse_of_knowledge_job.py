#!/usr/bin/env python3
"""Build production-ready packages for Curse of Knowledge (16:9 Landscape & 9:16 Portrait).

Pillar: "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức" (tier_1_broad)
Topic: "Lời Nguyền Hiểu Biết (The Curse of Knowledge): Vì Sao Càng Giỏi Càng Khó Dạy?"
Format:
  - curse-of-knowledge-16x9: 8 scenes, 32 visual beats, 8-part narrative arc landscape explainer
  - curse-of-knowledge-9x16: 5 scenes, 20 visual beats, vertical mobile short explainer
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List

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
    ResearchedScene,
    ResearchedTopic,
    build_scenes_from_story_rows,
    write_production_package,
)

# ---------------------------------------------------------------------------
# STORY 16:9 (8 Scenes — 8-Part Invisible Narrative Arc Landscape Explainer)
# (title, setting, tone, spoken_style, narrative_phase, rows)
# ---------------------------------------------------------------------------
STORY_16X9: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    (
        "Cú tát mở màn bàn họp",
        "A meeting room with a wooden discussion table.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Bạn hiểu rất rõ, nhưng nói chẳng ai hiểu.", "full_scene:CH01|Researcher stands animatedly beside whiteboard, gesturing with open hands while peer looks completely bewildered."),
            ("Càng cố giải thích cặn kẽ, người đối diện càng ngơ ngác.", "concept_metaphor:CH02|Close-up of coworker scratching head as miniature dense paragraphs of text float overhead like a dizzying swarm."),
            ("Bạn bực bội nghĩ rằng họ không chịu tập trung.", "full_scene:CH01|Researcher crosses arms with a slight frown of mild exasperation beside the glowing desk lamp."),
            ("Nhưng sự thật là, chính bộ não bạn đang lừa dối bạn.", "concept_metaphor:none|A clean hand-drawn diagram showing a human head silhouette with an intricate glowing maze inside locked behind frosted glass."),
        ],
    ),
    (
        "Ảo tưởng truyền đạt ý nghĩ",
        "A pure ivory background with clean lighting.",
        "analytical_crisp",
        "demystifying_truth",
        "empirical_conflict",
        [
            ("Chúng ta thường tin vào một ảo tưởng ngây thơ.", "visual_diagram:none|Two stick figures standing on opposite sides of a vast white space, separated by a wide chasm."),
            ("Rằng suy nghĩ trong đầu mình có thể truyền sang đầu người khác như một tập tin kỹ thuật số.", "concept_metaphor:none|A tiny cartoon digital file icon labeled Ý NGHĨ floating across the void, disintegrating into scattered dust midway."),
            ("Thế nhưng kiến thức một khi đã lọt vào não bộ,", "full_scene:CH01|Researcher holds a glowing golden key of insight in the palm of hand with gentle reverence."),
            ("nó lập tức bị khóa chặt bởi một lớp mã hóa vô hình.", "visual_diagram:none|The golden key transforms into a heavy charcoal padlock snapping shut around an abstract thought bubble."),
        ],
    ),
    (
        "Thí nghiệm gõ nhịp kinh điển Stanford",
        "A 1990 university psychology laboratory.",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Năm 1990, nhà tâm lý học Elizabeth Newton làm một thí nghiệm giản dị tại Đại học Stanford.", "full_scene:CH03|Professor Elizabeth Newton stands calmly in university lecture hall, taking notes on a wooden clipboard."),
            ("Bà chia các sinh viên thành hai nhóm: người gõ nhịp và người lắng nghe.", "visual_diagram:none|Clean table diagram dividing students into two columns: NGƯỜI GÕ NHỊP (Tappers) and NGƯỜI LẮNG NGHE (Listeners)."),
            ("Người gõ được yêu cầu dùng ngón tay gõ nhịp các bài hát nổi tiếng xuống mặt bàn gỗ.", "macro_prop:CH01|Close-up of four-finger hand rhythmically tapping the warm grain of a sturdy wooden tabletop with energetic motion lines."),
            ("Nhiệm vụ của người nghe là đoán xem đó là bài hát gì.", "full_scene:CH02|The listener leans forward with intense focus, cupping one ear toward the wooden desk."),
        ],
    ),
    (
        "Bàng hoàng khoảng cách năm mươi phần trăm và hai phẩy năm",
        "A pure ivory background with clean analytical layout.",
        "analytical_crisp",
        "ironic_exposure",
        "empirical_conflict",
        [
            ("Trước khi gõ, những người gõ tự tin đoán đối phương sẽ đoán đúng năm mươi phần trăm.", "visual_diagram:none|A proud hand-drawn prediction gauge pointing optimistically to 50% in warm terracotta ink."),
            ("Nhưng kết quả thực tế khiến cả khán phòng bàng hoàng.", "full_scene:CH03|The researcher looks down at the actual test score sheet in quiet disbelief."),
            ("Trong một trăm hai mươi bài hát, người nghe chỉ đoán trúng đúng ba bài.", "visual_diagram:none|Clean grid of 120 tiny paper note icons, where exactly 3 glow warm gold and 117 remain muted charcoal gray."),
            ("Tỷ lệ thành công vỏn vẹn hai phẩy năm phần trăm.", "visual_diagram:none|Bold contrast typography card: 50% DỰ ĐOÁN versus 2.5% THỰC TẾ on clean background."),
        ],
    ),
    (
        "Dàn nhạc trong đầu và tiếng cộc khô khốc",
        "A dual split acoustic contrast space.",
        "narrative_warm",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Khoảng cách kinh khủng đó đến từ đâu?", "concept_metaphor:none|A massive interrogation mark drawn in deep charcoal ink hovering over the wooden study desk."),
            ("Khi bạn gõ, trong đầu bạn đang vang lên cả một dàn nhạc giao hưởng hoàn chỉnh.", "concept_metaphor:CH01|The tapper smiles as floating miniature violinists, flutes, and brass instruments swirl in harmony around head."),
            ("Bạn nghe rõ từng ca từ, từng nốt nhạc luyến láy.", "macro_prop:CH01|Hand taps table while golden sheet music ribbons flow out seamlessly into the air."),
            ("Nhưng người đối diện chỉ nghe thấy những tiếng cộc cộc khô khốc và rời rạc.", "full_scene:CH02|The listener stares in complete bafflement as only three blunt charcoal Morse-like dots land on the table surface."),
        ],
    ),
    (
        "Lời nguyền hiểu biết và bi kịch chuyên môn",
        "A modern office with cluttered bookshelves.",
        "analytical_crisp",
        "systemic_friction",
        "lived_friction",
        [
            ("Đây chính là Lời nguyền Hiểu biết.", "visual_diagram:none|Bold diagnostic title card: LỜI NGUYỀN HIỂU BIẾT framed by a crisp rectangular charcoal border."),
            ("Một khi đã biết, bạn hoàn toàn bất lực trong việc hình dung trạng thái chưa biết của người khác.", "concept_metaphor:CH01|Researcher stands behind a one-way mirror, unable to perceive the shadowy confusion on the other side."),
            ("Càng trở thành chuyên gia, bạn càng nói bằng thứ ngôn ngữ trừu tượng.", "macro_prop:none|A heavy leather-bound dictionary floating mid-air, with complex jargon acronyms tumbling from its pages."),
            ("Và nhầm tưởng sự trừu tượng đó là điều hiển nhiên mà ai cũng phải hiểu.", "full_scene:CH01|Researcher shrugs casually while audience in background clutches their heads in cognitive overload."),
        ],
    ),
    (
        "Kỹ thuật neo cụ thể của Richard Feynman",
        "A sunny morning study table with simple tools.",
        "narrative_warm",
        "tactical_actionable",
        "actionable_resolution",
        [
            ("Để phá vỡ lời nguyền này, đừng cố giải thích to hơn hay dài dòng hơn.", "concept_metaphor:none|A loudspeaker crossed out with a bold charcoal diagonal line on clean white paper."),
            ("Hãy dùng kỹ thuật neo cụ thể của Richard Feynman.", "full_scene:CH04|A cheerful senior mentor in simple collared shirt holds a shiny brass physical compass on wooden table."),
            ("Dịch chuyển mọi khái niệm trừu tượng về một đồ vật cầm nắm được trong đời thực.", "macro_prop:none|An ethereal floating mathematical equation transforming upon touching a desk into a solid wooden building block."),
            ("Nếu không thể giải thích cho một đứa trẻ lớp năm hiểu, nghĩa là chính bạn cũng chưa thực sự hiểu.", "full_scene:CH04|The mentor squats down at eye level, explaining a simple wooden gears toy to an attentive young student."),
        ],
    ),
    (
        "Thấu cảm nhận thức và lắng nghe tiếng gõ",
        "A peaceful room bathed in warm afternoon sunlight.",
        "narrative_warm",
        "philosophical_anchor",
        "actionable_resolution",
        [
            ("Giao tiếp xuất sắc không phải là phô diễn bạn biết nhiều đến đâu.", "concept_metaphor:none|A towering pedestal of heavy textbooks fading into gentle transparency in warm sunlight."),
            ("Mà là lòng can đảm dám bước ra khỏi dàn nhạc trong đầu mình,", "full_scene:CH01|Researcher steps down from platform and sits directly opposite the peer at the wooden table."),
            ("để lắng nghe những tiếng gõ cộc cộc đơn độc của người đối diện.", "macro_prop:CH02|Coworker taps table gently with curious fingertips, met by researcher's patient attentive smile."),
            ("Bởi vì thấu cảm nhận thức, luôn có sức mạnh hơn ngàn lời giảng giải.", "full_scene:CH01|Both characters share a warm understanding laugh over open notebooks under golden afternoon light."),
        ],
    ),
]

# ---------------------------------------------------------------------------
# STORY 9:16 (5 Scenes — Mobile Standalone Explainer 45-60s)
# ---------------------------------------------------------------------------
STORY_9X16: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    (
        "Cú tát mở màn bàn trà",
        "A meeting room with a wooden discussion table.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Bạn hiểu rất rõ, nhưng nói chẳng ai hiểu.", "full_scene:CH01|Researcher stands animatedly beside whiteboard, gesturing with open hands while peer looks completely bewildered."),
            ("Càng cố giải thích cặn kẽ, người đối diện càng ngơ ngác.", "concept_metaphor:CH02|Close-up of coworker scratching head as miniature dense paragraphs of text float overhead."),
            ("Bạn bực bội nghĩ rằng họ không chịu tập trung.", "full_scene:CH01|Researcher crosses arms with mild exasperation beside the glowing desk lamp."),
            ("Nhưng chính bộ não bạn đang lừa dối bạn.", "concept_metaphor:none|A clean hand-drawn diagram showing a human head silhouette with a locked glowing maze inside."),
        ],
    ),
    (
        "Thực nghiệm gõ nhịp Stanford",
        "A 1990 university psychology laboratory.",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Năm 1990, Đại học Stanford làm một thí nghiệm lạ.", "full_scene:CH03|Professor Elizabeth Newton stands calmly in university lecture hall with wooden clipboard."),
            ("Họ cho người tham gia gõ nhịp các bài hát nổi tiếng xuống bàn.", "macro_prop:CH01|Close-up of four-finger hand rhythmically tapping the wooden tabletop with energetic motion lines."),
            ("Người gõ tin chắc năm mươi phần trăm người nghe sẽ đoán trúng.", "visual_diagram:none|Hand-drawn prediction gauge pointing to 50% in warm terracotta ink."),
            ("Nhưng thực tế, tỷ lệ đoán đúng chỉ là hai phẩy năm phần trăm.", "visual_diagram:none|Bold contrast typography card: 50% DỰ ĐOÁN versus 2.5% THỰC TẾ on clean background."),
        ],
    ),
    (
        "Dàn nhạc trong đầu",
        "A dual split acoustic contrast space.",
        "narrative_warm",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Khoa học gọi đây là Lời nguyền Hiểu biết.", "full_scene:CH01|Researcher taps forehead thoughtfully beside the wooden desk under warm lamplight."),
            ("Khi bạn gõ, trong đầu bạn đang vang lên cả dàn nhạc giao hưởng.", "concept_metaphor:CH01|The tapper smiles as floating miniature musical instruments swirl in harmony around head."),
            ("Bạn nghe rõ từng ca từ và giai điệu.", "concept_metaphor:none|A golden flowing ribbon of hand-drawn sheet music with musical notes wafts through clean white air."),
            ("Nhưng người nghe chỉ nghe thấy tiếng cộc cộc khô khốc vô nghĩa.", "full_scene:CH02|The listener stares in bafflement as only three blunt charcoal Morse-like dots land on the table."),
        ],
    ),
    (
        "Bẫy chuyên gia trừu tượng",
        "A modern office with cluttered bookshelves.",
        "analytical_crisp",
        "systemic_friction",
        "lived_friction",
        [
            ("Một khi đã biết, bạn không thể nhớ cảm giác khi chưa biết.", "concept_metaphor:CH01|Researcher stands behind a one-way mirror, unable to perceive the confusion on the other side."),
            ("Càng giỏi, bạn càng lạm dụng từ ngữ chuyên môn trừu tượng.", "macro_prop:none|A heavy leather-bound dictionary floating mid-air with jargon acronyms tumbling from pages."),
            ("Người nghe không dốt, họ chỉ chưa có bản nhạc trong đầu như bạn.", "full_scene:CH02|Coworker holds up hands with a polite helpless smile in front of the whiteboard."),
            ("Giải thích nhiều hơn chỉ làm họ thêm quá tải.", "visual_diagram:none|A stick figure head bowing down under a heavy pile of falling text bricks."),
        ],
    ),
    (
        "Vũ khí neo cụ thể Feynman",
        "A sunny morning study table with simple tools.",
        "narrative_warm",
        "tactical_actionable",
        "actionable_resolution",
        [
            ("Để thoát khỏi lời nguyền, hãy dùng kỹ thuật neo cụ thể.", "concept_metaphor:none|A shiny brass physical compass resting firmly on wooden table ground."),
            ("Kéo mọi ý niệm trừu tượng về một vật thể cầm nắm được.", "macro_prop:none|An abstract formula transforming into a tangible solid wooden block."),
            ("Giải thích sao cho một đứa trẻ mười tuổi cũng có thể hiểu.", "full_scene:CH04|Mentor explains a simple wooden gear toy to an attentive young student with warm smiles."),
            ("Bởi vì giao tiếp giỏi, là dũng cảm quên đi những gì mình biết.", "full_scene:CH01|Both characters share a warm understanding laugh over open notebooks under golden afternoon light."),
        ],
    ),
]


def build_sources() -> list[dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "Overconfidence in the Communication of Intent: Heard Melodies Are Sweet, but Those Unheard Are Sweeter",
            "reference": "Elizabeth L. Newton (1990). Doctoral Dissertation, Stanford University.",
            "facts": [
                "Người gõ đoán người nghe hiểu được năm mươi phần trăm.",
                "Người nghe chỉ đoán trúng ba trên một trăm hai mươi bài hát.",
                "Người gõ nghe thấy toàn bộ giai điệu trong đầu nên đoán quá cao.",
            ],
        },
        {
            "id": "SRC02",
            "title": "The Curse of Knowledge in Economic Settings: An Experimental Analysis",
            "reference": "Colin F. Camerer, George Loewenstein, & Martin Weber (1989). Journal of Political Economy, 97(5), 1232-1254.",
            "facts": [
                "Người có thông tin không thể bỏ qua thông tin khi dự đoán người khác.",
                "Lời nguyền hiểu biết tạo tổn thất giao tiếp trong tổ chức và dạy học.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Made to Stick: Why Some Ideas Survive and Others Die",
            "reference": "Chip Heath & Dan Heath (2007). Random House. ISBN: 978-1400064281.",
            "facts": [
                "Lời nguyền hiểu biết là rào cản khiến chuyên gia khó truyền đạt.",
                "Kỹ thuật neo cụ thể là vũ khí hiệu quả nhất để hóa giải sự trừu tượng.",
            ],
        },
    ]


def build_characters() -> list[dict[str, Any]]:
    return [
        {
            "id": "CH01",
            "name": "Nhân vật chuyên gia nghiên cứu",
            "role": "academic_expert",
            "appearance": CAST_APPEARANCE,
            "outfit": "Simple charcoal-rimmed round glasses, earthy olive crewneck sweater with comfortable turned-up sleeves.",
        },
        {
            "id": "CH02",
            "name": "Nhân vật đồng nghiệp người nghe",
            "role": "curious_peer",
            "appearance": CAST_APPEARANCE,
            "outfit": "Warm oatmeal-toned casual button-up shirt, natural posture of attentive desk work.",
        },
        {
            "id": "CH03",
            "name": "Giáo sư Elizabeth Newton",
            "role": "stanford_researcher",
            "appearance": CAST_APPEARANCE,
            "outfit": "Formal charcoal tailored vest over ivory blouse with academic notebook and pencil.",
        },
        {
            "id": "CH04",
            "name": "Người thầy thông thái Feynman",
            "role": "wise_mentor",
            "appearance": CAST_APPEARANCE,
            "outfit": "Relaxed vintage linen shirt with open collar and warm grandfatherly smile.",
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
    scenes[2].source_ids = ["SRC01"]
    scenes[2].claim_facts = [
        ("Năm 1990, nhà tâm lý học Elizabeth Newton làm một thí nghiệm giản dị tại Đại học Stanford.", "SRC01", "Người gõ đoán người nghe hiểu được năm mươi phần trăm."),
    ]
    scenes[3].source_ids = ["SRC01"]
    scenes[3].claim_facts = [
        ("Trong một trăm hai mươi bài hát, người nghe chỉ đoán trúng đúng ba bài.", "SRC01", "Người nghe chỉ đoán trúng ba trên một trăm hai mươi bài hát."),
        ("Tỷ lệ thành công vỏn vẹn hai phẩy năm phần trăm.", "SRC01", "Người nghe chỉ đoán trúng ba trên một trăm hai mươi bài hát."),
    ]
    scenes[5].source_ids = ["SRC02", "SRC03"]
    scenes[5].claim_facts = [
        ("Một khi đã biết, bạn hoàn toàn bất lực trong việc hình dung trạng thái chưa biết của người khác.", "SRC02", "Người có thông tin không thể bỏ qua thông tin khi dự đoán người khác."),
    ]
    scenes[6].source_ids = ["SRC03"]
    scenes[6].claim_facts = [
        ("Dịch chuyển mọi khái niệm trừu tượng về một đồ vật cầm nắm được trong đời thực.", "SRC03", "Kỹ thuật neo cụ thể là vũ khí hiệu quả nhất để hóa giải sự trừu tượng."),
    ]

    return ResearchedTopic(
        topic="Lời Nguyền Hiểu Biết (The Curse of Knowledge): Vì Sao Càng Giỏi Càng Khó Dạy?",
        audience="Người đi làm, quản lý, thầy cô giáo, kỹ sư và những ai thường xuyên gặp bế tắc khi giải thích kiến thức",
        goal="Bóc tách cơ chế tâm lý khiến chuyên gia mất khả năng thấu cảm nhận thức và trao công cụ neo cụ thể của Feynman",
        video_type="research_explainer",
        min_duration=180.0,
        max_duration=360.0,
        style=CURRENT_STYLE_DESCRIPTION,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        sources=build_sources(),
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _, _, _, _) in enumerate(STORY_16X9, 1)],
        characters=build_characters(),
        scenes=scenes,
        tone="Conversational Essayist điềm đạm, sắc sảo, phản trực giác, giải mã cơ chế tâm lý giao tiếp",
        language="vi",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        packaging=PackagingSpec(
            youtube_title="Vì Sao Càng Giỏi Càng Khó Dạy?",
            visual_hook="Nhân vật người que gõ nhịp ngón tay xuống bàn gỗ với dàn nhạc tưởng tượng trong đầu đối lập tiếng cộc khô khốc",
            text_overlay="LỜI NGUYỀN BIẾT RỒI",
            contrast_pair="Dàn nhạc giao hưởng trong đầu vs. Tiếng cộc khô khốc trên bàn",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "lời nguyền hiểu biết",
                "curse of knowledge",
                "vì sao càng giỏi càng khó dạy",
                "giao tiếp hiệu quả",
                "thí nghiệm gõ nhịp stanford",
                "elizabeth newton",
                "phương pháp feynman",
                "mô hình tư duy",
                "tâm lý học nhận thức",
            ],
        ),
    )


def build_topic_9x16() -> ResearchedTopic:
    story_tuples = [(title, setting, rows) for title, setting, _, _, _, rows in STORY_9X16]
    scenes = build_scenes_from_story_rows(story_tuples, character_id="CH01")
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = STORY_9X16[i][2]
        sc.spoken_style = STORY_9X16[i][3]
        sc.narrative_phase = STORY_9X16[i][4]

    scenes[1].source_ids = ["SRC01"]
    scenes[1].claim_facts = [
        ("Nhưng thực tế, tỷ lệ đoán đúng chỉ là hai phẩy năm phần trăm.", "SRC01", "Người nghe chỉ đoán trúng ba trên một trăm hai mươi bài hát."),
    ]
    scenes[3].source_ids = ["SRC02", "SRC03"]
    scenes[3].claim_facts = [
        ("Một khi đã biết, bạn không thể nhớ cảm giác khi chưa biết.", "SRC02", "Người có thông tin không thể bỏ qua thông tin khi dự đoán người khác."),
    ]

    return ResearchedTopic(
        topic="Lời Nguyền Hiểu Biết: Thí Nghiệm Gõ Nhịp Stanford (Shorts 9:16)",
        audience="Người xem video ngắn trên di động thích khám phá tâm lý học hành vi và giao tiếp",
        goal="Giải thích ngắn gọn 60 giây vì sao người giỏi giải thích dở bằng thí nghiệm gõ nhịp kinh điển",
        video_type="research_explainer",
        min_duration=45.0,
        max_duration=60.0,
        style=CURRENT_STYLE_DESCRIPTION,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=build_sources(),
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _, _, _, _) in enumerate(STORY_9X16, 1)],
        characters=build_characters(),
        scenes=scenes,
        tone="Conversational Essayist gãy gọn, bất ngờ, nhịp điệu nhanh và cuốn hút",
        language="vi",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        packaging=PackagingSpec(
            youtube_title="Vì Sao Người Thông Minh Nói Chẳng Ai Hiểu?",
            visual_hook="Bàn tay gõ nhịp xuống bàn gỗ đối lập tỷ lệ 50% và 2.5%",
            text_overlay="LỜI NGUYỀN BIẾT RỒI",
            contrast_pair="50% Kỳ vọng vs. 2.5% Thực tế",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "lời nguyền hiểu biết",
                "curse of knowledge",
                "thí nghiệm gõ nhịp",
                "tâm lý học ngắn",
                "kỹ năng giao tiếp",
            ],
        ),
    )


def count_total_beats(scenes: List[ResearchedScene]) -> int:
    return sum(len(sc.visual_beats) for sc in scenes)


def export_package(topic: ResearchedTopic, out_dir: Path) -> dict:
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
    (draft_dir / "outline.json").write_text(json.dumps(outline_data, ensure_ascii=False, indent=2), encoding="utf-8")
    content_text = (out_dir / "content.json").read_text(encoding="utf-8")
    (draft_dir / "content.json").write_text(content_text, encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description="Build Curse of Knowledge 16:9 & 9:16 production blueprint.")
    parser.add_argument("--ratio", choices=["16:9", "9:16", "dual"], default="dual", help="Aspect ratio to build")
    parser.add_argument("--out-dir", type=Path, default=SYS_DIR / "runs", help="Output directory root")
    args = parser.parse_args()

    ratios = ["16:9", "9:16"] if args.ratio == "dual" else [args.ratio]

    for r in ratios:
        if r == "16:9":
            topic = build_topic_16x9()
            job_name = "curse-of-knowledge-16x9"
        else:
            topic = build_topic_9x16()
            job_name = "curse-of-knowledge-9x16"

        target_dir = args.out_dir / job_name
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n[*] Đang xây dựng hồ sơ kỹ thuật cho: {job_name} ({r})...")
        print(f"    - Số phân cảnh: {len(topic.scenes)}")
        print(f"    - Tổng visual beats: {count_total_beats(topic.scenes)}")

        res = export_package(topic, target_dir)
        print(f"  [+] Đã xuất brief.json: {res['brief_file']}")
        print(f"  [+] Đã xuất content.json: {res['content_file']}")
        print(f"  [+] Đã xuất script.json: {res['script_file']}")
        print(f"  [+] Đã xuất cadence_file: {res['cadence_file']}")
        print(f"  [+] Brief SHA256: {res['brief_hash']}")
        print(f"  [+] Hợp đồng Schema 3.0: {'HỢP LỆ' if res['valid_contracts'] else 'LỖI'}")
        print(f"  [PASS] Đóng gói thành công tại {target_dir}")


if __name__ == "__main__":
    main()
