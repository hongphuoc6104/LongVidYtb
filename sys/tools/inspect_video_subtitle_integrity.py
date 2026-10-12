#!/usr/bin/env python3
"""
Adversarial Video & Subtitle Integrity Inspector
Stress-tests video/study_motivation_full_13m_final.mp4 and video/study_motivation_full_13m.srt
for:
1. Video technical invariants (1920x1080 @ 30fps, H.264 / AAC 48kHz, valid container duration).
2. A/V drift across all 8 chapter boundaries and total duration.
3. Stream corruptions, PTS monotonicity, and packet-level sanity.
4. Video frozen segments detection (threshold 3.8s per brief spec).
5. Subtitle strict character limit (<= 42 chars per line).
6. Subtitle monotonicity, duration validity, and zero overlaps.
7. Subtitle temporal alignment vs ground-truth ch{1..8}_spoken_cues.json (0 drift).
"""

import sys
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple


PROJ_ROOT = Path(__file__).resolve().parent.parent.parent
VIDEO_FINAL = PROJ_ROOT / "video" / "study_motivation_full_13m_final.mp4"
SRT_FINAL = PROJ_ROOT / "video" / "study_motivation_full_13m.srt"
BUNDLE_AUDIO = PROJ_ROOT / "sys" / "exports" / "study_motivation_bundle" / "audio"
CHAPTERS = [PROJ_ROOT / f"video/study-motivation-ch{i}-16x9/study-motivation-ch{i}-16x9_r1_final.mp4" for i in range(1, 9)]


def parse_srt_timestamp(ts_str: str) -> float:
    # Format: HH:MM:SS,mmm
    m = re.match(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", ts_str.strip())
    if not m:
        raise ValueError(f"Invalid SRT timestamp format: {ts_str}")
    h, m_val, s, ms = map(int, m.groups())
    return h * 3600 + m_val * 60 + s + ms / 1000.0


def run_cmd(cmd: List[str]) -> str:
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed ({res.returncode}): {' '.join(cmd)}\nStderr: {res.stderr}")
    return res.stdout


def inspect_video_stream(mp4_path: Path) -> Dict[str, Any]:
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", str(mp4_path)
    ]
    data = json.loads(run_cmd(cmd))
    video_stream = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    audio_stream = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    fmt = data["format"]
    return {
        "format": fmt,
        "video": video_stream,
        "audio": audio_stream,
        "duration": float(fmt["duration"]),
        "v_duration": float(video_stream["duration"]) if video_stream and "duration" in video_stream else None,
        "a_duration": float(audio_stream["duration"]) if audio_stream and "duration" in audio_stream else None,
        "size_bytes": int(fmt["size"]),
    }


def inspect_av_drift_and_boundaries() -> Dict[str, Any]:
    print("\n--- 1. Chapter Boundaries & Cumulative Durations ---")
    ch_info = []
    cumulative_offset = 0.0

    for idx, ch_p in enumerate(CHAPTERS, 1):
        if not ch_p.exists():
            raise FileNotFoundError(f"Chapter file missing: {ch_p}")
        info = inspect_video_stream(ch_p)
        v_dur = info["v_duration"] or info["duration"]
        a_dur = info["a_duration"] or info["duration"]
        fmt_dur = info["duration"]
        drift_ms = (a_dur - v_dur) * 1000.0
        start_offset = cumulative_offset
        cumulative_offset += fmt_dur
        ch_info.append({
            "chapter": idx,
            "path": str(ch_p),
            "v_dur": v_dur,
            "a_dur": a_dur,
            "fmt_dur": fmt_dur,
            "drift_ms": drift_ms,
            "start_offset": start_offset,
            "end_offset": cumulative_offset,
            "v_codec": info["video"]["codec_name"],
            "a_codec": info["audio"]["codec_name"],
            "width": info["video"]["width"],
            "height": info["video"]["height"],
            "fps": info["video"]["r_frame_rate"],
        })
        print(f"Chapter {idx}: duration={fmt_dur:.3f}s (V={v_dur:.3f}s, A={a_dur:.3f}s, drift={drift_ms:.1f}ms), offset=[{start_offset:.3f}s, {cumulative_offset:.3f}s]")

    master_info = inspect_video_stream(VIDEO_FINAL)
    master_v_dur = master_info["v_duration"] or master_info["duration"]
    master_a_dur = master_info["a_duration"] or master_info["duration"]
    master_fmt_dur = master_info["duration"]
    master_drift_ms = (master_a_dur - master_v_dur) * 1000.0

    print(f"\nMaster Video ({VIDEO_FINAL.name}):")
    print(f"  Duration: format={master_fmt_dur:.3f}s, V={master_v_dur:.3f}s, A={master_a_dur:.3f}s")
    print(f"  A/V stream difference: {master_drift_ms:.1f}ms")
    print(f"  Sum of chapters format duration: {cumulative_offset:.3f}s")
    print(f"  Discrepancy master vs sum of chapters: {abs(master_fmt_dur - cumulative_offset)*1000.0:.2f}ms")

    return {
        "chapters": ch_info,
        "cumulative_offset": cumulative_offset,
        "master_info": master_info,
        "master_drift_ms": master_drift_ms,
    }


