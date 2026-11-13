"""Multi-channel registry (SSOT for the 8-niche TikTok + YouTube experiment).

Each ``ChannelProfile`` bundles niche, persona, script tone, hook formulas, short/long
format specs, a Flow visual identity and researched reference channels. Production
reuses the existing pipeline unchanged (architect -> scriptwriting -> Flow CDP ->
Colab TTS -> Remotion render); a channel only swaps *content* inputs: ``brief.style``,
``brief.tone``, cast appearance and the ``brief.channel_profile`` provenance stamp.

Long-form YouTube videos feed short TikTok videos through the existing
``spinoff_shorts`` / ``omni_platform`` path (``sys/omni_platform.py``).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple

REGISTRY_VERSION = 1
CHANNEL_STYLE_PREFIX = "ch_"


@dataclass(frozen=True)
class FormatSpec:
    """Duration and retention structure for one output format."""

    format_profile: str
    duration_seconds: Tuple[int, int]
    beat_interval_seconds: Tuple[float, float]
    structure: Tuple[str, ...]
    closing: str


@dataclass(frozen=True)
class VisualIdentity:
    """Flow prompt identity. ``style_description`` is written verbatim into ``brief.style``."""

    profile_id: str
    label: str
    style_description: str
    cast_appearance: str
    outfit: str
    palette: Tuple[str, ...]
    thumbnail_rule: str


@dataclass(frozen=True)
class ReferenceChannel:
    name: str
    platform: str
    format: str  # "short" | "long"
    learn: str


@dataclass(frozen=True)
class SpeedOptimizationSpec:
    """Per-channel speed optimization & hybrid Remotion/Flow production profile."""

    render_mode: str  # "flow_full_frame" | "hybrid_motion" | "screen_capture_hybrid"
    fast_short_max_images: int
    spinoff_shorts_per_long: int
    remotion_motion_ratio: float
    estimated_short_minutes: Tuple[int, int]
    estimated_bundle_minutes: Tuple[int, int]
    notes: str


DEFAULT_BANNED_CTA_PHRASES: Tuple[str, ...] = (
    "đừng quên like",
    "nhấn chuông",
    "bấm chuông",
    "like share",
    "like và share",
    "like, share",
    "subscribe",
    "đăng ký kênh",
    "ấn theo dõi ngay",
    "bấm theo dõi ngay",
    "hãy like",
    "nhớ like",
    "để ủng hộ kênh",
)

ENGLISH_BANNED_CTA_PHRASES: Tuple[str, ...] = (
    "don't forget to like",
    "hit the bell",
    "smash that like",
    "like and subscribe",
    "subscribe to the channel",
    "leave a like",
    "please subscribe",
)

ALL_BANNED_CTA_PHRASES: Tuple[str, ...] = DEFAULT_BANNED_CTA_PHRASES + ENGLISH_BANNED_CTA_PHRASES

CHANNEL_ALIASES: Dict[str, str] = {
    "en_scale_and_bone": "en_plain_sight_ai",
    "en-scale-and-bone": "en_plain_sight_ai",
    "en_root_and_canopy": "en_kitchen_molecules",
    "en-root-and-canopy": "en_kitchen_molecules",
    "en_spawn_to_apex": "en_wait_how",
    "en-spawn-to-apex": "en_wait_how",
    "en_deep_time_strata": "en_parable_lamp",
    "en-deep-time-strata": "en_parable_lamp",
}

CHANNEL_DESCRIPTIONS: Dict[str, str] = {
    # Wave 1 VN (8 channels)
    "nao_luoi": (
        "Giải mã tâm lý học hành vi và những phản ứng vô thức của não bộ trong đời sống "
        "thường ngày bằng ngôn ngữ gần gũi, hài hước. Khám phá lý do vì sao bạn trì hoãn, "
        "overthinking hay lo âu qua hình vẽ 2D doodle trực quan."
    ),
    "tui_tien": (
        "Bóc tách dòng tiền, kinh tế học hành vi và những bẫy chi tiêu âm thầm rút cạn "
        "ví tiền mỗi ngày. Hướng dẫn quản lý tài chính cá nhân thông minh, minh bạch và "
        "thực tế cho người trẻ qua nét vẽ 2D doodle sinh động."
    ),
    "ua_sao_vay": (
        "Khám phá những sự thật bất ngờ, nghịch lý khoa học thú vị và bí ẩn đời thường "
        "trong tự nhiên qua các video giải thích ngắn gọn, súc tích. Trả lời thỏa đáng "
        "những câu hỏi 'ủa sao vậy' bằng hình vẽ minh họa cuốn hút."
    ),
    "su_ke_lai": (
        "Tái hiện lịch sử Việt Nam và thế giới qua lăng kính điện ảnh kịch tính, chân thực "
        "và giàu cảm xúc. Mỗi tập phim là một câu chuyện lịch sử sống động, chính xác, "
        "giúp người xem thấu hiểu sâu sắc cội nguồn và thời đại."
    ),
    "thuong_cho_kheo": (
        "Thấu hiểu tâm lý tình cảm, phong cách gắn bó và nghệ thuật giao tiếp khéo léo "
        "trong các mối quan hệ hiện đại. Cùng bóc tách xung đột, chữa lành tổn thương và "
        "học cách yêu thương tỉnh thức qua minh họa 2D tinh tế."
    ),
    "ho_so_ky_la": (
        "Lật mở những hồ sơ bí ẩn, sự kiện kỳ lạ và vụ án lịch sử có thật trên thế giới "
        "dựa trên tư liệu điều tra xác thực. Lời kể điềm tĩnh, khách quan kết hợp phong "
        "cách minh họa noir cuốn hút đến từng giây phút."
    ),
    "co_the_ke": (
        "Lắng nghe các cơ quan nội tạng trong cơ thể bạn tự cất tiếng kể chuyện khoa học "
        "y sinh đầy hóm hỉnh. Hiểu rõ cơ chế sinh học, nhịp sinh học và bí quyết chăm sóc "
        "sức khỏe chủ động qua góc nhìn nhân hóa độc đáo."
    ),
    "ai_binh_dan": (
        "Hướng dẫn ứng dụng trí tuệ nhân tạo và công cụ tự động hóa công việc cho người "
        "bình thường, không cần biết lập trình. Tiết kiệm hàng giờ mỗi ngày bằng các mẹo "
        "prompt, quy trình làm việc AI thực chiến và miễn phí."
    ),
    # Wave 2 VN (6 channels)
    "luat_ngam": (
        "Bóc tách những quy luật tâm lý xã hội ngầm, hiệu ứng bầy đàn và chiến thuật thao "
        "túng đám đông trong cuộc sống thường nhật. Giúp bạn nâng cao tư duy phản biện, "
        "làm chủ nghệ thuật đàm phán và bảo vệ bản thân."
    ),
    "ban_do_quyen_luc": (
        "Nhìn vào bản đồ địa lý để giải mã các thế cờ địa chính trị, chiến lược tài nguyên "
        "và các tuyến hàng hải huyết mạch toàn cầu. Phân tích nguyên nhân sâu xa của các "
        "xung đột và trật tự quyền lực thế giới đương đại."
    ),
    "dia_com": (
        "Khám phá những phản ứng hóa học thú vị và bí mật khoa học đằng sau bữa cơm gia đình "
        "Việt mỗi ngày. Giúp bạn hiểu đúng về dinh dưỡng, an toàn thực phẩm và mẹo nấu nướng "
        "khoa học để bảo vệ sức khỏe người thân."
    ),
    "luat_doi_thuong": (
        "Cẩm nang pháp lý dân sự bình dân giải thích dễ hiểu về hợp đồng lao động, thuê nhà, "
        "đặt cọc và quyền lợi tiêu dùng. Trang bị kiến thức luật thực tế giúp bạn tự tin "
        "bảo vệ quyền và lợi ích hợp pháp của mình."
    ),
    "banh_rang": (
        "Giải thích dễ hiểu các mắt xích kinh tế vĩ mô, chuỗi cung ứng, lãi suất và lạm "
        "phát tác động trực tiếp đến thu nhập của bạn. Thấy rõ sự vận hành của cỗ máy kinh "
        "tế toàn cầu qua nét vẽ minh họa trực quan."
    ),
    "vu_tru_ti_hon": (
        "Giải mã những bí ẩn bao la của vũ trụ học, vật lý lượng tử và thuyết tương đối bằng "
        "phong cách trực quan tối giản kiểu Feynman. Đưa những câu hỏi lớn về không-thời gian "
        "trở nên gần gũi, truyền cảm hứng cho mọi người."
    ),
    # Wave 3 VN (6 channels)
    "nghe_song_sot": (
        "Khám phá chiến lược phát triển sự nghiệp, kỹ năng đòn bẩy và những quy luật ngầm "
        "chốn công sở hiện đại. Giúp nhân sự trẻ và cấp quản lý định vị bản thân vững vàng "
        "trước làn sóng tự động hóa và biến động thị trường."
    ),
    "la_ban_hoc_thuat": (
        "Chia sẻ phương pháp tự học sâu, tư duy phản biện và kỹ năng đọc hiểu tài liệu nghiên "
        "cứu khoa học chuẩn xác. Biến những công trình học thuật hàn lâm phức tạp thành kiến "
        "thức ứng dụng thực tiễn cho cộng đồng học hỏi."
    ),
    "chanh_niem_ke": (
        "Lắng đọng tâm hồn cùng những câu chuyện Thiền, triết lý Phật giáo ứng dụng và thực "
        "hành chánh niệm giữa đời sống bận rộn. Giúp bạn buông bỏ âu lo, chuyển hóa phiền "
        "muộn và tìm lại sự bình an nội tâm đích thực."
    ),
    "loi_sang_soi": (
        "Giải mã các dụ ngôn Kinh Thánh và câu chuyện đức tin vượt thời gian qua nét vẽ 2D "
        "ấm áp, mộc mạc. Khám phá bài học yêu thương, lòng tha thứ, hy vọng và chiều sâu triết "
        "lý Kitô giáo ứng dụng vào đời sống hiện đại mỗi ngày."
    ),
    "minh_triet_song": (
        "Kết tinh triết lý phương Đông của Lão Tử, Trang Tử cùng chủ nghĩa Khắc kỷ phương Tây "
        "giúp rèn luyện bản lĩnh sống điềm tĩnh. Khám phá nghệ thuật vô vi, làm chủ cảm xúc "
        "và vững vàng tâm trí trước mọi biến cố cuộc đời."
    ),
    "tam_tinh_dem": (
        "Không gian lắng đọng buổi tối với những truyện ngụ ngôn ý nghĩa, chiêm nghiệm nhân "
        "sinh và bài học chữa lành tâm hồn. Giúp bạn khép lại những muộn phiền ngày dài, cảm "
        "nhận sự an yên và có một giấc ngủ thật thanh thản."
    ),
    # Wave 4 EN (18 channels)
    "en_lazy_brain": (
        "Decode why your brain procrastinates, craves quick dopamine, and sabotages deep work "
        "through neuroscience and behavioral psychology. Clear 2D doodle animations breaking "
        "down mental friction into actionable habits."
    ),
    "en_crowd_strings": (
        "Expose the invisible psychological strings behind mass conformity, herd behavior, and "
        "subtle societal manipulation. Research-backed explainer videos revealing how collective "
        "illusions shape our everyday decisions."
    ),
    "en_kindred_sketch": (
        "Deconstruct attachment theory, relationship dynamics, and emotional conflict with warmth "
        "and clarity. Hand-drawn 2D explainers helping you understand interpersonal boundaries, "
        "avoid burnout, and build authentic bonds."
    ),
    "en_first_principles": (
        "Strip complex problems down to their fundamental truths through mental models, game "
        "theory, and logical paradoxes. Visual essays designed to sharpen strategic thinking "
        "and decision-making from first principles."
    ),
    "en_wallet_anatomy": (
        "Dissect the behavioral economics, subtle subscription traps, and hidden financial "
        "incentives draining your wallet. Practical, visual explainers transforming personal "
        "finance literacy into high-leverage money habits."
    ),
    "en_macro_gears": (
        "Explore how central bank interest rates, global supply chains, and currency flows drive "
        "everyday economic realities. Engaging visual breakdowns of macroeconomic forces, inflation "
        "dynamics, and market cycles."
    ),
    "en_plain_sight_ai": (
        "Follow the visceral life-cycle of reptiles from leathery egg to apex survivor across 300 "
        "million years of evolution. Chronological, research-backed 2D natural history explainers "
        "uncovering ancient anatomical biomechanics."
    ),
    "en_career_leverage": (
        "Master the unspoken rules of modern workplaces, salary negotiations, and high-leverage "
        "professional skills. Strategic visual career guides helping ambitious knowledge workers "
        "thrive in an AI-accelerated economy."
    ),
    "en_fine_print": (
        "Uncover hidden clauses, fine print traps, and consumer rights buried inside everyday "
        "terms of service and employment contracts. Practical legal literacy explainers empowering "
        "you to protect your creative and financial rights."
    ),
    "en_inside_vessel": (
        "Journey deep inside human physiology, cellular defense mechanisms, and circadian biology "
        "through vivid visual metaphors. Understand how organs collaborate in real time to sustain "
        "life and fight unseen microscopic threats."
    ),
    "en_kitchen_molecules": (
        "Witness the hidden time-lapse warfare of plants—from dormant seed to 2,000-year canopy "
        "giant. Explore chronological evolutionary battles, mycorrhizal networks, and botanical "
        "adaptations through cinematic 2D explainer storytelling."
    ),
    "en_wait_how": (
        "Trace nature's most extreme chronological life cycles from microscopic egg to terrifying "
        "apex metamorphosis. Visual biology chronicles highlighting deep-sea adaptations, predatory "
        "mechanics, and bizarre survival transformations."
    ),
    "en_cold_case_ink": (
        "Re-examine history's greatest forensic mysteries, vanished expeditions, and scientific "
        "cold cases through primary documents. Rigorous investigative 2D documentary storytelling "
        "grounded in evidence, geography, and archival facts."
    ),
    "en_choke_point": (
        "Analyze the strategic straits, vital canals, and geographic chokepoints that dictate "
        "global trade, resource security, and geopolitical conflict. Clear cartographic explainers "
        "mapping world power and naval logistics."
    ),
    "en_pocket_cosmos": (
        "Unravel the mind-bending mysteries of astrophysics, black hole thermodynamics, and quantum "
        "paradoxes with elegant clarity. Visual cosmic explainers putting the grandeur of spacetime "
        "into intuitive, awe-inspiring perspectives."
    ),
    "en_second_arrow": (
        "Learn to drop the second arrow of mental suffering through classical Buddhist psychology, "
        "Stoic wisdom, and mindful fables. Gentle, research-grounded visual essays cultivating "
        "emotional resilience and stillness in everyday life."
    ),
    "en_parable_lamp": (
        "Excavate Earth's geological strata to uncover how ancient life survived five catastrophic "
        "mass extinctions and conquered continents. Chronological paleo-evolutionary documentaries "
        "tracing deep-time fossil ecosystems."
    ),
    "en_bamboo_marble": (
        "Bridge Western Stoic fortitude with Eastern Taoist harmony to cultivate unshakeable inner "
        "calm amidst modern chaos. Visual philosophical reflections merging Marcus Aurelius and Lao "
        "Tzu for clear-minded living and restful nights."
    ),
    # Pivoted EN aliases mapped to their authentic descriptions
    "en_scale_and_bone": (
        "Follow the visceral life-cycle of reptiles from leathery egg to apex survivor across 300 "
        "million years of evolution. Chronological, research-backed 2D natural history explainers "
        "uncovering ancient anatomical biomechanics."
    ),
    "en_root_and_canopy": (
        "Witness the hidden time-lapse warfare of plants—from dormant seed to 2,000-year canopy "
        "giant. Explore chronological evolutionary battles, mycorrhizal networks, and botanical "
        "adaptations through cinematic 2D explainer storytelling."
    ),
    "en_spawn_to_apex": (
        "Trace nature's most extreme chronological life cycles from microscopic egg to terrifying "
        "apex metamorphosis. Visual biology chronicles highlighting deep-sea adaptations, predatory "
        "mechanics, and bizarre survival transformations."
    ),
    "en_deep_time_strata": (
        "Excavate Earth's geological strata to uncover how ancient life survived five catastrophic "
        "mass extinctions and conquered continents. Chronological paleo-evolutionary documentaries "
        "tracing deep-time fossil ecosystems."
    ),
}


@dataclass(frozen=True)
class EngagementSpec:
    """Channel persona engagement, bridge to long-form, and closing CTA contracts."""

    cta_voice: str
    bridge_templates: Tuple[str, ...]
    close_templates: Tuple[str, ...]
    endcard_text: str
    banned_cta_phrases: Tuple[str, ...] = DEFAULT_BANNED_CTA_PHRASES


@dataclass(frozen=True)
class ChannelProfile:
    id: str
    name: str
    niche: str
    promise: str
    audience: str
    persona: str
    tone: str
    tone_rules: Tuple[str, ...]
    hook_formulas: Tuple[str, ...]
    avoid: Tuple[str, ...]
    short_spec: FormatSpec
    long_spec: FormatSpec
    visual: VisualIdentity
    references: Tuple[ReferenceChannel, ...]
    seed_topics: Tuple[str, ...]
    hashtags: Tuple[str, ...]
    monetization: Tuple[str, ...]
    philosophy_id: str = "cognition"
    voice: str = "VietNarrator"
    speed: float = 1.0
    wave: int = 1
    language: str = "vi"
    speed_optimization: Optional[SpeedOptimizationSpec] = None
    engagement: Optional[EngagementSpec] = None
    extra: Mapping[str, Any] = field(default_factory=dict)
    description: str = ""

    def __post_init__(self) -> None:
        if not self.description:
            desc = CHANNEL_DESCRIPTIONS.get(self.id) or CHANNEL_DESCRIPTIONS.get(CHANNEL_ALIASES.get(self.id, ""), "")
            if desc:
                object.__setattr__(self, "description", desc)

    @property
    def slug(self) -> str:
        return self.id.replace("_", "-")

    @property
    def git_branch(self) -> str:
        return f"channel/{self.slug}"

    @property
    def workspace_dirname(self) -> str:
        return f"channel-{self.slug}"

    @property
    def platform_routing(self) -> Dict[str, str]:
        return {"tiktok": "short_9x16", "youtube": "long_16x9"}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def sha256(self) -> str:
        payload = json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, default=list)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def spec_for(self, format_profile: str) -> FormatSpec:
        if format_profile == self.short_spec.format_profile:
            return self.short_spec
        if format_profile == self.long_spec.format_profile:
            return self.long_spec
        raise ValueError(f"Channel '{self.id}' has no spec for format '{format_profile}'")


def _short(duration: Tuple[int, int], closing: str, structure: Tuple[str, ...] | None = None) -> FormatSpec:
    return FormatSpec(
        format_profile="short_9x16",
        duration_seconds=duration,
        beat_interval_seconds=(2.0, 5.0),
        structure=structure
        or (
            "Hook <= 3s: shocking claim or relatable pain + striking first frame",
            "Open loop: promise the answer, delay it",
            "Escalation beats every 2-5s (new visual, number or twist)",
            "Payoff: answer the loop in one clear image",
            "Closing line",
        ),
        closing=closing,
    )


def _long(duration: Tuple[int, int], closing: str, structure: Tuple[str, ...] | None = None) -> FormatSpec:
    return FormatSpec(
        format_profile="long_16x9",
        duration_seconds=duration,
        beat_interval_seconds=(20.0, 30.0),
        structure=structure
        or (
            "Cold open 0-30s: strongest scene of the video, no channel intro",
            "Stakes: why this matters to the viewer's own life",
            "3-5 chapters, each opens with a mini-hook and ends with a re-hook",
            "Pattern interrupt every 20-30s (story, number, visual gag)",
            "Synthesis + practical takeaway",
            "Closing line pointing to the next video",
        ),
        closing=closing,
    )


def _doodle_style() -> Tuple[str, str, str]:
    """Reuse the existing hand-drawn doodle SSOT for the flagship channel."""
    from visual_style import CAST_APPEARANCE, DEFAULT_OUTFIT, STYLE_DESCRIPTION

    return STYLE_DESCRIPTION, CAST_APPEARANCE, DEFAULT_OUTFIT


def _build_channels() -> Tuple[ChannelProfile, ...]:
    doodle_style, doodle_cast, doodle_outfit = _doodle_style()
    return (
        ChannelProfile(
            id="nao_luoi",
            name="Não Lười",
            niche="Tâm lý và hành vi đời thường",
            promise="Giải thích vì sao bạn hành xử như vậy, bằng ngôn ngữ của bạn bè.",
            audience="Gen Z và người đi làm 18-30 tuổi, hay tự hỏi về bản thân",
            persona="Người bạn thân hiểu tâm lý, hơi cà khịa nhưng thương người xem",
            tone="Thân mật, cà khịa nhẹ, gọi người xem là 'bạn', có cảm xúc",
            tone_rules=(
                "Open with a behavior the viewer recognizes in themselves within 3 seconds.",
                "Name the psychology effect only after the viewer feels it.",
                "Allow light teasing and slang; never shame the viewer.",
                "Every list item gets one concrete everyday Vietnamese example.",
            ),
            hook_formulas=(
                "Nếu bạn hay [hành vi], não bạn đang [sự thật bất ngờ].",
                "[Số] dấu hiệu bạn đang [trạng thái] mà không biết.",
                "Bạn không lười. Não bạn đang [lý do].",
                "Vì sao càng [hành động] bạn lại càng [kết quả ngược]?",
            ),
            avoid=("Diagnosing mental illness", "Toxic-positivity advice", "Long academic definitions"),
            short_spec=_short((30, 45), "Hỏi người xem: bạn có bị như vậy không? Bình luận số 1 hoặc 2."),
            long_spec=_long((480, 720), "Gợi video tiếp theo cùng series tâm lý."),
            visual=VisualIdentity(
                profile_id="handdrawn_2d_explainer",
                label="Doodle stickman Nguệch Ngoạc (giữ phong cách hiện tại, biểu cảm mạnh hơn)",
                style_description=doodle_style,
                cast_appearance=doodle_cast,
                outfit=doodle_outfit,
                palette=("#F8F0DC", "#FFFFFF", "#3B82C4", "#F2B88B", "#93A88C", "#000000"),
                thumbnail_rule="Stickman with exaggerated emotion + 2-4 uppercase hand-lettered words on flat canvas.",
            ),
            references=(
                ReferenceChannel("Psych2Go Vietnam", "TikTok/YouTube Shorts", "short",
                                 "Relatable 'signs you are...' questions; viewer sees themselves."),
                ReferenceChannel("Psych2Go", "YouTube", "long",
                                 "7-15 min listicles with a fixed cartoon cast; empathy over lecture."),
            ),
            seed_topics=(
                "Vì sao bạn lướt điện thoại tới 2 giờ sáng dù rất buồn ngủ",
                "Vì sao càng gần deadline bạn càng muốn dọn phòng",
                "5 dấu hiệu bạn đang kiệt sức mà tưởng mình lười",
                "Vì sao bạn nhớ mãi một câu chê nhưng quên 10 lời khen",
                "Hiệu ứng chim mồi: vì sao bạn luôn chọn ly size vừa",
            ),
            hashtags=("#tamly", "#tamlyhoc", "#hieubanthan", "#genz", "#learnontiktok"),
            monetization=("YouTube AdSense (long)", "Affiliate sách tâm lý", "Booking app sức khỏe tinh thần"),
            wave=1,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=7,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.35,
                estimated_short_minutes=(8, 12),
                estimated_bundle_minutes=(35, 45),
                notes="Reuse 1.7.0 stickman templates; Remotion kinetic psychology badges + camera beats cut image count by 50%.",
            ),
            engagement=EngagementSpec(
                cta_voice="Bạn thân hơi cà khịa",
                bridge_templates=(
                    "Vì sao não lại đòi lại thời gian kiểu này? Bản dài mình mổ xẻ trên YouTube Não Lười.",
                ),
                close_templates=(
                    "Gửi cho đứa bạn hay thức khuya chung với bạn đi.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
        ),
        ChannelProfile(
            id="tui_tien",
            name="Túi Tiền Biết Nói",
            niche="Tiền và kinh tế đời sống",
            promise="Bóc tách tiền bạc đằng sau những thứ bạn mua mỗi ngày.",
            audience="Sinh viên, người mới đi làm thu nhập 7-20 triệu",
            persona="Người bạn mê con số, hay tính nhẩm giùm bạn",
            tone="Tò mò, rõ ràng, có số liệu cụ thể bằng tiền Việt",
            tone_rules=(
                "Always anchor numbers in VND and everyday items (ly trà sữa, tô phở, tiền trọ).",
                "Show the calculation step by step, one number per sentence.",
                "End with one money action the viewer can take today.",
                "Cite the source of every statistic in the description.",
            ),
            hook_formulas=(
                "Ly [món] [giá] nghìn, chủ quán thật ra lời bao nhiêu?",
                "Vì sao [thương hiệu/mô hình] lỗ mà vẫn mở thêm chi nhánh?",
                "Nếu mỗi ngày bạn bớt [khoản nhỏ], 5 năm sau bạn có [số tiền].",
                "Bạn đang trả tiền cho [thứ vô hình] mà không biết.",
            ),
            avoid=("Stock picks or investment advice", "Get-rich-quick claims", "Unsourced numbers"),
            short_spec=_short((45, 60), "Hỏi: bạn muốn mình bóc tách món nào tiếp theo?"),
            long_spec=_long((600, 900), "Gợi case study kinh doanh tiếp theo."),
            visual=VisualIdentity(
                profile_id="ch_ledger_doodle",
                label="Sổ tay kế toán vẽ tay: doodle trên giấy kẻ ô, tiền xu, biểu đồ vẽ tay",
                style_description=(
                    "Hand-drawn 2D notebook-ledger explainer illustration: wobbly black marker outlines (#1F1F1F) "
                    "on a flat warm grid-paper canvas (#FAF6E9 with faint #E3DCC8 square grid), flat unshaded fills "
                    "in money green (#2F9E5B), coin gold (#F2C14E), loss red (#D64545) and ink navy (#24364F); "
                    "hand-drawn bar charts, price tags and VND banknotes drawn as simple flat shapes; orthographic "
                    "2D, generous empty grid space, no gradients, no photorealism, no 3D."
                ),
                cast_appearance=(
                    "Simple 2D doodle stickman with a white round head, black dot eyes, thin wire arms and round hands, "
                    "small round glasses, always holding a pencil or a coin"
                ),
                outfit="Flat coin-gold (#F2C14E) T-shirt and navy (#24364F) trousers, no folds, no shading",
                palette=("#FAF6E9", "#2F9E5B", "#F2C14E", "#D64545", "#24364F"),
                thumbnail_rule="One big VND number or price tag + shocked stickman, hand-lettered on grid paper.",
            ),
            references=(
                ReferenceChannel("Sitcom Tài Chính", "TikTok", "short",
                                 "Turns economic concepts into short comedic skits."),
                ReferenceChannel("Học Viện Bò và Gấu", "YouTube", "long",
                                 "Business-model breakdowns of familiar industries (trà sữa, cà phê, bán lẻ)."),
            ),
            seed_topics=(
                "Ly trà sữa 35 nghìn: chủ quán lời thật bao nhiêu",
                "Vì sao siêu thị để sữa ở cuối cửa hàng",
                "Mua trả góp 0%: ai trả lãi cho bạn",
                "Vì sao quán cà phê sống được dù khách ngồi cả ngày",
                "Bớt 30 nghìn mỗi ngày, 5 năm sau bạn có bao nhiêu",
            ),
            hashtags=("#taichinhcanhan", "#kienthuckinhte", "#kinhte", "#tienbac", "#learnontiktok"),
            monetization=("YouTube AdSense (CPM cao nhất trong 8 kênh)", "Affiliate app tài chính / sách", "Booking"),
            wave=1,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=6,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.50,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(30, 40),
                notes="50% scenes use Remotion/Hyperframes VND cost breakdown cards & animated bar charts; only 5-6 Flow images per short.",
            ),
            engagement=EngagementSpec(
                cta_voice="Mê con số",
                bridge_templates=(
                    "Bảng tính đủ từng khoản mình để ở video dài trên YouTube.",
                ),
                close_templates=(
                    "Lưu lại, lần sau tính nhẩm trước khi quẹt thẻ.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
        ),
        ChannelProfile(
            id="ua_sao_vay",
            name="Ủa Sao Vậy?",
            niche="Sự thật bất ngờ, khoa học gây tò mò",
            promise="Mỗi video trả lời một câu 'ủa sao vậy' trong chưa tới một phút.",
            audience="Học sinh, sinh viên, người lướt TikTok giải trí 13-30 tuổi",
            persona="Linh vật 'Bé Ủa' tò mò, nói nhanh, hay há hốc mồm",
            tone="Nhanh, dồn dập, hài kiểu Gen Z, có twist cuối",
            tone_rules=(
                "First sentence is the question itself, phrased like a friend asking 'ủa'.",
                "Give a wrong-but-common answer first, then flip it.",
                "Max 2 seconds per visual beat in the first 10 seconds.",
                "End on a second surprising fact to trigger rewatch/share.",
            ),
            hook_formulas=(
                "Ủa, sao [hiện tượng quen thuộc] vậy?",
                "Ai cũng nghĩ [niềm tin phổ biến]. Sai bét.",
                "Điều gì xảy ra nếu [tình huống giả định]?",
                "[Vật quen thuộc] có một bí mật mà 99% người không để ý.",
            ),
            avoid=("Unverified viral myths", "Clickbait without payoff", "Pseudoscience"),
            short_spec=_short((20, 35), "Tung thêm 1 sự thật bất ngờ, hỏi: bạn có biết không?"),
            long_spec=_long((480, 720), "Gợi video 'tổng hợp 10 câu ủa sao vậy' tiếp theo.",
                            ("Cold open: the weirdest question of the episode",
                             "Compilation of 6-10 linked 'ủa sao vậy' questions",
                             "Each segment: question -> common wrong answer -> real answer -> visual proof",
                             "Running mascot gag between segments",
                             "Final mind-blowing fact + next episode tease")),
            visual=VisualIdentity(
                profile_id="ch_sticker_pop",
                label="Sticker pop: hoạt hình màu nổi viền trắng dày, linh vật Bé Ủa",
                style_description=(
                    "Bold 2D sticker-pop cartoon illustration: thick smooth black outlines with a chunky white sticker "
                    "border around every main object, saturated flat fills in lemon yellow (#FFD23F), coral (#FF6B6B), "
                    "teal (#2EC4B6) and grape (#7B2CBF) on a single flat solid pastel background (#FFF6D6 or #DFF7F4); "
                    "simple exaggerated proportions, big expressive eyes, comic motion lines and sparkle marks, "
                    "orthographic 2D, no gradients, no realistic textures, no 3D."
                ),
                cast_appearance=(
                    "Mascot 'Bé Ủa': a round lemon-yellow (#FFD23F) blob creature with huge white oval eyes, tiny black "
                    "pupils, a wide open mouth, two short stubby arms and a single curly antenna shaped like a question mark"
                ),
                outfit="No clothing; tiny coral (#FF6B6B) cheeks, chunky white sticker border",
                palette=("#FFF6D6", "#FFD23F", "#FF6B6B", "#2EC4B6", "#7B2CBF"),
                thumbnail_rule="Bé Ủa with open mouth next to the weird object + 2-3 word question in bold sticker letters.",
            ),
            references=(
                ReferenceChannel("Kiến Không Ngủ", "TikTok", "short",
                                 "Recurring mascot characters with personalities; Gen Z humor."),
                ReferenceChannel("Kiến Thức Thú Vị", "YouTube", "long",
                                 "Hand-drawn visuals, calm logical narration, 'little-known secrets' angle."),
            ),
            seed_topics=(
                "Ủa, sao muỗi chỉ đốt một số người",
                "Ủa, sao dưa hấu ngâm nước lại nổi",
                "Ủa, sao mình không tự cù lét mình được",
                "Điều gì xảy ra nếu bạn không ngủ 3 ngày",
                "Ủa, sao chai nước suối có hạn sử dụng",
            ),
            hashtags=("#uasaovay", "#kienthucthuvi", "#khoahoc", "#didyouknow", "#learnontiktok"),
            monetization=("Tăng follow nhanh làm phễu", "YouTube AdSense (compilation dài)", "Booking đồ chơi giáo dục"),
            wave=1,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=6,
                remotion_motion_ratio=0.40,
                estimated_short_minutes=(6, 9),
                estimated_bundle_minutes=(30, 40),
                notes="1 YouTube Long = 6-8 modular question chapters -> slices directly into 6 TikTok Shorts with zero extra Flow images.",
            ),
            engagement=EngagementSpec(
                cta_voice="Bé Ủa tò mò",
                bridge_templates=(
                    "Còn hai bí mật nữa về muỗi, Bé Ủa kể hết trên YouTube.",
                ),
                close_templates=(
                    "Ủa, bạn còn thắc mắc gì? Thả vô bình luận, Bé Ủa giải tiếp.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
        ),
        ChannelProfile(
            id="su_ke_lai",
            name="Sử Kể Lại",
            niche="Lịch sử Việt Nam và thế giới kể như phim",
            promise="Lịch sử không khô: mỗi tập là một bộ phim ngắn có nhân vật và kịch tính.",
            audience="Người trẻ 16-35 yêu lịch sử nhưng sợ sách giáo khoa",
            persona="Người kể chuyện trầm, biết nghỉ đúng lúc, thỉnh thoảng chêm câu hài",
            tone="Kể chuyện điện ảnh, kịch tính, tôn trọng sự thật lịch sử",
            tone_rules=(
                "Start in the middle of the decisive moment, then rewind.",
                "Every episode centers on one person and one choice.",
                "Separate documented facts from legend explicitly ('tương truyền...').",
                "Use recurring light gags sparingly; never mock national heroes.",
            ),
            hook_formulas=(
                "Năm [năm], một [nhân vật] chỉ có [nguồn lực nhỏ] đối đầu [đối thủ lớn].",
                "Quyết định này của [nhân vật] đã thay đổi lịch sử Việt Nam.",
                "Sự thật đằng sau [sự kiện quen thuộc] không giống sách giáo khoa.",
                "Chỉ một sai lầm, cả [triều đại/đội quân] sụp đổ.",
            ),
            avoid=("Politically sensitive modern history", "Unverified legends presented as fact", "Graphic violence"),
            short_spec=_short((60, 90), "Cắt ở cao trào: 'Phần tiếp theo có trên YouTube'."),
            long_spec=_long((900, 1500), "Gợi tập tiếp theo của series.",
                            ("Cold open in the decisive moment",
                             "Rewind: who, where, what was at stake",
                             "Rising action in 3-4 acts with cliffhanger re-hooks",
                             "Climax and consequence",
                             "Legacy: what it means for Vietnam today",
                             "Next episode tease")),
            visual=VisualIdentity(
                profile_id="ch_dong_ho_folk",
                label="Tranh dân gian Đông Hồ / khắc gỗ trên giấy dó",
                style_description=(
                    "2D Vietnamese Dong Ho folk woodblock-print illustration: bold carved black woodcut outlines "
                    "(#1E1E1E), flat natural-pigment fills in vermilion (#B5332E), pagoda-tree yellow (#D9A520), "
                    "indigo (#2C4A6E) and leaf green (#5E7D3A) on a warm handmade do-paper canvas (#EFE4C8) with a "
                    "subtle paper fiber texture; stylized flat folk figures in period costume, symmetrical "
                    "decorative composition, orthographic 2D, no gradients, no photorealism, no 3D."
                ),
                cast_appearance=(
                    "Stylized Dong Ho folk-print human figures with round faces, simple almond eyes, rosy cheek dots and "
                    "period-accurate Vietnamese costume for the episode's era"
                ),
                outfit="Era-specific flat costume in vermilion, indigo or yellow pigment, woodcut line folds only",
                palette=("#EFE4C8", "#B5332E", "#D9A520", "#2C4A6E", "#5E7D3A", "#1E1E1E"),
                thumbnail_rule="One hero figure in action pose + 2-4 word title carved in woodcut letters on do paper.",
            ),
            references=(
                ReferenceChannel("Sử Lược - Tóm Tắt Lịch Sử", "TikTok/YouTube", "short",
                                 "Fast map-driven summaries with narrative pacing."),
                ReferenceChannel("OverSimplified", "YouTube", "long",
                                 "History as a multi-episode sitcom with recurring gags (format only)."),
                ReferenceChannel("Hồn Sử Việt", "YouTube", "long",
                                 "Illustrated storytelling of Vietnamese legends and heroes."),
            ),
            seed_topics=(
                "Trận Bạch Đằng 938: cái bẫy cọc gỗ của Ngô Quyền",
                "Vì sao Lý Công Uẩn dời đô về Thăng Long",
                "Nguyễn Huệ hành quân thần tốc 1789",
                "Trạng Quỳnh: thật hay chỉ là truyền thuyết",
                "Vì sao chữ Quốc ngữ thay thế chữ Nôm",
            ),
            hashtags=("#lichsu", "#lichsuvietnam", "#sukelai", "#kechuyen", "#learnontiktok"),
            monetization=("YouTube AdSense (watch time dài)", "Affiliate sách lịch sử", "Series membership"),
            wave=1,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="flow_full_frame",
                fast_short_max_images=8,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.25,
                estimated_short_minutes=(10, 14),
                estimated_bundle_minutes=(40, 50),
                notes="Invest full Dong Ho artwork into YouTube Long, then extract 4 cliffhanger TikTok Shorts via omni_platform (0 extra images).",
            ),
            engagement=EngagementSpec(
                cta_voice="Người kể trầm",
                bridge_templates=(
                    "Nước cờ cuối của Ngô Quyền, bản đầy đủ có trên YouTube Sử Kể Lại.",
                ),
                close_templates=(
                    "Nếu thấy đáng nhớ, ở lại nghe tiếp những trận sau.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
        ),
        ChannelProfile(
            id="thuong_cho_kheo",
            name="Thương Cho Khéo",
            niche="Tình cảm, giao tiếp và cách cư xử",
            promise="Những tình huống tình cảm ai cũng gặp, và cách nói cho khéo.",
            audience="Người 18-30 đang yêu, độc thân hoặc mới chia tay",
            persona="Người chị/anh tâm lý, tâm sự nhỏ nhẹ, không phán xét",
            tone="Tâm sự, chạm cảm xúc, ấm áp, đôi khi hài nhẹ",
            tone_rules=(
                "Open with a dialogue line from a real-feeling situation.",
                "Show the wrong reply and the better reply side by side as two moments.",
                "Validate feelings before giving advice.",
                "Never stereotype genders; advice works for everyone.",
            ),
            hook_formulas=(
                "Khi người ấy nói '[câu nói]', thật ra họ đang muốn [điều ẩn].",
                "Đừng bao giờ trả lời '[câu sai]' khi người yêu [tình huống].",
                "[Số] câu nói làm người ấy thương bạn hơn.",
                "Bạn không cô đơn đâu, chỉ là [lý do].",
            ),
            avoid=("Manipulation or 'thao túng' tactics", "Gender stereotypes", "Shaming exes"),
            short_spec=_short((30, 60), "Hỏi: bạn đã từng nói câu sai này chưa? Tag người ấy."),
            long_spec=_long((600, 900), "Gợi video tình huống tiếp theo."),
            visual=VisualIdentity(
                profile_id="ch_pastel_duo",
                label="Pastel đôi bạn: 2 nhân vật Tũn và Mây đối thoại, nét mềm",
                style_description=(
                    "Soft 2D pastel line-art illustration: smooth thin warm-brown outlines (#5B4636), flat unshaded fills "
                    "in blush pink (#F7C6C7), lavender (#CDB4DB), mint (#BDE0C6) and butter (#FFF1B5) on a flat solid "
                    "cream canvas (#FFF8F0); two characters facing each other with speech-bubble-free composition, "
                    "rounded gentle shapes, small heart and sparkle accents, orthographic 2D, no gradients, no 3D."
                ),
                cast_appearance=(
                    "Recurring duo: 'Tũn', a young man with a round face, messy short black hair and dot eyes; and "
                    "'Mây', a young woman with a round face, shoulder-length black hair with a small clip and dot eyes; "
                    "both drawn in simple chibi-like proportions"
                ),
                outfit="Tũn wears a flat mint (#BDE0C6) hoodie; Mây wears a flat blush (#F7C6C7) cardigan",
                palette=("#FFF8F0", "#F7C6C7", "#CDB4DB", "#BDE0C6", "#FFF1B5", "#5B4636"),
                thumbnail_rule="Tũn and Mây with contrasting emotions + one short quoted phrase hand-lettered.",
            ),
            references=(
                ReferenceChannel("Giác Minh Luật", "TikTok", "short",
                                 "Gen Z language and everyday analogies about love and anxiety."),
                ReferenceChannel("Hồng Trân (Naiverosie)", "TikTok", "short",
                                 "Reflective dating psychology and communication."),
                ReferenceChannel("Tuệ An / Cửa Sổ Tình Yêu", "YouTube", "long",
                                 "Situation -> analysis -> advice structure."),
            ),
            seed_topics=(
                "Khi người yêu nói 'em không sao', bạn nên làm gì",
                "3 câu nói làm cuộc cãi vã tệ hơn",
                "Vì sao bạn hay thích người không thích mình",
                "Cách từ chối mà không làm mất lòng",
                "Dấu hiệu bạn đang yêu vì sợ cô đơn",
            ),
            hashtags=("#tinhyeu", "#tamsu", "#giaotiep", "#couple", "#learnontiktok"),
            monetization=("YouTube AdSense", "Affiliate sách / quà tặng", "Booking app hẹn hò"),
            wave=1,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=6,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.40,
                estimated_short_minutes=(7, 11),
                estimated_bundle_minutes=(32, 42),
                notes="Use based_on in-place facial expression variations for Tũn & Mây dialogue pairs + Remotion wrong/right reply cards.",
            ),
            engagement=EngagementSpec(
                cta_voice="Chị tâm lý nhỏ nhẹ",
                bridge_templates=(
                    "Nói lại sao cho khéo, chị kể kỹ hơn trong video dài trên YouTube.",
                ),
                close_templates=(
                    "Nếu câu này chạm vào bạn, gửi cho người ấy, không cần nói thêm.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
        ),
        ChannelProfile(
            id="ho_so_ky_la",
            name="Hồ Sơ Kỳ Lạ",
            niche="Bí ẩn và chuyện kỳ lạ có thật",
            promise="Những hồ sơ kỳ lạ có thật, kể bình tĩnh và có bằng chứng.",
            audience="Người 18-40 thích bí ẩn, trinh thám, phim tài liệu",
            persona="Thám tử điềm tĩnh mở từng tập hồ sơ",
            tone="Hồi hộp, chậm rãi, giọng trầm, mở nút thắt từng lớp",
            tone_rules=(
                "Start at the single most unexplainable detail.",
                "Reveal evidence one piece per beat; withhold the theory until late.",
                "Present 2-3 competing explanations fairly.",
                "No gore, no victim blaming, no naming private individuals in recent cases.",
            ),
            hook_formulas=(
                "Năm [năm], [số] người biến mất và chỉ để lại [chi tiết kỳ lạ].",
                "Đến nay chưa ai giải thích được vì sao [hiện tượng].",
                "Tấm ảnh này có một chi tiết khiến các chuyên gia im lặng.",
                "Hồ sơ số [số]: [tên vụ việc].",
            ),
            avoid=("Graphic violence or gore", "Recent crimes involving private persons", "Supernatural claims as fact"),
            short_spec=_short((60, 90), "Dừng ở chi tiết gay cấn nhất: 'Phần 2 có trên kênh'."),
            long_spec=_long((900, 1500), "Gợi hồ sơ tiếp theo.",
                            ("Cold open: the most unexplainable detail",
                             "Case file: setting, people, timeline",
                             "Evidence reveals one by one with re-hooks",
                             "Competing theories weighed fairly",
                             "What remains unexplained today",
                             "Next case tease")),
            visual=VisualIdentity(
                profile_id="ch_noir_dossier",
                label="Noir hồ sơ: minh họa 2D tương phản cao, đen trắng và một điểm đỏ",
                style_description=(
                    "2D noir graphic-novel illustration: heavy black ink shapes and crisp linework with high-contrast "
                    "flat shadows, limited palette of ink black (#111111), aged off-white paper (#E8E2D0), slate grey "
                    "(#5A5F66) and a single accent of evidence red (#C0392B); case-file props such as folders, stamped "
                    "documents, map pins and old photographs drawn flat; orthographic 2D, no gore, no blood, no "
                    "gradients, no photorealism, no 3D."
                ),
                cast_appearance=(
                    "Silhouette-style figures with simple faces, the narrator detective drawn as a faceless figure in a "
                    "long coat and hat seen from behind or in profile"
                ),
                outfit="Flat slate-grey long coat and hat; only evidence objects use the red accent",
                palette=("#111111", "#E8E2D0", "#5A5F66", "#C0392B"),
                thumbnail_rule="One mysterious object circled in red on off-white paper + 2-3 word case title.",
            ),
            references=(
                ReferenceChannel("Các kênh 'Kỳ Án / Hồ Sơ'", "TikTok", "short",
                                 "Start mid-mystery and cut at the peak with a part-2 call."),
                ReferenceChannel("Dương FG", "YouTube", "long",
                                 "Calm, detailed investigative storytelling."),
                ReferenceChannel("Độc Thám TV", "YouTube", "long",
                                 "Documentary-style reconstruction focused on evidence."),
            ),
            seed_topics=(
                "Sự cố đèo Dyatlov: 9 người leo núi và chiếc lều bị rạch từ bên trong",
                "Chuyến bay MH370 biến mất như thế nào",
                "Con tàu Mary Celeste trôi không người lái",
                "Người đàn ông Somerton và mẩu giấy 'Tamám Shud'",
                "Tín hiệu 'Wow!' từ vũ trụ năm 1977",
            ),
            hashtags=("#bian", "#hosokyla", "#chuyenkyla", "#mystery", "#learnontiktok"),
            monetization=("YouTube AdSense (retention cao)", "Series dài kỳ", "Membership"),
            wave=1,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="flow_full_frame",
                fast_short_max_images=8,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.30,
                estimated_short_minutes=(9, 13),
                estimated_bundle_minutes=(38, 48),
                notes="Build 1 deep 15-min Noir dossier on YouTube, slice 4 'Evidence #1..#4' cliffhanger shorts for TikTok with zero extra images.",
            ),
            engagement=EngagementSpec(
                cta_voice="Thám tử điềm tĩnh",
                bridge_templates=(
                    "Ba giả thuyết còn lại nằm trong hồ sơ đầy đủ trên YouTube.",
                ),
                close_templates=(
                    "Hồ sơ tiếp theo đang chờ mở. Theo dõi để không lỡ.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
        ),
        ChannelProfile(
            id="co_the_ke",
            name="Cơ Thể Kể",
            niche="Sức khỏe và cơ thể được nhân hóa",
            promise="Các cơ quan trong người bạn tự kể chuyện, vui mà đúng khoa học.",
            audience="Người 18-40 quan tâm sức khỏe, thói quen sinh hoạt",
            persona="Các cơ quan nội tạng biết nói, mỗi cơ quan một tính cách",
            tone="Hài, nhân hóa, dễ thương nhưng chính xác về khoa học",
            tone_rules=(
                "Open with 'if you do X, this is what your body does'.",
                "Let one organ character narrate in first person.",
                "Every health claim must cite a medical source in the description.",
                "Never claim cures; end with 'hỏi bác sĩ nếu...' when relevant.",
            ),
            hook_formulas=(
                "Nếu bạn [thói quen], đây là điều [cơ quan] phải chịu.",
                "Điều gì xảy ra với cơ thể khi bạn [hành động] trong [thời gian]?",
                "[Cơ quan] của bạn đang than phiền vì [thói quen].",
                "Đừng [thói quen phổ biến] nữa, [cơ quan] sẽ cảm ơn bạn.",
            ),
            avoid=("Cure or treatment claims", "Supplement promotion without evidence", "Body shaming"),
            short_spec=_short((30, 45), "Hỏi: bạn có thói quen này không? Lưu lại để nhắc mình."),
            long_spec=_long((480, 720), "Gợi tập 'một ngày của cơ quan khác'."),
            visual=VisualIdentity(
                profile_id="ch_organ_buddies",
                label="Nội tạng dễ thương: cơ quan có mặt và tính cách, nền trắng sạch",
                style_description=(
                    "Clean 2D kawaii medical-explainer illustration: smooth medium black outlines (#222222), flat "
                    "unshaded fills in soft organ pink (#F4A6A6), stomach peach (#F6C28B), liver maroon (#A23E48), lung "
                    "rose (#F28C9B) and calm blue (#7FB3D5) on a flat solid white canvas (#FFFFFF); organs drawn as "
                    "simplified anatomically recognizable characters with tiny faces, stubby arms and expressive "
                    "eyebrows; orthographic 2D, no gore, no realistic anatomy textures, no gradients, no 3D."
                ),
                cast_appearance=(
                    "Recurring organ characters: Tim (heart) brave and loud, Dạ Dày (stomach) dramatic complainer, "
                    "Gan (liver) tired hard worker, Não (brain-shaped round pink blob) overthinking boss; plus a simple "
                    "doodle human host with a round white head"
                ),
                outfit="Organs have no clothing; the human host wears a flat calm-blue (#7FB3D5) T-shirt",
                palette=("#FFFFFF", "#F4A6A6", "#F6C28B", "#A23E48", "#F28C9B", "#7FB3D5"),
                thumbnail_rule="One organ character with a dramatic expression + 2-3 word warning in bold letters.",
            ),
            references=(
                ReferenceChannel("Zack D. Films", "YouTube Shorts/TikTok", "short",
                                 "Drop straight into 'what happens if' with zero intro (format only)."),
                ReferenceChannel("Kurzgesagt", "YouTube", "long", "Deep, well-sourced science explainers."),
                ReferenceChannel("Bác sĩ Huy", "TikTok", "short", "Vietnamese doctor-backed health myths busting."),
            ),
            seed_topics=(
                "Điều gì xảy ra khi bạn nhịn ăn sáng 1 tháng",
                "Dạ dày nói gì khi bạn ăn khuya",
                "Một ngày của lá gan sau bữa nhậu",
                "Vì sao ngồi lâu làm đau lưng",
                "Uống nước đá có thật sự hại không",
            ),
            hashtags=("#suckhoe", "#cothe", "#songkhoe", "#bacsi", "#learnontiktok"),
            monetization=("YouTube AdSense", "Affiliate đồ gia dụng sức khỏe (không tuyên bố chữa bệnh)", "Booking"),
            wave=1,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=6,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.40,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(30, 40),
                notes="Fixed 4 organ mascots (Tim, Dạ Dày, Gan, Não) + Remotion timeline timers ('Sau 15 phút...', 'Sau 2 giờ...').",
            ),
            engagement=EngagementSpec(
                cta_voice="Nội tạng biết nói",
                bridge_templates=(
                    "Muốn nghe tim, gan, não kể tiếp? Bản dài trên YouTube.",
                ),
                close_templates=(
                    "Cái cổ của bạn nhờ mình nhắn: lưu video này giùm nó.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
        ),
        ChannelProfile(
            id="ai_binh_dan",
            name="AI Bình Dân",
            niche="Mẹo dùng AI và công nghệ cho người thường",
            promise="Một mẹo AI làm được ngay trong 1 phút, không cần biết code.",
            audience="Người đi làm văn phòng, sinh viên, chủ shop nhỏ",
            persona="Đồng nghiệp rành công nghệ, chỉ từng bước 'làm theo liền'",
            tone="Thực chiến, nhanh, hào hứng, chỉ từng bước",
            tone_rules=(
                "Show the end result in the first 3 seconds, then how.",
                "Every step must be reproducible with free tools.",
                "Use screen_capture shots for tool steps (ask user to record or capture via CDP).",
                "State tool names and limits honestly; no fake results.",
            ),
            hook_formulas=(
                "Một câu lệnh này giúp bạn [kết quả] trong [thời gian].",
                "Đừng [cách cũ] nữa, AI làm trong 30 giây.",
                "[Số] mẹo AI miễn phí dân văn phòng nên biết.",
                "Mình đã thử [công cụ] để [việc], và đây là kết quả.",
            ),
            avoid=("Promising income from AI", "Paid-tool shilling without disclosure", "Unsafe privacy practices"),
            short_spec=_short((30, 60), "Hỏi: bạn muốn mẹo cho công việc gì? Lưu lại để dùng."),
            long_spec=_long((600, 1200), "Gợi hướng dẫn chuyên sâu tiếp theo.",
                            ("Cold open: final result demo",
                             "Who needs this and what it saves",
                             "Step-by-step screen walkthrough in chapters",
                             "Common mistakes and limits",
                             "Template / prompt recap",
                             "Next tutorial tease")),
            visual=VisualIdentity(
                profile_id="ch_tech_doodle",
                label="Doodle công nghệ: stickman + khung màn hình, chèn quay màn hình thật",
                style_description=(
                    "Hand-drawn 2D tech doodle explainer illustration: wobbly black marker outlines (#000000), flat "
                    "unshaded fills in electric blue (#3B82C4), violet (#7C5CFF), mint (#34D399) and soft grey (#E5E7EB) "
                    "on a flat solid white canvas (#FFFFFF); simple hand-drawn laptop, phone and browser-window frames "
                    "with abstract placeholder content, cursor arrows and checkmarks; orthographic 2D, at least 60% "
                    "empty space, no gradients, no glossy UI, no 3D."
                ),
                cast_appearance=doodle_cast,
                outfit="Flat violet (#7C5CFF) hoodie and slate-grey trousers, no folds, no shading",
                palette=("#FFFFFF", "#3B82C4", "#7C5CFF", "#34D399", "#E5E7EB", "#000000"),
                thumbnail_rule="Before/after result on a hand-drawn screen + stickman pointing + 2-3 word promise.",
            ),
            references=(
                ReferenceChannel("Nghề Công Sở (Richard Võ)", "TikTok", "short",
                                 "'One prompt does X' with instant visible result."),
                ReferenceChannel("Văn Thế Web", "YouTube", "long", "Full step-by-step AI workflow tutorials."),
                ReferenceChannel("Nam Hệ Thống AI", "YouTube", "long", "Data-driven tool walkthroughs."),
            ),
            seed_topics=(
                "Dùng AI tóm tắt file PDF 50 trang trong 1 phút",
                "Viết email xin nghỉ phép khéo léo bằng một câu lệnh",
                "Tạo bảng chi tiêu tự động bằng AI và Google Sheets",
                "3 mẹo chụp ảnh sản phẩm bằng điện thoại và AI cho chủ shop",
                "Dùng AI luyện phỏng vấn xin việc",
            ),
            hashtags=("#ai", "#meocongnghe", "#chatgpt", "#vanphong", "#learnontiktok"),
            monetization=("YouTube AdSense", "Affiliate phần mềm / khóa học (có công khai)", "Template bán kèm"),
            philosophy_id="research_guide",
            wave=1,
            speed=1.0,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="screen_capture_hybrid",
                fast_short_max_images=4,
                spinoff_shorts_per_long=5,
                remotion_motion_ratio=0.60,
                estimated_short_minutes=(5, 8),
                estimated_bundle_minutes=(25, 35),
                notes="Fastest channel: 60% scenes are Remotion prompt terminal cards or screen_capture; only 3-4 Flow doodle images per short.",
            ),
            engagement=EngagementSpec(
                cta_voice="Đồng nghiệp chỉ từng bước",
                bridge_templates=(
                    "Bốn quy trình còn lại mình làm mẫu từng bước trên YouTube.",
                ),
                close_templates=(
                    "Lưu lại, mai làm theo liền. Gửi cho đồng nghiệp hay đọc hợp đồng.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
        ),
        ChannelProfile(
            id="luat_ngam",
            name="Luật Ngầm Đám Đông",
            niche="Tâm lý xã hội, hiệu ứng bầy đàn và nghệ thuật đàm phán đời thường",
            promise="Bóc tách một hiệu ứng tâm lý đám đông hoặc mánh thao túng trong 60 giây để không bị dẫn dắt.",
            audience="Người đi làm, người tiêu dùng, người muốn đọc vị hành vi xã hội",
            persona="Nhà quan sát hành vi sắc sảo, điềm tĩnh, vạch trần cơ chế ngầm",
            tone="Sắc sảo, khách quan, cuốn hút, mở nút từng lớp tâm lý",
            tone_rules=(
                "Bóc tách một cơ chế thao túng hoặc hiệu ứng bầy đàn trong 3 giây đầu.",
                "Đặt người xem vào vị trí nạn nhân trước, giải thích lý do tâm lý sau.",
                "Luôn dùng ví dụ đám đông đời thường tại Việt Nam (quán ăn đông khách, chen lấn, săn sale).",
                "Kết thúc bằng 1 bước tự vệ tâm lý cụ thể người xem dùng được ngay.",
            ),
            hook_formulas=(
                "Vì sao bạn luôn [hành vi bầy đàn] dù biết [hậu quả]?",
                "3 mánh tâm lý đám đông khiến bạn [hành động] mà không hề hay biết.",
                "Bạn không tự quyết định món đồ đó: đám đông đã chọn thay bạn.",
                "Nếu thấy [dấu hiệu đám đông], bạn đang rơi vào bẫy thao túng này.",
            ),
            avoid=("Lên án hay phán xét đạo đức người xem", "Lý thuyết tâm lý học hàn lâm thiếu ví dụ", "Mẹo thao túng phi đạo đức"),
            short_spec=_short((45, 60), "Hỏi người xem: bạn từng dính bẫy tâm lý này chưa? Bình luận số 1 nhé."),
            long_spec=_long((600, 900), "Gợi video tiếp theo về bẫy thao túng tâm lý đám đông."),
            visual=VisualIdentity(
                profile_id="ch_crowd_noir",
                label="Minh họa 2D noir trinh thám: hồ sơ giấy cũ, tương phản cao, sợi chỉ đỏ",
                style_description=(
                    "High-contrast 2D noir graphic-novel illustration on aged dossier paper canvas (#111111 heavy black ink, "
                    "#E8E2D0 aged dossier paper, #5A5F66 smoke-slate, single #C0392B crimson accent for strings and stamps); "
                    "shadowed crowd profiles, classified document dossiers, red connection threads and atmospheric silhouette contrasts; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero shading gradients."
                ),
                cast_appearance="Stylized anonymous silhouette figures in sharp trench coats and shadowed crowd profiles with glowing white slit eyes, zero stick figures",
                outfit="Sharp flat charcoal-black trench coat with crisp collar and single crimson lapel pin, no shading gradients",
                palette=("#111111", "#E8E2D0", "#5A5F66", "#C0392B", "#FFFFFF"),
                thumbnail_rule="Silhouette figure inspecting crimson case files + 2-4 uppercase VN words.",
            ),
            references=(
                ReferenceChannel("Academy of Ideas", "YouTube", "long",
                                 "Deep social psychology breakdowns with iconic 2D metaphors."),
                ReferenceChannel("Psych2Go Vietnam", "TikTok", "short",
                                 "Everyday psychological hooks that make viewers identify immediately."),
                ReferenceChannel("Nghệ Thuật Đàm Phán & Tâm Lý Học Hành Vi", "Book/Scripture", "long",
                                 "Nguyên lý đòn bẩy tâm lý đám đông, hiệu ứng mỏ neo và kỹ thuật nhượng bộ có đi có lại."),
            ),
            seed_topics=(
                "chọn theo đám đông",
                "Hiệu ứng bầy đàn: vì sao quán càng đông người ta lại càng muốn vào ăn",
                "Bẫy khan hiếm nhân tạo: mánh khóe khiến bạn chốt đơn trong 10 giây",
                "Hiệu ứng người ngoài cuộc: vì sao giữa đám đông không ai chịu ra tay giúp đỡ",
                "Thao túng bằng cảm giác tội lỗi trong đàm phán đời thường",
            ),
            hashtags=("#tamlyxahoi", "#hieuungbaydan", "#damphan", "#luatngam", "#kienthuc"),
            monetization=("YouTube AdSense", "Affiliate sách tâm lý & đàm phán", "Khóa học tư duy phản biện"),
            philosophy_id="cognition",
            wave=2,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=6,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.40,
                estimated_short_minutes=(8, 12),
                estimated_bundle_minutes=(35, 45),
                notes="Minimalist crowd stickmen vs focal red stickman; kinetic dominos & puppet strings in Remotion cut Flow generation.",
            ),
            engagement=EngagementSpec(
                cta_voice="Nhà quan sát sắc sảo",
                bridge_templates=(
                    "Ba mánh thao túng ngầm còn lại mình bóc tách trọn bộ trên YouTube Luật Ngầm Đám Đông.",
                ),
                close_templates=(
                    "Lưu lại để không bao giờ bị dẫn dắt. Gửi cho bạn bè hay bị bẫy săn sale.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@LuatNgamDamDongVN", "@LuatNgamVN", "@KenhLuatNgam", "@LuatNgamDamDong"]},
        ),
        ChannelProfile(
            id="ban_do_quyen_luc",
            name="Bản Đồ Quyền Lực",
            niche="Địa chính trị, kinh tế học tài nguyên và các tuyến hàng hải chiến lược",
            promise="Nhìn vào một tấm bản đồ để hiểu vì sao thế giới vận hành như hiện tại.",
            audience="Người quan tâm thời sự quốc tế, kinh tế vĩ mô, lịch sử địa lý",
            persona="Người giải mã bản đồ chiến lược bằng ngôn từ đời thường",
            tone="Mạch lạc, tầm nhìn lớn, dẫn chứng địa lý - tài nguyên xác đáng",
            tone_rules=(
                "Mở đầu bằng một điểm nghẽn địa lý hoặc tài nguyên bất ngờ ngoài thực địa hay trên sa bàn chiến lược.",
                "Mọi cuộc xung đột hay hiệp ước đều phải quy về dòng chảy tiền, dầu, khoáng sản hoặc hàng hóa.",
                (
                    "Hình ảnh tuân thủ 3 trụ cột nhiếp ảnh thực tế & vật lý: "
                    "(1) Địa hình vệ tinh 3D màu tự nhiên & sa bàn bàn phân tích địa chất; "
                    "(2) Nhiếp ảnh Macro 100mm cơ chế cơ khí/vật lý; "
                    "(3) Ảnh phóng sự công nghiệp & địa chính trị thực địa — đa dạng góc máy, vật liệu và ánh sáng "
                    "theo từng tập, tuyệt đối không dùng đồ họa vector 2D phẳng, vòng radar viễn tưởng, HUD hay chữ chèn "
                    "trong các beat nội dung."
                ),
                "Không thiên vị chính trị; chỉ phân tích lợi ích quốc gia và địa lý cốt lõi.",
            ),
            hook_formulas=(
                "Tử huyệt địa lý này giải thích vì sao [quốc gia] luôn [hành động].",
                "Nếu [eo biển/tuyến đường] này bị đóng, bữa ăn của bạn sẽ đắt gấp đôi.",
                "Vì sao tấm bản đồ này quyết định giá xăng dầu thế giới tuần tới?",
                "3 điểm nghẽn địa chính trị có thể làm tê liệt toàn cầu trong 48 giờ.",
            ),
            avoid=("Tuyên truyền chính trị một chiều", "Kích động thù hằn dân tộc", "Dự đoán chiến tranh giật gân vô căn cứ"),
            short_spec=_short((50, 60), "Hỏi người xem: bạn nghĩ điểm nghẽn tiếp theo nằm ở đâu? Bình luận nhé."),
            long_spec=_long((720, 1080), "Gợi mở chương tiếp theo về bàn cờ địa chính trị toàn cầu."),
            visual=VisualIdentity(
                profile_id="ch_tactical_atlas",
                label="Nhiếp ảnh thực tế 3 trụ cột: Địa hình vệ tinh/Sa bàn thật, Macro 100mm cơ khí & Phóng sự công nghiệp",
                style_description=(
                    "Three-pillar photorealistic geopolitical documentary photography with diverse per-episode lighting, "
                    "materials, and focal lengths: (1) True-color 3D orbital satellite relief photography and physical "
                    "walnut tabletop geological relief maps with brass compasses, steel dividers, raw ore stones, and "
                    "solid metal bars; (2) 100mm macro physical and mechanical photography of real machinery, copper motor "
                    "coils, silver permanent magnets, cleanroom silicon wafers, and hydrometallurgical tanks; "
                    "(3) Photorealistic industrial, maritime, and field documentary photography; strictly zero flat 2D "
                    "vector graphics, zero sci-fi HUD or radar rings, zero on-screen text clutter in body beats."
                ),
                cast_appearance=(
                    "Character-free physical realism: natural satellite terrain reliefs, real geological ore specimens, "
                    "physical brass navigation instruments, precision laboratory wafers, and real maritime freight vessels "
                    "(zero human cartoon figures)"
                ),
                outfit=(
                    "No cartoon clothing; authentic industrial metals, natural mineral textures, laboratory steel, "
                    "and weathered maritime hulls"
                ),
                palette=("#10202E", "#D8CBB8", "#C83E3B", "#D98A3C", "#2A6F68"),
                thumbnail_rule=(
                    "Full-bleed dramatic studio macro & 3D physical terrain relief photography (crimson steel locking "
                    "clamp gripping silicon wafer or metal bar over natural relief map) + 2-4 bold yellow uppercase VN "
                    "words with thick black outline in clean dark upper safe zone."
                ),
            ),
            references=(
                ReferenceChannel("RealLifeLore", "YouTube", "long",
                                 "Strategic geography and choke-point logistics explained via clean maps."),
                ReferenceChannel("Johnny Harris", "YouTube", "short",
                                 "Fast-paced visual map journalism showing why geography dictates borders and conflicts."),
                ReferenceChannel("Những Tù Nhân Của Địa Lý (Tim Marshall)", "Book/Scripture", "long",
                                 "Sách kinh điển giải thích địa lý tự nhiên định hình chính trị, chiến tranh và số phận các quốc gia."),
            ),
            seed_topics=(
                "xem bản đồ thế giới",
                "Eo biển Malacca: yết hầu năng lượng quyết định vận mệnh Đông Á",
                "Kênh đào Suez: vì sao một con tàu kẹt làm cả thế giới mất hàng tỷ đô",
                "Bản đồ đất hiếm: cuộc chiến ngầm đằng sau mọi chiếc smartphone",
                "Kênh đào Panama khô hạn: giá hàng hóa toàn cầu bị bóp nghẹt ra sao",
            ),
            hashtags=("#diachinhtri", "#bandoquyenluc", "#kinhtethegioi", "#lichsudialy", "#kienthuc"),
            monetization=("YouTube AdSense RPM cao", "Sponsor dịch vụ tài chính vĩ mô / logistics", "Affiliate sách địa lý & chiến lược"),
            philosophy_id="cognition",
            wave=2,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(30, 40),
                notes="Flat 2D contour maps with Remotion animated trade-route arrows & choke-point pulses save 50% Flow calls.",
            ),
            engagement=EngagementSpec(
                cta_voice="Nhà phân tích chiến lược",
                bridge_templates=(
                    "Tấm bản đồ toàn cảnh và ba kịch bản vận tải mình mổ xẻ trên YouTube Bản Đồ Quyền Lực.",
                ),
                close_templates=(
                    "Lưu lại để hiểu thời sự quốc tế. Bạn nghĩ eo biển nào quan trọng nhất?",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@BanDoQuyenLucVN", "@BanDoQuyenLucOfficial", "@KenhBanDoQuyenLuc", "@BanDoQuyenLuc"]},
        ),
        ChannelProfile(
            id="dia_com",
            name="Đĩa Cơm Khoa Học",
            niche="Hóa học ẩm thực, an toàn thực phẩm và khoa học trong căn bếp Việt",
            promise="Hiểu đúng từng phản ứng hóa học trong mâm cơm hàng ngày để ăn ngon và lành.",
            audience="Người nấu ăn gia đình, nhân viên văn phòng, người quan tâm sức khỏe ăn uống",
            persona="Đầu bếp mê hóa học, giải thích chuyện bếp núc bằng thực nghiệm vui vẻ",
            tone="Gần gũi, thực tế, khoa học rõ ràng, không hù dọa vô căn cứ",
            tone_rules=(
                "Bắt đầu bằng một thói quen nấu nướng hoặc niềm tin ẩm thực quen thuộc trong mâm cơm Việt.",
                "Giải thích phản ứng hóa học bằng hình vẽ ẩn dụ phân tử 2D cực kỳ dễ hiểu.",
                "Tuyệt đối không hù dọa ung thư vô căn cứ; đưa ra khoảng liều lượng và nhiệt độ an toàn.",
                "Kết thúc bằng 1 mẹo bếp núc ứng dụng được ngay tối nay.",
            ),
            hook_formulas=(
                "Vì sao [món ăn/thói quen bếp] tưởng vô hại lại biến chất ở [nhiệt độ]?",
                "Khoa học giải thích vì sao mẹ bạn luôn [thói quen nấu ăn] đúng đến kinh ngạc.",
                "Bí mật hóa học đằng sau miếng thịt kho tàu mềm rục mà không nát.",
                "Đừng [thói quen rã đông/bảo quản] kiểu này nếu không muốn vi khuẩn nhân đôi.",
            ),
            avoid=("Hù dọa ung thư giật gân (fear-mongering)", "Lời khuyên dinh dưỡng cực đoan", "Bác bỏ y học chính thống"),
            short_spec=_short((40, 55), "Hỏi người xem: nhà bạn có hay làm cách này không? Bình luận chia sẻ nhé."),
            long_spec=_long((600, 840), "Gợi thực đơn khoa học tiếp theo cho bữa cơm gia đình."),
            visual=VisualIdentity(
                profile_id="ch_culinary_mascots",
                label="Sticker-pop ẩm thực: linh vật Bé Gạo, Bé Lửa và phân tử dinh dưỡng viền trắng nổi",
                style_description=(
                    "Bold 2D kawaii culinary sticker-pop illustration on warm porcelain white canvas (#FFFDF7 warm porcelain white canvas, "
                    "#FF6B6B chili coral, #FFD166 egg-yolk gold, #06D6A0 herb mint, #26547C cast-iron navy) with smooth dark outlines "
                    "and chunky white sticker borders; expressive culinary ingredients, kitchen utensils and nutritional molecules; "
                    "orthographic 2D, at least 60% clean negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Adorable recurring personified kitchen mascots led by Bé Gạo (plump white rice-grain character with rosy cheeks and tiny chef toque), Bé Lửa (cheerful kitchen flame sprite), and expressive amino and sugar molecule buddies with full rounded mascot anatomy and expressive faces",
                outfit="Tiny white chef toque and red bandana on Bé Gạo; cheerful golden flame contour for Bé Lửa",
                palette=("#FFFDF7", "#FF6B6B", "#FFD166", "#06D6A0", "#26547C", "#FFFFFF"),
                thumbnail_rule="Expressive Bé Gạo mascot with food chemical reaction + 2-4 uppercase VN words.",
            ),
            references=(
                ReferenceChannel("Ann Reardon (How To Cook That)", "YouTube", "long",
                                 "Debunking viral food hacks with verified food science experiments."),
                ReferenceChannel("Nhiệt Kế Ẩm Thực", "TikTok", "short",
                                 "Everyday kitchen chemistry myths busted in 60 seconds."),
                ReferenceChannel("Hóa Học Ẩm Thực (On Food and Cooking - Harold McGee)", "Book/Scripture", "long",
                                 "Kinh thánh khoa học ẩm thực thế giới về cơ chế phân tử trong nhiệt độ, chất béo và gia vị."),
            ),
            seed_topics=(
                "nấu ăn tại nhà",
                "Phản ứng Maillard: bí quyết để thịt áp chảo dậy mùi thơm nức mũi",
                "Vì sao rã đông thịt bằng nước nóng là sai lầm nguy hiểm",
                "Hóa học của nồi nước dùng phở trong veo không bị đục",
                "Cơm nguội hâm lại: cách bảo quản đúng để không sinh độc tố",
            ),
            hashtags=("#diacomkhoahoc", "#antoanthucpham", "#khoahocnhabep", "#suckhoe", "#kienthuc"),
            monetization=("YouTube AdSense", "Sponsor thiết bị bếp / đồ gia dụng lành mạnh", "Affiliate sách ẩm thực & dinh dưỡng"),
            philosophy_id="cognition",
            wave=2,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=6,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.35,
                estimated_short_minutes=(8, 12),
                estimated_bundle_minutes=(35, 45),
                notes="Kitchen props & flat 2D temperature gauges in Remotion kinetic motion reduce image generation needs.",
            ),
            engagement=EngagementSpec(
                cta_voice="Đầu bếp khoa học",
                bridge_templates=(
                    "Toàn bộ bảng nhiệt độ chuẩn và năm thí nghiệm chi tiết mình để trên YouTube Đĩa Cơm Khoa Học.",
                ),
                close_templates=(
                    "Lưu lại để nấu bữa tối chuẩn ngon và an toàn. Gửi cho người nấu cơm nhà bạn nhé.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@DiaComKhoaHocVN", "@DiaComKhoaHocOfficial", "@KenhDiaComKhoaHoc", "@DiaComKhoaHoc"]},
        ),
        ChannelProfile(
            id="luat_doi_thuong",
            name="Luật Đời Thường",
            niche="Pháp lý dân sự bình dân: hợp đồng, thuê nhà, đặt cọc, lao động, vay mượn",
            promise="Hiểu đúng luật đời thường trong 1 phút để tự bảo vệ quyền lợi và túi tiền của mình.",
            audience="Người đi thuê nhà, người lao động, người kinh doanh nhỏ, gia đình trẻ",
            persona="Người bạn hiểu luật, giải thích điều khoản rắc rối bằng ví dụ bình dân",
            tone="Rõ ràng, chuẩn xác, thực tế, bảo vệ người yếu thế",
            tone_rules=(
                "Mở đầu bằng một tình huống tranh chấp tiền nong hoặc hợp đồng mà ai cũng có thể gặp.",
                "Trích dẫn đúng tinh thần điều luật hiện hành nhưng giải thích bằng từ ngữ bình dân.",
                "Luôn chỉ rõ: điều khoản nào là bẫy vô hiệu, làm sao thu thập chứng cứ hợp pháp.",
                "Khuyến cáo rõ: video mang tính tham khảo kiến thức, vụ việc cụ thể cần luật sư tư vấn.",
            ),
            hook_formulas=(
                "Đi thuê nhà thấy điều khoản này trong hợp đồng: tuyệt đối không đặt bút ký.",
                "Chủ nhà không chịu trả tiền cọc: 3 bước đòi lại tiền đúng luật 100%.",
                "Cho bạn thân vay tiền chuyển khoản ghi nội dung này: coi như mất trắng.",
                "Công ty ép nhân viên nghỉ việc không bồi thường: cách tự vệ chuẩn pháp lý.",
            ),
            avoid=("Tư vấn pháp lý cho vụ án cụ thể đang xử lý", "Xúi giục lách luật hoặc trốn tránh nghĩa vụ", "Dùng thuật ngữ pháp lý hàn lâm khó hiểu"),
            short_spec=_short((45, 60), "Hỏi người xem: bạn từng gặp tranh chấp tương tự chưa? Bình luận nhé."),
            long_spec=_long((600, 900), "Gợi vụ việc dân sự điển hình tiếp theo cần phòng tránh."),
            visual=VisualIdentity(
                profile_id="ch_legal_risograph",
                label="Đồ họa Risograph báo chí: minh họa bút mực New Yorker, con dấu pháp lý đỏ trên nền giấy ngà",
                style_description=(
                    "Mid-century New Yorker-inspired 2D editorial pen-and-ink risograph print on ivory newsprint canvas "
                    "(#F4EFE6 ivory newsprint, #1D3557 Prussian ink navy, #E63946 vermilion legal-stamp red, #A8DADC celadon highlight) "
                    "with subtle paper grain texture, crisp fountain-pen linework, contract seals and balance scales; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Expressive stylized human legal advocate with neat parted dark hair, horn-rimmed glasses, fountain pen and contract folder with proper stylized editorial human proportions",
                outfit="Crisp Prussian navy (#1D3557) blazer over cream collared shirt with vermilion red pocket square, no shading",
                palette=("#F4EFE6", "#1D3557", "#E63946", "#A8DADC", "#457B9D"),
                thumbnail_rule="Sharp legal advocate pointing out red contract trap + 2-4 uppercase VN words.",
            ),
            references=(
                ReferenceChannel("Luật Sư X", "TikTok", "short",
                                 "Clear legal warnings on everyday consumer and tenant traps in 60s."),
                ReferenceChannel("Thư Viện Pháp Luật", "YouTube", "long",
                                 "Systematic legal code explanations broken down for ordinary citizens."),
                ReferenceChannel("Bộ Luật Dân Sự & Luật Đất Đai Thực Chiến", "Book/Scripture", "long",
                                 "Căn cứ pháp lý chuẩn mực giải quyết tranh chấp hợp đồng, đặt cọc và quyền sở hữu tài sản."),
            ),
            seed_topics=(
                "đọc kỹ hợp đồng",
                "5 cái bẫy trong hợp đồng thuê nhà khiến sinh viên mất trắng tiền cọc",
                "Chuyển khoản cho vay tiền: ghi nội dung gì để có giá trị pháp lý",
                "Thử việc xong bị công ty cho nghỉ không lý do: bạn được bồi thường gì",
                "Mua đất giấy tay: những rủi ro pháp lý mất trắng nhà cửa",
            ),
            hashtags=("#luatdoithuong", "#phaplybinhdan", "#hopdong", "#baovequyenloi", "#kienthuc"),
            monetization=("YouTube AdSense", "Hợp tác giới thiệu văn phòng luật sư uy tín", "Template hợp đồng chuẩn dân sự"),
            philosophy_id="cognition",
            wave=2,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=6,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.40,
                estimated_short_minutes=(8, 11),
                estimated_bundle_minutes=(30, 42),
                notes="Contract parchment highlighting with Remotion red warning stamps cuts Flow generation by 40%.",
            ),
            engagement=EngagementSpec(
                cta_voice="Người bạn hiểu luật",
                bridge_templates=(
                    "Mẫu văn bản đòi cọc và toàn bộ căn cứ luật mình hướng dẫn kỹ trên YouTube Luật Đời Thường.",
                ),
                close_templates=(
                    "Lưu lại để tự bảo vệ túi tiền của mình. Gửi cho bạn bè đang chuẩn bị thuê phòng trọ.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@LuatDoiThuongVN", "@LuatDoiThuongOfficial", "@KenhLuatDoiThuong", "@LuatDoiThuong"]},
        ),
        ChannelProfile(
            id="banh_rang",
            name="Bánh Răng Thế Giới",
            niche="Kinh tế vĩ mô, lạm phát, lãi suất và chuỗi cung ứng toàn cầu giải thích bình dân",
            promise="Thấy rõ các bánh răng kinh tế ngầm đang tác động tới lương và giá cả quanh bạn.",
            audience="Người đi làm, nhà đầu tư cá nhân F0, chủ doanh nghiệp nhỏ",
            persona="Người tháo lắp cỗ máy kinh tế bằng sơ đồ bánh răng trực quan",
            tone="Logic, nhân quả sắc bén, biến vĩ mô khô khan thành chuyện sát sườn",
            tone_rules=(
                "Mỗi video chỉ giải thích đúng 1 mắt xích nhân quả vĩ mô (A tăng -> B giảm -> C tác động tới bạn).",
                "Quy mọi thuật ngữ lớn (Fed tăng lãi suất, nới lỏng định lượng) về giá tô phở, tiền lãi ngân hàng.",
                "Dùng sơ đồ bánh răng hoặc đường ống tiền tệ trực quan.",
                "Không khuyến nghị đầu cơ lướt sóng; tập trung vào cơ chế vận hành dài hạn.",
            ),
            hook_formulas=(
                "Ngân hàng Trung ương Mỹ vừa bấm một nút, vì sao giá bát phở ở Việt Nam lại tăng?",
                "Lạm phát thật ra không phải giá tăng: nó là tiền của bạn đang bốc hơi.",
                "Bánh răng kinh tế nào quyết định tiền lương của bạn sau 3 năm nữa?",
                "Vì sao lãi suất giảm mà người dân lại càng ngại chi tiêu?",
            ),
            avoid=("Khuyến nghị mua bán cổ phiếu, crypto cụ thể", "Dự đoán đáy đỉnh thị trường", "Lý thuyết kinh tế giáo điều thiếu số liệu"),
            short_spec=_short((45, 60), "Hỏi người xem: bạn có cảm nhận rõ bánh răng này chưa? Bình luận nhé."),
            long_spec=_long((660, 960), "Gợi bánh răng kinh tế tiếp theo đang âm thầm quay chuyển."),
            visual=VisualIdentity(
                profile_id="ch_macro_blueprint",
                label="Bản vẽ kinh tế vĩ mô: blueprint xanh Phổ, sơ đồ hệ thống tài chính Thụy Sĩ chuẩn xác",
                style_description=(
                    "Crisp 2D Prussian-blue architectural blueprint and Swiss macroeconomic schematic on deep navy canvas "
                    "(#142B47 Prussian blueprint navy background, #F1FAEE crisp white technical linework, #F4A261 brass-gold indicator accent, "
                    "#4CC9F0 cyan grid lines); precision technical drafting lines, systemic feedback loops, trade corridors and currency flow vectors; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Sleek flat geometric mid-century economist presenter with structured angular shoulders, neat hair, brass pointer rod, accompanied by technical cross-sections of container ships, central-bank vaults and currency scales",
                outfit="Flat dark-slate minimalist vest over rolled-up technical drafting shirt, zero shading",
                palette=("#142B47", "#F1FAEE", "#F4A261", "#4CC9F0", "#1D3557"),
                thumbnail_rule="Macroeconomic blueprint schematic with glowing gold key lever + 2-4 uppercase VN words.",
            ),
            references=(
                ReferenceChannel("Ray Dalio (How The Economic Machine Works)", "YouTube", "long",
                                 "Visual machine metaphor explaining credit cycles and inflation simply."),
                ReferenceChannel("Economics Explained", "YouTube", "short",
                                 "60-second animated macro breakdowns connecting interest rates to daily life."),
                ReferenceChannel("Dòng Tiền Thông Minh & Chu Kỳ Kinh Tế", "Book/Scripture", "long",
                                 "Cơ chế dòng tiền luân chuyển giữa các lớp tài sản khi lãi suất và lạm phát đảo chiều."),
            ),
            seed_topics=(
                "lo lắng tiền bạc",
                "Vì sao Mỹ in thêm nghìn tỷ USD nhưng cả thế giới gánh lạm phát",
                "Cơ chế lãi suất ngân hàng: chiếc phanh hãm cỗ máy kinh tế hoạt động ra sao",
                "Vòng xoáy giảm phát: vì sao giá hàng hóa hạ lại là cơn ác mộng",
                "Bẫy nợ quốc gia và cơ chế tái cấu trúc dòng vốn toàn cầu",
            ),
            hashtags=("#banhrangthegioi", "#kinhtevimo", "#lamphat", "#dongtien", "#kienthuc"),
            monetization=("YouTube AdSense RPM cao", "Sponsor nền tảng quản lý tài chính / ngân hàng", "Khóa học kiến thức kinh tế vĩ mô căn bản"),
            philosophy_id="cognition",
            wave=2,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.50,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Rotating 2D gear SVG components & currency pipe flows animated directly in Remotion cut Flow reliance.",
            ),
            engagement=EngagementSpec(
                cta_voice="Người tháo lắp cỗ máy kinh tế",
                bridge_templates=(
                    "Sơ đồ toàn bộ cỗ máy tiền tệ và chu kỳ 10 năm mình phân tích trên YouTube Bánh Răng Thế Giới.",
                ),
                close_templates=(
                    "Lưu lại để hiểu vì sao giá cả thay đổi. Bạn thấy bánh răng nào quan trọng nhất?",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@BanhRangTheGioiVN", "@BanhRangTheGioiOfficial", "@KenhBanhRangTheGioi", "@BanhRangTheGioi"]},
        ),
        ChannelProfile(
            id="vu_tru_ti_hon",
            name="Vũ Trụ Tí Hon",
            niche="Thiên văn học, vật lý lượng tử và các nghịch lý không-thời gian giải thích kiểu Feynman",
            promise="Đặt cả vũ trụ bao la vào một hình vẽ đơn giản để ai cũng chạm tới vẻ đẹp vật lý.",
            audience="Học sinh, sinh viên, người yêu khoa học vũ trụ và các câu hỏi lớn về thực tại",
            persona="Người kể chuyện bầu trời đêm theo tinh thần Feynman đầy tò mò",
            tone="Kinh ngạc, giàu hình ảnh ẩn dụ, chuẩn xác vật lý nhưng bình dị",
            tone_rules=(
                "Mở đầu bằng một câu hỏi ngây thơ nhưng chạm đến tận cùng bản chất vũ trụ.",
                "Tuyệt đối dùng tư duy Feynman: giải thích bằng quả bóng, tấm bạt cao su, không dùng phương trình khó.",
                "Khơi gợi cảm xúc ngạc nhiên, khiêm nhường trước quy luật của tạo hóa.",
                "Đảm bảo số liệu kích thước, khoảng cách được đối chiếu với vật thể quen thuộc.",
            ),
            hook_formulas=(
                "Nếu bạn rơi vào lỗ đen, bạn sẽ nhìn thấy tương lai của vũ trụ trước khi chết.",
                "Thời gian thật ra không hề trôi: nghịch lý này khiến Einstein mất 10 năm chứng minh.",
                "Mỗi nguyên tử trên tay bạn đều từng được tôi luyện bên trong một ngôi sao nổ tung.",
                "Nếu vũ trụ vô tận, tại sao bầu trời đêm lại có màu đen?",
            ),
            avoid=("Khoa học viễn tưởng giả danh vật lý lý thuyết", "Dùng công thức toán phức tạp làm nản lòng người xem", "Thần bí hóa tâm linh phản khoa học"),
            short_spec=_short((40, 55), "Hỏi người xem: câu hỏi vũ trụ nào khiến bạn tò mò nhất? Bình luận nhé."),
            long_spec=_long((720, 1020), "Gợi câu hỏi kỳ vĩ tiếp theo về không-thời gian."),
            visual=VisualIdentity(
                profile_id="ch_cosmos_vector",
                label="Vũ trụ vector hình học: phong cách Kurzgesagt rực rỡ, robot thám hiểm Tí Hon trên nền vũ trụ sâu",
                style_description=(
                    "Luminous Kurzgesagt-inspired 2D flat geometric space vector illustration on deep cosmic indigo canvas "
                    "(#0B1026 deep cosmic indigo canvas, #4CC9F0 pulsar cyan, #FF6B6B supernova coral, #FFD166 starlight gold, #7209B7 nebula violet) "
                    "with crisp rounded vector shapes, radiant celestial bodies, orbital trajectories and zero black marker outlines; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Adorable compact spherical robotic space-probe mascot Tí Hon with a glowing cyan visor eye and tiny thruster wings floating beside vibrant geometric planets",
                outfit="Seamless white and polished gold chassis plating with glowing pulsar-cyan optic lens visor, no human clothes",
                palette=("#0B1026", "#4CC9F0", "#FF6B6B", "#FFD166", "#7209B7", "#FFFFFF"),
                thumbnail_rule="Glowing robotic probe Tí Hon near dramatic space phenomenon + 2-4 uppercase VN words.",
            ),
            references=(
                ReferenceChannel("Kurzgesagt – In a Nutshell", "YouTube", "long",
                                 "Optimistic nihilism and cosmos mysteries explained with charming 2D animation."),
                ReferenceChannel("MinutePhysics", "YouTube", "short",
                                 "Stick figure physics breakdowns solving mind-bending paradoxes in minutes."),
                ReferenceChannel("Vũ Trụ Trong Vỏ Hạt Dẻ (Stephen Hawking)", "Book/Scripture", "long",
                                 "Nghịch lý lỗ đen và vẻ đẹp của vật lý lượng tử qua những ẩn dụ thị giác giàu hình ảnh."),
            ),
            seed_topics=(
                "ngắm nhìn bầu trời",
                "Nghịch lý Olbers: vì sao bầu trời đêm lại đen khi có vô số ngôi sao",
                "Hiệu ứng giãn nở thời gian: vì sao phi hành gia già chậm hơn",
                "Bên trong đường chân trời sự kiện của lỗ đen thực sự có gì",
                "Thí nghiệm khe đôi: một hạt có thể đi qua cả hai khe cùng lúc",
            ),
            hashtags=("#vutrutihon", "#thienvanhoc", "#vatly", "#khoahocvutru", "#kienthuc"),
            monetization=("YouTube AdSense", "Affiliate kính thiên văn / sách khoa học", "Sponsor các tổ chức giáo dục STEM"),
            philosophy_id="cognition",
            wave=2,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=6,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.40,
                estimated_short_minutes=(8, 11),
                estimated_bundle_minutes=(32, 42),
                notes="Flat 2D planet orbits, light beams & time dilation diagrams animated via Remotion SVG layers.",
            ),
            engagement=EngagementSpec(
                cta_voice="Người kể chuyện bầu trời đêm",
                bridge_templates=(
                    "Chuyến du hành trọn vẹn và ba nghịch lý lượng tử mình giải thích trên YouTube Vũ Trụ Tí Hon.",
                ),
                close_templates=(
                    "Lưu lại để cùng ngắm bầu trời đêm. Câu hỏi vật lý nào làm bạn đau đầu nhất?",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@VuTruTiHonVN", "@VuTruTiHonOfficial", "@KenhVuTruTiHon", "@VuTruTiHon"]},
        ),
        ChannelProfile(
            id="nghe_song_sot",
            name="Nghề Sống Sót",
            niche="Chiến lược sự nghiệp, quy luật ngầm chốn công sở và thích nghi thời đại AI",
            promise="Hiểu luật chơi thật sự của thị trường lao động để không bao giờ bị đào thải.",
            audience="Nhân viên văn phòng, sinh viên mới ra trường, quản lý cấp trung",
            persona="Đàn anh đi làm 10 năm nói thẳng sự thật công sở không màu hồng",
            tone="Thẳng thắn, thực tế, định hướng giải pháp nâng cấp giá trị bản thân",
            tone_rules=(
                "Mở đầu bằng một sự thật trần trụi chốn công sở mà trường học không bao giờ dạy.",
                "Nói thẳng nhưng mang tính xây dựng; không than vãn, tập trung vào đòn bẩy kỹ năng.",
                "Mọi lời khuyên đều phải giúp người xem tăng vị thế đàm phán lương và thăng tiến.",
                "Kết thúc bằng 1 hành động cụ thể có thể làm ngay vào sáng thứ Hai.",
            ),
            hook_formulas=(
                "Người chăm chỉ nhất công ty thường là người dễ bị thay thế nhất: vì sao?",
                "3 dấu hiệu công ty sắp thanh lọc nhân sự mà bạn cần nhận ra trước 3 tháng.",
                "Đừng bao giờ nói câu này khi sếp hỏi: 'Em thấy dạo này công việc thế nào?'",
                "Quy luật ngầm tăng lương 50%: không phải làm thêm giờ, mà là nắm mắt xích này.",
            ),
            avoid=("Lời khuyên độc hại: xúi giục phản bội đồng nghiệp", "Khoe khoang thành tích cá nhân", "Ru ngủ bằng những lời khuyên tích cực hời hợt"),
            short_spec=_short((45, 60), "Hỏi người xem: công ty bạn có như vậy không? Bình luận chia sẻ nhé."),
            long_spec=_long((600, 900), "Gợi chiến lược sự nghiệp dài hạn tiếp theo."),
            visual=VisualIdentity(
                profile_id="ch_career_doodle",
                label="Doodle công sở: stickman + bậc thang sự nghiệp/bàn cờ 2D tối giản",
                style_description=(
                    "Hand-drawn 2D career strategy doodle explainer illustration: wobbly black marker outlines (#000000), "
                    "flat unshaded fills in warm office cream (#F8F0DC), royal blue (#3B82C4), "
                    "coral accent (#F2B88B), sage green (#93A88C) and white (#FFFFFF) on a flat solid cream canvas (#F8F0DC); "
                    "simple flat 2D career ladders, office desks, lever metaphors and stickman with lanyard; "
                    "orthographic 2D, at least 60% empty negative space, no 3D, no gradients."
                ),
                cast_appearance=doodle_cast,
                outfit="Flat royal-blue (#3B82C4) shirt with simple ID lanyard, no shading",
                palette=("#F8F0DC", "#3B82C4", "#F2B88B", "#93A88C", "#FFFFFF", "#000000"),
                thumbnail_rule="Stickman choosing leverage lever over endless stairs + 2-4 uppercase VN words.",
            ),
            references=(
                ReferenceChannel("The Futur (Chris Do)", "YouTube", "long",
                                 "Negotiation tactics and career value proposition frameworks."),
                ReferenceChannel("An Is Here", "TikTok", "short",
                                 "Direct, grounded workplace survival insights for Vietnamese corporate youth."),
                ReferenceChannel("Kỹ Năng Đàm Phán & Thăng Tiến Chốn Công Sở", "Book/Scripture", "long",
                                 "Nguyên tắc xây dựng giá trị cốt lõi không thể thay thế và thiết lập ranh giới nghề nghiệp."),
            ),
            seed_topics=(
                "đi làm chăm chỉ",
                "Bẫy thăng tiến: vì sao làm quản lý cấp trung là vị trí dễ kiệt sức nhất",
                "Cách nói chuyện với sếp khó tính mà không bị mất lòng hay lép vế",
                "Kỹ năng tạo đòn bẩy: làm sao để công việc tự chứng minh giá trị",
                "Khi nào nên nghỉ việc: 4 tín hiệu cho thấy công ty đã hết đất phát triển",
            ),
            hashtags=("#nghesongsot", "#chuyencongso", "#kinhnghiemdilam", "#phattriensunghiep", "#kienthuc"),
            monetization=("YouTube AdSense", "Coaching 1-on-1 sự nghiệp", "Khóa học đàm phán lương và giao tiếp công sở"),
            philosophy_id="cognition",
            wave=2,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=6,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.35,
                estimated_short_minutes=(8, 11),
                estimated_bundle_minutes=(32, 42),
                notes="Desk props & leverage ladder metaphors in Remotion motion reduce need for complex Flow variations.",
            ),
            engagement=EngagementSpec(
                cta_voice="Đàn anh 10 năm kinh nghiệm",
                bridge_templates=(
                    "Quy trình bốn bước đàm phán lại mức lương mình hướng dẫn trọn vẹn trên YouTube Nghề Sống Sót.",
                ),
                close_templates=(
                    "Lưu lại để không bao giờ bị động chốn công sở. Gửi cho đứa bạn đang chán việc.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@NgheSongSotVN", "@NgheSongSotOfficial", "@KenhNgheSongSot", "@NgheSongSot"]},
        ),
        ChannelProfile(
            id="la_ban_hoc_thuat",
            name="La Bàn Học Thuật",
            niche="Phương pháp tự học sâu, đọc hiểu tài liệu khoa học và nghiên cứu cho người mới",
            promise="Biến mọi tài liệu học thuật phức tạp thành quy trình từng bước ai cũng làm theo được.",
            audience="Sinh viên, học viên cao học, nhà nghiên cứu trẻ, người tự học chuyên sâu",
            persona="Người hướng dẫn nghiên cứu tận tâm, giải nghĩa học thuật bằng tiếng Việt trong sáng",
            tone="Chân phương, có hệ thống, truyền cảm hứng tự học và tư duy phản biện",
            tone_rules=(
                "Mở đầu bằng nỗi sợ hãi tài liệu học thuật dày đặc hoặc rào cản thuật ngữ tiếng Anh.",
                "Phá vỡ bài báo khoa học thành 3 câu hỏi cốt lõi: Vấn đề gì? Phương pháp nào? Kết quả ra sao?",
                "Luôn minh họa bằng kỹ thuật Feynman: giải thích cho một đứa trẻ 10 tuổi cũng hiểu.",
                "Kết thúc bằng 1 công cụ tra cứu hoặc quy trình ghi chú học tập thực chiến.",
            ),
            hook_formulas=(
                "Đừng đọc bài báo khoa học từ đầu đến cuối: đây là cách đọc 15 phút nắm trọn ý.",
                "Kỹ thuật Feynman 4 bước giúp bạn làm chủ mọi kiến thức khó chỉ sau một buổi tối.",
                "Vì sao bạn đọc sách chuyên ngành càng nhiều lại càng thấy mình không nhớ gì?",
                "3 bước viết phần mở đầu bài nghiên cứu khiến giảng viên gật đầu ngay lập tức.",
            ),
            avoid=("Biến kiến thức bình dân thành rắc rối hàn lâm", "Cổ xúy học vẹt, học để đối phó thi cử", "Đạo văn hoặc hướng dẫn gian lận học thuật"),
            short_spec=_short((45, 60), "Hỏi người xem: môn học nào đang làm bạn đau đầu nhất? Bình luận nhé."),
            long_spec=_long((660, 960), "Gợi quy trình tự học sâu chủ đề tiếp theo."),
            visual=VisualIdentity(
                profile_id="ch_academic_sketchbook",
                label="Sổ tay học thuật cổ điển: minh họa bút mực Da Vinci, giấy da vellum và sơ đồ phân loại",
                style_description=(
                    "Classical Da Vinci and Oxford archival ivory vellum fountain-pen illustration on warm archival vellum canvas "
                    "(#F6F1E3 warm archival vellum, #1F2D3D deep indigo fountain-pen ink, #B8860B antique brass compass gold, "
                    "#4F6D5A botanical library sage) with fine ink linework, index cards, marginalia annotations and taxonomy diagrams; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Warm scholarly human presenter with wavy dark hair, round brass spectacles, and flat olive-tweed vest over rolled white sleeves, holding a fountain pen or open leather notebook",
                outfit="Flat olive-tweed vest over crisp rolled-sleeve ivory oxford shirt with brass spectacles, no shading",
                palette=("#F6F1E3", "#1F2D3D", "#B8860B", "#4F6D5A", "#8C7A6B"),
                thumbnail_rule="Scholarly presenter holding open glowing manuscript + 2-4 uppercase VN words.",
            ),
            references=(
                ReferenceChannel("Ali Abdaal", "YouTube", "long",
                                 "Evidence-based study techniques and active recall systems."),
                ReferenceChannel("Tiến Sĩ Trẻ", "TikTok", "short",
                                 "Bite-sized research tips and academic writing templates for Vietnamese students."),
                ReferenceChannel("Kỹ Thuật Feynman & Cách Học Sâu (Deep Work - Cal Newport)", "Book/Scripture", "long",
                                 "Phương pháp tập trung sâu và chia nhỏ tài liệu phức tạp thành mô hình tư duy trực quan."),
            ),
            seed_topics=(
                "ghi chép cẩn thận",
                "Cách đọc hiểu một bài báo khoa học chuẩn quốc tế trong vòng 20 phút",
                "Kỹ thuật Feynman: thước đo tối thượng để biết bạn thật sự hiểu",
                "Phương pháp ghi chú Zettelkasten: biến tài liệu rời rạc thành mạng lưới",
                "Cách đặt câu hỏi nghiên cứu sắc bén cho luận văn tốt nghiệp",
            ),
            hashtags=("#labanhocthuat", "#phuongphaphoc", "#nghiencuukhoahoc", "#feynman", "#kienthuc"),
            monetization=("YouTube AdSense", "Affiliate ứng dụng ghi chú / quản lý tài liệu (Notion, Obsidian)", "Khóa học phương pháp nghiên cứu cho sinh viên"),
            philosophy_id="research_guide",
            wave=2,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="screen_capture_hybrid",
                fast_short_max_images=5,
                spinoff_shorts_per_long=5,
                remotion_motion_ratio=0.55,
                estimated_short_minutes=(6, 9),
                estimated_bundle_minutes=(26, 36),
                notes="Paper summary cards & knowledge tree nodes rendered cleanly via Remotion motion cards.",
            ),
            engagement=EngagementSpec(
                cta_voice="Người hướng dẫn nghiên cứu",
                bridge_templates=(
                    "Toàn bộ template đọc bài báo và sơ đồ tư duy mình chia sẻ trên YouTube La Bàn Học Thuật.",
                ),
                close_templates=(
                    "Lưu lại để dùng khi làm bài tập lớn. Gửi cho bạn cùng nhóm làm luận văn nhé.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@LaBanHocThuatVN", "@LaBanHocThuatOfficial", "@KenhLaBanHocThuat", "@LaBanHocThuat"]},
        ),
        ChannelProfile(
            id="chanh_niem_ke",
            name="Chánh Niệm Kể",
            niche="Triết lý Phật giáo ứng dụng, Chánh niệm (Mindfulness) và tâm lý học buông bỏ trong đời sống hiện đại",
            promise="Một tích truyện Thiền và bài học Chánh niệm giúp bạn lắng dịu tâm trí, chuyển hóa khổ đau trong 60 giây.",
            audience="Người đi làm căng thẳng, người muốn tìm sự bình an nội tâm và hiểu đúng triết lý Phật học nguyên thủy",
            persona="Người kể chuyện nhà Thiền điềm đạm, giải thích Phật pháp bằng tâm lý học gần gũi, không mê tín",
            tone="Trầm ấm, từ bi, tĩnh tại, sâu sắc, chữa lành",
            tone_rules=(
                "Mở đầu bằng một tích truyện Thiền ngắn hoặc nỗi bất an tâm lý đời thường trong 3 giây.",
                "Dùng ẩn dụ mũi tên thứ hai hoặc hạt giống tâm để giải thích cơ chế khổ đau.",
                "Không mê tín dị đoan, không cầu xin ban phước; tập trung vào sự quán chiếu và buông bỏ của tự tâm.",
                "Kết thúc bằng 1 bài tập thở hoặc câu hỏi quán chiếu giúp an trú trong hiện tại.",
            ),
            hook_formulas=(
                "Vì sao bạn càng cố xua đuổi [cơn giận/lo âu] thì nó lại càng lớn lên?",
                "Mũi tên thứ hai: bí mật Phật học giúp bạn thoát khỏi 90% nỗi khổ cuộc đời.",
                "Câu chuyện chiếc thuyền rỗng: vì sao bạn tức giận khi bị người khác va vào?",
                "Khi tâm trí quá tải lúc nửa đêm, hãy thử dừng lại và làm điều này.",
            ),
            avoid=("Mê tín dị đoan hoặc cúng bái giải hạn", "Giáo điều tôn giáo áp đặt", "Phán xét nghiệp chướng của người khác"),
            short_spec=_short((45, 60), "Hỏi người xem: bạn đang vướng bận điều gì? Thở một hơi thật sâu và buông xuống nhé."),
            long_spec=_long((600, 960), "Gợi tích truyện Thiền và bài tập chánh niệm tiếp theo."),
            visual=VisualIdentity(
                profile_id="ch_zen_sumie",
                label="Tranh thủy mặc Sumi-e thiền định: mực tàu trên giấy xuyến chỉ, khoảng lặng tĩnh tại",
                style_description=(
                    "Serene 2D East-Asian Sumi-e ink-wash painting on handmade Xuan rice paper canvas "
                    "(#F5EFE0 warm textured rice paper, #1C1C1C expressive calligraphy brush ink, #5F7A61 bamboo sage wash, "
                    "#D98A76 soft lotus blush, #8C7A6B tea-earth) with generous meditative negative space, water ripples and swaying bamboo strokes; "
                    "orthographic 2D, at least 65% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Peaceful minimalist brush-painted Zen practitioner with gentle facial contours, calm closed eyes, and flowing bamboo-sage linen robe",
                outfit="Flowing unadorned bamboo-sage (#5F7A61) linen robe with wide sleeves, zero shading",
                palette=("#F5EFE0", "#1C1C1C", "#5F7A61", "#D98A76", "#8C7A6B"),
                thumbnail_rule="Serene Zen monk meditating near ink-wash ripples + 2-4 uppercase VN words.",
            ),
            references=(
                ReferenceChannel("Làng Mai (Plum Village)", "YouTube", "long",
                                 "Kể chuyện đời thường dịu dàng, dùng ẩn dụ hạt giống tâm và hơi thở để chuyển hóa cơn giận, lo âu."),
                ReferenceChannel("Doug's Dharma", "YouTube", "long",
                                 "Giải thích Phật học nguyên thủy (Tứ Diệu Đế, Mũi tên thứ hai, Vô thường) khách quan, rõ ràng cho người hiện đại."),
                ReferenceChannel("Einzelgänger (Buddhism & Zen Series)", "YouTube", "long",
                                 "Mở đầu bằng tích truyện Thiền ngắn 15s rồi phân tích tâm lý học ứng dụng sâu sắc."),
                ReferenceChannel("Kinh Pháp Cú (Dhammapada)", "Book/Scripture", "short",
                                 "Kho ẩn dụ gốc: Mũi tên thứ hai, Chiếc thuyền rỗng, Con voi bị thuần hóa."),
            ),
            seed_topics=(
                "lắng dịu tâm trí",
                "Ẩn Dụ Mũi Tên Thứ Hai: Vì Sao Nỗi Đau Là Bắt Buộc Nhưng Khổ Đau Là Tự Chọn?",
                "Khi Cơn Giận Bốc Lên: Cách Ôm Ấp Tâm Mình Theo Tinh Thần Thiền Sư Thích Nhất Hạnh",
                "Câu Chuyện Chiếc Thuyền Rỗng: Vì Sao Ta Luôn Giận Người Khác Dù Họ Vô Tình?",
                "Hiểu Đúng Về Chữ Duyên Và Chữ Nghiệp Để Không Tự Dằn Vặt Quá Khứ",
                "Nghệ Thuật Dừng Lại 3 Hơi Thở Khi Tâm Trí Quá Tải Giữa Đêm",
            ),
            hashtags=("#chanhniemke", "#phatgiaoungdung", "#thien", "#buongbo", "#chualanh"),
            monetization=("YouTube AdSense", "Affiliate sách chánh niệm & chuông xoay", "Khóa thiền tĩnh tâm"),
            philosophy_id="cognition",
            wave=3,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Lotus ripples and two-arrows animations handled via Remotion kinetic SVG layers.",
            ),
            engagement=EngagementSpec(
                cta_voice="Người kể chuyện nhà Thiền",
                bridge_templates=(
                    "Toàn bộ bài giảng và mười phút thiền thở sâu mình chia sẻ trên YouTube Chánh Niệm Kể.",
                ),
                close_templates=(
                    "Thở vào tâm tĩnh lặng, thở ra miệng mỉm cười. Gửi video này cho người bạn thương nhé.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@ChanhNiemKeVN", "@ChanhNiemKeOfficial", "@KenhChanhNiemKe", "@ChanhNiemKe"]},
        ),
        ChannelProfile(
            id="loi_sang_soi",
            name="Lời Sáng Soi",
            niche="Dụ ngôn Kinh Thánh, lịch sử văn minh Kitô giáo và bài học yêu thương - tha thứ - hy vọng trong đời sống",
            promise="Giải mã một Dụ ngôn Kinh Thánh hoặc câu chuyện đức tin vượt thời gian bằng nét vẽ 2D trực quan, ấm áp.",
            audience="Người Công giáo, Tin Lành và mọi khán giả yêu thích triết lý nhân văn, lịch sử Kinh Thánh và sự nâng đỡ tâm hồn",
            persona="Người kể chuyện Dụ ngôn gần gũi, truyền tải thông điệp ánh sáng, lòng bao dung và hy vọng",
            tone="Ấm áp, nhân văn, tôn trọng lịch sử - kinh điển, truyền hy vọng",
            tone_rules=(
                "Mở đầu bằng một Dụ ngôn cổ xưa đặt trong bối cảnh đời sống hiện đại.",
                "Nhấn mạnh giá trị nhân văn phổ quát: tha thứ, ân điển, tình yêu thương và sự khiêm nhường.",
                "Tôn trọng lịch sử và văn bản gốc; không tranh luận thần học giáo phái.",
                "Kết thúc bằng thông điệp nâng đỡ tâm hồn, thắp lên hy vọng cho người đang bế tắc.",
            ),
            hook_formulas=(
                "Dụ ngôn 2000 năm trước giải thích vì sao bạn càng [hành vi] lại càng [kết quả]?",
                "Vì sao tha thứ cho kẻ làm tổn thương bạn lại là món quà dành cho chính bạn?",
                "Hạt cải nhỏ bé nhất: nghịch lý về niềm tin làm thay đổi toàn bộ số phận.",
                "Bài học quản trị cuộc đời từ Dụ ngôn Nén Bạc mà người hiện đại nên biết.",
            ),
            avoid=("Tranh cãi giáo phái Kitô giáo", "Lên án hay đe dọa trừng phạt", "Giải nghĩa sai lệch văn cảnh lịch sử Kinh Thánh"),
            short_spec=_short((45, 60), "Hỏi người xem: bạn thấy bài học nào chạm vào lòng mình nhất? Bình luận nhé."),
            long_spec=_long((600, 960), "Gợi câu chuyện Dụ ngôn tiếp theo về lòng bao dung."),
            visual=VisualIdentity(
                profile_id="ch_parable_woodcut",
                label="Tranh khắc gỗ dụ ngôn: phong cách BibleProject, đường khắc thô mộc trên nền giấy cổ",
                style_description=(
                    "Bold BibleProject-inspired 2D carved linocut and woodblock parable print on aged parchment canvas "
                    "(#EFE4C8 antique parchment, #1E1E1E carved woodcut ink outlines, #D9A520 radiant oil-lamp gold, "
                    "#5E7D3A olive-branch green, #9E3B33 terracotta clay); expressive relief cuts, olive groves and radiant lanterns; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Dignified woodcut human storyteller in woven indigo and ochre cloak holding a warm glowing clay oil lamp",
                outfit="Woven indigo tunic under draped terracotta and ochre cloak, carved woodcut texture, no modern clothing",
                palette=("#EFE4C8", "#1E1E1E", "#D9A520", "#5E7D3A", "#9E3B33"),
                thumbnail_rule="Woodcut storyteller holding radiant oil lamp in dark + 2-4 uppercase VN words.",
            ),
            references=(
                ReferenceChannel("BibleProject", "YouTube", "long",
                                 "Chuẩn vàng thế giới về vẽ 2D sketch giải thích Dụ ngôn Kinh Thánh, lịch sử và từ khóa Ân điển, Tình yêu thương."),
                ReferenceChannel("IMBeggar", "YouTube", "short",
                                 "Phong cách stickman/doodle tối giản giải thích các câu hỏi lớn về đức tin, sự tha thứ và lòng khiêm nhường."),
                ReferenceChannel("Ascension Presents", "YouTube", "long",
                                 "Kết nối các dụ ngôn cổ xưa với khủng hoảng thực tế của con người hiện đại (cô đơn, thất bại, tha thứ)."),
                ReferenceChannel("Sách Châm Ngôn & Tân Ước", "Book/Scripture", "short",
                                 "Nguồn tích truyện gốc: Dụ ngôn Nén Bạc, Người Con Hoang Đàng, Người Samari Nhân Lành, Hạt Cải."),
            ),
            seed_topics=(
                "tha thứ bao dung",
                "Dụ Ngôn Nén Bạc: Bài Học Quản Trị Cuộc Đời Từ Câu Chuyện 2000 Năm Trước",
                "Vì Sao Tha Thứ Cho Người Làm Tổn Thương Mình Lại Là Giải Thoát Cho Chính Ta?",
                "Dụ Ngôn Người Con Hoang Đàng: Khi Nào Cánh Cửa Bao Dung Vẫn Mở Đợi Bạn Về?",
                "5 Lời Khuyên Về Tiền Bạc Và Sự Khôn Ngoan Trong Sách Châm Ngôn Salômôn",
                "Câu Chuyện David Và Goliath: Cách Chiến Thắng Những Gã Khổng Lồ Mang Tên Sợ Hãi",
            ),
            hashtags=("#loisangsoi", "#dungonkinhthanh", "#chualanh", "#baihoccuocsong", "#kienthuc"),
            monetization=("YouTube AdSense", "Affiliate sách hạt giống tâm hồn & văn hóa lịch sử", "Ủng hộ thiện nguyện cộng đồng"),
            philosophy_id="cognition",
            wave=3,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Warm parchment scrolls and glowing lantern rays animated in Remotion reduce Flow prompts.",
            ),
            engagement=EngagementSpec(
                cta_voice="Người kể chuyện Dụ ngôn",
                bridge_templates=(
                    "Toàn cảnh bối cảnh lịch sử và bài học chi tiết mình để trên YouTube Lời Sáng Soi.",
                ),
                close_templates=(
                    "Nguyện sự bình an ở cùng bạn đêm nay. Chia sẻ tia sáng này đến người cần được ủi an nhé.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@LoiSangSoiVN", "@LoiSangSoiOfficial", "@KenhLoiSangSoi", "@LoiSangSoi"]},
        ),
        ChannelProfile(
            id="minh_triet_song",
            name="Minh Triết Sống",
            niche="Minh triết Phương Đông (Lão Tử, Trang Tử) kết hợp Chủ nghĩa Khắc kỷ (Stoicism) giúp giữ tâm bất biến",
            promise="Một nguyên lý cổ xưa từ Lão Trang hoặc Khắc kỷ giúp bạn điềm tĩnh trước mọi biến cố đời thường.",
            audience="Người trưởng thành, người làm quản lý, người tìm kiếm bản lĩnh nội tâm và triết học ứng dụng",
            persona="Người bạn triết gia bình dị, đúc kết tinh hoa Đông - Tây thành nguyên tắc sống thực tế",
            tone="Điềm tĩnh, sâu sắc, khúc chiết, bản lĩnh",
            tone_rules=(
                "Mở đầu bằng một nghịch lý cuộc sống hoặc áp lực ganh đua thường nhật.",
                "Đối chiếu góc nhìn Vô Vi (Lão Tử) và Vòng tròn kiểm soát (Khắc kỷ).",
                "Không nói đạo lý sáo rỗng; tập trung vào hành động làm chủ tâm thức.",
                "Kết thúc bằng 1 thái độ sống giúp đứng vững trước thị phi và biến cố.",
            ),
            hook_formulas=(
                "Vì sao người càng tranh giành lại càng dễ mất mát, người buông tay lại có tất cả?",
                "Hoàng đế La Mã Marcus Aurelius đã làm gì khi bị thuộc cấp phản bội?",
                "Quy luật con ngựa của Tái Ông: vì sao xui xẻo hôm nay lại là phúc lành ngày mai?",
                "Cái dũng của người điềm tĩnh: tại sao im lặng lại có sức mạnh hơn vạn lời cãi vã?",
            ),
            avoid=("Triết lý bi quan, yếm thế lánh đời", "Lý thuyết triết học hàn lâm khó hiểu", "Đạo lý suông thiếu ứng dụng thực tế"),
            short_spec=_short((45, 60), "Hỏi người xem: bạn chọn cách buông bỏ hay đối đầu? Chia sẻ góc nhìn nhé."),
            long_spec=_long((600, 960), "Gợi bài học minh triết tiếp theo về nghệ thuật sống an nhiên."),
            visual=VisualIdentity(
                profile_id="ch_stoic_ink_scroll",
                label="Cuộn thư triết học cổ điển: nét cọ phương Đông kết hợp cột đá Khắc kỷ phương Tây",
                style_description=(
                    "Timeless 2D brush-and-chisel philosophical scroll illustration on aged silk-scroll cream canvas "
                    "(#F2E9D8 aged silk-scroll cream, #222831 charcoal ink, #4F6D5A pine-jade green, #C08552 warm bronze-ochre) "
                    "blending Eastern bamboo brushwork with crisp classical marble colonnades and stone stelae; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Composed bearded philosopher sage drawn in refined classical ink lines wearing a draped slate-and-linen tunic",
                outfit="Draped slate-charcoal and unbleached linen philosopher tunic with a simple leather sash, no modern details",
                palette=("#F2E9D8", "#222831", "#4F6D5A", "#C08552", "#E8D8C8"),
                thumbnail_rule="Composed philosopher standing calmly beside marble column + 2-4 uppercase VN words.",
            ),
            references=(
                ReferenceChannel("Einzelgänger (Taoism & Stoicism)", "YouTube", "long",
                                 "Kết hợp triết lý Vô Vi (Wu Wei) của Lão Tử và Khắc kỷ của Marcus Aurelius bằng cấu trúc 3 chương mạch lạc."),
                ReferenceChannel("Daily Stoic", "YouTube", "short",
                                 "Mở đầu bằng nghịch lý cảm xúc đời thường rồi giải quyết bằng vòng tròn kiểm soát Khắc kỷ."),
                ReferenceChannel("Tủ sách Thu Giang Nguyễn Duy Cần", "Book/Scripture", "long",
                                 "Chuẩn mực diễn giải triết học Đông phương sang tiếng Việt giản dị, sâu sắc."),
                ReferenceChannel("The School of Life", "YouTube", "long",
                                 "Emotional philosophy and philosophical practical lessons."),
            ),
            seed_topics=(
                "giữ tâm điềm tĩnh",
                "Triết Lý Vô Vi Của Lão Tử: Vì Sao Càng Cố Cưỡng Cầu Mọi Thứ Càng Vỡ Vụn?",
                "Cái Dũng Của Người Điềm Tĩnh: Khi Im Lặng Mạnh Hơn Vạn Lời Tranh Cãi",
                "Định Luật Con Ngựa Của Tái Ông: Vì Sao Xui Xẻo Hôm Nay Có Thể Là May Mắn Ngày Mai?",
                "Bài Học Của Hoàng Đế Marcus Aurelius Khi Đối Mặt Với Kẻ Phản Bội Và Thị Phi",
                "Cách Tách Biệt Thứ Kiểm Soát Được Và Thứ Phải Buông Bỏ Theo Triết Học Khắc Kỷ",
            ),
            hashtags=("#minhtrietsong", "#khacky", "#laotu", "#triethocungdung", "#binhtam"),
            monetization=("YouTube AdSense", "Affiliate sách triết học ứng dụng", "Khóa học tâm lý bản lĩnh lãnh đạo"),
            philosophy_id="cognition",
            wave=3,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Bamboo sway and Stoic dichotomy-of-control rings animated directly in Remotion.",
            ),
            engagement=EngagementSpec(
                cta_voice="Người bạn triết gia",
                bridge_templates=(
                    "Toàn bộ phân tích sâu sắc về Đạo Đức Kinh và Khắc kỷ mình chia sẻ trên YouTube Minh Triết Sống.",
                ),
                close_templates=(
                    "Tâm bất biến giữa dòng đời vạn biến. Lưu lại để tự nhắc nhở bản thân mỗi khi bất an.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@MinhTrietSongVN", "@MinhTrietSongOfficial", "@KenhMinhTrietSong", "@MinhTrietSong"]},
        ),
        ChannelProfile(
            id="tam_tinh_dem",
            name="Tâm Tĩnh Đêm",
            niche="Truyện ngụ ngôn tỉnh thức, bài học nhân quả, lòng biết ơn và chiêm nghiệm chữa lành trước khi ngủ",
            promise="Một câu chuyện ngụ ngôn lắng đọng mỗi tối giúp bạn gác lại âu lo và ngủ thật bình yên.",
            audience="Khán giả nghe đêm (21h-24h), người cần chữa lành tổn thương, yêu thích truyện ngụ ngôn nhân sinh",
            persona="Người kể chuyện đêm khuya ấm áp, thủ thỉ những bài học nhân sinh sâu sắc",
            tone="Thủ thỉ, lắng đọng, giàu cảm xúc, nhân văn",
            tone_rules=(
                "Mở đầu bằng không gian đêm yên ắng và một tình huống ngụ ngôn chạm đến cảm xúc.",
                "Nhịp kể chậm rãi, từ tốn; từng câu đều mang hơi thở chữa lành và vỗ về tâm hồn.",
                "Kết nối ngụ ngôn với lòng biết ơn cha mẹ, tình thân, sự tha thứ cho chính mình.",
                "Kết thúc bằng lời chúc ngủ ngon an yên, nhắc nhở gác lại muộn phiền của ngày hôm nay.",
            ),
            hook_formulas=(
                "Đêm nay trước khi nhắm mắt, có một câu chuyện ngắn mình muốn kể cho bạn nghe.",
                "Bài học từ chiếc bình nứt: vì sao những khiếm khuyết của bạn lại tạo nên điều kỳ diệu?",
                "Ba chiếc sàng của Socrates: điều bạn sắp nghe có thật sự đáng để bận lòng?",
                "Vì sao chúng ta luôn bao dung với người ngoài nhưng lại khắt khe với người thương nhất?",
            ),
            avoid=("Nội dung kinh dị hay gây giật mình ban đêm", "Giọng điệu chỉ trích nặng nề", "Kịch tính hóa xung đột gây khó ngủ"),
            short_spec=_short((45, 60), "Gửi lời chúc: Đêm nay hãy ngủ thật ngon nhé, ngày mai sẽ là một ngày mới dịu dàng."),
            long_spec=_long((600, 960), "Gợi câu chuyện ngụ ngôn chữa lành tiếp theo trước giờ đi ngủ."),
            visual=VisualIdentity(
                profile_id="ch_midnight_gouache",
                label="Màu bột gouache đêm ấm áp: phong cách Hoàng Tử Bé, bầu trời đêm nhung và trăng vàng",
                style_description=(
                    "Cozy Little Prince-inspired 2D flat matte gouache night-storybook illustration on velvety midnight indigo sky canvas "
                    "(#1B263B velvety midnight indigo sky, #F4D35E warm crescent-moon and lantern gold, #E09F7D cozy amber tea glow, "
                    "#778DA9 misty starlight blue, #F8F4E3 soft cream) with soft painterly edges, constellations and peaceful bedtime scenes; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Gentle storybook traveler with tousled dark hair and a warm golden-amber knitted scarf holding a steaming ceramic teacup under starry night skies",
                outfit="Cozy midnight-blue woolen coat with long warm golden-amber (#F4D35E) knitted scarf, zero shading",
                palette=("#1B263B", "#F4D35E", "#E09F7D", "#778DA9", "#F8F4E3"),
                thumbnail_rule="Gentle traveler sitting under starry crescent moon + 2-4 uppercase VN words.",
            ),
            references=(
                ReferenceChannel("Dare to do. Motivation", "YouTube", "long",
                                 "Kể chuyện ngụ ngôn Zen/Cổ tích cho người lớn với nhịp độ lắng đọng, đúc kết bài học nhân sinh ở 2 phút cuối."),
                ReferenceChannel("Hạt Giống Tâm Hồn", "YouTube", "short",
                                 "Chạm đúng tâm lý người Việt về tình thân, nhân quả, áp lực mưu sinh và sự tử tế."),
                ReferenceChannel("Hiểu Về Trái Tim (Minh Niệm)", "Book/Scripture", "long",
                                 "Nguồn cảm hứng phân tích tâm lý chữa lành, lòng biết ơn và luật nhân quả đời thường."),
                ReferenceChannel("Web5ngay", "YouTube", "long",
                                 "Bài học nhân sinh đời thường thủ thỉ, sâu lắng."),
            ),
            seed_topics=(
                "nghĩ về lòng biết ơn",
                "Ba Chiếc Sàng Của Socrates: Quy Tắc Lọc Lời Đồn Trước Khi Để Tâm Trí Bị Tổn Thương",
                "Chiếc Bình Nứt Và Bài Học Chấp Nhận Những Khiếm Khuyết Của Chính Mình",
                "Câu Chuyện Bát Mì Đêm Mưa: Vì Sao Ta Hay Tử Tế Với Người Lạ Nhưng Gắt Gỏng Với Người Thân?",
                "Luật Nhân Quả Trong Lời Nói: Một Câu Nói Ấm Áp Có Thể Cứu Một Ngày Tồi Tệ Ra Sao?",
                "Trước Khi Đi Ngủ Đêm Nay: 3 Thứ Cần Đặt Xuống Để Sáng Mai Thức Dậy Nhẹ Lòng",
            ),
            hashtags=("#tamtinhdem", "#truyenngungon", "#nhansinh", "#chualanhtamhon", "#binhyen"),
            monetization=("YouTube AdSense", "Affiliate trà thảo mộc & nến thơm", "Sách nói chiêm nghiệm đêm"),
            philosophy_id="cognition",
            wave=3,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Gentle floating lantern and moon glow transitions created via Remotion filters.",
            ),
            engagement=EngagementSpec(
                cta_voice="Người kể chuyện đêm khuya",
                bridge_templates=(
                    "Trọn vẹn câu chuyện ngụ ngôn và nhạc nền tĩnh tâm dài 20 phút trên YouTube Tâm Tĩnh Đêm.",
                ),
                close_templates=(
                    "Chúc bạn một giấc ngủ thật sâu và bình an. Hẹn gặp lại bạn vào đêm mai.",
                ),
                endcard_text="BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                banned_cta_phrases=DEFAULT_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@TamTinhDemVN", "@TamTinhDemOfficial", "@KenhTamTinhDem", "@TamTinhDem"]},
        ),
        ChannelProfile(
            id="en_lazy_brain",
            name="Lazy Brain Lab",
            niche="Neuroscience of procrastination, dopamine habits, focus & behavioral psychology",
            promise="Decode why your brain procrastinates, in plain English with relatable stickman doodles.",
            audience="Busy thinkers, students, and professionals fighting dopamine traps and distraction",
            persona="Curious neuroscience buddy who explains brain quirks without academic guilt",
            tone="Conversational, witty, empathetic, grounded in cognitive psychology",
            tone_rules=(
                "Hook with an everyday procrastination habit within 3 seconds.",
                "Explain the brain circuit using physical metaphors like leaky buckets or alarm bells.",
                "Zero shame or toxic hustle advice; focus on friction reduction.",
                "End with one frictionless 2-minute actionable experiment.",
            ),
            hook_formulas=(
                "Why your brain loves procrastinating on goals that actually matter to you.",
                "You are not lazy. Your prefrontal cortex is simply stuck in a loop.",
                "The 2-minute dopamine rule that breaks doomscrolling immediately.",
                "Why does cleaning your desk feel urgent only when a deadline hits?",
            ),
            avoid=("Diagnosing clinical mental illness", "Toxic hustle culture advice", "Heavy peer-reviewed jargon without plain analogies"),
            short_spec=_short((35, 50), "Which brain habit caught you today? Share your number below."),
            long_spec=_long((480, 720), "Join us next time as we explore more quirks of the human brain."),
            visual=VisualIdentity(
                profile_id="ch_en_lazy_brain_doodle",
                label="Minimalist Cognitive Vector: flat cream canvas, cobalt focal subject, coral accent",
                style_description=(
                    "Minimalist flat-vector cognitive explainer in Primer and Kurzgesagt aesthetic on solid flat warm cream canvas (#F8F0DC). "
                    "Exactly ONE single hero subject or behavioral metaphor per frame, rendered with clean solid flat fills and crisp defined outlines "
                    "in cobalt blue (#3B82C4) with a vibrant coral red (#E63946) action accent. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Iconic 2D minimalist vector stickman with clean white (#FFFFFF) circle head, solid black contour, tiny dot eyes, minimal smile, clean wire arms and round circle hands",
                outfit="Flat cobalt-blue (#3B82C4) t-shirt and dark trousers with crisp clean contours, zero shading, zero gradients",
                palette=("#F8F0DC", "#3B82C4", "#E63946"),
                thumbnail_rule="Extreme close-up of single cognitive hero subject with ticking clock metaphor on flat cream canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("The Paint Explainer", "YouTube", "long", "Ultra-minimalist doodle explainer pacing and clear visual metaphors."),
                ReferenceChannel("Better Ideas", "YouTube", "long", "Relatable self-improvement storytelling and procrastination deconstruction."),
                ReferenceChannel("Atomic Habits & Dopamine Nation", "Book/Scripture", "long", "Clear behavioral habit loops and neuroscience frameworks."),
                ReferenceChannel("Psych2Go Shorts", "TikTok/YouTube Shorts", "short", "High-relatability 3-second psychological hook questions."),
            ),
            seed_topics=(
                "Why Your Brain Loves Procrastinating on Important Goals (And How to Trick It)",
                "The 2-Minute Dopamine Reset That Stops Doomscrolling Instantly",
                "Why Perfectionism Paralyzes Your Prefrontal Cortex",
                "Revenge Bedtime Procrastination: Why You Stay Awake at 2 AM",
                "How Micro-Habits Bypass Your Brain's Threat Detector",
            ),
            hashtags=("#neuroscience", "#procrastination", "#dopamine", "#focus", "#habits", "#productivity"),
            monetization=("YouTube AdSense (long)", "Digital focus planners", "Curated book club affiliate"),
            philosophy_id="cognition",
            voice="OmniVoice_EnLazyBrain",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.4,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion dopamine meter pulse and countdown timer animations.",
            ),
            engagement=EngagementSpec(
                cta_voice="Curious neuroscience friend",
                bridge_templates=(
                    "Watch the complete 12-minute neuroscience breakdown on Lazy Brain Lab YouTube.",
                    "See the full dopamine experiment and habit loop guide on our main channel.",
                ),
                close_templates=(
                    "Which of these brain traps caught you today? Share your thoughts below.",
                    "Try the two-minute test today and see if your focus resets quietly.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@LazyBrainLab", "@LazyBrainLabHQ", "@LazyBrainDoodle", "@TheLazyBrainLab"]},
        ),
        ChannelProfile(
            id="en_crowd_strings",
            name="Crowd Strings",
            niche="Social psychology, herd behavior, subtle persuasion & everyday negotiation",
            promise="Expose the invisible social strings pulling your decisions, so you never get manipulated.",
            audience="Curious minds seeking psychological awareness, consumer defense, and smart negotiation",
            persona="Sharp observer of social currents, dissecting herd psychology with calm clarity",
            tone="Analytical, observant, intriguing, grounded in behavioral game theory",
            tone_rules=(
                "Hook with a common social compliance trap within 3 seconds.",
                "Expose the subtle persuasion cue or herd dynamic clearly.",
                "Illustrate with everyday retail, workplace, or social scenarios.",
                "Provide one immediate psychological boundary rule.",
            ),
            hook_formulas=(
                "7 psychological traps stores use to empty your wallet without you noticing.",
                "The anchoring trick that makes you overpay every single time.",
                "Why good people do terrible things inside a crowd.",
                "The Benjamin Franklin effect: how a tiny favor builds instant trust.",
            ),
            avoid=("Promoting deceitful manipulation tactics", "Paranoid conspiracy rhetoric", "Academic jargon without tangible examples"),
            short_spec=_short((35, 50), "Have you noticed this crowd trap before? Drop your reaction below."),
            long_spec=_long((480, 720), "Explore our next deep-dive on social psychology on Crowd Strings."),
            visual=VisualIdentity(
                profile_id="ch_en_crowd_noir",
                label="Minimalist Editorial Noir Vector: solid deep slate canvas, ivory silhouette, crimson tension accent",
                style_description=(
                    "Minimalist flat-vector editorial noir explainer in Vox aesthetic on solid flat deep slate canvas (#111827). "
                    "Exactly ONE single hero focal subject or herd metaphor per frame, rendered with bold solid fills and razor-sharp contours "
                    "in parchment ivory (#F3F4F6) and an electric crimson red (#DC2626) tension accent. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Sharp-suited minimal silhouette observer with crisp ivory collar and single crimson lapel pin, flat 2D vector style with zero hatching",
                outfit="Flat slate-black trench coat silhouette with crisp ivory collar and single crimson pin, clean vector contours",
                palette=("#111827", "#F3F4F6", "#DC2626"),
                thumbnail_rule="Extreme close-up of single silhouette cutting one crimson cord on flat deep slate canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("Charisma on Command", "YouTube", "long", "Deconstructing social dynamics and charisma in everyday conversations."),
                ReferenceChannel("The School of Life", "YouTube", "long", "Philosophical and psychological human behavior explanations."),
                ReferenceChannel("Influence by Robert Cialdini & Thinking, Fast and Slow by Daniel Kahneman", "Book/Scripture", "long", "Core cognitive biases, social proof, and decision architecture."),
                ReferenceChannel("Daily Negotiation Insights", "TikTok/YouTube Shorts", "short", "Punchy 30-second negotiation and psychological defense tips."),
            ),
            seed_topics=(
                "7 Psychological Traps Stores Use to Empty Your Wallet Without You Noticing",
                "The Anchoring Trick That Makes You Overpay Every Single Time",
                "Why Good People Do Terrible Things Inside a Crowd",
                "The Benjamin Franklin Effect: How Asking for a Tiny Favor Builds Instant Trust",
                "3 Negotiation Moves FBI Hostage Negotiators Use in Daily Life",
            ),
            hashtags=("#psychology", "#persuasion", "#socialpsychology", "#negotiation", "#influence", "#mindset"),
            monetization=("YouTube AdSense (long)", "Negotiation masterclass sponsorship", "Recommended psychology books affiliate"),
            philosophy_id="cognition",
            voice="OmniVoice_EnCrowdStrings",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.4,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion animated puppet string overlays and crowd vector arrows.",
            ),
            engagement=EngagementSpec(
                cta_voice="Astute social analyst",
                bridge_templates=(
                    "Watch the complete negotiation breakdown on Crowd Strings YouTube channel.",
                    "See all seven psychological tactics analyzed in full on our YouTube channel.",
                ),
                close_templates=(
                    "Have you spotted this tactic before? Comment your thoughts below.",
                    "Notice this cue tomorrow and tell us if you see through the crowd trap.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@CrowdStrings", "@CrowdStringsHQ", "@CrowdStringsLab", "@TheCrowdStrings"]},
        ),
        ChannelProfile(
            id="en_kindred_sketch",
            name="Kindred Sketch",
            niche="Attachment styles, relationship psychology, emotional intelligence & communication",
            promise="Make sense of relationship conflicts, attachment wounds, and emotional patterns with empathy.",
            audience="Couples, singles, and friends wanting emotionally mature, communicative relationships",
            persona="Warm relationship counselor friend who validates emotional pain while guiding healthy repair",
            tone="Warm, gentle, emotionally literate, compassionate, grounded in attachment research",
            tone_rules=(
                "Begin with an emotional tension anyone in a relationship recognizes immediately.",
                "Validate both sides without taking sides or assigning blame.",
                "Use physical metaphors like bridges or shields to explain emotional defense.",
                "End with one gentle phrasing shift for constructive communication.",
            ),
            hook_formulas=(
                "Why anxious and avoidant partners always seem to attract each other.",
                "Why the silent treatment hurts the brain like physical pain.",
                "4 subtle signs of emotional burnout in long relationships.",
                "How one simple phrasing shift stops arguments before they escalate.",
            ),
            avoid=("Toxic couple shaming", "Dating manipulation advice", "Armchair relationship diagnosis"),
            short_spec=_short((35, 50), "Has this dynamic ever shown up in your life? Let us know below."),
            long_spec=_long((480, 720), "Discover the full relationship masterclass on Kindred Sketch YouTube."),
            visual=VisualIdentity(
                profile_id="ch_en_pastel_duo",
                label="Minimalist Warm Relational Vector: soft cream canvas, espresso contours, warm rose accent",
                style_description=(
                    "Minimalist flat-vector relational psychology explainer in Vox and Kurzgesagt aesthetic on solid flat soft cream canvas (#FDFBF7). "
                    "Exactly ONE single hero interpersonal metaphor per frame, rendered with clean flat shapes and smooth organic contours "
                    "in deep espresso (#382216) with an emotive warm rose (#E05A67) accent. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Recurring minimal vector couple duo — Leo (tousled dark hair, warm espresso silhouette) and Maya (shoulder-length bob hair, warm rose accent)",
                outfit="Leo in flat sage-mint knit pullover; Maya in flat warm rose (#E05A67) cardigan with clean vector contours",
                palette=("#FDFBF7", "#382216", "#E05A67"),
                thumbnail_rule="Extreme close-up of two expressive minimal figures in emotional tension on flat cream canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("Psych2Go", "YouTube", "long", "Gentle animated relationship breakdowns and attachment insights."),
                ReferenceChannel("Cinema Therapy", "YouTube", "long", "Empathy-first relationship coaching and conflict resolution."),
                ReferenceChannel("Attached by Amir Levine & The Seven Principles by John Gottman", "Book/Scripture", "long", "Foundational empirical relationship science and conflict repair."),
                ReferenceChannel("Psych2Go Shorts", "TikTok/YouTube Shorts", "short", "Gentle relatable relationship queries."),
            ),
            seed_topics=(
                "Why Anxious and Avoidant Partners Always Attract Each Other",
                "Why the Silent Treatment Hurts the Brain Like Physical Pain",
                "4 Subtle Signs of Emotional Burnout in Long Relationships",
                "How One Phrasing Shift Stops Arguments Before They Escalate",
                "Why People Who Grow Up Hyper-Independent Struggle to Ask for Help",
            ),
            hashtags=("#relationships", "#attachmentstyle", "#emotionalintelligence", "#communication", "#couples", "#mentalhealth"),
            monetization=("YouTube AdSense (long)", "Couples communication prompt cards", "Mental health therapy app sponsor"),
            philosophy_id="cognition",
            voice="OmniVoice_EnKindredSketch",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion gentle speech bubble transitions and emotional connection pulses.",
            ),
            engagement=EngagementSpec(
                cta_voice="Empathetic communication guide",
                bridge_templates=(
                    "Watch the complete guide to healthy attachment on Kindred Sketch YouTube.",
                    "See the full 14-minute relationship repair masterclass on our main channel.",
                ),
                close_templates=(
                    "Have you noticed this pattern in your own connections? Share gently below.",
                    "Share this with someone whose bond you cherish and want to understand better.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@KindredSketch", "@KindredSketchHQ", "@KindredDoodle", "@TheKindredSketch"]},
        ),
        ChannelProfile(
            id="en_first_principles",
            name="First Principles Ink",
            niche="Mental models, game theory, logical paradoxes & first-principles decision making",
            promise="Strip complex problems down to fundamental truths so you can think clearly from first principles.",
            audience="Engineers, founders, strategists, and curious analytical problem-solvers",
            persona="Crisp first-principles thinker who breaks down complex logic with visual elegance",
            tone="Sharp, insightful, deductive, rational, structured",
            tone_rules=(
                "Open with a widely accepted assumption that produces an absurd paradox.",
                "Break the premise down to bedrock physical or mathematical truths.",
                "Use clean visual balance scale analogies and physical models rather than abstract math.",
                "End with a practical decision framework for daily evaluation.",
            ),
            hook_formulas=(
                "The Prisoner's Dilemma: why being purely selfish backfires in the long run.",
                "Survivorship bias: the WWII airplane bullet holes everyone misunderstood.",
                "Goodhart's Law: what happens when a measure becomes the target.",
                "Second-order thinking: how great strategists see three moves ahead.",
            ),
            avoid=("Unproven conspiracy models", "Dismissive intellectual arrogance", "Dense mathematical formulas without visual proof"),
            short_spec=_short((35, 50), "Which move would you play in this paradox? Comment your choice."),
            long_spec=_long((480, 720), "Master our next mental model in depth on First Principles Ink."),
            visual=VisualIdentity(
                profile_id="ch_en_first_principles_logic",
                label="Minimalist First-Principles Vector: deep navy canvas, chalk cyan structure, amber gold accent",
                style_description=(
                    "Minimalist flat-vector mental model explainer in Primer and Veritasium aesthetic on solid flat deep navy canvas (#0F172A). "
                    "Exactly ONE single geometric mental model or physical paradox metaphor per frame, rendered with crisp solid shapes "
                    "in chalk cyan (#38BDF8) and a bright amber gold (#F59E0B) focal point. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Minimalist systems thinker in clean profile with horn-rimmed glasses, rendered in crisp chalk-cyan vector linework",
                outfit="Flat white drafting shirt over navy vest with clean geometric contours, zero shading",
                palette=("#0F172A", "#38BDF8", "#F59E0B"),
                thumbnail_rule="Extreme close-up of single geometric paradox balancing on pivot point on flat navy canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("Veritasium", "YouTube", "long", "Deductive scientific reasoning, counter-intuitive paradoxes, and first principles."),
                ReferenceChannel("Primer", "YouTube", "long", "Game theory and evolutionary simulations explained with pure visual models."),
                ReferenceChannel("Farnam Street — The Great Mental Models & The Art of Thinking Clearly", "Book/Scripture", "long", "Latticework of mental models and cognitive fallacy deconstruction."),
                ReferenceChannel("Simulated Logic Shorts", "TikTok/YouTube Shorts", "short", "30-second game theory dilemmas and paradox demonstrations."),
            ),
            seed_topics=(
                "The Prisoner's Dilemma: Why Being Selfish Always Backfires in the Long Run",
                "Survivorship Bias: The WWII Plane Bullet Holes Everyone Misunderstood",
                "Goodhart's Law: What Happens When a Measure Becomes a Target",
                "Second-Order Thinking: How Great Strategists See Three Moves Ahead",
                "The Cobra Effect: Why Well-Intentioned Solutions Make Problems Worse",
            ),
            hashtags=("#mentalmodels", "#gametheory", "#firstprinciples", "#decisionmaking", "#logic", "#strategy"),
            monetization=("YouTube AdSense (long)", "Decision-making mental model templates", "Analytical strategy newsletter"),
            philosophy_id="cognition",
            voice="OmniVoice_EnFirstPrinciples",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion dynamic paradox animations and balance tipping sequences.",
            ),
            engagement=EngagementSpec(
                cta_voice="Rigorous systems thinker",
                bridge_templates=(
                    "Watch the complete first-principles analysis on First Principles Ink YouTube.",
                    "See all five strategic scenarios modeled in full on our YouTube channel.",
                ),
                close_templates=(
                    "How would you resolve this paradox? Share your thought process below.",
                    "Apply second-order thinking to one decision this week and notice what shifts.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@FirstPrinciplesInk", "@FirstPrinciplesHQ", "@FirstPrinciplesLab", "@MentalModelsInk"]},
        ),
        ChannelProfile(
            id="en_wallet_anatomy",
            name="Wallet Anatomy",
            niche="Behavioral personal finance, spending traps, Buy-Now-Pay-Later & everyday economics",
            promise="Dissect everyday spending traps and hidden unit economics so you keep more of what you earn.",
            audience="Young professionals and students navigating consumer traps, credit, and personal wealth",
            persona="Savvy financial older sibling who breaks down money psychology without boring spreadsheets",
            tone="Engaging, practical, eye-opening, direct, grounded in behavioral economics",
            tone_rules=(
                "Hook with an everyday purchase or financial habit that drains money silently.",
                "Break down the actual unit economics or cognitive bias behind the trap.",
                "Never shame modest spending; focus on structural leaks and compounding costs.",
                "End with one painless behavioral adjustment that protects your savings.",
            ),
            hook_formulas=(
                "Why earning more money rarely makes you rich: the Diderot effect explained.",
                "How Buy Now Pay Later quietly rewires your brain's pain receptors.",
                "Why busy coffee shops still go bankrupt: the hidden unit economics.",
                "Lifestyle creep: how quiet upgrades steal your financial freedom.",
            ),
            avoid=("Specific stock picking or crypto speculation", "Get rich quick promises", "Shaming small everyday pleasures"),
            short_spec=_short((35, 50), "Did this spending leak catch you this month? Tell us in the comments."),
            long_spec=_long((480, 720), "Build lasting financial clarity with our full breakdown on Wallet Anatomy."),
            visual=VisualIdentity(
                profile_id="ch_en_ledger_anatomy",
                label="Minimalist Financial Vector: sand ivory canvas, forest emerald subject, crimson alert accent",
                style_description=(
                    "Minimalist flat-vector personal finance explainer in Vox aesthetic on solid flat sand ivory canvas (#FAF8F5). "
                    "Exactly ONE single tangible financial metaphor per frame, rendered with bold clean flat shapes "
                    "in forest emerald (#1B4931) and an alert crimson red (#D9381E) leak accent. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Witty mid-century minimal bookkeeper with neat side-parted hair, round tortoiseshell spectacles, and clean flat vector contours",
                outfit="Flat forest-green vest over ivory shirt with neat navy tie and clean geometric lines",
                palette=("#FAF8F5", "#1B4931", "#D9381E"),
                thumbnail_rule="Extreme close-up of single leaking wallet or coin balance metaphor on flat ivory canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("Two Cents (PBS)", "YouTube", "long", "Approachable, illustrated personal finance and money psychology."),
                ReferenceChannel("The Plain Bagel", "YouTube", "long", "Pragmatic, calm breakdown of financial schemes and unit economics."),
                ReferenceChannel("The Psychology of Money by Morgan Housel", "Book/Scripture", "long", "Behavioral finance, compounding, and wealth preservation mindsets."),
                ReferenceChannel("Humphrey Yang", "YouTube", "short", "Snackable visual financial literacy and hidden fee warnings."),
            ),
            seed_topics=(
                "Why Earning More Money Rarely Makes You Rich (The Diderot Effect Explained)",
                "How Buy Now, Pay Later Quietly Rewires Your Brain's Pain Receptor",
                "Why Busy Coffee Shops Still Go Bankrupt: The Hidden Unit Economics",
                "Lifestyle Creep: How Quiet Upgrades Steal Your Freedom",
                "The Sunk Cost Trap That Keeps You Pouring Money into Bad Choices",
            ),
            hashtags=("#money", "#personalfinance", "#economics", "#financialfreedom", "#budgeting", "#wealth"),
            monetization=("YouTube AdSense (long)", "Personal finance budgeting spreadsheets", "High-yield savings platform sponsorship"),
            philosophy_id="cognition",
            voice="OmniVoice_EnWalletAnatomy",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.4,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion compounding coin bar animations and unit cost breakdown cards.",
            ),
            engagement=EngagementSpec(
                cta_voice="Pragmatic financial guide",
                bridge_templates=(
                    "Watch the complete unit economics breakdown on Wallet Anatomy YouTube channel.",
                    "See all five behavioral money traps explained in full on our YouTube channel.",
                ),
                close_templates=(
                    "Which everyday purchase was your biggest eye-opener? Let us know below.",
                    "Check your recurring subscriptions today and see what you can reclaim.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@WalletAnatomy", "@WalletAnatomyHQ", "@WalletAnatomyLab", "@TheWalletAnatomy"]},
        ),
        ChannelProfile(
            id="en_macro_gears",
            name="Macro Gears",
            niche="Macroeconomics, inflation, central bank interest rates & global supply chains simplified",
            promise="Explain how global economic forces, interest rates, and inflation impact your wallet.",
            audience="Informed citizens, business builders, and curious viewers wanting macroeconomic clarity",
            persona="Clear-headed economic explainer showing how the global economic engine works",
            tone="Objective, clarifying, fascinating, grounded in empirical economic history",
            tone_rules=(
                "Hook with a global economic headline connected straight to everyday living costs.",
                "Trace the transmission mechanism step by step with physical mechanical metaphors.",
                "Remain strictly non-partisan; present trade-offs and unintended consequences.",
                "Summarize the practical takeaway for personal assets and economic resilience.",
            ),
            hook_formulas=(
                "How the economic machine actually works in 12 minutes without the jargon.",
                "Who actually gets poorer first when a central bank prints new money?",
                "Why economic crises make gold prices move so wildly.",
                "The Cantillon Effect: why inflation never hits everyone equally.",
            ),
            avoid=("Political partisan blame games", "Short-term market forecasting", "Abstract dogma without historical data"),
            short_spec=_short((35, 50), "How has inflation touched your area lately? Share your observations below."),
            long_spec=_long((480, 720), "Explore our complete global economy series on Macro Gears."),
            visual=VisualIdentity(
                profile_id="ch_en_swiss_macro",
                label="Minimalist Macroeconomic Vector: salmon cream canvas, navy slate structure, signal orange accent",
                style_description=(
                    "Minimalist flat-vector macroeconomic explainer in Vox Swiss editorial style on solid flat salmon cream canvas (#F7F2EB). "
                    "Exactly ONE single macro monetary metaphor per frame, rendered with clean geometric silhouettes "
                    "in navy slate (#1E293B) and a high-impact signal orange (#EA580C) pivot accent. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Mid-century financial correspondent rendered in clean flat silhouette wearing structured navy suit and orange tie",
                outfit="Solid navy slate (#1E293B) suit with flat white shirt and bold signal orange tie, clean vector edges",
                palette=("#F7F2EB", "#1E293B", "#EA580C"),
                thumbnail_rule="Extreme close-up of single monumental interest rate lever on flat cream canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("Economics Explained", "YouTube", "long", "Global macroeconomic systems, national economies, and currency dynamics."),
                ReferenceChannel("How Money Works", "YouTube", "long", "Clear whiteboard-style explanations of complex economic phenomena."),
                ReferenceChannel("Principles for Dealing with the Changing World Order by Ray Dalio", "YouTube/Book", "long", "Debt cycles, central bank policies, and monetary history."),
                ReferenceChannel("Visual Capitalist Shorts", "YouTube Shorts", "short", "Infographic snapshots of macro trade routes and asset flows."),
            ),
            seed_topics=(
                "How the Economic Machine Actually Works in 12 Minutes (Without the Jargon)",
                "Who Actually Gets Poorer First When a Central Bank Prints New Money?",
                "Why Economic Crises Make Gold Prices Move So Wildly",
                "The Cantillon Effect: Why Inflation Never Hits Everyone Equally",
                "How One Tiny Semiconductor Fab Holds the Global Economy Together",
            ),
            hashtags=("#macroeconomics", "#economy", "#inflation", "#interestrates", "#money", "#geopolitics"),
            monetization=("YouTube AdSense (high RPM)", "Macro economic research briefing sponsor", "Curated economic history books affiliate"),
            philosophy_id="cognition",
            voice="OmniVoice_EnMacroGears",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.4,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion interactive currency flow arrows and interest rate dial animations.",
            ),
            engagement=EngagementSpec(
                cta_voice="Macroeconomic systems analyst",
                bridge_templates=(
                    "Watch the complete 14-minute global economic breakdown on Macro Gears YouTube.",
                    "See the full historical inflation case study on our main YouTube channel.",
                ),
                close_templates=(
                    "What economic signal do you follow closest? Share your thoughts below.",
                    "Track the money flow behind this week's headlines and see the pattern.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@MacroGears", "@MacroGearsHQ", "@MacroGearsLab", "@TheMacroGears"]},
        ),
        ChannelProfile(
            id="en_plain_sight_ai",
            name="Scale & Bone",
            niche="Reptile & amphibian evolution, egg-to-apex life-cycle survival stories & ancient biomechanics",
            promise="Follow the visceral life-cycle of reptiles from leathery egg to apex survivor across 300 million years of evolution.",
            audience="Nature documentary lovers, evolutionary biology fans, and viewers captivated by survival life-cycles",
            persona="Field herpetologist and evolutionary anatomist narrating chronological survival from Day-1 hatchling to apex predator",
            tone="Visceral, chronological, suspenseful, documentary-grade, grounded in evolutionary biomechanics",
            tone_rules=(
                "Open inside the leathery egg or at Day 1 of the hatchling's survival gauntlet within 3 seconds.",
                "Follow a strict chronological life-cycle arc: Egg -> Hatchling Sprint -> Juvenile Molting -> Adult Biomechanics -> Deep-Time Evolution.",
                "Reveal anatomical cross-sections of venom glands, thermal pit organs, or osteoderm bone armor.",
                "End with how this ancient reptile body plan survived mass extinctions that wiped out rival species.",
            ),
            hook_formulas=(
                "From Day 1 to Year 15: how a tiny Komodo hatchling survives a forest of cannibal adults.",
                "Inside the leathery egg: how reptiles broke free from the ocean 310 million years ago.",
                "How snakes lost all four legs and evolved infrared thermal vision instead.",
                "Why the crocodile body plan has barely changed since before the dinosaurs.",
            ),
            avoid=("Plastic 3D CGI monsters", "Dry textbook taxonomy lists without chronological story", "Sensationalized fake creature myths"),
            short_spec=_short((35, 50), "Which stage of this reptile's life cycle amazed you most? Comment below."),
            long_spec=_long((480, 720), "Explore our next evolutionary life-cycle chronicle on Scale & Bone YouTube."),
            visual=VisualIdentity(
                profile_id="ch_en_ai_doodle",
                label="Minimalist TierZoo Wildlife Vector: warm ivory canvas, deep moss creature, terracotta accent",
                style_description=(
                    "Minimalist flat-vector evolutionary biology explainer in TierZoo and BBC Earth aesthetic on solid flat warm ivory canvas (#F5F2EB). "
                    "Exactly ONE single hero creature or anatomical adaptation metaphor per frame, rendered with clean flat shapes "
                    "and smooth organic contours in deep moss green (#2D5A3A) with a vivid terracotta rust (#C85A32) vital accent. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Iconic 2D minimalist naturalist stickman with clean white (#FFFFFF) circle head, field hat, wire arms, and round circle hands",
                outfit="Flat olive safari vest in deep moss green (#2D5A3A) over simple trousers, zero shading, zero gradients",
                palette=("#F5F2EB", "#2D5A3A", "#C85A32"),
                thumbnail_rule="Extreme close-up of single hatching reptile egg or predator silhouette on flat ivory canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("PBS Eons", "YouTube", "long", "Chronological deep-time evolutionary storytelling and fossil biomechanics."),
                ReferenceChannel("TierZoo & Clint's Reptiles", "YouTube", "long", "Engaging herpetology, reptile survival mechanics, and evolutionary trade-offs."),
                ReferenceChannel("Your Inner Fish by Neil Shubin & The Rise and Fall of the Dinosaurs", "Book/Scripture", "long", "Comparative vertebrate anatomy and amniotic egg evolution."),
                ReferenceChannel("Natural History Life-Cycle Shorts", "TikTok/YouTube Shorts", "short", "60-second egg-to-apex reptile survival timelines."),
            ),
            seed_topics=(
                "From Egg to Cannibal Forest: How a Baby Komodo Dragon Survives Its First 5 Years",
                "How Snakes Lost Their Legs—And Evolved Infrared Thermal Pit Organs Instead",
                "Inside the Leathery Egg: How Reptiles Conquered Dry Land 310 Million Years Ago",
                "Why the Crocodile Body Plan Survived Two Mass Extinctions Unchanged",
                "The Biomechanics of a Viper Fang: How a Saliva Gland Turned into a Hypodermic Syringe",
            ),
            hashtags=("#reptiles", "#evolution", "#herpetology", "#lifecycle", "#naturedocumentary", "#biology"),
            monetization=("YouTube AdSense (high documentary RPM)", "Naturalist copperplate reptile field prints", "Wildlife & science documentary sponsorship"),
            philosophy_id="cognition",
            voice="OmniVoice_EnPlainSightAI",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(6, 9),
                estimated_bundle_minutes=(24, 34),
                notes="Remotion chronological Day-1 to Year-15 timeline counters and anatomical cross-section callouts.",
            ),
            engagement=EngagementSpec(
                cta_voice="Field herpetologist narrator",
                bridge_templates=(
                    "Watch the complete Egg-to-Apex reptile survival chronicle on Scale & Bone YouTube.",
                    "See all five evolutionary stages and anatomical cross-sections on our main channel.",
                ),
                close_templates=(
                    "Which reptile adaptation do you find most extraordinary? Tell us in the comments.",
                    "Follow the next 300-million-year survival story in our evolutionary field archive.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={
                "brand_slug": "en_scale_and_bone",
                "handle_candidates": ["@ScaleAndBone", "@ScaleAndBoneHQ", "@ColdBloodCodex", "@ReptileEvolutionLab"],
            },
        ),
        ChannelProfile(
            id="en_career_leverage",
            name="Career Leverage",
            niche="Workplace strategy, salary negotiation, unspoken corporate rules & AI-era career resilience",
            promise="Master unspoken workplace dynamics and build career leverage so your effort actually pays off.",
            audience="Mid-career corporate employees, professionals, and remote workers aiming for advancement",
            persona="Strategic corporate mentor who explains organizational power dynamics candidly",
            tone="Strategic, candid, empowering, realistic, pragmatic",
            tone_rules=(
                "Hook with a painful workplace paradox (e.g. why the hardest worker rarely gets promoted).",
                "Reveal the underlying organizational power dynamic or evaluation bias.",
                "Provide an ethical, actionable tactic to increase visibility and leverage.",
                "End with a clear conversational phrasing script for tough discussions.",
            ),
            hook_formulas=(
                "The Peter Principle: why the hardest worker in the office rarely gets promoted.",
                "3 quiet signs your company is preparing for layoffs and how to prepare.",
                "Why visibility beats raw effort inside large organizations every time.",
                "How to negotiate your salary using anchors without sounding greedy.",
            ),
            avoid=("Toxic workplace sabotage tactics", "Whiny anti-work venting", "Generic resume formatting clichés"),
            short_spec=_short((35, 50), "Have you seen this rule in action at work? Tell us below."),
            long_spec=_long((480, 720), "Gain complete career leverage with our full guide on Career Leverage."),
            visual=VisualIdentity(
                profile_id="ch_en_career_doodle",
                label="Minimalist Career Leverage Vector: light parchment canvas, slate figure, royal gold accent",
                style_description=(
                    "Minimalist flat-vector career strategy explainer in Vox editorial aesthetic on solid flat light parchment canvas (#F8F6F0). "
                    "Exactly ONE single professional leverage metaphor per frame, rendered with clean flat shapes "
                    "in deep slate (#2C3E50) and an elevated royal gold (#E5A93C) fulcrum accent. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Iconic 2D minimalist editorial stickman with clean white (#FFFFFF) circle head, crisp black contours, wire arms, and round circle hands",
                outfit="Flat royal cobalt shirt (#3B82C4) with simple office lanyard, zero digital shading",
                palette=("#F8F6F0", "#2C3E50", "#E5A93C"),
                thumbnail_rule="Extreme close-up of single minimal figure lifting monumental corporate block on flat parchment canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("Harvard Business Review Explainer", "YouTube", "long", "Evidence-based management, leadership, and workplace dynamics."),
                ReferenceChannel("LoewHaley", "YouTube", "short", "Witty, hyper-accurate satire and unwritten rules of corporate office life."),
                ReferenceChannel("The Almanack of Naval Ravikant & So Good They Can't Ignore You by Cal Newport", "Book/Scripture", "long", "Specific knowledge, career capital, and leverage building."),
                ReferenceChannel("Career Shapers", "YouTube Shorts", "short", "Punchy 30-second salary negotiation tactics."),
            ),
            seed_topics=(
                "The Peter Principle: Why the Hardest Worker in the Office Rarely Gets Promoted",
                "3 Quiet Signs Your Company Is Preparing for Layoffs (And How to Prepare)",
                "Why Visibility Beats Raw Effort Inside Large Organizations",
                "How to Negotiate Your Salary Using Anchors Without Sounding Greedy",
                "Specific Knowledge vs Replaceable Busywork in the Age of AI",
            ),
            hashtags=("#career", "#workplace", "#salarynegotiation", "#leadership", "#corporate", "#jobs"),
            monetization=("YouTube AdSense (high RPM)", "Executive career strategy toolkit", "Professional coaching platform sponsorship"),
            philosophy_id="cognition",
            voice="OmniVoice_EnCareerLeverage",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.4,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion salary anchor gauge animations and corporate ladder progress indicators.",
            ),
            engagement=EngagementSpec(
                cta_voice="Strategic workplace advisor",
                bridge_templates=(
                    "Watch the complete salary negotiation masterclass on Career Leverage YouTube.",
                    "See all five workplace power dynamics explained on our main YouTube channel.",
                ),
                close_templates=(
                    "Which workplace rule took you the longest to learn? Share your story below.",
                    "Review your projects this month: are they high visibility or just busywork?",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@CareerLeverage", "@CareerLeverageHQ", "@CareerLeverageLab", "@TheCareerLeverage"]},
        ),
        ChannelProfile(
            id="en_fine_print",
            name="Everyday Fine Print",
            niche="Consumer law literacy, rental & work contracts, hidden fees & subscription dark patterns",
            promise="Read between the lines of contracts and terms of service so you never sign away your rights.",
            audience="Renters, freelance workers, everyday consumers, and subscription users",
            persona="Protective legal literacy ally who translates dense legal legalese into everyday English",
            tone="Vigilant, clear, protective, informative, grounded in consumer protection law",
            tone_rules=(
                "Hook with an everyday contract clause that costs ordinary consumers thousands.",
                "Translate the legal jargon into simple, plain English.",
                "Explain the exact legal distinction (e.g. deposit vs non-refundable fee).",
                "Give one specific clause to look for or ask to amend before signing.",
            ),
            hook_formulas=(
                "The hidden clauses in everyday contracts that cost you thousands every year.",
                "Why security deposit and non-refundable fee mean completely different things.",
                "Subscription dark patterns: how apps make canceling intentionally confusing.",
                "What actually happens legally when someone sends money to the wrong account?",
            ),
            avoid=("Giving individualized legal counsel for pending lawsuits", "Advising illegal evasion of contracts", "Dense academic legal theory"),
            short_spec=_short((35, 50), "Have you ever been trapped by fine print like this? Share below."),
            long_spec=_long((480, 720), "Protect your consumer rights with the full guide on Everyday Fine Print."),
            visual=VisualIdentity(
                profile_id="ch_en_legal_vector",
                label="Minimalist Legal Editorial Vector: newsprint ivory canvas, midnight navy figure, vermilion seal accent",
                style_description=(
                    "Minimalist flat-vector legal investigative explainer in Vox journalistic aesthetic on solid flat newsprint ivory canvas (#F4EFE6). "
                    "Exactly ONE single consumer trap metaphor per frame, rendered with bold crisp shapes "
                    "in midnight navy (#1E293B) and a sharp legal seal vermilion (#E63946) focus accent. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Sharp-witted minimal consumer advocate drawn in bold flat vector silhouette with round spectacles inspecting highlighted clauses",
                outfit="Flat midnight navy blazer with vermilion pocket accent and round spectacles, clean vector edges",
                palette=("#F4EFE6", "#1E293B", "#E63946"),
                thumbnail_rule="Extreme close-up of single oversized magnifying glass exposing trap clause on flat ivory canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("LegalEagle", "YouTube", "long", "Entertaining yet rigorous legal analysis of real-world scenarios."),
                ReferenceChannel("Lehto's Law", "YouTube", "long", "Consumer rights, warranties, and practical contract jurisprudence."),
                ReferenceChannel("FTC Dark Patterns Reports & Consumer Contract Case Studies", "Book/Scripture", "long", "Documented predatory billing structures and deceptive UI cases."),
                ReferenceChannel("Law By Mike", "YouTube Shorts", "short", "Punchy 30-second consumer rights defense scenarios."),
            ),
            seed_topics=(
                "The Hidden Clauses in Everyday Contracts That Cost You Thousands Every Year",
                "Why Security Deposit and Non-Refundable Fee Mean Completely Different Things",
                "Subscription Dark Patterns: How Apps Make Canceling Intentionally Confusing",
                "What Actually Happens Legally When Someone Sends Money to the Wrong Account?",
                "5 Lease Clauses You Should Always Check Before Signing an Apartment Contract",
            ),
            hashtags=("#law", "#consumerrights", "#contracts", "#fineprint", "#legal", "#scams"),
            monetization=("YouTube AdSense (long)", "Contract review checklist toolkit", "Consumer advocacy legal tech partner"),
            philosophy_id="cognition",
            voice="OmniVoice_EnFinePrint",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.4,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion animated red highlight pen and magnifying glass zoom reveals.",
            ),
            engagement=EngagementSpec(
                cta_voice="Consumer protection guide",
                bridge_templates=(
                    "Watch the complete tenant contract breakdown on Everyday Fine Print YouTube.",
                    "See all five hidden contract traps explained on our main YouTube channel.",
                ),
                close_templates=(
                    "Have you ever run into a hidden fee trap? Tell us your experience below.",
                    "Check the terms on your next subscription before clicking accept.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@EverydayFinePrint", "@FinePrintDoodle", "@EverydayFinePrintHQ", "@ReadTheFinePrintLab"]},
        ),
        ChannelProfile(
            id="en_inside_vessel",
            name="Inside the Vessel",
            niche="Human physiology, sleep neuroscience, immune battles & signals from your organs",
            promise="Take a fascinating journey inside your own biology to understand what your organs are telling you.",
            audience="Health-conscious individuals, curious learners, and anyone seeking to understand their body",
            persona="Friendly anatomical explorer who turns human physiology into an epic adventure",
            tone="Curious, awe-inspiring, scientifically grounded, empathetic",
            tone_rules=(
                "Hook with a strange physical sensation everyone feels but few understand.",
                "Zoom inside the cellular or organ level with clear doodle personifications.",
                "Explain the evolutionary survival mechanism behind the body's reaction.",
                "End with one gentle, practical habit to support your physiological system.",
            ),
            hook_formulas=(
                "What happens inside your organs during 24 hours without sleep hour by hour.",
                "Why high stress makes your brain crave sugar uncontrollably.",
                "How your gut microbiome secretly sends mood signals to your brain.",
                "What caffeine actually does to adenosine receptors in your brain.",
            ),
            avoid=("Prescribing medical diagnoses or treatments", "Promoting unproven miracle supplements", "Sensational health fearmongering"),
            short_spec=_short((35, 50), "Has your body sent you this signal lately? Share in the comments."),
            long_spec=_long((480, 720), "Journey deeper into your physiology with Inside the Vessel on YouTube."),
            visual=VisualIdentity(
                profile_id="ch_en_organ_buddies",
                label="Minimalist Physiological Vector: deep cellular navy canvas, arterial crimson organ, electric cyan accent",
                style_description=(
                    "Minimalist flat-vector human physiology explainer in Kurzgesagt aesthetic on solid flat cellular navy canvas (#0A192F). "
                    "Exactly ONE single organ or biological mechanism metaphor per frame, rendered with vibrant solid vector shapes "
                    "in arterial crimson (#EF4444) and an electric bio cyan (#06B6D4) energy pulse accent. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Stylized flat vector anatomical silhouette revealing illuminated heart chamber or brain neural pathway, clean geometric shapes",
                outfit="Translucent flat organic vascular contours with vibrant bio-luminescent accents, zero clothing",
                palette=("#0A192F", "#EF4444", "#06B6D4"),
                thumbnail_rule="Extreme close-up of single glowing heart or brain neuron vessel on flat navy canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("Institute of Human Anatomy", "YouTube", "long", "Fascinating organ-level physiology explained with immense clarity."),
                ReferenceChannel("Kurzgesagt – Immune & Body Series", "YouTube", "long", "Epic microscopic battles between white blood cells, viruses, and bacteria."),
                ReferenceChannel("Why We Sleep by Matthew Walker & The Body by Bill Bryson", "Book/Scripture", "long", "Comprehensive anatomical storytelling and sleep architecture research."),
                ReferenceChannel("Kurzgesagt Shorts", "YouTube Shorts", "short", "60-second cellular and biological animations."),
            ),
            seed_topics=(
                "What Happens Inside Your Organs During 24 Hours Without Sleep (Hour by Hour)",
                "Why High Stress Makes Your Brain Crave Sugar Uncontrollably",
                "How Your Gut Microbiome Secretly Sends Mood Signals to Your Brain",
                "What Caffeine Actually Does to Adenosine Receptors in Your Brain",
                "Why Sitting for 8 Hours Triggers Low-Grade Alarm Signals Across Your Body",
            ),
            hashtags=("#biology", "#physiology", "#health", "#neuroscience", "#sleep", "#humanbody"),
            monetization=("YouTube AdSense (long)", "Sleep & physiology habits tracker", "Ergonomic & health brand sponsorship"),
            philosophy_id="cognition",
            voice="OmniVoice_EnInsideVessel",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.4,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion animated pulse beat lines and cellular magnification transitions.",
            ),
            engagement=EngagementSpec(
                cta_voice="Empathetic biological guide",
                bridge_templates=(
                    "Watch the complete 24-hour sleep cycle breakdown on Inside the Vessel YouTube.",
                    "See all five physiological stress signals explored on our main YouTube channel.",
                ),
                close_templates=(
                    "Has your body given you this warning signal before? Tell us below.",
                    "Give your vessel a restful pause tonight and notice how it responds.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@InsideTheVessel", "@InsideTheVesselHQ", "@InsideVesselLab", "@BodyVesselDoodle"]},
        ),
        ChannelProfile(
            id="en_kitchen_molecules",
            name="Root & Canopy",
            niche="Plant evolution through deep time, seed-to-giant life-cycle time-lapses & botanical warfare",
            promise="Witness the hidden time-lapse warfare of plants—from dormant seed to 2,000-year canopy giant.",
            audience="Nature documentary enthusiasts, botanical science fans, and viewers fascinated by time-lapse life cycles",
            persona="Botanical time-lapse chronicler revealing plants as slow-motion gladiators and chemical engineers",
            tone="Hypnotic, chronological, dramatic, revealing hidden underground and canopy survival battles",
            tone_rules=(
                "Open at Day 0 inside the dormant seed coat or underground root network within 3 seconds.",
                "Use chronological time-lapse progression (Day 1 -> Month 6 -> Year 50 -> Century 10) to reveal plant movement as active warfare.",
                "Show split soil-and-canopy cross-sections of root xylem conduits, mycorrhizal fungal webs, and chemical defense toxins.",
                "End with how this botanical strategy reshaped Earth's atmosphere or forest ecosystems.",
            ),
            hook_formulas=(
                "Year 1 to Year 200: how a strangler fig slowly devours a rainforest giant from the sky down.",
                "Why some pine cones refuse to open until a wildfire burns the forest alive.",
                "The 60-million-year hostage pact between a fig tree and a dying wasp.",
                "How carnivorous pitcher plants lure, drown, and digest prey in acid rainwater.",
            ),
            avoid=("Treating plants as passive static scenery", "Childish cartoon flower faces", "Dry gardening tips without evolutionary storytelling"),
            short_spec=_short((35, 50), "Did you know plants fought this fiercely in slow motion? Comment below."),
            long_spec=_long((480, 720), "Watch the next botanical time-lapse survival story on Root & Canopy YouTube."),
            visual=VisualIdentity(
                profile_id="ch_en_culinary_sticker",
                label="Minimalist Culinary Science Vector: stoneware linen canvas, olive sage subject, flame ochre accent",
                style_description=(
                    "Minimalist flat-vector culinary science explainer in Primer aesthetic on solid flat stoneware linen canvas (#F5EBE1). "
                    "Exactly ONE single molecular cooking metaphor or culinary vessel per frame, rendered with clean flat shapes "
                    "in olive sage (#4A6B53) and an active flame ochre (#D97706) heat accent. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Clean botanical and seed specimen profile rendered in flat vector shapes, tracing growth from split seed coat to green canopy",
                outfit="Natural bark texture and olive foliage flat vector fills, zero human clothing",
                palette=("#F5EBE1", "#4A6B53", "#D97706"),
                thumbnail_rule="Extreme close-up of single searing pan with explosive flavor molecule burst on flat linen canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("BBC Earth — The Green Planet (Sir David Attenborough)", "YouTube", "long", "Time-lapse cinematography framing plant growth as high-stakes predator-prey drama."),
                ReferenceChannel("Crime Pays But Botany Doesn't & PBS Eons", "YouTube", "long", "Evolutionary botany, plant ecology, and deep-time floral history."),
                ReferenceChannel("The Hidden Life of Trees by Peter Wohlleben & Finding the Mother Tree", "Book/Scripture", "long", "Mycorrhizal underground networks and forest survival strategies."),
                ReferenceChannel("Botanical Time-Lapse Shorts", "TikTok/YouTube Shorts", "short", "60-second seed-to-canopy growth and carnivorous plant traps."),
            ),
            seed_topics=(
                "Year 1 to Year 200: How a Strangler Fig Slowly Devours a Rainforest Giant",
                "Why Some Pine Cones Refuse to Open Until a Wildfire Burns the Forest Alive",
                "The 60-Million-Year Hostage Pact Between a Fig Tree and a Dying Wasp",
                "How Carnivorous Pitcher Plants Lure, Drown, and Digest Insects in Acid Rainwater",
                "How Grass Conquered the Planet and Engineered Grazing Mammals",
            ),
            hashtags=("#botany", "#plants", "#timelapse", "#evolution", "#naturedocumentary", "#lifecycle"),
            monetization=("YouTube AdSense (long)", "Archival botanical copperplate herbarium prints", "Nature & science documentary sponsorship"),
            philosophy_id="cognition",
            voice="OmniVoice_EnKitchenMolecules",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion time-lapse Day/Year counters and underground root-growth cross-section reveals.",
            ),
            engagement=EngagementSpec(
                cta_voice="Botanical time-lapse chronicler",
                bridge_templates=(
                    "Watch the complete 200-year botanical time-lapse chronicle on Root & Canopy YouTube.",
                    "See all five stages of underground root warfare on our main YouTube channel.",
                ),
                close_templates=(
                    "Which plant survival strategy surprised you most? Share your thoughts below.",
                    "Look closely at the trees around you tomorrow—an ancient slow-motion battle is unfolding.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={
                "brand_slug": "en_root_and_canopy",
                "handle_candidates": ["@RootAndCanopy", "@RootAndCanopyHQ", "@SilentKingdomBotany", "@BotanicalCodexLab"],
            },
        ),
        ChannelProfile(
            id="en_wait_how",
            name="Spawn to Apex",
            niche="Extreme animal & insect metamorphosis, deep-sea life cycles & parasite survival chronicles",
            promise="Trace nature's most extreme life cycles from microscopic spawn to final metamorphosis.",
            audience="Curious adults, biology lovers, and viewers hooked on bizarre chronological life-cycle transformations",
            persona="Natural history metamorphosis chronicler tracking Day-1 larvae through impossible biological transformations",
            tone="Riveting, chronological, wonder-filled, lucid, documentary-grade biological storytelling",
            tone_rules=(
                "Open at the most fragile or bizarre stage of the creature's life cycle within 3 seconds.",
                "Track every metamorphosis instar chronologically with exact Day/Hour milestones.",
                "Use cutaway lithograph plates to show what happens inside the cocoon, shell, or deep-sea abyss.",
                "End with the evolutionary payoff that makes this extreme life cycle worth the 99% mortality rate.",
            ),
            hook_formulas=(
                "Inside the chrysalis: how a caterpillar completely dissolves into soup and rebuilds its brain.",
                "Why every freshwater eel on Earth swims 4,000 miles to the Sargasso Sea just to die.",
                "Day 1 to Day 17 Years: how periodical cicadas count the seasons underground.",
                "How the immortal jellyfish reverses its own aging process back into a polyp.",
            ),
            avoid=("Childish cartoon mascots", "Clickbait fake biology", "Skipping stages of the chronological life cycle"),
            short_spec=_short((35, 50), "Which stage of this metamorphosis blew your mind? Let us know below."),
            long_spec=_long((480, 720), "Follow our next extreme life-cycle chronicle on Spawn to Apex on YouTube."),
            visual=VisualIdentity(
                profile_id="ch_en_sticker_pop",
                label="Minimalist Mechanism Vector: graphite slate canvas, safety amber gear, stark white accent",
                style_description=(
                    "Minimalist flat-vector mechanical explainer in Primer aesthetic on solid flat graphite slate canvas (#18181B). "
                    "Exactly ONE single ingenious mechanism metaphor per frame, rendered with clean flat geometric silhouettes "
                    "in safety amber (#F59E0B) and high-visibility stark white (#FAFAFA) motion indicators. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Bold geometric metamorphosis stage silhouette framed in clean vector circles, showing egg to mature organism",
                outfit="Natural exoskeleton and amber shell flat vector forms, zero human clothing",
                palette=("#18181B", "#F59E0B", "#FAFAFA"),
                thumbnail_rule="Extreme close-up of single interlocking mechanism puzzle on flat slate canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("Ze Frank & Deep Look (KQED)", "YouTube", "long", "Macro biological storytelling of insect metamorphosis, parasites, and marine life cycles."),
                ReferenceChannel("Deep Look Shorts", "TikTok/YouTube Shorts", "short", "High-retention 45-second close-up metamorphosis and survival hooks."),
                ReferenceChannel("Metamorphosis Insectorum Surinamensium by Maria Sibylla Merian", "Book/Scripture", "long", "Pioneering chronological life-cycle illustration uniting egg, larva, pupa, and host plant."),
                ReferenceChannel("Journey to the Microcosmos", "YouTube", "long", "Poetic, hypnotic narration of microscopic and larval life cycles."),
            ),
            seed_topics=(
                "Inside the Chrysalis: How a Caterpillar Dissolves into Liquid and Rebuilds Its Brain",
                "Why Every Eel on Earth Swims 4,000 Miles to the Sargasso Sea Just to Spawn and Die",
                "17 Years Underground: How Periodical Cicadas Count Tree Sap Cycles in the Dark",
                "The Immortal Jellyfish: How Turritopsis Dohrnii Reverses Its Own Life Cycle",
                "How the Axolotl Refused to Grow Up—And Unlocked Whole-Limb Regeneration",
            ),
            hashtags=("#metamorphosis", "#lifecycle", "#biology", "#nature", "#evolution", "#science"),
            monetization=("YouTube AdSense (long)", "Natural history metamorphosis lithograph prints", "Science & wildlife documentary sponsor"),
            philosophy_id="cognition",
            voice="OmniVoice_EnWaitHow",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion chronological Stage 1-4 metamorphosis wheel and cutaway zoom transitions.",
            ),
            engagement=EngagementSpec(
                cta_voice="Natural history metamorphosis chronicler",
                bridge_templates=(
                    "Watch the complete Egg-to-Apex metamorphosis chronicle on Spawn to Apex YouTube.",
                    "See every larval stage and cellular cutaway in full on our main YouTube channel.",
                ),
                close_templates=(
                    "Which biological transformation amazed you most? Tell us in the comments.",
                    "Join us next time as we trace another impossible life cycle from Day 1.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={
                "brand_slug": "en_spawn_to_apex",
                "handle_candidates": ["@SpawnToApex", "@SpawnToApexHQ", "@MetamorphosisFiles", "@LifeCycleCodex"],
            },
        ),
        ChannelProfile(
            id="en_cold_case_ink",
            name="Cold Case Ink",
            niche="Historical mysteries, vanished expeditions & scientific forensic investigations",
            promise="Re-examine history's greatest unexplained cases through primary documents and modern forensic science.",
            audience="Documentary enthusiasts, mystery solvers, and history lovers wanting rigorous investigations",
            persona="Impartial historical investigator weighing forensic evidence with documentary restraint",
            tone="Investigative, atmospheric, forensic, objective, suspenseful",
            tone_rules=(
                "Open with the verified timeline of the event without sensationalizing rumors.",
                "Establish the geographic isolation and extreme stakes using clean maps.",
                "Examine competing theories against modern scientific and forensic evidence.",
                "Draw a measured conclusion while respecting the unresolved human loss.",
            ),
            hook_formulas=(
                "The Dyatlov Pass incident: how avalanche physics solved the 1959 mystery.",
                "Why did the Mary Celeste crew abandon a perfectly safe ship full of food?",
                "The Flannan Isles lighthouse: what happened to the three keepers in 1900?",
                "The Dancing Plague of 1518: mass hysteria or ergot poisoning?",
            ),
            avoid=("Supernatural or alien sensationalism", "Graphic gore or disrespecting victims", "Unverified conspiracy rumors as fact"),
            short_spec=_short((35, 50), "Which forensic theory makes the most sense to you? Comment below."),
            long_spec=_long((480, 720), "Explore our complete forensic archive on Cold Case Ink on YouTube."),
            visual=VisualIdentity(
                profile_id="ch_en_forensic_noir",
                label="Minimalist Forensic Noir Vector: pitch black canvas, dossier white silhouette, evidence crimson accent",
                style_description=(
                    "Minimalist flat-vector forensic mystery explainer in Vox noir aesthetic on solid flat pitch black canvas (#0B0F19). "
                    "Exactly ONE single crucial evidence metaphor per frame, rendered with high-contrast flat silhouettes "
                    "in stark dossier white (#F1F5F9) and a single glowing evidence crimson (#E11D48) point. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Shadowy faceless trench-coat detective silhouette in fedora hat holding lantern beam over red-tagged clue",
                outfit="Solid flat dark slate trench coat with turned-up collar and fedora silhouette, zero shading",
                palette=("#0B0F19", "#F1F5F9", "#E11D48"),
                thumbnail_rule="Extreme close-up of single trench-coat silhouette beam striking single red evidence key on flat dark canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("Lemmino", "YouTube", "long", "Peerless documentary pacing, forensic neutrality, and primary-source rigor."),
                ReferenceChannel("Brew", "YouTube", "long", "Compelling storytelling of historical survivals and unexplained events."),
                ReferenceChannel("ETH Zurich Dyatlov Avalanche Study & Smithsonian Historical Archives", "Book/Scripture", "long", "Scientific forensic reconstruction and empirical records."),
                ReferenceChannel("Documentary Shorts", "YouTube Shorts", "short", "Atmospheric 50-second historical enigma spotlights."),
            ),
            seed_topics=(
                "The Dyatlov Pass Incident: How Avalanche Physics Solved the 1959 Mystery",
                "Why Did the Mary Celeste Crew Abandon a Perfectly Safe Ship Full of Food?",
                "The Flannan Isles Lighthouse: What Happened to the Three Keepers in 1900?",
                "The Dancing Plague of 1518: Mass Hysteria or Ergot Poisoning?",
                "The Tunguska Event: How an Airburst Flattened 800 Square Miles Without a Crater",
            ),
            hashtags=("#history", "#coldcase", "#documentary", "#mystery", "#forensics", "#investigation"),
            monetization=("YouTube AdSense (long)", "Historical map & investigative dossier prints", "Audiobook & documentary streaming partner"),
            philosophy_id="cognition",
            voice="OmniVoice_EnColdCaseInk",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion documentary photo zoom and timestamp typewriter transitions.",
            ),
            engagement=EngagementSpec(
                cta_voice="Forensic history narrator",
                bridge_templates=(
                    "Watch the complete documentary investigation on Cold Case Ink YouTube.",
                    "See all primary source documents and timeline charts on our main channel.",
                ),
                close_templates=(
                    "Which forensic clue stands out to you most? Share your deduction below.",
                    "Subscribe to join our next investigative case deep-dive into history.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@ColdCaseInk", "@ColdCaseInkHQ", "@ColdCaseDoodle", "@UnsolvedInkLab"]},
        ),
        ChannelProfile(
            id="en_choke_point",
            name="Choke Point Maps",
            niche="Geopolitics, maritime choke points, resource geography & pivotal historical turning points",
            promise="Trace the narrow straits, canals, and geography that dictate world trade, power, and conflict.",
            audience="Geopolitics enthusiasts, history buffs, and global affairs observers",
            persona="Strategic cartographer connecting global news directly to physical geography",
            tone="Strategic, panoramic, authoritative, clear, illuminating",
            tone_rules=(
                "Hook with a single narrow geographical bottleneck that controls global commodity prices.",
                "Use flat 2D maps to illustrate why countries have fought over this geography for centuries.",
                "Connect the historical pattern directly to modern maritime and trade headlines.",
                "End with a strategic summary of what happens if that bottleneck closes.",
            ),
            hook_formulas=(
                "Why one narrow strait controls the price of everything you buy.",
                "Why commercial planes almost never fly directly over the Tibetan plateau.",
                "How geography turned Panama and Suez into global bottlenecks.",
                "Why Russia's warm-water port obsession explains centuries of history.",
            ),
            avoid=("One-sided political propaganda", "Sensationalized ungrounded war predictions", "Nationalistic jingoism"),
            short_spec=_short((35, 50), "Did you realize this strait carried so much trade? Share below."),
            long_spec=_long((480, 720), "Explore our full geopolitical map library on Choke Point Maps."),
            visual=VisualIdentity(
                profile_id="ch_en_tactical_atlas",
                label="Minimalist Geopolitical Vector: maritime navy canvas, coastal sand landmass, blockade crimson accent",
                style_description=(
                    "Minimalist flat-vector strategic geography explainer in Vox and Johnny Harris cartographic aesthetic on solid flat maritime navy canvas (#0F172A). "
                    "Exactly ONE single pivotal choke point strait or maritime vessel metaphor per frame, rendered with clean flat land contours "
                    "in coastal sand ivory (#E2E8F0) and a single bold blockade crimson (#DC2626) vector. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Character-free strategic cartography emblem: 2D flat container ship silhouette and glowing blockade vector, zero human figures",
                outfit="Zero human clothing; clean vector maritime route indicators",
                palette=("#0F172A", "#E2E8F0", "#DC2626"),
                thumbnail_rule="Extreme close-up of single container ship entering glowing red blockade strait on flat navy canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("RealLifeLore", "YouTube", "long", "Global geographic analysis of strategic straits, logistics, and resource constraints."),
                ReferenceChannel("Map Men & Historia Civilis", "YouTube", "long", "Witty cartographic breakdowns and strategic military maneuver maps."),
                ReferenceChannel("Prisoners of Geography by Tim Marshall", "Book/Scripture", "long", "Foundational geopolitical analysis of mountains, rivers, and choke points."),
                ReferenceChannel("RealLifeLore Shorts", "YouTube Shorts", "short", "60-second geographic trivia and bottleneck snapshots."),
            ),
            seed_topics=(
                "Why One Narrow Strait Controls the Price of Everything You Buy",
                "Why Commercial Planes Almost Never Fly Directly Over the Tibetan Plateau",
                "How Geography Turned Panama and Suez into Global Bottlenecks",
                "Why Russia's Warm-Water Port Obsession Explains Centuries of History",
                "How River Systems Quietly Decided Which Civilizations Became Superpowers",
            ),
            hashtags=("#geopolitics", "#maps", "#geography", "#trade", "#history", "#worldaffairs"),
            monetization=("YouTube AdSense (high RPM)", "Strategic geopolitical map prints", "Global affairs newsletter sponsorship"),
            philosophy_id="cognition",
            voice="OmniVoice_EnChokePoint",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion animated maritime route lines and choke point zoom reveals.",
            ),
            engagement=EngagementSpec(
                cta_voice="Strategic global geographer",
                bridge_templates=(
                    "Watch the complete strategic strait breakdown on Choke Point Maps YouTube.",
                    "See all five global geographic bottlenecks analyzed in full on our YouTube channel.",
                ),
                close_templates=(
                    "Which geographic bottleneck surprised you most? Share your perspective below.",
                    "Trace the shipping route behind your favorite product and spot the choke point.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@ChokePointMaps", "@ChokePointMapsHQ", "@ChokePointInk", "@StrategicMapsLab"]},
        ),
        ChannelProfile(
            id="en_pocket_cosmos",
            name="Pocket Cosmos",
            niche="Astrophysics, black holes, quantum paradoxes & spacetime explained in Feynman style",
            promise="Explain mind-bending astrophysics and spacetime paradoxes using everyday analogies and gentle stick figures.",
            audience="Space lovers, students, science fiction thinkers, and curious cosmologists",
            persona="Enthusiastic Feynman-style cosmic companion bringing relativistic physics down to Earth",
            tone="Awe-inspiring, lucid, poetic yet rigorous, Feynman-esque",
            tone_rules=(
                "Hook with a cosmic thought experiment that breaks common sense completely.",
                "Use clean stick figures and everyday physical props like clocks or rubber sheets.",
                "Explain the relativistic math intuitively without intimidating equations.",
                "End with a breathtaking existential realization about our place in the cosmos.",
            ),
            hook_formulas=(
                "If the Sun disappeared right now, how long would Earth actually survive?",
                "Why one hour near a black hole equals seven years on Earth.",
                "Fermi's paradox: where is everybody in a galaxy of billions of stars?",
                "Quantum entanglement explained without mysticism or jargon.",
            ),
            avoid=("Sci-fi fantasy masquerading as real physics", "Overly mystical spiritual claims", "Dry tensor mathematics without physical intuition"),
            short_spec=_short((35, 50), "Does the scale of the cosmos blow your mind? Tell us below."),
            long_spec=_long((480, 720), "Journey through the wonders of spacetime with Pocket Cosmos on YouTube."),
            visual=VisualIdentity(
                profile_id="ch_en_cosmos_vector",
                label="Minimalist Cosmic Vector: void black canvas, electric nebula cyan body, solar flare gold accent",
                style_description=(
                    "Minimalist flat-vector astrophysics explainer in Kurzgesagt aesthetic on solid flat void black canvas (#050814). "
                    "Exactly ONE single celestial body or gravitational spacetime metaphor per frame, rendered with vibrant flat geometric silhouettes "
                    "in electric nebula cyan (#38BDF8) and a glowing solar flare gold (#FBBF24) event accent. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Clean geometric celestial sphere with vibrant planetary orbital ring and golden focal star, zero human figures",
                outfit="Flat geometric vector orbits, no clothing",
                palette=("#050814", "#38BDF8", "#FBBF24"),
                thumbnail_rule="Extreme close-up of single glowing celestial event horizon on flat void black canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("Kurzgesagt – Space Series", "YouTube", "long", "Cosmic scale, existential risks, and theoretical astrophysics visualized."),
                ReferenceChannel("ScienceClic English & Up and Atom", "YouTube", "long", "Relativistic spacetime physics and quantum mechanics rendered intuitively."),
                ReferenceChannel("Six Easy Pieces by Richard Feynman", "Book/Scripture", "long", "Masterful reduction of fundamental physics to everyday analogies."),
                ReferenceChannel("Astronomy Shorts", "YouTube Shorts", "short", "60-second cosmic scale comparisons and black hole facts."),
            ),
            seed_topics=(
                "If the Sun Disappeared Right Now, How Long Would Earth Actually Survive?",
                "Why One Hour Near a Black Hole Equals Seven Years on Earth",
                "Fermi's Paradox: Where Is Everybody in a Galaxy of Billions of Stars?",
                "Quantum Entanglement Explained Without Mysticism or Jargon",
                "What Actually Happens If You Cross the Event Horizon of a Supermassive Black Hole?",
            ),
            hashtags=("#space", "#astrophysics", "#cosmos", "#physics", "#blackhole", "#science"),
            monetization=("YouTube AdSense (long)", "Illustrated cosmic infographic prints", "Space exploration & science app sponsorship"),
            philosophy_id="cognition",
            voice="OmniVoice_EnPocketCosmos",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion spacetime curvature mesh animations and relativistic clock warp effects.",
            ),
            engagement=EngagementSpec(
                cta_voice="Cosmic wonder guide",
                bridge_templates=(
                    "Watch the complete spacetime relativity breakdown on Pocket Cosmos YouTube.",
                    "See all five cosmic paradoxes animated in full on our main YouTube channel.",
                ),
                close_templates=(
                    "Which cosmic mystery fascinates you most? Share your thoughts below.",
                    "Step outside tonight, look up at the stars, and remember your connection to it all.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@PocketCosmos", "@PocketCosmosHQ", "@PocketCosmosLab", "@TinyCosmosInk"]},
        ),
        ChannelProfile(
            id="en_second_arrow",
            name="The Second Arrow",
            niche="Secular & classical Buddhist psychology, Zen parables, mindfulness & letting go",
            promise="Learn to drop the second arrow of mental suffering through timeless Zen parables and mindfulness.",
            audience="Overthinkers, seekers of calm, and anyone navigating stress, grief, or emotional turbulence",
            persona="Gentle Zen companion sharing timeless parables with stillness and warmth",
            tone="Tranquil, poetic, calming, compassionate, grounded in early Buddhist psychology",
            tone_rules=(
                "Open with an everyday moment of overthinking or emotional tension.",
                "Introduce a classic Buddhist or Zen parable naturally (e.g. empty boat, second arrow).",
                "Distinguish clean physical pain from the optional mental suffering created by our stories.",
                "End with a peaceful breathing cue and a compassionate takeaway for the evening.",
            ),
            hook_formulas=(
                "The parable of the second arrow: why pain is inevitable, but suffering is optional.",
                "The empty boat story: how to stop taking everything personally.",
                "Thich Nhat Hanh on anger: how to hold difficult emotions without exploding.",
                "Impermanence explained: why accepting change dissolves anxiety.",
            ),
            avoid=("Dogmatic religious preaching", "Promoting superstitious rituals", "Toxic positivity or invalidating real grief"),
            short_spec=_short((35, 50), "Can you feel yourself dropping the second arrow tonight? Share below."),
            long_spec=_long((480, 720), "Find deep peace with our full mindful series on The Second Arrow."),
            visual=VisualIdentity(
                profile_id="ch_en_zen_sumie",
                label="Minimalist Zen Vector: rice paper cream canvas, sumi ink figure, lotus vermilion accent",
                style_description=(
                    "Minimalist flat-vector mindfulness explainer in modern Zen aesthetic on solid flat rice paper cream canvas (#F7F4EB). "
                    "Exactly ONE single meditative psychology metaphor per frame, rendered with serene bold flat shapes "
                    "in deep sumi ink (#1E293B) and a single lotus vermilion (#E0564C) deflection accent. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Serene seated meditator in clean flat sumi silhouette beside minimal lotus flower and calm circular ripple",
                outfit="Simple dark sumi-ink robe silhouette with clean flowing vector contours",
                palette=("#F7F4EB", "#1E293B", "#E0564C"),
                thumbnail_rule="Extreme close-up of single serene seated figure deflecting a single arrow on flat cream canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("Plum Village", "YouTube", "long", "Teachings of Thich Nhat Hanh on deep listening, anger transformation, and presence."),
                ReferenceChannel("Doug's Dharma", "YouTube", "long", "Early Buddhist philosophical scholarship grounded in secular life."),
                ReferenceChannel("Einzelgänger — Buddhism & Zen", "YouTube", "long", "Stoic and Zen allegories for modern mental peace."),
                ReferenceChannel("Mindful Shorts", "YouTube Shorts", "short", "60-second breathing cues and parables."),
            ),
            seed_topics=(
                "The Parable of the Second Arrow: Why Pain Is Inevitable, But Suffering Is Optional",
                "The Empty Boat Story: How to Stop Taking Everything Personally",
                "Thich Nhat Hanh on Anger: How to Hold Difficult Emotions Without Exploding",
                "Impermanence Explained: Why Accepting Change Dissolves Anxiety",
                "Why Overthinking Past Mistakes Feeds the Illusion of Control",
            ),
            hashtags=("#mindfulness", "#zen", "#buddhism", "#peace", "#meditation", "#mentalhealth"),
            monetization=("YouTube AdSense (long)", "Mindful meditation journal & chime", "Mindfulness & calm sleep app sponsorship"),
            philosophy_id="cognition",
            voice="OmniVoice_EnSecondArrow",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion gentle breathing circle pulses and calm water ripple effects.",
            ),
            engagement=EngagementSpec(
                cta_voice="Mindful meditation companion",
                bridge_templates=(
                    "Watch the complete second arrow meditation story on The Second Arrow YouTube.",
                    "See the full 15-minute parable and guided reflection on our main YouTube channel.",
                ),
                close_templates=(
                    "Take three slow breaths tonight and release what is outside your control.",
                    "May you sleep deeply and meet tomorrow with a peaceful, open heart.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@TheSecondArrowZen", "@SecondArrowDoodle", "@SecondArrowMind", "@TheSecondArrowLab"]},
        ),
        ChannelProfile(
            id="en_parable_lamp",
            name="Deep Time Strata",
            niche="Paleo-evolutionary turning points, geological strata epochs, mass extinctions & ancient ecosystems",
            promise="Excavate Earth's geological strata to witness how life survived five mass extinctions and conquered dry land.",
            audience="Paleontology enthusiasts, deep-time history fans, and viewers captivated by ancient Earth ecosystems",
            persona="Deep-time paleontologist narrating Earth's ancient ecosystems and evolutionary bottlenecks layer by rock layer",
            tone="Epic, investigative, chronological, grounded in paleontology and geological stratigraphy",
            tone_rules=(
                "Open at a specific geological boundary layer (e.g. 252 million years ago during the Great Dying) within 3 seconds.",
                "Unpack the chain reaction across ocean chemistry, atmosphere, and ancient reptiles/flora chronologically.",
                "Use carved rock-strata cross-sections and fossil specimen plates to show what vanished and what adapted.",
                "End with how that ancient evolutionary bottleneck shaped the anatomy of living creatures today.",
            ),
            hook_formulas=(
                "When giant 100-foot fungi ruled the Earth before trees even evolved.",
                "The Great Dying: how a tiny burrowing synapsid survived the worst extinction in Earth's history.",
                "Why Evolution keeps turning completely unrelated animals into crabs (Carcinisation).",
                "How a 60-million-year gap without wood-eating microbes created all the coal on Earth.",
            ),
            avoid=("Hollywood movie monster clichés", "Creationist or pseudoscientific timelines", "Dry mineral lists without survival drama"),
            short_spec=_short((35, 50), "Which prehistoric epoch would you be most terrified to visit? Comment below."),
            long_spec=_long((480, 720), "Excavate our next deep-time geological chronicle on Deep Time Strata on YouTube."),
            visual=VisualIdentity(
                profile_id="ch_en_deep_strata_vector",
                label="Minimalist Deep Time Vector: fossil ivory canvas, earth slate specimen, amber gold accent",
                style_description=(
                    "Minimalist flat-vector deep time evolutionary explainer in TierZoo aesthetic on solid flat fossil ivory canvas (#F5EFE6). "
                    "Exactly ONE single ancient creature silhouette or geological turning-point metaphor per frame, rendered with bold clean flat shapes "
                    "in earth slate (#292524) and a radiant fossil amber gold (#D97706) vital spark accent. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Expedition paleontologist in flat vector silhouette holding a field lantern near ancient fossil tracks",
                outfit="Flat earth-slate canvas field jacket and satchel, clean vector lines",
                palette=("#F5EFE6", "#292524", "#D97706"),
                thumbnail_rule="Extreme close-up of single fossilized amber specimen or giant predator skull silhouette on flat ivory canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("PBS Eons & Moth Light Media", "YouTube", "long", "Deep-time paleontology, obscure evolutionary lineages, and mass extinction reconstructions."),
                ReferenceChannel("History of the Earth", "YouTube", "long", "Chronological epoch-by-epoch documentary storytelling of ancient biospheres."),
                ReferenceChannel("The Ends of the World by Peter Brannen & Annals of the Former World", "Book/Scripture", "long", "Geological stratigraphy and the five mass extinctions."),
                ReferenceChannel("PBS Eons Shorts", "YouTube Shorts", "short", "60-second fossil mysteries and deep-time evolutionary twists."),
            ),
            seed_topics=(
                "When Giant 30-Foot Fungi Ruled the Continents Before Trees Evolved",
                "The Great Dying: How One Burrowing Creature Survived the Permian Extinction",
                "Why Evolution Keeps Turning Unrelated Crustaceans into Crabs (Carcinisation)",
                "How the Carboniferous Forest Fire Era Created Earth's Coal Seams",
                "How the First Tetrapods Crawled Out of Devonian Mud onto Dry Land",
            ),
            hashtags=("#paleontology", "#deeptime", "#evolution", "#geology", "#fossils", "#prehistoric"),
            monetization=("YouTube AdSense (long)", "Carved geological strata & fossil timeline prints", "Natural history museum & science sponsor"),
            philosophy_id="cognition",
            voice="OmniVoice_EnParableLamp",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion Million-Year geological depth counter and rock-strata scroll transitions.",
            ),
            engagement=EngagementSpec(
                cta_voice="Deep-time paleontologist",
                bridge_templates=(
                    "Watch the complete Permian extinction chronicle on Deep Time Strata YouTube.",
                    "See all five geological epochs excavated in full on our main YouTube channel.",
                ),
                close_templates=(
                    "Which ancient evolutionary survivor fascinated you most? Share below.",
                    "Every rock layer beneath your feet holds an entire lost world. See you in the next epoch.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={
                "brand_slug": "en_deep_time_strata",
                "handle_candidates": ["@DeepTimeStrata", "@DeepTimeStrataHQ", "@PaleoStrataCodex", "@TheDeepTimeStrata"],
            },
        ),
        ChannelProfile(
            id="en_bamboo_marble",
            name="Bamboo & Marble",
            niche="Stoicism meets Taoism: Marcus Aurelius, Lao Tzu, mindful night fables & inner calm",
            promise="Bridge Western Stoic strength with Eastern Taoist non-forcing for unshakeable inner peace.",
            audience="Nighttime thinkers, busy professionals, and seekers of stillness before sleep",
            persona="Quiet evening philosopher blending ancient wisdom into soothing bedtime reflections",
            tone="Soothing, reflective, philosophical, grounded, poetic",
            tone_rules=(
                "Open with a quiet evening scene inviting the viewer to set aside daily anxiety.",
                "Blend a Stoic principle of fortitude with a Taoist principle of non-forcing (Wu Wei).",
                "Use concrete parables like cracked jars, bamboo stalks, or marble columns.",
                "Conclude with a peaceful goodnight blessing and invitation to rest.",
            ),
            hook_formulas=(
                "Lao Tzu's philosophy of Wu Wei: why forcing your life only makes it fall apart.",
                "Socrates' three sieves: the 10-second rule before rumors ruin your peace.",
                "The Chinese farmer parable: why bad luck today might save you tomorrow.",
                "How Marcus Aurelius stayed calm surrounded by betrayal and chaos.",
            ),
            avoid=("Harsh lecturing tones", "Cynical nihilism", "Complex academic philosophy without practical heart"),
            short_spec=_short((35, 50), "Let this thought bring stillness to your night. Rest well."),
            long_spec=_long((480, 720), "Unwind completely with our full nighttime philosophical fable on Bamboo & Marble."),
            visual=VisualIdentity(
                profile_id="ch_en_twilight_stoic",
                label="Minimalist Nocturnal Philosophy Vector: midnight slate canvas, marble ivory silhouette, lantern gold accent",
                style_description=(
                    "Minimalist flat-vector philosophical explainer in tranquil nocturnal aesthetic on solid flat midnight slate canvas (#0F172A). "
                    "Exactly ONE single contemplative metaphor per frame, rendered with serene flat shapes "
                    "in pale marble ivory (#E2E8F0) and a gentle lantern gold (#F59E0B) crescent accent. "
                    "Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter."
                ),
                cast_appearance="Calm philosopher traveler silhouette in draped ivory cloak standing peacefully under a golden crescent moon",
                outfit="Flowing flat marble-ivory cloak with clean minimal contours",
                palette=("#0F172A", "#E2E8F0", "#F59E0B"),
                thumbnail_rule="Extreme close-up of single philosopher traveler silhouette gazing at golden crescent moon on flat midnight canvas + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("Einzelgänger — Stoicism & Taoism", "YouTube", "long", "Harmonizing Western Stoic virtue with Eastern Taoist non-striving."),
                ReferenceChannel("Daily Stoic", "YouTube", "long", "Practical dichotomy of control, Amor Fati, and evening reflection."),
                ReferenceChannel("Dare to do. Motivation", "YouTube", "long", "Evening parable stories for inner stillness and restful sleep."),
                ReferenceChannel("Daily Stoic Shorts", "TikTok/YouTube Shorts", "short", "60-second Stoic mindset reflections."),
            ),
            seed_topics=(
                "Lao Tzu's Philosophy of Wu Wei: Why Forcing Your Life Only Makes It Fall Apart",
                "Socrates' Three Sieves: The 10-Second Rule Before Rumors Ruin Your Peace",
                "The Chinese Farmer Parable: Why Bad Luck Today Might Save You Tomorrow",
                "How Marcus Aurelius Stayed Calm Surrounded by Betrayal and Chaos",
                "The Cracked Water Jar: A Quiet Night Story About Imperfection",
            ),
            hashtags=("#stoicism", "#taoism", "#philosophy", "#mindset", "#innerpeace", "#wisdom"),
            monetization=("YouTube AdSense (long)", "Mindful evening journal & herbal tea curation", "Meditation & sleep app sponsorship"),
            philosophy_id="cognition",
            voice="OmniVoice_EnBambooMarble",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.45,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(28, 38),
                notes="Remotion gentle moonlight float and bamboo sway transitions.",
            ),
            engagement=EngagementSpec(
                cta_voice="Quiet evening philosopher",
                bridge_templates=(
                    "Watch the complete nighttime fable and relaxing background on Bamboo & Marble YouTube.",
                    "See all five lessons on Stoic calm and Wu Wei on our main YouTube channel.",
                ),
                close_templates=(
                    "Wishing you a peaceful and rejuvenating night of rest. See you tomorrow evening.",
                    "Release today's burdens into the quiet night. Rest well and be at peace.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@BambooAndMarble", "@BambooAndMarbleHQ", "@BambooMarbleInk", "@StoicAndTaoLab"]},
        ),
    )


_CHANNELS: Optional[Dict[str, ChannelProfile]] = None


def channels() -> Dict[str, ChannelProfile]:
    """Return all channel profiles keyed by id (lazy, so visual_style loads once)."""
    global _CHANNELS
    if _CHANNELS is None:
        _CHANNELS = {c.id: c for c in _build_channels()}
    return _CHANNELS


def channel_ids() -> List[str]:
    return list(channels())


def get_channel(channel_id: str) -> ChannelProfile:
    key = (channel_id or "").strip()
    norm_key = key.replace("-", "_")
    resolved_key = CHANNEL_ALIASES.get(key, CHANNEL_ALIASES.get(norm_key, norm_key))
    found = channels().get(resolved_key) or channels().get(key)
    if found is None:
        raise ValueError(f"Unknown channel '{key}'. Allowed: {sorted(channels())}")
    return found


def get_channel_description(channel_id: str) -> str:
    """Return rich, niche-specific, SEO-optimized description (150-350 chars) for a channel."""
    key = (channel_id or "").strip()
    norm_key = key.replace("-", "_")
    resolved_key = CHANNEL_ALIASES.get(key, CHANNEL_ALIASES.get(norm_key, norm_key))
    if resolved_key in CHANNEL_DESCRIPTIONS:
        return CHANNEL_DESCRIPTIONS[resolved_key]
    try:
        ch = get_channel(key)
        return ch.description or CHANNEL_DESCRIPTIONS.get(ch.id, "")
    except Exception:
        return CHANNEL_DESCRIPTIONS.get(key, "")


def channel_for_style(style: Optional[str]) -> Optional[ChannelProfile]:
    """Find the channel whose non-default visual identity owns ``style`` verbatim."""
    if not style:
        return None
    for ch in channels().values():
        if ch.visual.profile_id.startswith(CHANNEL_STYLE_PREFIX) and ch.visual.style_description == style:
            return ch
    return None


ARCHETYPE_MAP: Dict[str, Dict[str, str]] = {
    # 1. stickman_doodle (6 channels)
    "nao_luoi": {"id": "stickman_doodle", "label": "1. Indie Doodle Stickman"},
    "ai_binh_dan": {"id": "stickman_doodle", "label": "1. Indie Doodle Stickman"},
    "nghe_song_sot": {"id": "stickman_doodle", "label": "1. Indie Doodle Stickman"},
    "en_lazy_brain": {"id": "stickman_doodle", "label": "1. Indie Doodle Stickman"},
    "en_plain_sight_ai": {"id": "stickman_doodle", "label": "1. Indie Doodle Stickman"},
    "en_career_leverage": {"id": "stickman_doodle", "label": "1. Indie Doodle Stickman"},
    # 2. noir_dossier (4 channels)
    "ho_so_ky_la": {"id": "noir_dossier", "label": "2. 2D Noir & Red-String Dossier"},
    "luat_ngam": {"id": "noir_dossier", "label": "2. 2D Noir & Red-String Dossier"},
    "en_crowd_strings": {"id": "noir_dossier", "label": "2. 2D Noir & Red-String Dossier"},
    "en_cold_case_ink": {"id": "noir_dossier", "label": "2. 2D Noir & Red-String Dossier"},
    # 3. kawaii_sticker (6 channels)
    "ua_sao_vay": {"id": "kawaii_sticker", "label": "3. Kawaii Mascots & Sticker-Pop"},
    "co_the_ke": {"id": "kawaii_sticker", "label": "3. Kawaii Mascots & Sticker-Pop"},
    "dia_com": {"id": "kawaii_sticker", "label": "3. Kawaii Mascots & Sticker-Pop"},
    "en_inside_vessel": {"id": "kawaii_sticker", "label": "3. Kawaii Mascots & Sticker-Pop"},
    "en_kitchen_molecules": {"id": "kawaii_sticker", "label": "3. Kawaii Mascots & Sticker-Pop"},
    "en_wait_how": {"id": "kawaii_sticker", "label": "3. Kawaii Mascots & Sticker-Pop"},
    # 4. pastel_duo (2 channels)
    "thuong_cho_kheo": {"id": "pastel_duo", "label": "4. Pastel Warm-Line Duo"},
    "en_kindred_sketch": {"id": "pastel_duo", "label": "4. Pastel Warm-Line Duo"},
    # 5. tactical_atlas (2 channels)
    "ban_do_quyen_luc": {"id": "tactical_atlas", "label": "5. 2D Tactical Cartography (Maps)"},
    "en_choke_point": {"id": "tactical_atlas", "label": "5. 2D Tactical Cartography (Maps)"},
    # 6. cosmos_vector (2 channels)
    "vu_tru_ti_hon": {"id": "cosmos_vector", "label": "6. Deep-Space Geometric Vector"},
    "en_pocket_cosmos": {"id": "cosmos_vector", "label": "6. Deep-Space Geometric Vector"},
    # 7. blueprint_ledger (6 channels)
    "tui_tien": {"id": "blueprint_ledger", "label": "7. Ledger, Blueprint & Swiss Infographic"},
    "banh_rang": {"id": "blueprint_ledger", "label": "7. Ledger, Blueprint & Swiss Infographic"},
    "la_ban_hoc_thuat": {"id": "blueprint_ledger", "label": "7. Ledger, Blueprint & Swiss Infographic"},
    "en_first_principles": {"id": "blueprint_ledger", "label": "7. Ledger, Blueprint & Swiss Infographic"},
    "en_wallet_anatomy": {"id": "blueprint_ledger", "label": "7. Ledger, Blueprint & Swiss Infographic"},
    "en_macro_gears": {"id": "blueprint_ledger", "label": "7. Ledger, Blueprint & Swiss Infographic"},
    # 8. editorial_risograph (2 channels)
    "luat_doi_thuong": {"id": "editorial_risograph", "label": "8. Editorial Risograph Print"},
    "en_fine_print": {"id": "editorial_risograph", "label": "8. Editorial Risograph Print"},
    # 9. zen_sumie (3 channels)
    "chanh_niem_ke": {"id": "zen_sumie", "label": "9. Sumi-e Zen Ink Wash"},
    "minh_triet_song": {"id": "zen_sumie", "label": "9. Sumi-e Zen Ink Wash"},
    "en_second_arrow": {"id": "zen_sumie", "label": "9. Sumi-e Zen Ink Wash"},
    # 10. woodcut_gouache (5 channels)
    "su_ke_lai": {"id": "woodcut_gouache", "label": "10. Woodblock Print & Night Gouache"},
    "loi_sang_soi": {"id": "woodcut_gouache", "label": "10. Woodblock Print & Night Gouache"},
    "tam_tinh_dem": {"id": "woodcut_gouache", "label": "10. Woodblock Print & Night Gouache"},
    "en_parable_lamp": {"id": "woodcut_gouache", "label": "10. Woodblock Print & Night Gouache"},
    "en_bamboo_marble": {"id": "woodcut_gouache", "label": "10. Woodblock Print & Night Gouache"},
}


def get_visual_archetype(channel_id: str) -> Dict[str, str]:
    """Return canonical 10-Archetype ID and badge label for a channel."""
    key = (channel_id or "").strip()
    norm_key = key.replace("-", "_")
    resolved_key = CHANNEL_ALIASES.get(key, CHANNEL_ALIASES.get(norm_key, norm_key))
    return dict(ARCHETYPE_MAP.get(resolved_key, ARCHETYPE_MAP.get(key, {"id": "unknown", "label": "Unknown Archetype"})))


def channel_profile_stamp(channel_id: str) -> Dict[str, Any]:
    """Provenance stamp matching ``brief-v3.json#/properties/channel_profile``."""
    ch = get_channel(channel_id)
    return {"id": ch.id, "version": REGISTRY_VERSION, "sha256": ch.sha256}


