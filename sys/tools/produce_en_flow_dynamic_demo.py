#!/usr/bin/env python3
"""Professional Audio-First Beat-Locked Seamless Google Flow Video Pipeline (V3).

Implements:
1. 18-Channel Brand Emblem Regeneration (`--regenerate-logos`):
   - Generates 100% zero-text 1:1 channel brand emblems on Google Flow (`BELUGA`),
     applies 1.05x edge overscan crop (eliminating raw Flow corner sparkles), and writes
     `avatar_800x800.png`, `logo.png`, and `watermark_150x150.png` into `sys/channels/<id>/assets/`.
2. Credit-Gated Dynamic Google Flow Video Pipeline (`--build-demo`):
   - Priority 1 (`dynamic_flow_chain`, whenever ANY profile in `CreditLedger` has `>= 7` credits):
     * Audio-First synthesis (`edge-tts` WordBoundary + competitor breath pauses + `-11.0 LUFS / -1.0 dBTP`)
       locks exact millisecond durations for every shot before visual generation.
     * Reference-Conditioned Keyframes (`maseQ` upload + `reference_media_ids` via `FlowVideoChainOrchestrator`)
       lock geometry within each continuous scene group so `nprQif` (`omni_flash` 4s/6s/8s) interpolates
       true physical motion without AI morphing slop.
     * Hybrid Continuity Stitching:
       - `0.0s` frame-accurate joins (`trim=start_frame=1`) inside continuous scene chains.
       - `0.24s` optical `xfade=transition=fade` across Act/Scene pivots aligned right onto narrator breath pauses.
       - `1.05x` edge overscan crop on all clips to eliminate Google Flow's raw bottom-right `✦` mark.
   - Priority 2 (`zero_credit_slide_fallback`, ONLY when 100% of profiles have `< 7` credits):
     * Supersampled zero-snap `zoompan` + `xfade` fallback (`render_vn_frame_video`).
3. Frame & Caption Packaging:
   - `9:16` Short (`1080x1920@30fps`): Vietnamese-standard 1-word alternating Red (`#FF3B30`) & Yellow (`#FFE600`)
     kinetic `.ass` subtitles (`MarginV=400`) + rounded `100x100` channel emblem at `W-w-24:H-h-56`.
   - `16:9` Long (`1920x1080@30fps`): Clean widescreen cinema frame + sidecar `.srt` + rounded `100x100`
     channel emblem at `W-w-36:H-h-36`.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from PIL import Image

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(ROOT_DIR), str(SYS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sys.flow_video.models import (  # noqa: E402
    ChainMode,
    ScenePairSpec,
    VideoChainSpec,
    VideoClipTask,
)
from sys.flow_video.orchestrator import FlowVideoChainOrchestrator  # noqa: E402
from sys.flow_video.stitcher import probe_video_clip  # noqa: E402

from channels.en_flow_video_formulas import (  # noqa: E402
    EN_CHANNEL_LOGO_PROMPTS,
    build_channel_motion_prompt,
    build_reference_keyframe_prompt,
)
from flow_cdp.cdp_direct_client import PROFILES  # noqa: E402
from flow_cdp.credit_ledger import MIN_VIDEO_CREDITS, CreditLedger  # noqa: E402
from flow_cdp.persistent_pool import PersistentWorkerPool  # noqa: E402
from flow_cdp.process_manager import get_process_manager  # noqa: E402
from tools.rebuild_en_from_competitor_frames import (  # noqa: E402
    COMPETITOR_VIDEO_TARGETS,
    build_vn_kinetic_1word_ass_and_srt,
    make_channel_watermark,
    render_vn_frame_video,
    synthesize_beats_with_competitor_cadence,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("produce_en_flow_dynamic_demo")

V3_DEMOS_ROOT = ROOT_DIR / "sys/runs/en_flow_v3_demos"


# ---------------------------------------------------------------------------
# Curated High-Retention V3 Dynamic Flow Video Demo Specs (~30s 9:16 & ~60s 16:9)
# ---------------------------------------------------------------------------

CURATED_V3_DEMO_SPECS: dict[str, dict[str, Any]] = {
    "en-wallet-anatomy:9x16": {
        "channel_slug": "en-wallet-anatomy",
        "aspect": "9:16",
        "title": "Why Menu Prices Hide Dollar Signs — And How Your Brain Pays 12% More",
        "voice": "en-US-AndrewNeural",
        "shots": [
            {
                "shot_id": "S01",
                "scene_group": "G1",
                "continues_prev": False,
                "scene_anchor": (
                    "Upscale warmly lit walnut restaurant dining table photographed on 35mm cinema glass at f/2.0, "
                    "soft warm candlelight bokeh, tactile cream linen menu card with abstract embossed gold bars and strictly zero readable text or digits"
                ),
                "narration": "Ever notice how upscale restaurants quietly erased every dollar sign from their menus?",
                "pause_after_sec": 0.28,
                "camera_verb": "Smooth 35mm macro dolly push-in",
                "start_visual": (
                    "Realistic 35mm WSJ consumer-economics documentary close-up on a dark walnut restaurant dining table with warm candlelight bokeh. "
                    "An open textured cream linen menu card displays clean abstract embossed horizontal lines while three small brushed-brass currency emblems "
                    "lift off the paper surface into warm air. Shallow depth of field f/2.0, photorealistic, strictly zero readable words, letters, or numbers."
                ),
                "end_visual": (
                    "On the same candlelit walnut dining table, the three brushed-brass currency emblems dissolve into fine golden dust motes above the blank cream linen menu "
                    "as a sleek brass magnifying loupe glides smoothly into frame, photorealistic 35mm macro, strictly zero text or numbers."
                ),
                "subject_motion": (
                    "the three brushed-brass currency emblems lift gently off the linen card and dissolve into golden dust motes as a brass magnifying loupe glides inward"
                ),
            },
            {
                "shot_id": "S02",
                "scene_group": "G1",
                "continues_prev": True,
                "scene_anchor": (
                    "Upscale warmly lit walnut restaurant dining table photographed on 35mm cinema glass at f/2.0, "
                    "soft warm candlelight bokeh, tactile physical leather bill folder and crisp green paper notes with zero readable text"
                ),
                "narration": "Cornell researchers tested this exact trick on diners—and spending jumped twelve percent.",
                "pause_after_sec": 0.36,
                "camera_verb": "Smooth lateral tabletop tracking glide",
                "end_visual": (
                    "Panning slightly across the same candlelit walnut restaurant table beside the linen menu, a black leather check folder opens to reveal "
                    "a stack of crisp emerald-tinted banknotes growing noticeably taller under warm rim light, photorealistic 35mm f/2.0, strictly zero text or digits."
                ),
                "subject_motion": (
                    "camera glides smoothly beside the linen menu to the open leather check folder as crisp emerald banknotes stack higher under warm candlelight"
                ),
            },
            {
                "shot_id": "S03",
                "scene_group": "G2",
                "continues_prev": False,
                "scene_anchor": (
                    "Moody obsidian-dark scientific studio with a translucent 3D glass-and-light anatomical human brain sculpture "
                    "lit by crisp crimson and cyan volumetric rim lighting, strictly zero text"
                ),
                "narration": "Why does one tiny symbol change your order? Seeing currency triggers your brain's pain center.",
                "pause_after_sec": 0.34,
                "camera_verb": "Slow precision macro zoom-in",
                "start_visual": (
                    "High-contrast 8K 3D biomedical-economic visualization in an obsidian-dark studio: a translucent glass human head and brain profile "
                    "with a vivid crimson-red (#D9381E) bioluminescent pulse igniting deep inside the insular cortex pain center, crisp studio rim light, strictly zero text."
                ),
                "end_visual": (
                    "Inside the same translucent 3D glass brain in the dark studio, concentric crimson-red neural shockwaves ripple outward through branching "
                    "cortical pathways from the glowing insular core, photorealistic Octane scientific render, strictly zero text."
                ),
                "subject_motion": (
                    "concentric crimson-red neural shockwaves ignite and ripple smoothly outward through the translucent 3D cortical pathways"
                ),
            },
            {
                "shot_id": "S04",
                "scene_group": "G2",
                "continues_prev": True,
                "scene_anchor": (
                    "Moody obsidian-dark scientific studio with a translucent 3D glass-and-light anatomical human brain sculpture "
                    "lit by calm cyan and amber volumetric rim lighting, strictly zero text"
                ),
                "narration": "Economists call this the pain of paying—and modern checkout is built to numb it.",
                "pause_after_sec": 0.34,
                "camera_verb": "Smooth optical pull-back",
                "end_visual": (
                    "Pulling back slightly on the same translucent 3D glass brain in the dark studio, a smooth cool-cyan contactless wave sweeps gently across the cortex, "
                    "dimming and soothing the sharp crimson pain glow into a calm tranquil blue-gold state, strictly zero text."
                ),
                "subject_motion": (
                    "a smooth luminous cyan wave sweeps across the translucent 3D brain, calming the bright crimson glow into tranquil cool blue light"
                ),
            },
            {
                "shot_id": "S05",
                "scene_group": "G3",
                "continues_prev": False,
                "scene_anchor": (
                    "Sleek dark-slate modern retail checkout counter photographed on 35mm macro cinema lens at f/2.0 "
                    "with warm tungsten background bokeh and crisp metallic highlights, strictly zero text"
                ),
                "narration": "Tap-to-pay terminals and casino chips sever the link between buying and losing cash.",
                "pause_after_sec": 0.30,
                "camera_verb": "Crisp 35mm tabletop lateral dolly",
                "start_visual": (
                    "Realistic 35mm macro shot on a sleek dark-slate checkout counter: a matte-black smartphone hovers inches above a modern brushed-aluminum "
                    "contactless payment reader beside two glossy red-and-emerald ceramic chips, warm retail bokeh behind, strictly zero text or logos."
                ),
                "end_visual": (
                    "On the same dark-slate checkout counter, as the matte-black smartphone taps near the brushed-aluminum reader, a soft cyan light ring glows "
                    "on the terminal while polished gold coins slide effortlessly away across the counter out of frame, photorealistic 35mm, zero text."
                ),
                "subject_motion": (
                    "the matte-black smartphone dips smoothly over the aluminum payment reader, triggering a soft cyan light ring while gold coins glide effortlessly away"
                ),
            },
            {
                "shot_id": "S06",
                "scene_group": "G4",
                "continues_prev": False,
                "scene_anchor": (
                    "Sunlit morning natural oak cafe table photographed on 35mm lens at f/2.0 with warm golden window light "
                    "and rich stitched brown leather wallet texture, strictly zero text"
                ),
                "narration": "Whenever spending feels effortless, pause three seconds and picture real bills leaving your hand.",
                "pause_after_sec": 0.28,
                "camera_verb": "Calm authoritative slow push-in to center lock",
                "start_visual": (
                    "Realistic 35mm close-up on a sunlit oak cafe table: two calm human hands hold a rich stitched espresso-brown leather wallet slightly open "
                    "revealing crisp green paper edges beside a white ceramic espresso cup with gentle rising steam, warm golden morning light, zero text."
                ),
                "end_visual": (
                    "On the same sunlit oak cafe table, the hands calmly fold the stitched brown leather wallet shut and rest it firmly on the wood grain "
                    "beside the steaming white ceramic espresso cup in composed financial clarity, photorealistic 35mm f/2.0, strictly zero text."
                ),
                "subject_motion": (
                    "the hands calmly fold the stitched leather wallet shut and set it firmly onto the sunlit oak table as delicate steam rises from the espresso cup"
                ),
            },
        ],
    },
    "en-first-principles:9x16": {
        "channel_slug": "en-first-principles",
        "aspect": "9:16",
        "title": "How a Wind-Powered Craft Outruns the Wind Pushing It",
        "voice": "en-US-ChristopherNeural",
        "shots": [
            {
                "shot_id": "S01",
                "scene_group": "G1",
                "continues_prev": False,
                "scene_anchor": (
                    "Vast dry desert salt flat under a crisp twilight slate sky (#0F172A), realistic 8K Veritasium outdoor field-test cinematography "
                    "with clean cyan and golden-amber aerodynamic streamlines, strictly zero chalkboards or text"
                ),
                "narration": "Can a wind-powered craft travel straight downwind faster than the wind pushing it?",
                "pause_after_sec": 0.30,
                "camera_verb": "Dynamic low-angle tracking push-in",
                "start_visual": (
                    "Veritasium 8K outdoor physics field-test shot on a vast desert salt flat under a deep twilight slate sky (#0F172A). "
                    "A sleek skeletal carbon-fiber three-wheeled land yacht with a tall spinning cobalt-cyan (#38BDF8) rotor mast rolls forward through "
                    "laminar golden-amber (#F59E0B) wind streamlines, strictly zero text, zero letters, zero chalkboards."
                ),
                "end_visual": (
                    "On the same desert salt flat under twilight slate sky (#0F172A), the carbon-fiber cyan-rotor land yacht surges cleanly past a drifting white "
                    "smoke puff carried by the golden wind streamlines, leaving the wind marker behind, strictly zero text."
                ),
                "subject_motion": (
                    "the skeletal carbon-fiber rotor land yacht accelerates smoothly past the drifting white wind-speed smoke puff across the open salt flat"
                ),
            },
            {
                "shot_id": "S02",
                "scene_group": "G1",
                "continues_prev": True,
                "scene_anchor": (
                    "Vast dry desert salt flat under a crisp twilight slate sky (#0F172A), realistic 8K Veritasium outdoor field-test cinematography "
                    "with glowing cyan and amber velocity arrows, strictly zero chalkboards or text"
                ),
                "narration": "Physics professors bet thousands it was impossible—until this vehicle hit nearly triple wind speed.",
                "pause_after_sec": 0.38,
                "camera_verb": "Smooth side-profile desert tracking shot",
                "end_visual": (
                    "Side-profile tracking shot on the exact same outdoor twilight salt flat (#0F172A): three long glowing cyan velocity arrows project forward "
                    "ahead of the speeding carbon-fiber rotor craft while one short amber wind arrow trails behind on the open horizon, strictly zero text."
                ),
                "subject_motion": (
                    "camera tracks smoothly alongside the speeding salt-flat craft as three bright cyan velocity arrows extend far ahead of the shorter amber wind arrow"
                ),
            },
            {
                "shot_id": "S03",
                "scene_group": "G2",
                "continues_prev": False,
                "scene_anchor": (
                    "Clean 3D X-ray mechanical drivetrain cutaway isolated in a pure dark slate-navy (#0F172A) studio void "
                    "with machined titanium, amber bevel gears, and cyan rotor blades, strictly zero chalkboards or text"
                ),
                "narration": "How? Its giant rotor isn't a windmill—it's geared directly to the rolling wheels.",
                "pause_after_sec": 0.30,
                "camera_verb": "Precision macro X-ray zoom-in",
                "start_visual": (
                    "Clean 8K 3D mechanical X-ray cutaway isolated against a pure dark slate-navy (#0F172A) void: glowing golden-amber (#F59E0B) bevel gears "
                    "inside the rolling rear wheel axle mesh with a vertical titanium drive shaft running up to pitch-angled cyan (#38BDF8) propeller blades, zero text."
                ),
                "end_visual": (
                    "Closer 3D X-ray cutaway in the same dark slate-navy (#0F172A) void: the rolling tire turns the golden bevel gears and vertical titanium shaft, "
                    "driving the cyan propeller blades to push a luminous pocket of air backward, strictly zero text."
                ),
                "subject_motion": (
                    "the golden bevel gears inside the axle rotate in crisp mechanical lockstep, spinning the vertical titanium shaft and cyan propeller blades"
                ),
            },
            {
                "shot_id": "S04",
                "scene_group": "G2",
                "continues_prev": True,
                "scene_anchor": (
                    "Clean 3D X-ray mechanical drivetrain cutaway isolated in a pure dark slate-navy (#0F172A) studio void "
                    "with crisp cyan thrust and red drag force vectors, strictly zero chalkboards or text"
                ),
                "narration": "As the ground turns the axle, the blades push backward against slower tail-wind.",
                "pause_after_sec": 0.36,
                "camera_verb": "Smooth isometric orbit pull-back",
                "end_visual": (
                    "Isometric 3D force-balance view in the same dark slate-navy (#0F172A) void: amber ground lines stream backward beneath the rolling tires "
                    "while a long forward cyan thrust arrow from the rotor clearly dwarfs a small crimson wheel-drag arrow, strictly zero text."
                ),
                "subject_motion": (
                    "the forward cyan rotor-thrust arrow extends decisively longer than the small crimson wheel-drag arrow as amber ground lines stream beneath the wheels"
                ),
            },
            {
                "shot_id": "S05",
                "scene_group": "G3",
                "continues_prev": False,
                "scene_anchor": (
                    "Minimalist macro physics demonstration isolated against a pure dark slate-navy (#0F172A) studio background "
                    "with two brushed-steel inclined wedges and a glossy amber seed, strictly zero chalkboards or text"
                ),
                "narration": "Like pinching a slick pumpkin seed between two fingers, tiny squeeze creates faster launch.",
                "pause_after_sec": 0.30,
                "camera_verb": "Crisp macro slow-motion push-in",
                "start_visual": (
                    "Minimalist 8K macro physics analogy against a pure dark slate-navy (#0F172A) background: two sleek brushed-steel angled blocks "
                    "converge from top and bottom onto a glossy golden-amber (#F59E0B) teardrop seed with subtle cyan force arrows, strictly zero text."
                ),
                "end_visual": (
                    "Against the same pure dark slate-navy (#0F172A) background, as the two brushed-steel angled blocks press a tiny distance inward, "
                    "the glossy golden-amber teardrop seed shoots rapidly forward leaving a crisp cyan streak, strictly zero text."
                ),
                "subject_motion": (
                    "the two brushed-steel angled blocks press gently inward and launch the glossy golden-amber seed swiftly forward along a clean cyan trail"
                ),
            },
            {
                "shot_id": "S06",
                "scene_group": "G4",
                "continues_prev": False,
                "scene_anchor": (
                    "Wide symmetrical desert salt flat horizon at twilight (#0F172A) with mirror salt reflections "
                    "and golden laminar wind streamlines, strictly zero chalkboards or text"
                ),
                "narration": "No physics law breaks—because real leverage harvests the speed gap between air and ground.",
                "pause_after_sec": 0.28,
                "camera_verb": "Calm centered horizon pull-back",
                "start_visual": (
                    "Wide symmetrical outdoor horizon shot back on the vast twilight desert salt flat (#0F172A): the sleek three-wheeled carbon-fiber land yacht "
                    "with its spinning cyan rotor races cleanly across dark mirror-like salt between golden wind streamlines above and ground below, zero text."
                ),
                "end_visual": (
                    "Wide serene horizon pull-back on the same twilight salt flat (#0F172A): the sleek cyan-rotor land yacht glides effortlessly toward the glowing "
                    "amber horizon line, harvesting the relative motion between sky and earth, strictly zero text."
                ),
                "subject_motion": (
                    "camera pulls smoothly back as the sleek three-wheeled wind craft glides effortlessly straight toward the clean twilight salt-flat horizon"
                ),
            },
        ],
    },
    "en-first-principles:16x9": {
        "channel_slug": "en-first-principles",
        "aspect": "16:9",
        "title": "The Electricity Myth: How Energy Actually Reaches a Light Bulb",
        "voice": "en-US-ChristopherNeural",
        "shots": [
            {
                "shot_id": "L01",
                "scene_group": "A1",
                "continues_prev": False,
                "scene_anchor": (
                    "Widescreen 16:9 dark space-slate (#0B1021) optical physics bench in open starry space with a brass knife switch, "
                    "amber battery cell, unlit glass filament bulb, and twin copper wires stretching toward a distant Moon, strictly zero chalkboards or text"
                ),
                "narration": "Picture a battery wired to a light bulb using copper wires stretching to the Moon and back.",
                "pause_after_sec": 0.30,
                "camera_verb": "Epic wide orbital push-in",
                "start_visual": (
                    "Cinematic widescreen 16:9 physics visualization on deep space-slate (#0B1021): on a sleek dark optical bench in the foreground, "
                    "a brass knife switch, a glowing amber battery cell, and an unlit clear glass filament bulb sit one meter apart, while two gleaming bare copper "
                    "wires loop far out into starry space toward a distant silver Moon. Crisp volumetric rim light, strictly zero text or chalkboards."
                ),
                "end_visual": (
                    "Closer widescreen framing on the same dark optical bench against starry space (#0B1021): the open brass knife switch blade hovers millimeters "
                    "above its copper contact just one meter across from the unlit glass filament bulb as twin copper wires trail toward the Moon, zero text."
                ),
                "subject_motion": (
                    "camera glides smoothly closer to the open brass knife switch and unlit glass filament bulb while the twin copper wires stretch toward the distant Moon"
                ),
            },
            {
                "shot_id": "L02",
                "scene_group": "A1",
                "continues_prev": True,
                "scene_anchor": (
                    "Widescreen 16:9 dark space-slate (#0B1021) optical physics bench in open starry space with brass knife switch "
                    "and glass filament bulb one meter apart, strictly zero chalkboards or text"
                ),
                "narration": "Snap that switch closed one meter from the bulb—how long until it lights up?",
                "pause_after_sec": 0.36,
                "camera_verb": "Crisp macro side push-in",
                "end_visual": (
                    "On the same dark space-slate optical bench (#0B1021), the brass knife blade snaps firmly into the copper terminal with a tiny crisp cyan spark, "
                    "launching a faint luminous ripple into the open one-meter gap toward the glass bulb, strictly zero text."
                ),
                "subject_motion": (
                    "the brass switch blade closes cleanly into the copper contact with a crisp cyan spark as a subtle luminous field ripple enters the air gap"
                ),
            },
            {
                "shot_id": "L03",
                "scene_group": "A2",
                "continues_prev": False,
                "scene_anchor": (
                    "Locked horizontal macro 3D cutaway of a single straight cylindrical copper wire centered against a pure deep-navy (#0F172A) void, "
                    "showing warm copper lattice atoms and glowing cyan electron spheres, strictly zero chalkboards or text"
                ),
                "narration": "School taught us that batteries push electrons through copper like water rushing through a hose.",
                "pause_after_sec": 0.28,
                "camera_verb": "Smooth horizontal cross-section dolly",
                "start_visual": (
                    "Clean 8K 3D scientific cutaway of a single straight horizontal copper wire cylinder centered against a pure deep-navy (#0F172A) void: "
                    "inside the glowing warm copper atomic lattice, tiny cyan (#38BDF8) electron spheres jiggle gently in place, strictly zero text."
                ),
                "end_visual": (
                    "Along the exact same single horizontal copper wire cutaway on deep navy (#0F172A), the tiny cyan electron spheres creep barely a fraction "
                    "of a millimeter to the right through the warm copper lattice at glacial snail speed, strictly zero text."
                ),
                "subject_motion": (
                    "the tiny cyan electron spheres inside the single horizontal copper lattice vibrate gently while drifting almost imperceptibly slowly to the right"
                ),
            },
            {
                "shot_id": "L04",
                "scene_group": "A2",
                "continues_prev": True,
                "scene_anchor": (
                    "Locked horizontal macro 3D cutaway of a single straight cylindrical copper wire centered against a pure deep-navy (#0F172A) void, "
                    "strictly zero chalkboards or text"
                ),
                "narration": "In reality, electrons drift slower than a snail—barely a tenth of a millimeter per second.",
                "pause_after_sec": 0.32,
                "camera_verb": "Slow macro pull-back along the same horizontal wire",
                "end_visual": (
                    "Pulling back slightly on the exact same single horizontal copper wire cutaway (#0F172A), a small sleek glass sand-timer trickles golden grains "
                    "above the wire while the cyan electron spheres inside advance less than a hair's breadth, strictly zero text."
                ),
                "subject_motion": (
                    "golden sand grains trickle steadily inside the small glass timer above the single horizontal copper wire while cyan electrons barely inch forward"
                ),
            },
            {
                "shot_id": "L05",
                "scene_group": "A2",
                "continues_prev": True,
                "scene_anchor": (
                    "Locked horizontal macro 3D cutaway of a single straight cylindrical copper wire centered against a pure deep-navy (#0F172A) void, "
                    "with golden electromagnetic wave rings radiating outside the wire, strictly zero chalkboards or text"
                ),
                "narration": "And in alternating current inside your walls, electrons never travel at all—they just wiggle in place.",
                "pause_after_sec": 0.36,
                "camera_verb": "Steady locked-off horizontal cutaway",
                "end_visual": (
                    "In the exact same single horizontal copper wire cutaway on deep navy (#0F172A), the cyan electron spheres oscillate rhythmically left and right "
                    "in place while luminous golden electromagnetic rings expand into the empty space outside the copper cylinder, strictly zero text."
                ),
                "subject_motion": (
                    "cyan electron spheres oscillate smoothly left and right in place inside the copper cylinder while golden field rings radiate into the space outside"
                ),
            },
            {
                "shot_id": "L06",
                "scene_group": "A3",
                "continues_prev": False,
                "scene_anchor": (
                    "Widescreen 3D electromagnetic circuit diagram suspended in a pure deep-slate (#0B1021) void: amber battery on left, "
                    "glass filament bulb on right, parallel top and bottom copper wires, cyan electric arcs and golden Poynting energy arrows, zero text"
                ),
                "narration": "So if electrons aren't carrying energy inside the metal, how does power reach the bulb?",
                "pause_after_sec": 0.30,
                "camera_verb": "Sweeping 3D isometric circuit reveal",
                "start_visual": (
                    "Stunning widescreen 8K 3D electromagnetic field visualization in a pure deep-slate (#0B1021) void: an amber battery cell on the left "
                    "and glass filament bulb on the right connected by parallel top and bottom copper wires, with cyan (#38BDF8) electric field arcs spanning "
                    "between the wires and circular amber magnetic rings wrapping the conductors, strictly zero text."
                ),
                "end_visual": (
                    "Across the same 3D parallel-wire circuit in deep slate (#0B1021), brilliant golden Poynting-vector energy streams flow straight through "
                    "the empty space between the wires from the battery on the left toward the glass bulb on the right, strictly zero text."
                ),
                "subject_motion": (
                    "cyan electric arcs and amber magnetic rings interlock as bright golden energy streams flow straight through empty space from battery toward bulb"
                ),
            },
            {
                "shot_id": "L07",
                "scene_group": "A3",
                "continues_prev": True,
                "scene_anchor": (
                    "Widescreen 3D electromagnetic circuit diagram suspended in a pure deep-slate (#0B1021) void with golden Poynting streamlines "
                    "converging into the glass filament bulb, strictly zero text"
                ),
                "narration": "Maxwell's equations prove electrical energy flows entirely through the empty space outside the wires.",
                "pause_after_sec": 0.30,
                "camera_verb": "Smooth tracking push toward the glass bulb",
                "end_visual": (
                    "Tracking right toward the glass bulb on the same 3D circuit (#0B1021), the golden electromagnetic energy streamlines curve radially inward "
                    "from the surrounding empty space right through the glass envelope into the tungsten filament, igniting a warm orange glow, zero text."
                ),
                "subject_motion": (
                    "golden electromagnetic energy streamlines converge inward from the surrounding empty space into the bulb filament as it begins glowing warm orange"
                ),
            },
            {
                "shot_id": "L08",
                "scene_group": "A3",
                "continues_prev": True,
                "scene_anchor": (
                    "Widescreen 3D perspective along twin parallel copper conductors in a pure deep-slate (#0B1021) void "
                    "guiding a luminous golden electromagnetic wave, strictly zero text"
                ),
                "narration": "Copper wires just act like railroad tracks, guiding those invisible fields at nearly light speed.",
                "pause_after_sec": 0.36,
                "camera_verb": "Wide cinematic arc along the parallel conductors",
                "end_visual": (
                    "Dynamic 3D perspective along the parallel copper conductors in deep slate (#0B1021): crisp cyan surface charge rings race along the outer "
                    "skin of the copper wires like rails, steering a radiant golden electromagnetic wave through the space between them, strictly zero text."
                ),
                "subject_motion": (
                    "luminous cyan surface rings glide rapidly along the outer skin of the parallel copper wires, steering a radiant golden wave through the gap"
                ),
            },
            {
                "shot_id": "L09",
                "scene_group": "A4",
                "continues_prev": False,
                "scene_anchor": (
                    "Widescreen 16:9 dark space-slate (#0B1021) optical bench against starry space with closed brass switch, "
                    "one-meter air gap, glass bulb, and distant silver Moon, strictly zero chalkboards or text"
                ),
                "narration": "In our Moon circuit, the field crosses the one-meter air gap in just nanoseconds.",
                "pause_after_sec": 0.28,
                "camera_verb": "Dramatic widescreen bench reveal",
                "start_visual": (
                    "Returning to the widescreen dark space-slate optical bench against starry space (#0B1021): the closed brass knife switch on the left emits "
                    "a translucent golden-cyan electromagnetic wavefront straight across the one-meter open gap toward the unlit glass bulb on the right while "
                    "the long copper wires trail far toward the distant Moon, strictly zero text."
                ),
                "end_visual": (
                    "On the same space-slate optical bench (#0B1021), the golden-cyan wavefront reaches the glass bulb one meter away and the tungsten filament "
                    "blossoms into a warm golden glow long before any signal reaches the distant silver Moon in the background, strictly zero text."
                ),
                "subject_motion": (
                    "the translucent golden-cyan wavefront crosses the one-meter gap in a smooth sweep and ignites the tungsten bulb into a warm golden glow"
                ),
            },
            {
                "shot_id": "L10",
                "scene_group": "A5",
                "continues_prev": False,
                "scene_anchor": (
                    "Clean 8K 3D physics studio view against pure deep slate (#0B1021) showing two separate helical copper transformer coils "
                    "separated by a visible open air gap, strictly zero chalkboards or text"
                ),
                "narration": "That is why transformers pass megawatts across open air gaps without a single electron jumping across.",
                "pause_after_sec": 0.30,
                "camera_verb": "Smooth centered dolly across air-gap coils",
                "start_visual": (
                    "Clean widescreen 8K 3D physics render against pure deep slate (#0B1021): two separate helical copper coils stand side by side with a clear "
                    "empty air gap between them, as luminous golden magnetic flux loops emerge from the left coil toward the right coil, strictly zero text."
                ),
                "end_visual": (
                    "Against pure deep slate (#0B1021), pulsing golden magnetic flux loops bridge cleanly across the empty air gap into the second copper coil "
                    "connected to a steadily shining warm-gold filament bulb on the right without any metal touching, strictly zero text."
                ),
                "subject_motion": (
                    "pulsing golden magnetic flux loops arc smoothly across the open air gap between the two separate copper coils, lighting the bulb on the right"
                ),
            },
            {
                "shot_id": "L11",
                "scene_group": "A6",
                "continues_prev": False,
                "scene_anchor": (
                    "Iconic symmetrical widescreen composition against pure deep space-slate (#0B1021) featuring a single radiant clear-glass "
                    "tungsten bulb wrapped in delicate cyan-and-gold field geometry, strictly zero text"
                ),
                "narration": "Wires never carried your electricity—they only steered the invisible fields moving around them.",
                "pause_after_sec": 0.28,
                "camera_verb": "Serene symmetrical final pull-back",
                "start_visual": (
                    "Iconic symmetrical widescreen 16:9 close-up against pure deep space-slate (#0B1021): a single radiant warm-gold glass filament bulb shines "
                    "in the center as delicate geometric cyan and golden electromagnetic field lines flow gracefully into it from empty space, zero text."
                ),
                "end_visual": (
                    "Wide serene symmetrical pull-back against pure deep space-slate (#0B1021): the lone warm-gold glass light bulb glows calmly at center frame "
                    "surrounded by a balanced halo of subtle cyan and amber field lines fading into clean dark space, strictly zero text."
                ),
                "subject_motion": (
                    "camera pulls smoothly back in perfect symmetry as delicate cyan and amber field lines cradle the glowing warm-gold filament bulb"
                ),
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# Phase 3: 18-Channel Brand Emblem Regeneration (1:1 Zero-Text + 1.05x Overscan)
# ---------------------------------------------------------------------------


def _clean_corner_sparkle(rgba: Image.Image) -> Image.Image:
    """Seamlessly remove Google Flow BELUGA bottom-right corner star via exact inverse-alpha unblending."""
    from flow_video.sparkle_unblend import clean_beluga_sparkle_pil

    return clean_beluga_sparkle_pil(rgba)


def regenerate_channel_logos(
    channels: list[str] | None = None,
    max_workers: int = 4,
    force: bool = True,
) -> dict[str, Any]:
    """Generate clean 1:1 zero-text brand emblems via Flow CDP for English channels."""
    target_slugs = channels or list(EN_CHANNEL_LOGO_PROMPTS.keys())
    work_dir = V3_DEMOS_ROOT / "_logo_batch_work"
    work_dir.mkdir(parents=True, exist_ok=True)

    ledger = CreditLedger()
    healthy_profiles = [
        p for p in PROFILES if p.get("name") not in ("profile_11",)
    ]
    # Prefer image_only_zero_credit or lowest-credit accounts first to preserve video credits,
    # while keeping full pool available for parallel workers.
    ordered_profiles = sorted(
        healthy_profiles,
        key=lambda p: ledger.get_balance(str(p.get("name")), default_credits=1000),
    )

    tasks: list[dict[str, Any]] = []
    for slug in target_slugs:
        norm_slug = slug.strip().replace("_", "-")
        if norm_slug not in EN_CHANNEL_LOGO_PROMPTS:
            raise KeyError(f"Unknown English channel slug for logo prompt: {slug}")
        raw_png = work_dir / f"{norm_slug}_raw.png"
        if not force and raw_png.is_file() and raw_png.stat().st_size > 10_000:
            continue
        tasks.append(
            {
                "id": f"logo_{norm_slug}",
                "jobId": f"logo_{norm_slug}",
                "prompt": EN_CHANNEL_LOGO_PROMPTS[norm_slug],
                "ratio": "1:1",
                "aspect": "1:1",
                "model": "BELUGA",
                "filename": raw_png.name,
                "out_dir": str(work_dir),
                "credit_cost": 0,
                "credit_reason": "image",
                "editorial_overlay": {"enabled": False},
            }
        )

    if tasks:
        logger.info(
            f"[LOGO-BATCH] Generating {len(tasks)} clean 1:1 zero-text brand emblems via Flow CDP (workers={max_workers})..."
        )
        pool = PersistentWorkerPool(
            target_workers=min(max_workers, len(ordered_profiles)),
            profiles=ordered_profiles,
            cooldown_seconds=25.0,
            pacing_seconds=2.0,
            stagger_seconds=1.0,
            headless=True,
            min_credits_required=0,
        )
        try:
            pool.start()
            for t in tasks:
                pool.submit_task(t)
            pool.wait_completion(timeout=900.0)
        finally:
            pool.shutdown()
            get_process_manager().terminate_all()

    results: dict[str, Any] = {}
    for slug in target_slugs:
        norm_slug = slug.strip().replace("_", "-")
        ch_dir = ROOT_DIR / "sys/channels" / norm_slug.replace("-", "_") / "assets"
        ch_dir.mkdir(parents=True, exist_ok=True)
        raw_png = work_dir / f"{norm_slug}_raw.png"
        if not raw_png.is_file() or raw_png.stat().st_size < 4096:
            results[norm_slug] = {"status": "failed", "error": f"Missing {raw_png}"}
            continue

        # Apply corner sparkle removal and 1.05x center overscan crop (2.5% per edge)
        with Image.open(raw_png) as im:
            rgba = _clean_corner_sparkle(im.convert("RGBA"))
            w, h = rgba.size
            mx = int(round(w * 0.025))
            my = int(round(h * 0.025))
            cropped = rgba.crop((mx, my, w - mx, h - my))
            avatar_800 = cropped.resize((800, 800), Image.Resampling.LANCZOS)
            wm_150 = cropped.resize((150, 150), Image.Resampling.LANCZOS)

            avatar_path = ch_dir / "avatar_800x800.png"
            logo_path = ch_dir / "logo.png"
            wm_path = ch_dir / "watermark_150x150.png"

            avatar_800.save(avatar_path, format="PNG")
            avatar_800.save(logo_path, format="PNG")
            wm_150.save(wm_path, format="PNG")

        raw_sidecar = raw_png.with_suffix(".json")
        if raw_sidecar.is_file():
            shutil.copy2(raw_sidecar, ch_dir / "avatar_800x800.json")

        results[norm_slug] = {
            "status": "completed",
            "avatar_800x800": str(avatar_path),
            "watermark_150x150": str(wm_path),
        }
        logger.info(f"[✓] [{norm_slug}] Updated avatar_800x800.png, logo.png, watermark_150x150.png")

    report_path = V3_DEMOS_ROOT / "logo_regeneration_report.json"
    report_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return results


# ---------------------------------------------------------------------------
# Phase 4: Credit-Gated Audio-First Seamless Flow Video Demo Builder
# ---------------------------------------------------------------------------


def build_scene_pairs_from_shots(
    channel_slug: str,
    shots: list[dict[str, Any]],
    beat_durations: list[float],
    frames_dir: Path,
    xfade_pivot_sec: float = 0.24,
) -> list[ScenePairSpec]:
    """Build reference-locked ScenePairSpecs aligned to exact spoken beat durations.

    - Continuous shots (`continues_prev=True`):
      * Reuse the exact `frames/{prev_shot_id}_end.png` boundary frame (`0` extra image calls,
        100% pixel-identical seam) and set `trim_first_frame=True`.
      * Generate `end_image_prompt` conditioned on that shared start frame (`end_based_on_start=True`)
        via `maseQ` + `reference_media_ids`.
    - Scene-pivot shots (`continues_prev=False` for index >= 1):
      * Start a new visual scene in the same channel `StyleDNA` right on the narrator's breath pause.
      * Add `xfade_pivot_sec` (`0.24s`) to the preceding shot's `target_duration` so the `0.24s` optical
        cross-dissolve between scene groups preserves exact millisecond global audio sync!
    """
    if len(shots) != len(beat_durations):
        raise ValueError(f"Shot count ({len(shots)}) != beat_durations count ({len(beat_durations)})")

    n = len(shots)
    pairs: list[ScenePairSpec] = []
    for idx, (shot, b_dur) in enumerate(zip(shots, beat_durations, strict=True)):
        shot_id = str(shot.get("shot_id") or f"S{idx + 1:02d}")
        continues_prev = bool(shot.get("continues_prev", False)) and idx > 0
        next_starts_new_group = (idx + 1 < n) and (not bool(shots[idx + 1].get("continues_prev", False)))

        # Add 0.24s overlap budget to the final shot of a scene group when another group follows
        eff_target_dur = round(float(b_dur) + (xfade_pivot_sec if next_starts_new_group else 0.0), 4)

        raw_end_vis = str(shot.get("end_visual", "")).strip()
        scene_anchor = shot.get("scene_anchor")
        motion_prompt = build_channel_motion_prompt(
            channel_slug=channel_slug,
            shot_action=str(shot.get("subject_motion", "subtle physical motion")),
            camera_move=shot.get("camera_verb"),
            is_interpolation=bool(raw_end_vis),
            scene_anchor=scene_anchor,
        )
        wrapped_end_prompt = (
            build_reference_keyframe_prompt(
                channel_slug,
                raw_end_vis,
                use_camera_angle_wrapper=False,
                scene_anchor=scene_anchor,
            )
            if raw_end_vis
            else None
        )

        if continues_prev:
            prev_id = str(shots[idx - 1].get("shot_id") or f"S{idx:02d}")
            shared_start_file = str((frames_dir / f"{prev_id}_end.png").resolve())
            sp = ScenePairSpec(
                id=shot_id,
                start_image_path=shared_start_file,
                start_image_prompt=None,
                end_image_path=None,
                end_image_prompt=wrapped_end_prompt,
                motion_prompt=motion_prompt,
                target_duration=eff_target_dur,
                trim_first_frame=True,
                start_based_on=None,
                end_based_on_start=bool(wrapped_end_prompt),
            )
        else:
            start_vis = str(shot.get("start_visual", "")).strip()
            if not start_vis:
                raise ValueError(f"Scene-opening shot {shot_id} requires 'start_visual'")
            sp = ScenePairSpec(
                id=shot_id,
                start_image_path=None,
                start_image_prompt=start_vis,
                end_image_path=None,
                end_image_prompt=wrapped_end_prompt,
                motion_prompt=motion_prompt,
                target_duration=eff_target_dur,
                trim_first_frame=False,
                start_based_on=None,
                end_based_on_start=bool(wrapped_end_prompt),
            )
        pairs.append(sp)

    return pairs


def teardown_colab_session(account: str | None, session: str | None) -> None:
    """Cleanly stop a specific Colab T4 session without affecting sibling squads."""
    if not account or not session:
        return
    try:
        from colab_bridge.client import Client

        base_cfg_path = SYS_DIR / "config.json"
        cfg: dict[str, Any] = (
            json.loads(base_cfg_path.read_text(encoding="utf-8"))
            if base_cfg_path.is_file()
            else {}
        )
        cfg.setdefault("colab_tts", {})
        cfg["colab_tts"]["session"] = session
        cfg["colab_tts"]["_session_explicit"] = True
        cfg["colab_tts"]["account"] = account
        client = Client(SYS_DIR, cfg)
        client.account = account
        client.session = session
        client.ensure_authenticated()
        client.stop()
        logger.info(f"Cleanly stopped Colab session {session} on {account}")
    except Exception as exc:
        logger.warning(f"Failed to teardown Colab session {session} on {account}: {exc}")


def package_final_on_colab_t4_nvenc(
    channel_slug: str,
    job_id: str,
    aspect: str,
    groups: list[list[int]],
    tasks: list[VideoClipTask],
    group_spoken_durs: list[float],
    beat_durations: list[float],
    audio_path: Path,
    ass_path: Path,
    srt_path: Path,
    watermark_png: Path,
    out_mp4: Path,
    fps: int = 30,
    xfade_pivot_sec: float = 0.24,
    overscan_crop: float = 1.05,
    scratch_dir: Path | None = None,
    colab_account: str | None = None,
) -> dict[str, Any]:
    """Upload raw Flow AI clips and render 100% on remote Colab Tesla T4 FFmpeg h264_nvenc (zero local CPU encode)."""
    import fcntl
    import zipfile

    from colab_bridge.client import Client

    is_short = aspect == "9:16"
    tw, th = (1080, 1920) if is_short else (1920, 1080)
    scratch = scratch_dir or out_mp4.parent / f"_nvenc_scratch_{job_id}"
    scratch.mkdir(parents=True, exist_ok=True)
    bundle_zip = scratch / "nvenc_bundle.zip"

    clip_specs: list[dict[str, Any]] = []
    for idx, t in enumerate(tasks):
        cp = Path(t.output_mp4_path)
        meta_c = probe_video_clip(cp)
        clip_specs.append(
            {
                "arcname": f"clip_{idx:02d}.mp4",
                "raw_dur": float(meta_c["duration"]),
                "trim_first": bool(getattr(t, "trim_first_frame", False)),
                "target_dur": float(t.target_duration) if getattr(t, "target_duration", None) else None,
            }
        )

    total_audio_dur = sum(beat_durations)
    with zipfile.ZipFile(bundle_zip, "w", compression=zipfile.ZIP_STORED) as zf:
        for idx, t in enumerate(tasks):
            zf.write(Path(t.output_mp4_path), arcname=f"clip_{idx:02d}.mp4")
        zf.write(watermark_png, arcname="watermark.png")
        zf.write(audio_path, arcname="audio.wav")
        if is_short and ass_path.is_file():
            zf.write(ass_path, arcname="subtitles.ass")
        if srt_path.is_file():
            zf.write(srt_path, arcname="subtitles.srt")
        manifest_meta = {
            "aspect": aspect,
            "is_short": is_short,
            "tw": tw,
            "th": th,
            "fps": fps,
            "overscan_crop": overscan_crop,
            "total_audio_dur": total_audio_dur,
            "groups": groups,
            "clips": clip_specs,
            "group_spoken_durs": group_spoken_durs,
            "xfade_pivot_sec": xfade_pivot_sec,
        }
        zf.writestr("bundle_manifest.json", json.dumps(manifest_meta, indent=2))

    # Deterministic per-job rotation across verified Colab T4 accounts so parallel squads spread cleanly
    import hashlib

    from tools.channel_production_common import VERIFIED_COLAB_ACCOUNTS

    base_accounts = list(VERIFIED_COLAB_ACCOUNTS)
    rot = int(hashlib.md5(job_id.encode("utf-8")).hexdigest()[:8], 16) % len(base_accounts)
    override_acc = colab_account or os.environ.get("VP_COLAB_ACCOUNT") or os.environ.get("COLAB_ACCOUNT")
    if override_acc:
        candidate_accounts = [override_acc] + [a for a in base_accounts if a != override_acc]
    else:
        candidate_accounts = base_accounts[rot:] + base_accounts[:rot]
    target_session = f"vp-en-{channel_slug}"

    last_exc: Exception | None = None
    for acc in candidate_accounts:
        lock_file = Path(f"/tmp/vp_en_colab_nvenc_{acc}.lock")
        lock_fd = None
        try:
            lock_fd = open(lock_file, "a")
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (BlockingIOError, OSError):
            if lock_fd:
                try:
                    lock_fd.close()
                except Exception:
                    pass
            continue

        try:
            base_cfg_path = SYS_DIR / "config.json"
            cfg: dict[str, Any] = (
                json.loads(base_cfg_path.read_text(encoding="utf-8"))
                if base_cfg_path.is_file()
                else {}
            )
            cfg.setdefault("colab_tts", {})
            cfg["colab_tts"]["session"] = target_session
            cfg["colab_tts"]["_session_explicit"] = True
            cfg["colab_tts"]["render_timeout_seconds"] = 1800
            cfg["colab_tts"]["account"] = acc

            client = Client(SYS_DIR, cfg)
            client.account = acc

            effective_session = target_session
            try:
                snap = client._budgets().snapshot("colab:" + acc)
                allocs = [
                    it["session"]
                    for it in snap.get("allocated_sessions", [])
                    if it.get("device") == "T4"
                    and (
                        it.get("session") == target_session
                        or str(it.get("session", "")).startswith("vp-")
                    )
                ]
                if not allocs:
                    allocs = [
                        it["session"]
                        for it in snap.get("allocated_sessions", [])
                        if it.get("device") == "T4" and it.get("session")
                    ]
                if allocs and effective_session not in allocs:
                    effective_session = allocs[0]
            except Exception:
                pass

            client.session = effective_session
            cfg["colab_tts"]["session"] = effective_session

            client.ensure_authenticated()
            try:
                client._ready(auto_start=True)
            except Exception as ex_ready:
                try:
                    from tools.channel_production_common import cleanup_stale_colab_state

                    cleanup_stale_colab_state(client, acc, effective_session)
                    client.session = target_session
                    client._ready(auto_start=True)
                except Exception as ex_recover:
                    raise ex_ready from ex_recover

            remote_dir = f"/content/vp_en_nvenc/{job_id}"
            remote_bundle = f"{remote_dir}/bundle.zip"

            client.exec(f"from pathlib import Path\nPath({remote_dir!r}).mkdir(parents=True, exist_ok=True)")
            client.call("upload", "-s", client.session, str(bundle_zip.resolve()), remote_bundle, timeout=300)

            remote_render_script = f"""
