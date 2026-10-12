"""English visual beat definitions (Editorial Graphic Edition) for the 48 scenes of the 13-minute Hard Things & Boredom explainer.

Covers the full 8-chapter narrative:
- Chapter 1: The Morning Screen Trap & The Effort Illusion (SC01-SC06)
- Chapter 2: Baseline Dopamine & The Contrast Principle of Effort (SC07-SC12)
- Chapter 3: Prehistoric Era: Effort-Driven Reward & Natural Stillness (SC13-SC18)
- Chapter 4: Ancient Classical Era: Stoic Voluntary Hardship & Mental Fortitude (SC19-SC24)
- Chapter 5: Medieval & Artisan Era: Monastic Silence, Craft & The Flow State (SC25-SC30)
- Chapter 6: Industrial & Commercial Era: The Rise of Packaged Instant Distraction (SC31-SC36)
- Chapter 7: Modern Digital Era: The Empty Room Shock Experiment & The Power of Boredom (SC37-SC42)
- Chapter 8: Three Neuro-Protocols to Trick Your Brain Into Loving Hard Things (SC43-SC48)
"""
from __future__ import annotations

STYLE_PREFIX = (
    "Editorial 2D hand-drawn ink illustration, crisp black ink lines on warm cream off-white paper background, "
    "muted earthy ochre and slate pastel fills, generous negative space, 16:9 widescreen composition. "
    "Anonymous stick figure with large round white head, thick bold black outline, simple dot eyes, expressive line mouth, "
    "thin stick limbs, single torso. Expressive physical posture and sightlines, zero brain cutaways, "
    "no realistic faces, no text, no letters, no numbers, no watermarks, uncluttered."
)

