#!/usr/bin/env python3
"""
Builder for Option B Full Storyboard Manifest (382 shots).
Splits all static holds > 3.0s into dynamic 1.5s - 2.0s sub-beats.
Ensures 100% compliance with Anonymous Stick-Figure Cast invariant
and strictly omits any subtitle margin restrictions.
"""
import json
from pathlib import Path

MANIFEST_245_PATH = Path("sys/exports/ancient_humans_bundle/manifest/manifest_245_shots.json")
MANIFEST_CH1_BLIND_PATH = Path("sys/exports/ancient_humans_bundle/manifest/ch1_blind_34_shots.json")
OUTPUT_MANIFEST_PATH = Path("sys/exports/ancient_humans_bundle/manifest/manifest_option_b_full.json")

PREFIX = (
    "2D hand-drawn explainer illustration in bold black marker-pen outline with flat muted pastel and "
    "warm earthy fills on a clean uncluttered off-white paper background, 16:9 widescreen. "
    "Cast invariant: anonymous stick-figure character with a large round solid-white head, thick 4px "
    "closed black outline, expressive simple dot/line eyes and eyebrows, thin stick limbs, and a single stick torso."
)

SUFFIX = (
    "Do NOT render any text, letters, words, watermarks, logos, photorealistic faces, or 3D shading."
)

NEG_PROMPT = (
    "photorealistic, 3D render, complex shading, anime, colorful gradients, text, watermark, bad anatomy, realistic humans, duplicate bodies"
)

def make_prompt(middle_action: str) -> str:
    cleaned = middle_action.strip().rstrip(".")
    return f"{PREFIX} {cleaned}. {SUFFIX}"

# Dictionary defining splits for all shots > 3.0s
SPLITS = {}

# ==========================================
# CHAPTER 1: The mystery of modern time (34 blind beats + 9 sub-beats = 43 shots)
# ==========================================
CH1_BLIND_SPLITS = {
    8: (
        0.5,
        "Extreme close-up of alarm clock locking in morning wake-up symbol as stick figure pulls blanket over head.",
        "Extreme close-up of the glowing digital alarm clock face on the nightstand locking in its wake-up bell icon as the exhausted stick figure pulls the blanket over its head inside a subtle hand-drawn circular loop arrow",
        "punch_in",
    ),
    9: (
        0.5,
        "Modern concrete buildings dissolving into wide open prehistoric golden savanna plains at dawn.",
        "Dynamic visual transition: modern gray concrete office buildings on the right dissolving like mist into wide open prehistoric golden savanna plains with flat-top acacia trees under warm dawn sunlight",
        "zoom_out",
    ),
    11: (
        0.5,
        "Close-up of prehistoric stick figure's peaceful smiling face watching a morning butterfly.",
        "Close-up of the prehistoric stick figure's large round white head resting peacefully on folded arms on a fur mat, smiling contentedly as a gentle golden butterfly flutters past in unhurried morning silence",
        "zoom_in",
    ),
    17: (
        0.5,
        "Extreme close-up of flashing warning siren and spinning gears above skeptical stick figure.",
        "Extreme close-up of a flashing red warning siren and spinning mechanical gears inside a thought cloud above the skeptical modern stick figure's furrowed eyebrows and wide eyes",
        "punch_in",
    ),
    18: (
        0.5,
        "Close-up of shivering caveman stick figure clutching empty stomach in cold rain.",
        "Close-up of the shivering prehistoric stick figure in tattered pelt clutching an empty rumbling stomach with wavy hunger lines under cold rain, depicting the bleak textbook stereotype of prehistoric misery",
        "zoom_in",
    ),
    20: (
        0.5,
        "Close-up of thick vintage textbook page depicting struggling caveman beside antique hourglass.",
        "Close-up of an open thick vintage history textbook page resting on a lectern, showing a hand-drawn sketch of a struggling caveman beside a slowly trickling antique glass hourglass",
        "pan_right",
    ),
    21: (
        0.5,
        "Macro underground view of intact ancient skeleton resting peacefully in deep terracotta earth.",
        "Macro close-up underground view of a robust, intact ancient human skeleton resting peacefully in deep warm terracotta earth strata, surrounded by a soft golden discovery glow",
        "zoom_in",
    ),
    33: (
        0.5,
        "Close-up of modern office stick figure pressing hands against glass window looking at sunlit horizon.",
        "Close-up of the modern office stick figure in a necktie pressing both hands against a glass office window, looking out wistfully toward the sunlit open savanna horizon",
        "zoom_in",
    ),
    34: (
        0.5,
        "Wide final cliffhanger composition of lone stick figure as calendar pages scatter into the sky.",
        "Wide atmospheric cliffhanger composition: a lone modern stick figure standing on a quiet open horizon as loose calendar pages and clock hands scatter upward into the breeze",
        "zoom_out",
    ),
}

# ==========================================
# CHAPTER 2: Skeletons as historical diary (+15 shots)
# ==========================================
SPLITS[45] = [
    ("a", 0.25, "Archaeological trench revealing two adjacent prehistoric graves.",
     "Overhead wide shot of two archaeological grave pits side-by-side in warm terracotta earth; clean grid strings stretched across the dig site under bright pale morning light.",
     "pan_left"),
    ("b", 0.25, "Camera drifting over Skeleton #1: robust, elongated, athletic frame.",
     "Slow pan over Skeleton #1 lying peacefully: thick dense femur bones, wide ribcage, athletic posture outlined in crisp black ink with bone-ivory fills.",
     "zoom_in"),
    ("c", 0.25, "Camera moving over Skeleton #2: curved spine, deformed joints.",
     "Slow pan over Skeleton #2 lying in compressed earth: noticeable S-curve in spine, flattened vertebrae, arthritic knees highlighted with subtle terracotta accents.",
     "pan_right"),
    ("d", 0.25, "Archaeologist kneeling between graves examining the profound contrast.",
     "Medium shot of stick-figure archaeologist kneeling on a wooden plank between the two graves, measuring tape in hand, looking thoughtfully back and forth.",
     "zoom_out"),
]

SPLITS[47] = [
    ("a", 0.5, "Close-up of Skeleton #1's skull showing broad jaw and perfect teeth.",
     "Close-up anatomical diagram of Skeleton #1's skull: wide strong mandibular arch, perfectly intact pearly white teeth without a single cavity or sign of decay.",
     "zoom_in"),
    ("b", 0.5, "Archaeologist using dental probe to inspect flawless ancient enamel.",
     "Close-up of an archaeologist's gloved hand holding a fine metal probe inspecting the molar teeth of Skeleton #1, clean bone contours highlighted with gentle mint-green aura.",
     "punch_in"),
]

SPLITS[50] = [
    ("a", 0.5, "Prehistoric feast spread across flat warm river rock with wild berries.",
     "Still life composition on a flat river boulder: clusters of deep purple wild blackberries, cracked hazelnuts, roasted root tubers, and strips of lean game meat.",
     "zoom_out"),
    ("b", 0.5, "Athletic hunter-gatherer stick figure picking and eating fresh berries happily.",
     "Medium shot of a lively stick figure reaching into tall berry bushes under dappled sunshine, enjoying fresh fruit with radiant vitality.",
     "zoom_in"),
]

SPLITS[59] = [
    ("a", 0.5, "Cross-section of Skeleton #1's thick femur bone with dense interior.",
     "Scientific anatomical cross-section diagram of Skeleton #1's femur: thick outer cortical bone and dense honeycomb trabecular structure indicating powerful athletic load.",
     "zoom_in"),
    ("b", 0.5, "Comparison cross-section of Skeleton #2's thin porous brittle bone walls.",
     "Cross-section comparison of Skeleton #2's femur: fragile thin bone walls, large porous marrow cavities, and red stress indicator arrows showing nutritional deficiency.",
     "punch_in"),
]

SPLITS[63] = [
    ("a", 0.333, "Neolithic field: stick figure bending over swinging a flint hoe.",
     "Wide shot of an early Neolithic muddy field; a lone stick figure hunched over, swinging a primitive wooden hoe with a knapped flint blade into heavy damp clay.",
     "pan_left"),
    ("b", 0.333, "Close-up of mud-caked, blistered hands gripping the rough wooden handle.",
     "Extreme close-up of stick figure's hands caked in dry brown mud, calluses and friction marks on palms gripping a rough tree branch tool handle.",
     "punch_in"),
    ("c", 0.334, "Farmer pausing to rub aching lower back under blistering midday heat.",
     "Medium shot of the farmer pausing work, placing one hand on lower back with a grimacing line mouth, small drops of sweat flying in the harsh golden sunlight.",
     "zoom_out"),
]

