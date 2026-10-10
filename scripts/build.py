# -*- coding: utf-8 -*-
"""Build BrainLab's static knowledge base from normalized JSON (stdlib only)."""
import json,html,posixpath,hashlib,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'data/alzheimer/program.json').exists():subprocess.run([sys.executable,str(ROOT/'scripts/count_research.py')],check=True)
for export_script in ['export_trials.py','export_draft.py','export_research_bundle.py']:
 subprocess.run([sys.executable,str(ROOT/'scripts'/export_script)],check=True)
DB=json.loads((ROOT/'data/knowledge.json').read_text(encoding='utf-8'))
ASSET_VERSIONS={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()[:12] for p in ['assets/style.css','assets/app.js']}
def asset_version(p):return ASSET_VERSIONS.get(p) or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()[:12]
R={r['id']:r for r in DB['records']};S={s['id']:s for s in DB['sources']};C={c['id']:c for c in DB['collections']}
PROGRAM=json.loads((ROOT/'data/alzheimer/program.json').read_text()) if (ROOT/'data/alzheimer/program.json').exists() else None
WORD_COUNT=json.loads((ROOT/'data/alzheimer/word-count.json').read_text()) if (ROOT/'data/alzheimer/word-count.json').exists() else None
assert len(R)==len(DB['records']) and len(S)==len(DB['sources']), 'Duplicate stable IDs'
for r in R.values():
 assert r['collection'] in C
 for sid in r['source_ids']+[sid for s in r['sections'] for sid in s.get('source_ids',[])]:assert sid in S,(r['id'],sid)
 for t in r['relationships']:assert t['target_id'] in R,(r['id'],t)
 for d in r.get('demands',[]):assert d['ability_id'] in R and d['level'] in (0,1,2)

def esc(x):return html.escape(str(x),quote=True)
def path(id):return C[R[id]['collection']]['path']+'/'+id+'/index.html'
def rel(target,page):return posixpath.relpath(target,posixpath.dirname(page) or '.')
def href(target,page):return esc(rel(target,page))
def link(id,page,label=None):return '<a href="'+href(path(id),page)+'">'+esc(label or R[id]['title'])+'</a>'
def source_link(sid,page):return '<a href="'+href('sources/index.html',page)+'#'+esc(sid)+'">'+esc(sid)+'</a>'
def cite(ids,page):return '<div class="citations">依据：'+''.join(source_link(s,page) for s in ids)+'</div>' if ids else ''
def table(rows,cls=''):
 wide=len(rows[0])>=5 or (len(rows[0])>=4 and any(len(str(cell))>=45 for row in rows[1:] for cell in row))
 if wide:cls=(cls+" wide-table").strip()
 hint='<p class="table-hint">多列表格可左右滑动查看；键盘可聚焦表格后使用方向键。</p>' if wide else ""
 return hint+'<div class="table-wrap" tabindex="0" role="region" aria-label="数据表格，可横向浏览"><table class="'+cls+'"><thead><tr>'+''.join('<th scope="col">'+esc(x)+'</th>' for x in rows[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in row)+'</tr>' for row in rows[1:])+'</tbody></table></div>'
def card(r,page,label=None):
 return '<a class="card" href="'+href(path(r['id']),page)+'"><span class="tag">'+esc(label or r['status'])+'</span><h3>'+esc(r['title'])+'</h3><p>'+esc(r['summary'])+'</p><div class="meta">'+esc(C[r['collection']]['title'])+' · '+esc(r['id'])+'　↗</div></a>'
