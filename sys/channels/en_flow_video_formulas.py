"""SSOT Flow Video Frame-Control, Motion Physics & Viewer Retention Formulas for All 18 English Channels.

Synthesized from multi-source practitioner workflows (Google Flow Scenebuilder, Ingredients/Reference
Conditioning, First-to-Last Frame Interpolation, Boundary-Frame Extend), reverse-engineered Google
First-Party Applets (`Style Writer`, `Shot Explorer`, `Story Sketch`, `Transition Machine`), and
empirical frame-by-frame competitor documentary analysis.
"""

from __future__ import annotations

from typing import Any, Dict

# ==============================================================================
# 1. THE 3 GOLDEN GOOGLE FLOW FRAME-CONTROL MODES (Anti-Morphing Law)
# ==============================================================================
FLOW_FRAME_CONTROL_MODES: Dict[str, Dict[str, Any]] = {
    "reference_start_end": {
        "mode_id": "reference_start_end",
        "rpc_id": "nprQif",
        "description": (
            "Mode 1 — Reference-Conditioned Start-End Interpolation (`START_END_FRAMES`). "
            "Frame B MUST be generated with `reference_media_ids=[frame_A_media_id]` via `ogiZ0b` "
            "(`Story Sketch` / `Shot Explorer` wrapper) so Frame A and Frame B share 100% locked "
            "geometry, lighting, and subject anatomy before `nprQif` interpolates motion."
        ),
        "allowed_when": "Same spatial world, progressive physical state change, or continuous camera orbit/dolly.",
        "trim_first_frame_on_join": False,
    },
    "boundary_extend": {
        "mode_id": "boundary_extend",
        "rpc_id": "maseQ+eb1hJf/nprQif",
        "description": (
            "Mode 2 — Boundary-Frame Daisy-Chain Extend. Extract final non-corrupted frame of Clip K "
            "(`ffmpeg -y -sseof -0.1 -i clip_K.mp4 -update 1 -q:v 1 last_frame.png`), upload via `maseQ` "
            "(0 credits), and feed as `first_frame_media_id` of Clip K+1 with `trim=start_frame=1` at stitch."
        ),
        "allowed_when": "Extending a single unbroken continuous take beyond 6s-8s with mathematically 0-pixel seam jump.",
        "trim_first_frame_on_join": True,
    },
    "single_frame_physics": {
        "mode_id": "single_frame_physics",
        "rpc_id": "eb1hJf",
        "description": (
            "Mode 3 — Single-Frame Physics Motion (`START_FRAME`) + Breath-Pause Editorial Transition. "
            "Used whenever shifting to a new conceptual metaphor, macro cutaway, or spatial location so "
            "`nprQif` NEVER morphs or melts unrelated compositions together."
        ),
        "allowed_when": "Scene/location jump, scale shift (orbital to microscopic), or rhetorical pivot on breath pause.",
        "trim_first_frame_on_join": False,
    },
}