def inspect_pts_monotonicity(mp4_path: Path) -> Dict[str, Any]:
    print("\n--- 2. PTS Monotonicity & Packet Timestamp Sanity ---")
    # Probe video and audio packet timestamps
    # Video packets: check DTS strictly monotonic, PTS valid
    cmd_v = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "packet=pts_time,dts_time,flags",
        "-of", "csv=p=0", str(mp4_path)
    ]
    out_v = run_cmd(cmd_v).strip().splitlines()
    print(f"Total video packets: {len(out_v)}")

    v_pts_errors = []
    v_dts_errors = []
    prev_dts = -1.0
    for i, line in enumerate(out_v):
        parts = line.split(",")
        if len(parts) >= 2:
            try:
                pts = float(parts[0])
                dts = float(parts[1])
            except ValueError:
                continue
            if dts < prev_dts:
                v_dts_errors.append((i, dts, prev_dts))
            if pts < 0:
                v_pts_errors.append((i, pts))
            prev_dts = dts

    # Audio packets: check PTS strictly monotonic
    cmd_a = [
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "packet=pts_time,dts_time",
        "-of", "csv=p=0", str(mp4_path)
    ]
    out_a = run_cmd(cmd_a).strip().splitlines()
    print(f"Total audio packets: {len(out_a)}")

    a_pts_errors = []
    prev_a_pts = -1.0
    for i, line in enumerate(out_a):
        parts = line.split(",")
        if len(parts) >= 1:
            try:
                pts = float(parts[0])
            except ValueError:
                continue
            if pts < prev_a_pts:
                a_pts_errors.append((i, pts, prev_a_pts))
            prev_a_pts = pts

    print(f"Video DTS monotonicity errors: {len(v_dts_errors)}")
    print(f"Video negative PTS errors: {len(v_pts_errors)}")
    print(f"Audio PTS monotonicity errors: {len(a_pts_errors)}")

    return {
        "v_packet_count": len(out_v),
        "a_packet_count": len(out_a),
        "v_dts_errors": v_dts_errors,
        "v_pts_errors": v_pts_errors,
        "a_pts_errors": a_pts_errors,
    }


