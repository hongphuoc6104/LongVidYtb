#!/usr/bin/env python3
"""Batch 3 Storyboard & Script Generator for ua_sao_vay and su_ke_lai.

Authors complete Schema 3.0 packages:
1. ua-sao-vay-batch3-16x9 (Long 16:9)
2. ua-sao-vay-batch3-9x16 (Short 9:16)
3. su-ke-lai-batch3-16x9 (Long 16:9)
4. su-ke-lai-batch3-9x16 (Short 9:16)
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if p not in sys.path:
        sys.path.insert(0, p)

from channel_production_common import compile_channel_scene_prompt  # noqa: E402
from channels.registry import (  # noqa: E402
    apply_channel,
    channel_cast,
    channel_profile_stamp,
    get_channel,
)
from content.research_story_architect import compute_brief_hash  # noqa: E402


def build_ua_sao_vay_data() -> tuple[dict, dict, dict, dict, dict, dict, dict, dict]:
    """Build all 4 files for ua-sao-vay-batch3-16x9 and ua-sao-vay-batch3-9x16."""
    ch = get_channel("ua_sao_vay")
    cast = channel_cast("ua_sao_vay", "CH01")
    stamp = channel_profile_stamp("ua_sao_vay")

    # -------------------------------------------------------------
    # 1. ua-sao-vay-batch3-9x16 (Short)
    # -------------------------------------------------------------
    short_topic = "Ủa Sao Mình Không Thể Tự Cù Lét Chính Mình Được Vậy?"
    short_title = "Ủa Sao Mình Không Thể Tự Cù Lét Chính Mình Được Vậy?"
    short_scenes_data = [
        {
            "id": "SC01",
            "title": "Cú sốc không thể tự làm mình nhột",
            "purpose": "Đặt ra bài kiểm tra trực tiếp trên cơ thể người xem",
            "narrative_situation": "hook_shock",
            "narrative_phase": "lived_friction",
            "narration": "Thử tự thọc ngón tay vào nách xem, có nhột tí nào không? Chắc chắn không. Nhưng người khác khẽ chạm nhẹ, bạn đã giật nảy mình cười sặc sụa.",
            "action": "Bé Ủa mascot poking its own lemon-yellow side with stubby fingers looking utterly unamused.",
            "setting": "Cozy living room studio with colorful cartoon pillows on pastel mint canvas #DFF7F4.",
            "camera": "Semantic camera: establishing full_scene transitioning to zoom-in focus on stubby fingers",
            "beats": [
                {
                    "id": "SC01_B1",
                    "quote": "Thử tự thọc ngón tay vào nách xem, có nhột tí nào không?",
                    "tempo": "burst",
                    "situation": "hook_shock",
                    "intent": "establish",
                    "shot": "full_scene",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: Bé Ủa mascot, a round lemon-yellow #FFD23F blob with wide open mouth and a question-mark antenna, poking its own side with stubby fingers with a confused expression on flat pastel mint canvas #DFF7F4, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. Bé Ủa wiggles stubby fingers trying to poke its own round side with huge wide open eyes, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC01_B2",
                    "quote": "Chắc chắn không.",
                    "tempo": "burst",
                    "situation": "hook_shock",
                    "intent": "focus",
                    "shot": "close_up",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: Close-up of Bé Ủa's lemon-yellow #FFD23F tummy remaining totally unreactive with a deadpan flat dot-eye expression and a bold red question mark sticker above on flat pastel mint canvas #DFF7F4, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. A flat deadpan expression settles on Bé Ủa's face as comic question marks pop up around its head, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC01_B3",
                    "quote": "Nhưng người khác khẽ chạm nhẹ,",
                    "tempo": "fast",
                    "situation": "hook_shock",
                    "intent": "pan",
                    "shot": "medium_shot",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: A playful second cartoon hand with coral #FF6B6B glove sneaking in from the edge to tickle Bé Ủa's side with electric comic vibration lines on flat pastel mint canvas #DFF7F4, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. A mystery gloved hand sneaks into frame and gently wiggles toward Bé Ủa, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC01_B4",
                    "quote": "bạn đã giật nảy mình cười sặc sụa.",
                    "tempo": "fast",
                    "situation": "hook_shock",
                    "intent": "focus",
                    "shot": "full_scene",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: Bé Ủa leaping up in mid-air laughing hysterically with squiggly tears of joy and bright yellow sparkle bursts on flat pastel mint canvas #DFF7F4, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. Bé Ủa bounces into the air laughing with tear drops flying from large oval eyes, silent visual storytelling, no talking, no lip movement",
                },
            ],
        },
        {
            "id": "SC02",
            "title": "Bóc trần bản sao vận động của tiểu não",
            "purpose": "Chỉ ra cơ chế tiểu não gửi bản sao hiệu lệnh vận động",
            "narrative_situation": "mechanism_step",
            "narrative_phase": "empirical_conflict",
            "narration": "Thủ phạm đứng sau trò đùa này là tiểu não. Khi tay bạn cử động, não lập tức phát bản sao hiệu lệnh báo trước điểm chạm.",
            "action": "Bé Ủa wearing oversized cartoon professor glasses pointing at a glowing pink brain cross-section.",
            "setting": "Cute cognitive laboratory with beaker stickers on pastel yellow background #FFF6D6.",
            "camera": "Semantic camera: medium_shot tracking to glowing brain cerebellum",
            "beats": [
                {
                    "id": "SC02_B1",
                    "quote": "Thủ phạm đứng sau trò đùa này là tiểu não.",
                    "tempo": "normal",
                    "situation": "mechanism_step",
                    "intent": "establish",
                    "shot": "medium_shot",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: Bé Ủa wearing round turquoise #2EC4B6 glasses holding a magnifying glass aimed at an adorable smiling pink brain diagram on flat pastel yellow canvas #FFF6D6, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. Bé Ủa raises a comic magnifying glass illuminating the back region of a cute stylized cartoon brain, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC02_B2",
                    "quote": "Khi tay bạn cử động,",
                    "tempo": "fast",
                    "situation": "mechanism_step",
                    "intent": "focus",
                    "shot": "close_up",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: Stylized cartoon neuron pathway with electric grape #7B2CBF lightning pulses flashing along a curved axon sticker on flat pastel yellow canvas #FFF6D6, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. Saturated purple comic lightning pulses zip along the nerve track toward a tiny stickman hand, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC02_B3",
                    "quote": "não lập tức phát bản sao hiệu lệnh",
                    "tempo": "normal",
                    "situation": "mechanism_step",
                    "intent": "pan",
                    "shot": "medium_shot",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: The cerebellum illustrated as a cute robot dispatcher stamping a glowing carbon-copy paper badge marked COPY on flat pastel yellow canvas #FFF6D6, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. A miniature mechanical stamper comes down pressing a bright sticker badge onto a telegram sheet, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC02_B4",
                    "quote": "báo trước điểm chạm.",
                    "tempo": "fast",
                    "situation": "mechanism_step",
                    "intent": "focus",
                    "shot": "close_up",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: A glowing red bullseye target sticker locking onto Bé Ủa's flank with predictive coordinate grids on flat pastel yellow canvas #FFF6D6, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. The red circular radar crosshair blinks and snaps into place on Bé Ủa's side, silent visual storytelling, no talking, no lip movement",
                },
            ],
        },
        {
            "id": "SC03",
            "title": "Lời bình sâu sắc về bộ lọc sinh tồn",
            "purpose": "Bình luận sắc bén về vai trò dập tắt cảm giác thừa thãi để bảo vệ sinh tồn",
            "narrative_situation": "editorial_commentary",
            "narrative_phase": "structural_model",
            "narration": "Lệnh triệt tiêu xúc giác dập tắt tín hiệu tức thì. Nếu không có bộ lọc này, bạn sẽ phát điên mỗi khi chớp mắt hay bước đi.",
            "action": "Bé Ủa walking calmly through a storm of noisy cartoon sensory letters with a protective glowing bubble.",
            "setting": "Minimalist sensory control room with soundproof foam pattern on flat pastel canvas.",
            "camera": "Semantic camera: slow tracking shot following Bé Ủa through sensory shield",
            "beats": [
                {
                    "id": "SC03_B1",
                    "quote": "Lệnh triệt tiêu xúc giác dập tắt tín hiệu tức thì.",
                    "tempo": "slow",
                    "situation": "editorial_commentary",
                    "intent": "establish",
                    "shot": "full_scene",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: A large cartoon sound-wave volume slider dropping down to complete mute with zero dB indicator beside Bé Ủa on flat pastel mint canvas #DFF7F4, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. The cartoon volume slider glides downward snapping into a blue mute button icon, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC03_B2",
                    "quote": "Nếu không có bộ lọc này,",
                    "tempo": "slow",
                    "situation": "editorial_commentary",
                    "intent": "focus",
                    "shot": "medium_shot",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: Bé Ủa looking overwhelmed with dizzy spiral eyes as thousands of chaotic sensory sparkles swarm around on flat pastel mint canvas #DFF7F4, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. Swarms of tiny buzzing sensory dots swirl around Bé Ủa as its eyes spin with comic dizziness, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC03_B3",
                    "quote": "bạn sẽ phát điên mỗi khi chớp mắt",
                    "tempo": "normal",
                    "situation": "editorial_commentary",
                    "intent": "pan",
                    "shot": "close_up",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: Extreme close-up of a giant blinking cartoon eye sticker with loud comic sound-effect letters BOOM on each blink on flat pastel yellow canvas #FFF6D6, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. The big cartoon eye blinks slowly while impact vibration rings radiate outward, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC03_B4",
                    "quote": "hay bước đi.",
                    "tempo": "slow",
                    "situation": "editorial_commentary",
                    "intent": "focus",
                    "shot": "medium_shot",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: Bé Ủa marching with tiny cartoon boots producing colorful rhythmic puff clouds on a clean path on flat pastel mint canvas #DFF7F4, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. Bé Ủa marches forward steadily as small dust puffs pop underfoot in a steady calm rhythm, silent visual storytelling, no talking, no lip movement",
                },
            ],
        },
        {
            "id": "SC04",
            "title": "Đánh lừa não bằng cánh tay robot trễ thời gian",
            "purpose": "Chứng minh qua thí nghiệm cánh tay robot có độ trễ",
            "narrative_situation": "mechanism_step",
            "narrative_phase": "structural_model",
            "narration": "Muốn tự làm mình nhột, bạn phải đánh lừa tiểu não. Khi gắn cánh tay robot trễ hai phần mười giây, người tham gia lập tức cười phá lên.",
            "action": "Bé Ủa operating a mechanical robotic lever that controls a feather duster with a digital clock counter.",
            "setting": "Robotics engineering workshop with colorful gear stickers on pastel background.",
            "camera": "Semantic camera: split contrast view between lever action and delayed feather touch",
            "beats": [
                {
                    "id": "SC04_B1",
                    "quote": "Muốn tự làm mình nhột,",
                    "tempo": "normal",
                    "situation": "before_after_contrast",
                    "intent": "establish",
                    "shot": "medium_shot",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: Bé Ủa scratching head thoughtfully beside a mechanical lever console marked TRICK THE BRAIN on flat pastel yellow canvas #FFF6D6, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. Bé Ủa taps its round chin with a stubby hand while surveying a sleek robotic gadget, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC04_B2",
                    "quote": "bạn phải đánh lừa tiểu não.",
                    "tempo": "fast",
                    "situation": "before_after_contrast",
                    "intent": "focus",
                    "shot": "close_up",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: A mischievous Bé Ủa pulling a red cartoon lever that lights up a digital stopwatch sticker on flat pastel yellow canvas #FFF6D6, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. Bé Ủa pulls the red mechanical lever downwards with a satisfying click, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC04_B3",
                    "quote": "Khi gắn cánh tay robot trễ hai phần mười giây,",
                    "tempo": "normal",
                    "situation": "mechanism_step",
                    "intent": "pan",
                    "shot": "medium_shot",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: A sleek teal #2EC4B6 robotic arm holding a feather duster hovering above Bé Ủa with a digital display glowing 200ms on flat pastel yellow canvas #FFF6D6, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. The robotic arm hovers for a split second before darting forward with the feather, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC04_B4",
                    "quote": "người tham gia lập tức cười phá lên.",
                    "tempo": "fast",
                    "situation": "mechanism_step",
                    "intent": "focus",
                    "shot": "full_scene",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: Bé Ủa bursting into helpless laughter as the delayed feather tickles its belly with coral #FF6B6B heart sparkles on flat pastel mint canvas #DFF7F4, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. Bé Ủa rolls on the floor giggling uncontrollably surrounded by pop-art heart bursts, silent visual storytelling, no talking, no lip movement",
                },
            ],
        },
        {
            "id": "SC05",
            "title": "Đỉnh cao trào bỏ lửng và chuyển phễu video dài",
            "purpose": "Tạo vòng lặp mở về ngoại lệ tâm thần và dẫn phễu về bản dài",
            "narrative_situation": "cliffhanger_peak",
            "narrative_phase": "actionable_resolution",
            "narration": "Vậy nhóm người đặc biệt nào vẫn có thể tự cù lét chính mình? Bản dài trên kênh Ủa Sao Vậy có câu trả lời đầy đủ nhé. Thả thêm thắc mắc kỳ lạ xuống dưới để Bé Ủa giải mã tiếp nghen.",
            "action": "Bé Ủa pointing at a glowing branching question portal leading to the channel endcard.",
            "setting": "Bright studio stage transition leading to channel community endcard.",
            "camera": "Semantic camera: medium_shot cliffhanger peak transitioning to full_scene outro endcard hold",
            "beats": [
                {
                    "id": "SC05_B1",
                    "quote": "Vậy nhóm người đặc biệt nào",
                    "tempo": "normal",
                    "situation": "cliffhanger_peak",
                    "intent": "establish",
                    "shot": "medium_shot",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: Bé Ủa with one stubby hand on its hip and a glowing purple silhouette sticker in the background on flat pastel mint canvas #DFF7F4, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. A mysterious shaded silhouette figure appears behind Bé Ủa with glowing question-mark eyes, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC05_B2",
                    "quote": "vẫn có thể tự cù lét chính mình?",
                    "tempo": "fast",
                    "situation": "cliffhanger_peak",
                    "intent": "focus",
                    "shot": "close_up",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: Dramatic close-up of Bé Ủa staring in awe at an intricate neural puzzle with one piece missing on flat pastel yellow canvas #FFF6D6, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. Bé Ủa gasps as a glowing puzzle piece hovers in mid-air above the brain diagram, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC05_B3",
                    "quote": "Bản dài trên kênh Ủa Sao Vậy có câu trả lời đầy đủ nhé.",
                    "tempo": "normal",
                    "situation": "cta_bridge",
                    "intent": "pan",
                    "shot": "full_scene",
                    "effect": "cut",
                    "desc": "Bold 2D sticker-pop cartoon illustration: Bé Ủa happily presenting a giant red video play button sticker framed by bold white outlines and star sparkles on flat pastel mint canvas #DFF7F4, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. Bé Ủa opens arms wide presenting a gleaming red play badge with sparkling comic stars, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC05_B4",
                    "quote": "Thả thêm thắc mắc kỳ lạ xuống dưới để Bé Ủa giải mã tiếp nghen.",
                    "tempo": "hold",
                    "situation": "cta_close",
                    "intent": "hold",
                    "shot": "full_scene",
                    "effect": "hold",
                    "is_endcard": True,
                    "desc": "Bold 2D sticker-pop cartoon illustration channel endcard: Bé Ủa waving both stubby arms warmly with a giant speech bubble reading 'ỦA SAO VẬY?' and pastel yellow background #FFF6D6, thick black outlines and chunky white border.",
                    "motion": "Smooth 2D sticker pop animation. Bé Ủa waves cheerily at the viewer as the channel logo settles into a stable endcard freeze, silent visual storytelling, no talking, no lip movement",
                },
            ],
        },
    ]

    short_brief = {
        "schema_version": "3.0",
        "topic": short_topic,
        "audience": "Khán giả đại chúng yêu thích khoa học đời sống, tò mò về cơ thể và tâm lý học",
        "goal": "Bóc trần cơ chế tiểu não triệt tiêu cảm giác tự thân và giải thích vì sao con người không thể tự cù lét chính mình",
        "video_type": "explainer",
        "duration": {"min_seconds": 35.0, "max_seconds": 50.0},
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Nghịch lý tự cù không nhột nhưng người khác chạm lại cười sặc sụa"},
            {"id": "R02", "text": "Tiểu não phát bản sao hiệu lệnh vận động báo trước điểm chạm"},
            {"id": "R03", "text": "Lệnh triệt tiêu xúc giác bảo vệ não bộ khỏi phát điên vì kích thích thừa"},
            {"id": "R04", "text": "Đánh lừa tiểu não bằng cánh tay robot trễ hai trăm mili giây"},
            {"id": "R05", "text": "Đỉnh cao trào bỏ lửng về nhóm người đặc biệt và chuyển phễu video dài"},
        ],
        "language": "vi",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "9:16",
        "format_profile": "short_9x16",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Central cancellation of self-produced tickle sensation",
                "reference": "Blakemore, S. J., Wolpert, D. M., & Frith, C. D. (1998). Nature Neuroscience, 1(7), 635-640.",
                "facts": [
                    "Tiểu não gửi tín hiệu triệt tiêu cảm giác dựa trên bản sao hiệu lệnh vận động.",
                    "Độ trễ cơ học trên một trăm mili giây khiến não không kịp ức chế và gây nhột trở lại.",
                ],
            }
        ],
        "outputs": [{"aspect_ratio": "9:16", "language": "vi", "subtitles": True, "voice": ch.voice, "speed": ch.speed}],
        "planning": {
            "success_criteria": [
                "Giải thích rõ ràng cơ chế bản sao vận động của tiểu não trong 45 giây bằng phong cách sticker pop",
                "Đạt tỷ lệ giữ chân cao với cú hích nghịch lý ban đầu và chuyển phễu mượt mà về bản dài",
            ],
            "avoid": ["Tránh dùng thuật ngữ y khoa khô khan mà không có ví dụ trực quan sinh động."],
            "prior_knowledge": "Không đòi hỏi kiến thức y sinh học chuyên sâu từ trước.",
            "pacing": "Nhanh, dồn dập, hài kiểu Gen Z, có twist cuối.",
            "domain_requirements": [],
            "assumptions": ["Mỗi phân cảnh được cân chỉnh theo công thức âm học P_tail và dung sai drift <= 0.3s."],
            "text_style": {
                "font": "sans-serif rõ nét, cùng kiểu và độ đậm xuyên suốt",
                "color": "#172033",
                "outline": "nền sáng tương phản",
                "size": "dễ đọc trên điện thoại (khung dọc 9:16)",
                "placement": "cách mép ít nhất 10%; tránh mặt và vùng phụ đề dưới cùng 18%",
            },
            "speech_rates": {
                "vi": {"units_per_second": 4.0, "uncertainty": 0.15, "source": "Acoustic calibrated cadence"},
                "en": {"units_per_second": 2.5, "uncertainty": 0.25, "source": "Estimated English reading rate"},
            },
        },
        "packaging": {
            "youtube_title": short_title,
            "thumbnail_spec": {
                "visual_hook": "Bé Ủa mắt tròn xoe há hốc mồm tự cù eo mình không nhột đối lập với robot cù trễ 200ms cười sặc sụa",
                "text_overlay": "ỦA SAO KHÔNG NHỘT?",
                "contrast_pair": "Tự thọc nách trơ như đá vs Robot cù trễ cười nắc nẻ",
                "thumbnail_prompt": "Bold 2D sticker-pop cartoon illustration: Mascot 'Bé Ủa', a round lemon-yellow (#FFD23F) blob creature with huge white oval eyes, tiny black pupils, wide open mouth and question-mark antenna, poking its own flank with stubby fingers looking confused with a giant red question mark sticker. On the other side, a robotic feather duster with a glowing digital display 200ms making Bé Ủa laugh with joy tears. Thick smooth black outlines with chunky white border on pastel mint background (#DFF7F4), large bold hand-lettered sticker text in upper third: 'ỦA SAO KHÔNG NHỘT?'. No realistic gradients, orthographic 2D.",
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Khoa Học Đời Sống & Nhận Thức Kỳ Thú",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["ua sao vay", "tu cu let", "vi sao khong nhot", "tieu nao", "khoa hoc vui", "shorts"],
            "cta_plan": {
                "cliffhanger_peak": "Vậy nhóm người đặc biệt nào trên thế giới vẫn có thể tự cù lét chính mình?",
                "bridge": "Bản dài trên kênh Ủa Sao Vậy có câu trả lời đầy đủ nhé.",
                "close": "Thả thêm thắc mắc kỳ lạ xuống dưới để Bé Ủa giải mã tiếp nghen.",
                "endcard_text": "ỦA SAO VẬY?",
            },
            "editorial_stance": {
                "myth_debunked": "Bạn không nhột vì tay mình chai lì hoặc do tâm lý biết trước vị trí chạm.",
                "why_generic_advice_fails": "Lời giải thích tâm lý chung chung bỏ qua mạng lưới dự đoán chuyển động tinh vi của tiểu não.",
                "channel_verdict": "Bộ não là hệ thống lọc tín hiệu tàn nhẫn, luôn chủ động xóa sạch mọi cảm giác do chính bạn tự tạo ra.",
                "tradeoff_or_blindspot": "Cơ chế dập cảm giác giúp bạn không phát điên vì quần áo, nhưng tước đi niềm vui tự làm mình cười.",
            },
            "actionable_value": {
                "core_mechanism": "Tiểu não phát bản sao vận động triệt tiêu xúc giác ngay trước khi ngón tay kịp chạm vào cơ thể.",
                "practical_rule_of_thumb": "Muốn tự cù lét, bạn phải dùng công cụ tạo độ trễ trên hai trăm mili giây để đánh lừa tiểu não.",
                "real_world_scenario": "Thí nghiệm robot cù lét có cần gạt trễ thời gian giúp các nhà khoa học chứng minh sai số dự đoán tạo ra tiếng cười.",
            },
        },
        "youtube_title": short_title,
        "thumbnail_spec": {
            "visual_hook": "Bé Ủa mắt tròn xoe há hốc mồm tự cù eo mình không nhột đối lập với robot cù trễ 200ms cười sặc sụa",
            "text_overlay": "ỦA SAO KHÔNG NHỘT?",
            "contrast_pair": "Tự thọc nách trơ như đá vs Robot cù trễ cười nắc nẻ",
            "thumbnail_prompt": "Bold 2D sticker-pop cartoon illustration: Mascot 'Bé Ủa', a round lemon-yellow (#FFD23F) blob creature with huge white oval eyes, tiny black pupils, wide open mouth and question-mark antenna, poking its own flank with stubby fingers looking confused with a giant red question mark sticker. On the other side, a robotic feather duster with a glowing digital display 200ms making Bé Ủa laugh with joy tears. Thick smooth black outlines with chunky white border on pastel mint background (#DFF7F4), large bold hand-lettered sticker text in upper third: 'ỦA SAO KHÔNG NHỘT?'. No realistic gradients, orthographic 2D.",
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Khoa Học Đời Sống & Nhận Thức Kỳ Thú",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["ua sao vay", "tu cu let", "vi sao khong nhot", "tieu nao", "khoa hoc vui", "shorts"],
        "parent_long_id": "ua-sao-vay-batch3-16x9",
        "cta_plan": {
            "cliffhanger_peak": "Vậy nhóm người đặc biệt nào trên thế giới vẫn có thể tự cù lét chính mình?",
            "bridge": "Bản dài trên kênh Ủa Sao Vậy có câu trả lời đầy đủ nhé.",
            "close": "Thả thêm thắc mắc kỳ lạ xuống dưới để Bé Ủa giải mã tiếp nghen.",
            "endcard_text": "ỦA SAO VẬY?",
        },
        "channel_profile": stamp,
        "engagement": asdict(ch.engagement),
        "editorial_stance": {
            "myth_debunked": "Bạn không nhột vì tay mình chai lì hoặc do tâm lý biết trước vị trí chạm.",
            "why_generic_advice_fails": "Lời giải thích tâm lý chung chung bỏ qua mạng lưới dự đoán chuyển động tinh vi của tiểu não.",
            "channel_verdict": "Bộ não là hệ thống lọc tín hiệu tàn nhẫn, luôn chủ động xóa sạch mọi cảm giác do chính bạn tự tạo ra.",
            "tradeoff_or_blindspot": "Cơ chế dập cảm giác giúp bạn không phát điên vì quần áo, nhưng tước đi niềm vui tự làm mình cười.",
        },
        "actionable_value": {
            "core_mechanism": "Tiểu não phát bản sao vận động triệt tiêu xúc giác ngay trước khi ngón tay kịp chạm vào cơ thể.",
            "practical_rule_of_thumb": "Muốn tự cù lét, bạn phải dùng công cụ tạo độ trễ trên hai trăm mili giây để đánh lừa tiểu não.",
            "real_world_scenario": "Thí nghiệm robot cù lét có cần gạt trễ thời gian giúp các nhà khoa học chứng minh sai số dự đoán tạo ra tiếng cười.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }

    content_scenes_short = []
    outline_short = []
    for s_idx, s in enumerate(short_scenes_data):
        sc_id = s["id"]
        outline_short.append({
            "scene_id": sc_id,
            "purpose": s["purpose"],
            "requirements": [f"R{s_idx+1:02d}"],
            "transition": "Tiếp tục theo trình tự diễn biến nội dung",
        })
        sc_images = []
        sc_beats = []
        for b_idx, b in enumerate(s["beats"]):
            img_id = f"{sc_id}_I{b_idx+1}"
            beat_id = f"{sc_id}_B{b_idx+1}"
            sc_images.append({
                "id": img_id,
                "description": b["desc"],
                "character_ids": ["CH01"],
                "preserve": "lemon-yellow mascot Bé Ủa, chunky white sticker border, pastel background, 2D sticker pop style",
                "change": b["desc"][:80],
                "reason": "Narration-locked full-frame beat.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": b["shot"],
                "tempo": b["tempo"],
                "narrative_situation": b["situation"],
                "emphasis_text": "",
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": True,
                "explanation": {
                    "quote": b["quote"],
                    "relation": "context",
                    "source_terms": ["tiểu não", "nhột"],
                    "visual_terms": ["sticker", "cartoon"],
                },
                "motion_prompt": b["motion"],
            })
            sc_beats.append({
                "id": beat_id,
                "image_id": img_id,
                "purpose": s["purpose"],
                "anchor": {"vi": {"quote": b["quote"], "occurrence": 1}},
                "effect": b["effect"],
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": b["tempo"],
                "narrative_situation": b["situation"],
                "camera_intent": b["intent"],
                "shot_type": b["shot"],
                "is_endcard": b.get("is_endcard", False),
            })

        content_scenes_short.append({
            "id": sc_id,
            "title": s["title"],
            "purpose": s["purpose"],
            "action": s["action"],
            "setting": s["setting"],
            "camera": s["camera"],
            "narration": s["narration"],
            "requirements": [f"R{s_idx+1:02d}"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "images": sc_images,
            "beats": sc_beats,
        })

    short_brief_hash = compute_brief_hash(short_brief)
    short_content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": short_brief_hash,
        "topic": short_topic,
        "duration": short_brief["duration"],
        "style": short_brief["style"],
        "required_points": short_brief["required_points"],
        "characters": [cast],
        "scenes": content_scenes_short,
        "coverage": [
            {"requirement_id": f"R{i+1:02d}", "scene_id": s["id"], "quote": s["narration"][:60]}
            for i, s in enumerate(short_scenes_data)
        ],
        "outline": outline_short,
        "claims": [
            {
                "scene_id": "SC02",
                "quote": "não lập tức phát bản sao hiệu lệnh báo trước điểm chạm",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Tiểu não gửi tín hiệu triệt tiêu cảm giác dựa trên bản sao hiệu lệnh vận động.",
            }
        ],
        "revision_response": [],
        "open_questions": [],
    }

    short_competitor = {
        "channel_id": "ua_sao_vay",
        "job_id": "ua-sao-vay-batch3-9x16",
        "topic": short_topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "AsapSCIENCE & Kurzgesagt",
                    "top_performing_videos": [
                        {
                            "title": "Why Can't You Tickle Yourself?",
                            "views": "6.8M views",
                            "hook_technique": "Khán giả thử cù chính mình ngay trong 3 giây đầu và nhận ra sự trơ lì.",
                            "pacing_structure": "Trải nghiệm tức thì -> Mô hình tiểu não dự đoán -> Thí nghiệm robot -> Kết luận sinh tồn.",
                            "retention_driver": "Trực quan hóa hoạt động nơ ron bằng hoạt họa ngộ nghĩnh nhiều màu sắc."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Kêu gọi hành động tương tác thân thể ngay lập tức tạo cảm giác tham gia thực tế.",
                        "Biến tiểu não thành nhân vật bảo vệ mẫn cán dập tắt cảm giác thừa."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 13,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Tự thọc ngón tay trơ như tượng đối lập với người khác chạm nhẹ đã giật nảy cười bò.",
                "counter_intuitive_truth_slap": "Không phải bạn chai lì cảm xúc, não bộ đã chủ động xóa sạch cảm giác từ trước khi tay chạm da."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Khởi đầu bằng thách thức tự cù nách trơ như đá."},
                {"phase": "empirical_conflict", "purpose": "Vạch trần bản sao vận động của tiểu não."},
                {"phase": "structural_model", "purpose": "Giải thích vai trò bộ lọc bảo vệ sự tỉnh táo."},
                {"phase": "actionable_resolution", "purpose": "Thí nghiệm robot tạo độ trễ và dẫn phễu video dài."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Sequential daisy-chain linking Start Frame to End Frame across all scenes."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Khoa Học Đời Sống & Nhận Thức Kỳ Thú",
            "myth_debunked": "Bạn không nhột vì tay mình chai lì hoặc do tâm lý biết trước vị trí chạm.",
            "channel_verdict": "Bộ não là hệ thống lọc tín hiệu tàn nhẫn, luôn chủ động xóa sạch mọi cảm giác do chính bạn tự tạo ra.",
            "actionable_rule_of_thumb": "Muốn tự cù lét, bạn phải dùng công cụ tạo độ trễ trên hai trăm mili giây để đánh lừa tiểu não."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "Vậy nhóm người đặc biệt nào trên thế giới vẫn có thể tự cù lét chính mình?",
            "bridge": "Bản dài trên kênh Ủa Sao Vậy có câu trả lời đầy đủ nhé.",
            "close": "Thả thêm thắc mắc kỳ lạ xuống dưới để Bé Ủa giải mã tiếp nghen.",
            "endcard_text": "ỦA SAO VẬY?"
        }
    }

    # -------------------------------------------------------------
    # 2. ua-sao-vay-batch3-16x9 (Long)
    # -------------------------------------------------------------
    long_topic = "Giải Mã Cơ Chế Thần Kinh: Vì Sao Bạn Không Thể Tự Cù Lét Chính Mình?"
    long_title = "Vì Sao Bạn Không Thể Tự Cù Lét Chính Mình?"
    long_scenes_data = [
        {
            "id": "SC01",
            "title": "Lời thách thức mở đầu và cảm giác kỳ quặc",
            "purpose": "Đặt ra bài kiểm tra trực tiếp trên cơ thể người xem",
            "narrative_situation": "hook_cold_open",
            "narrative_phase": "lived_friction",
            "setting": "Bright sticker-pop living room with colorful cartoon sofa on pastel yellow canvas #FFF6D6.",
            "narration": "Thử đưa ngón tay cù vào mạng sườn hoặc lòng bàn chân xem. Hoàn toàn trơ như đá. Bạn không hề thấy nhột, dù cố tình chọc mạnh hay đổi hướng bất ngờ. Nhưng chỉ cần đứa bạn chạm nhẹ đúng chỗ đó, bạn đã co rúm người cười sặc sụa. Chuyện gì đang xảy ra trong đầu bạn vậy?",
            "beats": [
                ("Thử đưa ngón tay cù vào mạng sườn hoặc lòng bàn chân xem.", "burst", "hook_cold_open", "establish", "full_scene", "Bé Ủa with questioning look attempting to tickle its own side on pastel mint canvas"),
                ("Hoàn toàn trơ như đá.", "burst", "hook_cold_open", "focus", "close_up", "Close up on Bé Ủa inspecting its flat lemon-yellow foot with dot eyes"),
                ("Bạn không hề thấy nhột, dù cố tình chọc mạnh hay đổi hướng bất ngờ.", "fast", "hook_cold_open", "focus", "medium_shot", "Bé Ủa turning stone-faced with comic rock textures overlaid on lemon-yellow body"),
                ("Nhưng chỉ cần đứa bạn chạm nhẹ đúng chỗ đó,", "fast", "hook_cold_open", "pan", "medium_shot", "Bé Ủa rapidly poking its flank from different comic angles with zigzag motion lines"),
                ("bạn đã co rúm người cười sặc sụa.", "normal", "hook_cold_open", "pan", "full_scene", "A playful cartoon friend hand tickling Bé Ủa causing it to coil up laughing in mid-air"),
                ("Chuyện gì đang xảy ra trong đầu bạn vậy?", "fast", "hook_cold_open", "focus", "close_up", "Bé Ủa staring directly at camera with antenna pulsing in bright question mark sparkles"),
            ],
        },
        {
            "id": "SC02",
            "title": "Trực giác sai lầm và lời giải thích thông thường",
            "purpose": "Bác bỏ các giả thuyết dân gian thiếu căn cứ khoa học",
            "narrative_situation": "mechanism_reveal",
            "narrative_phase": "lived_friction",
            "setting": "Cozy cartoon library corner with folklore scroll shelves on pastel canvas.",
            "narration": "Nhiều người nghĩ ngón tay không đủ nhạy, hoặc da tay quen thân nhiệt. Số khác tin rằng vì mắt thấy tay đưa tới nên tâm lý tự phòng bị. Những suy đoán đó nghe có vẻ hợp lý nhưng khoa học chứng minh đều sai. Kể cả khi nhắm mắt và tự cầm que gỗ chọc, bạn vẫn không thấy buồn.",
            "beats": [
                ("Nhiều người nghĩ ngón tay không đủ nhạy, hoặc da tay quen thân nhiệt.", "fast", "mechanism_reveal", "establish", "medium_shot", "Bé Ủa examining a giant cartoon fingerprint under magnifying glass with question marks"),
                ("Số khác tin rằng vì mắt thấy tay đưa tới nên tâm lý tự phòng bị.", "normal", "mechanism_reveal", "focus", "close_up", "A cute cartoon thermometer sticker registering warm body heat beside Bé Ủa"),
                ("Những suy đoán đó nghe có vẻ hợp lý nhưng khoa học chứng minh đều sai.", "normal", "mechanism_reveal", "pan", "medium_shot", "Bé Ủa wearing a blindfold trying to sneak up on its own shadow"),
                ("Kể cả khi nhắm mắt", "normal", "mechanism_reveal", "focus", "full_scene", "A big bright red sticker X stamping over ancient scroll drawings of misconceptions"),
                ("và tự cầm que gỗ chọc,", "fast", "mechanism_reveal", "pan", "medium_shot", "Bé Ủa holding a wooden stick while wearing sleep goggles in laboratory"),
                ("bạn vẫn không thấy buồn.", "normal", "mechanism_reveal", "focus", "close_up", "Bé Ủa holding the wooden wand against side with unblinking deadpan expression"),
            ],
        },
        {
            "id": "SC03",
            "title": "Nhạc trưởng tiểu não và bản sao hiệu lệnh",
            "purpose": "Giới thiệu tiểu não và khái niệm efference copy",
            "narrative_situation": "mechanism_step",
            "narrative_phase": "empirical_conflict",
            "setting": "High-tech cognitive laboratory backdrop with glowing brain diagrams and beaker stickers.",
            "narration": "Thủ phạm đứng sau hiện tượng trớ trêu này là tiểu não, nằm ngay sau gáy. Mỗi khi bạn quyết định cử động ngón tay, vỏ não vận động gửi hai tín hiệu cùng lúc. Tín hiệu thứ nhất truyền xuống cánh tay co cơ. Tín hiệu thứ hai, gọi là bản sao vận động, gửi sang tiểu não để báo trước tương lai.",
            "beats": [
                ("Thủ phạm đứng sau hiện tượng trớ trêu này là tiểu não, nằm ngay sau gáy.", "normal", "mechanism_step", "establish", "medium_shot", "Bé Ủa pointing proudly at the back of a stylized pastel purple cartoon brain diagram"),
                ("Mỗi khi bạn quyết định cử động ngón tay,", "fast", "mechanism_step", "focus", "close_up", "Motor cortex depicted as a miniature control switchboard with sparking turquoise buttons"),
                ("vỏ não vận động gửi hai tín hiệu cùng lúc.", "normal", "mechanism_step", "pan", "medium_shot", "Two branching electric arrows radiating outwards from brain motor center"),
                ("Tín hiệu thứ nhất truyền xuống cánh tay co cơ.", "fast", "mechanism_step", "pan", "full_scene", "An electric blue arrow traveling down a stylized arm muscle diagram"),
                ("Tín hiệu thứ hai, gọi là bản sao vận động,", "normal", "mechanism_step", "focus", "close_up", "A glowing golden stamped document marked EFFERENCE COPY appearing in cerebellum"),
                ("gửi sang tiểu não để báo trước tương lai.", "normal", "mechanism_step", "focus", "medium_shot", "Cerebellum robot wearing oracle crystal sunglasses reading future coordinates"),
            ],
        },
        {
            "id": "SC04",
            "title": "Mô hình dự đoán và lệnh triệt tiêu xúc giác",
            "purpose": "Phân tích cách tiểu não tính toán và dập tắt cảm giác",
            "narrative_situation": "solution_framework",
            "narrative_phase": "empirical_conflict",
            "setting": "Digital neural observatory monitoring sensory impulse flows on pastel turquoise walls.",
            "narration": "Dựa vào bản sao này, tiểu não tính toán vị trí, áp lực và thời điểm chạm da. Trước khi bạn kịp cảm nhận, nó gửi lệnh ức chế đến vỏ não cảm giác thân thể. Lệnh này hạ thấp độ nhạy vùng da chạm, dập tắt mọi cảm giác thừa. Não bộ chủ động bóp nghẹt kích thích trước khi nó kịp truyền về.",
            "beats": [
                ("Dựa vào bản sao này, tiểu não tính toán vị trí, áp lực và thời điểm chạm da.", "normal", "solution_framework", "establish", "medium_shot", "Cerebellum computing coordinates on a holographic radar grid displaying flank zones"),
                ("Trước khi bạn kịp cảm nhận,", "fast", "solution_framework", "focus", "close_up", "Digital pressure gauge measuring exact tactile force in comic millinewtons"),
                ("nó gửi lệnh ức chế đến vỏ não cảm giác thân thể.", "normal", "solution_framework", "pan", "medium_shot", "A stop sign shield flying from cerebellum to block incoming sensation pathways"),
                ("Lệnh này hạ thấp độ nhạy vùng da chạm,", "normal", "solution_framework", "focus", "close_up", "Skin surface receptors turning from alert red bells to asleep grey pillows"),
                ("dập tắt mọi cảm giác thừa.", "fast", "solution_framework", "pan", "full_scene", "A big comic broom sweeping away noisy tactile spark dots on pastel mint canvas"),
                ("Não bộ chủ động bóp nghẹt kích thích trước khi nó kịp truyền về.", "normal", "solution_framework", "focus", "medium_shot", "Bé Ủa standing calmly behind an impenetrable sensory firewall sticker"),
            ],
        },
        {
            "id": "SC05",
            "title": "Thử nghiệm thực tế và điểm dừng suy ngẫm",
            "purpose": "Mid CTA và giải thích nguyên lý sai số dự đoán gây cười",
            "narrative_situation": "mid_break_cta",
            "narrative_phase": "structural_model",
            "setting": "Interactive science studio stage with demonstration podium on pastel yellow canvas.",
            "narration": "Thử tự cù eo mình xem, bạn có nhột chút nào không? Không có bất ngờ thì không có tiếng cười. Tiếng cười khi bị cù là phản xạ sinh học kích hoạt khi có sai số dự đoán. Khi người khác cù, bạn không đoán trước vị trí và lực ấn, não phát tín hiệu kích động. Còn khi bạn tự làm, não hoàn toàn bình thản.",
            "beats": [
                ("Thử tự cù eo mình xem, bạn có nhột chút nào không?", "normal", "mid_break_cta", "establish", "medium_shot", "Bé Ủa with hand on hip inviting the viewer to poke themselves with a cute arrow"),
                ("Không có bất ngờ thì không có tiếng cười.", "fast", "mid_break_cta", "focus", "close_up", "A surprise gift box opening to reveal an empty flat question mark sticker"),
                ("Tiếng cười khi bị cù là phản xạ sinh học kích hoạt khi có sai số dự đoán.", "normal", "mid_break_cta", "pan", "medium_shot", "Diagram comparing prediction curve versus actual sensory impact spike"),
                ("Khi người khác cù, bạn không đoán trước vị trí và lực ấn, não phát tín hiệu kích động.", "fast", "mid_break_cta", "pan", "full_scene", "Random unpredictable comic tickle tentacles darting in playfully from all sides"),
                ("Còn khi bạn tự làm,", "normal", "mid_break_cta", "focus", "close_up", "Brain alarm bell ringing furiously with comic exclamation marks and flashes"),
                ("não hoàn toàn bình thản.", "slow", "mid_break_cta", "focus", "medium_shot", "Digital display showing PREDICTION ERROR: ZERO beside a placid smiling Bé Ủa"),
            ],
        },
        {
            "id": "SC06",
            "title": "Bình luận sắc bén: Bộ lọc bảo vệ sự tỉnh táo",
            "purpose": "Đánh giá sâu sắc vai trò sống còn của cơ chế dập tắt cảm giác",
            "narrative_situation": "editorial_commentary",
            "narrative_phase": "structural_model",
            "setting": "Minimalist philosophical study chamber with sensory filter dials on pastel mint canvas.",
            "narration": "Bộ não của bạn thực chất là một cỗ máy lọc thông tin tàn nhẫn và thực dụng. Nếu cơ thể không triệt tiêu cảm giác tự thân, cuộc sống sẽ hỗn loạn. Mỗi bước chân đi bạn giật mình vì bàn chân bị đè nén. Mỗi lần chớp mắt bạn phát điên vì mí mắt cọ vào nhãn cầu. Cơ chế dập cảm giác tự thân giữ bạn tỉnh táo.",
            "beats": [
                ("Bộ não của bạn thực chất là một cỗ máy lọc thông tin tàn nhẫn và thực dụng.", "slow", "editorial_commentary", "establish", "medium_shot", "Bé Ủa examining a heavy-duty industrial sorting funnel discarding irrelevant letters"),
                ("Nếu cơ thể không triệt tiêu cảm giác tự thân, cuộc sống sẽ hỗn loạn.", "slow", "editorial_commentary", "focus", "full_scene", "Chaotic storm of sensory sticker arrows pelting a stressed stickman in all directions"),
                ("Mỗi bước chân đi bạn giật mình vì bàn chân bị đè nén.", "normal", "editorial_commentary", "pan", "close_up", "Footstep on floor producing a blinding comic lightning explosion under the heel"),
                ("Mỗi lần chớp mắt bạn phát điên vì mí mắt cọ vào nhãn cầu.", "slow", "editorial_commentary", "focus", "close_up", "Eyeball sticker trembling nervously each time eyelids brush across its lens"),
                ("Cơ chế dập cảm giác tự thân", "normal", "editorial_commentary", "pan", "medium_shot", "A glowing turquoise translucent shield dome expanding around peaceful Bé Ủa"),
                ("giữ bạn tỉnh táo.", "slow", "editorial_commentary", "focus", "full_scene", "Bé Ủa sitting in zen meditation posture while chaotic noise bounces off shield"),
            ],
        },
        {
            "id": "SC07",
            "title": "Thí nghiệm cánh tay robot của Sarah Blakemore",
            "purpose": "Dẫn chứng nghiên cứu thực nghiệm tại University College London",
            "narrative_situation": "case_study",
            "narrative_phase": "structural_model",
            "setting": "University London robotics testing facility with mechanical arm and research charts.",
            "narration": "Giáo sư Sarah Blakemore tại Đại học London từng làm thí nghiệm kinh điển kiểm chứng cơ chế này. Bà chế tạo cánh tay robot cầm bọt biển cù vào lòng bàn tay tình nguyện viên. Khi người tham gia gạt cần và robot cù ngay, họ không thấy nhột. Nhưng khi cài độ trễ một phần mười giây giữa cú gạt và cú chạm, điều kỳ diệu xuất hiện.",
            "beats": [
                ("Giáo sư Sarah Blakemore tại Đại học London từng làm thí nghiệm kinh điển kiểm chứng cơ chế này.", "normal", "case_study", "establish", "medium_shot", "Cartoon scientist blackboard illustrating London university research credentials"),
                ("Bà chế tạo cánh tay robot cầm bọt biển cù vào lòng bàn tay tình nguyện viên.", "normal", "case_study", "pan", "full_scene", "A quirky 2D mechanical robotic arm holding a yellow sponge over a hand pad"),
                ("Khi người tham gia gạt cần và robot cù ngay, họ không thấy nhột.", "fast", "case_study", "focus", "close_up", "Volunteer hand pushing a retro arcade joystick forward in crisp cartoon style"),
                ("Nhưng khi cài độ trễ một phần mười giây giữa cú gạt và cú chạm,", "normal", "case_study", "focus", "medium_shot", "Volunteer smiling impassively with flat line mouth as sponge rubs palm directly"),
                ("điều kỳ diệu xuất hiện.", "normal", "case_study", "pan", "close_up", "Digital timer dial clicking to 100 milliseconds with glowing LED numerals"),
                ("Người tham gia lập tức thấy nhột nhẹ.", "fast", "case_study", "focus", "medium_shot", "Volunteer's eyes widening in sudden realization as a comic spark jumps up"),
            ],
        },
        {
            "id": "SC08",
            "title": "Đánh lừa tiểu não bằng độ trễ nhân tạo",
            "purpose": "Phân tích vì sao độ trễ thời gian phá vỡ mô hình dự đoán",
            "narrative_situation": "deep_dive_step",
            "narrative_phase": "structural_model",
            "setting": "Timing calibration workshop equipped with digital microsecond counters on pastel yellow walls.",
            "narration": "Khi độ trễ tăng lên hai trăm mili giây, người tham gia bắt đầu cười khúc khích. Độ trễ thời gian đã xé toạc mô hình dự đoán của tiểu não. Tiểu não ước lượng va chạm diễn ra ở giây thứ nhất, nhưng cú chạm đến ở giây thứ hai. Lệch pha tín hiệu xuất hiện, vỏ não không kịp dập tắt kích thích, cơn nhột ùa về.",
            "beats": [
                ("Khi độ trễ tăng lên hai trăm mili giây, người tham gia bắt đầu cười khúc khích.", "fast", "deep_dive_step", "establish", "medium_shot", "Volunteer giggling with rosy cheeks as robot arm strokes palm after delayed timer"),
                ("Độ trễ thời gian đã xé toạc mô hình dự đoán của tiểu não.", "normal", "deep_dive_step", "focus", "close_up", "A paper prediction graph tearing right down the middle with comic rip effect"),
                ("Tiểu não ước lượng va chạm diễn ra ở giây thứ nhất,", "normal", "deep_dive_step", "pan", "medium_shot", "Clock showing T=0 with cerebellum expecting contact and opening filter gate"),
                ("nhưng cú chạm đến ở giây thứ hai.", "fast", "deep_dive_step", "pan", "close_up", "Clock jumping to T+200ms while filter gate has already closed shut too early"),
                ("Lệch pha tín hiệu xuất hiện, vỏ não không kịp dập tắt kích thích,", "normal", "deep_dive_step", "focus", "medium_shot", "Red alert waves bursting past the delayed sensory gate in colorful cascade"),
                ("cơn nhột ùa về.", "fast", "deep_dive_step", "focus", "full_scene", "Full joyful explosion of laughter bubbles and music notes around the laboratory"),
            ],
        },
        {
            "id": "SC09",
            "title": "Ngoại lệ rùng mình từ chứng tâm thần phân liệt",
            "purpose": "Khảo sát trường hợp bệnh lý làm mất khả năng dự đoán",
            "narrative_situation": "deep_dive_step",
            "narrative_phase": "structural_model",
            "setting": "Clinical neuroscience archive room with case study folders on lavender pastel canvas.",
            "narration": "Khoa học ghi nhận nhóm người hy hữu có thể tự cù lét chính mình mà vẫn cười sặc sụa. Đó là những bệnh nhân tâm thần phân liệt có ảo tưởng bị kiểm soát. Ở họ, đường truyền bản sao vận động giữa vỏ não và tiểu não bị đứt gãy. Não không nhận ra cử động tự thân, tưởng rằng có thế lực ép tay họ di chuyển.",
            "beats": [
                ("Khoa học ghi nhận nhóm người hy hữu có thể tự cù lét chính mình mà vẫn cười sặc sụa.", "normal", "deep_dive_step", "establish", "medium_shot", "A rare medical case study folder opening with a glowing golden bookmark"),
                ("Đó là những bệnh nhân tâm thần phân liệt có ảo tưởng bị kiểm soát.", "normal", "deep_dive_step", "focus", "close_up", "Stylized silhouette head with marionette strings gently floating above"),
                ("Ở họ, đường truyền bản sao vận động giữa vỏ não và tiểu não bị đứt gãy.", "normal", "deep_dive_step", "pan", "medium_shot", "A glowing neural cable snapped in half with sparkling comic disconnect sparks"),
                ("Não không nhận ra cử động tự thân,", "slow", "deep_dive_step", "focus", "close_up", "A hand moving independently while the cartoon brain questions WHO MOVED THIS?"),
                ("tưởng rằng có thế lực ép tay họ di chuyển.", "slow", "deep_dive_step", "pan", "full_scene", "Gentle translucent ghostly puppet strings guiding stickman hand to tickle flank"),
                ("Cảm giác nhột bùng phát dữ dội.", "normal", "deep_dive_step", "focus", "medium_shot", "Bé Ủa noting down the profound neurological insight on a digital clipboard"),
            ],
        },
        {
            "id": "SC10",
            "title": "Lời bình triết lý: Ranh giới bản ngã và thế giới",
            "purpose": "Nhận định triết học về ranh giới bản thân và thực tại bên ngoài",
            "narrative_situation": "editorial_commentary",
            "narrative_phase": "actionable_resolution",
            "setting": "Panoramic reflective observation deck overlooking pastel horizon at twilight.",
            "narration": "Không thể tự cù lét không phải khiếm khuyết sinh học, mà là nền tảng để bạn nhận diện bản thân. Khả năng phân biệt rạch ròi hành động tự thân và tác động ngoại cảnh giúp bạn biết mình là ai trong không gian. Não bộ luôn hy sinh niềm vui phù phiếm để bảo vệ sinh tồn, giữ an toàn trước hiểm nguy bất ngờ.",
            "beats": [
                ("Không thể tự cù lét không phải khiếm khuyết sinh học,", "slow", "editorial_commentary", "establish", "medium_shot", "Bé Ủa balancing on a shiny philosophical seesaw of biology and consciousness"),
                ("mà là nền tảng để bạn nhận diện bản thân.", "slow", "editorial_commentary", "focus", "close_up", "A luminous silhouette mirror reflecting the distinct individual ego boundary"),
                ("Khả năng phân biệt rạch ròi hành động tự thân và tác động ngoại cảnh", "normal", "editorial_commentary", "pan", "medium_shot", "Two clean distinct puzzle pieces: SELF in lemon-yellow vs ENVIRONMENT in teal"),
                ("giúp bạn biết mình là ai trong không gian.", "slow", "editorial_commentary", "focus", "close_up", "Bé Ủa standing confidently at center of a clean geometric 3D coordinate compass"),
                ("Não bộ luôn hy sinh niềm vui phù phiếm để bảo vệ sinh tồn,", "slow", "editorial_commentary", "pan", "full_scene", "Brain placing golden armor around vital organs while waving away tickle toys"),
                ("giữ an toàn trước hiểm nguy bất ngờ.", "slow", "editorial_commentary", "focus", "medium_shot", "Bé Ủa nodding wisely with warm coral blush cheeks on serene pastel canvas"),
            ],
        },
        {
            "id": "SC11",
            "title": "Tổng kết và lời mời kết nối",
            "purpose": "Kết luận vui vẻ và kêu gọi khán giả tương tác",
            "narrative_situation": "outro",
            "narrative_phase": "actionable_resolution",
            "setting": "Cheerful channel studio outro set with colorful community board on pastel yellow canvas.",
            "narration": "Lần tới nếu bạn thử tự chọc nhột cơ thể nhưng bất thành, hãy cảm ơn người gác cổng tiểu não mẫn cán. Bạn còn câu hỏi kỳ quặc nào, bình luận để Bé Ủa giải mã tiếp nhé. Giờ thì đừng cố chọc nách mình nữa, để thời gian khám phá thêm những điều kỳ thú khác của tự nhiên thôi nào.",
            "beats": [
                ("Lần tới nếu bạn thử tự chọc nhột cơ thể nhưng bất thành,", "normal", "outro", "establish", "medium_shot", "Bé Ủa giving a cheerful salute to an imaginary miniature guardian at back of neck"),
                ("hãy cảm ơn người gác cổng tiểu não mẫn cán.", "normal", "outro", "focus", "close_up", "Cerebellum character wearing a guard hat smiling proudly and waving"),
                ("Bạn còn câu hỏi kỳ quặc nào, bình luận để Bé Ủa giải mã tiếp nhé.", "normal", "outro", "pan", "full_scene", "Bé Ủa pointing happily toward a pastel comment box with sparkling emojis"),
                ("Giờ thì đừng cố chọc nách mình nữa,", "fast", "outro", "focus", "medium_shot", "Bé Ủa waving hands no-no with a funny playful grin"),
                ("để thời gian khám phá thêm những điều kỳ thú khác của tự nhiên thôi nào.", "normal", "outro", "pan", "medium_shot", "Bé Ủa putting on explorer safari binoculars ready for the next adventure"),
                ("ỦA SAO VẬY?", "hold", "outro", "hold", "full_scene", "Full screen official channel endcard with Bé Ủa mascot and brand typography on pastel yellow", True),
            ],
        },
    ]

    long_brief = {
        "schema_version": "3.0",
        "topic": long_topic,
        "audience": "Khán giả quan tâm khoa học não bộ, tâm lý học hành vi và hiện tượng đời thường",
        "goal": "Giải mã tường tận cơ chế thần kinh efference copy của tiểu não và triết lý nhận diện bản thân đằng sau phản xạ cù lét",
        "video_type": "explainer",
        "duration": {"min_seconds": 180.0, "max_seconds": 240.0},
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "Thử nghiệm tự cù nách và nghịch lý trơ như đá"},
            {"id": "R02", "text": "Bác bỏ các giả thuyết dân gian về ngón tay và thân nhiệt"},
            {"id": "R03", "text": "Khám phá bản sao hiệu lệnh vận động efference copy của tiểu não"},
            {"id": "R04", "text": "Mô hình dự đoán và lệnh triệt tiêu xúc giác thân thể"},
            {"id": "R05", "text": "Nguyên lý sai số dự đoán kích hoạt phản xạ cười và mid-cta"},
            {"id": "R06", "text": "Lời bình sắc bén về bộ lọc sinh tồn giữ cho tâm trí tỉnh táo"},
            {"id": "R07", "text": "Thí nghiệm kinh điển cánh tay robot của Sarah Blakemore"},
            {"id": "R08", "text": "Đánh lừa tiểu não bằng độ trễ cơ học hai trăm mili giây"},
            {"id": "R09", "text": "Ngoại lệ rùng mình ở bệnh nhân tâm thần phân liệt có ảo tưởng bị kiểm soát"},
            {"id": "R10", "text": "Lời bình triết học: ranh giới bản ngã và nhận thức vị trí trong không gian"},
            {"id": "R11", "text": "Tổng kết ý nghĩa sinh học và lời mời bàn luận kết nối"},
        ],
        "language": "vi",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Central cancellation of self-produced tickle sensation",
                "reference": "Blakemore, S. J., Wolpert, D. M., & Frith, C. D. (1998). Nature Neuroscience, 1(7), 635-640.",
                "facts": [
                    "Tiểu não sử dụng bản sao hiệu lệnh vận động để dự đoán cảm giác xúc giác thân thể.",
                    "Lệnh ức chế làm giảm kích hoạt ở vỏ não cảm giác sơ cấp khi có kích thích tự tạo.",
                    "Độ trễ thời gian trên một trăm mili giây phá vỡ mô hình dự đoán và làm xuất hiện cảm giác nhột.",
                ],
            },
            {
                "id": "SRC02",
                "title": "Abnormalities in the awareness of action in schizophrenia",
                "reference": "Blakemore, S. J., Smith, J., Steel, R., Johnstone, E. C., & Frith, C. D. (2000). Trends in Cognitive Sciences, 4(1), 11-16.",
                "facts": [
                    "Bệnh nhân tâm thần phân liệt có ảo tưởng bị kiểm soát có thể tự cù lét chính mình do đứt gãy đường truyền bản sao vận động.",
                    "Khả năng phân biệt tự thân và ngoại lai là nền tảng của ý thức ranh giới bản ngã.",
                ],
            },
        ],
        "outputs": [{"aspect_ratio": "16:9", "language": "vi", "subtitles": False, "voice": ch.voice, "speed": ch.speed}],
        "planning": {
            "success_criteria": [
                "Truyền tải trọn vẹn 11 chặng lập luận khoa học thần kinh bằng văn phong Gen Z cuốn hút, không khô khan",
                "Hình ảnh 2D sticker pop sống động, 66 beats tương ứng 66 khung hình độc bản, nhịp độ biến thiên hài hòa",
            ],
            "avoid": ["Tuyệt đối không dùng các từ sáo rỗng AI cliché.", "Không dùng câu dài thở dốc quá 18 âm tiết."],
            "prior_knowledge": "Không đòi hỏi hiểu biết y khoa trước.",
            "pacing": "Kể chuyện sôi nổi, phân đoạn sắc sảo, nhịp độ biến thiên linh hoạt.",
            "domain_requirements": [],
            "assumptions": ["Mỗi phân cảnh được cân chỉnh theo công thức âm học P_tail và dung sai drift <= 0.3s."],
            "text_style": {
                "font": "sans-serif rõ nét, cùng kiểu và độ đậm xuyên suốt",
                "color": "#172033",
                "outline": "nền sáng tương phản",
                "size": "dễ đọc trên màn hình ngang (khung 16:9)",
                "placement": "cách mép ít nhất 10%; bố cục ngang thoáng, không ép lề dọc điện thoại",
            },
            "speech_rates": {
                "vi": {"units_per_second": 4.0, "uncertainty": 0.15, "source": "Acoustic calibrated cadence"},
                "en": {"units_per_second": 2.5, "uncertainty": 0.25, "source": "Estimated English reading rate"},
            },
        },
        "packaging": {
            "youtube_title": long_title,
            "thumbnail_spec": {
                "visual_hook": "Bé Ủa ngơ ngác tự thọc nách đối chiếu với robot cù lòng bàn tay cười phá lên trên nền sticker pop",
                "text_overlay": "VÌ SAO KHÔNG NHỘT?",
                "contrast_pair": "Tự cù trơ như tượng vs Robot cù cười sặc sụa",
            },
            "channel_pillar": "Khoa Học Đời Sống & Nhận Thức Kỳ Thú",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["ua sao vay", "vi sao khong the tu cu", "khoa hoc than kinh", "tieu nao", "efference copy", "giai ma co the"],
            "cta_plan": {
                "mid_cta": "Thử tự cù eo mình xem, bạn có nhột chút nào không?",
                "close": "Bạn còn câu hỏi kỳ quặc nào, bình luận để Bé Ủa giải mã tiếp nhé.",
                "endcard_text": "ỦA SAO VẬY?",
            },
            "editorial_stance": {
                "myth_debunked": "Nhiều người nghĩ bạn không thể tự cù lét chính mình vì tay bạn chạm vào điểm không nhạy cảm hoặc do tâm lý biết trước.",
                "why_generic_advice_fails": "Cách giải thích tâm lý chung chung bỏ qua hoàn toàn mạng lưới dự đoán chuyển động tinh vi của tiểu não.",
                "channel_verdict": "Bộ não của bạn là một hệ thống lọc tín hiệu tàn nhẫn, luôn chủ động xóa sạch mọi cảm giác do chính bạn tự tạo ra.",
                "tradeoff_or_blindspot": "Cơ chế dập tắt cảm giác giúp bạn không phát điên vì quần áo cọ xát, nhưng lại cướp đi niềm vui tự làm mình bật cười.",
            },
            "actionable_value": {
                "core_mechanism": "Tiểu não phát tín hiệu bản sao vận động để triệt tiêu cảm giác xúc giác ngay trước khi ngón tay kịp chạm vào cơ thể.",
                "practical_rule_of_thumb": "Quy tắc độ trễ: muốn tự cù lét cơ thể, bạn buộc phải dùng công cụ tạo ra độ trễ trên hai trăm mili giây để đánh lừa tiểu não.",
                "real_world_scenario": "Thử nghiệm cánh tay robot cù lét có cần điều khiển trễ giúp các nhà khoa học chứng minh sai số dự đoán kích hoạt phản xạ cười.",
            },
        },
        "youtube_title": long_title,
        "thumbnail_spec": {
            "visual_hook": "Bé Ủa ngơ ngác tự thọc nách đối chiếu với robot cù lòng bàn tay cười phá lên trên nền sticker pop",
            "text_overlay": "VÌ SAO KHÔNG NHỘT?",
            "contrast_pair": "Tự cù trơ như tượng vs Robot cù cười sặc sụa",
        },
        "channel_pillar": "Khoa Học Đời Sống & Nhận Thức Kỳ Thú",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["ua sao vay", "vi sao khong the tu cu", "khoa hoc than kinh", "tieu nao", "efference copy", "giai ma co the"],
        "cta_plan": {
            "mid_cta": "Thử tự cù eo mình xem, bạn có nhột chút nào không?",
            "close": "Bạn còn câu hỏi kỳ quặc nào, bình luận để Bé Ủa giải mã tiếp nhé.",
            "endcard_text": "ỦA SAO VẬY?",
        },
        "channel_profile": stamp,
        "engagement": asdict(ch.engagement),
        "editorial_stance": {
            "myth_debunked": "Nhiều người nghĩ bạn không thể tự cù lét chính mình vì tay bạn chạm vào điểm không nhạy cảm hoặc do tâm lý biết trước.",
            "why_generic_advice_fails": "Cách giải thích tâm lý chung chung bỏ qua hoàn toàn mạng lưới dự đoán chuyển động tinh vi của tiểu não.",
            "channel_verdict": "Bộ não của bạn là một hệ thống lọc tín hiệu tàn nhẫn, luôn chủ động xóa sạch mọi cảm giác do chính bạn tự tạo ra.",
            "tradeoff_or_blindspot": "Cơ chế dập tắt cảm giác giúp bạn không phát điên vì quần áo cọ xát, nhưng lại cướp đi niềm vui tự làm mình bật cười.",
        },
        "actionable_value": {
            "core_mechanism": "Tiểu não phát tín hiệu bản sao vận động để triệt tiêu cảm giác xúc giác ngay trước khi ngón tay kịp chạm vào cơ thể.",
            "practical_rule_of_thumb": "Quy tắc độ trễ: muốn tự cù lét cơ thể, bạn buộc phải dùng công cụ tạo ra độ trễ trên hai trăm mili giây để đánh lừa tiểu não.",
            "real_world_scenario": "Thử nghiệm cánh tay robot cù lét có cần điều khiển trễ giúp các nhà khoa học chứng minh sai số dự đoán kích hoạt phản xạ cười.",
        },
        "video_engine": "flow_video",
    }

    content_scenes_long = []
    outline_long = []
    for s_idx, s in enumerate(long_scenes_data):
        sc_id = s["id"]
        outline_long.append({
            "scene_id": sc_id,
            "purpose": s["purpose"],
            "requirements": [f"R{s_idx+1:02d}"],
            "transition": "Tiếp tục theo trình tự diễn biến nội dung",
        })
        sc_images = []
        sc_beats = []
        for b_idx, b in enumerate(s["beats"]):
            quote_text = b[0]
            tempo_val = b[1]
            sit_val = b[2]
            intent_val = b[3]
            shot_val = b[4]
            desc_text = b[5]
            is_endcard_flag = b[6] if len(b) > 6 else False
            img_id = f"{sc_id}_I{b_idx+1}"
            beat_id = f"{sc_id}_B{b_idx+1}"

            full_desc = f"Bold 2D sticker-pop cartoon illustration in 16:9 widescreen: {desc_text}, thick smooth black outlines with chunky white sticker borders, saturated flat fills in lemon yellow #FFD23F, coral #FF6B6B, teal #2EC4B6 and grape #7B2CBF on flat pastel background #FFF6D6, orthographic 2D, no gradients, no photorealism, no 3D."
            motion_str = f"Smooth 2D sticker pop animation in widescreen 16:9. {desc_text[:90]}, silent visual storytelling, no talking, no lip movement"

            sc_images.append({
                "id": img_id,
                "description": full_desc,
                "character_ids": ["CH01"],
                "preserve": "lemon-yellow mascot Bé Ủa, chunky white sticker border, pastel yellow background #FFF6D6, 2D sticker pop style",
                "change": desc_text[:80],
                "reason": "Narration-locked full-frame beat.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": shot_val,
                "tempo": tempo_val,
                "narrative_situation": sit_val,
                "emphasis_text": "",
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": True,
                "explanation": {
                    "quote": quote_text,
                    "relation": "context",
                    "source_terms": ["tiểu não", "bản sao vận động", "nhột"],
                    "visual_terms": ["sticker pop", "cartoon"],
                },
                "motion_prompt": motion_str,
            })
            sc_beats.append({
                "id": beat_id,
                "image_id": img_id,
                "purpose": s["purpose"],
                "anchor": {"vi": {"quote": quote_text, "occurrence": 1}},
                "effect": "hold" if is_endcard_flag else "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": tempo_val,
                "narrative_situation": sit_val,
                "camera_intent": intent_val,
                "shot_type": shot_val,
                "is_endcard": is_endcard_flag if is_endcard_flag else None,
            })

        content_scenes_long.append({
            "id": sc_id,
            "title": s["title"],
            "purpose": s["purpose"],
            "action": f"Bé Ủa participates in {s['title'].lower()} with animated sticker expressions.",
            "setting": s["setting"],
            "narrative_phase": s["narrative_phase"],
            "camera": f"Semantic camera: {s['beats'][0][3]} transitioning across beats.",
            "narration": s["narration"],
            "requirements": [f"R{s_idx+1:02d}"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01", "SRC02"] if s_idx >= 6 else ["SRC01"],
            "images": sc_images,
            "beats": sc_beats,
        })

    long_brief_hash = compute_brief_hash(long_brief)
    long_content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": long_brief_hash,
        "topic": long_topic,
        "duration": long_brief["duration"],
        "style": long_brief["style"],
        "required_points": long_brief["required_points"],
        "characters": [cast],
        "scenes": content_scenes_long,
        "coverage": [
            {"requirement_id": f"R{i+1:02d}", "scene_id": s["id"], "quote": s["narration"][:60]}
            for i, s in enumerate(long_scenes_data)
        ],
        "outline": outline_long,
        "claims": [
            {
                "scene_id": "SC03",
                "quote": "gọi là bản sao vận động, gửi sang tiểu não để báo trước tương lai",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Tiểu não sử dụng bản sao hiệu lệnh vận động để dự đoán cảm giác xúc giác thân thể.",
            },
            {
                "scene_id": "SC09",
                "quote": "bệnh nhân tâm thần phân liệt có ảo tưởng bị kiểm soát",
                "language": "vi",
                "source_id": "SRC02",
                "fact": "Bệnh nhân tâm thần phân liệt có ảo tưởng bị kiểm soát có thể tự cù lét chính mình do đứt gãy đường truyền bản sao vận động.",
            },
        ],
        "revision_response": [],
        "open_questions": [],
    }

    long_competitor = {
        "channel_id": "ua_sao_vay",
        "job_id": "ua-sao-vay-batch3-16x9",
        "topic": long_topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Kurzgesagt & SciShow",
                    "top_performing_videos": [
                        {
                            "title": "Why You Can't Tickle Yourself (And Who Actually Can)",
                            "views": "4.5M views",
                            "hook_technique": "Đặt câu hỏi trực diện và mời người xem tự cù ngay trong phòng.",
                            "pacing_structure": "Trải nghiệm cá nhân -> Giải phẫu tiểu não -> Thí nghiệm cánh tay robot trễ -> Trường hợp tâm thần phân liệt -> Triết lý nhận diện bản ngã.",
                            "retention_driver": "Hoạt họa độc bản lôi cuốn, giải thích nguyên lý thần kinh phức tạp thành phép ẩn dụ siêu gần gũi."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Dùng phép ẩn dụ người gác cổng tiểu não và bản sao giấy than để minh họa efference copy.",
                        "Chuyển từ tò mò sinh học sang chiều sâu triết lý về ranh giới bản ngã của con người."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 17,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Tự cù nách trơ như đá đối lập với đứa bạn khẽ chạm nhẹ đã co rúm người cười sặc sụa.",
                "counter_intuitive_truth_slap": "Không phải da bạn chai lì, chính tiểu não đã bóp nghẹt mọi cảm giác tự thân từ trước khi tay kịp chạm."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Khởi đầu bằng bài kiểm tra xúc giác tự thân trên cơ thể người xem."},
                {"phase": "empirical_conflict", "purpose": "Bác bỏ các giả thuyết dân gian về thân nhiệt và ngón tay."},
                {"phase": "structural_model", "purpose": "Giải mã chi tiết bản sao vận động efference copy của tiểu não."},
                {"phase": "actionable_resolution", "purpose": "Thí nghiệm robot tạo độ trễ và chiều sâu triết lý về ranh giới bản ngã."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Sequential daisy-chain linking Start Frame to End Frame across all scenes."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Khoa Học Đời Sống & Nhận Thức Kỳ Thú",
            "myth_debunked": "Nhiều người nghĩ bạn không thể tự cù lét chính mình vì tay bạn chạm vào điểm không nhạy cảm hoặc do tâm lý biết trước.",
            "channel_verdict": "Bộ não của bạn là một hệ thống lọc tín hiệu tàn nhẫn, luôn chủ động xóa sạch mọi cảm giác do chính bạn tự tạo ra.",
            "actionable_rule_of_thumb": "Quy tắc độ trễ: muốn tự cù lét cơ thể, bạn buộc phải dùng công cụ tạo ra độ trễ trên hai trăm mili giây để đánh lừa tiểu não."
        },
        "cta_and_spinoff_strategy": {
            "mid_cta": "Thử tự cù eo mình xem, bạn có nhột chút nào không?",
            "close": "Bạn còn câu hỏi kỳ quặc nào, bình luận để Bé Ủa giải mã tiếp nhé.",
            "endcard_text": "ỦA SAO VẬY?"
        }
    }

    return (
        short_brief, outline_short, short_content, short_competitor,
        long_brief, outline_long, long_content, long_competitor,
    )


def build_su_ke_lai_data() -> tuple[dict, dict, dict, dict, dict, dict, dict, dict]:
    """Build all 4 files for su-ke-lai-batch3-16x9 and su-ke-lai-batch3-9x16."""
    ch = get_channel("su_ke_lai")
    cast = channel_cast("su_ke_lai", "CH01")
    stamp = channel_profile_stamp("su_ke_lai")

    # -------------------------------------------------------------
    # 3. su-ke-lai-batch3-9x16 (Short)
    # -------------------------------------------------------------
    short_topic = "Vì Sao Quân Tây Sơn Vừa Đi Vừa Ngủ Vẫn Tới Thăng Long Đúng Hẹn?"
    short_title = "Vì Sao Quân Tây Sơn Vừa Đi Vừa Ngủ Vẫn Tới Kịp?"
    short_scenes_data = [
        {
            "id": "SC01",
            "title": "Cú sốc vừa đi vừa ngủ mà vẫn đại phá quân thù",
            "purpose": "Mở màn nghịch lý quân sự vừa đi vừa ngủ mà vẫn toàn thắng",
            "narrative_situation": "hook_shock",
            "narrative_phase": "lived_friction",
            "narration": "Vừa đi vừa ngủ gật dọc đường mà vẫn đánh tan hai mươi chín vạn giặc? Chuyện như đùa nhưng là chiến tích lừng lẫy năm một nghìn bảy trăm tám mươi chín.",
            "action": "Dong Ho folk print of two soldiers in indigo costume carrying a hammock with a sleeping warrior while marching through night mist.",
            "setting": "Mist-shrouded mountain pass carved in dark indigo woodcut on do paper #EFE4C8.",
            "camera": "Semantic camera: establishing full_scene transitioning to zoom-in on the hammock",
            "beats": [
                {
                    "id": "SC01_B1",
                    "quote": "Vừa đi vừa ngủ gật dọc đường mà vẫn đánh tan hai mươi chín vạn giặc?",
                    "tempo": "burst",
                    "situation": "hook_shock",
                    "intent": "establish",
                    "shot": "full_scene",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: Bold carved black woodcut outlines (#1E1E1E), flat natural pigment fills in vermilion (#B5332E) and indigo (#2C4A6E) on handmade warm do-paper canvas (#EFE4C8); two sturdy soldiers carrying a woven bamboo hammock on shoulders under moonlight, woodcut line folds, orthographic 2D, no 3D.",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. Two soldiers with steady purposeful strides carry the swinging bamboo hammock along a winding path, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC01_B2",
                    "quote": "Chuyện như đùa",
                    "tempo": "burst",
                    "situation": "hook_shock",
                    "intent": "focus",
                    "shot": "close_up",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: Close-up of a resolute warrior resting peacefully inside the hammock with arms crossed over a traditional curved saber on warm do-paper canvas (#EFE4C8), bold carved outlines and flat pagoda-tree yellow (#D9A520) fills.",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. The sleeping warrior's chest rises and falls gently as moonlit shadows drift across the do-paper canvas, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC01_B3",
                    "quote": "nhưng là chiến tích lừng lẫy",
                    "tempo": "fast",
                    "situation": "hook_shock",
                    "intent": "pan",
                    "shot": "medium_shot",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: A majestic war elephant with vermilion (#B5332E) silk banners emerging through misty bamboo silhouettes on warm do-paper canvas (#EFE4C8), bold woodcut linework and leaf green (#5E7D3A) accents.",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. The war elephant strides forward with mighty rhythm as traditional battle flags flutter in the night breeze, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC01_B4",
                    "quote": "năm một nghìn bảy trăm tám mươi chín.",
                    "tempo": "fast",
                    "situation": "hook_shock",
                    "intent": "focus",
                    "shot": "full_scene",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: An ancient imperial royal banner carved with year 1789 surrounded by soaring mythical phoenix clouds in natural vermilion and indigo on handmade do paper (#EFE4C8).",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. The imperial banner unfurls gracefully across the sky as stylized decorative clouds drift past, silent visual storytelling, no talking, no lip movement",
                },
            ],
        },
        {
            "id": "SC02",
            "title": "Bóc trần chiến thuật ba người một cáng",
            "purpose": "Giải mã cơ chế vận hành của đội hình tam nhân nhất cáng",
            "narrative_situation": "mechanism_step",
            "narrative_phase": "empirical_conflict",
            "narration": "Bí quyết của vua Quang Trung là đội hình ba người một cáng. Hai người khiêng, một người ngủ trên võng, luân phiên đổi vai ngày đêm không dừng bước.",
            "action": "Dong Ho woodcut illustration showing the three-man rotation mechanism in geometric symmetry.",
            "setting": "Tactical staging camp with bamboo stretcher racks on do paper #EFE4C8.",
            "camera": "Semantic camera: medium_shot tracking to detailed rotation diagram",
            "beats": [
                {
                    "id": "SC02_B1",
                    "quote": "Bí quyết của vua Quang Trung là đội hình ba người một cáng.",
                    "tempo": "normal",
                    "situation": "mechanism_step",
                    "intent": "establish",
                    "shot": "medium_shot",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: King Quang Trung in golden royal robe (#D9A520) gesturing with an imperial sword toward a neat woodcut tactical diagram on warm do-paper canvas (#EFE4C8), stylized round face, almond eyes, rosy cheek dots.",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. The king points his sword forward authoritatively as tactical markings illuminate on the handmade paper, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC02_B2",
                    "quote": "Hai người khiêng,",
                    "tempo": "fast",
                    "situation": "mechanism_step",
                    "intent": "focus",
                    "shot": "close_up",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: Close-up of two sturdy soldiers in indigo (#2C4A6E) tunic and bamboo hats gripping a polished wooden carrying pole on warm do-paper canvas (#EFE4C8), bold carved linework.",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. Muscular shoulders flex in unison under the carrying pole with disciplined cadence, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC02_B3",
                    "quote": "một người ngủ trên võng,",
                    "tempo": "normal",
                    "situation": "mechanism_step",
                    "intent": "pan",
                    "shot": "medium_shot",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: The third soldier sleeping serenely wrapped in a coarse hemp blanket inside the hammock with weapons securely tied beside on warm do-paper canvas (#EFE4C8).",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. The hammock sways gently back and forth maintaining smooth continuous motion along the trail, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC02_B4",
                    "quote": "luân phiên đổi vai ngày đêm không dừng bước.",
                    "tempo": "fast",
                    "situation": "mechanism_step",
                    "intent": "focus",
                    "shot": "full_scene",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: Cyclic arrows illustrating the seamless rotation of the three soldiers marching tirelessly through day sun and night moon on warm do-paper canvas (#EFE4C8).",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. Stylized circular rotation rings rotate gracefully demonstrating uninterrupted 24-hour march, silent visual storytelling, no talking, no lip movement",
                },
            ],
        },
        {
            "id": "SC03",
            "title": "Lời bình về kỷ luật và sức mạnh hậu cần",
            "purpose": "Nhận định sắc bén về vai trò hậu cần và kỷ luật thép",
            "narrative_situation": "editorial_commentary",
            "narrative_phase": "structural_model",
            "narration": "Không hạ trại nổi lửa, người lính nuốt bánh chưng lạnh xé toạc màn đêm. Đội hình cáng võng bảo tồn năng lượng, biến đường xa thành giờ dưỡng sức.",
            "action": "Soldiers eating cold banh chung quietly while marching through deep pine forests at night.",
            "setting": "Silent pine forest trail bathed in cold starlight with no campfires on do paper #EFE4C8.",
            "camera": "Semantic camera: slow tracking shot along the silent marching column",
            "beats": [
                {
                    "id": "SC03_B1",
                    "quote": "Không hạ trại nổi lửa,",
                    "tempo": "slow",
                    "situation": "editorial_commentary",
                    "intent": "establish",
                    "shot": "full_scene",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: Deep dark mountain wilderness under crescent moon with zero campfires or smoke columns, only silent silhouettes on warm do-paper canvas (#EFE4C8), dark indigo (#2C4A6E) tones.",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. The dark mountain pass lies in absolute quietness as the silent column glides forward without smoke, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC03_B2",
                    "quote": "người lính nuốt bánh chưng lạnh xé toạc màn đêm.",
                    "tempo": "slow",
                    "situation": "editorial_commentary",
                    "intent": "focus",
                    "shot": "close_up",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: A battle-hardened soldier unwrapping a green dong-leaf square banh chung while striding forward, bold carved black outlines and leaf green pigment (#5E7D3A) on do paper.",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. Dong leaves peel back revealing golden sticky rice as the soldier takes a bite without slowing his stride, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC03_B3",
                    "quote": "Đội hình cáng võng bảo tồn năng lượng,",
                    "tempo": "normal",
                    "situation": "editorial_commentary",
                    "intent": "pan",
                    "shot": "medium_shot",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: A stylized glowing energy medallion illuminating above the three-man squad symbolizing preserved physical stamina on warm do-paper canvas (#EFE4C8).",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. Warm golden aura glows steadily around the marching squad representing untiring vigor, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC03_B4",
                    "quote": "biến đường xa thành giờ dưỡng sức.",
                    "tempo": "slow",
                    "situation": "editorial_commentary",
                    "intent": "focus",
                    "shot": "full_scene",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: The grand panorama of the Tay Son army flowing effortlessly over Tam Diep mountain peaks like an unstoppable natural river on warm do paper (#EFE4C8).",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. The serpentine line of banners moves steadily over mountain ridges under the starry night sky, silent visual storytelling, no talking, no lip movement",
                },
            ],
        },
        {
            "id": "SC04",
            "title": "Đối chiếu sự ngạo mạn của Tôn Sĩ Nghị",
            "purpose": "Tương phản sự lơ là của tướng giặc với đòn tập kích sấm sét",
            "narrative_situation": "mechanism_step",
            "narrative_phase": "structural_model",
            "narration": "Tôn Sĩ Nghị mải mê yến tiệc, đinh ninh đối phương còn kẹt tận Thanh Hóa. Sự chủ quan đó đẩy quân giặc vào thế trận bão lửa không kịp trở tay.",
            "action": "Qing general Ton Si Nghi feasting arrogantly in Thang Long palace while Tay Son banners approach silently.",
            "setting": "Festive palace pavilion in Thang Long citadel hung with silk lanterns on do paper #EFE4C8.",
            "camera": "Semantic camera: split contrast view between feast hall and battle front",
            "beats": [
                {
                    "id": "SC04_B1",
                    "quote": "Tôn Sĩ Nghị mải mê yến tiệc,",
                    "tempo": "normal",
                    "situation": "before_after_contrast",
                    "intent": "establish",
                    "shot": "medium_shot",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: Qing general Ton Si Nghi in ornate Manchu robe drinking wine at a lavish palace banquet with roasted meats and dancing lanterns on warm do paper (#EFE4C8).",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. Wine cups clink lazily amid golden lanterns as the general laughs complacently at the banquet, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC04_B2",
                    "quote": "đinh ninh đối phương còn kẹt tận Thanh Hóa.",
                    "tempo": "fast",
                    "situation": "before_after_contrast",
                    "intent": "focus",
                    "shot": "close_up",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: A military map on table showing distance pins falsely placed hundreds of leagues away in Thanh Hoa with a dismissive wave gesture on do paper.",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. A careless hand tosses aside a scout report while the map markers remain far behind, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC04_B3",
                    "quote": "Sự chủ quan đó đẩy quân giặc",
                    "tempo": "normal",
                    "situation": "mechanism_step",
                    "intent": "pan",
                    "shot": "medium_shot",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: A dark storm of red-painted battle shields and blazing bamboo torches surrounding the Qing fortress walls on warm do paper (#EFE4C8).",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. Rows of thatched protective shields surge forward under raining fire arrows in intense rhythm, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC04_B4",
                    "quote": "vào thế trận bão lửa không kịp trở tay.",
                    "tempo": "fast",
                    "situation": "mechanism_step",
                    "intent": "focus",
                    "shot": "full_scene",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: The gates of Ngoc Hoi fort crumbling in blazing vermilion flames as armored elephants breach the perimeter on warm do paper (#EFE4C8).",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. Wooden fortress gates burst open as charging war elephants smash through the barricades, silent visual storytelling, no talking, no lip movement",
                },
            ],
        },
        {
            "id": "SC05",
            "title": "Đỉnh cao trào bỏ lửng và chuyển phễu video dài",
            "purpose": "Gợi mở đỉnh cao tâm lý chiến và dẫn phễu về bản dài Sử Kể Lại",
            "narrative_situation": "cliffhanger_peak",
            "narrative_phase": "actionable_resolution",
            "narration": "Nhưng đòn tâm lý rợn gáy nào khiến tướng sĩ quyết tử ở đồn Ngọc Hồi? Chi tiết cuộc tập kích rực lửa có trên bản dài Sử Kể Lại. Nếu thấy hào khí cha ông đáng nhớ, ở lại nghe tiếp những trận sau nhé.",
            "action": "The dramatic cliffhanger of the Ngoc Hoi assault transitioning to channel seal outro.",
            "setting": "Grand battle fortress gate leading into historical archival seal on handmade do paper #EFE4C8.",
            "camera": "Semantic camera: medium_shot peak cliffhanger to full_scene endcard hold",
            "beats": [
                {
                    "id": "SC05_B1",
                    "quote": "Nhưng đòn tâm lý rợn gáy nào",
                    "tempo": "normal",
                    "situation": "cliffhanger_peak",
                    "intent": "establish",
                    "shot": "medium_shot",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: King Quang Trung mounted on a towering war elephant raising his flaming torch toward the sky before dawn on warm do paper (#EFE4C8), vermilion and indigo pigments.",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. The torch flame billows against the dawn sky as the king's eyes burn with fierce determination, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC05_B2",
                    "quote": "khiến tướng sĩ quyết tử ở đồn Ngọc Hồi?",
                    "tempo": "fast",
                    "situation": "cliffhanger_peak",
                    "intent": "focus",
                    "shot": "close_up",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: Dramatic close-up of Tay Son warriors tying straw mats soaked in water around their bodies for storming the fire barricades on warm do paper (#EFE4C8).",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. Warriors pull wet straw ties tight with resolute expressions etched in woodcut lines, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC05_B3",
                    "quote": "Chi tiết cuộc tập kích rực lửa có trên bản dài Sử Kể Lại.",
                    "tempo": "normal",
                    "situation": "cta_bridge",
                    "intent": "pan",
                    "shot": "full_scene",
                    "effect": "cut",
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration: An ornate woodcut frame displaying the legendary battle panorama with an invitation scroll to the full YouTube episode on warm do paper (#EFE4C8).",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. The historical scroll rolls open revealing the expansive full-length campaign map, silent visual storytelling, no talking, no lip movement",
                },
                {
                    "id": "SC05_B4",
                    "quote": "Nếu thấy hào khí cha ông đáng nhớ, ở lại nghe tiếp những trận sau nhé.",
                    "tempo": "hold",
                    "situation": "cta_close",
                    "intent": "hold",
                    "shot": "full_scene",
                    "effect": "hold",
                    "is_endcard": True,
                    "desc": "2D Vietnamese Dong Ho folk woodblock-print illustration channel endcard: Official red royal seal reading 'SỬ KỂ LẠI' carved in authentic antique woodcut characters on handmade do paper (#EFE4C8).",
                    "motion": "Smooth 2D Dong Ho woodcut folk motion. The red imperial seal presses down leaving a permanent crisp impression on the handmade paper, silent visual storytelling, no talking, no lip movement",
                },
            ],
        },
    ]

    short_brief = {
        "schema_version": "3.0",
        "topic": short_topic,
        "audience": "Khán giả yêu thích lịch sử Việt Nam, nghệ thuật quân sự và câu chuyện hào hùng dân tộc",
        "goal": "Bóc trần chiến thuật hành quân ba người một cáng và tư duy hậu cần thiên tài của vua Quang Trung trong chiến dịch Kỷ Dậu 1789",
        "video_type": "explainer",
        "duration": {"min_seconds": 38.0, "max_seconds": 52.0},
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Nghịch lý vừa đi vừa ngủ mà vẫn hành quân thần tốc đánh tan giặc"},
            {"id": "R02", "text": "Chiến thuật ba người một cáng xoay tua liên tục ngày đêm"},
            {"id": "R03", "text": "Kỷ luật thép không nổi lửa và khẩu phần bánh chưng lạnh"},
            {"id": "R04", "text": "Sự chủ quan của Tôn Sĩ Nghị và đòn giáng sấm sét"},
            {"id": "R05", "text": "Đỉnh cao trào bỏ lửng về trận Ngọc Hồi và chuyển phễu video dài"},
        ],
        "language": "vi",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "9:16",
        "format_profile": "short_9x16",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Đại Nam Chính Biên Liệt Truyện & Hoàng Lê Nhất Thống Chí",
                "reference": "Ngô Gia Văn Phái (1789). Hoàng Lê Nhất Thống Chí, Hồi 14; Quốc Sử Quán Triều Nguyễn, Liệt Truyện Tây Sơn.",
                "facts": [
                    "Vua Quang Trung cho quân chia làm từng tốp ba người mang một chiếc cáng, hai người khiêng một người nằm nghỉ, thay nhau chạy suốt ngày đêm.",
                    "Đại quân ăn Tết sớm ở Tam Điệp vào ngày hai mươi tháng Chạp và mở tiệc khải hoàn tại Thăng Long trưa mùng năm Tết Kỷ Dậu.",
                ],
            }
        ],
        "outputs": [{"aspect_ratio": "9:16", "language": "vi", "subtitles": True, "voice": ch.voice, "speed": ch.speed}],
        "planning": {
            "success_criteria": [
                "Lột tả chân thực hào khí hành quân thần tốc của nghĩa quân Tây Sơn trong 45 giây tranh khắc gỗ Đông Hồ",
                "Cân chỉnh âm học chuẩn xác, nhịp điệu dồn dập, chuyển phễu sang video dài mượt mà",
            ],
            "avoid": ["Tránh lối kể liệt kê niên đại khô khan.", "Tuyệt đối không dùng văn mẫu AI cliché."],
            "prior_knowledge": "Không đòi hỏi nghiên cứu lịch sử chuyên sâu từ trước.",
            "pacing": "Kể chuyện điện ảnh, kịch tính, tôn trọng sự thật lịch sử.",
            "domain_requirements": [],
            "assumptions": ["Mỗi phân cảnh được cân chỉnh theo công thức âm học P_tail và dung sai drift <= 0.3s."],
            "text_style": {
                "font": "sans-serif rõ nét, cùng kiểu và độ đậm xuyên suốt",
                "color": "#172033",
                "outline": "nền sáng tương phản",
                "size": "dễ đọc trên điện thoại (khung dọc 9:16)",
                "placement": "cách mép ít nhất 10%; tránh mặt và vùng phụ đề dưới cùng 18%",
            },
            "speech_rates": {
                "vi": {"units_per_second": 4.0, "uncertainty": 0.15, "source": "Acoustic calibrated cadence"},
                "en": {"units_per_second": 2.5, "uncertainty": 0.25, "source": "Estimated English reading rate"},
            },
        },
        "packaging": {
            "youtube_title": short_title,
            "thumbnail_spec": {
                "visual_hook": "Chiến binh Tây Sơn nằm ngủ trên cáng gươm tuốt trần đối lập với voi chiến xung trận trong bão lửa Ngọc Hồi",
                "text_overlay": "VỪA ĐI VỪA NGỦ",
                "contrast_pair": "Ba người một cáng thâu đêm vs Bão lửa đại phá 29 vạn giặc",
                "thumbnail_prompt": "2D Vietnamese Dong Ho folk woodblock-print illustration: bold carved black woodcut outlines (#1E1E1E), flat natural pigment fills in vermilion (#B5332E) and indigo (#2C4A6E) on handmade warm do-paper canvas (#EFE4C8); two sturdy soldiers carrying a woven hammock with a sleeping warrior clutching a curved sword on one side, while a colossal armored war elephant charges forward through flaming fortress palisades on the other side. Large bold carved woodcut title in upper third: 'VỪA ĐI VỪA NGỦ'. Orthographic 2D, no photorealism, no 3D.",
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Hào Khí Lịch Sử & Nghệ Thuật Quân Sự Việt Nam",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["su ke lai", "tay son", "quang trung", "hanh quan than toc", "ba nguoi mot cang", "ngoc hoi dong da", "shorts"],
            "cta_plan": {
                "cliffhanger_peak": "Nhưng đòn tâm lý rợn gáy nào khiến tướng sĩ quyết tử ở đồn Ngọc Hồi?",
                "bridge": "Chi tiết cuộc tập kích rực lửa có trên bản dài Sử Kể Lại.",
                "close": "Nếu thấy hào khí cha ông đáng nhớ, ở lại nghe tiếp những trận sau nhé.",
                "endcard_text": "SỬ KỂ LẠI",
            },
            "editorial_stance": {
                "myth_debunked": "Dân gian truyền miệng rằng quân Tây Sơn dùng phép tàng hình hay thần chú bí hiểm để bay từ Phú Xuân ra Thăng Long.",
                "why_generic_advice_fails": "Cách nhìn mang màu sắc huyền bí phủ nhận hoàn toàn tư duy hậu cần và tổ chức quân sự thiên tài của vua Quang Trung.",
                "channel_verdict": "Chiến thắng thần tốc không đến từ phép màu, mà sinh ra từ kỷ luật thép và giải pháp hậu cần xoay tua ba người một cáng.",
                "tradeoff_or_blindspot": "Cuộc hành quân ép thể lực đến tận cùng giới hạn sinh học, đòi hỏi sự hy sinh thầm lặng của hàng vạn binh lính vô danh.",
            },
            "actionable_value": {
                "core_mechanism": "Đội hình ba người một cáng luân phiên hai người khiêng một người ngủ giúp đạo quân hành tiến liên tục ngày đêm không dừng bước.",
                "practical_rule_of_thumb": "Quy tắc xoay tua năng lượng: chia nhóm ba người đảo ca liên tục trên đường cơ động để duy trì sức chiến đấu tối đa.",
                "real_world_scenario": "Quân đoàn Tây Sơn vượt hơn sáu trăm cây số hiểm trở trong ba mươi ngày, đánh tan đồn Ngọc Hồi ngay trưa mùng năm Tết Kỷ Dậu.",
            },
        },
        "youtube_title": short_title,
        "thumbnail_spec": {
            "visual_hook": "Chiến binh Tây Sơn nằm ngủ trên cáng gươm tuốt trần đối lập với voi chiến xung trận trong bão lửa Ngọc Hồi",
            "text_overlay": "VỪA ĐI VỪA NGỦ",
            "contrast_pair": "Ba người một cáng thâu đêm vs Bão lửa đại phá 29 vạn giặc",
            "thumbnail_prompt": "2D Vietnamese Dong Ho folk woodblock-print illustration: bold carved black woodcut outlines (#1E1E1E), flat natural pigment fills in vermilion (#B5332E) and indigo (#2C4A6E) on handmade warm do-paper canvas (#EFE4C8); two sturdy soldiers carrying a woven hammock with a sleeping warrior clutching a curved sword on one side, while a colossal armored war elephant charges forward through flaming fortress palisades on the other side. Large bold carved woodcut title in upper third: 'VỪA ĐI VỪA NGỦ'. Orthographic 2D, no photorealism, no 3D.",
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Hào Khí Lịch Sử & Nghệ Thuật Quân Sự Việt Nam",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["su ke lai", "tay son", "quang trung", "hanh quan than toc", "ba nguoi mot cang", "ngoc hoi dong da", "shorts"],
        "parent_long_id": "su-ke-lai-batch3-16x9",
        "cta_plan": {
            "cliffhanger_peak": "Nhưng đòn tâm lý rợn gáy nào khiến tướng sĩ quyết tử ở đồn Ngọc Hồi?",
            "bridge": "Chi tiết cuộc tập kích rực lửa có trên bản dài Sử Kể Lại.",
            "close": "Nếu thấy hào khí cha ông đáng nhớ, ở lại nghe tiếp những trận sau nhé.",
            "endcard_text": "SỬ KỂ LẠI",
        },
        "channel_profile": stamp,
        "engagement": asdict(ch.engagement),
        "editorial_stance": {
            "myth_debunked": "Dân gian truyền miệng rằng quân Tây Sơn dùng phép tàng hình hay thần chú bí hiểm để bay từ Phú Xuân ra Thăng Long.",
            "why_generic_advice_fails": "Cách nhìn mang màu sắc huyền bí phủ nhận hoàn toàn tư duy hậu cần và tổ chức quân sự thiên tài của vua Quang Trung.",
            "channel_verdict": "Chiến thắng thần tốc không đến từ phép màu, mà sinh ra từ kỷ luật thép và giải pháp hậu cần xoay tua ba người một cáng.",
            "tradeoff_or_blindspot": "Cuộc hành quân ép thể lực đến tận cùng giới hạn sinh học, đòi hỏi sự hy sinh thầm lặng của hàng vạn binh lính vô danh.",
        },
        "actionable_value": {
            "core_mechanism": "Đội hình ba người một cáng luân phiên hai người khiêng một người ngủ giúp đạo quân hành tiến liên tục ngày đêm không dừng bước.",
            "practical_rule_of_thumb": "Quy tắc xoay tua năng lượng: chia nhóm ba người đảo ca liên tục trên đường cơ động để duy trì sức chiến đấu tối đa.",
            "real_world_scenario": "Quân đoàn Tây Sơn vượt hơn sáu trăm cây số hiểm trở trong ba mươi ngày, đánh tan đồn Ngọc Hồi ngay trưa mùng năm Tết Kỷ Dậu.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }

    content_scenes_short = []
    outline_short = []
    for s_idx, s in enumerate(short_scenes_data):
        sc_id = s["id"]
        outline_short.append({
            "scene_id": sc_id,
            "purpose": s["purpose"],
            "requirements": [f"R{s_idx+1:02d}"],
            "transition": "Tiếp tục theo trình tự diễn biến nội dung",
        })
        sc_images = []
        sc_beats = []
        for b_idx, b in enumerate(s["beats"]):
            img_id = f"{sc_id}_I{b_idx+1}"
            beat_id = f"{sc_id}_B{b_idx+1}"
            sc_images.append({
                "id": img_id,
                "description": b["desc"],
                "character_ids": ["CH01"],
                "preserve": "Dong Ho folk woodblock print style, handmade do-paper canvas #EFE4C8, carved black outlines #1E1E1E, period costume",
                "change": b["desc"][:80],
                "reason": "Narration-locked full-frame beat.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": b["shot"],
                "tempo": b["tempo"],
                "narrative_situation": b["situation"],
                "emphasis_text": "",
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": True,
                "explanation": {
                    "quote": b["quote"],
                    "relation": "context",
                    "source_terms": ["Tây Sơn", "ba người một cáng"],
                    "visual_terms": ["Đông Hồ", "khắc gỗ"],
                },
                "motion_prompt": b["motion"],
            })
            sc_beats.append({
                "id": beat_id,
                "image_id": img_id,
                "purpose": s["purpose"],
                "anchor": {"vi": {"quote": b["quote"], "occurrence": 1}},
                "effect": b["effect"],
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": b["tempo"],
                "narrative_situation": b["situation"],
                "camera_intent": b["intent"],
                "shot_type": b["shot"],
                "is_endcard": b.get("is_endcard", False),
            })

        content_scenes_short.append({
            "id": sc_id,
            "title": s["title"],
            "purpose": s["purpose"],
            "action": s["action"],
            "setting": s["setting"],
            "camera": s["camera"],
            "narration": s["narration"],
            "requirements": [f"R{s_idx+1:02d}"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "images": sc_images,
            "beats": sc_beats,
        })

    short_brief_hash = compute_brief_hash(short_brief)
    short_content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": short_brief_hash,
        "topic": short_topic,
        "duration": short_brief["duration"],
        "style": short_brief["style"],
        "required_points": short_brief["required_points"],
        "characters": [cast],
        "scenes": content_scenes_short,
        "coverage": [
            {"requirement_id": f"R{i+1:02d}", "scene_id": s["id"], "quote": s["narration"][:60]}
            for i, s in enumerate(short_scenes_data)
        ],
        "outline": outline_short,
        "claims": [
            {
                "scene_id": "SC02",
                "quote": "Bí quyết của vua Quang Trung là đội hình ba người một cáng",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Vua Quang Trung cho quân chia làm từng tốp ba người mang một chiếc cáng, hai người khiêng một người nằm nghỉ, thay nhau chạy suốt ngày đêm.",
            }
        ],
        "revision_response": [],
        "open_questions": [],
    }

    short_competitor = {
        "channel_id": "su_ke_lai",
        "job_id": "su-ke-lai-batch3-9x16",
        "topic": short_topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Đu Đuốc & Việt Sử Kiêu Hùng",
                    "top_performing_videos": [
                        {
                            "title": "Cuộc hành quân thần tốc của vua Quang Trung 1789",
                            "views": "3.2M views",
                            "hook_technique": "Đặt con số 600km đèo dốc trong 30 ngày và hỏi làm sao người xưa chạy kịp.",
                            "pacing_structure": "Thế cờ hiểm -> Giải pháp cáng võng xoay tua -> Hậu cần bánh chưng -> Trận Đống Đa rực lửa.",
                            "retention_driver": "Âm hưởng hào hùng, phân tích logic quân sự hiện đại vào bối cảnh trung đại."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Lột tả thực tế gian khổ của người lính thay vì thần thánh hóa siêu nhiên.",
                        "Công thức luân phiên 3 người 1 cáng giúp người xem dễ dàng hình dung và nhớ sâu."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 17,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Hai người lính vác cáng bước đi trong đêm mờ đối lập với chiến binh nằm ngủ tĩnh lặng trên võng gươm tuốt trần.",
                "counter_intuitive_truth_slap": "Không có phép thần bay lượn, chiến thắng thần tốc đến từ giải pháp cơ học xoay tua ba người một cáng."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Mở màn cú sốc vừa đi vừa ngủ vẫn đánh tan hai mươi chín vạn giặc."},
                {"phase": "empirical_conflict", "purpose": "Bóc tách cấu trúc đội hình ba người một cáng."},
                {"phase": "structural_model", "purpose": "Phân tích hậu cần không khói và bảo tồn năng lượng."},
                {"phase": "actionable_resolution", "purpose": "Đối chiếu chủ quan của giặc và chuyển phễu bản dài."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Sequential daisy-chain linking Start Frame to End Frame across all scenes."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Hào Khí Lịch Sử & Nghệ Thuật Quân Sự Việt Nam",
            "myth_debunked": "Dân gian truyền miệng rằng quân Tây Sơn dùng phép tàng hình hay thần chú bí hiểm để bay từ Phú Xuân ra Thăng Long.",
            "channel_verdict": "Chiến thắng thần tốc không đến từ phép màu, mà sinh ra từ kỷ luật thép và giải pháp hậu cần xoay tua ba người một cáng.",
            "actionable_rule_of_thumb": "Quy tắc xoay tua năng lượng: chia nhóm ba người đảo ca liên tục trên đường cơ động để duy trì sức chiến đấu tối đa."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "Nhưng đòn tâm lý rợn gáy nào khiến tướng sĩ quyết tử ở đồn Ngọc Hồi?",
            "bridge": "Chi tiết cuộc tập kích rực lửa có trên bản dài Sử Kể Lại.",
            "close": "Nếu thấy hào khí cha ông đáng nhớ, ở lại nghe tiếp những trận sau nhé.",
            "endcard_text": "SỬ KỂ LẠI"
        }
    }

    # -------------------------------------------------------------
    # 4. su-ke-lai-batch3-16x9 (Long)
    # -------------------------------------------------------------
    long_topic = "Cuộc Hành Quân Thần Tốc 1789: Bí Mật Đội Hình Ba Người Một Cáng"
    long_title = "Hành Quân Thần Tốc 1789: Bí Mật Ba Người Một Cáng"
    long_scenes_data = [
        {
            "id": "SC01",
            "title": "Tin sét đánh từ Thăng Long và quyết định định mệnh",
            "purpose": "Thiết lập bối cảnh nguy cấp năm 1788 và lễ đăng cơ núi Bân",
            "narrative_situation": "hook_cold_open",
            "narrative_phase": "lived_friction",
            "setting": "Sacred Mount Ban ceremonial terrace under billowing celestial clouds on do paper #EFE4C8.",
            "narration": "Năm một nghìn bảy trăm tám mươi tám, đại quân Mãn Thanh tràn vào Thăng Long. Nguyễn Huệ lập đàn tế trời tại núi Bân, lên ngôi hoàng đế Quang Trung. Vị vua trẻ hạ lệnh thần tốc tiến quân ra Bắc. Trước mắt là chặng đường nửa nghìn cây số hiểm trở, đèo dốc cheo leo. Quyết định táo bạo đã mở màn cho khúc tráng ca bất hủ.",
            "beats": [
                ("Năm một nghìn bảy trăm tám mươi tám, đại quân Mãn Thanh tràn vào Thăng Long.", "burst", "hook_cold_open", "establish", "full_scene", "Dong Ho woodcut illustration of imperial Thang Long citadel surrounded by Qing dragon banners"),
                ("Nguyễn Huệ lập đàn tế trời tại núi Bân,", "burst", "hook_cold_open", "focus", "medium_shot", "Mount Ban sacrificial altar with burning incense cauldrons under billowing heavens"),
                ("lên ngôi hoàng đế Quang Trung.", "fast", "hook_cold_open", "focus", "close_up", "Emperor Quang Trung in dragon robe receiving golden jade seal on warm do paper"),
                ("Vị vua trẻ hạ lệnh thần tốc tiến quân ra Bắc.", "fast", "hook_cold_open", "pan", "medium_shot", "Emperor drawing imperial sword pointing decisively northward toward distant mountain passes"),
                ("Trước mắt là chặng đường nửa nghìn cây số hiểm trở, đèo dốc cheo leo.", "normal", "hook_cold_open", "pan", "full_scene", "Expansive panoramic woodcut landscape of jagged Annamite mountain ridges and swift rivers"),
                ("Quyết định táo bạo đã mở màn cho khúc tráng ca bất hủ.", "normal", "hook_cold_open", "focus", "medium_shot", "Tay Son army ranks raising bronze spears in unison with vermilion banners"),
            ],
        },
        {
            "id": "SC02",
            "title": "Bài toán bất khả thi về cự ly và thời gian",
            "purpose": "Phân tích giới hạn sinh học và tốc độ hành quân thời trung đại",
            "narrative_situation": "mechanism_reveal",
            "narrative_phase": "lived_friction",
            "setting": "Imperial military strategy pavilion with maps of Annamite mountains on warm do paper.",
            "narration": "Từ Phú Xuân ra Thăng Long dài sáu trăm cây số, đèo cao dốc thẳm và sông ngòi chằng chịt. Bình thường một đạo quân đi bộ nhanh nhất cũng phải mất năm mươi ngày. Nhưng vua Quang Trung chỉ cho ba mươi ngày để tuyển quân và đánh tan giặc. Làm sao đoàn quân vạn người di chuyển vượt giới hạn sinh học như vậy?",
            "beats": [
                ("Từ Phú Xuân ra Thăng Long dài sáu trăm cây số, đèo cao dốc thẳm và sông ngòi chằng chịt.", "fast", "mechanism_reveal", "establish", "full_scene", "Old tactical military map with carved contour lines tracing 600 kilometers of rugged terrain"),
                ("Bình thường một đạo quân đi bộ nhanh nhất cũng phải mất năm mươi ngày.", "normal", "mechanism_reveal", "focus", "medium_shot", "Medieval soldiers trudging slowly with heavy pack loads through mud and rain"),
                ("Nhưng vua Quang Trung chỉ cho ba mươi ngày", "normal", "mechanism_reveal", "focus", "close_up", "Sun and moon calendar marks showing 50 long arduous marching days"),
                ("để tuyển quân", "fast", "mechanism_reveal", "pan", "medium_shot", "Imperial calendar scroll pinned with strict 30-day target marker"),
                ("và đánh tan giặc.", "normal", "mechanism_reveal", "focus", "close_up", "Sword striking down upon battle campaign timetable carving deep woodcut line"),
                ("Làm sao đoàn quân vạn người di chuyển vượt giới hạn sinh học như vậy?", "normal", "mechanism_reveal", "focus", "full_scene", "Stylized question glyph surrounded by marching soldier silhouettes on do paper"),
            ],
        },
        {
            "id": "SC03",
            "title": "Tuyển quân thần tốc tại Nghệ An",
            "purpose": "Khắc họa chặng dừng chân Nghệ An và bài toán hậu cần phình to",
            "narrative_situation": "mechanism_step",
            "narrative_phase": "empirical_conflict",
            "setting": "Vibrant Lam River military encampment surrounded by ancient bamboo groves on do paper #EFE4C8.",
            "narration": "Đến Nghệ An, vua dừng chân mười ngày để tuyển mộ thêm lực lượng. Cứ ba suất đinh lấy một người lính, tuyển thêm hơn một vạn tân binh tinh nhuệ. Quân số lên mười vạn người cùng hàng trăm thớt voi chiến. Quân đông đồng nghĩa gánh nặng lương thảo tăng vọt, nguy cơ chậm trễ hiển hiện trước mắt các tướng lĩnh.",
            "beats": [
                ("Đến Nghệ An, vua dừng chân mười ngày để tuyển mộ thêm lực lượng.", "normal", "mechanism_step", "establish", "medium_shot", "Ancient Lam River shores with Tay Son recruitment tents set under banyan trees"),
                ("Cứ ba suất đinh lấy một người lính, tuyển thêm hơn một vạn tân binh tinh nhuệ.", "fast", "mechanism_step", "focus", "close_up", "Village elder reviewing family census scrolls with imperial recruiting officer"),
                ("Quân số lên mười vạn người cùng hàng trăm thớt voi chiến.", "normal", "mechanism_step", "pan", "medium_shot", "Young sturdy Nghe An recruits stepping forward to receive bronze helmet and spear"),
                ("Quân đông đồng nghĩa gánh nặng lương thảo tăng vọt,", "normal", "mechanism_step", "pan", "full_scene", "Vast military parade of 100,000 soldiers with tusker war elephants lining riverbank"),
                ("nguy cơ chậm trễ", "fast", "mechanism_step", "focus", "close_up", "Stacked rice grain sacks and supply carts threatening to bottleneck march road"),
                ("hiển hiện trước mắt các tướng lĩnh.", "normal", "mechanism_step", "focus", "medium_shot", "General Ngo Van So and military advisors frowning over supply route congestion"),
            ],
        },
        {
            "id": "SC04",
            "title": "Khởi nguyên đội hình ba người một cáng",
            "purpose": "Giới thiệu sáng tạo chiến thuật ba người một cáng",
            "narrative_situation": "solution_framework",
            "narrative_phase": "empirical_conflict",
            "setting": "Field drill grounds with soldiers practicing rotation mechanics on warm do paper.",
            "narration": "Để giải quyết tốc độ và thể lực, vua Quang Trung sáng tạo chiến thuật ba người một cáng. Bộ binh chia thành từng tổ ba người mang một chiếc võng tre cơ động. Hai người khiêng chạy trước sau, người thứ ba nằm ngủ hồi sức trên võng cùng hành lý. Cứ đi vài dặm đường, họ lại đổi vai liên tục.",
            "beats": [
                ("Để giải quyết tốc độ và thể lực,", "normal", "solution_framework", "establish", "medium_shot", "King Quang Trung sketching structural squad blueprint on wooden writing tablet"),
                ("vua Quang Trung sáng tạo chiến thuật ba người một cáng.", "normal", "solution_framework", "focus", "close_up", "Detailed woodcut design of woven bamboo stretcher with reinforced hemp rope slings"),
                ("Bộ binh chia thành từng tổ ba người mang một chiếc võng tre cơ động.", "normal", "solution_framework", "pan", "medium_shot", "Soldiers forming organized three-man cells each carrying one sturdy bamboo litter"),
                ("Hai người khiêng chạy trước sau,", "fast", "solution_framework", "pan", "full_scene", "Two front and rear bearers marching in rhythmic double-time stride along trail"),
                ("người thứ ba nằm ngủ hồi sức trên võng cùng hành lý.", "normal", "solution_framework", "focus", "close_up", "Third soldier sleeping peacefully in hammock cradle clutching his scabbard"),
                ("Cứ đi vài dặm đường, họ lại đổi vai liên tục.", "fast", "solution_framework", "focus", "medium_shot", "Swift seamless bearer changeover mid-stride without setting litter on ground"),
            ],
        },
        {
            "id": "SC05",
            "title": "Kỷ luật xoay tua và lời mời bàn luận",
            "purpose": "Mid CTA và phân tích cỗ máy tuần hoàn cơ học",
            "narrative_situation": "mid_break_cta",
            "narrative_phase": "structural_model",
            "setting": "Mountain pass winding through morning mist with steady marching rhythm on do paper.",
            "narration": "Đội hình cáng võng biến toàn bộ đạo quân thành cỗ máy tuần hoàn liên tục chuyển động. Binh sĩ vừa ngủ say, vừa tiến về phía trước với tốc độ không suy giảm ngày đêm. Bạn nghĩ gì về kỷ luật hành quân này, hãy lưu video lại để cùng luận bàn nhé. Nhờ đó, nghĩa quân biến đường dài thành giờ dưỡng sức.",
            "beats": [
                ("Đội hình cáng võng biến toàn bộ đạo quân thành cỗ máy tuần hoàn liên tục chuyển động.", "normal", "mid_break_cta", "establish", "full_scene", "Perpetual motion graphic in Dong Ho style showing continuous rolling march lines"),
                ("Binh sĩ vừa ngủ say, vừa tiến về phía trước với tốc độ không suy giảm ngày đêm.", "normal", "mid_break_cta", "focus", "medium_shot", "Contrast of sleeper resting while column advances under burning torchlight"),
                ("Bạn nghĩ gì về kỷ luật hành quân này, hãy lưu video lại để cùng luận bàn nhé.", "normal", "mid_break_cta", "focus", "close_up", "Traditional carved scroll inviting viewer reflection on ancient military discipline"),
                ("Nhờ đó,", "fast", "mid_break_cta", "pan", "medium_shot", "Empty campsites bypassed completely as column pushes tirelessly forward"),
                ("nghĩa quân biến đường dài thành giờ dưỡng sức.", "normal", "mid_break_cta", "focus", "close_up", "Warrior waking up refreshed and exchanging place with tired front bearer"),
                ("Đạo quân giữ vững sức chiến đấu trước giờ xung trận.", "slow", "mid_break_cta", "focus", "full_scene", "Determined frontline soldiers marching with fierce eyes toward northern horizon"),
            ],
        },
        {
            "id": "SC06",
            "title": "Lời bình: Tư duy hậu cần thời trung đại",
            "purpose": "Đánh giá học thuật về quản trị năng lượng và bảo toàn sức chiến đấu",
            "narrative_situation": "editorial_commentary",
            "narrative_phase": "structural_model",
            "setting": "Historical study room with ancient scales and tactical treatises on handmade do paper.",
            "narration": "Nhiều người từng lầm tưởng chiến thắng của quân Tây Sơn dựa vào phép lạ hay sự liều lĩnh thuần túy. Cách nhìn đó bỏ qua tư duy hậu cần khoa học của vua Quang Trung. Ông hiểu sâu sắc rằng vũ khí mạnh nhất là năng lượng trong từng thớ cơ. Thay vì vắt kiệt thể lực, giải pháp cáng võng bảo tồn sức chiến đấu.",
            "beats": [
                ("Nhiều người từng lầm tưởng chiến thắng của quân Tây Sơn dựa vào phép lạ hay sự liều lĩnh thuần túy.", "slow", "editorial_commentary", "establish", "medium_shot", "Historian analyzing ancient texts on parchment surrounded by mystical folklore clouds"),
                ("Cách nhìn đó bỏ qua tư duy hậu cần khoa học của vua Quang Trung.", "slow", "editorial_commentary", "focus", "close_up", "Emperor Quang Trung depicted studying logistical supply ratios with measured brushwork"),
                ("Ông hiểu sâu sắc rằng vũ khí mạnh nhất", "normal", "editorial_commentary", "pan", "medium_shot", "Bronze sword and iron halberd resting alongside balanced ration balance scale"),
                ("là năng lượng trong từng thớ cơ.", "slow", "editorial_commentary", "focus", "close_up", "Anatomical woodcut drawing showing rested muscular tendon ready for explosive action"),
                ("Thay vì vắt kiệt thể lực,", "normal", "editorial_commentary", "pan", "medium_shot", "Contrast showing exhausted stragglers in conventional army versus rested Tay Son"),
                ("giải pháp cáng võng bảo tồn sức chiến đấu.", "slow", "editorial_commentary", "focus", "full_scene", "Fresh vigorous army arriving at border passes with unblemished battle morale"),
            ],
        },
        {
            "id": "SC07",
            "title": "Hậu cần khô: Bánh chưng lạnh xé toạc màn đêm",
            "purpose": "Chi tiết khẩu phần ăn khô không nổi lửa giữ bí mật tuyệt đối",
            "narrative_situation": "case_study",
            "narrative_phase": "structural_model",
            "setting": "Dense mountain forest under cold winter moon with shadows gliding noiselessly.",
            "narration": "Không chỉ giải bài toán ngủ nghỉ, nhà vua còn giải quyết triệt để vấn đề ăn uống dọc đường. Mỗi người lính mang theo khẩu phần bánh chưng, bánh tét và lương khô. Họ vừa đi vừa ăn, tuyệt đối không nổi lửa nấu nướng hay dựng lều. Không một làn khói bốc lên, hành tung mười vạn quân chìm vào màn đêm.",
            "beats": [
                ("Không chỉ giải bài toán ngủ nghỉ, nhà vua còn giải quyết triệt để vấn đề ăn uống dọc đường.", "normal", "case_study", "establish", "medium_shot", "Supply officer distributing green leaf packages to disciplined marching lines"),
                ("Mỗi người lính mang theo khẩu phần bánh chưng, bánh tét và lương khô.", "fast", "case_study", "focus", "close_up", "Traditional green square banh chung and cylindrical banh tet wrapped in banana leaves"),
                ("Họ vừa đi vừa ăn,", "normal", "case_study", "pan", "medium_shot", "Soldier sharing cold rice cake with fellow litter bearer while continuing march"),
                ("tuyệt đối không nổi lửa nấu nướng hay dựng lều.", "fast", "case_study", "focus", "close_up", "Strict imperial ban seal over flint and campfire symbol: NO SMOKE ALLOWED"),
                ("Không một làn khói bốc lên,", "slow", "case_study", "pan", "full_scene", "Pristine dark mountain forest canopy untouched by smoke under cold winter stars"),
                ("hành tung mười vạn quân chìm vào màn đêm.", "slow", "case_study", "focus", "medium_shot", "Ghostly army gliding noiselessly like shadows through mountain mist on do paper"),
            ],
        },
        {
            "id": "SC08",
            "title": "Cú lừa chiến lược khiến Tôn Sĩ Nghị mất cảnh giác",
            "purpose": "Phân tích sai lầm chủ quan của Tôn Sĩ Nghị tại Thăng Long",
            "narrative_situation": "deep_dive_step",
            "narrative_phase": "structural_model",
            "setting": "Gilded palace banquet hall in Thang Long with drinking cups and silk banners on do paper.",
            "narration": "Tại Thăng Long, Tôn Sĩ Nghị ung dung mở tiệc ăn Tết linh đình cùng vua tôi Lê Chiêu Thống. Thám tử báo về quân Tây Sơn còn tập hợp ở Nghệ An và Thanh Hóa. Tôn Sĩ Nghị tin chắc đối phương không thể vượt đường giá rét chỉ trong vài ngày. Sự chủ quan đẩy hai mươi chín vạn quân vào chiếc bẫy giăng sẵn.",
            "beats": [
                ("Tại Thăng Long, Tôn Sĩ Nghị ung dung mở tiệc ăn Tết linh đình cùng vua tôi Lê Chiêu Thống.", "normal", "deep_dive_step", "establish", "full_scene", "Grand banquet in Thang Long palace with Qing officers drinking wine and celebrating early New Year"),
                ("Thám tử báo về quân Tây Sơn còn tập hợp ở Nghệ An và Thanh Hóa.", "fast", "deep_dive_step", "focus", "medium_shot", "Qing scout on horseback reporting outdated military intelligence to complacent general"),
                ("Tôn Sĩ Nghị tin chắc đối phương không thể vượt đường giá rét chỉ trong vài ngày.", "normal", "deep_dive_step", "focus", "close_up", "Ton Si Nghi waving hand mockingly with dismissive smile over hot tea bowl"),
                ("Sự chủ quan", "fast", "deep_dive_step", "pan", "medium_shot", "Qing soldiers dropping guard, drinking wine and playing dice in Thang Long encampment"),
                ("đẩy hai mươi chín vạn quân", "normal", "deep_dive_step", "pan", "full_scene", "Massive Qing troop camps sprawling lazily along banks of Red River without defensive trenches"),
                ("vào chiếc bẫy giăng sẵn.", "slow", "deep_dive_step", "focus", "close_up", "A closing military tiger trap snapping shut over Qing dragon insignia"),
            ],
        },
        {
            "id": "SC09",
            "title": "Lời bình: Nghệ thuật tâm lý chiến đỉnh cao",
            "purpose": "Nhận định về bức thư cầu hòa và quyết định ăn Tết sớm ở Tam Điệp",
            "narrative_situation": "editorial_commentary",
            "narrative_phase": "structural_model",
            "setting": "Tam Diep forward defense line with flowering peach branches against mountain backdrop.",
            "narration": "Nghệ thuật quân sự của người anh hùng áo vải còn nằm ở khả năng điều khiển tâm lý đối phương. Ông gửi thư cầu hòa nhún nhường để ru ngủ sự cảnh giác của kẻ thù. Đồng thời, ông tổ chức ăn Tết sớm tại Tam Điệp, hẹn mùng bảy Tết vào Thăng Long mở tiệc. Lời tuyên bố đanh thép thắp sáng niềm tin tất thắng.",
            "beats": [
                ("Nghệ thuật quân sự của người anh hùng áo vải còn nằm ở khả năng điều khiển tâm lý đối phương.", "slow", "editorial_commentary", "establish", "medium_shot", "Emperor Quang Trung seated thoughtfully in military command tent reviewing psychological strategy"),
                ("Ông gửi thư cầu hòa nhún nhường để ru ngủ sự cảnh giác của kẻ thù.", "slow", "editorial_commentary", "focus", "close_up", "Diplomatic parchment scroll inscribed with polite deceptive peace overtures"),
                ("Đồng thời, ông tổ chức ăn Tết sớm tại Tam Điệp,", "normal", "editorial_commentary", "pan", "medium_shot", "Qing general reading humble envoy letter and puffing chest in arrogant pride"),
                ("hẹn mùng bảy Tết vào Thăng Long mở tiệc.", "normal", "editorial_commentary", "pan", "full_scene", "Tam Diep base camp soldiers raising wine cups under festive peach blossom boughs"),
                ("Lời tuyên bố đanh thép", "normal", "editorial_commentary", "focus", "close_up", "Emperor's fierce proclamation carved in bold woodcut characters: MÙNG BẢY VÀO THĂNG LONG"),
                ("thắp sáng niềm tin tất thắng.", "slow", "editorial_commentary", "focus", "medium_shot", "Flames of determination reflected in eyes of thousands of battle-ready warriors"),
            ],
        },
        {
            "id": "SC10",
            "title": "Đêm mùng năm Tết Kỷ Dậu rực lửa",
            "purpose": "Trận công kiên Ngọc Hồi Đống Đa và chiến thắng vượt kế hoạch 2 ngày",
            "narrative_situation": "case_study",
            "narrative_phase": "actionable_resolution",
            "setting": "Breached barricades of Ngoc Hoi fort bathed in fire and smoke on do paper #EFE4C8.",
            "narration": "Đêm mùng bốn rạng sáng mùng năm Tết Kỷ Dậu, bão lửa Tây Sơn ập xuống đồn Ngọc Hồi. Đội quân vừa đi vừa ngủ mười ngày trước nay hóa thành những chiến binh dũng mãnh cưỡi voi xông thẳng trận địa. Đồn lũy giặc sụp đổ chớp nhoáng, Tôn Sĩ Nghị hoảng hốt bỏ chạy qua cầu phao sông Nhị Hà.",
            "beats": [
                ("Đêm mùng bốn rạng sáng mùng năm Tết Kỷ Dậu,", "fast", "case_study", "establish", "full_scene", "Pre-dawn assault with thousands of bamboo storm shields rushing toward Ngoc Hoi fortress"),
                ("bão lửa Tây Sơn ập xuống đồn Ngọc Hồi.", "burst", "case_study", "focus", "close_up", "Firepot catapults hurling flaming oil jars shattering wooden fortification towers"),
                ("Đội quân vừa đi vừa ngủ mười ngày trước nay hóa thành những chiến binh dũng mãnh", "normal", "case_study", "pan", "medium_shot", "Fully rested fierce warriors charging through breached palisades with halberds flashing"),
                ("cưỡi voi xông thẳng trận địa.", "burst", "case_study", "focus", "close_up", "Heroic war elephant with iron-tipped tusks crushing enemy cannon barricades"),
                ("Đồn lũy giặc sụp đổ chớp nhoáng,", "fast", "case_study", "pan", "medium_shot", "Ton Si Nghi fleeing in panic without armor dropping his official golden seal in mud"),
                ("Tôn Sĩ Nghị hoảng hốt bỏ chạy qua cầu phao sông Nhị Hà.", "normal", "case_study", "focus", "full_scene", "Collapsed pontoon bridge on Red River with fleeing enemy troops drowning in cold current"),
            ],
        },
        {
            "id": "SC11",
            "title": "Khúc tráng ca ngàn năm vang vọng",
            "purpose": "Khải hoàn Thăng Long và khúc vĩ thanh lịch sử",
            "narrative_situation": "outro",
            "narrative_phase": "actionable_resolution",
            "setting": "Imperial citadel gate of Thang Long with blossoming spring flowers and royal banner.",
            "narration": "Trưa mùng năm Tết, vua Quang Trung ngự trên voi chiến tiến vào Thăng Long, áo bào đỏ đã sạm đen khói súng. Cuộc hành quân thần tốc ba người một cáng đi vào huyền thoại như minh chứng bất tử cho trí tuệ Việt Nam. Nếu thấy hào khí cha ông đáng nhớ, ở lại nghe tiếp những trận đánh sau nhé.",
            "beats": [
                ("Trưa mùng năm Tết, vua Quang Trung ngự trên voi chiến tiến vào Thăng Long,", "normal", "outro", "establish", "full_scene", "Triumphant entry of King Quang Trung riding majestic war elephant into Thang Long gates"),
                ("áo bào đỏ đã sạm đen khói súng.", "normal", "outro", "focus", "close_up", "Close-up of royal vermilion robe singed with dark gunpowder smoke stains of victory"),
                ("Cuộc hành quân thần tốc ba người một cáng đi vào huyền thoại", "normal", "outro", "pan", "medium_shot", "Bronze monument carving honoring the heroic three-man stretcher squads"),
                ("như minh chứng bất tử cho trí tuệ Việt Nam.", "slow", "outro", "focus", "close_up", "Golden sun rising over sacred dragon land with peaceful blossoming plum trees"),
                ("Nếu thấy hào khí cha ông đáng nhớ, ở lại nghe tiếp những trận đánh sau nhé.", "normal", "outro", "pan", "medium_shot", "Antique woodcut invitation scroll opening to future epic historical chapters"),
                ("SỬ KỂ LẠI", "hold", "outro", "hold", "full_scene", "Official ancient red seal of SU KE LAI stamped with pride on handmade do-paper canvas", True),
            ],
        },
    ]

    long_brief = {
        "schema_version": "3.0",
        "topic": long_topic,
        "audience": "Khán giả đam mê lịch sử dân tộc, chiến lược quân sự và những mốc son hào hùng của Việt Nam",
        "goal": "Phân tích toàn diện nghệ thuật hậu cần, tâm lý chiến và chiến thuật ba người một cáng giúp vua Quang Trung đại phá hai mươi chín vạn quân Thanh năm 1789",
        "video_type": "explainer",
        "duration": {"min_seconds": 185.0, "max_seconds": 245.0},
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "Tin dữ giặc chiếm Thăng Long và lễ đăng cơ núi Bân năm 1788"},
            {"id": "R02", "text": "Bài toán bất khả thi về cự ly sáu trăm cây số trong ba mươi ngày"},
            {"id": "R03", "text": "Chặng tuyển quân thần tốc tại Nghệ An nâng quân số lên mười vạn"},
            {"id": "R04", "text": "Sáng tạo đội hình hành quân ba người một cáng luân phiên liên tục"},
            {"id": "R05", "text": "Cỗ máy tuần hoàn bảo tồn năng lượng và mid-cta giao lưu"},
            {"id": "R06", "text": "Lời bình sâu sắc về tư duy quản trị năng lượng thời trung đại"},
            {"id": "R07", "text": "Khẩu phần hậu cần khô với bánh chưng không nổi lửa giữ tuyệt mật"},
            {"id": "R08", "text": "Cú lừa thám báo khiến Tôn Sĩ Nghị chủ quan mở tiệc ăn Tết linh đình"},
            {"id": "R09", "text": "Lời bình: Nghệ thuật tâm lý chiến đỉnh cao và lời hẹn ăn Tết mùng bảy"},
            {"id": "R10", "text": "Bão lửa Ngọc Hồi Đống Đa đại phá hai mươi chín vạn quân thù"},
            {"id": "R11", "text": "Khải hoàn Thăng Long trưa mùng năm Tết và khúc tráng ca muôn đời"},
        ],
        "language": "vi",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Hoàng Lê Nhất Thống Chí",
                "reference": "Ngô Gia Văn Phái (1789). Hoàng Lê Nhất Thống Chí, Hồi 14; Viện Sử Học biên dịch.",
                "facts": [
                    "Đội hình ba người một cáng luân phiên hai người khiêng một người nằm ngủ suốt chặng đường hành quân.",
                    "Vua Quang Trung cho quân ăn Tết sớm ở Tam Điệp vào ngày hai mươi tháng Chạp và tuyên bố mùng bảy sẽ vào Thăng Long ăn Tết lại.",
                    "Trận Ngọc Hồi Đống Đa toàn thắng trưa mùng năm Tết Kỷ Dậu, sớm hơn hai ngày so với kế hoạch ban đầu.",
                ],
            },
            {
                "id": "SRC02",
                "title": "Đại Nam Chính Biên Liệt Truyện - Truyện Ngụy Tây",
                "reference": "Quốc Sử Quán Triều Nguyễn. Đại Nam Liệt Truyện, Tập 2, Chính Biên.",
                "facts": [
                    "Quân Tây Sơn tuyển thêm một vạn quân tại Nghệ An theo tỷ lệ ba đinh lấy một lính.",
                    "Quân lính dùng rơm ướt quấn quanh người và khiêng ván chắn dập lửa để công phá đồn lũy Ngọc Hồi.",
                ],
            },
        ],
        "outputs": [{"aspect_ratio": "16:9", "language": "vi", "subtitles": False, "voice": ch.voice, "speed": ch.speed}],
        "planning": {
            "success_criteria": [
                "Tái hiện trọn vẹn hào khí anh hùng 1789 bằng tranh khắc gỗ Đông Hồ truyền thống trên 66 khung hình độc bản",
                "Phân tích chiều sâu tư duy hậu cần và kỷ luật quân sự, triệt tiêu hoàn toàn lối kể thần bí hóa",
            ],
            "avoid": ["Tuyệt đối không dùng văn mẫu AI cliché.", "Không dùng câu dài thở dốc quá 18 âm tiết."],
            "prior_knowledge": "Không đòi hỏi nghiên cứu chuyên sâu.",
            "pacing": "Kể chuyện điện ảnh, trầm hùng, kịch tính, tôn trọng lịch sử.",
            "domain_requirements": [],
            "assumptions": ["Mỗi phân cảnh được cân chỉnh theo công thức âm học P_tail và dung sai drift <= 0.3s."],
            "text_style": {
                "font": "sans-serif rõ nét, cùng kiểu và độ đậm xuyên suốt",
                "color": "#172033",
                "outline": "nền sáng tương phản",
                "size": "dễ đọc trên màn hình ngang (khung 16:9)",
                "placement": "cách mép ít nhất 10%; bố cục ngang thoáng, không ép lề dọc điện thoại",
            },
            "speech_rates": {
                "vi": {"units_per_second": 4.0, "uncertainty": 0.15, "source": "Acoustic calibrated cadence"},
                "en": {"units_per_second": 2.5, "uncertainty": 0.25, "source": "Estimated English reading rate"},
            },
        },
        "packaging": {
            "youtube_title": long_title,
            "thumbnail_spec": {
                "visual_hook": "Vua Quang Trung ngự trên lưng voi chiến áo bào sạm khói đối lập với đội hình cáng võng ba người thâu đêm",
                "text_overlay": "HÀNH QUÂN THẦN TỐC",
                "contrast_pair": "Đội hình cáng võng bí mật vs Bão lửa đại phá 29 vạn giặc",
            },
            "channel_pillar": "Hào Khí Lịch Sử & Nghệ Thuật Quân Sự Việt Nam",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["su ke lai", "quang trung", "tay son 1789", "hanh quan than toc", "ba nguoi mot cang", "dai pha quan thanh"],
            "cta_plan": {
                "mid_cta": "Bạn nghĩ gì về kỷ luật hành quân này, hãy lưu video lại để cùng luận bàn nhé.",
                "close": "Nếu thấy hào khí cha ông đáng nhớ, ở lại nghe tiếp những trận đánh sau nhé.",
                "endcard_text": "SỬ KỂ LẠI",
            },
            "editorial_stance": {
                "myth_debunked": "Dân gian truyền miệng rằng quân Tây Sơn dùng phép tàng hình hay thần chú bí hiểm để bay từ Phú Xuân ra Thăng Long.",
                "why_generic_advice_fails": "Cách nhìn mang màu sắc huyền bí phủ nhận hoàn toàn tư duy hậu cần và tổ chức quân sự thiên tài của vua Quang Trung.",
                "channel_verdict": "Chiến thắng thần tốc không đến từ phép màu, mà sinh ra từ kỷ luật thép và giải pháp hậu cần xoay tua ba người một cáng.",
                "tradeoff_or_blindspot": "Cuộc hành quân ép thể lực đến tận cùng giới hạn sinh học, đòi hỏi sự hy sinh thầm lặng của hàng vạn binh lính vô danh.",
            },
            "actionable_value": {
                "core_mechanism": "Đội hình ba người một cáng luân phiên hai người khiêng một người ngủ giúp đạo quân hành tiến liên tục ngày đêm không dừng bước.",
                "practical_rule_of_thumb": "Quy tắc xoay tua năng lượng: chia nhóm ba người đảo ca liên tục trên đường cơ động để duy trì sức chiến đấu tối đa.",
                "real_world_scenario": "Quân đoàn Tây Sơn vượt hơn sáu trăm cây số hiểm trở trong ba mươi ngày, đánh tan đồn Ngọc Hồi ngay trưa mùng năm Tết Kỷ Dậu.",
            },
        },
        "youtube_title": long_title,
        "thumbnail_spec": {
            "visual_hook": "Vua Quang Trung ngự trên lưng voi chiến áo bào sạm khói đối lập với đội hình cáng võng ba người thâu đêm",
            "text_overlay": "HÀNH QUÂN THẦN TỐC",
            "contrast_pair": "Đội hình cáng võng bí mật vs Bão lửa đại phá 29 vạn giặc",
        },
        "channel_pillar": "Hào Khí Lịch Sử & Nghệ Thuật Quân Sự Việt Nam",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["su ke lai", "quang trung", "tay son 1789", "hanh quan than toc", "ba nguoi mot cang", "dai pha quan thanh"],
        "cta_plan": {
            "mid_cta": "Bạn nghĩ gì về kỷ luật hành quân này, hãy lưu video lại để cùng luận bàn nhé.",
            "close": "Nếu thấy hào khí cha ông đáng nhớ, ở lại nghe tiếp những trận đánh sau nhé.",
            "endcard_text": "SỬ KỂ LẠI",
        },
        "channel_profile": stamp,
        "engagement": asdict(ch.engagement),
        "editorial_stance": {
            "myth_debunked": "Dân gian truyền miệng rằng quân Tây Sơn dùng phép tàng hình hay thần chú bí hiểm để bay từ Phú Xuân ra Thăng Long.",
            "why_generic_advice_fails": "Cách nhìn mang màu sắc huyền bí phủ nhận hoàn toàn tư duy hậu cần và tổ chức quân sự thiên tài của vua Quang Trung.",
            "channel_verdict": "Chiến thắng thần tốc không đến từ phép màu, mà sinh ra từ kỷ luật thép và giải pháp hậu cần xoay tua ba người một cáng.",
            "tradeoff_or_blindspot": "Cuộc hành quân ép thể lực đến tận cùng giới hạn sinh học, đòi hỏi sự hy sinh thầm lặng của hàng vạn binh lính vô danh.",
        },
        "actionable_value": {
            "core_mechanism": "Đội hình ba người một cáng luân phiên hai người khiêng một người ngủ giúp đạo quân hành tiến liên tục ngày đêm không dừng bước.",
            "practical_rule_of_thumb": "Quy tắc xoay tua năng lượng: chia nhóm ba người đảo ca liên tục trên đường cơ động để duy trì sức chiến đấu tối đa.",
            "real_world_scenario": "Quân đoàn Tây Sơn vượt hơn sáu trăm cây số hiểm trở trong ba mươi ngày, đánh tan đồn Ngọc Hồi ngay trưa mùng năm Tết Kỷ Dậu.",
        },
        "video_engine": "flow_video",
    }

    content_scenes_long = []
    outline_long = []
    for s_idx, s in enumerate(long_scenes_data):
        sc_id = s["id"]
        outline_long.append({
            "scene_id": sc_id,
            "purpose": s["purpose"],
            "requirements": [f"R{s_idx+1:02d}"],
            "transition": "Tiếp tục theo trình tự diễn biến nội dung",
        })
        sc_images = []
        sc_beats = []
        for b_idx, b in enumerate(s["beats"]):
            quote_text = b[0]
            tempo_val = b[1]
            sit_val = b[2]
            intent_val = b[3]
            shot_val = b[4]
            desc_text = b[5]
            is_endcard_flag = b[6] if len(b) > 6 else False
            img_id = f"{sc_id}_I{b_idx+1}"
            beat_id = f"{sc_id}_B{b_idx+1}"

            full_desc = f"2D Vietnamese Dong Ho folk woodblock-print illustration in 16:9 widescreen: {desc_text}, bold carved black woodcut outlines (#1E1E1E), flat natural pigment fills in vermilion (#B5332E), pagoda-tree yellow (#D9A520), indigo (#2C4A6E) and leaf green (#5E7D3A) on handmade warm do-paper canvas (#EFE4C8), orthographic 2D, no photorealism, no 3D."
            motion_str = f"Smooth 2D Dong Ho woodcut folk motion in widescreen 16:9. {desc_text[:90]}, silent visual storytelling, no talking, no lip movement"

            sc_images.append({
                "id": img_id,
                "description": full_desc,
                "character_ids": ["CH01"],
                "preserve": "Dong Ho folk woodblock print style, handmade do-paper canvas #EFE4C8, carved black outlines #1E1E1E, period costume",
                "change": desc_text[:80],
                "reason": "Narration-locked full-frame beat.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": shot_val,
                "tempo": tempo_val,
                "narrative_situation": sit_val,
                "emphasis_text": "",
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": True,
                "explanation": {
                    "quote": quote_text,
                    "relation": "context",
                    "source_terms": ["Tây Sơn", "Quang Trung", "hành quân"],
                    "visual_terms": ["Đông Hồ", "tranh khắc gỗ"],
                },
                "motion_prompt": motion_str,
            })
            sc_beats.append({
                "id": beat_id,
                "image_id": img_id,
                "purpose": s["purpose"],
                "anchor": {"vi": {"quote": quote_text, "occurrence": 1}},
                "effect": "hold" if is_endcard_flag else "cut",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": tempo_val,
                "narrative_situation": sit_val,
                "camera_intent": intent_val,
                "shot_type": shot_val,
                "is_endcard": is_endcard_flag if is_endcard_flag else None,
            })

        content_scenes_long.append({
            "id": sc_id,
            "title": s["title"],
            "purpose": s["purpose"],
            "action": f"Narrative enactment of {s['title'].lower()} in traditional Dong Ho folk style.",
            "setting": s["setting"],
            "narrative_phase": s["narrative_phase"],
            "camera": f"Semantic camera: {s['beats'][0][3]} transitioning across beats.",
            "narration": s["narration"],
            "requirements": [f"R{s_idx+1:02d}"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01", "SRC02"] if s_idx >= 7 else ["SRC01"],
            "images": sc_images,
            "beats": sc_beats,
        })

    long_brief_hash = compute_brief_hash(long_brief)
    long_content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": long_brief_hash,
        "topic": long_topic,
        "duration": long_brief["duration"],
        "style": long_brief["style"],
        "required_points": long_brief["required_points"],
        "characters": [cast],
        "scenes": content_scenes_long,
        "coverage": [
            {"requirement_id": f"R{i+1:02d}", "scene_id": s["id"], "quote": s["narration"][:60]}
            for i, s in enumerate(long_scenes_data)
        ],
        "outline": outline_long,
        "claims": [
            {
                "scene_id": "SC04",
                "quote": "vua Quang Trung sáng tạo chiến thuật ba người một cáng",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Vua Quang Trung cho quân chia làm từng tốp ba người mang một chiếc cáng, hai người khiêng một người nằm nghỉ, thay nhau chạy suốt ngày đêm.",
            },
            {
                "scene_id": "SC09",
                "quote": "hẹn mùng bảy Tết vào Thăng Long mở tiệc",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Vua Quang Trung cho quân ăn Tết sớm ở Tam Điệp vào ngày hai mươi tháng Chạp và tuyên bố mùng bảy sẽ vào Thăng Long ăn Tết lại.",
            },
        ],
        "revision_response": [],
        "open_questions": [],
    }

    long_competitor = {
        "channel_id": "su_ke_lai",
        "job_id": "su-ke-lai-batch3-16x9",
        "topic": long_topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Đu Đuốc & Việt Sử Kiêu Hùng",
                    "top_performing_videos": [
                        {
                            "title": "Bí Ẩn Cuộc Hành Quân Thần Tốc Tây Sơn 1789",
                            "views": "2.9M views",
                            "hook_technique": "Cảnh báo cự ly 600km vượt đèo lội suối trong giá rét mùa đông.",
                            "pacing_structure": "Nguy cơ mất nước -> Tuyển quân Nghệ An -> Sáng tạo ba người một cáng -> Hậu cần bánh chưng -> Đêm quyết chiến Ngọc Hồi -> Khải hoàn Thăng Long.",
                            "retention_driver": "Khai thác tư duy quản trị quân sự và nghệ thuật tâm lý chiến đỉnh cao."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Phân tích cặn kẽ giải pháp cơ học ba người một cáng thay vì chỉ ca ngợi chung chung.",
                        "Kết hợp mỹ thuật dân gian Đông Hồ tạo bản sắc văn hóa thuần Việt sâu sắc."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 17,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Tin cấp báo thất thủ Thăng Long đối lập với lễ tế trời núi Bân và lời thề xuất quân quyết tử.",
                "counter_intuitive_truth_slap": "Không có phép thần bay lượn, chiến thắng thần tốc đến từ giải pháp cơ học xoay tua ba người một cáng."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Khắc họa thế ngàn cân treo sợi tóc của đất nước cuối năm 1788."},
                {"phase": "empirical_conflict", "purpose": "Phân tích bài toán bất khả thi về cự ly và thời gian."},
                {"phase": "structural_model", "purpose": "Bóc tách giải pháp xoay tua ba người một cáng và hậu cần khô."},
                {"phase": "actionable_resolution", "purpose": "Trận công phá Ngọc Hồi Đống Đa rực lửa và khúc tráng ca khải hoàn."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Sequential daisy-chain linking Start Frame to End Frame across all scenes."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Hào Khí Lịch Sử & Nghệ Thuật Quân Sự Việt Nam",
            "myth_debunked": "Dân gian truyền miệng rằng quân Tây Sơn dùng phép tàng hình hay thần chú bí hiểm để bay từ Phú Xuân ra Thăng Long.",
            "channel_verdict": "Chiến thắng thần tốc không đến từ phép màu, mà sinh ra từ kỷ luật thép và giải pháp hậu cần xoay tua ba người một cáng.",
            "actionable_rule_of_thumb": "Quy tắc xoay tua năng lượng: chia nhóm ba người đảo ca liên tục trên đường cơ động để duy trì sức chiến đấu tối đa."
        },
        "cta_and_spinoff_strategy": {
            "mid_cta": "Bạn nghĩ gì về kỷ luật hành quân này, hãy lưu video lại để cùng luận bàn nhé.",
            "close": "Nếu thấy hào khí cha ông đáng nhớ, ở lại nghe tiếp những trận đánh sau nhé.",
            "endcard_text": "SỬ KỂ LẠI"
        }
    }

    return (
        short_brief, outline_short, short_content, short_competitor,
        long_brief, outline_long, long_content, long_competitor,
    )


def save_job(job_id: str, brief: dict, outline: dict, content: dict, competitor: dict) -> None:
    job_dir = SYS_DIR / "runs" / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    (job_dir / "brief.json").write_text(json.dumps(brief, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (job_dir / "outline.json").write_text(json.dumps(outline, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (job_dir / "content.json").write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (job_dir / "competitor_research.json").write_text(json.dumps(competitor, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Also compile images.json manifest
    compiled_items = []
    aspect = brief.get("aspect_ratio", "9:16")
    channel_id = brief.get("channel_profile", {}).get("id", "")
    ch_profile = get_channel(channel_id) if channel_id else None
    for sc in content.get("scenes", []):
        for img in sc.get("images", []):
            if ch_profile:
                final_prompt = compile_channel_scene_prompt(
                    ch_profile, brief, content, sc, img, aspect_ratio=aspect
                )
            else:
                final_prompt = img.get("description", "")
            aspect_tag = aspect.replace(":", "x")
            compiled_items.append({
                "image_id": img.get("id"),
                "scene_id": sc.get("id"),
                "path": f"revisions/images/1/{img.get('id')}_{aspect_tag}.jpg",
                "prompt": final_prompt,
                "motion_prompt": img.get("motion_prompt", ""),
            })

    images_manifest = {
        "checkpoint": "compiled",
        "total_images": len(compiled_items),
        "items": compiled_items,
    }
    (job_dir / "images.json").write_text(json.dumps(images_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved {job_id}: {len(content['scenes'])} scenes, {len(compiled_items)} compiled images")


def main() -> None:
    print("Generating ua_sao_vay packages...")
    (
        ua_s_brief, ua_s_outline, ua_s_content, ua_s_comp,
        ua_l_brief, ua_l_outline, ua_l_content, ua_l_comp,
    ) = build_ua_sao_vay_data()

    save_job("ua-sao-vay-batch3-9x16", ua_s_brief, {"outline": ua_s_outline}, ua_s_content, ua_s_comp)
    save_job("ua-sao-vay-batch3-16x9", ua_l_brief, {"outline": ua_l_outline}, ua_l_content, ua_l_comp)

    print("Generating su_ke_lai packages...")
    (
        su_s_brief, su_s_outline, su_s_content, su_s_comp,
        su_l_brief, su_l_outline, su_l_content, su_l_comp,
    ) = build_su_ke_lai_data()

    save_job("su-ke-lai-batch3-9x16", su_s_brief, {"outline": su_s_outline}, su_s_content, su_s_comp)
    save_job("su-ke-lai-batch3-16x9", su_l_brief, {"outline": su_l_outline}, su_l_content, su_l_comp)

    print("All 4 packages successfully generated!")


if __name__ == "__main__":
    main()
