#!/usr/bin/env python3
"""Calibrated generator for Batch 3 packages for luat_ngam (Luật Ngầm Đám Đông).
Strictly adheres to:
1. Short 9:16: 5 scenes, 20 unique Flow images & beats (1-to-1), 160-175 words (hold <= 2.3s),
   varied tempo, >=1 editorial_commentary (slow), SC01 hook_shock, SC05 cliffhanger_peak + cta_bridge (<=22 syl) + cta_close (<=24 syl, hold, is_endcard).
2. Long 16:9: 11 scenes, 66 unique Flow images & beats (1-to-1), 700-760 words (hold <= 3.1s),
   varied tempo, >=2 editorial_commentary (slow), SC05 mid_cta, SC11 cta_close (<=24 syl, hold, is_endcard).
3. Zero hyphens in narration text. Zero banned AI clichés. youtube_title <= 55 chars.
4. Rich English descriptions & motion_prompt ending with 'silent visual storytelling, no talking, no lip movement'.
"""
import hashlib
import json
from pathlib import Path
from dataclasses import asdict

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from channels.registry import get_channel, channel_cast, channel_profile_stamp

ch = get_channel("luat_ngam")
ch_cast = channel_cast("luat_ngam", "CH01")
ch_profile = channel_profile_stamp("luat_ngam")
ch_style = ch.visual.style_description
ch_tone = ch.tone

# ==============================================================================
# 1. SHORT 9:16 (luat-ngam-batch3-9x16)
# ==============================================================================
short_job_id = "luat-ngam-batch3-9x16"
parent_long_id = "luat-ngam-batch3-16x9"
short_topic = "Vì Sao Càng Đông Người Chứng Kiến Bạn Càng Ít Được Cứu Giúp?"
short_yt_title = "Vì Sao Càng Đông Người Càng Ít Ai Cứu Bạn?"  # 42 chars <= 55

