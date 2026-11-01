# Reviewed manual population, batch v1

## Outcome and authority boundary

12 independently reviewed **DERIVED SPECIFICATIONS** were admitted from research
batches A and B; none excluded. They are not professional approval, safety
certification, publisher-authored TOTE loops, or observed successful executions.
All original 10 records/operators/gestalts remain unchanged. Main data contains
22 loops, 132 steps, 4 operators and 8 existing gestalts; no SQL migration or new
lexical route was added. Researcher loop IDs are preserved exactly. The existing
protected `provenance` and `exit_predicate` gestalts are appropriate across these
domains; unreviewed domain-specific lexical proposals remain in the review
ledger rather than being silently promoted to canonical glyphs.

| IDs | Domain | Inclusion review and residual requirements |
|---|---|---|
| A-GEO-001 | GEOSPATIAL_CARTOGRAPHY | Training-exercise 10-pixel residual advice only; no universal mapping accuracy. Coordinate/reference/overlay acceptance still needs a cartographer. |
| A-GEO-002 | GEOSPATIAL_CARTOGRAPHY | Full-layer overlap detection supported; qualified boundary corrections, never automatic deletion or legal boundary certification. |
| A-QUAL-001 | MANUFACTURING_QUALITY | Outside-limit and nonrandom-pattern signals both matter; fixed limits and engineer-defined fresh-sample windows, not product certification. |
| A-QUAL-002 | MANUFACTURING_QUALITY | Stability before centering/reducing variation; targets, sampling and intervention remain qualified inputs. |
| A-PRES-001 | COLLECTIONS_PRESERVATION | Team-reviewed non-mechanical proposals and fresh logger review; no universal RH target, HVAC instructions or cessation of monitoring. |
| A-PRES-002 | COLLECTIONS_PRESERVATION | Before/after lighting effectiveness supported; collection-specific acceptance, no electrical work or object handling. |
| MB-B-PG-001 | database_administration | Plain-format, version-compatible backup verification; reacquisition is authored strategy, test restores still separate. |
| MB-B-PG-002 | database_administration | High-risk offline enable/check specification, not corruption repair. Independently establish disabled state, clean shutdown, backup, replication coordination and DBA authorization; existing failures stop/escalate. |
| MB-B-IM-001 | digital_imaging | Actual format/full-read checks supported. WEBP/dimensions/quality are declared inputs/example choices, not perceptual quality or malicious-image safety guarantees. |
| MB-B-IM-002 | digital_imaging | Explicit RMSE avoids conflicting default-metric wording. Threshold/schedule/human acceptance are authored; no monotonic improvement guarantee. |
| MB-B-WAI-001 | accessibility_web_qa | Draft title screening and scoped cross-page comparison only; not normative WCAG certification; semantic acceptance remains human. |
| MB-B-WAI-002 | accessibility_web_qa | Draft heading screening; starting H1/no skipped subheadings are profile criteria, not universal WCAG violations. |

Initial tests are source-grounded paraphrases. The original detailed initial
profiles are retained as authored prerequisites in `iteration_policy`.
Operations, fresh retests, exit criteria and iteration policies are explicitly
`authored_policy`, with evidence links identifying their motivation rather than
claiming the source prescribes the whole procedure. Bounds are author policy,
not implemented domain-action enforcement. A missing professional/site input is
unresolved; inclusion approval never supplies that input. Per-record decisions,
professions and unadmitted lexical proposals are in `data/manual-review.json`.

## Published evidence, not complete source snapshots

`data/sources/` contains 11 self-contained **reviewed evidence excerpt** documents:

- `manual-qgis-georef-excerpt-v1/`
- `manual-qgis-topology-excerpt-v1/`
- `manual-nist-control-excerpt-v1/`
- `manual-nist-unacceptable-excerpt-v1/`
- `manual-nps-environment-excerpt-v1/`
- `manual-pg-verifybackup-excerpt-v1/`
- `manual-pg-checksums-excerpt-v1/`
- `manual-im-identify-excerpt-v1/`
- `manual-im-compare-excerpt-v1/`
- `manual-w3c-title-excerpt-v1/`
- `manual-w3c-headings-excerpt-v1/`

