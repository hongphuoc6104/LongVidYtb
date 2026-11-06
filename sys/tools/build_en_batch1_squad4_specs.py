#!/usr/bin/env python3
"""Generator for English Batch 1 (Channels 10–12) Stage A Specs for W-Prep-Squad-4.

Channels:
10. en-choke-point (RealLifeLore | en-US-ChristopherNeural)
    - Long 16:9:  en-choke-point-batch1-16x9
    - Short 9:16: en-choke-point-batch1-9x16
11. en-root-and-canopy (BBC Earth Green Planet | en-GB-RyanNeural)
    - Long 16:9:  en-root-and-canopy-batch1-16x9
    - Short 9:16: en-root-and-canopy-batch1-9x16
12. en-spawn-to-apex (Deep Look PBS | en-US-EricNeural)
    - Long 16:9:  en-spawn-to-apex-batch1-16x9
    - Short 9:16: en-spawn-to-apex-batch1-9x16
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[2]
SPECS_DIR = ROOT_DIR / "sys/channels/en_batch1_specs"
SPECS_DIR.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# CHANNEL 10: en-choke-point
# ==============================================================================
CH10_ANCHOR = (
    "RealLifeLore hyper-realistic 3D orbital satellite terrain and deep bathymetric navy ocean cinematography "
    "with blue atmospheric limb glow and golden vector highlights, unlabeled 3D satellite relief terrain, "
    "strictly zero map labels, zero words, zero letters, zero numbers, strictly zero text"
)

CH10_LONG_NARRATIONS = [
    # ch1_hook (S01..S08)
    "Fifty thousand cargo vessels cross open oceans right now, carrying six million steel containers packed with industrial goods and energy supplies.",
    "Yet nearly eighty percent of all globally traded maritime cargo must funnel through just five narrow geographic straits and canals.",
    "At the Strait of Hormuz, twenty-one million barrels of crude petroleum pass through daily toward major international industrial refineries and markets.",
    "That single aquatic corridor carries twenty percent of global petroleum consumption and one-third of all liquefied natural gas traded worldwide.",
    "If this passage closes for even forty-eight hours, international supply chains shudder and global manufacturing grinds toward a severe economic standstill.",
    "While the strait measures twenty-one miles across, the actual navigable deepwater channel is remarkably narrower than most people ever imagine.",
    "Giant supertankers drafting twenty meters cannot navigate the shallow coastal reefs on either side without risking immediate catastrophic hull grounding.",
    "Two miles of open water dictate the global price of gasoline, plastics, agricultural fertilizers, and modern industrial life across our world.",
    # ch2_paradox (S09..S16)
    "Modern ultra-large crude carriers are colossal engineering marvels stretching four hundred meters long and displacing more than three hundred thousand tons.",
    "These massive industrial vessels take nearly three nautical miles to come to a complete dead stop when cruising at normal speed.",
    "Yet their intercontinental journeys depend entirely on geographic corridors formed hundreds of millions of years ago by ancient continental tectonic collisions.",
    "No matter how advanced modern satellite navigation becomes, physical naval geography remains the ultimate dictator of international trade and maritime commerce.",
    "A container ship sailing from Shanghai to Rotterdam must pass through three distinct geographic pinches before safely reaching European destination ports.",
    "Each bottleneck compounds transit risk, forcing international logistics operators into tight convoy schedules that leave zero margin for operational error.",
    "A single mechanical steering failure or navigational drift can paralyze billions of dollars of synchronized cargo shipments within a few minutes.",
    "The fundamental paradox of twenty-first century hyper-globalization is its complete dependence on ancient, unforgiving, and politically contested oceanic choke points.",
    # ch3_mechanism (S17..S24)
    "Let us examine the hydrographic bathymetry of the Strait of Hormuz to understand why alternative commercial routes simply do not exist.",
    "The northern Iranian coastline rises abruptly into jagged mountain ranges, dropping steeply into deep submerged canyons favorable for hostile naval operations.",
    "Conversely, the southern waters bordering the Arabian Peninsula are scattered with shallow coral reefs, sandbars, and unpredictable treacherous tidal rip currents.",
    "This bathymetric asymmetry compresses all large commercial vessels into a tight, internationally managed Traffic Separation Scheme between small desert islands.",
    "Ships enter through one two-mile inbound corridor and exit through an identical two-mile outbound lane separated by a narrow buffer.",
    "Deviating outside these demarcated deepwater channels exposes multi-million-dollar hulls to dangerous shoals and unmapped shallow rocky formations along the coast.",
    "This geometric constraint transforms vast open ocean navigation into the maritime equivalent of a crowded two-lane mountain highway packed with traffic.",
    "Geography forces rival nations and commercial competitors into the exact same narrow aquatic corridor every single hour of every single day.",
    # ch4_case_study_1 (S25..S32)
    "Travel six thousand miles eastward to Southeast Asia, where an even more congested maritime bottleneck governs international global manufacturing and trade.",
    "The Strait of Malacca connects the Indian Ocean to the South China Sea, spanning five hundred miles between Sumatra and Malaysia.",
    "Over one hundred thousand commercial vessels transit this tropical corridor every year, carrying one-quarter of all globally traded maritime goods.",
    "Nearly eighty percent of China's imported crude oil must navigate this single stretch of water to reach mainland industrial manufacturing refineries.",
    "Near Singapore, at the Phillips Channel, the navigable waterway pinches to an astonishingly narrow one-point-five nautical miles in total width.",
    "Hundreds of massive container ships, bulk carriers, and fishing vessels crowd together, creating one of the densest shipping jams on Earth.",
    "A severe accident or deliberate naval blockade in the Phillips Channel would force ships to divert around remote Indonesian island passages.",
    "Diverting around the Sunda or Lombok Straits adds thousands of extra miles, draining millions in additional bunker fuel per single voyage.",
    # ch5_escalation (S33..S40)
    "The geopolitical leverage created by these narrow gateways has transformed them into prime arenas for modern asymmetric grey-zone naval warfare.",
    "Small, high-speed patrol craft armed with anti-ship missiles can harass commercial freighters without triggering full conventional naval confrontations between powers.",
    "Inexpensive naval sea mines deployed in shallow waters can shut down an entire strait before specialized minesweepers can clear safe passages.",
    "Commercial maritime underwriters monitor these risks constantly through satellite tracking, calculating insurance risk premiums in real time across the globe.",
    "When regional tensions escalate, war-risk insurance premiums for commercial vessels transiting Hormuz can multiply fivefold within twenty-four hours of notice.",
    "Shipowners must pass these explosive insurance costs directly onto charterers, driving up freight rates across every major international trading route.",
    "Consequently, consumers thousands of miles away experience price spikes at fuel pumps and grocery checkout counters almost immediately after incidents occur.",
    "You do not need to sink a supertanker to disrupt world trade; financial insurance algorithms do it automatically and ruthlessly worldwide.",
    # ch6_case_study_2 (S41..S48)
    "Consider the Bab-el-Mandeb Strait, the critical gateway connecting the Gulf of Aden to the Red Sea and the Suez Canal.",
    "Measuring eighteen miles across, it funnels twelve percent of world trade moving between Asian industrial factories and European consumer retail markets.",
    "When regional conflicts erupted along the Yemeni coastline, commercial container fleets quickly abandoned the Red Sea transit corridor altogether for safety.",
    "Major container liners redirected their megaships around the southern tip of the African continent via the stormy Cape of Good Hope.",
    "This alternate oceanic route adds three thousand five hundred nautical miles and ten to fourteen additional sailing days per single voyage.",
    "Burning hundreds of additional metric tons of bunker fuel per vessel added billions of dollars in global logistics operating supply costs.",
    "European retailers faced sudden inventory delays, empty warehouse shelves, and inflated shipping container tariffs across countless essential consumer product categories.",
    "The Red Sea crisis demonstrated how fragile modern supply networks remain when ancient waterways become contested zones during international geopolitical tensions.",
    # ch7_systemic_shift (S49..S56)
    "In response to these persistent vulnerabilities, major industrialized economies have invested hundreds of billions attempting to build terrestrial overland bypasses.",
    "Saudi Arabia constructed the East-West crude pipeline to transport petroleum directly across the desert to the Red Sea port of Yanbu.",
    "The United Arab Emirates built the Habshan-Fujairah pipeline, delivering one-point-five million barrels daily directly to the Gulf of Oman coastline.",
    "Yet these overland pipelines can transport only a fraction of the twenty-one million barrels moving through Hormuz every single day.",
    "China has financed railway corridors and deepwater port projects through Pakistan and Myanmar to diminish its strategic reliance on Malacca transit.",
    "Proposals to dredge a shipping canal across Thailand's Kra Isthmus have lingered for centuries without achieving financial or political engineering feasibility.",
    "The physical reality remains inescapable: nothing on land matches the immense capacity and cost efficiency of maritime container shipping across oceans.",
    "Terrestrial infrastructure can cushion temporary shocks, but it cannot replace the colossal scale of global ocean shipping lanes across our planet.",
    # ch8_resolution (S57..S64)
    "As geopolitical competition intensifies across the twenty-first century, control over maritime choke points will define national power and economic sovereignty.",
    "Nations bordering these aquatic pinch points possess asymmetric leverage far exceeding their conventional economic output or military armed troop size.",
    "Every consumer electronic device, pharmaceutical ingredient, and automotive part you purchase has crossed at least one of these narrow oceanic corridors.",
    "The globalized economy operates like a vast circulatory system, pumping lifeblood resources through a handful of narrow, highly vulnerable geographic valves.",
    "Ensuring freedom of navigation across these straits requires immense naval deterrence, international diplomatic treaties, and delicate bilateral balance among superpowers.",
    "A single miscalculation, stray naval drone, or closed maritime channel can trigger cascading inflationary shockwaves across entire world financial markets.",
    "Next time you check the price of fuel or everyday consumer goods, remember the twenty-one miles that govern global trade.",
    "In an interconnected world, true geopolitical power belongs to whoever commands the world's most vulnerable ocean gateways and shipping corridors.",
]

for idx, s in enumerate(CH10_LONG_NARRATIONS, 1):
    cnt = len(s.split())
    assert 20 <= cnt <= 23, f"CH10 Long S{idx:02d} word count {cnt} outside 20-23: '{s}'"

CH10_CAMERAS = [
    "orbital satellite-to-strait zoom descent",
    "smooth lateral 3D relief map flight",
    "low-horizon naval corridor pass",
    "sweeping 3D cartographic orbital arc",
]

CH10_CHAPTER_NAMES = [
    "ch1_hook", "ch2_paradox", "ch3_mechanism", "ch4_case_study_1",
    "ch5_escalation", "ch6_case_study_2", "ch7_systemic_shift", "ch8_resolution"
]


def build_choke_point_long() -> Dict[str, Any]:
    shots = []
    for i in range(64):
        ch_idx = i // 8
        ch_name = CH10_CHAPTER_NAMES[ch_idx]
        is_opening = (i % 4 == 0)
        shot_id = f"S{i+1:02d}"
        cam = CH10_CAMERAS[i % 4]
        is_chapter_end = (i % 8 == 7)
        pause = 0.55 if is_chapter_end else 0.36

        start_vis = (
            f"RealLifeLore 8K orbital satellite perspective of maritime corridor for {ch_name} shot {shot_id}: "
            f"photorealistic 3D terrain relief and deep navy ocean bathymetry showing strategic water passes, "
            f"illuminated golden maritime shipping vectors gliding smoothly across water surfaces, "
            f"high-altitude atmospheric limb glow, photorealistic satellite cartography, strictly zero map labels, "
            f"zero words, zero letters, zero numbers, strictly zero text."
        )
        end_vis = (
            f"Continuing on the same orbital satellite view for {ch_name} shot {shot_id}: camera glides along the water corridor "
            f"as golden maritime vessel tracks concentrate into dense luminous ribbons through narrow strait bottlenecks, "
            f"deep ocean bathymetry, photorealistic cartography, strictly zero map labels, zero words, zero letters, "
            f"zero numbers, strictly zero text."
        )
        motion = (
            f"camera executes {cam} over the 3D maritime corridor as golden shipping vectors drift smoothly "
            f"through the narrow ocean passage"
        )

        shot_dict = {
            "shot_id": shot_id,
            "scene_group": ch_name,
            "continues_prev": not is_opening,
            "scene_anchor": CH10_ANCHOR,
            "narration": CH10_LONG_NARRATIONS[i],
            "pause_after_sec": pause,
            "camera_verb": cam,
            "start_visual": start_vis,
            "end_visual": end_vis,
            "subject_motion": motion,
            "speech_rate": "+0%",
        }
        shots.append(shot_dict)

    return {
        "job_id": "en-choke-point-batch1-16x9",
        "channel_slug": "en-choke-point",
        "aspect": "16:9",
        "title": "21 Miles of Leverage: Why the Strait of Hormuz & Malacca Dictate the Price of Everything You Buy",
        "youtube_title": "Why One Narrow Strait Controls Global Prices",
        "thumbnail_spec": {
            "visual_hook": "Orbital satellite relief map of the Strait of Hormuz with glowing amber shipping lanes pinched into a 2-mile bottleneck",
            "allowed_text": "21-MILE CHOKEHOLD",
            "overlay_card": False,
        },
        "voice": "en-US-ChristopherNeural",
        "shots": shots,
    }


CH10_SHORT_NARRATIONS = [
    "Twenty-one million barrels of petroleum pass through the Strait of Hormuz every day.",  # 13 words
    "Yet the actual navigable deepwater shipping channel is barely two miles wide in total.",  # 14 words
    "Giant supertankers drafting twenty meters cannot divert into shallower waters without running aground.",  # 13 words
    "If one ship sinks or detonates a naval mine, insurance rates surge fivefold.",  # 13 words
    "Global energy markets would instantly lose one-fifth of daily worldwide crude petroleum supply.",  # 13 words
    "Fuel pumps and consumer shipping prices across the globe would spike within days.",  # 13 words
    "Watch our full documentary for the complete geopolitical breakdown of these vital waterways.",  # 13 words
]

for idx, s in enumerate(CH10_SHORT_NARRATIONS, 1):
    cnt = len(s.split())
    assert 13 <= cnt <= 15, f"CH10 Short S{idx:02d} count {cnt} outside 13-15: '{s}'"


def build_choke_point_short() -> Dict[str, Any]:
    shots = [
        {
            "shot_id": "S01",
            "scene_group": "sg1_hook",
            "continues_prev": False,
            "scene_anchor": CH10_ANCHOR,
            "narration": CH10_SHORT_NARRATIONS[0],
            "pause_after_sec": 0.32,
            "camera_verb": "orbital satellite-to-strait zoom descent",
            "start_visual": "RealLifeLore 8K orbital satellite perspective looking down from high Earth orbit: dark navy ocean waters of the Persian Gulf converging into the narrow Strait of Hormuz, with luminous golden maritime vector lines tracing ship lanes across the water, photorealistic satellite relief, strictly zero map labels, zero words, zero letters, zero numbers, strictly zero text.",
            "end_visual": "On the same orbital satellite view of Hormuz, golden maritime stream particles compress into a dense luminous ribbon entering the strait, photorealistic satellite relief, strictly zero text.",
            "subject_motion": "camera descends from high Earth orbit toward the Strait of Hormuz as golden maritime trade particles drift through the ocean corridor",
            "speech_rate": "+2%",
        },
        {
            "shot_id": "S02",
            "scene_group": "sg1_hook",
            "continues_prev": True,
            "scene_anchor": CH10_ANCHOR,
            "narration": CH10_SHORT_NARRATIONS[1],
            "pause_after_sec": 0.34,
            "camera_verb": "smooth lateral 3D relief map flight",
            "start_visual": "High-contrast 3D orbital relief flight over the turquoise waters of the Strait of Hormuz, revealing shallow coral reefs on both sides and a narrow deep navy blue navigation corridor, photorealistic cartography, strictly zero text.",
            "end_visual": "Along the same 3D corridor, glowing amber lane boundaries illuminate the exact two-mile shipping channel between the rocky coastline and shallow reefs, strictly zero text.",
            "subject_motion": "camera glides smoothly along the 3D relief corridor as amber navigational boundary lines illuminate the narrow channel",
            "speech_rate": "+2%",
        },
        {
            "shot_id": "S03",
            "scene_group": "sg2_mechanism",
            "continues_prev": False,
            "scene_anchor": "Cinematic low-horizon naval view of a massive 300,000-ton crude oil supertanker cutting through deep ocean swells, foaming white bow wash, strictly zero text, zero logos",
            "narration": CH10_SHORT_NARRATIONS[2],
            "pause_after_sec": 0.32,
            "camera_verb": "low-horizon naval corridor pass",
            "start_visual": "Cinematic low-horizon naval view of a massive 300,000-ton red and black crude oil supertanker cutting through deep ocean swells, foaming white bow wash, strictly zero text, zero logos.",
            "end_visual": "Low-angle shot on the same supertanker as a hydrographic wireframe cross-section reveals its massive twenty-meter submerged hull passing closely above shallow seabed contours, strictly zero text.",
            "subject_motion": "the colossal oil tanker glides through ocean swells as foaming white water breaks along its bulbous bow",
            "speech_rate": "+2%",
        },
        {
            "shot_id": "S04",
            "scene_group": "sg2_mechanism",
            "continues_prev": True,
            "scene_anchor": "Cinematic low-horizon naval view of a massive 300,000-ton crude oil supertanker cutting through deep ocean swells, foaming white bow wash, strictly zero text, zero logos",
            "narration": CH10_SHORT_NARRATIONS[3],
            "pause_after_sec": 0.35,
            "camera_verb": "sweeping 3D cartographic orbital arc",
            "start_visual": "Dramatic cinematic 3D cartographic view over the Strait of Hormuz where a pulsing amber warning beacon radiates across the maritime corridor, strictly zero text.",
            "end_visual": "On the same cartographic map, glowing red risk radius rings expand outward across the Persian Gulf, halting nearby tanker vectors, strictly zero text.",
            "subject_motion": "concentric glowing red risk rings pulse outward across the strait as maritime traffic vectors halt in place",
            "speech_rate": "+2%",
        },
        {
            "shot_id": "S05",
            "scene_group": "sg3_impact",
            "continues_prev": False,
            "scene_anchor": CH10_ANCHOR,
            "narration": CH10_SHORT_NARRATIONS[4],
            "pause_after_sec": 0.32,
            "camera_verb": "high-altitude nautical tracking drift",
            "start_visual": "Photorealistic high-contrast data visualization of the world globe with glowing gold oil pipelines and shipping corridors across the Middle East, strictly zero text.",
            "end_visual": "On the same global visualization, the glowing Middle Eastern arterial node pulses urgently with crimson alert hues, strictly zero text.",
            "subject_motion": "the global trade network pulses with luminous golden data streams as the central Middle Eastern node flares red",
            "speech_rate": "+2%",
        },
        {
            "shot_id": "S06",
            "scene_group": "sg3_impact",
            "continues_prev": True,
            "scene_anchor": "Cinematic twilight view of a bustling container terminal with towering cranes and glowing amber port lighting against dark ocean waters, strictly zero text, zero logos",
            "narration": CH10_SHORT_NARRATIONS[5],
            "pause_after_sec": 0.34,
            "camera_verb": "low-horizon naval corridor pass",
            "start_visual": "Cinematic twilight view of a bustling container terminal with towering cranes and glowing amber port lighting against dark ocean waters, strictly zero text, zero logos.",
            "end_visual": "On the same container terminal, automated crane lights sweep across thousands of stacked colorful shipping containers under misty skies, strictly zero text.",
            "subject_motion": "towering container cranes pivot smoothly under twilight lighting as dockside beacons reflect on calm water",
            "speech_rate": "+2%",
        },
        {
            "shot_id": "S07",
            "scene_group": "sg4_cta",
            "continues_prev": False,
            "scene_anchor": CH10_ANCHOR,
            "narration": CH10_SHORT_NARRATIONS[6],
            "pause_after_sec": 0.36,
            "camera_verb": "majestic high-orbit slow push-in",
            "start_visual": "Breathtaking high-orbit view of Earth from space along the twilight terminator line, golden trade corridors glowing peacefully across dark oceans, cinematic IMAX realism, strictly zero text.",
            "end_visual": "On the same planetary view, sunlight flares gently across Earth's curved limb as global maritime shipping lanes glow in quiet harmony, strictly zero text.",
            "subject_motion": "camera glides forward in high orbit as golden sunbeams flare along Earth's atmospheric limb",
            "speech_rate": "+2%",
        },
    ]

    return {
        "job_id": "en-choke-point-batch1-9x16",
        "channel_slug": "en-choke-point",
        "aspect": "9:16",
        "parent_long_id": "en-choke-point-batch1-16x9",
        "title": "The Two-Mile Shipping Lane: What Happens if One Tanker Blocks the Strait of Hormuz",
        "youtube_title": "The 2-Mile Lane Holding Oil Hostage",
        "voice": "en-US-ChristopherNeural",
        "shots": shots,
    }


# ==============================================================================
# CHANNEL 11: en-root-and-canopy
# ==============================================================================
CH11_ANCHOR = (
    "BBC Earth Green Planet optical macro botany cinematography with rich damp soil and emerald cellular textures, "
    "shallow depth of field, and golden volumetric forest rim lighting, strictly zero text"
)

CH11_LONG_NARRATIONS = [
    # ch1_hook (S01..S08)
    "One hundred and fifty feet above the damp rainforest floor, a fruit-eating hornbill perches quietly on an ancient ironwood branch.",
    "Among the bird's droppings rests a microscopic strangler fig seed, coated sticky with protective mucilage and barely two millimeters wide.",
    "It lodges inside a moist crevice of moss and organic leaf mulch collecting between the host tree's towering primary limbs.",
    "High above the dim understory, bathed in intense equatorial sunlight, the tiny seed absorbs moisture and begins its two-century siege.",
    "Unlike ordinary rainforest trees that fight for sunlight from the dark ground up, the strangler begins its life in reverse.",
    "It germinates as an epiphyte, an aerial tenant living harmlessly upon the bark without extracting a single drop of host sap.",
    "Delicate green cotyledon leaves unfurl toward the sky, but beneath them, a pale subterranean root begins a perilous journey downward.",
    "That gossamer pioneer root must navigate one hundred and fifty feet of vertical bark before finding life-saving mineral soil below.",
    # ch2_paradox (S09..S16)
    "Parasitic plants like mistletoe pierce directly into their host's vascular tissues with microscopic intrusive suckers known to botanists as haustoria.",
    "But the strangler fig is not a true physiological parasite; it never steals water or synthesized sugars from host cells.",
    "It receives zero nutrients directly from the massive living ironwood tree upon whose towering wooden shoulders it silently and harmlessly perches.",
    "Instead, it relies exclusively on aerial moisture, rainwater trickling along the bark, and minute traces of decaying leaf litter above.",
    "If the strangler does not extract food or drink from its host, why does the host inevitably perish over time?",
    "The botanical paradox lies not in chemical theft, but in a slow, relentless architectural encirclement that spans entire human generations.",
    "The fig tree does not poison its benefactor; it simply constructs a living wooden prison that tightens year after year.",
    "It is a ruthless evolutionary execution conducted in absolute botanical silence, where physical support slowly becomes a lethal structural cage.",
    # ch3_mechanism (S17..S24)
    "For decades, the strangler fig exists as a fragile aerial thread, sending downward thin adventitious roots that hug the trunk.",
    "These roots crawl millimeter by millimeter down the vertical fissures of bark, producing adhesive hairs that grip the furrowed surface.",
    "They endure tropical droughts, hungry tree snails, and destructive canopy storms, surviving purely on atmospheric humidity and morning dew condensation.",
    "At this early epiphytic stage, the strangler grows with painstaking slowness because canopy mulch contains almost no vital soil minerals.",
    "Decades pass quietly as multiple aerial filaments slowly weave downward, dividing and creeping like slow-motion botanical vines across the bark.",
    "Yet the precise moment the pioneer root tip penetrates the damp leaf litter of the forest floor, everything changes overnight.",
    "Cellular sensors in the root cap detect rich reserves of nitrogen, phosphorus, and groundwater locked within the dark tropical soil.",
    "An explosive surge of rich subterranean nutrients flows upward through the xylem, dramatically supercharging the fig's dormant biological growth rate.",
    # ch4_case_study_1 (S25..S32)
    "With direct access to subterranean soil minerals, the thin aerial roots swell rapidly into thick, muscular columns of fibrous wood.",
    "The fig now pumps massive quantities of groundwater upward to its crown, which expands aggressively through the upper jungle canopy.",
    "Additional muscular adventitious roots cascade from higher branches, wrapping tightly around the host tree's trunk like heavy braided hemp ropes.",
    "When these expanding roots press tightly against one another, a remarkable botanical phenomenon known as root anastomosis begins to occur.",
    "The outer bark of adjoining roots rubs away under pressure, allowing living cambium layers to touch and merge together seamlessly.",
    "Vascular cells fuse together permanently, transforming dozens of separate dangling roots into an interconnected, rigid lattice cage around the host.",
    "This self-welding wooden cylinder gradually wraps the host trunk in an unyielding, steadily tightening corset of dense, high-strength tropical hardwood.",
    "What originally began as delicate airborne tendrils has now fully crystallized into an impenetrable structural tomb of fused botanical hardwood.",
    # ch5_escalation (S33..S40)
    "As the underground root system matures, the critical botanical battle shifts from the dim forest understory to the radiant canopy above.",
    "Fueled by limitless soil nutrients, the strangler fig produces enormous glossy leaves, forming a dense crown directly over the host.",
    "The ancient rainforest giant, which took three centuries to claim its place in the sun, is suddenly cast in shadow.",
    "Its photosynthetic output plummets dramatically as vital sunlight is intercepted by the fig's sprawling, umbrella-like canopy of dark green foliage.",
    "Deprived of direct sunlight, the host tree cannot produce sufficient glucose to maintain its massive cellular respiration and complex defense systems.",
    "Meanwhile, hundreds of feet below in the subterranean soil, the fig's roots aggressively invade and plunder the host tree's root zone.",
    "The strangler absorbs moisture and phosphorus before they can reach the host tree's deeper taproots, starving it of vital hydration.",
    "Stripped of sunlight above and completely robbed of groundwater below, the ancient forest monarch begins its terminal and irreversible physical decline.",
    # ch6_case_study_2 (S41..S48)
    "The definitive physical choke, however, occurs through the relentless, crushing mechanics of secondary plant growth along the heavily encaged trunk.",
    "Every growing season, a healthy forest tree expands radially outward, laying down new rings of vascular xylem and phloem tissue.",
    "Yet the ironwood cannot expand radially; the strangler fig's rigid fused root lattice forms an unyielding, impenetrable external wooden girdle.",
    "As the host tries to grow outward, immense mechanical pressure builds against the inner surface of the strangler's wooden cage.",
    "This crushing inward pressure pinches the host tree's delicate phloem vessels, the microscopic pipelines that transport sugar from leaves downward.",
    "Carbohydrates back up in the canopy while the host's root system starves, accelerating fungal rot within the subterranean root zone.",
    "Eventually, water transport through the crushed xylem fails entirely, and the massive host tree sheds its remaining brittle canopy branches.",
    "The massive host tree eventually dies standing upright, completely encased within the living wooden armor of its patient botanical executioner.",
    # ch7_systemic_shift (S49..S56)
    "With the death of the host tree, a new ecological phase begins inside the dark interior of the wooden cylinder.",
    "Moisture-loving fungi, voracious wood-boring beetle larvae, and millions of subterranean termites rapidly invade the dead ironwood trunk from all sides.",
    "Over several decades, decomposers thoroughly consume the dead host tree from the inside out, turning solid hardwood into rich organic humus.",
    "Rain washes the nutrient-rich decomposed dust downward, continuously fertilizing the strangler's own interior roots that line the hollow central column.",
    "What remains standing is an architectural miracle: a colossal, hollow cylinder of woven fig roots standing completely on its own.",
    "The strangler fig has replaced the host entirely, holding up its sprawling canopy without needing a single internal wooden support.",
    "Its fused root lattice is engineered by natural selection to withstand severe hurricane winds, flexing resiliently like an organic botanical tower.",
    "Where a solid three-hundred-ton forest giant once stood, a soaring hollow living cathedral now quietly commands the ancient tropical jungle.",
    # ch8_resolution (S57..S64)
    "But in the broader ecology of the rainforest, the strangler fig transforms from lethal competitor into an indispensable keystone species.",
    "Unlike seasonal rainforest trees that fruit in synchronized rhythms, strangler figs produce massive fruit crops asynchronously throughout the entire year.",
    "When general forest trees drop no fruit during equatorial dry seasons, fig trees provide the sole survival food for wildlife.",
    "Hundreds of diverse species of monkeys, toucans, fruit bats, and insects congregate in the fig's crown, preventing widespread forest starvation.",
    "The hollow central cylinder of fused roots becomes a vertical apartment complex, sheltering roosting bats, owls, tree frogs, and wild bees.",
    "What began as a ruthless two-hundred-year siege ends as the most biologically productive living structure in the entire jungle canopy.",
    "Next time you walk through an ancient forest, look up into the branches and remember the patient seed resting above.",
    "In nature's longest war, life and death are never opposites; they are essential partners in sculpting the ancient living forest.",
]

for idx, s in enumerate(CH11_LONG_NARRATIONS, 1):
    cnt = len(s.split())
    assert 20 <= cnt <= 23, f"CH11 Long S{idx:02d} word count {cnt} outside 20-23: '{s}'"

CH11_CAMERAS = [
    "subterranean-to-canopy vertical probe crane",
    "optical macro botanical dolly push-in",
    "gentle forest floor tracking glide",
    "canopy top-down spiral descent",
]


def build_root_and_canopy_long() -> Dict[str, Any]:
    shots = []
    for i in range(64):
        ch_idx = i // 8
        ch_name = CH10_CHAPTER_NAMES[ch_idx]
        is_opening = (i % 4 == 0)
        shot_id = f"S{i+1:02d}"
        cam = CH11_CAMERAS[i % 4]
        is_chapter_end = (i % 8 == 7)
        pause = 0.55 if is_chapter_end else 0.36

        start_vis = (
            f"BBC Earth Green Planet macro documentary cinematography for {ch_name} shot {shot_id}: "
            f"deep damp rainforest botany showing ancient textured bark, lush velvet emerald moss, "
            f"delicate root tendrils curling with organic turgor motion, warm volumetric sunbeams piercing misty canopy air, "
            f"crystal dewdrops on foliage, authentic optical macro f/2.8, strictly zero text."
        )
        end_vis = (
            f"Continuing on the same optical macro botanical view for {ch_name} shot {shot_id}: "
            f"strangler fig root structures expand across the textured host bark as warm golden sunlight grazes "
            f"fused cambium layers and rich damp moss, photorealistic BBC nature cinematography, strictly zero text."
        )
        motion = (
            f"camera executes {cam} along the vertical botanical trunk as moisture droplets glisten "
            f"and delicate root tendrils expand across bark fissures"
        )

        shot_dict = {
            "shot_id": shot_id,
            "scene_group": ch_name,
            "continues_prev": not is_opening,
            "scene_anchor": CH11_ANCHOR,
            "narration": CH11_LONG_NARRATIONS[i],
            "pause_after_sec": pause,
            "camera_verb": cam,
            "start_visual": start_vis,
            "end_visual": end_vis,
            "subject_motion": motion,
            "speech_rate": "+0%",
        }
        shots.append(shot_dict)

    return {
        "job_id": "en-root-and-canopy-batch1-16x9",
        "channel_slug": "en-root-and-canopy",
        "aspect": "16:9",
        "title": "200-Year Siege: How a Single Strangler Fig Seed Slowly Devours a Rainforest Giant",
        "youtube_title": "How a Strangler Fig Devours a Giant Tree",
        "thumbnail_spec": {
            "visual_hook": "Botanical cross-section of a hollow rainforest host trunk encased by a lattice cage of strangler fig roots",
            "allowed_text": "200-YEAR SIEGE",
            "overlay_card": False,
        },
        "voice": "en-GB-RyanNeural",
        "shots": shots,
    }


CH11_SHORT_NARRATIONS = [
    "When an ancient forest giant nears death, it does not hoard its resources.",  # 13 words
    "Deep underground, fungal mycorrhizal networks link ancient mother trees directly to young saplings.",  # 13 words
    "In its final months, the dying tree releases massive pulses of stored carbon.",  # 13 words
    "Tracer experiments prove these nutrients flow preferentially toward the tree's closest genetic descendants.",  # 13 words
    "The fungal mycelium acts like a living neural internet across entire ancient forests.",  # 13 words
    "Even after falling, the decaying nurse log shields new seedlings for two centuries.",  # 13 words
    "Watch our full documentary to explore the secret life and architecture of trees.",  # 13 words
]

for idx, s in enumerate(CH11_SHORT_NARRATIONS, 1):
    cnt = len(s.split())
    assert 13 <= cnt <= 15, f"CH11 Short S{idx:02d} count {cnt} outside 13-15: '{s}'"


def build_root_and_canopy_short() -> Dict[str, Any]:
    shots = [
        {
            "shot_id": "S01",
            "scene_group": "sg1_hook",
            "continues_prev": False,
            "scene_anchor": CH11_ANCHOR,
            "narration": CH11_SHORT_NARRATIONS[0],
            "pause_after_sec": 0.32,
            "camera_verb": "gentle forest floor tracking glide",
            "start_visual": "BBC Earth Green Planet macro documentary cinematography: ancient gnarled oak tree trunk in deep damp woodland, emerald moss clinging to bark, morning mist drifting through sunbeams, strictly zero text.",
            "end_visual": "On the same mossy trunk, golden morning sunlight grazes the furrowed bark as dewdrops glisten on velvety lichen, strictly zero text.",
            "subject_motion": "morning mist drifts gently through sunbeams grazing the moss-covered trunk of the ancient forest giant",
            "speech_rate": "+2%",
        },
        {
            "shot_id": "S02",
            "scene_group": "sg1_hook",
            "continues_prev": True,
            "scene_anchor": CH11_ANCHOR,
            "narration": CH11_SHORT_NARRATIONS[1],
            "pause_after_sec": 0.34,
            "camera_verb": "subterranean-to-canopy vertical probe crane",
            "start_visual": "Subterranean cross-section of damp rich forest soil showing thick ancient tree roots interlaced with glowing pale-white mycorrhizal fungal threads, glistening moisture droplets, optical macro, strictly zero text.",
            "end_visual": "Inside the same subterranean soil cross-section, camera glides along the fungal hyphae as faint luminous amber pulses begin flowing between root tips, strictly zero text.",
            "subject_motion": "camera glides through damp subterranean soil as delicate fungal hyphae pulse with glowing amber nutrients",
            "speech_rate": "+2%",
        },
        {
            "shot_id": "S03",
            "scene_group": "sg2_mechanism",
            "continues_prev": False,
            "scene_anchor": CH11_ANCHOR,
            "narration": CH11_SHORT_NARRATIONS[2],
            "pause_after_sec": 0.32,
            "camera_verb": "optical macro botanical dolly push-in",
            "start_visual": "Extreme probe-lens macro at f/2.8 inside damp humus: fibrous root tips surrounded by glowing bioluminescent amber nutrient spheres flowing into fungal pathways, strictly zero text.",
            "end_visual": "On the same root junction, glowing amber carbon streams accelerate through the branching fungal network toward distant roots, strictly zero text.",
            "subject_motion": "luminous amber nutrient streams flow steadily through microscopic fungal hyphae branching through dark soil",
            "speech_rate": "+2%",
        },
        {
            "shot_id": "S04",
            "scene_group": "sg2_mechanism",
            "continues_prev": True,
            "scene_anchor": CH11_ANCHOR,
            "narration": CH11_SHORT_NARRATIONS[3],
            "pause_after_sec": 0.34,
            "camera_verb": "subterranean-to-canopy vertical probe crane",
            "start_visual": "Split cross-section showing forest floor above with young saplings in moss and glowing nutrient hyphae connecting directly to their roots below, strictly zero text.",
            "end_visual": "On the same split view, amber light pulses intensify as they reach the delicate roots of the youngest sapling, strictly zero text.",
            "subject_motion": "luminous nutrient pulses travel along fungal threads and illuminate the tender root system of a young sapling",
            "speech_rate": "+2%",
        },
        {
            "shot_id": "S05",
            "scene_group": "sg3_impact",
            "continues_prev": False,
            "scene_anchor": CH11_ANCHOR,
            "narration": CH11_SHORT_NARRATIONS[4],
            "pause_after_sec": 0.32,
            "camera_verb": "optical macro botanical dolly push-in",
            "start_visual": "3D subterranean visualization: thousands of branching white fungal threads forming a vast luminous network through dark forest earth, strictly zero text.",
            "end_visual": "On the same network view, waves of bioluminescent amber and turquoise light ripple through interconnected fungal nodes, strictly zero text.",
            "subject_motion": "waves of bioluminescent light ripple through the vast interconnected subterranean mycelial network",
            "speech_rate": "+2%",
        },
        {
            "shot_id": "S06",
            "scene_group": "sg3_impact",
            "continues_prev": True,
            "scene_anchor": CH11_ANCHOR,
            "narration": CH11_SHORT_NARRATIONS[5],
            "pause_after_sec": 0.34,
            "camera_verb": "gentle forest floor tracking glide",
            "start_visual": "Forest floor macro view of a fallen moss-covered nurse log, tiny vibrant green fern fiddleheads and saplings growing out of decomposing wood, strictly zero text.",
            "end_visual": "On the same nurse log, warm sunlight filters through canopy mist, illuminating delicate green seedling leaves unfurling from rich humus, strictly zero text.",
            "subject_motion": "canopy mist swirls gently over the mossy nurse log as sunlight illuminates unfurling green seedling leaves",
            "speech_rate": "+2%",
        },
        {
            "shot_id": "S07",
            "scene_group": "sg4_cta",
            "continues_prev": False,
            "scene_anchor": CH11_ANCHOR,
            "narration": CH11_SHORT_NARRATIONS[6],
            "pause_after_sec": 0.36,
            "camera_verb": "subterranean-to-canopy vertical probe crane",
            "start_visual": "Majestic upward canopy view looking through towering rainforest trees toward sunlit emerald leaves swaying in gentle breeze, golden sunbeams streaming downward, strictly zero text.",
            "end_visual": "On the same canopy perspective, the camera cranes gently upward toward the radiant blue sky through golden sunlit foliage, strictly zero text.",
            "subject_motion": "camera cranes upward through the towering canopy as golden sunbeams stream through swaying emerald leaves",
            "speech_rate": "+2%",
        },
    ]

    return {
        "job_id": "en-root-and-canopy-batch1-9x16",
        "channel_slug": "en-root-and-canopy",
        "aspect": "9:16",
        "parent_long_id": "en-root-and-canopy-batch1-16x9",
        "title": "The Wood-Wide Web: How Dying Forest Giants Pump Carbon to Their Own Offspring",
        "youtube_title": "How Dying Trees Feed Their Own Offspring",
        "voice": "en-GB-RyanNeural",
        "shots": shots,
    }


# ==============================================================================
# CHANNEL 12: en-spawn-to-apex
# ==============================================================================
CH12_ANCHOR = (
    "Deep Look PBS extreme optical macro biology cinematography at f/2.8 with hyper-detailed microscopic anatomy "
    "isolated against a clean dark velvet bokeh backdrop, strictly zero text"
)

CH12_LONG_NARRATIONS = [
    # ch1_hook (S01..S08)
    "Suspended from a silk button beneath a woodland twig, a plump caterpillar sheds its final larval skin to form a chrysalis.",
    "Inside this translucent amber shell, the insect is not simply resting or growing new limbs like an ordinary vertebrate animal.",
    "It is actively dissolving its entire internal larval anatomy, systematically melting muscle fibers, digestive organs, and skin into organic broth.",
    "Powerful digestive enzymes called caspases flood the larval tissues, systematically digesting cells from within through a programmed biological suicide process.",
    "Within barely forty-eight hours, the plump green caterpillar has transformed entirely into a soupy liquid puddle of nutrient-rich cellular broth.",
    "Yet somehow, out of this unformed biological soup, an entirely new organism with wings, antennae, and compound eyes will self-assemble.",
    "Even more astonishingly, modern cognitive experiments reveal that the emerging adult butterfly often retains memories formed during its larval life.",
    "How can complex neurological memories survive when the physical brain and larval nervous system dissolve completely into formless biological fluid?",
    # ch2_paradox (S09..S16)
    "Complete insect metamorphosis, known scientifically as holometabolism, represents one of evolutionary biology's greatest living paradoxes and most remarkably successful adaptations.",
    "Nearly eighty-five percent of all known insect species on Earth undergo this radical and complete physical reboot during their life cycles.",
    "From an evolutionary engineering standpoint, melting down a fully functioning body seems like an extraordinarily risky and inefficient survival strategy.",
    "While encased inside the motionless chrysalis, the developing insect is utterly defenseless against parasitic wasps, predatory ants, and mold infections.",
    "Yet holometabolism allowed insects to conquer every terrestrial ecosystem on Earth, successfully dominating animal biodiversity for three hundred million years.",
    "The true evolutionary secret lies in total ecological niche separation between the hungry crawling larva and the mobile flying adult.",
    "Caterpillars eat leaves, while butterflies sip nectar; parents and offspring never compete for the exact same food resources or habitats.",
    "The humble crawling caterpillar exists purely to accumulate metabolic calories; the adult exists to disperse and reproduce across vast distances.",
    # ch3_mechanism (S17..S24)
    "How exactly does this astonishing biological architectural miracle actually occur inside the sealed protective chamber of the translucent chrysalis shell?",
    "The hidden secret lies within microscopic clusters of dormant embryonic stem cells called imaginal discs, present since the caterpillar hatched.",
    "There are specific imaginal discs for each adult structure: two for compound eyes, two for antennae, and four for wings.",
    "While the young caterpillar crawled and chewed foliage, these disc cells remained dormant, suppressed by high levels of juvenile hormone.",
    "When juvenile hormone levels drop sharply at pupation, caspase enzymes dissolve somatic larval cells, but imaginal discs are completely immune.",
    "Floating safely inside the rich protein soup of digested caterpillar tissue, these imaginal discs begin dividing at extraordinary biological speeds.",
    "Complex chemical signaling gradients guide the dividing cells, folding flat microscopic discs into hollow three-dimensional legs, wings, and sensory organs.",
    "The caterpillar was never truly a single creature; it was always an organic mobile incubator carrying embryonic blueprinted cellular architects.",
    # ch4_case_study_1 (S25..S32)
    "Let us look closely at how the adult compound eye constructs itself rapidly from a flat microscopic disc of living tissue.",
    "A wave of cellular differentiation sweeps across the disc surface, leaving thousands of hexagonal crystalline lenses called ommatidia in its wake.",
    "Each tiny ommatidium contains eight photoreceptor cells capable of detecting ultraviolet light wavelengths completely invisible to the ordinary human eye.",
    "Microscopic tracheal air tubes grow alongside the developing nerve cells, delivering high-pressure oxygen directly to fuel intense metabolic cellular synthesis.",
    "Meanwhile, specialized epidermal cells produce chitin, the tough and durable structural polysaccharide that forms the insect's rigid outer protective armor.",
    "On the developing wing pads, microscopic living cells arrange themselves precisely in dense overlapping rows like miniature botanical roof shingles.",
    "As these scale cells mature, they deposit intricate nanometer-scale photonic ridges that manipulate light waves to produce brilliant iridescent colors.",
    "Without using a single chemical pigment, delicate structural nanometer physics creates dazzling metallic blues and emerald greens across the wings.",
    # ch5_escalation (S33..S40)
    "The exact same cellular precision that builds butterfly wings also engineers some of nature's most lethal microscopic predatory hunting weaponry.",
    "Consider the formidable praying mantis, which transforms from a delicate three-millimeter hatchling into an apex ambush predator of the undergrowth.",
    "Its raptorial forelegs are mechanical masterpieces of predatory design, densely lined with razor-sharp sclerotized chitin spines that interlock perfectly together.",
    "When actively hunting, the mantis locks its legs using specialized cuticular catches, storing mechanical potential energy in elastic thoracic proteins.",
    "When released, the forelegs snap forward in forty milliseconds, producing an explosive acceleration exceeding twenty times the pull of Earth's gravity.",
    "Sharp chitin spines impale the prey instantly, preventing escape while powerful serrated mandibles immediately begin consuming the captured victim headfirst.",
    "High-speed macro cameras reveal that the mantis calculates prey distance using stereoscopic 3D vision unique among all known invertebrate creatures.",
    "Microscopic physical scale allows predatory insects to harness lightning-fast biomechanical strike physics completely unavailable to larger and heavier mammalian predators.",
    # ch6_case_study_2 (S41..S48)
    "Other highly specialized insects take biochemical micro-weaponry to extraordinary extremes, turning their own internal abdomens into explosive chemical reaction chambers.",
    "The bombardier beetle safely stores toxic hydroquinone and hydrogen peroxide in separate internal biological reservoirs protected by thick muscular valves.",
    "When directly threatened by a predator, it pumps both chemicals into a thick-walled reaction chamber lined with catalytic peroxidase enzymes.",
    "An instantaneous chemical explosion ensues, rapidly boiling the liquid mixture to one hundred degrees Celsius within fractions of a second.",
    "Built-up steam pressure forces the scalding, noxious chemical spray out through an articulated tip that can swivel three hundred sixty degrees.",
    "The beetle fires this boiling chemical barrage in rapid pulses at five hundred bursts per second, stunning aggressive hunting spiders.",
    "Deadly assassin bugs utilize hollow, needle-sharp stylets to inject digestive cocktails that rapidly liquefy prey organs from the inside out.",
    "At the microscopic scale, sophisticated biochemical synthesis and mechanical ballistics combine seamlessly into horrifyingly efficient and lethal predatory weapons systems.",
    # ch7_systemic_shift (S49..S56)
    "Returning to our translucent chrysalis, the complex internal metamorphosis is finally nearing completion after fourteen days of hyper-accelerated cellular construction.",
    "The adult internal organs are fully formed: pulsating tubular heart, branched tracheal respiratory network, and a completely redesigned adult nervous system.",
    "The pupal shell becomes almost completely transparent, revealing the fully formed compound eyes and folded, crumpled wings packed tightly inside.",
    "The adult insect swallows surrounding air to expand its body, cracking open the dorsal seam of the rigid chrysalis shell.",
    "It crawls out onto a nearby twig, hanging upside down with soft, shriveled wings that closely resemble damp velvet ribbons.",
    "Now begins a critical hydraulic operation: the insect's muscular heart pumps green hemolymph fluid under pressure into hollow wing veins.",
    "Like inflating thousands of microscopic balloons, steady hydraulic hemolymph pressure expands the delicate wings to their full majestic surface area.",
    "Subsequent exposure to ambient atmospheric oxygen catalyzes chemical sclerotization, cross-linking chitin proteins to harden the expanded wings permanently and rigidly.",
    # ch8_resolution (S57..S64)
    "Within two hours, the soft, vulnerable crawler has completed one of the most radical physical transformations in the living world.",
    "It takes effortless, agile flight on gossamer wings, an airborne aeronaut governed by panoramic compound eyes and acute chemoreceptor antennae.",
    "And what of those mysterious larval memories so carefully tested in controlled scientific laboratories by modern behavioral and evolutionary neurobiologists?",
    "High-resolution microscopic imaging shows that specific neural synaptic circuits in the caterpillar's mushroom bodies survive the entire liquefaction process intact.",
    "The core identity of the creature persisted through the biological storm, carried safely through the complete melting of its body.",
    "From microscopic egg to liquid chrysalis to apex hunter, the insect life cycle exemplifies the unmatched genius of natural evolution.",
    "Next time you see a butterfly drifting or a mantis stalking on a summer leaf, witness an astonishing biological miracle.",
    "They are master engineers of the micro universe, proof that true strength lies in the power to reinvent oneself completely.",
]

for idx, s in enumerate(CH12_LONG_NARRATIONS, 1):
    cnt = len(s.split())
    assert 20 <= cnt <= 23, f"CH12 Long S{idx:02d} word count {cnt} outside 20-23: '{s}'"

CH12_CAMERAS = [
    "locked Laowa 24mm probe macro push-in",
    "ultra-shallow-DOF lateral specimen track",
    "steady micro-habitat orbit",
    "translucent dorsal cuticle glide",
]


def build_spawn_to_apex_long() -> Dict[str, Any]:
    shots = []
    for i in range(64):
        ch_idx = i // 8
        ch_name = CH10_CHAPTER_NAMES[ch_idx]
        is_opening = (i % 4 == 0)
        shot_id = f"S{i+1:02d}"
        cam = CH12_CAMERAS[i % 4]
        is_chapter_end = (i % 8 == 7)
        pause = 0.55 if is_chapter_end else 0.36

        start_vis = (
            f"Deep Look PBS extreme optical macro biology cinematography for {ch_name} shot {shot_id}: "
            f"extreme close-up on translucent amber insect cuticle at f/2.8, glistening cellular surface fluids, "
            f"razor-thin depth of field isolated against a clean dark velvet bokeh background, "
            f"warm glancing keylight highlighting microscopic chitin structures, strictly zero text."
        )
        end_vis = (
            f"Continuing on the same optical macro biology shot for {ch_name} shot {shot_id}: "
            f"delicate anatomical micro-structures shift subtly as glancing keylight reflects off iridescent chitin scales "
            f"and pulsating tracheal vessels, photorealistic PBS biology cinematography, strictly zero text."
        )
        motion = (
            f"camera executes {cam} across the translucent insect cuticle as internal cellular fluid "
            f"and micro-appendages exhibit subtle biological motion"
        )

        shot_dict = {
            "shot_id": shot_id,
            "scene_group": ch_name,
            "continues_prev": not is_opening,
            "scene_anchor": CH12_ANCHOR,
            "narration": CH12_LONG_NARRATIONS[i],
            "pause_after_sec": pause,
            "camera_verb": cam,
            "start_visual": start_vis,
            "end_visual": end_vis,
            "subject_motion": motion,
            "speech_rate": "+3%",
        }
        shots.append(shot_dict)

    return {
        "job_id": "en-spawn-to-apex-batch1-16x9",
        "channel_slug": "en-spawn-to-apex",
        "aspect": "16:9",
        "title": "Inside the Chrysalis & Beyond: How Insects Liquefy Their Bodies and Engineer Microscopic Weapons",
        "youtube_title": "How Insects Liquefy and Rebuild Their Bodies",
        "thumbnail_spec": {
            "visual_hook": "Extreme macro backlit translucent chrysalis revealing glowing imaginal discs assembling compound eyes and wings",
            "allowed_text": "LIQUID REBIRTH",
            "overlay_card": False,
        },
        "voice": "en-US-EricNeural",
        "shots": shots,
    }


CH12_SHORT_NARRATIONS = [
    "Beneath murky freshwater lurks the fastest underwater strike in the entire animal kingdom.",  # 13 words
    "Dragonfly nymphs possess a hinged lower jaw called a mask folded beneath their chin.",  # 13 words
    "Instead of relying on muscle contraction, the nymph builds immense internal hydraulic pressure.",  # 13 words
    "A microscopic cuticle catch releases stored fluid tension like a high-velocity mechanical spring.",  # 13 words
    "The barbed labium launches outward in fifteen milliseconds, seizing prey before light reflects.",  # 13 words
    "Sharp grasping pincers drag the victim backward directly into waiting serrated chewing mandibles.",  # 13 words
    "Watch our full documentary to explore the terrifying micro weapons engineered by insects.",  # 13 words
]

for idx, s in enumerate(CH12_SHORT_NARRATIONS, 1):
    cnt = len(s.split())
    assert 13 <= cnt <= 15, f"CH12 Short S{idx:02d} count {cnt} outside 13-15: '{s}'"


def build_spawn_to_apex_short() -> Dict[str, Any]:
    shots = [
        {
            "shot_id": "S01",
            "scene_group": "sg1_hook",
            "continues_prev": False,
            "scene_anchor": CH12_ANCHOR,
            "narration": CH12_SHORT_NARRATIONS[0],
            "pause_after_sec": 0.32,
            "camera_verb": "locked Laowa 24mm probe macro push-in",
            "start_visual": "Deep Look PBS extreme optical macro biology cinematography at f/2.8: murky underwater pond habitat with green duckweed and a camouflaged dragonfly nymph clinging to submerged reed, strictly zero text.",
            "end_visual": "On the same submerged reed, camera pushes closer revealing the predatory nymph's faceted compound eyes glistening underwater against dark velvet aquatic bokeh, strictly zero text.",
            "subject_motion": "the camouflaged dragonfly nymph clings motionlessly to the submerged reed as tiny water bubbles drift upward",
            "speech_rate": "+3%",
        },
        {
            "shot_id": "S02",
            "scene_group": "sg1_hook",
            "continues_prev": True,
            "scene_anchor": CH12_ANCHOR,
            "narration": CH12_SHORT_NARRATIONS[1],
            "pause_after_sec": 0.34,
            "camera_verb": "ultra-shallow-DOF lateral specimen track",
            "start_visual": "Extreme macro lateral profile of the dragonfly nymph head: articulated chitin plates showing the folded labium mask tucked tightly under its thorax, strictly zero text.",
            "end_visual": "On the same close-up, glancing light highlights the serrated pincer claws at the tip of the folded labium mask, strictly zero text.",
            "subject_motion": "camera tracks laterally across the nymph's armored head as aquatic keylight glints on the folded jaw structure",
            "speech_rate": "+3%",
        },
        {
            "shot_id": "S03",
            "scene_group": "sg2_mechanism",
            "continues_prev": False,
            "scene_anchor": CH12_ANCHOR,
            "narration": CH12_SHORT_NARRATIONS[2],
            "pause_after_sec": 0.32,
            "camera_verb": "locked Laowa 24mm probe macro push-in",
            "start_visual": "Translucent macro view showing the nymph's abdominal cavity contracting, compressing hemolymph fluid under high internal pressure, optical macro f/2.8, strictly zero text.",
            "end_visual": "On the same specimen, internal fluid pressure shifts forward toward the thoracic labial hinge with subtle chitin tension, strictly zero text.",
            "subject_motion": "the nymph's abdomen contracts subtly as internal fluid pressure builds behind the locked jaw joint",
            "speech_rate": "+3%",
        },
        {
            "shot_id": "S04",
            "scene_group": "sg2_mechanism",
            "continues_prev": True,
            "scene_anchor": CH12_ANCHOR,
            "narration": CH12_SHORT_NARRATIONS[3],
            "pause_after_sec": 0.34,
            "camera_verb": "ultra-shallow-DOF lateral specimen track",
            "start_visual": "Extreme macro shot of the microscopic labial latch joint, glistening chitin cuticle mechanism locked in high-tension position, strictly zero text.",
            "end_visual": "On the exact same latch joint, the cuticle trigger releases smoothly as internal elastic tension uncoils, strictly zero text.",
            "subject_motion": "the microscopic chitin latch slips free, unleashing pent-up hydraulic force with razor-sharp mechanical precision",
            "speech_rate": "+3%",
        },
        {
            "shot_id": "S05",
            "scene_group": "sg3_impact",
            "continues_prev": False,
            "scene_anchor": CH12_ANCHOR,
            "narration": CH12_SHORT_NARRATIONS[4],
            "pause_after_sec": 0.32,
            "camera_verb": "high-speed microscopic slow-motion pass",
            "start_visual": "Ultra high-speed phantom macro camera view: the hinged lower mask explodes forward through clear pond water toward an unsuspecting water bug, strictly zero text.",
            "end_visual": "In the same high-speed frame, the extended barbed pincers snap shut around the water bug with foaming micro-cavitation bubbles, strictly zero text.",
            "subject_motion": "the hinged jaw shoots forward with blinding speed, snapping sharp terminal claws around the prey underwater",
            "speech_rate": "+3%",
        },
        {
            "shot_id": "S06",
            "scene_group": "sg3_impact",
            "continues_prev": True,
            "scene_anchor": CH12_ANCHOR,
            "narration": CH12_SHORT_NARRATIONS[5],
            "pause_after_sec": 0.34,
            "camera_verb": "locked Laowa 24mm probe macro push-in",
            "start_visual": "High-speed macro shot as the extended mask retracts rapidly, hauling the captured prey back beneath the nymph's armored head, strictly zero text.",
            "end_visual": "On the same view, the serrated chewing mandibles open and begin processing the prey against dark aquatic bokeh, strictly zero text.",
            "subject_motion": "the hydraulic mask retracts smoothly, pulling the trapped prey directly into the nymph's powerful chewing jaws",
            "speech_rate": "+3%",
        },
        {
            "shot_id": "S07",
            "scene_group": "sg4_cta",
            "continues_prev": False,
            "scene_anchor": CH12_ANCHOR,
            "narration": CH12_SHORT_NARRATIONS[6],
            "pause_after_sec": 0.36,
            "camera_verb": "steady micro-habitat orbit",
            "start_visual": "Deep Look PBS extreme macro beauty shot: an iridescent adult dragonfly perched on a sunlit reed with crystalline gossamer wings reflecting rainbow highlights, strictly zero text.",
            "end_visual": "On the same sunlit dragonfly, warm golden light catches its massive faceted compound eyes against clean dark woodland bokeh, strictly zero text.",
            "subject_motion": "the adult dragonfly twitches its iridescent wings gently in warm sunlight against dark woodland bokeh",
            "speech_rate": "+3%",
        },
    ]

    return {
        "job_id": "en-spawn-to-apex-batch1-9x16",
        "channel_slug": "en-spawn-to-apex",
        "aspect": "9:16",
        "parent_long_id": "en-spawn-to-apex-batch1-16x9",
        "title": "Hydraulic Strike: How a Dragonfly Nymph Fires Its Lower Jaw in 15 Milliseconds",
        "youtube_title": "The 15-Millisecond Hydraulic Jaw Strike",
        "voice": "en-US-EricNeural",
        "shots": shots,
    }


def main() -> None:
    specs = [
        ("en-choke-point_long_16x9.json", build_choke_point_long()),
        ("en-choke-point_short_9x16.json", build_choke_point_short()),
        ("en-root-and-canopy_long_16x9.json", build_root_and_canopy_long()),
        ("en-root-and-canopy_short_9x16.json", build_root_and_canopy_short()),
        ("en-spawn-to-apex_long_16x9.json", build_spawn_to_apex_long()),
        ("en-spawn-to-apex_short_9x16.json", build_spawn_to_apex_short()),
    ]

    for fname, data in specs:
        out_path = SPECS_DIR / fname
        out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        total_words = sum(len(s["narration"].split()) for s in data["shots"])
        print(f"[✓] Generated {out_path.name}: {len(data['shots'])} shots, {total_words} words, job_id={data['job_id']}")


if __name__ == "__main__":
    main()
