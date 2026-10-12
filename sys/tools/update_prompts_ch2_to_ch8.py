#!/usr/bin/env python3
"""
Update all prompts in manifest_245_shots.json for Chapters 2 through 8 (shots 40 to 245)
to adhere strictly to the Chapter 1 formula:
- Bold black marker-pen outline
- Flat muted pastel and warm earthy fills
- Clean uncluttered off-white paper background, 16:9 widescreen
- Anonymous stick-figure character cast invariant
- Expressive, context-rich visual actions matching the Vietnamese narration subtitles
- Strictly no text, letters, watermarks, photorealistic faces, or 3D shading
"""
import json
from pathlib import Path

MANIFEST_PATH = Path("sys/exports/ancient_humans_bundle/manifest/manifest_245_shots.json")

PREFIX = (
    "2D hand-drawn explainer illustration in bold black marker-pen outline with flat muted pastel and "
    "warm earthy fills on a clean uncluttered off-white paper background, 16:9 widescreen. "
    "Cast invariant: anonymous stick-figure character with a large round solid-white head, thick 4px "
    "closed black outline, expressive simple dot/line eyes and eyebrows, thin stick limbs, and a single stick torso."
)

SUFFIX = (
    "Do NOT render any text, letters, words, watermarks, logos, photorealistic faces, or 3D shading."
)

def make_prompt(middle_action: str) -> str:
    middle_clean = middle_action.strip().rstrip(".")
    return f"{PREFIX} {middle_clean}. {SUFFIX}"

# Dictionary mapping shot_index (40..245) to (action_en, middle_visual_action)
SHOT_ACTIONS = {}

# ==========================================
# CHAPTER 2: Skeletons as historical diary (Shots 40..76)
# ==========================================
# SC05 (shots 40..45): Archaeological excavation in Middle East
SHOT_ACTIONS[40] = (
    "Archaeological dig site in Middle East, dirt trench showing layers of soil and buried history.",
    "Wide establishing shot of an arid archaeological dig site in the Middle East under warm pale morning sunlight; terracotta and sandy ochre soil layers in a wide excavated trench; a lone stick-figure archaeologist holding a small shovel observing the deep earth."
)
SHOT_ACTIONS[41] = (
    "Stick figure archaeologist kneeling by excavation pit with measuring tape and dust brush.",
    "Medium shot of a stick-figure archaeologist kneeling beside a neat rectangular excavation pit in dusty warm brown earth, using a soft bristle brush to gently sweep away sand, grid measuring lines sketched above."
)
SHOT_ACTIONS[42] = (
    "Archaeologist pointing into trench as colleagues approach with excavation tools.",
    "Medium shot of the archaeologist standing near the trench with hand gesturing downward into the soil, two stick-figure colleagues carrying wooden sieves and trowels in muted sage green clothing against off-white background."
)
SHOT_ACTIONS[43] = (
    "Two distinct burial pits discovered side-by-side in ancient stratified earth.",
    "Overhead top-down diagrammatic shot of two rectangular excavation graves dug into warm earthy brown ground; each trench containing the faint silhouette of a buried skeleton lying peacefully."
)
SHOT_ACTIONS[44] = (
    "Close-up of stratified soil layers showing thousands of years separating the two graves.",
    "Close-up cross-section diagram of archaeological soil strata: warm ochre topsoil, reddish terracotta middle layer, deep sandy beige bottom layer; hand-drawn horizontal marker lines showing millenniums of sediment."
)
SHOT_ACTIONS[45] = (
    "Two ancient human skeletons side-by-side, belonging to two completely different eras.",
    "Split view showing two human skeleton illustrations in clean black lines with soft bone-ivory fills resting in adjacent earth pits; a curious stick figure standing between them looking back and forth thoughtfully."
)

# SC06 (shots 46..58): Anatomical examination of Skeleton #1 vs Skeleton #2
SHOT_ACTIONS[46] = (
    "Inspection of Skeleton #1: tall, sturdy frame with thick dense limb bones.",
    "Scientific anatomical diagram of Skeleton #1 standing tall and proud: thick sturdy black bone contours filled with clean off-white ivory, broad shoulders, robust athletic frame highlighted with subtle pale olive green aura."
)
SHOT_ACTIONS[47] = (
    "Inspection of Skeleton #1's strong jaw and clean, healthy teeth.",
    "Close-up diagram of Skeleton #1's skull and jawline: strong mandibular arch, perfectly intact healthy teeth without any decay pits, smooth rounded enamel in clean white fills."
)
SHOT_ACTIONS[48] = (
    "Skeleton #1's smooth, intact joints with zero signs of repetitive strain wear.",
    "Close-up inspection of knee and elbow joints of Skeleton #1: clean gap lines, perfectly preserved bone articulation surfaces circled by a soft pastel teal indicator ring."
)
SHOT_ACTIONS[49] = (
    "Visualizing Skeleton #1 in life: healthy athletic hunter-gatherer moving freely in nature.",
    "Dynamic illustration of an athletic stick figure striding smoothly across open green savannah under golden sunlight, carrying a light walking stick, looking vibrant and energetic."
)
SHOT_ACTIONS[50] = (
    "Diverse natural diet: wild berries, lean game, leafy tubers nourishing the body.",
    "Still life illustration of healthy prehistoric foods in flat earthy colors: a handful of deep purple wild berries, roasted lean game meat on a flat stone, roasted root tubers in warm terracotta."
)
SHOT_ACTIONS[51] = (
    "Transition to Skeleton #2: hunched posture and damaged spine.",
    "Scientific anatomical diagram of Skeleton #2: noticeably shorter posture, severe curvature in the thoracic and lumbar spine, hunched shoulders outlined with cautionary muted dusty-red accent lines."
)
SHOT_ACTIONS[52] = (
    "Severe spinal degeneration in Skeleton #2 from thousands of repetitive bends.",
    "Close-up scientific diagram of compressed vertebrae in Skeleton #2's spine: pinched spinal discs, jagged bone spurs from repetitive bending indicated by small crimson stress arrows."
)
SHOT_ACTIONS[53] = (
    "Close-up of Skeleton #2's teeth: extensive decay, cavity holes from starch-heavy grain diet.",
    "Close-up diagram of Skeleton #2's dental arch: pitted enamel, dark charcoal cavity spots, worn flattened molars resulting from grinding gritty flour, accented with dull beige fills."
)
SHOT_ACTIONS[54] = (
    "Worn, arthritic knee and ankle joints showing years of grueling daily field labor.",
    "Close-up diagram of damaged knee joints in Skeleton #2: rough irregular bone spurs, friction erosion marks circled by a dull brick-red highlight."
)
SHOT_ACTIONS[55] = (
    "Visualizing Skeleton #2 in life: exhausted worker bent double under heavy physical load.",
    "Side profile illustration of a weary stick figure bent almost 90 degrees at the waist, carrying a heavy woven grain basket across dry cracked clay earth under a scorching pale yellow sun."
)
SHOT_ACTIONS[56] = (
    "Skeleton #2 died at a noticeably young age, body broken prematurely by relentless toil.",
    "Somber medium shot of Skeleton #2 lying curled in a shallow grave, soft muted dust-grey tones, an hourglass icon beside the grave with sand nearly depleted."
)
SHOT_ACTIONS[57] = (
    "Direct side-by-side comparison: robust tall Skeleton #1 vs broken hunched Skeleton #2.",
    "Split-screen comparison diagram: on the left Skeleton #1 standing tall and robust with a soft green checkmark; on the right Skeleton #2 hunched and degraded with a soft red warning mark."
)
SHOT_ACTIONS[58] = (
    "The two skeletons lying in earth, inviting the audience to solve the historical puzzle.",
    "Medium shot of the two skeleton pits viewed from above; a stick figure researcher scratching their head in deep contemplation, a floating question mark in warm ochre between the trenches."
)

