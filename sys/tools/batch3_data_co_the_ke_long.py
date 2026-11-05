"""Detailed scene and storyboard data for co-the-ke-batch3-16x9 (Long 16:9).

Topic: "12 Giờ Của Dạ Dày Và Lá Gan Sau Một Bữa Ăn Khuya Nhiều Dầu Mỡ"
Total Scenes: 11 scenes (SC01..SC11)
Total Unique Flow Images: 66 images (6 images per scene, 1-to-1 beat mapping)
Total Beats: 66 beats
Total Spoken Words: ~737 words (~64-72 words per scene)
Average Image Hold: ~2.94s / image (<= 3.1s)
Editorial Commentary Scenes: SC04 and SC09 (slow tempo)
Mid-CTA: SC05 (22 syllables, sitting at ~40% runtime)
Close CTA: SC11 (20 syllables <= 24, final beat is_endcard: True)
"""

from typing import Any, Dict, List

def get_long_scenes() -> List[Dict[str, Any]]:
    scenes = [
        # SC01: Giờ 0 (23:00) - Tiệc Gà Rán Đêm Khuya Và Cú Sốc Dạ Dày
        {
            "id": "SC01",
            "title": "Bữa ăn khuya đẫm dầu mỡ và dạ dày giật mình thức giấc",
            "purpose": "Triển khai bước 1: tình huống ăn khuya lúc mười một giờ đêm và cú sốc dạ dày",
            "action": "Doodle human host eats fried chicken at 11:00 PM while cute peach stomach character reacts in shock to an avalanche of yellow grease.",
            "setting": "Clean 2D kawaii bedroom and digestive cross-section on flat pure white canvas #FFFFFF.",
            "camera": "Semantic camera: establishing full_scene zooming from bedroom clock into internal lumen",
            "narration": "Mười một giờ đêm, bạn ngồi ăn đĩa gà rán ngập mỡ giòn rụm rồi leo lên giường nằm. Trong bóng tối của ổ bụng, chiếc dạ dày màu đào đang mơ màng thì bỗng giật bắn mình. Hàng trăm giọt mỡ đặc quánh đổ sập xuống như một trận lũ quét bất ngờ. Chiếc dạ dày hốt hoảng bật còi báo động khẩn cấp cho toàn bộ cơ thể.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "images": [
                {
                    "id": "SC01_I1",
                    "description": "Clean 2D kawaii medical illustration: simple doodle human host in calm-blue T-shirt #7FB3D5 happily eating crispy fried chicken drumstick on bed, night clock on white wall pointing to 11:00 PM on flat pure white canvas #FFFFFF with smooth black outline #222222, >=60% negative space.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "clean flat #FFFFFF canvas, kawaii doodle human in calm-blue #7FB3D5 shirt",
                    "change": "human eating fried chicken drumstick at 11:00 PM",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "11:00 ĐÊM", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "hook_cold_open",
                    "emphasis_text": "11:00 ĐÊM",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Mười một giờ đêm, bạn ngồi ăn đĩa gà rán ngập mỡ giòn rụm",
                        "relation": "context",
                        "source_terms": ["ăn"],
                        "visual_terms": ["chicken"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The doodle human bites into the golden drumstick as glistening oil dots sparkle around the plate, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I2",
                    "description": "Clean 2D kawaii medical illustration: doodle human host in calm-blue shirt #7FB3D5 lies flat on white bed, clicking off the bedside lamp as darkness falls on flat white canvas #FFFFFF with smooth black outlines #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC01_I1",
                    "preserve": "clean flat white canvas #FFFFFF, doodle human host",
                    "change": "human turns off lamp and lies flat on bed to sleep",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "hook_cold_open",
                    "has_character": True,
                    "explanation": {
                        "quote": "rồi leo lên giường nằm.",
                        "relation": "context",
                        "source_terms": ["nằm"],
                        "visual_terms": ["bed"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The bedroom lamp clicks off and smooth camera pushes into the transparent stomach cross-section, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I3",
                    "description": "Clean 2D kawaii medical illustration: cute peach stomach character #F6C28B sleeping peacefully in pajamas inside a soft pink abdominal cavity on flat white canvas #FFFFFF with smooth black outlines #222222, floating tiny dream bubbles.",
                    "character_ids": ["CH01"],
                    "based_on": "SC01_I1",
                    "preserve": "flat white canvas #FFFFFF, peach stomach character #F6C28B",
                    "change": "peach stomach character sleeping peacefully in dark lumen",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "hook_cold_open",
                    "has_character": True,
                    "explanation": {
                        "quote": "Trong bóng tối của ổ bụng,",
                        "relation": "context",
                        "source_terms": ["ổ bụng"],
                        "visual_terms": ["stomach"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The dream bubbles slowly float upward as peaceful zzz letters pop, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I4",
                    "description": "Clean 2D kawaii medical illustration: peach stomach character #F6C28B suddenly jumps up with wide startled dot eyes and raised stubby arms as an alarm bell rings overhead on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC01_I3",
                    "preserve": "flat white canvas, peach stomach character",
                    "change": "stomach character startles awake in sudden panic",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "narrative_situation": "hook_cold_open",
                    "has_character": True,
                    "explanation": {
                        "quote": "chiếc dạ dày màu đào đang mơ màng thì bỗng giật bắn mình.",
                        "relation": "context",
                        "source_terms": ["giật bắn mình"],
                        "visual_terms": ["startled"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The peach stomach character leaps into the air with comical shock lines bursting around its head, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I5",
                    "description": "Clean 2D kawaii medical illustration: thick golden torrent of yellow grease droplets and chewed chicken meat cascading down the esophagus like a violent flash flood on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC01_I4",
                    "preserve": "flat white canvas, kawaii medical elements",
                    "change": "golden torrent of grease crashing down like a flash flood",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "LŨ QUÉT DẦU MỠ", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "hook_cold_open",
                    "emphasis_text": "LŨ QUÉT DẦU MỠ",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Hàng trăm giọt mỡ đặc quánh đổ sập xuống như một trận lũ quét bất ngờ.",
                        "relation": "context",
                        "source_terms": ["lũ quét"],
                        "visual_terms": ["grease"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The golden liquid avalanche splashes violently into the bottom of the stomach lumen, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC01_I6",
                    "description": "Clean 2D kawaii medical illustration: peach stomach character #F6C28B pulls down a large red emergency lever labeled SOS with flashing red warning sparks radiating outward on flat white canvas #FFFFFF with smooth black outlines #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC01_I5",
                    "preserve": "flat white canvas, peach stomach character",
                    "change": "stomach pulls red emergency SOS lever with alarm sirens",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "hook_cold_open",
                    "has_character": True,
                    "explanation": {
                        "quote": "Chiếc dạ dày hốt hoảng bật còi báo động khẩn cấp cho toàn bộ cơ thể.",
                        "relation": "context",
                        "source_terms": ["báo động"],
                        "visual_terms": ["lever"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Red alarm waves pulse outward rhythmically as the camera tracks upward toward the esophageal sphincter, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC01_B1",
                    "image_id": "SC01_I1",
                    "purpose": "Bữa ăn khuya lúc mười một giờ đêm",
                    "anchor": {"vi": {"quote": "Mười một giờ đêm, bạn ngồi ăn đĩa gà rán ngập mỡ giòn rụm", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "hook_cold_open",
                    "camera_intent": "establish"
                },
                {
                    "id": "SC01_B2",
                    "image_id": "SC01_I2",
                    "purpose": "Nằm ngang ngay sau khi ăn",
                    "anchor": {"vi": {"quote": "rồi leo lên giường nằm.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "hook_cold_open",
                    "camera_intent": "focus"
                },
                {
                    "id": "SC01_B3",
                    "image_id": "SC01_I3",
                    "purpose": "Dạ dày đang ngủ yên giấc trong bóng tối",
                    "anchor": {"vi": {"quote": "Trong bóng tối của ổ bụng,", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "hook_cold_open",
                    "camera_intent": "reveal"
                },
                {
                    "id": "SC01_B4",
                    "image_id": "SC01_I4",
                    "purpose": "Cú sốc thức giấc bất ngờ của dạ dày",
                    "anchor": {"vi": {"quote": "chiếc dạ dày màu đào đang mơ màng thì bỗng giật bắn mình.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "burst",
                    "narrative_situation": "hook_cold_open",
                    "camera_intent": "tension"
                },
                {
                    "id": "SC01_B5",
                    "image_id": "SC01_I5",
                    "purpose": "Trận lũ dầu mỡ tràn xuống dạ dày",
                    "anchor": {"vi": {"quote": "Hàng trăm giọt mỡ đặc quánh đổ sập xuống như một trận lũ quét bất ngờ.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "hook_cold_open",
                    "camera_intent": "detail"
                },
                {
                    "id": "SC01_B6",
                    "image_id": "SC01_I6",
                    "purpose": "Còi báo động khẩn cấp khắp cơ thể",
                    "anchor": {"vi": {"quote": "Chiếc dạ dày hốt hoảng bật còi báo động khẩn cấp cho toàn bộ cơ thể.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "hook_cold_open",
                    "camera_intent": "tension"
                }
            ],
            "tone": "narrative_warm",
            "narrative_situation": "hook_cold_open"
        },

        # SC02: Giờ 1 (00:00) - Thức Ăn Làm Giãn Van Thực Quản Và Cơn Trào Ngược Axit
        {
            "id": "SC02",
            "title": "Thức ăn làm giãn van thực quản và cơn trào ngược axit",
            "purpose": "Triển khai bước 2: cơ chế giãn cơ thắt thực quản dưới và trào ngược axit khi nằm ngang",
            "action": "Lower esophageal sphincter relaxes under fat hormone stimulation, allowing hot acid to breach into esophagus.",
            "setting": "Clean 2D anatomical cross-section of gastroesophageal junction on flat white canvas #FFFFFF.",
            "camera": "Semantic camera: close-up tracking acidic waves creeping past loosened sphincter ring",
            "narration": "Bước sang mười hai giờ đêm, bạn vừa chìm vào giấc ngủ thì rắc rối bắt đầu xuất hiện. Lượng chất béo lớn kích thích giải phóng hormone làm giãn lỏng cơ thắt thực quản dưới. Khi bạn nằm ở tư thế nằm ngang, axit dạ dày không còn trọng lực giữ lại. Từng đợt sóng axit đậm đặc tràn ngược lên cổ họng, gây ra cảm giác nóng rát ngực.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "images": [
                {
                    "id": "SC02_I1",
                    "description": "Clean 2D kawaii medical illustration: night clock pointing to 12:00 AM midnight while doodle human sleeps in bed on flat pure white canvas #FFFFFF with smooth black outline #222222, >=60% negative space.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "flat white canvas #FFFFFF, kawaii aesthetic",
                    "change": "midnight clock at 12:00 AM over sleeping human",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "12:00 ĐÊM", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "emphasis_text": "12:00 ĐÊM",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Bước sang mười hai giờ đêm, bạn vừa chìm vào giấc ngủ thì rắc rối bắt đầu xuất hiện.",
                        "relation": "context",
                        "source_terms": ["mười hai giờ đêm"],
                        "visual_terms": ["midnight"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The clock hands tick to 12:00 AM as a subtle ripple effect sweeps across the sleeping body, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I2",
                    "description": "Clean 2D kawaii medical illustration: cute muscular ring valve of lower esophagus depicted with tiny hormone cholecystokinin molecules loosening its fibers, valve edges becoming floppy on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC02_I1",
                    "preserve": "flat white canvas, anatomical valve styling",
                    "change": "muscular valve loosening under chemical hormone action",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "Lượng chất béo lớn kích thích giải phóng hormone làm giãn lỏng cơ thắt thực quản dưới.",
                        "relation": "context",
                        "source_terms": ["cơ thắt"],
                        "visual_terms": ["valve"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Tiny green hormone spark dots attach to the valve ring causing it to sag and widen loosely, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I3",
                    "description": "Clean 2D kawaii medical illustration: horizontal cross-section showing gravity arrow crossed out with a red X, as stomach liquid levels shift horizontally towards the open esophageal doorway on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC02_I2",
                    "preserve": "flat white canvas, medical schematic styling",
                    "change": "horizontal fluid leveling with crossed out gravity icon",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "Khi bạn nằm ở tư thế nằm ngang, axit dạ dày không còn trọng lực giữ lại.",
                        "relation": "context",
                        "source_terms": ["nằm ngang"],
                        "visual_terms": ["horizontal"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The yellow digestive fluid sloshes horizontally, spilling over the relaxed valve ridge, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I4",
                    "description": "Clean 2D kawaii medical illustration: bubbling neon-green gastric acid liquid with tiny fiery red chili sparks splashing upward into the pink esophageal lining on flat white canvas #FFFFFF with smooth black outlines #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC02_I3",
                    "preserve": "flat white canvas, anatomical tube drawing",
                    "change": "bubbling acid wave climbing upward into esophagus",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "TRÀO NGƯỢC AXIT", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "narrative_situation": "mechanism_step",
                    "emphasis_text": "TRÀO NGƯỢC AXIT",
                    "focus": {"x": 0.5, "y": 0.3},
                    "has_character": True,
                    "explanation": {
                        "quote": "Từng đợt sóng axit đậm đặc tràn ngược lên cổ họng,",
                        "relation": "context",
                        "source_terms": ["axit"],
                        "visual_terms": ["acid"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Sizzling acid bubbles pop with steam rings as the liquid crests upward along the esophageal tube, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I5",
                    "description": "Clean 2D kawaii medical illustration: doodle human sleeping host with glowing red heartburn flame icon in the center of the chest, face grimacing slightly in sleep on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC02_I4",
                    "preserve": "flat white canvas, doodle human host",
                    "change": "chest burning with red heartburn flame icon during sleep",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "gây ra cảm giác nóng rát ngực.",
                        "relation": "context",
                        "source_terms": ["nóng rát"],
                        "visual_terms": ["heartburn"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The flame icon pulses warm orange and red while the human character shifts uncomfortably in bed, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC02_I6",
                    "description": "Clean 2D kawaii medical illustration: peach stomach character #F6C28B holding a tiny umbrella trying in vain to shield the throat doorway from rising acid steam on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC02_I5",
                    "preserve": "flat white canvas, peach stomach character",
                    "change": "stomach holding umbrella looking helpless against acid steam",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "gây ra cảm giác nóng rát ngực.",
                        "relation": "context",
                        "source_terms": ["ngực"],
                        "visual_terms": ["umbrella"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The peach stomach drops the umbrella in exhaustion as churning peristalsis begins, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC02_B1",
                    "image_id": "SC02_I1",
                    "purpose": "Thời điểm mười hai giờ đêm nửa đêm",
                    "anchor": {"vi": {"quote": "Bước sang mười hai giờ đêm, bạn vừa chìm vào giấc ngủ thì rắc rối bắt đầu xuất hiện.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "establish"
                },
                {
                    "id": "SC02_B2",
                    "image_id": "SC02_I2",
                    "purpose": "Hormone làm giãn cơ thắt thực quản dưới",
                    "anchor": {"vi": {"quote": "Lượng chất béo lớn kích thích giải phóng hormone làm giãn lỏng cơ thắt thực quản dưới.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "detail"
                },
                {
                    "id": "SC02_B3",
                    "image_id": "SC02_I3",
                    "purpose": "Tư thế nằm ngang mất đi sự hỗ trợ của trọng lực",
                    "anchor": {"vi": {"quote": "Khi bạn nằm ở tư thế nằm ngang, axit dạ dày không còn trọng lực giữ lại.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "reveal"
                },
                {
                    "id": "SC02_B4",
                    "image_id": "SC02_I4",
                    "purpose": "Sóng axit tràn ngược lên thực quản",
                    "anchor": {"vi": {"quote": "Từng đợt sóng axit đậm đặc tràn ngược lên cổ họng,", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.3},
                    "tempo": "burst",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "tension"
                },
                {
                    "id": "SC02_B5",
                    "image_id": "SC02_I5",
                    "purpose": "Cảm giác nóng rát ngực trong giấc ngủ",
                    "anchor": {"vi": {"quote": "gây ra cảm giác nóng rát ngực.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "detail"
                },
                {
                    "id": "SC02_B6",
                    "image_id": "SC02_I6",
                    "purpose": "Dạ dày bất lực nhìn axit trào ngược",
                    "anchor": {"vi": {"quote": "gây ra cảm giác nóng rát ngực.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "focus"
                }
            ],
            "tone": "analytical_crisp",
            "narrative_situation": "mechanism_step"
        },

        # SC03: Giờ 2 (01:00) - Khối Mỡ Đậm Đặc Làm Chậm Quá Trình Làm Rỗng Dạ Dày
        {
            "id": "SC03",
            "title": "Khối mỡ đậm đặc làm chậm quá trình làm rỗng dạ dày",
            "purpose": "Triển khai bước 3: cơ chế làm rỗng dạ dày bị đình trệ do lipid đậm đặc",
            "action": "Stomach character vigorously kneads a stubborn thick greasy dough of food while pyloric sphincter stays tightly shut.",
            "setting": "Clean 2D kawaii internal stomach chamber with glowing gastric juice vats on flat white canvas #FFFFFF.",
            "camera": "Semantic camera: dynamic push into the pyloric valve refusing to let thick fatty chyme pass",
            "narration": "Một giờ sáng, chiếc dạ dày phải gồng mình co bóp cơ học liên tục trong đơn độc. Bình thường tinh bột chỉ mất hai tiếng để tiêu hóa, nhưng chất béo đậm đặc thì hoàn toàn khác. Dạ dày phải tiết ra lượng lớn enzyme pepsin và axit clohydric để nghiền nát khối thịt chiên. Quá trình làm rỗng dạ dày bị đình trệ, khiến thức ăn ứ đọng lại suốt đêm dài.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "images": [
                {
                    "id": "SC03_I1",
                    "description": "Clean 2D kawaii medical illustration: night clock pointing to 1:00 AM as peach stomach character #F6C28B rolls up its sleeves with focused determination on flat pure white canvas #FFFFFF with smooth black outline #222222, >=60% negative space.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "flat white canvas, peach stomach character",
                    "change": "stomach rolls up sleeves ready to work at 1:00 AM",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "1:00 SÁNG", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "emphasis_text": "1:00 SÁNG",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Một giờ sáng, chiếc dạ dày phải gồng mình co bóp cơ học liên tục trong đơn độc.",
                        "relation": "context",
                        "source_terms": ["Một giờ sáng"],
                        "visual_terms": ["1:00 AM"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The peach stomach takes a deep breath and readies its tiny arms for heavy churning, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I2",
                    "description": "Clean 2D kawaii medical illustration: stomach walls rippling rhythmically with powerful mechanical peristaltic contraction waves around a giant stubborn grease globule on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC03_I1",
                    "preserve": "flat white canvas, peach stomach character",
                    "change": "stomach contracting muscular walls around greasy globule",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "narrative_situation": "mechanism_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "Một giờ sáng, chiếc dạ dày phải gồng mình co bóp cơ học liên tục trong đơn độc.",
                        "relation": "context",
                        "source_terms": ["co bóp"],
                        "visual_terms": ["peristalsis"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Powerful rippling waves compress the food mass repeatedly with energetic bounce lines, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I3",
                    "description": "Clean 2D kawaii medical illustration: comparison diagram showing a light bread roll digesting in a 2-hour stopwatch versus a heavy fried chicken drumstick stuck inside a 6-hour stopwatch on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC03_I2",
                    "preserve": "flat white canvas, medical diagram styling",
                    "change": "comparison of carbohydrate 2h vs lipid 6h digestion time",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "2 GIỜ VS 6 GIỜ", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "before_after_contrast",
                    "emphasis_text": "2 GIỜ VS 6 GIỜ",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Bình thường tinh bột chỉ mất hai tiếng để tiêu hóa, nhưng chất béo đậm đặc thì hoàn toàn khác.",
                        "relation": "context",
                        "source_terms": ["tinh bột"],
                        "visual_terms": ["contrast"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The bread stopwatch spins quickly to empty while the fried chicken stopwatch crawls painfully slow, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I4",
                    "description": "Clean 2D kawaii medical illustration: peach stomach character using two hand-drawn spray bottles labeled 'Axit HCl' and 'Pepsin' showering the dense food mass with fizzing dissolving droplets on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC03_I3",
                    "preserve": "flat white canvas, peach stomach character",
                    "change": "stomach spraying enzyme and acid spray bottles on chyme",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "Dạ dày phải tiết ra lượng lớn enzyme pepsin và axit clohydric để nghiền nát khối thịt chiên.",
                        "relation": "context",
                        "source_terms": ["pepsin"],
                        "visual_terms": ["enzymes"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Sparkling mist sprays across the greasy chunk, slowly breaking its outer edges into chyme, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I5",
                    "description": "Clean 2D kawaii medical illustration: pyloric sphincter exit valve drawn as a sturdy locked iron gate with a red padlock, blocking the fatty food from entering the duodenum on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC03_I4",
                    "preserve": "flat white canvas, anatomical drawing",
                    "change": "pyloric valve locked shut preventing exit of un-emulsified fat",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "ĐÌNH TRỆ LÀM RỖNG", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "emphasis_text": "ĐÌNH TRỆ LÀM RỖNG",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Quá trình làm rỗng dạ dày bị đình trệ,",
                        "relation": "context",
                        "source_terms": ["đình trệ"],
                        "visual_terms": ["lock"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The locked gate rattles firmly shut as chyme bounces back into the stomach center, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC03_I6",
                    "description": "Clean 2D kawaii medical illustration: peach stomach character #F6C28B sitting on the floor leaning against bloated belly, sweating and sighing heavily amidst dense stagnant food puddles on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC03_I5",
                    "preserve": "flat white canvas, peach stomach character",
                    "change": "stomach sits exhausted amidst stagnant food puddles",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "khiến thức ăn ứ đọng lại suốt đêm dài.",
                        "relation": "context",
                        "source_terms": ["ứ đọng"],
                        "visual_terms": ["stagnant"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The stomach character rests its forehead in its hands while tiny steam puffs drift upward in fatigue, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC03_B1",
                    "image_id": "SC03_I1",
                    "purpose": "Một giờ sáng gồng mình co bóp",
                    "anchor": {"vi": {"quote": "Một giờ sáng, chiếc dạ dày phải gồng mình co bóp cơ học liên tục trong đơn độc.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "establish"
                },
                {
                    "id": "SC03_B2",
                    "image_id": "SC03_I2",
                    "purpose": "Sóng co bóp nhu động cơ học",
                    "anchor": {"vi": {"quote": "Một giờ sáng, chiếc dạ dày phải gồng mình co bóp cơ học liên tục trong đơn độc.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "burst",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "tension"
                },
                {
                    "id": "SC03_B3",
                    "image_id": "SC03_I3",
                    "purpose": "Đối chiếu thời gian tiêu hóa tinh bột và chất béo",
                    "anchor": {"vi": {"quote": "Bình thường tinh bột chỉ mất hai tiếng để tiêu hóa, nhưng chất béo đậm đặc thì hoàn toàn khác.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "before_after_contrast",
                    "camera_intent": "contrast"
                },
                {
                    "id": "SC03_B4",
                    "image_id": "SC03_I4",
                    "purpose": "Tiết enzyme pepsin và axit clohydric",
                    "anchor": {"vi": {"quote": "Dạ dày phải tiết ra lượng lớn enzyme pepsin và axit clohydric để nghiền nát khối thịt chiên.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "detail"
                },
                {
                    "id": "SC03_B5",
                    "image_id": "SC03_I5",
                    "purpose": "Quá trình làm rỗng môn vị bị đình trệ",
                    "anchor": {"vi": {"quote": "Quá trình làm rỗng dạ dày bị đình trệ,", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "reveal"
                },
                {
                    "id": "SC03_B6",
                    "image_id": "SC03_I6",
                    "purpose": "Thức ăn ứ đọng suốt đêm dài",
                    "anchor": {"vi": {"quote": "khiến thức ăn ứ đọng lại suốt đêm dài.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "focus"
                }
            ],
            "tone": "narrative_warm",
            "narrative_situation": "mechanism_step"
        },

        # SC04: Giờ 3 (02:00) - Lời Bình Sắc Bén 1: Đêm Phục Hồi Hóa Bãi Rác Thải (EDITORIAL COMMENTARY)
        {
            "id": "SC04",
            "title": "Lời bình sắc bén: Đêm tái tạo tế bào biến thành bãi rác chuyển hóa",
            "purpose": "Triển khai bước 4: lời bình sắc bén về việc cơ chế autophagy phục hồi tế bào bị phá hủy hoàn toàn",
            "action": "Philosophical editorial visual contrasting natural cellular autophagy cleaning with chaotic industrial waste grinder.",
            "setting": "Clean 2D conceptual stage contrasting cellular repair spa vs broken industrial grinder on flat white canvas #FFFFFF.",
            "camera": "Semantic camera: slow contemplative pan examining broken cellular maintenance machinery",
            "narration": "Hai giờ sáng là thời điểm lẽ ra các tế bào phải được nghỉ ngơi để sửa chữa tổn thương. Thay vì được thư giãn, chiếc dạ dày lúc này biến thành một chiếc máy xay công nghiệp quá tải. Việc ăn khuya khiến cơ chế tự thực bào ban đêm bị gián đoạn hoàn toàn. Đêm phục hồi sinh học quý giá bỗng chốc trở thành một bãi rác thải chuyển hóa ngổn ngang.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "images": [
                {
                    "id": "SC04_I1",
                    "description": "Clean 2D kawaii medical illustration: night clock pointing to 2:00 AM while celestial sparkles illuminate a serene cellular spa room on flat pure white canvas #FFFFFF with smooth black outline #222222, >=60% negative space.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "flat white canvas, 2D kawaii medical aesthetic",
                    "change": "2:00 AM clock over tranquil cellular repair setting",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "2:00 SÁNG", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "emphasis_text": "2:00 SÁNG",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Hai giờ sáng là thời điểm lẽ ra các tế bào phải được nghỉ ngơi để sửa chữa tổn thương.",
                        "relation": "context",
                        "source_terms": ["Hai giờ sáng"],
                        "visual_terms": ["repair"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Soft golden dust particles drift gently through the cellular space, transitioning toward the industrial grinder, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I2",
                    "description": "Clean 2D kawaii medical illustration: cute cells wearing white bandages smiling peacefully under healing green light crosses on flat white canvas #FFFFFF with smooth black outlines #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC04_I1",
                    "preserve": "flat white canvas, kawaii cell styling",
                    "change": "peaceful cells resting under soft green repair crosses",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "has_character": True,
                    "explanation": {
                        "quote": "Hai giờ sáng là thời điểm lẽ ra các tế bào phải được nghỉ ngơi để sửa chữa tổn thương.",
                        "relation": "context",
                        "source_terms": ["tế bào"],
                        "visual_terms": ["cells"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The cells breathe gently in sync as a harsh mechanical shadow cuts across the frame, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I3",
                    "description": "Clean 2D kawaii medical illustration: peach stomach character #F6C28B depicted as a smoking mechanical industrial food grinder with spinning jagged blades and glowing red gears on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC04_I2",
                    "preserve": "flat white canvas, peach stomach character",
                    "change": "stomach drawn as an overloaded smoky industrial grinder",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "MÁY XAY QUÁ TẢI", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "emphasis_text": "MÁY XAY QUÁ TẢI",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Thay vì được thư giãn, chiếc dạ dày lúc này biến thành một chiếc máy xay công nghiệp quá tải.",
                        "relation": "context",
                        "source_terms": ["máy xay"],
                        "visual_terms": ["grinder"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The metal grinder blades spin vigorously spewing gray exhaust puffs into the pristine white air, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I4",
                    "description": "Clean 2D kawaii medical illustration: autophagy cleaning robot mascot holding a broom with its power battery icon flashing empty red 0% on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC04_I3",
                    "preserve": "flat white canvas, kawaii medical elements",
                    "change": "autophagy cleaning robot shut down with battery at zero",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "has_character": True,
                    "explanation": {
                        "quote": "Việc ăn khuya khiến cơ chế tự thực bào ban đêm bị gián đoạn hoàn toàn.",
                        "relation": "context",
                        "source_terms": ["tự thực bào"],
                        "visual_terms": ["autophagy"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The cleaning robot slumps down dejectedly as its broom drops to the floor, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I5",
                    "description": "Clean 2D kawaii medical illustration: piles of un-metabolized lipid sludge and acidic foam cluttering the internal cell floor like an overflowing recycling dump on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC04_I4",
                    "preserve": "flat white canvas, medical cartoon styling",
                    "change": "overflowing metabolic clutter and junk barrels",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "has_character": True,
                    "explanation": {
                        "quote": "Đêm phục hồi sinh học quý giá bỗng chốc trở thành một bãi rác thải chuyển hóa ngổn ngang.",
                        "relation": "context",
                        "source_terms": ["bãi rác"],
                        "visual_terms": ["waste"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The clutter piles build up in height while a small warning sign tilts sideways, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC04_I6",
                    "description": "Clean 2D kawaii medical illustration: maroon liver #A23E48 and peach stomach #F6C28B standing back to back looking weary and disheartened amidst the metabolic mess on flat white canvas #FFFFFF with smooth black outlines #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC04_I5",
                    "preserve": "flat white canvas, organ characters",
                    "change": "liver and stomach back to back looking weary and disheartened",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "BÃI RÁC CHUYỂN HÓA", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "emphasis_text": "BÃI RÁC CHUYỂN HÓA",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Đêm phục hồi sinh học quý giá bỗng chốc trở thành một bãi rác thải chuyển hóa ngổn ngang.",
                        "relation": "context",
                        "source_terms": ["chuyển hóa"],
                        "visual_terms": ["disheartened"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Stomach and Liver sigh in unison as the camera pulls back smoothly to reveal the next phase in the gallbladder, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC04_B1",
                    "image_id": "SC04_I1",
                    "purpose": "Hai giờ sáng thời gian tế bào hồi phục",
                    "anchor": {"vi": {"quote": "Hai giờ sáng là thời điểm lẽ ra các tế bào phải được nghỉ ngơi để sửa chữa tổn thương.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "establish"
                },
                {
                    "id": "SC04_B2",
                    "image_id": "SC04_I2",
                    "purpose": "Các tế bào lẽ ra được thư giãn và tự sửa chữa",
                    "anchor": {"vi": {"quote": "Hai giờ sáng là thời điểm lẽ ra các tế bào phải được nghỉ ngơi để sửa chữa tổn thương.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "detail"
                },
                {
                    "id": "SC04_B3",
                    "image_id": "SC04_I3",
                    "purpose": "Dạ dày hóa thành cỗ máy xay quá tải",
                    "anchor": {"vi": {"quote": "Thay vì được thư giãn, chiếc dạ dày lúc này biến thành một chiếc máy xay công nghiệp quá tải.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "reveal"
                },
                {
                    "id": "SC04_B4",
                    "image_id": "SC04_I4",
                    "purpose": "Cơ chế tự thực bào autophagy bị đình trệ",
                    "anchor": {"vi": {"quote": "Việc ăn khuya khiến cơ chế tự thực bào ban đêm bị gián đoạn hoàn toàn.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "tension"
                },
                {
                    "id": "SC04_B5",
                    "image_id": "SC04_I5",
                    "purpose": "Rác thải chuyển hóa ngổn ngang trong tế bào",
                    "anchor": {"vi": {"quote": "Đêm phục hồi sinh học quý giá bỗng chốc trở thành một bãi rác thải chuyển hóa ngổn ngang.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "detail"
                },
                {
                    "id": "SC04_B6",
                    "image_id": "SC04_I6",
                    "purpose": "Nội tạng mệt mỏi trong bãi rác chuyển hóa",
                    "anchor": {"vi": {"quote": "Đêm phục hồi sinh học quý giá bỗng chốc trở thành một bãi rác thải chuyển hóa ngổn ngang.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "focus"
                }
            ],
            "tone": "reflective_slow",
            "narrative_situation": "editorial_commentary"
        },

        # SC05: Giờ 4 (03:00) - Túi Mật Bật Báo Động Và Điểm Dừng Rà Soát (MID-CTA)
        {
            "id": "SC05",
            "title": "Túi mật cày đêm xà phòng hóa mỡ kèm điểm dừng rà soát",
            "purpose": "Triển khai bước 5: túi mật bơm dịch mật nhũ hóa lipid và mid-cta rà soát bảo vệ dạ dày",
            "action": "Gallbladder pumps dark green bile into duodenum as Liver handles chemical valves, leading to mid-break CTA.",
            "setting": "Clean 2D anatomical biliary duct and gallbladder factory on flat white canvas #FFFFFF.",
            "camera": "Semantic camera: tracking bile injection into duodenum then pulling to friendly reminder card",
            "narration": "Ba giờ sáng, khối dưỡng trấp ngập mỡ bắt đầu tràn xuống tá tràng. Túi mật nhận lệnh co bóp khẩn cấp, bơm từng đợt dịch mật màu xanh thẫm để xà phòng hóa chất béo. Lá gan màu mận thức trắng mở từng van xả hóa chất trong cơn mệt mỏi cùng cực. Nếu bạn hay ăn khuya xong bị nóng cổ họng, hãy lưu video này lại để bảo vệ dạ dày nhé.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "images": [
                {
                    "id": "SC05_I1",
                    "description": "Clean 2D kawaii medical illustration: night clock pointing to 3:00 AM as fatty chyme sloshes into the curved C-loop of the duodenum on flat pure white canvas #FFFFFF with smooth black outline #222222, >=60% negative space.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "flat white canvas, anatomical kawaii drawing",
                    "change": "chyme entering duodenum at 3:00 AM",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "3:00 SÁNG", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "emphasis_text": "3:00 SÁNG",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Ba giờ sáng, khối dưỡng trấp ngập mỡ bắt đầu tràn xuống tá tràng.",
                        "relation": "context",
                        "source_terms": ["Ba giờ sáng"],
                        "visual_terms": ["duodenum"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The chyme stream flows down into the duodenum while a tiny green gallbladder mascot wakes up, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I2",
                    "description": "Clean 2D kawaii medical illustration: cute pear-shaped gallbladder mascot squeezing itself like an accordion, squirting dark emerald-green bile fluid into the fatty mixture on flat white canvas #FFFFFF with smooth black outlines #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC05_I1",
                    "preserve": "flat white canvas, gallbladder mascot",
                    "change": "gallbladder mascot squeezing green bile fluid",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "Túi mật nhận lệnh co bóp khẩn cấp, bơm từng đợt dịch mật màu xanh thẫm để xà phòng hóa chất béo.",
                        "relation": "context",
                        "source_terms": ["Túi mật"],
                        "visual_terms": ["bile"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Vibrant green bile jets spray across the yellow fat clusters, breaking them into tiny micelle droplets, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I3",
                    "description": "Clean 2D kawaii medical illustration: maroon liver character #A23E48 with disheveled hair and heavy eye bags turning a giant industrial valve with a wrench on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC05_I2",
                    "preserve": "flat white canvas, maroon liver character",
                    "change": "maroon liver turning heavy chemical valve in exhaustion",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "GAN BƠM DỊCH MẬT", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "emphasis_text": "GAN BƠM DỊCH MẬT",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Lá gan màu mận thức trắng mở từng van xả hóa chất trong cơn mệt mỏi cùng cực.",
                        "relation": "context",
                        "source_terms": ["Lá gan"],
                        "visual_terms": ["valve"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The maroon liver strains against the metal wheel as green pipes hum with intense fluid pressure, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I4",
                    "description": "Clean 2D kawaii medical illustration: zoomed-in micro view of bile salts surrounding triglyceride lipid molecules, turning large fat blobs into tiny emulsified droplets on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC05_I3",
                    "preserve": "flat white canvas, microscopic doodle aesthetic",
                    "change": "bile salts emulsifying fat into tiny micelle circles",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "để xà phòng hóa chất béo.",
                        "relation": "context",
                        "source_terms": ["xà phòng hóa"],
                        "visual_terms": ["emulsification"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Giant fat globules shatter smoothly into hundreds of tiny floating circles under bile salt action, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I5",
                    "description": "Clean 2D kawaii medical illustration: peach stomach character #F6C28B holding a smartphone with an illuminated ribbon save button icon, gently offering it to the viewer on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC05_I4",
                    "preserve": "flat white canvas, peach stomach character",
                    "change": "stomach holding smartphone with save button icon",
                    "reason": "Mid-CTA beat.",
                    "visible_text": [{"text": "LƯU ĐỂ XEM LẠI", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "mid_break_cta",
                    "emphasis_text": "LƯU ĐỂ XEM LẠI",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Nếu bạn hay ăn khuya xong bị nóng cổ họng, hãy lưu video này lại để bảo vệ dạ dày nhé.",
                        "relation": "context",
                        "source_terms": ["lưu video"],
                        "visual_terms": ["save"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The peach stomach smiles softly and points a wire finger toward the glowing save icon, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC05_I6",
                    "description": "Clean 2D kawaii medical illustration: simple doodle human host sitting up in bed taking a warm sip of water while peach stomach character breathes a sigh of relief on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC05_I5",
                    "preserve": "flat white canvas, doodle human host in blue shirt",
                    "change": "human sipping warm water while stomach relaxes",
                    "reason": "Mid-CTA hold beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "mid_break_cta",
                    "has_character": True,
                    "explanation": {
                        "quote": "Nếu bạn hay ăn khuya xong bị nóng cổ họng, hãy lưu video này lại để bảo vệ dạ dày nhé.",
                        "relation": "context",
                        "source_terms": ["bảo vệ"],
                        "visual_terms": ["water"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The doodle human smiles calmly as the warm water stream cools down the esophageal junction, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC05_B1",
                    "image_id": "SC05_I1",
                    "purpose": "Ba giờ sáng dưỡng trấp tràn xuống tá tràng",
                    "anchor": {"vi": {"quote": "Ba giờ sáng, khối dưỡng trấp ngập mỡ bắt đầu tràn xuống tá tràng.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "establish"
                },
                {
                    "id": "SC05_B2",
                    "image_id": "SC05_I2",
                    "purpose": "Túi mật bơm dịch mật khẩn cấp",
                    "anchor": {"vi": {"quote": "Túi mật nhận lệnh co bóp khẩn cấp, bơm từng đợt dịch mật màu xanh thẫm để xà phòng hóa chất béo.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "tension"
                },
                {
                    "id": "SC05_B3",
                    "image_id": "SC05_I3",
                    "purpose": "Lá gan cày đêm mở van hóa chất",
                    "anchor": {"vi": {"quote": "Lá gan màu mận thức trắng mở từng van xả hóa chất trong cơn mệt mỏi cùng cực.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "detail"
                },
                {
                    "id": "SC05_B4",
                    "image_id": "SC05_I4",
                    "purpose": "Nhũ hóa xà phòng hóa các hạt mỡ",
                    "anchor": {"vi": {"quote": "Túi mật nhận lệnh co bóp khẩn cấp, bơm từng đợt dịch mật màu xanh thẫm để xà phòng hóa chất béo.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mechanism_step",
                    "camera_intent": "reveal"
                },
                {
                    "id": "SC05_B5",
                    "image_id": "SC05_I5",
                    "purpose": "Điểm dừng rà soát Mid-CTA lưu video",
                    "anchor": {"vi": {"quote": "Nếu bạn hay ăn khuya xong bị nóng cổ họng, hãy lưu video này lại để bảo vệ dạ dày nhé.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "mid_break_cta",
                    "camera_intent": "focus"
                },
                {
                    "id": "SC05_B6",
                    "image_id": "SC05_I6",
                    "purpose": "Hành động bảo vệ dạ dày và nghỉ ngơi",
                    "anchor": {"vi": {"quote": "Nếu bạn hay ăn khuya xong bị nóng cổ họng, hãy lưu video này lại để bảo vệ dạ dày nhé.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "mid_break_cta",
                    "camera_intent": "hold"
                }
            ],
            "tone": "narrative_warm",
            "narrative_situation": "mid_break_cta"
        },

        # SC06: Giờ 5 (04:00) - Cơn Sóng Triglyceride Và Nhà Máy Gan Tăng Ca
        {
            "id": "SC06",
            "title": "Cơn lũ axit béo tràn vào máu và gan tổng hợp lipoprotein tỷ trọng thấp",
            "purpose": "Triển khai bước 6: gan tổng hợp VLDL và lipid tích tụ tế bào lúc bốn giờ sáng",
            "action": "Massive influx of free fatty acids enters portal vein as overworked Liver packages VLDL packages.",
            "setting": "Clean 2D hepatic chemical packaging plant with conveyor belts on flat white canvas #FFFFFF.",
            "camera": "Semantic camera: high-speed tracking along portal vein delivery stream into liver parenchyma",
            "narration": "Bốn giờ sáng chính là đỉnh điểm khủng hoảng chuyển hóa của lá gan. Hàng triệu phân tử axit béo tự do từ ruột non ồ ạt tràn vào tĩnh mạch cửa. Nhà máy gan phải vận hành hết công suất để gom mỡ và đóng gói thành lipoprotein tỷ trọng rất thấp. Một phần chất béo không kịp chuyển hóa bắt đầu lắng đọng trực tiếp bên trong các tế bào gan.",
            "requirements": ["R06"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "images": [
                {
                    "id": "SC06_I1",
                    "description": "Clean 2D kawaii medical illustration: night clock showing 4:00 AM glowing with amber warning halos while maroon liver #A23E48 stands in center of factory control room on flat pure white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "flat white canvas, maroon liver character",
                    "change": "4:00 AM clock glowing amber in liver factory control room",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "4:00 SÁNG", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "deep_dive_step",
                    "emphasis_text": "4:00 SÁNG",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Bốn giờ sáng chính là đỉnh điểm khủng hoảng chuyển hóa của lá gan.",
                        "relation": "context",
                        "source_terms": ["Bốn giờ sáng"],
                        "visual_terms": ["crisis"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The clock hands strike 4:00 as warning dials flicker from yellow to orange, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC06_I2",
                    "description": "Clean 2D kawaii medical illustration: wide blue portal vein highway carrying thousands of golden glowing fat droplets surging directly toward the liver on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC06_I1",
                    "preserve": "flat white canvas, vascular schematic drawing",
                    "change": "fat droplets rushing through portal vein highway",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "narrative_situation": "deep_dive_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "Hàng triệu phân tử axit béo tự do từ ruột non ồ ạt tràn vào tĩnh mạch cửa.",
                        "relation": "context",
                        "source_terms": ["tĩnh mạch cửa"],
                        "visual_terms": ["portal vein"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Fast-moving lipid bubbles zoom along the clear blue tube with speed motion streaks, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC06_I3",
                    "description": "Clean 2D kawaii medical illustration: maroon liver character #A23E48 frantically stamping brown shipping boxes labeled 'VLDL' on a rapidly moving factory conveyor belt on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC06_I2",
                    "preserve": "flat white canvas, maroon liver character",
                    "change": "liver stamping VLDL shipping boxes on conveyor belt",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "ĐÓNG GÓI VLDL", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "emphasis_text": "ĐÓNG GÓI VLDL",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Nhà máy gan phải vận hành hết công suất để gom mỡ và đóng gói thành lipoprotein tỷ trọng rất thấp.",
                        "relation": "context",
                        "source_terms": ["VLDL"],
                        "visual_terms": ["conveyor"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The liver character stamps down in rapid succession as labeled boxes speed past on the belt, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC06_I4",
                    "description": "Clean 2D kawaii medical illustration: conveyor belt jamming as too many VLDL boxes pile up, gears smoking and sparking under overloaded torque on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC06_I3",
                    "preserve": "flat white canvas, industrial line art",
                    "change": "conveyor belt jammed with smoking gears",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "deep_dive_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "Nhà máy gan phải vận hành hết công suất",
                        "relation": "context",
                        "source_terms": ["hết công suất"],
                        "visual_terms": ["jam"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Smoke puffs erupt from the jammed cogwheels as boxes tumble onto the factory floor, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC06_I5",
                    "description": "Clean 2D kawaii medical illustration: cross-section of hexagonal liver lobule cells, with yellow fat droplets squeezing into the cytoplasm and crowding the cell nucleus on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC06_I4",
                    "preserve": "flat white canvas, cellular histology drawing",
                    "change": "fat droplets accumulating inside hexagonal hepatocytes",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "MỠ ĐỌNG TẾ BÀO", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "emphasis_text": "MỠ ĐỌNG TẾ BÀO",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Một phần chất béo không kịp chuyển hóa bắt đầu lắng đọng trực tiếp bên trong các tế bào gan.",
                        "relation": "context",
                        "source_terms": ["lắng đọng"],
                        "visual_terms": ["hepatocytes"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Yellow oil droplets expand gradually inside the neat cell chambers, bulging their walls outward, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC06_I6",
                    "description": "Clean 2D kawaii medical illustration: maroon liver character #A23E48 sitting amidst stacked boxes of fat, wiping sweat with a towel, panting heavily on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC06_I5",
                    "preserve": "flat white canvas, maroon liver character",
                    "change": "liver sitting exhausted amidst fat boxes with towel",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "Một phần chất béo không kịp chuyển hóa bắt đầu lắng đọng trực tiếp bên trong các tế bào gan.",
                        "relation": "context",
                        "source_terms": ["tế bào gan"],
                        "visual_terms": ["exhausted"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The maroon liver wipes its forehead as the scene shifts toward the pounding heart, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC06_B1",
                    "image_id": "SC06_I1",
                    "purpose": "Bốn giờ sáng khủng hoảng chuyển hóa",
                    "anchor": {"vi": {"quote": "Bốn giờ sáng chính là đỉnh điểm khủng hoảng chuyển hóa của lá gan.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "establish"
                },
                {
                    "id": "SC06_B2",
                    "image_id": "SC06_I2",
                    "purpose": "Axit béo ồ ạt qua tĩnh mạch cửa",
                    "anchor": {"vi": {"quote": "Hàng triệu phân tử axit béo tự do từ ruột non ồ ạt tràn vào tĩnh mạch cửa.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "burst",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "tension"
                },
                {
                    "id": "SC06_B3",
                    "image_id": "SC06_I3",
                    "purpose": "Đóng gói lipoprotein VLDL",
                    "anchor": {"vi": {"quote": "Nhà máy gan phải vận hành hết công suất để gom mỡ và đóng gói thành lipoprotein tỷ trọng rất thấp.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "detail"
                },
                {
                    "id": "SC06_B4",
                    "image_id": "SC06_I4",
                    "purpose": "Băng chuyền quá tải",
                    "anchor": {"vi": {"quote": "Nhà máy gan phải vận hành hết công suất", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "reveal"
                },
                {
                    "id": "SC06_B5",
                    "image_id": "SC06_I5",
                    "purpose": "Mỡ lắng đọng trong tế bào gan",
                    "anchor": {"vi": {"quote": "Một phần chất béo không kịp chuyển hóa bắt đầu lắng đọng trực tiếp bên trong các tế bào gan.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "detail"
                },
                {
                    "id": "SC06_B6",
                    "image_id": "SC06_I6",
                    "purpose": "Lá gan kiệt sức vì quá tải mỡ",
                    "anchor": {"vi": {"quote": "Một phần chất béo không kịp chuyển hóa bắt đầu lắng đọng trực tiếp bên trong các tế bào gan.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "focus"
                }
            ],
            "tone": "analytical_crisp",
            "narrative_situation": "deep_dive_step"
        },

        # SC07: Giờ 6 (05:00) - Máu Dồn Về Ruột Và Trái Tim Bị Đánh Thức
        {
            "id": "SC07",
            "title": "Hệ mạch tạng dồn máu khiến tim tăng nhịp đập lúc rạng sáng",
            "purpose": "Triển khai bước 7: hệ mạch mạc treo dồn máu và tim đập nhanh ngăn cản hạ huyết áp tự nhiên",
            "action": "Heart character pumps heavily under sympathetic overdrive to supply digestive circulation instead of resting.",
            "setting": "Clean 2D cardiovascular circuit highlighting splanchnic arterial bed on flat white canvas #FFFFFF.",
            "camera": "Semantic camera: pulsing cardiac zoom tracking arterial rush into abdominal aorta",
            "narration": "Năm giờ sáng, khi không gian bên ngoài tĩnh lặng nhất thì bên trong cơ thể lại sôi sục. Để hỗ trợ quá trình tiêu hóa nặng nề, hệ tuần hoàn tạng buộc phải dồn lượng máu khổng lồ về ổ bụng. Trái tim không thể hạ huyết áp để nghỉ ngơi như chu kỳ tự nhiên. Thay vào đó, tim phải đập dồn dập từng nhịp nặng nề xuyên qua lồng ngực.",
            "requirements": ["R07"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "images": [
                {
                    "id": "SC07_I1",
                    "description": "Clean 2D kawaii medical illustration: early dawn clock showing 5:00 AM with soft morning blue tint on flat pure white canvas #FFFFFF with smooth black outline #222222, >=60% negative space.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "flat white canvas, 2D line art",
                    "change": "dawn clock at 5:00 AM in quiet morning room",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "5:00 SÁNG", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "deep_dive_step",
                    "emphasis_text": "5:00 SÁNG",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Năm giờ sáng, khi không gian bên ngoài tĩnh lặng nhất thì bên trong cơ thể lại sôi sục.",
                        "relation": "context",
                        "source_terms": ["Năm giờ sáng"],
                        "visual_terms": ["dawn"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. A gentle dawn gradient rises softly outside the window, while internal veins throb with rapid blood flow, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC07_I2",
                    "description": "Clean 2D kawaii medical illustration: anatomical diagram of the mesenteric circulatory network engorged with bright red blood vessels feeding the stomach and intestines on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC07_I1",
                    "preserve": "flat white canvas, vascular network drawing",
                    "change": "blood vessels engorged and pulsing with red volume",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "DỒN MÁU VỀ BỤNG", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "deep_dive_step",
                    "emphasis_text": "DỒN MÁU VỀ BỤNG",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Để hỗ trợ quá trình tiêu hóa nặng nề, hệ tuần hoàn tạng buộc phải dồn lượng máu khổng lồ về ổ bụng.",
                        "relation": "context",
                        "source_terms": ["tuần hoàn tạng"],
                        "visual_terms": ["mesenteric"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Thick red blood flow pulses swiftly down through the abdominal aorta into the gut network, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC07_I3",
                    "description": "Clean 2D kawaii medical illustration: brave rose heart character #F28C9B wearing running sweatbands, panting with sweat drops while pumping two giant piston handles on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC07_I2",
                    "preserve": "flat white canvas, rose heart character #F28C9B",
                    "change": "heart pumping heavy pistons wearing sweatbands",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "Trái tim không thể hạ huyết áp để nghỉ ngơi như chu kỳ tự nhiên.",
                        "relation": "context",
                        "source_terms": ["Trái tim"],
                        "visual_terms": ["heart"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The rose heart pumps up and down with intense exertion as rhythmic heartbeat sound waves emanate, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC07_I4",
                    "description": "Clean 2D kawaii medical illustration: nocturnal blood pressure chart showing an alert red line staying elevated at 130 instead of dropping down into the healthy green nocturnal dipping zone on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC07_I3",
                    "preserve": "flat white canvas, medical chart styling",
                    "change": "blood pressure chart showing failure to dip nocturnally",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "MẤT TRŨNG HUYẾT ÁP", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "emphasis_text": "MẤT TRŨNG HUYẾT ÁP",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Trái tim không thể hạ huyết áp để nghỉ ngơi như chu kỳ tự nhiên.",
                        "relation": "context",
                        "source_terms": ["huyết áp"],
                        "visual_terms": ["blood pressure"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The red graph line remains high and jagged with warning sparks flashing at its peak, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC07_I5",
                    "description": "Clean 2D kawaii medical illustration: doodle human host in calm-blue shirt sleeping in bed with visible thump-thump vibration lines echoing around the ribcage on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC07_I4",
                    "preserve": "flat white canvas, doodle human host",
                    "change": "human sleeping with vibration waves around chest",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "narrative_situation": "deep_dive_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "Thay vào đó, tim phải đập dồn dập từng nhịp nặng nề xuyên qua lồng ngực.",
                        "relation": "context",
                        "source_terms": ["đập dồn dập"],
                        "visual_terms": ["palpitation"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Thumping vibration ripples pulse outward from the chest with subtle comedic wobble, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC07_I6",
                    "description": "Clean 2D kawaii medical illustration: rose heart character #F28C9B leaning on a stopwatch timer, taking deep breaths beside the weary peach stomach on flat white canvas #FFFFFF with smooth black outlines #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC07_I5",
                    "preserve": "flat white canvas, heart and stomach characters",
                    "change": "heart and stomach leaning on timer catching breath",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "deep_dive_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "Thay vào đó, tim phải đập dồn dập từng nhịp nặng nề xuyên qua lồng ngực.",
                        "relation": "context",
                        "source_terms": ["lồng ngực"],
                        "visual_terms": ["breathing"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Heart catches breath as nerve fibers light up toward the sleeping brain, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC07_B1",
                    "image_id": "SC07_I1",
                    "purpose": "Năm giờ sáng không gian tĩnh lặng",
                    "anchor": {"vi": {"quote": "Năm giờ sáng, khi không gian bên ngoài tĩnh lặng nhất thì bên trong cơ thể lại sôi sục.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "establish"
                },
                {
                    "id": "SC07_B2",
                    "image_id": "SC07_I2",
                    "purpose": "Hệ tuần hoàn tạng dồn lượng máu lớn về ổ bụng",
                    "anchor": {"vi": {"quote": "Để hỗ trợ quá trình tiêu hóa nặng nề, hệ tuần hoàn tạng buộc phải dồn lượng máu khổng lồ về ổ bụng.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "tension"
                },
                {
                    "id": "SC07_B3",
                    "image_id": "SC07_I3",
                    "purpose": "Trái tim gồng mình bơm máu",
                    "anchor": {"vi": {"quote": "Trái tim không thể hạ huyết áp để nghỉ ngơi như chu kỳ tự nhiên.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "detail"
                },
                {
                    "id": "SC07_B4",
                    "image_id": "SC07_I4",
                    "purpose": "Mất trũng huyết áp sinh lý ban đêm",
                    "anchor": {"vi": {"quote": "Trái tim không thể hạ huyết áp để nghỉ ngơi như chu kỳ tự nhiên.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "reveal"
                },
                {
                    "id": "SC07_B5",
                    "image_id": "SC07_I5",
                    "purpose": "Nhịp tim đập dồn dập trong lồng ngực",
                    "anchor": {"vi": {"quote": "Thay vào đó, tim phải đập dồn dập từng nhịp nặng nề xuyên qua lồng ngực.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "burst",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "tension"
                },
                {
                    "id": "SC07_B6",
                    "image_id": "SC07_I6",
                    "purpose": "Trái tim mệt nhoài khi trời sắp sáng",
                    "anchor": {"vi": {"quote": "Thay vào đó, tim phải đập dồn dập từng nhịp nặng nề xuyên qua lồng ngực.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "focus"
                }
            ],
            "tone": "analytical_crisp",
            "narrative_situation": "deep_dive_step"
        },

        # SC08: Giờ 7 (06:00) - Não Bộ Mất Giấc Ngủ Sâu Và Độc Tố Đọng Lại
        {
            "id": "SC08",
            "title": "Tín hiệu thần kinh phế vị báo động cắt vụn giấc ngủ sâu của não",
            "purpose": "Triển khai bước 8: thần kinh phế vị gửi tín hiệu căng tức làm gián đoạn hệ thống glymphatic của não",
            "action": "Vagus nerve sends flashing electrical alerts to Brain character, preventing deep sleep waves and glymphatic clearance.",
            "setting": "Clean 2D cranial chamber showing pink brain character and cerebral spinal fluid canals on flat white canvas #FFFFFF.",
            "camera": "Semantic camera: tracking electrical impulses travelling up the vagal pathway into the cerebrum",
            "narration": "Sáu giờ sáng, tiếng chuông báo thức sắp reo nhưng não bộ vẫn chưa hề được phục hồi. Tín hiệu căng tức từ dây thần kinh phế vị ở dạ dày liên tục dội ngược lên vỏ não. Giấc ngủ sâu sóng chậm bị bẻ gãy thành từng mảnh vụn rời rạc. Hệ thống làm sạch độc tố thần kinh của não bộ bị đình trệ hoàn toàn vì tín hiệu báo động dạ dày.",
            "requirements": ["R08"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "images": [
                {
                    "id": "SC08_I1",
                    "description": "Clean 2D kawaii medical illustration: alarm clock displaying 6:00 AM on bedside table with morning sunbeams entering, doodle human still asleep with tense eyebrows on flat pure white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "flat white canvas, doodle bedroom scene",
                    "change": "6:00 AM clock with tense sleeping human",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "6:00 SÁNG", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "emphasis_text": "6:00 SÁNG",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Sáu giờ sáng, tiếng chuông báo thức sắp reo nhưng não bộ vẫn chưa hề được phục hồi.",
                        "relation": "context",
                        "source_terms": ["Sáu giờ sáng"],
                        "visual_terms": ["alarm"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The alarm hammer vibrates slightly as camera zooms inside the head to the pink brain character, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC08_I2",
                    "description": "Clean 2D kawaii medical illustration: glowing yellow vagus nerve cable transmitting rapid zigzag lightning bolts from the bloated stomach upward into the base of the skull on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC08_I1",
                    "preserve": "flat white canvas, neural pathway line art",
                    "change": "vagus nerve sparking with distress signals from stomach",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "DÂY THẦN KINH PHẾ VỊ", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "deep_dive_step",
                    "emphasis_text": "DÂY THẦN KINH PHẾ VỊ",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Tín hiệu căng tức từ dây thần kinh phế vị ở dạ dày liên tục dội ngược lên vỏ não.",
                        "relation": "context",
                        "source_terms": ["thần kinh phế vị"],
                        "visual_terms": ["vagus nerve"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Lightning bolt sparks zip up the nerve line in rapid sequence, flashing bright yellow, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC08_I3",
                    "description": "Clean 2D kawaii medical illustration: cute round pink brain blob #F4A6A6 wearing a nightcap, surrounded by shattered blue delta-wave sleep graphs falling like broken glass on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC08_I2",
                    "preserve": "flat white canvas, pink brain character #F4A6A6",
                    "change": "brain blob surrounded by broken shattered sleep-wave graphs",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "narrative_situation": "deep_dive_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "Giấc ngủ sâu sóng chậm bị bẻ gãy thành từng mảnh vụn rời rạc.",
                        "relation": "context",
                        "source_terms": ["Giấc ngủ sâu"],
                        "visual_terms": ["delta waves"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Smooth ocean-like delta wave curves crack and shatter into floating jagged fragments, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC08_I4",
                    "description": "Clean 2D kawaii medical illustration: glymphatic drainage pipes around the brain clogged with dark purple metabolite specks, clean cerebrospinal fluid unable to flush on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC08_I3",
                    "preserve": "flat white canvas, brain and glymphatic canal styling",
                    "change": "glymphatic canal pipes clogged with dark debris",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "HỆ GLYMPHATIC TẮC NGHẼN", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "emphasis_text": "HỆ GLYMPHATIC TẮC NGHẼN",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Hệ thống làm sạch độc tố thần kinh của não bộ bị đình trệ hoàn toàn",
                        "relation": "context",
                        "source_terms": ["làm sạch độc tố"],
                        "visual_terms": ["glymphatic"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Clear water pumps stutter to a halt as purple sediment settles into the narrow channels, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC08_I5",
                    "description": "Clean 2D kawaii medical illustration: pink brain blob #F4A6A6 holding a ringing red alarm phone receiver in panic, unable to find silence to clean its mental house on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC08_I4",
                    "preserve": "flat white canvas, pink brain character",
                    "change": "brain blob holding ringing red phone receiver looking stressed",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "deep_dive_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "vì tín hiệu báo động dạ dày.",
                        "relation": "context",
                        "source_terms": ["báo động dạ dày"],
                        "visual_terms": ["phone"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The red telephone cord vibrates with frantic sound waves as the brain covers its ears, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC08_I6",
                    "description": "Clean 2D kawaii medical illustration: pink brain blob #F4A6A6 and peach stomach #F6C28B connected by a tangled knotted telephone cord, looking at each other with mutual fatigue on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC08_I5",
                    "preserve": "flat white canvas, brain and stomach characters",
                    "change": "brain and stomach connected by tangled cord looking weary",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "has_character": True,
                    "explanation": {
                        "quote": "vì tín hiệu báo động dạ dày.",
                        "relation": "context",
                        "source_terms": ["dạ dày"],
                        "visual_terms": ["tangled"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The tangled cord droops between them as the morning sun rises fully on the horizon, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC08_B1",
                    "image_id": "SC08_I1",
                    "purpose": "Sáu giờ sáng não bộ chưa được phục hồi",
                    "anchor": {"vi": {"quote": "Sáu giờ sáng, tiếng chuông báo thức sắp reo nhưng não bộ vẫn chưa hề được phục hồi.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "establish"
                },
                {
                    "id": "SC08_B2",
                    "image_id": "SC08_I2",
                    "purpose": "Thần kinh phế vị truyền tín hiệu căng tức",
                    "anchor": {"vi": {"quote": "Tín hiệu căng tức từ dây thần kinh phế vị ở dạ dày liên tục dội ngược lên vỏ não.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "detail"
                },
                {
                    "id": "SC08_B3",
                    "image_id": "SC08_I3",
                    "purpose": "Giấc ngủ sâu bị bẻ gãy vụn",
                    "anchor": {"vi": {"quote": "Giấc ngủ sâu sóng chậm bị bẻ gãy thành từng mảnh vụn rời rạc.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "burst",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "tension"
                },
                {
                    "id": "SC08_B4",
                    "image_id": "SC08_I4",
                    "purpose": "Hệ thống glymphatic làm sạch độc tố bị đình trệ",
                    "anchor": {"vi": {"quote": "Hệ thống làm sạch độc tố thần kinh của não bộ bị đình trệ hoàn toàn", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "reveal"
                },
                {
                    "id": "SC08_B5",
                    "image_id": "SC08_I5",
                    "purpose": "Não bộ hoảng loạn nhận báo động",
                    "anchor": {"vi": {"quote": "vì tín hiệu báo động dạ dày.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "focus"
                },
                {
                    "id": "SC08_B6",
                    "image_id": "SC08_I6",
                    "purpose": "Sự kiệt quệ chung giữa não và dạ dày",
                    "anchor": {"vi": {"quote": "vì tín hiệu báo động dạ dày.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "deep_dive_step",
                    "camera_intent": "detail"
                }
            ],
            "tone": "narrative_warm",
            "narrative_situation": "deep_dive_step"
        },

        # SC09: Giờ 9 (08:00) - Lời Bình Sắc Bén 2: Mười Lăm Phút Sướng Miệng Đổi Mười Hai Giờ Kiệt Quệ (EDITORIAL COMMENTARY)
        {
            "id": "SC09",
            "title": "Lời bình sắc bén: Mười lăm phút sướng miệng đổi mười hai giờ kiệt quệ",
            "purpose": "Triển khai bước 9: lời bình sắc bén phân tích cái giá đắt đỏ của cơn thèm ăn đêm",
            "action": "Dramatic editorial contrast between fleeting 15-minute midnight pleasure and 12-hour organ depletion.",
            "setting": "Clean 2D balanced scale courtroom on flat white canvas #FFFFFF.",
            "camera": "Semantic camera: slow contemplative tilt examining the tilted imbalance scale",
            "narration": "Tám giờ sáng, bạn thức giấc và tự hỏi vì sao ngủ đủ giấc mà người vẫn mệt lử. Nhiều người thường đổ lỗi cho căng thẳng công việc hay thời tiết thay đổi. Nhưng cái giá đắt nhất của bữa ăn khuya chính là sự kiệt sức của toàn bộ bộ máy chuyển hóa. Mười lăm phút thỏa mãn vị giác đêm qua đã đổi lấy mười hai giờ làm việc kiệt cùng của nội tạng.",
            "requirements": ["R09"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "images": [
                {
                    "id": "SC09_I1",
                    "description": "Clean 2D kawaii medical illustration: morning clock at 8:00 AM as doodle human host sits at office desk clutching heavy forehead with a yawn on flat pure white canvas #FFFFFF with smooth black outline #222222, >=60% negative space.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "flat white canvas, doodle human host in blue shirt",
                    "change": "human at office desk at 8:00 AM yawning and exhausted",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "8:00 SÁNG", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "emphasis_text": "8:00 SÁNG",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Tám giờ sáng, bạn thức giấc và tự hỏi vì sao ngủ đủ giấc mà người vẫn mệt lử.",
                        "relation": "context",
                        "source_terms": ["Tám giờ sáng"],
                        "visual_terms": ["yawn"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The doodle human yawns widely as tiny question mark bubbles pop above its tired head, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC09_I2",
                    "description": "Clean 2D kawaii medical illustration: floating conceptual icons of office deadlines and stormy rain clouds, crossed out by a bold hand-drawn red marker on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC09_I1",
                    "preserve": "flat white canvas, conceptual icons",
                    "change": "work stress and weather icons crossed out in red",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "has_character": True,
                    "explanation": {
                        "quote": "Nhiều người thường đổ lỗi cho căng thẳng công việc hay thời tiết thay đổi.",
                        "relation": "context",
                        "source_terms": ["căng thẳng"],
                        "visual_terms": ["weather"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Red X marks slash decisively across the weather and deadline icons, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC09_I3",
                    "description": "Clean 2D kawaii medical illustration: intricate kawaii internal metabolic engine showing gears, pipes, and liver and stomach mascots steaming with worn-out springs popping out on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC09_I2",
                    "preserve": "flat white canvas, organ machinery styling",
                    "change": "internal metabolic engine steaming with worn-out gears",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "BỘ MÁY CHUYỂN HÓA", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "emphasis_text": "BỘ MÁY CHUYỂN HÓA",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Nhưng cái giá đắt nhất của bữa ăn khuya chính là sự kiệt sức của toàn bộ bộ máy chuyển hóa.",
                        "relation": "context",
                        "source_terms": ["bộ máy chuyển hóa"],
                        "visual_terms": ["engine"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Metal gears turn sluggishly with squeaking friction lines as steam vents continuously, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC09_I4",
                    "description": "Clean 2D kawaii medical illustration: giant mechanical balance scale: on the light high side sits a small plate of fried chicken labeled '15 PHÚT'; on the heavy sunken side sits four exhausted organ mascots labeled '12 GIỜ' on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC09_I3",
                    "preserve": "flat white canvas, balance scale drawing",
                    "change": "balance scale heavily tilted by 12 hours of organ labor",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "15 PHÚT VS 12 GIỜ", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "emphasis_text": "15 PHÚT VS 12 GIỜ",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Mười lăm phút thỏa mãn vị giác đêm qua đã đổi lấy mười hai giờ làm việc kiệt cùng của nội tạng.",
                        "relation": "context",
                        "source_terms": ["Mười lăm phút"],
                        "visual_terms": ["scale"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The balance scale tilts heavily downward on the organ side with a loud thud line, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC09_I5",
                    "description": "Clean 2D kawaii medical illustration: close-up of tired peach stomach #F6C28B and maroon liver #A23E48 leaning against each other on the sunken scale pan, holding tiny handwritten signs reading 'XIN HÃY NGHỈ' on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC09_I4",
                    "preserve": "flat white canvas, organ characters",
                    "change": "stomach and liver holding signs asking for rest",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "has_character": True,
                    "explanation": {
                        "quote": "đã đổi lấy mười hai giờ làm việc kiệt cùng của nội tạng.",
                        "relation": "context",
                        "source_terms": ["kiệt cùng"],
                        "visual_terms": ["plea"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The signs tremble slightly in their stubby hands as empathetic sparkles appear, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC09_I6",
                    "description": "Clean 2D kawaii medical illustration: doodle human host in calm-blue shirt gazing thoughtfully into a bathroom mirror, realizing the true cause of morning fatigue on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC09_I5",
                    "preserve": "flat white canvas, doodle human host",
                    "change": "human looking into mirror with enlightened understanding",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "has_character": True,
                    "explanation": {
                        "quote": "đã đổi lấy mười hai giờ làm việc kiệt cùng của nội tạng.",
                        "relation": "context",
                        "source_terms": ["nội tạng"],
                        "visual_terms": ["mirror"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The human nods in thoughtful resolution as the scene transitions toward actionable solutions, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC09_B1",
                    "image_id": "SC09_I1",
                    "purpose": "Tám giờ sáng mệt mỏi thức dậy",
                    "anchor": {"vi": {"quote": "Tám giờ sáng, bạn thức giấc và tự hỏi vì sao ngủ đủ giấc mà người vẫn mệt lử.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "establish"
                },
                {
                    "id": "SC09_B2",
                    "image_id": "SC09_I2",
                    "purpose": "Đổ lỗi cho căng thẳng hay thời tiết",
                    "anchor": {"vi": {"quote": "Nhiều người thường đổ lỗi cho căng thẳng công việc hay thời tiết thay đổi.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "reveal"
                },
                {
                    "id": "SC09_B3",
                    "image_id": "SC09_I3",
                    "purpose": "Bộ máy chuyển hóa bị kiệt sức",
                    "anchor": {"vi": {"quote": "Nhưng cái giá đắt nhất của bữa ăn khuya chính là sự kiệt sức của toàn bộ bộ máy chuyển hóa.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "detail"
                },
                {
                    "id": "SC09_B4",
                    "image_id": "SC09_I4",
                    "purpose": "Chiếc cân đối chiếu 15 phút và 12 giờ",
                    "anchor": {"vi": {"quote": "Mười lăm phút thỏa mãn vị giác đêm qua đã đổi lấy mười hai giờ làm việc kiệt cùng của nội tạng.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "contrast"
                },
                {
                    "id": "SC09_B5",
                    "image_id": "SC09_I5",
                    "purpose": "Nội tạng cầu xin được nghỉ ngơi",
                    "anchor": {"vi": {"quote": "đã đổi lấy mười hai giờ làm việc kiệt cùng của nội tạng.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "focus"
                },
                {
                    "id": "SC09_B6",
                    "image_id": "SC09_I6",
                    "purpose": "Sự giác ngộ trước gương buổi sáng",
                    "anchor": {"vi": {"quote": "đã đổi lấy mười hai giờ làm việc kiệt cùng của nội tạng.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "editorial_commentary",
                    "camera_intent": "reveal"
                }
            ],
            "tone": "reflective_slow",
            "narrative_situation": "editorial_commentary"
        },

        # SC10: Giờ 11 (10:00) - Quy Tắc Ba Giờ Rỗng Bụng Giúp Giải Phóng Hệ Tiêu Hóa
        {
            "id": "SC10",
            "title": "Quy tắc ba giờ rỗng bụng giúp giải phóng hệ tiêu hóa trước khi ngủ",
            "purpose": "Triển khai bước 10: quy tắc ngón tay cái 3 giờ rỗng bụng và phương án thay thế lành mạnh",
            "action": "Practical rule of thumb demonstration: stopping dinner 3 hours prior and replacing night binge with warm water/milk.",
            "setting": "Clean 2D kawaii kitchen and schedule blueprint on flat white canvas #FFFFFF.",
            "camera": "Semantic camera: clean tutorial layout tracking evening timeline from 7:00 PM dinner to 10:00 PM sleep",
            "narration": "Mười giờ sáng, dạ dày và lá gan mới bắt đầu tạm dọn sạch xong đợt tàn dư cuối cùng. Để chấm dứt vòng lặp kiệt quệ này, bạn chỉ cần ghi nhớ quy tắc ba giờ rỗng bụng. Hãy kết thúc bữa tối ít nhất ba tiếng trước khi đi ngủ để dạ dày kịp rỗng. Nếu đêm muộn quá đói, hãy chọn một cốc nước ấm hoặc nửa cốc sữa ấm thay vì dầu mỡ.",
            "requirements": ["R10"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "images": [
                {
                    "id": "SC10_I1",
                    "description": "Clean 2D kawaii medical illustration: morning clock showing 10:00 AM as peach stomach #F6C28B and maroon liver #A23E48 sweep away the very last dust specks with hand brooms on flat pure white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "flat white canvas, organ mascots",
                    "change": "10:00 AM clock as stomach and liver sweep last dust specks",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "10:00 SÁNG", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "practical_rule_of_thumb",
                    "emphasis_text": "10:00 SÁNG",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Mười giờ sáng, dạ dày và lá gan mới bắt đầu tạm dọn sạch xong đợt tàn dư cuối cùng.",
                        "relation": "context",
                        "source_terms": ["Mười giờ sáng"],
                        "visual_terms": ["broom"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The organ mascots sweep the floor clean and give a high-five, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC10_I2",
                    "description": "Clean 2D kawaii medical illustration: large neat 3-hour banner reading 'QUY TẮC 3 GIỜ RỖNG BỤNG' framed in calm mint green #34D399 on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC10_I1",
                    "preserve": "flat white canvas, clean banner aesthetic",
                    "change": "large neat 3-hour empty stomach rule card",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "QUY TẮC 3 GIỜ", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "practical_rule_of_thumb",
                    "emphasis_text": "QUY TẮC 3 GIỜ",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Để chấm dứt vòng lặp kiệt quệ này, bạn chỉ cần ghi nhớ quy tắc ba giờ rỗng bụng.",
                        "relation": "context",
                        "source_terms": ["quy tắc"],
                        "visual_terms": ["rule"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Green checkmark stars sparkle around the rule card, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC10_I3",
                    "description": "Clean 2D kawaii medical illustration: evening schedule diagram: dinner plate at 7:00 PM, followed by a clear empty stomach zone, and bed icon at 10:00 PM with green checkmarks on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC10_I2",
                    "preserve": "flat white canvas, schedule diagram styling",
                    "change": "7:00 PM dinner to 10:00 PM sleep 3-hour buffer timeline",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "7H TỐI -> 10H ĐÊM", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "practical_rule_of_thumb",
                    "emphasis_text": "7H TỐI -> 10H ĐÊM",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Hãy kết thúc bữa tối ít nhất ba tiếng trước khi đi ngủ để dạ dày kịp rỗng.",
                        "relation": "context",
                        "source_terms": ["ba tiếng"],
                        "visual_terms": ["timeline"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. A green timeline pointer sweeps smoothly from dinner to bedtime, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC10_I4",
                    "description": "Clean 2D kawaii medical illustration: empty clean peach stomach character #F6C28B smiling happily with pink cheeks and a thumbs-up hand on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC10_I3",
                    "preserve": "flat white canvas, peach stomach character",
                    "change": "stomach empty, clean and happy with thumbs-up",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "practical_rule_of_thumb",
                    "has_character": True,
                    "explanation": {
                        "quote": "để dạ dày kịp rỗng.",
                        "relation": "context",
                        "source_terms": ["kịp rỗng"],
                        "visual_terms": ["happy stomach"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The peach stomach does a joyful little wiggle on the spot, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC10_I5",
                    "description": "Clean 2D kawaii medical illustration: doodle human host in kitchen choosing a glass of warm water and a cup of warm milk over greasy fried instant noodles crossed out with a red X on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC10_I4",
                    "preserve": "flat white canvas, doodle human host in blue shirt",
                    "change": "human chooses warm water/milk instead of greasy fried noodles",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "NƯỚC ẤM THAY DẦU MỠ", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "practical_rule_of_thumb",
                    "emphasis_text": "NƯỚC ẤM THAY DẦU MỠ",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Nếu đêm muộn quá đói, hãy chọn một cốc nước ấm hoặc nửa cốc sữa ấm thay vì dầu mỡ.",
                        "relation": "context",
                        "source_terms": ["nước ấm"],
                        "visual_terms": ["warm water"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Gentle steam curls up warmly from the glass of water as the noodles slide offscreen, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC10_I6",
                    "description": "Clean 2D kawaii medical illustration: doodle human host taking a calm sip of warm water, feeling soothing warmth spread gently through the chest on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC10_I5",
                    "preserve": "flat white canvas, doodle human host",
                    "change": "human peacefully sips warm water feeling relaxed",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "narrative_situation": "practical_rule_of_thumb",
                    "has_character": True,
                    "explanation": {
                        "quote": "thay vì dầu mỡ.",
                        "relation": "context",
                        "source_terms": ["dầu mỡ"],
                        "visual_terms": ["calm"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The doodle human smiles with gentle relief as camera transitions into the finale ensemble, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC10_B1",
                    "image_id": "SC10_I1",
                    "purpose": "Mười giờ sáng dọn sạch tàn dư",
                    "anchor": {"vi": {"quote": "Mười giờ sáng, dạ dày và lá gan mới bắt đầu tạm dọn sạch xong đợt tàn dư cuối cùng.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "practical_rule_of_thumb",
                    "camera_intent": "establish"
                },
                {
                    "id": "SC10_B2",
                    "image_id": "SC10_I2",
                    "purpose": "Quy tắc ba giờ rỗng bụng",
                    "anchor": {"vi": {"quote": "Để chấm dứt vòng lặp kiệt quệ này, bạn chỉ cần ghi nhớ quy tắc ba giờ rỗng bụng.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "practical_rule_of_thumb",
                    "camera_intent": "reveal"
                },
                {
                    "id": "SC10_B3",
                    "image_id": "SC10_I3",
                    "purpose": "Kết thúc bữa tối 3 tiếng trước khi ngủ",
                    "anchor": {"vi": {"quote": "Hãy kết thúc bữa tối ít nhất ba tiếng trước khi đi ngủ để dạ dày kịp rỗng.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "practical_rule_of_thumb",
                    "camera_intent": "focus"
                },
                {
                    "id": "SC10_B4",
                    "image_id": "SC10_I4",
                    "purpose": "Dạ dày rỗng và được nghỉ ngơi",
                    "anchor": {"vi": {"quote": "để dạ dày kịp rỗng.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "practical_rule_of_thumb",
                    "camera_intent": "detail"
                },
                {
                    "id": "SC10_B5",
                    "image_id": "SC10_I5",
                    "purpose": "Thay thế bằng nước ấm hoặc sữa ấm",
                    "anchor": {"vi": {"quote": "Nếu đêm muộn quá đói, hãy chọn một cốc nước ấm hoặc nửa cốc sữa ấm thay vì dầu mỡ.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "practical_rule_of_thumb",
                    "camera_intent": "contrast"
                },
                {
                    "id": "SC10_B6",
                    "image_id": "SC10_I6",
                    "purpose": "Cảm giác dễ chịu và bảo vệ cơ thể",
                    "anchor": {"vi": {"quote": "thay vì dầu mỡ.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "fast",
                    "narrative_situation": "practical_rule_of_thumb",
                    "camera_intent": "focus"
                }
            ],
            "tone": "narrative_warm",
            "narrative_situation": "practical_rule_of_thumb"
        },

        # SC11: Giờ 12 (11:00) - Kết Bài Và Lời Nhắn Từ Nội Tạng (CLOSE CTA + ENDCARD)
        {
            "id": "SC11",
            "title": "Đánh thức cơ thể và lời nhắn bảo vệ nội tạng mỗi tối",
            "purpose": "Triển khai bước 11: kết bài hành trình 12 giờ và closing cta lưu video bảo vệ nội tạng",
            "action": "Ensemble organ characters and doodle human host celebrate harmonious health on stage, closing with endcard.",
            "setting": "Clean 2D kawaii medical stage with Stomach, Liver, Heart, and Brain on flat white canvas #FFFFFF.",
            "camera": "Semantic camera: broad celebratory pull-out to full channel branding and endcard",
            "narration": "Mười một giờ trưa hôm sau, hành trình mười hai giờ đầy sóng gió của các cơ quan cuối cùng đã khép lại. Cơ thể bạn không phải là cỗ máy vô cảm, mỗi cơ quan đều có nhịp sinh học cần được tôn trọng. Dạ dày và lá gan nhắn bạn lưu video lại để chăm sóc cơ thể tốt hơn mỗi tối nhé.",
            "requirements": ["R11"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "images": [
                {
                    "id": "SC11_I1",
                    "description": "Clean 2D kawaii medical illustration: clock pointing to 11:00 AM bright midday sun shining through as doodle human stretches arms feeling refreshed after learning the lesson on flat pure white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": None,
                    "preserve": "flat white canvas, doodle human host in blue shirt",
                    "change": "11:00 AM clock with human stretching in midday light",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "11:00 TRƯA - 12 GIỜ", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "outro",
                    "emphasis_text": "11:00 TRƯA - 12 GIỜ",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Mười một giờ trưa hôm sau, hành trình mười hai giờ đầy sóng gió của các cơ quan cuối cùng đã khép lại.",
                        "relation": "context",
                        "source_terms": ["Mười một giờ trưa"],
                        "visual_terms": ["midday"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The doodle human stretches arms wide with energetic motion lines as a warm breeze flows past, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC11_I2",
                    "description": "Clean 2D kawaii medical illustration: 12-hour circular journey map recap showing the clock route from 11 PM grease shock to 11 AM recovery on flat white canvas #FFFFFF with smooth black outlines #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC11_I1",
                    "preserve": "flat white canvas, circular roadmap styling",
                    "change": "circular 12-hour roadmap recap with cute icons",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "outro",
                    "has_character": True,
                    "explanation": {
                        "quote": "hành trình mười hai giờ đầy sóng gió của các cơ quan cuối cùng đã khép lại.",
                        "relation": "context",
                        "source_terms": ["hành trình"],
                        "visual_terms": ["roadmap"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The circular timeline glow pulses once in full circle, concluding the chronological cycle, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC11_I3",
                    "description": "Clean 2D kawaii medical illustration: artistic heart-shaped wreath framing all four cute organ characters: Tim (heart #F28C9B), Dạ Dày (stomach #F6C28B), Gan (liver #A23E48), and Não (brain #F4A6A6) on flat white canvas #FFFFFF.",
                    "character_ids": ["CH01"],
                    "based_on": "SC11_I2",
                    "preserve": "flat white canvas, all four organ characters",
                    "change": "four organ characters framed together in harmony",
                    "reason": "Narration-locked beat.",
                    "visible_text": [{"text": "TÔN TRỌNG CƠ THỂ", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "outro",
                    "emphasis_text": "TÔN TRỌNG CƠ THỂ",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Cơ thể bạn không phải là cỗ máy vô cảm, mỗi cơ quan đều có nhịp sinh học cần được tôn trọng.",
                        "relation": "context",
                        "source_terms": ["nhịp sinh học"],
                        "visual_terms": ["harmony"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The four organs hug each other gently with soft heart-shaped sparkles drifting upward, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC11_I4",
                    "description": "Clean 2D kawaii medical illustration: doodle human host gently patting peach stomach and maroon liver like beloved pets, with happy kawaii blush on their faces on flat white canvas #FFFFFF with smooth black outline #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC11_I3",
                    "preserve": "flat white canvas, human host and organ characters",
                    "change": "human host gently patting stomach and liver affectionately",
                    "reason": "Narration-locked beat.",
                    "visible_text": [],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "narrative_situation": "outro",
                    "has_character": True,
                    "explanation": {
                        "quote": "mỗi cơ quan đều có nhịp sinh học cần được tôn trọng.",
                        "relation": "context",
                        "source_terms": ["tôn trọng"],
                        "visual_terms": ["affection"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. The human smiles warmly while stomach and liver beam with cute blushes, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC11_I5",
                    "description": "Clean 2D kawaii medical illustration: peach stomach #F6C28B and maroon liver #A23E48 holding a glowing ribbon bookmark card labeled 'LƯU LẠI', waving warmly to the audience on flat white canvas #FFFFFF with smooth black outlines #222222.",
                    "character_ids": ["CH01"],
                    "based_on": "SC11_I4",
                    "preserve": "flat white canvas, stomach and liver characters",
                    "change": "stomach and liver holding save bookmark card inviting audience",
                    "reason": "Closing CTA beat.",
                    "visible_text": [{"text": "LƯU VIDEO LẠI NHÉ", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "narrative_situation": "cta_close",
                    "emphasis_text": "LƯU VIDEO LẠI NHÉ",
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Dạ dày và lá gan nhắn bạn lưu video lại để chăm sóc cơ thể tốt hơn mỗi tối nhé.",
                        "relation": "context",
                        "source_terms": ["lưu video"],
                        "visual_terms": ["bookmark"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. Stomach and liver wave both hands cheerfully while a soft green bookmark icon pulses gently, silent visual storytelling, no talking, no lip movement"
                },
                {
                    "id": "SC11_I6",
                    "description": "Clean 2D kawaii medical illustration: grand finale endcard on pure flat solid white canvas #FFFFFF with smooth black outlines #222222: Tim (heart #F28C9B), Dạ Dày (stomach #F6C28B), Gan (liver #A23E48), Não (brain #F4A6A6), and doodle human in calm-blue T-shirt #7FB3D5 all waving together, with bold upper-third text 'CƠ THỂ KỂ', >=60% negative space, no 3D.",
                    "character_ids": ["CH01"],
                    "based_on": "SC11_I5",
                    "preserve": "clean flat white canvas #FFFFFF, complete cast ensemble",
                    "change": "full cast waving in gentle looping hold endcard",
                    "reason": "Endcard frame.",
                    "visible_text": [{"text": "CƠ THỂ KỂ", "placement": "upper_third", "object": "emphasis"}],
                    "kind": "scene",
                    "shot_type": "full_scene",
                    "tempo": "hold",
                    "narrative_situation": "cta_close",
                    "emphasis_text": "CƠ THỂ KỂ",
                    "is_endcard": True,
                    "focus": {"x": 0.5, "y": 0.5},
                    "has_character": True,
                    "explanation": {
                        "quote": "Dạ dày và lá gan nhắn bạn lưu video lại để chăm sóc cơ thể tốt hơn mỗi tối nhé.",
                        "relation": "context",
                        "source_terms": ["chăm sóc cơ thể"],
                        "visual_terms": ["endcard"]
                    },
                    "motion_prompt": "Smooth 2D hand-drawn doodle explainer animation. All characters wave gently in a looping hold on pure white canvas, silent visual storytelling, no talking, no lip movement"
                }
            ],
            "beats": [
                {
                    "id": "SC11_B1",
                    "image_id": "SC11_I1",
                    "purpose": "Mười một giờ trưa hôm sau",
                    "anchor": {"vi": {"quote": "Mười một giờ trưa hôm sau, hành trình mười hai giờ đầy sóng gió của các cơ quan cuối cùng đã khép lại.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "outro",
                    "camera_intent": "establish"
                },
                {
                    "id": "SC11_B2",
                    "image_id": "SC11_I2",
                    "purpose": "Tổng kết vòng tuần hoàn mười hai giờ",
                    "anchor": {"vi": {"quote": "hành trình mười hai giờ đầy sóng gió của các cơ quan cuối cùng đã khép lại.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "outro",
                    "camera_intent": "detail"
                },
                {
                    "id": "SC11_B3",
                    "image_id": "SC11_I3",
                    "purpose": "Tôn trọng nhịp sinh học cơ thể",
                    "anchor": {"vi": {"quote": "Cơ thể bạn không phải là cỗ máy vô cảm, mỗi cơ quan đều có nhịp sinh học cần được tôn trọng.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "outro",
                    "camera_intent": "reveal"
                },
                {
                    "id": "SC11_B4",
                    "image_id": "SC11_I4",
                    "purpose": "Yêu thương và chăm sóc các cơ quan",
                    "anchor": {"vi": {"quote": "mỗi cơ quan đều có nhịp sinh học cần được tôn trọng.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "slow",
                    "narrative_situation": "outro",
                    "camera_intent": "focus"
                },
                {
                    "id": "SC11_B5",
                    "image_id": "SC11_I5",
                    "purpose": "Lời nhắn lưu video để chăm sóc cơ thể tốt hơn",
                    "anchor": {"vi": {"quote": "Dạ dày và lá gan nhắn bạn lưu video lại để chăm sóc cơ thể tốt hơn mỗi tối nhé.", "occurrence": 1}},
                    "effect": "cut",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "normal",
                    "narrative_situation": "cta_close",
                    "camera_intent": "focus"
                },
                {
                    "id": "SC11_B6",
                    "image_id": "SC11_I6",
                    "purpose": "Endcard kết thúc toàn bộ video dài",
                    "anchor": {"vi": {"quote": "Dạ dày và lá gan nhắn bạn lưu video lại để chăm sóc cơ thể tốt hơn mỗi tối nhé.", "occurrence": 1}},
                    "effect": "hold",
                    "focus": {"x": 0.5, "y": 0.5},
                    "tempo": "hold",
                    "narrative_situation": "cta_close",
                    "camera_intent": "hold",
                    "is_endcard": True
                }
            ],
            "tone": "narrative_warm",
            "narrative_situation": "cta_close"
        }
    ]
    return scenes
