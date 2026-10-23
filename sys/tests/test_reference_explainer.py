"""Production regressions for explicit entities, explanatory data and dispatch rights."""
import copy
import json
from unittest.mock import Mock, patch

import pytest

pytest.importorskip("flow_dispatch", reason="requires images module (flow_dispatch)")
pytest.importorskip("flow_prompts", reason="requires images module (flow_prompts)")

import image_pipeline  # noqa: E402
from content.research_story_architect import build_scenes_from_story_rows, validate_see_say_alignment  # noqa: E402
from explainer_contract import validate_explanations, validate_short  # noqa: E402
from flow_dispatch import authorized_profiles, validate_dependencies  # noqa: E402
from flow_prompts import PromptError, compile, create_pin, validate_pin  # noqa: E402
from flow_prompts.compiler import registry  # noqa: E402


def visual(**extra):
    return {'description': 'Two columns compare draft pages and book pages on white.',
            'aspect_ratio': '9:16', 'shot_type': 'full_scene', 'allowed_text': [], **extra}


def test_object_scene_compiler_has_no_cast_identity_or_physical_action_requirement():
    result = compile('NanoBanana2Lite', 'scene', visual(), '1.7.0')
    assert result['provenance']['references']['character'] is None
    assert 'Strict character-free composition' in result['prompt']
    assert 'high-velocity' not in result['prompt']
    assert 'warm-cool temperature contrast' not in result['prompt']
    assert 'clear black outer contours' in result['prompt']


def test_explicit_people_have_contextual_design_without_compulsory_identity_reference():
    result = compile('NanoBanana2Lite', 'scene', visual(has_character=True), '1.7.0')
    assert result['provenance']['references']['character'] is None
    assert 'Entity policy is explicit' in result['prompt']
    assert 'Strict character-free composition' not in result['prompt']


@pytest.mark.parametrize('fields', [{'has_character': 'false'}, {'has_character': True, 'character_free': True}])
def test_compiler_rejects_ambiguous_entity_policy(fields):
    with pytest.raises(PromptError, match='FLOW_ENTITY_POLICY_INVALID'):
        compile('NanoBanana2Lite', 'scene', visual(**fields), '1.7.0')


def test_static_explanation_is_not_rejected_as_a_lazy_action():
    result = compile('NanoBanana2Lite', 'scene', visual(description='Books resting on table, grouped into two labelled quantities.'), '1.7.0')
    assert 'Books resting on table' in result['prompt']
    with pytest.raises(PromptError, match='LAZY_VISUAL_ACTION_FORBIDDEN'):
        compile('NanoBanana2Lite', 'scene', visual(description='Books resting on table.'), '1.6.0')


def test_old_registry_pin_stays_valid():
    pin = create_pin('NanoBanana2Lite', '1.6.0')
    assert validate_pin(pin) == pin
    assert 'fine-to-medium warm-charcoal' in registry('1.6.0')['style']
    assert pin['registry_sha256'] != create_pin('NanoBanana2Lite', '1.7.0')['registry_sha256']


def test_story_rows_do_not_invent_default_ch01():
    scenes = build_scenes_from_story_rows([('Comparison', 'White field', [
        ('Hai cột so sánh lượng tài liệu.', 'full_scene|Two columns compare document quantities.'),
    ])])
    assert scenes[0].character_ids == []
    assert scenes[0].visual_beats[0].character_ids == []


@pytest.mark.parametrize('sentence,description', [
    ('Bản nháp 500 từ đánh bại một nghìn giờ đọc thêm.', 'A spaceship travels 500 kilometers through space.'),
    ('Sinh viên khảo sát 70 người trong thư viện.', '70 purple elephants dancing on Mars.'),
    ('', 'A diagram.'),
])
def test_matching_numbers_and_blank_text_do_not_certify_alignment(sentence, description):
    assert validate_see_say_alignment(sentence, description) is False


def authored_content():
    return {'characters': [], 'scenes': [{'narration': 'Bản nháp có 500 từ.', 'images': [{
        'id': 'SC01_I1', 'character_ids': [], 'has_character': False,
        'description': 'A draft page labelled 500 words.', 'explanation': {
            'quote': 'Bản nháp có 500 từ.', 'relation': 'quantity',
            'source_terms': ['Bản nháp'], 'visual_terms': ['draft page'],
        },
    }]}]}


