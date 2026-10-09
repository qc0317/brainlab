# -*- coding: utf-8 -*-
"""Build BrainLab's static knowledge base from normalized JSON (stdlib only)."""
import json,html,posixpath
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DB=json.loads((ROOT/'data/knowledge.json').read_text(encoding='utf-8'))
R={r['id']:r for r in DB['records']};S={s['id']:s for s in DB['sources']};C={c['id']:c for c in DB['collections']}
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
 return '<div class="table-wrap"><table class="'+cls+'"><thead><tr>'+''.join('<th scope="col">'+esc(x)+'</th>' for x in rows[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in row)+'</tr>' for row in rows[1:])+'</tbody></table></div>'
def card(r,page,label=None):
 return '<a class="card" href="'+href(path(r['id']),page)+'"><span class="tag">'+esc(label or r['status'])+'</span><h3>'+esc(r['title'])+'</h3><p>'+esc(r['summary'])+'</p><div class="meta">'+esc(C[r['collection']]['title'])+' · '+esc(r['id'])+'　↗</div></a>'
def cards(ids,page,cls=''):return '<div class="grid '+cls+'">'+''.join(card(R[i],page) for i in ids)+'</div>'
manifest=[]
def render(page,title,body,active='',description='BrainLab：阿尔茨海默病、认知游戏与产品体验研究知识库'):
 nav=[('alzheimer','阿尔茨海默病'),('duolingo','多邻国'),('keep','Keep'),('games','游戏'),('brain','脑网络'),('evidence','证据'),('design','设计')]
 head='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="'+esc(description)+'"><meta name="color-scheme" content="light"><title>'+esc(title)+'｜BrainLab</title><link rel="stylesheet" href="'+href('assets/style.css',page)+'"><script defer src="'+href('assets/search-data.js',page)+'"></script><script defer src="'+href('assets/app.js',page)+'"></script></head><body data-root="'+href('index.html',page)+'"><a class="skip" href="#main">跳至正文</a><header><div class="bar"><a class="brand" href="'+href('index.html',page)+'">BrainLab<span>研究知识库</span></a><nav class="topnav" aria-label="全站导航">'+''.join('<a'+(' class="active" aria-current="page"' if active==k else '')+' href="'+href(C[k]['path']+'/index.html',page)+'">'+v+'</a>' for k,v in nav)+'<a class="searchlink" href="'+href('search/index.html',page)+'">⌕ 检索</a></nav></div></header><main id="main">'
 foot='<footer class="pagefoot"><div>BrainLab · v'+DB['version']+' / '+DB['updated']+'<br>研究与设计基线 · 产品疗效尚未验证</div><div><a href="'+href('sources/index.html',page)+'">来源与读取范围</a><a href="'+href('design/design-schema/index.html',page)+'">编辑与扩展</a><a href="https://github.com/qc0317/brainlab">GitHub ↗</a></div></footer></main></body></html>'
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
body='<div class="hero"><div><div class="eyebrow">Cognitive Health / Research Library · 1.0</div><h1>从脑科学到日常练习，<br>把设计建立在证据之上。</h1><p>面向认知基本正常的中老年人，以有趣、可持续的日常游戏支持认知健康。这里汇集疾病机制、任务分析与体验研究，逐步检验功能维持与风险降低的可能性。</p><div class="actions"><a class="btn" href="search/index.html">检索知识库</a><a class="btn secondary" href="games/matrix.html">游戏 × 能力矩阵</a></div><div class="stats"><div><b>'+str(len(R))+'</b><span>知识与设计条目</span></div><div><b>'+str(len(S))+'</b><span>可追溯来源</span></div><div><b>15 / 9</b><span>游戏 / 认知能力</span></div></div></div><aside class="chain"><strong>研究 → 设计 → 验证</strong><ol><li>病理与脑网络</li><li>可操作的认知过程</li><li>规则明确的游戏任务</li><li>持续参与的产品体验</li><li>独立结果与长期研究</li></ol><small>每一跳都保留依据、假设和缺口。</small></aside></div><div class="notice"><strong>科学边界：</strong>参与不等于已证实的迁移训练，任务进步不等于疾病预防。当前没有验证 BrainLab 的认知或预防疗效。脑区关联用于研究导航，不是个人脑区诊断。</div><section class="section"><div class="sectionhead"><h2>三项核心研究</h2><a href="sources/index.html">阅读来源说明 ↗</a></div><p class="sub">分别深入疾病机制与两种产品体验，再连接到可检验的游戏设计。</p><div class="grid">'+topics+'</div></section><section class="section"><h2>相互关联的知识结构</h2><div class="grid">'
for k in ['brain','abilities','games','evidence','design']:
 c=C[k];body+='<a class="card" href="'+c['path']+'/index.html"><span class="tag">'+str(sum(r['collection']==k for r in R.values()))+' 个条目</span><h3>'+c['title']+'</h3><p>'+c['description']+'</p><div class="meta">浏览目录 →</div></a>'
