"""SSOT Flow Video Frame-Control, Motion Physics & Viewer Retention Formulas for All 20 Vietnamese Channels.

Synthesized from multi-source practitioner workflows (Google Flow Scenebuilder, Ingredients/Reference
Conditioning, First-to-Last Frame Interpolation, Boundary-Frame Extend), reverse-engineered Google
First-Party Applets (`Style Writer`, `Shot Explorer`, `Story Sketch`, `Transition Machine`), and
empirical frame-by-frame competitor documentary analysis across all 20 Vietnamese Video Pilot channels.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

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
# 3. ALL 20 VIETNAMESE CHANNELS — SPECIALIZED FLOW VIDEO PHYSICS & CONTINUITY SSOT
#    Pure topic-agnostic material physics, lens grammar, and lighting DNA.
#    Strictly ZERO hardcoded single-episode props or text-bearing chalkboards.
# ==============================================================================
VN_FLOW_VIDEO_FORMULAS: Dict[str, Dict[str, Any]] = {
    # --------------------------------------------------------------------------
    # Tier-A (0-9 views)
    # --------------------------------------------------------------------------
    "tui_tien": {
        "channel_id": "tui_tien",
        "channel_slug": "tui-tien",
        "niche": "Tiền và kinh tế đời sống (Consumer Economics & Behavioral Pricing)",
        "competitor_benchmark": "Two Cents PBS / WSJ Consumer Economics / Tài Chính & Kinh Doanh",
        "new_visual_label": "35mm Tabletop Commercial & Tactile Consumer Economics Cinematography",
        "style_description": (
            "35mm tabletop commercial cinematography with warm directional tungsten keylight and soft ambient fill "
            "on a clean textured linen or slate surface. High-contrast tactile product macro, rich tactile materials "
            "(leather wallets, crisp polymer banknotes, embossed coins, checkout receipts), warm amber and deep slate palette "
            "with selective emerald green accents. Shallow f/2.0 optical depth-of-field with silky background bokeh, "
            "commercial grade color grading, zero 2D doodle lines, zero cartoons."
        ),
        "subject_physics": (
            "Tactile real-world consumer product, crisp polymer banknote, leather, glass, and checkout hardware physics, "
            "smooth commercial studio lighting specular reflections, realistic weight transfer and clean f/2.0 optical rack-focus"
        ),
        "camera_grammar": [
            "smooth 35mm commercial dolly push-in",
            "eye-level lateral tabletop tracking pass",
            "clean macro product rack-focus",
        ],
        "continuity_anchor": (
            "WSJ Consumer Economics & Two Cents realistic 35mm tabletop cinematography with crisp commercial keylight, "
            "f/2.0 optical depth-of-field, and tactile anti-morph physical dynamics across diverse consumer environments, "
            "strictly zero readable text, words, or price digits"
        ),
        "forbidden_artifacts": [
            "flat 2D cartoon paper cutouts",
            "off-topic grocery items in non-grocery scenes",
            "gibberish printed letters",
            "warping credit card logos",
            "cartoon money bags",
        ],
        "thumbnail_rule": (
            "One tactile focal consumer object or sliced coin with crisp directional lighting, "
            "2-4 uppercase bold words, high contrast, zero overlay card, 25% margin"
        ),
    },
    "banh_rang": {
        "channel_id": "banh_rang",
        "channel_slug": "banh-rang",
        "niche": "Kinh tế vĩ mô, lạm phát, lãi suất và chuỗi cung ứng toàn cầu (Macroeconomics & Industrial Logistics)",
        "competitor_benchmark": "Practical Engineering / Wendover Productions",
        "new_visual_label": "Large-Scale Industrial Infrastructure & Macro Logistics Cinematography",
        "style_description": (
            "Large-scale industrial engineering and infrastructure documentary cinematography under crisp directional natural daylight. "
            "Deep slate navy, weathered industrial steel, and high-visibility safety orange accents. Towering container port gantry cranes, "
            "massive interlocking forged steel gears, drydocks, and automated logistics megastructures. Crisp architectural f/5.6 depth-of-field, "
            "clean horizontal horizons, and monumental mechanical scale."
        ),
        "subject_physics": (
            "Massive civil and industrial steel-and-concrete structural rigidity, realistic hydraulic and mechanical load transfer, "
            "authentic water wake, container crane suspension, and exhaust physics at megastructure scale"
        ),
        "camera_grammar": [
            "high-altitude architectural aerial survey",
            "steady lateral engineering tracking pass",
            "precision cutaway dolly push-in",
        ],
        "continuity_anchor": (
            "Practical Engineering & Wendover large-scale infrastructure documentary cinematography under crisp directional daylight, "
            "architectural lens depth-of-field, and rigid load-bearing anti-morph physics across changing engineering subjects, "
            "strictly zero text or map labels"
        ),
        "forbidden_artifacts": [
            "toy miniature tilt-shift blur",
            "rubbery bending steel beams",
            "gibberish signage or shipping container labels",
            "fast erratic FPV drone banking",
            "cartoon factory smokestacks",
        ],
        "thumbnail_rule": (
            "Monumental industrial gear or cargo megastructure framed against atmospheric sky, "
            "2-4 bold uppercase words, high contrast, zero overlay card, 25% margin"
        ),
    },
    "luat_doi_thuong": {
        "channel_id": "luat_doi_thuong",
        "channel_slug": "luat-doi-thuong",
        "niche": "Pháp lý dân sự bình dân: hợp đồng, thuê nhà, lao động, vay mượn (Civil Law & Consumer Contracts)",
        "competitor_benchmark": "LegalEagle / CNBC Make It / Luật Sư X",
        "new_visual_label": "Tactile Forensic Legal Document & Investigative Macro Cinematography",
        "style_description": (
            "Tactile forensic legal and investigative documentary cinematography with warm directional tungsten side-lighting (3200K) "
            "against rich mahogany, slate, and textured archival paper. Macro perpendicular push-ins, heavy brass balance scales, "
            "embossed red sealing wax, magnifying glass loupe refractions, and f/2.0 shallow depth of field. Serious editorial mood "
            "with deep shadows and warm amber accents."
        ),
        "subject_physics": (
            "Tactile physical paper grain, embossed brass seal, aged leather bookbinding, and polished glass optical refraction, "
            "smooth directional light sweep and crisp shallow depth-of-field optical focus pulls"
        ),
        "camera_grammar": [
            "forensic macro perpendicular push-in",
            "smooth tabletop lateral dolly pass",
            "composed editorial pull-back reveal",
        ],
        "continuity_anchor": (
            "CNBC & LegalEagle investigative documentary cinematography with warm directional tungsten side-lighting, "
            "deep mahogany and slate palette, macro f/2.0 shallow depth-of-field, and tactile anti-morph material physics "
            "across varying document scales, strictly zero readable words or letters"
        ),
        "forbidden_artifacts": [
            "warping AI gibberish typography",
            "cartoon wooden gavels",
            "shaky handheld camera",
            "distorted courtroom faces",
            "floating neon holograms",
        ],
        "thumbnail_rule": (
            "Close-up macro of brass scale or red wax seal on textured parchment under dramatic side-lighting, "
            "2-4 bold uppercase words, high contrast, zero overlay card, 25% margin"
        ),
    },
    "la_ban_hoc_thuat": {
        "channel_id": "la_ban_hoc_thuat",
        "channel_slug": "la-ban-hoc-thuat",
        "niche": "Phương pháp tự học sâu, tư duy phản biện & nghiên cứu khoa học (Deep Learning & Critical Research)",
        "competitor_benchmark": "Veritasium / 3Blue1Brown / Spiderum",
        "new_visual_label": "Kinematic Cognitive Experiment & Modern Laboratory Cinematography",
        "style_description": (
            "Veritasium-grade scientific laboratory and cognitive experimental cinematography with clean directional daylight (5600K) "
            "and subtle slate-cyan rim light. Modern minimalist research laboratory, optical glass prisms, laser refraction, "
            "precision balance fulcrums, clean chalkboard geometry without letters, and matte dark-blue slate aesthetics. "
            "Razor-sharp f/2.8 focus and clinical intellectual elegance."
        ),
        "subject_physics": (
            "Rigid mechanical kinematics, optical laser reflection and refraction through solid silica glass, "
            "laminar fluid flow in transparent acrylic tubes, crisp specular reflections on machined aluminum and brass"
        ),
        "camera_grammar": [
            "slow optical dolly push-in toward apparatus",
            "smooth horizontal lateral tracking pass",
            "subtle low-angle scientific tilt-up",
        ],
        "continuity_anchor": (
            "Veritasium scientific cinematography with crisp directional key light, deep slate-navy (#0F172A) palette, "
            "f/2.8 lens depth-of-field, and rigid anti-morph kinematics allowing dynamic experimental shifts, "
            "strictly zero chalkboards with text or gibberish formulas"
        ),
        "forbidden_artifacts": [
            "chalkboards with gibberish equations",
            "cartoon doodle lines",
            "rubbery bending metal",
            "magical floating fantasy orbs",
            "spinning off-topic props",
        ],
        "thumbnail_rule": (
            "High-contrast laboratory experiment or optical prism beam on dark slate, "
            "2-4 uppercase bold words, high contrast, zero overlay card, 25% margin"
        ),
    },
    "luat_ngam": {
        "channel_id": "luat_ngam",
        "channel_slug": "luat-ngam",
        "niche": "Tâm lý xã hội, hiệu ứng bầy đàn và nghệ thuật đàm phán đời thường (Social Dynamics & Mass Behavioral Architecture)",
        "competitor_benchmark": "Fern TV / Academy of Ideas / CDTeam",
        "new_visual_label": "3D Investigative Diorama & Architectural Surveillance Cinematography",
        "style_description": (
            "Moody Fern-style stylized 3D investigative diorama documentary cinematography. Desaturated slate-blue (#1E293B) and charcoal palette "
            "with selective amber and cyan volumetric searchlights. Orthogonal low-angle tracking across isometric urban cross-sections, "
            "synchronized faceless crowd silhouettes, architectural miniature models, and subterranean command rooms with geometric network connections."
        ),
        "subject_physics": (
            "Fern-style stylized 3D architectural diorama physics, smooth synchronized silhouette movement, "
            "volumetric light cones and crisp geometric network signal propagation along isometric planes"
        ),
        "camera_grammar": [
            "isometric-to-low-angle 3D architectural dolly",
            "locked orthogonal tracking pass across diorama",
            "slow subterranean crane descent into chamber",
        ],
        "continuity_anchor": (
            "Fern TV moody 3D investigative documentary aesthetic in desaturated slate-blue palette with selective cyan and warm amber volumetric spotlights, "
            "orthogonal lens depth, and synchronized anti-morph diorama physics across varying scene scopes, strictly zero text"
        ),
        "forbidden_artifacts": [
            "ragdoll crowd collisions",
            "bouncy 2D cartoon icons",
            "uncanny close-up facial distortion",
            "neon cyberpunk clutter",
            "gibberish neon billboards",
        ],
        "thumbnail_rule": (
            "Dramatic 3D isometric diorama with volumetric spotlight singling out one silhouette, "
            "2-4 bold uppercase words, high contrast, zero overlay card, 25% margin"
        ),
    },

    # --------------------------------------------------------------------------
    # Tier-B (0-7 views)
    # --------------------------------------------------------------------------
    "ua_sao_vay": {
        "channel_id": "ua_sao_vay",
        "channel_slug": "ua-sao-vay",
        "niche": "Sự thật bất ngờ, khoa học gây tò mò & vật lý đời thường (Everyday Curiosities & Cross-Section Physics)",
        "competitor_benchmark": "Veritasium / Zack D. Films",
        "new_visual_label": "3D Macro Cross-Section Physics & Everyday Phenomenon Cinema",
        "style_description": (
            "High-energy 3D macro cross-section and everyday phenomenon cinematography inspired by Zack D. Films and Veritasium. "
            "Vibrant yet physically grounded studio lighting with clean white and charcoal contrast. Photorealistic cross-sections "
            "of everyday objects (zippers, locks, ballpoint pens, micro-switches, pressurized cans) revealing inner mechanical kinematics "
            "with anatomical clarity and satisfying micro-motion."
        ),
        "subject_physics": (
            "Rigid interlocking mechanical cross-sections, high-pressure gas expansion, spring compression and recoil, "
            "fluid capillary action, and micro-particle dispersion rendered with tactile physical mass"
        ),
        "camera_grammar": [
            "slow slicing cross-section push-in",
            "locked 360-degree macro orbital rotation",
            "rapid-to-slow-motion mechanism track",
        ],
        "continuity_anchor": (
            "Zack D. Films & Veritasium 3D cross-section scientific cinema with clean high-key studio lighting, neutral slate studio background, "
            "razer-sharp f/4.0 mechanical depth-of-field, and rigid anti-morph interlocking kinematics, strictly zero text or speech bubbles"
        ),
        "forbidden_artifacts": [
            "cheap plastic mobile-game textures",
            "soft melting mechanical parts",
            "gibberish text labels",
            "distorted cartoon faces",
            "floating emoji icons",
        ],
        "thumbnail_rule": (
            "Surgically clean 3D cross-section of a familiar everyday object revealing unexpected inner mechanism, "
            "2-4 uppercase bold words, high contrast, zero overlay card, 25% margin"
        ),
    },
    "dia_com": {
        "channel_id": "dia_com",
        "channel_slug": "dia-com",
        "niche": "Hóa học ẩm thực, an toàn thực phẩm và nhiệt động học căn bếp (Culinary Chemistry & Food Science)",
        "competitor_benchmark": "America's Test Kitchen / Modernist Cuisine",
        "new_visual_label": "Macro Molecular Culinary & Thermal Reaction 3D Cinema",
        "style_description": (
            "Modernist Cuisine and America's Test Kitchen optical macro cinematography. Rich culinary palette of searing copper, "
            "deep caramel amber, crisp herb emerald, and matte cast-iron charcoal. High-speed thermal reactions (Maillard browning, "
            "caramelization, emulsification, water vapor boiling, crystallization) captured with razor-thin f/2.8 probe lenses and dramatic glancing rim light."
        ),
        "subject_physics": (
            "Thermal heat transfer, authentic viscous liquid emulsification, bubbling fat droplets, Maillard surface crusting, "
            "vapor convection currents, and organic cellular turgor in food tissue"
        ),
        "camera_grammar": [
            "Laowa probe lens macro push-in across bubbling surface",
            "slow lateral cast-iron pan glide",
            "high-speed vertical drop and sizzle tilt",
        ],
        "continuity_anchor": (
            "Modernist Cuisine extreme macro culinary cinematography with warm directional copper and tungsten lighting, "
            "shallow f/2.8 probe depth-of-field, and fluid thermal anti-morph physics across culinary ingredients, "
            "strictly zero floating recipe text or metric units"
        ),
        "forbidden_artifacts": [
            "fake rubber food models",
            "slimy melting distortions",
            "floating nutrient percentages",
            "unrealistic neon food colors",
            "dirty kitchen clutter",
        ],
        "thumbnail_rule": (
            "Ultra-macro sizzle of caramelizing crust or oil droplet emulsion on black cast iron, "
            "2-4 uppercase bold words, high contrast, zero overlay card, 25% margin"
        ),
    },
    "vu_tru_ti_hon": {
        "channel_id": "vu_tru_ti_hon",
        "channel_slug": "vu-tru-ti-hon",
        "niche": "Thiên văn học, vật lý lượng tử và không-thời gian (Astrophysics & Deep Space)",
        "competitor_benchmark": "Melodysheep / Astrum",
        "new_visual_label": "Deep-Space Ray-Marched IMAX Cinematography",
        "style_description": (
            "Melodysheep-inspired hyper-detailed IMAX deep-space cinematography. Deep void-black (#050814) interstellar space "
            "illuminated by a single coherent off-screen star keylight or accretion disk glow. Luminous nebula gas filaments, "
            "ray-marched volumetric plasma, realistic Rayleigh limb scattering along planetary horizons, and gravitational lensing "
            "around singularities. Grand cosmic scale with scientific grounding."
        ),
        "subject_physics": (
            "Ray-marched volumetric celestial atmospheres and plasma dynamics, Keplerian orbital mechanics, "
            "relativistic gravitational lensing, and realistic dust/gas particle drift across cosmic vacuums"
        ),
        "camera_grammar": [
            "grand parabolic space-probe flyby",
            "slow weightless orbital push-in toward terminator line",
            "zero-G lateral cosmic drift across ring plane",
        ],
        "continuity_anchor": (
            "Melodysheep hyper-detailed IMAX deep-space cinematography lit by a single coherent celestial keylight against pure velvet void, "
            "telephoto depth-of-field, and Keplerian anti-morph celestial physics across shifting cosmic scales, strictly zero text"
        ),
        "forbidden_artifacts": [
            "flat 2D cartoon planets",
            "chaotic handheld shake",
            "melting planetary geometry",
            "sci-fi HUD text or cockpit glass",
            "cheesy lens flare starbursts",
        ],
        "thumbnail_rule": (
            "Breathtaking glowing accretion disk or razor-thin planetary crescent against void-black space, "
            "2-4 bold uppercase words, high contrast, zero overlay card, 25% margin"
        ),
    },
    "chanh_niem_ke": {
        "channel_id": "chanh_niem_ke",
        "channel_slug": "chanh-niem-ke",
        "niche": "Triết lý Phật giáo ứng dụng, Chánh niệm & nghệ thuật buông bỏ (Applied Mindfulness & Zen Philosophy)",
        "competitor_benchmark": "Pursuit of Wonder / Aperture",
        "new_visual_label": "35mm Anamorphic Kyoto Zen Sanctuary & Rain Cinema",
        "style_description": (
            "Pursuit of Wonder and Aperture contemplative 35mm anamorphic cinema. Weathered natural cedar wood, wet river stones, "
            "mossy courtyard flagstones, and gentle drizzle rippling into stone water basins (tsukubai). Soft diffused overcast dawn light, "
            "gentle paper shoji lantern glow (2400K), drifting incense smoke, and deep muted earth-tone palette (#2D3748, #3F372C, #718096, #D4AF37). "
            "Calming, spacious visual silence."
        ),
        "subject_physics": (
            "Natural fluid rain ripples, gentle wind swaying bamboo leaves, slow organic drifting incense smoke curls, "
            "soft light dissipation through textured washi paper, and peaceful water droplet surface tension"
        ),
        "camera_grammar": [
            "anamorphic 35mm slow horizontal drift across sanctuary",
            "tranquil meditative push-in toward dripping eaves",
            "locked contemplative wide composition of courtyard",
        ],
        "continuity_anchor": (
            "Aperture & Pursuit of Wonder 35mm anamorphic contemplative cinema with natural dusk/rain chiaroscuro lighting, "
            "wide anamorphic depth-of-field, and serene atmospheric anti-morph physics across changing tranquil environments, strictly zero text"
        ),
        "forbidden_artifacts": [
            "anime fantasy effects",
            "neon cyberpunk colors",
            "abrupt whip pans",
            "talking human faces",
            "distorted statues",
        ],
        "thumbnail_rule": (
            "Solitary brass bell or stone water basin in misty Kyoto courtyard with single falling raindrop, "
            "2-4 uppercase bold words, high contrast, zero overlay card, 25% margin"
        ),
    },
    "minh_triet_song": {
        "channel_id": "minh_triet_song",
        "channel_slug": "minh-triet-song",
        "niche": "Minh triết Phương Đông & Chủ nghĩa Khắc kỷ (Eastern Philosophy & Stoicism)",
        "competitor_benchmark": "Einzelgänger / Daily Stoic",
        "new_visual_label": "Caravaggio Chiaroscuro Marble & Eastern Mountain Mist Cinema",
        "style_description": (
            "Einzelgänger and Daily Stoic documentary cinematography blending classical European chiaroscuro with Eastern ink-wash mountain landscapes. "
            "Weathered Roman marble busts, ancient bronze armillary spheres, windswept Huangshan pine trees, and drifting mountain fog. "
            "Single directional golden beam cutting through deep shadow (chiaroscuro), rich bronze, charcoal (#18181B), and warm ivory palette. "
            "Monumental stoic gravitas."
        ),
        "subject_physics": (
            "Slow Caravaggio chiaroscuro light-ray progression across weathered stone and bronze, drifting mountain mist particles, "
            "gentle candle flame flicker, and heavy stone tectonic stillness"
        ),
        "camera_grammar": [
            "contemplative slow museum dolly-in toward bust",
            "solemn low-angle architectural tilt-up",
            "composed chiaroscuro lateral tracking pass",
        ],
        "continuity_anchor": (
            "Caravaggio chiaroscuro classical documentary cinematography with single-source golden sunbeams, sculptural depth-of-field, "
            "and weathered material anti-morph physics across shifting philosophical metaphors, strictly zero text"
        ),
        "forbidden_artifacts": [
            "talking or smiling marble statues",
            "modern neon or cars",
            "fast shaky cuts",
            "glitchy CGI effects",
            "floating quote banners",
        ],
        "thumbnail_rule": (
            "Chiaroscuro side-lit marble bust of Marcus Aurelius or lone pine silhouette in mountain mist, "
            "2-4 bold uppercase words, high contrast, zero overlay card, 25% margin"
        ),
    },

    # --------------------------------------------------------------------------
    # Tier-C (High-Short / Low-Long Documentary)
    # --------------------------------------------------------------------------
    "co_the_ke": {
        "channel_id": "co_the_ke",
        "channel_slug": "co-the-ke",
        "niche": "Sức khỏe, tế bào sinh học và giải phẫu 3D (Human Physiology & Medical 3D)",
        "competitor_benchmark": "Nucleus Medical Media / Zack D. Films",
        "new_visual_label": "8K 3D Endoscopic Biomedical Cinematography",
        "style_description": (
            "Nucleus Medical Media and Zack D. Films biomedical 3D endoscopic documentary cinematography. "
            "Bioluminescent arterial reds (#EF4444), cyan capillaries (#06B6D4), and translucent cellular membranes. "
            "Subsurface-scattered biological tissue elasticity, rhythmic pulsatile vascular flow, and clear fiber-optic surgical illumination. "
            "Clinical precision without gore, beautiful physiological micro-worlds."
        ),
        "subject_physics": (
            "Subsurface-scattered wet biological tissue elasticity, rhythmic physiological pulsatile flow, "
            "coherent cellular and molecular motion suspended in translucent fluid plasma media"
        ),
        "camera_grammar": [
            "smooth endoscopic forward lumen dolly",
            "macro anatomical cross-section orbital arc",
            "micro-cellular shallow-DOF focus pull",
        ],
        "continuity_anchor": (
            "Nucleus Medical Media 8K 3D endoscopic biomedical cinematography with clean surgical fiber-optic rim lighting, "
            "shallow optical depth-of-field, and fluid pulsatile anti-morph physics across changing anatomical scales, strictly zero text labels"
        ),
        "forbidden_artifacts": [
            "dry plastic anatomy models",
            "floating anatomical text callouts",
            "sharp robotic camera snaps",
            "gratuitous surgical gore",
            "cartoon organs with eyes",
        ],
        "thumbnail_rule": (
            "Luminous 3D cross-section of a heart valve or red blood cell squeezing through a capillary, "
            "2-4 uppercase bold words, high contrast, zero overlay card, 25% margin"
        ),
    },
    "su_ke_lai": {
        "channel_id": "su_ke_lai",
        "channel_slug": "su-ke-lai",
        "niche": "Lịch sử Việt Nam và thế giới qua góc nhìn điện ảnh sử thi 35mm (35mm Historical Live-Action Docudrama)",
        "competitor_benchmark": "Kingdom of Heaven / Ridley Scott Historical Cinema / Epic History Docudrama",
        "new_visual_label": "35mm Historical Live-Action Docudrama (su_ke_lai_35mm_live_action_v3)",
        "visual_style_id": "su_ke_lai_35mm_live_action_v3",
        "recommended_speed": 1.30,
        "voice_profile_id": "VietNarrator_su_ke_lai",
        "visual_style_lock": (
            "Shot on 35mm Kodak Vision3 500T film, historical battle cinema docudrama, Ridley Scott Kingdom of Heaven aesthetic, "
            "practical period-accurate 10th-11th century Dai Viet lamellar armor and Song Dynasty iron laminar armor, "
            "authentic wet mud, river mist, torchlight chiaroscuro, shallow depth of field, natural film grain, "
            "zero CGI plasticity, zero text in frame."
        ),
        "negative_constraints": (
            "NO 2D cartoon, NO vector illustration, NO woodblock print, NO modern glasses, NO wristwatches, NO neon, "
            "NO glowing magic, NO samurai katana, NO European plate armor, NO AI gibberish text, NO signage, "
            "NO banners with text, NO cherry blossoms, NO plastic skin"
        ),
        "opening_shot_directives": {
            "allowed_text": None,
            "camera": "35mm anamorphic medium-wide establishing shot, slow handheld push-in through low river mist at dawn",
            "lighting": "Cold pre-dawn steel-blue overcast light pierced by warm flickering pitch-pine torches",
            "framing": "10th-11th century Dai Viet commander in weathered bronze-iron lamellar armor on muddy riverbank overlooking misty estuary",
        },
        "anchor_prompts": {
            "protagonist_anchor": (
                "Shot on 35mm Kodak Vision3 500T film, weathered 10th-11th century Dai Viet military commander in practical "
                "laced iron-and-bronze lamellar armor over dark indigo hemp tunic, mud-splattered leather vambraces, "
                "determined expression lit by flickering torchlight chiaroscuro, shallow depth of field, natural film grain, "
                "allowed_text=None, zero text in frame."
            ),
            "world_anchor": (
                "Shot on 35mm Kodak Vision3 500T film, misty estuarine riverbanks of 10th-11th century northern Dai Viet at dusk, "
                "wet riverbank mud, wooden palisade watchtowers, dark timber war junks silhouetted in drifting fog, "
                "Ridley Scott Kingdom of Heaven historical realism, natural film grain, allowed_text=None, zero text in frame."
            ),
            "prop_anchor": (
                "Shot on 35mm Kodak Vision3 500T film, close-up of practical 10th-11th century iron-tipped ironwood river stakes, "
                "forged bronze-hilted Dai Viet straight sword, and Song Dynasty iron laminar shield resting in wet mud beside "
                "burning pitch torches, shallow depth of field, natural film grain, allowed_text=None, zero text in frame."
            ),
        },
        "style_description": (
            "Locked V3 35mm Historical Live-Action Docudrama (su_ke_lai_35mm_live_action_v3) shot on Kodak Vision3 500T film "
            "in Ridley Scott Kingdom of Heaven aesthetic: practical period-accurate 10th-11th century Dai Viet lamellar armor and "
            "Song Dynasty iron laminar armor, authentic wet mud, drifting river mist, torchlight chiaroscuro, shallow depth of field, "
            "natural 35mm film grain, zero CGI plasticity, and strictly zero text in frame."
        ),
        "subject_physics": (
            "Authentic water ripple and tidal current physics around submerged iron-tipped stakes, heavy wet cloth and mud-caked "
            "lamellar armor weight, realistic torch ember drift and dense battlefield mist, natural human micro-expressions"
        ),
        "camera_grammar": [
            "35mm anamorphic low-angle tracking shot through river mist",
            "handheld shallow-DOF close-up on mud-caked armor and torchlit faces",
            "sweeping aerial crane over timber fleet formation in fog",
        ],
        "continuity_anchor": (
            "Locked V3 su_ke_lai_35mm_live_action_v3 35mm Kodak Vision3 500T historical live-action docudrama with practical "
            "10th-11th century Dai Viet lamellar and Song iron laminar armor, wet mud, river mist, torchlight chiaroscuro, "
            "natural film grain, zero CGI plasticity, zero text in frame"
        ),
        "forbidden_artifacts": [
            "2D cartoon or vector illustration",
            "woodblock print or parchment paper texture",
            "modern glasses or wristwatches",
            "samurai katana or European plate armor",
            "AI gibberish text, signage, or banners with text",
            "plastic CGI skin or glowing magic",
        ],
        "thumbnail_rule": (
            "35mm film close-up of mud-streaked Dai Viet commander in torchlit lamellar armor before misty river battle, "
            "2-4 bold uppercase words, high contrast, zero overlay card, 25% margin"
        ),
    },
    "ho_so_ky_la": {
        "channel_id": "ho_so_ky_la",
        "channel_slug": "ho-so-ky-la",
        "niche": "Bí ẩn, hồ sơ kỳ lạ và giám định pháp y (Forensic Mysteries & Unsolved Archives)",
        "competitor_benchmark": "LEMMiNO / Fern",
        "new_visual_label": "Atmospheric Noir 3D Forensic Crime-Scene Diorama",
        "style_description": (
            "LEMMiNO atmospheric noir 3D forensic documentary cinematography. Midnight charcoal (#0B0F19), desaturated slate, "
            "and cold rainy mist pierced by a single 45-degree desk lamp or flashlight beam. Archival evidence dossiers, "
            "red investigation thread connecting evidence pegs on cork, crime-scene diorama cutaways with forensic markers, "
            "and moody rainy window reflections. Intellectual, eerie, and deeply atmospheric."
        ),
        "subject_physics": (
            "Slow volumetric fog and rain particle drift across wet asphalt, realistic wet surface specular reflections, "
            "subtle physical tension in taut archival evidence threads, and chiaroscuro shadow cast from swinging light sources"
        ),
        "camera_grammar": [
            "brooding noir crane descent through mist",
            "slow forensic macro push-in toward evidence",
            "steady lateral diorama tracking pass across crime scene",
        ],
        "continuity_anchor": (
            "LEMMiNO atmospheric noir 3D forensic documentary cinematography in deep midnight slate palette with selective crimson/amber rim light, "
            "shallow forensic depth-of-field, and atmospheric anti-morph physics across shifting archival scales, strictly zero readable text"
        ),
        "forbidden_artifacts": [
            "cheap horror jumpscares",
            "gratuitous blood or gore",
            "neon cyberpunk colors",
            "gibberish newspaper headlines",
            "distorted screaming faces",
        ],
        "thumbnail_rule": (
            "Dark noir silhouette under a single harsh spotlight with red evidence thread or mysterious locked door, "
            "2-4 uppercase bold words, high contrast, zero overlay card, 25% margin"
        ),
    },
    "ban_do_quyen_luc": {
        "channel_id": "ban_do_quyen_luc",
        "channel_slug": "ban-do-quyen-luc",
        "niche": "Địa chính trị, kinh tế tài nguyên và hải trình chiến lược (Geopolitics & Strategic Chokepoints)",
        "competitor_benchmark": "RealLifeLore / Johnny Harris / Fern Documentary",
        "new_visual_label": "3-Pillar Photorealistic Geopolitical Documentary & 4-Mode Storytelling Cinema (ban_do_quyen_luc_4styles_photoreal_v3)",
        "visual_style_id": "ban_do_quyen_luc_4styles_photoreal_v3",
        "recommended_speed": 1.15,
        "voice_profile_id": "VietNarrator_ban_do_quyen_luc",
        "style_description": (
            "Three-pillar photorealistic geopolitical documentary cinematography fused with a 4-mode visual storytelling system "
            "(ban_do_quyen_luc_4styles_photoreal_v3): (1) True-color 3D orbital satellite relief, straits, and open-pit resource topography; "
            "(2) 100mm shallow-DOF macro engineering and industrial process mechanisms; (3) On-site maritime, smelting, port logistics, "
            "and geopolitical field photography with diverse per-beat locations, materials, and natural/industrial lighting "
            "(strictly zero repetitive tabletop desk or clamp props across beats). Paired in 2K post-compositing with CACH_1_HERO_STAMP, "
            "CACH_2_SPLIT_COMPARE, CACH_3_DOSSIER_LIST, and CACH_4_CINEMATIC_PACING."
        ),
        "subject_physics": (
            "Real-world geophysical relief lighting, authentic 100mm macro industrial metallurgy and fluidics, "
            "oceanic vessel wakes through narrow chokepoints, and clean 2K overscan camera pacing (zoom/pan + key-beat I2V motion)"
        ),
        "camera_grammar": [
            "orbital satellite-to-strait zoom descent",
            "100mm macro engineering rack-focus",
            "on-site industrial & maritime lateral tracking pass",
            "2K overscan dynamic camera pacing (zoom_in_center / pan_left_to_right / xfade=fade)",
        ],
        "continuity_anchor": (
            "RealLifeLore & Johnny Harris 3-pillar photorealistic geopolitical documentary cinematography combining orbital geography, "
            "100mm industrial macro, and field logistics photography with per-beat environmental diversity and 4-mode 2K storytelling pacing, "
            "strictly zero text, zero map labels, and zero repetitive tabletop props in raw Flow frames"
        ),
        "forbidden_artifacts": [
            "flat 2D Google Maps pins or vector cartoons",
            "repetitive walnut tabletop desk or crimson steel clamp props",
            "sci-fi holographic radar rings or glowing neon HUDs",
            "ships sliding onto dry land or warping coastlines",
            "AI gibberish country names or overlaid letters in raw Flow images",
        ],
        "thumbnail_rule": (
            "Flow-native high-CTR geopolitical conflict or bottleneck photography matching the episode topic (zero tabletop clamps), "
            "2-4 bold uppercase Vietnamese words in clean dark negative space, high contrast, zero offline PIL overlay card, < 2MB"
        ),
    },
    "loi_sang_soi": {
        "channel_id": "loi_sang_soi",
        "channel_slug": "loi-sang-soi",
        "niche": "Dụ ngôn Kinh Thánh, lịch sử văn minh & bài học nhân văn (Biblical Parables & Classical Civilization)",
        "competitor_benchmark": "BibleProject / Caravaggio Chiaroscuro",
        "new_visual_label": "Caravaggio Chiaroscuro Golden-Hour Ancient Parable & Oil-on-Parchment Cinema",
        "style_description": (
            "BibleProject narrative depth combined with Caravaggio chiaroscuro golden-hour oil-on-parchment cinematography. "
            "Ancient limestone arches, terracotta oil lamps with warm flickering wicks, olive groves in twilight, weathered clay tablets, "
            "and golden dust motes dancing in dramatic cathedral sunbeams. Warm ochre, olive green, deep burgundy, and burnished bronze palette. "
            "Solemn, sacred, and emotionally radiant."
        ),
        "subject_physics": (
            "Soft candle and terracotta oil lamp flame flicker, gentle desert breeze shifting fine sand particles, "
            "slow atmospheric dust mote suspension in golden light shafts, and realistic cloth drapery folds"
        ),
        "camera_grammar": [
            "golden-hour cathedral light dolly push-in",
            "slow tilt-down from ancient archway to clay lamp",
            "gentle lateral drift across stone courtyard",
        ],
        "continuity_anchor": (
            "Caravaggio chiaroscuro and BibleProject classical parable cinematography with golden-hour single-source sunbeams, "
            "sculptural depth-of-field, and weathered material anti-morph physics across ancient architectural settings, strictly zero text"
        ),
        "forbidden_artifacts": [
            "modern clothing or watches",
            "talking lip movement",
            "cheap CGI halos or glowing angels",
            "gibberish scripture lettering",
            "plastic props",
        ],
        "thumbnail_rule": (
            "Single glowing clay oil lamp on weathered stone in dark room with radiant golden beam, "
            "2-4 bold uppercase words, high contrast, zero overlay card, 25% margin"
        ),
    },

    # --------------------------------------------------------------------------
    # Tier-D (Psychology, Career, AI, Night Fables)
    # --------------------------------------------------------------------------
    "nao_luoi": {
        "channel_id": "nao_luoi",
        "channel_slug": "nao-luoi",
        "niche": "Khoa học thần kinh về Dopamine, thói quen & sự tập trung (Neuroscience of Habits & Dopamine)",
        "competitor_benchmark": "Kurzgesagt Habit Science / Huberman Lab / The Paint Explainer",
        "new_visual_label": "Bioluminescent Neural Synapse & High-Contrast Behavioral Split-Screen",
        "style_description": (
            "Kurzgesagt and Huberman Lab neuroscience cinematography with high-contrast scientific visual storytelling. "
            "Bioluminescent electric cyan (#38BDF8) and dopamine amber (#F59E0B) signal pulses traveling across intricate 3D neural synapses "
            "and axonal networks, juxtaposed with clean 35mm human behavioral moments (eyes focusing, fingers hesitating over smartphone screen). "
            "Deep slate background (#0F172A), crisp scientific depth of field, and dynamic neurotransmitter cascades."
        ),
        "subject_physics": (
            "Coherent bio-electrical signal pulses traveling along 3D neural axons and synaptic clefts, "
            "micro-vesicle neurotransmitter fusion, and calm realistic human body language in focus environments"
        ),
        "camera_grammar": [
            "sweeping 3D synaptic orbital arc",
            "diving cortex macro zoom-in",
            "calm 35mm shallow-DOF focus push-in",
        ],
        "continuity_anchor": (
            "Kurzgesagt & Huberman Lab high-contrast 3D neuroscience and behavioral cinematography with bioluminescent cyan/amber lighting, "
            "optical shallow depth-of-field, and bio-electrical anti-morph physics across shifting cognitive scales, strictly zero text"
        ),
        "forbidden_artifacts": [
            "cartoon brain with silly cartoon eyes",
            "strobing seizure flashes",
            "flat MS-Paint stick figures",
            "gibberish medical charts",
            "distorted human faces",
        ],
        "thumbnail_rule": (
            "Bioluminescent glowing neural synapse firing an electric amber spark against deep navy void, "
            "2-4 bold uppercase words, high contrast, zero overlay card, 25% margin"
        ),
    },
    "thuong_cho_kheo": {
        "channel_id": "thuong_cho_kheo",
        "channel_slug": "thuong-cho-kheo",
        "niche": "Tâm lý tình cảm, giao tiếp trắc ẩn & gắn kết con người (Compassionate Relationships & Attachment Psychology)",
        "competitor_benchmark": "The School of Life / Cinema Therapy",
        "new_visual_label": "Warm Editorial Watercolor & Golden-Hour Anamorphic Emotional Storytelling",
        "style_description": (
            "The School of Life and Cinema Therapy warm editorial 35mm anamorphic cinematography with subtle watercolor aesthetic undertones. "
            "Warm 3000K tungsten lamp glow, soft afternoon window rain refraction, steaming ceramic tea cups on warm wooden tables, "
            "and quiet shared human spaces. Kodak Vision3 500T warm grading, soft coral (#E05A67), warm amber, and deep earth tones. "
            "Deep emotional empathy and visual intimacy without melodrama."
        ),
        "subject_physics": (
            "Subtle authentic human micro-expressions and posture, natural breathing motion, gentle hand gestures, "
            "warm steam rising from ceramic cups, and soft window rain droplet condensation"
        ),
        "camera_grammar": [
            "empathetic slow 35mm table-level push-in",
            "intimate over-the-shoulder focus pull",
            "gentle lateral drift across shared living space",
        ],
        "continuity_anchor": (
            "Intimate 35mm live-action film cinematography with Kodak Vision3 500T color grading, warm 3000K tungsten bokeh, "
            "shallow f/1.8 depth-of-field, and quiet emotional anti-morph realism across changing character interactions, "
            "strictly zero text, no speaking or lip movement"
        ),
        "forbidden_artifacts": [
            "talking mouth movement or lip sync",
            "exaggerated soap-opera grimacing",
            "flat 2D cartoon doodles",
            "cold fluorescent hospital lighting",
            "distorted hands or extra fingers",
        ],
        "thumbnail_rule": (
            "Two silhouette figures seated across warm wooden table with glowing amber lamp between them, "
            "2-4 uppercase bold words, high contrast, zero overlay card, 25% margin"
        ),
    },
    "nghe_song_sot": {
        "channel_id": "nghe_song_sot",
        "channel_slug": "nghe-song-sot",
        "niche": "Chiến lược sự nghiệp, đòn bẩy công sở & thích nghi thời đại AI (Workplace Leverage & Career Strategy)",
        "competitor_benchmark": "Wall Street Journal / Harvard Business Review / Casgains",
        "new_visual_label": "Architectural Corporate Glass & Isometric Strategic Chessboard Cinematography",
        "style_description": (
            "Wall Street Journal and Harvard Business Review editorial photojournalism and architectural corporate cinematography. "
            "Sleek skyscraper glass reflections, high-contrast chiaroscuro shadows across modern executive boardrooms, "
            "polished dark granite floors, and metaphorical geometric brass chess pieces on an architectural marble grid. "
            "Deep charcoal (#1E293B), cool slate steel, and warm brass accents. Poised, strategic, and uncompromisingly professional."
        ),
        "subject_physics": (
            "Poised executive body language without speaking, crisp architectural light-and-shadow geometry across glass, steel, "
            "and dark wood, smooth precision mechanical balance, and subtle skyline motion"
        ),
        "camera_grammar": [
            "authoritative WSJ architectural lateral dolly",
            "low-angle executive boardroom push-in",
            "composed wide architectural pull-back reveal",
        ],
        "continuity_anchor": (
            "WSJ & HBR high-contrast editorial photojournalism cinematography with charcoal slate palette, warm directional brass lighting, "
            "f/2.0 shallow depth-of-field, and architectural anti-morph stability across shifting professional contexts, strictly zero text"
        ),
        "forbidden_artifacts": [
            "cartoon money bags",
            "talking lip movement",
            "warping office furniture",
            "cheap corporate clip-art handshakes",
            "cluttered messy desks",
        ],
        "thumbnail_rule": (
            "Poised dark silhouette standing before floor-to-ceiling glass skyline window with solitary brass chess king on marble, "
            "2-4 uppercase bold words, high contrast, zero overlay card, 25% margin"
        ),
    },
    "ai_binh_dan": {
        "channel_id": "ai_binh_dan",
        "channel_slug": "ai-binh-dan",
        "niche": "Công nghệ AI ứng dụng, tự động hóa & năng suất làm việc (Applied AI & Everyday Productivity)",
        "competitor_benchmark": "Jeff Su / Fireship / Matt Wolfe",
        "new_visual_label": "Sleek Dark-Mode Glassmorphism UI Telemetry & Tactile Productivity Desk Macro",
        "style_description": (
            "Sleek dark-mode glassmorphism and tactile productivity desk cinematography inspired by Jeff Su and Fireship. "
            "Matte obsidian desk setup, frosted glass UI panels with subtle cyan (#06B6D4) and violet telemetry pulses, "
            "high-end mechanical keyboard with tactile matte keycaps, and warm brass desk lamp accent. Razor-sharp f/2.0 macro focus, "
            "clean geometric data streams without readable text, and modern tech elegance."
        ),
        "subject_physics": (
            "Clean frosted glass UI light diffusion, subtle glowing data telemetry pulse propagation, "
            "mechanical keyboard switch tactile actuation, and crisp specular light glints across anodized aluminum hardware"
        ),
        "camera_grammar": [
            "smooth diagonal desk macro push-in",
            "sleek floating glassmorphism UI pan",
            "low-angle mechanical workspace lateral glide",
        ],
        "continuity_anchor": (
            "Jeff Su & Fireship sleek dark-mode glassmorphism UI and tactile workspace cinematography in obsidian and cyan palette, "
            "shallow f/2.0 optical depth-of-field, and rigid anti-morph hardware physics across tech environments, "
            "strictly zero readable software text or fake code lines"
        ),
        "forbidden_artifacts": [
            "fake Matrix green falling code",
            "cheesy glowing 3D humanoid robots",
            "cluttered messy wires",
            "warping UI text or icons",
            "cheap blue sci-fi holograms",
        ],
        "thumbnail_rule": (
            "Sleek glowing glassmorphic interface card floating above dark minimalist mechanical desk setup, "
            "2-4 bold uppercase words, high contrast, zero overlay card, 25% margin"
        ),
    },
    "tam_tinh_dem": {
        "channel_id": "tam_tinh_dem",
        "channel_slug": "tam-tinh-dem",
        "niche": "Truyện ngụ ngôn tĩnh thức, nhân quả & chiêm nghiệm chữa lành (Nocturnal Mindfulness & Soul-Healing Fables)",
        "competitor_benchmark": "Pursuit of Wonder / Studio Ghibli Nocturnal",
        "new_visual_label": "Atmospheric Midnight Velvet & Glowing Golden Lantern Fable Cinematography",
        "style_description": (
            "Pursuit of Wonder and Studio Ghibli nocturnal cinematography. Deep velvet indigo (#0B1026) night skies dusted with "
            "soft out-of-focus starlight, gentle golden lanterns (#F59E0B) glowing softly by a tranquil lakeside or old cottage window, "
            "fireflies drifting over calm water, and gentle nocturnal breeze rustling willow branches. Warm 2200K amber glow against "
            "cool midnight blue, serene, deeply comforting, and soul-healing."
        ),
        "subject_physics": (
            "Soft nocturnal wind swaying willow leaves and lantern cords, gentle water ripple reflections of golden light, "
            "drifting organic firefly light paths, and soft dissipation of warm lantern glow in cool midnight air"
        ),
        "camera_grammar": [
            "slow weightless drift across moonlit water",
            "gentle upward tilt toward golden glowing window",
            "composed wide nocturnal sanctuary hold",
        ],
        "continuity_anchor": (
            "Studio Ghibli nocturnal & Pursuit of Wonder atmospheric fable cinematography with deep velvet indigo palette and "
            "warm glowing golden lantern light, shallow cinematic depth-of-field, and tranquil atmospheric anti-morph physics "
            "across peaceful nocturnal settings, strictly zero text"
        ),
        "forbidden_artifacts": [
            "harsh daylight or fluorescent lighting",
            "fast erratic camera movements",
            "scary horror elements",
            "talking mouth movement",
            "garish neon colors",
        ],
        "thumbnail_rule": (
            "Single warm golden paper lantern glowing softly on tranquil midnight lake reflecting moonlight, "
            "2-4 uppercase bold words, high contrast, zero overlay card, 25% margin"
        ),
    },
}

# ==============================================================================
# 4. ALL 20 VIETNAMESE CHANNELS — MINIMALIST ICONIC LOGO PROMPTS
#    100% zero text, zero letters, zero numbers, 25% empty margin around edges.
# ==============================================================================
VN_CHANNEL_LOGO_PROMPTS: Dict[str, str] = {
    "tui_tien": (
        "Minimalist consumer economics emblem centered on a solid ivory background (#FAF8F5). "
        "A bold isometric cross-section of a circular coin sliced cleanly open to reveal deep emerald green (#1B4931) "
        "architectural layers surrounding a bright crimson red (#D9381E) diamond core. "
        "Pure flat vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "banh_rang": (
        "Minimalist macroeconomics engineering emblem centered on a solid warm cream background (#F7F2EB). "
        "Two interlocking dark slate navy (#1E293B) precision gear cogs framing a bold industrial orange (#EA580C) "
        "structural truss triangle at the center. "
        "Pure Swiss graphic vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "luat_doi_thuong": (
        "Minimalist legal civil law emblem centered on a solid newsprint ivory background (#F4EFE6). "
        "A bold midnight navy (#1E293B) magnifying glass loupe centered over balanced justice scales, "
        "accented with a single vivid vermilion red (#E63946) circular wax seal dot at the fulcrum. "
        "Pure editorial vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "la_ban_hoc_thuat": (
        "Minimalist cognitive learning and academic compass emblem centered on a solid deep navy background (#0F172A). "
        "A bold glowing golden amber (#F59E0B) compass needle levitating inside a crisp cyan (#38BDF8) geometric circle "
        "with four quadrant ticks. "
        "Pure flat vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "luat_ngam": (
        "Minimalist mass psychology network emblem centered on a solid dark slate background (#111827). "
        "A bold geometric triangle of three crisp ivory white (#F3F4F6) node spheres connected from above "
        "by taut glowing crimson red (#DC2626) marionette control lines meeting at a single apex diamond. "
        "Pure noir vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "ua_sao_vay": (
        "Minimalist science curiosity emblem centered on a solid charcoal slate background (#1E293B). "
        "A bold glowing electric amber (#F59E0B) stylized question-mark spiral unfolding into an interlocking "
        "geometric cog wheel in surgical white (#FAFAFA). "
        "Pure flat vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "dia_com": (
        "Minimalist culinary chemistry emblem centered on a solid warm linen background (#FDFBF7). "
        "A stylized clean cast-iron charcoal ring (#18181B) enclosing a vibrant terracotta flame (#EA580C) "
        "cradling a golden olive oil droplet (#EAB308) at the center. "
        "Pure culinary vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "vu_tru_ti_hon": (
        "Minimalist astrophysics emblem centered on a solid void-black background (#050814). "
        "A bold circular black hole silhouette encircled by a razor-sharp glowing solar gold (#FBBF24) photon ring "
        "and intersected diagonally by a sleek electric cyan (#38BDF8) orbital arc. "
        "Pure flat vector symbol, extreme contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "chanh_niem_ke": (
        "Minimalist Zen mindfulness emblem centered on a solid warm rice-paper cream background (#F7F4EB). "
        "A bold charcoal sumi-e ink enso circle (#1E293B) enclosing a single pristine falling water droplet "
        "rippling into concentric rings, accented with a warm gold (#D4AF37) leaf. "
        "Pure meditative vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "minh_triet_song": (
        "Minimalist stoic philosophy emblem centered on a solid midnight navy background (#0F172A). "
        "A bold vertical emblem split down the center: left half a fluted ivory (#E2E8F0) Greco-Roman marble column, "
        "right half a segmented emerald-sage bamboo stalk, topped by a warm gold (#F59E0B) crescent arc. "
        "Pure flat vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "co_the_ke": (
        "Minimalist biomedical physiology emblem centered on a solid deep navy background (#0A192F). "
        "A stylized 3D vector biconcave red blood cell in rich arterial crimson (#EF4444) framed inside a "
        "clean circular glowing cyan (#06B6D4) capillary vessel ring. "
        "Pure scientific vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "su_ke_lai": (
        "Minimalist historical warfare emblem centered on a solid dark stone background (#1C1917). "
        "A bold stylized bronze shield silhouette (#B45309) intersected diagonally by an ancient dragon spear "
        "in burnished steel with a glowing crimson torch ember (#DC2626) at the crest. "
        "Pure epic historical vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "ho_so_ky_la": (
        "Minimalist forensic mystery emblem centered on a solid pitch-black background (#0B0F19). "
        "A crisp circular white (#F1F5F9) fingerprint whorl silhouette sliced diagonally by a sharp 45-degree "
        "spotlight cone illuminating a single crimson red (#E11D48) central evidence node. "
        "Pure noir vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "ban_do_quyen_luc": (
        "Minimalist maritime geopolitics emblem centered on a solid deep navy background (#0F172A). "
        "Two bold coastal landmass silhouettes in sand white (#E2E8F0) forming a narrow oceanic strait "
        "with a vivid crimson red (#DC2626) directional navigation arrow passing cleanly through the gap. "
        "Pure cartographic vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "loi_sang_soi": (
        "Minimalist classical parable emblem centered on a solid parchment cream background (#F8F4E8). "
        "A stylized ancient clay oil lamp in warm terracotta (#C2410C) with a glowing imperial gold flame (#F59E0B) "
        "radiating seven clean concentric light arcs above. "
        "Pure sacred vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "nao_luoi": (
        "Minimalist cognitive neuroscience emblem centered on a solid dark navy background (#0F172A). "
        "A bold stylized brain silhouette in cobalt blue (#3B82C4) with a glowing bioluminescent amber (#F59E0B) "
        "synaptic spark discharging across the prefrontal cortex. "
        "Pure scientific vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "thuong_cho_kheo": (
        "Minimalist compassionate psychology emblem centered on a solid warm cream background (#FDFBF7). "
        "A bold continuous espresso-charcoal (#382216) line forming two facing minimalist profile silhouettes "
        "whose shared negative space creates a warm coral rose (#E05A67) heart bridge in the center. "
        "Pure clean vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "nghe_song_sot": (
        "Minimalist career strategy emblem centered on a solid light parchment background (#F8F6F0). "
        "A bold deep navy (#2C3E50) mechanical lever resting on a sharp triangle fulcrum, lifting a "
        "glowing imperial gold (#E5A93C) geometric cube effortlessly upward. "
        "Pure editorial vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "ai_binh_dan": (
        "Minimalist applied technology emblem centered on a solid obsidian background (#0F172A). "
        "A glowing cyan (#06B6D4) glassmorphic hexagonal chip framed by clean geometric circuit traces "
        "with a bright violet (#8B5CF6) core processor dot. "
        "Pure tech vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
    "tam_tinh_dem": (
        "Minimalist nocturnal peace emblem centered on a solid velvet midnight indigo background (#0B1026). "
        "A serene glowing golden paper lantern (#F59E0B) suspended over a calm water ripple arc "
        "reflecting a silver crescent moon in the darkness. "
        "Pure soothing nocturnal vector symbol, high contrast, 25% empty margin around all edges, "
        "strictly no text, no letters, no words, no numbers, pure icon."
    ),
}


# ==============================================================================
# 5. HELPER FUNCTIONS & VALIDATORS
# ==============================================================================
def get_vn_flow_formula(channel_id_or_slug: str) -> Dict[str, Any]:
    """Retrieve the VN Flow Video formula dictionary for a channel.

    Supports both underscore (`tui_tien`) and hyphen (`tui-tien`) lookup keys.
    """
    key = channel_id_or_slug.strip().lower()
    underscore_key = key.replace("-", "_")
    hyphen_key = key.replace("_", "-")

    if underscore_key in VN_FLOW_VIDEO_FORMULAS:
        return VN_FLOW_VIDEO_FORMULAS[underscore_key]

    for formula in VN_FLOW_VIDEO_FORMULAS.values():
        if formula.get("channel_slug") == hyphen_key or formula.get("channel_id") == underscore_key:
            return formula

    return VN_FLOW_VIDEO_FORMULAS["tui_tien"]


def build_vn_channel_motion_prompt(
    channel_id_or_slug: str,
    shot_action: str,
    camera_move: str | None = None,
    is_interpolation: bool = True,
    scene_anchor: str | None = None,
) -> str:
    """Compile the deterministic 4-component 70/30 Google Flow motion prompt for a Vietnamese channel.

    Uses per-shot `scene_anchor` when provided so scene-specific environments stay 100% locked
    without injecting off-topic props from other scenes.
    """
    spec = get_vn_flow_formula(channel_id_or_slug)
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


def build_vn_reference_keyframe_prompt(
    channel_id_or_slug: str,
    next_visual_state: str,
    use_camera_angle_wrapper: bool = False,
    scene_anchor: str | None = None,
) -> str:
    """Wrap destination keyframe prompt using Google's official Story Sketch / Shot Explorer formula."""
    spec = get_vn_flow_formula(channel_id_or_slug)
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