SPLITS[72] = [
    ("a", 0.25, "Biometric silhouette comparison: tall upright hunter vs stooped farmer.",
     "Direct side-by-side silhouette diagram: on the left, an upright athletic hunter-gatherer standing 178 cm tall; on the right, a hunched farmer standing 160 cm tall.",
     "zoom_in"),
    ("b", 0.25, "Biomechanical stress diagram of damaged farmer spine.",
     "Scientific diagram of the human vertebral column: glowing orange stress highlights at L4-L5 lumbar vertebrae showing disc herniation from daily grinding agricultural work.",
     "punch_in"),
    ("c", 0.25, "Nutritional contrast: colorful diverse wild foods vs bland grain mush.",
     "Split comparison: left side overflowing with colorful wild berries, herbs, fish, and nuts; right side showing a single cracked clay bowl filled with gray boiled barley gruel.",
     "pan_right"),
    ("d", 0.25, "Archaeologist noting down conclusion in field logbook.",
     "Medium shot of archaeologist closing the leather field journal, looking into the distance with a grave expression, realizing the high cost of the agricultural shift.",
     "zoom_out"),
]

SPLITS[73] = [
    ("a", 0.5, "Abstract timeline graphic: ancient hourglass pouring into modern gears.",
     "Conceptual illustration: an ancient glass hourglass with golden sand flowing down into complex mechanical cogs and digital clock faces, bridging millennia.",
     "zoom_in"),
    ("b", 0.5, "Modern stick figure looking down at ancient footprints in dry earth.",
     "Medium shot of modern stick figure in sneakers standing at the edge of the dig site, looking at preserved 10,000-year-old bare footprints in fossilized mud.",
     "zoom_out"),
]

SPLITS[76] = [
    ("a", 0.25, "Wide archaeological dig site at sunset with long cast shadows.",
     "Wide establishing landscape of the excavation site at sunset; long terracotta shadows stretching across dirt trenches, quiet desert wind blowing fine dust.",
     "pan_left"),
    ("b", 0.25, "Close-up of the two skulls looking up at the first evening star.",
     "Close-up of the two ancient skulls resting side-by-side in earth, looking upward towards a soft violet sky where the first evening star glimmers.",
     "zoom_in"),
    ("c", 0.25, "Archaeologist carrying canvas tool bag away into twilight.",
     "Medium shot of stick figure archaeologist walking along the trench rim carrying a satchel, silhouette framed against apricot and lavender sunset.",
     "pan_right"),
    ("d", 0.25, "Sky transitions to deep starlight over savanna, opening Chapter 3.",
     "Panoramic dissolve: the sky deepens into rich indigo dotted with white hand-drawn stars, acacia trees appearing on the horizon line.",
     "zoom_out"),
]

# ==========================================
# CHAPTER 3: Life as a hunter-gatherer (+18 shots)
# ==========================================
SPLITS[78] = [
    ("a", 0.5, "Wide shot: stick figure waking up leisurely on open savanna at dawn.",
     "Wide shot of a stick figure waking up leisurely on soft grass in an open savanna clearing; warm apricot sunrise rays filtering through the flat canopy of acacia trees.",
     "zoom_out"),
    ("b", 0.5, "Close-up: peaceful facial expression, bright dot eyes, zero alarm stress.",
     "Close-up of the stick figure's large round white head smiling contentedly, bright dot eyes wide and rested, hands stretching behind head in complete absence of any alarm.",
     "zoom_in"),
]

SPLITS[79] = [
    ("a", 0.166, "Wide camp: morning embers smoking gently in center of peaceful shelters.",
     "Wide establishing shot of a hunter-gatherer camp at sunrise; domed grass shelters arranged in a loose circle, faint white smoke curling up from morning embers.",
     "zoom_out"),
    ("b", 0.166, "Medium shot: stick figure stretching limbs following natural body rhythm.",
     "Medium shot of a stick figure standing up outside grass shelter, arms outstretched towards the sky in an expansive yawn, spine supple and relaxed.",
     "zoom_in"),
    ("c", 0.166, "Close-up hands: lifting a dried gourd flask to drink cool clean spring water.",
     "Close-up of stick figure's hands holding a hollowed golden gourd canteen, tilting it back to drink refreshing water, droplets glistening in the sun.",
     "punch_in"),
    ("d", 0.167, "Infographic: sun climbing naturally over horizon without any clock hands.",
     "Clean diagrammatic composition: a gentle stylized orange sun rising above a flat horizon line; no clock dials, numbers, or artificial grids anywhere in the sky.",
     "pan_right"),
    ("e", 0.167, "Group interaction: two tribe members conversing casually on a warm rock.",
     "Medium shot of two stick figures sitting side-by-side on a sun-warmed granite boulder, gesturing with open hands in relaxed morning conversation.",
     "pan_left"),
    ("f", 0.168, "Macro detail: bare feet stepping firmly on soft resilient savanna soil.",
     "Low-angle macro shot of bare stick figure feet stepping grounded and firm onto soft, grassy savanna earth, completely connected with natural terrain.",
     "zoom_in"),
]

SPLITS[80] = [
    ("a", 0.5, "Medium shot: tribe sharing cracked mongongo nuts and wild fruit.",
     "Medium shot of four stick figures sitting in a circle sharing roasted mongongo nuts and sweet yellow wild plums from woven shallow baskets.",
     "zoom_in"),
    ("b", 0.5, "Stick figure gesturing towards distant low hills to plan today's gathering.",
     "Medium shot of a stick figure standing and pointing an arm towards gentle rolling hills on the horizon, tribal companions looking and nodding in agreement.",
     "pan_right"),
]

SPLITS[88] = [
    ("a", 0.5, "Wide group: hunters squatting in circle evaluating fresh animal tracks.",
     "Wide shot of a small hunting party squatting in a tight circle on reddish sand, examining freshly made hoofprints with collective focus.",
     "zoom_out"),
    ("b", 0.5, "Close-up: hunter touching animal print in damp sand to gauge time.",
     "Close-up of a stick figure hunter kneeling, fingertips gently pressing the rim of an animal track in soft earth to judge moisture and freshness.",
     "punch_in"),
]

SPLITS[92] = [
    ("a", 0.2, "Medium shot: using a digging stick to unearth water-rich wild tubers.",
     "Medium shot of stick figure forager using a smooth curved digging stick to pry a large succulent water-root tuber from rich sandy soil.",
     "pan_left"),
    ("b", 0.2, "Macro nut basket: close-up of woven basket full of golden mongongo nuts.",
     "Close-up still life: a tightly woven straw basket overflowing with round cracked mongongo nuts, high protein fuel harvested without back strain.",
     "zoom_in"),
    ("c", 0.2, "Smiling face: stick figure enjoying abundant easy harvest.",
     "Close-up of stick figure smiling with satisfied curved mouth line, holding up a sweet wild root, eyes shining with abundance and ease.",
     "punch_in"),
    ("d", 0.2, "Tree canopy: gentle shade under expansive branches of ancient baobab.",
     "Low-angle shot looking up into the massive shady boughs of an ancient baobab tree, dappled sunlight shimmering through broad green leaves.",
     "zoom_out"),
    ("e", 0.2, "Walking back: slinging foraging sack over shoulder with light step.",
     "Medium shot of stick figure slinging a woven bag of nuts over one shoulder, walking back towards camp with a brisk, effortless stride.",
     "pan_right"),
]

SPLITS[94] = [
    ("a", 0.5, "Establishing: returning to camp in early afternoon under high sun.",
     "Wide shot of foragers returning to camp at 1:30 PM; sun just past noon, shadows still short, most of the day's sunlight remaining ahead.",
     "zoom_out"),
    ("b", 0.5, "Camp return: setting down food basket in camp center for everyone.",
     "Medium shot of forager setting down the loaded food basket in the center of camp, children and elders gathering round with smiles of welcome.",
     "zoom_in"),
]

SPLITS[97] = [
    ("a", 0.5, "Full body nap: stick figure dozing peacefully under baobab shade.",
     "Full body shot of a stick figure stretched out horizontally in deep cool baobab tree shade, one arm folded under head, dozing in peaceful siesta.",
     "zoom_in"),
    ("b", 0.5, "Breeze mood: green leaves fluttering gently in warm afternoon wind.",
     "Close-up shot of acacia branch leaves swaying softly in warm desert wind, tranquil atmosphere of total leisure and freedom from deadlines.",
     "pan_left"),
]

SPLITS[101] = [
    ("a", 0.5, "Action wide: antelope fleeing across heat shimmer on midday savanna.",
     "Wide action shot: a graceful antelope bounding across open savannah plains; wavy heat-haze distortion rising from golden parched grass.",
     "pan_right"),
    ("b", 0.5, "Close-up animal: quarry panting heavily, unable to sweat or vent heat.",
     "Close-up of the antelope running with tongue out, panting rapidly; heat stress indicators showing animal body temperature dangerously rising.",
     "zoom_in"),
]

SPLITS[102] = [
    ("a", 0.5, "Pacing stride: human stick figure hunter jogging at steady easy pace.",
     "Dynamic tracking shot of human stick figure hunter running with an easy, rhythmic endurance stride, arms loosely swinging, sweat evaporating smoothly.",
     "pan_left"),
    ("b", 0.5, "Determined eyes: calm steady breathing maintained across hours of chase.",
     "Close-up of hunter's round white head: steady focused dot eyes, calm rhythmic breathing line, perfectly adapted endurance biology.",
     "punch_in"),
]

