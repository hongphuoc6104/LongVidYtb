#!/usr/bin/env python3
"""Worker 3 Channel Spec Rebuilder for Batch 1.

Compiles 100% story-aligned Long (16:9) specs for:
1. la_ban_hoc_thuat (98 beats)
2. loi_sang_soi (98 beats)
3. luat_doi_thuong (117 beats)

Invariants strictly enforced:
- 0% generic boilerplate
- 0% Vietnamese diacritics in English prompts
- 0% 8k / 4k / photorealistic buzzwords
- 0% text overlays
- 100% unique scene descriptions across all beats
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from sys.tools.batch1_spec_builder import BUZZWORDS_REGEX, compile_and_save_spec
from typing import Any, Dict

# ==============================================================================
# 1. LA_BAN_HOC_THUAT (98 beats)
# Style: Veritasium / 3Blue1Brown
# ==============================================================================
LA_BAN_HOC_THUAT_SCENES: Dict[str, str] = {
    # Chapter 1: The Paradox of Reading & Forgetting (8 beats)
    "CH01_A01": "Student sitting at an organized wooden study desk closing a thick dense textbook with a sigh, realizing that despite finishing the volume the mind feels completely blank",
    "CH01_A02": "Student hand vigorously sliding a bright yellow fluorescent highlighter pen across printed paragraphs, covering entire pages in translucent luminous yellow ink",
    "CH01_A03": "Student looking puzzled and hesitant across a wooden seminar table as a colleague asks for the central thesis of the book, unable to articulate a single clear premise",
    "CH01_A04": "Cognitive diagram of human eyes smoothly scanning across printed sentences while the deeper cerebral neural circuitry remains idle without cognitive synthesis",
    "CH01_A05": "Visual contrast between the fragile illusion of superficial reading familiarity and the sudden collapse when attempting independent verbal articulation without notes",
    "CH01_A06": "Digital tablet screen displaying dozens of opened browser tabs and articles alongside a student experiencing complete cognitive information overload",
    "CH01_A07": "Split conceptual visual showing mere visual recognition of printed concepts on the left versus deep neural internalization on the right",
    "CH01_A08": "Analytical visualization of cognitive memory decay vectors pointing downward, introducing the universal natural mechanism of biological forgetting",

    # Chapter 2: The Ebbinghaus Forgetting Curve (9 beats)
    "CH02_A01": "Historic 1885 German laboratory interior where psychologist Hermann Ebbinghaus conducts meticulous memory experiments with handwritten syllable cards under oil lamp illumination",
    "CH02_A02": "Mathematical graph plotting the steep downward trajectory of the Ebbinghaus forgetting curve with a glowing curve plunging immediately after initial study",
    "CH02_A03": "Timeline counter indicating twenty minutes elapsed since learning, showing forty percent of acquired information evaporating like light mist from cognitive storage",
    "CH02_A04": "Clock marking twenty-four hours after study, with over seventy percent of the learned memory trace disintegrated into scattered faint conceptual fragments",
    "CH02_A05": "Memory retention graph hitting the bottom baseline thirty days later, showing almost total erasure of unreviewed data without scheduled recall intervention",
    "CH02_A06": "Evolutionary conceptual visual of prehistoric human ancestors needing efficient neural pruning to clear trivial survival noise and conserve cognitive energy",
    "CH02_A07": "Diagram of the human brain acting as an efficient biological filter, systematically discarding unreinforced sensory inputs to preserve metabolic energy",
    "CH02_A08": "High-priority neural transmission pulse illuminating a specific synaptic pathway to signal critical importance to long-term memory circuits",
    "CH02_A09": "Comparison between passive repetitive rereading leaving synapses untouched versus intense retrieval effort forcing neural networks to fire energetically",

    # Chapter 3: Active Recall (10 beats)
    "CH03_A01": "Cognitive science laboratory visualization highlighting the robust neural architecture strengthened through repeated active retrieval practices",
    "CH03_A02": "Decisive motion of a student firmly closing a thick textbook and grabbing a pen to explain the fundamental principles aloud into an empty quiet study room",
    "CH03_A03": "Student furrowing brow in intense cognitive strain while staring away from reference materials, feeling mental effort as memories are actively dredged up",
    "CH03_A04": "Microscopic visualization of dendritic spines and synaptic junctions thickening and solidifying during strenuous memory retrieval episodes",
    "CH03_A05": "Controlled laboratory experiment comparing two student cohorts, highlighting the group practicing self-testing achieving fivefold superior exam retention",
    "CH03_A06": "Conceptual scale demonstrating the law of desirable difficulty, where high cognitive retrieval effort correlates directly with permanent memory durability",
    "CH03_A07": "Crisp blank white sheet of paper on a clean oak desk, where a hand begins sketching a conceptual mind map purely from unassisted mental recall",
    "CH03_A08": "Visual audit comparing the unassisted sketch with the original textbook, identifying hidden knowledge gaps without judgment",
    "CH03_A09": "Dedicated student habit of transforming every study session into an unassisted retrieval quiz rather than passive page-turning",
    "CH03_A10": "Visualization of freshly learned concept nodes deeply anchoring and intertwining into the preexisting lattice of long-term memory networks",

    # Chapter 4: The Pitfall of Highlighters & Passive Summaries (11 beats)
    "CH04_A01": "High-angle view of a desk littered with multicolored fluorescent marker caps, highlighting the false sense of industrious productivity created by passive text marking",
    "CH04_A02": "Student looking at a page glowing with yellow and neon green stripes, experiencing visual stimulation without real semantic comprehension",
    "CH04_A03": "Notebook page filled with verbatim copied sentences from an author, illustrating mechanical muscle repetition devoid of conceptual synthesis",
    "CH04_A04": "Educational research bar chart demonstrating that passive highlighting and verbatim copying rank lowest among all study techniques for retention",
    "CH04_A05": "Shocked student freezing in an examination hall staring at a test question, realizing the colorful pages memorized visually offered zero functional comprehension",
    "CH04_A06": "Hand writing concise synthesis notes in original personal phrasing on an index card, distilling complex academic jargon into pure clarity",
    "CH04_A07": "Structured notebook where notes are formatted strictly as challenging self-inquiry questions on the left margin rather than factual answers",
    "CH04_A08": "Deep cognitive processing model showing how semantic restructuring and analytical manipulation cement memories permanently",
    "CH04_A09": "Student deliberately placing fluorescent highlighters into a drawer, choosing the demanding path of active conceptual reconstruction",
    "CH04_A10": "Conceptual balance showing how effortless study methods yield negligible retention while challenging friction creates enduring mastery",
    "CH04_A11": "Methodical study calendar mapped out with scientifically calculated intervals designed to intercept forgetting curves before memory decay sets in",

    # Chapter 5: Spaced Repetition (11 beats)
    "CH05_A01": "Dynamic visualization of the spaced repetition curve, where timely review interventions flatten the steep drop-off into a stable high-retention plateau",
    "CH05_A02": "Exhausted student surrounded by crumpled coffee cups cramming ten hours straight through the night, creating a brittle temporary memory veneer",
    "CH05_A03": "Geometric calendar timeline showing review intervals systematically expanding from one day to three days, one week, and one month",
    "CH05_A04": "The critical golden threshold of memory retrieval, pinpointing the precise moment a concept is on the verge of fading before an alert triggers recall",
    "CH05_A05": "Long-term memory storage vault sealing critical knowledge blocks as repeated retrieval cycles signal vital evolutionary importance",
    "CH05_A06": "Physical Leitner flashcard box with partitioned compartments, showing cards advancing to wider intervals upon correct recall or returning to daily review on error",
    "CH05_A07": "Focused student completing a rapid fifteen-minute spaced review session, achieving greater retention in minutes than hours of rote repetition",
    "CH05_A08": "Relaxed and composed student walking into a major academic exam hall with deep-seated instinctive mastery and zero pre-test panic",
    "CH05_A09": "Clockwork metronome ticking steadily on a minimalist desk, symbolizing rhythmic disciplined repetition outperforming sporadic manic cramming",
    "CH05_A10": "Metaphorical visualization of compound interest, where daily micro-investments in spaced recall snowball into vast intellectual capital",
    "CH05_A11": "Transition visual from personal memory consolidation to interpersonal communication, introducing the ultimate test of explaining ideas to others",

    # Chapter 6: The Feynman Technique (11 beats)
    "CH06_A01": "Renowned physicist Richard Feynman standing by a simple chalkboard, explaining quantum principles using intuitive visual metaphors to an attentive young child",
    "CH06_A02": "Academic workspace free of biological memory dependence, relying instead on an interconnected modular external thinking apparatus",
    "CH06_A03": "Individual crisp paper slip being written with exactly one self-contained atomic concept, stripped of extraneous academic ornament",
    "CH06_A04": "Traditional rigid file folders shown locking ideas into inflexible silos, preventing organic cross-disciplinary discovery",
    "CH06_A05": "Non-hierarchical web of human memory associations, demonstrating how ideas naturally connect through fluid associative synapses rather than rigid trees",
    "CH06_A06": "Unique alphanumeric index code assigned to an index card, allowing new conceptual branches to insert organically between existing notes",
    "CH06_A07": "Growing physical slip-box archive where cross-referencing link numbers form a living, responsive external neural network of thoughts",
    "CH06_A08": "Spark of intellectual insight illuminating when a biological principle links across notes to an unrelated sociological phenomenon",
    "CH06_A09": "Scholar engaging in animated dialogic inquiry with his wooden slip-box card cabinet, treating the archive as an intellectual conversational partner",
    "CH06_A10": "Proliferating web of interconnected ideas spontaneously generating unanticipated research questions and novel manuscript outlines",
    "CH06_A11": "Holistic ecosystem of self-directed scholarship where knowledge builds compounded systemic depth across years of deliberate practice",

    # Chapter 7: The Hoarding Illusion vs Active Application (11 beats)
    "CH07_A01": "Academic accumulator proudly gazing at overflowing bookshelves and massive digital drive folders filled with unread academic PDFs",
    "CH07_A02": "Dark storage warehouse filled with dusty unopened crates, representing hoarded information that never translates into functional competence",
    "CH07_A03": "Fleeting cognitive traces dissolving harmlessly during sleep after an individual merely skims through hundreds of digital pages without synthesis",
    "CH07_A04": "Real-world engineering workbench where theoretical formulas are immediately applied to solve an authentic mechanical mechanism problem",
    "CH07_A05": "Clear tangible project output such as a published essay or strategic briefing document emerging from a disciplined learning sprint",
    "CH07_A06": "Student writing an analytical critique of a dense paper, dismantling claims and testing premises rather than accepting authority passively",
    "CH07_A07": "Flowchart showing the transformation of raw information intake into structured synthesis, mental modeling, and real-world execution",
    "CH07_A08": "Hands-on laboratory environment where theoretical models are pressure-tested against real empirical variables to verify robustness",
    "CH07_A09": "Academic artisan carving out a refined original thesis by discarding decorative fluff and honing core functional insights",
    "CH07_A10": "Contrast between passive consumption consuming energy versus active creation generating intellectual stamina and confidence",
    "CH07_A11": "Transition to the modern learning environment, focusing on digital architecture and cognitive environment management",

    # Chapter 8: Attention Architecture & Deep Focus (11 beats)
    "CH08_A01": "Minimalist study sanctum illuminated by natural morning sunlight, completely devoid of digital clutter, screens, or extraneous distractions",
    "CH08_A02": "Intense cognitive laser beam focusing squarely on a single academic manuscript, demonstrating uninterrupted immersion",
    "CH08_A03": "High cognitive cost of a micro-distraction, showing how a single glance at a buzzing phone shatters deep intellectual immersion",
    "CH08_A04": "Attention residue visual showing cognitive threads lagging behind on an interrupted text message while the eyes try to read",
    "CH08_A05": "Twenty-minute recovery curve showing the prolonged, sluggish uphill climb required for the brain to regain peak concentration after a brief alert",
    "CH08_A06": "Deliberate environmental redesign where friction is introduced against distractions, locking smartphones and entertainment away",
    "CH08_A07": "Clean minimalist workspace featuring only one open notebook, one fountain pen, and the primary research volume under a soft warm lamp",
    "CH08_A08": "Smartphone resting powered down inside a closed wooden drawer in an adjacent room, establishing total acoustic and visual isolation",
    "CH08_A09": "Classic analog Pomodoro timer ticking rhythmically on a wooden desk, structuring cognitive effort into intense bounded intervals",
    "CH08_A10": "Twenty-five-minute deep work sprint where a researcher works with undivided devotion on a single complex analytical derivation",
    "CH08_A11": "Five-minute restorative pause showing a student walking away from the desk to drink fresh water, allowing default mode network consolidation",

    # Chapter 9: Digital Second Brain & AI Synthesis (10 beats)
    "CH09_A01": "Modern digital knowledge ecosystem integrating note-taking software and algorithmic tools to augment human cognitive bandwidth",
    "CH09_A02": "Metaphorical human brain illuminated with creative sparks, liberated from raw data storage by delegating rote archiving to digital databases",
    "CH09_A03": "Spaced repetition software algorithm surfacing a specific digital flashcard at the exact calculated threshold of forgetting",
    "CH09_A04": "Precision learning dashboard highlighting targeted knowledge blind spots, eliminating wasteful review of already mastered concepts",
    "CH09_A05": "Obsidian dynamic graph view rendering thousands of interconnected Markdown notes as an expanding multidimensional constellation of thoughts",
    "CH09_A06": "Intersection of two disparate concept clusters in a knowledge graph, igniting a glowing nexus of creative synthesis",
    "CH09_A07": "Intelligent digital interface acting as an indefatigable Socratic debate partner, posing rigorous counterarguments to a student thesis",
    "CH09_A08": "Socratic dialogue prompt on a screen challenging the student to identify logical fallacies in their freshly constructed argument",
    "CH09_A09": "Diagnostic map pinpointing unexamined assumptions and reasoning flaws within an academic draft",
    "CH09_A10": "Real-time feedback loop between human researcher and cognitive tools, refining conceptual clarity at unprecedented speed",

    # Chapter 10: Lifelong Cognitive Liberation (6 beats)
    "CH10_A01": "Vision of self-directed learning as an empowering noble privilege that unlocks intellectual sovereignty across an entire lifetime",
    "CH10_A02": "Fast-moving digital stream of twenty-first century information, showing obsolete static facts falling away while adaptive learning skills endure",
    "CH10_A03": "Lifelong learner standing agile and confident, equipped with first-principles learning frameworks to master any new discipline from scratch",
    "CH10_A04": "Fresh dawn breaking over a tranquil home library, inviting an immediate reset of one intellectual habits and cognitive architecture",
    "CH10_A05": "Student turning to an adjacent listener to distill a profoundly complex theory into simple, crystalline, everyday language",
    "CH10_A06": "Expanding geometric sphere of intellectual understanding illuminating boundless horizons of human curiosity and sovereign mastery",
}


# ==============================================================================
# 2. LOI_SANG_SOI (98 beats)
# Style: BibleProject / Caravaggio Chiaroscuro
# ==============================================================================
LOI_SANG_SOI_SCENES: Dict[str, str] = {
    # Chapter 1: The Sower & The Four Soils (8 beats)
    "CH01_A01": "Ancient solitary agrarian sower walking across a vast open field at late golden hour, wearing a coarse linen tunic and carrying a heavy weathered burlap seed sack over his shoulder under dramatic raking light",
    "CH01_A02": "Weathered calloused hand sweeping broadly across the open air, scattering thousands of radiant golden grain seeds caught in a brilliant beam of heavenly sunlight",
    "CH01_A03": "Hard cracked footpath where scattered wheat seeds lie exposed on compacted chalky dirt as a flock of black birds sweeps down in a flurry of dark wings",
    "CH01_A04": "Shallow scorched limestone outcrop where fragile green sprouts emerge prematurely, withering under a blistering sun without subterranean moisture",
    "CH01_A05": "Tangled cluster of menacing wild thorn bushes with sharp wooden spines wrapping aggressively around fragile young green seedlings in deep shadowy undergrowth",
    "CH01_A06": "Soft loamy dark alluvial soil warmly illuminated by a golden sunbeam, gently cradling fallen wheat grains in moist fertile furrowed earth",
    "CH01_A07": "Vast glowing golden wheat field rippling under gentle afternoon breeze, laden with heavy ripe ears multiplying thirty, sixty, and a hundredfold harvest",
    "CH01_A08": "Introspective composition framing the ancient sower gazing toward the viewer, holding an earthenware seed bowl while dramatic chiaroscuro shadows split the four terrains",

    # Chapter 2: The Hardened Pathway (9 beats)
    "CH02_A01": "Sun-baked ancient dirt road compacted to stone-like hardness by countless passing footsteps over generations, dry dust swirling across the impenetrable surface",
    "CH02_A02": "Weathered elder with closed posture and guarded expression turned away from the light, symbolic of a hardened cynical mind deaf to sincere wisdom",
    "CH02_A03": "Golden seed of truth resting completely stranded on the hard glazed dirt, unable to penetrate the impenetrable surface crust",
    "CH02_A04": "Solitary wheat grain lying desolate on the windswept road as evening shadows lengthen, devoid of morning dew or sheltering earth",
    "CH02_A05": "Flock of ominous ravens swooping abruptly down from gloomy storm clouds, their sharp beaks snatching away the exposed seed in a flash of dark feathers",
    "CH02_A06": "Allegorical visual of an individual surrounded by the flickering cold blue glare of electronic screens, distracted from quiet contemplative truth",
    "CH02_A07": "Whirling vortex of sensationalist tabloid headlines and trivial digital noise pulling human attention away into chaotic shallow turbulence",
    "CH02_A08": "Noisy clamoring crowd shouting in blurred shadows while a contemplative individual sits with hands covering ears, overwhelmed by vacuous chatter",
    "CH02_A09": "The barren empty highway returning to desolate silence beneath fading twilight, the discarded seed vanishing without ever taking root",

    # Chapter 3: The Rocky Ground (10 beats)
    "CH03_A01": "Rugged hillside of jagged white limestone covered only by a paper-thin layer of pale dry dust, masking the impenetrable bedrock beneath",
    "CH03_A02": "Young rustic youth with wide glowing eyes and impetuous excitement, grasping a new idea with impulsive passionate fervor",
    "CH03_A03": "Tender bright green wheat sprout shooting up with astonishing rapidity, waving proudly above the stony surface within days of sowing",
    "CH03_A04": "Youth gesturing boldly with passionate promises under morning sun, overflowing with premature self-assurance before facing real adversity",
    "CH03_A05": "Subterranean cross-section beneath the stony crust showing delicate white root tips abruptly hitting cold unyielding solid bedrock without finding any deep moisture",
    "CH03_A06": "Blazing midday sun beating down mercilessly from a cloudless sky, baking the shallow rock slab into a searing furnace that parches the tender seedling",
    "CH03_A07": "Arduous unglamorous reality of long-term discipline contrasting with fleeting emotional euphoria, symbolized by a heavy wooden yoke on stone",
    "CH03_A08": "Despondent youth staring down with crushed expectations as initial enthusiasm evaporates into disillusionment when difficulties mount",
    "CH03_A09": "Shriveled yellowed wheat stalk crumbling into brittle chaff on the sun-bleached rocks beneath passing boots",
    "CH03_A10": "Solemn chiaroscuro study of a withered plant stem lacking deep root anchors, reminding that shallow emotion collapses in the heat of testing",

    # Chapter 4: The Thorny Thicket (11 beats)
    "CH04_A01": "Seemingly rich agrarian plot where a sturdy young wheat stalk rises vigorously into the morning air with healthy green foliage",
    "CH04_A02": "Dark sinister tendrils of wild brambles creeping stealthily across the ground, sending prickly runners toward the flourishing green crop",
    "CH04_A03": "Dense thicket of barbed briars and interlocking thorns twisting tightly around the green stalk like barbed wire, suffocating its growth",
    "CH04_A04": "Anxious merchant hunched over wooden ledger tables late at night, tormented by mounting debts and relentless fear of scarcity",
    "CH04_A05": "Seductive allure of vanity and glittering gold coins casting deceptive reflections across a shadowy room, driving endless insatiable pursuit",
    "CH04_A06": "Towering wall of dense tangled brambles blocking out the warm golden rays of heaven, plunging the choking crop into suffocating twilight",
    "CH04_A07": "Aggressive creeping thorn roots invading subterranean soil, greedily drinking every drop of groundwater and starving the choked grain plant",
    "CH04_A08": "Gifted and virtuous individual sitting in deep weariness, paralyzed by conflicting worldly obligations and competing demands",
    "CH04_A09": "Mind fractured across hundreds of petty calculations, administrative stresses, and frantic status races that exhaust spiritual energy",
    "CH04_A10": "Person trapped in a relentless exhausting hamster wheel of material competition, accumulating possessions while spiritual vitality slowly atrophies",
    "CH04_A11": "Lush green leafy stalk that remains tragically sterile, bearing no grain kernels beneath its overgrown canopy of thorns, a silent heart-wrenching waste",

    # Chapter 5: The Fertile Ground & Abundant Harvest (11 beats)
    "CH05_A01": "Dawn light bathing a deeply tilled field of dark chocolate-brown alluvial soil, pulverized soft and crumbly, cleared of every rock and weed",
    "CH05_A02": "Gentle spring rain shower softly watering deep plowed furrows, preparing an open hospitable seedbed welcoming life without barrier",
    "CH05_A03": "Golden wheat grain nestled warmly within moist loamy earth, symbolizing an attentive soul receiving truth with genuine humility",
    "CH05_A04": "Humble seeker meditating by candlelight with an open receptive heart, holding onto virtuous truth like an inner sanctuary lamp through life storms",
    "CH05_A05": "Vibrant green shoot bursting through rich humus, its powerful taproot plunging deep into cool subterranean spring waters, standing firm against wind",
    "CH05_A06": "Majestic spreading wheat canopy offering shade and shelter, where small woodland songbirds gather joyfully in the peaceful leafy foliage",
    "CH05_A07": "Heavy clusters of ripe golden ears bending gracefully under their own weight, glowing resplendently in the radiant afternoon sunbeam",
    "CH05_A08": "Joyful harvest celebration with rustic ceramic earthenware jugs and woven wicker baskets overflowing with freshly threshed golden wheat",
    "CH05_A09": "Single humble seed transformed through patient cultivation into an astonishing bountiful yield of thirty, sixty, and a hundredfold",
    "CH05_A10": "Generous farmer extending broad weathered arms to share baskets of fresh golden bread with hungry travelers and impoverished neighbors",
    "CH05_A11": "Sublime composition capturing the crowning fruition of silent steadfast dedication, an enduring life of selfless meaning and grace",

    # Chapter 6: The Impartial Generosity of the Sower (11 beats)
    "CH06_A01": "Caravaggio-style low-angle view of the sower strong outstretched arm frozen in mid-release, casting golden seeds fearlessly across all horizons",
    "CH06_A02": "Shower of luminous amber seeds suspended mid-flight against deep velvety black shadows, floating down impartially upon every path",
    "CH06_A03": "Sower scattering grain without hesitation onto stony gravel and thorn patches alike, defying conventional human calculations of merit",
    "CH06_A04": "Majestic manifestation of divine grace and unconditional opportunity, offering the sacred gift of life equally to all created souls",
    "CH06_A05": "Golden morning sunbeam stretching evenly across both the pristine plowed furrows and the neglected trampled paths",
    "CH06_A06": "Refreshing rain clouds releasing soft drizzle upon the entirety of the vast countryside, nourishing the desolate wasteland and fertile field alike",
    "CH06_A07": "Visual contrast between the seed uniform divine vitality and the radically diverging fates determined by the recipient soil internal readiness",
    "CH06_A08": "Pilgrim seated by an arid wayside reflecting with hand over chest, realizing external circumstances are not to blame for inner stagnation",
    "CH06_A09": "Sleeping seed resting patiently inside dry earth, harboring immense dormant potential awaiting the awakening touch of moisture",
    "CH06_A10": "Closed fist clutched tightly in suspicion versus an open upturned palm welcoming the seed of grace with trust and openness",
    "CH06_A11": "Contemplative cross-section through the human soul, revealing the four soil strata coexisting within the landscape of the human heart",

    # Chapter 7: Deconstructing Modern Internal Soils (11 beats)
    "CH07_A01": "Antique wooden mirror reflecting an allegorical human heart divided into four distinct agrarian textures: stone, dust, briar, and loam",
    "CH07_A02": "Stone fortress wall erected around a bruised wounded psyche, shutting out authentic connection and gentle counsel in bitter self-defense",
    "CH07_A03": "Black ravens carrying off tender green shoots from a distracted mind, leaving behind an echoing barren void in the soul",
    "CH07_A04": "Seductive thin layer of emerald moss clinging to cold bare granite, an illusory promise of depth masking internal spiritual emptiness",
    "CH07_A05": "Flaming torch igniting dry straw that flares brightly for a brief instant before collapsing into cold gray ash without embers",
    "CH07_A06": "Somber twilight descending over a desolate hillside where broken dry stalks rattle in the cold wind, reflecting the cost of superficiality",
    "CH07_A07": "Hidden underground network of choking thorn roots silently draining moisture away from a struggling sapling, unseen from the surface",
    "CH07_A08": "Weary professional trapped in an opulent golden cage, surrounded by luxury yet starved of genuine purpose and inner stillness",
    "CH07_A09": "Beautiful flowering tree whose blossoms fall barren without setting fruit, strangled by subterranean anxiety and social comparison",
    "CH07_A10": "Soft fragrant dark loam turned up by an iron plowshare, releasing earthy vapor as it receives the falling rain in tranquil reverence",
    "CH07_A11": "Gentle light bathing the serene face of an elder whose life has become a deeply rooted sanctuary of compassionate wisdom",

    # Chapter 8: The Art of Cultivating the Soul (11 beats)
    "CH08_A01": "Heavy forged iron plowshare biting deep into hardened dry soil, turning over compacted crusts into rich dark underlying loam",
    "CH08_A02": "Strong agrarian hands guiding an ox-drawn wooden plow, deliberately breaking open stubborn patterns of pride and defensive rigidity",
    "CH08_A03": "Morning sun piercing deep into freshly furrowed trenches, airing out moldy dark cavities and warming the subterranean earth",
    "CH08_A04": "Laborer methodically digging up heavy limestone boulders with an iron crowbar and carrying them out beyond the perimeter wall",
    "CH08_A05": "Bare calloused hands covered in dark soil, tossing aside the last stubborn rocks with weary satisfaction and serene hope",
    "CH08_A06": "Pruning hook and sickle cutting through tangled thorny thickets, unearthing the roots of toxic worry with fearless resolve",
    "CH08_A07": "Living simply in quiet ascetic balance, stripping away superfluous luxuries and noisy ambition to restore clarity to the spirit",
    "CH08_A08": "Fresh earthenware amphora pouring cool crystalline spring water over freshly tilled soil, awakening the rich scent of fertile earth",
    "CH08_A09": "Soft warm light melting winter ice from the garden bed, healing old subterranean fractures with patient gentle warmth",
    "CH08_A10": "Restored fertile terraces ready for planting, rows of smooth crumbly soil waiting under a gentle morning sky for the sower arrival",
    "CH08_A11": "Sower standing at the edge of the renewed field at daybreak, holding a basket of premium seeds with quiet confidence in the coming harvest",

    # Chapter 9: Three Timeless Lessons for Life (10 beats)
    "CH09_A01": "Master craftsman patiently carving fine boxwood by candlelight, illustrating that true maturity cannot be rushed by impatient demands",
    "CH09_A02": "Hand gently tucking a tiny seed deep into dark soil, resisting the foolish urge to dig it up daily to measure invisible underground roots",
    "CH09_A03": "Towering ancient oak tree standing unshakeable amidst howling mountain storms, anchored by massive underground root systems twice as wide as its branches",
    "CH09_A04": "Compassionate traveler kneeling beside a wounded stranger on a dusty trail, looking past rough thorns to recognize shared fragile humanity",
    "CH09_A05": "Miraculous green shoot breaking through a crack in a seemingly dead stone monument, proving hope can resurrect from the most desolate grief",
    "CH09_A06": "Weathered hands freely releasing golden grain into the wind without counting returns, trusting in the quiet abundance of nature",
    "CH09_A07": "Helmsman keeping a firm hand on the wooden rudder through rolling ocean waves, controlling inner calm while the outer storm rages",
    "CH09_A08": "Flourishing orchard laden with sweet ripe figs and pomegranates, thriving because its roots tap into deep unpolluted springs",
    "CH09_A09": "Still clear mountain lake reflecting the infinite starry heavens without a single rippling wave of anxiety or pretense",
    "CH09_A10": "Majestic panoramic harvest vista where golden fields of wheat bow gracefully under the gentle golden glow of dawn",

    # Chapter 10: Nurturing the Good Seed Within (6 beats)
    "CH10_A01": "Solitary wanderer pausing beneath a majestic olive tree at dusk, breathing deeply and examining the fertile state of the inner soul",
    "CH10_A02": "Sparkling morning dewdrop resting gently on a green leaf, softening parched cracks in the soil with gentle grace and tender forgiveness",
    "CH10_A03": "Serene individual greeting the early dawn with a peaceful smile, extending warm words of encouragement to an anxious companion",
    "CH10_A04": "Vigorous young shoot rising gracefully toward the warm morning sky, bathed in a celestial beam of golden divine light",
    "CH10_A05": "Radiant luminous seed of peace glowing quietly within the sanctuary of the human heart, an inextinguishable divine ember",
    "CH10_A06": "Weathered agrarian sower looking serenely toward the expansive horizon, walking forward into a new day of patient faithful cultivation",
}


# ==============================================================================
# 3. LUAT_DOI_THUONG (117 beats)
# Style: LegalEagle / CNBC Make It
# ==============================================================================
LUAT_DOI_THUONG_SCENES: Dict[str, str] = {
    # Chapter 1: The Disappearing Deposit & Renter's Shock (10 beats)
    "CH01_A01": "Clean sunlit urban apartment interior on move-out day, with a young professional tenant holding packed cardboard boxes while expecting the return of a twenty million VND security deposit",
    "CH01_A02": "Landlord arriving at the apartment doorway with a critical scrutinizing expression, holding a lengthy clipboard checklist with a red ballpoint pen ready to note flaws",
    "CH01_A03": "Forensic perspective of the landlord inspecting wooden baseboards with a magnifying posture, searching meticulously for minor scuffs and microscopic blemishes",
    "CH01_A04": "Forensic detail of a faint pale mark on an off-white plaster wall and hairline micro-scuffs on hardwood floorboards being aggressively tallied on the landlord penalty sheet",
    "CH01_A05": "Landlord cold-facedly crossing out the entire twenty million deposit amount on a formal ledger while the stunned tenant stands frozen in disbelief beside packed luggage",
    "CH01_A06": "Frantic tenant flipping through the original paper lease agreement on a glass coffee table, finding past signatures now weaponized against their financial interests",
    "CH01_A07": "Detailed clause on a printed lease document showing heavily biased liquidated damages stipulations that leave the tenant completely defenceless",
    "CH01_A08": "Visual investigation metaphor showing a legal trap disguised beneath ordinary boilerplate rental contract paperwork",
    "CH01_A09": "Widespread phenomenon of systemic security deposit deductions affecting countless young urban apartment renters",
    "CH01_A10": "Tenant studying the open volume of the Vietnam Civil Code beneath a desk lamp, resolving to understand legal rights and statutory protections",

    # Chapter 2: Trap #1: Ambiguous Handover Protocol (11 beats)
    "CH02_A01": "Tenant hurriedly signing a key handover document on the first move-in day amidst moving boxes, trusting verbal goodwill without taking verification photos",
    "CH02_A02": "Macro focus on a single ambiguous phrase on the handover sheet reading apartment received in good condition without technical annexes or specifics",
    "CH02_A03": "The glaring absence of quantitative technical standards or baseline metrics attached to the vague good condition contract clause",
    "CH02_A04": "Handover document lacking any room-by-room inventory checklist, showing empty check-boxes that later become legal liabilities for the tenant",
    "CH02_A05": "Unrecorded existing hairline wall cracks and an aging yellowed wall air conditioner unit that was already decade-old upon initial move-in",
    "CH02_A06": "Time-lapse visual showing the natural physical aging and atmospheric oxidation of apartment fixtures over two years of normal occupancy",
    "CH02_A07": "Landlord demanding that the departing tenant pay for the complete replacement of a decade-old rusted air compressor unit",
    "CH02_A08": "Landlord pointing accusatorily at a warped kitchen cabinet hinge that was already misaligned long before the tenant moved in",
    "CH02_A09": "Unsubstantiated verbal recollection falling flat against written documentation when disputing pre-existing apartment defects",
    "CH02_A10": "Official move-in sheet signed two years prior showing the blank perfect state confirmation now turned decisively against the renter",
    "CH02_A11": "Dejected tenant sitting across from an unyielding landlord, realizing the severe legal cost of omitting photographic move-in documentation",

    # Chapter 3: Trap #2: Asymmetric Unilateral Termination (11 beats)
    "CH03_A01": "Sharp macro focus on the termination clause of a rental contract, exposing a blatant legal asymmetry between landlord and tenant rights",
    "CH03_A02": "Clause highlighted in red showing draconian penalty clauses applied strictly against the tenant while imposing zero accountability on the landlord",
    "CH03_A03": "Lease section dictating total forfeiture of one hundred percent of the security deposit if the tenant needs to vacate before the term ends",
    "CH03_A04": "Severe financial penalties binding the tenant contrasted against total impunity for the landlord upon breach of contract",
    "CH03_A05": "Landlord abruptly serving a seven-day notice to vacate because the property is being put up for sale or given to a relative",
    "CH03_A06": "Stressed tenant packing belongings in haste while the landlord returns only the base deposit without any compensatory penalty for early eviction",
    "CH03_A07": "Legal balance scale heavily tilted in favor of the lessor, violating fundamental principles of contractual equality and reciprocal consideration",
    "CH03_A08": "Disproportionate financial risk borne entirely by the tenant due to hidden contractual clauses accepted without careful legal scrutiny",
    "CH03_A09": "Model balanced contract provision where early termination penalties are mirrored identically for both lessor and lessee",
    "CH03_A10": "Equal reciprocal clause stipulating that early landlord termination requires refunding the deposit plus an identical penalty compensation sum",
    "CH03_A11": "Assertive tenant firmly marking red corrections on a draft lease agreement to establish bilateral reciprocity before signing",

    # Chapter 4: Trap #3: Exorbitant Repair Invoices & Depreciation (13 beats)
    "CH04_A01": "Move-out day table where the landlord slaps down a handwritten invoice listing exorbitant itemized charges for routine minor repairs",
    "CH04_A02": "Array of arbitrary punitive fees concocted by the landlord, demanding brand-new premium replacements for minor wear on old items",
    "CH04_A03": "Landlord demanding millions of VND to completely repaint the entire apartment because of standard slight discoloration of paint over time",
    "CH04_A04": "Landlord insisting on replacing the entire front door security lock assembly simply because the brass tumbler shows normal mechanical looseness",
    "CH04_A05": "Outrageous inflated line item for professional deep cleaning services added to the deduction tally without prior agreement",
    "CH04_A06": "Calculator screen where the landlord manufactured deductions add up precisely to or slightly exceed the twenty million deposit total",
    "CH04_A07": "Tenant refusing to pay additional surcharges and firmly demanding genuine fiscal receipts and third-party contractor invoices for all claimed repairs",
    "CH04_A08": "Landlord stammering and evading documentation when asked for certified VAT tax invoices and official repair company quotes",
    "CH04_A09": "Legal principle highlighting that unsubstantiated handwritten repair lists lack evidentiary standing to justify deposit deductions",
    "CH04_A10": "Landlord employing stall tactics, dodging phone calls and deliberately delaying deposit refunds hoping the tenant will tire and surrender",
    "CH04_A11": "Tenant remaining composed, organizing all written communications into a clear chronological evidentiary folder",
    "CH04_A12": "Visual comparison of natural paint fading versus intentional wall damage, demonstrating the clear distinction in property law",
    "CH04_A13": "Tenant holding ground with calm documentation, demonstrating that unsubstantiated deduction claims cannot withstand legal scrutiny",

    # Chapter 5: Civil Code 2015 Framework (13 beats)
    "CH05_A01": "Dignified leather-bound volume of the 2015 Civil Code of Vietnam open to Article 328 on security deposit regulations under clear daylight",
    "CH05_A02": "Legal maxim visualization showing statutory law overriding and nullifying any private contract clause that violates mandatory legal codes",
    "CH05_A03": "Article 472 of the Civil Code governing property lease contracts and defining reciprocal statutory duties of both parties",
    "CH05_A04": "Legal text of Article 479 of the Civil Code clearly delineating the tenant obligation to maintain leased assets in accordance with agreements",
    "CH05_A05": "Highlighting the core legal doctrine of natural wear and tear, exempting tenants from liability for inevitable property aging and deterioration",
    "CH05_A06": "Subtle natural fading of wall paint caused by seasonal humidity and ambient sunlight, legally recognized as non-compensable wear",
    "CH05_A07": "Soft worn polish on high-traffic wooden flooring around doorways, classified by statutory law as standard normal living wear",
    "CH05_A08": "Burned-out fluorescent light bulb reaching the end of its manufacturer-rated lifespan, classified as landlord operational overhead",
    "CH05_A09": "Statutory legal obligation requiring the landlord to maintain the leased premises in safe, habitable structural condition throughout occupancy",
    "CH05_A10": "Legal threshold defining tenant liability strictly to direct personal fault, negligence, or unauthorized physical alterations",
    "CH05_A11": "Graphic forensic distinction between a cracked glass pane caused by physical impact versus a window seal aged by weather",
    "CH05_A12": "Legal doctrine establishing that damages beyond natural wear must be empirically proven before any deposit forfeiture is permitted",
    "CH05_A13": "Burden of proof resting squarely on the lessor to substantiate claimed physical property damage with incontrovertible evidence",

    # Chapter 6: Handwritten Contracts & Digital Evidence Fortress (14 beats)
    "CH06_A01": "Legitimate handwritten rental contract bearing valid original signatures of both parties resting under an official courtroom seal of legal validity",
    "CH06_A02": "Legal explanation confirming that under Vietnamese law, rental contracts between private individuals do not require mandatory public notarization to be legally binding",
    "CH06_A03": "Tenant on move-in day methodically capturing comprehensive high-resolution digital photographs of every wall, fixture, and appliance",
    "CH06_A04": "Smartphone recording a continuous, unbroken, single-take video walkthrough entering from the front door through every room of the apartment",
    "CH06_A05": "Slow deliberate panning video inspecting every square meter of tiled flooring, ceiling corners, and minor existing hairline wall fractures",
    "CH06_A06": "Tenant testing bathroom water valves, flushing mechanisms, and electrical wall switches on camera to document working conditions on day one",
    "CH06_A07": "Mechanical electric utility meter and water meter dials clearly showing exact numerical baseline readings on move-in day",
    "CH06_A08": "Digital cloud messaging group showing the complete media package uploaded with certified timestamps and formally acknowledged by the landlord",
    "CH06_A09": "Screenshot of landlord written message confirming receipt and agreement with the move-in photographic inspection album",
    "CH06_A10": "Statutory validation of electronic data messages and digital media as recognized legal evidence under the Civil Procedure Code",
    "CH06_A11": "Encrypted cloud storage drive safely archiving all original photo files with preserved EXIF camera metadata and immutable timestamps",
    "CH06_A12": "Comprehensive digital evidence dossier ready to instantly refute any retroactive claim of tenant-caused property damage",
    "CH06_A13": "Landlord stunned into silence when shown move-in video proof showing the disputed air conditioner crack was already present two years prior",
    "CH06_A14": "Airtight shield of empirical digital documentation ensuring the safe return of the hard-earned deposit funds",

    # Chapter 7: The Bulletproof Handover Protocol (14 beats)
    "CH07_A01": "Tenant presenting a structured five-point protective contract addendum to the landlord before signing the initial lease agreement",
    "CH07_A02": "Clear legal clauses establishing enforceable parameters that prevent arbitrary deductions and guarantee prompt deposit refund",
    "CH07_A03": "Strict clause mandating the full return of the security deposit within a maximum of five business days following key handover",
    "CH07_A04": "Addendum rule strictly prohibiting unilateral deductions and requiring certified commercial invoices from licensed third-party contractors",
    "CH07_A05": "Symmetrical liquidated damages clause requiring landlord to pay double the deposit amount if the tenant is evicted prematurely",
    "CH07_A06": "Clear division of structural maintenance responsibility, allocating concealed plumbing leaks and foundational wall cracks exclusively to the lessor",
    "CH07_A07": "Forty-eight-hour repair response SLA allowing tenant to commission emergency repairs and deduct costs from future rent if landlord stalls",
    "CH07_A08": "Explicit contractual exemption protecting the tenant from financial liability for natural paint discoloration and normal wear",
    "CH07_A09": "Reference to Civil Code protections cited directly in the addendum to reinforce statutory rights regarding property deterioration",
    "CH07_A10": "Formal room-by-room move-in condition checklist signed by both parties and annexed as an indivisible schedule to the main lease",
    "CH07_A11": "Tenant and landlord initialing every single page of the contract and annexes along the page margins to eliminate any document substitution",
    "CH07_A12": "Two original signed contract copies resting side by side with fresh blue ink signatures and identical date stamps for each party",
    "CH07_A13": "Comprehensive binder holding the executed contract, verified annexes, and stamped photos, forming an impregnable legal defense",
    "CH07_A14": "Tenant holding the finalized contract folder with confidence, knowing the deposit is safeguarded by meticulous legal foresight",

    # Chapter 8: Tactical Negotiation & Dispute Escalation (13 beats)
    "CH08_A01": "Tenant maintaining total emotional composure during a tense move-out walkthrough, speaking firmly without raising voice or showing agitation",
    "CH08_A02": "Tenant avoiding physical confrontation or heated arguments, relying instead on structured legal arguments and verifiable documentation",
    "CH08_A03": "Tenant opening the initial move-in dossier on a tablet before the landlord, displaying timestamped photos matching pre-existing flaws",
    "CH08_A04": "Tenant citing Article 472 of the Civil Code of Vietnam, firmly reminding the lessor of the statutory legal obligation to return deposit funds",
    "CH08_A05": "Tenant demanding official tax invoices for any claimed repair costs and categorically rejecting arbitrary handwritten deduction sheets",
    "CH08_A06": "Drafting a formal written handover minutes recording the landlord refusal to refund the deposit, creating written evidence of default",
    "CH08_A07": "Tenant calmly notifying the landlord of impending escalation to the local Ward People Committee and neighbourhood police for mediation",
    "CH08_A08": "Landlord showing signs of anxiety at the prospect of administrative scrutiny, fearing municipal audit of rental tax and residency compliance",
    "CH08_A09": "Tenant delivering a formal written demand letter for deposit refund with an explicit three-day deadline for amicable settlement",
    "CH08_A10": "Formal notice letter stating that failure to refund will immediately trigger legal complaints to the district civil court and tax authority",
    "CH08_A11": "Confident tenant standing resolute on verified facts and legal statues, neutralizing landlord intimidation tactics",
    "CH08_A12": "Landlord recognizing that arbitrary deduction tactics will fail completely against a tenant backed by documented evidence and law",
    "CH08_A13": "Landlord begrudgingly signing the full deposit refund receipt and transferring the twenty million VND back to the tenant bank account",

    # Chapter 9: Three Steps to Legal Action & Court Mediation (12 beats)
    "CH09_A01": "Tenant stepping through the entrance of the local Ward People Committee building to file a formal grassroots mediation petition",
    "CH09_A02": "Infographic demonstrating that small claims rental deposit disputes are handled under expedited civil summary procedures",
    "CH09_A03": "Modest court fee filing receipt showing the negligible cost of a few hundred thousand VND, fully recoverable from the losing defendant",
    "CH09_A04": "Ward People Committee civil officer formally stamping the tenant mediation request to initiate administrative conciliation",
    "CH09_A05": "Formal conciliation hearing inside the Ward administrative office, with the commune mediator reviewing evidence from both parties",
    "CH09_A06": "Well-organized filing envelope delivered to the District People Court containing the lease contract, handover protocol, and bank statements",
    "CH09_A07": "Pre-trial court conciliation chamber where a civil judge examines the timestamped video evidence, guiding the landlord to settle",
    "CH09_A08": "Official court decision recording a binding mediated settlement, carrying the full immediate force of judicial enforcement",
    "CH09_A09": "Bank notification showing court-ordered asset freeze on landlord accounts in the event of persistent refusal to comply with judicial settlement",
    "CH09_A10": "Financial ledger calculating statutory interest accrued on the unlawfully withheld deposit sum under Civil Code Article 357",
    "CH09_A11": "Itemized judicial order assessing all court filing costs, mediation expenses, and legal fees against the losing non-compliant lessor",
    "CH09_A12": "Tenant walking out of the courthouse in bright sunshine, having secured full financial recovery through lawful justice",

    # Chapter 10: The Sovereign Renter's Checklist (6 beats)
    "CH10_A01": "Serene, warm, newly rented apartment living room bathed in soft morning light, representing a peaceful haven grounded in legal security",
    "CH10_A02": "Diligent renter methodically annotating a draft lease contract at a clean desk before committing any signature",
    "CH10_A03": "Tenant taking timestamped verification photographs of every room corner, establishing an unshakeable digital record before moving a single box",
    "CH10_A04": "Savvy tenant holding an organized folder of contracts and annexes, relying on legal literacy rather than verbal disputes to safeguard property",
    "CH10_A05": "Young professionals sharing a standard protective rental checklist with friends around a bright cafe table, promoting tenant empowerment",
    "CH10_A06": "Clean contract document stamped with verified approval, illustrating how legal awareness turns every lease into a safe, secure home",
}


def audit_channel_scenes(slug: str, scenes: Dict[str, str], expected_count: int) -> Dict[str, Any]:
    """Verify invariants for a channel's scene dictionary."""
    base_path = Path("sys/runs/batch1_merged_drafts") / f"{slug}_merged_base.json"
    with open(base_path, "r", encoding="utf-8") as f:
        base_beats = json.load(f)
    base_ids = [b["beat_id"] for b in base_beats]

    missing_keys = set(base_ids) - set(scenes.keys())
    extra_keys = set(scenes.keys()) - set(base_ids)

    descriptions = list(scenes.values())
    unique_desc = set(descriptions)

    non_ascii_issues = []
    buzzword_issues = []
    boilerplate_issues = []

    for k, text in scenes.items():
        if any(ord(c) >= 128 for c in text):
            non_ascii_issues.append((k, text))
        if BUZZWORDS_REGEX.search(text):
            buzzword_issues.append((k, text))
        if "clearly demonstrating the cause-and-effect" in text.lower():
            boilerplate_issues.append((k, text))

    report = {
        "slug": slug,
        "count": len(scenes),
        "expected_count": expected_count,
        "count_matches": len(scenes) == expected_count,
        "missing_keys": list(missing_keys),
        "extra_keys": list(extra_keys),
        "unique_count": len(unique_desc),
        "is_100_unique": len(unique_desc) == len(scenes),
        "non_ascii_count": len(non_ascii_issues),
        "buzzword_count": len(buzzword_issues),
        "boilerplate_count": len(boilerplate_issues),
        "is_clean": (
            len(missing_keys) == 0
            and len(extra_keys) == 0
            and len(unique_desc) == len(scenes)
            and len(non_ascii_issues) == 0
            and len(buzzword_issues) == 0
            and len(boilerplate_issues) == 0
        ),
    }
    return report


