from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "seed_loops.json"
PACKS = ROOT / "data" / "packs"
SCHEMA = ROOT / "schema.sql"
DATABASE = ROOT / "data" / "tote_loops.sqlite3"
EXPORT = ROOT / "data" / "tote_loops.json"

SCHEMA_VERSION = "0.2.0"

SENSES = {"visual", "auditory", "kinesthetic", "olfactory", "gustatory", "instrument", "internal", "none"}
EXTERNAL_SENSES = {"visual", "auditory", "kinesthetic", "olfactory", "gustatory", "instrument"}

# Which operators each phase may use. EXIT carries no operator.
PHASE_OPERATORS = {
    "TEST": {"external_observe", "internal_model"},
    "OPERATE": {"internal_model", "operative_intent", "execute"},
    "EXIT": {None},
}

# Which sense channels each operator may use.
OPERATOR_SENSES = {
    "external_observe": EXTERNAL_SENSES,
    "internal_model": SENSES - {"none", "instrument"},
    "operative_intent": {"internal"},
    "execute": {"kinesthetic", "none"},
    None: {"none"},
}

# Defaults applied to loops that predate versioning (schema 0.1.0 seed).
LOOP_DEFAULTS = {
    "version": 1,
    "status": "CURRENT",
    "supersedes": None,
    "source_basis": "curated seed (schema 0.1.0)",
    "verification_tier": "UNSPECIFIED",
}


class ValidationError(ValueError):
    pass


def template_steps(loop: dict) -> list[dict]:
    """Canonical observe-model-intend-act-observe branch for loops without explicit steps."""
    return [
        {"step_index": 0, "step_label": "observe", "phase": "TEST", "operator_id": "external_observe", "sense_channel": "instrument", "plain_text": loop["initial_test"], "nych_text": f"👀 {loop['initial_test']}", "proposition_kind": "OBSERVED", "provenance": "explicit", "next_on_match": 1, "next_on_mismatch": 1},
        {"step_index": 1, "step_label": "compare", "phase": "TEST", "operator_id": "internal_model", "sense_channel": "internal", "plain_text": "Compare observed state with the exit predicate.", "nych_text": "👁️🧠 compare observed state with protected exit predicate", "proposition_kind": "MODELED", "provenance": "inferred", "next_on_match": 5, "next_on_mismatch": 2},
        {"step_index": 2, "step_label": "select", "phase": "OPERATE", "operator_id": "operative_intent", "sense_channel": "internal", "plain_text": "Select one admissible operation without asserting its outcome.", "nych_text": "🗯️ select one admissible operation; outcome remains predicted", "proposition_kind": "INTENDED", "provenance": "predicted", "next_on_match": 3, "next_on_mismatch": 3},
        {"step_index": 3, "step_label": "execute", "phase": "OPERATE", "operator_id": "execute", "sense_channel": "none", "plain_text": "Execute the selected operation.", "nych_text": "💪 execute selected operation", "proposition_kind": "EXECUTED", "provenance": "explicit", "next_on_match": 4, "next_on_mismatch": 4},
        {"step_index": 4, "step_label": "verify", "phase": "TEST", "operator_id": "external_observe", "sense_channel": "instrument", "plain_text": "Reinspect external evidence; repeat if the exit predicate is false.", "nych_text": "👀 verify postcondition; if mismatch return to 🗯️ then 💪", "proposition_kind": "POSTCONDITION", "provenance": "postcondition", "next_on_match": 5, "next_on_mismatch": 2},
        {"step_index": 5, "step_label": "exit", "phase": "EXIT", "operator_id": None, "sense_channel": "none", "plain_text": loop["exit_predicate"], "nych_text": f"EXIT only if 👀 evidence matches: {loop['exit_predicate']}", "proposition_kind": "POSTCONDITION", "provenance": "postcondition", "next_on_match": None, "next_on_mismatch": 2},
    ]