# ==============================================================================
# 2. RETENTION & SHOT-CHAIN ARCHITECTURE (30s 9:16 Demo & 60s 16:9 Demo)
# ==============================================================================
RETENTION_SHOT_BLUEPRINTS: Dict[str, Dict[str, Any]] = {
    "short_9x16_demo": {
        "target_duration_range_sec": (27.0, 36.0),
        "recommended_shot_count": (6, 8),
        "avg_shot_duration_sec": 4.2,
        "first_2_5s_hook_rule": (
            "Zero dead air at t=0.0s: Frame 0 begins mid-motion on a counter-intuitive physical anomaly "
            "with stressed vocal syllable landing within 0.15s and 1-word Red/Yellow kinetic caption."
        ),
        "stages": [
            {"stage": "S1_kinetic_shock_hook", "window_sec": "0.0-4.2", "chain_mode": "reference_start_end"},
            {"stage": "S2_expectation_collapse", "window_sec": "4.2-8.5", "chain_mode": "boundary_extend"},
            {"stage": "S3_rhetorical_pivot", "window_sec": "8.5-12.8", "chain_mode": "single_frame_physics"},
            {"stage": "S4_micro_mechanism_reveal", "window_sec": "12.8-17.5", "chain_mode": "reference_start_end"},
            {"stage": "S5_systemic_escalation", "window_sec": "17.5-22.2", "chain_mode": "boundary_extend"},
            {"stage": "S6_irreversible_climax", "window_sec": "22.2-26.8", "chain_mode": "single_frame_physics"},
            {"stage": "S7_loop_closure_takeaway", "window_sec": "26.8-31.5", "chain_mode": "single_frame_physics"},
        ],
    },
    "long_16x9_demo": {
        "target_duration_range_sec": (54.0, 72.0),
        "recommended_shot_count": (10, 13),
        "avg_shot_duration_sec": 5.4,
        "accordion_pacing_rule": (
            "Act 1 Hook & High Stakes (0-18s, brisk 4.2-5.0s shots) -> "
            "Act 2 Deep Mechanism Escalation (18-46s, deliberate 5.2-6.2s shots with reference-locked pairs) -> "
            "Act 3 Mind-Expanding Resolution (46-62s+, sweeping pullback & contemplative hold)."
        ),
        "acts": [
            {"act": "Act1_Hook_And_Stakes", "shots": ["L01", "L02", "L03"]},
            {"act": "Act2_Mechanism_Escalation", "shots": ["L04", "L05", "L06", "L07", "L08"]},
            {"act": "Act3_Universal_Resolution", "shots": ["L09", "L10", "L11"]},
        ],
    },
}

UNIVERSAL_STABILITY_GUARDRAILS = (
    "locked physical geometry, stable architectural and material textures, consistent lighting direction, "
    "zero morphing, zero melting, strictly zero text, zero letters, zero numbers, zero chalkboards, "
    "zero watermarks, silent visual storytelling, no talking, no lip movement"
)

