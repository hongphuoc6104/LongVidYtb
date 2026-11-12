"""Worker 2: Rebuild Long Specs for Batch 1 Channels:
1. chanh_niem_ke (70 beats)
2. co_the_ke (117 beats)
3. dia_com (117 beats)

Produces 100% story-aligned English visual scene descriptions adhering strictly to:
- 0% generic boilerplate (NEVER use "clearly demonstrating the cause-and-effect explanatory mechanism").
- 0% Vietnamese diacritics (pure ASCII English).
- 0% 8k / 4k / photorealistic buzzwords.
- 0% text overlays / labels / logos.
- 100% unique scene descriptions across all beats in each channel.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

from sys.tools.batch1_spec_builder import compile_and_save_spec

ROOT_DIR = Path(__file__).resolve().parents[2]

# ==============================================================================
# 1. chanh_niem_ke: 70 beats
# Style: Cinematic Wabi-Sabi & Zen Sumi-e mindfulness visual
# ==============================================================================
CHANH_NIEM_KE_BEATS: Dict[str, str] = {
    # CH01: Cơn Mưa Trong Lòng & Chiếc Ly Đầy Nước (6 beats)
    "CH01_A01": "A contemplative figure sitting quietly on an aged cedar veranda watching gentle afternoon rain fall upon a serene bamboo garden, droplets streaking down a cold frosted glass window pane",
    "CH01_A02": "Dark rolling storm clouds gathering over a misty distant mountain ridge while a faint silhouette sits exhausted on worn tatami flooring, feeling the invisible weight of mental turbulence",
    "CH01_A03": "An antique wooden clock on a rustic wall surrounded by scattered scrolls and tangled ink strokes, depicting the restless racing thoughts between future anxieties and past regrets",
    "CH01_A04": "A clear glass tumbler filled to the absolute brim with water resting upon a polished ebony wooden table, the convex liquid meniscus trembling with surface tension",
    "CH01_A05": "A single crystalline water droplet hanging in mid-air just above the bulging water surface of the brimful glass, on the verge of causing water to overflow onto dark wood",
    "CH01_A06": "An overflowing water glass with droplets cascading across the dark wood grain surface, capturing the burdened and saturated mental state overwhelmed by imaginary worries",

    # CH02: Nguồn Gốc Của Những Nỗi Lo Không Tên (6 beats)
    "CH02_A01": "Twilight falling over weathered moss-covered stone lanterns in a quiet temple courtyard, where cool blue evening shadows gently embrace rustic gravel paths",
    "CH02_A02": "Ancient prehistoric hunter cautiously peering through dense primeval mist toward rustling forest shadows, evolutionary survival instinct heightened by snapping dry twigs",
    "CH02_A03": "A tranquil wooden tearoom illuminated by soft diffused daylight with bamboo blinds, contrasting ancient wilderness survival mechanisms with modern unnecessary distress",
    "CH02_A04": "A flickering traditional oil lamp casting distorted monstrous shadows onto weathered paper shoji screens, revealing how the frightened mind conjures imaginary beasts",
    "CH02_A05": "A silhouette kneeling before an hourglass with sand slipping away, trapped between phantom visions of tomorrow and immutable fading memories of yesterday",
    "CH02_A06": "A solitary autumn leaf resting motionless on the glassy mirror surface of a still garden pond, embodying the profound peace of the present moment",

    # CH03: Khoảng Trống Giữa Kích Thích & Phản Ứng (7 beats)
    "CH03_A01": "A vast serene horizon where gentle morning mist separates rolling mountains and a still reflective lake, illustrating the natural pause between an external stimulus and an inner response",
    "CH03_A02": "A solitary crystal raindrop pausing delicately on the curved edge of an antique moss-covered roof tile before falling through quiet morning air",
    "CH03_A03": "A rustic bamboo water fountain gently rocking as water accumulates, capturing the sacred stillness where inner freedom and emotional self-governance originate",
    "CH03_A04": "A traditional bamboo shishi-odoshi fountain clacking softly against river rock, while turbulent choppy water downstream contrasts with the steady rhythmic flow above",
    "CH03_A05": "A mindful practitioner stepping back one deliberate step onto weathered stepping stones, calmly observing swirling fallen leaves without being swept away",
    "CH03_A06": "A tiny ember on an incense stick glowing softly in a ceramic burner, its hot red spark gently cooling down into calm grey ash after three mindful seconds",
    "CH03_A07": "A calm solitary bird perched steadfastly on a weathered pine branch as autumn wind rustles the surrounding needles, choosing peace over frantic agitation",

    # CH04: Cạm Bẫy Của Việc Cố Kiểm Soát Mọi Thứ (8 beats)
    "CH04_A01": "Sunset golden rays illuminating precisely raked patterns of white sand in a Zen dry rock garden, where a hand reaches down to scoop a tight mound of fine sand",
    "CH04_A02": "A tightly clenched fist with streams of fine white sand escaping through finger crevices, demonstrating how forceful grasping causes life to slip away faster",
    "CH04_A03": "Unpredictable river currents swirling around ancient granite river boulders, symbolizing life's unyielding nature that cannot be coerced by human will",
    "CH04_A04": "Weathered wooden prayer beads resting on a cracked table next to clenched fingers, representing the deep exhaustion borne from clinging to total control",
    "CH04_A05": "An open relaxed hand turned upward in warm golden twilight, resting peacefully without clutching or grasping",
    "CH04_A06": "Grains of fine golden sand resting calmly on an open flat palm, preserved effortlessly without tension or forced grip",
    "CH04_A07": "A serene wooden footbridge spanning a flowing stream, symbolizing the peaceful surrender of ceasing a futile struggle against life's natural flow",
    "CH04_A08": "A smooth river stone resting deeply at the bottom of a tranquil mountain creek, embracing the surrounding water currents without resistance",

    # CH05: Hơi Thở Như Mỏ Neo Của Thực Tại (8 beats)
    "CH05_A01": "A traditional Japanese archery dojo where an archer releases an arrow flying toward a distant straw target, capturing life's primary unavoidable physical pain",
    "CH05_A02": "A wooden target struck by a single arrow, while dark swirling mist forms a phantom second arrow fired by our own spiraling thoughts and self-inflicted misery",
    "CH05_A03": "A calm meditator seated on a woven rush mat beside a peaceful open sliding door, turning inward to feel the gentle rising and falling rhythm of the chest",
    "CH05_A04": "Visual metaphor of ocean tides gently lapping against a smooth sandy shore, mirroring the natural rhythmic cadence of conscious deep breathing",
    "CH05_A05": "Soft cool morning breeze gently rustling fine linen curtains near a window, visualizing the cool touch of incoming air at the tip of the nose",
    "CH05_A06": "Gentle warm vapor drifting from an earthy ceramic tea bowl into cool morning air, representing warm exhale carrying away accumulated internal tension",
    "CH05_A07": "A sturdy iron anchor resting serenely on the sandy seabed amid swaying seagrass, symbolizing breath as the steadfast anchor of present-moment awareness",
    "CH05_A08": "A solitary wooden boat moored securely to a rustic wooden post in calm sheltered harbor waters, untouched by open ocean swells",

    # CH06: Cú Lật Ngược: Chấp Nhận Không Phải Là Bỏ Cuộc (8 beats)
    "CH06_A01": "A pristine white lotus flower blooming gracefully above dark murky pond water, its pristine petals untouched by the surrounding deep mud",
    "CH06_A02": "Lotus roots anchored deeply within nutrient-rich river silt while pure dewdrops glisten on expansive green floating pads above",
    "CH06_A03": "A traveler walking patiently along a narrow mountain path through swirling morning fog, accepting the misty veil without fighting the weather",
    "CH06_A04": "Soft billowing white clouds drifting serenely across a vast empty blue sky, symbolizing transient emotions passing through spacious awareness without leaving a trace",
    "CH06_A05": "Mountain creek water flowing gracefully around smooth mossy granite boulders, finding natural pathways around obstacles rather than crashing with blunt force",
    "CH06_A06": "A resilient green bamboo stalk bending gracefully under the heavy weight of winter snow without snapping, demonstrating supple strength through acceptance",
    "CH06_A07": "An old cedar tree with deep twisted roots standing tall on a breezy plateau, weathering gusts through deep rooted stillness",
    "CH06_A08": "A tranquil stone garden bench bathed in soft morning sidelight, offering an open invitation to rest in effortless acceptance",

    # CH07: Nghệ Thuật Đi Dạo Không Mục Đích (8 beats)
    "CH07_A01": "A winding cobblestone pathway meandering through an overgrown fern and moss forest without any signposts, welcoming an aimless peaceful stroll",
    "CH07_A02": "A person leaving a buzzing electronic device on a rustic wooden console before stepping barefoot onto a sun-dappled timber threshold",
    "CH07_A03": "Bare feet walking slowly and deliberately across soft green velvet moss and smooth river pebbles along an ancient garden path",
    "CH07_A04": "Looking up into a luminous canopy of translucent green maple leaves dappled by warm afternoon sunlight, freeing the mind from analytical calculation",
    "CH07_A05": "An exquisite antique ceramic tea bowl repaired with Kintsugi golden lacquer seams, celebrating cracks as luminous veins of unique enduring beauty",
    "CH07_A06": "Close-up of delicate golden lacquer lines bridging fractured earthenware edges, symbolizing wounded human spirit illuminated by compassionate acceptance",
    "CH07_A07": "A weathered handmade clay vessel cradled tenderly by two hands in soft morning light, honoring every imperfection and seasoned texture",
    "CH07_A08": "A sunlit clearing beneath an ancient weeping willow tree in a quiet neighborhood park, where gentle breezes return spacious freedom to the wandering mind",

    # CH08: Dọn Dẹp Không Gian Để Gột Rửa Tâm Trí (8 beats)
    "CH08_A01": "A serene mountain valley at dawn with morning mist rising between cedar trees, embodying mindfulness embedded in ordinary daily movements rather than remote seclusion",
    "CH08_A02": "A cluttered rustic desk covered in scattered papers, tipped inkpots, and forgotten artifacts, visually mirroring internal cognitive overwhelm and visual fatigue",
    "CH08_A03": "Hands carefully smoothing a clean neutral-toned linen blanket into neat crisp folds, then gently dusting a dark polished walnut tabletop with a soft cotton cloth",
    "CH08_A04": "Hands gently washing a rustic stoneware tea bowl under a thin stream of clear well water, feeling cooling droplets and delicate soap bubbles on skin",
    "CH08_A05": "Two hands mindfully raising a warm handmade stoneware teacup toward the lips, savoring the subtle bittersweet aroma rising in morning stillness",
    "CH08_A06": "A delicate ribbon of pale white steam swirling lazily through a golden sunbeam illuminating an uncluttered minimalist wooden room",
    "CH08_A07": "Spent tea leaves settling gently into the bottom of a glazed ceramic teapot in still amber water, representing settling anxieties and quieted thoughts",
    "CH08_A08": "A luminous, impeccably tidy minimalist wooden tatami room opening toward a tranquil rain-washed courtyard, restoring boundless openness to the mind",

    # CH09: Ba Câu Hỏi Tự Vấn Mỗi Khi Lo Lắng Tấn Công (7 beats)
    "CH09_A01": "Gathering storm clouds drifting over a tranquil mountain ridge, while an observer stands on a wooden pavilion pausing for a deep grounding breath",
    "CH09_A02": "A wide panoramic view of a calm mountain peak towering serenely above shifting valley mist, illustrating serenity beyond things outside personal control",
    "CH09_A03": "Ancient eroded river stones worn smooth by centuries of flowing water, reminding the spirit that present worries will fade like transient dust motes in five years",
    "CH09_A04": "A person setting down a heavy wicker basket and stepping forward onto solid stone earth, focusing on the smallest immediate practical action",
    "CH09_A05": "Pouring warm water from a cast iron kettle into a ceramic cup, alongside a wooden desk where a fountain pen rests upon a small strip of textured paper",
    "CH09_A06": "A hand writing single honest words onto textured washi paper with dark black ink, externalizing anxiety to dissolve phantom fears into manageable reality",
    "CH09_A07": "A bedside wooden nightstand with a gentle amber candle glow, an open blank journal, and dried lavender sprigs inviting grateful peaceful reflection before sleep",

    # CH10: Tìm Lại Sự Bình Yên Bên Trong Bạn (4 beats)
    "CH10_A01": "Bustling noisy city streets blurred in distant background haze, while a quiet secluded garden path leads toward an inviting sheltered wooden tea house",
    "CH10_A02": "A subterranean crystal-clear pool inside a quiet cave, perfectly motionless and undisturbed by roaring winds and storms howling on the mountain summit above",
    "CH10_A03": "A tranquil profile portrait of a person softly closing their eyes, taking a gentle deep breath as warm golden morning sidelight bathes peaceful features",
    "CH10_A04": "An ancient mossy stone basin reflecting a patch of luminous golden sunrise sky, filled with deep warmth, boundless compassion, and immutable quiet peace",
}


# ==============================================================================
# 2. co_the_ke: 117 beats
# Style: High-definition 3D biomedical anatomical animation still
# ==============================================================================
CO_THE_KE_BEATS: Dict[str, str] = {
    # CH01: 24 Giờ Thức Trắng: Bộ Não Bắt Đầu Cầu Cứu (10 beats)
    "CH01_A01": "Anatomical view of a human face in dark room, where drooping heavy eyelids struggle under midnight exhaustion while a cold intense blue beam from a smartphone screen strikes the exposed cornea",
    "CH01_A02": "Close-up of the human eye showing tired ocular muscles, a digital clock reading 3 AM reflected in the glassy pupil, and tiny red capillary vessels beginning to dilate across the sclera",
    "CH01_A03": "Microscopic surface of the cornea showing the natural tear film evaporating into dry patches, causing burning friction during every slow eyelid blink while temporal blood vessels throb",
    "CH01_A04": "A person sitting at a desk rubbing tired temples next to a steaming mug of black espresso, falsely believing caffeine can reverse systemic physiological breakdown",
    "CH01_A05": "Sagittal cross-section of the human cranium illuminating billions of strained cortical neurons flashing erratic distressed electrical impulses as intracellular ATP energy stores deplete",
    "CH01_A06": "High-magnification cutaway of a neural synapse where dense clusters of adenosine fatigue molecules accumulate and overwhelm receptor sites, paralyzing signal transmission",
    "CH01_A07": "Motor cortex cutaway showing sluggish delayed electrochemical discharges traveling down motor axons, resulting in trembling fingers and dangerously slowed physical reflexes",
    "CH01_A08": "Visual processing pathway in the occipital lobe struggling to decode repeated text lines, while overactivated microglia begin swarming surrounding neural tissue",
    "CH01_A09": "Cellular view of hungry microglial scavenger cells relentlessly pruning healthy synaptic terminals and dendritic spines after twenty-four continuous hours of wakefulness",
    "CH01_A10": "Cross-section of cortical gray matter where millions of vital memory synapses are being systematically uncoupled, illustrating irreversible structural neuronal attrition",

    # CH02: Hệ Thống Rửa Não Glymphatic Làm Việc Khi Nào? (11 beats)
    "CH02_A01": "Dynamic overview of the cerebral cortex during 16 active daytime hours, glowing with rapid glucose consumption and producing metabolic byproduct plumes like miniature exhaust trails",
    "CH02_A02": "Narrow interstitial clefts between brain cells progressively silting up with toxic fragments of misfolded beta-amyloid protein, forming sticky brown metabolic sludge",
    "CH02_A03": "Microscopic visualization of neurotoxic tau tangles and amyloid debris accumulating around neuron cell bodies, representing the pathological precursor to age-related cognitive decline",
    "CH02_A04": "Tight daytime interstitial spaces where glial cells and densely packed neurons leave virtually zero clearance for cerebrospinal fluid to penetrate and wash out waste",
    "CH02_A05": "Neural landscape transitioning into slow-wave deep sleep, where synchronized low-frequency electrical delta waves gently roll across the neocortex, opening the glymphatic gate",
    "CH02_A06": "Astrocytic endfeet actively shrinking by over sixty percent, transforming narrow microscopic crevices into wide, clear, pulsating anatomical channels",
    "CH02_A07": "Crystal-clear cerebrospinal fluid surging rhythmically through expanded perivascular tunnels driven by arterial pulsations, flushing deep brain tissues like an internal dishwasher",
    "CH02_A08": "Swirling torrents of biological cleansing fluid detaching sticky amyloid plaques and cellular detritus from living brain cells, sweeping debris into drainage conduits",
    "CH02_A09": "Meningeal lymphatic drainage vessels collecting dislodged waste proteins during the peak of the nocturnal cleansing shift while the body rests in deep slumber",
    "CH02_A10": "Sleep-deprived cerebral tissue where yesterday's uncleared metabolic sludge forms a dense suffocating barrier over delicate synaptic junctions",
    "CH02_A11": "A dense murky biochemical fog shrouding the prefrontal cortex, visualizing the severe cognitive haze and blocked mental processing after an all-nighter",

    # CH03: Khối Hạch Hạnh Nhân Bị Kích Hoạt Quá Mức (11 beats)
    "CH03_A01": "Morning view of an exhausted individual with pronounced dark periorbital circles, reacting with exaggerated autonomic stress to sudden urban traffic noises",
    "CH03_A02": "A person flinching and clenching their jaw at a mundane morning greeting, showing sudden emotional volatility rooted in neurochemical imbalance",
    "CH03_A03": "Deep coronal cutaway revealing the bilateral almond-shaped amygdala nuclei glowing with fiery orange electrical activity, acting as primitive alarm sentinels",
    "CH03_A04": "Long white matter axonal tract connecting the calm, well-rested prefrontal cortex to the amygdala, maintaining firm inhibitory governance over primitive emotional impulses",
    "CH03_A05": "Prefrontal regulatory signals acting like a steady hydraulic brake, dampening acute stress spikes and maintaining emotional equilibrium during daily frustrations",
    "CH03_A06": "Functional neuroimaging slice showing the sleep-starved prefrontal cortex going dark and hypometabolic, its inhibitory brake completely disengaged",
    "CH03_A07": "The uninhibited amygdala flaring with a dramatic sixty-percent surge in hyperactive electrical discharges, misinterpreting benign everyday sensory inputs as existential threats",
    "CH03_A08": "Sudden emotional instability manifested as tearful distress and volatile outbursts, followed by hollow exhaustion within the limbic circuitry",
    "CH03_A09": "The striatum and dopamine reward pathway hijacking executive control, driving impulsive reckless behavior and unchecked immediate gratification seeking",
    "CH03_A10": "An anatomical metaphor of a heavy transport truck careening down a steep mountain pass with severed brake lines, representing an uninhibited exhausted brain",
    "CH03_A11": "Hyperactive amygdala firing an urgent distress command directly to the hypothalamus, initiating a systemic biochemical emergency cascade throughout the body",

    # CH04: Tuyến Thượng Thận & Cơn Sốt Cortisol Kéo Dài (13 beats)
    "CH04_A01": "Sympathetic nervous trunk lighting up along the spinal column, instantly triggering the primitive fight-or-flight endocrine survival network",
    "CH04_A02": "Ancient human ancestors standing alert against nocturnal wilderness predators, illustrating how primal survival biology remains wired for acute night danger",
    "CH04_A03": "Close-up of the triangular adrenal glands perched atop the kidneys pumping a continuous surge of cortisol and adrenaline into the surrounding bloodstream",
    "CH04_A04": "Peripheral arterioles constricting under hormonal pressure while the myocardium contracts violently, driving arterial blood pressure upward",
    "CH04_A05": "Neuroendocrine axis showing the delicate homeostatic balance between circulating hunger hormones and satiety peptides in a well-rested state",
    "CH04_A06": "Plunging serum levels of leptin satiety molecules alongside an aggressive spike in circulating ghrelin, triggering uncontrollable primal hunger signals",
    "CH04_A07": "Systemic flood of stress cortisol impairing cell membrane insulin receptors across skeletal muscle and hepatic tissue beds",
    "CH04_A08": "Skeletal muscle cell membrane where glucose transporter channels fail to open, reducing cellular glucose uptake efficiency by forty percent",
    "CH04_A09": "Bloodstream cross-section showing elevated circulating glucose molecules resembling the glycemic profile of early-stage pre-diabetes after a sleepless night",
    "CH04_A10": "Glucose-starved brain detecting false cellular starvation and dispatching intense cravings for rapid simple carbohydrates and refined sugars",
    "CH04_A11": "A desk scene with sugary iced milk teas, glazed donuts, and refined pastries, visually reflecting desperate biological sugar cravings at three in the afternoon",
    "CH04_A12": "Abdominal cross-section illustrating rapid accumulation of dense visceral adipose tissue wrapping around internal organs, fueling metabolic syndrome",
    "CH04_A13": "Cellular view of mitochondria struggling within an energy-depleted biochemical furnace, emitting distress molecules under sustained hormonal strain",

    # CH05: Tế Bào Sát Thủ Tự Nhiên Sụt Giảm 70% (13 beats)
    "CH05_A01": "A fatigued individual shivering in a warm jacket during an exam period, catching a sudden seasonal cold after prolonged sleep restriction",
    "CH05_A02": "Microscopic overview of bone marrow capillaries where immune white blood cells interact closely with nocturnal circadian sleep rhythms",
    "CH05_A03": "Clinical laboratory view of a patient restricted to four hours of sleep, with automated hematology analyzers processing morning blood vials",
    "CH05_A04": "Dramatic visualization of circulating natural killer cell counts dropping by seventy percent across a translucent blood capillary cross-section",
    "CH05_A05": "High-resolution view of an active Natural Killer immune cell, bristling with molecular surface receptors that seek out diseased and mutant cells",
    "CH05_A06": "Natural Killer cell functioning like an elite rapid-response sentinel, patrolling endothelial vascular walls for infectious invaders and aberrant growths",
    "CH05_A07": "Natural killer cell scanning the surface of an epithelial cell infected with respiratory viral particles, identifying altered surface antigens",
    "CH05_A08": "Natural killer cell docking onto a target cell and discharging cytotoxic perforin and granzyme granules, neutralizing the pathogen-laden host cell",
    "CH05_A09": "Barely populated capillary lumen after sleep deprivation, where missing immune sentinels leave vascular walls unprotected against pathogens",
    "CH05_A10": "Hematopoietic stem cells inside dormant bone marrow failing to divide and mature without adequate nocturnal delta-wave recovery periods",
    "CH05_A11": "Airborne influenza and respiratory virus particles penetrating unprotected respiratory mucosal epithelial barriers with zero resistance",
    "CH05_A12": "Official epidemiological registry linking chronic nocturnal shift work and severe sleep deficits to Class 2A probable carcinogenic risk factors",
    "CH05_A13": "Vulnerable human physiology stripped of its immune shield, exposing how late nights silently dismantle long-term immunological resilience",

    # CH06: Cú Lật Ngược: Nợ Ngủ Không Thể Trả Bù Vào Cuối Tuần (14 beats)
    "CH06_A01": "A person sleeping late into a sunny Sunday afternoon, falsely hoping a weekend marathon will erase five days of severe sleep debt",
    "CH06_A02": "Conceptual calendar graphic contrasting five sleepless workdays with two oversleeping weekend days, highlighting the irreversible biological deficit",
    "CH06_A03": "Neocortex cutaway showing sudden localized neuron cluster shutdowns, where regional brain zones involuntarily power down for several seconds",
    "CH06_A04": "Detailed micro-circuit view of a focal cortical column falling silent into a micro-sleep state while surrounding areas barely sustain consciousness",
    "CH06_A05": "Subject experiencing a three-second micro-sleep episode with vacant unfocused eyes, completely unaware that conscious awareness has vanished",
    "CH06_A06": "Driver behind a steering wheel on a highway at night as micro-sleep hits, showing involuntary foot slip from the brake pedal",
    "CH06_A07": "Paralyzed neuromuscular pathways failing to trigger emergency avoidance reflexes in time, demonstrating the fatal danger of micro-sleeps",
    "CH06_A08": "Suprachiasmatic master clock thrown into chaos after irregular Sunday sleep hours, desynchronizing peripheral cellular timers across the body",
    "CH06_A09": "Sunday night ceiling staring followed by painful Monday morning grogginess, illustrating severe social jetlag and misaligned circadian rhythm",
    "CH06_A10": "Vascular endothelium under continuous nocturnal vasoconstriction, resulting in elevated resting arterial shear stress and reduced vessel elasticity",
    "CH06_A11": "Overworked cardiac muscle fibers contracting under chronic sympathetic tone, resulting in elevated nocturnal resting heart rate",
    "CH06_A12": "Longitudinal view of microvascular capillary beds suffering chronic low-grade inflammation and subtle structural vascular remodeling",
    "CH06_A13": "Deceptive late-night second wind fueled by an unnatural adrenaline surge, masking deepening physiological exhaustion",
    "CH06_A14": "A steady ticking circadian pendulum swinging smoothly day after day, representing consistent nightly sleep as the only true restorative cure",

    # CH07: Trận Chiến Giữa Ghrelin & Leptin: Bẫy Thèm Đường (14 beats)
    "CH07_A01": "Morning view of an empty breakfast table where an exhausted subject experiences gnawing gastric hunger pangs despite eating late last night",
    "CH07_A02": "Gastric mucosal lining actively secreting concentrated pulses of ghrelin hunger hormone into surrounding mesenteric blood vessels",
    "CH07_A03": "Subcutaneous adipose tissue cells suppressing the production and secretion of leptin, removing natural satiety feedback signals",
    "CH07_A04": "An empty plate surrounded by cravings for high-glycemic carbohydrates, illustrating insatiable primal hunger driven by hormonal imbalance",
    "CH07_A05": "Ventral tegmental area and nucleus accumbens lighting up intensely at images of fast food while executive control centers remain suppressed",
    "CH07_A06": "Sudden postprandial glucose spike surging through the bloodstream, prompting pancreatic beta cells to pump out massive waves of insulin",
    "CH07_A07": "Insulin resistance manifesting in skeletal muscle receptors, forcing excess circulating blood sugar into hepatic de novo lipogenesis",
    "CH07_A08": "Visceral adipose tissue expanding around the liver and mesentery, demonstrating how chronic sleep restriction fuels central obesity",
    "CH07_A09": "Continuous twenty-four-hour blood pressure recording showing the absence of normal nocturnal cardiovascular dipping during restless sleep",
    "CH07_A10": "Sustained nocturnal systolic pressure pounding against the aorta and coronary arteries without the normal restorative twenty-percent dip",
    "CH07_A11": "High arterial wall tension creating microscopic tears in the delicate endothelial lining of major coronary arteries",
    "CH07_A12": "Macrophages ingesting oxidized LDL particles at endothelial tear sites, forming early fibrous fatty streaks and narrowing arterial lumens",
    "CH07_A13": "Clinical cross-section of a narrowed coronary vessel illustrating how chronic short sleep doubles long-term risk of myocardial infarction",
    "CH07_A14": "Contrast between healthy elastic arterial walls and stiffened diseased vessels, urging preservation of cardiovascular health over late-night screens",

    # CH08: Đồng Hồ Sinh Học SCN & Ánh Sáng Xanh Điện Thoại (13 beats)
    "CH08_A01": "Anterior hypothalamus featuring the bilateral suprachiasmatic nucleus acting as the master conductor of 24-hour bodily biological rhythms",
    "CH08_A02": "Natural evening dusk wavelengths triggering retinal ganglion cells to signal the pineal gland to commence nocturnal melatonin secretion",
    "CH08_A03": "Gradual nocturnal drop in core body temperature, relaxation of skeletal muscle tone, and gentle onset of restorative sleepiness",
    "CH08_A04": "Bedroom scene where intense 460nm blue light from a handheld smartphone screen floods the pupil, striking melanopsin-containing retinal ganglion cells",
    "CH08_A05": "Melatonin secretion in the pineal gland abruptly extinguished by artificial blue photons, plunging the brain into artificial daytime alertness",
    "CH08_A06": "Sleep hypnogram diagramming alternating 90-minute ultradian cycles between Non-REM slow-wave sleep and Rapid Eye Movement dream phases",
    "CH08_A07": "Stage 3 Non-REM slow-wave sleep showing deep delta waves synchronizing across neocortex to repair cellular structures and replenish glycogen",
    "CH08_A08": "Rapid Eye Movement sleep stage with vivid theta waves replaying memories, filing long-term knowledge, and neutralizing emotional trauma",
    "CH08_A09": "Alarm clock buzzer abruptly shattering consciousness during the deepest trough of Stage 3 slow-wave sleep, causing abrupt sleep inertia",
    "CH08_A10": "Awakening with severe sleep inertia, marked by stiff joints, heaviness in the limbs, and a suffocating sense of mental disorientation",
    "CH08_A11": "Uncalibrated synaptic networks struggling to transmit baseline motor and executive signals during post-awakening grogginess",
    "CH08_A12": "Reliance on multiple energy drinks and caffeinated shots creating artificial adrenergic spikes that further disrupt next night's sleep onset",
    "CH08_A13": "Multi-organ diagram showing circadian desynchrony between heart, liver, and brain when the central circadian clock is chronically scrambled",

    # CH09: Quy Tắc 90 Phút & Giao Thức Tối Ưu Giấc Ngủ (12 beats)
    "CH09_A01": "A clinical sleep architecture blueprint outlining practical protocols to restore natural restorative sleep cycles and neuroendocrine harmony",
    "CH09_A02": "Clock graphic illustrating bedtime calculations in strict 90-minute blocks, targeting either five full cycles or four complete sleep cycles",
    "CH09_A03": "Comparison between six unbroken hours of four completed sleep cycles versus six and a half fragmented hours interrupted mid-cycle",
    "CH09_A04": "Evening bedroom ritual where digital screens are powered off and overhead lights are replaced by soft warm amber bedside lamps",
    "CH09_A05": "Warm dim illumination allowing natural pineal melatonin production to climb steadily, preparing the brain for gentle sleep transition",
    "CH09_A06": "Bedroom thermostat set to eighteen degrees Celsius, facilitating the natural nocturnal decline in core body temperature",
    "CH09_A07": "Fresh cool night air circulating through a slightly opened window, providing steady oxygen flow that promotes slower deeper respiration",
    "CH09_A08": "A warm evening bath causing peripheral capillary vasodilation in hands and feet, rapidly dumping core body heat to initiate sleepiness",
    "CH09_A09": "Afternoon clock displaying 2 PM as the definitive cutoff line for caffeine consumption, protecting nocturnal adenosine receptor availability",
    "CH09_A10": "Pharmacokinetic chart illustrating caffeine's eight-hour half-life, showing lingering molecules silently suppressing restorative slow-wave sleep",
    "CH09_A11": "Steaming cup of warm chamomile infusion on a wooden nightstand, replacing stimulants with natural relaxing botanical compounds",
    "CH09_A12": "Relaxed individual in bed listening to their steady rhythmic heartbeat, feeling restorative parasympathetic tone spread across every limb",

    # CH10: Thiết Lập Thói Quen Ngủ Phục Hồi Ngay Tối Nay (6 beats)
    "CH10_A01": "Conceptual artwork depicting healthy restorative sleep as the foundational biological pillar upholding physical vitality and cognitive clarity",
    "CH10_A02": "Human silhouette glowing with vibrant cellular energy and clear neurovascular circulation, emphasizing health as life's indispensable wealth",
    "CH10_A03": "Intricate 3D visualization of the human biological machine, showcasing tireless organ systems that deserve their nightly renewal shift",
    "CH10_A04": "A person intentionally placing their smartphone screen face down on a nightstand and switching off the bedside lamp into tranquil darkness",
    "CH10_A05": "Deep comfortable exhalation on a cool comfortable pillow, releasing all residual tension from facial, neck, and shoulder muscle groups",
    "CH10_A06": "Billions of regenerated neurons and immune cells glowing with renewed vitality, ready to awaken into a vibrant, clear-headed tomorrow",
}


# ==============================================================================
# 3. dia_com: 117 beats
# Style: Cinematic macro culinary food science photography
# ==============================================================================
DIA_COM_BEATS: Dict[str, str] = {
    # CH01: Mùi Thơm Đánh Thức Vị Giác & Bí Mật Màu Nâu (10 beats)
    "CH01_A01": "Warm inviting bistro interior on a chilly afternoon, focusing on a heavy black cast iron skillet where golden beads of rendered beef fat sizzle and pop vigorously",
    "CH01_A02": "Delicate curls of aromatic white vapor rising from a sizzling prime beef steak as its bright crimson surface rapidly transforms into a glossy mahogany crust",
    "CH01_A03": "Razor-sharp chef knife slicing through a thick seared steak on a dark butcher block, parting a crunchy exterior to reveal a glistening pink medium-rare center with rich juices pooling",
    "CH01_A04": "Two hands holding a freshly baked artisan Vietnamese baguette, its golden-blistered crust gently crackling under slight thumb pressure",
    "CH01_A05": "Warm morning sunlight illuminating toasted wheat flour dust and melting sweet butter on warm bread, alongside the bottom of a heavy pot showing crispy golden com chay rice crust",
    "CH01_A06": "Macro view of raw marbled beef before cooking, appearing pale and odorless, demonstrating that uncooked muscle tissue lacks complex savory aromas",
    "CH01_A07": "Pale lump of raw dough and a dull grayish piece of boiled meat in a simmering water bath, highlighting how boiling produces bland monochromatic food",
    "CH01_A08": "Steaming water bath devoid of roasted aroma, contrasted with the scorching dry iron surface of a hot skillet ready to trigger culinary transformation",
    "CH01_A09": "Microscopic thermal reaction at the meat-iron contact zone, where explosive heat unlocks hundreds of complex volatile flavor compounds within seconds",
    "CH01_A10": "Ancient glowing hearth embers illuminating early ancestral cooking, representing the foundational browning reactions that shaped human culinary evolution",

    # CH02: Phân Biệt Phản Ứng Maillard & Caramel Hóa (11 beats)
    "CH02_A01": "Warm home kitchen setup with two separate cooking vessels side by side, visually separating the two distinct browning pathways of culinary science",
    "CH02_A02": "Split culinary composition contrasting pure sugar syrup melting in a copper pot against a seasoned iron skillet searing protein-rich beef steak",
    "CH02_A03": "Heavy copper saucepan where pure white sucrose granules melt under 160 degrees Celsius, beginning to liquefy into clear syrup before turning pale gold",
    "CH02_A04": "Close-up of boiling sugar syrup bubbling gently as water evaporates, transforming into a deep viscous amber caramel with a delicate bittersweet edge",
    "CH02_A05": "Smooth glossy caramel drizzled onto marble, highlighting how pure thermal pyrolysis of sugar produces butterscotch aromas without savory meatiness",
    "CH02_A06": "Vintage 1912 French laboratory bench with amber glassware and brass burners, where chemist Louis-Camille Maillard conducted his pioneering experiments",
    "CH02_A07": "Warm glass test tube where dissolved amino acid solutions and simple reducing sugars react over a gentle flame, gradually darkening into rich golden amber",
    "CH02_A08": "Swirling golden liquid inside a laboratory flask releasing aromatic vapor plumes carrying the unmistakable fragrance of roasted meat and toasted bread",
    "CH02_A09": "Molecular visualization showing the essential collision between amine groups of amino acid protein chains and reactive carbonyl groups of reducing sugars",
    "CH02_A10": "Natural reducing sugars dispersed within grain starches and beef muscle fibers, awaiting thermal activation to begin their chemical cascade",
    "CH02_A11": "Dynamic molecular reassembly where amino acids and sugars dismantle their old bonds, reorganizing into complex cyclic flavor networks and deep brown pigments",

    # CH03: Ngưỡng Nhiệt Độ Vàng 140 Đến 165 Độ C (11 beats)
    "CH03_A01": "High-precision culinary infrared thermometer aiming its red dot at the center of a preheated cast iron pan, targeting the golden 140 to 165 degrees Celsius range",
    "CH03_A02": "Close-up of a skillet surface lingering below 140 degrees Celsius, where sluggish molecular movement leaves protein fibers unreactive and limp",
    "CH03_A03": "A pale steak placed into an insufficiently hot pan, its surface sweating cloudy juices and turning a dull unappetizing grey without crust formation",
    "CH03_A04": "Pot of vigorously boiling water at 100 degrees Celsius, showing how simmering heat fails to bridge the energy barrier required for browning reactions",
    "CH03_A05": "Searing skillet crossing the 140 degrees Celsius threshold, triggering an exponential acceleration of Maillard browning across the meat surface",
    "CH03_A06": "At 155 degrees Celsius, complex melanoidin polymers rapidly polymerizing into a crisp, deeply aromatic protective mahogany shell over the meat",
    "CH03_A07": "Excessive smoke billowing from an overheated pan surpassing 200 degrees Celsius, showing the critical boundary where flavor turns to scorched ruin",
    "CH03_A08": "Harsh destructive pyrolysis setting in above 200 degrees Celsius, where delicate aroma rings are shattered into bitter black acrid carbon crust",
    "CH03_A09": "Microscopic cross-section of charred food surface showing bitter heterocyclic amines and toxic polycyclic aromatic hydrocarbons replacing savory flavor",
    "CH03_A10": "A skilled chef attentively adjusting the gas burner flame, keeping the pan surface precisely balanced within the golden browning zone",
    "CH03_A11": "A thick steak gliding across the seasoned iron surface, perfectly maintaining the 150 degrees Celsius sweet spot for uniform mahogany crusting",

    # CH04: Kẻ Thù Số Một Của Vết Cháy Cạnh: Hơi Ẩm Bề Mặt (13 beats)
    "CH04_A01": "A premium cut of well-marbled beef steak placed onto a hot pan while still wet, causing unexpected steam to hiss and billow",
    "CH04_A02": "Sizzling snap dying out as pooling grey liquid surrounds the steak, turning a intended sear into an accidental soggy boil",
    "CH04_A03": "Thermodynamic heat diagram illustrating water's immense specific heat capacity, acting as an aggressive thermal heat sink on the pan surface",
    "CH04_A04": "Physical illustration of the latent heat of vaporization, showing the massive 2260 Joules required to vaporize a single gram of liquid water at boiling point",
    "CH04_A05": "Graphic comparison showing that boiling away one gram of surface water requires more than five times the energy needed to heat ice water to a boil",
    "CH04_A06": "Microscopic water film trapped between wet steak surface and hot iron, forming an insulating vapor barrier that caps pan temperature at 100 degrees Celsius",
    "CH04_A07": "The last stubborn droplets of surface water resisting evaporation, preventing the underlying meat proteins from reaching the 140 degrees threshold",
    "CH04_A08": "Meat fibers lifted slightly off the iron floor by trapped steam pockets, severing conductive direct contact heat transfer",
    "CH04_A09": "Unwanted internal heat conduction traveling inward while the exterior struggles to dry, prematurely cooking the interior fibers to grey well-done",
    "CH04_A10": "Cross-section of a poorly seared steak showing a thick overcooked grey band beneath a pale weak crust, having lost its precious pink center",
    "CH04_A11": "Wet fresh button mushrooms tossed hastily into hot oil, releasing a flood of watery liquid that extinguishes the frying sizzle",
    "CH04_A12": "Gas burner blazing at full blast beneath a crowded wet pan, yet helpless against the thermodynamic thermal buffer of unevaporated water",
    "CH04_A13": "Wooden cutting board with clean kitchen prep towels, demonstrating that moisture control must be executed completely before food touches heat",

    # CH05: Kỹ Thuật Làm Khô Bề Mặt & Muối Hút Ẩm (13 beats)
    "CH05_A01": "Professional kitchen prep counter where a chef uses thick absorbent paper towels to firmly dab every square inch of a thick ribeye steak",
    "CH05_A02": "Absorbent towel lifting microscopic water droplets from the meat surface, demonstrating the crucial first line of defense against surface steam",
    "CH05_A03": "Limitations of paper towel wiping, as deep internal moisture continues to migrate outward once muscle fibers contract under heat",
    "CH05_A04": "Chef's hand sprinkling coarse kosher salt crystals evenly across all surfaces of a thick raw steak, creating an even snowy mineral layer",
    "CH05_A05": "Uncovered salted steak resting on a stainless steel wire rack over a baking sheet, preparing for an uninhibited twelve-hour dry brine in the refrigerator",
    "CH05_A06": "First thirty minutes of dry brining, where salt crystals dissolve by drawing out tiny beads of surface moisture through osmotic pressure",
    "CH05_A07": "Concentrated liquid beads on the steak surface beginning to reabsorb, as the dissolved saline solution diffuses deeply into muscle fibers",
    "CH05_A08": "Salt ions penetrating deep into muscle fibrils, loosening actin and myosin protein bonds to create microscopic water-trapping pockets",
    "CH05_A09": "Relaxed protein matrix holding onto intracellular moisture tightly during cooking, preventing juices from squeezing out during high-heat searing",
    "CH05_A10": "Clean refrigerator interior where cold, dry circulating air acts as an effective dehumidification chamber around the exposed wire rack",
    "CH05_A11": "Steak after 24 hours of dry chilling, showcasing a firm, taut, dark mahogany pellicle completely free of surface water",
    "CH05_A12": "The completely dry pellicle making immediate direct physical contact with scorching hot cast iron with zero steam buffer",
    "CH05_A13": "Immediate explosion of Maillard reactions from the very first second of contact, forming a shatteringly crisp brown crust while locking in juices",

    # CH06: Cú Lật Ngược: Chảo Gang Không Phải Dẫn Nhiệt Tốt Nhất (14 beats)
    "CH06_A01": "A seasoned cast iron skillet gleaming under kitchen spotlight, ready to serve as the ultimate thermal tool for high-heat browning",
    "CH06_A02": "Infographic debunking the myth of cast iron thermal conductivity, comparing cast iron's relatively slow heat transmission to rapid copper and aluminum",
    "CH06_A03": "Thermal camera view of cast iron showing localized heat spots and uneven thermal dispersion when placed directly over an open flame",
    "CH06_A04": "Uneven sear on a thin pan showing burnt patches alongside pale raw spots, explaining why thermal mass matters more than conductivity",
    "CH06_A05": "A massive spinning cast iron flywheel rotating with tremendous momentum, metaphorically representing stored thermal energy that resists deceleration",
    "CH06_A06": "Lightweight thin aluminum skillet heating up rapidly in seconds, yet instantly losing surface temperature when cold food is introduced",
    "CH06_A07": "Temperature of a thin aluminum pan crashing below 100 degrees Celsius upon steak contact, silencing the sizzle into a limp steam bath",
    "CH06_A08": "Cold meat sweating juices into the cooled aluminum pan, stewing the exterior before any browning reaction can occur",
    "CH06_A09": "Dense, heavy cast iron pan acting as a deep thermal reservoir, holding thousands of stored calories within its thick iron walls",
    "CH06_A10": "Cold steak landing on thick cast iron with virtually zero temperature drop at the contact point, sustaining relentless conductive heat",
    "CH06_A11": "Flashed vapor disappearing instantly as the thick meat crust forms immediately, sealing in moisture and flavor without cooling the iron floor",
    "CH06_A12": "Skillet preheating gently over medium-low heat for ten minutes, allowing thermal saturation to fill the entire cast iron structure evenly",
    "CH06_A13": "A drop of water dancing in a spheroidal Leidenfrost state across the seasoned pan, signaling optimal thermal readiness",
    "CH06_A14": "Golden sear achieved effortlessly through patience and proper thermal saturation of the heavy iron skillet",

    # CH07: Hàng Trăm Hợp Chất Hương Thơm Mới Ra Đời (14 beats)
    "CH07_A01": "Bone-dry steak touching scorching seasoned iron, releasing an instantaneous orchestral sizzle and billowing aromatic vapor curls",
    "CH07_A02": "Millions of amino acid fragments and natural glucose molecules colliding at high speed within the sizzling millimeter-thin surface zone",
    "CH07_A03": "Molecular alchemy unfolding as simple raw building blocks fuse into over eight hundred distinct volatile aroma compounds",
    "CH07_A04": "Contrast between flat, odorless raw protein and the complex multidimensional bouquet generated by high-heat browning",
    "CH07_A05": "Alkylpyrazines forming within the crust, releasing roasted nutty popcorn-like notes into the surrounding air",
    "CH07_A06": "Oxygenated furan compounds generating sweet toasted caramel undertones that harmonize with rich rendered animal fats",
    "CH07_A07": "Sulfur-containing thiophenes and thiazoles creating the deep, savory, roasted meaty umami aroma that defines grilled dishes",
    "CH07_A08": "A gourmet diner bringing a forkful of seared steak to their lips, initiating the dual sensory perception of taste and olfaction",
    "CH07_A09": "Retronasal aromatic vapors traveling upward from the pharynx into the nasal cavity, stimulating millions of olfactory receptor neurons",
    "CH07_A10": "Sensory diagram showing retronasal olfaction contributing over eighty percent of what humans perceive as rich culinary flavor",
    "CH07_A11": "Blindfolded subject tasting seared steak with nose pinched, perceiving only flat salt and texture without rich roasted flavor notes",
    "CH07_A12": "Ancient hunter-gatherers gathered around a crackling wood fire, where the smell of roasted meat signaled safe nutritious sustenance",
    "CH07_A13": "Primal human limbic system and salivary glands immediately activating upon catching the first whiff of sizzling browned meat",
    "CH07_A14": "The humble sizzle at the bottom of a modern skillet bridging prehistoric instinct with modern culinary gastronomy",

    # CH08: Ứng Dụng Trong Cơm Cháy, Cà Phê & Bánh Mì (13 beats)
    "CH08_A01": "A traditional Asian kitchen wok revealing that Maillard browning is universal across global culinary traditions, not just Western steaks",
    "CH08_A02": "Crushed garlic cloves and sliced shallots hitting smoking peanut oil in a wok, crackling and turning translucent gold in seconds",
    "CH08_A03": "Clay pot of Vietnamese caramelized braised pork ribs, where bubbling sauce reduces into a rich mahogany glaze coating tender meat",
    "CH08_A04": "Traditional earthen pot containing caramelized catfish, with caramelized shallots and fish sauce developing rich savory depth",
    "CH08_A05": "Golden crispy rice crust com chay forming at the bottom of a heavy cast iron rice pot, crackling with savory toasted starch aromas",
    "CH08_A06": "Coffee roaster drum tumbling green coffee beans under intense convective heat, expanding beans as Maillard browning turns them chocolate brown",
    "CH08_A07": "Roasted coffee beans cracking during the first crack, releasing essential oils and hundreds of aromatic volatile compounds",
    "CH08_A08": "Artisan bakery deck oven where French baguettes bake, developing deeply browned blistered crusts while interior crumb stays moist at 100 degrees",
    "CH08_A09": "Chef reducing burner flame to medium-low after initial searing, allowing gentle heat to finish cooking the interior without burning the crust",
    "CH08_A10": "Perfectly cooked cutlet showing tender succulent meat throughout, framed by a delicate, evenly golden crunchy crust",
    "CH08_A11": "Simple home cookware on a gas burner, illustrating that culinary excellence requires temperature awareness rather than expensive gadgets",
    "CH08_A12": "Audio-visual transition as erratic watery spattering smooths out into a gentle, rhythmic, steady culinary sizzle",
    "CH08_A13": "A modest home dinner table glowing with beautifully browned family dishes, turning everyday cooking into a celebration of flavor science",

    # CH09: Ba Sai Lầm Khiến Món Ăn Bị Dai Khô Hoặc Khét (12 beats)
    "CH09_A01": "High-contrast culinary photo comparing a gorgeously golden-brown cutlet with a blackened, bitter scorched steak, warning of heat pitfalls",
    "CH09_A02": "Overcrowded skillet packed tightly with multiple cold steaks, causing immediate pan cooling and pooling grey cooking liquid",
    "CH09_A03": "Grey soggy meat boiling in its own extracted juices, showing the disastrous result of thermal overload from pan crowding",
    "CH09_A04": "Impatient tongs tearing raw meat from the pan surface prematurely, leaving shreds of meat stuck to the iron grate",
    "CH09_A05": "A chef waiting patiently until the Maillard crust naturally releases from the skillet bottom, allowing effortless turning without sticking",
    "CH09_A06": "Scorched skillet where pan surface exceeded 200 degrees Celsius, turning sweet aromatic compounds into bitter black carbonized char",
    "CH09_A07": "Chef gently scraping away minor charred edges with the back of a knife, preserving the golden mahogany zone beneath",
    "CH09_A08": "Platter of grilled meats served alongside a vibrant garden salad of crisp mint, cilantro, cucumber, and fresh leafy greens",
    "CH09_A09": "Fresh plant antioxidants and polyphenols neutralizing dietary free radicals and lipid peroxidation products in the digestive tract",
    "CH09_A10": "Acidic citrus marinade and fresh lime juice dressing tenderizing muscle fibers while reducing heterocyclic amine formation by half",
    "CH09_A11": "Traditional Vietnamese herb basket with perilla and coriander, perfectly balancing savory rich meats with digestive freshness",
    "CH09_A12": "Balanced dinner table celebrating crisp fresh greens as a natural protective shield for cardiovascular and digestive vitality",

    # CH10: Trở Thành Bậc Thầy Nhiệt Độ Trong Căn Bếp (6 beats)
    "CH10_A01": "Culinary workstation showing well-prepped ingredients, clean cutting boards, and steady burners, celebrating cooking as applied food science",
    "CH10_A02": "Coarse salt crystals drawing moisture and a heavy cast iron skillet glowing with steady stored heat, setting the stage for success",
    "CH10_A03": "Clean release of a golden seared fish fillet gliding effortlessly across the skillet, dispelling all fear of food sticking",
    "CH10_A04": "Everyday kitchen ingredients transforming into restaurant-quality delicacies through the conscious application of thermal principles",
    "CH10_A05": "Chef carefully patting ingredients dry and waiting for the pan to reach the smoking threshold before gently laying down the protein",
    "CH10_A06": "Warm, inviting dining table surrounded by happy family members enjoying flavorful, perfectly browned homemade dishes",
}


def run_worker2_rebuild() -> Dict[str, Any]:
    channels = [
        ("chanh_niem_ke", CHANH_NIEM_KE_BEATS, 70),
        ("co_the_ke", CO_THE_KE_BEATS, 117),
        ("dia_com", DIA_COM_BEATS, 117),
    ]

    results = {}
    for slug, scenes, expected_count in channels:
        print(f"\n==========================================")
        print(f"Compiling and validating: {slug} (expecting {expected_count} beats)")
        print(f"==========================================")

        assert len(scenes) == expected_count, (
            f"Beat count mismatch for {slug}: got {len(scenes)}, expected {expected_count}"
        )

        # Check unique scene descriptions
        unique_scenes = set(scenes.values())
        assert len(unique_scenes) == len(scenes), (
            f"Duplicate scene descriptions found in {slug}: {len(scenes) - len(unique_scenes)} duplicates"
        )

        # Check ASCII only
        for bid, desc in scenes.items():
            non_ascii = [c for c in desc if ord(c) >= 128]
            assert not non_ascii, f"Non-ASCII chars in {slug} {bid}: {non_ascii}"

        report = compile_and_save_spec(slug, scenes)
        results[slug] = report

        print(f"Report for {slug}:")
        print(f"  Beat count: {report['beat_count']}")
        print(f"  Unique prompts: {report['unique_prompts']}")
        print(f"  100% Unique: {report['is_100_unique']}")
        print(f"  Total Duration: {report['total_duration']}s (TTS: {report['tts_duration']}s, diff: {report['duration_diff']}s)")
        print(f"  Non-ASCII count: {report['non_ascii_count']}")
        print(f"  IS VALID: {report['is_valid']}")

        if not report["is_valid"]:
            raise RuntimeError(f"Spec compilation validation failed for {slug}: {report}")

    return results


if __name__ == "__main__":
    run_worker2_rebuild()
