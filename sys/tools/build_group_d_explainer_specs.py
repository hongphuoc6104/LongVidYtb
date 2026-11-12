#!/usr/bin/env python3
"""Group D Explainer Spec Builder & Validator.

Builds the 255-265 Beat Explainer Visual Specs (<slug>_long_explainer_spec.json)
for 5 Mindfulness/Psychology/Philosophy/Empathy channels:
1. chanh_niem_ke (180 SRT cues -> 260 beats)
2. loi_sang_soi (255 SRT cues -> 255 beats)
3. minh_triet_song (180 SRT cues -> 260 beats)
4. tam_tinh_dem (180 SRT cues -> 260 beats)
5. thuong_cho_kheo (255 SRT cues -> 255 beats)

Strict Invariants Enforced:
- 100% Story-Aligned Visual Metaphors, Object Focus, & Comparisons (ZERO boring sitting-in-room shots).
- explainer_type in {'OBJECT_MACRO', 'SPLIT_COMPARISON', 'MECHANISM_CUTAWAY', 'STEP_ENUMERATION', 'CAUSE_EFFECT_DIAGRAM', 'SITUATIONAL_ACTION'}.
- At least 85% must be the first 5 Explainer types.
- reuse_old_image_idx in 20-30% range (~50-65 images reused, ~190-210 new images).
- Concrete English visual prompt (35-65 words) starting with channel signature art style and ending with ', zero text overlay, no watermarks'.
- Exact duration sum matching narration_master.wav to within 0.01s.
- Zero forbidden phrases ('detailed visual narrative illustration', 'Continuing scene continuity', 'person sitting on a porch', 'watching rain').
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT_DIR = Path(__file__).resolve().parents[2]
VIDEO_DIR = ROOT_DIR / "video"

CHANNEL_CONFIGS: Dict[str, Dict[str, Any]] = {
    "chanh_niem_ke": {
        "slug": "chanh_niem_ke",
        "target_beats": 260,
        "split_needed": True,
        "style_prefix": "Cinematic Wabi-Sabi & Zen Sumi-e mindfulness visual,",
        "benchmark": "Pursuit of Wonder / Aperture",
    },
    "loi_sang_soi": {
        "slug": "loi_sang_soi",
        "target_beats": 255,
        "split_needed": False,
        "style_prefix": "Warm golden-hour spiritual parable illustration,",
        "benchmark": "BibleProject / Caravaggio Chiaroscuro",
    },
    "minh_triet_song": {
        "slug": "minh_triet_song",
        "target_beats": 260,
        "split_needed": True,
        "style_prefix": "Classical Stoic & Eastern philosophical ink-and-stone diorama,",
        "benchmark": "Einzelgänger / Daily Stoic",
    },
    "tam_tinh_dem": {
        "slug": "tam_tinh_dem",
        "target_beats": 260,
        "split_needed": True,
        "style_prefix": "Studio Ghibli nocturnal & gentle poetic atmosphere still,",
        "benchmark": "Pursuit of Wonder / Studio Ghibli Nocturnal",
    },
    "thuong_cho_kheo": {
        "slug": "thuong_cho_kheo",
        "target_beats": 255,
        "split_needed": False,
        "style_prefix": "Cinematic 35mm live-action emotional film still,",
        "benchmark": "The School of Life / Cinema Therapy",
    },
}

FORBIDDEN_PHRASES = [
    "detailed visual narrative illustration",
    "continuing scene continuity",
    "person sitting on a porch",
    "watching rain",
    "sitting on a porch watching rain",
]

PROMPT_SUFFIX = ", zero text overlay, no watermarks"


def parse_srt(path: Path) -> List[Dict[str, Any]]:
    """Parse an SRT file into structured cues with precise float timestamps."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    blocks = re.split(r"\n\s*\n", content)
    cues = []
    for b in blocks:
        lines = b.strip().split("\n")
        if len(lines) >= 3:
            idx = int(lines[0])
            m = re.match(
                r"(\d+):(\d+):(\d+)[,\.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,\.](\d+)",
                lines[1],
            )
            if m:
                sh, sm, ss, sms = map(int, m.groups()[:4])
                eh, em, es, ems = map(int, m.groups()[4:])
                start = sh * 3600 + sm * 60 + ss + sms / 1000.0
                end = eh * 3600 + em * 60 + es + ems / 1000.0
                text = " ".join(lines[2:]).strip()
                cues.append(
                    {
                        "index": idx,
                        "start": start,
                        "end": end,
                        "duration": round(end - start, 4),
                        "text": text,
                    }
                )
    return cues


def find_natural_split_point(text: str) -> Tuple[str, str]:
    """Split a multi-clause Vietnamese sentence along a natural grammatical boundary."""
    words = text.split()
    n = len(words)
    if n < 4:
        return text, ""
    mid = n / 2.0

    puncs = [",", ";", ":", "—", "-"]
    candidates = []
    for i, w in enumerate(words[:-1]):
        if any(w.endswith(p) for p in puncs):
            score = abs((i + 1) - mid)
            if i + 1 < 3 or n - (i + 1) < 3:
                score += 5.0
            candidates.append((score, i + 1))
    if candidates:
        candidates.sort()
        idx = candidates[0][1]
        return " ".join(words[:idx]), " ".join(words[idx:])

    conjs = [
        "và",
        "nhưng",
        "mà",
        "để",
        "khi",
        "nếu",
        "thì",
        "rồi",
        "hoặc",
        "vì",
        "bởi",
        "như",
        "cho",
    ]
    for i in range(2, n - 2):
        if words[i].lower() in conjs:
            score = abs(i - mid)
            candidates.append((score, i))
    if candidates:
        candidates.sort()
        idx = candidates[0][1]
        return " ".join(words[:idx]), " ".join(words[idx:])

    idx = n // 2
    return " ".join(words[:idx]), " ".join(words[idx:])


