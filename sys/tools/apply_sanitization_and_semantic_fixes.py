#!/usr/bin/env python3
"""Apply semantic alignment fixes and scrub banned texture words across all 36 English packages.

SSOT Governance:
- BANNED texture words: woodcut, scratchboard, stipple, hedcut, halftone, etching, engraving, intaglio,
  linocut, charcoal, copperplate, risograph, lithograph, gouge lines.
- Replaced with: 'clean flat-vector illustration, crisp smooth outlines, flat color fills' (or clean context equivalents).
- Semantic alignment: ensure each scene's visual prompts illustrate its narration line.
- Narration, scene IDs, timing, beats, character IDs kept 100% untouched.
- Image hashes (sha256) preserved consistent with image files on disk.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

BANNED_TEXTURE_TERMS = [
    "woodcut",
    "scratchboard",
    "stipple",
    "hedcut",
    "halftone",
    "etching",
    "engraving",
    "intaglio",
    "linocut",
    "charcoal",
    "copperplate",
    "risograph",
    "lithograph",
    "gouge lines",
]

CLEAN_REPLACEMENT = "clean flat-vector illustration, crisp smooth outlines, flat color fills"

_TEXTURE_PATTERN = re.compile(
    r"(?:(?<=\b)|(?<=[_-]))(?:woodcuts?|scratchboards?|stippl(?:e|ing|ed)?|hedcuts?|halftones?|etchings?|engravings?|intaglios?|linocuts?|copperplates?|risographs?|lithographs?|gouge\s+lines?)(?:(?=\b)|(?=[_-]))",
    re.IGNORECASE,
)

# Handle charcoal specially so "charcoal canvas" becomes "deep slate canvas", "charcoal coat" becomes "dark slate coat"
_CHARCOAL_CANVAS_RE = re.compile(r"\b(?:solid\s+)?charcoal\s+canvas\b", re.IGNORECASE)
_CHARCOAL_COAT_RE = re.compile(r"\bcharcoal(?:-black)?\s+trench\s+coat\b", re.IGNORECASE)
_CHARCOAL_COLOR_RE = re.compile(r"\b(?:slate\s+)?charcoal\b(?:\s+\(#[a-fA-F0-9]{6}\))?", re.IGNORECASE)


def scrub_texture_words(text: str) -> str:
    """Scrub banned texture terms and replace with clean flat vector style."""
    if not text:
        return ""
    # Specific contextual charcoal replacements
    cleaned = _CHARCOAL_CANVAS_RE.sub("flat solid deep slate canvas", text)
    cleaned = _CHARCOAL_COAT_RE.sub("dark slate trench coat", cleaned)
    # Generic texture replacements
    cleaned = _TEXTURE_PATTERN.sub(CLEAN_REPLACEMENT, cleaned)
    # Remaining charcoal uses (pencils, sketches, linework, etc.)
    cleaned = _CHARCOAL_COLOR_RE.sub(CLEAN_REPLACEMENT, cleaned)

    # Collapse repeated replacements
    rep = re.escape(CLEAN_REPLACEMENT)
    cleaned = re.sub(rf"(?:{rep}(?:\s*(?:and|,|&)\s*)?)+", CLEAN_REPLACEMENT, cleaned)
    # Clean up awkward double phrases like "clean flat-vector illustration... print"
    cleaned = re.sub(rf"{rep}\s+print\b", CLEAN_REPLACEMENT, cleaned)
    cleaned = re.sub(rf"{rep}\s+illustration\b", CLEAN_REPLACEMENT, cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


# Precise semantic alignments for en-lazy-brain-batch1-16x9
LAZY_BRAIN_16X9_IMAGES: Dict[str, str] = {
    # SC01: The Blinking Cursor Trap
    "SC01_I1": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman in cobalt-blue shirt sitting at an empty wooden desk staring paralyzed at an open laptop screen, >=75% negative space, zero clutter.",
    "SC01_I2": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A clean mechanical clock on the wall ticking past four hours in warm amber wash #E88D2A, >=75% negative space, zero clutter.",
    "SC01_I3": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A single glowing red vertical cursor blinking like an interrogation light against a blank screen, >=75% negative space, zero clutter.",
    "SC01_I4": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A small mechanical 90-second sand hourglass resting beside a clean blank paper sheet, >=75% negative space, zero clutter.",
    "SC01_I5": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman in cobalt t-shirt clutching chest in sudden physical tension, >=75% negative space, zero clutter.",
    "SC01_I6": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman frantically wiping a tidy desk with a small feather duster in extreme procrastination, >=75% negative space, zero clutter.",
    # SC02: The False Fatigue of Freeze Mode
    "SC02_I1": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman in cobalt t-shirt slumped completely flat across an empty wooden desk like a deflated balloon under an overhead lamp, >=75% negative space, zero clutter.",
    "SC02_I2": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman struggling to carry three heavy stone cinderblocks up a single clean flight of stairs, >=75% negative space, zero clutter.",
    "SC02_I3": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman looking into a small vanity mirror with a harsh thought bubble reflecting self-blame, >=75% negative space, zero clutter.",
    "SC02_I4": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A clean anatomical brain profile with frontal lobes highlighted in glowing cobalt blue, >=75% negative space, zero clutter.",
    "SC02_I5": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman sitting motionless on a stool beneath an empty battery meter showing zero energy expended, >=75% negative space, zero clutter.",
    "SC02_I6": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. An erratic alarm bell clapper ringing wildly above a highlighted prefrontal cortex profile, >=75% negative space, zero clutter.",
    # SC03: The Savanna Threat Radar
    "SC03_I1": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A clean brain profile pinpointing the almond-shaped amygdala pulsing in rich crimson ink, >=75% negative space, zero clutter.",
    "SC03_I2": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A vintage circular radar scanner sweeping across a dial detecting a single threat blip, >=75% negative space, zero clutter.",
    "SC03_I3": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Prehistoric hunter stickman crouching low in wind-blown savanna grass watching for danger, >=75% negative space, zero clutter.",
    "SC03_I4": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A primeval saber-tooth cat shadow silhouette leaping in raw black brush ink, >=75% negative space, zero clutter.",
    "SC03_I5": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. An email notification envelope glowing with a bright red warning badge, >=75% negative space, zero clutter.",
    "SC03_I6": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman face with dilated pupils reflecting the saber-tooth predator and email icon, >=75% negative space, zero clutter.",
    # SC04: The Neurobiology of Ambiguity
    "SC04_I1": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman standing before a towering question mark silhouette representing ambiguity, >=75% negative space, zero clutter.",
    "SC04_I2": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A giant stamped red wax seal reading 'DANGER' slamming down onto an innocent paper memo, >=75% negative space, zero clutter.",
    "SC04_I3": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Two vintage apothecary dropper bottles labeled adrenaline and cortisol dispensing single chemical droplets, >=75% negative space, zero clutter.",
    "SC04_I4": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stylized prefrontal neural circuits freezing over in crystalline ice patterns, >=75% negative space, zero clutter.",
    "SC04_I5": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman pulling backward against a heavy iron anchor chain labeled 'willpower myth', >=75% negative space, zero clutter.",
    "SC04_I6": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman taking cover behind a wooden desk as incoming paper notification arrows fly overhead, >=75% negative space, zero clutter.",
    # SC05: The Zeigarnik Background Drain
    "SC05_I1": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A glowing circular arrow loop that never closes spinning endlessly above stickman head, >=75% negative space, zero clutter.",
    "SC05_I2": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Vintage café vignette with psychologist Bluma Zeigarnik observing orders in quiet reflection, >=75% negative space, zero clutter.",
    "SC05_I3": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. An open mechanical filing cabinet in the brain with a single highlighted unfiled folder, >=75% negative space, zero clutter.",
    "SC05_I4": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A human silhouette showing an illuminated working memory battery draining rapidly, >=75% negative space, zero clutter.",
    "SC05_I5": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman walking down the street with a heavy persistent thought bubble carrying unfinished work, >=75% negative space, zero clutter.",
    "SC05_I6": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman tossing in bed under moonlight while a glowing unfinished email envelope floats overhead, >=75% negative space, zero clutter.",
    # SC06: The Failure of Hustle Shaming
    "SC06_I1": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. An oversized megaphone blasting aggressive motivational slogans at stickman, >=75% negative space, zero clutter.",
    "SC06_I2": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Motivational hustle posters on the wall cracking and crumbling into harmless dust, >=75% negative space, zero clutter.",
    "SC06_I3": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman grimacing under self-criticism while a tiny red megaphone whispers into ear, >=75% negative space, zero clutter.",
    "SC06_I4": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. The amygdala threat alarm bell ringing louder in response to angry internal yelling, >=75% negative space, zero clutter.",
    "SC06_I5": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman sitting cross-legged holding head in biological freeze while willpower drains, >=75% negative space, zero clutter.",
    "SC06_I6": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman lowering arms and breathing deeply as artificial hustle pressure dissolves, >=75% negative space, zero clutter.",
    # SC07: Prefrontal Energy Starvation
    "SC07_I1": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A glowing brain profile with the prefrontal cortex highlighted as a high-consumption power grid, >=75% negative space, zero clutter.",
    "SC07_I2": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A single glucose molecule glowing in golden amber light, >=75% negative space, zero clutter.",
    "SC07_I3": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A heavy metal valve struggling to balance competing threat signals and executive focus, >=75% negative space, zero clutter.",
    "SC07_I4": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Executive command signals halting before a clean red roadblock barrier in the brain, >=75% negative space, zero clutter.",
    "SC07_I5": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A laboratory beaker showing glucose liquid level dropping to the very bottom line, >=75% negative space, zero clutter.",
    "SC07_I6": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman seated before a keyboard with hands frozen above keys in mental energy exhaustion, >=75% negative space, zero clutter.",
    # SC08: The Tenacity Engine (aMCC)
    "SC08_I1": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A clean brain profile highlighting the anterior mid-cingulate cortex (aMCC) glowing in gold, >=75% negative space, zero clutter.",
    "SC08_I2": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. The aMCC illustrated as a sturdy brass steam engine piston turning a clean flywheel, >=75% negative space, zero clutter.",
    "SC08_I3": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Side-by-side growth comparison of a neural structure expanding after effortful resistance, >=75% negative space, zero clutter.",
    "SC08_I4": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman in cobalt t-shirt leaning shoulder against a heavy boulder labeled 'friction', >=75% negative space, zero clutter.",
    "SC08_I5": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Close-up of stickman's determined eye with subtle golden sparks igniting in the pupil, >=75% negative space, zero clutter.",
    "SC08_I6": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman standing tall atop a small conquered hill of draft papers with golden sunlight, >=75% negative space, zero clutter.",
    # SC09: The 90-Second Ugly Draft
    "SC09_I1": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman pulling out a scrap piece of torn brown paper with a pencil, >=75% negative space, zero clutter.",
    "SC09_I2": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Close-up of a fountain pen scratching messy unpolished words onto lined yellow scrap paper, >=75% negative space, zero clutter.",
    "SC09_I3": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. The red threat alarm bell over the amygdala shutting down with a clean mechanical click, >=75% negative space, zero clutter.",
    "SC09_I4": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. The saber-toothed tiger silhouette deflating into a tiny harmless purring kitten on the desk, >=75% negative space, zero clutter.",
    "SC09_I5": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Three rough handwritten sentences on scrap paper surrounded by calm blue pencil correction marks, >=75% negative space, zero clutter.",
    "SC09_I6": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman calmly holding an editor pencil comfortably reshaping the draft with a relaxed smile, >=75% negative space, zero clutter.",
    # SC10: Action Precedes Motivation
    "SC10_I1": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman sitting on a bench watching calendar pages blow away in wind, waiting for inspiration, >=75% negative space, zero clutter.",
    "SC10_I2": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A clean equation lettered in black ink across the canvas: 'ACTION -> MOTIVATION', >=75% negative space, zero clutter.",
    "SC10_I3": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A primitive fear monster silhouette crumbling into dust as stickman walks calmly past, >=75% negative space, zero clutter.",
    "SC10_I4": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman taking a single deliberate step forward into a dense gray fog in cobalt t-shirt, >=75% negative space, zero clutter.",
    "SC10_I5": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. The gray fog evaporating into radiant open space with warm amber wash #E88D2A on the horizon, >=75% negative space, zero clutter.",
    "SC10_I6": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman standing tall with relaxed posture at an organized clean desk, >=75% negative space, zero clutter.",
    # SC11: Closing Synthesis & The Tenacity Muscle
    "SC11_I1": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman gently touching forehead with one finger as a small golden neuron star pulses, >=75% negative space, zero clutter.",
    "SC11_I2": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Clean architectural blueprint of the brain with reinforced structural beams strengthening the frontal cortex, >=75% negative space, zero clutter.",
    "SC11_I3": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. A vintage computer monitor displaying an 'OVERRIDE SURVIVAL SCRIPT' prompt with a green checkmark, >=75% negative space, zero clutter.",
    "SC11_I4": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman smiling comfortably while dropping a stamped envelope into a vintage mailbox, >=75% negative space, zero clutter.",
    "SC11_I5": "Hand-inked 2D indie explainer doodle on flat quiet solid warm cotton rag paper #F8F0DC. Stickman closing a leather sketchbook with a satisfied smile under soft warm light, >=75% negative space, zero clutter.",
    "SC11_I6": "Official Lazy Brain Lab channel endcard plate on flat quiet solid warm cotton rag paper #F8F0DC with stickman waving friendly from the corner, >=75% negative space, zero clutter.",
}

# Precise semantic alignments for en-macro-gears-batch1-16x9
MACRO_GEARS_16X9_IMAGES: Dict[str, str] = {
    # SC01: The Dark Subdivisions and Data Centers
    "SC01_I1": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A single dark silhouette of a suburban house with an unlit porch lamp under twilight, >=75% negative space, zero clutter, zero suburban sprawl.",
    "SC01_I2": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A single silent black compute rack silhouette standing in clean cream linework #EDE8DC, >=75% negative space, zero warehouse clutter.",
    "SC01_I3": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. High-voltage transmission towers with perfectly strung conductor cables drawn in clean lines, >=75% negative space, zero clutter.",
    "SC01_I4": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. An empty concrete foundation pad with disconnected heavy copper cables coiled in gravel, >=75% negative space, zero clutter.",
    "SC01_I5": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. Detailed cutaway schematic of an industrial high-voltage transformer tank with brass bushing accents, >=75% negative space, zero clutter.",
    "SC01_I6": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. An economic balance scale holding idle bond certificates tipped downward, >=75% negative space, zero clutter.",
    # SC02: The Four-Year Wait Time Explosion
    "SC02_I1": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A clean historical 12-month calendar page marked with a brass clock icon, >=75% negative space, zero clutter.",
    "SC02_I2": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A dramatic 48-month calendar timeline marked with a bold vermilion warning underline #D9381E, >=75% negative space, zero clutter.",
    "SC02_I3": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. An official Department of Energy review insignia stamped with '2028 DELIVERY' in cream lines, >=75% negative space, zero clutter.",
    "SC02_I4": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A heavy industrial transformer silhouette standing between severed power grid lines, >=75% negative space, zero clutter.",
    "SC02_I5": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A domestic three-prong wall outlet displaying zero electrical voltage in cream linework, >=75% negative space, zero clutter.",
    "SC02_I6": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. Cavernous freight shipping docks with backlogged logistics manifests and empty transformer cradles, >=75% negative space, zero clutter.",
    # SC03: Electromagnetic Step-Down Mechanics
    "SC03_I1": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A clean isolated high-voltage ceramic insulator standing in cream linework, >=75% negative space, zero clutter.",
    "SC03_I2": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A towering high-voltage transmission pylon silhouette beneath a dark twilight sky, >=75% negative space, zero clutter.",
    "SC03_I3": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A single long-distance power transmission line stretching across open space, >=75% negative space, zero clutter.",
    "SC03_I4": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A smoldering domestic copper wire vaporizing under extreme electrical voltage in vermilion wash #D9381E, >=75% negative space, zero clutter.",
    "SC03_I5": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A massive substation transformer stepping down high voltage into safe current, >=75% negative space, zero clutter.",
    "SC03_I6": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. The correspondent observing a glowing substation transformer stepping power down safely, >=75% negative space, zero clutter.",
    # SC04: The Magnetic Core Meltdown Constraint
    "SC04_I1": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. Precision cutaway of a multi-ton transformer core with laminated steel wrapped in copper turns, >=75% negative space, zero clutter.",
    "SC04_I2": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A clean sine wave oscillating at 60 Hz with dynamic magnetic flux lines, >=75% negative space, zero clutter.",
    "SC04_I3": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. Circular circulating eddy-current loops generating heat within steel core laminations, >=75% negative space, zero clutter.",
    "SC04_I4": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. Smoldering copper coil insulation degrading under excessive thermal friction in vermilion #D9381E, >=75% negative space, zero clutter.",
    "SC04_I5": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. Crystalline iron grain lattice aligned to resist magnetic friction in bullion ochre #E9C46A, >=75% negative space, zero clutter.",
    "SC04_I6": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. The correspondent examining a precision-machined transformer core lamination with focused attention, >=75% negative space, zero clutter.",
    # SC05: Editorial Verdict on Metallurgy vs Software
    "SC05_I1": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A Silicon Valley cloud server icon crashing against a heavy steel foundry crucible, >=75% negative space, zero clutter.",
    "SC05_I2": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. Exponential software code curves meeting finite blast furnace smelting capacity, >=75% negative space, zero clutter.",
    "SC05_I3": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. An industrial foundry pouring glowing molten metal into heavy ingot molds, >=75% negative space, zero clutter.",
    "SC05_I4": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A heavy steel transformer lamination sheet unrolling under massive mechanical rollers, >=75% negative space, zero clutter.",
    "SC05_I5": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. An economic balance scale comparing infinite digital cloud bandwidth against finite metallurgical foundry output, >=75% negative space, zero clutter.",
    "SC05_I6": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. The correspondent standing before an industrial steel foundry in analytical reflection, >=75% negative space, zero clutter.",
    # SC06: Grain-Oriented Electrical Steel (GOES)
    "SC06_I1": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A heavy industrial spool of Grain-Oriented Electrical Steel (GOES) sitting on clean floor, >=75% negative space, zero clutter.",
    "SC06_I2": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. Industrial cold-reduction rollers compressing steel sheets under immense hydraulic pressure, >=75% negative space, zero clutter.",
    "SC06_I3": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A microscopic view of oriented crystalline magnetic grain domains aligned in parallel, >=75% negative space, zero clutter.",
    "SC06_I4": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A clean map silhouette of the United States with a single glowing manufacturing pin in Pennsylvania, >=75% negative space, zero clutter.",
    "SC06_I5": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. Close-up map pin glowing over Butler Pennsylvania beside a specialty steel icon, >=75% negative space, zero clutter.",
    "SC06_I6": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. The correspondent holding a thin sample sheet of GOES magnetic steel in cream linework, >=75% negative space, zero clutter.",
    # SC07: The Fifty-Thousand Bespoke Specs
    "SC07_I1": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. An automotive automated assembly line with robotic arms juxtaposed against a red crossed-out transformer, >=75% negative space, zero clutter.",
    "SC07_I2": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A patchwork map of North America divided into separate electric utility service territories, >=75% negative space, zero clutter.",
    "SC07_I3": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A neat stack of conflicting utility specification manuals on a desk, >=75% negative space, zero clutter.",
    "SC07_I4": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. An engineer silhouette pausing thoughtfully beside a single drafting sheet, >=75% negative space, zero clutter.",
    "SC07_I5": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. Skilled electrical craftsmen assembling transformer core laminations by hand, >=75% negative space, zero clutter.",
    "SC07_I6": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. The correspondent holding two incompatible copper connector fittings side by side, >=75% negative space, zero clutter.",
    # SC08: The Master Coil Winder Crunch
    "SC08_I1": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A veteran coil winder with focused expression guiding heavy insulated copper wire onto a rotating mandrel, >=75% negative space, zero clutter.",
    "SC08_I2": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. An electrical arc flash bursting through insulation during laboratory tolerance testing in vermilion #D9381E, >=75% negative space, zero clutter.",
    "SC08_I3": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A five-year apprentice progression gauge tracking skills from conductor prep to master winding, >=75% negative space, zero clutter.",
    "SC08_I4": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A demographic bar chart showing senior master winders retiring while apprentice benches remain half-filled, >=75% negative space, zero clutter.",
    "SC08_I5": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A lead time hourglass where sands of production slow dramatically due to labor scarcity, >=75% negative space, zero clutter.",
    "SC08_I6": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. Master winder's hands inspecting coil alignment with precision calipers, >=75% negative space, zero clutter.",
    # SC09: The AI Data Center Power Grab
    "SC09_I1": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A massive industrial compute cluster warehouse silhouette standing silent at night, >=75% negative space, zero clutter.",
    "SC09_I2": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A single tall high-voltage transmission pole silhouette feeding a private server farm, >=75% negative space, zero clutter.",
    "SC09_I3": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A corporate bank check stamped with advance reservation markings locking factory runs through 2030, >=75% negative space, zero clutter.",
    "SC09_I4": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A municipal power order ledger stamped with 'DEFERRED' behind private tech orders, >=75% negative space, zero clutter.",
    "SC09_I5": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. An aging municipal substation with weathered rust-streaked transformers waiting for replacements, >=75% negative space, zero clutter.",
    "SC09_I6": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. An economic balance scale tilted toward private infrastructure over public civic electrical grids, >=75% negative space, zero clutter.",
    # SC10: The Speed Limit of Physical Manufacturing
    "SC10_I1": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A massive industrial gear train where a small gear halts against a heavy steel cog, >=75% negative space, zero clutter.",
    "SC10_I2": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. Three modern icons: an electric charging station, a wind turbine, and a neural network chip, >=75% negative space, zero clutter.",
    "SC10_I3": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A single steel coil icon funneling into thousands of industrial applications across North America, >=75% negative space, zero clutter.",
    "SC10_I4": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A download progress bar failing at 99% beside an unyielding steel transformer, >=75% negative space, zero clutter.",
    "SC10_I5": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. An immense steel transformer core holding up digital cloud infrastructure, >=75% negative space, zero clutter.",
    "SC10_I6": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A single clean hairline crack across a dark glass insulator, >=75% negative space, zero clutter.",
    # SC11: Grid Standardization and the Real Economy
    "SC11_I1": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A standardized universal transformer specification sheet stamped 'STANDARDIZED', >=75% negative space, zero clutter.",
    "SC11_I2": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A new domestic steel rolling mill facility breaking ground beside modern apprentice training workshop, >=75% negative space, zero clutter.",
    "SC11_I3": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A multi-year calendar showing lead times decreasing back to 12 months in serene teal #2A9D8F, >=75% negative space, zero clutter.",
    "SC11_I4": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. The correspondent in navy suit pointing forward with analytical authority, >=75% negative space, zero clutter.",
    "SC11_I5": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. A massive interlocking brass industrial gear #C98A2C rotating smoothly, >=75% negative space, zero clutter.",
    "SC11_I6": "Tactile 2D letterpress print on flat quiet solid navy financial paper #0E1A2B. Macro Gears official channel emblem featuring an engraved gear and clean typography, >=75% negative space, zero clutter.",
}


def process_package(pkg_dir: Path) -> Tuple[int, int]:
    """Process a single package directory: apply semantic fixes and scrub texture words.

    Returns:
        (semantic_fixes_count, scrubbed_words_count)
    """
    content_file = pkg_dir / "content.json"
    images_file = pkg_dir / "images.json"
    rev_images_file = pkg_dir / "revisions/images/1/images.json"

    if not content_file.exists():
        return 0, 0

    with open(content_file, "r", encoding="utf-8") as f:
        content = json.load(f)

    with open(images_file, "r", encoding="utf-8") as f:
        images_manifest = json.load(f)

    semantic_fixes = 0
    scrubbed_count = 0
    pkg_name = pkg_dir.name

    # 1. Semantic alignment fixes for en-lazy-brain-batch1-16x9
    if pkg_name == "en-lazy-brain-batch1-16x9":
        for sc in content.get("scenes", []):
            for im in sc.get("images", []):
                iid = im["id"]
                if iid in LAZY_BRAIN_16X9_IMAGES:
                    new_d = LAZY_BRAIN_16X9_IMAGES[iid]
                    if im.get("description") != new_d:
                        im["description"] = new_d
                        im["motion_prompt"] = f"Smooth subtle camera movement focusing on {new_d[:120]}, silent storytelling, no talking"
                        if im.get("based_on"):
                            im["preserve"] = "Flat quiet solid background, palette, character silhouette"
                            im["change"] = f"Clean visible focus on {new_d[:120]}"
                        semantic_fixes += 1

    # 2. Semantic alignment fixes for en-macro-gears-batch1-16x9
    if pkg_name == "en-macro-gears-batch1-16x9":
        for sc in content.get("scenes", []):
            for im in sc.get("images", []):
                iid = im["id"]
                if iid in MACRO_GEARS_16X9_IMAGES:
                    new_d = MACRO_GEARS_16X9_IMAGES[iid]
                    if im.get("description") != new_d:
                        im["description"] = new_d
                        im["motion_prompt"] = f"Smooth subtle camera movement focusing on {new_d[:120]}, silent storytelling, no talking"
                        if im.get("based_on"):
                            im["preserve"] = "Flat quiet solid background, palette, character silhouette"
                            im["change"] = f"Clean visible focus on {new_d[:120]}"
                        semantic_fixes += 1

    # 3. Scrub texture words in content.json
    old_style = content.get("style", "")
    new_style = scrub_texture_words(old_style)
    if new_style != old_style:
        content["style"] = new_style
        scrubbed_count += 1

    for sc in content.get("scenes", []):
        old_set = sc.get("setting", "")
        new_set = scrub_texture_words(old_set)
        if new_set != old_set:
            sc["setting"] = new_set
            scrubbed_count += 1

        old_act = sc.get("action", "")
        new_act = scrub_texture_words(old_act)
        if new_act != old_act:
            sc["action"] = new_act
            scrubbed_count += 1

        for im in sc.get("images", []):
            old_desc = im.get("description", "")
            new_desc = scrub_texture_words(old_desc)
            if new_desc != old_desc:
                im["description"] = new_desc
                scrubbed_count += 1

            old_mp = im.get("motion_prompt", "")
            new_mp = scrub_texture_words(old_mp)
            if new_mp != old_mp:
                im["motion_prompt"] = new_mp
                scrubbed_count += 1

            if im.get("preserve"):
                old_p = im["preserve"]
                new_p = scrub_texture_words(old_p)
                if new_p != old_p:
                    im["preserve"] = new_p
                    scrubbed_count += 1

            if im.get("change"):
                old_c = im["change"]
                new_c = scrub_texture_words(old_c)
                if new_c != old_c:
                    im["change"] = new_c
                    scrubbed_count += 1

    # Build image map from content for images.json prompt reconstruction
    content_img_map = {}
    for sc in content.get("scenes", []):
        for im in sc.get("images", []):
            content_img_map[im["id"]] = im

    # 4. Scrub and rebuild prompts in images.json
    for item in images_manifest.get("items", []):
        iid = item.get("image_id")
        c_img = content_img_map.get(iid)
        old_prompt = item.get("prompt", "")
        old_mp = item.get("motion_prompt", "")

        # Motion prompt
        new_mp = scrub_texture_words(old_mp)
        if c_img and c_img.get("motion_prompt"):
            new_mp = c_img["motion_prompt"]
        item["motion_prompt"] = new_mp

        # Scrub prompt
        # If prompt has positive section before Negative directive
        if "Negative Visual Directive:" in old_prompt:
            pos_part, neg_part = old_prompt.split("Negative Visual Directive:", 1)
            new_pos = scrub_texture_words(pos_part)
            # If description was updated in content, reflect in Scene Composition & Action
            if c_img and "Scene Composition & Action:" in new_pos:
                pre, _ = new_pos.split("Scene Composition & Action:", 1)
                # Keep emphasis text or text policy if present
                desc = c_img["description"]
                new_pos = f"{pre}Scene Composition & Action: {desc}"
            new_prompt = f"{new_pos.rstrip()}\n\nNegative Visual Directive:{neg_part}"
        else:
            new_prompt = scrub_texture_words(old_prompt)

        if new_prompt != old_prompt:
            item["prompt"] = new_prompt
            scrubbed_count += 1

    # 5. Save content.json
    with open(content_file, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # 6. Save images.json
    with open(images_file, "w", encoding="utf-8") as f:
        json.dump(images_manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # 7. Save revisions/images/1/images.json if present
    if rev_images_file.exists():
        with open(rev_images_file, "w", encoding="utf-8") as f:
            json.dump(images_manifest, f, indent=2, ensure_ascii=False)
            f.write("\n")

    return semantic_fixes, scrubbed_count


def main() -> int:
    runs_dir = Path("sys/runs")
    pkg_dirs = sorted([p for p in runs_dir.glob("en-*-batch1-*") if p.is_dir()])
    print(f"[*] Processing {len(pkg_dirs)} English Batch 1 packages...")

    total_semantic_fixes = 0
    total_scrubs = 0
    modified_packages: List[str] = []

    for p in pkg_dirs:
        s_fixes, scrubs = process_package(p)
        if s_fixes > 0 or scrubs > 0:
            modified_packages.append(p.name)
            total_semantic_fixes += s_fixes
            total_scrubs += scrubs
            print(f"  [✓] {p.name}: {s_fixes} semantic fixes, {scrubs} scrubbed fields")

    print("\n[✓] All packages processed.")
    print(f"Total semantic fixes: {total_semantic_fixes}")
    print(f"Total scrubbed fields: {total_scrubs}")
    print(f"Total modified packages: {len(modified_packages)} / {len(pkg_dirs)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
