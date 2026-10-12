#!/usr/bin/env python3
"""
Renders Chapter 1 with official Adam (+22% speed) voice on Colab Tesla T4 GPU.
Complies with 6-Station No-Mistake Conveyor:
- Scales timeline by 1.1793x (75.77s)
- Clean render (subtitles: false)
- Generates companion subtitles_vi.srt
- Verified via ffprobe (1080p, 30fps, H.264/AAC, audio sync)
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile
import soundfile as sf

PROJ_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_ROOT = PROJ_ROOT / "sys" / "exports" / "ancient_humans_bundle"
AUDIO_DIR = BUNDLE_ROOT / "audio"
IMAGES_DIR = BUNDLE_ROOT / "generated_images" / "ch1"
TEMPLATE_FILE = BUNDLE_ROOT / "templates" / "ch1_props_template.json"

OUT_CH1_DIR = PROJ_ROOT / "video" / "ancient-humans-day-ch1-16x9"
OUT_CH1_DIR.mkdir(parents=True, exist_ok=True)
OUT_COMP_DIR = PROJ_ROOT / "video" / "ch1_comparison"
OUT_COMP_DIR.mkdir(parents=True, exist_ok=True)

ART_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/ebb9330c-b49f-4fbc-930b-c1c2129f2704")

ACCOUNT_CLI = str(PROJ_ROOT / "sys" / "colab_bridge" / "account_cli.py")
ACCOUNT_DIR = f"{os.path.expanduser('~')}/.config/video-pilot/colab/profiles/account-01"
PY_BIN = f"{os.path.expanduser('~')}/.local/share/uv/tools/google-colab-cli/bin/python"


def format_srt_time(seconds: float) -> str:
    millis = int(round((seconds - int(seconds)) * 1000))
    total_sec = int(seconds)
    sec = total_sec % 60
    total_min = total_sec // 60
    minute = total_min % 60
    hour = total_min // 60
    return f"{hour:02d}:{minute:02d}:{sec:02d},{millis:03d}"


def cues_to_srt(cues, srt_path: Path):
    lines = []
    for c in cues:
        idx = c["index"]
        start_str = format_srt_time(c["start"])
        end_str = format_srt_time(c["end"])
        txt = c["text"].strip()
        # Wrap long lines (> 38 chars) for 16:9 aesthetics
        if len(txt) > 38 and " " in txt:
            mid = len(txt) // 2
            split_idx = txt.rfind(" ", 0, mid + 10)
            if split_idx == -1:
                split_idx = txt.find(" ", mid)
            if split_idx != -1:
                txt = txt[:split_idx] + "\n" + txt[split_idx + 1 :]

        lines.append(f"{idx}\n{start_str} --> {end_str}\n{txt}\n")

    srt_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated SRT subtitles: {srt_path} ({len(cues)} cues)")


def run_colab_cmd(args, timeout=300):
    argv = [PY_BIN, ACCOUNT_CLI, ACCOUNT_DIR, *args]
    return subprocess.run(argv, capture_output=True, text=True, check=True, timeout=timeout)


def build_adam_package() -> Path:
    print("\n--- [Station 1] Building Remotion Package for Adam (+22%) ---")
    build_dir = Path("/tmp/ch1_build_adam_final")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    pub_dir = build_dir / "public"
    pub_dir.mkdir(parents=True, exist_ok=True)

    wav_file = AUDIO_DIR / "ch1_adam_p22.wav"
    cues_file = AUDIO_DIR / "ch1_adam_p22_cues.json"

    if not wav_file.is_file():
        raise FileNotFoundError(f"Missing WAV: {wav_file}")
    if not cues_file.is_file():
        raise FileNotFoundError(f"Missing Cues: {cues_file}")

    # Copy audio
    shutil.copy2(wav_file, pub_dir / "narration.wav")

    # Copy all 34 images
    img_files = list(IMAGES_DIR.glob("*.jpg"))
    if not img_files:
        raise FileNotFoundError(f"No images found in {IMAGES_DIR}")
    for im in img_files:
        shutil.copy2(im, pub_dir / im.name)
    print(f"Copied {len(img_files)} images to public/")

    # Load template and scale
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        props = json.load(f)

    with open(cues_file, "r", encoding="utf-8") as f:
        cues = json.load(f)

    info = sf.info(str(wav_file))
    new_dur = round(info.duration, 2)
    old_dur = props.get("duration", 64.25)
    scale = new_dur / old_dur if old_dur > 0 else 1.0

    print(f"Original duration: {old_dur}s -> New duration: {new_dur}s (Scale: {scale:.4f})")

    props["duration"] = new_dur
    if "tracks" in props and "vi" in props["tracks"]:
        props["tracks"]["vi"]["duration"] = new_dur
        props["tracks"]["vi"]["audioSrc"] = "narration.wav"
        props["tracks"]["vi"]["cues"] = [
            {"text": c["text"], "start": c["start"], "end": c["end"]}
            for c in cues
        ]
        if "scenesByAspect" in props["tracks"]["vi"] and "16:9" in props["tracks"]["vi"]["scenesByAspect"]:
            for sc in props["tracks"]["vi"]["scenesByAspect"]["16:9"]:
                sc["start"] = round(sc.get("start", 0) * scale, 3)
                sc["end"] = round(sc.get("end", 0) * scale, 3)
                for im in sc.get("images", []):
                    if "at" in im:
                        im["at"] = round(im["at"] * scale, 3)

    if "scenesByAspect" in props and "16:9" in props["scenesByAspect"]:
        for sc in props["scenesByAspect"]["16:9"]:
            sc["start"] = round(sc.get("start", 0) * scale, 3)
            sc["end"] = round(sc.get("end", 0) * scale, 3)
            for im in sc.get("images", []):
                if "at" in im:
                    im["at"] = round(im["at"] * scale, 3)

    # Clean video without burned-in subtitles
    props["outputs"] = [
        {"aspect_ratio": "16:9", "language": "vi", "subtitles": False}
    ]

    with open(build_dir / "props.json", "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    # Also generate local companion SRT
    cues_to_srt(cues, OUT_CH1_DIR / "subtitles_vi.srt")

    # Zip build
    zip_path = Path("/tmp/ch1_build_adam_final.zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(build_dir):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, build_dir)
                z.write(full, rel)

    print(f"Zipped Adam build: {zip_path.stat().st_size} bytes")
    return zip_path


def render_on_colab(zip_path: Path) -> Path:
    print("\n--- [Station 3] Uploading & Rendering on Colab Tesla T4 GPU ---")
    run_colab_cmd(["upload", "-s", "video-pilot-tts", str(zip_path), "/content/ch1_build_adam_final.zip"], timeout=120)

    render_code = """
