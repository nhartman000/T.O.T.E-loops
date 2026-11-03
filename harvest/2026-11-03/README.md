# NYCH TOTE-loop harvest snapshot — 2026-11-03 (mid-day)

**This is a MID-DAY SNAPSHOT taken while the harvest was still running (~11:56 EST).** Every harvested loop is
**PROVISIONAL and UNVERIFIED** (`status: candidate`, `epistemic_status: PROVISIONAL`, `review_status: provisional_unreviewed`).
Do not treat any row as canonical. 2 rows are hand-written canonical seeds from the original store.

Total loops exported: **92,719** (after ingest batches 1 and 2).

## Accuracy caveat
An earlier 40-item spot check of harvested loops found **21 correct, 6 partial, 13 wrong** (≈52% fully correct).
Expect a substantial error rate; human review is required before promotion.

## Files
| File | Contents |
| --- | --- |
| `tote_loops_2026-11-03.jsonl.gz` | gzip JSONL, one TOTELoop node per line (all columns from the Kuzu store; `provenance`, `techniques`, `termination_triggers` decoded to JSON) |
| `sample_50.jsonl` | 50 randomly sampled rows (seed 20261103) for quick inspection |

## Counts per source (provenance.method)
| Method | Loops |
| --- | --- |
| UI-HARVEST-1 | 56,564 |
| HOWTO-HARVEST-1 | 32,529 |
| HARVEST-BATCH-1 | 3,542 |
| UI-CANON-1 | 81 |
| manual_seed | 3 |

- `UI-HARVEST-1` / `UI-CANON-1`: tech help-center harvest (nych-ui-actions)
- `HOWTO-HARVEST-1`: everyday how-to pages (FTC, CFPB, usa.gov, CISA, platform help pages)
- `HARVEST-BATCH-1`: nych3 batch harvester from public-domain books (ISBN / Gutenberg refs)

## Counts per source host (provenance.first_ref.url)
| Host | Loops |
| --- | --- |
| support.microsoft.com | 20,568 |
| support.google.com | 19,074 |
| www.samsung.com | 9,952 |
| support.claude.com | 6,309 |
| blog.hootsuite.com | 3,902 |
| www.apartmentlist.com | 3,802 |
| (no URL: book/Gutenberg or manual seed) | 3,626 |
| zapier.com | 3,287 |
| www.tomsguide.com | 2,865 |
| bitwarden.com | 2,841 |
| later.com | 2,596 |
| www.bbb.org | 2,093 |
| support.1password.com | 2,023 |
| www.consumer.ftc.gov | 1,728 |
| www.aarp.org | 1,497 |
| swappa.com | 1,383 |
| help.snapchat.com | 1,359 |
| www.staysafeonline.org | 943 |
| www.grammarly.com | 686 |
| support.apple.com | 661 |
| help.shop.app | 418 |
| www.consumerfinance.gov | 368 |
| www.mercari.com | 165 |
| www.usa.gov | 160 |
| www.digitaltrends.com | 125 |
| support.discord.com | 112 |
| www.cisa.gov | 106 |
| www.zelle.com | 38 |
| help.offerup.com | 17 |
| support.signal.org | 8 |
| buffer.com | 6 |
| www.hud.gov | 1 |

## Counts per domain
| Domain | Loops |
| --- | --- |
| tech.ui | 56,645 |
| howto.digital_life | 9,596 |
| howto.social_creator | 8,555 |
| howto.ai_tools | 5,250 |
| howto.rental | 4,025 |
| cooking | 2,956 |
| howto.tech_phone | 2,112 |
| howto.marketplace | 1,706 |
| howto.shopping_returns | 1,285 |
| craft.woodworking | 266 |
| craft.knitting | 251 |
| craft.ropework | 70 |
| human_action.perception | 1 |
| human_action.locomotion | 1 |

## Provenance and quote policy
- Every harvested row carries `provenance` with `source`, `method`, and `first_ref` = source **URL** and **retrieval date**
  (or ISBN/page/Gutenberg id for book-derived rows). The **step** is recorded in `name` / `objective`.
- Quotes from source pages are limited to **at most 25 words** per step. Quote text is kept in the compact candidate
  export of the harvester, not in these store rows; no row here contains a quote longer than 25 words.
- **No raw scraped pages** are included in this repository. Source pages remain with their publishers; follow the URL.
- Not included: unpublished internal research layers or planning material, and no credentials or secrets.
