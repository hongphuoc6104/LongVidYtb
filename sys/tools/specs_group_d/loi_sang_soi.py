"""Bespoke Explainer Prompt Mapping for loi_sang_soi (157 new beats).

Every beat index maps to: (explainer_type, core_clause, details)
Guarantees 100% unique core subjects (b["prompt"].split(",")[1].strip()[:60].lower())
with zero template cycling and zero generic fallbacks.
"""

PREFIX = "Warm golden-hour spiritual parable illustration,"
SUFFIX = ", zero text overlay, no watermarks"

BESPOKE_BEATS = {
    1: (
        "SITUATIONAL_ACTION",
        "solitary biblical sower walking purposefully across a vast plowed field at dawn",
        "flowing coarse linen tunic, sweeping panoramic perspective, rich Rembrandt chiaroscuro, crisp Full HD 1080p",
    ),
    2: (
        "OBJECT_MACRO",
        "macro close-up of a weathered coarse burlap seed satchel slung across sower shoulder",
        "rough woven hemp fiber texture, wooden toggle clasp, warm golden morning light, crisp Full HD 1080p",
    ),
    4: (
        "OBJECT_MACRO",
        "radiant golden wheat grains suspended mid-air caught in diagonal morning sunbeams",
        "luminous floating seeds, airborne particles glistening like amber gems, crisp Full HD 1080p",
    ),
    5: (
        "OBJECT_MACRO",
        "macro view of individual golden grain kernels descending toward dry furrowed earth",
        "delicate gravitational descent, particles touching powdery brown loam, crisp Full HD 1080p",
    ),
    7: (
        "OBJECT_MACRO",
        "flock of glossy black ravens swooping down aggressively onto hard-packed dirt pathway",
        "sharp beaks pecking away scattered grains, agitated dark wings fluttering, crisp Full HD 1080p",
    ),
    8: (
        "OBJECT_MACRO",
        "completely bare barren hardened path with no remaining trace of fallen wheat seeds",
        "dry cracked earth surface showing zero organic growth, harsh midday sunlight, crisp Full HD 1080p",
    ),
    10: (
        "SPLIT_COMPARISON",
        "split comparison of premature green sprout on left versus scorched withered shoot on right",
        "tender sprout dying under blistering desert sun, shallow rocky soil failure, crisp Full HD 1080p",
    ),
    11: (
        "MECHANISM_CUTAWAY",
        "mechanism cutaway showing fragile seedling roots blocked by solid limestone shelf",
        "pale root tips bending sideways against impenetrable rock barrier without subterranean moisture, crisp Full HD 1080p",
    ),
    13: (
        "OBJECT_MACRO",
        "golden seeds landing amidst sinister thicket of tangled thorny briars and wild thistles",
        "sharp wooden bramble spikes surrounding innocent seeds, ominous cast shadows, crisp Full HD 1080p",
    ),
    14: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing invasive thorn vines strangling young tender sapling stems",
        "spiral constricting briars choking botanical sap flow, leaves suffocating in shadows, crisp Full HD 1080p",
    ),
    16: (
        "OBJECT_MACRO",
        "golden wheat seed resting peacefully within rich crumbly dark humic soil",
        "moist organic earth texture, subterranean warmth welcoming seed into gentle darkness, crisp Full HD 1080p",
    ),
    18: (
        "STEP_ENUMERATION",
        "sequential enumeration diorama displaying thirty-fold sixty-fold and hundred-fold wheat sheaves",
        "tripartite bountiful harvest comparison, golden stalks bending heavily under rich grain, crisp Full HD 1080p",
    ),
    20: (
        "STEP_ENUMERATION",
        "allegorical diorama exhibiting four distinct soil profiles representing human heart conditions",
        "four quadrants: trampled pathway, rocky ledge, thorny briars, fertile humus loam, crisp Full HD 1080p",
    ),
    22: (
        "OBJECT_MACRO",
        "hard-packed footpath trampled stone-hard by thousands of passing marching boots",
        "impermeable clay surface polished smooth by relentless pedestrian traffic, crisp Full HD 1080p",
    ),
    23: (
        "OBJECT_MACRO",
        "macro view of compressed dirt roadbed resisting steel plow blade without a scratch",
        "unyielding compacted mineral crust, complete absence of aeration or moisture, crisp Full HD 1080p",
    ),
    25: (
        "SPLIT_COMPARISON",
        "split portrayal of cynical detached listener on left versus attentive humble student on right",
        "crossed arms and cynical glare contrasted with open receptive posture and listening eyes, crisp Full HD 1080p",
    ),
    26: (
        "OBJECT_MACRO",
        "imposing invisible glass wall erected between human speaker and indifferent crowd",
        "cold transparent barrier deflecting sincere words like harmless raindrops, crisp Full HD 1080p",
    ),
    28: (
        "MECHANISM_CUTAWAY",
        "anatomical brain cutaway showing superficial information bouncing off cerebral cortex",
        "words failing to penetrate past sensory surface into emotional heart center, crisp Full HD 1080p",
    ),
    29: (
        "OBJECT_MACRO",
        "parched clay soil slab lacking even the tiniest hairline fracture for water absorption",
        "sealed terra-cotta texture, precious water beads rolling off surface without sinking, crisp Full HD 1080p",
    ),
    31: (
        "OBJECT_MACRO",
        "solitary seed lying exposed on sun-baked stone without single protecting drop of dew",
        "brutal thermal exposure, vulnerable grain kernel dehydrating under unforgiving sky, crisp Full HD 1080p",
    ),
    32: (
        "OBJECT_MACRO",
        "cold twilight shadow creeping across desolate empty roadway after sower departs",
        "melancholic evening chill descending upon forgotten wasted potential, crisp Full HD 1080p",
    ),
    34: (
        "OBJECT_MACRO",
        "high-speed macro capture of raven beak snatching single seed in fraction of a second",
        "instantaneous predatory loss, black feather sheen reflecting quick opportunistic theft, crisp Full HD 1080p",
    ),
    35: (
        "OBJECT_MACRO",
        "bare patch of hard dirt showing only solitary avian footprint where seed once rested",
        "poignant visual emptiness, complete eradication of spiritual opportunity, crisp Full HD 1080p",
    ),
    37: (
        "OBJECT_MACRO",
        "harsh blue digital screen flickering rapidly in dark room illuminating vacant human eyes",
        "modern superficial distraction, endless feed of flashing notifications stealing attention, crisp Full HD 1080p",
    ),
    39: (
        "SPLIT_COMPARISON",
        "split comparison of chaotic fragmented modern attention versus calm unified contemplation",
        "scattered red alert icons on left versus single steady candle flame on right, crisp Full HD 1080p",
    ),
    41: (
        "OBJECT_MACRO",
        "empty hollow bronze bell hanging motionless inside neglected abandoned belfry",
        "resonant interior void, total spiritual numbness following prolonged mindless distraction, crisp Full HD 1080p",
    ),
    43: (
        "OBJECT_MACRO",
        "wilted dried seed husk blowing away like dust across vast windy limestone plateau",
        "mournful loss of uncultivated truth, transient particle vanishing into oblivion, crisp Full HD 1080p",
    ),
    45: (
        "MECHANISM_CUTAWAY",
        "geological cutaway revealing paper-thin topsoil veneer over massive limestone boulder",
        "deceptive superficial layer, dark soil only one centimeter deep over impassable rock, crisp Full HD 1080p",
    ),
    46: (
        "OBJECT_MACRO",
        "shallow earthen tray holding tiny sprinkling of dirt atop solid marble slab",
        "artificial gardening display incapable of sustaining deep botanical root growth, crisp Full HD 1080p",
    ),
    48: (
        "OBJECT_MACRO",
        "portrait of youthful enthusiast with eyes ablaze with sudden ungrounded excitement",
        "intense fleeting passion, bright wide eyes illuminated by temporary flare of novelty, crisp Full HD 1080p",
    ),
    49: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing sudden straw flash fire flaring high into air then dying immediately",
        "pyrotechnic combustion curve of emotional hype lacking enduring fuel substrate, crisp Full HD 1080p",
    ),
    51: (
        "OBJECT_MACRO",
        "two tender green cotyledon leaves shooting upward with premature haste",
        "hyper-accelerated vertical sprout, fragile pale green stem stretching toward sky, crisp Full HD 1080p",
    ),
    52: (
        "OBJECT_MACRO",
        "admiring onlookers applauding decorative flower pot before true summer heat arrives",
        "superficial early praise celebrating deceptive outward appearance before trials, crisp Full HD 1080p",
    ),
    54: (
        "SPLIT_COMPARISON",
        "split view of imaginary smooth victory highway versus real mountain obstacle trail",
        "naive rose-tinted expectation on left contrasted with brutal jagged cliffs on right, crisp Full HD 1080p",
    ),
    55: (
        "OBJECT_MACRO",
        "fragile paper crown dissolving under the very first drop of summer thunderstorm rain",
        "illusory triumph evaporating at onset of genuine adversity, crisp Full HD 1080p",
    ),
    57: (
        "OBJECT_MACRO",
        "macro view of delicate white root tip crushing against cold subterranean rock surface",
        "botanical frustration, tender growth aborted by unyielding hidden mineral obstruction, crisp Full HD 1080p",
    ),
    58: (
        "OBJECT_MACRO",
        "cross-section of dry rocky bedrock completely devoid of subterranean water veins",
        "arid stone strata, thirsty mineral fissures holding zero moisture reserves, crisp Full HD 1080p",
    ),
    60: (
        "OBJECT_MACRO",
        "baking heat radiating from sun-drenched limestone slab scorching exposed root hairs",
        "thermal shock, delicate subterranean biology cooking on superheated subterranean pan, crisp Full HD 1080p",
    ),
    61: (
        "OBJECT_MACRO",
        "macro shot of curled shriveled green leaves turning yellow and limp under heat",
        "cellular turgor collapse, stem collapsing downward against hot dry gravel, crisp Full HD 1080p",
    ),
    63: (
        "SPLIT_COMPARISON",
        "split comparison of thrilling opening carnival fireworks versus solitary disciplined study desk",
        "fleeting emotional excitement on left versus steady unglamorous daily habit on right, crisp Full HD 1080p",
    ),
    65: (
        "OBJECT_MACRO",
        "cold extinguished campfire revealing only grey ash and unburnt damp kindling",
        "premature enthusiasm dying out completely without leaving lasting embers, crisp Full HD 1080p",
    ),
    67: (
        "OBJECT_MACRO",
        "fragile dried straw stalk snapping beneath heavy leather boot of passing traveler",
        "brittle dried seedling reduced to crushed yellow debris on rocky ground, crisp Full HD 1080p",
    ),
    69: (
        "CAUSE_EFFECT_DIAGRAM",
        "cause-and-effect architectural diagram linking deep subterranean anchor to storm survival",
        "tall cedar tree with deep taproot standing firm versus shallow sapling uprooted by wind, crisp Full HD 1080p",
    ),
    71: (
        "OBJECT_MACRO",
        "healthy young green wheat shoot thriving happily alongside dark fertile garden furrow",
        "emerald foliage glistening with morning moisture, promising early botanical vitality, crisp Full HD 1080p",
    ),
    72: (
        "OBJECT_MACRO",
        "sturdy green stalk standing erect with firm vascular turgor in crisp morning air",
        "robust young plant tissue displaying natural vigor and botanical promise, crisp Full HD 1080p",
    ),
    74: (
        "OBJECT_MACRO",
        "wide panoramic view of sunlit horizon offering endless fertile sky to young crop",
        "limitless developmental potential bathed in warm golden dawn radiance, crisp Full HD 1080p",
    ),
    75: (
        "OBJECT_MACRO",
        "dark spiky wild blackberry bramble tendrils crawling silently across garden border",
        "creeping botanical menace, prickly purple vines advancing toward young wheat, crisp Full HD 1080p",
    ),
    77: (
        "OBJECT_MACRO",
        "macro view of aggressive thorn clusters multiplying with terrifying vegetative vigor",
        "dense thicket of sharp hooked spines forming impenetrable suffocating thicket, crisp Full HD 1080p",
    ),
    78: (
        "OBJECT_MACRO",
        "coiling thorn vine wrapping tightly around green wheat stem like predatory python",
        "vegetative strangulation, thorny tendril cutting into soft green bark, crisp Full HD 1080p",
    ),
    80: (
        "OBJECT_MACRO",
        "stack of unpaid financial ledgers and urgent overdue notices weighing down work desk",
        "heavy ledger books with red balance marks, suffocating mundane economic anxieties, crisp Full HD 1080p",
    ),
    81: (
        "OBJECT_MACRO",
        "hourglass filled with running coins instead of sand slowly burying a small seedling",
        "materialistic fixation suffocating spiritual purpose under metallic monetary weight, crisp Full HD 1080p",
    ),
    83: (
        "OBJECT_MACRO",
        "bottomless golden goblet that can never be filled no matter how much wine is poured",
        "insatiable consumerist greed, hollow golden vessel leaking through hidden base, crisp Full HD 1080p",
    ),
    84: (
        "SPLIT_COMPARISON",
        "split comparison of exhausting status hamster wheel versus peaceful contemplative garden",
        "frantic corporate rat race on left versus serene seated reflection under fig tree on right, crisp Full HD 1080p",
    ),
    86: (
        "OBJECT_MACRO",
        "dark suffocating canopy of overgrown briars completely shutting out solar rays",
        "dim gloomy botanical underworld beneath thorns where sunlight never penetrates, crisp Full HD 1080p",
    ),
    87: (
        "OBJECT_MACRO",
        "macro shot of sharp thorn piercing tender vein of pale green wheat leaf",
        "chlorophyll drainage, sharp botanical thorn drawing sap from strangled wheat shoot, crisp Full HD 1080p",
    ),
    89: (
        "OBJECT_MACRO",
        "pale sickly wheat stalk surviving in perpetual twilight unable to produce grain heads",
        "etiolated yellowing stem stunted beneath heavy shade of predatory thistles, crisp Full HD 1080p",
    ),
    91: (
        "OBJECT_MACRO",
        "glowing ideal blueprint scroll forgotten and gathering cobwebs under pile of ledgers",
        "lost noble dreams buried beneath daily commercial transactions and pragmatic worries, crisp Full HD 1080p",
    ),
    93: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing human vital life force splintered into fifty competing trivial demands",
        "diffused energy vector map illustrating complete loss of concentrated core purpose, crisp Full HD 1080p",
    ),
    95: (
        "OBJECT_MACRO",
        "gilded carriage wheel sinking deeply into sticky mud of vanity and competition",
        "golden chariot trapped in quagmire, hollow pursuit of social prestige draining life, crisp Full HD 1080p",
    ),
    97: (
        "OBJECT_MACRO",
        "single fallen wheat grain lying crushed beneath heavy golden ingot in vault",
        "tragic spiritual sacrifice, invaluable living potential traded for dead metal bullion, crisp Full HD 1080p",
    ),
    99: (
        "OBJECT_MACRO",
        "macro profile of rich crumbly dark humic topsoil aerated and soft as velvet",
        "fertile earth aggregates rich with organic matter, earthy dark chocolate tones, crisp Full HD 1080p",
    ),
    100: (
        "OBJECT_MACRO",
        "neat stone wall constructed from jagged field stones patiently cleared from garden",
        "diligent agricultural labor, harmful rocks removed to build protective boundary, crisp Full HD 1080p",
    ),
    102: (
        "OBJECT_MACRO",
        "wide unobstructed garden bed ready for planting with smooth aerated soil beds",
        "ideal horticultural sanctuary, clean furrows stretching open under gentle spring sky, crisp Full HD 1080p",
    ),
    103: (
        "OBJECT_MACRO",
        "soft spring shower droplets gently irrigating deep furrows of fertile black earth",
        "nourishing raindrops sinking instantly into thirsty loam, misty atmospheric warmth, crisp Full HD 1080p",
    ),
    105: (
        "SPLIT_COMPARISON",
        "split portrayal of arrogant know-it-all on left versus deeply humble listener on right",
        "smug condescension contrasted with genuine humility and eager receptive attentiveness, crisp Full HD 1080p",
    ),
    106: (
        "OBJECT_MACRO",
        "open earthen bowl held with both hands catching pure rainwater from spring sky",
        "vessel of humble receptivity, ceramic bowl gathering every precious drop without spilling, crisp Full HD 1080p",
    ),
    108: (
        "MECHANISM_CUTAWAY",
        "mechanism cutaway of vigorous white taproot plunging deep into subterranean aquifer",
        "botanical hydration network, thriving root hairs absorbing minerals from rich moist loam, crisp Full HD 1080p",
    ),
    109: (
        "OBJECT_MACRO",
        "luxuriant network of lateral rootlets anchoring seedling securely in dark earth",
        "intricate subterranean root architecture providing unwavering stability and nourishment, crisp Full HD 1080p",
    ),
    111: (
        "OBJECT_MACRO",
        "healthy thick wheat stem crowned with lush emerald green leaves drinking morning light",
        "photosynthetic triumph, vigorous botanical growth thriving in fertile environment, crisp Full HD 1080p",
    ),
    112: (
        "OBJECT_MACRO",
        "magnificent heavy wheat head bending gracefully with thirty plump golden kernels",
        "bountiful first tier harvest, golden bearded wheat ear glistening in afternoon sun, crisp Full HD 1080p",
    ),
    114: (
        "OBJECT_MACRO",
        "dense cluster of golden wheat sheaves yielding sixty-fold harvest in autumn light",
        "multiplied abundance, rich field of heavy grain rippling in warm harvest breeze, crisp Full HD 1080p",
    ),
    115: (
        "OBJECT_MACRO",
        "endless golden ocean of ripe wheat rippling under wind yielding hundred-fold bounty",
        "miraculous agricultural triumph, vast sea of grain glowing like liquid gold at sunset, crisp Full HD 1080p",
    ),
    117: (
        "SPLIT_COMPARISON",
        "split comparison of single humble seed planted versus mountain of golden loaves baked",
        "tiny starting kernel on left contrasted with overflowing bakery banquet on right, crisp Full HD 1080p",
    ),
    119: (
        "OBJECT_MACRO",
        "overflowing wooden harvest granary filled to the rafters with glistening clean wheat",
        "abundant agricultural prosperity, wooden bins brimming with nourishing grain, crisp Full HD 1080p",
    ),
    121: (
        "OBJECT_MACRO",
        "joyful farming family sharing warm freshly baked sourdough bread around wooden table",
        "wholesome communal celebration, breaking golden crust in warm candlelight gratitude, crisp Full HD 1080p",
    ),
    123: (
        "OBJECT_MACRO",
        "wide perspective showing sower scattering seeds with completely equal generosity everywhere",
        "impartial divine grace, sowing hand releasing seeds across path rocks thorns and loam alike, crisp Full HD 1080p",
    ),
    125: (
        "SPLIT_COMPARISON",
        "split comparison of stingy calculating merchant versus open-handed generous sower",
        "counting individual pennies on left versus tossing golden grain freely across field on right, crisp Full HD 1080p",
    ),
    127: (
        "OBJECT_MACRO",
        "single seed falling upon cracked dry stone path illuminated by gentle loving beam",
        "unconditional offer of grace, seed offered even to the most hardened unpromising soil, crisp Full HD 1080p",
    ),
    128: (
        "OBJECT_MACRO",
        "rain cloud pouring refreshing water upon arid wasteland and fertile meadow without bias",
        "universal natural beneficence, falling moisture blessing every terrain with equal warmth, crisp Full HD 1080p",
    ),
    130: (
        "OBJECT_MACRO",
        "sunlight streaming across dark thorny ravine with the exact same brilliance as open field",
        "unconditional illumination, solar rays warming thistle patch and wheat furrow without partiality, crisp Full HD 1080p",
    ),
    131: (
        "OBJECT_MACRO",
        "sower face illuminated by golden dawn showing profound patient compassion without frustration",
        "peaceful spiritual countenance, serene brow accepting the mystery of disparate harvests, crisp Full HD 1080p",
    ),
    133: (
        "OBJECT_MACRO",
        "antique balance scale showing that true value lies in receptive soil rather than seed quality",
        "brass scale demonstrating seed is already perfect; the decisive variable is recipient soil, crisp Full HD 1080p",
    ),
    134: (
        "SPLIT_COMPARISON",
        "split comparison of blaming external circumstances versus tending one internal garden",
        "cursing the dry weather on left versus diligently digging well and removing stones on right, crisp Full HD 1080p",
    ),
    136: (
        "MECHANISM_CUTAWAY",
        "stratigraphic cutaway of human subconscious revealing layered geological soul strata",
        "cross-section of psyche showing surface habits, emotional stones, and fertile core depths, crisp Full HD 1080p",
    ),
    137: (
        "OBJECT_MACRO",
        "hardened cynical armor shell cracking open to reveal tender vulnerable inner soil",
        "iron protective mask fracturing, soft organic earth emerging from defensive casing, crisp Full HD 1080p",
    ),
    139: (
        "OBJECT_MACRO",
        "flock of metaphorical black birds representing cynical comments flying away into mist",
        "dispersion of toxic opinions, sky clearing above pathway as mindfulness takes root, crisp Full HD 1080p",
    ),
    140: (
        "SPLIT_COMPARISON",
        "split visual of superficial internet browsing versus immersive deep reading of classical text",
        "hyperactive scrolling thumb on left versus peaceful book illuminated by reading candle on right, crisp Full HD 1080p",
    ),
    142: (
        "OBJECT_MACRO",
        "excavated underground boulder lying beside deep trench showing rock removed by diligence",
        "triumph of inner effort, massive stone of cynicism hoisted out of spiritual garden, crisp Full HD 1080p",
    ),
    143: (
        "OBJECT_MACRO",
        "clear mountain spring bubbling through newly opened subterranean rock fissure",
        "living water bursting forth from newly liberated ground, quenching ancient dryness, crisp Full HD 1080p",
    ),
    145: (
        "OBJECT_MACRO",
        "pile of uprooted dry thorny vines withering on compost heap after thorough weeding",
        "cleared briars drying out harmlessly, garden bed completely purged of weed chokeholds, crisp Full HD 1080p",
    ),
    146: (
        "OBJECT_MACRO",
        "pruning shears cutting cleanly through thick invasive bramble stem threatening garden",
        "decisive spiritual boundaries, sharp iron blades severing toxic materialist attachments, crisp Full HD 1080p",
    ),
    148: (
        "OBJECT_MACRO",
        "clean uncluttered garden terrace with deep rich earth ready for new planting season",
        "peaceful cultivated sanctuary, spacious brown soil smiling beneath warm afternoon sun, crisp Full HD 1080p",
    ),
    149: (
        "OBJECT_MACRO",
        "heavy iron plowshare slicing cleanly through compacted soil turning over fresh moist earth",
        "deep cultivation in progress, dark rich subterranean layer turned upward toward sun, crisp Full HD 1080p",
    ),
    151: (
        "SPLIT_COMPARISON",
        "split comparison of painful initial plowing versus glorious subsequent golden harvest",
        "sweat and sharp plow cutting earth on left versus joyful harvest celebration on right, crisp Full HD 1080p",
    ),
    153: (
        "OBJECT_MACRO",
        "gentle earthworm aerating moist dark humus creating microscopic breathing channels",
        "invisible ecological allies, organic biological renewal restoring fertility to earth, crisp Full HD 1080p",
    ),
    155: (
        "OBJECT_MACRO",
        "compost bin transforming dry withered leaves into steaming dark nutrient-rich loam",
        "alchemical biological cycle, past failures and decayed matter converted into rich fertility, crisp Full HD 1080p",
    ),
    157: (
        "OBJECT_MACRO",
        "stone irrigation canal guiding crystal clear stream water into thirsty garden furrows",
        "intentional spiritual discipline, deliberate channel directing wisdom directly to roots, crisp Full HD 1080p",
    ),
    158: (
        "OBJECT_MACRO",
        "wooden sluice gate lifting to release fresh water across dry cultivated plots",
        "unhindered grace, life-giving stream revitalizing every corner of prepared soil, crisp Full HD 1080p",
    ),
    160: (
        "OBJECT_MACRO",
        "fragile newly germinated wheat shoot protected by circle of upright cedar shingles",
        "nursery shelter, delicate young seedling shielded from wind until stem thickens, crisp Full HD 1080p",
    ),
    161: (
        "SPLIT_COMPARISON",
        "split comparison of neglecting seed in darkness versus protecting it with caring fence",
        "abandoned trampled shoot on left versus nurtured thriving plant in fenced bed on right, crisp Full HD 1080p",
    ),
    163: (
        "OBJECT_MACRO",
        "solitary grain of wheat slipping through careless fingers into deep dark well water",
        "wasted fleeting moment, regret of neglected opportunity dissolving into deep water, crisp Full HD 1080p",
    ),
    164: (
        "OBJECT_MACRO",
        "barren windswept steppe showing empty horizon where magnificent field could have grown",
        "poignant agricultural tragedy, vast potential unfulfilled due to neglected cultivation, crisp Full HD 1080p",
    ),
    166: (
        "OBJECT_MACRO",
        "vivid green young wheat shoots standing proudly in crisp morning air",
        "promising juvenile phase, tender blades reaching upward with unblemished vigor, crisp Full HD 1080p",
    ),
    167: (
        "SPLIT_COMPARISON",
        "split visual of superficial emerald sprout on left versus deep hidden root network on right",
        "warning against deceptive outward appearance, underground foundation determines destiny, crisp Full HD 1080p",
    ),
    169: (
        "OBJECT_MACRO",
        "match flaring brilliantly in darkness for two seconds then leaving absolute pitch blackness",
        "superficial excitement without discipline, bright initial flash extinguished without trace, crisp Full HD 1080p",
    ),
    170: (
        "OBJECT_MACRO",
        "fierce midday summer sun beating down upon exposed unshaded rocky outcrop",
        "merciless environmental test, intense solar radiation testing depth of soil moisture, crisp Full HD 1080p",
    ),
    172: (
        "OBJECT_MACRO",
        "cracked dry clay pottery shard lying fractured in middle of dusty abandoned field",
        "collapse of ungrounded ambition, brittle pottery unable to survive kiln testing, crisp Full HD 1080p",
    ),
    173: (
        "OBJECT_MACRO",
        "contemplative silhouette of farmer standing beside empty field at quiet sunset",
        "melancholic agricultural reflection, sober evaluation of harvest failures and lessons, crisp Full HD 1080p",
    ),
    175: (
        "OBJECT_MACRO",
        "moist fertile garden plot where deep rich earth is completely choked by thorny briars",
        "tragedy of wasted fertility, excellent soil hijacked by aggressive parasitic weeds, crisp Full HD 1080p",
    ),
    176: (
        "OBJECT_MACRO",
        "macro view of sharp thorn barb embedded in soft pulp of green young wheat stalk",
        "physical stranglehold of materialism, sharp thorn choking vital botanical circulation, crisp Full HD 1080p",
    ),
    178: (
        "SPLIT_COMPARISON",
        "split comparison of golden trophy tarnishing on shelf versus living green tree blooming",
        "dead metallic status symbols on left versus living organic spiritual fruit on right, crisp Full HD 1080p",
    ),
    179: (
        "OBJECT_MACRO",
        "runner collapsing from exhaustion on treadmill surrounded by stacks of empty gold coins",
        "futility of endless social comparison, exhausting race leading only to spiritual depletion, crisp Full HD 1080p",
    ),
    181: (
        "OBJECT_MACRO",
        "withered yellow leaf falling silently from choked wheat plant onto dark briar patch",
        "silent botanical demise, gradual surrender to unchecked worldly distractions, crisp Full HD 1080p",
    ),
    183: (
        "OBJECT_MACRO",
        "soft velvety soil crumbling gently through open caring fingers in warm garden",
        "perfect tilth and moisture, welcoming fertile bed ready to embrace the seed, crisp Full HD 1080p",
    ),
    185: (
        "OBJECT_MACRO",
        "tall mature wheat ear bending gracefully heavy with sixty golden grains under sun",
        "triumph of genuine spiritual maturity, golden harvest bowing in natural humble grace, crisp Full HD 1080p",
    ),
    187: (
        "OBJECT_MACRO",
        "fresh green clover sprout emerging from center of old decaying tree stump",
        "inherent regenerative power of earth, life resurrecting from apparent decay and ruin, crisp Full HD 1080p",
    ),
    188: (
        "OBJECT_MACRO",
        "phoenix feather glowing like ember in soil sparking new life in desolate field",
        "symbol of radical spiritual rebirth, human capacity for total renewal through grace, crisp Full HD 1080p",
    ),
    190: (
        "OBJECT_MACRO",
        "sharp steel plowshare cutting deep furrow in hard clay throwing up rich dark loam",
        "courageous inner excavation, plowing through calcified habits to expose fresh ground, crisp Full HD 1080p",
    ),
    191: (
        "SPLIT_COMPARISON",
        "split comparison of stubborn unyielding stone monument versus soft plowable soil",
        "brittle dogmatism on left contrasted with supple teachable openheartedness on right, crisp Full HD 1080p",
    ),
    193: (
        "OBJECT_MACRO",
        "fresh mountain breeze blowing across freshly plowed field carrying scents of damp earth",
        "ventilation of ancient subterranean darkness, fresh oxygen awakening dormant vitality, crisp Full HD 1080p",
    ),
    194: (
        "OBJECT_MACRO",
        "early morning sunlight drying away damp mildew from wooden barn floorboards",
        "cleansing solar radiance dispelling stale shadows and damp mental stagnation, crisp Full HD 1080p",
    ),
    196: (
        "OBJECT_MACRO",
        "wheelbarrow carrying jagged heavy rocks away from garden plot toward ravine",
        "systematic removal of toxic mental grudges petty vanity and inherited biases, crisp Full HD 1080p",
    ),
    197: (
        "OBJECT_MACRO",
        "gardener throwing sharp thorny roots into burning fire pit to ensure they never return",
        "ruthless eradication of chronic weeds, destructive anxieties consumed in flames, crisp Full HD 1080p",
    ),
    199: (
        "OBJECT_MACRO",
        "wide airy soil bed offering deep expansive room for new root system to expand",
        "unrestricted botanical freedom, subterranean spaciousness inviting deep root growth, crisp Full HD 1080p",
    ),
    200: (
        "OBJECT_MACRO",
        "mud-stained human hands holding single radiant golden grain with profound tenderness",
        "devoted agricultural reverence, dirty working fingers cherishing the miracle of life, crisp Full HD 1080p",
    ),
    202: (
        "OBJECT_MACRO",
        "carefully bandaged gardener hand continuing to work soil despite scratches from thorns",
        "patient perseverance through painful personal transformation, unswerving devotion, crisp Full HD 1080p",
    ),
    203: (
        "OBJECT_MACRO",
        "deep taproot of dandelion pulled out completely intact with zero root remnant left",
        "total eradication of anxiety at its deepest subconscious root, lasting spiritual peace, crisp Full HD 1080p",
    ),
    205: (
        "OBJECT_MACRO",
        "traveler untying heavy iron baggage and setting it down beside road to walk freely",
        "unburdening soul from useless social status burdens, sudden lightness of step, crisp Full HD 1080p",
    ),
    207: (
        "OBJECT_MACRO",
        "steaming freshly turned loam releasing rich primordial fragrance of fertility into air",
        "sensory proof of renewed life, sweet rich aroma of moist earth under morning sun, crisp Full HD 1080p",
    ),
    209: (
        "OBJECT_MACRO",
        "cool spring water poured from earthen pitcher washing away dried mud from weary feet",
        "restorative cleansing ritual, soothing past trauma with gentle forgiveness and care, crisp Full HD 1080p",
    ),
    211: (
        "OBJECT_MACRO",
        "golden harvest diorama showing abundant sheaves stacked high in golden sunset glow",
        "splendid reward of unyielding patience, agricultural triumph beyond initial imagination, crisp Full HD 1080p",
    ),
    213: (
        "OBJECT_MACRO",
        "hand gently placing seed into dark moist furrow and smoothing warm soil over it",
        "faithful planting gesture, human responsibility fulfilled in alignment with grace, crisp Full HD 1080p",
    ),
    215: (
        "STEP_ENUMERATION",
        "inscribed wooden stele displaying Lesson One: The Sacred Virtue of Agricultural Patience",
        "first carved cedar tablet illuminated by amber torchlight, honoring unseen subterranean growth, crisp Full HD 1080p",
    ),
    216: (
        "SPLIT_COMPARISON",
        "split comparison of microwave instant gratification clock versus slow antique hourglass",
        "frantic digital second-counter on left versus patient steady trickle of sand grains on right, crisp Full HD 1080p",
    ),
    218: (
        "OBJECT_MACRO",
        "child frantically digging up seed every ten minutes to see if roots have grown",
        "folly of impatience, unearthing delicate subterranean embryo and causing its premature death, crisp Full HD 1080p",
    ),
    219: (
        "OBJECT_MACRO",
        "ancient massive oak tree standing majestic after five hundred years of silent growth",
        "triumph of imperceptible daily maturation, timeless canopy sheltering entire meadow, crisp Full HD 1080p",
    ),
    221: (
        "OBJECT_MACRO",
        "anchor chain stretching deep into dark ocean floor securing great sailing galleon",
        "unshakeable subterranean fortitude, deep inner grounding anchoring soul against tempest, crisp Full HD 1080p",
    ),
    222: (
        "MECHANISM_CUTAWAY",
        "mechanism cutaway showing taproot penetrating twice as deep into bedrock as tree height",
        "structural biological ratio, invisible subterranean anchor matching soaring canopy, crisp Full HD 1080p",
    ),
    224: (
        "SPLIT_COMPARISON",
        "split comparison of self-righteous judge pointing finger versus compassionate gardener",
        "harsh condemning gavel on left versus gentle hands wrapping bandage around bruised stem on right, crisp Full HD 1080p",
    ),
    225: (
        "OBJECT_MACRO",
        "bruised thorny cactus blossoming with stunning luminous white flower at midnight",
        "hidden spiritual potential, magnificent blossoming emerging from rough defensive prickly exterior, crisp Full HD 1080p",
    ),
    227: (
        "OBJECT_MACRO",
        "dormant wheat seed resting quietly in cold winter soil awaiting inevitable spring warmth",
        "patient subterranean hibernation, vital life spark preserved intact beneath snow cover, crisp Full HD 1080p",
    ),
    228: (
        "OBJECT_MACRO",
        "vibrant green sprout bursting through thick cracked slab of abandoned concrete pavement",
        "miraculous breakthrough of life in the most seemingly impossible desolate location, crisp Full HD 1080p",
    ),
    230: (
        "STEP_ENUMERATION",
        "inscribed wooden stele displaying Lesson Three: Continuous Cultivation of Inner Soil",
        "third carved cedar tablet illuminated by amber torchlight, focusing leverage on inner state, crisp Full HD 1080p",
    ),
    231: (
        "OBJECT_MACRO",
        "weather vane spinning wildly in storm wind while church stone foundation stands still",
        "uncontrollable exterior elements versus unshakeable interior bedrock citadel, crisp Full HD 1080p",
    ),
    233: (
        "OBJECT_MACRO",
        "gardener hands holding soil moisture meter carefully checking internal garden balance",
        "sovereign personal agency, directing focus exclusively to what is within one's control, crisp Full HD 1080p",
    ),
    235: (
        "OBJECT_MACRO",
        "stout stone lighthouse standing unshakeable while roaring ocean waves crash against base",
        "invulnerable inner fortitude, external emotional storms failing to flicker interior flame, crisp Full HD 1080p",
    ),
    237: (
        "OBJECT_MACRO",
        "crystal clear drop of morning dew resting upon clean white linen cloth in sunrise",
        "unblemished spiritual clarity, pure intention yielding serene joyful peace, crisp Full HD 1080p",
    ),
    239: (
        "OBJECT_MACRO",
        "golden wheat heads bowing low in humble reverence under warm morning sun",
        "full ears bowing down, true wisdom and abundance manifested in humble posture, crisp Full HD 1080p",
    ),
    241: (
        "OBJECT_MACRO",
        "polished bronze mirror reflecting calm peaceful face of meditative practitioner in dawn",
        "lucid introspection, quiet soul evaluating its internal landscape with serene honesty, crisp Full HD 1080p",
    ),
    242: (
        "STEP_ENUMERATION",
        "triptych illustration contrasting path edge rocky ledge and deep fertile furrow",
        "soul self-examination diorama, three conditions evaluated under gentle golden light, crisp Full HD 1080p",
    ),
    244: (
        "OBJECT_MACRO",
        "morning sunbeam piercing through morning fog illuminating path with dazzling clarity",
        "enlightening revelation, sudden spiritual understanding transforming inner landscape, crisp Full HD 1080p",
    ),
    245: (
        "OBJECT_MACRO",
        "crystalline morning dewdrop resting upon parched soil crack gently softening dry edge",
        "healing soothing touch, gentle compassion dissolving hard calcified resentments, crisp Full HD 1080p",
    ),
    247: (
        "OBJECT_MACRO",
        "gentle open palm releasing white doves of compassion and benevolent thoughts into sky",
        "intentional positive karma, benevolent wishes soaring outward across golden horizon, crisp Full HD 1080p",
    ),
    248: (
        "OBJECT_MACRO",
        "hands carefully weeding tiny single stray wild thistle from corner of vegetable patch",
        "deliberate daily vigilance, attending to minor emotional weeds before they take over, crisp Full HD 1080p",
    ),
    250: (
        "OBJECT_MACRO",
        "tender green wheat shoot stretching both arms wide to embrace golden morning sun",
        "pure unhindered botanical joy, celebration of life in fertile cultivated earth, crisp Full HD 1080p",
    ),
    252: (
        "OBJECT_MACRO",
        "glowing golden seed resting in warm chamber inside human chest emitting soft light",
        "divine spark inherent within human heart, sacred peace already present waiting to be tended, crisp Full HD 1080p",
    ),
    254: (
        "SITUATIONAL_ACTION",
        "peaceful sower kneeling by fertile garden bed smoothing dark warm loam with loving hands",
        "lifelong sacred commitment to inner cultivation, golden sunset enveloping fertile garden, crisp Full HD 1080p",
    ),
}

if __name__ == "__main__":
    print(f"Total bespoke beats for loi_sang_soi: {len(BESPOKE_BEATS)}")
    cores = [v[1][:60].lower() for v in BESPOKE_BEATS.values()]
    print(f"Unique cores count: {len(set(cores))}/{len(cores)}")
    assert len(set(cores)) == len(cores), f"Duplicates found: {len(cores) - len(set(cores))}"
    print("ALL 157 CORES ARE 100% UNIQUE!")