def test_explanation_requires_traceable_source_visual_terms_and_quantity():
    content = authored_content()
    assert validate_explanations(content) == []
    content['scenes'][0]['images'][0]['description'] = 'A spaceship travels far.'
    errors = validate_explanations(content)
    assert any('EXPLANATION_TERMS' in e for e in errors)
    assert any('EXPLANATION_QUANTITY' in e for e in errors)


def test_unused_character_does_not_silently_trigger_registration():
    content = authored_content()
    content['characters'] = [{'id': 'CH01'}]
    assert 'UNUSED_CHARACTER: CH01 must not trigger reference generation' in validate_explanations(content)


def test_production_request_gate_rejects_missing_explanation_before_planning_or_transport():
    content = authored_content()
    del content['scenes'][0]['images'][0]['explanation']
    p = Mock()
    p.brief.return_value = [{'style': registry('1.7.0')['style']}]
    with patch.object(image_pipeline, 'content', return_value=content), patch.object(image_pipeline, 'planned_units') as units:
        with pytest.raises(Exception, match='EXPLAINER_CONTRACT: EXPLANATION_REQUIRED'):
            image_pipeline._plan_request(p, 'test', 'SC01_I1', 'draft', [], None, None)
    units.assert_not_called()


def test_reference_short_supports_dynamic_duration():
    brief = {'style': registry('1.7.0')['style'], 'format_profile': 'short_9x16',
             'scene_count': 19, 'duration': {'min_seconds': 240, 'max_seconds': 420},
             'speed': 1.0, 'outputs': [{'subtitles': True}]}
    assert validate_short(brief) == []
    brief['speed'] = 1.2
    assert len(validate_short(brief)) == 1
    brief['speed'] = 1.0
    brief['outputs'] = [{'subtitles': False}]
    assert len(validate_short(brief)) == 1



def session_profiles(tmp_path):
    profiles = [{'id': f'p{i}', 'directory': 'Default', 'user_data_dir': str(tmp_path / str(i))} for i in range(3)]
    accounts = [{'id': f'a{i}', 'service': 'flow', 'profile': 'Default', 'metadata_root': p['user_data_dir']}
                for i, p in enumerate(profiles)]
    session = {'pool': ['a0', 'a1'], 'defaults': {'flow': 'a0'}, 'runtime_bindings': {
        'flow': {'account': 'a0', 'target': {'profile_path': str(tmp_path / '0/Default')}}}}
    return profiles, accounts, session


def test_pool_binding_does_not_force_single_worker_or_authorize_extra_accounts(tmp_path):
    profiles, accounts, session = session_profiles(tmp_path)
    assert [p['id'] for p in authorized_profiles(profiles, session, accounts, 'pool')] == ['p0', 'p1']
    assert [p['id'] for p in authorized_profiles(profiles, session, accounts, 'single_profile')] == ['p0']
    session['pool'] = []
    with pytest.raises(ValueError, match='FLOW_AUTHORIZED_POOL_EMPTY'):
        authorized_profiles(profiles, session, accounts, 'pool')


def test_dependency_validation_catches_cycles_and_missing_parents():
    units = [{'id': 'a', 'based_on': None}, {'id': 'b', 'based_on': 'a'}, {'id': 'c', 'based_on': None}]
    assert validate_dependencies(units) == 2
    units[0]['based_on'] = 'b'
    with pytest.raises(ValueError, match='FLOW_DEPENDENCY_CYCLE'):
        validate_dependencies(units)
    units[0]['based_on'] = 'missing'
    with pytest.raises(ValueError, match='FLOW_DEPENDENCY_MISSING'):
        validate_dependencies(units)


def test_recovery_does_not_reset_unknown_request_from_error_words(tmp_path):
    p = Mock()
    p.job.return_value = tmp_path
    folder = tmp_path / 'flow/attempts/key'
    folder.mkdir(parents=True)
    record = {'key': 'key', 'state': 'submitted', 'error': 'CDP_TRANSPORT_CLOSED Failed to fetch'}
    path = folder / 'request.json'
    path.write_text(json.dumps(record))
    before = path.read_bytes()
    with patch.object(image_pipeline, '_unresolved_conflict', return_value=copy.deepcopy(record)):
        result = image_pipeline.reconcile_stuck_conflict(p, 'test', 'SC01')
    assert result['state'] == 'submitted'
    assert path.read_bytes() == before
    p.event.assert_not_called()
