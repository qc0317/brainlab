# -*- coding: utf-8 -*-
"""Export the authored research and licensed figures; exclude original corpus."""
import json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
db=json.loads((ROOT/'data/knowledge.json').read_text());program=json.loads((ROOT/'data/alzheimer/program.json').read_text());records=[r for r in db['records'] if r.get('research_program')==program['id']]
files=['research-programs/alzheimer/DRAFT.md','research-programs/alzheimer/PROTOCOL.md','research-programs/alzheimer/TRIALS.md','data/alzheimer/program.json','data/alzheimer/word-count.json','data/alzheimer/trial-extractions.json','data/alzheimer/lampit-reanalysis.json','scripts/reproduce_lampit.py']
for r in records:
 for im in ([r['image']] if r.get('image') else [])+r.get('research_figures',[]):
  assert 'CC BY' in im['caption'], 'Figure permission must be explicit for this bundle'
  files.append(im['path'])
files=sorted(set(files));dest=ROOT/'downloads/alzheimer-research.zip';dest.parent.mkdir(exist_ok=True)
readme='BrainLab个人研究包\n打开 research-programs/alzheimer/DRAFT.md 阅读正文；图片使用相对路径，解压时请保留目录。\n结构化对照记录位于 data/alzheimer/trial-extractions.json。\n指定领域复算：data/alzheimer/lampit-reanalysis.json 保存输入/方法/结果；可运行 python3 scripts/reproduce_lampit.py 核算。仅用标准库，不改变输入。\n此包为审核中的研究草稿，数量达标不表示科学审核完成。\n原论文入口保留在正文中；图注记录来源、许可及裁剪。\n'
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,data in [('README.txt',readme.encode())]+[(name,(ROOT/name).read_bytes()) for name in files]:
  info=zipfile.ZipInfo(name,(2026,10,10,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
with zipfile.ZipFile(dest) as z:
 assert z.testzip() is None
 for name in files:assert z.read(name)==(ROOT/name).read_bytes()
print('Verified bundle:',len(files),'files;',dest.stat().st_size,'bytes')
