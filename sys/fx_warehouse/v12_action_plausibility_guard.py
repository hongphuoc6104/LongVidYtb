"""V12 Anti-Weirdness, Gesture Sanitizer & Physical-Plausibility Motion Guard.

Prevents AI video & image hallucination artifacts across historical docudrama pipelines:
1. `sanitize_action_and_gesture_prompt(prompt, *, mode="video"|"image", shot_class="")`:
   - Rewrites high-risk AI hallucination triggers into anatomically simple, physically
     grounded, historically authentic Đại Việt actions:
     * Eating / drinking into mouth (grotesque jaw/cup morphing) -> holding vessel steady
       or resting on wooden table.
     * Complex multi-finger gestures (`pointing finger`, `finger on lips`,
       `counting on fingers`, `intertwined fingers`, etc.) -> calm open palm resting on
       wooden table/hilt or dignified stillness (`anatomically accurate five-fingered
       hands in a simple relaxed grip`).
     * Tangled multi-body melee / acrobatics / spinning / backwards walking -> structured
       unidirectional formation movement or crisp single-subject framing.
     * Exaggerated grimacing / shouting / crying / mouth opening -> enforces
       `composed, historically dignified facial expression, lips naturally closed,
       zero exaggerated grimaces, zero lip movement`.
     * Anachronistic modern objects/gestures (`eyeglasses`, `wristwatch`, `metal buttons`,
       `zippers`, `modern salute`, `handshake`, `modern book spine`, `ballpoint pen`,
       `glass window panes`) -> authentic Đại Việt period equivalents.
   - Appends concise physical plausibility anchor on video prompts (`mode="video"`).
2. `audit_clip_motion_plausibility(mp4_path)`:
   - Lightweight `nice -n 15`, `-threads 1`, `256px` RGB + grayscale motion scan detecting:
     * `frame_jump_spike`: adjacent-frame L1 delta > `4.2x` median motion (catches sudden
       AI morph/flash pops),
     * `edge_flicker_warping`: severe high-frequency border oscillation / spatial warping,
     * `dead_frozen_stretch`: stalled frozen stretches inside dynamic Flow clips.
3. `render_clip_8frame_motion_strip(mp4_path, out_png)`:
   - Extracts 8 chronological frames (`t=2%, 16%, 30%, 44%, 58%, 72%, 86%, 97%`)
     horizontally tiled (`8x1`) using `nice -n 15 ffmpeg -threads 1` for visual inspection.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# Canonical Physical & Anatomical Guard Phrases
# ---------------------------------------------------------------------------

VIDEO_PHYSICAL_PLAUSIBILITY_ANCHOR: str = (
    "Grounded real-world physics and natural body weight; "
    "one single, slow, anatomically natural motion; "
    "stable object geometry with zero morphing, zero extra limbs, and zero erratic gestures."
)

DIGNIFIED_HAND_LOCK: str = (
    "anatomically accurate five-fingered hands in a simple relaxed grip"
)

COMPOSED_FACIAL_EXPRESSION_LOCK: str = (
    "composed, historically dignified facial expression, lips naturally closed, "
    "zero exaggerated grimaces, zero lip movement"
)

MOTION_STRIP_SAMPLE_RATIOS: tuple[float, ...] = (
    0.02,
    0.16,
    0.30,
    0.44,
    0.58,
    0.72,
    0.86,
    0.97,
)

DEFAULT_SPIKE_MULTIPLIER: float = 4.2
MIN_SPIKE_ABS_L1_DELTA: float = 3.5
DEFAULT_EDGE_FLICKER_THRESHOLD: float = 3.0
DEFAULT_FROZEN_DELTA_FLOOR: float = 0.06
DEFAULT_MAX_FROZEN_STRETCH_SEC: float = 1.10
DEFAULT_SCAN_MAX_EDGE_PX: int = 256
DEFAULT_NICE_LEVEL: int = 15


# ---------------------------------------------------------------------------
# Prompt Sanitization Rules
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ActionSanitizeRule:
    """Single regex detection & replacement rule for prompt sanitization."""

    category: str
    rule_id: str
    pattern: re.Pattern[str]
    replacement: str


_ACTION_SANITIZE_RULES: tuple[ActionSanitizeRule, ...] = (
    # 1. Eating / drinking into mouth -> holding vessel steady or resting on table
    ActionSanitizeRule(
        category="eating_drinking",
        rule_id="ban_drinking_into_mouth",
        pattern=re.compile(
            r"\b(?<!no\s)(?<!zero\s)(?<!without\s)(?:"
            r"(?:drinking|sipping|gulping|quaffing|chugging|slurping)"
            r"(?:\s+(?:from|down|out\s+of))?"
            r"(?:\s+(?:a\s+|an\s+|the\s+|his\s+|her\s+|their\s+)?"
            r"(?:hot\s+|warm\s+|cold\s+|herbal\s+|poisoned\s+|celadon\s+|porcelain\s+|"
            r"bronze\s+|ceramic\s+|clay\s+|bamboo\s+|wooden\s+|jade\s+)*"
            r"(?:tea\s*cups?|wine\s*cups?|cups?|bowls?|vessels?|gourds?|flasks?|goblets?|"
            r"tea|wine|water|broth|liquid))?"
            r"|"
            r"(?:raising|lifting|bringing|pressing|tilting|tipping|pouring)\s+"
            r"(?:a\s+|an\s+|the\s+|his\s+|her\s+|their\s+)?"
            r"(?:hot\s+|warm\s+|cold\s+|celadon\s+|porcelain\s+|bronze\s+|ceramic\s+|"
            r"clay\s+|bamboo\s+|wooden\s+|jade\s+)*"
            r"(?:tea\s*cups?|wine\s*cups?|cups?|bowls?|vessels?|gourds?|flasks?|goblets?|"
            r"tea|wine|water|liquid)\s+"
            r"(?:to|toward|towards|against|into)\s+"
            r"(?:his\s+|her\s+|their\s+|the\s+)?(?:open\s+|parted\s+)?(?:lips|mouth)"
            r")\b",
            re.IGNORECASE,
        ),
        replacement="holding vessel steady or resting calmly on wooden table",
    ),
    ActionSanitizeRule(
        category="eating_drinking",
        rule_id="ban_eating_into_mouth",
        pattern=re.compile(
            r"\b(?<!no\s)(?<!zero\s)(?<!without\s)(?:"
            r"(?:eating|chewing|biting\s+into|devouring|gobbling|swallowing\s+food|"
            r"stuffing\s+food(?:\s+into\s+(?:his\s+|her\s+|their\s+|the\s+)?mouth)?|"
            r"feeding\s+(?:himself|herself|themselves))"
            r"(?:\s+(?:a\s+|an\s+|the\s+|some\s+|his\s+|her\s+|their\s+)?"
            r"(?:sticky\s+|wrapped\s+|steamed\s+|dry\s+)?"
            r"(?:rice(?:\s+balls?)?|food|meal|rations?|porridge|meat|fruit|bread|noodles))?"
            r"|"
            r"putting\s+(?:food|rice(?:\s+balls?)?|meat|fruit|rations?)\s+"
            r"(?:in|into|to)\s+(?:his\s+|her\s+|their\s+|the\s+)?(?:mouth|lips)"
            r")\b",
            re.IGNORECASE,
        ),
        replacement=(
            "resting vessel and rations steadily on wooden table with "
            f"{DIGNIFIED_HAND_LOCK}"
        ),
    ),
    # 2. Complex multi-finger gestures -> calm open palm / dignified five-fingered grip
    ActionSanitizeRule(
        category="complex_finger_gesture",
        rule_id="ban_finger_on_lips",
        pattern=re.compile(
            r"\b(?:"
            r"(?:(?:pressing|raising|putting|holding|lifting|placing|touching)\s+)?"
            r"(?:a\s+|an\s+|one\s+|his\s+|her\s+|their\s+|the\s+)?"
            r"(?:single\s+|bony\s+|weathered\s+|trembling\s+|index\s+|fore)?"
            r"fingers?\s+(?:on|onto|to|against|over|across)\s+"
            r"(?:his\s+|her\s+|their\s+|the\s+)?(?:closed\s+|pursed\s+|sealed\s+)?lips"
            r"|"
            r"shushing\s+gestures?"
            r")\b",
            re.IGNORECASE,
        ),
        replacement=(
            "dignified stillness with calm open palm resting on wooden table, "
            f"{DIGNIFIED_HAND_LOCK}"
        ),
    ),
    ActionSanitizeRule(
        category="complex_finger_gesture",
        rule_id="ban_pointing_finger",
        pattern=re.compile(
            r"\b(?:"
            r"(?:pointing|wagging|crooking|beckoning\s+with)\s+"
            r"(?:a\s+|an\s+|one\s+|his\s+|her\s+|their\s+|the\s+)?"
            r"(?:single\s+|bony\s+|weathered\s+|trembling\s+|accusing\s+|index\s+|fore)?"
            r"fingers?(?:\s+(?:at|toward|towards|forward|upward|outward))?"
            r"|"
            r"(?:index\s+|accusing\s+|outstretched\s+)?pointing\s+fingers?"
            r")\b",
            re.IGNORECASE,
        ),
        replacement=(
            "calm open palm resting on wooden table or hilt, "
            f"{DIGNIFIED_HAND_LOCK}"
        ),
    ),
    ActionSanitizeRule(
        category="complex_finger_gesture",
        rule_id="ban_counting_on_fingers",
        pattern=re.compile(
            r"\b(?:"
            r"counting(?:\s+\w+)?\s+on\s+(?:his\s+|her\s+|their\s+|the\s+)?fingers"
            r"|"
            r"ticking\s+off(?:\s+\w+)?\s+on\s+(?:his\s+|her\s+|their\s+|the\s+)?fingers"
            r")\b",
            re.IGNORECASE,
        ),
        replacement=(
            "calm open palm resting on wooden table, "
            f"{DIGNIFIED_HAND_LOCK}"
        ),
    ),
    ActionSanitizeRule(
        category="complex_finger_gesture",
        rule_id="ban_intertwined_and_intricate_fingers",
        pattern=re.compile(
            r"\b(?:"
            r"(?:intertwined|interlaced|interlocking|interlocked|entangled|"
            r"crossed|knotted|twisting|contorted)\s+fingers"
            r"|"
            r"fingers\s+(?:intertwined|interlaced|interlocked|entangled|crossed)"
            r"|"
            r"snapping\s+(?:his\s+|her\s+|their\s+)?fingers"
            r"|"
            r"wringing\s+(?:his\s+|her\s+|their\s+)?hands"
            r"|"
            r"(?<!zero\s)(?<!no\s)(?:frantic|rapid)\s+hand\s+(?:waving|gestures?|movements?)"
            r"|"
            r"(?:multi[- ]object\s+)?juggling(?:\s+\w+)?"
            r"|"
            r"tying\s+(?:straw\s+)?sandal\s+(?:straps?|cords?|laces?)"
            r")\b",
            re.IGNORECASE,
        ),
        replacement=(
            "dignified stillness with calm open palm resting on hilt, "
            f"{DIGNIFIED_HAND_LOCK}"
        ),
    ),
    # 3. Tangled multi-body melee / acrobatics / spinning / backwards walking
    ActionSanitizeRule(
        category="chaotic_multi_body_or_acrobatics",
        rule_id="ban_tangled_multi_body_melee",
        pattern=re.compile(
            r"\b(?:"
            r"tangled\s+(?:multi[- ]body\s+)?(?:melee|combat|fighting|bodies|limbs)"
            r"|"
            r"multi[- ]body\s+(?:tangled\s+)?melee"
            r"|"
            r"multi[- ]limb\s+(?:grappling|wrestling|combat)"
            r"|"
            r"chaotic\s+(?:multi[- ]body\s+)?(?:melee|brawl|scrum|grappling|dogpile|pileup)"
            r"|"
            r"(?:grappling|wrestling)\s+(?:in\s+a\s+tangle|on\s+the\s+ground|chaotically)"
            r"|"
            r"entangled\s+(?:soldiers|warriors|fighters|bodies|limbs)"
            r"|"
            r"climbing\s+awkwardly\s+into\s+(?:a\s+|the\s+)?hammock"
            r")\b",
            re.IGNORECASE,
        ),
        replacement=(
            "structured unidirectional formation movement with crisp single-subject framing"
        ),
    ),
    ActionSanitizeRule(
        category="chaotic_multi_body_or_acrobatics",
        rule_id="ban_acrobatics_and_spinning",
        pattern=re.compile(
            r"\b(?:"
            r"acrobatics?|acrobatic\s+(?:flips?|leaps?|jumps?|stunts?|kicks?|combat)"
            r"|"
            r"backflips?|frontflips?|somersaults?|cartwheels?"
            r"|"
            r"mid[- ]air\s+(?:flips?|twists?|kicks?|spins?)|flying\s+kicks?|wuxia\s+wirework"
            r"|"
            r"pirouett(?:e|es|ing)|360[- ]degree\s+(?:body\s+)?spins?"
            r"|"
            r"twirling\s+(?:wildly|rapidly|around|body)"
            r"|"
            r"spinning\s+(?:wildly|rapidly|around|kick|slash|warrior|soldier|guard|body)"
            r"|"
            r"(?<!wooden\s)(?<!silk\s)spinning(?!\s+(?:wheel|wheels|jenny|top|tops|reel|spindle))"
            r")\b",
            re.IGNORECASE,
        ),
        replacement=(
            "crisp single-subject framing with structured unidirectional formation movement"
        ),
    ),
    ActionSanitizeRule(
        category="chaotic_multi_body_or_acrobatics",
        rule_id="ban_backwards_walking",
        pattern=re.compile(
            r"\b(?:"
            r"backwards?\s+(?:walking|running|marching|stepping|stride)"
            r"|"
            r"(?:walking|running|marching|stepping|stumbling|jogging)\s+backwards?"
            r"|"
            r"moonwalking"
            r")\b",
            re.IGNORECASE,
        ),
        replacement="structured unidirectional formation movement marching steadily forward",
    ),
    # 4. Exaggerated grimacing / shouting / crying / mouth opening
    ActionSanitizeRule(
        category="exaggerated_facial_or_open_mouth",
        rule_id="ban_grimacing_shouting_crying_open_mouth",
        pattern=re.compile(
            r"\b(?<!zero\s)(?<!no\s)(?<!without\s)(?:"
            r"exaggerated\s+grimac(?:e|es|ing)|grotesque\s+grimac(?:e|es|ing)|"
            r"(?<!exaggerated\s)grimac(?:ing|ed)|"
            r"(?:dramatic\s+)?(?:facial|face)\s+contortions?|contorted\s+face|"
            r"baring\s+(?:his\s+|her\s+|their\s+)?teeth|gnashing\s+teeth|"
            r"shouting(?:\s+(?:orders|wildly|aloud|angrily|fiercely|battle\s+cries))?|"
            r"screaming(?:\s+(?:aloud|wildly|in\s+\w+))?|"
            r"yelling(?:\s+(?:aloud|orders|wildly))?|"
            r"bellowing|shrieking|roaring\s+with\s+open\s+mouth|"
            r"crying(?:\s+(?:hysterically|bitterly|openly|profusely|aloud))?|"
            r"sobbing(?:\s+uncontrollably)?|"
            r"weeping(?:\s+(?:bitterly|openly|hysterically))?|"
            r"wailing(?:\s+aloud)?|"
            r"mouth\s+open(?:ing|ed)?(?:\s+wide)?|"
            r"wide[- ]open\s+(?:mouths?|jaws?)|open[- ]mouthed|"
            r"gaping\s+(?:mouths?|jaws?)|jaw[- ]drop(?:ping|ped)|"
            r"laughing\s+(?:wildly|hysterically|uproariously)|"
            r"talking\s+animatedly|"
            r"(?<!no\s)(?<!zero\s)lip[- ]flapping"
            r")\b",
            re.IGNORECASE,
        ),
        replacement=COMPOSED_FACIAL_EXPRESSION_LOCK,
    ),
    # 5. Anachronistic modern objects & gestures
    ActionSanitizeRule(
        category="modern_anachronism",
        rule_id="ban_eyeglasses",
        pattern=re.compile(
            r"\b(?:eye\s*glasses|reading\s+glasses|sunglasses|wire[- ]rimmed\s+glasses|spectacles)\b",
            re.IGNORECASE,
        ),
        replacement="unadorned natural eyes",
    ),
    ActionSanitizeRule(
        category="modern_anachronism",
        rule_id="ban_wristwatch",
        pattern=re.compile(
            r"\b(?:wrist\s*watch(?:es)?|pocket\s+watch(?:es)?|digital\s+watch(?:es)?|smart\s*watch(?:es)?)\b",
            re.IGNORECASE,
        ),
        replacement="plain hemp-bound silk bracer",
    ),
    ActionSanitizeRule(
        category="modern_anachronism",
        rule_id="ban_metal_buttons",
        pattern=re.compile(
            r"\b(?:shiny\s+|polished\s+)?(?:metal|brass|chrome|plastic)\s+buttons?\b",
            re.IGNORECASE,
        ),
        replacement="traditional Đại Việt cloth-knotted ties and cross-collar lapels",
    ),
    ActionSanitizeRule(
        category="modern_anachronism",
        rule_id="ban_zippers",
        pattern=re.compile(r"\bzippers?\b", re.IGNORECASE),
        replacement="woven silk sash fastening",
    ),
    ActionSanitizeRule(
        category="modern_anachronism",
        rule_id="ban_modern_salute",
        pattern=re.compile(
            r"\b(?:modern\s+(?:military\s+)?salutes?|(?:crisp\s+)?military\s+salutes?|"
            r"hand\s+salutes?\s+to\s+(?:the\s+)?(?:forehead|brow)|"
            r"saluting\s+(?:at\s+the\s+(?:forehead|brow)|modern[- ]style))\b",
            re.IGNORECASE,
        ),
        replacement="traditional Đại Việt clasped-fist bow",
    ),
    ActionSanitizeRule(
        category="modern_anachronism",
        rule_id="ban_handshake",
        pattern=re.compile(
            r"\b(?:modern\s+)?(?:handshakes?|shaking\s+hands)\b",
            re.IGNORECASE,
        ),
        replacement="traditional Đại Việt respectful clasped-hand greeting",
    ),
    ActionSanitizeRule(
        category="modern_anachronism",
        rule_id="ban_modern_book_spine",
        pattern=re.compile(
            r"\b(?:modern\s+book\s+spines?|hardcover\s+book(?:\s+spines?)?|"
            r"paperback\s+books?|modern\s+bound\s+books?)\b",
            re.IGNORECASE,
        ),
        replacement="rolled bamboo-slip scroll and stitched mulberry-paper manuscript",
    ),
    ActionSanitizeRule(
        category="modern_anachronism",
        rule_id="ban_ballpoint_pen",
        pattern=re.compile(
            r"\b(?:ballpoint\s+pens?|fountain\s+pens?|plastic\s+pens?|"
            r"modern\s+ink\s+pens?|gel\s+pens?)\b",
            re.IGNORECASE,
        ),
        replacement="bamboo calligraphy brush dipped in black pine-soot ink",
    ),
    ActionSanitizeRule(
        category="modern_anachronism",
        rule_id="ban_glass_window_panes",
        pattern=re.compile(
            r"\b(?:modern\s+|clear\s+)?(?:glass\s+window\s*panes?|"
            r"window\s*panes?\s+of\s+glass|plate[- ]glass\s+windows?|"
            r"clear\s+glass\s+windows?)\b",
            re.IGNORECASE,
        ),
        replacement="carved wooden lattice shutters and bamboo blinds",
    ),
    ActionSanitizeRule(
        category="modern_anachronism",
        rule_id="ban_modern_pop_gestures",
        pattern=re.compile(
            r"\b(?:thumbs[- ]up(?:\s+gestures?)?|peace[- ]sign(?:\s+gestures?)?|"
            r"v[- ]sign\s+fingers|high[- ]fives?|smart\s*phones?|cell\s*phones?)\b",
            re.IGNORECASE,
        ),
        replacement="dignified traditional Đại Việt posture",
    ),
    # 6. Auto-motion impact & battle-weapon boilerplate hallucination triggers (#341 / #343)
    ActionSanitizeRule(
        category="auto_motion_impact_or_boilerplate",
        rule_id="ban_snappy_prop_impact_lead",
        pattern=re.compile(
            r"\b(?:"
            r"Snappy(?:\s+\d+mm)?(?:\s+kinetic)?\s+micro-action\s+"
            r"(?:and\s+tactile\s+prop\s+impact|captures\s+immediate\s+physical\s+impact)"
            r"|"
            r"tactile\s+prop\s+impact"
            r")\b",
            re.IGNORECASE,
        ),
        replacement="Measured tactile micro-motion and crisp optical focus",
    ),
    ActionSanitizeRule(
        category="auto_motion_impact_or_boilerplate",
        rule_id="ban_forge_weapons_mud_boilerplate",
        pattern=re.compile(
            r"\bas\s+hands\s+forge,\s*write,\s*or\s+grip\s+weapons\s+and\s+tools,\s*"
            r"bodies\s+move\s+through\s+mud\s+or\s+terrain(?:\s+with\s+real\s+weight)?",
            re.IGNORECASE,
        ),
        replacement="with anatomically natural five-fingered hands and real gravity and weight",
    ),
)

_DEDUP_FACIAL_LOCK_RE = re.compile(
    rf"(?:{re.escape(COMPOSED_FACIAL_EXPRESSION_LOCK)})"
    rf"(?:\s*(?:,|;|and|or|with|while)\s*{re.escape(COMPOSED_FACIAL_EXPRESSION_LOCK)})+",
    re.IGNORECASE,
)

_DEDUP_HAND_LOCK_RE = re.compile(
    rf"({re.escape(DIGNIFIED_HAND_LOCK)})"
    rf"(?:(?:\s*(?:,|;|and)\s*[^.;]*?)?\s*{re.escape(DIGNIFIED_HAND_LOCK)})+",
    re.IGNORECASE,
)


def _clean_punctuation(text: str) -> str:
    out = re.sub(r"\s{2,}", " ", text or "")
    out = re.sub(r"\s+([,.;:!?])", r"\1", out)
    out = re.sub(r",\s*,+", ", ", out)
    out = re.sub(r"\.\s*\.+", ".", out)
    return out.strip()


def sanitize_action_and_gesture_prompt(
    prompt: str,
    *,
    mode: str = "video",
    shot_class: str = "",
) -> dict[str, Any]:
    """Sanitize risky AI gestures, facial contortions, chaotic melee, and modern anachronisms.

    Args:
        prompt: Input video motion prompt or image generation prompt.
        mode: Either `"video"` (appends physical plausibility anchor) or `"image"`.
        shot_class: Optional V12 shot class (e.g., `"MACRO_PROP"`, `"ENV_SENSORY"`, `"OTS_DIRTY"`).

    Returns:
        Dictionary containing `sanitized_prompt`, `changed`, `triggered_categories`,
        `triggered_rules`, `appended_anchor`, `enforced_facial_lock`, `mode`, and `shot_class`.
    """
    norm_mode = (mode or "video").strip().lower()
    if norm_mode not in ("video", "image"):
        raise ValueError(f"Unsupported mode={mode!r}; expected 'video' or 'image'.")

    norm_shot_class = (shot_class or "").strip().upper()
    is_zero_human_env = norm_shot_class in ("ENV_SENSORY", "ENVIRONMENTAL_SENSORY")
    original = (prompt or "").strip()
    working = original

    triggered_categories: list[str] = []
    triggered_rules: list[dict[str, str]] = []
    enforced_facial_lock = False

    for rule in _ACTION_SANITIZE_RULES:
        matches = list(rule.pattern.finditer(working))
        if not matches:
            continue

        replacement = rule.replacement
        if is_zero_human_env and rule.category in (
            "eating_drinking",
            "complex_finger_gesture",
            "exaggerated_facial_or_open_mouth",
        ):
            if rule.category == "eating_drinking":
                replacement = "ceramic vessel resting calmly on wooden table"
            elif rule.category == "complex_finger_gesture":
                replacement = "dignified architectural stillness across wooden surfaces"
            else:
                replacement = (
                    "calm atmospheric stillness, zero exaggerated grimaces, zero lip movement"
                )

        for m in matches:
            triggered_rules.append(
                {
                    "category": rule.category,
                    "rule_id": rule.rule_id,
                    "matched_text": m.group(0),
                    "replacement": replacement,
                }
            )
        if rule.category not in triggered_categories:
            triggered_categories.append(rule.category)
        if rule.category == "exaggerated_facial_or_open_mouth":
            enforced_facial_lock = True

        working = rule.pattern.sub(replacement, working)

    if COMPOSED_FACIAL_EXPRESSION_LOCK.lower() in working.lower():
        working = _DEDUP_FACIAL_LOCK_RE.sub(COMPOSED_FACIAL_EXPRESSION_LOCK, working)
        enforced_facial_lock = True

    if working.lower().count(DIGNIFIED_HAND_LOCK.lower()) > 1:
        working = _DEDUP_HAND_LOCK_RE.sub(r"\1", working)

    working = _clean_punctuation(working)

    appended_anchor = False
    if norm_mode == "video":
        anchor_low = VIDEO_PHYSICAL_PLAUSIBILITY_ANCHOR.lower()
        if anchor_low not in working.lower():
            if working:
                if working[-1] not in ".!?":
                    working = f"{working}."
                working = f"{working} {VIDEO_PHYSICAL_PLAUSIBILITY_ANCHOR}"
            else:
                working = VIDEO_PHYSICAL_PLAUSIBILITY_ANCHOR
            appended_anchor = True

    working = _clean_punctuation(working)
    return {
        "sanitized_prompt": working,
        "original_prompt": original,
        "mode": norm_mode,
        "shot_class": norm_shot_class,
        "changed": working != original,
        "is_clean_input": len(triggered_categories) == 0,
        "triggered_categories": triggered_categories,
        "triggered_rules": triggered_rules,
        "enforced_facial_lock": enforced_facial_lock,
        "appended_anchor": appended_anchor,
    }


# ---------------------------------------------------------------------------
# Lightweight Hardware-Safe Clip Motion Plausibility Scanner (`nice 15`, `-threads 1`)
# ---------------------------------------------------------------------------


def _build_nice_cmd(args: list[str], nice_level: int = DEFAULT_NICE_LEVEL) -> list[str]:
    """Prefix subprocess command with `nice -n <level>` when available on host."""
    nice_bin = shutil.which("nice")
    if nice_bin:
        return [nice_bin, "-n", str(int(nice_level)), *args]
    return list(args)


def _parse_rate(rate_str: str | None, default: float = 30.0) -> float:
    raw = (rate_str or "").strip()
    if not raw or raw == "0/0":
        return default
    if "/" in raw:
        num_s, den_s = raw.split("/", 1)
        try:
            num, den = float(num_s), float(den_s)
            return (num / den) if den > 0 and num > 0 else default
        except ValueError:
            return default
    try:
        val = float(raw)
        return val if val > 0 else default
    except ValueError:
        return default


def _probe_video_stream(
    mp4_path: Path,
    *,
    nice_level: int = DEFAULT_NICE_LEVEL,
) -> dict[str, Any]:
    """Probe width, height, fps, duration, and packet count using 1-thread `ffprobe`."""
    ffprobe_bin = shutil.which("ffprobe")
    if not ffprobe_bin:
        raise RuntimeError("ffprobe binary not found on PATH.")

    cmd = _build_nice_cmd(
        [
            ffprobe_bin,
            "-v",
            "error",
            "-threads",
            "1",
            "-count_packets",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,nb_read_packets,duration",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(mp4_path),
        ],
        nice_level=nice_level,
    )
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=30)
    if proc.returncode != 0:
        raise RuntimeError(
            f"ffprobe failed on {mp4_path}: {(proc.stderr or '').strip()}"
        )

    payload = json.loads(proc.stdout or "{}")
    streams = payload.get("streams") or []
    if not streams:
        raise RuntimeError(f"No video stream found in {mp4_path}")

    st = streams[0]
    width = int(st.get("width") or 0)
    height = int(st.get("height") or 0)
    if width <= 0 or height <= 0:
        raise RuntimeError(f"Invalid video dimensions ({width}x{height}) in {mp4_path}")

    fps = _parse_rate(st.get("avg_frame_rate")) or _parse_rate(st.get("r_frame_rate"), 30.0)
    fmt_dur = float((payload.get("format") or {}).get("duration") or 0.0)
    st_dur = float(st.get("duration") or 0.0)
    duration_sec = st_dur if st_dur > 0 else fmt_dur

    nb_frames_raw = st.get("nb_frames")
    nb_pkts_raw = st.get("nb_read_packets")
    nb_frames = 0
    for candidate in (nb_frames_raw, nb_pkts_raw):
        if candidate is not None and str(candidate).isdigit():
            nb_frames = int(candidate)
            if nb_frames > 0:
                break
    if nb_frames <= 0 and duration_sec > 0:
        nb_frames = max(1, int(round(duration_sec * fps)))
    if duration_sec <= 0 and nb_frames > 0 and fps > 0:
        duration_sec = nb_frames / fps

    return {
        "width": width,
        "height": height,
        "fps": fps,
        "duration_sec": duration_sec,
        "nb_frames": nb_frames,
    }


def _compute_scan_dimensions(
    width: int,
    height: int,
    max_edge_px: int = DEFAULT_SCAN_MAX_EDGE_PX,
) -> tuple[int, int]:
    """Scale video dimensions so the longer edge is `max_edge_px` (even integers >= 16)."""
    target = max(32, int(max_edge_px) // 2 * 2)
    if width >= height:
        scan_w = target
        scan_h = max(16, int(round(height * float(target) / float(width))) // 2 * 2)
    else:
        scan_h = target
        scan_w = max(16, int(round(width * float(target) / float(height))) // 2 * 2)
    return (scan_w, scan_h)


def audit_clip_motion_plausibility(
    mp4_path: str | Path,
    *,
    spike_multiplier: float = DEFAULT_SPIKE_MULTIPLIER,
    min_spike_abs_l1: float = MIN_SPIKE_ABS_L1_DELTA,
    edge_flicker_threshold: float = DEFAULT_EDGE_FLICKER_THRESHOLD,
    frozen_delta_floor: float = DEFAULT_FROZEN_DELTA_FLOOR,
    max_frozen_stretch_sec: float = DEFAULT_MAX_FROZEN_STRETCH_SEC,
    scan_max_edge_px: int = DEFAULT_SCAN_MAX_EDGE_PX,
    nice_level: int = DEFAULT_NICE_LEVEL,
) -> dict[str, Any]:
    """Scan an MP4 clip at 256px (`nice -n 15`, `-threads 1`) for AI motion anomalies.

    Detects:
      - `frame_jump_spike`: adjacent-frame L1 delta > `4.2x` median motion (and above
        quantization floor `min_spike_abs_l1`) catching mid-clip AI morph/flash pops.
      - `edge_flicker_warping`: severe high-frequency temporal sign-reversal flicker or
        excessive border instability relative to interior motion.
      - `dead_frozen_stretch`: contiguous frozen frame stretches >= `max_frozen_stretch_sec`.
    """
    p = Path(mp4_path)
    if not p.is_file() or p.stat().st_size == 0:
        return {
            "mp4_path": str(p),
            "passed": False,
            "status": "REJECT",
            "anomalies": ["missing_or_empty_video"],
            "frame_count": 0,
            "fps": 0.0,
            "duration_sec": 0.0,
            "scan_resolution": "0x0",
            "ffmpeg_nice_level": int(nice_level),
            "ffmpeg_threads": 1,
            "metrics": {},
        }

    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg binary not found on PATH.")

    meta = _probe_video_stream(p, nice_level=nice_level)
    scan_w, scan_h = _compute_scan_dimensions(
        meta["width"], meta["height"], max_edge_px=scan_max_edge_px
    )
    fps = float(meta["fps"] or 30.0)

    decode_cmd = _build_nice_cmd(
        [
            ffmpeg_bin,
            "-v",
            "error",
            "-threads",
            "1",
            "-i",
            str(p),
            "-vf",
            f"scale={scan_w}:{scan_h}:flags=bilinear",
            "-filter_threads",
            "1",
            "-threads",
            "1",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "pipe:1",
        ],
        nice_level=nice_level,
    )
    proc = subprocess.run(decode_cmd, capture_output=True, check=False, timeout=60)
    if proc.returncode != 0:
        return {
            "mp4_path": str(p),
            "passed": False,
            "status": "REJECT",
            "anomalies": ["corrupt_video_decode"],
            "frame_count": 0,
            "fps": round(fps, 3),
            "duration_sec": round(float(meta["duration_sec"]), 3),
            "scan_resolution": f"{scan_w}x{scan_h}",
            "ffmpeg_nice_level": int(nice_level),
            "ffmpeg_threads": 1,
            "metrics": {"stderr": (proc.stderr or b"").decode("utf-8", errors="ignore")[:300]},
        }

    frame_bytes = scan_w * scan_h * 3
    n_frames = len(proc.stdout) // frame_bytes
    if n_frames < 2:
        return {
            "mp4_path": str(p),
            "passed": False,
            "status": "REJECT",
            "anomalies": ["insufficient_frames"],
            "frame_count": int(n_frames),
            "fps": round(fps, 3),
            "duration_sec": round(float(meta["duration_sec"]), 3),
            "scan_resolution": f"{scan_w}x{scan_h}",
            "ffmpeg_nice_level": int(nice_level),
            "ffmpeg_threads": 1,
            "metrics": {},
        }

    raw = np.frombuffer(proc.stdout[: n_frames * frame_bytes], dtype=np.uint8)
    rgb = raw.reshape((n_frames, scan_h, scan_w, 3)).astype(np.float32)
    luma = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]

    # 1. Adjacent-frame RGB & Luma L1 motion deltas
    rgb_diffs = np.abs(rgb[1:] - rgb[:-1])
    frame_deltas = rgb_diffs.mean(axis=(1, 2, 3))
    luma_deltas = np.abs(luma[1:] - luma[:-1]).mean(axis=(1, 2))

    median_motion = float(np.median(frame_deltas))
    mean_motion = float(np.mean(frame_deltas))
    max_motion = float(np.max(frame_deltas))
    median_luma_motion = float(np.median(luma_deltas))

    denom = max(median_motion, 1e-3)
    spike_ratios = frame_deltas / denom
    max_spike_ratio = float(np.max(spike_ratios))

    spike_threshold_abs = max(float(min_spike_abs_l1), float(spike_multiplier) * median_motion)
    spike_mask = (frame_deltas > spike_threshold_abs) & (
        frame_deltas > float(spike_multiplier) * median_motion
    )
    spike_indices = [int(idx) for idx in np.nonzero(spike_mask)[0].tolist()]
    spike_timestamps = [round((idx + 1) / fps, 3) for idx in spike_indices]

    # 2. Outer-border temporal sign-reversal flicker & warping score
    bh = max(4, int(round(scan_h * 0.12)))
    bw = max(4, int(round(scan_w * 0.12)))
    border_mask = np.ones((scan_h, scan_w), dtype=bool)
    border_mask[bh : scan_h - bh, bw : scan_w - bw] = False
    core_mask = ~border_mask

    luma_step_diff = luma[1:] - luma[:-1]
    border_motion = float(np.abs(luma_step_diff[:, border_mask]).mean())
    core_motion = float(np.abs(luma_step_diff[:, core_mask]).mean())
    border_core_ratio = border_motion / max(core_motion, 0.25)

    edge_flicker_score = 0.0
    if n_frames >= 3:
        d1 = luma_step_diff[:-1]
        d2 = luma_step_diff[1:]
        reversal = (d1 * d2) < -36.0  # Opposite sign with >6 gray-level swing each way
        osc_mag = np.where(reversal, np.minimum(np.abs(d1), np.abs(d2)), 0.0)
        border_osc = float(osc_mag[:, border_mask].mean())
        full_osc = float(osc_mag.mean())
        edge_flicker_score = max(border_osc, full_osc * 0.85)

    # 3. Contiguous dead-frozen stretches
    frozen_steps = frame_deltas <= float(frozen_delta_floor)
    max_frozen_run = 0
    cur_run = 0
    for is_frozen in frozen_steps.tolist():
        if is_frozen:
            cur_run += 1
            if cur_run > max_frozen_run:
                max_frozen_run = cur_run
        else:
            cur_run = 0

    max_frozen_sec = max_frozen_run / fps
    frozen_ratio = float(np.mean(frozen_steps))
    actual_duration = float(meta["duration_sec"]) or (n_frames / fps)

    anomalies: list[str] = []
    if spike_indices:
        anomalies.append("frame_jump_spike")
    if edge_flicker_score > float(edge_flicker_threshold) or (
        border_core_ratio > 3.0 and border_motion > 4.5 and edge_flicker_score > 1.5
    ):
        anomalies.append("edge_flicker_warping")
    if max_frozen_sec >= float(max_frozen_stretch_sec) or (
        n_frames >= 15 and frozen_ratio >= 0.75
    ):
        anomalies.append("dead_frozen_stretch")

    return {
        "mp4_path": str(p),
        "passed": len(anomalies) == 0,
        "status": "PASS" if len(anomalies) == 0 else "REJECT",
        "anomalies": anomalies,
        "frame_count": int(n_frames),
        "fps": round(fps, 3),
        "duration_sec": round(actual_duration, 3),
        "scan_resolution": f"{scan_w}x{scan_h}",
        "ffmpeg_nice_level": int(nice_level),
        "ffmpeg_threads": 1,
        "metrics": {
            "median_frame_l1_delta": round(median_motion, 4),
            "median_luma_l1_delta": round(median_luma_motion, 4),
            "mean_frame_l1_delta": round(mean_motion, 4),
            "max_frame_l1_delta": round(max_motion, 4),
            "max_spike_ratio": round(max_spike_ratio, 4),
            "spike_ratio_threshold": float(spike_multiplier),
            "spike_frame_indices": spike_indices,
            "spike_timestamps_sec": spike_timestamps,
            "edge_flicker_score": round(edge_flicker_score, 4),
            "edge_flicker_threshold": float(edge_flicker_threshold),
            "border_to_core_motion_ratio": round(border_core_ratio, 4),
            "max_frozen_stretch_sec": round(max_frozen_sec, 4),
            "max_frozen_stretch_threshold_sec": float(max_frozen_stretch_sec),
            "frozen_frame_ratio": round(frozen_ratio, 4),
        },
    }


def _select_8_frame_indices(
    total_frames: int,
    ratios: tuple[float, ...] = MOTION_STRIP_SAMPLE_RATIOS,
) -> list[int]:
    """Map the 8 canonical percentage timestamps onto strictly distinct valid frame indices."""
    k = len(ratios)
    if total_frames <= 1:
        return [0] * k
    if total_frames <= k:
        return [min(total_frames - 1, int(round(r * (total_frames - 1)))) for r in ratios]

    raw = [min(total_frames - 1, max(0, int(round(r * (total_frames - 1))))) for r in ratios]
    # Enforce strictly increasing indices so FFmpeg `select` always emits all 8 frames
    for i in range(1, k):
        if raw[i] <= raw[i - 1]:
            raw[i] = raw[i - 1] + 1
    if raw[-1] >= total_frames:
        raw[-1] = total_frames - 1
        for i in range(k - 2, -1, -1):
            if raw[i] >= raw[i + 1]:
                raw[i] = max(0, raw[i + 1] - 1)
    return raw


def render_clip_8frame_motion_strip(
    mp4_path: str | Path,
    out_png: str | Path,
    *,
    tile_height: int = 256,
    nice_level: int = DEFAULT_NICE_LEVEL,
) -> dict[str, Any]:
    """Render an 8-frame (`t=2%, 16%, 30%, 44%, 58%, 72%, 86%, 97%`) horizontal strip PNG.

    Executes sequentially with `nice -n 15 ffmpeg -threads 1` (`tile=8x1`) for zero-lag
    visual AI inspection of gestures, limb continuity, and object stability across a clip.
    """
    src = Path(mp4_path)
    if not src.is_file() or src.stat().st_size == 0:
        raise FileNotFoundError(f"Video clip not found or empty: {src}")

    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg binary not found on PATH.")

    dst = Path(out_png)
    dst.parent.mkdir(parents=True, exist_ok=True)

    meta = _probe_video_stream(src, nice_level=nice_level)
    total_frames = max(1, int(meta["nb_frames"]))
    fps = float(meta["fps"] or 30.0)
    duration_sec = float(meta["duration_sec"] or (total_frames / fps))
    th = max(64, int(tile_height) // 2 * 2)
    tw = max(36, int(round(meta["width"] * float(th) / float(meta["height"]))) // 2 * 2)

    indices = _select_8_frame_indices(total_frames, MOTION_STRIP_SAMPLE_RATIOS)
    unique_sorted = sorted(set(indices))

    if len(unique_sorted) == len(MOTION_STRIP_SAMPLE_RATIOS):
        eq_terms = "+".join(f"eq(n\\,{idx})" for idx in indices)
        vf_expr = (
            f"select='{eq_terms}',"
            f"scale={tw}:{th}:flags=bicubic,"
            f"tile={len(MOTION_STRIP_SAMPLE_RATIOS)}x1"
        )
        cmd = _build_nice_cmd(
            [
                ffmpeg_bin,
                "-y",
                "-v",
                "error",
                "-threads",
                "1",
                "-i",
                str(src),
                "-vf",
                vf_expr,
                "-filter_threads",
                "1",
                "-threads",
                "1",
                "-vsync",
                "0",
                "-frames:v",
                "1",
                str(dst),
            ],
            nice_level=nice_level,
        )
    else:
        # Degenerate ultra-short clip (< 8 total frames): seek per ratio safely before last PTS
        max_seek = max(0.0, duration_sec - (1.2 / max(fps, 1.0)))
        in_args: list[str] = []
        filter_parts: list[str] = []
        stack_refs: list[str] = []
        for idx_k, r in enumerate(MOTION_STRIP_SAMPLE_RATIOS):
            t_seek = min(max_seek, max(0.0, r * duration_sec))
            in_args.extend(["-ss", f"{t_seek:.4f}", "-threads", "1", "-i", str(src)])
            filter_parts.append(f"[{idx_k}:v]scale={tw}:{th}:flags=bicubic[v{idx_k}]")
            stack_refs.append(f"[v{idx_k}]")
        filter_complex = (
            ";".join(filter_parts)
            + f";{''.join(stack_refs)}hstack=inputs={len(MOTION_STRIP_SAMPLE_RATIOS)}[outv]"
        )
        cmd = _build_nice_cmd(
            [
                ffmpeg_bin,
                "-y",
                "-v",
                "error",
                *in_args,
                "-filter_complex",
                filter_complex,
                "-filter_threads",
                "1",
                "-map",
                "[outv]",
                "-threads",
                "1",
                "-frames:v",
                "1",
                str(dst),
            ],
            nice_level=nice_level,
        )

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=60)
    if proc.returncode != 0 or not dst.is_file() or dst.stat().st_size == 0:
        raise RuntimeError(
            f"render_clip_8frame_motion_strip failed on {src}: {(proc.stderr or '').strip()}"
        )

    sampled_timestamps = [round(idx / max(fps, 1.0), 3) for idx in indices]
    return {
        "mp4_path": str(src),
        "out_png": str(dst),
        "tile_count": len(MOTION_STRIP_SAMPLE_RATIOS),
        "tile_width": tw,
        "tile_height": th,
        "strip_width": tw * len(MOTION_STRIP_SAMPLE_RATIOS),
        "strip_height": th,
        "sample_ratios": list(MOTION_STRIP_SAMPLE_RATIOS),
        "sampled_frame_indices": indices,
        "sampled_timestamps_sec": sampled_timestamps,
        "ffmpeg_nice_level": int(nice_level),
        "ffmpeg_threads": 1,
    }