def explicit_steps(loop: dict, symbols: dict) -> list[dict]:
    """Resolve a loop's authored steps (labels -> indices) and derive the evidentiary fields.

    Authors write only phase, operator, sense, text and branch labels. Proposition kind,
    provenance and NYCH text are derived, so they cannot be mislabelled by hand:
    an observation reached directly from an execution is a POSTCONDITION, never a
    plain OBSERVED fact, and an intention is always a prediction.
    """
    raw = loop["steps"]
    lid = loop["loop_id"]
    labels = [s["id"] for s in raw]
    if len(set(labels)) != len(labels):
        raise ValidationError(f"{lid}: duplicate step ids")
    index = {label: i for i, label in enumerate(labels)}

    def resolve(target, i, field):
        if target is None:
            return None
        if target not in index:
            raise ValidationError(f"{lid}: step '{labels[i]}' {field} -> unknown step '{target}'")
        return index[target]

    steps = []
    for i, s in enumerate(raw):
        default_next = labels[i + 1] if i + 1 < len(raw) else None
        is_exit = s["phase"] == "EXIT"
        steps.append({
            "step_index": i,
            "step_label": s["id"],
            "phase": s["phase"],
            "operator_id": s.get("op"),
            "sense_channel": s.get("sense", "none"),
            "plain_text": s["text"],
            "next_on_match": None if is_exit else resolve(s.get("on_match", default_next), i, "on_match"),
            "next_on_mismatch": resolve(s.get("on_mismatch", None if is_exit else default_next), i, "on_mismatch"),
        })

    post_targets = {st["next_on_match"] for st in steps if st["operator_id"] == "execute"}
    post_targets |= {st["next_on_mismatch"] for st in steps if st["operator_id"] == "execute"}
    for st in steps:
        op = st["operator_id"]
        if st["phase"] == "EXIT":
            kind, prov = "POSTCONDITION", "postcondition"
            st["nych_text"] = f"EXIT only if 👀 evidence matches: {st['plain_text']}"
        else:
            if op == "external_observe":
                if st["step_index"] in post_targets:
                    kind, prov = "POSTCONDITION", "postcondition"
                else:
                    kind, prov = "OBSERVED", "explicit"
            elif op == "internal_model":
                kind, prov = "MODELED", "inferred"
            elif op == "operative_intent":
                kind, prov = "INTENDED", "predicted"
            elif op == "execute":
                kind, prov = "EXECUTED", "explicit"
            else:
                raise ValidationError(f"{lid}: step '{st['step_label']}' has unknown operator {op!r}")
            st["nych_text"] = f"{symbols[op]} {st['plain_text']}"
        st["proposition_kind"], st["provenance"] = kind, prov
    return steps


def validate_steps(lid: str, steps: list[dict]) -> None:
    """Deterministic integrity rules every loop must satisfy before it enters the database."""
    problems = []
    n = len(steps)
    exits = [s for s in steps if s["phase"] == "EXIT"]
    if len(exits) != 1 or steps[-1]["phase"] != "EXIT":
        problems.append("must have exactly one EXIT step, placed last")
    exit_index = n - 1
    if not any(s["operator_id"] == "execute" for s in steps):
        problems.append("must contain at least one 💪 execute step")
    for s in steps:
        label, op, sense = s["step_label"], s["operator_id"], s["sense_channel"]
        if op not in PHASE_OPERATORS[s["phase"]]:
            problems.append(f"'{label}': operator {op!r} not allowed in phase {s['phase']}")
        if sense not in OPERATOR_SENSES.get(op, set()):
            problems.append(f"'{label}': sense '{sense}' not allowed for operator {op!r}")
        for field in ("next_on_match", "next_on_mismatch"):
            t = s[field]
            if t is not None and not 0 <= t < n:
                problems.append(f"'{label}': {field} out of range")
        if s["phase"] != "EXIT" and (s["next_on_match"] is None or s["next_on_mismatch"] is None):
            problems.append(f"'{label}': non-exit steps need both branches")
        if s["phase"] == "EXIT" and s["next_on_mismatch"] is None:
            problems.append("EXIT needs a mismatch branch (loop back when the predicate is false)")
        # Every action must be followed by a fresh external observation.
        if op == "execute":
            for field in ("next_on_match", "next_on_mismatch"):
                t = s[field]
                if t is None or steps[t]["operator_id"] != "external_observe":
                    problems.append(f"'{label}': 💪 must be followed by a fresh 👀 observation ({field})")
        # Only a fresh external observation may license EXIT.
        if s["next_on_match"] == exit_index and s["phase"] != "EXIT":
            if op not in ("external_observe", "internal_model") or s["phase"] != "TEST":
                problems.append(f"'{label}': only a TEST step may lead to EXIT")
        if s["next_on_mismatch"] == exit_index and s["phase"] != "EXIT":
            problems.append(f"'{label}': a mismatch may never lead to EXIT")
    # An internal model that licenses EXIT must itself rest on a fresh observation.
    for s in steps:
        if s["next_on_match"] == exit_index and s["operator_id"] == "internal_model":
            feeders = [p for p in steps if p["next_on_match"] == s["step_index"]]
            if not feeders or any(p["operator_id"] != "external_observe" for p in feeders):
                problems.append(f"'{s['step_label']}': a 👁️🧠 comparison that licenses EXIT must be fed only by 👀 observation")
    # Every step must be reachable from the first, and EXIT must be reachable.
    if n and not problems:
        seen, stack = set(), [0]
        while stack:
            i = stack.pop()
            if i in seen:
                continue
            seen.add(i)
            stack += [t for t in (steps[i]["next_on_match"], steps[i]["next_on_mismatch"]) if t is not None]
        unreachable = [steps[i]["step_label"] for i in range(n) if i not in seen]
        if unreachable:
            problems.append(f"unreachable steps: {', '.join(unreachable)}")
    if problems:
        raise ValidationError(f"{lid}: " + "; ".join(problems))


