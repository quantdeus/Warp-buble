#!/usr/bin/env python3
"""NX-01 physical-parameter metric search, v0.2: classical GR screening.

Metric: ds²=-c²dt²+[dx - beta*c*f(r)dt]²+dy²+dz².
Eulerian density: rho= -c⁴ beta² sin²(theta) (df/dr)² /(32πG).
Volume integral: E= -c⁴ beta²/(12G) ∫ r² (df/dr)² dr.
This is ONE energy component; not a full Tμν or FTL realizability proof.
"""
import csv, json, math
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.constants import c,G,pi,hbar

X,W0=leggauss(96)
U=(1+X)/2
W=W0/2

def shape(name,u):
    if name=="quintic_C2":
        return 1-10*u**3+15*u**4-6*u**5,-30*u**2*(1-u)**2,-60*u*(1-u)*(1-2*u)
    if name=="cubic_C1":
        return 1-3*u*u+2*u**3,-6*u*(1-u),-6+12*u
    if name=="cosine_C1":
        return (1+np.cos(pi*u))/2,-pi*np.sin(pi*u)/2,-(pi*pi/2)*np.cos(pi*u)
    raise ValueError(name)

def evaluate(profile,R,wall,beta):
    if R<=0 or wall<=0 or beta<0:raise ValueError("Invalid metric parameters")
    f,df,d2f=shape(profile,U)
    fp=df/wall
    J=wall*float(np.dot(W,(R+wall*U)**2 * fp**2))
    E=-(c**4/(12*G))*beta**2*J
    vol=4*pi/3*((R+wall)**3-R**3)
    return {
        "family":"alcubierre_flat_slices","profile":profile,"inner_radius_m":R,
        "wall_width_m":wall,"outer_radius_m":R+wall,"beta":beta,
        "radial_gradient_integral_m":J,
        "eulerian_energy_J":E,"shell_volume_m3":vol,
        "max_dfdr_1_m":float(np.max(abs(fp))),
        "max_d2fdr2_1_m2":float(np.max(abs(d2f))/wall**2),
        "formal_ftl_parameter":bool(beta>1),
        "WEC":"FAIL_EULERIAN_COUNTEREXAMPLE" if beta>0 and J>0 else "PASS_EULERIAN_ONLY",
        "NEC":"UNTESTED","QEI":"UNTESTED","causality":"UNTESTED",
        "stability":"UNTESTED","matter_source":"UNTESTED","physically_realizable_ftl":False
    }

def pareto(cases,keys):
    return [a for a in cases if not any(
       all(b[k]<=a[k] for k in keys) and any(b[k]<a[k] for k in keys)
       for b in cases if b is not a)]

def scan(output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    rows=[evaluate(p,R,w,beta)
        for p in ("quintic_C2","cubic_C1","cosine_C1")
        for R in (4.,6.,8.,12.)
        for w in (.5,1.,2.,4.,8.,12.,16.)
        for beta in (0.,.9,1.01,2.)]
    selected=[r for r in rows if r["inner_radius_m"]>=6 and r["beta"]>1 and r["profile"]=="quintic_C2"]
    best=min(selected,key=lambda r:abs(r["eulerian_energy_J"]))
    pf=pareto(selected,("radial_gradient_integral_m","shell_volume_m3","max_d2fdr2_1_m2"))
    for fname,data in (("candidate_metrics.csv",rows),("pareto_formal_ftl.csv",pf)):
        with (out/fname).open("w",encoding="utf-8",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(data)
    result={
       "status":"CLASSICAL_PHYSICS_GATE_ONLY",
       "date":"2026-10-25","metrics_screened":len(rows),
       "formal_ftl_parameters":sum(r["formal_ftl_parameter"] for r in rows),
       "wec_failure_among_formal_ftl":sum(r["formal_ftl_parameter"] and r["WEC"].startswith("FAIL") for r in rows),
       "physically_realizable_ftl_found":0,"pareto_candidates":len(pf),"best_energy_case":best,
       "limitations":[
         "No full Tμν or observer-robust NEC: additional verifier required",
         "Negative Eulerian energy violates WEC in this fixed ansatz",
         "No causality, quantum inequality, field-source or stability validation",
         "No claim of physical FTL, quantum advantage or exhaustive 12T search"]
    }
    (out/"summary.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    return result

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--out",default="physical-results")
    args=p.parse_args();print(json.dumps(scan(args.out),ensure_ascii=False,indent=2))
