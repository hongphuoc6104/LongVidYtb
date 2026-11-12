"""Bespoke Explainer Prompt Mapping for thuong_cho_kheo (157 new beats).

Every beat index maps to: (explainer_type, core_clause, details)
Guarantees 100% unique core subjects (b["prompt"].split(",")[1].strip()[:60].lower())
with zero template cycling and zero generic fallbacks.
"""

PREFIX = "Cinematic 35mm live-action emotional film still,"
SUFFIX = ", zero text overlay, no watermarks"

BESPOKE_BEATS = {
    1: (
        "OBJECT_MACRO",
        "steaming ceramic bowl of hot vegetable soup resting on cold dark wooden dinner table",
        "shallow depth of field, naturalistic 35mm film grain, moody intimate interior lighting, crisp Full HD 1080p",
    ),
    2: (
        "OBJECT_MACRO",
        "sharp invisible emotional fracture dividing dinner table between two seated family members",
        "casual careless remark freezing domestic warmth, subtle lighting split down tablecloth, crisp Full HD 1080p",
    ),
    4: (
        "OBJECT_MACRO",
        "weary expressive eyes reflecting warm dining room lamp light seeking compassionate understanding",
        "tender vulnerable gaze searching for warmth after long exhausting day outside, crisp Full HD 1080p",
    ),
    5: (
        "SPLIT_COMPARISON",
        "split comparison of vulnerable seeking gaze versus dismissive shrug of partner scrolling phone",
        "emotional bid for connection on left met with frigid indifference on right, crisp Full HD 1080p",
    ),
    7: (
        "OBJECT_MACRO",
        "macro close-up of white knuckles clenching tightly around wooden dining chair armrest",
        "isometric tension, acute physical manifestation of swallowed indignation and injustice, crisp Full HD 1080p",
    ),
    8: (
        "OBJECT_MACRO",
        "dark crimson reflection flaring across kitchen window glass mirroring sudden burst of fury",
        "smoldering rage erupting, Chiaroscuro shadows stretching across domestic room, crisp Full HD 1080p",
    ),
    10: (
        "OBJECT_MACRO",
        "ancient cracked photograph album pulled from drawer as ammunition in bitter argument",
        "weaponizing past mistakes, exhuming old healed scars to punish partner in quarrel, crisp Full HD 1080p",
    ),
    11: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram of sharp verbal arrowheads piercing translucent glowing bond between two people",
        "verbal cruelty severing delicate emotional threads of intimacy and trust, crisp Full HD 1080p",
    ),
    13: (
        "OBJECT_MACRO",
        "heavy bedroom wooden door slamming shut with brass latch vibrating violently",
        "abrupt physical rupture, domestic intimacy severed by angry slammed portal, crisp Full HD 1080p",
    ),
    14: (
        "OBJECT_MACRO",
        "thick soundproof glass wall erected down the center of cozy apartment hallway",
        "invisible psychological fortress separating two lovers standing feet apart in silence, crisp Full HD 1080p",
    ),
    16: (
        "OBJECT_MACRO",
        "bitter chilly stillness settling over empty dining table with half-eaten cooling dinner",
        "haunting domestic aftermath, silent room echoing with unspoken resentments, crisp Full HD 1080p",
    ),
    18: (
        "OBJECT_MACRO",
        "hairline crack spreading slowly across delicate celadon ceramic tea saucer",
        "cumulative relationship fracture, intimacy eroding because neither partner truly listened, crisp Full HD 1080p",
    ),
    20: (
        "SPLIT_COMPARISON",
        "split comparison of biological hearing acoustic waves versus profound emotional empathetic listening",
        "ear drum vibration diagram on left contrasted with heart-to-heart resonance on right, crisp Full HD 1080p",
    ),
    22: (
        "MECHANISM_CUTAWAY",
        "anatomical cutaway showing sound pressure waves striking tympanic membrane and dissipating",
        "passive physiological hearing, acoustic waves bouncing off ear canal without cognitive retention, crisp Full HD 1080p",
    ),
    23: (
        "OBJECT_MACRO",
        "common brass ear trumpet resting casually on table demonstrating effortless auditory function",
        "ordinary biological capacity, anyone with intact ears can passively register acoustic noise, crisp Full HD 1080p",
    ),
    25: (
        "OBJECT_MACRO",
        "autumn wind blowing dry golden leaves across porch without touching solid house door",
        "words passing in one ear and out the other, voice dissipating like wind on empty veranda, crisp Full HD 1080p",
    ),
    26: (
        "OBJECT_MACRO",
        "clean white wax tablet showing zero indentations after human voice finishes speaking",
        "unengaged memory, mental apparatus retaining zero emotional resonance from partner words, crisp Full HD 1080p",
    ),
    28: (
        "SITUATIONAL_ACTION",
        "listener leaning forward with warm eyes and open palms offering undivided sacred presence",
        "the art of authentic listening, conscious gift of unconditional attention to loved one, crisp Full HD 1080p",
    ),
    29: (
        "OBJECT_MACRO",
        "golden bridge of light spanning between two chests connecting hearts in deep understanding",
        "sacred emotional bond, profound empathy bridging the chasm between two separate worlds, crisp Full HD 1080p",
    ),
    31: (
        "OBJECT_MACRO",
        "pair of hands taking off tinted reading glasses and laying them flat on cedar desk",
        "shedding preconceptions, removing cognitive filters to perceive partner authentic reality, crisp Full HD 1080p",
    ),
    32: (
        "OBJECT_MACRO",
        "clear quiet room holding warm space for partner voice without interrupting single word",
        "generous silence, creating vast compassionate territory for someone to express pain, crisp Full HD 1080p",
    ),
    34: (
        "SPLIT_COMPARISON",
        "split comparison of active silent listener versus impatient debater rehearsing next rebuttal",
        "calm open gaze on left contrasted with agitated tapping foot and clenched jaw on right, crisp Full HD 1080p",
    ),
    35: (
        "OBJECT_MACRO",
        "tightly compressed lips concealing internal simmering boiling pot of mental arguments",
        "fake silence, mouth closed while mind frantically constructs defensive counter-attack, crisp Full HD 1080p",
    ),
    37: (
        "OBJECT_MACRO",
        "gladiator holding up iron buckler to deflect partner honest confession as an attack",
        "obsession with being right, converting intimate dialogue into courtroom defense, crisp Full HD 1080p",
    ),
    39: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing vulnerable confession warped by listener ego into hostile spear projectile",
        "defensive cognitive distortion, innocent disclosure interpreted as personal attack, crisp Full HD 1080p",
    ),
    41: (
        "OBJECT_MACRO",
        "family dining table transformed into boxing ring with red velvet ropes around plates",
        "domestic battleground, dinner intimacy perverted into ruthless competition for victory, crisp Full HD 1080p",
    ),
    43: (
        "OBJECT_MACRO",
        "hollow golden trophy standing in center of deserted cold living room after spouse leaves",
        "pyrrhic victory of ego, winning the argument while destroying the living relationship, crisp Full HD 1080p",
    ),
    45: (
        "OBJECT_MACRO",
        "checklist clipboard thrust immediately into face of crying partner sharing pain",
        "premature advice trap, offering sterile five-point action plans before validating grief, crisp Full HD 1080p",
    ),
    46: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing hasty technical solution suffocating the natural emotional release curve",
        "rushing to fix problem shutting down cathartic healing process before it completes, crisp Full HD 1080p",
    ),
    48: (
        "OBJECT_MACRO",
        "heavy burlap sack of office worries slung over bent shoulders of returning worker",
        "exhausting burden of modern labor, physical weight of day crushing spirit and vitality, crisp Full HD 1080p",
    ),
    49: (
        "OBJECT_MACRO",
        "bruised weeping heart silhouette glowing faintly with dim red light inside chest",
        "acute emotional depletion, heart bleeding from micro-rejections and sensory overload, crisp Full HD 1080p",
    ),
    51: (
        "SPLIT_COMPARISON",
        "split comparison of cold analytical interrogation versus warm holding hands in silence",
        "harsh finger pointing on left contrasted with gentle comforting palms on right, crisp Full HD 1080p",
    ),
    52: (
        "OBJECT_MACRO",
        "bucket of ice water poured directly onto fragile glowing ember in hearth",
        "icy intellectual analysis extinguishing the last fragile spark of intimate sharing, crisp Full HD 1080p",
    ),
    54: (
        "OBJECT_MACRO",
        "fragile wilted violet treated like hazardous crime scene evidence by harsh critic",
        "pathologizing weakness, converting innocent vulnerability into shameful moral fault, crisp Full HD 1080p",
    ),
    55: (
        "OBJECT_MACRO",
        "hand dismissively sweeping away tears as if brushing off trivial specks of dust",
        "emotional invalidation, minimizing partner genuine sorrow as childish over-reaction, crisp Full HD 1080p",
    ),
    57: (
        "OBJECT_MACRO",
        "heavy encyclopedia volume dropped squarely onto tiny delicate paper origami swan",
        "didactic lecture crushing fragile self-esteem, intellectual superiority as oppression, crisp Full HD 1080p",
    ),
    58: (
        "OBJECT_MACRO",
        "solitary figure slumped in kitchen corner looking down at own clumsy trembling hands",
        "internalized shame, feeling inadequate and broken after partner relentless critiques, crisp Full HD 1080p",
    ),
    60: (
        "OBJECT_MACRO",
        "closed wooden door with deadbolt turned in dark room where figure sits in silence",
        "retreat into isolation, withdrawing into defensive shell after repeated invalidation, crisp Full HD 1080p",
    ),
    61: (
        "OBJECT_MACRO",
        "dark chasm widening between two armchairs in cozy living room under ceiling lamp",
        "emotional alienation, invisible distance expanding between two people in same room, crisp Full HD 1080p",
    ),
    63: (
        "OBJECT_MACRO",
        "tender hands gently gathering fractured porcelain teacup pieces onto soft velvet cloth",
        "the need for validation, craving gentle witness to hold internal shattered pieces, crisp Full HD 1080p",
    ),
    65: (
        "SPLIT_COMPARISON",
        "split comparison of arid dry desert textbook versus warm crackling living room fireplace",
        "sterile intellectual logic on left contrasted with nurturing relational warmth on right, crisp Full HD 1080p",
    ),
    67: (
        "OBJECT_MACRO",
        "soft welcoming feather landing cushion receiving falling glass ornament without cracking",
        "emotional safe harbor, compassionate listener providing safe landing for partner feelings, crisp Full HD 1080p",
    ),
    69: (
        "OBJECT_MACRO",
        "golden kintsugi liquid lacquer gently flowing into deep ceramic crack binding edges",
        "healing power of empathy, golden understanding restoring fractured bond into beauty, crisp Full HD 1080p",
    ),
    71: (
        "MECHANISM_CUTAWAY",
        "iceberg diagram showing ten percent tip above water representing surface trivial argument",
        "the iceberg of marital conflict: small visible dispute floating above vast submerged needs, crisp Full HD 1080p",
    ),
    72: (
        "OBJECT_MACRO",
        "massive submerged blue glacial body extending deep into dark freezing ocean depths",
        "subterranean reality: deep unmet needs for safety affection and recognition beneath words, crisp Full HD 1080p",
    ),
    74: (
        "OBJECT_MACRO",
        "solitary dirty cotton sock lying on polished parquet floor beside lit dynamite fuse",
        "the trivial trigger: domestic sock acting as spark detonating months of accumulated resentment, crisp Full HD 1080p",
    ),
    75: (
        "SPLIT_COMPARISON",
        "split comparison of the physical laundry item on left versus deep emotional exhaustion on right",
        "the illusion of the conflict source versus the true biological and emotional reality, crisp Full HD 1080p",
    ),
    77: (
        "SITUATIONAL_ACTION",
        "weary spouse in rumpled business suit explaining fatigue with defensive raised palms",
        "defensive justification, attempting to explain away thoughtlessness with work exhaustion, crisp Full HD 1080p",
    ),
    78: (
        "SPLIT_COMPARISON",
        "split composition of two people shouting furiously across a tiny laundry basket on floor",
        "absurdity of escalating quarrel, two souls warring over inanimate cotton fabric, crisp Full HD 1080p",
    ),
    80: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing mechanical rational explanations acting as dry kindling to anger bonfire",
        "defensive logic pouring gasoline on emotional fire, explanation perceived as dismissal, crisp Full HD 1080p",
    ),
    81: (
        "OBJECT_MACRO",
        "sensitive acoustic microphone dropped onto floor with volume needle pinned at zero",
        "unheard partner, profound anguish of realizing one innermost cry is completely ignored, crisp Full HD 1080p",
    ),
    83: (
        "OBJECT_MACRO",
        "worn pair of domestic kitchen gloves lying beside pile of dishes in cold dim kitchen",
        "invisible domestic labor, deep exhaustion from years of unacknowledged unpraised sacrifice, crisp Full HD 1080p",
    ),
    84: (
        "OBJECT_MACRO",
        "heavy calendar pages flipping by rapidly accumulating gray dust over years of routine",
        "chronic neglect, years of slow emotional erosion accumulating into crisis point, crisp Full HD 1080p",
    ),
    86: (
        "OBJECT_MACRO",
        "old wedding photograph fading into yellow sepia tones beside chilled teacup on table",
        "existential fear, terror that original romantic devotion has cooled into indifferent habit, crisp Full HD 1080p",
    ),
    87: (
        "OBJECT_MACRO",
        "small bird trembling inside dark wooden box seeking crack of light to escape",
        "unvoiced insecurity, secret vulnerability too terrifying to put into explicit words, crisp Full HD 1080p",
    ),
    89: (
        "OBJECT_MACRO",
        "hand reaching across glass pane unable to touch the weeping face on the other side",
        "barrier of misunderstanding, failing to reach the genuine bleeding wound in loved one heart, crisp Full HD 1080p",
    ),
    91: (
        "OBJECT_MACRO",
        "towering red brick wall erected between two matching armchairs in living room",
        "ego defense fortress, self-protective pride preventing genuine intimate reconciliation, crisp Full HD 1080p",
    ),
    93: (
        "OBJECT_MACRO",
        "faint distress signal beacon flashing through heavy blizzard fog behind jagged mountain",
        "decoding hostile words: recognizing the desperate plea for connection behind harsh blame, crisp Full HD 1080p",
    ),
    95: (
        "OBJECT_MACRO",
        "deep underground cave chamber holding unwatered flowering lily seedling in dark",
        "unmet emotional needs, hidden tender longing for cherishing and safety awaiting recognition, crisp Full HD 1080p",
    ),
    97: (
        "OBJECT_MACRO",
        "thick thorny root system withering away instantly when warm golden spring rain falls",
        "dissolving conflict, roots of dispute evaporating once underlying sorrow is fully heard, crisp Full HD 1080p",
    ),
    99: (
        "SPLIT_COMPARISON",
        "split comparison of loud defensive loudspeaker versus clear calm reflective silver mirror",
        "blaring justification on left contrasted with serene emotional mirroring on right, crisp Full HD 1080p",
    ),
    100: (
        "OBJECT_MACRO",
        "pristine silver hand mirror reflecting weeping eyes back with total fidelity and gentleness",
        "reflective listening: reflecting partner emotions accurately without distortion or critique, crisp Full HD 1080p",
    ),
    102: (
        "OBJECT_MACRO",
        "calm water ripples catching and smoothing out turbulent waves from passing speedboat",
        "emotional regulation, calm listener presence absorbing and neutralizing reactive storms, crisp Full HD 1080p",
    ),
    103: (
        "SITUATIONAL_ACTION",
        "listener nodding slowly with deep sincerity and soft compassionate eyes",
        "somatic attunement, gentle physical signals assuring speaker they are fully received, crisp Full HD 1080p",
    ),
    105: (
        "OBJECT_MACRO",
        "heavy iron armor chestplate unbuckling and dropping onto floor revealing soft linen shirt",
        "disarming defense, partner feeling safe enough to drop protective aggression, crisp Full HD 1080p",
    ),
    106: (
        "OBJECT_MACRO",
        "single warm tear rolling down cheek catching amber lamplight in quiet room",
        "cathartic release, defensive rage giving way to genuine vulnerable grief and relief, crisp Full HD 1080p",
    ),
    108: (
        "OBJECT_MACRO",
        "closed wooden window shutters pushed wide open welcoming cool fresh evening breeze",
        "opening emotional pathways, replacing defensive interrogation with spacious curiosity, crisp Full HD 1080p",
    ),
    109: (
        "SPLIT_COMPARISON",
        "split comparison of sharp cross-examination gavel versus spacious open garden gate",
        "prosecutorial questioning on left contrasted with loving open-ended inquiry on right, crisp Full HD 1080p",
    ),
    111: (
        "OBJECT_MACRO",
        "key inscribed with question Tell Me More opening golden chest of private thoughts",
        "the golden question, inviting partner to unpack deeper layers of emotional experience, crisp Full HD 1080p",
    ),
    112: (
        "OBJECT_MACRO",
        "intricate tapestry unfurling along floor revealing rich hidden story of childhood memories",
        "rich narrative unfolding, partner discovering deep context behind contemporary triggers, crisp Full HD 1080p",
    ),
    114: (
        "OBJECT_MACRO",
        "two hands meeting across wooden table fingers gently interlacing in warm clasp",
        "physical reconciliation, tactile connection re-establishing secure emotional attachment, crisp Full HD 1080p",
    ),
    115: (
        "OBJECT_MACRO",
        "delicate balance scale holding two different colored weights in perfect horizontal harmony",
        "empathy without agreement: validating emotional pain without having to surrender personal truth, crisp Full HD 1080p",
    ),
    117: (
        "SPLIT_COMPARISON",
        "split visual of two different musical instruments cello and flute playing harmonious chord",
        "differentiating perspectives, two distinct melodies blending into unified acoustic beauty, crisp Full HD 1080p",
    ),
    119: (
        "OBJECT_MACRO",
        "artist easel holding two different landscape paintings of same mountain from west and east",
        "respecting different viewpoints, both paintings true yet capturing different angles, crisp Full HD 1080p",
    ),
    121: (
        "OBJECT_MACRO",
        "sturdy wooden fence gate with latch that opens smoothly in both directions",
        "flexible boundaries, healthy relational differentiation preserving individual autonomy, crisp Full HD 1080p",
    ),
    123: (
        "OBJECT_MACRO",
        "two distinct trees growing side by side whose branches mingle without tangling roots",
        "Kahlil Gibran pillar metaphor: standing together yet not too near like pillars of temple, crisp Full HD 1080p",
    ),
    125: (
        "OBJECT_MACRO",
        "pair of hiking boots walking side by side on mountain trail maintaining individual stride",
        "companionship in difference, traveling same journey while respecting personal rhythms, crisp Full HD 1080p",
    ),
    127: (
        "OBJECT_MACRO",
        "warm cotton blanket placed gently over partner lap in cozy reading armchair",
        "concrete expression of care, prioritizing loved one well-being over intellectual victory, crisp Full HD 1080p",
    ),
    128: (
        "SPLIT_COMPARISON",
        "split comparison of harsh courtroom verdict versus quiet embrace under warm doorway lamp",
        "sterile legalistic justice on left contrasted with transformative relational mercy on right, crisp Full HD 1080p",
    ),
    130: (
        "OBJECT_MACRO",
        "glowing candle flame burning steadily between two open journals on wooden desk",
        "shared sacred space, mutual vulnerability nurtured in quiet atmosphere of trust, crisp Full HD 1080p",
    ),
    131: (
        "OBJECT_MACRO",
        "old faded childhood doll repaired with fresh colored stitches resting on soft pillow",
        "healing old attachment wounds, tending the wounded inner child inside the adult spouse, crisp Full HD 1080p",
    ),
    133: (
        "SPLIT_COMPARISON",
        "split comparison of terrified child hiding in dark closet versus adult screaming in kitchen",
        "identifying the primal wound: adult rage revealing child terror of abandonment, crisp Full HD 1080p",
    ),
    134: (
        "OBJECT_MACRO",
        "compassionate hands holding small scared bird until its rapid heartbeat slows to calm",
        "co-regulation, nervous system calming down in presence of steady empathetic partner, crisp Full HD 1080p",
    ),
    136: (
        "OBJECT_MACRO",
        "soft green moss growing over ancient jagged boulder rounding all its sharp corners",
        "healing through time and gentleness, continuous love smoothing out historic trauma edges, crisp Full HD 1080p",
    ),
    137: (
        "OBJECT_MACRO",
        "two small seedlings planted close together intertwining trunks into single strong tree",
        "interdependent growth, two wounded souls healing together into resilient magnificent unity, crisp Full HD 1080p",
    ),
    139: (
        "OBJECT_MACRO",
        "clean tea towel carefully drying fine crystal wine glass without single smudge",
        "meticulous daily care, attending to relationship fragility with deliberate gentle touch, crisp Full HD 1080p",
    ),
    140: (
        "OBJECT_MACRO",
        "small clay incense burner with single strand of white smoke rising in draft-free room",
        "purifying domestic climate, replacing toxic blame with gentle fragrant atmosphere of peace, crisp Full HD 1080p",
    ),
    142: (
        "OBJECT_MACRO",
        "warm porcelain tea kettle boiling softly on low flame with pleasant rhythmic hum",
        "cozy hearth predictability, creating safe dependable domestic rhythms of connection, crisp Full HD 1080p",
    ),
    143: (
        "OBJECT_MACRO",
        "two handmade ceramic bowls placed neatly side by side on woven straw table mat",
        "equality and companionship, shared simple meal reflecting mutual respect and honor, crisp Full HD 1080p",
    ),
    145: (
        "OBJECT_MACRO",
        "warm wool blanket draped over couch back with soft indentation where someone rested",
        "gentle hospitality, home as an unconditional shelter of comfort and forgiveness, crisp Full HD 1080p",
    ),
    146: (
        "OBJECT_MACRO",
        "open front door glowing with warm amber hallway light welcoming traveler from storm",
        "secure attachment base, knowing home is always open with loving arms ready to embrace, crisp Full HD 1080p",
    ),
    148: (
        "OBJECT_MACRO",
        "two mugs of hot cocoa with melting marshmallows sitting on wooden windowsill in snow",
        "playful innocent connection, recovering childhood delight in shared intimate moments, crisp Full HD 1080p",
    ),
    149: (
        "OBJECT_MACRO",
        "brass oil lamp trimmed low casting intimate amber circle of light around two chairs",
        "focused relational sanctuary, darkening outside distractions to illuminate each other, crisp Full HD 1080p",
    ),
    151: (
        "OBJECT_MACRO",
        "fresh water pitcher poured into crystal bowl with clean linen towel waiting beside",
        "symbol of reconciliation, washing away grievances to restore unblemished fellowship, crisp Full HD 1080p",
    ),
    153: (
        "OBJECT_MACRO",
        "two pairs of walking shoes resting side by side on wooden entryway shoe bench",
        "shared life journey, walking companionably through worldly seasons as loyal partners, crisp Full HD 1080p",
    ),
    155: (
        "OBJECT_MACRO",
        "delicate paper lantern hanging in veranda swaying slowly in gentle night breeze",
        "fragile beauty of love, tended with mindfulness to keep light burning through squalls, crisp Full HD 1080p",
    ),
    157: (
        "OBJECT_MACRO",
        "deep slow exhalation vapor drifting into cool night air as shoulders drop in peace",
        "releasing the defensive posture, soul breathing deeply in safety of loving presence, crisp Full HD 1080p",
    ),
    158: (
        "OBJECT_MACRO",
        "open palms resting relaxed on tabletop with fingers gently curled without grasping",
        "posture of unconditional acceptance, hands ready to receive partner without demand, crisp Full HD 1080p",
    ),
    160: (
        "OBJECT_MACRO",
        "soft linen pillow receiving weary head as deep contented sigh escapes lips",
        "profound relational trust, resting knowing you are accepted in all your human imperfection, crisp Full HD 1080p",
    ),
    161: (
        "OBJECT_MACRO",
        "two cups of hot herbal tea steaming side by side under warm amber kitchen pendant lamp",
        "simple daily sacrament, shared tea marking victory of love over wounded ego pride, crisp Full HD 1080p",
    ),
    163: (
        "OBJECT_MACRO",
        "antique wooden clock ticking with reassuring slow steady pulse in quiet evening home",
        "healing cadence of time, moments of connection healing years of past misunderstanding, crisp Full HD 1080p",
    ),
    164: (
        "OBJECT_MACRO",
        "warm yellow light glowing from living room window illuminating damp night garden path",
        "beacon of love, domestic haven shining bright against cold darkness of the world, crisp Full HD 1080p",
    ),
    166: (
        "OBJECT_MACRO",
        "two jackets hanging side by side on wooden hallway coat pegs touching sleeves",
        "quiet intimacy of daily life, everyday companionship resting together in peaceful order, crisp Full HD 1080p",
    ),
    167: (
        "OBJECT_MACRO",
        "steaming teapot poured into two small ceramic cups with amber stream flowing smooth",
        "shared nourishment, pouring warmth and sweetness into daily routine of domestic life, crisp Full HD 1080p",
    ),
    169: (
        "OBJECT_MACRO",
        "soft wool slippers resting side by side on warm woven bedside rug under low light",
        "peaceful evening closure, retiring from worldly struggles into intimate mutual care, crisp Full HD 1080p",
    ),
    170: (
        "OBJECT_MACRO",
        "two pillows propped up together on wooden bedstead under soft goose down quilt",
        "shared rest, two weary travelers finding shelter in each other loving arms at night, crisp Full HD 1080p",
    ),
    172: (
        "OBJECT_MACRO",
        "gentle open palm reaching across white bedsheet resting tenderly on partner hand",
        "silent reconciliation gesture, simple touch conveying infinite forgiveness and love, crisp Full HD 1080p",
    ),
    173: (
        "OBJECT_MACRO",
        "single warm candle glowing on bedside table casting gentle dancing shadows on wall",
        "sanctuary of peace, quiet flame keeping vigil over two sleeping souls in harmony, crisp Full HD 1080p",
    ),
    175: (
        "OBJECT_MACRO",
        "golden sunrise beam touching window frame announcing fresh dawn of new understanding",
        "the morning after reconciliation, fresh beginning bathed in warm hopeful morning sun, crisp Full HD 1080p",
    ),
    176: (
        "SITUATIONAL_ACTION",
        "partner waiting patiently in quiet chair watching other take long deep breath of relief",
        "patient presence, honoring the natural rhythm of partner emotional decompression, crisp Full HD 1080p",
    ),
    178: (
        "OBJECT_MACRO",
        "taut neck muscles visibly relaxing as shoulders sink three inches lower in relief",
        "somatic proof of safety, body responding to non-judgmental presence by unclenching, crisp Full HD 1080p",
    ),
    179: (
        "SITUATIONAL_ACTION",
        "vulnerable spouse opening palms and speaking honest confession of fear and fatigue",
        "courage of openness, daring to reveal weak tender underbelly in safe emotional harbor, crisp Full HD 1080p",
    ),
    181: (
        "OBJECT_MACRO",
        "warm glowing sphere of golden light enclosing two seated companions in gentle cocoon",
        "relational field of safety, unconditional love creating sacred protective shelter, crisp Full HD 1080p",
    ),
    183: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing emotional pain burden dropping by half when listened to with empathy",
        "the empathy equation: shared grief divided by two; shared joy multiplied by two, crisp Full HD 1080p",
    ),
    185: (
        "OBJECT_MACRO",
        "sturdy crystal shield protecting tender heart from absorbing toxic emotional runoff",
        "healthy differentiation, loving deeply while maintaining personal emotional sovereign core, crisp Full HD 1080p",
    ),
    187: (
        "SPLIT_COMPARISON",
        "split comparison of bottomless toxic waste bucket versus healthy compassionate listener",
        "sponging negativity on left contrasted with grounded supportive rock on right, crisp Full HD 1080p",
    ),
    188: (
        "OBJECT_MACRO",
        "empty dry ceramic battery showing zero voltage with cracked surface in dark corner",
        "compassion fatigue warning, depleted caregiver unable to offer nourishment when empty, crisp Full HD 1080p",
    ),
    190: (
        "OBJECT_MACRO",
        "anxious child clutching mother apron strings in frantic terror of being left behind",
        "anxious attachment archetype, panic triggering demanding pursuit and interrogation, crisp Full HD 1080p",
    ),
    191: (
        "OBJECT_MACRO",
        "turtle withdrawing head completely inside impenetrable shell when touched by stick",
        "avoidant attachment archetype, retreating into silent isolation to escape perceived danger, crisp Full HD 1080p",
    ),
    193: (
        "OBJECT_MACRO",
        "heavy iron armor chestplate lined with soft velvet concealing deep weeping wound",
        "understanding armor, recognizing that hostile walls are constructed to protect fragile pain, crisp Full HD 1080p",
    ),
    194: (
        "OBJECT_MACRO",
        "compassionate eyes looking past prickly cactus needles to see delicate flower beneath",
        "empathetic perception, ceasing blame by recognizing the underlying fear in partner actions, crisp Full HD 1080p",
    ),
    196: (
        "SPLIT_COMPARISON",
        "split comparison of exhausted partner forcing fake listening versus honest gentle boundary",
        "resentful nodding on left contrasted with honest caring postponement on right, crisp Full HD 1080p",
    ),
    197: (
        "OBJECT_MACRO",
        "kettle whistling violently on high flame with steam shooting angrily from spout",
        "forced compliance danger, forcing oneself to listen when empty leading to explosive bitterness, crisp Full HD 1080p",
    ),
    199: (
        "SITUATIONAL_ACTION",
        "speaker placing hand gently on partner arm asking for thirty minutes of quiet pause",
        "healthy boundary communication, expressing desire to connect while honoring current fatigue, crisp Full HD 1080p",
    ),
    200: (
        "OBJECT_MACRO",
        "sturdy umbrella shielding small bird from torrential downpour until storm blows past",
        "protective boundary, caring refusal preserving relational goodwill and personal stamina, crisp Full HD 1080p",
    ),
    202: (
        "OBJECT_MACRO",
        "calendar page with evening tea appointment circled in warm red pencil beside clock",
        "sacred appointment, scheduling dedicated time to reconnect when both minds are rested, crisp Full HD 1080p",
    ),
    203: (
        "OBJECT_MACRO",
        "two hot cups of jasmine tea waiting on clean cedar table under soft amber lamp",
        "honoring commitment, scheduled conversation welcomed without feeling abandoned or dismissed, crisp Full HD 1080p",
    ),
    205: (
        "OBJECT_MACRO",
        "hand gently waving from doorway with warm loving smile promising quick return in peace",
        "secure temporary pause, partner understanding that stepping away is an act of preservation, crisp Full HD 1080p",
    ),
    207: (
        "OBJECT_MACRO",
        "ancient pine tree growing over old battlefield trench with green needles shading scars",
        "patience in healing, recognizing that deep relational scars heal through years of gentleness, crisp Full HD 1080p",
    ),
    209: (
        "OBJECT_MACRO",
        "warm loving hug in kitchen doorway with heads resting on each other shoulders",
        "reparative touch, warm consistent affection gradually dissolving ancient phantom insecurities, crisp Full HD 1080p",
    ),
    211: (
        "OBJECT_MACRO",
        "burning pile of old grievance lists in backyard fire pit turning to white ash",
        "forgiving the past, choosing to love the living partner here today instead of yesterday errors, crisp Full HD 1080p",
    ),
    213: (
        "OBJECT_MACRO",
        "antique brass navigational compass pointing steadily toward true north on stormy desk",
        "the relationship compass, three-station guide for navigating through marital squalls, crisp Full HD 1080p",
    ),
    215: (
        "OBJECT_MACRO",
        "two smooth river rocks nestled together in riverbed shaped by millions of water surges",
        "maturity through friction, recognizing that enduring harmony is forged through resolved conflicts, crisp Full HD 1080p",
    ),
    216: (
        "OBJECT_MACRO",
        "two hands working together to repair broken ceramic teapot with pure gold lacquer",
        "the reparative imperative, future of love determined by willingness to heal together, crisp Full HD 1080p",
    ),
    218: (
        "SITUATIONAL_ACTION",
        "practitioner holding up palm taking deep conscious breath and stopping mid-sentence",
        "the emergency pause, halting escalated argument when chest tightens before damage occurs, crisp Full HD 1080p",
    ),
    219: (
        "OBJECT_MACRO",
        "sharp iron dagger clattering onto stone floor as warrior decisively opens fingers",
        "dropping verbal weapons, refusing to speak words forged in impulsive wrath, crisp Full HD 1080p",
    ),
    221: (
        "OBJECT_MACRO",
        "two companions stepping into separate quiet rooms in home closing doors softly",
        "strategic cooling pause, physical separation allowing emotional tides to settle naturally, crisp Full HD 1080p",
    ),
    222: (
        "OBJECT_MACRO",
        "glass of cool ice water melting slowly on kitchen counter soothing the summer heat",
        "cooling down, precious interval allowing prefrontal cortex to regain moral control, crisp Full HD 1080p",
    ),
    224: (
        "OBJECT_MACRO",
        "thick legal brief of technical arguments swept decisively into wastepaper basket",
        "abandoning legalism, surrendering sterile debates over technical fault to save love, crisp Full HD 1080p",
    ),
    225: (
        "SITUATIONAL_ACTION",
        "partner looking deeply into spouse eyes and whispering sincere humble apology",
        "courageous apology: I am deeply sorry for causing you pain and making you feel alone, crisp Full HD 1080p",
    ),
    227: (
        "SPLIT_COMPARISON",
        "split comparison of arrogant unbroken ego versus humble teardrop of reconciliation",
        "petty stubborn pride on left contrasted with magnificent transformative humility on right, crisp Full HD 1080p",
    ),
    228: (
        "OBJECT_MACRO",
        "teardrop falling onto back of partner hand washing away months of accumulated suspicion",
        "cleansing tears, genuine sorrow dissolving defenses and opening gates to reconciliation, crisp Full HD 1080p",
    ),
    230: (
        "OBJECT_MACRO",
        "two pencils writing actionable agreements on shared notepad under warm table lamp",
        "constructive dialogue, collaborating on practical behavioral changes to protect future peace, crisp Full HD 1080p",
    ),
    231: (
        "OBJECT_MACRO",
        "stone staircase ascending sunlit garden hill with each step labeled with resolved problem",
        "conflict as staircase, each navigated dispute elevating relationship to higher intimacy, crisp Full HD 1080p",
    ),
    233: (
        "OBJECT_MACRO",
        "ancient Japanese kintsugi bowl shimmering with twenty-four karat gold vein lines",
        "becoming stronger at broken places, repaired relationship more magnificent than untouched porcelain, crisp Full HD 1080p",
    ),
    235: (
        "OBJECT_MACRO",
        "firm granite house foundation anchored in bedrock remaining solid in earthquake",
        "unshakable relational security, fear of abandonment banished by proven repair skills, crisp Full HD 1080p",
    ),
    237: (
        "OBJECT_MACRO",
        "two imperfect handmade pottery mugs sitting together happily on sunny morning patio",
        "embracing imperfection, loving spouse with all their quirks and flaws without resentment, crisp Full HD 1080p",
    ),
    239: (
        "OBJECT_MACRO",
        "radiant jewel box opening to reveal simple glowing orb of pure undivided presence",
        "the ultimate gift, offering unconditional undivided presence to loved one in distracted world, crisp Full HD 1080p",
    ),
    241: (
        "SPLIT_COMPARISON",
        "split comparison of screaming digital media carnival versus quiet tea ceremony between two",
        "clamoring for online stranger clicks on left versus intimate authentic communion on right, crisp Full HD 1080p",
    ),
    242: (
        "OBJECT_MACRO",
        "single warm candle glowing peacefully between two seated lovers in quiet dark room",
        "true connection, deep intimacy nurtured in sacred stillness with one precious human soul, crisp Full HD 1080p",
    ),
    244: (
        "OBJECT_MACRO",
        "busy laptop snapped shut and set aside on shelf while eyes turn fully to partner",
        "honoring priority, putting worldly busyness on pause to give undivided attention to love, crisp Full HD 1080p",
    ),
    245: (
        "OBJECT_MACRO",
        "two hands warmly cradling partner trembling hand assuring them of supreme importance",
        "affirming significance, nonverbal message: your voice and heart are my highest priority, crisp Full HD 1080p",
    ),
    247: (
        "OBJECT_MACRO",
        "steaming ceramic teapot pouring amber jasmine tea into two small matching cups",
        "ceremony of connection, sitting down together to brew tea and listen to heart stories, crisp Full HD 1080p",
    ),
    248: (
        "OBJECT_MACRO",
        "black smartphone switched off and placed inside dark cedar drawer out of sight",
        "digital detox for love, banishing screen intrusions to protect sacred domestic intimacy, crisp Full HD 1080p",
    ),
    250: (
        "SITUATIONAL_ACTION",
        "listener sitting completely still with open receptive gaze listening to long heartfelt confession",
        "uninterrupted listening, receiving entire story without interjecting single defense or advice, crisp Full HD 1080p",
    ),
    252: (
        "OBJECT_MACRO",
        "dissolving glass wall between two armchairs replaced by warm golden radiance of union",
        "vanishing distance, invisible emotional barriers melting away in warmth of understanding, crisp Full HD 1080p",
    ),
    254: (
        "OBJECT_MACRO",
        "two people walking side by side down sunlit autumn path holding hands in deep peace",
        "loving skillfully: true affection beginning with the courageous art of understanding hearts, crisp Full HD 1080p",
    ),
}

if __name__ == "__main__":
    print(f"Total bespoke beats for thuong_cho_kheo: {len(BESPOKE_BEATS)}")
    cores = [v[1][:60].lower() for v in BESPOKE_BEATS.values()]
    print(f"Unique cores count: {len(set(cores))}/{len(cores)}")
    assert len(set(cores)) == len(cores), f"Duplicates found: {len(cores) - len(set(cores))}"
    print("ALL 157 CORES ARE 100% UNIQUE!")
