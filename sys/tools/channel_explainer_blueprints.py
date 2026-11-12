"""
Channel Explainer Blueprints for Group A (5 Science Channels).
Provides rich semantic concept mappers and concrete visual prompt cores
for every cue in co_the_ke, dia_com, nao_luoi, ua_sao_vay, and vu_tru_ti_hon.
"""

from typing import Tuple


def get_cue_explainer_co_the_ke(cue_idx: int, text: str, chap_idx: int) -> Tuple[str, str]:
    t = text.lower()
    
    if chap_idx == 1:
        if cue_idx == 0:
            return "OBJECT_MACRO", "Extreme macro focus on heavy drooping human eyelids struggling under midnight exhaustion, microscopic orbicularis oculi muscle fibers under subtle cold blue luminescence"
        if cue_idx == 1:
            return "MECHANISM_CUTAWAY", "Anatomical cross-section through human eye showing harsh 480nm blue photon rays penetrating pupil and striking fatigued retinal photoreceptors"
        if cue_idx == 2:
            return "SITUATIONAL_ACTION", "Minimalist dark bedroom setting with clock silhouette and cold smartphone screen glow casting long shadows across clean empty space"
        if cue_idx == 3:
            return "SITUATIONAL_ACTION", "Illuminated smartphone screen hovering in dark space displaying video player interface and scrolling notification feed"
        if cue_idx == 4:
            return "OBJECT_MACRO", "Macro focus on mechanical wall clock dial with glowing hands crossing the 3 AM mark in deep midnight blue environment"
        if cue_idx == 5:
            return "OBJECT_MACRO", "Extreme macro of hyperemic capillary network swelling across the sclera of human eye with microscopic inflammation micro-droplets"
        if cue_idx == 6:
            return "MECHANISM_CUTAWAY", "Microscopic cross-section of corneal epithelial surface showing lipid tear film breaking and evaporating, exposing bare sensory nerve endings"
        if cue_idx == 7:
            return "MECHANISM_CUTAWAY", "Translucent anatomical rendering of human cranium highlighting glowing red pulsing pain pathways along temporalis muscle and trigeminal nerve"
        if cue_idx == 8:
            return "MECHANISM_CUTAWAY", "Anatomical view of cervical spine C1-C7 with strained trapezius and splenius capitis muscle fibers glowing in tense crimson tension bands"
        if cue_idx == 9:
            return "SPLIT_COMPARISON", "50/50 split comparison contrasting outwardly calm facial appearance with explosive microscopic biological stress within tissues"
        if cue_idx == 10:
            return "OBJECT_MACRO", "Macro view of dark steaming espresso pouring into glass cup with floating caffeine molecular structures symbolically hovering in steam"
        if cue_idx == 11:
            return "CAUSE_EFFECT_DIAGRAM", "Medical diagram showing caffeine molecules competitively blocking adenosine receptors without clearing the accumulating biochemical sleep pressure beneath"
        if cue_idx == 12:
            return "MECHANISM_CUTAWAY", "High-definition coronal cranial cutaway revealing cerebral cortex engulfed in chaotic amber-red distress signals and metabolic turbulence"
        if cue_idx == 13:
            return "MECHANISM_CUTAWAY", "Dense neural network visualization showing pyramidal neurons struggling to fire erratic action potentials with depleted ATP energy reservoirs"
        if cue_idx == 14:
            return "OBJECT_MACRO", "Molecular-level macro of cellular mitochondria in neural tissue showing fading ATP glow and structural membrane fatigue"
        if cue_idx == 15:
            return "MECHANISM_CUTAWAY", "Synaptic cleft crowded with dense amber clouds of accumulating adenosine neuromodulator molecules choking neurotransmission"
        if cue_idx == 16:
            return "CAUSE_EFFECT_DIAGRAM", "Flowchart diagram illustrating sluggish action potential conduction velocity slowing from 100 meters per second to a halting crawl"
        if cue_idx == 17:
            return "SPLIT_COMPARISON", "50/50 split comparison contrasting the neurological reflex latency of 0.08 percent blood alcohol concentration with 24-hour sleep deprivation"
        if cue_idx == 18:
            return "OBJECT_MACRO", "Macro focus on human hand extensor digitorum tendons with microscopic neuromuscular junction instability causing micro-tremors"
        if cue_idx == 19:
            return "MECHANISM_CUTAWAY", "Left hemisphere cortical language network showing Wernicke and Broca areas stalled with failing synaptic transmission loops"
        if cue_idx == 20:
            return "MECHANISM_CUTAWAY", "Microglia and astrocyte immune cells transforming into hyperactive phagocytic state within cortical parenchyma"
        if cue_idx == 21:
            return "MECHANISM_CUTAWAY", "High-magnification view of overactive microglia mistakenly engulfing and pruning healthy dendritic spines and synaptic boutons"
        if cue_idx == 22:
            return "CAUSE_EFFECT_DIAGRAM", "Coronal cutaway of brain tissue illustrating self-cannibalization by microglial pruning during prolonged wakefulness"
        if cue_idx == 23:
            return "MECHANISM_CUTAWAY", "Dendritic arborization withering and losing thousands of synaptic memory connections per hour of forced wakefulness"
        if cue_idx == 24:
            return "OBJECT_MACRO", "Distressed neural network pulsing in urgent warning amber-crimson light across deep cerebral cortex"

    if chap_idx == 2:
        if cue_idx <= 28:
            return "MECHANISM_CUTAWAY", "Overview of cerebral cortex during 16 active daytime hours, burning glucose and emitting metabolic byproduct plumes like miniature exhaust trails"
        if cue_idx <= 31:
            return "OBJECT_MACRO", "Microscopic interstitial space between cortical neurons clogged with sticky brown aggregates of misfolded beta-amyloid and hyperphosphorylated tau proteins"
        if cue_idx <= 35:
            return "SPLIT_COMPARISON", "50/50 split comparison showing tightly packed waking neural tissue blocking fluid entry versus dilated sleeping channels welcoming fluid flow"
        if cue_idx <= 41:
            return "MECHANISM_CUTAWAY", "Astrocytic endfeet expressing aquaporin-4 water channels shrinking by sixty percent, transforming narrow crevices into wide pulsating avenues"
        if cue_idx <= 46:
            return "MECHANISM_CUTAWAY", "Clear luminescent cerebrospinal fluid flushing through interstitial space driven by rhythmic arterial vasomotion pulses, washing away toxic protein plaques"
        return "CAUSE_EFFECT_DIAGRAM", "Schematic diagram showing nocturnal glymphatic drainage flushing cellular waste into dural lymphatic vessels and deep cervical lymph nodes"

    if chap_idx == 3:
        if cue_idx <= 56:
            return "OBJECT_MACRO", "Close-up of human face showing dark under-eye circles and strained facial expression reacting to loud urban noise"
        if cue_idx <= 63:
            return "MECHANISM_CUTAWAY", "Coronal cutaway showing bilateral almond-shaped amygdala nuclei flaring in blazing hyperactive red, firing uncontrolled distress alarms"
        if cue_idx <= 72:
            return "SPLIT_COMPARISON", "50/50 split comparison contrasting strong prefrontal cortex top-down inhibition during well-rested state versus severed connectivity after sleep loss"
        return "CAUSE_EFFECT_DIAGRAM", "Dynamic anatomical diorama showing uninhibited limbic emotional reactivity triggering sudden aggressive behavioral outbursts and stress responses"

    if chap_idx == 4:
        if cue_idx <= 87:
            return "MECHANISM_CUTAWAY", "Sympathetic nervous system firing intense electrical cascades downward along the thoracic spinal cord to the adrenal glands"
        if cue_idx <= 96:
            return "OBJECT_MACRO", "High-definition rendering of adrenal gland cortex atop human kidney pumping dense clouds of cortisol and adrenaline into bloodstream"
        if cue_idx <= 106:
            return "MECHANISM_CUTAWAY", "Microscopic cross-section of arterial vessel showing smooth muscle constriction and elevated blood pressure stressing endothelial cell lining"
        return "CAUSE_EFFECT_DIAGRAM", "Biological diagram illustrating sustained chronic cortisol elevation degrading vascular elasticity and driving systemic inflammation"

    if chap_idx == 5:
        if cue_idx <= 121:
            return "OBJECT_MACRO", "Close-up of inflamed pharyngeal mucosa and mouth ulceration occurring after consecutive all-nighters"
        if cue_idx <= 130:
            return "SPLIT_COMPARISON", "50/50 split comparison of bloodstream showing abundant active Natural Killer cells versus a 70 percent desolate reduction after one sleepless night"
        if cue_idx <= 140:
            return "MECHANISM_CUTAWAY", "Natural Killer lymphocyte failing to deliver perforin and granzyme granules to neutralize an invading viral pathogen"
        return "CAUSE_EFFECT_DIAGRAM", "Medical diagram showing suppressed immune surveillance leaving tissues vulnerable to infectious agents and cellular mutations"

    if chap_idx == 6:
        if cue_idx <= 156:
            return "SPLIT_COMPARISON", "50/50 split comparison contrasting financial bank balance ledger with biological irreversible cellular debt"
        if cue_idx <= 168:
            return "MECHANISM_CUTAWAY", "Axonal myelin sheaths in cerebral white matter showing micro-tears and degradation that weekend sleep-ins cannot repair"
        if cue_idx <= 178:
            return "CAUSE_EFFECT_DIAGRAM", "Circadian phase-shift diagram showing social jetlag destabilizing cellular metabolic clocks across liver, heart, and brain tissues"
        return "OBJECT_MACRO", "Hippocampal CA1 pyramidal neurons struggling with impaired long-term potentiation and memory consolidation deficits"

    if chap_idx == 7:
        if cue_idx <= 192:
            return "OBJECT_MACRO", "Cross-section of human stomach fundus lining rapidly secreting surging droplets of hunger-stimulating ghrelin peptide hormone"
        if cue_idx <= 202:
            return "SPLIT_COMPARISON", "50/50 hormonal battle split contrasting elevated ghrelin levels versus suppressed satiety hormone leptin from adipocytes"
        if cue_idx <= 212:
            return "MECHANISM_CUTAWAY", "Ventral striatum and nucleus accumbens dopamine reward circuits lighting up with intense cravings for refined sugars and carbohydrates"
        return "CAUSE_EFFECT_DIAGRAM", "Metabolic cycle diagram illustrating sleep deprivation driving excessive caloric intake and insulin resistance"

    if chap_idx == 8:
        if cue_idx <= 228:
            return "OBJECT_MACRO", "Anatomical focus on the suprachiasmatic nucleus (SCN) master clock perched directly atop the optic chiasm in the anterior hypothalamus"
        if cue_idx <= 238:
            return "MECHANISM_CUTAWAY", "Intrinsically photosensitive retinal ganglion cells absorbing 480nm blue light photons and relaying direct inhibitory signals to SCN"
        if cue_idx <= 248:
            return "SPLIT_COMPARISON", "50/50 split comparison of pineal gland showing healthy nighttime melatonin synthesis versus total suppression under smartphone light"
        return "CAUSE_EFFECT_DIAGRAM", "Molecular transcriptional clock feedback loop showing CLOCK and BMAL1 gene expression disrupted by artificial nocturnal illumination"

    if chap_idx == 9:
        if cue_idx <= 263:
            return "STEP_ENUMERATION", "Step-by-step hypnogram diagram illustrating 90-minute ultradian sleep cycle progressing from N1 light sleep to N3 slow-wave and REM"
        if cue_idx <= 273:
            return "MECHANISM_CUTAWAY", "Thermal regulation cutaway showing core body temperature dropping one degree Celsius while peripheral blood vessels dilate in hands and feet"
        if cue_idx <= 283:
            return "OBJECT_MACRO", "Pitch-black optimized bedroom sanctuary diorama with cool 18 degrees Celsius ambient atmosphere and zero light leaks"
        return "STEP_ENUMERATION", "Clear clinical diagram detailing evening wind-down protocol and sleep hygiene architecture for restorative rest"

    # chap_idx == 10
    if cue_idx <= 293:
        return "SPLIT_COMPARISON", "50/50 split comparison contrasting exhausted degraded neuron with regenerated vibrant neuron glowing with abundant ATP energy"
    if cue_idx <= 299:
        return "OBJECT_MACRO", "Regenerated neural network and fortified immune lymphocytes patrolling healthy vascular endothelium with restored vitality"
    return "MECHANISM_CUTAWAY", "Harmonious coronal view of healthy human brain bathed in calm nocturnal cerebrospinal fluid, concluding the restorative journey"


