#!/usr/bin/env python3
"""
Renders 3 comparison videos of Chapter 1 on Colab Tesla T4 GPU:
- ch1_namminh_p22 (Nam Minh +22%)
- ch1_minhquan_p22 (Minh Quân Pro +22%)
- ch1_adam_p22 (Adam +22%)
Applies hidden subtitles and scaled scene/beat timings.
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
OUT_VIDEO_DIR = PROJ_ROOT / "video" / "ch1_comparison"
OUT_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

ACCOUNT_CLI = str(PROJ_ROOT / "sys" / "colab_bridge" / "account_cli.py")
ACCOUNT_DIR = f"{os.path.expanduser('~')}/.config/video-pilot/colab/profiles/account-01"
PY_BIN = f"{os.path.expanduser('~')}/.local/share/uv/tools/google-colab-cli/bin/python"

VARIANTS = [
    {"name": "namminh", "label": "Nam Minh (+22%)", "audio_stem": "ch1_namminh_p22"},
    {"name": "minhquan", "label": "Minh Quân Pro (+22%)", "audio_stem": "ch1_minhquan_p22"},
    {"name": "adam", "label": "Adam (+22%)", "audio_stem": "ch1_adam_p22"},
]

def run_colab_cmd(args, timeout=300):
    argv = [PY_BIN, ACCOUNT_CLI, ACCOUNT_DIR, *args]
    return subprocess.run(argv, capture_output=True, text=True, check=True, timeout=timeout)

def build_variant_package(variant):
    name = variant["name"]
    stem = variant["audio_stem"]
    print(f"\n--- Building package for {variant['label']} ---")

    build_dir = Path(f"/tmp/ch1_build_{name}")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    pub_dir = build_dir / "public"
    pub_dir.mkdir(parents=True, exist_ok=True)

    wav_file = AUDIO_DIR / f"{stem}.wav"
    cues_file = AUDIO_DIR / f"{stem}_cues.json"

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

    print(f"Original duration: {old_dur}s -> New duration: {new_dur}s (Scale: {scale:.3f})")

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

    if "outputs" in props and isinstance(props["outputs"], list):
        for out in props["outputs"]:
            out["subtitles"] = False

    with open(build_dir / "props.json", "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    # Zip build
    zip_path = Path(f"/tmp/ch1_build_{name}.zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(build_dir):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, build_dir)
                z.write(full, rel)

    print(f"Zipped {name}: {zip_path.stat().st_size} bytes")
    return zip_path

def render_variant_on_colab(variant, zip_path):
    name = variant["name"]
    print(f"\n==================== RENDERING {variant['label']} ON COLAB ====================")
    
    # 1. Upload build zip
    print(f"Uploading {zip_path.name} to Colab...")
    run_colab_cmd(["upload", "-s", "video-pilot-tts", str(zip_path), f"/content/{zip_path.name}"], timeout=120)
    
    # 2. Render code on Colab
    code = f'''
import subprocess, zipfile, os, shutil
from pathlib import Path

job_dir = Path('/content/jobs/ch1_{name}')
if job_dir.exists():
    shutil.rmtree(job_dir)
job_dir.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile('/content/{zip_path.name}') as z:
    z.extractall(job_dir)

env = dict(os.environ, 
           VP_CHROME_PATH='/content/render-runtime/chrome-wrapper.sh', 
           DISABLE_FROM_SURFACE='true')

print("Starting render for ch1_{name}...")
p = subprocess.run(['node', '/content/render-runtime/renderer/render.mjs', str(job_dir)], 
                   cwd='/content/render-runtime', env=env, capture_output=True, text=True)
print('RENDER_RETURNCODE:', p.returncode)
print(p.stdout)
if p.stderr:
    print('STDERR:', p.stderr[-500:])

mp4s = list(job_dir.glob('**/*.mp4'))
print('RENDERED_MP4S:', [str(m) for m in mp4s])
'''
    print(f"Executing render for ch1_{name} on Colab T4...")
    argv = [PY_BIN, ACCOUNT_CLI, ACCOUNT_DIR, "exec", "-s", "video-pilot-tts", "--timeout", "600"]
    res = subprocess.run(argv, input=code, capture_output=True, text=True)
    print(res.stdout)
    if "RENDER_RETURNCODE: 0" not in res.stdout:
        print("Render failed! Stderr:", res.stderr)
        raise RuntimeError(f"Render failed for {name}")

    # 3. Find and download MP4
    dest_mp4 = OUT_VIDEO_DIR / f"ch1_{name}_p22.mp4"
    print(f"Downloading rendered MP4 to {dest_mp4}...")
    run_colab_cmd(["download", "-s", "video-pilot-tts", f"/content/jobs/ch1_{name}/video.mp4", str(dest_mp4)], timeout=180)
    print(f"DOWNLOADED: {dest_mp4} ({dest_mp4.stat().st_size / (1024*1024):.2f} MB)")

    # Mirror to artifact directory video/ folder for review surface
    art_video_dir = Path("/home/hongphuoc6104/.gemini/antigravity/brain/ebb9330c-b49f-4fbc-930b-c1c2129f2704/video")
    art_video_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dest_mp4, art_video_dir / f"ch1_{name}_p22.mp4")
    print(f"MIRRORED TO ARTIFACT: {art_video_dir / f'ch1_{name}_p22.mp4'}")
    return dest_mp4

def main():
    print("=== Starting Chapter 1 Voice Comparison Production ===")
    results = []
    for var in VARIANTS:
        zip_path = build_variant_package(var)
        mp4_path = render_variant_on_colab(var, zip_path)
        results.append({"variant": var, "mp4": str(mp4_path)})

    print("\n=======================================================")
    print("ALL 3 CHAPTER 1 VIDEOS RENDERED SUCCESSFULLY!")
    print("=======================================================")
    for r in results:
        print(f" - {r['variant']['label']}: {r['mp4']}")

if __name__ == "__main__":
    main()
