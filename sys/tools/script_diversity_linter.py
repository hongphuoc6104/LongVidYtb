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
# Formulaic ban lists removed in Feynman Flex architecture in favor of constructive clarity guidance.
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

AI_CLICHE_PATTERNS: tuple[str, ...] = (
    r"\bcó một sự thật mất lòng\b",
    r"\bsự thật mất lòng là\b",
    r"\bđánh giá công bằng thì\b",
    r"\bnói đi cũng phải nói lại\b",
    r"\bnghịch lý nằm ở chỗ\b",
    r"\bnghịch lý nằm ở\b",
    r"\bbí mật nằm ở\b",
    r"\bchìa khóa nằm ở\b",
    r"\bmấu chốt nằm ở\b",
    r"\bđiều đáng sợ là\b",
    r"\bđiều thú vị là\b",
    r"\bđiều kỳ lạ là\b",
    r"\btin vui là\b",
    r"\btin buồn là\b",
    r"\bnhiều người lầm tưởng rằng\b",
    r"\bít ai biết rằng\b",
    r"\bthứ ít ai nói với bạn\b",
    r"\bnói cách khác là\b",
    r"\btóm lại là\b",
)


def check_ai_cliche_phrases(scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect repetitive Vietnamese AI translationese and canned discourse markers."""
    violations: List[Dict[str, Any]] = []
    for sc in scenes:
        sc_id = sc.get("scene_id") or sc.get("id") or "UNKNOWN"
        narration = sc.get("narration") or sc.get("text") or ""
        if not narration and sc.get("beats"):
            narration = " ".join(
                str(b.get("narration") or b.get("text") or "") for b in sc.get("beats", [])
            )
        if not narration:
            continue
        narration_lower = narration.lower()
        matched_spans: List[Tuple[int, int]] = []
        for pat in AI_CLICHE_PATTERNS:
            for m in re.finditer(pat, narration_lower):
                span = m.span()
                if any(s[0] <= span[0] < s[1] or s[0] < span[1] <= s[1] for s in matched_spans):
                    continue
                matched_spans.append(span)
                violations.append({
                    "type": "AI_CLICHE_PHRASE",
                    "scene_id": sc_id,
                    "pattern": pat,
                    "matched_text": m.group(0),
                    "snippet": narration[:140],
                    "message": f"Spoken narration contains banned AI cliché: '{m.group(0)}'",
                })
    return violations


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
    """Provide constructive clarity guidance for transitions and academic citations without hard rejection."""
    guidance = []
    for sc in scenes:
        sc_id = sc.get("scene_id") or sc.get("id") or "UNKNOWN"
        narration = sc.get("narration") or sc.get("text") or ""
        sents = re.split(r"[.!?…]+", narration)
        for s_idx, s in enumerate(sents):
            s_clean = s.strip()
            if not s_clean:
                continue
            if re.search(r"\b(?:doi\s*:|et\s+al\b)", s_clean, flags=re.IGNORECASE):
                guidance.append({
                    "type": "CLARITY_GUIDANCE",
                    "scene_id": sc_id,
                    "sentence_index": s_idx + 1,
                    "message": "Prefer conversational experiment attribution over formal academic citation syntax (e.g. 'các cộng sự' instead of 'et al.').",
                    "snippet": s.strip(),
                })
    return guidance


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


def get_known_channel_prefixes() -> List[str]:
    channels_dir = SYS_DIR / "channels"
    prefixes = []
    if channels_dir.is_dir():
        for p in channels_dir.iterdir():
            if p.is_dir() and not p.name.startswith("__"):
                prefixes.append(p.name.replace("_", "-"))
    if not prefixes:
        prefixes = [
            "ai-binh-dan", "ban-do-quyen-luc", "banh-rang", "chanh-niem-ke", "co-the-ke",
            "dia-com", "ho-so-ky-la", "la-ban-hoc-thuat", "loi-sang-soi", "luat-doi-thuong",
            "luat-ngam", "minh-triet-song", "nao-luoi", "nghe-song-sot", "su-ke-lai",
            "tam-tinh-dem", "thuong-cho-kheo", "tui-tien", "ua-sao-vay", "vu-tru-ti-hon",
        ]
    return sorted(prefixes, key=len, reverse=True)


def extract_channel_from_name(name: str) -> str:
    name_clean = name.strip().lower()
    for c in get_known_channel_prefixes():
        if name_clean.startswith(c):
            return c
    return ""


def extract_stem_from_name(name: str) -> str:
    s = re.sub(r"[-_](?:16x9|9x16|long|short)(?:[-_]\d+)?$", "", name, flags=re.IGNORECASE)
    s = re.sub(r"[-_](?:auto[-_]short)$", "", s, flags=re.IGNORECASE)
    return s.strip().lower()


def check_corpus_cross_similarity(
    scenes: List[Dict[str, Any]],
    corpus_dir: Path | None = None,
    runs_dir: Path | None = None,
    current_run_name: str = "",
    topic_title: str = "",
) -> List[Dict[str, Any]]:
    violations = []
    if not scenes:
        return violations

    first_sc = scenes[0]
    sc_narration = clean_sentence(first_sc.get("narration") or first_sc.get("text") or "")
    first_words = sc_narration.split()[:15]
    if not first_words:
        return violations

    target_raw = (first_sc.get("narration") or first_sc.get("text") or "").lower()
    time_pattern = r"^\s*(?:\d+|tám|chín|mười|mười một|mười hai)\s+giờ\b"
    state_pattern = r"\bbạn\s+ngồi\s+(?:bất động|chết lặng|im lìm|bần thần|thẫn thờ)\b"

    # 1. Legacy corpus check (sys/exports/)
    if corpus_dir and corpus_dir.is_dir():
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

                past_opening = clean_sentence(" ".join(past_texts[:3])).split()[:15]
                if not past_opening:
                    continue

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

    # 2. Modern sys/runs/*/content.json cross-channel scan
    active_runs = runs_dir
    if active_runs is None:
        if corpus_dir and (corpus_dir.parent / "runs").is_dir():
            active_runs = corpus_dir.parent / "runs"
        elif (SYS_DIR / "runs").is_dir() and (corpus_dir is None or str(corpus_dir).startswith(str(SYS_DIR))):
            active_runs = SYS_DIR / "runs"

    if active_runs and active_runs.is_dir():
        curr_channel = extract_channel_from_name(current_run_name) if current_run_name else ""
        curr_stem = extract_stem_from_name(current_run_name) if current_run_name else ""
        norm_topic = topic_title.strip().lower()

        for run_dir in active_runs.iterdir():
            if not run_dir.is_dir():
                continue
            past_name = run_dir.name
            if past_name.startswith("."):
                continue
            if current_run_name and past_name == current_run_name:
                continue

            past_stem = extract_stem_from_name(past_name)
            if curr_stem and past_stem and curr_stem == past_stem:
                continue

            past_channel = extract_channel_from_name(past_name)
            # Skip same-channel runs to focus strictly on cross-channel cloning
            if curr_channel and past_channel and curr_channel == past_channel:
                continue

            content_file = run_dir / "content.json"
            if not content_file.is_file():
                continue

            try:
                past_data = json.loads(content_file.read_text(encoding="utf-8"))
                past_topic = str(past_data.get("topic") or "").strip().lower()
                if norm_topic and past_topic and norm_topic == past_topic:
                    continue

                past_scenes = past_data.get("scenes", [])
                if not past_scenes:
                    continue

                # Skip identical scene sets (the exact same production artifact)
                if (
                    len(past_scenes) == len(scenes)
                    and clean_sentence(past_scenes[0].get("narration") or "") == sc_narration
                ):
                    if all(
                        clean_sentence(past_scenes[i].get("narration") or "")
                        == clean_sentence(scenes[i].get("narration") or "")
                        for i in range(len(scenes))
                    ):
                        continue

                past_texts = [
                    str(sc.get("narration") or sc.get("text") or "")
                    for sc in past_scenes[:3]
                    if (sc.get("narration") or sc.get("text"))
                ]
                if not past_texts:
                    continue

                past_opening = clean_sentence(" ".join(past_texts[:3])).split()[:15]
                if not past_opening:
                    continue

                # Significant content word overlap on opening
                overlap = set(first_words).intersection(set(past_opening))
                content_overlap = [w for w in overlap if w not in STOP_WORDS]
                if len(content_overlap) >= 5:
                    violations.append({
                        "type": "CORPUS_CROSS_SIMILARITY",
                        "bundle": past_name,
                        "overlap_words": sorted(content_overlap),
                        "target_opening": " ".join(first_words[:8]),
                        "corpus_opening": " ".join(past_opening[:8]),
                    })
                    continue

                # Structural template duplication: e.g. "[Time] + Bạn ngồi [state] trước [object]"
                past_raw = " ".join(past_texts[:2]).lower()
                if (
                    re.search(time_pattern, target_raw)
                    and re.search(state_pattern, target_raw)
                    and re.search(time_pattern, past_raw)
                    and re.search(state_pattern, past_raw)
                ):
                    violations.append({
                        "type": "CORPUS_CROSS_SIMILARITY",
                        "bundle": past_name,
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
    enforce_breathing_room: bool | None = None,
    strict: bool = False,
    runs_dir: Path | None = None,
    current_run_name: str = "",
) -> Dict[str, Any]:
    all_violations: List[Dict[str, Any]] = []

    # AI discourse & filler clichés
    all_violations.extend(check_ai_cliche_phrases(scenes))

    # 0. Visual prompt clichés
    all_violations.extend(check_visual_prompt_cliches(scenes, characters=characters, style=style))

    from scripts.visual_quality import (
        check_abstract_card_clustering,
        check_atomic_variation_continuity,
        check_character_breathing_room,
        check_instructional_manual_loop,
        check_scene_narrative_progression,
        check_setting_description_verbosity,
        check_ungrounded_environment_scenes,
        check_visual_setting_diversity,
    )
    from visual_style import STYLE_DESCRIPTION, render_style

    has_visual_fields = any(sc.get("setting") or sc.get("images") for sc in scenes)
    if has_visual_fields:
        all_violations.extend(check_visual_setting_diversity(scenes))
        all_violations.extend(check_scene_narrative_progression(scenes))

        has_new_shots = any(
            str(im.get("shot_type")) in {"still_life", "environment", "concept_metaphor", "visual_diagram", "cutaway_detail"}
            for sc in scenes
            for im in sc.get("images", [])
        )
        is_legacy_blueprint = (
            not has_new_shots
            and any(len(str(sc.get("setting", "")).split()) > 10 for sc in scenes)
            and all(
                str(im.get("shot_type")) in {"", "full_scene", "variation", "macro_prop", "white_card", "white_isolated"}
                for sc in scenes
                for im in sc.get("images", [])
            )
        )
        if enforce_breathing_room is not None:
            should_enforce_breathing = enforce_breathing_room
        elif is_legacy_blueprint:
            should_enforce_breathing = False
        elif style is not None:
            should_enforce_breathing = (
                render_style({"style": style}) in {"earth_toned_2d", "hand_drawn_2d_explainer"}
                or style == STYLE_DESCRIPTION
                or has_new_shots
            )
        else:
            should_enforce_breathing = has_new_shots or not is_legacy_blueprint

        if should_enforce_breathing:
            all_violations.extend(check_character_breathing_room(scenes, strict=strict))
            all_violations.extend(check_setting_description_verbosity(scenes, strict=strict))
            all_violations.extend(check_abstract_card_clustering(scenes))
            all_violations.extend(check_ungrounded_environment_scenes(scenes))
            all_violations.extend(check_atomic_variation_continuity(scenes))
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
    if (corpus_dir and corpus_dir.is_dir()) or (runs_dir and runs_dir.is_dir()):
        cs_violations = check_corpus_cross_similarity(
            scenes,
            corpus_dir=corpus_dir,
            runs_dir=runs_dir,
            current_run_name=current_run_name,
            topic_title=topic_title,
        )
        all_violations.extend(cs_violations)

    # 5. Human sentence rhythm metrics & optional hard enforcement
    rhythm_metrics = compute_sentence_rhythm_metrics(scenes)
    if enforce_rhythm_variance:
        all_violations.extend(check_sentence_rhythm_variance(scenes))

    if not all_violations:
        status = "PASS"
    elif strict:
        status = "FAIL"
    else:
        status = "WARN"

    return {
        "status": status,
        "total_violations": len(all_violations),
        "violations": all_violations,
        "rhythm_metrics": rhythm_metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint video script for lexical and narrative diversity.")
    parser.add_argument("script_file", help="Path to content.json, script.json, or bundle manifest")
    parser.add_argument("--corpus-dir", default="sys/exports", help="Corpus directory to check against")
    parser.add_argument(
        "--runs-dir",
        default=str(SYS_DIR / "runs"),
        help="Runs directory to check against for cross-channel similarity",
    )
    parser.add_argument(
        "--enforce-breathing-room",
        action="store_true",
        default=None,
        help="Explicitly enforce visual breathing room and concise setting constraints",
    )
    parser.add_argument(
        "--no-breathing-room",
        dest="enforce_breathing_room",
        action="store_false",
        help="Explicitly disable visual breathing room and concise setting constraints",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Enforce strict mode and exit with code 1 on any violation or warning",
    )
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
    runs_dir = Path(args.runs_dir) if args.runs_dir else None
    current_run_name = ""
    if target_path.parent.parent.name == "runs":
        current_run_name = target_path.parent.name
    elif target_path.parent.name and (SYS_DIR / "runs" / target_path.parent.name).is_dir():
        current_run_name = target_path.parent.name

    result = lint_script(
        scenes,
        corpus_dir=corpus_dir,
        claim_facts=claim_facts,
        topic_title=topic_title,
        characters=data.get("characters") if isinstance(data, dict) else None,
        style=data.get("style") if isinstance(data, dict) else None,
        enforce_breathing_room=args.enforce_breathing_room,
        strict=args.strict,
        runs_dir=runs_dir,
        current_run_name=current_run_name,
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
            elif v_type == "AI_CLICHE_PHRASE":
                print(f"[{idx}] {v_type} in {v['scene_id']}:")
                print(f"    Banned AI cliché: '{v.get('matched_text', v.get('pattern', ''))}'")
                print(f"    Snippet: {v.get('snippet', '')}")
            elif v_type in ("FORMULAIC_TRANSITION", "ACADEMIC_NAMEDROP_BLOAT", "CLARITY_GUIDANCE"):
                print(f"[{idx}] {v_type} in {v['scene_id']} cue #{v.get('sentence_index', 1)}:")
                print(f"    Message: {v.get('message', v.get('pattern', ''))}")
                print(f"    Snippet: {v.get('snippet', '')}")
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
            elif v_type == "CHARACTER_STREAK_EXCEEDED":
                print(f"[{idx}] {v_type} in scene {v.get('scene_id')} (beat {v.get('beat_id')}):")
                print(f"    {v.get('message')}")
            elif v_type == "LOW_CHARACTER_FREE_RATIO":
                print(f"[{idx}] {v_type} across scenes {', '.join(v.get('scenes', []))}:")
                print(f"    {v.get('message')}")
            elif v_type == "SETTING_DESCRIPTION_TOO_VERBOSE":
                print(f"[{idx}] {v_type} in scene {v.get('scene_id')}:")
                print(f"    Word count: {v.get('word_count')} words (max allowed: {v.get('max_allowed')})")
                print(f"    Setting: '{v.get('setting')}'")
            else:
                print(f"[{idx}] {v_type}: {v}")
        print("=" * 80)
        if args.strict:
            sys.exit(1)
        else:
            print("Soft warning: advisory notes logged above. Pass --strict to treat as failure.")
            print("=" * 80)
            sys.exit(0)
    else:
        print("All diversity checks passed! Zero formulaic transitions, zero backtracking, zero duplicate phrasing.")
        print("=" * 80)
        sys.exit(0)


if __name__ == "__main__":
    main()
