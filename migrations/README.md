# TOTE SQLite migrations

The canonical fresh-build schema is `schema.sql`. It now creates the additive GST taxonomy/contribution tables and sets SQLite `PRAGMA user_version=2`. `src/build_db.py` consumes that schema when rebuilding its staged database; existing seed records and the legacy JSON export shape remain unchanged.

## Migration 002

`002_gst_taxonomy_additive.sql` applies the same additive schema to an existing pre-v2 TOTE database. It preserves the existing TOTE tables and installs the taxonomy, provenance, validation, review, and admission structures plus their integrity triggers.

Before applying this script to an existing database, inspect its current `PRAGMA user_version` and back up the database. Apply only to the existing pre-v2 schema (version 0 or 1); do not apply it to a database whose version is greater than 2. After application, confirm `PRAGMA user_version` is 2. Migration execution and database conformance tests are deferred for the approved later test pass.

Migration 002 creates schema structures only. It does not infer taxonomy or actor/action/object/tool rows for existing seed loops, admit them, or change the current exported JSON fields.