def channel_cast(channel_id: str, character_id: str = "CH01") -> Dict[str, str]:
    """Primary cast entry for ``content.characters`` using the channel's visual identity."""
    ch = get_channel(channel_id)
    return {
        "id": character_id,
        "name": ch.persona,
        "appearance": f"{ch.visual.cast_appearance}. {ch.visual.outfit}.",
        "outfit": ch.visual.outfit,
    }


def apply_channel(brief: Mapping[str, Any], channel_id: str) -> Dict[str, Any]:
    """Return a copy of ``brief`` with channel content inputs applied.

    Only schema-valid brief-v3 fields are touched: ``style``, ``tone``,
    ``channel_profile`` and the voice/speed of each output. Format, duration and
    every production contract stay owned by the existing pipeline.
    """
    ch = get_channel(channel_id)
    out = dict(brief)
    out["style"] = ch.visual.style_description
    out["tone"] = ch.tone
    out["channel_profile"] = channel_profile_stamp(ch.id)
    outputs = [dict(o) for o in out.get("outputs") or []]
    for o in outputs:
        o.setdefault("voice", ch.voice)
        o.setdefault("speed", ch.speed)
    if outputs:
        out["outputs"] = outputs
    tags = [t.lstrip("#") for t in ch.hashtags]
    kws = list(out.get("seo_keywords") or [])
    out["seo_keywords"] = kws + [t for t in tags if t not in kws]
    if ch.engagement is not None:
        eng = asdict(ch.engagement)
        out["engagement"] = {
            k: list(v) if isinstance(v, (list, tuple)) else v
            for k, v in eng.items()
        }
    return out


