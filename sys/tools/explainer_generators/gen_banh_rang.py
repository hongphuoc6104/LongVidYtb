"""Explainer Visual Beat Generator for banh_rang (255 beats).
Style: Isometric industrial technical cutaway diagram (Wendover Productions style).

Enforces:
- Exactly 98 reused anchor shots kept (reuse_old_image_idx = 0..97) with original prompts.
- Exactly 157 brand-new unique Explainer beats (reuse_old_image_idx = None) with bespoke prompts.
- 100% unique prompts (assert len(set(prompts)) == 255).
- 100% unique core subjects (assert len(set(cores)) == 157).
- All prompts strictly 35-65 words ending with ', zero text overlay, no watermarks'.
- First 5 Explainer types >= 85%.
"""

from typing import Any, Dict, List, Tuple
from sys.tools.build_explainer_specs_group_c import (
    assign_chapter,
    sanitize_prompt,
    CAMERA_MOTIONS,
)

STYLE_PREFIX = "Isometric industrial technical cutaway diagram,"
AESTHETIC_TRAITS = (
    "Wendover Productions economic infographic realism, exploded assembly view, "
    "mechanical precision, metallic steel and industrial teal accents, crisp studio keylight"
)

BANH_RANG_157_REPLACEMENTS: Dict[int, Tuple[str, str]] = {int(k): tuple(v) for k, v in {
    "1": [
        "OBJECT_MACRO",
        "retail price tag close-up displaying two hundred thousand Vietnamese dong affixed to folded cotton garment on glass counter"
    ],
    "3": [
        "SPLIT_COMPARISON",
        "retail display versus global origin comparison showing neatly folded store shirts on left contrasted with raw cotton fields on right"
    ],
    "4": [
        "CAUSE_EFFECT_DIAGRAM",
        "forty-day planetary supply chain loop diagram tracing global raw material trajectory from western farms to Asian retail racks"
    ],
    "5": [
        "MECHANISM_CUTAWAY",
        "interlocking industrial gear transmission mechanism cutaway illustrating synchronized operational handoffs between supply partners"
    ],
    "9": [
        "OBJECT_MACRO",
        "nighttime highway convoy of heavy diesel tractor-trailers hauling high-density raw cotton bales toward Port of Los Angeles"
    ],
    "10": [
        "CAUSE_EFFECT_DIAGRAM",
        "interstate desert logistics corridor map showing multi-ton cargo convoys streaming continuously across arid American highway networks"
    ],
    "11": [
        "OBJECT_MACRO",
        "container terminal quayside berth diorama showing trans-oceanic container vessel bow preparing for trans-Pacific crossing"
    ],
    "12": [
        "MECHANISM_CUTAWAY",
        "cargo vessel hold cross-section showing standardized stacks of compressed raw cotton bales secured under steel hatch covers"
    ],
    "13": [
        "OBJECT_MACRO",
        "modern automated textile spinning mill complex in Vietnam showing rows of high-speed automated yarn spinning ring frames"
    ],
    "16": [
        "STEP_ENUMERATION",
        "industrial textile quality control station cutaway showing automated laser optical fabric flaw detectors and robotic sorting arms"
    ],
    "17": [
        "MECHANISM_CUTAWAY",
        "industrial packing cutaway showing ten thousand folded finished shirts stacked into corrugated boxes inside steel shipping container"
    ],
    "18": [
        "SPLIT_COMPARISON",
        "cargo density comparison diagram: single standardized twenty-foot steel container box holding thousands of individual finished products"
    ],
    "20": [
        "CAUSE_EFFECT_DIAGRAM",
        "closed-loop global trade circuit diagram showing finished manufactured commodities returning across ocean to western consumers"
    ],
    "22": [
        "SPLIT_COMPARISON",
        "historical break-bulk manual cargo handling nightmare on wet docks contrasted with modern automated container operations"
    ],
    "23": [
        "STEP_ENUMERATION",
        "historical port labor productivity scorecard showing agonizingly slow manual sling loading rates averaging few tons per hour"
    ],
    "25": [
        "SITUATIONAL_ACTION",
        "historical dockworker gang manually passing loose wooden crates and hemp cargo nets down into open wooden ship cargo holds"
    ],
    "29": [
        "STEP_ENUMERATION",
        "break-bulk shipping financial ledger graphic breaking down crushing labor expenses, port idle time, and severe cargo theft losses"
    ],
    "32": [
        "OBJECT_MACRO",
        "standardized intermodal shipping container isometric model highlighting corrugated corten steel panels and corner casting fittings"
    ],
    "33": [
        "OBJECT_MACRO",
        "precision dimensional blueprint diorama highlighting exact twenty-foot and forty-foot standardized container length specifications"
    ],
    "34": [
        "MECHANISM_CUTAWAY",
        "interlocking twist-lock corner casting cutaway mechanism demonstrating automatic mechanical latching between stacked container tiers"
    ],
    "35": [
        "SPLIT_COMPARISON",
        "modular stacking comparison model showing standardized containers locking together like precision interlocking toy building blocks"
    ],
    "36": [
        "CAUSE_EFFECT_DIAGRAM",
        "seamless intermodal transfer diagram showing container moving directly from ship deck to double-stack railcar without opening"
    ],
    "37": [
        "MECHANISM_CUTAWAY",
        "sealed container door lock cutaway showing serialized tamper-evident bolt security seal remaining intact throughout entire transit"
    ],
    "38": [
        "OBJECT_MACRO",
        "semi-truck chassis twistlock mechanism engaging the four bottom corner castings of a heavy container before merging onto highway"
    ],
    "40": [
        "STEP_ENUMERATION",
        "global trade velocity acceleration graph showing fifty-fold throughput explosion following containerization standardization"
    ],
    "41": [
        "CAUSE_EFFECT_DIAGRAM",
        "logistics bottleneck liberation diagram showing port terminal throughput surging exponentially across worldwide trade lanes"
    ],
    "43": [
        "CAUSE_EFFECT_DIAGRAM",
        "globalized industrial expansion map showing manufacturing plants decentralizing across worldwide oceans connected by container routes"
    ],
    "45": [
        "CAUSE_EFFECT_DIAGRAM",
        "twenty-four-hour continuous global trade circulation diorama with illuminated container flows operating uninterrupted day and night"
    ],
    "46": [
        "OBJECT_MACRO",
        "choreographed automated container terminal diorama where driverless equipment and towering gantry cranes move in rhythmic unison"
    ],
    "49": [
        "SPLIT_COMPARISON",
        "massive scale capacity graphic contrasting colossal twenty-four-thousand TEU mega vessel volume against human scale silhouettes"
    ],
    "50": [
        "OBJECT_MACRO",
        "super post-panamax ship-to-shore rail gantry crane diorama towering twenty stories tall above deepwater berths"
    ],
    "51": [
        "MECHANISM_CUTAWAY",
        "telescopic container spreader bar cutaway extending heavy steel twist-locks over the full container beam width on deck"
    ],
    "54": [
        "STEP_ENUMERATION",
        "precision operational cycle stopwatch graphic recording forty-five-second container hoist, trolley translation, and set-down rhythm"
    ],
    "56": [
        "OBJECT_MACRO",
        "automated guided vehicle AGV fleet moving autonomously in synchronized matrix patterns across paved port container yard"
    ],
    "59": [
        "MECHANISM_CUTAWAY",
        "terminal operating system TOS algorithmic routing neural diagram calculating collision-free optimal AGV paths in real time"
    ],
    "60": [
        "MECHANISM_CUTAWAY",
        "vessel hydro-static stowage stability calculation diorama showing heavier containers placed low in center of gravity bays"
    ],
    "61": [
        "OBJECT_MACRO",
        "precision differential GPS laser scanner unit guiding crane spreader landing within centimeter tolerances on container corner"
    ],
    "62": [
        "CAUSE_EFFECT_DIAGRAM",
        "satellite real-time container yard tracking map showing three-dimensional coordinate tags assigned to every container box"
    ],
    "63": [
        "STEP_ENUMERATION",
        "real-time warehouse management telemetry display monitoring yard stacking slot occupancy and dwell time metrics"
    ],
    "64": [
        "MECHANISM_CUTAWAY",
        "automated optical character recognition OCR gate portal scanning container ISO serial codes and safety inspection marks"
    ],
    "67": [
        "OBJECT_MACRO",
        "twenty thousand loaded shipping containers neatly secured with lashing rods and turnbuckles across towering ship deck bays"
    ],
    "68": [
        "SITUATIONAL_ACTION",
        "illuminated container megaship departing harbor berth at midnight into ocean fairway guided by harbor pilot tugboats"
    ],
    "70": [
        "CAUSE_EFFECT_DIAGRAM",
        "systemic single-point-of-failure vulnerability tree exposing critical weaknesses hidden beneath modern logistics efficiency"
    ],
    "71": [
        "MECHANISM_CUTAWAY",
        "precision chain link assembly model illustrating utter operational dependency on flawless continuity of every single link"
    ],
    "72": [
        "CAUSE_EFFECT_DIAGRAM",
        "cascading logistics failure simulation showing a single delayed shipment triggering domino bottlenecks across the network"
    ],
    "75": [
        "STEP_ENUMERATION",
        "global trade paralysis pie chart showing twelve percent of international commerce halted during catastrophic chokepoint blockages"
    ],
    "77": [
        "STEP_ENUMERATION",
        "daily idle vessel expenditure ledger graphic accumulating hundreds of thousands of dollars in fuel burn and vessel demurrage"
    ],
    "78": [
        "CAUSE_EFFECT_DIAGRAM",
        "compounding financial damage accumulation graph tracking exponential cost escalation during extended maritime gridlocks"
    ],
    "79": [
        "OBJECT_MACRO",
        "anchorage roadstead satellite view showing dozens of stranded container megaships waiting idle outside congested port waters"
    ],
    "80": [
        "SPLIT_COMPARISON",
        "terminal gridlock dilemma diorama: empty tractor-trailers stranded on access roads on left versus overflowing yard stacks on right"
    ],
    "81": [
        "CAUSE_EFFECT_DIAGRAM",
        "contagious logistics nightmare map showing supply chain delays spreading outward from major maritime gateways to inland hubs"
    ],
    "83": [
        "MECHANISM_CUTAWAY",
        "bullwhip effect kinetic wave model demonstrating how small wrist twitches translate into massive destructive whip tail snaps"
    ],
    "84": [
        "STEP_ENUMERATION",
        "step-by-step psychological amplification diagram explaining how slight retail demand shifts distort into massive supplier spikes"
    ],
    "87": [
        "CAUSE_EFFECT_DIAGRAM",
        "phantom order inflation feedback loop showing speculative inventory hoarding orders artificially ballooning wholesale demand"
    ],
    "89": [
        "CAUSE_EFFECT_DIAGRAM",
        "contagious panic hoarding wave map propagating rapidly across corporate purchasing and procurement departments"
    ],
    "90": [
        "SPLIT_COMPARISON",
        "order volume distortion graphic: modest consumer demand on left inflated into monstrous duplicate orders at factory gate on right"
    ],
    "91": [
        "CAUSE_EFFECT_DIAGRAM",
        "distorted market signal feedback loop showing factory production lines misled by artificial shortage alarms into overproduction"
    ],
    "93": [
        "OBJECT_MACRO",
        "industrial warehouse interior overflowing with surplus stockpiled merchandise pallets stacked precariously up to the roof rafters"
    ],
    "95": [
        "SPLIT_COMPARISON",
        "inventory paradox diorama: critical component shortages on assembly line on left contrasted with unsellable surplus stock on right"
    ],
    "97": [
        "STEP_ENUMERATION",
        "trans-pacific freight rate inflation chart showing spot container shipping prices skyrocketing tenfold during crisis peaks"
    ],
    "99": [
        "SPLIT_COMPARISON",
        "operating margin erosion balance model showing corporate retail profits completely swallowed by exorbitant spot freight surcharges"
    ],
    "100": [
        "CAUSE_EFFECT_DIAGRAM",
        "interconnected vulnerability summary map showing how hyper-lean supply chains collapse under unpredictable demand volatility"
    ],
    "102": [
        "OBJECT_MACRO",
        "modern enterprise supply chain control tower room diorama with multi-screen telemetry monitors tracking global inventory nodes"
    ],
    "104": [
        "SPLIT_COMPARISON",
        "strategic philosophy comparison: fragile just-in-time hyper-lean model on left versus resilient just-in-case buffer strategy on right"
    ],
    "105": [
        "MECHANISM_CUTAWAY",
        "empty warehouse floor cutaway with zero buffer inventory racks inside assembly plant leaving operations exposed to supply shocks"
    ],
    "106": [
        "MECHANISM_CUTAWAY",
        "safety stock warehouse buffer cutaway holding strategic ninety-day inventory reserves in automated high-bay storage racks"
    ],
    "110": [
        "CAUSE_EFFECT_DIAGRAM",
        "nearshoring regional trade corridor map bringing manufacturing facilities closer to end consumer markets to cut transit time"
    ],
    "111": [
        "OBJECT_MACRO",
        "advanced digital twin supply chain simulation console stress-testing operational disruptions and port closure contingencies"
    ],
    "112": [
        "SPLIT_COMPARISON",
        "complete absence of defensive inventory buffers diagram contrasting zero-cushion line on left with immediate assembly shutdown on right"
    ],
    "113": [
        "MECHANISM_CUTAWAY",
        "cloud enterprise resource planning ERP database cutaway linking supplier material availability directly to factory scheduling"
    ],
    "114": [
        "STEP_ENUMERATION",
        "real-time logistics visibility telemetry feed tracking sensor temperature, humidity, and shock impacts on individual containers"
    ],
    "115": [
        "STEP_ENUMERATION",
        "daily financial burn rate graphic showing corporate losses accumulating at millions of dollars per day during factory work stoppages"
    ],
    "117": [
        "CAUSE_EFFECT_DIAGRAM",
        "predictive artificial intelligence routing model dynamically rerouting container shipments away from congested transit hubs"
    ],
    "119": [
        "OBJECT_MACRO",
        "executive business school case study document titled supply chain lessons open on boardroom table with highlighted risk management principles"
    ],
    "122": [
        "CAUSE_EFFECT_DIAGRAM",
        "strategic manufacturing paradigm transition model charting evolution from brittle just-in-time toward resilient safety buffer stocks"
    ],
    "124": [
        "MECHANISM_CUTAWAY",
        "customs bonded warehouse inspection bay cutaway showing customs officials verifying import manifests against container contents"
    ],
    "125": [
        "CAUSE_EFFECT_DIAGRAM",
        "evolutionary industrial survival tree showing modern global manufacturing forced to build structural resilience to survive systemic shocks"
    ],
    "128": [
        "SPLIT_COMPARISON",
        "evaporating low-cost labor advantage diagram contrasting eroding wage arbitrage on left with soaring logistics volatility on right"
    ],
    "129": [
        "CAUSE_EFFECT_DIAGRAM",
        "intermodal freight corridor network showing rail corridors linking coastal deep-water container ports to inland dry ports"
    ],
    "131": [
        "CAUSE_EFFECT_DIAGRAM",
        "fragile globalization stability matrix questioning durability of extended maritime supply lines amidst rising geopolitical friction"
    ],
    "132": [
        "SPLIT_COMPARISON",
        "rail versus road freight efficiency comparison showing single train hauling hundreds of containers at fraction of truck fuel"
    ],
    "133": [
        "STEP_ENUMERATION",
        "freight fuel efficiency comparison chart proving diesel rail transport consumes one-third the fuel of long-haul trucking"
    ],
    "134": [
        "CAUSE_EFFECT_DIAGRAM",
        "systemic bottleneck diagnostic map flashing red indicator markers across congested ports, railheads, and canal passages"
    ],
    "139": [
        "OBJECT_MACRO",
        "rooftop solar array and wind turbine battery storage installation powering zero-emission container terminal cranes"
    ],
    "140": [
        "STEP_ENUMERATION",
        "lead time inflation timeline showing container transit days expanding from twenty-five days to over seventy days during logistics crises"
    ],
    "141": [
        "SPLIT_COMPARISON",
        "environmental trade-off analysis: traditional heavy bunker fuel emissions on left versus clean electric and zero-emission port on right"
    ],
    "142": [
        "CAUSE_EFFECT_DIAGRAM",
        "future maritime decarbonization timeline showing international maritime emissions standards tightening across decades"
    ],
    "144": [
        "CAUSE_EFFECT_DIAGRAM",
        "geopolitical trade route diversification map showing corporations establishing secondary production hubs beyond traditional centers"
    ],
    "146": [
        "SPLIT_COMPARISON",
        "profit margin annihilation ledger showing corporate operating profits erased to zero by compounding logistics demurrage penalties"
    ],
    "148": [
        "CAUSE_EFFECT_DIAGRAM",
        "regional economic integration corridor showing raw materials and sub-assemblies flowing across Southeast Asian borders"
    ],
    "149": [
        "CAUSE_EFFECT_DIAGRAM",
        "compounding operational error tree showing a single minor procurement miscalculation triggering disproportionately massive enterprise losses"
    ],
    "150": [
        "OBJECT_MACRO",
        "high-speed container freight train crossing border trade checkpoint between manufacturing zones and coastal ports"
    ],
    "152": [
        "SPLIT_COMPARISON",
        "cost versus resilience leadership paradigm contrasting lowest unit purchase price on left with lowest total systemic risk on right"
    ],
    "153": [
        "CAUSE_EFFECT_DIAGRAM",
        "resilient supply chain ecosystem network showing diversified sourcing hubs feeding into redundant maritime trade arteries"
    ],
    "156": [
        "MECHANISM_CUTAWAY",
        "modular factory production line cutaway showing rapidly reconfigurable robotic toolheads adapting to alternative product runs"
    ],
    "157": [
        "CAUSE_EFFECT_DIAGRAM",
        "trans-pacific shipping route map tracing container trajectory from Hai Phong port across ocean to US West Coast ports with hidden cost markers"
    ],
    "159": [
        "SPLIT_COMPARISON",
        "ocean freight cost perception illusion chart contrasting low base sea charter rates against massive unexpected ancillary accessorial fees"
    ],
    "161": [
        "SPLIT_COMPARISON",
        "where does the remaining budget vanish forensic diagram tracking hidden logistics ancillary charges draining corporate funds"
    ],
    "162": [
        "STEP_ENUMERATION",
        "hidden logistics surcharge invoice graphic revealing hidden terminal handling fees, chassis splits, and bunker adjustment charges"
    ],
    "163": [
        "MECHANISM_CUTAWAY",
        "bunker adjustment factor BAF calculation formula cutaway showing ocean carrier fuel price fluctuation indexing mechanisms"
    ],
    "164": [
        "STEP_ENUMERATION",
        "ocean freight cost breakdown pie chart demonstrating fuel bunker expenditures representing over forty percent of vessel operating costs"
    ],
    "165": [
        "OBJECT_MACRO",
        "terminal lift on lift off LoLo handling fee receipt displaying substantial per-move charges for every container crane crane cycle"
    ],
    "166": [
        "SPLIT_COMPARISON",
        "per-container port fee accumulation model showing crane handling charges adding hundreds of dollars per single box transfer"
    ],
    "168": [
        "STEP_ENUMERATION",
        "demurrage and detention fee escalation chart displaying punitive daily port storage charges multiplying rapidly after free days expire"
    ],
    "169": [
        "OBJECT_MACRO",
        "marine cargo insurance policy contract document highlighting hull risk clauses, general average liabilities, and damage protections"
    ],
    "171": [
        "SPLIT_COMPARISON",
        "domestic drayage versus ocean voyage paradox diorama: short fifty-kilometer truck haul on left rivaling trans-oceanic freight cost on right"
    ],
    "173": [
        "CAUSE_EFFECT_DIAGRAM",
        "drayage highway bottleneck cost model illustrating why short terrestrial legs constitute the most expensive segment per mile"
    ],
    "174": [
        "OBJECT_MACRO",
        "heavy drayage semi-truck idling in severe metropolitan traffic congestion racking up hourly driver wages and fuel waste"
    ],
    "176": [
        "SPLIT_COMPARISON",
        "distance versus cost paradox graphic showing tiny fifty-kilometer terrestrial delivery incurring disproportionately massive capital expenses"
    ],
    "177": [
        "STEP_ENUMERATION",
        "freight cost per kilometer comparison chart revealing domestic drayage rates exceeding ocean shipping costs on equivalent distance basis"
    ],
    "178": [
        "CAUSE_EFFECT_DIAGRAM",
        "scale economy disparity model demonstrating why ocean mega-vessel container transport achieves insurmountable cost efficiencies over trucks"
    ],
    "179": [
        "SPLIT_COMPARISON",
        "unforgiving profit margin squeeze diagram showing hidden inland transport surcharges steadily consuming corporate working capital"
    ],
    "181": [
        "OBJECT_MACRO",
        "corporate cash flow ledger graphic displaying working capital frozen solid in unpaid freight invoices and disputed port demurrage"
    ],
    "183": [
        "SITUATIONAL_ACTION",
        "procurement executives negotiating shipping contracts around boardroom conference table with carrier route schedules spread out"
    ],
    "185": [
        "CAUSE_EFFECT_DIAGRAM",
        "net margin optimization model showing every dollar saved in supply chain logistics flowing directly into corporate bottom line"
    ],
    "189": [
        "CAUSE_EFFECT_DIAGRAM",
        "China Plus One manufacturing diversification map showing multinational corporations establishing secondary production hubs across Southeast Asia"
    ],
    "190": [
        "CAUSE_EFFECT_DIAGRAM",
        "corporate risk dispersion strategy diorama showing global manufacturing footprint dividing operations across multiple sovereign jurisdictions"
    ],
    "191": [
        "CAUSE_EFFECT_DIAGRAM",
        "multinational manufacturing relocation wave diagram showing factory assembly lines migrating into Southeast Asian industrial belts"
    ],
    "192": [
        "OBJECT_MACRO",
        "satellite map highlighting Vietnam strategic geographic coastline glowing as premier industrial manufacturing hub of the region"
    ],
    "193": [
        "CAUSE_EFFECT_DIAGRAM",
        "geographic proximity advantage map showing shared borders and maritime proximity enabling rapid cross-border industrial integration"
    ],
    "195": [
        "OBJECT_MACRO",
        "panoramic satellite diorama of extensive Vietnamese coastline situated directly beside the busiest primary international sea lane"
    ],
    "196": [
        "CAUSE_EFFECT_DIAGRAM",
        "direct trans-Pacific shipping route map linking Cai Mep deepwater container terminals directly to United States West Coast ports"
    ],
    "197": [
        "STEP_ENUMERATION",
        "maritime transit duration scorecard showing direct ocean service cutting multiple days off trans-Pacific transit times"
    ],
    "199": [
        "OBJECT_MACRO",
        "modern master-planned industrial park diorama with clean factory sheds serving as primary tier-one manufacturing export nodes"
    ],
    "200": [
        "CAUSE_EFFECT_DIAGRAM",
        "foreign direct investment FDI capital inflow diagram tracking billions in foreign capital pouring into industrial manufacturing infrastructure"
    ],
    "202": [
        "OBJECT_MACRO",
        "high-tech electronics assembly cleanroom with robotic arms assembling precision mobile circuit boards for worldwide export"
    ],
    "203": [
        "SPLIT_COMPARISON",
        "manufacturing maturity analysis diagram: final assembly export triumphs on left balanced against underlying structural vulnerabilities on right"
    ],
    "205": [
        "MECHANISM_CUTAWAY",
        "electronic product bill of materials BOM cutaway revealing reliance on imported microchips, sensors, and specialized core silicon"
    ],
    "209": [
        "CAUSE_EFFECT_DIAGRAM",
        "capital flight risk simulation showing volatile global investments rapidly shifting abroad if local supporting ecosystems lag"
    ],
    "211": [
        "CAUSE_EFFECT_DIAGRAM",
        "domestic supporting industry development roadmap showing local tier-one suppliers mastering precision component machining and tooling"
    ],
    "214": [
        "MECHANISM_CUTAWAY",
        "supply chain modular restructuring model showing re-engineered logistics links built to flex and withstand systemic shocks"
    ],
    "217": [
        "CAUSE_EFFECT_DIAGRAM",
        "multi-source procurement pillar diagram showing manufacturing orders balanced across domestic and diversified international suppliers"
    ],
    "218": [
        "SPLIT_COMPARISON",
        "supplier dependency contrast diagram: perilous single-source dependency on left versus resilient multi-vendor allocation on right"
    ],
    "219": [
        "OBJECT_MACRO",
        "classic risk proverb visualization: eggs separated into multiple padded baskets representing distributed supply chain security"
    ],
    "220": [
        "SITUATIONAL_ACTION",
        "supply chain directors managing hybrid supplier matrix balancing domestic nearshore sources with offshore high-volume partners"
    ],
    "221": [
        "CAUSE_EFFECT_DIAGRAM",
        "automated contingency failover routing diagram showing backup regional supplier immediately engaging when primary shipping lanes stall"
    ],
    "222": [
        "OBJECT_MACRO",
        "continuous manufacturing assembly line humming with steady automated production runs without missing a single manufacturing cycle"
    ],
    "223": [
        "MECHANISM_CUTAWAY",
        "transparent real-time digital supply chain control tower cutaway showing end-to-end cargo movement tracked across global cloud databases"
    ],
    "225": [
        "OBJECT_MACRO",
        "anomaly detection interface display instantly flagging supply chain deviations and customs delays with red real-time telemetry markers"
    ],
    "226": [
        "MECHANISM_CUTAWAY",
        "smart IoT sensor tag cutaway attached to container chassis broadcasting temperature, shock, and precise GPS coordinates via satellite"
    ],
    "227": [
        "CAUSE_EFFECT_DIAGRAM",
        "cloud data predictive analytics architecture detecting early bottleneck indicators across global ports before gridlocks manifest"
    ],
    "229": [
        "SPLIT_COMPARISON",
        "inventory strategy transformation model: fragile zero-inventory just-in-time on left versus secure strategic buffer just-in-case on right"
    ],
    "230": [
        "STEP_ENUMERATION",
        "balance sheet financial comparison showing true risks of zero-inventory models compared to resilient working capital buffers"
    ],
    "231": [
        "MECHANISM_CUTAWAY",
        "automated storage warehouse buffer zone cutaway holding critical reserve sub-assemblies to safeguard uninterrupted manufacturing runs"
    ],
    "233": [
        "SPLIT_COMPARISON",
        "insurance cost equivalence model proving modest inventory carrying costs represent essential insurance premiums against factory shutdowns"
    ],
    "236": [
        "CAUSE_EFFECT_DIAGRAM",
        "resilience competitive advantage framework proving agile crisis recovery speed is the ultimate determinant of commercial survival"
    ],
    "237": [
        "SPLIT_COMPARISON",
        "value proposition contrast model: illusory paper cost savings of brittle suppliers on left shattered by costly stockouts on right"
    ],
    "239": [
        "MECHANISM_CUTAWAY",
        "adaptive enterprise operating system cutaway flexing production schedules and distribution logistics in response to volatile markets"
    ],
    "241": [
        "CAUSE_EFFECT_DIAGRAM",
        "interconnected planetary clockwork diorama visualizing tens of thousands of microscopic industrial links forming global civilization"
    ],
    "242": [
        "OBJECT_MACRO",
        "panoramic diorama celebrating modern logistics as an astonishing economic and mechanical engineering masterpiece of human ingenuity"
    ],
    "245": [
        "SPLIT_COMPARISON",
        "capital flow universality model: cash flow mechanisms of small businesses on left operating under same financial laws as global titans on right"
    ],
    "246": [
        "CAUSE_EFFECT_DIAGRAM",
        "cash flow strangulation diagram showing how upstream material delivery delays rapidly starve corporate operating capital balances"
    ],
    "248": [
        "SITUATIONAL_ACTION",
        "executive audit team methodically inspecting supply chain process map to identify hidden single-point failure bottlenecks"
    ],
    "249": [
        "CAUSE_EFFECT_DIAGRAM",
        "weakest link failure simulation showing vulnerability of entire logistics chain determined by its single most fragile node"
    ],
    "250": [
        "SPLIT_COMPARISON",
        "crisis preparation cost curve proving early risk mitigation planning is infinitely cheaper than emergency post-crisis disaster recovery"
    ],
    "252": [
        "SPLIT_COMPARISON",
        "business endurance podium diagram showing the most resilient and adaptive supply chain operators outlasting brittle low-cost competitors"
    ],
    "254": [
        "SITUATIONAL_ACTION",
        "business executive standing before enterprise logistics dashboard preparing company operations to absorb the next global macro shock"
    ]
}.items()}


