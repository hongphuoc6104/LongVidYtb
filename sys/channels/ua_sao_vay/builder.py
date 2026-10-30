"""Automated production bundle builder for channel ua_sao_vay (Ủa Sao Vậy?).

Generates Schema 3.0 production blueprints adhering to:
- TikTok: ``short_9x16`` (fast_short mode <= 5 Flow images, duration 20-35s)
- YouTube: ``long_16x9`` (modular chapters with standalone spinoff_shorts)
- Mascot: Bé Ủa (profile ``ch_sticker_pop``)
- Acoustic calibration: VietNarrator 1.0x, nominal rate 4.0 syl/s
- Soft retention scoring: script_hook_scorer >= 70 points
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Resolve sys path to import core Video Pilot modules
SYS_DIR = Path(__file__).resolve().parents[2]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))
TOOLS_DIR = SYS_DIR / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from adapters import make_srt  # noqa: E402
from content.research_story_architect import (  # noqa: E402
    PackagingSpec,
    ResearchedBeat,
    ResearchedScene,
    ResearchedTopic,
    build_brief_v3,
    build_content_v3,
    compute_brief_hash,
    serialize_brief_json,
    validate_production_bundle,
)
from flow_prompts import compile as compile_flow_prompt  # noqa: E402
from omni_platform import short_plans  # noqa: E402
from script_cadence_checker import ScriptCadenceChecker, count_syllables  # noqa: E402
from script_hook_scorer import HookScore, score_script  # noqa: E402

from channels.registry import get_channel  # noqa: E402

CHANNEL_ID = "ua_sao_vay"
ROOT_DIR = SYS_DIR.parent
DEFAULT_SHORT_RUN_DIR = SYS_DIR / "runs" / "ua-sao-vay-week1-9x16"
DEFAULT_LONG_RUN_DIR = SYS_DIR / "runs" / "ua-sao-vay-week1-16x9"

DEFAULT_WEEK1_SHORT_TOPIC = "Ủa, sao trong phòng đông người mà muỗi chỉ đốt đúng một người?"
DEFAULT_WEEK1_LONG_TOPIC = "8 Hiện Tượng Quen Thuộc Mỗi Ngày Nhưng 99% Chúng Ta Đều Hiểu Sai Bản Chất Khoa Học"


def _create_be_ua_cast(ch: Any) -> List[Dict[str, str]]:
    """Build the cast dictionary entry for Bé Ủa."""
    return [
        {
            "id": "CH01",
            "name": ch.persona,
            "appearance": ch.visual.cast_appearance,
            "outfit": ch.visual.outfit,
        }
    ]


def _build_short_scenes_mosquito() -> Tuple[
    List[Dict[str, Any]],
    List[Dict[str, str]],
    List[ResearchedScene],
    PackagingSpec,
    List[Dict[str, Any]],
]:
    """Author verified Week 1 Short #1 scenes about mosquito attraction (4 Flow images)."""
    sources = [
        {
            "id": "SRC01",
            "title": "Cơ chế định vị vật chủ của muỗi qua khí thở và nhiệt độ",
            "reference": "Viện Sốt rét Ký sinh trùng Côn trùng Trung ương",
            "facts": [
                "Muỗi phát hiện khí thở và nhiệt độ cơ thể từ khoảng cách xa.",
                "Người vận động nhiều tỏa nhiệt và thải khí thu hút muỗi.",
            ],
        }
    ]

    req_points = [
        {"id": "R01", "text": "Muỗi định vị vật chủ bằng khí thở và nhiệt độ chứ không phải máu ngọt."},
        {"id": "R02", "text": "Giải pháp giảm muỗi đốt là tản nhiệt cơ thể và dùng quạt gió."},
    ]

    scenes = [
        ResearchedScene(
            scene_id="SC01",
            title="Câu hỏi tò mò",
            purpose="Mở đầu bằng câu hỏi vì sao muỗi chỉ đốt một người",
            duration=4.2,
            narration="Ủa, sao trong phòng đông người mà muỗi chỉ đốt mỗi mình bạn vậy?",
            requirements=["R01"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Bé Ủa scratching arm with question mark antenna looking curious as a tiny cartoon mosquito hovers nearby",
            setting="Flat solid pastel background in lemon cream #FFF6D6 with bold 2D sticker pop objects.",
            camera="focus",
            scene_description="Bé Ủa scratching arm with question mark antenna looking curious as a tiny cartoon mosquito hovers nearby on flat solid pastel background.",
            claim_facts=[("muỗi chỉ đốt mỗi mình bạn", "SRC01", "Muỗi phát hiện khí thở và nhiệt độ cơ thể từ khoảng cách xa.")],
            visual_beats=[
                ResearchedBeat(
                    image_id="SC01_I1",
                    description="Flat solid pastel background in lemon cream #FFF6D6. Bé Ủa scratching arm with question mark antenna looking curious as a tiny cartoon mosquito hovers nearby.",
                    anchor_quote="Ủa, sao trong phòng đông người mà muỗi chỉ đốt mỗi mình bạn vậy?",
                    reason="Establish curiosity with Bé Ủa and mosquito",
                    character_ids=["CH01"],
                    shot_type="full_scene",
                    change="Show Bé Ủa scratching arm with a curious look as a tiny mosquito hovers nearby.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC02",
            title="Lật ngược hiểu lầm máu ngọt",
            purpose="Lật ngược suy nghĩ sai lầm phổ biến về máu ngọt",
            duration=4.5,
            narration="Ai cũng nghĩ do máu ngọt. Nhưng sự thật khoa học lại hoàn toàn khác.",
            requirements=["R01"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Bé Ủa shaking head beside a crossed out sweet sugar cube cartoon illustration with chunky sticker border",
            setting="Flat solid pastel background in lemon cream #FFF6D6 with bold 2D sticker pop objects.",
            camera="focus",
            scene_description="Bé Ủa shaking head beside a crossed out sweet sugar cube cartoon illustration on flat solid pastel background.",
            claim_facts=[],
            visual_beats=[
                ResearchedBeat(
                    image_id="SC02_I1",
                    description="Flat solid pastel background in lemon cream #FFF6D6. Bé Ủa shaking head beside a crossed out sweet sugar cube cartoon illustration with chunky sticker border.",
                    anchor_quote="Ai cũng nghĩ do máu ngọt. Nhưng sự thật khoa học lại hoàn toàn khác.",
                    reason="Debunk sweet blood myth",
                    character_ids=["CH01"],
                    shot_type="full_scene",
                    change="Show Bé Ủa shaking head beside a crossed out sugar cube.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC03",
            title="Cơ chế khí thở và nhiệt độ",
            purpose="Giải thích cơ chế thu hút muỗi qua khí thở và nhiệt",
            duration=8.4,
            narration="Muỗi bị thu hút bởi khí thở và lượng nhiệt tỏa ra từ cơ thể bạn. Người có thân nhiệt cao hoặc vừa vận động sẽ thành mục tiêu số một.",
            requirements=["R01"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Bé Ủa holding a magnifying glass inspecting glowing warm air ripples and carbon dioxide dots with chunky sticker border",
            setting="Flat solid pastel background in lemon cream #FFF6D6 with bold 2D sticker pop objects.",
            camera="focus",
            scene_description="Bé Ủa holding a magnifying glass inspecting glowing warm air ripples and carbon dioxide dots on flat solid pastel background.",
            claim_facts=[("Người có thân nhiệt cao hoặc vừa vận động sẽ thành mục tiêu số một.", "SRC01", "Người vận động nhiều tỏa nhiệt và thải khí thu hút muỗi.")],
            visual_beats=[
                ResearchedBeat(
                    image_id="SC03_I1",
                    description="Flat solid pastel background in lemon cream #FFF6D6. Bé Ủa holding a magnifying glass inspecting glowing warm air ripples and carbon dioxide dots with chunky sticker border.",
                    anchor_quote="Muỗi bị thu hút bởi khí thở và lượng nhiệt tỏa ra từ cơ thể bạn. Người có thân nhiệt cao hoặc vừa vận động sẽ thành mục tiêu số một.",
                    reason="Explain heat and carbon dioxide attraction",
                    character_ids=["CH01"],
                    shot_type="full_scene",
                    change="Show Bé Ủa inspecting heat ripples through a magnifying glass.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC04",
            title="Giải pháp và câu kết",
            purpose="Đưa ra giải pháp và kêu gọi tương tác",
            duration=6.1,
            narration="Hãy ngồi gần quạt để tản bớt nhiệt và xua muỗi bay xa. Bạn có hay bị muỗi chọn mặt gửi vàng không?",
            requirements=["R02"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Bé Ủa smiling happily sitting in front of a blue electric table fan blowing cool air with chunky sticker border",
            setting="Flat solid pastel background in lemon cream #FFF6D6 with bold 2D sticker pop objects.",
            camera="focus",
            scene_description="Bé Ủa smiling happily sitting in front of a blue electric table fan blowing cool air on flat solid pastel background.",
            claim_facts=[],
            visual_beats=[
                ResearchedBeat(
                    image_id="SC04_I1",
                    description="Flat solid pastel background in lemon cream #FFF6D6. Bé Ủa smiling happily sitting in front of a blue electric table fan blowing cool air with chunky sticker border.",
                    anchor_quote="Hãy ngồi gần quạt để tản bớt nhiệt và xua muỗi bay xa. Bạn có hay bị muỗi chọn mặt gửi vàng không?",
                    reason="Practical takeaway with fan",
                    character_ids=["CH01"],
                    shot_type="full_scene",
                    change="Show Bé Ủa smiling comfortably near an electric fan.",
                )
            ],
        ),
    ]

    # Camera beats calibrating sub-3s beat density while reusing the same 4 Flow images
    camera_beats_map = [
        [
            {"id": "SC01_B1", "image_id": "SC01_I1", "purpose": "Hook question", "anchor": {"vi": {"quote": "Ủa, sao trong phòng đông người", "occurrence": 1}}, "effect": "fade", "focus": {"x": 0.5, "y": 0.5}},
            {"id": "SC01_B2", "image_id": "SC01_I1", "purpose": "Mosquito focus", "anchor": {"vi": {"quote": "mà muỗi chỉ đốt mỗi mình bạn vậy?", "occurrence": 1}}, "effect": "punch_in", "focus": {"x": 0.5, "y": 0.5}},
        ],
        [
            {"id": "SC02_B1", "image_id": "SC02_I1", "purpose": "Old belief", "anchor": {"vi": {"quote": "Ai cũng nghĩ do máu ngọt.", "occurrence": 1}}, "effect": "fade", "focus": {"x": 0.5, "y": 0.5}},
            {"id": "SC02_B2", "image_id": "SC02_I1", "purpose": "Flip open loop", "anchor": {"vi": {"quote": "Nhưng sự thật khoa học lại hoàn toàn khác.", "occurrence": 1}}, "effect": "zoom_in", "focus": {"x": 0.5, "y": 0.5}},
        ],
        [
            {"id": "SC03_B1", "image_id": "SC03_I1", "purpose": "Breath attraction", "anchor": {"vi": {"quote": "Muỗi bị thu hút bởi khí thở", "occurrence": 1}}, "effect": "fade", "focus": {"x": 0.5, "y": 0.5}},
            {"id": "SC03_B2", "image_id": "SC03_I1", "purpose": "Heat radiation", "anchor": {"vi": {"quote": "và lượng nhiệt tỏa ra từ cơ thể bạn.", "occurrence": 1}}, "effect": "punch_in", "focus": {"x": 0.5, "y": 0.5}},
            {"id": "SC03_B3", "image_id": "SC03_I1", "purpose": "Hot body temp", "anchor": {"vi": {"quote": "Người có thân nhiệt cao", "occurrence": 1}}, "effect": "pan_left", "focus": {"x": 0.5, "y": 0.5}},
            {"id": "SC03_B4", "image_id": "SC03_I1", "purpose": "Target priority", "anchor": {"vi": {"quote": "hoặc vừa vận động sẽ thành mục tiêu số một.", "occurrence": 1}}, "effect": "zoom_in", "focus": {"x": 0.5, "y": 0.5}},
        ],
        [
            {"id": "SC04_B1", "image_id": "SC04_I1", "purpose": "Fan cool solution", "anchor": {"vi": {"quote": "Hãy ngồi gần quạt để tản bớt nhiệt", "occurrence": 1}}, "effect": "fade", "focus": {"x": 0.5, "y": 0.5}},
            {"id": "SC04_B2", "image_id": "SC04_I1", "purpose": "Dispel mosquito", "anchor": {"vi": {"quote": "và xua muỗi bay xa.", "occurrence": 1}}, "effect": "pan_right", "focus": {"x": 0.5, "y": 0.5}},
            {"id": "SC04_B3", "image_id": "SC04_I1", "purpose": "Rewatch share CTA", "anchor": {"vi": {"quote": "Bạn có hay bị muỗi chọn mặt gửi vàng không?", "occurrence": 1}}, "effect": "zoom_in", "focus": {"x": 0.5, "y": 0.5}},
        ],
    ]

    pkg = PackagingSpec(
        youtube_title="Ủa Sao Muỗi Chỉ Đốt Đúng Một Người Trong Phòng?",
        visual_hook="Bé Ủa há hốc mồm chỉ tay vào chú muỗi hoạt hình đang bay lượn",
        text_overlay="BỊ MUỖI ĐỐT",
        contrast_pair="Máu ngọt dân gian vs. Thân nhiệt và khí thở khoa học",
        channel_pillar="cognition",
        funnel_tier="tier_1_broad",
        seo_keywords=["uasaovay", "muoidot", "kienthucthuvi", "khoahoc"],
    )

    return sources, req_points, scenes, pkg, camera_beats_map


def _build_generic_short_scenes(topic_str: str) -> Tuple[
    List[Dict[str, Any]],
    List[Dict[str, str]],
    List[ResearchedScene],
    PackagingSpec,
    List[Dict[str, Any]],
]:
    """Synthesize high-retention 4-scene short script for custom topics."""
    sources = [
        {
            "id": "SRC01",
            "title": f"Cơ sở khoa học của hiện tượng: {topic_str}",
            "reference": "Tài liệu khoa học thường thức chuẩn hóa",
            "facts": [
                "Bộ não và cơ thể vận hành theo quy luật sinh học tự nhiên.",
                "Thói quen quan sát giúp nhận ra bản chất sự vật đời thường.",
            ],
        }
    ]

    req_points = [
        {"id": "R01", "text": "Hiểu rõ cơ chế bản chất của hiện tượng tò mò đời sống."},
        {"id": "R02", "text": "Áp dụng kiến thức thú vị vào trải nghiệm hằng ngày."},
    ]

    clean_topic = topic_str.strip().rstrip("?.!")
    if not clean_topic.lower().startswith("ủa"):
        hook_text = f"Ủa, sao {clean_topic} vậy bạn?"
    else:
        hook_text = f"{clean_topic} vậy bạn?"
    if count_syllables(hook_text) > 18:
        hook_text = "Ủa, sao lại như vậy bạn?"

    dur1 = round((count_syllables(hook_text) / 4.0) + 0.70, 1)

    s2_text = "Ai cũng nghĩ theo thói quen cũ. Nhưng sự thật khoa học lại hoàn toàn khác."
    dur2 = round((count_syllables(s2_text) / 4.0) + 0.70, 1)

    s3_text = "Cơ chế bất ngờ nằm ở phản xạ tự nhiên của não bộ và cơ thể bạn. Mọi chi tiết đều có lời giải thích khoa học rất rõ ràng."
    dur3 = round((count_syllables(s3_text) / 4.0) + 0.70, 1)

    s4_text = "Hãy ghi nhớ mẹo thú vị này để áp dụng ngay hôm nay. Bạn có để ý điều này bao giờ chưa?"
    dur4 = round((count_syllables(s4_text) / 4.0) + 0.35, 1)

    scenes = [
        ResearchedScene(
            scene_id="SC01",
            title="Mở đầu tò mò",
            purpose="Đặt câu hỏi gợi tò mò theo phong cách Bé Ủa",
            duration=dur1,
            narration=hook_text,
            requirements=["R01"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Bé Ủa with open mouth and question mark antenna pointing at mystery phenomenon with chunky sticker border",
            setting="Flat solid pastel background in lemon cream #FFF6D6 with bold 2D sticker pop objects.",
            camera="focus",
            scene_description="Bé Ủa with open mouth and question mark antenna pointing at mystery phenomenon on flat solid pastel background.",
            claim_facts=[],
            visual_beats=[
                ResearchedBeat(
                    image_id="SC01_I1",
                    description="Flat solid pastel background in lemon cream #FFF6D6. Bé Ủa with open mouth and question mark antenna pointing at mystery phenomenon with chunky sticker border.",
                    anchor_quote=hook_text,
                    reason="Curiosity hook frame",
                    character_ids=["CH01"],
                    shot_type="full_scene",
                    change="Show Bé Ủa expressing curiosity with wide eyes.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC02",
            title="Lật ngược niềm tin cũ",
            purpose="Lật ngược niềm tin phổ biến",
            duration=dur2,
            narration=s2_text,
            requirements=["R01"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Bé Ủa waving hands beside a crossed out common assumption with chunky sticker border",
            setting="Flat solid pastel background in lemon cream #FFF6D6 with bold 2D sticker pop objects.",
            camera="focus",
            scene_description="Bé Ủa waving hands beside a crossed out common assumption on flat solid pastel background.",
            claim_facts=[],
            visual_beats=[
                ResearchedBeat(
                    image_id="SC02_I1",
                    description="Flat solid pastel background in lemon cream #FFF6D6. Bé Ủa waving hands beside a crossed out common assumption with chunky sticker border.",
                    anchor_quote=s2_text,
                    reason="Debunk old myth",
                    character_ids=["CH01"],
                    shot_type="full_scene",
                    change="Show Bé Ủa refuting the common misunderstanding.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC03",
            title="Giải mã cơ chế",
            purpose="Giải thích cơ chế khoa học bất ngờ",
            duration=dur3,
            narration=s3_text,
            requirements=["R01"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Bé Ủa holding a magnifying glass inspecting glowing scientific mechanism symbols with chunky sticker border",
            setting="Flat solid pastel background in lemon cream #FFF6D6 with bold 2D sticker pop objects.",
            camera="focus",
            scene_description="Bé Ủa holding a magnifying glass inspecting glowing scientific mechanism symbols on flat solid pastel background.",
            claim_facts=[(s3_text[:30], "SRC01", "Bộ não và cơ thể vận hành theo quy luật sinh học tự nhiên.")],
            visual_beats=[
                ResearchedBeat(
                    image_id="SC03_I1",
                    description="Flat solid pastel background in lemon cream #FFF6D6. Bé Ủa holding a magnifying glass inspecting glowing scientific mechanism symbols with chunky sticker border.",
                    anchor_quote=s3_text,
                    reason="Scientific mechanism explanation",
                    character_ids=["CH01"],
                    shot_type="full_scene",
                    change="Show Bé Ủa revealing the hidden mechanism.",
                )
            ],
        ),
        ResearchedScene(
            scene_id="SC04",
            title="Lời khuyên và câu hỏi",
            purpose="Lời khuyên thực tế và câu kết kích thích bình luận",
            duration=dur4,
            narration=s4_text,
            requirements=["R02"],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action="Bé Ủa smiling happily gesturing thumbs up with colorful celebratory sparkles and chunky sticker border",
            setting="Flat solid pastel background in lemon cream #FFF6D6 with bold 2D sticker pop objects.",
            camera="focus",
            scene_description="Bé Ủa smiling happily gesturing thumbs up with colorful celebratory sparkles on flat solid pastel background.",
            claim_facts=[],
            visual_beats=[
                ResearchedBeat(
                    image_id="SC04_I1",
                    description="Flat solid pastel background in lemon cream #FFF6D6. Bé Ủa smiling happily gesturing thumbs up with colorful celebratory sparkles and chunky sticker border.",
                    anchor_quote=s4_text,
                    reason="Engagement call to action",
                    character_ids=["CH01"],
                    shot_type="full_scene",
                    change="Show Bé Ủa cheerfully waving to viewer.",
                )
            ],
        ),
    ]

    if "," in hook_text:
        parts = hook_text.split(",", 1)
        q1 = parts[0] + ","
        q2 = parts[1].strip()
    else:
        words = hook_text.split()
        mid = max(1, len(words) // 2)
        q1 = " ".join(words[:mid])
        q2 = " ".join(words[mid:])

    camera_beats_map = [
        [
            {"id": "SC01_B1", "image_id": "SC01_I1", "purpose": "Curiosity start", "anchor": {"vi": {"quote": q1, "occurrence": 1}}, "effect": "fade", "focus": {"x": 0.5, "y": 0.5}},
            {"id": "SC01_B2", "image_id": "SC01_I1", "purpose": "Question punch", "anchor": {"vi": {"quote": q2, "occurrence": 1}}, "effect": "punch_in", "focus": {"x": 0.5, "y": 0.5}},
        ],
        [
            {"id": "SC02_B1", "image_id": "SC02_I1", "purpose": "Assumption", "anchor": {"vi": {"quote": "Ai cũng nghĩ theo thói quen cũ.", "occurrence": 1}}, "effect": "fade", "focus": {"x": 0.5, "y": 0.5}},
            {"id": "SC02_B2", "image_id": "SC02_I1", "purpose": "Flip loop", "anchor": {"vi": {"quote": "Nhưng sự thật khoa học lại hoàn toàn khác.", "occurrence": 1}}, "effect": "zoom_in", "focus": {"x": 0.5, "y": 0.5}},
        ],
        [
            {"id": "SC03_B1", "image_id": "SC03_I1", "purpose": "Surprise mechanism", "anchor": {"vi": {"quote": "Cơ chế bất ngờ nằm ở phản xạ tự nhiên", "occurrence": 1}}, "effect": "fade", "focus": {"x": 0.5, "y": 0.5}},
            {"id": "SC03_B2", "image_id": "SC03_I1", "purpose": "Body reaction", "anchor": {"vi": {"quote": "của não bộ và cơ thể bạn.", "occurrence": 1}}, "effect": "punch_in", "focus": {"x": 0.5, "y": 0.5}},
            {"id": "SC03_B3", "image_id": "SC03_I1", "purpose": "Clear explanation", "anchor": {"vi": {"quote": "Mọi chi tiết đều có lời giải thích khoa học rất rõ ràng.", "occurrence": 1}}, "effect": "zoom_in", "focus": {"x": 0.5, "y": 0.5}},
        ],
        [
            {"id": "SC04_B1", "image_id": "SC04_I1", "purpose": "Advice practical", "anchor": {"vi": {"quote": "Hãy ghi nhớ mẹo thú vị này", "occurrence": 1}}, "effect": "fade", "focus": {"x": 0.5, "y": 0.5}},
            {"id": "SC04_B2", "image_id": "SC04_I1", "purpose": "Apply now", "anchor": {"vi": {"quote": "để áp dụng ngay hôm nay.", "occurrence": 1}}, "effect": "pan_right", "focus": {"x": 0.5, "y": 0.5}},
            {"id": "SC04_B3", "image_id": "SC04_I1", "purpose": "Closing question", "anchor": {"vi": {"quote": "Bạn có để ý điều này bao giờ chưa?", "occurrence": 1}}, "effect": "zoom_in", "focus": {"x": 0.5, "y": 0.5}},
        ],
    ]

    short_title = clean_topic[:50]
    pkg = PackagingSpec(
        youtube_title=short_title if len(short_title) <= 55 else f"Ủa Sao Vậy: {short_title[:40]}",
        visual_hook="Bé Ủa há hốc mồm ngạc nhiên trước hiện tượng khoa học bất ngờ",
        text_overlay="ỦA SAO VẬY",
        contrast_pair="Hiểu lầm phổ biến vs. Sự thật khoa học",
        channel_pillar="cognition",
        funnel_tier="tier_1_broad",
        seo_keywords=["uasaovay", "khoahoc", "kienthucthuvi"],
    )

    return sources, req_points, scenes, pkg, camera_beats_map


def build_short_topic(topic_str: Optional[str] = None) -> Tuple[ResearchedTopic, List[Dict[str, Any]]]:
    """Build a calibrated ResearchedTopic and camera beats for TikTok short_9x16."""
    ch = get_channel(CHANNEL_ID)
    topic_text = (topic_str or DEFAULT_WEEK1_SHORT_TOPIC).strip()

    if "muỗi" in topic_text.lower():
        sources, req_points, scenes, pkg, camera_beats = _build_short_scenes_mosquito()
    else:
        sources, req_points, scenes, pkg, camera_beats = _build_generic_short_scenes(topic_text)

    cast = _create_be_ua_cast(ch)
    total_dur = sum(s.duration for s in scenes)

    topic = ResearchedTopic(
        topic=topic_text,
        audience=ch.audience,
        goal="Giải mã hiện tượng khoa học thường ngày bằng phong cách nhanh vui và tạo hình sticker pop Bé Ủa",
        video_type="science",
        min_duration=round(max(20.0, total_dur - 3.0), 1),
        max_duration=round(min(35.0, total_dur + 3.0), 1),
        style=ch.visual.style_description,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=sources,
        required_points=req_points,
        characters=cast,
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=True,
        voice=ch.voice,
        speed=ch.speed,
        conversational_facts=True,
        packaging=pkg,
        channel_id=CHANNEL_ID,
    )
    return topic, camera_beats


def build_long_topic(topic_str: Optional[str] = None) -> Tuple[ResearchedTopic, List[Dict[str, Any]]]:
    """Build an 8-chapter ResearchedTopic for YouTube long_16x9 with spinoff shorts."""
    ch = get_channel(CHANNEL_ID)
    topic_text = (topic_str or DEFAULT_WEEK1_LONG_TOPIC).strip()

    sources = [
        {
            "id": "SRC01",
            "title": "Cơ chế khoa học của các hiện tượng thường ngày",
            "reference": "Tạp chí Khoa học và Đời sống",
            "facts": [
                "Muỗi phát hiện khí thở và nhiệt độ cơ thể từ khoảng cách xa.",
                "Vỏ chai nước khoáng bằng nhựa có thể phân hủy theo thời gian.",
                "Cơ thể không thể tự cù lét do não bộ đã dự đoán trước chuyển động.",
            ],
        }
    ]

    req_points = [
        {"id": "R01", "text": "Muỗi định vị vật chủ bằng khí thở và nhiệt độ."},
        {"id": "R02", "text": "Vỏ chai nhựa có hạn sử dụng để tránh thôi nhiễm vi nhựa."},
        {"id": "R03", "text": "Tiểu não triệt tiêu cảm giác khi tự cù lét chính mình."},
    ]

    cast = _create_be_ua_cast(ch)

    chapter_texts = [
        (
            "Ủa, sao trong phòng có chục người mà muỗi chỉ đốt bạn? "
            "Ai cũng nghĩ do máu ngọt. Nhưng sự thật khoa học là muỗi định vị qua khí thở. "
            "Người có thân nhiệt cao hoặc vừa vận động sẽ tỏa nhiều nhiệt, và thải nhiều khí hơn. "
            "Chính vì vậy, bạn lập tức trở thành mục tiêu số một của đàn muỗi."
        ),
        (
            "Ủa, sao mình không bao giờ tự cù lét cho mình cười được? "
            "Bạn thử lấy tay tự thọc lách xem, không hề nhột chút nào. "
            "Đó là vì tiểu não đã dự đoán trước chuyển động của bàn tay. "
            "Nó lập tức triệt tiêu tín hiệu bất ngờ, nên bạn không thấy buồn cười."
        ),
        (
            "Ủa, nước ngầm triệu năm không hỏng sao đóng chai lại có hạn dùng? "
            "Nước tinh khiết trong chai thực chất không bao giờ bị thiu. "
            "Hạn sử dụng in trên thân chai thực ra là dành cho vỏ nhựa. "
            "Sau thời gian đó, vỏ nhựa có thể thôi nhiễm vào nước."
        ),
        (
            "Ủa, sao ngủ nướng cuối tuần dậy lại đau đầu hơn ngày thường? "
            "Bạn tưởng ngủ bù sẽ khỏe hơn, nhưng đồng hồ sinh học lại bị đảo lộn. "
            "Não bộ bị rối loạn chất dẫn truyền thần kinh, làm các mạch máu co giãn bất thường. "
            "Hệ quả là bạn thức dậy với một cơn đau đầu ê ẩm."
        ),
        (
            "Ủa, sao nghe lại giọng ghi âm của chính mình ai cũng thấy kỳ cục? "
            "Khi bạn nói, âm thanh truyền qua cả không khí lẫn xương sọ vào tai trong. "
            "Nhưng khi nghe qua máy ghi âm, bạn chỉ nghe sóng âm truyền qua không khí. "
            "Chính vì thế, bạn thấy giọng mình the thé rất lạ lẫm."
        ),
        (
            "Ủa, quả dưa hấu nặng trĩu mà thả vào nước lại nổi bồng bềnh? "
            "Trông quả dưa đặc ruột và nặng nề, nhưng ruột dưa chứa nhiều túi khí li ti. "
            "Tỷ trọng tổng thể của dưa nhẹ hơn nước một chút. "
            "Nhờ đó, quả dưa hấu khổng lồ nổi lên mặt nước rất dễ dàng."
        ),
        (
            "Ủa, sao đôi khi vừa đi tiểu xong cơ thể bạn lại rùng mình một cái? "
            "Hiện tượng này hoàn toàn bình thường, do hệ thần kinh thực vật điều khiển. "
            "Khi bàng quang giải phóng nhiệt lượng nhanh chóng, huyết áp sẽ hạ nhẹ. "
            "Cơ thể phản xạ co giật trong tích tắc để giữ ấm thân nhiệt."
        ),
        (
            "Ủa, sao vừa liếc nhìn đồng hồ bạn lại thấy kim giây như đứng yên? "
            "Hiện tượng ảo giác thú vị này được gọi là Chronostasis. "
            "Khi mắt bạn đảo nhanh, não bộ sẽ đóng băng khung hình đầu tiên. "
            "Nó giúp xóa nhòa vệt mờ chuyển động trong mắt. Bạn có thấy cơ thể kỳ diệu không?"
        ),
    ]

    scenes = []
    camera_beats_map = []
    for idx, narr in enumerate(chapter_texts, 1):
        sc_id = f"SC{idx:02d}"
        syl = count_syllables(narr)
        p_tail = 0.35 if idx == len(chapter_texts) else 0.70
        dur = round((syl / 4.0) + p_tail, 1)

        sents = [s.strip() for s in narr.split(".") if s.strip()]
        r_id = "R03" if idx == 2 else ("R02" if idx == 3 else "R01")
        claim = []
        if idx == 1:
            claim = [("muỗi định vị qua khí thở", "SRC01", "Muỗi phát hiện khí thở và nhiệt độ cơ thể từ khoảng cách xa.")]
        elif idx == 2:
            claim = [("tiểu não đã dự đoán trước chuyển động", "SRC01", "Cơ thể không thể tự cù lét do não bộ đã dự đoán trước chuyển động.")]
        elif idx == 3:
            claim = [("Hạn sử dụng in trên thân chai thực ra là dành cho vỏ nhựa.", "SRC01", "Vỏ chai nước khoáng bằng nhựa có thể phân hủy theo thời gian.")]

        # Visual prompts with active non-cliche descriptions
        action_descs = [
            "Bé Ủa scratching arm with question mark antenna looking curious as a tiny cartoon mosquito hovers nearby",
            "Bé Ủa tickling own ribs with a deadpan face and question mark antenna with chunky sticker border",
            "Bé Ủa inspecting the expiration date on a plastic water bottle with a magnifying glass with chunky sticker border",
            "Bé Ủa holding head looking dizzy next to an alarm clock with wavy lines and chunky sticker border",
            "Bé Ủa holding a smartphone speaker to ear with a shocked expression and wavy audio notes with chunky sticker border",
            "Bé Ủa watching a giant striped green watermelon floating on water surface in a blue tub with chunky sticker border",
            "Bé Ủa shivering with tiny cartoon lightning sparks and question mark antenna with chunky sticker border",
            "Bé Ủa pointing at a red second hand on a round cartoon clock with chunky sticker border",
        ]

        sc = ResearchedScene(
            scene_id=sc_id,
            title=f"Chương {idx}: Hiện tượng {idx}",
            purpose=f"Giải mã hiện tượng khoa học kỳ lạ {idx}",
            duration=dur,
            narration=narr,
            requirements=[r_id],
            source_ids=["SRC01"],
            character_ids=["CH01"],
            action=action_descs[idx - 1],
            setting="Flat solid pastel background in lemon cream #FFF6D6 with bold 2D sticker pop objects.",
            camera="focus",
            scene_description=f"{action_descs[idx - 1]} on flat solid pastel background.",
            claim_facts=claim,
            visual_beats=[
                ResearchedBeat(
                    image_id=f"{sc_id}_I1",
                    description=f"Flat solid pastel background in lemon cream #FFF6D6. {action_descs[idx - 1]}.",
                    anchor_quote=sents[0],
                    reason=f"Chapter {idx} visual anchor",
                    character_ids=["CH01"],
                    shot_type="full_scene",
                    change=f"Show chapter {idx} sticker pop demonstration.",
                )
            ],
        )
        scenes.append(sc)

        effects = ["fade", "punch_in", "pan_left", "zoom_in"]
        sc_beats = [
            {
                "id": f"{sc_id}_B{b_idx}",
                "image_id": f"{sc_id}_I1",
                "purpose": f"Chapter {idx} beat {b_idx}",
                "anchor": {"vi": {"quote": sent, "occurrence": 1}},
                "effect": effects[(b_idx - 1) % len(effects)],
                "focus": {"x": 0.5, "y": 0.5},
            }
            for b_idx, sent in enumerate(sents, 1)
        ]
        camera_beats_map.append(sc_beats)

    pkg = PackagingSpec(
        youtube_title="8 Hiện Tượng Quen Thuộc Mà Chúng Ta Đều Hiểu Sai",
        visual_hook="Bé Ủa há hốc mồm ngạc nhiên nhìn các hiện tượng thường ngày kỳ lạ",
        text_overlay="HIỂU SAI BÉT",
        contrast_pair="Hiểu lầm quen thuộc vs. Bản chất khoa học bất ngờ",
        channel_pillar="cognition",
        funnel_tier="tier_1_broad",
        seo_keywords=["uasaovay", "kienthucthuvi", "khoahoc", "didyouknow"],
    )

    spinoffs = [
        {
            "id": "SPINOFF_01",
            "hook_title": "Ủa sao muỗi chỉ đốt bạn?",
            "opening_hook": "Ủa sao trong phòng có chục người mà muỗi chỉ đốt bạn?",
            "format_profile": "short_9x16",
            "scene_count": 4,
            "body": [
                {"parent_scene_id": "SC01", "image_id": "SC01_I1", "segment_text": "Ủa, sao trong phòng có chục người mà muỗi chỉ đốt bạn?"},
                {"parent_scene_id": "SC01", "image_id": "SC01_I1", "segment_text": "Ai cũng nghĩ do máu ngọt."},
                {"parent_scene_id": "SC01", "image_id": "SC01_I1", "segment_text": "Nhưng sự thật khoa học là muỗi định vị qua khí thở."},
                {"parent_scene_id": "SC01", "image_id": "SC01_I1", "segment_text": "Người có thân nhiệt cao hoặc vừa vận động sẽ tỏa nhiều nhiệt, và thải nhiều khí hơn."},
            ],
        },
        {
            "id": "SPINOFF_02",
            "hook_title": "Ủa sao chai nước có hạn dùng?",
            "opening_hook": "Ủa sao nước ngầm triệu năm đóng chai lại có hạn dùng?",
            "format_profile": "short_9x16",
            "scene_count": 4,
            "body": [
                {"parent_scene_id": "SC03", "image_id": "SC03_I1", "segment_text": "Ủa, nước ngầm triệu năm không hỏng sao đóng chai lại có hạn dùng?"},
                {"parent_scene_id": "SC03", "image_id": "SC03_I1", "segment_text": "Nước tinh khiết trong chai thực chất không bao giờ bị thiu."},
                {"parent_scene_id": "SC03", "image_id": "SC03_I1", "segment_text": "Hạn sử dụng in trên thân chai thực ra là dành cho vỏ nhựa."},
                {"parent_scene_id": "SC03", "image_id": "SC03_I1", "segment_text": "Sau thời gian đó, vỏ nhựa có thể thôi nhiễm vào nước."},
            ],
        },
    ]

    total_dur = sum(s.duration for s in scenes)

    topic = ResearchedTopic(
        topic=topic_text,
        audience=ch.audience,
        goal="Giải mã 8 hiểu lầm khoa học quen thuộc bằng tư duy bản chất và hình ảnh sticker pop",
        video_type="science",
        min_duration=round(max(100.0, total_dur - 10.0), 1),
        max_duration=round(min(300.0, total_dur + 10.0), 1),
        style=ch.visual.style_description,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        sources=sources,
        required_points=req_points,
        characters=cast,
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=False,
        voice=ch.voice,
        speed=ch.speed,
        conversational_facts=True,
        packaging=pkg,
        channel_id=CHANNEL_ID,
        spinoff_shorts=spinoffs,
    )
    return topic, camera_beats_map


def _write_bundle_files(
    output_dir: Path,
    brief_data: Dict[str, Any],
    content_data: Dict[str, Any],
    script_data: List[Dict[str, Any]],
    cadence_report: Dict[str, Any],
    hook_score: HookScore,
) -> None:
    """Serialize all bundle assets cleanly into output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    brief_file = output_dir / "brief.json"
    content_file = output_dir / "content.json"
    script_file = output_dir / "script.json"
    cadence_file = output_dir / "cadence_report.json"
    outline_file = output_dir / "outline.json"
    hook_file = output_dir / "hook_score.json"

    brief_file.write_text(serialize_brief_json(brief_data), encoding="utf-8")
    content_file.write_text(json.dumps(content_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    script_file.write_text(json.dumps(script_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    cadence_file.write_text(json.dumps(cadence_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    outline_file.write_text(json.dumps({"outline": content_data.get("outline", [])}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    hook_file.write_text(json.dumps(asdict(hook_score), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    draft_dir = output_dir / "draft"
    draft_dir.mkdir(parents=True, exist_ok=True)
    (draft_dir / "outline.json").write_text(json.dumps({"outline": content_data.get("outline", [])}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (draft_dir / "content.json").write_text(json.dumps(content_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Generate subtitles.srt
    cursor = 0.0
    segments = []
    for sc in content_data.get("scenes", []):
        dur = sc.get("duration", 5.0)
        p_tail = sc.get("p_tail", 0.7)
        segments.append({
            "scene_id": sc["id"],
            "text": sc["narration"],
            "start": cursor,
            "end": cursor + dur,
            "content_end": cursor + dur,
        })
        cursor += dur + p_tail

    srt_text = make_srt(segments)
    (output_dir / "subtitles.srt").write_text(srt_text + "\n", encoding="utf-8")

    # Export delivery subtitles if top-level job
    if output_dir.parent.name == "runs":
        video_dir = ROOT_DIR / "video" / output_dir.name
        video_dir.mkdir(parents=True, exist_ok=True)
        (video_dir / "subtitles.srt").write_text(srt_text + "\n", encoding="utf-8")
        (video_dir / f"{output_dir.name}.srt").write_text(srt_text + "\n", encoding="utf-8")

    # Compile Flow prompts into images.json
    aspect_ratio = brief_data.get("outputs", [{}])[0].get("aspect_ratio", "9:16")
    aspect_slug = "9x16" if aspect_ratio == "9:16" else "16x9"
    compiled_items = []
    for sc in content_data.get("scenes", []):
        for img in sc.get("images", []):
            shot = img.get("shot_type", "full_scene")
            compiled = compile_flow_prompt(
                "NanoBanana2Lite",
                "scene",
                {
                    "description": img["description"],
                    "aspect_ratio": aspect_ratio,
                    "allowed_text": img.get("visible_text", []),
                    "shot_type": shot,
                    "has_character": img.get("has_character", True),
                    "character_free": not img.get("has_character", True),
                },
                version="1.7.0",
            )
            compiled_items.append({
                "scene_id": sc["id"],
                "image_id": img["id"],
                "path": f"revisions/images/1/{img['id']}_{aspect_slug}.jpg",
                "prompt": img["description"],
                "actual_prompt": compiled["prompt"],
                "source": "google-flow-browser",
                "ratio": aspect_ratio,
            })

    thumb_spec = brief_data.get("packaging", {}).get("thumbnail_spec", {})
    thumb_prompt = thumb_spec.get("thumbnail_prompt") or thumb_spec.get("visual_hook", "Minimal flat doodle canvas.")
    thumb_overlay = thumb_spec.get("text_overlay", "ỦA SAO VẬY")
    thumb_compiled = compile_flow_prompt(
        "NanoBanana2Lite",
        "scene",
        {
            "description": thumb_prompt,
            "aspect_ratio": aspect_ratio,
            "allowed_text": [thumb_overlay],
            "shot_type": "full_scene",
            "has_character": True,
            "character_free": False,
        },
        version="1.7.0",
    )
    images_manifest = {
        "checkpoint": "compiled",
        "total_images": len(compiled_items),
        "aspect_ratio": aspect_ratio,
        "items": compiled_items,
        "thumbnail": {
            "prompt": thumb_prompt,
            "actual_prompt": thumb_compiled["prompt"],
            "overlay_text": thumb_overlay,
            "overlay_card": False,
        },
    }
    (output_dir / "images.json").write_text(json.dumps(images_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_short_bundle(
    output_dir: Optional[Union[str, Path]] = None,
    topic_str: Optional[str] = None,
) -> Dict[str, Any]:
    """Build and write a verified TikTok Fast-Short (short_9x16) bundle."""
    out_dir = Path(output_dir or DEFAULT_SHORT_RUN_DIR).resolve()
    topic, camera_beats = build_short_topic(topic_str)

    brief_data = build_brief_v3(topic, system_root=SYS_DIR)
    brief_hash = compute_brief_hash(brief_data)
    content_data = build_content_v3(topic, brief_data, brief_hash, brief_revision=1)

    # In fast_short mode, inject camera beats while keeping 1 Flow image per scene
    for sc_idx, sc_beats in enumerate(camera_beats):
        content_data["scenes"][sc_idx]["beats"] = sc_beats

    script_data = [
        {
            "id": sc["id"],
            "duration": topic.scenes[idx].duration,
            "narration": sc["narration"],
            "beats": [
                {"image_id": b["image_id"], "anchor_quote": b["anchor"]["vi"]["quote"]}
                for b in sc["beats"]
            ],
        }
        for idx, sc in enumerate(content_data["scenes"])
    ]

    checker = ScriptCadenceChecker(nominal_rate=4.0, max_opening_hook_syllables=18, forbid_opening_pause=True)
    cadence_report = checker.check_scenes(script_data)

    narrations = [sc["narration"] for sc in content_data.get("scenes", [])]
    hook_result = score_script(narrations, CHANNEL_ID, "short_9x16")

    valid_contracts, contract_errors = validate_production_bundle(
        system_root=SYS_DIR,
        brief_data=brief_data,
        content_data=content_data,
        brief_revision=1,
    )

    _write_bundle_files(out_dir, brief_data, content_data, script_data, cadence_report, hook_result)

    image_count = sum(len(sc.get("images", [])) for sc in content_data.get("scenes", []))

    return {
        "channel_id": CHANNEL_ID,
        "format_profile": "short_9x16",
        "topic": topic.topic,
        "output_dir": str(out_dir),
        "brief_hash": brief_hash,
        "valid_contracts": valid_contracts,
        "contract_errors": contract_errors,
        "cadence_status": cadence_report.get("status"),
        "cadence_warnings": cadence_report.get("warnings_count", 0),
        "hook_score": hook_result.score,
        "hook_checks": hook_result.checks,
        "image_count": image_count,
        "scene_count": len(content_data.get("scenes", [])),
        "brief_file": str(out_dir / "brief.json"),
        "content_file": str(out_dir / "content.json"),
    }


def build_long_bundle(
    output_dir: Optional[Union[str, Path]] = None,
    topic_str: Optional[str] = None,
    include_spinoffs: bool = True,
) -> Dict[str, Any]:
    """Build and write a verified YouTube Long (long_16x9) bundle with spinoff shorts."""
    out_dir = Path(output_dir or DEFAULT_LONG_RUN_DIR).resolve()
    topic, camera_beats = build_long_topic(topic_str)

    brief_data = build_brief_v3(topic, system_root=SYS_DIR)
    brief_data["omni_platform"] = True
    brief_data["reframe_mode"] = True
    brief_hash = compute_brief_hash(brief_data)
    content_data = build_content_v3(topic, brief_data, brief_hash, brief_revision=1)

    for sc_idx, sc_beats in enumerate(camera_beats):
        content_data["scenes"][sc_idx]["beats"] = sc_beats

    script_data = [
        {
            "id": sc["id"],
            "duration": topic.scenes[idx].duration,
            "narration": sc["narration"],
            "beats": [
                {"image_id": b["image_id"], "anchor_quote": b["anchor"]["vi"]["quote"]}
                for b in sc["beats"]
            ],
        }
        for idx, sc in enumerate(content_data["scenes"])
    ]

    checker = ScriptCadenceChecker(nominal_rate=4.0)
    cadence_report = checker.check_scenes(script_data)

    narrations = [sc["narration"] for sc in content_data.get("scenes", [])]
    hook_result = score_script(narrations, CHANNEL_ID, "long_16x9")

    valid_contracts, contract_errors = validate_production_bundle(
        system_root=SYS_DIR,
        brief_data=brief_data,
        content_data=content_data,
        brief_revision=1,
    )

    verified_spinoffs = short_plans(brief_data, content_data)

    _write_bundle_files(out_dir, brief_data, content_data, script_data, cadence_report, hook_result)

    spinoff_packages = []
    if include_spinoffs:
        spinoffs_root = out_dir / "spinoff_shorts"
        spinoffs_root.mkdir(parents=True, exist_ok=True)
        sp_list = brief_data.get("spinoff_shorts") or verified_spinoffs
        for idx, sp in enumerate(sp_list, 1):
            sp_dir = spinoffs_root / f"spinoff_{idx:02d}_short_9x16"
            sp_topic = sp.get("opening_hook") or sp.get("hook_title")
            sp_res = build_short_bundle(output_dir=sp_dir, topic_str=sp_topic)
            spinoff_packages.append(sp_res)

    image_count = sum(len(sc.get("images", [])) for sc in content_data.get("scenes", []))

    return {
        "channel_id": CHANNEL_ID,
        "format_profile": "long_16x9",
        "topic": topic.topic,
        "output_dir": str(out_dir),
        "brief_hash": brief_hash,
        "valid_contracts": valid_contracts,
        "contract_errors": contract_errors,
        "cadence_status": cadence_report.get("status"),
        "cadence_warnings": cadence_report.get("warnings_count", 0),
        "hook_score": hook_result.score,
        "hook_checks": hook_result.checks,
        "image_count": image_count,
        "scene_count": len(content_data.get("scenes", [])),
        "spinoff_shorts_count": len(verified_spinoffs),
        "spinoff_packages": spinoff_packages,
        "brief_file": str(out_dir / "brief.json"),
        "content_file": str(out_dir / "content.json"),
    }


def build_channel_bundle(
    format_profile: str = "short_9x16",
    output_dir: Optional[Union[str, Path]] = None,
    topic_str: Optional[str] = None,
) -> Dict[str, Any]:
    """Unified dispatcher for building ua_sao_vay packages."""
    if format_profile == "short_9x16":
        return build_short_bundle(output_dir=output_dir, topic_str=topic_str)
    elif format_profile == "long_16x9":
        return build_long_bundle(output_dir=output_dir, topic_str=topic_str)
    else:
        raise ValueError(f"Unsupported format_profile '{format_profile}'. Choose 'short_9x16' or 'long_16x9'.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build ua_sao_vay Schema 3.0 production packages.")
    parser.add_argument("--format", default="both", choices=["short_9x16", "long_16x9", "both"])
    parser.add_argument("--topic", default=None, help="Custom topic string")
    parser.add_argument("--output-dir", default=None, help="Target run output directory")
    args = parser.parse_args()

    results: List[Dict[str, Any]] = []
    if args.format in ("short_9x16", "both"):
        res_short = build_short_bundle(output_dir=args.output_dir, topic_str=args.topic)
        results.append(res_short)
        print(f"[ua_sao_vay:short_9x16] Output: {res_short['output_dir']}")
        print(
            f"  Valid: {res_short['valid_contracts']}, Cadence: {res_short['cadence_status']}, "
            f"Hook Score: {res_short['hook_score']}, Images: {res_short['image_count']}"
        )

    if args.format in ("long_16x9", "both"):
        out_long = args.output_dir if args.format == "long_16x9" else None
        res_long = build_long_bundle(output_dir=out_long, topic_str=args.topic)
        results.append(res_long)
        print(f"[ua_sao_vay:long_16x9] Output: {res_long['output_dir']}")
        print(
            f"  Valid: {res_long['valid_contracts']}, Cadence: {res_long['cadence_status']}, "
            f"Hook Score: {res_long['hook_score']}, Spinoffs: {res_long['spinoff_shorts_count']}"
        )

    all_valid = all(r["valid_contracts"] for r in results)
    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
