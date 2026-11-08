# TOTE SQLite migrations

The canonical fresh-build schema is `schema.sql`. It creates the additive GST taxonomy/contribution tables and sets SQLite `PRAGMA user_version=2`. `src/build_db.py` consumes that schema when rebuilding its staged database; existing seed records and the legacy JSON export shape remain unchanged.

## Migration 002

`002_gst_taxonomy_additive.sql` applies the additive schema to an existing pre-v2 TOTE database. It preserves the existing TOTE tables and installs taxonomy, provenance, validation, review, and admission structures plus their integrity triggers. The SQL file does not change `user_version` itself; the guarded runner records version 2 only after the DDL and database checks succeed.

From the repository root, apply it with:

```sh
python migrations/apply_002.py
```

Pass a database path to target a different file:

```sh
python migrations/apply_002.py path/to/tote_loops.sqlite3
```

The runner enables foreign keys before opening an immediate transaction. It applies only when `PRAGMA user_version` is 0 or 1, returns without changes at version 2, and refuses versions above 2 or other unsupported versions. It runs `integrity_check` and `foreign_key_check` inside the transaction before committing. Any error rolls the migration back. Back up the database before applying it.

Migration 002 creates schema structures only. It does not infer taxonomy or actor/action/object/tool rows for existing seed loops, admit them, or change the current exported JSON fields. Migration execution and conformance tests are deferred for the later test pass requested by the owner.
