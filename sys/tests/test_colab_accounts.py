import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from colab_bridge import accounts


class AccountTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.patch=patch.object(accounts,'STORE',self.root/'store');self.patch.start();self.addCleanup(self.patch.stop)
        self.source=self.root/'source';self.source.mkdir()
        (self.source/'token.json').write_text('{"test_only":true}')
        (self.source/'sessions.json').write_text('{}')

    def test_import_is_private_and_does_not_replace_source(self):
        accounts.add('account-01',self.source)
        self.assertEqual(accounts.select(),'account-01')
        token=accounts.folder('account-01')/'token.json'
        self.assertEqual(token.stat().st_mode & 0o777,0o600)
        self.assertEqual(token.parent.stat().st_mode & 0o777,0o700)
        token.write_text('changed')
        self.assertEqual((self.source/'token.json').read_text(),'{"test_only":true}')

    def test_auto_chooses_enabled_authenticated_profile(self):
        accounts.add('one',self.source);accounts.add('two',self.source)
        d=accounts.registry();d['accounts'][0]['enabled']=False;accounts.save(d)
        self.assertEqual(accounts.select(),'two')
        with self.assertRaises(ValueError):accounts.select('one')

    def test_no_overwrite_or_path_escape(self):
        accounts.add('one',self.source)
        with self.assertRaises(ValueError):accounts.add('one',self.source)
        with self.assertRaises(ValueError):accounts.folder('../bad')

    def test_launcher_uses_profile_without_global_token_swap(self):
        binary=self.root/'colab';binary.write_text('#!/usr/bin/python3\n')
        argv=accounts.command(binary,'two',['sessions'])
        self.assertEqual(argv[0],'/usr/bin/python3')
        self.assertEqual(argv[-2:], [str(accounts.folder('two')),'sessions'])

    def test_enable_disable_role_and_remove_lifecycle(self):
        accounts.add('account-01', self.source)
        accounts.add('account-02', self.source, role='render')
        self.assertEqual(accounts.registry()['preferred'], 'account-01')

        # Disabling preferred account shifts preferred to next enabled account
        res = accounts.set_enabled('account-01', False)
        self.assertFalse(res['enabled'])
        self.assertEqual(accounts.registry()['preferred'], 'account-02')

        # Re-enabling works
        accounts.set_enabled('account-01', True)
        accounts.set_role('account-01', 'tts')
        self.assertEqual(accounts.select(role='tts'), 'account-01')
        self.assertEqual(accounts.select(role='render'), 'account-02')

        with self.assertRaises(ValueError):
            accounts.set_role('account-01', 'invalid-role')

        rem = accounts.remove('account-01', delete_files=True)
        self.assertEqual(rem['removed'], 'account-01')
        self.assertFalse(accounts.folder('account-01').exists())

    def test_auto_idle_skips_busy_locked_session(self):
        import fcntl
        from colab_bridge.protocol import stamp
        accounts.add('account-01', self.source)
        accounts.add('account-02', self.source)
        lock_dir = self.root / 'locks'
        lock_dir.mkdir(parents=True, exist_ok=True)
        lock_file = lock_dir / (stamp(['account-01', 'video-pilot-tts']) + '.lock')
        with lock_file.open('a') as handle:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertTrue(accounts.is_session_busy('account-01', 'video-pilot-tts', lock_dir=lock_dir))
            self.assertFalse(accounts.is_session_busy('account-02', 'video-pilot-tts', lock_dir=lock_dir))
            # Standard 'auto' still picks preferred, while 'auto-idle' picks idle account-02
            self.assertEqual(accounts.select('auto', lock_dir=lock_dir), 'account-01')
            self.assertEqual(accounts.select('auto-idle', lock_dir=lock_dir), 'account-02')
            pool = accounts.select_pool(lock_dir=lock_dir)
            self.assertEqual(pool, ['account-02'])
            st = accounts.status_all(lock_dir=lock_dir)
            self.assertEqual(st['ready_for_pool'], 1)
            fcntl.flock(handle, fcntl.LOCK_UN)

