#!/usr/bin/env python3
"""Script Diversity Linter for Video Pilot.

Ensures scripts possess high lexical diversity, adhere to strict forward chronology
(zero historical backtracking), avoid clichéd transitions ("Nhưng rồi...", "Bước sang...",
"Hãy cùng bước vào..."), and do not plagiarize or copy sentence formulas from prior productions.

Validation Checks:
  1. check_intra_video_repetitions: Detects repeated 3-4 gram phrases within close proximity.
  2. check_historical_backtracking: Enforces Strict Forward Chronology per chapter.
  3. check_formulaic_transitions: Flags clichéd mechanical transition templates.
  4. check_corpus_cross_similarity: Prevents opening formula mirroring across projects in sys/exports/.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

BANNED_FORMULAIC_TRANSITIONS = [
    r"^\s*nhưng rồi\b",
    r"^\s*thế nhưng rồi\b",
    r"^\s*bước sang\b",
    r"^\s*hãy cùng bước vào\b",
    r"^\s*hãy cùng khám phá\b",
    r"^\s*nhưng câu chuyện(?: áp lực)? chưa dừng lại ở đó\b",
    r"^\s*hãy thử ngẫm nghĩ\b",
    r"^\s*(?:xin\s+)?chào\b",
    r"^\s*chào\s+mừng\b",
    r"\bhôm\s+nay\s+chúng\s+ta\b",
    r"\btrong\s+video\s+này\b",
    r"^\s*hãy\s+(?:nghĩ\s+về|hình\s+dung|tưởng\s+tượng)\b",
    r"^\s*giờ\s+đây\s*,?\s*hãy\b",
    r"\bđể\s+tìm\s+câu\s+trả\s+lời\b",
]

BANNED_ACADEMIC_NAMEDROPS = [
    r"\bet\s+al\.",
    r"\bdoi\s*:",
    r"\(\d{4}\)",
    r"\b(?:giáo\s+sư|tiến\s+sĩ)\s+(?!quốc\s+tế\b|đại\s+học\b|hội\s+đồng\b|hướng\s+dẫn\b|phản\s+biện\b|đầu\s+ngành\b)[a-zA-ZÀ-ỹ]+\s+[a-zA-ZÀ-ỹ]+",
    r"\bnghiên\s+cứu\s+năm\s+(?:\d+|một\s+nghìn|hai\s+nghìn)\s+của\b",
]

# Topic-agnostic default: custom_chronology_rules from brief.json defines chapter boundaries.
HISTORICAL_BACKTRACK_RULES: Dict[int, List[str]] = {}

MICRO_ACTION_FILLER_RE = re.compile(
    r"^\s*(?:bạn\s+|rồi\s+)?(?:cầm\s+cây\s+bút|đặt\s+xuống\s+tờ\s+giấy|gấp\s+cuốn\s+sách|mở\s+sách\s+ra|đặt\s+bút\s+xuống|lật\s+trang\s+giấy)\b",
    re.IGNORECASE,
)

STOP_WORDS = {
    "và", "của", "là", "có", "được", "trong", "để", "cho", "với", "không",
    "khi", "này", "đó", "những", "các", "một", "bạn", "ta", "thì", "mà",
    "ra", "vào", "lại", "về", "như", "đã", "sẽ", "đang", "từ", "ở", "lên",
}


def clean_sentence(text: str) -> str:
    cleaned = re.sub(r"\[pause:[^\]]+\]", " ", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"[^\w\s\d]", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip().lower()


def get_words(text: str) -> List[str]:
    return [w for w in clean_sentence(text).split() if w]


def get_ngrams(words: List[str], n: int) -> List[Tuple[str, ...]]:
    return [tuple(words[i:i + n]) for i in range(len(words) - n + 1)]


def is_meaningful_ngram(ngram: Tuple[str, ...]) -> bool:
    meaningful = [w for w in ngram if w not in STOP_WORDS]
    return len(meaningful) >= 2


def check_formulaic_transitions(scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    violations = []
    for sc in scenes:
        sc_id = sc.get("scene_id") or sc.get("id") or "UNKNOWN"
        narration = sc.get("narration") or sc.get("text") or ""
        # Check start of sentences and academic name-drop bloat
        sents = re.split(r"[.!?…]+", narration)
        for s_idx, s in enumerate(sents):
            s_clean = s.strip().lower()
            if not s_clean:
                continue
            for pattern in BANNED_FORMULAIC_TRANSITIONS:
                if re.search(pattern, s_clean):
                    violations.append({
                        "type": "FORMULAIC_TRANSITION",
                        "scene_id": sc_id,
                        "sentence_index": s_idx + 1,
                        "pattern": pattern,
                        "snippet": s.strip(),
                    })
                    break
            for pattern in BANNED_ACADEMIC_NAMEDROPS:
                if re.search(pattern, s_clean, flags=re.IGNORECASE):
                    violations.append({
                        "type": "ACADEMIC_NAMEDROP_BLOAT",
                        "scene_id": sc_id,
                        "sentence_index": s_idx + 1,
                        "pattern": pattern,
                        "snippet": s.strip(),
                    })
                    break
    return violations


def check_micro_action_filler(scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect scenes with >= 3 ultra-short physical micro-instruction commands."""
    violations: List[Dict[str, Any]] = []
    for sc in scenes:
        sc_id = sc.get("scene_id") or sc.get("id") or "UNKNOWN"
        narration = sc.get("narration") or sc.get("text") or ""
        sents = [s.strip() for s in re.split(r"[.!?…]+", narration) if s.strip()]
        matches = [
            s for s in sents
            if len(get_words(s)) <= 6 and MICRO_ACTION_FILLER_RE.search(s)
        ]
        if len(matches) >= 3:
            violations.append({
                "type": "MICRO_ACTION_FILLER_BABBLE",
                "scene_id": sc_id,
                "count": len(matches),
                "snippet": " | ".join(matches[:3]),
            })
    return violations


