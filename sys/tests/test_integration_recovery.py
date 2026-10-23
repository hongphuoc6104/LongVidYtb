"""Regression checks at the production entry boundaries; providers are isolated."""
import asyncio
import copy
import re
from unittest.mock import AsyncMock, patch

import adapters
import execution
import pytest
import test_colab_tts as audio_fixtures
import test_execution_v4 as execution_fixtures

from pilot import read, write


@pytest.fixture
def job():
    fixture = execution_fixtures.ExecutionTests()
    fixture.setUp()
    fixture.new('auto')
    try:
        yield fixture
    finally:
        fixture.doCleanups()


def test_audio_and_render_use_frozen_configuration_after_global_edit(job):
    initial = adapters.config(job.p, job.job)
    changed = read(job.root / 'config.json')
    changed['audio_lufs'] = -30
    changed['colab_tts']['batch_size'] = 1
    write(job.root / 'config.json', changed)
    actual = adapters.config(job.p, job.job)
    assert actual == initial
    actual['colab_tts']['batch_size'] = 8
    assert adapters.config(job.p, job.job) == initial
    assert adapters.config(job.p)['audio_lufs'] == -30


def test_core_records_actual_sources_and_distinguishes_technical_completion(job):
    job.author_inputs()
    with job.providers():
        state = execution.advance(job.p, job.job)
    assert state['complete']
    for stage in state['checkpoints']:
        assert stage['technical_complete']
        assert stage['quality_approved'] is False
    receipt = read(job.p.job(job.job) / 'revisions/audio/1/runtime.json')
    assert receipt['source_sha256']
    assert receipt['config_sha256']
    assert receipt['completed_at'] >= receipt['started_at']


def test_provider_rejection_does_not_change_prompt_or_resubmit():
    from flow_cdp.cdp_direct_client import DirectCDPProfileSession
    session = DirectCDPProfileSession.__new__(DirectCDPProfileSession)
    session.project_id = 'fixture-project'
    session.name = 'fixture-profile'
    session.evaluate = AsyncMock(return_value={'status': 200, 'text': 'fixture-response'})
    with patch('flow_cdp.cdp_direct_client.flow_rpc.image_request', return_value='fixture-wire') as wire, \
         patch('flow_cdp.cdp_direct_client.flow_rpc.first_payload', side_effect=RuntimeError('PUBLIC_ERROR_UNSAFE_GENERATION')):
        with pytest.raises(RuntimeError, match='PUBLIC_ERROR_UNSAFE_GENERATION'):
            asyncio.run(session.generate_image('Keep the approved authored composition.'))
    assert wire.call_count == 1
    assert wire.call_args.kwargs['prompt'] == 'Keep the approved authored composition.'
    assert session.evaluate.await_count == 1


def test_editorial_questions_survive_standard_content_export():
    from content.research_story_architect import build_brief_v3, create_demo_trial_topic
    topic = create_demo_trial_topic()
    editorial = {'primary_question': 'Khi nào một lời giải thích thực sự giúp ta hiểu?'}
    topic.human_editorial = copy.deepcopy(editorial)
    brief = build_brief_v3(topic)
    assert brief['human_editorial'] == editorial
    topic.human_editorial['primary_question'] = 'changed'
    assert brief['human_editorial'] == editorial


@pytest.mark.parametrize('reconciliation_fails', [False, True])
def test_unsubmitted_tts_reconciles_missing_session_without_duplicate_send(reconciliation_fails):
    from colab_bridge.client import Client, ColabError
    fixture = audio_fixtures.ProtocolTests()
    fixture.setUp()
    try:
        with patch('colab_bridge.client.cli', return_value='/bin/true'):
            client = Client(fixture.root, fixture.cfg)
        mkdir_attempts = []
        submissions = []

        def call(*args, **kwargs):
            code = kwargs.get('code', '')
            if '.mkdir(' in code:
                mkdir_attempts.append(code)
                if len(mkdir_attempts) == 1:
                    raise ColabError('COLAB_SESSION_NOT_FOUND: fixture-session')
            if '.run(' in code:
                submissions.append(code)
            marker = re.search(r'VP_EXEC_OK_[0-9a-f]+', code)
            return marker.group() if marker else ''

        def download(remote, folder, req):
            audio_fixtures.fake_result(folder / 'result', req)

        with patch.object(client, 'ensure_authenticated'), patch.object(client, 'call', side_effect=call), \
             patch.object(client, '_download', side_effect=download), patch.object(client, '_ready') as ready, \
             patch.object(client, 'reconcile', side_effect=ColabError('assignment unknown') if reconciliation_fails else None) as reconcile:
            if reconciliation_fails:
                with pytest.raises(ColabError, match='assignment unknown'):
                    client.synthesize(fixture.req, fixture.root / 'out', fixture.root / 'cache')
            else:
                client.synthesize(fixture.req, fixture.root / 'out', fixture.root / 'cache')
                result = read(fixture.root / 'out/tts-result.json')
                assert result['segments'][0]['scene_id'] == fixture.req['segments'][0]['scene_id']
            assert reconcile.call_count == 1
            assert len(submissions) == (0 if reconciliation_fails else 1)
            assert ready.call_count == (0 if reconciliation_fails else 1)
    finally:
        fixture.doCleanups()