def writer_brief(channel_id: str, format_profile: str) -> str:
    """Markdown guidance handed to vp-research-architect / vp-scriptwriting for one job."""
    ch = get_channel(channel_id)
    spec = ch.spec_for(format_profile)
    lines = [
        f"# Channel: {ch.name} ({ch.id}) — {format_profile}",
        f"Promise: {ch.promise}",
        f"Audience: {ch.audience}",
        f"Persona: {ch.persona}",
        f"Tone: {ch.tone}",
        f"Duration: {spec.duration_seconds[0]}-{spec.duration_seconds[1]}s; "
        f"new beat every {spec.beat_interval_seconds[0]:g}-{spec.beat_interval_seconds[1]:g}s",
        "## Structure",
        *[f"- {s}" for s in spec.structure],
        f"- Closing: {spec.closing}",
        "## Tone rules",
        *[f"- {r}" for r in ch.tone_rules],
        "## Hook formulas",
        *[f"- {h}" for h in ch.hook_formulas],
        "## Avoid",
        *[f"- {a}" for a in ch.avoid],
        f"## Visual: {ch.visual.label}",
        f"- Thumbnail: {ch.visual.thumbnail_rule}",
    ]
    if ch.speed_optimization is not None:
        so = ch.speed_optimization
        lines.extend(
            [
                "## Speed & Hybrid Render Optimization",
                f"- Git branch: `{ch.git_branch}` | Local workspace: `{ch.workspace_dirname}`",
                f"- Platform routing: TikTok = `{ch.platform_routing['tiktok']}`, YouTube = `{ch.platform_routing['youtube']}`",
                f"- Render mode: `{so.render_mode}` (Remotion motion ratio: {int(so.remotion_motion_ratio * 100)}%)",
                f"- Fast-short max Flow images: {so.fast_short_max_images} | Spin-off shorts per YouTube long: {so.spinoff_shorts_per_long}",
                f"- Target build time: {so.estimated_short_minutes[0]}-{so.estimated_short_minutes[1]} min/short, "
                f"{so.estimated_bundle_minutes[0]}-{so.estimated_bundle_minutes[1]} min/bundle",
                f"- Strategy: {so.notes}",
            ]
        )
    return "\n".join(lines)