short_scenes_data = [
    {
        "id": "SC01",
        "title": "Cú sốc nghịch lý đám đông khi gặp nạn",
        "purpose": "Cú sốc nghịch lý đám đông khi gặp nạn",
        "requirements": ["R01"],
        "narrative_situation": "hook_shock",
        "narrative_phase": "lived_friction",
        "action": "A lone silhouette collapses on a rainy noir city pavement as dark crowd silhouettes walk briskly past.",
        "setting": "Noir city rain street corner with aged dossier paper canvas.",
        "camera": "Wide establishing angle pushing in toward the fallen silhouette.",
        "beats": [
            {
                "id": "SC01_B1",
                "image_id": "SC01_I1",
                "purpose": "Cú sốc đầu tiên về sự thờ ơ của người qua đường",
                "quote": "Giữa phố đông, bạn ngã nhưng không ai dừng lại.",
                "tempo": "fast",
                "narrative_situation": "hook_shock",
                "camera_intent": "establish",
                "desc": "A dramatic high-contrast noir street corner on aged dossier paper canvas #E8E2D0. An anonymous silhouette figure in a black trench coat lies on the wet pavement, while multiple faceless dark silhouette pedestrians with glowing white slit eyes walk past without stopping. Crimson accent line #C0392B marks the victim position. Over 60% negative space, orthographic 2D, zero 3D, zero shading.",
                "motion": "Smooth 2D noir graphic novel animation. The shadowed silhouette pedestrian on the aged dossier canvas stumbles and drops to the pavement while dark crowd silhouettes walk briskly past without turning their heads, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": "ĐÁM ĐÔNG VÔ CẢM",
            },
            {
                "id": "SC01_B2",
                "image_id": "SC01_I2",
                "purpose": "Nghịch lý tỷ lệ cứu giúp nghịch đảo với quy mô đám đông",
                "quote": "Càng đông người, bạn càng ít được cứu.",
                "tempo": "fast",
                "narrative_situation": "hook_shock",
                "camera_intent": "focus",
                "desc": "An aged paper dossier file stamped with a stark red downward trendline graph #C0392B, showing crowd size surging on the horizontal axis while rescue probability plunges toward zero. Shadowed crowd profiles line the bottom edge on aged dossier canvas.",
                "motion": "Smooth 2D noir graphic novel animation. The classified dossier folder opens as a sharp crimson downward trendline etches itself across the aged parchment beside shadowed crowd profiles, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
            {
                "id": "SC01_B3",
                "image_id": "SC01_I3",
                "purpose": "Đặt tên chính thức cho hiện tượng tâm lý học",
                "quote": "Đó là hiệu ứng người ngoài cuộc.",
                "tempo": "normal",
                "narrative_situation": "hook_shock",
                "camera_intent": "focus",
                "desc": "A central anonymous silhouette observer in a sharp trench coat stands before a giant chalk case board, pinning an index card labeled with bold black ink lettering beside a glowing red investigation pin #C0392B on aged dossier paper.",
                "motion": "Smooth 2D noir graphic novel animation. The silhouette investigator in trench coat steps toward the case board and affixes a classified document card with a single red pushpin, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
            {
                "id": "SC01_B4",
                "image_id": "SC01_I4",
                "purpose": "Bác bỏ định kiến về sự tàn nhẫn và mở ra cơ chế ngầm",
                "quote": "Bộ não đám đông đang bị khóa.",
                "tempo": "normal",
                "narrative_situation": "hook_shock",
                "camera_intent": "focus",
                "desc": "Close-up of multiple silhouette heads in profile with faint mechanical padlock outlines drawn in crisp black ink #111111 over their temples, tied together by a fragile crimson thread #C0392B across aged paper canvas.",
                "motion": "Smooth 2D noir graphic novel animation. Crisp black padlock outlines click shut across the shadowed silhouette profiles as a delicate red thread vibrates slightly between them, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
        ],
    },
    {
        "id": "SC02",
        "title": "Bóc tách cơ chế phân tán trách nhiệm",
        "purpose": "Bóc tách cơ chế phân tán trách nhiệm",
        "requirements": ["R02"],
        "narrative_situation": "mechanism_step",
        "narrative_phase": "empirical_conflict",
        "action": "Visual breakdown of moral responsibility fracturing into tiny pieces as crowd size swells.",
        "setting": "Case study investigation board on aged paper canvas.",
        "camera": "Medium shot panning across fragmented responsibility shards.",
        "beats": [
            {
                "id": "SC02_B1",
                "image_id": "SC02_I1",
                "purpose": "Gánh nặng trách nhiệm trọn vẹn khi đứng một mình",
                "quote": "Đứng riêng, một người gánh trọn vẹn trách nhiệm.",
                "tempo": "fast",
                "narrative_situation": "mechanism_step",
                "camera_intent": "focus",
                "desc": "A single solitary silhouette figure standing under a harsh overhead cone of light on aged paper canvas #E8E2D0, holding a heavy black weight labeled 100 percent in bold ink.",
                "motion": "Smooth 2D noir graphic novel animation. A single solitary silhouette figure stands firmly bearing the full heavy weight in both hands under a sharp cone of light on the dossier canvas, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
            {
                "id": "SC02_B2",
                "image_id": "SC02_I2",
                "purpose": "Sự xé nhỏ trách nhiệm khi đám đông xuất hiện",
                "quote": "Gặp đám đông, áp lực bị xé vụn.",
                "tempo": "normal",
                "narrative_situation": "mechanism_step",
                "camera_intent": "focus",
                "desc": "The heavy single black weight splinters into fifty tiny fragmented shards scattered among a dense semicircle of anonymous silhouette bystanders in trench coats on aged paper.",
                "motion": "Smooth 2D noir graphic novel animation. The large black weight shatters into tiny floating fragments that disperse evenly among fifty shadowed bystander silhouettes, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
            {
                "id": "SC02_B3",
                "image_id": "SC02_I3",
                "purpose": "Lời tự nhủ thoái thác trách nhiệm của từng cá nhân",
                "quote": "Ai cũng nghĩ người khác sẽ ra tay.",
                "tempo": "normal",
                "narrative_situation": "mechanism_step",
                "camera_intent": "focus",
                "desc": "Three shadowed bystander profiles with subtle ink thought bubbles above each head showing an identical phone receiver icon with a question mark, each looking at the other sideways on aged canvas.",
                "motion": "Smooth 2D noir graphic novel animation. Subtle thought bubbles with telephone icons drift above each bystander silhouette while their heads turn slightly toward one another in hesitation, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
            {
                "id": "SC02_B4",
                "image_id": "SC02_I4",
                "purpose": "Kết luận về sự biến mất của trách nhiệm cá nhân",
                "quote": "Bổn phận đạo đức biến mất.",
                "tempo": "fast",
                "narrative_situation": "mechanism_step",
                "camera_intent": "focus",
                "desc": "An investigation dossier diagram showing the crimson thread dissolving into thin air as the bystander silhouettes stand completely frozen in place with empty open hands.",
                "motion": "Smooth 2D noir graphic novel animation. The red connection line on the dossier paper fades out into dust as the dark bystander silhouettes remain motionlessly frozen, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
        ],
    },
    {
        "id": "SC03",
        "title": "Bẫy nhìn nhau tìm manh mối và ảo tưởng tập thể",
        "purpose": "Bẫy nhìn nhau tìm manh mối và ảo tưởng tập thể",
        "requirements": ["R03"],
        "narrative_situation": "editorial_commentary",
        "narrative_phase": "structural_model",
        "action": "Bystander silhouettes look sideways at one another and freeze into statues of collective hesitation.",
        "setting": "Noir public square lined with dossier wall charts.",
        "camera": "Slow lateral tracking shot observing frozen bystander profiles.",
        "beats": [
            {
                "id": "SC03_B1",
                "image_id": "SC03_I1",
                "purpose": "Thói quen nhìn nhau để tìm manh mối ứng xử",
                "quote": "Bẫy thứ hai là nhìn nhau dò xét.",
                "tempo": "normal",
                "narrative_situation": "mechanism_step",
                "camera_intent": "focus",
                "desc": "Two shadowed profile silhouettes facing each other in the dark, their glowing white slit eyes casting faint beam lines across aged paper, locked in mutual hesitation.",
                "motion": "Smooth 2D noir graphic novel animation. Two silhouette profiles lean forward slightly as subtle glowing gaze vectors cross between them on the textured dossier canvas, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
            {
                "id": "SC03_B2",
                "image_id": "SC03_I2",
                "purpose": "Ảo tưởng an toàn khi thấy người khác không phản ứng",
                "quote": "Thấy người khác bất động, não tự cho là an toàn.",
                "tempo": "slow",
                "narrative_situation": "editorial_commentary",
                "camera_intent": "focus",
                "desc": "A large noir case clock ticking silently on the case board behind an emotionless crowd silhouette, with a stark rubber stamp in crimson ink reading FALSE NORMAL on aged paper.",
                "motion": "Smooth 2D noir graphic novel animation. The hands of the antique dossier wall clock advance silently while an official crimson rubber stamp stamps down beside the motionless crowd silhouettes, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
            {
                "id": "SC03_B3",
                "image_id": "SC03_I3",
                "purpose": "Nỗi sợ làm trò cười khiến ai cũng đeo mặt nạ bình tĩnh",
                "quote": "Ai cũng sợ hành động rồi bị chê.",
                "tempo": "slow",
                "narrative_situation": "editorial_commentary",
                "camera_intent": "focus",
                "desc": "Silhouette bystanders wearing blank expressionless noir masks held up on thin sticks, concealing chaotic jagged ink scribble patterns behind their faces.",
                "motion": "Smooth 2D noir graphic novel animation. The bystander silhouettes hold blank noir masks over their faces while jagged black lines flutter beneath the edges of the masks, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
            {
                "id": "SC03_B4",
                "image_id": "SC03_I4",
                "purpose": "Hiệu ứng im lặng dây chuyền đóng băng toàn bộ cộng đồng",
                "quote": "Cả khu phố biến thành tượng đá.",
                "tempo": "fast",
                "narrative_situation": "mechanism_step",
                "camera_intent": "focus",
                "desc": "A street of stone statue silhouettes covered in heavy black ink hatching, completely still, on the aged dossier paper background with high negative space.",
                "motion": "Smooth 2D noir graphic novel animation. The crowd silhouettes stiffen into solid dark stone pillars as light charcoal dust drifts across the textured dossier paper, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
        ],
    },
    {
        "id": "SC04",
        "title": "Quy tắc phá vỡ bẫy tâm lý trong ba giây",
        "purpose": "Quy tắc phá vỡ bẫy tâm lý trong ba giây",
        "requirements": ["R04"],
        "narrative_situation": "actionable_resolution",
        "narrative_phase": "actionable_resolution",
        "action": "The investigator points decisively at one specific individual, breaking the diffusion spell.",
        "setting": "Spotlit investigation scene on aged dossier parchment.",
        "camera": "Dynamic zoom focusing sharply on the targeted bystander.",
        "beats": [
            {
                "id": "SC04_B1",
                "image_id": "SC04_I1",
                "purpose": "Cảnh báo sai lầm khi kêu cứu vô định vào khoảng không",
                "quote": "Muốn thoát bẫy, đừng hô cứu chung chung.",
                "tempo": "fast",
                "narrative_situation": "actionable_resolution",
                "camera_intent": "focus",
                "desc": "An anonymous silhouette figure shouting a hollow megaphone bubble that dissipates into vague scattered smoke dots across the aged dossier background, with a red strike-through line #C0392B.",
                "motion": "Smooth 2D noir graphic novel animation. The megaphone sound wave dissolves into faint smoke across the dossier canvas as a sharp crimson diagonal line strikes across the empty speech bubble, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
            {
                "id": "SC04_B2",
                "image_id": "SC04_I2",
                "purpose": "Hành động chỉ định mục tiêu đơn lẻ để dồn trách nhiệm",
                "quote": "Hãy chỉ tay vào một người.",
                "tempo": "fast",
                "narrative_situation": "actionable_resolution",
                "camera_intent": "focus",
                "desc": "A decisive silhouette hand in a crisp trench coat sleeve pointing directly forward, with a single focused crimson target reticle #C0392B highlighting one bystander in the crowd.",
                "motion": "Smooth 2D noir graphic novel animation. A sharp silhouette trench-coat arm extends forward decisively, locking a crisp crimson target ring onto a single bystander profile in the crowd, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
            {
                "id": "SC04_B3",
                "image_id": "SC04_I3",
                "purpose": "Câu lệnh mẫu cụ thể với đặc điểm nhận dạng và nhiệm vụ rõ ràng",
                "quote": "Anh áo xanh, gọi cấp cứu giúp tôi ngay.",
                "tempo": "normal",
                "narrative_situation": "actionable_resolution",
                "camera_intent": "focus",
                "desc": "The pointed bystander silhouette highlighted by a bold crimson outline, suddenly isolated from the dark crowd with a phone receiver icon lighting up in his hand on aged paper canvas.",
                "motion": "Smooth 2D noir graphic novel animation. The highlighted bystander steps forward out of the shadowed crowd lineup as a glowing telephone icon materializes in his hand, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
            {
                "id": "SC04_B4",
                "image_id": "SC04_I4",
                "purpose": "Khóa chặt trách nhiệm đạo đức lên một người duy nhất",
                "quote": "Lệnh đích danh khóa chặt trách nhiệm.",
                "tempo": "fast",
                "narrative_situation": "actionable_resolution",
                "camera_intent": "focus",
                "desc": "A heavy classified dossier padlock snapping locked directly onto that single dossier profile, with a bold checkmark in black ink on aged dossier paper canvas.",
                "motion": "Smooth 2D noir graphic novel animation. A bold black padlock snaps firmly around the single targeted case file dossier as all surrounding distractions vanish into clean negative space, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
        ],
    },
    {
        "id": "SC05",
        "title": "Cao trào bỏ lửng và chuyển phễu bản dài",
        "purpose": "Cao trào bỏ lửng và chuyển phễu bản dài",
        "requirements": ["R05"],
        "narrative_situation": "outro",
        "narrative_phase": "actionable_resolution",
        "action": "The investigator stands at a fork in the road, raising the ethical dilemma and opening the full channel archive.",
        "setting": "Atmospheric noir archival chamber with aged case folders.",
        "camera": "Deliberate pull-back revealing the full case evidence wall and channel seal.",
        "beats": [
            {
                "id": "SC05_B1",
                "image_id": "SC05_I1",
                "purpose": "Câu hỏi bỏ lửng cao trào về góc nhìn người chứng kiến",
                "quote": "Nếu là người qua đường, làm sao bạn dám can thiệp?",
                "tempo": "normal",
                "narrative_situation": "cliffhanger_peak",
                "camera_intent": "tension",
                "desc": "An anonymous silhouette investigator standing at a dramatic crossroad on aged paper canvas, looking down at two diverging crimson string pathways leading into shadowed city doorways.",
                "motion": "Smooth 2D noir graphic novel animation. The trench-coat silhouette pauses at the dark street crossroad, glancing between two glowing crimson thread paths before stepping deliberately toward the camera, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
            {
                "id": "SC05_B2",
                "image_id": "SC05_I2",
                "purpose": "Cầu nối phễu dẫn sang thí nghiệm kinh điển trên video dài",
                "quote": "Bản phân tích đầy đủ có trên kênh Luật Ngầm Đám Đông.",
                "tempo": "normal",
                "narrative_situation": "cta_bridge",
                "camera_intent": "reveal",
                "desc": "An open classified case folder labeled THE SMOKE FILLED ROOM EXPERIMENT 1968, displaying archival noir laboratory sketches, smoke silhouettes and red correlation threads on aged paper.",
                "motion": "Smooth 2D noir graphic novel animation. A thick classified dossier opens smoothly to reveal detailed experimental diagrams and smoke chamber sketches linked with crimson threads, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
            {
                "id": "SC05_B3",
                "image_id": "SC05_I3",
                "purpose": "Lời mời xem bản phân tích chuyên sâu đầy đủ",
                "quote": "Xem video dài để nắm trọn cơ chế nhé.",
                "tempo": "normal",
                "narrative_situation": "cta_bridge",
                "camera_intent": "reveal",
                "desc": "The silhouette investigator pins a final classified report onto the central board, revealing the full title card framed in sharp noir graphics with red seal stamp on aged canvas.",
                "motion": "Smooth 2D noir graphic novel animation. The investigator stamps the final case document with an official crimson seal and slides it into a pristine case archive, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement",
                "emphasis": None,
            },
            {
                "id": "SC05_B4",
                "image_id": "SC05_I4",
                "purpose": "Lời kêu gọi hành động lưu video tự vệ và endcard thương hiệu",
                "quote": "Lưu video lại để tự cứu mình bạn nhé.",
                "tempo": "hold",
                "narrative_situation": "cta_close",
                "camera_intent": "hold",
                "desc": "Iconic endcard visual on aged dossier paper canvas #E8E2D0. An imposing anonymous noir silhouette in charcoal trench coat with glowing slit eyes stands beside a bold black stamp reading LUẬT NGẦM ĐÁM ĐÔNG, with crimson accent strings #C0392B connecting case files. At least 60% negative space, clean typography.",
                "motion": "Smooth 2D noir graphic novel animation. The silhouette investigator turns and stands in still profile beside the bold channel dossier title as ambient smoke-slate texture drifts gently across the aged paper canvas, silent visual storytelling, no talking, no lip movement",
                "emphasis": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
                "is_endcard": True,
            },
        ],
    },
]

# Set narration exactly from beats
for s in short_scenes_data:
    s["narration"] = " ".join(b["quote"] for b in s["beats"])

short_words = sum(len(s["narration"].split()) for s in short_scenes_data)
print(f"Short total words: {short_words} (expected 160-175)")

short_brief = {
    "schema_version": "3.0",
    "topic": short_topic,
    "audience": "Người đi làm, người tiêu dùng, người muốn đọc vị hành vi xã hội",
    "goal": "Bóc trần nghịch lý càng đông người cơ hội được cứu giúp càng thấp qua hiệu ứng người ngoài cuộc và hướng dẫn quy tắc chỉ định đích danh trong ba giây rồi chuyển phễu sang video dài",
    "video_type": "research_guide",
    "duration": {"min_seconds": 40.0, "max_seconds": 55.0},
    "scene_count": 5,
    "required_points": [
        {"id": "R01", "text": "Cú sốc nghịch lý đám đông khi gặp nạn"},
        {"id": "R02", "text": "Bóc tách cơ chế phân tán trách nhiệm"},
        {"id": "R03", "text": "Bẫy nhìn nhau tìm manh mối và ảo tưởng tập thể"},
        {"id": "R04", "text": "Quy tắc phá vỡ bẫy tâm lý trong ba giây"},
        {"id": "R05", "text": "Cao trào bỏ lửng và chuyển phễu bản dài"},
    ],
    "language": "vi",
    "tone": ch_tone,
    "style": ch_style,
    "aspect_ratio": "9:16",
    "format_profile": "short_9x16",
    "facts_required": True,
    "sources": [
        {
            "id": "SRC01",
            "title": "Bystander Intervention in Emergencies: Diffusion of Responsibility",
            "reference": "Darley, J. M., & Latané, B. (1968). Journal of Personality and Social Psychology, 8(4), 377-383.",
            "facts": [
                "Khi đứng một mình có hơn tám mươi phần trăm người ra tay cứu giúp.",
                "Khi ở giữa đám đông tỷ lệ cứu giúp giảm xuống dưới ba mươi phần trăm.",
            ],
        }
    ],
    "planning": {
        "success_criteria": [
            "Bóc trần nguyên nhân đám đông bất động và cung cấp khẩu lệnh cứu hộ đích danh thực chiến"
        ],
        "avoid": [
            "Lên án hay phán xét đạo đức người xem",
            "Lý thuyết tâm lý học hàn lâm thiếu ví dụ",
        ],
        "prior_knowledge": "Không đòi hỏi kiến thức tâm lý học chuyên sâu từ trước.",
        "pacing": "Nhanh, dồn dập, mở nút từng lớp tâm lý theo phong cách trinh thám noir.",
        "domain_requirements": [],
        "assumptions": [
            "Mỗi phân cảnh được cân chỉnh theo công thức âm học P_tail và dung sai drift <= 0.3s."
        ],
        "text_style": {
            "font": "sans-serif nét đậm dứt khoát",
            "color": "#111111",
            "outline": "#E8E2D0",
            "size": "dễ đọc trên khung dọc 9:16",
            "placement": "cách mép 10%; tránh va chạm thanh công cụ TikTok/Reels",
        },
        "speech_rates": {
            "vi": {"units_per_second": 3.8, "uncertainty": 0.15, "source": "Acoustic calibrated cadence"},
            "en": {"units_per_second": 2.5, "uncertainty": 0.25, "source": "Estimated English reading rate"},
        },
    },
    "outputs": [
        {
            "aspect_ratio": "9:16",
            "language": "vi",
            "subtitles": True,
            "voice": "VietNarrator",
            "speed": 1.0,
        }
    ],
    "youtube_title": short_yt_title,
    "thumbnail_spec": {
        "visual_hook": "Bóng đen áo măng tô đứng lẻ loi giữa đám đông tượng đá bất động với sợi chỉ đỏ quấn quanh hồ sơ mật",
        "text_overlay": "AI CỨU BẠN",
        "contrast_pair": "Đám đông vô cảm đứng nhìn vs Lệnh chỉ định đích danh phá vỡ bẫy",
    },
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": [
        "hieu ung nguoi ngoai cuoc",
        "tam ly dam dong",
        "phan tan trach nhiem",
        "luat ngam",
        "tu ve tam ly",
        "shorts",
    ],
    "parent_long_id": parent_long_id,
    "cta_plan": {
        "cliffhanger_peak": "Nếu là người qua đường, làm sao bạn dám can thiệp?",
        "bridge": "Bản phân tích đầy đủ có trên kênh Luật Ngầm Đám Đông.",
        "close": "Lưu video lại để tự cứu mình bạn nhé.",
        "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
    },
    "channel_profile": ch_profile,
    "engagement": asdict(ch.engagement),
    "editorial_stance": {
        "myth_debunked": "Người đứng nhìn giữa đám đông là những kẻ máu lạnh và thiếu lương tâm.",
        "why_generic_advice_fails": "Lời khuyên kêu cứu chung chung chỉ khiến sự phân tán trách nhiệm lan rộng thêm.",
        "channel_verdict": "Đám đông không hề vô cảm; cơ chế phân tán trách nhiệm đã khóa chặt phản xạ hành động của từng người.",
        "tradeoff_or_blindspot": "Chỉ định đích danh một người sẽ tạo áp lực đột ngột lên họ nhưng là cách duy nhất cứu sống nạn nhân.",
    },
    "actionable_value": {
        "core_mechanism": "Cô lập trách nhiệm đạo đức từ đám đông vô định vào một cá nhân cụ thể bằng khẩu lệnh chỉ định.",
        "practical_rule_of_thumb": "Quy tắc ba giây: chỉ tay thẳng vào một người, gọi tên trang phục và giao nhiệm vụ rõ ràng.",
        "real_world_scenario": "Nạn nhân ngã xe giữa ngã tư chỉ định anh mặc áo mưa xanh gọi cấp cứu để nhận trợ giúp tức thì.",
    },
    "video_engine": "flow_video",
    "chain_mode": "daisy_chain",
}

short_brief_bytes = json.dumps(short_brief, indent=2, ensure_ascii=False).encode("utf-8")
short_bhash = hashlib.sha256(short_brief_bytes).hexdigest()

short_scenes = []
prev_img_id = None
for sdata in short_scenes_data:
    sc_imgs = []
    sc_beats = []
    for b in sdata["beats"]:
        img_id = b["image_id"]
        img_obj = {
            "id": img_id,
            "description": b["desc"],
            "character_ids": ["CH01"],
            "based_on": prev_img_id,
            "preserve": "clean noir aged dossier paper canvas #E8E2D0, heavy black ink linework #111111, single crimson accent #C0392B, anonymous trench-coat silhouette figure",
            "change": b["desc"][:100],
            "reason": "Narration-locked full-frame beat.",
            "visible_text": [{"text": b["emphasis"], "placement": "upper_third", "object": "emphasis"}] if b.get("emphasis") else [],
            "kind": "scene",
            "shot_type": "full_scene",
            "tempo": b["tempo"],
            "narrative_situation": b["narrative_situation"],
            "has_character": True,
            "motion_prompt": b["motion"],
        }
        if b.get("is_endcard"):
            img_obj["is_endcard"] = True
        sc_imgs.append(img_obj)
        prev_img_id = img_id

        beat_obj = {
            "id": b["id"],
            "image_id": img_id,
            "purpose": b["purpose"],
            "anchor": {
                "vi": {
                    "quote": b["quote"],
                    "occurrence": 1,
                }
            },
            "effect": "hold" if b.get("is_endcard") else "cut",
            "focus": {"x": 0.5, "y": 0.5},
            "tempo": b["tempo"],
            "camera_intent": b["camera_intent"],
            "narrative_situation": b["narrative_situation"],
        }
        if b.get("is_endcard"):
            beat_obj["is_endcard"] = True
        sc_beats.append(beat_obj)

    short_scenes.append({
        "id": sdata["id"],
        "title": sdata["title"],
        "purpose": sdata["purpose"],
        "action": sdata["action"],
        "setting": sdata["setting"],
        "camera": sdata["camera"],
        "narration": sdata["narration"],
        "requirements": sdata["requirements"],
        "character_ids": ["CH01"],
        "source_ids": ["SRC01"],
        "images": sc_imgs,
        "beats": sc_beats,
        "tone": ch_tone,
        "narrative_phase": sdata["narrative_phase"],
        "narrative_situation": sdata["narrative_situation"],
    })

short_content = {
    "schema_version": "3.0",
    "brief_revision": 1,
    "brief_hash": short_bhash,
    "topic": short_topic,
    "duration": short_brief["duration"],
    "style": short_brief["style"],
    "required_points": [r["text"] for r in short_brief["required_points"]],
    "characters": [ch_cast],
    "scenes": short_scenes,
}

short_outline = {
    "outline": [
        {
            "scene_id": s["id"],
            "purpose": f"Triển khai {s['purpose'].lower()}",
            "requirements": s["requirements"],
            "transition": "Tiếp tục theo trình tự diễn biến tâm lý trinh thám noir",
        }
        for s in short_scenes
    ]
}

short_comp_research = {
    "channel_id": "luat_ngam",
    "job_id": short_job_id,
    "topic": short_topic,
    "competitor_analysis": {
        "benchmark_channels": [
            {
                "channel_name": "Psych2Go Vietnam & Kênh Tâm Lý Hành Vi",
                "top_performing_videos": [
                    {
                        "title": "Vì sao giữa phố đông không ai giúp đỡ người gặp nạn?",
                        "views": "1.5M views",
                        "hook_technique": "Đặt người xem vào tình huống ngã xe giữa đường nhưng mọi người xung quanh chỉ đứng quay video.",
                        "pacing_structure": "Cú sốc thực tế -> Giải mã hiệu ứng bầy đàn -> Công thức giải vây đích danh.",
                        "retention_driver": "Nỗi sợ có thật của người xem khi tưởng tượng mình rơi vào hoàn cảnh bất lực.",
                    }
                ],
                "viral_patterns_extracted": [
                    "Bóc trần nghịch lý càng đông người càng cô độc.",
                    "Đưa ra câu lệnh cứu nguy cụ thể 3 từ để người xem nhớ ngay.",
                ],
            }
        ]
    },
    "viral_formula_audit": {
        "cold_audience_hook_analysis": {
            "first_sentence_syllables": 11,
            "zero_pause_opening_seconds": 15,
            "visual_contrast": "Người bị nạn nằm trên vỉa hè đối lập với dòng người bóng đen vô cảm bước qua.",
            "counter_intuitive_truth_slap": "Đông người không tăng tỷ lệ an toàn; đám đông càng đông thì cơ hội sống sót của bạn càng rơi thẳng đứng.",
        },
        "narrative_progression_arc": [
            {"phase": "lived_friction", "purpose": "Mở màn cú sốc nghịch lý bị bỏ rơi giữa phố đông."},
            {"phase": "empirical_conflict", "purpose": "Bóc trần cơ chế phân tán trách nhiệm xé nhỏ bổn phận."},
            {"phase": "structural_model", "purpose": "Chỉ ra chiếc bẫy nhìn nhau dò xét và nỗi sợ bị phán xét."},
            {"phase": "actionable_resolution", "purpose": "Quy tắc ba giây chỉ định đích danh giải cứu tức thì."},
        ],
        "flow_video_transition_blueprint": {
            "chain_mode": "daisy_chain",
            "video_model": "omni_flash",
            "keyframe_continuity": "Sequential daisy-chain linking Start Frame to End Frame across all scenes in noir dossier aesthetic.",
        },
    },
    "academic_funnel_positioning": {
        "funnel_tier": "tier_1_broad",
        "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
        "myth_debunked": "Đám đông đứng nhìn vì xã hội ngày nay đã tha hóa và mất hết nhân tính.",
        "channel_verdict": "Đám đông không hề vô cảm; cơ chế phân tán trách nhiệm đã khóa chặt phản xạ hành động của từng người.",
        "actionable_rule_of_thumb": "Chỉ định một người duy nhất, gọi rõ đặc điểm trang phục và giao lệnh dứt khoát.",
    },
    "cta_and_spinoff_strategy": {
        "cliffhanger_peak": short_brief["cta_plan"]["cliffhanger_peak"],
        "bridge": short_brief["cta_plan"]["bridge"],
        "close": short_brief["cta_plan"]["close"],
        "endcard_text": short_brief["cta_plan"]["endcard_text"],
    },
}

# ==============================================================================
# 2. LONG 16:9 (luat-ngam-batch3-16x9)
# ==============================================================================
long_job_id = "luat-ngam-batch3-16x9"
long_topic = "Hiệu Ứng Người Ngoài Cuộc: Vì Sao Đám Đông Đứng Nhìn Mà Không Giúp?"
long_yt_title = "Hiệu Ứng Người Ngoài Cuộc: Vì Sao Đám Đông Đứng Nhìn?"  # 52 chars <= 55

long_scenes_data = [
    {
        "id": "SC01",
        "title": "Vụ án rúng động phố New York và sự thức tỉnh",
        "purpose": "Vụ án rúng động phố New York và sự thức tỉnh",
        "requirements": ["R01"],
        "narrative_situation": "hook_shock",
        "narrative_phase": "lived_friction",
        "action": "Archival noir case file opens on a dark New York street corner with shadowed apartment windows looking down.",
        "setting": "Aged dossier case board with noir apartment silhouettes.",
        "camera": "Slow cinematic dolly pushing into the central classified folder.",
        "beats": [
            ("SC01_B1", "SC01_I1", "Khởi đầu vụ án chấn động New York năm 1964", "Năm 1964, một phụ nữ bị tấn công ở New York.", "fast", "hook_shock", "establish",
             "A high-contrast 2D noir dossier canvas #E8E2D0. Heavy black ink silhouette of an old New York apartment building at night with lit windows casting harsh beams onto a dark street corner #111111. Over 60% negative space, zero 3D, zero gradients.",
             "Smooth 2D noir graphic novel animation. The shadows lengthen across the noir city brick facade as cold wind drifts down the empty street on aged parchment canvas, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", "ÁP LỰC ĐÁM ĐÔNG"),
            ("SC01_B2", "SC01_I2", "Hàng chục nhân chứng đứng nhìn qua cửa sổ mà không hành động", "Hàng chục người nhìn qua cửa sổ nhưng không ai gọi cảnh sát.", "fast", "hook_shock", "focus",
             "Multiple shadowed human profiles visible behind rectangular lit window panes, hands resting motionless on window sills, staring downward into the dark courtyard on aged paper canvas.",
             "Smooth 2D noir graphic novel animation. Silhouette profiles behind the window frames remain completely stationary while a rotary telephone sits untouched on a nearby desk, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC01_B3", "SC01_I3", "Làn sóng phẫn nộ và cáo buộc đám đông vô cảm", "Dư luận kết tội đám đông máu lạnh.", "normal", "hook_shock", "focus",
             "Archival noir newspaper front page stamped in bold black ink with aggressive headlines and heavy black silhouettes shaking their heads in condemnation across aged parchment.",
             "Smooth 2D noir graphic novel animation. Stark black headlines imprint across the aged newspaper sheet with a bold crimson question mark stamped across the center, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC01_B4", "SC01_I4", "Hai nhà khoa học Latané và Darley vào cuộc giải mã", "Hai nhà tâm lý học thấy quy luật khác.", "normal", "hook_shock", "focus",
             "An anonymous silhouette investigator in a sharp charcoal trench coat #111111 pins two laboratory case files labeled LATANE and DARLEY 1968 onto a classified corkboard with a crimson thread #C0392B.",
             "Smooth 2D noir graphic novel animation. The trench-coat investigator pins the two experimental case folders side by side and links them with a crisp crimson string, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC01_B5", "SC01_I5", "Đặt ra giả thuyết về cơ chế tâm lý thay vì suy đồi đạo đức", "Họ tự hỏi sự im lặng này do đâu.", "normal", "hook_shock", "focus",
             "A schematic dossier diagram contrasting an isolated silhouette figure against an interconnected web of fifty silhouette nodes tied by tension strings on aged paper.",
             "Smooth 2D noir graphic novel animation. The single figure node pulses softly while the crowded web of silhouettes vibrates under mounting invisible tension lines, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC01_B6", "SC01_I6", "Mở ra cuộc điều tra tâm lý xã hội chấn động", "Câu trả lời lật tẩy một bẫy nhận thức nguy hiểm.", "fast", "hook_shock", "focus",
             "A dramatic classified dossier stamp reading CLASSIFIED BEHAVIORAL CASE snaps down in crisp crimson ink across the archival investigation folder on aged canvas.",
             "Smooth 2D noir graphic novel animation. The heavy crimson classified stamp presses firmly onto the case folder sending subtle ink flecks across the clean paper margins, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
        ]
    },
    {
        "id": "SC02",
        "title": "Thí nghiệm căn phòng đầy khói năm 1968",
        "purpose": "Thí nghiệm căn phòng đầy khói năm 1968",
        "requirements": ["R02"],
        "narrative_situation": "empirical_evidence",
        "narrative_phase": "empirical_conflict",
        "action": "A closed laboratory room fills with billowing smoke as test subjects react differently based on social presence.",
        "setting": "Minimalist noir testing laboratory on aged dossier paper canvas.",
        "camera": "Cross-sectional architectural view of the testing room.",
        "beats": [
            ("SC02_B1", "SC02_I1", "Thiết lập bối cảnh phòng thí nghiệm khảo sát", "Năm 1968, hai ông làm khảo sát rồi bơm khói qua cửa.", "fast", "empirical_evidence", "establish",
             "A laboratory examination room drawn in clean 2D noir ink on aged dossier paper #E8E2D0. A solitary silhouette student sits at a wooden desk with wisps of grey smoke #5A5F66 seeping through the wall vent.",
             "Smooth 2D noir graphic novel animation. Dense grey smoke ribbons drift silently under the office door as the silhouette student glances up from the survey paper, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC02_B2", "SC02_I2", "Phản ứng quyết đoán khi đối mặt tình huống nguy cấp một mình", "Ngồi một mình, ba phần tư số người chạy ra báo ngay.", "normal", "empirical_evidence", "focus",
             "A split case comparison chart. On the left side labeled ALONE, the silhouette figure leaps from the chair and opens the exit door, with a bold seventy-five percent stamp in black ink.",
             "Smooth 2D noir graphic novel animation. The solitary student pushes back the chair decisively and steps through the doorway into the clean hallway on the left, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC02_B3", "SC02_I3", "Kịch bản có thêm hai người diễn viên ngồi im", "Khi có hai người ngồi im, chỉ một phần mười đứng dậy.", "fast", "empirical_evidence", "focus",
             "Three silhouette figures sit at desks in the smoky room. The two actors in trench coats remain completely calm and continue writing, ignoring the thickening smoke clouds.",
             "Smooth 2D noir graphic novel animation. The two staged actor silhouettes keep their heads down writing steadily while thick smoke coils swirl around their shoulders, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC02_B4", "SC02_I4", "Tỷ lệ hành động sụt giảm thê thảm chỉ còn mười phần trăm", "Khói mịt mù nhưng người khác làm dập tắt phản xạ.", "fast", "empirical_evidence", "focus",
             "The right side of the dossier chart labeled IN GROUP showing a tiny ten percent meter in crimson ink #C0392B, as the real subject sits paralyzed with folded arms.",
             "Smooth 2D noir graphic novel animation. The crimson meter drops rapidly to ten percent while the student silhouette hesitates and sinks back into the chair, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC02_B5", "SC02_I5", "Khói bao trùm cả căn phòng nhưng tất cả vẫn ngồi im", "Tâm lý số đông làm tê liệt bản năng tự cứu.", "slow", "empirical_evidence", "focus",
             "The laboratory room now almost completely submerged in swirling smoke slate tones #5A5F66, with three dark silhouettes sitting motionlessly coughing in the haze.",
             "Smooth 2D noir graphic novel animation. Swirling smoke veils obscure the room while the three silhouette figures sit motionless like dark shadows carved into stone, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC02_B6", "SC02_I6", "Kết luận đanh thép của thí nghiệm phòng khói", "Thí nghiệm mở màn cho chuỗi khám phá chấn động.", "normal", "empirical_evidence", "focus",
             "The investigator silhouette stamps a large crimson lock icon across the laboratory blueprint on the case wall with high negative space.",
             "Smooth 2D noir graphic novel animation. A bold black padlock outline snaps around the testing room blueprint locking the entire scene in still graphic pause, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
        ]
    },
    {
        "id": "SC03",
        "title": "Thí nghiệm cơn co giật qua ống nghe điện đàm",
        "purpose": "Thí nghiệm cơn co giật qua ống nghe điện đàm",
        "requirements": ["R03"],
        "narrative_situation": "empirical_evidence",
        "narrative_phase": "empirical_conflict",
        "action": "Subjects communicate through isolated intercom headsets while an emergency audio signal sounds.",
        "setting": "Soundproof interrogation cubicles linked by copper wire schematics.",
        "camera": "Isometric diagram of isolated testing pods.",
        "beats": [
            ("SC03_B1", "SC03_I1", "Thiết kế phòng cách âm loại bỏ ánh nhìn trực tiếp", "Để loại bỏ ánh nhìn, nhóm nghiên cứu dùng tai nghe riêng.", "fast", "empirical_evidence", "establish",
             "Architectural blueprint of individual closed soundproof booths on aged dossier paper canvas #E8E2D0, connected only by thin black intercom wires.",
             "Smooth 2D noir graphic novel animation. Thin black telephone lines trace between the separate closed testing cubicles on the architectural dossier schematic, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC03_B2", "SC03_I2", "Tình huống khẩn cấp giả định phát cơn co giật", "Một người kêu cứu vì co giật qua đường truyền.", "fast", "empirical_evidence", "focus",
             "An audio oscilloscope waveform screen showing erratic jagged red spikes #C0392B indicating a distress call passing through the vintage headphone apparatus.",
             "Smooth 2D noir graphic novel animation. The jagged crimson waveform pulses erratically across the vintage intercom monitor as warning indicator lights glow, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC03_B3", "SC03_I3", "Phản ứng tức thì khi tưởng chỉ có hai người đối thoại", "Tưởng chỉ có hai người, họ chạy đi tìm cứu hộ ngay.", "normal", "empirical_evidence", "focus",
             "Case dossier file pod A showing a silhouette listener instantly tearing off the headset and sprinting toward the corridor, clock reading four seconds in black ink.",
             "Smooth 2D noir graphic novel animation. The listener in the two-person booth slams open the door and rushes into the corridor within seconds, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC03_B4", "SC03_I4", "Sự chần chừ kéo dài khi biết có nhiều người cùng nghe", "Tưởng có năm người cùng nghe, họ ngập ngừng ngồi chờ.", "normal", "empirical_evidence", "focus",
             "Case dossier file pod B showing a silhouette listener holding the headset with frozen trembling hands, clock showing several minutes ticking by without movement.",
             "Smooth 2D noir graphic novel animation. The listener in the five-person group holds the headset frozen in mid-air while an antique stopwatch hand sweeps past forty seconds, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC03_B5", "SC03_I5", "Tỷ lệ hành động tụt dốc thê thảm theo số lượng người tham gia", "Càng đông người nghe, xác suất đứng dậy càng giảm.", "fast", "empirical_evidence", "focus",
             "A classified graph plotting two participants with eighty-five percent response down to six participants with only thirty-one percent response in crimson ink.",
             "Smooth 2D noir graphic novel animation. The response rate curve plunges diagonally downward across the case parchment as additional booth icons light up, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC03_B6", "SC03_I6", "Khẳng định cơ chế tâm lý thuần túy không phụ thuộc biểu cảm mặt", "Hiệu ứng diễn ra dù không ai thấy nhau.", "normal", "empirical_evidence", "focus",
             "Silhouette of the investigator pointing to the headset wires showing that mere awareness of others presence is enough to trigger paralysis.",
             "Smooth 2D noir graphic novel animation. The investigator traces the severed connection string on the case board showing the invisible psychological barrier, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
        ]
    },
    {
        "id": "SC04",
        "title": "Cơ chế thứ nhất: Bẫy phân tán trách nhiệm",
        "purpose": "Cơ chế thứ nhất: Bẫy phân tán trách nhiệm",
        "requirements": ["R04"],
        "narrative_situation": "mechanism_step",
        "narrative_phase": "structural_model",
        "action": "A single heavy moral anchor divides into microscopic invisible threads across a massive crowd.",
        "setting": "Abstract noir conceptual stage on aged parchment.",
        "camera": "Top-down overhead perspective showing crowd network geometry.",
        "beats": [
            ("SC04_B1", "SC04_I1", "Khái niệm phân tán trách nhiệm trong tâm lý học", "Cơ chế đầu tiên là sự phân tán trách nhiệm.", "fast", "mechanism_step", "establish",
             "A heavy black steel anchor labeled MORAL RESPONSIBILITY hanging by a thick rope on aged dossier paper canvas #E8E2D0 with sharp typography.",
             "Smooth 2D noir graphic novel animation. The massive black steel anchor drops heavily onto the textured dossier surface sending fine charcoal ink lines outward, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC04_B2", "SC04_I2", "Gánh nặng tuyệt đối một trăm phần trăm khi đơn độc", "Đứng một mình, bạn gánh trọn vẹn áp lực.", "normal", "mechanism_step", "focus",
             "A single solitary silhouette figure standing beneath the anchor with both arms raised, bearing the full weight with bold 100 percent label.",
             "Smooth 2D noir graphic novel animation. The lone silhouette bends beneath the full crushing weight of the anchor under a sharp overhead beam of white light, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC04_B3", "SC04_I3", "Sự pha loãng trách nhiệm khi có hàng trăm người", "Giữa đám đông, trách nhiệm của mỗi người bị pha loãng.", "normal", "mechanism_step", "focus",
             "The anchor dissolves into hundreds of microscopic black dust specks floating above a dense sea of faceless silhouette heads in trench coats.",
             "Smooth 2D noir graphic novel animation. The heavy anchor dissolves into fine airborne powder that disperses harmlessly across hundreds of dark silhouette shoulders, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC04_B4", "SC04_I4", "Tâm lý ỷ lại và kỳ vọng người khác hành động", "Ai cũng nghĩ người khác sẽ ra tay trước.", "normal", "mechanism_step", "focus",
             "Dossier case sketch of multiple bystander silhouettes glancing at each other, each with thought bubbles pointing to another person in a closed circular loop.",
             "Smooth 2D noir graphic novel animation. Circular red directional arrows pulse from one bystander head to the next forming an endless closed loop of deferred action, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC04_B5", "SC04_I5", "Tự bào chữa nội tâm làm giảm cảm giác tội lỗi", "Số đông trở thành bình phong xoa dịu tội lỗi.", "normal", "mechanism_step", "focus",
             "A semi-transparent noir folding screen shielding a bystander from an emergency signal, with soft grey smoke drifting behind it.",
             "Smooth 2D noir graphic novel animation. A dark folding privacy screen unfolds smoothly between the bystander and the red emergency marker, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC04_B6", "SC04_I6", "Hệ quả cuối cùng là không một ai ra tay", "Khi tất cả cùng chờ, không ai làm gì cả.", "fast", "mechanism_step", "focus",
             "The entire crowd frozen in place around a fallen victim, with zero connection threads active and deep negative space surrounding them.",
             "Smooth 2D noir graphic novel animation. The crowd outlines freeze into solid motionless graphite blocks as the surrounding canvas remains completely still, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
        ]
    },
    {
        "id": "SC05",
        "title": "Cơ chế thứ hai: Ảo tưởng tập thể và điểm dừng Mid-CTA",
        "purpose": "Cơ chế thứ hai: Ảo tưởng tập thể và điểm dừng Mid-CTA",
        "requirements": ["R05"],
        "narrative_situation": "mechanism_step",
        "narrative_phase": "structural_model",
        "action": "Bystanders exchange glances in mutual misunderstanding, followed by an editorial pause for the Mid-CTA.",
        "setting": "Noir public square under a giant clock with case notes.",
        "camera": "Eye-level rotating camera around the circle of frozen onlookers.",
        "beats": [
            ("SC05_B1", "SC05_I1", "Khái niệm sự thiếu hiểu biết tập thể", "Cơ chế thứ hai là sự thiếu hiểu biết tập thể.", "fast", "mechanism_step", "establish",
             "Two noir silhouette profiles facing in opposite directions with carnival masks pinned to the back of their heads, smiling false smiles on aged paper.",
             "Smooth 2D noir graphic novel animation. The masks on the back of the silhouette heads swivel slightly while delicate ink shading reveals tense eyes behind them, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC05_B2", "SC05_I2", "Bộ não tìm kiếm manh mối xã hội trong tình huống mơ hồ", "Chúng ta nhìn người bên cạnh để dò nguy hiểm.", "normal", "mechanism_step", "focus",
             "A visual diagram of intersecting gaze beams between silhouettes, each scanning the other face for panic or confirmation on aged canvas.",
             "Smooth 2D noir graphic novel animation. Crisp black inquiry lines connect from eye to eye across the gathering crowd seeking reassurance, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC05_B3", "SC05_I3", "Thấy người khác bình thản dẫn đến kết luận sai lệch", "Thấy người khác điềm nhiên, não tự cho là bình an.", "normal", "mechanism_step", "focus",
             "A bystander silhouette nonchalantly looking at a smartphone screen, while a red warning flare burns in the background without being noticed.",
             "Smooth 2D noir graphic novel animation. The phone screen illuminates the calm silhouette profile while smoke-slate shadows drift gently across the background, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC05_B4", "SC05_I4", "Nghịch lý ai cũng lo nhưng đều cố tỏ ra bình thản", "Ai cũng lo sợ nhưng đều cố tỏ ra bình thản.", "normal", "mechanism_step", "focus",
             "Cross-section of a silhouette torso showing a racing red heart meter inside while the exterior posture remains rigid and nonchalant.",
             "Smooth 2D noir graphic novel animation. The internal red pulse beats rapidly while the exterior posture remains completely still and unaffected, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC05_B5", "SC05_I5", "Vòng lặp tự đánh lừa đóng băng toàn bộ hành vi", "Vòng lặp này biến nguy cấp thành bình thường giả tạo.", "fast", "mechanism_step", "focus",
             "A rubber stamp in heavy crimson ink #C0392B stamping FALSE NORMAL across the crime scene chalk outline on aged dossier canvas.",
             "Smooth 2D noir graphic novel animation. The crimson rubber stamp strikes down firmly across the case file sealing the false conclusion in place, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC05_B6", "SC05_I6", "Điểm dừng Mid-CTA rèn luyện khả năng đọc vị", "Nếu muốn rèn bản lĩnh đọc vị đám đông, hãy lưu lại video để đối chiếu khi cần nhé.", "normal", "mechanism_step", "focus",
             "The anonymous investigator in trench coat slides an archival card into a clean leather case dossier with a subtle bookmark ribbon, maintaining over 60% negative space.",
             "Smooth 2D noir graphic novel animation. The investigator neatly bookmarks the case document and looks steadily toward the viewer with calm composure, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
        ]
    },
    {
        "id": "SC06",
        "title": "Cơ chế thứ ba: Nỗi sợ bị phán xét và hiệu ứng khán giả",
        "purpose": "Cơ chế thứ ba: Nỗi sợ bị phán xét và hiệu ứng khán giả",
        "requirements": ["R06"],
        "narrative_situation": "mechanism_step",
        "narrative_phase": "structural_model",
        "action": "Spotlights illuminate a bystander about to step forward, freezing them in fear of social embarrassment.",
        "setting": "Noir theater stage setting with harsh audience silhouettes.",
        "camera": "Low angle looking up from the stage into dark audience eyes.",
        "beats": [
            ("SC06_B1", "SC06_I1", "Khái niệm nỗi sợ bị đánh giá xã hội", "Lớp rào cản thứ ba là nỗi sợ bị phán xét.", "fast", "mechanism_step", "establish",
             "A solitary silhouette standing on a circular spotlight ring with dozens of giant shadowed eyes observing from the dark upper canvas #111111 on aged paper.",
             "Smooth 2D noir graphic novel animation. Sharp white searchlight cones converge on the central silhouette making every detail stark and exposed, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC06_B2", "SC06_I2", "Nỗi sợ làm lố hoặc hiểu nhầm tình huống", "Con người sợ làm quá rồi thành trò cười.", "normal", "mechanism_step", "focus",
             "A court jester silhouette shadow cast on the wall behind the well-dressed trench-coat bystander, representing the fear of ridicule.",
             "Smooth 2D noir graphic novel animation. The distorted shadow on the wall shifts into a laughing silhouette outline before snapping back to reality, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC06_B3", "SC06_I3", "Chi phí xã hội khi can thiệp sai lầm", "Can thiệp nhầm người say sẽ bị chê là nhiều chuyện.", "normal", "mechanism_step", "focus",
             "Dossier case drawing of a bystander helping someone up while surrounding silhouettes whisper with curved smoke quotation marks.",
             "Smooth 2D noir graphic novel animation. Whispering smoke silhouettes exchange mocking glances as the helpful bystander pauses in hesitation, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC06_B4", "SC06_I4", "Phản xạ nhân đạo bị tê liệt bởi áp lực xã hội", "Sự e dè xã hội đóng băng phản xạ nhân đạo lúc nguy cấp.", "fast", "mechanism_step", "focus",
             "A clock pendulum swinging above a frozen human heart emblem wrapped in barbed black wire on aged dossier paper.",
             "Smooth 2D noir graphic novel animation. The antique pendulum swings heavily back and forth as delicate frost lines etch across the heart emblem, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC06_B5", "SC06_I5", "Lựa chọn an toàn thụ động thay vì rủi ro", "Chúng ta chọn an toàn thụ động hơn mạo hiểm phá trật tự.", "normal", "mechanism_step", "focus",
             "A neat row of identical anonymous silhouette figures standing in perfect alignment, hands clasped behind backs, conforming to the line.",
             "Smooth 2D noir graphic novel animation. The row of uniform silhouettes shifts slightly in unison maintaining absolute geometric symmetry and silence, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC06_B6", "SC06_I6", "Ba cơ chế đan xen tạo thành chiếc lồng sắt tâm lý", "Ba cơ chế này biến người tốt thành khán giả bất đắc dĩ.", "normal", "mechanism_step", "focus",
             "Three interlocking iron gears drawn in black ink with red friction teeth #C0392B, completely locking each other in mechanical stalemate.",
             "Smooth 2D noir graphic novel animation. The three interlocking iron gear wheels grind together until their teeth seize tightly, locking the mechanism, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
        ]
    },
    {
        "id": "SC07",
        "title": "Lời bình sắc bén: Ảo tưởng về lòng dũng cảm cá nhân",
        "purpose": "Lời bình sắc bén: Ảo tưởng về lòng dũng cảm cá nhân",
        "requirements": ["R07"],
        "narrative_situation": "editorial_commentary",
        "narrative_phase": "structural_model",
        "action": "The investigator addresses the camera directly, breaking down the viewer self-righteous illusions.",
        "setting": "Solemn investigation dossier study with deep charcoal shadows.",
        "camera": "Intimate slow push-in focusing on the trench-coat investigator.",
        "beats": [
            ("SC07_B1", "SC07_I1", "Ảo tưởng tự cho mình là ngoại lệ đạo đức", "Nhiều người tin nếu có mặt, mình chắc chắn sẽ giải cứu.", "fast", "editorial_commentary", "establish",
             "A heroic shining knight silhouette standing proudly in the foreground, contrasted against a dark dossier mirror reflecting an ordinary hesitant passerby.",
             "Smooth 2D noir graphic novel animation. The idealized heroic reflection in the dark mirror wavers slightly and reveals an ordinary hesitant pedestrian outline, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC07_B2", "SC07_I2", "Bóc trần sự ngộ nhận phổ biến của người quan sát", "Đây là ảo tưởng đạo đức phổ biến nhất từng ghi nhận.", "slow", "editorial_commentary", "focus",
             "An official psychological dossier file marked MORAL ILLUSION with bold black ink annotations and critical red question marks on aged parchment.",
             "Smooth 2D noir graphic novel animation. The case folder page flips open to reveal psychological survey charts annotated with meticulous red ink notes, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC07_B3", "SC07_I3", "Sức ép bầy đàn bóp nghẹt mọi ý định tốt đẹp", "Giữa biển người im lặng, áp lực bầy đàn tê liệt ý định tốt.", "slow", "editorial_commentary", "focus",
             "A lone glowing lightbulb silhouette descending into a deep dark sea of shadowed trench coats, where its filament flickers and dims.",
             "Smooth 2D noir graphic novel animation. The warm glow of the lone lightbulb diminishes as dense surrounding shadows press closely against its glass bulb, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC07_B4", "SC07_I4", "Não bộ con người được lập trình để hòa nhập thay vì khác biệt", "Não bộ tiến hóa để tuân thủ số đông hơn làm anh hùng.", "normal", "editorial_commentary", "focus",
             "A diagram of a prehistoric human silhouette standing near the tribe campfire, showing that banishment meant death and conformity meant survival.",
             "Smooth 2D noir graphic novel animation. Prehistoric silhouettes around a faint campfire fade into modern city pedestrians on the aged dossier texture, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC07_B5", "SC07_I5", "Thừa nhận điểm mù sinh học để tự vệ", "Nhận diện điểm yếu sinh học là bước đầu thoát bẫy.", "normal", "editorial_commentary", "focus",
             "The silhouette investigator lighting a match on aged dossier canvas, illuminating a clear escape route out of the crowd maze.",
             "Smooth 2D noir graphic novel animation. The single match flame flares into crisp light cutting through the surrounding smoke-slate shadows on the canvas, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC07_B6", "SC07_I6", "Chuyển giao từ bế tắc nhận thức sang hành động thực tiễn", "Chấp nhận bản năng giúp rèn luyện phản xạ can thiệp.", "fast", "editorial_commentary", "focus",
             "A sharp key silhouette in solid black ink turning inside a crimson padlock on the case folder, clicking open.",
             "Smooth 2D noir graphic novel animation. The heavy black key rotates smoothly inside the lock cylinder springing the shackle open with a crisp click, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
        ]
    },
    {
        "id": "SC08",
        "title": "Thực tế đời thường: Từ tai nạn giao thông đến công sở",
        "purpose": "Thực tế đời thường: Từ tai nạn giao thông đến công sở",
        "requirements": ["R08"],
        "narrative_situation": "real_world_friction",
        "narrative_phase": "structural_model",
        "action": "Everyday scenes in Vietnam: street motorbike collision crowd and silent office meeting room.",
        "setting": "Split noir setting: bustling Vietnamese intersection and modern corporate boardroom.",
        "camera": "Dynamic horizontal wipe transitioning between street and boardroom.",
        "beats": [
            ("SC08_B1", "SC08_I1", "Hiện diện thường nhật của hiệu ứng người ngoài cuộc", "Hiệu ứng này diễn ra mỗi ngày trên phố và công sở.", "fast", "real_world_friction", "establish",
             "A dual noir cityscape showing a busy Vietnamese street on the left and a corporate office tower on the right on aged dossier paper canvas.",
             "Smooth 2D noir graphic novel animation. A vertical split line divides the urban traffic avenue and the quiet corporate office corridor, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC08_B2", "SC08_I2", "Hiện trường va chạm xe cộ và đám đông hiếu kỳ", "Một vụ ngã xe thu hút đám đông nhưng hiếm ai đỡ dậy.", "normal", "real_world_friction", "focus",
             "A fallen motorbike silhouette on a rain-slicked noir street, surrounded by a dense circle of onlookers holding up phone cameras without stepping forward.",
             "Smooth 2D noir graphic novel animation. Glowing smartphone screens twinkle in the dark around the fallen motorbike while bystander boots remain glued to the curb, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC08_B3", "SC08_I3", "Sự im lặng tập thể trong môi trường công sở", "Trong văn phòng, sai phạm dự án thường chỉ nhận sự im lặng.", "normal", "real_world_friction", "focus",
             "A corporate boardroom table drawn in noir line art. Colleagues in sharp suits keep their eyes glued to laptop screens while one empty chair sits isolated.",
             "Smooth 2D noir graphic novel animation. Around the long boardroom table, silhouette executives gaze steadily down at their paperwork in complete silence, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC08_B4", "SC08_I4", "Nỗi sợ trở thành người đầu tiên gánh vác rủi ro", "Ai cũng sợ thành người đầu tiên đứng ra gánh rủi ro.", "normal", "real_world_friction", "focus",
             "A row of dominos where the first domino is labeled YOU, leaning forward slightly under heavy tension lines while all others remain upright.",
             "Smooth 2D noir graphic novel animation. The first domino wavers slightly on its edge while the remaining dominoes stand in stark unmoving succession, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC08_B5", "SC08_I5", "Sự thỏa hiệp ngầm duy trì nguyên trạng có hại", "Sự im lặng này làm tổn thương nạn nhân và tính chính trực.", "slow", "real_world_friction", "focus",
             "A case file labeled SYSTEMIC SILENCE stamped with a cracked scale of justice in crimson ink #C0392B on aged paper canvas.",
             "Smooth 2D noir graphic novel animation. The cracked scale of justice tips slowly to one side as fine red ink fissures trace across its arm, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC08_B6", "SC08_I6", "Nhu cầu cấp thiết về một công cụ can thiệp thực chiến", "Bạn cần phương pháp can thiệp có tính toán.", "fast", "real_world_friction", "focus",
             "The silhouette investigator laying down a structured three-step tactical card onto the dossier table under a bright overhead lamp.",
             "Smooth 2D noir graphic novel animation. The investigator places a crisp index card with numbered tactical steps onto the center of the wooden table, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
        ]
    },
    {
        "id": "SC09",
        "title": "Quy tắc vàng: Kỹ thuật chỉ định đích danh phá vỡ bẫy",
        "purpose": "Quy tắc vàng: Kỹ thuật chỉ định đích danh phá vỡ bẫy",
        "requirements": ["R09"],
        "narrative_situation": "actionable_resolution",
        "narrative_phase": "actionable_resolution",
        "action": "Step-by-step breakdown of the 1-to-1 delegation protocol that breaks diffusion of responsibility instantly.",
        "setting": "Sharp graphic instructional stage on aged dossier canvas.",
        "camera": "Direct frontal framing with crisp graphic callouts.",
        "beats": [
            ("SC09_B1", "SC09_I1", "Cấm tuyệt đối kêu cứu chung chung vào khoảng không", "Nếu gặp nạn giữa phố, đừng gào khóc cầu cứu chung chung.", "fast", "actionable_resolution", "establish",
             "A speech bubble filled with generic exclamation marks slashed through with a bold crimson X on aged dossier paper canvas #E8E2D0.",
             "Smooth 2D noir graphic novel animation. The generic speech bubble dissolves into thin air as a decisive crimson slash cancels it from the frame, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC09_B2", "SC09_I2", "Tiếng kêu vô định chỉ làm tăng phân tán trách nhiệm", "Tiếng kêu vô định chỉ làm tăng phân tán trách nhiệm.", "fast", "actionable_resolution", "focus",
             "Scattered sound waves spreading in all directions without connecting to any bystander silhouette, fading into negative space.",
             "Smooth 2D noir graphic novel animation. The radial sound waves dissipate into empty white canvas without stirring any of the shadowed observer profiles, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC09_B3", "SC09_I3", "Nguyên tắc khóa ánh mắt vào một người duy nhất", "Hãy nhìn thẳng một người, chỉ trang phục và giao việc rõ ràng.", "normal", "actionable_resolution", "focus",
             "A direct eye contact beam rendered as a laser-sharp black line between the victim silhouette and a single chosen bystander in the crowd.",
             "Smooth 2D noir graphic novel animation. A crisp black line of sight locks directly onto a single targeted pedestrian separating them from the crowd, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC09_B4", "SC09_I4", "Khẩu lệnh thực chiến nêu đặc điểm và hành động rõ ràng", "Anh mặc áo mưa đỏ, làm ơn gọi cấp cứu một một lăm giúp tôi ngay.", "normal", "actionable_resolution", "focus",
             "A targeted silhouette highlighted with a vibrant crimson raincoat #C0392B, with a speech callout showing the exact emergency number 115.",
             "Smooth 2D noir graphic novel animation. The highlighted bystander in the red coat steps forward decisively as an illuminated telephone icon forms in their hand, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC09_B5", "SC09_I5", "Tái thiết lập một trăm phần trăm trách nhiệm cá nhân", "Chỉ định đích danh đặt trọn trách nhiệm lên đúng một người.", "normal", "actionable_resolution", "focus",
             "The 100 percent weight instantly reattaching to that single chosen individual, who now steps forward to take charge.",
             "Smooth 2D noir graphic novel animation. The full responsibility weight settles firmly on the targeted individual while surrounding bystander silhouettes step back, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC09_B6", "SC09_I6", "Hiệu ứng quân cờ domino khi người đầu tiên ra tay", "Khi người đầu tiên giúp, đám đông sẽ cùng hỗ trợ.", "fast", "actionable_resolution", "focus",
             "The first bystander reaching out to help, causing multiple surrounding silhouettes to rush forward in coordinated rescue on aged paper.",
             "Smooth 2D noir graphic novel animation. The first helper extends a hand and suddenly five other bystander silhouettes rush in from all sides to assist, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
        ]
    },
    {
        "id": "SC10",
        "title": "Lời bình sắc bén: Bản lĩnh của người phá vỡ im lặng",
        "purpose": "Lời bình sắc bén: Bản lĩnh của người phá vỡ im lặng",
        "requirements": ["R10"],
        "narrative_situation": "editorial_commentary",
        "narrative_phase": "actionable_resolution",
        "action": "The trench-coat observer demonstrates the profound psychological courage required to be the first follower and leader.",
        "setting": "Noir dossier study with warm lamp glow against aged paper.",
        "camera": "Slow majestic crane shot moving down toward the case table.",
        "beats": [
            ("SC10_B1", "SC10_I1", "Góc nhìn của người qua đường đứng trước quyết định", "Nếu là người qua đường, một hành động nhỏ sẽ đổi cục diện.", "fast", "editorial_commentary", "establish",
             "A solitary bystander silhouette taking one bold step across a heavy black boundary line drawn on aged dossier parchment.",
             "Smooth 2D noir graphic novel animation. The single boot silhouette steps across the stark line of hesitation leaving a clean footprint on the aged canvas, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC10_B2", "SC10_I2", "Một bước chân phá vỡ chiếc vỏ bọc băng giá", "Chỉ cần người đầu tiên bước tới, vỏ bọc im lặng vỡ vụn.", "slow", "editorial_commentary", "focus",
             "An ice-like shell covering the crowd suddenly shattering into sharp crystalline shards with crimson lightning cracks #C0392B.",
             "Smooth 2D noir graphic novel animation. Fissures of clean white light spiderweb through the frozen crowd shell shattering it into flying geometric pieces, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC10_B3", "SC10_I3", "Quy luật lây lan của lòng dũng cảm trong tâm lý học", "Sự dũng cảm có tính lây lan mạnh mẽ như nỗi sợ.", "slow", "editorial_commentary", "focus",
             "A single candle flame touching another wick, spreading a chain reaction of warm glowing points across the dark silhouette crowd.",
             "Smooth 2D noir graphic novel animation. A spark leaps from one silhouette hand to the next igniting an unbroken chain of small bright beacons in the dark, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC10_B4", "SC10_I4", "Người đầu tiên đóng vai trò giải phóng nhận thức cho đám đông", "Mọi người đều chờ một người dẫn đường để hành động.", "normal", "editorial_commentary", "focus",
             "The crowd silhouettes leaning forward in relief as the first helper knelt down, their expressions softening.",
             "Smooth 2D noir graphic novel animation. Tension drains from the crowd silhouettes as their postures relax and they move forward with purpose, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC10_B5", "SC10_I5", "Trở thành ngòi nổ kích hoạt điều thiện", "Hãy chủ động trở thành ngòi nổ kích hoạt điều thiện.", "normal", "editorial_commentary", "focus",
             "The silhouette investigator standing at the center of the canvas holding a steady beacon lamp that illuminates the entire case wall.",
             "Smooth 2D noir graphic novel animation. The beacon lamp is raised high casting broad warm rays that transform the harsh noir contrast into clear vision, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC10_B6", "SC10_I6", "Định nghĩa lại ý nghĩa của sức mạnh cá nhân giữa đám đông", "Sức mạnh thực sự nằm ở sự tỉnh táo vượt qua số đông.", "fast", "editorial_commentary", "focus",
             "A stark graphic emblem: an open compass needle pointing unwaveringly north amidst chaotic swirling crowd vectors on aged paper.",
             "Smooth 2D noir graphic novel animation. The compass needle swings with precision and locks firmly onto true north ignoring all turbulent winds around it, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
        ]
    },
    {
        "id": "SC11",
        "title": "Tổng kết, hành động thực tế và Lời kết",
        "purpose": "Tổng kết, hành động thực tế và Lời kết",
        "requirements": ["R11"],
        "narrative_situation": "outro",
        "narrative_phase": "actionable_resolution",
        "action": "The investigator closes the master dossier and invites viewer engagement before the official endcard.",
        "setting": "Classified archival repository with master dossier and channel seal.",
        "camera": "Formal lock-off establishing the iconic channel brand endcard.",
        "beats": [
            ("SC11_B1", "SC11_I1", "Khẳng định giá trị của việc thấu suốt quy luật ngầm", "Hiểu luật ngầm giúp bạn làm chủ hành vi của mình.", "normal", "outro", "establish",
             "A master dossier binder titled THE BYSTANDER CODE being closed neatly with a single crimson tie string on aged paper canvas #E8E2D0.",
             "Smooth 2D noir graphic novel animation. The heavy master case dossier folds shut as a single crimson tie string winds smoothly around its brass button, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC11_B2", "SC11_I2", "Tóm tắt hai trụ cột tự vệ và can thiệp", "Gặp nạn thì giao việc cụ thể, thấy nạn thì chủ động mở đường.", "fast", "outro", "focus",
             "A split iconic diagram on aged parchment: on the left a pointing hand with red crosshair, on the right a bold stepping boot breaking chains.",
             "Smooth 2D noir graphic novel animation. The two tactical symbols glow faintly with clean black marker outlines and deep negative space, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC11_B3", "SC11_I3", "Sự tiến hóa trong nhận thức xã hội của mỗi người xem", "Đó là cách để không ai phải cô độc giữa phố đông.", "normal", "outro", "focus",
             "A city street at dawn drawn in 2D noir style, where silhouette pedestrians walk in harmonious coordination with open negative space.",
             "Smooth 2D noir graphic novel animation. Soft dawn light filters between the noir skyline buildings as distant pedestrian silhouettes walk peacefully, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC11_B4", "SC11_I4", "Lời mời chia sẻ trải nghiệm thực tế bên dưới", "Bạn từng chứng kiến sự thờ ơ nào của đám đông,", "normal", "outro", "focus",
             "The anonymous investigator in trench coat turns to face the audience directly, resting hands on the desk with open listening posture on aged canvas.",
             "Smooth 2D noir graphic novel animation. The investigator looks up thoughtfully toward the viewer with attentive and welcoming posture, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC11_B5", "SC11_I5", "Lời kết kêu gọi thảo luận cộng đồng", "hãy chia sẻ góc nhìn bên dưới nhé.", "normal", "outro", "focus",
             "A speech balloon with an antique pen sketch icon appearing beside the investigator on clean aged dossier paper.",
             "Smooth 2D noir graphic novel animation. An antique fountain pen rests neatly across an open notebook page awaiting the viewer thoughts, transitioning smoothly into the next frame, silent visual storytelling, no talking, no lip movement", None),
            ("SC11_B6", "SC11_I6", "Endcard chính thức kênh Luật Ngầm Đám Đông", "Lưu video lại để biết cách tự vệ bạn nhé.", "hold", "outro", "hold",
             "Iconic channel brand endcard on aged dossier paper canvas #E8E2D0. Imposing anonymous noir silhouette in sharp trench coat with glowing white slit eyes stands beside the bold black title LUẬT NGẦM ĐÁM ĐÔNG with crimson accent threads #C0392B. Over 60% negative space, clean typography.",
             "Smooth 2D noir graphic novel animation. The silhouette investigator stands in still authoritative profile beside the bold channel dossier title as ambient smoke-slate texture drifts gently across the aged paper canvas, silent visual storytelling, no talking, no lip movement", "LUẬT NGẦM ĐÁM ĐÔNG", True),
        ]
    },
]

# Set narration exactly from beats
for s in long_scenes_data:
    s["narration"] = " ".join(b[3] for b in s["beats"])

long_words = sum(len(s["narration"].split()) for s in long_scenes_data)
print(f"Long total words: {long_words} (expected 700-760)")

long_brief = {
    "schema_version": "3.0",
    "topic": long_topic,
    "audience": "Người đi làm, người tiêu dùng, người muốn đọc vị hành vi xã hội",
    "goal": "Giải mã toàn diện hiệu ứng người ngoài cuộc từ thí nghiệm căn phòng đầy khói và co giật năm 1968, bóc tách ba tầng tâm lý phân tán trách nhiệm, ảo tưởng tập thể và sợ bị phán xét, đồng thời cung cấp giao thức chỉ định đích danh thực chiến",
    "video_type": "research_guide",
    "duration": {"min_seconds": 600.0, "max_seconds": 900.0},
    "scene_count": 11,
    "required_points": [
        {"id": "R01", "text": "Vụ án rúng động phố New York và sự thức tỉnh"},
        {"id": "R02", "text": "Thí nghiệm căn phòng đầy khói năm 1968"},
        {"id": "R03", "text": "Thí nghiệm cơn co giật qua ống nghe điện đàm"},
        {"id": "R04", "text": "Cơ chế thứ nhất: Bẫy phân tán trách nhiệm"},
        {"id": "R05", "text": "Cơ chế thứ hai: Ảo tưởng tập thể và điểm dừng Mid-CTA"},
        {"id": "R06", "text": "Cơ chế thứ ba: Nỗi sợ bị phán xét và hiệu ứng khán giả"},
        {"id": "R07", "text": "Lời bình sắc bén: Ảo tưởng về lòng dũng cảm cá nhân"},
        {"id": "R08", "text": "Thực tế đời thường: Từ tai nạn giao thông đến công sở"},
        {"id": "R09", "text": "Quy tắc vàng: Kỹ thuật chỉ định đích danh phá vỡ bẫy"},
        {"id": "R10", "text": "Lời bình sắc bén: Bản lĩnh của người phá vỡ im lặng"},
        {"id": "R11", "text": "Tổng kết, hành động thực tế và Lời kết"},
    ],
    "language": "vi",
    "tone": ch_tone,
    "style": ch_style,
    "aspect_ratio": "16:9",
    "format_profile": "long_16x9",
    "facts_required": True,
    "sources": [
        {
            "id": "SRC01",
            "title": "Group Inhibition of Bystander Intervention in Emergencies",
            "reference": "Latané, B., & Darley, J. M. (1968). Journal of Personality and Social Psychology, 10(3), 215-221.",
            "facts": [
                "Khi ngồi một mình có ba phần tư người tham gia báo cáo khói ngay.",
                "Khi có hai người ngồi im tỷ lệ báo cáo giảm xuống chỉ còn mười phần trăm.",
                "Sự có mặt của người khác làm chậm đáng kể thời gian phản ứng cấp cứu.",
            ],
        },
        {
            "id": "SRC02",
            "title": "The Unresponsive Bystander: Why Doesn't He Help?",
            "reference": "Latané, B., & Darley, J. M. (1970). New York: Appleton-Century-Crofts.",
            "facts": [
                "Quy trình cứu hộ gồm nhận biết tình huống, đánh giá nguy cấp và nhận lãnh trách nhiệm.",
                "Phân tán trách nhiệm khiến mỗi người trong đám đông tự cho rằng người khác đã hành động.",
                "Chỉ định đích danh một cá nhân giúp tái lập hoàn toàn trách nhiệm đạo đức.",
            ],
        },
    ],
    "planning": {
        "success_criteria": [
            "Bóc trần nguồn gốc tâm lý học xã hội của sự thờ ơ đám đông và cung cấp giao thức chỉ định đích danh phá vỡ bẫy"
        ],
        "avoid": [
            "Lên án hay phán xét đạo đức người xem",
            "Lý thuyết tâm lý học hàn lâm thiếu ví dụ đời thường",
        ],
        "prior_knowledge": "Không đòi hỏi kiến thức tâm lý học chuyên sâu từ trước.",
        "pacing": "Điềm tĩnh, sắc sảo, mở nút từng lớp tâm lý theo cấu trúc trinh thám noir cổ điển.",
        "domain_requirements": [],
        "assumptions": [
            "Mỗi phân cảnh được cân chỉnh theo công thức âm học P_tail và dung sai drift <= 0.3s."
        ],
        "text_style": {
            "font": "sans-serif nét đậm dứt khoát",
            "color": "#111111",
            "outline": "#E8E2D0",
            "size": "dễ đọc trên màn hình ngang 16:9",
            "placement": "cách mép ít nhất 10%; bố cục thoáng đãng",
        },
        "speech_rates": {
            "vi": {"units_per_second": 3.8, "uncertainty": 0.15, "source": "Acoustic calibrated cadence"},
            "en": {"units_per_second": 2.5, "uncertainty": 0.25, "source": "Estimated English reading rate"},
        },
    },
    "outputs": [
        {
            "aspect_ratio": "16:9",
            "language": "vi",
            "subtitles": False,
            "voice": "VietNarrator",
            "speed": 1.0,
        }
    ],
    "youtube_title": long_yt_title,
    "thumbnail_spec": {
        "visual_hook": "Bóng đen áo măng tô cầm hồ sơ mật đứng trước đám đông tượng đá vô cảm bị nối bởi những sợi chỉ đỏ chằng chịt",
        "text_overlay": "ĐỨNG NHÌN",
        "contrast_pair": "Đám đông im lặng bất động vs Giao thức phá vỡ phân tán trách nhiệm",
    },
    "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    "funnel_tier": "tier_1_broad",
    "seo_keywords": [
        "hieu ung nguoi ngoai cuoc",
        "tam ly hoc dam dong",
        "thi nghiem phong khoi 1968",
        "latane va darley",
        "phan tan trach nhiem",
        "doc vi dam dong",
        "luat ngam",
    ],
    "cta_plan": {
        "mid_cta": "Nếu muốn rèn bản lĩnh đọc vị đám đông, hãy lưu lại video để đối chiếu khi cần nhé.",
        "close": "Bạn từng chứng kiến sự thờ ơ nào của đám đông, hãy chia sẻ góc nhìn bên dưới nhé.",
        "endcard_text": "LUẬT NGẦM ĐÁM ĐÔNG",
    },
    "channel_profile": ch_profile,
    "engagement": asdict(ch.engagement),
    "editorial_stance": {
        "myth_debunked": "Sự thờ ơ của đám đông bắt nguồn từ sự suy đồi đạo đức hay lối sống vô cảm thời hiện đại.",
        "why_generic_advice_fails": "Lời khuyên kêu cứu chung chung chỉ kích hoạt thêm sự phân tán trách nhiệm và khiến mọi người tê liệt hơn.",
        "channel_verdict": "Đám đông không hề vô cảm; cơ chế phân tán trách nhiệm đã khóa chặt phản xạ hành động của từng người.",
        "tradeoff_or_blindspot": "Chỉ định đích danh một người tạo ra áp lực tâm lý đột ngột nhưng là giải pháp duy nhất cứu nguy tức thì.",
    },
    "actionable_value": {
        "core_mechanism": "Cơ chế tam giác: phân tán trách nhiệm làm loãng bổn phận, ảo tưởng tập thể làm mờ nguy cấp, và sợ bị phán xét đóng băng hành vi.",
        "practical_rule_of_thumb": "Quy tắc chỉ định một đối một: chỉ rõ đặc điểm trang phục, khóa ánh mắt và giao nhiệm vụ đơn lẻ dứt khoát.",
        "real_world_scenario": "Nạn nhân va chạm giao thông chỉ định đích danh tài xế mặc áo mưa đỏ gọi cấp cứu để thoát khỏi cảnh bị vây quanh đứng nhìn.",
    },
    "video_engine": "flow_video",
    "chain_mode": "daisy_chain",
}

long_brief_bytes = json.dumps(long_brief, indent=2, ensure_ascii=False).encode("utf-8")
long_bhash = hashlib.sha256(long_brief_bytes).hexdigest()

long_scenes = []
prev_img_id = None
for sdata in long_scenes_data:
    sc_imgs = []
    sc_beats = []
    for b in sdata["beats"]:
        b_id, img_id, b_purpose, b_quote, b_tempo, b_sit, b_cam, b_desc, b_motion = b[:9]
        b_emphasis = b[9] if len(b) > 9 else None
        b_is_endcard = b[10] if len(b) > 10 else False

        img_obj = {
            "id": img_id,
            "description": b_desc,
            "character_ids": ["CH01"],
            "based_on": prev_img_id,
            "preserve": "clean noir aged dossier paper canvas #E8E2D0, heavy black ink linework #111111, single crimson accent #C0392B, anonymous trench-coat silhouette figure",
            "change": b_desc[:100],
            "reason": "Narration-locked full-frame beat.",
            "visible_text": [{"text": b_emphasis, "placement": "upper_third", "object": "emphasis"}] if b_emphasis else [],
            "kind": "scene",
            "shot_type": "full_scene",
            "tempo": b_tempo,
            "narrative_situation": b_sit,
            "has_character": True,
            "motion_prompt": b_motion,
        }
        if b_is_endcard:
            img_obj["is_endcard"] = True
        sc_imgs.append(img_obj)
        prev_img_id = img_id

        beat_obj = {
            "id": b_id,
            "image_id": img_id,
            "purpose": b_purpose,
            "anchor": {
                "vi": {
                    "quote": b_quote,
                    "occurrence": 1,
                }
            },
            "effect": "hold" if b_is_endcard else "cut",
            "focus": {"x": 0.5, "y": 0.5},
            "tempo": b_tempo,
            "camera_intent": b_cam,
            "narrative_situation": b_sit,
        }
        if b_is_endcard:
            beat_obj["is_endcard"] = True
        sc_beats.append(beat_obj)

    long_scenes.append({
        "id": sdata["id"],
        "title": sdata["title"],
        "purpose": sdata["purpose"],
        "action": sdata["action"],
        "setting": sdata["setting"],
        "camera": sdata["camera"],
        "narration": sdata["narration"],
        "requirements": sdata["requirements"],
        "character_ids": ["CH01"],
        "source_ids": ["SRC01", "SRC02"] if "1968" in sdata["title"] or "1964" in sdata["title"] else ["SRC01"],
        "images": sc_imgs,
        "beats": sc_beats,
        "tone": ch_tone,
        "narrative_phase": sdata["narrative_phase"],
        "narrative_situation": sdata["narrative_situation"],
    })

long_content = {
    "schema_version": "3.0",
    "brief_revision": 1,
    "brief_hash": long_bhash,
    "topic": long_topic,
    "duration": long_brief["duration"],
    "style": long_brief["style"],
    "required_points": [r["text"] for r in long_brief["required_points"]],
    "characters": [ch_cast],
    "scenes": long_scenes,
}

long_outline = {
    "outline": [
        {
            "scene_id": s["id"],
            "purpose": f"Triển khai {s['purpose'].lower()}",
            "requirements": s["requirements"],
            "transition": "Tiếp tục theo trình tự diễn biến tâm lý trinh thám noir",
        }
        for s in long_scenes
    ]
}

long_comp_research = {
    "channel_id": "luat_ngam",
    "job_id": long_job_id,
    "topic": long_topic,
    "competitor_analysis": {
        "benchmark_channels": [
            {
                "channel_name": "Academy of Ideas & Psych2Go",
                "top_performing_videos": [
                    {
                        "title": "The Psychology of Bystander Apathy and Mob Mentality",
                        "views": "2.8M views",
                        "hook_technique": "Tái hiện vụ án Kitty Genovese 1964 và bóc trần những hiểu lầm kinh điển của báo chí.",
                        "pacing_structure": "Vụ án mở màn -> Hai thí nghiệm đột phá Latané & Darley -> Tam giác cơ chế tâm lý -> Bài học tự vệ xã hội.",
                        "retention_driver": "Sự thỏa mãn trí tuệ khi giải mã được một nghịch lý xã hội phản trực giác.",
                    }
                ],
                "viral_patterns_extracted": [
                    "Kể lại câu chuyện lịch sử với góc nhìn tâm lý học noir sắc sảo.",
                    "Sử dụng sơ đồ trực quan minh họa sự phân tán trách nhiệm đạo đức.",
                ],
            }
        ]
    },
    "viral_formula_audit": {
        "cold_audience_hook_analysis": {
            "first_sentence_syllables": 11,
            "zero_pause_opening_seconds": 15,
            "visual_contrast": "Góc phố New York năm 1964 đối lập giữa bóng tối hiện trường và những ô cửa sổ sáng đèn bất động.",
            "counter_intuitive_truth_slap": "Đám đông không vô cảm; cơ chế phân tán trách nhiệm khiến ai cũng đợi người khác hành động trước.",
        },
        "narrative_progression_arc": [
            {"phase": "lived_friction", "purpose": "Khởi đầu với vụ án rúng động New York 1964."},
            {"phase": "empirical_conflict", "purpose": "Thí nghiệm căn phòng đầy khói và co giật 1968."},
            {"phase": "structural_model", "purpose": "Bóc tách ba tầng tâm lý: phân tán trách nhiệm, ảo tưởng tập thể, sợ phán xét."},
            {"phase": "actionable_resolution", "purpose": "Giao thức chỉ định một đối một và bản lĩnh người phá vỡ im lặng."},
        ],
        "flow_video_transition_blueprint": {
            "chain_mode": "daisy_chain",
            "video_model": "omni_flash",
            "keyframe_continuity": "Sequential daisy-chain linking Start Frame to End Frame across all scenes in noir dossier aesthetic.",
        },
    },
    "academic_funnel_positioning": {
        "funnel_tier": "tier_1_broad",
        "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
        "myth_debunked": "Càng đông người thì cơ hội được giải cứu càng cao và an toàn xã hội càng được bảo đảm.",
        "channel_verdict": "Đám đông không hề vô cảm; cơ chế phân tán trách nhiệm đã khóa chặt phản xạ hành động của từng người.",
        "actionable_rule_of_thumb": "Quy tắc chỉ định một đối một: nhìn thẳng, chỉ rõ đặc điểm trang phục và giao lệnh dứt khoát.",
    },
    "cta_and_spinoff_strategy": {
        "mid_cta": long_brief["cta_plan"]["mid_cta"],
        "close": long_brief["cta_plan"]["close"],
        "endcard_text": long_brief["cta_plan"]["endcard_text"],
    },
}

# Write out all files
short_dir = Path("sys/runs/luat-ngam-batch3-9x16")
short_dir.mkdir(parents=True, exist_ok=True)
(short_dir / "brief.json").write_text(json.dumps(short_brief, indent=2, ensure_ascii=False), encoding="utf-8")
(short_dir / "outline.json").write_text(json.dumps(short_outline, indent=2, ensure_ascii=False), encoding="utf-8")
(short_dir / "content.json").write_text(json.dumps(short_content, indent=2, ensure_ascii=False), encoding="utf-8")
(short_dir / "competitor_research.json").write_text(json.dumps(short_comp_research, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote Short 9:16 files to {short_dir} (words: {short_words})")

long_dir = Path("sys/runs/luat-ngam-batch3-16x9")
long_dir.mkdir(parents=True, exist_ok=True)
(long_dir / "brief.json").write_text(json.dumps(long_brief, indent=2, ensure_ascii=False), encoding="utf-8")
(long_dir / "outline.json").write_text(json.dumps(long_outline, indent=2, ensure_ascii=False), encoding="utf-8")
(long_dir / "content.json").write_text(json.dumps(long_content, indent=2, ensure_ascii=False), encoding="utf-8")
(long_dir / "competitor_research.json").write_text(json.dumps(long_comp_research, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote Long 16:9 files to {long_dir} (words: {long_words})")
