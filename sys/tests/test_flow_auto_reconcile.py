"""Tests for Flow request auto-reconciliation, ledger synchronization, and transient recovery."""
import json
import shutil
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image

from pilot import ROOT, Pilot, Blocked, read, write, digest
import image_pipeline as ip
from account_budget import Budgets


class FlowAutoReconcileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for n in ['schemas', '.agents', 'tests', 'examples', 'scripts']:
            shutil.copytree(ROOT / n, self.root / n)
        for n in ['pilot.py', 'workflow.py', 'machine_review.py', 'image_pipeline.py',
                  'prompt_templates.py', 'content_contract.py', 'adapters.py', 'config.json',
                  'account_budget.py', 'flow_management.py', 'execution.py', 'AGENTS.md', 'GEMINI.md']:
            shutil.copy(ROOT / n, self.root / n)
        cfg = read(self.root / 'config.json')
        cfg.pop('flow_batch', None)
        cfg['flow_require_ui_evidence'] = True
        cfg['flow_management_store'] = str(self.root)
        write(self.root / 'config.json', cfg)
        self.p = Pilot(self.root)
        self.j = 'reconcile-test'
        self.p.new(self.j, read(ROOT / 'examples/m1/brief.json'))
        self.p.approve(self.j, 'control', 1, 'TEST FIXTURE')
        d = read(ROOT / 'examples/m1/content.json')
        _, r, h = self.p.brief(self.j)
        d.update(brief_revision=r, brief_hash=h)
        write(self.p.job(self.j) / 'draft/content.json', d)
        self.p.run(self.j, 'content')
        self.p.approve(self.j, 'content', 1, 'TEST FIXTURE')
        self.preflight()
        self.calls = []
        self.mock = patch('adapters.gflow', side_effect=self.provider)
        self.mock.start()

    def tearDown(self):
        self.mock.stop()
        self.p.db.close()
        self.tmp.cleanup()

    def preflight(self, **changes):
        base = self.p.job(self.j) / 'flow'
        base.mkdir(exist_ok=True)
        Image.new('RGB', (30, 30)).save(base / 'preflight.png')
        model_name = read(self.root / 'config.json')['flow_model']
        e = dict(
            observed_at=time.time(),
            mode='image',
            credits_per_generation=0,
            model=model_name,
            profile='video-pilot',
            project='Video Pilot',
            observer='TEST',
            account_confirmed=True,
            operations=['image', 'character-register'],
            screenshot='flow/preflight.png',
            screenshot_hash=digest(base / 'preflight.png'),
        )
        e.update(changes)
        write(base / 'preflight.json', e)

    def provider(self, p, *args, **kwargs):
        self.calls.append(args)
        folder = Path(args[args.index('--out') + 1])
        registration = args[0] == 'character'
        import hashlib
        rgb = tuple(hashlib.sha256(' '.join(args).encode()).digest()[:3])
        Image.new('RGB', (720, 1280), rgb).save(folder / 'result.png')
        chars = list(args[args.index('--character') + 1:]) if '--character' in args else []
        if not registration:
            write(folder / 'result.json', {
                'jobId': args[args.index('--id') + 1],
                'type': 'image',
                'prompt': args[args.index('--prompt') + 1],
                'ratio': '9:16',
                'characters': chars,
                'source': 'google-flow-browser',
                'status': 'downloaded',
            })
        write(folder.parent / 'ui-proof.json', {
            'passed': True,
            'mode': 'character-register' if registration else 'image',
            'characters': chars,
        })
        Image.new('RGB', (30, 30)).save(folder.parent / 'before-submit.png')
        return SimpleNamespace(returncode=0, stdout='TEST PROVIDER', stderr='')

    def test_auto_reconcile_disk_download(self):
        """If an attempt was interrupted or timed out but download/result.png exists on disk,
        auto_reconcile_attempt updates state to 'downloaded' and syncs the ledger."""
        target = 'ref:CH01'
        prompt = 'A character reference'
        cfg, ratio, actual_prompt, identity, key = ip._plan_request(
            self.p, self.j, target, prompt, (), None, None
        )
        attempt_dir = self.p.job(self.j) / 'flow/attempts' / key
        download_dir = attempt_dir / 'download'
        download_dir.mkdir(parents=True, exist_ok=True)
        img_path = download_dir / 'result.png'
        Image.new('RGB', (720, 1280), (10, 20, 30)).save(img_path)
        write(download_dir / 'result.json', {
            'jobId': key[:16],
            'type': 'image',
            'prompt': actual_prompt,
            'ratio': ratio,
            'characters': [],
            'source': 'google-flow-browser',
            'status': 'downloaded',
        })
        record = {
            'key': key,
            'identity': identity,
            'state': 'ambiguous',
            'error': 'Connection dropped after download',
            'submitted_at': time.time(),
        }
        write(attempt_dir / 'request.json', record)

        # Before explicit reconciliation, _unresolved_conflict calls auto_reconcile_attempt
        rec = ip.auto_reconcile_attempt(self.p, self.j, attempt_dir, record)
        self.assertEqual(rec['state'], 'downloaded')
        self.assertEqual(read(attempt_dir / 'request.json')['state'], 'downloaded')
        self.assertIsNone(ip._unresolved_conflict(self.p, self.j, target))

        # Calling request() returns the downloaded file immediately without calling gflow
        calls_before = len(self.calls)
        res = ip.request(self.p, self.j, target, prompt)
        self.assertEqual(res['state'], 'downloaded')
        self.assertEqual(len(self.calls), calls_before)

    def test_transient_transport_error_marked_not_submitted_and_synced(self):
        """When a websocket disconnect or transport error occurs during request,
        it is marked 'not_submitted' and synced to the ledger so resubmission is allowed."""
        target = 'ref:CH01'
        prompt = 'A character reference'

        def fail_transport(*args, **kwargs):
            raise RuntimeError("CDP_TRANSPORT_CLOSED: ConnectionClosed('no close frame received or sent')")

        with patch('adapters.gflow', side_effect=fail_transport):
            with self.assertRaises(Blocked):
                ip.request(self.p, self.j, target, prompt)

        # Check attempt record on disk
        candidates = list((self.p.job(self.j) / 'flow/attempts').glob('*/request.json'))
        target_attempts = [q for q in candidates if read(q)['identity']['target'] == target]
        self.assertTrue(len(target_attempts) > 0)
        rec = read(target_attempts[0])
        self.assertEqual(rec['state'], 'not_submitted')

        # Check that it did NOT leave an unresolved conflict
        self.assertIsNone(ip._unresolved_conflict(self.p, self.j, target))

        # Now when gflow works normally, subsequent request proceeds cleanly without FLOW_BUDGET lock
        res = ip.request(self.p, self.j, target, prompt)
        self.assertEqual(res['state'], 'downloaded')

    def test_historical_ambiguous_transient_auto_reset(self):
        """If a prior attempt was written as ambiguous due to 'no close frame received or sent',
        request() detects the transient pattern, auto-resets conflict to not_submitted, and succeeds."""
        target = 'ref:CH01'
        prompt = 'A character reference'
        cfg, ratio, actual_prompt, identity, key = ip._plan_request(
            self.p, self.j, target, prompt, (), None, None
        )
        attempt_dir = self.p.job(self.j) / 'flow/attempts' / key
        attempt_dir.mkdir(parents=True, exist_ok=True)
        record = {
            'key': key,
            'identity': identity,
            'state': 'ambiguous',
            'error': 'no close frame received or sent',
            'submitted_at': time.time(),
        }
        write(attempt_dir / 'request.json', record)

        # Calling request() will auto-recover the transient conflict and generate successfully
        res = ip.request(self.p, self.j, target, prompt)
        self.assertEqual(res['state'], 'downloaded')
        self.assertEqual(read(attempt_dir / 'request.json')['state'], 'downloaded')

    def test_flow_reconcile_without_asset_sets_not_submitted_and_syncs_ledger(self):
        """flow-reconcile without --asset (using UI evidence) reconciles attempt to 'not_submitted'
        and synchronizes the budget ledger."""
        target = 'ref:CH01'
        prompt = 'A character reference'
        cfg, ratio, actual_prompt, identity, key = ip._plan_request(
            self.p, self.j, target, prompt, (), None, None
        )
        attempt_dir = self.p.job(self.j) / 'flow/attempts' / key
        attempt_dir.mkdir(parents=True, exist_ok=True)
        record = {
            'key': key,
            'identity': identity,
            'state': 'ambiguous',
            'error': 'Provider timeout with unknown status',
            'submitted_at': time.time(),
        }
        write(attempt_dir / 'request.json', record)

        # Mock owner.json for budget ledger tracking
        b = Budgets(self.root)
        from session_store import locked_json
        b.bind_identity('test_account', 'test_account', 'test_evidence')
        owner = {
            'account': 'test_account',
            'identity': 'test_account',
            'operation': 'test_session',
            'session': 'test_session',
        }
        write(attempt_dir / 'owner.json', owner)
        with locked_json(b.path, b.read) as data:
            acc = b._account(data, 'test_account')
            acc.setdefault('flow', {})['test_session'] = {
                key: {'slots': 1, 'state': 'ambiguous', 'at': time.time(), 'evidence': 'test'}
            }

        # Create UI evidence proving generation did not submit / produce image
        shot = self.root / 'ui_error.png'
        Image.new('RGB', (200, 200), (255, 0, 0)).save(shot)
        evidence = {
            'request': key,
            'observer': 'operator_ui_check',
            'screenshot': str(shot),
            'matched_download': False,
            'not_submitted': True,
        }
        evidence_file = self.root / 'evidence.json'
        write(evidence_file, evidence)

        # Execute flow-reconcile with asset=None
        args = SimpleNamespace(
            job=self.j,
            command='flow-reconcile',
            request=key,
            asset=None,
            note='Operator verified generation failed in UI',
            evidence=str(evidence_file),
        )
        result = ip.flow_action(self.p, args)
        self.assertEqual(result['state'], 'not_submitted')
        self.assertEqual(read(attempt_dir / 'request.json')['state'], 'not_submitted')

        # Verify ledger was synced to not_submitted
        ledger_state = b.read()['accounts']['test_account']['flow']['test_session'][key]['state']
        self.assertEqual(ledger_state, 'not_submitted')

    def test_pre_submission_flag_avoids_ambiguous(self):
        """When pre-submission check or captcha/token throws with generation_submitted=False,
        request() marks state as 'not_submitted' instead of 'ambiguous'."""
        target = 'ref:CH01'
        prompt = 'A character reference'

        def fail_pre_submit(*args, **kwargs):
            err = RuntimeError("CAPTCHA_FAILED: empty token")
            err.generation_submitted = False
            raise err

        with patch('adapters.gflow', side_effect=fail_pre_submit):
            with self.assertRaises(Blocked):
                ip.request(self.p, self.j, target, prompt)

        candidates = list((self.p.job(self.j) / 'flow/attempts').glob('*/request.json'))
        target_attempts = [q for q in candidates if read(q)['identity']['target'] == target]
        self.assertTrue(len(target_attempts) > 0)
        rec = read(target_attempts[0])
        self.assertEqual(rec['state'], 'not_submitted')
        self.assertIsNone(ip._unresolved_conflict(self.p, self.j, target))


if __name__ == '__main__':
    unittest.main()

