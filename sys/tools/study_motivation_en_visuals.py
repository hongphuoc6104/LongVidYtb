"""English visual beat definitions (Editorial Graphic Edition) for the 48 scenes of the 13-minute Study Motivation History explainer.

Covers the full historical narrative:
- Chapter 1: The Study Desk Nightmare & The Fluctuating Inspiration Paradox (SC01-SC06)
- Chapter 2: The 300,000-Year Evolutionary Brain & Dopamine SEEKING System (SC07-SC12)
- Chapter 3: Prehistoric Era: The Natural Instinct of Learning Through Free Play (SC13-SC18)
- Chapter 4: Ancient Era: The Clay Tablet Schools of Sumer Edubba (SC19-SC24)
- Chapter 5: Feudal Era: Clan Burden & The Imperial Examination Trap (SC25-SC30)
- Chapter 6: Industrial Era: The Prussian Factory School Model (SC31-SC36)
- Chapter 7: Digital Era: The Three-Way Trap of Self, Family, and Society (SC37-SC42)
- Chapter 8: Awakening the Prehistoric Learner: 3 Keys to Love Learning Again (SC43-SC48)
"""
from __future__ import annotations

STYLE_PREFIX = (
    "Editorial 2D hand-drawn ink illustration, crisp black ink lines on warm cream off-white paper background, "
    "muted earthy ochre and slate pastel fills, generous negative space, 16:9 widescreen composition. "
    "Anonymous stick figure with large round white head, thick bold black outline, simple dot eyes, expressive line mouth, "
    "thin stick limbs, single torso. Expressive physical posture and sightlines, zero brain cutaways, "
    "no realistic faces, no text, no letters, no numbers, no watermarks, uncluttered."
)

