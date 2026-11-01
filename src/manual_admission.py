"""Mechanical candidate admission; not semantic extraction or effect execution."""
import copy
from contextlib import closing
import shutil
import json
from pathlib import Path
import re
import sqlite3
import tempfile

from .manual_agent import ROOT, digest, encoded, identifier, read_snapshot
from .build_db import steps_for, export_database


def schema_check(value, schema, root=None, path='$'):
    """The small JSON Schema subset used by the shipped contract, fail closed."""
    root = schema if root is None else root
    if '$ref' in schema:
        ref = root
        for part in schema['$ref'].removeprefix('#/').split('/'):
            ref = ref[part]
        return schema_check(value, ref, root, path)
    supported = {'$schema', '$defs', 'title', 'type', 'additionalProperties', 'required', 'properties', 'const', 'enum', 'pattern', 'items', 'minItems', 'maxItems', 'uniqueItems', 'minLength', 'minimum', 'maximum'}
    if set(schema) - supported:
        raise ValueError('Unsupported schema keyword')
    types = {'object': dict, 'array': list, 'string': str, 'integer': int}
    if 'type' in schema and (not isinstance(value, types[schema['type']]) or (schema['type']=='integer' and isinstance(value, bool))):
        raise ValueError(f'{path}: wrong type')
    if 'const' in schema and value != schema['const']:
        raise ValueError(f'{path}: invalid constant')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(f'{path}: invalid enum')
    if isinstance(value, dict):
        if set(schema.get('required', [])) - value.keys():
            raise ValueError(f'{path}: missing fields')
        props = schema.get('properties', {})
        if schema.get('additionalProperties') is False and value.keys() - props.keys():
            raise ValueError(f'{path}: unexpected fields')
        for k, v in value.items():
            if k in props:
                schema_check(v, props[k], root, path+'.'+k)
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0) or len(value) > schema.get('maxItems', float('inf')):
            raise ValueError(f'{path}: array bounds')
        if schema.get('uniqueItems') and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            raise ValueError(f'{path}: duplicate items')
        for v in value:
            schema_check(v, schema.get('items', {}), root, path+'[]')
    if isinstance(value, str):
        if len(value.strip()) < schema.get('minLength', 0) or ('pattern' in schema and not re.search(schema['pattern'], value)):
            raise ValueError(f'{path}: invalid string')
    if type(value) is int and not schema.get('minimum', -float('inf')) <= value <= schema.get('maximum', float('inf')):
        raise ValueError(f'{path}: number bounds')


def fingerprint(loop):
    # Conservative lexical semantic key, not a paraphrase/embedding detector.
    fields = [loop[k] for k in ('domain', 'objective', 'initial_test', 'exit_predicate')]
    return digest(encoded([' '.join(re.findall(r'\w+', s.casefold())) for s in fields]))


