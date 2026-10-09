# -*- coding: utf-8 -*-
"""Count substantive new AD body; exclude navigation, references and repeats."""
import json,re,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
db=json.loads((ROOT/'data/knowledge.json').read_text());program=json.loads((ROOT/'data/alzheimer/program.json').read_text());seen=set();chapters=[]
def norm(t):return re.sub(r'\s+','',t).strip()
def han(t):return len(re.findall(r'[\u3400-\u4dbf\u4e00-\u9fff]',t))
for r in db['records']:
 if r.get('research_program')!=program['id']:continue
 texts=[]
 for s in r['sections']:
  texts.extend(s.get('text',[]));texts.extend(s.get('items',[]))
  texts.extend('；'.join(row) for row in s.get('table',[])[1:])
 count=chars=repeat=0
 for t in texts:
  t=norm(t)
  if not t:continue
  h=hashlib.sha256(t.encode()).hexdigest()
  if h in seen:repeat+=han(t);continue
  seen.add(h);count+=han(t);chars+=len(t)
 chapters.append({'id':r['id'],'title':r['title'],'han_chars':count,'visible_chars':chars,'excluded_repeated_han':repeat,'status':r.get('content_status','draft')})
report={'program':program['id'],'target_han_chars':program['target_han_chars'],'counted_han_chars':sum(c['han_chars'] for c in chapters),'visible_chars':sum(c['visible_chars'] for c in chapters),'excluded_repeated_han':sum(c['excluded_repeated_han'] for c in chapters),'drafted_chapters':len(chapters),'planned_chapters':sum(len(p['chapters']) for p in program['parts']),'target_met':sum(c['han_chars'] for c in chapters)>=program['target_han_chars'],'chapters':chapters,'counting_rule':program['counting_rule']}
(ROOT/'data/alzheimer/word-count.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='chapters'},ensure_ascii=False))

if "--require-target" in sys.argv and not report["target_met"]:raise SystemExit("Research target not met; GOAL must remain active")
