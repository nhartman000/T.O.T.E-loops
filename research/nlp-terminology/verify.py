#!/usr/bin/env python3
"""Verify minimal evidence against PRIVATE webpage snapshots, not book pages."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def verify():
    taxonomy = json.loads((ROOT / 'taxonomy.json').read_text())
    excerpts = json.loads((ROOT / 'excerpts.json').read_text())['excerpts']
    by_id = {e['id']: e for e in excerpts}
    errors = []
    if len(by_id) != len(excerpts):
        errors.append('Duplicate evidence IDs')
    source_ids = {s['id'] for s in taxonomy['sources']}
    for source in taxonomy['sources']:
        path = ROOT / source['snapshot']
        if not path.is_file():
            errors.append(f'Missing private snapshot: {path.name}')
        elif hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            errors.append(f'Source hash mismatch: {source["id"]}')
    for e in excerpts:
        path = ROOT / e['local_snapshot']
        if not path.is_file():
            errors.append(f'Missing snapshot for {e["id"]}')
            continue
        text = path.read_text()
        if e['source_id'] not in source_ids:
            errors.append(f'Unknown source for {e["id"]}')
        if hashlib.sha256(text.encode()).hexdigest() != e['snapshot_sha256']:
            errors.append(f'Excerpt snapshot hash mismatch: {e["id"]}')
        start = e['start_character']
        if text[start:start + len(e['quote'])] != e['quote']:
            errors.append(f'Literal excerpt/offset mismatch: {e["id"]}')
    term_ids = {t['id'] for t in taxonomy['terms']}
    if len(term_ids) != len(taxonomy['terms']):
        errors.append('Duplicate term IDs')
    for t in taxonomy['terms']:
        if any(eid not in by_id for eid in t['evidence_ids']):
            errors.append(f'Unknown term evidence: {t["id"]}')
        elif not any(t['exact_term'] in by_id[eid]['quote'] for eid in t['evidence_ids']):
            errors.append(f'Exact term missing from evidence: {t["id"]}')
        if t['book_page_directly_read']:
            errors.append(f'Unsupported direct book-page claim: {t["id"]}')
    for r in taxonomy['relations']:
        if r['from'] not in term_ids or r['to'] not in term_ids:
            errors.append(f'Unknown relation endpoint: {r["id"]}')
        if any(eid not in by_id for eid in r['evidence_ids']):
            errors.append(f'Unknown relation evidence: {r["id"]}')
    result = {
        'status': 'PASS' if not errors else 'FAIL',
        'terms': len(taxonomy['terms']),
        'relations': len(taxonomy['relations']),
        'literal_excerpts': len(excerpts),
        'quoted_whitespace_words': sum(len(e['quote'].split()) for e in excerpts),
        'errors': errors,
        'verified': 'Snapshot hashes, literal webpage excerpt offsets, exact-term occurrence, reference integrity',
        'not_verified': 'Original book pages, semantic entailment, edition equivalence, historical first use, clinical efficacy',
    }
    (ROOT / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(verify())
