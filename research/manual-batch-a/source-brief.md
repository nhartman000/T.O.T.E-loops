# Manual batch A — research source brief

## Scope and epistemic boundary

This batch contains six **DERIVED** specifications: two each for geospatial/cartography, manufacturing quality, and collections preservation. None is an executed professional procedure, observed successful loop, professional certification, MG8 runtime demonstration, database population, or canonical QSON evidence. All iteration budgets are author policy, not manual requirements. No seed, builder, schema, database, application source, or other research batch was changed. No commit or push was performed.

The assigned directory is the entire write scope. Repository discovery/build/database tests from the MG8 population reference are intentionally not run: this is isolated candidate research, not authorized population. The grounded-citations skill and MG8 `references/tote-domain-population.md` were loaded; their distinction between derived descriptions, execution evidence and lexical routes is preserved.

## Retrieval → scan → derivation

The publisher sections were fetched with HTTP requests, converted to UTF-8 text, saved and read in full before the candidate specifications were authored. The georeferencing lesson explicitly discusses residuals and aerial-image comparison; this motivated a residual-review loop rather than a generic map-editing task.[1] The topology section explains rule-dependent validation, polygon overlaps, error tables and digitizing fixes; this motivated a reviewed polygon-overlap loop.[2]

The NIST control-chart section explicitly distinguishes outside-limit findings from nonrandom patterns inside limits, and calls for investigating assignable causes; this motivated a signal-review loop.[3] The separate stable-but-unacceptable section calls for improvement only after stability, using experiments, calibration or historical-data re-analysis; this motivated a distinct improvement-review loop, with repeat monitoring supported by the control-chart section.[4][3]

The NPS environment chapter explicitly links monitoring, qualified team planning, non-mechanical controls and evaluation of effectiveness; its lighting section separately specifies baseline information and before/after measurement, motivating the two preservation loops.[5]

### Exact manual coverage and limitations

| IDs | Primary section actually scanned | Derivation boundary |
|---|---|---|
| A-GEO-001 | QGIS 3.40 Training Manual §14.2, especially §14.2.2 | The 10-pixel advice belongs to the Finland forestry exercise, not a universal accuracy standard. Absolute dX/dY comparison and sign-off are derived. |
| A-GEO-002 | QGIS 3.40 User Manual §25.2.5, Topology Checker Plugin | Zero-overlap exit requires an approved no-overlap coverage model. It is not cadastral/legal validity. |
| A-QUAL-001 | NIST/SEMATECH e-Handbook §6.3.1 | Fresh-data verification window, pattern rules, action approval and cause disposition are supplied policy, not specified numerically by the manual. |
| A-QUAL-002 | e-Handbook §6.1.5 plus §6.3.1 | Process target and variability acceptance limits must come from qualified review; stability is not product acceptability. |
| A-PRES-001 | NPS Museum Handbook I, Ch.4, §§G/H; printed pp.4:29–4:34 | Only a non-mechanical proposal/review is specified; collection-specific limits and observation duration require expert approval. |
| A-PRES-002 | Same chapter, §J; printed pp.4:46–4:51 | Site-matched before/after review and exposure criteria require a conservator. No electrical installation, UV operation or object-handling steps are given. |

NPS retained coverage is exactly PDF pages 32–37 and 49–54 (printed pp.4:29–4:34 and 4:46–4:51). The rest of the downloaded chapter was processed in memory only and not retained. No full handbook or full chapter is published. QGIS snapshots retain the two open documentation sections; NIST snapshots retain only two handbook subsections. Candidate evidence is limited to short exact passages, with separate support labels for initial test, action, retest and exit.

## Editions, provenance and rights

QGIS sources use versioned **3.40** documentation URLs, not `latest`. QGIS states the current documentation is under the GNU Free Documentation License 1.3 or later.[9] The snapshots are extracted text, not original HTML and not a replacement manual; attribution and source/licensing URLs are retained. This research bundle does not represent an independently relicensed edition.

The NPS chapter identifies itself as **2016**. NPS states its own material is generally public domain unless otherwise indicated; this does not extend to protected third-party material.[8] Only selected text pages are retained; no images or third-party figures are reproduced in the candidates.

NIST sections are live HTML without an edition/date displayed in the retained section. NIST's policy generally excludes its employee-created non-SRD works from US copyright protection but preserves qualifications for other works.[7] Because the handbook is co-produced with SEMATECH, this batch does **not** assume blanket public-domain status: limited attributed research quotations are the conservative rights basis, not a claim to redistribute the full work. Foreign rights and third-party ownership remain unresolved.

`source-manifest.json` records publisher URLs, final redirect URLs, UTC access timestamps, extraction format, snapshot SHA-256, and downloaded-response SHA-256. The raw response hash is a retrieval receipt, not a promise of reconstructibility: raw HTML/PDF bytes are not retained. Candidate `sha256` always hashes the actual local text snapshot. PDF quote line breaks are preserved; HTML extraction preserves internal paragraph line breaks while using spaces between elements. Website chrome is omitted when a main element is available.

## Artifacts and checks

- `candidates.json`: six records with required fields and explicit support-bearing excerpts.
- `snapshots/`: eight publisher-text snapshots (five manual sections/chapter selections and three rights pages).
- `source-manifest.json`: eight provenance/access/hash records.
- `citation-ledger.json`: task-local citation ledger with eight cited sources. The unused initial licensing-route probe was removed without renumbering the retained source IDs.
- `retrieve.py`: retrieval/extraction recipe; rerunning performs new retrievals and updates access/hash records.
- `derive.py`: curated derivation and exact-substring quote selection from the scanned snapshots.
- `verify.py` / `verification.json`: quote, hash, inventory, field and support-coverage checks; these check provenance structure, not semantic entailment or professional validity.
- `.venv/`: isolated retrieval dependencies; no system packages installed.

The initial system Python lacked `requests`; an in-scope virtual environment resolved that blocker. An initial QGIS licensing URL returned a thin/non-authoritative body; it was replaced with the publisher's actual licensing page before any rights conclusion. No professional procedure was executed.

## Sources

[1] https://docs.qgis.org/3.40/en/docs/training_manual/forestry/map_georeferencing.html — 14.2. Lesson: Georeferencing a Map — QGIS Documentation  documentation
[2] https://docs.qgis.org/3.40/en/docs/user_manual/plugins/core_plugins/plugins_topology_checker.html — 25.2.5. Topology Checker Plugin — QGIS Documentation  documentation
[3] https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc31.htm — 6.3.1. What are Control
Charts?
[4] https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc15.htm — 6.1.5. What to do if "In Control" but Unacceptable?
[5] https://www.nps.gov/subjects/museums/upload/MHI_Ch4_Environment.pdf — NPS Museum Handbook Part I, Chapter 4: Museum Collections Environment (2016)
[7] https://www.nist.gov/open/license — Copyright, Fair Use, and Licensing Statements for SRD, Data, Software, and Technical Series Publications | NIST
[8] https://www.nps.gov/aboutus/disclaimer.htm — Disclaimer (U.S. National Park Service)
[9] https://docs.qgis.org/3.40/en/docs/about/license/index.html — Complying with Licenses — QGIS Documentation  documentation