def test_audio_multi_shard_dispatch_and_support_files_validation(tmp_path):
    from colab_bridge import parallel_audio
    from colab_bridge.client import Client, ColabError

    fixture = audio_fixtures.ProtocolTests()
    fixture.setUp()
    try:
        with patch('colab_bridge.client.cli', return_value='/bin/true'):
            client = Client(fixture.root, fixture.cfg)
        bad_req = copy.deepcopy(fixture.req)
        bad_req['support_files'] = [{
            'name': 'audio_mastering.py',
            'local_path': str(fixture.root / 'missing_audio_mastering.py'),
            'sha256': '0' * 64,
        }]
        with pytest.raises(ColabError, match='COLAB_SUPPORT_CHANGED'):
            client.synthesize(bad_req, fixture.root / 'out_bad', fixture.root / 'cache')

        multi_req = copy.deepcopy(fixture.req)
        base_seg = copy.deepcopy(multi_req['segments'][0])
        base_item = copy.deepcopy(multi_req['items'][0])
        multi_req['segments'] = []
        multi_req['items'] = []
        for idx in range(6):
            seg = copy.deepcopy(base_seg)
            seg['scene_id'] = f'SC{idx + 1:02d}'
            seg['text'] = f'Câu thử nghiệm thứ {idx + 1}.'
            seg['items'] = [idx]
            item = copy.deepcopy(base_item)
            item['scene_id'] = seg['scene_id']
            item['text'] = seg['text']
            multi_req['segments'].append(seg)
            multi_req['items'].append(item)

        shards = parallel_audio.request_shards(multi_req, scenes_per_shard=2)
        assert len(shards) == 3
        shard_results = []
        for idx, shard in enumerate(shards):
            shard_out = tmp_path / f'shard_{idx}'
            audio_fixtures.fake_result(shard_out, shard)
            shard_results.append({
                'index': idx,
                'request_id': shard['request_id'],
                'out': str(shard_out),
            })
        assembled = parallel_audio.prepare_assembly(multi_req, shard_results, tmp_path / 'prepared')
        assert len(assembled['prepared_audio']) >= 6
        prepared_meta = read(tmp_path / 'prepared/prepared-tts-result.json')
        assert [s['scene_id'] for s in prepared_meta['segments']] == [f'SC{i:02d}' for i in range(1, 7)]
    finally:
        fixture.doCleanups()


def test_images_profile_exact_match_and_1_7_0_character_contract(tmp_path):
    from flow_cdp import bridge as flow_bridge

    p1_dir = tmp_path / 'chrome' / 'Profile 1'
    p10_dir = tmp_path / 'chrome' / 'Profile 10'
    p1_dir.mkdir(parents=True)
    p10_dir.mkdir(parents=True)

    base_dir = tmp_path / 'attempt_base'
    dl_dir = base_dir / 'download'
    dl_dir.mkdir(parents=True)
    base_img = dl_dir / 'base.png'
    base_img.write_bytes(b'fakepng')
    write(base_dir / 'owner.json', {'profile_path': str(p1_dir)})

    profiles_cfg = [
        {'id': 'profile-10', 'user_data_dir': str(tmp_path / 'chrome'), 'directory': 'Profile 10', 'port': 9231},
        {'id': 'profile-01', 'user_data_dir': str(tmp_path / 'chrome'), 'directory': 'Profile 1', 'port': 9222},
    ]
    captured = {}

    def fake_batch(specs, timeout=None, before_submit=None, profile_id='', use_multi_profile=True):
        captured['profile_id'] = profile_id
        captured['specs'] = specs
        return [{'path': str(base_img), 'sha256': 'abc', 'profile_id': profile_id}]

    with patch.object(flow_bridge, '_config', return_value={'flow_cdp_profiles': profiles_cfg, 'flow_queue_trial_enabled': True}), \
         patch.object(flow_bridge, 'require_queue_acceptance'), \
         patch.object(flow_bridge, 'generate_cdp_batch', side_effect=fake_batch):
        flow_bridge.generate_cdp_image(
            prompt='Flat 2D hand-drawn explainer.',
            base_ref_path=base_img,
            base_media_id='media-123',
            out_dir=tmp_path / 'out',
            use_character_ref=False,
        )
    assert captured['profile_id'] == 'profile-01'