body+='<a class="card" href="sources/index.html"><span class="tag">来源层</span><h3>来源与证据范围</h3><p>记录原文、年份、证据类型、读取范围与限制，反向查看引用它的知识条目。</p><div class="meta">'+str(len(S))+' 项来源 →</div></a></div></section><section class="section"><h2>建议的阅读路径</h2>'+cards(['ad-foundations','ad-translation','design-outcomes'],p)+'<p class="sub" style="margin-top:24px">本轮完成知识库基线。下一阶段优先做少量会话原型与目标用户实测；专题研究继续补全文、偏倚评估及专家审查。<a href="archive/v0.3.html">查看单页历史版本</a></p></section>'
render(p,'认知健康与游戏设计',body)
# Hubs and level-three entries
for k,c in C.items():
 ids=[r['id'] for r in R.values() if r['collection']==k];p=c['path']+'/index.html'
 b=crumb(p,title=c['title'])+intro(c['title'],c['description'],'Research Collection',str(len(ids))+' 个条目 · 更新 '+DB['updated'])
 if k in ['duolingo','keep']:
  b+='<div class="notice hub-note"><strong>观察范围：</strong>'+('官方资料与 2022 历史界面；未实测当前原生 App。' if k=='duolingo' else '官方开发者说明与公开 Web 目录/详情；未实测原生跟练、AI、付费和推送流程。')+'“体验分析”与“设计建议”是分析模型，未声称已验证黏性效果。</div>'
 elif k=='alzheimer':b+='<div class="notice hub-note"><strong>专题研究基线：</strong>深入机制、方法与设计转译，属于叙述性研究草案；尚未完成系统检索、所有全文提取或专家审稿。痴呆总体证据保留原终点，不改写为 AD 特异性疗效。</div>'
 elif k=='brain':b+='<div class="notice hub-note">这些关联为多系统教学映射；没有本项目的游戏脑成像证据。历史“一游戏、一脑区、可预防”的强推断已纠正。</div>'
 elif k=='games':b+='<div class="actions"><a class="btn" href="matrix.html">查看游戏 × 能力矩阵</a><a class="btn secondary" href="'+href('abilities/index.html',p)+'">认知能力目录</a></div><div class="notice hub-note">任务需求依据明确规则判断；不是疗效排行榜。黑白翻转、堆叠水果采用暂定规则；密室逃脱仍需指定作品与关卡。</div>'
 b+=cards(ids,p,'two' if k in ['duolingo','keep'] else '')
 render(p,c['title'],b,k,c['description'])
