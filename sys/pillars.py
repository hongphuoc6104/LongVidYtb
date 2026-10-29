"""Channel content philosophy and dynamic depth registry (SSOT for multi-philosophy production).

Replaces rigid hard constraints, forced narrative arcs, and paradox mandates with
constructive guidance, exemplars, and adaptive flow.
Each job selects a philosophy through ``brief.channel_philosophy`` or legacy ``brief.channel_pillar``.
Missing values resolve to the default COGNITION philosophy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, List, Mapping, Optional, Tuple

TIER_1 = "tier_1_broad"
TIER_2 = "tier_2_mid"
TIER_3 = "tier_3_conversion"

SCREEN_CAPTURE_SHOT = "screen_capture"
SCREEN_CAPTURE_SOURCES: Tuple[str, str] = ("user_recorded", "cdp_auto")


@dataclass(frozen=True)
class DepthEstimate:
    recommended_scenes: Tuple[int, int]
    recommended_minutes: Tuple[float, float]
    target_syllables: int
    rationale: str

    @property
    def min_scenes(self) -> int:
        return self.recommended_scenes[0]

    @property
    def min_syllables(self) -> int:
        return self.target_syllables

    @property
    def target_minutes(self) -> Tuple[float, float]:
        return self.recommended_minutes


# Backward compatibility alias
DepthFloor = DepthEstimate


@dataclass(frozen=True)
class ContentPhilosophy:
    id: str
    name: str
    summary: str
    principles: Tuple[str, ...]
    exemplar_hooks: Tuple[str, ...]
    visual_guidance: str
    academic_props: bool = False
    screen_capture_tiers: FrozenSet[str] = frozenset()
    funnel: Mapping[str, str] = field(default_factory=dict)
    depth_overrides: Mapping[str, DepthEstimate] = field(default_factory=dict)


# Backward compatibility alias
Pillar = ContentPhilosophy
PillarConfig = ContentPhilosophy


COGNITION = ContentPhilosophy(
    id="cognition",
    name="Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    summary=(
        "Khám phá bản chất nhận thức, mô hình tư duy và phương pháp luận giải quyết vấn đề "
        "qua lăng kính trực quan, đơn giản hóa các ý niệm phức tạp theo tinh thần Feynman."
    ),
    principles=(
        "Một ý niệm cốt lõi cho mỗi câu nói; giải thích khái niệm phức tạp bằng từ ngữ giản dị.",
        "Mở đầu bằng quan sát đời thực hoặc hiện tượng quen thuộc gợi tò mò tự nhiên.",
        "Xây dựng chuỗi suy luận nhân quả rõ ràng từ quan sát đời sống đến nguyên lý gốc.",
        "Kết nối tri thức với hành động thực tiễn mang lại giá trị nhận thức rõ ràng cho người xem.",
    ),
    exemplar_hooks=(
        "Tại sao người càng thông minh lại càng dễ rơi vào bẫy tự tin thái quá?",
        "Có một sự thật kỳ lạ: càng cố kiểm soát thời gian, ta lại càng thấy thiếu thốn.",
        "Bạn đã bao giờ tự hỏi vì sao những kế hoạch hoàn hảo nhất vẫn thường đổ vỡ?",
    ),
    visual_guidance=(
        "2D indie doodle tối giản trên nền phẳng (#FFFFFF/#F8F0DC): 1 nhân vật gậy trắng + 1 ẩn dụ "
        "hình ảnh trọng tâm, khung hình domino phát triển tuần tự không rườm rà."
    ),
    academic_props=False,
    screen_capture_tiers=frozenset(),
    funnel={
        TIER_1: "Cognitive biases and everyday paradoxes",
        TIER_2: "First-principles reasoning and mental models",
        TIER_3: "Deep thinking tooling and systematic workflows",
    },
)

RESEARCH_GUIDE = ContentPhilosophy(
    id="research_guide",
    name="Hướng Dẫn Nghiên Cứu Khoa Học Cho Người Mới",
    summary=(
        "Đồng hành cùng người mới bước chân vào nghiên cứu học thuật: từ tư duy đặt câu hỏi, "
        "phương pháp thu thập dữ liệu đến thực hành công cụ chuyên sâu."
    ),
    principles=(
        "Học thuật hóa không đồng nghĩa với ngôn từ phức tạp; diễn giải chân phương, dễ hiểu.",
        "Tập trung vào giải pháp cho những khó khăn thực tế của học viên và nhà nghiên cứu trẻ.",
        "Minh họa quy trình từng bước, cung cấp ví dụ thực chiến và công cụ khả thi.",
        "Khuyến khích tư duy phản biện và liêm chính học thuật trong nghiên cứu.",
    ),
    exemplar_hooks=(
        "Viết tổng quan tài liệu không khó như bạn nghĩ nếu biết 3 bước lọc này.",
        "Sai lầm phổ biến nhất khi chọn đề tài nghiên cứu là chọn thứ quá rộng.",
        "Làm thế nào để quản lý hàng trăm bài báo khoa học mà không bị quá tải?",
    ),
    visual_guidance=(
        "Hình minh họa 2D rõ ràng kết hợp biểu đồ trực quan, tài liệu nghiên cứu tối giản; "
        "hỗ trợ ảnh chụp màn hình công cụ ở tầng thực hành chuyên sâu."
    ),
    academic_props=True,
    screen_capture_tiers=frozenset({TIER_3}),
    funnel={
        TIER_1: "Common beginner mistakes and misconceptions in research",
        TIER_2: "The essence of each step: question, literature review, design, data, writing, submission/peer review",
        TIER_3: "Deep tooling: Zotero, Google Scholar, SPSS/R, LaTeX, journal selection",
    },
    depth_overrides={
        TIER_3: DepthEstimate(
            recommended_scenes=(24, 30),
            recommended_minutes=(10.0, 15.0),
            target_syllables=2700,
            rationale="Tier 3 conversion tutorial requires deep tooling demonstration",
        )
    },
)

PHILOSOPHIES: Dict[str, ContentPhilosophy] = {p.id: p for p in (COGNITION, RESEARCH_GUIDE)}
DEFAULT_PHILOSOPHY_ID = COGNITION.id

# Backward compatibility alias
PILLARS: Dict[str, ContentPhilosophy] = PHILOSOPHIES
DEFAULT_PILLAR_ID = DEFAULT_PHILOSOPHY_ID


def get_philosophy(key: Optional[str]) -> ContentPhilosophy:
    """Resolve a philosophy by id or display name; empty -> default. Unknown raises ValueError."""
    raw = (key or "").strip()
    if not raw:
        return PHILOSOPHIES[DEFAULT_PHILOSOPHY_ID]
    if raw in PHILOSOPHIES:
        return PHILOSOPHIES[raw]
    for p in PHILOSOPHIES.values():
        if p.name.casefold() == raw.casefold():
            return p
    raise ValueError(f"Unknown channel_philosophy '{raw}'. Allowed ids: {sorted(PHILOSOPHIES)}")


# Backward-compatible alias
get_pillar = get_philosophy


def _brief_field(brief: Mapping[str, Any], name: str) -> Any:
    pkg = brief.get("packaging") or {}
    return brief.get(name) or (pkg.get(name) if isinstance(pkg, Mapping) else None)


def philosophy_for_brief(brief: Mapping[str, Any]) -> ContentPhilosophy:
    """Resolve ContentPhilosophy from brief metadata (supports channel_philosophy or legacy channel_pillar)."""
    key = _brief_field(brief, "channel_philosophy") or _brief_field(brief, "channel_pillar")
    return get_philosophy(key)


# Backward-compatible alias
pillar_for_brief = philosophy_for_brief


def depth_floor_for(brief: Mapping[str, Any]) -> Optional[DepthEstimate]:
    """Return a philosophy/tier-specific long-form depth floor, or None to use format profile defaults."""
    philosophy = philosophy_for_brief(brief)
    tier = _brief_field(brief, "funnel_tier") or ""
    return philosophy.depth_overrides.get(tier)


def content_depth_estimate(brief_or_topic: Mapping[str, Any] | str) -> DepthEstimate:
    """Dynamically estimate scene count and duration based on topic depth and cognitive goals.

    Replaces rigid hard floors with content-aware estimation calibrated to narrative depth,
    cognitive points, and presentation format.
    """
    if isinstance(brief_or_topic, str):
        brief_data: Mapping[str, Any] = {"topic": brief_or_topic}
    elif isinstance(brief_or_topic, Mapping):
        brief_data = brief_or_topic
    else:
        brief_data = {}

    format_profile = (
        brief_data.get("format_profile")
        or brief_data.get("aspect_ratio")
        or "long_16x9"
    )

    # 1. Short-form (9:16 portrait)
    if format_profile in ("short_9x16", "9:16"):
        required_points = brief_data.get("required_points") or []
        num_pts = len(required_points)
        scenes_min = max(3, min(6, num_pts + 1 if num_pts else 4))
        scenes_max = max(scenes_min + 1, min(8, scenes_min + 2))
        return DepthEstimate(
            recommended_scenes=(scenes_min, scenes_max),
            recommended_minutes=(0.75, 1.5),
            target_syllables=240,
            rationale="Short-form dynamic pacing tailored for rapid engagement (45-90s).",
        )

    # 2. Long-form (16:9 landscape)
    philosophy = philosophy_for_brief(brief_data)
    tier = _brief_field(brief_data, "funnel_tier") or ""

    # Check tier overrides if configured for this philosophy
    override = philosophy.depth_overrides.get(tier)
    if override is not None:
        return override

    required_points = brief_data.get("required_points") or []
    num_points = len(required_points)
    topic = str(brief_data.get("topic") or "explainer")

    if num_points == 0:
        if tier == TIER_1:
            rec_scenes = (12, 16)
            rec_mins = (5.0, 7.5)
            target_sylls = 1400
            rationale = f"Tier 1 broad awareness depth for '{topic}': accessible conceptual framing."
        elif tier == TIER_2:
            rec_scenes = (16, 20)
            rec_mins = (7.0, 9.5)
            target_sylls = 1800
            rationale = f"Tier 2 first-principles depth for '{topic}': detailed mechanism exploration."
        else:
            rec_scenes = (14, 18)
            rec_mins = (6.0, 8.5)
            target_sylls = 1600
            rationale = f"Standard explainer depth for '{topic}': dynamic narrative progression."
    elif num_points <= 2:
        rec_scenes = (10, 14)
        rec_mins = (4.5, 6.5)
        target_sylls = 1200
        rationale = f"Focused concept depth: {num_points} key points across {rec_scenes[0]}-{rec_scenes[1]} scenes."
    elif num_points <= 4:
        rec_scenes = (14, 18)
        rec_mins = (6.0, 8.5)
        target_sylls = 1600
        rationale = f"Multi-faceted explainer: {num_points} key points across {rec_scenes[0]}-{rec_scenes[1]} scenes."
    elif num_points <= 6:
        rec_scenes = (18, 24)
        rec_mins = (8.0, 11.0)
        target_sylls = 2200
        rationale = f"Comprehensive deep-dive: {num_points} key points across {rec_scenes[0]}-{rec_scenes[1]} scenes."
    else:
        rec_scenes = (22, 30)
        rec_mins = (10.0, 14.0)
        target_sylls = 2600
        rationale = f"Extensive treatise: {num_points} key points across {rec_scenes[0]}-{rec_scenes[1]} scenes."

    return DepthEstimate(
        recommended_scenes=rec_scenes,
        recommended_minutes=rec_mins,
        target_syllables=target_sylls,
        rationale=rationale,
    )


def check_screen_capture(brief: Mapping[str, Any], scenes: List[Mapping[str, Any]]) -> List[str]:
    """Validate screen_capture shots against philosophy/tier policy and the recorded source decision.

    The source (user_recorded vs cdp_auto) is asked from the user only when a video
    actually contains screen_capture shots; until then the job must stop here.
    """
    errors: List[str] = []
    capture_ids = [
        str(sc.get("id", "SC??"))
        for sc in scenes
        for v in (sc.get("images") or [])
        if isinstance(v, Mapping) and v.get("shot_type") == SCREEN_CAPTURE_SHOT
    ]
    if not capture_ids:
        return errors
    philosophy = philosophy_for_brief(brief)
    tier = _brief_field(brief, "funnel_tier")
    if tier not in philosophy.screen_capture_tiers:
        errors.append(
            f"SCREEN_CAPTURE_NOT_ALLOWED: pillar '{philosophy.id}' tier '{tier}' forbids screen_capture shots ({', '.join(capture_ids)})"
        )
    source = brief.get("screen_capture_source")
    if source not in SCREEN_CAPTURE_SOURCES:
        errors.append(
            "SCREEN_CAPTURE_SOURCE_REQUIRED: ask the user whether the recordings are "
            f"user_recorded or cdp_auto before continuing (scenes: {', '.join(capture_ids)})"
        )
    return errors
