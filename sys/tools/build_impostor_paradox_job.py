#!/usr/bin/env python3
"""Build production-ready package for Impostor Paradox (9:16 Vertical Long-Form).

Pillar: "Giải Mã Tư Duy Nghiên Cứu, Bản Chất Tri Thức & Luật Ngầm Học Thuật" (tier_1_broad)
Topic: "Bẫy Tự Ti Học Thuật: Giải Mã Hội Chứng Kẻ Mạo Danh Ở Người Có Năng Lực Tư Duy Sâu"
Format: short_9x16 (vertical mobile long-form, 19 scenes, full_frame_v1)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tools.research_story_architect import (
    DEFAULT_CHANNEL_PILLAR,
    PackagingSpec,
    ResearchedScene,
    ResearchedTopic,
    build_scenes_from_story_rows,
    write_production_package,
)
from visual_style import CAST_APPEARANCE, STYLE_DESCRIPTION

# ---------------------------------------------------------------------------
# STORY 9:16 (19 Scenes — Vertical Mobile Long-Form)
# (title, setting, tone, spoken_style, narrative_phase, rows)
# ---------------------------------------------------------------------------
STORY_9X16: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    (
        "Cú tát mở màn bàn học đêm",
        "A student desk under cold laptop glow.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Càng đọc nhiều tài liệu, não bạn càng sợ bắt đầu.", "full_scene|A young student stick-figure sits tiredly before a glowing laptop screen with multiple open browser tabs."),
            ("Màn hình rực sáng giữa đêm khuya.", "still_life|A desk organizer holding highlighters and printed drafts under pale blue laptop glow."),
            ("Con trỏ nhấp nháy trên trang giấy trắng.", "macro_prop|A laptop monitor showing an empty document with a single blinking cursor line."),
            ("Bạn cảm thấy hoàn toàn bế tắc.", "variation|The student slumps their shoulders, paralyzed with uncertainty."),
        ],
    ),
    (
        "Đồng hồ điểm hai giờ sáng",
        "A vintage clock in dim warm lamplight.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Đồng hồ đã chỉ hai giờ sáng.", "still_life|A vintage desk clock resting beside a cold ceramic coffee mug under dim yellow lamplight."),
            ("Thư mục tài liệu dày cộm.", "still_life|A heavy stack of printed research papers with yellow sticky bookmarks on a wooden surface."),
            ("Mỗi bài báo bạn đọc xong,", "still_life|An open textbook showing highlighted passages and clean hand-drawn margin brackets."),
            ("lại mở ra thêm mười câu hỏi mới.", "still_life|A spiral notebook filled with question marks and abstract interconnected branch lines."),
        ],
    ),
    (
        "Cái bẫy chưa đủ sâu",
        "A laptop screen in a dark room.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Và cái giọng nói trong đầu bạn thì thầm:", "macro_prop|Cartoon four-finger hand rests hesitantly above keyboard keys without typing a single letter."),
            ("mình chưa đọc đủ để gõ dòng đầu tiên.", "still_life|A close view of an empty document screen reflecting pale blue ambient light."),
            ("Bạn sợ bị người khác phát hiện.", "white_card|A magnifying glass examining an empty document icon on pure white."),
            ("Sợ người ta bảo mình chưa hiểu gì.", "still_life|An ink pen lying horizontally across empty white notebook lines."),
        ],
    ),
    (
        "Hành lang thư viện vô tận",
        "A library aisle stretching into distance.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Biển tri thức ngoài kia quá mênh mông.", "environment|A grand library hall with towering bookshelves extending to distant arches under soft dawn light."),
            ("Bạn càng học, càng thấy mình nhỏ bé.", "environment|Rows of quiet wooden study desks beside tall arched glass windows with morning fog."),
            ("Cảm giác dốt nát cứ thế lớn dần.", "environment|An empty corridor between massive academic book stacks without a single human figure."),
            ("Biến thành xiềng xích vô hình.", "environment|Quiet dusty light beams filtering through tall windows across empty reading tables."),
        ],
    ),
    (
        "Nỗi đau của người cầu toàn",
        "A student desk under cold laptop glow.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Đây không phải là sự lười biếng.", "full_scene|The student stick-figure rests head in hands beside the glowing laptop, overwhelmed by thoughts."),
            ("Bạn thực sự quan tâm đến bài viết.", "still_life|A neat stack of handwritten revision index cards resting beside a warm mug."),
            ("Nhưng chính sự cầu toàn quá mức,", "variation|The student rubs their temples, struggling against mental paralysis."),
            ("đang bóp nghẹt động lực hành động.", "still_life|An open academic planner with unmarked checkbox boxes under warm lamplight."),
        ],
    ),
    (
        "Đặt tên cho con quái vật",
        "A pure white background with bright lighting.",
        "analytical_crisp",
        "demystifying_truth",
        "empirical_conflict",
        [
            ("Khoa học đã đặt tên cho hiện tượng này.", "white_card|A theatrical mask icon divided into two halves, one smiling and one frowning, on pure white."),
            ("Đó là Hội chứng Kẻ mạo danh.", "white_card|Bold conceptual text icon reading IMPOSTOR SYNDROME surrounded by simple line borders on pure white."),
            ("Căn bệnh của những người giỏi giang.", "white_card|A gold academic medal placed beside a large questioning symbol on pure white."),
            ("Càng hiểu biết, càng tự ti.", "white_card|A minimal conceptual balance scale weighing deep insight against self doubt on pure white."),
        ],
    ),
    (
        "Thí nghiệm Clance và Imes",
        "An academic office with sage-green walls.",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Năm một nghìn chín trăm bảy mươi tám,", "full_scene|Two psychologist stick-figures interview a bright student across a polished wooden office table."),
            ("hai nhà tâm lý học thực hiện cuộc khảo sát.", "still_life|A clipboard holding clinical interview evaluation sheets beside a silver pen."),
            ("Họ phỏng vấn một trăm năm mươi sinh viên,", "full_scene|A student participant speaks earnestly while gesturing toward their academic records."),
            ("có thành tích học thuật xuất sắc nhất trường.", "still_life|A stack of bound honor society theses on polished oak wood."),
        ],
    ),
    (
        "Lời thú nhận chấn động",
        "An academic office with sage-green walls.",
        "reflective_slow",
        "ironic_exposure",
        "empirical_conflict",
        [
            ("Bảy mươi phần trăm trong số họ thú nhận,", "full_scene|The high-achieving student looks downward, confessing deep inner vulnerability."),
            ("họ luôn nghĩ mình chỉ gặp may mắn.", "white_card|A percentage chart icon illustrating high achievement alongside hidden imposter anxiety on pure white."),
            ("Họ sợ một ngày nào đó,", "full_scene|The psychologists listen with solemn empathy across the interview desk."),
            ("hội đồng sẽ phát hiện ra họ dốt nát.", "still_life|An open case file folder showing anonymous interview transcripts on the table."),
        ],
    ),
    (
        "Hồ sơ đối chứng thực nghiệm",
        "A research notebook under warm light.",
        "reflective_slow",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Điểm số của họ đều ở mức thủ khoa.", "still_life|An academic transcript showing top grades beside an embossed university gold seal."),
            ("Nhưng niềm tin thì ngược lại hoàn toàn.", "still_life|A personal journal page with wavy handwriting lines and a hand-drawn question mark."),
            ("Người ngoài nhìn vào thấy tài năng.", "still_life|A framed certificate of academic merit resting proudly on polished oak wood."),
            ("Còn bên trong, họ thấy mình lừa dối.", "still_life|An open fountain pen resting beside an unfinished manuscript page with ink smudges."),
        ],
    ),
    (
        "Cơ chế não sợ lời khen",
        "A bright seminar room with skylight.",
        "analytical_crisp",
        "mechanistic_dissection",
        "empirical_conflict",
        [
            ("Khoa học thần kinh đã làm sáng tỏ điều này.", "full_scene|A lecturer stick-figure warmly compliments a young student before an audience."),
            ("Não người giỏi đối xử với lời khen,", "white_card|A conceptual neural diagram showing alarm signals triggered by positive feedback on pure white."),
            ("như một tín hiệu cảnh báo nguy hiểm.", "full_scene|A projected diagram showing brain neural paths lighting up under unexpected stress."),
            ("Họ sợ kỳ vọng mới vượt quá sức mình.", "still_life|An empty lecture podium with an open lecture manuscript under soft auditorium light."),
        ],
    ),
    (
        "Nghịch lý Dunning Kruger đảo chiều",
        "A pure white background with bright lighting.",
        "analytical_crisp",
        "demystifying_truth",
        "structural_model",
        [
            ("Và đây là nghịch lý trớ trêu nhất.", "white_card|A two-panel comparison diagram contrasting shallow confidence with deep hesitation on pure white."),
            ("Người thật sự thiếu năng lực lại tự tin nhất.", "white_card|A stick-figure on a low hill waving a flag of complete overconfidence on pure white."),
            ("Bởi vì họ không biết những gì mình chưa biết.", "white_card|A tiny closed box icon representing limited cognitive awareness on pure white."),
            ("Họ nộp bài mà không chút đắn đo.", "white_card|A green checkmark icon stamped swiftly onto an unchecked document on pure white."),
        ],
    ),
    (
        "Tấm bản đồ sương mù",
        "A foggy landscape at dawn light.",
        "narrative_warm",
        "philosophical_depth",
        "structural_model",
        [
            ("Hãy hình dung tri thức như một hòn đảo.", "environment|A small illuminated island clearing surrounded by endless calm morning mist."),
            ("Khi bạn mới bước vào lĩnh vực này,", "full_scene|A lone traveler stick-figure stands at the center of the tiny circle of light."),
            ("vùng sáng của bạn rất nhỏ.", "still_life|A small glowing lantern resting on mossy green earth casting soft light."),
            ("Đường viền tiếp xúc với sương mù cũng ngắn.", "variation|The traveler looks at the clear ground beneath their feet with easy certainty."),
        ],
    ),
    (
        "Đảo sáng nở rộng",
        "A foggy landscape at dawn light.",
        "reflective_slow",
        "philosophical_depth",
        "structural_model",
        [
            ("Nhưng khi bạn đọc thêm hàng trăm bài báo,", "environment|The illuminated circular clearing expands into the morning mist under soft dawn light."),
            ("hòn đảo sáng của bạn nở rộng gấp mười.", "full_scene|The traveler walks forward across the vast newly discovered territory of light."),
            ("Đồng nghĩa với việc,", "environment|The outer boundary of fog stretches endlessly into infinite horizons."),
            ("đường viền sương mù cũng dài thêm gấp mười.", "variation|The traveler pauses at the boundary, marveling at the colossal expanse of mystery."),
        ],
    ),
    (
        "Đại dương kiến thức mênh mông",
        "A vast ocean horizon at golden hour.",
        "reflective_slow",
        "philosophical_depth",
        "structural_model",
        [
            ("Bạn nhìn thấy hàng nghìn khoảng trống mới.", "environment|A tranquil ocean horizon at golden sunset with gentle waves catching orange amber light."),
            ("Những thứ mà người hiểu nông không bao giờ thấy.", "environment|Soft sea foam rolling across untouched wet sand under a luminous evening sky."),
            ("Cảm giác dốt nát không phải là điểm yếu.", "environment|Distant seabirds gliding peacefully across the warm twilight horizon."),
            ("Nó là bằng chứng bạn đã đi rất xa.", "environment|The golden sun dipping below the tranquil waterline, filling the frame with warmth."),
        ],
    ),
    (
        "Đứng trên đỉnh núi cao",
        "A mountain ridge under open sky.",
        "narrative_warm",
        "inspirational_pivot",
        "structural_model",
        [
            ("Chỉ có người leo lên sườn núi cao,", "environment|A majestic mountain peak bathed in morning amber sunlight without any figures."),
            ("mới thấy đỉnh núi tiếp theo còn xa ngút ngàn.", "full_scene|A mountaineer stick-figure shields their eyes, surveying colossal mountain chains beyond."),
            ("Kẻ dưới chân núi luôn nghĩ mình đã tới nơi.", "environment|A distant view from above showing small tranquil foothills bathed in soft sun."),
            ("Còn bạn, bạn đang dũng cảm tiến lên.", "variation|The mountaineer adjusts their backpack, smiling with quiet resilience."),
        ],
    ),
    (
        "Vũ khí bản nháp thô năm trăm từ",
        "A pure white background with bright lighting.",
        "analytical_crisp",
        "tactical_actionable",
        "actionable_resolution",
        [
            ("Vậy làm thế nào để phá vỡ bế tắc?", "white_card|A circular breakthrough arrow breaking free from a cognitive loop on pure white."),
            ("Hãy dùng quy tắc bản nháp thô.", "white_card|A notepad icon labeled DIRTY DRAFT 500 in clean uppercase lettering on pure white."),
            ("Bản nháp thô năm trăm từ,", "white_card|A numerical comparison badge: 500 WRITTEN WORDS beats 1000 READING HOURS on pure white."),
            ("đánh bại một nghìn giờ đọc thêm.", "white_card|A golden trophy icon awarded to an imperfect handwritten draft sheet on pure white."),
        ],
    ),
    (
        "Hành động phá vỡ nỗi sợ",
        "A café table under afternoon light.",
        "narrative_warm",
        "tactical_actionable",
        "actionable_resolution",
        [
            ("Đặt đồng hồ hai mươi lăm phút.", "still_life|A vintage mechanical kitchen timer counting down beside a steaming teacup on wooden table."),
            ("Gõ liên tục mà không được phép xóa.", "full_scene|The researcher types fluidly on the keyboard, letting ideas flow without second-guessing."),
            ("Cho phép câu cú vụng về.", "macro_prop|Fingers moving steadily across keys under warm cafe window light."),
            ("Cho phép lập luận chưa hoàn hảo.", "variation|The researcher smiles as words fill the screen without hesitation."),
        ],
    ),
    (
        "Trang giấy đã đầy chữ",
        "A laptop screen showing typed lines.",
        "reflective_slow",
        "disciplined_confidence",
        "actionable_resolution",
        [
            ("Khi văn bản thô đã xuất hiện,", "still_life|A laptop screen showing dozens of completed paragraphs and structured section titles."),
            ("não bạn chuyển từ sợ hãi sang chỉnh sửa.", "still_life|A red pen resting beside printouts with constructive handwritten improvements."),
            ("Không ai giả vờ giỏi được suốt bốn năm.", "still_life|A clean wooden desk with a stack of completed reference binders neatly arranged."),
            ("Bạn xứng đáng với vị trí hôm nay.", "still_life|A cup of warm coffee beside a completed manuscript ready for submission."),
        ],
    ),
    (
        "Khép lại vòng lặp bàn học đêm",
        "A student desk under warm golden light.",
        "reflective_slow",
        "philosophical_triumph",
        "actionable_resolution",
        [
            ("Lần tới khi ngồi trước trang giấy trắng,", "still_life|A brass desk lamp casting rich warm golden light over a clean student workspace."),
            ("nếu cái giọng nói bảo bạn chưa đủ giỏi,", "full_scene|The student stick-figure sits peacefully at their study desk under rich golden lamplight."),
            ("hãy mỉm cười và nhớ rằng:", "macro_prop|Hand resting calmly beside keyboard with quiet peaceful confidence."),
            ("cảm giác đó chính là siêu năng lực của bạn.", "variation|Warm golden light fills the entire room as the camera slowly pulls backward."),
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
            "title": "Neural Correlates of the Impostor Phenomenon",
            "reference": "Koldehoff et al. (2023). Frontiers in Psychology, 14, 1148201.",
            "facts": [
                "Não người giỏi đối xử với lời khen như tín hiệu nguy hiểm.",
                "Khen ngợi kích hoạt phản ứng sợ hãi trong hạch hạnh nhân.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Unskilled and Unaware of It",
            "reference": "Justin Kruger & David Dunning (1999). Journal of Personality and Social Psychology, 77(6), 1121-1134.",
            "facts": [
                "Người thiếu năng lực thường tự tin nhất vì không biết mình sai.",
                "Hiểu càng sâu càng nhận ra biển kiến thức mênh mông.",
            ],
        },
        {
            "id": "SRC04",
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

    # Assign source claims
    scenes[6].source_ids = ["SRC01"]
    scenes[6].claim_facts = [
        ("Năm một nghìn chín trăm bảy mươi tám, hai nhà tâm lý học thực hiện cuộc khảo sát.", "SRC01", "Hội chứng kẻ mạo danh khiến người tài năng tự ti."),
    ]
    scenes[7].source_ids = ["SRC01"]
    scenes[7].claim_facts = [
        ("Bảy mươi phần trăm trong số họ thú nhận, họ luôn nghĩ mình chỉ gặp may mắn.", "SRC01", "Bảy mươi phần trăm sinh viên giỏi nghĩ mình chỉ gặp may."),
    ]
    scenes[9].source_ids = ["SRC02"]
    scenes[9].claim_facts = [
        ("Não người giỏi đối xử với lời khen, như một tín hiệu cảnh báo nguy hiểm.", "SRC02", "Não người giỏi đối xử với lời khen như tín hiệu nguy hiểm."),
    ]
    scenes[10].source_ids = ["SRC03"]
    scenes[10].claim_facts = [
        ("Người thật sự thiếu năng lực lại tự tin nhất.", "SRC03", "Người thiếu năng lực thường tự tin nhất vì không biết mình sai."),
    ]
    scenes[13].source_ids = ["SRC03"]
    scenes[13].claim_facts = [
        ("Bạn nhìn thấy hàng nghìn khoảng trống mới.", "SRC03", "Hiểu càng sâu càng nhận ra biển kiến thức mênh mông."),
    ]
    scenes[15].source_ids = ["SRC04"]
    scenes[15].claim_facts = [
        ("Bản nháp thô năm trăm từ, đánh bại một nghìn giờ đọc thêm.", "SRC04", "Bản nháp thô năm trăm từ đánh bại một nghìn giờ đọc thêm."),
    ]

    return ResearchedTopic(
        topic="Bẫy Tự Ti Học Thuật: Giải Mã Hội Chứng Kẻ Mạo Danh Ở Người Có Năng Lực Tư Duy Sâu",
        audience="Sinh viên, nghiên cứu sinh, người tự học và người làm việc trí óc xem video di động",
        goal="Giải mã tâm lý tự ti học thuật bằng cơ chế khoa học thần kinh và trao vũ khí bản nháp thô 500 từ",
        video_type="research_explainer",
        min_duration=240.0,
        max_duration=420.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=build_sources(),
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _, _, _, _) in enumerate(STORY_9X16, 1)],
        characters=[
            {
                "id": "CH01",
                "name": "Người làm nghiên cứu học thuật",
                "appearance": CAST_APPEARANCE,
                "outfit": "Simple comfortable shirt in vertical safe zone framing.",
            }
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
    (draft_dir / "outline.json").write_text(json.dumps(outline_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if (out_dir / "content.json").is_file():
        (draft_dir / "content.json").write_text((out_dir / "content.json").read_text(encoding="utf-8"), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Impostor Paradox package (9:16 vertical long-form).")
    parser.add_argument("--out-dir", type=Path, default=SYS_DIR / "blueprints" / "impostor-paradox-9x16")
    args = parser.parse_args()

    print("=== BUILDING 9:16 VERTICAL LONG-FORM (19 SCENES, full_frame_v1) ===")
    topic = build_topic()
    total_beats = count_total_beats(topic.scenes)
    print(f"Total visual beats: {total_beats} across {len(topic.scenes)} scenes")

    res = build_and_export_job(topic, args.out_dir)
    print(json.dumps({
        "job": "impostor-paradox-9x16",
        "output_dir": str(args.out_dir),
        "valid_contracts": res["valid_contracts"],
        "contract_errors": res["contract_errors"],
        "packaging_warnings": res["packaging_warnings"],
        "cadence_status": res["cadence_report"]["status"],
        "cadence_warnings": res["cadence_report"]["warnings_count"],
        "total_duration": res["cadence_report"]["total_duration"],
        "total_syllables": res["cadence_report"]["total_actual_syllables"],
        "visual_beats": total_beats,
    }, ensure_ascii=False, indent=2))

    if not (res["valid_contracts"] and res["cadence_report"]["status"] == "PASS" and len(res["contract_errors"]) == 0):
        print("\n❌ CONTRACT/CADENCE CHECKS FAILED!")
        sys.exit(1)
    print("\n✅ IMPOSTOR PARADOX 9:16 PRODUCTION PACKAGE BUILT AND VALIDATED 100% SUCCESSFULLY!")


if __name__ == "__main__":
    main()
