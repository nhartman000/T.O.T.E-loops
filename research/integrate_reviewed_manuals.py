"""One bounded, independently reviewed conversion; private research inputs required.

Writes a NEW isolated output only. Does not fetch manuals, execute domain actions,
publish, or overwrite the repository data. Review decisions below are inclusion
reviews of DERIVED specifications, never professional/safety certification.
"""
from pathlib import Path
import argparse
import json
import re
import shutil
import tempfile

from src.manual_agent import ROOT, digest, encoded, scan_source
from src.manual_admission import integrate_batch, audit_output


INITIAL = {
    'A-GEO-001': 'Inspect the ground-control-point table dX[pixels] and dY[pixels] errors and review digitized points and entered coordinates when the exercise error exceeds 10 pixels.',
    'A-GEO-002': 'Apply the active Must not overlap rule to all features and inspect errors by type, layer and feature ID.',
    'A-QUAL-001': 'Inspect control-chart points for outside-limit observations and systematic nonrandom patterns; either finding warrants investigation.',
    'A-QUAL-002': 'Check whether the statistically stable process has an average level too high or too low, or unacceptable variability.',
    'A-PRES-001': 'Determine whether temperature and RH levels are stable and within the recommended set point and permissible range.',
    'A-PRES-002': 'Gather baseline and ongoing lighting information and assess required light levels, UV blocking, IR and visible-light control.',
    'MB-B-PG-001': 'Use pg_verifybackup to check a pg_basebackup backup against its server-generated backup_manifest.',
    'MB-B-PG-002': 'With the server shut down cleanly, use pg_checksums --check to check cluster checksums; verification exits zero only without checksum errors.',
    'MB-B-IM-001': 'Use magick identify to inspect actual image format and dimensions and report incomplete or corrupt image data; use +ping for accurate pixel characteristics.',
    'MB-B-IM-002': 'Use magick compare -verbose -metric rmse to measure differences between the reference image and its reconstruction, including the all-channel result.',
    'MB-B-WAI-001': 'Check that a page title adequately and briefly describes page content and differs from titles of other pages on the website.',
    'MB-B-WAI-002': 'Check heading presence, starting H1, skipped or blank levels, missing visual headings, descriptive text and nesting against page content.',
}
DECISIONS = {
    'A-GEO-001': '10 pixels belongs only to the Finland forestry exercise. Absolute component interpretation and overlay sign-off are authored, not general cartographic accuracy.',
    'A-GEO-002': 'Full-layer validation and rule meaning are supported. Boundary correction remains qualified review, not automatic deletion or cadastral certification.',
    'A-QUAL-001': 'Outside limits and nonrandom patterns both matter. Do not widen limits to hide a signal. Finite-window absence of signals is not proof of stability or product conformance.',
    'A-QUAL-002': 'The source supports stability before centering/reducing variation and proposes experiments/calibration/reanalysis. Targets, sampling and verification windows remain required professional inputs.',
    'A-PRES-001': 'Source supports team planning, non-mechanical measures, monitoring and adjustment. No collection-independent RH/temperature prescription; continuous monitoring must continue.',
    'A-PRES-002': 'Source explicitly supports before/after monitoring and reducing exposure. Preserve collection-specific criteria; exclude installations, electrical work and object handling.',
    'MB-B-PG-001': 'The source supports creation then verification, not automatic retry. Plain-format WAL-capable verification and version compatibility are required by this profile; verification does not replace test restores.',
    'MB-B-PG-002': 'High-risk in-place rewrite is explicitly documented. Include only as an offline configuration-to-verification specification, never corruption repair. Disabled state, clean shutdown, protected backup, replication coordination and approval must be established externally; existing failures stop/escalate.',
    'MB-B-IM-001': 'The command and identify checks are documented. WEBP, dimensions, quality 85 and new filenames are profile inputs/example choices, not universal quality guarantees. Untrusted inputs require an external sandbox/resource policy.',
    'MB-B-IM-002': 'Explicit RMSE avoids contradictory default-metric prose/table. The normalized all-channel example supports measurement; no universal threshold, monotonic quality guarantee or exit-code semantics is inferred.',
    'MB-B-WAI-001': 'Draft Easy Checks provide screening, not normative conformance. Semantic adequacy requires human judgment; distinctiveness holds only for the declared compared pages. No bookmark code is retained/executed.',
    'MB-B-WAI-002': 'Draft screening questions are supported. Starting-H1/no-skipped-subheading criteria are this profile, not universal WCAG violations. Reload/repetition/editing and human semantic acceptance are authored.',
}


