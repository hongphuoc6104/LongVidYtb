#!/usr/bin/env python3
"""Build production-ready package for Impostor Paradox (9:16 Vertical Short Explainer).

Pillar: "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức" (tier_1_broad)
Topic: "Bẫy Tự Ti Học Thuật: Giải Mã Hội Chứng Kẻ Mạo Danh Ở Người Có Năng Lực Tư Duy Sâu"
Format: short_9x16 (vertical mobile short-form, 5 standalone scenes SC01..SC05, full_frame_v1)
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
    DEFAULT_CHANNEL_PILLAR,
    PackagingSpec,
    ResearchedScene,
    ResearchedTopic,
    build_scenes_from_story_rows,
    write_production_package,
)
from content.research_story_architect import (
    CURRENT_STYLE_DESCRIPTION as STYLE_DESCRIPTION,
)

# ---------------------------------------------------------------------------
# STORY 9:16 (5 Standalone Scenes — SSOT Short Explainer 45-60s)
# (title, setting, tone, spoken_style, narrative_phase, rows)
# ---------------------------------------------------------------------------
STORY_9X16: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    (
        "Cú tát mở màn bàn học đêm",
        "A computer workspace under cold laptop glow.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Càng đọc nhiều tài liệu, não bạn càng sợ bắt đầu.", "full_scene:CH01|Researcher freezes before glowing laptop screen surrounded by towering open browser tabs."),
            ("Ánh đèn hắt bóng giữa đêm khuya.", "concept_metaphor:none|Dozens of miniature digital document windows cascade down and crowd the desktop space."),
            ("Con trỏ nhấp nháy trên trang giấy trắng.", "concept_metaphor:none|Extreme close-up of the screen where a vertical charcoal cursor pulses like a tiny heartbeat in a white void."),
            ("Tờ nháp trắng biến thành bức tường gạch khổng lồ chặn đứng lối đi.", "concept_metaphor:none|The blank paper transforms into a towering impenetrable charcoal brick wall rising straight from the desk, completely blocking the forward path."),
        ],
    ),
    (
        "Nghịch lý tự ti kẻ mạo danh",
        "A pure white background with bright lighting.",
        "analytical_crisp",
        "demystifying_truth",
        "empirical_conflict",
        [
            ("Khoa học gọi đây là Hội chứng Kẻ mạo danh.", "visual_diagram:none|Clean white card featuring bold charcoal typography: HỘI CHỨNG KẺ MẠO DANH framed by crisp diagnostic bounding box."),
            ("Bảy mươi phần trăm sinh viên giỏi,", "visual_diagram:none|Hand-drawn column chart on clean white: a bold 70% column in terracotta red towering over a 30% column in muted gray."),
            ("nghĩ mình chỉ gặp may chứ không hề có thực lực.", "concept_metaphor:CH01|Researcher holds up a smiling porcelain theater mask that cracks down the middle, revealing cold sweat and inner dread."),
            ("Càng hiểu biết sâu, bạn càng thấy biển kiến thức mênh mông.", "concept_metaphor:CH01|Researcher sits pensively at wooden desk under warm lamplight, hands clasped with sincere humility."),
        ],
    ),
    (
        "Cán cân bản nháp thô năm trăm từ",
        "A pure white background with bright lighting.",
        "analytical_crisp",
        "tactical_actionable",
        "actionable_resolution",
        [
            ("Để thoát khỏi bẫy tự ti này,", "concept_metaphor:none|Clean white card featuring a circular loop of cognitive paralysis shattered by a bold angular red breakthrough arrow."),
            ("hãy dùng quy tắc bản nháp thô năm trăm từ.", "visual_diagram:none|A rough crumpled paper sheet boldly stamped BẢN NHÁP THÔ 500 TỪ in heavy charcoal block lettering on clean white."),
            ("Bản nháp thô năm trăm từ,", "concept_metaphor:CH01|Researcher firmly holds a raw hand-written manuscript sheet with bold terracotta strike-throughs on the wooden desk."),
            ("đánh bại một nghìn giờ đọc thêm vô nghĩa.", "visual_diagram:none|Balance scale where the tiny rough draft paper tilts the brass arm down with heavy force, catapulting a massive leaning stack of books high into the air."),
        ],
    ),
    (
        "Ẩn dụ hòn đảo tri thức và sương mù",
        "A misty vast ocean horizon.",
        "narrative_warm",
        "philosophical_anchor",
        "structural_model",
        [
            ("Tri thức giống như một hòn đảo giữa đại dương.", "concept_metaphor:none|A luminous circular plateau of light labeled ĐẢO TRI THỨC stands isolated in a calm dark sea."),
            ("Đảo càng mở rộng,", "concept_metaphor:none|The island plateau expands wider with warm ochre stone pathways radiating outward from the center into the water."),
            ("đường bờ biển tiếp xúc với sương mù càng dài.", "concept_metaphor:CH04|The traveler lifts an ochre lantern high, revealing dense swirling charcoal mist along the vast expanding perimeter."),
            ("Cảm giác chưa đủ chính là bằng chứng bạn đang tiến bộ.", "full_scene:CH04|The traveler smiles with calm determination, facing the misty horizon without fear under warm lantern light."),
        ],
    ),
    (
        "Kích hoạt hành động hai mươi lăm phút",
        "A morning writing table under sunlight.",
        "narrative_warm",
        "tactical_actionable",
        "actionable_resolution",
        [
            ("Đặt đồng hồ hai mươi lăm phút.", "concept_metaphor:none|A 25-minute hourglass on a warm wooden ground, with sand grains transforming as they fall into streaming written words."),
            ("Gõ liên tục mà không được phép xóa.", "full_scene:CH01|The researcher types rapidly on the laptop keyboard, eyes ablaze with momentum, ignoring mistakes."),
            ("Cho phép bản thân viết những câu văn vụng về.", "macro_prop:CH01|Cartoon four-finger hands hammering keys rhythmically while draft text streams across the screen without backspace."),
            ("Bởi vì trang nháp xấu xí, luôn giá trị hơn trang giấy trắng hoàn hảo.", "full_scene:CH01|The researcher holds up a completed rough draft with a warm triumphant smile under morning sunlight."),
        ],
    ),
]


def build_sources() -> list[dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "The Impostor Phenomenon in High Achieving Women",
            "reference": "Pauline R. Clance & Suzanne A. Imes (1978). Psychotherapy: Theory, Research & Practice, 15(3), 241-247.",
            "facts": [
                "Bảy mươi phần trăm sinh viên giỏi nghĩ mình chỉ gặp may.",
                "Hội chứng kẻ mạo danh khiến người tài năng tự ti.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Unskilled and Unaware of It",
            "reference": "Justin Kruger & David Dunning (1999). Journal of Personality and Social Psychology, 77(6), 1121-1134.",
            "facts": [
                "Người thiếu năng lực thường tự tin nhất vì không biết mình sai.",
                "Càng hiểu biết sâu càng nhận ra biển kiến thức mênh mông.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Bird by Bird: Shitty First Drafts",
            "reference": "Anne Lamott (1994). Anchor Books. ISBN: 978-0385480017.",
            "facts": [
                "Bản nháp thô năm trăm từ đánh bại một nghìn giờ đọc thêm.",
                "Viết nháp tự do phá vỡ vòng lặp sợ hãi nhận thức.",
            ],
        },
    ]


def build_topic() -> ResearchedTopic:
    story_tuples = [(title, setting, rows) for title, setting, _, _, _, rows in STORY_9X16]
    scenes = build_scenes_from_story_rows(story_tuples, character_id="CH01")
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = STORY_9X16[i][2]
        sc.spoken_style = STORY_9X16[i][3]
        sc.narrative_phase = STORY_9X16[i][4]

    # Assign source claims for 5 scenes
    scenes[1].source_ids = ["SRC01", "SRC02"]
    scenes[1].claim_facts = [
        ("Bảy mươi phần trăm sinh viên giỏi,", "SRC01", "Bảy mươi phần trăm sinh viên giỏi nghĩ mình chỉ gặp may."),
        ("Càng hiểu biết sâu, bạn càng thấy biển kiến thức mênh mông.", "SRC02", "Càng hiểu biết sâu càng nhận ra biển kiến thức mênh mông."),
    ]
    scenes[2].source_ids = ["SRC03"]
    scenes[2].claim_facts = [
        ("Bản nháp thô năm trăm từ, đánh bại một nghìn giờ đọc thêm vô nghĩa.", "SRC03", "Bản nháp thô năm trăm từ đánh bại một nghìn giờ đọc thêm."),
    ]

    return ResearchedTopic(
        topic="Bẫy Tự Ti Học Thuật: Giải Mã Hội Chứng Kẻ Mạo Danh Ở Người Có Năng Lực Tư Duy Sâu",
        audience="Sinh viên, nghiên cứu sinh, người tự học và người làm việc trí óc xem video di động",
        goal="Giải mã tâm lý tự ti học thuật bằng cơ chế khoa học thần kinh và trao vũ khí bản nháp thô 500 từ",
        video_type="research_explainer",
        min_duration=45.0,
        max_duration=60.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=build_sources(),
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _, _, _, _) in enumerate(STORY_9X16, 1)],
        characters=[
            {
                "id": "CH01",
                "name": "Nhân vật sinh viên nghiên cứu",
                "role": "academic_student",
                "appearance": CAST_APPEARANCE,
                "outfit": "Simple earth-toned student sweatshirt or comfortable hoodie in warm gray, appropriate for desk study.",
            },
            {
                "id": "CH04",
                "name": "Người lữ hành trên đảo tri thức",
                "role": "knowledge_traveler",
                "appearance": CAST_APPEARANCE,
                "outfit": "Simple outdoor traveler cloak with rugged boots and warm ochre lantern.",
            },
        ],
        scenes=scenes,
        tone="Conversational Essayist điềm đạm, ấm áp, sắc sảo, giải tỏa áp lực nhận thức",
        language="vi",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        packaging=PackagingSpec(
            youtube_title="Càng Đọc Nhiều Càng Sợ Viết: Ảo Giác Tự Ti Học Thuật",
            visual_hook="Nhân vật người que ngồi trước màn hình laptop sáng với 30 tab mở và trang văn bản trắng",
            text_overlay="BẪY TỰ TI",
            contrast_pair="Đọc thêm 1000 giờ vs. Viết bản nháp thô 500 từ",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "hội chứng kẻ mạo danh",
                "impostor syndrome",
                "bẫy tự ti học thuật",
                "tư duy nghiên cứu",
                "dunning kruger",
                "kỹ năng viết luận văn",
                "nghiên cứu khoa học di động",
            ],
        ),
    )


def count_total_beats(scenes: List[ResearchedScene]) -> int:
    return sum(len(sc.visual_beats) for sc in scenes)


def build_and_export_job(topic: ResearchedTopic, out_dir: Path) -> dict:
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
    (draft_dir / "outline.json").write_text(json.dumps(outline_data, ensure_ascii=False, indent=2))
    content_text = (out_dir / "content.json").read_text(encoding="utf-8")
    (draft_dir / "content.json").write_text(content_text, encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description="Build Impostor Paradox 9:16 production blueprint.")
    parser.add_argument(
        "--out",
        type=Path,
        default=SYS_DIR / "content" / "blueprints" / "impostor-paradox-9x16",
        help="Target output blueprint directory",
    )
    args = parser.parse_args()

    topic = build_topic()
    total_beats = count_total_beats(topic.scenes)
    print(f"Building topic: {topic.topic}")
    print(f"Total scenes: {len(topic.scenes)}, Total visual beats: {total_beats}")

    out_dir = args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    build_and_export_job(topic, out_dir)
    print(f"Exported package to {out_dir}")
    print(f"Visual beats: {total_beats} across {len(topic.scenes)} scenes")


if __name__ == "__main__":
    main()