def cards(ids,page,cls=''):return '<div class="grid '+cls+'">'+''.join(card(R[i],page) for i in ids)+'</div>'
manifest=[]
def render(page,title,body,active='',description='BrainLab：阿尔茨海默病、认知游戏与产品体验研究知识库'):
 nav=[('alzheimer','阿尔茨海默病'),('duolingo','多邻国'),('keep','Keep'),('games','游戏'),('brain','脑网络'),('evidence','证据'),('design','设计')]
 head='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="'+esc(description)+'"><meta name="color-scheme" content="light"><title>'+esc(title)+'｜BrainLab</title><link rel="stylesheet" href="'+href('assets/style.css',page)+'?v='+asset_version('assets/style.css')+'">'+('<script defer src="'+href('assets/search-data.js',page)+'?v='+asset_version('assets/search-data.js')+'"></script>' if page=='search/index.html' else '')+'<script defer src="'+href('assets/app.js',page)+'?v='+asset_version('assets/app.js')+'"></script></head><body data-root="'+href('index.html',page)+'"><a class="skip" href="#main">跳至正文</a><header><div class="bar"><a class="brand" href="'+href('index.html',page)+'">BrainLab<span>研究知识库</span></a><nav class="topnav" aria-label="全站导航">'+''.join('<a'+(' class="active" aria-current="page"' if active==k else '')+' href="'+href(C[k]['path']+'/index.html',page)+'">'+v+'</a>' for k,v in nav)+'<a class="searchlink" href="'+href('search/index.html',page)+'">⌕ 检索</a></nav></div></header><main id="main">'
 foot='<footer class="pagefoot"><div>BrainLab · v'+DB['version']+' / '+DB['updated']+'<br>个人研究资料库 · 读取范围与结论条件详见各章</div><div><a href="'+href('sources/index.html',page)+'">来源与读取范围</a><a href="'+href('design/design-schema/index.html',page)+'">编辑与扩展</a><a href="https://github.com/qc0317/brainlab">GitHub ↗</a></div></footer></main></body></html>'
 file=ROOT/page;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(head+body+foot,encoding='utf-8');manifest.append(page)
def crumb(page,c=None,title=None):return '<nav class="crumb" aria-label="面包屑"><a href="'+href('index.html',page)+'">首页</a>'+(' / <a href="'+href(C[c]['path']+'/index.html',page)+'">'+esc(C[c]['title'])+'</a>' if c else '')+(' / <span>'+esc(title)+'</span>' if title else '')+'</nav>'
def intro(title,summary,tag='知识库',meta=''):
 return '<div class="pageintro"><div class="eyebrow">'+esc(tag)+'</div><h1>'+esc(title)+'</h1><p class="summary">'+esc(summary)+'</p>'+('<div class="meta-line">'+esc(meta)+'</div>' if meta else '')+'</div>'
# Landing: three independent research entries plus connected collections
p='index.html'
topics=''
for n,k in enumerate(['alzheimer','duolingo','keep'],1):
 count=sum(r['collection']==k for r in R.values());c=C[k]
 topics+='<a class="card topic" href="'+href(c['path']+'/index.html',p)+'"><div class="number">RESEARCH / 0'+str(n)+'</div><h3>'+esc(c['title'])+'</h3><p>'+esc(c['description'])+'</p><div class="meta">'+str(count)+' 个研究条目 · 进入专题 →</div></a>'
body='<div class="hero"><div><div class="eyebrow">Personal Research / Literature &amp; Data</div><h1>认知健康与脑部训练，<br>从文献与数据开始研究。</h1><p>个人非商业研究资料库。先读懂疾病，再审查训练预防的可能性；保留原文出处、中文解析、数据与相反证据，方便多端阅读和持续复盘。</p><div class="actions"><a class="btn" href="search/index.html">检索知识库</a><a class="btn secondary" href="games/matrix.html">游戏 × 能力矩阵</a></div><div class="stats"><div><b>'+str(len(R))+'</b><span>知识与设计条目</span></div><div><b>'+str(len(S))+'</b><span>可追溯来源</span></div><div><b>15 / 9</b><span>游戏 / 认知能力</span></div></div></div><aside class="chain"><strong>研究 → 设计 → 验证</strong><ol><li>病理与脑网络</li><li>可操作的认知过程</li><li>规则明确的游戏任务</li><li>持续参与的产品体验</li><li>独立结果与长期研究</li></ol><small>每一跳都保留依据、假设和缺口。</small></aside></div><div class="notice"><strong>研究阅读：</strong>任务学习、独立认知、生活功能、临床发病和病理指标分别记录。阿尔茨海默病十万字专题正在重建；全文审核和阶段性结论按章节标记。</div><section class="section"><div class="sectionhead"><h2>三项核心研究</h2><a href="sources/index.html">阅读来源说明 ↗</a></div><p class="sub">分别深入疾病机制与两种产品体验，再连接到可检验的游戏设计。</p><div class="grid">'+topics+'</div></section><section class="section"><h2>相互关联的知识结构</h2><div class="grid">'
for k in ['brain','abilities','games','evidence','design']:
 c=C[k];body+='<a class="card" href="'+c['path']+'/index.html"><span class="tag">'+str(sum(r['collection']==k for r in R.values()))+' 个条目</span><h3>'+c['title']+'</h3><p>'+c['description']+'</p><div class="meta">浏览目录 →</div></a>'