# ==============================================================================
# 3. ALL 18 ENGLISH CHANNELS — SPECIALIZED FLOW VIDEO PHYSICS & CONTINUITY SSOT (V3.1)
#    Pure topic-agnostic material physics, lens grammar, and lighting DNA aligned 100%
#    with user-approved `sys/channels/en_rebuilt_style_specs/<slug>/<slug>_rebuilt_spec.json`.
#    Strictly ZERO hardcoded single-episode props or text-bearing chalkboards.
# ==============================================================================
EN_FLOW_VIDEO_FORMULAS: Dict[str, Dict[str, Any]] = {
    "en-first-principles": {
        "channel_id": "en_first_principles",
        "channel_slug": "en-first-principles",
        "niche": "Mental Models & Physics Paradoxes",
        "competitor_benchmark": "Veritasium",
        "subject_physics": (
            "Rigid real-world mechanical kinematics and laminar fluid or electromagnetic field dynamics, "
            "crisp specular reflections on machined metal and optical glass, natural high-shutter motion blur"
        ),
        "camera_grammar": ["slow optical dolly push-in", "smooth horizontal lateral tracking pass", "subtle low-angle scientific tilt-up"],
        "continuity_anchor": (
            "High-contrast 8K Veritasium scientific cinematography with crisp directional key light, "
            "deep slate-navy (#0F172A) contrast, and clean cyan/amber physical vector accents, strictly zero chalkboards or text"
        ),
        "forbidden_artifacts": ["chalkboards with gibberish equations", "cartoon doodle lines", "rubbery bending metal", "off-topic lab props"],
    },
    "en-scale-and-bone": {
        "channel_id": "en_scale_and_bone",
        "channel_slug": "en-scale-and-bone",
        "niche": "Zoology & Animal Life-Cycle Evolution",
        "competitor_benchmark": "BBC Earth / PBS Eons",
        "subject_physics": (
            "Authentic vertebrate muscular biomechanics, natural fur/feather/scale micro-textures reacting to wind and water, "
            "anatomically grounded weight transfer and organic breathing motion"
        ),
        "camera_grammar": ["telephoto 400mm shallow-DOF wildlife tracking shot", "slow crane reveal across natural habitat", "intimate eye-level optical push-in"],
        "continuity_anchor": (
            "BBC Earth natural-history wildlife cinematography on long-focal cinema glass, "
            "golden natural atmospheric daylight, rich organic terrain textures, strictly zero text"
        ),
        "forbidden_artifacts": ["plastic skin or feathers", "extra morphing limbs", "cartoon animal faces", "sliding weightless feet"],
    },
    "en-pocket-cosmos": {
        "channel_id": "en_pocket_cosmos",
        "channel_slug": "en-pocket-cosmos",
        "niche": "Astrophysics & Deep Space Exploration",
        "competitor_benchmark": "Melodysheep / Astrum",
        "subject_physics": (
            "Ray-marched volumetric celestial atmospheres and plasma dynamics, Keplerian orbital mechanics, "
            "realistic Rayleigh limb scattering and physically accurate gravitational light bending"
        ),
        "camera_grammar": ["grand parabolic space-probe flyby", "slow weightless orbital push-in toward terminator line", "zero-G lateral cosmic drift"],
        "continuity_anchor": (
            "Melodysheep hyper-detailed IMAX deep-space cinematography lit by a single coherent off-screen star keylight "
            "against pure velvet interstellar void, strictly zero text"
        ),
        "forbidden_artifacts": ["flat 2D cartoon planets", "chaotic handheld shake", "melting planetary geometry", "sci-fi HUD text"],
    },
    "en-deep-time-strata": {
        "channel_id": "en_deep_time_strata",
        "channel_slug": "en-deep-time-strata",
        "niche": "Geology & Deep Earth History",
        "competitor_benchmark": "History of the Earth",
        "subject_physics": (
            "Heavy geological mass and tectonic inertia, realistic viscous magma/sediment/ocean fluid dynamics, "
            "volumetric volcanic steam and atmospheric dust transport across ancient terrain"
        ),
        "camera_grammar": ["heavy tectonic aerial survey glide", "slow geological cliff-strata tilt", "deep-ocean optical probe drift"],
        "continuity_anchor": (
            "History of the Earth paleo-geological documentary cinematography with hyper-detailed mineral, basalt, "
            "and sedimentary textures under dramatic primordial atmospheric lighting, strictly zero text"
        ),
        "forbidden_artifacts": ["modern human buildings or grass in ancient eras", "jelly-like water physics", "fast FPV drone banking"],
    },
    "en-inside-vessel": {
        "channel_id": "en_inside_vessel",
        "channel_slug": "en-inside-vessel",
        "niche": "Human Physiology & Medical 3D",
        "competitor_benchmark": "Nucleus Medical Media",
        "subject_physics": (
            "Subsurface-scattered wet biological tissue elasticity, rhythmic physiological pulsatile flow, "
            "coherent cellular and molecular motion suspended in translucent fluid media"
        ),
        "camera_grammar": ["smooth endoscopic forward lumen dolly", "macro anatomical cross-section orbital arc", "micro-cellular shallow-DOF focus pull"],
        "continuity_anchor": (
            "Nucleus Medical Media 8K 3D endoscopic biomedical cinematography with glistening subsurface tissue textures "
            "and clean surgical fiber-optic rim lighting, strictly zero text labels"
        ),
        "forbidden_artifacts": ["dry plastic anatomy models", "floating anatomical text callouts", "sharp robotic camera snaps"],
    },
    "en-macro-gears": {
        "channel_id": "en_macro_gears",
        "channel_slug": "en-macro-gears",
        "niche": "Macroeconomics, Infrastructure & Industrial Engineering",
        "competitor_benchmark": "Practical Engineering / Wendover Productions",
        "subject_physics": (
            "Massive civil and industrial steel-and-concrete structural rigidity, realistic hydraulic and mechanical load transfer, "
            "authentic water/exhaust/cable physics at megastructure scale"
        ),
        "camera_grammar": ["high-altitude architectural aerial survey", "steady lateral engineering tracking pass", "precision cutaway dolly push-in"],
        "continuity_anchor": (
            "Practical Engineering & Wendover large-scale infrastructure documentary cinematography under crisp directional daylight, "
            "high-detail industrial materials, strictly zero text or map labels"
        ),
        "forbidden_artifacts": ["toy miniature blur", "rubbery bending steel beams", "gibberish signage or labels"],
    },
    "en-fine-print": {
        "channel_id": "en_fine_print",
        "channel_slug": "en-fine-print",
        "niche": "Consumer Law & Hidden Contracts",
        "competitor_benchmark": "CNBC Make It / LegalEagle",
        "subject_physics": (
            "Tactile physical paper, embossed metal seal, leather, and glass tabletop micro-physics, "
            "smooth directional light sweep and crisp shallow depth-of-field optical focus pulls"
        ),
        "camera_grammar": ["forensic macro perpendicular push-in", "smooth tabletop lateral dolly", "composed editorial pull-back"],
        "continuity_anchor": (
            "CNBC / LegalEagle investigative financial documentary cinematography with warm directional tungsten side-lighting, "
            "rich mahogany and slate tones, and abstract geometric document lines with strictly zero readable words or letters"
        ),
        "forbidden_artifacts": ["warping AI gibberish typography", "cartoon wooden gavels", "shaky handheld camera"],
    },
    "en-crowd-strings": {
        "channel_id": "en_crowd_strings",
        "channel_slug": "en-crowd-strings",
        "niche": "Mass Psychology & Investigative 3D Documentary",
        "competitor_benchmark": "Fern / Academy of Ideas",
        "subject_physics": (
            "Fern-style stylized 3D investigative diorama physics, smooth synchronized silhouette movement, "
            "volumetric light cones and crisp geometric network signal propagation"
        ),
        "camera_grammar": ["isometric-to-low-angle 3D architectural dolly", "locked orthogonal tracking pass", "slow subterranean crane descent"],
        "continuity_anchor": (
            "Fern TV moody 3D investigative documentary aesthetic in desaturated slate-blue and concrete grey "
            "with selective cyan and warm amber volumetric spotlights, strictly zero text"
        ),
        "forbidden_artifacts": ["ragdoll crowd collisions", "bouncy 2D cartoon icons", "uncanny close-up facial distortion"],
    },
    "en-cold-case-ink": {
        "channel_id": "en_cold_case_ink",
        "channel_slug": "en-cold-case-ink",
        "niche": "Forensic Mysteries & Unsolved Archives",
        "competitor_benchmark": "LEMMiNO",
        "subject_physics": (
            "Slow volumetric fog and rain particle drift, realistic wet surface specular reflections, "
            "subtle physical tension in archival evidence threads and chiaroscuro shadow movement"
        ),
        "camera_grammar": ["brooding noir crane descent", "slow forensic macro push-in", "steady lateral diorama tracking pass"],
        "continuity_anchor": (
            "LEMMiNO atmospheric noir 3D forensic documentary cinematography in deep midnight slate, monochrome silver, "
            "and selective crimson/amber rim light, strictly zero readable text"
        ),
        "forbidden_artifacts": ["cheap horror jumpscares", "gore", "neon cyberpunk colors", "gibberish newspaper text"],
    },
    "en-choke-point": {
        "channel_id": "en_choke_point",
        "channel_slug": "en-choke-point",
        "niche": "Maritime Geopolitics & Satellite Maps",
        "competitor_benchmark": "RealLifeLore / Johnny Harris",
        "subject_physics": (
            "High-altitude orbital cloud swirl drift, luminous golden maritime/strategic flow vectors gliding cleanly along waterways, "
            "realistic ocean wake physics through narrow geographic corridors"
        ),
        "camera_grammar": ["orbital satellite-to-strait zoom descent", "smooth lateral 3D relief map flight", "low-horizon naval corridor pass"],
        "continuity_anchor": (
            "RealLifeLore hyper-realistic 3D orbital satellite terrain and deep bathymetric navy ocean cinematography "
            "with blue atmospheric limb glow and golden vector highlights, strictly zero map text or labels"
        ),
        "forbidden_artifacts": ["flat 2D Google Maps pins", "ships sliding onto dry land", "warping coastlines", "gibberish country names"],
    },
    "en-root-and-canopy": {
        "channel_id": "en_root_and_canopy",
        "channel_slug": "en-root-and-canopy",
        "niche": "Botany & Forest Ecology",
        "competitor_benchmark": "BBC Earth (The Green Planet)",
        "subject_physics": (
            "Organic botanical cellular growth and turgor motion, delicate moisture droplet surface tension, "
            "gentle forest breeze swaying foliage and floating spore/pollen particles in sunbeams"
        ),
        "camera_grammar": ["subterranean-to-canopy vertical probe crane", "optical macro botanical dolly push-in", "gentle forest floor tracking glide"],
        "continuity_anchor": (
            "BBC Earth Green Planet optical macro botany cinematography with rich damp soil and emerald cellular textures, "
            "shallow depth of field, and golden volumetric forest rim lighting, strictly zero text"
        ),
        "forbidden_artifacts": ["plastic origami plants", "strobing timelapse flicker", "2D flat leaf cutouts"],
    },
    "en-spawn-to-apex": {
        "channel_id": "en_spawn_to_apex",
        "channel_slug": "en-spawn-to-apex",
        "niche": "Micro-Biology & Chronological Insect Life-Cycle",
        "competitor_benchmark": "Deep Look PBS",
        "subject_physics": (
            "Articulated arthropod exoskeleton and micro-organism biomechanics, high-surface-tension water droplet physics, "
            "iridescent chitin specular shift under razor-thin macro depth of field"
        ),
        "camera_grammar": ["locked Laowa 24mm probe macro push-in", "ultra-shallow-DOF lateral specimen track", "steady micro-habitat orbit"],
        "continuity_anchor": (
            "Deep Look PBS extreme optical macro biology cinematography at f/2.8 with hyper-detailed microscopic anatomy "
            "isolated against a clean dark velvet bokeh backdrop, strictly zero text"
        ),
        "forbidden_artifacts": ["3D Pixar cartoon bug faces", "mutating leg counts", "gelatinous body melting"],
    },
    "en-second-arrow": {
        "channel_id": "en_second_arrow",
        "channel_slug": "en-second-arrow",
        "niche": "Stoicism & Classical Philosophy",
        "competitor_benchmark": "Einzelgänger / Daily Stoic",
        "subject_physics": (
            "Slow Caravaggio chiaroscuro light-ray and shadow progression across weathered stone and bronze, "
            "drifting dust motes, gentle rain or flame flicker with solemn classical stillness"
        ),
        "camera_grammar": ["contemplative slow museum dolly-in", "solemn low-angle architectural tilt-up", "composed chiaroscuro lateral pan"],
        "continuity_anchor": (
            "Classical Caravaggio chiaroscuro cinematography over aged Greco-Roman marble, weathered bronze, "
            "and timeless Mediterranean stone architecture lit by single-source golden sunbeams, strictly zero text"
        ),
        "forbidden_artifacts": ["talking or smiling marble statues", "modern neon or cars", "fast shaky cuts"],
    },
    "en-bamboo-marble": {
        "channel_id": "en_bamboo_marble",
        "channel_slug": "en-bamboo-marble",
        "niche": "Eastern Philosophy & Contemplative Essays",
        "competitor_benchmark": "Pursuit of Wonder / Aperture",
        "subject_physics": (
            "Tranquil natural wind, mist, rain, and water-ripple fluid physics, subtle contemplative human stillness, "
            "soft warm lantern or dusk light breathing gently across natural wood and stone"
        ),
        "camera_grammar": ["anamorphic 35mm slow horizontal drift", "tranquil meditative push-in", "locked contemplative wide composition"],
        "continuity_anchor": (
            "Aperture & Pursuit of Wonder moody 35mm anamorphic contemplative cinema with natural dusk/rain chiaroscuro, "
            "serene East Asian timber, moss, and misty mountain textures, strictly zero text"
        ),
        "forbidden_artifacts": ["anime fantasy effects", "neon cyberpunk colors", "abrupt whip pans"],
    },
    "en-kindred-sketch": {
        "channel_id": "en_kindred_sketch",
        "channel_slug": "en-kindred-sketch",
        "niche": "Relationships, Empathy & Attachment Psychology",
        "competitor_benchmark": "The School of Life / Cinema Therapy",
        "subject_physics": (
            "Subtle authentic human micro-expressions, natural breathing and gentle hand gestures, "
            "warm candle/lamp light reflections and soft window rain refraction at shallow f/1.8 depth of field"
        ),
        "camera_grammar": ["empathetic slow 35mm table-level push-in", "intimate over-the-shoulder focus pull", "gentle lateral drift across shared space"],
        "continuity_anchor": (
            "Intimate 35mm live-action film cinematography with Kodak Vision3 500T color grading, warm 3000K tungsten bokeh, "
            "natural skin and fabric grain, and quiet emotional realism, strictly zero text, no speaking or lip movement"
        ),
        "forbidden_artifacts": ["talking mouth movement", "exaggerated soap-opera grimacing", "flat 2D cartoon doodles", "cold fluorescent hospital light"],
    },
    "en-lazy-brain": {
        "channel_id": "en_lazy_brain",
        "channel_slug": "en-lazy-brain",
        "niche": "Neuroscience of Dopamine, Focus & Habits",
        "competitor_benchmark": "Kurzgesagt / Huberman Lab",
        "subject_physics": (
            "Coherent bio-electrical signal pulses traveling along 3D neural axons and synaptic clefts, "
            "paired with calm 35mm human focus body language and smooth optical light transitions"
        ),
        "camera_grammar": ["sweeping 3D synaptic orbital arc", "diving cortex macro zoom-in", "calm 35mm shallow-DOF focus push-in"],
        "continuity_anchor": (
            "High-contrast 8K 3D biomedical neuroscience visualization in deep midnight space with bioluminescent cyan/amber "
            "pathways and moody 35mm behavioral focus cinematography, strictly zero text"
        ),
        "forbidden_artifacts": ["cartoon brain with eyes", "strobing seizure flashes", "flat MS-Paint stick figures"],
    },
    "en-career-leverage": {
        "channel_id": "en_career_leverage",
        "channel_slug": "en-career-leverage",
        "niche": "Workplace Strategy, Economics of Careers & Leverage",
        "competitor_benchmark": "Wall Street Journal / Harvard Business Review",
        "subject_physics": (
            "Poised executive body language without speaking, crisp architectural light-and-shadow geometry across glass, steel, "
            "and dark wood, smooth precision mechanical balance and subtle skyline motion"
        ),
        "camera_grammar": ["authoritative WSJ architectural lateral dolly", "low-angle executive push-in", "composed wide boardroom pull-back"],
        "continuity_anchor": (
            "WSJ & HBR high-contrast editorial photojournalism cinematography in charcoal slate, crisp architectural glass, "
            "and warm brass directional lighting at f/2.0 shallow depth of field, strictly zero text"
        ),
        "forbidden_artifacts": ["cartoon money bags", "talking lip movement", "warping office furniture"],
    },
    "en-wallet-anatomy": {
        "channel_id": "en_wallet_anatomy",
        "channel_slug": "en-wallet-anatomy",
        "niche": "Behavioral Pricing & Consumer Finance",
        "competitor_benchmark": "Two Cents PBS / WSJ Consumer Economics",
        "subject_physics": (
            "Tactile real-world consumer product, currency, leather, glass, and checkout hardware physics, "
            "smooth commercial studio lighting reflections and clean f/2.0 optical rack-focus"
        ),
        "camera_grammar": ["smooth 35mm commercial dolly push-in", "eye-level lateral tabletop/aisle tracking", "clean macro product rack-focus"],
        "continuity_anchor": (
            "WSJ Consumer Economics & Two Cents realistic 35mm documentary and tabletop macro cinematography "
            "with crisp commercial lighting, rich physical textures, and strictly zero readable text, words, or price digits"
        ),
        "forbidden_artifacts": ["flat 2D cartoon paper cutouts", "off-topic grocery items in non-grocery scenes", "gibberish printed letters"],
    },
}


