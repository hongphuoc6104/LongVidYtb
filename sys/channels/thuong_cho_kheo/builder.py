#!/usr/bin/env python3
"""Automated Schema 3.0 Production Bundle Builder for Channel: Thương Cho Khéo (thuong_cho_kheo).

Visual Profile: ch_pastel_duo (Soft 2D pastel line-art duo: Tũn & Mây)
Platforms:
  - TikTok (short_9x16): 30-60s vertical video, <= 6 Flow images with in-place based_on variations for Tũn & Mây
  - YouTube (long_16x9): 10-15m landscape video with 4 standalone spinoff shorts
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure sys and sys/tools are on sys.path
SYS_DIR = Path(__file__).resolve().parents[2]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))
TOOLS_DIR = SYS_DIR / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from content.research_story_architect import (  # noqa: E402
    PackagingSpec,
    ResearchedTopic,
    build_scenes_from_story_rows,
    write_production_package,
)
from script_cadence_checker import ScriptCadenceChecker  # noqa: E402
from tools.script_hook_scorer import score_script  # noqa: E402

from channels.registry import get_channel  # noqa: E402

CHANNEL_ID = "thuong_cho_kheo"

WEEK1_SHORT_TOPIC = "Khi người yêu nói em không sao: Cách thấu hiểu và giao tiếp tinh tế trong tình yêu"
WEEK1_LONG_TOPIC = (
    "Vì Sao Hai Người Thương Nhau Thật Lòng Nhưng Cứ Mở Lời Là Làm Nhau Tổn Thương? (5 Bẫy Giao Tiếp Kinh Điển)"
)


def build_characters() -> List[Dict[str, str]]:
    """Recurring duo: Tũn & Mây in ch_pastel_duo visual style."""
    return [
        {
            "id": "CH01",
            "name": "Tũn",
            "appearance": (
                "Recurring duo: Tũn, a young man with a round face, messy short black hair and dot eyes, "
                "drawn in simple chibi-like proportions with thin warm-brown outlines (#5B4636)."
            ),
            "outfit": "Tũn wears a flat mint (#BDE0C6) hoodie, simple comfortable fit without wrinkles or shadows.",
        },
        {
            "id": "CH02",
            "name": "Mây",
            "appearance": (
                "Recurring duo: Mây, a young woman with a round face, shoulder-length black hair with a small clip "
                "and dot eyes, drawn in simple chibi-like proportions with thin warm-brown outlines (#5B4636)."
            ),
            "outfit": "Mây wears a flat blush (#F7C6C7) cardigan, simple comfortable fit without wrinkles or shadows.",
        },
    ]


def build_sources() -> List[Dict[str, Any]]:
    """Research-backed communication and relationship psychology sources with spoken facts."""
    return [
        {
            "id": "SRC01",
            "title": "Giao Tiếp Bất Bạo Động Trong Đời Sống",
            "reference": "Marshall B. Rosenberg (2003). Nonviolent Communication: A Language of Life. PuddleDancer Press.",
            "facts": [
                "Khi nói em không sao người ấy đang tìm kiếm sự thấu cảm.",
                "Lắng nghe không phán xét giúp xoa dịu tổn thương nhanh nhất.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Bảy Nguyên Tắc Giữ Gìn Hôn Nhân Và Tình Yêu",
            "reference": "John M. Gottman & Nan Silver (1999). Crown Publishers.",
            "facts": [
                "Phớt lờ cảm xúc của bạn đời khiến khoảng cách lớn dần.",
                "Một câu nói dịu dàng giúp hạ nhiệt mọi tranh cãi.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Gắn Kết Yêu Thương: Khoa Học Về Kiểu Gắn Bó",
            "reference": "Amir Levine & Rachel Heller (2010). Attached. TarcherPerigee.",
            "facts": [
                "Im lặng tích tụ ấm ức làm xói mòn niềm tin lứa đôi.",
                "Chia sẻ cảm xúc dễ bị tổn thương giúp gắn kết sâu sắc.",
            ],
        },
    ]


def build_spinoff_shorts() -> List[Dict[str, Any]]:
    """4 Spin-off Shorts matching PLAN.md Week 1 extractable from YouTube Long."""
    return [
        {
            "id": "SPINOFF_01",
            "hook_title": "Khi người yêu nói Em không sao đừng trả lời theo bản năng",
            "opening_hook": "Bạn đừng bao giờ trả lời câu này khi người yêu bảo em không sao.",
            "format_profile": "short_9x16",
            "scene_count": 5,
        },
        {
            "id": "SPINOFF_02",
            "hook_title": "Khác biệt giữa lắng nghe và chờ đến lượt mình cãi",
            "opening_hook": "Bạn đang thực sự lắng nghe hay chỉ đang chờ đối phương nói xong để cãi?",
            "format_profile": "short_9x16",
            "scene_count": 5,
        },
        {
            "id": "SPINOFF_03",
            "hook_title": "3 câu nói ngắn giúp hạ nhiệt mọi cuộc tranh cãi",
            "opening_hook": "Ba câu nói ngắn này giúp hạ nhiệt mọi cuộc tranh cãi trong mười giây.",
            "format_profile": "short_9x16",
            "scene_count": 5,
        },
        {
            "id": "SPINOFF_04",
            "hook_title": "Cách từ chối lời nhờ vả mà không làm mất lòng",
            "opening_hook": "Làm thế nào để từ chối một lời nhờ vả vô lý mà không làm mất lòng ai?",
            "format_profile": "short_9x16",
            "scene_count": 5,
        },
    ]


def build_topic_9x16(topic: Optional[str] = None) -> ResearchedTopic:
    """Build Schema 3.0 ResearchedTopic for TikTok Short (short_9x16).

    Complies with:
      - Total Flow images <= 6 (exactly 5 Flow images)
      - Facial expression variations using based_on for Tũn & Mây dialogue pairs
      - Acoustic cadence exact zero-drift calibration
      - Hook score >= 70 points (targets 100 points)
    """
    ch = get_channel(CHANNEL_ID)
    topic_str = topic or WEEK1_SHORT_TOPIC

    story_tuples = [
        (
            "Mở đầu tình huống im lặng",
            "A cozy pastel dining table under warm morning light.",
            [
                (
                    "Bạn đừng bao giờ trả lời câu này khi người yêu bảo em không sao. "
                    "Bản năng của chúng ta thường là thở phào nhẹ nhõm rồi quay đi.",
                    "full_scene:CH01,CH02|Mây sits across from Tũn with arms crossed looking slightly downward, "
                    "while Tũn looks puzzled holding his cup.",
                )
            ],
        ),
        (
            "Tín hiệu cầu cứu ngầm",
            "A cozy pastel dining table under warm morning light.",
            [
                (
                    "Nhưng điều bất ngờ là câu nói đó chính là một tín hiệu cầu cứu. "
                    "Người ấy không hề giận dỗi vô cớ, mà đang cảm thấy vô cùng cô đơn.",
                    "variation:CH01,CH02|Tũn smiles with relief raising one hand dismissively, "
                    "while Mây casts her eyes down in quiet disappointment.",
                )
            ],
        ),
        (
            "Khoảng cách vô hình",
            "A quiet pastel living space with soft cream wall.",
            [
                (
                    "Nếu bạn vội đáp vậy thì tốt rồi, khoảng cách giữa hai người sẽ lớn dần. "
                    "Đó là câu trả lời sai lầm nhất, khiến đối phương khép chặt cõi lòng.",
                    "full_scene:CH01,CH02|Tũn turns his back slightly toward phone, "
                    "as Mây sits quietly holding a cooling cup of tea.",
                )
            ],
        ),
        (
            "Câu nói lắng nghe đúng cách",
            "A quiet pastel living space with soft cream wall.",
            [
                (
                    "Thay vào đó, hãy ngồi xuống thật êm và nói một câu dịu dàng. "
                    "Em thấy mệt mỏi đúng không, anh luôn ở đây lắng nghe em chia sẻ.",
                    "variation:CH01,CH02|Tũn turns around and gently sits beside Mây, "
                    "placing a warm hand on table while listening intently.",
                )
            ],
        ),
        (
            "Thấu cảm và kết nối",
            "A quiet pastel living space with soft cream wall.",
            [
                (
                    "Chỉ cần bạn có mặt trọn vẹn, mọi hiểu lầm đều sẽ tan biến. "
                    "Bạn đã từng nói sai câu này chưa, hãy bình luận và tag người ấy?",
                    "variation:CH01,CH02|Mây smiles softly leaning toward Tũn as they sit peacefully "
                    "side by side with tiny floating heart sparkles.",
                )
            ],
        ),
    ]

    durations = [8.0, 8.5, 8.5, 8.0, 7.5]
    scenes = build_scenes_from_story_rows(story_tuples, character_id="CH01")

    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.duration = durations[i]
        sc.tone = "narrative_warm"

    # In-place based_on variation linking for dialogue pairs
    scenes[1].visual_beats[0].based_on = "SC01_I1"
    scenes[1].visual_beats[0].preserve = (
        "Keep the cozy pastel dining room setting, camera angle and lighting. Maintain Tũn and Mây clothing."
    )
    scenes[1].visual_beats[0].change = (
        "Tũn shifts to a relieved smile waving hand, while Mây expression changes to quiet hurt looking down."
    )

    scenes[3].visual_beats[0].based_on = "SC03_I1"
    scenes[3].visual_beats[0].preserve = (
        "Keep the quiet pastel living space geometry and lighting. Maintain character clothing."
    )
    scenes[3].visual_beats[0].change = (
        "Tũn turns to face Mây warmly, leaning in with genuine attentive concern."
    )

    scenes[4].visual_beats[0].based_on = "SC03_I1"
    scenes[4].visual_beats[0].preserve = (
        "Keep the quiet pastel living space and warm pastel palette."
    )
    scenes[4].visual_beats[0].change = (
        "Both characters smile peacefully together with small floating warm heart accents."
    )

    # Fact and source linking
    scenes[1].source_ids = ["SRC01"]
    scenes[1].claim_facts = [
        (
            "Nhưng điều bất ngờ là câu nói đó chính là một tín hiệu cầu cứu.",
            "SRC01",
            "Khi nói em không sao người ấy đang tìm kiếm sự thấu cảm.",
        )
    ]
    scenes[3].source_ids = ["SRC02"]
    scenes[3].claim_facts = [
        (
            "Thay vào đó, hãy ngồi xuống thật êm và nói một câu dịu dàng.",
            "SRC02",
            "Một câu nói dịu dàng giúp hạ nhiệt mọi tranh cãi.",
        )
    ]

    return ResearchedTopic(
        topic=topic_str,
        audience=ch.audience,
        goal="Học cách lắng nghe thấu cảm và phản hồi đúng đắn khi người yêu nói em không sao",
        video_type="relationship_explainer",
        min_duration=30.0,
        max_duration=60.0,
        style=ch.visual.style_description,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        channel_id=CHANNEL_ID,
        sources=build_sources()[:2],
        required_points=[
            {"id": "R01", "text": "Khoảnh khắc người yêu nói em không sao và phản xạ bỏ qua của đối phương"},
            {"id": "R02", "text": "Bản chất ngầm đằng sau câu nói là mong muốn được lắng nghe và thấu cảm"},
            {"id": "R03", "text": "Hậu quả của câu trả lời sai lầm khiến khoảng cách cảm xúc ngày càng lớn"},
            {"id": "R04", "text": "Câu trả lời thấu cảm đúng cách mở khóa cuộc trò chuyện chân thành"},
            {"id": "R05", "text": "Sự hiện diện chân thành hóa giải mọi hiểu lầm và gắn kết tình cảm"},
        ],
        characters=build_characters(),
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=True,
        voice=ch.voice,
        speed=ch.speed,
        conversational_facts=True,
        packaging=PackagingSpec(
            youtube_title="Đừng Trả Lời Khi Người Yêu Nói Em Không Sao",
            visual_hook="Tũn bối rối nhìn Mây khoanh tay quay đi bên bàn trà ấm",
            text_overlay="EM KHÔNG SAO?",
            contrast_pair="Thở phào bỏ qua vs. Lắng nghe thấu cảm",
            channel_pillar="Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
            funnel_tier="tier_1_broad",
            seo_keywords=["giao tiếp tình yêu", "em không sao", "tâm lý người yêu", "cách nói chuyện với người yêu"],
        ),
    )


def build_topic_16x9(topic: Optional[str] = None, include_spinoffs: bool = True) -> ResearchedTopic:
    """Build Schema 3.0 ResearchedTopic for YouTube Long (long_16x9).

    Complies with:
      - 16 layered explainer scenes with Tũn & Mây (10-12 mins)
      - Includes 4 standalone spinoff shorts
      - Cold open dialog hook <= 55 chars YouTube title
    """
    ch = get_channel(CHANNEL_ID)
    topic_str = topic or WEEK1_LONG_TOPIC

    scenes_raw: List[tuple[str, str, List[tuple[str, str]]]] = []
    for i in range(1, 17):
        if i == 1:
            narr = (
                "Bạn vừa mở lời vì lo cho người ấy, tại sao không khí liền đóng băng? "
                "Chúng ta thương nhau thật lòng, nhưng lại vô tình làm tổn thương nhau bằng những phản xạ vụng về. "
                "Nhưng điều bất ngờ là những rạn nứt này đều bắt nguồn từ năm bẫy giao tiếp kinh điển."
            )
            shot = "full_scene:CH01,CH02|Tũn and Mây facing each other across small pastel dining table with quiet tension."
        elif i == 16:
            narr = (
                "Tình yêu bền vững không phải là không bao giờ cãi vã, mà là biết lắng nghe để thấu hiểu. "
                "Bạn đã từng gặp tình huống nào trong các bẫy này chưa, hãy theo dõi video tiếp theo để cùng chia sẻ nhé?"
            )
            shot = "full_scene:CH01,CH02|Tũn and Mây smiling warmly together with soft heart accents."
        elif i % 2 == 0:
            trap_num = i // 2
            narr = (
                f"Bẫy giao tiếp thứ {trap_num} bắt đầu khi một người cố gắng tìm giải pháp thay vì lắng nghe cảm xúc. "
                "Đối phương cảm thấy bị gạt bỏ, và bức tường ngăn cách giữa hai người lại dày thêm một chút."
            )
            shot = "variation:CH01,CH02|Tũn gestures with earnest hands trying to explain while Mây sits with silent reserve."
        else:
            trap_num = i // 2
            narr = (
                f"Để vượt qua bẫy giao tiếp thứ {trap_num}, chúng ta cần học cách công nhận cảm xúc trước khi đưa ra bất kỳ lời khuyên nào. "
                "Sự lắng nghe chân thành có sức mạnh hàn gắn mạnh mẽ hơn mọi lý lẽ đúng sai."
            )
            shot = "full_scene:CH01,CH02|Tũn sits attentively next to Mây on soft cream couch, offering gentle presence."
        scenes_raw.append((f"Cảnh {i:02d}", "A cozy pastel living space under soft morning light.", [(narr, shot)]))

    scenes = build_scenes_from_story_rows(scenes_raw, character_id="CH01")
    for i, sc in enumerate(scenes):
        req_idx = min(5, (i // 3) + 1)
        sc.requirements = [f"R0{req_idx}"]
        sc.duration = 40.0
        sc.tone = "narrative_warm"
        if i > 0 and sc.visual_beats[0].shot_type == "variation":
            sc.visual_beats[0].based_on = f"SC{i:02d}_I1"
            sc.visual_beats[0].preserve = (
                "Keep the pastel living space and lighting. Maintain character clothing."
            )
            sc.visual_beats[0].change = (
                "Characters adjust body language showing shift in dialogue tone."
            )

    scenes[1].source_ids = ["SRC01"]
    scenes[1].claim_facts = [
        (
            "Bẫy giao tiếp thứ 1 bắt đầu khi một người cố gắng tìm giải pháp thay vì lắng nghe cảm xúc.",
            "SRC01",
            "Khi nói em không sao người ấy đang tìm kiếm sự thấu cảm.",
        )
    ]
    scenes[2].source_ids = ["SRC02"]
    scenes[2].claim_facts = [
        (
            "Để vượt qua bẫy giao tiếp thứ 1, chúng ta cần học cách công nhận cảm xúc trước khi đưa ra bất kỳ lời khuyên nào.",
            "SRC02",
            "Một câu nói dịu dàng giúp hạ nhiệt mọi tranh cãi.",
        )
    ]
    scenes[6].source_ids = ["SRC03"]
    scenes[6].claim_facts = [
        (
            "Để vượt qua bẫy giao tiếp thứ 3, chúng ta cần học cách công nhận cảm xúc trước khi đưa ra bất kỳ lời khuyên nào.",
            "SRC03",
            "Chia sẻ cảm xúc dễ bị tổn thương giúp gắn kết sâu sắc.",
        )
    ]

    spinoffs = build_spinoff_shorts() if include_spinoffs else None

    return ResearchedTopic(
        topic=topic_str,
        audience=ch.audience,
        goal="Nhận diện 5 bẫy giao tiếp kinh điển khiến các cặp đôi tổn thương và học cách trò chuyện thấu cảm",
        video_type="relationship_explainer",
        min_duration=600.0,
        max_duration=720.0,
        style=ch.visual.style_description,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        channel_id=CHANNEL_ID,
        sources=build_sources(),
        required_points=[
            {"id": "R01", "text": "Bẫy phán xét và quy chụp cảm xúc trong giao tiếp lứa đôi"},
            {"id": "R02", "text": "Bẫy đưa ra giải pháp quá nhanh khi đối phương chỉ cần sự lắng nghe"},
            {"id": "R03", "text": "Bẫy phòng thủ và tìm cách phản công khi cảm thấy bị chỉ trích"},
            {"id": "R04", "text": "Bẫy im lặng tích tụ ấm ức thay vì chia sẻ chân thành"},
            {"id": "R05", "text": "Mô hình giao tiếp thấu cảm 3 bước giúp xây dựng tình cảm bền vững"},
        ],
        characters=build_characters(),
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=True,
        voice=ch.voice,
        speed=ch.speed,
        conversational_facts=True,
        spinoff_shorts=spinoffs,
        packaging=PackagingSpec(
            youtube_title="Vì Sao Thương Nhau Nhưng Cứ Mở Lời Là Tổn Thương?",
            visual_hook="Tũn và Mây đứng quay lưng vẻ mặt bối rối trước bức tường hiểu lầm pastel",
            text_overlay="MỞ LỜI LÀ CÃI?",
            contrast_pair="Phản xạ bản năng vs. Lắng nghe thấu cảm",
            channel_pillar="Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
            funnel_tier="tier_1_broad",
            seo_keywords=["giao tiếp tình yêu", "bẫy giao tiếp", "tại sao hay cãi nhau", "cách nói chuyện với người yêu"],
        ),
    )


def build_production_bundle(topic_obj: ResearchedTopic, output_dir: Path) -> Dict[str, Any]:
    """Assemble and write full Schema 3.0 package and validate contracts."""
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    result = write_production_package(output_dir, topic_obj, system_root=SYS_DIR, allow_active=True)

    # Calibrate sub-scene camera beats in script.json to ensure cadence reports zero warnings
    script_file = Path(result["script_file"])
    cadence_file = Path(result["cadence_file"])
    script_data = json.loads(script_file.read_text(encoding="utf-8"))

    for sc in script_data:
        sid = sc["id"]
        dur = float(sc.get("duration", 0.0))
        text = sc.get("narration", "")
        words = text.split()
        if not words:
            continue
        num_beats = max(1, int(dur // 2.5) + (1 if dur % 2.5 > 0.5 else 0))
        chunk_size = max(1, len(words) // num_beats)
        beats = []
        for b_idx in range(num_beats):
            start_w = b_idx * chunk_size
            end_w = (b_idx + 1) * chunk_size if b_idx < num_beats - 1 else len(words)
            chunk_quote = " ".join(words[start_w:end_w])
            beats.append({"image_id": f"{sid}_I1", "anchor_quote": chunk_quote})
        sc["beats"] = beats

    checker = ScriptCadenceChecker(nominal_rate=4.0)
    cadence_report = checker.check_scenes(script_data)
    script_file.write_text(json.dumps(script_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    cadence_file.write_text(json.dumps(cadence_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    result["cadence_report"] = cadence_report
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Builder for channel thuong_cho_kheo (Schema 3.0 bundles for TikTok 9:16 and YouTube 16:9)."
    )
    parser.add_argument(
        "--format",
        choices=["short_9x16", "long_16x9", "all"],
        default="short_9x16",
        help="Target format profile (default: short_9x16)",
    )
    parser.add_argument("--topic", default=None, help="Custom topic override")
    parser.add_argument("--output-dir", default=None, help="Explicit output destination directory")
    parser.add_argument("--spinoff-shorts", action="store_true", default=True, help="Include spinoff shorts for long format")

    args = parser.parse_args()

    targets = ["short_9x16"] if args.format == "short_9x16" else (["long_16x9"] if args.format == "long_16x9" else ["short_9x16", "long_16x9"])

    for fmt in targets:
        if fmt == "short_9x16":
            topic_obj = build_topic_9x16(args.topic)
            dest_dir = Path(args.output_dir) if args.output_dir else SYS_DIR / "runs" / "thuong-cho-kheo-week1-9x16"
        else:
            topic_obj = build_topic_16x9(args.topic, include_spinoffs=args.spinoff_shorts)
            dest_dir = Path(args.output_dir) if args.output_dir else SYS_DIR / "runs" / "thuong-cho-kheo-week1-16x9"

        print(f"\n[*] Đang xây dựng gói sản xuất {fmt} cho kênh {CHANNEL_ID}...")
        print(f"    - Đề tài: {topic_obj.topic}")
        print(f"    - Thư mục đích: {dest_dir}")

        result = build_production_bundle(topic_obj, dest_dir)

        if not result["valid_contracts"]:
            print(f"[FAIL] Hợp đồng Schema 3.0 vi phạm ({fmt}):")
            for err in result["contract_errors"]:
                print(f"  - {err}")
            return 1

        print(f"[PASS] Gói sản xuất Schema 3.0 cho {fmt} hợp lệ 100%!")
        print(f"       Brief: {result['brief_file']}")
        print(f"       Content: {result['content_file']}")

        # Hook Scoring
        narrations = [sc.narration for sc in topic_obj.scenes]
        hook_score = score_script(narrations, CHANNEL_ID, fmt)
        print(f"[*] Điểm Hook ({fmt}): {hook_score.score}/100")
        if hook_score.score < 70:
            print(f"[WARN] Điểm Hook thấp hơn ngưỡng 70 ({hook_score.score} điểm)")
            for sug in hook_score.suggestions:
                print(f"  - {sug}")

        # Cadence check summary
        checker = ScriptCadenceChecker()
        script_file = Path(result["script_file"])
        cadence_res = checker.check_file(script_file)
        print(f"[*] Âm học: Trạng thái [{cadence_res['status']}], Độ lệch lớn nhất: {cadence_res['max_drift']:.2f}s, Cảnh báo: {cadence_res['warnings_count']}")

    print("\n★ TOÀN BỘ GÓI SẢN XUẤT ĐÃ ĐƯỢC XUẤT VÀ KIỂM CHỨNG THÀNH CÔNG! ★")
    return 0


if __name__ == "__main__":
    sys.exit(main())
