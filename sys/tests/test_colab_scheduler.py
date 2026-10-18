"""Real file-lock contention and durable owner tests; no provider traffic."""

from __future__ import annotations

import copy
import json
from unittest.mock import patch

import pytest
from account_budget import Budgets
from colab_bridge import accounts
from colab_bridge.client import Client, ColabError
from colab_bridge.health import audit
from colab_bridge.scheduler import PoolUnavailable, RuntimeScheduler
from remote_audio import configure_accounts
from session_store import Sessions


@pytest.fixture
def pool(tmp_path):
    with patch.object(accounts, "STORE", tmp_path / "profiles"):
        for name in ("one", "two", "alias-one"):
            accounts.add(name)
            (accounts.folder(name) / "token.json").write_text("{}")
        budget = Budgets(tmp_path / "management")
        for name, identity in [("one", "google:one"), ("two", "google:two"), ("alias-one", "google:one")]:
            budget.bind_identity("colab:" + name, identity, "TEST verified fixture")
        yield tmp_path, RuntimeScheduler(tmp_path, store=budget.path.parent, lock_dir=tmp_path / "locks")


def test_independent_controllers_claim_different_accounts_atomically(pool):
    root, first = pool
    second = RuntimeScheduler(root, store=first.store, lock_dir=first.locks)
    with first.claim(["one", "two"], session="tts", request="a", journal=root / "a.json", exact=False) as one:
        with second.claim(
            ["alias-one", "one", "two"], session="render", request="b", journal=root / "b.json", exact=False
        ) as two:
            assert (one, two) == ("one", "two")
            assert accounts.is_session_busy("one", "tts", lock_dir=first.locks)
            assert accounts.is_session_busy("two", "render", lock_dir=first.locks)


def test_unknown_send_keeps_runtime_reserved_after_runner_exits(pool):
    root, manager = pool
    journal = root / "a.json"
    with manager.claim(["one"], session="tts", request="old", journal=journal, exact=True):
        journal.write_text(json.dumps({"phase": "ambiguous", "account": "one", "request_id": "old"}))
    with manager.claim(
        ["alias-one", "two"], session="tts", request="new", journal=root / "b.json", exact=False
    ) as selected:
        assert selected == "two"
    with manager.claim(["one"], session="tts", request="old", journal=journal, exact=True) as selected:
        assert selected == "one"
    with pytest.raises(PoolUnavailable, match="POOL_WAIT"):
        with manager.claim(
            ["alias-one"], session="other", request="new", journal=root / "c.json", exact=True, wait_seconds=0
        ):
            pytest.fail("A duplicate alias must not reuse an unresolved remote session")


def test_pending_journal_from_legacy_runner_is_imported(pool):
    root, manager = pool
    journal = root / "runs/legacy/cache/colab-tts/req/state.json"
    journal.parent.mkdir(parents=True)
    journal.write_text(json.dumps({"phase": "submitted", "account": "one", "request_id": "legacy"}))
    with manager.claim(
        ["alias-one", "two"], session="tts", request="new", journal=root / "new.json", exact=False
    ) as selected:
        assert selected == "two"


def test_identical_request_hash_in_another_job_does_not_bypass_pending_owner(pool):
    root, manager = pool
    old = root/'runs/old/cache/colab-tts/same/state.json'
    old.parent.mkdir(parents=True)
    old.write_text(json.dumps({'phase': 'ambiguous', 'account': 'one', 'request_id': 'same'}))
    with manager.claim(['one', 'two'], session='tts', request='same',
                       journal=root/'runs/new/cache/colab-tts/same/state.json', exact=False) as selected:
        assert selected == 'two'


def test_collection_can_resolve_multiple_old_requests_without_forgetting_other_roots(pool):
    root, manager = pool
    first = root/'old-checkout/a.json'
    first.parent.mkdir()
    with manager.claim(['one'], session='tts', request='a', journal=first, exact=True):
        first.write_text(json.dumps({'phase': 'ambiguous', 'account': 'one', 'request_id': 'a'}))
    second = root/'old-checkout/b.json'
    second.write_text(json.dumps({'phase': 'submitted', 'account': 'one', 'request_id': 'b'}))
    with manager.claim(['one'], session='tts', request='b', journal=second, exact=True, collection_only=True) as selected:
        assert selected == 'one'
    assert first in manager.pending('one', 'new', root/'new.json')
    assert second in manager.pending('one', 'new', root/'new.json')
    with pytest.raises(PoolUnavailable):
        with manager.claim(['one'], session='tts', request='new', journal=root/'new.json', exact=False, wait_seconds=0):
            pytest.fail('Collecting another request must not free an unresolved owner')


