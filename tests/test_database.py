import json
import sqlite3
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from src import build_db
from src.build_db import DATABASE, EXPORT, build


class DatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global DATABASE, EXPORT
        cls.temp = tempfile.TemporaryDirectory(prefix='tote-db-tests-')
        DATABASE = Path(cls.temp.name)/'tote_loops.sqlite3'
        EXPORT = Path(cls.temp.name)/'tote_loops.json'
        with patch.multiple(build_db, DATABASE=DATABASE, EXPORT=EXPORT):
            build()

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_build_is_isolated_from_repository_outputs(self):
        self.assertNotEqual(DATABASE, build_db.DATABASE)
        self.assertNotEqual(EXPORT, build_db.EXPORT)

    def test_seed_counts_and_foreign_keys(self):
        conn = sqlite3.connect(DATABASE)
        try:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM modality_operators").fetchone()[0], 4)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM tote_loops").fetchone()[0], 22)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM tote_steps").fetchone()[0], 132)
            self.assertEqual(conn.execute("PRAGMA foreign_key_check").fetchall(), [])
        finally:
            conn.close()

    def test_every_loop_retests_after_execution(self):
        conn = sqlite3.connect(DATABASE)
        try:
            bad = conn.execute("SELECT COUNT(*) FROM tote_steps WHERE phase='OPERATE' AND operator_id='execute' AND next_on_match NOT IN (SELECT step_index FROM tote_steps t2 WHERE t2.loop_id=tote_steps.loop_id AND t2.phase='TEST')").fetchone()[0]
            self.assertEqual(bad, 0)
        finally:
            conn.close()

    def test_exit_requires_postcondition(self):
        conn = sqlite3.connect(DATABASE)
        try:
            bad = conn.execute("SELECT COUNT(*) FROM tote_steps WHERE phase='EXIT' AND proposition_kind!='POSTCONDITION'").fetchone()[0]
            self.assertEqual(bad, 0)
        finally:
            conn.close()

    def test_json_export_is_valid(self):
        data = json.loads(EXPORT.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], "0.1.0")
        self.assertEqual(len(data["loops"]), 22)


if __name__ == "__main__":
    unittest.main()