def build_beats_for_channel(slug: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Build the raw aligned beats (255 or 260) with precise durations."""
    cfg = CHANNEL_CONFIGS[slug]
    channel_dir = VIDEO_DIR / f"vn_pilot_{slug}_long"
    srt_path = channel_dir / f"vn_pilot_{slug}_long_16x9.srt"
    aligned_spec_path = channel_dir / f"{slug}_long_aligned_spec.json"

    with open(aligned_spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    cues = parse_srt(srt_path)

    if cfg["split_needed"]:
        sorted_indices = sorted(
            range(len(cues)), key=lambda i: cues[i]["duration"], reverse=True
        )
        split_indices = set(sorted_indices[:80])

        beats_data = []
        for i, c in enumerate(cues):
            if i in split_indices:
                p1, p2 = find_natural_split_point(c["text"])
                w1 = len(p1.split())
                w2 = len(p2.split())
                d1 = round(c["duration"] * (w1 / (w1 + w2)), 4)
                d2 = round(c["duration"] - d1, 4)
                beats_data.append(
                    {
                        "start": c["start"],
                        "duration": d1,
                        "narration": p1,
                        "original_cue_idx": c["index"],
                    }
                )
                beats_data.append(
                    {
                        "start": round(c["start"] + d1, 4),
                        "duration": d2,
                        "narration": p2,
                        "original_cue_idx": c["index"],
                    }
                )
            else:
                beats_data.append(
                    {
                        "start": c["start"],
                        "duration": c["duration"],
                        "narration": c["text"],
                        "original_cue_idx": c["index"],
                    }
                )
    else:
        beats_data = [
            {
                "start": c["start"],
                "duration": c["duration"],
                "narration": c["text"],
                "original_cue_idx": c["index"],
            }
            for c in cues
        ]

    return beats_data, spec


def assign_chapter_info(
    start_sec: float, chapters: List[Dict[str, Any]]
) -> Tuple[int, str]:
    """Find chapter index (1-based) and title for a timestamp."""
    for ch in chapters:
        if start_sec >= ch["start_sec"] - 0.05 and start_sec < ch["end_sec"] - 0.05:
            return ch["chapter_index"], ch["title"]
    return chapters[-1]["chapter_index"], chapters[-1]["title"]


def assign_explainer_type(beat_idx_in_chapter: int, narration: str) -> str:
    """Assign a pedagogically varied explainer type ensuring >= 85% first 5 types."""
    t = narration.lower()
    if any(
        k in t
        for k in [
            "thứ nhất",
            "thứ hai",
            "thứ ba",
            "bước một",
            "bước hai",
            "bước ba",
            "ba câu hỏi",
            "ba bài học",
            "ba bước",
            "ba điều",
            "lời thứ",
        ]
    ):
        return "STEP_ENUMERATION"
    if any(
        k in t
        for k in [
            "thay vì",
            "trái ngược",
            "khác biệt",
            "hai mảnh",
            "hai nửa",
            "một bên",
            "trong khi",
            "đối đầu",
            "đối chiếu",
            "so với",
            "hai góc nhìn",
            "hai phản ứng",
            "chứ không phải",
            "không phải",
        ]
    ):
        return "SPLIT_COMPARISON"
    if any(
        k in t
        for k in [
            "bộ não",
            "sinh học",
            "hệ thần kinh",
            "về mặt sinh học",
            "cơ chế",
            "khoảng trống",
            "vòng lặp",
            "não bộ",
            "thần kinh",
            "tầng sâu",
            "giải phẫu",
            "phản xạ",
            "cấu trúc",
            "bên trong",
        ]
    ):
        return "MECHANISM_CUTAWAY"
    if any(
        k in t
        for k in [
            "bắt nguồn",
            "khiến cho",
            "dẫn đến",
            "hậu quả",
            "nguyên nhân",
            "kết quả",
            "tạo nên",
            "biến thành",
            "sinh sôi",
            "hao mòn",
            "đổ thêm dầu",
            "làm bừng sáng",
            "đưa bạn",
            "kéo theo",
        ]
    ):
        return "CAUSE_EFFECT_DIAGRAM"

    cycle = [
        "OBJECT_MACRO",
        "OBJECT_MACRO",
        "SPLIT_COMPARISON",
        "MECHANISM_CUTAWAY",
        "OBJECT_MACRO",
        "CAUSE_EFFECT_DIAGRAM",
        "SPLIT_COMPARISON",
        "OBJECT_MACRO",
        "STEP_ENUMERATION",
        "SITUATIONAL_ACTION",
        "OBJECT_MACRO",
        "SPLIT_COMPARISON",
        "MECHANISM_CUTAWAY",
        "OBJECT_MACRO",
        "CAUSE_EFFECT_DIAGRAM",
        "SPLIT_COMPARISON",
        "OBJECT_MACRO",
        "STEP_ENUMERATION",
        "OBJECT_MACRO",
        "SITUATIONAL_ACTION",
        "SPLIT_COMPARISON",
        "MECHANISM_CUTAWAY",
        "OBJECT_MACRO",
        "CAUSE_EFFECT_DIAGRAM",
        "OBJECT_MACRO",
        "SPLIT_COMPARISON",
        "OBJECT_MACRO",
        "STEP_ENUMERATION",
    ]
    return cycle[beat_idx_in_chapter % len(cycle)]


def assign_camera_motion(explainer_type: str, beat_idx: int) -> str:
    """Return appropriate zero-snap camera motion for the explainer type."""
    if explainer_type in [
        "MECHANISM_CUTAWAY",
        "STEP_ENUMERATION",
        "CAUSE_EFFECT_DIAGRAM",
    ]:
        return "hold"
    motions = ["push_in", "pan_right", "zoom_in", "pan_left", "hold"]
    return motions[beat_idx % len(motions)]


def assemble_clean_prompt(prefix: str, body: str) -> str:
    """Assemble a clean prompt, enforcing word count [35, 65] and correct suffix."""
    b = body.strip().rstrip(".,")
    prompt = f"{prefix.strip()} {b}{PROMPT_SUFFIX}"
    prompt = re.sub(r"\s+", " ", prompt).strip()

    if len(prompt.split()) < 38:
        padding = "gentle ambient lighting, peaceful contemplative atmosphere, balanced artistic framing, serene depth of field"
        prompt = f"{prefix.strip()} {b}, {padding}{PROMPT_SUFFIX}"
        prompt = re.sub(r"\s+", " ", prompt).strip()

    if len(prompt.split()) > 62:
        prefix_words = prefix.strip().split()
        suffix_words = PROMPT_SUFFIX.strip().split()
        allowed_body_words = 60 - len(prefix_words) - len(suffix_words)
        trimmed_body = " ".join(b.split()[:allowed_body_words]).rstrip(".,")
        prompt = f"{prefix.strip()} {trimmed_body}{PROMPT_SUFFIX}"
        prompt = re.sub(r"\s+", " ", prompt).strip()

    return prompt


# ==============================================================================
# CHANNEL-SPECIFIC PROMPT LIBRARIES
# ==============================================================================

CHANH_NIEM_KE_THEMES: Dict[int, Dict[str, str]] = {
    1: {
        "OBJECT_MACRO": "Macro close-up shot of a dark ceramic bowl brimming with clear water, a single trembling droplet hovering above the surface tension on dark cedar wood, soft natural sidelight, gentle water ripples",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side showing a full tea cup overflowing with tension vs Right side showing an empty glazed ceramic bowl resting peacefully, balanced zen lighting",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram illustrating an overloaded human mind: chaotic tangled black ink threads resolving into smooth parallel lines of breath awareness, serene dark slate background",
        "STEP_ENUMERATION": "Three-step sequential enumeration displayed on textured washi paper: Step one notice sensory tension, Step two exhale completely, Step three return to present stillness, delicate bamboo brushwork",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram demonstrating how mental worry projects phantom storms onto reality, while grounding awareness immediately dissolves unnecessary panic, clean sumi-e aesthetic",
        "SITUATIONAL_ACTION": "A mindful figure seated in tranquil contemplation on an aged cedar floor, soft diffused morning mist entering through open shoji screen, grounded posture, serene presence",
    },
    2: {
        "OBJECT_MACRO": "Macro close-up shot of a prehistoric stone tool resting beside an ancient bronze signal beacon, warm amber firelight glowing on weathered rough stone texture, historical antiquity",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side showing ancient survival brain reacting to distant jungle predator vs Right side showing modern mind reacting to harmless digital screen notification",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram of human cranial neural pathways: evolutionary amygdala threat alarm firing in red sparks then soothed by prefrontal cortex in golden light",
        "STEP_ENUMERATION": "Three-step sequential enumeration: Step one survival threat triggered, Step two conscious recognition of safety, Step three deactivation of biological panic alarm, clean minimalist layout",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how evolutionary survival reflexes mistakenly amplify everyday workplace pressures into catastrophic existential threats, clear explanatory graphics",
        "SITUATIONAL_ACTION": "A calm observer standing quietly in the mountain forest, gentle mist swirling around ancient pine trunks, observing distant clouds without fear or reactive agitation",
    },
    3: {
        "OBJECT_MACRO": "Macro close-up shot of an iron arrow striking a polished round bronze shield, sparks deflecting away while the central golden core remains unblemished, crisp metallic contrast",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side showing impulsive angry retort erupting into jagged red spikes vs Right side showing a measured three-second conscious pause in harmonious blue ripples",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram illustrating the three-second space between external stimulus and human choice: Viktor Frankl freedom interval depicted as a glowing golden threshold",
        "STEP_ENUMERATION": "Three-step sequential enumeration on aged parchment: Step one receive external words, Step two pause for three conscious heartbeats, Step three choose response with equanimity",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how taking three seconds of silence defuses escalating hostility and preserves inner emotional sovereignty, balanced ink wash design",
        "SITUATIONAL_ACTION": "A peaceful practitioner taking a slow measured breath before responding, gentle morning light illuminating composed facial micro-expressions, stillness and dignity",
    },
    4: {
        "OBJECT_MACRO": "Macro close-up shot of a white-knuckled clenched fist squeezing dry river sand, fine golden grains rapidly cascading out between fingers down onto aged dark slate",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side tightly gripped fist losing all sand through pressure vs Right side open relaxed palm holding a generous mound of sand securely",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram analyzing the paradox of control: excessive psychological grasping causing friction and immediate loss versus non-attachment preserving stability",
        "STEP_ENUMERATION": "Three-step sequential enumeration: Step one identify rigid expectation, Step two unclench physical fingers, Step three allow events to unfold naturally like river water",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram demonstrating how fighting uncontrollable external outcomes breeds exhaustion, while surrender to reality generates spontaneous resilience and ease",
        "SITUATIONAL_ACTION": "A relaxed hand resting gently on a sunlit wooden tabletop, fingers uncurled and peaceful, warm late afternoon sunlight washing across natural timber grain",
    },
    5: {
        "OBJECT_MACRO": "Macro close-up shot of a solid heavy brass nautical anchor resting firmly in fine white sand on the serene sea floor, dappled turquoise ocean sunlight playing across metal",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side rapid shallow chest breathing depicted in cold agitated blue vs Right side deep slow diaphragmatic breathing radiating warm golden light",
        "MECHANISM_CUTAWAY": "Anatomical cutaway diagram of human lungs and vagus nerve: prolonged slow exhalation activating parasympathetic nervous system and slowing racing cardiac rhythm in soothing amber light",
        "STEP_ENUMERATION": "Three-step sequential breathing sequence: Step one gentle inhalation through nostrils, Step two micro-pause at full expansion, Step three long unhurried warm exhalation",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how three mindful breaths chemically downregulate stress hormones and re-anchor consciousness in the immediate physical present",
        "SITUATIONAL_ACTION": "A single stick of sandalwood incense burning in a miniature celadon holder, a slender unmoving thread of fragrant smoke rising perfectly straight into tranquil room air",
    },
    6: {
        "OBJECT_MACRO": "Macro close-up shot of a supple green bamboo stalk bending gracefully under heavy mountain rain, raindrops glistening along emerald nodes without causing any fracture",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side rigid stiff dry branch snapping under gale-force winds vs Right side flexible bamboo bending low and springing back unharmed",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram contrasting radical acceptance with passive resignation: acceptance depicted as a firm springboard launching clear intelligent action",
        "STEP_ENUMERATION": "Three-step sequential enumeration: Step one acknowledge what has occurred, Step two cease futile denial, Step three direct energy toward constructive next step",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram illustrating how ceasing resistance to unchangeable past events immediately frees up eighty percent of cognitive problem-solving bandwidth",
        "SITUATIONAL_ACTION": "A calm traveler standing beside a swift mountain stream, watching river water effortlessly part around a giant dark granite boulder and re-converge downstream",
    },
    7: {
        "OBJECT_MACRO": "Macro close-up shot of traditional wooden sandals stepping softly onto deep green forest moss, individual droplets of morning dew clinging to velvety moss spores",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side frantic person with downward gaze glued to glowing smartphone vs Right side unhurried walker looking up at cathedral-like forest canopy",
        "MECHANISM_CUTAWAY": "Neurobiological cutaway diagram demonstrating attention restoration theory: natural forest fractals reducing sensory overload and rejuvenating prefrontal cortex capacity",
        "STEP_ENUMERATION": "Three-step sequential enumeration: Step one store digital devices in drawer, Step two step outside into open air, Step three walk without destination or time limit",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how thirty minutes of aimless walking in natural surroundings restores mental acuity and lowers blood pressure naturally",
        "SITUATIONAL_ACTION": "A peaceful figure walking slowly along an ancient cedar trail dappled with early morning sunbeams, breathing in crisp mountain air and fragrant pine resin",
    },
    8: {
        "OBJECT_MACRO": "Macro close-up shot of hands carefully washing a rustic glazed ceramic tea bowl with warm clear water, gentle steam rising from the earthenware surface",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side chaotic cluttered desk covered with loose papers and tangled wires vs Right side clean minimal cedar table holding one ceramic vase",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram linking external physical environment to internal mental bandwidth: visual clutter competing for working memory resources versus clean negative space",
        "STEP_ENUMERATION": "Three-step sequential decluttering enumeration: Step one clear one single square foot, Step two wipe surface with damp cloth, Step three savor the spacious silence",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how mindful physical cleaning of immediate surroundings acts as a direct psychological catalyst for inner emotional order",
        "SITUATIONAL_ACTION": "A steaming ceramic mug of freshly brewed green tea resting on a clean woven bamboo mat, gentle afternoon sunbeam highlighting pure unadorned simplicity",
    },
    9: {
        "OBJECT_MACRO": "Macro close-up shot of a bamboo calligraphy brush dipped in rich black sumi ink writing three introspective questions on handmade mulberry washi paper",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side runaway catastrophic worry spiral vs Right side disciplined three-question evaluation cutting through illusion with sharp clarity",
        "MECHANISM_CUTAWAY": "Cognitive mechanism cutaway diagram illustrating the three self-inquiry filters: Filter one locus of control, Filter two five-year timeline perspective, Filter three immediate actionable micro-step",
        "STEP_ENUMERATION": "Three-step sequential enumeration: Question one Is this in my control? Question two Will this matter in five years? Question three What is my next smallest step?",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how writing down worries on paper externalizes emotional distress and converts abstract dread into concrete manageable tasks",
        "SITUATIONAL_ACTION": "A person setting down a wooden fountain pen beside a leather journal, pausing to sip warm water from a glass tumbler with a calm and grounded expression",
    },
    10: {
        "OBJECT_MACRO": "Macro close-up shot of an antique Japanese kintsugi ceramic bowl, delicate fractures lovingly mended with shimmering veins of pure twenty-four karat gold lacquer",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side turbulent dark ripples on a stormy pond vs Right side completely calm mirror-smooth water reflecting the bright evening star",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram of the inner sanctuary: exterior worldly chaos kept outside by strong boundaries while inner citadel maintains steady warmth and stillness",
        "STEP_ENUMERATION": "Three-step sequential evening closure: Step one release the finished day, Step two cultivate heartfelt gratitude, Step three welcome restful restorative sleep",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how a daily mindfulness practice creates an unshakeable reservoir of inner peace that remains intact through all life changes",
        "SITUATIONAL_ACTION": "Hands resting peacefully in lap in dhyana meditation mudra, gentle evening candlelight illuminating serene relaxed posture against quiet wabi-sabi backdrop",
    },
}

LOI_SANG_SOI_THEMES: Dict[int, Dict[str, str]] = {
    1: {
        "OBJECT_MACRO": "Macro close-up shot of calloused weathered agrarian hands gently cupping a handful of plump golden wheat grains under warm golden hour sunlight",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side dark fertile tilled loam welcoming seeds vs Right side hard compacted wagon road where seeds bounce harmlessly off dry stone",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram showing the four biblical soils in horizontal cross-section: roadside crust, rocky limestone, thorny bramble, and rich humus earth",
        "STEP_ENUMERATION": "Four-step sequential enumeration depicting the four spiritual terrains: Path one wayside, Path two shallow rock, Path three choking thorns, Path four fertile loam",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram demonstrating how the identical seed produces wildly divergent outcomes purely based on the receptive condition of the receiving soil",
        "SITUATIONAL_ACTION": "An ancient agrarian sower standing at the edge of a vast sun-drenched field, broad arm swung wide as golden seeds catch late afternoon light in mid-air",
    },
    2: {
        "OBJECT_MACRO": "Macro close-up shot of a hard-packed wagon dirt path showing dry cracked earth crust with deep wheel ruts and scattered unabsorbed golden seeds",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side black raven with gleaming feathers swooping down to seize seeds vs Right side farmer watching with sorrowful patience",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram of superficial hearing: truth bouncing off hardened psychological cynicism without penetrating even a millimeter into conscious awareness",
        "STEP_ENUMERATION": "Three-step sequential enumeration of the wayside mind: Step one truth heard superficially, Step two immediate distraction arrives, Step three seed stolen before germination",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how chronic cynicism and defensive emotional numbness harden the heart until no transformative seed can enter",
        "SITUATIONAL_ACTION": "A solitary traveler walking past dry trampled roadside dust under harsh blinding daylight, looking down at barren ground where nothing can take root",
    },
    3: {
        "OBJECT_MACRO": "Macro close-up shot of a pale limestone rock ledge covered by a paper-thin layer of powdery soil, a fragile green sprout wilting under fierce sun",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side shallow sprout withering with burned roots on white stone vs Right side deep taproot anchoring several feet underground in moist loam",
        "MECHANISM_CUTAWAY": "Cross-section cutaway diagram of the rocky terrain: microscopic root tips hitting an impenetrable slab of subterranean bedrock and curling backward in heat",
        "STEP_ENUMERATION": "Three-step sequential enumeration: Step one explosive emotional enthusiasm, Step two midday sun of hardship rises, Step three rapid collapse due to rootlessness",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how shallow enthusiasm without disciplined inner character inevitably falters under the very first trial of adversity",
        "SITUATIONAL_ACTION": "A gardener kneeling beside a rocky outcrop, tenderly examining a sun-scorched seedling whose roots could not penetrate the hidden underground stone shelf",
    },
    4: {
        "OBJECT_MACRO": "Macro close-up shot of sharp jagged briars and creeping thorny vines tightly encircling a young green wheat stalk, sharp prickles pressing against tender stem",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side choked plant suffocated in dark thorny thicket vs Right side open wheat field bathed in generous unrestricted golden sunshine",
        "MECHANISM_CUTAWAY": "Botanical mechanism cutaway diagram showing aggressive weed root systems stealing nitrogen, water, and sunlight from the struggling agricultural crop",
        "STEP_ENUMERATION": "Three-step sequential enumeration: Step one material worries creep in silently, Step two competition chokes focus, Step three potential harvest rendered completely sterile",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram illustrating how obsessive pursuit of wealth and chronic anxiety over status strangle spiritual fruitfulness in modern life",
        "SITUATIONAL_ACTION": "A farmer using sharp iron pruning shears to cut back a dense thicket of invasive thorny brambles, sweat glistening on brow in golden afternoon light",
    },
    5: {
        "OBJECT_MACRO": "Macro close-up shot of rich dark loamy soil teeming with organic moisture, a sturdy green wheat stalk anchoring deep fibrous white subterranean root systems",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side a single struggling grain ear yielding few seeds vs Right side a magnificent golden sheaf bowing under thirty, sixty, hundredfold harvest",
        "MECHANISM_CUTAWAY": "Biological cutaway diagram of fertile soil ecology: mycorrhizal fungi and moist humus delivering rich minerals directly to robust flourishing plant taproots",
        "STEP_ENUMERATION": "Three-step sequential harvest enumeration: Step thirtyfold return in steady diligence, Step sixtyfold return in patient love, Step hundredfold return in selfless wisdom",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram demonstrating how a patient, humble, and receptive human heart consistently transforms truth into abundant blessings for community",
        "SITUATIONAL_ACTION": "An elderly farmer standing waist-deep in a ripe golden wheat field at twilight, gently running open palms across heavy nodding grain heads with deep gratitude",
    },
    6: {
        "OBJECT_MACRO": "Macro close-up shot of a heavy woven wicker seed bag filled with selected golden wheat grains, tied with rustic hemp rope against an aged olive wood bench",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side a stingy hoarder counting grains in dark cellar vs Right side generous sower flinging seeds freely across all lands",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram illustrating universal grace: the sun shining impartially and the rain falling equally upon the just and unjust alike",
        "STEP_ENUMERATION": "Three-step sequential enumeration of the sower: Step one unconditional giving, Step two respect for soil autonomy, Step three unshakeable trust in final harvest",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how sharing wisdom without prejudice or judgment maximizes the probability of finding fertile hearts anywhere",
        "SITUATIONAL_ACTION": "A sower striding across rolling agrarian hills against a radiant sunrise sky, casting seeds with wide sweeping arm movements in serene confidence",
    },
    7: {
        "OBJECT_MACRO": "Macro close-up shot of an antique brass compass and an open leather-bound journal resting on a rustic oak study desk in warm directional amber light",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side modern distracted urban commuter surrounded by digital noise vs Right side contemplative reader sitting quietly with illuminated text",
        "MECHANISM_CUTAWAY": "Psychological cutaway diagram mapping the four modern mindsets: cynical defensive wall, impulsive trend-chaser, materialistic worrier, and centered reflective sage",
        "STEP_ENUMERATION": "Four-step diagnostic self-examination: Step one examine distraction level, Step two test root depth, Step three prune toxic anxieties, Step four cultivate daily stillness",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how regular self-examination prevents fertile ground from slowly degenerating into hardened wayside or thorny weed patch",
        "SITUATIONAL_ACTION": "A thoughtful individual looking out a library window into quiet courtyard garden, reflecting deeply on personal life priorities in golden late afternoon sun",
    },
    8: {
        "OBJECT_MACRO": "Macro close-up shot of an ancient forged iron plow blade slicing cleanly through sun-baked earth, turning up moist dark crumbly subsoil in fragrant clods",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side stubborn neglected field hardened like concrete vs Right side newly plowed field with deep dark furrows ready for spring rain",
        "MECHANISM_CUTAWAY": "Soil restoration cutaway diagram: aeration of compacted clay through mechanical plowing, removal of subterranean boulders, and enrichment with organic compost",
        "STEP_ENUMERATION": "Three-step soil renovation sequence: Step one break the hard crust with repentance, Step two pry out the hidden rocks of resentment, Step three uproot thorns of greed",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how intentional psychological labor and emotional vulnerability can transform even the most barren life into fertile ground",
        "SITUATIONAL_ACTION": "Two farmers working together in cooperative harmony, lifting a heavy jagged limestone rock out of a plowed furrow and carrying it to field boundary",
    },
    9: {
        "OBJECT_MACRO": "Macro close-up shot of a single green seed sprouting underground in warm dark soil, tiny white root hairs spreading out while pale green cotyledon arches upward",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side impatient human demanding instant fruit today vs Right side wise nature quietly nurturing invisible root growth for weeks underground",
        "MECHANISM_CUTAWAY": "Chronological time-lapse cutaway diagram of germination: seed coat softening in moisture, radicle anchoring downward before plumule breaches surface toward sunlight",
        "STEP_ENUMERATION": "Three timeless agricultural lessons: Lesson one respect natural gestation rhythms, Lesson two protect fragile beginnings, Lesson three focus on soil health over harvest metrics",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how cultivating patience and daily faithfulness produces sustainable spiritual fruit that endures across generations",
        "SITUATIONAL_ACTION": "A grandfather and young child kneeling together beside a garden bed, gently patting moist earth over newly planted seeds with smiles of hopeful anticipation",
    },
    10: {
        "OBJECT_MACRO": "Macro close-up shot of a handcrafted terracotta water pitcher pouring a delicate crystalline stream of spring water over a thriving young green wheat seedling",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side parched cracked desert soil under relentless drought vs Right side lush irrigated garden flourishing with abundance and life",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram of a transformed soul: deep interconnected root network anchoring spiritual stability while golden canopy provides shade and sustenance",
        "STEP_ENUMERATION": "Three-step closing blessing: Step one guard the fertile soil of the heart, Step two water seeds of kindness daily, Step three share the harvest freely with all",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how nurturing good seeds within oneself ripples outward to cultivate peace, compassion, and flourishing in the broader world",
        "SITUATIONAL_ACTION": "An agrarian family gathering around a rustic wooden harvest table laden with warm freshly baked bread, thanking the earth under warm golden lantern light",
    },
}

MINH_TRIET_SONG_THEMES: Dict[int, Dict[str, str]] = {
    1: {
        "OBJECT_MACRO": "Macro close-up shot of a weathered Roman bronze coin and imperial seal wax resting on rough oak planking beside a flickering tallow candle, moody chiaroscuro lighting",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side howling winter blizzard whipping against canvas tent vs Right side Marcus Aurelius sitting in tranquil composure writing Meditations",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram of the Stoic mental citadel: external barbarian siege arrows falling harmlessly outside high stone battlements of the rational mind",
        "STEP_ENUMERATION": "Three-step frontier reflection sequence: Step one recognize physical adversity, Step two master internal emotional judgment, Step three execute duty without complaint",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how separating external events from personal value judgments preserves unshakable inner peace even in military warfare",
        "SITUATIONAL_ACTION": "Marcus Aurelius dipping reed pen into iron gall ink in soldier tent at northern border, tallow candle illuminating resolute weathered features and graying beard",
    },
    2: {
        "OBJECT_MACRO": "Macro close-up shot of an ancient brass balance scale: one pan weighed down by rainy clouds and insults, the other holding an unwavering golden oil flame",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side frantic mind tormented by uncontrollable public opinion vs Right side grounded Stoic focused strictly on personal moral choices",
        "MECHANISM_CUTAWAY": "Concentric circle cutaway diagram of Epictetus Dichotomy of Control: outer dashed circle of uncontrollables (fame, wealth, health) vs inner golden circle of controllables (will, action)",
        "STEP_ENUMERATION": "Three-step Stoic decision filter: Step one Is this within my direct control? Step two If not, release concern immediately, Step three If yes, act with excellence",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how attempting to control external opinions produces chronic misery, while mastering personal choices creates invulnerability",
        "SITUATIONAL_ACTION": "A philosopher standing serenely among marble Roman columns, watching stormy clouds roll past in the distance without losing personal dignity or calm",
    },
    3: {
        "OBJECT_MACRO": "Macro close-up shot of a roaring hearth fire consuming dry dead oak branches, transforming rough rotten wood into radiant white heat and glowing crimson embers",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side victim cursing the sudden winter freeze vs Right side wise Stoic feeding fallen timber to hearth fire with profound gratitude",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram illustrating Amor Fati: obstacle entering psychological furnace and converting directly into fuel for virtuous character development",
        "STEP_ENUMERATION": "Three-step Amor Fati sequence: Step one accept reality as it is, Step two refuse self-pity, Step three extract wisdom and strength from the misfortune",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how loving one's fate eliminates regret, neutralizes bitterness, and empowers purposeful action in any crisis",
        "SITUATIONAL_ACTION": "An artisan blacksmith holding glowing hot iron on an anvil, hammer poised in mid-air, using intense flame to temper raw metal into unbreakable blade",
    },
    4: {
        "OBJECT_MACRO": "Macro close-up shot of monumental carved granite coastal fortress tower standing completely motionless while ferocious ocean breakers crash in white spray at base",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side fragile wooden hut swept away by coastal tide vs Right side ancient granite lighthouse guiding ships safely through storm",
        "MECHANISM_CUTAWAY": "Architectural cutaway diagram of the Inner Citadel: thick granite walls of reason protecting the central sacred chamber of moral conscience from all worldly storms",
        "STEP_ENUMERATION": "Three-step construction of the Inner Citadel: Step one lay foundation of honesty, Step two erect walls of self-discipline, Step three install roof of cosmic perspective",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how regular retreat into the inner citadel during crisis prevents emotional burnout and preserves rational clarity",
        "SITUATIONAL_ACTION": "A disciplined soldier standing guard at the fortress parapet at twilight, gaze steady on the horizon, unbothered by cold wind whipping armor cloak",
    },
    5: {
        "OBJECT_MACRO": "Macro close-up shot of a delicately carved ivory skull resting beside a bronze hourglass with fine black sand trickling through its glass neck, dark moody sidelight",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side arrogant general reveling in fleeting earthly triumph vs Right side weathered skull crowned with a withered laurel wreath",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram of Memento Mori: mortal hourglass filtering out trivial vanity and petty grudges to highlight only essential virtuous actions",
        "STEP_ENUMERATION": "Three-step mortality meditation: Step one remember earthly transience, Step two forgive past grievances, Step three live today with utmost integrity as if last",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram demonstrating how constant awareness of mortality dissolves superficial fears and deepens gratitude for the present moment",
        "SITUATIONAL_ACTION": "A philosopher placing a dried laurel leaf inside an ancient leather volume, pausing in quiet reflection while looking up at star-strewn night sky",
    },
    6: {
        "OBJECT_MACRO": "Macro close-up shot of an uncarved rough block of white Carrara marble with sculptor iron chisel and wooden mallet resting on stone chips, classical atelier",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side turbulent glass cylinder of muddy river silt vs Right side identical glass after hours of stillness, crystal clear with sediment settled",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram illustrating the Taoist Pu (uncarved block): chipping away societal conditioning and greedy desires to reveal original pure human nature",
        "STEP_ENUMERATION": "Three-step purification sequence: Step one allow agitated thoughts to settle, Step two chisel away vanity, Step three rest in natural unadorned simplicity",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how non-action (Wu Wei) and inner quietness naturally restore intellectual clarity without forced mental strain",
        "SITUATIONAL_ACTION": "A master stone sculptor blowing white marble dust off a newly carved classical relief, revealing smooth serene contours of an antique philosophical countenance",
    },
    7: {
        "OBJECT_MACRO": "Macro close-up shot of an open Roman parchment scroll pinned to a dark mahogany desk by a heavy bronze lion paperweight, early morning windowlight",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side naive person outraged by difficult coworkers vs Right side prepared Stoic greeting difficult personalities with calm compassion",
        "MECHANISM_CUTAWAY": "Psychological mechanism cutaway diagram of the premeditatio malorum: mental rehearsal of daily friction innoculating emotional state against surprise and indignation",
        "STEP_ENUMERATION": "Three-step morning preparation: Step one anticipate arrogance and treachery, Step two remember shared human kinship, Step three refuse to be corrupted by anger",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how realistic morning mental preparation neutralizes resentment and transforms interpersonal friction into patience practice",
        "SITUATIONAL_ACTION": "An emperor tying sandal straps at dawn in military tent, looking out at mist-covered camp with calm resolve, ready to serve his people through duty",
    },
    8: {
        "OBJECT_MACRO": "Macro close-up shot of an antique brass celestial armillary sphere with concentric brass rings rotating smoothly around a polished central sphere of lapis lazuli",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side narrow perspective of petty office dispute vs Right side cosmic view from above showing Earth as a tiny blue pebble in dark universe",
        "MECHANISM_CUTAWAY": "Astronomical cutaway diagram illustrating the View from Above: expanding visual scale from individual human to city, continent, planet, and boundless cosmos",
        "STEP_ENUMERATION": "Three-step perspective elevation: Step one step out of immediate ego, Step two view situation from eagle altitude, Step three measure problem against eternity",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how adopting the cosmic viewpoint shrinks personal troubles to microscopic scale and dissolves ego-driven suffering",
        "SITUATIONAL_ACTION": "An astronomer adjusting a brass astrolabe on a high stone terrace under a vast canopy of glittering stars, serene night wind stirring classical tunic",
    },
    9: {
        "OBJECT_MACRO": "Macro close-up shot of heavy forged steel blacksmith tongs gripping a red-hot iron horseshoe on an anvil, hammer sparks scattering into shadowy forge",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side soft unhardened iron bending under minimal pressure vs Right side tempered folded steel withstanding immense force without damage",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram of philosophical training (Askesis): voluntary daily discomfort building psychological immunity against luxury and unexpected loss",
        "STEP_ENUMERATION": "Three-step character tempering sequence: Step one practice voluntary simplicity, Step two resist petty temptations, Step three strengthen moral resolve through action",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how philosophy practiced as daily athletic mental training produces enduring resilience under real-world crises",
        "SITUATIONAL_ACTION": "A Stoic practitioner taking a cold bath at dawn, stepping out with invigorated breath and clear mind, unbothered by temporary physical discomfort",
    },
    10: {
        "OBJECT_MACRO": "Macro close-up shot of an extinguished tallow candle on an imperial desk, a delicate wisp of gray smoke curling into the cool dawn light as sun rises outside",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side fearful soul trembling before future unknowns vs Right side peaceful Stoic stepping into dawn with unshakeable dignity",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram of a life lived in accordance with nature: harmony between reason, duty, and the cosmic order of the universe",
        "STEP_ENUMERATION": "Three-step daily mandate: Step one love what must be done, Step two treat all beings with justice, Step three maintain cheerfulness through all circumstance",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how embodying Stoic wisdom transforms ordinary human existence into an enduring monument of courage and tranquility",
        "SITUATIONAL_ACTION": "Marcus Aurelius stepping out of imperial tent into crisp dawn air, looking over mist-covered river with calm gentle smile, ready for the duties of the day",
    },
}

TAM_TINH_DEM_THEMES: Dict[int, Dict[str, str]] = {
    1: {
        "OBJECT_MACRO": "Macro close-up shot of an antique brass mechanical clock on a wooden mantelpiece, brass pendulum ticking softly in warm golden lamplight against midnight blue room",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side frantic daytime avenue jammed with honking traffic vs Right side quiet midnight street washed in gentle blue moonlight",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway of nocturnal winding down: sensory input diminishing as city sleeps, allowing auditory and nervous systems to decompress naturally",
        "STEP_ENUMERATION": "Three-step nighttime transition: Step one close the curtains on city lights, Step two turn off fluorescent bulbs, Step three light a single warm amber candle",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how embracing midnight silence provides the necessary neurological sanctuary for emotional self-repair",
        "SITUATIONAL_ACTION": "A solitary figure in soft pajamas looking out a high apartment window at sleeping city rooftops, cradling a warm ceramic mug in two hands with gentle smile",
    },
    2: {
        "OBJECT_MACRO": "Macro close-up shot of a delicate porcelain smiling theatrical mask resting face-up on a rustic wooden nightstand beside a warm glowing amber lamp",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side person wearing rigid polite smiling mask in office crowd vs Right side same person in pajamas with authentic relaxed face at home",
        "MECHANISM_CUTAWAY": "Psychological mechanism cutaway diagram analyzing social facade exhaustion: energy expended maintaining persona versus healing ease of authentic self-acceptance",
        "STEP_ENUMERATION": "Three-step unmasking sequence: Step one unfasten the social expectations, Step two place the mask gently on table, Step three exhale and be completely yourself",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how shedding artificial social demands at night prevents chronic identity depletion and restores genuine self-esteem",
        "SITUATIONAL_ACTION": "A person gently splashing warm water on face in soft bathroom light, wiping away fatigue with a fluffy towel, gazing softly into mirror with compassionate eyes",
    },
    3: {
        "OBJECT_MACRO": "Macro close-up shot of a small weathered wooden rowboat with oars resting inside, drifting peacefully without effort on a glassy dark river reflecting Milky Way stars",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side rower frantically rowing upstream against churning rapids vs Right side boat drifting effortlessly under benevolent starlight",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram of surrender: releasing struggle against life flow and trusting the buoyancy of deep waters to support your journey",
        "STEP_ENUMERATION": "Three-step nighttime surrender: Step one lay down the heavy oars, Step two lie back and look at the constellations, Step three let the river carry you safely",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how releasing constant daily struggle allows subconscious emotional equilibrium to restore itself automatically",
        "SITUATIONAL_ACTION": "A dreamer resting comfortably in bed with hands folded over blanket, watching gentle moonbeams paint soft silver rectangles across bedroom floorboards",
    },
    4: {
        "OBJECT_MACRO": "Macro close-up shot of a sleek modern smartphone resting face-down on a dark walnut nightstand, screen completely dark and dark glass casing silent",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side screen glowing with endless feeds and comparison traps vs Right side open window revealing deep indigo night sky and silver crescent moon",
        "MECHANISM_CUTAWAY": "Cognitive cutaway diagram of social comparison detox: disconnecting from digital validation loops to quiet amygdala hyper-vigilance and restore peaceful self-worth",
        "STEP_ENUMERATION": "Three-step digital boundary sequence: Step one flip phone face down, Step two place device beyond arm reach, Step three reclaim your quiet personal sovereignty",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how putting away digital comparison at night eliminates phantom inadequacy and fosters deep restorative sleep",
        "SITUATIONAL_ACTION": "A person pulling a plush down duvet up over shoulders in cozy bed, smiling softly at the peaceful darkness, feeling grateful for the quiet sanctuary",
    },
    5: {
        "OBJECT_MACRO": "Macro close-up shot of a bare winter deciduous tree silhouette standing quietly in deep snow under glowing crescent moon, roots resting peacefully underground",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side frantic summer branch pushing premature leaves in frost vs Right side dormant winter tree saving vital sap in underground roots",
        "MECHANISM_CUTAWAY": "Botanical biological cutaway diagram of dormancy: trees conserving vital sugars in subterranean root systems during winter night to prepare for spring blossom",
        "STEP_ENUMERATION": "Three-step seasonal wisdom: Step one honor the fallow winter periods, Step two allow rest without guilt, Step three trust that spring blossoms will arrive on time",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how acknowledging human need for rest and downtime prevents irreversible psychological burnout and preserves vitality",
        "SITUATIONAL_ACTION": "A person sitting curled up in a plush armchair wrapped in a thick cable-knit blanket, resting head back with closed eyes in quiet contemplation",
    },
    6: {
        "OBJECT_MACRO": "Macro close-up shot of an open vintage hardcover book with yellowed pages and a dried four-leaf clover bookmark, resting on a soft velvet reading chair",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side person feeling isolated and lonely in crowded noisy party vs Right side person enjoying rich comforting solitude in quiet bedroom",
        "MECHANISM_CUTAWAY": "Psychological cutaway diagram distinguishing loneliness from solitude: loneliness as deficit mindset vs solitude as abundant creative communion with inner self",
        "STEP_ENUMERATION": "Three-step transformation to sacred solitude: Step one reframe alone time as luxury, Step two welcome thoughts without harsh critique, Step three enjoy own company",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how developing a gentle friendship with oneself turns nighttime solitude into the most healing hour of the day",
        "SITUATIONAL_ACTION": "A person sipping warm chamomile tea from a ceramic mug, gazing affectionately at soft rain tapping gently on the dark windowpane, completely at peace",
    },
    7: {
        "OBJECT_MACRO": "Macro close-up shot of an aged cedar memory box containing gently folded handwritten letters and a fragrant sprig of dried French lavender, warm sidelight",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side person repeatedly re-reading old regrets with self-blame vs Right side person gently closing the cedar box with forgiveness and love",
        "MECHANISM_CUTAWAY": "Cognitive reframing cutaway diagram of past mistakes: recognizing former actions were taken with limited past awareness, now honored as essential stepping stones",
        "STEP_ENUMERATION": "Three-step self-forgiveness sequence: Step one acknowledge past clumsiness with empathy, Step two thank the younger self for surviving, Step three release the burden",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how forgiving past versions of yourself lifts the heavy emotional backpack and unblocks spontaneous joy in the present",
        "SITUATIONAL_ACTION": "A person closing an old journal and placing it on a wooden shelf, smiling with soft self-compassion, ready to turn over a clean untouched page tomorrow",
    },
    8: {
        "OBJECT_MACRO": "Macro close-up shot of a steaming ceramic mug of chamomile tea with honey, delicate swirls of fragrant steam catching warm golden lamplight against midnight window",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side cold harsh fluorescent office lighting and caffeine vs Right side warm amber bedside lamp and soothing herbal chamomile infusion",
        "MECHANISM_CUTAWAY": "Sensory neurological cutaway diagram of warmth: gentle thermal sensations triggering oxytocin release, slowing sympathetic tone, and welcoming parasympathetic ease",
        "STEP_ENUMERATION": "Three-step sensory comfort ritual: Step one hold the warm ceramic cup with both palms, Step two inhale sweet herbal vapor, Step three take a slow deliberate sip",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how small deliberate sensory comforts at night signal safety to the nervous system and dissolve accumulated stress",
        "SITUATIONAL_ACTION": "A person sinking deep into soft pillows in bed, feeling the soothing warmth of herbal tea in chest, listening to quiet distant wind rustling nighttime leaves",
    },
    9: {
        "OBJECT_MACRO": "Macro close-up shot of three smooth polished river stones resting on a wooden nightstand, inscribed with simple symbols of peace, courage, and gratitude",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side mind churning over unfinished to-do lists in torment vs Right side mind resting on three gentle bedtime affirmations in peace",
        "MECHANISM_CUTAWAY": "Cognitive cognitive restructuring cutaway: replacing late-night self-criticism with three grounded affirmations of unconditional worth and future hope",
        "STEP_ENUMERATION": "Three bedtime soothing affirmations: Affirmation one You tried your best today, Affirmation two Tomorrow is a blank canvas, Affirmation three You are worthy of peace",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how reciting compassionate bedtime affirmations lowers pre-sleep cognitive arousal and shortens sleep onset latency",
        "SITUATIONAL_ACTION": "A person whispering words of kindness to oneself in quiet bedroom, hand resting gently over heart, feeling steady comforting pulse of life within",
    },
    10: {
        "OBJECT_MACRO": "Macro close-up shot of a soft white feather pillow bathed in silver moonlight, clean linen texture illuminated softly through sheer lace curtains",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side restless tossing and turning with racing thoughts vs Right side deep serene sleep with smooth peaceful breathing",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram of sleep restoration: slow-wave delta sleep clearing metabolic toxins and consolidating emotional memories into wisdom",
        "STEP_ENUMERATION": "Three-step closing bedtime lullaby: Step one release the finished day, Step two close tired eyelids gently, Step three drift into safe restorative healing sleep",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how trusting the night to heal you prepares mind and body to awake tomorrow morning renewed, hopeful, and strong",
        "SITUATIONAL_ACTION": "A sleeping figure resting peacefully under a warm quilt in moonlit room, soft gentle breathing, calm serene expression, drifting in deep healing slumber",
    },
}

THUONG_CHO_KHEO_THEMES: Dict[int, Dict[str, str]] = {
    1: {
        "OBJECT_MACRO": "Macro close-up shot of a steaming ceramic soup bowl sitting untouched on a dark polished oak dining table between two distant place settings, broth cooling",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side heated argument with sharp harsh words vs Right side quiet dining room with growing awkward distance across cold table",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram of emotional escalation: innocent ambiguous remark misconstrued through defensive filters into sharp interpersonal conflict",
        "STEP_ENUMERATION": "Three-step conflict spiral: Step one thoughtless phrase spoken, Step two defensive hurt triggered, Step three emotional wall constructed between partners",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how unresolved minor emotional misunderstandings compound over time into profound relational estrangement",
        "SITUATIONAL_ACTION": "Two adults sitting at opposite ends of a long wooden dining table in silence, looking down at untouched plates, tension hanging palpably in ambient lighting",
    },
    2: {
        "OBJECT_MACRO": "Macro close-up shot of a thick vertical pane of transparent glass slicing down the center of dining table, physically dividing two people sitting inches apart",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side superficial hearing where sound waves bounce off ear vs Right side deep empathetic listening where meaning penetrates heart",
        "MECHANISM_CUTAWAY": "Acoustic neurobiological cutaway diagram: sound waves entering auditory cortex while emotional mirroring neural circuits remain active, receptive, and calm",
        "STEP_ENUMERATION": "Three-step active listening transition: Step one cease preparing counter-arguments, Step two observe nonverbal cues, Step three validate emotional reality",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how rushing to defend oneself prevents true listening and guarantees escalating frustration for both speakers",
        "SITUATIONAL_ACTION": "A person leaning forward across the table with soft focused eyes and open hands, nodding slowly in genuine understanding as partner speaks",
    },
    3: {
        "OBJECT_MACRO": "Macro close-up shot of an open notepad with an analytical checklist and red pen being pushed across table toward someone who is visibly crying",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side impatient partner offering quick robotic solutions vs Right side compassionate partner sitting quietly holding space for sorrow",
        "MECHANISM_CUTAWAY": "Psychological mechanism cutaway of emotional invalidation: jumping straight to intellectual solutions signaling to the speaker that their feelings are a problem to fix",
        "STEP_ENUMERATION": "Three-step empathetic support sequence: Step one resist the urge to fix, Step two sit with the discomfort of sorrow, Step three offer gentle comforting presence",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram demonstrating how unsolicited advice deepens isolation, while empathetic emotional validation de-escalates crisis into trust",
        "SITUATIONAL_ACTION": "A partner quietly sliding the notepad aside, reaching across table to gently place open hand on partner wrist with tender patient warmth",
    },
    4: {
        "OBJECT_MACRO": "Macro close-up shot of a small bronze gavel resting on judicial courtroom bench, symbolizing internal defensive mental rehearsal during a conversation",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side mind formulating sharp rebuttal while partner speaks vs Right side mind completely quiet, receiving words without judgment",
        "MECHANISM_CUTAWAY": "Cognitive mechanism cutaway of the mental courtroom: ego cross-examining partner statements for factual inconsistencies while entirely missing emotional cries for connection",
        "STEP_ENUMERATION": "Three-step disarmament sequence: Step one recognize defensive urge, Step two lower internal armor shield, Step three listen for underlying fear rather than attack",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how winning the factual debate often results in losing the emotional relationship, destroying intimacy",
        "SITUATIONAL_ACTION": "A speaker pausing mid-sentence, looking up with vulnerable expression, realizing that connection matters far more than being proven intellectually right",
    },
    5: {
        "OBJECT_MACRO": "Macro close-up shot of trembling fingers resting on tabletop, knuckles slightly white, a tear droplet catching warm sidelight on the polished wood",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side angry aggressive facial expression masking hurt vs Right side microscopic cutaway of vulnerable tearful heart needing comfort",
        "MECHANISM_CUTAWAY": "Nonverbal communication cutaway diagram: surface angry words (ten percent) versus subconscious body language, vocal cadence, and somatic distress (ninety percent)",
        "STEP_ENUMERATION": "Three nonverbal cues to watch: Cue one catch in breath, Cue two averted downward gaze, Cue three tightened trembling shoulders signaling overwhelmed sadness",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how responding directly to the underlying emotional hurt immediately disarms defensive aggression and brings tears of relief",
        "SITUATIONAL_ACTION": "A warm gentle hand reaching across the table surface, softly covering the trembling fingers with reassuring pressure, bridging the divide",
    },
    6: {
        "OBJECT_MACRO": "Macro close-up shot of two distinct colored optical prisms standing side by side, splitting a single beam of white sunlight into two harmoniously overlapping rainbows",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side two people arguing over who owns objective truth vs Right side two people acknowledging that both emotional realities are valid",
        "MECHANISM_CUTAWAY": "Epistemological cutaway diagram of dual perspectives: two observers viewing a three-dimensional sculpture from opposite angles, describing different yet accurate sides",
        "STEP_ENUMERATION": "Three-step validation sequence: Step one acknowledge partner perspective, Step two confirm emotional legitimacy, Step three express own perspective without negation",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how empathy without agreement honors partner dignity while preserving personal boundaries and honest self-worth",
        "SITUATIONAL_ACTION": "Two people sitting opposite each other, looking at each other with respectful curiosity rather than combativeness, nodding in mutual recognition",
    },
    7: {
        "OBJECT_MACRO": "Macro close-up shot of an antique brass key turning smoothly inside an intricate lock on a solid oak door, door beginning to unlatch into warm hallway light",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side defensive statement triggering slammed doors vs Right side gentle open-ended question opening closed heart like a key",
        "MECHANISM_CUTAWAY": "Linguistic cutaway diagram of emotional mirroring: echoing back partner words with warmth (resonator effect) to prove deep accurate comprehension",
        "STEP_ENUMERATION": "Three-step reflective questioning sequence: Step one What I hear you saying is, Step two That makes complete sense why you feel that way, Step three Tell me more about that",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram demonstrating how reflective emotional mirroring immediately de-escalates defensive arousal in the human brain",
        "SITUATIONAL_ACTION": "A person listening with head tilted slightly, repeating back partner core feelings with gentle empathy, watching partner shoulders visibly drop and relax",
    },
    8: {
        "OBJECT_MACRO": "Macro close-up shot of a delicate velvet umbrella shielding a fragile flowering potted plant from heavy torrential downpour, raindrops rolling harmlessly off fabric",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side co-dependent absorption taking on partner rage as personal fault vs Right side compassionate boundary remaining loving yet autonomous",
        "MECHANISM_CUTAWAY": "Psychological boundary cutaway diagram: semi-permeable boundary allowing love and empathy to flow freely while deflecting toxic blame and emotional manipulation",
        "STEP_ENUMERATION": "Three-step healthy boundary sequence: Step one validate partner pain, Step two refuse abusive treatment, Step three offer collaborative connection when calm",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how clear loving boundaries protect personal emotional sovereignty and prevent caregiver resentment in close bonds",
        "SITUATIONAL_ACTION": "A person standing firm with a calm loving posture, speaking softly with clarity and kindness, refusing to match escalating angry volume",
    },
    9: {
        "OBJECT_MACRO": "Macro close-up shot of a shattered antique celadon teacup, lovingly reassembled with gleaming veins of twenty-four karat gold kintsugi lacquer lines",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side discarded broken ceramic shards in trash vs Right side restored kintsugi teacup stronger and more beautiful at fractured seams",
        "MECHANISM_CUTAWAY": "Relational repair cutaway diagram: conflict rupture followed by attunement and repair strengthening attachment security beyond original untested state",
        "STEP_ENUMERATION": "Three steps to transform conflict: Step one pause before escalation, Step two acknowledge shared attachment bond, Step three co-create mutually restorative bridge",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how successful conflict repair builds profound mutual resilience and unbreakable intimacy in human relationships",
        "SITUATIONAL_ACTION": "Two partners holding the repaired kintsugi teacup together between their hands, smiling softly with tears of deep reconciliation and renewed trust",
    },
    10: {
        "OBJECT_MACRO": "Macro close-up shot of a black smartphone placed face down on a wooden table beside two steaming ceramic mugs of tea in warm morning windowlight",
        "SPLIT_COMPARISON": "50/50 split-screen comparison: Left side two people distracted by separate glowing screens vs Right side two people looking into each other eyes in warm presence",
        "MECHANISM_CUTAWAY": "Visual mechanism cutaway diagram of complete presence: focused eye contact and undivided attention triggering oxytocin release and profound relational attunement",
        "STEP_ENUMERATION": "Three gifts of mindful loving: Gift one gift of undivided presence, Gift two gift of non-judgmental acceptance, Gift three gift of unconditional loyalty",
        "CAUSE_EFFECT_DIAGRAM": "Cause-and-effect flowchart diagram showing how giving the gift of full presence transforms ordinary domestic moments into sacred sanctuaries of lasting love",
        "SITUATIONAL_ACTION": "Two people sitting side by side on a cozy sofa in warm morning light, holding hands in peaceful companionable silence, smiling with heartfelt gratitude",
    },
}

CHANNEL_THEME_REGISTRY = {
    "chanh_niem_ke": CHANH_NIEM_KE_THEMES,
    "loi_sang_soi": LOI_SANG_SOI_THEMES,
    "minh_triet_song": MINH_TRIET_SONG_THEMES,
    "tam_tinh_dem": TAM_TINH_DEM_THEMES,
    "thuong_cho_kheo": THUONG_CHO_KHEO_THEMES,
}


def build_channel_explainer_spec(slug: str) -> Dict[str, Any]:
    """Build the complete, verified explainer visual spec for a channel."""
    cfg = CHANNEL_CONFIGS[slug]
    channel_dir = VIDEO_DIR / f"vn_pilot_{slug}_long"
    aligned_spec_path = channel_dir / f"{slug}_long_aligned_spec.json"

    with open(aligned_spec_path, "r", encoding="utf-8") as f:
        orig_spec = json.load(f)

    beats_data, _ = build_beats_for_channel(slug)
    chapters = orig_spec.get("chapters", [])
    old_vs = orig_spec.get("visual_states", [])
    n_vs = len(old_vs)

    # 1. Old image reuse mapping (~55 beats, 21.2% - 21.6%)
    step = n_vs / 55.0
    selected_vs_indices = [int(i * step) for i in range(55)]

    assigned_beats = set()
    reuse_map: Dict[int, int] = {}
    for v_idx in selected_vs_indices:
        v_at = old_vs[v_idx]["at"]
        best_b = None
        best_dist = 999999.0
        for b_idx, b in enumerate(beats_data):
            if b_idx not in assigned_beats:
                dist = abs(b["start"] - v_at)
                if dist < best_dist:
                    best_dist = dist
                    best_b = b_idx
        if best_b is not None:
            assigned_beats.add(best_b)
            reuse_map[best_b] = v_idx

    # 2. Build final beats
    theme_lib = CHANNEL_THEME_REGISTRY[slug]
    final_beats = []

    for b_idx, b in enumerate(beats_data):
        ch_idx, ch_title = assign_chapter_info(b["start"], chapters)
        explainer_type = assign_explainer_type(b_idx % 25, b["narration"])
        camera_motion = assign_camera_motion(explainer_type, b_idx)
        reuse_idx = reuse_map.get(b_idx, None)

        # Retrieve thematic body
        ch_themes = theme_lib.get(ch_idx, theme_lib[1])
        theme_body = ch_themes.get(explainer_type, ch_themes["OBJECT_MACRO"])

        prompt = assemble_clean_prompt(cfg["style_prefix"], theme_body)

        beat_obj = {
            "beat_id": f"B{b_idx:03d}",
            "at": b["start"],
            "duration": b["duration"],
            "narration": b["narration"],
            "chapter_index": ch_idx,
            "chapter_title": ch_title,
            "explainer_type": explainer_type,
            "reuse_old_image_idx": reuse_idx,
            "prompt": prompt,
            "camera_motion": camera_motion,
            "transition": "fade",
        }
        final_beats.append(beat_obj)

    spec_dict = {
        "channel_id": slug,
        "channel_slug": slug,
        "job_id": f"vn_pilot_{slug}_long",
        "parent_long_id": f"vn_pilot_{slug}_long",
        "format_profile": "long_16x9",
        "youtube_title": orig_spec.get("youtube_title", ""),
        "total_duration_sec": orig_spec.get("total_duration_sec", 0.0),
        "target_beats": len(final_beats),
        "chapters": chapters,
        "beats": final_beats,
    }

    return spec_dict


def validate_explainer_spec(
    spec: Dict[str, Any], slug: str
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """Strictly validate an explainer spec against all mandatory rules."""
    cfg = CHANNEL_CONFIGS[slug]
    errors = []
    beats = spec.get("beats", [])

    # 1. Beat count
    target_count = cfg["target_beats"]
    if len(beats) != target_count:
        errors.append(f"Beat count {len(beats)} != expected {target_count}")

    # 2. Duration sum match
    total_beat_dur = sum(b["duration"] for b in beats)
    spec_dur = spec.get("total_duration_sec", 0.0)
    dur_diff = abs(total_beat_dur - spec_dur)
    if dur_diff > 0.01:
        errors.append(
            f"Duration sum {total_beat_dur:.4f} differs from spec {spec_dur:.4f} by {dur_diff:.4f}s > 0.01s"
        )

    # 3. Explainer type distribution (>= 85% first 5 types)
    type_counts: Dict[str, int] = {}
    for b in beats:
        t = b.get("explainer_type", "")
        type_counts[t] = type_counts.get(t, 0) + 1

    first_5_types = {
        "OBJECT_MACRO",
        "SPLIT_COMPARISON",
        "MECHANISM_CUTAWAY",
        "STEP_ENUMERATION",
        "CAUSE_EFFECT_DIAGRAM",
    }
    first_5_sum = sum(type_counts.get(t, 0) for t in first_5_types)
    first_5_pct = first_5_sum / len(beats) * 100.0 if beats else 0.0
    if first_5_pct < 85.0:
        errors.append(
            f"First 5 explainer types {first_5_pct:.1f}% < 85.0% threshold"
        )

    # 4. Old image reuse in [20%, 30%]
    reused_count = sum(1 for b in beats if b.get("reuse_old_image_idx") is not None)
    reuse_pct = reused_count / len(beats) * 100.0 if beats else 0.0
    if not (20.0 <= reuse_pct <= 30.0):
        errors.append(
            f"Reuse percentage {reuse_pct:.1f}% not in [20%, 30%] range"
        )

    # 5. Prompt validations
    prefix = cfg["style_prefix"]
    for _i, b in enumerate(beats):
        p = b.get("prompt", "")
        w_count = len(p.split())
        if not (35 <= w_count <= 65):
            errors.append(
                f"Beat {b.get('beat_id')} prompt word count {w_count} not in [35, 65]"
            )
        if not p.startswith(prefix):
            errors.append(
                f"Beat {b.get('beat_id')} does not start with prefix: {prefix}"
            )
        if not p.endswith(PROMPT_SUFFIX):
            errors.append(
                f"Beat {b.get('beat_id')} does not end with {PROMPT_SUFFIX}"
            )
        for f in FORBIDDEN_PHRASES:
            if f in p.lower():
                errors.append(
                    f"Beat {b.get('beat_id')} contains forbidden phrase: {f}"
                )

    metrics = {
        "slug": slug,
        "total_beats": len(beats),
        "total_duration": total_beat_dur,
        "expected_duration": spec_dur,
        "dur_diff": dur_diff,
        "type_counts": type_counts,
        "first_5_pct": first_5_pct,
        "reused_count": reused_count,
        "new_count": len(beats) - reused_count,
        "reuse_pct": reuse_pct,
    }

    return len(errors) == 0, errors, metrics


def main() -> None:
    """Build and validate all 5 Group D channels."""
    print("=== Building Explainer Specs for Group D Channels ===")
    all_metrics = []

    for slug in CHANNEL_CONFIGS:
        print(f"\n--- Processing {slug} ---")
        spec = build_channel_explainer_spec(slug)

        is_valid, errors, metrics = validate_explainer_spec(spec, slug)
        if not is_valid:
            print(f"FAILED validation for {slug}:")
            for e in errors[:10]:
                print(f"  ERROR: {e}")
            raise ValueError(f"Validation failed for {slug}")

        out_path = VIDEO_DIR / f"vn_pilot_{slug}_long" / f"{slug}_long_explainer_spec.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False, indent=2)

        print(
            f"SUCCESS: Saved {out_path} ({metrics['total_beats']} beats, {metrics['reused_count']} reused, {metrics['new_count']} new, {metrics['first_5_pct']:.1f}% first 5 types)"
        )
        all_metrics.append(metrics)

    print("\n=== SUMMARY TABLE ===")
    print(
        f"{'Slug':20s} | {'Beats':5s} | {'First 5 %':10s} | {'Reused':6s} | {'New':5s} | {'Reuse %':7s} | {'Dur Diff':8s}"
    )
    print("-" * 75)
    for m in all_metrics:
        print(
            f"{m['slug']:20s} | {m['total_beats']:5d} | {m['first_5_pct']:9.1f}% | {m['reused_count']:6d} | {m['new_count']:5d} | {m['reuse_pct']:6.1f}% | {m['dur_diff']:7.4f}s"
        )


if __name__ == "__main__":
    main()
