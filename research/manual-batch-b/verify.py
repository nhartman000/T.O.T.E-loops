from pathlib import Path
import collections,datetime,hashlib,json,subprocess
R=Path(__file__).resolve().parent
loops=json.loads((R/'candidates.json').read_text()); manifest=json.loads((R/'source-manifest.json').read_text())
def require(ok,msg):
 if not ok: raise ValueError(msg)
required={'loop_id','name','domain','profession','objective','initial_test','exit_predicate','max_iterations','epistemic_status','gestalts','procedure','sources','review_required','notes'}
require(len(loops)==6,'six records required'); counts=collections.Counter(x['domain'] for x in loops)
require(len(counts)==3 and set(counts.values())=={2},'two per domain'); require(len({x['loop_id'] for x in loops})==6,'duplicate IDs')
for key,m in manifest.items():
 require(hashlib.sha256((R/m['local_snapshot']).read_bytes()).hexdigest()==m['sha256'],key+' text hash')
 require(hashlib.sha256((R/m['raw_snapshot']).read_bytes()).hexdigest()==m['raw_sha256'],key+' raw hash')
nq=0
for x in loops:
 require(required<=x.keys(),x['loop_id']+' fields');require(x['epistemic_status']=='DERIVED' and x['review_required'] is True,'boundary')
 require(isinstance(x['max_iterations'],int) and x['max_iterations']>0,'cap');require(bool(x['gestalts']['lexical']),'lexical')
 support=set()
 for s in x['sources']:
  text=(R/s['local_snapshot']).read_text(); require(hashlib.sha256(text.encode()).hexdigest()==s['sha256'],'source hash')
  for q in s['quotes']:
   require(q['text'] in text,'nonverbatim quote');support.update(q['supports']);nq+=1
   require(q['locator']==s['local_snapshot']+':L'+str(text[:text.index(q['text'])].count('\n')+1),'locator')
 require({'initial_test','procedure.operate_step','procedure.retest','exit_predicate'}<=support,'missing phase support')
S='/home/deepsleep_r/.hermes/skills/research/grounded-citations/scripts/sources.py'
for key,id,needle in [('pg_license',3,'Permission to use'),('im_license',6,'Source form shall'),('w3c_easy',9,'These checks cover'),('w3c_license',10,'Public documents on'),('w3c_software_license',11,'Permission')]:
 text=(R/manifest[key]['local_snapshot']).read_text();excerpt=next(line for line in text.splitlines() if needle.lower() in line.lower())
 subprocess.run(['python',S,'--ledger',str(R/'citation-ledger.json'),'quote',str(id),'--text',excerpt,'--from',str(R/manifest[key]['local_snapshot'])],check=True,capture_output=True)
p=subprocess.run(['python',S,'--ledger',str(R/'citation-ledger.json'),'verify',str(R/'source-brief.md'),'--evidence'],check=True,capture_output=True,text=True)
result={'status':'PASS','verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate_count':len(loops),'domain_counts':dict(counts),'checked_quotes':nq,'checked_source_snapshots':len(manifest),'quote_validation':'exact substring and line locator; phase support labels checked structurally, entailment not automated','domain_operations_executed':False,'citation_verification':p.stdout+p.stderr,'candidates_sha256':hashlib.sha256((R/'candidates.json').read_bytes()).hexdigest()}
(R/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
