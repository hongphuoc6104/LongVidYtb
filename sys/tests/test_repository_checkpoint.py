"""Offline regressions for the consolidated repository checkpoint."""
from __future__ import annotations

import asyncio
import importlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from account_budget import Budgets
from content_contract import validate_brief, validate_content
from flow_cdp import bridge
from flow_cdp.cdp_direct_client import PROFILES, DirectCDPProfileSession
from flow_cdp.lease_manager import FlowJobLeaseManager
from flow_cdp.multi_profile_manager import MultiProfileDispatcher
from flow_cdp.patch_partitioner import Patch
from tools.research_story_architect import (
    ResearchedTopic,
    build_brief_v3,
    build_content_v3,
    compute_brief_hash,
    write_production_package,
)
from visual_pacing import smooth_interpolated_beats
from visual_style import STYLE_DESCRIPTION

from pilot import ROOT, Blocked


def test_direct_error_cannot_rewrite_submission_journal(tmp_path: Path) -> None:
    folder = tmp_path / 'attempt'
    (folder / 'download').mkdir(parents=True)
    record = folder / 'request.json'
    record.write_text(json.dumps({'state': 'submitted', 'identity': {'request': 'original'}}))
    before = record.read_bytes()
    specs = [{'testCase': 'one', 'outDir': str(folder / 'download')}]
    with patch.object(bridge, 'SYS_ROOT', tmp_path), patch.object(bridge, 'require_queue_acceptance'), \
            patch.object(bridge, 'ensure_connected', return_value={}), \
            patch.object(bridge, 'get_socket_path', return_value=tmp_path / 'missing.sock'), \
            patch.object(bridge, '_execute_via_cdp_direct', side_effect=RuntimeError('socket lost after send')):
        with pytest.raises(RuntimeError, match='after send'):
            bridge._execute_sub_batch(specs)
    assert record.read_bytes() == before


@pytest.mark.parametrize('message', ['socket lost after send', 'CAPTCHA', 'PUBLIC_ERROR_UNUSUAL_ACTIVITY'])
def test_unknown_or_provider_refusal_does_not_rotate_or_resubmit(message: str) -> None:
    manager = MagicMock()
    manager.job_id = 'owned-job'
    worker = SimpleNamespace(profile_id='p1', port=9225)
    manager.acquire_healthy_worker.return_value = worker
    dispatcher = MultiProfileDispatcher(manager)
    item = Patch(patch_id='one', items=[{'testCase': 'one'}])
    execute = MagicMock(side_effect=RuntimeError(message))
    with pytest.raises(RuntimeError, match=message):
        dispatcher.execute_patch_with_failover(item, execute)
    assert execute.call_count == 1
    manager.replace_worker_for_job.assert_not_called()
    assert item.retry_count == 0


@pytest.mark.parametrize('batch', [False, True])
def test_provider_refusal_never_reexecutes_rpc(batch: bool) -> None:
    session = DirectCDPProfileSession(PROFILES[0])
    session.evaluate = AsyncMock(return_value={'status': 403, 'text': 'provider-refusal-fixture'})
    session.connect = AsyncMock()
    with patch('flow_cdp.cdp_direct_client.flow_rpc.first_payload', side_effect=ValueError('CAPTCHA')):
        with pytest.raises(RuntimeError, match='FLOW_PROVIDER_BLOCKED'):
            asyncio.run(session.generate_images_batch(['A scene']) if batch else session.generate_image('A scene'))
    assert session.evaluate.await_count == 1
    session.connect.assert_not_awaited()


def test_all_disabled_profiles_return_without_waiting(tmp_path: Path) -> None:
    manager = FlowJobLeaseManager(lock_dir=tmp_path)
    with patch('flow_cdp.lease_manager.time.sleep') as wait:
        profiles = manager.lease_profiles('job', [{'id': 'p1', 'enabled': False}])
    assert profiles == []
    wait.assert_not_called()


def test_bound_job_uses_only_its_owned_profile_and_serial_dispatch(tmp_path: Path) -> None:
    profiles = [{'id': f'p{number}', 'user_data_dir': str(tmp_path), 'directory': f'Profile {number}'} for number in [1, 2]]
    bound = str(tmp_path / 'Profile 2')
    pilot = MagicMock()
    manager = MagicMock()
    manager.workers = {'p2': object()}
    with patch.object(bridge, '_config', return_value={'flow_cdp_profiles': profiles}), \
            patch('pilot.Pilot', return_value=pilot), patch('execution.is_job', return_value=True), \
            patch('execution.settings', return_value={'management_session': {'runtime_bindings': {'flow': {'target': {'profile_path': bound}}}}}), \
            patch.object(bridge, 'MultiProfileManager', return_value=manager) as pool, \
            patch.object(bridge, 'MultiProfileDispatcher') as dispatcher:
        bridge.generate_cdp_batch([{'testCase': 'one', 'jobId': 'owned', 'prompt': 'A scene.'}])
    assert pool.call_args.kwargs['profiles_config'] == [profiles[1]]
    assert pool.call_args.kwargs['max_workers_per_job'] == 1
    assert dispatcher.return_value.dispatch_all.call_args.kwargs['max_concurrency'] == 1
    pilot.db.close.assert_called_once()


