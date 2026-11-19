#!/usr/bin/env python3
"""Automated production bundle builder for channel 'co_the_ke' (Cơ Thể Kể).

Channel Niche: Sức khỏe và cơ thể được nhân hóa.
Persona: Người dẫn chuyện khoa học giải phẫu 3D y sinh điềm tĩnh, đáng tin cậy.
Visual: 8K 3D Endoscopic Biomedical Cinematography (profile 'ch_co_the_ke_biomedical_v3' / 'co_the_ke_3d_biomedical_v3').

Builds Schema 3.0 bundles for:
  - YouTube/TikTok Short (short_9x16, <= 8 Flow images, 48-60s target)
  - YouTube Long (long_16x9, 10 chapters / 240+ beats target, with standalone spinoff_shorts)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parents[3]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content.research_story_architect import (  # noqa: E402
    PackagingSpec,
    ResearchedTopic,
    build_scenes_from_story_rows,
    validate_production_bundle,
    write_production_package,
)
from tools.script_cadence_checker import ScriptCadenceChecker  # noqa: E402
from tools.script_hook_scorer import HookScore, score_script  # noqa: E402

from channels.registry import get_channel  # noqa: E402

CHANNEL_ID = "co_the_ke"
DEFAULT_SHORT_JOB = "co-the-ke-week1-9x16"
DEFAULT_LONG_JOB = "co-the-ke-week1-16x9"

# ---------------------------------------------------------------------------
# ANATOMICAL 3D ASSEMBLIES (SSOT for co_the_ke / co_the_ke_3d_biomedical_v3)
# ---------------------------------------------------------------------------


def build_characters() -> List[Dict[str, Any]]:
    """Return 3D biomedical anatomical focal assemblies for endoscopic visual consistency."""
    return [
        {
            "id": "CH01",
            "name": "Hệ Tuần Hoàn & Tim 3D",
            "role": "anatomical_3d_assembly",
            "appearance": (
                "Translucent 3D biomedical volumetric human heart and arterial capillary network "
                "illuminated by pulsing arterial crimson (#EF4444) and clinical cyan (#06B6D4) over deep navy (#0A192F)."
            ),
            "outfit": "Pure anatomical 3D subsurface-scattering biological tissue, zero cartoon eyes or clothing.",
        },
        {
            "id": "CH02",
            "name": "Niêm Mạc Dạ Dày & Hệ Tiêu Hóa 3D",
            "role": "anatomical_3d_assembly",
            "appearance": (
                "Unreal Engine 5 3D translucent human stomach cutaway showing mucosal rugae folds, "
                "gastric acid micro-currents in luminous amber (#F59E0B) and alert crimson (#EF4444)."
            ),
            "outfit": "Clean photorealistic 3D endoscopic organ visualization, zero gore and zero cartoon face.",
        },
        {
            "id": "CH03",
            "name": "Tiểu Thùy Gan & Chuyển Hóa 3D",
            "role": "anatomical_3d_assembly",
            "appearance": (
                "3D electron-microscope hepatic lobule cutaway with oxygenated vascular sinusoids, "
                "glycogen energy granules, and toxin filtration pathways in cyan (#06B6D4) and warm amber (#F59E0B)."
            ),
            "outfit": "Scientific 3D biomedical macro structure on obsidian navy background (#0A192F).",
        },
        {
            "id": "CH04",
            "name": "Vỏ Não & Mạng Synap Thần Kinh 3D",
            "role": "anatomical_3d_assembly",
            "appearance": (
                "Translucent 3D cortical brain cross-section and bioluminescent hippocampal neuron synapses "
                "discharging electric cyan (#06B6D4) signals across cerebrospinal glymphatic channels."
            ),
            "outfit": "Anatomical 3D neural X-ray projection with zero sticky 2D cartoon traits.",
        },
        {
            "id": "CH05",
            "name": "Hình Khối Giải Phẫu X-Quang 3D (Host)",
            "role": "human_xray_subject",
            "appearance": (
                "Photorealistic translucent 3D X-ray human silhouette rim-lit in clinical cyan (#06B6D4) "
                "revealing cervical spine, ribcage, and vascular core against deep biomedical navy (#0A192F)."
            ),
            "outfit": "Translucent diagnostic 3D medical silhouette without flat stickman outlines.",
        },
    ]


# ---------------------------------------------------------------------------
# WEEK 1 TIKTOK SHORT (short_9x16: <= 6 Flow images, 30-45s)
# ---------------------------------------------------------------------------

STORY_WEEK1_SHORT: List[Tuple[str, str, str, str, str, List[Tuple[str, str]]]] = [
    (
        "Cú tát mở đầu với con số 27 cân",
        "A dark clinical 3D biomedical scan environment (#0A192F) illuminated by cyan-blue X-ray light.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            (
                "Nếu bạn cúi đầu nhìn điện thoại, cổ bạn phải gánh hai mươi bảy cân.",
                (
                    "full_scene:CH05|Translucent 3D X-ray human profile bending neck 60 degrees over a phone screen "
                    "while cervical vertebrae glow intense arterial crimson (#EF4444) under compressive stress."
                ),
            ),
        ],
    ),
    (
        "Khối lượng tương đương đứa trẻ tám tuổi",
        "Deep navy biomedical laboratory space (#0A192F) with 3D volumetric biomechanical force vectors.",
        "analytical_crisp",
        "demystifying_truth",
        "empirical_conflict",
        [
            (
                "Nhưng điều bất ngờ là, áp lực này tương đương bạn cõng một đứa trẻ tám tuổi trên vai suốt cả ngày.",
                (
                    "concept_metaphor:CH05|3D volumetric medical X-ray side-view contrasting neutral zero-degree cervical stack "
                    "in calm cyan (#06B6D4) against strained 60-degree disc load in crimson (#EF4444), zero text."
                ),
            ),
        ],
    ),
    (
        "Đốt sống cổ phát tín hiệu cầu cứu",
        "3D endoscopic close-up inside strained cervical discs and stretched trapezius muscle fibers.",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            (
                "Khi đầu nghiêng sáu mươi độ, các đốt sống cổ lập tức phát tín hiệu đau buốt vì cơ bắp bị căng rách.",
                (
                    "concept_metaphor:CH04|Macro 3D Unreal Engine render of compressed intervertebral disc "
                    "pulsing crimson nociceptor nerve spikes toward glowing cyan brainstem tracts."
                ),
            ),
        ],
    ),
    (
        "Lưu lượng máu và oxy giảm sút",
        "3D internal vertebral artery endoscopy with flowing biconcave red blood cells.",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            (
                "Lượng máu dẫn lên não sụt giảm, khiến bạn nhanh chóng hoa mắt và giảm hiệu suất làm việc.",
                (
                    "concept_metaphor:CH01|3D endoscopic look inside constricted vertebral artery where arterial crimson "
                    "red blood cells squeeze slowly through pinched vessel walls toward dimmed brain neurons."
                ),
            ),
        ],
    ),
    (
        "Giải pháp nâng tầm mắt và lời kêu gọi",
        "Clean 3D clinical upright spine alignment studio illuminated in luminous X-ray cyan (#06B6D4).",
        "narrative_warm",
        "tactical_actionable",
        "actionable_resolution",
        [
            (
                "Chỉ cần nâng điện thoại ngang tầm mắt là bạn đã cứu chiếc cổ của mình. "
                "Bạn có hay cúi đầu dùng điện thoại không, chia sẻ cảm giác cổ vai gáy của bạn cùng Cơ Thể Kể nhé?",
                (
                    "full_scene:CH05|Translucent 3D X-ray human silhouette raising smartphone smoothly to eye level as "
                    "cervical spine realigns upright and glows restorative cyan (#06B6D4)."
                ),
            ),
        ],
    ),
]


def build_week1_short_sources() -> List[Dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "Assessment of Stresses in the Cervical Spine Caused by Posture and Position of the Head",
            "reference": "Dr. Kenneth K. Hansraj (2014). Surgical Technology International, 25, 277-279.",
            "facts": [
                "Đầu nghiêng 60 độ khiến đốt sống cổ gánh tải 27 cân.",
                "Trọng lượng đầu người ở tư thế thẳng chỉ khoảng năm cân.",
                "Áp lực cột sống tăng vọt gây thoái hóa đĩa đệm và căng cơ.",
                "Giữ đầu thẳng giúp triệt tiêu hoàn toàn áp lực lên cổ.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Cerebral Blood Flow Hemodynamics During Forward Head Posture in Healthy Young Adults",
            "reference": "Dr. David M. Harrison et al. (2019). Journal of Clinical Medicine, 8(8), 1210.",
            "facts": [
                "Cúi gập cổ làm giảm lượng máu động mạch cấp lên não.",
                "Tuần hoàn máu não suy giảm gây chóng mặt và mất tập trung.",
            ],
        },
    ]


def build_week1_short_topic(topic_title: Optional[str] = None) -> ResearchedTopic:
    """Build week 1 short 9:16 topic (<= 6 Flow images, 5 scenes)."""
    ch = get_channel(CHANNEL_ID)
    title = topic_title or "Vì sao cúi đầu nhìn điện thoại làm đốt sống cổ gánh sức nặng 27 kg?"
    scenes = build_scenes_from_story_rows(
        [(t, s, r) for t, s, _, _, _, r in STORY_WEEK1_SHORT],
        character_id="CH05",
    )
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = STORY_WEEK1_SHORT[i][2]
        sc.spoken_style = STORY_WEEK1_SHORT[i][3]
        sc.narrative_phase = STORY_WEEK1_SHORT[i][4]

    scenes[0].source_ids = ["SRC01"]
    scenes[0].claim_facts = [
        ("cổ bạn phải gánh hai mươi bảy cân", "SRC01", "Đầu nghiêng 60 độ khiến đốt sống cổ gánh tải 27 cân.")
    ]
    scenes[1].source_ids = ["SRC01"]
    scenes[1].claim_facts = [
        ("áp lực này tương đương bạn cõng một đứa trẻ tám tuổi", "SRC01", "Trọng lượng đầu người ở tư thế thẳng chỉ khoảng năm cân.")
    ]
    scenes[2].source_ids = ["SRC01"]
    scenes[2].claim_facts = [
        ("các đốt sống cổ lập tức phát tín hiệu đau buốt", "SRC01", "Áp lực cột sống tăng vọt gây thoái hóa đĩa đệm và căng cơ.")
    ]
    scenes[3].source_ids = ["SRC02"]
    scenes[3].claim_facts = [
        ("Lượng máu dẫn lên não sụt giảm", "SRC02", "Cúi gập cổ làm giảm lượng máu động mạch cấp lên não.")
    ]
    scenes[4].source_ids = ["SRC01"]
    scenes[4].claim_facts = [
        ("nâng điện thoại ngang tầm mắt là bạn đã cứu chiếc cổ của mình", "SRC01", "Giữ đầu thẳng giúp triệt tiêu hoàn toàn áp lực lên cổ.")
    ]

    return ResearchedTopic(
        topic=title,
        audience=ch.audience,
        goal="Giải mã gánh nặng 27kg lên đốt sống cổ khi cúi đầu nhìn điện thoại và hướng dẫn thói quen nâng ngang tầm mắt",
        video_type="science",
        min_duration=30.0,
        max_duration=45.0,
        style=ch.visual.style_description,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=build_week1_short_sources(),
        required_points=[{"id": f"R{i:02d}", "text": t} for i, (t, _, _, _, _, _) in enumerate(STORY_WEEK1_SHORT, 1)],
        characters=build_characters(),
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=True,
        voice="VietNarrator_co_the_ke",
        speed=1.12,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        channel_id=CHANNEL_ID,
        packaging=PackagingSpec(
            youtube_title="Vì Sao Cúi Đầu Khiến Cổ Bạn Gánh Nặng 27 Cân?",
            visual_hook="Nhân vật người que cúi đầu bấm điện thoại với hình ảnh đốt sống cổ chịu tải trọng tương đương đứa trẻ tám tuổi",
            text_overlay="GÁNH NẶNG 27 KG",
            contrast_pair="Nhìn ngang nhẹ tênh vs. Cúi 60 độ gánh 27kg",
            channel_pillar="Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
            funnel_tier="tier_1_broad",
            seo_keywords=["sức khỏe", "cột sống cổ", "cúi đầu dùng điện thoại", "text neck", "cơ thể kể"],
        ),
    )


# ---------------------------------------------------------------------------
# WEEK 1 YOUTUBE LONG (long_16x9: 8 scenes, 24 beats, 3 spinoff shorts)
# ---------------------------------------------------------------------------

STORY_WEEK1_LONG: List[Tuple[str, str, str, str, str, List[Tuple[str, str]]]] = [
    (
        "Cuộc họp khẩn cấp lúc 2 giờ sáng",
        "Dark deep-navy 3D biomedical scan sanctuary (#0A192F) with volumetric volumetric neural alarm pulses.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            (
                "Nếu bạn quyết định thức trắng đêm nay, đây là lúc các cơ quan kích hoạt báo động khẩn.",
                (
                    "full_scene:CH04|3D translucent cortical brain cross-section glowing with arterial crimson (#EF4444) "
                    "stress waves over deep biomedical navy (#0A192F) space at midnight."
                ),
            ),
            (
                "Nhưng điều kinh hoàng nhất không phải là cơn buồn ngủ ập đến.",
                (
                    "concept_metaphor:CH04|Microscopic 3D X-ray camera diving through blood-brain barrier capillary walls "
                    "lit by stark clinical cyan (#06B6D4) and crimson alarm rim lighting."
                ),
            ),
            (
                "Lúc hai giờ sáng, não bộ phát tín hiệu cầu cứu vì protein độc tố bắt đầu tích tụ.",
                (
                    "full_scene:CH04|3D electron-microscope view of dark protein plaque clusters accumulating around strained "
                    "cortical neurons glowing faint crimson (#EF4444), zero text."
                ),
            ),
            (
                "Tim và gan phải gồng mình hoạt động gấp đôi để giữ cơ thể đứng vững.",
                (
                    "full_scene:CH01,CH03|Translucent 3D volumetric human torso cutaway highlighting pulsating heart chambers "
                    "and dense capillary hepatic lobules straining under crimson workload."
                ),
            ),
        ],
    ),
    (
        "Não bộ và hệ thống dọn rác glymphatic bị đình trệ",
        "Translucent 3D cerebrospinal fluid space bathed in restorative cyan (#06B6D4) depth.",
        "analytical_crisp",
        "demystifying_truth",
        "empirical_conflict",
        [
            (
                "Khi bạn ngủ say, hệ thống dọn rác trong não sẽ tự động xả dòng dịch rửa trôi protein độc.",
                (
                    "concept_metaphor:CH04|Luminous clinical cyan (#06B6D4) cerebrospinal fluid surge washing cleanly through "
                    "shrinking astrocyte perivascular channels in smooth 3D endoscopic motion."
                ),
            ),
            (
                "Nhưng nếu bạn thức trắng, van xả dòng làm sạch gần như khép chặt.",
                (
                    "visual_diagram:none|3D biomedical cross-section of tight swollen astrocytes sealing narrow perivascular drains "
                    "in deep obsidian slate (#0F172A) with zero fluid clearance."
                ),
            ),
            (
                "Chất độc beta-amyloid ứ đọng lại từng phút như dòng thải ùn tắc.",
                (
                    "concept_metaphor:CH04|Dense crimson (#EF4444) beta-amyloid protein aggregates clinging to branching neural "
                    "dendrites under moody deep-navy surgical lighting."
                ),
            ),
            (
                "Đây là lý do bạn cảm thấy đầu óc nặng trĩu và mờ mịt sau nửa đêm.",
                (
                    "full_scene:CH04|3D translucent human cranium filled with dim pulsing red hypoxic fog as synaptic "
                    "electric sparks visibly stutter and weaken."
                ),
            ),
        ],
    ),
    (
        "Trái tim tăng tốc trong đêm tĩnh lặng",
        "3D internal cardiology chamber illuminated by arterial crimson (#EF4444) valve motion.",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            (
                "Trong khi đó, hệ tuần hoàn và cơ tim phải nhận lệnh tăng áp liên tục.",
                (
                    "full_scene:CH01|Unreal Engine 5 3D volumetric beating heart racing rapidly inside translucent chest ribs, "
                    "coronary arteries pulsing fierce arterial crimson (#EF4444)."
                ),
            ),
            (
                "Nồng độ hormone cortisol tăng cao kích thích huyết áp nhảy vọt liên tục.",
                (
                    "visual_diagram:none|Macro 3D vascular tunnel showing red blood cell torrents surging past taut arterial "
                    "endothelial walls lit in warm amber (#F59E0B) stress markers."
                ),
            ),
            (
                "Thay vì được nghỉ ngơi hạ nhịp xuống bốn mươi đến năm mươi nhịp mỗi phút,",
                (
                    "concept_metaphor:CH01|Clean 3D anatomical split view contrasting serene cyan (#06B6D4) resting myocardium "
                    "against stressed hyper-active crimson heart wall."
                ),
            ),
            (
                "tim bạn bị ép co bóp dồn dập như thể bạn đang chạy dốc giữa đêm.",
                (
                    "full_scene:CH01|Rapid 3D endoscopic camera racing through turbulent aortic valve leaflets pounding against "
                    "high systolic vascular resistance."
                ),
            ),
        ],
    ),
    (
        "Lá gan kiệt sức trong nhà máy lọc độc",
        "Microscopic 3D hepatic lobule sinusoids in deep biomedical navy (#0A192F).",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            (
                "Ở tầng dưới cơ thể, lá gan đang đối diện một ca trực quá tải.",
                (
                    "full_scene:CH03|Translucent 3D biomedical liver lobule cutaway illuminated by strained crimson (#EF4444) "
                    "bile ducts and frantic metabolic enzyme streams."
                ),
            ),
            (
                "Ba giờ sáng vốn là khung giờ vàng để gan tái tạo tế bào và phân giải mỡ.",
                (
                    "concept_metaphor:CH03|Macro 3D hepatocyte cell network shimmering with regenerative cyan (#06B6D4) repair "
                    "pulses breaking down clean golden glycogen chains."
                ),
            ),
            (
                "Nhưng khi bạn thức, gan buộc phải chuyển hướng điều phối đường huyết khẩn cấp.",
                (
                    "concept_metaphor:CH03|3D metabolic pathway animation redirecting amber (#F59E0B) glucose vesicles "
                    "away from cellular repair toward emergency bloodstream supply."
                ),
            ),
            (
                "Lượng mỡ thừa không được xử lý kịp sẽ bắt đầu lắng đọng âm thầm.",
                (
                    "visual_diagram:none|Microscopic 3D cellular close-up of tiny amber lipid droplets accumulating inside "
                    "liver hepatocyte vacuoles against dark slate #0F172A."
                ),
            ),
        ],
    ),
    (
        "Cơn đói đêm và phản ứng axit dạ dày",
        "3D endoscopic gastric lumen with mucosal folds under clinical rim lighting.",
        "narrative_warm",
        "systemic_friction",
        "lived_friction",
        [
            (
                "Đến bốn giờ sáng, hệ tiêu hóa phát ra tín hiệu đói giả đầy đánh lừa.",
                (
                    "full_scene:CH02|3D translucent human stomach churning empty with crimson (#EF4444) peristaltic contraction waves "
                    "rippling across glistening mucosal folds."
                ),
            ),
            (
                "Hormone ghrelin kích thích cơn thèm ăn tăng vọt gấp rưỡi mức bình thường.",
                (
                    "visual_diagram:none|3D cellular close-up of hormone ghrelin molecules binding greedily to glowing hypothalamic "
                    "receptors in pulsing amber (#F59E0B) and crimson (#EF4444)."
                ),
            ),
            (
                "Dạ dày liên tục thúc ép não tìm kiếm đồ ngọt và tinh bột cay nóng.",
                (
                    "full_scene:CH02|Subsurface 3D X-ray zoom bridging stomach vagus nerve fibers ascending directly into the "
                    "appetite center of the brain in glowing cyan-amber pulses."
                ),
            ),
            (
                "Nếu bạn nuông chiều ăn khuya, axit dịch vị sẽ bào mòn lớp nhầy bảo vệ nhanh hơn.",
                (
                    "concept_metaphor:CH02|3D gastric acid droplets erupting toward strained stomach mucosal barrier eroding subtle "
                    "surface mucus film in arterial crimson warning tones."
                ),
            ),
        ],
    ),
    (
        "Cú sụp đổ năng lượng lúc 6 giờ sáng",
        "3D neural receptor field bathed in stark cold morning biomedical contrast.",
        "analytical_crisp",
        "ironic_exposure",
        "empirical_conflict",
        [
            (
                "Sáu giờ sáng, ánh bình minh ló dạng cũng là lúc cơ thể chạm đáy năng lượng.",
                (
                    "full_scene:CH05|Translucent 3D anatomical silhouette sitting slumped in cold dawn window light as overall "
                    "bioluminescent organ aura dims dramatically."
                ),
            ),
            (
                "Phân tử adenosine gây buồn ngủ đã lấp đầy mọi thụ thể thần kinh trong não.",
                (
                    "concept_metaphor:CH04|Macro 3D neuron membrane where hundreds of crimson-amber (#EF4444/#F59E0B) adenosine "
                    "molecules lock tightly onto neural receptor pockets."
                ),
            ),
            (
                "Một ly cà phê đậm đặc lúc này chỉ là giải pháp đánh lừa tạm thời.",
                (
                    "concept_metaphor:CH04|Crystalline 3D caffeine molecules wedging temporarily into receptor caps while crowded "
                    "adenosine swarms wait directly outside the gate."
                ),
            ),
            (
                "Cơn mệt mỏi nén lại sẽ bùng nổ dữ dội hơn vào đầu giờ chiều.",
                (
                    "full_scene:CH04|Dramatic 3D neural wave crashing through receptors once caffeine clears, flooding cortex "
                    "synapses with heavy deep fatigue pulses."
                ),
            ),
        ],
    ),
    (
        "Hóa giải tổn thương và phục hồi khoa học",
        "Clean serene 3D homeostatic cellular restoration environment in luminous cyan (#06B6D4).",
        "narrative_warm",
        "tactical_actionable",
        "actionable_resolution",
        [
            (
                "Để bù đắp sau một đêm thức trắng, đừng cố lạm dụng nước tăng lực kích thích.",
                (
                    "concept_metaphor:none|3D cardiac artery showing jagged tachycardia spikes calmed back to steady turquoise-cyan "
                    "harmonic pulse once stimulant surge is avoided."
                ),
            ),
            (
                "Hãy bù đắp cho não một giấc ngủ ngắn hai mươi phút vào buổi trưa.",
                (
                    "full_scene:CH04|Serene 3D glowing cortical network clearing ambient static with gentle restorative cyan (#06B6D4) "
                    "theta brainwaves during a brief rest window."
                ),
            ),
            (
                "Uống đủ nước ấm và ăn bữa sáng cân bằng để giảm áp lực cho gan và dạ dày.",
                (
                    "full_scene:CH03|Luminous 3D cellular hydration waves infusing liver lobules and soothing gastric folds "
                    "into calm translucent clinical balance."
                ),
            ),
            (
                "Tối hôm sau, hãy ngủ trước hai mươi ba giờ để chu kỳ sinh học tự hồi phục.",
                (
                    "full_scene:CH01|Coordinated 3D transparent human torso glowing steadily at 60 BPM restful rhythm under "
                    "balanced cyan-blue circadian light."
                ),
            ),
        ],
    ),
    (
        "Lắng nghe phản hồi sinh học của cơ thể",
        "Harmonious 3D anatomical whole-body visualization in crisp cyan (#06B6D4) over deep navy (#0A192F).",
        "narrative_warm",
        "philosophical_anchor",
        "actionable_resolution",
        [
            (
                "Cơ thể bạn là một cỗ máy sinh học kỳ diệu nhưng không phải vô hạn.",
                (
                    "concept_metaphor:none|Wide 3D X-ray silhouette revealing coordinated glowing heart, brain, lungs, and liver "
                    "operating in synchronized cyan luminescence."
                ),
            ),
            (
                "Mỗi giờ bạn thức khuya là một lần các tế bào miễn dịch phải gồng gánh kiệt sức.",
                (
                    "full_scene:CH05|3D vascular overview showing natural killer immune cells slowing down inside darkened capillaries "
                    "when circadian recovery is skipped."
                ),
            ),
            (
                "Chăm sóc sức khỏe bắt đầu từ việc trả lại giờ ngủ cho bộ não và trái tim bên trong.",
                (
                    "full_scene:CH01,CH04|Synchronized 3D brain neural pathways and rhythmic heart valves glowing warm cyan (#06B6D4) "
                    "in deep nocturnal restoration."
                ),
            ),
            (
                "Bạn thường ngủ lúc mấy giờ vào các đêm trong tuần, chia sẻ cùng Cơ Thể Kể ở phần bình luận nhé?",
                (
                    "full_scene:CH05|Balanced upright 3D X-ray anatomical form glowing calm clinical cyan over clean deep navy "
                    "negative space (#0A192F), zero text."
                ),
            ),
        ],
    ),
]


def build_week1_long_sources() -> List[Dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "The Glymphatic System: A Beginner Guide",
            "reference": "Dr. Nadia Aalling Jessen et al. (2015). Neurochemical Research, 40(12), 2583-2599.",
            "facts": [
                "Hệ thống não dọn độc tố hiệu quả nhất khi ngủ say.",
                "Thức trắng đêm làm ứ đọng chất thải thần kinh trong não.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Circadian Disruption and Metabolic Disease",
            "reference": "Dr. Frank A.J.L. Scheer et al. (2009). PNAS, 106(11), 4471-4476.",
            "facts": [
                "Thức khuya làm tăng hormone thèm ăn ghrelin của dạ dày.",
                "Gan bị đảo lộn chu kỳ chuyển hóa mỡ khi thức khuya.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Cardiovascular Consequences of Sleep Deprivation",
            "reference": "Dr. Detlev Ganten & Dr. Thomas Penzel (2018). European Heart Journal, 39(10), 834-843.",
            "facts": [
                "Thiếu ngủ kích hoạt hệ giao cảm làm tăng huyết áp và nhịp tim.",
                "Huyết áp không hạ ban đêm làm tăng nguy cơ tổn thương tim.",
            ],
        },
    ]


def build_week1_long_spinoff_shorts() -> List[Dict[str, Any]]:
    return [
        {
            "id": "SPINOFF_01",
            "hook_title": "Dạ Dày Than Phiền Gì Khi Bạn Ăn Mì Đêm?",
            "opening_hook": "Nếu bạn ăn mì gói lúc nửa đêm, dạ dày sẽ khóc thét.",
            "format_profile": "short_9x16",
            "scene_count": 4,
            "body": [
                {
                    "parent_scene_id": "SC05",
                    "image_id": "SC05_I1",
                    "segment_text": "Đến bốn giờ sáng, hệ tiêu hóa phát ra tín hiệu đói giả đầy đánh lừa.",
                },
                {
                    "parent_scene_id": "SC05",
                    "image_id": "SC05_I2",
                    "segment_text": "Hormone ghrelin kích thích cơn thèm ăn tăng vọt gấp rưỡi mức bình thường.",
                },
                {
                    "parent_scene_id": "SC05",
                    "image_id": "SC05_I3",
                    "segment_text": "Dạ dày liên tục thúc ép não tìm kiếm đồ ngọt và tinh bột cay nóng.",
                },
                {
                    "parent_scene_id": "SC05",
                    "image_id": "SC05_I4",
                    "segment_text": "Nếu bạn nuông chiều ăn khuya, axit dịch vị sẽ bào mòn lớp nhầy bảo vệ nhanh hơn.",
                },
            ],
        },
        {
            "id": "SPINOFF_02",
            "hook_title": "Não Bộ Thức Đêm: Bẫy Độc Tố Chờ Bạn Lúc 2 Giờ",
            "opening_hook": "Nếu bạn thức trắng đêm nay, não bạn không thể dọn rác.",
            "format_profile": "short_9x16",
            "scene_count": 4,
            "body": [
                {
                    "parent_scene_id": "SC02",
                    "image_id": "SC02_I1",
                    "segment_text": "Khi bạn ngủ say, hệ thống dọn rác trong não sẽ tự động xả dòng dịch rửa trôi protein độc.",
                },
                {
                    "parent_scene_id": "SC02",
                    "image_id": "SC02_I2",
                    "segment_text": "Nhưng nếu bạn thức trắng, van xả dòng làm sạch gần như khép chặt.",
                },
                {
                    "parent_scene_id": "SC02",
                    "image_id": "SC02_I3",
                    "segment_text": "Chất độc beta-amyloid ứ đọng lại từng phút như dòng thải ùn tắc.",
                },
                {
                    "parent_scene_id": "SC02",
                    "image_id": "SC02_I4",
                    "segment_text": "Đây là lý do bạn cảm thấy đầu óc nặng trĩu và mờ mịt sau nửa đêm.",
                },
            ],
        },
        {
            "id": "SPINOFF_03",
            "hook_title": "Một Ca Trực Quá Tải Của Lá Gan Khi Thức Khuya",
            "opening_hook": "Nếu bạn thức khuya sau hai giờ, lá gan sẽ quá tải.",
            "format_profile": "short_9x16",
            "scene_count": 4,
            "body": [
                {
                    "parent_scene_id": "SC04",
                    "image_id": "SC04_I1",
                    "segment_text": "Ở tầng dưới cơ thể, lá gan đang đối diện một ca trực quá tải.",
                },
                {
                    "parent_scene_id": "SC04",
                    "image_id": "SC04_I2",
                    "segment_text": "Ba giờ sáng vốn là khung giờ vàng để gan tái tạo tế bào và phân giải mỡ.",
                },
                {
                    "parent_scene_id": "SC04",
                    "image_id": "SC04_I3",
                    "segment_text": "Nhưng khi bạn thức, gan buộc phải chuyển hướng điều phối đường huyết khẩn cấp.",
                },
                {
                    "parent_scene_id": "SC04",
                    "image_id": "SC04_I4",
                    "segment_text": "Lượng mỡ thừa không được xử lý kịp sẽ bắt đầu lắng đọng âm thầm.",
                },
            ],
        },
    ]


def build_week1_long_topic(topic_title: Optional[str] = None) -> Tuple[ResearchedTopic, Dict[str, Any]]:
    """Build week 1 long 16:9 topic and its accompanying omni_plan."""
    ch = get_channel(CHANNEL_ID)
    title = (
        topic_title
        or "Hành Trình 24 Giờ Bên Trong Cơ Thể Khi Bạn Thức Trắng Đêm: Tim, Gan Và Não Bộ Phải Gồng Gánh Ra Sao?"
    )
    scenes = build_scenes_from_story_rows(
        [(t, s, r) for t, s, _, _, _, r in STORY_WEEK1_LONG],
        character_id="CH04",
    )
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = STORY_WEEK1_LONG[i][2]
        sc.spoken_style = STORY_WEEK1_LONG[i][3]
        sc.narrative_phase = STORY_WEEK1_LONG[i][4]

    scenes[1].source_ids = ["SRC01"]
    scenes[1].claim_facts = [
        (
            "hệ thống dọn rác trong não sẽ tự động xả dòng dịch rửa trôi protein độc",
            "SRC01",
            "Hệ thống não dọn độc tố hiệu quả nhất khi ngủ say.",
        )
    ]
    scenes[2].source_ids = ["SRC03"]
    scenes[2].claim_facts = [
        (
            "Nồng độ hormone cortisol tăng cao kích thích huyết áp nhảy vọt liên tục",
            "SRC03",
            "Thiếu ngủ kích hoạt hệ giao cảm làm tăng huyết áp và nhịp tim.",
        )
    ]
    scenes[3].source_ids = ["SRC02"]
    scenes[3].claim_facts = [
        (
            "Lượng mỡ thừa không được xử lý kịp sẽ bắt đầu lắng đọng âm thầm",
            "SRC02",
            "Gan bị đảo lộn chu kỳ chuyển hóa mỡ khi thức khuya.",
        )
    ]
    scenes[4].source_ids = ["SRC02"]
    scenes[4].claim_facts = [
        (
            "Hormone ghrelin kích thích cơn thèm ăn tăng vọt gấp rưỡi mức bình thường",
            "SRC02",
            "Thức khuya làm tăng hormone thèm ăn ghrelin của dạ dày.",
        )
    ]

    spinoff_shorts = build_week1_long_spinoff_shorts()
    omni_plan = {
        "spinoff_shorts": spinoff_shorts,
        "social_copy": {
            "youtube_description": "Giải mã cơ chế sinh học khi thức trắng đêm với sự tham gia của Tim, Dạ Dày, Gan và Não Bộ.",
            "facebook_post": "Hành trình 24 giờ cơ thể khi thức trắng đêm: các cơ quan phải gồng gánh ra sao?",
        },
    }

    topic = ResearchedTopic(
        topic=title,
        audience=ch.audience,
        goal="Giải mã cuộc họp khẩn cấp và cơ chế suy kiệt của các cơ quan khi bạn thức trắng 24 giờ",
        video_type="science",
        min_duration=180.0,
        max_duration=360.0,
        style=ch.visual.style_description,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        sources=build_week1_long_sources(),
        required_points=[{"id": f"R{i:02d}", "text": t} for i, (t, _, _, _, _, _) in enumerate(STORY_WEEK1_LONG, 1)],
        characters=build_characters(),
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=True,
        voice="VietNarrator_co_the_ke",
        speed=1.12,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        channel_id=CHANNEL_ID,
        spinoff_shorts=spinoff_shorts,
        packaging=PackagingSpec(
            youtube_title="24 Giờ Thức Trắng: Tim, Gan Và Não Gánh Ra Sao?",
            visual_hook="Cuộc họp khẩn cấp lúc 2 giờ sáng giữa Não, Tim và Gan trên bàn họp cơ thể với ánh đèn vàng cảnh báo",
            text_overlay="CUỘC HỌP 2H SÁNG",
            contrast_pair="Tỉnh táo giả tạo vs. Kiệt quệ tế bào",
            channel_pillar="Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
            funnel_tier="tier_1_broad",
            seo_keywords=["thức trắng đêm", "tác hại thức khuya", "não bộ thức đêm", "gan thải độc", "cơ thể kể"],
        ),
    )

    return topic, omni_plan


# ---------------------------------------------------------------------------
# EXPORT AND AUDIT FUNCTIONS
# ---------------------------------------------------------------------------


def export_package(
    topic: ResearchedTopic,
    out_dir: Path,
    omni_plan: Optional[Dict[str, Any]] = None,
    system_root: Path = SYS_DIR,
) -> Dict[str, Any]:
    """Export and validate complete Schema 3.0 package to target directory."""
    result = write_production_package(
        output_dir=out_dir,
        topic=topic,
        system_root=system_root,
        omni_plan=omni_plan,
        allow_active=True,
    )

    # Validate draft mirrors
    draft_dir = out_dir / "draft"
    draft_dir.mkdir(parents=True, exist_ok=True)
    outline_data = {
        "outline": [
            {
                "scene_id": sc.scene_id,
                "purpose": sc.purpose,
                "requirements": list(sc.requirements),
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            }
            for sc in topic.scenes
        ]
    }
    (draft_dir / "outline.json").write_text(
        json.dumps(outline_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    content_text = (out_dir / "content.json").read_text(encoding="utf-8")
    (draft_dir / "content.json").write_text(content_text, encoding="utf-8")

    return result


def audit_bundle(pkg_dir: Path, channel_id: str = CHANNEL_ID) -> Dict[str, Any]:
    """Audit production bundle against Schema 3.0 contracts, cadence, and hook scorer."""
    brief_data = json.loads((pkg_dir / "brief.json").read_text(encoding="utf-8"))
    content_data = json.loads((pkg_dir / "content.json").read_text(encoding="utf-8"))
    script_data = json.loads((pkg_dir / "script.json").read_text(encoding="utf-8"))

    # 1. Schema 3.0 Contract Validation
    valid_contracts, errors = validate_production_bundle(
        system_root=SYS_DIR,
        brief_data=brief_data,
        content_data=content_data,
    )

    # 2. Acoustic Cadence Check
    checker = ScriptCadenceChecker(nominal_rate=4.0)
    cadence_res = checker.check_scenes(script_data)

    # 3. Hook Retention Scoring
    format_profile = brief_data.get("format_profile") or "short_9x16"
    narrations = [sc["narration"] for sc in content_data.get("scenes", [])]
    hook_res: HookScore = score_script(narrations, channel_id=channel_id, format_profile=format_profile)

    # 4. Total Images Count
    total_images = sum(len(sc.get("images", [])) for sc in content_data.get("scenes", []))

    return {
        "pkg_dir": str(pkg_dir),
        "format_profile": format_profile,
        "valid_contracts": valid_contracts,
        "contract_errors": errors,
        "cadence_report": cadence_res,
        "hook_score": hook_res.score,
        "hook_checks": hook_res.checks,
        "total_images": total_images,
    }


def build_co_the_ke_bundle(
    format_choice: str = "all",
    out_dir: Optional[Path] = None,
    topic_title: Optional[str] = None,
    job_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Build complete co_the_ke production package(s)."""
    base_dir = out_dir or (SYS_DIR / "runs")
    results: Dict[str, Any] = {}

    build_short = format_choice in ("short_9x16", "9:16", "all", "both", "dual")
    build_long = format_choice in ("long_16x9", "16:9", "all", "both", "dual")

    if build_short:
        j_short = job_name if (job_name and not build_long) else DEFAULT_SHORT_JOB
        target_short = base_dir / j_short
        print(f"\n[*] Đang xây dựng gói TikTok Short (9:16) tại: {target_short}")
        short_topic = build_week1_short_topic(topic_title)
        res_short = export_package(short_topic, target_short)
        audit_short = audit_bundle(target_short)
        results["short_9x16"] = {
            "dir": str(target_short),
            "export": res_short,
            "audit": audit_short,
        }
        print(f"  [+] Hợp đồng Schema 3.0: {'HỢP LỆ' if audit_short['valid_contracts'] else 'LỖI'}")
        print(f"  [+] Số ảnh Flow: {audit_short['total_images']} (ngưỡng: <= 6)")
        print(f"  [+] Điểm Hook: {audit_short['hook_score']} / 100")

    if build_long:
        j_long = job_name if (job_name and not build_short) else DEFAULT_LONG_JOB
        target_long = base_dir / j_long
        print(f"\n[*] Đang xây dựng gói YouTube Long (16:9) tại: {target_long}")
        long_topic, omni_plan = build_week1_long_topic(topic_title)
        res_long = export_package(long_topic, target_long, omni_plan=omni_plan)
        audit_long = audit_bundle(target_long)
        results["long_16x9"] = {
            "dir": str(target_long),
            "export": res_long,
            "audit": audit_long,
        }
        print(f"  [+] Hợp đồng Schema 3.0: {'HỢP LỆ' if audit_long['valid_contracts'] else 'LỖI'}")
        print(f"  [+] Số ảnh Flow: {audit_long['total_images']}")
        print(f"  [+] Số Spinoff Shorts: {len(omni_plan['spinoff_shorts'])}")
        print(f"  [+] Điểm Hook: {audit_long['hook_score']} / 100")

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Automated Schema 3.0 production bundle builder for channel 'co_the_ke'."
    )
    parser.add_argument(
        "--format",
        choices=["short_9x16", "long_16x9", "all"],
        default="all",
        help="Format to build: short_9x16 (TikTok), long_16x9 (YouTube), or all (default)",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Custom topic title (defaults to Week 1 topic in PLAN.md)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=SYS_DIR / "runs",
        help="Root directory for output bundles (default: sys/runs)",
    )
    parser.add_argument(
        "--job-name",
        type=str,
        default=None,
        help="Custom job directory name override",
    )
    args = parser.parse_args()

    print(f"=== BUILDER TỰ ĐỘNG KÊNH: CƠ THỂ KỂ ({CHANNEL_ID}) ===")
    results = build_co_the_ke_bundle(
        format_choice=args.format,
        out_dir=args.out_dir,
        topic_title=args.topic,
        job_name=args.job_name,
    )

    all_valid = True
    for fmt, res in results.items():
        audit = res["audit"]
        if not audit["valid_contracts"]:
            print(f"[FAIL] {fmt} vi phạm hợp đồng: {audit['contract_errors']}")
            all_valid = False
        if fmt == "short_9x16" and audit["total_images"] > 6:
            print(f"[FAIL] short_9x16 có {audit['total_images']} ảnh (vượt quá 6 ảnh Flow)")
            all_valid = False
        if audit["hook_score"] < 70:
            print(f"[FAIL] {fmt} có điểm Hook {audit['hook_score']} (< 70)")
            all_valid = False

    if all_valid:
        print("\n[SUCCESS] Tất cả các gói sản xuất đều hợp lệ 100%!")
        return 0
    else:
        print("\n[ERROR] Có lỗi kiểm định xảy ra.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
