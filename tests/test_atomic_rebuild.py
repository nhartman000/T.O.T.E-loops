"""A failed canonical rebuild must leave the previous database and export intact (third-opinion review 2026-11-03)."""
import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import build_db


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class AtomicRebuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='tote-atomic-')
        d = Path(self.temp.name)
        self.db, self.export = d / 'tote_loops.sqlite3', d / 'tote_loops.json'
        with patch.multiple(build_db, DATABASE=self.db, EXPORT=self.export):
            build_db.build()
        self.before = (digest(self.db), digest(self.export))

    def tearDown(self):
        self.temp.cleanup()

    def assert_preserved(self):
        self.assertEqual((digest(self.db), digest(self.export)), self.before)
        conn = sqlite3.connect(self.db)
        try:
            self.assertEqual(conn.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM tote_loops').fetchone()[0], 22)
        finally:
            conn.close()
        self.assertEqual(sorted(p.name for p in self.db.parent.iterdir()), ['tote_loops.json', 'tote_loops.sqlite3'])

    def test_missing_schema_preserves_previous_database(self):
        with patch.multiple(build_db, DATABASE=self.db, EXPORT=self.export, SCHEMA=Path(self.temp.name) / 'missing.sql'):
            with self.assertRaises(FileNotFoundError):
                build_db.build()
        self.assert_preserved()

    def test_failure_during_export_preserves_previous_outputs(self):
        with patch.multiple(build_db, DATABASE=self.db, EXPORT=self.export), \
             patch.object(build_db, 'export_database', side_effect=RuntimeError('boom')):
            with self.assertRaises(RuntimeError):
                build_db.build()
        self.assert_preserved()

    def test_successful_rebuild_is_byte_identical(self):
        with patch.multiple(build_db, DATABASE=self.db, EXPORT=self.export):
            build_db.build()
        self.assertEqual(digest(self.export), self.before[1])


if __name__ == '__main__':
    unittest.main()