for r in R.values():
 p=path(r['id']);c=r['collection'];secs=r['sections']
 b=crumb(p,c,r['title'])+intro(r['title'],r['summary'],C[c]['title'],r['id']+' · '+r['status']+' · 更新 '+r['reviewed'])
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
  im=r['image'];b+='<section id="interface"><h2>界面样本与观察记录</h2><figure class="research-image"><img loading="lazy" width="1280" height="720" src="'+href(im['path'],p)+'" alt="'+esc(im['caption'])+'"><figcaption>'+esc(im['caption'])+' '+source_link(im['source_id'],p)+'</figcaption></figure></section>'
 if r['source_ids']:
  b+='<section id="refs"><h2>引用来源与读取范围</h2><ul class="refs">'
  for sid in r['source_ids']:
   s=S[sid];b+='<li>'+source_link(sid,p)+' · <a href="'+esc(s['url'])+'" target="_blank" rel="noopener">'+esc(s['title'])+' ↗</a><small>'+esc(str(s['year'])+' · '+s['kind']+' · '+s['access'])+('；'+esc(s['note']) if s['note'] else '')+'</small></li>'
  b+='</ul></section>'
 b+='</article><aside class="toc"><strong>本页目录</strong><nav aria-label="条目章节">'+''.join('<a href="#s'+str(i)+'">'+esc(s['title'])+'</a>' for i,s in enumerate(secs))+('<a href="#interface">界面观察</a>' if r.get('image') else '')+('<a href="#refs">来源与范围</a>' if r['source_ids'] else '')+'<a href="#related">关联条目</a></nav><div class="aside-note"><span class="tag">'+esc(r['status'])+'</span><small>关联 ≠ 因果或疗效。<br>证据更新时保留版本、适用条件和相反结果。</small><p>'+link('design-schema',p,'如何编辑与扩展 →')+'</p></div></aside></div>'
 b+='<section class="relations" id="related"><h2>继续沿关联阅读</h2><div class="grid">'+''.join(card(R[t['target_id']],p,t['label']) for t in r['relationships'])+'</div>'
 backlinks=[x['id'] for x in R.values() if any(t['target_id']==r['id'] for t in x['relationships'])]
 if backlinks:b+='<h3 style="margin-top:26px">哪些条目关联本页</h3><div class="backlinks">'+''.join(link(t,p) for t in backlinks)+'</div>'
 b+='</section>';render(p,r['title'],b,c,r['summary'])
# Source catalogue and reverse citations
p='sources/index.html';b=crumb(p,title='来源')+intro('来源与读取范围','先看证据类型、适用人群和读取范围，再决定它能支持何种结论。','Evidence Provenance',str(len(S))+' 项来源 · 访问基线 2026-10-09')+'<div class="notice">本版采用机构、论文原文和官方产品资料。部分只有摘要/概要，已逐项标记；没有把未阅读全文当作已完成系统综述。原生产品未实测的能力与流程不作为已观察事实。来源年份可能为访问年份，相关说明见备注。</div>'
for sid,s in S.items():
 used=[r['id'] for r in R.values() if sid in set(r['source_ids']+[v for a in r['sections'] for v in a.get('source_ids',[])])]
 b+='<section class="source-item" id="'+sid+'"><span class="tag">'+sid+' · '+esc(s['kind'])+'</span><h2><a href="'+esc(s['url'])+'" target="_blank" rel="noopener">'+esc(s['title'])+' ↗</a></h2><div class="meta-line">'+str(s['year'])+' · 读取范围：'+esc(s['access'])+' · 复核 '+s['reviewed']+'</div>'+('<p>'+esc(s['note'])+'</p>' if s['note'] else '')+'<div class="backlinks">被引用：'+''.join(link(i,p) for i in used)+'</div></section>'
render(p,'来源与证据范围',b)
# Matrix, no unsupported evidence scores
p='games/matrix.html';ab=[r for r in R.values() if r['collection']=='abilities'];games=[r for r in R.values() if r['collection']=='games']
b=crumb(p,'games','需求矩阵')+intro('游戏 × 认知能力矩阵','任务需求的工作判断，帮助选任务和提出研究问题；不是疗效、脑区激活或预防效果矩阵。','Task Demands','15 个游戏 · 9 类能力 · 规则基线 v1')+'<div class="legend"><span>● 主要需求</span><span>◐ 次要/条件性需求</span><span>— 默认规则下未突出</span></div><div class="searchbox" style="margin-top:20px"><div class="filters"><div class="field"><label for="matrix-q">游戏名称</label><input id="matrix-q" type="search" placeholder="例如：数独"></div><div class="field"><label for="matrix-ability">只看主要涉及的能力</label><select id="matrix-ability"><option value="">全部能力</option>'+''.join('<option value="'+a['id']+'">'+esc(a['title'])+'</option>' for a in ab)+'</select></div><button id="matrix-reset" type="button">重置</button></div><div id="matrix-count" class="resultmeta" aria-live="polite">15 个游戏</div></div><div class="table-wrap"><table class="matrix"><thead><tr><th scope="col">游戏 / 规则</th>'+''.join('<th scope="col">'+link(a['id'],p)+'</th>' for a in ab)+'</tr></thead><tbody>'
for g in games:
 b+='<tr data-name="'+esc(g['title'])+'" data-main="'+esc(' '.join(d['ability_id'] for d in g['demands'] if d['level']==2))+'"><th scope="row">'+link(g['id'],p)+(' <span class="tag warn">暂定</span>' if g.get('needs_clarification') else '')+'</th>'+''.join('<td class="l'+str(d['level'])+'" aria-label="'+esc(R[d['ability_id']]['title'])+'：'+['未突出','次要或条件性','主要'][d['level']]+'">'+['—','◐','●'][d['level']]+'</td>' for d in g['demands'])+'</tr>'
