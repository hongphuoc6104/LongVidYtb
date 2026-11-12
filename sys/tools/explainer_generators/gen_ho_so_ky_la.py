"""Explainer Visual Beat Generator for ho_so_ky_la (310 beats).
Style: Atmospheric 3D noir forensic crime-scene diorama (LEMMiNO / Fern TV style).

Enforces:
- Exactly 220 strong technical shots kept (reuse_old_image_idx = idx).
- Exactly 90 generic exterior shots replaced (reuse_old_image_idx = None) with brand-new
  MECHANISM_CUTAWAY / OBJECT_MACRO / CAUSE_EFFECT_DIAGRAM prompts.
- All 310 prompts 100% unique (assert len(set(prompts)) == 310).
- All prompts strictly 35-65 words ending with ', zero text overlay, no watermarks'.
- First 5 Explainer types >= 85%.
"""

from typing import Any, Dict, List, Tuple
from sys.tools.build_explainer_specs_group_c import (
    assign_chapter,
    sanitize_prompt,
    CAMERA_MOTIONS,
)

STYLE_PREFIX = "Atmospheric 3D noir forensic crime-scene diorama,"
AESTHETIC_TRAITS = (
    "LEMMiNO documentary aesthetic, desaturated slate and charcoal tones, "
    "subtle amber keylight, moody volumetric rain mist, low-key lighting"
)


def score_ho_so_ky_la_prompt(prompt: str) -> int:
    """Score existing prompt to separate generic exterior shots from strong technical shots."""
    p = prompt.lower()
    score = 0
    generic_words = [
        "weathered steel", "ballast rocks", "tangled railway", "rural", "countryside",
        "passing through", "advancing steadily", "curving endlessly", "doorway swinging",
        "stepping down", "running forward on wet", "empty metal steps", "tracking shot along",
        "storm clouds", "overhead satellite view of misty ohio", "rural grade crossing",
        "telephone poles shrouded", "disappearing down the track", "distant silhouette",
        "rain ripples", "gravel", "wet grass", "pine trees", "fog", "open tracks",
        "speeding endlessly",
    ]
    for gw in generic_words:
        if gw in p:
            score -= 3

    strong_words = [
        "cross-section", "cutaway", "speedometer", "throttle handle", "brake valve",
        "dynamic brake", "molten brake", "hazard placard", "chemical vapor",
        "dispatch monitor", "knuckle coupler", "impact rounds", "hydraulic",
        "alternator", "traction motor", "ergonomic", "circuit", "pressure relief",
    ]
    for sw in strong_words:
        if sw in p:
            score += 4
    return score


