#!/usr/bin/env python3
"""8-qubit QAOA over 8 CLASSICALLY EVALUATED Alcubierre metric variants.

One-hot candidate selection: minimize Σ score_i*x_i + 5(Σx_i-1)^2.
score combines logarithmic |Eulerian E|, shell volume, curvature proxy.
ALL candidates fail Eulerian WEC. This is NOT an FTL feasibility oracle.
"""
import csv, json, math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize

def shortlist(path):
    with open(path,encoding="utf-8",newline="") as f:
        rows=[r for r in csv.DictReader(f) if r["profile"]=="quintic_C2" and float(r["beta"])==1.01 and float(r["inner_radius_m"])>=6]
    rows.sort(key=lambda r:abs(float(r["eulerian_energy_J"])))
    out=[]
    for r in rows:
        if any(float(r["inner_radius_m"])==float(x["inner_radius_m"]) and abs(float(r["wall_width_m"])-float(x["wall_width_m"]))<4 for x in out):
            continue
        out.append(r)
        if len(out)==8:break
    if len(out)!=8:raise ValueError("Need 8 distinct real metric cases")
    return out

def scores(cases):
    e=np.array([abs(float(r["eulerian_energy_J"])) for r in cases])
    curv=np.array([float(r["max_d2fdr2_1_m2"]) for r in cases])
    vol=np.array([float(r["shell_volume_m3"]) for r in cases])
    return (np.log10(e/e.min())+.25*curv/curv.max()+.25*vol/vol.max()).tolist()

def E(mask,values,penalty=5):
    n=mask.bit_count()
    return sum(values[i] for i in range(8) if mask & (1<<i))+penalty*(n-1)**2

def qasm(values,gammas,betas,penalty=5):
    # QUBO: linear a_i=score_i-penalty, pair a_ij=2*penalty
    a=[v-penalty for v in values]
    z=[-v/2-7*penalty/2 for v in a]
    out=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[8];','creg c[8];']
    out += [f'h q[{i}];' for i in range(8)]
    for g,b in zip(gammas,betas):
        out += [f'rz({2*g*zi:.11f}) q[{i}];' for i,zi in enumerate(z)]
        for i in range(8):
            for j in range(i+1,8):
                out += [f'cx q[{i}],q[{j}];',f'rz({g*penalty:.11f}) q[{j}];',f'cx q[{i}],q[{j}];']
        out += [f'rx({2*b:.11f}) q[{i}];' for i in range(8)]
    out.append('measure q -> c;')
    return '\n'.join(out)+'\n'

def distribution(values,params):
    p=len(params)//2
    if 2*p!=len(params):raise ValueError("Even parameter count needed")
    energy=np.array([E(i,values) for i in range(256)])
    state=np.full(256,1/16,dtype=complex)
    masks=np.arange(256)
    for gamma,beta in zip(params[:p],params[p:]):
        state*=np.exp(-1j*gamma*energy)
        cs=math.cos(beta); sn=-1j*math.sin(beta)
        for q in range(8):
            ix=masks[(masks & (1<<q))==0]
            old0=state[ix].copy();old1=state[ix^(1<<q)].copy()
            state[ix]=cs*old0+sn*old1
            state[ix^(1<<q)]=sn*old0+cs*old1
    return energy,abs(state)**2

def run(input_csv,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    cases=shortlist(input_csv); s=scores(cases)
    exact=min((E(i,s),i) for i in range(256))
    rng=np.random.default_rng(20261025)
    objective=lambda param:float(np.dot(*distribution(s,param)))
    attempts=[minimize(objective,rng.uniform(-.5,1,size=4),method="COBYLA",options={"maxiter":160,"rhobeg":.6}) for _ in range(4)]
    best=min(attempts,key=lambda r:r.fun)
    en,p=distribution(s,best.x)
    feasible_index=int(np.argmax([p[1<<i] for i in range(8)]))
    result={
      "date":"2026-10-25","local_simulation":"COMPLETED","cloud_submission":"NOT_EXECUTED_BY_THIS_SCRIPT",
      "metrics_count":8,"QAOA_qubits":8,"layers":2,
      "all_candidates_fail_WEC":all(x["WEC"]=="FAIL_EULERIAN_COUNTEREXAMPLE" for x in cases),
      "objective":"energy logarithmic ratio + curvature penalty + shell volume penalty; one-hot penalty 5",
      "classical_exact_mask":format(exact[1],"08b"),"classical_best_objective":exact[0],
      "qaoa_expected_objective":float(np.dot(en,p)),
      "qaoa_raw_mode_mask":format(int(np.argmax(p)),"08b"),
      "qaoa_feasible_postselected_mask":format(1<<feasible_index,"08b"),
      "qaoa_feasible_matches_classical":(1<<feasible_index)==exact[1],
      "qaoa_probability_of_exact_best":float(p[exact[1]]),
      "qaoa_onehot_mass":float(sum(p[1<<i] for i in range(8))),
      "angles":[float(x) for x in best.x],
      "cases":[{"R_m":float(v["inner_radius_m"]),"wall_m":float(v["wall_width_m"]),"energy_J":float(v["eulerian_energy_J"]),"score":s[i]} for i,v in enumerate(cases)],
      "physically_realizable_ftl":False,"quantum_advantage_demonstrated":False
    }
    (output/"physical_metric_8q.qasm").write_text(qasm(s,best.x[:2],best.x[2:]),encoding="utf-8")
    (output/"physical_metric_8q.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    return result

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument("--metric-csv",required=True);parser.add_argument("--out",default="qaoa-results")
    p=parser.parse_args();print(json.dumps(run(p.metric_csv,p.out),ensure_ascii=False,indent=2))
