(()=>{
 'use strict';
 const data=window.BRAINLAB_INDEX||[],root=document.body.dataset.root||'index.html';
 const base=new URL(root,location.href),url=p=>new URL(p,base).href;
 const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n};
 const query=document.getElementById('query');
 if(query){
  const category=document.getElementById('category'),status=document.getElementById('status'),out=document.getElementById('results'),count=document.getElementById('result-count');
  [...new Set(data.map(x=>x.status))].sort((a,b)=>a.localeCompare(b,'zh')).forEach(s=>{const o=el('option','',s);o.value=s;status.append(o)});
  const params=new URLSearchParams(location.search);query.value=params.get('q')||'';category.value=params.get('category')||'';status.value=params.get('status')||'';
  function run(){
   const words=query.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
   const matches=data.filter(x=>(!category.value||x.collection===category.value)&&(!status.value||x.status===status.value)&&words.every(w=>x.text.toLocaleLowerCase().includes(w)));
   out.replaceChildren();count.textContent=`找到 ${matches.length} 条 · 知识与来源分别标记`;
   if(!matches.length){out.append(el('div','empty','没有匹配结果。试试更短的关键词，或清除专题与状态筛选。'));return}
   matches.forEach(x=>{const article=el('article','result'),tag=el('span','tag',x.category+' · '+x.status),h=el('h2'),a=el('a','',x.title);a.href=url(x.url);h.append(a);article.append(tag,h,el('p','',x.summary));out.append(article)});
  }
  function update(){const p=new URLSearchParams();if(query.value.trim())p.set('q',query.value.trim());if(category.value)p.set('category',category.value);if(status.value)p.set('status',status.value);history.replaceState(null,'',location.pathname+(p.size?'?'+p:'')+location.hash);run()}
  document.getElementById('search-form').addEventListener('submit',e=>{e.preventDefault();update()});query.addEventListener('input',update);category.addEventListener('change',update);status.addEventListener('change',update);
  document.getElementById('reset').addEventListener('click',()=>{query.value='';category.value='';status.value='';update();query.focus()});run();
 }
 const mq=document.getElementById('matrix-q');
 if(mq){const ability=document.getElementById('matrix-ability'),rows=[...document.querySelectorAll('tr[data-name]')];
  function filter(){let n=0;for(const row of rows){const show=row.dataset.name.toLowerCase().includes(mq.value.trim().toLowerCase())&&(!ability.value||row.dataset.main.split(' ').includes(ability.value));row.hidden=!show;if(show)n++}document.getElementById('matrix-count').textContent=n+' 个游戏';document.getElementById('matrix-empty').hidden=n>0}
  mq.addEventListener('input',filter);ability.addEventListener('change',filter);document.getElementById('matrix-reset').addEventListener('click',()=>{mq.value='';ability.value='';filter()})
 }
 // Preserve previously shared single-page chapter links.
 const legacy={duolingo:'research/duolingo/index.html',dementia:'research/alzheimer/index.html',keep:'research/keep/index.html',brain:'brain/index.html',abilities:'abilities/index.html',games:'games/index.html',matrix:'games/matrix.html',science:'research/alzheimer/ad-intervention/index.html',experience:'design/design-session/index.html',roadmap:'design/design-outcomes/index.html'};
 if(document.body.dataset.root==='index.html'&&legacy[location.hash.slice(1)])location.replace(url(legacy[location.hash.slice(1)]));
})();
