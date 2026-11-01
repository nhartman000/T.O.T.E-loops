from pathlib import Path
from urllib.request import urlopen, Request
from html.parser import HTMLParser
import hashlib,json,datetime,subprocess
ROOT=Path(__file__).resolve().parent
class Text(HTMLParser):
 def __init__(self): super().__init__();self.parts=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ('script','style'): self.skip+=1
  if t in ('p','div','h1','h2','h3','h4','li','pre','tr','br'): self.parts.append('\n')
 def handle_endtag(self,t):
  if t in ('script','style'): self.skip-=1
  if t in ('p','div','h1','h2','h3','h4','li','pre','tr'): self.parts.append('\n')
 def handle_data(self,d):
  if not self.skip:self.parts.append(d)
urls={
 'pg_verifybackup':'https://www.postgresql.org/docs/18/app-pgverifybackup.html',
 'pg_checksums':'https://www.postgresql.org/docs/18/app-pgchecksums.html',
 'pg_license':'https://www.postgresql.org/about/licence/',
 'im_identify':'https://imagemagick.org/identify/',
 'im_compare':'https://imagemagick.org/compare/',
 'im_license':'https://imagemagick.org/license/',
 'w3c_title':'https://www.w3.org/WAI/test-evaluate/easy-checks/title/',
 'w3c_headings':'https://www.w3.org/WAI/test-evaluate/easy-checks/headings/',
 'w3c_easy':'https://www.w3.org/WAI/test-evaluate/easy-checks/',
 'w3c_license':'https://www.w3.org/copyright/document-license/',
 'w3c_software_license':'https://www.w3.org/copyright/software-license/'
}
ROOT.joinpath('snapshots').mkdir(parents=True,exist_ok=True)
ROOT.joinpath('.gitignore').write_text('snapshots/\n__pycache__/\n')
ledger=ROOT/'citation-ledger.json'
S='/home/deepsleep_r/.hermes/skills/research/grounded-citations/scripts/sources.py'
subprocess.run(['python',S,'--ledger',str(ledger),'reset'],check=True)
records={}
for key,url in urls.items():
 with urlopen(Request(url,headers={'User-Agent':'ManualResearch/1.0'}),timeout=60) as r:
  raw=r.read();final=r.url;headers=dict(r.headers)
 ROOT.joinpath('snapshots',key+'.html').write_bytes(raw)
 parser=Text();parser.feed(raw.decode('utf-8'))
 text='\n'.join(' '.join(x.split()) for x in ''.join(parser.parts).splitlines() if x.strip())+'\n'
 ROOT.joinpath('snapshots',key+'.txt').write_text(text)
 records[key]={'url':url,'resolved_url':final,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'http_last_modified':headers.get('Last-Modified'),'local_snapshot':'snapshots/'+key+'.txt','sha256':hashlib.sha256(text.encode()).hexdigest(),'raw_snapshot':'snapshots/'+key+'.html','raw_sha256':hashlib.sha256(raw).hexdigest(),'text_characters':len(text)}
 subprocess.run(['python',S,'--ledger',str(ledger),'add',url,'--title',key],check=True)
 print(key,len(raw),len(text))
ROOT.joinpath('source-manifest.json').write_text(json.dumps(records,indent=2)+'\n')
