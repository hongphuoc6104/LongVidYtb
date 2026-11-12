"""Bespoke Explainer Prompt Mapping for minh_triet_song (190 new beats).

Every beat index maps to: (explainer_type, core_clause, details)
Guarantees 100% unique core subjects (b["prompt"].split(",")[1].strip()[:60].lower())
with zero template cycling and zero generic fallbacks.
"""

PREFIX = "Classical Stoic & Eastern philosophical ink-and-stone diorama,"
SUFFIX = ", zero text overlay, no watermarks"

BESPOKE_BEATS = {
    1: (
        "OBJECT_MACRO",
        "vast frozen Danube river winding through misty snowy pine forest under blizzard",
        "distant Roman legionary frontier outpost, biting frost, muted antique parchment palette, crisp Full HD 1080p",
    ),
    2: (
        "OBJECT_MACRO",
        "heavy military canvas tent flapping violently under howling northern gale",
        "rough wool guy-ropes trembling under blizzard wind, solitary campaign bivouac, crisp Full HD 1080p",
    ),
    4: (
        "OBJECT_MACRO",
        "solitary flickering brass oil lamp illuminating weathered oak campaign desk",
        "warm pool of golden candlelight on papyrus scroll, chilling shadows beyond, crisp Full HD 1080p",
    ),
    5: (
        "SITUATIONAL_ACTION",
        "Roman emperor Marcus Aurelius seated alone in heavy wool cloak at night",
        "weary dignified posture, philosopher king writing Meditations, classical chiaroscuro, crisp Full HD 1080p",
    ),
    6: (
        "SPLIT_COMPARISON",
        "split composition of outer barbarian war storm versus quiet contemplative inner sanctuary",
        "screaming blizzards and iron swords on left contrasted with unmoving candle flame on right, crisp Full HD 1080p",
    ),
    7: (
        "OBJECT_MACRO",
        "carved marble bust profile remaining completely steadfast amidst swirling snowflakes",
        "unflinching stoic gaze, timeless granite serenity defying turbulent northern elements, crisp Full HD 1080p",
    ),
    9: (
        "OBJECT_MACRO",
        "desolate empty Roman colonnade with fallen autumn leaves drifting through cold mist",
        "Antonine plague diorama, somber abandoned streets of imperial Rome in crisis, crisp Full HD 1080p",
    ),
    10: (
        "OBJECT_MACRO",
        "distant northern horizon engulfed in black smoke and burning frontier barricades",
        "barbarian siege fires glowing ominously along border palisade under winter dusk, crisp Full HD 1080p",
    ),
    11: (
        "OBJECT_MACRO",
        "iron siege engines surrounded by spiked wooden fortifications in deep frozen mud",
        "relentless military blockade, grim iron ballistas mounted against dark forest line, crisp Full HD 1080p",
    ),
    12: (
        "OBJECT_MACRO",
        "shadowy conspirator silhouette clutching hidden iron dagger behind marble pillars",
        "rebellion lurking in court shadows, political betrayal threatening imperial throne, crisp Full HD 1080p",
    ),
    14: (
        "OBJECT_MACRO",
        "bronze imperial seal resting quietly beside plain unadorned iron writing stylus",
        "supreme authority wielded with total humility and absence of self-pity, crisp Full HD 1080p",
    ),
    15: (
        "OBJECT_MACRO",
        "blank papyrus roll untainted by bitter words of complaint or resentment",
        "pure philosophical record, sovereign mind refusing to indulge in grievance, crisp Full HD 1080p",
    ),
    17: (
        "OBJECT_MACRO",
        "massive granite cliff standing unshaken as violent thunderbolts strike the sea",
        "stoic fortitude, tectonic rock absorbing storm lightning without single fracture, crisp Full HD 1080p",
    ),
    19: (
        "OBJECT_MACRO",
        "reed pen tip carving deliberate Greek philosophical letters into rough parchment",
        "ink flowing into timeless maxims, manual discipline engraving inner resilience, crisp Full HD 1080p",
    ),
    20: (
        "OBJECT_MACRO",
        "inscribed stone tablet bearing stoic decree on sovereign mental tranquility",
        "deep chiseled Roman capitals illuminated by side lantern light in soldier tent, crisp Full HD 1080p",
    ),
    22: (
        "SITUATIONAL_ACTION",
        "stoic sage Epictetus leaning on wooden staff standing atop weathered marble terrace",
        "humble freed slave philosopher, dignified posture against Aegean dawn horizon, crisp Full HD 1080p",
    ),
    23: (
        "OBJECT_MACRO",
        "straight deliberate line chiseled deep across flat granite flagstone terrace",
        "the dichotomy of control demarcation, absolute boundary separating two worlds, crisp Full HD 1080p",
    ),
    24: (
        "SPLIT_COMPARISON",
        "split perspective of two realms: internal sovereignty on left versus external chaos on right",
        "orderly garden of free will contrasted with turbulent ocean of random circumstance, crisp Full HD 1080p",
    ),
    25: (
        "OBJECT_MACRO",
        "golden morning sunbeam striking chiseled stone line casting crisp linear shadow",
        "illuminating clarity of Stoic discernment, stark contrast between light and shade, crisp Full HD 1080p",
    ),
    26: (
        "SPLIT_COMPARISON",
        "split comparison diorama contrasting mortal frailty with immutable philosophical truth",
        "crumbling clay urn beside eternal geometric sphere carved from solid basalt, crisp Full HD 1080p",
    ),
    28: (
        "OBJECT_MACRO",
        "carved stone compass pointing true north resting upon chiseled terrace boundary",
        "foundational moral orientation, tranquility born from respecting natural limits, crisp Full HD 1080p",
    ),
    29: (
        "OBJECT_MACRO",
        "open human palm holding glowing sovereign orb representing conscious choice and virtue",
        "things in our power: our opinions impulses desires and moral decisions, crisp Full HD 1080p",
    ),
    30: (
        "OBJECT_MACRO",
        "sculpted marble hand firmly gripping helm of ship navigating through shallow reefs",
        "sovereign navigation, autonomous will guiding personal character through life, crisp Full HD 1080p",
    ),
    32: (
        "MECHANISM_CUTAWAY",
        "architectural cutaway of an impregnable inner acropolis fortress within human skull",
        "the inner citadel diorama, inviolable sanctuary of reason protected by high walls, crisp Full HD 1080p",
    ),
    33: (
        "OBJECT_MACRO",
        "sovereign royal throne room occupied solely by personified conscience and reason",
        "unquestioned internal autonomy, supreme ruler of personal attitude and moral stance, crisp Full HD 1080p",
    ),
    34: (
        "OBJECT_MACRO",
        "bronze lantern burning with unquenchable flame inside roaring wind tunnel",
        "impervious inner light, flame shielded by crystal glass burning steadily, crisp Full HD 1080p",
    ),
    35: (
        "OBJECT_MACRO",
        "serene philosopher king resting hand on breastplate with absolute self-mastery",
        "inner composure, mastery over passions shining through dignified countenance, crisp Full HD 1080p",
    ),
    37: (
        "OBJECT_MACRO",
        "flock of autumn leaves whirled into frantic vortex by unpredictable mountain gusts",
        "things outside our control: external reputation wealth health and other opinions, crisp Full HD 1080p",
    ),
    38: (
        "OBJECT_MACRO",
        "fragile soap bubble reflecting crowd faces before bursting instantly into empty air",
        "evanescent nature of public praise and censure, illusory fleeting validation, crisp Full HD 1080p",
    ),
    39: (
        "SPLIT_COMPARISON",
        "split comparison of puppet tethered to cheering crowd versus independent stoic sage",
        "marionette dangling on strings on left versus grounded philosopher standing tall on right, crisp Full HD 1080p",
    ),
    41: (
        "OBJECT_MACRO",
        "massive stone wheel of fortune Fortuna turning inexorably crushing mortal plans",
        "blind cyclical destiny, cosmic forces moving indifferent to human demands, crisp Full HD 1080p",
    ),
    43: (
        "OBJECT_MACRO",
        "tortured Prometheus chained to Caucasian rock writhing in futile mental agony",
        "torment of fighting immutable fate, unnecessary suffering born from futile resentment, crisp Full HD 1080p",
    ),
    44: (
        "OBJECT_MACRO",
        "iron shackles slipping off wrists onto stone floor as hands open freely",
        "release from grasping, absolute spiritual liberation gained by abandoning futile control, crisp Full HD 1080p",
    ),
    45: (
        "OBJECT_MACRO",
        "soaring solitary eagle gliding effortlessly on high thermal currents above jagged peaks",
        "unhindered philosophical freedom, elevation above mundane attachments, crisp Full HD 1080p",
    ),
    47: (
        "OBJECT_MACRO",
        "dry pine log thrown into center of blazing ceramic smelting kiln",
        "Amor Fati metaphor: blazing fire converting every obstacle into fuel and flame, crisp Full HD 1080p",
    ),
    48: (
        "OBJECT_MACRO",
        "roaring golden furnace flames consuming dry timber and growing brighter and hotter",
        "the impediment to action advances action: what stands in the way becomes the way, crisp Full HD 1080p",
    ),
    50: (
        "SITUATIONAL_ACTION",
        "rugged mountaineer stepping deliberately onto fallen avalanche boulder to climb higher",
        "transforming hindrance into stepping stone, ascent facilitated by fallen rock, crisp Full HD 1080p",
    ),
    51: (
        "OBJECT_MACRO",
        "rough natural stone steps ascending sheer granite cliff face toward clouds",
        "adverse terrain converted into ascending staircase of character development, crisp Full HD 1080p",
    ),
    53: (
        "OBJECT_MACRO",
        "blacksmith heavy steel sledgehammer descending upon glowing orange iron billet",
        "crucible of adversity, blunt force forging resilience and molecular density, crisp Full HD 1080p",
    ),
    54: (
        "SPLIT_COMPARISON",
        "split comparison of shattered fragile clay pot versus forged unbreakable steel blade",
        "fragility crushed by hammer on left versus steel tempered into deadly perfection on right, crisp Full HD 1080p",
    ),
    55: (
        "OBJECT_MACRO",
        "razor-sharp Damascus steel gladius sword gleaming with intricate folded metal patterns",
        "masterpiece born from flame and hammer, soul tempered through endured suffering, crisp Full HD 1080p",
    ),
    57: (
        "OBJECT_MACRO",
        "ancient gnarled oak tree clinging fiercely to windswept sea cliff with deep roots",
        "botanical fortitude, storm winds forcing root fibers deeper into rock crevices, crisp Full HD 1080p",
    ),
    58: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram linking gale wind velocity to exponential root anchoring depth in bedrock",
        "adversity directly stimulating structural reinforcement in moral character, crisp Full HD 1080p",
    ),
    60: (
        "OBJECT_MACRO",
        "open arms carved in classical marble welcoming both storm rain and gentle sunlight",
        "radical hospitality to fate, embracing whatever Providence delivers without grievance, crisp Full HD 1080p",
    ),
    61: (
        "OBJECT_MACRO",
        "calm unblemished shield bearing engraved motto Amor Fati reflecting clear blue sky",
        "unconditional love of destiny, shield that reflects all arrows without bitterness, crisp Full HD 1080p",
    ),
    63: (
        "OBJECT_MACRO",
        "unbroken granite column standing upright amidst ruins of fallen Roman forum",
        "indomitable dignity, architectural monument surviving earthquake and fire intact, crisp Full HD 1080p",
    ),
    64: (
        "OBJECT_MACRO",
        "golden dawn beam piercing through dense dark storm clouds over stormy sea",
        "ray of providence illuminating turbulent waters, hope shining through adversity, crisp Full HD 1080p",
    ),
    65: (
        "OBJECT_MACRO",
        "rugged winding mountain trail leading up to luminous sunlit alpine sanctuary",
        "steep path of virtue, demanding ascent rewarded by panoramic cosmic clarity, crisp Full HD 1080p",
    ),
    67: (
        "OBJECT_MACRO",
        "sacred bronze brazier burning with eternal flame of determined philosophical resolve",
        "fueling the inner spark, trials transformed into fuel for unshakeable virtue, crisp Full HD 1080p",
    ),
    68: (
        "OBJECT_MACRO",
        "intricate Roman mosaic medallion depicting interlocking hands holding sun and anvil",
        "allegory of Amor Fati, cosmic partnership between mortal soul and divine providence, crisp Full HD 1080p",
    ),
    70: (
        "OBJECT_MACRO",
        "vast churning ocean with towering dark waves threatening coastal fishing skiff",
        "elemental chaos, overwhelming storm swells crashing against frail human craft, crisp Full HD 1080p",
    ),
    71: (
        "OBJECT_MACRO",
        "massive ocean breaker exploding into white foam against immovable granite sea wall",
        "violent collision of passions against the defensive rampart of stoic equanimity, crisp Full HD 1080p",
    ),
    72: (
        "OBJECT_MACRO",
        "red hot molten lava erupting from volcanic fissure tearing through cool forest floor",
        "destructive fury of unmastered anger, visceral wrath consuming inner peace, crisp Full HD 1080p",
    ),
    74: (
        "OBJECT_MACRO",
        "runaway war chariot engulfed in flames before even reaching the battle line",
        "self-destructive wrath, blind passion overturning the vehicle of reason, crisp Full HD 1080p",
    ),
    75: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram showing how explosive anger blinds driver before enemy contact is made",
        "internal fire destroying tactical effectiveness, rage as suicide of reason, crisp Full HD 1080p",
    ),
    76: (
        "OBJECT_MACRO",
        "tragic classical mask of rage fracturing from internal stress into jagged pieces",
        "temper tantrum leading to psychic ruin, anger as brief temporary madness, crisp Full HD 1080p",
    ),
    78: (
        "OBJECT_MACRO",
        "exquisite antique ceramic vase dropped onto marble floor shattering into hundred shards",
        "irreversible consequence of brief uncontrolled temper, sudden catastrophic loss, crisp Full HD 1080p",
    ),
    79: (
        "OBJECT_MACRO",
        "sharp porcelain shards scattered across dark empty hall reflecting cold moonlight",
        "broken relationships, ruinous debris left behind by one careless explosive outburst, crisp Full HD 1080p",
    ),
    80: (
        "SPLIT_COMPARISON",
        "split comparison of decades of patient bridge building versus ten seconds of arson",
        "stone bridge constructed over generations on left versus ruined charred span on right, crisp Full HD 1080p",
    ),
    81: (
        "OBJECT_MACRO",
        "snapped friendship friendship cord of woven gold thread severed by angry iron dagger",
        "fragile social trust severed in a single heartbeat of wounded pride, crisp Full HD 1080p",
    ),
    83: (
        "OBJECT_MACRO",
        "burning pitch dropping from high torch scorching the bare hand holding it aloft",
        "Seneca proverb visual: he who holds the torch of vengeance burns his own fingers first, crisp Full HD 1080p",
    ),
    84: (
        "OBJECT_MACRO",
        "blistered scarred hand nursing painful burns while enemy walks away untouched",
        "folly of resentment, holding hot coals with intention of throwing them at another, crisp Full HD 1080p",
    ),
    85: (
        "CAUSE_EFFECT_DIAGRAM",
        "flowchart showing hatred consuming the vessel containing it before reaching target",
        "toxic emotional acid corroding internal organs while external target remains oblivious, crisp Full HD 1080p",
    ),
    86: (
        "OBJECT_MACRO",
        "clay crucible melting and fracturing under excessive internal chemical heat",
        "somatic burnout, body and soul incinerated by chronic unexpressed resentment, crisp Full HD 1080p",
    ),
    88: (
        "OBJECT_MACRO",
        "wild desert briar bush bearing only needle-sharp thorns and zero fragrant blossoms",
        "nature of malicious people: expecting figs from thistles is the folly of the fool, crisp Full HD 1080p",
    ),
    90: (
        "OBJECT_MACRO",
        "polished bronze mirror reflecting distorted snarling face of raging man",
        "grotesque ugliness of wrath, mirror held up to expose the ridiculous loss of dignity, crisp Full HD 1080p",
    ),
    92: (
        "OBJECT_MACRO",
        "cloud of acrid sulfur smoke dispersing completely into pure evening mountain air",
        "passions dissipating, emotional storm clearing to reveal pristine untouched sky, crisp Full HD 1080p",
    ),
    93: (
        "OBJECT_MACRO",
        "tranquil temple courtyard washed clean by fresh rain in cool serene dusk",
        "restoration of equilibrium, stone flags glistening in pure peaceful stillness, crisp Full HD 1080p",
    ),
    95: (
        "OBJECT_MACRO",
        "still mountain pool reflecting vast unbroken blue vault of heaven without single ripple",
        "unclouded mind of the sage, mirror of consciousness undisturbed by external breeze, crisp Full HD 1080p",
    ),
    96: (
        "OBJECT_MACRO",
        "impenetrable Roman fortress gateway built from dressed basalt blocks and bronze bolts",
        "impregnable character, calm composure serving as the ultimate fortress of the soul, crisp Full HD 1080p",
    ),
    97: (
        "OBJECT_MACRO",
        "solid granite cornerstone supporting weight of massive imperial arch without shifting",
        "steadfast moral integrity, foundational maturity anchoring entire personality, crisp Full HD 1080p",
    ),
    99: (
        "SITUATIONAL_ACTION",
        "triumphant Roman general riding gilded chariot through roaring cheering crowds",
        "imperial triumph procession, laurel wreath on brow, golden eagles held high, crisp Full HD 1080p",
    ),
    100: (
        "OBJECT_MACRO",
        "gleaming golden wheel of triumphal chariot turning through sea of laurel leaves",
        "apex of worldly glory, magnificent spectacle celebrating transient military conquest, crisp Full HD 1080p",
    ),
    101: (
        "OBJECT_MACRO",
        "tens of thousands of cheering citizens waving palm branches from Colosseum tiers",
        "deafening adoration, intoxicating roaring applause echoing across Roman hills, crisp Full HD 1080p",
    ),
    102: (
        "SITUATIONAL_ACTION",
        "humble slave standing behind general whispering the sacred warning into his ear",
        "Respice post te! Hominem te esse memento! Remember that thou art mortal!, crisp Full HD 1080p",
    ),
    103: (
        "OBJECT_MACRO",
        "carved human skull resting beside golden laurel victory wreath on stone altar",
        "Memento Mori contrast: ephemeral temporal triumph beside eternal human mortality, crisp Full HD 1080p",
    ),
    105: (
        "OBJECT_MACRO",
        "antique brass hourglass resting quietly upon open illuminated manuscript of Seneca",
        "temporal precision, glass bulbs measuring the steady irreversible passage of life, crisp Full HD 1080p",
    ),
    106: (
        "OBJECT_MACRO",
        "fine golden sand grains trickling steadily through narrow glass orifice one by one",
        "irretrievable seconds escaping, tactile visualization of relentlessly flowing time, crisp Full HD 1080p",
    ),
    107: (
        "OBJECT_MACRO",
        "empty upper bulb of hourglass showing last thirty grains ready to descend",
        "scarcity of remaining hours, acute awareness of finitude awakening precious presence, crisp Full HD 1080p",
    ),
    108: (
        "OBJECT_MACRO",
        "shadow of sundial gnomon lengthening steadily across carved Roman numeral dial",
        "inevitable progression of dusk, the creeping line marking hours gone forever, crisp Full HD 1080p",
    ),
    109: (
        "OBJECT_MACRO",
        "wilted dried rose petal drifting silently into rushing river current and vanishing",
        "ephemeral beauty, human life as brief floating petal on the river of eternity, crisp Full HD 1080p",
    ),
    111: (
        "SPLIT_COMPARISON",
        "split comparison of trembling mortal in terror of death versus serene sage welcoming it",
        "paralyzing dread on left contrasted with peaceful equanimity and ready departure on right, crisp Full HD 1080p",
    ),
    112: (
        "OBJECT_MACRO",
        "weary actor taking final gracious bow on wooden stage as velvet curtain descends",
        "Epictetus stage metaphor: playing one's allotted role well then exiting with grace, crisp Full HD 1080p",
    ),
    114: (
        "OBJECT_MACRO",
        "harvested golden grape cluster placed reverently into wicker wine basket at dusk",
        "ripeness is all, life brought to full natural completion without greed for extra time, crisp Full HD 1080p",
    ),
    115: (
        "OBJECT_MACRO",
        "ripe olive falling gently from branch into soft moss beneath olive grove tree",
        "blessing the tree that bore it and thanking the earth that receives it, crisp Full HD 1080p",
    ),
    116: (
        "OBJECT_MACRO",
        "content traveler packing leather satchel and extinguishing hearth lamp before sleep",
        "peaceful preparation, leaving the feast of life satisfied without complaint, crisp Full HD 1080p",
    ),
    118: (
        "SPLIT_COMPARISON",
        "split comparison of trivial petty grievances versus cosmic perspective from starry heavens",
        "squabbling over pennies on left versus vast glowing Milky Way galaxy above on right, crisp Full HD 1080p",
    ),
    120: (
        "OBJECT_MACRO",
        "globe of Earth viewed from orbital height looking like tiny dust mote in sunlight",
        "the view from above, insignificance of mortal boundaries and territorial wars, crisp Full HD 1080p",
    ),
    121: (
        "OBJECT_MACRO",
        "magnifying glass held over tiny ant hill where soldier ants fight over grain",
        "stoic cosmic detachment, observing human imperial rivalries as ant skirmishes, crisp Full HD 1080p",
    ),
    123: (
        "OBJECT_MACRO",
        "deep breath of crisp alpine air filling lungs on high mountain ridge in sunrise",
        "vital appreciation of existence, every breath recognized as unmerited temporary gift, crisp Full HD 1080p",
    ),
    125: (
        "OBJECT_MACRO",
        "two friends embracing warmly in doorway knowing each parting could be their last",
        "sanctified presence, Memento Mori transforming ordinary greeting into sacred tenderness, crisp Full HD 1080p",
    ),
    127: (
        "OBJECT_MACRO",
        "warm porcelain tea bowl cradled with deep mindfulness in both hands in morning sun",
        "drinking life fully, mundane moments elevated to sublime appreciation by mortality, crisp Full HD 1080p",
    ),
    128: (
        "SPLIT_COMPARISON",
        "split visual of cold indifferent stone statue versus warm compassionate beating heart",
        "debunking the false myth of Stoicism as unfeeling sociopathy, crisp Full HD 1080p",
    ),
    129: (
        "SPLIT_COMPARISON",
        "split portrayal of cynical detached hermit versus devoted Roman father tending sick child",
        "frigid escapism on left contrasted with loving familial duty and warmth on right, crisp Full HD 1080p",
    ),
    130: (
        "OBJECT_MACRO",
        "hand tenderly wiping tear from friend cheek with profound empathetic gentleness",
        "stoic empathy: feeling with others while maintaining sovereign inner stability, crisp Full HD 1080p",
    ),
    132: (
        "OBJECT_MACRO",
        "compassionate eyes of Roman emperor gazing at wounded soldiers with deep brotherhood",
        "Marcus Aurelius cosmopolitan love: we are made for cooperation like feet hands eyes, crisp Full HD 1080p",
    ),
    133: (
        "OBJECT_MACRO",
        "warm blanket laid over shivering shoulders of poor beggar outside imperial gates",
        "active civic benevolence, virtue expressed through concrete compassionate service, crisp Full HD 1080p",
    ),
    134: (
        "SPLIT_COMPARISON",
        "split comparison of hysterical emotional drowning versus calm lifeguard swimming to rescue",
        "flailing in panic on left contrasted with disciplined skillful rescuer pulling victim ashore, crisp Full HD 1080p",
    ),
    136: (
        "OBJECT_MACRO",
        "stalwart helmsman keeping eyes fixed on polar star while steering lifeboat through gale",
        "disciplined care, inner steadiness required to actually help those in distress, crisp Full HD 1080p",
    ),
    137: (
        "OBJECT_MACRO",
        "surgeon calm steady hands operating delicately under battlefield emergency lantern",
        "mastery over squeamishness, emotional discipline enabling healing intervention, crisp Full HD 1080p",
    ),
    138: (
        "OBJECT_MACRO",
        "unshakable lighthouse keeper refueling lantern mechanism while waves lash the glass",
        "steadfast duty, providing guidance to lost ships through disciplined vigilance, crisp Full HD 1080p",
    ),
    140: (
        "OBJECT_MACRO",
        "deep calm ocean abyss remaining undisturbed two hundred meters beneath hurricane",
        "subterranean peace, surface turbulence unable to disturb profound oceanic serenity, crisp Full HD 1080p",
    ),
    141: (
        "OBJECT_MACRO",
        "warm glowing charcoal brazier keeping entire stone room warm throughout winter night",
        "enduring inner benevolence, warmth radiating steadily without chaotic flares, crisp Full HD 1080p",
    ),
    142: (
        "OBJECT_MACRO",
        "delicate balance scale holding heavy stone of duty balanced by golden feather of love",
        "synthesis of stoic rigor and profound humanity, harmonious moral equilibrium, crisp Full HD 1080p",
    ),
    144: (
        "OBJECT_MACRO",
        "blooming wild violet growing courageously between cracked slabs of military fortress",
        "gentle tenderness flourishing amidst stern granite fortifications, crisp Full HD 1080p",
    ),
    145: (
        "OBJECT_MACRO",
        "hand gently releasing injured sparrow back into open sky after splinting its wing",
        "tender stewardship of life, compassionate benevolence without possessive clinging, crisp Full HD 1080p",
    ),
    146: (
        "OBJECT_MACRO",
        "pristine crystal mirror showing flawless surface untainted by dust or fingerprint",
        "clear conscience, moral integrity far more precious than superficial flattery, crisp Full HD 1080p",
    ),
    147: (
        "SPLIT_COMPARISON",
        "split comparison of hollow crowd applause fading away versus unshakeable self-respect",
        "empty echoing stadium on left versus serene scholar smiling at clean conscience on right, crisp Full HD 1080p",
    ),
    149: (
        "OBJECT_MACRO",
        "open hand pouring cool refreshing water for thirsty traveler from plain clay jug",
        "unconditional altruism, offering nourishment without calculating debt or return, crisp Full HD 1080p",
    ),
    150: (
        "OBJECT_MACRO",
        "apple tree offering heavy ripe fruit to passing strangers without asking praise",
        "natural generosity, producing good fruit simply because it is in its nature to do so, crisp Full HD 1080p",
    ),
    152: (
        "OBJECT_MACRO",
        "granite sea cliff growing smoother and more majestic after millennia of storm waves",
        "character refined by adversity, hardships polish the soul into regal brilliance, crisp Full HD 1080p",
    ),
    153: (
        "OBJECT_MACRO",
        "soaring pine tree trunks reaching higher into sunlight after surviving forest fire",
        "post-traumatic growth, surviving catastrophe leaves soul taller and more resilient, crisp Full HD 1080p",
    ),
    155: (
        "OBJECT_MACRO",
        "sculpted marble head of Socrates with peaceful serene expression during final trial",
        "true philosophical nobility, dignity maintained in face of unjust condemnation, crisp Full HD 1080p",
    ),
    156: (
        "OBJECT_MACRO",
        "golden laurel wreath placed upon open philosophical book on simple wooden podium",
        "supreme triumph of character, wisdom and moral courage outshining military power, crisp Full HD 1080p",
    ),
    158: (
        "SITUATIONAL_ACTION",
        "stoic philosopher seated in quiet room mentally rehearsing potential future catastrophes",
        "Premeditatio Malorum practice: visualization of exile poverty betrayal and sickness, crisp Full HD 1080p",
    ),
    159: (
        "OBJECT_MACRO",
        "sudden lightning bolt striking solitary watchtower out of seemingly clear blue sky",
        "element of surprise, reality never providing advance warning before disaster strikes, crisp Full HD 1080p",
    ),
    161: (
        "SPLIT_COMPARISON",
        "split comparison of sudden financial bankruptcy versus sudden slander by old friend",
        "empty money vault on left versus whispered false rumors behind back on right, crisp Full HD 1080p",
    ),
    162: (
        "OBJECT_MACRO",
        "experienced gladiator calmly adjusting bronze armor before entering dark arena",
        "mental rehearsal removes terror, familiarization disarming the sting of surprise, crisp Full HD 1080p",
    ),
    163: (
        "CAUSE_EFFECT_DIAGRAM",
        "diagram demonstrating that shock and panic stem from novelty rather than hardship itself",
        "cognitive habituation curve showing preparedness reducing emotional amplitude by eighty percent, crisp Full HD 1080p",
    ),
    165: (
        "OBJECT_MACRO",
        "serene countenance of judge remaining steady while rude heckler screams in court",
        "forewarned is forearmed, anticipated insults failing to trigger reactive rage, crisp Full HD 1080p",
    ),
    166: (
        "OBJECT_MACRO",
        "blindfolded traveler stumbling through brambles because he cannot see the path",
        "forgiving the ignorant: they do wrong because they lack moral sight, crisp Full HD 1080p",
    ),
    168: (
        "OBJECT_MACRO",
        "soldier packing sturdy shield and field rations at dawn before storming breached wall",
        "courageous preparation, meeting harsh eventualities with deliberate foresight, crisp Full HD 1080p",
    ),
    169: (
        "OBJECT_MACRO",
        "thick padded martial shield deflecting heavy iron javelin with soft dull thud",
        "cushioning the blow, foresight converting devastating crisis into manageable challenge, crisp Full HD 1080p",
    ),
    170: (
        "OBJECT_MACRO",
        "smooth rounded river stone that diverts torrent of water without losing single flake",
        "non-reactive resilience, deflecting malicious intent through inner hydrodynamic calm, crisp Full HD 1080p",
    ),
    172: (
        "OBJECT_MACRO",
        "sailors thoroughly inspecting ship hull caulking and ropes while sea is calm as glass",
        "pre-crisis preparation, fortifying defenses before tempest breaks on horizon, crisp Full HD 1080p",
    ),
    173: (
        "OBJECT_MACRO",
        "heavy iron anchor winched onto deck ready for emergency deployment at first squall",
        "readiness for deployment, steadfast emergency anchor ensuring survival in rocks, crisp Full HD 1080p",
    ),
    174: (
        "OBJECT_MACRO",
        "stone pier extending into ocean providing safe shelter behind its protective curve",
        "reliable harbor, internal sanctuary sheltering ship of mind from howling gale, crisp Full HD 1080p",
    ),
    175: (
        "OBJECT_MACRO",
        "sturdy wooden sea dike holding back surging high spring tide from coastal village",
        "steadfast barrier, resisting submerged currents without buckling under hydraulic head, crisp Full HD 1080p",
    ),
    177: (
        "OBJECT_MACRO",
        "antique Roman coin showing two-faced Janus looking simultaneously at birth and death",
        "cosmic cycle, understanding that every creation inevitably carries its dissolution, crisp Full HD 1080p",
    ),
    179: (
        "OBJECT_MACRO",
        "magnifying glass held over blooming cherry blossom appreciating its fragile beauty",
        "heightened gratitude, impermanence endowing present existence with exquisite sweetness, crisp Full HD 1080p",
    ),
    180: (
        "OBJECT_MACRO",
        "steaming cup of herbal tea shared between two companions beside warm stone hearth",
        "sanctified ordinary fellowship, savoring humble companionship as priceless treasure, crisp Full HD 1080p",
    ),
    181: (
        "OBJECT_MACRO",
        "two elderly friends conversing warmly on sunlit bench in autumn afternoon light",
        "intimate communion, shared laughter and honest talk cherished before winter arrives, crisp Full HD 1080p",
    ),
    183: (
        "OBJECT_MACRO",
        "monk sitting peacefully in open courtyard while autumn leaves drift gently around him",
        "unshakeable equanimity, serene presence amidst the swirling flux of world changes, crisp Full HD 1080p",
    ),
    184: (
        "OBJECT_MACRO",
        "bronze statue of Athena standing unwavering as dark storm clouds gather over Athens",
        "fearless fortitude, divine reason elevated above mortal terrors and phantom anxieties, crisp Full HD 1080p",
    ),
    186: (
        "MECHANISM_CUTAWAY",
        "diorama cutaway of fortified inner citadel tower rising high above outer besieged city",
        "the Inner Citadel: impregnable keep inside the soul that no external enemy can breach, crisp Full HD 1080p",
    ),
    187: (
        "OBJECT_MACRO",
        "polished steel mirror reflecting flying arrows and spears deflecting harmlessly off surface",
        "invulnerable shield of virtue, malicious gossip and weapon blades bouncing off harmlessly, crisp Full HD 1080p",
    ),
    188: (
        "OBJECT_MACRO",
        "warm glowing sanctuary hearth burning quietly behind impenetrable iron fortress door",
        "ultimate inner refuge, warm peaceful hearth accessible anytime by retreating within, crisp Full HD 1080p",
    ),
    190: (
        "OBJECT_MACRO",
        "crowded noisy Roman market bazaar with merchants shouting and cartwheels rattling on cobbles",
        "chaotic sensory overstimulation, urban cacophony testing mental concentration, crisp Full HD 1080p",
    ),
    191: (
        "OBJECT_MACRO",
        "quiet cloistered courtyard tucked immediately behind noisy market wall in shade",
        "instant transition to peace, step inside the inner chamber to find immediate stillness, crisp Full HD 1080p",
    ),
    192: (
        "SITUATIONAL_ACTION",
        "weary citizen stepping into shaded courtyard breathing deeply and touching calm chest",
        "retreating into the inner citadel, finding immediate haven within own conscious breath, crisp Full HD 1080p",
    ),
    193: (
        "OBJECT_MACRO",
        "small clear spring bubbling quietly in center of shaded courtyard surrounded by ferns",
        "inexhaustible inner wellspring, peace residing permanently within own spiritual core, crisp Full HD 1080p",
    ),
    195: (
        "OBJECT_MACRO",
        "ancient granite bedrock extending miles deep below shifting topsoil and dead leaves",
        "immutable foundation, eternal stillness underlying the transient movements of life, crisp Full HD 1080p",
    ),
    196: (
        "OBJECT_MACRO",
        "four seasons tree diorama: blooming spring green summer yellow autumn bare winter",
        "perpetual cosmic cycle, accepting natural birth maturation decay and renewal, crisp Full HD 1080p",
    ),
    197: (
        "OBJECT_MACRO",
        "withered brown maple leaf dropping naturally onto rich compost soil to nourish earth",
        "natural surrender, yielding to seasonal rotation without struggle or regret, crisp Full HD 1080p",
    ),
    198: (
        "OBJECT_MACRO",
        "astronomical astrolabe tracking eternal orbital revolutions of planets and stars",
        "cosmic harmony, mortal life integrated seamlessly into majestic universal order, crisp Full HD 1080p",
    ),
    200: (
        "SPLIT_COMPARISON",
        "split comparison of swimmer fighting against ocean rip current versus floating with it",
        "exhausting futile struggle on left contrasted with effortless survival on right, crisp Full HD 1080p",
    ),
    201: (
        "OBJECT_MACRO",
        "iron gate swinging wide open allowing river floodwater to pass harmlessly through",
        "releasing resistance, yielding to reality preventing structural destruction, crisp Full HD 1080p",
    ),
    202: (
        "OBJECT_MACRO",
        "supple willow branch bending smoothly under weight of snow until snow slides off",
        "wisdom of yielding, compliance with nature preserving branch from snapping, crisp Full HD 1080p",
    ),
    204: (
        "OBJECT_MACRO",
        "hand opening completely flat releasing dead bird back into forest soil beneath fern",
        "peaceful release, letting go of past attachments to make room for new journeys, crisp Full HD 1080p",
    ),
    206: (
        "SITUATIONAL_ACTION",
        "stoic philosopher standing calmly on elevated terrace gazing down at bustling forum",
        "elevation above petty squabbles, observing mundane drama with wise compassionate detachment, crisp Full HD 1080p",
    ),
    208: (
        "OBJECT_MACRO",
        "stonemason chisel shaping rough square granite block into perfect geometric keystone",
        "daily moral refinement, chiseling raw impulses into virtuous structured habits, crisp Full HD 1080p",
    ),
    209: (
        "OBJECT_MACRO",
        "single dressed stone block being placed precisely into defensive citadel parapet wall",
        "building character: each act of self-restraint lays an unshakeable block in fortress wall, crisp Full HD 1080p",
    ),
    210: (
        "OBJECT_MACRO",
        "mortar setting firmly between heavy stone blocks forming solid unified rampart",
        "integration of virtuous habits into impregnable fortress of moral character, crisp Full HD 1080p",
    ),
    212: (
        "OBJECT_MACRO",
        "massive fortified stone citadel standing proud atop mountain ridge bathed in sunset",
        "unconquerable soul, inner fortress fully built resisting any conceivable earthly crisis, crisp Full HD 1080p",
    ),
    213: (
        "OBJECT_MACRO",
        "unflickering oil lamp burning peacefully inside deep recessed alcove of fortress keep",
        "inviolable peace, no external catastrophe capable of stealing serenity from the citadel, crisp Full HD 1080p",
    ),
    215: (
        "SPLIT_COMPARISON",
        "split comparison of dusty academic lecture hall versus gritty wrestling gymnasium",
        "abstract theoretical lecturing on left contrasted with sweat and real combat practice on right, crisp Full HD 1080p",
    ),
    216: (
        "SITUATIONAL_ACTION",
        "stoic practitioner lifting heavy stone and practicing disciplined breathing in field",
        "embodied philosophy, training mental resilience through daily physical and moral tests, crisp Full HD 1080p",
    ),
    217: (
        "OBJECT_MACRO",
        "coarse woolen blanket and simple loaf of barley bread on bare wooden tabletop",
        "voluntary simplicity, training soul to be content with the most basic necessities, crisp Full HD 1080p",
    ),
    218: (
        "SPLIT_COMPARISON",
        "split comparison of reading philosophy book versus putting virtue into concrete action",
        "passive reading on left contrasted with intervening to stop injustice on right, crisp Full HD 1080p",
    ),
    220: (
        "OBJECT_MACRO",
        "stoic sage meeting insulting heckler with polite respectful smile and steady eyes",
        "disarming malice through unflinching courtesy, responding to insults with calm dignity, crisp Full HD 1080p",
    ),
    221: (
        "SPLIT_COMPARISON",
        "split composition showing angry speaker poison tongue versus serene listener armor",
        "insults revealing the speaker wounded sickness while passing harmlessly by the sage, crisp Full HD 1080p",
    ),
    222: (
        "OBJECT_MACRO",
        "arrow striking solid bronze cuirass and falling harmlessly into dust at warrior feet",
        "invulnerable dignity, external venom unable to penetrate self-respect of the virtuous, crisp Full HD 1080p",
    ),
    223: (
        "OBJECT_MACRO",
        "open attentive ears listening patiently to bitter complaint without defensive frown",
        "magnanimous hearing, absorbing grievances without resentment or counter-accusation, crisp Full HD 1080p",
    ),
    225: (
        "SITUATIONAL_ACTION",
        "practitioner stepping into freezing mountain stream bucket shower without flinching",
        "voluntary hardship exercise, training nervous system to master physical comfort cravings, crisp Full HD 1080p",
    ),
    226: (
        "SITUATIONAL_ACTION",
        "traveler walking patiently in rough woolen tunic through pouring cold autumn rain",
        "enduring discomfort cheerfully, proving happiness does not depend on mild weather, crisp Full HD 1080p",
    ),
    227: (
        "OBJECT_MACRO",
        "iron padlock snapped onto ornate box of luxury sweets demonstrating self-restraint",
        "conquest of appetite, voluntary restraint forging iron willpower and discipline, crisp Full HD 1080p",
    ),
    229: (
        "OBJECT_MACRO",
        "blacksmith steel tongs holding glowing iron bar quenching it in cold water trough",
        "tempering character, alternations of heat and cold hardening will into steel, crisp Full HD 1080p",
    ),
    230: (
        "OBJECT_MACRO",
        "hermit simple clay bowl holding water and wild berries on clean sunlit rock",
        "freedom of minimal needs, discovering how very little is required to live rich life, crisp Full HD 1080p",
    ),
    231: (
        "OBJECT_MACRO",
        "broken golden chains lying open on ground as barefoot philosopher walks into sun",
        "contentment as true wealth, he who needs least is richest and freest among men, crisp Full HD 1080p",
    ),
    233: (
        "OBJECT_MACRO",
        "carpenter plumb bob hanging motionless showing perfect vertical alignment over timber",
        "single-minded focus on present duty, absolute vertical alignment with moral obligation, crisp Full HD 1080p",
    ),
    234: (
        "SPLIT_COMPARISON",
        "split comparison of mind trapped in yesterday swamp versus lost in tomorrow fog",
        "regret in murky swamp on left versus dread in thick mist on right, crisp Full HD 1080p",
    ),
    235: (
        "OBJECT_MACRO",
        "bright sunlit stepping stone of right now standing firm between two dark chasms",
        "the eternal now, the only territory where human action and virtue can ever exist, crisp Full HD 1080p",
    ),
    236: (
        "OBJECT_MACRO",
        "hourglass with sand flowing right now illuminated by concentrated optical spotlight",
        "this present moment belongs to you alone, claim it with total focus and reverence, crisp Full HD 1080p",
    ),
    238: (
        "SITUATIONAL_ACTION",
        "artisan hands actively carving wood block with total absorption and precise skill",
        "immersion in duty, action dispelling anxiety as craftsman pours soul into work, crisp Full HD 1080p",
    ),
    239: (
        "OBJECT_MACRO",
        "dense morning fog evaporating completely as brilliant sun clears the mountain crest",
        "phantom future worries burning off before the radiant light of focused daily action, crisp Full HD 1080p",
    ),
    241: (
        "OBJECT_MACRO",
        "noble upright Roman citizen in toga walking with dignified stride through senate hall",
        "philosophy lived rather than debated, moral majesty visible in every stride and gesture, crisp Full HD 1080p",
    ),
    242: (
        "OBJECT_MACRO",
        "carved lion head on marble fountain pouring steady stream of clear water day and night",
        "unwavering virtue and nobility of spirit, constant generous flow of good character, crisp Full HD 1080p",
    ),
    244: (
        "OBJECT_MACRO",
        "sandy arena floor where boxing glove strikes heavy sandbag without breaking bag",
        "life as combat arena, training to absorb heavy blows without dropping guard, crisp Full HD 1080p",
    ),
    245: (
        "OBJECT_MACRO",
        "battered iron gladiator shield bearing hundreds of sword dents yet completely intact",
        "heroic resilience, bearing scars of combat with pride while structural integrity holds, crisp Full HD 1080p",
    ),
    246: (
        "SITUATIONAL_ACTION",
        "fighter rising decisively to feet from canvas floor refusing to concede defeat",
        "the unconquerable mind, refusing to yield internally no matter how hard life strikes, crisp Full HD 1080p",
    ),
    247: (
        "OBJECT_MACRO",
        "ancient bronze anvil remaining completely whole after million hammer strikes",
        "steadfast fortitude, enduring blows without anger while remaining unbroken and firm, crisp Full HD 1080p",
    ),
    249: (
        "OBJECT_MACRO",
        "open iron lock that cannot close unless internal tumbler mechanism turns",
        "Epictetus doctrine of consent: no one can hurt your soul without your own consent, crisp Full HD 1080p",
    ),
    250: (
        "OBJECT_MACRO",
        "balance scale where moral choice sits sovereign weighing external event against reason",
        "the sovereign faculty of judgment, power to decide whether an event is harm or opportunity, crisp Full HD 1080p",
    ),
    251: (
        "OBJECT_MACRO",
        "turbulent sea surrounding solitary lighthouse while lantern keeper tends wick calmly",
        "external chaos versus internal duty, keeping personal flame burning true regardless of storm, crisp Full HD 1080p",
    ),
    252: (
        "OBJECT_MACRO",
        "pristine white toga without single stain draped neatly over unbending iron chair",
        "uncompromised honor and integrity preserved through turbulent political crises, crisp Full HD 1080p",
    ),
    254: (
        "SITUATIONAL_ACTION",
        "philosopher opening heavy oak window shutters to welcome cold fresh dawn air",
        "embracing the present day with genuine courage and openhearted resolve, crisp Full HD 1080p",
    ),
    255: (
        "OBJECT_MACRO",
        "golden morning sunbeam illuminating Roman forum arches as day work begins",
        "living this single day fully as if it were the entirety of life, crisp Full HD 1080p",
    ),
    257: (
        "SITUATIONAL_ACTION",
        "stoic citizen walking forward into morning streets with calm purposeful stride",
        "stepping out as autonomous master of own soul, serene and ready for duty, crisp Full HD 1080p",
    ),
    258: (
        "OBJECT_MACRO",
        "serene countenance smiling with gentle humor at the absurdities of the world",
        "stoic cheerfulness, meeting human frailty with benevolence and warm amusement, crisp Full HD 1080p",
    ),
    259: (
        "OBJECT_MACRO",
        "radiant polished round bronze shield reflecting morning sun like blinding mirror",
        "impenetrable shield of virtue and inner peace protecting soul on journey through life, crisp Full HD 1080p",
    ),
}

if __name__ == "__main__":
    print(f"Total bespoke beats for minh_triet_song: {len(BESPOKE_BEATS)}")
    cores = [v[1][:60].lower() for v in BESPOKE_BEATS.values()]
    print(f"Unique cores count: {len(set(cores))}/{len(cores)}")
    assert len(set(cores)) == len(cores), f"Duplicates found: {len(cores) - len(set(cores))}"
    print("ALL 190 CORES ARE 100% UNIQUE!")
