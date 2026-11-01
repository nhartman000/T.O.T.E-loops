# Manual batch B — derived candidates only

Six authored TOTE specifications; three domains, two per domain. Not executed, certified, imported into a seed, or admitted by a runtime. No source commands were executed. Snapshot parsing, hashing and quotation checks are research verification only.

## Scanning and source selection

Read full extracted primary manual pages (not search snippets), including limitations and options. PostgreSQL manuals are pinned to major version 18.[1][2]
ImageMagick live pages display v7.1.2-35 but are not immutable release manuals; the Identify example itself reports 7.0.4-8.[4][5]
WAI title and heading pages are explicitly Draft, updated 19 March 2024.[7][8]
Source manifest records retrieval UTC, resolved URL, hashes of raw HTML and normalized text, and any Last-Modified header. Candidate quotes carry exact line locators into normalized snapshots.

## Derivation boundaries

The sources supply checks, operation primitives, examples and/or quality criteria, NOT these complete TOTE controllers. Fresh observations after change, iteration caps, failure/unknown routes, authorization, immutable candidate naming and escalation rules are author policy. Numeric bounds are not recommendations from manuals. PostgreSQL checksum enabling rewrites pages and demands a clean shutdown; that candidate requires explicit DBA approval and is not a corruption-repair strategy.[2]
Backup verification does not replace test restoration.[1]
Image quality thresholds and delivery targets are project policy; RMSE is explicitly chosen because the Compare page contradicts itself about the default metric.[5]
WAI Easy Checks are intentionally non-exhaustive; passing them is not accessibility certification.[9]

## Rights and publication boundary

Only short attributed verbatim excerpts appear in candidates. Raw HTML/full extracted text are local research snapshots, excluded by this directory's .gitignore; .gitignore is not access control and does not alter already-tracked files. Do not publish snapshots without rights review.

PostgreSQL grants copying/modification of software and documentation subject to notice conditions; retain its copyright, permission and disclaimer terms if republishing covered materials.[3]
Attribution: The PostgreSQL Global Development Group and The Regents of the University of California. ImageMagick manual links its open-source license, whose Source definition includes documentation source; redistribution requires the license, notices, attribution, and marking modifications.[6]
Attribution: Copyright © 1999 ImageMagick Studio LLC. Review documentation applicability before bulk republication; no bulk republication performed.

WAI pages link the permissive Software and Document License in their footer, not merely the generic Document License.[7][8][11]
The generic document-license page was also retrieved for comparison, not substituted for the actual linked license.[10]
Attribution: Copyright © 2026 World Wide Web Consortium. Includes short material copied from or derived from [Draft]
Page Title - Easy Checks and [Draft]
Headings - Easy Checks (original URLs in Sources); source editor Kevin White, EOWG. Draft status is preserved. These independently authored research candidates do not amend W3C documents or establish a new W3C technical specification.

## Verification

Run `python verify.py`. Verifies list size, two-per-domain grouping, required fields, lexical gestalts, DERIVED/review boundaries, hashes of all local sources, exact excerpt membership, quote support coverage for initial test/operate/fresh retest/exit, unique IDs and locator consistency. Citation-ledger evidence validation is separate from semantic entailment; no executable-loop validation is claimed.

## Files

- candidates.json: six rich candidate records (not canonical database schema).
- source-manifest.json: all retrieval/version-independent fingerprints.
- citation-ledger.json: citation IDs and checked verbatim evidence.
- snapshots/: ignored, full research HTML and normalized text.
- retrieve.py / assemble.py / verify.py: retrieval, assembly, and offline verification helpers.
- verification.json: actual verification result, generated after checks.

See THIRD_PARTY_NOTICES.txt for retained license terms. Original source prose is unmodified in quotes; surrounding procedures are independently authored derivations, not publisher instructions.

## Sources

[1] https://www.postgresql.org/docs/18/app-pgverifybackup.html — pg_verifybackup
[2] https://www.postgresql.org/docs/18/app-pgchecksums.html — pg_checksums
[3] https://www.postgresql.org/about/licence — pg_license
[4] https://imagemagick.org/identify — im_identify
[5] https://imagemagick.org/compare — im_compare
[6] https://imagemagick.org/license — im_license
[7] https://www.w3.org/WAI/test-evaluate/easy-checks/title — w3c_title
[8] https://www.w3.org/WAI/test-evaluate/easy-checks/headings — w3c_headings
[9] https://www.w3.org/WAI/test-evaluate/easy-checks — w3c_easy
[10] https://www.w3.org/copyright/document-license — w3c_license
[11] https://www.w3.org/copyright/software-license — w3c_software_license
