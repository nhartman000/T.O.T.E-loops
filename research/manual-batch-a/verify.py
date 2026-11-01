from pathlib import Path
import json,hashlib,collections,subprocess
ROOT=Path(__file__).parent
L=json.loads((ROOT/'candidates.json').read_text())
M=json.loads((ROOT/'source-manifest.json').read_text())
def require(condition,message):
    if not condition: raise ValueError(message)
fields='loop_id name domain profession objective initial_test exit_predicate max_iterations epistemic_status gestalts procedure sources review_required notes'.split()
require(len(L)==6,'six candidates required')
require(len({x['loop_id'] for x in L})==6,'duplicate ID')
counts=collections.Counter(x['domain'] for x in L)
require(len(counts)==3 and set(counts.values())=={2},'three domains with two each')
quote_count=0
for m in M:
    require(hashlib.sha256((ROOT/m['local_snapshot']).read_bytes()).hexdigest()==m['sha256'],'manifest hash mismatch')
for x in L:
    require(set(fields)<=set(x),'missing candidate fields')
    require(x['epistemic_status']=='DERIVED','status')
    require(type(x['max_iterations']) is int and x['max_iterations']>0,'bound')
    require(x['gestalts']['lexical'] and x['review_required'],'lexical/review missing')
    require(all(k in x['procedure'] for k in ['operate_step','retest','stop_conditions']),'procedure')
    supports=set()
    for s in x['sources']:
        b=(ROOT/s['local_snapshot']).read_bytes(); text=b.decode('utf-8')
        require(hashlib.sha256(b).hexdigest()==s['sha256'],'candidate hash mismatch')
        require(all(s.get(k) for k in ['url','title','publisher','section','license','edition','accessed_at','rights_basis_url']),'source metadata')
        for q in s['quotes']:
            require(q['text'] in text,'not an exact substring')
            require(len(q['text'].split())<=50,'excerpt too long')
            quote_count+=1;supports.update(q['supports'])
    require({'initial_test','procedure.operate_step','procedure.retest','exit_predicate'}<=supports,'missing phase support')
result={'status':'PASS','candidate_count':len(L),'domain_counts':dict(counts),'manifest_snapshot_count':len(M),'candidate_source_references':sum(len(x['sources']) for x in L),'exact_quote_occurrences_checked':quote_count,'all_candidate_and_manifest_sha256_match':True,'all_four_tote_phases_have_quote_support_labels':True,'max_quote_words':max(len(q['text'].split()) for x in L for s in x['sources'] for q in s['quotes']),'scope':'Isolated derived specifications only; no professional execution, semantic-entailment certification, schema/build/database integration or runtime test.'}
(ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
