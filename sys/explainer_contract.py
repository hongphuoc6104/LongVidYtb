"""Reference-led explainer validation. Structural bindings are not semantic certification."""
from __future__ import annotations

import re
from typing import Any

try:
    from flow_prompts.compiler import registry
except ImportError:
    STYLE_170 = "Hand-drawn 2D explanatory illustration. Use clear black outer contours with slight natural hand-drawn irregularity and simple internal lines. Use selective flat color areas and only small simple grounding shadows when useful. Keep silhouettes readable on a mobile screen. Use a clean white field for isolated objects, comparisons and diagrams; contextual scenes may use broad flat color areas with only essential setting cues. Explain one clear relationship through objects, quantities, labels, arrows or relevant contextual action. Static objects and diagrams are valid explanations. No cinematic lighting, blue-gray shadow system, glossy volume, gradients, paper aging, photorealism or 3D. Draw a complete scene image."
    def registry(v):
        return {'style': STYLE_170}

STYLE_VERSION = '1.7.0'


def is_reference_explainer(brief: dict[str, Any]) -> bool:
    return brief.get('style') == registry(STYLE_VERSION)['style']


def validate_short(brief: dict[str, Any]) -> list[str]:
    """Apply the strict short contract to new reference-led jobs only."""
    if not is_reference_explainer(brief) or brief.get('format_profile') != 'short_9x16':
        return []
    errors = []
    duration = brief.get('duration', {})
    if brief.get('scene_count') != 5:
        errors.append('SHORT_SCENE_COUNT: exactly five standalone scenes required')
    if not (45 <= duration.get('min_seconds', 0) <= duration.get('max_seconds', 0) <= 60):
        errors.append('SHORT_DURATION: authored duration must stay within 45–60 seconds')
    if brief.get('speed', 1.0) != 1.0:
        errors.append('SHORT_SPEED: narration speed must be 1.0')
    for output in brief.get('outputs', []):
        if output.get('subtitles') is not True:
            errors.append('SHORT_SUBTITLES: portrait output requires subtitles')
    return errors


def validate_explanations(content: dict[str, Any]) -> list[str]:
    """Check explicit entity intent and traceable authored explanation bindings.

    Exact terms establish provenance, not translation accuracy or factual truth.
    An actual image review must still establish the intended relationship.
    """
    errors = []
    declared = {c['id'] for c in content.get('characters', [])}
    used = set()
    for scene in content.get('scenes', []):
        for image in scene.get('images', []):
            key = image['id']
            ids = image.get('character_ids', [])
            used.update(ids)
            if type(image.get('has_character')) is not bool:
                errors.append(f'ENTITY_POLICY_REQUIRED: {key} needs explicit has_character')
            if ids and not image.get('has_character'):
                errors.append(f'ENTITY_POLICY_CONFLICT: {key} has identity references but forbids people')
            binding = image.get('explanation')
            if not isinstance(binding, dict):
                errors.append(f'EXPLANATION_REQUIRED: {key} needs an authored source/visual binding')
                continue
            quote = binding.get('quote', '')
            if not quote.strip() or quote not in scene.get('narration', ''):
                errors.append(f'EXPLANATION_QUOTE: {key} quote must occur in its narration')
            if binding.get('relation') not in {'quantity', 'comparison', 'grouping', 'cause_effect', 'progression', 'structure', 'context'}:
                errors.append(f'EXPLANATION_RELATION: {key} needs a supported explanatory relationship')
            for field, text in [('source_terms', quote), ('visual_terms', image.get('description', ''))]:
                terms = binding.get(field)
                if not isinstance(terms, list) or not terms or any(
                    not isinstance(t, str) or not t.strip() or t.casefold() not in text.casefold() for t in terms
                ):
                    errors.append(f'EXPLANATION_TERMS: {key} {field} must trace to actual text')
            # A declared digit quantity must survive into the visual description
            # or approved lettering. Matching numbers alone never proves alignment.
            visual = image.get('description', '') + ' ' + str(image.get('visible_text', []))
            numbers = set(re.findall(r'\b\d+(?:[.,]\d+)?\b', quote))
            if numbers - set(re.findall(r'\b\d+(?:[.,]\d+)?\b', visual)):
                errors.append(f'EXPLANATION_QUANTITY: {key} omits an authored quantity')
    for identity in sorted(declared - used):
        errors.append(f'UNUSED_CHARACTER: {identity} must not trigger reference generation')
    return errors
