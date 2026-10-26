"""Real tar regression cases; no Docker or managed hosts required."""
import io
import json
import os
import tarfile
from unittest.mock import patch
import test_operations as harness
ops = harness.ops


class ArchiveSafety(harness.Operations):
    # Inherit the lifecycle harness, but not its tests (installed below).
    def archive(self, entries):
        path = self.base / 'attack.tar.gz'
        with tarfile.open(path, 'w:gz') as tf:
            for name, kind, target in entries:
                m = tarfile.TarInfo(name)
                m.type = kind
                m.linkname = target
                m.size = 1 if kind == tarfile.REGTYPE else 0
                tf.addfile(m, io.BytesIO(b'x') if m.size else None)
        return path

    def test_adversarial_graphs_both_orders(self):
        f = tarfile.REGTYPE
        s = tarfile.SYMTYPE
        d = tarfile.DIRTYPE
        good = ('paperless/data/blob', f, '')
        cases = [
            [('paperless/data/link', s, '/etc/passwd')],
            [('paperless/data/link', s, '../../outside')],
            [('paperless/data/link', s, '../media/blob'), ('paperless/media/blob', f, '')],
            [('paperless/data/link', s, 'missing')],
            [('paperless/data/link', s, 'missing/../blob'), good],
            [('paperless/data/link', s, 'blob/.') , good],
            [('paperless/data/a', s, 'b'), ('paperless/data/b', s, 'a')],
            [('paperless/data/a', s, 'b'), ('paperless/data/b', s, 'blob'), good],
            [('paperless/data/a', s, '.'), ('paperless/data/a/child', f, '')],
            [('paperless/data/a', s, 'dir'), ('paperless/data/dir', d, '')],
            [('paperless/data/a', tarfile.LNKTYPE, 'paperless/data/blob'), good],
            [good, good],
            [('paperless/data', s, 'media')],
            [('paperless/data/../media/a', f, '')],
            [('/paperless/data/a', f, '')],
            [('paperless/data//a', f, '')],
            [('paperless/data/./a', f, '')],
            [('paperless/data/fifo', tarfile.FIFOTYPE, '')],
            [('paperless/data/a', f, ''), ('paperless/data/a/child', f, '')],
            [('paperless/data/a', s, 'b/../blob'), ('paperless/data/b', s, 'blob'), good],
        ]
        for entries in cases:
            for order in (entries, list(reversed(entries))):
                with self.subTest(entries=order):
                    with self.assertRaisesRegex(RuntimeError, 'Unsafe'):
                        ops.validate_archive(self.archive(order))

    def test_forward_reference_valid_in_both_orders(self):
        entries = [('paperless/data/cache/snapshots/rev/file', tarfile.SYMTYPE, '../../blobs/hash'),
                   ('paperless/data/cache/blobs/hash', tarfile.REGTYPE, '')]
        for order in (entries, list(reversed(entries))):
            self.assertEqual(ops.validate_archive(self.archive(order)), 1)

    def test_invalid_source_link_backup_restarts_without_success(self):
        (self.root / 'data' / 'bad-link').symlink_to('/etc/passwd')
        with self.assertRaisesRegex(RuntimeError, 'Unsafe'):
            self.make_backup()
        self.assertTrue(any('start' in c for c in self.calls))
        self.assertFalse(list((self.base / 'backups').glob('*/SUCCESS')))

    def test_hf_links_actual_backup_restore_and_hardlink_materialization(self):
        cache = self.root / 'data' / 'models--fixture'
        (cache / 'blobs').mkdir(parents=True)
        (cache / 'snapshots' / 'revision').mkdir(parents=True)
        blob = cache / 'blobs' / 'hash'
        blob.write_bytes(b'synthetic model bytes')
        os.link(blob, cache / 'blobs' / 'hardcopy')
        for n in range(22):
            (cache / 'snapshots' / 'revision' / str(n)).symlink_to('../../blobs/hash')
        expected = ops.digest(blob)
        backup = self.make_backup()
        self.fresh()
        ops.restore(backup, False, 'http://localhost:8000')
        for n in range(22):
            link = cache / 'snapshots' / 'revision' / str(n)
            self.assertTrue(link.is_symlink())
            self.assertEqual(os.readlink(link), '../../blobs/hash')
            self.assertEqual(ops.digest(link), expected)
        self.assertEqual(ops.digest(cache / 'blobs' / 'hardcopy'), expected)

    def test_manifest_mismatch_stops_before_web_start_or_index(self):
        backup = self.make_backup()
        baseline = (backup / 'comparison.json').read_bytes()
        self.fresh()
        self.calls.clear()
        with patch.object(ops, 'comparison_manifest', return_value={'different': True}):
            with self.assertRaisesRegex(RuntimeError, 'comparison manifest differs'):
                ops.restore(backup, False, 'http://localhost:8000')
        self.assertFalse(any('reindex' in c or '--wait' in c for c in self.calls))
        self.assertEqual(self.calls[-1][-1], 'stop')
        self.assertEqual((backup / 'comparison.json').read_bytes(), baseline)
        self.assertEqual((backup / 'comparison.json').stat().st_mode & 0o777, 0o400)

    def test_manifest_checksum_corruption(self):
        backup = self.make_backup()
        (backup / 'comparison.json').chmod(0o600)
        (backup / 'comparison.json').write_text('{}')
        with self.assertRaisesRegex(RuntimeError, 'checksum'):
            ops.validate_backup(backup)

    def test_manifest_counts_ids_and_hashed_state(self):
        raw = {t: [] for t in ops.COMPARISON_TABLES}
        raw['documents_document'] = [{'id': 1, 'content': 'private', 'deleted_at': None},
                                     {'id': 2, 'content': 'trash', 'deleted_at': '2026-01-01'}]
        raw['auth_user'] = [{'id': 1, 'is_active': True}]
        with patch.object(ops, 'output', return_value=json.dumps(raw)):
            manifest = ops.comparison_manifest()
        self.assertEqual(manifest['documents'], {'active': 1, 'trash': 1, 'ids': [1, 2]})
        self.assertNotIn('private', json.dumps(manifest))
        raw['documents_document'][0]['content'] = 'changed'
        with patch.object(ops, 'output', return_value=json.dumps(raw)):
            self.assertNotEqual(manifest, ops.comparison_manifest())
        for table, row in [('documents_tag', {'id': 5, 'name': 'changed'}),
                           ('auth_user', {'id': 1, 'is_active': False})]:
            raw[table] = [row]
            with patch.object(ops, 'output', return_value=json.dumps(raw)):
                self.assertNotEqual(manifest['tables'][table], ops.comparison_manifest()['tables'][table])


# Reuse setup/helpers without running inherited cases twice.
for name in dir(harness.Operations):
    if name.startswith('test_') and name not in ArchiveSafety.__dict__:
        setattr(ArchiveSafety, name, None)
