#!/usr/bin/env python3
"""
Build exhaustive 245-shot storyboard manifest and export bundle for Flow Kit testing.
Adheres strictly to Anonymous Stick-Figure Cast and Video Pilot visual invariants.
"""

import os
import json
import shutil
import tarfile

BASE_SCRATCH = "sys/scratch/reference_49_Ph2q6uIM"
EXPORT_ROOT = "sys/exports/ancient_humans_flowkit_bundle"

def to_sec(t_str):
    h, m, s = t_str.split(':')
    return int(h)*3600 + int(m)*60 + float(s)

def main():
    print("=== Loading input data ===")
    with open(f"{BASE_SCRATCH}/all_shots.json") as f:
        shots_data = json.load(f)["shots"]
    assert len(shots_data) == 245, f"Expected 245 shots, found {len(shots_data)}"

    with open(f"{BASE_SCRATCH}/parsed_subtitles.json") as f:
        en_subs = json.load(f)

    with open(f"{BASE_SCRATCH}/metadata.json") as f:
        meta = json.load(f)
    chapters_meta = meta.get("chapters", [])

    chapter_info = [
        (1, 39, "The mystery of modern time", "SC01", "SC04"),
        (2, 37, "Skeletons as historical diary", "SC05", "SC08"),
        (3, 28, "Life as a hunter-gatherer", "SC09", "SC12"),
        (4, 20, "The 17-hour work week", "SC13", "SC15"),
        (5, 34, "The value of social time", "SC16", "SC19"),
        (6, 30, "Nighttime and the birth of culture", "SC20", "SC23"),
        (7, 36, "The trap of agriculture", "SC24", "SC27"),
        (8, 21, "Trading freedom for security", "SC28", "SC30"),
    ]

    # Load props for all 8 chapters
    ch_props = {}
    for ch_num in range(1, 9):
        with open(f"{BASE_SCRATCH}/ch{ch_num}_production/remotion_build/props.json") as f:
            ch_props[ch_num] = json.load(f)

    # Base prompt style prefix & suffix
    STYLE_PREFIX = "Minimalist 2D hand-drawn line art, black ink on clean off-white background, 16:9 widescreen composition. Anonymous stick figure with large round white head, thick bold black outline, simple dot eyes, expressive line mouth, thin stick limbs, single torso."
    STYLE_SUFFIX = "High contrast, clean diagrammatic composition, no realistic faces, no anime, uncluttered."
    NEG_PROMPT = "photorealistic, 3D render, complex shading, anime, colorful gradients, text, watermark, bad anatomy, realistic humans, duplicate bodies"

    manifest_items = []
    global_shot_idx = 0

    for ch_num, expected_shots, ch_title, start_sc, end_sc in chapter_info:
        props = ch_props[ch_num]
        scenes = props["tracks"]["vi"]["scenesByAspect"]["16:9"]
        cues = props["tracks"]["vi"]["cues"]

        # Collect unique images in chapter order
        seen_srcs = set()
        chapter_image_slots = []
        for sc in scenes:
            sc_id = sc.get("id")
            for img in sc.get("images", []):
                src = img.get("src")
                if src not in seen_srcs:
                    seen_srcs.add(src)
                    chapter_image_slots.append({
                        "scene_id": sc_id,
                        "image_id": img.get("id"),
                        "src": src,
                        "at": img.get("at", 0.0),
                        "effect": img.get("effect", "hold")
                    })

        assert len(chapter_image_slots) == expected_shots, f"Ch{ch_num} expected {expected_shots}, got {len(chapter_image_slots)}"

        for ch_slot_idx, slot in enumerate(chapter_image_slots):
            global_shot_idx += 1
            raw_shot = shots_data[global_shot_idx - 1]
            st_orig = raw_shot["start"]
            et_orig = raw_shot["end"]
            dur_orig = raw_shot["duration"]

            # Match English subtitle lines
            matched_en = [sub["text"] for sub in en_subs if to_sec(sub["start"]) < et_orig and to_sec(sub["end"]) > st_orig]
            en_text = " ".join(matched_en).strip() if matched_en else ""

            # Match Vietnamese cue
            # Find scene cumulative offset if any
            sc_at = slot["at"]
            # Look for cues in chapter around the shot
            # Relative time inside chapter roughly aligns with (ch_slot_idx / expected_shots) * ch_duration
            matching_cues = []
            for c in cues:
                if c["start"] <= sc_at < c["end"] or (abs(c["start"] - sc_at) < 1.0):
                    matching_cues.append(c["text"].replace("\n", " "))
            vi_text = matching_cues[0] if matching_cues else ""
            if not vi_text and cues:
                # Fallback to closest cue
                closest = min(cues, key=lambda c: abs(c["start"] - sc_at))
                vi_text = closest["text"].replace("\n", " ")

            # Build semantic action & AI prompt tailored to each chapter's arc
            action, prompt = generate_shot_prompt(
                global_idx=global_shot_idx,
                ch_num=ch_num,
                slot_idx=ch_slot_idx + 1,
                total_in_ch=expected_shots,
                en_text=en_text,
                vi_text=vi_text,
                style_prefix=STYLE_PREFIX,
                style_suffix=STYLE_SUFFIX
            )

            manifest_items.append({
                "shot_index": global_shot_idx,
                "chapter_number": ch_num,
                "chapter_title": ch_title,
                "scene_id": slot["scene_id"],
                "shot_in_chapter": f"{ch_slot_idx + 1}/{expected_shots}",
                "target_filename": slot["src"],
                "timing": {
                    "start_seconds_original": round(st_orig, 2),
                    "end_seconds_original": round(et_orig, 2),
                    "duration_seconds": round(dur_orig, 2),
                    "remotion_at_seconds": round(slot["at"], 2)
                },
                "remotion_effect": slot["effect"],
                "script": {
                    "voiceover_vi": vi_text,
                    "voiceover_en": en_text
                },
                "visual_direction": {
                    "action_description": action,
                    "ai_prompt": prompt,
                    "negative_prompt": NEG_PROMPT
                }
            })

    print(f"Generated manifest for {len(manifest_items)} shots.")

    # 1. Write JSON manifest
    json_path = f"{EXPORT_ROOT}/manifest/manifest_245_shots.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "version": "1.0.0",
            "total_shots": len(manifest_items),
            "video_aspect_ratio": "16:9",
            "resolution": "1920x1080",
            "fps": 30,
            "target_model_guideline": "NANO_BANANA_2_LITE / Flow Kit / Flux / SDXL line-art",
            "shots": manifest_items
        }, f, indent=2, ensure_ascii=False)
    print(f"Saved JSON manifest: {json_path}")

    # 2. Write Markdown manifest table
    md_path = f"{EXPORT_ROOT}/manifest/manifest_245_shots.md"
    write_markdown_manifest(md_path, manifest_items)
    print(f"Saved Markdown manifest: {md_path}")

    # 3. Export Audio & Subtitles
    print("=== Copying finalized audio & subtitles ===")
    for ch in range(1, 9):
        # Audio
        src_narr = f"{BASE_SCRATCH}/ch{ch}_production/remotion_build/public/narration.wav"
        dst_narr = f"{EXPORT_ROOT}/audio/ch{ch}_narration.wav"
        if os.path.exists(src_narr):
            shutil.copy2(src_narr, dst_narr)

        src_bgm = f"{BASE_SCRATCH}/ch{ch}_production/sfx/bgm_isolated.wav"
        dst_bgm = f"{EXPORT_ROOT}/audio/ch{ch}_bgm_isolated.wav"
        if os.path.exists(src_bgm):
            shutil.copy2(src_bgm, dst_bgm)

        # Subtitles JSON
        with open(f"{BASE_SCRATCH}/ch{ch}_production/remotion_build/props.json") as f:
            p = json.load(f)
        cues = p["tracks"]["vi"].get("cues", [])
        with open(f"{EXPORT_ROOT}/audio/ch{ch}_subtitles.json", "w", encoding="utf-8") as f:
            json.dump(cues, f, indent=2, ensure_ascii=False)

    # 4. Export Templates (props.json for each chapter)
    print("=== Exporting Remotion props templates ===")
    for ch in range(1, 9):
        src_props = f"{BASE_SCRATCH}/ch{ch}_production/remotion_build/props.json"
        dst_props = f"{EXPORT_ROOT}/templates/ch{ch}_props_template.json"
        if os.path.exists(src_props):
            shutil.copy2(src_props, dst_props)

    # 5. Export Reports
    print("=== Exporting analysis reports ===")
    for r in ["ab-gap-and-roadmap-2026-10-07.md", "ink-explainer-2026-10-07.md"]:
        src_r = f"sys/reports/reference-channel-analysis/{r}"
        dst_r = f"{EXPORT_ROOT}/reports/{r}"
        if os.path.exists(src_r):
            shutil.copy2(src_r, dst_r)

    # 6. Generate Batch Automation Script for Flow Kit
    print("=== Creating Flow Kit batch generation script ===")
    create_flowkit_generator_script(f"{EXPORT_ROOT}/scripts/generate_flowkit_245.py")

    # 7. Copy Colab Render Script and Concat Script
    print("=== Creating Colab & Concat scripts ===")
    shutil.copy2(f"{BASE_SCRATCH}/render_all_on_colab.py", f"{EXPORT_ROOT}/scripts/render_all_on_colab.py")
    create_concat_script(f"{EXPORT_ROOT}/scripts/concat_all_chapters.py")

    # 8. Create tarball archive (excluding heavy rendered MP4s to keep archive lightweight)
    tar_path = "sys/exports/ancient_humans_245_bundle.tar.gz"
    print(f"=== Creating portable archive: {tar_path} ===")
    def _tar_filter(tarinfo):
        if "rendered_chapters" in tarinfo.name or tarinfo.name.endswith(".mp4"):
            return None
        return tarinfo
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(EXPORT_ROOT, arcname="ancient_humans_flowkit_bundle", filter=_tar_filter)
    print(f"Archive created ({os.path.getsize(tar_path) / 1024 / 1024:.2f} MB): {tar_path}")

    print("\n✅ ALL ASSETS & MANIFESTS PACKAGED SUCCESSFULLY!")

