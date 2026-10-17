"""Desktop-only, format-aware pause planning; all waveform processing stays on Colab."""

from __future__ import annotations

import math
import re
from typing import Any

from format_profiles import get_profile
from output_contract import outputs

POLICY = "format_v1"
PAUSE_RE = re.compile(r"\[pause:\s*([0-9.]+)\s*(ms|s)?\s*\]", re.IGNORECASE)
SENTENCE_RE = re.compile(r'(?<=[.!?])\s+|(?<=[.!?]["\'”’])\s+')


def pause_seconds(value: Any) -> float:
    """Reject invalid authored holds rather than silently clamping timing."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("PAUSE_POLICY: pause must be a number between 0 and 8 seconds")
    if not math.isfinite(value) or not 0 <= value <= 8:
        raise ValueError("PAUSE_POLICY: pause must be finite and between 0 and 8 seconds")
    return float(value)


def settings_for_language(brief: dict, language: str) -> dict[str, Any]:
    """Shared-language dual outputs use one long-form track, never two conflicting clocks."""
    aspects = [plan["aspect_ratio"] for plan in outputs(brief) if plan["language"] == language]
    if not aspects:
        raise ValueError("PAUSE_POLICY: language has no output")
    aspect = "16:9" if "16:9" in aspects else aspects[0]
    profile = get_profile(aspect)
    return {"profile": profile["id"], **profile["narration_pauses"]}


def split_narration(text: str, settings: dict, *, opening: bool = False) -> list[dict[str, Any]]:
    """Keep sentence text and exact explicit gaps, including a final authored pause.

    Short means fewer than eight whitespace tokens (a Vietnamese syllable proxy).
    Commas split only utterances longer than 180 characters, as in the legacy path.
    Natural pauses inside each utterance are left to the model.
    """
    if opening and PAUSE_RE.search(text):
        raise ValueError("OPENING_SCENE_PAUSE_FORBIDDEN: SC01 cannot contain explicit pause tags")
    if re.search(r"\[pause:", PAUSE_RE.sub("", text), re.IGNORECASE):
        raise ValueError("PAUSE_POLICY: malformed pause tag")
    result: list[dict[str, Any]] = []

    def append_words(words: str) -> None:
        for sentence in SENTENCE_RE.split(words.strip()):
            parts = re.split(r"(?<=[,;:\-])\s+", sentence) if len(sentence) > 180 else [sentence]
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                terminal = part.rstrip('"\'”’')[-1:] in ".!?…"
                short = len(part.split()) < 8
                key = ("short_sentence" if short else "sentence") if terminal else "minor"
                if opening and terminal:
                    key = "opening_" + key
                result.append({"text": part, "pause": settings[key], "reason": key})

    cursor = 0
    for match in PAUSE_RE.finditer(text):
        append_words(text[cursor:match.start()])
        if not result:
            raise ValueError("PAUSE_POLICY: an explicit pause must follow spoken text")
        value = float(match.group(1))
        unit = (match.group(2) or "").lower()
        seconds = pause_seconds(value / 1000 if unit == "ms" or (not unit and value > 10) else value)
        previous = result[-1]
        if previous["reason"] == "explicit":
            seconds = round(pause_seconds(previous["pause"] + seconds), 9)
        previous.update(pause=seconds, reason="explicit")
        cursor = match.end()
    append_words(text[cursor:])
    if not result:
        raise ValueError("PAUSE_POLICY: narration must contain spoken text")
    return result


def plan_scene(
    scene: dict, text: str, language: str, settings: dict,
    retake: int, last: bool, *, opening: bool = False,
) -> tuple[dict, list[dict]]:
    """Resolve each boundary once: sentence OR explicit OR scene, plus a minimum learner hold."""
    chunks = split_narration(text, settings, opening=opening)
    hold = pause_seconds(scene.get("audio_direction", {}).get(language, {}).get("learner_pause_seconds", 0))
    final = chunks[-1]
    if final["reason"] != "explicit":
        final.update(pause=settings["tail" if last else "scene"], reason="tail" if last else "scene")
    if hold > final["pause"]:
        final.update(pause=hold, reason="learner_hold")
    request = {
        "scene_id": scene["id"], "narration": text,
        "texts": [chunk["text"] for chunk in chunks],
        "gaps": [chunk["pause"] for chunk in chunks[:-1]],
        "tail": final["pause"], "tone": scene.get("tone"), "retake": retake,
    }
    audit = [{"scene_id": scene["id"], **chunk} for chunk in chunks]
    return request, audit


def plan_tracks(brief: dict, content: dict, takes: dict, primary: str) -> tuple[list, list, dict]:
    """Apply identical planning rules to primary and secondary language tracks."""
    primary_scenes, secondary, tracks = [], [], {}
    for language in dict.fromkeys(plan["language"] for plan in outputs(brief)):
        settings = settings_for_language(brief, language)
        boundaries = []
        for index, scene in enumerate(content["scenes"]):
            text = scene.get("narration_en" if language == "en" else "narration", "")
            planned, audit = plan_scene(
                scene, text, language, settings, takes.get(scene["id"], 0),
                index == len(content["scenes"]) - 1, opening=index == 0,
            )
            boundaries.extend(audit)
            if language == primary:
                primary_scenes.append(planned)
            else:
                for chunk in audit:
                    secondary.append({"scene_id": scene["id"], "language": language,
                                      "text": chunk["text"], "tail": chunk["pause"],
                                      "tone": scene.get("tone"), "retake": planned["retake"]})
        tracks[language] = {
            "profile": settings["profile"], "boundaries": boundaries,
            "inserted_seconds": round(sum(chunk["pause"] for chunk in boundaries), 3),
        }
    return primary_scenes, secondary, {"version": POLICY, "tracks": tracks}