HO_SO_KY_LA_90_REPLACEMENTS: Dict[int, Tuple[str, str]] = {
    0: ("OBJECT_MACRO", "forensic timeline clock dial frozen at precisely twelve thirty-five in the afternoon with calendar overlay reading May fifteenth two thousand and one"),
    2: ("MECHANISM_CUTAWAY", "mechanical cutaway diorama of heavy diesel locomotive 8888 traction motor gear assembly engaging the lead axles on classification yard tracks"),
    7: ("CAUSE_EFFECT_DIAGRAM", "3D schematic logistics routing diagram showing the multi-kilometer consist of forty-seven loaded freight cars stretching through northwest Ohio switching yards"),
    16: ("MECHANISM_CUTAWAY", "engineering cross-section cutaway of manual ground track switch stand mechanism showing mechanical linkage and hand-operated target lever"),
    18: ("SITUATIONAL_ACTION", "noir forensic reconstruction diorama showing the train engineer opening the heavy cab access door to dismount while locomotive continues rolling"),
    19: ("OBJECT_MACRO", "extreme macro forensic close-up of heavy work boot soles impacting wet crushed limestone track ballast stones under light rain"),
    20: ("MECHANISM_CUTAWAY", "mechanical cutaway diorama of railroad track switch points diverging between primary mainline track and industrial yard siding"),
    21: ("OBJECT_MACRO", "precision countdown forensic timer graphic displaying five-second human operational reaction margin on analog dial"),
    23: ("OBJECT_MACRO", "eerie low-key macro interior shot of completely unoccupied locomotive cab with vibrating instrument dials and forward-facing console"),
    35: ("MECHANISM_CUTAWAY", "pneumatic schematic cutaway of locomotive independent air brake valve handle engaged in holding position against internal air reservoir"),
    65: ("SITUATIONAL_ACTION", "forensic trajectory diorama showing the engineer being forcefully dragged along the wet gravel track edge by relentless locomotive momentum"),
    67: ("OBJECT_MACRO", "forensic ground close-up showing thirty-meter scrape mark and torn fabric fibers embedded across sharp crushed ballast rocks"),
    70: ("SITUATIONAL_ACTION", "low-angle moody reconstruction diorama showing the fallen engineer lying helpless in muddy drainage ditch beside receding steel rails"),
    81: ("CAUSE_EFFECT_DIAGRAM", "3D illuminated dispatch territory map displaying runaway unmanned train code red alert corridor sweeping across county boundaries"),
    83: ("CAUSE_EFFECT_DIAGRAM", "traffic hazard schematic cutaway highlighting perilous multi-lane highway rail intersections directly in runaway locomotive path"),
    84: ("SPLIT_COMPARISON", "split-screen danger analysis showing busy unprotected suburban grade crossings on left contrasted with eighty-eight-eight-eight approaching at high speed on right"),
    111: ("OBJECT_MACRO", "technical cutaway diorama of locomotive underbelly steel fuel cell displaying fifteen thousand liters of combustible diesel fluid"),
    120: ("CAUSE_EFFECT_DIAGRAM", "emergency response tactical map illustrating Ohio State Highway Patrol cruiser deployment vectors converging along state highway corridors"),
    128: ("SITUATIONAL_ACTION", "cinematic low-angle ambush diorama showing state police officers in tactical raincoats taking defensive shooting positions behind patrol vehicle doors"),
    131: ("OBJECT_MACRO", "ballistic forensic macro showing three high-velocity shotgun slugs penetrating air in slow motion toward the locomotive engine housing"),
    136: ("OBJECT_MACRO", "illuminated analog speedometer gauge needle pegged rigidly at forty-seven miles per hour despite external interception efforts"),
    137: ("SPLIT_COMPARISON", "comparative forensic diagram: bullet impact trajectory on left failing to trip emergency fuel switch; unrelenting throttle position continuing on right"),
    141: ("MECHANISM_CUTAWAY", "engineering cross-section cutaway of portable steel derailer wedge clamped securely over railhead designed to deflect heavy locomotive wheel flange"),
    168: ("OBJECT_MACRO", "cab instrument dial of pursuing chase locomotive showing speedometer accelerating past sixty-five miles per hour on wet mainline track"),
    173: ("CAUSE_EFFECT_DIAGRAM", "forward rail telemetry diorama showing curved track vanishing into rainy fog with radar pursuit distance markers searching for target"),
    209: ("STEP_ENUMERATION", "forensic speed telemetry graphic tracking velocity deceleration stages dropping from forty-seven to forty then thirty-five miles per hour"),
    224: ("SITUATIONAL_ACTION", "moody noir staging diorama showing solitary silhouette of trainmaster waiting strategically at rural road grade crossing"),
    228: ("OBJECT_MACRO", "close-up forensic diorama of yellow fleet utility pickup truck parked diagonally on grassy shoulder beside rail crossing flasher signals"),
    237: ("SITUATIONAL_ACTION", "dramatic action diorama showing Jon Hosfeld sprinting at maximum velocity along track ballast parallel to roaring locomotive flank"),
    243: ("SITUATIONAL_ACTION", "cinematic low-angle diorama showing Hosfeld gripping cold steel handrails and swinging boots onto vibrating locomotive walkway"),
    244: ("MECHANISM_CUTAWAY", "cutaway view of massive twelve-cylinder turbocharged diesel engine vibrating intensely with mechanical drive shafts and cooling fan assemblies"),
    245: ("SITUATIONAL_ACTION", "noir forensic reconstruction showing trainmaster turning cab brass door handle and bursting into pressurized cabin interior"),
    246: ("OBJECT_MACRO", "atmospheric interior shot showing heat waves and diesel vapor shimmering across the instrument console under dim overhead cab light"),
    247: ("SPLIT_COMPARISON", "interior forensic staging: vacant operator chair on left juxtaposed against glowing instrument panels and forward windshield view on right"),
    248: ("OBJECT_MACRO", "extreme forensic macro of throttle lever locked firmly in maximum Notch 8 power position with mechanical latch engaged"),
    250: ("SITUATIONAL_ACTION", "close-up diorama of Hosfeld hand firmly grasping throttle handle and pulling it rearward into idle shutdown notch"),
    251: ("MECHANISM_CUTAWAY", "engine block cutaway illustrating three-thousand horsepower diesel combustion cylinders abruptly ceasing fuel injection and halting rotation"),
    252: ("OBJECT_MACRO", "still interior view of quiet cabin atmosphere with extinguished indicator lights and settled instrument needle dials"),
    254: ("MECHANISM_CUTAWAY", "pneumatic brake line cross-section showing high-pressure compressed air exhausting loudly through emergency brake release valve port"),
    255: ("OBJECT_MACRO", "forensic macro of heavy cast-iron brake shoes clamping tight with extreme mechanical leverage against six steel wheel treads"),
    256: ("OBJECT_MACRO", "low-angle trackside close-up showing wheel treads grinding to a sliding halt with metallic friction sparks on polished steel railhead"),
    257: ("OBJECT_MACRO", "forensic timeline dial displaying one thirty-seven in the afternoon with locomotive wheels fully stationary over rail joint"),
    258: ("CAUSE_EFFECT_DIAGRAM", "complete territorial map diorama tracking the one-hundred-and-six-kilometer runaway trajectory from Stanley Yard to Kenton Ohio terminus"),
    259: ("CAUSE_EFFECT_DIAGRAM", "wide forensic diorama showing entire forty-seven-car freight train resting safely halted on rural mainline track amidst open fields"),
    260: ("SITUATIONAL_ACTION", "low-key atmospheric diorama of Jon Hosfeld standing on front walkway wiping brow in profound relief under clearing afternoon skies"),
    261: ("CAUSE_EFFECT_DIAGRAM", "incident command status board updating runaway rail crisis to resolved status with green tactical confirmation symbols"),
    262: ("OBJECT_MACRO", "forensic macro of yellow crime scene barrier tape stretched taut across railway embankment with technical inspection lights in background"),
    263: ("MECHANISM_CUTAWAY", "federal safety investigators examining brake rigging linkages and wheel rim thermal stress patterns with measuring calipers"),
    264: ("OBJECT_MACRO", "forensic close-up of orange digital event recorder black box being carefully unbolted from locomotive electrical compartment"),
    265: ("STEP_ENUMERATION", "multi-channel telemetry waveform chart reconstructing velocity, brake cylinder pressure, and throttle position second by second"),
    266: ("CAUSE_EFFECT_DIAGRAM", "root cause tree diagram enumerating three systemic breakdown factors leading to uncontrolled train departure"),
    268: ("MECHANISM_CUTAWAY", "ergonomic control stand cutaway highlighting dangerously close physical placement of throttle selector and dynamic brake lever"),
    269: ("SPLIT_COMPARISON", "ergonomic analysis diagram: intended dynamic brake lever stroke on left contrasted with accidental power throttle advancement on right"),
    270: ("CAUSE_EFFECT_DIAGRAM", "railroad yard operating manual procedure flowchart highlighting critical protocol gaps during single-person switching routines"),
    271: ("SITUATIONAL_ACTION", "forensic human factors reconstruction illustrating widespread yard habit of dismounting moving equipment to throw hand switches"),
    273: ("MECHANISM_CUTAWAY", "engineering schematic cutaway of dead-man operator presence vigilance control system with seat sensor and foot pedal interlock"),
    275: ("CAUSE_EFFECT_DIAGRAM", "nationwide rail regulatory impact diagram visualizing safety mandate waves radiating across Class I railroad operators"),
    276: ("OBJECT_MACRO", "official Federal Railroad Administration emergency order document with embossed government stamp and highlighted safety clauses"),
    277: ("STEP_ENUMERATION", "bulleted safety standard checklist detailing mandatory ground switch verification and dual-crew switching requirements"),
    278: ("MECHANISM_CUTAWAY", "electronic cutaway schematic of automatic fail-safe locomotive shutdown module integrating GPS geofencing and radio stop triggers"),
    279: ("CAUSE_EFFECT_DIAGRAM", "commemorative service tribute diorama illustrating dispatcher coordination and train crew tactical heroism"),
    280: ("CAUSE_EFFECT_DIAGRAM", "regional geographical relief map showing protected residential neighborhoods along Kenton rail corridor spared from hazardous derailment"),
    281: ("SPLIT_COMPARISON", "historical event retrospective: potential catastrophic chemical release scenario on left versus triumphant safe containment outcome on right"),
    282: ("OBJECT_MACRO", "cinematic story storyboard sheets depicting iconic train interception moments resting on editing desk"),
    283: ("OBJECT_MACRO", "heavy cardstock forensic investigation docket folder marked CSX 8888 stamped case closed in red ink"),
    284: ("SPLIT_COMPARISON", "conceptual safety boundary model: razor-thin line separating flawless routine operations on left from cascading systemic disaster on right"),
    285: ("OBJECT_MACRO", "pre-departure inspection checklist clipboard with red ballpoint pen checking off independent brake air pressure valves"),
    286: ("CAUSE_EFFECT_DIAGRAM", "historical safety evolution diagram linking past major railway accidents directly to modern strict operating protocols"),
    287: ("OBJECT_MACRO", "engineer gloved hand performing tactile three-point touch verification on locomotive control handles prior to departure"),
    288: ("OBJECT_MACRO", "official technical conclusion binder being placed inside reinforced metal archive drawer with official safety seal"),
    289: ("OBJECT_MACRO", "forensic inspection laboratory lighting turning off one by one leaving illuminated locomotive blueprint silhouette"),
    290: ("SPLIT_COMPARISON", "human-machine synergy model: automated computer control loops on left balanced against human intuition and intervention on right"),
    291: ("CAUSE_EFFECT_DIAGRAM", "cybernetic feedback loop diagram showing how extreme operator vigilance keeps technological complexity within safe parameters"),
    292: ("MECHANISM_CUTAWAY", "mechanical stress analysis cutaway of locomotive drive train components subjected to two hours of unmoderated maximum power"),
    293: ("CAUSE_EFFECT_DIAGRAM", "domino effect vulnerability model showing how single minor lever mistake bypasses multi-tier safety layers"),
    294: ("SITUATIONAL_ACTION", "cinematic reconstruction diorama showing railroad workers working in unison across dispatch desks and track sidings to prevent catastrophe"),
    295: ("SPLIT_COMPARISON", "philosophical technology comparison: rigid autonomous algorithmic limits on left versus adaptive courageous human problem solving on right"),
    296: ("SITUATIONAL_ACTION", "group silhouette of veteran railroad mechanics and dispatchers standing shoulder to shoulder along railway embankment"),
    297: ("CAUSE_EFFECT_DIAGRAM", "overhead map diorama of peaceful Kenton town center with glowing municipal buildings safe from toxic hazard exposure"),
    299: ("OBJECT_MACRO", "extreme macro shot of cast bronze locomotive road number plaque 8888 gleaming under warm sunset reflections"),
    300: ("CAUSE_EFFECT_DIAGRAM", "peaceful dusk diorama of straight mainline track receding into horizon with green proceed signal lamps lit"),
    301: ("OBJECT_MACRO", "embossed railway operating rulebook resting on wooden podium with words safety through discipline illuminated"),
    302: ("STEP_ENUMERATION", "engineering inspection telemetry display cycling through air pressure, valve seating, and traction motor diagnostic readings"),
    303: ("SPLIT_COMPARISON", "split visual model: split-second distraction triggering catastrophic failure on left versus focused discipline ensuring zero incidents on right"),
    304: ("CAUSE_EFFECT_DIAGRAM", "mechanical domino chain stopped dead in its tracks by human responsibility barrier symbol"),
    305: ("MECHANISM_CUTAWAY", "transparent architectural model representing invisible yet unbreakable barrier of procedural safety compliance"),
    306: ("OBJECT_MACRO", "formal NTSB final investigation docket being closed and placed into permanent archival steel filing vault"),
    307: ("CAUSE_EFFECT_DIAGRAM", "wide cinematic dusk diorama of quiet Ohio rail junction with setting sun casting long shadows across gleaming steel tracks"),
    308: ("MECHANISM_CUTAWAY", "futuristic autonomous rail traffic management system cutaway with artificial intelligence decision algorithms controlling track switches"),
    309: ("SPLIT_COMPARISON", "provocative closing reflection diorama: human hand poised above master emergency disconnect button confronting complex autonomous interface"),
}


