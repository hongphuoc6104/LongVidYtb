#!/usr/bin/env python3
"""Data generator for en-inside-vessel Batch 1 specs (Long 16:9 and Short 9:16).
Competitor: Nucleus Medical Media | Voice: en-US-EricNeural
"""

from typing import Any, Dict, List


def get_inside_vessel_long() -> Dict[str, Any]:
    scene_anchor_base = (
        "Nucleus Medical Media 8K 3D endoscopic biomedical cinematography with glistening subsurface tissue textures "
        "and clean surgical fiber-optic rim lighting, strictly zero text labels"
    )

    chapters = [
        ("ch1_hook", "Hour 0 to 6: Normal Baseline and Adenosine Buildup"),
        ("ch2_paradox", "Hour 8 to 12: Circadian Desynchronization and Cortisol Surge"),
        ("ch3_mechanism", "Hour 14 to 16: Glymphatic Drainage Stagnation"),
        ("ch4_case_study_1", "Hour 18: Micro-Capillary Vasoconstriction and Hypoxia"),
        ("ch5_escalation", "Hour 20: Systemic Endothelial Inflammation"),
        ("ch6_case_study_2", "Hour 22: Metabolic Stress and Micro-Thrombi"),
        ("ch7_systemic_shift", "Hour 24: Myocardial Strain and Hemodynamic Overload"),
        ("ch8_resolution", "Slow-Wave Sleep and Microvascular Restoration"),
    ]

    # 64 shots: 8 chapters x 8 shots.
    # Grouping within each chapter: shots 0..3 (group A, S01 starts False, S02-04 True),
    # shots 4..7 (group B, S05 starts False, S06-08 True).
    # Word count per shot: strictly 21 to 22 words (to ensure duration stays under 580s with EricNeural).
    # pause_after_sec: 0.36 (internal), 0.40 (mid-chapter pivot), 0.55 (chapter end).

    raw_shots_data = [
        # Chapter 1: ch1_hook (S01 - S08)
        {
            "narration": "Right now, your heart beats seventy times a minute, pumping billions of crimson erythrocytes smoothly through three miles of glistening micro-capillaries.",
            "camera_verb": "Smooth endoscopic forward lumen dolly",
            "start_visual": "Nucleus Medical Media 8K endoscopic shot inside a healthy human cerebral arteriole: glistening crimson red blood cells flowing smoothly through translucent lumen, strictly zero text.",
            "end_visual": "Dollying deeper into the branching microvascular network: glowing endothelial cells line vessel walls with clean surgical fiber-optic rim illumination, strictly zero text.",
            "subject_motion": "flexible biconcave red blood cells glide smoothly in single-file pulsatile rhythm through the glistening capillary channel",
        },
        {
            "narration": "During normal waking hours, trillions of active cerebral neurons consume glucose rapidly, constantly burning cellular energy to transmit electrical signals.",
            "camera_verb": "Macro anatomical cross-section orbital arc",
            "start_visual": "Translucent 3D cutaway of cerebral cortex: glowing networks of pyramidal neurons firing delicate cyan electrical synaptic pulses, strictly zero text.",
            "end_visual": "Orbiting the neural mesh: vibrant synaptic junctions pulse with light as golden glucose molecules pass from micro-capillaries into astrocytes, strictly zero text.",
            "subject_motion": "cyan action potentials flicker rhythmically across branching dendrites as nutrients diffuse through surrounding interstitial fluid",
        },
        {
            "narration": "With every molecule of energy consumed, a metabolic byproduct called adenosine steadily accumulates inside the microscopic spaces between your brain cells.",
            "camera_verb": "Micro-cellular shallow-DOF focus pull",
            "start_visual": "Extreme close-up on interstitial synaptic cleft: glowing amber adenosine molecules accumulating gently around post-synaptic receptor sites, strictly zero text.",
            "end_visual": "Focus pulling from neural membrane to interstitial fluid: concentration of amber molecular droplets steadily rises across the cellular matrix, strictly zero text.",
            "subject_motion": "amber adenosine molecules drift through clear interstitial fluid, gradually clustering around receptor protein channels",
        },
        {
            "narration": "As adenosine binds to specialized neural receptors, it produces a gentle braking effect, gradually building what neuroscientists call sleep pressure.",
            "camera_verb": "Precision receptor docking push-in",
            "start_visual": "High-magnification view of neural membrane: amber adenosine molecules approaching purple G-protein coupled receptor complexes, strictly zero text.",
            "end_visual": "Pushing tight into the receptor pocket as adenosine docks smoothly, causing internal signaling proteins to slow neuronal firing rates, strictly zero text.",
            "subject_motion": "adenosine molecule docks into the membrane receptor pocket, triggering a subtle dampening pulse through the neuron",
        },
        {
            "narration": "By hour six of continuous wakefulness, your vascular endothelium remains supple and elastic, maintaining optimal blood pressure and tissue perfusion.",
            "camera_verb": "Endothelial cell surface glide",
            "start_visual": "Smooth gliding pass along the inner wall of a muscular arteriole: pristine endothelial cells flexing comfortably with each systolic pulse, strictly zero text.",
            "end_visual": "Gliding toward a capillary junction: endothelial cell junctions remain tightly sealed, preventing any fluid leakage into surrounding tissue, strictly zero text.",
            "subject_motion": "healthy endothelial walls expand and contract with rhythmic elasticity in sync with gentle pulsatile fluid flow",
        },
        {
            "narration": "Nitric oxide gas diffuses continuously from endothelial cells into surrounding smooth muscle, keeping microscopic vessels relaxed and wide open for flow.",
            "camera_verb": "Vascular smooth muscle cutaway push",
            "start_visual": "Cutaway view through arteriole wall: tiny glowing cyan nitric oxide molecules diffusing from inner endothelium into circumferential muscle fibers, strictly zero text.",
            "end_visual": "Pushing into relaxing muscle bands: vascular tone remains calm and dilated, allowing high-volume laminar blood flow, strictly zero text.",
            "subject_motion": "cyan gas molecules diffuse outward through tissue layers, causing smooth muscle bands to relax and widen the lumen",
        },
        {
            "narration": "At this early stage, your immune system circulates quietly in background surveillance mode, showing zero signs of pathological vascular stress.",
            "camera_verb": "Immune surveillance tracking pass",
            "start_visual": "Wide lumen shot of flowing bloodstream: spherical white leukocytes drifting peacefully along the center of the vessel without adhering, strictly zero text.",
            "end_visual": "Tracking a solitary neutrophil floating past smooth endothelial lining without sticking or triggering inflammatory alarms, strictly zero text.",
            "subject_motion": "spherical white blood cells tumble serenely through blood plasma alongside crimson red blood cells without touching walls",
        },
        {
            "narration": "However, as your natural bedtime approaches and passes without rest, an invisible microscopic domino effect begins across every organ system.",
            "camera_verb": "Systemic organ pull-back transition",
            "start_visual": "Macro view of cerebral micro-capillaries transitioning smoothly into wider anatomical cutaway of human brain and circulatory network, strictly zero text.",
            "end_visual": "Pulling back as the calm blue ambient lighting of normal physiology shifts toward an urgent amber warning tone, strictly zero text.",
            "subject_motion": "camera pulls back through translucent organ layers as subtle amber stress hues begin tinting vascular conduits",
        },

        # Chapter 2: ch2_paradox (S09 - S16)
        {
            "narration": "By hour eight to twelve of missed sleep, your master circadian clock in the hypothalamus detects an unnatural, prolonged wake state.",
            "camera_verb": "Hypothalamic nucleus orbital arc",
            "start_visual": "Translucent 3D visualization of the suprachiasmatic nucleus: microscopic neural clock cells pulsing with desynchronized amber electrical rhythms, strictly zero text.",
            "end_visual": "Orbiting the neural cluster as disrupted circadian signals cascade downward into the pituitary gland through endocrine pathways, strictly zero text.",
            "subject_motion": "delicate circadian pacemaker cells pulse erratically as their normal synchronized electrical cadence fragments",
        },
        {
            "narration": "Instead of dropping into restorative nocturnal quiescence, your adrenal glands begin pumping elevated pulses of cortisol and adrenaline into circulation.",
            "camera_verb": "Adrenal cortex micro-dolly push",
            "start_visual": "Close-up cutaway of the adrenal gland cortex: endocrine secretory vesicles releasing glowing orange cortisol hormone droplets into capillaries, strictly zero text.",
            "end_visual": "Dollying alongside bloodstream as cortisol surges rapidly through systemic circulation, binding to receptors across distant blood vessel walls, strictly zero text.",
            "subject_motion": "orange hormone droplets burst continuously from adrenal cells, flooding into the venous blood stream",
        },
        {
            "narration": "This unexpected hormonal surge forces your vascular system into an emergency state of chronic vasoconstriction, raising systemic arterial pressure unprompted.",
            "camera_verb": "Arteriole constriction macro push",
            "start_visual": "Endoscopic view inside a peripheral arteriole: smooth muscular wall beginning to tense and tighten inward under cortisol stimulation, strictly zero text.",
            "end_visual": "Pushing forward as the vessel lumen narrows by twenty percent, forcing blood cells into high-velocity turbulent shear stress, strictly zero text.",
            "subject_motion": "arteriole muscular wall contracts forcefully, constricting the lumen diameter and compressing flowing red blood cells",
        },
        {
            "narration": "Endothelial cells lining your blood vessels begin producing superoxide radicals, molecules that greedily scavenge and destroy your vital nitric oxide.",
            "camera_verb": "Endothelial radical synthesis zoom",
            "start_visual": "High-magnification view of endothelial cell surface: glowing red superoxide free radicals emerging from stressed cellular mitochondria, strictly zero text.",
            "end_visual": "Zooming into the fluid boundary: red radicals collide with cyan nitric oxide molecules, annihilating them in tiny oxidative bursts, strictly zero text.",
            "subject_motion": "red oxidative radicals rapidly collide with cyan nitric oxide, extinguishing the protective vasodilator signal",
        },
        {
            "narration": "Deprived of nitric oxide, delicate micro-capillary beds lose their natural elasticity, becoming rigid and resistant to rhythmic cardiac pulse waves.",
            "camera_verb": "Capillary wall stiffness track",
            "start_visual": "Cross-section of a stiffening cerebral capillary: vessel wall appearing fibrous and inflexible under high-pressure blood flow, strictly zero text.",
            "end_visual": "Tracking the rigid vessel as pulsatile systolic pressure hammers against stiffened walls without normal shock-absorbing elasticity, strictly zero text.",
            "subject_motion": "stiffened capillary walls shudder under rhythmic blood pressure spikes without expanding naturally to absorb shock",
        },
        {
            "narration": "In the brain, neurons continue firing despite lacking proper metabolic clearance, struggling to maintain clear synaptic neurotransmitter recycling and signaling pathways.",
            "camera_verb": "Exhausted synapse focus pull",
            "start_visual": "Close-up of a fatigued cortical synapse: neurotransmitter vesicles depleting rapidly while un-recycled glutamate lingers in the synaptic cleft, strictly zero text.",
            "end_visual": "Focus pulling to the post-synaptic dendritic spine: receptor proteins becoming desensitized, causing delayed and sluggish synaptic transmission, strictly zero text.",
            "subject_motion": "neurotransmitter vesicles release erratically while clearing pumps struggle to remove excess molecules from the cleft",
        },
        {
            "narration": "Adenosine levels now reach saturation thresholds, yet your conscious willpower and stress hormones forcefully override the brain's natural shutdown command.",
            "camera_verb": "Receptor saturation orbital glide",
            "start_visual": "Dense 3D landscape of neural membranes: almost every single adenosine receptor fully occupied by glowing amber molecules, strictly zero text.",
            "end_visual": "Orbiting the saturated membrane as competing adrenaline signals artificially force ion channels open against the heavy braking pressure, strictly zero text.",
            "subject_motion": "amber adenosine molecules completely blanket receptors while conflicting adrenaline pulses spark sharp erratic discharges",
        },
        {
            "narration": "This artificial chemical conflict creates a severe physiological rift, setting the stage for catastrophic microvascular and cognitive failure in hours ahead.",
            "camera_verb": "Cerebral vascular wide pull-back",
            "start_visual": "Wide 3D cutaway of the human brain: dense network of cerebral blood vessels glowing with turbulent amber friction hues, strictly zero text.",
            "end_visual": "Pulling back to reveal the intricate deep brain structures struggling under metabolic overload as hour fourteen arrives, strictly zero text.",
            "subject_motion": "camera pulls back through translucent brain tissue revealing congested capillary networks pulsing with elevated tension",
        },

        # Chapter 3: ch3_mechanism (S17 - S24)
        {
            "narration": "By hour fourteen, a silent anatomical disaster strikes your cerebral tissue: the complete shutdown of your brain's unique glymphatic drainage system.",
            "camera_verb": "Perivascular space lumen dolly",
            "start_visual": "Nucleus 3D cutaway of a cerebral blood vessel surrounded by a fluid-filled perivascular tunnel: clear cerebrospinal fluid flowing slowly, strictly zero text.",
            "end_visual": "Dollying down the perivascular space as fluid currents stall and stagnate into motionless, murky pools, strictly zero text.",
            "subject_motion": "clear fluid currents within the perivascular tunnel decelerate rapidly until fluid flow comes to a complete standstill",
        },
        {
            "narration": "Under normal slow-wave sleep, specialized glial cells shrink by sixty percent, allowing cerebrospinal fluid to wash through and flush toxins.",
            "camera_verb": "Astrocyte interstitial volume macro",
            "start_visual": "Branching star-shaped astrocytes forming dense interlocking barriers around cerebral capillaries in wakefulness, strictly zero text.",
            "end_visual": "Showing theoretical sleep state: astrocytes shrinking away to open wide interstitial channels, then snapping back to swollen wakefulness, strictly zero text.",
            "subject_motion": "swollen astrocyte end-feet press tightly against vessel walls, completely sealing off interstitial drainage pathways",
        },
        {
            "narration": "Because you remain awake, your astrocytes stay swollen and tightly packed, sealing off the vital interstitial channels like tightly locked floodgates.",
            "camera_verb": "Astrocytic end-feet barrier push",
            "start_visual": "Extreme close-up on astrocyte end-feet wrapping tightly around a cerebral capillary: gaps between cells measure mere nanometers, strictly zero text.",
            "end_visual": "Pushing tight to the sealed junction where cerebrospinal fluid is blocked from entering the neural parenchyma, strictly zero text.",
            "subject_motion": "swollen glial cell membranes press tightly together, preventing cleansing cerebrospinal fluid from circulating",
        },
        {
            "narration": "Deprived of convective fluid flushing, neurotoxic metabolic debris begins accumulating directly around vulnerable synaptic junctions throughout your fragile cerebral cortex.",
            "camera_verb": "Toxic plaque accumulation track",
            "start_visual": "Translucent neural tissue space: sticky amber fragments of beta-amyloid peptide aggregating along dendritic branches, strictly zero text.",
            "end_visual": "Tracking the accumulation: tangled hyperphosphorylated tau proteins begin precipitating out of solution around neuronal axons, strictly zero text.",
            "subject_motion": "sticky amber peptide fragments collide and clump together into dark microscopic aggregates along neural branches",
        },
        {
            "narration": "Beta-amyloid fragments stick together into insoluble oligomers, generating localized oxidative stress that damages delicate neuronal membranes and dendritic spine receptors.",
            "camera_verb": "Amyloid oligomer surface zoom",
            "start_visual": "High-magnification view of jagged beta-amyloid cluster adhering to cell membrane: lipid bilayer warping under oxidative stress, strictly zero text.",
            "end_visual": "Zooming into the membrane damage: ion leaks develop across the damaged lipid bilayer, destabilizing cellular electrochemical equilibrium, strictly zero text.",
            "subject_motion": "jagged protein oligomers embed into the flexible lipid membrane, causing localized structural distortion and micro-tears",
        },
        {
            "narration": "Simultaneously, microglial cells, the resident immune defenders of the brain, detect this stagnant debris and transform into an angry pro-inflammatory state.",
            "camera_verb": "Microglia phenotypic activation arc",
            "start_visual": "Delicate ramified microglial cell with long branching survey arms resting peacefully in brain parenchyma, strictly zero text.",
            "end_visual": "Orbiting as the cell withdraws its branches, swelling into an amoeboid inflammatory warrior releasing cytotoxic cytokines, strictly zero text.",
            "subject_motion": "the microglial cell rapidly retracts its thin branches and transforms into an enlarged amoeboid inflammatory cell",
        },
        {
            "narration": "These activated microglia release tumor necrosis factor and interleukins, sparking microscopic inflammation that spreads rapidly through delicate surrounding brain tissue.",
            "camera_verb": "Cytokine cloud dispersion push",
            "start_visual": "Activated microglial cell discharging a radiant cloud of glowing purple cytokine signaling molecules into surrounding interstitial fluid, strictly zero text.",
            "end_visual": "Pushing along the cytokine wave as signaling molecules bind to neighboring capillary endothelial receptors, triggering inflammatory responses, strictly zero text.",
            "subject_motion": "purple cytokine molecules diffuse rapidly through interstitial space, binding to vascular and neural membranes",
        },
        {
            "narration": "Your brain is now marinating in its own metabolic exhaust, unable to clean itself without the essential reset of deep sleep.",
            "camera_verb": "Cerebral parenchyma slow tilt-up",
            "start_visual": "Wide macro cross-section of cerebral cortex: dark murky interstitial fluid saturated with glowing amber waste particles, strictly zero text.",
            "end_visual": "Tilting upward through layers of stressed neurons where electrical signaling becomes noticeably fragmented and erratic, strictly zero text.",
            "subject_motion": "dense amber haze of un-cleared waste molecules lingers motionlessly around fatigued neurons and capillaries",
        },

        # Chapter 4: ch4_case_study_1 (S25 - S32)
        {
            "narration": "As hour eighteen arrives, your microvascular circulation reaches a critical physiological bottleneck inside the narrowest capillaries throughout your entire body.",
            "camera_verb": "Capillary entrance forward push",
            "start_visual": "Endoscopic camera positioned at the junction where a terminal arteriole branches into hair-thin capillary tubes, strictly zero text.",
            "end_visual": "Pushing directly into the entrance of a six-micrometer capillary lumen: diameter is barely wide enough for one cell, strictly zero text.",
            "subject_motion": "camera navigates into a constricted capillary entrance where flowing plasma velocity slows abruptly",
        },
        {
            "narration": "A normal red blood cell measures eight micrometers in diameter, meaning it must physically deform and fold to squeeze through capillaries.",
            "camera_verb": "Erythrocyte biconcave macro arc",
            "start_visual": "Hero shot of an eight-micrometer biconcave red blood cell suspended in golden plasma, glistening and supple, strictly zero text.",
            "end_visual": "Orbiting the flexible disc as it approaches the narrower six-micrometer capillary aperture under steady hemodynamic pressure, strictly zero text.",
            "subject_motion": "the biconcave disc tumbles gently through clear plasma, maintaining its smooth aerodynamic contour",
        },
        {
            "narration": "Under the influence of prolonged wakefulness and oxidative stress, red blood cell membranes become increasingly rigid and resistant to folding.",
            "camera_verb": "Membrane spectrin stiffening zoom",
            "start_visual": "High-magnification cutaway of erythrocyte membrane: spectrin protein cytoskeleton network under oxidative cross-linking, strictly zero text.",
            "end_visual": "Zooming into the spectrin mesh: rigid protein cross-links lock the membrane in place, drastically reducing cellular deformability, strictly zero text.",
            "subject_motion": "the flexible spectrin protein lattice becomes dense and rigid, restricting natural membrane deformation",
        },
        {
            "narration": "When these stiffened erythrocytes enter the narrow capillary entrance, they hesitate, causing acute microvascular traffic jams and sharp localized pressure spikes.",
            "camera_verb": "Capillary bottleneck jam tracking",
            "start_visual": "Constricted capillary entrance: a stiffened red blood cell lodges awkwardly against the vessel wall, blocking cells behind, strictly zero text.",
            "end_visual": "Tracking the backup: a queue of crimson erythrocytes stacks up tightly behind the bottleneck under rising upstream pressure, strictly zero text.",
            "subject_motion": "stiff red blood cells collide and stack together at the narrow vessel opening, creating an acute microvascular blockage",
        },
        {
            "narration": "To force these unyielding cells through, your cardiovascular system elevates upstream capillary pressure, subjecting fragile endothelial cells to intense shear stress.",
            "camera_verb": "Endothelial shear vector visualization",
            "start_visual": "3D view of capillary wall: high-velocity plasma jets squeezing around wedged cells, creating glowing red mechanical shear stress vectors, strictly zero text.",
            "end_visual": "Pushing along the stressed endothelial surface as mechanical friction strips away the protective delicate surface glycocalyx layer, strictly zero text.",
            "subject_motion": "luminous shear stress vectors flicker along the endothelial surface as trapped cells are forced through under pressure",
        },
        {
            "narration": "The protective endothelial glycocalyx, a lush sugar-protein forest coating the vessel interior, sheds rapidly under this relentless and abrasive mechanical grinding.",
            "camera_verb": "Glycocalyx degradation focus pull",
            "start_visual": "Extreme close-up on capillary interior: lush emerald green bush-like glycocalyx structures swaying in flowing plasma, strictly zero text.",
            "end_visual": "Focus pulling as high shear force strips glycocalyx strands away, exposing bare, vulnerable endothelial cell membrane underneath, strictly zero text.",
            "subject_motion": "emerald glycocalyx strands detach and fragment into the bloodstream, leaving bare endothelial patches behind",
        },
        {
            "narration": "With capillaries constricted and blood flow stalled, localized oxygen delivery to surrounding brain and muscle tissue drops by fifteen percent.",
            "camera_verb": "Tissue hypoxia color transition",
            "start_visual": "Macro view of cerebral parenchyma surrounding the blocked capillary: tissue glowing healthy oxygenated pink, strictly zero text.",
            "end_visual": "Transitioning as oxygen saturation falls: tissue hue shifts toward a desaturated hypoxic cyan-grey under severe cellular hypoxia, strictly zero text.",
            "subject_motion": "tissue luminosity dims and shifts from vibrant pink to dull cyan-grey as dissolved oxygen levels deplete",
        },
        {
            "narration": "Deprived of steady oxygen, neurons begin misfiring, manifesting outwardly as the sluggish reaction times and brain fog of sleep deprivation.",
            "camera_verb": "Synaptic misfire macro push",
            "start_visual": "Translucent view of cortical pyramidal neurons: electrical action potentials stuttering and dropping out along synaptic chains, strictly zero text.",
            "end_visual": "Pushing into a failing dendritic branch where action potential voltage collapses mid-pathway, failing to transmit critical information, strictly zero text.",
            "subject_motion": "action potential pulses flash erratically, sputtering and fading before reaching target synaptic boutons",
        },

        # Chapter 5: ch5_escalation (S33 - S40)
        {
            "narration": "By hour twenty without sleep, localized vascular strain escalates into a widespread systemic inflammatory cascade throughout your entire cardiovascular system.",
            "camera_verb": "Systemic vascular network sweep",
            "start_visual": "Wide 3D transparent human vascular model: major arteries and capillary networks pulsing with widespread amber-red inflammatory activation, strictly zero text.",
            "end_visual": "Sweeping down through mesenteric and renal vascular beds where endothelial activation spreads like wildfire across vessel walls, strictly zero text.",
            "subject_motion": "camera sweeps down through the glowing vascular tree as red inflammatory waves propagate through peripheral vessels",
        },
        {
            "narration": "Endothelial cells, stripped of their protective glycocalyx and battered by shear stress, begin rapidly expressing sticky adhesion molecules called selectin receptors.",
            "camera_verb": "Selectin adhesion molecule push-in",
            "start_visual": "Close-up on damaged endothelial surface: tiny Y-shaped selectin receptor proteins erupting across the cell membrane like velcro, strictly zero text.",
            "end_visual": "Pushing tight to the receptors as they project into the bloodstream, ready to snag passing white blood cells, strictly zero text.",
            "subject_motion": "thousands of tiny Y-shaped selectin molecules sprout rapidly from endothelial cell membranes into the plasma stream",
        },
        {
            "narration": "Passing neutrophils, normally gliding freely down the center of blood vessels, snag onto these selectins and begin rolling erratically along walls.",
            "camera_verb": "Neutrophil rolling tracking pass",
            "start_visual": "Endoscopic view of arteriole lumen: large spherical white neutrophils colliding with endothelial selectins along the vessel perimeter, strictly zero text.",
            "end_visual": "Tracking a neutrophil rolling slowly along the sticky endothelial surface, flattening out as it prepares for firm adhesion, strictly zero text.",
            "subject_motion": "spherical white neutrophils snag on vessel walls, rolling and tumbling along the sticky endothelial surface",
        },
        {
            "narration": "Integrin receptors lock the neutrophils firmly in place, where they flatten out and crawl between endothelial cell junctions into surrounding tissue.",
            "camera_verb": "Leukocyte extravasation macro push",
            "start_visual": "High-magnification view of flattened neutrophil firmly adhered to vessel wall: extending pseudopod between two endothelial cells, strictly zero text.",
            "end_visual": "Pushing tight as the neutrophil squeezes through the tight junction, releasing destructive proteases that weaken the vascular wall, strictly zero text.",
            "subject_motion": "the white blood cell squeezes its mass through the narrow endothelial gap, migrating out into surrounding tissue",
        },
        {
            "narration": "This inflammatory infiltration breaches the integrity of the blood-vessel barrier, causing plasma fluid and proteins to leak into interstitial spaces.",
            "camera_verb": "Microvascular leak fluid tracking",
            "start_visual": "Cross-section of a leaky post-capillary venule: clear protein-rich plasma fluid seeping through compromised endothelial gaps, strictly zero text.",
            "end_visual": "Tracking fluid accumulating in surrounding interstitial space: local tissues swell with microscopic inflammatory edema, strictly zero text.",
            "subject_motion": "clear fluid leaks continuously from between endothelial cells, forming pools of edema in the interstitial space",
        },
        {
            "narration": "In the liver, hepatocytes detect circulating inflammatory cytokines and rapidly accelerate production of C-reactive protein and clotting factors like fibrinogen.",
            "camera_verb": "Hepatic sinusoid synthesis push",
            "start_visual": "Nucleus 3D cutaway of liver liver lobule: hepatocytes bordering hepatic sinusoids actively packaging proteins into secretory vesicles, strictly zero text.",
            "end_visual": "Pushing into the sinusoid lumen as dense clouds of C-reactive protein and fibrous fibrinogen molecules discharge into blood, strictly zero text.",
            "subject_motion": "dense clouds of fibrinogen and CRP molecules erupt from liver cells, flooding directly into systemic circulation",
        },
        {
            "narration": "Fibrinogen makes your blood significantly thicker and more viscous, forcing your heart to work harder to maintain baseline systemic circulation.",
            "camera_verb": "Blood viscosity macro orbital",
            "start_visual": "Endoscopic view of blood flow inside a large vein: plasma thickening into a sluggish, syrupy consistency under high fibrinogen, strictly zero text.",
            "end_visual": "Orbiting the dense blood stream: red blood cells clumping together into long stacks called rouleaux formations, strictly zero text.",
            "subject_motion": "sluggish, viscous blood plasma flows with heavy resistance as red blood cells stack together like coins",
        },
        {
            "narration": "What began as a simple lack of sleep has now transformed into a full-body vascular state mimicking early-stage sepsis or trauma.",
            "camera_verb": "Full vascular inflammatory pull-back",
            "start_visual": "Microscopic view of congested capillaries transitioning into anatomical cutaway of major internal organs: liver, kidneys, and heart, strictly zero text.",
            "end_visual": "Pulling back as amber and crimson inflammatory markers illuminate every major organ bed under chronic cardiovascular overload, strictly zero text.",
            "subject_motion": "camera pulls back through translucent organ systems revealing widespread inflammatory stress throughout the body",
        },

        # Chapter 6: ch6_case_study_2 (S41 - S48)
        {
            "narration": "At hour twenty-two, systemic metabolic exhaustion strikes your endocrine system, triggering acute insulin resistance across skeletal muscle and liver tissue.",
            "camera_verb": "Insulin receptor macro push-in",
            "start_visual": "3D view of skeletal muscle cell membrane: Y-shaped insulin receptors protruding into interstitial fluid bathed in golden glucose molecules, strictly zero text.",
            "end_visual": "Pushing tight to an insulin receptor: inflammatory kinase enzymes phosphorylate internal receptor domains, completely blocking downstream signaling, strictly zero text.",
            "subject_motion": "insulin molecules bind to surface receptors, but internal phosphorylation defects prevent glucose channel opening",
        },
        {
            "narration": "Because insulin receptors are desensitized by cortisol and cytokines, glucose transporter channels fail to migrate outward to the cell membrane surface.",
            "camera_verb": "GLUT4 transporter vesicle tracking",
            "start_visual": "Inside muscle cell cytoplasm: glowing GLUT4 storage vesicles remaining immobilized near the nucleus instead of docking at membrane, strictly zero text.",
            "end_visual": "Tracking the cell membrane: surface remains bare of glucose channels, leaving extracellular glucose stranded outside the cell, strictly zero text.",
            "subject_motion": "glucose transport vesicles remain trapped deep inside cytoplasm, unable to reach the cell membrane",
        },
        {
            "narration": "Glucose molecules accumulate dangerously in the bloodstream, while cellular powerhouses inside your muscle fibers starve for essential metabolic carbohydrate fuel.",
            "camera_verb": "Vascular hyperglycemia macro pass",
            "start_visual": "Bloodstream crowded with glowing golden glucose hexagons drifting alongside erythrocytes without being absorbed into surrounding muscle, strictly zero text.",
            "end_visual": "Gliding past exhausted muscle fibers whose intracellular mitochondria slow their ATP production due to substrate starvation, strictly zero text.",
            "subject_motion": "golden glucose crystals accumulate in dense clusters within the bloodstream while muscle cells display low energy",
        },
        {
            "narration": "Simultaneously, circulating blood platelets become hyper-reactive, their surface membranes expressing activation markers that actively promote dangerous micro-clot formation throughout vessels.",
            "camera_verb": "Platelet activation dynamic push",
            "start_visual": "Close-up on resting discoid blood platelets floating in plasma: smooth surfaces and inactive granule storage compartments, strictly zero text.",
            "end_visual": "Pushing into a platelet as it detects endothelial collagen: sprouting long spider-like pseudopods and exposing sticky GP IIb/IIIa receptors, strictly zero text.",
            "subject_motion": "smooth disc-shaped platelets rapidly transform into spiky, adhesive cells with extended pseudopods",
        },
        {
            "narration": "Activated platelets bind to exposed subendothelial collagen fibers, releasing thromboxane A2 to recruit even more adhesive platelets into growing vascular aggregates.",
            "camera_verb": "Platelet plug aggregation arc",
            "start_visual": "Damaged endothelial gap where collagen is exposed: activated platelets anchoring firmly to the fibrous structural matrix, strictly zero text.",
            "end_visual": "Orbiting the forming micro-thrombus as incoming platelets adhere to one another, creating a web of fibrin threads, strictly zero text.",
            "subject_motion": "activated platelets pile rapidly on top of each other, binding together with glistening fibrin mesh strands",
        },
        {
            "narration": "Fibrin strands polymerize across the platelet plug, trapping red blood cells and creating tiny obstructive micro-thrombi inside peripheral capillary vascular networks.",
            "camera_verb": "Micro-thrombus fibrin mesh zoom",
            "start_visual": "High-magnification view of growing clot: glowing white fibrin strands weaving tightly around trapped crimson erythrocytes, strictly zero text.",
            "end_visual": "Zooming into the capillary lumen: the micro-thrombus occludes seventy percent of the cross-sectional area, restricting local perfusion, strictly zero text.",
            "subject_motion": "white fibrin threads tighten around trapped blood cells, forming a dense plug inside the narrow vessel",
        },
        {
            "narration": "While healthy bodies dissolve these micro-clots quickly, sleep deprivation impairs natural fibrinolysis, leaving delicate micro-vessels chronically occluded and starved of flow.",
            "camera_verb": "Impaired fibrinolysis tracking pass",
            "start_visual": "Macro view of trapped micro-clot: tissue plasminogen activator molecules approaching the fibrin mesh in insufficient quantities, strictly zero text.",
            "end_visual": "Tracking the persistent clot: fibrin mesh remains intact and un-cleaved, leaving downstream tissue perpetually under-perfused, strictly zero text.",
            "subject_motion": "cleaving enzymes fail to dissolve the fibrin network, allowing the microscopic clot to persist inside the lumen",
        },
        {
            "narration": "By hour twenty-two, your vascular tree is operating on borrowed time, increasingly vulnerable to sudden focal ischemia and severe microvascular collapse.",
            "camera_verb": "Microvascular occlusion pull-back",
            "start_visual": "Close-up on occluded micro-vessel transitioning into wide 3D anatomical view of peripheral capillary beds in limbs and torso, strictly zero text.",
            "end_visual": "Pulling back as multiple tiny focal points of microvascular occlusion glow with ischemic warning hues across the body, strictly zero text.",
            "subject_motion": "camera pulls back revealing scattered microscopic vascular bottlenecks throughout the human anatomy",
        },

        # Chapter 7: ch7_systemic_shift (S49 - S56)
        {
            "narration": "As the twenty-fourth hour without sleep arrives, your cardiovascular system suffers severe, unremitting autonomic and hemodynamic strain throughout every major artery.",
            "camera_verb": "Cardiac anatomy 3D orbital",
            "start_visual": "Nucleus 8K anatomical cutaway of human heart: left ventricle pumping forcefully against high systemic vascular resistance, strictly zero text.",
            "end_visual": "Orbiting the myocardium: coronary arteries branching across the epicardium pulse with elevated wall stress and turbulent flow, strictly zero text.",
            "subject_motion": "the heart muscle contracts with increased mechanical force, shuddering slightly against elevated arterial backpressure",
        },
        {
            "narration": "Sympathetic nervous system drive remains locked on full throttle, constantly flooding myocardial cells with noradrenaline without essential nocturnal parasympathetic recovery.",
            "camera_verb": "Myocardial sympathetic junction push",
            "start_visual": "Microscopic view of cardiac sympathetic nerve terminals releasing clouds of noradrenaline directly onto cardiac muscle fibers, strictly zero text.",
            "end_visual": "Pushing into myocardial beta-receptors: calcium channels remain forcefully open, driving rapid, unceasing intracellular calcium cycling, strictly zero text.",
            "subject_motion": "noradrenaline molecules bombard myocardial receptors, triggering intense fluorescent calcium surges within muscle cells",
        },
        {
            "narration": "Inside cardiac myocytes, overworked cellular mitochondria produce excessive reactive oxygen species, causing subtle micro-damage to the delicate contractile sarcomere protein filaments.",
            "camera_verb": "Myocyte sarcomere macro cutaway",
            "start_visual": "Extreme close-up inside cardiac muscle fiber: interlocking actin and myosin protein filaments sliding past each other rapidly, strictly zero text.",
            "end_visual": "Cutaway to intracellular mitochondria: glowing red oxidative free radicals escaping from electron transport chains into myofibrils, strictly zero text.",
            "subject_motion": "actin and myosin filaments slide forcefully while red oxidative sparks disperse into surrounding cytoplasm",
        },
        {
            "narration": "Your blood pressure now averages ten to fifteen millimeters of mercury higher than normal, completely abolishing the healthy nocturnal dip.",
            "camera_verb": "Aortic arch pressure wave track",
            "start_visual": "Endoscopic view inside the ascending aorta: massive crimson blood bolus ejecting from aortic valve under high systolic pressure, strictly zero text.",
            "end_visual": "Tracking the pressure pulse down the aortic arch: stiff arterial walls reflect back intense wave echoes, straining the left ventricle, strictly zero text.",
            "subject_motion": "pulsatile pressure waves surge down the aorta, bouncing violently against stiffened peripheral vascular walls",
        },
        {
            "narration": "In the kidneys, renal arterioles constrict forcefully to protect delicate glomeruli from hypertension, inadvertently reducing glomerular filtration rates by ten percent.",
            "camera_verb": "Renal glomerulus micro-push",
            "start_visual": "3D cutaway of a kidney nephron: afferent arteriole feeding into the dense capillary ball of Bowman's capsule, strictly zero text.",
            "end_visual": "Pushing into the glomerulus: afferent arteriole tightly constricts, reducing blood filtration and causing metabolic waste retention, strictly zero text.",
            "subject_motion": "the feeding renal arteriole constricts tightly, visibly slowing fluid filtration through glomerular capillary loops",
        },
        {
            "narration": "In the brain, micro-sleep events begin occurring at the cellular level: isolated neuronal clusters literally power down for hundreds of milliseconds.",
            "camera_verb": "Cortical micro-sleep focal dropout",
            "start_visual": "Translucent 3D view of cerebral cortex: hundreds of firing neural networks flickering cyan, with one isolated focal patch suddenly going pitch black, strictly zero text.",
            "end_visual": "Tracking across the dormant cluster: neurons enter momentary quiescent slow-wave states while surrounding circuits continue firing erratically, strictly zero text.",
            "subject_motion": "a distinct patch of cortical neurons shuts down completely for a second before flickering back to erratic wakefulness",
        },
        {
            "narration": "During these micro-sleep lapses, sensory processing completely disconnects, explaining why sleep-deprived individuals experience catastrophic and dangerous lapses in situational awareness.",
            "camera_verb": "Thalamocortical sensory gate tracking",
            "start_visual": "Cutaway of the thalamus: incoming sensory electrical signals arriving from optical and auditory nerves, strictly zero text.",
            "end_visual": "Tracking signals to the thalamocortical gate: transmission lines shut down mid-conduction, blocking sensory data from reaching the cortex, strictly zero text.",
            "subject_motion": "streaming sensory impulses hit a closed neurological gating barrier, dissolving into static without reaching higher centers",
        },
        {
            "narration": "Your body has reached the outer perimeter of biological endurance; without immediate sleep, permanent structural vascular damage becomes imminent and irreversible.",
            "camera_verb": "Total anatomy systemic pull-back",
            "start_visual": "Macro view of stressed cerebral capillary beds transitioning into wide anatomical visualization of full human body, strictly zero text.",
            "end_visual": "Pulling back into dark cinematic void as the exhausted, glowing vascular silhouette of the human body pulses with emergency amber light, strictly zero text.",
            "subject_motion": "camera pulls back into a grand full-body anatomical view revealing universal cardiovascular and neurological exhaustion",
        },

        # Chapter 8: ch8_resolution (S57 - S64)
        {
            "narration": "Finally, the moment your eyes close and sleep takes hold, a magnificent physiological rescue operation initiates across every organ system.",
            "camera_verb": "Nocturnal transition ambient shift",
            "start_visual": "Cinematic 3D anatomical view of brain: chaotic amber and red stress hues smoothly transitioning into a serene, soothing deep indigo-blue, strictly zero text.",
            "end_visual": "Gliding across the cerebral cortex as erratic electrical spikes give way to synchronized, sweeping delta brain waves, strictly zero text.",
            "subject_motion": "chaotic rapid electrical flickering calms smoothly into broad, rhythmic waves of soothing indigo luminescence",
        },
        {
            "narration": "Deep slow-wave delta sleep begins, triggering your parasympathetic vagus nerve to release calming acetylcholine and rapidly decelerate cardiac pumping output.",
            "camera_verb": "Vagal cardiac slowing push-in",
            "start_visual": "Endoscopic view of cardiac sinoatrial node: glowing cyan acetylcholine molecules showering from vagal nerve terminals, strictly zero text.",
            "end_visual": "Pushing toward cardiac muscle: pacemaker firing intervals lengthen smoothly, dropping heart rate into a calm, restorative rhythm, strictly zero text.",
            "subject_motion": "cyan neurotransmitter molecules calm the pacemaker cells, slowing heart muscle contractions into a steady, peaceful cadence",
        },
        {
            "narration": "Systemic blood vessels dilate instantly as sympathetic tone collapses, allowing stiff arterial walls to rest and re-establish their supple natural elasticity.",
            "camera_verb": "Arteriole vasodilation smooth track",
            "start_visual": "Endoscopic view inside a previously constricted peripheral arteriole: smooth muscular wall relaxing and expanding outward, strictly zero text.",
            "end_visual": "Tracking the widened lumen: smooth laminar blood flow restores, eliminating turbulent shear stress and calming endothelial friction, strictly zero text.",
            "subject_motion": "arteriole walls expand smoothly, doubling the lumen area and restoring calm laminar blood circulation",
        },
        {
            "narration": "Most dramatically, inside the brain, glial cells shrink dramatically by sixty percent, reopening the dormant glymphatic floodgates in full force.",
            "camera_verb": "Glymphatic floodgate reopening push",
            "start_visual": "Macro view of perivascular channels around cerebral vessels: swollen astrocytes shrinking away, widening interstitial spaces fourfold, strictly zero text.",
            "end_visual": "Pushing into the opened channel as crystal-clear cerebrospinal fluid rushes through in powerful cleansing convective waves, strictly zero text.",
            "subject_motion": "astrocytes shrink dramatically as torrents of clear cleansing fluid sweep through newly opened interstitial channels",
        },
        {
            "narration": "Pulsatile waves of cerebrospinal fluid wash through the parenchyma, sweeping away beta-amyloid, tau proteins, and accumulated adenosine into venous drainage channels.",
            "camera_verb": "Metabolic waste flush orbital",
            "start_visual": "Interlocking neural networks: powerful convective currents of clear fluid dislodging amber beta-amyloid plaques from dendritic branches, strictly zero text.",
            "end_visual": "Orbiting the cleansing current as toxic peptides and metabolic waste dissolve into fluid and flush into dural venous sinuses, strictly zero text.",
            "subject_motion": "powerful fluid waves sweep amber waste particles effortlessly out of synaptic crevices toward venous drainage canals",
        },
        {
            "narration": "Endothelial cells immediately activate nitric oxide synthesis, repairing damaged glycocalyx surface forests and restoring tight junctions between neighboring vascular cells.",
            "camera_verb": "Glycocalyx regrowth micro-zoom",
            "start_visual": "Extreme close-up on bare capillary wall: fresh emerald green glycocalyx proteoglycans rapidly sprouting and branching outward, strictly zero text.",
            "end_visual": "Zooming along the lush restored forest: tight junction proteins seal gaps between cells, completely halting fluid leakage, strictly zero text.",
            "subject_motion": "lush emerald glycocalyx filaments regrow rapidly across the endothelial surface, creating a pristine protective carpet",
        },
        {
            "narration": "Erythrocyte membranes recover their natural flexibility, and insulin receptors resensitize, rapidly replenishing depleted cellular glycogen reserves throughout resting muscle tissue.",
            "camera_verb": "Cellular recovery macro glide",
            "start_visual": "Macro view of red blood cells passing effortlessly through capillaries, folding and flexing with perfect elastic grace, strictly zero text.",
            "end_visual": "Gliding to skeletal muscle: insulin receptors active again, transporting golden glucose smoothly into cytoplasm to recharge mitochondria, strictly zero text.",
            "subject_motion": "flexible red blood cells glide seamlessly through narrow vessels while glucose channels open smoothly to nourish cells",
        },
        {
            "narration": "Sleep is not merely a passive mental pause; it is the vital biological engineering required to keep your body alive.",
            "camera_verb": "Grand anatomical harmony pull-back",
            "start_visual": "Cinematic wide 3D visualization: human body glowing in serene indigo and gold harmony, circulatory and neural networks restored, strictly zero text.",
            "end_visual": "Pulling back into tranquil velvet void: the restored biological masterpiece pulses with calm, perfect life, strictly zero text.",
            "subject_motion": "camera rises gracefully away as the glowing, harmonious human circulatory network pulses in serene health",
        },
    ]

    shots: List[Dict[str, Any]] = []
    for idx, raw in enumerate(raw_shots_data):
        shot_num = idx + 1
        ch_idx = idx // 8
        ch_name, _ = chapters[ch_idx]
        pos_in_ch = idx % 8

        continues = pos_in_ch not in (0, 4)

        if pos_in_ch == 7:
            pause = 0.55
        elif pos_in_ch == 3:
            pause = 0.40
        else:
            pause = 0.36

        words = raw["narration"].strip().split()
        if not (20 <= len(words) <= 23):
            raise ValueError(f"Shot S{shot_num:02d} has {len(words)} words; must be 20-23 words: {raw['narration']}")

        shots.append(
            {
                "shot_id": f"S{shot_num:02d}",
                "scene_group": ch_name,
                "continues_prev": continues,
                "scene_anchor": scene_anchor_base,
                "narration": raw["narration"],
                "speech_rate": "+8%",
                "pause_after_sec": pause,
                "camera_verb": raw["camera_verb"],
                "start_visual": raw["start_visual"],
                "end_visual": raw["end_visual"],
                "subject_motion": raw["subject_motion"],
            }
        )

    return {
        "job_id": "en-inside-vessel-batch1-16x9",
        "channel_slug": "en-inside-vessel",
        "aspect": "16:9",
        "title": "24 Hours Without Sleep: Hour-by-Hour Organ & Micro-Capillary Breakdown Inside Your Body",
        "youtube_title": "Inside Your Body During 24 Hours Awake",
        "voice": "en-US-EricNeural",
        "thumbnail_spec": {
            "visual_hook": "Translucent 3D medical cutaway of cerebral capillaries and glowing neurons accumulating amber metabolic waste plaques",
            "allowed_text": "24 HOURS AWAKE",
            "overlay_card": False,
        },
        "shots": shots,
    }


