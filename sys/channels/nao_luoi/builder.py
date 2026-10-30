#!/usr/bin/env python3
"""Automatic Schema 3.0 Production Bundle Builder for Channel: Não Lười (nao_luoi).

Channel: Não Lười (nao_luoi) — Niche: Tâm lý & hành vi đời thường
Platform routing:
  - TikTok: short_9x16 (mode: fast_short <= 7 Flow images + Remotion camera beats)
  - YouTube: long_16x9 (with 4 spinoff shorts extracted via omni_platform)

Supports custom input topic or defaults to Week 1 editorial roadmap from PLAN.md.
Calibrated to 100% Schema 3.0 contracts, Conversational Essayist cadence, and Hook score >= 70.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parents[3]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from channels.registry import (  # noqa: E402
    get_channel,
)
from content.research_story_architect import (  # noqa: E402
    DEFAULT_CHANNEL_PILLAR,
    PackagingSpec,
    ResearchedTopic,
    build_scenes_from_story_rows,
    validate_production_bundle,
    write_production_package,
)
from tools.script_cadence_checker import ScriptCadenceChecker  # noqa: E402
from tools.script_hook_scorer import score_script  # noqa: E402

CHANNEL_ID = "nao_luoi"

# -----------------------------------------------------------------------------
# WEEK 1 CANONICAL STORIES FROM PLAN.md
# -----------------------------------------------------------------------------

# Fast-Short #4: "Vì sao bạn thức tới 2 giờ sáng dù mắt đã díp lại? (Trả thù giờ đi ngủ)" (35s, 6 ảnh Flow)
WEEK1_FAST_SHORT_STORY: List[Tuple[str, str, str, str, str, List[Tuple[str, str]]]] = [
    (
        "Cú tát thức khuya lướt màn hình",
        "A dark bedroom under cold phone screen glow.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            (
                "Vì sao bạn thức tới hai giờ sáng dù mắt đã díp lại? Thế nhưng ngón tay vẫn tiếp tục lướt màn hình trong vô thức.",
                "full_scene:CH01|Researcher stickman lies under blanket in dark room, face lit by cold smartphone screen.",
            ),
        ],
    ),
    (
        "Ảo giác đòi lại quyền kiểm soát",
        "A pure ivory background with clean lighting.",
        "analytical_crisp",
        "demystifying_truth",
        "empirical_conflict",
        [
            (
                "Não bạn không hề muốn thức khuya để xem clip ngắn. Thực chất nó đang muốn đòi lại quyền kiểm soát cuộc sống.",
                "concept_metaphor:CH01|Researcher stickman looks pensively at an oversized pocket watch with hands spinning backward.",
            ),
        ],
    ),
    (
        "Khoa học giải mã trả thù giờ ngủ",
        "A university psychology research workspace.",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            (
                "Khoa học gọi hiện tượng này là sự trì hoãn giấc ngủ để trả thù.",
                "visual_diagram:none|A clean bold typography card reading TRẢ THÙ GIỜ NGỦ in crisp black lettering.",
            ),
            (
                "Cả ngày bạn đã phải gồng mình làm hài lòng cấp trên và đồng nghiệp.",
                "full_scene:CH01|Researcher sits at an office desk under high stacks of work folders.",
            ),
        ],
    ),
    (
        "Ốc đảo tự do đêm muộn",
        "A quiet cozy study corner under warm desk lamp.",
        "narrative_warm",
        "philosophical_anchor",
        "structural_model",
        [
            (
                "Đêm muộn trở thành ốc đảo tự do duy nhất bạn được là chính mình. Nhưng cái giá phải trả là sự kiệt sức vào sáng hôm sau.",
                "full_scene:CH01|Researcher sits calmly wrapped in a cozy blanket beside a window under crescent moonlight.",
            ),
        ],
    ),
    (
        "Quy tắc ngắt kết nối mười phút",
        "A sunny morning desk bathed in warm natural light.",
        "narrative_warm",
        "tactical_actionable",
        "actionable_resolution",
        [
            (
                "Hãy thử quy tắc ngắt kết nối mười phút trước khi lên giường. Bạn có hay thức khuya như vậy không? Hãy bình luận cho Não Lười biết nhé.",
                "macro_prop:CH01|Researcher smiles warmly from behind a tidy morning study desk beside a smartphone placed face-down on a wooden bedside table.",
            ),
        ],
    ),
]

# YouTube Long #1: "Tại Sao Càng Tự Trách Bản Thân Bạn Lại Càng Trì Hoãn? (Giải Mã Cơ Chế Phòng Vệ Của Não Bộ)" (16 scenes, 4 phases)
WEEK1_LONG_STORY: List[Tuple[str, str, str, str, List[Tuple[str, str]]]] = [
    # Phase 1: Lived friction (SC01-SC04)
    (
        "Bàn học đêm và màn hình nhấp nháy",
        "A dark study corner under soft desk lamp.",
        "narrative_warm",
        "lived_friction",
        [
            ("Vì sao bạn nằm lướt điện thoại cả tiếng đồng hồ dù bài chưa xong?", "full_scene:CH01|Researcher lies on bed under soft lamp glow holding a smartphone."),
            ("Nhưng điều bất ngờ là, bạn càng tự mắng thì tay lại càng không thể dừng lại.", "concept_metaphor:CH01|Researcher taps forehead beside a tall stack of pending documents."),
        ],
    ),
    (
        "Vòng xoáy tự trách bản thân",
        "A quiet room with deep evening shadows.",
        "narrative_warm",
        "lived_friction",
        [
            ("Hóa ra đây là phản ứng phòng vệ của não bộ chứ bạn không hề lười biếng.", "full_scene:CH01|Researcher sits pensively at wooden table with arms folded in mild regret."),
            ("Càng tự trách móc, lồng ngực bạn lại càng cảm thấy nặng nề hơn.", "concept_metaphor:CH01|A small charcoal weight rests on top of a hand-drawn chest outline."),
        ],
    ),
    (
        "Nghịch lý càng mắng càng liệt",
        "A simple minimalist room under soft ambient light.",
        "narrative_warm",
        "lived_friction",
        [
            ("Bạn nghĩ tự trách sẽ tạo động lực đứng dậy.", "full_scene:CH01|Researcher points sternly toward an open study notebook on desk."),
            ("Thế nhưng bàn tay lại tiếp tục tìm về điện thoại.", "concept_metaphor:CH01|A smartphone screen pulses with gentle pale blue light in the shadows."),
        ],
    ),
    (
        "Trốn chạy vào thế giới ảo",
        "A dim bedroom corner with moonlight outside window.",
        "narrative_warm",
        "lived_friction",
        [
            ("Lướt mạng xã hội là cách bạn tạm quên cảm giác tội lỗi.", "full_scene:CH01|Researcher stares quietly out the window at the distant crescent moon."),
            ("Một vòng lặp bế tắc không lối thoát cứ thế kéo dài.", "concept_metaphor:CH01|A circular charcoal arrow drawn on clean ground loops endlessly."),
        ],
    ),
    # Phase 2: Empirical conflict (SC05-SC08)
    (
        "Khoa học thần kinh về sự né tránh",
        "A university psychology research workspace.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Khoa học thần kinh khẳng định bạn không hề lười.", "visual_diagram:none|A clean white card displaying bold text: BẠN KHÔNG HỀ LƯỜI in black marker."),
            ("Giáo sư Timothy Pychyl đã chứng minh điều này qua thực nghiệm.", "full_scene:CH01|Researcher examines research papers on a sturdy analytical wooden table."),
        ],
    ),
    (
        "Báo động đỏ của hạch hạnh nhân",
        "A psychology laboratory with clean ivory background.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Khi bạn đối diện một công việc khó và mơ hồ,", "concept_metaphor:CH01|Researcher stands before an oversized question mark drawn on paper."),
            ("hạch hạnh nhân trong não bộ lập tức kích hoạt báo động.", "visual_diagram:none|A hand-drawn warning shield graphic stamped BÁO ĐỘNG CẢM XÚC in bold terracotta."),
        ],
    ),
    (
        "Vỏ não lý trí bị lấn át",
        "A cognitive research room with analytical boards.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Hạch hạnh nhân xem áp lực công việc như mối đe dọa sinh tồn.", "full_scene:CH01|Researcher steps back cautiously from a large imposing document folder."),
            ("Nó ra lệnh cho cơ thể phải né tránh để tự vệ.", "concept_metaphor:CH01|A small protective barrier appears around the researcher figure."),
        ],
    ),
    (
        "Trì hoãn là sự điều hòa cảm xúc",
        "A modern testing space with clean white boards.",
        "analytical_crisp",
        "empirical_conflict",
        [
            ("Trì hoãn thực chất là né tránh cảm giác tiêu cực tức thì.", "visual_diagram:none|Balance scale comparing short-term relief on one side to future guilt on the other."),
            ("Bộ não chỉ đang cố bảo vệ bạn khỏi sự căng thẳng.", "full_scene:CH01|Researcher places hand over heart with gentle realization and calm smile."),
        ],
    ),
    # Phase 3: Structural model (SC09-SC12)
    (
        "Bẫy cầu toàn và phản ứng đóng băng",
        "A clean studio corner with drafting equipment.",
        "narrative_warm",
        "structural_model",
        [
            ("Càng sợ làm không hoàn hảo, não bạn càng đóng băng.", "full_scene:CH01|Researcher stands motionless before a giant blank drawing sheet."),
            ("Nỗi sợ thất bại biến trang giấy trắng thành bức tường thành.", "concept_metaphor:CH01|A single blank sketchpad stands tall with a small doorway sketched at the base."),
        ],
    ),
    (
        "Tự trách tiếp thêm năng lượng cho nỗi sợ",
        "A quiet library desk under warm ceiling light.",
        "narrative_warm",
        "structural_model",
        [
            ("Khi bạn tự trách, bạn vô tình xác nhận mối đe dọa là có thật.", "full_scene:CH01|Researcher leans over desk studying a diagram of cognitive feedback loops."),
            ("Não bộ càng cảnh giác và càng muốn rút lui sâu hơn.", "concept_metaphor:CH01|A hand gently folds an origami crane on the clean wooden surface."),
        ],
    ),
    (
        "Sự kiệt sức của ý chí",
        "An open terrace study space under afternoon light.",
        "narrative_warm",
        "structural_model",
        [
            ("Ý chí của con người giống như một cục pin có hạn.", "visual_diagram:none|A simple hand-drawn battery icon with three solid black charge bars on clean white."),
            ("Dùng hết năng lượng để phán xét sẽ chẳng còn sức để hành động.", "full_scene:CH01|Researcher rests chin on hand looking thoughtfully at an open textbook."),
        ],
    ),
    (
        "Mô hình phòng vệ nhận thức",
        "A minimalist discussion corner with a chalkboard.",
        "narrative_warm",
        "structural_model",
        [
            ("Muốn phá vỡ bẫy này, bạn phải thay đổi cơ chế phản ứng.", "concept_metaphor:CH01|A hand draws a sharp right-angle bypass route around a roadblock symbol."),
            ("Chuyển từ chế độ tự trừng phạt sang chế độ tự thấu hiểu.", "full_scene:CH01|Researcher sketches a friendly cartoon character giving a supportive thumbs-up."),
        ],
    ),
    # Phase 4: Actionable resolution (SC13-SC16)
    (
        "Liều thuốc tự trắc ẩn của Kristin Neff",
        "A bright morning study table under golden sunlight.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Tiến sĩ Kristin Neff chỉ ra rằng sự tự trắc ẩn mới là chìa khóa.", "full_scene:CH01|Researcher sits upright at clean morning desk holding a warm teacup."),
            ("Hãy đối xử với bản thân như một người bạn thân đang gặp khó khăn.", "concept_metaphor:CH01|Two friendly stickmen share a high-five under bright morning sunlight."),
        ],
    ),
    (
        "Quy tắc một trăm hai mươi giây",
        "A fresh sunlit studio table with notebook and pen.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Khi thấy muốn trì hoãn, hãy áp dụng quy tắc một trăm hai mươi giây.", "macro_prop:none|A small clean sandglass sitting on a polished wooden desk grain."),
            ("Chỉ cam kết ngồi vào bàn và làm đúng hai phút.", "full_scene:CH01|Researcher writes smoothly on a fresh notepad without hesitation."),
        ],
    ),
    (
        "Hạ thấp ngưỡng cản tâm lý",
        "A peaceful study room with open window and breeze.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Hai phút quá ngắn để hạch hạnh nhân cảm thấy bị đe dọa.", "concept_metaphor:CH01|A towering mountain shrinks down into a small stepping stone in clean air."),
            ("Và khi đã bắt đầu, đà quán tính sẽ tự khắc đẩy bạn đi tiếp.", "full_scene:CH01|Researcher smiles with momentum, turning the page of completed work."),
        ],
    ),
    (
        "Khép vòng lặp và kết nối tiếp theo",
        "A serene morning balcony bathed in sunrise warmth.",
        "narrative_warm",
        "actionable_resolution",
        [
            ("Bạn không cần hoàn hảo để bắt đầu, hãy bắt đầu để dần hoàn thiện hơn.", "full_scene:CH01|Researcher looks out toward the golden morning sunrise with quiet confidence."),
            ("Bạn có muốn theo dõi tập tiếp theo cùng series tâm lý Não Lười không?", "concept_metaphor:CH01|A clean directional arrow points toward the upcoming episode card on white canvas."),
        ],
    ),
]

# Spinoff shorts definition for YouTube Long bundle
WEEK1_SPINOFF_DEFS = [
    {
        "id": "SPINOFF_01",
        "hook_title": "Vì sao gần deadline bạn lại muốn dọn phòng?",
        "opening_hook": "Vì sao càng gần deadline bạn lại muốn dọn phòng?",
        "format_profile": "short_9x16",
        "scene_count": 5,
    },
    {
        "id": "SPINOFF_02",
        "hook_title": "Bạn không lười: não đang đóng băng vì sợ hoàn hảo",
        "opening_hook": "Bạn không hề lười: não bạn đang bật chế độ đóng băng.",
        "format_profile": "short_9x16",
        "scene_count": 5,
    },
    {
        "id": "SPINOFF_03",
        "hook_title": "Quy tắc 120 giây đánh lừa bộ não đang trì hoãn",
        "opening_hook": "Quy tắc một trăm hai mươi giây đánh lừa sự trì hoãn.",
        "format_profile": "short_9x16",
        "scene_count": 5,
    },
    {
        "id": "SPINOFF_04",
        "hook_title": "Vì sao bạn thức tới 2 giờ sáng dù rất buồn ngủ?",
        "opening_hook": "Vì sao bạn thức tới hai giờ sáng dù mắt đã díp lại?",
        "format_profile": "short_9x16",
        "scene_count": 5,
    },
]


def _nao_luoi_cast() -> List[Dict[str, str]]:
    ch = get_channel(CHANNEL_ID)
    return [
        {
            "id": "CH01",
            "name": ch.persona,
            "appearance": ch.visual.cast_appearance,
            "outfit": ch.visual.outfit,
        }
    ]


# -----------------------------------------------------------------------------
# BUILDER FUNCTIONS
# -----------------------------------------------------------------------------

def build_fast_short_topic(topic_title: Optional[str] = None) -> ResearchedTopic:
    """Build a calibrated short_9x16 ResearchedTopic for channel 'nao_luoi' (<= 7 Flow images)."""
    ch = get_channel(CHANNEL_ID)
    title = topic_title or "Vì sao bạn thức tới 2 giờ sáng dù mắt đã díp lại? (Trả thù giờ đi ngủ)"

    story_tuples = [(t, s, r) for t, s, _, _, _, r in WEEK1_FAST_SHORT_STORY]
    scenes = build_scenes_from_story_rows(story_tuples, character_id="CH01")
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R0{i+1}"]
        sc.tone = WEEK1_FAST_SHORT_STORY[i][2]
        sc.narrative_phase = WEEK1_FAST_SHORT_STORY[i][4]

    scenes[2].source_ids = ["SRC01"]
    scenes[2].claim_facts = [
        (
            "Khoa học gọi hiện tượng này là sự trì hoãn giấc ngủ để trả thù.",
            "SRC01",
            "Trì hoãn giờ ngủ là cách tâm lý bù đắp tự do ban ngày.",
        )
    ]

    return ResearchedTopic(
        topic=title,
        audience=ch.audience,
        goal="Giải mã hiện tượng tâm lý trả thù giờ đi ngủ và trao giải pháp ngắt kết nối 10 phút",
        video_type="research_explainer",
        min_duration=30.0,
        max_duration=45.0,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        required_points=[{"id": f"R0{i+1}", "text": WEEK1_FAST_SHORT_STORY[i][0]} for i in range(5)],
        sources=[
            {
                "id": "SRC01",
                "title": "Bedtime Procrastination: A Self-Regulation Problem",
                "reference": "Floor M. Kroese et al. (2014). Frontiers in Psychology, 5, 611.",
                "facts": [
                    "Trì hoãn giờ ngủ là cách tâm lý bù đắp tự do ban ngày.",
                    "Tâm lý trả thù giờ ngủ xuất phát từ áp lực công việc.",
                ],
            }
        ],
        characters=_nao_luoi_cast(),
        scenes=scenes,
        channel_id=CHANNEL_ID,
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        packaging=PackagingSpec(
            youtube_title="Vì Sao Bạn Thức Tới 2 Giờ Sáng Dù Buồn Ngủ?",
            visual_hook="Nhân vật người que nằm lướt điện thoại trong phòng tối với màn hình phát sáng",
            text_overlay="TRẢ THÙ GIỜ NGỦ",
            contrast_pair="Áp lực ban ngày vs. Tự do giả tạo ban đêm",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=["thức khuya", "trì hoãn giờ ngủ", "tâm lý học", "gen z", "não lười"],
        ),
    )


def build_long_explainer_topic(
    topic_title: Optional[str] = None,
    spinoffs: bool = True,
) -> ResearchedTopic:
    """Build a calibrated long_16x9 ResearchedTopic for channel 'nao_luoi' with spinoff shorts."""
    ch = get_channel(CHANNEL_ID)
    title = topic_title or "Tại Sao Càng Tự Trách Bản Thân Bạn Lại Càng Trì Hoãn? (Giải Mã Cơ Chế Phòng Vệ Của Não Bộ)"

    story_tuples = [(t, s, r) for t, s, _, _, r in WEEK1_LONG_STORY]
    scenes = build_scenes_from_story_rows(story_tuples, character_id="CH01")
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = WEEK1_LONG_STORY[i][2]
        sc.narrative_phase = WEEK1_LONG_STORY[i][3]

    scenes[4].source_ids = ["SRC01"]
    scenes[4].claim_facts = [
        (
            "Giáo sư Timothy Pychyl đã chứng minh điều này qua thực nghiệm.",
            "SRC01",
            "Trì hoãn thực chất là né tránh căng thẳng, không phải lười biếng.",
        )
    ]

    spinoff_list = list(WEEK1_SPINOFF_DEFS) if spinoffs else []

    return ResearchedTopic(
        topic=title,
        audience=ch.audience,
        goal="Giải mã cơ chế phòng vệ tâm lý đằng sau sự trì hoãn và hướng dẫn kỹ thuật tự trắc ẩn",
        video_type="research_explainer",
        min_duration=480.0,
        max_duration=720.0,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        required_points=[{"id": f"R{i+1:02d}", "text": WEEK1_LONG_STORY[i][0]} for i in range(len(WEEK1_LONG_STORY))],
        sources=[
            {
                "id": "SRC01",
                "title": "Procrastination and Mood Regulation",
                "reference": "Timothy A. Pychyl & Fuschia M. Sirois (2013). Social and Personality Psychology Compass, 7(2), 115-127.",
                "facts": [
                    "Trì hoãn thực chất là né tránh căng thẳng, không phải lười biếng.",
                    "Hạch hạnh nhân xem áp lực công việc là mối đe dọa sinh tồn.",
                ],
            }
        ],
        characters=_nao_luoi_cast(),
        scenes=scenes,
        channel_id=CHANNEL_ID,
        subtitles=False,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        packaging=PackagingSpec(
            youtube_title="Càng Tự Trách Bạn Càng Trì Hoãn?",
            visual_hook="Nhân vật người que ngồi ôm đầu trước bàn học với chiếc điện thoại phát sáng",
            text_overlay="BẪY TỰ TRÁCH",
            contrast_pair="Tự trừng phạt căng thẳng vs. Tự trắc ẩn hành động",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=["trì hoãn", "tự trách bản thân", "tâm lý học hành vi", "tâm lý học", "não lười", "gen z"],
        ),
        spinoff_shorts=spinoff_list,
    )


# -----------------------------------------------------------------------------
# EXPORT & VALIDATION OPERATIONS
# -----------------------------------------------------------------------------

def export_fast_short(
    topic_title: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Export TikTok short_9x16 bundle (fast_short <= 7 Flow images)."""
    target_dir = output_dir or (SYS_DIR / "runs" / "nao-luoi-week1-9x16")
    topic = build_fast_short_topic(topic_title)
    if target_dir.exists():
        shutil.rmtree(target_dir)
    res = write_production_package(target_dir, topic, system_root=SYS_DIR)
    return res


