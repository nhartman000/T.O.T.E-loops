from __future__ import annotations

import argparse
from pathlib import Path
import sqlite3
import sys


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = Path(__file__).with_name("002_gst_taxonomy_additive.sql")
TARGET_VERSION = 2
SUPPORTED_SOURCE_VERSIONS = {0, 1}


def _statements(sql: str):
    """Yield complete SQLite statements, including compound trigger bodies."""
    buffer = ""
    for line in sql.splitlines(keepends=True):
        buffer += line
        if sqlite3.complete_statement(buffer):
            statement = buffer.strip()
            if statement:
                yield statement
            buffer = ""
    if buffer.strip():
        raise ValueError("migration ends with an incomplete SQL statement")


def apply(database: Path) -> str:
    if not database.is_file():
        raise FileNotFoundError(f"database not found: {database}")
    sql = MIGRATION.read_text(encoding="utf-8")
    conn = sqlite3.connect(database, isolation_level=None)
    try:
        # Foreign-key enforcement must be enabled before BEGIN; SQLite ignores
        # attempts to change this pragma from inside an active transaction.
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("BEGIN IMMEDIATE")
        version = int(conn.execute("PRAGMA user_version").fetchone()[0])

        if version == TARGET_VERSION:
            conn.execute("ROLLBACK")
            return "already at schema version 2; no changes made"
        if version > TARGET_VERSION:
            raise RuntimeError(
                f"database schema version {version} is newer than supported version 2"
            )
        if version not in SUPPORTED_SOURCE_VERSIONS:
            raise RuntimeError(
                f"database schema version {version} is unsupported; expected 0 or 1"
            )

        for statement in _statements(sql):
            # The SQL file's FK pragma is harmless here; it matches the
            # connection setting established before the transaction.
            conn.execute(statement)

        # Version changes only after every DDL statement has succeeded. Checks
        # remain inside the same transaction, so any failure rolls back both.
        conn.execute(f"PRAGMA user_version = {TARGET_VERSION}")
        integrity = conn.execute("PRAGMA integrity_check").fetchall()
        if integrity != [("ok",)]:
            raise RuntimeError(f"integrity_check failed: {integrity!r}")
        foreign_key_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_key_errors:
            raise RuntimeError(f"foreign_key_check failed: {foreign_key_errors!r}")

        conn.execute("COMMIT")
        return "migration 002 applied; schema version is 2"
    except BaseException:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply TOTE GST taxonomy migration 002 atomically."
    )
    parser.add_argument(
        "database",
        nargs="?",
        type=Path,
        default=ROOT / "data" / "tote_loops.sqlite3",
        help="SQLite database path (default: data/tote_loops.sqlite3)",
    )
    args = parser.parse_args()
    try:
        print(apply(args.database))
    except (OSError, sqlite3.Error, RuntimeError, ValueError) as exc:
        print(f"migration failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