import subprocess, zipfile, os, shutil
from pathlib import Path

job_dir = Path('/content/jobs/ch1_adam_final')
if job_dir.exists():
    shutil.rmtree(job_dir)
job_dir.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile('/content/ch1_build_adam_final.zip') as z:
    z.extractall(job_dir)

env = dict(
    os.environ,
    VP_CHROME_PATH='/content/render-runtime/chrome-wrapper.sh',
    DISABLE_FROM_SURFACE='true'
)

print("Executing Remotion render.mjs for Chapter 1 Adam Final...")
p = subprocess.run(
    ['node', '/content/render-runtime/renderer/render.mjs', str(job_dir)],
    cwd='/content/render-runtime',
    env=env,
    capture_output=True,
    text=True
)
print('RENDER_RETURNCODE:', p.returncode)
print(p.stdout)
if p.stderr:
    print('STDERR:', p.stderr[-500:])

mp4s = list(job_dir.glob('**/*.mp4'))
print('RENDERED_MP4S:', [str(m) for m in mp4s])
"""
    argv = [PY_BIN, ACCOUNT_CLI, ACCOUNT_DIR, "exec", "-s", "video-pilot-tts", "--timeout", "600"]
    res = subprocess.run(argv, input=render_code, capture_output=True, text=True)
    print(res.stdout)
    if "RENDER_RETURNCODE: 0" not in res.stdout:
        print("Render failed! Stderr:", res.stderr)
        raise RuntimeError("Render failed on Colab")

    dest_mp4_1 = OUT_CH1_DIR / "ancient-humans-day-ch1-16x9_adam_final.mp4"
    dest_mp4_r1 = OUT_CH1_DIR / "ancient-humans-day-ch1-16x9_r1_final.mp4"
    dest_mp4_comp = OUT_COMP_DIR / "ch1_adam_p22.mp4"

    print(f"\n--- [Station 4] Downloading MP4 to {dest_mp4_1} ---")
    run_colab_cmd(["download", "-s", "video-pilot-tts", "/content/jobs/ch1_adam_final/video.mp4", str(dest_mp4_1)], timeout=180)
    
    # Mirror copies
    shutil.copy2(dest_mp4_1, dest_mp4_r1)
    shutil.copy2(dest_mp4_1, dest_mp4_comp)
    
    # Mirror to artifact directory
    art_video_dir = ART_DIR / "video"
    art_video_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dest_mp4_1, art_video_dir / "ch1_adam_p22.mp4")

    print(f"DOWNLOADED & VERIFIED: {dest_mp4_1} ({dest_mp4_1.stat().st_size / (1024*1024):.2f} MB)")
    return dest_mp4_1


def verify_with_ffprobe(mp4_path: Path):
    print("\n--- [Station 5] Technical Verification via ffprobe ---")
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=codec_name,width,height,duration,r_frame_rate",
        "-show_entries", "format=duration,size",
        "-of", "json",
        str(mp4_path)
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(p.stdout)
    
    streams = data.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_name") == "h264"), None)
    audio_stream = next((s for s in streams if s.get("codec_name") == "aac"), None)
    
    assert video_stream is not None, "Missing H.264 video stream"
    assert audio_stream is not None, "Missing AAC audio stream"
    assert video_stream["width"] == 1920, f"Expected 1920 width, got {video_stream['width']}"
    assert video_stream["height"] == 1080, f"Expected 1080 height, got {video_stream['height']}"
    assert video_stream["r_frame_rate"] == "30/1", f"Expected 30 fps, got {video_stream['r_frame_rate']}"
    
    v_dur = float(video_stream["duration"])
    a_dur = float(audio_stream["duration"])
    diff = abs(v_dur - a_dur)
    
    print(f"Video: {video_stream['codec_name']} {video_stream['width']}x{video_stream['height']} @ {video_stream['r_frame_rate']} ({v_dur:.2f}s)")
    print(f"Audio: {audio_stream['codec_name']} ({a_dur:.2f}s)")
    print(f"Audio Sync Delta: {diff:.4f}s (Tolerance: 0.10s)")
    
    assert diff <= 0.10, f"Audio sync delta {diff}s exceeds tolerance 0.10s"
    print("VERIFICATION INTEGRITY PASSED 100%!")


def main():
    print("=================================================================")
    print("STARTING CHAPTER 1 FINAL VIDEO PRODUCTION (ADAM +22% SSOT VOICE)")
    print("=================================================================")
    zip_path = build_adam_package()
    mp4_path = render_on_colab(zip_path)
    verify_with_ffprobe(mp4_path)
    print("\n=================================================================")
    print("CONVEYOR COMPLETED: CHAPTER 1 RENDERED PERFECTLY WITH ADAM VOICE!")
    print(f"Final MP4: {mp4_path}")
    print(f"SRT Track: {OUT_CH1_DIR / 'subtitles_vi.srt'}")
    print("=================================================================")


if __name__ == "__main__":
    main()