# ==============================================================================
# Non-Destructive Competitor Rebuild Bridge (V3.3)
# ==============================================================================

REBUILT_CHANNEL_ALIASES: Dict[str, str] = {
    # 4 renamed EN channels & aliases
    "en_plain_sight_ai": "en-scale-and-bone",
    "en-plain-sight-ai": "en-scale-and-bone",
    "en_scale_and_bone": "en-scale-and-bone",
    "en-scale-and-bone": "en-scale-and-bone",
    "en_kitchen_molecules": "en-root-and-canopy",
    "en-kitchen-molecules": "en-root-and-canopy",
    "en_root_and_canopy": "en-root-and-canopy",
    "en-root-and-canopy": "en-root-and-canopy",
    "en_wait_how": "en-spawn-to-apex",
    "en-wait-how": "en-spawn-to-apex",
    "en_spawn_to_apex": "en-spawn-to-apex",
    "en-spawn-to-apex": "en-spawn-to-apex",
    "en_parable_lamp": "en-deep-time-strata",
    "en-parable-lamp": "en-deep-time-strata",
    "en_deep_time_strata": "en-deep-time-strata",
    "en-deep-time-strata": "en-deep-time-strata",
}


def _resolve_rebuilt_channel_keys(channel_id: str) -> Tuple[str, str, str]:
    """Resolve (lang, formula_key, norm_id) for any of the 38 channels + 4 aliases.

    Returns:
        (lang, formula_key, normalized_id)
        where lang is 'VN' or 'EN', formula_key is the dictionary lookup key,
        and normalized_id is underscore-separated ID (e.g. 'tui_tien', 'en_first_principles').
    """
    raw = (channel_id or "").strip().lower()
    aliased = REBUILT_CHANNEL_ALIASES.get(raw, raw)
    u = aliased.replace("-", "_")
    h = aliased.replace("_", "-")

    from channels.en_flow_video_formulas import EN_FLOW_VIDEO_FORMULAS
    from channels.vn_flow_video_formulas import VN_FLOW_VIDEO_FORMULAS

    if u in VN_FLOW_VIDEO_FORMULAS:
        return "VN", u, u
    if h in EN_FLOW_VIDEO_FORMULAS:
        return "EN", h, h.replace("-", "_")

    # Check if channel exists in legacy registry and map to rebuilt
    if raw in CHANNEL_ALIASES:
        leg_aliased = CHANNEL_ALIASES[raw]
        leg_u = leg_aliased.replace("-", "_")
        leg_h = leg_aliased.replace("_", "-")
        if leg_u in VN_FLOW_VIDEO_FORMULAS:
            return "VN", leg_u, leg_u
        if leg_h in EN_FLOW_VIDEO_FORMULAS:
            return "EN", leg_h, leg_h.replace("-", "_")

    raise ValueError(f"Unknown rebuilt channel '{channel_id}'. Expected one of 38 channels or 4 aliases.")


