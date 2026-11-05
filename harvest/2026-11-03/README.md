# NYCH TOTE-loop harvest snapshot — 2026-11-03 (mid-day)

**This is a MID-DAY SNAPSHOT taken while the harvest was still running (~11:56 EST).** Every harvested loop is
**PROVISIONAL and UNVERIFIED** (`status: candidate`, `epistemic_status: PROVISIONAL`, `review_status: provisional_unreviewed`).
Do not treat any row as canonical. 2 rows are hand-written canonical seeds from the original store.

Total loops exported: **92,719** (after ingest batches 1 and 2).

## End-of-day update (2026-11-03, ~17:40 EST) — harvest stopped
The data files in this folder are still the **mid-day** export (92,719 loops). Final numbers after the harvest ended:
- **Store total: 105,130 TOTELoops** (105,128 candidate, 2 canonical seeds). New loops per ingest batch: Job B batch 1 +23,464 (store 63,535); Job B batch 2 → store 92,719 (incl. Job A batch 1); Job B final 0 new; Job A final tech.ui ingest → 105,130; final howto rebuild 0 new.
- **Job A (vendor help centers), cached pages:** microsoft 1,500 · google_youtube 1,353 · samsung 1,178 · google_accounts 381 · claude 367 · google_android 252 · google_mail 233 · ms_copilot 221 · google_chrome 205 · google_maps 170 · google_gemini 154 · google_drive 137 · google_calendar 117 · google_docs 78 · apple 39 (timeouts) · tiktok 35 · twitch 25. tech.ui export: 150,052 extracted actions (144,655 mapped to 81 classes, 5,397 unmapped), 68,975 instance loops.
- **Job B (how-to sites), pages:** apartmentlist 700 · tomsguide 1,000 · snapchat 500 · ftc 492 · cashapp 459 · zapier 433 · bbb 419 · cfpb 364 · later 349 · bitwarden 346 · onepassword 300 · swappa 300 · aarp 270 · hootsuite 237 · staysafeonline 200 · dropbox 131 · grammarly 107 · shopapp 77 · mercari 61 · learnfree 60 · usagov 57 · zelle 47 · cisa 46 · digitaltrends 21 · discord 6 · offerup 4 · hud 2 · buffer 1 · signal 1 — **6,990 pages**; 41,062 how-to actions after filtering (44,945 site-repeated chrome lines dropped).
- **Blocked or failed sources:** reddit (403, 0 pages), discord (403 ×517), signal (403 ×161), offerup (403 ×96), motorola and costco support (robots.txt), Google Play / Photos / Pixel Phone / Assistant help (timeouts, 0 articles), apple (read timeouts, 39 pages only).
- Everything is still **PROVISIONAL and not human-verified**. The current review entry point is `REVIEW/START_HERE_r3.md` on knowledge-graph branch `nych3-integration` (commit d27056f).

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