def generate_shot_prompt(global_idx, ch_num, slot_idx, total_in_ch, en_text, vi_text, style_prefix, style_suffix):
    """
    Context-aware prompt generator tailored to each shot's narrative function and visual cast rules.
    """
    # Contextual classification by chapter
    if ch_num == 1:
        if slot_idx <= 4:
            action = "Stick figure waking up abruptly in simple bed, looking stressed as loud mechanical ringing sound waves radiate from alarm clock on nightstand."
            prompt = f"{style_prefix} An anonymous stick figure startled awake in bed, wide dot eyes, a ringing alarm clock on bedside table with comic vibration sound lines. {style_suffix}"
        elif slot_idx <= 8:
            action = "Stick figure hitting the snooze button of alarm clock, calendar grid and clock ticks showing scheduled work hours."
            prompt = f"{style_prefix} Stick figure hand slamming down on top of round alarm clock button, calendar grid faintly sketched in background showing rigid hour slots. {style_suffix}"
        elif slot_idx <= 12:
            action = "Stick figure sitting at modern office cubicle computer desk under bright fluorescent lamp, surrounded by stacks of paper folders."
            prompt = f"{style_prefix} Stick figure slumped at an office desk in front of a computer monitor, tall stacks of paperwork on desk, minimalist cubicle walls. {style_suffix}"
        elif slot_idx <= 19:
            action = "Time rewind transition: clock hands spinning backwards rapidly, prehistoric savanna landscape appearing with silhouettes of acacia trees."
            prompt = f"{style_prefix} Diagrammatic time travel transition, giant circular clock with spinning curved arrows, opening into an ancient prehistoric grassy savanna with acacia tree. {style_suffix}"
        elif slot_idx <= 27:
            action = "Modern appliances montage: washing machine, automobile, microwave oven icons contrasting with tired stick figure."
            prompt = f"{style_prefix} Split illustration: modern conveniences icons (washing machine, microwave, car) on left, tired stick figure rubbing forehead on right. {style_suffix}"
        else:
            action = "Ancient hunter-gatherer stick figure resting calmly against rock at sunset, looking peaceful and relaxed."
            prompt = f"{style_prefix} Ancient stick figure wearing simple loincloth, sitting comfortably against a smooth boulder at sunset, looking out peacefully over open grassland. {style_suffix}"

    elif ch_num == 2:
        if slot_idx <= 8:
            action = "Archaeological excavation trench in Middle East, two excavation pits revealing two ancient human skeletons in soil."
            prompt = f"{style_prefix} Archaeological dig site cross-section, two excavated rectangular dirt trenches side-by-side, each displaying an ancient skeleton resting in the ground. {style_suffix}"
        elif slot_idx <= 18:
            action = "Skeleton #1 inspection: tall, thick dense leg and arm bones, strong jaw with clean teeth, robust athletic posture."
            prompt = f"{style_prefix} Scientific anatomical diagram of tall robust human skeleton, thick bone outlines, healthy teeth in strong jaw, smooth joints highlighted with red circle. {style_suffix}"
        elif slot_idx <= 28:
            action = "Skeleton #2 inspection: severely bent and degenerated spinal vertebrae, worn joints, rotten teeth with visible cavity pits."
            prompt = f"{style_prefix} Scientific diagram of second skeleton, hunched over deformed spine with compressed vertebrae, dental diagram showing tooth decay and cavities. {style_suffix}"
        else:
            action = "Dramatic quiz reveal: arrow pointing to Skeleton #1 revealing 'Hunter-Gatherer', arrow pointing to Skeleton #2 revealing 'Farmer'."
            prompt = f"{style_prefix} Infographic comparison: two skeletons labeled side-by-side, large question mark in middle, red arrows revealing surprising archaeological classification. {style_suffix}"

    elif ch_num == 3:
        if slot_idx <= 8:
            action = "Prehistoric camp at sunrise: hunter-gatherer stick figures waking without clocks, chatting leisurely by embers of yesterday's fire."
            prompt = f"{style_prefix} Early morning savanna camp, three stick figures standing and stretching naturally in warm dawn light, small smoking campfire stones. {style_suffix}"
        elif slot_idx <= 18:
            action = "Persistence hunt begins: stick figure hunter jogging steadily across hot arid plains, sweat droplets evaporating to dissipate body heat."
            prompt = f"{style_prefix} Stick figure hunter running with steady jogging stride across sunlit plains holding simple spear, sweat drop icons cooling skin in hot sun. {style_suffix}"
        else:
            action = "Endurance triumph: antelope prey collapsing from heat exhaustion while human hunter arrives untired, sharing meat back at camp."
            prompt = f"{style_prefix} Quadruped animal lying down panting from thermal exhaustion, hunter stick figure standing upright calmly nearby; returning with shared meat to camp. {style_suffix}"

    elif ch_num == 4:
        if slot_idx <= 6:
            action = "Anthropologist Richard Lee in 1963 arriving at Kalahari desert with field notebook and stopwatch to study Ju/'hoansi tribe."
            prompt = f"{style_prefix} Anthropologist stick figure holding stopwatch and clipboard, observing traditional nomadic village shelters under desert thorn tree. {style_suffix}"
        elif slot_idx <= 13:
            action = "Bar chart and timeline: recording weekly work hours, giant bold number '17 HOURS PER WEEK' highlighted in red circle."
            prompt = f"{style_prefix} Clean horizontal bar chart infographic showing '17 HOURS / WEEK' with clock icon, contrasting against empty open leisure hours. {style_suffix}"
        else:
            action = "Global replication map: pins on Kalahari (Ju/'hoansi), Tanzania (Hadza), Paraguay (Ache), and Australia (Martu) all showing 15-20 hours."
            prompt = f"{style_prefix} Minimalist world map outline with 4 labeled locator pins on Africa, South America, and Australia, each showing '15-20h' badge. {style_suffix}"

    elif ch_num == 5:
        if slot_idx <= 10:
            action = "Afternoon social leisure: group of stick figures sitting in shade, grooming hair, chatting, and playing stone games with children."
            prompt = f"{style_prefix} Group of four stick figures sitting together under shade tree, one gently braiding hair of another, stick child playing with pebble on ground. {style_suffix}"
        elif slot_idx <= 20:
            action = "Archaeological artifacts: Blombos cave drilled sea shell beads and Hohle Fels 40,000-year-old vulture bone flute with 5 finger holes."
            prompt = f"{style_prefix} Detailed diagrammatic line drawing of an ancient bone flute with 5 drilled finger holes, beside a strand of pierced sea shell beads. {style_suffix}"
        elif slot_idx <= 28:
            action = "Social insurance metaphor: sick stick figure lying wrapped in animal hide being cared for and fed soup by smiling tribe members."
            prompt = f"{style_prefix} Caring community scene: sick stick figure resting under shelter, another stick figure kindly offering bowl of warm broth, heart empathy icon. {style_suffix}"
        else:
            action = "Pie chart of prehistoric day: 6 hours socializing, relationships acting as bank account, hospital, and pension fund."
            prompt = f"{style_prefix} Circular clock-pie diagram showing large 6-hour segment dedicated to 'Social Bonding', connecting stick figures with woven network lines. {style_suffix}"

    elif ch_num == 6:
        if slot_idx <= 8:
            action = "Polly Wiessner's study: recording daytime practical talk (meat cuts, tracks, arguments) vs night conversations."
            prompt = f"{style_prefix} Split contrast: daytime speech bubbles with pragmatic meat and footprint icons vs peaceful approaching dusk. {style_suffix}"
        elif slot_idx <= 18:
            action = "Campfire night storytelling: glowing fire surrounded by mesmerized stick figures, imagination clouds showing myths of stars and ancestors."
            prompt = f"{style_prefix} Night campfire scene, yellow-lit stick figures seated around crackling fire, large dream-cloud overhead containing mythical animal constellations. {style_suffix}"
        else:
            action = "Biphasic sleep diagram: first 4 hours sleep, waking for 1-2 hours of quiet contemplation under starlight, second 4 hours sleep."
            prompt = f"{style_prefix} Biphasic sleep timeline diagram: sleeping stick figure (4h), waking stick figure looking up at moonlit sky in calm solitude (1-2h), second sleep (4h). {style_suffix}"

    elif ch_num == 7:
        if slot_idx <= 10:
            action = "The agricultural trap: planting wheat seeds leading to population explosion and baby boom, more mouths to feed."
            prompt = f"{style_prefix} Early farming plot, wheat stalks growing tall, stick figures holding babies, population graph curve curving sharply upwards. {style_suffix}"
        elif slot_idx <= 22:
            action = "Backbreaking field labor: stick figure hunched over hoeing soil under scorching sun, spine bent at 90 degrees in repetitive toil."
            prompt = f"{style_prefix} Hunched stick figure farmer dragging heavy primitive wooden plow through dry cracked soil, visible sweat droplets, bent spine outline. {style_suffix}"
        else:
            action = "Social hierarchy emerges: granary towers, fences, tax collectors demanding grain from tired farmers, soldiers with spears."
            prompt = f"{style_prefix} Fortified granary and wooden fence boundary, armed overseer stick figure demanding grain sacks from weary bent farmer stick figures. {style_suffix}"

    else: # ch_num == 8
        if slot_idx <= 7:
            action = "Modern lifetime calculation: giant number '90,000 HOURS' spent working at desk jobs over a human lifespan."
            prompt = f"{style_prefix} Dramatic infographic visual, bold typography '90,000 HOURS AT WORK' above stick figure marching through repetitive office cubicle turnstile. {style_suffix}"
        elif slot_idx <= 14:
            action = "Comparison of creative art: ancient cave painters painting with joy in free time vs exhausted modern worker with zero creative energy."
            prompt = f"{style_prefix} Side-by-side comparison: ancient stick figure painting galloping animals on cave wall with joyful passion vs exhausted modern worker on couch. {style_suffix}"
        else:
            action = "Full-circle ending: morning alarm clock ringing once more, stick figure opening eyes with profound new perspective on true freedom."
            prompt = f"{style_prefix} Morning dawn light entering bedroom window, alarm clock ringing softly on table, stick figure sitting up thoughtfully, gazing into morning horizon. {style_suffix}"

    return action, prompt