def build_channel_motion_prompt(
    channel_slug: str,
    shot_action: str,
    camera_move: str | None = None,
    is_interpolation: bool = True,
    scene_anchor: str | None = None,
) -> str:
    """Compile the deterministic 4-component 70/30 Google Flow motion prompt for a specific channel.

    Uses per-shot `scene_anchor` when provided so scene-specific environments stay 100% locked
    without injecting off-topic props from other scenes.
    """
    slug = channel_slug.strip().replace("_", "-")
    spec = EN_FLOW_VIDEO_FORMULAS.get(slug) or EN_FLOW_VIDEO_FORMULAS["en-first-principles"]
    cam = camera_move or spec["camera_grammar"][0]
    mode_prefix = (
        "Continuous fluid spatial transition between start and end frames:"
        if is_interpolation
        else "Cinematic single-shot motion:"
    )
    action_clean = " ".join((shot_action or "").split()).rstrip(".")
    anchor_clean = " ".join((scene_anchor or spec["continuity_anchor"]).split()).rstrip(".")
    return (
        f"{mode_prefix} {cam}. {action_clean}. "
        f"Material physics: {spec['subject_physics']}. "
        f"Visual & lighting lock: {anchor_clean}. "
        f"{UNIVERSAL_STABILITY_GUARDRAILS}."
    )


