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
    speed_optimization: Optional[SpeedOptimizationSpec] = None
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
            wave=2,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="flow_full_frame",
                fast_short_max_images=8,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.25,
                estimated_short_minutes=(10, 14),
                estimated_bundle_minutes=(40, 50),
                notes="Invest full Dong Ho artwork into YouTube Long, then extract 4 cliffhanger TikTok Shorts via omni_platform (0 extra images).",
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
            wave=2,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=6,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.40,
                estimated_short_minutes=(7, 11),
                estimated_bundle_minutes=(32, 42),
                notes="Use based_on in-place facial expression variations for Tũn & Mây dialogue pairs + Remotion wrong/right reply cards.",
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
            wave=2,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="hybrid_motion",
                fast_short_max_images=6,
                spinoff_shorts_per_long=4,
                remotion_motion_ratio=0.40,
                estimated_short_minutes=(7, 10),
                estimated_bundle_minutes=(30, 40),
                notes="Fixed 4 organ mascots (Tim, Dạ Dày, Gan, Não) + Remotion timeline timers ('Sau 15 phút...', 'Sau 2 giờ...').",
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
            wave=2,
            speed_optimization=SpeedOptimizationSpec(
                render_mode="screen_capture_hybrid",
                fast_short_max_images=4,
                spinoff_shorts_per_long=5,
                remotion_motion_ratio=0.60,
                estimated_short_minutes=(5, 8),
                estimated_bundle_minutes=(25, 35),
                notes="Fastest channel: 60% scenes are Remotion prompt terminal cards or screen_capture; only 3-4 Flow doodle images per short.",
            ),
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
