"""Master Builder & Validator for Group C 255-310 Beat Explainer Visual Specs.

Channels:
1. ban_do_quyen_luc (255 beats)
2. banh_rang (255 beats)
3. ho_so_ky_la (310 beats)
4. luat_ngam (305 beats)
5. su_ke_lai (305 beats)

Generates:
- video/vn_pilot_<slug>_long/<slug>_long_explainer_spec.json
"""

from __future__ import annotations

import json
import re
import wave
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT_DIR = Path("/home/hongphuoc6104/Desktop/vp-agent-core")

FORBIDDEN_PHRASES = [
    "detailed visual narrative illustration",
    "continuing scene continuity",
    "repetitive generic landscape",
]

CAMERA_MOTIONS = ["push_in", "pan_right", "pull_back", "pan_left"]


def parse_srt(srt_path: Path) -> List[Dict[str, Any]]:
    """Parse SRT into cue blocks."""
    content = srt_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"(\d+)\s*\n(\d\d:\d\d:\d\d,\d\d\d)\s*-->\s*(\d\d:\d\d:\d\d,\d\d\d)\s*\n(.*?)(?=\n\s*\n\d+|\Z)",
        re.DOTALL,
    )
    blocks = []
    for m in pattern.finditer(content):
        idx, s_str, e_str, text = m.groups()

        def to_sec(s: str) -> float:
            h, mn, sec_ms = s.split(":")
            sec, ms = sec_ms.split(",")
            return int(h) * 3600 + int(mn) * 60 + int(sec) + int(ms) / 1000.0

        s_sec = to_sec(s_str)
        e_sec = to_sec(e_str)
        blocks.append(
            {
                "idx": int(idx),
                "start": s_sec,
                "end": e_sec,
                "raw_dur": round(e_sec - s_sec, 3),
                "narration": " ".join(text.strip().split()),
            }
        )
    return blocks