def inspect_frozen_segments(mp4_path: Path, max_freeze_sec: float = 3.80) -> List[Dict[str, float]]:
    print(f"\n--- 3. Frozen Video Segment Detection (threshold > {max_freeze_sec}s) ---")
    cmd = [
        "ffmpeg", "-v", "info", "-i", str(mp4_path),
        "-vf", f"freezedetect=n=0.003:d={max_freeze_sec}",
        "-map", "v:0", "-f", "null", "-"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    freezes = []
    current_start = None
    for line in res.stderr.splitlines():
        if "freeze_start" in line:
            m = re.search(r"freeze_start:\s*([\d\.]+)", line)
            if m:
                current_start = float(m.group(1))
        elif "freeze_end" in line and current_start is not None:
            m_end = re.search(r"freeze_end:\s*([\d\.]+)", line)
            m_dur = re.search(r"freeze_duration:\s*([\d\.]+)", line)
            if m_end and m_dur:
                end = float(m_end.group(1))
                dur = float(m_dur.group(1))
                freezes.append({"start": current_start, "end": end, "duration": dur})
                current_start = None

    print(f"Detected frozen segments exceeding {max_freeze_sec}s: {len(freezes)}")
    for f in freezes:
        print(f"  FREEZE DETECTED: {f['start']:.2f}s -> {f['end']:.2f}s (duration: {f['duration']:.2f}s)")
    return freezes


def stress_test_subtitles(srt_path: Path, chapter_offsets: List[Dict[str, Any]]) -> Dict[str, Any]:
    print("\n--- 4. Subtitle Stress-Test & Temporal Sync ---")
    if not srt_path.exists():
        raise FileNotFoundError(f"SRT file missing: {srt_path}")

    content = srt_path.read_text(encoding="utf-8").strip()
    raw_blocks = content.split("\n\n")
    print(f"Total raw SRT blocks: {len(raw_blocks)}")

    blocks = []
    lines_over_42 = []
    overlaps = []
    negative_durations = []
    monotonicity_violations = []

    prev_end = 0.0

    for b_idx, block in enumerate(raw_blocks, 1):
        lines = block.strip().split("\n")
        if len(lines) < 3:
            raise ValueError(f"Malformed SRT block #{b_idx}:\n{block}")
        
        cue_num = int(lines[0].strip())
        time_line = lines[1].strip()
        ts_parts = time_line.split("-->")
        if len(ts_parts) != 2:
            raise ValueError(f"Malformed timestamp line in block #{b_idx}: {time_line}")
        
        start_ts = parse_srt_timestamp(ts_parts[0])
        end_ts = parse_srt_timestamp(ts_parts[1])
        text_lines = lines[2:]

        # Duration check
        if end_ts <= start_ts:
            negative_durations.append((cue_num, start_ts, end_ts))

        # Monotonicity check
        if b_idx > 1 and start_ts < blocks[-1]["start"]:
            monotonicity_violations.append((cue_num, start_ts, blocks[-1]["start"]))

        # Overlap check
        if start_ts < prev_end - 0.001:  # Allow 1ms tolerance
            overlaps.append((cue_num, start_ts, prev_end, prev_end - start_ts))

        # Line length check
        for l_num, text_line in enumerate(text_lines, 1):
            if len(text_line) > 42:
                lines_over_42.append({
                    "cue": cue_num,
                    "line_num": l_num,
                    "length": len(text_line),
                    "text": text_line
                })

        blocks.append({
            "cue": cue_num,
            "start": start_ts,
            "end": end_ts,
            "duration": end_ts - start_ts,
            "text": "\n".join(text_lines)
        })
        prev_end = end_ts

    print(f"Parsed cues: {len(blocks)}")
    print(f"Lines exceeding 42 characters: {len(lines_over_42)}")
    print(f"Cues with end <= start: {len(negative_durations)}")
    print(f"Monotonicity violations: {len(monotonicity_violations)}")
    print(f"Timestamp overlaps: {len(overlaps)}")

    # Temporal sync against ch{1..8}_spoken_cues.json
    print("\n--- 5. Comparing Subtitles Against Ground-Truth spoken_cues.json ---")
    all_ground_cues = []
    for ch_item in chapter_offsets:
        ch = ch_item["chapter"]
        cues_f = BUNDLE_AUDIO / f"ch{ch}_spoken_cues.json"
        if not cues_f.exists():
            raise FileNotFoundError(f"Missing cues file: {cues_f}")
        cues_data = json.loads(cues_f.read_text(encoding="utf-8"))
        for c in cues_data:
            all_ground_cues.append({
                "chapter": ch,
                "ch_offset": ch_item["start_offset"],
                "ch_dur": ch_item["fmt_dur"],
                "start": ch_item["start_offset"] + float(c["start"]),
                "end": min(ch_item["start_offset"] + ch_item["fmt_dur"], ch_item["start_offset"] + float(c["end"])),
                "text": c["text"],
                "scene_id": c.get("scene_id", ""),
            })

    print(f"Total ground cues across 8 chapters: {len(all_ground_cues)}")
    if len(all_ground_cues) != len(blocks):
        print(f"WARNING: Count mismatch! Ground cues: {len(all_ground_cues)}, SRT cues: {len(blocks)}")

    sync_drifts = []
    for idx, (b, g) in enumerate(zip(blocks, all_ground_cues), 1):
        start_diff = abs(b["start"] - g["start"])
        end_diff = abs(b["end"] - g["end"])
        if start_diff > 0.005 or end_diff > 0.005:  # Tolerance: 5ms due to ms rounding
            sync_drifts.append({
                "cue": b["cue"],
                "srt_start": b["start"],
                "ground_start": g["start"],
                "start_diff_ms": start_diff * 1000.0,
                "srt_end": b["end"],
                "ground_end": g["end"],
                "end_diff_ms": end_diff * 1000.0,
            })

    print(f"Temporal sync discrepancies (> 5ms): {len(sync_drifts)}")
    if sync_drifts:
        for sd in sync_drifts[:5]:
            print(f"  Drift at cue #{sd['cue']}: start_diff={sd['start_diff_ms']:.2f}ms, end_diff={sd['end_diff_ms']:.2f}ms")

    return {
        "cue_count": len(blocks),
        "lines_over_42": lines_over_42,
        "negative_durations": negative_durations,
        "monotonicity_violations": monotonicity_violations,
        "overlaps": overlaps,
        "sync_drifts": sync_drifts,
    }


def main():
    print("=" * 70)
    print("ADVERSARIAL VIDEO & SUBTITLE EMPIRICAL INSPECTION")
    print("=" * 70)

    # 1. Video and chapter inspection
    av_data = inspect_av_drift_and_boundaries()

    # 2. PTS monotonicity and packet sanity
    pts_data = inspect_pts_monotonicity(VIDEO_FINAL)

    # 3. Frozen video check
    freezes = inspect_frozen_segments(VIDEO_FINAL, max_freeze_sec=3.80)

    # 4. Subtitle stress-test
    sub_data = stress_test_subtitles(SRT_FINAL, av_data["chapters"])

    print("\n" + "=" * 70)
    print("EMPIRICAL SUMMARY & VERDICT CHECK")
    print("=" * 70)

    failures = []
    
    # Check Master duration
    dur = av_data["master_info"]["duration"]
    if not (540.0 <= dur <= 1020.0):
        failures.append(f"Master video duration {dur:.2f}s outside [540s, 1020s] (9-17m)")

    # Check resolution & framerate
    v_st = av_data["master_info"]["video"]
    if v_st["width"] != 1920 or v_st["height"] != 1080:
        failures.append(f"Video resolution {v_st['width']}x{v_st['height']} is not 1920x1080")
    if v_st["r_frame_rate"] != "30/1":
        failures.append(f"Video framerate {v_st['r_frame_rate']} is not 30 fps")
    if v_st["codec_name"] != "h264":
        failures.append(f"Video codec {v_st['codec_name']} is not h264")

    # Check audio codec
    a_st = av_data["master_info"]["audio"]
    if a_st["codec_name"] != "aac":
        failures.append(f"Audio codec {a_st['codec_name']} is not aac")
    if int(a_st["sample_rate"]) != 48000:
        failures.append(f"Audio sample rate {a_st['sample_rate']} is not 48000")

    # Check PTS errors
    if pts_data["v_dts_errors"]:
        failures.append(f"Video DTS monotonicity errors: {len(pts_data['v_dts_errors'])}")
    if pts_data["a_pts_errors"]:
        failures.append(f"Audio PTS monotonicity errors: {len(pts_data['a_pts_errors'])}")

    # Check freezes > 3.8s
    if freezes:
        failures.append(f"Frozen video segments (> 3.80s): {len(freezes)}")

    # Check subtitle constraints
    if sub_data["cue_count"] != 160:
        failures.append(f"Subtitle cue count {sub_data['cue_count']} != 160")
    if sub_data["lines_over_42"]:
        failures.append(f"Subtitle lines exceeding 42 characters: {len(sub_data['lines_over_42'])}")
    if sub_data["negative_durations"]:
        failures.append(f"Subtitle cues with end <= start: {len(sub_data['negative_durations'])}")
    if sub_data["monotonicity_violations"]:
        failures.append(f"Subtitle monotonicity violations: {len(sub_data['monotonicity_violations'])}")
    if sub_data["overlaps"]:
        failures.append(f"Subtitle timestamp overlaps: {len(sub_data['overlaps'])}")
    if sub_data["sync_drifts"]:
        failures.append(f"Subtitle sync drifts vs cues: {len(sub_data['sync_drifts'])}")

    if failures:
        print("\nVERDICT: REQUEST_CHANGES")
        print("FAILURES DETECTED:")
        for f in failures:
            print(f"  [X] {f}")
        sys.exit(1)
    else:
        print("\nVERDICT: APPROVE")
        print("ALL VERIFICATIONS PASSED WITH ZERO DEFECTS!")
        sys.exit(0)


if __name__ == "__main__":
    main()