import subprocess, sys, json, os, zipfile
from pathlib import Path

work = Path({remote_dir!r})
bundle_zip = work / "bundle.zip"
with zipfile.ZipFile(bundle_zip, 'r') as zf:
    zf.extractall(work)

res = subprocess.run(
    ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=256x256:d=0.04", "-c:v", "h264_nvenc", "-f", "null", "-"],
    capture_output=True, text=True
)
if res.returncode != 0:
    raise RuntimeError("COLAB_NVENC_UNAVAILABLE: h264_nvenc not supported on remote GPU: " + res.stderr)

meta = json.loads((work / "bundle_manifest.json").read_text())
is_short = meta["is_short"]
tw, th = int(meta["tw"]), int(meta["th"])
fps = int(meta["fps"])
overscan_crop = float(meta["overscan_crop"])
total_audio_dur = float(meta["total_audio_dur"])
groups = meta["groups"]
clips = meta["clips"]
group_spoken_durs = meta["group_spoken_durs"]
xfade_pivot_sec = float(meta["xfade_pivot_sec"])

ow = max(tw, int(round(tw * overscan_crop / 2.0)) * 2)
oh = max(th, int(round(th * overscan_crop / 2.0)) * 2)
base_scale = f"scale={{ow}}:{{oh}}:force_original_aspect_ratio=increase,crop={{tw}}:{{th}}:(in_w-{{tw}})/2:(in_h-{{th}})/2,setsar=1,fps={{fps}}"

