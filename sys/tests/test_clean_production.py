"""Revision retention across approved, rejected and missing module states."""
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scripts.clean_production as cp


def make_db(db_path: Path, rows):
    """rows: list of (job, module, state, revision) tuples."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS modules("
        "job TEXT, module TEXT, state TEXT, revision INTEGER, "
        "envelope TEXT, hash TEXT, PRIMARY KEY(job, module))"
    )
    for job, module, state, revision in rows:
        conn.execute(
            "INSERT INTO modules(job, module, state, revision, envelope, hash) "
            "VALUES (?,?,?,?,?,?)",
            (job, module, state, revision, "", ""),
        )
    conn.commit()
    conn.close()


def make_rev_file(revisions_dir: Path, module: str, revision, filename: str, content: bytes = b"x" * 1024):
    p = revisions_dir / module / str(revision)
    p.mkdir(parents=True, exist_ok=True)
    f = p / filename
    f.write_bytes(content)
    return f


class CleanProductionPruneTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.runs_dir = self.root / "runs"
        self.state_dir = self.root / ".state"
        self.db_path = self.state_dir / "jobs.sqlite"
        self.exports_dir = self.root / "exports"
        self.runs_dir.mkdir(parents=True)
        self.state_dir.mkdir(parents=True)

        patcher_root = patch.object(cp, "ROOT", self.root)
        patcher_runs = patch.object(cp, "RUNS_DIR", self.runs_dir)
        patcher_db = patch.object(cp, "DB_PATH", self.db_path)
        patcher_exports = patch.object(cp, "EXPORTS_DIR", self.exports_dir)
        patcher_state = patch.object(cp, "STATE_DIR", self.state_dir)
        for p in (patcher_root, patcher_runs, patcher_db, patcher_exports, patcher_state):
            p.start()
            self.addCleanup(p.stop)

        self.addCleanup(self.tmp.cleanup)

    def revisions_dir(self, job_id):
        return self.runs_dir / job_id / "revisions"

    # --- Case 1: original bug scenario ------------------------------------
    def test_retains_every_revision_even_with_different_approved_numbers(self):
        """render approved@1, images approved@3 (after two rejections).
        Must keep render/1 and images/3, and retain images/1 + images/2.
        This reproduces the exact scenario from the bug report."""
        job = "jobA"
        rev_dir = self.revisions_dir(job)
        render1 = make_rev_file(rev_dir, "render", 1, "out.mp4")
        images1 = make_rev_file(rev_dir, "images", 1, "scene1.png")
        images2 = make_rev_file(rev_dir, "images", 2, "scene1.png")
        images3 = make_rev_file(rev_dir, "images", 3, "scene1.png")

        make_db(self.db_path, [
            (job, "render", "approved", 1),
            (job, "images", "approved", 3),
        ])

        cp.prune_unapproved_revisions(job, dry_run=False)

        self.assertTrue(images3.exists(), "approved images revision 3 must survive pruning")
        self.assertTrue(render1.exists(), "approved render revision 1 must survive pruning")
        self.assertTrue(images1.exists(), "history must be preserved")
        self.assertTrue(images2.exists(), "history must be preserved")

    # --- Case 2: fail-closed on non-approved module -------------------------
    def test_fail_closed_when_module_not_approved(self):
        """A module sitting in needs_changes/pending/stale/blocked must have
        NOTHING deleted from its revisions/ folder — we cannot know which
        draft, if any, is worth keeping."""
        job = "jobB"
        rev_dir = self.revisions_dir(job)
        audio1 = make_rev_file(rev_dir, "audio", 1, "line.wav")
        audio2 = make_rev_file(rev_dir, "audio", 2, "line.wav")

        make_db(self.db_path, [
            (job, "render", "approved", 1),
            (job, "audio", "needs_changes", 2),
        ])

        cp.prune_unapproved_revisions(job, dry_run=False)

        self.assertTrue(audio1.exists(), "non-approved module: revision 1 must be untouched")
        self.assertTrue(audio2.exists(), "non-approved module: revision 2 must be untouched")

    # --- Case 3: module folder with no database row at all ------------------
    def test_module_folder_without_database_row_is_untouched(self):
        job = "jobC"
        rev_dir = self.revisions_dir(job)
        orphan = make_rev_file(rev_dir, "subtitles", 1, "cap.png")

        # 'subtitles' has no row in modules at all.
        make_db(self.db_path, [
            (job, "render", "approved", 1),
        ])

        cp.prune_unapproved_revisions(job, dry_run=False)

        self.assertTrue(orphan.exists(), "module absent from DB must not be pruned")

    # --- Case 4: dry_run must not delete, but must count correctly ----------
    def test_dry_run_excludes_revision_media_from_candidates(self):
        job = "jobD"
        rev_dir = self.revisions_dir(job)
        render1 = make_rev_file(rev_dir, "render", 1, "out.mp4", content=b"r" * 500)
        images_approved = make_rev_file(rev_dir, "images", 2, "scene1.png", content=b"i" * 700)
        images_draft = make_rev_file(rev_dir, "images", 1, "scene1.png", content=b"d" * 300)

        make_db(self.db_path, [
            (job, "render", "approved", 1),
            (job, "images", "approved", 2),
        ])

        freed = cp.prune_unapproved_revisions(job, dry_run=True)

        self.assertEqual(freed, 0, "revision media are not deletion candidates")
        self.assertTrue(render1.exists())
        self.assertTrue(images_approved.exists())
        self.assertTrue(images_draft.exists(), "dry_run must not actually delete anything")

    # --- Case 5: non-media files in an unapproved revision are preserved ----
    def test_non_media_files_preserved_in_unapproved_revision(self):
        job = "jobE"
        rev_dir = self.revisions_dir(job)
        draft_json = make_rev_file(rev_dir, "content", 1, "draft.json", content=b'{"a":1}')
        draft_media = make_rev_file(rev_dir, "content", 1, "still.png")
        approved_dir = rev_dir / "content" / "2"
        approved_dir.mkdir(parents=True, exist_ok=True)
        (approved_dir / "final.json").write_bytes(b'{"a":2}')

        make_db(self.db_path, [
            (job, "render", "approved", 1),
            (job, "content", "approved", 2),
        ])

        cp.prune_unapproved_revisions(job, dry_run=False)

        self.assertTrue(draft_json.exists(), "non-media (.json) files must never be deleted by this tool")
        self.assertTrue(draft_media.exists(), "rejected media remain evidence")


class PeriodicCleanupAndDedupTests(unittest.TestCase):
    def _age_tree(self, path: Path, mtime: float = 1.0) -> None:
        for entry in list(path.rglob("*")) + [path]:
            if not entry.is_symlink():
                os.utime(entry, (mtime, mtime))

    def test_video_work_prune_fails_closed_without_valid_final_mp4(self):
        with tempfile.TemporaryDirectory() as tmp:
            video_dir = Path(tmp) / "video"
            job_dir = video_dir / "job_unverified"
            render_dir = job_dir / "_work_short" / "render_2k"
            render_dir.mkdir(parents=True)
            chunk = render_dir / "chunk_01.mp4"
            chunk.write_bytes(b"chunk-bytes")
            (job_dir / "final_short.mp4").write_bytes(b"corrupt")
            self._age_tree(job_dir)

            with patch.object(cp, "validate_video_integrity", return_value=(False, "corrupt")):
                freed = cp.prune_verified_video_work_intermediates(video_dir=video_dir, dry_run=False)

            self.assertEqual(freed, 0)
            self.assertTrue(chunk.exists(), "must fail closed when final mp4 fails ffprobe")

    def test_video_work_prune_cleans_render_chunks_preserves_flow_frames_and_clips(self):
        with tempfile.TemporaryDirectory() as tmp:
            video_dir = Path(tmp) / "video"
            job_dir = video_dir / "job_verified"
            work_short = job_dir / "_work_short"
            work_long = job_dir / "_work_long"

            # Regenerable intermediates
            colab_dir = work_long / "_colab_render"
            render_dir = work_short / "render_2k"
            fonts_dir = work_short / "fonts"
            old_imgs = work_long / "images_old_98"
            for d in (colab_dir, render_dir, fonts_dir, old_imgs):
                d.mkdir(parents=True)
            (colab_dir / "part1.mp4").write_bytes(b"a" * 4096)
            (render_dir / "seg.mp4").write_bytes(b"b" * 4096)
            (fonts_dir / "font.ttf").write_bytes(b"c" * 2048)
            (old_imgs / "img_old.png").write_bytes(b"d" * 2048)
            payload_zip = work_short / "payload.zip"
            payload_zip.write_bytes(b"z" * 1024)

            # Protected Flow sources + metadata + deliverables
            frames_dir = job_dir / "frames"
            clips_dir = job_dir / "clips"
            work_imgs = work_long / "images"
            flow_clips = work_short / "flow_video" / "clips"
            for d in (frames_dir, clips_dir, work_imgs, flow_clips):
                d.mkdir(parents=True)
            frame_file = frames_dir / "b01.png"
            clip_file = clips_dir / "c01.mp4"
            work_img_file = work_imgs / "b01.png"
            flow_clip_file = flow_clips / "seg01.mp4"
            spec_file = job_dir / "spec.json"
            final_mp4 = job_dir / "final_long.mp4"
            frame_file.write_bytes(b"frame")
            clip_file.write_bytes(b"clip")
            work_img_file.write_bytes(b"img")
            flow_clip_file.write_bytes(b"flow")
            spec_file.write_text("{}", encoding="utf-8")
            final_mp4.write_bytes(b"final-mp4-data")
            self._age_tree(job_dir)

            with patch.object(cp, "validate_video_integrity", return_value=(True, "Video hợp lệ")):
                dry_freed = cp.prune_verified_video_work_intermediates(video_dir=video_dir, dry_run=True)
                self.assertGreater(dry_freed, 0)
                self.assertTrue(render_dir.exists())
                freed = cp.prune_verified_video_work_intermediates(video_dir=video_dir, dry_run=False)

            self.assertEqual(freed, dry_freed)
            for removed in (colab_dir, render_dir, fonts_dir, old_imgs, payload_zip):
                self.assertFalse(removed.exists(), f"{removed} should be pruned")
            for kept in (frame_file, clip_file, work_img_file, flow_clip_file, spec_file, final_mp4):
                self.assertTrue(kept.exists(), f"{kept} must be preserved")

    def test_deduplicate_identical_job_deliverables_hardlinks_matching_sha256_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            job_dir = Path(tmp) / "job_dedup"
            job_dir.mkdir()
            payload_a = b"A" * (1024 * 1024 + 64)
            payload_b = b"B" * (1024 * 1024 + 64)

            p1 = job_dir / "final_long.mp4"
            p2 = job_dir / "final_long_2k.mp4"
            p3 = job_dir / "other_same_size.mp4"
            p1.write_bytes(payload_a)
            p2.write_bytes(payload_a)
            p3.write_bytes(payload_b)

            freed = cp.deduplicate_identical_job_deliverables(job_dir, min_bytes=1024 * 1024, dry_run=False)
            self.assertEqual(freed, len(payload_a))
            self.assertEqual(p1.stat().st_ino, p2.stat().st_ino)
            self.assertNotEqual(p1.stat().st_ino, p3.stat().st_ino)
            self.assertEqual(p2.read_bytes(), payload_a)
            self.assertEqual(p3.read_bytes(), payload_b)

    def test_periodic_scratch_and_caches_respects_retention_and_preserves_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scratch = root / "sys" / "scratch"
            stale = scratch / "foo_render_work"
            fresh = scratch / "bar_render_work"
            archive = scratch / "legacy_tools_archive"
            for d in (stale, fresh, archive):
                d.mkdir(parents=True)
            (stale / "tmp.mp4").write_bytes(b"x" * 2048)
            (fresh / "active.mp4").write_bytes(b"y" * 2048)
            (archive / "keep.py").write_text("print(1)\n", encoding="utf-8")
            evidence = scratch / "evidence.png"
            evidence.write_bytes(b"png")

            self._age_tree(stale, mtime=1.0)
            self._age_tree(archive, mtime=1.0)
            os.utime(evidence, (1.0, 1.0))

            freed = cp.prune_periodic_scratch_and_caches(
                repo_root=root,
                scratch_dir=scratch,
                retention_hours=2.0,
                dry_run=False,
            )
            self.assertGreaterEqual(freed, 2048)
            self.assertFalse(stale.exists())
            self.assertTrue(fresh.exists())
            self.assertTrue((archive / "keep.py").exists())
            self.assertTrue(evidence.exists())


if __name__ == "__main__":
    unittest.main()
