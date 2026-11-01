"""Author-curated DERIVED specifications after reading publisher section snapshots."""
from pathlib import Path
import json,re,hashlib,subprocess,collections
ROOT=Path(__file__).parent
manifest=json.loads((ROOT/'source-manifest.json').read_text())
M={x['key']:x for x in manifest}
S='/home/deepsleep_r/.hermes/skills/research/grounded-citations/scripts/sources.py'

def exact(key, words):
    # Select the original substring, preserving PDF line breaks; no quote normalization on disk.
    text=(ROOT/M[key]['local_snapshot']).read_text()
    pattern=r'\s+'.join(re.escape(w) for w in words.split())
    m=re.search(pattern,text)
    if not m: raise ValueError((key,words))
    return m.group()

def src(key,section,quotes):
    m=M[key]
    license=( 'GNU Free Documentation License 1.3 or later; short research excerpts with attribution; see QGIS licensing snapshot.' if key.startswith('qgis') else
        'US government NPS text generally public domain under 17 USC 105, unless otherwise indicated; third-party images excluded.' if key.startswith('nps') else
        'NIST employee non-SRD text generally not copyright-protected in US under 17 USC 105; handbook co-produced with SEMATECH, so no blanket public-domain assertion; limited attributed research quotations only.')
    edition=('QGIS 3.40 documentation' if key.startswith('qgis') else 'Museum Handbook Part I, Chapter 4 (2016)' if key.startswith('nps') else 'NIST/SEMATECH e-Handbook of Statistical Methods, live HTML; no edition/date displayed in retained section')
    out={k:m[k] for k in ['url','title','local_snapshot','sha256','accessed_at']}
    out.update(publisher='QGIS Project' if key.startswith('qgis') else 'US National Park Service' if key.startswith('nps') else 'NIST / SEMATECH',section=section,license=license,edition=edition,rights_basis_url=M['qgis-license' if key.startswith('qgis') else 'nps-rights' if key.startswith('nps') else 'nist-rights']['url'])
    out['quotes']=[{'text':exact(key,q),'supports':supports} for q,supports in quotes]
    for q in out['quotes']:
        subprocess.run(['python',S,'--ledger',str(ROOT/'citation-ledger.json'),'quote',m['citation_id'].split(']')[0].strip('['),'--text',q['text'],'--from',str(ROOT/m['local_snapshot'])],check=True,capture_output=True,text=True)
    return out

common_stop=['Exit only when the fresh retest satisfies the exit predicate; preserve the before/after evidence.', 'Stop unresolved on missing evidence, missing authorization, no measurable progress, oscillation, or exhausted author-policy iteration budget.']
def loop(id,name,domain,profession,objective,test,exit,operate,retest,sources,review,notes,lexical,budget=3):
    return dict(loop_id=id,name=name,domain=domain,profession=profession,objective=objective,initial_test=test,exit_predicate=exit,max_iterations=budget,epistemic_status='DERIVED',gestalts={'lexical':lexical},procedure={'operate_step':operate,'retest':retest,'stop_conditions':common_stop},sources=sources,review_required=review,notes=notes+['This is an author-derived research specification, not a published TOTE loop, executed procedure, certified result, or professional authorization.','max_iterations is author policy, not a manual requirement. Test windows, review criteria, progress checks and closure logic are derived unless explicitly quoted.'])
