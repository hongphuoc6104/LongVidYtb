"""Bespoke Explainer Prompt Mapping for tam_tinh_dem (190 new beats).

Every beat index maps to: (explainer_type, core_clause, details)
Guarantees 100% unique core subjects (b["prompt"].split(",")[1].strip()[:60].lower())
with zero template cycling and zero generic fallbacks.
"""

PREFIX = "Studio Ghibli nocturnal & gentle poetic atmosphere still,"
SUFFIX = ", zero text overlay, no watermarks"

BESPOKE_BEATS = {
    1: (
        "OBJECT_MACRO",
        "warm streetlamp casting long pool of soft amber radiance across wet asphalt road",
        "soft indigo night tones, warm glowing amber illumination, hand-painted anime aesthetic, crisp Full HD 1080p",
    ),
    2: (
        "OBJECT_MACRO",
        "vast empty avenue extending into quiet night horizon without a single soul",
        "peaceful deserted city street bathed in moonlight, quiet storefront awnings, crisp Full HD 1080p",
    ),
    3: (
        "OBJECT_MACRO",
        "vintage bicycle resting peacefully against iron railing under quiet street corner",
        "stationary wheels at rest, cessation of daytime haste, tranquil nocturnal stillness, crisp Full HD 1080p",
    ),
    4: (
        "OBJECT_MACRO",
        "darkened shopfront roll-up steel shutters pulled down firmly in deep nighttime silence",
        "closed neighborhood bakery, day labor complete, peaceful suburban sanctuary, crisp Full HD 1080p",
    ),
    6: (
        "OBJECT_MACRO",
        "delicate tree branches silhouetted against deep starry indigo sky swaying in gentle breeze",
        "poetic nocturnal rhythm, soft wind whispering through leaves like a gentle lullaby, crisp Full HD 1080p",
    ),
    7: (
        "OBJECT_MACRO",
        "soft pale moonbeams filtering through sheer window curtains onto polished wooden floor",
        "gentle silver light quadrangles resting on cedar floorboards, tranquil bedroom calm, crisp Full HD 1080p",
    ),
    8: (
        "OBJECT_MACRO",
        "vintage wooden wall clock with round brass pendulum ticking unhurriedly in dim room",
        "gentle rhythmic acoustic pulse, measured soothing heartbeat of quiet midnight hours, crisp Full HD 1080p",
    ),
    9: (
        "OBJECT_MACRO",
        "macro view of carved oak pendulum swinging smoothly between dark and light arcs",
        "hypnotic peaceful cadence, reassuring passage of resting time, crisp Full HD 1080p",
    ),
    11: (
        "OBJECT_MACRO",
        "two gentle hands cupping a steaming ceramic mug of hot chamomile tea in low light",
        "comforting thermal tactile sensation, warming tired fingers after long exhausting day, crisp Full HD 1080p",
    ),
    12: (
        "OBJECT_MACRO",
        "delicate tendril of fragrant herbal steam rising gracefully from tea cup toward lamp",
        "curling vapor ribbon carrying soothing notes of honey and dried blossoms, crisp Full HD 1080p",
    ),
    13: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing chamomile herbal vapors soothing tense neck and shoulder muscle fibers",
        "gradual physiological unwinding, tightness melting into deep restorative relaxation, crisp Full HD 1080p",
    ),
    15: (
        "OBJECT_MACRO",
        "crystalline condensation droplets tracing winding paths down dark cool windowpane",
        "gentle nocturnal cleansing, external moisture washing away accumulated daytime dust, crisp Full HD 1080p",
    ),
    16: (
        "OBJECT_MACRO",
        "soft blurred city lights glowing like colorful pastel bokeh orbs beyond rain glass",
        "distant nocturnal metropolis transformed into dreamy luminous watercolor backdrop, crisp Full HD 1080p",
    ),
    18: (
        "OBJECT_MACRO",
        "open personal journal lying on warm desk beside glowing desk lamp with inked fountain pen",
        "sacred intimate communion with self, returning to original inner innocence, crisp Full HD 1080p",
    ),
    19: (
        "OBJECT_MACRO",
        "small clay bird figurine resting peacefully beside open book on cedar windowsill",
        "quiet domestic companionship, soul finding its serene nest in midnight hours, crisp Full HD 1080p",
    ),
    21: (
        "OBJECT_MACRO",
        "deep indigo velvet shadows embracing cozy armchair like soft caring mother arms",
        "protective nocturnal cocoon, silence acting as restorative medicine for weary heart, crisp Full HD 1080p",
    ),
    23: (
        "SPLIT_COMPARISON",
        "split comparison of forced smiling daytime porcelain mask versus tired real face in mirror",
        "stiff theatrical facade on left contrasted with vulnerable exhausted genuine eyes on right, crisp Full HD 1080p",
    ),
    24: (
        "OBJECT_MACRO",
        "stiff white ceramic mask painted with cheerful permanent smile lying flat on desk",
        "corporate compliance facade, rigid pleasantry worn to satisfy external expectations, crisp Full HD 1080p",
    ),
    25: (
        "OBJECT_MACRO",
        "tired human eyes reflecting dim lamplight revealing heavy unspoken emotional fatigue",
        "quiet truth behind the mask, soul admitting the heavy toll of constant pleasing, crisp Full HD 1080p",
    ),
    27: (
        "OBJECT_MACRO",
        "heavy iron visor helmet set down on low table showing deep scratches from battle",
        "laying down emotional armor, releasing the exhausting mandate to appear invincible, crisp Full HD 1080p",
    ),
    28: (
        "SPLIT_COMPARISON",
        "split portrayal of supporting entire family like granite pillar versus trembling hands alone",
        "stoic pillar duty on left contrasted with fragile solitary human need for care on right, crisp Full HD 1080p",
    ),
    29: (
        "OBJECT_MACRO",
        "worn leather backpack bulging with heavy stones of expectations resting on floorboards",
        "physical manifestation of familial duty, setting down the unvoiced burdens of years, crisp Full HD 1080p",
    ),
    31: (
        "OBJECT_MACRO",
        "circus clown colorful costume hanging limp on wooden hanger in silent dark dressing room",
        "the performance ends, cessation of the exhausting duty to entertain others, crisp Full HD 1080p",
    ),
    32: (
        "OBJECT_MACRO",
        "echoing empty auditorium with rows of vacant red velvet seats after crowd departs",
        "sudden cavernous emptiness, profound hollow stillness following loud social gatherings, crisp Full HD 1080p",
    ),
    33: (
        "OBJECT_MACRO",
        "silent mobile phone lying face-down on nightstand without a single caring message",
        "unasked questions, loneliness of carrying burdens without anyone inquiring if you are okay, crisp Full HD 1080p",
    ),
    35: (
        "SITUATIONAL_ACTION",
        "weary figure gently unfastening heavy woolen coat and letting it drape over chair back",
        "shedding daytime armor, profound physical liberation as outer layers are released, crisp Full HD 1080p",
    ),
    36: (
        "OBJECT_MACRO",
        "single warm exhalation vapor dissipating softly into quiet amber lamplight of bedroom",
        "sigh of deep relief, tension dissolving into the peaceful quietness of personal sanctuary, crisp Full HD 1080p",
    ),
    37: (
        "OBJECT_MACRO",
        "cozy bedroom walls lined with warm wooden bookshelves and soft framed drawings",
        "gentle domestic sanctuary, comforting architecture sheltering soul from worldly judgment, crisp Full HD 1080p",
    ),
    39: (
        "OBJECT_MACRO",
        "soft fluffy woolen blanket draped across armchair inviting tired body to collapse in peace",
        "unconditional permission to rest, zero demands for bravery in the quiet of midnight, crisp Full HD 1080p",
    ),
    40: (
        "OBJECT_MACRO",
        "weary hands resting open upon soft cotton knees in posture of total honest surrender",
        "honoring exhaustion, acknowledging personal limits without shame or self-recrimination, crisp Full HD 1080p",
    ),
    42: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing self-compassion act of accepting exhaustion releasing deep healing endorphins",
        "emotional catharsis mechanism, admitting vulnerability unlocking soothing mental restoration, crisp Full HD 1080p",
    ),
    43: (
        "OBJECT_MACRO",
        "single warm incandescent bulb glowing inside paper lantern casting amber light on floor",
        "authentic selfhood, safe space where being completely ordinary is sacred and enough, crisp Full HD 1080p",
    ),
    45: (
        "OBJECT_MACRO",
        "small wooden rowboat drifting peacefully down tranquil wide river under starry night sky",
        "nocturnal river parable, craft floating effortlessly on glassy dark water reflecting stars, crisp Full HD 1080p",
    ),
    46: (
        "OBJECT_MACRO",
        "mirror-like dark river surface reflecting thousands of sparkling golden constellations",
        "cosmic river reflection, boat floating between two infinite skies of luminous starlight, crisp Full HD 1080p",
    ),
    47: (
        "OBJECT_MACRO",
        "cluster of twinkling diamond stars shining through indigo sky above quiet weeping willows",
        "celestial tranquility, gentle stellar radiance illuminating gentle ripples of midnight river, crisp Full HD 1080p",
    ),
    48: (
        "OBJECT_MACRO",
        "vast peaceful water horizon merging seamlessly into dark misty forest shores",
        "boundaryless serenity, quiet river journey free from urgent destinations or docking ports, crisp Full HD 1080p",
    ),
    50: (
        "SPLIT_COMPARISON",
        "split comparison of frantic daytime rowing against rapids versus nighttime drifting at ease",
        "sweat and strained muscles on left contrasted with oars resting across gunwales on right, crisp Full HD 1080p",
    ),
    51: (
        "OBJECT_MACRO",
        "macro close-up of blistered white-knuckled hands gripping weathered wooden boat oar",
        "strained muscular exhaustion from perpetual fighting against life turbulent currents, crisp Full HD 1080p",
    ),
    52: (
        "OBJECT_MACRO",
        "raging white-water river rapids tossing small craft violently among sharp jagged rocks",
        "daytime existential struggle, endless friction against uncontrollable worldly obstacles, crisp Full HD 1080p",
    ),
    53: (
        "OBJECT_MACRO",
        "towering ocean waves crashing over small wooden prow threatening to swamp vessel",
        "overwhelming pressure of external demands, feeling close to drowning in daily obligations, crisp Full HD 1080p",
    ),
    55: (
        "OBJECT_MACRO",
        "dense cargo of heavy iron lockboxes weighing down rowboat nearly to water level",
        "burdensome mental baggage, excessive expectations dragging down inner vitality, crisp Full HD 1080p",
    ),
    56: (
        "OBJECT_MACRO",
        "smooth glass-like water surface reflecting serene full moon in absolute stillness",
        "storm subsided, nocturnal calm returning to water as wind dies down completely, crisp Full HD 1080p",
    ),
    57: (
        "OBJECT_MACRO",
        "ripples smoothing out into flat liquid mirror around drifting wooden boat hull",
        "subsiding turbulence, external chaos settling into restorative nocturnal peace, crisp Full HD 1080p",
    ),
    59: (
        "SITUATIONAL_ACTION",
        "hands gently pulling wooden oars inside boat and laying them flat on bottom boards",
        "releasing the struggle, deliberate choice to stop fighting natural river current, crisp Full HD 1080p",
    ),
    60: (
        "OBJECT_MACRO",
        "tired hands resting limp and open beside wooden gunwale catching cool gentle mist",
        "unclenched palms, releasing tension into cool night air, fingers relaxing in peace, crisp Full HD 1080p",
    ),
    61: (
        "OBJECT_MACRO",
        "gentle river current carrying wooden boat smoothly forward through misty canyon",
        "yielding to flow, trusting the natural carrying capacity of life without strain, crisp Full HD 1080p",
    ),
    62: (
        "OBJECT_MACRO",
        "water lilies parting gently around boat bow as it glides silently down stream",
        "effortless movement, river welcoming vessel with gentle caressing fluid motion, crisp Full HD 1080p",
    ),
    64: (
        "OBJECT_MACRO",
        "luminous golden swirl of Milky Way galaxy arching across entire indigo night sky",
        "magnificent cosmic tapestry, vast stellar river mirroring the quiet water below, crisp Full HD 1080p",
    ),
    65: (
        "OBJECT_MACRO",
        "paper origami boat floating freely on pond without human steersman or rudder",
        "surrendering forced control, accepting that destiny unfolds in its own wise rhythm, crisp Full HD 1080p",
    ),
    67: (
        "OBJECT_MACRO",
        "gentle dark water ripples lapping rhythmically against curved cedar boat planks",
        "soothing acoustic lullaby, aquatic embrace holding traveler safe in maternal embrace, crisp Full HD 1080p",
    ),
    69: (
        "OBJECT_MACRO",
        "traveler lying back comfortably on soft blankets in bottom of boat looking at stars",
        "earned repose, absolute surrender to restful slumber under canopy of night sky, crisp Full HD 1080p",
    ),
    70: (
        "OBJECT_MACRO",
        "relaxed silhouette floating between star-filled river and star-filled heavens",
        "weightless tranquility, total bodily release into the cradle of the cosmos, crisp Full HD 1080p",
    ),
    72: (
        "SITUATIONAL_ACTION",
        "solitary silhouette standing by apartment window looking out at sprawling midnight city",
        "contemplative night gaze, solitary figure holding warm cup looking across dark rooftops, crisp Full HD 1080p",
    ),
    73: (
        "SPLIT_COMPARISON",
        "split comparison of running marathon competitors ahead versus lonely walker in alley",
        "phantom race anxiety, fear of falling behind peers contrasted with quiet unique journey, crisp Full HD 1080p",
    ),
    74: (
        "OBJECT_MACRO",
        "creeping cold fog slithering across windowsill like subtle invisible tendril of doubt",
        "creeping social insecurity, late-night comparison trap whispering inadequacy into ear, crisp Full HD 1080p",
    ),
    76: (
        "OBJECT_MACRO",
        "glowing smartphone screen displaying glamorous social media milestones and luxury vacation photos",
        "digital illusion of universal perfection, highlight reels distorting perception of normal life, crisp Full HD 1080p",
    ),
    77: (
        "OBJECT_MACRO",
        "glittering golden trophy standing on high pedestal illuminated by flattering spotlights",
        "external emblems of early success, glittering facade hiding behind-the-scenes struggles, crisp Full HD 1080p",
    ),
    78: (
        "OBJECT_MACRO",
        "carousel of smiling faces posing at glamorous parties under bright fairy lights",
        "curated public display, synthetic theater of happiness masking private loneliness, crisp Full HD 1080p",
    ),
    79: (
        "OBJECT_MACRO",
        "fragile golden mirror cracking down the center to reveal hollow gray void behind",
        "piercing the illusion, recognizing that surface perfection is an empty mirage, crisp Full HD 1080p",
    ),
    81: (
        "SPLIT_COMPARISON",
        "split comparison of spring cherry blossom versus winter plum blossom in snow",
        "different blooming seasons: plum does not compete with cherry; each blossoms in its time, crisp Full HD 1080p",
    ),
    82: (
        "OBJECT_MACRO",
        "antique astronomical clock showing individual personal timeline marked by birth star",
        "sovereign life rhythm, walking along one own ordained astrological time zone in peace, crisp Full HD 1080p",
    ),
    83: (
        "OBJECT_MACRO",
        "patient river turtle walking steadily across mossy forest floor reaching stream safely",
        "dignity of slow progress, deliberate unhurried pacing arriving safely at destination, crisp Full HD 1080p",
    ),
    85: (
        "OBJECT_MACRO",
        "dark empty cavern illuminated by single warm candle turning stone walls to gold",
        "reframing solitude, solitary space transformed from cold prison into sacred temple, crisp Full HD 1080p",
    ),
    86: (
        "OBJECT_MACRO",
        "crystal prism purifying chaotic white light into clear focused beam of pure blue",
        "sacred quiet filter, solitary time distilling mental noise into spiritual clarity, crisp Full HD 1080p",
    ),
    87: (
        "OBJECT_MACRO",
        "monastery courtyard fountain bubbling softly in solitary moonlight surrounded by garden",
        "communion with inner self, returning to the pristine spring of own soul, crisp Full HD 1080p",
    ),
    89: (
        "OBJECT_MACRO",
        "seashell held to ear listening to the deep authentic ocean murmur of inner heart",
        "hearing the forgotten whisper, reclaiming deepest buried longings in quiet night, crisp Full HD 1080p",
    ),
    90: (
        "OBJECT_MACRO",
        "childhood watercolor sketchbook lying open showing vibrant colorful flying dragons",
        "resurrecting neglected dreams, pure authentic creative aspirations awaiting awakening, crisp Full HD 1080p",
    ),
    91: (
        "OBJECT_MACRO",
        "small wooden music box playing delicate forgotten melody in quiet room",
        "gentle chime of nostalgia, authentic childhood innocence preserved untouched by world, crisp Full HD 1080p",
    ),
    93: (
        "SPLIT_COMPARISON",
        "split comparison of loud superficial party chatter versus quiet solitary cup of tea",
        "hollow chattering on left contrasted with nourishing contemplative silence on right, crisp Full HD 1080p",
    ),
    94: (
        "OBJECT_MACRO",
        "cacophony of glowing television screens flashing urgent breaking news headlines",
        "invasive media noise, modern impulse to drown sacred silence in sensationalist chatter, crisp Full HD 1080p",
    ),
    96: (
        "OBJECT_MACRO",
        "warm velvety midnight sky holding city below in soft protective caring embrace",
        "benevolent nocturnal presence, darkness as a loyal guardian rather than frightening void, crisp Full HD 1080p",
    ),
    98: (
        "OBJECT_MACRO",
        "gentle shadow sitting quietly beside armchair like faithful companion dog resting chin",
        "faithful presence of stillness, quiet solitude sharing midnight vigil without judgment, crisp Full HD 1080p",
    ),
    99: (
        "OBJECT_MACRO",
        "secluded mountain valley sanctuary where zero clocks or measuring tapes exist",
        "freedom from social metrics, sacred refuge where pace is never evaluated or judged, crisp Full HD 1080p",
    ),
    101: (
        "SPLIT_COMPARISON",
        "split comparison of bare winter tree versus vibrant springtime blooming canopy",
        "seasonal cycle: shedding leaves is not death but wise preservation of core sap, crisp Full HD 1080p",
    ),
    102: (
        "OBJECT_MACRO",
        "winter oak tree standing dignified in snow holding vital green sap deep within trunk",
        "hibernation wisdom, resting deeply in cold months to prepare for glorious spring explosion, crisp Full HD 1080p",
    ),
    103: (
        "MECHANISM_CUTAWAY",
        "subterranean cutaway showing tree roots drinking underground moisture throughout winter",
        "invisible subterranean accumulation, quiet winter rest fueling future spring vigor, crisp Full HD 1080p",
    ),
    104: (
        "OBJECT_MACRO",
        "macro view of subterranean root hair absorbing microscopic mineral water droplet in darkness",
        "unseen daily nourishment, private quiet restoration taking place away from public eyes, crisp Full HD 1080p",
    ),
    106: (
        "OBJECT_MACRO",
        "dormant brown garden bed covered in white snow blanket waiting peacefully for spring",
        "fallow season, resting soil accumulating mineral fertility for future golden harvest, crisp Full HD 1080p",
    ),
    107: (
        "OBJECT_MACRO",
        "glowing green bud tightly wrapped in winter scales sleeping safely on branch tip",
        "embryo of tomorrow, future blossoming safely protected inside protective winter sheath, crisp Full HD 1080p",
    ),
    108: (
        "OBJECT_MACRO",
        "antique clock spring slowly uncoiling to release its stored mechanical tension in cabinet",
        "necessity of unwinding, releasing accumulated torque so mechanism does not snap, crisp Full HD 1080p",
    ),
    110: (
        "OBJECT_MACRO",
        "classical musical sheet showing whole rest note symbol surrounded by empty staff",
        "the beauty of the musical rest: silence between notes is what creates melody and meaning, crisp Full HD 1080p",
    ),
    111: (
        "CAUSE_EFFECT_DIAGRAM",
        "musical composition wave diagram proving melody collapses into chaos without rests",
        "necessity of pauses, deliberate silent intervals creating harmony out of sound, crisp Full HD 1080p",
    ),
    112: (
        "OBJECT_MACRO",
        "violin bow resting gently across wooden instrument body in velvet-lined case",
        "musician instrument at rest, strings relaxing so acoustic tone remains pure and sweet, crisp Full HD 1080p",
    ),
    113: (
        "OBJECT_MACRO",
        "weary runner stepping off track taking sip of cool water and sitting on bench",
        "honoring rest, pausing not as defeat but as essential preparation for long journey, crisp Full HD 1080p",
    ),
    115: (
        "OBJECT_MACRO",
        "deep restorative delta brainwaves flowing in slow undulating turquoise ribbons on monitor",
        "neurobiological sleep architecture, nocturnal cellular repair rebuilding synaptic pathways, crisp Full HD 1080p",
    ),
    116: (
        "OBJECT_MACRO",
        "healing golden salve being smoothed gently over fractured ceramic bowl seam",
        "cellular restorative process, gentle sleep repairing microscopic micro-tears of life, crisp Full HD 1080p",
    ),
    117: (
        "OBJECT_MACRO",
        "tender green vine unfurling tiny tendril toward first ray of dawn after rain",
        "resurrection of energy, night pause naturally yielding fresh morning vitality, crisp Full HD 1080p",
    ),
    119: (
        "OBJECT_MACRO",
        "warm yellow light shining from window of small wooden cottage in middle of snowy woods",
        "cozy haven in wilderness, warm welcoming refuge amidst cold vast nocturnal forest, crisp Full HD 1080p",
    ),
    120: (
        "OBJECT_MACRO",
        "open brick hearth fireplace burning with crackling dry cedar logs and golden embers",
        "elemental warmth, radiating comforting heat that banishes all outdoor winter chills, crisp Full HD 1080p",
    ),
    122: (
        "OBJECT_MACRO",
        "steaming kettle whistling softly on wood stove pouring fragrant amber water into mug",
        "simple domestic ritual, comforting sounds and warm scents grounding soul in present peace, crisp Full HD 1080p",
    ),
    124: (
        "OBJECT_MACRO",
        "soft pair of knitted woolen socks warming tired feet beside glowing hearth",
        "sensory comfort, gentle physical pampering releasing accumulated stress from walking, crisp Full HD 1080p",
    ),
    125: (
        "OBJECT_MACRO",
        "old well-loved storybook resting open on arm of stuffed armchair beside reading lamp",
        "gentle literary sanctuary, familiar comforting words carrying mind to peaceful lands, crisp Full HD 1080p",
    ),
    127: (
        "OBJECT_MACRO",
        "sleeping orange cat curled into tight ball purring softly on woven wool rug",
        "master of restful contentment, feline relaxation embodying pure unhurried peace, crisp Full HD 1080p",
    ),
    128: (
        "OBJECT_MACRO",
        "warm amber glow of table lamp reflecting softly in brass knobs of mahogany desk",
        "intimate golden atmosphere, cozy interior sanctuary holding soul in gentle warmth, crisp Full HD 1080p",
    ),
    130: (
        "OBJECT_MACRO",
        "heavy wool tapestry hanging over bedroom door muffling all external street sounds",
        "acoustic buffer, total barrier insulating quiet private world from outside chaos, crisp Full HD 1080p",
    ),
    131: (
        "OBJECT_MACRO",
        "hand gently tracing circle of rim of warm tea mug feeling smooth glazed surface",
        "mindful tactile contact, grounding awareness in comforting tangible reality of cup, crisp Full HD 1080p",
    ),
    132: (
        "OBJECT_MACRO",
        "small slice of dried orange floating inside amber tea infusing drink with citrus scent",
        "subtle sensory delight, golden fruit slice glowing like miniature sun inside cup, crisp Full HD 1080p",
    ),
    134: (
        "OBJECT_MACRO",
        "pile of old broken pottery shards being tenderly buried in garden soil beneath flowerbed",
        "burying past errors, honoring old lessons while releasing shame into fertile compost, crisp Full HD 1080p",
    ),
    135: (
        "OBJECT_MACRO",
        "iron key turning smoothly inside ancient rusted lock opening long-sealed garden gate",
        "forgiving oneself, turning the key of compassion to liberate soul from self-blame, crisp Full HD 1080p",
    ),
    136: (
        "OBJECT_MACRO",
        "heavy iron balance scale with weights tipped by single white feather of self-forgiveness",
        "mercy outweighing judgment, gentleness tipping the balance toward inner peace, crisp Full HD 1080p",
    ),
    138: (
        "OBJECT_MACRO",
        "paper sailboat carrying written list of old regrets burning peacefully on dark pond",
        "ritual of release, past mistakes converted into smoke and ash floating away on water, crisp Full HD 1080p",
    ),
    139: (
        "OBJECT_MACRO",
        "white ash dispersing weightlessly across dark ripples of pond under moonlight",
        "complete spiritual purification, immutable history surrendered to forgiving cosmos, crisp Full HD 1080p",
    ),
    140: (
        "OBJECT_MACRO",
        "child and adult self holding hands under ancient sheltering weeping willow tree",
        "reconciliation with past self, embracing younger self with deep understanding and love, crisp Full HD 1080p",
    ),
    142: (
        "OBJECT_MACRO",
        "soft bandage wrapped tenderly around healed scar on forearm with wild daisies pinned",
        "honoring survival, scars treated as medals of resilience rather than badges of shame, crisp Full HD 1080p",
    ),
    143: (
        "OBJECT_MACRO",
        "crystal clear raindrops washing away chalk words written on school blackboard",
        "clean slate, yesterday errors completely dissolved by natural grace of night, crisp Full HD 1080p",
    ),
    144: (
        "OBJECT_MACRO",
        "pristine empty chalkboard drying in morning air ready for new inspiring sketches",
        "infinite tomorrow, untouched potential waiting for fresh purposeful beginnings, crisp Full HD 1080p",
    ),
    145: (
        "OBJECT_MACRO",
        "gentle open palm releasing captured butterfly back into moonlit summer garden",
        "releasing self-punishment, granting absolute freedom to own imprisoned heart, crisp Full HD 1080p",
    ),
    147: (
        "OBJECT_MACRO",
        "old clock pendulum slowing down gently into comfortable steady meditative swing",
        "settling into natural tempo, mind attuning to the slower healing frequency of night, crisp Full HD 1080p",
    ),
    148: (
        "OBJECT_MACRO",
        "gentle breeze rustling through sheer lace curtain blowing scent of rain into room",
        "fresh natural ventilation, night air refreshing bedroom with cool invigorating calm, crisp Full HD 1080p",
    ),
    149: (
        "OBJECT_MACRO",
        "two glowing fireflies dancing in slow playful loops above grassy garden border",
        "innocent nighttime play, tiny sparks of wonder dancing through velvet darkness, crisp Full HD 1080p",
    ),
    151: (
        "OBJECT_MACRO",
        "smooth rounded river pebble resting comfortably on bedside wooden tray",
        "grounding talisman, smooth mineral texture reminding soul of enduring stability, crisp Full HD 1080p",
    ),
    152: (
        "OBJECT_MACRO",
        "vast nocturnal sky filled with billions of gentle shining stars embracing the planet",
        "cosmic sanctuary, universal benevolence wrapping every living being in peaceful care, crisp Full HD 1080p",
    ),
    154: (
        "OBJECT_MACRO",
        "heavy pack dropped onto floor with loud soft thud as shoulders rise and drop in relief",
        "unburdened posture, body rejoicing in sudden absence of fifty kilograms of expectations, crisp Full HD 1080p",
    ),
    156: (
        "OBJECT_MACRO",
        "cemetery of old worries sleeping peacefully under blanket of soft fallen autumn leaves",
        "letting past rest, yesterday anxieties asleep beneath nature restorative compost, crisp Full HD 1080p",
    ),
    157: (
        "OBJECT_MACRO",
        "dark quiet forest illuminated by soft silver moonlight where all creatures sleep soundly",
        "universal rest, all nature resting in tranquil harmony under starry nighttime sky, crisp Full HD 1080p",
    ),
    159: (
        "OBJECT_MACRO",
        "severed strings of puppet marionette lying in neat coil beside small wooden easel",
        "autonomy reclaimed, refusing to dance to other people expectations or scripts, crisp Full HD 1080p",
    ),
    160: (
        "OBJECT_MACRO",
        "heavy iron yoke lifting off shoulders of kneeling traveler by gentle invisible hands",
        "release from approval addiction, sovereign soul standing tall in own dignity, crisp Full HD 1080p",
    ),
    161: (
        "OBJECT_MACRO",
        "clean white canvas resting on painter easel in quiet studio waiting for painter touch",
        "own sovereign life, authoring personal story without seeking crowd approval, crisp Full HD 1080p",
    ),
    163: (
        "OBJECT_MACRO",
        "distant city lights viewed from hill looking like harmless scattered glitter dust",
        "perspective of distance, distant opinions losing all power to dictate personal peace, crisp Full HD 1080p",
    ),
    164: (
        "OBJECT_MACRO",
        "single sunflower turning its face toward gentle midnight moon in quiet field",
        "blooming for oneself, living authentically without needing universal applause, crisp Full HD 1080p",
    ),
    165: (
        "OBJECT_MACRO",
        "heavy wooden door closing softly and latch clicking firmly shut against night street",
        "sanctuary boundary, locking out the noise and opinions of the outside world, crisp Full HD 1080p",
    ),
    166: (
        "OBJECT_MACRO",
        "warm wool slippers waiting beside soft woven bedside rug under gentle amber light",
        "homecoming comfort, body settling into restorative domestic peace and security, crisp Full HD 1080p",
    ),
    168: (
        "OBJECT_MACRO",
        "wooden acoustic metronome slowing its beat from allegro to largo tempo on piano",
        "decelerating life pace, returning to comfortable human biological rhythm, crisp Full HD 1080p",
    ),
    169: (
        "SITUATIONAL_ACTION",
        "traveler slowing stride to walk mindfully through quiet moonlit grove of pine trees",
        "honoring slow pace, walking deliberately to savor each breath of fresh forest air, crisp Full HD 1080p",
    ),
    170: (
        "OBJECT_MACRO",
        "snail moving with majestic patient dignity across wet glistening garden flagstone",
        "perfection of slowness, steady progress that never rushes yet always reaches goal, crisp Full HD 1080p",
    ),
    171: (
        "OBJECT_MACRO",
        "mirror-like pool in Japanese garden holding moon reflection with unshakeable stillness",
        "tranquility surpassing worldly ambition, inner quiet worth more than golden trophies, crisp Full HD 1080p",
    ),
    173: (
        "OBJECT_MACRO",
        "open iron birdcage hanging in window while canary perches freely on outdoor branch",
        "breaking free from societal molds, choosing wild authentic freedom over cage, crisp Full HD 1080p",
    ),
    174: (
        "OBJECT_MACRO",
        "handmade ceramic coffee cup with imperfect wonky rim holding delicious steaming drink",
        "daring to be imperfect, celebrating clumsy authentic humanity over sterile perfection, crisp Full HD 1080p",
    ),
    175: (
        "OBJECT_MACRO",
        "wild colorful wildflower meadow growing naturally without manicured garden hedges",
        "courage of authentic wildness, blooming according to inner nature without apology, crisp Full HD 1080p",
    ),
    177: (
        "OBJECT_MACRO",
        "young tree sapling drinking midnight mist under stars growing imperceptibly taller",
        "invisible daily maturation, nighttime rest feeding tomorrow growth in secret, crisp Full HD 1080p",
    ),
    178: (
        "OBJECT_MACRO",
        "tender green leaf unfurling silently under moonlight glistening with silver dew",
        "sacred quiet growth, soul expanding in depth through endured quiet seasons, crisp Full HD 1080p",
    ),
    179: (
        "OBJECT_MACRO",
        "carved wooden growth chart on bedroom door showing steady upward pencil notches",
        "tangible proof of progress, small daily efforts accumulating into profound wisdom, crisp Full HD 1080p",
    ),
    181: (
        "OBJECT_MACRO",
        "smooth rounded river stone with beautiful multicolored quartz veins running through it",
        "river tumbling polish, hardships transforming rough mineral into precious smooth jewel, crisp Full HD 1080p",
    ),
    182: (
        "OBJECT_MACRO",
        "macro view of fine golden scratches on antique silver compass case shining warmly",
        "honoring scars, marks of survival validating warrior courage and perseverance, crisp Full HD 1080p",
    ),
    184: (
        "OBJECT_MACRO",
        "calm water surface of garden stone basin holding perfect reflection of evening star",
        "anchoring serenity, protecting inner tranquility against all outside intrusion, crisp Full HD 1080p",
    ),
    186: (
        "SITUATIONAL_ACTION",
        "traveler letting out long relaxed breath as body sinks deeply into soft mattress",
        "earned physical relief, surrendering into unconditional nocturnal safety and peace, crisp Full HD 1080p",
    ),
    187: (
        "OBJECT_MACRO",
        "heavy brass lock bolt slid firmly across door frame keeping all critics outside",
        "absolute boundary, external judgments stopped permanently at threshold of bedroom, crisp Full HD 1080p",
    ),
    188: (
        "OBJECT_MACRO",
        "empty hallway outside door quiet and dark with no one left to demand anything",
        "complete cessation of demands, solitary autonomy reigning in bedroom sanctuary, crisp Full HD 1080p",
    ),
    190: (
        "OBJECT_MACRO",
        "warm white ceramic teacup resting on rustic wooden coaster beside small wax candle",
        "minimalist midnight tea ceremony, simple objects creating profound atmosphere of comfort, crisp Full HD 1080p",
    ),
    191: (
        "OBJECT_MACRO",
        "wall calendar page for today with bold black checkmark drawn through the date",
        "official closure, another day completed and surrendered into historical record, crisp Full HD 1080p",
    ),
    192: (
        "OBJECT_MACRO",
        "leather briefcase snapped shut and placed in dark corner until tomorrow morning",
        "putting work away, official shutdown of professional identity and commercial duties, crisp Full HD 1080p",
    ),
    193: (
        "OBJECT_MACRO",
        "thin wisp of white incense smoke curling and vanishing into soft evening darkness",
        "dissolving worries, anxieties evaporating weightlessly into nocturnal air, crisp Full HD 1080p",
    ),
    195: (
        "OBJECT_MACRO",
        "warm sudsy water running over hands washing away ink stains and city grime",
        "purifying wash, cleansing ritual washing away psychological dust of long workday, crisp Full HD 1080p",
    ),
    196: (
        "OBJECT_MACRO",
        "stack of closed office folders lying quietly under paperweight on office desk",
        "unfinished work resting peacefully, trusting that tomorrow will have its own strength, crisp Full HD 1080p",
    ),
    197: (
        "OBJECT_MACRO",
        "harsh telephone receiver resting in cradle with silent light on answering machine",
        "disconnected from urgency, no telephone calls or urgent demands allowed to pierce room, crisp Full HD 1080p",
    ),
    198: (
        "OBJECT_MACRO",
        "peaceful quiet room with only gentle ticking of wall clock and soft wind outside",
        "total absence of interruption, pristine quietness wrapping sleeping home in care, crisp Full HD 1080p",
    ),
    200: (
        "OBJECT_MACRO",
        "warm ceramic mug held close to cheek feeling radiant thermal warmth against skin",
        "healing heat, banishing the cold indifference endured throughout busy day outside, crisp Full HD 1080p",
    ),
    201: (
        "OBJECT_MACRO",
        "limp relaxed fingers uncurling completely resting softly on woven cotton bedsheet",
        "complete physical surrender, letting go of the instinct to grasp hold or defend, crisp Full HD 1080p",
    ),
    203: (
        "OBJECT_MACRO",
        "clean white mirror reflecting room with warm golden lamp and cozy bed corner",
        "sanctuary free from critics, no one here demanding impossible perfection or performance, crisp Full HD 1080p",
    ),
    204: (
        "OBJECT_MACRO",
        "weary head resting gently on soft goose feather pillow closing eyes in gratitude",
        "admitting exhaustion, honoring the body need for restorative deep healing slumber, crisp Full HD 1080p",
    ),
    205: (
        "OBJECT_MACRO",
        "gentle hands crossed lightly over chest feeling rhythmic steady beating of heart",
        "heart at rest, giving the faithful cardiac center permission to rest and rejuvenate, crisp Full HD 1080p",
    ),
    206: (
        "SITUATIONAL_ACTION",
        "meditative figure seated cross-legged on floor doing nothing but breathing slowly in out",
        "pure being, resting in existence without needing to achieve or produce anything, crisp Full HD 1080p",
    ),
    208: (
        "OBJECT_MACRO",
        "deep slow inhalation expanding ribcage with fresh pine-scented night mountain air",
        "restorative breath, feeding exhausted neural circuits with pure refreshing oxygen, crisp Full HD 1080p",
    ),
    209: (
        "MECHANISM_CUTAWAY",
        "flowchart showing herbal chamomile molecules binding to GABA receptors in sleeping brain",
        "neurochemical tranquility, biological transition into deep delta restorative sleep cycles, crisp Full HD 1080p",
    ),
    211: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing trapezius and shoulder muscle tension dropping as head rests on pillow",
        "physical decompression, releasing sixty pounds of accumulated daytime postural tension, crisp Full HD 1080p",
    ),
    213: (
        "OBJECT_MACRO",
        "clear amber tea liquor inside cup showing tiny golden star reflected in center",
        "discovering inner peace, finding that serenity is already residing within the heart, crisp Full HD 1080p",
    ),
    214: (
        "OBJECT_MACRO",
        "liquid mirror of tea holding reflection of full moon and passing silver cloud",
        "mind as calm tea bowl, reflecting universe without grasping or generating ripples, crisp Full HD 1080p",
    ),
    216: (
        "OBJECT_MACRO",
        "gentle hand smoothing soft blanket over own shoulder with maternal self-tenderness",
        "practicing self-compassion, treating oneself with the same kindness given to loved child, crisp Full HD 1080p",
    ),
    217: (
        "OBJECT_MACRO",
        "warm embrace of soft plush quilt wrapping around body like warm caring hug",
        "radical self-acceptance, enveloping fragile vulnerable self in unconditional love, crisp Full HD 1080p",
    ),
    219: (
        "STEP_ENUMERATION",
        "three inscribed wooden bedtime affirmation tokens resting beside warm night lamp",
        "three nocturnal whispers: You did your best; Tomorrow is clean; You deserve peace, crisp Full HD 1080p",
    ),
    220: (
        "STEP_ENUMERATION",
        "first token inscribed: Tonight acknowledge that you gave your absolute best today",
        "affirming effort, validating honest work regardless of flawed external results, crisp Full HD 1080p",
    ),
    221: (
        "OBJECT_MACRO",
        "small bronze medal inscribed with laurel branch of quiet personal integrity on desk",
        "private victory, celebrating unpraised perseverance through quiet difficult hours, crisp Full HD 1080p",
    ),
    223: (
        "STEP_ENUMERATION",
        "second token inscribed: Tomorrow is an untouched blank sheet awaiting your steps",
        "clean page promise, sunrise bringing total renewal unburdened by past failures, crisp Full HD 1080p",
    ),
    224: (
        "OBJECT_MACRO",
        "pristine white notebook page completely unwritten glowing softly in dawn light",
        "unwritten future, today mistakes having zero power to dictate tomorrow potential, crisp Full HD 1080p",
    ),
    225: (
        "STEP_ENUMERATION",
        "third token inscribed: You are unconditionally worthy of profound peace and joy",
        "essential human worth, claiming entitlement to happiness simply because you exist, crisp Full HD 1080p",
    ),
    226: (
        "OBJECT_MACRO",
        "golden heart amulet glowing with warm gentle amber light inside velvet jewelry box",
        "inherent preciousness, unshakeable worth untouched by external productivity metrics, crisp Full HD 1080p",
    ),
    228: (
        "OBJECT_MACRO",
        "taking final mindful sip of sweet chamomile tea savoring lingering honey warmth",
        "sweet completion, closing the nocturnal tea ceremony with deep sensory gratitude, crisp Full HD 1080p",
    ),
    229: (
        "OBJECT_MACRO",
        "chest gently rising in slow deep inhalation of soothing lavender room fragrance",
        "final cleansing breath, filling spiritual lungs with evening peace and calm, crisp Full HD 1080p",
    ),
    230: (
        "OBJECT_MACRO",
        "oxygen stream washing through bronchial tree like cool mountain brook over stones",
        "vital cellular baptism, refreshing life force washing through tired biological frame, crisp Full HD 1080p",
    ),
    231: (
        "OBJECT_MACRO",
        "long slow exhalation blowing out tiny candle flame leaving room in peaceful dark",
        "extinguishing flame, surrendering into velvet embrace of restful darkness, crisp Full HD 1080p",
    ),
    233: (
        "OBJECT_MACRO",
        "fragrant dried lavender bundle hanging upside down in window releasing calming scent",
        "botanical aromatherapy, soothing floral perfume washing away mental residue of day, crisp Full HD 1080p",
    ),
    234: (
        "OBJECT_MACRO",
        "sheer white curtains billowing gently like slow ocean waves in nocturnal bedroom window",
        "gentle breath of the house, peaceful rhythm of night rocking soul to sleep, crisp Full HD 1080p",
    ),
    235: (
        "OBJECT_MACRO",
        "empty glass tumbler and folded napkin resting quietly in dark room at rest",
        "completion of day, total stillness descending upon every object in domestic haven, crisp Full HD 1080p",
    ),
    237: (
        "OBJECT_MACRO",
        "golden sunrise beam touching windowsill forecasting healthy renewed morning heart",
        "promise of renewal, sleeping with certainty that morning will bring healed vitality, crisp Full HD 1080p",
    ),
    238: (
        "OBJECT_MACRO",
        "green sprout pushing upward through fertile loam anticipating tomorrow warmth",
        "regenerative optimism, life preparing fresh energy during quiet hours of rest, crisp Full HD 1080p",
    ),
    239: (
        "OBJECT_MACRO",
        "clean straight road stretching across sunlit green hills toward bright horizon",
        "renewed path, faith in tomorrow journey born from deep restorative night rest, crisp Full HD 1080p",
    ),
    240: (
        "OBJECT_MACRO",
        "delicate night-blooming cereus flower opening its pure white petals under stars",
        "silent nocturnal beauty, wondrous transformation unfolding in absolute quietness, crisp Full HD 1080p",
    ),
    242: (
        "OBJECT_MACRO",
        "faint ribbon of lavender incense smoke lingering like silver dream veil in room",
        "scented dream gateway, aromatic mist guiding consciousness into sweet restorative visions, crisp Full HD 1080p",
    ),
    244: (
        "SITUATIONAL_ACTION",
        "weary traveler whispering goodnight to today and closing heavy bedroom door in peace",
        "closing ceremony, releasing today with gratitude and stepping into realm of dreams, crisp Full HD 1080p",
    ),
    245: (
        "OBJECT_MACRO",
        "glowing dream ship sailing smoothly into floating clouds of luminous stardust",
        "entry into dreamland, consciousness embarking on magical nocturnal voyage of healing, crisp Full HD 1080p",
    ),
    247: (
        "OBJECT_MACRO",
        "solitary candle wick sending tiny curl of smoke into moonlight as clock strikes twelve",
        "sacred midnight hour, the quiet threshold between yesterday and tomorrow, crisp Full HD 1080p",
    ),
    248: (
        "OBJECT_MACRO",
        "mountain path covered in heavy snow illuminated by gentle silver light of full moon",
        "serene endurance, knowing that even during bitter storms the cosmos remains peaceful, crisp Full HD 1080p",
    ),
    249: (
        "OBJECT_MACRO",
        "vast planetary globe spinning quietly in starry space wrapped in protective atmosphere",
        "cosmic cradle, universe cradling all living creatures in grand benevolent design, crisp Full HD 1080p",
    ),
    250: (
        "OBJECT_MACRO",
        "soft velvety darkness tucking city under its caring indigo wing like mother hen",
        "universal maternal night, protecting all weary mortals under mantle of peace, crisp Full HD 1080p",
    ),
    252: (
        "OBJECT_MACRO",
        "soft silk chrysalis hanging from moonlit branch keeping caterpillar safe inside",
        "protective nocturnal cocoon, enclosing sleeper in safe transformational chamber, crisp Full HD 1080p",
    ),
    253: (
        "OBJECT_MACRO",
        "deep velvet night embracing sleepy village in silence as every house lamp dims",
        "universal bedtime, village settling into shared synchronized restorative slumber, crisp Full HD 1080p",
    ),
    254: (
        "OBJECT_MACRO",
        "hands pulling thick goose down comforter up to chin feeling sublime warmth",
        "ultimate cozy bliss, nesting into soft warmth as eyelids grow heavy and relaxed, crisp Full HD 1080p",
    ),
    256: (
        "OBJECT_MACRO",
        "closed eyelids with relaxed eyelashes resting softly in dim warm night light",
        "surrender to sleep, conscious mind releasing control and slipping into deep calm, crisp Full HD 1080p",
    ),
    258: (
        "OBJECT_MACRO",
        "peaceful face resting on pillow with faint gentle smile dreaming under starry window",
        "sweet restorative dreams, serene countenances blessed with deep profound nocturnal peace, crisp Full HD 1080p",
    ),
    259: (
        "OBJECT_MACRO",
        "solitary glowing crescent moon floating in deep indigo sky surrounded by twinkling stars",
        "eternal peaceful night, celestial benediction wishing deep sweet restful sleep to all, crisp Full HD 1080p",
    ),
}

if __name__ == "__main__":
    print(f"Total bespoke beats for tam_tinh_dem: {len(BESPOKE_BEATS)}")
    cores = [v[1][:60].lower() for v in BESPOKE_BEATS.values()]
    print(f"Unique cores count: {len(set(cores))}/{len(cores)}")
    assert len(set(cores)) == len(cores), f"Duplicates found: {len(cores) - len(set(cores))}"
    print("ALL 190 CORES ARE 100% UNIQUE!")
