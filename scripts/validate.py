# -*- coding: utf-8 -*-
"""Check referential integrity, local links/anchors and published page structure."""
import json
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=set();self.links=[];self.lang=None;self.main=0;self.h1=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html':self.lang=a.get('lang')
  if a.get('id'):
   assert a['id'] not in self.ids,('duplicate DOM id',a['id']);self.ids.add(a['id'])
  if tag=='main':self.main+=1
  if tag=='h1':self.h1+=1
  for k in ('href','src'):
   if k in a:self.links.append(a[k])
manifest=json.loads((ROOT/'data/build-manifest.json').read_text())
pages={}
for p in manifest['pages']:
 parser=Page();parser.feed((ROOT/p).read_text());pages[p]=parser
 assert parser.lang=='zh-CN' and parser.main==1 and parser.h1==1,(p,'semantic structure')
errors=[];checked=0
for p,parser in pages.items():
 for url in parser.links:
  u=urlsplit(url)
  if u.scheme or u.netloc:continue
  target=unquote(u.path)
  if target.startswith('/brainlab/'):dest=ROOT/target.removeprefix('/brainlab/')
  elif target.startswith('/'):continue
  else:dest=(ROOT/p).parent/target if target else ROOT/p
  dest=dest.resolve()
  if dest.is_dir():dest/= 'index.html'
  if not dest.exists():errors.append((p,url,'missing file'));continue
  if u.fragment and dest.suffix=='.html':
   rp=str(dest.relative_to(ROOT));dp=pages.get(rp)
   if not dp:dp=Page();dp.feed(dest.read_text())
   if unquote(u.fragment) not in dp.ids:errors.append((p,url,'missing anchor'))
  checked+=1
assert not errors,errors[:30]
db=json.loads((ROOT/'data/knowledge.json').read_text());index=json.loads((ROOT/'data/search-index.json').read_text())
ids={r['id'] for r in db['records']};sources={s['id'] for s in db['sources']}
trial_data=json.loads((ROOT/'data/alzheimer/trial-extractions.json').read_text())
trial_ids={'trial-'+x['id'] for x in trial_data['studies']}
assert {x['id'] for x in index}==ids|sources|trial_ids
assert len(index)==len(ids)+len(sources)+len(trial_ids)
for x in index:
 target=urlsplit(x['url']);assert target.path in pages and (not target.fragment or target.fragment in pages[target.path].ids),('search target missing',x['id'])
for r in db['records']:
 if r['collection']=='games':
  assert len(r['demands'])==9
  assert len({d['ability_id'] for d in r['demands']})==9
  assert all(d['ability_id'] in ids and d['level'] in (0,1,2) for d in r['demands'])
 for rel in r['relationships']:assert rel['target_id'] in ids and rel['type'] in ['task-demand','research-context','see-also']
# Validate structured evidence provenance, not scientific effect correctness.
extract_path=ROOT/'data/alzheimer/trial-extractions.json'
if extract_path.exists():
 extracts=json.loads(extract_path.read_text())
 record_map={x['id']:x for x in db['records']}
 source_map={x['id']:x for x in db['sources']}
 study_ids=set()
 allowed_levels={'clinical_dementia_algorithm','claims_adrd','independent_cognition','task_and_transfer','task_and_eeg','clinical_dementia','clinical_dementia_and_mci'}
 for x in extracts['studies']:
  assert x['id'] not in study_ids,('duplicate study extraction',x['id'])
  study_ids.add(x['id'])
  assert x['source_id'] in source_map and x['record_id'] in record_map
  assert x['source_id'] in record_map[x['record_id']]['source_ids'],('uncited extraction source',x['id'])
  assert x['source_url']==source_map[x['source_id']]['url'],('provenance URL mismatch',x['id'])
  assert x['outcome_level'] in allowed_levels
  assert x['intervention_role'] in extracts['intervention_roles']
  for e in x.get('effects',[]):
   assert e['ci_lower']<=e['estimate']<=e['ci_upper'],('invalid effect interval',x['id'])
   assert e['ci_level'] in [.95,.99] and e['unit'] and e['endpoint'] and e['contrast'] and e['source_location']
   if e['measure']=='HR':assert e['ci_lower']>0
   if e['p_value'] is not None:assert 0<=e['p_value']<=1

  if x.get('event_counts'):
   assert x['event_counts']['note'] and x['event_counts']['source_location']
   for e in x['event_counts']['groups']:
    assert isinstance(e['events'],int) and isinstance(e['participants'],int) and 0<=e['events']<=e['participants'],('invalid event denominator',x['id'])
  if x.get('individual_change'):
   assert x['individual_change']['threshold'] and x['individual_change']['limitations']
   assert all(0<=v<=1 for v in x['individual_change']['proportions'].values())

  for field in ['population','intervention','comparator','outcome','effect_summary','limitations_and_pending','access_scope','cohort_key','audit_status']:
   assert isinstance(x[field],str) and x[field].strip(),('missing extraction field',x['id'],field)
 assert not extracts['complete'] or all(x['audit_status']=='verified' for x in extracts['studies']), 'Incomplete study audits cannot be labelled complete'

# Download integrity: archived authored files must match the current build.
import zipfile
bundle_path=ROOT/'downloads/alzheimer-research.zip'
with zipfile.ZipFile(bundle_path) as archive:
 assert archive.testzip() is None, 'Corrupt research archive'
 for name in archive.namelist():
  assert not name.startswith('/') and '..' not in Path(name).parts, 'Unsafe archive member'
  if name=='README.txt':continue
  assert archive.read(name)==(ROOT/name).read_bytes(),('Stale offline research file',name)
 draft=(ROOT/'research-programs/alzheimer/DRAFT.md').read_text()
 word_count=json.loads((ROOT/'data/alzheimer/word-count.json').read_text())
assert format(word_count['counted_han_chars'],',') in draft, 'Stale draft count'

print(f'PASS: {len(pages)} pages; {checked} local links/assets/anchors; {len(index)} searchable records; all citations, relationships and demand IDs valid')