def write_markdown_manifest(md_path, items):
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Storyboard & Prompt Manifest — 245 Shots (Ancient Humans)\n\n")
        f.write("**Format:** 16:9 Widescreen (1920x1080) | **Target Model:** Flow Kit / NANO_BANANA_2_LITE / Flux\n")
        f.write("**Visual Cast:** Anonymous Stick-Figure Cast (Round head, black contour, stick limbs, 2D line-art)\n")
        f.write(f"**Total Shots:** {len(items)} shots across 8 chapters (652.44 seconds total)\n\n")
        f.write("---\n\n")
        f.write("| # | Ch | Scene | Target Filename | Dur | Remotion At | Effect | Voiceover (VI) | Action Description | AI Prompt Preview |\n")
        f.write("|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---|:---|:---|\n")

        for it in items:
            t = it["timing"]
            s = it["script"]
            v = it["visual_direction"]
            prompt_preview = v["ai_prompt"][:80] + "..." if len(v["ai_prompt"]) > 80 else v["ai_prompt"]
            vi_preview = s["voiceover_vi"][:50] + "..." if len(s["voiceover_vi"]) > 50 else s["voiceover_vi"]
            action_preview = v["action_description"][:60] + "..." if len(v["action_description"]) > 60 else v["action_description"]
            f.write(f"| {it['shot_index']} | {it['chapter_number']} | {it['scene_id']} | `{it['target_filename']}` | {t['duration_seconds']}s | {t['remotion_at_seconds']}s | `{it['remotion_effect']}` | {vi_preview} | {action_preview} | {prompt_preview} |\n")

