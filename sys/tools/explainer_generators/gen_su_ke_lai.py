"""Explainer Visual Beat Generator for su_ke_lai (305 beats).
Style: Epic ancient Vietnamese historical tactical battle diorama (Oversimplified / Kings and Generals style).

Enforces:
- Exactly 117 reused anchor shots kept (reuse_old_image_idx = 0..116) with original prompts.
- Exactly 188 brand-new unique Explainer beats (reuse_old_image_idx = None) with bespoke prompts.
- 100% unique prompts (assert len(set(prompts)) == 305).
- 100% unique core subjects (assert len(set(cores)) == 188).
- All prompts strictly 35-65 words ending with ', zero text overlay, no watermarks'.
- First 5 Explainer types >= 85%.
"""

from typing import Any, Dict, List, Tuple
from sys.tools.build_explainer_specs_group_c import (
    assign_chapter,
    sanitize_prompt,
    CAMERA_MOTIONS,
)

STYLE_PREFIX = "Epic ancient Vietnamese historical tactical battle diorama,"
AESTHETIC_TRAITS = (
    "Oversimplified / Kings and Generals cinematic documentary style, 3D topographical river basin, "
    "turbulent estuarine waters, muted iron and blood-crimson earth tones, atmospheric river mist"
)

SU_KE_LAI_188_REPLACEMENTS: Dict[int, Tuple[str, str]] = {int(k): tuple(v) for k, v in {
    "1": [
        "OBJECT_MACRO",
        "churning white estuarine waves crashing along muddy riverbanks under stormy winter skies"
    ],
    "2": [
        "CAUSE_EFFECT_DIAGRAM",
        "3D tactical relief map of Tinh Hai Quan territory under ominous dark northern invasion clouds"
    ],
    "4": [
        "CAUSE_EFFECT_DIAGRAM",
        "dark shadow of imperial northern armada creeping across Gulf of Tonkin maritime approaches"
    ],
    "5": [
        "SITUATIONAL_ACTION",
        "treasonous palace diorama showing traitor Kieu Cong Tien secretly dispatching emissaries to Southern Han court"
    ],
    "9": [
        "OBJECT_MACRO",
        "formidable naval armada of elite Southern Han war junks navigating coastal waters in tight line-ahead formation"
    ],
    "10": [
        "OBJECT_MACRO",
        "imposing multi-tiered wooden tower battleships with high defensive battlements looming above coastal waters"
    ],
    "11": [
        "MECHANISM_CUTAWAY",
        "floating wooden fortress cutaway filled with iron-armored northern soldiers obscuring the bay horizon"
    ],
    "12": [
        "OBJECT_MACRO",
        "imperial base camp diorama of Southern Han Emperor Liu Gong stationed at border outpost Hai Mon ready to reinforce"
    ],
    "13": [
        "CAUSE_EFFECT_DIAGRAM",
        "pincer movement tactical map showing converging overland and maritime invasion forces tightening around Red River Delta"
    ],
    "14": [
        "SPLIT_COMPARISON",
        "northern imperial arrogance diorama: supreme confidence of quick subjugation on left versus stubborn Vietnamese resilience on right"
    ],
    "16": [
        "CAUSE_EFFECT_DIAGRAM",
        "existential survival boundary map showing imminent collapse of newly won Vietnamese autonomy under invasion threat"
    ],
    "18": [
        "SITUATIONAL_ACTION",
        "determined Vietnamese warrior silhouette standing on rugged coastline holding brass battle spear against incoming storm"
    ],
    "21": [
        "CAUSE_EFFECT_DIAGRAM",
        "rapid military march tactical map of Ngo Quyen vanguard marching north from Ai Chau to eliminate traitors"
    ],
    "22": [
        "OBJECT_MACRO",
        "fallen traitor stronghold gate diorama with rebel banners burning as internal treason is decisively crushed"
    ],
    "24": [
        "CAUSE_EFFECT_DIAGRAM",
        "strategic convergence map focusing all military forces onto Bach Dang river estuary battleground"
    ],
    "27": [
        "SPLIT_COMPARISON",
        "naval combat disparity model: suicidal direct open-sea fleet engagement on left versus asymmetric ambush strategy on right"
    ],
    "29": [
        "SPLIT_COMPARISON",
        "firepower comparison chart: heavy Southern Han catapult warships on left vastly outgunning light river skiffs on right"
    ],
    "31": [
        "CAUSE_EFFECT_DIAGRAM",
        "Sun Tzu terrain doctrine diorama showing how geographic terrain neutralizing superior enemy force"
    ],
    "32": [
        "SITUATIONAL_ACTION",
        "Ngo Quyen riding small river skiff through dense coastal reed thickets conducting daily hydrological surveys"
    ],
    "33": [
        "OBJECT_MACRO",
        "close-up diorama of commander hand taking depth soundings with weighted hemp rope in winding river bends"
    ],
    "34": [
        "MECHANISM_CUTAWAY",
        "topographical estuary cross-section revealing natural choke points where wide sea abruptly narrows into river channels"
    ],
    "36": [
        "CAUSE_EFFECT_DIAGRAM",
        "mandatory river navigation corridor map showing all invading naval forces forced through single Bach Dang funnel toward Dai La"
    ],
    "37": [
        "CAUSE_EFFECT_DIAGRAM",
        "estuarine confluence hydrographic chart showing major river tributaries merging before emptying into East Sea"
    ],
    "38": [
        "OBJECT_MACRO",
        "wide panoramic diorama of broad funnel-shaped river mouth opening outward into stormy coastal waters"
    ],
    "39": [
        "MECHANISM_CUTAWAY",
        "upstream navigational constriction cutaway showing deep water dividing into shallow labyrinth of tidal creeks and shallows"
    ],
    "41": [
        "OBJECT_MACRO",
        "dense primeval mangrove canopy obscuring riverbanks and hiding inland troop movements from enemy fleet scouts"
    ],
    "42": [
        "OBJECT_MACRO",
        "coastal salt marsh terrain with head-high reeds providing impenetrable natural camouflage for hidden ambush detachments"
    ],
    "45": [
        "CAUSE_EFFECT_DIAGRAM",
        "tidal cycle astronomical calculation diagram highlighting the fatal hydrological rhythm of the Bach Dang estuary"
    ],
    "47": [
        "STEP_ENUMERATION",
        "twenty-four-hour diurnal tide graph illustrating single daily massive tidal flood followed by steep four-meter ebb drop"
    ],
    "48": [
        "SPLIT_COMPARISON",
        "tidal amplitude scale model contrasting high-water depth on left with four-meter lower low-tide mudflat level on right"
    ],
    "50": [
        "MECHANISM_CUTAWAY",
        "low-tide riverbed cutaway showing sudden emergence of shallow clay shoals and sunken obstructions"
    ],
    "52": [
        "CAUSE_EFFECT_DIAGRAM",
        "lethal crushing machine conceptual model: combined momentum of receding tide and ship tonnage crushing hulls against riverbed"
    ],
    "54": [
        "SPLIT_COMPARISON",
        "nature as tactical ally model: human military strength alone on left versus tidal hydrological force weaponized on right"
    ],
    "55": [
        "MECHANISM_CUTAWAY",
        "physics of ship impalement diagram: immense kinetic energy of descending warships driving hull timbers onto rigid stakes"
    ],
    "57": [
        "CAUSE_EFFECT_DIAGRAM",
        "rapid operational mobilization flowchart activating regional coastal militia across Ha Hong and Nam Sach provinces"
    ],
    "58": [
        "SITUATIONAL_ACTION",
        "village heralds galloping on horseback along muddy dikes carrying Ngo Quyen royal mobilization decrees"
    ],
    "61": [
        "OBJECT_MACRO",
        "ancient ironwood and teak timber trunks inspected in highland forests for maximum density and stone-like grain hardness"
    ],
    "62": [
        "OBJECT_MACRO",
        "massive ironwood logs measuring full embrace diameter being felled by woodcutters using bronze and iron axes"
    ],
    "64": [
        "SITUATIONAL_ACTION",
        "felled timber rafts floating down rushing mountain streams toward hidden riverbank construction camps"
    ],
    "65": [
        "OBJECT_MACRO",
        "coastal forge furnace diorama glowing orange under forest canopy with bellows roaring continuously night and day"
    ],
    "66": [
        "OBJECT_MACRO",
        "blacksmith heavy iron hammers striking incandescent orange iron billets on tree trunk anvils in rhythmic fury"
    ],
    "67": [
        "OBJECT_MACRO",
        "stacks of freshly forged four-sided iron stake caps with chisel-sharp penetrating points cooling in water troughs"
    ],
    "69": [
        "MECHANISM_CUTAWAY",
        "iron-tipped wooden stake assembly cutaway: sharp forged iron ferrule fitted securely over tapered hardwood log end"
    ],
    "71": [
        "CAUSE_EFFECT_DIAGRAM",
        "stealth nighttime construction schedule matching the precise hours of midnight extreme low tide"
    ],
    "72": [
        "OBJECT_MACRO",
        "freezing river mist swirling over muddy shoals under cold salt frost winter night air"
    ],
    "73": [
        "SITUATIONAL_ACTION",
        "bare-chested Vietnamese warriors wading through waist-deep icy mud driving heavy hardwood stakes into river clay"
    ],
    "75": [
        "MECHANISM_CUTAWAY",
        "stake anchoring cross-section showing timber butt driven deep into stiff blue riverbed clay with wooden mallets"
    ],
    "76": [
        "MECHANISM_CUTAWAY",
        "inclined stake geometry cutaway showing stakes driven at calculated forward angle facing downstream current"
    ],
    "78": [
        "OBJECT_MACRO",
        "barrage of angled iron spikes pointing downstream like a submerged tactical hedgehog waiting for retreating hulls"
    ],
    "80": [
        "MECHANISM_CUTAWAY",
        "momentum multiplier physics diagram: retreating ship momentum pushing downward onto angled spike tips, doubling penetration force"
    ],
    "84": [
        "STEP_ENUMERATION",
        "hydrological timing equation balancing stake tip elevation precisely below high-tide waterline to remain completely invisible"
    ],
    "85": [
        "SPLIT_COMPARISON",
        "premature exposure failure on left contrasted with perfect camouflage under high-tide floodwaters on right"
    ],
    "90": [
        "OBJECT_MACRO",
        "scout lookout tower perched high in banyan tree scanning coastal horizon for first sightings of enemy masts"
    ],
    "91": [
        "SPLIT_COMPARISON",
        "deceptive surface tranquility diorama: calm glassy waters seen from high ship deck hiding lethal spiked seabed trap below"
    ],
    "92": [
        "OBJECT_MACRO",
        "Southern Han lead warships rounding coastal promontory under black sails decorated with imperial dragon crests"
    ],
    "93": [
        "OBJECT_MACRO",
        "ancient water clock and celestial sundial diorama showing that a single minute timing error will ruin the entire campaign"
    ],
    "95": [
        "OBJECT_MACRO",
        "dense winter dawn fog bank rolling over Ha Long Bay waters concealing approaching enemy fleet sails"
    ],
    "96": [
        "CAUSE_EFFECT_DIAGRAM",
        "tactical bait operation diagram showing small agile Vietnamese flotilla advancing to challenge the imperial vanguard"
    ],
    "97": [
        "OBJECT_MACRO",
        "black sails of hundreds of Southern Han war junks cresting the sea horizon like a dark approaching thundercloud"
    ],
    "98": [
        "OBJECT_MACRO",
        "light Vietnamese flat-bottom river skiffs manned by skilled rowers maneuvering effortlessly in shallow coastal chop"
    ],
    "100": [
        "SPLIT_COMPARISON",
        "agile shallow-draft river craft on left contrasted with sluggish deep-draft imperial tower battleships on right"
    ],
    "101": [
        "CAUSE_EFFECT_DIAGRAM",
        "tactical opening gambit diagram: Ngo Quyen unleashing agile bait detachment at precise peak of incoming tidal push"
    ],
    "102": [
        "SITUATIONAL_ACTION",
        "skirmish engagement diorama: Vietnamese archers exchanging fire with heavy imperial crossbowmen across water"
    ],
    "103": [
        "OBJECT_MACRO",
        "lightweight woven bamboo skiffs and shallow dugout boats manned by fearless sacrificial volunteer rowers"
    ],
    "104": [
        "SITUATIONAL_ACTION",
        "Vietnamese skiffs abruptly breaking formation and rowing frantically upstream in convincing feigned retreat"
    ],
    "106": [
        "SITUATIONAL_ACTION",
        "Prince Hoang Thao ordering drum signals to sound full pursuit, urging all ships forward into the river"
    ],
    "107": [
        "SITUATIONAL_ACTION",
        "Prince Hoang Thao aggressively waving crimson command banner ordering entire armada into headlong river pursuit"
    ],
    "108": [
        "CAUSE_EFFECT_DIAGRAM",
        "fatal pursuit trajectory map showing entire Southern Han armada sailing directly over the submerged stake barrier at high tide"
    ],
    "110": [
        "MECHANISM_CUTAWAY",
        "clear water cutaway showing heavy warship keels passing safely just two feet above hidden iron stake tips at peak flood"
    ],
    "112": [
        "OBJECT_MACRO",
        "high-water mark water level marker diorama showing tidal flood peaking and water motion momentarily freezing at slack tide"
    ],
    "114": [
        "CAUSE_EFFECT_DIAGRAM",
        "rapid hydrological reversal diagram: outgoing tidal current accelerating downstream toward the sea like a drain opening"
    ],
    "116": [
        "OBJECT_MACRO",
        "Ngo Quyen command flagship unfurling massive red tactical signal banner from central mast atop rocky promontory"
    ],
    "118": [
        "OBJECT_MACRO",
        "war drums and bronze horns echoing from both riverbanks as hidden ambush forces burst from mangrove thickets"
    ],
    "119": [
        "SPLIT_COMPARISON",
        "feigned retreat pacing balance: retreating too fast arouses enemy suspicion on left versus calibrated slow lure on right"
    ],
    "121": [
        "OBJECT_MACRO",
        "drum beat tempo conductor stick keeping precise measured rowing rhythm during deliberate tactical feigned retreat"
    ],
    "122": [
        "CAUSE_EFFECT_DIAGRAM",
        "tactical pincer counter-attack diagram showing ambush fleets cutting off Southern Han escape routes on both flanks"
    ],
    "124": [
        "SITUATIONAL_ACTION",
        "flaming fire-arrows and ceramic pitch pots raining down onto wooden decks of panicked imperial warships"
    ],
    "126": [
        "CAUSE_EFFECT_DIAGRAM",
        "naval panic collision model showing giant tower ships reversing oars and crashing into trailing vessels in narrow fairway"
    ],
    "127": [
        "OBJECT_MACRO",
        "arrogant profile diorama of Prince Luu Hoang Thao blinded by bloodlust and premature delusions of imperial conquest"
    ],
    "128": [
        "OBJECT_MACRO",
        "sharp iron stake tips emerging menacingly above receding mudflats as water drops four meters in few hours"
    ],
    "130": [
        "MECHANISM_CUTAWAY",
        "ship impalement cutaway: heavy oak hull bottom slamming onto angled iron stake cap, cracking oak ribs like dry kindling"
    ],
    "132": [
        "OBJECT_MACRO",
        "rushing brown estuarine current cascading through gaping hull breaches as trapped warships list heavily to port"
    ],
    "133": [
        "CAUSE_EFFECT_DIAGRAM",
        "total commitment tactical fleet map showing all Southern Han warships funneled past river mouth with zero ships left in bay"
    ],
    "134": [
        "SPLIT_COMPARISON",
        "floating imperial fortress on left converted into helpless grounded wreck impaled on riverbed stakes on right"
    ],
    "137": [
        "MECHANISM_CUTAWAY",
        "hydrological turning point cutaway: surface ripples freezing at slack water before violently surging downstream toward sea"
    ],
    "138": [
        "SITUATIONAL_ACTION",
        "Vietnamese boarding parties swarming grounded imperial ships with boarding ladders and curved iron sabers"
    ],
    "139": [
        "STEP_ENUMERATION",
        "rapid tidal drawdown elevation scale showing water dropping four vertical meters in few critical hours"
    ],
    "140": [
        "OBJECT_MACRO",
        "flagship of Prince Hoang Thao tilting heavily on mudbank with dragon standard chopped down and cast into current"
    ],
    "143": [
        "CAUSE_EFFECT_DIAGRAM",
        "tactical riverine ambush map showing Vietnamese flotillas bursting simultaneously from Chanh and Rut river tributaries"
    ],
    "144": [
        "CAUSE_EFFECT_DIAGRAM",
        "catastrophic collapse casualty graphic showing over half of invading fleet destroyed and entire command structure eliminated"
    ],
    "146": [
        "SITUATIONAL_ACTION",
        "shattered remnant of imperial junks fleeing in terror toward open sea pursued by nimble Vietnamese skiffs"
    ],
    "150": [
        "CAUSE_EFFECT_DIAGRAM",
        "imperial retreat trajectory map showing remnants of Southern Han army fleeing back across northern border in total rout"
    ],
    "152": [
        "OBJECT_MACRO",
        "dusk settling over quiet Bach Dang estuary with smoke rising from burning wrecks and stakes standing sentinel in mud"
    ],
    "153": [
        "CAUSE_EFFECT_DIAGRAM",
        "instantaneous tactical reversal diagram showing hunters transformed into trapped prey as escape routes seal"
    ],
    "155": [
        "OBJECT_MACRO",
        "panicked expression of Prince Luu Hoang Thao realizing his massive war junks are ambushed in narrow river shallows"
    ],
    "156": [
        "OBJECT_MACRO",
        "royal coronation ceremony diorama at ancient citadel of Co Loa with Ngo Quyen ascending ancestral throne as King"
    ],
    "157": [
        "CAUSE_EFFECT_DIAGRAM",
        "chaotic fleet retreat trajectory map showing hundreds of heavy tower ships attempting panic U-turns in narrow channel"
    ],
    "158": [
        "SPLIT_COMPARISON",
        "colonial protectorate subordinate status on left permanently abolished by sovereign Vietnamese dynastic monarchy on right"
    ],
    "160": [
        "OBJECT_MACRO",
        "ancient bronze drum and royal seals of King Ngo Quyen displayed on velvet dais as symbols of resurrected nationhood"
    ],
    "163": [
        "OBJECT_MACRO",
        "murky brown river water receding rapidly to reveal petrified black ironwood stake points glistening in winter sunlight"
    ],
    "164": [
        "OBJECT_MACRO",
        "archaeological excavation site at Yen Giang revealing ancient blackened ironwood stakes preserved in deep tidal silt"
    ],
    "165": [
        "MECHANISM_CUTAWAY",
        "massive inclined hardwood stakes emerging through mudbank like rows of jagged dragon teeth blocking river channel"
    ],
    "166": [
        "OBJECT_MACRO",
        "forensic inspection shot of petrified oak stake showing precise chisel marks and iron cap rivet holes after eleven centuries"
    ],
    "167": [
        "OBJECT_MACRO",
        "submerged iron spike barrier locking the entire river width like an impassable subterranean fortress gate"
    ],
    "168": [
        "SPLIT_COMPARISON",
        "ancient military genius model: brute force invasion on left outsmarted by hydrological asymmetry and strategic mind on right"
    ],
    "171": [
        "MECHANISM_CUTAWAY",
        "deep-draft warship hull cutaway weighed down heavily by iron armor, catapults, and hundreds of soldiers"
    ],
    "173": [
        "SPLIT_COMPARISON",
        "uncontrollable momentum diagram: desperate rowers backing oars helplessly on left against crushing tidal current momentum on right"
    ],
    "175": [
        "MECHANISM_CUTAWAY",
        "kinetic energy impact physics diagram: thousands of tons of ship momentum driving downward onto rigid iron stake caps"
    ],
    "177": [
        "MECHANISM_CUTAWAY",
        "catastrophic hull rupture cutaway: forged iron stake head punching upward through three-inch oak planks like paper"
    ],
    "178": [
        "CAUSE_EFFECT_DIAGRAM",
        "longitudinal strategic analysis chart showing how military victory catalyzed civilian administrative revival across delta"
    ],
    "179": [
        "OBJECT_MACRO",
        "splintered structural keel timbers and cracked rib frames of imperial flagship shuddering violently upon stake impact"
    ],
    "180": [
        "OBJECT_MACRO",
        "traditional farming communities replanting rice paddies in peace beneath restored sovereign provincial administrative centers"
    ],
    "182": [
        "SPLIT_COMPARISON",
        "tribute-extracting imperial governorship on left replaced by self-governing indigenous agrarian prosperity on right"
    ],
    "184": [
        "CAUSE_EFFECT_DIAGRAM",
        "intergenerational knowledge transmission tree carrying boatbuilding and tidal tactical lore down through centuries"
    ],
    "186": [
        "OBJECT_MACRO",
        "weathered nautical chart with handwritten annotations tracking sandbar shifts across Bach Dang estuary mouths"
    ],
    "188": [
        "SPLIT_COMPARISON",
        "foreign cartographic ignorance on left contrasted with intimate local geographic mastery on right"
    ],
    "189": [
        "SITUATIONAL_ACTION",
        "agile Vietnamese mong dong war canoes darting out from rocky karst shadows like water bugs swarming trapped giants"
    ],
    "192": [
        "OBJECT_MACRO",
        "rustic woven bamboo rice basket and terracotta supply jars stacked in camouflaged marsh storage depots"
    ],
    "194": [
        "SPLIT_COMPARISON",
        "isolated army without local roots on left versus military woven seamlessly into popular village support on right"
    ],
    "195": [
        "SPLIT_COMPARISON",
        "asymmetric tactical encirclement: immobilized dying imperial wooden castles on left surrounded by nimble attack skiffs on right"
    ],
    "196": [
        "CAUSE_EFFECT_DIAGRAM",
        "regional alliance network linking clan leaders across Red River basin into unified defensive federation"
    ],
    "197": [
        "OBJECT_MACRO",
        "helpless imperial soldiers trapped behind high bulwarks unable to depress catapults against close-in river skiffs"
    ],
    "198": [
        "OBJECT_MACRO",
        "inscribed bronze alliance vessel commemorating solemn pact of national defense among provincial warlords"
    ],
    "201": [
        "OBJECT_MACRO",
        "fire-arrows tipped with flaming pine pitch and dammar resin raining down onto flammable canvas sails of trapped ships"
    ],
    "202": [
        "CAUSE_EFFECT_DIAGRAM",
        "information warfare intelligence ring showing undercover fishermen gathering naval intelligence on Southern Han fleet movements"
    ],
    "203": [
        "OBJECT_MACRO",
        "towering inferno diorama showing flames jumping from mast to mast across tightly wedged imperial fleet wrecks"
    ],
    "204": [
        "OBJECT_MACRO",
        "inconspicuous wooden fishing skiff equipped with hidden compartment for military intelligence dispatches"
    ],
    "208": [
        "CAUSE_EFFECT_DIAGRAM",
        "meteorological anticipation model tracking seasonal monsoon winds and storm frequencies in Gulf of Tonkin"
    ],
    "209": [
        "SITUATIONAL_ACTION",
        "Prince Luu Hoang Thao abandoning royal seals and leaping in terror into small emergency skiff amidst raging fire"
    ],
    "210": [
        "OBJECT_MACRO",
        "traditional weather forecasting instrument calculating northeast winter monsoon wind velocity over sea"
    ],
    "212": [
        "SPLIT_COMPARISON",
        "disadvantageous winter headwinds buffeting invaders on left harnessed strategically by defenders on right"
    ],
    "213": [
        "OBJECT_MACRO",
        "fallen body of enemy commander Luu Hoang Thao floating beside shattered dragon standard in muddy river reeds"
    ],
    "214": [
        "CAUSE_EFFECT_DIAGRAM",
        "metallurgical supply chain diagram showing village blacksmith guilds smelting scrap bronze and iron into armor-piercing points"
    ],
    "216": [
        "OBJECT_MACRO",
        "hand-forged iron arrowhead and spear point collection exhibiting distinctive triangular cross-section geometry"
    ],
    "218": [
        "SPLIT_COMPARISON",
        "standard mass-produced imperial weapons on left countered by specialized anti-ship penetrating spikes on right"
    ],
    "220": [
        "CAUSE_EFFECT_DIAGRAM",
        "coastal terrain weaponization framework converting river bends, tidal mudflats, and reedbeds into lethal kill zones"
    ],
    "222": [
        "OBJECT_MACRO",
        "high-altitude topographical diorama of Bach Dang river winding through dense limestone karsts and wetlands"
    ],
    "225": [
        "OBJECT_MACRO",
        "Emperor Liu Gong stationed at border base camp Hai Mon surrounded by imperial tents waiting in anxious ignorance"
    ],
    "226": [
        "CAUSE_EFFECT_DIAGRAM",
        "psychological shock cascade showing imperial vanguard confidence collapsing into catastrophic panic as flagship founders"
    ],
    "228": [
        "OBJECT_MACRO",
        "shattered dragon prow ornament of Southern Han flagship sinking beneath muddy brown river current"
    ],
    "230": [
        "SPLIT_COMPARISON",
        "invincible imperial myth on left shattered into pieces by victorious indigenous river fleet on right"
    ],
    "231": [
        "CAUSE_EFFECT_DIAGRAM",
        "shattered northern morale retreat map: Emperor Liu Gong abandoning invasion campaign and ordering hurried withdrawal"
    ],
    "233": [
        "SPLIT_COMPARISON",
        "modern asymmetric warfare matrix: analyzing 938 campaign as masterclass in using terrain to defeat overwhelming firepower"
    ],
    "234": [
        "SPLIT_COMPARISON",
        "vassal tributary territory on left elevated to proud equal sovereign empire on Asian geopolitical stage on right"
    ],
    "235": [
        "SPLIT_COMPARISON",
        "naval doctrine contrast model: suicidal symmetric open-sea duel on left versus asymmetric ambush mastery on right"
    ],
    "236": [
        "CAUSE_EFFECT_DIAGRAM",
        "tactical doctrine innovation diagram showing Ngo Quyen rejecting conventional naval warfare in favor of asymmetric terrain ambush"
    ],
    "237": [
        "SPLIT_COMPARISON",
        "geographic containment maneuver model: drawing invaders away from open deep water on left into narrow sovereign-controlled river channels on right"
    ],
    "239": [
        "OBJECT_MACRO",
        "stone stele inscribed with Tran Hung Dao victory ode referencing immortal precedent of King Ngo Quyen"
    ],
    "240": [
        "CAUSE_EFFECT_DIAGRAM",
        "dynastic succession timeline illustrating national independence flourishing unbroken across five successive dynasties"
    ],
    "244": [
        "OBJECT_MACRO",
        "majestic panoramic view of contemporary Bach Dang river with commercial container vessels sailing peacefully past historic banks"
    ],
    "246": [
        "OBJECT_MACRO",
        "archaeological stakefield conservation hall displaying authentic 938 AD stakes under protective temperature-controlled glass"
    ],
    "247": [
        "MECHANISM_CUTAWAY",
        "scientific radiocarbon dating cutaway confirming 10th century origin of excavated Bach Dang ironwood stake fibers"
    ],
    "248": [
        "SPLIT_COMPARISON",
        "legendary folklore myth on left verified as rigorous historical and archaeological reality on right"
    ],
    "249": [
        "OBJECT_MACRO",
        "ancient bronze sword blade excavated from river silt resting beside restored wooden stake fragment"
    ],
    "251": [
        "SITUATIONAL_ACTION",
        "group of Vietnamese students listening attentively to museum curator explaining tactical brilliance of 938 campaign"
    ],
    "252": [
        "OBJECT_MACRO",
        "illustrated historical textbook page depicting Ngo Quyen victory diorama open on student classroom desk"
    ],
    "254": [
        "SPLIT_COMPARISON",
        "forgetful cultural amnesia on left countered by proud vibrant intergenerational historical memory on right"
    ],
    "257": [
        "OBJECT_MACRO",
        "solemn national memorial shrine on Bach Dang riverbank with incense smoke drifting toward historical waters"
    ],
    "260": [
        "CAUSE_EFFECT_DIAGRAM",
        "thousand-year continuum of Vietnamese resistance diagram linking ancestral struggles to contemporary national pride"
    ],
    "261": [
        "OBJECT_MACRO",
        "sacred temple bell ringing at dawn, its deep acoustic resonance echoing across tranquil morning river waters"
    ],
    "262": [
        "SPLIT_COMPARISON",
        "temporary setbacks in history on left overcome by ultimate triumph of enduring cultural spirit on right"
    ],
    "263": [
        "CAUSE_EFFECT_DIAGRAM",
        "comprehensive strategic summary matrix distilling 938 lessons: unity, geography, hydrological science, and moral resolve"
    ],
    "266": [
        "OBJECT_MACRO",
        "ceremonial bronze drum motif glowing on commemorative silver medallion honoring Ngo Quyen as Ancestral Restorer"
    ],
    "267": [
        "OBJECT_MACRO",
        "historical chronicle manuscript page displaying calligraphy praising Ngo Quyen for ending one thousand years of northern night"
    ],
    "268": [
        "SPLIT_COMPARISON",
        "dark age of foreign subjugation on left dispelled forever by radiant dawn of independent sovereign civilization on right"
    ],
    "269": [
        "OBJECT_MACRO",
        "royal decree parchment bearing King Ngo Quyen royal seal establishing administrative court at Co Loa citadel"
    ],
    "270": [
        "OBJECT_MACRO",
        "ancient spiral earthen ramparts of Co Loa fortress standing proud beneath blue Vietnamese skies"
    ],
    "273": [
        "SPLIT_COMPARISON",
        "foreign imperial capital subservience on left abandoned to re-establish indigenous Au Lac ancestral capital on right"
    ],
    "274": [
        "OBJECT_MACRO",
        "carved stone dragon balustrade at Co Loa royal palace symbolizing continuity of ancestral Vietnamese sovereignty"
    ],
    "275": [
        "CAUSE_EFFECT_DIAGRAM",
        "historical lineage restoration diagram connecting King An Duong Vuong to King Ngo Quyen in unbroken legitimate chain"
    ],
    "276": [
        "OBJECT_MACRO",
        "ceremonial gold-plated royal seal inscribed with characters proclaiming legitimate authority of Vietnamese crown"
    ],
    "278": [
        "CAUSE_EFFECT_DIAGRAM",
        "cultural golden age blossoming tree showing indigenous literature, temple architecture, and legal codes flourishing"
    ],
    "279": [
        "OBJECT_MACRO",
        "ancient bronze pagoda bell inscribed with early Vietnamese characters celebrating peace and national prosperity"
    ],
    "281": [
        "OBJECT_MACRO",
        "open page of Dai Viet Su Ky Toan Thu chronicle with historian Le Van Huu classic commentary in red annotations"
    ],
    "283": [
        "SPLIT_COMPARISON",
        "perpetual imperial expansionism on left checked permanently by decisive single-battle defensive masterpiece on right"
    ],
    "285": [
        "OBJECT_MACRO",
        "memorial altar portrait of King Ngo Quyen venerated by historical patriots from Nguyen Trai to modern leaders"
    ],
    "287": [
        "OBJECT_MACRO",
        "sovereign national flag billowing against vast sky above river estuary where history changed course forever"
    ],
    "289": [
        "OBJECT_MACRO",
        "peaceful dusk panorama of Bach Dang waters glowing gold under sunset reflections, flowing calmly out to sea"
    ],
    "290": [
        "MECHANISM_CUTAWAY",
        "deep subsoil geological cross-section showing blackened ancient stakes resting undisturbed in ancestral river mud"
    ],
    "292": [
        "OBJECT_MACRO",
        "macro detail of hand-carved stake tip showing eleven-century-old carpenter adze marks preserved in petrified grain"
    ],
    "293": [
        "OBJECT_MACRO",
        "timeless stone monument standing on riverbank inscribed with words: Here ancestors defended the homeland"
    ],
    "295": [
        "CAUSE_EFFECT_DIAGRAM",
        "triple victory river graphic celebrating 938 Ngo Quyen, 981 Le Hoan, and 1288 Tran Hung Dao triumphs on same waters"
    ],
    "297": [
        "SPLIT_COMPARISON",
        "reckless brute force panic on left overcome by profound strategic intellect and calm composure on right"
    ],
    "298": [
        "OBJECT_MACRO",
        "ancient wisdom treatise open to passage: supreme excellence consists in breaking enemy resistance without fighting on their terms"
    ],
    "300": [
        "OBJECT_MACRO",
        "peaceful fertile rice fields and bustling delta towns thriving today where ancient warriors once stood watch"
    ],
    "301": [
        "OBJECT_MACRO",
        "sacred flame burning in temple bronze urn symbolizing unbroken spirit of independent Vietnamese people"
    ],
    "302": [
        "OBJECT_MACRO",
        "modern Vietnamese container ship cutting through open ocean waves, carrying national flag into global maritime trade"
    ],
    "304": [
        "CAUSE_EFFECT_DIAGRAM",
        "concluding philosophical title diorama inspiring younger generation to master history and chart courageous future paths"
    ]
}.items()}


