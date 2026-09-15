# TOTE-Loops

Canonical seed database for describing software and AI control loops using the
current NYCH modality operators and Test–Operate–Test–Exit structure.

The database stores the semantic process first. Emoji are sparse annotations,
not replacements for every word.

## Canonical operators

| Symbol | Meaning |
| --- | --- |
| `👀` | externally observe or inspect evidence |
| `👁️🧠` | internally model, imagine, recall, or compare |
| `🗯️` | operative thought or intention |
| `💪` | execute an operation |

An action is never recorded as an observation. A predicted postcondition is not
promoted to an observed state. A loop exits only after external evidence matches
the declared exit predicate.

## Build and verify

```bash
python -m src.build_db
python -m unittest discover -s tests
```

This produces `data/tote_loops.sqlite3` and the deterministic export
`data/tote_loops.json` from `data/seed_loops.json`.

## Initial scope

The first population contains curated loops for unit testing, debugging, CI
repair, LLM output gating, retrieval grounding, tool-call verification,
multi-agent relay integrity, memory round trips, dependency repair, and model
evaluation.

## Epistemic status

This repository is a seed ontology and reference dataset. Entries describe
admissible control-loop structures; they are not evidence that a specific AI
system executed those loops successfully.
