#!/usr/bin/env python3
"""Spec builder for en-scale-and-bone (Long 16:9 and Short 9:16)."""

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

ANCHOR_CLIFF = (
    "BBC Earth natural-history wildlife cinematography on long-focal cinema glass, "
    "golden natural atmospheric daylight, rich organic terrain textures on sheer granite crag, strictly zero text"
)
ANCHOR_BIOMECH = (
    "Authentic vertebrate muscular biomechanics and feather micro-textures reacting to alpine wind, "
    "shallow depth-of-field 400mm cinema lens, crisp natural mountain rim lighting, strictly zero text"
)
ANCHOR_AERIAL = (
    "Vast alpine cinematic aerial survey, soaring mountain peaks shrouded in morning mist, "
    "crisp directional sunlight catching snow dust and rock faces, strictly zero text"
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
        anchor: str = ANCHOR_CLIFF,
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
    # Group 1: The Precipice Edge
    add_shot(
        "S01",
        "ch1_hook",
        False,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "Perched three thousand feet above an alpine chasm, a seventy-day-old golden eagle chick teeters precariously upon a razor-sharp granite cliff edge.",
        "BBC Earth wildlife frame: high Scottish Highland granite precipice shrouded in swirling mist, morning sunlight glinting off lichen-covered rock.",
        "Pushing closer with 400mm telephoto lens onto the downy brown fledgling gripping the granite ridge, wind ruffling its feathers.",
        "roaring alpine wind ruffles the downy plumage of the eagle fledgling as it grips the lichen-encrusted granite ridge",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S02",
        "ch1_hook",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "Freezing hundred-mile-per-hour alpine gales howl upward from the valley floor, buffeting the fledgling's untested wings toward the terrifying drop below.",
        "Intimate eye-level view of the eagle fledgling facing directly into the howling alpine wind.",
        "Pushing in on the chick's piercing golden amber eyes reflecting the sheer dizzying vertical drop beneath the cliff face.",
        "golden eagle chick blinks against howling updrafts as its amber eyes track distant rocky spires below",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S03",
        "ch1_hook",
        True,
        0.36,
        "Slow crane reveal across natural habitat",
        "Beneath its clutching yellow talons lies only empty air and jagged talus boulders ready to crush any miscalculated wing stroke.",
        "Camera cranes vertically downward from the eagle chick's talons along the sheer vertical rock wall.",
        "Revealing thousands of feet of sheer vertical drop terminating in razor-sharp slate boulders and ancient glacial scree slopes.",
        "camera sweeps down the terrifying vertical rock face revealing jagged talus fields thousands of feet below",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S04",
        "ch1_hook",
        True,
        0.44,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "For ten long weeks, this narrow ledge of moss and dry pine twigs has been its entire sheltered, safe universe.",
        "Close tracking shot of the messy alpine eyrie nest woven from sturdy birch branches and dry mountain moss.",
        "Tracking along the weathered sticks of the nest toward the fledgling standing hesitantly at the outermost perimeter boundary.",
        "camera tracks past weathered pine nest branches toward the fledgling stepping cautiously to the sheer ledge boundary",
        ANCHOR_CLIFF,
    )

    # Group 2: The Approaching Moment
    add_shot(
        "S05",
        "ch1_hook",
        False,
        0.36,
        "Slow crane reveal across natural habitat",
        "Now, its downy juvenile feathers have hardened into dark, rigid flight quills, signaling an urgent biological countdown that cannot be stopped.",
        "BBC Earth wildlife cinematography: morning sun breaking through mountain cloud cover illuminating the fledgling's developing wing feathers.",
        "Crane reveals the full five-foot wingspan of the fledgling as it stretches its muscular wings against the golden sunrise.",
        "fledgling unfurls its developing wings, showing dark flight quills glistening against brilliant morning mountain light",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S06",
        "ch1_hook",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "Its massive breast muscles twitch with involuntary nervous contractions, burning through precious stored fat reserves with every passing freezing hour.",
        "Macro telephoto view of the fledgling's feathered chest and powerful pectoral muscular girdle under golden side-lighting.",
        "Pushing in on the rhythmic pulsing contractions of the pectoral flight muscles under the dense insulating brown plumage.",
        "pectoral flight muscles contract in involuntary shivering spasms as the fledgling tests aerodynamic wind resistance",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S07",
        "ch1_hook",
        True,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "To become sovereign monarch of these skies, this clumsy mountain chick must commit to the ultimate act of blind evolutionary faith.",
        "Telephoto tracking shot following the chick as it shifts its weight forward on the extreme lip of the stone.",
        "Tracking closer as small pebbles dislodge from under its sharp curved talons, tumbling silently into the immense yawning abyss.",
        "loose granite pebbles break away under the chick's talons, falling soundlessly into the deep alpine mist",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S08",
        "ch1_hook",
        True,
        0.55,
        "Slow crane reveal across natural habitat",
        "A single hesitation means slow starvation on the cliff, while a premature plunge means fatal deceleration against the mountain boulders below.",
        "Wide cinematic crane rising above the solitary granite crag flanked by majestic snow-dusted alpine mountain spires.",
        "Sweeping upward into the cold blue sky, leaving the lone fledgling dwarfed against the monumental geological scale of the mountain.",
        "camera rises smoothly into the high alpine air, framing the lone eagle fledgling against towering jagged peaks",
        ANCHOR_AERIAL,
    )

    # ==========================================
    # CHAPTER 2: ch2_paradox (S09..S16)
    # ==========================================
    # Group 1: The Withdrawal of the Mother
    add_shot(
        "S09",
        "ch2_paradox",
        False,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "For two months, the mother golden eagle was a fiercely protective guardian, delivering fresh mountain hares to satisfy its ravenous hunger.",
        "BBC Earth wildlife frame: majestic adult female golden eagle landing softly on the mossy eyrie nest in soft morning mist.",
        "Telephoto tracking shot as the magnificent mother drops a freshly caught mountain hare beside her eager chirping offspring.",
        "adult golden eagle mother lands on the nest with outstretched wings, delivering prey to her excited chick",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S10",
        "ch2_paradox",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "She shielded the fragile fledgling from freezing torrential downpours beneath her seven-foot wingspan, tearing tender morsels for its daily nourishment.",
        "Intimate eye-level shot of the mother sheltering the young fledgling under her massive, dark brown feathered mantle.",
        "Pushing in as she gently preens the fledgling's head feathers with the blunt curve of her razor-sharp hooked beak.",
        "mother eagle gently preens the chick's neck feathers with her beak, sheltering it from alpine mist",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S11",
        "ch2_paradox",
        True,
        0.36,
        "Slow crane reveal across natural habitat",
        "Yet abruptly, on the seventy-first freezing morning, the maternal bond appears to shatter into cold, calculated and utterly merciless indifference.",
        "Crane shot rising over the eyrie ledge as early morning frost covers the sticks and the mother is nowhere to be seen.",
        "Revealing the fledgling standing entirely alone on the cold frozen ledge, calling out with shrill, desperate juvenile cries.",
        "lone fledgling pacing frantically across the empty frost-covered eyrie, emitting sharp whistling distress calls",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S12",
        "ch2_paradox",
        True,
        0.44,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "She does not land in the nest; instead, she perches across the chasm, prominently gripping a fat mountain grouse just outside reach.",
        "Telephoto view across the deep chasm focusing on the adult eagle perched on an isolated pinnacle rock fifty yards away.",
        "Tracking across the gulf as the mother rips into the grouse carcass in full view of her starving, crying chick.",
        "mother eagle perches across the chasm tearing into fresh game, deliberately withholding food from her fledgling",
        ANCHOR_CLIFF,
    )

    # Group 2: The Evolutionary Calculation
    add_shot(
        "S13",
        "ch2_paradox",
        False,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "To casual human observers, this deliberate deprivation seems cruel; yet evolutionary biologists recognize it as a mandatory life-or-death biological calculation.",
        "Intimate telephoto perspective of the fledgling's distressed posture as its stomach hollows from three consecutive days without food.",
        "Tracking the chick's hungry gaze locked onto the food across the chasm, neck stretched forward over the vertical void.",
        "fledgling leans out dangerously over the abyss, stretching its neck and calling toward the distant food",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S14",
        "ch2_paradox",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "A well-fed chick is far too heavy to generate initial aerodynamic lift with untested flight muscles on its maiden launch.",
        "Close anatomical push-in on the fledgling's abdominal contour and leg joints as it balances on the rock ridge.",
        "Pushing in as the chick loses excess water weight and fat, shifting its center of gravity toward its aerodynamic chest.",
        "chick shifts its weight forward, revealing leaner streamlined body proportions optimized for initial aerodynamic flight",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S15",
        "ch2_paradox",
        True,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "By starving her chick, the mother forces its body to burn off dead weight while weaponizing hunger against primal acrophobia.",
        "Telephoto tracking shot of the fledgling stepping repeatedly toward the cliff edge, driven by overwhelming hunger pangs.",
        "Tracking as the chick flaps its wings vigorously on the rock, feeling the upward tug of the rising thermal draft.",
        "fledgling flaps its large wings in place, generating powerful air currents that lift its talons momentarily off rock",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S16",
        "ch2_paradox",
        True,
        0.55,
        "Slow crane reveal across natural habitat",
        "Hunger becomes the indispensable evolutionary catalyst, transforming paralyzing instinctual terror into the desperate, reckless courage required to jump into air.",
        "Cinematic crane rising behind the fledgling silhouetted against the vast glowing chasm separating it from its mother.",
        "Crane reveals the adult eagle soaring in sweeping circles through the thermal gap, demonstrating the flight path its chick must take.",
        "adult eagle glides effortlessly across the chasm on outstretched wings, carving a soaring path through mountain updrafts",
        ANCHOR_AERIAL,
    )

    # ==========================================
    # CHAPTER 3: ch3_mechanism (S17..S24)
    # ==========================================
    # Group 1: Skeletal and Keel Architecture
    add_shot(
        "S17",
        "ch3_mechanism",
        False,
        0.36,
        "Intimate eye-level optical push-in",
        "Inside the young fledgling's body lies fifty million years of avian evolutionary engineering, beginning with an astonishing ultralight skeletal framework.",
        "BBC Earth scientific wildlife cinematography: macro anatomical view of the eagle's feathered shoulder and chest structure under soft backlight.",
        "Pushing in on the pectoral girdle where massive flight muscles anchor to the deep bony carina sternum keel.",
        "camera pushes in on the eagle's powerful chest structure, emphasizing the deep aerodynamic muscular anchor",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S18",
        "ch3_mechanism",
        True,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "Unlike heavy dense mammalian bone, an eagle's skeleton is pneumatic: completely hollow within and braced by microscopic internal truss struts.",
        "Macro telephoto view of the fledgling's wing bones flexing under tension as it beats its wings against mountain wind.",
        "Tracking along the wing humerus and radius, capturing how the lightweight honeycomb structure flexes without fracturing under high aerodynamic load.",
        "wing joints flex smoothly under wind resistance, absorbing turbulent shear through resilient internal biological geometry",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S19",
        "ch3_mechanism",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "Its entire skeleton weighs less than its feathers, granting the bird an extraordinary strength-to-weight ratio unmatched by modern carbon fiber.",
        "Intimate eye-level perspective of the fledgling folding its massive wings tightly against its streamlined body.",
        "Pushing in on the seamless aerodynamic contour of the plumage forming an immaculate low-drag biological teardrop.",
        "feathers settle tightly into a sleek aerodynamic profile, channeling mountain winds smoothly over the bird's back",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S20",
        "ch3_mechanism",
        True,
        0.44,
        "Slow crane reveal across natural habitat",
        "Connecting this skeletal frame are massive pectoral muscles capable of generating thirty pounds of downward thrust with every single powerful beat.",
        "Low-angle crane shot looking up at the fledgling standing tall on the crag, beating its wings in full downward power-strokes.",
        "Craning up as gusts from the wing beats blow dust and dry pine needles off the ledge in dramatic swirling vortices.",
        "powerful downward wing stroke creates visible swirling dust vortices across the rocky ledge surface",
        ANCHOR_BIOMECH,
    )

    # Group 2: Feather Interlocking Micro-Physics
    add_shot(
        "S21",
        "ch3_mechanism",
        False,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "Even more remarkable is the microscopic architecture of the primary flight feathers, known as the ten finger quills of the wingtip.",
        "BBC Earth wildlife macro: extreme telephoto close-up of the outermost primary wing feathers fanning out against bright mountain sky.",
        "Tracking along the individual separated flight feathers as they spread apart like splayed human fingers in the wind.",
        "primary wingtip feathers splay apart individually, twisting dynamically to relieve aerodynamic wingtip vortex drag",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S22",
        "ch3_mechanism",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "Thousands of microscopic hooklets called barbules interlock like biological zippers, creating an airtight aerodynamic foil that withstands savage hurricane gusts.",
        "Macro optical push-in on the dark brown feather vane, revealing microscopic interlocking hooklets catching sunlight.",
        "Pushing deeper as the smooth airtight surface flexes under pressure without permitting a single molecule of air to bleed through.",
        "feather vane flexes under intense wind pressure, maintaining an airtight curved aerodynamic foil surface",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S23",
        "ch3_mechanism",
        True,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "When air rushes over the cambered upper surface, it accelerates, dropping air pressure and sucking the bird vertically into the sky.",
        "Telephoto view of the wing cross-section from the side as mountain wind streams across the curved feather surface.",
        "Tracking as the wing automatically arches upward under the invisible suction of low pressure generated across its curved dorsum.",
        "entire wing arches upward as aerodynamic lift force overcomes the physical weight of the young bird",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S24",
        "ch3_mechanism",
        True,
        0.55,
        "Slow crane reveal across natural habitat",
        "Every physical millimeter of the chick is aerodynamically primed for flight; all that remains is the cognitive leap into the void.",
        "Cinematic crane shot rising above the fledgling's head, framing the bird poised at the edge of the sheer alpine drop.",
        "Sweeping outward toward the vast mountain horizon where jagged snowy summits stretch toward the sunlit infinity.",
        "camera sweeps over the fledgling's head into the colossal expanse of alpine valleys bathed in morning gold",
        ANCHOR_AERIAL,
    )

    # ==========================================
    # CHAPTER 4: ch4_case_study_1 (S25..S32)
    # ==========================================
    # Group 1: Mountain Thermal Physics
    add_shot(
        "S25",
        "ch4_case_study_1",
        False,
        0.36,
        "Slow crane reveal across natural habitat",
        "To conquer the harsh alpine wilderness, an eagle cannot merely flap its wings; it must master the invisible highways of mountain thermals.",
        "BBC Earth wide aerial view: dark jagged granite mountain slopes absorbing the heat of the rising morning sun.",
        "Crane glides along the vertical rock face where shimmering heat waves rise like transparent mirages into the cold sky.",
        "shimmering transparent heat waves rise rapidly along the sunlit vertical granite mountain face",
        ANCHOR_AERIAL,
    )
    add_shot(
        "S26",
        "ch4_case_study_1",
        True,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "As dawn sunlight bakes dark granite faces, the surrounding air warms rapidly, expanding and rushing upward in powerful chimney-like updrafts.",
        "Telephoto tracking shot following mountain mist and moisture rising in vertical speed along the sheer cliff wall.",
        "Tracking upward as small dry leaves and pine needles are sucked vertically upward in the rising column of warm air.",
        "pine needles and loose mountain debris ascend smoothly inside the powerful vertical thermal updraft column",
        ANCHOR_AERIAL,
    )
    add_shot(
        "S27",
        "ch4_case_study_1",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "These anabatic winds generate vertical elevator columns climbing at twenty miles per hour, capable of lifting fifteen-pound eagles without effort.",
        "Intimate eye-level view of the fledgling extending its neck over the edge, feeling the warm rising thermal current on its face.",
        "Pushing in on the chick's facial contour as its delicate sensory facial feathers vibrate in the rushing upward airstream.",
        "delicate facial feathers around the eagle chick's beak vibrate rapidly in the rising stream of warm mountain air",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S28",
        "ch4_case_study_1",
        True,
        0.44,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "Yet mountain aerodynamics are treacherous: directly adjacent to rising thermals lie violent downdrafts and turbulent rotors that slam birds into stone.",
        "Wide telephoto shot of the rocky mountain notch where swirling wind vortices form turbulent cloud eddies in mid-air.",
        "Tracking as swirling cloud tendrils violently tumble and rotate along the jagged leeward cliff face.",
        "swirling cloud tendrils spin violently in chaotic rotor vortices along the shadow side of the granite ridge",
        ANCHOR_AERIAL,
    )

    # Group 2: The Mother's Flight Demonstration
    add_shot(
        "S29",
        "ch4_case_study_1",
        False,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "High above the canyon, the adult mother provides a masterclass in aerodynamic navigation, carving effortless figure-eights across the thermal boundary.",
        "BBC Earth wildlife frame: adult golden eagle soaring high above the alpine chasm against dramatic storm clouds.",
        "Telephoto tracking shot following the magnificent bird as she banks gracefully into the rising thermal core without flapping once.",
        "adult eagle banks smoothly on flat wings, spiraling effortlessly upward within the invisible thermal core",
        ANCHOR_AERIAL,
    )
    add_shot(
        "S30",
        "ch4_case_study_1",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "She adjusts her slotted wingtip feathers by fractions of a millimeter, dynamically dampening turbulence and converting sheer shear into kinetic speed.",
        "Intimate telephoto perspective of the soaring eagle's wingtip, capturing subtle micro-adjustments of individual feathers.",
        "Pushing in on the primary feathers twisting independently to bleed off drag and maintain laminar boundary airflow across the wing.",
        "wingtip feathers twist independently in rapid micro-adjustments to neutralize sudden turbulent wind shear",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S31",
        "ch4_case_study_1",
        True,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "She calls out with a sharp, piercing whistle that echoes off the granite walls, commanding her fledgling to watch and follow.",
        "Adult eagle banking across the chasm, opening her yellow beak to emit a sharp, piercing alpine hunting cry.",
        "Tracking as the sound reverberates across the rocky cliffs, reaching the fledgling perched three thousand feet above the gorge.",
        "adult eagle emits a piercing cry mid-flight as sound echoes across the vertical amphitheater of cliffs",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S32",
        "ch4_case_study_1",
        True,
        0.55,
        "Slow crane reveal across natural habitat",
        "The fledgling tracks her effortless trajectory with dilated pupils, internalizing the geometry of the invisible sky it must soon conquer alone.",
        "Cinematic crane rising behind the fledgling's head, showing its gaze locked onto the soaring silhouette of its mother below.",
        "Sweeping around the chick as its body begins leaning forward, aligning its shoulders with the exact wind vector of the valley.",
        "fledgling leans its chest into the wind vector, mirroring the aerodynamic posture of its mother below",
        ANCHOR_CLIFF,
    )

    # ==========================================
    # CHAPTER 5: ch5_escalation (S33..S40)
    # ==========================================
    # Group 1: The Maiden Plunge
    add_shot(
        "S33",
        "ch5_escalation",
        False,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "The decisive seventy-second morning arrives with bitter sub-zero mountain frost and a sudden ferocious crosswind ripping across the eyrie ledge.",
        "BBC Earth wildlife cinematography: frost needles covering the granite ledge as icy gale winds blow snow dust into the air.",
        "Telephoto tracking shot of the shivering fledgling standing at the extreme stone point, hunger burning in its amber eyes.",
        "fledgling shivers against bitter sub-zero gales as icy snow crystals whip across the sheer granite ledge",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S34",
        "ch5_escalation",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "Driven by sheer starvation and instinctual panic, the young eagle leans too far forward; its yellow talons lose their grip.",
        "Intimate close-up of the chick's curved yellow talons slipping on the frost-slicked granite ledge.",
        "Pushing in as the stone crumbles beneath its claws, breaking contact with the solid earth for the first time in life.",
        "eagle chick's talons slip on frost-slick granite as its body tips forward into uncontrollable freefall",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S35",
        "ch5_escalation",
        True,
        0.36,
        "Slow crane reveal across natural habitat",
        "It falls: five hundred feet of sheer vertical plummet, tumbling end over end toward the merciless jagged talus rocks below.",
        "Wide dramatic crane shot capturing the chick tumbling headfirst down the sheer vertical face of the three-thousand-foot precipice.",
        "Tracking the rapid fall as the chick flails its wings chaotically in the violent airstream, accelerating toward terminal speed.",
        "fledgling plummets in chaotic freefall down the sheer cliff face, wings flapping wildly without aerodynamic control",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S36",
        "ch5_escalation",
        True,
        0.44,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "Wind shrieks through its chaotic feathers as the mountain floor rushes upward with terrifying, lethal speed toward its helpless body.",
        "Telephoto tracking shot following the tumbling bird from below as the granite crags flash past in dizzying motion blur.",
        "Tracking the plummeting silhouette as it drops within two hundred feet of jagged slate boulders at sixty miles an hour.",
        "plummeting eagle chick accelerates toward jagged boulders below as wind tears through its splayed feathers",
        ANCHOR_CLIFF,
    )

    # Group 2: The Aerodynamic Catch
    add_shot(
        "S37",
        "ch5_escalation",
        False,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "At the final split-second before catastrophic impact, evolutionary instinct overrides terror: the chick snaps its wings fully open and locks joints.",
        "BBC Earth high-speed telephoto frame: the plummeting fledgling suddenly snapping its primary flight wings into a rigid horizontal plane.",
        "Tracking as the broad dark wings lock into place, instantly transforming a deadweight drop into a high-speed forward glide.",
        "fledgling snaps wings fully outward and locks its carpal joints, catching the rushing air in a sudden deceleration",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S38",
        "ch5_escalation",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "The rushing air slams into the underside of the broad wings, producing a monumental upward deceleration that bows the feather quills.",
        "Intimate tracking shot alongside the eagle chick as its flight feathers bow upward under immense aerodynamic g-forces.",
        "Pushing in on the bird's focused expression as its tail feathers spread into an aerodynamic rudder, stabilizing its flight attitude.",
        "flight feathers arch upward under massive lift forces as the eagle levels off mere yards above jagged rocks",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S39",
        "ch5_escalation",
        True,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "Instead of smashing into stone, the fledgling swoops upward in a breathtaking parabolic arc, skimming twenty feet above the boulders.",
        "Telephoto shot tracking the young eagle as it sweeps smoothly upward, converting sixty miles of dive speed into altitude.",
        "Tracking as the eagle glides clear of the talus boulder field and out over the open expanse of the valley floor.",
        "young eagle surges upward in a soaring climb over the boulder field, sailing out across the open valley abyss",
        ANCHOR_AERIAL,
    )
    add_shot(
        "S40",
        "ch5_escalation",
        True,
        0.55,
        "Slow crane reveal across natural habitat",
        "It is airborne: clumsy, terrified, and breathless, but flying under its own biological power for the very first time in existence.",
        "Cinematic wide crane tracking the fledgling soaring over the majestic green Scottish glen far below.",
        "Rising above the young eagle as it beats its wings rhythmically, climbing steadily into the safety of the open sky.",
        "camera soars alongside the young eagle as it climbs steadily into golden morning light above the green glen",
        ANCHOR_AERIAL,
    )

    # ==========================================
    # CHAPTER 6: ch6_case_study_2 (S41..S48)
    # ==========================================
    # Group 1: The Territorial Gauntlet
    add_shot(
        "S41",
        "ch6_case_study_2",
        False,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "Surviving the first leap is only the entrance exam; the fledgling must now run the deadly gauntlet of alpine territorial conflict.",
        "BBC Earth wildlife frame: high alpine ridge line under moody slate clouds, where an adult rival eagle patrols the border.",
        "Telephoto tracking shot following an immense territorial male golden eagle soaring with aggressive posture along the ridgeline.",
        "huge territorial adult eagle glides menacingly along the mountain ridge, scanning for intruding juveniles",
        ANCHOR_AERIAL,
    )
    add_shot(
        "S42",
        "ch6_case_study_2",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "Adult golden eagles defend fifty square miles of mountain airspace with savage ferocity, frequently executing lethal strikes against intruding juveniles.",
        "Intimate view of the territorial adult's menacing talons curled into striking weapons beneath its feathered thighs.",
        "Pushing in on the glistening two-inch black talons capable of crushing skulls with four hundred pounds of grip pressure.",
        "two-inch black talons flex rhythmically in mid-flight as the adult predator locks onto the young fledgling",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S43",
        "ch6_case_study_2",
        True,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "When the resident territorial male eagle spots the inexperienced fledgling, he tucks his wings and enters a ferocious hundred-and-fifty-mile-per-hour attack stoop.",
        "Telephoto tracking shot of the adult folding wings into a sleek teardrop missile, diving vertically from the high clouds.",
        "Tracking the diving adult as wind screams across its plumage, hurtling directly toward the vulnerable young bird below.",
        "adult eagle dives in a screaming high-speed attack stoop toward the young fledgling navigating the valley",
        ANCHOR_AERIAL,
    )
    add_shot(
        "S44",
        "ch6_case_study_2",
        True,
        0.44,
        "Slow crane reveal across natural habitat",
        "The mother eagle intercepts the attack in mid-air, clashing talons with the intruder in a ferocious rolling dogfight above the abyss.",
        "Wide crane shot capturing the mother eagle slamming into the attacking male in mid-air, talons locked together in fierce combat.",
        "Craning as the two massive birds cartwheel downward in locked combat before disengaging and driving the intruder away.",
        "two giant adult eagles cartwheel through the sky with interlocked talons before breaking apart in dramatic flight",
        ANCHOR_AERIAL,
    )

    # Group 2: The Alpine Blizzard
    add_shot(
        "S45",
        "ch6_case_study_2",
        False,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "Days later, a savage autumn blizzard engulfs the high peaks, burying the mountain crags in blinding whiteout and zero visibility.",
        "BBC Earth wildlife frame: roaring blizzard winds whipping heavy snowdrifts across dark jagged granite crags.",
        "Telephoto tracking shot of the fledgling huddled tightly under a shallow rock overhang, covered in a mantle of white snow.",
        "fledgling perches resolutely under a narrow rock overhang as howling blizzard winds dump heavy snow onto its mantle",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S46",
        "ch6_case_study_2",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "With sub-zero mountain temperatures threatening hypothermia, its dense downy under-feathers trap a warm layer of insulating air against its skin.",
        "Intimate macro telephoto view of the fledgling's plumage puffing out to trap warm air pockets beneath its feathers.",
        "Pushing in as snow melts harmlessly on the oily outer flight feathers without penetrating into the dry, warm down below.",
        "insulating downy feathers expand, trapping body heat while icy snow melts harmlessly off oily outer wing quills",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S47",
        "ch6_case_study_2",
        True,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "For three brutal days without food, the young bird endures the blizzard, demonstrating the formidable physiological resilience of its lineage.",
        "Telephoto tracking shot showing the fledgling shaking heavy snow from its head and wings as the storm begins to break.",
        "Tracking as morning sunlight cuts through clearing storm clouds, illuminating the snow-dusted eagle ready for hunt.",
        "eagle shakes heavy snow from its feathers as golden sunlight breaks through retreating storm clouds",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S48",
        "ch6_case_study_2",
        True,
        0.55,
        "Slow crane reveal across natural habitat",
        "The brutal crucible of storm and conflict has forged a battle-hardened predator, replacing clumsy juvenile hesitation with lethal, calm confidence.",
        "Cinematic crane rising above the sunlit snow-capped alpine ridge where the fledgling spreads its wings in triumphant readiness.",
        "Sweeping upward into crystal-clear blue skies as the bird launches cleanly off the crag into smooth rising thermal air.",
        "camera sweeps up as the confident young eagle launches effortlessly into pristine blue skies above the snowy range",
        ANCHOR_AERIAL,
    )

    # ==========================================
    # CHAPTER 7: ch7_systemic_shift (S49..S56)
    # ==========================================
    # Group 1: The Apex Sensory Weapons
    add_shot(
        "S49",
        "ch7_systemic_shift",
        False,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "By month four, the young golden eagle has developed the most formidable hunting sensory apparatus in the entire vertebrate kingdom.",
        "BBC Earth wildlife frame: magnificent close telephoto portrait of the juvenile eagle perched on a high granite sentinel post.",
        "Telephoto tracking shot pushing in on the bird's golden-amber eyes scanning the distant valley floor with laser focus.",
        "eagle turns its head with razor precision, its piercing amber eyes locking onto distant movement miles away",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S50",
        "ch7_systemic_shift",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "Its eyes contain one million photoreceptor cones per square millimeter, resolving a running rabbit from over two miles away in flight.",
        "Intimate optical push-in on the eagle's pupil contracting and expanding with remarkable speed in the bright sunlight.",
        "Pushing in on the pecten oculi vascular comb inside the eye providing intense oxygenation and crystal-clear high-speed motion tracking.",
        "eagle's pupil contracts sharply, resolving minute motion on the distant valley floor with microscopic clarity",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S51",
        "ch7_systemic_shift",
        True,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "Binocular vision with thirty-five degrees of stereoscopic overlap allows it to judge distance and dive vectors with lethal trigonometric precision.",
        "Frontal telephoto view of the eagle's face as both eyes lock forward into a terrifying predatory binocular stare.",
        "Tracking as the eagle calculates its dive trajectory, leaning forward with shoulders hunched in ready coiled tension.",
        "eagle's eyes lock forward in intense binocular focus, its muscular shoulders coiling for an explosive dive",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S52",
        "ch7_systemic_shift",
        True,
        0.44,
        "Slow crane reveal across natural habitat",
        "Beneath its heavy feathered brow, a transparent nictitating membrane acts as natural biological flight goggles during high-velocity alpine stoop dives.",
        "Macro telephoto shot of the eagle's eye as the translucent nictitating membrane sweeps horizontally across the gleaming cornea.",
        "Craning closer as the protective membrane cleans and moistens the eye while maintaining full optical visual clarity in gale winds.",
        "translucent nictitating membrane flashes across the cornea, protecting the eye against hundred-mile-per-hour winds",
        ANCHOR_BIOMECH,
    )

    # Group 2: The Two-Hundred-MPH Stoop
    add_shot(
        "S53",
        "ch7_systemic_shift",
        False,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "Now comes the ultimate test of the young hunter: executing its very first solo kill against a full-grown mountain hare.",
        "BBC Earth wildlife frame: vast rolling heather hills two thousand feet below, where a white mountain hare feeds cautiously.",
        "Telephoto tracking shot following the eagle soaring high above, tilting its wings into a tight steepening bank.",
        "young eagle banks sharply into a dive above the heather moors, locking target onto the grazing hare below",
        ANCHOR_AERIAL,
    )
    add_shot(
        "S54",
        "ch7_systemic_shift",
        True,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "It folds its wings into an arrowhead silhouette, dropping like a kinetic artillery shell at nearly two hundred miles an hour.",
        "High-speed telephoto tracking shot following the eagle screaming downward in an immaculate, aerodynamic dive.",
        "Tracking the bullet-like plunge as the mountain crags blur past in terrifying speed, the bird tracking its target without flinching.",
        "eagle hurtles earthward in an arrowhead dive, adjusting its flight path with micro-twitches of its tail feathers",
        ANCHOR_AERIAL,
    )
    add_shot(
        "S55",
        "ch7_systemic_shift",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "At sixty feet, it flares its massive wings into airbrakes, thrusts its talons forward, and strikes with crushing kinetic force.",
        "Low-angle high-speed tracking shot as the eagle flares its broad wings mere feet above the heather moor.",
        "Pushing in as its immense yellow talons strike the target with instant, humane precision, sending heather dust flying.",
        "eagle flares its wings in a violent brake, driving its powerful talons forward into an explosive accurate strike",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S56",
        "ch7_systemic_shift",
        True,
        0.55,
        "Slow crane reveal across natural habitat",
        "The transformation is complete: the helpless, starving chick on the precipice has evolved into the supreme ruler of the alpine skies.",
        "Cinematic crane rising from the triumphant eagle standing proudly over its prize amidst the purple heather moors.",
        "Sweeping upward into the golden sunset illuminating the majestic Scottish mountains stretching across the breathtaking horizon.",
        "camera sweeps majestically upward from the eagle, revealing the boundless wilderness domain it now commands",
        ANCHOR_AERIAL,
    )

    # ==========================================
    # CHAPTER 8: ch8_resolution (S57..S64)
    # ==========================================
    # Group 1: The Evolutionary Lesson
    add_shot(
        "S57",
        "ch8_resolution",
        False,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "The terrifying cliffside crucible of the golden eagle reveals nature’s most profound rule: growth demands the total destruction of comfort.",
        "BBC Earth documentary conclusion: serene wide shot of the sheer granite cliff where the eyrie nest sits empty.",
        "Telephoto tracking shot across the weathered sticks of the abandoned nest, quiet under the soft golden alpine twilight.",
        "abandoned nest of weathered sticks rests silently in the twilight breeze on the high granite cliff ledge",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S58",
        "ch8_resolution",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "Had the mother continued to feed her fledgling in the nest, the chick would have grown heavy, weak, and ultimately perished.",
        "Intimate eye-level view of the narrow ledge where the young bird once stood frozen in absolute terror.",
        "Pushing in on the empty rock surface where lichen grows quietly, undisturbed by the struggles of the past.",
        "camera pushes in on the silent lichen-covered rock where the fledgling once gripped the cliff in terror",
        ANCHOR_CLIFF,
    )
    add_shot(
        "S59",
        "ch8_resolution",
        True,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "Only by facing the abyss, starving off excess weight, and risking total ruin could its magnificent latent potential be unlocked.",
        "Telephoto tracking shot following an eagle feather drifting weightlessly on the mountain thermal breeze above the canyon.",
        "Tracking the feather as it floats past towering vertical rock walls, bathed in the rich amber glow of setting sun.",
        "single golden eagle feather drifts gracefully on warm thermal air currents past monumental granite cliff faces",
        ANCHOR_AERIAL,
    )
    add_shot(
        "S60",
        "ch8_resolution",
        True,
        0.44,
        "Slow crane reveal across natural habitat",
        "Every creature on Earth, from birds to humans, must eventually confront its own cliff edge where safety must be abandoned.",
        "Cinematic crane shot looking down the dizzying three-thousand-foot precipice into the vast green valley below.",
        "Craning upward from the abyss toward the towering mountain summits glowing in brilliant alpine twilight.",
        "camera cranes smoothly from the dark depths of the gorge toward the radiant glowing mountain summits above",
        ANCHOR_AERIAL,
    )

    # Group 2: The Sovereign Monarch
    add_shot(
        "S61",
        "ch8_resolution",
        False,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "High above the rolling clouds, the young sovereign golden eagle now rides the ferocious hundred-mile-per-hour alpine thermals with effortless, supreme mastery.",
        "BBC Earth wildlife frame: glorious golden eagle soaring above a sea of fluffy white alpine clouds at ten thousand feet.",
        "Telephoto tracking shot flying alongside the majestic bird as its seven-foot wingspan cuts through the pristine mountain air.",
        "eagle glides serenely above a rolling sea of white clouds, golden sunlight gleaming off its brown plumage",
        ANCHOR_AERIAL,
    )
    add_shot(
        "S62",
        "ch8_resolution",
        True,
        0.36,
        "Intimate eye-level optical push-in",
        "What once was a terrifying void of death has become its boundless private kingdom, an endless playground of wind and light.",
        "Intimate optical tracking shot pushing in on the eagle's calm, majestic facial profile in smooth level flight.",
        "Pushing in as the bird tilts its head downward, surveying miles of mountain wilderness with complete, fearless serenity.",
        "eagle gazes down upon its mountain domain with sovereign calm, its amber eyes bright with absolute mastery",
        ANCHOR_BIOMECH,
    )
    add_shot(
        "S63",
        "ch8_resolution",
        True,
        0.36,
        "Telephoto 400mm shallow-DOF wildlife tracking shot",
        "It tilts its dark primary feathers, banking gracefully toward the setting sun as evening shadows fill the deep Scottish glens.",
        "Telephoto shot tracking the eagle as it banks toward the blazing crimson and gold horizon across the mountain peaks.",
        "Tracking the magnificent bird silhouetted against the colossal setting sun, carving majestic arcs into the evening sky.",
        "eagle banks into a graceful sweeping turn toward the setting sun, illuminated in brilliant golden rim light",
        ANCHOR_AERIAL,
    )
    add_shot(
        "S64",
        "ch8_resolution",
        True,
        0.55,
        "Slow crane reveal across natural habitat",
        "Forged in the merciless crucible of the alpine ridge, the golden eagle flies forever free, sovereign master of the skies.",
        "Grand BBC Earth finale crane shot pulling back into the vast Scottish Highland sky as dusk settles over the mountains.",
        "Sweeping into the infinite twilight firmament as the solitary eagle soars higher until it becomes a jewel in the sky.",
        "camera sweeps majestically backward and upward as the sovereign eagle soars higher into the twilight sky",
        ANCHOR_AERIAL,
    )

    return shots


def get_short_shots() -> list[dict[str, Any]]:
    # 7 shots, 13-15 words per shot, CTA in S07
    shots = [
        {
            "shot_id": "S01",
            "scene_group": "G1",
            "continues_prev": False,
            "scene_anchor": ANCHOR_CLIFF,
            "narration": "On a sheer three-thousand-foot Scottish cliff edge, an eagle mother abruptly stops feeding her chick.",
            "pause_after_sec": 0.35,
            "camera_verb": "Telephoto 400mm shallow-DOF wildlife tracking shot",
            "start_visual": "BBC Earth wildlife frame: sheer Highland granite precipice shrouded in swirling mist with fledgling calling from nest, strictly zero text.",
            "end_visual": "Telephoto push-in on the downy fledgling calling desperately from the sticks of the eyrie, strictly zero text.",
            "subject_motion": "fledgling paced frantically on the cliff edge calling with sharp juvenile cries",
        },
        {
            "shot_id": "S02",
            "scene_group": "G1",
            "continues_prev": True,
            "scene_anchor": ANCHOR_CLIFF,
            "narration": "She perches across the dizzying gulf, clutching fresh mountain prey just beyond its desperate reach.",
            "pause_after_sec": 0.35,
            "camera_verb": "Telephoto 400mm shallow-DOF wildlife tracking shot",
            "start_visual": "Adult golden eagle perched on granite pinnacle fifty yards across the yawning canyon abyss.",
            "end_visual": "Tracking the adult eagle tearing into game while deliberately withholding food from her starving fledgling, strictly zero text.",
            "subject_motion": "adult eagle tears into food across the chasm, ignoring the desperate calls of her chick",
        },
        {
            "shot_id": "S03",
            "scene_group": "G2",
            "continues_prev": False,
            "scene_anchor": ANCHOR_BIOMECH,
            "narration": "This is not cruelty; it is a calculated life-or-death biological necessity for maiden flight survival.",
            "pause_after_sec": 0.35,
            "camera_verb": "Intimate eye-level optical push-in",
            "start_visual": "Macro telephoto view of the chick's powerful breast muscles and developing dark flight quills, strictly zero text.",
            "end_visual": "Pushing in as the fledgling stretches its wings against howling wind currents rising from below, strictly zero text.",
            "subject_motion": "young eagle stretches its developing wings, testing aerodynamic wind resistance on the ledge",
        },
        {
            "shot_id": "S04",
            "scene_group": "G2",
            "continues_prev": True,
            "scene_anchor": ANCHOR_BIOMECH,
            "narration": "A well-fed heavy chick lacks sufficient pectoral lift and would crash directly into rocks.",
            "pause_after_sec": 0.35,
            "camera_verb": "Telephoto 400mm shallow-DOF wildlife tracking shot",
            "start_visual": "Vertical view looking down the three-thousand-foot cliff face to jagged talus boulders below.",
            "end_visual": "Tracking the chick's streamlined body as starvation burns off dead weight before the launch, strictly zero text.",
            "subject_motion": "fledgling shifts its weight forward on the extreme lip of the stone precipice",
        },
        {
            "shot_id": "S05",
            "scene_group": "G3",
            "continues_prev": False,
            "scene_anchor": ANCHOR_AERIAL,
            "narration": "Overwhelming hunger finally forces the terrified bird to leap forward into the roaring abyss.",
            "pause_after_sec": 0.35,
            "camera_verb": "Slow crane reveal across natural habitat",
            "start_visual": "Cinematic wide shot of the fledgling poised at the outermost edge of the cliff.",
            "end_visual": "Crane captures the fledgling stepping into empty space, plummeting five hundred feet in freefall, strictly zero text.",
            "subject_motion": "young eagle steps into the void, plummeting downward before locking its wings into a glide",
        },
        {
            "shot_id": "S06",
            "scene_group": "G3",
            "continues_prev": True,
            "scene_anchor": ANCHOR_AERIAL,
            "narration": "Its wings snap open, catching powerful thermal updrafts to soar sovereign across the glen.",
            "pause_after_sec": 0.35,
            "camera_verb": "Telephoto 400mm shallow-DOF wildlife tracking shot",
            "start_visual": "Young eagle flaring its seven-foot wingspan, pulling out of the dive mere yards above boulders.",
            "end_visual": "Tracking the bird soaring upward in a majestic climbing arc into sunlit alpine skies, strictly zero text.",
            "subject_motion": "young eagle swoops gracefully upward on rising thermals, mastering its very first flight",
        },
        {
            "shot_id": "S07",
            "scene_group": "G4",
            "continues_prev": False,
            "scene_anchor": ANCHOR_AERIAL,
            "narration": "Watch the full alpine expedition to witness how young eagles master hundred-mile-per-hour mountain thermals.",
            "pause_after_sec": 0.35,
            "camera_verb": "Slow crane reveal across natural habitat",
            "start_visual": "BBC Earth wide panorama of the sovereign eagle soaring above mist-shrouded Highland peaks.",
            "end_visual": "Grand crane pulling back into the golden sunset sky as the monarch claims its domain, strictly zero text.",
            "subject_motion": "camera sweeps upward into glorious golden sunset as the eagle glides sovereign over the wilderness",
        },
    ]
    return shots


def build_and_save() -> None:
    long_shots = get_long_shots()
    short_shots = get_short_shots()

    long_spec = {
        "job_id": "en-scale-and-bone-batch1-16x9",
        "channel_slug": "en-scale-and-bone",
        "aspect": "16:9",
        "title": "Apex of the Ridge: How a Fragile Golden Eagle Chick Masters 100-MPH Alpine Thermals",
        "youtube_title": "How Golden Eagle Chicks Survive the Ridge",
        "thumbnail_spec": {
            "visual_hook": "Macro wildlife frame of a golden eagle fledgling on a snow-dusted granite cliff edge facing a roaring alpine gale",
            "allowed_text": "FIRST LEAP",
            "overlay_card": False,
        },
        "voice": "en-GB-RyanNeural",
        "shots": long_shots,
    }

    short_spec = {
        "job_id": "en-scale-and-bone-batch1-9x16",
        "parent_long_id": "en-scale-and-bone-batch1-16x9",
        "channel_slug": "en-scale-and-bone",
        "aspect": "9:16",
        "title": "The First Leap: Why Eagle Mothers Stop Feeding Their Chicks on the Cliff Edge",
        "youtube_title": "Why Eagle Mothers Starve Their Chicks",
        "thumbnail_spec": {
            "visual_hook": "Intimate telephoto wildlife frame of adult eagle holding trout out of chick reach on sheer vertical granite abyss",
            "allowed_text": "HARSH LOVE",
            "overlay_card": False,
        },
        "voice": "en-GB-RyanNeural",
        "shots": short_shots,
    }

    print("Validating en-scale-and-bone Long...")
    validate_shots(long_shots, is_long=True)
    print("Validating en-scale-and-bone Short...")
    validate_shots(short_shots, is_long=False)

    p_long = OUT_DIR / "en-scale-and-bone_long_16x9.json"
    p_short = OUT_DIR / "en-scale-and-bone_short_9x16.json"

    p_long.write_text(json.dumps(long_spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    p_short.write_text(json.dumps(short_spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved: {p_long} and {p_short}")


if __name__ == "__main__":
    build_and_save()
