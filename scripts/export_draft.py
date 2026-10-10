# -*- coding: utf-8 -*-
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];d=json.loads((root/'data/knowledge.json').read_text());p=json.loads((root/'data/alzheimer/program.json').read_text());w=json.loads((root/'data/alzheimer/word-count.json').read_text());records={r['id']:r for r in d['records']};sources={s['id']:s for s in d['sources']};lines=['# '+p['title'],'','进行中 · 正文起草与数据审核并行。','',f"目前新版正文去重计数：{w['counted_han_chars']:,} 汉字 / 目标至少 {w['target_han_chars']:,} 汉字；不是已完成十万字报告。",'',p['counting_rule'],'','用途：个人非商业研究与多端阅读；文献许可、原文与原创解析分别记录。','']
for part in p['parts']:
 lines+=['# '+part['title'],'',part['description'],'','阅读问题：'+part.get('reader_question',''),'']
 for ch in part['chapters']:
  if ch['id'] not in p['drafted_record_ids']:continue
  r=records[ch['id']];lines+=['## '+r['title'],'',r['summary'],'','状态：起草完成，审核进行中。','']
  for sec in r['sections']:
   lines+=['### '+sec['title'],'']
   lines+=sum(([t,''] for t in sec.get('text',[])),[])
   lines+=['- '+i for i in sec.get('items',[])]+[''] if sec.get('items') else []
   table=sec.get('table',[])
   if table:lines+=['| '+' | '.join(table[0])+' |','| '+' | '.join('---' for _ in table[0])+' |']+['| '+' | '.join(row)+' |' for row in table[1:]]+['']
   if sec.get('source_ids'):lines+=['依据：'+', '.join('['+sid+']('+sources[sid]['url']+')' for sid in sec['source_ids']),'']
  for im in ([r['image']] if r.get('image') else [])+r.get('research_figures',[]):
   lines+=['### '+im.get('title','原文图'),'','!['+im['caption']+'](../../'+im['path']+')','',im['caption'],'','来源：['+im['source_id']+']('+sources[im['source_id']]['url']+')','']
  lines+=['### 该章原文来源','']
  for sid in r['source_ids']:
   s=sources[sid];lines+=['- ['+sid+'｜'+s['title']+']('+s['url']+') · '+s['access']+'。'+s['note']]
  lines+=['']
lines+=['# 全文审核状态','','全部60章已有草稿，但核心原文、补充材料、数据提取、可读性与页面交互审核尚未全部完成。字数达标不能替代这些工作。','']
lines+=['# 尚未起草的章节',''] if any(ch['id'] not in p['drafted_record_ids'] for part in p['parts'] for ch in part['chapters']) else []
for part in p['parts']:
 missing=[ch['title'] for ch in part['chapters'] if ch['id'] not in p['drafted_record_ids']]
 if missing:lines+=['## '+part['title'],'']+['- '+name for name in missing]+['']
(root/'research-programs/alzheimer/DRAFT.md').write_text('\n'.join(lines))
