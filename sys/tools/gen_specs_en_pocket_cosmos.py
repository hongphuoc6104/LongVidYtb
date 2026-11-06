#!/usr/bin/env python3
"""Spec builder for en-pocket-cosmos (Long 16:9 and Short 9:16)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SYS_TOOLS = Path(__file__).resolve().parent
if str(SYS_TOOLS) not in sys.path:
    sys.path.insert(0, str(SYS_TOOLS))

from generate_en_batch1_specs import validate_shots

OUT_DIR = Path("sys/channels/en_batch1_specs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ANCHOR_SPACE = (
    "Melodysheep hyper-detailed IMAX deep-space cinematography lit by a single coherent off-screen star keylight "
    "against pure velvet interstellar void, strictly zero text"
)
ANCHOR_EARTH_ORBIT = (
    "Cinematic 8K orbital view of planet Earth floating against the deep velvet cosmic void, "
    "realistic Rayleigh atmospheric scattering and blue oceanic limb glow, strictly zero text"
)
ANCHOR_SURFACE_FROZEN = (
    "Cinematic exoplanetary surface perspective of Earth under starlight, vast frozen oceans and glaciers "
    "illuminated by the luminous Milky Way spiral in absolute crystal-clear atmosphere, strictly zero text"
)
ANCHOR_ABYSS = (
    "Cinematic deep abyssal ocean trench cinematography, luminous geothermal hydrothermal vents glowing "
    "with electric cyan and amber minerals in eternal oceanic blackness, strictly zero text"
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
        anchor: str = ANCHOR_SPACE,
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
    # Group 1: The Disappearing Sun
    add_shot(
        "S01",
        "ch1_hook",
        False,
        0.33,
        "Grand parabolic space-probe flyby",
        "At this exact microsecond, imagine the Sun instantly vanishes from existence: no supernova explosion, no expanding red giant, simply gone forever.",
        "Melodysheep IMAX deep-space view: the blazing incandescent golden Sun dominating the cosmic frame with swirling convective plasma flares.",
        "Parabolic flyby past the solar orb as its intense golden corona abruptly flickers and snaps into absolute pitch-black vacuum.",
        "blazing solar corona abruptly vanishes into cold velvet blackness, leaving an empty gravitational coordinate in deep space",
        ANCHOR_SPACE,
    )
    add_shot(
        "S02",
        "ch1_hook",
        True,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Yet back on Earth, ninety-three million miles away, absolutely nobody notices anything unusual as children play under warm golden afternoon sunshine.",
        "Cinematic orbital view of vibrant blue planet Earth bathed in warm radiant sunlight, pacific cloud swirls gleaming under blue limb scattering.",
        "Pushing in toward the sunlit continent where lush green forests and glittering oceans bask peacefully under golden daylight.",
        "camera pushes in on the radiant daylight hemisphere of Earth turning gracefully in peaceful Keplerian orbit",
        ANCHOR_EARTH_ORBIT,
    )
    add_shot(
        "S03",
        "ch1_hook",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "Because photons travel at the cosmic speed limit of three hundred thousand kilometers per second, solar rays require eight minutes to arrive.",
        "Deep-space view looking across the vast interplanetary void separating the empty solar coordinates from the glowing blue marble of Earth.",
        "Drifting laterally through space alongside an immense wavefront of golden photons streaming through the cold dark vacuum toward Earth.",
        "camera drifts alongside a vast luminous beam of sunlight traveling across ninety-three million miles of vacuum",
        ANCHOR_SPACE,
    )
    add_shot(
        "S04",
        "ch1_hook",
        True,
        0.44,
        "Grand parabolic space-probe flyby",
        "For eight minutes and twenty seconds, our planet continues orbiting happily through space, sustained entirely by borrowed light from an extinct star.",
        "Parabolic space-probe perspective gliding above the ecliptic plane, showing Earth tracing its curved Keplerian orbital ellipse in glowing cyan.",
        "Flyby tracking Earth along its glowing curved trajectory, unaware that the central gravitational anchor holding it has ceased to exist.",
        "Earth follows its curved orbital trajectory around the empty solar coordinate, illuminated by the final streaming solar rays",
        ANCHOR_SPACE,
    )

    # Group 2: The Gravitational Wave
    add_shot(
        "S05",
        "ch1_hook",
        False,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "General relativity dictates that gravity is not an instantaneous force; it travels across spacetime fabric at the exact same cosmic speed limit.",
        "Melodysheep IMAX cosmic visual: the fabric of spacetime visualized as an immense glowing cyan coordinate grid warped by massive stellar gravity.",
        "Pushing in on the empty central crater in spacetime as ripples of gravitational waves propagate outward like concentric waves in water.",
        "gravitational waves ripple outward across the warped spacetime fabric in concentric luminous waves at the speed of light",
        ANCHOR_SPACE,
    )
    add_shot(
        "S06",
        "ch1_hook",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "The curvature of space flattened by the Sun relaxes into flat Euclidean geometry, sending a gravitational wave racing outwards alongside the light.",
        "Spacetime coordinate grid uncoiling from a deep gravitational funnel into a pristine flat geometrical plane behind the expanding wave.",
        "Drifting alongside the combined front of the gravitational shockwave and the terminal boundary of the final photon wave.",
        "camera drifts beside the expanding spacetime ripple as the warped gravitational well snaps into flat planar void",
        ANCHOR_SPACE,
    )
    add_shot(
        "S07",
        "ch1_hook",
        True,
        0.33,
        "Grand parabolic space-probe flyby",
        "Eight minutes pass with clockwork indifference; the final beam of sunlight and the gravitational wave arrive at Earth at the exact same instant.",
        "Wide cinematic view of Earth centered in frame as the sharp trailing edge of sunlight races across the blue oceans.",
        "Flyby as the trailing shadow border sweeps over the daytime continents, plunging entire landmasses into sudden, terrifying midnight blackness.",
        "trailing edge of sunlight sweeps across Earth's continents, extinguishing daylight into instant pitch-black darkness",
        ANCHOR_EARTH_ORBIT,
    )
    add_shot(
        "S08",
        "ch1_hook",
        True,
        0.55,
        "Slow weightless orbital push-in toward terminator line",
        "In a fraction of a second, the daytime sky snaps black, stars ignite in mid-afternoon, and our world breaks free forever.",
        "Orbital perspective as the illuminated daylight hemisphere vanishes completely, replaced by millions of brilliant pinpoint stars against velvet blackness.",
        "Pushing in on the darkened planet as city electrical grids flicker into view like delicate glowing amber spiderwebs in the dark.",
        "daylight hemisphere instantly darkens as dazzling field of stars emerges, revealing glowing spiderwebs of city lights",
        ANCHOR_EARTH_ORBIT,
    )

    # ==========================================
    # CHAPTER 2: ch2_paradox (S09..S16)
    # ==========================================
    # Group 1: The Tangential Slingshot
    add_shot(
        "S09",
        "ch2_paradox",
        False,
        0.33,
        "Grand parabolic space-probe flyby",
        "With the Sun’s gravitational well flattened to zero, Earth no longer bends along an elliptical curve around the center of our solar system.",
        "Melodysheep IMAX view: high-angle perspective of the inner solar system showing Earth's glowing elliptical orbit line unspooling.",
        "Parabolic flyby as the curved cyan orbital ellipse snaps like a cut string, releasing the planet into a straight tangential velocity vector.",
        "curved orbital ellipse snaps cleanly, releasing planet Earth into a straight tangential trajectory through deep space",
        ANCHOR_SPACE,
    )
    add_shot(
        "S10",
        "ch2_paradox",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "Newton’s first law of motion takes absolute command: Earth hurtles in a straight tangent line at thirty kilometers every single second.",
        "Deep-space perspective tracking Earth from the side as it streaks smoothly across the dark void at sixty-seven thousand miles per hour.",
        "Drifting alongside the dark blue orb as it glides past the orbits of Mars and the outer gas giants into uncharted deep space.",
        "darkened Earth hurtles steadily through the black void at thirty kilometers per second along a straight linear path",
        ANCHOR_SPACE,
    )
    add_shot(
        "S11",
        "ch2_paradox",
        True,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "There is no cosmic turbulence, no violent shuddering, and no physical jolt felt by any living human standing on the planet surface.",
        "Cinematic orbital close-up of Earth's atmosphere gliding smoothly across the frame without any atmospheric stripping or shock.",
        "Pushing in on the calm, unperturbed cloud formations drifting serenely above darkened continents under sparkling celestial starlight.",
        "delicate swirling clouds drift serenely across dark continents under brilliant starlight without atmospheric disturbance",
        ANCHOR_EARTH_ORBIT,
    )
    add_shot(
        "S12",
        "ch2_paradox",
        True,
        0.44,
        "Grand parabolic space-probe flyby",
        "Earth’s mass and velocity carry it silently outward into the interstellar abyss, transitioning from an anchored planet into a lonely rogue nomad.",
        "Parabolic space-probe flyby looking back at the shrinking solar system as inner planets disperse in different linear directions into the dark.",
        "Flyby expanding into vast interstellar scale as Earth becomes an isolated jewel drifting through the infinite velvet sea of the Milky Way.",
        "camera sweeps wide into deep interstellar space as solitary Earth drifts into the colossal starfield of the Milky Way",
        ANCHOR_SPACE,
    )

    # Group 2: The Stolen Sky
    add_shot(
        "S13",
        "ch2_paradox",
        False,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Looking upward from the surface, humans behold an astronomical sight never witnessed in five billion years of terrestrial evolutionary existence.",
        "Cinematic surface view looking up from a dark mountain observatory into the crystal-clear night sky devoid of any moon or sun.",
        "Pushing in on the celestial dome where the glowing gaseous spiral arm of the Milky Way blazes with blinding clarity from horizon to horizon.",
        "luminous Milky Way galactic core blazes in pristine clarity across the crystal-clear night sky without light pollution",
        ANCHOR_SURFACE_FROZEN,
    )
    add_shot(
        "S14",
        "ch2_paradox",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "The Moon has completely vanished from sight: with no solar photons left to reflect off its lunar regolith, it becomes an invisible ghost.",
        "Deep-space view looking toward the orbital plane of the Moon revolving silently around the darkened globe of Earth.",
        "Drifting past the dark silhouette of the Moon, only detectable as a black circular shadow eclipsing distant sparkling background stars.",
        "dark circular silhouette of the Moon occults background star clusters as it orbits the darkened globe of Earth",
        ANCHOR_SPACE,
    )
    add_shot(
        "S15",
        "ch2_paradox",
        True,
        0.33,
        "Grand parabolic space-probe flyby",
        "Jupiter, Saturn, Mars, and Venus all blink out one by one as the trailing edge of darkness sweeps past their distant orbits.",
        "Parabolic flyby across the solar system as the gleaming lanterns of Jupiter and Saturn fade into absolute blackness as sunlight leaves them.",
        "Flyby as the entire familiar planetary family dissolves into invisible dark masses floating cold and separate across interstellar space.",
        "glowing planetary discs of Jupiter and Saturn fade into cold darkness as the solar shadow sweeps across outer orbits",
        ANCHOR_SPACE,
    )
    add_shot(
        "S16",
        "ch2_paradox",
        True,
        0.55,
        "Slow weightless orbital push-in toward terminator line",
        "Humanity stands under a cathedral of cold, indifferent distant stars, suddenly stripped of the cosmic hearth that birthed all life.",
        "Wide cinematic view of darkened Earth framed against the immense luminous spiral dust lanes of our home galaxy.",
        "Pushing in slowly toward the fragile blue marble as its glowing atmospheric halo radiates its final thermal warmth into the void.",
        "fragile glowing atmospheric halo of Earth radiates faint thermal warmth into the freezing infinity of deep space",
        ANCHOR_SPACE,
    )

    # ==========================================
    # CHAPTER 3: ch3_mechanism (S17..S24)
    # ==========================================
    # Group 1: The Cessation of Photosynthesis
    add_shot(
        "S17",
        "ch3_mechanism",
        False,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Within twenty-four hours of eternal darkness, the foundational biochemical engine of the global biosphere grinds to an absolute, permanent halt.",
        "Melodysheep exoplanetary surface cinematography: dense tropical rainforest canopy illuminated by faint starlight and artificial research floodlights.",
        "Pushing in toward a lush green broadleaf fern as microscopic cellular chloroplasts cease their photosynthetic photon absorption cycles.",
        "camera pushes in on dark green fern leaf as cellular metabolic activity slows under the sudden absence of solar photons",
        ANCHOR_SURFACE_FROZEN,
    )
    add_shot(
        "S18",
        "ch3_mechanism",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "Without incoming solar photons, plant chlorophyll can no longer split water molecules to generate glucose, shutting down global oxygen production completely.",
        "Macro optical view of leaf cellular stomata closing tightly under cool descending atmospheric temperatures.",
        "Drifting laterally across the forest canopy as thousands of plant species enter metabolic dormancy, halting carbon dioxide absorption forever.",
        "camera drifts across the silent darkened forest canopy as leaves stiffen under dropping atmospheric humidity",
        ANCHOR_SURFACE_FROZEN,
    )
    add_shot(
        "S19",
        "ch3_mechanism",
        True,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Yet contrary to popular apocalyptic belief, humanity will not immediately suffocate: Earth’s atmosphere contains a colossal reservoir of breathable oxygen.",
        "Cinematic orbital perspective of Earth's thin luminous blue atmospheric layer glowing softly against the dark vacuum.",
        "Pushing in on the dense lower troposphere containing six quintillion kilograms of atmospheric gases wrapped snugly around the globe.",
        "thin blue atmospheric boundary layer remains intact, holding vast reserves of breathable air around the dark planet",
        ANCHOR_EARTH_ORBIT,
    )
    add_shot(
        "S20",
        "ch3_mechanism",
        True,
        0.44,
        "Grand parabolic space-probe flyby",
        "Even with zero photosynthetic replenishment, eight billion humans and all animal life would take several millennia to consume the existing atmospheric supply.",
        "Parabolic space-probe flyby skimming over the illuminated electrical grids of major coastal cities glowing in the dark.",
        "Flyby revealing resilient human infrastructure powered by nuclear fission, coal, and geothermal energy glowing brightly in the dark.",
        "electric grids of metropolitan cities blaze with artificial light, defying the absolute blackness of deep space",
        ANCHOR_EARTH_ORBIT,
    )

    # Group 2: The Thermal Plunge
    add_shot(
        "S21",
        "ch3_mechanism",
        False,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "The true lethal threat is not lack of oxygen; it is the merciless, exponential collapse of surface planetary thermal energy.",
        "Melodysheep climate physics simulation: infrared thermal imaging of Earth showing warm red and yellow continental heat signatures.",
        "Pushing in as the warm thermal colors rapidly cool into deep indigo, cyan, and violet as heat radiates into space.",
        "infrared thermal heat map of Earth shifts rapidly from warm amber to cold deep cyan as surface warmth bleeds into vacuum",
        ANCHOR_EARTH_ORBIT,
    )
    add_shot(
        "S22",
        "ch3_mechanism",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "Earth’s surface normally absorbs one hundred and seventy-four petawatts of continuous solar radiation, balancing what it radiates into cold vacuum.",
        "Deep-space view showing the planet radiating blackbody infrared radiation into the three-Kelvin cosmic background void.",
        "Drifting alongside the planet as the energy balance becomes completely one-sided, bleeding internal thermal reserves into the infinite void.",
        "unbalanced blackbody radiation bleeds steadily from Earth's upper atmosphere into the three-Kelvin cosmic background",
        ANCHOR_SPACE,
    )
    add_shot(
        "S23",
        "ch3_mechanism",
        True,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "By hour seventy-two, average global surface temperatures drop from fourteen degrees Celsius down to zero, locking freshwater rivers in ice.",
        "Cinematic surface view of a broad winding river passing through a forested valley under brilliant stellar illumination.",
        "Pushing in as crystal needle dendrites of ice rapidly nucleate across the water surface, locking the river into rigid glass.",
        "geometric ice crystal dendrites shoot rapidly across the river surface, freezing the running water into solid glass",
        ANCHOR_SURFACE_FROZEN,
    )
    add_shot(
        "S24",
        "ch3_mechanism",
        True,
        0.55,
        "Grand parabolic space-probe flyby",
        "A living planet accustomed to geological balances of heat begins an unprecedented plunge toward thermal equilibrium with the cold cosmic void.",
        "Parabolic flyby pulling back from the freezing continents, showing vast white ice sheets expanding across formerly temperate landmasses.",
        "Flyby expanding into orbit as shimmering auroras dance across the darkened polar caps in cold green and violet curtains.",
        "shimmering green auroral curtains dance across the polar skies above continents rapidly freezing under starlight",
        ANCHOR_EARTH_ORBIT,
    )

    # ==========================================
    # CHAPTER 4: ch4_case_study_1 (S25..S32)
    # ==========================================
    # Group 1: Week One: The Global Sub-Zero Freeze
    add_shot(
        "S25",
        "ch4_case_study_1",
        False,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Seven days after the sun vanished, global average surface temperatures plunge past minus twenty degrees Celsius across all six continents.",
        "Melodysheep surface view: downtown cityscape standing frozen in absolute silence under crystal starlight with zero vehicle traffic.",
        "Pushing in past snowdrifts burying abandoned streets, skyscrapers coated in sheets of glistening hoarfrost from street level to rooftop.",
        "glistening hoarfrost coats skyscraper glass facades as deep snowdrifts bury abandoned metropolitan avenues",
        ANCHOR_SURFACE_FROZEN,
    )
    add_shot(
        "S26",
        "ch4_case_study_1",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "Global weather patterns fundamentally collapse: because weather is driven by differential solar heating between equator and poles, wind dies away.",
        "Wide panoramic view of mountain ranges and frozen valleys where the atmosphere has become unnaturally calm, motionless, and dead.",
        "Drifting across the still mountain peaks as turbulent atmospheric jet streams dissolve into stagnant, motionless freezing air layers.",
        "high-altitude atmospheric jet streams decelerate and dissolve into dead, motionless crystal-clear freezing air",
        ANCHOR_SURFACE_FROZEN,
    )
    add_shot(
        "S27",
        "ch4_case_study_1",
        True,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Without convective evaporation from warm oceans, global cloud formation ceases completely; the night sky becomes a perpetually pristine crystal glass window.",
        "Orbital perspective looking down through the thinning cloud cover at the dark outline of continents rimmed in ice.",
        "Pushing in as the last remnants of oceanic stratus clouds evaporate and settle, leaving the planetary atmosphere completely cloudless.",
        "remaining atmospheric cloud decks evaporate and vanish, leaving the entire globe under a crystal-clear cloudless sky",
        ANCHOR_EARTH_ORBIT,
    )
    add_shot(
        "S28",
        "ch4_case_study_1",
        True,
        0.44,
        "Grand parabolic space-probe flyby",
        "Surviving terrestrial animal species face catastrophic biological collapse as freezing temperatures destroy food supplies and water sources across every single habitat.",
        "Surface frame of a frozen pine forest under moonlight-bright starlight, snow-covered branches sagging in absolute sub-zero silence.",
        "Flyby along the frozen forest floor where small mammals have retreated into deep subterranean burrows seeking residual soil warmth.",
        "camera glides along the frozen forest floor where all surface biological movement has ceased beneath deep snow",
        ANCHOR_SURFACE_FROZEN,
    )

    # Group 2: The Thermal Insulation of the Atmosphere
    add_shot(
        "S29",
        "ch4_case_study_1",
        False,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Why does Earth not freeze into absolute zero immediately? The secret lies in the colossal thermal inertia of our oceans.",
        "Melodysheep IMAX view of the dark global ocean spanning thousands of miles across the curved horizon under starlight.",
        "Pushing in toward the ocean surface where waves churn with immense kinetic energy, releasing stored thermal warmth into air.",
        "dark oceanic waves churn under brilliant starlight, releasing massive stored thermal enthalpy into the cold air",
        ANCHOR_SURFACE_FROZEN,
    )
    add_shot(
        "S30",
        "ch4_case_study_1",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "Water has one of the highest specific heat capacities of any substance in chemistry: four thousand one hundred joules per kilogram.",
        "Macro optical cross-section of seawater molecules transferring thermal kinetic energy upward toward the frigid atmospheric interface.",
        "Drifting across the water column showing convection currents circulating warmer deep water up toward the cooling surface.",
        "deep marine convection currents circulate warm water upward from the depths toward the rapidly cooling surface layer",
        ANCHOR_ABYSS,
    )
    add_shot(
        "S31",
        "ch4_case_study_1",
        True,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "The oceans hold over one septillion kilograms of water, functioning like a gargantuan planetary thermal battery that cushions the catastrophic fall.",
        "Orbital view of the vast Pacific Ocean basin glowing faintly in infrared thermal bands against the frozen surrounding landmasses.",
        "Pushing in on the marine expanse as thin sheets of sea ice begin creeping outward from polar shores toward the equator.",
        "thin sheets of pack ice expand outward from coastlines across the dark surface of the Pacific Ocean basin",
        ANCHOR_EARTH_ORBIT,
    )
    add_shot(
        "S32",
        "ch4_case_study_1",
        True,
        0.55,
        "Grand parabolic space-probe flyby",
        "This oceanic battery buys Earth precious time, preventing the immediate atmospheric freeze that would otherwise occur on an airless rocky world.",
        "Parabolic space-probe flyby skimming over the boundary where sea ice meets open liquid ocean under the Milky Way.",
        "Flyby tracking the expanding sea ice shelf glistening under celestial starlight as the planet hurtles through the cosmic void.",
        "camera sweeps along the edge of expanding polar pack ice as solitary Earth hurtles forward through deep space",
        ANCHOR_SPACE,
    )

    # ==========================================
    # CHAPTER 5: ch5_escalation (S33..S40)
    # ==========================================
    # Group 1: Month One to Six: The Ice Shield
    add_shot(
        "S33",
        "ch5_escalation",
        False,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "One year into the interstellar drift, surface temperatures plunge to a punishing minus seventy-three degrees Celsius across the entire globe.",
        "Melodysheep surface visual: high Arctic-like conditions dominating equatorial cities like Singapore and Panama, buried under glaciers.",
        "Pushing in on palm trees encased completely in solid transparent ice, frozen like prehistoric specimens under the blazing starlight.",
        "glaciers engulf tropical avenues as palm trees stand encased in solid transparent ice under the starry sky",
        ANCHOR_SURFACE_FROZEN,
    )
    add_shot(
        "S34",
        "ch5_escalation",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "The surface of every ocean on Earth freezes solid, forming a continuous crust of sea ice several meters thick everywhere.",
        "Wide cinematic tracking shot across what was once the open Atlantic Ocean, now an endless expanse of ridged blue ice.",
        "Drifting over colossal pressure ridges and blue ice crevasses glowing under the radiant dust lanes of the galactic center.",
        "camera drifts across endless expanses of ridged oceanic sea ice stretching to the dark horizon under the stars",
        ANCHOR_SURFACE_FROZEN,
    )
    add_shot(
        "S35",
        "ch5_escalation",
        True,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Yet here occurs a miraculous biological salvation: ice floats on water because its crystalline solid structure is less dense than liquid.",
        "Cinematic cross-section of the ocean surface showing the thick floating sheet of ice resting atop deep liquid seawater below.",
        "Pushing down through the translucent blue ice into the dark liquid marine depths sheltered beneath the insulating frozen canopy.",
        "camera descends through translucent blue surface ice into the sheltered liquid marine abyss beneath the frozen sheet",
        ANCHOR_ABYSS,
    )
    add_shot(
        "S36",
        "ch5_escalation",
        True,
        0.44,
        "Grand parabolic space-probe flyby",
        "Ice is an exceptional thermal insulator: as the surface sheet thickens, it blocks heat transfer, preserving vast liquid oceans below.",
        "Parabolic space-probe flyby looking down at the completely white frozen planetary sphere glistening under starlight like Jupiter’s moon Europa.",
        "Flyby revealing the global ice shell sealing in billions of cubic kilometers of liquid ocean heated from the planetary core below.",
        "global ice shell seals the entire planetary ocean, creating an insulated aquatic world warmed from interior depths",
        ANCHOR_EARTH_ORBIT,
    )

    # Group 2: The Core’s Internal Fire
    add_shot(
        "S37",
        "ch5_escalation",
        False,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Deep beneath the frozen ocean crust, Earth possesses an independent, unyielding nuclear engine that has burned for four billion years.",
        "Melodysheep 3D geological cross-section: slicing through Earth's crust and mantle to reveal the incandescent glowing molten core.",
        "Pushing in toward the outer liquid iron core churning at six thousand degrees Celsius, matching the temperature of the Sun.",
        "camera pushes through tectonic layers to the incandescent liquid iron core churning under immense geological pressure",
        ANCHOR_SPACE,
    )
    add_shot(
        "S38",
        "ch5_escalation",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "Continuous radioactive decay of primordial isotopes—uranium, thorium, and potassium—generates forty-seven terawatts of internal heat flowing steadily upward through the mantle.",
        "Glowing mineral conduits in the deep mantle conducting geothermal heat upward through basaltic tectonic plates toward ocean trenches.",
        "Drifting along tectonic fault lines where superheated volcanic magma chambers warm subterranean rock formations for hundreds of miles.",
        "geothermal heat plumes rise through the solid mantle rock, channeling primordial nuclear warmth toward abyssal rifts",
        ANCHOR_ABYSS,
    )
    add_shot(
        "S39",
        "ch5_escalation",
        True,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "This continuous internal geothermal flux ensures that the ocean floor will never freeze, keeping vast marine abyssal ecosystems alive indefinitely.",
        "Cinematic view of the ocean floor six miles beneath the surface ice, bathed in complete silence and absolute liquid warmth.",
        "Pushing in on hydrothermal vents spewing mineral-rich black smoke columns into the surrounding deep warm ocean trenches.",
        "hydrothermal vents spew mineral-rich black plumes into the surrounding liquid trench water, nourishing abyssal ecosystems",
        ANCHOR_ABYSS,
    )
    add_shot(
        "S40",
        "ch5_escalation",
        True,
        0.55,
        "Grand parabolic space-probe flyby",
        "Even as surface temperatures approach absolute cold, the interior fire of Earth guarantees that liquid life endures deep beneath the ice.",
        "Parabolic space-probe flyby showing Earth drifting gracefully past distant sparkling nebulae and interstellar gas clouds in deep space.",
        "Flyby highlighting the dual nature of rogue Earth: a frozen dead exterior crust shielding a thriving, warm subterranean ocean world.",
        "camera sweeps around the frozen rogue planet as its warm volcanic core pulses beneath miles of protective ice",
        ANCHOR_SPACE,
    )

    # ==========================================
    # CHAPTER 6: ch6_case_study_2 (S41..S48)
    # ==========================================
    # Group 1: Year One: Liquid Air and Nitrogen Snow
    add_shot(
        "S41",
        "ch6_case_study_2",
        False,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Decades into its journey through deep interstellar space, surface temperatures drop toward a bone-chilling minus two hundred and fifteen Celsius.",
        "Melodysheep surface cinematography: surreal frozen landscape under starlight where atmospheric gases begin undergoing bizarre phase transitions.",
        "Pushing in toward an icy plain where the air itself appears hazy, condensing into translucent clouds of liquefied gas mist.",
        "translucent clouds of liquefied atmospheric mist drift slowly across the glassy frozen surface of the dead continent",
        ANCHOR_SURFACE_FROZEN,
    )
    add_shot(
        "S42",
        "ch6_case_study_2",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "At minus one hundred and ninety-six degrees, nitrogen gas—seventy-eight percent of our air—begins condensing and raining down as liquid drops.",
        "Macro perspective of delicate nitrogen raindrops condensing out of the frigid sky, splashing onto glassy frozen ground.",
        "Drifting laterally across riverbeds carved not by water, but by cascading streams of liquid nitrogen flowing into frozen basins.",
        "cascading streams of liquid nitrogen flow through glassy frozen channels across the alien surface of Earth",
        ANCHOR_SURFACE_FROZEN,
    )
    add_shot(
        "S43",
        "ch6_case_study_2",
        True,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "At minus two hundred and ten, liquid nitrogen freezes into crystalline snow, blanketing the planet under white drifts of frozen air.",
        "Wide shot of surreal dunes composed entirely of frozen nitrogen crystals glistening under the sharp pinpoint light of distant stars.",
        "Pushing in on the frozen nitrogen dunes as gentle planetary outgassing creates strange geysers venting into the thin remaining vacuum.",
        "nitrogen snow dunes glisten under sparkling starlight as cold geysers vent plumes into the crystal-clear thin air",
        ANCHOR_SURFACE_FROZEN,
    )
    add_shot(
        "S44",
        "ch6_case_study_2",
        True,
        0.44,
        "Grand parabolic space-probe flyby",
        "Earth’s atmosphere has literally fallen to the ground: the sky is now a hard vacuum, rivaling the emptiness of deep interstellar space.",
        "Parabolic space-probe flyby skimming just miles above the frozen mountain summits without encountering any atmospheric aerodynamic drag.",
        "Flyby looking straight out into the cosmos through zero atmosphere: every star burns with pure, un-twinkling piercing sharpness.",
        "stars burn with un-twinkling piercing brilliance through the collapsed atmosphere above frozen mountain summits",
        ANCHOR_SPACE,
    )

    # Group 2: The Subterranean Human Enclaves
    add_shot(
        "S45",
        "ch6_case_study_2",
        False,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "What became of human civilization? Survivors did not perish on the frozen surface; they migrated deep into geothermal subterranean megastructures.",
        "Cinematic interior view of an immense subterranean cavern illuminated by glowing warm amber LED lights and hydroponic gardens.",
        "Pushing in along underground city platforms built directly adjacent to deep volcanic geothermal steam conduits and magma chambers.",
        "human engineering platforms thrive inside deep geothermal caverns, powered by unlimited subterranean volcanic steam",
        ANCHOR_ABYSS,
    )
    add_shot(
        "S46",
        "ch6_case_study_2",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "Tapping unlimited geothermal heat and nuclear fission reactors, self-contained underground biospheres grow crops, recycle water, and maintain stable artificial human societies.",
        "Underground hydroponic agricultural towers glowing with vibrant purple and green grow-lights, producing lush food crops in abundance.",
        "Drifting past vertical habitat cylinders where millions of citizens live comfortably in climate-controlled environments beneath miles of rock.",
        "vertical hydroponic farming towers produce abundant green crops inside insulated climate-controlled cavern habitats",
        ANCHOR_ABYSS,
    )
    add_shot(
        "S47",
        "ch6_case_study_2",
        True,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Miles of solid granite rock and frozen surface ice above provide perfect insulation and complete shielding against dangerous cosmic radiation.",
        "Cross-section showing miles of protective bedrock, frozen oceans, and nitrogen glaciers separating the deep cities from vacuum above.",
        "Pushing in on the heavy airlocks and geothermal conduits anchoring human technology deep in the planetary mantle.",
        "massive titanium airlocks and geothermal conduits anchor subterranean human cities securely within the deep continental crust",
        ANCHOR_ABYSS,
    )
    add_shot(
        "S48",
        "ch6_case_study_2",
        True,
        0.55,
        "Grand parabolic space-probe flyby",
        "Humanity survives not as surface dwellers, but as planetary passengers riding inside a self-sustaining cosmic spaceship through the stellar ocean.",
        "Parabolic flyby pulling smoothly away from the surface of Earth into the grand majesty of deep interstellar space.",
        "Flyby revealing the solitary planet as an armored organic starship carrying the flame of intelligent life across the void.",
        "camera sweeps wide into deep interstellar space as solitary armored Earth cruises like a cosmic starship",
        ANCHOR_SPACE,
    )

    # ==========================================
    # CHAPTER 7: ch7_systemic_shift (S49..S56)
    # ==========================================
    # Group 1: The Abyssal Biosphere
    add_shot(
        "S49",
        "ch7_systemic_shift",
        False,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Meanwhile, in the deep liquid ocean trenches, the non-human biosphere thrives completely oblivious to the catastrophe on the surface above.",
        "Melodysheep abyssal cinematography: dark marine trench six miles deep, where giant hydrothermal chimneys tower like underwater spires.",
        "Pushing in on the volcanic chimney belching mineral-rich black hydrothermal fluids at three hundred degrees Celsius into the water.",
        "black smoker hydrothermal chimney vents superheated mineral-rich fluids into the dark warm abyssal trench water",
        ANCHOR_ABYSS,
    )
    add_shot(
        "S50",
        "ch7_systemic_shift",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "Here, life does not depend on sunlight: chemotrophic extremophile bacteria oxidize hydrogen sulfide and methane to synthesize organic energy directly.",
        "Macro optical push-in on thick white microbial mats coating the volcanic rock, pulsating with rich chemotrophic bacterial life.",
        "Drifting laterally past dense colonies of giant tube worms with vibrant crimson plumes waving rhythmically in the warm currents.",
        "giant tube worms with crimson plumes sway rhythmically in geothermal currents beside thriving white microbial mats",
        ANCHOR_ABYSS,
    )
    add_shot(
        "S51",
        "ch7_systemic_shift",
        True,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Blind crabs, ghost octopuses, and bioluminescent deep-sea predators continue their evolutionary dances, entirely unaffected by the vanishing of the Sun.",
        "Cinematic view of an ethereal translucent ghost octopus swimming gracefully above a field of hydrothermal vent chimneys.",
        "Pushing in as glowing bioluminescent pulses ripple across the creature’s mantle, illuminating the deep sea in electric cyan sparks.",
        "translucent ghost octopus glides gracefully through warm trench water, rippling with electric cyan bioluminescence",
        ANCHOR_ABYSS,
    )
    add_shot(
        "S52",
        "ch7_systemic_shift",
        True,
        0.44,
        "Grand parabolic space-probe flyby",
        "For these abyssal organisms, the Sun was never their God; Earth’s radioactive interior has always been their sole, eternal provider.",
        "Parabolic space-probe flyby cutting from the glowing underwater hydrothermal vent chimneys to the exterior frozen shell of the planet.",
        "Flyby contrasting the pitch-black exterior ice with the vibrant, warm hydrothermal life flourishing in perpetual warmth below.",
        "camera sweeps from the vibrant glowing hydrothermal vents to the silent frozen ice shell protecting the world above",
        ANCHOR_SPACE,
    )

    # Group 2: Earth as a Rogue Planet
    add_shot(
        "S53",
        "ch7_systemic_shift",
        False,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Astronomers estimate that our galaxy contains hundreds of billions of rogue planets: free-floating worlds drifting unbound between the distant stars.",
        "Melodysheep IMAX cosmic vista: wide view of the Milky Way spiral arm populated with dozens of dark rogue planet silhouettes.",
        "Pushing in on Earth as it joins this nomadic galactic fleet, cruising quietly through the Orion Arm of our galaxy.",
        "Earth glides peacefully through the starry dust lanes of the Orion Arm among billions of unseen nomadic rogue worlds",
        ANCHOR_SPACE,
    )
    add_shot(
        "S54",
        "ch7_systemic_shift",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "Liberated from solar orbital entrapment, Earth faces zero danger from the eventual solar red-giant phase that would otherwise incinerate it.",
        "Deep-space view looking back toward the distant location where the Sun once burned, now an empty pinpoint in the dark.",
        "Drifting alongside Earth as it glides past interstellar dust clouds and glowing pink reflection nebulae drifting through the void.",
        "camera drifts past glowing pink reflection nebulae as Earth travels safely outside the danger zone of stellar death",
        ANCHOR_SPACE,
    )
    add_shot(
        "S55",
        "ch7_systemic_shift",
        True,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Protected by its frozen shell and geothermal core, our world can wander through interstellar space for tens of billions of years.",
        "Cinematic portrait of Earth as a majestic frozen sphere reflecting the soft purple and gold light of distant star clusters.",
        "Pushing in toward the ice-crusted planet as its gravitational field captures interstellar dust and micrometeorites like cosmic passengers.",
        "frozen Earth sweeps through interstellar dust lanes, capturing faint cosmic particles within its gravitational sphere",
        ANCHOR_SPACE,
    )
    add_shot(
        "S56",
        "ch7_systemic_shift",
        True,
        0.55,
        "Grand parabolic space-probe flyby",
        "A planet that began as a delicate cradle under solar light has evolved into a nearly indestructible, eternal interstellar voyager.",
        "Grand parabolic flyby around Earth silhouetted against a magnificent sweeping panorama of the Andromeda galaxy and distant star clouds.",
        "Flyby gliding smoothly under the south celestial pole, capturing the quiet dignity of a world that refused to freeze into extinction.",
        "camera executes a majestic parabolic sweep around Earth framed against the colossal glowing swirl of the Andromeda galaxy",
        ANCHOR_SPACE,
    )

    # ==========================================
    # CHAPTER 8: ch8_resolution (S57..S64)
    # ==========================================
    # Group 1: The Destiny of Capture
    add_shot(
        "S57",
        "ch8_resolution",
        False,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Hundreds of millions of years in the future, Earth’s wandering trajectory will inevitably intersect the gravitational sphere of another star.",
        "Melodysheep IMAX cosmic sequence: a warm orange K-type dwarf star glowing softly in the distance of interstellar space.",
        "Pushing in as Earth glides into the outer gravitational perimeter of the new solar system, decelerating into a wide hyperbolic arc.",
        "Earth glides toward the warm golden glow of a new K-type dwarf star, entering its outer gravitational influence",
        ANCHOR_SPACE,
    )
    add_shot(
        "S58",
        "ch8_resolution",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "Gravitational interactions with a gas giant could bleed off excess velocity, settling Earth into a stable, warm new circular orbit.",
        "Orbital simulation showing Earth executing a three-body gravitational slingshot past a massive ringed gas giant planet.",
        "Drifting alongside Earth as the gravitational brake rounds its trajectory into a serene circular orbit around the golden host star.",
        "three-body gravitational interaction rounds Earth's trajectory into a serene circular orbit around the new star",
        ANCHOR_SPACE,
    )
    add_shot(
        "S59",
        "ch8_resolution",
        True,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "As new stellar warmth bathes the frozen planet, crystalline nitrogen snow sublimates back into gas, restoring a rich, dense, breathable atmosphere.",
        "Cinematic surface view of nitrogen glaciers sublimating into swirling white clouds under the gentle golden rays of the new star.",
        "Pushing in as crystalline ice crusts melt into rushing rivers of liquid water, flowing joyfully across ancient resurrected continents.",
        "glaciers sublimate into swirling clouds as sparkling liquid water begins flowing freely across thawed continental plains",
        ANCHOR_SURFACE_FROZEN,
    )
    add_shot(
        "S60",
        "ch8_resolution",
        True,
        0.44,
        "Grand parabolic space-probe flyby",
        "The mile-thick oceanic ice crust melts away, releasing the subterranean ocean and its resilient ecosystems back into the warm sunshine.",
        "Parabolic space-probe flyby over the thawing oceans as the global ice pack breaks apart into shimmering blue lagoons.",
        "Flyby revealing open liquid seas sparkling under the golden light of the second star, reborn after an eon of darkness.",
        "global ice sheets break apart into glittering blue lagoons, restoring open sparkling seas to the reborn planet",
        ANCHOR_EARTH_ORBIT,
    )

    # Group 2: The Cosmic Perspective
    add_shot(
        "S61",
        "ch8_resolution",
        False,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Humanity emerges from deep geothermal vaults, stepping once again onto green soil beneath the dawn of an entirely new sun.",
        "Cinematic surface view of a lush green hillside overlooking a tranquil ocean bay under the soft golden light of the new star.",
        "Pushing in past young flowering trees blooming in the warm breeze as human explorers look up toward the sky with reverence.",
        "camera pushes in past flowering green trees toward the sparkling shoreline as a gentle warm breeze ripples the water",
        ANCHOR_SURFACE_FROZEN,
    )
    add_shot(
        "S62",
        "ch8_resolution",
        True,
        0.33,
        "Zero-G lateral cosmic drift",
        "We are not merely fragile hitchhikers on a rock; life is a tenacious, self-preserving cosmic force capable of enduring stellar extinction.",
        "Melodysheep IMAX view looking out across the revitalized planet turning serenely in its new golden solar home.",
        "Drifting laterally as vibrant blue oceans and white fluffy clouds reflect brilliant light into the surrounding cosmos.",
        "camera drifts past the revitalized blue and green marble of Earth reflecting radiant starlight into deep space",
        ANCHOR_EARTH_ORBIT,
    )
    add_shot(
        "S63",
        "ch8_resolution",
        True,
        0.33,
        "Slow weightless orbital push-in toward terminator line",
        "Even if the Sun were extinguished this very second, the story of planet Earth does not conclude in silent, permanent death.",
        "Cinematic wide angle capturing Earth and its new companion star aligned in celestial harmony against the starry cosmos.",
        "Pushing in slowly on the glowing blue planet as its renewed atmosphere scatters brilliant electric-blue light across the void.",
        "Earth's rejuvenated atmosphere scatters electric blue light across space, vibrant and defiant against cosmic darkness",
        ANCHOR_EARTH_ORBIT,
    )
    add_shot(
        "S64",
        "ch8_resolution",
        True,
        0.55,
        "Grand parabolic space-probe flyby",
        "Our home world would journey through the dark, conquer the cosmic deep, and rise triumphant in the light of another dawn.",
        "Grand Melodysheep documentary finale flyby pulling smoothly back from Earth into the vast luminous expanse of the Milky Way.",
        "Sweeping into the infinite starry firmament as the glowing planet becomes a radiant star among stars, immortal and unconquered.",
        "camera executes a grand pull-back into deep interstellar space as Earth shines like a brilliant jewel in the Milky Way",
        ANCHOR_SPACE,
    )

    return shots


def get_short_shots() -> list[dict[str, Any]]:
    # 7 shots, 13-15 words per shot, CTA in S07
    shots = [
        {
            "shot_id": "S01",
            "scene_group": "G1",
            "continues_prev": False,
            "scene_anchor": ANCHOR_SPACE,
            "narration": "If the Sun vanished right now, Earth would not instantly plunge into darkness or freeze.",
            "pause_after_sec": 0.35,
            "camera_verb": "Grand parabolic space-probe flyby",
            "start_visual": "Melodysheep IMAX deep space view of the blazing Sun abruptly disappearing, leaving an empty gravitational ring in space, strictly zero text.",
            "end_visual": "Parabolic flyby past the empty solar coordinate into pitch-black void, strictly zero text.",
            "subject_motion": "blazing solar disc vanishes abruptly into absolute velvet blackness leaving empty space",
        },
        {
            "shot_id": "S02",
            "scene_group": "G1",
            "continues_prev": True,
            "scene_anchor": ANCHOR_SPACE,
            "narration": "For eight minutes and twenty seconds, we would orbit happily under bright borrowed sunlight.",
            "pause_after_sec": 0.35,
            "camera_verb": "Zero-G lateral cosmic drift",
            "start_visual": "Deep-space view looking across ninety-three million miles of vacuum toward planet Earth.",
            "end_visual": "Drifting alongside a vast beam of traveling solar photons streaming toward the blue planet, strictly zero text.",
            "subject_motion": "camera drifts beside traveling beam of sunlight racing across ninety-three million miles of vacuum",
        },
        {
            "shot_id": "S03",
            "scene_group": "G2",
            "continues_prev": False,
            "scene_anchor": ANCHOR_SPACE,
            "narration": "Photons and gravitational waves travel across spacetime at the exact same cosmic speed limit.",
            "pause_after_sec": 0.35,
            "camera_verb": "Slow weightless orbital push-in toward terminator line",
            "start_visual": "Spacetime fabric visualized as a glowing cyan coordinate grid rippling with concentric gravitational waves.",
            "end_visual": "Pushing in on the wave crests traveling in synchrony with the final boundary of light, strictly zero text.",
            "subject_motion": "concentric gravitational ripples expand outward across spacetime at the speed of light",
        },
        {
            "shot_id": "S04",
            "scene_group": "G2",
            "continues_prev": True,
            "scene_anchor": ANCHOR_SPACE,
            "narration": "Until that wave strikes, Earth feels the gravitational pull of a completely extinct star.",
            "pause_after_sec": 0.35,
            "camera_verb": "Grand parabolic space-probe flyby",
            "start_visual": "High-angle view of the solar system plane showing Earth tracing its normal curved Keplerian ellipse.",
            "end_visual": "Flyby as the planet continues curving in empty space, held by the receding wave, strictly zero text.",
            "subject_motion": "Earth continues its curved orbital path around the empty point until the wave arrives",
        },
        {
            "shot_id": "S05",
            "scene_group": "G3",
            "continues_prev": False,
            "scene_anchor": ANCHOR_EARTH_ORBIT,
            "narration": "At eight minutes twenty seconds, daylight snaps black and our orbital tether cleanly breaks.",
            "pause_after_sec": 0.35,
            "camera_verb": "Slow weightless orbital push-in toward terminator line",
            "start_visual": "Orbital perspective of daytime Earth as the sharp shadow border suddenly sweeps across continents.",
            "end_visual": "Pushing in as city electrical lights ignite against absolute pitch-black cosmic space, strictly zero text.",
            "subject_motion": "daylight instantly extinguishes across the planet, revealing glowing spiderwebs of city lights",
        },
        {
            "shot_id": "S06",
            "scene_group": "G3",
            "continues_prev": True,
            "scene_anchor": ANCHOR_SPACE,
            "narration": "Earth slingshots tangentially into deep space at thirty kilometers every second as a rogue.",
            "pause_after_sec": 0.35,
            "camera_verb": "Zero-G lateral cosmic drift",
            "start_visual": "Deep-space view as Earth's curved orbit snaps straight, releasing the dark planet into the void.",
            "end_visual": "Drifting alongside the dark planet as it streaks through the starry Milky Way, strictly zero text.",
            "subject_motion": "dark planet hurtles in a straight tangent line at thirty kilometers per second through space",
        },
        {
            "shot_id": "S07",
            "scene_group": "G4",
            "continues_prev": False,
            "scene_anchor": ANCHOR_SPACE,
            "narration": "Explore the complete chronological simulation of Earth's frozen survival in our full cosmic investigation.",
            "pause_after_sec": 0.35,
            "camera_verb": "Grand parabolic space-probe flyby",
            "start_visual": "Melodysheep IMAX view of frozen Earth drifting past brilliant starry nebulae in the void.",
            "end_visual": "Majestic pull-back flyby into the vast cosmic ocean as solitary Earth journeys into eternity, strictly zero text.",
            "subject_motion": "camera sweeps wide into deep interstellar space as solitary frozen Earth journeys into eternity",
        },
    ]
    return shots


def build_and_save() -> None:
    long_shots = get_long_shots()
    short_shots = get_short_shots()

    long_spec = {
        "job_id": "en-pocket-cosmos-batch1-16x9",
        "channel_slug": "en-pocket-cosmos",
        "aspect": "16:9",
        "title": "If the Sun Vanished Right Now: Hour-by-Hour Physics of Earth's Survival in Deep Space",
        "youtube_title": "What If the Sun Vanished Right Now?",
        "thumbnail_spec": {
            "visual_hook": "Deep-space wide shot of Earth half-frozen in electric cyan twilight drifting away from an empty gravitational ring",
            "allowed_text": "8 MINUTES LEFT",
            "overlay_card": False,
        },
        "voice": "en-US-ChristopherNeural",
        "shots": long_shots,
    }

    short_spec = {
        "job_id": "en-pocket-cosmos-batch1-9x16",
        "parent_long_id": "en-pocket-cosmos-batch1-16x9",
        "channel_slug": "en-pocket-cosmos",
        "aspect": "9:16",
        "title": "8 Minutes of Stolen Light: Why Earth Would Keep Orbiting an Empty Sky",
        "youtube_title": "8 Minutes Before Earth Freezes in Space",
        "thumbnail_spec": {
            "visual_hook": "IMAX deep space vista of solar system plane with vanishing solar orb and outward gravitational ripple wave toward Earth",
            "allowed_text": "STOLEN LIGHT",
            "overlay_card": False,
        },
        "voice": "en-US-ChristopherNeural",
        "shots": short_shots,
    }

    print("Validating en-pocket-cosmos Long...")
    validate_shots(long_shots, is_long=True)
    print("Validating en-pocket-cosmos Short...")
    validate_shots(short_shots, is_long=False)

    p_long = OUT_DIR / "en-pocket-cosmos_long_16x9.json"
    p_short = OUT_DIR / "en-pocket-cosmos_short_9x16.json"

    p_long.write_text(json.dumps(long_spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    p_short.write_text(json.dumps(short_spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved: {p_long} and {p_short}")


if __name__ == "__main__":
    build_and_save()