b+='</tbody></table></div><p id="matrix-empty" class="empty" hidden>没有匹配的游戏，请调整条件。</p><div class="notice"><strong>如何阅读：</strong>同名游戏因规则、限时、熟练程度和提示不同，会调用不同过程。等级 0 不表示完全没有该过程。历史“神经网络游戏”“四合一连连看”等名称不足以确定独立玩法，待补充规则后再纳入。逐游戏迁移证据审查尚未完成。</div><div class="actions"><a class="btn secondary" href="'+href('design/design-translation/index.html',p)+'">从矩阵进入产品设计 →</a></div>'
render(p,'游戏能力需求矩阵',b,'games')
# Search index embeds all authored text for offline browsing; URLs relative to root.
search=[dict(id=r['id'],title=r['title'],summary=r['summary'],collection=r['collection'],category=C[r['collection']]['title'],status=r['status'],url=path(r['id']),text=' '.join([r['title'],r['summary'],*r.get('aliases',[]),json.dumps(r['sections'],ensure_ascii=False)])) for r in R.values()]
search += [dict(id=s['id'],title=s['title'],summary=s['note'] or s['access'],collection='sources',category='来源',status=s['kind'],url='sources/index.html#'+s['id'],text=' '.join(map(str,s.values()))) for s in S.values()]
(ROOT/'data/search-index.json').write_text(json.dumps(search,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'assets/search-data.js').write_text('window.BRAINLAB_INDEX='+json.dumps(search,ensure_ascii=False).replace('<','\\u003c')+';',encoding='utf-8')
p='search/index.html';b=crumb(p,title='检索')+intro('检索整个知识库','搜索正文、来源与历史别名，按专题和证据状态筛选。','Knowledge Search')+'<form id="search-form" class="searchbox"><div class="filters"><div class="field wide"><label for="query">关键词</label><input id="query" type="search" placeholder="海马、迁移、暂停、阿兹海默…" autocomplete="off"></div><div class="field"><label for="category">专题</label><select id="category"><option value="">全部专题</option>'+''.join('<option value="'+k+'">'+esc(c['title'])+'</option>' for k,c in C.items())+'<option value="sources">来源</option></select></div><div class="field"><label for="status">条目状态 / 证据类型</label><select id="status"><option value="">全部状态</option></select></div><button type="submit">检索</button><button id="reset" type="button">重置</button></div></form><p id="result-count" class="resultmeta" aria-live="polite"></p><div id="results" class="results"></div><noscript><p class="nojs">检索需要 JavaScript。可以通过首页各专题目录浏览全部内容。</p></noscript>'
render(p,'全站检索',b)
render('404.html','页面未找到',intro('这个页面没有找到','可以返回知识库首页，或通过检索寻找对应条目。')+'<div class="actions"><a class="btn" href="/brainlab/">返回首页</a><a class="btn secondary" href="/brainlab/search/">检索知识库</a></div>')
(ROOT/'.nojekyll').touch()
(ROOT/'data/build-manifest.json').write_text(json.dumps({'version':DB['version'],'pages':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Built {len(manifest)} pages, {len(R)} records, {len(S)} sources')