def get_cue_explainer_dia_com(cue_idx: int, text: str, chap_idx: int) -> Tuple[str, str]:
    t = text.lower()
    
    if chap_idx == 1:
        if cue_idx <= 2:
            return "OBJECT_MACRO", "Macro high-speed photography of shimmering beef fat beads sizzling and bubbling on smoking 180 degrees Celsius cast iron surface"
        if cue_idx <= 5:
            return "MECHANISM_CUTAWAY", "Cross-section macro showing raw red beef muscle fibers rapidly transforming into a rich mahogany brown seared crust"
        if cue_idx <= 9:
            return "SPLIT_COMPARISON", "50/50 cross-section comparison contrasting crunchy deep-brown seared crust with tender juicy pink interior meat fibers"
        if cue_idx <= 14:
            return "OBJECT_MACRO", "Extreme macro focus on golden blistered crust of freshly baked baguette and crunchy caramelized rice crust at bottom of pot"
        if cue_idx <= 20:
            return "OBJECT_MACRO", "Succulent amber meat juices and savory lipids glistening across oak cutting board beside thinly sliced seared steak"
        return "CAUSE_EFFECT_DIAGRAM", "Culinary diagram illustrating how intense surface searing locks in internal juices while creating hundreds of aroma compounds"

    if chap_idx == 2:
        if cue_idx <= 29:
            return "SPLIT_COMPARISON", "50/50 comparison contrasting French chemist Louis-Camille Maillard reaction on steak versus sugar caramelization in copper pan"
        if cue_idx <= 38:
            return "MECHANISM_CUTAWAY", "Molecular cutaway showing nucleophilic attack between amino acid amine groups and reducing sugar carbonyl groups forming glycosylamine"
        if cue_idx <= 46:
            return "SPLIT_COMPARISON", "Side-by-side scientific comparison of protein-rich savory meat browning versus pure sucrose thermal pyrolysis at 160 degrees Celsius"
        return "CAUSE_EFFECT_DIAGRAM", "Chemical taxonomy flowchart separating Maillard reaction aroma pathways from simple sugar caramelization melting"

    if chap_idx == 3:
        if cue_idx <= 59:
            return "CAUSE_EFFECT_DIAGRAM", "Thermal threshold diagram highlighting the golden Maillard window between 140 and 165 degrees Celsius"
        if cue_idx <= 68:
            return "SPLIT_COMPARISON", "50/50 comparison showing sluggish gray meat reaction below 140 degrees Celsius versus explosive golden browning at 155 degrees Celsius"
        if cue_idx <= 76:
            return "OBJECT_MACRO", "Infrared thermal imaging camera view of searing skillet showing precise radiant heat distribution across meat surface"
        return "CAUSE_EFFECT_DIAGRAM", "Chemical danger curve showing bitter acrid charring, toxic acrylamide, and heterocyclic amines forming above 180 degrees Celsius"

    if chap_idx == 4:
        if cue_idx <= 88:
            return "OBJECT_MACRO", "Extreme macro focus on tiny water moisture beads glistening across surface of cold steak, showing enemy number one of searing"
        if cue_idx <= 97:
            return "CAUSE_EFFECT_DIAGRAM", "Physics diagram demonstrating latent heat of vaporization requiring 2260 Joules per gram of surface water before temperature exceeds 100 degrees"
        if cue_idx <= 106:
            return "SPLIT_COMPARISON", "50/50 split comparison contrasting wet steak trapped in gray 100 degrees Celsius boiling steam versus bone-dry steak instantly searing"
        return "MECHANISM_CUTAWAY", "Cross-section showing boiling steam vapor layer pushing meat away from pan surface and blocking thermal conduction"

    if chap_idx == 5:
        if cue_idx <= 122:
            return "STEP_ENUMERATION", "Step-by-step demonstration of dry-brining steak with coarse kosher salt crystals resting on surface of meat"
        if cue_idx <= 132:
            return "MECHANISM_CUTAWAY", "Microscopic cross-section of meat fibers showing osmotic draw of liquid outward, salt dissolving, and reabsorption deep into muscle protein matrix"
        if cue_idx <= 142:
            return "OBJECT_MACRO", "Steak resting on elevated wire rack in cold refrigerator, cool circulating air dehydrating the surface to a completely dry matte finish"
        return "STEP_ENUMERATION", "Technique demonstration showing heavy paper towel pressing firmly to absorb every remaining trace of exterior moisture"

    if chap_idx == 6:
        if cue_idx <= 157:
            return "SPLIT_COMPARISON", "50/50 physical properties comparison contrasting low thermal conductivity of cast iron against high thermal conductivity of aluminum"
        if cue_idx <= 168:
            return "MECHANISM_CUTAWAY", "Cross-section of heavy 5-millimeter thick cast iron skillet demonstrating massive volumetric heat capacity storing enormous thermal energy"
        if cue_idx <= 178:
            return "SPLIT_COMPARISON", "50/50 thermal response comparison showing thin pan temperature crashing when cold meat enters versus cast iron maintaining searing heat"
        return "CAUSE_EFFECT_DIAGRAM", "Heat transfer diagram showing steady radiant and conductive heat flow from thick iron base into bottom of steak"

    if chap_idx == 7:
        if cue_idx <= 192:
            return "CAUSE_EFFECT_DIAGRAM", "Chemical cascade diagram showing Amadori rearrangement producing hundreds of complex new aroma molecules"
        if cue_idx <= 202:
            return "OBJECT_MACRO", "Molecular visual representation of roasted pyrazine molecules producing nutty roasted aroma notes over searing meat"
        if cue_idx <= 212:
            return "OBJECT_MACRO", "Molecular macro focus on savory furan and meaty thiol compounds rising into aromatic steam"
        return "MECHANISM_CUTAWAY", "Cutaway of human nasal cavity showing volatile Maillard aroma compounds binding to olfactory receptors and triggering saliva flow"

    if chap_idx == 8:
        if cue_idx <= 228:
            return "OBJECT_MACRO", "Macro view of crispy Vietnamese golden rice crust (cơm cháy) forming at the bottom of a heavy cast iron pot"
        if cue_idx <= 238:
            return "MECHANISM_CUTAWAY", "Microscopic cross-section of rice grains showing starch gelatinization, retrogradation, and toasted Maillard browning"
        if cue_idx <= 248:
            return "OBJECT_MACRO", "High-speed macro of roasting Arabica coffee beans cracking and turning rich chocolate brown during first crack"
        return "OBJECT_MACRO", "Artisan sourdough bread crust blistering with micro-bubbles of golden crunchy caramelized sugars"

    if chap_idx == 9:
        if cue_idx <= 263:
            return "SPLIT_COMPARISON", "50/50 kitchen mistake comparison contrasting an overcrowded steaming pan versus a properly spaced skillet searing cleanly"
        if cue_idx <= 273:
            return "STEP_ENUMERATION", "Technique diagram showing the danger of premature flipping versus allowing uninterrupted contact to develop crust"
        if cue_idx <= 283:
            return "CAUSE_EFFECT_DIAGRAM", "Thermal smoke point diagram showing whole butter burning into bitter black particles versus high-heat clarified ghee or tallow"
        return "STEP_ENUMERATION", "Three-step checklist summarizing pan spacing, contact patience, and oil smoke point discipline"

    # chap_idx == 10
    if cue_idx <= 293:
        return "OBJECT_MACRO", "Master chef skillet technique showing golden butter basting with fresh thyme and crushed garlic foaming over seared steak"
    if cue_idx <= 299:
        return "SPLIT_COMPARISON", "50/50 plate presentation showing perfectly cooked medium-rare ribeye with crunchy mahogany crust and vibrant tender interior"
    return "OBJECT_MACRO", "Warm inviting kitchen studio composition celebrating culinary heat mastery and the science of delicious golden browning"