def get_inside_vessel_short() -> Dict[str, Any]:
    scene_anchor_base = (
        "Nucleus Medical Media 8K 3D endoscopic biomedical cinematography with glistening subsurface tissue textures "
        "and clean surgical fiber-optic rim lighting, strictly zero text labels"
    )

    # 7 shots, 13 to 15 words per shot, parent_long_id: en-inside-vessel-batch1-16x9
    raw_shots = [
        {
            "shot_id": "S01",
            "scene_group": "G1",
            "continues_prev": False,
            "narration": "Human capillaries are mere hair-thin tunnels, half the diameter of the blood cells entering them.",  # 15 words
            "pause_after_sec": 0.34,
            "camera_verb": "Endoscopic capillary approach push",
            "start_visual": "Nucleus Medical Media 9:16 vertical shot: endoscopic view inside a narrowing arteriole branching into microscopic capillaries, strictly zero text.",
            "end_visual": "Approaching the tiny six-micrometer capillary entrance where blood plasma accelerates into the bottleneck, strictly zero text.",
            "subject_motion": "camera navigates down the narrowing vessel toward the hair-thin capillary entrance",
        },
        {
            "shot_id": "S02",
            "scene_group": "G1",
            "continues_prev": True,
            "narration": "An eight-micrometer red blood cell must physically deform to squeeze into the narrow passage.",  # 14 words
            "pause_after_sec": 0.36,
            "camera_verb": "Erythrocyte deformation macro push",
            "start_visual": "Vertical view of an eight-micrometer biconcave disc red blood cell approaching the six-micrometer vessel mouth, strictly zero text.",
            "end_visual": "Pushing closer as the flexible red cell compresses against the entrance, folding like a parachute, strictly zero text.",
            "subject_motion": "the biconcave disc deforms elastically into an elongated bullet shape to enter the tube",
        },
        {
            "shot_id": "S03",
            "scene_group": "G2",
            "continues_prev": False,
            "narration": "Inside the cell membrane, elastic spectrin protein networks stretch without breaking under crushing pressures.",  # 14 words
            "pause_after_sec": 0.34,
            "camera_verb": "Membrane spectrin cytoskeleton zoom",
            "start_visual": "Macro cutaway through erythrocyte membrane: glowing hexagonal spectrin protein cytoskeleton stretching under tension, strictly zero text.",
            "end_visual": "Zooming into the flexible protein coils as they deform smoothly without tearing or losing structural integrity, strictly zero text.",
            "subject_motion": "the hexagonal protein mesh stretches and elongates along the lines of mechanical stress",
        },
        {
            "shot_id": "S04",
            "scene_group": "G2",
            "continues_prev": True,
            "narration": "Tightly pressed against the vessel wall, the cell unloads oxygen molecules in milliseconds.",  # 13 words
            "pause_after_sec": 0.36,
            "camera_verb": "Gas exchange molecular focus pull",
            "start_visual": "Close-up inside the capillary: folded red blood cell sliding against glistening endothelial wall, strictly zero text.",
            "end_visual": "Focus pulling to glowing cyan oxygen molecules diffusing across the ultra-thin vessel wall into tissue, strictly zero text.",
            "subject_motion": "cyan oxygen molecules detach from hemoglobin and diffuse across the translucent capillary membrane",
        },
        {
            "shot_id": "S05",
            "scene_group": "G3",
            "continues_prev": False,
            "narration": "Exiting the bottleneck into wider venules, the resilient cell snaps back into shape.",  # 13 words
            "pause_after_sec": 0.34,
            "camera_verb": "Venule expansion tracking pass",
            "start_visual": "Vertical shot of capillary widening into a venule: elongated red blood cell emerging from narrow tunnel, strictly zero text.",
            "end_visual": "Tracking the cell as elastic tension instantly restores its classic biconcave disc geometry, strictly zero text.",
            "subject_motion": "the elongated cell rebounds instantly into its symmetrical biconcave disc shape upon entering the venule",
        },
        {
            "shot_id": "S06",
            "scene_group": "G3",
            "continues_prev": True,
            "narration": "Your body performs this miraculous microscopic folding acrobatics billions of times every single second.",  # 14 words
            "pause_after_sec": 0.36,
            "camera_verb": "Microvascular network sweep",
            "start_visual": "Wide 9:16 vertical view of glowing capillary beds throughout human muscle tissue, strictly zero text.",
            "end_visual": "Sweeping across the dense microvascular network as millions of cells fold and glide in perfect harmony, strictly zero text.",
            "subject_motion": "thousands of red blood cells squeeze continuously through the shimmering capillary meshwork",
        },
        {
            "shot_id": "S07",
            "scene_group": "G4",
            "continues_prev": False,
            "narration": "Explore the complete hour-by-hour vascular breakdown in our full deep-dive video linked below.",  # 13 words
            "pause_after_sec": 0.25,
            "camera_verb": "Grand anatomical harmony pull-back",
            "start_visual": "Vertical anatomical view: glowing human cardiovascular silhouette illuminated by fiber-optic rim light, strictly zero text.",
            "end_visual": "Pulling back into deep navy background as the complete vascular tree pulses peacefully in unison, strictly zero text.",
            "subject_motion": "camera glides smoothly away as the luminous human circulatory system pulses with gentle life",
        },
    ]

    for s in raw_shots:
        s["scene_anchor"] = scene_anchor_base
        w_cnt = len(s["narration"].strip().split())
        if not (13 <= w_cnt <= 15):
            raise ValueError(f"Shot {s['shot_id']} has {w_cnt} words; must be 13-15 words: {s['narration']}")

    return {
        "job_id": "en-inside-vessel-batch1-9x16",
        "parent_long_id": "en-inside-vessel-batch1-16x9",
        "channel_slug": "en-inside-vessel",
        "aspect": "9:16",
        "title": "The Hair-Thin Bottleneck: How Red Blood Cells Fold to Survive Crushing Capillary Pressure",
        "youtube_title": "How Blood Cells Squeeze Through Capillaries",
        "voice": "en-US-EricNeural",
        "shots": raw_shots,
    }
