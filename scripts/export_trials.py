# -*- coding: utf-8 -*-
"""Generate the downloadable research comparison from canonical extracts."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
x=json.loads((ROOT/'data/alzheimer/trial-extractions.json').read_text())
def cell(v):return str(v).replace('|','\\|').replace('\n',' ')
lines=['# 核心研究对照表','','由结构化提取数据自动生成；当前 '+str(len(x['studies']))+' 条记录，均为部分提取，完整方法审核仍在进行。','','同队列的不同随访不是独立重复验证；综述与原试验可能重叠。直接训练、综合方案与背景干预分别阅读。']
for role,label in x['intervention_roles'].items():
 lines+=['','## '+label,'','|研究|人群与对照|实际终点|效应|限制与待核|','|---|---|---|---|---|']
 for s in x['studies']:
  if s['intervention_role']!=role:continue
  lines.append('|['+s['id']+']('+s['source_url']+')|'+cell(s['population']+'；'+s['comparator'])+'|'+cell(s['outcome'])+'|'+cell(s['effect_summary'])+'|'+cell(s['limitations_and_pending'])+'|')
lines+=['','## 逐项效应','','|研究与比较|终点|效应|95%区间|单位|P值|原文位置与说明|','|---|---|---|---|---|---|---|']
for s in x['studies']:
 for e in s.get('effects',[]):lines.append('|'+cell(s['id']+'：'+e['contrast'])+'|'+cell(e['endpoint'])+'|'+cell(e['measure']+' '+str(e['estimate']))+'|'+str(e['ci_lower'])+' 至 '+str(e['ci_upper'])+'|'+cell(e['unit'])+'|'+('未录入' if e['p_value'] is None else str(e['p_value']))+'|'+cell(e['source_location']+'；'+e['note'])+'|')
lines+=['','## 其他原文统计','','没有完整效应量与区间的比较不以零值补齐。']
for s in x['studies']:
 for st in s.get('statistics',[]):lines.append('- '+cell(s['id']+'：'+st['contrast']+'；'+st['endpoint']+'；'+st['test']+'='+('未报告统计量' if st['value'] is None else str(st['value']))+'；自由度'+str(st.get('df',[]))+'；P='+str(st['p_value'])+'；'+st['source_location']))
 if s.get('multiplicity_note'):lines.append('- '+cell(s['id']+'：'+s['multiplicity_note']))
lines+=['','## 原文分母、模型与差异','']
for study in x['studies']:
 if study.get('event_counts'):
  ev=study['event_counts'];lines+=['### '+study['id']+'｜事件记录','',ev['source_location'],'','|群体|事件数|人数|','|---|---|---|']+['|'+cell(e['label'])+'|'+str(e['events'])+'|'+str(e['participants'])+'|' for e in ev['groups']]+['',ev['note'],'']
 if study.get('model_details'):
  m=study['model_details'];lines+=['模型：'+m['model'],'','调整变量：'+', '.join(m['adjustment_covariates']),'',m['within_arm_booster'],'',m['pending'],'']
 for d in study.get('discrepancies',[]):lines+=['原文差异：'+d['source_location'],'','文字：'+d['text_label']+'；表未调整：'+d['table_unadjusted']+'；表调整：'+d['table_adjusted'],'',d['resolution'],'']
 if study.get('effect_definition'):
  e=study['effect_definition'];lines+=['### '+study['id']+'｜效应定义','',e['numerator'],'',e['denominator'],'',e['source_location']+'；'+e['ci_status'],'']
lines+=['','[下载结构化JSON](../../data/alzheimer/trial-extractions.json)']
(ROOT/'research-programs/alzheimer/TRIALS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