# SC07 (shots 59..72): The guessing game & paradox
SHOT_ACTIONS[59] = (
    "Presenter posing the dramatic question: who is who?",
    "Medium shot of an expressive stick figure presenter pointing both arms outward toward the two archaeological pits, eyes wide with an engaging quizzical expression."
)
SHOT_ACTIONS[60] = (
    "Audience guessing: pointing instinctively to the tall, strong Skeleton #1.",
    "Group shot of modern stick figures in casual pastel shirts in a lecture setting, all confidently raising their hands and pointing toward Skeleton #1."
)
SHOT_ACTIONS[61] = (
    "Assuming Skeleton #1 must be the civilized farmer with food security and shelter.",
    "Conceptual illustration: above Skeleton #1 floats a daydream thought bubble containing a neat wooden house, a stone granary brimming with grain, and organized tools in calm pastel green."
)
SHOT_ACTIONS[62] = (
    "Visualizing the supposed benefits of civilization: granary storage, protection from nature.",
    "Detailed diagram of a cozy ancient agricultural homestead: thatched roof hut in warm straw yellow, orderly fences, sacks of harvested grain stacked high beside the door."
)
SHOT_ACTIONS[63] = (
    "Assuming Skeleton #2 must be the wretched, starving primitive hunter-gatherer.",
    "Conceptual illustration: above Skeleton #2 floats a daydream thought bubble of a shivering stick figure in cold rain, gnawing on a dry tree root in dull slate-blue tones."
)
SHOT_ACTIONS[64] = (
    "The common myth of hunter-gatherer life as short, brutish, and constantly on the brink of starvation.",
    "Dramatic illustration of a stick figure hunter fleeing from a shadowy wild beast in thorny dry bushes, portraying the popular myth of constant prehistoric peril."
)
SHOT_ACTIONS[65] = (
    "The persistent modern assumption that technological progress always improves physical health.",
    "Conceptual timeline infographic: a rising stair-step graph in pastel blue leading from a primitive stone hand-axe up to modern gear, showing the assumed upward trajectory of human well-being."
)
SHOT_ACTIONS[66] = (
    "Re-examining the physical evidence under the magnifying glass.",
    "Close-up shot of a large round magnifying glass held by a stick figure, focusing sharply on the dense healthy femur bone of Skeleton #1."
)
SHOT_ACTIONS[67] = (
    "Re-examining the decayed teeth and crushed spine of Skeleton #2.",
    "Close-up shot of the magnifying glass moving over Skeleton #2, revealing the crushed lumbar vertebrae and eroded molar teeth in sharp clarity."
)
SHOT_ACTIONS[68] = (
    "The contradiction between modern assumptions and physical bone reality.",
    "Infographic scale balance: on the left pan rests ideological assumptions ('Civilization = Health'); on the heavier right pan rests solid heavy bone fossils tipping the scale down."
)
SHOT_ACTIONS[69] = (
    "The presenter leaning forward to shatter the audience's preconceptions.",
    "Medium close-up of the stick figure presenter raising one index finger knowingly, expressive wide dot eyes with an eyebrow raised in intrigue."
)
SHOT_ACTIONS[70] = (
    "Preparing the big reveal: swapping the labels.",
    "Two blank parchment identification tags hanging above the two skeletons; a hand holding a black marker pen poised ready to write the unexpected truth."
)
SHOT_ACTIONS[71] = (
    "Tension building: the answer that defies common intuition.",
    "Dramatic wide shot: spotlight cone of warm pastel light illuminating the two skeletons in the darkened archaeological hall, creating a focused stage for the reveal."
)
SHOT_ACTIONS[72] = (
    "The reveal begins: preparing to reveal the identity of Skeleton #1.",
    "Close-up of Skeleton #1 with a large golden curtain pulling back to reveal an ancient savannah backdrop in warm amber and earthy ochre tones."
)

# SC08 (shots 73..76): The shocking reveal
SHOT_ACTIONS[73] = (
    "Reveal: Skeleton #1 was the free hunter-gatherer living 30,000 years ago.",
    "Bold infographic reveal: Skeleton #1 labeled with an earthy green laurel banner reading 'Hunter-Gatherer'; an athletic stick figure in simple loincloth standing proudly beside it with a hunting bow."
)
SHOT_ACTIONS[74] = (
    "Reveal: Skeleton #2 was the civilized farmer living in the agricultural era.",
    "Bold infographic reveal: Skeleton #2 labeled with a terracotta brown banner reading 'Early Farmer'; a weary stick figure hunched over a heavy stone hoe standing beside it."
)
SHOT_ACTIONS[75] = (
    "The paradox stated: farming broke the human body, hunting kept it thriving.",
    "Split conceptual comparison: on left, hunter-gatherer jogging effortlessly through flowering meadow in pastel greens; on right, early farmer collapsed in exhaustion over muddy furrow in dull grey-brown."
)
SHOT_ACTIONS[76] = (
    "Transition to exploring how prehistoric humans actually spent their days.",
    "Wide transition shot: the archaeological dig dissolves into a boundless sun-drenched prehistoric savannah with golden grasses, acacia trees, and wandering game in warm earthy tones."
)

# ==========================================
# CHAPTER 3: Life as a hunter-gatherer (Shots 77..104)
# ==========================================
# SC09 (shots 77..83): Waking up at sunrise naturally without alarms
SHOT_ACTIONS[77] = (
    "Savanna camp at early sunrise, peaceful dawn sky in lavender and apricot tones.",
    "Wide establishing shot of a prehistoric campsite on the African savanna at dawn; soft pastel lavender and apricot sky; silhouettes of acacia trees and a small cluster of grass dome shelters."
)
SHOT_ACTIONS[78] = (
    "Hunter-gatherer waking up gently without any alarm clock or loud noise.",
    "Medium shot inside a simple open grass shelter: a stick figure waking up slowly on a woven reed mat, rubbing eyes with a relaxed smile as gentle amber morning light washes across the floor."
)
SHOT_ACTIONS[79] = (
    "Body naturally well-rested after following the natural circadian rhythm.",
    "Stick figure standing up in front of the shelter, arms stretching high toward the morning sun in healthy posture, a soft yellow sunrise glow surrounding the character."
)
SHOT_ACTIONS[80] = (
    "Stepping out into the crisp morning savanna air, birds chirping in trees.",
    "Wide shot of the stick figure walking onto the open dewy grassland; gentle pastel green grass tufts; birds sketched in delicate black wings fluttering above in the pale sky."
)
SHOT_ACTIONS[81] = (
    "Tribe members rising at their own natural pace, greeting each other warmly.",
    "Medium shot of three stick figures meeting in the camp clearing, greeting each other with open hand gestures and smiles, completely free from rush or anxiety."
)
SHOT_ACTIONS[82] = (
    "Gentle smoke rising from the revived morning hearth stones.",
    "Close-up of glowing charcoal embers between three river rocks; a stick figure blowing gently to rekindle the fire with wisps of pale grey smoke curling into the air."
)
SHOT_ACTIONS[83] = (
    "Sitting peacefully by the fire, breathing in the morning without schedule.",
    "Two stick figures sitting cross-legged on warm earth beside the crackling small hearth, enjoying the warmth of the fire, looking out calmly across the open plains."
)

