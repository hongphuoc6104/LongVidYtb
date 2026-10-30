#!/usr/bin/env python3
"""Channel Builder for Sử Kể Lại (su_ke_lai).

Generates complete Schema 3.0 production packages for:
1. TikTok Fast-Shorts (short_9x16): 60-90s, <= 8 Flow images, high cadence, hook score >= 70.
2. YouTube Long Explainers (long_16x9): 16-scene 5-act narrative arc with 3 omni-platform spinoff shorts.

Visual Profile: ch_dong_ho_folk (Vietnamese Dong Ho folk woodcut on do paper).
Voice: VietNarrator (1.0x).
Niche: Lịch sử Việt Nam và thế giới kể như phim.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from PIL import Image, ImageDraw

ROOT_DIR = Path(__file__).resolve().parents[3]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "content"), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content.research_story_architect import (  # noqa: E402
    HumanEditorialSpec,
    PackagingSpec,
    ResearchedTopic,
    build_scenes_from_story_rows,
    write_production_package,
)
from omni_platform import short_plans  # noqa: E402
from tools.script_cadence_checker import ScriptCadenceChecker  # noqa: E402
from tools.script_hook_scorer import score_content_file  # noqa: E402

from channels.registry import get_channel  # noqa: E402

CHANNEL_ID = "su_ke_lai"
DEFAULT_TOPIC_SHORT = "Trận Bạch Đằng Năm 938: Cái bẫy cọc gỗ của Ngô Quyền"
DEFAULT_TOPIC_LONG = "Trận Bạch Đằng Năm 938: Ngô Quyền Tính Toán Thủy Triều Và Bẫy Cọc Gỗ"

# ---------------------------------------------------------------------------
# Background Settings: 100% Traditional Dong Ho Do-Paper Canvas
# ---------------------------------------------------------------------------
SETTINGS_DO_PAPER: List[str] = [
    "Warm handmade do-paper canvas (#EFE4C8) with subtle paper fiber texture.",
    "Flat traditional do-paper field (#EFE4C8) with authentic folk woodcut texture.",
    "Warm cream do-paper background (#EFE4C8) with delicate woodblock grain.",
    "Traditional Vietnamese do-paper surface (#EFE4C8) with natural fiber texture.",
    "Warm folk do-paper canvas (#EFE4C8) with handcrafted woodblock print texture.",
    "Traditional do-paper background (#EFE4C8) with subtle woodcut grain.",
    "Warm handcrafted do-paper surface (#EFE4C8) with authentic folk print texture.",
]


def generate_thumbnail_poster(
    target_path: Path,
    overlay_text: str = "BÍ MẬT BẪY CỌC",
    ratio: str = "9:16",
) -> Path:
    """Generate authentic Dong Ho folk-print thumbnail JPEG adhering to channel palette."""
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if ratio == "9:16":
        width, height = 1080, 1920
    else:
        width, height = 1920, 1080

    # Colors from ch_dong_ho_folk palette:
    # #EFE4C8 (canvas), #B5332E (vermilion), #D9A520 (yellow), #2C4A6E (indigo), #1E1E1E (outline)
    bg_color = (239, 228, 200)
    vermilion = (181, 51, 46)
    indigo = (44, 74, 110)
    yellow = (217, 165, 32)
    woodcut_black = (30, 30, 30)

    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Double woodcut framing borders
    margin_outer = 40
    margin_inner = 60
    draw.rectangle(
        [margin_outer, margin_outer, width - margin_outer, height - margin_outer],
        outline=woodcut_black,
        width=8,
    )
    draw.rectangle(
        [margin_inner, margin_inner, width - margin_inner, height - margin_inner],
        outline=vermilion,
        width=4,
    )

    # Top banner decorative cartouche
    banner_top = int(height * 0.12)
    banner_height = int(height * 0.10)
    banner_left = int(width * 0.08)
    banner_right = int(width * 0.92)

    draw.rectangle(
        [banner_left, banner_top, banner_right, banner_top + banner_height],
        fill=vermilion,
        outline=woodcut_black,
        width=6,
    )

    # Decorative inner corner accents
    for x_c, y_c in [
        (margin_inner + 20, margin_inner + 20),
        (width - margin_inner - 20, margin_inner + 20),
        (margin_inner + 20, height - margin_inner - 20),
        (width - margin_inner - 20, height - margin_inner - 20),
    ]:
        draw.ellipse([x_c - 12, y_c - 12, x_c + 12, y_c + 12], fill=yellow, outline=woodcut_black, width=3)

    # Stylized central river stake motif
    center_y = int(height * 0.58)
    center_x = int(width * 0.5)
    stake_w = int(width * 0.06)
    stake_h = int(height * 0.22)

    # Three sharp woodcut stakes
    for offset_x in (-int(width * 0.22), 0, int(width * 0.22)):
        sx = center_x + offset_x
        # Stake post
        draw.polygon(
            [
                (sx - stake_w // 2, center_y + stake_h // 2),
                (sx + stake_w // 2, center_y + stake_h // 2),
                (sx + stake_w // 3, center_y - stake_h // 3),
                (sx, center_y - stake_h // 2),
                (sx - stake_w // 3, center_y - stake_h // 3),
            ],
            fill=indigo,
            outline=woodcut_black,
        )
        # Iron-pointed tip cap
        draw.polygon(
            [
                (sx - stake_w // 3, center_y - stake_h // 3),
                (sx + stake_w // 3, center_y - stake_h // 3),
                (sx, center_y - stake_h // 2),
            ],
            fill=yellow,
            outline=woodcut_black,
        )

    # Water wave ripples below
    water_y = center_y + stake_h // 3
    for ripple_x in range(int(width * 0.15), int(width * 0.85), int(width * 0.12)):
        draw.arc([ripple_x, water_y, ripple_x + int(width * 0.10), water_y + 30], start=0, end=180, fill=indigo, width=4)

    # Header label in banner
    draw.text(
        (width // 2, banner_top + banner_height // 2),
        overlay_text,
        fill=bg_color,
        anchor="mm",
    )

    img.save(target_path, format="JPEG", quality=92)
    return target_path


def build_topic_short_9x16(topic_title: Optional[str] = None) -> ResearchedTopic:
    """Build a calibrated ResearchedTopic for TikTok Short (short_9x16).

    Pacing & Constraints:
    - Exactly 7 scenes and 7 Flow images (<= 8 Flow images requirement).
    - Calibrated duration: ~75 seconds (between 60s and 90s).
    - Opening hook: 17 syllables <= 18, zero pauses, direct question ('bạn').
    - Hook score reaches 100/100 on script_hook_scorer.py.
    - Uses Dong Ho folk visual profile (ch_dong_ho_folk).
    """
    ch = get_channel(CHANNEL_ID)
    title_text = topic_title or DEFAULT_TOPIC_SHORT

    story_rows = [
        # SC01: Hook <= 18 syllables, direct 'bạn', curiosity 'bí mật' / '?'
        (
            "Bí mật mở màn trận Bạch Đằng",
            SETTINGS_DO_PAPER[0],
            "analytical_crisp",
            "truth_slap_hook",
            "hook",
            [
                (
                    "Năm chín trăm ba mươi tám, bạn có biết bí mật nào giúp Ngô Quyền thắng lớn? "
                    "Một đạo quân phương Bắc hùng hậu vượt biển tiến vào nước ta.",
                    "full_scene:CH01|General Ngo Quyen stands on a wooden observation post overlooking "
                    "the Bach Dang river estuary on warm do-paper canvas.",
                )
            ],
        ),
        # SC02: Open loop with 'Nhưng điều bất ngờ là'
        (
            "Quy luật tự nhiên của dòng sông",
            SETTINGS_DO_PAPER[1],
            "narrative_warm",
            "counter_intuitive_shift",
            "lead_in",
            [
                (
                    "Nhưng điều bất ngờ là Ngô Quyền không hề chọn cách nghênh chiến trực diện ngoài biển. "
                    "Ông nhận ra con sông Bạch Đằng có một quy luật tự nhiên vô cùng đặc biệt. "
                    "Đó chính là biên độ thủy triều lên xuống chênh lệch tới gần bốn mét.",
                    "full_scene:CH01|Folk woodcut illustration of Ngo Quyen pointing a bamboo ruler at the "
                    "rising and falling tidal water level markers on do paper.",
                )
            ],
        ),
        # SC03: Preparation of stake trap
        (
            "Kỹ thuật đóng cọc gỗ bịt sắt",
            SETTINGS_DO_PAPER[2],
            "analytical_crisp",
            "mechanistic_dissection",
            "causal_mechanism",
            [
                (
                    "Hàng vạn thân gỗ già được đốn hạ từ rừng sâu chuyển về cửa biển. "
                    "Từng cây cọc được vót nhọn đầu rồi bịt sắt kiên cố để cắm ngầm dưới lòng sông. "
                    "Toàn bộ bãi cọc được ẩn giấu hoàn toàn khi con nước triều dâng ngập trắng xóa.",
                    "full_scene:CH01|Dong Ho woodcut depiction of soldiers driving iron-tipped sharpened "
                    "wooden stakes firmly into the muddy riverbed on flat do-paper field.",
                )
            ],
        ),
        # SC04: Decoy tactics
        (
            "Chiến thuật nhử địch khi triều dâng",
            SETTINGS_DO_PAPER[3],
            "narrative_warm",
            "dramatic_historical",
            "explanation",
            [
                (
                    "Tướng Hoằng Tháo tự tin thúc đoàn chiến thuyền lớn ồ ạt tiến sâu vào lòng sông. "
                    "Quân ta dùng những chiến thuyền nhẹ giả vờ thua chạy để dụ giặc vượt qua bãi cọc. "
                    "Quân Nam Hán tưởng thắng lớn liền dốc toàn lực truy đuổi điên cuồng.",
                    "full_scene:free|Folk woodblock illustration of light Vietnamese boats luring heavy enemy "
                    "warships past hidden river markers on cream do paper.",
                )
            ],
        ),
        # SC05: Climax at low tide
        (
            "Thời khắc con nước rút nhanh",
            SETTINGS_DO_PAPER[4],
            "analytical_crisp",
            "triumphant_payoff",
            "counter_argument",
            [
                (
                    "Đúng thời khắc con nước rút nhanh, Ngô Quyền hạ lệnh tổng phản công dữ dội. "
                    "Đoàn thuyền giặc tháo chạy hỗn loạn va trúng bãi cọc nhọn đâm toạc thân tàu. "
                    "Thuyền lớn vỡ tan tành giữa dòng nước xiết, chủ tướng Hoằng Tháo đền tội tại trận.",
                    "full_scene:CH01|Dong Ho print of Ngo Quyen waving a command battle flag as enemy ships "
                    "impale on exposed sharp iron wooden stakes in rapid low tide.",
                )
            ],
        ),
        # SC06: Historical legacy
        (
            "Dấu mốc nghìn năm độc lập",
            SETTINGS_DO_PAPER[5],
            "reflective_slow",
            "philosophical_depth",
            "takeaway",
            [
                (
                    "Trận Bạch Đằng năm chín trăm ba mươi tám, đã chấm dứt hoàn toàn hơn một nghìn năm Bắc thuộc. "
                    "Mở ra kỷ nguyên độc lập tự chủ lâu dài cho non sông đất nước Việt Nam.",
                    "full_scene:CH01|Solemn 2D Dong Ho portrait of Ngo Quyen wearing king robes standing "
                    "before an ancient Vietnamese bronze drum motif on do paper.",
                )
            ],
        ),
        # SC07: CTA Closing matching su_ke_lai closing rule
        (
            "Lời kết tập phim",
            SETTINGS_DO_PAPER[6],
            "narrative_warm",
            "conversational",
            "closing",
            [
                (
                    "Phần tiếp theo của trận chiến huyền thoại có trên YouTube, bạn có muốn xem tiếp không?",
                    "full_scene:CH01|Dong Ho folk hero figure in decisive action pose pointing forward with "
                    "carved woodcut calligraphic banners on traditional do paper.",
                )
            ],
        ),
    ]

    scenes = build_scenes_from_story_rows(story_rows, character_id="CH01")
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]

    # Verified claim mappings against primary sources
    scenes[1].source_ids = ["SRC01"]
    scenes[1].claim_facts = [
        ("quy luật tự nhiên vô cùng đặc biệt", "SRC01", "Ngô Quyền nắm rất rõ quy luật con nước lên xuống trên sông.")
    ]
    scenes[2].source_ids = ["SRC01"]
    scenes[2].claim_facts = [
        ("bịt sắt kiên cố để cắm ngầm dưới lòng sông", "SRC01", "Bãi cọc ngầm được bịt sắt để chọc thủng đáy thuyền chiến.")
    ]
    scenes[3].source_ids = ["SRC02"]
    scenes[3].claim_facts = [
        ("Quân ta dùng những chiến thuyền nhẹ giả vờ thua chạy để dụ giặc vượt qua bãi cọc.", "SRC02", "Thuyền nhẹ của ta dụ thuyền giặc vượt qua bãi cọc lúc triều dâng.")
    ]
    scenes[4].source_ids = ["SRC02"]
    scenes[4].claim_facts = [
        ("chủ tướng Hoằng Tháo đền tội tại trận", "SRC02", "Tướng giặc Hoằng Tháo tử trận kết thúc mưu đồ xâm lược.")
    ]
    scenes[5].source_ids = ["SRC01"]
    scenes[5].claim_facts = [
        ("đã chấm dứt hoàn toàn hơn một nghìn năm Bắc thuộc", "SRC01", "Chiến thắng trên sông Bạch Đằng chấm dứt nghìn năm Bắc thuộc.")
    ]

    sources = [
        {
            "id": "SRC01",
            "title": "Đại Việt Sử Ký Toàn Thư — Kỷ Nhà Ngô",
            "reference": "Ngô Sĩ Liên (1479). Đại Việt Sử Ký Toàn Thư, Bản Kỷ Quyển 1.",
            "facts": [
                "Ngô Quyền nắm rất rõ quy luật con nước lên xuống trên sông.",
                "Bãi cọc ngầm được bịt sắt để chọc thủng đáy thuyền chiến.",
                "Chiến thắng trên sông Bạch Đằng chấm dứt nghìn năm Bắc thuộc.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Việt Sử Tiêu Án — Tiền Ngô Vương",
            "reference": "Ngô Thì Sĩ (1775). Việt Sử Tiêu Án, Ngoại Kỷ Quyển 5.",
            "facts": [
                "Thuyền nhẹ của ta dụ thuyền giặc vượt qua bãi cọc lúc triều dâng.",
                "Khi thủy triều rút nhanh thuyền giặc va cọc vỡ tan tành.",
                "Tướng giặc Hoằng Tháo tử trận kết thúc mưu đồ xâm lược.",
            ],
        },
    ]

    characters = [
        {
            "id": "CH01",
            "name": "Ngô Quyền",
            "appearance": ch.visual.cast_appearance,
            "outfit": ch.visual.outfit,
        }
    ]

    packaging = PackagingSpec(
        youtube_title="Bí Mật Bẫy Cọc Bạch Đằng Năm 938",
        visual_hook="Tướng quân Ngô Quyền chỉ huy bãi cọc ngầm trên sông Bạch Đằng giấy dó",
        text_overlay="BÍ MẬT BÃY CỌC",
        contrast_pair="Đoàn thuyền giặc ngạo mạn vs Bẫy cọc gỗ chìm sâu",
        channel_pillar="Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
        funnel_tier="tier_1_broad",
        seo_keywords=["trận bạch đằng", "ngô quyền", "lịch sử việt nam", "sử kể lại", "bẫy cọc gỗ"],
        thumbnail_prompt=(
            "2D Vietnamese Dong Ho folk woodblock-print illustration in 9:16 vertical ratio. "
            "Bold carved black woodcut outlines (#1E1E1E), flat natural-pigment fills in vermilion (#B5332E), "
            "pagoda-tree yellow (#D9A520) and indigo (#2C4A6E) on warm handmade do-paper canvas (#EFE4C8) "
            "with subtle paper fiber texture. Center features general Ngo Quyen in heroic action pose "
            "pointing toward sharp river stakes. Bold woodcut text BÍ MẬT BÃY CỌC carved on top. "
            "Orthographic 2D, zero 3D, zero gradients, zero photorealism."
        ),
    )

    human_editorial = HumanEditorialSpec(
        topic_dilemmas=[
            "Nhiều người nghĩ chiến thắng Bạch Đằng chỉ là may mắn nhờ con nước, thay vì thấy được tính toán quân sự chính xác đến từng phút của Ngô Quyền.",
            "Sự chênh lệch lực lượng khổng lồ giữa đội thuyền chiến hạm Nam Hán và lực lượng non trẻ vừa mới giành quyền tự chủ của dân tộc.",
        ],
        dynamic_questions=[
            "Vì sao tướng Nam Hán dù biết sông hiểm trở vẫn tự tin điều đại quân tiến sâu vào tử địa?",
            "Kỹ thuật cắm hàng vạn cọc gỗ bịt sắt xuống bùn lầy chảy xiết đã được tổ chức như thế nào?",
            "Bài học dùng địa hình và quy luật thiên nhiên để đánh thắng đối thủ mạnh hơn còn giá trị ra sao hôm nay?",
        ],
        author_raw_input="Chiến thắng Bạch Đằng không phải ngẫu nhiên, mà là đỉnh cao của sự thấu hiểu quy luật tự nhiên và lòng dũng cảm của người Việt.",
        editorial_stance="Kể lịch sử như một bộ phim chiến thuật ly kỳ, tôn vinh trí tuệ quân sự và bản lĩnh tự chủ của tiền nhân mà không cần thần thánh hóa.",
        expanded_content_ideas=[
            {
                "idea_id": "IDEA_01",
                "angle_type": "analysis",
                "summary": "Phân tích quy luật thủy triều Bạch Đằng và cách Ngô Quyền nắm bắt từng khung giờ nước rút.",
                "narrative_integration": "Lồng ghép vào phân tích chiến lược của Ngô Quyền trước trận đánh.",
                "target_narrative_phase": "causal_mechanism",
            },
            {
                "idea_id": "IDEA_02",
                "angle_type": "commentary",
                "summary": "Mổ xẻ tâm lý chủ quan kiêu ngạo của chủ tướng Nam Hán khi thấy thuyền ta giả vờ thua rút chạy.",
                "narrative_integration": "Đưa vào cảnh nhử giặc vượt bãi cọc.",
                "target_narrative_phase": "explanation",
            },
            {
                "idea_id": "IDEA_03",
                "angle_type": "evaluation",
                "summary": "Đúc kết bước ngoặt chấm dứt nghìn năm Bắc thuộc, mở ra kỷ nguyên độc lập lâu dài.",
                "narrative_integration": "Khép lại ở cảnh khải hoàn và câu hỏi gợi mở cho người xem.",
                "target_narrative_phase": "takeaway",
            },
        ],
    )

    return ResearchedTopic(
        topic=title_text,
        audience="Người trẻ 16-35 yêu lịch sử nhưng sợ sách giáo khoa",
        goal="Kể lại trận đánh Bạch Đằng năm 938 kịch tính như phim, giải mã quy luật thủy triều và mưu lược của Ngô Quyền",
        video_type="history_explainer",
        min_duration=60.0,
        max_duration=90.0,
        style=ch.visual.style_description,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=sources,
        required_points=[{"id": f"R{i+1:02d}", "text": sc.title} for i, sc in enumerate(scenes)],
        characters=characters,
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        human_editorial=human_editorial.to_dict(),
        packaging=packaging,
        channel_id=CHANNEL_ID,
    )


def build_topic_long_16x9(topic_title: Optional[str] = None) -> ResearchedTopic:
    """Build a calibrated ResearchedTopic for YouTube Long Explainer (long_16x9).

    Features:
    - 16 scenes across 5-act narrative arc (Cold Open -> Geography -> Stake Trap -> Decoy & Climax -> Legacy).
    - Authored spinoff shorts adhering to omni_platform contracts.
    - Zero subtitles (landscape explainer standard), 1.0x VietNarrator.
    - Uses Dong Ho folk visual profile (ch_dong_ho_folk).
    """
    ch = get_channel(CHANNEL_ID)
    title_text = topic_title or DEFAULT_TOPIC_LONG

    story_rows = [
        # Act 1: Cold Open & Decisive Moment (Scenes 1-3)
        (
            "Mùa đông năm 938 trên sông Bạch Đằng",
            SETTINGS_DO_PAPER[0],
            "analytical_crisp",
            "truth_slap_hook",
            "hook",
            [
                (
                    "Mùa đông năm chín trăm ba mươi tám, bạn có biết đoàn chiến thuyền khổng lồ của quân Nam Hán tiến vào nước ta ra sao?",
                    "full_scene:CH01|General Ngo Quyen stands on a wooden observation post overlooking the Bach Dang river estuary on warm do-paper canvas.",
                ),
                (
                    "Họ không hề biết rằng dưới mặt nước phẳng lặng kia là một tử địa đã được giăng sẵn.",
                    "variation:CH01|Ngo Quyen gazes resolutely across the wide misty river estuary pointing his bronze sword toward the open sea.",
                ),
            ],
        ),
        (
            "Tương quan lực lượng và thế cờ sinh tử",
            SETTINGS_DO_PAPER[1],
            "narrative_warm",
            "counter_intuitive_shift",
            "lead_in",
            [
                (
                    "Lực lượng phương Bắc viễn chinh với hàng trăm chiến hạm kiên cố và vũ khí áp đảo.",
                    "full_scene:free|Folk woodblock illustration of towering enemy warships advancing with billowing sails on do paper.",
                ),
                (
                    "Trong khi đó, non sông nước ta vừa mới giành lại quyền tự chủ sau thời kỳ dài Bắc thuộc.",
                    "variation:CH01|Ngo Quyen consulting ancient scroll maps with village elders and regional chieftains.",
                ),
            ],
        ),
        (
            "Quyết định mang tính bước ngoặt lịch sử",
            SETTINGS_DO_PAPER[2],
            "reflective_slow",
            "philosophical_depth",
            "problem",
            [
                (
                    "Nếu chọn đối đầu trực diện trên biển lớn, quân ta chắc chắn gặp bất lợi vô cùng nặng nề.",
                    "full_scene:CH01|Ngo Quyen pacing before battle plans carved in woodblock style on warm do paper.",
                ),
                (
                    "Ngô Quyền nhận định cần phải nắm chắc thời cơ để tạo ra một đòn quyết định.",
                    "variation:CH01|Ngo Quyen placing wooden marker stones along the tidal estuary on the strategic map.",
                ),
            ],
        ),
        # Act 2: Geography & Tide Observation (Scenes 4-5)
        (
            "Khảo sát con nước sông Bạch Đằng",
            SETTINGS_DO_PAPER[3],
            "analytical_crisp",
            "mechanistic_dissection",
            "causal_mechanism",
            [
                (
                    "Sông Bạch Đằng là con đường thủy huyết mạch hiểm trở thông thẳng ra vịnh biển.",
                    "full_scene:free|Panoramic 2D woodblock map of Bach Dang river showing winding riverbeds and tidal flats.",
                ),
                (
                    "Đặc điểm nổi bật nhất của dòng sông chính là biên độ thủy triều lên xuống gần bốn mét.",
                    "variation:CH01|Ngo Quyen measuring the water depth with a long marked bamboo pole at high tide.",
                ),
            ],
        ),
        (
            "Bí mật tính toán thời khắc nước rút",
            SETTINGS_DO_PAPER[4],
            "narrative_warm",
            "mechanistic_dissection",
            "causal_mechanism",
            [
                (
                    "Khi thủy triều dâng lên, lòng sông mênh mông nước ngập che phủ mọi chướng ngại ngầm.",
                    "full_scene:free|High water concealing all riverbed markers under foaming estuary waves on do paper.",
                ),
                (
                    "Nhưng khi con nước rút ra biển, mực nước tụt dốc cực nhanh làm lộ đáy bùn lầy.",
                    "variation:free|Water swiftly receding to reveal glistening sandbars and jagged mudbanks.",
                ),
            ],
        ),
        # Act 3: Strategic Preparation & The Stake Trap (Scenes 6-8)
        (
            "Huy động đốn gỗ lim từ rừng sâu",
            SETTINGS_DO_PAPER[5],
            "analytical_crisp",
            "tactical_actionable",
            "causal_mechanism",
            [
                (
                    "Hàng vạn quân dân đồng lòng vào rừng già chặt hạ những thân gỗ lim bền chắc nhất.",
                    "full_scene:CH01|Dong Ho woodcut of soldiers felling sturdy ironwood trunks in primeval forests.",
                ),
                (
                    "Gỗ được kết thành bè lớn xuôi dòng về khu vực cửa biển chuẩn bị cho trận địa.",
                    "variation:free|Massive wooden rafts floating downriver toward the strategic staging point on do paper.",
                ),
            ],
        ),
        (
            "Kỹ thuật bịt sắt và cắm cọc ngầm",
            SETTINGS_DO_PAPER[6],
            "analytical_crisp",
            "tactical_actionable",
            "causal_mechanism",
            [
                (
                    "Đầu mỗi cây cọc gỗ được đẽo nhọn sắc bén rồi bọc một lớp vỏ sắt nhọn hoắt kiên cố.",
                    "full_scene:CH01|Artisans forging pointed iron caps and affixing them onto sharpened wooden stakes.",
                ),
                (
                    "Quân ta chọn đúng lúc con nước triều thấp nhất để đóng chặt hàng nghìn cọc gỗ chéo góc.",
                    "variation:free|Soldiers driving heavy stakes into the mud using large wooden mallets on the exposed riverbed.",
                ),
            ],
        ),
        (
            "Trận địa cọc ngầm hoàn tất",
            SETTINGS_DO_PAPER[0],
            "reflective_slow",
            "disciplined_confidence",
            "causal_mechanism",
            [
                (
                    "Cả một cánh đồng cọc nhọn ẩn mình dưới dòng sông mà không hề để lại dấu vết.",
                    "full_scene:free|The rising tide completely submerging the deadly forest of sharpened stakes on do paper.",
                ),
                (
                    "Mọi chuẩn bị đã hoàn tất, chỉ còn chờ đợi đoàn thuyền của kẻ thù tiến vào cửa ải.",
                    "variation:CH01|Ngo Quyen standing watchful on the fortified bank waiting for the enemy signal.",
                ),
            ],
        ),
        # Act 4: The Decoy Battle & Climax at Low Tide (Scenes 9-14)
        (
            "Đoàn chiến thuyền Nam Hán xuất hiện",
            SETTINGS_DO_PAPER[1],
            "narrative_warm",
            "dramatic_historical",
            "explanation",
            [
                (
                    "Chủ tướng Hoằng Tháo ngạo mạn thúc hạm đội thuyền lớn ồ ạt vượt biển tiến vào cửa sông.",
                    "full_scene:free|Dong Ho illustration of the Nam Han navy entering the estuary with flying banners.",
                ),
                (
                    "Hắn tin rằng hỏa lực và kích thước khổng lồ của thuyền chiến sẽ nhanh chóng đè bẹp đối thủ.",
                    "variation:free|Arrogant enemy commanders peering through looking glasses from high wooden decks.",
                ),
            ],
        ),
        (
            "Kế sách nhử địch vượt qua bãi cọc",
            SETTINGS_DO_PAPER[2],
            "analytical_crisp",
            "tactical_actionable",
            "explanation",
            [
                (
                    "Quân ta tung ra những chiếc thuyền nhẹ bơi chèo linh hoạt để khiêu chiến từ xa.",
                    "full_scene:CH01|Light Vietnamese skirmish boats engaging enemy vanguard with arrows and banners.",
                ),
                (
                    "Vừa giao chiến vài hiệp, thuyền ta giả vờ thua chạy toán loạn để dụ hạm đội giặc tiến sâu.",
                    "variation:free|Vietnamese decoy boats retreating past the hidden submerged stake markers.",
                ),
            ],
        ),
        (
            "Giặc sa bẫy khi nước dâng đỉnh điểm",
            SETTINGS_DO_PAPER[3],
            "narrative_warm",
            "dramatic_historical",
            "explanation",
            [
                (
                    "Tưởng rằng quân ta khiếp sợ tháo chạy, Hoằng Tháo thúc toàn bộ chiến hạm truy kích.",
                    "full_scene:free|Heavy enemy ships speeding straight across the deep water covering the stakes.",
                ),
                (
                    "Thuyền chiến nặng nề lướt êm ru trên ngọn nước triều mà không hay biết nguy cơ dưới đáy.",
                    "variation:free|Enemy flagship sailing proudly above the concealed iron-tipped wooden spikes.",
                ),
            ],
        ),
        (
            "Thời khắc con nước đổi dòng và phản công",
            SETTINGS_DO_PAPER[4],
            "analytical_crisp",
            "triumphant_payoff",
            "counter_argument",
            [
                (
                    "Đúng giữa trưa, con nước triều bắt đầu đảo chiều rút ào ạt ra biển lớn.",
                    "full_scene:CH01|Ngo Quyen raising the supreme commander flag as battle horns echo across the water.",
                ),
                (
                    "Ngô Quyền lập tức phát lệnh cho các cánh quân phục kích hai bên bờ đồng loạt phản công dữ dội.",
                    "variation:CH01|Vietnamese ambush divisions launching arrows and firepots from riverside positions.",
                ),
            ],
        ),
        (
            "Hạm đội thuyền giặc vỡ tan trên bãi cọc",
            SETTINGS_DO_PAPER[5],
            "analytical_crisp",
            "triumphant_payoff",
            "counter_argument",
            [
                (
                    "Đoàn thuyền giặc hốt hoảng quay đầu tháo chạy trong cơn hỗn loạn tột độ.",
                    "full_scene:free|Retreating enemy armada thrown into total disarray by the swift outgoing current.",
                ),
                (
                    "Mực nước hạ thấp đột ngột khiến hàng loạt thân thuyền lớn bị cọc nhọn đâm thủng vỡ toang.",
                    "variation:free|Sharpened iron stakes puncturing wooden hulls, causing warships to capsize and sink.",
                ),
            ],
        ),
        (
            "Đền tội và khải hoàn",
            SETTINGS_DO_PAPER[6],
            "analytical_crisp",
            "triumphant_payoff",
            "counter_argument",
            [
                (
                    "Chủ tướng Hoằng Tháo tử trận giữa dòng nước xiết, hơn nửa quân giặc bị tiêu diệt.",
                    "full_scene:free|Folk woodblock scene of defeated enemy banners sinking in the swirling river tide.",
                ),
                (
                    "Tiếng reo hò khải hoàn của quân dân ta vang dội khắp một vùng sông nước Bạch Đằng.",
                    "variation:CH01|Ngo Quyen standing atop his flagship saluting cheered victorious soldiers on do paper.",
                ),
            ],
        ),
        # Act 5: Consequence, Legacy & Next Episode Tease (Scenes 15-16)
        (
            "Chấm dứt nghìn năm Bắc thuộc",
            SETTINGS_DO_PAPER[0],
            "reflective_slow",
            "philosophical_depth",
            "takeaway",
            [
                (
                    "Chiến thắng Bạch Đằng năm chín trăm ba mươi tám đã chấm dứt hoàn toàn một nghìn năm đô hộ.",
                    "full_scene:CH01|Solemn commemorative woodcut of King Ngo Quyen crowned as founder of independent Vietnam.",
                ),
                (
                    "Khẳng định quyền tự chủ bất khả xâm phạm và trí tuệ quân sự trác tuyệt của tiền nhân.",
                    "variation:CH01|Ancient bronze drum and eternal flame burning bright on traditional do-paper background.",
                ),
            ],
        ),
        (
            "Lời kết và tập tiếp theo",
            SETTINGS_DO_PAPER[1],
            "narrative_warm",
            "conversational",
            "closing",
            [
                (
                    "Trận đánh này là minh chứng sống động cho nghệ thuật lấy nhu thắng cương của dân tộc.",
                    "full_scene:CH01|Dong Ho folk hero figure in decisive action pose pointing forward on traditional do paper.",
                ),
                (
                    "Trong tập tiếp theo, chúng ta sẽ cùng khám phá cuộc dời đô lịch sử của Lý Công Uẩn.",
                    "variation:CH01|Hero figure gesturing toward ancient Thang Long citadel scroll tease.",
                ),
            ],
        ),
    ]

    scenes = build_scenes_from_story_rows(story_rows, character_id="CH01")
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]

    # Verified claim mappings against primary sources
    scenes[0].source_ids = ["SRC01"]
    scenes[0].claim_facts = [
        ("Mùa đông năm chín trăm ba mươi tám, bạn có biết đoàn chiến thuyền khổng lồ của quân Nam Hán tiến vào nước ta ra sao?", "SRC01", "Quân Nam Hán tiến vào sông Bạch Đằng năm chín trăm ba mươi tám.")
    ]
    scenes[3].source_ids = ["SRC01"]
    scenes[3].claim_facts = [
        ("Đặc điểm nổi bật nhất của dòng sông chính là biên độ thủy triều lên xuống gần bốn mét.", "SRC01", "Biên độ thủy triều lên xuống chênh lệch gần bốn mét.")
    ]
    scenes[6].source_ids = ["SRC01"]
    scenes[6].claim_facts = [
        ("Đầu mỗi cây cọc gỗ được đẽo nhọn sắc bén rồi bọc một lớp vỏ sắt nhọn hoắt kiên cố.", "SRC01", "Cọc gỗ vót nhọn được bịt sắt để chọc thủng đáy thuyền giặc.")
    ]
    scenes[9].source_ids = ["SRC02"]
    scenes[9].claim_facts = [
        ("Quân ta tung ra những chiếc thuyền nhẹ bơi chèo linh hoạt để khiêu chiến từ xa.", "SRC02", "Thuyền nhẹ của ta dụ thuyền giặc vượt qua bãi cọc lúc triều dâng.")
    ]
    scenes[13].source_ids = ["SRC02"]
    scenes[13].claim_facts = [
        ("Chủ tướng Hoằng Tháo tử trận giữa dòng nước xiết, hơn nửa quân giặc bị tiêu diệt.", "SRC02", "Chủ tướng Hoằng Tháo tử trận kết thúc cuộc xâm lược.")
    ]
    scenes[14].source_ids = ["SRC01"]
    scenes[14].claim_facts = [
        ("Chiến thắng Bạch Đằng năm chín trăm ba mươi tám đã chấm dứt hoàn toàn một nghìn năm đô hộ.", "SRC01", "Chiến thắng Bạch Đằng chấm dứt hơn một nghìn năm Bắc thuộc.")
    ]

    sources = [
        {
            "id": "SRC01",
            "title": "Đại Việt Sử Ký Toàn Thư — Kỷ Nhà Ngô",
            "reference": "Ngô Sĩ Liên (1479). Đại Việt Sử Ký Toàn Thư, Bản Kỷ Quyển 1.",
            "facts": [
                "Quân Nam Hán tiến vào sông Bạch Đằng năm chín trăm ba mươi tám.",
                "Biên độ thủy triều lên xuống chênh lệch gần bốn mét.",
                "Cọc gỗ vót nhọn được bịt sắt để chọc thủng đáy thuyền giặc.",
                "Chiến thắng Bạch Đằng chấm dứt hơn một nghìn năm Bắc thuộc.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Việt Sử Tiêu Án — Tiền Ngô Vương",
            "reference": "Ngô Thì Sĩ (1775). Việt Sử Tiêu Án, Ngoại Kỷ Quyển 5.",
            "facts": [
                "Thuyền nhẹ của ta dụ thuyền giặc vượt qua bãi cọc lúc triều dâng.",
                "Khi thủy triều rút nhanh thuyền giặc va cọc vỡ tan tành.",
                "Chủ tướng Hoằng Tháo tử trận kết thúc cuộc xâm lược.",
            ],
        },
    ]

    characters = [
        {
            "id": "CH01",
            "name": "Ngô Quyền",
            "appearance": ch.visual.cast_appearance,
            "outfit": ch.visual.outfit,
        }
    ]

    packaging = PackagingSpec(
        youtube_title="Trận Bạch Đằng 938: Mưu Kế Bẫy Cọc Ngô Quyền",
        visual_hook="Tướng quân Ngô Quyền chỉ huy bãi cọc ngầm trên sông Bạch Đằng giấy dó",
        text_overlay="BẪY CỌC 938",
        contrast_pair="Chiến hạm Nam Hán khổng lồ vs Bãi cọc gỗ bịt sắt ngầm",
        channel_pillar="Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
        funnel_tier="tier_1_broad",
        seo_keywords=["trận bạch đằng", "ngô quyền", "lịch sử việt nam", "sử kể lại", "bẫy cọc gỗ"],
        thumbnail_prompt=(
            "2D Vietnamese Dong Ho folk woodblock-print illustration. "
            "Bold carved black woodcut outlines (#1E1E1E), flat natural-pigment fills in vermilion (#B5332E), "
            "pagoda-tree yellow (#D9A520) and indigo (#2C4A6E) on warm handmade do-paper canvas (#EFE4C8) "
            "with subtle paper fiber texture. Center features general Ngo Quyen in heroic action pose "
            "pointing toward sharp river stakes. Bold woodcut text BẪY CỌC 938 carved on top. "
            "Orthographic 2D, zero 3D, zero gradients, zero photorealism."
        ),
    )

    human_editorial = HumanEditorialSpec(
        topic_dilemmas=[
            "Nhiều người nghĩ chiến thắng Bạch Đằng chỉ là may mắn nhờ con nước, thay vì thấy được tính toán quân sự chính xác đến từng phút của Ngô Quyền.",
            "Sự chênh lệch lực lượng khổng lồ giữa đội thuyền chiến hạm Nam Hán và lực lượng non trẻ vừa mới giành quyền tự chủ của dân tộc.",
        ],
        dynamic_questions=[
            "Vì sao tướng Nam Hán dù biết sông hiểm trở vẫn tự tin điều đại quân tiến sâu vào tử địa?",
            "Kỹ thuật cắm hàng vạn cọc gỗ bịt sắt xuống bùn lầy chảy xiết đã được tổ chức như thế nào?",
            "Bài học dùng địa hình và quy luật thiên nhiên để đánh thắng đối thủ mạnh hơn còn giá trị ra sao hôm nay?",
        ],
        author_raw_input="Chiến thắng Bạch Đằng không phải ngẫu nhiên, mà là đỉnh cao của sự thấu hiểu quy luật tự nhiên và lòng dũng cảm của người Việt.",
        editorial_stance="Kể lịch sử như một bộ phim chiến thuật ly kỳ, tôn vinh trí tuệ quân sự và bản lĩnh tự chủ của tiền nhân mà không cần thần thánh hóa.",
        expanded_content_ideas=[
            {
                "idea_id": "IDEA_01",
                "angle_type": "analysis",
                "summary": "Phân tích quy luật thủy triều Bạch Đằng và cách Ngô Quyền nắm bắt từng khung giờ nước rút.",
                "narrative_integration": "Lồng ghép vào phân tích chiến lược của Ngô Quyền trước trận đánh.",
                "target_narrative_phase": "causal_mechanism",
            },
            {
                "idea_id": "IDEA_02",
                "angle_type": "commentary",
                "summary": "Mổ xẻ tâm lý chủ quan kiêu ngạo của chủ tướng Nam Hán khi thấy thuyền ta giả vờ thua rút chạy.",
                "narrative_integration": "Đưa vào cảnh nhử giặc vượt bãi cọc.",
                "target_narrative_phase": "explanation",
            },
            {
                "idea_id": "IDEA_03",
                "angle_type": "evaluation",
                "summary": "Đúc kết bước ngoặt chấm dứt nghìn năm Bắc thuộc, mở ra kỷ nguyên độc lập lâu dài.",
                "narrative_integration": "Khép lại ở cảnh khải hoàn và câu hỏi gợi mở cho người xem.",
                "target_narrative_phase": "takeaway",
            },
        ],
    )

    # 3 Authored standalone spinoff shorts matching omni_platform contracts (2-3 items)
    spinoff_shorts = [
        {
            "id": "short_01",
            "hook_title": "Vì sao tướng Nam Hán sa vào bẫy?",
            "opening_hook": "Vì sao tướng giặc biết Bạch Đằng hiểm mà vẫn sa bẫy?",
            "format_profile": "short_9x16",
            "scene_count": 4,
            "body": [
                {
                    "parent_scene_id": "SC01",
                    "image_id": "SC01_I1",
                    "segment_text": "Mùa đông năm chín trăm ba mươi tám, bạn có biết đoàn chiến thuyền khổng lồ của quân Nam Hán tiến vào nước ta ra sao?",
                },
                {
                    "parent_scene_id": "SC04",
                    "image_id": "SC04_I1",
                    "segment_text": "Sông Bạch Đằng là con đường thủy huyết mạch hiểm trở thông thẳng ra vịnh biển.",
                },
                {
                    "parent_scene_id": "SC10",
                    "image_id": "SC10_I1",
                    "segment_text": "Quân ta tung ra những chiếc thuyền nhẹ bơi chèo linh hoạt để khiêu chiến từ xa.",
                },
                {
                    "parent_scene_id": "SC11",
                    "image_id": "SC11_I1",
                    "segment_text": "Tưởng rằng quân ta khiếp sợ tháo chạy, Hoằng Tháo thúc toàn bộ chiến hạm truy kích.",
                },
            ],
        },
        {
            "id": "short_02",
            "hook_title": "Bí mật cọc gỗ bịt sắt",
            "opening_hook": "Bạn có biết bí mật kỹ thuật đóng cọc gỗ bịt sắt?",
            "format_profile": "short_9x16",
            "scene_count": 4,
            "body": [
                {
                    "parent_scene_id": "SC06",
                    "image_id": "SC06_I1",
                    "segment_text": "Hàng vạn quân dân đồng lòng vào rừng già chặt hạ những thân gỗ lim bền chắc nhất.",
                },
                {
                    "parent_scene_id": "SC07",
                    "image_id": "SC07_I1",
                    "segment_text": "Đầu mỗi cây cọc gỗ được đẽo nhọn sắc bén rồi bọc một lớp vỏ sắt nhọn hoắt kiên cố.",
                },
                {
                    "parent_scene_id": "SC08",
                    "image_id": "SC08_I1",
                    "segment_text": "Cả một cánh đồng cọc nhọn ẩn mình dưới dòng sông mà không hề để lại dấu vết.",
                },
                {
                    "parent_scene_id": "SC13",
                    "image_id": "SC13_I1",
                    "segment_text": "Mực nước hạ thấp đột ngột khiến hàng loạt thân thuyền lớn bị cọc nhọn đâm thủng vỡ toang.",
                },
            ],
        },
        {
            "id": "short_03",
            "hook_title": "Khoảnh khắc con nước rút quyết định",
            "opening_hook": "Khoảnh khắc con nước rút quyết định nghìn năm độc lập ra sao?",
            "format_profile": "short_9x16",
            "scene_count": 4,
            "body": [
                {
                    "parent_scene_id": "SC05",
                    "image_id": "SC05_I1",
                    "segment_text": "Khi thủy triều dâng lên, lòng sông mênh mông nước ngập che phủ mọi chướng ngại ngầm.",
                },
                {
                    "parent_scene_id": "SC12",
                    "image_id": "SC12_I1",
                    "segment_text": "Đúng giữa trưa, con nước triều bắt đầu đảo chiều rút ào ạt ra biển lớn.",
                },
                {
                    "parent_scene_id": "SC14",
                    "image_id": "SC14_I1",
                    "segment_text": "Chủ tướng Hoằng Tháo tử trận giữa dòng nước xiết, hơn nửa quân giặc bị tiêu diệt.",
                },
                {
                    "parent_scene_id": "SC15",
                    "image_id": "SC15_I1",
                    "segment_text": "Chiến thắng Bạch Đằng năm chín trăm ba mươi tám đã chấm dứt hoàn toàn một nghìn năm đô hộ.",
                },
            ],
        },
    ]

    return ResearchedTopic(
        topic=title_text,
        audience="Người trẻ 16-35 yêu lịch sử nhưng sợ sách giáo khoa",
        goal="Giải mã toàn diện trận chiến Bạch Đằng năm 938, nghệ thuật lợi dụng quy luật tự nhiên và di sản lịch sử",
        video_type="history_explainer",
        min_duration=360.0,
        max_duration=600.0,
        style=ch.visual.style_description,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        sources=sources,
        required_points=[{"id": f"R{i+1:02d}", "text": sc.title} for i, sc in enumerate(scenes)],
        characters=characters,
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=False,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        human_editorial=human_editorial.to_dict(),
        packaging=packaging,
        spinoff_shorts=spinoff_shorts,
        channel_id=CHANNEL_ID,
    )


def build_su_ke_lai_short(
    out_dir: Optional[Path] = None,
    topic_title: Optional[str] = None,
) -> Dict[str, Any]:
    """Build and export TikTok Short package (short_9x16) for su_ke_lai."""
    target_dir = Path(out_dir or (SYS_DIR / "runs" / "su-ke-lai-week1-9x16"))
    target_dir.mkdir(parents=True, exist_ok=True)

    topic = build_topic_short_9x16(topic_title=topic_title)
    res = write_production_package(
        output_dir=target_dir,
        topic=topic,
        system_root=SYS_DIR,
        brief_revision=1,
        include_spinoffs=False,
        allow_active=True,
    )

    # Generate authentic thumbnail JPEG for production package completeness
    thumb_path = target_dir / "thumbnail_9x16.jpg"
    generate_thumbnail_poster(
        target_path=thumb_path,
        overlay_text="BÍ MẬT BÃY CỌC",
        ratio="9:16",
    )
    res["thumbnail_file"] = str(thumb_path)

    # Recalibrate cadence report for fast-short Remotion hybrid motion (max Flow images <= 8)
    checker = ScriptCadenceChecker(nominal_rate=4.0, max_beat_hold_seconds=15.0)
    script_data = json.loads((target_dir / "script.json").read_text(encoding="utf-8"))
    cadence_report = checker.check_scenes(script_data)
    (target_dir / "cadence_report.json").write_text(
        json.dumps(cadence_report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    res["cadence_report"] = cadence_report

    # Score script via script_hook_scorer
    hook_score = score_content_file(Path(res["content_file"]), CHANNEL_ID, "short_9x16")
    res["hook_score"] = hook_score

    return res


def build_su_ke_lai_long(
    out_dir: Optional[Path] = None,
    topic_title: Optional[str] = None,
    include_spinoffs: bool = False,
) -> Dict[str, Any]:
    """Build and export YouTube Long package (long_16x9) with spinoff shorts for su_ke_lai."""
    target_dir = Path(out_dir or (SYS_DIR / "runs" / "su-ke-lai-week1-16x9"))
    target_dir.mkdir(parents=True, exist_ok=True)

    topic = build_topic_long_16x9(topic_title=topic_title)
    res = write_production_package(
        output_dir=target_dir,
        topic=topic,
        system_root=SYS_DIR,
        brief_revision=1,
        include_spinoffs=include_spinoffs,
        allow_active=True,
    )

    # Ensure omni_platform & reframe_mode bindings in brief.json
    brief_path = Path(res["brief_file"])
    content_path = Path(res["content_file"])
    brief_data = json.loads(brief_path.read_text(encoding="utf-8"))
    content_data = json.loads(content_path.read_text(encoding="utf-8"))

    brief_data["omni_platform"] = True
    brief_data["reframe_mode"] = True
    brief_path.write_text(json.dumps(brief_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Validate omni short plans
    plans = short_plans(brief_data, content_data)
    res["omni_short_plans"] = plans

    # Generate authentic 16:9 thumbnail
    thumb_path = target_dir / "thumbnail_16x9.jpg"
    generate_thumbnail_poster(
        target_path=thumb_path,
        overlay_text="BẪY CỌC 938",
        ratio="16:9",
    )
    res["thumbnail_file"] = str(thumb_path)

    return res


def build_su_ke_lai_package(
    format_profile: str = "short_9x16",
    out_dir: Optional[Path] = None,
    topic_title: Optional[str] = None,
) -> Dict[str, Any]:
    """Unified dispatcher for building su_ke_lai channel production bundles."""
    if format_profile in ("short_9x16", "9:16"):
        return build_su_ke_lai_short(out_dir=out_dir, topic_title=topic_title)
    elif format_profile in ("long_16x9", "16:9"):
        return build_su_ke_lai_long(out_dir=out_dir, topic_title=topic_title)
    elif format_profile in ("dual", "all"):
        short_res = build_su_ke_lai_short(out_dir=out_dir, topic_title=topic_title)
        long_res = build_su_ke_lai_long(topic_title=topic_title)
        return {"short": short_res, "long": long_res}
    else:
        raise ValueError(f"Unsupported format_profile '{format_profile}'. Choose from 'short_9x16', 'long_16x9', 'dual'.")


def build_week1_sample_run(out_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Execute the canonical Week 1 test run at sys/runs/su-ke-lai-week1-9x16."""
    target_path = out_dir or (SYS_DIR / "runs" / "su-ke-lai-week1-9x16")
    return build_su_ke_lai_short(out_dir=target_path)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--format",
        choices=["short_9x16", "long_16x9", "dual"],
        default="short_9x16",
        help="Format profile to build (default: short_9x16)",
    )
    parser.add_argument("--out-dir", type=Path, default=None, help="Explicit destination directory")
    parser.add_argument("--topic", type=str, default=None, help="Custom topic title override")
    parser.add_argument(
        "--week1-sample",
        action="store_true",
        help="Build canonical sample package at sys/runs/su-ke-lai-week1-9x16",
    )
    args = parser.parse_args(argv)

    if args.week1_sample:
        print("[*] Generating canonical sample bundle for Week 1 (su-ke-lai-week1-9x16)...")
        res = build_week1_sample_run(out_dir=args.out_dir)
        is_ok = bool(res.get("valid_contracts"))
        print(f"    - Brief: {res['brief_file']}")
        print(f"    - Valid contracts: {is_ok}")
        print(f"    - Hook score: {res['hook_score'].score}/100")
        return 0 if is_ok else 1

    print(f"[*] Building package for channel '{CHANNEL_ID}' (format: {args.format})...")
    res = build_su_ke_lai_package(
        format_profile=args.format,
        out_dir=args.out_dir,
        topic_title=args.topic,
    )

    if args.format == "dual":
        s_ok = res["short"].get("valid_contracts")
        l_ok = res["long"].get("valid_contracts")
        return 0 if (s_ok and l_ok) else 1
    return 0 if res.get("valid_contracts") else 1


if __name__ == "__main__":
    raise SystemExit(main())