def validate_vn_shot_visual_diversity(
    shots: List[Dict[str, Any]],
    max_same_environment_run: int = 2,
    max_jaccard: float = 0.72,
) -> List[str]:
    """Detect visual repetition across consecutive shots.

    Checks:
    1. Pairwise Jaccard word-token similarity between consecutive shots (<= max_jaccard).
    2. Consecutive runs of identical environment or scene anchors (<= max_same_environment_run).

    Args:
        shots: List of shot dictionaries.
        max_same_environment_run: Maximum allowed consecutive shots sharing identical environment tags.
        max_jaccard: Maximum allowed Jaccard token overlap between consecutive shots.

    Returns:
        List of warning/violation strings.
    """
    if len(shots) < 2:
        return []

    violations: List[str] = []

    def _extract_tokens(shot: Dict[str, Any]) -> set[str]:
        text_parts: List[str] = []
        for key in ("visual", "start_visual", "end_visual", "subject_motion", "scene_anchor"):
            val = shot.get(key)
            if val and isinstance(val, str):
                text_parts.append(val)
        if not text_parts:
            for k, val in shot.items():
                if isinstance(val, str) and k not in ("shot_id", "id", "chain_mode", "stage", "camera_verb"):
                    text_parts.append(val)
        full_text = " ".join(text_parts).lower()
        words = re.findall(r"\b[a-z0-9_]{3,}\b", full_text)
        return set(words)

    # 1. Jaccard token overlap between adjacent shots
    for i in range(len(shots) - 1):
        shot_a = shots[i]
        shot_b = shots[i + 1]

        tokens_a = _extract_tokens(shot_a)
        tokens_b = _extract_tokens(shot_b)

        if not tokens_a or not tokens_b:
            continue

        intersection = tokens_a & tokens_b
        union = tokens_a | tokens_b

        if not union:
            continue

        jaccard = len(intersection) / len(union)
        if jaccard > max_jaccard:
            id_a = shot_a.get("shot_id") or f"shot_{i+1}"
            id_b = shot_b.get("shot_id") or f"shot_{i+2}"
            violations.append(
                f"Consecutive shots {id_a} and {id_b} exceed visual token similarity threshold: "
                f"Jaccard={jaccard:.3f} > {max_jaccard:.2f}"
            )

    # 2. Maximum consecutive identical environment run check
    current_env = None
    current_run = 0
    for i, shot in enumerate(shots):
        env = (
            shot.get("scene_anchor")
            or shot.get("environment")
            or shot.get("location")
            or shot.get("visual_environment")
        )
        if env and isinstance(env, str):
            env_normalized = env.strip().lower()
            if env_normalized == current_env:
                current_run += 1
                if current_run > max_same_environment_run:
                    shot_id = shot.get("shot_id") or f"shot_{i+1}"
                    violations.append(
                        f"Shot {shot_id} exceeds maximum consecutive environment run "
                        f"({current_run} > {max_same_environment_run}) for environment '{env}'"
                    )
            else:
                current_env = env_normalized
                current_run = 1
        else:
            current_env = None
            current_run = 0

    return violations


__all__ = [
    "FLOW_FRAME_CONTROL_MODES",
    "RETENTION_SHOT_BLUEPRINTS",
    "UNIVERSAL_STABILITY_GUARDRAILS",
    "VN_CHANNEL_LOGO_PROMPTS",
    "VN_FLOW_VIDEO_FORMULAS",
    "build_vn_channel_motion_prompt",
    "build_vn_reference_keyframe_prompt",
    "get_vn_flow_formula",
    "validate_vn_shot_visual_diversity",
]