body+='<a class="card" href="sources/index.html"><span class="tag">来源层</span><h3>来源与证据范围</h3><p>记录原文、年份、证据类型、读取范围与限制，反向查看引用它的知识条目。</p><div class="meta">'+str(len(S))+' 项来源 →</div></a></div></section><section class="section"><h2>建议的阅读路径</h2>'+cards(['ad-foundations','ad-translation','design-outcomes'],p)+'<p class="sub" style="margin-top:24px">阿尔茨海默病专题正在按四条阅读主线重建，目标不少于十万字正文；已起草内容与待研究内容分开显示。<a href="archive/v0.3.html">查看单页历史版本</a></p></section>'
render(p,'认知健康与游戏设计',body)
# Hubs and level-three entries
for k,c in C.items():
 ids=[r['id'] for r in R.values() if r['collection']==k];p=c['path']+'/index.html'
 b=crumb(p,title=c['title'])+intro(c['title'],c['description'],'Research Collection',str(len(ids))+' 个条目 · 更新 '+DB['updated'])
 if k in ['duolingo','keep']:
  b+='<div class="notice hub-note"><strong>观察范围：</strong>'+('官方资料与 2022 历史界面；未实测当前原生 App。' if k=='duolingo' else '官方开发者说明与公开 Web 目录/详情；未实测原生跟练、AI、付费和推送流程。')+'“体验分析”与“设计建议”是分析模型，未声称已验证黏性效果。</div>'
 elif k=='alzheimer':b+='<div class="notice hub-note"><strong>专题重建：</strong>这是一项正在推进的个人文献研究。先读已起草的概念与证据，再查看规划章节；新版正文按实际汉字计数；字数达标与科学、阅读和页面审核分别记录。</div>'
 elif k=='brain':b+='<div class="notice hub-note">这些关联为多系统教学映射；没有本项目的游戏脑成像证据。历史“一游戏、一脑区、可预防”的强推断已纠正。</div>'
 elif k=='games':b+='<div class="actions"><a class="btn" href="matrix.html">查看游戏 × 能力矩阵</a><a class="btn secondary" href="'+href('abilities/index.html',p)+'">认知能力目录</a></div><div class="notice hub-note">任务需求依据明确规则判断；不是疗效排行榜。黑白翻转、堆叠水果采用暂定规则；密室逃脱仍需指定作品与关卡。</div>'
 if k=='alzheimer' and PROGRAM:
  b+='<div class="research-progress"><div><span class="eyebrow">个人研究 · 重建进行中</span><h2>脑部训练对于预防阿尔茨海默病，可能有效吗？</h2><p>按疾病、原因与表现、脑部变化、训练证据四条主线阅读。假设需要检验，支持、无差异和反对证据均保留。</p></div><div class="progress-count"><b>'+format(WORD_COUNT['counted_han_chars'],',')+'</b><span> / 100,000 正文汉字</span><small>'+str(WORD_COUNT['drafted_chapters'])+' / '+str(WORD_COUNT['planned_chapters'])+' 章已起草 · 尚未完成</small></div></div>'
  b+='<div class="actions"><a class="btn" href="'+href(path('ad-foundations'),p)+'">先从“疾病是什么”开始</a><a class="btn secondary" href="'+href('research-programs/alzheimer/PROTOCOL.md',p)+'">研究方案与计数口径</a><a class="btn secondary" href="'+href('research-programs/alzheimer/DELIVERY-AUDIT.md',p)+'">交付审核与剩余工作</a><a class="btn secondary" href="'+href('research/alzheimer/trials/index.html',p)+'">核心研究对照表</a><a class="btn secondary" href="'+href('data/alzheimer/word-count.json',p)+'">查看实际字数</a><a class="btn secondary" href="'+href('research-programs/alzheimer/DRAFT.md',p)+'">下载当前正文</a><a class="btn secondary" href="'+href('downloads/alzheimer-research.zip',p)+'" download>下载离线研究包</a></div><nav class="reading-parts" aria-label="专题阅读主线">'+''.join('<a href="#part-'+x['id']+'">'+esc(x['title'])+'</a>' for x in PROGRAM['parts'])+'</nav>'
  b+='<section class="section"><h2>这一专题怎样展开</h2><p>'+esc(PROGRAM.get('reading_logic',''))+'</p><p>第3部分解释大脑变化与认知受影响的联系，第4部分据此检验训练可能性。机制基础与临床效应分别记录，并通过具体研究连接。</p></section>'
  written=set(PROGRAM['drafted_record_ids'])
  for part in PROGRAM['parts']:
   available=[ch['id'] for ch in part['chapters'] if ch['id'] in written and ch['id'] in R]
   planned=[ch for ch in part['chapters'] if ch['id'] not in written]
   b+='<section class="section" id="part-'+part['id']+'"><h2>'+esc(part['title'])+'</h2><p class="sub">'+esc(part['description'])+'</p><div class="notice"><strong>带着问题阅读：</strong>'+esc(part.get('reader_question',''))+'</div>'+cards(available,p,'two')
   if planned:b+='<details class="planned"><summary>后续章节 · '+str(len(planned))+' 章待撰写/重写</summary><ol>'+''.join('<li>'+esc(ch['title'])+' <span class="meta-line">尚未完成</span></li>' for ch in planned)+'</ol></details>'
   b+='<p class="sub">'+esc(part.get('next_bridge',''))+'</p></section>'
  legacy=[i for i in ids if i not in written]
  if legacy:b+='<section class="section"><h2>机制旧稿与研究线索</h2><p class="sub">保留用于继续扩展与复盘；这些旧条目尚未按新专题要求重写，不计入十万字正文。</p>'+cards(legacy,p)+'</section>'
 else:b+=cards(ids,p,'two' if k in ['duolingo','keep'] else '')
 render(p,c['title'],b,k,c['description'])
