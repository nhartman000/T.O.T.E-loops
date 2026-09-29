import json
import sqlite3
import unittest

from src.build_db import (
    DATABASE, EXPORT, SCHEMA, SCHEMA_VERSION, ValidationError,
    build, explicit_steps, load_seed, validate_steps,
)

SYMBOLS = {"external_observe": "👀", "internal_model": "👁️🧠", "operative_intent": "🗯️", "execute": "💪"}


def resolve(steps):
    loop = {"loop_id": "t.loop.v1", "steps": steps}
    return explicit_steps(loop, SYMBOLS)


class DatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()
        cls.seed, _ = load_seed()

    def query(self, sql, *args):
        conn = sqlite3.connect(DATABASE)
        try:
            return conn.execute(sql, args).fetchall()
        finally:
            conn.close()

    def test_counts_match_seed_and_foreign_keys(self):
        self.assertEqual(self.query("SELECT COUNT(*) FROM modality_operators")[0][0], 13)
        self.assertEqual(self.query("SELECT COUNT(*) FROM tote_loops")[0][0], len(self.seed["loops"]))
        self.assertEqual(self.query("PRAGMA foreign_key_check"), [])

    def test_canonical_annotation_operators(self):
        expected = {
            "internal_sensation": "🫀",
            "first_person": "👤",
            "second_person": "👥️",
            "third_person_narrative": "🗣",
            "past_tense": "⏪️",
            "present_tense": "🎁",
            "future_tense": "⏩️",
            "internal_auditory": "👂",
            "external_auditory": "👂👂",
        }
        rows = dict(self.query("SELECT operator_id, symbol FROM modality_operators"))
        for operator_id, symbol in expected.items():
            self.assertEqual(rows.get(operator_id), symbol)
        definitions = dict(self.query("SELECT operator_id, definition FROM modality_operators"))
        self.assertIn("Hidden computation is not excluded", definitions["internal_auditory"])
        self.assertIn("unmarked process is unspecified, not absent", definitions["internal_auditory"])
        self.assertIn("every user-facing response", definitions["external_auditory"])

    def test_original_seed_loops_unchanged(self):
        # The ten schema-0.1.0 loops keep their six template steps and become CURRENT v1.
        rows = self.query("SELECT loop_id, version, status, (SELECT COUNT(*) FROM tote_steps s WHERE s.loop_id=l.loop_id) FROM tote_loops l WHERE verification_tier='UNSPECIFIED'")
        self.assertEqual(len(rows), 10)
        for _, version, status, n in rows:
            self.assertEqual((version, status, n), (1, "CURRENT", 6))

    def test_every_execution_is_followed_by_fresh_observation(self):
        bad = self.query("""
            SELECT COUNT(*) FROM tote_steps s WHERE s.operator_id='execute' AND (
              NOT EXISTS (SELECT 1 FROM tote_steps t WHERE t.loop_id=s.loop_id AND t.step_index=s.next_on_match AND t.operator_id='external_observe')
              OR NOT EXISTS (SELECT 1 FROM tote_steps t WHERE t.loop_id=s.loop_id AND t.step_index=s.next_on_mismatch AND t.operator_id='external_observe'))""")
        self.assertEqual(bad[0][0], 0)

    def test_exit_requires_postcondition_and_is_last(self):
        self.assertEqual(self.query("SELECT COUNT(*) FROM tote_steps WHERE phase='EXIT' AND proposition_kind!='POSTCONDITION'")[0][0], 0)
        bad = self.query("SELECT COUNT(*) FROM tote_steps s WHERE phase='EXIT' AND step_index != (SELECT MAX(step_index) FROM tote_steps t WHERE t.loop_id=s.loop_id)")
        self.assertEqual(bad[0][0], 0)

    def test_no_mismatch_leads_to_exit(self):
        bad = self.query("SELECT COUNT(*) FROM tote_steps s JOIN tote_steps e ON e.loop_id=s.loop_id AND e.phase='EXIT' WHERE s.phase!='EXIT' AND s.next_on_mismatch=e.step_index")
        self.assertEqual(bad[0][0], 0)

    def test_observation_reached_from_action_is_postcondition(self):
        bad = self.query("""
            SELECT COUNT(*) FROM tote_steps s JOIN tote_steps t ON t.loop_id=s.loop_id AND t.step_index=s.next_on_match
            WHERE s.operator_id='execute' AND t.proposition_kind!='POSTCONDITION'""")
        self.assertEqual(bad[0][0], 0)

    def test_external_observation_uses_an_external_sense(self):
        bad = self.query("SELECT COUNT(*) FROM tote_steps WHERE operator_id='external_observe' AND sense_channel IN ('internal','none')")
        self.assertEqual(bad[0][0], 0)

    def test_at_most_one_current_version_per_behavior(self):
        self.assertEqual(self.query("SELECT behavior_id FROM tote_loops WHERE status='CURRENT' GROUP BY behavior_id HAVING COUNT(*) > 1"), [])

    def test_machine_drafted_loops_are_not_promoted(self):
        bad = self.query("SELECT COUNT(*) FROM tote_loops WHERE verification_tier='MACHINE_DRAFTED' AND (status='CURRENT' OR epistemic_status!='EXPERIMENTAL')")
        self.assertEqual(bad[0][0], 0)

    def test_json_export_is_valid(self):
        data = json.loads(EXPORT.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], SCHEMA_VERSION)
        self.assertEqual(len(data["loops"]), len(self.seed["loops"]))