def normalize_with_offsets(text):
    parts = list(re.finditer(r'\S+', text))
    flat = ' '.join(p.group() for p in parts)
    positions = []
    for i, part in enumerate(parts):
        if i:
            positions.append(part.start()-1)
        positions.extend(range(part.start(), part.end()))
    return flat, positions


def assemble(output):
    output = Path(output)
    if output.exists():
        raise ValueError('Use a fresh output directory')
    original_seed = json.loads((ROOT/'data/seed_loops.json').read_text())
    # Always derive from the original records; replay against populated main is
    # tested independently by integrate_batch, with carried provenance.
    seed = dict(original_seed, loops=[l for l in original_seed['loops'] if l['loop_id'].startswith(('ai.', 'code.'))])
    seed.pop('manual_admission', None)  # Reconstruct the original, unadmitted baseline.
    records = []
    manifests = {}
    for b in 'ab':
        base = ROOT/f'research/manual-batch-{b}'
        manifest = json.loads((base/'source-manifest.json').read_text())
        manifests[b] = {m['url']: m for m in manifest} if b == 'a' else {m['url']: m for m in manifest.values()}
        records.extend((b, c) for c in json.loads((base/'candidates.json').read_text()))
    if set(INITIAL) != {c['loop_id'] for _, c in records}:
        raise ValueError('Unexpected research record inventory; re-review required')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='manual-excerpts-', dir=output.parent) as temporary:
        snapshots = Path(temporary)/'sources'
        gathered = {}
        for b, c in records:
            for source in c['sources']:
                key = (b, source['local_snapshot'])
                entry = gathered.setdefault(key, dict(source=source, professions=set(), domains=set(), sections=set(), quotes=[]))
                entry['professions'].add(c['profession'])
                entry['domains'].add(c['domain'])
                entry['sections'].add(source['section'])
                for quote in source['quotes']:
                    if quote['text'] not in entry['quotes']:
                        entry['quotes'].append(quote['text'])
        prepared = {}
        for (b, local), entry in gathered.items():
            source = entry['source']
            path = ROOT/f'research/manual-batch-{b}'/local
            raw_text = path.read_bytes()
            if digest(raw_text) != source['sha256']:
                raise ValueError('Private source hash differs: '+local)
            text = raw_text.decode('utf-8')
            flat, offsets = normalize_with_offsets(text)
            manifest = manifests[b][source['url']]
            source_id = 'manual-'+Path(local).stem.replace('_', '-')+'-excerpt-v1'
            excerpt_quotes = []
            derivation = []
            for original_quote in entry['quotes']:
                # Batch A encodes some line breaks as literal backslash-n.
                quote = ' '.join(original_quote.replace('\\n', '\n').split())
                start = flat.find(quote)
                if start < 0:
                    raise ValueError('Quote not in independently read private text: '+quote)
                a, z = offsets[start], offsets[start+len(quote)-1]+1
                excerpt_quotes.append(quote)
                derivation.append(dict(quote=quote, private_text_start=a, private_text_end=z,
                                       private_text_sha256=digest(raw_text), private_locator=local,
                                       private_line_start=text.count('\n', 0, a)+1))
            response_hash = manifest.get('retrieved_response_sha256', manifest.get('raw_sha256'))
            representation = dict(
                source_id=source_id, url=source['url'], publisher=source['publisher'],
                title=source['title'], edition=source.get('edition', source.get('version')),
                section=sorted(entry['sections']), domain=sorted(entry['domains']),
                profession=sorted(entry['professions']), license=source['license'], access='public', format='text',
                review_needs=['No execution authority; domain professional approval required before use'],
                representation='reviewed_evidence_excerpt',
                original_retrieval=dict(response_sha256=response_hash, text_sha256=digest(raw_text),
                    retrieved_at=manifest.get('accessed_at', manifest.get('retrieved_at')),
                    response_retained_privately=b == 'b',
                    note='Research retrieval hash, not independently authenticated publisher identity. Original response not bundled; A retained extracted text only. NPS PDF extraction/page labels were reviewed separately.'),
                excerpt_derivation=dict(method='Minimal selected text, whitespace collapsed; no ellipses inside quotations. Authored header and blank-line separators added. No full manual was scanned by this admission run.',
                    excerpts=derivation),
                rights_notice='See data/THIRD_PARTY_NOTICES.txt and data/licenses/. This excerpt selection is changed/abridged from the linked original; no endorsement.')
            header = ('REVIEWED EVIDENCE EXCERPT — NOT A COMPLETE MANUAL OR A NETWORK SCAN\n'
                      + source['title']+'\n'+source['url']+'\n'
                      + 'Publisher: '+source['publisher']+'\n'
                      + 'Sections: '+'; '.join(sorted(entry['sections']))+'\n'
                      + 'Rights: '+source['license']+'\n'
                      + 'Change notice: selected excerpts; whitespace normalized. See THIRD_PARTY_NOTICES.txt and licenses/.\n')
            excerpt = header+'\n'+'\n\n'.join(excerpt_quotes)+'\n'
            snap = scan_source(representation, snapshots, raw=excerpt.encode(), chunk_chars=16000)
            prepared[(b, local)] = (source_id, snap)
        candidates = []
        reviews = []
        fields = ('loop_id','name','domain','objective','exit_predicate','max_iterations','epistemic_status')
        for b, original in records:
            loop = {k: original[k] for k in fields}
            loop.update(initial_test=INITIAL[loop['loop_id']], gestalts=['provenance','exit_predicate'])
            evidence = []
            initial_evidence = []
            for source in original['sources']:
                sid, snap = prepared[(b, source['local_snapshot'])]
                for q in source['quotes']:
                    quote = ' '.join(q['text'].replace('\\n', '\n').split())
                    start = snap['text'].index(quote, snap['text'].index('Change notice:'))
                    end = start + len(quote)
                    chunk = next(ch for ch in snap['chunks'] if ch['start'] <= start < end <= ch['end'])
                    if 'initial_test' in q['supports']:
                        initial_evidence.append(len(evidence))
                    evidence.append(dict(source_id=sid, snapshot_sha256=snap['snapshot_sha256'],
                        chunk_id=chunk['chunk_id'], start=start, end=end, quote=quote))
            def authored(text):
                return dict(text=text, basis='authored_policy', evidence=list(range(len(evidence))))
            policy = ('At most '+str(loop['max_iterations'])+' operation/fresh-retest cycles; initial passing test may exit. '
                      + 'Entry prerequisites and detailed test profile (authored): '+original['initial_test']+' '
                      + ' '.join(original['procedure']['stop_conditions'])+' '
                      + ' '.join(original['notes'])+' '+DECISIONS[loop['loop_id']])
            review = dict(reviewer='Integration reviewer (separate from batch A/B research agents)', status='approved',
                notes='Approved for database inclusion as a DERIVED SPECIFICATION only. '+DECISIONS[loop['loop_id']],
                safety='Not professional approval, safety certification, operating authorization, or observed success. '+(original['review_required'] if isinstance(original['review_required'], str) else 'Qualified domain owner must approve all actual actions. '+DECISIONS[loop['loop_id']]),
                license='Only minimal attributed evidence excerpts retained; no raw manuals/PDFs/images published. '+'; '.join(s['license'] for s in original['sources'])+' See data/THIRD_PARTY_NOTICES.txt and data/licenses/.')
            candidate = dict(loop=loop, procedure=dict(
                initial_test=dict(text=loop['initial_test'], basis='source_fact', evidence=list(range(len(evidence)))),
                operation=authored(original['procedure']['operate_step']),
                fresh_retest=authored(original['procedure']['retest']),
                exit=authored(loop['exit_predicate']), iteration_policy=authored(policy)),
                evidence=evidence, review=review)
            candidates.append(candidate)
            reviews.append(dict(loop_id=loop['loop_id'], domain=loop['domain'], profession=original['profession'],
                decision='approved_derived_specification_only', reasoning=DECISIONS[loop['loop_id']],
                researcher_lexical_routes_not_admitted=original['gestalts']['lexical'],
                original_candidate_sha256=digest(encoded(original))))
        batch = dict(format_version='1.0', batch_id='manuals-2026-11-01-v1', candidates=candidates)
        result = integrate_batch(batch, seed, snapshots, output)
        (output/'manual-batch-v1.json').write_bytes(encoded(batch))
        (output/'manual-review.json').write_bytes(encoded(dict(reviews=reviews, excluded=[],
            scope='Independent source-context review for specification inclusion only, not domain certification. All operations/retests/exits/bounds are authored; initial tests are source-grounded paraphrases. No added gestalts; provenance and exit_predicate are existing domain-neutral protected terms.',
            original_seed_semantic_sha256=digest(json.dumps(seed, sort_keys=True).encode()))))
        print(json.dumps(audit_output(output), sort_keys=True))
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    assemble(parser.parse_args().output)