def test_global_default_does_not_disable_pool_but_exact_binding_wins():
    cfg = {"colab_tts": {"account": "auto-idle"}}
    selection = {"defaults": {"colab": "colab:one"}}
    configure_accounts(cfg, selection)
    assert cfg["colab_tts"]["account"] == "auto-idle"
    selection["runtime_bindings"] = {"colab": {"account": "colab:two"}}
    configure_accounts(cfg, selection)
    assert cfg["colab_tts"]["account"] == "two"


def test_switching_to_auto_pool_preserves_submitted_pins_and_existing_snapshots(tmp_path):
    sessions = Sessions(tmp_path)
    sessions.path.parent.mkdir()
    bound = {'service': 'colab', 'account': 'colab:one', 'runtime_session': 'original'}
    sessions.path.write_text(json.dumps({'version': 1, 'pool': ['colab:one', 'colab:two'],
        'runtime_bindings': {'colab': bound, 'flow': {'account': 'browser-one'}},
        'pins': {'submitted': {'account': 'colab:one', 'session': 'original'}}}))
    frozen = sessions.snapshot()
    sessions.select(['colab:one', 'colab:two'], {'colab': 'colab:two'}, selection='auto')
    assert frozen['runtime_bindings']['colab'] == bound
    assert 'colab' not in sessions.snapshot()['runtime_bindings']
    assert sessions.read()['pins']['submitted']['account'] == 'colab:one'
    assert sessions.snapshot()['runtime_bindings']['flow']['account'] == 'browser-one'
    assert sessions.read()['runtime_binding_history'][-1]['binding'] == bound


def test_client_pool_claim_obeys_job_allowlist_and_exact_frozen_owner(pool):
    root, manager = pool
    selection = {"pool": ["colab:two"], "defaults": {"colab": "colab:one"}}
    cfg = {
        "colab_tts": {
            "account": "auto-idle",
            "management_session": selection,
            "management_store": str(manager.store),
            "queue_wait_seconds": 0,
        }
    }
    with (
        patch("colab_bridge.client.cli", return_value="/bin/true"),
        patch("colab_bridge.scheduler.RuntimeScheduler", return_value=manager),
    ):
        client = Client(root, cfg)
        with client._execution_slot({}, "request", root / "req.json", "tts"):
            assert client.account == "two"
        bound = copy.deepcopy(cfg)
        bound["colab_tts"]["management_session"] = {
            "pool": ["colab:one"],
            "runtime_bindings": {"colab": {"service": "colab", "account": "colab:one", "runtime_session": "frozen"}},
        }
        exact = Client(root, bound)
        assert not exact.auto_pool
        assert (exact.account, exact.session) == ("one", "frozen")
        with manager.claim(["one"], session="frozen", request="other", journal=root / "other.json", exact=True):
            with pytest.raises(ColabError, match="POOL_WAIT"):
                with exact._execution_slot({}, "request", root / "req.json", "tts"):
                    pytest.fail("A frozen binding must queue, never switch accounts")


def test_recent_unhealthy_kernel_is_not_selected_for_new_work(pool):
    root, manager = pool
    import time

    (manager.store / "colab-health.json").write_text(
        json.dumps(
            {
                "checked_at": time.time(),
                "accounts": [
                    {"id": "one", "state": "kernel_timeout", "server_assignment": {}},
                    {"id": "two", "state": "authenticated_idle", "server_assignment": {}},
                ],
            }
        )
    )
    with manager.claim(
        ["one", "two"], session="tts", request="new", journal=root / "new.json", exact=False
    ) as selected:
        assert selected == "two"


def test_health_distinguishes_duplicate_profiles_and_live_t4_without_allocation(pool):
    _, manager = pool
    observations = {
        "one": {"verified": True, "identity": "google:one", "assignment_count": 1, "named_assignment_active": True},
        "alias-one": {
            "verified": True,
            "identity": "google:one",
            "assignment_count": 1,
            "named_assignment_active": False,
        },
        "two": {"verified": True, "identity": "google:two", "assignment_count": 0},
    }
    with (
        patch.object(accounts, "assignment_state", side_effect=lambda binary, name, session, **kw: observations[name]),
        patch(
            "colab_bridge.health.kernel_health", return_value={"verified": True, "t4": True, "tts_installed": True}
        ) as kernel,
    ):
        report = audit(store=manager.store, check_kernels=True)
    assert report["authenticated_accounts"] == 3
    assert report["verified_identities"] == 2
    assert report["active_assignments"] == 1
    assert report["t4_ready"] == 1
    assert report["unique_authenticated_idle"] == 1
    assert kernel.call_count == 1
    assert report["provider_gpu_capacity"] == "not_tested"