def test_partial_dispatch_cannot_claim_the_entire_batch_was_unsent() -> None:
    manager = MagicMock()
    manager.workers = {'p1': object(), 'p2': object()}
    dispatcher = MultiProfileDispatcher(manager)
    patches = [Patch(patch_id=str(index), items=[{'testCase': str(index)}]) for index in range(2)]

    def execute(item: Patch, executor: object) -> list[dict]:
        if item.patch_id == '0':
            return [{'path': 'collected-fixture'}]
        error = Blocked('Proven pre-send failure for this patch only')
        error.generation_submitted = False
        raise error

    with patch.object(dispatcher, 'execute_patch_with_failover', side_effect=execute):
        with pytest.raises(RuntimeError, match='FLOW_PARTIAL_BATCH') as caught:
            dispatcher.dispatch_all(patches, MagicMock())
    assert getattr(caught.value, 'generation_submitted', None) is not False


def test_batch_budget_is_bounded_and_duplicate_aliases_are_rejected(tmp_path: Path) -> None:
    ledger = Budgets(tmp_path)
    ledger.bind_identity('a', 'same-provider', 'fixture identity')
    ledger.bind_identity('alias', 'same-provider', 'fixture alias')
    ledger.flow_submit_many('a', 'image', [('one', 100)], evidence='fixture send')
    with pytest.raises(ValueError, match='budget'):
        ledger.flow_submit_many('alias', 'image', [('two', 1)], evidence='fixture overflow')
    with pytest.raises(ValueError, match='Existing request'):
        ledger.flow_submit_many('alias', 'registration', [('one', 1)], evidence='fixture duplicate')
    assert ledger.snapshot('a')['flow']['image']['slots'] == 100


def test_pacing_keeps_measured_anchors_and_records_adjusted_estimates() -> None:
    measured = [{'at': at, 'timing_method': 'acoustic_word_timestamps'} for at in [0., 1., 7., 12.]]
    before = [item['at'] for item in measured]
    smooth_interpolated_beats(measured, 0., 20.)
    assert [item['at'] for item in measured] == before
    estimated = [{'at': at, 'timing_method': 'narration_anchor_interpolated'} for at in [0., 4.5, 4.6, 8.]]
    smooth_interpolated_beats(estimated, 16., 27.)
    assert estimated[1]['at'] != 4.5
    assert estimated[1]['original_at'] == 4.5
    assert all(item['timing_method'] == 'narration_anchor_interpolated' for item in estimated)


def test_package_export_cannot_overwrite_active_run(tmp_path: Path) -> None:
    (tmp_path / 'revisions').mkdir()
    source = tmp_path / 'brief.json'
    source.write_text('existing active job input')
    topic = ResearchedTopic(topic='A question', audience='Students', goal='Understand', video_type='explainer')
    with pytest.raises(ValueError, match='ACTIVE_JOB_DESTINATION'):
        write_production_package(tmp_path, topic)
    assert source.read_text() == 'existing active job input'


@pytest.mark.parametrize(('module', 'factory'), [
    ('build_collectors_fallacy_jobs', 'build_topic_16x9'),
    ('build_collectors_fallacy_jobs', 'build_topic_9x16'),
    ('build_adversarial_ai_package', 'build_topic_16x9'),
    ('build_adversarial_ai_package', 'build_topic_9x16'),
    ('build_reviewer_2_jobs', 'build_topic_16x9'),
    ('build_reviewer_2_jobs', 'build_topic_9x16'),
    ('build_feynman_16x9_job', 'build_topic'),
])
def test_source_factories_build_valid_light_style_contracts(module: str, factory: str) -> None:
    topic = getattr(importlib.import_module('tools.' + module), factory)()
    brief = build_brief_v3(topic)
    digest = compute_brief_hash(brief)
    content = build_content_v3(topic, brief, digest)
    validate_brief(ROOT, brief)
    validate_content(ROOT, brief, 1, digest, content)
    assert brief['style'] == STYLE_DESCRIPTION
    assert content['style'] == STYLE_DESCRIPTION
