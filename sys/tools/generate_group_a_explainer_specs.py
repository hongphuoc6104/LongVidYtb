#!/usr/bin/env python3
"""
Group A Explainer Spec Architect:
Generates 255-305 Beat Explainer Visual Specs (<slug>_long_explainer_spec.json)
for the 5 Science/Body/Brain/Physics Channels:
1. co_the_ke (305 beats)
2. dia_com (305 beats)
3. nao_luoi (305 beats)
4. ua_sao_vay (305 beats)
5. vu_tru_ti_hon (255 beats)

Enforces:
1. assert len(set(b["prompt"].strip() for b in beats)) == len(beats)
2. new_beats core subjects 100% unique (max_repeat == 1)
3. ZERO "8k" / "8K" keywords (Full HD 1080p standard)
4. Exact reuse of all valid existing images (117 or 98)
5. Word counts strictly 35-65 words ending with ", zero text overlay, no watermarks"
"""

import json
import os
import re
import wave
from typing import Dict, List, Any, Tuple, Optional, Set

from tools.channel_data_co_the_ke import CO_THE_KE_NEW_PROMPTS
from tools.channel_data_dia_com import DIA_COM_NEW_PROMPTS
from tools.channel_data_nao_luoi import NAO_LUOI_NEW_PROMPTS
from tools.channel_data_ua_sao_vay import UA_SAO_VAY_NEW_PROMPTS
from tools.channel_data_vu_tru_ti_hon import VU_TRU_TI_HON_NEW_PROMPTS

CHANNEL_NEW_PROMPTS = {
    "co_the_ke": CO_THE_KE_NEW_PROMPTS,
    "dia_com": DIA_COM_NEW_PROMPTS,
    "nao_luoi": NAO_LUOI_NEW_PROMPTS,
    "ua_sao_vay": UA_SAO_VAY_NEW_PROMPTS,
    "vu_tru_ti_hon": VU_TRU_TI_HON_NEW_PROMPTS,
}

FORBIDDEN_PHRASES = [
    "detailed visual narrative illustration",
    "continuing scene continuity",
    "person sitting in room",
    "sitting on edge of mattress",
    "two hands holding",
]

CHANNELS = ["co_the_ke", "dia_com", "nao_luoi", "ua_sao_vay", "vu_tru_ti_hon"]

CONFIGS = {
    "co_the_ke": {
        "slug": "co_the_ke",
        "hyphen_slug": "co-the-ke",
        "total_cues": 305,
        "style_prefix": "High-definition 3D biomedical anatomical animation still",
        "tail": "Nucleus Medical Media scientific clarity, vivid translucent organic tissues, glowing cellular dynamics, medical laboratory studio lighting, zero text overlay, no watermarks",
    },
    "dia_com": {
        "slug": "dia_com",
        "hyphen_slug": "dia-com",
        "total_cues": 305,
        "style_prefix": "Cinematic macro culinary food science photography",
        "tail": "35mm commercial culinary cinematography, shallow depth of field, glistening mouth-watering textures, vibrant natural gastronimic studio lighting, zero text overlay, no watermarks",
    },
    "nao_luoi": {
        "slug": "nao_luoi",
        "hyphen_slug": "nao-luoi",
        "total_cues": 305,
        "style_prefix": "3D neuroscience and cognitive psychology explainer visualization",
        "tail": "high-contrast conceptual clarity, vivid glowing bio-electric synapses, clean scientific infographic diorama, soft ambient laboratory studio lighting, zero text overlay, no watermarks",
    },
    "ua_sao_vay": {
        "slug": "ua_sao_vay",
        "hyphen_slug": "ua-sao-vay",
        "total_cues": 305,
        "style_prefix": "High-definition 3D somatosensory and physics explainer diorama",
        "tail": "optical laboratory physics diorama, translucent acrylic light pathways, clean tactile mechanics, balanced studio illumination, zero text overlay, no watermarks",
    },
    "vu_tru_ti_hon": {
        "slug": "vu_tru_ti_hon",
        "hyphen_slug": "vu-tru-ti-hon",
        "total_cues": 255,
        "style_prefix": "Cinematic deep space astronomical documentary diorama",
        "tail": "photorealistic astrophysical clarity, radiant stellar luminescence, detailed celestial mechanics, scientific documentary studio lighting, zero text overlay, no watermarks",
    },
}


