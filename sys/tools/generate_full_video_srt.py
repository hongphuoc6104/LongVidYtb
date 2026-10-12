#!/usr/bin/env python3
"""
Generates the master subtitles SRT file (ancient_humans_full_11m.srt) for the
11-minute full video by concatenating cues from all 8 chapters with cumulative duration offsets.
"""
import json
import subprocess
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_ROOT = PROJ_ROOT / "sys" / "exports" / "ancient_humans_bundle"
AUDIO_DIR = BUNDLE_ROOT / "audio"
VIDEO_DIR = PROJ_ROOT / "video"

def format_srt_time(seconds: float) -> str:
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        millis = 999
    total_sec = int(seconds)
    sec = total_sec % 60
    total_min = total_sec // 60
    minute = total_min % 60
    hour = total_min // 60
    return f"{hour:02d}:{minute:02d}:{sec:02d},{millis:03d}"

def wrap_subtitle_text(txt: str, max_line_len: int = 38) -> str:
    txt = txt.strip()
    if len(txt) <= max_line_len or " " not in txt:
        return txt
    mid = len(txt) // 2
    split_idx = txt.rfind(" ", 0, mid + 8)
    if split_idx == -1:
        split_idx = txt.find(" ", mid)
    if split_idx != -1:
        return txt[:split_idx] + "\n" + txt[split_idx + 1:]
    return txt

def get_chapter_duration(ch_num: int) -> float:
    # First check rendered chapter MP4 duration
    candidates = [
        VIDEO_DIR / f"ancient-humans-day-ch{ch_num}-16x9" / f"ancient-humans-day-ch{ch_num}-16x9_r1_final.mp4",
        BUNDLE_ROOT / "rendered_chapters" / f"ch{ch_num}_rendered.mp4",
        VIDEO_DIR / f"ancient-humans-day-ch{ch_num}-16x9" / f"ancient-humans-day-ch{ch_num}-16x9_adam_final.mp4",
    ]
    for cand in candidates:
        if cand.is_file() and cand.stat().st_size > 10000:
            try:
                cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(cand)]
                dur_str = subprocess.check_output(cmd, text=True).strip()
                return float(dur_str)
            except Exception:
                pass

    # Fallback to spoken cues last end
    cues_file = AUDIO_DIR / f"ch{ch_num}_spoken_cues.json"
    if cues_file.is_file():
        cues = json.loads(cues_file.read_text(encoding="utf-8"))
        if cues:
            return float(cues[-1]["end"])
    return 80.0

def generate_master_srt(output_paths: list[Path]):
    current_offset = 0.0
    global_index = 1
    srt_blocks = []

    print("--- Calculating timeline offsets and compiling master SRT ---")
    for ch in range(1, 9):
        cues_file = AUDIO_DIR / f"ch{ch}_spoken_cues.json"
        ch_dur = get_chapter_duration(ch)
        print(f"Chapter {ch}: offset = {current_offset:.2f}s, duration = {ch_dur:.2f}s")

        if cues_file.is_file():
            cues = json.loads(cues_file.read_text(encoding="utf-8"))
            for c in cues:
                start_sec = current_offset + float(c["start"])
                end_sec = current_offset + float(c["end"])
                # Clamp end to chapter boundary
                if end_sec > current_offset + ch_dur + 0.5:
                    end_sec = current_offset + ch_dur

                text = wrap_subtitle_text(c["text"])
                srt_blocks.append(
                    f"{global_index}\n"
                    f"{format_srt_time(start_sec)} --> {format_srt_time(end_sec)}\n"
                    f"{text}\n"
                )
                global_index += 1

        current_offset += ch_dur

    full_srt_content = "\n".join(srt_blocks)
    for out_p in output_paths:
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(full_srt_content, encoding="utf-8")
        print(f"Saved master SRT ({len(srt_blocks)} subtitles) to {out_p}")

if __name__ == "__main__":
    targets = [
        VIDEO_DIR / "ancient_humans_full_11m.srt",
        VIDEO_DIR / "ancient-humans-day-full-16x9" / "ancient-humans-day-full-16x9.srt",
        BUNDLE_ROOT / "ancient_humans_full_11m.srt"
    ]
    generate_master_srt(targets)