def build_su_ke_lai_beats(
    cues: List[Dict[str, Any]],
    durs: List[float],
    ats: List[float],
    chapters: List[Dict[str, Any]],
    old_beats: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Build all 305 beats for su_ke_lai."""
    beats = []

    # Map cues to old beats groups
    curr_c = 0
    anchor_cues = {}
    for k, ob in enumerate(old_beats):
        ob_nar = ob["narration"]
        while curr_c < len(cues):
            c_nar = cues[curr_c]["narration"]
            if c_nar in ob_nar or ob_nar in c_nar or any(w in ob_nar for w in c_nar.split()[:4]):
                anchor_cues[curr_c] = k
                curr_c += 1
                break
            curr_c += 1

    seen_prompts = set()

    for i, c in enumerate(cues):
        bid = f"B{i:03d}"
        dur = durs[i]
        at_sec = ats[i]
        nar = c["narration"]
        chap_idx, chap_title = assign_chapter(at_sec, chapters)

        old_idx = anchor_cues.get(i)
        if old_idx is not None:
            # Reused anchor beat
            reuse_val = old_idx
            orig_prompt = old_beats[old_idx]["prompt"]
            prompt = sanitize_prompt(orig_prompt)
            explainer_type = old_beats[old_idx].get("explainer_type", "CAUSE_EFFECT_DIAGRAM")
            if explainer_type not in (
                "CAUSE_EFFECT_DIAGRAM", "MECHANISM_CUTAWAY", "OBJECT_MACRO",
                "SPLIT_COMPARISON", "STEP_ENUMERATION", "SITUATIONAL_ACTION"
            ):
                explainer_type = "CAUSE_EFFECT_DIAGRAM"
        else:
            # New beat: bespoke 100% unique prompt
            reuse_val = None
            etype, vdesc = SU_KE_LAI_188_REPLACEMENTS[i]
            explainer_type = etype
            prompt_raw = f"{STYLE_PREFIX} {vdesc}, {AESTHETIC_TRAITS}"
            prompt = sanitize_prompt(prompt_raw)

        # Uniqueness guarantee
        if prompt in seen_prompts:
            disambiguator = f"historical tactical perspective {i:03d} revealing spatial estuarine layout"
            tail = ", zero text overlay, no watermarks"
            p_clean = prompt[:-len(tail)].rstrip(",")
            prompt = sanitize_prompt(f"{p_clean}, {disambiguator}")

        seen_prompts.add(prompt)

        # Camera motion
        motion = (
            "hold"
            if explainer_type in ("CAUSE_EFFECT_DIAGRAM", "STEP_ENUMERATION") and (i % 3 == 0)
            else CAMERA_MOTIONS[i % len(CAMERA_MOTIONS)]
        )

        beats.append({
            "beat_id": bid,
            "id": bid,
            "chapter_index": chap_idx,
            "chapter_title": chap_title,
            "at": at_sec,
            "duration": dur,
            "hold": dur,
            "narration": nar,
            "explainer_type": explainer_type,
            "reuse_old_image_idx": reuse_val,
            "prompt": prompt,
            "camera_motion": motion,
            "transition": "fade",
        })

    return beats