def parse_srt(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.strip().split("\n\n")
    cues = []
    for b in blocks:
        lines = b.strip().split("\n")
        if len(lines) >= 3:
            idx = int(lines[0])
            m = re.match(r"(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)", lines[1])
            if m:
                s_h, s_m, s_s, s_ms = map(int, m.groups()[:4])
                e_h, e_m, e_s, e_ms = map(int, m.groups()[4:])
                start_sec = s_h * 3600 + s_m * 60 + s_s + s_ms / 1000.0
                end_sec = e_h * 3600 + e_m * 60 + e_s + e_ms / 1000.0
                text = " ".join(lines[2:]).strip()
                cues.append({
                    "cue_idx": idx,
                    "start": start_sec,
                    "end": end_sec,
                    "duration": end_sec - start_sec,
                    "text": text,
                })
    return cues


def get_wav_duration(path: str) -> float:
    with wave.open(path, "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


def clean_and_constrain_prompt(prefix: str, core: str, tail: str, min_words: int = 35, max_words: int = 65) -> str:
    core_clean = core
    for fp in FORBIDDEN_PHRASES:
        core_clean = re.sub(re.escape(fp), "", core_clean, flags=re.IGNORECASE)
    core_clean = re.sub(r"\b8[kK]\b", "crisp Full HD 1080p", core_clean)
    core_clean = re.sub(r"\s+", " ", core_clean).strip(" ,;")
    
    if core_clean.lower().startswith(prefix.lower()):
        core_clean = core_clean[len(prefix):].strip(" ,;")
        
    suffix = ", zero text overlay, no watermarks"
    if tail.endswith("zero text overlay, no watermarks"):
        tail_base = tail[:-len("zero text overlay, no watermarks")].strip(" ,;")
    else:
        tail_base = tail.strip(" ,;")
    tail_base = re.sub(r"\b8[kK]\b", "crisp Full HD 1080p", tail_base)
        
    full = f"{prefix}, {core_clean}, {tail_base}{suffix}"
    words = full.split()
    
    if len(words) < min_words:
        pad = "sharp focus, high visual clarity, ample negative space"
        full = f"{prefix}, {core_clean}, {pad}, {tail_base}{suffix}"
        words = full.split()
        
    if len(words) < min_words:
        pad2 = "expertly rendered cinematic composition with clean scientific accuracy"
        full = f"{prefix}, {core_clean}, {pad2}, {tail_base}{suffix}"
        words = full.split()

    if len(words) > max_words:
        short_tail = "studio lighting"
        full = f"{prefix}, {core_clean}, {short_tail}{suffix}"
        words = full.split()
        if len(words) > max_words:
            excess = len(words) - max_words
            core_words = core_clean.split()
            trimmed_core = " ".join(core_words[:-excess])
            full = f"{prefix}, {trimmed_core}, {short_tail}{suffix}"
            
    if not full.endswith(", zero text overlay, no watermarks"):
        full = full.rstrip(" ,;") + ", zero text overlay, no watermarks"
        
    full = re.sub(r"\b8[kK]\b", "crisp Full HD 1080p", full)
    return full


def extract_clean_old_core(old_prompt: str) -> str:
    p = old_prompt
    for pfx in [
        "High-definition 3D biomedical anatomical animation still,",
        "Cinematic macro culinary food science photography,",
        "Hand-drawn 2D Vietnamese indie doodle explainer illustration (Nghech Ngoac webcomic aesthetic),",
        "High-definition 3D somatosensory and physics explainer diorama,",
        "Cinematic deep space astronomical documentary diorama,",
        "3D neuroscience & cognitive psychology explainer visualization,",
        "3D neuroscience and cognitive psychology explainer visualization,",
    ]:
        if p.startswith(pfx):
            p = p[len(pfx):].strip()
            break
            
    p = re.sub(r"^(Establishing wide diorama|Detailed scene showing|Macro close-up cutaway burst focusing on|Dynamic perspective cutaway showing|Visual mechanism cutaway demonstrating):\s*", "", p, flags=re.IGNORECASE)
    
    for tail_pat in [
        r"Nucleus Medical Media scientific clarity.*$",
        r"raw freehand MS-Paint marker linework.*$",
        r"35mm commercial culinary cinematography.*$",
        r"optical laboratory physics diorama.*$",
        r"Kip Thorne relativistic astrophysics accuracy.*$",
        r"photorealistic astrophysical clarity.*$",
        r"high-contrast conceptual clarity.*$",
        r"standard clear composition with.*$",
    ]:
        p = re.sub(tail_pat, "", p, flags=re.IGNORECASE).strip(" ,;")
        
    p = re.sub(r"\b8[kK]\b", "crisp Full HD 1080p", p)
    return p.strip()


def determine_explainer_type(prompt: str, cue_text: str, default_type: str = "MECHANISM_CUTAWAY") -> str:
    p_lower = prompt.lower()
    c_lower = cue_text.lower()
    
    if any(k in p_lower for k in ["split", "versus", "vs", "50/50", "contrasting", "comparison"]):
        return "SPLIT_COMPARISON"
    if any(k in p_lower for k in ["macro", "extreme close-up", "close-up", "microscopic", "texture of"]):
        return "OBJECT_MACRO"
    if any(k in p_lower for k in ["cross-section", "cutaway", "molecular", "cellular", "internal", "receptor", "anatomical"]):
        return "MECHANISM_CUTAWAY"
    if any(k in p_lower for k in ["step", "sequence", "phase", "progression", "stage"]):
        return "STEP_ENUMERATION"
    if any(k in p_lower for k in ["diagram", "pathway", "flowchart", "schematic", "vector", "graph"]):
        return "CAUSE_EFFECT_DIAGRAM"
        
    if any(k in c_lower for k in ["tại sao", "vì sao", "nguyên nhân", "bởi vì", "hậu quả", "dẫn đến"]):
        return "CAUSE_EFFECT_DIAGRAM"
    if any(k in c_lower for k in ["so với", "ngược lại", "khác với", "hai", "trái ngược"]):
        return "SPLIT_COMPARISON"
    if any(k in c_lower for k in ["bước", "giai đoạn", "tiếp theo", "thứ nhất", "thứ hai"]):
        return "STEP_ENUMERATION"
        
    return default_type


def generate_explainer_spec_for_channel(slug: str) -> Dict[str, Any]:
    conf = CONFIGS[slug]
    srt_path = f"video/vn_pilot_{slug}_long/vn_pilot_{slug}_long_16x9.srt"
    aligned_path = f"video/vn_pilot_{slug}_long/{slug}_long_aligned_spec.json"
    wav_path = f"video/vn_pilot_{slug}_long/narration_master.wav"
    
    cues = parse_srt(srt_path)
    with open(aligned_path, encoding="utf-8") as f:
        aligned_data = json.load(f)
        
    old_beats = aligned_data.get("beats", [])
    chapters = aligned_data.get("chapters", [])
    
    wav_dur = get_wav_duration(wav_path) if os.path.exists(wav_path) else aligned_data.get("total_duration_sec", cues[-1]["end"])
    total_srt_duration = sum(c["duration"] for c in cues)
    duration_scale = wav_dur / total_srt_duration
    
    # Map old beats to starting cues
    c_idx = 0
    cue_to_old_beat: Dict[int, int] = {}
    for o_idx, ob in enumerate(old_beats):
        o_text = ob["narration"].strip()
        while c_idx < len(cues):
            c_text = cues[c_idx]["text"].strip()
            if o_text.startswith(c_text[:min(25, len(c_text))]):
                cue_to_old_beat[c_idx] = o_idx
                break
            c_idx += 1
            
    assert len(cue_to_old_beat) == len(old_beats), f"Failed to map all old beats in {slug}: {len(cue_to_old_beat)}/{len(old_beats)}"
    
    new_dict = CHANNEL_NEW_PROMPTS[slug]
    expected_new_count = len(cues) - len(old_beats)
    assert len(new_dict) == expected_new_count, f"{slug}: new dict length {len(new_dict)} != {expected_new_count}"

    camera_motions = ["push_in", "pan_right", "pull_back", "pan_left", "hold"]
    
    beats = []
    current_time = 0.0
    type_counts: Dict[str, int] = {}
    reused_count = 0
    
    for i, c in enumerate(cues):
        beat_id = f"B{i:03d}"
        dur = round(c["duration"] * duration_scale, 4)
        cue_text = c["text"]
        
        # Find chapter
        assigned_chap = chapters[-1]
        for chap in chapters:
            if c["start"] >= chap["start_sec"] - 0.05 and c["start"] < chap["end_sec"] - 0.05:
                assigned_chap = chap
                break
                
        chap_idx = assigned_chap["chapter_index"]
        chap_title = assigned_chap["title"]
        
        if i in cue_to_old_beat:
            old_idx = cue_to_old_beat[i]
            reused_count += 1
            raw_prompt = re.sub(r"\b8[kK]\b", "crisp Full HD 1080p", old_beats[old_idx]["prompt"])
            old_core = extract_clean_old_core(raw_prompt)
            explainer_type = determine_explainer_type(old_core, cue_text)
            prompt = clean_and_constrain_prompt(conf["style_prefix"], old_core, conf["tail"])
            prompt = re.sub(r"\b8[kK]\b", "crisp Full HD 1080p", prompt)
            reuse_idx_val = old_idx
        else:
            reuse_idx_val = None
            explainer_type, core = new_dict[i]
            prompt = clean_and_constrain_prompt(conf["style_prefix"], core, conf["tail"])
            prompt = re.sub(r"\b8[kK]\b", "crisp Full HD 1080p", prompt)
            
        type_counts[explainer_type] = type_counts.get(explainer_type, 0) + 1
        cam = camera_motions[i % len(camera_motions)]
        
        beat_obj = {
            "beat_id": beat_id,
            "id": beat_id,
            "cue_idx": i,
            "narration": cue_text,
            "duration": dur,
            "at": round(current_time, 4),
            "chapter_index": chap_idx,
            "chapter_title": chap_title,
            "explainer_type": explainer_type,
            "reuse_old_image_idx": reuse_idx_val,
            "prompt": prompt,
            "camera_motion": cam,
            "transition": "fade",
        }
        beats.append(beat_obj)
        current_time += dur
        
    # Scale correction on last beat so sum exactly matches wav_dur
    total_beats_dur = sum(b["duration"] for b in beats)
    diff = round(wav_dur - total_beats_dur, 4)
    beats[-1]["duration"] = round(beats[-1]["duration"] + diff, 4)
    
    core_explainer_types = ["MECHANISM_CUTAWAY", "OBJECT_MACRO", "SPLIT_COMPARISON", "STEP_ENUMERATION", "CAUSE_EFFECT_DIAGRAM"]
    core_count = sum(type_counts.get(t, 0) for t in core_explainer_types)
    core_ratio = core_count / float(len(beats))
    
    metadata = {
        "channel_id": slug,
        "total_beats": len(beats),
        "new_images_to_generate": len(beats) - reused_count,
        "reused_old_images": reused_count,
        "reuse_ratio": round(reused_count / float(len(beats)), 4),
        "explainer_type_distribution": type_counts,
        "core_explainer_percentage": round(core_ratio * 100.0, 2),
        "total_duration_sec": round(wav_dur, 4),
    }
    
    spec = {
        "channel_id": slug,
        "channel_slug": conf["hyphen_slug"],
        "job_id": f"{conf['hyphen_slug']}_long_{len(beats)}_explainer",
        "parent_long_id": f"{conf['hyphen_slug']}_long_{len(beats)}",
        "format_profile": "long_16x9_high_density",
        "youtube_title": aligned_data.get("youtube_title", ""),
        "total_duration_sec": round(wav_dur, 4),
        "thumbnail_spec": aligned_data.get("thumbnail_spec", {}),
        "cta_plan": aligned_data.get("cta_plan", {}),
        "chapters": chapters,
        "metadata": metadata,
        "beats": beats,
        "voice": aligned_data.get("voice", f"VietNarrator_{slug}"),
        "voice_profile": aligned_data.get("voice_profile", f"sys/assets/voices/ch_{slug}/profile.json"),
    }
    
    return spec


def validate_explainer_spec(spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors = []
    slug = spec["channel_id"]
    beats = spec.get("beats", [])
    expected_cues = CONFIGS[slug]["total_cues"]
    
    if len(beats) != expected_cues:
        errors.append(f"Beat count {len(beats)} != expected {expected_cues}")
        
    core_types = {"MECHANISM_CUTAWAY", "OBJECT_MACRO", "SPLIT_COMPARISON", "STEP_ENUMERATION", "CAUSE_EFFECT_DIAGRAM", "SITUATIONAL_ACTION"}
    core_count = 0
    reused = 0
    
    # 1. Check prompt uniqueness across all beats
    all_prompts = [b["prompt"].strip() for b in beats]
    if len(set(all_prompts)) != len(beats):
        errors.append(f"Duplicate prompts found: {len(set(all_prompts))}/{len(beats)}")
        
    # 2. Check new beats core subjects uniqueness (Orchestrator Gate 1 rule)
    new_beats = [b for b in beats if b.get("reuse_old_image_idx") is None]
    cores = [b["prompt"].split(",")[1].strip()[:60].lower() for b in new_beats]
    if len(set(cores)) != len(cores):
        errors.append(f"Duplicate core subjects in new beats: {len(set(cores))}/{len(cores)}")
        
    for i, b in enumerate(beats):
        w_cnt = len(b["prompt"].split())
        if w_cnt < 35 or w_cnt > 65:
            errors.append(f"Beat {b['beat_id']} prompt word count {w_cnt} not in [35, 65]: {b['prompt']}")
        if not b["prompt"].endswith(", zero text overlay, no watermarks"):
            errors.append(f"Beat {b['beat_id']} prompt does not end with strict suffix: {b['prompt']}")
        for fp in FORBIDDEN_PHRASES:
            if fp in b["prompt"].lower():
                errors.append(f"Beat {b['beat_id']} prompt contains forbidden phrase '{fp}'")
        if re.search(r"\b8[kK]\b", b["prompt"]):
            errors.append(f"Beat {b['beat_id']} prompt contains forbidden 8K keyword: {b['prompt']}")
        if b["explainer_type"] not in core_types:
            errors.append(f"Beat {b['beat_id']} unknown explainer_type {b['explainer_type']}")
        if b["explainer_type"] != "SITUATIONAL_ACTION":
            core_count += 1
        if b["reuse_old_image_idx"] is not None:
            reused += 1
            
    core_ratio = core_count / float(len(beats)) if beats else 0
    if core_ratio < 0.85:
        errors.append(f"Core explainer ratio {core_ratio*100:.1f}% is below mandatory 85%")
        
    return len(errors) == 0, errors


def main():
    print("="*80)
    print("STARTING GROUP A EXPLAINER SPEC GENERATOR FOR 5 CHANNELS")
    print("="*80)
    
    results = {}
    
    for slug in CHANNELS:
        print(f"\nProcessing {slug}...")
        spec = generate_explainer_spec_for_channel(slug)
        is_valid, errors = validate_explainer_spec(spec)
        
        out_path = f"video/vn_pilot_{slug}_long/{slug}_long_explainer_spec.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False, indent=2)
            
        print(f"Saved {out_path} ({len(spec['beats'])} beats)")
        if not is_valid:
            print(f"VALIDATION ERRORS ({len(errors)}):")
            for err in errors[:10]:
                print(f"  - {err}")
            raise ValueError(f"Validation failed for {slug}")
        else:
            print(f"Validation PASSED: {len(spec['beats'])} beats, 100% unique, {spec['metadata']['reused_old_images']} reused, {spec['metadata']['new_images_to_generate']} new, {spec['metadata']['core_explainer_percentage']}% core explainer!")
            
        results[slug] = spec
        
    print("\n" + "="*80)
    print("ALL 5 EXPLAINER SPECS GENERATED AND VALIDATED SUCCESSFULLY!")
    print("="*80)


if __name__ == "__main__":
    main()