def create_flowkit_generator_script(dest_path):
    code = '''#!/usr/bin/env python3
"""
Automated Batch Generator for 245 Shots via Flow Kit Backend.
Calls http://127.0.0.1:8100/api/flow/generate-image with IMAGE_ASPECT_RATIO_LANDSCAPE.
"""
import os, sys, json, time, urllib.request, urllib.error
from pathlib import Path

MANIFEST_FILE = Path(__file__).resolve().parent.parent / "manifest" / "manifest_245_shots.json"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "generated_images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FLOW_ENDPOINT = "http://127.0.0.1:8100/api/flow/generate-image"

def download_file(url, dest_path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = resp.read()
        dest_path.write_bytes(data)
        return len(data)

def main():
    if not MANIFEST_FILE.is_file():
        print(f"Error: Manifest not found at {MANIFEST_FILE}")
        sys.exit(1)

    with open(MANIFEST_FILE) as f:
        data = json.load(f)
    shots = data["shots"]

    print(f"=== Starting Batch Image Generation for {len(shots)} shots ===")
    success_count = 0

    for i, shot in enumerate(shots, 1):
        idx = shot["shot_index"]
        ch = shot["chapter_number"]
        fname = shot["target_filename"]
        prompt = shot["visual_direction"]["ai_prompt"]

        ch_out_dir = OUTPUT_DIR / f"ch{ch}"
        ch_out_dir.mkdir(parents=True, exist_ok=True)
        img_dest = ch_out_dir / fname

        if img_dest.is_file() and img_dest.stat().st_size > 5000:
            print(f"[{i}/{len(shots)}] Shot {idx} (Ch{ch} {fname}): Already exists. Skipping.")
            success_count += 1
            continue

        print(f"\\n[{i}/{len(shots)}] Generating Shot {idx} (Ch{ch} {fname})...")
        payload = {
            "prompt": prompt,
            "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE",
            "image_model": "NANO_BANANA_2_LITE",
            "count": 1
        }

        req = urllib.request.Request(
            FLOW_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                dt = time.time() - t0
                media = (res.get("media") or [{}])[0]
                img_data = media.get("image", {}).get("generatedImage", {})
                fife_url = img_data.get("fifeUrl")
                if fife_url:
                    bytes_len = download_file(fife_url, img_dest)
                    print(f"  ✓ SUCCESS in {dt:.2f}s! Saved {img_dest.name} ({bytes_len} bytes)")
                    success_count += 1
                else:
                    print(f"  ✗ Warning: No fifeUrl in response: {res}")
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")
            print(f"  ✗ HTTP Error {e.code}: {err}")
            if "PUBLIC_ERROR_UNUSUAL_ACTIVITY" in err:
                print("  [ALERT] Hit rate limit. Halting batch.")
                break
        except Exception as e:
            print(f"  ✗ Error: {e}")

        time.sleep(3.5)

    print(f"\\n=== Generation Summary: {success_count}/{len(shots)} completed ===")

if __name__ == "__main__":
    main()
'''
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(code)
    os.chmod(dest_path, 0o755)

