#!/usr/bin/env python3
"""Generator & Pre-synthesizer for 18 Vietnamese Short 9:16 Full-Chain Specifications.

Generates:
  sys/channels/vn_rebuilt_style_specs/<slug>/<slug>_short_fullchain_spec.json
Pre-synthesizes:
  video/vn_pilot_<slug_underscored>_short_fullchain/narration_master.wav
  video/vn_pilot_<slug_underscored>_short_fullchain/_work_short/narration.wav
  video/vn_pilot_<slug_underscored>_short_fullchain/_work_short/subtitles_kinetic_9x16.ass
  video/vn_pilot_<slug_underscored>_short_fullchain/_work_short/subtitles.srt
  video/vn_pilot_<slug_underscored>_short_fullchain/_work_short/watermark_100x100.png
  video/vn_pilot_<slug_underscored>_short_fullchain/<slug_underscored>_short_aligned_spec.json
"""

from __future__ import annotations

import json
import logging
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure sys is in PYTHONPATH
SYS_DIR = Path(__file__).resolve().parent.parent
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

import channels.vn_flow_video_formulas as vf
from tools.produce_vn_dual_mode import (
    build_clean_sidecar_srt,
    build_vn_kinetic_ass_subtitles,
    make_rounded_watermark,
    synthesize_vn_narration_and_words,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("fleet_architect_shorts")

# Safety guard banned terms (case-insensitive substring match)
FLOW_UNSAFE_PATTERNS = [
    r"\bgun\b",
    r"\bshotgun\b",
    r"\bbullet\b",
    r"\bshoot\b",
    r"\bblood\b",
    r"\bcorpse\b",
    r"\bkill\b",
    r"\bweapon\b",
    r"\bexplosion\b",
    r"\bbomb\b",
    r"\bsuicide\b",
    r"\bmurder\b",
    r"\bdead body\b",
]

BANNED_CTA_PHRASES = [
    "đừng quên like",
    "nhấn chuông",
    "bấm chuông",
    "like share",
    "like và share",
    "subscribe",
    "đăng ký kênh",
    "ấn theo dõi",
    "bấm theo dõi",
    "hãy like",
    "nhớ like",
    "ủng hộ kênh",
]

def count_syllables(text: str) -> int:
    clean = re.sub(r"\[pause:[^\]]+\]", "", text).strip()
    return len([w for w in clean.split() if w])

def validate_spec_safety_and_rules(spec: Dict[str, Any]) -> None:
    slug = spec["channel_slug"]
    title = spec["youtube_title"]
    if len(title) > 55:
        raise ValueError(f"[{slug}] youtube_title exceeds 55 chars: '{title}' ({len(title)} chars)")

    # CTA syllable budget
    cta = spec.get("cta_plan", {})
    bridge = cta.get("bridge", "")
    close = cta.get("close", "")
    b_syl = count_syllables(bridge)
    c_syl = count_syllables(close)
    if b_syl > 22:
        raise ValueError(f"[{slug}] bridge CTA exceeds 22 syllables: '{bridge}' ({b_syl})")
    if c_syl > 24:
        raise ValueError(f"[{slug}] close CTA exceeds 24 syllables: '{close}' ({c_syl})")

    for phrase in BANNED_CTA_PHRASES:
        if phrase in bridge.lower() or phrase in close.lower():
            raise ValueError(f"[{slug}] Banned CTA phrase '{phrase}' in CTA: bridge='{bridge}', close='{close}'")

    beats = spec.get("beats", [])
    if len(beats) not in (12, 13):
        raise ValueError(f"[{slug}] Beats count must be 12 or 13, got {len(beats)}")

    hook_syl = count_syllables(beats[0]["narration"])
    if hook_syl > 18:
        raise ValueError(f"[{slug}] S01 hook exceeds 18 syllables: '{beats[0]['narration']}' ({hook_syl})")

    # Flow safety checks
    for b in beats:
        p = b.get("prompt", "")
        mp = b.get("motion_prompt", "")
        for pat in FLOW_UNSAFE_PATTERNS:
            if re.search(pat, p, re.IGNORECASE):
                raise ValueError(f"[{slug}] Unsafe word '{pat}' found in beat {b['id']} prompt: {p}")
            if re.search(pat, mp, re.IGNORECASE):
                raise ValueError(f"[{slug}] Unsafe word '{pat}' found in beat {b['id']} motion_prompt: {mp}")
        # Zero text in keyframe prompts
        if "zero text" not in p.lower() and "no text" not in p.lower() and "strictly zero text" not in p.lower():
            raise ValueError(f"[{slug}] Beat {b['id']} prompt missing 'zero text' directive: {p}")


# Data definitions for the 18 channels
RAW_CHANNEL_SPECS: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # 1. banh-rang
    # -------------------------------------------------------------------------
    {
        "slug": "banh-rang",
        "youtube_title": "Chuỗi Cung Ứng Biển: Mắt Xích Thầm Lặng Đổi Đời Bạn",
        "thumbnail_text": "CHUỖI CUNG ỨNG",
        "visual_hook": "Vertical 9:16 macro cross-section view of automated container terminal with giant yellow gantry cranes loading a 20,000 TEU vessel under morning daylight, zero overlays, 25% margin",
        "bridge": "Khám phá toàn cảnh bài toán logistics biển trên video dài của kênh.",
        "close": "Hãy trân trọng từng món đồ nhỏ bé bạn đang cầm trên tay.",
        "beats": [
            {
                "id": "S01",
                "narration": "Một hành trình hai mươi nghìn cây số trên đại dương mênh mông,",
                "prompt": "Vertical 9:16 aerial establishing shot of a massive industrial deepwater container shipping port terminal at dawn, rows of giant yellow gantry cranes loading a 400-meter container vessel, turquoise open ocean water, photorealistic Wendover Productions logistics aesthetic, 8k documentary still, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth 35mm commercial dolly push-in toward the towering container vessel berthed at dawn dock, cranes lifting containers with locked physical geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "tưởng như bình thường nhưng lại là kỳ quan chuỗi cung ứng ngầm.",
                "prompt": "Vertical 9:16 eye-level architectural shot along the side of a massive 400-meter container ship, towering stacks of colorful metal shipping containers locked together, morning sun glinting off steel hulls, crisp f/5.6 depth of field, strictly zero text, no cartoons.",
                "motion_prompt": "Steady lateral engineering tracking pass along the colossal steel hull, containers stacked in perfect rigid alignment, water wake lapping against hull, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Mười lăm năm trước, những con tàu khổng lồ thế này là điều không tưởng,",
                "prompt": "Vertical 9:16 high-angle architectural survey of a modern shipyard drydock with massive container ships under assembly, weathered industrial steel and safety orange accents, crisp directional daylight, strictly zero text, no cartoons.",
                "motion_prompt": "Slow cinematic vertical pedestal move rising above the drydock scaffolding, massive steel plates resting with rigid load-bearing stability, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": None,
            },
            {
                "id": "S04",
                "narration": "khi chiều dài của chúng bằng bốn sân bóng đá tiêu chuẩn cộng lại.",
                "prompt": "Vertical 9:16 panoramic aerial view showing the full 400-meter length of a container ship navigating through a calm harbor channel, dramatic scale comparison with small tugboats guiding it, crisp blue ocean, strictly zero text, no cartoons.",
                "motion_prompt": "High-altitude architectural aerial survey following the massive ship moving forward at steady speed, realistic bow waves cutting through calm harbor water, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S03",
            },
            {
                "id": "S05",
                "narration": "Hàng vạn thùng hàng được định vị chính xác bằng hệ thống điều phối tự động.",
                "prompt": "Vertical 9:16 precision cutaway shot of an automated robotic port gantry crane spreader lowering onto a steel container with mechanical alignment, industrial hydraulic pistons, crisp metallic textures, strictly zero text, no cartoons.",
                "motion_prompt": "Precision cutaway dolly push-in on the crane spreader locking smoothly into corner castings, realistic hydraulic dampening, steady industrial lighting, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S06",
                "narration": "Chỉ cần một mắt xích tại cảng biển bị nghẽn trong nửa ngày,",
                "prompt": "Vertical 9:16 wide shot of multiple container ships idling at sea outside a congested deepwater port, hazy sunset horizon, calm sea with anchor chains deployed, high atmospheric realism, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle tracking pass across the idling fleet waiting offshore, water ripples catching golden sunset rays, massive ships holding locked position, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": "S05",
            },
            {
                "id": "S07",
                "narration": "hàng trăm chuyến tàu ngoài khơi lập tức phải xếp hàng dài trên biển.",
                "prompt": "Vertical 9:16 telephoto compressed perspective showing five massive container ships anchored in single file off a foggy coastline, ocean swell, cool maritime grading, strictly zero text, no cartoons.",
                "motion_prompt": "Slow telephoto push-in compressing the line of anchored ships in the fog, gentle natural wave rolling against steel bows, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S06",
            },
            {
                "id": "S08",
                "narration": "Chi phí vận chuyển toàn cầu khi đó lập tức tăng vọt gấp năm lần.",
                "prompt": "Vertical 9:16 macro shot of industrial brass ship throttle levers and navigational dials on a commercial vessel bridge, dials resting at idle, warm instrument backlighting, strictly zero text, no cartoons.",
                "motion_prompt": "Slow macro rack focus across the brass control levers to the bridge window overlooking the dark ocean, steady specular gleam, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Hàng triệu món đồ trên bàn làm việc của bạn đều đi qua hải trình này.",
                "prompt": "Vertical 9:16 warm indoor tabletop photograph of a modern wooden desk with a laptop, ceramic coffee mug, and notebook, bathed in soft morning window light, high aesthetic realism, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth dolly pullback from the ceramic mug on the wooden desk, revealing a calm productive morning workspace, soft natural light, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S10",
                "narration": "Từ linh kiện điện tử tinh xảo cho đến hạt cà phê thơm lừng buổi sáng.",
                "prompt": "Vertical 9:16 macro top-down split composition showing raw roasted coffee beans beside a sleek anodized aluminum smartphone casing on polished slate, natural daylight, strictly zero text, no cartoons.",
                "motion_prompt": "Gentle downward push-in highlighting the tactile contrast between organic coffee beans and precision milled metal, steady light, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S09",
            },
            {
                "id": "S11",
                "narration": "Tất cả đều vận hành trơn tru nhờ những bánh răng logistics thầm lặng.",
                "prompt": "Vertical 9:16 majestic wide aerial view of a container mega-ship cruising through open blue ocean at full steam, white foam wake stretching to the horizon under clear sunny sky, strictly zero text, no cartoons.",
                "motion_prompt": "Sweeping cinematic aerial tracking shot alongside the ship cruising steadily, foam wake trailing into deep turquoise water, grand monumental scale, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Khám phá toàn cảnh bài toán logistics biển trên video dài của kênh.",
                "prompt": "Vertical 9:16 macro tabletop shot of an architectural marine map and nautical compass resting on polished mahogany table beside a glowing tablet screen, warm amber studio light, strictly zero text, no cartoons.",
                "motion_prompt": "Slow deliberate push-in toward the brass nautical instruments and tablet display, warm reflections on polished wood, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy trân trọng từng món đồ nhỏ bé bạn đang cầm trên tay.",
                "prompt": "Vertical 9:16 contemplative shot of human hands holding a warm ceramic coffee cup looking out a high window toward a distant industrial harbor at sunrise, tranquil mood, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle dolly pullback from the hands and cup toward the sunrise harbor view, soft golden morning light, serene ending, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 2. luat-doi-thuong
    # -------------------------------------------------------------------------
    {
        "slug": "luat-doi-thuong",
        "youtube_title": "3 Bẫy Hợp Đồng Thuê Nhà Khiến Bạn Mất Trắng Cọc",
        "thumbnail_text": "BẪY HỢP ĐỒNG",
        "visual_hook": "Vertical 9:16 macro forensic tactile photograph of printed rental contract paper under directional tungsten lamp with red correction pen, zero overlays, 25% margin",
        "bridge": "Xem cẩm nang pháp lý thuê nhà chi tiết trên video dài của kênh.",
        "close": "Hãy đọc kỹ từng dòng chữ trước khi đặt bút ký hợp đồng.",
        "beats": [
            {
                "id": "S01",
                "narration": "Ký vào bản hợp đồng thuê nhà, bạn tin mình đã đọc rất kỹ.",
                "prompt": "Vertical 9:16 macro forensic tabletop photograph of a fountain pen nib hovering over the signature line of a thick printed rental agreement on a dark oak desk, warm 3000K desk lamp illumination, tactile paper fibers visible, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth 35mm macro push-in toward the fountain pen nib hovering steadily over the contract signature line, golden desk lamp gleam on polished wood, locked geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Nhưng những cái bẫy tinh vi thường giấu kín ở dòng chữ bé tí cuối trang.",
                "prompt": "Vertical 9:16 macro top-down view of a heavy brass magnifying glass resting on the fine-print paragraph at the bottom of the legal parchment, sharp optical glass distortion, strictly zero text, no cartoons.",
                "motion_prompt": "Slow optical rack focus shifting from the brass rim of the magnifying glass to the crisp paper weave underneath, steady warm lamplight, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Điều khoản đầu tiên là phí hao mòn tự nhiên bị biến thành lỗi người thuê.",
                "prompt": "Vertical 9:16 interior shot of an apartment wall showing a faint hairline paint scuff beside a wooden door frame, natural window light casting soft shadows, realistic architectural details, strictly zero text, no cartoons.",
                "motion_prompt": "Slow lateral tracking pass along the apartment wall highlighting the faint plaster scuff, realistic daylight texture, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S04",
                "narration": "Từng vết xước nhỏ trên tường hay bản lề cửa đều bị trừ thẳng vào cọc.",
                "prompt": "Vertical 9:16 macro shot of a brass door hinge with slight metallic patina and screwdriver mark, directional side light, tactile architectural macro, strictly zero text, no cartoons.",
                "motion_prompt": "Slow macro push-in toward the brass hinge, showing metallic texture and subtle wear marks under warm raking light, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S03",
            },
            {
                "id": "S05",
                "narration": "Cái bẫy thứ hai là quy định báo trước ba mươi ngày bằng văn bản giấy.",
                "prompt": "Vertical 9:16 tabletop shot of a modern smartphone resting beside a formal printed paper notice on dark oak, phone screen glowing softly next to paper fibers, strictly zero text, no cartoons.",
                "motion_prompt": "Slow lateral tracking from glowing smartphone to the formal paper notice, contrasting modern chat with rigid paper requirement, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S06",
                "narration": "Một tin nhắn báo dọn nhà qua mạng sẽ lập tức bị coi là phạm luật.",
                "prompt": "Vertical 9:16 close-up of a human hand holding a smartphone in an empty apartment room, bare wooden floor catching afternoon sunlight, solitary mood, strictly zero text, no cartoons.",
                "motion_prompt": "Slow camera orbit around the hand holding the smartphone in the empty sunlit room, gentle shadows stretching across floorboards, zero morphing.",
                "camera_motion": "orbit_cw",
                "transition": "dissolve",
                "based_on": "S05",
            },
            {
                "id": "S07",
                "narration": "Bạn mất trắng hai tháng tiền cọc mồ hôi nước mắt mà không thể khiếu nại.",
                "prompt": "Vertical 9:16 shot of an empty open leather wallet resting on an apartment windowsill beside a brass door key, afternoon light fading into dusk, strictly zero text, no cartoons.",
                "motion_prompt": "Slow dolly pullback from the empty wallet and solitary key on the windowsill, warm dusk light slowly dimming, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S08",
                "narration": "Người thuê nhà thường e ngại đàm phán vì nghĩ hợp đồng mẫu là bất biến.",
                "prompt": "Vertical 9:16 two-shot across a wooden conference table showing two silhouetted figures seated opposite each other with contract documents between them, professional setting, strictly zero text, no cartoons.",
                "motion_prompt": "Slow steady push-in down the center of the wooden table toward the documents between the two figures, warm ambient office light, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Luật pháp sinh ra để bảo vệ người hiểu rõ từng chữ ký của mình.",
                "prompt": "Vertical 9:16 macro tabletop composition of a classic wooden judge gavel resting horizontally beside bound leather law books on mahogany, rich tactile wood grain, strictly zero text, no cartoons.",
                "motion_prompt": "Slow cinematic lateral slide past the polished wooden gavel toward the leather-bound book spines, dignified warm lighting, zero morphing.",
                "camera_motion": "pan_left",
                "transition": "smoothleft",
                "based_on": None,
            },
            {
                "id": "S10",
                "narration": "Chỉ cần dùng bút gạch bỏ điều vô lý và yêu cầu hai bên cùng ký nháy.",
                "prompt": "Vertical 9:16 close-up of a hand using a red ink pen to firmly draw a neat horizontal line across an unreasonable clause on a contract page, crisp paper, strictly zero text, no cartoons.",
                "motion_prompt": "Slow precision push-in following the red pen stroke crossing the printed clause with decisive firmness, steady lamplight, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S11",
                "narration": "Bạn sẽ nắm chắc chiếc khiên pháp lý để bảo vệ tài sản của bản thân.",
                "prompt": "Vertical 9:16 shot of a confident tenant hand firmly holding apartment keys attached to a clean leather keychain, standing in front of a bright modern apartment doorway, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle dolly pullback as hand grips apartment keys with calm confidence in warm daylight doorway, pristine realism, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Xem cẩm nang pháp lý thuê nhà chi tiết trên video dài của kênh.",
                "prompt": "Vertical 9:16 macro shot of a tablet display showing legal checklist blueprints resting on a wooden desk beside a neat stack of signed contracts, warm desk lamp, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the tablet display and organized contract stack on the desk, warm evening study ambiance, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy đọc kỹ từng dòng chữ trước khi đặt bút ký hợp đồng.",
                "prompt": "Vertical 9:16 serene closing shot of a fountain pen resting securely in its velvet-lined case on a mahogany desk beside warm morning sunbeams, peace of mind mood, strictly zero text, no cartoons.",
                "motion_prompt": "Slow elegant pullback from the fountain pen resting in its case, morning sunlight sweeping across desk surface, dignified calm, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 3. la-ban-hoc-thuat
    # -------------------------------------------------------------------------
    {
        "slug": "la-ban-hoc-thuat",
        "youtube_title": "Bí Quyết Tự Học Sâu Nhớ Lâu Gấp Mười Lần",
        "thumbnail_text": "TỰ HỌC SÂU",
        "visual_hook": "Vertical 9:16 kinematic cognitive laboratory shot of a researcher demonstrating learning mechanisms with acrylic blocks under cool 5600K laboratory light, zero overlays, 25% margin",
        "bridge": "Lộ trình rèn luyện tư duy tự học đang chờ bạn trên video dài.",
        "close": "Hãy thử giải thích một điều vừa học cho người bên cạnh nghe.",
        "beats": [
            {
                "id": "S01",
                "narration": "Bạn đọc đi đọc lại một trang sách nhưng đầu óc vẫn trống rỗng.",
                "prompt": "Vertical 9:16 cinematic laboratory shot of an open hardcover scientific textbook on a clean white desk, pages illuminated by a sleek adjustable desk lamp, student hand resting pensively beside it, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the open textbook under focused task light, subtle page texture, locked physical geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Não bạn chỉ quen mặt chữ chứ không hề ghi nhớ bản chất vấn đề.",
                "prompt": "Vertical 9:16 macro top-down shot of a blank white notepad with a wooden pencil resting in the center, cool 5600K laboratory lighting, high negative space, strictly zero text, no cartoons.",
                "motion_prompt": "Slow optical rack focus from the sharp graphite tip of the pencil to the clean paper grain, pristine minimalist aesthetic, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Phương pháp Feynman chỉ ra con đường tiếp thu tri thức hoàn toàn khác.",
                "prompt": "Vertical 9:16 shot of an intuitive physical demonstration: three clear acrylic geometric blocks arranged in balance on a frosted glass laboratory tabletop, clean modern science aesthetic, strictly zero text, no cartoons.",
                "motion_prompt": "Smooth lateral tracking pass around the acrylic blocks catching directional studio highlights, crisp reflections, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S04",
                "narration": "Hãy lấy một tờ giấy trắng và giải thích khái niệm đó thật đơn giản.",
                "prompt": "Vertical 9:16 close-up of a hand drawing a simple minimalist circular diagram with a graphite pencil on thick art paper, natural daylight, strictly zero text, no cartoons.",
                "motion_prompt": "Precision push-in following the pencil tip smoothly drawing a continuous clean circle on the white page, tactile paper sound mood, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S03",
            },
            {
                "id": "S05",
                "narration": "Không dùng thuật ngữ phức tạp, chỉ dùng những câu chuyện đời thường.",
                "prompt": "Vertical 9:16 macro shot of simple everyday metaphors: a small wooden balance scale holding a polished river stone and a brass weight, neutral grey background, strictly zero text, no cartoons.",
                "motion_prompt": "Slow tilt down from the balancing arm to the stone settling into equilibrium, realistic weight physics, zero morphing.",
                "camera_motion": "pan_down",
                "transition": "smoothdown",
                "based_on": None,
            },
            {
                "id": "S06",
                "narration": "Ngay khi bạn bị vấp ở một câu hỏi ngây thơ, đó chính là lỗ hổng.",
                "prompt": "Vertical 9:16 shot of the circular pencil diagram on paper with a subtle gap left open in its contour, graphite pencil pointing directly at the gap, strictly zero text, no cartoons.",
                "motion_prompt": "Slow push-in toward the open gap in the circle, sharp optical focus on the paper texture, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": "S04",
            },
            {
                "id": "S07",
                "narration": "Đóng sách lại, quay về nguồn gốc ban đầu để lấp kín khoảng trống đó.",
                "prompt": "Vertical 9:16 shot of hands gently closing a thick academic tome with quiet determination, neat laboratory desk, morning sunlight streaming across surface, strictly zero text, no cartoons.",
                "motion_prompt": "Slow deliberate pullback as hands close the book cover, soft sunlight dust motes dancing in morning beam, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S08",
                "narration": "Bộ não con người chỉ thực sự nhớ khi nó tự kết nối các mảnh ghép.",
                "prompt": "Vertical 9:16 shot of two precision wooden interlocking puzzle pieces sliding smoothly into one solid joint on a white workbench, strictly zero text, no cartoons.",
                "motion_prompt": "Smooth macro push-in as two wooden pieces slide together and lock seamlessly, crisp joinery physics, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Biến kiến thức vay mượn thành trực giác tự nhiên của chính bản thân.",
                "prompt": "Vertical 9:16 eye-level shot of a student standing confidently in front of a clean white glassboard with simple geometric sketches, holding a marker at side with smile, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle dolly pullback from the student, bright natural daylight illuminating the uncluttered study room, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S08",
            },
            {
                "id": "S10",
                "narration": "Học ít đi nhưng hiểu sâu đến tận cùng gốc rễ vấn đề.",
                "prompt": "Vertical 9:16 macro shot of a single green sprout emerging through clean dark potting soil in a white ceramic dish, bright laboratory daylight, strictly zero text, no cartoons.",
                "motion_prompt": "Slow low-angle tilt up along the delicate stem of the sprout, rich soil texture, vivid green leaves catching light, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": None,
            },
            {
                "id": "S11",
                "narration": "Tri thức thực sự là thứ còn đọng lại sau khi bạn đã quên hết công thức.",
                "prompt": "Vertical 9:16 wide shot of an organized minimalist study space at dusk, warm lamp glowing beside a tidy stack of notebooks, peace and mastery atmosphere, strictly zero text, no cartoons.",
                "motion_prompt": "Slow cinematic lateral tracking pass across the tranquil study space, warm amber light spilling across wooden floorboards, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Lộ trình rèn luyện tư duy tự học đang chờ bạn trên video dài.",
                "prompt": "Vertical 9:16 macro tabletop view of a tablet displaying a cognitive roadmap blueprint beside a neat ceramic mug, soft studio light, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the tablet screen resting on clean wooden desk, pristine modern aesthetic, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy thử giải thích một điều vừa học cho người bên cạnh nghe.",
                "prompt": "Vertical 9:16 warm shot of two friends seated with tea cups engaged in an animated meaningful discussion beside a bright window, gentle smiles, strictly zero text, no cartoons.",
                "motion_prompt": "Slow graceful pullback from the two friends conversing in warm sunlight, calm intellectual camaraderie, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 4. luat-ngam
    # -------------------------------------------------------------------------
    {
        "slug": "luat-ngam",
        "youtube_title": "Quy Luật Ngầm Điều Khiển Hành Vi Của Đám Đông",
        "thumbnail_text": "QUY LUẬT NGẦM",
        "visual_hook": "Vertical 9:16 3D investigative diorama of an architectural metro concourse with illuminated crowd path vectors under high-angle surveillance lighting, zero overlays, 25% margin",
        "bridge": "Xem bản bóc tách mười quy luật tâm lý ngầm trên video dài của kênh.",
        "close": "Hãy giữ sự tỉnh táo trước mọi lựa chọn của đám đông.",
        "beats": [
            {
                "id": "S01",
                "narration": "Bước vào một quán ăn đông đúc, bạn nghĩ mình tự chọn bàn ngồi.",
                "prompt": "Vertical 9:16 high-angle architectural surveillance diorama of a bustling urban café interior, warm directional spotlights highlighting customer movement across slate floors, sleek Fern TV investigative aesthetic, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth 35mm overhead crane push-in toward the central dining area, customers moving in natural fluid paths under warm spotlights, locked geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Nhưng mọi bước chân đã được sắp đặt từ trước qua kiến trúc không gian.",
                "prompt": "Vertical 9:16 isometric cutaway model of the café layout showing illuminated pathways in soft amber light guiding movement from entrance to counter, architectural diorama, strictly zero text, no cartoons.",
                "motion_prompt": "Slow camera orbit around the isometric cutaway model, revealing subtle geometric floor partitions and directional lighting, zero morphing.",
                "camera_motion": "orbit_cw",
                "transition": "dissolve",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Con người có xu hướng vô thức đi theo lối mòn nơi có nhiều bóng người.",
                "prompt": "Vertical 9:16 eye-level shot of polished commercial marble floor reflecting soft footsteps of pedestrians moving along a curved glass corridor, strictly zero text, no cartoons.",
                "motion_prompt": "Low-angle lateral tracking pass alongside moving footwear on polished marble, crisp specular reflections, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S04",
                "narration": "Hiệu ứng bằng chứng xã hội khiến não bộ tắt cơ chế phản biện.",
                "prompt": "Vertical 9:16 high-angle shot of a crowd standing on a city plaza, several individuals looking toward a central architectural sculpture, overcast daylight, strictly zero text, no cartoons.",
                "motion_prompt": "Slow vertical pedestal rise capturing the collective gaze of the crowd on the plaza, locked architectural perspective, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": None,
            },
            {
                "id": "S05",
                "narration": "Khi thấy mọi người cùng nhìn lên trời, bạn cũng sẽ ngước mắt nhìn theo.",
                "prompt": "Vertical 9:16 low-angle upward shot from ground level showing silhouetted figures looking up toward an open atrium glass dome, soft diffused daylight, strictly zero text, no cartoons.",
                "motion_prompt": "Smooth upward tilt toward the glass dome ceiling, following the synchronized angle of looking up, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": "S04",
            },
            {
                "id": "S06",
                "narration": "Các nhà thiết kế thương mại tận dụng quy luật này để dẫn dắt hành vi.",
                "prompt": "Vertical 9:16 macro architectural blueprint model of a retail showroom with curved partitions and warm downlights, brass compass resting on blueprint paper, strictly zero text, no cartoons.",
                "motion_prompt": "Slow macro push-in across the curved miniature partitions on the blueprint, warm directional spotlight, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S07",
                "narration": "Đặt những món sinh lời cao nhất ngang tầm mắt và giữa dòng người qua lại.",
                "prompt": "Vertical 9:16 eye-level shot along a sleek retail display shelf, premium items spot-lit at golden ratio eye-height, soft background bokeh of shoppers, strictly zero text, no cartoons.",
                "motion_prompt": "Steady eye-level tracking pass along the illuminated display shelf, glistening surfaces under spotlight, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": "S06",
            },
            {
                "id": "S08",
                "narration": "Đám đông tưởng mình tự do nhưng thực chất đang đi theo kịch bản định sẵn.",
                "prompt": "Vertical 9:16 high-angle survey of a modern transit terminal with streaming crowds moving through parallel turnstiles, symmetrical architectural geometry, strictly zero text, no cartoons.",
                "motion_prompt": "Slow high-angle zoom out revealing the massive geometric flow of the terminal concourse, steady mechanical order, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Nhận ra lực đẩy vô hình giúp bạn lấy lại quyền kiểm soát tâm trí.",
                "prompt": "Vertical 9:16 ground-level shot of a single individual pausing still in the middle of a moving pedestrian concourse, calm deliberate posture, strictly zero text, no cartoons.",
                "motion_prompt": "Slow optical rack focus highlighting the still person as the crowd gently streams past on both sides, quiet defiance mood, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S08",
            },
            {
                "id": "S10",
                "narration": "Dừng lại một giây trước khi hùa theo dòng người đang vội vã.",
                "prompt": "Vertical 9:16 close-up of a person taking a quiet step aside onto an open quiet granite landing, overlooking the busy city below, fresh morning breeze, strictly zero text, no cartoons.",
                "motion_prompt": "Slow lateral pan from the moving crowd onto the tranquil granite terrace, soft natural morning sunlight, zero morphing.",
                "camera_motion": "pan_left",
                "transition": "smoothleft",
                "based_on": "S09",
            },
            {
                "id": "S11",
                "narration": "Bản lĩnh cá nhân bắt đầu từ lúc bạn dám bước chậm lại để quan sát.",
                "prompt": "Vertical 9:16 wide composition of an observant person standing quietly beside a grand glass window in an architectural library, looking out at urban horizon, strictly zero text, no cartoons.",
                "motion_prompt": "Slow graceful pullback revealing the vast quiet library interior around the thoughtful observer, serene intellectual clarity, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Xem bản bóc tách mười quy luật tâm lý ngầm trên video dài của kênh.",
                "prompt": "Vertical 9:16 tabletop shot of a tablet displaying architectural behavior diagrams resting beside a pair of eyeglasses on dark slate, warm desk light, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the tablet display and eyeglasses on slate counter, warm ambient study lighting, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy giữ sự tỉnh táo trước mọi lựa chọn của đám đông.",
                "prompt": "Vertical 9:16 contemplative shot of an open balcony looking toward sunrise over the city skyline, single coffee mug resting on railing, calm sovereignty, strictly zero text, no cartoons.",
                "motion_prompt": "Slow cinematic pullback from the coffee mug toward the vast open dawn sky, golden sunlight filling the frame, peaceful resolution, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 5. ua-sao-vay
    # -------------------------------------------------------------------------
    {
        "slug": "ua-sao-vay",
        "youtube_title": "Tại Sao Mắt Bạn Tự Động Nhắm Khi Giật Mình?",
        "thumbnail_text": "PHẢN XẠ CHỚP MẮT",
        "visual_hook": "Vertical 9:16 3D macro cross-section anatomy of the human eye and optic nerve pathway reacting to an approaching object under studio lighting, zero overlays, 25% margin",
        "bridge": "Khám phá trọn bộ phản xạ sinh tồn kỳ lạ trên video dài của kênh.",
        "close": "Hãy quan sát những điều kỳ diệu ngay trong chính cơ thể bạn.",
        "beats": [
            {
                "id": "S01",
                "narration": "Một vật thể lao tới trước mặt, mi mắt bạn lập tức sập xuống.",
                "prompt": "Vertical 9:16 high-speed macro photograph of an eye in ultra-slow motion beginning to close in response to a sudden gust of air, individual eyelashes sharp and clear, 3D Zack D Films anatomical clarity, strictly zero text, no cartoons.",
                "motion_prompt": "Slow-motion macro push-in toward the eye as the upper eyelid begins its rapid downward reflex, pristine ocular specular highlight, locked anatomy, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Toàn bộ diễn ra trong một phần mười giây, nhanh hơn cả suy nghĩ.",
                "prompt": "Vertical 9:16 3D biological cross-section showing the eyelid fully shielding the cornea, glistening tear film layer under clean studio side-lighting, strictly zero text, no cartoons.",
                "motion_prompt": "Precision lateral tracking pass across the closed eyelid curve, showing soft skin texture and lash barrier, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Đây là phản xạ chớp mắt sinh tồn nguyên thủy bảo vệ giác mạc quý giá.",
                "prompt": "Vertical 9:16 3D cutaway visualization of the human cornea and crystalline lens glowing with natural bioluminescent clarity, dark velvet background, strictly zero text, no cartoons.",
                "motion_prompt": "Slow camera orbit around the transparent corneal dome, light refracting gently through optical layers, zero morphing.",
                "camera_motion": "orbit_cw",
                "transition": "dissolve",
                "based_on": None,
            },
            {
                "id": "S04",
                "narration": "Tín hiệu ánh sáng không đi qua vỏ não mà truyền thẳng tới thân não.",
                "prompt": "Vertical 9:16 3D neuro-anatomical illustration showing a glowing pulse of electrical signal traveling directly along the short reflex arc to the brainstem, strictly zero text, no cartoons.",
                "motion_prompt": "Rapid smooth tracking move following the luminescent electrical impulse along the nerve pathway, clean dark-field microscopy aesthetic, zero morphing.",
                "camera_motion": "pan_down",
                "transition": "smoothdown",
                "based_on": "S03",
            },
            {
                "id": "S05",
                "narration": "Thần kinh vận nhãn kích hoạt cơ vòng mi co lại với tốc độ tối đa.",
                "prompt": "Vertical 9:16 detailed 3D model of the orbicularis oculi muscle fibers encircling the eye socket contracting smoothly, warm anatomical color palette, strictly zero text, no cartoons.",
                "motion_prompt": "Macro push-in on the circular muscle fibers contracting inward with realistic biological elasticity, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S06",
                "narration": "Một tấm khiên sinh học tự nhiên đóng lại ngăn mọi hạt bụi nguy hiểm.",
                "prompt": "Vertical 9:16 high-speed macro shot of tiny airborne water droplets bouncing harmlessly off the smooth outer surface of closed eyelids, studio backlighting, strictly zero text, no cartoons.",
                "motion_prompt": "Ultra slow-motion capture of micro droplets deflecting away from the eyelid skin, glistening liquid physics, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S05",
            },
            {
                "id": "S07",
                "narration": "Dù bạn có cố gắng mở to mắt đến đâu, bản năng cũng sẽ thắng lý trí.",
                "prompt": "Vertical 9:16 eye-level portrait of a person attempting to hold gaze steady while a gentle puff of air approaches, eye naturally blinking shut, authentic human expression, strictly zero text, no cartoons.",
                "motion_prompt": "Slow steady push-in on the person face capturing the involuntary micro-expression as the reflex takes over, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S08",
                "narration": "Cơ thể chúng ta được lập trình với hàng trăm cơ chế tự vệ kỳ diệu.",
                "prompt": "Vertical 9:16 full-body transparent 3D anatomical silhouette showing glowing neural reflex centers in the spine and brainstem, deep slate background, strictly zero text, no cartoons.",
                "motion_prompt": "Slow vertical tilt down along the glowing spinal column reflex pathways, soft amber luminescence, zero morphing.",
                "camera_motion": "pan_down",
                "transition": "smoothdown",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Mỗi phản xạ tự động đều là kết quả của hàng triệu năm tiến hóa.",
                "prompt": "Vertical 9:16 artistic macro composition of a fossilized ammonite shell resting beside a modern microscope objective on clean glass, warm side lighting, strictly zero text, no cartoons.",
                "motion_prompt": "Slow lateral slide from the ancient spiral shell to the precision optical lens, timeless evolutionary mood, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S10",
                "narration": "Giữ cho chúng ta bình an giữa vô vàn biến động của thế giới xung quanh.",
                "prompt": "Vertical 9:16 serene portrait of a person taking a deep breath in a lush sunlit park, eyes gently opening to morning light, natural documentary realism, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle dolly pullback as the person opens eyes with peaceful awareness, golden sun flare through green leaves, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S11",
                "narration": "Lắng nghe cơ thể là bước đầu tiên để hiểu sự tinh xảo của tự nhiên.",
                "prompt": "Vertical 9:16 macro shot of a hand resting gently against sunlight on a wooden porch railing, skin catching golden rim light, organic peaceful texture, strictly zero text, no cartoons.",
                "motion_prompt": "Slow push-in toward the hand in golden sunlight, soft warmth and tactile human presence, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S10",
            },
            {
                "id": "S12",
                "narration": "Khám phá trọn bộ phản xạ sinh tồn kỳ lạ trên video dài của kênh.",
                "prompt": "Vertical 9:16 macro tabletop shot of an anatomical sketchbook and medical model resting beside a tablet screen on an oak desk, warm study lamp, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the tablet screen and sketchbook on the wooden desk, warm evening ambiance, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy quan sát những điều kỳ diệu ngay trong chính cơ thể bạn.",
                "prompt": "Vertical 9:16 close-up of a human eye opening fully in clear morning daylight, pupil dilating naturally with crystal clarity and deep brown iris patterns, strictly zero text, no cartoons.",
                "motion_prompt": "Slow graceful pullback from the crystal clear iris revealing the calm reflective face in soft morning window light, serene ending, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 6. dia-com
    # -------------------------------------------------------------------------
    {
        "slug": "dia-com",
        "youtube_title": "Bí Mật Khoa Học Của Mùi Thơm Thịt Nướng Cháy Cạnh",
        "thumbnail_text": "PHẢN ỨNG MAILLARD",
        "visual_hook": "Vertical 9:16 macro molecular culinary shot of a prime beef steak searing in a heavy cast iron skillet with golden caramelized crust under chef studio lighting, zero overlays, 25% margin",
        "bridge": "Xem bí quyết áp chảo chuẩn nhà hàng năm sao trên video dài của kênh.",
        "close": "Hãy thử áp dụng nguyên lý nhiệt độ cho bữa tối hôm nay.",
        "beats": [
            {
                "id": "S01",
                "narration": "Đặt miếng thịt lên chảo nóng, tiếng xèo xèo và mùi thơm bốc lên.",
                "prompt": "Vertical 9:16 macro culinary photograph of a thick seasoned steak being placed into a smoking hot seasoned cast iron skillet, golden oil shimmering, America's Test Kitchen commercial aesthetic, 8k culinary still, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth 35mm macro dolly push-in toward the steak hitting the hot skillet, gentle steam rising with realistic fluid dynamics under directional tungsten lighting, locked geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Thứ đánh thức khứu giác của bạn là một phản ứng hóa học kỳ diệu.",
                "prompt": "Vertical 9:16 macro shot of aromatic steam plumes swirling gracefully upward from the skillet surface into a soft dark background, warm golden backlighting, strictly zero text, no cartoons.",
                "motion_prompt": "Slow-motion capture of steam swirls rising and diffusing into warm studio air, pristine liquid and gas physics, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Ở ngưỡng một trăm bốn mươi độ C, phản ứng May-át bắt đầu bùng nổ.",
                "prompt": "Vertical 9:16 macro extreme close-up of the steak underside forming a rich golden-brown caramelized crust against hot black cast iron, bubbling juices, strictly zero text, no cartoons.",
                "motion_prompt": "Slow optical rack focus across the bubbling meat juices to the crisp seared crust forming on the hot iron, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": "S01",
            },
            {
                "id": "S04",
                "narration": "Các phân tử axit amin và đường khử va chạm mãnh liệt dưới nhiệt cao.",
                "prompt": "Vertical 9:16 stylized 3D molecular visualization of amino acid and sugar molecules interacting and bonding under thermal heat waves, warm amber glow, strictly zero text, no cartoons.",
                "motion_prompt": "Smooth 3D orbit around the bonding molecular structures glowing with warm thermal energy, clean scientific culinary aesthetic, zero morphing.",
                "camera_motion": "orbit_cw",
                "transition": "dissolve",
                "based_on": None,
            },
            {
                "id": "S05",
                "narration": "Chúng tái cấu trúc thành hàng trăm hợp chất hương thơm mới chưa từng có.",
                "prompt": "Vertical 9:16 macro top-down view of the steak being basted with melted foaming butter, fresh thyme sprig, and crushed garlic clove, golden bubbles dancing, strictly zero text, no cartoons.",
                "motion_prompt": "Slow downward push-in as a chef spoon ladles foaming golden butter over the herb-topped steak, rich culinary textures, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S06",
                "narration": "Tạo nên lớp vỏ nâu giòn rụm và vị ngọt đậm đà đặc trưng của món ăn.",
                "prompt": "Vertical 9:16 cross-section macro shot of the sliced steak on a wooden cutting board, perfectly crisp dark brown crust contrasting with tender pink juicy interior, strictly zero text, no cartoons.",
                "motion_prompt": "Slow lateral slide across the resting sliced meat, glistening meat juices and razor-sharp seared crust texture, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": "S05",
            },
            {
                "id": "S07",
                "narration": "Nếu chảo quá nguội, nước bên trong sẽ thoát ra làm thịt bị luộc chín.",
                "prompt": "Vertical 9:16 macro comparison shot of a grey, unseared meat cut sitting in pooling cloudy liquid in a dull pan, flat cool lighting, culinary mistake demonstration, strictly zero text, no cartoons.",
                "motion_prompt": "Slow push-in highlighting the wet soggy surface and lack of crust in an underheated pan, clear educational contrast, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S08",
                "narration": "Nếu nhiệt độ vượt quá hai trăm độ, thức ăn sẽ bị cháy đen và đắng ngắt.",
                "prompt": "Vertical 9:16 macro shot of an over-torched charred pan surface with black acrid carbon residue and thin acrid smoke, stark harsh lighting, strictly zero text, no cartoons.",
                "motion_prompt": "Slow tilt down across the charred edge, highlighting the destructive effect of excess heat, zero morphing.",
                "camera_motion": "pan_down",
                "transition": "smoothdown",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Nấu nướng đỉnh cao thực chất là bài toán kiểm soát nhiệt độ chính xác.",
                "prompt": "Vertical 9:16 eye-level shot of a professional chef hand holding an infrared laser thermometer aimed at a seasoned skillet on a gas range, blue flame halo, strictly zero text, no cartoons.",
                "motion_prompt": "Slow deliberate tracking move alongside the chef steady hand, blue gas flames softly licking the underside of the pan, zero morphing.",
                "camera_motion": "pan_left",
                "transition": "smoothleft",
                "based_on": None,
            },
            {
                "id": "S10",
                "narration": "Làm chủ ngọn lửa là bạn đã nắm trong tay chìa khóa của hương vị.",
                "prompt": "Vertical 9:16 macro close-up of clean blue gas flame rings glowing steadily beneath a heavy iron grate, pristine kitchen equipment, strictly zero text, no cartoons.",
                "motion_prompt": "Slow push-in toward the concentric rings of steady blue flames, clean industrial culinary lighting, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": "S09",
            },
            {
                "id": "S11",
                "narration": "Mỗi bữa ăn ngon là sự hòa quyện hoàn hảo giữa khoa học và tình yêu ẩm thực.",
                "prompt": "Vertical 9:16 beautiful plated dish of sliced seared steak with roasted garlic and fresh rosemary on a warm ceramic plate, soft dining room candlelight, strictly zero text, no cartoons.",
                "motion_prompt": "Slow elegant pullback from the plated meal, warm romantic dining room ambiance, exquisite culinary presentation, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Xem bí quyết áp chảo chuẩn nhà hàng năm sao trên video dài của kênh.",
                "prompt": "Vertical 9:16 macro shot of a tablet displaying thermal culinary charts resting beside a chef knife and wooden pepper mill on a marble counter, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the tablet display and polished culinary tools, warm kitchen task lighting, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy thử áp dụng nguyên lý nhiệt độ cho bữa tối hôm nay.",
                "prompt": "Vertical 9:16 warm inviting shot of a home kitchen stove with a freshly seared meal resting in an iron skillet, warm evening sunlight streaming through window, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle pullback revealing the cozy sunlit kitchen counter, appetizing warmth, peaceful home cooking conclusion, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 7. vu-tru-ti-hon
    # -------------------------------------------------------------------------
    {
        "slug": "vu-tru-ti-hon",
        "youtube_title": "Điều Gì Xảy Ra Khi Rơi Vào Bên Trong Hố Đen?",
        "thumbnail_text": "RƠI VÀO HỐ ĐEN",
        "visual_hook": "Vertical 9:16 deep-space ray-marched IMAX shot of a supermassive black hole with glowing golden accretion disk bending starlight, zero overlays, 25% margin",
        "bridge": "Hành trình thám hiểm hố đen toàn cảnh đang chờ trên video dài của kênh.",
        "close": "Hãy ngước nhìn bầu trời đêm với lòng ngưỡng mộ vô tận.",
        "beats": [
            {
                "id": "S01",
                "narration": "Nếu bạn trôi dạt về phía hố đen, thời gian sẽ dần chậm lại.",
                "prompt": "Vertical 9:16 deep-space ray-marched IMAX photograph of a supermassive black hole floating in deep void, glowing golden-orange relativistic accretion disk warping background starlight, Melodysheep cosmic aesthetic, strictly zero text, no cartoons.",
                "motion_prompt": "Slow majestic camera push-in toward the swirling black hole shadow, gravitational lensing bending background constellations with mathematically locked geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Lực hấp dẫn khổng lồ bẻ cong cả không gian và tia sáng xung quanh.",
                "prompt": "Vertical 9:16 close view of the photon sphere ring of light looping twice around the jet-black event horizon, intense Doppler blue-shifting on the approaching side, strictly zero text, no cartoons.",
                "motion_prompt": "Slow camera orbit around the photon sphere, revealing the dramatic distortion of distant galaxies curved into concentric optical rings, zero morphing.",
                "camera_motion": "orbit_cw",
                "transition": "dissolve",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Tại chân trời sự kiện, ánh sáng cũng không còn đường thoát ra ngoài.",
                "prompt": "Vertical 9:16 macro perspective from just outside the pitch-black boundary of the event horizon, a thin razor-sharp ring of trapped light trembling, deep cosmos void, strictly zero text, no cartoons.",
                "motion_prompt": "Slow forward glide skimming the curved edge of absolute darkness, stellar light bending into an infinite crescent, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S02",
            },
            {
                "id": "S04",
                "narration": "Người quan sát từ xa sẽ thấy bạn đóng băng vĩnh viễn ở ranh giới vô tận.",
                "prompt": "Vertical 9:16 distant observational view from a research probe cockpit, seeing a tiny red-shifted silhouette hovering motionless at the edge of the black hole horizon, strictly zero text, no cartoons.",
                "motion_prompt": "Slow steady zoom out from the probe viewport, red-shifted light fading into extreme infrared darkness, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S05",
                "narration": "Nhưng dưới góc nhìn của bạn, bạn vẫn lao thẳng vào tâm điểm kỳ dị.",
                "prompt": "Vertical 9:16 first-person cockpit view plunging through the event horizon, the entire external universe compressing into a single glowing disc of light overhead, strictly zero text, no cartoons.",
                "motion_prompt": "Rapid forward dolly plunge into the dark interior, overhead sky disc shrinking and shifting toward intense violet light, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S06",
                "narration": "Hiệu ứng kéo dãn mì sợi sẽ kéo dài từng nguyên tử trên cơ thể.",
                "prompt": "Vertical 9:16 scientific visualization of extreme gravitational tidal gradient stretching radiant particles into long parallel filament lines directed toward a point, strictly zero text, no cartoons.",
                "motion_prompt": "Slow tilt down following glowing filament particles elongating along gravitational geodesics, pure particle physics realism, zero morphing.",
                "camera_motion": "pan_down",
                "transition": "smoothdown",
                "based_on": "S05",
            },
            {
                "id": "S07",
                "narration": "Mọi định luật vật lý quen thuộc đều sụp đổ hoàn toàn trước điểm kỳ dị.",
                "prompt": "Vertical 9:16 abstract geometric representation of spacetime manifold curving to infinite density at a single glowing point, mathematical curvature visualization, strictly zero text, no cartoons.",
                "motion_prompt": "Slow camera push-in toward the pinpoint singularity, grid lines warping into infinite curvature with locked geometry, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S08",
                "narration": "Không gian và thời gian đổi chỗ cho nhau, hướng về một kết cục tất yếu.",
                "prompt": "Vertical 9:16 breathtaking view inside the event horizon where future directions all converge inward toward the central singularity, cosmic surrealism, strictly zero text, no cartoons.",
                "motion_prompt": "Slow rotating pan across the inverted spacetime horizon, silent cosmic awe, zero morphing.",
                "camera_motion": "orbit_cw",
                "transition": "dissolve",
                "based_on": "S07",
            },
            {
                "id": "S09",
                "narration": "Hố đen không chỉ là cỗ máy hủy diệt mà còn là nơi lưu giữ thông tin vũ trụ.",
                "prompt": "Vertical 9:16 theoretical physics visualization of Hawking radiation quantum entangled particle pairs separating at the event horizon boundary, faint ethereal luminescence, strictly zero text, no cartoons.",
                "motion_prompt": "Slow lateral tracking pass along the boundary as quantum particles separate gracefully into deep space, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S10",
                "narration": "Nhắc nhở chúng ta về sự nhỏ bé của loài người trước thiên hà bao la.",
                "prompt": "Vertical 9:16 panoramic view of the Milky Way spiral galaxy seen from an immense cosmic distance, a tiny speck of light in the vast cosmic web, strictly zero text, no cartoons.",
                "motion_prompt": "Slow sweeping pull-back revealing the immense spiral galaxy swirling silently in deep space, humbling cosmic scale, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S11",
                "narration": "Chiêm ngưỡng vũ trụ sâu thẳm để thấy trân quý từng khoảnh khắc hiện tại.",
                "prompt": "Vertical 9:16 silhouette of a lone human standing on a quiet desert dune looking up at a crystal clear night sky ablaze with the Milky Way, cool starlight, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle dolly pullback from the solitary stargazer on the desert crest, millions of stars glistening silently overhead, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Hành trình thám hiểm hố đen toàn cảnh đang chờ trên video dài của kênh.",
                "prompt": "Vertical 9:16 macro tabletop shot of an astronomical telescope eyepiece and stellar chart resting beside a glowing tablet screen on an observatory desk, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the tablet screen displaying astrophysics simulation blueprints, warm observatory red night-light, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy ngước nhìn bầu trời đêm với lòng ngưỡng mộ vô tận.",
                "prompt": "Vertical 9:16 wide majestic shot of an astronomical observatory dome open to the starry night sky at twilight, serene blue hour glow on mountains, strictly zero text, no cartoons.",
                "motion_prompt": "Slow sweeping upward tilt toward the open observatory slit and the sparkling starfield beyond, peaceful cosmic transcendence, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 8. chanh-niem-ke
    # -------------------------------------------------------------------------
    {
        "slug": "chanh-niem-ke",
        "youtube_title": "Nghệ Thuật Buông Bỏ Những Lo Âu Vô Hình Trong Đầu",
        "thumbnail_text": "NGHỆ THUẬT BUÔNG BỎ",
        "visual_hook": "Vertical 9:16 35mm anamorphic Kyoto Zen sanctuary courtyard with raindrops falling onto a stone basin surrounded by moss, zero overlays, 25% margin",
        "bridge": "Trọn bộ phương pháp thiền định buông xả đang có trên video dài của kênh.",
        "close": "Hãy nhắm mắt thở sâu và buông bỏ gánh nặng ngay lúc này.",
        "beats": [
            {
                "id": "S01",
                "narration": "Chúng ta thường kiệt sức vì những lo toan chưa từng xảy ra.",
                "prompt": "Vertical 9:16 35mm anamorphic photograph of a quiet wooden veranda of a traditional Kyoto Zen temple overlooking a moss garden in gentle rain, raindrops rippling in a smooth stone water basin, Aperture meditative aesthetic, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth 35mm dolly push-in toward the mossy stone basin as raindrops fall with realistic fluid physics, tranquil overcast light, locked geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Tâm trí mải miết chạy đua với hàng ngàn kịch bản tồi tệ tưởng tượng.",
                "prompt": "Vertical 9:16 macro shot of fallen autumn leaves swirling gently in an eddy of clear mountain stream water over smooth dark river pebbles, strictly zero text, no cartoons.",
                "motion_prompt": "Slow-motion tracking pass following a golden leaf swirling calmly in the water eddy, realistic water refraction, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Càng cố xua đuổi sự sợ hãi, bạn lại càng tiếp thêm năng lượng cho nó.",
                "prompt": "Vertical 9:16 interior shot of a minimalist tatami room with a soft paper shoji screen casting diffused morning light onto a solitary meditation cushion, strictly zero text, no cartoons.",
                "motion_prompt": "Slow cinematic lateral tracking across the woven tatami mat toward the meditation cushion, serene soft lighting, zero morphing.",
                "camera_motion": "pan_left",
                "transition": "smoothleft",
                "based_on": None,
            },
            {
                "id": "S04",
                "narration": "Hãy ngồi lại trong yên lặng và quan sát dòng suy nghĩ như mây trôi.",
                "prompt": "Vertical 9:16 vertical composition showing soft white mist rolling slowly over deep green pine mountain ridges at dawn, wide negative space sky, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle tilt up following the morning mist rising gracefully above pine tree silhouettes, serene atmospheric depth, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": None,
            },
            {
                "id": "S05",
                "narration": "Đám mây có thể u ám, nhưng bầu trời phía sau vẫn luôn bao la tĩnh lặng.",
                "prompt": "Vertical 9:16 wide sky view showing a dark rain cloud drifting slowly away to reveal clear golden morning sunlight breaking through, strictly zero text, no cartoons.",
                "motion_prompt": "Slow time-lapse style tracking move as the cloud edge parts and golden light spills across the frame, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": "S04",
            },
            {
                "id": "S06",
                "narration": "Bạn không phải là suy nghĩ hỗn độn đó, bạn là không gian chứa đựng chúng.",
                "prompt": "Vertical 9:16 macro shot of a single water droplet resting in perfect equilibrium on a broad lotus leaf, reflecting the morning sky, strictly zero text, no cartoons.",
                "motion_prompt": "Slow macro push-in on the spherical water droplet trembling slightly without breaking, glistening surface tension, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S07",
                "narration": "Thả lỏng đôi vai, hít một hơi sâu và đón nhận hiện tại như nó vốn là.",
                "prompt": "Vertical 9:16 close-up of a person seated in peaceful posture, hands resting softly on knees, shoulders gently lowering with a relaxed breath, soft window daylight, strictly zero text, no cartoons.",
                "motion_prompt": "Slow subtle push-in capturing the gentle release of physical tension in the posture, peaceful natural realism, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S08",
                "narration": "Nỗi buồn hay niềm vui đến rồi cũng sẽ tự nhiên tan biến theo quy luật.",
                "prompt": "Vertical 9:16 shot of gentle water ripples expanding outward across a still garden pond and smoothing back into a flawless mirror, strictly zero text, no cartoons.",
                "motion_prompt": "Slow high-angle tracking pass as the ripples dissipate completely, returning the water surface to glass-like calm, zero morphing.",
                "camera_motion": "pan_down",
                "transition": "smoothdown",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Bình yên không nằm ở việc kiểm soát mọi thứ xung quanh.",
                "prompt": "Vertical 9:16 shot of a weathered stone lantern standing peacefully in a bamboo grove as wind gently sways the tall green stalks, strictly zero text, no cartoons.",
                "motion_prompt": "Slow lateral pan past the stone lantern as bamboo stalks sway gracefully in the mountain breeze, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S10",
                "narration": "Mà nằm ở sự vững vàng chấp nhận những điều không thể thay đổi.",
                "prompt": "Vertical 9:16 macro shot of a smooth river stone resting solid and unmoved in the center of a swirling mountain brook, clear flowing water, strictly zero text, no cartoons.",
                "motion_prompt": "Slow push-in toward the immovable river stone as clean water streams smoothly around its flanks, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S09",
            },
            {
                "id": "S11",
                "narration": "Một tâm trí an tĩnh là món quà quý giá nhất bạn có thể tự tặng mình.",
                "prompt": "Vertical 9:16 wide shot of an open wooden veranda looking out toward a calm Zen gravel garden raked in concentric circular ripples, morning warmth, strictly zero text, no cartoons.",
                "motion_prompt": "Slow graceful pullback along the veranda floorboards, peaceful harmony between architecture and nature, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Trọn bộ phương pháp thiền định buông xả đang có trên video dài của kênh.",
                "prompt": "Vertical 9:16 macro tabletop shot of a brass singing bowl with wooden mallet resting beside a warm glowing candle on a polished cedar table, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the brass singing bowl and candle flame, warm amber meditative reflections, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy nhắm mắt thở sâu và buông bỏ gánh nặng ngay lúc này.",
                "prompt": "Vertical 9:16 serene closing shot of a person sitting peacefully with eyes softly closed in warm morning sun, a gentle smile of relief on lips, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle pullback revealing the tranquil room bathed in soft morning sunbeams, profound inner peace conclusion, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 9. minh-triet-song
    # -------------------------------------------------------------------------
    {
        "slug": "minh-triet-song",
        "youtube_title": "Bài Học Khắc Kỷ: Giữ Tâm Bình Thản Trước Sóng Gió",
        "thumbnail_text": "BÀI HỌC KHẮC KỶ",
        "visual_hook": "Vertical 9:16 Caravaggio chiaroscuro marble bust of Marcus Aurelius illuminated by dramatic single golden-hour sidelight, zero overlays, 25% margin",
        "bridge": "Xem mười nguyên tắc khắc kỷ chuyển hóa nghịch cảnh trên video dài.",
        "close": "Hãy tập trung vào những điều bạn có thể làm tốt hôm nay.",
        "beats": [
            {
                "id": "S01",
                "narration": "Biến cố ập đến bất ngờ, điều làm bạn gục ngã là cách bạn nghĩ.",
                "prompt": "Vertical 9:16 Caravaggio chiaroscuro marble sculpture bust of a Roman stoic philosopher standing against a deep shadow background, dramatic single 3200K golden keylight carving facial contours, Daily Stoic contemplative aesthetic, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth 35mm push-in toward the stoic marble bust, raking golden light revealing fine sculpted marble texture with locked geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Không phải sự việc bên ngoài khiến ta khổ, mà là góc nhìn của chính ta.",
                "prompt": "Vertical 9:16 close-up of the marble statue calm, resolute carved eyes looking into the distance, deep shadow on one side, warm highlight on the other, strictly zero text, no cartoons.",
                "motion_prompt": "Slow camera orbit around the marble profile, light transition sweeping softly across the brow and cheekbone, zero morphing.",
                "camera_motion": "orbit_cw",
                "transition": "dissolve",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Triết gia Khắc kỷ chia thế giới làm hai nửa rất rõ ràng:",
                "prompt": "Vertical 9:16 tabletop shot of a classical brass armillary sphere and an antique hourglass resting on dark polished walnut table, dramatic chiaroscuro side lighting, strictly zero text, no cartoons.",
                "motion_prompt": "Slow lateral tracking pass between the brass rings and the glass hourglass containing falling sand, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S04",
                "narration": "Những thứ ta kiểm soát được và những thứ hoàn toàn ngoài tầm với.",
                "prompt": "Vertical 9:16 macro shot of golden sand granules trickling steadily through the narrow neck of an antique glass hourglass, sharp specular highlights, strictly zero text, no cartoons.",
                "motion_prompt": "Precision macro push-in on the steady trickle of sand grains falling with locked gravity physics, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": "S03",
            },
            {
                "id": "S05",
                "narration": "Thời tiết, thị trường hay lòng người là điều bạn không thể đổi thay.",
                "prompt": "Vertical 9:16 wide view of storm clouds gathering over an ancient stone coastline, dark ocean waves crashing against a massive granite sea cliff, strictly zero text, no cartoons.",
                "motion_prompt": "Slow majestic tilt up from the crashing sea foam to the immovable granite cliff facing the dark storm, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": None,
            },
            {
                "id": "S06",
                "narration": "Nhưng thái độ và hành động hiện tại luôn nằm trọn trong tay bạn.",
                "prompt": "Vertical 9:16 close-up of a human hand writing steady ink notes in a leather journal on an oak desk by candlelight, deliberate calm posture, strictly zero text, no cartoons.",
                "motion_prompt": "Slow push-in following the deliberate movement of the quill or pen, warm candle flame flickering steadily, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S07",
                "narration": "Khi dồn toàn bộ tâm sức vào vòng tròn kiểm soát của chính mình,",
                "prompt": "Vertical 9:16 top-down composition of a brass navigation compass resting in the exact center of a parchment circle drawn on stone, warm directional beam, strictly zero text, no cartoons.",
                "motion_prompt": "Slow downward push-in toward the compass needle settling firmly pointing North, steady light, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S08",
                "narration": "bạn sẽ không còn cảm giác bất lực hay oán trách hoàn cảnh.",
                "prompt": "Vertical 9:16 eye-level shot of a person standing calm and composed on a high stone terrace overlooking a windy mountain valley at sunrise, strictly zero text, no cartoons.",
                "motion_prompt": "Slow dolly pullback from the calm observer facing the vast sunrise valley, cool mountain wind in hair, serene posture, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Trở ngại trước mắt chính là bài kiểm tra tôi luyện lòng kiên định.",
                "prompt": "Vertical 9:16 macro shot of a blacksmith anvil with glowing red-hot iron bar being shaped by a heavy steel hammer under golden sparks, strictly zero text, no cartoons.",
                "motion_prompt": "Slow-motion capture of hammer striking the hot iron, sparks dancing in dark workshop, crisp metal physics, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S10",
                "narration": "Sóng gió càng lớn, ngọn hải đăng tâm trí càng tỏa sáng rực rỡ.",
                "prompt": "Vertical 9:16 majestic shot of a solitary stone lighthouse standing atop a rugged rock reef, glowing beacon beam sweeping through dark ocean mist, strictly zero text, no cartoons.",
                "motion_prompt": "Slow rotational sweep following the powerful lighthouse beam piercing through sea mist, rock reef standing immovable, zero morphing.",
                "camera_motion": "orbit_cw",
                "transition": "dissolve",
                "based_on": None,
            },
            {
                "id": "S11",
                "narration": "Giữ vững phẩm giá và sự điềm tĩnh trước mọi nghịch cảnh cuộc đời.",
                "prompt": "Vertical 9:16 Caravaggio style composition of an ancient stone archway framing a tranquil golden morning vista, warm light washing over classical stone pillars, strictly zero text, no cartoons.",
                "motion_prompt": "Slow graceful push-in through the stone archway toward the peaceful sunlit morning horizon, timeless dignity mood, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Xem mười nguyên tắc khắc kỷ chuyển hóa nghịch cảnh trên video dài.",
                "prompt": "Vertical 9:16 tabletop shot of a bound leather book titled with embossed classical patterns resting beside a brass magnifying glass on dark wood, warm desk lamp, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the leather volume and brass accessories, warm scholarly study ambiance, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy tập trung vào những điều bạn có thể làm tốt hôm nay.",
                "prompt": "Vertical 9:16 contemplative shot of a person looking thoughtfully through an open library window toward sunrise, warm golden sunbeams filling the room, strictly zero text, no cartoons.",
                "motion_prompt": "Slow elegant pullback from the thoughtful figure into the warm book-lined room, inspiring resolution conclusion, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 10. co-the-ke
    # -------------------------------------------------------------------------
    {
        "slug": "co-the-ke",
        "youtube_title": "Dạ Dày Cầu Cứu: Điều Gì Xảy Ra Khi Bạn Ăn Đêm?",
        "thumbnail_text": "DẠ DÀY CẦU CỨU",
        "visual_hook": "Vertical 9:16 8K 3D endoscopic biomedical visualization of the human stomach lining with gastric acid reactions under cool medical imaging lighting, zero overlays, 25% margin",
        "bridge": "Lộ trình phục hồi hệ tiêu hóa khoa học đang có trên video dài của kênh.",
        "close": "Hãy bảo vệ dạ dày bằng cách ăn tối sớm hơn mỗi ngày.",
        "beats": [
            {
                "id": "S01",
                "narration": "Lúc hai giờ sáng, một tô mì cay nóng hổi ập xuống dạ dày.",
                "prompt": "Vertical 9:16 8K 3D endoscopic biomedical visualization of the gastric lumen inside the human stomach, warm folds of mucosa glistening with protective mucus layer under clean clinical light, Nucleus Medical Media aesthetic, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth 35mm endoscopic push-in through the gastric cavity, natural physiological peristalsis movement with locked anatomical geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Trong khi các cơ quan nghỉ ngơi, dạ dày bất ngờ bị đánh thức khẩn cấp.",
                "prompt": "Vertical 9:16 3D medical visualization showing gastric rugae folds stretching to accommodate sudden spicy content, vivid warm endoscopic illumination, strictly zero text, no cartoons.",
                "motion_prompt": "Steady endoscopic tracking pass along the curving stomach wall, mucosal folds flexing under realistic biological elasticity, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Hàng triệu tuyến vị lập tức tiết axit Clo-hy-đric để tiêu hóa.",
                "prompt": "Vertical 9:16 macro microscopic cutaway of parietal cells in the gastric glands releasing microscopic droplets of hydrochloric acid into the cavity, strictly zero text, no cartoons.",
                "motion_prompt": "Precision macro push-in on the gland pores secreting clear droplets, pristine biomedical fluid dynamics, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S04",
                "narration": "Nồng độ axit đậm đặc tương đương dung dịch làm sạch kim loại.",
                "prompt": "Vertical 9:16 3D visualization of gastric acid solution bubbling gently against dense digestive enzymes, amber scientific glow, dark background, strictly zero text, no cartoons.",
                "motion_prompt": "Slow camera orbit around the bubbling digestive fluid, soft luminous highlights on acid droplets, zero morphing.",
                "camera_motion": "orbit_cw",
                "transition": "dissolve",
                "based_on": "S03",
            },
            {
                "id": "S05",
                "narration": "Lớp màng nhầy mỏng manh phải căng mình gánh từng đợt sóng nhiệt.",
                "prompt": "Vertical 9:16 high-magnification view of the protective mucosal epithelial barrier holding firm against glowing digestive enzymes, cellular integrity, strictly zero text, no cartoons.",
                "motion_prompt": "Slow lateral slide along the mucosal boundary, cellular wall holding firm with locked geometry, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S06",
                "narration": "Khi bạn nằm ngang đi ngủ, van tâm vị đóng không chặt gây trào ngược.",
                "prompt": "Vertical 9:16 anatomical cross-section showing the lower esophageal sphincter valve failing to seal tightly in horizontal posture, clear fluid rising slightly, strictly zero text, no cartoons.",
                "motion_prompt": "Slow tilt up from the stomach fundus toward the relaxed esophageal sphincter, realistic biological motion, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": None,
            },
            {
                "id": "S07",
                "narration": "Dịch vị trào lên thực quản gây cảm giác nóng rát cồn cào lồng ngực.",
                "prompt": "Vertical 9:16 3D endoscopic view inside the lower esophagus showing irritated pink squamous epithelium illuminated by warm clinical lighting, strictly zero text, no cartoons.",
                "motion_prompt": "Slow forward tracking through the esophageal lumen, realistic tissue elasticity under clinical inspection light, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S06",
            },
            {
                "id": "S08",
                "narration": "Những tổn thương vi thể lặp đi lặp lại bào mòn dần sức đề kháng.",
                "prompt": "Vertical 9:16 microscopic cellular grid of epithelial cells showing subtle stress markers under high-resolution fluorescent confocal microscopy, strictly zero text, no cartoons.",
                "motion_prompt": "Slow zoom in on the cellular grid structure, soft green and blue biomedical fluorophores, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Đổi lại vài phút thỏa mãn cơn thèm là cái giá quá đắt của sức khỏe.",
                "prompt": "Vertical 9:16 still life of a steaming midnight noodle bowl left half-eaten on a dark kitchen table beside a clock reading 2:15 AM, moody dim lighting, strictly zero text, no cartoons.",
                "motion_prompt": "Slow dolly pullback from the half-eaten bowl, dim kitchen shadows stretching across table, solitary mood, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S10",
                "narration": "Hãy cho cơ quan tiêu hóa một khoảng nghỉ ngơi xứng đáng mỗi đêm.",
                "prompt": "Vertical 9:16 3D visualization of the stomach cavity returning to a calm, restful state with balanced pH and soothing pale pink lining, serene lighting, strictly zero text, no cartoons.",
                "motion_prompt": "Slow graceful push-in through the peaceful rested gastric lumen, calm mucosal glow, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S11",
                "narration": "Cơ thể biết ơn sự chăm sóc từ những thói quen ăn uống lành mạnh.",
                "prompt": "Vertical 9:16 bright morning kitchen scene showing a person pouring fresh water from a glass pitcher into a clear cup, sunlight streaming across counter, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle dolly pullback as clear water fills the cup, bright morning warmth and vibrant health aesthetic, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Lộ trình phục hồi hệ tiêu hóa khoa học đang có trên video dài của kênh.",
                "prompt": "Vertical 9:16 macro tabletop shot of a nutritional biology book and medical digestive model resting on a clean desk beside a tablet screen, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the tablet display and organized wellness guide, warm daytime studio lighting, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy bảo vệ dạ dày bằng cách ăn tối sớm hơn mỗi ngày.",
                "prompt": "Vertical 9:16 serene closing shot of a person smiling peacefully while resting in a comfortable sunlit bedroom, calm restorative atmosphere, strictly zero text, no cartoons.",
                "motion_prompt": "Slow elegant pullback from the restful scene, golden daylight filling the bedroom with soothing serenity, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 11. su-ke-lai
    # -------------------------------------------------------------------------
    {
        "slug": "su-ke-lai",
        "youtube_title": "Kỳ Mưu Cọc Gỗ Sông Bạch Đằng Đánh Tan Giặc Nam Hán",
        "thumbnail_text": "BẠCH ĐẰNG 938",
        "visual_hook": "Vertical 9:16 3D historical battlefield diorama of Bach Dang river at low tide revealing sharpened iron-tipped wooden stakes with historical wooden war galleys, zero overlays, 25% margin",
        "bridge": "Xem phân tích sa bàn chiến thuật Bạch Đằng trên video dài của kênh.",
        "close": "Hãy tự hào về hào khí ngàn năm của tiền nhân dựng nước.",
        "beats": [
            {
                "id": "S01",
                "narration": "Đêm mùa đông năm chín ba tám, dòng sông Bạch Đằng cuộn sóng ngầm.",
                "prompt": "Vertical 9:16 3D historical battlefield diorama of the wide Bach Dang estuary at midnight, cold moonlight glinting off churning brackish river water, mist swirling over tidal reeds, Kings and Generals epic historical aesthetic, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth 35mm low-angle tracking pass along the misty river surface as cold moonlight reflects off rippling water, locked historical geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Dưới làn sương, hàng ngàn thân gỗ lim vót nhọn được cắm sâu xuống lòng sông.",
                "prompt": "Vertical 9:16 underwater and waterline cross-section showing massive ironwood stakes with sharpened iron tips being driven deep into the riverbed silt, torchlight flickering above, strictly zero text, no cartoons.",
                "motion_prompt": "Slow vertical tilt down from torchlit waterline to the massive sharpened stakes firmly embedded in river sediment, realistic silt displacement, zero morphing.",
                "camera_motion": "pan_down",
                "transition": "smoothdown",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Ngô Quyền đã tính toán quy luật con nước thủy triều chính xác từng khắc.",
                "prompt": "Vertical 9:16 eye-level shot of ancient Vietnamese military commanders studying an earthen terrain sand table illuminated by bronze oil lamps in a command tent, strictly zero text, no cartoons.",
                "motion_prompt": "Slow cinematic push-in across the detailed river sand table toward the commander determined gaze, flickering warm torchlight, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S04",
                "narration": "Sáng hôm sau, đoàn thuyền chiến Nam Hán ồ ạt tiến vào cửa sông lộng gió.",
                "prompt": "Vertical 9:16 panoramic aerial view of hundreds of heavy Chinese Southern Han wooden war galleys with red silk sails sailing arrogantly up the high-tide river mouth, morning mist, strictly zero text, no cartoons.",
                "motion_prompt": "High-angle sweeping tracking shot following the armada sailing upstream with full sails billowing in morning wind, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S05",
                "narration": "Những thuyền nhỏ của quân ta vờ rút lui nhử giặc vào bẫy ngầm.",
                "prompt": "Vertical 9:16 telephoto shot of agile Vietnamese light rowing boats feigning retreat through river channels, oars churning water rhythmically, strictly zero text, no cartoons.",
                "motion_prompt": "Dynamic lateral tracking shot alongside the agile rowing boats maneuvering swiftly through tidal reeds, zero morphing.",
                "camera_motion": "pan_left",
                "transition": "smoothleft",
                "based_on": "S04",
            },
            {
                "id": "S06",
                "narration": "Khi thủy triều rút nhanh, bãi cọc nhọn nhô lên khỏi mặt nước.",
                "prompt": "Vertical 9:16 ground-level waterline shot of the river water rapidly receding, sharp dark ironwood stake points piercing through the retreating surface froth, dramatic lighting, strictly zero text, no cartoons.",
                "motion_prompt": "Time-lapse style downward water movement revealing the endless field of jagged stakes rising from the riverbed, zero morphing.",
                "camera_motion": "pan_down",
                "transition": "smoothdown",
                "based_on": "S02",
            },
            {
                "id": "S07",
                "narration": "Đội hình thuyền giặc va vào hàng cọc gỗ, vỡ toác và mắc cạn giữa dòng.",
                "prompt": "Vertical 9:16 dynamic impact shot of a massive enemy war galley hull grinding to an abrupt halt atop submerged wooden stakes, heavy oak timbers splintering under vessel weight, water splashing, strictly zero text, no cartoons.",
                "motion_prompt": "Slow-motion dramatic push-in as the heavy wooden hull lodges firmly onto the stakes, realistic timber stress and water displacement, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S06",
            },
            {
                "id": "S08",
                "narration": "Quân ta từ các nhánh lau sậy đồng loạt phản công dưới tiếng trống trận.",
                "prompt": "Vertical 9:16 heroic wide shot of Vietnamese war craft bursting out from hidden reed tributaries, bronze drums beating rhythmically on command decks, banner flags waving, strictly zero text, no cartoons.",
                "motion_prompt": "Sweeping forward dolly tracking following the fleet advancing with unstoppable momentum into the open river, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Chỉ trong một ngày, toàn bộ âm mưu xâm lược của giặc tan tành.",
                "prompt": "Vertical 9:16 high-angle survey of the stranded armada abandoned on the muddy riverbed at low tide, smoke curling into overcast winter sky, victory mood, strictly zero text, no cartoons.",
                "motion_prompt": "Slow high-altitude crane pullback revealing the stranded fleet across the vast mudflats, majestic winter horizon, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S08",
            },
            {
                "id": "S10",
                "narration": "Trận đánh mở ra kỷ nguyên độc lập tự chủ lâu dài cho non sông.",
                "prompt": "Vertical 9:16 majestic panoramic view of Bach Dang river at sunset, calm golden water flowing peacefully past ancient green riverbanks, peaceful sovereign land, strictly zero text, no cartoons.",
                "motion_prompt": "Slow cinematic lateral tracking pass across the calm golden river surface, evening sunbeams touching sacred waters, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S11",
                "narration": "Trí tuệ quân sự đỉnh cao là biết dựa vào sức mạnh tự nhiên để chiến thắng.",
                "prompt": "Vertical 9:16 museum macro close-up of a preserved historical Bach Dang ironwood stake displayed on polished stone in a heritage hall, warm respectful lighting, strictly zero text, no cartoons.",
                "motion_prompt": "Slow push-in toward the thousand-year-old preserved wood grain and iron tip, solemn historical reverence, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Xem phân tích sa bàn chiến thuật Bạch Đằng trên video dài của kênh.",
                "prompt": "Vertical 9:16 tabletop shot of a 3D tactical terrain map of Bach Dang river estuary with miniature ships and tidal indicators beside a glowing tablet, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the tactical river terrain table and historical documents, warm studio lamp, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy tự hào về hào khí ngàn năm của tiền nhân dựng nước.",
                "prompt": "Vertical 9:16 grand closing shot of the modern Bach Dang river monument at sunrise, bronze statue standing proud against glowing dawn sky, peaceful homeland, strictly zero text, no cartoons.",
                "motion_prompt": "Slow majestic pullback from the monument toward the vast sunlit horizon, golden sunrise filling the frame with national pride, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 12. ban-do-quyen-luc
    # -------------------------------------------------------------------------
    {
        "slug": "ban-do-quyen-luc",
        "youtube_title": "Eo Biển Hormuz: Nút Thắt Dầu Mỏ Khiến Thế Giới Nín Thở",
        "thumbnail_text": "NÚT THẮT HORMUZ",
        "visual_hook": "Vertical 9:16 3D orbital satellite relief map of the Strait of Hormuz with glowing maritime navigation vectors and oil supertanker convoys, zero overlays, 25% margin",
        "bridge": "Xem toàn bộ hồ sơ địa chính trị Hormuz trên video dài của kênh.",
        "close": "Hãy nhìn vào các điểm nghẽn để thấu hiểu ván cờ thế giới.",
        "beats": [
            {
                "id": "S01",
                "narration": "Một eo biển hẹp chỉ ba mươi hải lý quyết định giá dầu toàn cầu.",
                "prompt": "Vertical 9:16 3D orbital satellite relief perspective of the Strait of Hormuz, rugged desert coastlines of Oman and Iran framing the turquoise narrow maritime passage, RealLifeLore investigative vector aesthetic, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth 35mm orbital push-in toward the narrowest constriction of the strait, realistic sun glint on deep ocean water, locked geographic geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Nơi một phần năm lượng dầu mỏ tiêu thụ trên thế giới bắt buộc phải đi qua.",
                "prompt": "Vertical 9:16 high-altitude survey of three massive VLCC crude oil supertankers sailing in line through the deep blue shipping lane, long white foam wakes trailing, strictly zero text, no cartoons.",
                "motion_prompt": "Steady high-altitude tracking pass alongside the convoy of massive oil tankers cruising through the strait, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Mỗi ngày có hàng trăm siêu tàu chở dầu rẽ sóng nối đuôi nhau.",
                "prompt": "Vertical 9:16 telephoto maritime view of the bow of a 300,000-ton crude carrier slicing through calm blue water, giant red bulbous bow cutting ocean swell, strictly zero text, no cartoons.",
                "motion_prompt": "Slow telephoto push-in toward the towering ship bow, water spray churning in morning sunlight, monumental scale, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S02",
            },
            {
                "id": "S04",
                "narration": "Làn hàng hải quốc tế ở đây hẹp đến mức chỉ đủ hai tàu tránh nhau.",
                "prompt": "Vertical 9:16 top-down satellite visualization of the twin two-mile-wide inbound and outbound separation channels in the strait, deep navy ocean water, strictly zero text, no cartoons.",
                "motion_prompt": "Slow downward zoom highlighting the narrow corridor between rugged island promontories, crisp bathymetric contours, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S05",
                "narration": "Nằm kẹp giữa các thế lực địa chính trị lớn với toan tính quyền lực.",
                "prompt": "Vertical 9:16 dramatic low-angle shot of rugged arid coastal cliffs towering over the narrow sea lane, deep desert shadows, harsh desert sunlight, strictly zero text, no cartoons.",
                "motion_prompt": "Slow cinematic lateral slide past the towering coastal bluffs looking down at distant tankers on the water, zero morphing.",
                "camera_motion": "pan_left",
                "transition": "smoothleft",
                "based_on": None,
            },
            {
                "id": "S06",
                "narration": "Chỉ cần một biến cố nhỏ làm nghẽn dòng chảy qua eo biển Hormuz,",
                "prompt": "Vertical 9:16 high-angle shot of a supertanker slowing to an emergency halt near a navigational buoy, anchor splash churning water into foam, strictly zero text, no cartoons.",
                "motion_prompt": "Slow-motion push-in as the massive ship slows and drops anchor, ripples expanding outward across the sea, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S07",
                "narration": "giá nhiên liệu và chuỗi cung ứng thế giới sẽ rơi vào khủng hoảng.",
                "prompt": "Vertical 9:16 macro shot of global financial market trading terminal monitors displaying fluctuating red and green candlestick charts in a dim room, strictly zero text, no cartoons.",
                "motion_prompt": "Slow optical rack focus across the glowing trading screens to a financial analyst hand resting on desk, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S08",
                "narration": "Các nền kinh tế lớn đều phải cử hạm đội tàu tuần tra bảo vệ.",
                "prompt": "Vertical 9:16 eye-level shot of a modern naval destroyer escorting a commercial crude carrier through open desert waters, steel gray hull slicing waves, strictly zero text, no cartoons.",
                "motion_prompt": "Steady lateral tracking pass alongside the naval escort ship keeping vigilant guard, realistic maritime spray, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Bản đồ quyền lực không nằm trên những tờ tuyên ngôn hoa mỹ.",
                "prompt": "Vertical 9:16 top-down shot of an antique brass compass and callipers measuring distances on a detailed maritime nautical chart on mahogany desk, strictly zero text, no cartoons.",
                "motion_prompt": "Slow precision push-in toward the brass calliper tips measuring the narrow strait on the chart, warm study lamplight, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S10",
                "narration": "Nó được định hình bởi những điểm nghẽn địa lý hiểm hóc trên mặt biển.",
                "prompt": "Vertical 9:16 3D relief globe visualization highlighting the strategic maritime chokepoints of the world connected by glowing trade arcs, strictly zero text, no cartoons.",
                "motion_prompt": "Slow rotating orbit around the 3D relief globe, focusing on the Middle East maritime corridors, zero morphing.",
                "camera_motion": "orbit_cw",
                "transition": "dissolve",
                "based_on": "S09",
            },
            {
                "id": "S11",
                "narration": "Kẻ nắm giữ yếu huyệt này sẽ có đòn bẩy điều tiết kinh tế toàn cầu.",
                "prompt": "Vertical 9:16 wide sunset view from a high mountain ridge overlooking the entire Strait of Hormuz, sun sinking into golden waters as ships navigate calmly below, strictly zero text, no cartoons.",
                "motion_prompt": "Slow majestic tilt up from the sea lanes to the glorious golden sunset sky, grand geopolitical scale, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Xem toàn bộ hồ sơ địa chính trị Hormuz trên video dài của kênh.",
                "prompt": "Vertical 9:16 macro tabletop shot of an investigative maritime dossier with satellite photographs and nautical charts beside a tablet screen on slate, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the tablet display and analytical maps, warm desk illumination, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy nhìn vào các điểm nghẽn để thấu hiểu ván cờ thế giới.",
                "prompt": "Vertical 9:16 contemplative shot of a diplomat or analyst looking out a high glass office window toward a busy harbor at twilight, quiet strategic insight, strictly zero text, no cartoons.",
                "motion_prompt": "Slow elegant pullback from the observer into the tranquil office, harbor lights twinkling on the horizon, serene conclusion, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 13. loi-sang-soi
    # -------------------------------------------------------------------------
    {
        "slug": "loi-sang-soi",
        "youtube_title": "Dụ Ngôn Người Gieo Giống: Đất Tâm Hồn Của Bạn Là Gì?",
        "thumbnail_text": "NGƯỜI GIEO GIỐNG",
        "visual_hook": "Vertical 9:16 Caravaggio chiaroscuro golden-hour oil-on-parchment parable shot of an ancient sower scattering golden wheat seeds across sunlit furrowed soil, zero overlays, 25% margin",
        "bridge": "Xem bài học chiêm nghiệm cuộc sống sâu sắc trên video dài của kênh.",
        "close": "Hãy chăm sóc mảnh đất tâm hồn của chính bạn mỗi ngày.",
        "beats": [
            {
                "id": "S01",
                "narration": "Một người gieo giống bước ra đồng, rải những hạt thóc đầu tiên.",
                "prompt": "Vertical 9:16 Caravaggio chiaroscuro golden-hour oil-on-parchment photograph of an ancient sower walking along a furrowed hillside at dawn, hand scattering golden wheat seeds into the morning air, BibleProject parabolic aesthetic, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth 35mm push-in following the sower hand as golden seeds scatter gracefully through warm sunbeams, locked biblical geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Hạt rơi bên vệ đường bị chim muông sà xuống ăn mất khi chưa kịp nảy mầm.",
                "prompt": "Vertical 9:16 ground-level shot of wheat seeds lying exposed on hard-packed dirt path, gentle birds swooping down in soft morning light, strictly zero text, no cartoons.",
                "motion_prompt": "Slow-motion low-angle tracking pass across the dry roadside path as birds flutter softly, natural realism, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Hạt rơi trên sỏi đá mọc lên nhanh chóng nhưng rễ không sâu nên sớm khô.",
                "prompt": "Vertical 9:16 macro shot of a fragile green seedling sprouting in thin dust atop cracked limestone rock under harsh midday sun, drooping leaves, strictly zero text, no cartoons.",
                "motion_prompt": "Slow macro push-in on the withered green seedling on barren rock, harsh sunbeams accentuating shallow roots, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S04",
                "narration": "Hạt rơi vào bụi gai bị gai góc bóp nghẹt, không thể đơm hoa kết trái.",
                "prompt": "Vertical 9:16 close-up of sharp thorn bushes crowding out young wheat stalks, tangled branches casting deep shadows over choked shoots, strictly zero text, no cartoons.",
                "motion_prompt": "Slow tilt down through the tangle of dry thorny briars choking the delicate wheat stalk, zero morphing.",
                "camera_motion": "pan_down",
                "transition": "smoothdown",
                "based_on": None,
            },
            {
                "id": "S05",
                "narration": "Chỉ những hạt rơi vào đất tốt màu mỡ mới sinh sôi gấp trăm lần.",
                "prompt": "Vertical 9:16 lush macro shot of healthy, tall golden wheat heads swaying gently in rich dark loam soil under warm afternoon sun, bountiful harvest mood, strictly zero text, no cartoons.",
                "motion_prompt": "Slow upward tilt through golden wheat stalks glowing with rich amber light, abundant agricultural vitality, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": None,
            },
            {
                "id": "S06",
                "narration": "Hạt giống chính là lời minh triết và cơ hội quý giá trong đời bạn.",
                "prompt": "Vertical 9:16 macro shot of open human hands holding a handful of radiant golden wheat grains, warm candlelight illuminating palm lines, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle push-in toward the open hands filled with golden grain, warm spiritual reverence, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S07",
                "narration": "Còn mảnh đất là trạng thái tâm hồn trước những biến thiên cuộc sống.",
                "prompt": "Vertical 9:16 wide composition of an expansive cultivated field at golden hour, plowed soil furrows leading the eye toward a solitary olive tree, strictly zero text, no cartoons.",
                "motion_prompt": "Slow sweeping lateral tracking pass along the plowed soil furrows toward the ancient olive tree, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S08",
                "narration": "Nếu lòng đầy gai góc của định kiến và lo toan, cơ hội quý cũng vụt mất.",
                "prompt": "Vertical 9:16 moody chiaroscuro composition of dry thorny branches cast in deep silhouette against an overcast twilight sky, strictly zero text, no cartoons.",
                "motion_prompt": "Slow pullback from the dark silhouette of thorns into the quiet twilight landscape, contemplative mood, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Muốn gặt quả ngọt, việc đầu tiên là nhổ sạch cỏ dại trong tâm trí.",
                "prompt": "Vertical 9:16 ground-level shot of hands gently clearing dry weeds and pebbles from rich dark garden soil, preparing clean earth, strictly zero text, no cartoons.",
                "motion_prompt": "Slow push-in on the caring hands working the fertile earth with patience and devotion, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S10",
                "narration": "Kiên nhẫn xới đất và nuôi dưỡng hạt mầm bằng tình yêu chân thành.",
                "prompt": "Vertical 9:16 macro shot of a fresh green sprout bathed in gentle water drops falling like soft dew from a clay pitcher, morning sunlight, strictly zero text, no cartoons.",
                "motion_prompt": "Ultra slow-motion capture of water drops nourishing the tiny green sprout in rich dark soil, sparkling light, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": "S09",
            },
            {
                "id": "S11",
                "narration": "Khi tâm hồn được thanh lọc, mọi điều thiện lành sẽ tự nhiên đơm hoa.",
                "prompt": "Vertical 9:16 wide panoramic shot of an endless golden wheat field rippling like ocean waves under a warm sunset sky, peace and abundance, strictly zero text, no cartoons.",
                "motion_prompt": "Slow sweeping dolly pullback across the sunlit wheat heads swaying in the evening breeze, breathtaking golden glow, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Xem bài học chiêm nghiệm cuộc sống sâu sắc trên video dài của kênh.",
                "prompt": "Vertical 9:16 macro tabletop shot of an ancient leather parchment scroll and brass oil lamp resting beside a glowing tablet screen on an olive wood desk, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the parchment scroll and oil lamp flame, warm golden spiritual study ambiance, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy chăm sóc mảnh đất tâm hồn của chính bạn mỗi ngày.",
                "prompt": "Vertical 9:16 serene closing shot of a person sitting peacefully beneath a large fig tree in a golden field, holding a single wheat stalk with gentle gratitude, strictly zero text, no cartoons.",
                "motion_prompt": "Slow elegant pullback from the peaceful figure beneath the tree, sunset light warming the pastoral landscape, tranquil ending, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 14. nao-luoi
    # -------------------------------------------------------------------------
    {
        "slug": "nao-luoi",
        "youtube_title": "Bẫy Dopamine: Vì Sao Bạn Càng Lướt Càng Thấy Mệt Mỏi?",
        "thumbnail_text": "BẪY DOPAMINE",
        "visual_hook": "Vertical 9:16 bioluminescent neural synapse split-screen visualization of dopamine receptor overload vs exhausted smartphone scrolling, zero overlays, 25% margin",
        "bridge": "Khám phá phương pháp cai nghiện dopamine tự nhiên trên video dài.",
        "close": "Hãy đặt điện thoại xuống và bắt tay vào việc quan trọng nhất.",
        "beats": [
            {
                "id": "S01",
                "narration": "Định lướt mạng mười phút, ngoảnh đi ngoảnh lại đã trôi hai tiếng.",
                "prompt": "Vertical 9:16 cinematic high-contrast photograph of a person lying on bed in a dark bedroom, face illuminated by the harsh blue glow of a smartphone screen, clock in background showing late night, Kurzgesagt and Huberman behavioral aesthetic, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth 35mm push-in toward the smartphone screen blue light reflecting in tired eyes, dark room shadows, locked geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Bạn không hề thiếu ý chí, mà bộ não đang bị mắc kẹt trong bẫy dopamine.",
                "prompt": "Vertical 9:16 3D bioluminescent neural synapse visualization showing glowing dopamine neurotransmitter molecules flooding synaptic clefts, deep indigo background, strictly zero text, no cartoons.",
                "motion_prompt": "Rapid smooth tracking move into the synaptic cleft as luminous dopamine molecules bind to receptors, vivid neural glow, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S03",
                "narration": "Mỗi cú quẹt ngón tay đem lại phần thưởng bất ngờ với kích thích nhỏ.",
                "prompt": "Vertical 9:16 macro close-up of a human thumb swiping rapidly up on a sleek glass smartphone screen, micro color flashes illuminating fingertips, strictly zero text, no cartoons.",
                "motion_prompt": "Slow-motion capture of thumb swiping upward in rhythm, glass surface catching dynamic ambient light reflections, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S01",
            },
            {
                "id": "S04",
                "narration": "Vùng tưởng thưởng thần kinh liên tục đòi hỏi liều kích thích cao hơn.",
                "prompt": "Vertical 9:16 3D brain map highlighting the glowing nucleus accumbens and mesolimbic pathway pulsing with intense electrical activity, strictly zero text, no cartoons.",
                "motion_prompt": "Slow camera orbit around the 3D transparent brain model, reward pathway pulsing with rhythmic amber light, zero morphing.",
                "camera_motion": "orbit_cw",
                "transition": "dissolve",
                "based_on": "S02",
            },
            {
                "id": "S05",
                "narration": "Khi các thụ thể bị bão hòa, bạn mất sạch hứng thú với việc quan trọng.",
                "prompt": "Vertical 9:16 microscopic visualization of desensitized neural receptors retracting into the cell membrane, glowing synapses dimming down to cool cyan, strictly zero text, no cartoons.",
                "motion_prompt": "Slow tilt down as synaptic receptor ports close and the neural glow fades into muted blue, zero morphing.",
                "camera_motion": "pan_down",
                "transition": "smoothdown",
                "based_on": "S02",
            },
            {
                "id": "S06",
                "narration": "Đọc một cuốn sách hay làm việc sâu bỗng trở nên vô cùng tẻ nhạt.",
                "prompt": "Vertical 9:16 eye-level shot of an open paper notebook and fountain pen lying neglected on a sunlit wooden desk beside an abandoned chair, strictly zero text, no cartoons.",
                "motion_prompt": "Slow lateral slide past the neglected notebook and pen, quiet dust motes floating in afternoon sunbeam, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S07",
                "narration": "Bạn kiệt sức không phải do làm việc, mà vì não bị kích thích quá tải.",
                "prompt": "Vertical 9:16 moody close-up of an adult rubbing tired temples with closed eyes, soft desk lamp glow casting gentle shadows on exhausted features, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle push-in on the person rubbing temples, authentic human vulnerability and cognitive fatigue, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S08",
                "narration": "Để thoát khỏi vòng lặp trì hoãn, hãy cắt đứt nguồn dopamine rẻ tiền.",
                "prompt": "Vertical 9:16 decisive action shot of a hand firmly placing a smartphone face-down inside a wooden desk drawer and sliding it shut, strictly zero text, no cartoons.",
                "motion_prompt": "Deliberate forward push-in as the wooden drawer slides shut with clean mechanical finality, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Để điện thoại ở phòng khác và dành ba mươi phút đầu ngày tĩnh lặng.",
                "prompt": "Vertical 9:16 serene morning shot of a clear glass of water and fresh journal resting on a clean wooden table by an open window, morning breeze, strictly zero text, no cartoons.",
                "motion_prompt": "Slow dolly pullback from the water glass on the sunlit table, crisp morning freshness, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S10",
                "narration": "Cho phép các thụ thể thần kinh được nghỉ ngơi và tự cân bằng lại.",
                "prompt": "Vertical 9:16 3D neural visualization of dopamine receptors re-emerging on the cell surface in balanced, healthy golden equilibrium, serene blue field, strictly zero text, no cartoons.",
                "motion_prompt": "Slow graceful orbit around the restored neural synapse glowing with calm steady luminescence, zero morphing.",
                "camera_motion": "orbit_cw",
                "transition": "dissolve",
                "based_on": "S05",
            },
            {
                "id": "S11",
                "narration": "Lấy lại khả năng tập trung sâu là bạn đã làm chủ cuộc sống của mình.",
                "prompt": "Vertical 9:16 eye-level shot of a focused person immersed in writing in a quiet library, calm purposeful expression, bright natural daylight, strictly zero text, no cartoons.",
                "motion_prompt": "Slow elegant pullback revealing the productive quiet library atmosphere around the focused writer, deep flow state mood, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Khám phá phương pháp cai nghiện dopamine tự nhiên trên video dài.",
                "prompt": "Vertical 9:16 macro tabletop shot of a habit tracker notebook and analog stopwatch resting beside a glowing tablet screen on dark oak desk, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the tablet display and organized productivity journal, warm desk lamp, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy đặt điện thoại xuống và bắt tay vào việc quan trọng nhất.",
                "prompt": "Vertical 9:16 inspiring closing shot of a person closing their eyes, taking a deep centering breath, and picking up a pen with calm determination, morning sunlight, strictly zero text, no cartoons.",
                "motion_prompt": "Slow cinematic pullback from the determined writer into the bright sunlit workspace, empowering resolution, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 15. thuong-cho-kheo
    # -------------------------------------------------------------------------
    {
        "slug": "thuong-cho-kheo",
        "youtube_title": "Nghệ Thuật Lắng Nghe Để Thấu Hiểu Trọn Vẹn Người Khác",
        "thumbnail_text": "NGHỆ THUẬT LẮNG NGHE",
        "visual_hook": "Vertical 9:16 warm editorial watercolor and golden-hour anamorphic shot of two figures seated on a sunlit balcony with gentle understanding, zero overlays, 25% margin",
        "bridge": "Xem nghệ thuật giao tiếp chữa lành tâm hồn trên video dài của kênh.",
        "close": "Hãy mở rộng trái tim để lắng nghe người thân yêu hôm nay.",
        "beats": [
            {
                "id": "S01",
                "narration": "Khi người bạn thương im lặng, bạn vội nghĩ họ đã hết quan tâm.",
                "prompt": "Vertical 9:16 warm editorial watercolor and 35mm anamorphic photograph of a person sitting pensively by a sunlit window with a warm ceramic tea cup, soft evening sunbeams, The School of Life emotional storytelling aesthetic, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth 35mm dolly push-in toward the contemplative figure beside the window, soft golden-hour shadows stretching across wooden floor, locked geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Nhưng khoảng lặng đôi khi là chiếc khiên chắn của nỗi niềm khó nói.",
                "prompt": "Vertical 9:16 close-up of hands gently cupping a warm ceramic mug, gentle steam rising into golden evening light, fragile emotional intimacy, strictly zero text, no cartoons.",
                "motion_prompt": "Slow optical rack focus from the ceramic mug to the delicate steam drifting into the warm air, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Phần lớn chúng ta lắng nghe không phải để hiểu mà để chuẩn bị đáp trả.",
                "prompt": "Vertical 9:16 two-shot across a wooden coffee table showing two individuals seated opposite each other, one speaking earnestly while the other listens thoughtfully, strictly zero text, no cartoons.",
                "motion_prompt": "Slow lateral tracking pass along the coffee table, capturing the genuine emotional presence between the two people, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S04",
                "narration": "Chúng ta vội đưa ra lời khuyên khi đối phương chỉ cần một bờ vai.",
                "prompt": "Vertical 9:16 macro shot of a gentle hand reaching across the table to lightly rest beside another hand, warm connection, soft bokeh, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle push-in as hand reaches across table with tender reassurance, warm natural daylight, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S03",
            },
            {
                "id": "S05",
                "narration": "Lắng nghe đích thực là tạm gác cái tôi và định kiến của bản thân.",
                "prompt": "Vertical 9:16 eye-level portrait of a compassionate listener with warm, gentle eyes reflecting undivided attention and empathy, soft golden hour lighting, strictly zero text, no cartoons.",
                "motion_prompt": "Slow subtle push-in on the compassionate expression, authentic emotional warmth, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S06",
                "narration": "Nhìn sâu vào ánh mắt và cảm nhận cảm xúc chưa được gọi tên.",
                "prompt": "Vertical 9:16 close-up of eyes softening with genuine understanding, warm sunlight reflecting in irises, poignant cinematic intimacy, strictly zero text, no cartoons.",
                "motion_prompt": "Slow optical push-in toward the expressive eyes, delicate eyelid movement and natural breathing, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": "S05",
            },
            {
                "id": "S07",
                "narration": "Một cái gật đầu ấm áp có sức mạnh hơn ngàn lời an ủi sáo rỗng.",
                "prompt": "Vertical 9:16 medium shot of a gentle affirming nod between two friends sitting on a park bench under golden autumn trees, leaves drifting, strictly zero text, no cartoons.",
                "motion_prompt": "Slow tracking move alongside the bench capturing the gentle nod and comforting silence, zero morphing.",
                "camera_motion": "pan_left",
                "transition": "smoothleft",
                "based_on": None,
            },
            {
                "id": "S08",
                "narration": "Khi được lắng nghe trọn vẹn, những vết thương lòng sẽ tự chữa lành.",
                "prompt": "Vertical 9:16 artistic macro composition of a green leaf with a healed seam holding dew drops under morning sunlight, delicate organic resilience, strictly zero text, no cartoons.",
                "motion_prompt": "Slow tilt up along the healed leaf surface, dew droplets catching rainbow prism rays, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Yêu thương không phải là thay đổi người khác theo ý muốn của mình.",
                "prompt": "Vertical 9:16 wide view of an open garden with diverse wildflowers blooming freely together in wild harmony, golden sunlight, strictly zero text, no cartoons.",
                "motion_prompt": "Slow sweeping lateral slide across the colorful wildflower garden swaying gently in summer breeze, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S10",
                "narration": "Yêu thương là tạo ra không gian an toàn để họ được là chính họ.",
                "prompt": "Vertical 9:16 warm inviting living room with a glowing fireplace, soft wool blanket on an armchair, gentle twilight outside window, strictly zero text, no cartoons.",
                "motion_prompt": "Slow graceful pullback revealing the safe, warm shelter of the cozy hearth, soothing ambiance, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S11",
                "narration": "Học cách lắng nghe bằng cả trái tim để tình cảm luôn bền chặt.",
                "prompt": "Vertical 9:16 two people walking side-by-side along a quiet seaside promenade at sunset, comfortable shared silence, golden reflections on wet sand, strictly zero text, no cartoons.",
                "motion_prompt": "Slow tracking shot from behind the two walking companions toward the glowing sunset horizon, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Xem nghệ thuật giao tiếp chữa lành tâm hồn trên video dài của kênh.",
                "prompt": "Vertical 9:16 macro tabletop shot of an illustrated relationship journal and ceramic vase with fresh lavender beside a tablet on dark wood, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the tablet screen and journal, warm ambient lamp glow, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy mở rộng trái tim để lắng nghe người thân yêu hôm nay.",
                "prompt": "Vertical 9:16 warm closing shot of two smiling family members sharing an affectionate embrace in a sun-drenched doorway, profound emotional peace, strictly zero text, no cartoons.",
                "motion_prompt": "Slow elegant pullback from the tender embrace into the warm home interior, loving heartfelt conclusion, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 16. nghe-song-sot
    # -------------------------------------------------------------------------
    {
        "slug": "nghe-song-sot",
        "youtube_title": "Chiến Lược Đòn Bẩy: Chăm Chỉ Có Tăng Được Lương?",
        "thumbnail_text": "ĐÒN BẨY CÔNG SỞ",
        "visual_hook": "Vertical 9:16 architectural corporate glass and isometric strategic chessboard shot with silver pieces moving decisively under dramatic executive lighting, zero overlays, 25% margin",
        "bridge": "Trọn bộ cẩm nang đàm phán thăng tiến đang có trên video dài của kênh.",
        "close": "Hãy bắt đầu nâng cấp giá trị bản thân ngay từ hôm nay.",
        "beats": [
            {
                "id": "S01",
                "narration": "Chăm chỉ cày cuốc cả năm nhưng bảng lương của bạn vẫn giậm chân.",
                "prompt": "Vertical 9:16 architectural corporate glass and steel office photograph of an executive conference room at dusk, empty sleek ergonomic chairs around a reflective glass table overlooking city skyline, Wall Street Journal career strategy aesthetic, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth 35mm push-in down the center of the reflective conference table toward the floor-to-ceiling city window, locked geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Doanh nghiệp không trả tiền cho sự vất vả, họ trả cho sự khó thay thế.",
                "prompt": "Vertical 9:16 macro shot of a sleek polished marble chessboard on a corporate desk, a single silver knight piece standing advanced in front of rows of black pawns, strictly zero text, no cartoons.",
                "motion_prompt": "Slow optical rack focus from the pawns to the solitary silver knight, crisp reflections on marble, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S03",
                "narration": "Nếu công việc ai cũng làm được, bạn sẽ luôn ở thế yếu khi đàm phán.",
                "prompt": "Vertical 9:16 high-angle isometric view of a modern open-plan office with identical workstations in repetitive grid alignment, cool corporate lighting, strictly zero text, no cartoons.",
                "motion_prompt": "Slow vertical pedestal rise over the uniform office cubicle grid, geometric architectural order, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": None,
            },
            {
                "id": "S04",
                "narration": "Người thông minh không cạnh tranh bằng số giờ ngồi ở văn phòng.",
                "prompt": "Vertical 9:16 macro shot of an executive analog wrist watch on dark leather strap resting beside a closed leather folio on an oak desk, ticking calmly, strictly zero text, no cartoons.",
                "motion_prompt": "Slow macro push-in on the precision mechanical watch movement and brushed steel bezel, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S05",
                "narration": "Họ tập trung xây dựng kỹ năng kép hiếm có mà thị trường đang khao khát.",
                "prompt": "Vertical 9:16 close-up of two precision steel gear cogs interlocking smoothly and multiplying mechanical torque, warm industrial corporate spotlight, strictly zero text, no cartoons.",
                "motion_prompt": "Precision lateral tracking as the two interlocking gears rotate smoothly in perfect mechanical synchronization, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S06",
                "narration": "Kết hợp chuyên môn sâu với tư duy hệ thống và xử lý khủng hoảng.",
                "prompt": "Vertical 9:16 eye-level shot of a professional strategist standing beside a transparent glass board with elegant structural workflow vectors, pointing calmly, strictly zero text, no cartoons.",
                "motion_prompt": "Slow steady push-in toward the confident professional at the glass board, bright daylight, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S05",
            },
            {
                "id": "S07",
                "narration": "Trở thành mắt xích then chốt trong chuỗi tạo ra lợi nhuận tổ chức.",
                "prompt": "Vertical 9:16 macro shot of a heavy gold-plated keystone link in a solid steel chain resting on dark slate, dramatic rim lighting, strictly zero text, no cartoons.",
                "motion_prompt": "Slow optical rack focus along the steel chain to the golden keystone link, tactile metallic textures, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S08",
                "narration": "Khi bạn nắm giữ đòn bẩy then chốt, vị thế thương lượng tự đổi chiều.",
                "prompt": "Vertical 9:16 two-shot across a polished boardroom table showing a confident professional presenting terms with a calm smile, corporate glass backdrop, strictly zero text, no cartoons.",
                "motion_prompt": "Slow deliberate push-in down the boardroom table toward the poised professional, warm executive lighting, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Đừng bán rẻ thời gian, hãy đầu tư nâng cấp giá trị nội tại bản thân.",
                "prompt": "Vertical 9:16 top-down composition of a sleek modern laptop, financial strategy books, and a ceramic coffee mug on a clean wooden desk, morning sunbeams, strictly zero text, no cartoons.",
                "motion_prompt": "Slow downward push-in highlighting the high-value learning workspace, crisp natural light, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S10",
                "narration": "Nâng cao năng lực chuyên môn là cách bảo hiểm tốt nhất cho sự nghiệp.",
                "prompt": "Vertical 9:16 eye-level shot of an executive walking confidently through a sunlit glass atrium corridor toward the city skyline, tailored attire, strictly zero text, no cartoons.",
                "motion_prompt": "Steady tracking shot behind the executive striding forward with calm purpose through the modern atrium, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S09",
            },
            {
                "id": "S11",
                "narration": "Làm chủ cuộc chơi công sở bằng tư duy chiến lược và sự khác biệt.",
                "prompt": "Vertical 9:16 wide shot of the silver chess piece alone in center of the board reflecting dramatic executive spotlights, masterclass mood, strictly zero text, no cartoons.",
                "motion_prompt": "Slow sweeping camera orbit around the triumphant silver piece, pristine marble surface reflections, zero morphing.",
                "camera_motion": "orbit_cw",
                "transition": "dissolve",
                "based_on": "S02",
            },
            {
                "id": "S12",
                "narration": "Trọn bộ cẩm nang đàm phán thăng tiến đang có trên video dài của kênh.",
                "prompt": "Vertical 9:16 macro tabletop shot of an executive career roadmap folio and gold pen resting beside a tablet screen on mahogany, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the tablet display and strategic career guide, warm study light, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy bắt đầu nâng cấp giá trị bản thân ngay từ hôm nay.",
                "prompt": "Vertical 9:16 inspiring closing shot of a professional standing on an outdoor skyscraper terrace overlooking the thriving city at dawn, calm confidence, strictly zero text, no cartoons.",
                "motion_prompt": "Slow elegant pullback from the terrace toward the vast morning sky, golden sun rising over the cityscape, empowering conclusion, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 17. ai-binh-dan
    # -------------------------------------------------------------------------
    {
        "slug": "ai-binh-dan",
        "youtube_title": "Tự Động Hóa Bằng AI Tiết Kiệm Bốn Giờ Mỗi Ngày",
        "thumbnail_text": "TỰ ĐỘNG HÓA AI",
        "visual_hook": "Vertical 9:16 sleek dark-mode glassmorphism UI telemetry and tactile productivity desk macro showing AI automated pipeline workflows executing, zero overlays, 25% margin",
        "bridge": "Xem hướng dẫn thiết lập hệ thống tự động hóa trên video dài của kênh.",
        "close": "Hãy thử ứng dụng trí tuệ nhân tạo vào công việc ngay hôm nay.",
        "beats": [
            {
                "id": "S01",
                "narration": "Đừng mất bốn tiếng làm báo cáo thủ công mỗi ngày một cách vất vả.",
                "prompt": "Vertical 9:16 sleek dark-mode glassmorphism photograph of a modern dual-monitor workstation, a tired office worker hand resting on a precision wireless mouse beside a messy stack of paper reports, Jeff Su productivity aesthetic, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth 35mm push-in toward the glowing dark-mode monitors, cyan ambient backlight reflecting on dark desk surface, locked geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Khi một chuỗi lệnh tự động giải quyết xong chỉ trong mười giây.",
                "prompt": "Vertical 9:16 macro shot of a sleek anodized aluminum mechanical keyboard with a glowing cyan enter key being pressed firmly, strictly zero text, no cartoons.",
                "motion_prompt": "Slow-motion precision push-in as the finger taps the glowing key, mechanical switch travel, crisp specular highlights, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Hàng ngàn dòng số liệu hỗn loạn lập tức được phân loại chuẩn xác.",
                "prompt": "Vertical 9:16 dynamic visualization of glowing data nodes cascading into neat, organized isometric grid matrices on a dark glass screen, futuristic telemetry aesthetic, strictly zero text, no cartoons.",
                "motion_prompt": "Rapid smooth tracking move following cascading data streams snapping into perfect symmetrical rows, zero morphing.",
                "camera_motion": "pan_down",
                "transition": "smoothdown",
                "based_on": None,
            },
            {
                "id": "S04",
                "narration": "Trí tuệ nhân tạo không sinh ra để thay thế người lao động chăm chỉ.",
                "prompt": "Vertical 9:16 warm eye-level shot of a professional smiling with relief as automated tasks complete, soft studio lighting, natural documentary realism, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle push-in on the smiling professional enjoying a calm moment, natural warmth, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S05",
                "narration": "Nó sinh ra để giải phóng bạn khỏi những thao tác lặp đi lặp lại nhàm chán.",
                "prompt": "Vertical 9:16 macro split view of automated file icons flying effortlessly between folders on a glass screen, smooth fluid motion graphics, strictly zero text, no cartoons.",
                "motion_prompt": "Slow lateral slide following seamless file transfer animations on dark glassmorphic UI, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S06",
                "narration": "Kết hợp các công cụ bảng tính với mô hình xử lý ngôn ngữ hiện đại.",
                "prompt": "Vertical 9:16 3D geometric concept of two glowing digital puzzle pieces connecting: a spreadsheet grid and a neural network node, cyan and amber lights, strictly zero text, no cartoons.",
                "motion_prompt": "Smooth 3D orbit around the two digital puzzle components snapping together, clean tech aesthetic, zero morphing.",
                "camera_motion": "orbit_cw",
                "transition": "dissolve",
                "based_on": None,
            },
            {
                "id": "S07",
                "narration": "Bạn biến chiếc máy tính thành một trợ lý đắc lực làm việc suốt đêm.",
                "prompt": "Vertical 9:16 nighttime shot of an ultra-clean minimalist desk with laptop running quietly under warm ambient desk light while room sleeps, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth dolly pullback from the quiet glowing laptop, serene nighttime productivity mood, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S08",
                "narration": "Dành quỹ thời gian quý báu cho quyết định chiến lược và sáng tạo.",
                "prompt": "Vertical 9:16 close-up of a person sketching strategic mind-map concepts with a fountain pen on an elegant sketchbook, natural morning window light, strictly zero text, no cartoons.",
                "motion_prompt": "Slow push-in following the creative pen strokes on paper, peaceful high-level thinking mood, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Ai biết tận dụng công cụ mới sẽ đi nhanh hơn phần còn lại gấp mười lần.",
                "prompt": "Vertical 9:16 architectural time-lapse view of a sleek modern skyscraper office with daylight sweeping across desks as one professional works effortlessly, strictly zero text, no cartoons.",
                "motion_prompt": "Slow cinematic lateral tracking pass across the futuristic office floor, morning sunlight streaming in, zero morphing.",
                "camera_motion": "pan_left",
                "transition": "smoothleft",
                "based_on": None,
            },
            {
                "id": "S10",
                "narration": "Công nghệ không phức tạp, chỉ cần bạn sẵn sàng thay đổi thói quen.",
                "prompt": "Vertical 9:16 macro shot of a friendly human hand reaching out to touch an interactive glowing glass holographic interface, warm touch, strictly zero text, no cartoons.",
                "motion_prompt": "Slow precision push-in toward the fingertip touching the responsive glass panel, gentle light ripple, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S11",
                "narration": "Làm chủ công nghệ để công nghệ phục vụ trọn vẹn cho cuộc sống của bạn.",
                "prompt": "Vertical 9:16 serene wide shot of a professional leaving the office early on a sunny afternoon with bag over shoulder, satisfied smile, strictly zero text, no cartoons.",
                "motion_prompt": "Slow graceful pullback as the professional walks out into golden afternoon sunlight, work-life balance mastery, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Xem hướng dẫn thiết lập hệ thống tự động hóa trên video dài của kênh.",
                "prompt": "Vertical 9:16 macro tabletop shot of an automation workflow blueprint displayed on a tablet screen beside a wireless keyboard on walnut desk, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the tablet screen and clean desk accessories, warm ambient study lighting, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy thử ứng dụng trí tuệ nhân tạo vào công việc ngay hôm nay.",
                "prompt": "Vertical 9:16 inspiring closing shot of a bright modern home office with coffee cup steaming gently in morning sun, peaceful productive day ahead, strictly zero text, no cartoons.",
                "motion_prompt": "Slow elegant pullback from the inviting desk into the sunny room, empowering technological liberation conclusion, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },

    # -------------------------------------------------------------------------
    # 18. tam-tinh-dem
    # -------------------------------------------------------------------------
    {
        "slug": "tam-tinh-dem",
        "youtube_title": "Khoảng Lặng Nửa Đêm: Vỗ Về Mệt Mỏi Sau Ngày Dài",
        "thumbnail_text": "KHOẢNG LẶNG ĐÊM",
        "visual_hook": "Vertical 9:16 atmospheric midnight velvet and glowing golden lantern fable shot of a rain-streaked window overlooking a sleepy nocturnal city, zero overlays, 25% margin",
        "bridge": "Thưởng thức trọn vẹn câu chuyện ru ngủ vỗ về trên video dài của kênh.",
        "close": "Hãy khép mi lại và đón nhận giấc ngủ an lành lúc này.",
        "beats": [
            {
                "id": "S01",
                "narration": "Đêm nay hãy để mọi âu lo lại sau lưng, bạn đã cố gắng rất nhiều.",
                "prompt": "Vertical 9:16 atmospheric midnight velvet and glowing golden lantern photograph of a rain-streaked bedroom window looking out at distant blurred city lights, warm amber lamp inside, Studio Ghibli nocturnal aesthetic, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth 35mm push-in toward the rain-streaked window pane, water droplets tracing gentle paths in golden lamp glow, locked geometry, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S02",
                "narration": "Tiếng mưa rơi êm đềm ru thế giới ngoài kia chìm vào giấc ngủ say.",
                "prompt": "Vertical 9:16 macro shot of raindrops splashing softly on an old wooden windowsill, glistening in amber light, deep midnight blue shadows, strictly zero text, no cartoons.",
                "motion_prompt": "Slow-motion capture of raindrops pattering rhythmically on the wet sill, tranquil nocturnal mood, zero morphing.",
                "camera_motion": "zoom_in",
                "transition": "fade",
                "based_on": "S01",
            },
            {
                "id": "S03",
                "narration": "Một ngày dài với những bộn bề và áp lực cuối cùng cũng đã khép lại.",
                "prompt": "Vertical 9:16 cozy bedroom interior showing an open book resting upside down on a soft wool blanket beside a sleeping cat, warm bedside lamp, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle tracking pass across the soft blanket and resting cat, deep cozy comfort, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S04",
                "narration": "Ngọn đèn vàng ấm áp thắp sáng góc phòng quen thuộc và bình yên.",
                "prompt": "Vertical 9:16 close-up of a vintage ceramic lamp with a pleated paper shade emitting soft 2700K golden light, casting gentle warm rings on a wooden nightstand, strictly zero text, no cartoons.",
                "motion_prompt": "Slow subtle push-in toward the glowing lamp shade, soothing amber warmth filling the frame, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S03",
            },
            {
                "id": "S05",
                "narration": "Thả lỏng toàn bộ cơ thể, lắng nghe từng hơi thở chậm rãi và nhịp nhàng.",
                "prompt": "Vertical 9:16 peaceful shot of a person resting comfortably in soft linen bedding, breathing slowly in the dim golden room light, deep tranquility, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle push-in on the peaceful sleeping profile, chest rising and falling in rhythmic rest, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S06",
                "narration": "Không còn vội vã, không còn những kỳ vọng nặng trĩu trên đôi vai.",
                "prompt": "Vertical 9:16 macro shot of a ceramic mug of warm chamomile tea resting on the nightstand, delicate curls of aromatic steam rising slowly, strictly zero text, no cartoons.",
                "motion_prompt": "Slow-motion tracking of the gentle steam curl dissolving into the midnight air, soothing stillness, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": "S04",
            },
            {
                "id": "S07",
                "narration": "Bạn xứng đáng có một khoảng lặng dịu dàng để vỗ về tâm hồn.",
                "prompt": "Vertical 9:16 wide view of a quiet cottage balcony under a starry midnight sky, a paper lantern glowing softly as summer crickets hum, strictly zero text, no cartoons.",
                "motion_prompt": "Slow majestic camera pullback from the glowing paper lantern into the vast starry night, serene atmosphere, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S08",
                "narration": "Hãy tha thứ cho những điều bạn chưa làm được trọn vẹn hôm nay.",
                "prompt": "Vertical 9:16 macro shot of a fallen autumn blossom floating peacefully down a dark still garden pond under moonlight, ripples softening, strictly zero text, no cartoons.",
                "motion_prompt": "Slow tracking move following the blossom floating in calm water, gentle moonlight reflections, zero morphing.",
                "camera_motion": "pan_right",
                "transition": "smoothright",
                "based_on": None,
            },
            {
                "id": "S09",
                "narration": "Ngày mai là một khởi đầu mới tinh khôi với những hy vọng mới.",
                "prompt": "Vertical 9:16 subtle dawn twilight creeping over distant mountain silhouettes, first faint violet glow on the horizon while stars still twinkle, strictly zero text, no cartoons.",
                "motion_prompt": "Slow upward tilt toward the fading stars as dawn violet light touches the sky, peaceful promise, zero morphing.",
                "camera_motion": "pan_up",
                "transition": "smoothup",
                "based_on": None,
            },
            {
                "id": "S10",
                "narration": "Giữ lấy sự dịu dàng trong lòng để bước tiếp con đường phía trước.",
                "prompt": "Vertical 9:16 close-up of hands gently smoothing a soft cotton quilt over shoulders, feeling warmth and safety in the quiet night, strictly zero text, no cartoons.",
                "motion_prompt": "Slow gentle push-in as hands settle comfortably under the warm quilt, total security, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": "S05",
            },
            {
                "id": "S11",
                "narration": "Chúc bạn có một giấc ngủ thật ngon lành và bình yên đêm nay.",
                "prompt": "Vertical 9:16 wide atmospheric view of the bedroom slowly dimming into deep peaceful midnight blue, nightlight glowing like a tiny firefly, strictly zero text, no cartoons.",
                "motion_prompt": "Slow graceful pullback as the room settles into profound silent slumber, tranquil nocturnal peace, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S12",
                "narration": "Thưởng thức trọn vẹn câu chuyện ru ngủ vỗ về trên video dài của kênh.",
                "prompt": "Vertical 9:16 macro tabletop shot of an illustrated fable book and glowing brass lantern beside a tablet screen on a bedside table, strictly zero text, no cartoons.",
                "motion_prompt": "Slow smooth push-in toward the glowing lantern and bedside tablet display, warm bedtime ambiance, zero morphing.",
                "camera_motion": "push_in",
                "transition": "fade",
                "based_on": None,
            },
            {
                "id": "S13",
                "narration": "Hãy khép mi lại và đón nhận giấc ngủ an lành lúc này.",
                "prompt": "Vertical 9:16 serene closing shot of the rain stopping, moon emerging through clouds to cast silver light across the quiet sleeping room, absolute stillness, strictly zero text, no cartoons.",
                "motion_prompt": "Slow cinematic pullback toward the silver moonlit window, deep peaceful nocturnal lullaby conclusion, zero morphing.",
                "camera_motion": "zoom_out",
                "transition": "fade",
                "based_on": "S12",
            },
        ],
    },
]


def build_full_spec_dict(raw: Dict[str, Any]) -> Dict[str, Any]:
    slug = raw["slug"]
    slug_u = slug.replace("-", "_")
    f_spec = vf.get_vn_flow_formula(slug)

    beats = raw["beats"]
    # Build scene pairs
    scene_pairs = []
    for i in range(len(beats) - 1):
        pair_id = f"PAIR_{i+1:02d}"
        scene_pairs.append({
            "id": pair_id,
            "start_beat_id": beats[i]["id"],
            "end_beat_id": beats[i+1]["id"],
            "target_duration": 4.0,
            "motion_prompt": beats[i]["motion_prompt"],
            "mode": "reference_start_end" if (i % 2 == 0) else "boundary_extend",
        })

    spec = {
        "channel_id": slug_u,
        "channel_slug": slug,
        "job_id": f"vn_pilot_{slug_u}_short_fullchain",
        "parent_long_id": f"{slug}-long-master",
        "format_profile": "short_9x16",
        "aspect": "9:16",
        "video_model": "omni_1_2_flash",
        "chain_mode": "scene_pairs",
        "voice": "VietNarrator",
        "total_duration_sec": 48.0,
        "youtube_title": raw["youtube_title"],
        "title": raw["youtube_title"],
        "thumbnail_spec": {
            "visual_hook": raw["visual_hook"],
            "allowed_text": raw["thumbnail_text"],
            "overlay_card": False,
            "prompt": (
                f"{raw['visual_hook']}, bold uppercase text '{raw['thumbnail_text']}', "
                f"{f_spec['continuity_anchor']}, strictly zero graphic overlays, no cartoons."
            ),
        },
        "packaging": {
            "cta_plan": {
                "bridge": raw["bridge"],
                "close": raw["close"],
            }
        },
        "cta_plan": {
            "bridge": raw["bridge"],
            "close": raw["close"],
        },
        "beats": beats,
        "scene_pairs": scene_pairs,
        "metadata": {
            "beats_count": len(beats),
            "pairs_count": len(scene_pairs),
            "total_duration_sec": 48.0,
            "youtube_title_length": len(raw["youtube_title"]),
            "bridge_syllables": count_syllables(raw["bridge"]),
            "close_syllables": count_syllables(raw["close"]),
        },
    }
    return spec


def process_channel(raw: Dict[str, Any], dry_tts: bool = False) -> Dict[str, Any]:
    slug = raw["slug"]
    slug_u = slug.replace("-", "_")
    logger.info(f"=== Processing Short Full-Chain for: {slug} ({slug_u}) ===")

    spec = build_full_spec_dict(raw)
    validate_spec_safety_and_rules(spec)

    # 1. Save spec to sys/channels/vn_rebuilt_style_specs/<slug>/<slug>_short_fullchain_spec.json
    spec_dir = SYS_DIR / f"channels/vn_rebuilt_style_specs/{slug}"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_file = spec_dir / f"{slug}_short_fullchain_spec.json"

    # 2. Setup video directories
    video_dir = Path("video") / f"vn_pilot_{slug_u}_short_fullchain"
    work_dir = video_dir / "_work_short"
    video_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    master_wav = video_dir / "narration_master.wav"
    work_wav = work_dir / "narration.wav"
    ass_path = work_dir / "subtitles_kinetic_9x16.ass"
    srt_path = work_dir / "subtitles.srt"
    watermark_png = work_dir / "watermark_100x100.png"
    aligned_spec_file = video_dir / f"{slug_u}_short_aligned_spec.json"

    # Fast cache check: if audio and spec are already present (>100KB), reuse and skip TTS
    if master_wav.is_file() and master_wav.stat().st_size > 100_000 and spec_file.is_file():
        logger.info(f"[{slug}] Reusing cached audio ({master_wav.stat().st_size} bytes) and spec at {spec_file}")
        cached_spec = json.loads(spec_file.read_text(encoding="utf-8"))
        words_count = 0
        if aligned_spec_file.is_file():
            aligned_d = json.loads(aligned_spec_file.read_text(encoding="utf-8"))
            words_count = len(aligned_d.get("words", []))
        return {
            "slug": slug,
            "spec_file": str(spec_file),
            "master_wav": str(master_wav),
            "total_duration": cached_spec.get("total_duration_sec", 48.0),
            "beats_count": len(cached_spec.get("beats", [])),
            "words_count": words_count,
        }

    # Synthesize audio with edge-tts VietNarrator
    logger.info(f"[{slug}] Synthesizing narration audio with VietNarrator...")
    tts_work_dir = work_dir / "_tts_work"
    norm_wav, real_total_dur, beat_durs, global_words = synthesize_vn_narration_and_words(
        beats=spec["beats"],
        voice="VietNarrator",
        audio_dir=tts_work_dir,
    )

    # Copy normalized wav to both master and work paths
    shutil.copy2(norm_wav, master_wav)
    shutil.copy2(norm_wav, work_wav)
    logger.info(f"[{slug}] Cached audio to {master_wav} ({master_wav.stat().st_size} bytes, {real_total_dur:.2f}s)")

    # Build kinetic ASS and sidecar SRT
    build_vn_kinetic_ass_subtitles(global_words, real_total_dur, ass_path, margin_v=270, outline=6)
    build_clean_sidecar_srt(spec["beats"], beat_durs, real_total_dur, srt_path)
    make_rounded_watermark(None, watermark_png, size=100, opacity=0.92, radius=15)

    # Update spec with exact measured durations
    spec["total_duration_sec"] = round(real_total_dur, 2)
    spec["metadata"]["total_duration_sec"] = round(real_total_dur, 2)
    cur_t = 0.0
    for i, b in enumerate(spec["beats"]):
        b_dur = round(beat_durs[i], 2)
        b["duration"] = b_dur
        b["at"] = round(cur_t, 2)
        cur_t += b_dur

    # Update scene pairs target durations
    for i, p in enumerate(spec["scene_pairs"]):
        if i < len(beat_durs):
            p["target_duration"] = round(beat_durs[i], 2)

    # Write spec file
    spec_file.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info(f"[{slug}] Saved updated spec to {spec_file}")

    # Write aligned spec file with words
    aligned_data = dict(spec)
    aligned_data["words"] = global_words
    aligned_data["beat_durations"] = [round(d, 2) for d in beat_durs]
    aligned_spec_file.write_text(json.dumps(aligned_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info(f"[{slug}] Saved aligned spec to {aligned_spec_file}")

    return {
        "slug": slug,
        "spec_file": str(spec_file),
        "master_wav": str(master_wav),
        "total_duration": real_total_dur,
        "beats_count": len(spec["beats"]),
        "words_count": len(global_words),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", type=str, default="all", help="Channel slug or 'all'")
    args = parser.parse_args()

    channels_to_process = (
        RAW_CHANNEL_SPECS
        if args.channel == "all"
        else [c for c in RAW_CHANNEL_SPECS if c["slug"] == args.channel]
    )

    if not channels_to_process:
        print(f"Unknown channel: {args.channel}")
        sys.exit(1)

    results = []
    for raw in channels_to_process:
        res = process_channel(raw)
        results.append(res)

    print("\n" + "=" * 60)
    print(f"COMPLETED {len(results)}/18 SHORT SPECS & AUDIO PRE-SYNTHESIS")
    print("=" * 60)
    for r in results:
        print(f"✓ {r['slug']:<20} | Dur: {r['total_duration']:.2f}s | Beats: {r['beats_count']} | Words: {r['words_count']} | Spec: {r['spec_file']}")


if __name__ == "__main__":
    main()
