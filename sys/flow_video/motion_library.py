"""Channel-Agnostic Camera Motion, Exit Seams & Positive-Framing Library for Flow Video.

Provides:
- 6 canonical camera moves (with start-frame composition rules & Omni Frame-Link phrasing)
- 6 canonical exit seams (with start-frame setup & final-second motion sentences)
- Archetype viewing-comfort policies (strictly disables aggressive flash/edge whips
  on 2D Doodle `nao_luoi`/`en_lazy_brain` and `archetype_5_mindful_healing` channels)
- Positive-framing replacements (positive descriptors instead of negative prompt spam)
- Timecoded prompt builder (`Veo 3.1 Lite` 70-100w Seam vs `Omni 1.2 Flash` 40-70w Frame-Link).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from fx_warehouse.archetypes import get_channel_archetype  # noqa: E402

CAMERA_MOVES: dict[str, dict[str, str]] = {
    "push_in": {
        "label": "Push in",
        "composition_rule": (
            "Hero subject at mid-distance in the center third with open ground in front of the lens; "
            "subject occupies ~30% of the frame leaving clear travel runway."
        ),
        "camera_template": "Smooth camera pushes in steadily toward {subject} in {setting}, wide 28mm lens at chest height",
        "frame_link_template": (
            "Smooth camera pushes forward from {subject} in {setting} and glides seamlessly into "
            "{next_subject} in {next_setting}, wide 28mm lens"
        ),
    },
    "pull_back": {
        "label": "Pull back",
        "composition_rule": (
            "Tight framing on one striking physical detail of the hero subject (~60% of frame) "
            "whose edges hint at the wider surrounding environment."
        ),
        "camera_template": "Smooth camera pulls back from a tight view of {subject} to reveal {setting}, wide 28mm lens",
        "frame_link_template": (
            "Smooth camera pulls out from {subject} in {setting}, widens and settles onto "
            "{next_subject} in {next_setting}, wide 28mm lens"
        ),
    },
    "truck_lateral": {
        "label": "Truck (lateral)",
        "composition_rule": (
            "Hero subject placed in the left or right third, empty travel lane on the opposite side, "
            "with vertical mid-ground parallax elements (pillars, beams, trees)."
        ),
        "camera_template": "Smooth camera slides laterally sideways past foreground silhouettes to reveal {subject} in {setting}, wide 28mm lens at hip height",
        "frame_link_template": (
            "Smooth camera trucks sideways past foreground geometry from {subject} in {setting} "
            "to arrive cleanly on {next_subject} in {next_setting}, wide 28mm lens"
        ),
    },
    "tracking_alongside": {
        "label": "Tracking alongside",
        "composition_rule": (
            "Hero subject viewed side-on near the center with a continuous horizontal path or "
            "ground line crossing the frame in the direction of motion."
        ),
        "camera_template": "Smooth camera tracks laterally alongside {subject} as it progresses across {setting}, wide 28mm lens at hip height",
        "frame_link_template": (
            "Smooth camera tracks alongside {subject} in {setting} and flows directly into "
            "{next_subject} in {next_setting}, wide 28mm lens"
        ),
    },
    "orbit": {
        "label": "Orbit",
        "composition_rule": (
            "Hero subject centered and fully visible with clear margin on both sides and distinct "
            "background landmarks that reveal angular parallax during rotation."
        ),
        "camera_template": "Smooth camera orbits a gentle quarter turn around {subject} at head height in {setting}, wide 28mm lens with shifting background",
        "frame_link_template": (
            "Smooth camera orbits around {subject} in {setting} and continues smoothly round to reveal "
            "{next_subject} in {next_setting}, wide 28mm lens"
        ),
    },
    "crane_up": {
        "label": "Crane up",
        "composition_rule": (
            "Lens positioned low near ground textures in the foreground while the tall hero "
            "structure rises toward open upper sky or ceiling headroom."
        ),
        "camera_template": "Smooth camera rises vertically from low ground level beside {subject} and tilts upward across {setting}, wide 28mm lens",
        "frame_link_template": (
            "Smooth camera rises from low level beside {subject} in {setting} and tilts seamlessly "
            "into {next_subject} in {next_setting}, wide 28mm lens"
        ),
    },
}

EXIT_SEAMS: dict[str, dict[str, str]] = {
    "leaves_wipe": {
        "seam_color": "green",
        "start_image_setup": (
            "3D foreground bamboo stalks, reed blades, or lush canopy foliage framing the travel edge "
            "for deep optical parallax while keeping the midground hero subject razor-sharp."
        ),
        "final_second_sentence": (
            "In the final second, the camera executes a crisp 3D foreground bamboo and foliage parallax sweep "
            "across the frame edge while keeping the hero subject clean and sharp."
        ),
    },
    "dark_opening": {
        "seam_color": "black",
        "start_image_setup": (
            "A deep Caravaggio-lit timber archway, fortress gate shadow recess, or dark architectural threshold "
            "along the travel path."
        ),
        "final_second_sentence": (
            "In the final second, the camera glides smoothly past {prop} into a deep Caravaggio torchlit "
            "shadow archway pass at the frame edge."
        ),
    },
    "white_flash": {
        "seam_color": "white",
        "start_image_setup": (
            "A warm golden anamorphic sunbeam or flickering pitch-torch light source near the upper frame edge "
            "casting crisp directional specular highlights."
        ),
        "final_second_sentence": (
            "In the final second, a warm golden anamorphic sunbeam and torch flare sweeps diagonally across "
            "the lens near {prop} without washing out the hero subject."
        ),
    },
    "dust_smoke_cloud": {
        "seam_color": "grey",
        "start_image_setup": (
            "A subtle translucent wisp of warm torch embers and fine golden dust parallax near the outer frame edge "
            "while keeping the hero subject and face razor-sharp in clear air."
        ),
        "final_second_sentence": (
            "In the final second, the camera glides past a thin wisp of warm torch embers at the frame edge "
            "while keeping the main subject in crisp focus."
        ),
    },
    "edge_pass": {
        "seam_color": "neutral",
        "start_image_setup": (
            "A Kurosawa-style foreground architectural timber pillar, fluttering silk war-banner edge, or weathered "
            "shield edge placed cleanly along the camera travel edge."
        ),
        "final_second_sentence": (
            "In the final second, the camera sweeps smoothly past {prop} as a Kurosawa foreground pillar, "
            "silk war-banner, or shield edge wipe before clearing cleanly."
        ),
    },
    "final_hold": {
        "seam_color": "none",
        "start_image_setup": (
            "Clean, balanced hero framing centered with ample breathing headroom and crisp optical separation."
        ),
        "final_second_sentence": (
            "In the final two seconds, the camera decelerates to a steady hold with a shallow-DoF anamorphic "
            "rack-focus settle onto the hero subject."
        ),
    },
}

BEAT_PACING_ENERGY: dict[str, dict[str, str]] = {
    "hook": {"energy": "high", "speed": "brisk", "easing": "quick start easing into a steady glide"},
    "context": {"energy": "medium", "speed": "measured", "easing": "steady, constant speed"},
    "mechanism": {"energy": "calm", "speed": "deliberate", "easing": "gentle start and steady controlled pace"},
    "twist": {"energy": "highest", "speed": "swift", "easing": "starting measured and accelerating cleanly"},
    "payoff": {"energy": "calmest", "speed": "slow", "easing": "gentle start settling into a calm final hold"},
    "chapter_beat": {"energy": "medium", "speed": "steady", "easing": "smooth, even documentary glide"},
}

POSITIVE_FRAMING_REPLACEMENTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bno\s+text\b|\bzero\s+text(?:\s+overlays?)?\b", re.I), "plain unmarked surfaces"),
    (re.compile(r"\bno\s+cars\b|\bno\s+vehicles\b", re.I), "empty open ground"),
    (re.compile(r"\bno\s+people\b|\bempty\s+of\s+people\b", re.I), "uninhabited scene"),
    (re.compile(r"\bno\s+talking\b|\bno\s+speech\b", re.I), "simple still pose with closed mouth"),
    (re.compile(r"\bno\s+logos?\b|\bno\s+watermarks?\b", re.I), "clean unbranded material surfaces"),
)

_DOODLE_STATIC_OR_SOFT_CHANNELS = frozenset({"nao_luoi", "en_lazy_brain"})
_BIOMED_SPACE_CHANNELS = frozenset({"co_the_ke", "en_inside_vessel", "vu_tru_ti_hon", "en_pocket_cosmos"})
_CINEMA_35MM_CHANNELS = frozenset({"su_ke_lai"})


def get_channel_lens_spec(channel_id: str) -> str:
    """Return optical lens specification suited to the channel's visual grammar."""
    if (channel_id or "").strip().lower() in _CINEMA_35MM_CHANNELS:
        return "35mm anamorphic film lens"
    return "wide 28mm lens"