def load_seed() -> tuple[dict, bytes]:
    """Merge the base seed with every pack in data/packs, in sorted filename order."""
    parts = [SEED.read_bytes()]
    seed = json.loads(parts[0])
    gestalts = {g["gestalt_id"]: g for g in seed["gestalts"]}
    loops = list(seed["loops"])
    for pack_path in sorted(PACKS.glob("*.json")) if PACKS.exists() else []:
        raw = pack_path.read_bytes()
        parts.append(raw)
        pack = json.loads(raw)
        for g in pack.get("gestalts", []):
            if g["gestalt_id"] in gestalts and gestalts[g["gestalt_id"]] != g:
                raise ValidationError(f"{pack_path.name}: conflicting gestalt {g['gestalt_id']}")
            gestalts[g["gestalt_id"]] = g
        loops.extend(pack["loops"])
    seed["gestalts"] = [gestalts[k] for k in sorted(gestalts)]
    seed["loops"] = loops
    digest = hashlib.sha256(b"\n".join(parts))
    return seed, digest.hexdigest().encode()


def export_database(conn: sqlite3.Connection, seed_hash: str) -> dict:
    conn.row_factory = sqlite3.Row
    loops = []
    for row in conn.execute("SELECT * FROM tote_loops ORDER BY loop_id"):
        item = dict(row)
        item["gestalts"] = [dict(x) for x in conn.execute("SELECT g.*, lg.role FROM gestalts g JOIN loop_gestalts lg USING (gestalt_id) WHERE lg.loop_id=? ORDER BY g.gestalt_id", (row["loop_id"],))]
        item["steps"] = [dict(x) for x in conn.execute("SELECT * FROM tote_steps WHERE loop_id=? ORDER BY step_index", (row["loop_id"],))]
        loops.append(item)
    return {
        "schema_version": SCHEMA_VERSION,
        "seed_sha256": seed_hash,
        "operators": [dict(x) for x in conn.execute("SELECT * FROM modality_operators ORDER BY operator_id")],
        "loops": loops,
    }


LOOP_COLUMNS = ("loop_id", "behavior_id", "version", "status", "supersedes", "name", "domain", "objective", "initial_test", "exit_predicate", "max_iterations", "epistemic_status", "source_basis", "verification_tier")
STEP_COLUMNS = ("loop_id", "step_index", "step_label", "phase", "operator_id", "sense_channel", "plain_text", "nych_text", "proposition_kind", "provenance", "next_on_match", "next_on_mismatch")


def build() -> None:
    seed, seed_hash = load_seed()
    symbols = {op["operator_id"]: op["symbol"] for op in seed["operators"]}
    DATABASE.unlink(missing_ok=True)
    conn = sqlite3.connect(DATABASE)
    try:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.executemany("INSERT INTO modality_operators VALUES (:operator_id,:symbol,:canonical_name,:definition,:evidence_channel,:may_assert_action)", seed["operators"])
        conn.executemany("INSERT INTO gestalts VALUES (:gestalt_id,:glyph,:lexical_form,:sense,:route,:recoverability_note)", seed["gestalts"])
        # Insert superseded targets before the rows that point at them.
        ordered = sorted(seed["loops"], key=lambda l: (l.get("version", 1), l["loop_id"]))
        resolved, errors = [], []
        for raw in ordered:
            loop = {**LOOP_DEFAULTS, "behavior_id": raw["loop_id"], **raw}
            try:
                steps = explicit_steps(loop, symbols) if "steps" in loop else template_steps(loop)
                validate_steps(loop["loop_id"], steps)
            except ValidationError as exc:
                errors.append(str(exc))
                continue
            resolved.append((loop, steps))
        if errors:
            raise ValidationError(f"{len(errors)} loop(s) failed validation:\n  " + "\n  ".join(errors))
        for loop, steps in resolved:
            conn.execute(f"INSERT INTO tote_loops ({','.join(LOOP_COLUMNS)}) VALUES ({','.join('?' * len(LOOP_COLUMNS))})", tuple(loop[k] for k in LOOP_COLUMNS))
            for gestalt_id in loop.get("gestalts", []):
                conn.execute("INSERT INTO loop_gestalts VALUES (?,?,?)", (loop["loop_id"], gestalt_id, "process-context"))
            for step in steps:
                conn.execute(f"INSERT INTO tote_steps ({','.join(STEP_COLUMNS)}) VALUES ({','.join('?' * len(STEP_COLUMNS))})", (loop["loop_id"],) + tuple(step[k] for k in STEP_COLUMNS[1:]))
        conn.commit()
        exported = export_database(conn, seed_hash.decode())
        EXPORT.write_text(json.dumps(exported, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except Exception:
        conn.close()
        DATABASE.unlink(missing_ok=True)
        raise
    conn.close()


if __name__ == "__main__":
    build()
