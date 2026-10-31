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
                "Mở đầu bằng một điểm nghẽn địa lý hoặc tài nguyên bất ngờ trên bản đồ.",
                "Mọi cuộc xung đột hay hiệp ước đều phải quy về dòng chảy tiền, dầu hoặc hàng hóa.",
                "Dùng bản đồ phẳng 2D tối giản có mũi tên chiến lược rõ ràng.",
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
                label="Bản đồ chiến lược 2D: hải đồ, điểm nghẽn hàng hải, đường kinh tế trên nền đại dương sâu",
                style_description=(
                    "Crisp 2D flat editorial cartography and strategic war-room atlas illustration on deep maritime navy canvas "
                    "(#0F2439 deep maritime navy ocean, #EDE3CE parchment landmass with fine topographic contour lines, "
                    "#E63946 strategic choke-point red, #F4A261 trade-route amber, #2A9D8F radar teal); "
                    "clean vector contour lines, trade corridors, shipping routes and nautical coordinates; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Character-free cartographic emblem: brass compass rose, flat 2D naval vessels, strategic route arrows, and topographic landmass reliefs (zero human characters)",
                outfit="No human clothing; crisp brass and crimson cartographic vector markers",
                palette=("#0F2439", "#EDE3CE", "#E63946", "#F4A261", "#2A9D8F"),
                thumbnail_rule="Strategic strait map with glowing red choke point + 2-4 uppercase VN words.",
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
                label="Lazy Brain Doodle — Cream canvas, blue-shirt stickman, brain & dopamine metaphors",
                style_description="Hand-drawn 2D neuroscience and focus doodle explainer: wobbly black marker outlines (#000000), flat unshaded fills in warm cream (#F8F0DC), bold cobalt blue (#3B82C4), coral (#F2B88B), sage (#93A88C) and white (#FFFFFF) on a solid cream canvas (#F8F0DC); oversized bald circle stickman in blue shirt with simple analog clock, neuron synapses and phone screens; orthographic 2D, minimal, at least 60% negative space, zero 3D, zero gradients.",
                cast_appearance="Iconic 2D doodle stickman with oversized white (#FFFFFF) bald circle head, bold pitch-black (#000000) marker outline, tiny dot eyes, minimal smile, wire arms and round white circle hands",
                outfit="Flat cobalt-blue (#3B82C4) t-shirt over slate-gray pants, no shading",
                palette=("#F8F0DC", "#3B82C4", "#F2B88B", "#93A88C", "#2E4361", "#FFFFFF", "#000000"),
                thumbnail_rule="Stickman with exaggerated emotion staring at clock + 2-4 uppercase bold words on flat cream canvas.",
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
                label="Psychological crowd noir: high-contrast 2D graphic novel, aged dossier paper, crimson puppet strings",
                style_description=(
                    "High-contrast 2D psychological noir graphic-novel art on aged dossier paper canvas "
                    "(#111111 ink black, #E8E2D0 dossier paper, #5A5F66 slate shadow, #C0392B crimson puppet-strings); "
                    "sharp chiaroscuro ink shadows, dossier pins, connecting string matrices and anonymous crowd silhouettes; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Sharp-suited anonymous noir observer silhouette with glowing white lapel pin amidst shadowed crowd figures and crimson influence threads",
                outfit="Sharp charcoal-black suit silhouette with crisp white collar and glowing crimson pin, no shading",
                palette=("#111111", "#E8E2D0", "#5A5F66", "#C0392B", "#FFFFFF"),
                thumbnail_rule="Noir silhouette cutting crimson puppet strings + 2-4 uppercase words on flat dossier background.",
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
                label="Soft pastel warm-line duo: Psych2Go-inspired empathetic characters Leo and Maya on warm cream",
                style_description=(
                    "Soft Psych2Go-inspired 2D pastel line-art illustration on warm cream canvas "
                    "(#FFF8F0 warm cream canvas, #5B4636 smooth warm-espresso outlines, #F7C6C7 blush pink, #CDB4DB soft lavender, "
                    "#BDE0C6 sage mint, #FFF1B5 butter yellow); gentle emotional storytelling, warm domestic and relational vignettes; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Recurring expressive young couple and friends duo — Leo (warm wavy brown hair, kind eyes, flat mint sweater) and Maya (shoulder-length dark bob hair, expressive eyes, flat blush cardigan)",
                outfit="Leo in flat sage-mint (#BDE0C6) crewneck sweater; Maya in soft blush-pink (#F7C6C7) button cardigan",
                palette=("#FFF8F0", "#5B4636", "#F7C6C7", "#CDB4DB", "#BDE0C6", "#FFF1B5"),
                thumbnail_rule="Leo and Maya having an honest conversation + 2-4 uppercase words on soft cream canvas.",
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
            id="en_ego_unmasked",
            name="Ego Unmasked",
            niche="Carl Jung depth psychology, Shadow Work, ego defense mechanisms & self-awareness",
            promise="Examine the shadow parts of your psyche, dissolve ego defenses, and gain genuine self-knowledge.",
            audience="Self-reflective adults interested in Jungian depth psychology and inner sovereignty",
            persona="Calm philosophical analyst exploring the unconscious mind with respect and clarity",
            tone="Reflective, profound, grounded, psychologically penetrating",
            tone_rules=(
                "Open with an uncomfortable ego defense mechanism viewers immediately recognize.",
                "Deconstruct the unconscious drive using Carl Jung's concepts simply.",
                "Keep the exploration objective, compassionate, and empowering.",
                "Conclude with an integrative reflection question for quiet journaling.",
            ),
            hook_formulas=(
                "Carl Jung's Shadow Work explained: why what you hate in others is hidden in you.",
                "The spotlight effect: why nobody is judging you as much as you think.",
                "How your ego uses busyness to hide deep insecurity.",
                "The persona trap: what happens when you become your social mask.",
            ),
            avoid=("Superficial pop-spirituality clichés", "Demonizing psychological defenses", "Mystical jargon without grounding"),
            short_spec=_short((35, 50), "Does this shadow dynamic ring true for you? Reflect with us below."),
            long_spec=_long((480, 720), "Continue your inner exploration with our deep-dive on Ego Unmasked."),
            visual=VisualIdentity(
                profile_id="ch_en_jungian_noir",
                label="Jungian chiaroscuro noir: dramatic graphic-novel engraving, golden alchemical mirror, shadow masks",
                style_description=(
                    "Dramatic 2D chiaroscuro graphic-novel engraving on ivory parchment canvas "
                    "(#141418 obsidian ink black, #EAE2D3 ivory parchment, #C89B3C alchemical mirror gold, #9E2A2B shadow crimson); "
                    "high-contrast psychological shadow archetypes, dual theater masks, and symbolic golden mirrors; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Refined graphic-novel protagonist in charcoal high-collar coat holding an ivory theater mask beside a golden mirror silhouette",
                outfit="High-collared charcoal frock coat over dark vest with alchemical gold pocket-watch chain, no shading",
                palette=("#141418", "#EAE2D3", "#C89B3C", "#9E2A2B", "#FFFFFF"),
                thumbnail_rule="Character removing ivory mask revealing golden silhouette + 2-4 uppercase words.",
            ),
            references=(
                ReferenceChannel("Eternalised", "YouTube", "long", "In-depth explorations of Jungian archetypes, shadow, and existential philosophy."),
                ReferenceChannel("Academy of Ideas", "YouTube", "long", "Psychological sovereignty, individualism, and Carl Jung case studies."),
                ReferenceChannel("Man and His Symbols by Carl Jung & The Courage to Be Disliked", "Book/Scripture", "long", "Unconscious symbolism, shadow integration, and Adlerian psychology."),
                ReferenceChannel("Jungian Reflections", "YouTube", "short", "Punchy 40-second reflections on projection and ego traps."),
            ),
            seed_topics=(
                "Carl Jung's Shadow Work Explained: Why What You Hate in Others Is Hidden in You",
                "The Spotlight Effect: Why Nobody Is Judging You as Much as You Think",
                "How Your Ego Uses Busyness to Hide Deep Insecurity",
                "The Persona Trap: What Happens When You Become Your Social Mask",
                "5 Defense Mechanisms Your Mind Uses Without Your Permission",
            ),
            hashtags=("#psychology", "#carljung", "#shadowwork", "#philosophy", "#selfawareness", "#mindset"),
            monetization=("YouTube AdSense (long)", "Shadow work guided workbook", "Depth philosophy book curation"),
            philosophy_id="cognition",
            voice="OmniVoice_EnEgoUnmasked",
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
                notes="Remotion subtle shadow silhouette dissolve and mirror reflection animations.",
            ),
            engagement=EngagementSpec(
                cta_voice="Thoughtful depth philosopher",
                bridge_templates=(
                    "Watch the complete Jungian shadow exploration on Ego Unmasked YouTube channel.",
                    "See the full 15-minute examination of ego defense structures on our main channel.",
                ),
                close_templates=(
                    "Which defense mechanism caught your awareness today? Leave a reflection below.",
                    "Take a quiet breath and notice where this persona appears in your week.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@EgoUnmasked", "@EgoUnmaskedHQ", "@EgoUnmaskedLab", "@TheEgoUnmasked"]},
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
                "Use visual logic trees and balance scale analogies rather than abstract math.",
                "End with a practical decision framework for daily evaluation.",
            ),
            hook_formulas=(
                "The Prisoner's Dilemma: why being purely selfish backfires in the long run.",
                "Survivorship bias: the WWII airplane bullet holes everyone misunderstood.",
                "Goodhart's Law: what happens when a measure becomes the target.",
                "Second-order thinking: how great strategists see three moves ahead.",
            ),
            avoid=("Unproven conspiracy models", "Dismissive intellectual arrogance", "Dense mathematical notation without visual proof"),
            short_spec=_short((35, 50), "Which move would you play in this paradox? Comment your choice."),
            long_spec=_long((480, 720), "Master our next mental model in depth on First Principles Ink."),
            visual=VisualIdentity(
                profile_id="ch_en_blueprint_logic",
                label="Prussian blueprint logic schematic: razor-sharp mental models, decision trees, amber node highlights",
                style_description=(
                    "Razor-sharp 2D Prussian blueprint and mental-model schematic on deep blueprint blue canvas "
                    "(#142B47 deep blueprint blue canvas, #F8FAFC crisp white drafting lines, #FFB703 amber focal accent, #38BDF8 cyan node accent); "
                    "clean systemic flowcharts, domino sequences, first-principles logic breakdowns; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Sleek flat geometric mid-century strategist character with angular spectacles and crisp white drafting jacket pointing at clean decision trees and domino chains",
                outfit="Minimalist white drafting lab jacket over Prussian navy turtleneck with angular amber spectacles",
                palette=("#142B47", "#F8FAFC", "#FFB703", "#38BDF8", "#0F172A"),
                thumbnail_rule="Strategist pointing pointer at glowing amber root cause + 2-4 uppercase words.",
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
                notes="Remotion dynamic decision tree animations and domino tipping sequences.",
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
                profile_id="ch_en_ledger_grid",
                label="Financial ledger notebook sketch: fountain-pen ink on graph paper, green dollars, deficit red ink",
                style_description=(
                    "Hand-inked 2D financial ledger notebook illustration on warm square-grid graph paper "
                    "(#FAF6E9 ivory paper with faint #E3DCC8 grid, #2F9E5B dollar emerald, #F2C14E bullion gold, #D64545 deficit red, #24364F fountain-pen navy); "
                    "clean balance-sheet columns, cashflow conduits, and financial anatomy charts; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Witty mid-century editorial bookkeeper character with neat side-parted hair, round tortoiseshell glasses, green visor and vest and fountain pen",
                outfit="Forest green accountant vest over rolled-up sleeve ivory shirt with neat navy tie and tortoiseshell glasses",
                palette=("#FAF6E9", "#24364F", "#2F9E5B", "#F2C14E", "#D64545", "#E3DCC8"),
                thumbnail_rule="Bookkeeper circling red deficit trap on giant ledger + 2-4 uppercase words.",
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
                label="Swiss macroeconomic editorial vector: Economist-style clean geometry, trade routes, central bank navy",
                style_description=(
                    "Bold Economist-style 2D flat geometric Swiss editorial vector infographic on financial-press paper canvas "
                    "(#F3EFE6 financial-press paper, #0F2C59 central-bank navy, #D9381E inflation vermilion, #2A9D8F trade teal, #E9C46A reserve gold) "
                    "with zero marker wobble, precise economic indicators, container shipping icons and monetary policy levers; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Crisp flat vector editorial host in structured navy suit and vermilion tie alongside clean cargo ships, interest-rate levers and currency bars",
                outfit="Sharp tailored central-bank navy (#0F2C59) two-button suit with crisp white shirt and vermilion tie",
                palette=("#F3EFE6", "#0F2C59", "#D9381E", "#2A9D8F", "#E9C46A"),
                thumbnail_rule="Host pulling central-bank interest lever + 2-4 uppercase words on clean paper.",
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
            name="Plain Sight AI",
            niche="Practical no-code AI workflows, prompt engineering & office automation for regular people",
            promise="Demystify AI tools and provide repeatable 3-step prompt workflows that save hours of work.",
            audience="Office workers, students, creators, and freelancers who want practical AI utility without coding",
            persona="Down-to-earth tech guide who cuts through hype to deliver genuinely useful workflows",
            tone="Direct, practical, encouraging, step-by-step, no-BS",
            tone_rules=(
                "Hook with a tedious office task that usually takes two hours.",
                "Demonstrate the exact prompt formula and structure step by step.",
                "Highlight the verification step to catch AI hallucinations cleanly.",
                "End with a copy-pasteable prompt template viewers can use immediately.",
            ),
            hook_formulas=(
                "Why buying expensive AI tools wastes your time: 3 free workflows that work.",
                "Stop asking AI to write an email: use this 3-part prompt structure instead.",
                "How to audit any contract for hidden red flags in 60 seconds with AI.",
                "5 repeatable AI workflows that save 2 hours of office work every day.",
            ),
            avoid=("Selling get-rich-quick AI gimmicks", "Promoting unverified AI wrapper tools", "Overly complex code installations"),
            short_spec=_short((35, 50), "Which repetitive task would you like automated next? Comment below."),
            long_spec=_long((480, 720), "Download our free prompt workflow library on Plain Sight AI YouTube."),
            visual=VisualIdentity(
                profile_id="ch_en_ai_doodle",
                label="Plain Sight AI Doodle — Violet hoodie stickman, browser frames and prompt cards",
                style_description="Hand-drawn 2D practical AI workflow doodle explainer: wobbly black marker outlines (#000000), flat unshaded fills in clean white (#FFFFFF), electric violet (#7C5CFF), tech cobalt (#3B82C4), mint green (#34D399) and dark slate (#2E4361) on a solid white canvas (#FFFFFF); stickman in violet hoodie pointing at clean browser cards, clipboard checklists, and prompt tags; orthographic 2D, minimal, at least 60% negative space, zero 3D.",
                cast_appearance="Iconic 2D doodle stickman with oversized white (#FFFFFF) bald circle head, clean black outline, tech-savvy dot eyes, wire arms, and round circle hands",
                outfit="Flat violet hoodie (#7C5CFF) with subtle cyan accent, no shading",
                palette=("#FFFFFF", "#7C5CFF", "#3B82C4", "#34D399", "#2E4361", "#000000"),
                thumbnail_rule="Stickman comparing an empty prompt vs a 3-part structure + 2-4 uppercase bold words.",
            ),
            references=(
                ReferenceChannel("Jeff Su", "YouTube", "long", "Practical productivity hacks, prompt structures, and office automation."),
                ReferenceChannel("Matt Wolfe", "YouTube", "long", "Curated evaluations of genuinely useful AI software and workflows."),
                ReferenceChannel("Anthropic & OpenAI Official Prompt Engineering Guides", "Book/Scripture", "long", "Systematic chain-of-thought and few-shot structuring benchmarks."),
                ReferenceChannel("Jeff Su Shorts", "TikTok/YouTube Shorts", "short", "60-second productivity and prompt tips."),
            ),
            seed_topics=(
                "Why Buying Expensive AI Tools Wastes Your Time (And 3 Free Workflows That Work)",
                "Stop Asking AI to Write an Email—Use This 3-Part Prompt Structure Instead",
                "How to Audit Any Contract for Hidden Red Flags in 60 Seconds with AI",
                "5 Repeatable AI Workflows That Save 2 Hours of Office Work Every Day",
                "Why AI Hallucinates—And the Simple Verification Step Most People Skip",
            ),
            hashtags=("#ai", "#artificialintelligence", "#productivity", "#promptengineering", "#chatgpt", "#automation"),
            monetization=("YouTube AdSense (long)", "Curated prompt workflow repository", "Productivity software sponsorship"),
            philosophy_id="research_guide",
            voice="OmniVoice_EnPlainSightAI",
            speed=1.0,
            wave=4,
            language="en",
            speed_optimization=SpeedOptimizationSpec(
                render_mode="screen_capture_hybrid",
                fast_short_max_images=5,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.5,
                estimated_short_minutes=(6, 9),
                estimated_bundle_minutes=(24, 34),
                notes="Remotion interactive prompt typing previews and verification checklists.",
            ),
            engagement=EngagementSpec(
                cta_voice="Practical workflow coach",
                bridge_templates=(
                    "Watch the complete step-by-step tutorial on Plain Sight AI YouTube channel.",
                    "See all five prompt templates with full live examples on our main channel.",
                ),
                close_templates=(
                    "What repetitive task do you want automated next? Tell us in the comments.",
                    "Test this prompt template today and see how many minutes you save.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@PlainSightAI", "@PlainSightAIHQ", "@PlainSightAILab", "@GetPlainSightAI"]},
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
                label="Career Leverage Doodle — Royal-blue shirt stickman, leverage bars and corporate ladders",
                style_description="Hand-drawn 2D career strategy doodle explainer: wobbly black marker outlines (#000000), flat unshaded fills in warm cream (#F8F0DC), royal cobalt blue (#3B82C4), warm peach (#F2B88B), deep slate (#2E4361) and white (#FFFFFF) on a solid cream canvas (#F8F0DC); stickman in royal blue shirt with office lanyard standing by wooden levers, corporate ladder rungs, and meeting tables; orthographic 2D, minimal, at least 60% negative space, zero 3D.",
                cast_appearance="Iconic 2D doodle stickman with oversized white (#FFFFFF) bald circle head, bold black outline, professional lanyard, wire arms, and round circle hands",
                outfit="Flat royal-blue shirt (#3B82C4) with simple company lanyard, no shading",
                palette=("#F8F0DC", "#3B82C4", "#F2B88B", "#2E4361", "#FFFFFF", "#000000"),
                thumbnail_rule="Stickman lifting a heavy corporate ladder using a leverage bar + 2-4 uppercase bold words.",
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
                profile_id="ch_en_risograph_law",
                label="Vintage legal risograph print: 3-color mid-century New Yorker editorial, red seal ink on newsprint",
                style_description=(
                    "Crisp 3-color mid-century New Yorker editorial risograph print on newsprint ivory canvas "
                    "(#F4EFE6 newsprint ivory, #1D3557 navy ink, #E63946 red-seal ink, #457B9D steel blue); "
                    "stippled halftone textures, magnifying-glass investigations and consumer protection clauses; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Sharp-witted human consumer advocate drawn in expressive fountain-pen ink with neat hair, spectacles, navy blazer and brass magnifying glass inspecting red-stamped contract clauses",
                outfit="Unshaded navy blazer with steel-blue collar, spectacles, and brass magnifying glass in pocket",
                palette=("#F4EFE6", "#1D3557", "#E63946", "#457B9D", "#D8E2DC"),
                thumbnail_rule="Consumer advocate holding magnifying glass over giant hidden fee clause + 2-4 uppercase words.",
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
                label="Kawaii medical mascots: clean clinical white canvas, personified organ characters Ticker, Gurgle, Cortex",
                style_description=(
                    "Clean 2D kawaii medical mascot illustration on pure clinical white canvas "
                    "(#FFFFFF background, #222222 smooth outlines, #F4A6A6 heart pink, #F6C28B stomach peach, #7FB3D5 oxygen blue, #82E0AA immune-cell mint); "
                    "cute personified human physiology, friendly cells, and cartoon anatomy; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Adorable recurring personified body mascots — brave Ticker the Heart, dramatic Gurgle the Stomach, calm Cortex the Brain, and armored little T-Cell defender with expressive faces and full character anatomy",
                outfit="Tiny white medical headband on Ticker; little warrior helmet on T-Cell defender",
                palette=("#FFFFFF", "#222222", "#F4A6A6", "#F6C28B", "#7FB3D5", "#82E0AA"),
                thumbnail_rule="Cute Ticker the Heart sounding an alarm siren + 2-4 uppercase words on clean white.",
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
            name="Kitchen Molecules",
            niche="Food chemistry, kitchen safety myths, cooking reactions & ultra-processed food science",
            promise="Unlock the fascinating science of cooking and debunk dangerous kitchen myths with microbiology.",
            audience="Home cooks, foodies, and curious minds curious about culinary chemistry and safety",
            persona="Passionate food scientist who brings molecular kitchen reactions to life with stick figures",
            tone="Lively, appetizing, scientific, accessible, myth-busting",
            tone_rules=(
                "Hook with a common kitchen habit or cooking myth people do every day.",
                "Explain the chemical or biological mechanism (e.g. Maillard reaction, bacterial curve).",
                "Use relatable kitchen analogies with pans, thermometers, and molecules.",
                "End with one simple chef-science technique that improves food quality or safety.",
            ),
            hook_formulas=(
                "The chemistry of reused cooking oil: what actually happens at 350 degrees?",
                "Never thaw frozen meat in hot water: here is the bacteria math.",
                "The Maillard reaction: why browning makes almost everything taste better.",
                "Is the 5-second dropped food rule real? What microbiology says.",
            ),
            avoid=("Extreme fad diet preaching", "Sensational food fearmongering", "Rejecting peer-reviewed nutritional science"),
            short_spec=_short((35, 50), "Did this kitchen rule surprise you? Tell us your cooking habits below."),
            long_spec=_long((480, 720), "Master the science of delicious food with Kitchen Molecules on YouTube."),
            visual=VisualIdentity(
                profile_id="ch_en_culinary_sticker",
                label="Food science sticker-pop cartoon: die-cut white borders, cheerful culinary mascots Sunny and Sizzle",
                style_description=(
                    "Vibrant 2D die-cut sticker-pop food-science cartoon on warm buttercream canvas "
                    "(#FFF9EB warm buttercream canvas, #FF6B6B sear coral, #FFD166 butter gold, #06D6A0 basil green, #118AB2 steam blue) "
                    "with thick smooth outlines, chunky white sticker borders, and lively Maillard reaction sprites; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Cheerful anthropomorphic culinary mascots — Sunny the golden egg, Sizzle the skillet sprite, and bouncy flavor-molecule buddies with big expressive eyes",
                outfit="Tiny red chef kerchief on Sunny; cheerful blue steam plume on Sizzle sprite",
                palette=("#FFF9EB", "#FF6B6B", "#FFD166", "#06D6A0", "#118AB2", "#2B2D42"),
                thumbnail_rule="Sunny the egg character dodging a smoking pan + 2-4 uppercase words on buttercream canvas.",
            ),
            references=(
                ReferenceChannel("MinuteFood", "YouTube", "long", "Snackable physics and chemistry behind everyday kitchen processes."),
                ReferenceChannel("Adam Ragusea", "YouTube", "long", "Practical food science, kitchen myths, and culinary culinary realities."),
                ReferenceChannel("On Food and Cooking by Harold McGee & Ultra-Processed People", "Book/Scripture", "long", "Masterwork of culinary chemistry, industrial food science, and emulsions."),
                ReferenceChannel("MinuteFood Shorts", "TikTok/YouTube Shorts", "short", "Bite-sized 45-second cooking science myth-busters."),
            ),
            seed_topics=(
                "The Chemistry of Reused Cooking Oil: What Actually Happens at 350 Degrees?",
                "Never Thaw Frozen Meat in Hot Water—Here Is the Bacteria Math",
                "The Maillard Reaction: Why Browning Makes Almost Everything Taste Better",
                "Is the 5-Second Dropped Food Rule Real? What Microbiology Says",
                "Why Honey Never Spoils While Fresh Bread Molds in Days",
            ),
            hashtags=("#foodscience", "#cooking", "#chemistry", "#food", "#kitchen", "#science"),
            monetization=("YouTube AdSense (long)", "Kitchen science temperature guide cheat sheets", "High-quality kitchenware sponsorship"),
            philosophy_id="cognition",
            voice="OmniVoice_EnKitchenMolecules",
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
                notes="Remotion thermometer rise animation and molecular bonding visuals.",
            ),
            engagement=EngagementSpec(
                cta_voice="Culinary science teacher",
                bridge_templates=(
                    "Watch the complete cooking oil chemistry experiment on Kitchen Molecules YouTube.",
                    "See all five kitchen science myth-busters in full on our YouTube channel.",
                ),
                close_templates=(
                    "Which cooking myth were you taught growing up? Share your kitchen story below.",
                    "Try browning at higher heat next time and taste the chemical difference.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@KitchenMolecules", "@KitchenMoleculesHQ", "@KitchenScienceInk", "@FoodMoleculesLab"]},
        ),
        ChannelProfile(
            id="en_wait_how",
            name="Wait, How?",
            niche="Everyday physics paradoxes, debunked school myths & surprising natural phenomena",
            promise="Answer everyday physical curiosities with delightful clarity so you see the world anew.",
            audience="Curious adults, students, and thinkers who love asking why everyday things work the way they do",
            persona="Playful Feynman-style physics teacher who explains bizarre phenomena effortlessly",
            tone="Playful, mind-expanding, intuitive, lucid, wonder-filled",
            tone_rules=(
                "Hook with an everyday observation that sounds intuitive but is completely misunderstood.",
                "Show why the popular schoolbook explanation is subtly incomplete.",
                "Use clear mechanical stickman doodles to illustrate the true physical force.",
                "End with an 'aha' moment that changes how viewers see that phenomenon forever.",
            ),
            hook_formulas=(
                "8 everyday science myths your school teachers got completely wrong.",
                "Why mosquitoes only bite one specific person in a crowded room.",
                "How airplanes actually stay up: why both popular explanations are incomplete.",
                "Why ice is slippery even below freezing temperatures.",
            ),
            avoid=("Overly formal university tensor equations", "Clickbait without legitimate physical answers", "Conspiracy pseudoscience"),
            short_spec=_short((35, 50), "Did your teacher teach you this myth too? Let us know below."),
            long_spec=_long((480, 720), "Discover the wonder behind everyday physics on Wait How on YouTube."),
            visual=VisualIdentity(
                profile_id="ch_en_sticker_pop",
                label="Electric sticker-pop science mascot: bouncy star-spark creature Quark with question-mark antenna",
                style_description=(
                    "Energetic 2D sticker-pop science cartoon on warm cream canvas "
                    "(#FFF6D6 warm cream, #FFD23F electric lemon, #FF6B6B coral red, #2EC4B6 bright teal, #7B2CBF proton violet) "
                    "with bold smooth outlines, chunky white sticker borders, and eye-opening everyday physics curiosities; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Recurring mascot Quark — a bouncy round electric-lemon (#FFD23F) star-spark creature with huge curious oval eyes, tiny floating hands and a hovering question-mark antenna",
                outfit="Natural golden spark glow, tiny teal bow tie and floating question-mark antenna, no human clothes",
                palette=("#FFF6D6", "#FFD23F", "#FF6B6B", "#2EC4B6", "#7B2CBF", "#1D3557"),
                thumbnail_rule="Mascot Quark with giant shocked eyes looking at everyday mystery + 2-4 uppercase words.",
            ),
            references=(
                ReferenceChannel("MinutePhysics", "YouTube", "long", "Stick-figure animations explaining deep physical laws simply."),
                ReferenceChannel("MinutePhysics Shorts", "TikTok/YouTube Shorts", "short", "Punchy 45-second physics paradox and thought-experiment animations."),
                ReferenceChannel("AsapSCIENCE", "YouTube", "long", "Fun, dynamic science answers to everyday curiosities."),
                ReferenceChannel("What If? by Randall Munroe (xkcd)", "Book/Scripture", "long", "Serious scientific answers to absurd hypothetical questions."),
                ReferenceChannel("Steve Mould", "YouTube", "long", "Hands-on physical demonstrations of bizarre fluid and mechanical paradoxes."),
            ),
            seed_topics=(
                "8 Everyday Science Myths Your School Teachers Got Completely Wrong",
                "Why Mosquitoes Only Bite One Specific Person in a Crowded Room",
                "How Airplanes Actually Stay Up (Why Both Popular Explanations Are Incomplete)",
                "Why Ice Is Slippery Even Below Freezing Temperature",
                "Why Mirrors Flip Left and Right—But Never Top and Bottom",
            ),
            hashtags=("#physics", "#science", "#waithow", "#curiosity", "#education", "#stem"),
            monetization=("YouTube AdSense (long)", "Illustrated science paradox poster prints", "Science educational app sponsor"),
            philosophy_id="cognition",
            voice="OmniVoice_EnWaitHow",
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
                notes="Remotion trajectory particle bursts and optical ray path animations.",
            ),
            engagement=EngagementSpec(
                cta_voice="Inquisitive science explorer",
                bridge_templates=(
                    "Watch the complete aerodynamics breakdown on Wait How YouTube channel.",
                    "See all eight school science myths debunked on our main YouTube channel.",
                ),
                close_templates=(
                    "Which everyday mystery has always puzzled you? Tell us in the comments.",
                    "Look closely at this phenomenon tomorrow and see the physics at play.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@WaitHowScience", "@WaitHowDoodle", "@WaitHowExplained", "@WaitHowLab"]},
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
                label="Forensic noir graphic novel: deep ink black, aged case-file manila, red evidence tags, trench coat silhouette",
                style_description=(
                    "Classic 2D forensic noir graphic-novel illustration on aged case-file manila canvas "
                    "(#111111 deep ink black, #E8E2D0 aged case-file manila, #5A5F66 fog-slate, #C0392B forensic evidence crimson); "
                    "chalk contours, archive folders, magnifying lenses, and high-contrast shadow drama; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Shadowy faceless trench-coat detective silhouette in a fedora hat holding a warm lantern beam over crimson-tagged archival clues",
                outfit="Classic flat charcoal trench coat with turned-up collar, wide-brim fedora hat, zero shading",
                palette=("#111111", "#E8E2D0", "#5A5F66", "#C0392B", "#FFFFFF"),
                thumbnail_rule="Trench coat detective lantern beam highlighting clue + 2-4 uppercase words.",
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
                label="Strategic maritime atlas: Vox-style flat cartography, sand topographic landmasses, choke point straits",
                style_description=(
                    "Crisp Vox and Johnny Harris-inspired 2D flat strategic cartography illustration on deep maritime navy ocean canvas "
                    "(#0D1B2A deep maritime navy ocean, #E6CCB2 topographic sand landmasses, #E63946 blockade crimson, #FFB703 shipping-lane gold, #4EA8DE strait cyan); "
                    "fine topographic contour lines, container vessel icons, blockade vectors, and maritime choke points; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Character-free strategic cartography emblem: precision compass rose, 2D flat tanker silhouettes, maritime choke-point contours, and glowing trade-corridor arrows (zero human characters)",
                outfit="No human clothing; high-contrast gold and crimson cartographic vector overlays",
                palette=("#0D1B2A", "#E6CCB2", "#E63946", "#FFB703", "#4EA8DE"),
                thumbnail_rule="Glowing crimson blockade over strategic strait map + 2-4 uppercase words.",
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
                label="Deep-space geometric vector: Kurzgesagt-style cosmic indigo, vibrant nebula colors, robotic probe Nova",
                style_description=(
                    "Vibrant Kurzgesagt-inspired 2D flat geometric space vector art on deep space indigo canvas "
                    "(#0B1026 deep space indigo, #4CC9F0 pulsar cyan, #F72585 nebula magenta, #FFD166 solar gold, #7209B7 cosmic violet) "
                    "with clean lineless rounded vector forms, geometric celestial spheres, gravitational lensing curves; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Cute spherical golden-and-white deep-space probe mascot Nova with a glowing cyan digital eye and tiny solar-panel wings orbiting luminous geometric planets",
                outfit="Polished white ceramic body shell with gold accents and solar-panel wings, no human clothing",
                palette=("#0B1026", "#4CC9F0", "#F72585", "#FFD166", "#7209B7", "#FFFFFF"),
                thumbnail_rule="Mascot Nova orbiting a glowing ringed planet + 2-4 uppercase words on deep indigo.",
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
                label="Sumi-e Zen brush-ink wash: handmade Xuan paper, bamboo sage wash, mindful monk and tranquil water ripples",
                style_description=(
                    "Minimalist 2D Zen Sumi-e brush-ink wash illustration on warm Xuan rice paper canvas "
                    "(#F5EFE0 handmade rice paper, #1C1C1C calligraphy brush ink, #5F7A61 bamboo sage wash, #D98A76 lotus coral) "
                    "with tranquil negative space, spontaneous calligraphy strokes, lotus blossoms, and quiet water ripples; "
                    "orthographic 2D, at least 65% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Serene brush-painted mindfulness monk in flowing sage-linen robes beside calm water ripples, lotus blossoms and bamboo",
                outfit="Loose-fitting bamboo-sage (#5F7A61) linen meditation robe with gentle brush-edge contours",
                palette=("#F5EFE0", "#1C1C1C", "#5F7A61", "#D98A76", "#8C7A6B"),
                thumbnail_rule="Serene monk deflecting the second arrow with calm mind + 2-4 uppercase words.",
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
            name="Parable & Lamp",
            niche="Biblical parables, wisdom of Proverbs & Ecclesiastes, forgiveness, grace & hope illustrated",
            promise="Illuminate timeless biblical parables, wisdom literature, and hope with heartwarming stick figures.",
            audience="Faith seekers, lovers of timeless moral parables, and viewers seeking forgiveness and hope",
            persona="Kind biblical storyteller unpacking ancient wisdom with warmth, grace, and humility",
            tone="Warm, inspiring, reflective, gracious, literary",
            tone_rules=(
                "Begin with an ancient moral parable and its immediate modern parallel.",
                "Unpack the historical context and original literary meaning with care.",
                "Emphasize forgiveness, self-examination, and stewardship over moral superiority.",
                "End with an uplifting message of hope, reconciliation, and quiet purpose.",
            ),
            hook_formulas=(
                "The Parable of the Talents explained: what a 2,000-year-old story reveals about fear.",
                "Why forgiving someone who hurt you is the only way to set yourself free.",
                "The Prodigal Son: why both brothers missed the father's heart.",
                "5 timeless lessons on wealth and humility from the Book of Proverbs.",
            ),
            avoid=("Sectarian doctrinal attacks", "Doomsday condemnation or fear-based messaging", "Twisting ancient texts out of context"),
            short_spec=_short((35, 50), "Has this parable spoken to your journey today? Let us know below."),
            long_spec=_long((480, 720), "Discover more timeless biblical wisdom on Parable & Lamp on YouTube."),
            visual=VisualIdentity(
                profile_id="ch_en_parable_woodcut",
                label="Carved woodblock parable print: BibleProject linocut relief, radiant oil-lamp gold, ancient parchment",
                style_description=(
                    "Expressive BibleProject-inspired 2D carved woodblock and linocut parable print on aged parchment canvas "
                    "(#EFE4C8 aged parchment, #1E1E1E bold carved woodcut ink, #D9A520 glowing lamp gold, #5E7D3A olive-leaf green, #A44A3F Galilean terracotta); "
                    "textured relief gouge lines, radiant lamps, olive trees and timeless architectural arches; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Warm woodcut human parable narrator in ancient woven cloak holding a radiant golden clay oil lamp and olive branch",
                outfit="Hand-carved Galilean terracotta tunic draped under a woven ochre mantle, no modern garments",
                palette=("#EFE4C8", "#1E1E1E", "#D9A520", "#5E7D3A", "#A44A3F"),
                thumbnail_rule="Woodcut narrator holding radiant oil lamp in dark courtyard + 2-4 uppercase words.",
            ),
            references=(
                ReferenceChannel("BibleProject", "YouTube", "long", "Literary analysis and visual theology of biblical narratives."),
                ReferenceChannel("IMBeggar", "YouTube", "long", "Poetic, hand-drawn reflections on forgiveness, humility, and grace."),
                ReferenceChannel("Ascension Presents", "YouTube", "long", "Practical life wisdom derived from timeless moral scriptures."),
                ReferenceChannel("BibleProject Shorts", "YouTube Shorts", "short", "60-second word studies and visual parable summaries."),
            ),
            seed_topics=(
                "The Parable of the Talents Explained: What a 2,000-Year-Old Story Reveals About Fear",
                "Why Forgiving Someone Who Hurt You Is the Only Way to Set Yourself Free",
                "The Prodigal Son: Why Both Brothers Missed the Father's Heart",
                "5 Timeless Lessons on Wealth and Humility from the Book of Proverbs",
                "The Good Samaritan: Why Compassion Always Crosses Invisible Boundaries",
            ),
            hashtags=("#parables", "#wisdom", "#hope", "#faith", "#proverbs", "#forgiveness"),
            monetization=("YouTube AdSense (long)", "Illustrated proverb study cards", "Christian literature and family audiobooks partner"),
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
                notes="Remotion warm lamp glow overlays and parchment scroll unroll animations.",
            ),
            engagement=EngagementSpec(
                cta_voice="Gracious parable storyteller",
                bridge_templates=(
                    "Watch the complete Parable of the Talents breakdown on Parable & Lamp YouTube.",
                    "See all five lessons on wisdom and grace on our main YouTube channel.",
                ),
                close_templates=(
                    "May this reminder bring peace, forgiveness, and renewal to your week ahead.",
                    "Share this timeless story with someone who needs a word of encouragement.",
                ),
                endcard_text="FULL VIDEO ON YOUTUBE",
                banned_cta_phrases=ALL_BANNED_CTA_PHRASES,
            ),
            extra={"handle_candidates": ["@ParableAndLamp", "@ParableAndLampHQ", "@ParableLampDoodle", "@TheParableLamp"]},
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
                label="Twilight Stoic-Taoist gouache: deep slate-indigo canvas, warm marble ivory, celadon bamboo, golden crescent moon",
                style_description=(
                    "Tranquil 2D flat midnight gouache and classical ink bedtime illustration on deep twilight slate-indigo canvas "
                    "(#1D2D44 deep twilight slate-indigo canvas, #F0EBD8 warm marble ivory, #84A98C bamboo celadon, #E9C46A warm lantern gold, #748CAB misty mountain blue); "
                    "soft matte gouache silhouettes, tranquil bamboo groves, classical marble colonnades and moonlit water; "
                    "orthographic 2D, at least 60% negative space, zero 3D, zero gradients."
                ),
                cast_appearance="Calm philosopher traveler painted in soft flat gouache wearing a draped ivory-and-slate cloak standing peacefully between a classical marble column and swaying celadon bamboo under a golden crescent moon",
                outfit="Flowing flat ivory-and-slate philosopher cloak with clean soft edges, no modern details",
                palette=("#1D2D44", "#F0EBD8", "#84A98C", "#E9C46A", "#748CAB"),
                thumbnail_rule="Philosopher traveler looking at golden moon between bamboo and marble + 2-4 uppercase words.",
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
    found = channels().get(key)
    if found is None:
        raise ValueError(f"Unknown channel '{key}'. Allowed: {sorted(channels())}")
    return found


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
    # 2. noir_dossier (5 channels)
    "ho_so_ky_la": {"id": "noir_dossier", "label": "2. 2D Noir & Red-String Dossier"},
    "luat_ngam": {"id": "noir_dossier", "label": "2. 2D Noir & Red-String Dossier"},
    "en_crowd_strings": {"id": "noir_dossier", "label": "2. 2D Noir & Red-String Dossier"},
    "en_ego_unmasked": {"id": "noir_dossier", "label": "2. 2D Noir & Red-String Dossier"},
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
    return dict(ARCHETYPE_MAP.get(channel_id, {"id": "unknown", "label": "Unknown Archetype"}))


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
