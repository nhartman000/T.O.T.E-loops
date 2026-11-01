from pathlib import Path
import requests, hashlib, json, datetime, subprocess
from bs4 import BeautifulSoup
import pymupdf as fitz
ROOT=Path(__file__).parent
S='/home/deepsleep_r/.hermes/skills/research/grounded-citations/scripts/sources.py'
ledger=str(ROOT/'citation-ledger.json')
def cite(*args):
    return subprocess.check_output(['python',S,'--ledger',ledger,*args],text=True).strip()
items=[
('qgis-georef','https://docs.qgis.org/3.40/en/docs/training_manual/forestry/map_georeferencing.html'),
('qgis-topology','https://docs.qgis.org/3.40/en/docs/user_manual/plugins/core_plugins/plugins_topology_checker.html'),
('nist-control','https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc31.htm'),
('nist-unacceptable','https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc15.htm'),
('nps-environment','https://www.nps.gov/subjects/museums/upload/MHI_Ch4_Environment.pdf'),
('qgis-license','https://docs.qgis.org/3.40/en/docs/about/license/index.html'),
('nist-rights','https://www.nist.gov/open/license'),
('nps-rights','https://www.nps.gov/aboutus/disclaimer.htm')]
manifest=[]
for key,url in items:
    r=requests.get(url,timeout=90);r.raise_for_status()
    if key=='nps-environment':
        doc=fitz.open(stream=r.content,filetype='pdf')
        pages=[{'pdf_page':i+1,'text':p.get_text()} for i,p in enumerate(doc)]
        # Save only selected environment monitoring sections, not the entire handbook/chapter.
        selected=[p for p in pages if 32<=p['pdf_page']<=37 or 49<=p['pdf_page']<=54]
        text='\n\n'.join('[PDF page %d]\n%s'%(p['pdf_page'],p['text']) for p in selected)
        title='NPS Museum Handbook Part I, Chapter 4: Museum Collections Environment (2016)'
    else:
        soup=BeautifulSoup(r.content,'html.parser')
        title=soup.title.get_text(' ',strip=True) if soup.title else key
        for tag in soup(['script','style','nav']):tag.decompose()
        main=soup.find('div',role='main') or soup.find('main') or soup.body
        text=main.get_text(' ',strip=True)
    out=ROOT/'snapshots'/f'{key}.txt';out.write_text(text,encoding='utf-8')
    rec={'key':key,'url':url,'final_url':r.url,'title':title,'accessed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'http_status':r.status_code,'local_snapshot':str(out.relative_to(ROOT)),'snapshot_format':'UTF-8 extracted publisher text; HTML whitespace normalized; PDF extraction preserves line breaks','sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'retrieved_response_sha256':hashlib.sha256(r.content).hexdigest(),'retrieved_response_retained':False}
    rec['citation_id']=cite('add',url,'--title',title)
    manifest.append(rec)
    print(key,len(text),rec['citation_id'],title)
(ROOT/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