def get_cue_explainer_nao_luoi(cue_idx: int, text: str, chap_idx: int) -> Tuple[str, str]:
    t = text.lower()
    
    if chap_idx == 1:
        if cue_idx <= 2:
            return "SITUATIONAL_ACTION", "Minimalist smartphone screen illuminated in dark space displaying message notification and glowing two-minute timer symbol"
        if cue_idx <= 6:
            return "OBJECT_MACRO", "Extreme macro focus on human thumb swiping rapidly across glowing glass screen through high-velocity video feeds"
        if cue_idx <= 11:
            return "OBJECT_MACRO", "Wall clock dial showing glowing hands advancing rapidly by two full hours in a single fleeting instant"
        if cue_idx <= 17:
            return "SPLIT_COMPARISON", "50/50 split comparison contrasting the initial promise of a brief glance with the reality of lost evening hours"
        if cue_idx <= 21:
            return "OBJECT_MACRO", "Smartphone screen switching off, leaving dark reflective glass mirroring a weary face in empty quiet room"
        return "MECHANISM_CUTAWAY", "Sagittal view of cerebral cortex showing depleted neurotransmitter channels and lingering hollow cognitive exhaustion"

    if chap_idx == 2:
        if cue_idx <= 29:
            return "SPLIT_COMPARISON", "50/50 scientific comparison debunking the myth of dopamine as happiness molecule versus its true role as craving driver"
        if cue_idx <= 38:
            return "MECHANISM_CUTAWAY", "Wolfram Schultz monkey neurobiology experiment showing dopamine firing in ventral tegmental area upon reward cue rather than reward receipt"
        if cue_idx <= 46:
            return "OBJECT_MACRO", "Microscopic neural synapse junction with glowing cyan dopamine vesicles releasing across the synaptic cleft into awaiting receptors"
        return "CAUSE_EFFECT_DIAGRAM", "Neurochemical diagram illustrating the difference between anticipatory wanting (dopamine) and hedonic liking (opioid receptors)"

    if chap_idx == 3:
        if cue_idx <= 59:
            return "CAUSE_EFFECT_DIAGRAM", "Dopamine dynamics graph showing baseline firing suddenly spiking 250 percent during rapid social media stimulation"
        if cue_idx <= 68:
            return "MECHANISM_CUTAWAY", "Homeostatic neural balance scale tipping violently as brain attempts to protect receptors from excessive dopamine saturation"
        if cue_idx <= 76:
            return "SPLIT_COMPARISON", "50/50 comparison contrasting dopamine peak euphoria against the steep compensatory crash into an irritable dopamine trough"
        return "OBJECT_MACRO", "D2 dopamine receptors in striatum temporarily downregulating and internalizing, leaving brain insensitive to everyday pleasures"

    if chap_idx == 4:
        if cue_idx <= 88:
            return "SPLIT_COMPARISON", "50/50 evolutionary split contrasting ancient hunter-gatherer searching for scarce wild honey versus modern algorithmic supernormal stimuli"
        if cue_idx <= 97:
            return "MECHANISM_CUTAWAY", "Primitive limbic reward circuitry overwhelmed by infinite digital novelty, bells, and notification badges"
        if cue_idx <= 106:
            return "CAUSE_EFFECT_DIAGRAM", "Evolutionary mismatch diagram showing modern sensory overload short-circuiting ancestral survival motivational pathways"
        return "OBJECT_MACRO", "Neural pathways in prefrontal cortex fatigued from continuous decision fatigue and algorithmic manipulation"

    if chap_idx == 5:
        if cue_idx <= 122:
            return "CAUSE_EFFECT_DIAGRAM", "Psychological mechanism diagram revealing procrastination as emotional avoidance of discomfort rather than laziness"
        if cue_idx <= 132:
            return "MECHANISM_CUTAWAY", "Hyperactive amygdala detecting perceived threat in a difficult task and triggering emotional distress escape behavior"
        if cue_idx <= 142:
            return "SPLIT_COMPARISON", "50/50 brain circuit comparison showing severed executive prefrontal cortex control while impulsive limbic system grabs smartphone"
        return "CAUSE_EFFECT_DIAGRAM", "Vicious cycle flowchart connecting task anxiety to digital escape, followed by guilt, shame, and deepened procrastination"

    if chap_idx == 6:
        if cue_idx <= 157:
            return "SPLIT_COMPARISON", "50/50 myth-busting comparison contrasting harsh ascetic deprivation against realistic neurobiological receptor restoration"
        if cue_idx <= 168:
            return "MECHANISM_CUTAWAY", "Striatal medium spiny neurons upregulating D2 dopamine receptors back to cell membranes during low-stimulation calm periods"
        if cue_idx <= 178:
            return "CAUSE_EFFECT_DIAGRAM", "Neuroplastic recovery timeline showing baseline sensitivity returning after reducing artificial high-intensity spikes"
        return "OBJECT_MACRO", "Peaceful neural diorama illustrating restored cognitive clarity and natural pleasure in reading and deep thought"

    if chap_idx == 7:
        if cue_idx <= 192:
            return "STEP_ENUMERATION", "Friction design diagram showing how increasing physical resistance by twenty seconds breaks automatic digital addiction loops"
        if cue_idx <= 202:
            return "OBJECT_MACRO", "Smartphone placed inside closed drawer in another room while display is switched to stark monochrome grayscale"
        if cue_idx <= 212:
            return "SPLIT_COMPARISON", "50/50 visual comparison of colorful addictive screen versus dull gray screen stripping dopamine trigger cues"
        return "STEP_ENUMERATION", "Frictionless work station setup with clear wooden desk, open physical notebook, and zero electronic distractions"

    if chap_idx == 8:
        if cue_idx <= 228:
            return "STEP_ENUMERATION", "Seven-day dopamine reset protocol timeline showing progressive daily adjustments without extreme ascetic isolation"
        if cue_idx <= 238:
            return "STEP_ENUMERATION", "Morning routine showing 60-minute digital-free sacred window with natural morning sunlight exposure and hydration"
        if cue_idx <= 248:
            return "SPLIT_COMPARISON", "50/50 dopamine quality comparison contrasting passive cheap scrolling against effort-driven rewards from exercise and creation"
        return "OBJECT_MACRO", "Cold shower neural invigorator diorama showing sustained 250 percent gentle dopamine elevation without an abrupt crash"

    if chap_idx == 9:
        if cue_idx <= 263:
            return "STEP_ENUMERATION", "Two-minute rule diagram illustrating how committing to just 120 seconds lowers psychological activation energy"
        if cue_idx <= 273:
            return "MECHANISM_CUTAWAY", "Prefrontal cortex tricking the amygdala by framing the task as a microscopic non-threatening action"
        if cue_idx <= 283:
            return "SPLIT_COMPARISON", "50/50 physics metaphor comparison contrasting high static friction at rest with smooth kinetic friction once in motion"
        return "OBJECT_MACRO", "Hourglass showing two minutes passing effortlessly, leading directly into unbroken flow state and focused work"

    # chap_idx == 10
    if cue_idx <= 293:
        return "OBJECT_MACRO", "Human cranium diorama with prefrontal cortex radiating calm bioluminescent sapphire light, steering daily actions with intention"
    if cue_idx <= 299:
        return "SPLIT_COMPARISON", "50/50 life comparison showing chaotic reactive existence versus focused intentional self-mastery and deep agency"
    return "MECHANISM_CUTAWAY", "Harmonious 3D neural diorama with balanced dopamine neurotransmission and clear mental focus, concluding the journey"