def get_wav_duration(wav_path: Path) -> float:
    with wave.open(str(wav_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


def scale_durations_to_wav(cues: List[Dict[str, Any]], wav_dur: float) -> Tuple[List[float], List[float]]:
    raw_sum = sum(c["raw_dur"] for c in cues)
    factor = wav_dur / raw_sum
    durs = [round(c["raw_dur"] * factor, 4) for c in cues]
    diff = round(wav_dur - sum(durs), 4)
    durs[-1] = round(durs[-1] + diff, 4)

    ats = [0.0]
    for d in durs[:-1]:
        ats.append(round(ats[-1] + d, 4))
    return durs, ats


def assign_chapter(at_sec: float, chapters: List[Dict[str, Any]]) -> Tuple[int, str]:
    for c in chapters:
        if c["start_sec"] <= at_sec < c["end_sec"]:
            return c["chapter_index"], c["title"]
    return chapters[-1]["chapter_index"], chapters[-1]["title"]


def sanitize_prompt(prompt: str, target_min: int = 35, target_max: int = 65) -> str:
    """Format prompt to strictly 35-65 words, ending with ', zero text overlay, no watermarks'."""
    tail = ", zero text overlay, no watermarks"

    p = prompt.strip()
    p = re.sub(r"\b8k\b", "crisp Full HD 1080p", p, flags=re.IGNORECASE)

    for t in [tail, ", strictly zero text", ", zero text", ", no watermarks"]:
        if p.endswith(t):
            p = p[: -len(t)].strip()

    pl = p.lower()
    for fp in FORBIDDEN_PHRASES:
        if fp in pl:
            p = re.sub(re.escape(fp), "cinematic focal staging", p, flags=re.IGNORECASE)

    enrichments = [
        "standard clear composition with ample negative space",
        "dramatic cinematic lighting with balanced contrast",
        "precision forensic detailing and spatial depth",
        "meticulous visual geometry framing the focal subject",
    ]
    enrich_idx = 0
    while len((p.rstrip(",") + tail).split()) < target_min and enrich_idx < len(enrichments):
        p += ", " + enrichments[enrich_idx]
        enrich_idx += 1

    while len((p.rstrip(",") + tail).split()) > target_max:
        if "," in p:
            parts = p.rsplit(",", 1)
            candidate = parts[0].strip()
            if len((candidate.rstrip(",") + tail).split()) >= target_min:
                p = candidate
                continue
        words = p.split()[:-1]
        p = " ".join(words)

    final = p.rstrip(",") + tail
    final_len = len(final.split())
    assert target_min <= final_len <= target_max, (
        f"Prompt length {final_len} not in [{target_min}, {target_max}]: {final}"
    )
    return final


def build_channel_spec(slug: str) -> Dict[str, Any]:
    """Build and validate long explainer spec for a given channel."""
    video_dir = ROOT_DIR / f"video/vn_pilot_{slug}_long"
    srt_p = video_dir / f"vn_pilot_{slug}_long_16x9.srt"
    aligned_p = video_dir / f"{slug}_long_aligned_spec.json"
    wav_p = video_dir / "narration_master.wav"

    assert srt_p.exists(), f"Missing SRT file {srt_p}"
    assert aligned_p.exists(), f"Missing aligned spec {aligned_p}"
    assert wav_p.exists(), f"Missing narration WAV {wav_p}"

    cues = parse_srt(srt_p)
    wav_dur = get_wav_duration(wav_p)
    durs, ats = scale_durations_to_wav(cues, wav_dur)

    with open(aligned_p, encoding="utf-8") as f:
        aligned = json.load(f)

    chapters = aligned["chapters"]
    old_beats = aligned.get("beats", [])

    # Import channel generators dynamically
    if slug == "ban_do_quyen_luc":
        from sys.tools.explainer_generators.gen_ban_do_quyen_luc import build_ban_do_quyen_luc_beats

        beats = build_ban_do_quyen_luc_beats(cues, durs, ats, chapters, old_beats)
    elif slug == "banh_rang":
        from sys.tools.explainer_generators.gen_banh_rang import build_banh_rang_beats

        beats = build_banh_rang_beats(cues, durs, ats, chapters, old_beats)
    elif slug == "ho_so_ky_la":
        from sys.tools.explainer_generators.gen_ho_so_ky_la import build_ho_so_ky_la_beats

        beats = build_ho_so_ky_la_beats(cues, durs, ats, chapters, old_beats)
    elif slug == "luat_ngam":
        from sys.tools.explainer_generators.gen_luat_ngam import build_luat_ngam_beats

        beats = build_luat_ngam_beats(cues, durs, ats, chapters, old_beats)
    elif slug == "su_ke_lai":
        from sys.tools.explainer_generators.gen_su_ke_lai import build_su_ke_lai_beats

        beats = build_su_ke_lai_beats(cues, durs, ats, chapters, old_beats)
    else:
        raise ValueError(f"Unknown slug {slug}")

    # Validate beat count
    expected_counts = {
        "ban_do_quyen_luc": 255,
        "banh_rang": 255,
        "ho_so_ky_la": 310,
        "luat_ngam": 305,
        "su_ke_lai": 305,
    }
    expected = expected_counts[slug]
    assert len(beats) == expected, f"{slug}: expected {expected} beats, got {len(beats)}"

    # Validate durations
    total_dur = round(sum(b["duration"] for b in beats), 4)
    expected_dur = round(wav_dur, 4)
    assert abs(total_dur - expected_dur) < 0.01, f"{slug}: duration mismatch {total_dur} vs {expected_dur}"

    # Validate prompts
    for b in beats:
        p = b["prompt"]
        words = len(p.split())
        assert 35 <= words <= 65, f"{slug} {b['beat_id']}: word count {words} not in [35, 65]: {p}"
        assert p.endswith(", zero text overlay, no watermarks"), f"{slug} {b['beat_id']}: tail mismatch: {p}"
        for fp in FORBIDDEN_PHRASES:
            assert fp not in p.lower(), f"{slug} {b['beat_id']}: forbidden phrase {fp} in {p}"

    # Validate explainer types
    type_counts = {}
    for b in beats:
        t = b["explainer_type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    first_5 = sum(
        type_counts.get(k, 0)
        for k in ["CAUSE_EFFECT_DIAGRAM", "MECHANISM_CUTAWAY", "OBJECT_MACRO", "SPLIT_COMPARISON", "STEP_ENUMERATION"]
    )
    first_5_pct = first_5 / len(beats) * 100
    assert first_5_pct >= 85.0, f"{slug}: first 5 types {first_5_pct:.2f}% < 85%"

    # Validate reuse
    reuse_count = sum(1 for b in beats if b["reuse_old_image_idx"] is not None)
    if slug in ("ban_do_quyen_luc", "banh_rang"):
        assert reuse_count == 98, f"{slug}: expected 98 reused, got {reuse_count}"
    elif slug in ("luat_ngam", "su_ke_lai"):
        assert reuse_count == 117, f"{slug}: expected 117 reused, got {reuse_count}"
    elif slug == "ho_so_ky_la":
        assert reuse_count == 220, f"ho_so_ky_la: expected 220 reused, got {reuse_count}"

    # Validate 100% unique prompts
    unique_prompts = set(b["prompt"].strip() for b in beats)
    assert len(unique_prompts) == len(beats), (
        f"{slug}: expected {len(beats)} unique prompts, got {len(unique_prompts)} ({len(beats) - len(unique_prompts)} duplicates)"
    )

    # Assemble final explainer spec dictionary
    spec = {
        "job_id": f"vn_pilot_{slug}_long",
        "channel_id": aligned.get("channel_id", slug),
        "channel_slug": slug.replace("_", "-"),
        "parent_long_id": f"vn_pilot_{slug}_long",
        "format_profile": "long_16x9",
        "youtube_title": aligned.get("youtube_title") or aligned.get("title", ""),
        "total_duration_sec": total_dur,
        "thumbnail_spec": aligned.get("thumbnail_spec", {}),
        "cta_plan": aligned.get("cta_plan", {}),
        "chapters": chapters,
        "beat_durations": [b["duration"] for b in beats],
        "beats": beats,
        "metadata": {
            **aligned.get("metadata", {}),
            "explainer_spec_version": "1.0.0",
            "explainer_beats_count": len(beats),
            "explainer_types_distribution": type_counts,
            "reused_old_images_count": reuse_count,
            "new_explainer_images_count": len(beats) - reuse_count,
            "first_5_explainer_types_pct": round(first_5_pct, 2),
        },
        "voice": aligned.get("voice", f"VietNarrator_{slug}"),
        "voice_profile": aligned.get("voice_profile", f"sys/assets/voices/ch_{slug}/profile.json"),
    }

    # Save to disk
    out_p = video_dir / f"{slug}_long_explainer_spec.json"
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
    print(f"[{slug}] Saved {len(beats)} beats explainer spec to {out_p}")
    return spec


def main():
    slugs = ["ban_do_quyen_luc", "banh_rang", "ho_so_ky_la", "luat_ngam", "su_ke_lai"]
    results = {}
    for s in slugs:
        spec = build_channel_spec(s)
        results[s] = spec

    print("\n" + "=" * 80)
    print("ALL 5 GROUP C EXPLAINER SPECS SUCCESSFULLY BUILT & VALIDATED!")
    print("=" * 80)


if __name__ == "__main__":
    main()
