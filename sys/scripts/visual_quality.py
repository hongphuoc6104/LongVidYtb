"""Deterministic authoring guards; these do not certify image semantics."""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

_SETTING_ALIASES = {
    'study_desk': r'study (?:desk|room)|bàn học|phòng trọ',
    'laboratory': r'laborator|phòng thí nghiệm',
    'lecture_hall': r'lecture hall|giảng đường',
    'cafe': r'caf[eé]|quán cà phê',
}


def setting_key(scene: dict[str, Any]) -> str:
    """Prefer declared physical setting; never infer it from narration."""
    text = ' '.join(str(scene.get('setting', '')).casefold().split())
    for key, pattern in _SETTING_ALIASES.items():
        if re.search(pattern, text):
            return key
    return text.strip(' .')


def check_visual_setting_diversity(scenes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    keys = [setting_key(scene) for scene in scenes]
    streak = 0
    previous = ''
    for scene, key in zip(scenes, keys, strict=True):
        streak = streak + 1 if key and key == previous else 1
        previous = key
        if key and streak > 2:
            violations.append({'type': 'SETTING_MONOTONY_STREAK', 'scene_id': scene.get('id'), 'setting': key})
    if len(scenes) >= 10:
        for key, count in Counter(k for k in keys if k).items():
            if count / len(scenes) > .30:
                violations.append({'type': 'LOW_VISUAL_SETTING_VARIETY', 'setting': key,
                                   'scenes': [s.get('id') for s, k in zip(scenes, keys, strict=True) if k == key]})
    return violations


def check_instructional_manual_loop(scenes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Require two repeated operations, avoiding flags for merely discussing a paper/book.
    operations = (r'(?:gấp|đóng)\s+(?:cuốn\s+)?sách|close\s+(?:the\s+)?(?:text)?book',
                  r'(?:lấy|đặt|viết.*?lên)\s+(?:một\s+)?tờ giấy trắng|take.*?blank (?:sheet|paper)',
                  r'khoanh\s+(?:tròn|chỗ)|circle\s+(?:the\s+)?(?:gap|question)',
                  r'mở\s+(?:cuốn\s+)?sách|open\s+(?:the\s+)?(?:text)?book')
    pairs: Counter[tuple[int, int]] = Counter()
    refs: dict[tuple[int, int], list[str]] = {}
    for scene in scenes:
        text = str(scene.get('narration') or scene.get('narration_en') or '').casefold()
        found = [i for i, pattern in enumerate(operations) if re.search(pattern, text)]
        for i, first in enumerate(found):
            for second in found[i + 1:]:
                pair = (first, second)
                pairs[pair] += 1
                refs.setdefault(pair, []).append(scene.get('id', scene.get('scene_id', '?')))
    return [{'type': 'INSTRUCTIONAL_MANUAL_REPETITION', 'scenes': refs[pair]}
            for pair, count in pairs.items() if count > 3]


_NARRATIVE_PHASE_PATTERNS = (
    # Phase 1: Lived friction / everyday context (study, workplace, street, home, clinic, daily life)
    r'study|desk|room|cafe|lecture|office|highway|street|kitchen|home|clinic|station|commut|bàn học|phòng trọ|giảng đường|đời thực|ký túc xá|sinh viên|văn phòng|đường phố|bệnh viện|nhà ga',
    # Phase 2: Empirical observation / field survey / experiment / data evidence
    r'laborator|experiment|control group|survey|sensor|observation|field|archive|data|chart|trial|comparison|thí nghiệm|thực nghiệm|đối chứng|đối chiếu|kiểm chứng|khảo sát|dữ liệu|quan sát|thực địa',
    # Phase 3: Structural mechanism / conceptual model / diagram / metaphor / network
    r'brain|neural|metaphor|bridge|map|histor|pyramid|matrix|diagram|network|model|system|flow|graph|blueprint|não|thần kinh|ẩn dụ|cầu|bản đồ|lịch sử|tháp|ma trận|sơ đồ|mạng lưới|mô hình|hệ thống',
    # Phase 4: Actionable resolution / real-world return / synthesis / application
    r'study|desk|paper|article|application|defense|committee|workplace|corridor|hub|practice|workflow|sunrise|morning|resolved|balanced|bàn học|bài báo|ứng dụng|đời thực|bảo vệ|hội đồng|khóa luận|thực hành|giải pháp',
)

_PHASE_NAME_INDEX = {
    'lived_friction': 0,
    'hook': 0,
    'lead_in': 0,
    'empirical_conflict': 1,
    'problem': 1,
    'structural_model': 2,
    'causal_mechanism': 2,
    'explanation': 2,
    'counter_argument': 2,
    'actionable_resolution': 3,
    'takeaway': 3,
    'closing': 3,
}

MAX_CONSECUTIVE_VARIATIONS = 2


def check_scene_narrative_progression(scenes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Check declared visual evidence in order across 4 functional storytelling phases."""
    if len(scenes) < 10:
        return []
    next_zone = 0
    for scene in scenes:
        explicit_phase = str(
            scene.get('narrative_phase') or scene.get('editorial_section') or ''
        ).strip().casefold()
        if explicit_phase in _PHASE_NAME_INDEX and _PHASE_NAME_INDEX[explicit_phase] == next_zone:
            next_zone += 1
            if next_zone == len(_NARRATIVE_PHASE_PATTERNS):
                return []
            continue
        # Only visual fields count; mentioning a lab in speech does not change the room.
        visual = str(scene.get('setting', '')) + ' ' + ' '.join(
            str(image.get('description', '')) for image in scene.get('images', []))
        if re.search(_NARRATIVE_PHASE_PATTERNS[next_zone], visual.casefold()):
            next_zone += 1
            if next_zone == len(_NARRATIVE_PHASE_PATTERNS):
                return []
    return [{'type': 'NARRATIVE_SETTING_PROGRESSION', 'missing_zone': next_zone + 1}]


def apply_room_continuity(
    images: list[dict[str, Any]],
    max_consecutive_variations: int = MAX_CONSECUTIVE_VARIATIONS,
) -> None:
    """Within one authored room, return shots reuse the first full-scene reference (capped at max_consecutive_variations)."""
    base = None
    variation_streak = 0
    for image in images:
        shot = image.get('shot_type')
        if shot == 'full_scene':
            if base and not image.get('based_on') and variation_streak < max_consecutive_variations:
                image['based_on'] = base
                image['shot_type'] = 'variation'
                image['preserve'] = 'Keep room layout, window geometry, furniture, props and figure design.'
                variation_streak += 1
            elif not image.get('based_on'):
                base = image['id']
                variation_streak = 0
        elif shot == 'variation':
            variation_streak += 1
        else:
            variation_streak = 0
        if image.get('based_on') and image.get('has_character', True):
            lock = 'Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.'
            if 'expression' not in image.get('preserve', '').casefold() and 'biểu cảm' not in image.get('preserve', '').casefold():
                image['preserve'] = (image.get('preserve', '').rstrip() + ' ' + lock).strip()


def check_excessive_variation_streak(
    scenes: list[dict[str, Any]],
    max_streak: int = MAX_CONSECUTIVE_VARIATIONS,
) -> list[dict[str, Any]]:
    """Flag scenes that hold the same camera angle via > max_streak consecutive variations (anti-AI-slop guard)."""
    violations: list[dict[str, Any]] = []
    for sc in scenes:
        sc_id = str(sc.get('id', sc.get('scene_id', '?')))
        streak = 0
        for idx, im in enumerate(sc.get('images', [])):
            shot = str(im.get('shot_type', '')).strip().casefold()
            if shot == 'variation' or im.get('based_on'):
                streak += 1
                if streak > max_streak:
                    violations.append({
                        'type': 'EXCESSIVE_VARIATION_STREAK',
                        'scene_id': sc_id,
                        'beat_id': str(im.get('id', f'{sc_id}_I{idx + 1}')),
                        'streak': streak,
                        'max_allowed': max_streak,
                        'message': f'Too many consecutive variation beats ({streak} > {max_streak}) in {sc_id}; insert a macro_prop, visual_diagram, or fresh angle.',
                    })
            else:
                streak = 0
    return violations


_HUMAN_KEYWORDS_PATTERN = re.compile(
    r'\b(?:student|learner|figure|person|hand|finger|nhân vật|người)\b',
    re.IGNORECASE,
)


def _is_character_beat(beat: dict[str, Any]) -> bool:
    """Classify whether a visual beat is a standard full_scene/variation room beat vs a visual-break beat."""
    if beat.get('character_free') is True or beat.get('has_character') is False:
        return False
    shot_type = str(beat.get('shot_type', '')).strip().casefold()
    if shot_type in {'still_life', 'environment', 'white_card', 'white_isolated', 'visual_diagram', 'cutaway_detail', 'concept_metaphor', 'macro_prop'}:
        return False
    if beat.get('has_character') is True:
        return True
    if shot_type in {'full_scene', 'variation'}:
        return True
    if beat.get('character_ids'):
        return True
    desc = str(beat.get('description', '')).casefold()
    if desc and _HUMAN_KEYWORDS_PATTERN.search(desc):
        return True
    return False


def check_character_breathing_room(
    scenes: list[dict[str, Any]],
    strict: bool = False,
) -> list[dict[str, Any]]:
    """Check visual breathing room.

    Under the Feynman visual formula (1 character + 1 focal metaphor on clean flat canvas
    with progressive domino frames adding detail incrementally without decorative clutter),
    progressive domino frames are supported and not blocked by arbitrary empty-frame counts
    or rigid streak caps (strict=False by default).
    When strict=True, legacy 4-beat streak and 30% rest ratio checks are evaluated.
    """
    if not strict:
        return []

    beats: list[dict[str, Any]] = []
    for sc in scenes:
        images = sc.get('images')
        sc_id = str(sc.get('id', sc.get('scene_id', '?')))
        if images and isinstance(images, list):
            for im in images:
                beats.append({'scene_id': sc_id, 'beat_id': str(im.get('id', sc_id)), 'beat': im})
        else:
            beats.append({'scene_id': sc_id, 'beat_id': sc_id, 'beat': sc})

    if not beats:
        return []

    violations: list[dict[str, Any]] = []

    # 1. Consecutive character streak check (max 4 in strict mode)
    char_streak = 0
    for idx, item in enumerate(beats):
        if _is_character_beat(item['beat']):
            char_streak += 1
            if char_streak > 4:
                violations.append({
                    'type': 'CHARACTER_STREAK_EXCEEDED',
                    'scene_id': item['scene_id'],
                    'beat_id': item['beat_id'],
                    'beat_index': idx,
                    'streak': char_streak,
                    'message': f'Excessive consecutive character beats ({char_streak} > 4)',
                    'guidance': 'Consider using concept_metaphor or visual_diagram to provide visual breathing room if not using progressive domino frames.',
                })
        else:
            char_streak = 0

    # 2. Rolling 10-beat sequence check (>= 30% character-free in strict mode)
    if len(beats) >= 10:
        for i in range(len(beats) - 9):
            window = beats[i : i + 10]
            rest_count = sum(1 for b in window if not _is_character_beat(b['beat']))
            if rest_count < 3:
                violations.append({
                    'type': 'LOW_CHARACTER_FREE_RATIO',
                    'scene_id': window[0]['scene_id'],
                    'window_start': i,
                    'window_end': i + 10,
                    'scenes': sorted({b['scene_id'] for b in window}),
                    'beat_ids': [b['beat_id'] for b in window],
                    'character_free_count': rest_count,
                    'ratio': round(rest_count / 10.0, 2),
                    'message': f'Insufficient visual breathing room in 10-beat window ({rest_count}/10 < 30%)',
                    'guidance': 'Incorporate focal metaphors or diagram frames if character presence feels continuous.',
                })

    return violations


def check_setting_description_verbosity(
    scenes: list[dict[str, Any]],
    max_words: int = 30,
    strict: bool = False,
) -> list[dict[str, Any]]:
    """Flag setting descriptions exceeding word threshold.

    Under the Feynman visual formula, setting descriptions describe a clean flat canvas
    with 1 character + 1 focal metaphor. Hard 8-word/10-word caps are relaxed to constructive
    guidance (default max_words=30, strict=False).
    When strict=True, strict 10-word ceiling is enforced.
    """
    effective_max = 10 if strict else max_words
    violations: list[dict[str, Any]] = []
    for sc in scenes:
        setting = str(sc.get('setting', '')).strip()
        if not setting:
            continue
        words = setting.split()
        if len(words) > effective_max:
            sc_id = str(sc.get('id', sc.get('scene_id', '?')))
            violations.append({
                'type': 'SETTING_DESCRIPTION_TOO_VERBOSE',
                'scene_id': sc_id,
                'setting': setting,
                'word_count': len(words),
                'max_allowed': effective_max,
                'message': f"Setting description exceeds {effective_max} words ({len(words)} words): '{setting}'",
                'guidance': 'Keep flat canvas setting descriptions focused on the character and focal metaphor without interior room clutter.',
            })
    return violations


def check_abstract_card_clustering(
    scenes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Ban clustering of > 2 consecutive abstract card shots (white_card, visual_diagram, cutaway_detail)."""
    beats: list[dict[str, Any]] = []
    for sc in scenes:
        images = sc.get('images')
        sc_id = str(sc.get('id', sc.get('scene_id', '?')))
        if images and isinstance(images, list):
            for im in images:
                beats.append({'scene_id': sc_id, 'beat_id': str(im.get('id', sc_id)), 'beat': im})
        else:
            beats.append({'scene_id': sc_id, 'beat_id': sc_id, 'beat': sc})

    violations: list[dict[str, Any]] = []
    abstract_streak = 0
    abstract_shots = {'white_card', 'white_isolated', 'visual_diagram', 'cutaway_detail'}
    for idx, item in enumerate(beats):
        shot = str(item['beat'].get('shot_type', '')).strip().casefold()
        if shot in abstract_shots:
            abstract_streak += 1
            if abstract_streak > 2:
                violations.append({
                    'type': 'CONSECUTIVE_ABSTRACT_CARDS_EXCEEDED',
                    'scene_id': item['scene_id'],
                    'beat_id': item['beat_id'],
                    'beat_index': idx,
                    'streak': abstract_streak,
                    'message': f'Too many consecutive abstract cards ({abstract_streak} > 2)',
                })
        else:
            abstract_streak = 0
    return violations


def check_ungrounded_environment_scenes(
    scenes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Ban ungrounded environment scenes that lack character grounding, metaphor marker, or active story location."""
    violations: list[dict[str, Any]] = []
    for sc in scenes:
        sc_id = str(sc.get('id', sc.get('scene_id', '?')))
        setting = str(sc.get('setting', '')).strip()
        images = sc.get('images', [])
        for im in images:
            shot = str(im.get('shot_type', '')).strip().casefold()
            if shot == 'environment':
                desc = str(im.get('description', '')).casefold()
                has_metaphor = any(w in desc for w in ('metaphor', 'symbol', 'boundary', 'tension', 'horizon', 'mist', 'void'))
                has_chars = bool(im.get('character_ids')) or bool(sc.get('character_ids'))
                if not has_metaphor and not has_chars and not setting:
                    violations.append({
                        'type': 'UNGROUNDED_ENVIRONMENT_SCENE',
                        'scene_id': sc_id,
                        'beat_id': str(im.get('id', sc_id)),
                        'message': 'Ungrounded environment shot lacks character grounding, metaphor marker, or active story setting',
                    })
    return violations


def check_atomic_variation_continuity(
    scenes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Enforce atomic variation continuity: each variation must reference a valid base within the same scene."""
    violations: list[dict[str, Any]] = []
    for sc in scenes:
        sc_id = str(sc.get('id', sc.get('scene_id', '?')))
        images = sc.get('images', [])
        seen_ids = set()
        for im in images:
            im_id = str(im.get('id', ''))
            seen_ids.add(im_id)
            shot = str(im.get('shot_type', '')).strip().casefold()
            if shot == 'variation':
                based_on = str(im.get('based_on', '')).strip()
                if not based_on or based_on not in seen_ids:
                    violations.append({
                        'type': 'BROKEN_VARIATION_CONTINUITY',
                        'scene_id': sc_id,
                        'beat_id': im_id,
                        'based_on': based_on,
                        'message': f"Variation '{im_id}' does not immediately follow or reference a prior base in the same scene",
                    })
    return violations