SPLITS[104] = [
    ("a", 0.333, "Triumphant return: hunter carrying quarry home in golden evening glow.",
     "Wide shot of hunter walking back into camp carrying harvested game over shoulders; sky washed in radiant amber and golden evening glow.",
     "pan_right"),
    ("b", 0.333, "Sharing meat: dividing portions equally among families with zero hoarding.",
     "Medium shot of community members carving and distributing meat equally among all families; no locked storage, no greed, universal trust.",
     "zoom_in"),
    ("c", 0.334, "Community joy: smiling faces around evening fire ready for dinner.",
     "Close-up of three stick figures smiling warmly, preparing cooking skewers around the lively orange evening fire, celebratory atmosphere.",
     "zoom_out"),
]

# ==========================================
# CHAPTER 4: The 17-hour work week (+18 shots)
# ==========================================
SPLITS[106] = [
    ("a", 0.333, "Establishing: Anthropologist Richard Lee arriving in Kalahari in 1963.",
     "Wide shot of anthropologist Richard Lee arriving in the arid Kalahari borderlands in 1963; vintage canvas-topped jeep parked by dusty thornscrub.",
     "zoom_out"),
    ("b", 0.333, "Tool macro: Swiss mechanical stopwatch and scientific field notebook.",
     "Macro close-up on a wooden field desk: a vintage steel mechanical stopwatch with winding crown, and an open notebook with lined observation columns.",
     "punch_in"),
    ("c", 0.334, "Observer stance: Richard Lee watching from under acacia with notebook.",
     "Medium shot of stick-figure anthropologist standing discreetly under thornbush shade with pencil and clipboard, observing tribal activities.",
     "pan_left"),
]

SPLITS[108] = [
    ("a", 0.5, "Preconception: myth of primitive life as miserable endless starvation.",
     "Conceptual sketch illustrating the old historical myth: stick figure shivering in rags, looking desperate and starving in a harsh barren wasteland.",
     "zoom_in"),
    ("b", 0.5, "Reality clash: giant bold question mark appearing as reality defies myth.",
     "Dramatic graphic split: a bold question mark in red line-art separating the bleak starvation myth from the actual scene of smiling, well-fed bushmen.",
     "punch_in"),
]

SPLITS[111] = [
    ("a", 0.25, "Shadowing labor: Richard Lee timing a hunter with stopwatch in hand.",
     "Medium shot of Richard Lee walking several paces behind a Ju/'hoansi forager, glancing down at the ticking stopwatch in his palm.",
     "pan_right"),
    ("b", 0.25, "Stopwatch tick: needle clicking precisely to 2 hours before stopping.",
     "Macro close-up of the mechanical stopwatch face: needle clicking around to the 2-hour mark and clicking to a full stop for the day.",
     "punch_in"),
    ("c", 0.25, "Notes check: bold checkmark inked across Tuesday field record.",
     "Close-up of paper field log: crisp handwritten rows for Monday, Tuesday, Wednesday, with a bold ink checkmark over 'Work completed: 2 hrs 15 min'.",
     "zoom_in"),
    ("d", 0.25, "Surprised scientist: Richard Lee pushing glasses up, stunned by data.",
     "Medium shot of anthropologist stick figure pushing round glasses up his nose, dot eyes widened in utter astonishment at the empirical findings.",
     "zoom_out"),
]

SPLITS[113] = [
    ("a", 0.5, "Tool repair: hunter sharpening arrow point in just minutes per week.",
     "Close-up of stick figure hunter sitting cross-legged, lightly polishing an arrow point against a sandstone block; quick, effortless maintenance.",
     "zoom_in"),
    ("b", 0.5, "No maintenance: zero complex machinery, zero unpaid repair bills.",
     "Conceptual diagram: simple hunting tools (bow, digger, pouch) encircled in soft green checkmark; no broken engines, no mortgages, no debt.",
     "zoom_out"),
]

SPLITS[115] = [
    ("a", 0.142, "Big bold graphic: giant numbers '17 HOURS / WEEK' circled in red.",
     "Bold typographic infographic: giant clean hand-drawn numbers '17 HOURS / WEEK' prominently centered, circled with energetic red marker stroke.",
     "punch_in"),
    ("b", 0.142, "Daily breakdown bar chart: only 2.4 hours of work per day required.",
     "Clean vertical bar chart: a single day bar divided into 2.4 hours of subsistence labor at the base, with 21.6 hours of complete leisure above.",
     "zoom_in"),
    ("c", 0.142, "Leisure open field: vast expanse of free daytime hours under blue sky.",
     "Wide minimalist landscape: vast open savanna plain under clean pale sky, visual metaphor for uninterrupted vastness of personal free time.",
     "pan_left"),
    ("d", 0.143, "Contrast shadow: silhouette of modern office worker buried under inbox.",
     "Shadow silhouette comparison: faint outline of modern office worker hunched under towering stacks of paperwork and buzzing notification bells.",
     "zoom_in"),
    ("e", 0.143, "Relaxing hunter: Ju/'hoansi man lying on elbows listening to savanna wind.",
     "Medium shot of Ju/'hoansi stick figure lying on elbows in golden grass, eyes half-closed, smiling peacefully in the gentle afternoon breeze.",
     "pan_right"),
    ("f", 0.143, "Children playing: tribal youngsters playing pebble tossing game.",
     "Medium shot of tribal stick-figure children happily tossing rounded pebbles into hollows in the sand, completely free from rigid school bells.",
     "zoom_in"),
    ("g", 0.145, "Harmonious conclusion: perfect balance between survival and rest.",
     "Balanced visual composition: an ancient scale in perfect horizontal balance, with a simple hunting bow on one side and a sleeping figure on the other.",
     "zoom_out"),
]

SPLITS[117] = [
    ("a", 0.5, "Modern calendar: reaching the 17-hour limit by Wednesday noon.",
     "Infographic modern calendar: weekly Monday-to-Friday schedule where the 17-hour mark is reached by Wednesday at 11:30 AM in red marker.",
     "zoom_in"),
    ("b", 0.5, "Exhausted clerk: office worker collapsing face down on keyboard at 2 PM.",
     "Medium shot of modern stick figure in necktie collapsed face down onto a desktop keyboard at 2:00 PM Wednesday, comic steam puffing from head.",
     "punch_in"),
]

SPLITS[119] = [
    ("a", 0.5, "Academic skepticism: scholars debating whether Kalahari was an anomaly.",
     "Medium shot of three university scholar stick figures in suits gesturing skeptically at a blackboard, arguing whether the Kalahari data was unique.",
     "pan_left"),
    ("b", 0.5, "World map transition: world map opens with arrows pointing to continents.",
     "Wide diagrammatic world map illustration: clean black continent outlines on off-white paper, with 4 bright arrows radiating to different cultures.",
     "zoom_out"),
]

SPLITS[120] = [
    ("a", 0.333, "Tanzania Hadza: independent study of Hadza tribe confirms 14-18 hrs.",
     "Wide shot of Lake Eyasi basin in Tanzania: acacia scrubland where Hadza hunter-gatherers live, confirmed to work only 14 to 18 hours per week.",
     "zoom_out"),
    ("b", 0.333, "Hadza forager climbing baobab tree with wooden pegs to harvest honey.",
     "Medium shot of agile Hadza stick figure climbing the trunk of a giant baobab tree using wooden hammered pegs to collect wild honey comb.",
     "pan_left"),
    ("c", 0.334, "Badge verification: green verified stamp '15 HOURS/WEEK' stamped on data.",
     "Graphic stamp: a clean green circular badge stamped onto a field parchment reading 'HADZA: 15 HOURS/WEEK VERIFIED' in crisp line-art.",
     "punch_in"),
]

SPLITS[122] = [
    ("a", 0.5, "Australia Martu: indigenous Martu foragers in Western Desert work < 20 hrs.",
     "Wide shot of the red sand spinifex desert of Western Australia: Martu indigenous stick figure tracking game, working under 20 hours weekly.",
     "pan_right"),
    ("b", 0.5, "Universal biological constant: 15-20 hours was human baseline for 300,000 yrs.",
     "Conceptual summary graphic: a bold glowing timeline stretching 300,000 years with a steady green line hovering at '15-20 Hours Weekly Work'.",
     "zoom_in"),
]

# ==========================================
# CHAPTER 5: The value of social time (+22 shots)
# ==========================================
SPLITS[125] = [
    ("a", 0.5, "Afternoon camp: warm golden light filtering through acacia branches.",
     "Wide shot of the camp bathed in warm afternoon sunlight; long soft shadows, smoke rising lazily, community members gathered in peaceful clusters.",
     "zoom_out"),
    ("b", 0.5, "Two stick figures lounging against a smooth boulder sharing quiet laughs.",
     "Medium shot of two stick figures lounging comfortably against a smooth sun-baked granite boulder, smiling and sharing quiet conversation.",
     "zoom_in"),
]

SPLITS[133] = [
    ("a", 0.5, "Mother combing child's hair with smooth bone comb under shade.",
     "Medium shot of stick figure mother gently combing her child's hair with a polished bone comb under the dappled shade of an acacia tree.",
     "zoom_in"),
    ("b", 0.5, "Close-up of child's relaxed smiling round face feeling loved and safe.",
     "Close-up of the child's round white head leaning into mother's hand, eyes closed contentedly, smiling in absolute safety and warmth.",
     "punch_in"),
]

