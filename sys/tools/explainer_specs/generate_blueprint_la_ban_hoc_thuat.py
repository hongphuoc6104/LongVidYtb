"""Generate bespoke 157 blueprints for la_ban_hoc_thuat with 100% unique core subjects."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent

# 157 explicit bespoke entries for la_ban_hoc_thuat: idx -> (etype, scene_description)
# Every scene_description starts with a unique subject noun phrase so scene[:60].lower() is unique.
ENTRIES = {
    0: ("CAUSE_EFFECT_DIAGRAM", "cognitive paradox coordinate plane contrasting perceived learning volume against actual recall retention"),
    1: ("SPLIT_COMPARISON", "split-screen comparison contrasting a massive thick textbook on the left against fragile mental retention nodes"),
    3: ("OBJECT_MACRO", "fluorescent neon yellow highlighter marker aggressively illuminating entire printed page paragraphs"),
    5: ("SPLIT_COMPARISON", "split-screen comparison contrasting active hand highlighter motion against dormant unengaged synaptic pathways"),
    6: ("CAUSE_EFFECT_DIAGRAM", "harsh reality divergence graph showing retention crashing down while confidence remains falsely elevated"),
    8: ("OBJECT_MACRO", "blank summary notepad where a student hand hesitates unable to write a single core thesis"),
    9: ("MECHANISM_CUTAWAY", "cognitive failure mechanism cutaway diagram dissecting why passive reading fails to form long-term synaptic connections"),
    11: ("SPLIT_COMPARISON", "split-screen comparison contrasting effortless eye tracking over text against genuine deep cognitive synthesis"),
    12: ("MECHANISM_CUTAWAY", "illusion of competence diagram illustrating surface familiarity masking deep conceptual voids"),
    14: ("CAUSE_EFFECT_DIAGRAM", "surface familiarity dissolution chart showing fragile confidence collapsing during verbal articulation"),
    15: ("OBJECT_MACRO", "digital smartphone feed with endless saved bookmark icons creating a false illusion of accumulated knowledge"),
    17: ("SPLIT_COMPARISON", "split-screen comparison contrasting casual recognition of an idea against genuine intellectual ownership"),
    19: ("STEP_ENUMERATION", "cognitive breakthrough roadmap diagram laying out four structured steps to shatter passive learning illusions"),
    22: ("OBJECT_MACRO", "historical portrait sketch of Hermann Ebbinghaus surrounded by mathematical memory data tables"),
    23: ("CAUSE_EFFECT_DIAGRAM", "memory decay velocity measurement chart plotting retention percentage against elapsed hours"),
    24: ("CAUSE_EFFECT_DIAGRAM", "mathematical coordinate plot of the Ebbinghaus forgetting curve tracing steep exponential memory drop"),
    26: ("CAUSE_EFFECT_DIAGRAM", "precipitous memory drop graph showing immediate post-learning retention plummeting violently"),
    27: ("OBJECT_MACRO", "twenty-minute digital stopwatch timer highlighting the critical initial memory degradation window"),
    29: ("MECHANISM_CUTAWAY", "short-term memory buffer cutaway showing fifty percent of newly encoded data packets evaporating"),
    30: ("OBJECT_MACRO", "twenty-four hour calendar block graphic illustrating seventy percent information loss after one day"),
    32: ("OBJECT_MACRO", "fragmented memory shards floating disconnected in dark obsidian cognitive space after a full day"),
    33: ("CAUSE_EFFECT_DIAGRAM", "thirty-day memory baseline graph showing retention flatlining near zero without deliberate review"),
    35: ("CAUSE_EFFECT_DIAGRAM", "biological exoneration model proving rapid forgetting stems from natural evolutionary pruning rather than bad memory"),
    36: ("MECHANISM_CUTAWAY", "evolutionary survival filter cutaway prioritizing immediate physical threat data over abstract facts"),
    38: ("MECHANISM_CUTAWAY", "brain metabolic energy conservation engine actively pruning unreferenced neural synapses"),
    40: ("STEP_ENUMERATION", "strategic persuasion protocol diagram convincing the subconscious brain that studied facts are vital"),
    42: ("SPLIT_COMPARISON", "split-screen comparison contrasting futile repetitive rereading against high-yield active self-testing"),
    44: ("STEP_ENUMERATION", "active recall foundational diagram detailing the mental mechanics of pulling knowledge out from memory"),
    46: ("MECHANISM_CUTAWAY", "cognitive wiring schematic showing how retrieval practice transforms transient sparks into deep neural roots"),
    47: ("OBJECT_MACRO", "firm hand closing a textbook cover completely to force independent memory retrieval practice"),
    49: ("OBJECT_MACRO", "blank white paper canvas receiving handwritten core principles retrieved entirely from internal memory"),
    50: ("CAUSE_EFFECT_DIAGRAM", "mental cognitive friction meter indicating the intense neurological effort required during active recall"),
    52: ("CAUSE_EFFECT_DIAGRAM", "desirable difficulty curve demonstrating that greater retrieval strain produces dramatically stronger memory traces"),
    53: ("MECHANISM_CUTAWAY", "synaptic consolidation cutaway diagram showing dendritic spines thickening under active retrieval effort"),
    55: ("CAUSE_EFFECT_DIAGRAM", "fivefold retention multiplier bar chart comparing active recall performance against standard rereading"),
    56: ("OBJECT_MACRO", "laboratory research clipboard documenting empirical cognitive science study trials across student cohorts"),
    58: ("SPLIT_COMPARISON", "split-screen comparison showing testing-group exam scores towering over passive review student results"),
    59: ("CAUSE_EFFECT_DIAGRAM", "inverse retrieval effort law diagram proving that harder cognitive retrieval yields exponentially longer retention"),
    61: ("MECHANISM_CUTAWAY", "cognitive landfill cutaway illustrating effortless shallow inputs being dumped instantly by working memory"),
    62: ("OBJECT_MACRO", "crisp blank sheet of white paper ready for unfiltered memory dump and knowledge mapping"),
    64: ("OBJECT_MACRO", "diagnostic gap analysis sheet highlighting missing conceptual nodes and broken logical arguments"),
    66: ("STEP_ENUMERATION", "habitual retrieval reflex loop diagram embedding active self-quizzing into daily study routines"),
    68: ("MECHANISM_CUTAWAY", "deep intellectual root system anchoring abstract formulas into permanent long-term cognitive bedrock"),
    70: ("OBJECT_MACRO", "colorful fluorescent highlighter pen array lying crossed out on an open study notebook"),
    72: ("CAUSE_EFFECT_DIAGRAM", "pseudo-productivity illusion trap diagram mapping visual busyness against near-zero critical thinking"),
    73: ("CAUSE_EFFECT_DIAGRAM", "highlighter hazard vulnerability flowchart detailing how bright ink tricks the brain into passive complacency"),
    75: ("MECHANISM_CUTAWAY", "visual cortex stimulation cutaway showing bright ink activating visual pathways while conceptual circuits sleep"),
    76: ("SPLIT_COMPARISON", "split-screen comparison contrasting mindless transcription copying against active question-driven note taking"),
    78: ("CAUSE_EFFECT_DIAGRAM", "mechanical hand transcription diagram training motor reflexes while bypassing analytical comprehension"),
    79: ("OBJECT_MACRO", "educational science research meta-analysis paper rating highlighting as the least effective study technique"),
    81: ("OBJECT_MACRO", "wasted study hours graph illustrating endless weekend highlighting yielding near-zero test retention"),
    82: ("CAUSE_EFFECT_DIAGRAM", "fluency illusion deception model showing smooth textual reading masking underlying incomprehension"),
    84: ("SITUATIONAL_ACTION", "student sitting frozen at an exam desk staring at a blank test paper with sudden realization"),
    85: ("STEP_ENUMERATION", "three-tier intelligent note-taking methodology replacing passive summaries with generative synthesis"),
    87: ("SPLIT_COMPARISON", "split-screen comparison contrasting rambling technical jargon against clear simple language child explanation"),
    88: ("OBJECT_MACRO", "Cornell study notebook layout featuring a left column dedicated entirely to self-testing prompt questions"),
    90: ("CAUSE_EFFECT_DIAGRAM", "cognitive depth gradient pyramid showing question-driven notes outperforming rote transcription"),
    92: ("OBJECT_MACRO", "bold hand deliberately capping and packing away colorful highlighters into a pencil case"),
    94: ("CAUSE_EFFECT_DIAGRAM", "cognitive ease trap diagram showing that comfortable effortless study produces fragile perishable learning"),
    96: ("STEP_ENUMERATION", "spaced repetition schedule master timeline spacing reviews across expanding calendar intervals"),
    98: ("MECHANISM_CUTAWAY", "spaced repetition engine cutaway showing timed retrieval pulses flattening the steep decay slope"),
    100: ("CAUSE_EFFECT_DIAGRAM", "forgetting curve transformation diagram showing exponential decay turning into a permanent plateau"),
    101: ("SPLIT_COMPARISON", "split-screen comparison contrasting frantic pre-exam cramming against calm spaced review cycles"),
    103: ("CAUSE_EFFECT_DIAGRAM", "cramming rapid evaporation curve showing post-exam retention crashing to absolute zero within 48 hours"),
    104: ("STEP_ENUMERATION", "fractional study cycle calendar dividing curriculum into bite-sized daily spaced repetition units"),
    106: ("STEP_ENUMERATION", "expanding review interval sequence diagram detailing review sessions at day one, three, seven, and thirty"),
    107: ("OBJECT_MACRO", "golden review timing clock showing the precise moment memory begins to fade as optimal study time"),
    109: ("MECHANISM_CUTAWAY", "neural retrieval pulse cutaway diagram rescuing a fading memory trace right at the brink of oblivion"),
    110: ("OBJECT_MACRO", "urgent priority signal beacon flashing inside a neural network node demanding permanent storage"),
    112: ("MECHANISM_CUTAWAY", "long-term cognitive vault cutaway locking consolidated concepts into myelinated neural circuits"),
    113: ("OBJECT_MACRO", "wooden Leitner box apparatus featuring five distinct compartment slots for spaced card review"),
    114: ("STEP_ENUMERATION", "Leitner card promotion protocol diagram moving mastered flashcards to wider review intervals"),
    116: ("CAUSE_EFFECT_DIAGRAM", "fifty percent time savings comparison chart demonstrating how Leitner spacing cuts total study hours"),
    118: ("SITUATIONAL_ACTION", "confident learner reviewing flashcards calmly on a park bench completely free from exam anxiety"),
    120: ("STEP_ENUMERATION", "daily micro-discipline habit loop linking ten minutes of card reviews to morning routine"),
    122: ("CAUSE_EFFECT_DIAGRAM", "exponential cognitive compound interest graph tracking small daily reviews yielding massive mastery"),
    124: ("STEP_ENUMERATION", "Feynman verification diagnostic protocol testing genuine conceptual understanding through explanation"),
    126: ("OBJECT_MACRO", "blackboard diagram sketch of Richard Feynman explaining quantum electrodynamics with simple diagrams"),
    128: ("OBJECT_MACRO", "Niklas Luhmann massive publication bibliography tallying seventy books and four hundred academic papers"),
    129: ("MECHANISM_CUTAWAY", "Zettelkasten card index cabinet cutaway revealing interconnected wooden drawers of atomic notes"),
    130: ("SPLIT_COMPARISON", "split-screen comparison contrasting fallible biological memory against reliable external Zettelkasten card filing"),
    132: ("MECHANISM_CUTAWAY", "Zettelkasten internal workflow architecture detailing note capture, atomic refactoring, and bidirectional linking"),
    134: ("OBJECT_MACRO", "crisp paper index card containing a single atomic idea written in clear self-contained sentences"),
    135: ("SPLIT_COMPARISON", "split-screen comparison contrasting rigid folder silos against dynamic interconnected card graph nodes"),
    137: ("CAUSE_EFFECT_DIAGRAM", "knowledge isolation hazard diagram showing rigid category folders blocking interdisciplinary insight"),
    138: ("MECHANISM_CUTAWAY", "associative neural network architecture diagram modeling human memory as an interconnected mesh"),
    140: ("MECHANISM_CUTAWAY", "multidimensional concept spiderweb graph connecting disparate intellectual nodes across disciplines"),
    141: ("OBJECT_MACRO", "alphanumeric index card address numbering format like 1.1a branching between existing notes"),
    143: ("STEP_ENUMERATION", "branching note insertion sequence diagram nesting a new breakthrough idea between two established cards"),
    144: ("CAUSE_EFFECT_DIAGRAM", "network density multiplier curve showing value increasing exponentially with every new card connection"),
    146: ("MECHANISM_CUTAWAY", "living intellectual nervous system map reflecting the evolving cognitive landscape of the researcher"),
    147: ("OBJECT_MACRO", "glowing concept seed sprouting new cross-disciplinary branches across a digital knowledge canvas"),
    149: ("MECHANISM_CUTAWAY", "intellectual collision spark diagram generating novel insights where two unrelated disciplines intersect"),
    150: ("SPLIT_COMPARISON", "split-screen comparison contrasting static card storage against an interactive conversational thinking partner"),
    152: ("CAUSE_EFFECT_DIAGRAM", "autocatalytic knowledge growth feedback loop demonstrating ideas generating further questions autonomously"),
    154: ("STEP_ENUMERATION", "deep self-directed learning cycle diagram moving from curating knowledge to publishing original work"),
    156: ("CAUSE_EFFECT_DIAGRAM", "collector trap illusion diagnostic diagram warning against hoarding unread digital books and papers"),
    157: ("OBJECT_MACRO", "towering stacks of unread physical books and unread PDF downloads creating false intellectual security"),
    159: ("SPLIT_COMPARISON", "split-screen comparison contrasting a passive warehouse brain against an active creative workshop mind"),
    160: ("CAUSE_EFFECT_DIAGRAM", "document hoarding anxiety loop showing excessive collecting paralyzing creative output"),
    162: ("CAUSE_EFFECT_DIAGRAM", "passive learning dead-end diagram showing non-interactive reading leading straight to zero retention"),
    164: ("MECHANISM_CUTAWAY", "overnight synaptic pruning cutaway showing unexercised memory traces dissolving completely during sleep"),
    165: ("STEP_ENUMERATION", "applied knowledge action cycle diagram requiring every learned concept to be deployed in real projects"),
    167: ("MECHANISM_CUTAWAY", "real-world problem solving apparatus channeling theoretical knowledge into concrete engineering solutions"),
    168: ("STEP_ENUMERATION", "project-based learning execution framework guiding the creation of tangible intellectual deliverables"),
    170: ("OBJECT_MACRO", "crisp two-page executive analytical brief summarizing complex academic findings for workplace utility"),
    171: ("OBJECT_MACRO", "fountain pen nib gliding across textured paper sharpening vague thoughts into crystalline logic"),
    173: ("SPLIT_COMPARISON", "split-screen comparison contrasting muddled mental fog against razor-sharp written paragraphs on paper"),
    174: ("OBJECT_MACRO", "clean geometric concept flowchart sketch turning complex theoretical text into clear structural nodes"),
    176: ("MECHANISM_CUTAWAY", "structural logic bottleneck analysis diagram exposing flawed assumptions hidden by superficial reading"),
    177: ("SPLIT_COMPARISON", "split-screen comparison contrasting isolated solitary study against presenting ideas to a peer critique group"),
    179: ("CAUSE_EFFECT_DIAGRAM", "peer scrutiny pressure curve driving the student to investigate foundational axioms deeply"),
    180: ("SITUATIONAL_ACTION", "confident intellectual speaker standing before a chalkboard sharing synthesized knowledge with clarity"),
    182: ("MECHANISM_CUTAWAY", "brain operating mode transition diagram switching from receptive intake to active generative synthesis"),
    184: ("STEP_ENUMERATION", "rigorous critical inquiry framework testing hypotheses against empirical counterexamples"),
    186: ("MECHANISM_CUTAWAY", "deep work neuro-cognitive focus chamber shielding mental processes from environmental noise"),
    188: ("MECHANISM_CUTAWAY", "peak cognitive processing engine operating at maximum mental throughput on difficult problems"),
    189: ("OBJECT_MACRO", "digital notification badge array pinging incessantly and fragmenting executive attention"),
    191: ("CAUSE_EFFECT_DIAGRAM", "cognitive fragmentation scatter plot showing notification interruptions shattering continuous focus chains"),
    192: ("CAUSE_EFFECT_DIAGRAM", "distraction penalty economic cost chart quantifying lost productive output from constant checking"),
    194: ("SPLIT_COMPARISON", "split-screen comparison contrasting multitasking myth against neurological reality of task switching penalty"),
    195: ("MECHANISM_CUTAWAY", "attention residue cognitive diagram showing mental bandwidth stuck on prior uncompleted tasks"),
    197: ("SPLIT_COMPARISON", "split-screen comparison showing physical presence at desk while subconscious attention lingers on phone notifications"),
    198: ("OBJECT_MACRO", "twenty-three minute recovery stopwatch timer required to regain deep focus after a minor distraction"),
    200: ("CAUSE_EFFECT_DIAGRAM", "shallow learning loop diagram proving that frequent device checks prevent reaching flow state entirely"),
    201: ("MECHANISM_CUTAWAY", "protective digital fortress boundary wall shielding the study desk from online distraction sources"),
    203: ("STEP_ENUMERATION", "study environment optimization checklist eliminating digital friction, background noise, and clutter"),
    204: ("OBJECT_MACRO", "minimalist wooden study desk equipped only with one book, a notebook, and a single pen"),
    206: ("OBJECT_MACRO", "smartphone sealed securely inside an opaque lockbox placed in another room during study"),
    208: ("OBJECT_MACRO", "classic analog Pomodoro timer dial set to twenty-five minutes of uninterrupted focused effort"),
    210: ("OBJECT_MACRO", "twenty-five minute countdown progress bar glowing in electric cyan during deep concentration"),
    212: ("OBJECT_MACRO", "five-minute rejuvenation tea cup beside a quiet window representing restorative mindful rest"),
    214: ("MECHANISM_CUTAWAY", "digital cognitive leverage architecture augmenting human intellect with modern software tools"),
    216: ("MECHANISM_CUTAWAY", "second brain digital architecture diagram syncing markdown notes, flashcards, and graph views"),
    217: ("SPLIT_COMPARISON", "split-screen comparison contrasting overburdened biological memory against light liberated creative mind"),
    219: ("CAUSE_EFFECT_DIAGRAM", "cognitive load reduction curve showing externalizing knowledge storage freeing ninety percent working memory"),
    220: ("STEP_ENUMERATION", "automated spaced repetition habit loop surfacing review cards right at the optimal retrieval moment"),
    222: ("OBJECT_MACRO", "smart digital flashcard surfacing automatically on screen seconds before predicted memory expiration"),
    223: ("CAUSE_EFFECT_DIAGRAM", "optimized study efficiency trajectory cutting exam preparation duration by more than half"),
    225: ("SPLIT_COMPARISON", "split-screen comparison contrasting targeted weak-point drilling against redundant study of mastered facts"),
    226: ("MECHANISM_CUTAWAY", "living digital knowledge graph expanding dynamically with colorful interconnected topic clusters"),
    228: ("OBJECT_MACRO", "multidimensional spiderweb concept graph rotating smoothly on an obsidian screen display"),
    229: ("OBJECT_MACRO", "bright intellectual spark bridging two distant clusters on a concept graph igniting a new project"),
    231: ("MECHANISM_CUTAWAY", "accumulated intellectual bedrock foundation supporting ambitious creative and career ventures"),
    232: ("SPLIT_COMPARISON", "split-screen comparison contrasting solitary study struggles against intelligent conversational AI tutoring"),
    234: ("STEP_ENUMERATION", "Socratic dialectic question-and-answer protocol testing conceptual understanding to its core"),
    236: ("OBJECT_MACRO", "radar chart highlighting conceptual blind spots and logical fallacies for immediate remediation"),
    238: ("MECHANISM_CUTAWAY", "real-time intellectual feedback loop correcting misconceptions before they calcify into bad habits"),
    240: ("SITUATIONAL_ACTION", "autonomous scholar looking out toward an illuminated horizon with quiet intellectual self-reliance"),
    242: ("MECHANISM_CUTAWAY", "intellectual liberation engine empowering the individual to master any complex domain independently"),
    243: ("STEP_ENUMERATION", "twenty-first century core survival skills pyramid placing autonomous meta-learning at the peak"),
    245: ("CAUSE_EFFECT_DIAGRAM", "academic knowledge obsolescence curve showing static university curricula decaying rapidly over time"),
    246: ("SPLIT_COMPARISON", "split-screen comparison contrasting rigid obsolete graduates against agile adaptable self-learners"),
    248: ("SITUATIONAL_ACTION", "adaptable self-taught professional mastering a brand new complex discipline starting from ground zero"),
    249: ("CAUSE_EFFECT_DIAGRAM", "lifelong learning acceleration curve proving neuroplasticity enables rapid mastery at any life stage"),
    251: ("STEP_ENUMERATION", "four-step Feynman technique summary card: choose concept, explain simply, find gaps, and refine"),
    253: ("OBJECT_MACRO", "luminous cognitive key unlocking a radiant golden doorway to boundless intellectual potential"),
}


def build_blueprint_la_ban_hoc_thuat():
    cues = json.loads(Path("/tmp/new_cues_la_ban_hoc_thuat.json").read_text())
    cue_indices = [c["idx"] for c in cues]

    assert len(ENTRIES) == len(cue_indices), f"Entries count {len(ENTRIES)} != cues count {len(cue_indices)}"
    assert set(ENTRIES.keys()) == set(cue_indices), f"Mismatch in keys: {set(cue_indices) - set(ENTRIES.keys())}"

    # Verify cores uniqueness
    cores = [desc[:60].lower() for _, desc in ENTRIES.values()]
    assert len(set(cores)) == len(cores), f"Duplicate cores found: {len(set(cores))}/{len(cores)}"

    # Generate blueprint python code
    lines = [
        '"""Bespoke 157 Explainer Blueprints for la_ban_hoc_thuat (157 new beats).',
        "",
        "Maps every new cue index in la_ban_hoc_thuat to bespoke (explainer_type, scene_description)",
        "so that every prompt directly translates and explains its Vietnamese sentence.",
        '"""',
        "",
        "from typing import Dict, Tuple",
        "",
        "LA_BAN_HOC_THUAT_BESPOKE_157: Dict[int, Tuple[str, str]] = {",
    ]

    for idx in sorted(ENTRIES.keys()):
        etype, desc = ENTRIES[idx]
        desc_esc = desc.replace('"', '\\"')
        lines.append(f'    {idx}: ("{etype}", "{desc_esc}"),')

    lines.append("}")
    lines.append("")

    out_file = ROOT / "sys" / "tools" / "explainer_specs" / "blueprint_la_ban_hoc_thuat.py"
    out_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {out_file} with {len(ENTRIES)} bespoke entries. Cores 100% unique!")


if __name__ == "__main__":
    build_blueprint_la_ban_hoc_thuat()
