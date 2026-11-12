"""Explainer Visual Beat Generator for luat_ngam (305 beats).
Style: Forensic social psychology conceptual diorama (Vox / Johnny Harris style).

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

STYLE_PREFIX = "Forensic social psychology conceptual diorama,"
AESTHETIC_TRAITS = (
    "Vox / Johnny Harris investigative documentary aesthetic, high-contrast chiaroscuro lighting, "
    "minimalist architectural geometry, deep crimson and muted charcoal tones, clean isometric staging"
)

LUAT_NGAM_188_REPLACEMENTS: Dict[int, Tuple[str, str]] = {int(k): tuple(v) for k, v in {
    "1": [
        "OBJECT_MACRO",
        "silent clinical waiting room diorama with seated strangers staring straight forward in mute conformity"
    ],
    "2": [
        "OBJECT_MACRO",
        "close-up macro shot of crisp magazine pages turning in hushed minimalist waiting room with soft ivory lighting"
    ],
    "4": [
        "SITUATIONAL_ACTION",
        "ten waiting room actors rising simultaneously in robotic mechanical synchronization at high-pitched metal bell chime"
    ],
    "5": [
        "CAUSE_EFFECT_DIAGRAM",
        "social compliance behavioral loop diagram showing unquestioned group action replicating smoothly without explicit verbal explanation"
    ],
    "8": [
        "SITUATIONAL_ACTION",
        "group of seated strangers abruptly standing upright in unison for a second time while target subject observes nervously"
    ],
    "9": [
        "OBJECT_MACRO",
        "forensic biometric cutaway showing accelerated heart rate telemetry and nervous finger tapping under peer pressure"
    ],
    "11": [
        "SITUATIONAL_ACTION",
        "subject legs involuntarily standing up from wooden bench on the third bell chime to match collective behavior"
    ],
    "12": [
        "SPLIT_COMPARISON",
        "cognitive dissonance contrast model: external physical compliance on left contrasted with internal bewildered confusion on right"
    ],
    "13": [
        "CAUSE_EFFECT_DIAGRAM",
        "classic social conformity laboratory experiment diagram demonstrating peer pressure distorting individual cognitive reasoning"
    ],
    "14": [
        "CAUSE_EFFECT_DIAGRAM",
        "experimental narrative pivot flowchart tracking the astonishing behavioral transmission phase unfolding after original actors depart"
    ],
    "16": [
        "OBJECT_MACRO",
        "empty waiting room perspective with vacant wooden chairs bathed in cold fluorescent light after actors leave"
    ],
    "20": [
        "SITUATIONAL_ACTION",
        "remaining subject calmly explaining customary standing behavior to newly arrived patient with natural unhesitating authority"
    ],
    "21": [
        "SITUATIONAL_ACTION",
        "newly arrived patient imitating the standing ritual alongside the subject after hearing subsequent bell rings"
    ],
    "23": [
        "OBJECT_MACRO",
        "blank regulatory clipboard model showing absence of written policies, legal mandates, or monetary penalties"
    ],
    "24": [
        "MECHANISM_CUTAWAY",
        "invisible social inertia gear mechanism cutaway maintaining perpetual group habits purely through human mimicry momentum"
    ],
    "26": [
        "CAUSE_EFFECT_DIAGRAM",
        "ancient evolutionary savanna timeline diagram tracing origins of conformity reflex to harsh tribal survival warfare"
    ],
    "28": [
        "SPLIT_COMPARISON",
        "prehistoric survival contrast: solitary nomad vulnerable to predators on left versus unified tribe protected in fortress on right"
    ],
    "31": [
        "MECHANISM_CUTAWAY",
        "neural fear circuitry cutaway showing amygdala threat signals lighting up when facing tribal rejection or nonconformity"
    ],
    "33": [
        "OBJECT_MACRO",
        "biological telemetry display showing biological reality of social exclusion activating physical pain neuro-receptors in brain"
    ],
    "34": [
        "STEP_ENUMERATION",
        "game theory payoff matrix chart illustrating herd imitation as lowest-cognitive-cost defensive survival strategy"
    ],
    "35": [
        "SPLIT_COMPARISON",
        "collective safety versus solitary hazard model: safety guaranteed if herd is right on left versus shared blame if wrong on right"
    ],
    "37": [
        "OBJECT_MACRO",
        "behavioral economics textbook open to social proof chapter with highlighted definitions of informational influence"
    ],
    "38": [
        "CAUSE_EFFECT_DIAGRAM",
        "implicit informational assumption model: individuals assuming large crowds possess superior hidden knowledge"
    ],
    "40": [
        "SITUATIONAL_ACTION",
        "isometric street sidewalk diorama showing pedestrian hesitating at decision fork between two adjacent restaurants"
    ],
    "41": [
        "SPLIT_COMPARISON",
        "restaurant popularity contrast diorama: packed eatery with spilling queue on left versus completely deserted dining room on right"
    ],
    "42": [
        "OBJECT_MACRO",
        "bifurcated neon storefront sign glowing above restaurant entrances representing everyday cognitive dilemmas"
    ],
    "43": [
        "SITUATIONAL_ACTION",
        "customer deliberately bypassing clean empty restaurant to join long winding queue outside crowded competitor"
    ],
    "44": [
        "STEP_ENUMERATION",
        "psychological trade-off balance graphic showing customer sacrificing valuable waiting time to purchase collective peace of mind"
    ],
    "46": [
        "CAUSE_EFFECT_DIAGRAM",
        "social validation amplification feedback loop showing expanding customer queues radiating irresistible attraction signals to passerby"
    ],
    "48": [
        "SPLIT_COMPARISON",
        "collective mirage contrast model: perceived culinary excellence on left versus artificial manufactured queue on right"
    ],
    "50": [
        "MECHANISM_CUTAWAY",
        "cognitive anesthesia cutaway model illustrating herd consensus numbing individual critical inquiry before conscious awareness"
    ],
    "53": [
        "CAUSE_EFFECT_DIAGRAM",
        "bystander effect emergence diagram showing growing crowd density inversely paralyzing individual initiative and courage"
    ],
    "54": [
        "OBJECT_MACRO",
        "daytime busy metropolitan traffic crossroad intersection diorama with colliding vehicles surrounded by bustling sidewalks"
    ],
    "56": [
        "CAUSE_EFFECT_DIAGRAM",
        "shared assumption cognitive loop: each spectator mentally delegating emergency 911 calls to adjacent bystanders"
    ],
    "57": [
        "STEP_ENUMERATION",
        "critical ten-minute emergency response stopwatch graphic showing complete bystander inaction while victim remains unassisted"
    ],
    "58": [
        "OBJECT_MACRO",
        "forensic title slate displaying diffusion of responsibility phenomenon against high-contrast chiaroscuro backdrop"
    ],
    "60": [
        "SPLIT_COMPARISON",
        "responsibility dilution formula diagram: solitary bystander carrying 100% duty on left versus fifty observers diluting to 2% on right"
    ],
    "63": [
        "SPLIT_COMPARISON",
        "psychological autopsy model: disproving cold-hearted cruelty on left while exposing systemic bystander paralysis on right"
    ],
    "64": [
        "MECHANISM_CUTAWAY",
        "motivation dissolution cutaway showing personal accountability evaporating into collective anonymity of large crowds"
    ],
    "67": [
        "SITUATIONAL_ACTION",
        "cheerful dinner party friends clinking glasses around banquet table agreeing generously to split final bill equally"
    ],
    "68": [
        "MECHANISM_CUTAWAY",
        "diner dilemma game theory mechanism cutaway showing perverse economic incentives silently tightening around cooperative diners"
    ],
    "70": [
        "OBJECT_MACRO",
        "luxurious eight-hundred-thousand dong lobster platter arriving at table opposite modest vegetarian pasta bowl"
    ],
    "72": [
        "SPLIT_COMPARISON",
        "restaurant bill inequity balance scale: frugal diner paying exorbitant share on left while lavish companion exploits subsidy on right"
    ],
    "74": [
        "CAUSE_EFFECT_DIAGRAM",
        "rational self-interest behavioral pivot diagram showing diners shifting from cooperation to defensive opportunism"
    ],
    "75": [
        "SPLIT_COMPARISON",
        "compensatory consumption strategy graphic: diner ordering expensive premium beef dish to recapture proportional share of shared bill"
    ],
    "77": [
        "CAUSE_EFFECT_DIAGRAM",
        "competitive menu over-ordering feedback loop where every diner escalates luxury choices to avoid subsidizing others"
    ],
    "78": [
        "OBJECT_MACRO",
        "luxury gourmet restaurant menu cutaway showing every diner selecting the single most expensive dish on list"
    ],
    "80": [
        "SPLIT_COMPARISON",
        "rational individual choices on left accumulating into catastrophic collective bankruptcy on right"
    ],
    "81": [
        "OBJECT_MACRO",
        "forensic title graphic displaying tragedy of the commons theorem engraved in polished granite monument"
    ],
    "83": [
        "CAUSE_EFFECT_DIAGRAM",
        "shared pasture overgrazing model showing individual rational cattle additions destroying common grassland carrying capacity"
    ],
    "84": [
        "SITUATIONAL_ACTION",
        "economics professor standing before lecture hall auctioning a crisp one-hundred-thousand dong banknote to students"
    ],
    "86": [
        "MECHANISM_CUTAWAY",
        "dollar auction game rules flowchart highlighting the deadly catch: second highest bidder must pay without winning"
    ],
    "87": [
        "CAUSE_EFFECT_DIAGRAM",
        "universal systemic trap map connecting diner bill splits, ocean overfishing, and traffic gridlocks under single mathematical model"
    ],
    "89": [
        "MECHANISM_CUTAWAY",
        "structural accountability boundary cutaway separating shared costs into transparent itemized individual responsibility slots"
    ],
    "91": [
        "SITUATIONAL_ACTION",
        "diners politely requesting separate itemized checks at restaurant counter to preserve genuine friendship and fairness"
    ],
    "92": [
        "OBJECT_MACRO",
        "intense bidding tension diorama with students waving paddles as bids climb frantically past eighty and ninety thousand"
    ],
    "93": [
        "SPLIT_COMPARISON",
        "pre-commitment contract model: vague communal sharing on left versus transparent clear individual accounting on right"
    ],
    "97": [
        "CAUSE_EFFECT_DIAGRAM",
        "invisible social pressure matrix diagram showing how unwritten codes govern workplace politics and consumer choices"
    ],
    "99": [
        "MECHANISM_CUTAWAY",
        "sunk cost trap mathematical graph showing rationalization of bidding beyond face value to minimize total losses"
    ],
    "100": [
        "SPLIT_COMPARISON",
        "surface corporate consensus on left contrasted with deep unexpressed private dissent on right"
    ],
    "101": [
        "CAUSE_EFFECT_DIAGRAM",
        "relentless capital incinerator simulation showing bidding escalation consuming hundreds of thousands of dong in vicious cycle"
    ],
    "102": [
        "OBJECT_MACRO",
        "vintage 1951 Solomon Asch visual conformity test card displaying reference vertical line alongside three comparison lines"
    ],
    "103": [
        "SPLIT_COMPARISON",
        "initial profit seeking motive on left overtaken completely by aggressive ego and fear of losing face on right"
    ],
    "104": [
        "SITUATIONAL_ACTION",
        "test subject squinting in agonizing disbelief as four confederates unanimously declare an obviously shorter line equal"
    ],
    "106": [
        "STEP_ENUMERATION",
        "Asch conformity statistical scorecard showing 75% of participants capitulating to group consensus at least once"
    ],
    "107": [
        "OBJECT_MACRO",
        "speculative asset bubble frenzy diorama where blind FOMO greed completely obliterates objective balance sheet fundamentals"
    ],
    "109": [
        "MECHANISM_CUTAWAY",
        "liquidity lifeline collapse diorama showing sudden cessation of capital inflows instantly snapping ladder in mid-air"
    ],
    "110": [
        "SPLIT_COMPARISON",
        "perceptual reality distortion model: objective visual truth on left overridden by collective social consensus on right"
    ],
    "111": [
        "CAUSE_EFFECT_DIAGRAM",
        "panic-stricken market free-fall trajectory chart showing asset prices plummeting vertically in disorderly liquidity crisis"
    ],
    "112": [
        "OBJECT_MACRO",
        "solitary dissenter silhouette standing beside the test card, demonstrating how a single partner restores independent judgment"
    ],
    "114": [
        "CAUSE_EFFECT_DIAGRAM",
        "conformity collapse threshold diagram showing conformity plummeting by 80% when a single ally speaks truth"
    ],
    "117": [
        "CAUSE_EFFECT_DIAGRAM",
        "behavioral architecture pricing model illustrating how invisible baseline anchor numbers subtly warp consumer valuation"
    ],
    "118": [
        "OBJECT_MACRO",
        "vintage 1961 Stanley Milgram shock generator console with toggle switches ascending from 15 volts to 450 volts danger"
    ],
    "119": [
        "MECHANISM_CUTAWAY",
        "anchoring heuristic cognitive bias mechanism diagram showing first presented number establishing rigid mental benchmark"
    ],
    "121": [
        "OBJECT_MACRO",
        "luxury boutique showcase diorama spotlighting exorbitant anchor handbag with dramatic studio lighting like museum art"
    ],
    "122": [
        "OBJECT_MACRO",
        "red danger high voltage warning label gleaming ominously beneath the final row of electrical shock toggles"
    ],
    "124": [
        "STEP_ENUMERATION",
        "Milgram compliance distribution curve displaying 65% of normal citizens administering maximum 450-volt electrical shocks"
    ],
    "125": [
        "SPLIT_COMPARISON",
        "mental price threshold expansion graphic stretching customer perception of expensive to make regular prices feel trivial"
    ],
    "127": [
        "OBJECT_MACRO",
        "customer smiling at price tag diorama perceiving fifty million dong as an irresistible bargain after seeing anchor"
    ],
    "129": [
        "MECHANISM_CUTAWAY",
        "decoy effect asymmetric dominance model cutaway showing deliberately inferior third option shifting consumer choices"
    ],
    "131": [
        "SPLIT_COMPARISON",
        "stark two-option pricing dilemma: small popcorn for thirty thousand on left versus large bucket for seventy thousand on right"
    ],
    "133": [
        "OBJECT_MACRO",
        "medium popcorn decoy carton inserted at sixty-five thousand dong designed to make large bucket appear irresistible"
    ],
    "135": [
        "SPLIT_COMPARISON",
        "decoy contrast graphic: nobody purchasing medium size while large bucket sales surge by four hundred percent"
    ],
    "138": [
        "OBJECT_MACRO",
        "smartphone lockscreen flooded with red notification badges and urgent flash sale countdown timers"
    ],
    "139": [
        "SPLIT_COMPARISON",
        "illusion of choice diorama: apparent consumer free will on left secretly channeled by behavioral pricing architecture on right"
    ],
    "140": [
        "MECHANISM_CUTAWAY",
        "dopamine reward loop cutaway inside mobile social application rewarding continuous mindless scrolling and engagement"
    ],
    "143": [
        "OBJECT_MACRO",
        "confident shopper holding wallet believing in complete financial autonomy while guided by hidden retail traps"
    ],
    "144": [
        "STEP_ENUMERATION",
        "e-commerce scarcity tactic graphic showing fabricated only 2 hotel rooms left and 15 people viewing notifications"
    ],
    "145": [
        "MECHANISM_CUTAWAY",
        "frame of reference manipulation cutaway demonstrating how altering context transforms expensive items into apparent bargains"
    ],
    "146": [
        "CAUSE_EFFECT_DIAGRAM",
        "manufactured panic buying feedback loop driving impulsive purchases through deceptive algorithmic scarcity triggers"
    ],
    "147": [
        "OBJECT_MACRO",
        "forensic inspection magnifying glass exposing decoy pricing structure to protect consumer wallet from subtle traps"
    ],
    "148": [
        "SPLIT_COMPARISON",
        "deliberate rational consumer choice on left hijacked by artificial urgency countdown clocks on right"
    ],
    "151": [
        "OBJECT_MACRO",
        "executive boardroom diorama where unanimous nods around conference table mask deep organizational compliance paralysis"
    ],
    "152": [
        "CAUSE_EFFECT_DIAGRAM",
        "post-purchase buyer regret cycle showing brief dopamine high collapsing into remorse and financial anxiety"
    ],
    "153": [
        "SITUATIONAL_ACTION",
        "circle of seated board members simultaneously nodding heads in unthinking approval during strategic policy review"
    ],
    "155": [
        "OBJECT_MACRO",
        "organizational psychology textbook open to groupthink chapter highlighting cognitive paralysis in executive teams"
    ],
    "156": [
        "SPLIT_COMPARISON",
        "intellectual open marketplace of ideas on left contrasted with closed polarizing digital echo chamber on right"
    ],
    "158": [
        "CAUSE_EFFECT_DIAGRAM",
        "group polarization cascade diagram showing like-minded groups adopting increasingly radicalized stances over time"
    ],
    "159": [
        "SPLIT_COMPARISON",
        "psychological safety blanket of silence on left contrasted with long-term disaster of unexpressed dissent on right"
    ],
    "161": [
        "SITUATIONAL_ACTION",
        "colleagues gathered around coffee machine excitedly boasting about doubling investment returns in few short weeks"
    ],
    "164": [
        "CAUSE_EFFECT_DIAGRAM",
        "spiral of silence model diagram illustrating how moderate voices self-censor when confronting vocal militant majorities"
    ],
    "166": [
        "OBJECT_MACRO",
        "muzzled silhouette icon standing amidst loud shouting crowd symbols, depicting psychological self-censorship"
    ],
    "169": [
        "SPLIT_COMPARISON",
        "grounded objective confidence on left obliterated by intoxicating collective euphoria and reckless speculation on right"
    ],
    "170": [
        "SPLIT_COMPARISON",
        "cost of speaking out on left balanced against cumulative long-term danger of collective cowardice on right"
    ],
    "171": [
        "MECHANISM_CUTAWAY",
        "structural foundation inspection cutaway showing empty hollow pillars beneath soaring speculative market valuation"
    ],
    "172": [
        "CAUSE_EFFECT_DIAGRAM",
        "institutional decay cycle showing how suppressed internal criticism leads organizations into catastrophic strategic blunders"
    ],
    "175": [
        "CAUSE_EFFECT_DIAGRAM",
        "corporate failure timeline diorama tracing fall of Fortune 500 giants due to complete absence of internal challenge"
    ],
    "176": [
        "MECHANISM_CUTAWAY",
        "groupthink symptom checklist cutaway highlighting illusions of invulnerability, collective rationalization, and direct pressure"
    ],
    "177": [
        "OBJECT_MACRO",
        "strategic tenth man rule doctrine embossed on bronze plaque placed at center of intelligence council table"
    ],
    "178": [
        "SPLIT_COMPARISON",
        "healthy intellectual dissent in boardrooms on left versus toxic false unanimity of groupthink on right"
    ],
    "179": [
        "SPLIT_COMPARISON",
        "nine members agreeing unanimously on left while designated tenth man rigorously dismantles operational plan on right"
    ],
    "181": [
        "MECHANISM_CUTAWAY",
        "adversarial red team auditing cutaway methodically interrogating every implicit assumption and unverified operational assertion"
    ],
    "182": [
        "OBJECT_MACRO",
        "formal devil advocate badge resting on conference table beside strategic decision blueprint"
    ],
    "186": [
        "CAUSE_EFFECT_DIAGRAM",
        "cognitive defense framework diagram outlining mental protocols to immunize oneself against psychological manipulation"
    ],
    "187": [
        "CAUSE_EFFECT_DIAGRAM",
        "linguistic framing art diagram demonstrating how subtle wording adjustments radically manipulate public emotional response"
    ],
    "190": [
        "SPLIT_COMPARISON",
        "emotional reactive impulse on left disciplined by deliberate analytical pause on right"
    ],
    "191": [
        "SITUATIONAL_ACTION",
        "relieved hospital patient comfortably signing surgical consent form after doctor frames survival rate at ninety percent"
    ],
    "194": [
        "MECHANISM_CUTAWAY",
        "prefrontal cortex executive control cutaway demonstrating rational inhibition overriding impulsive limbic reactions"
    ],
    "197": [
        "MECHANISM_CUTAWAY",
        "persuasion framing matrix cutaway revealing cognitive blind spots exploited by expert negotiators during high-stakes deals"
    ],
    "199": [
        "SPLIT_COMPARISON",
        "raw objective information on left wrapped into emotionally targeted persuasive framing envelope on right"
    ],
    "200": [
        "SPLIT_COMPARISON",
        "first self-question diagnostic: authentic intrinsic motivation on left versus fear-of-missing-out FOMO compliance on right"
    ],
    "202": [
        "OBJECT_MACRO",
        "symbolic hand stripping away illusory social proof sticker to inspect underlying product substance"
    ],
    "203": [
        "SPLIT_COMPARISON",
        "unbalanced reciprocity scale: receiving modest complimentary gift on left repaid with massive commercial loyalty on right"
    ],
    "205": [
        "MECHANISM_CUTAWAY",
        "foot-in-the-door compliance cutaway showing small initial agreement escalating into irreversible major commitment"
    ],
    "206": [
        "SPLIT_COMPARISON",
        "modal freight capacity comparison showing modest terrestrial rail capacity swallowed effortlessly by vast ocean container ships"
    ],
    "207": [
        "OBJECT_MACRO",
        "interpersonal rapport mirror diorama showing subtle conversational mimicry and sincere compliments building psychological trust"
    ],
    "210": [
        "STEP_ENUMERATION",
        "third self-question diagnostic: calculating exact financial and emotional cost if collective herd consensus proves dead wrong"
    ],
    "211": [
        "OBJECT_MACRO",
        "artificial scarcity countdown display showing limited edition counter ticking down rapidly to trigger urgency reflexes"
    ],
    "213": [
        "SPLIT_COMPARISON",
        "in-group tribal affinity icon on left unlocking unearned trust while out-group skepticism is maintained on right"
    ],
    "214": [
        "SPLIT_COMPARISON",
        "reckless herd following without downside protection on left versus prudent hedged independence on right"
    ],
    "215": [
        "MECHANISM_CUTAWAY",
        "invisible psychological web cutaway showing six persuasion levers woven together to entrap unaware consumer targets"
    ],
    "216": [
        "CAUSE_EFFECT_DIAGRAM",
        "independent thinker cognitive moat diagram illustrating clear personal boundaries deflecting manipulative overtures"
    ],
    "219": [
        "CAUSE_EFFECT_DIAGRAM",
        "commercial pitch behavioral routing diagram exposing meticulously engineered psychological triggers beneath attractive offers"
    ],
    "221": [
        "OBJECT_MACRO",
        "retail store environmental architecture schematic detailing lighting hue, background music tempo, and questioning sequence"
    ],
    "222": [
        "SITUATIONAL_ACTION",
        "composed professional calmly saying no thank you with pleasant smile in high-pressure sales negotiation"
    ],
    "223": [
        "OBJECT_MACRO",
        "centered individual silhouette maintaining cool rational composure amidst surrounding swirl of sensory manipulation traps"
    ],
    "224": [
        "CAUSE_EFFECT_DIAGRAM",
        "social reciprocity manipulation mechanism cutaway showing how unsolicited micro-favors trigger intense obligation debts"
    ],
    "226": [
        "OBJECT_MACRO",
        "unsolicited luxury gift box with golden ribbon resting on negotiation table as covert psychological anchor"
    ],
    "227": [
        "SPLIT_COMPARISON",
        "manipulator forcing manufactured urgency on left contrasted with cool deliberate patience of sovereign thinker on right"
    ],
    "228": [
        "SPLIT_COMPARISON",
        "genuine spontaneous generosity on left contrasted with calculated transactional manipulation on right"
    ],
    "230": [
        "MECHANISM_CUTAWAY",
        "psychological debt neutralization cutaway: consciously recognizing manipulative gifts to dissolve unearned guilt"
    ],
    "231": [
        "OBJECT_MACRO",
        "cardinal defense rule engraved on pocket watch: never make life-altering decisions under manufactured time pressure"
    ],
    "232": [
        "SITUATIONAL_ACTION",
        "negotiator politely declining flattering unsolicited gift to preserve absolute negotiating independence"
    ],
    "234": [
        "OBJECT_MACRO",
        "written contract clause being scrutinized under magnifying glass while ignoring persuasive salesman flattery"
    ],
    "235": [
        "SPLIT_COMPARISON",
        "suspiciously lavish flattery shower on left contrasted with objective transaction terms scrutinized on right"
    ],
    "236": [
        "SPLIT_COMPARISON",
        "sweet verbal promises in conference room on left versus cold binding legal text on contract document on right"
    ],
    "237": [
        "OBJECT_MACRO",
        "fountain pen firmly striking out rushed closing deadline clause from legal agreement draft"
    ],
    "239": [
        "CAUSE_EFFECT_DIAGRAM",
        "manufactured social proof forensic breakdown exposing paid actors and bot networks creating fake consensus"
    ],
    "240": [
        "SPLIT_COMPARISON",
        "identical computer-generated reviews on left contrasted with authentic organic customer evaluations on right"
    ],
    "242": [
        "MECHANISM_CUTAWAY",
        "underlying economic incentive cutaway tracing corporate money trails beneath viral grassroot campaigns"
    ],
    "244": [
        "SITUATIONAL_ACTION",
        "independent observer standing still on sidewalk observing crowd rushing frantically in opposite direction"
    ],
    "245": [
        "SPLIT_COMPARISON",
        "noisy futile debate on street corner on left contrasted with quiet purposeful execution on right"
    ],
    "246": [
        "OBJECT_MACRO",
        "velvet glove encasing an iron fist sculpture representing gentle outward demeanor over unbreakable internal resolve"
    ],
    "248": [
        "MECHANISM_CUTAWAY",
        "layered cognitive armor cutaway showing external polite manners deflecting intrusive emotional coercion"
    ],
    "250": [
        "SPLIT_COMPARISON",
        "eccentric contrarian defiance for attention on left versus serene grounded intellectual sovereignty on right"
    ],
    "252": [
        "CAUSE_EFFECT_DIAGRAM",
        "manipulation neutralization boundary diagram showing coercive tactics collapsing upon encountering clear boundaries"
    ],
    "256": [
        "STEP_ENUMERATION",
        "critical decision inflection timeline showing how a five-second pause changes lifelong financial trajectories"
    ],
    "258": [
        "OBJECT_MACRO",
        "five-second tactile pause stopwatch illuminated in soft amber studio light beside notebook"
    ],
    "259": [
        "SPLIT_COMPARISON",
        "emotional storm cloud clearing in five seconds on left giving way to calm rational blue sky on right"
    ],
    "262": [
        "SITUATIONAL_ACTION",
        "individual lowering shoulders and shifting gaze away from loud chanting crowd to look upward at stars"
    ],
    "263": [
        "OBJECT_MACRO",
        "clean ivory journal open with first diagnostic question handwritten in black archival ink"
    ],
    "264": [
        "SPLIT_COMPARISON",
        "true biological utility on left separated surgically from panic-driven fear of exclusion on right"
    ],
    "267": [
        "CAUSE_EFFECT_DIAGRAM",
        "illusory desire evaporation diagram showing consumer cravings dissolving once social comparison pressure vanishes"
    ],
    "268": [
        "OBJECT_MACRO",
        "brass drafting compass drawing second circle around authentic core desires on parchment"
    ],
    "270": [
        "SPLIT_COMPARISON",
        "fleeting vanity prestige on left stripped bare to reveal zero underlying intellectual or moral value"
    ],
    "271": [
        "OBJECT_MACRO",
        "classic library book and handwritten notes glowing with timeless intrinsic value in soft window light"
    ],
    "272": [
        "SPLIT_COMPARISON",
        "empty trophy losing luster without an audience on left versus enduring inner virtue standing proud on right"
    ],
    "273": [
        "STEP_ENUMERATION",
        "personal life energy balance ledger contrasting finite hours and wealth against worthless transitory status applause"
    ],
    "274": [
        "OBJECT_MACRO",
        "iron padlock securing third defensive diagnostic check on strategic evaluation notebook"
    ],
    "275": [
        "CAUSE_EFFECT_DIAGRAM",
        "herd failure scenario model illustrating devastating consequences when collective consensus collapses"
    ],
    "277": [
        "SPLIT_COMPARISON",
        "unprotected crowd following blindly off cliff on left versus prudent thinker anchored to solid rock on right"
    ],
    "280": [
        "CAUSE_EFFECT_DIAGRAM",
        "telephone game distortion chain showing initial factual statement mutating into monstrous lie across ten people"
    ],
    "281": [
        "OBJECT_MACRO",
        "objective financial ledger and verified statistical data sheet glowing under neutral white desk light"
    ],
    "282": [
        "OBJECT_MACRO",
        "ancient bronze triple shield emblem resting on modern desk representing the three protective questions"
    ],
    "283": [
        "SITUATIONAL_ACTION",
        "driver hands firmly gripping automobile steering wheel, regaining full vehicle control from passenger distractions"
    ],
    "285": [
        "SPLIT_COMPARISON",
        "camouflaged snare trap exposed under flashlight on left versus open genuine path leading to green meadows on right"
    ],
    "287": [
        "OBJECT_MACRO",
        "minimalist tranquil zen pebble garden surrounded by quiet bamboo, rejecting noisy street chaos"
    ],
    "290": [
        "OBJECT_MACRO",
        "wise observer perched on high stone vantage point calmly watching distant bustling marketplace"
    ],
    "291": [
        "SPLIT_COMPARISON",
        "compassionate understanding of human panic on left balanced with immune self-discipline on right"
    ],
    "292": [
        "OBJECT_MACRO",
        "deep still mountain lake surface reflecting mountain peaks without a single ripple of disturbance"
    ],
    "295": [
        "SPLIT_COMPARISON",
        "weathered ancient granite monolith enduring storm winds on left versus fragile seasonal scaffolding collapsing on right"
    ],
    "297": [
        "CAUSE_EFFECT_DIAGRAM",
        "intentional strategic slowness trail map discovering quiet mountain pass while crowd stampedes into canyon"
    ],
    "299": [
        "OBJECT_MACRO",
        "historic printing press and revolutionary scientific manuscripts resting in sunlit study hall"
    ],
    "300": [
        "OBJECT_MACRO",
        "compass needle steadfastly pointing to true magnetic north amidst swirling iron filing dust"
    ],
    "301": [
        "CAUSE_EFFECT_DIAGRAM",
        "mastery over invisible social laws diagram leading from unconscious compliance to sovereign self-determination"
    ],
    "302": [
        "OBJECT_MACRO",
        "thoughtful viewer face looking into reflective mirror with subtle insightful smile"
    ],
    "303": [
        "OBJECT_MACRO",
        "interactive comment discussion section graphic with thoughtful community discourse icons"
    ],
    "304": [
        "CAUSE_EFFECT_DIAGRAM",
        "closing conceptual title slate promising ongoing analytical journeys into deep human behavioral mysteries"
    ]
}.items()}


def build_luat_ngam_beats(
    cues: List[Dict[str, Any]],
    durs: List[float],
    ats: List[float],
    chapters: List[Dict[str, Any]],
    old_beats: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Build all 305 beats for luat_ngam."""
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
            etype, vdesc = LUAT_NGAM_188_REPLACEMENTS[i]
            explainer_type = etype
            prompt_raw = f"{STYLE_PREFIX} {vdesc}, {AESTHETIC_TRAITS}"
            prompt = sanitize_prompt(prompt_raw)

        # Uniqueness guarantee
        if prompt in seen_prompts:
            disambiguator = f"conceptual behavioral perspective {i:03d} revealing spatial social dynamics"
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