def get_cue_explainer_ua_sao_vay(cue_idx: int, text: str, chap_idx: int) -> Tuple[str, str]:
    t = text.lower()
    
    if chap_idx == 1:
        if cue_idx <= 2:
            return "SITUATIONAL_ACTION", "Minimalist modern bathroom diorama with clean mirror above sink reflecting soft morning daylight"
        if cue_idx <= 5:
            return "SPLIT_COMPARISON", "50/50 split comparison showing person raising physical right hand while mirror reflection raises virtual left hand"
        if cue_idx <= 9:
            return "CAUSE_EFFECT_DIAGRAM", "Physics question diorama posing the fundamental paradox: why do mirrors reverse left-right but not up-down?"
        if cue_idx <= 14:
            return "SPLIT_COMPARISON", "50/50 surreal comparison showing real upright posture versus an imaginary vertical inversion with feet pointing at ceiling"
        if cue_idx <= 20:
            return "OBJECT_MACRO", "Pristine flat silver-backed glass mirror showing zero vertical coordinate distortion as head remains strictly at top"
        return "CAUSE_EFFECT_DIAGRAM", "Schematic diagram presenting the optical symmetry dilemma puzzling physicists and philosophers for centuries"

    if chap_idx == 2:
        if cue_idx <= 29:
            return "STEP_ENUMERATION", "Optical ray-tracing diagram showing incident light rays reflecting off flat mirror surface according to Law of Reflection"
        if cue_idx <= 38:
            return "MECHANISM_CUTAWAY", "Physics cutaway demonstrating angle of incidence equals angle of reflection for photons striking mirror perpendicular plane"
        if cue_idx <= 46:
            return "SPLIT_COMPARISON", "50/50 ray-path comparison showing light from right hand bouncing straight back into right eye with zero lateral ray crossing"
        return "CAUSE_EFFECT_DIAGRAM", "Laser beam demonstration showing straight parallel photon vectors bouncing back along their exact axis of arrival"

    if chap_idx == 3:
        if cue_idx <= 59:
            return "CAUSE_EFFECT_DIAGRAM", "3D Cartesian coordinate system XYZ showing mirror inverting strictly the normal Z-axis while X and Y remain untouched"
        if cue_idx <= 68:
            return "MECHANISM_CUTAWAY", "Front-to-back inversion cutaway illustrating normal vector reflection z becomes negative z without horizontal transposition"
        if cue_idx <= 76:
            return "SPLIT_COMPARISON", "50/50 comparison contrasting front-to-back topological inversion against an imaginary 180-degree physical rotation"
        return "OBJECT_MACRO", "Rubber glove turned inside out showing topological front-to-back inversion matching the exact geometry of mirror reflection"

    if chap_idx == 4:
        if cue_idx <= 88:
            return "MECHANISM_CUTAWAY", "Cognitive psychology diorama of human brain subconsciously executing a mental rotation around the vertical Y-axis"
        if cue_idx <= 97:
            return "SPLIT_COMPARISON", "50/50 cognitive split showing human bilateral symmetry tricking the brain into falsely perceiving a left-right swap"
        if cue_idx <= 106:
            return "CAUSE_EFFECT_DIAGRAM", "Neuropsychology diagram showing why asymmetric objects reveal the Z-axis inversion that bilateral bodies mask"
        return "OBJECT_MACRO", "Asymmetric arrow prop held before mirror demonstrating straight front-to-back pointing without lateral transposition"

    if chap_idx == 5:
        if cue_idx <= 122:
            return "STEP_ENUMERATION", "Step-by-step physical demonstration with right-handed rubber glove being peeled inside-out into a left-handed glove"
        if cue_idx <= 132:
            return "OBJECT_MACRO", "Molecular chirality representation showing non-superimposable mirror image enantiomers in stereochemistry"
        if cue_idx <= 142:
            return "SPLIT_COMPARISON", "50/50 stereochemical comparison showing D-glucose and L-glucose molecules reflecting across optical mirror plane"
        return "CAUSE_EFFECT_DIAGRAM", "Geometric proof diagram proving mirror transformation is non-rotational parity inversion (chirality change)"

    if chap_idx == 6:
        if cue_idx <= 157:
            return "SPLIT_COMPARISON", "50/50 thought experiment comparison showing person lying down horizontally before a large floor-to-ceiling mirror"
        if cue_idx <= 168:
            return "CAUSE_EFFECT_DIAGRAM", "Physics coordinate diagram showing horizontal body head staying at head side and feet at feet side without swapping"
        if cue_idx <= 178:
            return "SPLIT_COMPARISON", "50/50 paradox resolution showing that if mirrors flipped horizontal axis, lying down would flip head and feet"
        return "MECHANISM_CUTAWAY", "Ray vectors demonstrating reflection is strictly perpendicular to mirror surface regardless of body orientation"

    if chap_idx == 7:
        if cue_idx <= 192:
            return "OBJECT_MACRO", "White card with printed bold word held before mirror, showing the text appearing reversed to the human viewer"
        if cue_idx <= 202:
            return "SPLIT_COMPARISON", "50/50 demonstration showing that YOU rotated the card 180 degrees to face the mirror, creating the reversal yourself"
        if cue_idx <= 212:
            return "OBJECT_MACRO", "Transparent acetate sheet with text held before mirror showing letters completely unreversed when viewed from behind"
        return "OBJECT_MACRO", "Front hood of emergency ambulance showing reverse-printed lettering aligning perfectly in vehicle rearview mirror"

    if chap_idx == 8:
        if cue_idx <= 228:
            return "OBJECT_MACRO", "Close-up of polished stainless steel soup spoon showing inverted reflection on concave side and upright reflection on convex side"
        if cue_idx <= 238:
            return "MECHANISM_CUTAWAY", "Optical ray diagram of concave spherical mirror focusing parallel light rays through focal point F to create inverted real image"
        if cue_idx <= 248:
            return "MECHANISM_CUTAWAY", "Convex mirror ray diagram showing diverging reflected light creating a wide-angle virtual upright image for road safety"
        return "OBJECT_MACRO", "Parabolic mirage 3D optical illusion projecting a floating solid hologram of a coin hovering in mid-air"

    if chap_idx == 9:
        if cue_idx <= 263:
            return "OBJECT_MACRO", "James Webb Space Telescope primary mirror array featuring 18 hexagonal beryllium segments coated in vaporized gold"
        if cue_idx <= 273:
            return "MECHANISM_CUTAWAY", "High-power industrial laser cavity diagram showing dielectric mirrors bouncing photon cascades with 99.999 percent reflectivity"
        if cue_idx <= 283:
            return "OBJECT_MACRO", "Extreme ultraviolet (EUV) photolithography multilayer Mo/Si mirror focusing 13.5nm light for 2nm microchip fabrication"
        return "STEP_ENUMERATION", "Three-panel engineering display illustrating space exploration, laser surgery, and semiconductor nanolithography"

    # chap_idx == 10
    if cue_idx <= 293:
        return "OBJECT_MACRO", "Clean reflective optical prism splitting white sunlight into pure chromatic spectral beams on slate tabletop"
    if cue_idx <= 299:
        return "SPLIT_COMPARISON", "50/50 philosophical comparison showing passive everyday perception transformed into curious scientific understanding"
    return "OBJECT_MACRO", "Pristine physics laboratory diorama celebrating optics, geometry, and human curiosity, concluding the explainer journey"


