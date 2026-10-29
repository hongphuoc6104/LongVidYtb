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

try:
    from remote_audio import primary_scene_request
except ImportError:
    primary_scene_request = None
from content.research_story_architect import build_brief_v3, build_content_v3
from scripts.subtitles import audit_cues, phrase_chunks, sentence_units, subtitle_cues
from scripts.visual_quality import (
    apply_room_continuity,
    check_character_breathing_room,
    check_instructional_manual_loop,
    check_scene_narrative_progression,
    check_setting_description_verbosity,
    check_visual_setting_diversity,
)
from tools.build_full_frame_acceptance import build_topic

SYSTEM = Path(__file__).resolve().parents[1]
CAMERA_MJS_EXISTS = (SYSTEM / 'renderer/camera.mjs').is_file()
CAPTIONS_MJS_EXISTS = (SYSTEM / 'renderer/captions.mjs').is_file()
RENDERER_INDEX_EXISTS = (SYSTEM / 'renderer/index.tsx').is_file()
try:
    from colab_bridge.job_protocol import build_render_request
except ImportError:
    build_render_request = None


def _camera_result(script: str) -> object:
    prelude = """
import {buildCalmCameraPlan, calmCameraFrame, calmCameraStyle,
  BASE_OVERSCAN, CALM_MAX_ZOOM_PER_SEC} from './sys/renderer/camera.mjs';
"""
    result = subprocess.run(['node', '--input-type=module', '-e', prelude + script],
                            cwd=SYSTEM.parent, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


@pytest.mark.skipif(not CAMERA_MJS_EXISTS, reason="renderer/camera.mjs unavailable in pruned workspace")
def test_calm_camera_bounds_speed_and_rests_on_short_or_dense_shots() -> None:
    data = _camera_result("""
const results = [];
for (const fps of [24, 30, 60]) {
  for (const duration of [0.8, 1.2, 2.39, 2.4, 3.8, 8]) {
    for (const effect of ['zoom_in', 'zoom_out', 'push_in', 'pull_back', 'punch_in',
                          'pan_left', 'pan_right', 'slide_left', 'shake', 'hold']) {
      const scene = {start: 0, end: duration, images: [{at: 0, src: 'a.jpg', camera_motion: effect}]};
      const camera = buildCalmCameraPlan([scene])[0][0];
      const scales = Array.from({length: Math.ceil(duration * fps) + 1}, (_, i) => calmCameraFrame(camera, i / fps).scale);
      results.push({fps, duration, effect, scales});
    }
  }
}
console.log(JSON.stringify(results));
""")
    for case in data:
        scales = case['scales']
        changes = [right - left for left, right in zip(scales, scales[1:], strict=False)]
        assert min(scales) >= 1.045
        assert max(scales) <= 1.045 * 1.015 + 1e-12
        assert all(abs(change) * case['fps'] <= .004 + 1e-12 for change in changes)
        assert all(change >= -1e-12 for change in changes) or all(change <= 1e-12 for change in changes)
        if case['duration'] < 2.4 or case['effect'] in {'pan_left', 'pan_right', 'slide_left', 'shake', 'hold'}:
            assert len(set(scales)) == 1
        else:
            assert max(scales) > min(scales)
            assert abs(changes[0]) * case['fps'] < .0005
    cards = _camera_result("""
console.log(JSON.stringify(['white_card', 'macro_prop', 'white_isolated'].map(shot_type => {
  const camera = buildCalmCameraPlan([{start: 0, end: 8, images: [{at: 0, shot_type, camera_motion: 'punch_in'}]}])[0][0];
  return [calmCameraFrame(camera, 0), calmCameraFrame(camera, 4), calmCameraFrame(camera, 8)];
})));
""")
    assert all(start == middle == end for start, middle, end in cards)


@pytest.mark.skipif(not CAMERA_MJS_EXISTS, reason="renderer/camera.mjs unavailable in pruned workspace")
def test_calm_variation_cuts_share_time_and_focal_origin() -> None:
    data = _camera_result("""
const images = [
  {at: 0, src: 'base.jpg', camera_motion: 'zoom_in', focus: {x: .4, y: .4}},
  {at: 1.15, src: 'pose1.jpg', shot_type: 'variation', camera_motion: 'pan_right', focus: {x: .65, y: .58}},
  {at: 2.19, src: 'pose2.jpg', shot_type: 'variation', camera_motion: 'zoom_out'},
  {at: 3.82, src: 'pose2.jpg', camera_motion: 'punch_in'},
];
const plan = buildCalmCameraPlan([{start: 0, end: 6, images}])[0];
console.log(JSON.stringify(images.slice(1).map((beat, i) => ({
  before: calmCameraFrame(plan[i], beat.at - 1/30),
  outgoing: calmCameraStyle(calmCameraFrame(plan[i], beat.at)),
  incoming: calmCameraStyle(calmCameraFrame(plan[i+1], beat.at)),
  after: calmCameraFrame(plan[i+1], beat.at),
  sharedGroup: plan[i] === plan[i+1],
}))));
""")
    for cut in data:
        assert cut['sharedGroup']
        assert cut['outgoing'] == cut['incoming']
        assert cut['after']['focusX'] == 40
        assert cut['after']['focusY'] == 40
        assert abs(cut['after']['scale'] - cut['before']['scale']) * 30 <= .004


@pytest.mark.skipif(not CAMERA_MJS_EXISTS, reason="renderer/camera.mjs unavailable in pruned workspace")
def test_calm_camera_rest_budget_crosses_scene_boundaries_and_is_seek_safe() -> None:
    data = _camera_result("""
const scenes = Array.from({length: 4}, (_, i) => ({start: i*3, end: (i+1)*3,
  images: [{at: 0, camera_motion: 'punch_in', src: `${i}.jpg`}]}));
const plan = buildCalmCameraPlan(scenes);
const camera = plan[0][0];
const times = [2, 0, 3, 1, -1, 4, 2];
console.log(JSON.stringify({
  amplitudes: plan.map(beats => beats[0].amplitude),
  frames: times.map(t => calmCameraFrame(camera, t)),
  clean: calmCameraFrame(undefined, 0),
}));
""")
    assert data['amplitudes'][0] > 0
    assert data['amplitudes'][1:3] == [0, 0]
    assert data['amplitudes'][3] > 0
    assert data['frames'][0] == data['frames'][-1]
    assert data['frames'][1] == data['frames'][4]
    assert data['frames'][2] == data['frames'][5]
    assert data['clean'] == {'scale': 1.045, 'focusX': 50, 'focusY': 42}


@pytest.mark.skipif(not CAMERA_MJS_EXISTS, reason="renderer/camera.mjs unavailable in pruned workspace")
def test_dissolve_keeps_outgoing_camera_and_legacy_no_intent_is_steady() -> None:
    data = _camera_result("""
const scene = {start: 0, end: 9, images: [
  {at: 0, src: 'a.jpg', effect: 'zoom_out', focus: {x: .35, y: .35}},
  {at: 4, src: 'b.jpg', effect: 'fade', focus: {x: .65, y: .58}},
]};
const plan = buildCalmCameraPlan([scene])[0];
const legacy = buildCalmCameraPlan([{start: 0, end: 10, image: 'legacy.jpg'}])[0][0];
console.log(JSON.stringify({
  end: calmCameraStyle(calmCameraFrame(plan[0], 4)),
  outgoing: calmCameraStyle(calmCameraFrame(plan[0], 4.15)),
  incoming: calmCameraStyle(calmCameraFrame(plan[1], 4.15)),
  legacyStart: calmCameraFrame(legacy, 0), legacyEnd: calmCameraFrame(legacy, 10),
}));
""")
    assert data['end'] == data['outgoing']
    assert data['incoming']['transformOrigin'] != data['outgoing']['transformOrigin']
    assert data['legacyStart'] == data['legacyEnd']
    if RENDERER_INDEX_EXISTS:
        renderer = (SYSTEM / 'renderer/index.tsx').read_text()
        assert '...calmCameraStyle(previousCamera, previousEditorial)' in renderer
        assert '...calmCameraStyle(camera, editorial)' in renderer
        assert 'const punchSpring' not in renderer
        assert 'microRot' not in renderer


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


@pytest.mark.skipif(primary_scene_request is None, reason="remote_audio pruned in this worktree")
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


@pytest.mark.skipif(not CAMERA_MJS_EXISTS or not CAPTIONS_MJS_EXISTS, reason="renderer camera.mjs or captions.mjs unavailable in pruned workspace")
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
    scenes = [{'id': f'SC{i:02}', 'setting': 'A study desk at night.', 'shot_type': 'full_scene',
               'narration': 'Gấp sách lại, rồi khoanh chỗ chưa nhớ.'} for i in range(1, 11)]
    assert {'SETTING_MONOTONY_STREAK', 'LOW_VISUAL_SETTING_VARIETY'} == {
        row['type'] for row in check_visual_setting_diversity(scenes)}
    assert check_instructional_manual_loop(scenes)[0]['type'] == 'INSTRUCTIONAL_MANUAL_REPETITION'
    assert check_scene_narrative_progression(scenes)[0]['type'] == 'NARRATIVE_SETTING_PROGRESSION'
    assert check_visual_setting_diversity(scenes[:2]) == []
    assert check_instructional_manual_loop(scenes[:3]) == []

    # Under flexible Feynman formula, progressive character domino frames pass cleanly by default
    assert check_character_breathing_room(scenes) == []
    # Strict mode provides legacy checks if explicitly requested
    strict_breathing = check_character_breathing_room(scenes, strict=True)
    assert any(v['type'] in {'CHARACTER_STREAK_EXCEEDED', 'LOW_CHARACTER_FREE_RATIO'} for v in strict_breathing)
    assert check_character_breathing_room(scenes[:4], strict=True) == []

    verbose_scenes = [{'id': 'SC01', 'setting': 'A very long detailed room description with lots of props and lamps and books everywhere.'}]
    # Relaxed setting threshold allows descriptive canvas notes without hard 10-word rejection
    assert check_setting_description_verbosity(verbose_scenes) == []
    # Strict mode flags verbose settings with constructive guidance
    strict_verbosity = check_setting_description_verbosity(verbose_scenes, strict=True)
    assert strict_verbosity[0]['type'] == 'SETTING_DESCRIPTION_TOO_VERBOSE'
    assert 'guidance' in strict_verbosity[0]
    assert check_setting_description_verbosity(scenes[:2]) == []


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


@pytest.mark.skipif(build_render_request is None, reason="colab_bridge pruned in this worktree")
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
    assert result.stdout.strip() == "['pan_right']"
    assert (tmp_path / 'source/renderer/camera.mjs').is_file()
