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


def check_scene_narrative_progression(scenes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Check declared visual evidence in order for long narratives, not exact percentages."""
    if len(scenes) < 10:
        return []
    patterns = (r'study|desk|room|cafe|lecture|bàn học|phòng trọ|giảng đường|đời thực|ký túc xá|sinh viên',
                r'laborator|experiment|control group|thí nghiệm|thực nghiệm|đối chứng|đối chiếu|kiểm chứng',
                r'brain|neural|metaphor|bridge|map|histor|pyramid|matrix|não|thần kinh|ẩn dụ|cầu|bản đồ|lịch sử|tháp|ma trận|sơ đồ',
                r'study|desk|paper|article|application|defense|committee|bàn học|bài báo|ứng dụng|đời thực|bảo vệ|hội đồng|khóa luận')
    next_zone = 0
    for scene in scenes:
        # Only visual fields count; mentioning a lab in speech does not change the room.
        visual = str(scene.get('setting', '')) + ' ' + ' '.join(
            str(image.get('description', '')) for image in scene.get('images', []))
        if re.search(patterns[next_zone], visual.casefold()):
            next_zone += 1
            if next_zone == len(patterns):
                return []
    return [{'type': 'NARRATIVE_SETTING_PROGRESSION', 'missing_zone': next_zone + 1}]


def apply_room_continuity(images: list[dict[str, Any]]) -> None:
    """Within one authored room, return shots reuse the first full-scene reference."""
    base = None
    for image in images:
        if image.get('shot_type') == 'full_scene':
            if base and not image.get('based_on'):
                image['based_on'] = base
                image['shot_type'] = 'variation'
                image['preserve'] = 'Keep room layout, window geometry, furniture, props and figure design.'
            elif not image.get('based_on'):
                base = image['id']
        if image.get('based_on'):
            lock = 'Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.'
            if 'expression' not in image.get('preserve', '').casefold():
                image['preserve'] = image.get('preserve', '') + ' ' + lock
