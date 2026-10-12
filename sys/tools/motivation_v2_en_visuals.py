"""English visual beat definitions (V2 Editorial Graphic Edition) for the 48 scenes of the 13-minute Motivation History explainer.

Key V2 Upgrades over V1 (`motivation_en_visuals.py`):
1. Eliminates AI metaphor cliches (no cartoon brain cutaways, no wooden abacus/pipe valve inside skulls, no iron anchors/chains, no sci-fi hourglass portals).
2. Replaces repetitive split-screen formulas with cinematic foreground/background depth, physical stick-figure acting, architectural scale, and clean editorial negative space.
3. Embeds explicit semantic camera motion (`zoom_out`, `zoom_in`, `punch_in`, `pan_right`, `pan_left`) per beat so Remotion camera movement follows narrative intent rather than a mechanical modulo-5 loop, with zero consecutive duplicate camera motions inside any scene.
"""

from __future__ import annotations

STYLE_PREFIX = (
    "Editorial 2D hand-drawn ink illustration, crisp black ink lines on warm cream off-white paper background, "
    "muted earthy ochre and slate pastel fills, generous negative space, 16:9 widescreen composition. "
    "Anonymous stick figure with large round white head, thick bold black outline, simple dot eyes, expressive line mouth, "
    "thin stick limbs, single torso. Expressive physical posture and sightlines, zero brain cutaways, "
    "no realistic faces, no text, no letters, no numbers, no watermarks, uncluttered."
)