Each directory holds `original.bin` (the **excerpt document**, not the original
network response), normalized `snapshot.txt`, and `snapshot.json`. A prominent
header says this is not a complete manual or network scan. Metadata separately
retains original URL, edition/section/page, publisher, domains/professions,
research retrieval response/text hashes, retrieval time and the private text
slice/line locators. `raw_sha256` and `snapshot_sha256` describe only the retained
excerpt representation. Whitespace is collapsed transparently; no ellipses or
new publisher assertions are inserted inside quotations. The generic scanner
was used offline to validate these retained excerpt bytes, not to claim that it
fetched, authenticated or scanned the original manuals.

The original batch-A response bytes were not retained by its researcher;
extracted text was retained privately. NPS PDF page extraction was separately
reviewed, not passed off as scanner-native PDF handling. Batch-B private HTML
and text hashes were checked. Hashes establish byte integrity, not independent
publisher authentication. Original-source comparison requires the private
research snapshots; public audits validate the retained excerpts and derived
data only.

Only necessary attributed quotations are published, with rights qualifications
and full license notices in `data/THIRD_PARTY_NOTICES.txt` and `data/licenses/`.
NIST/SEMATECH is not blanket-labelled public domain; NPS third-party images are
excluded; W3C pages remain labelled DRAFT. QGIS short research quotations retain
GFDL attribution/license and no unverified invariant-section declaration. No
full manuals, raw PDFs, bookmark scripts, research virtualenvs or private
snapshots are part of this publication set. Repository MIT does not relicense
third-party material. Further/full redistribution requires fresh rights review.

## Canonical build and verification

```sh
python -m src.build_db
python -m src.manual_agent validate --batch data/manual-batch-v1.json --snapshots data/sources
python -m src.manual_agent audit --output data
python -m unittest discover -s tests -v
```

`src.build_db` consumes sibling `provenance.json`, validating exact candidate,
fingerprint, source and retained-batch inventories before replacing a DB and
preserving exact operation and fresh-retest text. Enriched seeds include a
top-level `manual_admission` map binding admitted IDs to complete candidate hashes;
missing sibling provenance is rejected. Only original unmarked seeds without
admitted procedures use the legacy generic steps. Main provenance now retains
the exact batch envelope from `data/manual-batch-v1.json`, verified against its
existing batch hash. Migration preserved all prior candidate/source declarations
and all 33 retained source files without edits; only the added inventory changes
the export's seed hash, not its loop/operator/step content.
The canonical export serialization matches admission/audit serialization. The
main `data/seed_loops.json`, `data/tote_loops.json` and locally generated
`data/tote_loops.sqlite3` are populated, not merely a separate candidate bundle.
The SQLite artifact remains ignored by the repository's existing policy;
rebuild it from the committed seed, provenance and excerpts, or download the
verified SQLite/JSON/source bundle from the GitHub Actions artifact.

Tests cover dotted loop identity versus stricter filesystem source IDs,
traversal rejection, real canonical rebuild and audit, unchanged original seed
semantic hash, all admitted decisions, SQL integrity/foreign keys, exact
procedures, idempotent replay, missing-provenance rejection, immutable historical
source declarations, orphan/duplicate candidates, exact inventory membership,
fake batch hashes and rehashed candidate mutation. The source schema permits safe dotted identity
segments without changing or normalizing researcher IDs. `schema.sql` is unchanged.

`research/integrate_reviewed_manuals.py` performs the explicit conversion using
private inputs and a NEW `--output` directory. It neither overwrites main data
nor fetches/publishes/executes manual actions. Promotion into main data was
explicitly authorized; previous artifacts were backed up locally under
`work/pre-manual-population/` (ignored). The published retained evidence is
sufficient for offline rebuild/audit without private inputs.

Primary Bandler/Grinder body text remains inaccessible. The separate NLP
terminology sidecar is partial, mostly secondary/mediated and **not canonical**;
no historical terminology claims were imported into these operational records.
No ORK/BONIT mesh execution, domain-command execution, commit or push is claimed.
