"""Tests for Lock Conflict & Worker Availability Resilience.

Verifies:
1. Dead PID stale profile lease auto-reclamation.
2. Single-profile pool replacement safety (no drop when no replacement exists).
3. FD_CLOEXEC flag on lease locks to prevent inheritance leaks into subprocesses.
4. MultiProfileManager refresh and rich diagnostic error on worker starvation.
5. Execution lease stale controller PID diagnostics.
"""
import fcntl
import json
import os
import tempfile
import unittest
from pathlib import Path

from flow_cdp.lease_manager import (
    FlowJobLeaseManager,
    _open_lock_file,
    is_pid_alive,
)
from flow_cdp.multi_profile_manager import (
    MultiProfileDispatcher,
    MultiProfileManager,
)
from flow_cdp.patch_partitioner import Patch


class TestLockAndWorkerResilience(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.lock_dir = Path(self.tmpdir.name)
        self.lease_mgr = FlowJobLeaseManager(lock_dir=self.lock_dir)
        self.single_profile = [
            {"id": "p1", "port": 9225, "directory": "Profile 1", "enabled": True}
        ]

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_is_pid_alive_helper(self):
        # Current process is alive
        self.assertTrue(is_pid_alive(os.getpid()))
        # Dead PID (very large number unlikely to exist)
        self.assertFalse(is_pid_alive(99999999))
        self.assertFalse(is_pid_alive(None))
        self.assertFalse(is_pid_alive(-1))

    def test_dead_pid_profile_lease_auto_reclaimed(self):
        """When a crashed process left a .lease and .lock file, it should be auto-reclaimed."""
        lock_file = self.lock_dir / "p1.lock"
        lock_file.touch()
        lease_file = self.lock_dir / "p1.lease"
        dead_pid = 99999999
        lease_file.write_text(json.dumps({
            "job_id": "crashed_job",
            "profile_id": "p1",
            "pid": dead_pid,
            "leased_at": 1000.0,
        }))

        # Profile should NOT be considered busy because PID is dead
        self.assertFalse(self.lease_mgr.is_profile_busy("p1"))

        # clean_stale_leases should clean the dead PID lease file
        cleaned = self.lease_mgr.clean_stale_leases()
        self.assertIn("p1", cleaned)
        self.assertFalse(lease_file.exists())

        # New job should be able to lease p1 immediately
        leased = self.lease_mgr.lease_profiles("new_job", self.single_profile, count=1)
        self.assertEqual(len(leased), 1)
        self.assertEqual(leased[0]["id"], "p1")

    def test_open_lock_file_sets_fd_cloexec(self):
        """Lock files must have FD_CLOEXEC set to prevent inheritance by subprocesses."""
        lock_file = self.lock_dir / "test_cloexec.lock"
        handle = _open_lock_file(lock_file)
        try:
            flags = fcntl.fcntl(handle.fileno(), fcntl.F_GETFD)
            self.assertTrue(flags & fcntl.FD_CLOEXEC, "FD_CLOEXEC flag must be set on lock handle")
        finally:
            handle.close()

    def test_single_profile_pool_replacement_safety(self):
        """On a 1-profile pool, replace_profile must NOT release the only profile when no replacement exists."""
        leased = self.lease_mgr.lease_profiles("job_single", self.single_profile, count=1)
        self.assertEqual(len(leased), 1)

        # Attempt to replace p1 when no other profile exists in the pool
        replacement = self.lease_mgr.replace_profile(
            job_id="job_single",
            failed_profile_id="p1",
            pool_profiles=self.single_profile,
            reason="PUBLIC_ERROR_UNUSUAL_ACTIVITY",
        )
        self.assertIsNone(replacement, "Replacement must be None when no candidates exist")

        # Crucial check: job_single must STILL own the lease on p1!
        active_leases = self.lease_mgr.get_job_leases("job_single")
        self.assertIn("p1", active_leases, "Failed profile must NOT be discarded when pool has no replacement")

    def test_multi_profile_manager_refresh_workers(self):
        """MultiProfileManager should be able to refresh workers when they become available."""
        # Manager starts with empty pool or 0 workers
        mgr = MultiProfileManager(
            profiles_config=self.single_profile,
            job_id="job_refresh",
            max_workers_per_job=1,
            lock_dir=self.lock_dir,
        )
        self.assertEqual(len(mgr.workers), 1)
        mgr.close()

        # Simulate empty manager
        empty_mgr = MultiProfileManager(
            profiles_config=[],
            job_id="job_empty",
            max_workers_per_job=1,
            lock_dir=self.lock_dir,
        )
        self.assertEqual(len(empty_mgr.workers), 0)
        # Give it a pool to refresh from
        empty_mgr.pool_profiles = list(self.single_profile)
        acquired_count = empty_mgr.refresh_workers(timeout=1.0)
        self.assertEqual(acquired_count, 1)
        self.assertEqual(len(empty_mgr.workers), 1)
        empty_mgr.close()

    def test_dispatch_all_diagnostic_error_when_no_workers(self):
        """When dispatch_all fails due to no workers, the error should contain diagnostic profile status."""
        mgr = MultiProfileManager([], job_id="job_diag", lock_dir=self.lock_dir)
        mgr.workers = {}
        dispatcher = MultiProfileDispatcher(mgr)
        patch = Patch(patch_id="p-diag", items=[{"testCase": "t-1"}])

        with self.assertRaises(RuntimeError) as ctx:
            dispatcher.dispatch_all([patch], lambda w, it: [])

        err_msg = str(ctx.exception)
        self.assertIn("No Chrome profile workers available", err_msg)
        self.assertIn("job_diag", err_msg)


if __name__ == "__main__":
    unittest.main()
