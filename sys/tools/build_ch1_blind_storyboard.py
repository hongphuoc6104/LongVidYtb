#!/usr/bin/env python3
"""
Zero-Reference Blind Test Storyboard Builder for Chapter 1 (SC01-SC04, 64.25s, 34 Beats).
Constructs the visual storyboard strictly from:
1. Clean Vietnamese scene audio pauses (SC01.wav..SC04.wav via ffmpeg silencedetect)
2. Vietnamese script clauses (ch1_subtitles.json)
3. The 6 Visual Function Archetypes (VF1..VF6), Shot Framing Progression, and Anonymous Stick-Figure Cast.
"""

import json
import shutil
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent.parent.parent
BUNDLE_ROOT = PROJ_ROOT / "sys" / "exports" / "ancient_humans_bundle"
MANIFEST_DIR = BUNDLE_ROOT / "manifest"
TEMPLATES_DIR = BUNDLE_ROOT / "templates"
CLEAN_VOICE_DIR = BUNDLE_ROOT / "audio" / "clean_voice"
SCRATCH_CH1_AUDIO = PROJ_ROOT / "sys" / "scratch" / "reference_49_Ph2q6uIM" / "ch1_production" / "audio_v2"

STYLE_PREFIX = (
    "2D hand-drawn explainer illustration in bold black marker-pen outline with flat muted pastel "
    "and warm earthy fills on a clean uncluttered off-white paper background, 16:9 widescreen. "
    "Cast invariant: anonymous stick-figure character with a large round solid-white head, "
    "thick 4px closed black outline, expressive simple dot/line eyes and eyebrows, thin stick limbs, "
    "and a single stick torso. "
)

STYLE_SUFFIX = (
    " Do NOT render any text, letters, words, watermarks, logos, photorealistic faces, or 3D shading."
)