def get_rebuilt_competitor_formula(channel_id: str) -> Dict[str, Any]:
    """Return the merged Flow physics + 5-stage dialogue formula dict for any of the 38 channels.

    Supports all 20 Vietnamese channels, 18 English channels, and 4 renamed aliases.
    """
    lang, key, _norm_id = _resolve_rebuilt_channel_keys(channel_id)
    if lang == "VN":
        from channels.vn_competitor_script_formulas import VN_COMPETITOR_SCRIPT_FORMULAS
        from channels.vn_flow_video_formulas import VN_FLOW_VIDEO_FORMULAS

        flow_data = dict(VN_FLOW_VIDEO_FORMULAS[key])
        script_data = VN_COMPETITOR_SCRIPT_FORMULAS.get(key, {})
        merged = dict(flow_data)
        for k, v in script_data.items():
            if k not in merged or k in ("competitor_dialogue_formula", "competitor_name", "voice"):
                merged[k] = v
        return merged
    else:
        from channels.en_competitor_script_formulas import EN_COMPETITOR_SCRIPT_FORMULAS
        from channels.en_flow_video_formulas import EN_FLOW_VIDEO_FORMULAS

        flow_data = dict(EN_FLOW_VIDEO_FORMULAS[key])
        script_data = EN_COMPETITOR_SCRIPT_FORMULAS.get(key, {})
        merged = dict(flow_data)
        for k, v in script_data.items():
            if k not in merged or k in ("competitor_dialogue_formula", "competitor_name", "voice"):
                merged[k] = v
        return merged