for r in R.values():
 p=path(r['id']);c=r['collection'];secs=r['sections']
 b=crumb(p,c,r['title'])+intro(r['title'],r['summary'],C[c]['title'],r['id']+' · '+r['status']+' · 更新 '+r['reviewed'])
 if r.get('research_program') and PROGRAM:
  part=next(x for x in PROGRAM['parts'] if x['id']==r['part'])
  ch_count=next((x['han_chars'] for x in WORD_COUNT['chapters'] if x['id']==r['id']),0)
  b+='<div class="reader-meta"><strong>'+esc(part['title'])+'</strong><span>正文 '+format(ch_count,',')+' 汉字 · 起草完成，审核进行中</span></div><details class="learning"><summary>本节帮助理解什么</summary><ul>'+''.join('<li>'+esc(x)+'</li>' for x in r.get('learning_objectives',[]))+'</ul></details>'
 if r.get('basis'):b+='<div class="notice hub-note">资料与观察依据：'+esc(r['basis'])+'</div>'

 if r.get('needs_clarification'):b+='<div class="notice hub-note"><strong>规则待确认：</strong>历史名称或类型不足以唯一确定玩法。本页规则是工作定义，后续须指定版本。</div>'
 b+='<div class="layout"><article class="content">'
 for i,s in enumerate(secs):
  b+='<section id="s'+str(i)+'"><h2>'+esc(s['title'])+'</h2>'+''.join('<p>'+esc(t)+'</p>' for t in s.get('text',[]))
  if s.get('items'):b+='<ul>'+''.join('<li>'+esc(x)+'</li>' for x in s['items'])+'</ul>'
  if s.get('table'):b+=table(s['table'])
  b+=cite(s.get('source_ids',[]),p)+'</section>'
 if r.get('demands'):
  b+='<section id="demands"><h2>游戏 × 能力需求</h2><p class="sub">● 主要需求　◐ 次要/条件性需求　— 未突出；依据规则分析，非疗效强度。</p><div class="labelrow">'+''.join(link(d['ability_id'],p,('● ' if d['level']==2 else '◐ ' if d['level']==1 else '— ')+R[d['ability_id']]['title']) for d in r['demands'])+'</div></section>'
 if r.get('image'):
  im=r['image'];b+='<section id="interface"><h2>'+esc(im.get('title','界面样本与观察记录'))+'</h2><figure class="research-image"><img loading="lazy" width="'+str(im.get('width',1280))+'" height="'+str(im.get('height',720))+'" src="'+href(im['path'],p)+'" alt="'+esc(im['caption'])+'"><figcaption>'+esc(im['caption'])+' '+source_link(im['source_id'],p)+'</figcaption></figure></section>'
 for fi,im in enumerate(r.get('research_figures',[])):
  assert im['source_id'] in S and im['license_url']
  b+='<section id="figure-'+str(fi)+'"><h2>'+esc(im['title'])+'</h2><figure class="research-image"><a href="'+href(im['path'],p)+'"><img loading="lazy" width="'+str(im['width'])+'" height="'+str(im['height'])+'" src="'+href(im['path'],p)+'" alt="'+esc(im['caption'])+'"></a><figcaption>'+esc(im['caption'])+' '+source_link(im['source_id'],p)+' · <a href="'+esc(im['license_url'])+'">使用许可</a></figcaption></figure></section>'
 used_sources=list(dict.fromkeys(r['source_ids']+[sid for section in secs for sid in section.get('source_ids',[])]+[im['source_id'] for im in r.get('research_figures',[])]+([r['image']['source_id']] if r.get('image') else [])))
 if used_sources:
  b+='<section id="refs"><h2>引用来源与读取范围</h2><ul class="refs">'
  for sid in used_sources:
   s=S[sid];b+='<li>'+source_link(sid,p)+' · <a href="'+esc(s['url'])+'" target="_blank" rel="noopener">'+esc(s['title'])+' ↗</a><small>'+esc(str(s['year'])+' · '+s['kind']+' · '+s['access'])+('；'+esc(s['note']) if s['note'] else '')+('；许可：'+esc(s['license']) if s.get('license') else '')+'</small></li>'
  b+='</ul></section>'
 b+='</article><aside class="toc"><strong>本页目录</strong><nav aria-label="条目章节">'+''.join('<a href="#s'+str(i)+'">'+esc(s['title'])+'</a>' for i,s in enumerate(secs))+('<a href="#interface">'+esc(r['image'].get('title','界面观察'))+'</a>' if r.get('image') else '')+''.join('<a href="#figure-'+str(fi)+'">'+esc(im['title'])+'</a>' for fi,im in enumerate(r.get('research_figures',[])))+('<a href="#refs">来源与范围</a>' if used_sources else '')+'<a href="#related">关联条目</a></nav><div class="aside-note"><span class="tag">'+esc(r['status'])+'</span><small>关联 ≠ 因果或疗效。<br>证据更新时保留版本、适用条件和相反结果。</small><p>'+link('design-schema',p,'如何编辑与扩展 →')+'</p></div></aside></div>'
 b+='<section class="relations" id="related"><h2>继续沿关联阅读</h2><div class="grid">'+''.join(card(R[t['target_id']],p,t['label']) for t in r['relationships'])+'</div>'
 backlinks=[x['id'] for x in R.values() if any(t['target_id']==r['id'] for t in x['relationships'])]
 if backlinks:b+='<h3 style="margin-top:26px">哪些条目关联本页</h3><div class="backlinks">'+''.join(link(t,p) for t in backlinks)+'</div>'
 b+='</section>';render(p,r['title'],b,c,r['summary'])