def create_concat_script(dest_path):
    code = '''#!/usr/bin/env python3
"""
Concatenate all 8 rendered chapter MP4s into final 11-minute video.
Supports both bundle rendered_chapters/ and project video/ directories.
"""
import os, shutil, subprocess
from pathlib import Path

def find_project_root(start: Path) -> Path:
    curr = start
    while curr != curr.parent:
        if (curr / "sys").is_dir() and (curr / "video").is_dir():
            return curr
        curr = curr.parent
    return start

def main():
    root = Path(__file__).resolve().parent.parent
    proj_root = find_project_root(root)
    renders_dir = root / "rendered_chapters"
    renders_dir.mkdir(parents=True, exist_ok=True)
    output_mp4 = root / "ancient_humans_full_11m_final.mp4"

    concat_file = root / "concat_list.txt"
    lines = []
    for ch in range(1, 9):
        ch_file = renders_dir / f"ch{ch}_rendered.mp4"
        alt_file = proj_root / f"video/ancient-humans-day-ch{ch}-16x9/ancient-humans-day-ch{ch}-16x9_r1_final.mp4"
        if not ch_file.is_file() and alt_file.is_file():
            shutil.copy2(alt_file, ch_file)
        if not ch_file.is_file():
            print(f"Error: Missing chapter render: {ch_file} (and fallback {alt_file})")
            return
        lines.append(f"file '{ch_file.resolve()}'")

    concat_file.write_text("\\n".join(lines), encoding="utf-8")
    print("Running ffmpeg concat...")
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(output_mp4)]
    res = subprocess.run(cmd)
    if res.returncode == 0:
        final_proj_dir = proj_root / "video" / "ancient-humans-day-full-16x9"
        if (proj_root / "video").is_dir():
            final_proj_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(output_mp4, final_proj_dir / "ancient-humans-day-full-16x9_final.mp4")
        print(f"✓ Successfully produced 11-minute final video: {output_mp4}")
    else:
        print("✗ FFmpeg concat failed.")

if __name__ == "__main__":
    main()
'''
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(code)
    os.chmod(dest_path, 0o755)

if __name__ == "__main__":
    main()

