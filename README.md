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

## No loop is definitive

A loop is the **best accepted version for now**, not the one true way to do
something. Each row in `tote_loops` is one *version* of a behavior:

- `behavior_id` names the behavior (for example `trade.painting.load_brush`);
  `loop_id` names one version of it (`trade.painting.load_brush.v1`).
- `status` is `CURRENT` (best accepted version), `CANDIDATE` (proposed, not yet
  accepted), or `SUPERSEDED` (replaced by a better version). The database allows
  at most one `CURRENT` version per behavior.
- A better way of doing something is added as a new version with `supersedes`
  pointing at the old one. Old versions are kept, never deleted, so the history
  of how a behavior improved stays in the record.
- `verification_tier` records how far a version has been checked:
  `MACHINE_DRAFTED` → `HUMAN_REVIEWED` → `HUMAN_VERIFIED` →
  `OBSERVATION_VERIFIED` (checked against recorded behavior). Machine-drafted
  loops cannot be `CURRENT`.

To accept a candidate: review it, raise its `verification_tier`, set its
`status` to `CURRENT`, and set any previous `CURRENT` version of the same
behavior to `SUPERSEDED`.

## Sense channels

Every step records the sense that carries it in `sense_channel`: `visual`,
`auditory`, `kinesthetic`, `olfactory`, `gustatory`, `instrument` (evidence read
from a tool, log, or measurement), `internal`, or `none`. For 👀 steps it is the
sense the evidence arrives through; for 👁️🧠 steps it is the modality being
imagined or recalled (picturing a stroke is `visual`, recalling the feel of a
loaded brush is `kinesthetic`).

## Loop packs and authored steps

Additional loops live in `data/packs/*.json`, merged with the base seed at
build time. A loop may carry its own `steps`; if it does not, the six-step
template is used. Authors write only the phase, operator, sense, text, and
branch labels:

```json
{"id": "feel_hold", "phase": "TEST", "op": "external_observe", "sense": "kinesthetic",
 "text": "Hold the brush level; feel the weight and watch for a drop.",
 "on_match": "exit", "on_mismatch": "intend"}
```

Branches default to the next step. `proposition_kind`, `provenance`, and the
NYCH text are derived by the builder so they cannot be mislabelled by hand
(an observation reached directly from an action is always a `POSTCONDITION`).
The build rejects any loop that breaks the integrity rules: every 💪 must be
followed by a fresh 👀 on both branches, only a TEST step may lead to EXIT, a
mismatch never leads to EXIT, a 👁️🧠 comparison may license EXIT only when fed
by 👀 observation, and every step must be reachable.

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

The `trades_*` packs add 51 construction-trade loops (painting, drywall,
carpentry, general site work). They are machine-drafted candidates: status
`CANDIDATE`, epistemic status `EXPERIMENTAL`, tier `MACHINE_DRAFTED`. Their
`source_basis` cites an O*NET-SOC occupation as a reference only; the steps
themselves have not been observed or verified.

## Epistemic status

This repository is a seed ontology and reference dataset. Entries describe
admissible control-loop structures; they are not evidence that a specific AI
system executed those loops successfully.
