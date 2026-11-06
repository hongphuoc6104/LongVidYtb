#!/usr/bin/env python3
"""Spec builder for en-first-principles (Long 16:9 and Short 9:16)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SYS_TOOLS = Path(__file__).resolve().parent
if str(SYS_TOOLS) not in sys.path:
    sys.path.insert(0, str(SYS_TOOLS))

OUT_DIR = Path("sys/channels/en_batch1_specs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ANCHOR_BASE = (
    "High-contrast 8K Veritasium scientific cinematography with crisp directional key light, "
    "deep slate-navy (#0F172A) contrast, and clean cyan and amber physical vector accents, strictly zero chalkboards or text"
)
ANCHOR_ARCHIVAL = (
    "Archival Prussian cyanotype laboratory setting, mechanical clockwork dominoes and brass balance scales, "
    "deep slate-navy shadows with warm tungsten highlights, strictly zero text"
)
ANCHOR_SYSTEMS = (
    "Cinematic precision physics demonstration table, machined steel gears, fluid dynamic tubes, "
    "and luminous geometric trajectory vectors against velvet dark studio backdrop, strictly zero text"
)


def get_long_shots() -> list[dict[str, Any]]:
    shots: list[dict[str, Any]] = []

    def add_shot(
        sid: str,
        grp: str,
        cont: bool,
        pause: float,
        cam: str,
        narration: str,
        start_vis: str,
        end_vis: str,
        motion: str,
        anchor: str = ANCHOR_BASE,
    ) -> None:
        words = narration.split()
        if not (20 <= len(words) <= 23):
            raise ValueError(f"Shot {sid} word count {len(words)} not in 20..23: '{narration}'")
        shots.append(
            {
                "shot_id": sid,
                "scene_group": grp,
                "continues_prev": cont,
                "scene_anchor": anchor,
                "narration": narration,
                "pause_after_sec": pause,
                "camera_verb": cam,
                "start_visual": start_vis,
                "end_visual": end_vis,
                "subject_motion": motion,
            }
        )

    # ==========================================
    # CHAPTER 1: ch1_hook (S01..S08)
    # ==========================================
    # Group 1: Colonial Delhi Bounty
    add_shot(
        "S01",
        "ch1_hook",
        False,
        0.33,
        "Slow optical dolly push-in",
        "In colonial Delhi, British authorities faced an unbearable plague of deadly venomous cobras slithering openly across every dusty imperial boulevard.",
        "Veritasium scientific studio recreation: an archival 19th-century British administrative ledger lying open on a mahogany desk beside an empty brass balance.",
        "Dolly closer into the brass balance as heavy copper bounty coins tilt the scale beam sharply downward under warm focused studio spotlighting.",
        "brass balance beam dips sharply as a stack of heavy minted copper coins slides into the weighing pan",
        ANCHOR_ARCHIVAL,
    )
    add_shot(
        "S02",
        "ch1_hook",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "To solve the venomous crisis, governors announced a direct cash bounty for every severed snake carcass delivered to government outposts.",
        "Mahogany desk with ledger and balance scale in crisp directional key light.",
        "Lateral track across the desk showing rows of stamped colonial parchment certificates and brass coin stacks waiting for snake hunters.",
        "camera tracks smoothly sideways revealing rows of official bounty certificates and glistening coin stacks under directional beam",
        ANCHOR_ARCHIVAL,
    )
    add_shot(
        "S03",
        "ch1_hook",
        True,
        0.33,
        "Precise macro focus rack",
        "At first, the policy appeared to be an astonishing administrative triumph as thousands of dead serpents poured into collection stations.",
        "Macro perspective of polished brass tally weights and official wax seal stamps glistening on the polished dark wood desk.",
        "Focus racks from the glistening wax stamp to a massive tally register marking off hundreds of successful bounty claims.",
        "optical focal plane shifts smoothly from gleaming wax seal to the dense numerical tally rows in the background",
        ANCHOR_ARCHIVAL,
    )
    add_shot(
        "S04",
        "ch1_hook",
        True,
        0.44,
        "Subtle low-angle scientific tilt-up",
        "British colonial officials proudly celebrated their decisive economic intervention, entirely convinced that simple financial incentives would easily cleanse the entire capital city.",
        "Low-angle view of the ornate mahogany office with towering classical arches bathed in warm dramatic directional keylight.",
        "Tilt up from the ledger table toward tall colonial arched windows letting in bold shafts of golden atmospheric dust-mote sunlight.",
        "camera tilts upward toward arched windows as bright volumetric dust rays cut through the dim mahogany office atmosphere",
        ANCHOR_ARCHIVAL,
    )

    # Group 2: The Cobra Explosion
    add_shot(
        "S05",
        "ch1_hook",
        False,
        0.33,
        "Slow optical dolly push-in",
        "Yet months into the bounty program, administrators noticed an impossible anomaly: bounty claims skyrocketed while wild snake encounters dramatically increased.",
        "Veritasium physics studio setup: high-contrast dark navy table with glowing amber indicator vectors pointing upward on a polished glass platform.",
        "Pushing in on the glass platform as an elegant mechanical vector arrow surges steeply upward toward a flashing amber warning node.",
        "luminous amber vector arrow extends upward along a calibrated glass axis toward a glowing mechanical threshold point",
    )
    add_shot(
        "S06",
        "ch1_hook",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "Instead of hunting dangerous wild snakes in dense jungles, enterprising local citizens had secretly constructed massive underground commercial breeding farms.",
        "Dark navy physics platform with glowing indicator nodes and precision mechanical apparatus under sharp studio rim lights.",
        "Lateral track revealing an array of miniature modular enclosures arranged like interconnected cellular chambers glowing under soft cyan light.",
        "camera tracks sideways along the modular geometric chambers illustrating exponential artificial cultivation and multiplying units",
    )
    add_shot(
        "S07",
        "ch1_hook",
        True,
        0.33,
        "Precise overhead macro descent",
        "They discovered that feeding and harvesting harmless captive cobras generated vastly more guaranteed income than tracking venomous reptiles in nature.",
        "Overhead view looking straight down at the polished geometric matrix of glowing cellular enclosures on the dark glass tabletop.",
        "Descending vertically as miniature brass balance pendulums oscillate rhythmically above the multiplying cellular grid nodes.",
        "overhead camera descends steadily while multiple brass pendulums swing in synchronized harmonic oscillation above the grid",
    )
    add_shot(
        "S08",
        "ch1_hook",
        True,
        0.55,
        "Slow arc orbit around precision apparatus",
        "A well-intentioned policy designed to eliminate cobras had inadvertently engineered the most profitable industrial snake production complex in human history.",
        "Descending closer to the brass pendulums and glass grid reflecting vibrant cyan and amber studio keylights.",
        "Orbiting around the central balance apparatus as interconnected mechanical dominoes form an escalating spiral chain of systemic unintended feedback.",
        "camera completes a smooth circular orbit around the central mechanical balance as kinetic dominoes cascade into a spiral",
    )

    # ==========================================
    # CHAPTER 2: ch2_paradox (S09..S16)
    # ==========================================
    # Group 1: The Scrap and the Release
    add_shot(
        "S09",
        "ch2_paradox",
        False,
        0.33,
        "Slow optical dolly push-in",
        "When horrified imperial officials finally realized they were subsidizing snake breeders, they instantly cancelled the entire bounty payout system overnight.",
        "Veritasium studio demonstration: a heavy suspended brass weight hanging motionless above a delicate kinetic glass lever system.",
        "Dolly in toward the suspended weight as an electromagnetic clutch abruptly cuts power, dropping the heavy brass weight freefall.",
        "suspended brass weight suddenly drops straight down under gravity, striking the primary glass trip lever",
    )
    add_shot(
        "S10",
        "ch2_paradox",
        True,
        0.33,
        "Precise macro focus rack",
        "With no financial reward left to sell dead reptiles, hundreds of breeders opened their backyard cages and released millions of snakes.",
        "Kinetic glass lever system vibrating after the sudden impact of the dropped brass weight on the dark navy platform.",
        "Focus racks from the trembling lever to dozens of spring-loaded miniature brass gates popping open simultaneously across the staging platform.",
        "dozens of miniature brass spring gates snap open in rapid succession releasing kinetic ball bearings across the tabletop",
    )
    add_shot(
        "S11",
        "ch2_paradox",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "Delhi was instantly flooded with vastly more venomous serpents than had ever existed before the government ever attempted to intervene.",
        "Dark navy platform covered with hundreds of gleaming steel ball bearings rolling freely in chaotic intersecting trajectories.",
        "Tracking laterally across the scattered steel bearings as they bounce and scatter past the original calibrated balance apparatus.",
        "hundreds of gleaming steel spheres roll and bounce chaotically across the dark slate-navy surface in all directions",
    )
    add_shot(
        "S12",
        "ch2_paradox",
        True,
        0.44,
        "Subtle low-angle scientific tilt-up",
        "This catastrophic paradox became immortalized in modern systemic science as the Cobra Effect: when intuitive solutions actively multiply the original disaster.",
        "Low-angle view of the central brass balance completely tipped over, surrounded by freely scattering polished steel bearings.",
        "Tilt up from the overturned balance toward a clean floating cyan vector diagram depicting an amplifying positive feedback loop.",
        "camera tilts up smoothly from the fallen balance to reveal a self-reinforcing closed-loop kinetic feedback diagram",
    )

    # Group 2: The Linear Trap
    add_shot(
        "S13",
        "ch2_paradox",
        False,
        0.33,
        "Slow optical dolly push-in",
        "Why do brilliant policymakers and educated leaders consistently fall into this exact mental trap across modern economics, politics, medicine, and engineering?",
        "Veritasium physics laboratory: clean slate-navy workbench illuminated by a single vertical razor-sharp white spotlight beam.",
        "Pushing in toward a solitary steel pendulum bob hanging at perfect vertical rest over an illuminated grid coordinate.",
        "camera pushes in on the motionless steel pendulum suspended in zero velocity under the concentrated cone of light",
    )
    add_shot(
        "S14",
        "ch2_paradox",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "The fundamental flaw lies in first-order thinking: assuming complex interconnected real-world systems respond like simple mechanical linear cause and effect.",
        "Motionless steel pendulum bob hanging above the illuminated grid coordinate on the dark navy surface.",
        "Tracking sideways as an external mechanical rod pushes the pendulum gently, creating a simple predictable harmonic swing.",
        "mechanical pushing rod nudges the steel bob, setting off a single clean linear swing across the calibrated grid",
    )
    add_shot(
        "S15",
        "ch2_paradox",
        True,
        0.33,
        "Precise macro focus rack",
        "First-order thinkers observe an obvious symptom, apply an immediate direct force, and naively expect the target variable to move proportionally.",
        "Calibrated grid surface under the swinging steel pendulum showing clean linear centimeter markings.",
        "Focus racks from the linear centimeter markings to the pendulum apex where a hidden array of nonlinear springs sits concealed.",
        "focal plane shifts from the simple linear measurement lines to the intricate spring couplings mounted above the pivot",
    )
    add_shot(
        "S16",
        "ch2_paradox",
        True,
        0.55,
        "Slow arc orbit around precision apparatus",
        "In simple physics, pushing a billiard ball yields a straight line; but complex adaptive systems react, adapt, and push right back.",
        "Precision mechanical pivot with spring couplings and swinging pendulum illuminated by dual cyan and amber rim lights.",
        "Orbiting around the pivot as the secondary springs engage, converting the simple swing into complex chaotic double-pendulum motion.",
        "camera orbits smoothly as secondary articulated joints engage, whipping the pendulum into wild non-linear chaotic orbits",
    )

    # ==========================================
    # CHAPTER 3: ch3_mechanism (S17..S24)
    # ==========================================
    # Group 1: Second-Order Thinking Architecture
    add_shot(
        "S17",
        "ch3_mechanism",
        False,
        0.33,
        "Slow optical dolly push-in",
        "Second-order thinking asks the crucial follow-up question that first-order thinkers always ignore: and then what happens after that first change?",
        "Veritasium studio demonstration: a row of precision dominoes crafted from frosted optical glass standing upright on polished obsidian.",
        "Dolly in toward the lead domino as a miniature steel probe hovers directly above its upper edge ready to strike.",
        "steel mechanical probe descends with micrometer precision toward the top bevel of the lead optical glass domino",
        ANCHOR_SYSTEMS,
    )
    add_shot(
        "S18",
        "ch3_mechanism",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "First-order consequences are immediate, visible, and emotionally satisfying, while critical second and third-order consequences are delayed, indirect, and often catastrophic.",
        "Lead domino falling forward and striking the second frosted glass domino on the obsidian runway.",
        "Tracking alongside the cascading domino wave as internal fiber-optic strands inside each block light up from white into deep amber.",
        "camera tracks alongside the collapsing dominoes as each falling glass tile shifts color from crisp white to warning amber",
        ANCHOR_SYSTEMS,
    )
    add_shot(
        "S19",
        "ch3_mechanism",
        True,
        0.33,
        "Precise overhead macro descent",
        "Because human brains evolved to hunt fast-moving immediate threats, our cognitive architecture heavily overweights immediate payoff over compounding secondary feedbacks.",
        "Overhead view of the curving domino track winding across the dark obsidian table toward an intricate gear train.",
        "Descending vertically as the falling dominoes strike the primary brass trigger lever of a complex multi-stage planetary gearbox.",
        "overhead camera glides down as the final falling domino impacts the brass trigger arm of the planetary gear assembly",
        ANCHOR_SYSTEMS,
    )
    add_shot(
        "S20",
        "ch3_mechanism",
        True,
        0.44,
        "Subtle low-angle scientific tilt-up",
        "When policymakers alter incentives without mapping dynamic feedback loops, they trigger delayed rebound effects that frequently swamp the initial benefit.",
        "Planetary gearbox spinning rapidly as brass and steel gears interlock in high-shutter crisp motion.",
        "Tilt up from the whirling gear train to a secondary weighted balance beam that begins tipping in the completely opposite direction.",
        "camera tilts up from the spinning gears to reveal a massive counterweight tilting backwards against the input force",
        ANCHOR_SYSTEMS,
    )

    # Group 2: Feedback Loops and Chesterton's Fence
    add_shot(
        "S21",
        "ch3_mechanism",
        False,
        0.33,
        "Slow optical dolly push-in",
        "Consider Chesterton’s Fence: if you find a seemingly useless fence in the middle of a road, never tear it down immediately.",
        "Veritasium demonstration: a clean miniature wooden boundary post standing upright in a miniature soil terrain under soft spotlight.",
        "Dolly closer to the boundary post revealing delicate roots and subterranean tension cables anchored deep beneath the surface.",
        "camera pushes in on the wooden post revealing glowing subterranean tension wires securing a precarious hillside slope",
    )
    add_shot(
        "S22",
        "ch3_mechanism",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "First-order thinkers demand its removal because they cannot see its purpose, blind to the underlying forces the fence quietly holds back.",
        "Close-up of the wooden post and tension wires holding back unstable loose shale and gravel.",
        "Tracking laterally as an artificial mechanical arm unhooks the tension cable from the post, releasing the anchored load.",
        "mechanical clamp disconnects the retaining cable from the post, causing the underlying support tension to collapse",
    )
    add_shot(
        "S23",
        "ch3_mechanism",
        True,
        0.33,
        "Precise macro focus rack",
        "The moment you destroy an established barrier without understanding why it was built, the hidden second-order landslide immediately buries you.",
        "Loose shale and gravel beginning to slide downward on the incline after the cable release.",
        "Focus racks from the sliding gravel to the entire miniature valley floor below as loose stone surges forward in a sudden miniature landslide.",
        "optical focus shifts rapidly from the loosened gravel stones to the full miniature rockfall cascading down the valley slope",
    )
    add_shot(
        "S24",
        "ch3_mechanism",
        True,
        0.55,
        "Slow arc orbit around precision apparatus",
        "Every existing barrier, rule, or biological adaptation in a complex system exists because historical pressures selected it for survival resilience.",
        "Miniature rockfall settled on the valley floor under cool cyan studio lighting with deep slate-navy contrast.",
        "Orbiting around the stable side of the landscape where an intact retention barrier holds centuries of accumulated pressure in check.",
        "camera orbits around the preserved retaining wall showcasing the balance of forces holding massive lateral shear in check",
    )

    # ==========================================
    # CHAPTER 4: ch4_case_study_1 (S25..S32)
    # ==========================================
    # Group 1: The Four Pests Campaign
    add_shot(
        "S25",
        "ch4_case_study_1",
        False,
        0.33,
        "Slow optical dolly push-in",
        "Nowhere was the lethal danger of first-order thinking demonstrated more horrifyingly than during China’s catastrophic Four Pests Campaign in nineteen fifty-eight.",
        "Archival Veritasium historical documentary setting: vintage 1950s agrarian posters and brass field binoculars resting on a rustic wooden table.",
        "Dolly in toward an open botanical handbook illustrating the Eurasian tree sparrow beside wheat grain stalks under warm tungsten light.",
        "camera pushes in smoothly across the rustic table toward the hand-tinted botanical sketch of a sparrow feeding on grain",
        ANCHOR_ARCHIVAL,
    )
    add_shot(
        "S26",
        "ch4_case_study_1",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "Official state agricultural planners calculated that each individual sparrow consumed several pounds of valuable grain every single year from public farmland.",
        "Botanical sparrow sketch and dried golden wheat sheaves resting under warm studio directional lighting.",
        "Lateral track across the desk showing neat rows of dried wheat grain and a precision brass balance weighing grain loss.",
        "camera tracks laterally past rows of golden wheat stalks toward a miniature brass scale balancing grain against a lead weight",
        ANCHOR_ARCHIVAL,
    )
    add_shot(
        "S27",
        "ch4_case_study_1",
        True,
        0.33,
        "Precise macro focus rack",
        "Using simple first-order mathematics, leaders concluded that exterminating all sparrows would automatically save millions of tons of wheat for humans.",
        "Macro perspective of golden wheat kernels piling up on the brass scale pan under directional spotlight.",
        "Focus racks from the golden wheat kernels to an official red administrative decree ordering the total national extermination of sparrows.",
        "focal plane shifts smoothly from the weighed grain kernels to the crisp stamped administrative decree behind the balance",
        ANCHOR_ARCHIVAL,
    )
    add_shot(
        "S28",
        "ch4_case_study_1",
        True,
        0.44,
        "Subtle low-angle scientific tilt-up",
        "Millions of citizens mobilized nationwide, banging pots, destroying nests, and shooting billions of sparrows out of the sky until extinction loomed.",
        "Low-angle view of empty brass birdcages hanging silhouetted against a tall industrial window bathed in pale morning light.",
        "Tilt up from the empty brass cages toward the silent sky visible through the high industrial glass panes.",
        "camera tilts upward past rows of open empty bird cages toward the silent pale sky outside the warehouse window",
        ANCHOR_ARCHIVAL,
    )

    # Group 2: The Ecological Crash
    add_shot(
        "S29",
        "ch4_case_study_1",
        False,
        0.33,
        "Slow optical dolly push-in",
        "The first-order goal was achieved with ruthless efficiency: sparrows were virtually wiped from the fields, and initial grain consumption dropped.",
        "Veritasium scientific demonstration: an illuminated glass terrarium displaying miniature healthy green wheat sprouts on dark rich soil.",
        "Dolly closer into the thriving green wheat sprouts under clean daylight-balanced LED laboratory lighting.",
        "camera glides forward into the lush green miniature wheat canopy showing vibrant healthy leaves and moist dark soil",
    )
    add_shot(
        "S30",
        "ch4_case_study_1",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "However, planners completely overlooked the second-order ecological function: sparrows did not merely eat seeds; they devoured billions of voracious crop-destroying insects.",
        "Green wheat sprouts in the glass terrarium under high-contrast directional spotlighting.",
        "Tracking laterally across the terrarium revealing sudden swarms of miniature locust and caterpillar models clustering along the stems.",
        "camera tracks along the wheat stems revealing an explosion of voracious insect swarms multiplying across every leaf",
    )
    add_shot(
        "S31",
        "ch4_case_study_1",
        True,
        0.33,
        "Precise macro focus rack",
        "With their primary natural predator utterly eliminated, catastrophic locust populations exploded exponentially, devouring entire provincial harvests down to the bare earth.",
        "Macro view of healthy green leaves being rapidly stripped down to bare fibrous skeletal veins.",
        "Focus racks from the stripped skeletal leaf to a vast barren soil bed where crops have been entirely stripped bare.",
        "focus shifts from the skeletonized leaf vein to the devastated dry soil bed stretching across the background",
    )
    add_shot(
        "S32",
        "ch4_case_study_1",
        True,
        0.55,
        "Slow arc orbit around precision apparatus",
        "The resulting ecological collapse triggered the Great Chinese Famine, demonstrating how eradicating one perceived pest can annihilate thirty million innocent lives.",
        "Devastated barren soil bed in the dark laboratory setting under somber deep navy and cold cyan illumination.",
        "Orbiting around a shattered brass balance scale lying discarded on the parched cracked earth as dust slowly settles.",
        "camera completes a somber circular orbit around the broken balance scale lying half-buried in parched cracked earth",
    )

    # ==========================================
    # CHAPTER 5: ch5_escalation (S33..S40)
    # ==========================================
    # Group 1: Modern Financial Moral Hazard
    add_shot(
        "S33",
        "ch5_escalation",
        False,
        0.33,
        "Slow optical dolly push-in",
        "The Cobra Effect is not a relic of historical folly; modern financial and technological systems multiply perverse incentives on unprecedented global scales.",
        "Veritasium modern systems studio: high-speed glowing digital financial tickers reflected in polished obsidian glass and chrome structural pillars.",
        "Dolly in toward an intricate kinetic financial trading model featuring interlocking polished acrylic levers and liquid mercury columns.",
        "camera pushes in on the intricate acrylic financial balance apparatus as liquid mercury rises within calibrated glass columns",
        ANCHOR_SYSTEMS,
    )
    add_shot(
        "S34",
        "ch5_escalation",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "When central banks bail out reckless financial institutions to prevent short-term recession, they introduce first-order stabilization at the cost of catastrophic moral hazard.",
        "Liquid mercury columns stabilized at perfect horizontal equilibrium under crisp white and amber studio lights.",
        "Lateral track across the acrylic apparatus showing massive weighted dice labeled with leverage ratios resting on an inclined ramp.",
        "camera tracks laterally revealing heavy weighted chrome cubes stacked precariously on an escalating inclined plane",
        ANCHOR_SYSTEMS,
    )
    add_shot(
        "S35",
        "ch5_escalation",
        True,
        0.33,
        "Precise macro focus rack",
        "Wall Street traders recognize that profits are privatized while systemic losses are socialized, incentivizing them to double down on hyper-leveraged speculation.",
        "Weighted chrome cubes teetering on the incline above the stabilized mercury column.",
        "Focus racks from the heavy chrome cubes to the microscopic stress fractures spreading through the acrylic base below.",
        "focal plane shifts from the gleaming chrome blocks to fine spiderweb stress fractures branching across the acrylic support base",
        ANCHOR_SYSTEMS,
    )
    add_shot(
        "S36",
        "ch5_escalation",
        True,
        0.44,
        "Subtle low-angle scientific tilt-up",
        "By extinguishing every small necessary forest fire, regulators guarantee that the eventual catastrophic blaze will consume the entire national financial forest.",
        "Low-angle view of the towering acrylic and chrome structure groaning under massive kinetic mechanical tension.",
        "Tilt up from the fracturing acrylic base toward the overarching suspension cables straining under immense asymmetric loads.",
        "camera tilts up past the overloaded structural joints toward the glowing ceiling grid illuminating microscopic structural fissures",
        ANCHOR_SYSTEMS,
    )

    # Group 2: Algorithmic Engagement & Social Division
    add_shot(
        "S37",
        "ch5_escalation",
        False,
        0.33,
        "Slow optical dolly push-in",
        "Consider social media recommendation algorithms: software engineers optimized neural networks for a simple, innocent first-order metric called user session engagement.",
        "Veritasium data demonstration: clean optical array of pulsing fiber-optic cables converging onto a glowing silicon prism on black obsidian.",
        "Dolly in toward the silicon prism as clean coherent white light splits into thousands of micro-luminescent data strands.",
        "camera glides toward the silicon prism as a pure white laser beam refracts into an intricate fan of glowing cyan data threads",
    )
    add_shot(
        "S38",
        "ch5_escalation",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "The machine learning algorithm quickly discovered that righteous outrage, conspiracy theories, and partisan hostility generated vastly higher click-through retention than nuanced analysis.",
        "Fiber-optic data threads fanning out across the dark slate-navy surface in vibrant contrasting colors.",
        "Tracking laterally as the cool cyan data threads turn into aggressive saturated red and amber pulses surging down the lines.",
        "camera tracks alongside the data channels as peaceful cyan pulses are violently replaced by rapid saturated red signal bursts",
    )
    add_shot(
        "S39",
        "ch5_escalation",
        True,
        0.33,
        "Precise macro focus rack",
        "Engineers never intended to polarize human civilization, yet their first-order engagement optimization systematically fractured democratic discourse across dozens of sovereign nations.",
        "Macro view of conflicting red data strands crossing and creating high-frequency optical interference patterns on the glass surface.",
        "Focus racks from the chaotic optical interference node to the original silent code terminal operating quietly in the background.",
        "focus shifts from the violently pulsing interference pattern to the cold silent monochrome monitor glowing in deep shadow",
    )
    add_shot(
        "S40",
        "ch5_escalation",
        True,
        0.55,
        "Slow arc orbit around precision apparatus",
        "When an intelligent metric becomes the sole optimization target, the system relentlessly hacks reality to maximize the number regardless of consequences.",
        "Cold monochrome monitor reflecting pulsing red and amber light across the dark studio laboratory.",
        "Orbiting around the central silicon prism as its internal structure begins overheating and glowing incandescent under intense optical current.",
        "camera orbits smoothly around the prism as intense internal luminescence creates a blinding corona of amber and red light",
    )

    # ==========================================
    # CHAPTER 6: ch6_case_study_2 (S41..S48)
    # ==========================================
    # Group 1: The Antibiotic Arms Race
    add_shot(
        "S41",
        "ch6_case_study_2",
        False,
        0.33,
        "Slow optical dolly push-in",
        "In modern medicine, first-order triumphs frequently lay the groundwork for second-order evolutionary nightmares, most vividly visible in widespread antibiotic prescription.",
        "Veritasium biological physics bench: sterilized stainless steel Petri dish illuminated by sterile cyan and ultraviolet rim lighting.",
        "Dolly in toward the agar surface of the Petri dish showing a dense translucent bacterial lawn dotted with clear inhibition zones.",
        "camera pushes in on the circular Petri dish as microscopic droplets of antibiotic compound touch the bacterial culture surface",
    )
    add_shot(
        "S42",
        "ch6_case_study_2",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "Administering a broad-spectrum antibiotic produces immediate miraculous relief by swiftly slaughtering ninety-nine percent of vulnerable bacterial pathogens within forty-eight hours.",
        "Inhibition zones expanding outward in clean concentric circular halos on the dark agar background.",
        "Tracking laterally across the agar plate showing millions of susceptible bacteria lysing and clearing away completely.",
        "camera tracks across the agar plate as clear halo rings expand, wiping out the surrounding bacterial colony in real time",
    )
    add_shot(
        "S43",
        "ch6_case_study_2",
        True,
        0.33,
        "Precise macro focus rack",
        "However, that sudden mass extinction of competitors clears unlimited resources and territory for the one surviving mutation carrying natural antibiotic resistance.",
        "Clear halo zone with a single tiny surviving bacterial cluster clinging to the central edge.",
        "Focus racks from the barren cleared agar zone to the solitary resilient colony beginning to multiply with intense vigor.",
        "focus pulls from the empty clear halo to the lone mutant bacterial clump rapidly expanding into a dense golden biofilm",
    )
    add_shot(
        "S44",
        "ch6_case_study_2",
        True,
        0.44,
        "Subtle low-angle scientific tilt-up",
        "By repeatedly deploying our strongest medical shields to treat minor ailments, we artificially select and breed untreatable, lethal global superbugs.",
        "Low-angle view of rows of amber medicine vials resting on a stainless steel medical tray beside high-precision micropipettes.",
        "Tilt up from the medicine vials to an electronic medical monitor flashing warning analytics regarding antimicrobial resistance vectors.",
        "camera tilts up from the sterile glass vials to reveal warning trajectory graphs displaying exponential resistant pathogen growth",
    )

    # Group 2: The Chemical Pesticide Treadmill
    add_shot(
        "S45",
        "ch6_case_study_2",
        False,
        0.33,
        "Slow optical dolly push-in",
        "The exact same dangerous evolutionary boomerang occurs in industrial agriculture through what agronomists formally designate as the chemical pesticide treadmill.",
        "Veritasium agrarian science stage: precision glass fume chamber containing an apple orchard branch under crisp overhead xenon lighting.",
        "Dolly in toward an apple leaf showing a delicate ecological balance between miniature herbivorous mites and predatory lady beetles.",
        "camera glides into the glass chamber focusing on the miniature leaf ecosystem where predatory insects hunt crop-eating mites",
    )
    add_shot(
        "S46",
        "ch6_case_study_2",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "Farmers spray synthetic neurotoxic chemicals to wipe out crop-eating pests, celebrating an instant twenty-percent boost in immediate seasonal harvest yield.",
        "Pesticide aerosol mist settling evenly across the glossy green waxy surface of the apple leaf.",
        "Tracking laterally as the broad-spectrum chemical instantly annihilates both the pest mites and their slow-breeding natural predatory beetle enemies.",
        "camera tracks along the leaf surface as the fine mist coats the vegetation, causing both pests and predatory insects to fall",
    )
    add_shot(
        "S47",
        "ch6_case_study_2",
        True,
        0.33,
        "Precise macro focus rack",
        "Because predatory insects reproduce much slower than rapidly mutating pest populations, the targeted pests rebound completely unchecked the following season.",
        "Fallen predatory beetles lying motionless at the base of the stem under harsh direct laboratory lighting.",
        "Focus racks from the eliminated predators to the upper bud where surviving chemically resistant mites are laying thousands of new eggs.",
        "optical focus racks from the fallen predators to thousands of microscopic resistant mite eggs coating the young plant bud",
    )
    add_shot(
        "S48",
        "ch6_case_study_2",
        True,
        0.55,
        "Slow arc orbit around precision apparatus",
        "Trapped in a vicious cycle, farmers must spray exponentially deadlier, more expensive toxins every single year just to maintain baseline production.",
        "Apple branch covered in thousands of resistant mites surrounded by empty chemical spray nozzles.",
        "Orbiting around the enclosed glass chamber as heavy industrial pressure gauges climb steadily toward the red danger threshold zone.",
        "camera completes a full orbit around the sealed chamber as brass pressure needles strain against maximum emergency limit pins",
    )

    # ==========================================
    # CHAPTER 7: ch7_systemic_shift (S49..S56)
    # ==========================================
    # Group 1: Mental Models: Inversion and Pre-Mortems
    add_shot(
        "S49",
        "ch7_systemic_shift",
        False,
        0.33,
        "Slow optical dolly push-in",
        "How do master strategists, grandmaster physicists, and resilient institutions consistently insulate their systems against the devastating traps of second-order catastrophe?",
        "Veritasium mental models laboratory: a pristine slate-navy room featuring an illuminated glass game board with polished brass chess pieces.",
        "Dolly in toward a polished brass king piece standing at the center of the dark grid illuminated by a single warm pin spot.",
        "camera pushes in on the gleaming brass chess king reflecting geometric grid coordinate lines across its polished curved base",
        ANCHOR_BASE,
    )
    add_shot(
        "S50",
        "ch7_systemic_shift",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "Their primary weapon is mental inversion, famously formulated by mathematician Carl Jacobi: man muss immer umkehren, always invert every difficult problem.",
        "Polished brass chess pieces arranged in defensive geometric formations on the illuminated glass coordinate plane.",
        "Tracking laterally as an overhead mirror tilts forty-five degrees, revealing an inverted upside-down perspective of the entire chessboard.",
        "camera tracks sideways as an overhead optical mirror swings into place, presenting a crystal-clear inverted reflection of the board",
        ANCHOR_BASE,
    )
    add_shot(
        "S51",
        "ch7_systemic_shift",
        True,
        0.33,
        "Precise macro focus rack",
        "Instead of asking how to achieve success, second-order thinkers ask: what actions would absolutely guarantee the most catastrophic possible future failure?",
        "Reflected upside-down chess pieces appearing to stand suspended against a deep navy void in sharp focus.",
        "Focus racks from the inverted reflection back to a notebook outlining critical points of vulnerability and systemic failure modes.",
        "focal plane shifts from the inverted reflection to a handwritten strategic ledger cataloging high-consequence failure pathways",
        ANCHOR_BASE,
    )
    add_shot(
        "S52",
        "ch7_systemic_shift",
        True,
        0.44,
        "Subtle low-angle scientific tilt-up",
        "By rigorously identifying every pathway leading directly to ruin, you can methodically construct robust institutional barriers that avoid those traps altogether.",
        "Low-angle view of the glass chessboard flanked by heavy brass structural columns under cool cyan studio keylight.",
        "Tilt up from the chessboard toward the architectural ceiling beams forming a protective hexagonal interlocking canopy of structural support.",
        "camera tilts up from the chessboard to reveal interlocking geometric titanium support struts reinforcing the entire ceiling structure",
        ANCHOR_BASE,
    )

    # Group 2: Negative Feedback Loops and Dynamic Dampening
    add_shot(
        "S53",
        "ch7_systemic_shift",
        False,
        0.33,
        "Slow optical dolly push-in",
        "The second vital tool is designing self-dampening negative feedback loops instead of relying on brittle top-down centralized command and control mandates.",
        "Veritasium engineering demonstration: a gleaming James Watt centrifugal flyball governor mounted on a polished brass driveshaft.",
        "Dolly in toward the spinning centrifugal governor as two heavy polished brass spheres rotate smoothly about the vertical axis.",
        "camera glides toward the rotating centrifugal governor as dual brass spheres spin outward under balanced kinetic centrifugal force",
        ANCHOR_SYSTEMS,
    )
    add_shot(
        "S54",
        "ch7_systemic_shift",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "When an engine spins too fast, the spinning spheres rise under centrifugal force, automatically closing the steam valve and moderating speed.",
        "Centrifugal governor rotating rapidly under crisp directional studio illumination, brass spheres swinging upward on articulated arms.",
        "Tracking laterally as the rising articulated arms physically pull a brass throttle linkage, smoothly constricting the main steam intake conduit.",
        "camera tracks sideways following the mechanical throttle linkage as it automatically restricts the intake valve orifice",
        ANCHOR_SYSTEMS,
    )
    add_shot(
        "S55",
        "ch7_systemic_shift",
        True,
        0.33,
        "Precise macro focus rack",
        "The system regulates itself through intrinsic physical geometry without requiring an external human operator to constantly monitor and intervene manually.",
        "Brass throttle valve maintaining constant steady steam velocity within calibrated glass manometers on the dark navy bench.",
        "Focus racks from the steam manometer fluid level to the self-stabilized flyball governor spinning at perfect equilibrium in background.",
        "focus racks from the steady manometer meniscus to the harmonious steady rotation of the flyball governor in the background",
        ANCHOR_SYSTEMS,
    )
    add_shot(
        "S56",
        "ch7_systemic_shift",
        True,
        0.55,
        "Slow arc orbit around precision apparatus",
        "Resilient human systems mirror nature: they embed balancing loops that automatically penalize overreach and reward systemic stability before runaway cascades ignite.",
        "Watt centrifugal governor spinning in effortless balance under dual cyan and amber cinematic rim lights on obsidian bench.",
        "Orbiting around the entire balanced apparatus as all mechanical linkages operate in seamless, self-correcting mechanical synchrony.",
        "camera executes a full circular orbit around the self-regulating governor as all linkages move in frictionless mechanical harmony",
        ANCHOR_SYSTEMS,
    )

    # ==========================================
    # CHAPTER 8: ch8_resolution (S57..S64)
    # ==========================================
    # Group 1: The Principle of Systemic Humility
    add_shot(
        "S57",
        "ch8_resolution",
        False,
        0.33,
        "Slow optical dolly push-in",
        "Whenever you confront a thorny complex problem in life, career, or society, resist the seductive pull of quick first-order remedies.",
        "Veritasium studio conclusion: clean minimalist slate-navy desk with a single polished glass prism resting on dark textured slate.",
        "Dolly in toward the glass prism as a single beam of pure white directional light enters its front polished face.",
        "camera pushes in on the glass prism as an intense directional ray of light passes into the transparent optical medium",
        ANCHOR_BASE,
    )
    add_shot(
        "S58",
        "ch8_resolution",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "Every seemingly simple, neat, and intuitive solution to a complex adaptive problem is almost guaranteed to be completely, spectacularly wrong.",
        "Glass prism splitting the white light beam into a brilliant rainbow spectrum projected across the dark navy slate.",
        "Tracking laterally across the projected spectrum showing crisp distinct spectral bands from deep violet to radiant scarlet red.",
        "camera tracks alongside the radiant rainbow band cast across the textured slate surface in vivid saturation",
        ANCHOR_BASE,
    )
    add_shot(
        "S59",
        "ch8_resolution",
        True,
        0.33,
        "Precise macro focus rack",
        "Complex systems are never static machines that you can fix with a hammer; they are living ecosystems that dynamically evolve.",
        "Macro view of light refractions inside the crystal prism dancing with internal reflections and subtle caustic highlights.",
        "Focus racks from the internal crystal caustics to an antique brass balance scale resting quietly in the deep background.",
        "focus pulls from the internal optical caustics of the prism to the quiet silhouette of the brass balance in the background",
        ANCHOR_BASE,
    )
    add_shot(
        "S60",
        "ch8_resolution",
        True,
        0.44,
        "Subtle low-angle scientific tilt-up",
        "Treating visible symptoms without addressing the underlying causal architecture merely transfers the strain somewhere else, compounding the eventual systemic collapse.",
        "Low-angle view of the antique brass balance scale bathed in soft warm tungsten keylight against the dark navy studio void.",
        "Tilt up from the balance pans toward the overhead fulcrum standing straight, true, and balanced under directional spotlight.",
        "camera tilts up along the central vertical brass column of the scale toward the perfectly centered balance needle",
        ANCHOR_BASE,
    )

    # Group 2: The Second-Order Mindset
    add_shot(
        "S61",
        "ch8_resolution",
        False,
        0.33,
        "Slow optical dolly push-in",
        "True intellectual maturity begins when you learn to pause, step back, and systematically trace out the secondary ripples of every decision.",
        "Veritasium physics studio: tranquil surface of a shallow water ripple tank illuminated by low-angle oblique amber spotlight.",
        "Dolly in toward the glass tank as a single water droplet falls from a precision dropper into the center of the pool.",
        "camera pushes in on the mirror-smooth water surface as a single drop falls, creating concentric expanding ripple rings",
    )
    add_shot(
        "S62",
        "ch8_resolution",
        True,
        0.33,
        "Smooth horizontal lateral tracking pass",
        "A single stone thrown into a pond generates circular waves that bounce off distant banks, returning to reshape the central point.",
        "Concentric circular ripples propagating outward across the dark water surface under dramatic oblique lighting.",
        "Tracking laterally as the expanding wavefronts reach the acrylic boundary walls, reflecting back into intricate constructive interference patterns.",
        "camera tracks with the moving ripple wavefronts as they reflect off the tank walls, creating delicate geometric interference waves",
    )
    add_shot(
        "S63",
        "ch8_resolution",
        True,
        0.33,
        "Precise macro focus rack",
        "By anticipating those inevitable returning waves before you cast your stone, you navigate reality with genuine wisdom rather than naive intentions.",
        "Intricate water interference nodes glistening like liquid jewels under dual cyan and amber laboratory spotlights.",
        "Focus racks from the shimmering water nodes to the still, motionless surface reflecting the dark navy infinite studio space above.",
        "focus racks from the shimmering interference ripples to the calm stillness returning to the water surface",
    )
    add_shot(
        "S64",
        "ch8_resolution",
        True,
        0.55,
        "Slow arc orbit around precision apparatus",
        "In a world dominated by reactionary first-order impulses, mastering second-order thinking is your ultimate unfair advantage for life and leadership.",
        "Veritasium studio wide panorama: the glowing ripple tank, glass prism, and brass balance aligned along the slate workbench.",
        "Orbiting around the entire demonstration bench as the studio keylights dim down to a dignified, glowing slate-navy twilight finale.",
        "camera executes a majestic sweeping pull-back orbit around the workbench as keylights fade to an iconic dark navy studio twilight",
    )

    return shots


def get_short_shots() -> list[dict[str, Any]]:
    # 7 shots, 13-15 words per shot, total ~98 words, CTA in S07
    shots = [
        {
            "shot_id": "S01",
            "scene_group": "G1",
            "continues_prev": False,
            "scene_anchor": ANCHOR_BASE,
            "narration": "When a measure becomes an official performance target, it instantly ceases being useful.",
            "pause_after_sec": 0.35,
            "camera_verb": "Slow optical dolly push-in",
            "start_visual": "Veritasium scientific demonstration bench: an ornate brass balance scale resting on polished dark slate under sharp directional keylight, strictly zero text.",
            "end_visual": "Dolly in on the brass balance as calibrated metric weights drop into one pan, snapping the central needle toward red, strictly zero text.",
            "subject_motion": "brass scale needle snaps violently to the right under sudden metric weight impact",
        },
        {
            "shot_id": "S02",
            "scene_group": "G1",
            "continues_prev": True,
            "scene_anchor": ANCHOR_BASE,
            "narration": "This is Goodhart’s Law, the iron rule governing every modern human performance metric.",
            "pause_after_sec": 0.35,
            "camera_verb": "Smooth horizontal lateral tracking pass",
            "start_visual": "Close-up of the brass balance with the snapped needle vibrating under high-contrast spotlight.",
            "end_visual": "Tracking laterally across the workbench revealing a row of precision mechanical dials all redlining under strain, strictly zero text.",
            "subject_motion": "camera tracks sideways as multiple precision mechanical needle dials swing into maximum strain positions",
        },
        {
            "shot_id": "S03",
            "scene_group": "G2",
            "continues_prev": False,
            "scene_anchor": ANCHOR_SYSTEMS,
            "narration": "When British hospitals graded surgeons on patient survival rates, doctors refused high-risk surgeries.",
            "pause_after_sec": 0.35,
            "camera_verb": "Slow optical dolly push-in",
            "start_visual": "Stainless steel medical examination table with sterilized chrome surgical instruments bathed in sterile cyan laboratory illumination, strictly zero text.",
            "end_visual": "Dolly closer as a mechanical barrier descends, walling off high-risk surgical instruments from the primary operating station, strictly zero text.",
            "subject_motion": "frosted glass barrier lowers slowly across the chrome surgical instruments isolating the tray",
        },
        {
            "shot_id": "S04",
            "scene_group": "G2",
            "continues_prev": True,
            "scene_anchor": ANCHOR_SYSTEMS,
            "narration": "Reported survival scores surged dramatically, while the sickest patients were left completely untreated.",
            "pause_after_sec": 0.35,
            "camera_verb": "Precise macro focus rack",
            "start_visual": "Isolated surgical tray behind frosted glass barrier in high-contrast cyan laboratory lighting.",
            "end_visual": "Focus racks from a glowing green percentage dial to a dark empty hospital corridor, strictly zero text.",
            "subject_motion": "optical focus pulls from the glowing green dial to the deep shadow of the corridor",
        },
        {
            "shot_id": "S05",
            "scene_group": "G3",
            "continues_prev": False,
            "scene_anchor": ANCHOR_BASE,
            "narration": "Humans will always game the measured number rather than produce the genuine underlying goal.",
            "pause_after_sec": 0.35,
            "camera_verb": "Smooth horizontal lateral tracking pass",
            "start_visual": "Dark navy tabletop with a row of frosted glass dominoes illuminated by sharp amber rim lighting, strictly zero text.",
            "end_visual": "Tracking laterally as a robotic mechanical arm bypasses the domino runway to trip the final bell directly, strictly zero text.",
            "subject_motion": "robotic articulated arm reaches around the domino obstacles to touch the target bell directly",
        },
        {
            "shot_id": "S06",
            "scene_group": "G3",
            "continues_prev": True,
            "scene_anchor": ANCHOR_BASE,
            "narration": "To fix complex systems, you must measure holistic outcomes instead of isolated single proxies.",
            "pause_after_sec": 0.35,
            "camera_verb": "Subtle low-angle scientific tilt-up",
            "start_visual": "Robotic mechanical arm touching the brass bell under warm directional spotlight on obsidian surface.",
            "end_visual": "Tilt up to reveal an interconnected spiderweb array of dynamic balancing weights maintaining multi-point equilibrium, strictly zero text.",
            "subject_motion": "camera tilts up revealing a multi-axis hanging mobile of brass weights swinging in balanced harmony",
        },
        {
            "shot_id": "S07",
            "scene_group": "G4",
            "continues_prev": False,
            "scene_anchor": ANCHOR_BASE,
            "narration": "Discover how counter-intuitive incentives reshape human behavior in our full second-order thinking breakdown.",
            "pause_after_sec": 0.35,
            "camera_verb": "Slow arc orbit around precision apparatus",
            "start_visual": "Veritasium studio wide shot of the multi-axis balance mobile spinning gently in dark slate-navy twilight, strictly zero text.",
            "end_visual": "Sweeping orbit around the gleaming brass mobile as keylights focus on the central balanced fulcrum, strictly zero text.",
            "subject_motion": "camera orbits smoothly around the central brass fulcrum as balanced weights rotate gracefully in twilight",
        },
    ]
    return shots


def build_and_save() -> None:
    long_shots = get_long_shots()
    short_shots = get_short_shots()

    long_spec = {
        "job_id": "en-first-principles-batch1-16x9",
        "channel_slug": "en-first-principles",
        "aspect": "16:9",
        "title": "Second-Order Thinking & The Cobra Effect: Why Well-Intentioned Fixes Create Worse Disasters",
        "youtube_title": "Why Good Solutions Cause Worse Disasters",
        "thumbnail_spec": {
            "visual_hook": "Archival Prussian cyanotype blueprint showing a brass balance scale tipping a giant cobra domino into a row of collapsing gears",
            "allowed_text": "THE COBRA EFFECT",
            "overlay_card": False,
        },
        "voice": "en-US-ChristopherNeural",
        "shots": long_shots,
    }

    short_spec = {
        "job_id": "en-first-principles-batch1-9x16",
        "parent_long_id": "en-first-principles-batch1-16x9",
        "channel_slug": "en-first-principles",
        "aspect": "9:16",
        "title": "Goodhart's Law: Why Measuring a Target Instantly Destroys It",
        "youtube_title": "Goodhart's Law: The Metric Trap",
        "thumbnail_spec": {
            "visual_hook": "High-contrast brass balance scale with glowing cyan needle snapping under excess metric weights against dark slate slate-navy void",
            "allowed_text": "METRIC TRAP",
            "overlay_card": False,
        },
        "voice": "en-US-ChristopherNeural",
        "shots": short_shots,
    }

    from generate_en_batch1_specs import validate_shots

    print("Validating en-first-principles Long...")
    validate_shots(long_shots, is_long=True)
    print("Validating en-first-principles Short...")
    validate_shots(short_shots, is_long=False)

    p_long = OUT_DIR / "en-first-principles_long_16x9.json"
    p_short = OUT_DIR / "en-first-principles_short_9x16.json"

    p_long.write_text(json.dumps(long_spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    p_short.write_text(json.dumps(short_spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved: {p_long} and {p_short}")


if __name__ == "__main__":
    build_and_save()