# Step 1: Stitch each contiguous scene group on Tesla T4 h264_nvenc
group_mp4s = []
for g_idx, indices in enumerate(groups):
    g_out = str(work / f"scene_group_{{g_idx:02d}}.mp4")
    g_cmd = ["ffmpeg", "-y"]
    g_filters = []
    g_vlabels = []
    for local_i, c_idx in enumerate(indices):
        cs = clips[c_idx]
        g_cmd.extend(["-i", str(work / cs["arcname"])])
        raw_dur = float(cs["raw_dur"])
        trim_first = bool(cs["trim_first"])
        target_dur = cs["target_dur"]
        eff_raw_dur = max(0.05, raw_dur - (1.0 / fps)) if trim_first else raw_dur
        trim_step = ",trim=start_frame=1,setpts=PTS-STARTPTS" if trim_first else ""
        if target_dur is not None and target_dur > 0:
            ratio = eff_raw_dur / target_dur
            if 0.7 <= ratio <= 1.35:
                pts_factor = target_dur / eff_raw_dur
                vf = f"[{{local_i}}:v]{{base_scale}}{{trim_step}},setpts={{pts_factor:.6f}}*PTS[cv{{local_i}}]"
            elif target_dur > eff_raw_dur * 1.35:
                extra = target_dur - eff_raw_dur
                vf = f"[{{local_i}}:v]{{base_scale}}{{trim_step}},tpad=stop_mode=clone:stop_duration={{extra:.3f}},setpts=PTS-STARTPTS[cv{{local_i}}]"
            else:
                speed_factor = 1.0 / 1.35
                vf = f"[{{local_i}}:v]{{base_scale}}{{trim_step}},setpts={{speed_factor:.6f}}*PTS,trim=duration={{target_dur:.3f}},setpts=PTS-STARTPTS[cv{{local_i}}]"
        else:
            vf = f"[{{local_i}}:v]{{base_scale}}{{trim_step}},setpts=PTS-STARTPTS[cv{{local_i}}]"
        g_filters.append(vf)
        g_vlabels.append(f"[cv{{local_i}}]")
    g_filters.append(f"{{''.join(g_vlabels)}}concat=n={{len(indices)}}:v=1:a=0[gvout]")
    g_cmd.extend([
        "-filter_complex", ";".join(g_filters),
        "-map", "[gvout]",
        "-c:v", "h264_nvenc", "-preset", "p4", "-b:v", "12M", "-pix_fmt", "yuv420p",
        "-r", str(fps), g_out
    ])
    gp_res = subprocess.run(g_cmd, capture_output=True, text=True)
    if gp_res.returncode != 0:
        raise RuntimeError(f"Remote NVENC group {{g_idx}} stitch failed: " + gp_res.stderr[-800:])
    group_mp4s.append(g_out)