SPLITS[136] = [
    ("a", 0.333, "Craftsman drilling tiny hole in ostrich eggshell bead with flint awl.",
     "Medium shot of stick figure artisan sitting cross-legged, using a delicate stone awl to drill a center hole through an ostrich eggshell disc.",
     "pan_left"),
    ("b", 0.333, "Macro close-up: threading polished ivory-white beads onto fine sinew cord.",
     "Macro close-up of skilled hands threading circular white eggshell beads onto a slender braided sinew cord, craftsmanship requiring patience.",
     "punch_in"),
    ("c", 0.334, "Artisan holding up finished shimmering bead necklace in sunlight.",
     "Medium shot of artisan holding up the finished long strand of beaded necklace in sunlight, admiring its symmetry with a proud smile.",
     "zoom_out"),
]

SPLITS[138] = [
    ("a", 0.2, "Communal gift exchange (Hxaro) ceremony under central baobab.",
     "Wide shot of the tribal Hxaro gift exchange under the large camp tree; two visiting families meeting with smiles and open palms.",
     "zoom_out"),
    ("b", 0.2, "Hand-to-hand gesture: presenting a beautifully carved wooden bow.",
     "Close-up of two pairs of stick figure hands: one presenting an ornate carved wooden bow, the other receiving it with open respect.",
     "punch_in"),
    ("c", 0.2, "Recipient's joyful expression, hands clasped over chest in gratitude.",
     "Medium shot of recipient clasping hands over heart with a glowing line smile, genuine bond of alliance and mutual survival formed.",
     "zoom_in"),
    ("d", 0.2, "Elders sitting together smoking herb pipe, discussing old genealogies.",
     "Medium shot of two tribal elders sitting on straw mats, sharing a carved wood pipe, conversing without any rush or time pressure.",
     "pan_right"),
    ("e", 0.2, "Children playing tag in the background, dust motes glowing in sunlight.",
     "Wide background view of children laughing and chasing each other playfully, their feet kicking up golden dust motes in the late afternoon sun.",
     "zoom_out"),
]

SPLITS[144] = [
    ("a", 0.25, "Young hunters shooting blunt arrows at melon target on termite mound.",
     "Medium shot of three young stick-figure hunters shooting blunt practice arrows at a round wild melon perched atop a tall red termite mound.",
     "pan_left"),
    ("b", 0.25, "One hunter hits bullseye, celebrating with arms flung high in air.",
     "Dynamic medium shot of one hunter striking the melon, arms raised in high victory cheer, companion laughing and clapping hands.",
     "punch_in"),
    ("c", 0.25, "Friends falling onto grass in laughter, playful camaraderie.",
     "Medium shot of the young friends tumbling playfully onto the soft grass, laughing with open mouths in pure joy and camaraderie.",
     "zoom_in"),
    ("d", 0.25, "Panoramic view of camp alive with free spontaneous social play.",
     "Wide panoramic shot showing entire camp filled with unstructured conversation, craftwork, and play; society functioning through mutual connection.",
     "zoom_out"),
]

SPLITS[145] = [
    ("a", 0.5, "Stick figure gazing out over open savanna in peaceful contemplation.",
     "Medium shot of a stick figure leaning chin on hands, gazing out over the vast golden savanna plain in quiet, serene contemplation.",
     "zoom_in"),
    ("b", 0.5, "A solitary bird soaring high across soft apricot and lilac sky.",
     "Wide scenic shot: a solitary hawk gliding with outstretched wings against a tranquil evening sky painted in soft apricot and lilac hues.",
     "pan_right"),
]

SPLITS[147] = [
    ("a", 0.333, "Boiling mongongo nuts in clay pot over gentle afternoon cooking fire.",
     "Medium shot of a small clay pot resting over three hearth stones, cooking mongongo nuts with gentle steam rising into the calm air.",
     "zoom_in"),
    ("b", 0.333, "Handing roasted marrow bone to elderly member with respectful two-hand gesture.",
     "Close-up of a younger stick figure offering a roasted bone to an elder using both hands, traditional gesture of honor and community care.",
     "punch_in"),
    ("c", 0.334, "Elder enjoying warm food with contented smile beside family.",
     "Medium shot of the elder smiling warmly, savoring the nutritious meal, surrounded by family members eating together in harmony.",
     "zoom_out"),
]

SPLITS[148] = [
    ("a", 0.5, "Visual concept: social bond lines weaving tribe together without police.",
     "Conceptual diagram: 30 stick figures in a circle connected by fine golden thread lines of mutual reciprocity; no walls, prisons, or police needed.",
     "zoom_in"),
    ("b", 0.5, "Resilient social safety net: when one hunter fails, another shares.",
     "Split illustration: one hunter returning with empty hands is immediately welcomed and handed a generous bowl of stew by his neighbor.",
     "pan_left"),
]

SPLITS[154] = [
    ("a", 0.5, "Fossil evidence: healed femur fracture bone circled with teal aura.",
     "Scientific anatomical illustration: fossilized ancient human femur with a thick, fully healed bone callus circled by a soft teal evidence aura.",
     "zoom_in"),
    ("b", 0.5, "Flashback: tribe carrying injured member on stretcher across plains.",
     "Evocative flashback: four stick figures carrying an injured comrade on a stretcher of branches and hide across the plains, refusing to leave him behind.",
     "zoom_out"),
]

SPLITS[155] = [
    ("a", 0.5, "Modern contrast: single stick figure alone in cold modern apartment.",
     "Sad contrast shot: a stick figure sitting alone on a minimalist chair in a high-rise concrete apartment, staring at a blank wall in isolation.",
     "zoom_in"),
    ("b", 0.5, "Ancient warmth: tribal members sleeping nestled under shared hides.",
     "Warm prehistoric contrast: a family of stick figures sleeping cozily nestled together under soft animal hides, protected and never abandoned.",
     "punch_in"),
]

SPLITS[156] = [
    ("a", 0.166, "Dusk settling over savanna: sky shifts from peach to indigo.",
     "Wide panoramic landscape: dusk settling over the African savanna; sky transitioning from soft peach along horizon to deep indigo above.",
     "pan_right"),
    ("b", 0.166, "Stick figures gathering naturally towards central campfire as twilight falls.",
     "Medium shot of tribe members walking slowly from shelters toward the central camp circle as shadows merge into evening.",
     "pan_left"),
    ("c", 0.166, "Lighting the main campfire: dried thatch catching flame with bright sparks.",
     "Close-up of a stick figure touching a spark to dried savanna grass, flame flaring up bright orange and illuminating smiling faces.",
     "punch_in"),
    ("d", 0.167, "Tribe sitting shoulder-to-shoulder in tight warm circle around blaze.",
     "Medium shot of the entire tribe seated shoulder-to-shoulder around the roaring orange campfire, warm firelight dancing on white round heads.",
     "zoom_in"),
    ("e", 0.167, "Glowing red embers pulsating softly with the nighttime breeze.",
     "Close-up shot of glowing charcoal embers pulsating with warm amber light as gentle nocturnal breeze breathes over the hearth.",
     "punch_in"),
    ("f", 0.168, "Campfire silhouette against breathtaking canopy of stars above.",
     "Wide dramatic shot: the small circle of firelight glowing like an ember on the vast dark earth, beneath a breathtaking dome of hand-drawn stars.",
     "zoom_out"),
]

# ==========================================
# CHAPTER 6: Nighttime and the birth of culture (+20 shots)
# ==========================================
SPLITS[161] = [
    ("a", 0.5, "Title document: Anthropologist Polly Wiessner's landmark 2014 study.",
     "Scientific paper graphic: title page reading 'Polly Wiessner: Embers for the Soul (2014)' with clean marker pen illustration of campfire.",
     "zoom_in"),
    ("b", 0.5, "Cassette reel spinning slowly in portable recorder in night camp.",
     "Close-up of a vintage portable audio cassette recorder with twin reels turning gently, capturing fireside voices in the desert darkness.",
     "punch_in"),
]

SPLITS[162] = [
    ("a", 0.5, "Archive stacks: 40 years of audio cassette tapes and research notebooks.",
     "Still life composition: neatly stacked vintage audio cassette tapes labeled 1974-2014 alongside thick spiral field notebooks filled with notes.",
     "zoom_in"),
    ("b", 0.5, "Researcher stick figure wearing headphones, transcribing campfire lore.",
     "Medium shot of researcher stick figure wearing large retro over-ear headphones, jotting transcription notes under a small desk lamp.",
     "pan_left"),
]

SPLITS[163] = [
    ("a", 0.5, "Daytime talk infographic: 75% practical hunting, food, and complaints.",
     "Daytime diagram: stick figures under sun with speech bubbles containing arrows, animal footprints, berries, and economic tallies (75%).",
     "zoom_in"),
    ("b", 0.5, "Nighttime talk infographic: 81% myths, ghost stories, jokes, and songs.",
     "Nighttime diagram: stick figures around fire with speech bubbles containing soaring birds, stars, mythical animals, and musical notes (81%).",
     "punch_in"),
]

