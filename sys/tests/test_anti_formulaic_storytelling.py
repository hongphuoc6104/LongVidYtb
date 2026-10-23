"""E2E Anti-Formulaic Storytelling Benchmark & Verification Suite.

Validates that removing the 7 rigid, cookie-cutter constraints unlocks natural,
multi-domain storytelling while preserving all high-retention formulaic guardrails.
"""
from __future__ import annotations

import math
from collections import Counter
from pathlib import Path

from content.research_story_architect import (
    PackagingSpec,
    ResearchedTopic,
    build_brief_v3,
    build_content_v3,
    build_scenes_from_story_rows,
)
from content_contract import validate_content
from scripts.camera_motion import assign_scene_camera_effects, scene_camera_motions
from scripts.visual_quality import (
    check_scene_narrative_progression,
    check_visual_setting_diversity,
)
from tools.build_full_frame_acceptance import build_topic
from visual_pacing import check_see_say_beat_density

SYSTEM = Path(__file__).resolve().parents[1]


def shannon_entropy(items: list[str]) -> float:
    """Compute Shannon entropy in bits for a discrete sequence."""
    if not items:
        return 0.0
    counts = Counter(items)
    total = len(items)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def _non_desk_story_rows() -> list[tuple[str, str, list[tuple[str, str]]]]:
    """A 10-scene Behavioral Economics / Urban Traffic script with zero 'study desk' rooms."""
    return [
        (
            "Nghịch lý mở thêm làn đường",
            "An urban highway interchange at rush hour.",
            [
                ("Mở rộng đường cao tốc đôi khi chỉ làm kẹt xe nghiêm trọng hơn.", "full_scene|Commuters sit trapped on a newly widened six-lane highway."),
                ("Hàng tỷ đô la đổ vào bê tông, nhưng tốc độ di chuyển lại quay về vạch xuất phát.", "variation|A driver grips the steering wheel as the digital clock ticks forward."),
            ],
        ),
        (
            "Ảo giác giải phóng không gian",
            "A municipal planning office in soft daylight.",
            [
                ("Khi thấy nút thắt cổ chai, phản xạ tự nhiên của chúng ta là nới rộng chỗ hẹp.", "full_scene|An engineer points a marker at a congested road map on a planning table."),
                ("Ta tin rằng thêm diện tích mặt đường sẽ chia nhỏ lượng xe hiện có.", "still_life|A detailed traffic blueprint and pipe diagram resting under office lamps."),
            ],
        ),
        (
            "Khảo sát thực địa tại các đại lộ",
            "A traffic observation bridge in morning light.",
            [
                ("Nhưng dữ liệu thực địa từ các đợt mở rộng cao tốc lại kể một câu chuyện ngược lại.", "environment|A wide traffic observation bridge overlooking multi-lane roads in morning light."),
                ("Chỉ vài năm sau khi thông xe, lưu lượng phương tiện tăng vọt lấp đầy mọi làn mới.", "still_life|A field sensor screen showing traffic volume climbing back to 100 percent capacity."),
            ],
        ),
        (
            "Cơ chế nhu cầu cảm ứng",
            "A conceptual diagram studio under neutral light.",
            [
                ("Trong kinh tế học giao thông, hiện tượng này được gọi là nhu cầu cảm ứng.", "still_life|Two branching arrows on a printed economic chart showing hidden demand and supply."),
                ("Đường rộng hơn làm giảm chi phí thời gian tạm thời, kéo những người từng đi tàu chuyển sang lái xe.", "full_scene|Stick-figure commuters leave the train platform and walk toward parked cars."),
            ],
        ),
        (
            "Nghịch lý Braess trong mạng lưới",
            "A network model room under ambient glow.",
            [
                ("Nhà toán học Dietrich Braess thậm chí chứng minh một nghịch lý kỳ lạ hơn.", "full_scene|A researcher points at a network graph of two routes connected by a shortcut bridge."),
                ("Thêm một cây cầu tắt vào mạng lưới có thể khiến mọi tài xế đều đi chậm hơn trước.", "variation|All stick-figure cars crowd onto the middle shortcut bridge, creating a two-way jam."),
            ],
        ),
        (
            "Tại sao trực giác cá nhân đánh lừa hệ thống?",
            "A quiet tram stop in evening light.",
            [
                ("Mỗi người đều chọn lối đi có lợi nhất cho riêng mình ở thời điểm đó.", "environment|A quiet tram stop platform at dusk with distant avenue lights."),
                ("Nhưng khi hàng vạn người cùng tối ưu hóa cá nhân, điểm cân bằng chung lại sụp đổ.", "still_life|A transit schedule sheet and route map resting beside the quiet tram platform rails."),
            ],
        ),
        (
            "Đối chứng: Khi thành phố dỡ bỏ đường cao tốc",
            "A riverside urban park in bright daylight.",
            [
                ("Điều bất ngờ nhất xảy ra khi các đô thị làm điều ngược lại: dỡ bỏ đường cao tốc.", "environment|A restored stream and pedestrian parkway where an elevated highway once stood."),
                ("Tại Seoul, khi tháo dỡ tuyến đường xuyên tâm, giao thông quanh thành phố không hề tê liệt.", "still_life|A comparative transit speed chart on a display board beside the park stream."),
            ],
        ),
        (
            "Dịch chuyển hành vi thay vì đổ thêm bê tông",
            "A transit hub in morning daylight.",
            [
                ("Khi cung đường cũ biến mất, nhu cầu di chuyển tự phân bổ sang tàu điện và các khung giờ khác.", "full_scene|Passengers move smoothly between a metro entrance and a tree-lined walkway."),
                ("Hệ thống giao thông không phải là đường ống nước tĩnh, mà là một cơ thể thích nghi.", "still_life|An adaptive network map balancing train, bus and car flows on a display console."),
            ],
        ),
        (
            "Bài học cho mọi hệ thống quá tải",
            "An operations workplace under balanced overhead light.",
            [
                ("Quy luật này xuất hiện ngay trong cách chúng ta quản lý công việc hàng ngày.", "full_scene|A team lead reviews a workflow board with three focused task lanes."),
                ("Mở thêm kênh họp hay kéo dài giờ làm chỉ hút thêm việc vụn vặt vào lấp chỗ trống.", "variation|Extra sticky notes pile onto the board as the team lead pauses to reconsider."),
            ],
        ),
        (
            "Thiết kế giới hạn để giữ luồng thông suốt",
            "An elevated urban balcony at sunrise.",
            [
                ("Muốn giải quyết tắc nghẽn bền vững, đừng chỉ hỏi làm sao mở rộng sức chứa.", "environment|An elevated urban balcony at sunrise overlooking a balanced city transit corridor."),
                ("Hãy thiết kế lại chi phí lựa chọn để dòng chảy tự tìm về đúng luồng hiệu quả nhất.", "full_scene|A commuter steps onto a departing tram as traffic flows steadily beside it."),
            ],
        ),
    ]