# SC10 (shots 84..90): Morning gathering, wild berries and nuts, democratic discussion
SHOT_ACTIONS[84] = (
    "Sharing morning food: wild berries and roasted mongongo nuts.",
    "Still life close-up of communal breakfast: flat woven reed basket filled with rich purple wild berries and cracked brown mongongo nuts beside roasted roots in terracotta clay."
)
SHOT_ACTIONS[85] = (
    "Eating leisurely while chatting about the day ahead.",
    "Medium shot of a small circle of five stick figures snacking from communal baskets, laughing and exchanging hand gestures in lively casual conversation."
)
SHOT_ACTIONS[86] = (
    "Equal democratic discussion: no boss, no chief ordering others around.",
    "Concept illustration of egalitarian community: stick figures seated in a perfect circle on flat ground under an acacia shade tree; no elevated throne, every figure on equal level."
)
SHOT_ACTIONS[87] = (
    "Discussing where ripe fruits have been spotted and where game tracks lead.",
    "A stick figure pointing outward across the savanna with two fingers, miming animal footprints in the dirt while others lean in listening attentively with nods."
)
SHOT_ACTIONS[88] = (
    "Deciding naturally as a group whether to forage or stay in camp today.",
    "Group scene where stick figures shrug casually and smile: some decide to go berry picking, others decide to relax and repair hunting bows, complete personal autonomy."
)
SHOT_ACTIONS[89] = (
    "Children playing freely around the elders without rigid school schedules.",
    "Two small stick children chasing a colorful hand-made rolling hoop toy across the camp ground in joyful motion, while elders watch fondly from the shade."
)
SHOT_ACTIONS[90] = (
    "A calm, harmonious morning devoid of commute, traffic, or deadlines.",
    "Wide peaceful shot of the entire campsite bathed in warm golden daylight; tranquil smoke curling upward; nature and human existence in perfect unhurried balance."
)

# SC11 (shots 91..97): Easy workflow finished by midday, relaxing in shade
SHOT_ACTIONS[91] = (
    "Departing for a short morning foraging walk in nearby scrubland.",
    "Wide shot of three stick figures walking leisurely through knee-high savanna grasses with light woven foraging bags, chatting under warm morning sun."
)
SHOT_ACTIONS[92] = (
    "Gathering abundant mongongo nuts and wild tubers effortlessly from rich soil.",
    "Medium shot of a stick figure using a simple pointed digging stick to unearth plump edible tubers from moist dark soil, placing them into a leather sling."
)
SHOT_ACTIONS[93] = (
    "Checking animal traps and gathering edible greens near riverbank.",
    "Stick figure by a winding pastel-blue creek checking a simple woven fish basket trap, lush green reeds and blooming water lilies along the bank."
)
SHOT_ACTIONS[94] = (
    "Returning to camp with full bags by early afternoon.",
    "Stick figures returning to camp with baskets overflowing with nuts and tubers; the sun reaches zenith overhead in a bright pale blue sky."
)
SHOT_ACTIONS[95] = (
    "All essential subsistence work for the entire day is already complete.",
    "Infographic clock dial showing morning hours from 8 AM to 11 AM highlighted in soft green ('Work Done'), leaving the entire remainder of the day completely open and free."
)
SHOT_ACTIONS[96] = (
    "Hanging strips of meat on wooden racks to dry in the gentle breeze.",
    "Medium shot of a wooden A-frame drying rack with thin strips of rich red meat curing in the clean air and sun, a stick figure adjusting a hanging string."
)
SHOT_ACTIONS[97] = (
    "Stretching out in the shade of a large baobab tree for an afternoon nap.",
    "Stick figure resting peacefully with head propped on a smooth log under the vast cooling canopy of an ancient baobab tree, dappled shadows on golden sand."
)

# SC12 (shots 98..104): Persistence hunting, endurance cooling
SHOT_ACTIONS[98] = (
    "The hunting expedition: tracking an antelope across the open plain.",
    "Wide shot of two stick-figure hunters kneeling in tall grass, examining fresh hoof prints in sandy soil, pointing toward an antelope grazing in the distance."
)
SHOT_ACTIONS[99] = (
    "Human superpower: endurance running under midday heat.",
    "Dynamic action shot of a stick figure hunter jogging with a steady, rhythmic stride across the sun-drenched savannah holding a light spear."
)
SHOT_ACTIONS[100] = (
    "Millions of sweat glands evaporating moisture to keep the human body cool.",
    "Scientific conceptual illustration: close-up of stick figure runner surrounded by tiny translucent cyan sweat droplets evaporating in the dry air, cooling arrow indicators."
)
SHOT_ACTIONS[101] = (
    "The animal prey cannot sweat, panting heavily as internal heat rises.",
    "Medium shot of an antelope stopping under the blazing sun, tongue hanging out, panting heavily, surrounded by wavy red heat distortion lines."
)
SHOT_ACTIONS[102] = (
    "The hunter maintains an unhurried, relentless jogging pace across hours.",
    "Side profile tracking shot of the hunter steadily jogging past landscape landmarks (termite mound, acacia tree, dry riverbed) with calm steady breathing."
)
SHOT_ACTIONS[103] = (
    "The prey collapses from heat exhaustion without a single violent clash.",
    "The antelope collapses gently onto the soft grass from thermal exhaustion; the human hunter walks up calmly and respectfully, resting the spear tip."
)
SHOT_ACTIONS[104] = (
    "Returning to camp with meat for the entire tribe, celebrated with smiles.",
    "The hunter arriving back at the campsite carrying the harvested game; tribe members stepping forward with welcoming arms and radiant smiles in the warm afternoon light."
)

# ==========================================
# CHAPTER 4: The 17-hour work week (Shots 105..124)
# ==========================================
# SC13 (shots 105..110): Richard Lee 1963 in Kalahari desert
SHOT_ACTIONS[105] = (
    "1963: Anthropologist Richard Lee arriving at the Kalahari desert border.",
    "Wide shot of the vast red sand dunes of the Kalahari desert under pale azure sky; a vintage off-road vehicle parked near sparse desert scrub; stick-figure researcher stepping out."
)
SHOT_ACTIONS[106] = (
    "Richard Lee equipped with clipboard, notebook, and mechanical stopwatch.",
    "Medium shot of the anthropologist stick figure wearing a classic sun safari hat, holding a mechanical ticking stopwatch in one hand and a clipboard notebook in the other."
)
SHOT_ACTIONS[107] = (
    "Encountering the Ju/'hoansi hunter-gatherer tribe in their desert haven.",
    "Medium wide shot of Richard Lee respectfully approaching a peaceful Ju/'hoansi settlement of curved grass huts under a giant camelthorn tree."
)
SHOT_ACTIONS[108] = (
    "Expecting to find extreme hardship, poverty, and relentless desperate struggle.",
    "Thought bubble above Lee's head showing a bleak imagined scene: starving stick figures desperately searching dry barren dust for scraps in gloomy grey tones."
)
SHOT_ACTIONS[109] = (
    "Reality shocks the researcher: villagers lounging, singing, and laughing.",
    "Contrast scene: Lee watching in astonishment as villagers sit comfortably in shade, chatting, laughing, playing string games, looking robust and untroubled."
)
SHOT_ACTIONS[110] = (
    "Lee decides to conduct strict scientific time-allocation measurements.",
    "Close-up of Lee opening his ledger notebook, drawing strict measurement columns: 'Hunting', 'Gathering', 'Tool Care', 'Leisure', pencil poised."
)