def apply_positive_framing(text: str) -> str:
    """Convert raw negative-spam clauses into positive visual surface descriptions."""
    out = (text or "").strip()
    for pat, replacement in POSITIVE_FRAMING_REPLACEMENTS:
        out = pat.sub(replacement, out)
    out = re.sub(r"\s{2,}", " ", out)
    out = re.sub(r",\s*,+", ", ", out)
    return out.strip(" ,")


def get_channel_motion_policy(channel_id: str) -> dict[str, Any]:
    """Return viewing-comfort & transition routing constraints for any of the 38 channels."""
    arch_id = get_channel_archetype(channel_id)
    if arch_id == "archetype_5_mindful_healing" or channel_id in _DOODLE_STATIC_OR_SOFT_CHANNELS:
        return {
            "channel_id": channel_id,
            "archetype_id": arch_id,
            "allow_exit_seams": False,
            "allowed_seams": ("final_hold",),
            "default_transition_mode": "soft_fade",
            "default_dissolve_sec": 0.24,
            "allowed_camera_moves": ("push_in", "pull_back", "truck_lateral"),
            "comfort_note": "Strictly calm, gentle camera motion and soft fades; aggressive flashes/edge whips banned.",
        }

    if channel_id in _BIOMED_SPACE_CHANNELS:
        allowed_seams = ("dark_opening", "white_flash", "dust_smoke_cloud", "edge_pass", "final_hold")
    else:
        allowed_seams = ("leaves_wipe", "dark_opening", "white_flash", "dust_smoke_cloud", "edge_pass", "final_hold")

    return {
        "channel_id": channel_id,
        "archetype_id": arch_id,
        "allow_exit_seams": True,
        "allowed_seams": allowed_seams,
        "default_transition_mode": "seam",
        "default_dissolve_sec": 0.18,
        "allowed_camera_moves": tuple(CAMERA_MOVES.keys()),
        "comfort_note": "Standard documentary motion & natural masked exit seams enabled.",
    }


