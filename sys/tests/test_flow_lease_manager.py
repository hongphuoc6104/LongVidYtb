"""Unit tests for FlowJobLeaseManager and MultiProfileManager multi-job isolation."""
import tempfile
import unittest
from pathlib import Path

from flow_cdp.lease_manager import FlowJobLeaseManager
from flow_cdp.multi_profile_manager import MultiProfileManager


class TestFlowJobLeaseManager(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.lock_dir = Path(self.tmpdir.name)
        self.lease_mgr = FlowJobLeaseManager(lock_dir=self.lock_dir)
        self.profiles = [
            {"id": f"profile_{i}", "port": 9220 + i, "directory": f"Profile {i}", "enabled": True}
            for i in range(1, 11)  # 10 profiles in pool
        ]

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_job_quota_limited_to_max_profiles(self):
        # Job A requests 5 profiles, but max is 2
        leased = self.lease_mgr.lease_profiles("job_A", self.profiles, count=5, max_profiles_per_job=2)
        self.assertEqual(len(leased), 2)
        self.assertEqual([p["id"] for p in leased], ["profile_1", "profile_2"])

        # Second request from same job does not exceed quota
        leased_again = self.lease_mgr.lease_profiles("job_A", self.profiles, count=2, max_profiles_per_job=2)
        self.assertEqual(len(leased_again), 2)

    def test_parallel_jobs_isolated_no_collision(self):
        # Job A leases 2 profiles
        leased_a = self.lease_mgr.lease_profiles("job_A", self.profiles, count=2, max_profiles_per_job=2)
        ids_a = {p["id"] for p in leased_a}
        self.assertEqual(len(ids_a), 2)

        # Job B leases 2 profiles simultaneously
        leased_b = self.lease_mgr.lease_profiles("job_B", self.profiles, count=2, max_profiles_per_job=2)
        ids_b = {p["id"] for p in leased_b}
        self.assertEqual(len(ids_b), 2)

        # Job C leases 2 profiles simultaneously
        leased_c = self.lease_mgr.lease_profiles("job_C", self.profiles, count=2, max_profiles_per_job=2)
        ids_c = {p["id"] for p in leased_c}
        self.assertEqual(len(ids_c), 2)

        # Verify zero overlap between jobs
        self.assertTrue(ids_a.isdisjoint(ids_b))
        self.assertTrue(ids_b.isdisjoint(ids_c))
        self.assertTrue(ids_a.isdisjoint(ids_c))

    def test_dynamic_profile_replacement_during_job_run(self):
        # Job A starts with profile_1 and profile_2
        self.lease_mgr.lease_profiles("job_A", self.profiles, count=2, max_profiles_per_job=2)

        # profile_1 encounters failure/cooldown, job requests replacement
        replacement = self.lease_mgr.replace_profile("job_A", "profile_1", self.profiles, reason="PUBLIC_ERROR_UNUSUAL_ACTIVITY")
        self.assertIsNotNone(replacement)
        self.assertNotEqual(replacement["id"], "profile_1")

        # profile_1 is no longer busy
        self.assertFalse(self.lease_mgr.is_profile_busy("profile_1"))

        # Replacement is registered to job_A
        active_leases = self.lease_mgr.get_job_leases("job_A")
        self.assertEqual(len(active_leases), 2)
        self.assertNotIn("profile_1", active_leases)
        self.assertIn(replacement["id"], active_leases)

    def test_multi_profile_manager_integration_with_job_lease(self):
        # Instantiate MultiProfileManager scoped to job_1 with 10 pool profiles
        with MultiProfileManager(
            profiles_config=self.profiles,
            job_id="job_prod_01",
            max_workers_per_job=2,
            lock_dir=self.lock_dir,
        ) as mgr:
            self.assertEqual(len(mgr.workers), 2)
            worker_ids = list(mgr.workers.keys())

            # Simulate failure and dynamic swap
            first_worker = mgr.workers[worker_ids[0]]
            new_worker = mgr.replace_worker_for_job(first_worker, reason="test rate-limit")
            self.assertIsNotNone(new_worker)
            self.assertIn(new_worker.profile_id, mgr.workers)
            self.assertNotIn(first_worker.profile_id, mgr.workers)
            self.assertEqual(len(mgr.workers), 2)

        # After context exit, all leases are released
        self.assertEqual(self.lease_mgr.get_job_leases("job_prod_01"), [])

    def test_clean_stale_leases_on_init(self):
        stale_lease = self.lock_dir / "profile_stale.lease"
        stale_lease.write_text('{"job_id": "dead", "profile_id": "profile_stale", "pid": 999999}')
        self.assertTrue(stale_lease.exists())

        new_mgr = FlowJobLeaseManager(lock_dir=self.lock_dir)
        self.assertFalse(stale_lease.exists())

    def test_lease_profiles_with_timeout_polling(self):
        # Pool with only 1 profile
        single_pool = [{"id": "single_p", "port": 9222, "directory": "P1", "enabled": True}]
        # Job 1 claims it
        leased_1 = self.lease_mgr.lease_profiles("j1", single_pool, count=1, max_profiles_per_job=1)
        self.assertEqual(len(leased_1), 1)

        import threading
        # Background timer to release j1 after 0.5s
        def release_later():
            import time
            time.sleep(0.5)
            self.lease_mgr.release_all_for_job("j1")

        threading.Thread(target=release_later, daemon=True).start()

        # Job 2 requests with timeout=2.0s
        leased_2 = self.lease_mgr.lease_profiles("j2", single_pool, count=1, max_profiles_per_job=1, timeout=2.0)
        self.assertEqual(len(leased_2), 1)
        self.assertEqual(leased_2[0]["id"], "single_p")


if __name__ == "__main__":
    unittest.main()
