"""Behavioral quality regressions without provider, TTS or rendered-media claims."""
from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import pytest
from adapters import DEFAULT_PAUSE
from content_contract import ContractError, validate_content
from flow_prompts import compile as compile_prompt
from format_profiles import clearance_for_output
from output_contract import outputs, voice_settings
from remote_audio import primary_scene_request
from scripts.subtitles import audit_cues, phrase_chunks, sentence_units, subtitle_cues
from scripts.visual_quality import (
    apply_room_continuity,
    check_instructional_manual_loop,
    check_scene_narrative_progression,
    check_visual_setting_diversity,
)
from tools.build_full_frame_acceptance import build_topic
from tools.research_story_architect import build_brief_v3, build_content_v3

SYSTEM = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('ratio', ['16:9', '9:16'])
def test_full_frame_prompt_does_not_reserve_caption_band(ratio: str) -> None:
    record = compile_prompt('NanoBanana2', 'scene', {
        'description': 'A confused anonymous stick figure at a desk.', 'aspect_ratio': ratio,
        'allowed_text': [], 'caption_clearance': {'edge': 'bottom', 'fraction': .18},
        'shot_type': 'macro_prop',
    }, '1.3.0')
    assert '"caption_clearance": null' in record['prompt']
    assert 'full-bleed' in record['prompt']
    assert 'four-finger' in record['prompt']
    assert 'abstract wavy ink lines' in record['prompt']
    assert 'Reserve the specified caption band' not in record['prompt']
    assert clearance_for_output('16:9', True) is None
    assert clearance_for_output('9:16', True) == {'edge': 'bottom', 'fraction': .18}


@pytest.mark.parametrize('text', [
    'Trang sách vàng kín, đầu bạn vẫn trống. Bạn gạch thêm một dòng.',
    'He said “Done.” Next sentence! A third?',
    'Giá trị 3.14 vẫn đúng. Câu sau… Một câu nữa.',
])
def test_captions_preserve_tokens_and_sentence_boundaries(text: str) -> None:
    phrases = phrase_chunks(text, 30)
    assert ' '.join(phrases) == text
    assert all(len(sentence_units(phrase)) == 1 for phrase in phrases)
    cues = subtitle_cues([{'scene_id': 'SC01', 'text': text, 'start': 0., 'end': 15.}])
    assert audit_cues(cues)['errors'] == []
    assert audit_cues([{'text': text, 'start': 0., 'end': 15.}])['errors'][0]['code'] == 'CAPTION_CROSS_SENTENCE'


def test_remote_sentence_requests_keep_language_parts_and_tone_aligned() -> None:
    text = 'Bạn thử active recall. Rồi kiểm tra kết quả.'
    item = primary_scene_request({'id': 'SC01', 'vocabulary': [{'word': 'active recall'}],
                                  'tone': 'analytical_crisp'}, text, 'vi', DEFAULT_PAUSE, 2, False)
    assert item['texts'] == ['Bạn thử active recall.', 'Rồi kiểm tra kết quả.']
    assert item['gaps'] == [.5]
    assert len(item['parts']) == len(item['texts'])
    assert any(part['lang'] == 'en' for part in item['parts'][0])
    assert item['tone'] == 'analytical_crisp'
    assert item['retake'] == 2
    assert item['tail'] == .7