SPLITS[171] = [
    ("a", 0.5, "Elder storyteller gesturing towards night sky, smoke forming visions.",
     "Medium shot of elder stick figure gesturing with animated arms towards the dark sky, campfire smoke twisting into dreamlike animal silhouettes.",
     "zoom_in"),
    ("b", 0.5, "Starry celestial creatures: celestial lion and hunter walking the Milky Way.",
     "Wide overhead view: constellation drawings in white chalk lines showing a celestial lion and cosmic hunter leaping across the starry Milky Way.",
     "zoom_out"),
]

SPLITS[172] = [
    ("a", 0.5, "Desert night map: distant campfires linked by glowing story threads.",
     "Overhead map illustration: dark Kalahari desert dotted with small isolated glowing campfires, connected by luminous golden web lines of shared lore.",
     "pan_right"),
    ("b", 0.5, "Wanderer arriving at distant camp, welcomed immediately like brother.",
     "Medium shot of a lone traveling stick figure arriving at an unfamiliar campfire, greeted with open arms and shared meat through common stories.",
     "zoom_in"),
]

SPLITS[179] = [
    ("a", 0.142, "Fire dying down: red coals shimmering as story circle disperses.",
     "Medium shot of the campfire dying down to soft crimson coals; tribe members quietly stretching and heading toward their thatch dome shelters.",
     "zoom_out"),
    ("b", 0.142, "Crawling under animal skin blankets inside cozy grass hut.",
     "Medium shot of stick figure crawling inside domed grass shelter, pulling soft warm hide blankets over shoulders onto straw bedding.",
     "zoom_in"),
    ("c", 0.142, "Close-up of sleeping face: peaceful breathing in natural darkness.",
     "Close-up of stick figure's head resting on leather-wrapped roll, peaceful curved sleeping eyes, breathing in steady unmedicated rhythm.",
     "punch_in"),
    ("d", 0.143, "First sleep concept: deep slow-wave slumber free from modern anxiety.",
     "Conceptual diagram: an ancient human sleeping soundly beneath a crescent moon; soft blue tranquil aura representing restorative slow-wave sleep.",
     "pan_left"),
    ("e", 0.143, "Moon gliding through starry sky above silhouetted baobab branches.",
     "Serene landscape: silver crescent moon moving slowly through the indigo night sky between the twisted silhouette branches of a baobab tree.",
     "zoom_out"),
    ("f", 0.143, "A gentle cooling night breeze whispering through the quiet thatch roof.",
     "Close-up of gentle desert breeze rustling dry grass thatch of shelter roof, serene tranquil ambiance under diamond stars.",
     "pan_right"),
    ("g", 0.145, "Entire campsite wrapped in absolute, healing silence under starlight.",
     "Wide landscape shot: the entire camp sleeping under the vast night sky, absolute silence and peace undisturbed by electric lighting.",
     "zoom_in"),
]

SPLITS[180] = [
    ("a", 0.333, "Biphasic sleep timeline: 4 hours sleep, 1 hour waking, 4 hours sleep.",
     "Infographic timeline: a graceful curve showing 'First Sleep' (9pm-1am), 'The Watch' waking interval (1am-2am), and 'Second Sleep' (2am-6am).",
     "zoom_in"),
    ("b", 0.333, "Stick figure waking naturally around 1 AM feeling calm and lucid.",
     "Medium shot of stick figure waking naturally inside shelter around 1:00 AM; no grogginess, no racing heartbeat, perfectly alert and calm.",
     "punch_in"),
    ("c", 0.334, "Stretching gently in the cool moonlit air with zero insomnia panic.",
     "Stick figure sitting up in moonlit doorway of grass shelter, gently rotating shoulders and breathing the cool crisp midnight air.",
     "zoom_out"),
]

SPLITS[183] = [
    ("a", 0.333, "Stepping out into midnight air, gazing up at diamond star canopy.",
     "Medium shot of stick figure stepping out onto cool sand under brilliant starlight, gazing upward at the shimmering Milky Way with serene wonder.",
     "zoom_out"),
    ("b", 0.333, "Stirring the hearth: adding small dry branch to revive gentle flames.",
     "Close-up of stick figure placing a slender dry acacia twig onto coals, a playful tongue of yellow flame leaping up and casting golden light.",
     "punch_in"),
    ("c", 0.334, "Neighbor stick figure emerges from nearby shelter, smiling in greeting.",
     "Medium shot of a neighbor stick figure quietly emerging from an adjacent shelter, smiling and padding softly over to join by the revived fire.",
     "zoom_in"),
]

SPLITS[185] = [
    ("a", 0.25, "Two midnight companions whispering quietly beside the renewed fire.",
     "Medium shot of the two midnight friends sitting by the fire, talking in soft hushed whispers, gestures gentle and intimate.",
     "zoom_in"),
    ("b", 0.25, "Soft humming: one taps rhythm on dried calabash in midnight stillness.",
     "Close-up of hands gently tapping a soothing rhythm on a dried hollow calabash gourd, soft musical notes floating into the night.",
     "punch_in"),
    ("c", 0.25, "A mother nursing infant in tranquil serenity by her doorway.",
     "Medium shot of a mother stick figure sitting by her shelter entrance softly nursing her sleeping baby in the calm, unhurried midnight air.",
     "pan_left"),
    ("d", 0.25, "Natural meditation: mind floating in peaceful alpha wave tranquility.",
     "Conceptual illustration: stick figure silhouette sitting in meditation beside embers, soft pastel ripples radiating from head representing peace.",
     "zoom_out"),
]

SPLITS[186] = [
    ("a", 0.5, "Yawning gently: returning to bedding as eyelids grow pleasantly heavy.",
     "Medium shot of stick figure standing up from fire, stretching arms with a wide pleasant yawn, ready to return to warm hide bed.",
     "zoom_in"),
    ("b", 0.5, "Drifting into sweet second sleep: dreaming under fading stars.",
     "Close-up of stick figure slipping under soft furs, closing eyes with a faint smile, drifting effortlessly into dream-rich second sleep.",
     "punch_in"),
]

SPLITS[188] = [
    ("a", 0.5, "Dawn horizon glowing rose and gold, morning birds beginning chorus.",
     "Wide sunrise shot: pale rose and amber light washing over the eastern horizon, stylized morning songbirds perched on acacia twigs singing.",
     "pan_right"),
    ("b", 0.5, "Stick figure sitting up refreshed, energized for another timeless day.",
     "Medium shot of stick figure sitting up outside shelter in crisp dawn sunlight, arms energized and posture upright, completely rejuvenated.",
     "zoom_in"),
]

# ==========================================
# CHAPTER 7: The trap of agriculture (+28 shots)
# ==========================================
SPLITS[192] = [
    ("a", 0.333, "Wide shot: Fertile Crescent river valley winding through lush hills.",
     "Wide shot of the Fertile Crescent river valley in lush olive greens and silt browns; Zagros mountains in background under bright dawn.",
     "zoom_out"),
    ("b", 0.333, "Hunter stick figure noticing wild wheat stalks heavy with golden grain.",
     "Medium shot of a hunter-gatherer stick figure stopping near a riverbank, curiously examining tall stalks of wild einkorn wheat.",
     "pan_left"),
    ("c", 0.334, "Tasting grain: rubbing grains between palms and chewing sweet starch.",
     "Close-up of stick figure's hands rubbing a wheat ear between palms, blowing away the chaff and tasting the raw sweet grain seeds.",
     "punch_in"),
]

SPLITS[193] = [
    ("a", 0.5, "Stick figure kneeling in damp alluvial silt digging a neat furrow.",
     "Medium shot of a stick figure kneeling in dark, moist river silt, using a pointed wooden stick to carve a straight planting furrow.",
     "pan_left"),
    ("b", 0.5, "Dropping golden wheat seeds: close-up of seeds falling into dark earth.",
     "Extreme close-up of a stick figure's hand gently dropping grains of wheat into a furrowed trench in damp brown soil, sun gleaming on the seeds.",
     "punch_in"),
]

SPLITS[195] = [
    ("a", 0.5, "Sprouting wheat: green shoots rising in neat rows across plowed dirt.",
     "Low-angle shot of bright green wheat shoots sprouting upwards in uniform rows from freshly tilled soil, dew drops sparkling on blades.",
     "zoom_in"),
    ("b", 0.5, "Smiling farmer: stick figure standing proudly admiring obedient crop.",
     "Medium shot of stick figure farmer standing hands on hips, smiling proudly at the obedient green sprouts, thinking famine is solved forever.",
     "zoom_out"),
]

SPLITS[196] = [
    ("a", 0.333, "Infographic: 1 acre of wheat producing 1000 lbs vs 100 acres for 1 deer.",
     "Infographic comparison: a small patch of wheat field yielding a mountain of grain sacks versus an enormous forest yielding a single deer.",
     "zoom_in"),
    ("b", 0.333, "Big bold arrow: 'CALORIES PER ACRE: +1000%' leaping upward.",
     "Graphic arrow diagram: a thick golden arrow surging vertically labeled '+1000% CALORIES', celebrating apparent triumph over scarcity.",
     "punch_in"),
    ("c", 0.334, "Early Neolithic village stacking grain sacks in high celebratory piles.",
     "Medium shot of Neolithic villagers stacking woven sacks of grain into a towering mound outside mud huts, waving their hands in celebration.",
     "zoom_out"),
]

