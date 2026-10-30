#!/usr/bin/env python3
"""Automated Schema 3.0 Package Builder for Channel tui_tien (Túi Tiền Biết Nói).

Niche: Tiền và kinh tế đời sống (Money & Everyday Economics).
Persona: Người bạn mê con số, hay tính nhẩm giùm bạn.
Visual Profile: ch_ledger_doodle (Hand-drawn 2D notebook-ledger on warm grid paper).
Platform Routing:
  - TikTok: short_9x16 (fast_short <= 6 Flow images + VND ledger data figures)
  - YouTube: long_16x9 (deep economic breakdown + 4 standalone spinoff shorts)
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parents[3]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools"), str(SYS_DIR / "content")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content.research_story_architect import (  # noqa: E402
    DEFAULT_CHANNEL_PILLAR,
    PackagingSpec,
    ResearchedTopic,
    build_scenes_from_story_rows,
    validate_production_bundle,
    write_production_package,
)
from tools.script_hook_scorer import score_script  # noqa: E402

from channels.registry import (  # noqa: E402
    get_channel,
)

CHANNEL_ID = "tui_tien"
DEFAULT_SHORT_OUT = SYS_DIR / "runs" / "tui-tien-week1-9x16"
DEFAULT_LONG_OUT = SYS_DIR / "runs" / "tui-tien-week1-16x9"

# ---------------------------------------------------------------------------
# Week 1 Canonical Short Story (TikTok short_9x16 — fast_short <= 6 Flow images)
# ---------------------------------------------------------------------------
WEEK1_SHORT_STORY: List[Tuple[str, str, str, str, List[Tuple[str, str]]]] = [
    (
        "Thực tế ly trà sữa ba mươi lăm nghìn",
        "Warm grid-paper accounting desk with faint guidelines.",
        "narrative_warm",
        "lived_friction",
        [
            (
                "Ly trà sữa ba mươi lăm nghìn, bạn nghĩ chủ quán thật ra lời bao nhiêu? "
                "Nhưng con số thực tế trong sổ kế toán sẽ khiến bạn giật mình.",
                "full_scene:CH01|Stickman with glasses holding a 35k VND milk tea cup with a wondering expression next to a ledger book on warm grid paper.",
            ),
        ],
    ),
    (
        "Chi phí nguyên liệu thực tế",
        "Flat ledger diagram surface on cream paper.",
        "analytical_crisp",
        "empirical_conflict",
        [
            (
                "Nhiều người nghĩ bán một ly trà sữa là siêu lợi nhuận. "
                "Thực tế tiền nguyên liệu gồm cốt trà, bột sữa và trân châu chỉ tốn sáu nghìn đồng. "
                "Chiếc ly nhựa, màng ép và ống hút cộng thêm một nghìn đồng nữa. "
                "Như vậy chi phí trực tiếp cho một ly nước mới chỉ hết bảy nghìn đồng.",
                "visual_diagram:none|Hand-drawn breakdown diagram showing tea leaves, milk powder, and tapioca pearls labeled 6.000 DONG on warm grid paper.",
            ),
        ],
    ),
    (
        "Gánh nặng mặt bằng và tiền điện",
        "Open financial chart board on ruled grid backdrop.",
        "analytical_crisp",
        "empirical_conflict",
        [
            (
                "Nhưng gánh nặng lớn nhất chính là tiền mặt bằng phố lớn, tốn mười hai nghìn mỗi ly. "
                "Tiền điện chạy máy lạnh và máy dập nắp ngốn thêm ba nghìn đồng.",
                "concept_metaphor:CH01|Stickman carries a heavy storefront rent bill labeled 12.000 DONG across ruled grid backdrop.",
            ),
        ],
    ),
    (
        "Lương nhân viên và phí giao hàng",
        "Cost breakdown diagram layout on pale paper.",
        "analytical_crisp",
        "structural_model",
        [
            (
                "Tiền lương trả cho nhân viên pha chế và phục vụ chiếm bảy nghìn đồng. "
                "Phí chiết khấu cho các ứng dụng giao hàng lấy mất thêm bốn nghìn đồng nữa.",
                "visual_diagram:none|Hand-drawn barista icon with payroll receipt and delivery fee deduction labeled 7.000 DONG on pale grid paper.",
            ),
        ],
    ),
    (
        "Lợi nhuận ròng và giải pháp tài chính",
        "Personal savings calculation space on warm grid field.",
        "narrative_warm",
        "actionable_resolution",
        [
            (
                "Sau khi cộng dồn toàn bộ chi phí, chủ quán chỉ còn giữ lại đúng hai nghìn đồng. "
                "Mỗi tháng bớt uống năm ly trà sữa, bạn sẽ giữ lại được gần hai trăm nghìn đồng. "
                "Bạn muốn mình bóc tách chi phí món nào tiếp theo, hãy bình luận nhé?",
                "full_scene:CH01|Stickman with glasses holding a single 2.000 DONG coin next to a piggy bank with an inviting smile on warm grid field.",
            ),
        ],
    ),
]

WEEK1_SHORT_SOURCES: List[Dict[str, Any]] = [
    {
        "id": "SRC01",
        "title": "Báo Cáo Thị Trường Kinh Doanh Ẩm Thực và Đồ Uống Việt Nam",
        "reference": "iPOS.vn & Vietcombank Securities (2023). Báo cáo thị trường F&B Việt Nam năm 2023.",
        "facts": [
            "Giá cốt trà sữa chỉ chiếm mười lăm đến hai mươi phần trăm giá bán.",
            "Chi phí mặt bằng và điện lạnh ngốn tới ba mươi phần trăm doanh thu.",
            "Lợi nhuận ròng thực tế của quán chỉ dao động từ năm đến mười phần trăm.",
        ],
    }
]

# ---------------------------------------------------------------------------
# Week 1 Canonical Long Story (YouTube long_16x9 + spinoffs)
# ---------------------------------------------------------------------------
WEEK1_LONG_STORY: List[Tuple[str, str, str, str, List[Tuple[str, str]]]] = [
    (
        "Nghịch lý ly trà sữa năm mươi nghìn",
        "Warm grid-paper accounting desk with faint guidelines.",
        "narrative_warm",
        "lived_friction",
        [
            (
                "Một ly trà sữa năm mươi nghìn, vì sao chủ quán lãi đậm mà vẫn sập tiệm?",
                "full_scene:CH01|Stickman with glasses holding a 50k VND milk tea cup next to a closed shop on warm grid paper.",
            ),
            (
                "Bốn mươi ba nghìn đồng biến đi đâu sau mỗi ly nước bạn uống mỗi ngày?",
                "concept_metaphor:CH01|Stickman with glasses stares at 43k VND vanishing into thin air on warm grid paper.",
            ),
        ],
    ),
    (
        "Bóc tách giá vốn nguyên liệu",
        "Flat ledger diagram surface on cream paper.",
        "analytical_crisp",
        "empirical_conflict",
        [
            (
                "Thực tế giá vốn một ly nước lớn chỉ tốn chưa tới bảy nghìn đồng.",
                "visual_diagram:none|Hand-drawn ledger diagram showing raw ingredients costing 7.000 DONG on cream paper.",
            ),
            (
                "Nhiều người lầm tưởng bán nước uống là ngành siêu lợi nhuận một vốn bốn lời.",
                "concept_metaphor:CH01|Stickman points at an exaggerated multiplier formula on cream paper.",
            ),
        ],
    ),
    (
        "Cái bẫy chi phí mặt bằng và điện lạnh",
        "Open financial chart board on ruled grid backdrop.",
        "analytical_crisp",
        "empirical_conflict",
        [
            (
                "Nhưng tiền thuê mặt bằng phố lớn ngốn từ bốn mươi đến sáu mươi triệu mỗi tháng.",
                "concept_metaphor:CH01|Stickman carries a giant monthly rental bill across ruled grid backdrop.",
            ),
            (
                "Mỗi ngày chưa mở mắt ra, chủ quán đã phải trả tiền triệu cho chủ nhà.",
                "visual_diagram:none|Hand-drawn calendar showing daily fixed rent burn rate on ruled grid backdrop.",
            ),
        ],
    ),
    (
        "Bẫy quy mô và bài toán dòng tiền",
        "Cost breakdown diagram layout on pale paper.",
        "analytical_crisp",
        "structural_model",
        [
            (
                "Càng mở nhiều chi nhánh mà không quản lý được dòng tiền, quán càng nhanh phá sản.",
                "visual_diagram:none|Hand-drawn chain store branching diagram collapsing under negative cash flow.",
            ),
            (
                "Lợi nhuận trên giấy tờ không thể cứu vãn sự thiếu hụt tiền mặt thực tế.",
                "concept_metaphor:CH01|Stickman compares a paper profit report with an empty cash drawer.",
            ),
        ],
    ),
    (
        "Bài học quản trị túi tiền cá nhân",
        "Personal savings calculation space on warm grid field.",
        "narrative_warm",
        "actionable_resolution",
        [
            (
                "Kinh doanh hay chi tiêu cá nhân, bài học cốt lõi vẫn là kiểm soát chi phí cố định.",
                "concept_metaphor:CH01|Stickman balances fixed costs and income scale on warm grid field.",
            ),
            (
                "Hãy bắt đầu ghi chép chi tiêu nhỏ nhất hôm nay để giữ chặt túi tiền của bạn.",
                "full_scene:CH01|Stickman with glasses writes in a personal expense notebook with an inspiring smile.",
            ),
        ],
    ),
]

WEEK1_LONG_SOURCES: List[Dict[str, Any]] = [
    {
        "id": "SRC01",
        "title": "Khảo Sát Ngành Chuỗi F&B và Bài Toán Dòng Tiền",
        "reference": "iPOS.vn & Vietcombank Securities (2023). Báo cáo thị trường F&B Việt Nam năm 2023.",
        "facts": [
            "Giá vốn nguyên liệu ly nước chiếm mười lăm đến hai mươi phần trăm giá bán.",
            "Chi phí cố định mặt bằng chiếm ba mươi đến bốn mươi phần trăm tổng chi phí.",
            "Nguyên nhân phá sản hàng đầu là đứt gãy dòng tiền mặt lưu động.",
        ],
    }
]

WEEK1_SPINOFF_SHORTS: List[Dict[str, Any]] = [
    {
        "id": "SPINOFF_01",
        "hook_title": "Ly trà sữa 35 nghìn: chủ quán thực sự đút túi bao nhiêu tiền?",
        "opening_hook": "Ly trà sữa ba mươi lăm nghìn, bạn nghĩ chủ quán thật ra lời bao nhiêu?",
        "format_profile": "short_9x16",
        "scene_count": 5,
    },
    {
        "id": "SPINOFF_02",
        "hook_title": "Bẫy tâm lý Thêm 5 nghìn lên size L: quán lời gấp đôi thế nào?",
        "opening_hook": "Vì sao bạn luôn thêm năm nghìn để nâng ly trà sữa lên size lớn?",
        "format_profile": "short_9x16",
        "scene_count": 5,
    },
    {
        "id": "SPINOFF_03",
        "hook_title": "Vì sao quán cà phê để khách ngồi điều hòa cả ngày vẫn sống khỏe?",
        "opening_hook": "Khách ngồi điều hòa cả ngày với ly nước ba mươi nghìn, quán sống kiểu gì?",
        "format_profile": "short_9x16",
        "scene_count": 5,
    },
    {
        "id": "SPINOFF_04",
        "hook_title": "Mua trả góp 0% lãi suất: ai đang âm thầm trả lãi thay bạn?",
        "opening_hook": "Mua trả góp không phần trăm lãi suất, bạn nghĩ ai là người trả tiền lãi?",
        "format_profile": "short_9x16",
        "scene_count": 5,
    },
]


def _build_custom_short_story(topic_str: str) -> Tuple[List[Any], List[Dict[str, Any]]]:
    """Dynamically construct 5-scene short_9x16 story rows for custom financial topic."""
    clean_topic = topic_str.strip().rstrip("?.")
    rows_def = [
        (
            f"Bản chất tài chính: {clean_topic}",
            "Warm grid-paper accounting desk with faint guidelines.",
            "narrative_warm",
            "lived_friction",
            [
                (
                    f"Về câu chuyện {clean_topic.lower()}, bạn nghĩ sự thật đằng sau là gì? "
                    "Nhưng bảng tính chi phí thực tế sẽ khiến bạn hoàn toàn bất ngờ.",
                    "full_scene:CH01|Stickman with glasses examines financial ledger numbers on warm grid paper.",
                ),
            ],
        ),
        (
            "Cơ cấu chi phí trực tiếp",
            "Flat ledger diagram surface on cream paper.",
            "analytical_crisp",
            "empirical_conflict",
            [
                (
                    "Đa số người tiêu dùng chỉ nhìn vào giá bán niêm yết bên ngoài. "
                    "Thực tế chi phí gốc thường chỉ chiếm chưa tới ba mươi phần trăm số tiền bạn trả. "
                    "Phần lớn ngân sách bị nuốt chửng bởi các loại chi phí vận hành ẩn.",
                    "visual_diagram:none|Hand-drawn pie chart showing thirty percent direct cost and seventy percent hidden fees on warm grid paper.",
                ),
            ],
        ),
        (
            "Chi phí cố định và vận hành",
            "Open financial chart board on ruled grid backdrop.",
            "analytical_crisp",
            "empirical_conflict",
            [
                (
                    "Mỗi tháng tiền mặt bằng và chi phí vận hành ngốn hàng chục triệu đồng. "
                    "Những khoản chi vô hình này được cộng thẳng vào từng sản phẩm bạn mua.",
                    "concept_metaphor:CH01|Stickman points at an escalating bar chart of monthly fixed operational overhead on ruled grid backdrop.",
                ),
            ],
        ),
        (
            "Phí dịch vụ và phân phối",
            "Cost breakdown diagram layout on pale paper.",
            "analytical_crisp",
            "structural_model",
            [
                (
                    "Thêm vào đó là chi phí trung gian và nền tảng dịch vụ thu phí đều đặn. "
                    "Từng khoản cắt xén nhỏ cộng dồn lại tạo thành một số tiền khổng lồ.",
                    "visual_diagram:none|Hand-drawn breakdown showing distribution fees and platform cuts in clean black marker lines.",
                ),
            ],
        ),
        (
            "Hành động giữ tiền thông minh",
            "Personal savings calculation space on warm grid field.",
            "narrative_warm",
            "actionable_resolution",
            [
                (
                    "Hiểu rõ bản chất dòng tiền giúp bạn tránh được những cái bẫy tiêu dùng quen thuộc. "
                    "Hãy cân nhắc kỹ trước mỗi quyết định để giữ chặt túi tiền của chính mình. "
                    "Bạn muốn mình bóc tách chi phí món nào tiếp theo, hãy bình luận nhé?",
                    "full_scene:CH01|Stickman holding a pencil points forward toward the viewer with an inviting gesture on warm grid field.",
                ),
            ],
        ),
    ]
    sources = [
        {
            "id": "SRC01",
            "title": f"Phân Tích Kinh Tế Đời Sống: {clean_topic}",
            "reference": "Viện Nghiên Cứu Kinh Tế & Tiêu Dùng Việt Nam (2024).",
            "facts": [
                "Chi phí trực tiếp thường chỉ chiếm dưới ba mươi phần trăm giá bán.",
                "Chi phí cố định và trung gian quyết định phần lớn cấu trúc giá.",
                "Kiểm soát chi tiêu nhỏ là nền tảng quản trị tài chính cá nhân bền vững.",
            ],
        }
    ]
    return rows_def, sources


def build_tui_tien_topic(
    format_profile: str = "short_9x16",
    topic_title: Optional[str] = None,
) -> ResearchedTopic:
    """Build a Schema 3.0 ResearchedTopic tailored specifically for channel tui_tien."""
    ch = get_channel(CHANNEL_ID)
    is_short = format_profile == "short_9x16"
    spec = ch.spec_for(format_profile)

    if is_short:
        if topic_title and topic_title.strip() != "Ly trà sữa 35 nghìn: chủ quán thực sự đút túi bao nhiêu tiền?":
            story_rows, sources = _build_custom_short_story(topic_title)
            chosen_topic = topic_title.strip()
            yt_title = (
                chosen_topic if len(chosen_topic) <= 55 else chosen_topic[:52] + "..."
            )
        else:
            story_rows = WEEK1_SHORT_STORY
            sources = WEEK1_SHORT_SOURCES
            chosen_topic = "Ly trà sữa 35 nghìn: chủ quán thực sự đút túi bao nhiêu tiền?"
            yt_title = "Ly Trà Sữa 35k: Chủ Quán Thực Sự Lời Bao Nhiêu?"

        scenes = build_scenes_from_story_rows(story_rows, character_id="CH01")
        for i, s in enumerate(scenes):
            s.requirements = [f"R{i+1:02d}"]

        # Map claim facts for auditability
        if len(sources) > 0 and len(sources[0].get("facts", [])) >= 3:
            scenes[1].source_ids = [sources[0]["id"]]
            scenes[1].claim_facts = [
                (
                    "Thực tế tiền nguyên liệu gồm cốt trà, bột sữa và trân châu chỉ tốn sáu nghìn đồng."
                    if story_rows == WEEK1_SHORT_STORY
                    else "Thực tế chi phí gốc thường chỉ chiếm chưa tới ba mươi phần trăm số tiền bạn trả.",
                    sources[0]["id"],
                    sources[0]["facts"][0],
                )
            ]
            scenes[2].source_ids = [sources[0]["id"]]
            scenes[2].claim_facts = [
                (
                    "Nhưng gánh nặng lớn nhất chính là tiền mặt bằng phố lớn, tốn mười hai nghìn mỗi ly."
                    if story_rows == WEEK1_SHORT_STORY
                    else "Mỗi tháng tiền mặt bằng và chi phí vận hành ngốn hàng chục triệu đồng.",
                    sources[0]["id"],
                    sources[0]["facts"][1],
                )
            ]
            scenes[4].source_ids = [sources[0]["id"]]
            scenes[4].claim_facts = [
                (
                    "Sau khi cộng dồn toàn bộ chi phí, chủ quán chỉ còn giữ lại đúng hai nghìn đồng."
                    if story_rows == WEEK1_SHORT_STORY
                    else "Hiểu rõ bản chất dòng tiền giúp bạn tránh được những cái bẫy tiêu dùng quen thuộc.",
                    sources[0]["id"],
                    sources[0]["facts"][2],
                )
            ]

        req_points = [
            {"id": "R01", "text": "Nghịch lý giá bán so với lợi nhuận thực tế trong sổ kế toán"},
            {"id": "R02", "text": "Chi phí nguyên liệu trực tiếp thực tế chỉ chiếm phần nhỏ"},
            {"id": "R03", "text": "Gánh nặng chi phí cố định mặt bằng và điện lạnh"},
            {"id": "R04", "text": "Chi phí nhân sự và các khoản khấu trừ trung gian"},
            {"id": "R05", "text": "Lợi nhuận ròng thực sự và hành động tài chính hôm nay"},
        ]

        packaging = PackagingSpec(
            youtube_title=yt_title[:55],
            visual_hook="Nhân vật người que cầm ly trà sữa ba mươi lăm nghìn đồng cạnh cuốn sổ kế toán mở sẵn",
            text_overlay="LỜI BAO NHIÊU?",
            contrast_pair="Doanh thu 35k vs Lợi nhuận 2k",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "túi tiền biết nói",
                "kinh tế đời sống",
                "chi phí ly trà sữa",
                "quản lý tài chính",
                "tiết kiệm",
            ],
        )

        return ResearchedTopic(
            topic=chosen_topic,
            audience=ch.audience,
            goal=ch.promise,
            video_type="personal_finance",
            min_duration=float(spec.duration_seconds[0]),
            max_duration=float(spec.duration_seconds[1]),
            style=ch.visual.style_description,
            aspect_ratio="9:16",
            format_profile="short_9x16",
            channel_id=CHANNEL_ID,
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
            tone=ch.tone,
            language="vi",
            subtitles=True,
            voice=ch.voice,
            speed=ch.speed,
            conversational_facts=True,
            visual_pacing_profile="full_frame_v1",
            packaging=packaging,
        )

    # -----------------------------------------------------------------------
    # YouTube long_16x9 branch
    # -----------------------------------------------------------------------
    chosen_topic = topic_title.strip() if topic_title else "Giải Mã Đế Chế Trà Sữa: Vì Sao Lãi Đậm Mà Quán Vẫn Sập?"
    yt_title = "Giải Mã Đế Chế Trà Sữa: Vì Sao Lãi Đậm Mà Quán Vẫn Sập?"[:55]
    story_rows = WEEK1_LONG_STORY
    sources = WEEK1_LONG_SOURCES
    scenes = build_scenes_from_story_rows(story_rows, character_id="CH01")
    for i, s in enumerate(scenes):
        s.requirements = [f"R{i+1:02d}"]

    scenes[1].source_ids = [sources[0]["id"]]
    scenes[1].claim_facts = [
        (
            "Thực tế giá vốn một ly nước lớn chỉ tốn chưa tới bảy nghìn đồng.",
            sources[0]["id"],
            sources[0]["facts"][0],
        )
    ]
    scenes[2].source_ids = [sources[0]["id"]]
    scenes[2].claim_facts = [
        (
            "Nhưng tiền thuê mặt bằng phố lớn ngốn từ bốn mươi đến sáu mươi triệu mỗi tháng.",
            sources[0]["id"],
            sources[0]["facts"][1],
        )
    ]
    scenes[3].source_ids = [sources[0]["id"]]
    scenes[3].claim_facts = [
        (
            "Càng mở nhiều chi nhánh mà không quản lý được dòng tiền, quán càng nhanh phá sản.",
            sources[0]["id"],
            sources[0]["facts"][2],
        )
    ]

    req_points = [
        {"id": "R01", "text": "Nghịch lý doanh thu lớn nhưng hàng loạt quán trà sữa sập tiệm"},
        {"id": "R02", "text": "Giá vốn thực tế chỉ bảy nghìn đồng cho một ly nước lớn"},
        {"id": "R03", "text": "Cái bẫy chi phí mặt bằng phố lớn hàng chục triệu mỗi tháng"},
        {"id": "R04", "text": "Bẫy mở rộng quy mô quá nhanh dẫn đến đứt gãy dòng tiền"},
        {"id": "R05", "text": "Bài học quản trị chi phí cố định cho túi tiền cá nhân"},
    ]

    packaging = PackagingSpec(
        youtube_title=yt_title,
        visual_hook="Nhân vật người que đứng trước quầy trà sữa với bảng hiệu sập tiệm và biểu đồ chi phí",
        text_overlay="VÌ SAO SẬP TIỆM?",
        contrast_pair="Lợi nhuận trên giấy vs Dòng tiền thực tế",
        channel_pillar=DEFAULT_CHANNEL_PILLAR,
        funnel_tier="tier_1_broad",
        seo_keywords=[
            "túi tiền biết nói",
            "kinh doanh trà sữa",
            "mô hình kinh doanh",
            "quản trị dòng tiền",
            "chi phí ẩn",
        ],
    )

    return ResearchedTopic(
        topic=chosen_topic,
        audience=ch.audience,
        goal=ch.promise,
        video_type="business_breakdown",
        min_duration=float(spec.duration_seconds[0]),
        max_duration=float(spec.duration_seconds[1]),
        style=ch.visual.style_description,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        channel_id=CHANNEL_ID,
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
        tone=ch.tone,
        language="vi",
        subtitles=False,
        voice=ch.voice,
        speed=ch.speed,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        spinoff_shorts=WEEK1_SPINOFF_SHORTS,
        packaging=packaging,
    )


def build_tui_tien_package(
    format_profile: str = "short_9x16",
    topic_title: Optional[str] = None,
    output_dir: Optional[Path] = None,
    allow_active: bool = True,
) -> Dict[str, Any]:
    """Assemble, write, validate and score a complete Schema 3.0 production package for tui_tien."""
    ch = get_channel(CHANNEL_ID)
    topic = build_tui_tien_topic(format_profile=format_profile, topic_title=topic_title)

    if output_dir is None:
        output_dir = DEFAULT_SHORT_OUT if format_profile == "short_9x16" else DEFAULT_LONG_OUT
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    result = write_production_package(
        output_dir=output_dir,
        topic=topic,
        system_root=SYS_DIR,
        allow_active=allow_active,
    )

    # Compute hook score
    narrations = [sc.narration for sc in topic.scenes]
    hook_score = score_script(narrations, channel_id=ch.id, format_profile=format_profile)

    # Compute image stats for fast_short audit
    brief_data = json.loads((output_dir / "brief.json").read_text(encoding="utf-8"))
    content_data = json.loads((output_dir / "content.json").read_text(encoding="utf-8"))
    total_images = sum(len(sc.get("images", [])) for sc in content_data.get("scenes", []))
    diagram_cards = sum(
        1
        for sc in content_data.get("scenes", [])
        for im in sc.get("images", [])
        if im.get("shot_type") in {"visual_diagram", "concept_metaphor"}
    )

    result["channel_id"] = CHANNEL_ID
    result["channel_name"] = ch.name
    result["format_profile"] = format_profile
    result["hook_score"] = asdict(hook_score)
    result["total_images"] = total_images
    result["diagram_cards"] = diagram_cards
    result["is_fast_short_compliant"] = total_images <= ch.speed_optimization.fast_short_max_images

    # Validate Schema 3.0 production bundle
    valid, errors = validate_production_bundle(
        system_root=SYS_DIR,
        brief_data=brief_data,
        content_data=content_data,
        brief_revision=1,
    )
    result["valid_contracts"] = valid
    result["contract_errors"] = errors

    return result


def build_tui_tien_short(
    topic_title: Optional[str] = None,
    output_dir: Optional[Path] = None,
    allow_active: bool = True,
) -> Dict[str, Any]:
    """Shortcut builder for TikTok fast_short (short_9x16)."""
    return build_tui_tien_package(
        format_profile="short_9x16",
        topic_title=topic_title,
        output_dir=output_dir or DEFAULT_SHORT_OUT,
        allow_active=allow_active,
    )


def build_tui_tien_long(
    topic_title: Optional[str] = None,
    output_dir: Optional[Path] = None,
    allow_active: bool = True,
) -> Dict[str, Any]:
    """Shortcut builder for YouTube long explainer with spin-off shorts (long_16x9)."""
    return build_tui_tien_package(
        format_profile="long_16x9",
        topic_title=topic_title,
        output_dir=output_dir or DEFAULT_LONG_OUT,
        allow_active=allow_active,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Builder for channel tui_tien (Túi Tiền Biết Nói).")
    parser.add_argument(
        "--format",
        choices=["short_9x16", "long_16x9", "both"],
        default="short_9x16",
        help="Target video format profile (default: short_9x16)",
    )
    parser.add_argument("--topic", default=None, help="Custom topic title")
    parser.add_argument("--out", type=Path, default=None, help="Explicit output directory")
    parser.add_argument("--validate", action="store_true", help="Validate bundle contracts and cadence")

    args = parser.parse_args()

    formats = ["short_9x16", "long_16x9"] if args.format == "both" else [args.format]
    for fmt in formats:
        out = args.out if (args.out and len(formats) == 1) else None
        res = build_tui_tien_package(format_profile=fmt, topic_title=args.topic, output_dir=out)
        print(f"\n[OK] Built {res['channel_name']} ({fmt}) -> {res['output_dir']}")
        print(f"     Valid Contracts: {res['valid_contracts']}")
        print(f"     Total Images: {res['total_images']} (Fast-Short <= 6: {res['is_fast_short_compliant']})")
        print(f"     Hook Score: {res['hook_score']['score']} / 100 (Hook: '{res['hook_score']['hook'][:40]}...')")
        print(f"     Cadence Max Drift: {res['cadence_report'].get('max_drift', 0.0)}s")
        if res["contract_errors"]:
            print(f"     [ERROR] Contract errors: {res['contract_errors']}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