def get_cue_explainer_vu_tru_ti_hon(cue_idx: int, text: str, chap_idx: int) -> Tuple[str, str]:
    t = text.lower()
    
    if chap_idx == 1:
        if cue_idx <= 2:
            return "SITUATIONAL_ACTION", "Solitary astronaut in white EVA suit drifting weightlessly through deep space with gold visor reflecting dense starfield"
        if cue_idx <= 5:
            return "OBJECT_MACRO", "Colossal pitch-black sphere of supermassive black hole blotting out stars against cosmic deep space void"
        if cue_idx <= 9:
            return "MECHANISM_CUTAWAY", "Photon sphere diorama at 1.5 Schwarzschild radii where light rays are trapped in unstable circular orbits"
        if cue_idx <= 14:
            return "CAUSE_EFFECT_DIAGRAM", "General relativity diagram showing the Schwarzschild event horizon as the absolute boundary of no return"
        return "OBJECT_MACRO", "Blinding edge of event horizon rim glowing with trapped photon ring against cosmic darkness"

    if chap_idx == 2:
        if cue_idx <= 25:
            return "OBJECT_MACRO", "Vast glowing accretion disk of superheated ionized plasma swirling around black hole at relativistic speeds"
        if cue_idx <= 31:
            return "SPLIT_COMPARISON", "50/50 Doppler beaming comparison showing approaching plasma side blazing blue-white while receding side dims into faint red"
        if cue_idx <= 37:
            return "MECHANISM_CUTAWAY", "Magnetic field lines twisting into powerful collimated relativistic plasma jets blasting thousands of light-years into space"
        return "CAUSE_EFFECT_DIAGRAM", "Thermodynamic energy conversion diagram showing gravitational potential converting to intense radiant X-ray luminosity"

    if chap_idx == 3:
        if cue_idx <= 49:
            return "CAUSE_EFFECT_DIAGRAM", "Spacetime curvature diagram illustrating Einstein gravitational time dilation deepening near the event horizon"
        if cue_idx <= 56:
            return "SPLIT_COMPARISON", "50/50 time relativity split showing distant observer clock ticking normally while astronaut clock slows to a near standstill"
        if cue_idx <= 63:
            return "MECHANISM_CUTAWAY", "Gravitational redshift cutaway showing light waves escaping astronaut stretching into long invisible radio wavelengths"
        return "SPLIT_COMPARISON", "Proper time comparison showing astronaut wristwatch continuing to tick with completely normal local rhythm"

    if chap_idx == 4:
        if cue_idx <= 75:
            return "STEP_ENUMERATION", "Step-by-step passage through the event horizon of a supermassive black hole showing smooth local spacetime curvature"
        if cue_idx <= 83:
            return "SPLIT_COMPARISON", "50/50 scale comparison contrasting gentle horizon crossing of supermassive black hole against violent stellar black hole"
        if cue_idx <= 91:
            return "CAUSE_EFFECT_DIAGRAM", "Causal boundary diagram showing all internal future light cones tilting irreversibly inward toward the center"
        return "OBJECT_MACRO", "Astronaut crossing the event horizon boundary with zero physical barrier, entering causally isolated realm"

    if chap_idx == 5:
        if cue_idx <= 104:
            return "MECHANISM_CUTAWAY", "Differential gravitational tidal force vectors pulling with extreme strength on astronaut feet compared to head"
        if cue_idx <= 112:
            return "SPLIT_COMPARISON", "50/50 spaghettification comparison showing vertical radial stretching paired with horizontal lateral compression"
        if cue_idx <= 119:
            return "OBJECT_MACRO", "Microscopic atomic view showing molecular bonds elongating and pulling apart into a fine ribbon of subatomic particles"
        return "CAUSE_EFFECT_DIAGRAM", "Tidal tensor equation diagram illustrating tidal force scaling inversely with the cube of radial distance"

    if chap_idx == 6:
        if cue_idx <= 132:
            return "CAUSE_EFFECT_DIAGRAM", "Metric tensor signature inversion diagram showing spatial radius coordinate r swapping roles with time coordinate t"
        if cue_idx <= 140:
            return "SPLIT_COMPARISON", "50/50 conceptual comparison showing how the singularity is no longer a location in space but an unavoidable future moment"
        if cue_idx <= 148:
            return "MECHANISM_CUTAWAY", "Inward-tilting light cone geometry showing every possible trajectory leading inevitably to the central singularity"
        return "SPLIT_COMPARISON", "Time arrow metaphor illustrating that escaping the singularity is as impossible as traveling backward to yesterday"

    if chap_idx == 7:
        if cue_idx <= 162:
            return "OBJECT_MACRO", "Looking backward toward the external universe, seeing background starlight compressed into a bright shrinking circle overhead"
        if cue_idx <= 170:
            return "MECHANISM_CUTAWAY", "Extreme optical aberration ray tracing showing infinite gravitational blueshift brightening the diminishing optical keyhole"
        if cue_idx <= 178:
            return "SPLIT_COMPARISON", "50/50 field of view comparison showing external universe shrinking to a pinpoint as ink-black darkness swallows periphery"
        return "OBJECT_MACRO", "Final fleeting glimpse of external starlight focused into an intense blue-violet optical portal above"

    if chap_idx == 8:
        if cue_idx <= 192:
            return "OBJECT_MACRO", "Central gravitational singularity diorama showing mathematical point of infinite density and zero physical volume"
        if cue_idx <= 200:
            return "MECHANISM_CUTAWAY", "Spacetime curvature Riemann curvature scalar tending to infinity, tearing smooth fabric of spacetime into quantum foam"
        if cue_idx <= 207:
            return "SPLIT_COMPARISON", "50/50 theoretical physics split showing where Einstein general relativity breaks down and quantum mechanics collapses"
        return "OBJECT_MACRO", "Planck scale quantum gravity foam at 10 to the minus 35 meters where space and time cease to exist"

    if chap_idx == 9:
        if cue_idx <= 220:
            return "MECHANISM_CUTAWAY", "Quantum vacuum fluctuation diagram at event horizon showing virtual particle-antiparticle pairs spontaneously generating"
        if cue_idx <= 228:
            return "MECHANISM_CUTAWAY", "Negative energy virtual particle falling into black hole while positive particle escapes as thermal Hawking radiation"
        if cue_idx <= 234:
            return "CAUSE_EFFECT_DIAGRAM", "Black hole evaporation timeline showing slow mass loss over 10 to the 100th power years until final micro-detonation"
        return "OBJECT_MACRO", "Final microscopic quantum flash of an evaporating black hole dissolving into pure radiant photons"

    # chap_idx == 10
    if cue_idx <= 244:
        return "OBJECT_MACRO", "Panoramic view of supermassive black hole anchoring the spinning arms of a vibrant spiral galaxy across deep cosmos"
    if cue_idx <= 249:
        return "SPLIT_COMPARISON", "50/50 cosmic reflection showing human consciousness made of stardust gazing back at the deepest mysteries of space"
    return "OBJECT_MACRO", "Serene cinematic wide view of distant nebulae and cosmic web, concluding the astronomical documentary journey"