# SC14 (shots 111..116): Meticulous measurement of weekly work hours
SHOT_ACTIONS[111] = (
    "Shadowing villagers every day to record every single minute of labor.",
    "Medium shot of Lee walking unobtrusively behind a foraging stick figure, clicking his stopwatch and jotting down timestamps on his clipboard."
)
SHOT_ACTIONS[112] = (
    "Measuring foraging duration: only 2 to 3 days per week spent collecting food.",
    "Calendar infographic showing 7 day boxes: only 2.5 days have small gathering basket icons in pale green, while 4.5 days are completely blank open leisure."
)
SHOT_ACTIONS[113] = (
    "Measuring tool repair and household chores: negligible minutes per day.",
    "Close-up of a stick figure leisurely sharpening an arrow tip with a smooth stone, taking only a few minutes before putting it aside to chat."
)
SHOT_ACTIONS[114] = (
    "Summing the weekly total: an unbelievable 17 hours of labor per week.",
    "Bold typographic infographic: giant clean numeral '17' prominently displayed in deep warm terracotta, encircled by a laurel wreath with text 'HOURS PER WEEK'."
)
SHOT_ACTIONS[115] = (
    "Daily breakdown: only about 2.4 hours of work per day required to thrive.",
    "Clock diagram: 24-hour circle where only a tiny slice of 2.4 hours is colored soft green, leaving the vast majority of the day completely unburdened."
)
SHOT_ACTIONS[116] = (
    "Nutritional verification: calorie intake exceeded modern recommended standards.",
    "Diagrammatic scale comparing food intake: bowl of protein-rich nuts and game meat weighing down scale, revealing over 2,140 clean nutritious calories per person daily."
)

# SC15 (shots 117..124): Modern comparison & global replication
SHOT_ACTIONS[117] = (
    "Comparison with modern 40-hour work week: surpassing 17 hours by Wednesday.",
    "Modern office calendar infographic: Monday (8h) + Tuesday (8h) + Wednesday morning (2h) quickly exceeds 17 hours, leaving 2.5 grueling days still remaining."
)
SHOT_ACTIONS[118] = (
    "Exhausted modern office worker slumping over desk halfway through the week.",
    "Medium shot of a modern stick figure in necktie collapsed forward onto office keyboard, surrounded by glowing monitors, overflowing inboxes, and lukewarm coffee cup."
)
SHOT_ACTIONS[119] = (
    "Skeptics wondering if the Kalahari Ju/'hoansi were just an isolated fluke.",
    "Academic lecture hall: stick figure professors raising skeptical hands and questioning notes, wondering if other hunter-gatherers worked more."
)
SHOT_ACTIONS[120] = (
    "Global replication: studying the Hadza tribe in Tanzania.",
    "World map spotlight on Tanzania: Hadza hunter-gatherer stick figure with recurve bow near Lake Eyasi, logging identical 14 to 18 hours per week of food labor."
)
SHOT_ACTIONS[121] = (
    "Studying the Aché tribe in the dense subtropical forests of Paraguay.",
    "World map spotlight on South America: Aché hunter-gatherer stick figure moving through lush green rainforest canopy, logging identical 15 to 20 hours per week."
)
SHOT_ACTIONS[122] = (
    "Studying the Martu aboriginal foragers in the Australian Western Desert.",
    "World map spotlight on Australia: Martu stick figure foraging in red spinifex desert, confirming consistent 16 hours per week of subsistence effort."
)
SHOT_ACTIONS[123] = (
    "The verdict of human anthropology: the original affluent society.",
    "Infographic title banner 'THE ORIGINAL AFFLUENT SOCIETY' in warm terracotta lettering, uniting four diverse hunter-gatherer figures with smiling expressions."
)
SHOT_ACTIONS[124] = (
    "Posing the central question: what did humans do with all their free time?",
    "A curious stick figure leaning against an ancient boulder at sunset, looking into the warm glowing horizon, wondering where all those hours went."
)

# ==========================================
# CHAPTER 5: The value of social time (Shots 125..158)
# ==========================================
# SC16 (shots 125..132): Afternoon social leisure in camp
SHOT_ACTIONS[125] = (
    "Golden afternoon light settling across the peaceful encampment.",
    "Wide establishing shot of the tribal camp bathed in warm honey-gold afternoon light; long gentle tree shadows stretching across clean sand."
)
SHOT_ACTIONS[126] = (
    "The most important hours of the week: unstructured communal leisure.",
    "Medium shot of several stick figures relaxing together in a loose circle on animal hides, leaning back comfortably against woven packs."
)
SHOT_ACTIONS[127] = (
    "Social grooming: stick figures gently braiding and untangling hair.",
    "Close-up of one stick figure gently sitting behind another, combing and braiding hair with careful fingers, both smiling in mutual comfort."
)
SHOT_ACTIONS[128] = (
    "Playful teasing, jokes, and burst of shared community laughter.",
    "Two stick figures sharing a funny gesture; comic speech bubbles with small laughter spark symbols, faces lit up with wide happy grins."
)
SHOT_ACTIONS[129] = (
    "Stick figure elder crafting delicate beads from sea shells.",
    "Close-up of a stick figure sitting cross-legged, using a fine flint drill to carefully bore a neat hole through a small pale pink marine shell."
)
SHOT_ACTIONS[130] = (
    "Strung shell beads forming an intricate ornamental necklace.",
    "Close-up of hands threading polished shell beads onto a fine braided sinew cord, soft mother-of-pearl and ochre colors shimmering gently."
)
SHOT_ACTIONS[131] = (
    "Another artisan etching delicate geometric patterns onto ostrich eggshell.",
    "Hands using a sharp quartz flake to engrave fine cross-hatched chevron lines onto the creamy curved surface of a sturdy ostrich eggshell water flask."
)
SHOT_ACTIONS[132] = (
    "Creating purely for the joy of beauty and personal expression.",
    "Stick figure holding up the finished engraved shell to catch the sunlight, admiring the delicate artistic work with proud satisfaction."
)