# 34 Beats derived strictly from SC01..SC04.wav acoustic pauses (silencedetect) & Vietnamese clauses
CH1_BLIND_BEATS = [
    # ==================== SC01 (0.00s - 14.52s, 8 Beats) ====================
    {
        "beat_index": 1,
        "scene_id": "SC01",
        "start_ch": 0.00,
        "end_ch": 0.79,
        "at_scene": 0.00,
        "duration": 0.79,
        "voiceover_vi": "Sáng nay,",
        "acoustic_trigger": "Mở cảnh 0.00s + Ngắt hơi dấu phẩy tại 0.53s–0.79s (dur=0.26s)",
        "visual_function": "VF1_ESTABLISHING",
        "shot_framing": "Wide establishing shot",
        "effect": "zoom_in",
        "draw_on": False,
        "line_boil": True,
        "based_on": None,
        "allowed_text": [],
        "action_description_vi": "Phòng ngủ hiện đại tờ mờ sáng màu xanh xám lạnh, nhân vật người que đang nằm ngủ trong chăn, chiếc đồng hồ báo thức đặt trên tủ đầu giường.",
        "core_prompt": (
            "Wide establishing shot of a dim modern bedroom at early dawn in cool slate-blue tones; "
            "an anonymous stick figure sleeping peacefully under a blanket in bed; "
            "a digital alarm clock sitting quietly on the nightstand."
        ),
    },
    {
        "beat_index": 2,
        "scene_id": "SC01",
        "start_ch": 0.79,
        "end_ch": 2.95,
        "at_scene": 0.79,
        "duration": 2.16,
        "voiceover_vi": "một cỗ máy đã gắt gỏng gọi bạn dậy.",
        "acoustic_trigger": "Đạo cụ 'cỗ máy' + Ngắt câu dài tại 2.34s–3.15s (dur=0.82s)",
        "visual_function": "VF2_ACTION_STATE",
        "shot_framing": "Medium close-up",
        "effect": "shake",
        "draw_on": False,
        "line_boil": True,
        "based_on": 1,
        "allowed_text": [],
        "action_description_vi": "Chiếc đồng hồ báo thức rung bần bật phát tia sét đỏ và sóng âm chói tai; nhân vật người que giật bắn mình mở choàng mắt mệt mỏi.",
        "core_prompt": (
            "Medium close-up in the same modern bedroom: the alarm clock on the nightstand violently vibrating "
            "in mid-air with jagged red soundwave lightning bolts; the stick figure jolting awake in bed "
            "with wide startled exhausted eyes and messy motion lines."
        ),
    },
    {
        "beat_index": 3,
        "scene_id": "SC01",
        "start_ch": 2.95,
        "end_ch": 4.50,
        "at_scene": 2.95,
        "duration": 1.55,
        "voiceover_vi": "Bạn tắt nó đi.",
        "acoustic_trigger": "Động từ hành động 'tắt nó đi' + Ngắt câu tại 3.89s–4.72s (dur=0.83s)",
        "visual_function": "VF2_ACTION_STATE",
        "shot_framing": "Close-up",
        "effect": "punch_in",
        "draw_on": False,
        "line_boil": True,
        "based_on": 2,
        "allowed_text": [],
        "action_description_vi": "Cận cảnh cánh tay người que thò ra khỏi chăn đập mạnh bàn tay xuống nút trên đỉnh đồng hồ báo thức làm nó im bặt.",
        "core_prompt": (
            "Close-up shot of the stick figure's hand reaching out from under the blanket and slamming down "
            "hard onto the top button of the alarm clock on the nightstand, with comic impact burst lines."
        ),
    },
    {
        "beat_index": 4,
        "scene_id": "SC01",
        "start_ch": 4.50,
        "end_ch": 6.85,
        "at_scene": 4.50,
        "duration": 2.35,
        "voiceover_vi": "Từ giây phút đó, ngày của bạn đã bị định sẵn:",
        "acoustic_trigger": "Ngắt phẩy 5.34s + Ngắt dấu hai chấm 6.69s–6.95s (dur=0.26s)",
        "visual_function": "VF5_METAPHOR_CAUSAL",
        "shot_framing": "Medium shot",
        "effect": "zoom_out",
        "draw_on": False,
        "line_boil": True,
        "based_on": None,
        "allowed_text": [],
        "action_description_vi": "Nhân vật ngồi rũ rượi bên mép giường; phía trên hiện bảng lịch trình kẻ ô dày đặc và sợi dây xích nối cổ tay nhân vật vào chiếc đồng hồ treo tường lớn.",
        "core_prompt": (
            "Medium shot of the exhausted stick figure sitting slumped on the edge of the bed with drooping eyes; "
            "a giant rigid grid calendar and a large wall clock floating above, with a hand-drawn iron chain "
            "linking the clock to the stick figure's wrist."
        ),
    },
    {
        "beat_index": 5,
        "scene_id": "SC01",
        "start_ch": 6.85,
        "end_ch": 8.35,
        "at_scene": 6.85,
        "duration": 1.50,
        "voiceover_vi": "bạn phải đi đâu, làm gì,",
        "acoustic_trigger": "Liệt kê hành động + Ngắt phẩy tại 7.56s và 8.16s–8.43s (dur=0.27s)",
        "visual_function": "VF2_ACTION_STATE",
        "shot_framing": "Two-panel split composition",
        "effect": "slide_left",
        "draw_on": False,
        "line_boil": True,
        "based_on": None,
        "allowed_text": [],
        "action_description_vi": "Chia 2 ô hành động: bên trái là nhân vật đeo cà vạt chạy hối hả theo mũi tên đỏ tới tòa nhà văn phòng; bên phải là nhân vật ngồi gõ máy tính trước chồng hồ sơ cao ngất.",
        "core_prompt": (
            "Two-panel vertical split composition: left panel shows the stick figure wearing a red necktie "
            "rushing along a strict red directional arrow toward an office building; right panel shows the same "
            "stick figure hunched at an office desk typing on a computer beside a tall stack of folders."
        ),
    },
    {
        "beat_index": 6,
        "scene_id": "SC01",
        "start_ch": 8.35,
        "end_ch": 10.30,
        "at_scene": 8.35,
        "duration": 1.95,
        "voiceover_vi": "và bao nhiêu giờ thuộc về kẻ khác.",
        "acoustic_trigger": "Ẩn dụ 'thuộc về kẻ khác' + Ngắt câu dài tại 9.67s–10.55s (dur=0.87s)",
        "visual_function": "VF5_METAPHOR_CAUSAL",
        "shot_framing": "Flat 2D conceptual diagram",
        "effect": "zoom_in",
        "draw_on": False,
        "line_boil": True,
        "based_on": None,
        "allowed_text": [],
        "action_description_vi": "Mặt đồng hồ tròn lớn bị chia như chiếc bánh; bàn tay khổng lồ mặc vest từ trên cao thò xuống lấy đi 3/4 số múi giờ, để lại nhân vật người que nhỏ bé đứng nhìn bất lực.",
        "core_prompt": (
            "Conceptual 2D illustration: a giant circular clock face divided like a pie chart; "
            "a huge boss stick-hand in a dark suit cuff reaching down from above and grabbing three-quarters "
            "of the red clock slices, while the small worker stick figure stands below looking up helplessly."
        ),
    },
    {
        "beat_index": 7,
        "scene_id": "SC01",
        "start_ch": 10.30,
        "end_ch": 11.70,
        "at_scene": 10.30,
        "duration": 1.40,
        "voiceover_vi": "Tối nay, trước khi ngủ,",
        "acoustic_trigger": "Chuyển thời gian 'Tối nay' + Ngắt phẩy tại 10.79s và 11.54s–11.76s",
        "visual_function": "VF1_ESTABLISHING",
        "shot_framing": "Wide shot",
        "effect": "pan_left",
        "draw_on": False,
        "line_boil": True,
        "based_on": None,
        "allowed_text": [],
        "action_description_vi": "Trở lại phòng ngủ lúc đêm khuya (trăng lưỡi liềm ngoài cửa sổ), nhân vật người que kiệt sức ngồi bên mép giường chuẩn bị đi ngủ.",
        "core_prompt": (
            "Wide shot of the modern bedroom at late night with a crescent moon and stars visible through the window; "
            "the stick figure sitting exhausted on the bed edge with heavy drooping eyelids and a sweat drop."
        ),
    },
    {
        "beat_index": 8,
        "scene_id": "SC01",
        "start_ch": 11.70,
        "end_ch": 14.52,
        "at_scene": 11.70,
        "duration": 2.82,
        "voiceover_vi": "bạn lại hẹn chính cỗ máy ấy gọi mình dậy lần nữa.",
        "acoustic_trigger": "Khép vòng lặp cảnh 1 + Kết file SC01.wav tại 13.82s–14.52s",
        "visual_function": "VF6_PAYOFF_PIVOT",
        "shot_framing": "Close-up",
        "effect": "zoom_in",
        "draw_on": False,
        "line_boil": True,
        "based_on": 7,
        "allowed_text": [],
        "action_description_vi": "Cận cảnh nhân vật với vẻ mặt cam chịu ấn nút hẹn giờ lại trên chiếc đồng hồ báo thức, phía sau là mũi tên vòng tròn khép kín biểu thị vòng lặp.",
        "core_prompt": (
            "Close-up in the night bedroom: the weary stick figure dutifully pressing the button to set the alarm clock "
            "on the nightstand again, framed by a subtle hand-drawn circular loop arrow in the background."
        ),
    },

    # ==================== SC02 (14.52s - 30.38s, 8 Beats) ====================
    {
        "beat_index": 9,
        "scene_id": "SC02",
        "start_ch": 14.52,
        "end_ch": 16.92,
        "at_scene": 0.00,
        "duration": 2.40,
        "voiceover_vi": "Giờ hãy quay về năm mươi nghìn năm trước.",
        "acoustic_trigger": "Mở cảnh SC02 + Số liệu niên đại '50.000 năm' + Ngắt câu 16.27s–17.21s (dur=0.94s)",
        "visual_function": "VF3_DIAGRAM_DATA",
        "shot_framing": "Flat 2D timeline diagram",
        "effect": "pan_left",
        "draw_on": True,
        "line_boil": True,
        "based_on": None,
        "allowed_text": ["50,000"],
        "action_description_vi": "Trục thời gian ngang có mũi tên cong quay ngược từ hình bóng đô thị xám bên phải lùi về cảnh thảo nguyên hoang sơ nắng ấm bên trái, kèm con số '50,000'.",
        "core_prompt": (
            "Flat 2D diagrammatic timeline on warm parchment paper: a bold curved arrow sweeping backward "
            "from a small gray modern city silhouette on the right to a warm golden prehistoric savanna on the left, "
            "rendering ONLY the bold hand-drawn number '50,000' above the arrow."
        ),
    },
    {
        "beat_index": 10,
        "scene_id": "SC02",
        "start_ch": 16.92,
        "end_ch": 18.67,
        "at_scene": 2.40,
        "duration": 1.75,
        "voiceover_vi": "Một người thức giấc theo ánh bình minh,",
        "acoustic_trigger": "Thiết lập nhân vật tiền sử + Ngắt phẩy tại 18.50s–18.79s (dur=0.29s)",
        "visual_function": "VF1_ESTABLISHING",
        "shot_framing": "Wide establishing shot",
        "effect": "zoom_in",
        "draw_on": False,
        "line_boil": True,
        "based_on": None,
        "allowed_text": [],
        "action_description_vi": "Toàn cảnh mái đá và thảo nguyên rộng mở dưới ánh bình minh vàng cam ấm áp; nhân vật người que mặc áo da thú nằm trên tấm da thú từ từ mở mắt tỉnh giấc tự nhiên.",
        "core_prompt": (
            "Wide establishing shot of a peaceful prehistoric rock shelter overlooking a sunlit savanna at golden sunrise; "
            "an anonymous stick figure wearing a simple shaggy brown animal pelt waking up naturally on a fur mat "
            "as warm sunbeams touch his face."
        ),
    },
    {
        "beat_index": 11,
        "scene_id": "SC02",
        "start_ch": 18.67,
        "end_ch": 21.42,
        "at_scene": 4.15,
        "duration": 2.75,
        "voiceover_vi": "không báo thức, không lịch trình, chẳng vội đi đâu.",
        "acoustic_trigger": "Chuỗi 3 phủ định (ngắt phẩy 19.21s, 20.01s) + Ngắt câu 20.96s–21.77s (dur=0.82s)",
        "visual_function": "VF4_CONTRAST_SPLIT",
        "shot_framing": "Medium shot with 3 negation icons",
        "effect": "pan_right",
        "draw_on": False,
        "line_boil": True,
        "based_on": 10,
        "allowed_text": ["X"],
        "action_description_vi": "Nhân vật nằm gối đầu lên tay thư thái ngắm nắng sớm; phía trên hiện 3 biểu tượng nhỏ bị gạch chéo đỏ (X): đồng hồ báo thức, tờ lịch kẻ ô, và đồng hồ bấm giờ.",
        "core_prompt": (
            "Medium shot of the prehistoric stick figure in brown pelt relaxing calmly with hands behind his head at sunrise; "
            "floating above him are three small hand-drawn icons each crossed out with a bold red 'X': "
            "an alarm clock, a grid calendar, and a rushing stopwatch."
        ),
    },
    {
        "beat_index": 12,
        "scene_id": "SC02",
        "start_ch": 21.42,
        "end_ch": 22.75,
        "at_scene": 6.90,
        "duration": 1.33,
        "voiceover_vi": "Anh có một ngọn giáo,",
        "acoustic_trigger": "Đạo cụ định danh #1 'ngọn giáo' + Ngắt phẩy tại 22.59s–22.85s (dur=0.26s)",
        "visual_function": "VF2_ACTION_STATE",
        "shot_framing": "Medium close-up prop focus",
        "effect": "slide_left",
        "draw_on": False,
        "line_boil": True,
        "based_on": None,
        "allowed_text": [],
        "action_description_vi": "Cận cảnh một ngọn giáo gỗ buộc mũi đá lửa sắc sảo dựng tựa vào tảng đá bên cạnh chỗ ngủ.",
        "core_prompt": (
            "Focused medium close-up of a single handcrafted wooden spear with a chipped flint stone tip "
            "leaning against a warm sandstone rock in morning light."
        ),
    },
    {
        "beat_index": 13,
        "scene_id": "SC02",
        "start_ch": 22.75,
        "end_ch": 24.82,
        "at_scene": 8.23,
        "duration": 2.07,
        "voiceover_vi": "hai tấm da thú và đống lửa sưởi.",
        "acoustic_trigger": "Đạo cụ #2 & #3 + Ngắt câu dài tại 24.38s–25.21s (dur=0.83s)",
        "visual_function": "VF2_ACTION_STATE",
        "shot_framing": "Medium wide shot",
        "effect": "zoom_out",
        "draw_on": False,
        "line_boil": True,
        "based_on": 12,
        "allowed_text": [],
        "action_description_vi": "Góc máy mở rộng hiển thị trọn vẹn 3 tài sản: ngọn giáo gỗ, hai tấm da thú trải cạnh nhau và đống lửa trại đang cháy ấm áp.",
        "core_prompt": (
            "Medium wide shot of the prehistoric camp showing the stick figure's three possessions together: "
            "the stone-tipped wooden spear, two neatly folded brown animal pelts, and a warm crackling stone-ring campfire "
            "with gentle rising smoke."
        ),
    },
    {
        "beat_index": 14,
        "scene_id": "SC02",
        "start_ch": 24.82,
        "end_ch": 26.40,
        "at_scene": 10.30,
        "duration": 1.58,
        "voiceover_vi": "Anh ngồi dậy, vươn vai,",
        "acoustic_trigger": "Động từ cơ thể 'ngồi dậy, vươn vai' + Ngắt phẩy tại 25.66s và 26.22s–26.47s",
        "visual_function": "VF2_ACTION_STATE",
        "shot_framing": "Medium shot",
        "effect": "zoom_in",
        "draw_on": False,
        "line_boil": True,
        "based_on": 13,
        "allowed_text": [],
        "action_description_vi": "Nhân vật người que tiền sử ngồi dậy bên đống lửa, vươn rộng hai tay lên cao đón nắng bình minh với gương mặt tươi tỉnh.",
        "core_prompt": (
            "Medium shot of the prehistoric stick figure in animal pelt sitting up beside the campfire "
            "and stretching both arms wide toward the morning sky with a refreshed happy expression."
        ),
    },
    {
        "beat_index": 15,
        "scene_id": "SC02",
        "start_ch": 26.40,
        "end_ch": 28.55,
        "at_scene": 11.88,
        "duration": 2.15,
        "voiceover_vi": "tự hỏi câu mà bạn chưa từng đủ tự do để hỏi:",
        "acoustic_trigger": "Mệnh đề 'đủ tự do để hỏi' + Ngắt hai chấm tại 28.39s–28.70s (dur=0.31s)",
        "visual_function": "VF4_CONTRAST_SPLIT",
        "shot_framing": "Wide over-the-shoulder POV shot",
        "effect": "pan_right",
        "draw_on": False,
        "line_boil": True,
        "based_on": 14,
        "allowed_text": [],
        "action_description_vi": "Góc máy từ sau vai nhân vật tiền sử đứng nhìn ra toàn cảnh thảo nguyên, sông suối và đàn chim bay tự do dưới bầu trời mênh mông.",
        "core_prompt": (
            "Over-the-shoulder wide shot from behind the prehistoric stick figure standing at the shelter edge, "
            "gazing out over a vast open savanna, winding river, and birds flying freely across an open horizon."
        ),
    },
    {
        "beat_index": 16,
        "scene_id": "SC02",
        "start_ch": 28.55,
        "end_ch": 30.38,
        "at_scene": 14.03,
        "duration": 1.83,
        "voiceover_vi": "Hôm nay mình làm gì nhỉ?",
        "acoustic_trigger": "Câu hỏi tu từ kết cảnh SC02 + Ngắt cuối file tại 29.69s–30.38s",
        "visual_function": "VF6_PAYOFF_PIVOT",
        "shot_framing": "Close-up",
        "effect": "punch_in",
        "draw_on": False,
        "line_boil": True,
        "based_on": 14,
        "allowed_text": ["?"],
        "action_description_vi": "Cận cảnh nhân vật người que tiền sử một tay chống cằm, mỉm cười thảnh thơi, phía trên đầu là bong bóng suy nghĩ chứa một dấu chấm hỏi '?' vẽ tay.",
        "core_prompt": (
            "Close-up of the prehistoric stick figure in animal pelt smiling serenely with one hand on his chin, "
            "a clean thought bubble above his head containing ONLY a single bold hand-drawn question mark '?'."
        ),
    },

    # ==================== SC03 (30.38s - 46.72s, 7 Beats) ====================
    {
        "beat_index": 17,
        "scene_id": "SC03",
        "start_ch": 30.38,
        "end_ch": 32.98,
        "at_scene": 0.00,
        "duration": 2.60,
        "voiceover_vi": "Não bạn hẳn đang phản đối: không thể nào!",
        "acoustic_trigger": "Mở cảnh SC03 + Ngắt hai chấm 31.80s + Ngắt câu 32.54s–33.37s (dur=0.83s)",
        "visual_function": "VF6_PAYOFF_PIVOT",
        "shot_framing": "Medium close-up",
        "effect": "shake",
        "draw_on": False,
        "line_boil": True,
        "based_on": None,
        "allowed_text": ["!", "X"],
        "action_description_vi": "Nhân vật người que hiện đại đưa hai tay ôm đầu vẻ mặt không tin nổi; phía trên đỉnh đầu hiện hình vẽ bộ não màu hồng phát tia chớp cùng dấu '!' và 'X' đỏ.",
        "core_prompt": (
            "Medium close-up of the modern stick figure holding both hands to his head in disbelief; "
            "above his head floats a hand-drawn pink brain icon sparking with lightning bolts and ONLY "
            "a bold red '!' and 'X' symbol."
        ),
    },
    {
        "beat_index": 18,
        "scene_id": "SC03",
        "start_ch": 32.98,
        "end_ch": 35.43,
        "at_scene": 2.60,
        "duration": 2.45,
        "voiceover_vi": "Đời xưa tàn khốc, ngắn ngủi và tuyệt vọng,",
        "acoustic_trigger": "Ngắt phẩy 34.04s + Ngắt phẩy 35.28s–35.58s (dur=0.30s)",
        "visual_function": "VF2_ACTION_STATE",
        "shot_framing": "Wide dramatic shot",
        "effect": "zoom_in",
        "draw_on": False,
        "line_boil": True,
        "based_on": None,
        "allowed_text": [],
        "action_description_vi": "Bức tranh định kiến u ám: người tiền sử gầy gò co ro dưới cơn mưa giông tối tăm và sấm chớp, xung quanh là cành cây khô trụi lá.",
        "core_prompt": (
            "Dark dramatic wide shot illustrating the grim stereotype of prehistory: a shivering stick figure "
            "in tattered pelt huddled under cold pouring rain and lightning flashes amid barren thorny trees."
        ),
    },
    {
        "beat_index": 19,
        "scene_id": "SC03",
        "start_ch": 35.43,
        "end_ch": 37.03,
        "at_scene": 5.05,
        "duration": 1.60,
        "voiceover_vi": "từng giây đều là sinh tồn.",
        "acoustic_trigger": "Cao trào định kiến + Ngắt câu dài tại 36.56s–37.40s (dur=0.84s)",
        "visual_function": "VF2_ACTION_STATE",
        "shot_framing": "Medium action shot",
        "effect": "pan_left",
        "draw_on": False,
        "line_boil": True,
        "based_on": 18,
        "allowed_text": [],
        "action_description_vi": "Trong khung cảnh u ám đó, nhân vật người tiền sử hoảng hốt bỏ chạy khi một con hổ răng kiếm nhe nanh nhảy ra từ bụi rậm.",
        "core_prompt": (
            "Medium action shot in the same dark prehistoric setting: the terrified stick figure sprinting away "
            "with sweat drops flying as a fierce saber-toothed tiger lunges from the shadows behind him."
        ),
    },
    {
        "beat_index": 20,
        "scene_id": "SC03",
        "start_ch": 37.03,
        "end_ch": 39.63,
        "at_scene": 6.65,
        "duration": 2.60,
        "voiceover_vi": "Suốt nhiều thế kỷ, ai cũng tin thế.",
        "acoustic_trigger": "Ngắt phẩy 38.17s + Ngắt câu dài tại 39.20s–40.02s (dur=0.82s)",
        "visual_function": "VF5_METAPHOR_CAUSAL",
        "shot_framing": "Medium wide shot",
        "effect": "zoom_out",
        "draw_on": False,
        "line_boil": True,
        "based_on": None,
        "allowed_text": [],
        "action_description_vi": "Một chồng sách lịch sử cổ dày cộp đặt cạnh bức tranh đóng khung vẽ cảnh người tiền sử khổ sở; ba nhân vật người que hiện đại đứng nhìn và gật đầu tin tưởng.",
        "core_prompt": (
            "Medium wide illustration: three modern stick figures nodding in agreement while looking at a framed "
            "wall picture of a miserable caveman, beside a tall stack of thick old history books and an hourglass."
        ),
    },
    {
        "beat_index": 21,
        "scene_id": "SC03",
        "start_ch": 39.63,
        "end_ch": 42.98,
        "at_scene": 9.25,
        "duration": 3.35,
        "voiceover_vi": "Nhưng bằng chứng chứng minh điều đó sai lầm đã nằm sâu dưới lòng đất.",
        "acoustic_trigger": "Chuyển hướng 'Nhưng bằng chứng... sâu dưới lòng đất' + Ngắt câu 42.55s–43.41s (dur=0.87s)",
        "visual_function": "VF3_DIAGRAM_DATA",
        "shot_framing": "Flat 2D geological cross-section diagram",
        "effect": "pan_right",
        "draw_on": True,
        "line_boil": True,
        "based_on": None,
        "allowed_text": [],
        "action_description_vi": "Sơ đồ mặt cắt lòng đất 3 tầng: tầng trên cùng là mặt cỏ, tầng giữa là đất nâu, và tầng sâu dưới cùng là bộ xương người cổ đại khỏe mạnh nằm cạnh mũi giáo đá được khoanh vòng tròn sáng.",
        "core_prompt": (
            "Flat 2D geological cross-section diagram: green grass on the surface at the top, layered brown earth "
            "strata in the middle, and deep underground at the bottom a well-preserved ancient skeleton and stone "
            "spearhead highlighted by a glowing golden circle."
        ),
    },
    {
        "beat_index": 22,
        "scene_id": "SC03",
        "start_ch": 42.98,
        "end_ch": 44.83,
        "at_scene": 12.60,
        "duration": 1.85,
        "voiceover_vi": "Khi các nhà khoa học khai quật lên,",
        "acoustic_trigger": "Hành động 'khai quật' + Ngắt phẩy tại 44.68s–44.93s (dur=0.25s)",
        "visual_function": "VF2_ACTION_STATE",
        "shot_framing": "Medium shot",
        "effect": "zoom_in",
        "draw_on": False,
        "line_boil": True,
        "based_on": 21,
        "allowed_text": [],
        "action_description_vi": "Hai nhà khảo cổ người que đội mũ rộng vành quỳ xuống hố khai quật, cầm chổi nhỏ và kính lúp tỉ mỉ quét lớp cát phủ trên bộ xương cổ đại.",
        "core_prompt": (
            "Medium shot at an archaeological dig trench: two archaeologist stick figures wearing explorer sun hats "
            "kneeling down, using a small brush and magnifying glass to carefully uncover the ancient skeleton from the earth."
        ),
    },
    {
        "beat_index": 23,
        "scene_id": "SC03",
        "start_ch": 44.83,
        "end_ch": 46.72,
        "at_scene": 14.45,
        "duration": 1.89,
        "voiceover_vi": "nó đã đảo lộn mọi thứ.",
        "acoustic_trigger": "Động từ mạnh 'đảo lộn mọi thứ' + Kết cảnh SC03 tại 46.03s–46.72s",
        "visual_function": "VF6_PAYOFF_PIVOT",
        "shot_framing": "Medium close-up",
        "effect": "punch_in",
        "draw_on": False,
        "line_boil": True,
        "based_on": 22,
        "allowed_text": ["!"],
        "action_description_vi": "Nhà khảo cổ giật mình kinh ngạc khi nhìn kết quả; bên cạnh là chồng sách lịch sử cũ bị lật nhào lộn ngược 180 độ với mũi tên xoay đảo chiều và dấu '!'.",
        "core_prompt": (
            "Dynamic medium close-up: the archaeologist stick figure gasping in shock with wide eyes as old history "
            "books flip upside down in mid-air alongside a bold curved 180-degree reversal arrow and ONLY an exclamation mark '!'."
        ),
    },

    # ==================== SC04 (46.72s - 64.25s, 11 Beats) ====================
    {
        "beat_index": 24,
        "scene_id": "SC04",
        "start_ch": 46.72,
        "end_ch": 48.57,
        "at_scene": 0.00,
        "duration": 1.85,
        "voiceover_vi": "Và đó là một bí ẩn lớn.",
        "acoustic_trigger": "Mở cảnh SC04 + Ngắt câu dài tại 48.12s–48.94s (dur=0.82s)",
        "visual_function": "VF6_PAYOFF_PIVOT",
        "shot_framing": "Medium shot",
        "effect": "zoom_in",
        "draw_on": False,
        "line_boil": True,
        "based_on": None,
        "allowed_text": ["?"],
        "action_description_vi": "Nhân vật người que hiện đại đứng giữa phông nền sáng tối tương phản, cầm kính lúp nhìn vào một dấu chấm hỏi '?' lớn đặt trên bệ đá.",
        "core_prompt": (
            "Medium shot of an inquisitive stick figure standing before a giant hand-drawn question mark '?' "
            "on a pedestal, holding a magnifying glass with a puzzled expression."
        ),
    },
    {
        "beat_index": 25,
        "scene_id": "SC04",
        "start_ch": 48.57,
        "end_ch": 50.97,
        "at_scene": 1.85,
        "duration": 2.40,
        "voiceover_vi": "Bạn sống quanh muôn vàn cỗ máy tiết kiệm thời gian:",
        "acoustic_trigger": "Mệnh đề dẫn nhập thiết bị + Ngắt hai chấm tại 50.80s–51.11s (dur=0.31s)",
        "visual_function": "VF1_ESTABLISHING",
        "shot_framing": "Wide shot",
        "effect": "zoom_out",
        "draw_on": False,
        "line_boil": True,
        "based_on": None,
        "allowed_text": [],
        "action_description_vi": "Nhân vật người que hiện đại đứng ở trung tâm căn phòng tiện nghi với khung lưới 4 góc sẵn sàng hiển thị các thiết bị tiết kiệm thời gian.",
        "core_prompt": (
            "Wide shot of a modern stick figure standing in the center of a bright modern home interior, "
            "surrounded by clean quadrant frames showing household technology and clocks."
        ),
    },
    {
        "beat_index": 26,
        "scene_id": "SC04",
        "start_ch": 50.97,
        "end_ch": 51.57,
        "at_scene": 4.25,
        "duration": 0.60,
        "voiceover_vi": "máy giặt,",
        "acoustic_trigger": "Đạo cụ liệt kê #1 + Ngắt phẩy tại 51.39s–51.72s (dur=0.33s)",
        "visual_function": "VF2_ACTION_STATE",
        "shot_framing": "2x2 Quad-grid layout (Panel 1/4 active)",
        "effect": "slide_left",
        "draw_on": False,
        "line_boil": True,
        "based_on": 25,
        "allowed_text": [],
        "action_description_vi": "Bố cục Lưới 2x2: Ô trên bên trái nổi bật chiếc máy giặt cửa tròn đang xoay quần áo sủi bọt xà phòng (3 ô còn lại phác mờ).",
        "core_prompt": (
            "2x2 quad-grid layout on clean paper: the top-left panel brightly highlights a hand-drawn "
            "front-loading washing machine spinning clothes with soap bubbles, while the other three panels "
            "remain faint sketchy outlines."
        ),
    },
    {
        "beat_index": 27,
        "scene_id": "SC04",
        "start_ch": 51.57,
        "end_ch": 52.37,
        "at_scene": 4.85,
        "duration": 0.80,
        "voiceover_vi": "máy rửa bát,",
        "acoustic_trigger": "Đạo cụ liệt kê #2 + Ngắt phẩy tại 52.21s–52.49s (dur=0.27s)",
        "visual_function": "VF2_ACTION_STATE",
        "shot_framing": "2x2 Quad-grid layout (Panels 1-2/4 active)",
        "effect": "pan_right",
        "draw_on": False,
        "line_boil": True,
        "based_on": 26,
        "allowed_text": [],
        "action_description_vi": "Trên cùng bố cục Lưới 2x2: Ô trên trái có máy giặt, và ô trên phải bật sáng chiếc máy rửa bát mở hé cửa với những chiếc đĩa trắng lấp lánh.",
        "core_prompt": (
            "2x2 quad-grid layout continuing the sequence: top-left panel shows the washing machine, "
            "and top-right panel now brightly highlights an open dishwasher filled with sparkling clean plates and water jets."
        ),
    },
    {
        "beat_index": 28,
        "scene_id": "SC04",
        "start_ch": 52.37,
        "end_ch": 53.22,
        "at_scene": 5.65,
        "duration": 0.85,
        "voiceover_vi": "lò vi sóng,",
        "acoustic_trigger": "Đạo cụ liệt kê #3 + Ngắt phẩy tại 53.09s–53.32s (dur=0.23s)",
        "visual_function": "VF2_ACTION_STATE",
        "shot_framing": "2x2 Quad-grid layout (Panels 1-3/4 active)",
        "effect": "pan_left",
        "draw_on": False,
        "line_boil": True,
        "based_on": 27,
        "allowed_text": [],
        "action_description_vi": "Trên cùng bố cục Lưới 2x2: Thêm ô dưới trái bật sáng chiếc lò vi sóng có khay thức ăn đang quay phát tia sóng ấm.",
        "core_prompt": (
            "2x2 quad-grid layout continuing the sequence: washing machine at top-left, dishwasher at top-right, "
            "and bottom-left panel now brightly highlights a glowing microwave oven heating a bowl of food."
        ),
    },
    {
        "beat_index": 29,
        "scene_id": "SC04",
        "start_ch": 53.22,
        "end_ch": 53.82,
        "at_scene": 6.50,
        "duration": 0.60,
        "voiceover_vi": "xe hơi,",
        "acoustic_trigger": "Đạo cụ liệt kê #4 + Ngắt phẩy tại 53.68s–53.94s (dur=0.25s)",
        "visual_function": "VF2_ACTION_STATE",
        "shot_framing": "2x2 Quad-grid layout (All 4/4 panels active)",
        "effect": "punch_in",
        "draw_on": False,
        "line_boil": True,
        "based_on": 28,
        "allowed_text": [],
        "action_description_vi": "Hoàn thiện toàn bộ Lưới 2x2 cả 4 thiết bị: Máy giặt, Máy rửa bát, Lò vi sóng, và ô dưới phải bật sáng chiếc xe hơi hiện đại đang lăn bánh nhanh.",
        "core_prompt": (
            "Complete 2x2 quad-grid illustration showing all four time-saving machines in full color: "
            "washing machine (top-left), dishwasher (top-right), microwave oven (bottom-left), and a sleek "
            "modern commuter car speeding with motion lines (bottom-right)."
        ),
    },
    {
        "beat_index": 30,
        "scene_id": "SC04",
        "start_ch": 53.82,
        "end_ch": 55.27,
        "at_scene": 7.10,
        "duration": 1.45,
        "voiceover_vi": "để cho bạn thêm thì giờ.",
        "acoustic_trigger": "Mệnh đề mục đích + Ngắt câu dài tại 54.86s–55.70s (dur=0.83s)",
        "visual_function": "VF5_METAPHOR_CAUSAL",
        "shot_framing": "Medium conceptual diagram",
        "effect": "zoom_in",
        "draw_on": False,
        "line_boil": True,
        "based_on": 29,
        "allowed_text": [],
        "action_description_vi": "4 thiết bị gia dụng thu nhỏ dẫn ống phễu rót các đồng xu thời gian (vẽ hình mặt đồng hồ) vào tay nhân vật người que đang mỉm cười kỳ vọng.",
        "core_prompt": (
            "Conceptual 2D illustration: the four modern appliances channeling glowing clock-face coins "
            "through a funnel toward the modern stick figure holding out an expectant basket."
        ),
    },
    {
        "beat_index": 31,
        "scene_id": "SC04",
        "start_ch": 55.27,
        "end_ch": 57.15,
        "at_scene": 8.55,
        "duration": 1.88,
        "voiceover_vi": "Vậy cớ sao một người không chút công nghệ",
        "acoustic_trigger": "Mở câu hỏi đối lập (nửa đầu) + Điểm neo từ khóa 'không chút công nghệ'",
        "visual_function": "VF4_CONTRAST_SPLIT",
        "shot_framing": "50/50 Vertical Split-Screen",
        "effect": "slide_left",
        "draw_on": False,
        "line_boil": True,
        "based_on": None,
        "allowed_text": [],
        "action_description_vi": "Chia đôi màn hình 50/50: nửa trái ấm áp là người tiền sử mặc da thú chỉ cầm 1 cây giáo gỗ ngồi thảnh thơi dưới gốc cây; nửa phải xám lạnh là người hiện đại bị vây quanh bởi đống máy móc và dây điện.",
        "core_prompt": (
            "50/50 vertical split-screen comparison: left half in warm golden tones shows the prehistoric stick figure "
            "in animal pelt relaxing peacefully under a tree with only a wooden spear; right half in cool gray tones "
            "shows the modern stick figure tangled in cables and surrounded by appliances."
        ),
    },
    {
        "beat_index": 32,
        "scene_id": "SC04",
        "start_ch": 57.15,
        "end_ch": 58.97,
        "at_scene": 10.43,
        "duration": 1.82,
        "voiceover_vi": "lại có nhiều thời gian rảnh hơn bạn?",
        "acoustic_trigger": "Nửa sau câu hỏi so sánh + Ngắt câu dài tại 58.55s–59.40s (dur=0.85s)",
        "visual_function": "VF3_DIAGRAM_DATA",
        "shot_framing": "Flat 2D balance scale diagram",
        "effect": "zoom_in",
        "draw_on": False,
        "line_boil": True,
        "based_on": 31,
        "allowed_text": ["?"],
        "action_description_vi": "Chiếc cân đĩa lớn: đĩa bên người tiền sử trĩu nặng những mặt trời/đồng hồ thời gian rảnh rỗi; đĩa bên người hiện đại bị hất tung lên cao vì trống rỗng, kèm dấu '?'.",
        "core_prompt": (
            "2D metaphorical balance scale diagram: on the left pan, the prehistoric stick figure sits beside "
            "a huge overflowing pile of golden leisure sun-clocks weighing the scale down; on the right pan, "
            "the modern stick figure is lifted high with an empty pan and ONLY a bold '?' symbol."
        ),
    },
    {
        "beat_index": 33,
        "scene_id": "SC04",
        "start_ch": 58.97,
        "end_ch": 61.67,
        "at_scene": 12.25,
        "duration": 2.70,
        "voiceover_vi": "Suốt ngày anh ta đã làm gì mà bạn không thể?",
        "acoustic_trigger": "Câu hỏi hành động + Ngắt câu dài tại 61.28s–62.10s (dur=0.82s)",
        "visual_function": "VF2_ACTION_STATE",
        "shot_framing": "Medium wide contrast shot",
        "effect": "pan_right",
        "draw_on": False,
        "line_boil": True,
        "based_on": None,
        "allowed_text": [],
        "action_description_vi": "Nhân vật người que tiền sử ung dung dạo bước và trò chuyện bên đống lửa giữa thảo nguyên ngập nắng, trong khi nhân vật hiện đại đứng sau cửa kính văn phòng nhìn sang đầy thắc mắc.",
        "core_prompt": (
            "Medium wide contrast scene: the prehistoric stick figure strolling leisurely across a sunny savanna camp, "
            "while on the far right the modern office stick figure peers out from behind a cramped glass office window "
            "with a curious envious expression."
        ),
    },
    {
        "beat_index": 34,
        "scene_id": "SC04",
        "start_ch": 61.67,
        "end_ch": 64.25,
        "at_scene": 14.95,
        "duration": 2.58,
        "voiceover_vi": "Và thời gian của bạn đã biến đi đâu?",
        "acoustic_trigger": "Câu hỏi kết chương + Ngắt cuối file SC04.wav tại 63.52s–64.25s",
        "visual_function": "VF6_PAYOFF_PIVOT",
        "shot_framing": "Close-up cliffhanger payoff",
        "effect": "punch_in",
        "draw_on": False,
        "line_boil": True,
        "based_on": None,
        "allowed_text": ["?"],
        "action_description_vi": "Cận cảnh nhân vật người que hiện đại nhìn xuống hai bàn tay trống rỗng khi những chiếc đồng hồ và tờ lịch tan thành từng mảnh bay vút lên bầu trời theo gió, kèm dấu '?' lớn.",
        "core_prompt": (
            "Dramatic close-up payoff shot: the modern stick figure looking down at his empty open hands "
            "as clock faces and calendar pages dissolve and blow away into the wind like autumn leaves, "
            "with ONLY a single bold hand-drawn '?' floating above."
        ),
    },
]