def validate_batch(batch, seed, snapshots, *, require_approved=False):
    schema_check(batch, json.loads((ROOT/'docs/manual-agent-candidate-format.json').read_text()))
    operators = {o['operator_id'] for o in seed['operators']}
    if not {'external_observe', 'internal_model', 'operative_intent', 'execute'} <= operators:
        raise ValueError('Canonical operators missing')
    gestalts = {g['gestalt_id'] for g in seed['gestalts']}
    existing = {l['loop_id']: l for l in seed['loops']}
    names = {l['name']: l['loop_id'] for l in seed['loops']}
    fingerprints = {fingerprint(l): l['loop_id'] for l in seed['loops']}
    seen = set()
    for c in batch['candidates']:
        loop = c['loop']
        # Loop identity is not used as a path; the contract permits dotted IDs.
        # Filesystem source IDs continue through the stricter identifier().
        lid = loop['loop_id']
        if lid in seen:
            raise ValueError('Duplicate candidate ID')
        seen.add(lid)
        if set(loop['gestalts']) - gestalts:
            raise ValueError('Unknown gestalt; add separately reviewed lexical gestalt to seed first')
        if lid in existing and existing[lid] != loop:
            raise ValueError('Existing loop ID cannot change')
        if names.get(loop['name'], lid) != lid or fingerprints.get(fingerprint(loop), lid) != lid:
            raise ValueError('Duplicate name/semantic fingerprint')
        names[loop['name']] = lid
        fingerprints[fingerprint(loop)] = lid
        if require_approved and c['review']['status'] != 'approved':
            raise ValueError('Integration requires explicit reviewed approval')
        if c['review']['status'] == 'rejected':
            raise ValueError('Rejected candidate')
        for e in c['evidence']:
            snap = read_snapshot(snapshots, e['source_id'])
            if e['snapshot_sha256'] != snap['snapshot_sha256'] or snap['source']['source_id'] != e['source_id']:
                raise ValueError('Evidence snapshot identity mismatch')
            chunk = next((ch for ch in snap['chunks'] if ch['chunk_id'] == e['chunk_id']), None)
            if not chunk or not chunk['start'] <= e['start'] < e['end'] <= chunk['end'] or snap['text'][e['start']:e['end']] != e['quote']:
                raise ValueError('Evidence quote/locator does not match snapshot')
        for term in c.get('terminology', []):
            if any(i >= len(c['evidence']) for i in term['evidence']):
                raise ValueError('Invalid terminology evidence index')
            if not any(term['exact_term'] in c['evidence'][i]['quote'] for i in term['evidence']):
                raise ValueError('Exact terminology must occur verbatim in cited excerpt')
        for claim in c['procedure'].values():
            if any(i >= len(c['evidence']) for i in claim['evidence']):
                raise ValueError('Invalid evidence index')
            if claim['basis'] == 'source_fact' and not claim['evidence']:
                raise ValueError('Source facts need exact source evidence')
        if not any(x['basis']=='source_fact' for x in c['procedure'].values()):
            raise ValueError('At least one grounded procedural source fact required')
        if c['procedure']['initial_test']['text'] != loop['initial_test'] or c['procedure']['exit']['text'] != loop['exit_predicate']:
            raise ValueError('Procedure/seed predicate mismatch')
    return {'batch_id': batch['batch_id'], 'validated': len(seen), 'note': 'Quotes and structure verified; semantic entailment, fresh-test adequacy and licensing remain reviewer judgments.'}


def build_isolated(seed, candidates, folder):
    """Unchanged SQL schema and canonical step/operator structure."""
    by_id = {c['loop']['loop_id']: c for c in candidates}
    if len(by_id) != len(candidates) or seed.get('manual_admission', {}) != {lid: digest(encoded(c)) for lid, c in by_id.items()}:
        raise ValueError('Procedure inventory differs from admitted seed inventory')
    seed_bytes = encoded(seed)
    (folder/'seed_loops.json').write_bytes(seed_bytes)
    with closing(sqlite3.connect(folder/'tote_loops.sqlite3')) as conn:
        conn.executescript((ROOT/'schema.sql').read_text())
        conn.executemany('INSERT INTO modality_operators VALUES (:operator_id,:symbol,:canonical_name,:definition,:evidence_channel,:may_assert_action)', seed['operators'])
        conn.executemany('INSERT INTO gestalts VALUES (:gestalt_id,:glyph,:lexical_form,:sense,:route,:recoverability_note)', seed['gestalts'])
        for loop in seed['loops']:
            conn.execute('INSERT INTO tote_loops VALUES (?,?,?,?,?,?,?,?)', tuple(loop[k] for k in ('loop_id','name','domain','objective','initial_test','exit_predicate','max_iterations','epistemic_status')))
            conn.executemany('INSERT INTO loop_gestalts VALUES (?,?,?)', [(loop['loop_id'], g, 'process-context') for g in loop['gestalts']])
            steps = steps_for(loop)
            if loop['loop_id'] in by_id:
                procedure = by_id[loop['loop_id']]['procedure']
                for index, key, prefix in [(3, 'operation', '💪'), (4, 'fresh_retest', '👀')]:
                    steps[index]['plain_text'] = procedure[key]['text']
                    steps[index]['nych_text'] = prefix + ' ' + procedure[key]['text']
            for s in steps:
                conn.execute('INSERT INTO tote_steps VALUES (?,?,?,?,?,?,?,?,?,?)', (loop['loop_id'], *(s[k] for k in ('step_index','phase','operator_id','plain_text','nych_text','proposition_kind','provenance','next_on_match','next_on_mismatch'))))
        if conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or conn.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Database integrity failure')
        conn.commit()
        (folder/'tote_loops.json').write_bytes(encoded(export_database(conn, digest(seed_bytes))))