SPLITS[199] = [
    ("a", 0.333, "Population boom: farming mother surrounded by 5 crying babies.",
     "Medium shot of a farmer mother stick figure inside a mud hut, overwhelmed with five small children crying for porridge simultaneously.",
     "zoom_in"),
    ("b", 0.333, "Infographic contrast: forager 1 birth / 4 yrs vs farmer 1 birth / year.",
     "Infographic comparison: hunter-gatherer mother carrying 1 spaced child every 4 years vs sedentary farmer mother giving birth every 12 months.",
     "punch_in"),
    ("c", 0.334, "Desperate farmer father looking at grain bin emptying twice as fast.",
     "Medium shot of farmer father peering into a woven grain silo, alarmed to see grain disappearing rapidly before next season arrives.",
     "zoom_out"),
]

SPLITS[201] = [
    ("a", 0.333, "Mathematical trap: 10x more food, but 12x more hungry mouths.",
     "Diagrammatic equation: food production increased by 10x, but population exploded by 12x; the balance tipping into chronic perpetual shortage.",
     "zoom_in"),
    ("b", 0.333, "Empty grain bowl: hungry hands reaching out from all corners of frame.",
     "Close-up of a cracked ceramic bowl holding only a few sparse grain kernels, several thin stick-figure hands reaching toward it eagerly.",
     "punch_in"),
    ("c", 0.334, "Farmer sweating under pressure, realizing there is no turning back.",
     "Medium shot of farmer stick figure clutching head in hands, sweat beads popping as realization dawns that hunting can no longer feed this crowd.",
     "zoom_out"),
]

SPLITS[202] = [
    ("a", 0.5, "Crowded village: mud huts packed cheek by jowl with muddy alleyways.",
     "Wide shot of an early Neolithic permanent settlement: mud-brick homes crowded tightly together, open refuse ditches, smoke trapped between walls.",
     "zoom_out"),
    ("b", 0.5, "Flies and disease: sick stick figures coughing around livestock pens.",
     "Medium shot of villagers coughing with curved sick lines around muddy animal pens; swarms of black flies buzzing around penned goats.",
     "zoom_in"),
]

SPLITS[203] = [
    ("a", 0.5, "Monoculture meal: bland gray porridge in rough ceramic bowl every day.",
     "Close-up still life: a cracked unadorned clay bowl filled with thick gray barley gruel, lacking any meat, wild berries, or fresh nutrients.",
     "zoom_in"),
    ("b", 0.5, "Decayed teeth: dental diagram showing extensive cavities and worn enamel.",
     "Scientific close-up diagram of farmer's teeth: dark charcoal cavity holes in molars, pitted enamel worn flat by abrasive stone-mill grit.",
     "punch_in"),
]

SPLITS[207] = [
    ("a", 0.333, "Work week explosion: chart comparing 17 hours vs 60+ hours of labor.",
     "Dramatic graphic bar comparison: hunter-gatherer 17-hour bar in calm green vs agricultural 60-hour bar towering in alarming terracotta red.",
     "zoom_in"),
    ("b", 0.333, "Waking before dawn: farmer struggling out of straw pallet at 4:30 AM.",
     "Medium shot of farmer stick figure struggling to sit up in dark mud hut at 4:30 AM, body stiff, face grimacing with aches and sore muscles.",
     "punch_in"),
    ("c", 0.334, "Marching into fields with heavy wooden tools under freezing morning fog.",
     "Wide silhouette shot: line of hunched farmers carrying heavy wooden plows and sickles, trudging into cold mist before sunrise.",
     "pan_right"),
]

SPLITS[212] = [
    ("a", 0.5, "Digging irrigation canal: swinging heavy mattock into rock-hard clay.",
     "Medium shot of farmer swinging a heavy stone mattock into baked clay soil, digging an irrigation trench under blazing sun.",
     "pan_left"),
    ("b", 0.5, "Carrying water: heavy terracotta jars balanced across aching yoke.",
     "Medium shot of farmer carrying two massive earthenware jars filled with river water slung across a wooden shoulder yoke, spine bent in strain.",
     "zoom_in"),
]

SPLITS[213] = [
    ("a", 0.125, "Locust plague: dark swarm of locusts blotting out midday sun.",
     "Wide shot of sky turning black as an immense swarm of locusts descends upon the ripening golden wheat field, buzzing wings filling air.",
     "zoom_out"),
    ("b", 0.125, "Farmer waving burning torch in desperation to save the wheat crop.",
     "Action medium shot: farmer running between wheat rows frantically waving a smoking torch, trying to repel thousands of voracious insects.",
     "punch_in"),
    ("c", 0.125, "Rodent infestation: mice and rats gnawing through woven thatch granary.",
     "Close-up of granary wall: wild rodents gnawing through thatch and grain sacks, wheat kernels spilling out onto dirt floor.",
     "zoom_in"),
    ("d", 0.125, "Severe drought: parched earth cracked into deep fissures, wheat dying.",
     "Low-angle shot of cracked parched clay soil, withered brown wheat stalks bending limp and dead under ruthless cloudless sky.",
     "pan_right"),
    ("e", 0.125, "Hailstorm disaster: ice stones hammering down, flattening mature stalks.",
     "Dramatic shot of white hail stones pelting down violently, flattening mature wheat heads into mud hours before harvest.",
     "punch_in"),
    ("f", 0.125, "Night watch: farmer standing guard in pouring rain with wooden spear.",
     "Medium shot of farmer shivering in heavy rain at midnight, holding a fire-hardened wooden spear to protect fields from wild boar.",
     "zoom_in"),
    ("g", 0.125, "Exhaustion collapse: farmer weeping on knees in ruined muddy furrow.",
     "Medium shot of farmer collapsing onto knees in muddy furrow, hands clutching head, weeping in complete despair over destroyed crops.",
     "zoom_out"),
    ("h", 0.125, "Permanent anxiety: wide stressed eyes realizing agriculture never sleeps.",
     "Close-up of farmer's large round white head: wide anxious dot eyes, sweat and rain streaming, realizing farming requires perpetual vigilance.",
     "punch_in"),
]

SPLITS[216] = [
    ("a", 0.333, "Granary surplus: high mud granary overflowing with guarded barley sacks.",
     "Wide shot of massive communal granary fortress built of thick mud bricks, stuffed with thousands of grain sacks under heavy wooden beam roof.",
     "zoom_out"),
    ("b", 0.333, "Greed and envy: neighbors peering suspiciously at locked granary door.",
     "Medium shot of stick figures eyeing the granary with suspicion, hands hovering over flint daggers, mutual trust completely shattered.",
     "zoom_in"),
    ("c", 0.334, "Thieves in the night: shadowy figures climbing stockade wall to steal grain.",
     "Dramatic night shot: shadowy silhouettes creeping over a sharpened log palisade wall, clutching empty sacks to raid stored food.",
     "punch_in"),
]

SPLITS[218] = [
    ("a", 0.5, "Hierarchy pyramid: high king and priest on top, soldiers, peasants below.",
     "Clean diagrammatic pyramid: golden crown king and priest at apex, bronze-armored soldiers in middle tier, hundreds of bent peasants at base.",
     "zoom_in"),
    ("b", 0.5, "Armed guards: bronze spear soldiers keeping watch over bent laborers.",
     "Medium shot of two upright soldiers in bronze helmets holding long spears, standing watch over submissive peasants harvesting wheat.",
     "zoom_out"),
]

SPLITS[220] = [
    ("a", 0.5, "Tax collector recording bushels on cuneiform clay tablet with stylus.",
     "Medium shot of royal tax collector in fine robes pressing wedge-shaped stylus into soft clay tablet, carting away 80% of the harvest.",
     "zoom_in"),
    ("b", 0.5, "Farmer family left staring at tiny remaining pouch of grain for winter.",
     "Medium shot of peasant farmer family staring at a single pathetic pouch of grain left in corner, barely enough to survive until spring.",
     "punch_in"),
]

SPLITS[221] = [
    ("a", 0.5, "Temple bronze bell ringing loudly, summoning workers at crack of dawn.",
     "Close-up of a heavy bronze bell swinging and clanging atop temple tower, bold sound wave arcs commanding all humans into labor.",
     "punch_in"),
    ("b", 0.5, "Peasants marching in lockstep rows into fields under overseer's gaze.",
     "Wide shot of peasants marching in rigid lockstep columns into the fields, heads down, individual autonomy and freedom erased.",
     "pan_right"),
]

SPLITS[224] = [
    ("a", 0.5, "Cross-section: Skeleton #2 buried beneath modern paved asphalt road.",
     "Cross-section diagram: sleek asphalt highway on top with modern car, and deep below in compressed sediment rests Skeleton #2 clutching a sickle.",
     "zoom_out"),
    ("b", 0.5, "Close-up of skeleton's hand curled around flint sickle, eternal symbol.",
     "Close-up of Skeleton #2's ancient bone fingers curled tightly around a flint sickle, the eternal physical evidence of humanity's ancient trap.",
     "zoom_in"),
]