def export_long_explainer(
    topic_title: Optional[str] = None,
    output_dir: Optional[Path] = None,
    spinoffs: bool = True,
) -> Dict[str, Any]:
    """Export YouTube long_16x9 bundle with attached spinoff_shorts."""
    target_dir = output_dir or (SYS_DIR / "runs" / "nao-luoi-week1-16x9")
    topic = build_long_explainer_topic(topic_title, spinoffs=spinoffs)
    if target_dir.exists():
        shutil.rmtree(target_dir)
    res = write_production_package(target_dir, topic, system_root=SYS_DIR)
    return res


def export_week1_bundle(output_root: Optional[Path] = None) -> Dict[str, Any]:
    """Export complete Week 1 production bundle: 1 YouTube Long + 1 TikTok Fast-Short."""
    root = output_root or (SYS_DIR / "runs")
    short_res = export_fast_short(output_dir=root / "nao-luoi-week1-9x16")
    long_res = export_long_explainer(output_dir=root / "nao-luoi-week1-16x9", spinoffs=True)
    return {
        "channel_id": CHANNEL_ID,
        "fast_short": short_res,
        "long_explainer": long_res,
    }


def validate_bundle(bundle_dir: Path) -> Dict[str, Any]:
    """Validate an exported production bundle: Schema 3.0 contracts, Hook score, and Cadence."""
    brief_path = bundle_dir / "brief.json"
    content_path = bundle_dir / "content.json"
    script_path = bundle_dir / "script.json"

    if not (brief_path.is_file() and content_path.is_file()):
        raise FileNotFoundError(f"Missing brief.json or content.json in {bundle_dir}")

    brief_data = json.loads(brief_path.read_text(encoding="utf-8"))
    content_data = json.loads(content_path.read_text(encoding="utf-8"))

    # 1. Schema 3.0 Production Bundle Contract Validation
    valid_contracts, contract_errors = validate_production_bundle(
        system_root=SYS_DIR,
        brief_data=brief_data,
        content_data=content_data,
        brief_revision=1,
    )

    # 2. Hook score check
    format_profile = brief_data.get("format_profile", "short_9x16")
    narrations = [sc["narration"] for sc in content_data.get("scenes", [])]
    hook_result = score_script(narrations, CHANNEL_ID, format_profile=format_profile)

    # 3. Acoustic Cadence Check
    checker = ScriptCadenceChecker(nominal_rate=4.0)
    if script_path.is_file():
        script_data = json.loads(script_path.read_text(encoding="utf-8"))
        cadence_res = checker.check_scenes(script_data)
    else:
        cadence_res = {}

    # 4. Total Flow images
    total_images = sum(len(sc.get("images", [])) for sc in content_data.get("scenes", []))

    return {
        "bundle_dir": str(bundle_dir),
        "format_profile": format_profile,
        "valid_contracts": valid_contracts,
        "contract_errors": contract_errors,
        "hook_score": hook_result.score,
        "hook_passed": hook_result.score >= 70,
        "hook_checks": hook_result.checks,
        "hook": hook_result.hook,
        "total_images": total_images,
        "fast_short_image_cap_passed": total_images <= 7 if format_profile == "short_9x16" else True,
        "cadence_report": cadence_res,
        "channel_profile": brief_data.get("channel_profile", {}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Builder for Channel 'nao_luoi' (Não Lười).")
    parser.add_argument(
        "--format",
        choices=["short_9x16", "long_16x9", "both"],
        default="short_9x16",
        help="Target production format profile",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Target output directory (default: sys/runs/nao-luoi-week1-<format>)",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Custom topic title (defaults to Week 1 topic in PLAN.md)",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate existing bundle at --out without re-exporting",
    )
    args = parser.parse_args()

    out_path = args.out
    if args.validate_only:
        if not out_path or not out_path.exists():
            print(f"[!] Target directory {out_path} does not exist for validation.")
            return 1
        summary = validate_bundle(out_path)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0 if summary["valid_contracts"] and summary["hook_passed"] else 1

    if args.format == "short_9x16":
        dest = out_path or (SYS_DIR / "runs" / "nao-luoi-week1-9x16")
        print(f"[*] Building TikTok Short (9:16 fast_short) at {dest}...")
        export_fast_short(topic_title=args.topic, output_dir=dest)
        summary = validate_bundle(dest)
        print(f"[✓] Bundle valid: {summary['valid_contracts']}")
        print(f"[✓] Flow images: {summary['total_images']} (cap <= 7: {summary['fast_short_image_cap_passed']})")
        print(f"[✓] Hook score: {summary['hook_score']} / 100 (passed: {summary['hook_passed']})")
        print(f"[✓] Hook: {summary['hook']}")
        if not summary["valid_contracts"] or not summary["hook_passed"]:
            return 1

    elif args.format == "long_16x9":
        dest = out_path or (SYS_DIR / "runs" / "nao-luoi-week1-16x9")
        print(f"[*] Building YouTube Long (16:9 explainer) at {dest}...")
        export_long_explainer(topic_title=args.topic, output_dir=dest, spinoffs=True)
        summary = validate_bundle(dest)
        print(f"[✓] Bundle valid: {summary['valid_contracts']}")
        print(f"[✓] Hook score: {summary['hook_score']} / 100 (passed: {summary['hook_passed']})")
        print(f"[✓] Hook: {summary['hook']}")
        if not summary["valid_contracts"] or not summary["hook_passed"]:
            return 1

    elif args.format == "both":
        root = out_path or (SYS_DIR / "runs")
        print(f"[*] Building full Week 1 bundle at {root}...")
        export_week1_bundle(output_root=root)
        s1 = validate_bundle(root / "nao-luoi-week1-9x16")
        s2 = validate_bundle(root / "nao-luoi-week1-16x9")
        print(f"[✓] Short bundle valid: {s1['valid_contracts']}, Hook: {s1['hook_score']} (passed: {s1['hook_passed']})")
        print(f"[✓] Long bundle valid: {s2['valid_contracts']}, Hook: {s2['hook_score']} (passed: {s2['hook_passed']})")
        if not s1["valid_contracts"] or not s2["valid_contracts"] or not s1["hook_passed"] or not s2["hook_passed"]:
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
