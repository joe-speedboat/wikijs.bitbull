"""Local behavioral tests: real temporary files/tar; Docker and root operations mocked.
Run: python3 -m unittest discover -s paperless/scripts -p 'test_*.py' -v
No Docker daemon, production host, or root privileges are used.
"""
import copy
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('ops', Path(__file__).with_name('paperless_ops.py'))
assert spec is not None and spec.loader is not None
ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ops)


class Operations(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'paperless'
        self.root.mkdir()
        for name in (*ops.PARTS, 'postgres'):
            (self.root / name).mkdir()
        (self.root / 'media' / 'document.pdf').write_bytes(b'representative document\x00')
        self.cfg = {'name': 'paperless', 'services': {s: {'image': s + ':old',
                    'networks': {'default': None}} for s in ops.SERVICES},
                    'networks': {'default': {}}}
        self.cfg['services']['db']['volumes'] = [{'type': 'bind', 'source': str(self.root / 'postgres'),
                                                'target': '/var/lib/postgresql'}]
        (self.root / 'compose' / 'compose.yaml').write_text(json.dumps(self.cfg))
        self.calls = []
        self.inject_failure = None
        self.internal = True
        self.ready = True
        self.real_run = subprocess.run
        for target, replacement in [('ROOT', self.root), ('run', self.fake_run),
                                    ('free_space', lambda *a: None)]:
            p = patch.object(ops, target, replacement)
            p.start()
            self.addCleanup(p.stop)
        for target in ('os.chown', 'time.sleep'):
            p = patch.object(ops.os if target.startswith('os') else ops.time,
                             target.split('.')[1])
            p.start()
            self.addCleanup(p.stop)
        self.images = {s: ('postgres' if s == 'db' else s) + '@sha256:' + 'a' * 64
                       for s in ops.SERVICES}

    def fake_run(self, args, **kwargs):
        self.calls.append(args)
        if self.inject_failure and self.inject_failure(args):
            raise subprocess.CalledProcessError(1, args, stderr=b'private detail')
        if args[0] == 'tar':
            return self.real_run(args, check=True, stderr=subprocess.PIPE, **kwargs)
        data = b''
        if 'config' in args and '--format' in args:
            data = json.dumps(self.cfg).encode()
        elif 'ps' in args:
            data = b'' if '--all' in args else args[-1].encode()
        elif '{{.Image}}' in args:
            data = args[-1].encode()
        elif '{{json .RepoDigests}}' in args:
            data = json.dumps([self.images.get(args[-1], 'webserver@sha256:' + 'b' * 64)]).encode()
        elif 'pg_dump' in args:
            data = b'fake dump for control-flow test only'
        elif 'psql' in args:
            data = json.dumps({t: [] for t in ops.COMPARISON_TABLES}).encode()
        elif '--version' in args:
            data = b'postgres (PostgreSQL) 18.1'
        elif 'pg_isready' in args and not self.ready:
            raise subprocess.CalledProcessError(1, args)
        elif '{{json .NetworkSettings.Networks}}' in args:
            data = b'{"paperless_default": {}}'
        elif '{{.Internal}}' in args:
            data = b'true' if self.internal else b'false'
        if hasattr(kwargs.get('stdout'), 'write'):
            kwargs['stdout'].write(data)
        return subprocess.CompletedProcess(args, 0, data)

    def make_backup(self):
        # root ownership is the only backup precondition not available to this unprivileged harness.
        original = ops.require
        def check(ok, message):
            if message != 'Backup parent must be root-owned and mode 0700':
                original(ok, message)
        with patch.object(ops, 'require', check):
            return ops.backup(self.base / 'backups')

    def fresh(self):
        shutil.rmtree(self.root)  # Only this test's generated directory.

    def test_backup_archive_hashes_and_restart(self):
        backup = self.make_backup()
        self.assertTrue((backup / 'SUCCESS').exists())
        images, size = ops.validate_backup(backup)
        self.assertEqual(images, self.images)
        self.assertGreater(size, 0)
        self.assertTrue(any('start' in c and 'webserver' in c for c in self.calls))

    def test_dump_failure_restarts_no_success(self):
        self.inject_failure = lambda a: 'pg_dump' in a
        with self.assertRaises(subprocess.CalledProcessError):
            self.make_backup()
        self.assertTrue(any('start' in c for c in self.calls))
        self.assertFalse(list((self.base / 'backups').glob('*/SUCCESS')))

    def test_restart_failure_not_success(self):
        self.inject_failure = lambda a: 'start' in a
        with self.assertRaises(subprocess.CalledProcessError):
            self.make_backup()
        self.assertFalse(list((self.base / 'backups').glob('*/SUCCESS')))

    def test_restore_real_archive_media_and_isolation(self):
        backup = self.make_backup()
        self.fresh()
        ops.restore(backup, False, 'http://localhost:8000')
        cfg = json.loads((self.root / 'compose' / 'compose.yaml').read_text())
        self.assertTrue(cfg['networks']['default']['internal'])
        self.assertEqual(cfg['services']['db']['image'], self.images['db'])
        self.assertEqual(ops.media_hashes(), json.loads((backup / 'media.json').read_text()))
        network_check = next(i for i, c in enumerate(self.calls) if '{{.Internal}}' in c)
        restore = next(i for i, c in enumerate(self.calls) if '--exit-on-error' in c)
        self.assertLess(network_check, restore)

    def test_restore_existing_target_refused(self):
        backup = self.make_backup()
        count = len(self.calls)
        with self.assertRaisesRegex(RuntimeError, 'empty'):
            ops.restore(backup, False, 'http://localhost:8000')
        self.assertEqual(len(self.calls), count)

    def test_checksum_corruption_refused(self):
        backup = self.make_backup()
        (backup / 'database.dump').chmod(0o600)
        (backup / 'database.dump').write_bytes(b'corrupt')
        with self.assertRaisesRegex(RuntimeError, 'checksum'):
            ops.validate_backup(backup)

    def test_archive_traversal_refused(self):
        backup = self.make_backup()
        (backup / 'files.tar.gz').chmod(0o600)
        (backup / 'SHA256SUMS.json').chmod(0o600)
        with tarfile.open(backup / 'files.tar.gz', 'w:gz') as archive:
            m = tarfile.TarInfo('paperless/media/../../escape')
            m.size = 1
            archive.addfile(m, io.BytesIO(b'x'))
        checks = json.loads((backup / 'SHA256SUMS.json').read_text())
        checks['files.tar.gz'] = ops.digest(backup / 'files.tar.gz')
        ops.save(backup / 'SHA256SUMS.json', checks)
        with self.assertRaisesRegex(RuntimeError, 'Unsafe'):
            ops.validate_backup(backup)

    def test_isolation_failure_stops_stack(self):
        backup = self.make_backup()
        self.fresh()
        self.internal = False
        with self.assertRaisesRegex(RuntimeError, 'not internal'):
            ops.restore(backup, False, 'http://localhost:8000')
        self.assertEqual(self.calls[-1][-1], 'stop')
        self.assertFalse(any('--exit-on-error' in c for c in self.calls))

    def test_readiness_timeout_stops_and_retains(self):
        backup = self.make_backup()
        self.fresh()
        self.ready = False
        with self.assertRaisesRegex(RuntimeError, 'timeout'):
            ops.restore(backup, False, 'http://localhost:8000')
        self.assertEqual(sum('pg_isready' in c for c in self.calls), 60)
        self.assertTrue((self.root / 'media' / 'document.pdf').exists())
        self.assertEqual(self.calls[-1][-1], 'stop')

    def test_upgrade_changes_only_webserver_image(self):
        before = copy.deepcopy(self.cfg)
        with patch.object(ops, 'backup', self.make_backup_noarg):
            ops.upgrade('3.3.4', self.base / 'backups')
        after = json.loads((self.root / 'compose' / 'compose.yaml').read_text())
        after['services']['webserver']['image'] = before['services']['webserver']['image']
        self.assertEqual(before, after)
        self.assertTrue(any('--no-deps' in c and c[-1] == 'webserver' for c in self.calls))

    def make_backup_noarg(self, _destination):
        return self.base / 'verified-backup'

    def test_upgrade_invalid_version_no_mutation(self):
        for version in ('latest', '3', 'v3.3.4', '3.3.4;exit'):
            with self.assertRaises(RuntimeError):
                ops.upgrade(version, self.base)
        self.assertFalse(self.calls)

    def test_shared_lock_rejects_concurrent_operation(self):
        lock_path = self.base / 'operations.lock'
        original_open = open
        def local_open(path, *args, **kwargs):
            return original_open(lock_path if path == '/run/lock/paperless-operations.lock' else path,
                                 *args, **kwargs)
        with original_open(lock_path, 'w') as held:
            ops.fcntl.flock(held, ops.fcntl.LOCK_EX | ops.fcntl.LOCK_NB)
            with patch('builtins.open', local_open), patch.object(ops.os, 'geteuid', return_value=0), \
                    patch.object(ops.os, 'umask'), patch.object(ops.signal, 'signal'), \
                    patch.object(ops.sys, 'argv', ['paperless_ops.py', 'backup']), \
                    patch.dict(ops.os.environ):
                with self.assertRaisesRegex(RuntimeError, 'holds the lock'):
                    ops.main()
        self.assertFalse(self.calls)

    def test_partial_stop_failure_still_restarts(self):
        self.inject_failure = lambda a: 'stop' in a
        with self.assertRaises(subprocess.CalledProcessError):
            self.make_backup()
        self.assertTrue(any('start' in c for c in self.calls))
        self.assertFalse(list((self.base / 'backups').glob('*/SUCCESS')))

    def test_low_disk_refuses_before_stop(self):
        with patch.object(ops, 'free_space', side_effect=RuntimeError('Insufficient free disk space')):
            with self.assertRaisesRegex(RuntimeError, 'disk'):
                self.make_backup()
        self.assertFalse(any('stop' in c for c in self.calls))

    def test_missing_success_refused(self):
        backup = self.make_backup()
        (backup / 'SUCCESS').unlink()
        with self.assertRaisesRegex(RuntimeError, 'SUCCESS'):
            ops.validate_backup(backup)

    def test_production_mode_is_explicit(self):
        backup = self.make_backup()
        self.fresh()
        ops.restore(backup, True, 'http://ignored.example.net')
        cfg = json.loads((self.root / 'compose' / 'compose.yaml').read_text())
        self.assertFalse(cfg['networks']['default']['internal'])
        self.assertNotIn('environment', cfg['services']['webserver'])

    def test_rendered_dollars_are_escaped(self):
        path = self.base / 'literal.json'
        ops.save_compose(path, {'value': 'literal$VARIABLE${VALUE}'})
        self.assertEqual(json.loads(path.read_text())['value'], 'literal$$VARIABLE$${VALUE}')

    def test_upgrade_backup_failure_prevents_pull(self):
        with patch.object(ops, 'backup', side_effect=RuntimeError('backup failed')):
            with self.assertRaisesRegex(RuntimeError, 'backup failed'):
                ops.upgrade('3.3.4', self.base)
        self.assertFalse(any('pull' in c or '--no-deps' in c for c in self.calls))

    def test_upgrade_failure_no_automatic_rollback(self):
        self.inject_failure = lambda a: '--no-deps' in a
        with patch.object(ops, 'backup', self.make_backup_noarg):
            with self.assertRaises(subprocess.CalledProcessError):
                ops.upgrade('3.3.4', self.base)
        self.assertTrue((self.root / 'compose' / 'upgrade-candidate.json').exists())
        self.assertEqual(json.loads((self.root / 'compose' / 'compose.yaml').read_text()), self.cfg)


if __name__ == '__main__':
    unittest.main()