# Step 2: Join scene groups with 0.24s breath-aligned xfade + .ass captions + squircle logo on Tesla T4 h264_nvenc
watermark_png = str(work / "watermark.png")
audio_path = str(work / "audio.wav")
ass_path = str(work / "subtitles.ass")

cmd = ["ffmpeg", "-y"]
for gp in group_mp4s:
    cmd.extend(["-i", gp])
wm_idx = len(group_mp4s)
cmd.extend(["-i", watermark_png])
audio_idx = len(group_mp4s) + 1
cmd.extend(["-i", audio_path])

filter_chains = []
if len(group_mp4s) == 1:
    filter_chains.append("[0:v]setsar=1[vjoined]")
    cur_v = "vjoined"
else:
    cum_offset = 0.0
    prev_lbl = "0:v"
    for g_i in range(1, len(group_mp4s)):
        cum_offset += group_spoken_durs[g_i - 1]
        out_lbl = f"vg{{g_i}}"
        filter_chains.append(
            f"[{{prev_lbl}}][{{g_i}}:v]xfade=transition=fade:duration={{xfade_pivot_sec:.4f}}:offset={{max(0.05, cum_offset):.4f}}[{{out_lbl}}]"
        )
        prev_lbl = out_lbl
    cur_v = prev_lbl

