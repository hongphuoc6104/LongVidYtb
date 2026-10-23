"""Reference-led explainer validation. Structural bindings are not semantic certification."""
from __future__ import annotations

import re
from typing import Any

try:
    from flow_prompts.compiler import registry
except ImportError:
    def registry(version):
        return {'style': 'HandDrawn2D'}

STYLE_VERSION = '1.7.0'


def is_reference_explainer(brief: dict[str, Any]) -> bool:
    return brief.get('style') == registry(STYLE_VERSION).get('style', 'HandDrawn2D')


def validate_short(brief: dict[str, Any]) -> list[str]:
    """Apply the short contract to portrait spin-off jobs (dynamic duration)."""
    if not is_reference_explainer(brief) or brief.get('format_profile') != 'short_9x16':
        return []
    errors = []
    if brief.get('speed', 1.0) != 1.0:
        errors.append('SHORT_SPEED: narration speed must be 1.0')
    for output in brief.get('outputs', []):
        if output.get('subtitles') is not True:
            errors.append('SHORT_SUBTITLES: portrait output requires subtitles')
    return errors


def validate_human_editorial(brief: dict[str, Any]) -> list[str]:
    """Validate dynamic topic-specific questions and expanded human editorial ideas."""
    editorial = brief.get('human_editorial')
    if not isinstance(editorial, dict):
        return []
    errors = []
    questions = [str(q).strip() for q in editorial.get('dynamic_questions', []) if str(q).strip()]
    if len(questions) != len(set(q.casefold() for q in questions)):
        errors.append('HUMAN_EDITORIAL_DUPLICATE_QUESTIONS: dynamic_questions must be unique')
    dilemmas = {str(d).strip().casefold() for d in editorial.get('topic_dilemmas', []) if str(d).strip()}
    if any(q.casefold() in dilemmas for q in questions):
        errors.append('HUMAN_EDITORIAL_QUESTION_COPIED: dynamic_questions must be distinct from topic_dilemmas')
    ideas = editorial.get('expanded_content_ideas', [])
    summaries = []
    for idx, i in enumerate(ideas):
        if isinstance(i, dict):
            s = str(i.get('idea_summary') or i.get('summary') or '').strip()
            if not s:
                errors.append(f'HUMAN_EDITORIAL_EMPTY_IDEA: expanded_content_ideas[{idx}] requires summary or idea_summary')
            else:
                summaries.append(s)
    if len(summaries) != len(set(s.casefold() for s in summaries)):
        errors.append('HUMAN_EDITORIAL_DUPLICATE_IDEAS: expanded_content_ideas must contain distinct ideas')
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