def _timecodes_for_clip(
    clip_duration_sec: int,
    is_final_hold: bool,
    *,
    viral_v7: bool = False,
) -> tuple[str, str]:
    d = int(clip_duration_sec)
    if viral_v7:
        if d <= 4:
            return ("0-2.6s", "2.6-4s") if is_final_hold else ("0-2.8s", "2.8-4s")
        if d <= 6:
            return ("0-4.2s", "4.2-6s") if is_final_hold else ("0-4.4s", "4.4-6s")
        return ("0-4.5s", "4.5-6s") if is_final_hold else ("0-5.2s", "5.2-6.5s")
    if d <= 4:
        return ("0-3s", "3-4s") if is_final_hold else ("0-3.2s", "3.2-4s")
    if d <= 6:
        return ("0-4.5s", "4.5-6s") if is_final_hold else ("0-5s", "5-6s")
    return ("0-6s", "6-8s") if is_final_hold else ("0-6.5s", "6.5-8s")


def _normalize_tabletop_camera_sentence(cam_sentence: str) -> str:
    """Adapt human-height camera templates into overhead 45-degree tabletop phrasing."""
    replacements = (
        ("at chest height", "over the tabletop at a high 45-degree angle"),
        ("at hip height", "over the tabletop at a high 45-degree angle"),
        ("at head height in", "from a high 45-degree overhead angle in"),
        ("from low ground level beside", "from a high 45-degree tabletop angle above"),
    )
    out = cam_sentence
    for old, new in replacements:
        out = out.replace(old, new)
    if "45-degree" not in out:
        out = f"{out}, over the tabletop at a high 45-degree angle"
    return out