# ==========================================
# CHAPTER 8: Trading freedom for security (+12 shots)
# ==========================================
SPLITS[226] = [
    ("a", 0.333, "Modern alarm clock dispensing endless roll of printed paper receipt.",
     "Close-up of modern digital alarm clock on bedside table violently spewing a continuous roll of white paper receipt across bedroom floor.",
     "zoom_in"),
    ("b", 0.333, "Macro receipt: '10,000 YEARS UNPAID OVERTIME SINCE AGRICULTURAL REVOLUTION'.",
     "Macro close-up on receipt tape: bold printed text 'INVOICE: 10,000 YEARS UNPAID OVERTIME' with itemized dates from 8000 BC to 2026.",
     "punch_in"),
    ("c", 0.334, "Receipt tape morphs into heavy iron chain wrapped around figure's ankle.",
     "Conceptual visual metaphor: the endless paper receipt unrolling out the door morphs into heavy black iron chain links locked around the modern stick figure's ankle.",
     "zoom_out"),
]

SPLITS[227] = [
    ("a", 0.5, "Flashback: ancient hunter-gatherer resting under acacia at golden sunset.",
     "Infographic nostalgia: an ancient hunter-gatherer stick figure resting calmly under an acacia tree, watching a tranquil sunset.",
     "zoom_out"),
    ("b", 0.5, "Luminous typography: '15 - 20 HOURS / WEEK' glowing above ancient plains.",
     "Typography graphic: glowing soft emerald numbers '15 - 20 HOURS / WEEK' hovering serenely over open savanna, representing biological heritage.",
     "zoom_in"),
]

SPLITS[228] = [
    ("a", 0.5, "Scientific balance scale: healthy Skeleton #1 soaring high with wellness.",
     "Scientific balance scale: healthy Skeleton #1 holding a laurel wreath of wellness, towering over modern sedentary ailments.",
     "zoom_in"),
    ("b", 0.5, "Macro bone: unblemished dense limb bones gleaming with vital health.",
     "Macro diagram of Skeleton #1's thick femur and intact spinal column, glowing with clean white vitality and zero osteoarthritis.",
     "punch_in"),
]

SPLITS[230] = [
    ("a", 0.2, "Campfire circle: golden fire illuminating faces under Milky Way canopy.",
     "Golden campfire illuminating faces under the starry Milky Way, stories weaving peace and solidarity across the community.",
     "zoom_out"),
    ("b", 0.2, "Musician playing bone flute: gentle notes floating into quiet night.",
     "Medium shot of ancient stick figure playing a five-hole swan bone flute, delicate hand-drawn musical curls drifting towards stars.",
     "zoom_in"),
    ("c", 0.2, "Family nestled under soft furs, drifting into natural first sleep.",
     "Medium shot of parents and child nestled under soft hide blankets, eyes closed in deep, natural, undisturbed first sleep.",
     "punch_in"),
    ("d", 0.2, "Midnight waking: soft conversation and shared smiles beside glowing coals.",
     "Medium shot of two friends sitting by glowing red embers in peaceful midnight hour, chatting in whispers, utterly free from worry.",
     "pan_left"),
    ("e", 0.2, "Waking naturally at sunrise without an alarm clock, refreshed and free.",
     "Wide dawn shot: tribe members rising as sun peeks over horizon, bodies energized, minds calm, zero mechanical alarms in existence.",
     "zoom_out"),
]

SPLITS[236] = [
    ("a", 0.333, "Modern desk: sticky notes, ringing smartphone, flashing 'URGENT' email.",
     "Close-up of cluttered modern office desk: laptop screen flashing red 'URGENT', smartphone vibrating with reminder buzzes, coffee cup.",
     "zoom_in"),
    ("b", 0.333, "Stick figure clutching temples as dark storm cloud swirls overhead.",
     "Medium shot of modern stick figure in necktie clutching temples, small dark storm cloud with red lightning bolts swirling above head.",
     "punch_in"),
    ("c", 0.334, "Digital clock blinking 08:59 as heart rate graph spikes in anxiety.",
     "Conceptual split: digital numbers '08:59' flashing aggressively beside an erratic red heart-rate electrocardiogram spiking in panic.",
     "zoom_out"),
]

SPLITS[240] = [
    ("a", 0.5, "Alarm clock on bedside table, red digital glow fading to quiet gray.",
     "Close-up of the alarm clock on the nightstand: its aggressive ringing vibrations have halted, red LED glow softening to gentle gray.",
     "zoom_in"),
    ("b", 0.5, "Stick figure hand firmly presses off button, silencing the machine.",
     "Close-up of stick figure's hand reaching out with calm deliberate intention, pressing the off button; total quiet fills the bedroom.",
     "punch_in"),
]

SPLITS[241] = [
    ("a", 0.5, "Stick figure sitting on edge of bed in soft morning light, eyes calm.",
     "Medium shot of stick figure sitting peacefully on the edge of the bed; soft golden morning light streaming across bare feet on wooden floor.",
     "zoom_in"),
    ("b", 0.5, "Looking at open hands, recognizing ancestral strength and biology within.",
     "Close-up of stick figure holding open hands in morning light, calm round white head contemplating the 300,000-year legacy in human DNA.",
     "punch_in"),
]