def test_non_desk_topic_passes_narrative_progression_and_diversity() -> None:
    """Fix #1 & #4 & #5: A non-student-desk topic (Urban Economics) must pass setting progression,
    exhibit dynamic middle-act prosody modulation, and link coverage quotes to relevant sentences.
    """
    scenes = build_scenes_from_story_rows(_non_desk_story_rows())
    topic = ResearchedTopic(
        topic="Nghịch lý mở rộng đường cao tốc và cơ chế nhu cầu cảm ứng",
        audience="Người đi làm và người quan tâm tư duy hệ thống tại Việt Nam",
        goal="Hiểu vì sao mở thêm làn đường không giải quyết kẹt xe và cách áp dụng tư duy hệ thống.",
        video_type="research_explainer",
        aspect_ratio="16:9",
        format_profile="long_16x9",
        min_duration=90.0,
        max_duration=360.0,
        scenes=scenes,
        subtitles=False,
        voice="VietNarrator",
        speed=1.0,
        visual_pacing_profile="full_frame_v1",
        style="Hand-drawn 2D marker illustration, anonymous round-headed stick figures, flat muted teal and amber.",
        characters=[
            {
                "id": "CH01",
                "name": "Người quan sát",
                "appearance": "Anonymous round white head with thick black outline, dot eyes and thin black stick limbs.",
                "outfit": "Olive field jacket.",
            }
        ],
        required_points=[
            {"id": "R01", "text": "trạng thái điểm cân bằng chung sụp đổ khi tối ưu hóa cá nhân"},
            {"id": "R02", "text": "thiết kế lại chi phí lựa chọn để dòng chảy tự tìm về đúng luồng"},
        ],
        sources=[
            {
                "id": "SRC01",
                "title": "The Fundamental Law of Road Congestion",
                "reference": "Duranton & Turner (2011), American Economic Review 101(6), 2616-2652.",
                "facts": ["Lưu lượng phương tiện tăng tỷ lệ thuận với số làn đường mở thêm."],
            }
        ],
        conversational_facts=True,
        packaging=PackagingSpec(
            youtube_title="Vì Sao Càng Mở Rộng Đường Càng Kẹt Xe?",
            visual_hook="A six-lane highway jammed next to an empty shortcut diagram.",
            text_overlay="NGHỊCH LÝ ĐƯỜNG RỘNG",
            contrast_pair="Thêm làn đường và giảm tốc độ di chuyển",
        ),
    )
    # Attach requirements & claim to specific scenes where the matching sentence is the SECOND sentence
    topic.scenes[5].requirements = ["R01"]
    topic.scenes[9].requirements = ["R02"]
    topic.scenes[2].source_ids = ["SRC01"]
    topic.scenes[2].claim_facts = [
        (
            "Chỉ vài năm sau khi thông xe, lưu lượng phương tiện tăng vọt lấp đầy mọi làn mới.",
            "SRC01",
            "Lưu lượng phương tiện tăng tỷ lệ thuận với số làn đường mở thêm.",
        )
    ]

    # Attach explicit narrative_phase, allow_expression_shift, and enable_sound_design to verify schema v3 serialization
    topic.enable_sound_design = True
    topic.scenes[0].narrative_phase = "lived_friction"
    topic.scenes[2].narrative_phase = "empirical_conflict"
    topic.scenes[4].narrative_phase = "structural_model"
    topic.scenes[9].narrative_phase = "actionable_resolution"
    topic.scenes[0].visual_beats[1].allow_expression_shift = True

    from content.research_story_architect import compute_brief_hash
    from content_contract import validate_brief
    brief = build_brief_v3(topic)
    validate_brief(SYSTEM, brief)
    assert brief.get("enable_sound_design") is True
    b_hash = compute_brief_hash(brief)
    content = build_content_v3(topic, brief, b_hash)
    assert content["scenes"][0].get("narrative_phase") == "lived_friction"
    assert content["scenes"][0]["images"][1].get("allow_expression_shift") is True

    # 1. Scene Narrative Progression must pass even without 'study_desk' or 'laboratory'
    assert check_scene_narrative_progression(content["scenes"]) == []
    assert check_visual_setting_diversity(content["scenes"]) == []
    validate_content(SYSTEM, brief, 1, b_hash, content)

    # 4. Dynamic Prosody Wave: middle scenes (SC03..SC08) must NOT be 100% locked to 'analytical_crisp'
    middle_tones = [sc.get("tone") for sc in content["scenes"][2:8]]
    assert len(set(middle_tones)) >= 2, f"Expected dynamic middle tones, got flat {middle_tones}"

    # 5. Coverage Quote Semantic Matching: R01 & R02 match the 2nd sentence of SC06 and SC10, not blindly split('.')[0]
    cov_by_req = {c["requirement_id"]: c["quote"] for c in content["coverage"]}
    assert "điểm cân bằng chung" in cov_by_req["R01"]
    assert "chi phí lựa chọn" in cov_by_req["R02"]