# Source catalogue and reverse citations
p='sources/index.html';b=crumb(p,title='来源')+intro('来源与读取范围','先看证据类型、适用人群和读取范围，再决定它能支持何种结论。','Evidence Provenance',str(len(S))+' 项来源 · 访问基线 2026-10-09')+'<div class="notice">本版采用机构、论文原文和官方产品资料。部分只有摘要/概要，已逐项标记；没有把未阅读全文当作已完成系统综述。原生产品未实测的能力与流程不作为已观察事实。来源年份可能为访问年份，相关说明见备注。</div>'
for sid,s in S.items():
 used=[r['id'] for r in R.values() if sid in set(r['source_ids']+[v for a in r['sections'] for v in a.get('source_ids',[])])]
 b+='<section class="source-item" id="'+sid+'"><span class="tag">'+sid+' · '+esc(s['kind'])+'</span><h2><a href="'+esc(s['url'])+'" target="_blank" rel="noopener">'+esc(s['title'])+' ↗</a></h2><div class="meta-line">'+str(s['year'])+' · 读取范围：'+esc(s['access'])+' · 复核 '+s['reviewed']+'</div>'+('<p>'+esc(s['note'])+'</p>' if s['note'] else '')+('<p>许可：'+esc(s['license'])+'</p>' if s.get('license') else '')+('<p>同一试验：'+esc(s['trial_id'])+'</p>' if s.get('trial_id') else '')+'<div class="backlinks">被引用：'+''.join(link(i,p) for i in used)+'</div></section>'