def main():
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    CLEAN_VOICE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copy clean mono WAVs for Chapter 1 (SC01..SC04.wav) into bundle/audio/clean_voice/
    if SCRATCH_CH1_AUDIO.is_dir():
        for sc in ["SC01", "SC02", "SC03", "SC04"]:
            src_wav = SCRATCH_CH1_AUDIO / f"{sc}.wav"
            if src_wav.is_file():
                shutil.copy2(src_wav, CLEAN_VOICE_DIR / f"{sc}.wav")

    # 2. Build manifest items for the 34 blind-test beats
    shots_out = []
    scene_counts = {"SC01": 0, "SC02": 0, "SC03": 0, "SC04": 0}
    for b in CH1_BLIND_BEATS:
        scene_counts[b["scene_id"]] += 1

    for b in CH1_BLIND_BEATS:
        idx = b["beat_index"]
        fname = f"ch1_blind_beat_{idx:02d}_{b['start_ch']:05.2f}s.jpg"
        full_prompt = f"{STYLE_PREFIX}{b['core_prompt']}{STYLE_SUFFIX}"
        shots_out.append({
            "shot_index": idx,
            "chapter_number": 1,
            "chapter_title": "The mystery of modern time (Blind Test 34 Beats)",
            "scene_id": b["scene_id"],
            "shot_in_chapter": f"{idx}/{len(CH1_BLIND_BEATS)}",
            "target_filename": fname,
            "timing": {
                "start_seconds_chapter": b["start_ch"],
                "end_seconds_chapter": b["end_ch"],
                "duration_seconds": b["duration"],
                "remotion_at_seconds": b["at_scene"],
                "acoustic_trigger": b["acoustic_trigger"],
            },
            "voiceover_vi": b["voiceover_vi"],
            "visual_direction": {
                "visual_function": b["visual_function"],
                "shot_framing": b["shot_framing"],
                "action_description_vi": b["action_description_vi"],
                "remotion_effect": b["effect"],
                "draw_on": b["draw_on"],
                "line_boil": b["line_boil"],
                "based_on_shot_index": b["based_on"],
                "allowed_text": b["allowed_text"],
                "ai_prompt": full_prompt,
            },
        })

    manifest_payload = {
        "project": "ancient-humans-ch1-blind-test",
        "methodology": "Zero-Reference Acoustic-Pause & Semantic-Clause Storyboarding (Blind Test)",
        "chapter_number": 1,
        "total_duration_seconds": 64.25,
        "total_shots": len(shots_out),
        "scene_distribution": scene_counts,
        "aspect_ratio": "16:9",
        "resolution": "1920x1080",
        "shots": shots_out,
    }

    json_path = MANIFEST_DIR / "ch1_blind_34_shots.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(manifest_payload, f, ensure_ascii=False, indent=2)

    # 3. Write Markdown human-readable table
    md_path = MANIFEST_DIR / "ch1_blind_34_shots.md"
    md_lines = [
        "# Bảng Storyboard Thử Nghiệm Mù — Chương 1 (34 Beats, `0.00s – 64.25s`)\n",
        f"- **Phương pháp**: Thiết kế mù 100% từ khoảng ngắt âm học (`SC01..SC04.wav`) + lời thoại tiếng Việt (`ch1_subtitles.json`).",
        f"- **Tổng số Beats**: `{len(shots_out)}` (`SC01: {scene_counts['SC01']}`, `SC02: {scene_counts['SC02']}`, `SC03: {scene_counts['SC03']}`, `SC04: {scene_counts['SC04']}`).\n",
        "| Beat | Cảnh | Mốc Chương (`start–end`) | `at` (Cảnh) | Lời thoại tiếng Việt | Chức năng & Góc máy | Hiệu ứng & `based_on` | Mô tả cảnh vẽ (VI) | AI Prompt (EN) |",
        "| :---: | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- |",
    ]
    for s in shots_out:
        vd = s["visual_direction"]
        tm = s["timing"]
        based = f"`based_on: B{vd['based_on_shot_index']:02d}`" if vd["based_on_shot_index"] else "Độc lập"
        fx = f"`{vd['remotion_effect']}`" + (" + `draw_on`" if vd["draw_on"] else "")
        md_lines.append(
            f"| **B{s['shot_index']:02d}** | `{s['scene_id']}` | `{tm['start_seconds_chapter']:.2f}s–{tm['end_seconds_chapter']:.2f}s` (`{tm['duration_seconds']:.2f}s`) "
            f"| `{tm['remotion_at_seconds']:.2f}s` | {s['voiceover_vi']} | `{vd['visual_function']}`<br/>{vd['shot_framing']} "
            f"| {fx}<br/>{based} | {vd['action_description_vi']} | `{vd['ai_prompt']}` |"
        )
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    # 4. Update ch1_props_template.json (backup original 39-shot reference template first)
    tpl_path = TEMPLATES_DIR / "ch1_props_template.json"
    backup_path = TEMPLATES_DIR / "ch1_props_template_ref39.json.bak"
    if tpl_path.is_file() and not backup_path.is_file():
        shutil.copy2(tpl_path, backup_path)

    with open(tpl_path, "r", encoding="utf-8") as f:
        tpl = json.load(f)

    scenes = tpl["tracks"]["vi"]["scenesByAspect"]["16:9"]
    for sc in scenes:
        sc_id = sc["id"]
        sc_shots = [s for s in shots_out if s["scene_id"] == sc_id]
        sc_images = []
        for s in sc_shots:
            vd = s["visual_direction"]
            img_entry = {
                "id": f"B{s['shot_index']:02d}",
                "src": s["target_filename"],
                "at": s["timing"]["remotion_at_seconds"],
                "effect": vd["remotion_effect"],
                "line_boil": vd["line_boil"],
            }
            if vd["draw_on"]:
                img_entry["draw_on"] = True
            sc_images.append(img_entry)
        sc["image"] = sc_images[0]["src"]
        sc["images"] = sc_images

    with open(tpl_path, "w", encoding="utf-8") as f:
        json.dump(tpl, f, ensure_ascii=False, indent=2)

    print(f"[OK] Generated {json_path}")
    print(f"[OK] Generated {md_path}")
    print(f"[OK] Updated {tpl_path} with {len(shots_out)} blind-test beats ({scene_counts})")


if __name__ == "__main__":
    main()