# SC17 (shots 133..140): Blombos cave beads and Hohle Fels bone flute
SHOT_ACTIONS[133] = (
    "Archaeological evidence of deep antiquity: Blombos Cave in South Africa.",
    "Cross-section diagram of Blombos Cave overlooking the ocean; ancient cave mouth opening onto a pastel turquoise sea, layers of ochre sediment within."
)
SHOT_ACTIONS[134] = (
    "70,000-year-old pierced Nassarius sea shell beads unearthed from sand.",
    "Scientific artifact illustration: cluster of ancient pierced marine snail shells, perfectly drilled through the aperture, tinted with red ochre pigment."
)
SHOT_ACTIONS[135] = (
    "Transporting shells over hundreds of kilometers as tokens of affection and trade.",
    "Dotted trail line across a landscape map connecting the coastal sea to deep inland camps, showing ancient social exchange networks."
)
SHOT_ACTIONS[136] = (
    "Hohle Fels Cave in Germany: unearthing a 40,000-year-old musical instrument.",
    "Diagrammatic view of Hohle Fels Cave interior in muted slate tones; a spotlight highlighting a buried ivory and bone artifact in ancient clay."
)
SHOT_ACTIONS[137] = (
    "The vulture bone flute: meticulously carved with 5 tuned finger holes.",
    "Detailed scientific illustration of the 40,000-year-old flute carved from a griffon vulture wing bone; 5 precisely spaced circular finger holes clearly shown."
)
SHOT_ACTIONS[138] = (
    "Stick figure musician raising the bone flute to play ancient melodies.",
    "Medium shot of a stick figure holding the bone flute to lips, playing music with closed eyes; soft pastel musical note icons drifting gently into the air."
)
SHOT_ACTIONS[139] = (
    "Tribe members gathered around, listening in deep emotional enchantment.",
    "Circle of stick figures listening attentively in serene silence, heads tilted in peaceful appreciation of the haunting flute melodies."
)
SHOT_ACTIONS[140] = (
    "Music and art were not luxury afterthoughts—they were essential human core.",
    "Infographic showing human heart icon intertwined with flute and shell necklace, glowing in warm pastel peach tones on off-white paper."
)

# SC18 (shots 141..148): Art and beauty as foundational human pursuits
SHOT_ACTIONS[141] = (
    "Cave wall painting: blowing red ochre paint over hands to create stencils.",
    "Medium shot inside a rock shelter: stick figure pressing hand against rough stone wall, blowing red ochre powder through a reed pipe to leave hand stencils."
)
SHOT_ACTIONS[142] = (
    "The rock art gallery: running bison, horses, and gazelles in bold lines.",
    "Wide shot of rock art mural featuring expressive running animals in charcoal black and terracotta red lines, dynamic motion strokes."
)
SHOT_ACTIONS[143] = (
    "Art did not produce food or fuel, yet ancestors devoted countless hours to it.",
    "Concept illustration: scale balance with a basket of tubers on one side and a carved artwork on the other, balanced in equal dignified harmony."
)
SHOT_ACTIONS[144] = (
    "Artistic expression fostered deep shared identity and tribal cohesion.",
    "Group of stick figures standing together before the painted cave wall, hands raised in unity, feeling connected across generations."
)
SHOT_ACTIONS[145] = (
    "Decorating tools, hunting bows, and leather cloaks with intricate fringe.",
    "Close-up of utilitarian tools enhanced with beauty: a spear thrower carved with a leaping ibex motif, stitching on a soft leather wrap."
)
SHOT_ACTIONS[146] = (
    "Living not merely to survive, but to experience wonder and aesthetic joy.",
    "Stick figure standing on a scenic rocky bluff looking at a magnificent pastel sunset over rolling hills, arms wide open to the sky."
)
SHOT_ACTIONS[147] = (
    "Contrast with modern culture where artistic expression is squeezed out by work.",
    "Split view: ancient figure painting cave walls with radiant joy vs modern worker staring blankly at spreadsheet with dead eyes."
)
SHOT_ACTIONS[148] = (
    "The profound realization: free time was the birthplace of human soul.",
    "Stick figure sitting in peaceful contemplation beneath a starry dusk sky, a warm inner light glowing within the chest."
)

# SC19 (shots 149..158): Social bonding as health insurance, pension, and hospital
SHOT_ACTIONS[149] = (
    "The deeper evolutionary purpose of afternoon socializing.",
    "Infographic network diagram: lines connecting circle of stick figures, forming an unbroken web of mutual trust and affection in soft teal lines."
)
SHOT_ACTIONS[150] = (
    "In a world without banks, relationships were your savings account.",
    "Conceptual illustration: two stick figures warmly embracing, surrounded by a glowing shield of community protection against life's perils."
)
SHOT_ACTIONS[151] = (
    "In a world without hospitals, your tribe was your intensive care unit.",
    "Medium shot of an injured stick figure with wrapped leg resting comfortably inside a warm hut, two companions gently feeding them warm broth."
)
SHOT_ACTIONS[152] = (
    "In a world without pension funds, respect for elders guaranteed survival.",
    "An elderly stick figure with walking cane seated comfortably near the hearth, surrounded by attentive younger members bringing roasted food."
)
SHOT_ACTIONS[153] = (
    "Sharing food unconditionally: today you catch game, tomorrow others share with you.",
    "Hand-to-hand exchange illustration: one stick figure passing a roasted cut of meat to another with open palms, zero monetary transaction."
)
SHOT_ACTIONS[154] = (
    "Fossil evidence of healed femur fractures proving deep ancient care.",
    "Scientific diagram of an ancient human femur bone showing a fully healed fracture callus, proof that the tribe carried and cared for the injured for months."
)
SHOT_ACTIONS[155] = (
    "The emotional security of knowing you will never be abandoned alone.",
    "Stick figure sleeping peacefully under the shelter of the camp, surrounded by watchful campfires and vigilant caring companions."
)
SHOT_ACTIONS[156] = (
    "Social bonding time was not 'lazy wasted time'—it was survival itself.",
    "Infographic clock diagram: the 6 hours of afternoon socializing labeled with a sturdy anchor icon 'COMMUNITY RESILIENCE'."
)
SHOT_ACTIONS[157] = (
    "Modern loneliness contrasting sharply with prehistoric communal intimacy.",
    "Split panel: lone modern stick figure eating instant noodles alone in tiny apartment vs warm lively tribal circle eating together by fire."
)
SHOT_ACTIONS[158] = (
    "The afternoon sun slowly dips below the horizon, ushering in the magical night.",
    "Wide sunset view: the golden savannah sky transitions into rich warm orange and deep indigo, signaling the start of the evening fire."
)

# ==========================================
# CHAPTER 6: Nighttime and the birth of culture (Shots 159..188)
# ==========================================
# SC20 (shots 159..165): Polly Wiessner 2014 study: daytime vs nighttime talk
SHOT_ACTIONS[159] = (
    "Dusk descends across the savannah, bringing cool refreshing night breezes.",
    "Wide establishing shot of the savannah at twilight: deep indigo sky, warm orange glow on the horizon, cool breeze rustling tall dry grasses."
)
SHOT_ACTIONS[160] = (
    "The greatest hours of the prehistoric day are only just beginning.",
    "Camp center: stick figures walking toward the central hearth carrying dry fire logs, smiles of anticipation on their faces."
)
SHOT_ACTIONS[161] = (
    "Anthropologist Polly Wiessner's landmark 2014 research study.",
    "Illustration of researcher Polly Wiessner with audio recording equipment, studying decades of transcribed tribal conversations."
)
SHOT_ACTIONS[162] = (
    "Decades of recorded conversation tapes among the Ju/'hoansi bushmen.",
    "Close-up of vintage magnetic cassette audio tapes with handwritten labels 'Ju/'hoansi Day Talk' and 'Ju/'hoansi Night Fireside Conversations'."
)
SHOT_ACTIONS[163] = (
    "Sorting conversations into daytime practical talk versus nighttime talk.",
    "Infographic split comparison table: left column with sun icon 'Daytime Conversations' vs right column with crescent moon icon 'Firelight Conversations'."
)
SHOT_ACTIONS[164] = (
    "Daytime talk: 75% practical affairs—meat portions, hunting tracks, petty arguments.",
    "Daytime scene with speech bubbles filled with practical symbols: cuts of meat, animal tracks, complaining hand gestures, pragmatic daily logistics."
)
SHOT_ACTIONS[165] = (
    "The pragmatic necessity of daytime survival talk.",
    "Stick figures discussing animal tracks on the ground during bright midday sun, focused exclusively on food gathering and survival logistics."
)

