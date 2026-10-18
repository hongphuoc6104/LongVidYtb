"""Offline load probes for terminal Flow failures; never connect to a browser."""
from __future__ import annotations

import threading
import time
from typing import Any

import pytest

from flow_cdp.multi_profile_manager import MultiProfileDispatcher, MultiProfileManager
from flow_cdp.patch_partitioner import Patch


def profiles(count: int) -> list[dict[str, Any]]:
    return [{'id': f'fixture-{index}', 'port': 1, 'directory': 'Offline'} for index in range(count)]


def patches(count: int) -> list[Patch]:
    return [Patch(patch_id=f'patch-{index}', items=[{'testCase': f'shot-{index}'}]) for index in range(count)]


@pytest.mark.parametrize('reason', [
    'PUBLIC_ERROR_UNUSUAL_ACTIVITY', 'CAPTCHA', 'HTTP 429', 'HTTP 401',
    'quota exceeded', 'socket disconnected after send',
])
def test_terminal_error_stops_every_unstarted_patch(reason: str) -> None:
    manager = MultiProfileManager(profiles(1), cooldown_seconds=0)
    work = patches(100)
    calls = []

    def refused(worker: Any, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        calls.append(items[0]['testCase'])
        raise RuntimeError(reason)

    with pytest.raises(RuntimeError, match=reason):
        MultiProfileDispatcher(manager).dispatch_all(work, refused, max_concurrency=1)
    assert calls == ['shot-0']
    assert all(item.status == 'pending' and item.retry_count == 0 for item in work[1:])
    assert manager.workers['fixture-0'].failure_count == 1


def test_already_running_success_is_collected_after_another_worker_fails() -> None:
    manager = MultiProfileManager(profiles(2), cooldown_seconds=0)
    work = patches(20)
    both_running = threading.Barrier(2)
    let_finish = threading.Event()
    calls = []

    def execute(worker: Any, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        identity = items[0]['testCase']
        calls.append(identity)
        both_running.wait(timeout=5)
        if identity == 'shot-0':
            let_finish.set()
            raise RuntimeError('PUBLIC_ERROR_UNUSUAL_ACTIVITY')
        assert let_finish.wait(timeout=5)
        time.sleep(0.02)
        return [{'media_id': 'offline-result', 'request_id': identity}]

    with pytest.raises(RuntimeError, match='FLOW_PARTIAL_BATCH'):
        MultiProfileDispatcher(manager).dispatch_all(work, execute, max_concurrency=2)
    assert sorted(calls) == ['shot-0', 'shot-1']
    assert work[1].completed_items['shot-1']['media_id'] == 'offline-result'
    assert all(item.status == 'pending' for item in work[2:])


def test_large_queue_serializes_each_profile_and_keeps_all_results() -> None:
    manager = MultiProfileManager(profiles(3))
    lock = threading.Lock()
    active: set[str] = set()
    collision = []
    used: set[str] = set()

    def execute(worker: Any, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        with lock:
            if worker.profile_id in active:
                collision.append(worker.profile_id)
            active.add(worker.profile_id)
            used.add(worker.profile_id)
        time.sleep(0.0001)
        with lock:
            active.remove(worker.profile_id)
        return [{'request_id': items[0]['testCase']}]

    results = MultiProfileDispatcher(manager).dispatch_all(patches(1000), execute, max_concurrency=24)
    assert len(results) == len({item['request_id'] for item in results}) == 1000
    assert collision == []
    assert used == set(manager.workers)


def test_fully_unsent_failure_keeps_original_error_and_does_not_advance_queue() -> None:
    manager = MultiProfileManager(profiles(1), cooldown_seconds=0)
    work = patches(10)
    error = RuntimeError('Invalid local contract')
    error.generation_submitted = False

    def invalid(worker: Any, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        raise error

    with pytest.raises(RuntimeError) as caught:
        MultiProfileDispatcher(manager).dispatch_all(work, invalid, max_concurrency=1)
    assert caught.value is error
    assert all(item.status == 'pending' for item in work[1:])


