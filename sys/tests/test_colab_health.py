"""Unit tests for concurrent Colab account health auditing and server assignment reconciliation."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from account_budget import Budgets
from colab_bridge import accounts, health
from colab_bridge.client import Client, ColabError
from colab_bridge.protocol import stamp


class ColabHealthAndReconcileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = self.root / "profiles"
        self.mgmt = self.root / "management"
        self.patch_store = patch.object(accounts, "STORE", self.store)
        self.patch_store.start()
        self.addCleanup(self.patch_store.stop)

        self.src = self.root / "src"
        self.src.mkdir()
        (self.src / "token.json").write_text('{"refresh_token": "tok"}')
        (self.src / "sessions.json").write_text("{}")

        for i in range(1, 5):
            accounts.add(f"account-0{i}", self.src)

    def test_concurrent_health_audit_detects_duplicates_and_t4_readiness(self) -> None:
        def fake_assignment_state(binary, name, session, timeout=30, refresh_auth=False):
            if name in ("account-01", "account-04"):
                # Duplicate Google identity across two profiles
                return {
                    "verified": True,
                    "identity": "google:dup-user",
                    "assignment_count": 1,
                    "named_assignment_active": name == "account-01",
                }
            if name == "account-02":
                return {
                    "verified": True,
                    "identity": "google:idle-user",
                    "assignment_count": 0,
                    "named_assignment_active": False,
                }
            return {"verified": False, "reason": "login_required"}

        def fake_kernel_health(binary, name, session, timeout=25, **kwargs):
            return {"verified": True, "t4": True, "tts_installed": True}

        with patch.object(accounts, "assignment_state", side_effect=fake_assignment_state), \
             patch.object(health, "kernel_health", side_effect=fake_kernel_health):
            report = health.audit(
                session="video-pilot-tts",
                refresh_auth=True,
                check_kernels=True,
                workers=4,
                store=self.mgmt,
            )

        self.assertEqual(report["total_accounts"], 4)
        self.assertEqual(report["verified_identities"], 2)
        self.assertEqual(report["authenticated_accounts"], 3)
        self.assertEqual(report["t4_ready"], 1)
        self.assertEqual(report["unique_authenticated_idle"], 1)
        acc4 = next(x for x in report["accounts"] if x["id"] == "account-04")
        self.assertEqual(acc4.get("duplicate_of"), "account-01")
        self.assertTrue((self.mgmt / "colab-health.json").is_file())

    def test_reconcile_releases_ambiguous_allocation_when_server_has_zero_assignments(self) -> None:
        budgets = Budgets(self.mgmt)
        alias = "colab:account-01"
        identity = "google:user-01"
        budgets.bind_identity(alias, identity, "ev-init")
        t0 = 1700000000.0
        budgets.allocated(alias, "video-pilot-tts", device="T4", at=t0, evidence="ev-alloc")

        journal = budgets.path.parent / ("allocation-" + stamp(identity) + ".json")
        journal.write_text(
            json.dumps(
                {
                    "phase": "ambiguous",
                    "account": "account-01",
                    "session": "video-pilot-tts",
                    "allocation_started_at": t0,
                }
            )
        )

        cfg = {
            "colab_tts": {
                "enabled": True,
                "account": "account-01",
                "session": "video-pilot-tts",
                "management_store": str(self.mgmt),
            }
        }
        with patch("colab_bridge.client.cli", return_value="/bin/true"):
            client = Client(self.root, cfg)

        with patch.object(
            client,
            "_assignment_state",
            return_value={
                "verified": True,
                "identity": identity,
                "assignment_count": 0,
                "named_assignment_active": False,
                "source": "colab_server",
            },
        ):
            res = client.reconcile()

        self.assertEqual(res["state"], "released")
        saved_journal = json.loads(journal.read_text())
        self.assertEqual(saved_journal["phase"], "released")
        self.assertEqual(budgets.snapshot(alias)["allocated_sessions"], [])

    def test_reconcile_confirms_allocated_t4_when_named_session_is_active(self) -> None:
        budgets = Budgets(self.mgmt)
        alias = "colab:account-02"
        identity = "google:user-02"
        budgets.bind_identity(alias, identity, "ev-init")
        t0 = 1700000000.0

        journal = budgets.path.parent / ("allocation-" + stamp(identity) + ".json")
        journal.parent.mkdir(parents=True, exist_ok=True)
        journal.write_text(
            json.dumps(
                {
                    "phase": "submitted",
                    "account": "account-02",
                    "session": "video-pilot-tts",
                    "allocation_started_at": t0,
                }
            )
        )

        cfg = {
            "colab_tts": {
                "enabled": True,
                "account": "account-02",
                "session": "video-pilot-tts",
                "management_store": str(self.mgmt),
            }
        }
        with patch("colab_bridge.client.cli", return_value="/bin/true"):
            client = Client(self.root, cfg)

        with patch.object(
            client,
            "_assignment_state",
            return_value={
                "verified": True,
                "identity": identity,
                "assignment_count": 1,
                "named_assignment_active": True,
                "source": "colab_server",
            },
        ), patch.object(client, "exec", return_value='VP_GPU="Tesla T4"\n'):
            res = client.reconcile()

        self.assertEqual(res["device"], "Tesla T4")
        self.assertEqual(json.loads(journal.read_text())["phase"], "allocated")
        self.assertEqual(len(budgets.snapshot(alias)["allocated_sessions"]), 1)

    def test_start_refuses_double_allocation_when_journal_is_pending(self) -> None:
        budgets = Budgets(self.mgmt)
        alias = "colab:account-01"
        identity = "google:user-01"
        budgets.bind_identity(alias, identity, "ev-init")
        journal = budgets.path.parent / ("allocation-" + stamp(identity) + ".json")
        journal.parent.mkdir(parents=True, exist_ok=True)
        journal.write_text(json.dumps({"phase": "submitted", "account": "account-01", "session": "video-pilot-tts"}))

        cfg = {
            "colab_tts": {
                "enabled": True,
                "account": "account-01",
                "session": "video-pilot-tts",
                "management_store": str(self.mgmt),
            }
        }
        with patch("colab_bridge.client.cli", return_value="/bin/true"):
            client = Client(self.root, cfg)

        with self.assertRaisesRegex(ColabError, "COLAB_ALLOCATION_PENDING"):
            client.start()


if __name__ == "__main__":
    unittest.main()