# Each entry in EN_SCENE_BEATS_V2[scene_id] is a 3-tuple:
#   (framing_label, english_visual_description, semantic_camera_effect)
EN_SCENE_BEATS_V2: dict[str, list[tuple[str, str, str]]] = {
    # ==================== CHAPTER 1: THE MONDAY MORNING PARADOX ====================
    "SC01": [
        (
            "Wide establishing office morning",
            "Clean editorial widescreen view of a sunlit modern apartment desk at morning, an open laptop casting a pale rectangle across a blank page while a lone stick figure sits motionless with hands resting flat on the wooden surface",
            "zoom_out",
        ),
        (
            "Close-up blinking cursor",
            "Intimate close-up of a stark white document screen with a single vertical black cursor bar standing alone in vast negative space beside a lukewarm ceramic coffee mug",
            "zoom_in",
        ),
        (
            "Medium distraction reach",
            "Side-angle medium shot of the stick figure's hand drifting away from the keyboard toward a smartphone lying face-up at the edge of the desk, posture slightly slumped",
            "pan_right",
        ),
        (
            "Over-the-shoulder endless scroll",
            "Over-the-shoulder editorial frame showing the stick figure's thumb flicking past small minimalist rectangular cards on the phone screen while the laptop monitor behind stays completely blank",
            "zoom_in",
        ),
        (
            "Low-angle afternoon shadows",
            "Low-angle view of the desk as long late-afternoon window shadows stretch across the floor, three empty coffee cups lined up beside the untouched keyboard",
            "pan_left",
        ),
        (
            "Wide quiet guilt payoff",
            "Wide high-contrast frame with generous cream negative space: the stick figure leaning back in the swivel chair, resting chin on hand, staring quietly at the unfinished work as dusk settles outside",
            "zoom_out",
        ),
    ],
    "SC02": [
        (
            "Wide self-reproach mirror",
            "Minimalist hallway composition where a stick figure stands before a tall rectangular wall mirror, shoulders drooping under an invisible weight while a neat to-do checklist hangs untouched on the wall",
            "zoom_out",
        ),
        (
            "Close-up checklist boxes",
            "Crisp close-up of a paper notepad with five empty square checkboxes and a fountain pen resting diagonally across the blank lines, zero ink marks made",
            "zoom_in",
        ),
        (
            "Medium bookshelf of remedies",
            "Medium shot of the stick figure standing before a wooden shelf stacked with brightly colored productivity planners, sand timers, and habit journals that remain unopened",
            "pan_right",
        ),
        (
            "Dramatic paradigm shift frame",
            "Bold editorial frame where a clean red ink brushstroke sweeps across a dark tangled scribble cloud above the desk, revealing a calm upright silhouette of the stick figure beneath",
            "punch_in",
        ),
        (
            "Medium open window perspective",
            "Medium shot of the stick figure stepping away from the cluttered desk toward a tall open window overlooking a wide horizon of ancient hills and modern city rooftops",
            "pan_left",
        ),
        (
            "Wide liberating realization",
            "Wide balanced composition with the stick figure looking directly toward the camera with a calm, curious posture as the cluttered office walls fade into clean warm parchment space",
            "zoom_out",
        ),
    ],
    "SC03": [
        (
            "Wide nineteenth-century archive room",
            "Tall sunlit library hall lined with wooden archival shelves and leather-bound lexicons, a stick-figure historian standing at a reading lectern examining a nineteenth-century manuscript",
            "zoom_out",
        ),
        (
            "Close-up historical timeline bar",
            "Clean editorial timeline etched in black ink across warm cream paper: three centuries of quiet agrarian life followed by a sharp vertical spike rising after the year 1880",
            "pan_right",
        ),
        (
            "Medium linguistic comparison",
            "Medium shot of the stick-figure historian holding open two large folio pages: the older page showing simple tools like a plow and hearth, the newer industrial page stamped with factory schedules",
            "zoom_in",
        ),
        (
            "Sudden industrial book stacks",
            "Sharp perspective shot of tall stacks of twentieth-century management manuals and corporate motivational handbooks rising like skyscrapers on a library table",
            "punch_in",
        ),
        (
            "Close-up magnifying glass on text",
            "Close-up of a brass magnifying glass hovering over crisp printed lines in an archival dictionary, highlighting how recently the modern workplace term entered human speech",
            "zoom_in",
        ),
        (
            "Wide historical mystery payoff",
            "Wide atmospheric shot of the stick-figure historian looking down the long library corridor toward a sunlit courtyard where ancient artisans and farmers once worked without self-help books",
            "zoom_out",
        ),
    ],
    "SC04": [
        (
            "Wide monumental heritage panorama",
            "Sweeping widescreen vista uniting an Egyptian limestone pyramid on the left horizon, a Gothic stone cathedral spire in the center, and terraced rice fields on the right under a clear sky",
            "pan_right",
        ),
        (
            "Medium medieval master mason",
            "Medium shot of a stick-figure stonemason on timber scaffolding calmly carving a stone arch with mallet and chisel, surrounded by open air and birds rather than clocks or posters",
            "zoom_in",
        ),
        (
            "Medium ocean navigator",
            "Dynamic medium shot of stick-figure sailors on the wooden deck of an ancient sailing vessel trimming canvas sails together while reading the stars and wind on the open sea",
            "pan_left",
        ),
        (
            "Close-up artisan hands on wood",
            "Intimate close-up of a stick figure's hands guiding a wooden plane across an oak beam, crisp wood shavings curling upward in warm morning light",
            "zoom_in",
        ),
        (
            "Sharp contrast modern desk",
            "Sudden dramatic cut to a lone modern stick figure sitting under harsh fluorescent light in front of a glowing spreadsheet with shoulders tense and eyes wide",
            "punch_in",
        ),
        (
            "Wide historical question frame",
            "Wide editorial composition with a stick-figure narrator standing between an ancient stone archway and a modern glass office desk, inviting the viewer to compare the two worlds",
            "zoom_out",
        ),
    ],
    "SC05": [
        (
            "Wide environmental mismatch stage",
            "Clean architectural cross-section showing an ancient stick-figure hunter holding a wooden spear standing bewildered inside a sterile glass-and-steel corporate cubicle corridor",
            "zoom_out",
        ),
        (
            "Close-up wildlife metaphor",
            "Editorial illustration of a sleek ocean dolphin resting inside a dry, neatly tiled office room—visually clear, calm, and poignant without any cartoon text labels",
            "zoom_in",
        ),
        (
            "Medium ancestor at modern desk",
            "Medium shot of the prehistoric stick figure sitting awkwardly on an ergonomic swivel chair, poking cautiously at a wireless mouse as if searching for real tracks on the desk pad",
            "pan_right",
        ),
        (
            "Close-up eyes seeking horizon",
            "Close-up of a modern stick figure's round white head by an office window: in the glass reflection, wide sunlit savanna grass ripples where the cubicle walls should be",
            "zoom_in",
        ),
        (
            "Sudden alarm notification jolt",
            "Sharp framing of a red calendar popup appearing on the monitor screen, startling the stick figure whose posture tenses like a hunter hearing a snap in the brush",
            "punch_in",
        ),
        (
            "Wide compassionate insight",
            "Wide warm frame where the modern stick figure stands up from the desk and looks at their own hands with quiet understanding rather than frustration",
            "zoom_out",
        ),
    ],
    "SC06": [
        (
            "Wide four-epoch horizon",
            "Panoramic editorial frieze across warm cream paper depicting four distinct eras connected by a single stone footpath: savanna campfire, river-valley wheat field, village forge, and modern city skyline",
            "pan_right",
        ),
        (
            "Medium hunter on the trail",
            "Medium tracking shot of a stick-figure hunter striding briskly across open grassland with a woven basket and wooden spear under a golden morning sun",
            "pan_right",
        ),
        (
            "Medium ancient harvest builder",
            "Medium shot of ancient stick-figure villagers stacking golden wheat sheaves beside a mud-brick granary and limestone monument by a flowing river",
            "zoom_in",
        ),
        (
            "Medium medieval craft workshop",
            "Medium shot of a medieval stick-figure blacksmith and carpenter working side by side under an open timber roof, exchanging finished tools with village neighbors",
            "pan_left",
        ),
        (
            "Dramatic modern cubicle contrast",
            "Tight framing of a modern stick figure illuminated by a laptop screen in a quiet high-rise room, looking back toward the warm sunlit footpath of history",
            "punch_in",
        ),
        (
            "Wide chapter transition payoff",
            "Wide inviting view of the stick-figure narrator stepping onto the first stone marker of the historical trail as the horizon opens into deep evolutionary time",
            "zoom_out",
        ),
    ],

    # ==================== CHAPTER 2: THE DOPAMINE COMPASS ====================
    "SC07": [
        (
            "Wide evolutionary timeline strip",
            "Minimalist horizontal proportion bar stretching across the entire frame: a long warm ochre band spanning ninety-nine percent of the width, ending in a razor-thin blue sliver on the far right edge",
            "pan_right",
        ),
        (
            "Close-up magnifying the modern sliver",
            "Extreme close-up of a magnifying lens hovering over the tiny final millimeter of the timeline bar where miniature factories, steam trains, and laptops are crowded together",
            "zoom_in",
        ),
        (
            "Medium prehistoric camp life",
            "Medium shot of a small band of stick-figure foragers walking lightly across an open plateau under vast clouds, representing the long evolutionary baseline of humanity",
            "zoom_out",
        ),
        (
            "Medium unchanging human silhouette",
            "Clean editorial silhouette of a stick figure walking forward while the background scenery shifts rapidly from acacia trees to stone temples to glass skyscrapers",
            "pan_right",
        ),
        (
            "Sharp biological reality check",
            "Bold close-up of a modern stick figure wearing a dress shirt and tie, rolling up a sleeve to reveal the exact same simple stick-figure hand that once gripped a flint spear",
            "punch_in",
        ),
        (
            "Wide evolutionary perspective payoff",
            "Wide serene composition placing the tiny modern office desk at the edge of an immense prehistoric landscape to show the true scale of human time",
            "zoom_out",
        ),
    ],
    "SC08": [
        (
            "Wide popular myth gallery",
            "Editorial gallery room where a giant glossy neon sign shaped like a candy bar and a lounge chair sits on a pedestal, while a stick-figure neuroscientist shakes their head calmly",
            "zoom_out",
        ),
        (
            "Medium sweeping away the myth",
            "Medium shot of the stick-figure scientist pushing aside the decorative candy-and-couch display to reveal a rugged wooden compass and a pair of running sandals on the table",
            "pan_left",
        ),
        (
            "Close-up directional compass needle",
            "Crisp close-up of a brass compass resting on an open field map, its needle swinging decisively toward a distant fruit grove and glowing with warm amber ink lines",
            "zoom_in",
        ),
        (
            "Dynamic pursuit stride",
            "Low-angle action shot of a stick figure leaning forward in a brisk, purposeful stride up a hillside trail, eyes locked on a ripe berry bush ahead",
            "pan_right",
        ),
        (
            "Dramatic moment of action ignition",
            "Sharp close-up of the stick figure's foot pushing off the ground with energetic amber motion lines radiating from the stride—capturing drive as movement rather than passive sitting",
            "punch_in",
        ),
        (
            "Wide pursuit over pleasure payoff",
            "Wide composition showing the stick figure climbing the sunlit ridge with alert posture, guided by the warm directional compass line toward the horizon",
            "zoom_out",
        ),
    ],
    "SC09": [
        (
            "Wide savanna sightline",
            "Expansive widescreen view of an open savanna where a stick-figure forager stands on a low rock outcrop looking directly across a clear sightline toward a fruit-laden baobab tree",
            "zoom_out",
        ),
        (
            "Close-up visual target lock",
            "Close-up of the stick figure's eyes widening with focus as a clean golden dotted sightline connects their gaze directly to a cluster of ripe orange figs on the branch",
            "zoom_in",
        ),
        (
            "Medium brisk approach",
            "Medium tracking shot of the stick figure walking briskly along the golden sightline, reaching up with both hands to pluck the real fruit from the branch",
            "pan_right",
        ),
        (
            "Medium contrast abstract goal",
            "Contrasting medium shot in a modern room where a stick figure looks through a telescope into thick gray fog toward a distant, barely visible paper flag on the horizon",
            "pan_left",
        ),
        (
            "Close-up fading signal in fog",
            "Close-up of the brass compass needle spinning aimlessly without a target when pointed into the blank gray fog of an abstract quarterly chart",
            "punch_in",
        ),
        (
            "Wide tangible sightline payoff",
            "Wide clear editorial frame showing the compass needle locking firmly back in place the moment a concrete, visible object is placed within arm's reach",
            "zoom_out",
        ),
    ],
    "SC10": [
        (
            "Wide wilderness energy balance",
            "Wide sunlit canyon where a stick-figure hunter stands at the base of two paths: a gentle footpath leading to a nearby stream with fish, and a steep rocky cliff disappearing into barren clouds",
            "zoom_out",
        ),
        (
            "Medium weighing effort and return",
            "Medium shot of a rustic wooden balance scale on a flat stone: one pan holds a heavy stack of firewood representing bodily effort, the other holds a basket of fresh tubers",
            "zoom_in",
        ),
        (
            "Close-up meager return rejection",
            "Close-up of the wooden scale tipping sharply downward when a single tiny dry seed is placed against a massive boulder of exhausting effort",
            "punch_in",
        ),
        (
            "Medium wise conservation rest",
            "Medium shot of the prehistoric stick figure sitting calmly in the shade of an acacia tree to conserve strength when the trail ahead offers no clear food or water",
            "pan_left",
        ),
        (
            "Medium modern paper mountain",
            "Medium shot of a modern stick figure sitting before a towering stack of blank binders whose reward is an invisible digital icon far away",
            "pan_right",
        ),
        (
            "Wide biological wisdom payoff",
            "Wide calm frame showing the stick figure resting beside the wooden scale—illustrating that pausing before a vague, unrewarding task is an ancient survival safeguard",
            "zoom_out",
        ),
    ],
    "SC11": [
        (
            "Wide misty crossroads",
            "Atmospheric wide shot of a stick figure holding a warm lantern at dusk before two trails: a clear stone path leading to a glowing hearth on the left, and a murky endless corridor on the right",
            "zoom_out",
        ),
        (
            "Medium stepping into the murky corridor",
            "Medium shot of the stick figure taking a hesitant step toward a desk piled with vague, unlabelled folders while the lantern flame dims to a tiny flicker",
            "zoom_in",
        ),
        (
            "Close-up protective lantern dimming",
            "Close-up of the brass lantern's oil regulator smoothly lowering the flame to save fuel when no landmark is visible ahead—a clean mechanical metaphor on the desk",
            "punch_in",
        ),
        (
            "Medium physical heaviness on couch",
            "Medium shot of the stick figure sitting heavily on a sofa with arms resting on knees, not out of moral failure, but because the body is in fuel-conservation mode",
            "pan_left",
        ),
        (
            "Close-up flame reigniting with clarity",
            "Close-up of the lantern flame rising bright and warm the instant a small, clear sketch of a finished chair is placed right beside it on the table",
            "zoom_in",
        ),
        (
            "Wide reassuring perspective",
            "Wide balanced frame of the stick figure standing up with the relit lantern, understanding how clarity of outcome governs human energy",
            "zoom_out",
        ),
    ],
    "SC12": [
        (
            "Wide open landscape transition",
            "Wide cinematic view where the walls of a modern study fold back like clean paper screens to reveal a sunlit East African savanna stretching to the horizon",
            "zoom_out",
        ),
        (
            "Medium narrator walking into history",
            "Medium tracking shot of the stick-figure narrator walking past a weathered prehistoric standing stone carved with a handprint motif into tall golden grass",
            "pan_right",
        ),
        (
            "Close-up footprints in warm earth",
            "Close-up of bare stick-figure footprints pressed into soft riverbank clay beside fresh antelope tracks and fallen wild figs",
            "zoom_in",
        ),
        (
            "Wide morning camp awakening",
            "Wide shot of a small circular camp beneath umbrella thorn trees as thin blue woodsmoke rises into the clear morning sky",
            "pan_left",
        ),
        (
            "Medium welcoming prehistoric band",
            "Medium shot of three prehistoric stick figures looking up from tending their morning fire with relaxed, welcoming postures and zero haste",
            "zoom_in",
        ),
        (
            "Wide prehistoric horizon payoff",
            "Grand widescreen establishing frame of the open savanna under morning light, ready to explore how humanity lived and worked for three hundred millennia",
            "zoom_out",
        ),
    ],

    # ==================== CHAPTER 3: THE IMMEDIATE-RETURN SAVANNA ====================
    "SC13": [
        (
            "Wide savanna sunrise camp",
            "Golden morning sun rising over an open savanna camp with acacia trees as a small band of stick-figure hunter-gatherers wake naturally without alarm clocks",
            "zoom_out",
        ),
        (
            "Medium calm morning preparation",
            "Medium shot of stick figures stretching beside warm campfire embers and picking up woven reed baskets and wooden digging sticks with relaxed posture",
            "zoom_in",
        ),
        (
            "Medium morning foraging walk",
            "Tracking medium shot of three stick-figure foragers walking side by side along a sunlit stream bank, plucking ripe wild figs directly into their baskets",
            "pan_right",
        ),
        (
            "Close-up hands gathering fruit",
            "Close-up of a stick figure's hands placing fresh figs and tubers into a woven basket, every physical movement producing a visible, fragrant result within minutes",
            "zoom_in",
        ),
        (
            "Medium midday camp sharing",
            "Medium shot under the noon shade of a large tree where the same stick figures sit together eating and sharing the morning harvest around the camp",
            "pan_left",
        ),
        (
            "Wide immediate-return harmony",
            "Wide peaceful view of the small band living in a complete single-day loop of effort and nourishment under the open sky",
            "zoom_out",
        ),
    ],
    "SC14": [
        (
            "Wide riverbank morning search",
            "Wide shot of a prehistoric stick figure standing alertly by a winding stream, scanning the muddy bank and nearby trees in the crisp morning air",
            "zoom_out",
        ),
        (
            "Close-up fresh tracks in mud",
            "Close-up of the stick figure kneeling to touch clear hoofprints pressed into damp earth beside a bush heavy with ripe berries",
            "zoom_in",
        ),
        (
            "Medium purposeful harvesting",
            "Medium shot of the stick figure reaching into a hollow tree trunk to collect golden wild honeycomb and digging up crisp roots with a pointed stick",
            "pan_right",
        ),
        (
            "Close-up overflowing woven basket",
            "Close-up of the woven basket now brimming with golden honeycomb, figs, and tubers—an immediate, unmistakable physical reward held in both hands",
            "punch_in",
        ),
        (
            "Medium cheerful return stride",
            "Medium tracking shot of the stick figure walking back toward camp with the full basket slung over one shoulder and a light, energetic step",
            "pan_left",
        ),
        (
            "Wide midday satisfaction payoff",
            "Wide sunlit frame of the stick figure arriving back at the camp circle before noon with food for the whole group",
            "zoom_out",
        ),
    ],
    "SC15": [
        (
            "Wide anthropological field study",
            "Wide view of a stick-figure anthropologist sitting quietly on a camp stool with a field notebook, observing a peaceful hunter-gatherer camp in a sunlit clearing",
            "zoom_out",
        ),
        (
            "Close-up field notebook tally",
            "Close-up of the anthropologist's open paper notebook showing seven simple hand-drawn sun symbols for the week, with only two and a half suns shaded for foraging hours",
            "zoom_in",
        ),
        (
            "Medium afternoon shade leisure",
            "Medium shot of stick-figure hunter-gatherers relaxing in the cool shade of a baobab tree during the afternoon, chatting, playing string games, and resting",
            "pan_right",
        ),
        (
            "Medium unhurried craftwork",
            "Medium shot of a stick figure calmly smoothing a wooden bow stave and stringing shell beads while children play nearby without any rush or fatigue",
            "pan_left",
        ),
        (
            "Close-up serene rested expression",
            "Close-up of a prehistoric stick figure leaning back against a tree trunk with bright, rested eyes and relaxed shoulders in the warm afternoon breeze",
            "zoom_in",
        ),
        (
            "Wide abundant leisure payoff",
            "Wide harmonious view of the camp enjoying long hours of rest, conversation, and recovery under the golden savanna canopy",
            "zoom_out",
        ),
    ],
    "SC16": [
        (
            "Wide savanna tracking trail",
            "Wide shot of two stick-figure hunters crouching together on a grassy trail, pointing at subtle marks in the dust like keen detectives solving an outdoor puzzle",
            "zoom_out",
        ),
        (
            "Close-up reading the wind and grass",
            "Close-up of a stick figure examining a bent blade of grass and testing the wind direction with an uplifted finger, eyes alert with curiosity",
            "zoom_in",
        ),
        (
            "Medium cooperative hand signals",
            "Medium shot of three stick figures exchanging silent, agile hand signals across the tall grass, moving with the fluid coordination of a team sport",
            "pan_right",
        ),
        (
            "Close-up handcrafted bow precision",
            "Close-up of a stick figure drawing a handcrafted wooden bow with calm, practiced mastery—every muscle engaged in a challenging, absorbing skill",
            "punch_in",
        ),
        (
            "Medium joyful celebration",
            "Medium shot of the stick-figure hunters clasping forearms and smiling broadly together after a successful track in the open meadow",
            "pan_left",
        ),
        (
            "Wide play-and-work unity payoff",
            "Wide energetic shot of the hunters carrying their harvest back across the sunlit plain as if returning from a triumphant game",
            "zoom_out",
        ),
    ],
    "SC17": [
        (
            "Wide evening campfire circle",
            "Warm golden campfire blazing at the center of the prehistoric camp under a deep indigo night sky filled with stars, stick figures gathered in a close circle",
            "zoom_out",
        ),
        (
            "Medium sharing roasted harvest",
            "Medium shot of a stick-figure hunter handing portions of skewered roasted meat and wild figs directly to an elder and a child beside the crackling flames",
            "zoom_in",
        ),
        (
            "Close-up grateful eye contact",
            "Intimate close-up of two stick figures looking directly into each other's eyes across the warm orange firelight as food is shared, nodding with genuine gratitude",
            "zoom_in",
        ),
        (
            "Medium lively firelight storytelling",
            "Medium shot of a stick figure standing beside the fire using expressive hand gestures to recount the day's tracking adventure while the whole band listens attentively",
            "pan_right",
        ),
        (
            "Close-up shared laughter around embers",
            "Close-up of three stick figures around the fire smiling warmly together, the golden glow of the hearth reflecting on their round white heads",
            "pan_left",
        ),
        (
            "Wide communal belonging payoff",
            "Wide tranquil night view of the glowing campfire circle surrounded by the quiet savanna—a complete picture of human belonging and immediate meaning",
            "zoom_out",
        ),
    ],
    "SC18": [
        (
            "Wide three-stone camp emblem",
            "Wide editorial view of three flat river stones arranged beside a warm campfire, painted in simple ochre ink with a ripe fig, a wooden bow, and two joined hands",
            "zoom_out",
        ),
        (
            "Medium morning autonomy stride",
            "Medium shot of a prehistoric stick figure stepping out into the morning meadow at their own natural pace, free of schedules or bells",
            "pan_right",
        ),
        (
            "Medium visible midday harvest",
            "Medium shot of two stick-figure foragers lifting a full basket of wild fruit and roasted fish that their own hands gathered that very morning",
            "zoom_in",
        ),
        (
            "Medium evening fire fellowship",
            "Medium shot of the camp band sitting shoulder to shoulder around the evening hearth, sharing the meal and warm conversation under the stars",
            "pan_left",
        ),
        (
            "Close-up calm fulfilled ancestor",
            "Close-up of the prehistoric stick figure looking out over the firelit camp with clear, peaceful eyes—needing zero motivational speeches to love being alive",
            "zoom_in",
        ),
        (
            "Wide savanna chapter closing",
            "Wide panoramic pull-back of the glowing campfire under the starry sky before the horizon shifts toward the first river valleys of agriculture",
            "zoom_out",
        ),
    ],

    # ==================== CHAPTER 4: THE AGRICULTURAL RUPTURE ====================
    "SC19": [
        (
            "Wide Fertile Crescent fields",
            "Sweeping widescreen view of an ancient river valley with mud-brick huts, straight irrigation trenches, and stick-figure farmers bending over long plowed furrows",
            "zoom_out",
        ),
        (
            "Medium sowing dry seeds",
            "Medium shot of a stick-figure farmer walking slowly under a hot sun, dropping tiny grain seeds into dry brown earth from a woven pouch",
            "pan_right",
        ),
        (
            "Close-up empty dirt-stained hands",
            "Close-up of the farmer's tired hands at sunset covered in dry dust, looking down at a bare dirt furrow that offers zero food to eat tonight",
            "zoom_in",
        ),
        (
            "Wide six-moon horizon arc",
            "Editorial night composition where the stick-figure farmer stands beside the bare field looking up at six crescent moon phases arcing across the sky before harvest season",
            "zoom_out",
        ),
        (
            "Close-up longing for immediate fruit",
            "Close-up of the farmer glancing back toward a distant forest edge where wild berry bushes grow, feeling the strange new tension of waiting half a year for a meal",
            "punch_in",
        ),
        (
            "Wide delayed-return tension payoff",
            "Wide shot of the lone farmer leaning on a wooden hoe at dusk beside the vast, silent, unharvested field",
            "zoom_out",
        ),
    ],
    "SC20": [
        (
            "Wide irrigation canal digging",
            "Wide shot of ancient stick-figure farmers bending under a blazing sun to dig a long mud irrigation trench beside rows of tiny green sprouts",
            "pan_right",
        ),
        (
            "Medium repetitive weeding toil",
            "Medium shot of an exhausted stick-figure farmer kneeling in the dirt furrow, pulling weeds row after row from morning until late afternoon",
            "zoom_in",
        ),
        (
            "Close-up sweat on wooden hoe",
            "Close-up of the farmer's hands gripping a rough wooden hoe handle as heavy drops of sweat fall onto the dry soil",
            "zoom_in",
        ),
        (
            "Medium hauling river water",
            "Medium tracking shot of two stick-figure farmers carrying heavy clay water jars on shoulder poles from the river to the parched field",
            "pan_left",
        ),
        (
            "Close-up weary sunset pause",
            "Close-up of the ancient farmer wiping their forehead at sunset, staring at green stalks that still cannot be eaten for months",
            "punch_in",
        ),
        (
            "Wide unanswered question on the plain",
            "Wide evening shot of the tired farming figures walking back to their mud-brick village beside the unfinished canal",
            "zoom_out",
        ),
    ],
    "SC21": [
        (
            "Wide autumn storm horizon",
            "Wide dramatic view of dark autumn clouds gathering over a small ancient farming village centered around a communal mud-brick granary",
            "zoom_out",
        ),
        (
            "Medium inspecting low grain stores",
            "Medium shot of a stick-figure farmer and family peering inside a half-empty woven grain bin with tense, concerned postures",
            "zoom_in",
        ),
        (
            "Close-up frost on bare branch",
            "Close-up of crisp white frost crystals forming on a dry wheat stalk, signaling the approaching winter scarcity",
            "punch_in",
        ),
        (
            "Medium urgent communal harvest",
            "Medium shot of stick-figure villagers working shoulder to shoulder with bronze sickles, cutting and binding wheat sheaves before the rain begins",
            "pan_right",
        ),
        (
            "Close-up determined grip on sickle",
            "Close-up of the ancient farmer's hand gripping a curved bronze sickle with fierce focus to protect the household from hunger",
            "zoom_in",
        ),
        (
            "Wide village survival payoff",
            "Wide shot of the villagers carrying heavy golden sheaves into the central granary together as wind sweeps across the valley",
            "zoom_out",
        ),
    ],
    "SC22": [
        (
            "Wide ancient walled city-state",
            "Monumental stone walls and stepped ziggurat of an early empire where teams of stick-figure laborers haul timber and dressed stone blocks",
            "zoom_out",
        ),
        (
            "Close-up carved stone relief of toil",
            "Close-up of an ancient weathered stone relief carving showing stick figures carrying a heavy wooden yoke across their shoulders—the visual root of the word labor",
            "zoom_in",
        ),
        (
            "Medium royal scribe and grain tax",
            "Medium shot of an ancient stick-figure scribe holding a clay cuneiform tablet and stylus while guards watch farmers stack sacks of grain at the state gate",
            "pan_right",
        ),
        (
            "Medium quarry stone hauling",
            "Low-angle medium shot of stick-figure workers pulling a massive limestone block on wooden rollers with thick hemp ropes under the hot sun",
            "pan_left",
        ),
        (
            "Close-up steep granary steps",
            "Tight shot of exhausted stick-figure peasants climbing steep brick stairs with heavy woven grain sacks on their backs",
            "punch_in",
        ),
        (
            "Wide shadow of the ziggurat",
            "Wide atmospheric shot of a stick-figure laborer pausing to catch breath in the long shadow of the state monument",
            "zoom_out",
        ),
    ],
    "SC23": [
        (
            "Wide Giza workers village and bakery",
            "Wide historical view of the busy state bakery and brewery complex right beside the pyramid builders' village at Giza under warm late-afternoon light",
            "zoom_out",
        ),
        (
            "Medium daily ration distribution",
            "Medium shot of stick-figure stone masons lining up cheerfully at the end of their shift to receive warm round loaves of bread and clay jars of beer",
            "pan_right",
        ),
        (
            "Close-up warm bread and clay jug",
            "Close-up of a stick-figure builder holding a golden-crusted loaf of bread and a cool clay jar in both hands with an immediate, satisfied posture",
            "zoom_in",
        ),
        (
            "Medium evening barracks feast",
            "Medium shot of the stick-figure builders sitting together around outdoor ovens and fire pits, eating roasted fish and fresh bread after the day's stone hauling",
            "pan_left",
        ),
        (
            "Close-up daily cycle completion",
            "Close-up of a mason setting down their bronze chisel beside a warm meal—turning a twenty-year monument project into a tangible single-day reward",
            "punch_in",
        ),
        (
            "Wide sunset over Giza village",
            "Wide warm view of the builders' camp glowing with cooking fires at the foot of the rising limestone pyramid",
            "zoom_out",
        ),
    ],
    "SC24": [
        (
            "Wide temple courtyard at dawn",
            "Grand architectural view of an ancient stone temple courtyard by a full flowing river as morning sunbeams illuminate carved pillars and banners",
            "zoom_out",
        ),
        (
            "Medium sacred harvest procession",
            "Medium shot of ancient stick-figure farmers and artisans walking together along the river terrace carrying first-fruit wheat bundles toward the temple altar",
            "pan_right",
        ),
        (
            "Close-up placing carved capstone",
            "Close-up of two stick-figure masons carefully setting a finely carved stone block into place with calm, reverent concentration",
            "zoom_in",
        ),
        (
            "Low-angle monument to eternity",
            "Low-angle heroic perspective of stick-figure builders looking up at the sunlit limestone steps rising toward the sky as a shared cosmic work",
            "zoom_in",
        ),
        (
            "Medium community gathered by river",
            "Medium shot of the village standing together along the stone embankment watching the seasonal river waters fill the irrigation channels",
            "pan_left",
        ),
        (
            "Wide sacred purpose payoff",
            "Wide harmonious panorama of river, fields, and stone temple united under a radiant golden sky",
            "zoom_out",
        ),
    ],

    # ==================== CHAPTER 5: THE ARTISAN'S PRIDE ====================
    "SC25": [
        (
            "Wide medieval valley morning",
            "Scenic widescreen landscape of a medieval valley with timber-framed cottages, a watermill by a stream, terraced paddies, and a village forge under morning mist",
            "zoom_out",
        ),
        (
            "Close-up rooster and morning sun",
            "Close-up of a wooden weathervane and a crowing rooster perched on a thatched roof as the sun rises naturally over the hills—zero mechanical clocks in sight",
            "zoom_in",
        ),
        (
            "Medium task-oriented fieldwork",
            "Medium shot of a medieval stick-figure farmer testing the morning soil and guiding a wooden plow pulled by an ox at a steady, self-directed pace",
            "pan_right",
        ),
        (
            "Medium open village workshops",
            "Medium tracking shot along a cobblestone lane where a potter, a weaver, and a carpenter work inside open-front shops facing the village green",
            "pan_left",
        ),
        (
            "Close-up calm artisan rhythm",
            "Close-up of a weaver's hands passing a wooden shuttle through linen threads in natural window light without any stopwatch or supervisor",
            "zoom_in",
        ),
        (
            "Wide natural rhythm payoff",
            "Wide peaceful view of the village community working in step with daylight, weather, and the concrete task at hand",
            "zoom_out",
        ),
    ],
    "SC26": [
        (
            "Wide sunlit carpentry workshop",
            "Wide interior-exterior view of a traditional timber workshop opening onto a village square, stacked with seasoned oak planks and hand tools",
            "zoom_out",
        ),
        (
            "Medium planing fragrant oak",
            "Medium shot of a stick-figure carpenter leaning forward with skilled rhythm to push a hand plane along a solid oak chair leg on a workbench",
            "pan_right",
        ),
        (
            "Close-up carving maker mark",
            "Close-up of the carpenter using a small gouge chisel to carve a personal craft emblem underneath the finished wooden seat",
            "zoom_in",
        ),
        (
            "Medium direct handover to neighbor",
            "Medium shot outside the workshop door where the carpenter hands the completed oak chair directly to a smiling village neighbor",
            "pan_left",
        ),
        (
            "Close-up warm handshake of respect",
            "Close-up of the carpenter and the neighbor clasping hands beside the sturdy chair while passing villagers nod in appreciation",
            "punch_in",
        ),
        (
            "Wide human-scale economy payoff",
            "Wide shot of the lively village green where every tool, loaf, and chair connects the maker directly to the person who uses it",
            "zoom_out",
        ),
    ],
    "SC27": [
        (
            "Wide medieval blacksmith forge",
            "Warm atmospheric view of a traditional blacksmith forge with a glowing brick hearth, leather bellows, heavy iron anvil, and racks of tongs",
            "zoom_out",
        ),
        (
            "Medium heating raw iron",
            "Medium shot of the stick-figure master blacksmith pulling the bellows lever as bright orange coals heat a rough bar of iron",
            "zoom_in",
        ),
        (
            "Close-up hammer sparks on anvil",
            "Dynamic close-up of the blacksmith's hammer striking the glowing blade on the anvil with crisp precision as golden sparks arc across the frame",
            "punch_in",
        ),
        (
            "Medium quenching in water barrel",
            "Medium shot of the blacksmith plunging the shaped iron blade into a wooden barrel of water as a clean plume of white steam rises toward the rafters",
            "pan_right",
        ),
        (
            "Close-up inspecting finished blade",
            "Close-up of the stick-figure artisan holding up the polished, gleaming plowshare and sword in both hands, admiring the flawless edge they created from start to finish",
            "zoom_in",
        ),
        (
            "Wide master artisan pride payoff",
            "Wide shot of the proud blacksmith standing at the open forge doorway presenting the finished iron tools to admiring village farmers",
            "zoom_out",
        ),
    ],
    "SC28": [
        (
            "Wide ancestral homestead and terraces",
            "Wide view of a multi-generational family of stick figures tending terraced fields beside a stone-and-timber family homestead under clear skies",
            "zoom_out",
        ),
        (
            "Medium passing down craft tools",
            "Medium shot of an elder stick figure placing a well-worn wooden plane and iron chisel into the hands of a young apprentice beside the family workbench",
            "zoom_in",
        ),
        (
            "Medium repairing stone boundary wall",
            "Medium shot of parent and young stick figure lifting flat fieldstones together to mend the terrace wall that protects their household's harvest",
            "pan_right",
        ),
        (
            "Close-up carved family lintel",
            "Close-up of the wooden beam above the cottage doorway carved with generations of family emblems, grounding daily work in household honor",
            "zoom_in",
        ),
        (
            "Medium shared midday meal by field",
            "Medium shot of the three generations sitting on a woven mat under a shade tree, sharing rice, bread, and soup beside the land they cultivate together",
            "pan_left",
        ),
        (
            "Wide enduring kinship payoff",
            "Wide warm frame of the family standing together overlooking their terraced valley at late afternoon",
            "zoom_out",
        ),
    ],
    "SC29": [
        (
            "Wide wheel of the seasons",
            "Clean editorial circular calendar painted on a wooden village board showing golden harvest sheaves alternating with festival lanterns and winter hearths",
            "zoom_out",
        ),
        (
            "Medium autumn harvest festival",
            "Lively medium shot of stick-figure villagers gathered around long wooden tables on the village green with paper lanterns, flutes, and shared harvest dishes",
            "pan_right",
        ),
        (
            "Close-up resting farm tools",
            "Close-up of bronze sickles and wooden rakes hung neatly on a barn wall beside a wreath of autumn wheat, signaling that the season's heavy work is complete",
            "zoom_in",
        ),
        (
            "Medium cozy winter hearth",
            "Medium interior shot of a stick-figure family sitting warmly around an indoor stone fireplace while snow falls outside the window, mending nets and telling stories without guilt",
            "pan_left",
        ),
        (
            "Close-up peaceful unhurried rest",
            "Close-up of a stick figure sipping warm tea by the firelight with completely relaxed shoulders—zero late-night emails or unfinished spreadsheets following them home",
            "zoom_in",
        ),
        (
            "Wide seasonal balance payoff",
            "Wide serene view of the quiet village under a starry winter sky, resting deeply before spring returns",
            "zoom_out",
        ),
    ],
    "SC30": [
        (
            "Wide three-era craft table",
            "Clean editorial composition showing a long wooden table displaying three real tangible works side by side: a basket of wild figs, a golden wheat sheaf, and a forged iron blade",
            "pan_right",
        ),
        (
            "Medium prehistoric gatherer holding fruit",
            "Medium shot of a prehistoric stick figure holding up a freshly gathered basket of figs by the campfire with bright, focused eyes",
            "zoom_in",
        ),
        (
            "Medium ancient farmer holding wheat",
            "Medium shot of an ancient stick-figure farmer cradling a heavy golden bundle of harvested wheat beside the village granary",
            "pan_left",
        ),
        (
            "Medium medieval artisan holding blade",
            "Medium shot of a feudal stick-figure blacksmith lifting a gleaming iron plowshare forged by their own hands on the anvil",
            "zoom_in",
        ),
        (
            "Close-up hands touching real creation",
            "Intimate close-up of a stick figure's hands resting proudly on a finished wooden chair on a sunlit workbench—sight, touch, and effort united in one solid object",
            "punch_in",
        ),
        (
            "Wide tangible meaning payoff",
            "Wide balanced frame of the stick figure standing calmly beside the three historical creations before the dark smoke of the industrial era appears on the horizon",
            "zoom_out",
        ),
    ],

    # ==================== CHAPTER 6: THE INDUSTRIAL ALIENATION ====================
    "SC31": [
        (
            "Wide nineteenth-century factory gate",
            "Towering red-brick factory entrance dominated by a giant iron clock face and a roaring steam whistle under a gray industrial sky",
            "zoom_out",
        ),
        (
            "Medium lockstep morning march",
            "Medium shot of long rows of identical stick-figure workers walking in synchronized lockstep through the narrow iron gate at dawn",
            "pan_right",
        ),
        (
            "Close-up punching the timecard",
            "Sharp close-up of a stick figure's hand pushing a paper timecard into a heavy cast-iron stamping clock as the minute hand snaps forward",
            "punch_in",
        ),
        (
            "Medium cavernous machine hall",
            "Medium view down a vast factory hall filled with overhead iron line shafts, spinning leather belts, and stick figures standing fixed at narrow stations",
            "pan_left",
        ),
        (
            "Close-up barred window and sunlit field",
            "Close-up of a soot-streaked factory window looking out at a distant green hillside that the worker inside can no longer step out to touch",
            "zoom_in",
        ),
        (
            "Wide clock-ruled floor payoff",
            "Wide high-angle view of the giant mechanical clock overlooking the entire regimented factory floor",
            "zoom_out",
        ),
    ],
    "SC32": [
        (
            "Wide Taylorism stopwatch study",
            "Wide view of an early twentieth-century assembly line where a stick-figure efficiency manager in a vest stands with a brass stopwatch and clipboard behind a line worker",
            "zoom_out",
        ),
        (
            "Medium single-bolt repetition",
            "Medium shot of a stick-figure worker standing before a moving conveyor belt, turning the exact same wrench on an identical metal plate passing by",
            "pan_right",
        ),
        (
            "Close-up wrench turning bolt",
            "Extreme close-up of an iron wrench tightening a single hexagonal bolt on a flat steel bracket while identical brackets queue endlessly behind it",
            "punch_in",
        ),
        (
            "Wide fragmented blueprint on wall",
            "Editorial wall diagram showing a complete wooden carriage drawing sliced by red scissor lines into fifty tiny isolated metal parts that no single worker ever assembles whole",
            "zoom_out",
        ),
        (
            "Close-up exhausted blank gaze",
            "Close-up of the assembly-line stick figure with drooping posture and weary eyes watching the endless belt move past without ever seeing a finished product",
            "zoom_in",
        ),
        (
            "Wide conveyor alienation payoff",
            "Wide shot of the long mechanical conveyor belt stretching across the hall while the manager taps the stopwatch",
            "pan_left",
        ),
    ],
    "SC33": [
        (
            "Wide modern glass cubicle floor",
            "Wide architectural view of a twenty-first-century open office floor lined with identical white desks and glowing dual monitors in cool fluorescent light",
            "zoom_out",
        ),
        (
            "Medium sea of abstract spreadsheets",
            "Medium shot of a modern stick figure sitting between two large screens filled with rows of tiny cells, percentage bars, and nested folder icons",
            "zoom_in",
        ),
        (
            "Close-up mouse click into the cloud",
            "Close-up of the stick figure's hand clicking a wireless mouse as a document icon vanishes into an abstract cloud symbol on screen, leaving the physical desk bare",
            "pan_right",
        ),
        (
            "Medium endless inbox stack",
            "Medium shot of the stick figure watching new digital message envelopes appear on the monitor at the exact rate old ones are cleared",
            "pan_left",
        ),
        (
            "Close-up empty palms over keyboard",
            "Poignant close-up of the stick figure lifting both hands off the keyboard and looking down at their empty palms after ten hours of abstract screen work",
            "punch_in",
        ),
        (
            "Wide silent screen floor payoff",
            "Wide evening view of the quiet office floor where rows of monitors glow brightly while the human workers sit drained of energy",
            "zoom_out",
        ),
    ],
    "SC34": [
        (
            "Wide thirty-day calendar bridge",
            "Editorial widescreen composition where a modern stick figure sits at a desk on the left, separated from a small digital paycheck icon on the far right by thirty blank paper calendar squares",
            "pan_right",
        ),
        (
            "Medium prehistoric fire memory",
            "Warm medium shot of a prehistoric stick figure lowering a wooden spear and immediately lifting a steaming roasted meal from the campfire the very same evening",
            "zoom_in",
        ),
        (
            "Close-up cold banking notification",
            "Close-up of a smartphone screen resting on a dark desk, displaying a tiny row of abstract digits once a month with zero warmth, aroma, or physical substance",
            "punch_in",
        ),
        (
            "Medium staring across blank weeks",
            "Medium shot of the modern stick figure leaning chin on hand, looking across the long paper chain of twenty-nine unrewarded workdays stretching across the room",
            "pan_left",
        ),
        (
            "Close-up brass compass pointing nowhere",
            "Close-up of the ancient brass compass lying beside the keyboard, its needle motionless because a digital number thirty days away cannot wake an immediate-return drive",
            "zoom_in",
        ),
        (
            "Wide delayed-reward gap payoff",
            "Wide shot of the lone office desk facing the vast wall calendar that separates today's effort from next month's abstract number",
            "zoom_out",
        ),
    ],
    "SC35": [
        (
            "Wide corporate pep-rally stage",
            "Wide view of an office conference room decorated with giant exclamation-mark banners, shiny plastic trophies, and stacks of glossy motivational books",
            "zoom_out",
        ),
        (
            "Medium speaker with megaphone",
            "Medium shot of an energetic stick-figure presenter standing on a podium shouting into a large megaphone toward rows of tired office stick figures",
            "pan_right",
        ),
        (
            "Close-up paper bandage on iron beam",
            "Sharp editorial close-up of a small decorative paper sticker being pressed over a deep structural crack in a heavy stone arch—incapable of bearing real weight",
            "punch_in",
        ),
        (
            "Medium three coffee cups and posters",
            "Medium shot of a stick figure back at their cubicle surrounded by framed wall slogans and three empty espresso cups, still staring at the same abstract spreadsheet",
            "pan_left",
        ),
        (
            "Close-up fading confetti on floor",
            "Close-up of paper confetti lying motionless on the office carpet beside a pair of tired feet under the desk",
            "zoom_in",
        ),
        (
            "Wide hollow hype payoff",
            "Wide quiet shot of the empty conference room after the speech ends, showing that external shouting cannot fix a broken work structure",
            "zoom_out",
        ),
    ],
    "SC36": [
        (
            "Wide late-night bedroom glow",
            "Wide interior shot of a dark bedroom at 1:00 AM where a stick figure sits upright in bed illuminated by a smartphone playing a fiery inspirational video",
            "zoom_out",
        ),
        (
            "Medium midnight surge of resolve",
            "Medium shot of the stick figure pumping a fist in bed while holding a bright red paper lantern that glows warmly in the quiet night",
            "zoom_in",
        ),
        (
            "Wide morning desk reality",
            "Wide morning cut to the exact same stick figure at 8:00 AM sitting before a complex multi-tab spreadsheet in cold daylight",
            "pan_right",
        ),
        (
            "Close-up extinguished lantern",
            "Close-up of the red paper lantern lying folded and unlit beside the keyboard and cold coffee mug as the morning task offers zero tangible anchor",
            "punch_in",
        ),
        (
            "Medium wry recognition sigh",
            "Medium shot of the stick figure leaning back with a gentle, self-aware half-smile, realizing why midnight excitement always evaporates by morning",
            "pan_left",
        ),
        (
            "Wide doorway to behavioral lab",
            "Wide transitional frame where the stick figure looks toward a bright university laboratory doorway with two wooden worktables visible inside",
            "zoom_out",
        ),
    ],

    # ==================== CHAPTER 7: THE SISYPHUS LAB & THREE PILLARS ====================
    "SC37": [
        (
            "Wide university psychology lab",
            "Bright, clean university laboratory room with two wooden worktables, open boxes of colorful plastic building bricks, and a stick-figure researcher holding a notepad",
            "zoom_out",
        ),
        (
            "Medium Group 1 assembling robot",
            "Medium shot of a stick-figure participant at the first table eagerly snapping plastic bricks together to build a small standing toy robot",
            "zoom_in",
        ),
        (
            "Close-up row of standing robots",
            "Close-up of five completed toy robots lined up neatly on a wooden display shelf beside small paper bills earned for each model",
            "pan_right",
        ),
        (
            "Medium proud sixth completion",
            "Medium shot of the participant smiling with clear pride as they place a sixth finished robot onto the growing display line",
            "zoom_in",
        ),
        (
            "Close-up researcher tally sheet",
            "Close-up of the researcher's clipboard showing a tall bar chart beside the table where creations are preserved",
            "punch_in",
        ),
        (
            "Wide visible progress payoff",
            "Wide warm frame of the participant admiring the long row of eleven standing models built by their own hands",
            "zoom_out",
        ),
    ],
    "SC38": [
        (
            "Wide Group 2 Sisyphus table",
            "Wide shot of the second laboratory table where a stick-figure participant hands a freshly assembled toy robot to the researcher beside the exact same stack of paper bills",
            "zoom_out",
        ),
        (
            "Medium dismantling in plain sight",
            "Medium shot of the researcher immediately pulling the newly built robot apart into loose plastic bricks right in front of the participant's eyes and dropping them back into the box",
            "punch_in",
        ),
        (
            "Close-up stunned expression",
            "Close-up of the participant's round white head with wide eyes watching their careful handiwork reduced to a pile of scattered pieces",
            "zoom_in",
        ),
        (
            "Medium pushing chair back",
            "Medium shot of the participant dropping their hands from the table and pushing their chair back, stopping early even though more paper bills sit waiting",
            "pan_left",
        ),
        (
            "Wide two-table side-by-side view",
            "Wide single-room view showing both tables in the same laboratory: eleven proud standing robots on the left table versus a quiet pile of loose bricks on the right table",
            "pan_right",
        ),
        (
            "Close-up untouched bills beside bricks",
            "Close-up of crisp paper bills lying untouched beside the disassembled plastic bricks—proving that human drive collapses when meaning is erased",
            "zoom_out",
        ),
    ],
    "SC39": [
        (
            "Wide three-pillar stone archway",
            "Grand architectural illustration of a classical stone archway supported by three carved columns standing on a sunlit plaza",
            "zoom_out",
        ),
        (
            "Close-up three relief emblems",
            "Close-up panning across the three carved stone medallions on the columns: a directional compass, a handcrafted wooden chair, and two clasped hands",
            "pan_right",
        ),
        (
            "Medium researchers inspecting cracks",
            "Medium shot of two stick-figure psychologists with notebooks pointing up at fractures spreading across the stone columns under heavy gray clouds of modern routine",
            "zoom_in",
        ),
        (
            "Close-up coins unable to prop arch",
            "Sharp close-up of a stack of coins placed beneath the cracking stone beam, slipping aside because external rewards cannot replace the three structural columns",
            "punch_in",
        ),
        (
            "Medium focusing on the first column",
            "Medium shot of the stick-figure narrator stepping beside the first stone column carved with the directional compass of self-direction",
            "pan_left",
        ),
        (
            "Wide diagnostic architecture payoff",
            "Wide clear view of the three-column archway standing as the blueprint for repairing human energy",
            "zoom_out",
        ),
    ],
    "SC40": [
        (
            "Wide open ridge vs glass box",
            "Deep-perspective editorial frame: in the foreground, a modern stick figure sits inside a cramped glass booth surrounded by red alarm bells; through the window behind, an open sunlit ridge stretches free",
            "zoom_out",
        ),
        (
            "Medium artisan choosing rhythm",
            "Warm medium shot of a traditional stick-figure carpenter setting down their plane to step outside and breathe the morning air whenever the task reaches a natural pause",
            "pan_left",
        ),
        (
            "Medium notification hailstorm",
            "Medium shot of the modern stick figure ducking over a laptop as red popup cards, chat bubbles, and surveillance timers crowd around the monitor",
            "pan_right",
        ),
        (
            "Close-up wrists pulled by strings",
            "Close-up of the stick figure's hands hovering over the keyboard while thin dotted red lines from five different alert icons pull their wrists in opposite directions",
            "punch_in",
        ),
        (
            "Close-up defensive fatigue posture",
            "Close-up of the stick figure resting their forehead on one hand in front of the ringing screen—their mind shutting down to defend its lost sense of control",
            "zoom_in",
        ),
        (
            "Wide fractured compass pillar",
            "Wide shot of the first stone column carved with a compass showing a deep crack across its center",
            "zoom_out",
        ),
    ],
    "SC41": [
        (
            "Wide overflowing granary vs bare desk",
            "Editorial composition contrasting an ancient stick-figure farmer standing beside a woven granary brimming with golden grain in the background against a modern worker at a completely bare white desk in the foreground",
            "zoom_out",
        ),
        (
            "Close-up hands in golden grain",
            "Warm close-up of an artisan's hands lifting real harvested wheat sheaves and touching the smooth grain of a newly planed oak board",
            "zoom_in",
        ),
        (
            "Medium year of files vanishing",
            "Medium shot of a modern stick figure clicking a mouse on a laptop as twelve months of digital folders float upward into a pale cloud icon, leaving zero trace on the desk",
            "pan_right",
        ),
        (
            "Close-up empty palms before dark screen",
            "Intimate close-up of the modern stick figure looking down at their open, empty hands reflected in a switched-off black monitor at the end of the year",
            "punch_in",
        ),
        (
            "Medium reaching for solid craft",
            "Medium shot of the stick figure touching the wooden surface of the desk, yearning for a real, finished creation that their eyes can verify",
            "pan_left",
        ),
        (
            "Wide fractured chair pillar",
            "Wide shot of the second stone column carved with a handcrafted chair showing a deep fracture across its stone shaft",
            "zoom_out",
        ),
    ],
    "SC42": [
        (
            "Wide dark room and warm campfire window",
            "Atmospheric wide shot of a lone modern stick figure sitting in a dark room lit only by cold blue monitor light, while a warm painting of a tribal campfire hangs on the wall behind",
            "zoom_out",
        ),
        (
            "Medium village face-to-face gratitude",
            "Warm medium shot of a village baker handing a fresh loaf directly across a wooden counter to a smiling child and parent who look into their eyes with thanks",
            "pan_left",
        ),
        (
            "Medium isolated screen cubicle",
            "Medium shot of the modern stick figure sitting knees-up on a swivel chair at night, sending digital reports toward rows of faceless gray avatar circles on a screen",
            "pan_right",
        ),
        (
            "Close-up cold screen reflection",
            "Close-up of the stick figure's face illuminated by the pale blue rectangle of the monitor in a completely silent room",
            "zoom_in",
        ),
        (
            "Close-up three brass keys on desk",
            "Crisp close-up of three warm brass keys resting on the wooden desk—their bows shaped like a compass, a small chair, and two joined hands—catching the first golden ray of dawn",
            "punch_in",
        ),
        (
            "Wide dawn light entering window",
            "Wide hopeful shot as warm morning sunlight streams through the open window across the desk, preparing the four practical solutions of the final chapter",
            "zoom_out",
        ),
    ],

    # ==================== CHAPTER 8: REDESIGNING YOUR DAILY HUNT ====================
    "SC43": [
        (
            "Wide sunlit reconciliation study",
            "Bright, warm editorial room where a modern stick figure in a rolled-up shirt stands face to face with a friendly prehistoric hunter stick figure holding a wooden spear",
            "zoom_out",
        ),
        (
            "Medium handshake across eras",
            "Medium shot of the modern stick figure and the prehistoric hunter smiling warmly and clasping hands across a sunlit wooden table",
            "zoom_in",
        ),
        (
            "Close-up setting down self-blame",
            "Close-up of the modern stick figure placing a heavy dark ledger down on the floor and opening a clean, bright sketchpad on the desk",
            "pan_right",
        ),
        (
            "Medium side-by-side allies",
            "Medium shot of the prehistoric hunter standing calmly beside the modern desk, pointing with their spear toward a small, clear target card pinned by the monitor",
            "pan_left",
        ),
        (
            "Close-up calm confident posture",
            "Close-up of the modern stick figure taking a deep breath with upright shoulders and clear, focused eyes—working with human nature rather than fighting it",
            "punch_in",
        ),
        (
            "Wide ready-for-action payoff",
            "Wide balanced frame of the modern worker and ancient hunter ally standing together in the sunlit room",
            "zoom_out",
        ),
    ],
    "SC44": [
        (
            "Wide giant boulder on desk",
            "Wide editorial shot of a stick figure standing before a massive, intimidating uncarved gray stone block resting atop their office desk",
            "zoom_out",
        ),
        (
            "Medium dividing into small bricks",
            "Medium shot of the stick figure using a clean wooden ruler and pencil to divide the overwhelming block into six small, neat hand-sized building bricks",
            "zoom_in",
        ),
        (
            "Close-up thirty-minute sand glass",
            "Crisp close-up of a wooden thirty-minute sand hourglass standing beside a single index card showing one clear drawing of an opening paragraph",
            "punch_in",
        ),
        (
            "Medium focused micro-hunt",
            "Medium shot of the stick figure typing with brisk, absorbed focus while the golden sand flows smoothly through the glass timer",
            "pan_right",
        ),
        (
            "Close-up first completed brick",
            "Close-up of the sand finishing its run right as the stick figure places a solid finished wooden block onto the corner of the desk with a satisfied nod",
            "zoom_in",
        ),
        (
            "Wide momentum building payoff",
            "Wide shot of the stick figure eagerly reaching for the second small index card as a neat row of finished blocks begins to grow",
            "zoom_out",
        ),
    ],
    "SC45": [
        (
            "Wide tactile wooden workspace",
            "Warm overhead view of a wooden desk featuring a thick open paper notebook, a bold black fountain pen, paper index cards, and a steaming cup of tea beside the laptop",
            "zoom_out",
        ),
        (
            "Close-up decisive ink strikethrough",
            "Extreme close-up of the stick figure's hand drawing a thick, unmistakable black ink line across a completed item in the physical paper notebook",
            "punch_in",
        ),
        (
            "Medium moving physical cards",
            "Medium shot of the stick figure moving colorful paper index cards by hand from a stack on the left to a growing completed stack on the right",
            "pan_right",
        ),
        (
            "Close-up tall stack of finished cards",
            "Close-up of the stick figure's fingers tapping the thick, solid stack of completed paper cards that their eyes and hands can physically verify",
            "zoom_in",
        ),
        (
            "Medium satisfied artisan posture",
            "Medium shot of the stick figure leaning back at the desk holding the fountain pen with the same quiet pride as a village carpenter admiring a finished chair",
            "pan_left",
        ),
        (
            "Wide tactile workspace payoff",
            "Wide warm frame of the desk where physical paper and ink anchor abstract digital work in the real world",
            "zoom_out",
        ),
    ],
    "SC46": [
        (
            "Wide stone threshold at dawn",
            "Wide shot of a stick figure standing at the shadowy doorway of a shelter looking out at a stone footpath where the tiles ahead are initially unlit",
            "zoom_out",
        ),
        (
            "Close-up five-minute first step",
            "Close-up of the stick figure's foot stepping boldly onto the very first stone tile right outside the doorway—and that tile immediately glowing warm amber",
            "punch_in",
        ),
        (
            "Medium sequential path lighting up",
            "Medium tracking shot from the side as each consecutive stone tile lights up golden one by one ONLY after the stick figure's foot touches it",
            "pan_right",
        ),
        (
            "Close-up motion igniting focus",
            "Close-up of the stick figure's hands opening a document and writing a single rough line, which immediately sparks a warm amber glow across the desk lamp",
            "zoom_in",
        ),
        (
            "Medium brisk effortless stride",
            "Medium shot of the stick figure now striding forward at full speed along the illuminated stone path with upright, energized posture",
            "pan_left",
        ),
        (
            "Wide action-before-emotion payoff",
            "Wide inspiring view of the long golden path trailing behind the moving stick figure under an open morning sky",
            "zoom_out",
        ),
    ],
    "SC47": [
        (
            "Wide evening lantern gathering",
            "Warm evening view of a wooden table lit by a hanging amber lantern where three modern stick-figure friends sit together sharing hot tea and lively conversation",
            "zoom_out",
        ),
        (
            "Medium real-world feedback exchange",
            "Medium shot of a stick figure showing a finished sketch or project page to a colleague across the table, who smiles and nods with genuine face-to-face appreciation",
            "zoom_in",
        ),
        (
            "Close-up clinking ceramic mugs",
            "Intimate close-up of two stick figures clinking warm ceramic tea mugs across the lantern-lit table—recreating the ancient warmth of the tribal campfire",
            "pan_right",
        ),
        (
            "Medium closing the laptop at sunset",
            "Medium shot of the stick figure calmly folding the laptop shut as the sun sets outside the window, leaving work completely behind for the night",
            "pan_left",
        ),
        (
            "Close-up peaceful evening stretch",
            "Close-up of the stick figure standing by the open night window looking up at the crescent moon and stars with rested, guilt-free eyes",
            "zoom_in",
        ),
        (
            "Wide tranquil night recovery payoff",
            "Wide serene exterior view of the warm golden window glowing softly in the quiet night, restoring energy for tomorrow",
            "zoom_out",
        ),
    ],
    "SC48": [
        (
            "Wide Monday morning callback sunlit",
            "The exact same modern apartment desk from Scene 1 at 8:00 AM Monday, now bathed in warm golden morning sunlight streaming through an open window",
            "zoom_out",
        ),
        (
            "Medium calm morning arrival",
            "Medium shot of the stick figure sitting down at the wooden desk with a steaming mug of coffee, looking at the laptop with a calm, self-assured smile",
            "zoom_in",
        ),
        (
            "Close-up single paper task card",
            "Close-up of the stick figure placing one small paper index card with a single clear thirty-minute goal and a fountain pen right beside the keyboard",
            "punch_in",
        ),
        (
            "Medium effortless first keystrokes",
            "Medium shot of the stick figure placing both hands on the keyboard and smoothly typing the first lines of work as crisp text fills the formerly blank screen",
            "pan_right",
        ),
        (
            "Medium ancient ally nod by window",
            "Medium shot showing the warm golden reflection of the prehistoric hunter in the sunlit window glass nodding in quiet harmony beside the working modern stick figure",
            "pan_left",
        ),
        (
            "Wide final closing loop frame",
            "Wide cinematic pull-back of the bright sunlit room as the stick figure works with calm, steady momentum—completing the 13-minute visual journey",
            "zoom_out",
        ),
    ],
}


