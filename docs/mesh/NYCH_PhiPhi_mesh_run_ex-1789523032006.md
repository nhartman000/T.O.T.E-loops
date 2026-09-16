# NYCH PhiPhi Mesh Run — ex-1789523032006

**Status:** Architecture/design record only. **Not database population.**

This document preserves the substantive consensus reached during the PhiPhi multi-agent NYCH/T.O.T.E. mesh run. Participants: ChatGPT `nx-001`, Gemini `nx-002`, Gemini `nx-003`.

## Core normative specification

### Four orthogonal modality operators
- `👀 X` — external observation / sensor-environment capture.
- `👁️🧠 X` — internal model, prediction, expectation, or belief.
- `🗯️ X` — explicitly licensed operative intention / target.
- `💪 X` — executed physical or operational action.

These types are invariant. Confidence does not change modality.

### Anti-promotion invariants
1. `ACT(T) ⇏ OBS(Postcondition(T))` — execution never proves its expected result.
2. `ACT(P) ⇏ INTENT(P)` — an action never proves the actor's goal.
3. `MODEL(X) ⇏ OBS(X)` — belief/prediction never becomes observation merely through confidence.
4. `END(trace) ≠ EXIT(TOTE)` — narrative termination is not verified goal satisfaction.

## Dual residuals

NYCH evaluates two distinct errors:

`E_model = Δ(OBS, MODEL)` — epistemic/model residual.

`E_goal = Δ(OBS, INTENT)` — goal/control residual.

Residual domain is `{MATCH, MISMATCH, UNKNOWN(⊥)}`. A residual is `⊥` whenever either required operand is absent, unlicensed, stale, conflicted, or otherwise unresolved. Absence of mismatch is never evidence of match.

### Control matrix
| State | E_model | E_goal | Required transition |
|---|---|---|---|
| A | MATCH | MATCH | verified target satisfaction → EXIT |
| B | MATCH | MISMATCH | PLAN → authorization → ACT |
| C | MISMATCH | MATCH | UPDATE MODEL; suppress actuator |
| D | MISMATCH | MISMATCH | UPDATE MODEL → REPLAN → authorization → ACT |
| PARTIAL | either `⊥` | either `⊥` | preserve partial state; request/await evidence; no default A |

State C is important: a stale model does not justify actuation when reality already satisfies the goal.

## Action authorization

Residual resolution does not directly invoke `💪`. B/D authorize planning, after which an explicit single-use `ActionPermit` is required.

Conceptual permit:

`ActionPermit(instance_id, epoch, revision, state∈{B,D}, plan_hash, semantic_hash, status)`

`status ∈ {ISSUED, CONSUMED, REVOKED, EXPIRED}`

The permit is bound to the exact normative snapshot and plan. Changes to relevant observation/model/intention/provenance/comparison semantics invalidate it. Dispatch must atomically revalidate and consume the permit before recording ACT, preventing stale or replayed authorization.

ACT appends an actuation event only. It never synthesizes expected `👀` evidence.

## Temporal semantics

Separate:
- `epoch`: changes across an executed action / verification boundary.
- `revision`: changes when licensed semantic/provenance state changes within an epoch.

After successful ACT, open the next verification epoch. Historical residuals remain immutable. MODEL and INTENT may be explicitly carried forward as references to their original assertions when scope permits; OBS cannot be carried forward as post-action verification.

Therefore a newly opened post-action epoch has unresolved postcondition residuals until fresh licensed observation arrives.

A later observation may verify the post-action state without proving that the action caused it. Causal attribution and temporal validity are separate.

## Event-sourced reference architecture

Target structure:

`Immutable Event Log → Pure Reducer → Derived NYCH State → Authorization`

No controller directly edits derived state.

Recommended event partition:
- Evidence: `Observe`, `ModelAssert`, `IntentAssert`
- Execution: `Actuate`
- Governance: `PlanCommit`, `PermitIssue`, `PermitRevoke`, `ExitIssue`, `RequestEvidence`, retraction/supersession records

Governance records are not evidence operands and cannot enter Δ. This prevents circular justification (for example, an ExitCertificate cannot itself prove E_goal=MATCH).

Historical state is reproducible from a causal cut of the append-only event log. Retractions/corrections append new events rather than rewriting history.

## Exit authorization

EXIT should be mechanically auditable rather than inferred from narrative completion. A conceptual certificate binds the evidence and semantics used to justify State A:

`ExitCertificate(instance, epoch, revision, obs_ref, model_ref, intent_ref, E_model=MATCH, E_goal=MATCH, semantic_hash)`

An authorization certificate is downstream of evidence and residual computation; it is never evidence itself.

## Evidence conflicts and fusion