if is_short and os.path.exists(ass_path):
    escaped_ass = ass_path.replace("\\\\", "/").replace(":", r"\\:").replace("'", r"\\'")
    filter_chains.append(f"[{{cur_v}}]ass=filename='{{escaped_ass}}'[vsub]")
    cur_v = "vsub"

wm_pos = "W-w-24:H-h-56" if is_short else "W-w-36:H-h-36"
filter_chains.append(f"[{{cur_v}}][{{wm_idx}}:v]overlay={{wm_pos}}[vout]")
filter_chains.append(f"[{{audio_idx}}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[aout]")

out_mp4 = str(work / "final.mp4")
cmd.extend([
    "-filter_complex", ";".join(filter_chains),
    "-map", "[vout]",
    "-map", "[aout]",
    "-c:v", "h264_nvenc",
    "-preset", "p4",
    "-b:v", "6M",
    "-pix_fmt", "yuv420p",
    "-r", str(fps),
    "-c:a", "aac",
    "-b:a", "192k",
    "-ar", "48000",
    "-t", f"{{total_audio_dur:.3f}}",
    "-movflags", "+faststart",
    out_mp4
])

p = subprocess.run(cmd, capture_output=True, text=True)
if p.returncode != 0:
    raise RuntimeError("Remote FFmpeg NVENC failed: " + p.stderr[-1000:])