def main():
    print(f"Loading Chapter 1 blind manifest from {MANIFEST_CH1_BLIND_PATH}...")
    with open(MANIFEST_CH1_BLIND_PATH, encoding="utf-8") as f:
        ch1_blind_data = json.load(f)
    shots_ch1_blind = ch1_blind_data["shots"]
    assert len(shots_ch1_blind) == 34, f"Expected 34 Ch1 blind shots, got {len(shots_ch1_blind)}"

    print(f"Loading base manifest from {MANIFEST_245_PATH}...")
    with open(MANIFEST_245_PATH, encoding="utf-8") as f:
        base_data = json.load(f)

    shots_245 = base_data["shots"]
    assert len(shots_245) == 245, f"Expected 245 shots, got {len(shots_245)}"

    new_shots = []
    global_shot_idx = 0

    # Track chapter statistics
    chapter_shot_counts = {}
    chapter_added_subbeats = {}

    # 1. Process Chapter 1 from 34 blind-test beats + 9 sub-beats = 43 shots
    chapter_shot_counts[1] = 0
    chapter_added_subbeats[1] = 0
    for bshot in shots_ch1_blind:
        idx = bshot["shot_index"]
        vd = bshot.get("visual_direction", {})
        orig_dur = round(bshot["timing"]["duration_seconds"], 2)
        orig_start = round(bshot["timing"]["start_seconds_chapter"], 2)
        orig_remotion_at = round(bshot["timing"]["remotion_at_seconds"], 2)
        orig_filename = bshot["target_filename"]
        vo_vi = bshot.get("voiceover_vi", "")
        act_desc = vd.get("action_description_vi") or vd.get("action_description") or ""
        eff = vd.get("remotion_effect") or "zoom_in"
        raw_prompt = vd.get("ai_prompt", "")

        if idx in CH1_BLIND_SPLITS:
            ratio, b_act_desc, b_visual_action, b_eff = CH1_BLIND_SPLITS[idx]
            chapter_added_subbeats[1] += 1
            dur_a = round(orig_dur * ratio, 2)
            dur_b = round(orig_dur - dur_a, 2)
            end_a = round(orig_start + dur_a, 2)
            end_b = round(orig_start + orig_dur, 2)

            # Beat A preserves existing filename on disk (ch1_blind_beat_XX_YY.YYs.jpg)
            global_shot_idx += 1
            chapter_shot_counts[1] += 1
            new_shots.append(
                {
                    "shot_index": global_shot_idx,
                    "original_shot_index": idx,
                    "sub_beat_id": f"{idx}a",
                    "chapter_number": 1,
                    "chapter_title": "The mystery of modern time",
                    "scene_id": bshot["scene_id"],
                    "shot_in_chapter": "",
                    "target_filename": orig_filename,
                    "timing": {
                        "start_seconds_original": orig_start,
                        "end_seconds_original": end_a,
                        "duration_seconds": dur_a,
                        "remotion_at_seconds": orig_remotion_at,
                    },
                    "remotion_effect": eff,
                    "draw_on": bool(vd.get("draw_on", False)),
                    "script": {"voiceover_vi": vo_vi, "voiceover_en": ""},
                    "visual_direction": {
                        "action_description": act_desc,
                        "ai_prompt": raw_prompt,
                        "negative_prompt": NEG_PROMPT,
                    },
                }
            )

            # Beat B gets new filename ch1_blind_beat_{idx:02d}b_{end_a:05.2f}s.jpg
            global_shot_idx += 1
            chapter_shot_counts[1] += 1
            fname_b = f"ch1_blind_beat_{idx:02d}b_{end_a:05.2f}s.jpg"
            new_shots.append(
                {
                    "shot_index": global_shot_idx,
                    "original_shot_index": idx,
                    "sub_beat_id": f"{idx}b",
                    "chapter_number": 1,
                    "chapter_title": "The mystery of modern time",
                    "scene_id": bshot["scene_id"],
                    "shot_in_chapter": "",
                    "target_filename": fname_b,
                    "timing": {
                        "start_seconds_original": end_a,
                        "end_seconds_original": end_b,
                        "duration_seconds": dur_b,
                        "remotion_at_seconds": round(orig_remotion_at + dur_a, 2),
                    },
                    "remotion_effect": b_eff,
                    "draw_on": False,
                    "script": {"voiceover_vi": vo_vi, "voiceover_en": ""},
                    "visual_direction": {
                        "action_description": b_act_desc,
                        "ai_prompt": make_prompt(b_visual_action),
                        "negative_prompt": NEG_PROMPT,
                    },
                }
            )
        else:
            global_shot_idx += 1
            chapter_shot_counts[1] += 1
            new_shots.append(
                {
                    "shot_index": global_shot_idx,
                    "original_shot_index": idx,
                    "sub_beat_id": None,
                    "chapter_number": 1,
                    "chapter_title": "The mystery of modern time",
                    "scene_id": bshot["scene_id"],
                    "shot_in_chapter": "",
                    "target_filename": orig_filename,
                    "timing": {
                        "start_seconds_original": orig_start,
                        "end_seconds_original": round(orig_start + orig_dur, 2),
                        "duration_seconds": orig_dur,
                        "remotion_at_seconds": orig_remotion_at,
                    },
                    "remotion_effect": eff,
                    "draw_on": bool(vd.get("draw_on", False)),
                    "script": {"voiceover_vi": vo_vi, "voiceover_en": ""},
                    "visual_direction": {
                        "action_description": act_desc,
                        "ai_prompt": raw_prompt,
                        "negative_prompt": NEG_PROMPT,
                    },
                }
            )

    # 2. Process Chapters 2..8 from shots_245 + SPLITS
    for shot in shots_245:
        idx = shot["shot_index"]
        ch = shot["chapter_number"]
        if ch == 1:
            continue
        chapter_shot_counts.setdefault(ch, 0)
        chapter_added_subbeats.setdefault(ch, 0)

        # Check if this shot is to be split
        if idx in SPLITS:
            split_defs = SPLITS[idx]
            n_splits = len(split_defs)
            chapter_added_subbeats[ch] += (n_splits - 1)

            orig_dur = round(shot["timing"]["duration_seconds"], 2)
            orig_start = round(shot["timing"]["start_seconds_original"], 2)
            orig_remotion_at = round(shot["timing"]["remotion_at_seconds"], 2)
            orig_filename = shot["target_filename"]
            # e.g. shot_02_159.76s.jpg -> prefix 'shot_02', ext '.jpg'
            fname_parts = orig_filename.rsplit("_", 1)
            fname_prefix = fname_parts[0]

            # Calculate individual durations
            accum_dur = 0.0
            split_durs = []
            for i, (letter, ratio, action_desc, visual_action, effect) in enumerate(split_defs):
                if i == n_splits - 1:
                    d = round(orig_dur - accum_dur, 2)
                else:
                    d = round(orig_dur * ratio, 2)
                    accum_dur += d
                split_durs.append(d)

            # Build sub-beats
            curr_start = orig_start
            curr_remotion_at = orig_remotion_at

            for i, (letter, ratio, action_desc, visual_action, effect) in enumerate(split_defs):
                global_shot_idx += 1
                chapter_shot_counts[ch] += 1
                dur = split_durs[i]
                curr_end = round(curr_start + dur, 2)

                subbeat_id = f"{idx}{letter}"
                target_fname = f"{fname_prefix}{letter}_{curr_start:.2f}s.jpg"

                subbeat_shot = {
                    "shot_index": global_shot_idx,
                    "original_shot_index": idx,
                    "sub_beat_id": subbeat_id,
                    "chapter_number": ch,
                    "chapter_title": shot["chapter_title"],
                    "scene_id": shot["scene_id"],
                    "shot_in_chapter": f"{shot['shot_in_chapter']} (Beat {letter})",
                    "target_filename": target_fname,
                    "timing": {
                        "start_seconds_original": curr_start,
                        "end_seconds_original": curr_end,
                        "duration_seconds": dur,
                        "remotion_at_seconds": round(curr_remotion_at, 2)
                    },
                    "remotion_effect": effect,
                    "script": shot.get("script", {}),
                    "visual_direction": {
                        "action_description": action_desc,
                        "ai_prompt": make_prompt(visual_action),
                        "negative_prompt": NEG_PROMPT
                    }
                }
                new_shots.append(subbeat_shot)
                curr_start = curr_end
                curr_remotion_at += dur

        else:
            # Unsplit shot
            global_shot_idx += 1
            chapter_shot_counts[ch] += 1

            # Clean any legacy subtitle instruction if present
            vd = shot.get("visual_direction", {})
            action_desc = vd.get("action_description", "")
            raw_prompt = vd.get("ai_prompt", "")
            
            # Clean prompt to guarantee 100% invariant
            cleaned_prompt = raw_prompt.replace("Keep the bottom 20% of the frame plain and unobstructed for subtitles.", "").strip()
            while "  " in cleaned_prompt:
                cleaned_prompt = cleaned_prompt.replace("  ", " ")

            unsplit_shot = {
                "shot_index": global_shot_idx,
                "original_shot_index": idx,
                "sub_beat_id": None,
                "chapter_number": ch,
                "chapter_title": shot["chapter_title"],
                "scene_id": shot["scene_id"],
                "shot_in_chapter": shot["shot_in_chapter"],
                "target_filename": shot["target_filename"],
                "timing": shot["timing"],
                "remotion_effect": shot.get("remotion_effect", "hold"),
                "script": shot.get("script", {}),
                "visual_direction": {
                    "action_description": action_desc,
                    "ai_prompt": cleaned_prompt,
                    "negative_prompt": vd.get("negative_prompt", NEG_PROMPT)
                }
            }
            new_shots.append(unsplit_shot)

    # Now fix shot_in_chapter to reflect new totals per chapter
    # Group shots by chapter to assign 'K/Total'
    ch_totals = {}
    for s in new_shots:
        ch = s["chapter_number"]
        ch_totals[ch] = ch_totals.get(ch, 0) + 1

    ch_counters = {}
    for s in new_shots:
        ch = s["chapter_number"]
        ch_counters[ch] = ch_counters.get(ch, 0) + 1
        sub_id = s.get("sub_beat_id")
        if sub_id:
            s["shot_in_chapter"] = f"{ch_counters[ch]}/{ch_totals[ch]} (Beat {sub_id})"
        else:
            s["shot_in_chapter"] = f"{ch_counters[ch]}/{ch_totals[ch]}"

    # Validate invariants
    print("\n=== Validating Invariants ===")
    long_holds = [s for s in new_shots if s["timing"]["duration_seconds"] > 3.0]
    assert len(long_holds) == 0, f"Found {len(long_holds)} shots with duration > 3.0s! {long_holds}"
    print("PASS: 0 shots with duration > 3.0s.")

    subtitle_mentions = [
        s for s in new_shots 
        if "bottom 20%" in s["visual_direction"]["ai_prompt"] or "unobstructed for subtitles" in s["visual_direction"]["ai_prompt"]
    ]
    assert len(subtitle_mentions) == 0, f"Found {len(subtitle_mentions)} subtitle mentions!"
    print("PASS: 0 subtitle margin mentions in AI prompts.")

    assert len(new_shots) == 382, f"Expected 382 total shots, got {len(new_shots)}"
    print(f"PASS: Total shot count is exactly {len(new_shots)}.")

    out_data = {
        "version": "2.0.0-option-b",
        "title": "Ancient Humans — Option B Dynamic Pacing Manifest (382 Beats)",
        "total_shots": len(new_shots),
        "total_original_shots": 245,
        "total_added_subbeats": len(new_shots) - 245,
        "video_aspect_ratio": "16:9",
        "resolution": "1920x1080",
        "fps": 30,
        "pacing_contract": "Max shot duration <= 2.2s. Dynamic camera shifts between establishing, close-up, and action beats.",
        "visual_cast_invariant": "Anonymous Stick Figure (solid round white head, 4px bold black outline, simple dot/line eyes, thin stick limbs, off-white background).",
        "chapter_breakdown": {
            f"chapter_{ch}": {
                "original_shots": count - chapter_added_subbeats[ch],
                "added_subbeats": chapter_added_subbeats[ch],
                "total_shots": count
            }
            for ch, count in ch_totals.items()
        },
        "shots": new_shots
    }

    OUTPUT_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully wrote Option B manifest to: {OUTPUT_MANIFEST_PATH}")
    print(f"File size: {OUTPUT_MANIFEST_PATH.stat().st_size:,} bytes")

    print("\nChapter breakdown summary:")
    for ch, count in sorted(ch_totals.items()):
        print(f"  Chapter {ch}: {ch_totals[ch]} shots (Original: {count - chapter_added_subbeats[ch]}, Added: +{chapter_added_subbeats[ch]})")

if __name__ == "__main__":
    main()