render(p,'来源与证据范围',b)
# Matrix, no unsupported evidence scores
p='games/matrix.html';ab=[r for r in R.values() if r['collection']=='abilities'];games=[r for r in R.values() if r['collection']=='games']
b=crumb(p,'games','需求矩阵')+intro('游戏 × 认知能力矩阵','任务需求的工作判断，帮助选任务和提出研究问题；不是疗效、脑区激活或预防效果矩阵。','Task Demands','15 个游戏 · 9 类能力 · 规则基线 v1')+'<div class="legend"><span>● 主要需求</span><span>◐ 次要/条件性需求</span><span>— 默认规则下未突出</span></div><div class="searchbox" style="margin-top:20px"><div class="filters"><div class="field"><label for="matrix-q">游戏名称</label><input id="matrix-q" type="search" placeholder="例如：数独"></div><div class="field"><label for="matrix-ability">只看主要涉及的能力</label><select id="matrix-ability"><option value="">全部能力</option>'+''.join('<option value="'+a['id']+'">'+esc(a['title'])+'</option>' for a in ab)+'</select></div><button id="matrix-reset" type="button">重置</button></div><div id="matrix-count" class="resultmeta" aria-live="polite">15 个游戏</div></div><div class="table-wrap"><table class="matrix"><thead><tr><th scope="col">游戏 / 规则</th>'+''.join('<th scope="col">'+link(a['id'],p)+'</th>' for a in ab)+'</tr></thead><tbody>'
for g in games:
 b+='<tr data-name="'+esc(g['title'])+'" data-main="'+esc(' '.join(d['ability_id'] for d in g['demands'] if d['level']==2))+'"><th scope="row">'+link(g['id'],p)+(' <span class="tag warn">暂定</span>' if g.get('needs_clarification') else '')+'</th>'+''.join('<td class="l'+str(d['level'])+'" aria-label="'+esc(R[d['ability_id']]['title'])+'：'+['未突出','次要或条件性','主要'][d['level']]+'">'+['—','◐','●'][d['level']]+'</td>' for d in g['demands'])+'</tr>'
b+='</tbody></table></div><p id="matrix-empty" class="empty" hidden>没有匹配的游戏，请调整条件。</p><div class="notice"><strong>如何阅读：</strong>同名游戏因规则、限时、熟练程度和提示不同，会调用不同过程。等级 0 不表示完全没有该过程。历史“神经网络游戏”“四合一连连看”等名称不足以确定独立玩法，待补充规则后再纳入。逐游戏迁移证据审查尚未完成。</div><div class="actions"><a class="btn secondary" href="'+href('design/design-translation/index.html',p)+'">从矩阵进入产品设计 →</a></div>'
render(p,'游戏能力需求矩阵',b,'games')
# Structured trial browser: data remains independently downloadable.
p='research/alzheimer/trials/index.html'
EXTRACTS=json.loads((ROOT/'data/alzheimer/trial-extractions.json').read_text())
b=crumb(p,title='核心训练研究对照')+intro('核心训练研究对照','逐项查看人群、对照和实际终点，再回到原文与详细解读。当前为第一批部分提取，完整数据与方法审核仍在进行。','Literature Comparison')
b+='<div class="notice">同一试验的不同随访不是独立重复验证；综述与原始试验可能重叠。认知、任务、脑电及临床发生分别记录。</div><div class="actions"><a class="btn secondary" href="'+href('data/alzheimer/trial-extractions.json',p)+'" download>下载结构化数据 JSON</a><a class="btn secondary" href="'+href('research-programs/alzheimer/TRIALS.md',p)+'" download>下载研究对照表</a></div>'
b+='<nav class="reading-parts" aria-label="按研究跳转">'+''.join('<a href="#trial-'+esc(x['id'])+'">'+esc(x['id'])+'</a>' for x in EXTRACTS['studies'])+'</nav>'
b+='<div class="grid">'
for role,label in EXTRACTS['intervention_roles'].items():
 group=[x for x in EXTRACTS['studies'] if x['intervention_role']==role]
 b+='<div class="card"><h2>'+esc(label)+'</h2><p>'+('综合方案不能拆成游戏独立疗效。' if role=='multidomain' else '帮助理解背景与认知收益，不能当作直接游戏预防试验。' if role=='background' else '检查训练任务、独立认知与长期临床结果。')+'</p><ul>'+''.join('<li><a href="#trial-'+esc(x['id'])+'">'+esc(S[x['source_id']]['title'])+'</a></li>' for x in group)+'</ul></div>'