def source_descriptor(snapshots, source_id):
    return {k: v for k, v in read_snapshot(snapshots, source_id).items() if k not in ('text', 'chunks')}


def validate_provenance(seed, provenance, snapshots):
    """Verify exact inventories and retained batch membership before any rebuild.

    The seed binds complete admitted candidates, not merely loop predicates.
    These hashes detect corruption, not an authenticated history: someone able
    to rewrite the seed and all evidence can still author a different bundle.
    """
    if not isinstance(provenance, dict) or provenance.get('format_version') != '1.0':
        raise ValueError('Unsupported provenance format')
    for key, kind in (('candidates', list), ('batches', dict), ('batch_envelopes', dict), ('fingerprints', dict), ('sources', dict)):
        if not isinstance(provenance.get(key), kind):
            raise ValueError('Missing or invalid provenance inventory: '+key)
    candidates = provenance['candidates']
    by_id = {c['loop']['loop_id']: c for c in candidates}
    if len(by_id) != len(candidates):
        raise ValueError('Duplicate provenance candidate')
    expected_admission = {lid: digest(encoded(c)) for lid, c in by_id.items()}
    if seed.get('manual_admission', {}) != expected_admission:
        raise ValueError('Seed admitted-loop inventory differs from provenance')
    loops = {l['loop_id']: l for l in seed['loops']}
    if len(loops) != len(seed['loops']):
        raise ValueError('Duplicate seed loop identity')
    for lid, c in by_id.items():
        if loops.get(lid) != c['loop']:
            raise ValueError('Provenance loop missing or differs from seed')
        validate_batch(dict(format_version='1.0', batch_id='retained', candidates=[c]), seed, snapshots, require_approved=True)
    expected_fingerprints = {lid: fingerprint(c['loop']) for lid, c in by_id.items()}
    if provenance['fingerprints'] != expected_fingerprints or len(set(expected_fingerprints.values())) != len(by_id):
        raise ValueError('Provenance fingerprint inventory mismatch')
    source_ids = {e['source_id'] for c in candidates for e in c['evidence']}
    if set(provenance['sources']) != source_ids:
        raise ValueError('Source inventory mismatch')
    for sid in source_ids:
        if provenance['sources'][sid] != source_descriptor(snapshots, sid):
            raise ValueError('Source identity changed; use a new source_id for changed bytes or metadata')
    envelopes = provenance['batch_envelopes']
    if set(provenance['batches']) != set(envelopes):
        raise ValueError('Batch envelope inventory mismatch')
    members = {}
    for bid, envelope in envelopes.items():
        validate_batch(envelope, seed, snapshots, require_approved=True)
        if envelope['batch_id'] != bid or digest(encoded(envelope)) != provenance['batches'][bid]:
            raise ValueError('Batch identity/hash mismatch')
        for candidate in envelope['candidates']:
            lid = candidate['loop']['loop_id']
            if candidate != by_id.get(lid):
                raise ValueError('Batch membership differs from retained candidates')
            members[lid] = candidate
    if members != by_id:
        raise ValueError('Candidate inventory differs from batch membership')