EN_SCENE_BEATS_HARD_THINGS: dict[str, list[tuple[str, str, str]]] = {
    # ==================== CHAPTER 1: THE MORNING SCREEN TRAP ====================
    "SC01": [
        ("Wide morning desk and glowing phone", "Wide shot of a clean wooden work desk in early morning light, an unopened laptop sitting beside a brightly glowing smartphone while a stick figure reaches toward the small screen", "zoom_out"),
        ("Close-up untouched complex blueprint", "Close-up of a thick project binder and fountain pen lying completely untouched on the warm oak desk surface", "zoom_in"),
        ("Medium thumb scrolling posture", "Medium side view of the stick figure slouching in an office chair, thumb flicking endlessly upward across the glowing mobile screen", "pan_right"),
        ("Over-the-shoulder rapid feed cards", "Over-the-shoulder view looking past the stick figure at a stream of tiny floating geometric media cards rising from the handheld device", "zoom_in"),
        ("Low-angle heavy hand on mouse", "Low-angle shot of the stick figure's other hand resting limply near the laptop trackpad, feeling an invisible wall of resistance", "pan_left"),
        ("Wide morning sunlight fading", "Wide cinematic pull-back showing the room shadows lengthening across the floor while the important project remains unopened", "zoom_out"),
    ],
    "SC02": [
        ("Wide mirror of self-doubt", "Wide shot of the stick figure standing before a tall minimalist wall mirror in a quiet hallway, shoulders drooping in frustration", "zoom_out"),
        ("Close-up crumpled daily checklist", "Close-up of a small paper notepad with uncrossed task lines lying beside a cold ceramic mug on the table", "zoom_in"),
        ("Medium red ink slash across blame", "Bold editorial composition where a sweeping crimson ink brushstroke crosses out a dark storm cloud hovering above the stick figure", "punch_in"),
        ("Medium upright posture shift", "Medium shot of the stick figure lifting their chin with a calm, curious gaze as the heavy cloud dissolves into clean cream paper", "pan_right"),
        ("Close-up steady hands on desk", "Close-up of two stick-figure hands placing a notebook neatly in the center of the desk with composed energy", "pan_left"),
        ("Wide open studio perspective", "Wide balanced frame showing the stick figure standing in an airy sunlit study room, ready to examine the hidden mechanism", "zoom_out"),
    ],
    "SC03": [
        ("Wide balanced seesawbeam on stone", "Wide architectural illustration of a sleek wooden balance beam resting on a triangular stone fulcrum in the center of a cream studio", "zoom_out"),
        ("Close-up pleasure weight pressing down", "Close-up of the left side of the wooden beam weighed down by a cluster of bright neon confectionery cubes and tiny bells", "zoom_in"),
        ("Medium stick figure watching tilt", "Medium shot of a researcher stick figure holding a clipboard on the right third of the frame, observing the tilted wooden beam", "pan_right"),
        ("Close-up counter-weights dropping", "Close-up of dark slate stone blocks automatically sliding onto the opposite end of the beam to restore horizontal equilibrium", "punch_in"),
        ("Medium tilted discomfort reaction", "Medium shot of an everyday stick figure sitting beside the tilted beam, rubbing their temples as the heavy slate side tips downward", "pan_left"),
        ("Wide equilibrium law diagram", "Wide editorial view of the balance beam oscillating softly under warm gallery lighting, illustrating internal homeostasis", "zoom_out"),
    ],
    "SC04": [
        ("Wide buffet of instant stimuli", "Wide shot of a modern lounge table overflowing with glowing screens, party confetti, and tall dessert glasses around a stick figure", "zoom_out"),
        ("Close-up overflowing neon goblet", "Close-up of a tall glass brimming with sparkling amber bubbles that spill over onto the wooden tabletop", "zoom_in"),
        ("Medium numbed expression amidst noise", "Medium shot of the stick figure sitting among the floating party icons with half-closed, exhausted eyes and flat posture", "pan_right"),
        ("Over-the-shoulder gray workbook", "Over-the-shoulder view looking from the bright neon table toward a plain wooden drafting table that looks dull and gray by contrast", "zoom_in"),
        ("Low-angle stepping back from desk", "Low-angle shot of the stick figure recoiling slightly from the plain drafting table as if a simple book were a steep mountain", "pan_left"),
        ("Wide contrast of overstimulation", "Wide composition showing the tiny stick figure surrounded by towering carnival lights while the quiet library door stands in shadow", "zoom_out"),
    ],
    "SC05": [
        ("Wide mountain trail vs escalator", "Wide editorial landscape showing a gentle stone staircase leading up a scenic hill beside a noisy neon conveyor belt", "zoom_out"),
        ("Medium traveler pausing at base", "Medium shot of the stick figure standing at the bottom step of the stone staircase, looking up at the summit with hesitation", "zoom_in"),
        ("Close-up boots on stone step", "Close-up of simple ink-drawn boots resting on the first carved stone step, surrounded by small wildflowers", "pan_right"),
        ("Overhead winding path to vista", "High-angle view of the winding stone trail leading to a bright pavilion overlooking a peaceful valley", "zoom_in"),
        ("Medium looking back at conveyor", "Medium shot of the stick figure glancing back at the crowded neon belt that leads only in a tight circle", "pan_left"),
        ("Wide horizon of meaningful effort", "Wide pull-back revealing the vast open sky above the hilltop pavilion, inviting a deeper inquiry into human drive", "zoom_out"),
    ],
    "SC06": [
        ("Wide grand gallery of eras", "Wide panoramic ink illustration of a long arched stone colonnade connecting five distinct historical courtyards", "zoom_out"),
        ("Medium narrator figure at first arch", "Medium shot of the stick figure standing at the first stone archway, gesturing invitingly down the sunlit corridor", "zoom_in"),
        ("Close-up symbolic objects on pedestals", "Close-up of four stone pedestals holding a wooden fire-drill, a classical scroll, a brass lens, and a modern hourglass", "pan_right"),
        ("Low-angle sunlit colonnade", "Low-angle perspective of tall architectural arches casting rhythmic geometric shadows across the cream floor", "zoom_in"),
        ("Medium confident stride forward", "Medium shot of the stick figure walking steadily into the first courtyard with an eager, inquisitive posture", "pan_left"),
        ("Wide journey opening vista", "Expansive wide shot framing the entire historical colonnade under a clear ochre sky", "zoom_out"),
    ],

    # ==================== CHAPTER 2: BASELINE DOPAMINE & CONTRAST ====================
    "SC07": [
        ("Wide acoustic wave laboratory", "Wide shot of a clean scientific drafting room where a long horizontal parchment chart spans across a wide wooden wall", "zoom_out"),
        ("Close-up steady baseline wave", "Close-up of a smooth, rhythmic ink waveform pulsing gently along a steady horizontal reference line on cream parchment", "zoom_in"),
        ("Medium scientist stick figure pointing", "Medium shot of a stick figure in a simple lab coat pointing a wooden rod toward the steady middle line of the chart", "pan_right"),
        ("Close-up rising wave peak", "Close-up of the ink line rising smoothly into a graceful arch as a small lantern illuminates the paper", "punch_in"),
        ("Medium harmonious posture", "Medium shot of an everyday stick figure walking briskly beside the steady waveform with balanced, energetic stride", "pan_left"),
        ("Wide balanced chart panorama", "Wide view of the drafting room showing how the steady baseline supports calm, sustained daily focus", "zoom_out"),
    ],
    "SC08": [
        ("Wide comparison of two mornings", "Wide architectural view of two adjacent minimalist rooms separated by a clean stone pillar", "zoom_out"),
        ("Close-up sudden vertical spike", "Close-up of an ink waveform shooting violently upward like a jagged lightning bolt and then plunging into a deep trough", "zoom_in"),
        ("Medium figure in deep trough", "Medium shot of a stick figure sitting at the bottom of the drawn trough, looking up at a normal wooden desk that towers overhead", "pan_right"),
        ("Close-up step altitude gap", "Detailed close-up of a brass caliper measuring the vertical distance between the deep trough and the normal task platform", "punch_in"),
        ("Medium exhausted sigh at desk", "Medium shot of the stick figure resting their chin on the desk because the reward level has dropped below the baseline", "pan_left"),
        ("Wide trough to plateau perspective", "Wide editorial frame illustrating how an early spike makes ordinary productive work feel like climbing out of a canyon", "zoom_out"),
    ],
    "SC09": [
        ("Wide neurobiology observation room", "Wide shot of an academic lecture room with a large slate board displaying clean geometric reward curves", "zoom_out"),
        ("Close-up expectation vs reality gap", "Close-up of two parallel horizontal bars on parchment where a dashed arrow measures the gap between expected and actual reward", "zoom_in"),
        ("Medium scholar holding bell and apple", "Medium shot of a scholar stick figure holding a small brass bell in one hand and a simple wooden apple prop in the other", "pan_right"),
        ("Close-up spark at surprise cue", "Close-up of a bright golden ink starburst appearing at the exact moment the brass bell rings on the timeline", "punch_in"),
        ("Medium figure leaning in with interest", "Medium shot of an observer stick figure leaning forward eagerly as the unexpected discovery unfolds on the table", "pan_left"),
        ("Wide lecture hall synthesis", "Wide pull-back of the quiet lecture hall showing the elegance of reward prediction in everyday behavior", "zoom_out"),
    ],
    "SC10": [
        ("Wide morning kitchen and study", "Wide shot of a bright apartment morning where a stick figure sits on a sofa surrounded by snack wrappers and a glowing tablet", "zoom_out"),
        ("Close-up towering entertainment peak", "Close-up of a tall paper tower built from stacked entertainment cards casting a long dark shadow over a small study notebook", "zoom_in"),
        ("Medium transition to work desk", "Medium shot of the stick figure walking slowly from the bright sofa to the wooden work desk with heavy, dragging footsteps", "pan_right"),
        ("Over-the-shoulder dull gray page", "Over-the-shoulder view of the open notebook looking completely flat and uninviting after the morning entertainment spike", "zoom_in"),
        ("Low-angle yawning stick figure", "Low-angle shot of the stick figure stretching and yawning, struggling to muster interest in the quiet page", "pan_left"),
        ("Wide shadowed desk room", "Wide shot showing how morning overstimulation steals the natural flavor of productive daytime work", "zoom_out"),
    ],
    "SC11": [
        ("Wide serene sunlit conservatory", "Wide shot of a quiet glass conservatory filled with potted ferns and a single wooden writing table in the morning sun", "zoom_out"),
        ("Close-up warm teacup on saucer", "Close-up of a simple ceramic cup of warm tea steaming gently on a bare wooden tabletop with no digital devices in sight", "zoom_in"),
        ("Medium calm breathing by window", "Medium shot of the stick figure standing by the tall window, hands clasped loosely behind their back, gazing at the garden", "pan_right"),
        ("Close-up smooth rising ink line", "Close-up of the parchment waveform rising gently above the calm baseline as the stick figure opens a sketchbook", "punch_in"),
        ("Medium sketching with focus", "Medium shot of the stick figure drawing architectural lines in the sketchbook with an absorbed, peaceful smile", "pan_left"),
        ("Wide sunlit flow room", "Wide pull-back showing the tranquil conservatory where low morning stimulation makes deep work feel naturally rewarding", "zoom_out"),
    ],
    "SC12": [
        ("Wide stone bridge to antiquity", "Wide cinematic view of a stone footbridge crossing a misty canyon from a modern studio toward an open natural plain", "zoom_out"),
        ("Medium figure stepping onto bridge", "Medium shot of the stick figure walking across the stone arch, carrying only a simple leather satchel", "zoom_in"),
        ("Close-up compass on stone parapet", "Close-up of a brass pocket compass resting on the stone railing, needle pointing toward the open wilderness ahead", "pan_right"),
        ("Overhead canyon transition", "High-angle bird's-eye view of the bridge linking modern architectural lines with organic rolling hills", "zoom_in"),
        ("Medium looking toward open plain", "Medium shot of the stick figure shading their eyes as warm wind sweeps across the tall grass on the far bank", "pan_left"),
        ("Wide natural horizon opening", "Expansive wide shot of the untouched landscape where effort and reward were originally forged together", "zoom_out"),
    ],

    # ==================== CHAPTER 3: PREHISTORIC EFFORT-DRIVEN REWARD ====================
    "SC13": [
        ("Wide prehistoric savanna morning", "Wide establishing shot of an open prehistoric grassland under early morning sun, with scattered acacia trees and rocky outcrops", "zoom_out"),
        ("Close-up wooden fire-drill spindle", "Close-up of two stick-figure hands briskly spinning a wooden spindle against a dry cedar hearth board until a wisp of smoke rises", "zoom_in"),
        ("Medium kneeling by kindling", "Medium shot of a prehistoric stick figure in a simple hide tunic kneeling intently over the smoking kindling bundle", "pan_right"),
        ("Close-up first golden flame", "Close-up of a bright orange-ochre flame bursting to life in the dry grass bundle after sustained physical effort", "punch_in"),
        ("Medium warm smile by fire", "Medium shot of the stick figure sitting back with a deeply satisfied expression as the warm firelight illuminates their face", "pan_left"),
        ("Wide savanna camp at sunrise", "Wide pull-back showing the small column of smoke rising peacefully into the vast morning sky", "zoom_out"),
    ],
    "SC14": [
        ("Wide rocky cliffside bee hive", "Wide shot of a tall limestone cliff face with wild honeycombs tucked high inside a sunlit rock crevice", "zoom_out"),
        ("Medium climbing the rock ledges", "Medium shot of a nimble prehistoric stick figure climbing carefully up the natural stone ledges with a woven basket slung over one shoulder", "zoom_in"),
        ("Close-up hand gripping stone", "Close-up of ink-drawn fingers gripping a rough limestone hold, showing real physical exertion before the reward", "pan_right"),
        ("Close-up golden honeycomb harvest", "Close-up of a piece of golden wild honeycomb being placed gently into the woven reed basket", "punch_in"),
        ("Medium sharing at cliff base", "Medium shot of two prehistoric stick figures sitting at the base of the cliff, happily tasting the hard-won honey together", "pan_left"),
        ("Wide natural effort landscape", "Wide landscape view illustrating that every ancient pleasure required an honest investment of movement and skill", "zoom_out"),
    ],
    "SC15": [
        ("Wide quiet afternoon under baobab", "Wide shot of three prehistoric stick figures resting in the cool shade of a giant baobab tree during the quiet midday heat", "zoom_out"),
        ("Close-up clouds drifting slowly", "Close-up of soft ink-drawn cumulus clouds drifting slowly across a vast, empty cream-colored sky", "zoom_in"),
        ("Medium whittling a wooden spear", "Medium shot of a stick figure calmly whittling a smooth wooden shaft with a flint flake, unhurried and completely at ease", "pan_right"),
        ("Close-up ripples on still pond", "Close-up of a single leaf touching a quiet waterhole, sending gentle concentric ink rings across the surface", "zoom_in"),
        ("Medium gazing at distant hills", "Medium shot of another stick figure lying on the grass with hands behind head, peacefully watching birds glide overhead", "pan_left"),
        ("Wide tranquil savanna stillness", "Expansive wide shot of the silent savanna afternoon, showing hours of natural stillness with zero artificial stimulation", "zoom_out"),
    ],
    "SC16": [
        ("Wide rainstorm clearing over plain", "Wide shot of dark rain clouds parting over a prehistoric valley to reveal fresh green shoots along a stream", "zoom_out"),
        ("Close-up carving stone tool", "Close-up of patient hands striking a flint core with a river cobble to shape a symmetrical hand-axe", "zoom_in"),
        ("Medium testing the sharp edge", "Medium shot of the stick figure inspecting the newly flaked stone edge against the morning light with quiet pride", "pan_right"),
        ("Close-up finished tools in row", "Close-up of three neatly crafted stone tools arranged on a flat rock, representing tangible mastery", "punch_in"),
        ("Medium standing ready for the day", "Medium shot of the stick figure rising from the boulder with alert, energized posture after the quiet morning rest", "pan_left"),
        ("Wide valley ready for exploration", "Wide panoramic frame showing the stick figure setting out across the valley with effortless natural drive", "zoom_out"),
    ],
    "SC17": [
        ("Wide twilight campfire circle", "Wide shot of a small clan of stick figures gathered around a glowing campfire under a canopy of ink-drawn stars", "zoom_out"),
        ("Close-up roasting roots and game", "Close-up of wooden skewers resting near the warm embers after a full day of foraging and walking", "zoom_in"),
        ("Medium elder gesturing story", "Medium shot of an elder stick figure using expressive hand gestures to recount the day's trek across the hills", "pan_right"),
        ("Close-up attentive listeners", "Close-up of two young stick figures leaning forward with bright eyes, completely absorbed in the spoken tale", "zoom_in"),
        ("Medium shared laughter around fire", "Medium shot of the group nodding and smiling together in warm companionship without any external distractions", "pan_left"),
        ("Wide starlit savanna harmony", "Wide pull-back of the peaceful night camp where effort, rest, and reward formed a single unbroken circle", "zoom_out"),
    ],
    "SC18": [
        ("Wide sunrise over stone monuments", "Wide transitional landscape where the open grassland gradually gives way to paved stone roads and classical columns", "zoom_out"),
        ("Medium figure walking stone road", "Medium shot of the stick figure walking along a newly laid Roman-style stone road toward a marble portico", "zoom_in"),
        ("Close-up carved marble milestone", "Close-up of a weathered stone milestone marking the transition into the classical world of cities and philosophy", "pan_right"),
        ("Low-angle classical colonnade", "Low-angle view of tall Doric columns rising against the morning sky", "zoom_in"),
        ("Medium robed philosopher waiting", "Medium shot of a stick figure in a simple classical toga standing calmly on the portico steps", "pan_left"),
        ("Wide classical courtyard vista", "Wide architectural view of an ancient Mediterranean courtyard where thinkers confronted the first wave of urban luxury", "zoom_out"),
    ],

    # ==================== CHAPTER 4: ANCIENT STOIC VOLUNTARY HARDSHIP ====================
    "SC19": [
        ("Wide ancient Roman banquet vs courtyard", "Wide architectural composition showing a noisy banquet terrace in the distance while a quiet stone study sits in the foreground", "zoom_out"),
        ("Close-up ornate goblets and garlands", "Close-up of overflowing silver goblets and fruit platters on a marble table representing urban overindulgence", "zoom_in"),
        ("Medium tired patrician figure", "Medium shot of a wealthy ancient stick figure reclining on a silk couch, looking bored and restless despite the feast", "pan_right"),
        ("Over-the-shoulder philosopher observing", "Over-the-shoulder view from a quiet colonnade as a Stoic stick figure in a plain cloak observes the restless banquet", "zoom_in"),
        ("Close-up stylus on wax tablet", "Close-up of a bronze stylus inscribing calm geometric lines onto a simple wooden wax tablet", "pan_left"),
        ("Wide quiet courtyard refuge", "Wide shot of the tranquil inner courtyard with a single olive tree and stone bench", "zoom_out"),
    ],
    "SC20": [
        ("Wide Spartan and Stoic training ground", "Wide shot of an open-air classical courtyard at dawn with a cold stone water basin and a plain wooden cot", "zoom_out"),
        ("Close-up coarse barley bread and water", "Close-up of a simple clay bowl holding a piece of dark barley bread beside a pitcher of clear water on a rough plank", "zoom_in"),
        ("Medium Stoic figure washing with cold water", "Medium shot of the robed stick figure splashing cool water from the stone basin onto their face with brisk energy", "pan_right"),
        ("Close-up thin straw mat on floor", "Close-up of a neatly rolled woven straw mat lying directly on the clean stone floor", "punch_in"),
        ("Medium writing letters at dawn", "Medium shot of the Stoic stick figure sitting upright at a simple wooden trestle table, writing earnestly by oil lamp", "pan_left"),
        ("Wide serene morning portico", "Wide pull-back showing the philosopher surrounded by spacious, uncluttered architecture and morning light", "zoom_out"),
    ],
    "SC21": [
        ("Wide classical gymnasium exercise", "Wide shot of stick figures practicing discus and running along a sanded track inside an ancient palaestra", "zoom_out"),
        ("Medium lifting heavy stone weights", "Medium shot of a stick figure lifting a pair of carved stone halteres weights with steady, disciplined posture", "zoom_in"),
        ("Close-up sand hourglass flowing", "Close-up of fine sand flowing steadily through a clear glass bulb mounted in a bronze frame", "pan_right"),
        ("Medium calm conversation under olive tree", "Medium shot of two philosopher stick figures walking slowly along a gravel path, discussing resilience", "zoom_in"),
        ("Low-angle steadfast posture in wind", "Low-angle shot of a stick figure standing firm on a windy hillside, cloak billowing while their stance remains unshaken", "pan_left"),
        ("Wide Mediterranean coastline", "Wide scenic view of rocky cliffs meeting a calm sea, symbolizing mental poise through voluntary simplicity", "zoom_out"),
    ],
    "SC22": [
        ("Wide ancient library of scrolls", "Wide shot of a classical scroll library with wooden pigeonholes holding ratusan papyrus rolls", "zoom_out"),
        ("Close-up unrolling papyrus scroll", "Close-up of stick-figure hands carefully unrolling a long papyrus manuscript filled with neat ink columns", "zoom_in"),
        ("Medium reading aloud in silence", "Medium shot of a scholar stick figure standing at a sloped wooden lectern, immersed in deep study", "pan_right"),
        ("Close-up oil lamp steady flame", "Close-up of a terracotta oil lamp burning with a steady, unwavering flame beside the lectern", "punch_in"),
        ("Medium taking thoughtful notes", "Medium shot of the scholar pausing to reflect, fingers resting lightly on chin with tranquil satisfaction", "pan_left"),
        ("Wide sunlit colonnade of wisdom", "Wide architectural pull-back showing shafts of sunlight illuminating the quiet hall of scrolls", "zoom_out"),
    ],
    "SC23": [
        ("Wide contrast of two ancient paths", "Wide editorial illustration showing a cluttered banquet hall on the left third and an airy stone study on the right third", "zoom_out"),
        ("Close-up heavy chains of indulgence", "Close-up of tangled silk ribbons wrapping around an ornate goblet, symbolizing how constant luxury breeds boredom", "zoom_in"),
        ("Medium vibrant scholar stepping out", "Medium shot of the disciplined stick figure stepping briskly out of the stone study into the fresh morning air", "pan_right"),
        ("Close-up chisel carving marble", "Close-up of an ancient sculptor's mallet and chisel striking a crisp line into white marble", "punch_in"),
        ("Medium admiring carved column", "Medium shot of the artisan stick figure stepping back to admire a tall, fluted marble column", "pan_left"),
        ("Wide classical acropolis at noon", "Wide panoramic shot of enduring stone temples built through patient, undistracted daily discipline", "zoom_out"),
    ],
    "SC24": [
        ("Wide winding road to medieval abbey", "Wide landscape showing a cobblestone path leading from classical ruins toward a quiet stone monastery in the hills", "zoom_out"),
        ("Medium traveler approaching wooden gate", "Medium shot of the stick figure walking calmly toward a heavy oak archway set in a mossy stone wall", "zoom_in"),
        ("Close-up iron ring knocker", "Close-up of a simple wrought-iron ring resting against aged oak planks", "pan_right"),
        ("Overhead cloister garden geometry", "High-angle view of a square stone cloister surrounding a symmetrical herb garden and central well", "zoom_in"),
        ("Medium entering quiet vaulted hall", "Medium shot of the stick figure stepping into a peaceful vaulted stone corridor where footsteps echo softly", "pan_left"),
        ("Wide medieval workshop courtyard", "Wide establishing view of the tranquil craft and scriptorium courtyard", "zoom_out"),
    ],

    # ==================== CHAPTER 5: MEDIEVAL SILENCE, CRAFT & FLOW ====================
    "SC25": [
        ("Wide medieval scriptorium hall", "Wide shot of a vaulted stone scriptorium where stick-figure scribes sit at angled wooden desks under high lancet windows", "zoom_out"),
        ("Close-up quill pen on vellum", "Close-up of a goose-feather quill drawing a delicate initial ornament in rich black ink on smooth parchment", "zoom_in"),
        ("Medium scribe in deep concentration", "Medium side view of a stick figure leaning over the slanted desk, completely absorbed in the rhythmic motion of the quill", "pan_right"),
        ("Close-up inkwell and brass dividers", "Close-up of a ceramic inkhorn and a pair of brass geometric dividers resting neatly beside the manuscript", "punch_in"),
        ("Medium calm stillness in hall", "Medium shot of two scribes working side by side in companionable silence as dust motes float in a sunbeam", "pan_left"),
        ("Wide illuminated hall atmosphere", "Wide pull-back showing the serene grandeur of a workspace designed entirely for single-task focus", "zoom_out"),
    ],
    "SC26": [
        ("Wide master lens-grinder workshop", "Wide shot of a Renaissance optical workshop with wooden workbenches, glass blanks, and tall arched windows", "zoom_out"),
        ("Close-up hands polishing glass lens", "Close-up of stick-figure hands rotating a curved glass lens over a brass grinding dish with rhythmic precision", "zoom_in"),
        ("Medium artisan checking light refraction", "Medium shot of the artisan stick figure holding the polished lens up to the window light, eyes bright with wonder", "pan_right"),
        ("Close-up focused beam of light", "Close-up of a crisp beam of sunlight passing through the finished lens to form a bright focal point on the workbench", "punch_in"),
        ("Medium steady posture over hours", "Medium shot of the artisan returning to the polishing wheel with unhurried, joyful absorption", "pan_left"),
        ("Wide workshop at golden hour", "Wide shot of the quiet workshop bathed in warm afternoon light, free of any external interruption", "zoom_out"),
    ],
    "SC27": [
        ("Wide Flow channel chart on parchment", "Wide editorial illustration of a diagonal corridor drawn between rising challenge on the vertical axis and skill on the horizontal axis", "zoom_out"),
        ("Close-up figure in the Flow corridor", "Close-up of a stick figure striding effortlessly along the central diagonal path where high skill meets high challenge", "zoom_in"),
        ("Medium psychologist figure explaining", "Medium shot of a scholar stick figure gesturing toward the central diagonal corridor with an open palm", "pan_right"),
        ("Close-up clock hands fading away", "Close-up of a pocket watch whose hands dissolve into soft ink swirls, symbolizing the disappearance of time awareness", "punch_in"),
        ("Medium woodcarver immersed in work", "Medium shot of a stick figure carving intricate floral patterns into an oak panel with fluid, effortless grace", "pan_left"),
        ("Wide harmonious studio of mastery", "Wide composition showing how deep challenge transforms effort into the highest form of human enjoyment", "zoom_out"),
    ],
    "SC28": [
        ("Wide cathedral stonemason yard", "Wide shot of a medieval stonecutters' yard beside a rising Gothic archway, with neatly stacked limestone blocks", "zoom_out"),
        ("Close-up compass and carpenter square", "Close-up of an iron mason's square and dividers measuring a precisely dressed cornerstone", "zoom_in"),
        ("Medium mason tapping chisel", "Medium shot of a stick-figure stonemason tapping a wooden mallet rhythmically against a stone arch keystone", "pan_right"),
        ("Low-angle vaulted arch rising", "Low-angle view looking up at the interlocking stone ribs of a high vaulted ceiling", "zoom_in"),
        ("Medium quiet pride in craftsmanship", "Medium shot of two masons standing together, brushing stone dust from their aprons while looking up at the completed arch", "pan_left"),
        ("Wide timeless cathedral silhouette", "Wide pull-back showing the soaring stone structure standing against a peaceful evening sky", "zoom_out"),
    ],
    "SC29": [
        ("Wide tranquil monastery garden walk", "Wide shot of stick figures walking slowly around a quiet cloister garden after a full day of focused craft", "zoom_out"),
        ("Close-up water trickling into stone basin", "Close-up of a clear stream of water pouring from a bronze spout into a mossy stone fountain", "zoom_in"),
        ("Medium sitting on stone bench", "Medium shot of a stick figure sitting peacefully on a garden bench, listening to the quiet evening breeze", "pan_right"),
        ("Close-up closed manuscript clasp", "Close-up of a brass clasp fastening shut on a thick leather-bound volume after the day's pages are complete", "punch_in"),
        ("Medium restful gaze at evening star", "Medium shot of the stick figure looking up at the first evening star appearing above the cloister roof", "pan_left"),
        ("Wide deep rest and renewal", "Wide shot of the silent courtyard, illustrating how protected solitude kept the mind sharp for hard tasks", "zoom_out"),
    ],
    "SC30": [
        ("Wide skyline shifting to smokestacks", "Wide transitional panorama where quiet stone rooftops give way to brick chimneys, telegraph wires, and bustling streets", "zoom_out"),
        ("Medium figure watching rotary press", "Medium shot of the stick figure standing before a large cast-iron printing press churning out stacks of penny broadsheets", "zoom_in"),
        ("Close-up spinning iron gears", "Close-up of interlocking iron gears and paper rollers moving at high mechanical speed", "pan_right"),
        ("Low-angle telegraph poles and billboards", "Low-angle shot of criss-crossing overhead wires and tall illustrated street placards", "zoom_in"),
        ("Medium hurried crowd passing by", "Medium shot of stick-figure pedestrians rushing past in bowler hats, holding folded newspapers in front of their faces", "pan_left"),
        ("Wide dawn of the attention economy", "Wide urban perspective showing the historical moment when silence began to be replaced by mass distraction", "zoom_out"),
    ],

    # ==================== CHAPTER 6: INDUSTRIAL & PACKAGED DISTRACTION ====================
    "SC31": [
        ("Wide 20th-century bustling boulevard", "Wide shot of an early twentieth-century city street lined with bright electric marquees, newsstands, and confectionery shops", "zoom_out"),
        ("Close-up sensational newspaper stack", "Close-up of bundles of illustrated broadsheets tied with twine, designed to grab the eye of every passerby", "zoom_in"),
        ("Medium commuter surrounded by posters", "Medium shot of a stick figure waiting at a tram stop, surrounded by dozens of competing placard illustrations", "pan_right"),
        ("Close-up coin dropping into slot", "Close-up of a brass coin dropping into a mechanical arcade viewer box", "punch_in"),
        ("Medium distracted walk down street", "Medium shot of the stick figure looking from one bright shop window to another, unable to settle their gaze", "pan_left"),
        ("Wide city of constant novelty", "Wide pull-back showing the urban landscape turning attention into an industrial commodity", "zoom_out"),
    ],
    "SC32": [
        ("Wide living room with glowing television", "Wide shot of a mid-century living room where a boxy cathode-ray television sits in the corner casting flickering light", "zoom_out"),
        ("Close-up channel dial clicking", "Close-up of stick-figure fingers turning a rotary channel knob endlessly in search of faster entertainment", "zoom_in"),
        ("Medium slumped on sofa for hours", "Medium side view of the stick figure sinking deep into an armchair, eyes fixed passively on the flickering glass screen", "pan_right"),
        ("Over-the-shoulder Dusty violin and books", "Over-the-shoulder view looking past the television toward a wooden bookshelf and violin case gathering dust in the corner", "zoom_in"),
        ("Low-angle hypnotic screen glow", "Low-angle shot of the flickering light washing over the passive stick figure's face in the darkened room", "pan_left"),
        ("Wide passive consumption room", "Wide composition contrasting effortless passive viewing with the quiet instruments of active creation left behind", "zoom_out"),
    ],
    "SC33": [
        ("Wide fragmented modern open office", "Wide shot of a busy open-plan office where stick figures sit at desks surrounded by floating mail envelopes and ringing bells", "zoom_out"),
        ("Close-up fractured hourglass sand", "Close-up of an hourglass broken into four tiny compartments where sand spills sideways before finishing a single cycle", "zoom_in"),
        ("Medium figure juggling five folders", "Medium shot of a stick figure trying to write in a ledger while three pop-up message cards hover around their shoulders", "pan_right"),
        ("Close-up shallow puddle vs deep well", "Editorial visual comparing a wide, ankle-deep puddle of water on pavement with a deep stone well shaft", "punch_in"),
        ("Medium rubbing forehead at desk", "Medium shot of the stick figure leaning back at the cluttered desk, exhausted from constant context switching", "pan_left"),
        ("Wide office of shallow busyness", "Wide view of the fragmented workspace where deep concentration has become a rare luxury", "zoom_out"),
    ],
    "SC34": [
        ("Wide comparison of two work habits", "Wide architectural view of a quiet timber cabin study on the right third and a noisy media lounge on the left third", "zoom_out"),
        ("Close-up frayed rope of attention", "Close-up of a braided hemp rope whose fibers are frayed and thin from being pulled in ten directions at once", "zoom_in"),
        ("Medium figure struggling with complex book", "Medium shot of a stick figure opening a thick technical volume, only to glance nervously toward a buzzing phone after ten seconds", "pan_right"),
        ("Close-up trembling compass needle", "Close-up of a compass needle spinning erratically because a small magnet is held too close to the brass casing", "punch_in"),
        ("Medium closing the book in defeat", "Medium shot of the stick figure shutting the heavy volume and reaching for the easy glowing screen instead", "pan_left"),
        ("Wide erosion of deep focus", "Wide editorial frame showing how habitual micro-entertainment weakens our tolerance for cognitively demanding work", "zoom_out"),
    ],
    "SC35": [
        ("Wide waiting line with phones", "Wide shot of five stick figures standing in a queue at a coffee counter, every single one hunched over a glowing smartphone", "zoom_out"),
        ("Close-up elevator interior", "Close-up inside a small elevator where three stick figures stare downward at their palms during a ten-second ride", "zoom_in"),
        ("Medium red traffic light pause", "Medium shot of a stick figure stopped at a pedestrian crosswalk, immediately pulling out a phone for a five-second scroll", "pan_right"),
        ("Close-up vanishing empty spaces", "Editorial diagram of a daily calendar grid where every tiny white gap between tasks is filled with dark cross-hatching", "punch_in"),
        ("Medium overloaded head posture", "Medium shot of the stick figure walking into their home at night with shoulders tense and eyes weary from nonstop input", "pan_left"),
        ("Wide city with zero quiet moments", "Wide dusk panorama of a city where every single second of waiting has been colonized by artificial stimulation", "zoom_out"),
    ],
    "SC36": [
        ("Wide university psychology corridor", "Wide shot of a clean, quiet university research corridor leading to a single white experimental room door", "zoom_out"),
        ("Medium researcher holding stopwatch", "Medium shot of a researcher stick figure in spectacles standing beside the doorway with a clipboard and brass stopwatch", "zoom_in"),
        ("Close-up basket of collected phones", "Close-up of a woven tray holding smartphones, watches, and pens surrendered by participants before entering", "pan_right"),
        ("Low-angle plain wooden door opening", "Low-angle view of the heavy wooden door swinging open to reveal a completely bare, sunlit room inside", "zoom_in"),
        ("Medium participant stepping inside", "Medium shot of a curious stick figure stepping across the threshold into the empty room", "pan_left"),
        ("Wide setup of the famous experiment", "Wide architectural view of the observation window overlooking the minimalist test chamber", "zoom_out"),
    ],

    # ==================== CHAPTER 7: THE EMPTY ROOM SHOCK EXPERIMENT & BOREDOM ====================
    "SC37": [
        ("Wide bare experimental room", "Wide shot of a completely bare room containing only one wooden chair and a small table, with a stick figure sitting alone", "zoom_out"),
        ("Close-up wall clock ticking slowly", "Close-up of a minimalist round wall clock whose minute hand moves forward by just one tiny notch toward fifteen minutes", "zoom_in"),
        ("Medium fidgeting on wooden chair", "Medium shot of the stick figure tapping their foot, crossing and uncrossing arms, uncomfortable with the total silence", "pan_right"),
        ("Close-up small box with button", "Close-up of a small rectangular metal box on the table featuring a single round button and a tiny lightning-spark emblem", "punch_in"),
        ("Medium looking at the button", "Medium shot of the stick figure staring intensely at the small metal box as the silence in the room grows heavier", "pan_left"),
        ("Wide fifteen-minute solitude test", "Wide high-angle view of the lone stick figure inside the quiet four walls", "zoom_out"),
    ],
    "SC38": [
        ("Wide observation window reaction", "Wide shot seen through the glass observation window as the seated stick figure reaches a finger toward the metal box", "zoom_out"),
        ("Close-up finger pressing shock button", "Close-up of a stick-figure index finger pressing down on the button, producing a sharp jagged ink spark at the fingertip", "punch_in"),
        ("Medium jolted posture in chair", "Medium shot of the stick figure flinching slightly from the unpleasant electric zap, yet looking oddly relieved to feel something", "pan_right"),
        ("Close-up researcher notes on clipboard", "Close-up of a researcher's chart showing a tall bar of participants who chose painful stimulation over quiet sitting", "zoom_in"),
        ("Medium pressing the button again", "Medium shot of the restless stick figure leaning forward to press the spark button a second time rather than sit in silence", "pan_left"),
        ("Wide paradox of modern boredom", "Wide editorial frame illustrating humanity's extreme aversion to fifteen minutes of unstimulated solitude", "zoom_out"),
    ],
    "SC39": [
        ("Wide transition from restlessness to calm", "Wide shot of the same bare room where a second stick figure sits back peacefully on the chair, ignoring the button box", "zoom_out"),
        ("Close-up sand settling in glass jar", "Close-up of a clear glass jar of water where swirling silt gradually settles to the bottom, leaving the water crystal clear", "zoom_in"),
        ("Medium calm eyes looking at ceiling", "Medium shot of the stick figure breathing slowly after the first five minutes of restlessness pass away", "pan_right"),
        ("Close-up constellation of ideas", "Editorial ink illustration of clean geometric star-lines connecting softly in the air above the quiet thinker", "punch_in"),
        ("Medium subtle smile of clarity", "Medium shot of the stick figure sitting upright with a relaxed, lucid expression as mental clutter clears", "pan_left"),
        ("Wide peaceful room transformation", "Wide pull-back showing the empty room transformed from a prison of boredom into a sanctuary of mental reset", "zoom_out"),
    ],
    "SC40": [
        ("Wide default mode network studio", "Wide architectural illustration of an internal archive library where tiny stick-figure librarians organize shelves during quiet hours", "zoom_out"),
        ("Close-up connecting distant threads", "Close-up of two separate ink threads being tied together into a neat weaver's knot across a drafting board", "zoom_in"),
        ("Medium walking through quiet park", "Medium shot of a stick figure strolling alone along a tree-lined park path without headphones or phone", "pan_right"),
        ("Close-up lightbulb sketch in notebook", "Close-up of a sudden creative diagram appearing on a pocket notepad after the quiet walk", "punch_in"),
        ("Medium energized stride back home", "Medium shot of the stick figure walking briskly back toward their studio, brimming with fresh ideas", "pan_left"),
        ("Wide restorative power of stillness", "Wide landscape showing how unstructured quiet time unlocks deep problem-solving and intrinsic drive", "zoom_out"),
    ],
    "SC41": [
        ("Wide dopamine baseline reset diagram", "Wide editorial chart on cream paper showing an overstimulated jagged line settling back down to a calm, fertile valley", "zoom_out"),
        ("Close-up dry sponge absorbing water", "Close-up of a dry natural sponge soaking up clear water from a shallow porcelain dish", "zoom_in"),
        ("Medium figure approaching wooden desk", "Medium shot of the stick figure walking up to a plain wooden desk after twenty minutes of quiet stillness", "pan_right"),
        ("Close-up textbook looking inviting", "Close-up of an open engineering or philosophy book whose crisp pages now glow with warm, inviting amber light", "punch_in"),
        ("Medium eager posture sitting down", "Medium shot of the stick figure pulling the chair in eagerly, excited to engage with the challenging material", "pan_left"),
        ("Wide contrast trick revealed", "Wide balanced frame showing that when boredom precedes work, hard tasks become the brain's favorite reward", "zoom_out"),
    ],
    "SC42": [
        ("Wide three archway keys on hilltop", "Wide panoramic shot of three monumental stone archways standing atop a sunlit hill, each bearing a carved geometric key emblem", "zoom_out"),
        ("Medium figure standing before arches", "Medium shot of the stick figure looking up at the three archways with confident readiness", "zoom_in"),
        ("Close-up brass key in hand", "Close-up of a finely crafted brass key resting in the stick figure's open palm", "pan_right"),
        ("Low-angle sunlit steps ascending", "Low-angle view of wide stone steps leading directly through the central archway", "zoom_in"),
        ("Medium stepping onto the first step", "Medium shot of the stick figure ascending the steps with purposeful, energetic momentum", "pan_left"),
        ("Wide vista of practical mastery", "Expansive wide shot opening into the final chapter of actionable daily protocols", "zoom_out"),
    ],

    # ==================== CHAPTER 8: 3 PROTOCOLS TO LOVE HARD THINGS ====================
    "SC43": [
        ("Wide morning bedroom without phone", "Wide shot of a sunlit bedroom at dawn where a stick figure wakes up beside an analog mechanical alarm clock", "zoom_out"),
        ("Close-up phone locked in wooden box", "Close-up of a smartphone placed neatly inside a closed wooden box on a hallway shelf far from the desk", "zoom_in"),
        ("Medium pouring warm water in silence", "Medium shot of the stick figure pouring warm water from a kettle in a quiet kitchen, enjoying the morning stillness", "pan_right"),
        ("Close-up sixty-minute golden dial", "Close-up of a clean circular clock face with the first sixty minutes shaded in calm warm ochre", "punch_in"),
        ("Medium sitting at desk with fresh mind", "Medium shot of the stick figure sitting down at the work desk at seven in the morning, opening the hardest project first", "pan_left"),
        ("Wide first-key morning sanctuary", "Wide pull-back of the sunlit study where protecting the first hour makes deep work effortless", "zoom_out"),
    ],
    "SC44": [
        ("Wide neuro-resilience training hall", "Wide editorial illustration of a stick figure standing before a series of progressively taller stone stepping blocks", "zoom_out"),
        ("Close-up stepping onto higher block", "Close-up of the stick figure stepping firmly onto a challenging stone block while a warm golden aura brightens around their posture", "zoom_in"),
        ("Medium choosing the stairs over lift", "Medium shot of the stick figure cheerfully taking a steep stone staircase instead of an idle bench", "pan_right"),
        ("Close-up growing oak sapling", "Close-up of a sturdy young oak tree thickening its trunk against a brisk mountain breeze", "punch_in"),
        ("Medium finishing an extra page", "Medium shot of the stick figure at a desk writing one extra page when tired, straightening their back with pride", "pan_left"),
        ("Wide tenacious willpower growth", "Wide composition showing how every small voluntary challenge physically strengthens the capacity for endurance", "zoom_out"),
    ],
    "SC45": [
        ("Wide craftsman desk with milestone tokens", "Wide shot of a clean wooden desk where a long project is divided into small wooden blocks and a glass jar", "zoom_out"),
        ("Close-up dropping marble into jar", "Close-up of stick-figure fingers dropping a smooth glass marble into a jar after finishing one focused chapter", "zoom_in"),
        ("Medium savoring the process", "Medium shot of the stick figure pausing to admire a newly drawn diagram, nodding with intrinsic satisfaction", "pan_right"),
        ("Close-up fountain pen gliding on paper", "Close-up of a fountain pen nib gliding smoothly across textured cream paper, celebrating the craft itself", "punch_in"),
        ("Medium stretching with a smile", "Medium shot of the stick figure taking a deep, victorious breath after a thirty-minute deep work sprint", "pan_left"),
        ("Wide self-sustaining effort loop", "Wide view of the workspace where reward is woven directly into the act of doing hard things", "zoom_out"),
    ],
    "SC46": [
        ("Wide two-minute boredom reset ritual", "Wide shot of a stick figure sitting at a desk, pushing the keyboard slightly away to sit still for two quiet minutes", "zoom_out"),
        ("Close-up hands resting on knees", "Close-up of relaxed stick-figure hands resting palms-down on knees while a small sand timer runs on the desk", "zoom_in"),
        ("Medium gazing at blank wall calmly", "Medium shot of the stick figure looking at the plain cream wall, letting the urge for distraction rise and pass away", "pan_right"),
        ("Close-up last grain of sand falling", "Close-up of the final grain of sand dropping in the two-minute glass timer", "punch_in"),
        ("Medium reaching eagerly for pen", "Medium shot of the stick figure picking up the pen with renewed vigor as the brain welcomes the task", "pan_left"),
        ("Wide quiet room of focus", "Wide pull-back showing how a brief pause of pure stillness resets focus at any hour of the day", "zoom_out"),
    ],
    "SC47": [
        ("Wide redesigned minimalist workspace", "Wide shot of an airy, clutter-free wooden desk beside a window, holding only one open notebook, one pen, and a small plant", "zoom_out"),
        ("Close-up tidy desk surface", "Close-up of the warm grain of the oak desk with zero distracting cables, badges, or flashing screens", "zoom_in"),
        ("Medium stick figure sitting with poise", "Medium shot of the stick figure sitting upright at the clean desk, shoulders relaxed and gaze steady", "pan_right"),
        ("Over-the-shoulder clear action plan", "Over-the-shoulder view of the notebook showing three clear, structured steps for the morning's most important work", "zoom_in"),
        ("Low-angle confident hand writing", "Low-angle shot of the stick figure's hand writing smoothly across the page without hesitation", "pan_left"),
        ("Wide sanctuary of deep creation", "Wide architectural frame celebrating the workspace as a launchpad for meaningful mastery", "zoom_out"),
    ],
    "SC48": [
        ("Wide morning sun filling the study", "Wide cinematic return to the morning desk from Scene 1, now bathed in warm golden sunrise light with the phone put away", "zoom_out"),
        ("Close-up pen writing fluid lines", "Close-up of the fountain pen moving effortlessly across the previously blank page, filling it with crisp ink lines", "zoom_in"),
        ("Medium serene smile of mastery", "Medium shot of the stick figure smiling calmly as they work, completely immersed in the once-difficult project", "pan_right"),
        ("Close-up finished pages stacked neatly", "Close-up of a neat stack of completed manuscript pages resting beside a warm cup of tea", "punch_in"),
        ("Medium looking out at bright horizon", "Medium shot of the stick figure glancing out the open window at a vast, clear morning sky", "pan_left"),
        ("Wide loop closure payoff", "Expansive final wide shot of the peaceful study room, holding on the quiet triumph of a mind that loves doing hard things", "zoom_out"),
    ],
}


def get_scene_beats_v2(scene_id: str, count: int = 6) -> list[tuple[str, str, str]]:
    """Return `count` visual beats (framing, description, semantic_camera) for a given scene_id."""
    base = EN_SCENE_BEATS_HARD_THINGS.get(scene_id)
    if not base:
        raise KeyError(f"Unknown scene_id in EN_SCENE_BEATS_HARD_THINGS: {scene_id}")
    if count <= len(base):
        return list(base[:count])
    result = list(base)
    extra_framings = [
        ("Detailed close-up angle", "zoom_in"),
        ("Wide editorial perspective", "zoom_out"),
        ("Side-angle tracking view", "pan_right"),
    ]
    while len(result) < count:
        idx = len(result) - len(base)
        f_label, cam = extra_framings[idx % len(extra_framings)]
        _, desc, _ = base[idx % len(base)]
        result.append((f_label, f"{desc}, alternate editorial perspective", cam))
    return result