b+='</div>'
for x in EXTRACTS['studies']:
 assert x['source_id'] in S and x['record_id'] in R
 b+='<section class="section" id="trial-'+esc(x['id'])+'"><span class="tag">部分提取 · 审核中</span><h2>'+esc(S[x['source_id']]['title'])+'</h2>'
 b+=table([['提取字段','当前记录'],['人群',x['population']],['训练或干预',x['intervention']],['比较对象',x['comparator']],['实际终点',x['outcome']],['结果',x['effect_summary']],['同队列标识',x['cohort_key']],['读取范围',x['access_scope']],['限制与待核',x['limitations_and_pending']]])
 if x.get('effects'):
  b+='<h3>逐项效应与终点</h3>'+table([['比较','终点','效应值','置信区间','单位','原文位置与说明']]+[[e['contrast'],e['endpoint'],e['measure']+' '+str(e['estimate']),format(e['ci_level'],'.0%')+'：'+str(e['ci_lower'])+' 至 '+str(e['ci_upper']),e['unit'],e['source_location']+'；'+e['note']] for e in x['effects']])
 else:b+='<p class="sub">'+esc(x.get('numeric_missing_reason','完整数值待提取'))+'</p>'
 if x.get('statistics'):
  b+='<h3>原文统计检验</h3>'+table([['比较','终点','统计量','自由度','P值','位置']]+[[e['contrast'],e['endpoint'],e['test']+' '+('未报告统计量' if e['value'] is None else str(e['value'])),str(e.get('df',[])),e.get('p_relation','=')+str(e['p_value']),e['source_location']] for e in x['statistics']])
 if x.get('multiplicity_note'):b+='<p>'+esc(x['multiplicity_note'])+'</p>'
 if x.get('event_counts'):
  ev=x['event_counts'];b+='<h3>事件数与分析分母</h3>'+table([['群体','事件数','人数']]+[[e['label'],str(e['events']),str(e['participants'])] for e in ev['groups']])+'<p>'+esc(ev['note'])+'</p><p class="sub">'+esc(ev['source_location'])+'</p>'
 if x.get('model_details'):
  model=x['model_details'];b+='<details class="learning"><summary>模型与调整变量</summary><p>'+esc(model['model'])+'</p><p>'+esc('、'.join(model['adjustment_covariates']))+'</p><p>'+esc(model['within_arm_booster'])+'</p><p>'+esc(model['pending'])+'</p></details>'
 if x.get('discrepancies'):
  b+='<h3>原文差异 · 尚未裁决</h3>'+table([['位置','文字标签','表格未调整','表格调整','处理']]+[[e['source_location'],e['text_label'],e['table_unadjusted'],e['table_adjusted'],e['resolution']] for e in x['discrepancies']])
 if x.get('reanalysis_artifact'):
  b+='<p><a href="'+href(x['reanalysis_artifact'],p)+'">查看本库独立复算的输入、方法和结果 JSON</a> · <a href="'+href('scripts/reproduce_lampit.py',p)+'">下载指定复算脚本</a></p><p class="sub">复算范围与原文差异详见正文；独立复算不代表出版商正式更正。</p>'
 if x.get('analysis_flow'):
  f=x['analysis_flow'];labels={'experimental_1':'实验1','experimental_2':'实验2','control':'活动对照'}
  b+='<h3>登记与纳入分析</h3>'+table([['阶段','人数'],['初始登记',str(f['registered'])],['纳入分析',str(f['included_analysis'])]]+[[labels.get(k,k),str(v)] for k,v in f['analysis_groups'].items()])+'<p>'+esc(f['inclusion'])+'</p><p>'+esc(f['note'])+'</p><p class="sub">'+esc(f['source_location'])+'</p>'
 if x.get('participant_flow'):
  f=x['participant_flow'];b+='<h3>筛选、随机与分析人数</h3>'+table([['阶段','人数'],['筛选',str(f['screened'])],['随机分配',str(f['randomized'])]])
  labels={'intervention':'综合干预','control':'对照','hearing':'听力干预','education':'健康教育'}
  b+=table([['组别','随机人数','修正意向治疗人数']]+[[labels.get(g['label'],g['label']),str(g['randomized']),str(g.get('modified_itt','未录入'))] for g in f['groups']])
  if f.get('modified_itt_definition'):b+='<p>分析纳入条件：'+esc(f['modified_itt_definition'])+'</p>'
  b+='<p class="sub">'+esc(f['source_location'])+'；不同阶段分母不能混用。</p>'
 if x.get('safety'):
  f=x['safety'];b+='<h3>安全性记录 · 人数</h3>'+table([['记录','干预组','对照组'],['至少一次不良事件',str(f['counts']['intervention']),str(f['counts']['control'])],['肌肉骨骼疼痛',str(f['musculoskeletal_pain']['intervention']),str(f['musculoskeletal_pain']['control'])]])+'<p>'+esc(f['note'])+'</p><p class="sub">'+esc(f['source_location'])+'</p>'
 if x.get('individual_change'):
  f=x['individual_change'];labels={'photo':'摄影','quilt':'拼布','dual':'双项目','social':'社交','placebo':'安慰活动'}
  b+='<h3>个体变化阈值 · '+esc(f['endpoint'])+'</h3><p>'+esc(f['threshold'])+'</p>'+table([['活动','超过阈值比例']]+[[labels.get(k,k),format(v,'.0%')] for k,v in f['proportions'].items()])+'<p>'+esc(f['limitations'])+'</p><p class="sub">'+esc(f['source_location'])+'</p>'
 if x.get('historical_protocol'):
  f=x['historical_protocol'];b+='<h3>历史第一次加强训练方案</h3>'+table([['字段','方案记录'],['时间',f['first_booster_timing']],['随机子样本比例',format(f['random_subsample_fraction'],'.0%')],['初始出席资格',format(f['initial_attendance_eligibility_fraction'],'.0%')],['课程',str(f['planned_sessions'])+'次，每次'+str(f['minutes_per_session'])+'分钟，'+str(f['delivery_weeks'])+'周内']])+'<p>'+esc(f['interpretation'])+'</p><p>'+esc(f['pending'])+'</p><p class="sub">'+esc(f['source_location'])+'</p>'
 if x.get('effect_definition'):
  ed=x['effect_definition'];b+='<details class="learning"><summary>效应量计算口径</summary><p>'+esc(ed['numerator'])+'</p><p>'+esc(ed['denominator'])+'</p><p>'+esc(ed['source_location']+'；'+ed['ci_status'])+'</p></details>'
 b+='<div class="actions"><a class="btn" href="'+href(path(x['record_id']),p)+'">阅读详细章节</a><a class="btn secondary" href="'+esc(x['source_url'])+'" target="_blank" rel="noopener">查看原始文献 ↗</a></div>'+cite([x['source_id']],p)+'</section>'