EN_SCENE_BEATS_STUDY: dict[str, list[tuple[str, str, str]]] = {
    # ==================== CHAPTER 1: THE STUDY DESK NIGHTMARE ====================
    "SC01": [
        ("Wide late night study desk", "Wide shot of a minimalist wooden desk late at night, an open textbook lying flat under warm desk lamp light while a stick figure sits with head resting on palms", "zoom_out"),
        ("Close-up untouched blank page", "Close-up of an open notebook with pristine blank grid lines beside a black ballpoint pen resting horizontally across the page", "zoom_in"),
        ("Medium slumped posture", "Medium side view of the stick figure leaning forward over the desk, shoulders slumping heavily under an invisible weight of fatigue", "pan_right"),
        ("Over-the-shoulder stacked textbooks", "Over-the-shoulder frame looking past the stick figure toward a towering neat stack of thick course syllabi and exercise workbooks", "zoom_in"),
        ("Low-angle motionless pen", "Low-angle perspective focusing on the stationary fingertips hovering just above the pen, unable to initiate the writing motion", "pan_left"),
        ("Wide quiet guilt payoff", "Wide cinematic pull-back showing generous negative space around the illuminated desk, the student staring thoughtfully into the quiet midnight room", "zoom_out"),
    ],
    "SC02": [
        ("Wide searching for motivation", "Wide shot of the stick figure scrolling through a phone on the edge of the desk, illuminated by the pale blue mobile glow", "zoom_out"),
        ("Close-up motivational video cards", "Close-up of minimalist rectangular video thumbnail cards representing fiery speeches, leaving the viewer cold and untouched", "zoom_in"),
        ("Medium self-reproach moment", "Medium shot of the stick figure looking at their own reflection in a window pane, shaking head gently in self-blame", "pan_right"),
        ("Dramatic red brushstroke barrier", "Bold editorial frame where a single sweeping red ink brushstroke crosses out the mental cloud of self-criticism above the desk", "punch_in"),
        ("Medium calm realization posture", "Medium shot of the stick figure straightening their spine, realizing willpower was never the missing ingredient", "pan_left"),
        ("Wide liberating open window", "Wide composition showing the stick figure looking out at the open starlit horizon with a peaceful, curious expression", "zoom_out"),
    ],
    "SC03": [
        ("Wide historical lexicon library", "Wide view of a quiet 19th-century archival library with towering wooden bookshelves and tall arched windows casting soft sunlight", "zoom_out"),
        ("Close-up ancient dictionary page", "Close-up of an antique leather-bound encyclopedia page, examining early definitions of learning and craft without modern buzzwords", "zoom_in"),
        ("Medium historian stick figure", "Medium shot of a stick-figure scholar holding a brass magnifying glass over historical timelines etched in dark ink", "pan_right"),
        ("Timeline rise of study terms", "Editorial graphic timeline showing flat centuries of organic apprenticeship followed by a steep spike of school manuals after 1880", "zoom_in"),
        ("Side-by-side linguistic contrast", "Side-by-side comparison of old artisan workshop tools versus rigid modern classroom schedules laid out on parchment", "pan_left"),
        ("Wide realization of modern novelty", "Wide shot with the scholar gesturing toward the realization that forced study motivation is a modern cultural invention", "zoom_out"),
    ],
    "SC04": [
        ("Wide ancient architecture panorama", "Panoramic wide frame connecting an ancient stone megalith, an artisan ceramic kiln, and an ancient astrolabe under open sky", "zoom_out"),
        ("Close-up artisan hand chiseling", "Close-up of an ancient stick figure's hands carefully carving delicate geometric patterns into soft sandstone blocks", "zoom_in"),
        ("Medium master teaching apprentice", "Medium shot of an ancient master showing an attentive young apprentice how to mix pigments by an open clay hearth", "pan_right"),
        ("Overhead pottery wheel rotation", "Top-down view of a spinning potter's wheel shaping wet clay with fluid, effortless concentration and zero self-help slogans", "zoom_in"),
        ("Medium shared craft satisfaction", "Medium shot of the apprentice lifting the finished bowl toward the master, both nodding in quiet mutual respect", "pan_left"),
        ("Wide monument rising in sunlight", "Wide pull-back showing ancient monuments rising under sunrise, created purely through organic apprenticeship and necessity", "zoom_out"),
    ],
    "SC05": [
        ("Wide modern classroom corridor", "Wide shot of a sterile modern hallway with numbered classroom doors and rows of identical wooden student desks", "zoom_out"),
        ("Medium hunter standing in classroom", "Medium shot of a prehistoric hunter stick figure with simple fur tunic standing bewildered inside a rigid modern lecture hall", "zoom_in"),
        ("Close-up chalkboard equations", "Close-up of abstract mathematical symbols and dry text filling a chalkboard with zero visual connection to the physical earth", "pan_right"),
        ("Low-angle desk barrier", "Low-angle shot looking up past the edge of the rigid wooden desk, showing the physical constriction of sitting motionless for hours", "punch_in"),
        ("Medium staring outside window", "Medium shot of the student looking longingly through the classroom window at green tree canopies swaying in the wind", "pan_left"),
        ("Wide evolutionary friction frame", "Wide editorial split composition contrasting boundless natural savanna landscape with the four rectangular walls of the study cubicle", "zoom_out"),
    ],
    "SC06": [
        ("Wide stone road of history", "Wide cinematic panorama showing an ancient winding stone road passing four monumental gateway arches through human history", "zoom_out"),
        ("Medium traveler at milestone", "Medium shot of the stick figure standing beside an ancient stone milestone, looking down the path with renewed curiosity", "zoom_in"),
        ("Four eras visual emblems", "Editorial composition displaying four symbolic relics: a campfire spark, a clay tablet, an ink scroll, and a schoolhouse clock", "pan_right"),
        ("Close-up compass needle alignment", "Close-up of a bronze compass pointing steadily north along the historical road as warm morning sun illuminates the path", "zoom_in"),
        ("Medium invitation stride", "Medium shot of the stick figure taking confident, purposeful steps forward along the stone path toward the historical horizon", "pan_left"),
        ("Wide grand opening horizon", "Expansive wide pull-back celebrating the beginning of the 300,000-year quest to rediscover the joy of true learning", "zoom_out"),
    ],

    # ==================== CHAPTER 2: THE 300,000-YEAR BRAIN ====================
    "SC07": [
        ("Wide evolutionary savanna dawn", "Wide establishing shot of an East African savanna at dawn, golden grasses waving under an ancient acacia silhouette", "zoom_out"),
        ("Close-up 300,000-year timeline bar", "Editorial timeline across parchment: 99 percent colored in warm savanna ochre, ending in a tiny hairline blue slit of modernity", "zoom_in"),
        ("Medium hunter reading tracks", "Medium shot of a prehistoric hunter kneeling to inspect fresh animal tracks pressed into moist riverbank silt", "pan_right"),
        ("Close-up animal paw print", "Detailed close-up of a crisp animal print in the mud, showing how reading natural signs was humanity's first literacy", "punch_in"),
        ("Medium hunter looking into distance", "Medium shot of the hunter rising and gazing across the rolling plain with sharp, eager, bright eyes", "pan_left"),
        ("Wide nature as living encyclopedia", "Expansive wide shot showing the entire landscape functioning as an immersive, dynamic open-air laboratory", "zoom_out"),
    ],
    "SC08": [
        ("Wide exploratory compass hill", "Wide shot of a stick figure standing atop a grassy knoll holding a brass navigational compass toward unseen valleys", "zoom_out"),
        ("Close-up glowing spark of curiosity", "Intimate close-up of a soft golden glowing spark hovering above an open field journal, symbolizing the SEEKING instinct", "zoom_in"),
        ("Medium peering over ridgeline", "Medium shot of the stick figure shading eyes with one hand, eagerly peering over a rocky ridgeline to discover what lies beyond", "pan_right"),
        ("Editorial neural search pathway", "Editorial ink composition showing branching exploratory pathlines spreading naturally across a cream terrain map", "zoom_in"),
        ("Low-angle stride toward unknown", "Low-angle heroic angle of the stick figure stepping over boulders with dynamic energy, pursuing an intriguing scent on the breeze", "pan_left"),
        ("Wide horizon of endless questions", "Wide sweeping landscape with rolling hills inviting limitless investigation, proving the human mind was born to explore", "zoom_out"),
    ],
    "SC09": [
        ("Wide hunt for tangible clues", "Wide shot of the stick figure tracking vibrant red berries through a sun-dappled forest grove", "zoom_out"),
        ("Close-up ripening berry cluster", "Close-up of plump wild berries gleaming on a branch, providing immediate visual confirmation of discovery", "zoom_in"),
        ("Medium joyful harvesting reach", "Medium shot of the stick figure gently plucking the ripe fruit, face lighting up with genuine satisfaction", "pan_right"),
        ("Dopamine trail illustration", "Clean editorial diagram of an unbroken line connecting perception, pursuit, and tangible attainment on parchment", "punch_in"),
        ("Medium tasting sweet reward", "Medium shot of the stick figure tasting the berry, experiencing immediate neurochemical reinforcement of exploratory effort", "pan_left"),
        ("Wide complete learning loop", "Wide composition showing the stick figure resting beside the gathered basket, satisfied with the fruitful morning quest", "zoom_out"),
    ],
    "SC10": [
        ("Wide balance scale of survival", "Wide shot of a rustic wooden balance scale resting on a flat boulder under the shade of an ancient baobab tree", "zoom_out"),
        ("Close-up scale dishes comparison", "Close-up of the scale: one tray heavy with a substantial bundle of firewood, the other bearing only a dry seed husk", "zoom_in"),
        ("Medium analytical consideration", "Medium shot of the stick figure observing the tilted scale with a thoughtful, pragmatic gaze", "pan_right"),
        ("Abstract equations vanishing in fog", "Editorial visual of abstract mathematical formulas dissolving into thin morning mist while real firewood remains solid", "zoom_in"),
        ("Low-angle conservation decision", "Low-angle shot showing the stick figure deciding to conserve precious bodily energy rather than chase phantom rewards", "pan_left"),
        ("Wide natural wisdom of rest", "Wide landscape frame affirming that biological hesitation before vague, meaningless tasks is an evolved survival shield", "zoom_out"),
    ],
    "SC11": [
        ("Wide quiet lamp and open ledgers", "Wide shot of a modern desk with an antique brass lantern casting a warm amber puddle of light over closed binders", "zoom_out"),
        ("Close-up protective wooden brake", "Close-up of a carved wooden wagon brake holding a cart wheel firmly stationary on a steep slope", "zoom_in"),
        ("Medium sigh of self-compassion", "Medium shot of the student stick figure sitting back, taking a deep breath of relief and releasing chronic self-blame", "pan_right"),
        ("Dissolving scribble of guilt", "Editorial ink frame where tangled dark scribbles of guilt around the student's head evaporate into clean paper space", "punch_in"),
        ("Medium calm hands on table", "Medium shot of relaxed hands resting palms-up on the wooden surface, open and ready for a healthier approach", "pan_left"),
        ("Wide serene room atmosphere", "Wide balanced composition showing a calm, tranquil room where study frustration has been replaced by biological understanding", "zoom_out"),
    ],
    "SC12": [
        ("Wide walls folding into horizon", "Wide cinematic transition where the apartment walls fold open like a folding parchment screen into an endless savanna vista", "zoom_out"),
        ("Medium step across threshold", "Medium shot of the modern stick figure stepping across the doorway threshold onto sun-warmed grassy earth", "zoom_in"),
        ("Close-up grass touching ankles", "Close-up of blades of golden savanna grass brushing softly against the traveler's footsteps", "pan_right"),
        ("Overhead endless plain perspective", "High-angle architectural view looking down from the sky as the lone figure ventures out into the wide prehistoric world", "zoom_in"),
        ("Medium deep breath of open air", "Medium shot of the stick figure closing eyes and breathing in the fresh morning wind, leaving artificial pressure behind", "pan_left"),
        ("Wide portal to ancestral learning", "Grand panoramic pull-back opening the vast historical landscape where learning was once as natural as breathing", "zoom_out"),
    ],

    # ==================== CHAPTER 3: PREHISTORIC PLAY ====================
    "SC13": [
        ("Wide hunter-gatherer encampment", "Wide view of a peaceful prehistoric family camp at morning, conical skin shelters nestled beside a clear winding stream", "zoom_out"),
        ("Medium children playing with pebbles", "Medium shot of three small stick-figure children laughing as they skip flat pebbles across the glassy river surface", "zoom_in"),
        ("Close-up flint knapping craft", "Close-up of an elder's weathered hands striking a flint core with an antler hammer, sending crisp flakes flying", "pan_right"),
        ("Low-angle child watching elder", "Low-angle shot of a young child kneeling beside the elder, absorbing every wrist angle with intense, voluntary focus", "zoom_in"),
        ("Medium child imitating gesture", "Medium shot of the child picking up a small pebble and playfully imitating the knapping rhythm with a joyful grin", "pan_left"),
        ("Wide idyllic camp harmony", "Wide panoramic frame showing living, working, and learning flowing together in complete harmony without a single school bell", "zoom_out"),
    ],
    "SC14": [
        ("Wide hunting game in meadow", "Wide shot of children running across a sunlit meadow, playing a mock hunting game with slender wooden reeds", "zoom_out"),
        ("Close-up toy bow and blunt arrow", "Close-up of a child's hand drawing a small bent-willow toy bow aimed playfully at a woven grass target", "zoom_in"),
        ("Medium leap through tall grass", "Medium dynamic shot of a child leaping over a fallen log with agile balance, laughing aloud in pure delight", "pan_right"),
        ("Tracking hide-and-seek game", "Tracking shot moving alongside children crouching behind boulders, learning silent stalking skills through hide-and-seek", "zoom_in"),
        ("Low-angle celebratory cheer", "Low-angle shot of the children gathering together in a triumphant circle after successfully surrounding the practice target", "pan_left"),
        ("Wide unity of play and survival", "Wide panoramic view illustrating Peter Gray's insight: free play is nature's ultimate academy for masterly skill", "zoom_out"),
    ],
    "SC15": [
        ("Wide relaxed campsite afternoon", "Wide shot of adult hunter-gatherers relaxing under shade trees while children wander freely between different craft activities", "zoom_out"),
        ("Medium no testing or grading", "Medium shot of an adult weaving a reed basket, smiling warmly at a child who attempts three clumsy stitches without correction", "zoom_in"),
        ("Close-up unjudged reed basket", "Close-up of the imperfect child basket sitting proudly beside the elder's work, valued as natural experimentation", "pan_right"),
        ("Editorial crossed-out report card", "Minimalist graphic frame showing zero letter grades or red marks, replaced by warm communal belonging", "punch_in"),
        ("Medium voluntary apprentice return", "Medium shot of the child choosing to untangle the reed and try again entirely from personal intrinsic curiosity", "pan_left"),
        ("Wide culture of unconditional trust", "Wide shot capturing the profound tribal culture of autonomy, where every child's innate drive to master the world is trusted", "zoom_out"),
    ],
    "SC16": [
        ("Wide hearth fire rekindling", "Wide view of dusk settling over the camp as a boy successfully blows a glowing ember into bright crackling flame", "zoom_out"),
        ("Close-up glowing tinder nest", "Close-up of dry grass fibers igniting into a warm golden blossom of light under gentle, patient breath", "zoom_in"),
        ("Medium shared warmth and smiles", "Medium shot of camp companions gathering around the new fire, warming their hands and patting the boy's back in gratitude", "pan_right"),
        ("Overhead circle of light", "Top-down view of the golden ring of firelight illuminating happy faces, contrasting with deep purple twilight outside", "zoom_in"),
        ("Low-angle proud young firekeeper", "Low-angle heroic angle of the boy standing tall beside the hearth, feeling deeply capable and undeniably valuable", "pan_left"),
        ("Wide immediate consequence payoff", "Wide shot reinforcing the power of direct utility: when learning immediately warms your family, motivation is absolute", "zoom_out"),
    ],
    "SC17": [
        ("Wide storytelling circle under stars", "Wide frame of the entire band sitting close around the central bonfire beneath an immense canopy of swirling stars", "zoom_out"),
        ("Medium elder pointing to constellations", "Medium shot of an elder storyteller raising an arm to trace constellations in the night sky, narrating seasonal migrations", "zoom_in"),
        ("Close-up rapt child expressions", "Close-up of young stick-figure faces glowing in amber firelight, eyes wide with wonder, drinking in ancestral lore", "pan_right"),
        ("Silhouettes of animals in smoke", "Artistic smoke curls rising from the fire forming ethereal silhouettes of galloping antelopes and river courses", "zoom_in"),
        ("Medium community song rhythm", "Medium shot of the tribe clapping rhythmic hands together, embedding navigational memories into catchy oral chants", "pan_left"),
        ("Wide nocturnal universe of lore", "Expansive starry wide pull-back capturing the magical night classroom where knowledge was celebrated as communal poetry", "zoom_out"),
    ],
    "SC18": [
        ("Wide sunrise over peaceful plain", "Wide cinematic golden hour shot looking out over the prehistoric horizon as hundreds of generations thrived in balance", "zoom_out"),
        ("Close-up joyful young hunter face", "Close-up of a young hunter smiling with genuine self-assurance, confident in their relationship with the earth", "zoom_in"),
        ("Medium stone road ahead turning", "Medium shot of the path beginning to ascend toward distant stone walls and cultivated fields", "pan_right"),
        ("Distant silhouette of granaries", "Distant view of massive mud-brick storage towers and canal dikes cutting sharp artificial lines across the marsh", "zoom_in"),
        ("Low-angle transition to heavy stone", "Low-angle shot of heavy squared foundation stones replacing natural turf underfoot", "pan_left"),
        ("Wide closing of golden freedom", "Wide evocative pull-back as the golden age of self-directed learning gives way to the dawn of institutional discipline", "zoom_out"),
    ],

    # ==================== CHAPTER 4: ANCIENT SUMER EDUBBA ====================
    "SC19": [
        ("Wide mesopotamian city-state", "Wide establishing view of an ancient Sumerian city along the Euphrates, towering ziggurat overlooking canal grids and mud-brick walls", "zoom_out"),
        ("Medium temple granary gates", "Medium shot of temple priests weighing sacks of harvested barley against balance weights at the fortified storehouse gates", "zoom_in"),
        ("Close-up stylus stamping wet clay", "Close-up of a reed stylus pressing wedge-shaped cuneiform marks into a moist clay tablet to record bushel debts", "pan_right"),
        ("Rows of accounting tablets drying", "High-angle view of hundreds of drying clay tablets laid out in monotonous rows under the blistering desert sun", "zoom_in"),
        ("Medium birth of administrative need", "Medium shot of high officials consulting tablet rolls, realizing they need an army of trained scribes to maintain state control", "pan_left"),
        ("Wide arrival at the tablet house", "Wide exterior shot of the mud-brick Edubba academy where young Sumerian boys enter the first formal schoolhouse in history", "zoom_out"),
    ],
    "SC20": [
        ("Wide interior of edubba classroom", "Wide shot inside the dim mud-brick Edubba schoolroom, rows of boys sitting cross-legged on earthen floors holding clay lumps", "zoom_out"),
        ("Medium school master with birch rod", "Medium shot of the stern headmaster holding a willow cane over his shoulder, pacing between silent rows of students", "zoom_in"),
        ("Close-up trembling hand on clay", "Close-up of a young boy's shaking fingers trying to press a complex triangular wedge mark without slipping", "pan_right"),
        ("Dramatic strike on wooden desk", "Punch-in shock frame as the cane strikes the clay floor beside the boy's knees, dust puffs rising into the air", "punch_in"),
        ("Medium bowed heads under pressure", "Medium shot of student heads bowed low in sheer anxiety, repeating tedious syllabic lists from dawn till dusk", "pan_left"),
        ("Wide dread of formal schooling", "Wide grim perspective showing the birth of fear-based compliance, where physical intimidation replaced natural discovery", "zoom_out"),
    ],
    "SC21": [
        ("Wide bureaucratic schoolroom grind", "Wide view of students mechanically copying tax registers of sheep, wool, and oil rations across endless identical tablets", "zoom_out"),
        ("Close-up boring accounting lists", "Close-up of wet clay tablet filled with repetitive numbers and commodity signs, completely devoid of poetry or wonder", "zoom_in"),
        ("Medium student staring at doorway", "Medium shot of a young student gazing past the teacher's shoulder toward the bright sunny street outside", "pan_right"),
        ("Visual contrast clay vs butterfly", "Poetic visual contrast: a dull grey clay tablet on the floor while a delicate desert swallow flits through the courtyard", "zoom_in"),
        ("Low-angle scribe as tool of state", "Low-angle shot depicting the school's true purpose: forging compliant administrative cogs for temple bureaucracy", "pan_left"),
        ("Wide loss of personal meaning", "Wide stark composition emphasizing how personal curiosity was subordinated to imperial bookkeeping and institutional routine", "zoom_out"),
    ],
    "SC22": [
        ("Wide archeological excavation site", "Wide view of a modern archeological trench revealing ancient Sumerian brick foundations under sweeping desert winds", "zoom_out"),
        ("Close-up excavated 4000-year tablet", "Close-up of a cracked, authentic 4,000-year-old cuneiform tablet preserved in museum lighting, inscribed with a student's diary", "zoom_in"),
        ("Medium museum scholar translating", "Medium shot of an epigrapher translating the ancient text: 'I arrived late, I was caned; I miswrote, I was caned'", "pan_right"),
        ("Editorial echo across millennia", "Editorial ink frame blending the ancient Sumerian boy rubbing his knuckles with a modern student rubbing tired temples", "punch_in"),
        ("Medium timeless student misery", "Medium shot showing the profound human realization that academic dread is not a personal flaw but an ancient institutional scar", "pan_left"),
        ("Wide universal historical continuity", "Wide frame connecting four millennia of student suffering, proving our study exhaustion has deep archaeological roots", "zoom_out"),
    ],
    "SC23": [
        ("Wide sunset outside edubba walls", "Wide shot of the tired Sumerian boy trudging home through dusty alleyways after a grueling twelve-hour school day", "zoom_out"),
        ("Medium heavy slump of shoulders", "Medium shot of the boy clutching his clay tablet satchel, shoulders curved under the burden of chronic performance dread", "zoom_in"),
        ("Close-up bruised fingers on clay", "Close-up of ink-stained, dusty fingertips bearing cane marks, holding the brittle evidence of mandatory compliance", "pan_right"),
        ("Extinction of exploratory flame", "Minimalist visual metaphor: a bright golden spark of curiosity being smothered beneath a heavy, cold slab of grey clay", "zoom_in"),
        ("Medium gaze toward free riverbirds", "Medium shot of the student looking up at free river herons flying toward the marshes, yearning for vanished autonomy", "pan_left"),
        ("Wide birth of academic revulsion", "Wide evocative frame marking the historical moment where learning became permanently associated with duress and revulsion", "zoom_out"),
    ],
    "SC24": [
        ("Wide bridge connecting two ancient worlds", "Wide transitional panorama connecting the mud-brick ziggurat plains of Sumer to the curved tiled roofs of feudal East Asia", "zoom_out"),
        ("Medium scholar carrying heavy scroll", "Medium shot of a feudal Chinese scholar carrying a bamboo slip case over mountain passes toward an imperial academy", "zoom_in"),
        ("Close-up clan crest on scroll ribbon", "Close-up of an ornate embroidered silk ribbon bearing the ancestral seal of an entire extended family clan", "pan_right"),
        ("Growing mountain of expectations", "Editorial visualization of an immense stone mountain of family duty towering behind the lone walking scholar", "zoom_in"),
        ("Low-angle silhouette of imperial roof", "Low-angle majestic view of the curved eaves of the imperial examination hall silhouetted against an orange dusk sky", "pan_left"),
        ("Wide gateway to feudal competition", "Wide dramatic pull-back opening Chapter 5, where learning became the ultimate high-stakes gamble for family honor and survival", "zoom_out"),
    ],

    # ==================== CHAPTER 5: FEUDAL CLAN BURDEN ====================
    "SC25": [
        ("Wide feudal village study chamber", "Wide interior of an ancient wooden village study, paper lattice windows filtering late-night moonlight onto paper scrolls", "zoom_out"),
        ("Close-up oil lamp flickering low", "Close-up of an oil saucer lamp with a burning cotton wick, casting long wavering shadows across an open commentary volume", "zoom_in"),
        ("Medium scholar massaging temples", "Medium shot of a young scholar in traditional hemp robes pressing tired fingers into temples, fighting overwhelming sleep", "pan_right"),
        ("Ancestral portrait hanging behind", "High-angle perspective showing the stern, expectant ancestral family portrait hanging directly above the scholar's desk", "zoom_in"),
        ("Low-angle stacked bamboo scrolls", "Low-angle view looking past stacks of classical bamboo commentaries, conveying the suffocating volume of required texts", "pan_left"),
        ("Wide lonely weight of the night", "Wide poignant composition framing the lone scholar illuminated by the fragile oil flame amidst deep midnight shadows", "zoom_out"),
    ],
    "SC26": [
        ("Wide village gathering send-off", "Wide shot of an entire village clan gathered in front of the ancestral hall to send their brightest son to the capital exams", "zoom_out"),
        ("Medium clan elder offering pouch", "Medium shot of the village patriarch placing a pouch of pooled copper coins into the young scholar's trembling hands", "zoom_in"),
        ("Close-up tears of maternal hope", "Close-up of the scholar's mother looking up with moist eyes filled with desperate hopes of escaping crippling poverty", "pan_right"),
        ("Golden cart of official promotion", "Dream-like editorial silhouette above the crowd showing a mandarin's gilded palanquin, symbolizing royal advancement", "zoom_in"),
        ("Low-angle scholar bowing to clan", "Low-angle shot of the scholar bowing deeply to the ground before his elders, accepting the unbearable debt of honor", "pan_left"),
        ("Wide heavy golden chain of duty", "Wide frame visualizing the clan's hopes not as wings, but as an inescapable golden chain binding the student to success", "zoom_out"),
    ],
    "SC27": [
        ("Wide rote recitation hall", "Wide view of a feudal academy courtyard where fifty students sway back and forth in perfect unison, reciting classical texts", "zoom_out"),
        ("Medium rhythmic swaying recitation", "Medium shot of students rocking rhythmically on knees, eyes closed, chanting thousands of rhymed verses by heart", "zoom_in"),
        ("Close-up rigid eight-legged essay rules", "Close-up of an ink scroll displaying the rigid grammatical symmetries and forbidden words of the eight-legged essay format", "pan_right"),
        ("Master's ferule ready on lectern", "Crisp punch-in focusing on the master's wooden ferule resting on the lacquered lectern, ready to strike deviations", "punch_in"),
        ("Medium student suppressing original thought", "Medium shot of a student hesitating, biting lip, swallowing down an original question to recite the orthodox doctrine", "pan_left"),
        ("Wide cage of intellectual conformity", "Wide balanced view showing how the imperial system systematically suffocated independent curiosity to ensure political loyalty", "zoom_out"),
    ],
    "SC28": [
        ("Wide imperial examination cells", "Wide exterior shot of the colossal imperial examination compound with thousands of tiny identical brick cell cubicles", "zoom_out"),
        ("Medium scholar locked inside cell", "Medium shot of the scholar cramped inside a narrow three-foot brick booth with only two planks for desk and bench", "zoom_in"),
        ("Close-up candle burning down to wick", "Close-up of a melting wax candle dripping onto official rice paper while the candidate writes with frantic precision", "pan_right"),
        ("Overhead maze of prison-like rows", "High-angle architectural view looking straight down on the endless grid of exam cells resembling a maximum-security prison", "zoom_in"),
        ("Low-angle candidate fainting in despair", "Low-angle dramatic shot of a nearby candidate slumping forward across his ruined paper, overcome by terror and fatigue", "pan_left"),
        ("Wide three-day crucible of fear", "Wide grim panorama capturing the three-day locked ordeal where thousands competed for a microscopic fraction of winning degrees", "zoom_out"),
    ],
    "SC29": [
        ("Wide empty examination courtyard", "Wide view of the imperial courtyard after the exam, littered with discarded scrap paper and broken charcoal brushes", "zoom_out"),
        ("Medium failed scholar walking away", "Medium shot of a white-haired scholar walking away with slumped head, having failed the exam for the twentieth year", "zoom_in"),
        ("Close-up single golden name on board", "Close-up of the imperial yellow billboard listing the top three winners, while thousands of names are completely absent", "pan_right"),
        ("Editorial split: honor versus ruin", "Editorial graphic split: the tiny golden celebration banquet versus the vast grey sea of forgotten, broken aspirants", "punch_in"),
        ("Medium scholar looking at wasted youth", "Medium shot of the scholar gazing at his ink-calloused fingers, mourning decades of life sacrificed for an illusion", "pan_left"),
        ("Wide tragedy of instrumental study", "Wide tragic landscape underscoring how making learning a weapon for social mobility destroyed its innate sacred beauty", "zoom_out"),
    ],
    "SC30": [
        ("Wide bridge to industrial dawn", "Wide transition moving from the quiet tiled roofs of feudal Asia across ocean waves toward smoky European port cities", "zoom_out"),
        ("Medium clock tower rising in fog", "Medium shot of a monumental gothic clock tower emerging from thick grey coal fog in 19th-century Britain", "zoom_in"),
        ("Close-up ticking clockwork gears", "Close-up of heavy brass clockwork gears meshing together with unyielding, mechanical, rhythmic precision", "pan_right"),
        ("Silhouette of factory chimneys", "Editorial silhouette of rows of brick factory chimneys belching dark smoke into the cold dawn sky", "zoom_in"),
        ("Low-angle crowds entering gates", "Low-angle view of thousands of workers carrying lunch pails marching through iron factory gates to the whistle blow", "pan_left"),
        ("Wide dawn of the school factory", "Wide dramatic vista introducing the industrial revolution, where society decided to rebuild schoolrooms in the factory's image", "zoom_out"),
    ],

    # ==================== CHAPTER 6: INDUSTRIAL FACTORY SCHOOL ====================
    "SC31": [
        ("Wide 19th-century industrial city", "Wide establishing shot of a 19th-century industrial manufacturing metropolis, iron bridges and soot-stained brick mills", "zoom_out"),
        ("Medium factory manager consulting blueprint", "Medium shot of factory directors meeting with state ministers, reviewing plans for standardized public education", "zoom_in"),
        ("Close-up steam engine piston stroke", "Close-up of a massive polished iron steam piston pumping up and down in relentless, unvarying mechanical tempo", "pan_right"),
        ("Rows of spinning jenny operators", "High-angle perspective showing dozens of workers lined up along identical textile machines, operating like clockwork parts", "zoom_in"),
        ("Low-angle requirement for obedient labor", "Low-angle shot emphasizing the industrial state's hunger for workers who arrive on time and follow orders without debate", "pan_left"),
        ("Wide blueprint of compulsory school", "Wide blueprint composition showing the architectural birth of the modern compulsory classroom modeled on the factory floor", "zoom_out"),
    ],
    "SC32": [
        ("Wide prussian factory classroom", "Wide view of a cavernous Victorian classroom with sixty identical wooden desks bolted to floorboards in rigid straight rows", "zoom_out"),
        ("Medium teacher on elevated podium", "Medium shot of a strict schoolmaster standing on an elevated wooden dais, tapping a pointer against a wall chart", "zoom_in"),
        ("Close-up student birth year batches", "Close-up of an official state register sorting children strictly by manufacturing year rather than ability or interest", "pan_right"),
        ("Low-angle rows of identical postures", "Low-angle perspective down the aisle showing sixty identical boys sitting with hands folded flat on identical desk tops", "punch_in"),
        ("Medium child stifling a yawn", "Medium shot of an eight-year-old boy trying desperately not to move a muscle, terrified of being disciplined for fidgeting", "pan_left"),
        ("Wide industrial assembly line of minds", "Wide sweeping shot demonstrating John Taylor Gatto's critique: school turned into an assembly line to produce uniform humans", "zoom_out"),
    ],
    "SC33": [
        ("Wide brass school bell on wall", "Wide shot of the classroom wall dominated by a heavy brass electric bell linked by wires to the municipal clock tower", "zoom_out"),
        ("Close-up hammer striking bell gong", "Dynamic close-up of the metal hammer vibrating violently against the bronze bell, sending jarring sound waves outward", "punch_in"),
        ("Medium simultaneous standing drill", "Medium shot of all sixty students instantly rising from their chairs in unison at the bell strike like wind-up automata", "pan_right"),
        ("Visual equivalence bell and factory siren", "Editorial split frame showing the school bell vibrating on the left and the factory steam horn screaming on the right", "zoom_in"),
        ("Medium conditioning of time anxiety", "Medium shot of a young student clutching books, eyes fixed on the clock second-hand, conditioned to fear delay", "pan_left"),
        ("Wide choreography of obedience", "Wide panoramic frame illustrating how scheduled bell pulses dismantled natural circadian rhythms and internal curiosity", "zoom_out"),
    ],
    "SC34": [
        ("Wide suppression of individual flair", "Wide view of a teacher walking down the classroom aisle, collecting a boy's unauthorized sketchbook of beetles", "zoom_out"),
        ("Close-up drawing of beetle confiscated", "Close-up of a vibrant hand-drawn sketch of a stag beetle being placed face-down beneath a stack of standardized worksheets", "zoom_in"),
        ("Medium boy looking down in shame", "Medium shot of the young naturalist staring at his desk, feeling that his natural fascination with life is a shameful defect", "pan_right"),
        ("One-size-fits-all mold illustration", "Editorial graphic showing diverse irregular crystals being forced through an identical square steel extrusion die", "zoom_in"),
        ("Low-angle teacher lecturing conformity", "Low-angle view of the teacher commanding the class to return to page forty-two of the identical state primer", "pan_left"),
        ("Wide tragedy of the standard child", "Wide melancholic frame capturing the systematic suppression of divergent brilliance in the name of administrative order", "zoom_out"),
    ],
    "SC35": [
        ("Wide report card distribution day", "Wide classroom composition showing the teacher holding a stack of report cards adorned with red and gold stamps", "zoom_out"),
        ("Close-up red number one mark", "Close-up of a stark red failing grade stamped onto paper beside a rank number indicating last place in the cohort", "punch_in"),
        ("Medium top student gold medal", "Medium shot of the top student standing proudly with a gold medal pinned to coat, while peers look on with bitter envy", "pan_right"),
        ("The carrot and stick diagram", "Editorial diagram illustrating the introduction of extrinsic carrot-and-stick motivators to replace vanished intrinsic joy", "zoom_in"),
        ("Medium crying child hiding report", "Medium shot of a child stuffing the report card into a pocket before going home, dreading parental punishment", "pan_left"),
        ("Wide reign of artificial numbers", "Wide stark frame establishing how human worth was reduced to arbitrary numerical scales, breeding lifelong evaluation anxiety", "zoom_out"),
    ],
    "SC36": [
        ("Wide transition to 21st century", "Wide cinematic transition moving from 19th-century blackboard chalk dust into the glowing fiber-optic network of the 21st century", "zoom_out"),
        ("Medium modern student at desk", "Medium shot of a contemporary student surrounded by digital devices, but still trapped in the Prussian classroom design", "zoom_in"),
        ("Close-up identical desk and bell app", "Close-up of a smartphone screen buzzing with a digital school timetable alarm that mirrors the 1880 factory bell", "pan_right"),
        ("Dual inheritance of shame and rote", "Editorial montage combining ancient Sumerian clay canes, feudal examination anxiety, and factory bells around the desk", "zoom_in"),
        ("Low-angle student overwhelmed by noise", "Low-angle shot of the student holding head with both hands as digital notifications flash alongside homework reminders", "pan_left"),
        ("Wide entering the digital crisis", "Wide dramatic pull-back opening Chapter 7: the perfect storm of ancestral mismatch, parental guilt, and algorithmic distraction", "zoom_out"),
    ],

    # ==================== CHAPTER 7: THE DIGITAL TRAP ====================
    "SC37": [
        ("Wide contemporary student room night", "Wide establishing shot of a modern bedroom at 11 PM, desk illuminated by dual monitors, desk lamp, and phone screen", "zoom_out"),
        ("Close-up homework notification flood", "Close-up of a laptop screen showing multiple tabs of online learning portals, overdue assignment banners, and grades", "zoom_in"),
        ("Medium student paralyzed between choices", "Medium side view of the student sitting frozen between the glowing phone in left hand and the heavy biology book on right", "pan_right"),
        ("Three-directional arrow trap graphic", "Editorial graphic showing three dark arrows labeled Self-Blame, Family Expectation, and Social Race converging on the desk", "punch_in"),
        ("Low-angle exhaustion in the blue glow", "Low-angle shot looking up at the student's weary face illuminated by cold monitor light, feeling totally cornered", "pan_left"),
        ("Wide paralysis of modern learner", "Wide expansive frame with ample negative space emphasizing the profound isolation and paralysis of modern study guilt", "zoom_out"),
    ],
    "SC38": [
        ("Wide self-determination pillars", "Wide architectural frame displaying three classical Greek pillars labeled Autonomy, Competence, and Relatedness", "zoom_out"),
        ("Medium crumbling pillar of autonomy", "Medium shot of the Autonomy pillar cracking and crumbling as chains of mandated syllabi pull tight around it", "zoom_in"),
        ("Close-up crushed competence metric", "Close-up of the Competence base being chipped away by constant graded comparisons and hyper-competitive rank lists", "pan_right"),
        ("Severed bridge of connection", "Editorial visual of a severed stone bridge symbolizing the complete isolation of studying alone in competitive panic", "zoom_in"),
        ("Medium student amidst the ruins", "Medium shot of the student kneeling among the fragments of intrinsic drive, wondering where the desire to learn went", "pan_left"),
        ("Wide psychological diagnosis frame", "Wide balanced view showing Deci & Ryan's fundamental diagnosis: when autonomy and connection die, motivation naturally vanishes", "zoom_out"),
    ],
    "SC39": [
        ("Wide family dinner table tension", "Wide shot of a dining room table where parents review a test score paper while the student sits with eyes cast downward", "zoom_out"),
        ("Medium parental love distorted as fear", "Medium shot of parents' earnest faces, their genuine love and anxiety for their child's future coming across as harsh pressure", "zoom_in"),
        ("Close-up neighbor's child comparison", "Close-up of the parents tapping a phone screen displaying a cousin's prestigious university acceptance letter", "pan_right"),
        ("Invisible backpack of debt", "Editorial visual metaphor: an immense backpack filled with family sacrifices and tuition loans strapped onto the student's back", "punch_in"),
        ("Low-angle student shrinking in chair", "Low-angle shot of the student shrinking into their seat, feeling that a bad test mark is a betrayal of the entire family", "pan_left"),
        ("Wide suffocating family burden", "Wide frame capturing the painful tragedy of filial guilt, where parental devotion accidentally suffocates intrinsic curiosity", "zoom_out"),
    ],
    "SC40": [
        ("Wide social media feed of glory", "Wide shot of a giant smartphone screen towering like a billboard, displaying viral reels of prodigies and perfect study vlogs", "zoom_out"),
        ("Medium student scrolling in darkness", "Medium shot of the student sitting in darkness, watching curated highlight reels of sixteen-hour daily study routines", "zoom_in"),
        ("Close-up artificial hustle aesthetic", "Close-up of pastel highlighters, digital timers counting down, and competitive study-with-me streams generating chronic inadequacy", "pan_right"),
        ("The endless rat race treadmill", "Editorial illustration of stick figures running frantically on an accelerating conveyor belt chasing an unreachable golden diploma", "zoom_in"),
        ("Low-angle feeling forever behind", "Low-angle view of the student looking up at the towering scoreboard of societal prestige, feeling permanently inadequate", "pan_left"),
        ("Wide madness of hyper-competition", "Wide expansive composition condemning the hyper-optimized rat race that turned education into an anxiety-driven sport", "zoom_out"),
    ],
    "SC41": [
        ("Wide battle of stimuli at desk", "Wide shot of the study desk staged like a dramatic battlefield between an open textbook on the left and a smartphone on the right", "zoom_out"),
        ("Close-up glowing slot machine screen", "Close-up of the phone screen bursting with colorful notification badges, variable rewards, and instant micro-dopamine hits", "zoom_in"),
        ("Close-up dry paragraph of text", "Close-up of dense black textbook print that requires fifteen minutes of sustained concentration before yielding any payoff", "pan_right"),
        ("Prehistoric hunter facing slot machine", "Humorous and tragic editorial juxtaposition: a prehistoric hunter standing bewildered before a high-tech Las Vegas slot machine", "punch_in"),
        ("Medium hand pulled toward screen", "Medium shot of the student's hand drifting almost involuntarily toward the phone, hijacked by hyper-stimulatory design", "pan_left"),
        ("Wide uneven evolutionary contest", "Wide frame making clear that the student is not weak-willed; their ancient brain is outmatched by billion-dollar attention algorithms", "zoom_out"),
    ],
    "SC42": [
        ("Wide sunrise breaking through blinds", "Wide shot of the student's room as soft morning light pierces horizontal window blinds, illuminating the dust motes in the air", "zoom_out"),
        ("Medium student releasing the self-blame", "Medium shot of the student taking both hands off their face, taking a deep breath of forgiveness and looking directly forward", "zoom_in"),
        ("Close-up tears giving way to clarity", "Close-up of the student's eyes clearing, seeing that the centuries-old system was broken, not their personal mind or soul", "pan_right"),
        ("Dissolving the four historical ghosts", "Editorial composition showing the Sumerian cane, feudal scroll, Prussian clock, and phone notification dissolving into white air", "punch_in"),
        ("Medium standing up tall with spine straight", "Medium shot of the student rising from the chair with dignity, ready to reclaim ownership of their learning journey", "pan_left"),
        ("Wide threshold of rebirth", "Wide hopeful horizon pull-back setting the stage for Chapter 8: the practical blueprint to awaken the ancient curious learner within", "zoom_out"),
    ],

    # ==================== CHAPTER 8: 3 KEYS TO REAWAKEN THE LEARNER ====================
    "SC43": [
        ("Wide inner savanna sunrise", "Wide panoramic frame where the modern room blends harmoniously with golden savanna dawn, the student standing at the center", "zoom_out"),
        ("Medium ancestral ally silhouette", "Medium shot of the prehistoric hunter stick figure standing shoulder-to-shoulder with the modern student, smiling warmly", "zoom_in"),
        ("Three golden keys on table", "Clean editorial composition of three radiant golden keys resting on a clean wooden table: Autonomy, Micro-Quests, Community", "pan_right"),
        ("Close-up picking up first key", "Close-up of the student's fingers lifting the first key of Micro-Quests, feeling its tangible, solid weight", "zoom_in"),
        ("Medium confident smile returning", "Medium shot of the student looking at the open desk with genuine excitement, seeing it no longer as a prison but as an expedition", "pan_left"),
        ("Wide launchpad of lifelong adventure", "Wide balanced pull-back celebrating the return of human curiosity as a lifelong joyful adventure of the mind", "zoom_out"),
    ],
    "SC44": [
        ("Wide clearing the desk battlefield", "Wide shot of the student deliberately sweeping away unnecessary clutter, leaving only a single notepad and fountain pen", "zoom_out"),
        ("Close-up twenty-minute sand timer", "Close-up of a minimalist wooden twenty-minute sand timer turned over, golden grains trickling down with calm focus", "zoom_in"),
        ("Medium writing single clear mission", "Medium shot of the student writing a single tangible mission card: 'Master three steps of cellular respiration'", "pan_right"),
        ("Small game hunt metaphor", "Editorial graphic showing the massive textbook transforming into a small, approachable hunting quest that can be completed before lunch", "punch_in"),
        ("Medium ticking off completed box", "Medium shot of the student making a crisp black checkmark in the box twenty minutes later, feeling a surge of real dopamine", "pan_left"),
        ("Wide momentum of short sprints", "Wide frame demonstrating Barbara Oakley's principle: small, tangible victories trigger the brain's natural SEEKING momentum", "zoom_out"),
    ],
    "SC45": [
        ("Wide creative sketching on large paper", "Wide view of the student leaning over a large sheet of butcher paper, drawing colorful mind maps and flow diagrams with markers", "zoom_out"),
        ("Close-up playful trial-and-error arrow", "Close-up of a hand drawing a funny cartoon sketch to explain an physics concept, crossing out an error and laughing freely", "zoom_in"),
        ("Medium hands-on building moment", "Medium shot of the student assembling a quick cardboard model to test a mechanical idea, learning directly through fingers", "pan_right"),
        ("Shattered cage of standardized rules", "Editorial illustration of a broken wire birdcage, symbolizing the liberation of personal, idiosyncratic learning styles", "punch_in"),
        ("Medium joy of personal discovery", "Medium shot of the student leaning back, pointing at their own diagram with a glowing lightbulb moment of genuine comprehension", "pan_left"),
        ("Wide reclaiming autonomy in action", "Wide composition proving Carol Dweck and Deci's insight: when you own the process and celebrate mistakes, study becomes play", "zoom_out"),
    ],
    "SC46": [
        ("Wide modern campfire circle of friends", "Wide shot of three student friends sitting around a small wooden coffee table with tea mugs, discussing an idea eagerly", "zoom_out"),
        ("Medium student explaining concept", "Medium shot of our stick figure gesturing animatedly with hands, explaining a historical insight to an engaged, nodding friend", "zoom_in"),
        ("Close-up shared laughter over discovery", "Close-up of friends laughing together as a difficult concept suddenly clicks into simple, elegant common sense", "pan_right"),
        ("Echo of ancient tribal hearth", "Editorial blend showing the modern tea table overlapping with the ancient tribal bonfire, keeping the social learning flame alive", "zoom_in"),
        ("Medium mutual encouragement high-five", "Medium shot of two friends clapping hands in solidarity, turning competitive isolation into cooperative celebration", "pan_left"),
        ("Wide warmth of collaborative truth", "Wide rich composition emphasizing that knowledge was never meant to be hoarded in fear, but shared like bread and stories", "zoom_out"),
    ],
    "SC47": [
        ("Wide transformation of the study space", "Wide shot of the newly organized desk bathed in soft natural morning sunlight, clean wooden surfaces, green potted plant", "zoom_out"),
        ("Close-up phone resting in drawer", "Close-up of the smartphone placed peacefully inside a closed desk drawer across the room, silenced and out of sight", "zoom_in"),
        ("Medium warm desk lamp lighting up", "Medium shot of the student reaching out to click on the warm brass desk lamp, illuminating a clean open notepad", "pan_right"),
        ("Expedition desk metaphor", "Editorial visual metaphor: the study desk depicted as an explorer's wooden campaign table equipped with maps and binoculars", "punch_in"),
        ("Medium taking comfortable seat", "Medium shot of the student sitting down with relaxed shoulders, balanced breath, and quiet, steady inner readiness", "pan_left"),
        ("Wide sanctuary of natural curiosity", "Wide harmonious frame celebrating the study desk transformed from a place of dread into a personal sanctuary of wonder", "zoom_out"),
    ],
    "SC48": [
        ("Wide closing the full narrative loop", "Wide cinematic pull-back of the bright sunlit room as the student sits peacefully before the open book, ready to begin", "zoom_out"),
        ("Close-up pen gliding across paper", "Intimate close-up of the fountain pen tip smoothly gliding across smooth cream paper, leaving clean, confident black ink lines", "zoom_in"),
        ("Medium peaceful focused expression", "Medium shot of the student's face with a quiet, grounded smile, deeply immersed in the pure joy of understanding", "pan_right"),
        ("Ancestral hunter reflection in glass", "Medium reflection in the window glass showing the ancient hunter smiling in harmonious approval beside the modern student", "pan_left"),
        ("Low-angle steady momentum", "Low-angle perspective capturing the effortless, calm momentum of someone who studies not for show, but for the love of truth", "punch_in"),
        ("Wide final master frame", "Expansive cinematic pull-back as golden light fills the entire 16:9 canvas, completing the 13-minute journey through human history", "zoom_out"),
    ],
}


def get_scene_beats_v2(scene_id: str, count: int = 6) -> list[tuple[str, str, str]]:
    """Return `count` distinct (framing, english_description, camera_effect) tuples for `scene_id`."""
    base = list(EN_SCENE_BEATS_STUDY[scene_id])
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
        idx = len(base) - len(EN_SCENE_BEATS_STUDY[scene_id])
        candidate = extra_angles[idx % len(extra_angles)]
        if base and candidate[2] == base[-1][2]:
            alt_effect = "pan_right" if candidate[2] != "pan_right" else "zoom_in"
            candidate = (candidate[0], candidate[1], alt_effect)
        base.append(candidate)
    return base[:count]


def get_scene_beats(scene_id: str, count: int = 6) -> list[tuple[str, str]]:
    """Backward-compatible helper returning (framing, english_description) 2-tuples."""
    return [(f, d) for f, d, _ in get_scene_beats_v2(scene_id, count)]
