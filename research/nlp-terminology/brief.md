# NLP exact terminology and TOTE loop functions — bounded research brief

## Result and attribution boundaries

**Partial research result, not a completed early-book extraction.** No original body page of *The Structure of Magic*, *Patterns*, or *Frogs into Princes* was successfully read in this run. The JSON deliberately separates actual text access from catalog metadata and mediated quotations.

The usable exact wording comes principally from Robert Dilts’s public author-site pages: a copyright-guidelines page reproducing a short *Tools for Dreamers* passage and a quotation attributed to Grinder/Bandler, plus the articles “Motivation” and “Modeling.”[1][16][17]

- **Origin:** Dilts explicitly attributes the T.O.T.E. model to Miller, Galanter and Pribram (1960), rather than to Bandler/Grinder; the actual 1960 book was not read, so this is a mediated origin attribution, not an original-page citation.[16]
- **Early Grinder/Bandler terminology:** the author-site reproduction identifies *The Structure of Magic Vol. II*, Grinder and Bandler, Science and Behavior Books, Palo Alto, 1976, p. 45; its term is **congruency**, describing aligned output channels carrying compatible messages.[1] This is a **secondary reproduced quotation**, not independently verified against the book page; it does not establish congruency as a TOTE test or exit rule.[1]
- **Later formulations:** TEST, OPERATE, EXIT, mental strategy, fixed goal/variable means and feedback-loop wording belong here to the passage attributed to *Tools for Dreamers*, Dilts, Epstein & Dilts, pp. 23–24, as reproduced on Dilts’s site.[1] Do not reattribute that passage to an early Bandler/Grinder volume.
- **Later coauthored reference:** Dilts’s bibliography lists *Neuro-Linguistic Programming: The Study of the Structure of Subjective Experience, Volume I*, Meta Publications, Capitola, 1980, with Grinder, Bandler and DeLozier.[6] No title page or body text was obtained; the biography is not proof of an exhaustive author list, specific terms or page locations in that volume.

## Functional taxonomy (all descriptions below are paraphrases)

The local research JSON has 15 exact-term records and four relation records; it is an independent research artifact, not a proposed canonical schema change.

- **TEST → OPERATE:** operate if the goal is not achieved.[1]
- **OPERATE → TEST:** assessment again after operation is an **analyst interpretation**, supported by the ordered model name and continued-operation account, not an independently quoted transition sentence.[1][16]
- **Repeated test → OPERATE:** continue operation while the conditions are unmet; “retest” is an analyst label here, **not a verified exact source term**.[16]
- **TEST → EXIT:** satisfaction of test criteria permits the next step.[1]
- **Evidence procedures:** the “Modeling Capabilities” section identifies them with determining progress toward the goal.[17]
- **Nested T.O.T.E.s / sub-loops / sub-skills:** the section “Levels of Complexity of Skills and Capabilities” uses these names for smaller skill components of more complex capabilities.[17]

None of those later descriptions proves that early Bandler/Grinder books use identical labels, diagrams or transition rules. No clinical efficacy conclusion or executable therapeutic procedure is supplied.

## Bibliographic and access coverage

| Work / resource | What was actually read | Boundary |
|---|---|---|
| *The Structure of Magic I* | Google Books catalog, illustrated edition, Science and Behavior Books, 1975; ISBN 0831400447 / 9780831400446, 225 pages; limited contents and automated common-terms list | No original body page read; common-terms lists are not accepted as quotation/definition evidence.[8] |
| *The Structure of Magic II* | Google Books catalog, ISBN 0831400498 / 9780831400491, 198 pages; Dilts’s reproduced p.45 passage | Google catalog displays 1975, whereas Dilts cites 1976. Edition/date discrepancy unresolved; p.45 is a locator reported by Dilts, not a checked page image.[1][10] |
| *Patterns …*, Vol. I | Internet Archive item metadata: Bandler, associated Grinder, 1975, Cupertino: Meta, ISBN 091699001X | Explicitly access-restricted; no body text acquired, no borrow/login restriction bypassed.[9] |
| *Frogs into Princes* | Google Books catalog: Bandler/Grinder, edition 4, Real People Press, 1979, ISBN 0911226192 / 9780911226195, 194 pages | No actual body pages read; promotional description is not used as book-text evidence.[11] |
| *Tools for Dreamers* | Short passage reproduced on Dilts’s webpage, identified there as 1993 pp.23–24 | Biography lists 1991, Todd Epstein and Robert W. Dilts, Meta Publications, Capitola. Original edition not checked; year/edition discrepancy retained.[1][6] |
| *Neuro-Linguistic Programming … Volume I* | Dilts’s author bibliography, 1980 | No exact-term extraction or page claim from this unread volume.[6] |
| “Motivation”; “Modeling” | Full extracted public webpages, ©1998 Robert Dilts | Cite web headings/paragraphs, not invented book page numbers.[16][17] |

## Access failures and lawful limits

HTTP retrieval of the Crown House *Structure of Magic* product pages, the Pribram author-archive book landing page/PDF, and HathiTrust catalog returned 403; the NLP University Press encyclopedia page returned 465. Two alternate paths on the NLPU host returned 404. URLs and outcomes are recorded in `access-log.json`. These failures are not evidence that a work contains or lacks a term.

The extraction tool was unavailable because its configured backend supported search only, so public webpages were retrieved directly by HTTP. The real browser could not start because Chromium held the configured real-profile database lock. No browser/profile configuration was changed. No login, paywall or access restriction was bypassed. Search surfaced third-party full-book PDF mirrors, but these were not fetched or used because authorization could not be established.

## Evidence and verification

- `taxonomy.json`: exact terms, source lineage, distinct functional paraphrases, relation support levels and attribution limits.
- `excerpts.json`: minimal publishable excerpts, exact web locators, snapshot hashes and character offsets. Matching is against locally retrieved webpage text; **not** verification against original book images.
- `citations.json`: task-local citation ledger; original source URLs are retained.
- `verify.py` / `verification.json`: reproducible literal-substring, hash, term-to-excerpt and relation-reference checks.
- `private-snapshots/`: ignored full retrieved webpage text/HTML. No copyrighted full book was downloaded. Keep snapshots private; `.gitignore` excludes this directory.

The verifier can be rerun locally with `python verify.py`. A distribution omitting private snapshots cannot independently rerun full-text matching; the minimal sidecar documents the results without republishing those snapshots. Citation verification confirms reference identity and attached evidence, not scholarly truth or independent original-page access.

## Sources

[1] https://nlpu.com/Patterns/patt22.htm
[6] https://www.nlpu.com/robbio.htm
[8] https://books.google.com/books/about/The_Structure_of_Magic.html?id=WEtBAQAAIAAJ
[9] https://archive.org/details/patternsofhypnot0001band
[10] https://books.google.com/books?id=7vvaAAAAMAAJ
[11] https://books.google.com/books/about/Frogs_Into_Princes.html?id=LH52QgAACAAJ
[16] https://www.nlpu.com/Articles/artic17.htm
[17] https://www.nlpu.com/Articles/artic19.htm