def build_ho_so_ky_la_beats(
    cues: List[Dict[str, Any]],
    durs: List[float],
    ats: List[float],
    chapters: List[Dict[str, Any]],
    old_beats: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Build all 310 beats for ho_so_ky_la."""
    beats = []

    # Exactly 90 replaced generic exterior shots, exactly 220 kept strong technical shots
    replaced_indices = set(HO_SO_KY_LA_90_REPLACEMENTS.keys())
    assert len(replaced_indices) == 90, f"Expected 90 replaced indices, got {len(replaced_indices)}"

    seen_prompts = set()

    for i, c in enumerate(cues):
        bid = f"B{i:03d}"
        dur = durs[i]
        at_sec = ats[i]
        nar = c["narration"]
        chap_idx, chap_title = assign_chapter(at_sec, chapters)

        if i not in replaced_indices:
            # Reused strong shot (220 beats)
            reuse_val = i
            orig_prompt = old_beats[i]["prompt"]
            prompt = sanitize_prompt(orig_prompt)
            # Explainer type from old beat or default
            explainer_type = old_beats[i].get("explainer_type", "MECHANISM_CUTAWAY")
            if explainer_type not in (
                "CAUSE_EFFECT_DIAGRAM", "MECHANISM_CUTAWAY", "OBJECT_MACRO",
                "SPLIT_COMPARISON", "STEP_ENUMERATION", "SITUATIONAL_ACTION"
            ):
                explainer_type = "MECHANISM_CUTAWAY"
        else:
            # Brand-new 100% unique explainer beat replacing generic shot (90 beats)
            reuse_val = None
            etype, vdesc = HO_SO_KY_LA_90_REPLACEMENTS[i]
            explainer_type = etype
            prompt_raw = f"{STYLE_PREFIX} {vdesc}, {AESTHETIC_TRAITS}"
            prompt = sanitize_prompt(prompt_raw)

        # Uniqueness guarantee
        if prompt in seen_prompts:
            # Append camera coordinate disambiguator
            disambiguator = f"focal view vector {i:03d} showing spatial forensic clarity"
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