Multiple observations must be resolved before Δ. Contradictory evidence must not be arbitrarily converted into MATCH/MISMATCH.

Conceptual resolution:

`resolve_OBS(instance, epoch, state_rep) → OBS* | ⊥`

Diagnostic reasons for `⊥` may include `MISSING`, `CONFLICT`, `STALE`, `INVALID_PROVENANCE`, while the normative residual algebra remains ternary.

Derived/fused observations must preserve a provenance DAG and use an explicitly admissible transform:

`DerivedOBS = f(OBS_1 … OBS_n; transform_id)`

Licensing requires the transform and all required ancestors to remain valid. Retraction/mutation of an ancestor invalidates dependent residuals and authorizations. Provenance cycles are forbidden.

Confidence/reliability is metadata and never changes modality.

## State representations and Δ

Residual comparison must bind the comparator and representation schema:

`Δ(a, b; comparator_id, state_rep_schema)`

Comparator/tolerance/schema changes can change MATCH/MISMATCH and therefore belong in authorization dependency hashes. Semantically incompatible StateReps must not be silently compared.

## Template/runtime separation

The canonical NYCH concept of a T.O.T.E. database that can 'infer intent' is constrained by anti-promotion.

A retrieved template may provide:
- MODEL prior / candidate goal
- PLAN prior
- action schema

It may not instantiate `👀 OBS` or `🗯️ INTENT` without independently licensed sources. A plausible inferred goal is represented as a model/candidate intent, not an operative intention.

Thus Gestalt/T.O.T.E. retrieval narrows the hypothesis/planning space without manufacturing evidence or authority.

## Namespace isolation and cross-TOTE transforms

Evidence is scoped by trace/TOTE instance/epoch. Evidence from one TOTE cannot satisfy another merely because context is nearby or semantically similar.

Cross-instance transfer requires an explicit typed, provenance-preserving dependency edge. Imported information preserves modality only when the edge explicitly licenses the shared evidence scope; otherwise it remains model information in the target instance.

## Fast Track vs Slow/Canonical Track

Fast Track is reinterpreted as **skipping redundant computation, never skipping normative semantic distinctions**.

It may cache/reuse validated templates and computations but may not omit or fabricate modality licensing, provenance, residual semantics, temporal boundaries, or authorization checks.

Certification target is decision-preserving prefix equivalence. For every trace prefix, Fast and Canonical execution must expose equivalent normative projections and identical legal/illegal ACT and EXIT decisions. Final-state equality alone is insufficient because an implementation could have performed an illegal intermediate action.

Compression/decompression must preserve every safety-relevant distinction required to reproduce residual classifications and authorization decisions.

## Key adversarial/property tests agreed during mesh run

- all 3×3 residual combinations
- missing OBS/MODEL/INTENT → dependent `⊥`
- MODEL→OBS promotion rejected
- ACT→INTENT inference rejected
- ACT never synthesizes OBS
- END never becomes EXIT
- B/D cannot ACT without valid plan+permit
- C never actuates
- consumed permit replay rejected
- semantic/provenance mutation invalidates permit
- pre-action OBS cannot verify post-action epoch
- delayed/out-of-order sensor evidence cannot be assigned by ingestion time alone
- duplicate ingestion is idempotent
- causally independent event permutations produce equivalent derived state
- conflicting observations produce unresolved evidence rather than fabricated certainty
- inferred/template goal cannot populate INTENT
- cross-instance evidence rejected without an admissible dependency edge
- provenance DAG cycles rejected
- Fast/Canonical prefix-equivalence violations emit counterexamples

## Resulting architecture

The mesh run shifts NYCH's center of gravity from emoji/symbol compression alone toward a typed epistemic and T.O.T.E. control substrate:

`OBS / MODEL / INTENT`

`↓`

`E_model + E_goal`

`↓`

`A / B / C / D / PARTIAL`

`↓`

`UPDATE / PLAN / EXIT-CERTIFICATE`

`↓`

`ACTION-PERMIT`

`↓`

`ACT`

`↓`

`NEW VERIFICATION EPOCH`

Symbolic compression, consonant residue, density thresholds, and concrete AST syntax remain experimental implementation layers unless separately promoted to normative status.

## Next-run objective

The next PhiPhi run should **populate the repository's T.O.T.E. database**, not extend this architecture document. ChatGPT/nx-001 is the integration authority because it has repository write capability. Gemini agents should generate candidate entries in a machine-validated interchange format and return them to nx-001; nx-001 validates modality licensing, schema compliance, deduplication, provenance, and database constraints before committing accepted entries.

A separate `.ork` orchestration specification should define that contribution protocol so peer agents submit candidates rather than claiming repository writes.
