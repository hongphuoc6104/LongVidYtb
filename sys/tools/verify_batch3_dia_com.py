import json, re
from pathlib import Path
from tools.editorial_value_linter import lint_editorial_and_narrative_quality
from tools.cta_tone_linter import lint_cta
from tools.script_diversity_linter import check_ai_cliche_phrases, check_intra_video_repetitions
from content_contract import validate_content, schema_errors

jobs = ["sys/runs/dia-com-batch3-9x16", "sys/runs/dia-com-batch3-16x9"]

for job in jobs:
    print(f"\n==================== VALIDATING {job} ====================")
    p = Path(job)
    brief = json.loads((p / "brief.json").read_text(encoding="utf-8"))
    content = json.loads((p / "content.json").read_text(encoding="utf-8"))
    outline = json.loads((p / "outline.json").read_text(encoding="utf-8"))
    comp = json.loads((p / "competitor_research.json").read_text(encoding="utf-8"))

    # 1. Schemas
    err_b = schema_errors("sys", "brief-v3.json", brief)
    assert not err_b, f"Brief schema errors in {job}: {err_b}"
    print("[PASS] Brief Schema v3")

    err_c = schema_errors("sys", "content-v3.json", content)
    assert not err_c, f"Content schema errors in {job}: {err_c}"
    print("[PASS] Content Schema v3")

    err_o = schema_errors("sys", "outline-v3.json", outline)
    assert not err_o, f"Outline schema errors in {job}: {err_o}"
    print("[PASS] Outline Schema v3")

    # 2. validate_content
    validate_content("sys", brief, 1, content["brief_hash"], content)
    print("[PASS] validate_content (M1 Contract)")

    # 3. Editorial & Visual Density Linter
    ed_rep = lint_editorial_and_narrative_quality(brief, content)
    errs = ed_rep["errors"]
    assert ed_rep["passed"], f"Editorial linter failed in {job}: {errs}"
    hold_sec = ed_rep["avg_unique_image_hold_sec"]
    sits = list(ed_rep["narrative_situations"].keys())
    print(f"[PASS] Editorial Linter: hold={hold_sec}s/img, situations={sits}")

    # 4. CTA Linter
    cta_err = lint_cta(brief, content)
    assert not cta_err, f"CTA errors in {job}: {cta_err}"
    print("[PASS] CTA Tone Linter (0 errors)")

    # 5. Diversity & Clichés
    cliche_err = check_ai_cliche_phrases(content["scenes"])
    assert not cliche_err, f"AI Cliche violations in {job}: {cliche_err}"
    print("[PASS] AI Cliché Linter (0 violations)")

    intra_err = check_intra_video_repetitions(content["scenes"])
    assert not intra_err, f"Intra-video repetitions in {job}: {intra_err}"
    print("[PASS] Intra-Video Repetitions (0 violations)")

    # 6. Specific rules audit
    # Hyphens in Vietnamese narration
    for sc in content["scenes"]:
        narr = sc.get("narration", "")
        assert "-" not in narr, f"Hyphen found in narration of {job} {sc['id']}: {narr}"
    print("[PASS] Zero hyphens in spoken narration")

    # YouTube title length <= 55
    yt_title = brief.get("youtube_title", "")
    assert len(yt_title) <= 55, f"YouTube title > 55 chars in {job}: {len(yt_title)} chars: {yt_title}"
    print(f"[PASS] YouTube title length <= 55 chars ({len(yt_title)} chars): {yt_title}")

    # Motion prompt check
    for sc in content["scenes"]:
        for img in sc.get("images", []):
            mp = img.get("motion_prompt", "")
            assert mp.endswith("silent visual storytelling, no talking, no lip movement"), f"Invalid motion prompt ending in {job} {img['id']}: {mp}"
    print("[PASS] All motion prompts end with silent visual storytelling, no talking, no lip movement")

    # 1-to-1 beat to image mapping
    all_beats = [b for sc in content["scenes"] for b in sc.get("beats", [])]
    all_images = [img for sc in content["scenes"] for img in sc.get("images", [])]
    assert len(all_beats) == len(all_images), f"Beats count {len(all_beats)} != Images count {len(all_images)}"
    beat_img_ids = [b["image_id"] for b in all_beats]
    img_ids = [img["id"] for img in all_images]
    assert beat_img_ids == img_ids, f"Beat image_ids do not match image ids in order in {job}"
    print(f"[PASS] Exact 1-to-1 Beat-to-Image mapping ({len(all_beats)} beats, {len(all_images)} images)")

    # Final beat endcard check
    last_beat = all_beats[-1]
    last_img = all_images[-1]
    assert last_beat.get("is_endcard") is True, f"Last beat is_endcard not True in {job}"
    assert last_beat.get("tempo") == "hold", f"Last beat tempo not hold in {job}"
    assert last_beat.get("effect") == "hold", f"Last beat effect not hold in {job}"
    assert last_img.get("is_endcard") is True, f"Last image is_endcard not True in {job}"
    print("[PASS] Final beat endcard verified (is_endcard: true, tempo: hold, effect: hold)")

print("\n>>> ALL QUALITY GATES PASSED 100% WITH ZERO ERRORS! <<<")