def build_timecoded_video_prompt(
    camera_move: str,
    hero_subject: str,
    setting: str,
    model: str = "veo_3_1_lite",
    clip_duration_sec: int = 8,
    transition_mode: str = "seam",
    exit_seam: str = "dark_opening",
    seam_prop: str = "dark doorway",
    beat_role: str = "context",
    secondary_motion: str = "subtle atmospheric dust drifting",
    has_person: bool = False,
    next_subject: str = "",
    next_location: str = "",
    style_cue: str = "consistent documentary color grading and sharp optical depth",
    anti_symbol_surfaces: str = "masts, hulls, buildings, walls, and uniforms",
    lens_spec: str = "wide 28mm lens",
    scene_type: str = "live_action",
    diegetic_audio_cue: str = "",
    viral_v7: bool = False,
) -> str:
    """Build a low-risk timecoded video prompt calibrated for Veo 3.1 Lite or Omni 1.2 Flash."""
    move_key = camera_move if camera_move in CAMERA_MOVES else "push_in"
    move_spec = CAMERA_MOVES[move_key]
    pacing = BEAT_PACING_ENERGY.get(beat_role, BEAT_PACING_ENERGY["context"])
    is_final = exit_seam == "final_hold"
    t_main, t_end = _timecodes_for_clip(clip_duration_sec, is_final, viral_v7=viral_v7)
    is_veo_lite = "lite" in (model or "").lower()
    active_lens = (lens_spec or "wide 28mm lens").strip()

    if transition_mode == "frame_link" and not is_veo_lite and next_subject and next_location and not is_final:
        cam_sentence = move_spec["frame_link_template"].format(
            subject=hero_subject,
            setting=setting,
            next_subject=next_subject,
            next_setting=next_location,
        )
        if active_lens != "wide 28mm lens":
            cam_sentence = cam_sentence.replace("wide 28mm lens", active_lens)
        person_clause = (
            "Any person remains still with a closed mouth; only the camera travels."
            if has_person
            else ""
        )
        prompt = (
            f"[{t_main}] First frame shows {hero_subject}; last frame arrives on {next_subject}. "
            f"{cam_sentence}, {pacing['speed']} pace with {pacing['easing']}. "
            f"[{t_end}] Settles smoothly into the target composition. One unbroken continuous shot, "
            f"{style_cue}. {person_clause} Silent visual storytelling, no talking, no lip movement, no music."
        )
        return re.sub(r"\s{2,}", " ", prompt).strip()

    cam_sentence = move_spec["camera_template"].format(subject=hero_subject, setting=setting)
    if active_lens != "wide 28mm lens":
        cam_sentence = cam_sentence.replace("wide 28mm lens", active_lens)
    if scene_type == "tactical_sand_table":
        cam_sentence = _normalize_tabletop_camera_sentence(cam_sentence)
    seam_spec = EXIT_SEAMS.get(exit_seam if exit_seam in EXIT_SEAMS else "dark_opening", EXIT_SEAMS["dark_opening"])
    if transition_mode == "soft_fade" and not is_final:
        end_sentence = (
            f"In the final second, the camera continues its gentle {move_spec['label'].lower()} glide cleanly without abrupt motion."
        )
    else:
        prop_val = seam_prop or ("dark architectural opening" if exit_seam == "dark_opening" else "foreground pillar edge")
        end_sentence = seam_spec["final_second_sentence"].format(prop=prop_val)

    foley_clause = str(diegetic_audio_cue or "").strip()
    if foley_clause:
        person_clause = (
            "People perform dynamic physical action with closed mouths and no spoken dialogue; only natural action and camera movement."
            if has_person
            else ""
        )
        audio_tail = (
            "Dynamic physical action with closed mouths and no spoken dialogue or background music; "
            f"synchronized diegetic sound: {foley_clause.rstrip('.')}."
        )
    else:
        person_clause = (
            "The person stays calm and almost still with a closed mouth, hands resting naturally; only the camera moves."
            if has_person
            else ""
        )
        audio_tail = "silent visual storytelling, no talking, no lip movement, no speech, no music, quiet ambient room texture only."

    if is_veo_lite:
        prompt = (
            f"[{t_main}] {cam_sentence}. The camera is already moving smoothly from the opening frame, "
            f"{pacing['speed']} pace with {pacing['easing']}. Subtle natural secondary motion only: {secondary_motion}. "
            f"[{t_end}] {end_sentence} Single unbroken continuous shot staying strictly in {setting}, {style_cue}, "
            f"light natural motion blur only on fast movement. {person_clause} "
            f"Plain unmarked {anti_symbol_surfaces} with zero flags, insignia, letters, logos, or numbers; "
            f"{audio_tail}"
        )
    else:
        non_lite_tail = audio_tail if foley_clause else "silent visual storytelling, no talking, no lip movement."
        prompt = (
            f"[{t_main}] {cam_sentence}, {pacing['speed']} pace ({pacing['easing']}), {secondary_motion}. "
            f"[{t_end}] {end_sentence} One continuous shot, {style_cue}. {person_clause} "
            f"Plain unmarked surfaces, {non_lite_tail}"
        )

    return re.sub(r"\s{2,}", " ", prompt).strip()
