# -*- coding: utf-8 -*-
"""Reproduce the explicitly specified DL check from published extracted inputs.
Run from any directory: python3 /path/to/scripts/reproduce_lampit.py
This checks the supplied aggregate data, not individual participant observations.
"""
import json, math
from pathlib import Path
root=Path(__file__).resolve().parents[1]
x=json.loads((root/'data/alzheimer/lampit-reanalysis.json').read_text())
r=x['rows'];assert len(r)==8 and all(v['variance']>0 for v in r)
w=[1/v['variance'] for v in r]
fixed=sum(a*v['g'] for a,v in zip(w,r))/sum(w)
q=sum(a*(v['g']-fixed)**2 for a,v in zip(w,r));df=len(r)-1
c=sum(w)-sum(a*a for a in w)/sum(w)
tau=max(0,(q-df)/c)
wr=[1/(v['variance']+tau) for v in r]
g=sum(a*v['g'] for a,v in zip(wr,r))/sum(wr)
se=math.sqrt(1/sum(wr));z=1.95996398454
result=dict(g=g,ci_lower=g-z*se,ci_upper=g+z*se,ci_level=.95,Q=q,df=df,tau_squared=tau,I_squared_percent=max(0,(q-df)/q)*100)
for name,value in result.items():assert math.isclose(value,x['result'][name],rel_tol=1e-10,abs_tol=1e-10),name
print(json.dumps({'method':'specified DL aggregate-data check','result':result,'matches_saved_result':True},ensure_ascii=False,indent=2))
