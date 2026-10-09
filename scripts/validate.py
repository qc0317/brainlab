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
assert {x['id'] for x in index}==ids|sources
assert len(index)==len(ids)+len(sources)
for r in db['records']:
 if r['collection']=='games':
  assert len(r['demands'])==9
  assert len({d['ability_id'] for d in r['demands']})==9
  assert all(d['ability_id'] in ids and d['level'] in (0,1,2) for d in r['demands'])
 for rel in r['relationships']:assert rel['target_id'] in ids and rel['type'] in ['task-demand','research-context','see-also']
print(f'PASS: {len(pages)} pages; {checked} local links/assets/anchors; {len(index)} searchable records; all citations, relationships and demand IDs valid')