def get_scene_beats_v2(scene_id: str, count: int = 6) -> list[tuple[str, str, str]]:
    """Return `count` distinct (framing, english_description, camera_effect) tuples for `scene_id`."""
    base = list(EN_SCENE_BEATS_V2[scene_id])
    if count <= len(base):
        return base[:count]
    extra_angles = [
        (
            "High-angle bird's-eye editorial view",
            f"Top-down architectural perspective of {base[0][1].lower()}, clean black ink line art with warm cream negative space",
            "zoom_out",
        ),
        (
            "Low-angle expressive perspective",
            f"Low-angle heroic perspective of {base[1][1].lower()}, warm ochre and slate pastel fills",
            "zoom_in",
        ),
    ]
    while len(base) < count:
        idx = len(base) - len(EN_SCENE_BEATS_V2[scene_id])
        candidate = extra_angles[idx % len(extra_angles)]
        # Avoid consecutive duplicate camera effects
        if base and candidate[2] == base[-1][2]:
            alt_effect = "pan_right" if candidate[2] != "pan_right" else "zoom_in"
            candidate = (candidate[0], candidate[1], alt_effect)
        base.append(candidate)
    return base[:count]


def get_scene_beats(scene_id: str, count: int = 6) -> list[tuple[str, str]]:
    """Backward-compatible helper returning (framing, english_description) 2-tuples."""
    return [(f, d) for f, d, _ in get_scene_beats_v2(scene_id, count)]