L=[]
L.append(loop('A-GEO-001','Review forestry map ground-control residuals','GEOSPATIAL_CARTOGRAPHY','Cartographer / forestry GIS technician','Prepare a legacy forestry map registration for reviewer acceptance.',
'Read fresh dX[pixels] and dY[pixels] for the exercise map control points; flag residuals exceeding the exercise-specific 10-pixel criterion and check coordinate transcription.',
'After correction, every reviewed absolute dX and dY is at most 10 pixels, control-point identities and CRS are confirmed, and a cartographer accepts the overlay comparison; not a universal mapping accuracy claim.',
'Propose one correction to a demonstrably mis-digitized control point or transcribed coordinate, for a cartographer to approve on a working copy; preserve the reference values and prior residuals.',
'Recompute the control-point residual table from the changed working copy and compare the registered map with its reference aerial image; do not reuse the old residuals.',
[src('qgis-georef','Training Manual §14.2.2, Follow Along: Georeferencing the scanned map',[
('The error in pixels can be seen also in the GCP table in the dX[pixels] and dY[pixels] columns.',['initial_test','procedure.retest']),
('The error in pixels should not be higher than 10 pixels.',['initial_test','exit_predicate']),
('If it is, you should review the points you have digitized and the coordinates you have entered to find what the problem is.',['procedure.operate_step']),
('set the map transparency to 50% and compare it to the aerial image.',['procedure.retest','exit_predicate'])])],
'Cartographer must approve the coordinate system, reference imagery, corrections and acceptance criteria before use; unsuitable as cadastral/navigation assurance.',
['The 10-pixel advice is from this Finland forestry training exercise only; the absolute component interpretation and mandatory overlay sign-off are conservative author derivations.'],['forestry map control-point residual','legacy paper map georeferencing']))
L.append(loop('A-GEO-002','Resolve reviewed polygon overlap findings','GEOSPATIAL_CARTOGRAPHY','Cartographer / spatial data quality analyst','Bring a thematic polygon coverage into conformance with an approved no-overlap rule without erasing legitimate features.',
'Run full-layer topology validation using the reviewer-approved Must not overlap rule; retain feature IDs and inspect flagged common areas against the authoritative reference.',
'A fresh full-layer validation reports zero overlaps under the same approved rule, and a cartographer confirms the corrections preserve the intended boundaries; no claim of legal boundary accuracy.',
'For one confirmed erroneous overlap, propose a boundary edit on a copy using the authoritative map evidence; a cartographer must approve edits, not automatic deletion of every flagged feature.',
'Apply the same active rule to all features again after the approved edit and review the new error table, including previously edited neighbors.',
[src('qgis-topology','User Manual §25.2.5, polygon rules and error validation',[
('Must not overlap : Adjacent polygons should not share common area.',['initial_test','exit_predicate']),
('Validate All : applies the active rules to all the features of the involved layer(s)',['initial_test','procedure.retest']),
('Errors will show up in the table of results containing type of error, layer and feature ID.',['initial_test','procedure.retest']),
('where you can use QGIS digitizing tools to fix the error.',['procedure.operate_step'])])],
'Spatial-data custodian must approve applicable topology rules and authoritative boundaries; do not modify cadastral or other legally consequential data without qualified authorization.',
['Zero-error termination and reviewer sign-off are derived; a clean checker output is not proof of geographic truth.'],['polygon overlap review','thematic coverage topology']))
L.append(loop('A-QUAL-001','Review a statistical process-control signal','MANUFACTURING_QUALITY','Quality engineer / statistical process-control analyst','Resolve a reviewed chart signal using documentary evidence and an approved corrective-action plan.',
'Inspect a valid chart with approved fixed control limits and predeclared nonrandom-pattern rules; flag an outside-limit point or systematic pattern.',
'Fresh samples over a quality-engineer-defined verification window show no outside-limit points or signals under the same approved pattern rules; documented cause disposition is accepted by the engineer. This does not certify product conformance.',
'Investigate the suspected assignable cause and draft one evidence-supported corrective-action request for qualified review; this research specification gives no machine adjustment or shop-floor command.',
'After separately authorized corrective work, chart newly collected samples under the approved sampling plan and test the same limits and nonrandom-pattern rules; do not merely relabel old points.',
[src('nist-control','e-Handbook §6.3.1, Strategies for dealing with out-of-control findings',[
('If a data point falls outside the control limits, we assume that the process is probably out of control',['initial_test']),
('an investigation is warranted to find and eliminate the cause or causes.',['procedure.operate_step']),
('Control charts are used to routinely monitor quality.',['procedure.retest']),
('"in control" implies that all points are between the control limits and they form a random pattern.',['exit_predicate','procedure.retest'])])],
'Quality engineer/statistician must approve chart assumptions, sampling window, pattern rules and corrective-action request; any physical intervention requires a separate qualified site procedure.',
['Finite-window absence of signals is not proof of perpetual stability. Do not widen limits to suppress a signal; verification-window length and cause disposition are authored review policy.'],['assignable cause chart signal','quality control nonrandom pattern']))
L.append(loop('A-QUAL-002','Review stable but off-target process performance','MANUFACTURING_QUALITY','Manufacturing quality engineer','Prepare and assess a reviewed improvement proposal for a stable but unacceptable process.',
'First confirm stability using the approved control-chart plan; compare the documented process level and variability with separately approved target and acceptance limits. Enter only if stable but unacceptable.',
'New post-intervention data remain stable and meet the preapproved target/variation criteria over the approved verification window, with quality-engineer sign-off; missing specification or stability evidence is unresolved, not success.',
'Choose one documented improvement proposal (experimental study, calibration review, or historical-data re-analysis) for quality-engineer approval. Do not perform calibration or prescribe process settings in this research artifact.',
'After any separately approved intervention, collect independent fresh observations, check stability first, then recompare level and variability with the unchanged approved target criteria.',
[src('nist-unacceptable','e-Handbook §6.1.5, Process improvement techniques / Process must be stable',[
('the average level is too high or too low or the variability is unacceptable?',['initial_test','exit_predicate']),
('experiments calibration re-analysis of historical database can be initiated to put the process on target or reduce the variability.',['procedure.operate_step','exit_predicate']),
('the process must be stable before it can be centered at a target value or its overall variation can be reduced.',['initial_test','procedure.retest','exit_predicate'])]),
src('nist-control','e-Handbook §6.3.1, monitoring and in-control interpretation',[
('Control charts are used to routinely monitor quality.',['procedure.retest']),
('"in control" implies that all points are between the control limits and they form a random pattern.',['initial_test','procedure.retest','exit_predicate'])])],
'Quality engineer/statistician must approve stability, specification limits, target tolerances, sample design and any experiment/calibration; this is not equipment operating guidance.',
['The two handbook sections motivate the improvement-and-monitoring structure; fresh-sample closure and specific acceptance criteria must be supplied by the qualified reviewer.'],['stable process off target','unacceptable process variability']))
L.append(loop('A-PRES-001','Review a museum collection microclimate deviation','COLLECTIONS_PRESERVATION','Museum collections manager / preventive conservator','Assess whether a reviewed non-mechanical preservation change restores approved temperature/RH conditions.',
'Review calibrated logger records and contextual observations against conservator-approved temperature/RH setpoints, permissible fluctuations and a declared assessment window; identify a persistent deviation.',
'Fresh logger records for the agreed post-change window are stable and within the approved setpoint ranges, with conservator acceptance; close this corrective episode only, not ongoing monitoring.',
'Prepare one evidence-based non-mechanical climate-control proposal for the qualified museum team; the team decides and separately authorizes any implementation. No HVAC work, hazardous materials treatment, or object relocation is instructed here.',
'After an approved change, review newly recorded logger data with matched locations and contextual notes, comparing against the same approved ranges and baseline.',
[src('nps-environment','Museum Handbook I, Ch.4 §§G.4/H.1, printed pp.4:30–4:32; PDF pp.33–35',[
('if temperature and RH levels are stable and within the recommended set point and permissible range',['initial_test','exit_predicate']),
('Assemble a qualified team to carefully plan and implement a climate control strategy.',['procedure.operate_step','review_required']),
('Implement non-mechanical measures to control climate when and wherever feasible',['procedure.operate_step']),
('Monitor regularly to insure that these controls are effective and adjust accordingly.',['procedure.retest'])])],
'Preventive conservator, curator and facilities team must approve collection-specific limits, observation duration and any intervention. No universal RH prescription is inferred.',
['No numerical climate target is imported: different collection materials and historic structures require professional judgment. Baseline duration requirements are not replaced by this loop budget.'],['collection microclimate deviation','museum temperature humidity review']))
L.append(loop('A-PRES-002','Review the effectiveness of a collection lighting plan','COLLECTIONS_PRESERVATION','Museum conservator / collections lighting coordinator','Assess whether a reviewed lighting-protection change meets collection-specific exposure criteria.',
'Review baseline visible-light, UV, heat and exposure-duration records at declared monitoring sites against conservator-approved material-specific criteria; flag a deviation or unverified filter performance.',
'Fresh before/after-comparable site records satisfy all approved visible-light, UV, heat and exposure-duration criteria, and the conservator accepts effectiveness; ongoing exposure monitoring continues.',
'Prepare one lighting-improvement-plan revision for conservator and facilities review, such as a documented reduction in exposure duration. Any installation, electrical work or handling of collection objects is outside this specification.',
'After separate approval/implementation, obtain new comparable readings from the same declared sites and assess the approved exposure schedule; retain the before/after Light and Heat Measurement Record.',
[src('nps-environment','Museum Handbook I, Ch.4 §J.1–3, printed pp.4:46–4:49; PDF pp.49–52',[
('gather baseline and ongoing lighting information',['initial_test']),
('Lower light intensity and duration in exhibit and storage areas.',['procedure.operate_step']),
('Monitor and document light levels before and after taking any action to be sure that your changes have been effective.',['procedure.retest']),
('be sure that light levels are at required levels and that UV blocking materials are still effective, that there is no IR and that visible light is appropriately controlled',['exit_predicate'])])],
'Conservator and facilities staff must approve sensitivity classifications, exposure budgets, meter procedures, plan revisions and any physical/electrical work; no object-safety guarantee.',
['The multi-factor exit and continuation of monitoring are derived review policy. No electrical procedure, UV source operation or fixed lighting level is prescribed.'],['museum lighting effectiveness','collection light exposure review']))
(ROOT/'candidates.json').write_text(json.dumps(L,indent=2,ensure_ascii=False)+'\n')
print('Wrote',len(L),'DERIVED candidates',dict(collections.Counter(x['domain'] for x in L)))