def test_video_worker_records_granular_stage_timings_and_remotion_concurrency(tmp_path):
    import test_remote_render as render_fixtures
    from colab_bridge.job_protocol import build_render_request, bundle
    from colab_bridge.job_worker import run

    folder = tmp_path / 'video_job'
    folder.mkdir()
    (folder / 'image.png').write_bytes(b'fixture')
    (folder / 'audio.wav').write_bytes(b'fixture')
    brief = {
        'aspect_ratio': '9:16',
        'outputs': [
            {'aspect_ratio': '9:16', 'language': 'en', 'subtitles': True, 'voice': 'VietNarrator', 'speed': 1.0}
        ],
    }
    content = {
        'schema_version': '3.0',
        'scenes': [
            {
                'id': 'SC01',
                'title': 'A question',
                'narration_en': 'I see a predator.',
                'beats': [
                    {
                        'id': 'BT01',
                        'image_id': 'IM01',
                        'anchor': {'en': {'quote': 'I', 'occurrence': 1}},
                        'effect': 'hold',
                        'focus': {'x': 0.5, 'y': 0.5},
                    }
                ],
            }
        ],
    }
    images = {'items': [{'scene_id': 'SC01', 'image_id': 'IM01', 'ratio': '9:16', 'path': 'image.png'}]}
    track = {
        'language': 'en',
        'voice': 'VietNarrator',
        'speed': 1.0,
        'wav': 'audio.wav',
        'duration': 5.0,
        'segments': [
            {
                'scene_id': 'SC01',
                'text': 'I see a predator.',
                'start': 0.0,
                'end': 5.0,
                'content_end': 4.5,
                'path': 'audio.wav',
            }
        ],
    }
    audio = dict(track, tracks={'en': track})
    req = build_render_request(render_fixtures.ROOT, brief, content, images, audio, lambda x: folder / x)
    target = folder / 'input.zip'
    bundle(req, target)
    chrome = folder / 'chrome'
    chrome.touch()

    def remote_run(argv, **kwargs):
        if argv[0] == 'node':
            out = folder / 'output'
            (out / 'video.mp4').write_bytes(b'\0\0\0\x18ftypisom' + b'fixture')
            write(out / 'layout.json', {
                'passed': True,
                'concurrency': 6,
                'remotion_concurrency': 2,
                'host_cpus': 2,
                'timings': {
                    'bundle_seconds': 1.2,
                    'layout_seconds': 0.5,
                    'stills_seconds': 0.8,
                    'render_media_seconds': 10.4,
                },
            })
            (out / 'SC01.png').write_bytes(b'stillfixture')

    def probe(argv, **kwargs):
        if argv[0] == 'node':
            return str(chrome) + '\n'
        if argv[0] == 'nvidia-smi':
            return 'fixture Tesla T4\n'
        return '{"format": {"duration": "5.0"}, "streams": [{"codec_type": "video", "codec_name": "h264", "width": 1080, "height": 1920}, {"codec_type": "audio", "codec_name": "aac"}]}'

    with patch('colab_bridge.job_worker.subprocess.run', side_effect=remote_run), \
         patch('colab_bridge.job_worker.subprocess.check_output', side_effect=probe):
        report = run(target, folder / 'output', req['request_id'], req['worker_sha256'])

    assert report['remotion_concurrency'] == 2
    assert 'stage_timings' in report
    for key in ('unpack_seconds', 'timeline_seconds', 'runtime_setup_seconds', 'render_seconds', 'ffprobe_seconds'):
        assert key in report['stage_timings']
        assert report['stage_timings'][key] >= 0.0