def integrate_batch(batch, seed, snapshots, output, *, prior_provenance=None):
    output = Path(output)
    if output.exists():
        raise ValueError('Output already exists; use a fresh output directory')
    validate_batch(batch, seed, snapshots, require_approved=True)
    if seed.get('manual_admission') and prior_provenance is None:
        raise ValueError('Enriched seed requires prior provenance')
    if prior_provenance is not None:
        validate_provenance(seed, prior_provenance, snapshots)
    prior = prior_provenance if prior_provenance is not None else {'candidates': [], 'batches': {}, 'batch_envelopes': {}}
    old = {c['loop']['loop_id']: c for c in prior['candidates']}
    for c in batch['candidates']:
        lid = c['loop']['loop_id']
        if lid in old and old[lid] != c:
            raise ValueError('Existing provenance cannot be silently replaced')
        old[lid] = c
    batch_hash = digest(encoded(batch))
    batches = dict(prior['batches'])
    if batch['batch_id'] in batches and batches[batch['batch_id']] != batch_hash:
        raise ValueError('Batch ID reused with different contents')
    batches[batch['batch_id']] = batch_hash
    envelopes = copy.deepcopy(prior['batch_envelopes'])
    envelopes[batch['batch_id']] = copy.deepcopy(batch)
    candidates = sorted(old.values(), key=lambda c: c['loop']['loop_id'])
    for c in candidates:
        validate_batch(dict(format_version='1.0', batch_id='carried', candidates=[c]), seed, snapshots, require_approved=True)
    result = copy.deepcopy(seed)
    ids = {l['loop_id'] for l in result['loops']}
    for c in batch['candidates']:
        if c['loop']['loop_id'] not in ids:
            result['loops'].append(copy.deepcopy(c['loop']))
    source_ids = sorted({e['source_id'] for c in candidates for e in c['evidence']})
    provenance = dict(format_version='1.0', batches=batches, batch_envelopes=envelopes, candidates=candidates, fingerprints={c['loop']['loop_id']: fingerprint(c['loop']) for c in candidates}, sources={sid: source_descriptor(snapshots, sid) for sid in source_ids})
    result['manual_admission'] = {c['loop']['loop_id']: digest(encoded(c)) for c in candidates}
    validate_provenance(result, provenance, snapshots)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.manual-build-', dir=output.parent) as temp:
        stage = Path(temp)/'result'
        stage.mkdir()
        build_isolated(result, candidates, stage)
        for source_id in source_ids:
            shutil.copytree(Path(snapshots)/identifier(source_id), stage/'sources'/source_id)
        (stage/'provenance.json').write_bytes(encoded(provenance))
        stage.rename(output)
    return dict(seed=result, provenance=provenance, output=str(output))


def audit_output(output):
    folder = Path(output)
    seed_bytes = (folder/'seed_loops.json').read_bytes()
    seed = json.loads(seed_bytes)
    provenance = json.loads((folder/'provenance.json').read_text())
    validate_provenance(seed, provenance, folder/'sources')
    with tempfile.TemporaryDirectory(prefix='tote-audit-') as temp:
        stage = Path(temp)
        build_isolated(seed, provenance['candidates'], stage)
        expected = (stage/'tote_loops.json').read_bytes()
        if expected != (folder/'tote_loops.json').read_bytes():
            raise ValueError('Output export differs from seed and procedure provenance')
    with closing(sqlite3.connect((folder/'tote_loops.sqlite3').resolve().as_uri()+'?mode=ro', uri=True)) as conn:
        if conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or conn.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Output database integrity failure')
        if encoded(export_database(conn, digest(seed_bytes))) != expected:
            raise ValueError('Output database content differs from deterministic rebuild')
    return dict(audited=True, loops=len(seed['loops']), candidates=len(provenance['candidates']))