def compute_sentence_rhythm_metrics(scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculates human storytelling cadence variation (sentence length stddev & short punchy sentences)."""
    import math
    lengths: List[int] = []
    short_punchy_count = 0
    for sc in scenes:
        narration = sc.get("narration") or sc.get("text") or ""
        sents = [s.strip() for s in re.split(r"[.!?…]+", narration) if s.strip()]
        for s in sents:
            words = get_words(s)
            if not words:
                continue
            wc = len(words)
            lengths.append(wc)
            if 2 <= wc <= 8:
                short_punchy_count += 1
    if not lengths:
        return {"sentence_count": 0, "mean_syllables": 0.0, "stddev_syllables": 0.0, "short_punchy_count": 0}
    mean = sum(lengths) / len(lengths)
    variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
    return {
        "sentence_count": len(lengths),
        "mean_syllables": round(mean, 2),
        "stddev_syllables": round(math.sqrt(variance), 2),
        "short_punchy_count": short_punchy_count,
    }


def check_sentence_rhythm_variance(
    scenes: List[Dict[str, Any]],
    min_stddev_syllables: float = 1.8,
) -> List[Dict[str, Any]]:
    """Flags chapters or scripts where every sentence has nearly identical robotic length."""
    metrics = compute_sentence_rhythm_metrics(scenes)
    violations: List[Dict[str, Any]] = []
    if metrics["sentence_count"] >= 8 and metrics["stddev_syllables"] < min_stddev_syllables:
        violations.append({
            "type": "ROBOTIC_SENTENCE_CADENCE",
            "scene_id": "GLOBAL",
            "stddev_syllables": metrics["stddev_syllables"],
            "min_required_stddev": min_stddev_syllables,
            "snippet": f"Độ lệch chuẩn độ dài câu quá thấp ({metrics['stddev_syllables']} âm tiết); cần xen kẽ câu ngắn (3-7 chữ) và câu phân tích dài.",
        })
    return violations


def check_historical_backtracking(
    scenes: List[Dict[str, Any]],
    topic_title: str = "",
    custom_chronology_rules: Dict[int, List[str]] | None = None,
) -> List[Dict[str, Any]]:
    violations = []
    active_rules = (
        {int(k): v for k, v in custom_chronology_rules.items()}
        if custom_chronology_rules is not None
        else HISTORICAL_BACKTRACK_RULES
    )
    if not active_rules:
        return violations

    for sc in scenes:
        sc_id = sc.get("scene_id") or sc.get("id") or "UNKNOWN"
        ch_num = sc.get("chapter")
        if not ch_num:
            m = re.match(r"SC0?(\d+)", sc_id, re.IGNORECASE)
            if m:
                idx = int(m.group(1))
                ch_num = (idx - 1) // 6 + 1

        if not ch_num or ch_num not in active_rules:
            continue
        forbidden_words = active_rules[ch_num]
        narration = (sc.get("narration") or sc.get("text") or "").lower()
        for kw in forbidden_words:
            pattern = r"(?<!\w)" + re.escape(kw) + r"(?!\w)"
            if re.search(pattern, narration):
                violations.append({
                    "type": "HISTORICAL_BACKTRACKING",
                    "scene_id": sc_id,
                    "chapter": ch_num,
                    "keyword": kw,
                    "snippet": narration[:120],
                })
    return violations


def check_intra_video_repetitions(
    scenes: List[Dict[str, Any]],
    ngram_size: int = 4,
    window_scenes: int = 4,
    claim_facts: Set[str] | None = None,
) -> List[Dict[str, Any]]:
    violations = []
    claims_set = claim_facts or set()

    scene_ngrams: List[Tuple[str, int, List[Tuple[str, ...]]]] = []
    for sc_idx, sc in enumerate(scenes):
        sc_id = sc.get("scene_id") or sc.get("id") or f"SC{sc_idx+1:02d}"
        ch_num = sc.get("chapter", 0)
        words = get_words(sc.get("narration") or sc.get("text") or "")
        ngrams = [ng for ng in get_ngrams(words, ngram_size) if is_meaningful_ngram(ng)]
        scene_ngrams.append((sc_id, ch_num, ngrams))

    for i in range(len(scene_ngrams)):
        sc_i_id, ch_i, ngrams_i = scene_ngrams[i]
        # Check within window_scenes
        end_win = min(len(scene_ngrams), i + window_scenes + 1)
        for j in range(i + 1, end_win):
            sc_j_id, ch_j, ngrams_j = scene_ngrams[j]
            overlap = set(ngrams_i).intersection(set(ngrams_j))
            for ng in overlap:
                phrase = " ".join(ng)
                # Ignore if part of an official academic claim quote
                if any(phrase in c.lower() for c in claims_set):
                    continue
                violations.append({
                    "type": "INTRA_VIDEO_REPETITION",
                    "scenes": (sc_i_id, sc_j_id),
                    "phrase": phrase,
                })
    return violations


def check_corpus_cross_similarity(
    scenes: List[Dict[str, Any]],
    corpus_dir: Path,
) -> List[Dict[str, Any]]:
    violations = []
    if not scenes or not corpus_dir.is_dir():
        return violations

    first_sc = scenes[0]
    sc_narration = clean_sentence(first_sc.get("narration") or first_sc.get("text") or "")
    first_words = sc_narration.split()[:15]
    if not first_words:
        return violations

    # Check against known past manifests in corpus_dir
    for sub in corpus_dir.iterdir():
        if sub.name in ("study_motivation_bundle", "attention_architect_bundle"):
            continue
        manifest_p = sub / "manifest" / "phonetic_normalized_script_8ch.json"
        if not manifest_p.is_file():
            continue
        try:
            corpus_data = json.loads(manifest_p.read_text(encoding="utf-8"))
            past_texts: List[str] = []
            if isinstance(corpus_data, dict):
                if "chapters" in corpus_data and isinstance(corpus_data["chapters"], list):
                    for ch in corpus_data["chapters"]:
                        for s in ch.get("sentences", []):
                            past_texts.append(s.get("original_text", ""))
                elif "ch1" in corpus_data:
                    for s in corpus_data["ch1"]:
                        past_texts.append(s.get("original_text", ""))

            if not past_texts:
                continue

            # Compare first 3 sentences of past video
            past_opening = clean_sentence(" ".join(past_texts[:3])).split()[:15]
            if not past_opening:
                continue

            # Calculate word overlap ratio on opening
            overlap = set(first_words).intersection(set(past_opening))
            content_overlap = [w for w in overlap if w not in {"và", "của", "là", "có", "được", "trong", "để", "cho", "với", "không"}]
            if len(content_overlap) >= 3:
                violations.append({
                    "type": "CORPUS_CROSS_SIMILARITY",
                    "bundle": sub.name,
                    "overlap_words": content_overlap,
                    "target_opening": " ".join(first_words[:8]),
                    "corpus_opening": " ".join(past_opening[:8]),
                })

            # Check structural template duplication: e.g. "[Time] + Bạn ngồi [state] trước [object]"
            time_pattern = r"^\s*(?:\d+|tám|chín|mười|mười một|mười hai)\s+giờ\b"
            state_pattern = r"\bbạn\s+ngồi\s+(?:bất động|chết lặng|im lìm|bần thần|thẫn thờ)\b"
            target_raw = (first_sc.get("narration") or first_sc.get("text") or "").lower()
            past_raw = " ".join(past_texts[:2]).lower()
            if (re.search(time_pattern, target_raw) and re.search(state_pattern, target_raw) and
                re.search(time_pattern, past_raw) and re.search(state_pattern, past_raw)):
                violations.append({
                    "type": "CORPUS_CROSS_SIMILARITY",
                    "bundle": sub.name,
                    "overlap_words": ["time_state_template_clone"],
                    "target_opening": " ".join(first_words[:8]),
                    "corpus_opening": " ".join(past_opening[:8]),
                })
        except Exception:
            continue

    return violations


def check_visual_prompt_cliches(
    scenes: List[Dict[str, Any]],
    characters: List[Dict[str, Any]] | None = None,
    style: str | None = None,
) -> List[Dict[str, Any]]:
    """Flags any visual description fields that contain banned visual clichés."""
    from flow_prompts import find_visual_cliche

    violations: List[Dict[str, Any]] = []
    if style and isinstance(style, str):
        cliche = find_visual_cliche(style)
        if cliche:
            violations.append({
                "type": "FLOW_CLICHE_FORBIDDEN",
                "scene_id": "GLOBAL",
                "field": "style",
                "cliche": cliche,
                "snippet": style[:120],
            })
    for ch in characters or []:
        ch_id = ch.get("id") if isinstance(ch, dict) else getattr(ch, "id", "CH")
        for field in ("appearance", "outfit", "name"):
            val = ch.get(field) if isinstance(ch, dict) else getattr(ch, field, None)
            if val and isinstance(val, str):
                cliche = find_visual_cliche(val)
                if cliche:
                    violations.append({
                        "type": "FLOW_CLICHE_FORBIDDEN",
                        "scene_id": "GLOBAL",
                        "image_id": ch_id,
                        "field": f"character.{field}",
                        "cliche": cliche,
                        "snippet": val[:120],
                    })
    for sc in scenes:
        sc_id = sc.get("scene_id") or sc.get("id") or "UNKNOWN"
        for field in ("setting", "prompt", "action", "description", "bg_description"):
            val = sc.get(field)
            if val and isinstance(val, str):
                cliche = find_visual_cliche(val)
                if cliche:
                    violations.append({
                        "type": "FLOW_CLICHE_FORBIDDEN",
                        "scene_id": sc_id,
                        "field": field,
                        "cliche": cliche,
                        "snippet": val[:120],
                    })
        for im in sc.get("images", []):
            im_id = im.get("id") or "IMAGE"
            for field in ("description", "preserve", "change"):
                val = im.get(field)
                if val and isinstance(val, str):
                    cliche = find_visual_cliche(val)
                    if cliche:
                        violations.append({
                            "type": "FLOW_CLICHE_FORBIDDEN",
                            "scene_id": sc_id,
                            "image_id": im_id,
                            "field": field,
                            "cliche": cliche,
                            "snippet": val[:120],
                        })
            for vt in im.get("visible_text", []):
                if isinstance(vt, str):
                    cliche = find_visual_cliche(vt)
                    if cliche:
                        violations.append({
                            "type": "FLOW_CLICHE_FORBIDDEN",
                            "scene_id": sc_id,
                            "image_id": im_id,
                            "field": "visible_text",
                            "cliche": cliche,
                            "snippet": vt[:120],
                        })
                elif isinstance(vt, dict):
                    for subf in ("text", "placement", "object"):
                        subval = vt.get(subf)
                        if subval and isinstance(subval, str):
                            cliche = find_visual_cliche(subval)
                            if cliche:
                                violations.append({
                                    "type": "FLOW_CLICHE_FORBIDDEN",
                                    "scene_id": sc_id,
                                    "image_id": im_id,
                                    "field": f"visible_text.{subf}",
                                    "cliche": cliche,
                                    "snippet": subval[:120],
                                })
        for bt in sc.get("visual_beats", []):
            bt_id = getattr(bt, "image_id", None) or (bt.get("image_id") if isinstance(bt, dict) else "BEAT")
            for field in ("description", "preserve", "change"):
                val = getattr(bt, field, None) if not isinstance(bt, dict) else bt.get(field)
                if val and isinstance(val, str):
                    cliche = find_visual_cliche(val)
                    if cliche:
                        violations.append({
                            "type": "FLOW_CLICHE_FORBIDDEN",
                            "scene_id": sc_id,
                            "image_id": bt_id,
                            "field": field,
                            "cliche": cliche,
                            "snippet": val[:120],
                        })
            vts = getattr(bt, "visible_text", None) if not isinstance(bt, dict) else bt.get("visible_text")
            for vt in vts or []:
                if isinstance(vt, str):
                    cliche = find_visual_cliche(vt)
                    if cliche:
                        violations.append({
                            "type": "FLOW_CLICHE_FORBIDDEN",
                            "scene_id": sc_id,
                            "image_id": bt_id,
                            "field": "visible_text",
                            "cliche": cliche,
                            "snippet": vt[:120],
                        })
                elif isinstance(vt, dict):
                    for subf in ("text", "placement", "object"):
                        subval = vt.get(subf)
                        if subval and isinstance(subval, str):
                            cliche = find_visual_cliche(subval)
                            if cliche:
                                violations.append({
                                    "type": "FLOW_CLICHE_FORBIDDEN",
                                    "scene_id": sc_id,
                                    "image_id": bt_id,
                                    "field": f"visible_text.{subf}",
                                    "cliche": cliche,
                                    "snippet": subval[:120],
                                })
    return violations


def lint_script(
    scenes: List[Dict[str, Any]],
    corpus_dir: Path | None = None,
    claim_facts: Set[str] | None = None,
    topic_title: str = "",
    custom_chronology_rules: Dict[int, List[str]] | None = None,
    enforce_rhythm_variance: bool = False,
    characters: List[Dict[str, Any]] | None = None,
    style: str | None = None,
) -> Dict[str, Any]:
    all_violations: List[Dict[str, Any]] = []

    # 0. Visual prompt clichés
    all_violations.extend(check_visual_prompt_cliches(scenes, characters=characters, style=style))

    from scripts.visual_quality import (
        check_instructional_manual_loop,
        check_scene_narrative_progression,
        check_visual_setting_diversity,
    )
    has_visual_fields = any(sc.get("setting") or sc.get("images") for sc in scenes)
    if has_visual_fields:
        all_violations.extend(check_visual_setting_diversity(scenes))
        all_violations.extend(check_scene_narrative_progression(scenes))
    all_violations.extend(check_instructional_manual_loop(scenes))

    # 1. Formulaic transitions & micro-action filler babble
    ft_violations = check_formulaic_transitions(scenes)
    all_violations.extend(ft_violations)
    all_violations.extend(check_micro_action_filler(scenes))

    # 2. Historical backtracking (topic-aware or custom brief rules)
    hb_violations = check_historical_backtracking(
        scenes,
        topic_title=topic_title,
        custom_chronology_rules=custom_chronology_rules,
    )
    all_violations.extend(hb_violations)

    # 3. Intra-video repetitions
    ir_violations = check_intra_video_repetitions(scenes, claim_facts=claim_facts)
    all_violations.extend(ir_violations)

    # 4. Corpus cross similarity
    if corpus_dir and corpus_dir.is_dir():
        cs_violations = check_corpus_cross_similarity(scenes, corpus_dir)
        all_violations.extend(cs_violations)

    # 5. Human sentence rhythm metrics & optional hard enforcement
    rhythm_metrics = compute_sentence_rhythm_metrics(scenes)
    if enforce_rhythm_variance:
        all_violations.extend(check_sentence_rhythm_variance(scenes))

    return {
        "status": "PASS" if not all_violations else "FAIL",
        "total_violations": len(all_violations),
        "violations": all_violations,
        "rhythm_metrics": rhythm_metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint video script for lexical and narrative diversity.")
    parser.add_argument("script_file", help="Path to content.json, script.json, or bundle manifest")
    parser.add_argument("--corpus-dir", default="sys/exports", help="Corpus directory to check against")
    args = parser.parse_args()

    target_path = Path(args.script_file)
    if not target_path.is_file():
        print(f"ERROR: File {target_path} not found.", file=sys.stderr)
        sys.exit(2)

    data = json.loads(target_path.read_text(encoding="utf-8"))
    scenes: List[Dict[str, Any]] = []
    claim_facts: Set[str] = set()
    topic_title: str = data.get("topic", "")

    if isinstance(data, dict):
        if "scenes" in data and isinstance(data["scenes"], list):
            scenes = data["scenes"]
        elif "chapters" in data and isinstance(data["chapters"], list):
            for ch in data["chapters"]:
                for s in ch.get("sentences", []):
                    scenes.append({
                        "scene_id": s.get("scene_id"),
                        "chapter": ch.get("chapter"),
                        "narration": s.get("original_text"),
                    })
        elif "tracks" in data:
            for sc in data.get("tracks", {}).get("vi", {}).get("scenesByAspect", {}).get("16:9", []):
                scenes.append(sc)

        if "sources" in data:
            for src in data["sources"]:
                for f in src.get("facts", []):
                    claim_facts.add(clean_sentence(f))
        if "claims" in data:
            for cl in data["claims"]:
                if isinstance(cl, dict) and "fact" in cl:
                    claim_facts.add(clean_sentence(cl["fact"]))
                elif isinstance(cl, dict) and "quote" in cl:
                    claim_facts.add(clean_sentence(cl["quote"]))

    # Also check sibling brief.json if present
    sibling_brief = target_path.parent / "brief.json"
    if sibling_brief.is_file():
        try:
            b_data = json.loads(sibling_brief.read_text(encoding="utf-8"))
            if not topic_title:
                topic_title = b_data.get("topic", "")
            for src in b_data.get("sources", []):
                for f in src.get("facts", []):
                    claim_facts.add(clean_sentence(f))
        except Exception:
            pass

    corpus_dir = Path(args.corpus_dir)
    result = lint_script(
        scenes,
        corpus_dir=corpus_dir,
        claim_facts=claim_facts,
        topic_title=topic_title,
        characters=data.get("characters") if isinstance(data, dict) else None,
        style=data.get("style") if isinstance(data, dict) else None,
    )

    print("=" * 80)
    print("                 SCRIPT DIVERSITY & ZERO-BACKTRACKING LINTER")
    print("=" * 80)
    print(f"Target: {target_path}")
    print(f"Total scenes analyzed: {len(scenes)}")
    print(f"Status: {result['status']} (Violations: {result['total_violations']})")
    print("-" * 80)

    if result["violations"]:
        for idx, v in enumerate(result["violations"], 1):
            v_type = v["type"]
            if v_type == "HISTORICAL_BACKTRACKING":
                print(f"[{idx}] {v_type} in {v['scene_id']} (Ch{v['chapter']}):")
                print(f"    Forbidden keyword found: '{v['keyword']}'")
                print(f"    Snippet: {v['snippet']}")
            elif v_type in ("FORMULAIC_TRANSITION", "ACADEMIC_NAMEDROP_BLOAT"):
                print(f"[{idx}] {v_type} in {v['scene_id']} cue #{v['sentence_index']}:")
                print(f"    Pattern: {v['pattern']}")
                print(f"    Snippet: {v['snippet']}")
            elif v_type == "INTRA_VIDEO_REPETITION":
                print(f"[{idx}] {v_type} between {v['scenes'][0]} and {v['scenes'][1]}:")
                print(f"    Repeated phrase: '{v['phrase']}'")
            elif v_type == "CORPUS_CROSS_SIMILARITY":
                print(f"[{idx}] {v_type} with bundle '{v['bundle']}':")
                print(f"    Overlap words: {v['overlap_words']}")
                print(f"    Target opening: {v['target_opening']}")
                print(f"    Corpus opening: {v['corpus_opening']}")
            elif v_type == "FLOW_CLICHE_FORBIDDEN":
                target_desc = f"{v['scene_id']}" + (f" ({v['image_id']})" if v.get('image_id') else "")
                print(f"[{idx}] {v_type} in {target_desc} field '{v.get('field', 'visual')}':")
                print(f"    Forbidden cliché: '{v.get('cliche')}'")
                print(f"    Snippet: {v.get('snippet')}")
            else:
                print(f"[{idx}] {v_type}: {v}")
        print("=" * 80)
        sys.exit(1)
    else:
        print("All diversity checks passed! Zero formulaic transitions, zero backtracking, zero duplicate phrasing.")
        print("=" * 80)
        sys.exit(0)


if __name__ == "__main__":
    main()