# SC21 (shots 166..172): Campfire storytelling: myths, cosmology, legends
SHOT_ACTIONS[166] = (
    "Lighting the central campfire: crackling flames leaping into the dark.",
    "Close-up of glowing logs bursting into brilliant warm orange and golden yellow flames, sparks dancing upward into the crisp night air."
)
SHOT_ACTIONS[167] = (
    "At night around the fire, conversations transform completely.",
    "Circle of stick figures gathered closely around the roaring campfire, golden light dancing warmly across their white round heads."
)
SHOT_ACTIONS[168] = (
    "81% of night talk: myths, stories, folklore, and distant ancestral memories.",
    "Infographic pie chart of night conversation: 81% slice glowing in bright amber firelight labeled 'Stories, Myths, Cosmic Humor'."
)
SHOT_ACTIONS[169] = (
    "The master storyteller stick figure stands up with animated gestures.",
    "Medium shot of an elder stick figure standing beside the flames, arms raised high acting out a legendary tale, shadow dancing on the earth."
)
SHOT_ACTIONS[170] = (
    "Listeners lean forward in mesmerized wonder, eyes reflecting firelight.",
    "Close-up of three listener stick figures leaning forward with wide engaged dot eyes, captivated smiles in the warm yellow glow."
)
SHOT_ACTIONS[171] = (
    "Imagination cloud overhead: celestial animals and stars coming alive.",
    "A glowing pastel dream-cloud floating above the campfire, showing mythical constellations, spirit animals, and legendary ancestral journeys."
)
SHOT_ACTIONS[172] = (
    "Stories connecting disparate tribes across hundreds of miles through shared lore.",
    "Conceptual map of ancient landscape at night, multiple distant glowing campfires connected by shimmering golden threads of shared folklore."
)

# SC22 (shots 173..179): Firelight extending imagination and human culture
SHOT_ACTIONS[173] = (
    "Fire was more than heat or cooking—it extended the psychological day.",
    "Diagrammatic visual: the campfire creates a protective glowing bubble of light and warmth pushed outward against the vast predator-filled night."
)
SHOT_ACTIONS[174] = (
    "Inside the fire circle, fear of darkness was banished by laughter.",
    "Group laughter around the hearth: stick figures clapping hands, throwing dry twigs on the fire, warmth radiating through the small band."
)
SHOT_ACTIONS[175] = (
    "Shared storytelling expanded the human mind's capacity for empathy.",
    "Two stick figures sharing an emotional moment by the dying embers, a soft glowing heart icon between them representing shared understanding."
)
SHOT_ACTIONS[176] = (
    "Passing moral codes, ethical wisdom, and survival survival law to youth.",
    "Elder stick figure gently guiding a young stick child, pointing toward the fire and the night sky, transmitting ancient tribal wisdom."
)
SHOT_ACTIONS[177] = (
    "Singing ancient rhythmic chants accompanied by rhythmic clapping.",
    "The tribe singing together in unison around the fire, rhythmic clapping hands with soft musical sound pulses rippling out into the dark."
)
SHOT_ACTIONS[178] = (
    "The fire dies down into a bed of deep red glowing coals.",
    "Close-up of the hearth with logs settled into peaceful glowing red charcoal embers, gentle smoke drifting under the vast starry sky."
)
SHOT_ACTIONS[179] = (
    "Preparing for bed in deep emotional contentment and mental peace.",
    "Stick figures quietly walking to their grass shelters under the Milky Way, completely relaxed and emotionally fulfilled."
)

# SC23 (shots 180..188): Biphasic sleep: 4h sleep + midnight watch + 4h sleep
SHOT_ACTIONS[180] = (
    "How ancient humans actually slept before electric light.",
    "Night sky filled with countless twinkling stars and the soft milky glow of the galaxy arched above the quiet sleeping camp."
)
SHOT_ACTIONS[181] = (
    "Biphasic sleep: humans did not sleep eight continuous unbroken hours.",
    "Timeline infographic diagram: 'First Sleep (4h)' -> 'Midnight Watch (1-2h)' -> 'Second Sleep (4h)', illustrated with crescent moon phases."
)
SHOT_ACTIONS[182] = (
    "First sleep: four hours of deep physical restoration after dusk.",
    "Medium shot of a stick figure sleeping deeply and soundly under a warm animal pelt inside the shelter, chest rising and falling peacefully."
)
SHOT_ACTIONS[183] = (
    "Waking naturally around midnight in total stillness and serenity.",
    "The stick figure waking quietly around midnight, sitting up without grogginess or alarm, looking outside into the moonlit clearing."
)
SHOT_ACTIONS[184] = (
    "The midnight watch: an hour of quiet contemplation under the stars.",
    "Medium shot of the stick figure sitting quietly beside the warm embers, gazing up into the brilliant star-filled sky in serene solitude."
)
SHOT_ACTIONS[185] = (
    "Whispering quietly with neighbors, meditating, or tending the embers.",
    "Two figures meeting quietly in the night, whispering softly for a few minutes in mutual camaraderie, adding a small branch to the hearth."
)
SHOT_ACTIONS[186] = (
    "A tranquil hour of the mind, completely free from anxiety and stress.",
    "Close-up of the stick figure's face bathed in soft silver moonlight, eyes calm and peaceful, breathing in the cool night air."
)
SHOT_ACTIONS[187] = (
    "Returning to shelter for the second peaceful sleep until dawn.",
    "The figure crawling back under the warm pelt, curling up comfortably for the second round of deep restful sleep."
)
SHOT_ACTIONS[188] = (
    "Waking at dawn renewed, having lived in perfect harmony with natural cycles.",
    "Dawn breaks with soft pink and golden rays; the stick figure emerges fresh, clear-eyed, and energized for the new day."
)