print("NVENC_RENDER_SUCCESS")
"""
            exec_out = client.exec(remote_render_script, timeout=900)
            if "NVENC_RENDER_SUCCESS" not in exec_out:
                raise RuntimeError(f"Colab NVENC execution failed: {exec_out}")

            client.call(
                "download",
                "-s",
                client.session,
                f"{remote_dir}/final.mp4",
                str(out_mp4.resolve()),
                timeout=300,
            )

            try:
                client.exec(f"import shutil\nshutil.rmtree({remote_dir!r}, ignore_errors=True)")
            except Exception:
                pass

            meta = probe_video_clip(out_mp4)
            meta["video_encoder"] = "colab_t4_h264_nvenc"
            meta["colab_account"] = acc
            meta["colab_session"] = client.session
            logger.info(f"Colab Tesla T4 FFmpeg h264_nvenc render succeeded on {acc} ({client.session})")
            return meta
        except Exception as exc:
            last_exc = exc
            logger.warning(f"Colab account {acc} failed: {exc}. Trying next candidate...")
            continue
        finally:
            if lock_fd:
                try:
                    fcntl.flock(lock_fd, fcntl.LOCK_UN)
                    lock_fd.close()
                except Exception:
                    pass

    raise RuntimeError(f"All Colab accounts unavailable for T4 NVENC render: {last_exc}")


def stitch_hybrid_scene_groups_and_package(
    channel_slug: str,
    aspect: str,
    shots: list[dict[str, Any]],
    tasks: list[VideoClipTask],
    beat_durations: list[float],
    audio_path: Path,
    ass_path: Path,
    srt_path: Path,
    watermark_png: Path,
    out_mp4: Path,
    fps: int = 30,
    xfade_pivot_sec: float = 0.24,
    render_backend: str = "colab_nvenc",
    job_id: str | None = None,
    dry_run: bool = False,
    colab_account: str | None = None,
) -> dict[str, Any]:
    """Canonical remote Colab Tesla T4 FFmpeg h264_nvenc hybrid scene-group stitcher & compositor.
    Zero local CPU video encoding in live production (dry_run synthetic stub only for unit tests).
    """
    is_short = aspect == "9:16"
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    scratch = out_mp4.parent / f"_hybrid_stitch_{aspect.replace(':', 'x')}"
    scratch.mkdir(parents=True, exist_ok=True)

    # Partition tasks into contiguous scene groups based on `continues_prev`
    groups: list[list[int]] = []
    for idx, shot in enumerate(shots):
        continues_prev = bool(shot.get("continues_prev", False)) and idx > 0
        if not groups or not continues_prev:
            groups.append([idx])
        else:
            groups[-1].append(idx)

    group_spoken_durs: list[float] = [
        round(sum(float(beat_durations[i]) for i in indices), 4) for indices in groups
    ]

    if dry_run:
        tw, th = (1080, 1920) if is_short else (1920, 1080)
        dur = max(0.5, sum(beat_durations))
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=c=black:s={tw}x{th}:d={dur:.3f}:r={fps}",
                "-i",
                str(audio_path.resolve()),
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-t",
                f"{dur:.3f}",
                str(out_mp4.resolve()),
            ],
            check=True,
            capture_output=True,
        )
        meta = probe_video_clip(out_mp4)
        meta["video_encoder"] = "dry_run_stub"
        meta["colab_account"] = None
        meta["colab_session"] = None
    else:
        if render_backend != "colab_nvenc":
            raise ValueError(
                f"Unsupported live render_backend={render_backend!r}; local CPU rendering has been purged in favor of 'colab_nvenc'."
            )
        logger.info(f"Submitting 100% remote Colab Tesla T4 FFmpeg h264_nvenc render for {out_mp4.name}...")
        meta = package_final_on_colab_t4_nvenc(
            channel_slug=channel_slug,
            job_id=job_id or out_mp4.stem,
            aspect=aspect,
            groups=groups,
            tasks=tasks,
            group_spoken_durs=group_spoken_durs,
            beat_durations=beat_durations,
            audio_path=audio_path,
            ass_path=ass_path,
            srt_path=srt_path,
            watermark_png=watermark_png,
            out_mp4=out_mp4,
            fps=fps,
            xfade_pivot_sec=xfade_pivot_sec,
            overscan_crop=1.05,
            scratch_dir=scratch,
            colab_account=colab_account,
        )

    if srt_path.is_file():
        shutil.copy2(srt_path, out_mp4.with_suffix(".srt"))
    if is_short and ass_path.is_file():
        shutil.copy2(ass_path, out_mp4.with_suffix(".ass"))

    shutil.rmtree(scratch, ignore_errors=True)
    return meta


def produce_dynamic_flow_demo(
    spec_data: dict[str, Any],
    max_workers: int = 6,
    resume: bool = True,
    dry_run: bool = False,
    render_backend: str = "colab_nvenc",
    teardown_colab: bool = False,
    output_root: Path | None = None,
    colab_account: str | None = None,
) -> dict[str, Any]:
    """Run full Audio-First Beat-Locked Dynamic Google Flow Video Pipeline (with 0-credit slide fallback)."""
    t0 = time.monotonic()
    channel_slug = str(spec_data["channel_slug"]).strip().replace("_", "-")
    aspect = str(spec_data.get("aspect", "9:16")).strip()
    aspect_tag = aspect.replace(":", "x")
    shots = list(spec_data["shots"])
    target_cfg = COMPETITOR_VIDEO_TARGETS.get(channel_slug, {})
    voice = str(spec_data.get("voice") or target_cfg.get("voice") or "en-US-AndrewNeural")

    job_id = str(spec_data.get("job_id") or f"{channel_slug}-v3-demo-{aspect_tag}")
    run_dir = (output_root or V3_DEMOS_ROOT) / job_id
    audio_dir = run_dir / "audio"
    subs_dir = run_dir / "subs"
    flow_work_dir = run_dir / "flow_chain"
    video_out_dir = ROOT_DIR / "video" / job_id
    run_dir.mkdir(parents=True, exist_ok=True)
    video_out_dir.mkdir(parents=True, exist_ok=True)

    summary_path = run_dir / "demo_summary.json"
    final_mp4 = video_out_dir / f"{job_id}.mp4"
    if resume and final_mp4.is_file() and summary_path.is_file():
        logger.info(f"[{job_id}] Video already completed and verified -> {final_mp4}")
        return json.loads(summary_path.read_text(encoding="utf-8"))

    # 1. Audio-First Synthesis (Exact WordBoundary + Competitor Breath Pauses + -11.0 LUFS)
    cached_wav = audio_dir / "narration.wav"
    cached_align = audio_dir / "word_alignment.json"
    if resume and cached_wav.is_file() and cached_align.is_file():
        align_data = json.loads(cached_align.read_text(encoding="utf-8"))
        cached_beats = list(align_data.get("beat_durations_sec") or [])
        if len(cached_beats) == len(shots):
            norm_wav = cached_wav
            total_audio_dur = float(align_data["total_duration_sec"])
            beat_durations = [float(x) for x in cached_beats]
            global_words = list(align_data.get("words") or [])
            logger.info(f"[{job_id}] Step 1/4: Reusing cached voiceover & alignment ({total_audio_dur:.2f}s)...")
        else:
            norm_wav, total_audio_dur, beat_durations, global_words = synthesize_beats_with_competitor_cadence(
                beats=shots, voice=voice, audio_dir=audio_dir
            )
    else:
        logger.info(f"[{job_id}] Step 1/4: Synthesizing voiceover ({voice}) and measuring exact beat durations...")
        norm_wav, total_audio_dur, beat_durations, global_words = synthesize_beats_with_competitor_cadence(
            beats=shots,
            voice=voice,
            audio_dir=audio_dir,
        )
    ass_path = subs_dir / "subtitles_kinetic_9x16.ass"
    srt_path = subs_dir / "subtitles.srt"
    build_vn_kinetic_1word_ass_and_srt(
        beats=shots,
        beat_durations=beat_durations,
        global_words=global_words,
        total_dur=total_audio_dur,
        ass_path=ass_path,
        srt_path=srt_path,
    )
    logger.info(
        f"[{job_id}] Audio locked: total={total_audio_dur:.2f}s across {len(beat_durations)} shots "
        f"({[round(d, 2) for d in beat_durations]}), {len(global_words)} words."
    )

    # 2. Verify True Channel Emblem Watermark (100x100 squircle, radius=16, opacity=0.92)
    watermark_png = run_dir / "watermark_100x100.png"
    make_channel_watermark(channel_slug, watermark_png, size=100)

    # 3. Credit-Gated Priority Check (Priority 1 = Dynamic Flow Video; Priority 2 = 0-Credit Slide Fallback)
    ledger = CreditLedger()
    eligible_video_profiles = ledger.select_eligible_profiles(PROFILES, min_credits=MIN_VIDEO_CREDITS)
    has_video_credits = len(eligible_video_profiles) > 0

    frames_dir = flow_work_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    xfade_pivot_sec = 0.24
    scene_pairs = build_scene_pairs_from_shots(
        channel_slug=channel_slug,
        shots=shots,
        beat_durations=beat_durations,
        frames_dir=frames_dir,
        xfade_pivot_sec=xfade_pivot_sec,
    )

    chain_mode = ChainMode.SCENE_PAIRS if has_video_credits else ChainMode.ZERO_CREDIT_FLIPBOOK
    logger.info(
        f"[{job_id}] Step 2/4: Credit-Gate -> {len(eligible_video_profiles)} video-eligible profiles "
        f"(>= {MIN_VIDEO_CREDITS} credits). Selected mode: {chain_mode.value.upper()}."
    )

    chain_spec = VideoChainSpec(
        job_id=job_id,
        mode=chain_mode,
        aspect=aspect,
        video_model="omni_flash",
        duration_seconds=6,
        scene_pairs=scene_pairs,
        audio_path=None,
        no_talking_prompt_guard=True,
        keep_veo_audio=False,
        target_fps=30,
        normalize_audio_lufs=False,
        auto_duration=True,
        auto_fallback_zero_credit=False if has_video_credits else True,
        channel_id=channel_slug,
        overscan_crop=1.05,
    )
    (run_dir / "chain_spec.json").write_text(
        json.dumps(chain_spec.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    eff_workers = min(max_workers, max(1, len(eligible_video_profiles))) if has_video_credits else max_workers
    orchestrator = FlowVideoChainOrchestrator(
        spec=chain_spec,
        work_dir=flow_work_dir,
        output_mp4_path=flow_work_dir / "raw_stitched_preview.mp4",
        max_workers=eff_workers,
        headless=True,
        resume=resume,
        dry_run=dry_run,
        skip_stitch=True,
    )
    chain_report = orchestrator.run()

    # Reload completed tasks from manifest for final hybrid stitching & frame packaging
    manifest_data = json.loads((flow_work_dir / "chain_manifest.json").read_text(encoding="utf-8"))
    completed_tasks = [VideoClipTask.from_dict(td) for td in manifest_data["tasks"]]
    if has_video_credits and not dry_run:
        flipbook_leaks = [
            t.clip_id
            for t in completed_tasks
            if t.profile_used == "local_zero_credit_flipbook"
            or not Path(t.output_mp4_path).with_suffix(".json").is_file()
        ]
        if flipbook_leaks:
            raise RuntimeError(
                f"[{job_id}] Strict Dynamic Video Gate failed: clips {flipbook_leaks} fell back to static flipbook or lack .json sidecar!"
            )

    final_mp4 = video_out_dir / f"{job_id}.mp4"
    actual_mode = str(chain_report.get("mode", chain_mode.value))

    logger.info(f"[{job_id}] Step 3/4: Packaging final {aspect} video -> {final_mp4} (mode={actual_mode})...")
    if actual_mode == ChainMode.ZERO_CREDIT_FLIPBOOK.value and not dry_run:
        # Pure 0-credit slide fallback uses V2 supersampled zero-snap zoompan + xfade
        fallback_frames = [Path(t.start_frame_path) for t in completed_tasks]
        fallback_beats = [
            {
                "narration": s["narration"],
                "camera_motion": "push_in" if i % 2 == 0 else "zoom_out",
                "transition": "fade",
            }
            for i, s in enumerate(shots)
        ]
        render_vn_frame_video(
            frames=fallback_frames,
            beats=fallback_beats,
            beat_durations=beat_durations,
            audio_path=norm_wav,
            ass_path=ass_path,
            srt_path=srt_path,
            watermark_png=watermark_png,
            out_mp4=final_mp4,
            aspect=aspect,
        )
        final_meta = probe_video_clip(final_mp4)
        final_meta["video_encoder"] = "local_libx264"
        final_meta["colab_account"] = None
        final_meta["colab_session"] = None
    else:
        final_meta = stitch_hybrid_scene_groups_and_package(
            channel_slug=channel_slug,
            aspect=aspect,
            shots=shots,
            tasks=completed_tasks,
            beat_durations=beat_durations,
            audio_path=norm_wav,
            ass_path=ass_path,
            srt_path=srt_path,
            watermark_png=watermark_png,
            out_mp4=final_mp4,
            fps=30,
            xfade_pivot_sec=xfade_pivot_sec,
            render_backend=render_backend,
            job_id=job_id,
            dry_run=dry_run,
            colab_account=colab_account,
        )

    if teardown_colab and final_meta.get("colab_account") and final_meta.get("colab_session"):
        teardown_colab_session(final_meta["colab_account"], final_meta["colab_session"])

    # 4. Extract 1-FPS QA Frames for Visual Frame-by-Frame Verification
    qa_frames_dir = run_dir / "qa_frames_1fps"
    if qa_frames_dir.exists():
        shutil.rmtree(qa_frames_dir)
    qa_frames_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(final_mp4.resolve()),
            "-vf",
            "fps=1,scale=540:-2",
            "-q:v",
            "3",
            str(qa_frames_dir / "frame_%02ds.jpg"),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    elapsed = round(time.monotonic() - t0, 2)
    summary = {
        "job_id": job_id,
        "channel_slug": channel_slug,
        "title": spec_data.get("title", ""),
        "aspect": aspect,
        "voice": voice,
        "motion_mode": actual_mode,
        "video_encoder": final_meta.get("video_encoder", "local_libx264"),
        "colab_account": final_meta.get("colab_account"),
        "eligible_video_profiles_at_start": len(eligible_video_profiles),
        "total_audio_duration_sec": round(total_audio_dur, 3),
        "final_video_duration_sec": final_meta["duration"],
        "width": final_meta["width"],
        "height": final_meta["height"],
        "fps": final_meta["fps"],
        "nb_shots": len(shots),
        "beat_durations_sec": beat_durations,
        "total_credit_cost": chain_report.get("total_credit_cost", 0),
        "profiles_used": chain_report.get("profiles_used", []),
        "final_mp4": str(final_mp4),
        "srt_path": str(final_mp4.with_suffix(".srt")),
        "ass_path": str(final_mp4.with_suffix(".ass")) if aspect == "9:16" else None,
        "qa_frames_dir": str(qa_frames_dir),
        "elapsed_seconds": elapsed,
    }
    (run_dir / "demo_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    logger.info(
        f"[✓] [{job_id}] Completed in {elapsed:.1f}s -> {final_mp4} "
        f"({final_meta['width']}x{final_meta['height']}, {final_meta['duration']:.2f}s, "
        f"encoder={summary['video_encoder']}, credits={summary['total_credit_cost']}, mode={actual_mode})"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Produce V3 English Channel Logos & Dynamic Flow Video Demos")
    parser.add_argument(
        "--regenerate-logos",
        action="store_true",
        help="Regenerate clean 1:1 zero-text brand emblems via Flow CDP for English channels",
    )
    parser.add_argument(
        "--channels",
        type=str,
        default=None,
        help="Comma-separated channel slugs for --regenerate-logos (default: all 18 English channels)",
    )
    parser.add_argument(
        "--demo-key",
        type=str,
        default=None,
        help="Curated demo key to produce (e.g., 'en-wallet-anatomy:9x16', 'en-first-principles:9x16', 'en-first-principles:16x9')",
    )
    parser.add_argument(
        "--spec-json",
        "--chain-spec",
        dest="spec_json",
        type=str,
        default=None,
        help="Custom JSON spec file path to produce a dynamic Flow video demo",
    )
    parser.add_argument(
        "--output-root",
        type=str,
        default=None,
        help="Output root directory for runs (defaults to sys/runs/en_flow_v3_demos)",
    )
    parser.add_argument(
        "--colab-account",
        type=str,
        default=None,
        help="Preferred Colab T4 account for NVENC render",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=6,
        help="Max concurrent Flow CDP workers (default: 6)",
    )
    parser.add_argument(
        "--render-backend",
        choices=["colab_nvenc"],
        default="colab_nvenc",
        help="Canonical packaging render backend: remote Colab Tesla T4 FFmpeg h264_nvenc (default: colab_nvenc)",
    )
    parser.add_argument(
        "--teardown-colab",
        action="store_true",
        help="Cleanly stop Colab sessions after batch completion",
    )
    parser.add_argument("--no-resume", action="store_true", help="Force fresh generation without resuming cached clips")
    parser.add_argument("--dry-run", action="store_true", help="Run synthetic dry-run without opening Chrome")
    args = parser.parse_args()

    if args.output_root:
        global V3_DEMOS_ROOT
        V3_DEMOS_ROOT = Path(args.output_root)

    if args.colab_account:
        os.environ["VP_COLAB_ACCOUNT"] = str(args.colab_account).strip()

    try:
        if args.regenerate_logos:
            slugs = [s.strip() for s in args.channels.split(",") if s.strip()] if args.channels else None
            regenerate_channel_logos(channels=slugs, max_workers=args.max_workers, force=args.no_resume)

        if args.demo_key:
            keys = [k.strip() for k in args.demo_key.split(",") if k.strip()]
            for k in keys:
                spec_dict = CURATED_V3_DEMO_SPECS.get(k)
                if spec_dict is None:
                    candidate = Path(f"sys/channels/en_flow_v3_specs/{k.replace(':', '_')}.json")
                    if candidate.exists():
                        spec_dict = json.loads(candidate.read_text(encoding="utf-8"))
                    else:
                        raise KeyError(f"Unknown --demo-key '{k}'. Choices: {list(CURATED_V3_DEMO_SPECS.keys())} or sys/channels/en_flow_v3_specs/")
                produce_dynamic_flow_demo(
                    spec_data=spec_dict,
                    max_workers=args.max_workers,
                    resume=not args.no_resume,
                    dry_run=args.dry_run,
                    render_backend=args.render_backend,
                    teardown_colab=args.teardown_colab,
                    output_root=Path(args.output_root) if args.output_root else None,
                    colab_account=args.colab_account,
                )

        if args.spec_json:
            for raw_spec_p in [p.strip() for p in args.spec_json.split(",") if p.strip()]:
                spec_p = Path(raw_spec_p)
                data = json.loads(spec_p.read_text(encoding="utf-8"))
                produce_dynamic_flow_demo(
                    spec_data=data,
                    max_workers=args.max_workers,
                    resume=not args.no_resume,
                    dry_run=args.dry_run,
                    render_backend=args.render_backend,
                    teardown_colab=args.teardown_colab,
                    output_root=Path(args.output_root) if args.output_root else None,
                    colab_account=args.colab_account,
                )
    finally:
        get_process_manager().terminate_owned()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
