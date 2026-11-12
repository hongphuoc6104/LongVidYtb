"""Bespoke Explainer Prompt Mapping for chanh_niem_ke (190 new beats).

Every beat index maps to: (explainer_type, core_clause, details)
Guarantees 100% unique core subjects (b["prompt"].split(",")[1].strip()[:60].lower())
with zero template cycling and zero generic fallbacks.
"""

PREFIX = "Cinematic Wabi-Sabi & Zen Sumi-e mindfulness visual,"
SUFFIX = ", zero text overlay, no watermarks"

BESPOKE_BEATS = {
    1: (
        "OBJECT_MACRO",
        "macro close-up of solitary raindrops trickling down cold frosted windowpane",
        "subtle earth tones, sumi-e ink wash texture, tranquil natural light, crisp Full HD 1080p, serene depth of field",
    ),
    2: (
        "OBJECT_MACRO",
        "panoramic view of tranquil temple moss garden veiled in soft misty rain",
        "weathered cedar veranda, muted slate gray tones, diffused ambient morning illumination, crisp Full HD 1080p",
    ),
    4: (
        "SPLIT_COMPARISON",
        "split comparison of serene outdoor rain versus inner churning tempest storm clouds",
        "contrasting quiet garden mist on left with dark turbulent crimson squall on right, crisp Full HD 1080p",
    ),
    5: (
        "OBJECT_MACRO",
        "macro shot of rough dark granite stone pressing heavily onto worn wooden desk",
        "dense mineral texture, deep shadow beneath stone, quiet contemplative atmosphere, crisp Full HD 1080p",
    ),
    6: (
        "CAUSE_EFFECT_DIAGRAM",
        "flowchart diagram of dark black sumi ink diffusing rapidly through clear water basin",
        "macro fluid dynamics, organic tendrils of dark ink multiplying in translucent liquid, crisp Full HD 1080p",
    ),
    8: (
        "MECHANISM_CUTAWAY",
        "mechanism cutaway of brass mechanical clock gears turning endlessly without rest",
        "interlocking cogs under perpetual rotational tension, antique horological diorama, crisp Full HD 1080p",
    ),
    9: (
        "SPLIT_COMPARISON",
        "split contrast of urgent tomorrow calendar notices versus present quiet evening",
        "frantic highlighted agenda dates on left versus peaceful unwritten paper on right, crisp Full HD 1080p",
    ),
    10: (
        "OBJECT_MACRO",
        "macro focus on brittle withered autumn leaves swirling in circular water eddy",
        "decayed golden-brown foliage trapped in repetitive whirlpool current, wabi-sabi melancholy, crisp Full HD 1080p",
    ),
    11: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing restless intersecting looping brushstrokes forming mental labyrinth",
        "expressive charcoal sumi calligraphy spirals looping endlessly without exit, crisp Full HD 1080p",
    ),
    13: (
        "OBJECT_MACRO",
        "macro profile of crystal water tumbler filled to absolute meniscus brim",
        "translucent convex water dome trembling with delicate surface tension, dark ebony table, crisp Full HD 1080p",
    ),
    14: (
        "OBJECT_MACRO",
        "extreme close-up of convex water surface tension trembling like drawn bowstring",
        "refracted ambient candlelight shimmering on curved liquid membrane, dramatic macro focus, crisp Full HD 1080p",
    ),
    16: (
        "CAUSE_EFFECT_DIAGRAM",
        "cause-and-effect shot of clear water overflowing and cascading over glass rim onto dark cedar",
        "liquid spilling across polished wood grain, dynamic droplets captured in mid-motion, crisp Full HD 1080p",
    ),
    18: (
        "MECHANISM_CUTAWAY",
        "mechanism diagram illustrating overloaded human working memory capacity as an overflowing vessel",
        "subtle translucent cranial silhouette containing spilling water tumbler, cognitive overload model, crisp Full HD 1080p",
    ),
    19: (
        "OBJECT_MACRO",
        "macro close-up of an open human palm bearing imaginary heavy iron weights",
        "strained hand posture over aged wooden floorboard, invisible gravitational burden, crisp Full HD 1080p",
    ),
    20: (
        "OBJECT_MACRO",
        "delicate translucent phantom spiderwebs spun from silver thread dissolving in air",
        "fragile imaginary gossamer strands floating in dark empty space, wabi-sabi ethereal aesthetic, crisp Full HD 1080p",
    ),
    22: (
        "SPLIT_COMPARISON",
        "split contrast of tiny actual fact pebble on left beside giant looming shadow on right",
        "objective physical event pebble dwarfed by towering projected mental silhouette, crisp Full HD 1080p",
    ),
    23: (
        "OBJECT_MACRO",
        "solitary smooth river pebble sitting quietly upon plain wooden floor",
        "simple minimalist Zen composition, cool gray mineral texture, tranquil natural light, crisp Full HD 1080p",
    ),
    24: (
        "CAUSE_EFFECT_DIAGRAM",
        "flowchart of branching dark neural ink roots multiplying outward from single thought node",
        "cerebral sumi-e wash diagram illustrating runaway cognitive rumination cascades, crisp Full HD 1080p",
    ),
    26: (
        "MECHANISM_CUTAWAY",
        "primitive evolutionary brain diagram highlighting survival alert trigger system",
        "paleolithic hunter silhouette scanning shadowy brush, primal neural defense pathways, crisp Full HD 1080p",
    ),
    27: (
        "OBJECT_MACRO",
        "ancient carved stone spearhead resting alert beside glowing prehistoric campfire embers",
        "flint tool texture, warm amber ember glow, defensive sentinel vigilance, crisp Full HD 1080p",
    ),
    28: (
        "MECHANISM_CUTAWAY",
        "cutaway showing sudden sound shockwave causing human amygdala to flash bright crimson",
        "neurobiological threat reflex, acoustic concentric ripples reaching hyper-vigilant limbic core, crisp Full HD 1080p",
    ),
    30: (
        "SPLIT_COMPARISON",
        "split visual of tiny harmless rustling grass stem versus imagined towering predator silhouette",
        "magnified threat perception illusion, gentle field breeze contrasted with frightening mental projection, crisp Full HD 1080p",
    ),
    31: (
        "OBJECT_MACRO",
        "peaceful minimalist tatami room with soft paper shoji screen filtering gentle evening light",
        "uncluttered Japanese living space, woven rush mat texture, absolute domestic security, crisp Full HD 1080p",
    ),
    32: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram illustrating persistent chronic stress hormones slowly draining cellular vital energy",
        "biological hourglass graphic with vital luminescence leaking away under false alarms, crisp Full HD 1080p",
    ),
    33: (
        "OBJECT_MACRO",
        "empty tranquil cedar veranda looking out onto completely empty silent courtyard",
        "safe home sanctuary, serene raindrops dripping from eaves, complete absence of danger, crisp Full HD 1080p",
    ),
    35: (
        "OBJECT_MACRO",
        "flickering flame of brass oil lamp casting long trembling amber light against cedar wall",
        "solitary wick flame dancing in drafts, warm chiaroscuro wood grain shadows, crisp Full HD 1080p",
    ),
    36: (
        "OBJECT_MACRO",
        "exaggerated distorted shadows stretching across weathered wood planks under dim flame",
        "grotesque dancing wall phantoms born from simple innocent objects in candlelight, crisp Full HD 1080p",
    ),
    37: (
        "SPLIT_COMPARISON",
        "split comparison of dark menacing wall shadow versus harmless tiny candle wick producing it",
        "illuminating the optical illusion, phantom psychological fear versus harmless physical source, crisp Full HD 1080p",
    ),
    39: (
        "OBJECT_MACRO",
        "blank untouched calendar page for tomorrow resting peacefully on clean wooden desk",
        "pristine empty washi paper sheet, unwritten future potential free from preconceived dread, crisp Full HD 1080p",
    ),
    40: (
        "OBJECT_MACRO",
        "antique iron birdcage sitting open with door swinging gently in empty breeze",
        "rusty metal bars with wide-open portal, voluntary psychological confinement dissolved, crisp Full HD 1080p",
    ),
    41: (
        "OBJECT_MACRO",
        "burned charcoal embers of past regrets completely cold and inert upon ceramic plate",
        "extinguished ash and carbon remains, immutable history rendered harmless by acceptance, crisp Full HD 1080p",
    ),
    43: (
        "OBJECT_MACRO",
        "single unmoving drop of dew suspended from tip of fresh pine needle",
        "perfect spherical water gem, absolute stillness of present moment, morning mist, crisp Full HD 1080p",
    ),
    45: (
        "STEP_ENUMERATION",
        "ancient brush calligraphy scroll displaying philosophical wisdom inscription",
        "vertical sumi-e scroll unfurling on cedar table, classical Zen insight on human agency, crisp Full HD 1080p",
    ),
    46: (
        "MECHANISM_CUTAWAY",
        "cognitive timeline diagram marking outer external trigger event on left timeline axis",
        "stimulus node depicted as ringing iron bell sending sensory pulses along neural branch, crisp Full HD 1080p",
    ),
    47: (
        "SPLIT_COMPARISON",
        "split composition revealing luminous golden space of pause between stimulus and action",
        "Frankl psychological gap visual, radiant sacred interval separating external event from response, crisp Full HD 1080p",
    ),
    48: (
        "OBJECT_MACRO",
        "crystal prism catching single beam of light in absolute dark vacuum of silence",
        "optical clarity, concentrated pure awareness illuminating the quiet threshold of choice, crisp Full HD 1080p",
    ),
    50: (
        "OBJECT_MACRO",
        "glistening raindrop suspended delicately at edge of green mossy temple roof tile",
        "macro water droplet hanging in stillness between gathering and falling, architectural Zen detail, crisp Full HD 1080p",
    ),
    51: (
        "OBJECT_MACRO",
        "macro close-up of water droplet trembling in equilibrium just before falling",
        "surface tension hesitation on moss edge, suspended animation of natural time, crisp Full HD 1080p",
    ),
    52: (
        "OBJECT_MACRO",
        "ripples expanding in perfect circular concentric rings on dark stone water basin",
        "peaceful wave propagation across still reflective water surface, meditative geometry, crisp Full HD 1080p",
    ),
    54: (
        "OBJECT_MACRO",
        "unlocked antique brass padlock lying open on polished dark wooden surface",
        "open iron hasp, release from automatic reactive conditioning, liberating inner agency, crisp Full HD 1080p",
    ),
    55: (
        "MECHANISM_CUTAWAY",
        "mechanism diagram of mechanical clockwork automaton jerking uncontrollably on metal tracks",
        "robotic reflex archetype, unconscious impulsive response triggered by external string tug, crisp Full HD 1080p",
    ),
    56: (
        "MECHANISM_CUTAWAY",
        "rigid copper gears engaging instantly without cognitive filter or deliberation",
        "meshing toothed wheels driving reactive behavior blindly, mechanical determinism diorama, crisp Full HD 1080p",
    ),
    57: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing reactive spark striking dry straw and igniting immediate red flames",
        "rapid emotional combustion cycle, unexamined anger flaring into destructive blaze, crisp Full HD 1080p",
    ),
    59: (
        "SPLIT_COMPARISON",
        "split comparison of sharp angry words clashing like crossing iron blades in mid-air",
        "verbal retaliation battle on left versus calm silent shield absorbing force on right, crisp Full HD 1080p",
    ),
    60: (
        "OBJECT_MACRO",
        "wooden marionette puppet with tangled strings being pulled by invisible external hands",
        "carved doll dangling helplessly, vulnerability to manipulative external provocation, crisp Full HD 1080p",
    ),
    61: (
        "OBJECT_MACRO",
        "bamboo water rocker shishi-odoshi slowly filling with mountain stream trickle",
        "zen garden acoustic water dropper balancing steadily before purposeful release, crisp Full HD 1080p",
    ),
    63: (
        "SPLIT_COMPARISON",
        "split perspective showing practitioner stepping back one pace to observe emotional tide",
        "subject stepping out of raging river current onto dry firm riverbank boulder, crisp Full HD 1080p",
    ),
    65: (
        "OBJECT_MACRO",
        "glowing red wood ember fading peacefully into soft gray ash without burning timber",
        "deprived of reactive oxygen, destructive wrath cooling into inert harmless dust, crisp Full HD 1080p",
    ),
    66: (
        "OBJECT_MACRO",
        "clear optical crystal lens revealing crisp focused details of distant landscape",
        "magnifying glass bringing obscured truth into sharp lucidity, calm discernment, crisp Full HD 1080p",
    ),
    68: (
        "SPLIT_COMPARISON",
        "split visual of jagged path carved by anger versus smooth stones laid by wise calm",
        "scorched earth ruin on left versus harmonious blossoming garden pathway on right, crisp Full HD 1080p",
    ),
    69: (
        "OBJECT_MACRO",
        "soaring solitary crane flying freely across wide golden dawn horizon above mist",
        "unfettered flight, soaring spiritual autonomy inviolable by outside judgment, crisp Full HD 1080p",
    ),
    71: (
        "OBJECT_MACRO",
        "precise combed rake lines in zen dry landscape rock garden under soft morning light",
        "rippling gravel patterns in Ryoanji temple sand garden, pristine harmonious order, crisp Full HD 1080p",
    ),
    72: (
        "OBJECT_MACRO",
        "human hand reaching down to scoop handful of fine white quartz sand from garden",
        "tactile contact with mineral grains, grasping impulse disturbing the raked calm, crisp Full HD 1080p",
    ),
    73: (
        "OBJECT_MACRO",
        "macro close-up of white knuckles clenching tightly around dry quartz sand",
        "muscular tension in gripping fist, forceful psychological control posture, crisp Full HD 1080p",
    ),
    75: (
        "OBJECT_MACRO",
        "fine white sand trickling like liquid hourglass stream between tightly clenched fingers",
        "sand grains escaping lateral gaps between fingers, futility of desperate grasping, crisp Full HD 1080p",
    ),
    76: (
        "CAUSE_EFFECT_DIAGRAM",
        "cause-and-effect comparison of gripping force versus rate of sand escaping fingers",
        "diagrammatic curves proving higher compressive tension accelerates resource loss, crisp Full HD 1080p",
    ),
    77: (
        "OBJECT_MACRO",
        "empty cupped hand dusted with only faint trace of chalky dry sand residue",
        "bare unfulfilled palm following exhausting exertion, visual metaphor for over-control, crisp Full HD 1080p",
    ),
    79: (
        "SPLIT_COMPARISON",
        "split comparison of trying to grasp flowing wind versus letting words disperse into air",
        "fist clutching empty air on left versus open palm letting breeze pass through freely, crisp Full HD 1080p",
    ),
    80: (
        "OBJECT_MACRO",
        "winding mountain path splitting into three misty directions among pine trees",
        "uncontrollable future bifurcations shrouded in natural fog, humility before destiny, crisp Full HD 1080p",
    ),
    81: (
        "OBJECT_MACRO",
        "wild mountain river naturally carving its own curved course around immovable boulder",
        "unforced Taoist water flow, yielding around solid obstacle without conflict, crisp Full HD 1080p",
    ),
    83: (
        "OBJECT_MACRO",
        "fragile ceramic plate piled dangerously high with too many heavy river stones",
        "excessive burden tipping delicate balance, psychological micro-management strain, crisp Full HD 1080p",
    ),
    84: (
        "OBJECT_MACRO",
        "rigid iron clamp locked tightly onto delicate wooden sculpture threatening to crack it",
        "inflexible expectation crushing organic beauty, forceful imposition of will, crisp Full HD 1080p",
    ),
    85: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing rigid expectation snapping under weight of unpredictable real events",
        "stress analysis graphic illustrating fracture point of unyielding mental assumptions, crisp Full HD 1080p",
    ),
    86: (
        "OBJECT_MACRO",
        "taut frayed rope strand under excessive mechanical strain ready to unravel",
        "individual hemp fibers tearing under prolonged tension, chronic anxiety fatigue, crisp Full HD 1080p",
    ),
    88: (
        "OBJECT_MACRO",
        "relaxed open human hand resting palm upward upon smooth cool cedar floorboard",
        "curved gentle fingers without grasping tension, wabi-sabi serene posture of surrender, crisp Full HD 1080p",
    ),
    90: (
        "OBJECT_MACRO",
        "mound of fine river sand resting peacefully undisturbed on wide flat open palm",
        "unclenched hand cradling intact grains, equilibrium achieved through releasing grip, crisp Full HD 1080p",
    ),
    91: (
        "OBJECT_MACRO",
        "intact pyramid of golden sand grains resting calmly without a single grain falling",
        "complete retention through radical stillness, non-coercive peaceful coexistence, crisp Full HD 1080p",
    ),
    93: (
        "SPLIT_COMPARISON",
        "split comparison of exhausting futile battle against waves versus resting serenely on shore",
        "swimmer flailing against rip current on left versus resting safely on warm sand dune, crisp Full HD 1080p",
    ),
    94: (
        "OBJECT_MACRO",
        "hand gently opening to release captive songbird into broad blue sky",
        "liberating gesture, releasing possessive demand granting absolute freedom to both, crisp Full HD 1080p",
    ),
    96: (
        "OBJECT_MACRO",
        "pure clear mountain brook flowing effortlessly over smooth moss-covered river rocks",
        "unimpeded liquid fluidity, natural harmony without resistance or stagnation, crisp Full HD 1080p",
    ),
    97: (
        "OBJECT_MACRO",
        "white egret feather drifting weightlessly downward onto mirror surface of pond",
        "zero resistance descent, landing softly without generating splashes or disruption, crisp Full HD 1080p",
    ),
    99: (
        "OBJECT_MACRO",
        "slender sandalwood incense stick smoldering in dark bronze burner on low table",
        "delicate glowing ember tip, aromatic amber atmosphere in quiet tea room, crisp Full HD 1080p",
    ),
    100: (
        "OBJECT_MACRO",
        "delicate ribbon of fragrant white smoke curving in tranquil serpentine patterns",
        "unhurried fluid smoke currents dancing slowly through peaceful sunlit air, crisp Full HD 1080p",
    ),
    101: (
        "OBJECT_MACRO",
        "straight vertical smoke column rising steadily in completely still draft-free room",
        "unwavering focus, pure centered stability rising directly toward ceiling timber, crisp Full HD 1080p",
    ),
    102: (
        "OBJECT_MACRO",
        "solitary dark stone lantern surrounded by fallen autumn maple leaves in silence",
        "aged granite lantern standing eternal amidst impermanent red foliage, crisp Full HD 1080p",
    ),
    104: (
        "OBJECT_MACRO",
        "heavy wrought iron ship anchor resting securely on firm harbor seabed bedrock",
        "thick marine chain extending upward, steadfast stability against surging tidal currents, crisp Full HD 1080p",
    ),
    105: (
        "MECHANISM_CUTAWAY",
        "anatomical cutaway of ribcage gently expanding and contracting with rhythmic inhalation",
        "luminous breath mechanics, diaphragm moving rhythmically like ocean tide, crisp Full HD 1080p",
    ),
    106: (
        "MECHANISM_CUTAWAY",
        "visual flow diagram of cool air entering nasal passages and warming deep into diaphragm",
        "golden breath streamline descending along spine to root center, grounding awareness, crisp Full HD 1080p",
    ),
    108: (
        "OBJECT_MACRO",
        "tangled ball of dark yarn unrolling endlessly across bare tatami mat floor",
        "messy thought spirals scattering randomly, wandering mind detached from physical body, crisp Full HD 1080p",
    ),
    109: (
        "OBJECT_MACRO",
        "chest silhouette slowly lifting in gentle deep inhalation in warm morning light",
        "conscious respiration posture, serene profile of mindful practitioner seated tall, crisp Full HD 1080p",
    ),
    110: (
        "MECHANISM_CUTAWAY",
        "luminous azure air stream filling bronchial tree with refreshing oxygenation",
        "vital prana revitalizing lung lobes, cool blue light washing away nervous tension, crisp Full HD 1080p",
    ),
    112: (
        "MECHANISM_CUTAWAY",
        "microscopic view of glowing red blood cells absorbing fresh oxygen molecules",
        "cellular respiration diorama, cellular revitalizing nourish flowing through capillaries, crisp Full HD 1080p",
    ),
    113: (
        "MECHANISM_CUTAWAY",
        "medical pulse waveform leveling from rapid jagged spikes into slow gentle sine waves",
        "heart rate variability calming, physiological shift to parasympathetic rest, crisp Full HD 1080p",
    ),
    114: (
        "OBJECT_MACRO",
        "macro close-up of relaxed hands and loose supple wrists resting naturally on linen cloth",
        "subtle earth tones, sumi-e ink wash texture, tranquil natural light, crisp Full HD 1080p",
    ),
    116: (
        "OBJECT_MACRO",
        "warm breath condensing into soft gentle vapor and vanishing into crisp evening air",
        "visible exhalation dissipating effortlessly, releasing accumulated mental burdens, crisp Full HD 1080p",
    ),
    117: (
        "MECHANISM_CUTAWAY",
        "neurobiological cutaway showing parasympathetic vagus activation restoring cellular equilibrium",
        "glowing blue autonomic neural pathways calming systemic heart rhythm, crisp Full HD 1080p",
    ),
    118: (
        "SPLIT_COMPARISON",
        "split comparison of distant abstract mind labyrinth versus grounded physical breath here",
        "foggy imaginary worries on left versus crisp tangible air entering nostrils on right, crisp Full HD 1080p",
    ),
    120: (
        "OBJECT_MACRO",
        "warm glowing hearth fire welcoming a traveler returning to rustic timber home",
        "interior sanctum, amber fireplace embers casting peaceful light across floor, crisp Full HD 1080p",
    ),
    121: (
        "STEP_ENUMERATION",
        "timeline diorama tracking human breath from first newborn cry to wise elder tranquility",
        "unbroken golden thread of breath weaving through every season of human lifetime, crisp Full HD 1080p",
    ),
    123: (
        "OBJECT_MACRO",
        "steady gentle pulse of glowing heart lamp shining steadily inside storm lantern",
        "protected interior flame shielded by glass from driving rain, unshakeable vitality, crisp Full HD 1080p",
    ),
    124: (
        "OBJECT_MACRO",
        "gentle mindful attention focused on subtle air currents passing through nostrils",
        "luminous microscopic air stream, meditative sensory grounding, quiet room, crisp Full HD 1080p",
    ),
    125: (
        "OBJECT_MACRO",
        "stout hemp mooring rope securely tied in cleat hitch holding boat steady in harbor",
        "secure nautical hitch, grounding anchor line preventing vessel from drifting, crisp Full HD 1080p",
    ),
    127: (
        "OBJECT_MACRO",
        "sturdy nautical anchor resting steadily on seabed resisting swirling underwater currents",
        "heavy iron flukes embedded in stone bedrock, unwavering emotional stability, crisp Full HD 1080p",
    ),
    128: (
        "SPLIT_COMPARISON",
        "split comparison of false concept of surrender as broken weapon versus true acceptance",
        "shattered sword of defeat on left versus enlightened sage welcoming reality on right, crisp Full HD 1080p",
    ),
    130: (
        "OBJECT_MACRO",
        "iron shackle lying rusted and snapped open in mountain soil under blooming clover",
        "broken bond of fatalism, active freedom blossoming from conscious understanding, crisp Full HD 1080p",
    ),
    131: (
        "SPLIT_COMPARISON",
        "split comparison of deep roots of existential insecurity versus clear light of awareness",
        "tangled shadowy underground briars on left contrasted with lucid sunbeam on right, crisp Full HD 1080p",
    ),
    132: (
        "OBJECT_MACRO",
        "proud unbent oak tree standing tall with roots firmly planted in rocky hillside soil",
        "stoic botanical resilience, confronting weather elements with majestic dignity, crisp Full HD 1080p",
    ),
    133: (
        "OBJECT_MACRO",
        "unflinching eyes reflected in polished bronze mirror facing reality without distortion",
        "lucid self-honesty, gazing directly into facts without fear or embellishment, crisp Full HD 1080p",
    ),
    135: (
        "SPLIT_COMPARISON",
        "split contrast of unrealistic demand for universal praise versus quiet acceptance of reality",
        "fragile porcelain expectations shattering on left versus resilient stone patio on right, crisp Full HD 1080p",
    ),
    136: (
        "OBJECT_MACRO",
        "rugged mountain contour map showing winding elevations and deep natural valleys",
        "topographical truth of existence, life as undulating landscape rather than flat board, crisp Full HD 1080p",
    ),
    137: (
        "OBJECT_MACRO",
        "swirling river currents dancing around granite boulders in perpetual fluid motion",
        "Heraclitean flux, dynamic living water constantly reshaping its channel, crisp Full HD 1080p",
    ),
    138: (
        "OBJECT_MACRO",
        "unpredictable rain shower falling over sunny meadow creating simultaneous rainbow mist",
        "capricious nature of external weather, coexistence of sun and rain without complaint, crisp Full HD 1080p",
    ),
    140: (
        "OBJECT_MACRO",
        "drained clay oil lamp with dying ember wick resting beside dry earthen jug",
        "depleted reserves from fighting uncontrollable reality, visual exhaustion metaphor, crisp Full HD 1080p",
    ),
    141: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing internal friction and emotional resistance sapping vital energy battery",
        "mechanic cutaway revealing how mental resistance creates intense thermal drain, crisp Full HD 1080p",
    ),
    142: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram of the Buddhist two arrows: first arrow of event plus second arrow of mental resistance",
        "first iron arrow of physical event beside painful second arrow self-inflicted by anger, crisp Full HD 1080p",
    ),
    144: (
        "OBJECT_MACRO",
        "slender flexible bamboo stalk bending gracefully low before roaring mountain wind",
        "yielding wisdom of nature, supple green stalk bowing to earth under storm gust, crisp Full HD 1080p",
    ),
    145: (
        "OBJECT_MACRO",
        "curved green bamboo stem yielding fluidly to heavy gust without splintering",
        "biomechanical elasticity, hollow culm redistributing stress effortlessly, crisp Full HD 1080p",
    ),
    146: (
        "OBJECT_MACRO",
        "noble warrior standing upright and calm facing raw truth without defensive shield",
        "serene stoic posture, dignified acceptance of factual reality in open field, crisp Full HD 1080p",
    ),
    147: (
        "OBJECT_MACRO",
        "resilient bamboo springing upright to vertical position after storm passes unharmed",
        "instant post-crisis recovery, pristine bamboo grove standing tall in sunlight, crisp Full HD 1080p",
    ),
    149: (
        "OBJECT_MACRO",
        "persistent icy winter rain falling steadily on dark slate courtyard stone tiles",
        "cold puddles reflecting dreary sky, melancholic atmospheric wabi-sabi stillness, crisp Full HD 1080p",
    ),
    150: (
        "OBJECT_MACRO",
        "deep taproot of pine tree gripping bedrock tightly beneath mountain soil surface",
        "subterranean anchorage, unshakable core strength allowing branches to sway freely, crisp Full HD 1080p",
    ),
    151: (
        "SPLIT_COMPARISON",
        "split comparison of futile punching against stone wall versus pivoting to open gate",
        "bruised fists against rock on left versus serene figure walking through open archway, crisp Full HD 1080p",
    ),
    153: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing instantaneous evaporation of mental burden when gripping hands release",
        "heavy iron weight dissolving into weightless steam as palms unclench, crisp Full HD 1080p",
    ),
    154: (
        "CAUSE_EFFECT_DIAGRAM",
        "formula breakdown showing: Suffering equals Pain multiplied by Resistance",
        "mathematical mindfulness equation inscribed with sumi ink on textured washi parchment, crisp Full HD 1080p",
    ),
    156: (
        "CAUSE_EFFECT_DIAGRAM",
        "flowchart showing immediate drop in mental suffering when resistance factor drops to zero",
        "suffering graph plunging to baseline as acceptance unlocks mental peace, crisp Full HD 1080p",
    ),
    157: (
        "OBJECT_MACRO",
        "isolated sensory nerve signal traveling smoothly along spinal cord without emotional panic",
        "pure physical sensation stripped of cognitive catastrophic narrative overlay, crisp Full HD 1080p",
    ),
    159: (
        "SPLIT_COMPARISON",
        "split visual of dropping heavy iron shield versus stepping forward with open hands",
        "wearisome defensive posture abandoned in favor of courageous openhearted engagement, crisp Full HD 1080p",
    ),
    160: (
        "OBJECT_MACRO",
        "wooden boat drifting effortlessly downriver guided by natural river current",
        "effortless navigation, oars resting quietly while river flow carries craft forward, crisp Full HD 1080p",
    ),
    162: (
        "OBJECT_MACRO",
        "modern black smartphone left behind on wooden entryway console table",
        "blank dark screen, deliberate technological detachment for mindful walking journey, crisp Full HD 1080p",
    ),
    163: (
        "SPLIT_COMPARISON",
        "split contrast of rigid factory assembly line footsteps versus natural barefoot earth walking",
        "regimented industrial pacing on left versus organic contact with forest soil on right, crisp Full HD 1080p",
    ),
    164: (
        "OBJECT_MACRO",
        "mechanical pedometer displaying glowing step counter digits under harsh fluorescent light",
        "quantified life metrics turning simple movement into stressful performance target, crisp Full HD 1080p",
    ),
    165: (
        "OBJECT_MACRO",
        "digital fitness tracker watch showing sterile heart rate metrics and target graphs",
        "cold pixelated notifications dissecting natural biological rhythms into numbers, crisp Full HD 1080p",
    ),
    167: (
        "OBJECT_MACRO",
        "visual representation of noisy sound spikes and cacophony of overlapping car horns",
        "aggressive urban acoustic waveform clutter piercing mental tranquility, crisp Full HD 1080p",
    ),
    168: (
        "OBJECT_MACRO",
        "bare feet hovering above cold synthetic asphalt detached from living earth",
        "alienation from nature, synthetic soles insulating human body from grounding soil, crisp Full HD 1080p",
    ),
    169: (
        "OBJECT_MACRO",
        "rustic wooden sandals stepping gently onto damp moss-covered flagstone pathway",
        "grounded stride, tactile connection between cedar geta footwear and living moss, crisp Full HD 1080p",
    ),
    171: (
        "OBJECT_MACRO",
        "ancient granite stepping stones lined with lush emerald moss winding through cedar grove",
        "timeless stone trail curving gently under towering ancient cryptomeria trees, crisp Full HD 1080p",
    ),
    172: (
        "OBJECT_MACRO",
        "macro focus on crystalline morning dewdrop resting on tender green bamboo shoot",
        "pristine botanical purity, sparkling water bead catching first rays of forest dawn, crisp Full HD 1080p",
    ),
    173: (
        "OBJECT_MACRO",
        "bamboo canopy whispering softly in breeze with dappled golden sunbeams dancing through leaves",
        "serene natural symphony, emerald foliage swaying gently in mountain forest wind, crisp Full HD 1080p",
    ),
    174: (
        "OBJECT_MACRO",
        "cool forest mist brushing against skin of walking practitioner in quiet woods",
        "tactile sensory awakening, crisp refreshing mountain vapor awakening sensory presence, crisp Full HD 1080p",
    ),
    176: (
        "OBJECT_MACRO",
        "complex math chalkboard formula slowly dissolving like fog into clear mountain air",
        "intellectual problems dissolving, mental burden evaporating into forest spaciousness, crisp Full HD 1080p",
    ),
    177: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing forest phytoncides lowering cortisol levels in human bloodstream",
        "botanical healing chemistry, pine aerosols restoring autonomic nervous balance, crisp Full HD 1080p",
    ),
    178: (
        "OBJECT_MACRO",
        "wilted green fern frond slowly unfurling and rejuvenating in fresh rainwater",
        "botanical restoration, revitalized cells drinking mountain moisture with deep relief, crisp Full HD 1080p",
    ),
    180: (
        "OBJECT_MACRO",
        "antique ceramic tea bowl with prominent gleaming veins of pure gold kintsugi lacquer",
        "japanese kintsukuroi art, fractures celebrated with shimmering twenty-four karat gold lines, crisp Full HD 1080p",
    ),
    181: (
        "SPLIT_COMPARISON",
        "split comparison of ordinary plain bowl versus kintsugi bowl made precious by its scars",
        "generic factory dish on left versus unique historical masterwork bowl on right, crisp Full HD 1080p",
    ),
    182: (
        "OBJECT_MACRO",
        "golden kintsugi seam reflecting candlelight with timeless character and poise",
        "luminous lacquer seam, scars transformed into the most captivating feature of the vessel, crisp Full HD 1080p",
    ),
    184: (
        "OBJECT_MACRO",
        "close-up of weathered wooden temple pillar bearing historic marks of ancient storms",
        "deep wood fissures, dignified aging showing survival through centuries of trials, crisp Full HD 1080p",
    ),
    185: (
        "OBJECT_MACRO",
        "rough handmade pottery bowl bearing maker thumbprint preserved in hardened glaze",
        "wabi-sabi authenticity, human imperfection celebrated as authentic soulful touch, crisp Full HD 1080p",
    ),
    187: (
        "OBJECT_MACRO",
        "pair of caring hands gently holding fractured ceramic shard with deep reverence",
        "compassionate embrace, holding wounded parts with tenderness rather than condemnation, crisp Full HD 1080p",
    ),
    188: (
        "OBJECT_MACRO",
        "soft golden lacquer brush delicately filling fissure with compassion and care",
        "healing restorative craft, golden urushi resin binding broken edges with honor, crisp Full HD 1080p",
    ),
    190: (
        "OBJECT_MACRO",
        "solitary silhouette strolling aimlessly along winding meadow path under pink sunset",
        "unhurried pace without itinerary, walking purely to experience the act of walking, crisp Full HD 1080p",
    ),
    191: (
        "OBJECT_MACRO",
        "white dandelion seeds dispersing weightlessly across open twilight sky",
        "airy liberation, thoughts floating freely without attachment across sunset expanse, crisp Full HD 1080p",
    ),
    193: (
        "SPLIT_COMPARISON",
        "split visual of remote icy Himalayan hermitage peak versus humble kitchen cutting board",
        "exotic ascetic isolation on left versus sacred ordinary mindfulness in everyday kitchen, crisp Full HD 1080p",
    ),
    194: (
        "OBJECT_MACRO",
        "pair of hands washing fresh green vegetables in wooden tub of well water",
        "clear droplets splashing off crisp lettuce leaves, humble domestic mindfulness, crisp Full HD 1080p",
    ),
    195: (
        "OBJECT_MACRO",
        "focused gaze watching single drop of green matcha tea drip from bamboo whisk",
        "chanoyu tea ceremony precision, total absorption in singular present movement, crisp Full HD 1080p",
    ),
    197: (
        "SPLIT_COMPARISON",
        "split contrast of chaotic disorganized workspace reflecting restless cluttered mind",
        "disheveled papers mirroring scattered thoughts on left versus clean serenity on right, crisp Full HD 1080p",
    ),
    198: (
        "OBJECT_MACRO",
        "dark desk surface buried under unorganized documents tangled cables and crumpled notes",
        "visual chaotic noise, overwhelming cognitive friction draining mental stamina, crisp Full HD 1080p",
    ),
    199: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing visual clutter acting as multiple micro-distractions draining cognitive focus",
        "scattered red alert rays from messy objects bombarding human visual cortex, crisp Full HD 1080p",
    ),
    200: (
        "OBJECT_MACRO",
        "tired eyes rubbing bridge of nose beside messy heap of unsorted paperwork",
        "sensory exhaustion, physical strain from environmental visual disorder, crisp Full HD 1080p",
    ),
    202: (
        "OBJECT_MACRO",
        "hands neatly folding thick linen blanket into crisp squared corners on woven mat",
        "deliberate domestic care, crisp folded edge restoring immediate geometric calm, crisp Full HD 1080p",
    ),
    203: (
        "OBJECT_MACRO",
        "damp cotton cloth wiping single streak of dust off dark polished walnut tabletop",
        "purifying sweep, glossy reflection emerging beneath simple mindful cleaning stroke, crisp Full HD 1080p",
    ),
    205: (
        "OBJECT_MACRO",
        "clear mountain tap water flowing gently over cupped human hands in ceramic sink",
        "refreshing temperature sensation, water cascading over skin in quiet morning kitchen, crisp Full HD 1080p",
    ),
    206: (
        "OBJECT_MACRO",
        "iridescent soap bubbles glistening on ceramic dish under soft morning kitchen window",
        "delicate rainbow reflections on white suds, beauty discovered in mundane dishwashing, crisp Full HD 1080p",
    ),
    208: (
        "OBJECT_MACRO",
        "steam rising from handcrafted ceramic cup of freshly whisked bitter ceremonial matcha",
        "emerald froth texture, earthy aroma curling in quiet contemplative morning light, crisp Full HD 1080p",
    ),
    209: (
        "MECHANISM_CUTAWAY",
        "flavor sensory mapping diagram illustrating transition from bitter tannin to sweet finish",
        "tastebud receptor pathways, mindful degustation tracing lingering sweetness in throat, crisp Full HD 1080p",
    ),
    211: (
        "OBJECT_MACRO",
        "single bamboo chopsticks placing one pickled plum precisely in center of rice bowl",
        "single-pointed attention, exquisite reverence applied to the simplest breakfast meal, crisp Full HD 1080p",
    ),
    212: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing tactile sensory focus breaking cycle of wandering speculative thoughts",
        "direct sensory neural circuit overriding default mode network rumination loop, crisp Full HD 1080p",
    ),
    214: (
        "OBJECT_MACRO",
        "fine dark tea grounds settling quietly to bottom of glazed ceramic teacup",
        "turbid water clearing naturally without stirring, peaceful gravitation of thoughts, crisp Full HD 1080p",
    ),
    215: (
        "OBJECT_MACRO",
        "crystal clear tea liquor resting above still settled sediment at cup bottom",
        "perfect clarity achieved through patience, undisturbed stillness revealing transparency, crisp Full HD 1080p",
    ),
    217: (
        "OBJECT_MACRO",
        "empty peaceful room flooded with warm morning sunlight across clean wooden floor",
        "spacious tranquility, dust-free floorboards glowing warmly in radiant morning dawn, crisp Full HD 1080p",
    ),
    218: (
        "OBJECT_MACRO",
        "minimalist zen room with sliding shoji doors pushed wide open to endless horizon",
        "unobstructed view of misty mountains, physical spaciousness expanding mental horizon, crisp Full HD 1080p",
    ),
    219: (
        "OBJECT_MACRO",
        "vast calm lake reflecting unbroken sky without a single ripple or cloud",
        "mirror-like water surface, tranquil consciousness reflecting universe with equanimity, crisp Full HD 1080p",
    ),
    221: (
        "OBJECT_MACRO",
        "dense charcoal storm clouds rolling swiftly across mountain pass blocking sunlight",
        "looming meteorological pressure, sudden intrusive anxiety gathering on mental horizon, crisp Full HD 1080p",
    ),
    222: (
        "OBJECT_MACRO",
        "bronze bell striker pausing in mid-air one millimeter before contacting temple bell",
        "suspended tension, intentional deep breath breaking reflexive panic cascade, crisp Full HD 1080p",
    ),
    223: (
        "STEP_ENUMERATION",
        "three numbered wooden inquiry tablets hanging side by side in quiet monastery alcove",
        "carved cedar plaques displaying the three grounding questions of mindfulness inquiry, crisp Full HD 1080p",
    ),
    225: (
        "STEP_ENUMERATION",
        "inscribed tablet one with question: Is this circumstance within my sphere of control?",
        "calligraphy brush strokes on cedar plaque illuminated by warm lantern light, crisp Full HD 1080p",
    ),
    226: (
        "SPLIT_COMPARISON",
        "split comparison of immovable giant mountain cliff versus futile attempt to push it",
        "unyielding tectonic granite face contrasted with foolish human strain, crisp Full HD 1080p",
    ),
    227: (
        "OBJECT_MACRO",
        "raging thundercloud unmoved by human shouting from distant valley floor",
        "indifference of cosmic elements, worry powerless to alter lightning trajectory, crisp Full HD 1080p",
    ),
    228: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing self-directed rumination overheating neural circuits without external effect",
        "closed thermal loop burning away emotional stamina with zero real-world leverage, crisp Full HD 1080p",
    ),
    230: (
        "STEP_ENUMERATION",
        "inscribed tablet two with question: Will this event matter in five years?",
        "second carved cedar plaque illuminated by warm lantern light, temporal perspective shift, crisp Full HD 1080p",
    ),
    231: (
        "OBJECT_MACRO",
        "single microscopic dust speck illuminated in diagonal sunlight beam before fading away",
        "cosmic scale perspective, present crisis shrinking to ephemeral floating particle, crisp Full HD 1080p",
    ),
    232: (
        "OBJECT_MACRO",
        "relentless ocean waves smoothing rough footprints on sandy beach into flat perfection",
        "inevitable tide of time washing away temporary marks, restorative natural oblivion, crisp Full HD 1080p",
    ),
    234: (
        "STEP_ENUMERATION",
        "inscribed tablet three with question: What is the single smallest action I can take now?",
        "third carved cedar plaque illuminated by warm lantern light, micro-action mandate, crisp Full HD 1080p",
    ),
    235: (
        "SPLIT_COMPARISON",
        "split comparison of passive paralyzed daydreaming monster versus taking one tiny step forward",
        "monstrous shadow of rumination on left versus practical single step on flagstone on right, crisp Full HD 1080p",
    ),
    236: (
        "SITUATIONAL_ACTION",
        "practitioner standing up decisively from chair and stretching arms toward morning sky",
        "kinesthetic physical movement breaking mental paralysis, purposeful embodied action, crisp Full HD 1080p",
    ),
    238: (
        "OBJECT_MACRO",
        "ink pen tip writing concrete worry words onto small square of coarse washi paper",
        "tactile externalization, abstract terror committed to ink on paper making it manageable, crisp Full HD 1080p",
    ),
    239: (
        "OBJECT_MACRO",
        "pen resting flat on desk beside paper showing worry externalized and separated from self",
        "spatial separation between thinker and written thought, objective emotional distance, crisp Full HD 1080p",
    ),
    241: (
        "OBJECT_MACRO",
        "single small oil lamp beam instantly dispelling monstrous room shadows",
        "luminescent clarity triumphing over darkness, phantom terrors vanishing before factual light, crisp Full HD 1080p",
    ),
    242: (
        "OBJECT_MACRO",
        "sturdy stone column base standing unshakeable on solid granite foundation",
        "unwavering structural stability, mental foundation rooted in objective reality, crisp Full HD 1080p",
    ),
    244: (
        "STEP_ENUMERATION",
        "three polished river stones inscribed with gratitude tokens resting on cedar coaster",
        "smooth pebbles marked with symbols of family health and simple shelter, crisp Full HD 1080p",
    ),
    245: (
        "OBJECT_MACRO",
        "bubbling freshwater mountain spring emerging crystal clear from mossy rock cleft",
        "inexhaustible fountain of gratitude bubbling up through cool mossy granite fissures, crisp Full HD 1080p",
    ),
    246: (
        "OBJECT_MACRO",
        "tender green seed germinating and sending vibrant white root into moist dark earth",
        "budding peace, gratitude nurturing organic inner growth in fertile heart soil, crisp Full HD 1080p",
    ),
    248: (
        "SPLIT_COMPARISON",
        "split comparison of hectic noisy city intersection versus quiet inner sanctum within chest",
        "crowded traffic blur on left versus unmoving tranquil lantern chamber inside on right, crisp Full HD 1080p",
    ),
    249: (
        "OBJECT_MACRO",
        "heavy iron weights suspended by invisible cords hovering above empty tabletop",
        "ephemeral nature of societal pressures, perceived burdens suspended without touching ground, crisp Full HD 1080p",
    ),
    250: (
        "OBJECT_MACRO",
        "weary traveler walking boots resting beside welcoming hearth fire in quiet lodge",
        "journey pause, resting tired feet after long passage, welcoming shelter, crisp Full HD 1080p",
    ),
    251: (
        "OBJECT_MACRO",
        "warm glowing doorway of home beaconing through twilight mist to returning traveler",
        "amber doorway inviting return, soul finding its original peaceful dwelling place, crisp Full HD 1080p",
    ),
    253: (
        "OBJECT_MACRO",
        "impenetrable inner stone sanctuary keeping candle flame burning completely still in storm",
        "sacred inner fortress, exterior squalls unable to flicker the quiet interior light, crisp Full HD 1080p",
    ),
    254: (
        "OBJECT_MACRO",
        "serene mountain lake mirror reflecting pristine snow peak without single ripple",
        "unbroken equanimity, pristine water surface holding mountain reflection in timeless peace, crisp Full HD 1080p",
    ),
    256: (
        "OBJECT_MACRO",
        "practitioner hands resting peacefully in lap in dhyana mudra with serene posture",
        "harmonious meditation mudra, thumb tips touching gently forming circle of wholeness, crisp Full HD 1080p",
    ),
    258: (
        "OBJECT_MACRO",
        "golden-amber tea liquor in small ceramic bowl emitting gentle soothing warmth",
        "nourishing tea bowl held in open hands, gentle steam rising into calm morning room, crisp Full HD 1080p",
    ),
    259: (
        "OBJECT_MACRO",
        "single blooming white lotus flower floating quietly on still pond under peaceful sky",
        "pure blossoming compassion, pristine white petals resting untouched by muddy water beneath, crisp Full HD 1080p",
    ),
}

if __name__ == "__main__":
    print(f"Total bespoke beats for chanh_niem_ke: {len(BESPOKE_BEATS)}")
    cores = [v[1][:60].lower() for v in BESPOKE_BEATS.values()]
    print(f"Unique cores count: {len(set(cores))}/{len(cores)}")
    assert len(set(cores)) == len(cores), f"Duplicates found: {len(cores) - len(set(cores))}"
    print("ALL 190 CORES ARE 100% UNIQUE!")