# ==========================================
# CHAPTER 7: The trap of agriculture (Shots 189..224)
# ==========================================
# SC24 (shots 189..197): The ancient 300,000-year schedule vs the first wheat seed
SHOT_ACTIONS[189] = (
    "For 300,000 years, this was the universal schedule of the human species.",
    "Wide panoramic illustration of prehistoric hunter-gatherers thriving across generations: hunting, gathering, socializing, storytelling in unbroken rhythm."
)
SHOT_ACTIONS[190] = (
    "A life of abundant leisure, robust bodies, rich culture, and personal autonomy.",
    "Collage of positive hunter-gatherer moments: athletic runner, communal fire circle, bone flute musician, peaceful sleep under starlight."
)
SHOT_ACTIONS[191] = (
    "Then, roughly 10,000 years ago, everything changed forever.",
    "Dramatic visual turning point: a sudden sharp divide across the composition, shifting from boundless savannah into fenced farmland."
)
SHOT_ACTIONS[192] = (
    "In the Fertile Crescent of the Middle East, someone planted a seed.",
    "Wide shot of the Fertile Crescent river valley in lush olive greens and silt browns; Zagros mountains in background under bright dawn."
)
SHOT_ACTIONS[193] = (
    "A stick figure kneeling in freshly tilled earth, dropping golden wheat seeds.",
    "Close-up of a stick figure's hand gently dropping grains of wheat into a furrowed trench in damp brown soil, sun gleaming on the seeds."
)
SHOT_ACTIONS[194] = (
    "The birth of agriculture: domesticating wheat, barley, sheep, and goats.",
    "Agricultural landscape: small plot of young green wheat shoots sprouting in neat rows; penned sheep in a wooden hurdle enclosure."
)
SHOT_ACTIONS[195] = (
    "It seemed like a magnificent triumph over unpredictable wild nature.",
    "Thought bubble of early farmers: celebrating a massive pile of harvested golden wheat sheaves, smiling with supposed victory over famine."
)
SHOT_ACTIONS[196] = (
    "More total food produced per square mile than hunting could ever yield.",
    "Infographic comparison: a small patch of wheat field yielding a mountain of grain sacks versus an enormous forest yielding a single deer."
)
SHOT_ACTIONS[197] = (
    "The fateful bargain: trading leisure and health for calories and numbers.",
    "Conceptual illustration of an ancient scale: heavy sacks of grain tipping down, while the feather of freedom and free time flies away into the sky."
)

# SC25 (shots 198..206): The illusion of progress and population trap
SHOT_ACTIONS[198] = (
    "The agricultural promise: food security and an easier life for all.",
    "Illustration of a neat early Neolithic farming village with mud-brick homes, golden thatch roofs, and smiling farmers stacking grain."
)
SHOT_ACTIONS[199] = (
    "The reality: the insidious population explosion trap.",
    "Infographic line chart: human population curve shooting steeply upward like a red rocket, accompanied by crowded stick figures."
)
SHOT_ACTIONS[200] = (
    "More grain meant more babies, and more babies meant more mouths to feed.",
    "A stick figure mother holding three crying babies at once, looking overwhelmed beside an empty clay pot, flour dust on her hands."
)
SHOT_ACTIONS[201] = (
    "The farm could produce 10 times more food, but now had 12 times more people.",
    "Arithmetic visual: 10 grain sacks divided among 12 hungry stick figures; each person receives less than the original hunter-gatherer."
)
SHOT_ACTIONS[202] = (
    "Villages grew crowded, unsanitary, and vulnerable to devastating disease.",
    "Crowded muddy village alleyway with stick figures coughing, close proximity to animal dung and mud-brick pens, dull grey tones."
)
SHOT_ACTIONS[203] = (
    "Monoculture diet of grain caused severe malnutrition and tooth decay.",
    "Medical contrast: flat bowl of bland grey wheat porridge causing dental cavities and stunted growth, compared with vibrant wild hunter diet."
)
SHOT_ACTIONS[204] = (
    "Farming was an irreversible trap: you could never go back to hunting.",
    "Dramatic illustration: a heavy wooden gate slamming shut behind the farmers, locking them inside the agricultural fields forever."
)
SHOT_ACTIONS[205] = (
    "If the tribe stopped farming, half the population would instantly starve.",
    "A desperate farmer looking over the vast wheat field, realizing there are too many people to survive on wild game and berries alone."
)
SHOT_ACTIONS[206] = (
    "Wheat domesticated humans, not the other way around.",
    "Conceptual satire: a giant tall golden stalk of wheat holding a stick figure farmer on a leash, commanding them to hoe the ground."
)

# SC26 (shots 207..215): Backbreaking agricultural labor from dawn to dusk
SHOT_ACTIONS[207] = (
    "The explosion of daily workload: from 17 hours to 60+ hours a week.",
    "Infographic bar chart explosion: 17-hour green bar of hunter-gatherers suddenly dwarfed by a towering 60-hour red bar of peasant farmers."
)
SHOT_ACTIONS[208] = (
    "Dawn to dusk backbreaking toil: clearing heavy stones from rocky soil.",
    "Stick figure farmer straining with bulging muscles to lift a massive heavy boulder from the dirt field, sweat flying from the brow."
)
SHOT_ACTIONS[209] = (
    "Dragging heavy primitive wooden plows through thick resistant mud.",
    "Two stick figures harnessed together, dragging a heavy wooden scratch-plow through thick sticky clay under a burning pale yellow sun."
)
SHOT_ACTIONS[210] = (
    "Spine bent at a permanent 90-degree angle for hours on end.",
    "Side profile of a hunched farmer bent double over a short-handled hoe, red stress lines highlighting the crushed spinal vertebrae."
)
SHOT_ACTIONS[211] = (
    "Constant weeding: thorny thistles and weeds threatening the crop.",
    "Farmer on knees desperately pulling aggressive prickly weeds from between wheat rows, hands blistered and bleeding."
)
SHOT_ACTIONS[212] = (
    "Digging irrigation canals and carrying heavy water jars under scorching sun.",
    "Farmer carrying two heavy earthenware water jars balanced on a shoulder yoke, trudging through dusty irrigation ditches."
)
SHOT_ACTIONS[213] = (
    "Fending off locust swarms, rodents, and devastating crop blights.",
    "Despairing farmer waving stick helplessly as a swarm of locusts descends on the green wheat crop, ruined harvest."
)
SHOT_ACTIONS[214] = (
    "Grinding grain for hours on stone querns, ruining knees and wrists.",
    "Woman stick figure kneeling on hard stone floor, endlessly pushing a heavy hand-grindstone back and forth over grain, worn arthritic joints."
)
SHOT_ACTIONS[215] = (
    "Collapsing in exhaustion at dusk, with zero energy left for art or music.",
    "Exhausted farmer collapsing face-down onto rough straw bedding in dark mud hut, completely depleted, no campfire songs."
)

# SC27 (shots 216..224): Enclosure, granaries, guards, taxation, social hierarchy
SHOT_ACTIONS[216] = (
    "Granaries created surplus, and surplus created greed and theft.",
    "Tall fortified mud-brick granary tower filled with grain sacks; nervous guards watching from the parapet with sharp spears."
)
SHOT_ACTIONS[217] = (
    "Building high wooden stockade walls to keep neighbors out.",
    "Sharp wooden palisade fence enclosing the village; stick figure looking through fence gaps at armed raiders outside."
)
SHOT_ACTIONS[218] = (
    "The emergence of social hierarchy: rulers, priests, soldiers, and peasants.",
    "Social pyramid diagram: crowned king and fat tax collector at the top; armed soldiers in the middle; bent, weary peasant farmers crushed at bottom."
)
SHOT_ACTIONS[219] = (
    "The tax collector arrives to seize the farmer's hard-earned harvest.",
    "Stern official stick figure with clay tablet and stylus, pointing commandingly as soldiers confiscate half of the farmer's grain baskets."
)
SHOT_ACTIONS[220] = (
    "The peasant is left with just enough grain to survive until the next harvest.",
    "Depressed farmer family looking into an almost empty clay jar, holding back tears as the tax cart rumbles away in the distance."
)
SHOT_ACTIONS[221] = (
    "Personal autonomy vanishes: bells, rules, masters, and rigid schedules.",
    "Large bronze temple bell ringing loudly above the village, summoning farmers to report for forced labor at the palace."
)
SHOT_ACTIONS[222] = (
    "The invention of debt, mortgages, and economic servitude.",
    "Stick figure farmer bound by a rope leash labeled with a debt tally tablet, trudging behind a wealthy landowner."
)
SHOT_ACTIONS[223] = (
    "The trap closed tight: humans became prisoners of the agricultural machine.",
    "Metaphorical illustration: farmer inside a giant mechanical clockwork gear made of stone and wheat, turning endlessly without escape."
)
SHOT_ACTIONS[224] = (
    "The ancient skeletons in the Middle East tell this exact historical tragedy.",
    "Connecting back to Chapter 2: split image showing Skeleton #2's ruined spine beside the exhausted peasant farmer, the truth laid bare."
)