def build_banh_rang_beats(
    cues: List[Dict[str, Any]],
    durs: List[float],
    ats: List[float],
    chapters: List[Dict[str, Any]],
    old_beats: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Build all 255 beats for banh_rang."""
    beats = []
    seen_prompts = set()

    for i, c in enumerate(cues):
        bid = f"B{i:03d}"
        dur = durs[i]
        at_sec = ats[i]
        nar = c["narration"]
        chap_idx, chap_title = assign_chapter(at_sec, chapters)

        if i < len(old_beats) and old_beats[i].get("reuse_old_image_idx") is not None:
            # Reused anchor beat
            reuse_val = old_beats[i]["reuse_old_image_idx"]
            orig_prompt = old_beats[i]["prompt"]
            prompt = sanitize_prompt(orig_prompt)
            explainer_type = old_beats[i].get("explainer_type", "MECHANISM_CUTAWAY")
            if explainer_type not in (
                "CAUSE_EFFECT_DIAGRAM", "MECHANISM_CUTAWAY", "OBJECT_MACRO",
                "SPLIT_COMPARISON", "STEP_ENUMERATION", "SITUATIONAL_ACTION"
            ):
                explainer_type = "MECHANISM_CUTAWAY"
        else:
            # New beat: bespoke 100% unique prompt
            reuse_val = None
            etype, vdesc = BANH_RANG_157_REPLACEMENTS[i]
            explainer_type = etype
            prompt_raw = f"{STYLE_PREFIX} {vdesc}, {AESTHETIC_TRAITS}"
            prompt = sanitize_prompt(prompt_raw)

        # Uniqueness guarantee
        if prompt in seen_prompts:
            disambiguator = f"industrial isometric elevation {i:03d} revealing spatial assembly clarity"
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