def get_rebuilt_visual_identity(channel_id: str) -> VisualIdentity:
    """Return a VisualIdentity populated with the rebuilt competitor benchmark.

    Resolves both VN channels (via VN_FLOW_VIDEO_FORMULAS) and EN channels + 4 renamed EN aliases
    (via EN_FLOW_VIDEO_FORMULAS), with profile_id=f"ch_rebuilt_{norm_id}".
    """
    _lang, _key, norm_id = _resolve_rebuilt_channel_keys(channel_id)
    formula = get_rebuilt_competitor_formula(channel_id)

    # Resolve legacy channel profile if available for fallback appearance/palette
    try:
        legacy_ch = get_channel(channel_id)
    except Exception:
        legacy_ch = None

    profile_id = f"ch_rebuilt_{norm_id}"
    label = (
        formula.get("new_visual_label")
        or formula.get("competitor_benchmark")
        or formula.get("competitor_name")
        or (legacy_ch.visual.label if legacy_ch else f"Rebuilt {norm_id}")
    )
    style_description = (
        formula.get("style_description")
        or formula.get("continuity_anchor")
        or (legacy_ch.visual.style_description if legacy_ch else "")
    )
    thumbnail_rule = (
        formula.get("thumbnail_rule")
        or (legacy_ch.visual.thumbnail_rule if legacy_ch else "")
        or f"One high-contrast focal subject representing {formula.get('competitor_benchmark', norm_id)}, 2-4 uppercase bold words, zero overlay card, 25% margin"
    )
    cast_appearance = (
        formula.get("cast_appearance")
        or (legacy_ch.visual.cast_appearance if legacy_ch else "Realistic documentary subject with contextual focus")
    )
    outfit = (
        formula.get("outfit")
        or (legacy_ch.visual.outfit if legacy_ch else "Contextual documentary styling, zero cartoon elements")
    )
    palette = (
        tuple(formula.get("palette", ()))
        or (legacy_ch.visual.palette if legacy_ch else ("#0F172A", "#38BDF8", "#F59E0B", "#10B981"))
    )

    return VisualIdentity(
        profile_id=profile_id,
        label=label,
        style_description=style_description,
        cast_appearance=cast_appearance,
        outfit=outfit,
        palette=palette,
        thumbnail_rule=thumbnail_rule,
    )


def apply_rebuilt_channel(brief: Mapping[str, Any], channel_id: str) -> Dict[str, Any]:
    """Apply rebuilt competitor visual identity and formulas to brief.

    Calls apply_channel(brief, channel_id), overrides out["style"] with rebuilt
    competitor style_description, and attaches out["rebuilt_competitor_benchmark"].
    """
    out = apply_channel(brief, channel_id)
    rebuilt_visual = get_rebuilt_visual_identity(channel_id)
    formula = get_rebuilt_competitor_formula(channel_id)

    out["style"] = rebuilt_visual.style_description
    benchmark = (
        formula.get("competitor_benchmark")
        or formula.get("competitor_name")
        or ""
    )
    out["rebuilt_competitor_benchmark"] = benchmark
    out["rebuilt_visual_label"] = rebuilt_visual.label
    out["rebuilt_profile_id"] = rebuilt_visual.profile_id

    formula_voice = formula.get("voice")
    if formula_voice and "outputs" in out:
        for o in out["outputs"]:
            o["voice"] = formula_voice

    return out