render(p,'核心训练研究对照',b,'alzheimer')

# Search index embeds all authored text for offline browsing; URLs relative to root.
search=[dict(id=r['id'],title=r['title'],summary=r['summary'],collection=r['collection'],category=C[r['collection']]['title'],status=r['status'],url=path(r['id']),text=' '.join([r['title'],r['summary'],*r.get('aliases',[]),json.dumps(r['sections'],ensure_ascii=False)])) for r in R.values()]
search += [dict(id=s['id'],title=s['title'],summary=s['note'] or s['access'],collection='sources',category='来源',status=s['kind'],url='sources/index.html#'+s['id'],text=' '.join(map(str,s.values()))) for s in S.values()]
search += [dict(id='trial-'+x['id'],title=S[x['source_id']]['title']+'｜研究对照',summary=x['effect_summary'],collection='alzheimer',category='研究数据',status=EXTRACTS['intervention_roles'][x['intervention_role']],url='research/alzheimer/trials/index.html#trial-'+x['id'],text=json.dumps(x,ensure_ascii=False)) for x in EXTRACTS['studies']]
(ROOT/'data/search-index.json').write_text(json.dumps(search,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'assets/search-data.js').write_text('window.BRAINLAB_INDEX='+json.dumps(search,ensure_ascii=False).replace('<','\\u003c')+';',encoding='utf-8')
p='search/index.html';b=crumb(p,title='检索')+intro('检索整个知识库','搜索正文、来源与历史别名，按专题和证据状态筛选。','Knowledge Search')+'<form id="search-form" class="searchbox"><div class="filters"><div class="field wide"><label for="query">关键词</label><input id="query" type="search" placeholder="海马、迁移、暂停、阿兹海默…" autocomplete="off"></div><div class="field"><label for="category">专题</label><select id="category"><option value="">全部专题</option>'+''.join('<option value="'+k+'">'+esc(c['title'])+'</option>' for k,c in C.items())+'<option value="sources">来源</option></select></div><div class="field"><label for="status">条目状态 / 证据类型</label><select id="status"><option value="">全部状态</option></select></div><button type="submit">检索</button><button id="reset" type="button">重置</button></div></form><p id="result-count" class="resultmeta" aria-live="polite"></p><div id="results" class="results"></div><noscript><p class="nojs">检索需要 JavaScript。可以通过首页各专题目录浏览全部内容。</p></noscript>'
render(p,'全站检索',b)
render('404.html','页面未找到',intro('这个页面没有找到','可以返回知识库首页，或通过检索寻找对应条目。')+'<div class="actions"><a class="btn" href="/brainlab/">返回首页</a><a class="btn secondary" href="/brainlab/search/">检索知识库</a></div>')
(ROOT/'.nojekyll').touch()
(ROOT/'data/build-manifest.json').write_text(json.dumps({'version':DB['version'],'pages':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Built {len(manifest)} pages, {len(R)} records, {len(S)} sources')