def main():
    print("=================================================================")
    print("Worker 3: Rebuilding specs for 3 Batch 1 channels")
    print("=================================================================")

    tasks = [
        ("la_ban_hoc_thuat", LA_BAN_HOC_THUAT_SCENES, 98),
        ("loi_sang_soi", LOI_SANG_SOI_SCENES, 98),
        ("luat_doi_thuong", LUAT_DOI_THUONG_SCENES, 117),
    ]

    all_valid = True
    compilation_reports = {}

    for slug, scenes, expected_cnt in tasks:
        print(f"\n--- [1] Auditing scenes for {slug} ---")
        audit = audit_channel_scenes(slug, scenes, expected_cnt)
        print(f"  Count: {audit['count']}/{audit['expected_count']} (matches: {audit['count_matches']})")
        print(f"  Unique: {audit['unique_count']}/{audit['count']} (100% unique: {audit['is_100_unique']})")
        print(f"  Non-ASCII: {audit['non_ascii_count']}")
        print(f"  Buzzwords: {audit['buzzword_count']}")
        print(f"  Boilerplate: {audit['boilerplate_count']}")
        print(f"  Audit clean: {audit['is_clean']}")

        if not audit["is_clean"]:
            print(f"ERROR: Audit failed for {slug}!")
            all_valid = False
            continue

        print(f"--- [2] Compiling and saving spec for {slug} ---")
        report = compile_and_save_spec(slug, scenes)
        compilation_reports[slug] = report
        print(f"  Beat count: {report['beat_count']}")
        print(f"  Unique prompts: {report['unique_prompts']}/{report['beat_count']} (100%: {report['is_100_unique']})")
        print(f"  Total dur: {report['total_duration']}s, TTS dur: {report['tts_duration']}s (diff: {report['duration_diff']}s)")
        print(f"  Non-ASCII count: {report['non_ascii_count']}")
        print(f"  SPEC IS VALID: {report['is_valid']}")

        if not report["is_valid"]:
            print(f"ERROR: Spec compilation marked invalid for {slug}!")
            all_valid = False

    print("\n=================================================================")
    if all_valid:
        print("SUCCESS: All 3 channels passed strict validation and compiled successfully!")
    else:
        print("FAILURE: One or more channels failed validation.")
        sys.exit(1)


if __name__ == "__main__":
    main()