def test_cold_open_beat_density_accepts_natural_hook_windows() -> None:
    """Fix #2: Cold open accepts 3..5 beats in [0, 5s) and 6..10 beats in [0, 12.5s),
    while still rejecting sluggish 1-beat or 2-beat openings.
    """
    # 3 beats in [0, 5s) and 7 beats in [0, 12.5s) -> natural dramatic pacing
    natural_scenes = [
        {
            "id": "SC01",
            "start": 0.0,
            "end": 6.2,
            "images": [
                {"id": "I1", "at": 0.0},
                {"id": "I2", "at": 1.8},
                {"id": "I3", "at": 3.5},
                {"id": "I4", "at": 5.1},
            ],
        },
        {
            "id": "SC02",
            "start": 6.2,
            "end": 13.0,
            "images": [
                {"id": "I5", "at": 0.0},
                {"id": "I6", "at": 2.1},
                {"id": "I7", "at": 4.2},
            ],
        },
    ]
    assert check_see_say_beat_density(natural_scenes) == []

    # Sluggish 1-beat cold open must still fail
    sluggish = [
        {
            "id": "SC01",
            "start": 0.0,
            "end": 6.2,
            "images": [{"id": "I1", "at": 0.0}],
        }
    ]
    errors = check_see_say_beat_density(sluggish)
    assert any("OPENING_VISUAL_DENSITY" in e for e in errors)


