from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "seed_loops.json"
SCHEMA = ROOT / "schema.sql"
DATABASE = ROOT / "data" / "tote_loops.sqlite3"
EXPORT = ROOT / "data" / "tote_loops.json"


def steps_for(loop: dict) -> list[dict]:
    """Construct the canonical observe-model-intend-act-observe branch."""
    return [
        {"step_index": 0, "phase": "TEST", "operator_id": "external_observe", "plain_text": loop["initial_test"], "nych_text": f"👀 {loop['initial_test']}", "proposition_kind": "OBSERVED", "provenance": "explicit", "next_on_match": 1, "next_on_mismatch": 1},
        {"step_index": 1, "phase": "TEST", "operator_id": "internal_model", "plain_text": "Compare observed state with the exit predicate.", "nych_text": "👁️🧠 compare observed state with protected exit predicate", "proposition_kind": "MODELED", "provenance": "inferred", "next_on_match": 5, "next_on_mismatch": 2},
        {"step_index": 2, "phase": "OPERATE", "operator_id": "operative_intent", "plain_text": "Select one admissible operation without asserting its outcome.", "nych_text": "🗯️ select one admissible operation; outcome remains predicted", "proposition_kind": "INTENDED", "provenance": "predicted", "next_on_match": 3, "next_on_mismatch": 3},
        {"step_index": 3, "phase": "OPERATE", "operator_id": "execute", "plain_text": "Execute the selected operation.", "nych_text": "💪 execute selected operation", "proposition_kind": "EXECUTED", "provenance": "explicit", "next_on_match": 4, "next_on_mismatch": 4},
        {"step_index": 4, "phase": "TEST", "operator_id": "external_observe", "plain_text": "Reinspect external evidence; repeat if the exit predicate is false.", "nych_text": "👀 verify postcondition; if mismatch return to 🗯️ then 💪", "proposition_kind": "POSTCONDITION", "provenance": "postcondition", "next_on_match": 5, "next_on_mismatch": 2},
        {"step_index": 5, "phase": "EXIT", "operator_id": None, "plain_text": loop["exit_predicate"], "nych_text": f"EXIT only if 👀 evidence matches: {loop['exit_predicate']}", "proposition_kind": "POSTCONDITION", "provenance": "postcondition", "next_on_match": None, "next_on_mismatch": 2}
    ]


def export_database(conn: sqlite3.Connection, seed_hash: str) -> dict:
    conn.row_factory = sqlite3.Row
    loops = []
    for row in conn.execute("SELECT * FROM tote_loops ORDER BY loop_id"):
        item = dict(row)
        item["gestalts"] = [dict(x) for x in conn.execute("SELECT g.*, lg.role FROM gestalts g JOIN loop_gestalts lg USING (gestalt_id) WHERE lg.loop_id=? ORDER BY g.gestalt_id", (row["loop_id"],))]
        item["steps"] = [dict(x) for x in conn.execute("SELECT * FROM tote_steps WHERE loop_id=? ORDER BY step_index", (row["loop_id"],))]
        loops.append(item)
    return {
        "schema_version": "0.1.0",
        "seed_sha256": seed_hash,
        "operators": [dict(x) for x in conn.execute("SELECT * FROM modality_operators ORDER BY operator_id")],
        "loops": loops,
    }


def build() -> None:
    seed_bytes = SEED.read_bytes()
    seed = json.loads(seed_bytes)
    DATABASE.unlink(missing_ok=True)
    conn = sqlite3.connect(DATABASE)
    try:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.executemany("INSERT INTO modality_operators VALUES (:operator_id,:symbol,:canonical_name,:definition,:evidence_channel,:may_assert_action)", seed["operators"])
        conn.executemany("INSERT INTO gestalts VALUES (:gestalt_id,:glyph,:lexical_form,:sense,:route,:recoverability_note)", seed["gestalts"])
        for loop in seed["loops"]:
            conn.execute("INSERT INTO tote_loops VALUES (?,?,?,?,?,?,?,?)", tuple(loop[k] for k in ("loop_id","name","domain","objective","initial_test","exit_predicate","max_iterations","epistemic_status")))
            for gestalt_id in loop["gestalts"]:
                conn.execute("INSERT INTO loop_gestalts VALUES (?,?,?)", (loop["loop_id"], gestalt_id, "process-context"))
            for step in steps_for(loop):
                conn.execute("INSERT INTO tote_steps VALUES (?,?,?,?,?,?,?,?,?,?)", (loop["loop_id"], step["step_index"], step["phase"], step["operator_id"], step["plain_text"], step["nych_text"], step["proposition_kind"], step["provenance"], step["next_on_match"], step["next_on_mismatch"]))
        conn.commit()
        exported = export_database(conn, hashlib.sha256(seed_bytes).hexdigest())
        EXPORT.write_text(json.dumps(exported, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    finally:
        conn.close()


if __name__ == "__main__":
    build()
