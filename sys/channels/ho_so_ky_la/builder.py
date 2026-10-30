#!/usr/bin/env python3
"""Automated Production Bundle Builder for Channel 6: Hồ Sơ Kỳ Lạ (ho_so_ky_la).

Channel Niche: Bí ẩn và chuyện kỳ lạ có thật
Visual Identity: ch_noir_dossier (2D noir graphic-novel, high contrast #111111, #E8E2D0, #5A5F66, #C0392B)
Persona: Thám tử điềm tĩnh mở từng tập hồ sơ (Detective CH01)
Voice: VietNarrator (speed 1.0x)

Outputs:
- TikTok Short (short_9x16, <= 8 Flow images, 60-90s, Hook score >= 70)
- YouTube Long (long_16x9, multi-scene documentary explainer + 4 omni-platform spinoff shorts)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure sys and sys/tools are in sys.path
SYS_DIR = Path(__file__).resolve().parents[2]
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from channels.registry import get_channel  # noqa: E402
from content.research_story_architect import (  # noqa: E402
    HumanEditorialSpec,
    PackagingSpec,
    ResearchedScene,
    ResearchedTopic,
    build_brief_v3,
    build_content_v3,
    build_scenes_from_story_rows,
    compute_brief_hash,
    generate_script_json,
    serialize_brief_json,
    validate_production_bundle,
)
from tools.script_cadence_checker import (  # noqa: E402
    NOMINAL_SPEECH_RATE,
    ScriptCadenceChecker,
)
from tools.script_hook_scorer import score_script  # noqa: E402

CHANNEL_ID = "ho_so_ky_la"
VISUAL_PROFILE_ID = "ch_noir_dossier"
FAST_SHORT_MAX_IMAGES = 8
SPINOFF_SHORTS_COUNT = 4

# ---------------------------------------------------------------------------
# DEFAULT WEEK 1 PRODUCTION DATA: Con tàu Mary Celeste
# ---------------------------------------------------------------------------

STORY_ROWS_9X16: List[Tuple[str, str, str, str, List[Tuple[str, str]]]] = [
    (
        "Bí ẩn con tàu ma giữa đại dương",
        "Flat aged off-white paper canvas with high-contrast noir shadows.",
        "narrative_warm",
        "lived_friction",
        [
            (
                "Bạn có biết bí mật rùng rợn về con tàu ma trôi dạt không một bóng người?",
                "full_scene:CH01|Silhouette of the detective in long coat and hat examining an aged case folder on off-white paper.",
            ),
            (
                "Giữa đại dương mênh mông, con tàu Ma-ri Xê-lét được tìm thấy hoàn toàn nguyên vẹn. Thế nhưng mười người trên tàu đã biến mất mà không để lại bất kỳ dấu vết nào.",
                "concept_metaphor:none|A stark black ink drawing of a two-masted wooden brigantine floating on calm ocean waves under off-white sky.",
            ),
        ],
    ),
    (
        "Hiện trường kỳ lạ không một dấu vết",
        "Flat noir investigative case desk with folders and stamped documents.",
        "narrative_warm",
        "empirical_conflict",
        [
            (
                "Trên bàn ăn, thức ăn vẫn còn nguyên vẹn và ấm nóng. Quần áo của thủy thủ đoàn được xếp gọn gàng trong các khoang ngủ.",
                "still_life:none|A flat top-down illustration of a neat wooden cabin table with clean plates and folded sailor clothes.",
            ),
            (
                "Tiền bạc và hàng hóa quý giá trong kho hàng không hề bị đụng tới. Dường như mọi người vừa mới rời đi chỉ vài phút trước đó.",
                "variation:CH01|Detective silhouette shines a focused flashlight beam onto undisturbed cargo crates with red evidence tags.",
            ),
        ],
    ),
    (
        "Hai giả thuyết đối đầu",
        "Flat vintage nautical chart table on aged off-white background.",
        "analytical_crisp",
        "structural_model",
        [
            (
                "Giả thuyết cướp biển tấn công ngay lập tức bị các điều tra viên bác bỏ. Nếu cướp biển cướp tàu, vì sao hàng hóa giá trị vẫn còn nguyên?",
                "visual_diagram:none|A flat nautical navigation map with red map pins and crossed black ink question marks.",
            ),
            (
                "Một giả thuyết khác cho rằng cồn công nghiệp bốc hơi tạo áp suất nguy hiểm. Thuyền trưởng đã ra lệnh sơ tán khẩn cấp xuống thuyền cứu sinh.",
                "concept_metaphor:none|A line-art cutaway showing wooden cargo barrels emitting subtle vapor wisps with red warning stamp.",
            ),
        ],
    ),
    (
        "Manh mối đứt đoạn giữa biển khơi",
        "Flat dark ocean horizon silhouette under pale grey sky.",
        "reflective_slow",
        "actionable_resolution",
        [
            (
                "Chiếc thuyền cứu sinh duy nhất đã biến mất cùng toàn bộ nhật ký hải trình. Sợi dây thừng buộc thuyền bị đứt đoạn trôi nổi giữa làn sóng dữ.",
                "still_life:none|A single severed towline rope floating in dark ink water beside a missing lifeboat outline.",
            ),
            (
                "Đến tận ngày nay, bí ẩn về số phận của mười con người vẫn chưa có lời giải đáp. Bạn có tin vào lời nguyền con tàu ma? Đón xem phần tiếp theo để biết câu trả lời.",
                "full_scene:CH01|The detective closes the thick case dossier stamped with a prominent red wax seal.",
            ),
        ],
    ),
]

STORY_ROWS_16X9: List[Tuple[str, str, str, str, List[Tuple[str, str]]]] = [
    (
        "Tiếng chuông gác đêm và con tàu vô chủ",
        "Flat aged off-white paper canvas with high-contrast noir shadows.",
        "narrative_warm",
        "lived_friction",
        [
            (
                "Bạn có biết vụ mất tích bí ẩn nhất lịch sử hàng hải thế giới là gì không?",
                "full_scene:CH01|Silhouette of the detective in long coat and hat examining an aged case folder on off-white paper.",
            ),
            (
                "Tháng mười hai năm một nghìn tám trăm bảy mươi hai, người ta tìm thấy con tàu trôi dạt giữa đại dương.",
                "concept_metaphor:none|A stark black ink drawing of a two-masted wooden brigantine floating on calm ocean waves under off-white sky.",
            ),
        ],
    ),
    (
        "Lời khai nhân chứng tàu Dei Gratia",
        "Flat vintage nautical chart table on aged off-white background.",
        "narrative_warm",
        "lived_friction",
        [
            (
                "Thủy thủ đoàn tàu bạn nhận thấy những cánh buồm căng gió nhưng đường đi lảo đảo vô định.",
                "visual_diagram:none|Vintage brass nautical compass and spyglass resting on an aged sea navigation chart.",
            ),
            (
                "Họ áp sát mạn thuyền và gõ chuông báo hiệu nhưng hoàn toàn không có tiếng người đáp lại.",
                "full_scene:CH01|Detective silhouette peers through antique binoculars toward a quiet ship silhouette in the mist.",
            ),
        ],
    ),
    (
        "Hồ sơ khởi hành từ cảng New York",
        "Flat noir investigative case desk with folders and stamped documents.",
        "narrative_warm",
        "empirical_conflict",
        [
            (
                "Hồ sơ lưu trữ tại cảng ghi nhận tàu rời bến vào đầu tháng mười một với đầy đủ trang thiết bị.",
                "still_life:none|A yellowed official harbor registry document stamped with red wax and historical seal.",
            ),
            (
                "Khoang tàu chở hơn một nghìn bảy trăm thùng cồn công nghiệp được niêm phong cẩn thận.",
                "concept_metaphor:none|A flat cross-section line drawing of wooden barrels stacked symmetrically in cargo hull.",
            ),
        ],
    ),
    (
        "Thuyền trưởng Benjamin Briggs và gia đình",
        "Flat cabin interior wall outline in clean noir line-art.",
        "narrative_warm",
        "empirical_conflict",
        [
            (
                "Vị thuyền trưởng dày dạn kinh nghiệm đi cùng người vợ trẻ và đứa con gái mới hai tuổi.",
                "still_life:none|Framed silhouette oval photograph of a Victorian captain family resting on wooden cabinet.",
            ),
            (
                "Ông nổi tiếng là người điềm tĩnh, cẩn trọng và không bao giờ đưa ra quyết định liều lĩnh.",
                "variation:CH01|Detective examines the captain logbook table with focused flashlight beam on dark surface.",
            ),
        ],
    ),
    (
        "Khám nghiệm hiện trường cabin",
        "Flat top-down dining table composition in high-contrast ink line.",
        "analytical_crisp",
        "empirical_conflict",
        [
            (
                "Bữa ăn dở dang trên bàn vẫn còn nguyên vẹn, chứng tỏ cuộc rời tàu diễn ra trong chớp mắt.",
                "still_life:none|A clean top-down wooden table with porcelain plates and cutlery arranged in orderly peace.",
            ),
            (
                "Quần áo ấm của cả gia đình vẫn được xếp gọn gàng trong các rương gỗ ở phòng ngủ.",
                "concept_metaphor:none|Neatly folded wool blankets and open travel leather trunk on clean minimalist floor.",
            ),
        ],
    ),
    (
        "Kho vàng bạc và tài sản nguyên vẹn",
        "Flat cargo storage compartment drawn in high contrast black and grey.",
        "analytical_crisp",
        "structural_model",
        [
            (
                "Toàn bộ tài sản cá nhân và tiền lương của thủy thủ đoàn vẫn nằm nguyên trong hòm khóa.",
                "still_life:none|Heavy iron-banded chest with solid padlocks intact and gleaming in subtle grey highlights.",
            ),
            (
                "Lương thực và nước ngọt trên tàu đủ dùng cho sáu tháng hành trình mà không hề hấn gì.",
                "concept_metaphor:none|Rows of sealed water casks and grain sacks standing tall with zero signs of plundering.",
            ),
        ],
    ),
    (
        "Chiếc thuyền cứu sinh độc nhất biến mất",
        "Flat starboard wooden ship deck outline under pale ocean sky.",
        "analytical_crisp",
        "structural_model",
        [
            (
                "Dây neo của xuồng cứu sinh duy nhất đã bị cắt đứt vội vã từ phía mạn phải của con tàu.",
                "concept_metaphor:none|Empty wooden davit arms with severed hemp ropes dangling over dark sea waters.",
            ),
            (
                "Thước đo hải đồ và đồng hồ định vị thiên văn cũng được mang theo khi mọi người rời đi.",
                "still_life:none|An empty brass instrument velvet box sitting open on the navigation table.",
            ),
        ],
    ),
    (
        "Bác bỏ giả thuyết cướp biển tấn công",
        "Flat noir investigation archive with pinned evidence cards.",
        "analytical_crisp",
        "structural_model",
        [
            (
                "Không có bất kỳ dấu vết giằng co, xô xát hay vũ khí nào được tìm thấy trên khắp các boong.",
                "visual_diagram:none|A red cross mark stamped firmly over a pirate skull icon on white dossier card.",
            ),
            (
                "Nếu là hải tặc, chúng không thể bỏ qua kho cồn quý giá và hòm tiền vàng nằm ngay trước mắt.",
                "full_scene:CH01|Detective shakes head thoughtfully while reviewing forensic evidence tags on black board.",
            ),
        ],
    ),
    (
        "Giả thuyết bão biển hay vòi rồng nước",
        "Flat vintage meteorological pressure chart with hand-drawn isobar lines.",
        "reflective_slow",
        "counter_argument",
        [
            (
                "Một số người nghĩ tới vòi rồng bất ngờ tràn qua boong tàu cuốn phăng toàn bộ thủy thủ.",
                "concept_metaphor:none|A swirling black ink spiral cyclone diagram sweeping across calm ocean coordinate lines.",
            ),
            (
                "Nhưng nhật ký hải trình ghi nhận thời tiết những ngày đó vô cùng thuận lợi và biển lặng.",
                "visual_diagram:none|Barometer gauge showing steady high atmospheric pressure needle pointing to fair weather.",
            ),
        ],
    ),
    (
        "Giả thuyết nổ áp suất hơi cồn công nghiệp",
        "Flat chemical formula sketch on off-white aged paper background.",
        "reflective_slow",
        "causal_mechanism",
        [
            (
                "Khi nhiệt độ hầm hàng tăng cao, hơi cồn bốc lên có thể tạo ra tiếng nổ và áp suất dữ dội.",
                "concept_metaphor:none|Subtle steam wisps escaping from wooden barrel seams with red cautionary exclamation mark.",
            ),
            (
                "Lo sợ tàu nổ tung, thuyền trưởng đã vội vã sơ tán cả nhà xuống chiếc thuyền nhỏ kéo sau.",
                "variation:CH01|Detective shines light on the open hold hatch cover found lying flat on the deck.",
            ),
        ],
    ),
    (
        "Sợi dây thừng định mệnh bị sóng biển cắt đứt",
        "Flat dark ocean horizon silhouette under pale grey sky.",
        "reflective_slow",
        "actionable_resolution",
        [
            (
                "Sợi dây thừng buộc thuyền cứu sinh vào tàu mẹ đã bị đứt rời giữa một cơn gió giật bất ngờ.",
                "still_life:none|A frayed end of thick hemp rope floating lonely on deep dark ink water surface.",
            ),
            (
                "Chiếc thuyền nhỏ bé trôi dạt ra xa trong sự bất lực tuyệt vọng của mười con người giữa biển khơi.",
                "concept_metaphor:none|A tiny wooden rowboat silhouette isolated in vast empty negative space of ocean expanse.",
            ),
        ],
    ),
    (
        "Bí ẩn một trăm năm mươi năm chưa có lời giải",
        "Flat noir case file desk with multiple yellowed archives.",
        "reflective_slow",
        "actionable_resolution",
        [
            (
                "Đến tận ngày nay, số phận của thuyền trưởng Briggs và gia đình vẫn mãi là một ẩn số lớn.",
                "visual_diagram:none|A timeline chart from 1872 to modern day marked with an enduring red question mark.",
            ),
            (
                "Không một thi thể hay mảnh vỡ nào của chiếc thuyền cứu sinh từng dạt vào bờ biển thế giới.",
                "full_scene:CH01|The detective stands in profile closing the Mary Celeste folder under a dim desk lamp.",
            ),
        ],
    ),
    (
        "Đóng lại hồ sơ con tàu ma",
        "Solid ivory neutral field with minimal noir evidence prop.",
        "reflective_slow",
        "closing",
        [
            (
                "Hồ sơ con tàu Ma-ri Xê-lét khép lại với câu hỏi lớn nhất về giới hạn của tự nhiên và con người.",
                "concept_metaphor:none|A large red wax seal stamped firmly across a closed dark dossier folder labeled CASE CLOSED.",
            ),
            (
                "Bạn tin vào giả thuyết khoa học hay lời nguyền biển sâu? Hãy để lại ý kiến của bạn nhé.",
                "variation:CH01|Detective raises hat slightly in polite salute to the audience before stepping back.",
            ),
        ],
    ),
    (
        "Gợi mở hồ sơ kỳ lạ tiếp theo",
        "Clean aged off-white canvas with fresh dossier preview.",
        "reflective_slow",
        "closing",
        [
            (
                "Tuần sau, chúng ta sẽ mở tiếp tập hồ sơ về sự cố đèo Đi-át-lốp với chín người leo núi.",
                "still_life:none|A fresh dossier folder labeled DYATLOV INCIDENT with a red bookmark ribbon ready to open.",
            ),
            (
                "Đăng ký kênh để cùng đồng hành trong những hành trình khám phá bí ẩn có thật tiếp theo.",
                "full_scene:CH01|Detective places new dossier onto center of desk, ready for the next investigative case.",
            ),
        ],
    ),
]


def _build_sources() -> List[Dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "Mary Celeste: The Mystery of the Abandoned Ship",
            "reference": "Brian Hicks (2004). Ballantine Books. ISBN: 978-0345463920.",
            "facts": [
                "Con tàu trôi dạt giữa đại dương hoàn toàn nguyên vẹn hàng hóa.",
                "Toàn bộ mười người trên tàu biến mất không để lại dấu vết.",
                "Thuyền cứu sinh duy nhất và nhật ký hàng hải đều biến mất.",
                "Khoang tàu chứa một nghìn bảy trăm thùng cồn công nghiệp.",
                "Bữa ăn dở dang và quần áo vẫn xếp gọn trong các khoang.",
            ],
        }
    ]


def _build_editorial() -> HumanEditorialSpec:
    return HumanEditorialSpec(
        topic_dilemmas=[
            "Vì sao toàn bộ thủy thủ đoàn lại rời bỏ một con tàu hoàn toàn nguyên vẹn và đầy đủ lương thực để nhảy xuống chiếc thuyền cứu sinh nhỏ bé giữa biển động?",
        ],
        dynamic_questions=[
            "Liệu có áp lực vô hình nào từ tự nhiên hoặc tâm lý hoảng loạn đã buộc thuyền trưởng Briggs phải ra quyết định rời tàu ngay tức khắc?",
            "Manh mối dây thừng bị đứt nói lên điều gì về nỗ lực cuối cùng của thủy thủ đoàn nhằm níu giữ con tàu mẹ?",
        ],
        author_raw_input="Một vụ mất tích bí ẩn có thật trong lịch sử hàng hải thế giới, nơi mọi giả thuyết thông thường đều bị bác bỏ bởi hiện trường nguyên vẹn.",
        editorial_stance="Kể lại vụ việc một cách điềm đạm, tôn trọng sự thật lịch sử và chứng cứ thực nghiệm thay vì thêu dệt những yếu tố siêu nhiên vô căn cứ.",
        expanded_content_ideas=[
            {
                "idea_id": "IDEA_01",
                "angle_type": "analysis",
                "summary": "Phân tích cơ chế bốc hơi và áp suất của một nghìn bảy trăm thùng cồn công nghiệp trong khoang kín.",
                "target_narrative_phase": "causal_mechanism",
            },
            {
                "idea_id": "IDEA_02",
                "angle_type": "evaluation",
                "summary": "Đánh giá chi tiết hải trình và tình trạng dây thừng cứu hộ để làm rõ bi kịch chia cắt giữa tàu mẹ và xuồng nhỏ.",
                "target_narrative_phase": "counter_argument",
            },
        ],
    )


def build_topic_9x16(topic_title: Optional[str] = None) -> ResearchedTopic:
    """Build a TikTok Short (short_9x16, <= 8 Flow images, 60-90s) production topic."""
    ch = get_channel(CHANNEL_ID)
    scenes: List[ResearchedScene] = build_scenes_from_story_rows(STORY_ROWS_9X16, character_id="CH01")

    # Link requirements and facts
    for idx, sc in enumerate(scenes):
        r_id = f"R{idx+1:02d}"
        sc.requirements = [r_id]

    scenes[0].source_ids = ["SRC01"]
    scenes[0].claim_facts = [
        (
            "con tàu Ma-ri Xê-lét được tìm thấy hoàn toàn nguyên vẹn",
            "SRC01",
            "Con tàu trôi dạt giữa đại dương hoàn toàn nguyên vẹn hàng hóa.",
        ),
        (
            "mười người trên tàu đã biến mất mà không để lại bất kỳ dấu vết nào",
            "SRC01",
            "Toàn bộ mười người trên tàu biến mất không để lại dấu vết.",
        ),
    ]
    scenes[3].source_ids = ["SRC01"]
    scenes[3].claim_facts = [
        (
            "Chiếc thuyền cứu sinh duy nhất đã biến mất cùng toàn bộ nhật ký hải trình",
            "SRC01",
            "Thuyền cứu sinh duy nhất và nhật ký hàng hải đều biến mất.",
        ),
    ]

    req_points = [{"id": f"R{idx+1:02d}", "text": sc.title} for idx, sc in enumerate(scenes)]
    sources = _build_sources()

    total_dur = sum(s.duration for s in scenes)
    min_dur = round(max(50.0, total_dur * 0.90), 1)
    max_dur = round(total_dur * 1.15, 1)

    title_text = topic_title or "Bí Ẩn Tàu Mary Celeste: Vụ Mất Tích Không Lời Giải"
    if len(title_text) > 55:
        title_text = title_text[:52] + "..."

    packaging = PackagingSpec(
        youtube_title=title_text,
        visual_hook="A solitary wooden brigantine floating on dark ocean water with a glowing red evidence circle around the empty deck",
        text_overlay="CON TÀU MA",
        contrast_pair="Thuyền nguyên vẹn vs Người biến mất",
        channel_pillar="Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
        funnel_tier="tier_1_broad",
        seo_keywords=["tàu ma mary celeste", "bí ẩn mất tích", "hồ sơ kỳ lạ", "chuyện kỳ lạ có thật"],
        thumbnail_prompt="One mysterious abandoned ship circled in red on off-white paper, 2D noir graphic-novel illustration, heavy black ink shapes and flat slate grey shadows.",
        layout_mode="integrated_poster",
        typography_style="Bold hand-drawn crimson-red (#C0392B) uppercase lettering on aged paper canvas",
    )

    return ResearchedTopic(
        topic=topic_title or "Hồ Sơ Con Tàu Mary Celeste: Bí Ẩn Vụ Mất Tích Giữa Đại Dương",
        audience=ch.audience,
        goal="Khám phá và giải mã hồ sơ bí ẩn con tàu Mary Celeste trôi dạt không người lái năm 1872 bằng chứng cứ điều tra thực tế.",
        video_type="investigative_dossier",
        min_duration=min_dur,
        max_duration=max_dur,
        style=ch.visual.style_description,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        subtitles=True,
        voice=ch.voice,
        speed=ch.speed,
        visual_pacing_profile="full_frame_v1",
        sources=sources,
        required_points=req_points,
        characters=[
            {
                "id": "CH01",
                "name": ch.persona,
                "appearance": ch.visual.cast_appearance,
                "outfit": ch.visual.outfit,
            }
        ],
        scenes=scenes,
        packaging=packaging,
        human_editorial=_build_editorial(),
        channel_id=CHANNEL_ID,
    )


def build_topic_16x9(topic_title: Optional[str] = None) -> ResearchedTopic:
    """Build a YouTube Long (long_16x9, 14 scenes, documentary explainer + 4 spinoff shorts) production topic."""
    ch = get_channel(CHANNEL_ID)
    scenes: List[ResearchedScene] = build_scenes_from_story_rows(STORY_ROWS_16X9, character_id="CH01")

    # Link requirements and claims
    for idx, sc in enumerate(scenes):
        sc.requirements = [f"R{idx+1:02d}"]

    scenes[0].source_ids = ["SRC01"]
    scenes[0].claim_facts = [
        (
            "người ta tìm thấy con tàu trôi dạt giữa đại dương",
            "SRC01",
            "Con tàu trôi dạt giữa đại dương hoàn toàn nguyên vẹn hàng hóa.",
        ),
    ]
    scenes[2].source_ids = ["SRC01"]
    scenes[2].claim_facts = [
        (
            "Khoang tàu chở hơn một nghìn bảy trăm thùng cồn công nghiệp",
            "SRC01",
            "Khoang tàu chứa một nghìn bảy trăm thùng cồn công nghiệp.",
        ),
    ]
    scenes[4].source_ids = ["SRC01"]
    scenes[4].claim_facts = [
        (
            "Quần áo ấm của cả gia đình vẫn được xếp gọn gàng trong các rương gỗ",
            "SRC01",
            "Bữa ăn dở dang và quần áo vẫn xếp gọn trong các khoang.",
        ),
    ]
    scenes[6].source_ids = ["SRC01"]
    scenes[6].claim_facts = [
        (
            "Dây neo của xuồng cứu sinh duy nhất đã bị cắt đứt vội vã",
            "SRC01",
            "Thuyền cứu sinh duy nhất và nhật ký hàng hải đều biến mất.",
        ),
    ]
    scenes[11].source_ids = ["SRC01"]
    scenes[11].claim_facts = [
        (
            "số phận của thuyền trưởng Briggs và gia đình vẫn mãi là một ẩn số lớn",
            "SRC01",
            "Toàn bộ mười người trên tàu biến mất không để lại dấu vết.",
        ),
    ]

    req_points = [{"id": f"R{idx+1:02d}", "text": sc.title} for idx, sc in enumerate(scenes)]
    sources = _build_sources()

    total_dur = sum(s.duration for s in scenes)
    min_dur = round(total_dur * 0.90, 1)
    max_dur = round(total_dur * 1.15, 1)

    title_text = topic_title or "Bí Ẩn Tàu Mary Celeste: Vụ Mất Tích Không Lời Giải"
    if len(title_text) > 55:
        title_text = title_text[:52] + "..."

    packaging = PackagingSpec(
        youtube_title=title_text,
        visual_hook="A solitary wooden brigantine floating on dark ocean water with a glowing red evidence circle around the empty deck",
        text_overlay="HỒ SƠ TÀU MA",
        contrast_pair="Thuyền nguyên vẹn vs Người biến mất",
        channel_pillar="Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
        funnel_tier="tier_1_broad",
        seo_keywords=["hồ sơ con tàu mary celeste", "vụ mất tích bí ẩn", "bí ẩn hàng hải", "chuyện kỳ lạ có thật"],
        thumbnail_prompt="One mysterious abandoned ship circled in red on off-white paper, 2D noir graphic-novel illustration, heavy black ink shapes and flat slate grey shadows.",
        layout_mode="integrated_poster",
        typography_style="Bold hand-drawn crimson-red (#C0392B) uppercase lettering on aged paper canvas",
    )

    # 4 Omnichannel spinoff shorts extracted from master 16:9 scenes (zero extra Flow images needed)
    spinoff_shorts = [
        {
            "id": "SPINOFF_01",
            "hook_title": "Chi Tiết Kỳ Lạ Trên Boong Tàu Mary Celeste",
            "opening_hook": "Bạn có biết chi tiết kỳ lạ nhất trên con tàu Ma-ri Xê-lét?",
            "format_profile": "short_9x16",
            "scene_count": 4,
            "body": [
                {
                    "parent_scene_id": "SC01",
                    "image_id": "SC01_I1",
                    "segment_text": "Bạn có biết vụ mất tích bí ẩn nhất lịch sử hàng hải thế giới là gì không?",
                },
                {
                    "parent_scene_id": "SC04",
                    "image_id": "SC04_I1",
                    "segment_text": "Vị thuyền trưởng dày dạn kinh nghiệm đi cùng người vợ trẻ và đứa con gái mới hai tuổi.",
                },
                {
                    "parent_scene_id": "SC05",
                    "image_id": "SC05_I1",
                    "segment_text": "Bữa ăn dở dang trên bàn vẫn còn nguyên vẹn, chứng tỏ cuộc rời tàu diễn ra trong chớp mắt.",
                },
                {
                    "parent_scene_id": "SC07",
                    "image_id": "SC07_I1",
                    "segment_text": "Dây neo của xuồng cứu sinh duy nhất đã bị cắt đứt vội vã từ phía mạn phải của con tàu.",
                },
            ],
        },
        {
            "id": "SPINOFF_02",
            "hook_title": "Vì Sao Giả Thuyết Cướp Biển Tàu Ma Bị Bác Bỏ?",
            "opening_hook": "Vì sao giả thuyết cướp biển con tàu ma bị bác bỏ ngay?",
            "format_profile": "short_9x16",
            "scene_count": 4,
            "body": [
                {
                    "parent_scene_id": "SC06",
                    "image_id": "SC06_I1",
                    "segment_text": "Toàn bộ tài sản cá nhân và tiền lương của thủy thủ đoàn vẫn nằm nguyên trong hòm khóa.",
                },
                {
                    "parent_scene_id": "SC08",
                    "image_id": "SC08_I1",
                    "segment_text": "Không có bất kỳ dấu vết giằng co, xô xát hay vũ khí nào được tìm thấy trên khắp các boong.",
                },
                {
                    "parent_scene_id": "SC08",
                    "image_id": "SC08_I2",
                    "segment_text": "Nếu là hải tặc, chúng không thể bỏ qua kho cồn quý giá và hòm tiền vàng nằm ngay trước mắt.",
                },
                {
                    "parent_scene_id": "SC09",
                    "image_id": "SC09_I1",
                    "segment_text": "Một số người nghĩ tới vòi rồng bất ngờ tràn qua boong tàu cuốn phăng toàn bộ thủy thủ.",
                },
            ],
        },
        {
            "id": "SPINOFF_03",
            "hook_title": "Giả Thuyết Khoa Học Giải Thích Lệnh Bỏ Tàu",
            "opening_hook": "Bạn có biết giả thuyết khoa học hợp lý nhất vụ bỏ tàu?",
            "format_profile": "short_9x16",
            "scene_count": 4,
            "body": [
                {
                    "parent_scene_id": "SC03",
                    "image_id": "SC03_I2",
                    "segment_text": "Khoang tàu chở hơn một nghìn bảy trăm thùng cồn công nghiệp được niêm phong cẩn thận.",
                },
                {
                    "parent_scene_id": "SC10",
                    "image_id": "SC10_I1",
                    "segment_text": "Khi nhiệt độ hầm hàng tăng cao, hơi cồn bốc lên có thể tạo ra tiếng nổ và áp suất dữ dội.",
                },
                {
                    "parent_scene_id": "SC10",
                    "image_id": "SC10_I2",
                    "segment_text": "Lo sợ tàu nổ tung, thuyền trưởng đã vội vã sơ tán cả nhà xuống chiếc thuyền nhỏ kéo sau.",
                },
                {
                    "parent_scene_id": "SC11",
                    "image_id": "SC11_I1",
                    "segment_text": "Sợi dây thừng buộc thuyền cứu sinh vào tàu mẹ đã bị đứt rời giữa một cơn gió giật bất ngờ.",
                },
            ],
        },
        {
            "id": "SPINOFF_04",
            "hook_title": "Manh Mối Đứt Đoạn Của Mười Thủy Thủ Biến Mất",
            "opening_hook": "Manh mối nào hé lộ số phận mười thủy thủ biến mất?",
            "format_profile": "short_9x16",
            "scene_count": 4,
            "body": [
                {
                    "parent_scene_id": "SC02",
                    "image_id": "SC02_I1",
                    "segment_text": "Thủy thủ đoàn tàu bạn nhận thấy những cánh buồm căng gió nhưng đường đi lảo đảo vô định.",
                },
                {
                    "parent_scene_id": "SC11",
                    "image_id": "SC11_I2",
                    "segment_text": "Chiếc thuyền nhỏ bé trôi dạt ra xa trong sự bất lực tuyệt vọng của mười con người giữa biển khơi.",
                },
                {
                    "parent_scene_id": "SC12",
                    "image_id": "SC12_I1",
                    "segment_text": "Đến tận ngày nay, số phận của thuyền trưởng Briggs và gia đình vẫn mãi là một ẩn số lớn.",
                },
                {
                    "parent_scene_id": "SC13",
                    "image_id": "SC13_I1",
                    "segment_text": "Hồ sơ con tàu Ma-ri Xê-lét khép lại với câu hỏi lớn nhất về giới hạn của tự nhiên và con người.",
                },
            ],
        },
    ]

    return ResearchedTopic(
        topic=topic_title or "Hồ Sơ Con Tàu Mary Celeste: Bí Ẩn Vụ Mất Tích Giữa Đại Dương",
        audience=ch.audience,
        goal="Tái hiện toàn diện hồ sơ điều tra bí ẩn con tàu Mary Celeste trôi dạt năm 1872 với bằng chứng và các giả thuyết đối trọng.",
        video_type="investigative_documentary",
        min_duration=min_dur,
        max_duration=max_dur,
        style=ch.visual.style_description,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        subtitles=False,
        voice=ch.voice,
        speed=ch.speed,
        visual_pacing_profile="full_frame_v1",
        sources=sources,
        required_points=req_points,
        characters=[
            {
                "id": "CH01",
                "name": ch.persona,
                "appearance": ch.visual.cast_appearance,
                "outfit": ch.visual.outfit,
            }
        ],
        scenes=scenes,
        packaging=packaging,
        human_editorial=_build_editorial(),
        channel_id=CHANNEL_ID,
        spinoff_shorts=spinoff_shorts,
    )


def export_package(topic: ResearchedTopic, output_dir: Path, include_spinoffs: bool = False) -> Dict[str, Any]:
    """Assemble and write all Schema 3.0 package artifacts and run validation."""
    output_dir.mkdir(parents=True, exist_ok=True)
    brief_data = build_brief_v3(topic, system_root=SYS_DIR)
    if topic.spinoff_shorts:
        brief_data.update(omni_platform=True, reframe_mode=True, spinoff_shorts=topic.spinoff_shorts)

    brief_hash = compute_brief_hash(brief_data)
    content_data = build_content_v3(topic, brief_data, brief_hash, brief_revision=1)
    script_data = generate_script_json(topic)

    checker = ScriptCadenceChecker(
        nominal_rate=NOMINAL_SPEECH_RATE,
        forbid_opening_pause=True,
        max_opening_hook_syllables=18,
    )
    cadence_report = checker.check_scenes(script_data)

    # Calculate Hook score
    narrations = [sc["narration"] for sc in content_data["scenes"]]
    hook_score_result = score_script(narrations, CHANNEL_ID, topic.format_profile or "short_9x16")

    brief_file = output_dir / "brief.json"
    content_file = output_dir / "content.json"
    script_file = output_dir / "script.json"
    cadence_file = output_dir / "cadence_report.json"

    brief_file.write_text(serialize_brief_json(brief_data), encoding="utf-8")
    content_file.write_text(json.dumps(content_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    script_file.write_text(json.dumps(script_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    cadence_file.write_text(json.dumps(cadence_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    draft_dir = output_dir / "draft"
    draft_dir.mkdir(parents=True, exist_ok=True)
    outline_data = {"outline": content_data.get("outline", [])}
    (draft_dir / "outline.json").write_text(json.dumps(outline_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (draft_dir / "content.json").write_text(json.dumps(content_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    valid_contracts, contract_errors = validate_production_bundle(
        system_root=SYS_DIR,
        brief_data=brief_data,
        content_data=content_data,
        brief_revision=1,
    )

    return {
        "output_dir": str(output_dir),
        "brief_file": str(brief_file),
        "content_file": str(content_file),
        "script_file": str(script_file),
        "cadence_file": str(cadence_file),
        "brief_hash": brief_hash,
        "valid_contracts": valid_contracts,
        "contract_errors": contract_errors,
        "hook_score": hook_score_result.score,
        "hook_score_result": hook_score_result,
        "cadence_report": cadence_report,
        "total_images": sum(len(sc.get("images", [])) for sc in content_data["scenes"]),
    }


def build_production_bundle(
    format_profile: str = "short_9x16",
    output_dir: Optional[Path] = None,
    topic_title: Optional[str] = None,
) -> Dict[str, Any]:
    """Top-level convenience builder for ho_so_ky_la."""
    if format_profile == "short_9x16":
        topic = build_topic_9x16(topic_title)
        target_dir = output_dir or (SYS_DIR / "runs" / "ho-so-ky-la-week1-9x16")
    elif format_profile == "long_16x9":
        topic = build_topic_16x9(topic_title)
        target_dir = output_dir or (SYS_DIR / "runs" / "ho-so-ky-la-week1-16x9")
    else:
        raise ValueError(f"Unsupported format_profile: {format_profile}")

    return export_package(topic, target_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description="Builder for Channel ho_so_ky_la production packages.")
    parser.add_argument("--format", choices=["short_9x16", "long_16x9", "dual"], default="short_9x16", help="Format profile to build")
    parser.add_argument("--out-dir", type=Path, default=None, help="Destination directory (default: sys/runs/<job>)")
    parser.add_argument("--topic", type=str, default=None, help="Custom topic title")
    args = parser.parse_args()

    formats = ["short_9x16", "long_16x9"] if args.format == "dual" else [args.format]
    all_ok = True

    for fmt in formats:
        out = args.out_dir if (args.out_dir and args.format != "dual") else None
        res = build_production_bundle(format_profile=fmt, output_dir=out, topic_title=args.topic)
        print("=" * 70)
        print(f"[*] KÊNH 6: HO_SO_KY_LA — ĐÃ XUẤT GÓI: {fmt}")
        print(f"    - Output: {res['output_dir']}")
        print(f"    - Brief SHA256: {res['brief_hash']}")
        print(f"    - Số ảnh Flow: {res['total_images']}")
        print(f"    - Hook score: {res['hook_score']} / 100")
        print(f"    - Hợp đồng Schema 3.0: {'PASS' if res['valid_contracts'] else 'FAIL'}")
        if not res["valid_contracts"]:
            all_ok = False
            for err in res["contract_errors"]:
                print(f"      [!] Lỗi: {err}")
        print("=" * 70)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
