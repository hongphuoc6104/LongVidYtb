#!/usr/bin/env python3
"""Automated production bundle builder for channel 'co_the_ke' (Cơ Thể Kể).

Channel Niche: Sức khỏe và cơ thể được nhân hóa.
Persona: Các cơ quan nội tạng biết nói (Tim, Dạ Dày, Gan, Não, và Host).
Visual: Clean 2D kawaii medical-explainer (profile 'ch_organ_buddies').

Builds Schema 3.0 bundles for:
  - TikTok Short (short_9x16, <= 6 Flow images, 30-45s)
  - YouTube Long (long_16x9, 8 scenes, 24 visual beats, with 3 standalone spinoff_shorts)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parents[3]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content.research_story_architect import (  # noqa: E402
    PackagingSpec,
    ResearchedTopic,
    build_scenes_from_story_rows,
    validate_production_bundle,
    write_production_package,
)
from tools.script_cadence_checker import ScriptCadenceChecker  # noqa: E402
from tools.script_hook_scorer import HookScore, score_script  # noqa: E402

from channels.registry import get_channel  # noqa: E402

CHANNEL_ID = "co_the_ke"
DEFAULT_SHORT_JOB = "co-the-ke-week1-9x16"
DEFAULT_LONG_JOB = "co-the-ke-week1-16x9"

# ---------------------------------------------------------------------------
# CHARACTERS DEFINITION (SSOT for co_the_ke / ch_organ_buddies)
# ---------------------------------------------------------------------------


def build_characters() -> List[Dict[str, Any]]:
    """Return recurring organ mascots and human host character specifications."""
    return [
        {
            "id": "CH01",
            "name": "Tim (Quả tim dũng cảm)",
            "role": "organ_mascot",
            "appearance": (
                "Cute 2D kawaii heart character Tim with bright red-pink body, tiny expressive face, "
                "stubby arms and eyebrows, brave and energetic posture."
            ),
            "outfit": "No clothing, bare cute organ character.",
        },
        {
            "id": "CH02",
            "name": "Dạ Dày (Cơ quan kịch tính)",
            "role": "organ_mascot",
            "appearance": (
                "Cute 2D kawaii stomach character Da Day with peach-colored soft shape, "
                "tiny dramatic round eyes and theatrical mouth."
            ),
            "outfit": "No clothing, bare cute organ character.",
        },
        {
            "id": "CH03",
            "name": "Gan (Lá gan chăm chỉ)",
            "role": "organ_mascot",
            "appearance": (
                "Cute 2D kawaii liver character Gan with maroon-toned smooth rounded body, "
                "tired but diligent eyes and tiny stubby arms."
            ),
            "outfit": "No clothing, bare cute organ character.",
        },
        {
            "id": "CH04",
            "name": "Não (Bộ não chỉ huy)",
            "role": "organ_mascot",
            "appearance": (
                "Cute 2D kawaii brain-shaped round pink blob mascot Nao with thoughtful eyebrows and stubby arms."
            ),
            "outfit": "No clothing, bare cute organ character.",
        },
        {
            "id": "CH05",
            "name": "Chủ nhân cơ thể (Host)",
            "role": "human_host",
            "appearance": "Simple 2D indie doodle stickman with round white head, dot eyes and thin wire arms.",
            "outfit": "Unshaded flat calm-blue (#7FB3D5) simple T-shirt and dark trousers.",
        },
    ]


# ---------------------------------------------------------------------------
# WEEK 1 TIKTOK SHORT (short_9x16: <= 6 Flow images, 30-45s)
# ---------------------------------------------------------------------------

STORY_WEEK1_SHORT: List[Tuple[str, str, str, str, str, List[Tuple[str, str]]]] = [
    (
        "Cú tát mở đầu với con số 27 cân",
        "A bright minimalist medical clinic corner with a clean wooden consultation table.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            (
                "Nếu bạn cúi đầu nhìn điện thoại, cổ bạn phải gánh hai mươi bảy cân.",
                (
                    "full_scene:CH05|Doodle human host bends neck downward looking at glowing phone screen "
                    "while heavy weight indicator badge appears on neck."
                ),
            ),
        ],
    ),
    (
        "Khối lượng tương đương đứa trẻ tám tuổi",
        "A pure white studio space with an analytical comparison scale on the floor.",
        "analytical_crisp",
        "demystifying_truth",
        "empirical_conflict",
        [
            (
                "Nhưng điều bất ngờ là, áp lực này tương đương bạn cõng một đứa trẻ tám tuổi trên vai suốt cả ngày.",
                (
                    "concept_metaphor:CH05|Cute cartoon dumbbell labeled twenty-seven kilograms pressing "
                    "down on human neck silhouette on clean canvas."
                ),
            ),
        ],
    ),
    (
        "Đốt sống cổ phát tín hiệu cầu cứu",
        "A modern ergonomic laboratory with an anatomical spine display board.",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            (
                "Khi đầu nghiêng sáu mươi độ, các đốt sống cổ lập tức phát tín hiệu đau buốt vì cơ bắp bị căng rách.",
                (
                    "concept_metaphor:CH04|Cute round pink blob brain mascot Nao waves warning alarm flag as "
                    "mechanical spine diagram flashes soft red on white board."
                ),
            ),
        ],
    ),
    (
        "Lưu lượng máu và oxy giảm sút",
        "A clean vascular medical examination room with soft directional daylight.",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            (
                "Lượng máu dẫn lên não sụt giảm, khiến bạn nhanh chóng hoa mắt và giảm hiệu suất làm việc.",
                (
                    "concept_metaphor:CH01|Cute kawaii heart mascot Tim pumps energetically holding tiny "
                    "water hose pointing toward brain icon on white canvas."
                ),
            ),
        ],
    ),
    (
        "Giải pháp nâng tầm mắt và lời kêu gọi",
        "A sunny open morning room with clean white walls and a tidy standing desk.",
        "narrative_warm",
        "tactical_actionable",
        "actionable_resolution",
        [
            (
                "Chỉ cần nâng điện thoại ngang tầm mắt là bạn đã cứu chiếc cổ của mình. "
                "Bạn có hay cúi đầu dùng điện thoại không, lưu lại để nhắc mình nhé?",
                (
                    "full_scene:CH05|Doodle human host lifts phone straight to eye level with "
                    "cheerful relaxed posture and upright spine."
                ),
            ),
        ],
    ),
]


def build_week1_short_sources() -> List[Dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "Assessment of Stresses in the Cervical Spine Caused by Posture and Position of the Head",
            "reference": "Dr. Kenneth K. Hansraj (2014). Surgical Technology International, 25, 277-279.",
            "facts": [
                "Đầu nghiêng 60 độ khiến đốt sống cổ gánh tải 27 cân.",
                "Trọng lượng đầu người ở tư thế thẳng chỉ khoảng năm cân.",
                "Áp lực cột sống tăng vọt gây thoái hóa đĩa đệm và căng cơ.",
                "Giữ đầu thẳng giúp triệt tiêu hoàn toàn áp lực lên cổ.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Cerebral Blood Flow Hemodynamics During Forward Head Posture in Healthy Young Adults",
            "reference": "Dr. David M. Harrison et al. (2019). Journal of Clinical Medicine, 8(8), 1210.",
            "facts": [
                "Cúi gập cổ làm giảm lượng máu động mạch cấp lên não.",
                "Tuần hoàn máu não suy giảm gây chóng mặt và mất tập trung.",
            ],
        },
    ]


def build_week1_short_topic(topic_title: Optional[str] = None) -> ResearchedTopic:
    """Build week 1 short 9:16 topic (<= 6 Flow images, 5 scenes)."""
    ch = get_channel(CHANNEL_ID)
    title = topic_title or "Vì sao cúi đầu nhìn điện thoại làm đốt sống cổ gánh sức nặng 27 kg?"
    scenes = build_scenes_from_story_rows(
        [(t, s, r) for t, s, _, _, _, r in STORY_WEEK1_SHORT],
        character_id="CH05",
    )
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = STORY_WEEK1_SHORT[i][2]
        sc.spoken_style = STORY_WEEK1_SHORT[i][3]
        sc.narrative_phase = STORY_WEEK1_SHORT[i][4]

    scenes[0].source_ids = ["SRC01"]
    scenes[0].claim_facts = [
        ("cổ bạn phải gánh hai mươi bảy cân", "SRC01", "Đầu nghiêng 60 độ khiến đốt sống cổ gánh tải 27 cân.")
    ]
    scenes[1].source_ids = ["SRC01"]
    scenes[1].claim_facts = [
        ("áp lực này tương đương bạn cõng một đứa trẻ tám tuổi", "SRC01", "Trọng lượng đầu người ở tư thế thẳng chỉ khoảng năm cân.")
    ]
    scenes[2].source_ids = ["SRC01"]
    scenes[2].claim_facts = [
        ("các đốt sống cổ lập tức phát tín hiệu đau buốt", "SRC01", "Áp lực cột sống tăng vọt gây thoái hóa đĩa đệm và căng cơ.")
    ]
    scenes[3].source_ids = ["SRC02"]
    scenes[3].claim_facts = [
        ("Lượng máu dẫn lên não sụt giảm", "SRC02", "Cúi gập cổ làm giảm lượng máu động mạch cấp lên não.")
    ]
    scenes[4].source_ids = ["SRC01"]
    scenes[4].claim_facts = [
        ("nâng điện thoại ngang tầm mắt là bạn đã cứu chiếc cổ của mình", "SRC01", "Giữ đầu thẳng giúp triệt tiêu hoàn toàn áp lực lên cổ.")
    ]

    return ResearchedTopic(
        topic=title,
        audience=ch.audience,
        goal="Giải mã gánh nặng 27kg lên đốt sống cổ khi cúi đầu nhìn điện thoại và hướng dẫn thói quen nâng ngang tầm mắt",
        video_type="science",
        min_duration=30.0,
        max_duration=45.0,
        style=ch.visual.style_description,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=build_week1_short_sources(),
        required_points=[{"id": f"R{i:02d}", "text": t} for i, (t, _, _, _, _, _) in enumerate(STORY_WEEK1_SHORT, 1)],
        characters=build_characters(),
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        channel_id=CHANNEL_ID,
        packaging=PackagingSpec(
            youtube_title="Vì Sao Cúi Đầu Khiến Cổ Bạn Gánh Nặng 27 Cân?",
            visual_hook="Nhân vật người que cúi đầu bấm điện thoại với hình ảnh đốt sống cổ chịu tải trọng tương đương đứa trẻ tám tuổi",
            text_overlay="GÁNH NẶNG 27 KG",
            contrast_pair="Nhìn ngang nhẹ tênh vs. Cúi 60 độ gánh 27kg",
            channel_pillar="Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
            funnel_tier="tier_1_broad",
            seo_keywords=["sức khỏe", "cột sống cổ", "cúi đầu dùng điện thoại", "text neck", "cơ thể kể"],
        ),
    )


# ---------------------------------------------------------------------------
# WEEK 1 YOUTUBE LONG (long_16x9: 8 scenes, 24 beats, 3 spinoff shorts)
# ---------------------------------------------------------------------------

STORY_WEEK1_LONG: List[Tuple[str, str, str, str, str, List[Tuple[str, str]]]] = [
    (
        "Cuộc họp khẩn cấp lúc 2 giờ sáng",
        "A clean 2D medical explainer room with a white wooden meeting desk.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            (
                "Nếu bạn quyết định thức trắng đêm nay, đây là lúc các cơ quan họp khẩn.",
                (
                    "full_scene:CH04|Cute round pink blob brain mascot Nao stands at whiteboard holding "
                    "meeting notes beside meeting desk."
                ),
            ),
            (
                "Nhưng điều kinh hoàng nhất không phải là cơn buồn ngủ ập đến.",
                (
                    "concept_metaphor:CH04|Large question mark drawn in soft peach ink floating over the clean meeting table."
                ),
            ),
            (
                "Lúc hai giờ sáng, não bộ phát tín hiệu cầu cứu vì độc tố bắt đầu tích tụ.",
                (
                    "full_scene:CH04|Brain mascot Nao points nervously to chart showing rising red toxin indicators."
                ),
            ),
            (
                "Tim và gan phải gồng mình hoạt động gấp đôi để giữ bạn tỉnh táo.",
                (
                    "full_scene:CH01,CH03|Heart mascot Tim and liver mascot Gan stand ready with energetic and determined expressions."
                ),
            ),
        ],
    ),
    (
        "Não bộ và hệ thống dọn rác glymphatic bị đình trệ",
        "A soft-lit ivory room with an analytical neurological cleaning diagram.",
        "analytical_crisp",
        "demystifying_truth",
        "empirical_conflict",
        [
            (
                "Khi bạn ngủ say, hệ thống dọn rác trong não sẽ tự động xả nước rửa trôi protein rác.",
                (
                    "concept_metaphor:CH04|Brain mascot Nao holds tiny garden watering hose gently flushing "
                    "away small gray clutter blocks."
                ),
            ),
            (
                "Nhưng nếu bạn thức trắng, van xả nước làm sạch hoàn toàn đóng chặt.",
                (
                    "visual_diagram:none|A clean hand-drawn diagram showing a closed golden door latch with zero water flow."
                ),
            ),
            (
                "Chất độc beta-amyloid ứ đọng lại từng phút như rác thải ùn tắc.",
                (
                    "concept_metaphor:CH04|Tiny gray dust particles gathering in small clusters around thoughtful brain mascot Nao."
                ),
            ),
            (
                "Đây là lý do bạn cảm thấy đầu óc nặng trĩu và mờ mịt sau nửa đêm.",
                (
                    "full_scene:CH04|Brain mascot Nao holds tiny temples with stubby arms expressing cognitive fatigue."
                ),
            ),
        ],
    ),
    (
        "Trái tim tăng tốc trong đêm tĩnh lặng",
        "A high-tech cardiology observation room with a glowing rhythmic pulse display.",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            (
                "Trong khi đó, quả tim dũng cảm Tim phải nhận lệnh tăng áp.",
                (
                    "full_scene:CH01|Cute kawaii heart mascot Tim holding miniature megaphone giving pumping signals on white floor."
                ),
            ),
            (
                "Nồng độ hormone cortisol tăng cao kích thích huyết áp nhảy múa liên tục.",
                (
                    "visual_diagram:none|Clean line chart showing blood pressure curve climbing upward sharply in soft pink ink."
                ),
            ),
            (
                "Thay vì được nghỉ ngơi đập chậm lại từ bốn mươi đến năm mươi nhịp mỗi phút,",
                (
                    "concept_metaphor:CH01|Heart mascot Tim holding a tiny stopwatch measuring rhythmic ticking cadence."
                ),
            ),
            (
                "tim bạn bị ép đập dồn dập như thể bạn đang leo dốc giữa đêm.",
                (
                    "full_scene:CH01|Heart mascot Tim jogs energetically along an inclined running track with determined brave expression."
                ),
            ),
        ],
    ),
    (
        "Lá gan kiệt sức trong nhà máy lọc độc",
        "A modern hepatic laboratory with rows of glowing biochemical test tubes.",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            (
                "Ở tầng dưới cơ thể, lá gan Gan đang đối diện một ca trực ác mộng.",
                (
                    "full_scene:CH03|Cute kawaii liver mascot Gan wearing forehead sweatband holding miniature wrench."
                ),
            ),
            (
                "Ba giờ sáng vốn là khung giờ vàng để gan tái tạo tế bào và phân giải mỡ.",
                (
                    "concept_metaphor:CH03|Liver mascot Gan inspecting three clean glass filtering flasks labeled Glycogen on wooden shelf."
                ),
            ),
            (
                "Nhưng khi bạn thức, gan buộc phải chuyển hướng điều phối năng lượng khẩn cấp.",
                (
                    "concept_metaphor:CH03|Liver mascot Gan hurriedly turning tiny valves redirecting golden energy droplets."
                ),
            ),
            (
                "Lượng mỡ thừa không được xử lý kịp sẽ bắt đầu lắng đọng âm thầm.",
                (
                    "visual_diagram:none|Clean microscopic cellular diagram showing tiny lipid bubbles settling gently on white surface."
                ),
            ),
        ],
    ),
    (
        "Cơn đói đêm và tiếng kêu gào của dạ dày",
        "A warm domestic kitchen nook with an open pantry at midnight.",
        "narrative_warm",
        "systemic_friction",
        "lived_friction",
        [
            (
                "Đến bốn giờ sáng, cơ quan kịch tính nhất bắt đầu nổi loạn.",
                (
                    "full_scene:CH02|Cute kawaii peach stomach mascot Da Day holding empty metal bowl with dramatic frown."
                ),
            ),
            (
                "Hormone ghrelin kích thích cơn thèm ăn tăng vọt gấp rưỡi mức bình thường.",
                (
                    "visual_diagram:none|Hand-drawn bar chart contrasting normal appetite versus nighttime hunger spike in peach ink."
                ),
            ),
            (
                "Dạ Dày liên tục gửi tín hiệu đòi nạp đường và tinh bột cay nóng.",
                (
                    "full_scene:CH02|Stomach mascot Da Day waving tiny spoon dramatically demanding midnight instant noodles."
                ),
            ),
            (
                "Nếu bạn nuông chiều ăn khuya, axit dịch vị sẽ cào xé thành dạ dày không thương tiếc.",
                (
                    "concept_metaphor:CH02|Stomach mascot Da Day dodging miniature splashing droplet bubbles of acid on white ground."
                ),
            ),
        ],
    ),
    (
        "Cú sụp đổ năng lượng lúc 6 giờ sáng",
        "A minimalist sunrise study corner with golden morning light.",
        "analytical_crisp",
        "ironic_exposure",
        "empirical_conflict",
        [
            (
                "Sáu giờ sáng, ánh bình minh ló dạng cũng là lúc cơ thể chạm đáy năng lượng.",
                (
                    "full_scene:CH05|Doodle human host sitting at desk under gentle golden morning rays yawning softly."
                ),
            ),
            (
                "Phân tử adenosine gây buồn ngủ đã lấp đầy mọi thụ thể thần kinh trong não.",
                (
                    "concept_metaphor:CH04|Brain mascot Nao surrounded by small receptor slots completely "
                    "saturated with glowing adenosine tokens."
                ),
            ),
            (
                "Một ly cà phê đậm đặc lúc này chỉ là giải pháp đánh lừa tạm thời.",
                (
                    "concept_metaphor:CH04|A miniature porcelain coffee cup pushing aside an adenosine token without removing it."
                ),
            ),
            (
                "Cơn mệt mỏi nén lại sẽ bùng nổ dữ dội hơn vào đầu giờ chiều.",
                (
                    "full_scene:CH04|Brain mascot Nao waving caution sign as energy battery indicator shows one blinking red bar."
                ),
            ),
        ],
    ),
    (
        "Hóa giải tổn thương và phục hồi khoa học",
        "A peaceful wellness recovery lounge with calming indoor green plants.",
        "narrative_warm",
        "tactical_actionable",
        "actionable_resolution",
        [
            (
                "Để bù đắp sau một đêm thức trắng, đừng cố uống nhiều nước tăng lực.",
                (
                    "concept_metaphor:none|A cartoon energy can crossed out with a neat diagonal pencil stroke on white paper."
                ),
            ),
            (
                "Hãy bù đắp cho não một giấc ngủ ngắn hai mươi phút vào buổi trưa.",
                (
                    "full_scene:CH04|Brain mascot Nao resting peacefully on a soft cloud-shaped white pillow."
                ),
            ),
            (
                "Uống thêm nước ấm và ăn bữa sáng thanh nhẹ để giảm áp lực cho gan.",
                (
                    "full_scene:CH03|Liver mascot Gan smiling cheerfully beside a tall clear glass of fresh water."
                ),
            ),
            (
                "Tối hôm sau, hãy đi ngủ sớm trước mười một giờ để chu kỳ sinh học tự hồi phục.",
                (
                    "full_scene:CH01|Heart mascot Tim pumps at a calm relaxed pace beside a small moon crescent icon."
                ),
            ),
        ],
    ),
    (
        "Lắng nghe tiếng nói của cơ thể",
        "A warm bright consultation hall with an inspiring anatomy mural.",
        "narrative_warm",
        "philosophical_anchor",
        "actionable_resolution",
        [
            (
                "Cơ thể bạn là một cỗ máy kỳ diệu nhưng không phải vô hạn.",
                (
                    "concept_metaphor:none|A clean hand-drawn outline of human body with four friendly glowing mascot silhouettes inside."
                ),
            ),
            (
                "Mỗi giờ bạn thức khuya là một lần các cơ quan phải gồng gánh mệt nhoài.",
                (
                    "full_scene:CH05|Doodle human host standing side-by-side with Tim, Da Day, Gan and Nao in warm camaraderie."
                ),
            ),
            (
                "Yêu thương bản thân bắt đầu từ việc cho những người bạn bên trong được nghỉ ngơi.",
                (
                    "full_scene:CH01,CH04|Heart Tim and Brain Nao high-five each other warmly on clean white canvas."
                ),
            ),
            (
                "Bạn có hay thức khuya sau mười hai giờ đêm không, bình luận để cùng nhau thay đổi nhé?",
                (
                    "full_scene:CH05|Doodle human host waves cheerful hand toward camera with friendly open gesture."
                ),
            ),
        ],
    ),
]


def build_week1_long_sources() -> List[Dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "The Glymphatic System: A Beginner Guide",
            "reference": "Dr. Nadia Aalling Jessen et al. (2015). Neurochemical Research, 40(12), 2583-2599.",
            "facts": [
                "Hệ thống não dọn độc tố hiệu quả nhất khi ngủ say.",
                "Thức trắng đêm làm ứ đọng chất thải thần kinh trong não.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Circadian Disruption and Metabolic Disease",
            "reference": "Dr. Frank A.J.L. Scheer et al. (2009). PNAS, 106(11), 4471-4476.",
            "facts": [
                "Thức khuya làm tăng hormone thèm ăn ghrelin của dạ dày.",
                "Gan bị đảo lộn chu kỳ chuyển hóa mỡ khi thức khuya.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Cardiovascular Consequences of Sleep Deprivation",
            "reference": "Dr. Detlev Ganten & Dr. Thomas Penzel (2018). European Heart Journal, 39(10), 834-843.",
            "facts": [
                "Thiếu ngủ kích hoạt hệ giao cảm làm tăng huyết áp và nhịp tim.",
                "Huyết áp không hạ ban đêm làm tăng nguy cơ tổn thương tim.",
            ],
        },
    ]


def build_week1_long_spinoff_shorts() -> List[Dict[str, Any]]:
    return [
        {
            "id": "SPINOFF_01",
            "hook_title": "Dạ Dày Than Phiền Gì Khi Bạn Ăn Mì Đêm?",
            "opening_hook": "Nếu bạn ăn mì gói lúc nửa đêm, dạ dày sẽ khóc thét.",
            "format_profile": "short_9x16",
            "scene_count": 4,
            "body": [
                {
                    "parent_scene_id": "SC05",
                    "image_id": "SC05_I1",
                    "segment_text": "Đến bốn giờ sáng, cơ quan kịch tính nhất bắt đầu nổi loạn.",
                },
                {
                    "parent_scene_id": "SC05",
                    "image_id": "SC05_I2",
                    "segment_text": "Hormone ghrelin kích thích cơn thèm ăn tăng vọt gấp rưỡi mức bình thường.",
                },
                {
                    "parent_scene_id": "SC05",
                    "image_id": "SC05_I3",
                    "segment_text": "Dạ Dày liên tục gửi tín hiệu đòi nạp đường và tinh bột cay nóng.",
                },
                {
                    "parent_scene_id": "SC05",
                    "image_id": "SC05_I4",
                    "segment_text": "Nếu bạn nuông chiều ăn khuya, axit dịch vị sẽ cào xé thành dạ dày không thương tiếc.",
                },
            ],
        },
        {
            "id": "SPINOFF_02",
            "hook_title": "Não Bộ Thức Đêm: Bẫy Độc Tố Chờ Bạn Lúc 2 Giờ",
            "opening_hook": "Nếu bạn thức trắng đêm nay, não bạn không thể dọn rác.",
            "format_profile": "short_9x16",
            "scene_count": 4,
            "body": [
                {
                    "parent_scene_id": "SC02",
                    "image_id": "SC02_I1",
                    "segment_text": "Khi bạn ngủ say, hệ thống dọn rác trong não sẽ tự động xả nước rửa trôi protein rác.",
                },
                {
                    "parent_scene_id": "SC02",
                    "image_id": "SC02_I2",
                    "segment_text": "Nhưng nếu bạn thức trắng, van xả nước làm sạch hoàn toàn đóng chặt.",
                },
                {
                    "parent_scene_id": "SC02",
                    "image_id": "SC02_I3",
                    "segment_text": "Chất độc beta-amyloid ứ đọng lại từng phút như rác thải ùn tắc.",
                },
                {
                    "parent_scene_id": "SC02",
                    "image_id": "SC02_I4",
                    "segment_text": "Đây là lý do bạn cảm thấy đầu óc nặng trĩu và mờ mịt sau nửa đêm.",
                },
            ],
        },
        {
            "id": "SPINOFF_03",
            "hook_title": "Một Ca Trực Quá Tải Của Lá Gan Khi Thức Khuya",
            "opening_hook": "Nếu bạn thức khuya sau hai giờ, lá gan sẽ quá tải.",
            "format_profile": "short_9x16",
            "scene_count": 4,
            "body": [
                {
                    "parent_scene_id": "SC04",
                    "image_id": "SC04_I1",
                    "segment_text": "Ở tầng dưới cơ thể, lá gan Gan đang đối diện một ca trực ác mộng.",
                },
                {
                    "parent_scene_id": "SC04",
                    "image_id": "SC04_I2",
                    "segment_text": "Ba giờ sáng vốn là khung giờ vàng để gan tái tạo tế bào và phân giải mỡ.",
                },
                {
                    "parent_scene_id": "SC04",
                    "image_id": "SC04_I3",
                    "segment_text": "Nhưng khi bạn thức, gan buộc phải chuyển hướng điều phối năng lượng khẩn cấp.",
                },
                {
                    "parent_scene_id": "SC04",
                    "image_id": "SC04_I4",
                    "segment_text": "Lượng mỡ thừa không được xử lý kịp sẽ bắt đầu lắng đọng âm thầm.",
                },
            ],
        },
    ]


def build_week1_long_topic(topic_title: Optional[str] = None) -> Tuple[ResearchedTopic, Dict[str, Any]]:
    """Build week 1 long 16:9 topic and its accompanying omni_plan."""
    ch = get_channel(CHANNEL_ID)
    title = (
        topic_title
        or "Hành Trình 24 Giờ Bên Trong Cơ Thể Khi Bạn Thức Trắng Đêm: Tim, Gan Và Não Bộ Phải Gồng Gánh Ra Sao?"
    )
    scenes = build_scenes_from_story_rows(
        [(t, s, r) for t, s, _, _, _, r in STORY_WEEK1_LONG],
        character_id="CH04",
    )
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = STORY_WEEK1_LONG[i][2]
        sc.spoken_style = STORY_WEEK1_LONG[i][3]
        sc.narrative_phase = STORY_WEEK1_LONG[i][4]

    scenes[1].source_ids = ["SRC01"]
    scenes[1].claim_facts = [
        (
            "hệ thống dọn rác trong não sẽ tự động xả nước rửa trôi protein rác",
            "SRC01",
            "Hệ thống não dọn độc tố hiệu quả nhất khi ngủ say.",
        )
    ]
    scenes[2].source_ids = ["SRC03"]
    scenes[2].claim_facts = [
        (
            "Nồng độ hormone cortisol tăng cao kích thích huyết áp nhảy múa liên tục",
            "SRC03",
            "Thiếu ngủ kích hoạt hệ giao cảm làm tăng huyết áp và nhịp tim.",
        )
    ]
    scenes[3].source_ids = ["SRC02"]
    scenes[3].claim_facts = [
        (
            "Lượng mỡ thừa không được xử lý kịp sẽ bắt đầu lắng đọng âm thầm",
            "SRC02",
            "Gan bị đảo lộn chu kỳ chuyển hóa mỡ khi thức khuya.",
        )
    ]
    scenes[4].source_ids = ["SRC02"]
    scenes[4].claim_facts = [
        (
            "Hormone ghrelin kích thích cơn thèm ăn tăng vọt gấp rưỡi mức bình thường",
            "SRC02",
            "Thức khuya làm tăng hormone thèm ăn ghrelin của dạ dày.",
        )
    ]

    spinoff_shorts = build_week1_long_spinoff_shorts()
    omni_plan = {
        "spinoff_shorts": spinoff_shorts,
        "social_copy": {
            "youtube_description": "Giải mã cơ chế sinh học khi thức trắng đêm với sự tham gia của Tim, Dạ Dày, Gan và Não Bộ.",
            "facebook_post": "Hành trình 24 giờ cơ thể khi thức trắng đêm: các cơ quan phải gồng gánh ra sao?",
        },
    }

    topic = ResearchedTopic(
        topic=title,
        audience=ch.audience,
        goal="Giải mã cuộc họp khẩn cấp và cơ chế suy kiệt của các cơ quan khi bạn thức trắng 24 giờ",
        video_type="science",
        min_duration=180.0,
        max_duration=360.0,
        style=ch.visual.style_description,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        sources=build_week1_long_sources(),
        required_points=[{"id": f"R{i:02d}", "text": t} for i, (t, _, _, _, _, _) in enumerate(STORY_WEEK1_LONG, 1)],
        characters=build_characters(),
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        channel_id=CHANNEL_ID,
        spinoff_shorts=spinoff_shorts,
        packaging=PackagingSpec(
            youtube_title="24 Giờ Thức Trắng: Tim, Gan Và Não Gánh Ra Sao?",
            visual_hook="Cuộc họp khẩn cấp lúc 2 giờ sáng giữa Não, Tim và Gan trên bàn họp cơ thể với ánh đèn vàng cảnh báo",
            text_overlay="CUỘC HỌP 2H SÁNG",
            contrast_pair="Tỉnh táo giả tạo vs. Kiệt quệ tế bào",
            channel_pillar="Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
            funnel_tier="tier_1_broad",
            seo_keywords=["thức trắng đêm", "tác hại thức khuya", "não bộ thức đêm", "gan thải độc", "cơ thể kể"],
        ),
    )

    return topic, omni_plan


# ---------------------------------------------------------------------------
# EXPORT AND AUDIT FUNCTIONS
# ---------------------------------------------------------------------------


def export_package(
    topic: ResearchedTopic,
    out_dir: Path,
    omni_plan: Optional[Dict[str, Any]] = None,
    system_root: Path = SYS_DIR,
) -> Dict[str, Any]:
    """Export and validate complete Schema 3.0 package to target directory."""
    result = write_production_package(
        output_dir=out_dir,
        topic=topic,
        system_root=system_root,
        omni_plan=omni_plan,
        allow_active=True,
    )

    # Validate draft mirrors
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
        json.dumps(outline_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    content_text = (out_dir / "content.json").read_text(encoding="utf-8")
    (draft_dir / "content.json").write_text(content_text, encoding="utf-8")

    return result


def audit_bundle(pkg_dir: Path, channel_id: str = CHANNEL_ID) -> Dict[str, Any]:
    """Audit production bundle against Schema 3.0 contracts, cadence, and hook scorer."""
    brief_data = json.loads((pkg_dir / "brief.json").read_text(encoding="utf-8"))
    content_data = json.loads((pkg_dir / "content.json").read_text(encoding="utf-8"))
    script_data = json.loads((pkg_dir / "script.json").read_text(encoding="utf-8"))

    # 1. Schema 3.0 Contract Validation
    valid_contracts, errors = validate_production_bundle(
        system_root=SYS_DIR,
        brief_data=brief_data,
        content_data=content_data,
    )

    # 2. Acoustic Cadence Check
    checker = ScriptCadenceChecker(nominal_rate=4.0)
    cadence_res = checker.check_scenes(script_data)

    # 3. Hook Retention Scoring
    format_profile = brief_data.get("format_profile") or "short_9x16"
    narrations = [sc["narration"] for sc in content_data.get("scenes", [])]
    hook_res: HookScore = score_script(narrations, channel_id=channel_id, format_profile=format_profile)

    # 4. Total Images Count
    total_images = sum(len(sc.get("images", [])) for sc in content_data.get("scenes", []))

    return {
        "pkg_dir": str(pkg_dir),
        "format_profile": format_profile,
        "valid_contracts": valid_contracts,
        "contract_errors": errors,
        "cadence_report": cadence_res,
        "hook_score": hook_res.score,
        "hook_checks": hook_res.checks,
        "total_images": total_images,
    }


def build_co_the_ke_bundle(
    format_choice: str = "all",
    out_dir: Optional[Path] = None,
    topic_title: Optional[str] = None,
    job_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Build complete co_the_ke production package(s)."""
    base_dir = out_dir or (SYS_DIR / "runs")
    results: Dict[str, Any] = {}

    build_short = format_choice in ("short_9x16", "9:16", "all", "both", "dual")
    build_long = format_choice in ("long_16x9", "16:9", "all", "both", "dual")

    if build_short:
        j_short = job_name if (job_name and not build_long) else DEFAULT_SHORT_JOB
        target_short = base_dir / j_short
        print(f"\n[*] Đang xây dựng gói TikTok Short (9:16) tại: {target_short}")
        short_topic = build_week1_short_topic(topic_title)
        res_short = export_package(short_topic, target_short)
        audit_short = audit_bundle(target_short)
        results["short_9x16"] = {
            "dir": str(target_short),
            "export": res_short,
            "audit": audit_short,
        }
        print(f"  [+] Hợp đồng Schema 3.0: {'HỢP LỆ' if audit_short['valid_contracts'] else 'LỖI'}")
        print(f"  [+] Số ảnh Flow: {audit_short['total_images']} (ngưỡng: <= 6)")
        print(f"  [+] Điểm Hook: {audit_short['hook_score']} / 100")

    if build_long:
        j_long = job_name if (job_name and not build_short) else DEFAULT_LONG_JOB
        target_long = base_dir / j_long
        print(f"\n[*] Đang xây dựng gói YouTube Long (16:9) tại: {target_long}")
        long_topic, omni_plan = build_week1_long_topic(topic_title)
        res_long = export_package(long_topic, target_long, omni_plan=omni_plan)
        audit_long = audit_bundle(target_long)
        results["long_16x9"] = {
            "dir": str(target_long),
            "export": res_long,
            "audit": audit_long,
        }
        print(f"  [+] Hợp đồng Schema 3.0: {'HỢP LỆ' if audit_long['valid_contracts'] else 'LỖI'}")
        print(f"  [+] Số ảnh Flow: {audit_long['total_images']}")
        print(f"  [+] Số Spinoff Shorts: {len(omni_plan['spinoff_shorts'])}")
        print(f"  [+] Điểm Hook: {audit_long['hook_score']} / 100")

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Automated Schema 3.0 production bundle builder for channel 'co_the_ke'."
    )
    parser.add_argument(
        "--format",
        choices=["short_9x16", "long_16x9", "all"],
        default="all",
        help="Format to build: short_9x16 (TikTok), long_16x9 (YouTube), or all (default)",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Custom topic title (defaults to Week 1 topic in PLAN.md)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=SYS_DIR / "runs",
        help="Root directory for output bundles (default: sys/runs)",
    )
    parser.add_argument(
        "--job-name",
        type=str,
        default=None,
        help="Custom job directory name override",
    )
    args = parser.parse_args()

    print(f"=== BUILDER TỰ ĐỘNG KÊNH: CƠ THỂ KỂ ({CHANNEL_ID}) ===")
    results = build_co_the_ke_bundle(
        format_choice=args.format,
        out_dir=args.out_dir,
        topic_title=args.topic,
        job_name=args.job_name,
    )

    all_valid = True
    for fmt, res in results.items():
        audit = res["audit"]
        if not audit["valid_contracts"]:
            print(f"[FAIL] {fmt} vi phạm hợp đồng: {audit['contract_errors']}")
            all_valid = False
        if fmt == "short_9x16" and audit["total_images"] > 6:
            print(f"[FAIL] short_9x16 có {audit['total_images']} ảnh (vượt quá 6 ảnh Flow)")
            all_valid = False
        if audit["hook_score"] < 70:
            print(f"[FAIL] {fmt} có điểm Hook {audit['hook_score']} (< 70)")
            all_valid = False

    if all_valid:
        print("\n[SUCCESS] Tất cả các gói sản xuất đều hợp lệ 100%!")
        return 0
    else:
        print("\n[ERROR] Có lỗi kiểm định xảy ra.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