def test_renderer_cut_uses_camera_and_landscape_caption_is_transparent() -> None:
    script = '''
import {selectSemanticCameraEffect, overscanScale} from './sys/renderer/camera.mjs';
import {captionStyle} from './sys/renderer/captions.mjs';
console.log(JSON.stringify({
  cut: selectSemanticCameraEffect({effect:'cut'}, {camera:'wide'}, 0),
  zoom: selectSemanticCameraEffect({effect:'zoom_in'}, {}, 0),
  minScale: overscanScale(1),
  landscape: captionStyle(1920,1080), portrait: captionStyle(1080,1920)
}));
'''
    result = subprocess.run(['node', '--input-type=module', '-e', script], cwd=SYSTEM.parent,
                            capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    assert data['cut'] == 'zoom_out'
    assert data['zoom'] == 'zoom_in'
    assert data['minScale'] == 1.045
    assert data['landscape']['background'] == 'transparent'
    assert data['landscape']['border'] == 'none'
    assert data['portrait']['background'] == 'transparent'
    assert data['portrait']['border'] == 'none'


@pytest.mark.parametrize('speed', [0.85, 1.16, 1.39])
def test_viet_narrator_rejects_uncalibrated_speed(speed: float) -> None:
    brief = {'aspect_ratio': '16:9', 'outputs': [
        {'language': 'vi', 'aspect_ratio': '16:9', 'subtitles': False, 'voice': 'VietNarrator', 'speed': speed}]}
    with pytest.raises(ValueError, match='OUTPUT_CONTRACT'):
        outputs(brief)
    del brief['outputs'][0]['speed']
    with pytest.raises(ValueError, match='OUTPUT_CONTRACT'):
        voice_settings(brief, 'vi', {'tts_voice': 'VietNarrator', 'tts_speed': speed})
    assert voice_settings(brief, 'vi', {'tts_voice': 'VietNarrator'})['speed'] == 1.0


def test_room_return_retains_base_and_expression_lock() -> None:
    images = [{'id': 'I1', 'shot_type': 'full_scene', 'based_on': None, 'preserve': ''},
              {'id': 'I2', 'shot_type': 'macro_prop', 'based_on': None},
              {'id': 'I3', 'shot_type': 'full_scene', 'based_on': None, 'preserve': ''}]
    apply_room_continuity(images)
    assert images[2]['based_on'] == 'I1'
    assert images[2]['shot_type'] == 'variation'
    assert 'Expression lock' in images[2]['preserve']
    assert images[1]['based_on'] is None
    original = copy.deepcopy(images)
    apply_room_continuity(images)
    assert images == original


def test_diversity_blocks_monotony_and_repeated_operation_pairs() -> None:
    scenes = [{'id': f'SC{i:02}', 'setting': 'A study desk at night.',
               'narration': 'Gấp sách lại, rồi khoanh chỗ chưa nhớ.'} for i in range(1, 11)]
    assert {'SETTING_MONOTONY_STREAK', 'LOW_VISUAL_SETTING_VARIETY'} == {
        row['type'] for row in check_visual_setting_diversity(scenes)}
    assert check_instructional_manual_loop(scenes)[0]['type'] == 'INSTRUCTIONAL_MANUAL_REPETITION'
    assert check_scene_narrative_progression(scenes)[0]['type'] == 'NARRATIVE_SETTING_PROGRESSION'
    assert check_visual_setting_diversity(scenes[:2]) == []
    assert check_instructional_manual_loop(scenes[:3]) == []


def test_acceptance_contract_enforces_visual_journey_before_provider_calls() -> None:
    topic = build_topic()
    brief = build_brief_v3(topic)
    content = build_content_v3(topic, brief, 'TEST')
    validate_content(SYSTEM, brief, 1, 'TEST', content)
    assert brief['outputs'][0]['subtitles'] is False
    assert brief['outputs'][0]['speed'] == 1.0
    assert all(beat['effect'] != 'cut' for scene in content['scenes'] for beat in scene['beats'])
    for scene in content['scenes']:
        scene['setting'] = 'A study desk at night.'
    with pytest.raises(ContractError, match='SETTING_MONOTONY_STREAK'):
        validate_content(SYSTEM, brief, 1, 'TEST', content)


def test_full_frame_plan_rejects_uniform_motion_and_missing_expression_lock() -> None:
    topic = build_topic()
    brief = build_brief_v3(topic)
    original = build_content_v3(topic, brief, 'TEST')
    uniform = copy.deepcopy(original)
    for beat in uniform['scenes'][0]['beats']:
        beat['effect'] = 'zoom_in'
    with pytest.raises(ContractError, match='CAMERA_MOTION_MONOTONY'):
        validate_content(SYSTEM, brief, 1, 'TEST', uniform)
    unlocked = copy.deepcopy(original)
    variation = next(image for image in unlocked['scenes'][0]['images'] if image['based_on'])
    variation['preserve'] = 'Keep the room and furniture.'
    with pytest.raises(ContractError, match='EXPRESSION_LOCK_REQUIRED'):
        validate_content(SYSTEM, brief, 1, 'TEST', unlocked)


def test_remote_source_manifest_contains_executable_camera_dependencies(tmp_path: Path) -> None:
    import sys

    from colab_bridge.job_protocol import build_render_request

    request = build_render_request(SYSTEM, {'outputs': []}, {'scenes': []}, {'items': []},
                                   {'tracks': {}, 'wav': 'fixture.wav'}, lambda name: SYSTEM / 'config.json')
    # Only source files are exercised; the asset is explicitly not synthesized audio.
    for record in request['files']:
        if record['name'].startswith('source/'):
            target = tmp_path / record['name']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(Path(record['local_path']).read_bytes())
    result = subprocess.run([sys.executable, '-I', '-c',
                             'import sys; sys.path.insert(0, sys.argv[1]); '
                             'from scripts.story_plan import timeline; '
                             'from scripts.camera_motion import scene_camera_motions; '
                             'print(scene_camera_motions({"beats":[{"image_id":"I1","effect":"cut"}]}))',
                             str(tmp_path / 'source')], capture_output=True, text=True, check=True)
    assert result.stdout.strip() == "['zoom_in']"
    assert (tmp_path / 'source/renderer/camera.mjs').is_file()
