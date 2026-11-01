# Research evidence archive

The public evidence briefs, candidate records, source manifests, citation ledgers
and historical verification reports here preserve the derivation trail for the
reviewed population and the separately **partial** NLP terminology taxonomy.
They are not an alternative seed, a canonical taxonomy, or evidence that domain
operations were executed. Final admitted records and their minimal excerpt
evidence are in `data/`; see [the population review](../docs/manual-population-review.md).

## Reproducible public path

From the repository root, with Python 3.10+ and no private inputs:

```sh
python -m src.build_db
python -m src.manual_agent audit --output data
python -m unittest discover -s tests -v
```

For new research, use [the bounded manual-agent workflow](../docs/manual-agent.md),
not the historical scripts below. No schedule is enabled.

## Historical scripts: private-input reproduction only

**Every Python script under this `research/` directory is an archival research
helper, not a supported clean-checkout command or a CI prerequisite.** Batch A/B
`derive.py`/`assemble.py`/`verify.py` require omitted private source snapshots and
some require a researcher-local citation helper at an absolute path.
`retrieve.py` scripts are historical unbounded retrieval recipes: they can
replace local research files, follow redirects, and are **not** the hardened
public-source scanner. Do not use them as the population agent or run them
against live research evidence. The production scanner is `src.manual_agent`.

`integrate_reviewed_manuals.py` documents the original reviewed conversion and
requires private batch A/B inputs. It writes a new output directory, not main
data. `nlp-terminology/verify.py` requires private webpage snapshots and writes
its verification report; it cannot establish direct access to original book
pages. The committed `verification.json` reports record historical checks, not
checks newly run by a public checkout. Do not regenerate them from missing or
substitute evidence.

Private snapshots, full HTML/PDFs and environments are intentionally omitted.
Public excerpts retain their respective rights; the repository MIT license does
not relicense third-party text. Manual rights/notices are retained in
[`data/THIRD_PARTY_NOTICES.txt`](../data/THIRD_PARTY_NOTICES.txt); NLP excerpts
retain their source-specific attribution and limited research-quotation notice.
Unresolved original Bandler/Grinder text access and edition/page differences
remain explicit in [`nlp-terminology/brief.md`](nlp-terminology/brief.md).