def test_content_visual_quality_ssot_and_nguech_ngoac_flat_2d_compliance():
    import content.visual_quality as content_vq
    import flow_prompts
    import scripts.visual_quality as scripts_vq
    from content.research_story_architect import build_brief_v3, build_content_v3
    from tools.build_ai_sycophancy_9x16 import build_topic
    from visual_style import STYLE_DESCRIPTION

    assert content_vq.check_visual_setting_diversity is scripts_vq.check_visual_setting_diversity
    assert content_vq.check_instructional_manual_loop is scripts_vq.check_instructional_manual_loop

    topic = build_topic()
    assert topic.style == STYLE_DESCRIPTION
    brief = build_brief_v3(topic)
    assert brief.get('human_editorial') and 'topic_dilemmas' in brief['human_editorial']

    content_v3 = build_content_v3(topic, brief, 'test-hash')
    pin = flow_prompts.freeze('NanoBanana2', '1.7.0')
    char_compiled = flow_prompts.compile_pinned(
        pin,
        'reference',
        {
            'description': 'Minh in flat terracotta shirt.',
            'aspect_ratio': '9:16',
            'has_character': True,
        },
    )
    assert STYLE_DESCRIPTION in char_compiled['prompt']

    labeled_beats = 0
    fake_ref = {'media_id': '11111111-2222-3333-4444-555555555555', 'sha256': 'a' * 64}
    for scene in content_v3['scenes']:
        for img in scene['images']:
            assert 'pendant light' not in img.get('setting', '').lower()
            assert 'lamplight' not in img.get('setting', '').lower()
            assert 'glowing' not in img.get('description', '').lower()
            assert 'glow' not in str(img.get('change', '')).lower()
            if img.get('visible_text'):
                labeled_beats += 1
            is_var = bool(img.get('based_on')) or img.get('shot_type') == 'variation'
            has_char = bool(img.get('characters'))
            data = {
                'description': img['description'],
                'setting': img.get('setting'),
                'action': img.get('action'),
                'shot_type': img.get('shot_type', 'full_scene'),
                'aspect_ratio': '9:16',
                'allowed_text': list(img.get('visible_text') or []),
                'has_character': has_char,
                'character_free': not has_char,
            }
            if has_char:
                data['character_reference'] = fake_ref
            if is_var:
                data['base_reference'] = fake_ref
                data['preserve'] = [img['preserve']] if isinstance(img.get('preserve'), str) else list(img.get('preserve') or ['Keep frame'])
                data['change'] = [img['change']] if isinstance(img.get('change'), str) else list(img.get('change') or ['Update pose'])
            compiled = flow_prompts.compile_pinned(
                pin,
                'variation' if is_var else 'scene',
                data,
            )
            assert STYLE_DESCRIPTION in compiled['prompt']
    assert labeled_beats >= 7


def test_core_review_approval_and_selective_stage_invalidation():
    import workflow

    fixture = execution_fixtures.ExecutionTests()
    fixture.setUp()
    try:
        fixture.new()
        execution.author(fixture.p, fixture.job, 'outline', fixture.outline(), 'TEST author')
        step = execution.advance(fixture.p, fixture.job)
        assert (step['phase'], step['action']) == ('outline', 'review')
        cp0 = next(c for c in step['checkpoints'] if c['phase'] == 'outline')
        assert cp0['technical_complete'] is True
        assert cp0['quality_approved'] is False
        fixture.approve('outline')
        cp0_after = next(c for c in execution.observe(fixture.p, fixture.job)['checkpoints'] if c['phase'] == 'outline')
        assert cp0_after['quality_approved'] is True

        execution.author(fixture.p, fixture.job, 'dialogue', fixture.content, 'TEST author')
        with fixture.providers():
            for phase in ('dialogue', 'audio', 'images', 'video'):
                step = workflow.advance(fixture.p, fixture.job)
                assert (step['phase'], step['action']) == (phase, 'review')
                cp = next(c for c in step['checkpoints'] if c['phase'] == phase)
                assert cp['technical_complete'] is True
                assert cp['quality_approved'] is False
                fixture.approve(phase)
                cp_after = next(c for c in execution.observe(fixture.p, fixture.job)['checkpoints'] if c['phase'] == phase)
                assert cp_after['quality_approved'] is True
            assert execution.advance(fixture.p, fixture.job)['complete'] is True

        rows = fixture.p.rows(fixture.job)
        assert rows['audio']['revision'] == 1
        assert rows['images']['revision'] == 1
    finally:
        fixture.doCleanups()