def build_reference_keyframe_prompt(
    channel_slug: str,
    next_visual_state: str,
    use_camera_angle_wrapper: bool = False,
    scene_anchor: str | None = None,
) -> str:
    """Wrap destination keyframe prompt using Google's official Story Sketch / Shot Explorer formula."""
    slug = channel_slug.strip().replace("_", "-")
    spec = EN_FLOW_VIDEO_FORMULAS.get(slug) or EN_FLOW_VIDEO_FORMULAS["en-first-principles"]
    core = " ".join((next_visual_state or "").split()).rstrip(".")
    anchor_clean = " ".join((scene_anchor or spec["continuity_anchor"]).split()).rstrip(".")
    if use_camera_angle_wrapper:
        return (
            f"A cinematic new camera angle of this exact scene: {core}. "
            f"Preserve exact subject identity, material textures, and lighting from reference ({anchor_clean}). "
            "Strict zero-text policy: zero words, zero letters, zero numbers, zero watermarks."
        )
    return (
        f"Generate an image showing what happens next based on this input: {core}. "
        f"Preserve exact subject geometry, color grade, and environment anchor ({anchor_clean}). "
        "Strict zero-text policy: zero words, zero letters, zero numbers, zero watermarks."
    )


EN_CHANNEL_LOGO_PROMPTS: dict[str, str] = {
    "en-first-principles": (
        "Minimalist geometric emblem centered on a solid deep navy background (#0F172A). "
        "A bold, razor-sharp balance fulcrum deconstructed into pure geometry: a glowing golden amber (#F59E0B) "
        "sphere levitating at the apex of a sleek cyan (#38BDF8) equilateral triangle pivot with two clean horizontal "
        "balance beams. Pure flat vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-scale-and-bone": (
        "Minimalist biomechanics anatomy emblem centered on a solid warm ivory background (#F5F2EB). "
        "A bold stylized cross-section of a vertebrate bone vertebra curving seamlessly into a logarithmic golden spiral, "
        "rendered in deep forest moss green (#2D5A3A) with a terracotta amber (#C85A32) marrow core. "
        "Pure flat vector symbol, sharp graphic contours, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-pocket-cosmos": (
        "Minimalist astrophysics emblem centered on a solid void-black background (#050814). "
        "A bold circular black hole silhouette encircled by a razor-sharp glowing solar gold (#FBBF24) photon ring "
        "and intersected diagonally by a sleek electric cyan (#38BDF8) orbital arc. "
        "Pure flat vector symbol, extreme contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-deep-time-strata": (
        "Minimalist paleontology and geology emblem centered on a solid fossil-ivory background (#F5EFE6). "
        "A bold circular geological medallion showing horizontal dark charcoal (#292524) rock strata layers "
        "encasing a centered golden amber (#D97706) fossil ammonite spiral shell. "
        "Pure flat vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-inside-vessel": (
        "Minimalist medical physiology emblem centered on a solid deep navy background (#0A192F). "
        "A stylized 3D vector biconcave red blood cell in rich arterial crimson (#EF4444) framed inside a "
        "clean circular glowing cyan (#06B6D4) capillary vessel ring. "
        "Pure scientific vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-macro-gears": (
        "Minimalist heavy civil engineering emblem centered on a solid warm cream background (#F7F2EB). "
        "Two interlocking dark slate navy (#1E293B) precision gear cogs framing a bold industrial orange (#EA580C) "
        "structural truss triangle at the center. "
        "Pure Swiss graphic vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-fine-print": (
        "Minimalist legal investigation emblem centered on a solid newsprint ivory background (#F4EFE6). "
        "A bold midnight navy (#1E293B) magnifying glass loupe centered over balanced justice scales, "
        "accented with a single vivid vermilion red (#E63946) circular wax dot at the fulcrum. "
        "Pure editorial vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-crowd-strings": (
        "Minimalist intelligence network emblem centered on a solid dark slate background (#111827). "
        "A bold geometric triangle of three crisp ivory white (#F3F4F6) node spheres connected from above "
        "by taut glowing crimson red (#DC2626) marionette control lines meeting at a single apex diamond. "
        "Pure noir vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-cold-case-ink": (
        "Minimalist forensic mystery emblem centered on a solid pitch-black background (#0B0F19). "
        "A crisp circular white (#F1F5F9) fingerprint whorl silhouette sliced diagonally by a sharp 45-degree "
        "spotlight cone illuminating a single crimson red (#E11D48) central point. "
        "Pure noir vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-choke-point": (
        "Minimalist maritime geopolitics emblem centered on a solid deep navy background (#0F172A). "
        "Two bold coastal landmass silhouettes in sand white (#E2E8F0) forming a narrow oceanic strait "
        "with a vivid crimson red (#DC2626) directional navigation arrow passing cleanly through the gap. "
        "Pure cartographic vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-root-and-canopy": (
        "Minimalist botanical forestry emblem centered on a solid warm linen background (#F5EBE1). "
        "A symmetrical circular medallion showing a lush forest green (#2E5A44) tree crown above mirrored "
        "by spreading underground roots below, united around a glowing amber gold (#D97706) seed heart. "
        "Pure nature vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-spawn-to-apex": (
        "Minimalist macro predatory biology emblem centered on a solid dark graphite background (#18181B). "
        "A bold surgical white (#FAFAFA) praying mantis raptorial claw silhouette poised in strike position "
        "with a glowing amber gold (#F59E0B) faceted eye gem at the joint. "
        "Pure graphic vector symbol, extreme contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-second-arrow": (
        "Minimalist Zen philosophy emblem centered on a solid warm rice-paper cream background (#F7F4EB). "
        "A bold charcoal sumi-e ink enso circle (#1E293B) enclosing one straight arrow above and a second arrow "
        "cleanly snapped in half below, accented with a single vermilion red (#E0564C) dot. "
        "Pure meditative vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-bamboo-marble": (
        "Minimalist classical philosophy emblem centered on a solid midnight navy background (#0F172A). "
        "A bold vertical emblem split down the center: left half a fluted ivory (#E2E8F0) Greco-Roman marble column, "
        "right half a segmented emerald-sage bamboo stalk, topped by a warm gold (#F59E0B) crescent arc. "
        "Pure flat vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-kindred-sketch": (
        "Minimalist human psychology emblem centered on a solid warm cream background (#FDFBF7). "
        "A bold continuous espresso-charcoal (#382216) line forming two facing minimalist profile silhouettes "
        "whose shared negative space creates a warm coral rose (#E05A67) heart bridge in the center. "
        "Pure clean vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-lazy-brain": (
        "Minimalist cognitive neuroscience emblem centered on a solid warm cream background (#F8F0DC). "
        "A bold cobalt blue (#3B82C4) stylized brain silhouette encircled by a clean dark ink orbital loop "
        "with a vivid coral red (#E63946) lightning spark at the frontal lobe. "
        "Pure scientific vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-career-leverage": (
        "Minimalist executive strategy emblem centered on a solid light parchment background (#F8F6F0). "
        "A bold deep navy (#2C3E50) mechanical lever resting on a sharp triangle fulcrum, lifting a "
        "glowing imperial gold (#E5A93C) geometric cube effortlessly upward. "
        "Pure editorial vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "en-wallet-anatomy": (
        "Minimalist consumer economics emblem centered on a solid ivory background (#FAF8F5). "
        "A bold isometric cross-section of a circular coin sliced cleanly open to reveal deep emerald green (#1B4931) "
        "architectural layers surrounding a bright crimson red (#D9381E) diamond core. "
        "Pure financial vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
}


__all__ = [
    "EN_CHANNEL_LOGO_PROMPTS",
    "EN_FLOW_VIDEO_FORMULAS",
    "FLOW_FRAME_CONTROL_MODES",
    "RETENTION_SHOT_BLUEPRINTS",
    "UNIVERSAL_STABILITY_GUARDRAILS",
    "build_channel_motion_prompt",
    "build_reference_keyframe_prompt",
]