# ==========================================
# CHAPTER 8: Trading freedom for security (Shots 225..245)
# ==========================================
# SC28 (shots 225..231): The morning alarm clock is the final invoice
SHOT_ACTIONS[225] = (
    "The ringing alarm clock this morning was the direct consequence of that ancient trap.",
    "Close-up of a modern alarm clock ringing violently on a sleek nightstand, electric lightning bolts and harsh audio shockwaves."
)
SHOT_ACTIONS[226] = (
    "The alarm clock is the latest receipt in a 10,000-year unpaid transaction.",
    "The alarm clock dispensing an endless paper receipt tape that unrolls across the floor, covered with dates stretching from 8000 BC to 2026."
)
SHOT_ACTIONS[227] = (
    "For hundreds of thousands of years, humans worked only 15 to 20 hours a week.",
    "Infographic nostalgia: an ancient hunter-gatherer stick figure resting calmly under an acacia tree, watching a tranquil sunset."
)
SHOT_ACTIONS[228] = (
    "The skeletons in the soil proved that ancient humans were healthier and freer.",
    "Scientific balance scale: healthy Skeleton #1 holding a laurel wreath of wellness, towering over modern sedentary ailments."
)
SHOT_ACTIONS[229] = (
    "Afternoons were dedicated to friends, laughter, children, and music.",
    "Montage of human warmth: braiding hair, playing bone flute, laughing with children, carving shells under gentle dappled shade."
)
SHOT_ACTIONS[230] = (
    "Nights were dedicated to campfire stories, celestial myths, and biphasic rest.",
    "Golden campfire illuminating faces under the starry Milky Way, stories weaving peace and solidarity across the community."
)
SHOT_ACTIONS[231] = (
    "Then agriculture slammed the door shut, and each era accelerated the pace.",
    "Fast-forward timeline: Neolithic farm -> Medieval fiefdom -> Industrial smokestack factory -> Modern high-tech skyscraper office."
)

# SC29 (shots 232..238): Lifetime toll: 90,000 hours of work, illusory finish lines
SHOT_ACTIONS[232] = (
    "Modern humans will spend an staggering 90,000 hours of life at work.",
    "Dramatic infographic typography: giant bold numbers '90,000 HOURS' towering over a tiny modern stick figure carrying a briefcase."
)
SHOT_ACTIONS[233] = (
    "Walking inside a giant endless corporate hamster wheel.",
    "Modern stick figure in necktie running endlessly inside a giant metal hamster wheel, surrounded by fluorescent office lights."
)
SHOT_ACTIONS[234] = (
    "Chasing illusory financial milestones: savings targets, pensions, promotions.",
    "Stick figure running after a dangling carrot labeled 'Retirement at 65' suspended on a stick, perpetually out of reach."
)
SHOT_ACTIONS[235] = (
    "Sacrificing youth, vitality, and daylight to earn paper currency.",
    "Metaphorical trade: stick figure feeding vibrant colorful life hours into a shredder machine, which spits out dry green dollar bills."
)
SHOT_ACTIONS[236] = (
    "The constant chronic background anxiety of modern schedules.",
    "Stick figure sitting in a modern subway or cubicle, surrounded by floating stress storm clouds: calendars, unread emails, deadlines."
)
SHOT_ACTIONS[237] = (
    "Modern luxury, yet starved for the one thing our ancestors had in abundance: time.",
    "Split contrast: luxury modern gadgets (smartphone, sports car, smart TV) in cold grey room vs completely empty schedule of happy ancestor."
)
SHOT_ACTIONS[238] = (
    "Trading priceless freedom for fragile security.",
    "Stick figure sitting inside a gilded golden birdcage; the door is open, but the figure stares hypnotized at a glowing smartphone screen."
)

# SC30 (shots 239..245): Full circle ending: waking up with new wisdom
SHOT_ACTIONS[239] = (
    "Coming back to the bedroom where this journey began.",
    "Wide shot of the modern bedroom at dawn: the bed, the nightstand, the quiet morning light creeping through window blinds."
)
SHOT_ACTIONS[240] = (
    "The alarm clock sits on the table, no longer an all-powerful master.",
    "Medium shot of the digital alarm clock, now quiet; beside it rests a cup of warm tea emitting gentle curly steam."
)
SHOT_ACTIONS[241] = (
    "The stick figure sits on the edge of the bed, viewing the world with new eyes.",
    "Medium shot of the stick figure sitting upright on the bedside, head tilted thoughtfully, expressive eyes filled with deep newfound understanding."
)
SHOT_ACTIONS[242] = (
    "Remembering the hunter-gatherer spirit encoded inside our DNA.",
    "Superimposed reflection in the bedroom mirror: behind the modern stick figure stands the silhouette of the proud ancient hunter looking over open plains."
)
SHOT_ACTIONS[243] = (
    "Realizing that your time belongs to you, not just to employers or machines.",
    "Stick figure looking down at own two hands with a quiet, confident smile, reclaiming agency over personal life and moments."
)
SHOT_ACTIONS[244] = (
    "Opening the window curtains wide to welcome the morning sunshine.",
    "Stick figure pulling back the bedroom curtains, flooding the room with brilliant warm golden sunlight, trees and open sky visible outside."
)
SHOT_ACTIONS[245] = (
    "A final inspiring question: what will you choose to do with your hours today?",
    "Wide, uplifting final shot: stick figure standing by the open window bathed in golden morning light, looking toward a bright hopeful horizon, clean off-white sky."
)

def update_manifest():
    print(f"Loading manifest from {MANIFEST_PATH}...")
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    shots = data["shots"]
    updated_count = 0

    for s in shots:
        idx = s["shot_index"]
        ch = s.get("chapter_number", 1)
        if ch < 2 or ch > 8:
            continue

        if idx not in SHOT_ACTIONS:
            print(f"WARNING: No action defined for Shot #{idx} (Ch{ch})!")
            continue

        action_en, visual_middle = SHOT_ACTIONS[idx]
        full_ai_prompt = make_prompt(visual_middle)

        vd = s.get("visual_direction") or {}
        vd["action_description"] = action_en
        vd["ai_prompt"] = full_ai_prompt
        # Ensure negative prompt is clean
        vd["negative_prompt"] = (
            "photorealistic, 3D render, complex shading, anime, colorful gradients, text, "
            "watermark, bad anatomy, realistic humans, duplicate bodies"
        )
        s["visual_direction"] = vd
        updated_count += 1

    print(f"Updated {updated_count} shots in Chapters 2 through 8.")
    assert updated_count == 206, f"Expected 206 shots updated, got {updated_count}"

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved updated manifest to {MANIFEST_PATH}!")

if __name__ == "__main__":
    update_manifest()
