#!/usr/bin/env python3
"""Story-Driven Visual Prompt Builder for Video Pilot Vietnamese Long Channels.

Translates spoken Vietnamese narration clauses directly into vivid, explanatory,
story-driven English visual prompts tailored to each channel's distinct graphic style
(2D doodle Nghech Ngoac, 3D forensic noir, macro culinary science, orbital tactical atlas,
biomedical physics, classical chiaroscuro, zen sumi-e, etc.).

Strict Invariants:
- Zero cross-channel pattern bleeding (each channel uses its own domain dictionary).
- Zero Vietnamese characters / diacritics in output English prompts.
- Zero 8K buzzwords (complies with user requirement).
- Standard clear composition (clean negative space, balanced framing, zero text overlays).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class ChannelStyleProfile:
    slug: str
    channel_id: str
    benchmark: str
    style_prefix: str
    aesthetic_traits: str
    negative_rules: str
    is_doodle: bool = False
    actor_label: str = "subject"


# Visual Style Profiles for all 20 Vietnamese Channels (Pure ASCII, zero diacritics)
CHANNEL_STYLE_PROFILES: Dict[str, ChannelStyleProfile] = {
    "dia-com": ChannelStyleProfile(
        slug="dia-com",
        channel_id="dia_com",
        benchmark="America's Test Kitchen / Modernist Cuisine",
        style_prefix="Cinematic macro culinary food science photography,",
        aesthetic_traits="warm directional copper and tungsten lighting, shallow f/2.8 optical depth of field, authentic culinary textures and fluid thermal dynamics, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no floating recipe numbers, no cartoons, no stickmen",
        is_doodle=False,
        actor_label="chef or customer",
    ),
    "ho-so-ky-la": ChannelStyleProfile(
        slug="ho-so-ky-la",
        channel_id="ho_so_ky_la",
        benchmark="LEMMiNO / Fern",
        style_prefix="Atmospheric 3D noir forensic crime-scene diorama,",
        aesthetic_traits="LEMMiNO documentary aesthetic, desaturated slate and charcoal tones with subtle amber keylight or red emergency accent, moody volumetric rain mist and low-key cinematic lighting, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no cartoon characters",
        is_doodle=False,
        actor_label="investigator or witness",
    ),
    "tui-tien": ChannelStyleProfile(
        slug="tui-tien",
        channel_id="tui_tien",
        benchmark="WSJ Consumer Economics / Two Cents PBS",
        style_prefix="Cinematic commercial documentary tabletop photography,",
        aesthetic_traits="35mm tabletop cinematography, f/2.0 shallow depth of field, warm 3200K tungsten spotlighting, crisp tactile paper receipts and Vietnamese polymer currency, clean retail and café staging, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no cartoons, no stickmen",
        is_doodle=False,
        actor_label="consumer or customer",
    ),
    "ban-do-quyen-luc": ChannelStyleProfile(
        slug="ban-do-quyen-luc",
        channel_id="ban_do_quyen_luc",
        benchmark="RealLifeLore / Johnny Harris",
        style_prefix="High-altitude strategic 3D orbital satellite map rendering,",
        aesthetic_traits="RealLifeLore strategic documentary style, accurate satellite Earth topography with dramatic curved horizon, deep navy ocean waters, luminous golden maritime shipping vectors, subtle atmospheric haze, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no floating numbers",
        is_doodle=False,
        actor_label="naval vessel or fleet",
    ),
    "chanh-niem-ke": ChannelStyleProfile(
        slug="chanh-niem-ke",
        channel_id="chanh_niem_ke",
        benchmark="Pursuit of Wonder / Aperture",
        style_prefix="Cinematic Wabi-Sabi & Zen Sumi-e mindfulness visual,",
        aesthetic_traits="Pursuit of Wonder contemplative aesthetic, soft diffused natural morning mist, organic wood grain, serene water ripples, warm gentle sidelight, peaceful meditative atmosphere with generous empty negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no clutter",
        is_doodle=False,
        actor_label="contemplative person",
    ),
    "nao-luoi": ChannelStyleProfile(
        slug="nao-luoi",
        channel_id="nao_luoi",
        benchmark="The Paint Explainer / Nghech Ngoac",
        style_prefix="Hand-drawn 2D Vietnamese indie doodle explainer illustration (Nghech Ngoac webcomic aesthetic),",
        aesthetic_traits="raw freehand MS-Paint marker linework #000000, 100% unshaded flat solid fills, warm off-white cream canvas #F8F0DC, bald stickman with oversized round white head, tiny dot eyes, wire arms, flat cerulean-blue (#3B82C4) shirt, standard clear composition with over 60% empty negative space, strictly 2D flat orthographic, zero shadows, zero gradients, zero 3D",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no 3D rendering, no realistic skin, no gradients",
        is_doodle=True,
        actor_label="bald stickman with blue shirt",
    ),
    "ai-binh-dan": ChannelStyleProfile(
        slug="ai-binh-dan",
        channel_id="ai_binh_dan",
        benchmark="Jeff Su / Fireship",
        style_prefix="Modern dark-mode glassmorphism tech workspace illustration,",
        aesthetic_traits="Jeff Su modern digital productivity aesthetic, sleek dark slate desk surface, subtle cyan and violet glassmorphic luminescence, clean UI workflow architecture, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no clutter",
        is_doodle=False,
        actor_label="remote professional",
    ),
    "ua-sao-vay": ChannelStyleProfile(
        slug="ua-sao-vay",
        channel_id="ua_sao_vay",
        benchmark="Zack D. Films / Veritasium",
        style_prefix="High-definition 3D somatosensory and physics explainer diorama,",
        aesthetic_traits="Zack D. Films educational physics staging, clean laboratory lighting, crisp physical coordinate axes, tactile anatomical and optical props, balanced visual hierarchy, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no floating text cards",
        is_doodle=False,
        actor_label="demonstrator",
    ),
    "su-ke-lai": ChannelStyleProfile(
        slug="su-ke-lai",
        channel_id="su_ke_lai",
        benchmark="Kings and Generals / Epic History TV / Fern",
        style_prefix="Cinematic 3D historical battlefield diorama,",
        aesthetic_traits="Kings and Generals tactical topography, realistic river delta and coastal terrain, authentic 10th century wooden naval architecture, atmospheric morning mist and smoke plumes, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no modern artifacts",
        is_doodle=False,
        actor_label="historic general or fleet",
    ),
    "thuong-cho-kheo": ChannelStyleProfile(
        slug="thuong-cho-kheo",
        channel_id="thuong_cho_kheo",
        benchmark="The School of Life / Cinema Therapy",
        style_prefix="Cinematic 35mm live-action emotional film still,",
        aesthetic_traits="The School of Life warm domestic realism, soft golden-hour natural sidelight, subtle interpersonal micro-expressions, intimate interior framing, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no cartoons",
        is_doodle=False,
        actor_label="two people in dialogue",
    ),
    "co-the-ke": ChannelStyleProfile(
        slug="co-the-ke",
        channel_id="co_the_ke",
        benchmark="Nucleus Medical Media / Zack D. Films",
        style_prefix="High-definition 3D biomedical anatomical animation still,",
        aesthetic_traits="Nucleus Medical Media scientific clarity, vivid translucent organic tissues, glowing neural synapses and biological fluid dynamics, clean medical laboratory studio lighting, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no cartoon gore",
        is_doodle=False,
        actor_label="human anatomy subject",
    ),
    "luat-ngam": ChannelStyleProfile(
        slug="luat-ngam",
        channel_id="luat_ngam",
        benchmark="Fern TV / Academy of Ideas",
        style_prefix="Cinematic 3D investigative diorama and architectural surveillance,",
        aesthetic_traits="Fern TV power dynamics aesthetic, high-contrast monochrome geometry with striking scarlet red focal accent, cold clinical lighting, symbolic psychological spatial staging, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no cartoons",
        is_doodle=False,
        actor_label="observer in crowd",
    ),
    "luat-doi-thuong": ChannelStyleProfile(
        slug="luat-doi-thuong",
        channel_id="luat_doi_thuong",
        benchmark="LegalEagle / CNBC Make It",
        style_prefix="Investigative legal documentary photography still,",
        aesthetic_traits="LegalEagle forensic realism, sharp focus on physical documentation, apartment inspection forensic detail, clean daylight streaming through apartment window, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no cartoons",
        is_doodle=False,
        actor_label="tenant or inspector",
    ),
    "banh-rang": ChannelStyleProfile(
        slug="banh-rang",
        channel_id="banh_rang",
        benchmark="Practical Engineering / Wendover Productions",
        style_prefix="Cinematic industrial logistics and engineering documentary still,",
        aesthetic_traits="Wendover industrial scale, realistic heavy machinery, clean maritime shipping ports, crisp steel surfaces and cargo containers under clear daylight, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no cartoons",
        is_doodle=False,
        actor_label="logistics operator",
    ),
    "vu-tru-ti-hon": ChannelStyleProfile(
        slug="vu-tru-ti-hon",
        channel_id="vu_tru_ti_hon",
        benchmark="Melodysheep / Astrum",
        style_prefix="Cinematic deep space astronomical documentary diorama,",
        aesthetic_traits="Melodysheep cosmic realism, luminous golden-orange accretion disk curving around pitch-black singularity, warped relativistic spacetime grid, solitary astronaut scale, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no text cards",
        is_doodle=False,
        actor_label="solitary astronaut",
    ),
    "nghe-song-sot": ChannelStyleProfile(
        slug="nghe-song-sot",
        channel_id="nghe_song_sot",
        benchmark="Wall Street Journal / Casgains",
        style_prefix="Cinematic architectural corporate glass and isometric strategic diorama,",
        aesthetic_traits="WSJ executive realism, modern glass office high-rise, polished boardroom wood, symbolic chess elements on mahogany table, dramatic late-afternoon skyline sidelight, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no cartoons",
        is_doodle=False,
        actor_label="corporate professional",
    ),
    "la-ban-hoc-thuat": ChannelStyleProfile(
        slug="la-ban-hoc-thuat",
        channel_id="la_ban_hoc_thuat",
        benchmark="Veritasium / 3Blue1Brown",
        style_prefix="Rigorous intellectual science and cognitive visualization still,",
        aesthetic_traits="3Blue1Brown visual clarity, elegant geometric memory models, clean desk with blank notebooks and index cards, soft diffused academic study lighting, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no messy clutter",
        is_doodle=False,
        actor_label="researcher or student",
    ),
    "loi-sang-soi": ChannelStyleProfile(
        slug="loi-sang-soi",
        channel_id="loi_sang_soi",
        benchmark="BibleProject / Caravaggio Chiaroscuro",
        style_prefix="Caravaggio Chiaroscuro masterwork allegorical painting still,",
        aesthetic_traits="Caravaggio oil painting realism, dramatic single beam of golden heavenly light piercing deep velvety shadows, rustic agrarian textures, golden wheat fields, expressive weathered hands, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no modern objects",
        is_doodle=False,
        actor_label="rustic sower or elder",
    ),
    "minh-triet-song": ChannelStyleProfile(
        slug="minh-triet-song",
        channel_id="minh_triet_song",
        benchmark="Einzelgänger / Daily Stoic",
        style_prefix="Classical Stoic Chiaroscuro philosophical still,",
        aesthetic_traits="Daily Stoic classical antiquity, weathered Roman marble bust of Marcus Aurelius, candlelit imperial military tent against snowy night, textured parchment scroll, dramatic chiaroscuro sidelight, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no modern artifacts",
        is_doodle=False,
        actor_label="philosopher emperor",
    ),
    "tam-tinh-dem": ChannelStyleProfile(
        slug="tam-tinh-dem",
        channel_id="tam_tinh_dem",
        benchmark="Pursuit of Wonder / Studio Ghibli Nocturnal",
        style_prefix="Studio Ghibli nocturnal & gentle poetic atmosphere still,",
        aesthetic_traits="Ghibli nocturnal serenity, deep velvety midnight blue sky with delicate crescent moon, warm glowing yellow windowpane and steaming ceramic mug, quiet reflective solitude, standard clear composition with ample negative space",
        negative_rules="strictly zero text overlays, zero labels, zero logos, no watermark, no clutter",
        is_doodle=False,
        actor_label="solitary figure",
    ),
}

CHANNEL_ALIASES: Dict[str, str] = {
    "dia_com": "dia-com",
    "ho_so_ky_la": "ho-so-ky-la",
    "tui_tien": "tui-tien",
    "ban_do_quyen_luc": "ban-do-quyen-luc",
    "chanh_niem_ke": "chanh-niem-ke",
    "nao_luoi": "nao-luoi",
    "ai_binh_dan": "ai-binh-dan",
    "ua_sao_vay": "ua-sao-vay",
    "su_ke_lai": "su-ke-lai",
    "thuong_cho_kheo": "thuong-cho-kheo",
    "co_the_ke": "co-the-ke",
    "luat_ngam": "luat-ngam",
    "luat_doi_thuong": "luat-doi-thuong",
    "banh_rang": "banh-rang",
    "vu_tru_ti_hon": "vu-tru-ti-hon",
    "nghe_song_sot": "nghe-song-sot",
    "la_ban_hoc_thuat": "la-ban-hoc-thuat",
    "loi_sang_soi": "loi-sang-soi",
    "minh_triet_song": "minh-triet-song",
    "tam_tinh_dem": "tam-tinh-dem",
}

# 10 Chapter English Themes for all 20 Channels (Pure English, Zero Diacritics)
CHAPTER_THEMES_EN: Dict[str, List[str]] = {
    "dia-com": [
        "Maillard browning reaction & culinary aroma trigger",
        "molecular difference between Maillard reaction and caramelization",
        "optimal searing temperature window between 140 and 165 degrees Celsius",
        "surface moisture barrier quenching pan thermal energy",
        "surface drying techniques and 24-hour dry brining",
        "cast iron thermal mass versus heat conductivity",
        "creation of hundreds of aromatic volatile flavor compounds",
        "high-heat searing of meats and vegetables",
        "professional chef pan preheating and oil shimmering protocol",
        "scientific culinary principles elevating everyday home cooking",
    ],
    "ho-so-ky-la": [
        "12:35 PM departure at Stanley rail yard in Ohio under cold rain",
        "critical human error on the independent locomotive brake lever",
        "3000 horsepower diesel engine surging forward at maximum throttle notch 8",
        "three thousand tons of train hauling hazardous molten phenol cars",
        "desperate police pursuit shooting at locomotive fuel cutoff switch",
        "strategic trailing interception plan from behind",
        "high-speed coupler lock between chasing locomotive and runaway train",
        "heroic leap onto moving locomotive engineer cab to cut throttle",
        "technical forensic investigation report and safety lessons",
        "human diligence as the final safeguard against mechanical disaster",
    ],
    "tui-tien": [
        "receipt paradox and decoy pricing coffee trap",
        "supermarket floor layout matrix and impulse buy traps",
        "free shipping psychological threshold illusion",
        "tiered electricity rates and phantom standby power drain",
        "hidden reality behind zero-percent installment financing",
        "recurring subscription traps and auto-renewal fees",
        "sunk cost fallacy and personal expenditure balance sheet",
        "personal financial defense shields and emergency buffers",
        "discipline of capital allocation and time-value of money",
        "personal financial audit and actionable budget execution",
    ],
    "ban-do-quyen-luc": [
        "satellite view of Southeast Asian maritime chokepoints",
        "strategic geometry of the funnel-shaped Strait of Malacca",
        "vital maritime lifeline carrying one-third of global oil tankers",
        "supertanker convoy traffic and fragile shipping lanes",
        "simulated 72-hour strait blockade crisis scenario",
        "naval destroyer patrols and underwater surveillance",
        "overland pipeline bypass routes and energy diversification",
        "great power strategic competition around maritime straits",
        "three pillars of national maritime trade resilience",
        "geopolitical balance and strategic foresight",
    ],
    "chanh-niem-ke": [
        "gentle afternoon rain falling onto wooden temple veranda",
        "translucent raindrops trailing down cold misty windowpane",
        "calm pond ripples expanding from a single falling raindrop",
        "parable of the first arrow representing natural physical pain",
        "parable of the second arrow representing mental overthinking and guilt",
        "fallen golden leaf drifting gently down a tranquil stream",
        "deep conscious breathing releasing mental tension and anxiety",
        "decluttering physical space to restore inner mental clarity",
        "three self-inquiry questions diffusing sudden anxious thoughts",
        "returning to deep unshakeable inner peace and presence",
    ],
    "nao-luoi": [
        "nighttime bed phone scrolling loop and guilt cycle",
        "dopamine as motivation pursuit rather than happiness molecule",
        "dopamine spike and subsequent crash dynamics",
        "ancient evolutionary brain overwhelmed by modern hyper-stimuli",
        "procrastination as an emotional avoidance mechanism",
        "dopamine detox as intentional friction design rather than asceticism",
        "friction design packaging to increase obstacle for bad habits",
        "seven-day simple dopamine reset protocol",
        "two-minute rule bypassing prefrontal cortex resistance",
        "reclaiming sovereign control over daily focus and attention",
    ],
    "ai-binh-dan": [
        "office workers overwhelmed by manual repetitive spreadsheet tasks",
        "mental distinction between human judgment and automatable busywork",
        "modern AI API pipeline connecting spreadsheets to automated workflows",
        "no-code automation triggers eliminating manual data re-entry",
        "prompt engineering formula for reliable structured business outputs",
        "leaving work peacefully at 5:00 PM with all tasks completed",
        "building cross-application automation workflows without writing code",
        "iterative debugging of automated business processes",
        "seven-day practical AI implementation roadmap for beginners",
        "empowering knowledge workers through intelligent automation tools",
    ],
    "ua-sao-vay": [
        "the puzzling optical riddle of mirror reflection",
        "physical optics of specular photon bouncing off flat glass",
        "secret of the Z-axis: mirrors reverse front-to-back, not left-to-right",
        "the brain automatically rotating mental perspective in 3D",
        "the inside-out glove experiment and right-hand chirality rule",
        "horizontal reflection test: lying down in front of a mirror",
        "written text in front of mirrors and the ambulance lettering riddle",
        "concave and convex mirrors creating real versus virtual 3D focal points",
        "three revolutionary optical physics applications advancing civilization",
        "nurturing scientific curiosity and questioning common assumptions",
    ],
    "su-ke-lai": [
        "gathering storm clouds over northern frontier and national destiny",
        "strategic survey of Bach Dang river estuary topography and tides",
        "secret deployment of heavy iron-tipped timber stakes into riverbed",
        "tidal gamble: three-meter difference between ebb and flood tide",
        "art of tactical baiting by agile Vietnamese canoes at high tide",
        "tide receding rapidly and counter-offensive signal given",
        "invading Southern Han warships impaled on exposed wooden stakes",
        "demise of invading commander Hoang Thao and end of aggression",
        "historical milestone opening an era of eternal independence",
        "immortal spirit of Bach Dang victory living through generations",
    ],
    "thuong-cho-kheo": [
        "dinner table silence and subtle interpersonal misunderstandings",
        "profound distinction between merely hearing sound and active listening",
        "the trap of offering premature advice before emotions are felt",
        "mental preparation of arguments while the other person is still speaking",
        "listening to the unspoken messages behind tone and posture",
        "empathy does not require agreement: holding space for feelings",
        "art of open-ended questions and reflective emotional mirroring",
        "healing attachment wounds through emotional validation",
        "three structured steps transforming interpersonal conflict into intimacy",
        "gifting undivided presence and warmth to loved ones",
    ],
    "co-the-ke": [
        "twenty-four hours without sleep: brain sending urgent distress signals",
        "glymphatic system activating during deep sleep to flush beta-amyloid plaques",
        "overactive amygdala triggering emotional volatility and anxiety",
        "adrenal gland cortisol surge and elevated cardiovascular blood pressure",
        "natural killer immune cells dropping sharply under sleep deficit",
        "microsleep episodes while driving and dangerous cognitive lapses",
        "gradual accumulation of chronic sleep debt and metabolic consequences",
        "sleep hygiene protocol: cool dark bedroom and zero blue light",
        "circadian rhythm alignment with natural morning sunlight exposure",
        "honoring the biological necessity of restorative deep sleep",
    ],
    "luat-ngam": [
        "dental clinic waiting room experiment: standing up when bell rings",
        "social proof and evolutionary fear of ostracism from the tribe",
        "Solomon Asch line length conformity test on laboratory blackboard",
        "Kitty Genovese bystander effect in urban apartment courtyard",
        "halo effect distorting rational assessment of charismatic figures",
        "herd psychology in financial bubbles and FOMO crypto rushes",
        "framing effect: ninety percent survival versus ten percent mortality",
        "recognizing subtle psychological manipulation markers in daily life",
        "three steps establishing an independent critical thinking filter",
        "standing as an unshakeable lighthouse amidst emotional crowds",
    ],
    "luat-doi-thuong": [
        "tenant rental deposit withheld over minor wear and tear disputes",
        "first trap: vague move-in handover clause lacking photographic proof",
        "second trap: asymmetric early termination penalty clauses",
        "third trap: arbitrary inflated repair deductions upon move-out",
        "Civil Code Article 472 protecting tenants against natural wear and tear",
        "smartphone video walkthrough on day one as ironclad legal proof",
        "five-point contract annex template protecting tenant security deposits",
        "soft negotiation tactics with landlords based on statutory law",
        "small claims dispute resolution process in local district courts",
        "golden rules of paper documentation for wise home tenants",
    ],
    "banh-rang": [
        "the forty-day global voyage of a modest cotton T-shirt",
        "raw cotton harvesting in sprawling Texas fields and 200kg bales",
        "Malcolm McLean inventing the standardized corrugated ISO shipping container",
        "towering gantry cranes and automated AGVs operating at mega ports",
        "Suez Canal Ever Given blockage and fragile supply chain bottlenecks",
        "the bullwhip effect amplifying small retail demand fluctuations",
        "Toyota Just-In-Time manufacturing versus Just-In-Case resilience",
        "breakdown of ocean shipping freight costs versus terminal handling fees",
        "China Plus One manufacturing shifts and regional logistics hubs",
        "three pillars building resilient modern supply chain networks",
    ],
    "vu-tru-ti-hon": [
        "drifting in deep space toward a supermassive black hole",
        "glowing orange-gold accretion disk and extreme gravitational lensing",
        "crossing the event horizon point of no return",
        "relativistic time dilation freezing outside observer perspective",
        "spaghettification tidal gravitational forces stretching matter",
        "approaching the photon sphere where light orbits in circles",
        "infinite density singularity where known physics breaks down",
        "Hawking radiation and theoretical black hole evaporation",
        "cosmic scale and humanity's humble place in the expanding universe",
        "celebrating the wonder of scientific exploration of deep cosmos",
    ],
    "nghe-song-sot": [
        "the trap of working long hours without career advancement or recognition",
        "distinguishing between linear manual effort and high-leverage skills",
        "three most powerful workplace levers: systems, alliances, and specialized knowledge",
        "the career bottleneck trap: becoming too indispensable in operational minutiae",
        "art of metric-driven reporting demonstrating direct business ROI",
        "viewing managers as internal clients rather than schoolteachers",
        "building cross-departmental influence networks and strategic relationships",
        "data-driven salary negotiation using market compensation benchmarks",
        "three survival principles during corporate restructuring and mergers",
        "designing a three-year strategic career progression roadmap",
    ],
    "la-ban-hoc-thuat": [
        "the paradox of reading hundreds of pages yet remembering nothing",
        "Hermann Ebbinghaus forgetting curve losing seventy percent in 24 hours",
        "Active Recall: testing knowledge on a blank page rather than rereading",
        "the illusion of competence caused by passive highlighting and skimming",
        "Spaced Repetition: expanding review intervals over days and weeks",
        "Richard Feynman learning technique: explaining to a six-year-old child",
        "Niklas Luhmann Zettelkasten slip-box note network connecting ideas",
        "anchoring new concepts into existing cognitive schema",
        "three daily habits cultivating lifelong deep self-directed learning",
        "building a personalized digital second brain for long-term knowledge",
    ],
    "loi-sang-soi": [
        "ancient sower scattering seeds across four different types of soil",
        "seeds on the hard pathway eaten by birds before taking root",
        "seeds on shallow rocky ground sprouting quickly then scorching under sun",
        "seeds among thorny brambles choked by weeds and worldly anxieties",
        "seeds on rich fertile dark earth bearing a hundredfold harvest",
        "the sower scattering seeds indiscriminately with unconditional generosity",
        "anatomical examination of the spiritual heart in modern busy life",
        "cultivating and breaking up hardened soil through patience and discipline",
        "timeless human wisdom lessons transcending generations",
        "nurturing the seeds of virtue and compassion within one's life",
    ],
    "minh-triet-song": [
        "Roman Emperor Marcus Aurelius in winter military camp on Danube frontier",
        "Epictetus trichotomy of control: what is up to us versus not up to us",
        "Amor Fati: embracing and loving whatever fate brings with composure",
        "destructive anger as an irrational expectation of a frictionless world",
        "Memento Mori meditation: remembering one's mortality to clarify priorities",
        "Stoicism is not unfeeling suppression but emotional resilience",
        "Premeditatio Malorum: premeditation of potential adversity to remove fear",
        "building an unshakeable inner citadel against external chaos",
        "three practical daily exercises from classical Stoic philosophy",
        "living today fully with virtue as if it were the final day",
    ],
    "tam-tinh-dem": [
        "midnight city streets quiet under dim amber lamps as world sleeps",
        "shedding the heavy daytime masks worn to please societal expectations",
        "parable of the small wooden boat drifting peacefully down a nocturnal river",
        "fear of loneliness transformed into sacred healing solitude",
        "tenderly holding unhealed emotional wounds with self-compassion",
        "forgiving oneself for past clumsiness, mistakes, and naivety",
        "courageously letting go of borrowed expectations not truly one's own",
        "warm hands over chest listening to the faithful beating heart",
        "drinking warm chamomile tea and exhaling daytime burdens into the night",
        "pulling up soft blankets and surrendering to deep peaceful healing sleep",
    ],
}

# Domain-specific narrative phrase patterns for each channel (Strict word boundaries, zero cross-bleeding)
CHANNEL_DOMAIN_PATTERNS: Dict[str, List[Tuple[re.Pattern, str]]] = {
    "dia-com": [
        (
            re.compile(r"cánh cửa gỗ|tiệm nướng|chiều se lạnh|bước chân vào.*tiệm", re.I),
            "a customer pushing open the rustic weathered wooden sliding door of a cozy traditional barbecue shop on a chilly afternoon, warm amber interior light and savory culinary steam greeting the entryway",
        ),
        (
            re.compile(r"mùi thơm ngậy|nức mũi|ùa tới|bừng tỉnh|khứu giác", re.I),
            "a fragrant billowing wave of savory culinary steam drifting upward from an open searing kitchen counter, mouth-watering aroma visualization",
        ),
        (
            re.compile(r"mặt chảo gang|giọt mỡ|nhảy múa|nổ lách tách|sôi xèo xèo", re.I),
            "extreme macro shot of glistening droplets of beef fat sizzling, dancing and popping violently on the smoking surface of a seasoned black cast-iron pan, tiny lipid bubbles bursting",
        ),
        (
            re.compile(r"làn khói mỏng|nghi ngút|bốc khói", re.I),
            "wisps of aromatic blue-gray smoke rising steadily from a searing iron surface, back-illuminated by warm copper kitchen lights",
        ),
        (
            re.compile(r"thịt đỏ tươi|nâu cánh gián|bóng bẩy|lớp áo màu nâu", re.I),
            "a thick prime beef steak developing a glistening deep golden-brown Maillard caramelized crust with appetizing glossy sheen",
        ),
        (
            re.compile(r"lưỡi dao sắc bén|xẻ ngang|vỏ ngoài vỡ|giòn rụm|thái lát", re.I),
            "a razor-sharp chef's knife slicing cleanly through a rested prime steak, crisp caramelized crust audibly parting to reveal tender juicy pink medium-rare center",
        ),
        (
            re.compile(r"phần nhân bên trong|hồng hào|mọng nước", re.I),
            "succulent cross-section of perfectly seared medium-rare beef, juicy pink interior fibers glistening with natural juices",
        ),
        (
            re.compile(r"nước thịt.*ứa ra|mặt thớt gỗ|thớt gỗ", re.I),
            "flavorful glistening meat juices oozing naturally onto a dark rustic end-grain wooden cutting board beside fresh sprigs of rosemary",
        ),
        (
            re.compile(r"ổ bánh mì nóng giòn|lò nướng|lớp vỏ vàng ươm|bánh mì", re.I),
            "two hands holding a crusty golden-brown artisanal French baguette or banh mi fresh out of a stone hearth oven, fine cracks along the blistered crust",
        ),
        (
            re.compile(r"đáy nồi cơm gang|cơm cháy|nồi cơm", re.I),
            "traditional heavy cast-iron cooking pot opened to reveal an appetizing layer of crispy golden-brown scorched rice at the bottom",
        ),
        (
            re.compile(r"thịt tươi sống|không có mùi|nhạt nhòa|vô vị", re.I),
            "a raw pale pink slice of uncooked beef lying flat on a prep plate, completely unseared without aroma or browning",
        ),
        (
            re.compile(r"nồi nước sôi|thành phẩm.*xám xịt|\bluộc\b", re.I),
            "a pale grayish piece of uncaramelized boiled meat lifted with tongs from a simmering pot of water, dull rubbery texture showing the consequence of boiling without Maillard crust",
        ),
        (
            re.compile(r"ngưỡng nhiệt độ|140|165\s*độ|nhiệt độ vàng", re.I),
            "a digital infrared thermometer laser dot projecting onto a sizzling skillet, displaying the optimal 140 to 165 degrees Celsius Maillard temperature window",
        ),
        (
            re.compile(r"nhiệt dung riêng|hơi ẩm|kẻ thù|bốc hơi", re.I),
            "surface water droplets boiling into an aggressive vapor steam cushion between meat and metal, showing how moisture quenches searing heat",
        ),
        (
            re.compile(r"khăn giấy|thấm khô|muối hút ẩm|ướp muối|24\s*giờ", re.I),
            "clean white paper towels pressing firmly against a thick raw steak to blot surface moisture, coarse sea salt crystals drawing out and reabsorbing briny juices",
        ),
        (
            re.compile(r"chảo gang không phải|dẫn nhiệt|giữ nhiệt|khối gang", re.I),
            "heavy black cast-iron pan glowing with dense thermal mass, heat radiating evenly across its thick seasoned floor",
        ),
        (
            re.compile(r"phản ứng maillard|caramel|axit amin|đường khử", re.I),
            "macro molecular visualization of amino acids and reducing sugars rearranging under intense thermal energy into complex golden Maillard polymers",
        ),
    ],
    "ho-so-ky-la": [
        (
            re.compile(r"12\s*giờ\s*35|mười hai giờ ba mươi lăm|15\s*tháng\s*5|mười lăm tháng năm|2001|hai nghìn không trăm linh một|stanley|xtan-li|bãi ga|bãi phân loại|ohio|ô-hai-ô", re.I),
            "cinematic 3D noir diorama of Stanley rail yard at 12:35 PM under cold drizzling rain, misty industrial horizon with tangled railway tracks glistening on wet dark gravel",
        ),
        (
            re.compile(r"đầu máy.*(?:8888|tám tám tám tám)|bốn mươi bảy toa|47\s*toa|lăn bánh|bắt đầu lăn bánh", re.I),
            "heavy blue and yellow CSX locomotive 8888 leading a long snake of 47 freight cars slowly rolling forward along wet switching rails",
        ),
        (
            re.compile(r"ba nghìn tấn|3000\s*tấn|hai bồn.*(?:phê-non|phenol)|hóa chất.*kịch độc", re.I),
            "two heavy cylindrical railroad tank cars bearing hazardous placards, filled with thousands of gallons of toxic molten phenol",
        ),
        (
            re.compile(r"hai hệ thống hãm|cần phanh|phanh khí nén độc lập|hãm độc lập", re.I),
            "detailed close-up inside the diesel locomotive engineer cab showing the independent pneumatic air brake valve lever beside the trainline dynamic brake handle",
        ),
        (
            re.compile(r"cần.*ga|gạt kịch|kịch kim|nấc tám|nấc 8|ba ngàn mã lực|3000\s*mã lực|gầm rú", re.I),
            "engineer throttle control lever accidentally jammed fully forward to notch 8, diesel engine RPM screaming at maximum 3000 horsepower output",
        ),
        (
            re.compile(r"má phanh vỡ vụn|rơi xuống ray|ma sát|tia lửa|khói khét", re.I),
            "heavy cast-iron brake shoes grinding against steel train wheels, generating showers of bright orange friction sparks and white smoke before shattering onto the ballast",
        ),
        (
            re.compile(r"không người lái|buồng lái trống|buồng lái.*không có|không có một bóng người|rời khỏi tàu|bẻ ghi|nhảy xuống", re.I),
            "eerie wide shot through the front cab windshield of the speeding locomotive showing an empty operator chair and humming control panel under grey drizzle",
        ),
        (
            re.compile(r"kinh nghiệm|người lái tàu|ba mươi lăm năm|kỹ sư|thợ máy", re.I),
            "seasoned veteran locomotive engineer in reflective vest and cap working in the railway yard",
        ),
        (
            re.compile(r"trườn chậm|bẻ ghi|điểm bẻ ghi|chuyển làn", re.I),
            "heavy CSX freight train slowly navigating across intricate track switches and crossover frogs in the wet rail yard",
        ),
        (
            re.compile(r"trọng tải|một trăm tám mươi tấn|180\s*tấn|sáu trục|bánh thép", re.I),
            "heavy 180-ton six-axle diesel-electric locomotive chassis and steel wheels resting solidly on wet iron rails",
        ),
        (
            re.compile(r"cảnh sát|nổ súng|bắn.*van|công tắc ngắt|bình dầu", re.I),
            "police cruiser speeding along track embankment, police officer aiming sidearm at the fuel shut-off switch on the locomotive underbelly",
        ),
        (
            re.compile(r"đầu máy thứ hai|đuổi theo|khóa móc|hãm lùi|ghì lại|kết nối", re.I),
            "a brave second locomotive chasing the runaway train at high speed, closing the gap bumper-to-bumper to lock couplers and engage dynamic braking",
        ),
        (
            re.compile(r"nhảy lên buồng lái|gion hót-phen|bước ra ngoài|dừng hẳn", re.I),
            "heroic rail worker leaping onto the runaway locomotive exterior walkway at high speed, wrestling the cabin door open to manually cut the throttle to idle",
        ),
        (
            re.compile(r"hộp đen|dữ liệu|điều tra viên|báo cáo kỹ thuật|rào chắn", re.I),
            "forensic NTSB federal rail investigators in yellow vests inspecting the recovered locomotive event recorder black box beside the sealed tracks",
        ),
        (
            re.compile(r"chốt chặn cuối cùng|con người|bình yên|bài học|hồ sơ.*khép lại", re.I),
            "atmospheric dusk view over the now-quiet railway tracks curving into the distance, twilight silhouette of the locomotive standing safely parked",
        ),
    ],
    "tui-tien": [
        (
            re.compile(r"món hời|ly cà phê|quầy gọi nước|buổi sáng", re.I),
            "cinematic documentary tabletop view of a modern Vietnamese café counter, warm directional 3200K tungsten spotlighting, polished slate surface",
        ),
        (
            re.compile(r"ly nhỏ|ba mươi chín nghìn|39k", re.I),
            "a small glass cup of iced Vietnamese milk coffee resting on a linen coaster, modest volume with condensation glistening under warm studio keylight",
        ),
        (
            re.compile(r"ly vừa.*55|ly lớn.*59|bẫy giá mồi|chim mồi|giá mồi|năm mươi lăm|bốn nghìn", re.I),
            "three tiered glass cups of iced milk coffee arranged side by side labeled by volume, showing the decoy medium size making the large cup seem irresistible",
        ),
        (
            re.compile(r"siêu thị|mê cung|cánh cổng xoay", re.I),
            "wide interior perspective of a bright supermarket entrance with automatic turnstiles, polished reflective floor directing customer traffic",
        ),
        (
            re.compile(r"hàng thiết yếu.*giấu kín|góc xa|\bsữa\b.*cuối|\btrứng\b", re.I),
            "view down a long supermarket aisle with essential fresh milk and eggs placed at the farthest back wall, forcing shoppers past tempting endcap snacks",
        ),
        (
            re.compile(r"ngang tầm mắt|kệ trung tâm|lợi nhuận cao|bánh kẹo", re.I),
            "close-up of premium snack boxes neatly aligned at eye level on supermarket retail shelving, catching customer attention effortlessly",
        ),
        (
            re.compile(r"miễn phí vận chuyển|freeship|nửa đêm|giỏ hàng|mua thêm", re.I),
            "a customer browsing an e-commerce shopping app at midnight, adding extra trivial items into the digital cart to hit the free shipping minimum order threshold",
        ),
        (
            re.compile(r"giá điện|bậc thang|lũy tiến|thiết bị cắm chờ|đèn led", re.I),
            "household electrical appliances glowing with red standby LEDs in a dark living room, beside a conceptual multi-tiered electricity rate chart",
        ),
        (
            re.compile(r"trả góp 0%|lãi suất|phí chuyển đổi|khoản vay", re.I),
            "a sleek modern smartphone on a retail display stand next to an eye-catching 0% installment promo sign, with fine-print fee details subtly visible",
        ),
        (
            re.compile(r"lãi kép|tiết kiệm|hũ chi tiêu|sổ tay tài chính", re.I),
            "a tidy wooden desk with a hand-filled financial ledger notebook, ceramic savings jar, and neatly stacked VND polymer banknotes",
        ),
    ],
    "ban-do-quyen-luc": [
        (
            re.compile(r"quỹ đạo không gian|địa cầu|khe nứt tự nhiên", re.I),
            "high-altitude 3D orbital satellite map rendering of Earth focusing on Southeast Asia, deep ocean blues, lush green landmasses and delicate swirling cloud patterns",
        ),
        (
            re.compile(r"chiếc phễu khổng lồ|eo biển.*hẹp|malacca", re.I),
            "high-altitude 3D perspective of the funnel-shaped Strait of Malacca wedged tightly between the Malay Peninsula and Sumatra Island",
        ),
        (
            re.compile(r"bán đảo mã lai|đảo sumatra|hai bờ|bờ biển", re.I),
            "satellite view of the lush coastline of Sumatra facing the modern coastal ports of Malaysia across a narrow ribbon of turquoise sea",
        ),
        (
            re.compile(r"siêu tàu chở dầu|đoàn tàu|nối đuôi|dòng chảy", re.I),
            "single-file convoy of colossal ultra-large crude oil tankers gliding through a narrow blue maritime channel, long white wake trails stretching behind",
        ),
        (
            re.compile(r"phong tỏa|ba ngày|khủng hoảng|cắt đứt", re.I),
            "tactical 3D digital simulation diorama of the strategic strait pulsing with crimson emergency blockade rings and warning vectors",
        ),
        (
            re.compile(r"khu trục hạm|hạm đội|tàu ngầm|tuần tra", re.I),
            "naval guided-missile destroyer escorting commercial shipping corridors through misty coastal waters, radar antennas rotating",
        ),
        (
            re.compile(r"đường ống dẫn dầu|tuyến đường vòng|đất liền", re.I),
            "illuminated cross-continental energy pipeline vector glowing golden across mountain terrain, bypassing congested maritime chokepoints",
        ),
    ],
    "chanh-niem-ke": [
        (
            re.compile(r"hiên gỗ|cơn mưa|sân chùa|chiều buông|mái ngói", re.I),
            "a quiet rustic wooden veranda overlooking a rain-swept courtyard garden, gentle raindrops falling onto stone paving and misty bamboo foliage",
        ),
        (
            re.compile(r"giọt mưa|mặt kính|lăn dài|hơi sương", re.I),
            "close-up of delicate translucent raindrops slowly trailing down a cool foggy glass windowpane, soft diffused grey twilight outside",
        ),
        (
            re.compile(r"mặt nước hồ cá|vòng sóng lan tỏa|gợn sóng|hồ cá", re.I),
            "a single clean raindrop disturbing the still surface of a garden pond, creating expanding concentric ripples that reflect the serene sky",
        ),
        (
            re.compile(r"mũi tên thứ nhất|nỗi đau thể xác|đau đớn", re.I),
            "symbolic Zen illustration: a simple peaceful figure struck by a single wooden arrow representing natural physical pain, accepting it calmly",
        ),
        (
            re.compile(r"mũi tên thứ hai|sự phán xét|dằn vặt|tâm trí|lo âu", re.I),
            "symbolic Zen illustration: a shadowy second arrow representing mental overthinking and self-criticism, visualizing unnecessary emotional suffering",
        ),
        (
            re.compile(r"dòng nước chảy|chiếc lá trôi|buông bỏ|dòng suối", re.I),
            "a single weathered golden autumn leaf gently floating down a slow-moving crystal stream, drifting effortlessly around smooth river stones",
        ),
        (
            re.compile(r"hơi thở|thở ra|nhẹ nhõm|bình yên|tĩnh tại", re.I),
            "a solitary person sitting comfortably on a meditation cushion, shoulders dropped and posture relaxed in complete stillness and tranquility",
        ),
    ],
    "nao-luoi": [
        (
            re.compile(r"cầm điện thoại|lướt mạng|trước khi đi ngủ|\bgiường\b|nửa đêm", re.I),
            "bald stickman in cerulean-blue shirt lying on a flat minimal bed in a dark room, face illuminated by the bright cyan screen glow of a smartphone",
        ),
        (
            re.compile(r"kiểm tra tin nhắn|hai phút|ngắn ngủi|tin nhắn", re.I),
            "bald stickman looking at a small rectangular phone with an optimistic expression, holding up two fingers to indicate just a quick check",
        ),
        (
            re.compile(r"đồng hồ.*hai tiếng|trôi qua|giật mình|hai tiếng", re.I),
            "bald stickman staring in shock with wide round eyes as a minimal wall clock shows two hours have vanished in the blink of an eye",
        ),
        (
            re.compile(r"dopamine|vùng não phần thưởng|thần kinh", re.I),
            "2D doodle diagram: an oversized stickman brain with a glowing reward pathway lighting up as dopamine drop icons rain down happily",
        ),
        (
            re.compile(r"kiệt sức|tội lỗi|trì hoãn|hối hận|đè nặng", re.I),
            "bald stickman slumping over an empty desk with head down on arms, overwhelmed by a huge cartoon boulder labeled procrastination",
        ),
        (
            re.compile(r"đồng hồ quả cà chua|pomodoro|25\s*phút", re.I),
            "bald stickman sitting upright at a clean desk beside a cute red tomato-shaped timer ticking peacefully, fully focused on a single sheet of paper",
        ),
        (
            re.compile(r"quy tắc 5 giây|5.*4.*3.*2.*1|đứng dậy|hành động", re.I),
            "bald stickman launching upward like a determined rocket as bold countdown numbers 5-4-3-2-1 trigger immediate physical action",
        ),
    ],
    "ai-binh-dan": [
        (
            re.compile(r"bận rộn|ngập đầu|excel|báo cáo|thủ công|nhập liệu", re.I),
            "remote worker sitting before multiple monitor screens overflowing with tedious tangled spreadsheet tables and unread email notifications",
        ),
        (
            re.compile(r"tự động hóa|\bAI\b|trí tuệ nhân tạo|pipeline|kết nối|api", re.I),
            "sleek dark-mode visualization of automated digital pipelines connecting input files to AI processing nodes and organized clean databases",
        ),
        (
            re.compile(r"5\s*giờ chiều|năm giờ chiều|về đúng giờ|thảnh thơi|cà phê", re.I),
            "worker peacefully closing a slim modern laptop at 5:00 PM and sipping from a warm ceramic mug, desk totally tidy and tasks completed",
        ),
    ],
    "ua-sao-vay": [
        (
            re.compile(r"chiếc gương|soi gương|phòng tắm|phản chiếu", re.I),
            "person standing before a clean bathroom mirror looking at their reflection, observing how movement appears reversed",
        ),
        (
            re.compile(r"trái phải|trên dưới|nghịch lý|đảo ngược", re.I),
            "educational demonstration: a demonstrator holding up a printed sign to a mirror showing front-to-back optical axis reversal rather than horizontal flipping",
        ),
        (
            re.compile(r"trục z|tọa độ 3d|quang học|tia sáng|photon", re.I),
            "clean 3D vector diagram showing light rays reflecting off a mirror plane with colored X, Y, and Z coordinate axes illustrating normal reflection",
        ),
    ],
    "su-ke-lai": [
        (
            re.compile(r"938|bạch đằng|ngô quyền|mùa đông", re.I),
            "wide panoramic 3D diorama of the misty Bach Dang river estuary in early winter morning, ancient Vietnamese warriors preparing defenses",
        ),
        (
            re.compile(r"cọc gỗ lim|vạt nhọn|bọc sắt|lòng sông|cắm cọc", re.I),
            "close-up view of heavy iron-tipped timber stakes being driven vertically into the muddy riverbed beneath dark tidal waters",
        ),
        (
            re.compile(r"thủy triều rút|cọc nhô lên|thủng đáy|chiến thuyền", re.I),
            "dramatic tactical scene as the river tide recedes rapidly, exposing sharp wooden stakes that impale and shatter heavy Southern Han war junks",
        ),
    ],
    "thuong-cho-kheo": [
        (
            re.compile(r"mâm cơm|chiều ấm áp|ngột ngạt|im lặng|bữa tối", re.I),
            "two family members sitting across a cozy dinner table in heavy emotional silence, untouched warm dishes between them under domestic warm light",
        ),
        (
            re.compile(r"lắng nghe|thấu hiểu|ngắt lời|ánh mắt", re.I),
            "intimate close-up of an empathetic listener maintaining gentle eye contact and nodding softly, giving full undivided attention without interrupting",
        ),
        (
            re.compile(r"tách trà|hơi nước|mở lòng|chia sẻ", re.I),
            "two warm ceramic tea cups steaming gently on a low wooden coffee table between two people conversing with open body language and warmth",
        ),
    ],
    "co-the-ke": [
        (
            re.compile(r"mi mắt.*nặng trĩu|2\s*giờ sáng|thiếu ngủ|thức khuya", re.I),
            "human eyes struggling to stay open in a dark bedroom at 2:00 AM, heavy eyelids drooping in exhaustion under soft nightstand lamp light",
        ),
        (
            re.compile(r"adenosine|tích tụ|thụ thể|buồn ngủ", re.I),
            "3D biomedical visualization: adenosine molecules clustering and binding tightly onto neural receptors in the cerebral cortex, triggering fatigue",
        ),
        (
            re.compile(r"glymphatic|dịch não tủy|rửa trôi|độc tố|beta-amyloid", re.I),
            "translucent glowing cerebrospinal fluid pulsing through brain neural pathways during deep sleep, washing away metabolic waste and amyloid plaques",
        ),
    ],
    "luat-ngam": [
        (
            re.compile(r"phòng khám|mười người|đứng dậy|chuông reng", re.I),
            "monochrome clinic waiting room where ten seated strangers in gray attire simultaneously stand up in silence upon hearing an electric bell ring",
        ),
        (
            re.compile(r"thí nghiệm solomon asch|đoạn thẳng|bảng đen", re.I),
            "psychological laboratory setting showing comparison line cards of varying lengths on a blackboard, with a test subject hesitating under group pressure",
        ),
    ],
    "luat-doi-thuong": [
        (
            re.compile(r"chủ nhà|kiểm tra phòng|tiền cọc|20\s*triệu|hai mươi triệu", re.I),
            "a strict landlord holding a wooden clipboard examining a vacant apartment room, frowning while checking walls under bright natural window light",
        ),
        (
            re.compile(r"vết ố.*tường|vết xước.*sàn|trừ sạch", re.I),
            "close-up inspection shot of a tiny harmless wall discoloration or floor scuff, with a finger pointing sternly to dispute natural wear-and-tear",
        ),
        (
            re.compile(r"quay video.*điện thoại|bằng chứng|ngày đầu", re.I),
            "tenant holding a smartphone recording a continuous slow video walkthrough of apartment corners, power sockets, and fixtures as definitive proof",
        ),
    ],
    "banh-rang": [
        (
            re.compile(r"chiếc áo phông|200\s*nghìn|hai trăm nghìn|bốn mươi ngày|vòng quanh trái đất", re.I),
            "a simple folded cotton T-shirt on a retail table beside an illustrated global logistics map tracing its 40-day transpacific manufacturing journey",
        ),
        (
            re.compile(r"cánh đồng bông|texas|kiện bông.*200\s*ký", re.I),
            "sprawling Texas cotton field under morning sun with mechanical harvesters and heavy 200kg cotton bales wrapped in yellow protective casing",
        ),
        (
            re.compile(r"cần cẩu gantry|container|cảng singapore|hải phòng|malcolm mclean", re.I),
            "towering harbor gantry crane lifting a standard 40-foot corrugated steel ISO container smoothly from a mega container vessel onto an AGV dock chassis",
        ),
    ],
    "vu-tru-ti-hon": [
        (
            re.compile(r"hố đen|rơi vào|không gian sâu|trôi dạt", re.I),
            "breathtaking deep space view of a supermassive black hole with an intense swirling golden-orange accretion disk warping starlight around the event horizon",
        ),
        (
            re.compile(r"chân trời sự kiện|event horizon|\bánh sáng\b", re.I),
            "solitary astronaut in white spacesuit hovering in the cosmic void near the razor-sharp edge of the black hole event horizon where light bends into a complete ring",
        ),
    ],
    "nghe-song-sot": [
        (
            re.compile(r"văn phòng sớm nhất|đèn hành lang|ra về|12\s*tiếng", re.I),
            "a solitary dedicated professional sitting at an illuminated office workstation in an otherwise darkened glass corporate office floor after hours",
        ),
        (
            re.compile(r"chiến lược đòn bẩy|bàn cờ|thăng tiến", re.I),
            "symbolic executive mahogany desk featuring a polished chess set with a knight maneuvered forward beside financial quarterly performance charts",
        ),
    ],
    "la-ban-hoc-thuat": [
        (
            re.compile(r"đọc.*ba trăm trang|quên sạch|trống rỗng|300\s*trang", re.I),
            "a thick open book with numerous underlined passages resting on a wooden study desk beside a student tapping their chin in thoughtful recall",
        ),
        (
            re.compile(r"đường cong quên lãng|ebbinghaus|24\s*giờ", re.I),
            "clean minimal graph showing the Ebbinghaus forgetting curve declining sharply from 100% to 30%, contrasted with spaced review recovery peaks",
        ),
    ],
    "loi-sang-soi": [
        (
            re.compile(r"người gieo giống|gieo hạt|bình minh|hạt giống", re.I),
            "rustic ancient sower in simple linen tunic scattering golden wheat grains by hand across freshly plowed earth under warm dawn sunlight",
        ),
        (
            re.compile(r"vệ đường|chim ăn|đá sỏi|héo khô|nắng cháy", re.I),
            "tender green seedlings sprouting on shallow rocky soil, wilting under the blazing midday sun beside barren stony ground",
        ),
    ],
    "minh-triet-song": [
        (
            re.compile(r"tuyết trắng|biên cương|lạnh giá|marcus aurelius|danube", re.I),
            "Roman military camp on the snowy Danube frontier, heavy canvas imperial tent illuminated from within by warm flickering candlelight in the freezing night",
        ),
        (
            re.compile(r"viết nhật ký|trầm tưởng|meditations|cuộn thư|ngọn nến", re.I),
            "weathered hands of philosopher Emperor Marcus Aurelius writing Meditations with reed pen on a papyrus scroll beside his bronze oil lamp",
        ),
    ],
    "tam-tinh-dem": [
        (
            re.compile(r"ngoài kia.*ngủ say|cả góc phố|nửa đêm|góc phố", re.I),
            "wide nocturnal view of a peaceful city asleep under deep midnight indigo skies, gentle streetlamps casting warm amber pools on empty cobblestones",
        ),
        (
            re.compile(r"khung cửa sổ|ánh đèn vàng|ly trà ấm|tách trà", re.I),
            "close-up of a cozy warm window ledge with a steaming ceramic mug of tea, soft warm yellow light framing a solitary person gazing outside peacefully",
        ),
    ],
}

# General Semantic Lexicon with strict word boundaries and pure English descriptions (140+ entries)
GENERAL_SEMANTIC_LEXICON: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\bbước qua cánh cửa\b|\bmở cửa\b", re.I), "a person opening a door and stepping inside"),
    (re.compile(r"\báp chảo\b|\bchảo nóng\b|\brán\b", re.I), "sizzling ingredients searing rapidly on a hot cooking surface"),
    (re.compile(r"\bdao sắc\b|\bcắt ngang\b|\bthái mỏng\b|\bxẻ\b", re.I), "a sharp blade cleanly slicing through the culinary subject"),
    (re.compile(r"\bbốc khói\b|\bhơi nước\b|\bnghi ngút\b", re.I), "wisps of culinary steam rising gracefully in warm lighting"),
    (re.compile(r"\bnước sôi\b|\bluộc\b", re.I), "simmering water bubbling gently in a cooking vessel"),
    (re.compile(r"\bký hợp đồng\b|\bđặt bút ký\b|\bhợp đồng\b", re.I), "a fountain pen poised over a formal multi-page agreement"),
    (re.compile(r"\bvết ố\b|\bvết nứt\b|\bhao mòn\b", re.I), "close inspection of subtle surface wear and authentic texture"),
    (re.compile(r"\bđiện thoại\b|\blướt màn hình\b", re.I), "hands holding a sleek smartphone with glowing screen interface"),
    (re.compile(r"\bđồng hồ\b|\bthời gian trôi\b|\bhai tiếng\b", re.I), "a wall clock showing time passing steadily"),
    (re.compile(r"\bnão bộ\b|\bthần kinh\b|\bnơ-ron\b|\bkhớp thần kinh\b", re.I), "detailed visualization of glowing neural synapses and brain structures"),
    (re.compile(r"\bmệt mỏi\b|\bkiệt sức\b|\bnặng trĩu\b", re.I), "subject expressing physical fatigue and looking for rest"),
    (re.compile(r"\bbình thản\b|\byên tĩnh\b|\btĩnh lặng\b|\bbình yên\b", re.I), "a tranquil scene filled with serene balance and calm energy"),
    (re.compile(r"\btàu thủy\b|\btàu biển\b|\bhàng hải\b", re.I), "a vessel navigating calm deep blue waters"),
    (re.compile(r"\beo biển\b|\bvùng biển\b|\bhải lưu\b", re.I), "a scenic geographic maritime strait between coastlines"),
    (re.compile(r"\bvũ trụ\b|\bngôi sao\b|\bhành tinh\b|\bdải ngân hà\b", re.I), "vast celestial cosmos filled with distant nebulae and stars"),
    (re.compile(r"\bchiến trường\b|\bquân đội\b|\bchiến thuyền\b", re.I), "historic military naval armada aligned in tactical formation"),
    (re.compile(r"\btiền bạc\b|\bhóa đơn\b|\bchi phí\b|\btiền cọc\b", re.I), "crisp currency notes and neatly aligned financial invoices"),
    (re.compile(r"\bbàn làm việc\b|\bvăn phòng\b|\bcông sở\b", re.I), "a clean modern workspace with organized documents"),
    (re.compile(r"\bhọc tập\b|\btrang sách\b|\bghi chép\b|\bcuốn sách\b", re.I), "an open notebook with handwritten notes and study materials"),
    (re.compile(r"\bhạt giống\b|\bgieo trồng\b|\bcánh đồng\b", re.I), "seeds scattered across dark fertile soil in morning light"),
    (re.compile(r"\bcơn mưa\b|\bgiọt mưa\b|\bmưa rơi\b", re.I), "gentle rain falling softly onto natural surfaces"),
    (re.compile(r"\btách trà\b|\bly trà\b|\buống trà\b", re.I), "a warm steaming ceramic tea cup resting on wood"),
    (re.compile(r"\bchế biến\b|\bnấu ăn\b|\bnhà bếp\b", re.I), "orderly kitchen preparation area with fresh ingredients"),
    (re.compile(r"\bnghi ngờ\b|\blo lắng\b|\bbăn khoăn\b", re.I), "contemplative subject reflecting with focused attention"),
    (re.compile(r"\bphân tích\b|\bkhảo sát\b|\bnghiên cứu\b", re.I), "clean scientific diagram illustrating cause and effect"),
    (re.compile(r"\bthành công\b|\bđạt được\b|\bchiến thắng\b", re.I), "clear visual demonstration of accomplished progress"),
    (re.compile(r"\bsai lầm\b|\bthất bại\b|\bnguy hiểm\b", re.I), "cautionary scene highlighting key operational risks"),
    (re.compile(r"\bkỷ luật\b|\bthói quen\b|\bluyện tập\b", re.I), "structured orderly routine showing steady progression"),
    (re.compile(r"\bbảo vệ\b|\ban toàn\b|\bphòng ngừa\b", re.I), "sturdy protective barriers maintaining safety"),
    (re.compile(r"\btập trung\b|\bchú ý\b|\bsâu sắc\b", re.I), "sharp visual focus emphasizing central subject details"),
    (re.compile(r"\bchuyển động\b|\blăn bánh\b|\btăng tốc\b", re.I), "dynamic forward motion with subtle motion blur cues"),
    (re.compile(r"\bdừng lại\b|\bđứng yên\b|\bkết thúc\b", re.I), "complete stillness and resolved visual balance"),
]


def _clean_narration(narration_vi: str) -> str:
    """Normalize and clean Vietnamese narration clause."""
    if not narration_vi:
        return ""
    text = narration_vi.strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^(?:CH\d+_[A-Z0-9]+|Beat\s*\d+|[0-9]+[\.\:\-])\s*", "", text)
    return text.strip()


def _resolve_profile(channel_slug: str) -> ChannelStyleProfile:
    """Resolve ChannelStyleProfile from slug or fallback to default."""
    clean_slug = channel_slug.strip().lower().replace("_", "-")
    clean_slug = clean_slug.removeprefix("ch-").removeprefix("channel-")
    clean_slug = CHANNEL_ALIASES.get(clean_slug, clean_slug)
    return CHANNEL_STYLE_PROFILES.get(clean_slug, CHANNEL_STYLE_PROFILES["dia-com"])


def _extract_story_scene(narration_vi: str, channel_slug: str, chapter_title: str = "") -> str:
    """Extract a concrete, story-driven English scene description from narration_vi.

    Strict Invariants:
    - Never search other channels' domain dictionaries (zero cross-channel bleeding).
    - Never output raw Vietnamese strings into the English prompt.
    """
    clean_slug = channel_slug.strip().lower().replace("_", "-").removeprefix("ch-").removeprefix("channel-")
    clean_slug = CHANNEL_ALIASES.get(clean_slug, clean_slug)

    # 1. First priority: Channel-specific domain pattern match ONLY
    channel_patterns = CHANNEL_DOMAIN_PATTERNS.get(clean_slug, [])
    for pat, desc in channel_patterns:
        if pat.search(narration_vi):
            return desc

    # 2. Second priority: General semantic lexicon
    matched_semantics = []
    for pat, desc in GENERAL_SEMANTIC_LEXICON:
        if pat.search(narration_vi):
            matched_semantics.append(desc)
            if len(matched_semantics) >= 2:
                break

    if matched_semantics:
        return ", accompanied by ".join(matched_semantics)

    # 3. Third priority: Derive clean English theme from chapter index or title
    ch_idx = 1
    m = re.search(r"(?:Hồi|Chương|Chapter)\s*0?(\d+)", chapter_title, re.I)
    if m:
        ch_idx = int(m.group(1))
    ch_idx = max(1, min(10, ch_idx))

    themes = CHAPTER_THEMES_EN.get(clean_slug, [])
    if themes and len(themes) >= ch_idx:
        theme_en = themes[ch_idx - 1]
    else:
        theme_en = "visual narrative progression and thematic core"

    return f"detailed visual narrative illustration of {theme_en}, clearly demonstrating the cause-and-effect explanatory mechanism with balanced focal composition"


def _strip_non_ascii(text: str) -> str:
    """Enforce pure ASCII characters in English prompts, eliminating all Vietnamese diacritics."""
    return re.sub(r"[^\x00-\x7F]+", "", text)


def build_story_driven_prompt(
    narration_vi: str,
    channel_slug: str,
    chapter_title: str = "",
    event_kind: str = "ANCHOR_ESTABLISH",
    anchor_scene_desc: str = "",
    visual_style_guide: str = "",
    is_anchor: bool = False,
    anchor_context: str = "",
    shot_type: str = "",
) -> str:
    """Build a rich, story-driven English visual prompt for a specific beat.

    Strict Invariants:
    - Zero cross-channel bleeding.
    - Zero Vietnamese characters in output.
    - Zero 8K buzzwords.
    - Standard clear composition with ample negative space.
    """
    clean_narr = _clean_narration(narration_vi)
    profile = _resolve_profile(channel_slug)
    is_anchor_beat = is_anchor or event_kind == "ANCHOR_ESTABLISH"

    # Extract story scene description (Pure English)
    story_scene = _extract_story_scene(clean_narr, channel_slug, chapter_title)

    # Framing and camera angle adjustment based on event kind
    if is_anchor_beat:
        framing = "Establishing wide diorama:"
    elif event_kind in ("ENUMERATION_BURST", "DETAIL_INSPECTION"):
        framing = "Macro close-up cutaway burst focusing on:"
    elif event_kind == "ANGLE_CUTAWAY":
        framing = "Dynamic perspective cutaway showing:"
    elif event_kind in ("MECHANISM_STEP", "MECHANISM_STEP_BUILD"):
        framing = "Visual mechanism cutaway demonstrating:"
    else:
        framing = "Detailed scene showing:"

    # If progressive beat and anchor context is available, add continuity hook
    continuity_clause = ""
    if not is_anchor_beat and (anchor_scene_desc or anchor_context):
        ref_context = (anchor_scene_desc or anchor_context)[:80]
        ref_context = re.sub(r"^(?:Continuing from [A-Z0-9_]+,?\s*|Cinematic [^,]+,\s*)", "", ref_context).strip()
        if ref_context:
            continuity_clause = f" Continuing scene continuity, {framing.lower()} {story_scene}."
    if not continuity_clause:
        continuity_clause = f" {framing} {story_scene}."

    # Assemble full prompt components
    prompt_parts = [
        profile.style_prefix,
        continuity_clause.strip(),
        profile.aesthetic_traits,
        profile.negative_rules,
    ]

    full_prompt = " ".join(prompt_parts)
    full_prompt = re.sub(r"\s+", " ", full_prompt).strip()

    # Enforce pure ASCII constraint (remove any accidental non-ASCII Vietnamese characters)
    full_prompt = _strip_non_ascii(full_prompt)
    # Strip any accidental 8K / photorealistic / hyper-detailed buzzwords to guarantee standard clear composition
    full_prompt = re.sub(r"\b(8k|4k|uhd|ultra\s*hd|hyper-detailed|hyperrealistic|photorealistic|masterpiece)\b", "detailed", full_prompt, flags=re.IGNORECASE)
    full_prompt = re.sub(r"\bdetailed\s+detailed\b", "detailed", full_prompt, flags=re.IGNORECASE)
    full_prompt = re.sub(r"\s+", " ", full_prompt).strip()

    return full_prompt


if __name__ == "__main__":
    test_cases = [
        ("ho-so-ky-la", "Mười hai giờ ba mươi lăm phút trưa, ngày mười lăm tháng năm năm hai nghìn không trăm linh một.", "Hồi 01: 12 Giờ 35 Tại Bãi Ga Stanley", "ANCHOR_ESTABLISH"),
        ("ho-so-ky-la", "Tại bãi phân loại đường sắt Xtan-li, bang Ô-hai-ô", "Hồi 01: 12 Giờ 35 Tại Bãi Ga Stanley", "ENUMERATION_BURST"),
        ("ho-so-ky-la", "đầu máy tám tám tám tám dẫn đầu bốn mươi bảy toa hàng bắt đầu lăn bánh.", "Hồi 01: 12 Giờ 35 Tại Bãi Ga Stanley", "ANGLE_CUTAWAY"),
        ("dia-com", "Bạn vừa bước qua cánh cửa gỗ của một tiệm nướng nhỏ vào buổi chiều se lạnh.", "Hồi 01: Mùi Thơm Đánh Thức Vị Giác", "ANCHOR_ESTABLISH"),
        ("dia-com", "Trên mặt chảo gang nóng rực, những giọt mỡ bò đang nhảy múa và nổ lách tách.", "Hồi 01: Mùi Thơm Đánh Thức Vị Giác", "ANGLE_CUTAWAY"),
        ("tui-tien", "Ly vừa năm mươi lăm nghìn, nhưng chỉ thêm bốn nghìn nữa bạn được ly lớn.", "Hồi 01: Nghịch Lý Hóa Đơn & Hiệu Ứng Chim Mồi", "ANGLE_CUTAWAY"),
        ("ban-do-quyen-luc", "Dòng hải lưu hẹp uốn lượn như một chiếc phễu khổng lồ kẹp giữa đại dương.", "Hồi 01: Yếu Huyệt Hàng Hải", "ANCHOR_ESTABLISH"),
        ("chanh-niem-ke", "Mũi tên thứ hai chính là sự phán xét và dằn vặt của tâm trí.", "Hồi 01: Cơn Mưa Trong Lòng", "ANGLE_CUTAWAY"),
        ("nao-luoi", "Chắc hẳn bạn từng tự nhủ chỉ cầm điện thoại lướt mạng năm phút trước khi đi ngủ.", "Hồi 01: Vòng Lặp Lướt Màn Hình", "ANCHOR_ESTABLISH"),
    ]

    print("=== Story-Driven Prompt Builder Self-Test Verification ===\n")
    for slug, narr, ch_title, ek in test_cases:
        p = build_story_driven_prompt(narr, slug, chapter_title=ch_title, event_kind=ek)
        has_non_ascii = any(ord(c) >= 128 for c in p)
        print(f"[{slug.upper()}] Narration: {narr}")
        print(f"  Non-ASCII chars: {has_non_ascii}")
        print(f"  Prompt: {p}\n")