class VersioningTests(unittest.TestCase):
    """No loop is definitive: a new version supersedes an old one without deleting it."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(SCHEMA.read_text(encoding="utf-8"))

    def tearDown(self):
        self.conn.close()

    def insert(self, loop_id, version, status, supersedes=None):
        self.conn.execute(
            "INSERT INTO tote_loops (loop_id, behavior_id, version, status, supersedes, name, domain, objective, initial_test, exit_predicate, max_iterations, epistemic_status, source_basis, verification_tier) "
            "VALUES (?, 'b', ?, ?, ?, 'n', 'd', 'o', 'i', 'e', 1, 'EXPERIMENTAL', 's', 'HUMAN_REVIEWED')",
            (loop_id, version, status, supersedes))

    def test_two_current_versions_are_rejected(self):
        self.insert("b.v1", 1, "CURRENT")
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert("b.v2", 2, "CURRENT", "b.v1")

    def test_supersession_keeps_history(self):
        self.insert("b.v1", 1, "SUPERSEDED")
        self.insert("b.v2", 2, "CURRENT", "b.v1")
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM tote_loops WHERE behavior_id='b'").fetchone()[0], 2)


class ValidatorTests(unittest.TestCase):
    def ok(self):
        return [
            {"id": "look", "phase": "TEST", "op": "external_observe", "sense": "visual", "text": "look"},
            {"id": "act", "phase": "OPERATE", "op": "execute", "sense": "kinesthetic", "text": "act"},
            {"id": "see", "phase": "TEST", "op": "external_observe", "sense": "visual", "text": "see", "on_match": "exit", "on_mismatch": "act"},
            {"id": "exit", "phase": "EXIT", "op": None, "sense": "none", "text": "done", "on_mismatch": "act"},
        ]

    def test_valid_loop_passes(self):
        validate_steps("t", resolve(self.ok()))

    def test_action_without_fresh_observation_rejected(self):
        steps = self.ok()
        steps.insert(2, {"id": "think", "phase": "OPERATE", "op": "internal_model", "sense": "visual", "text": "think"})
        with self.assertRaises(ValidationError):
            validate_steps("t", resolve(steps))

    def test_mismatch_to_exit_rejected(self):
        steps = self.ok()
        steps[2]["on_mismatch"] = "exit"
        with self.assertRaises(ValidationError):
            validate_steps("t", resolve(steps))

    def test_internal_sense_on_external_observation_rejected(self):
        steps = self.ok()
        steps[0]["sense"] = "internal"
        with self.assertRaises(ValidationError):
            validate_steps("t", resolve(steps))

    def test_model_cannot_license_exit_after_action(self):
        steps = self.ok()
        steps[2] = {"id": "see", "phase": "TEST", "op": "external_observe", "sense": "visual", "text": "see", "on_mismatch": "act"}
        steps.insert(3, {"id": "judge", "phase": "TEST", "op": "internal_model", "sense": "visual", "text": "judge", "on_match": "exit", "on_mismatch": "act"})
        validate_steps("t", resolve(steps))  # fed by observation: allowed
        steps[1]["on_match"] = "judge"
        steps[1]["on_mismatch"] = "judge"
        with self.assertRaises(ValidationError):
            validate_steps("t", resolve(steps))

    def test_unknown_branch_target_rejected(self):
        steps = self.ok()
        steps[2]["on_mismatch"] = "nowhere"
        with self.assertRaises(ValidationError):
            resolve(steps)


if __name__ == "__main__":
    unittest.main()