def test_acceptance_ending_beats_and_camera_entropy() -> None:
    """Fix #3 & #6: Ending beats across SC02..SC12 are no longer 100% identical 'Focus on the hands'
    macro_prop clones, and camera motion entropy across generic beats is > 1.5 bits (no 2-state ping-pong).
    """
    topic = build_topic()
    brief = build_brief_v3(topic)
    content = build_content_v3(topic, brief, "TEST_ENTROPY")
    validate_content(SYSTEM, brief, 1, "TEST_ENTROPY", content)

    tail_Focus_clones = [
        sc["images"][-1]["description"]
        for sc in content["scenes"][1:]
        if "Focus on the hands and the study object already named" in sc["images"][-1]["description"]
    ]
    assert len(tail_Focus_clones) == 0, f"Found mechanical tail clones: {tail_Focus_clones}"

    tail_shot_types = [sc["images"][-1]["shot_type"] for sc in content["scenes"][1:]]
    assert len(set(tail_shot_types)) >= 2, f"Expected diverse ending shot types, got {tail_shot_types}"

    # Verify camera motion diversity across a 6-beat generic scene (no ping-pong loop)
    generic_scene = {
        "id": "SC05",
        "camera": "",
        "images": [{"id": f"I{i}", "description": f"Character action step {i}"} for i in range(1, 7)],
        "beats": [{"image_id": f"I{i}", "effect": "cut"} for i in range(1, 7)],
    }
    motions = scene_camera_motions(generic_scene)
    assert shannon_entropy(motions) >= 1.5, f"Camera entropy too low ({shannon_entropy(motions):.2f} bits): {motions}"
    assert all(a != b for a, b in zip(motions, motions[1:], strict=False)), f"Adjacent duplicate camera motions: {motions}"

    # Verify diagram/white_card beats can use 'hold' when appropriate
    diagram_effects = assign_scene_camera_effects(["Sơ đồ đối chiếu hai nhánh trên nền trắng", "Wide establishing shot"])
    assert diagram_effects[0] == "hold"
    assert diagram_effects[1] == "zoom_out"


def test_character_outfit_and_expression_shift_flexibility() -> None:
    """Fix #7: Verify variation beats can explicitly request an expression shift in `change`
    without raising EXPRESSION_LOCK_REQUIRED, while anonymous cast jobs (1.1.0-1.3.0) do not
    inject the hardcoded '#8CCFE8 short-sleeve shirt' mascot lock into requested_prompt.
    """
    import copy
    from unittest.mock import MagicMock, patch

    import image_pipeline

    topic = build_topic()
    brief = build_brief_v3(topic)
    content = build_content_v3(topic, brief, "TEST_EXPR")

    # 7a. Explicit expression shift in 'change' passes validation even if 'preserve' omits 'expression'
    shifted = copy.deepcopy(content)
    variation = next(img for img in shifted["scenes"][0]["images"] if img.get("based_on"))
    variation["preserve"] = "Keep the exact room layout, desk and lamp."
    variation["change"] = "Expression shift: the student's eyebrows lift in sudden realization."
    validate_content(SYSTEM, brief, 1, "TEST_EXPR", shifted)

    # 7b. Anonymous cast version (1.3.0) does not append '#8CCFE8 short-sleeve shirt' in requested_prompt
    dummy_pilot = MagicMock()
    dummy_pilot.payload.return_value = content
    dummy_pilot.brief.return_value = (brief, "HASH")
    with patch("flow_management.prompt_pin", return_value={"version": "1.3.0"}):
        prompt_out = image_pipeline.requested_prompt(
            dummy_pilot, "job1", "ref:CH01", "A researcher in an olive field jacket.", "", "16:9", registration=True
        )
    assert "#8CCFE8" not in prompt_out
    assert "olive field jacket" in prompt_out

