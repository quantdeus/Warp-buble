#!/usr/bin/env python3
"""TIP v0.1: topology of Russian terms and virtual 12.5T unordered pairs.

Generates hypotheses and a small 8-qubit research-workplan QASM.
NO 12.5T evaluations, NO cloud job, NO physically validated FTL.
"""
import argparse
import json
from pathlib import Path

ROOTS = {
  "metric": ("метрик", "геометри", "солитон", "пузыр"),
  "energy": ("энерг", "вакуум", "казимир", "сжати"),
  "bound": ("квант", "неравенств"),
  "causality": ("причинност", "горизонт"),
  "stability": ("устойчивост", "прилив"),
  "evidence": ("эксперимент", "измерен", "воспроизводим"),
}
GATES = ("metric","formal_ftl","energy_conditions","quantum_bounds",
         "horizon_causality","stability","engineerability","experiment")
TASKS = ("metric","Tmunu","NEC_WEC","QEI","causality","stability","sources","replication")
VALUE = (5,5,5,4,4,4,4,3)
SYNERGY = {(0,1):2.,(1,2):2.5,(1,3):1.8,(0,4):1.2,(4,5):1.8,
           (2,7):2.1,(3,6):1.9,(5,7):1.6,(6,7):1.2}

def pair_count(n):
    if n < 0: raise ValueError("n must be nonnegative")
    return n*(n-1)//2

def offset(n,i):
    return i*(2*n-i-1)//2

def unrank_pair(index,n):
    if not 0 <= index < pair_count(n): raise IndexError(index)
    lo,hi = 0,n-1
    while lo+1 < hi:
        m=(lo+hi)//2
        if offset(n,m) <= index: lo=m
        else: hi=m
    i=hi if offset(n,hi)<=index else lo
    return i,i+1+index-offset(n,i)

def rank_pair(i,j,n):
    if not 0<=i<j<n: raise ValueError("invalid pair")
    return offset(n,i)+j-i-1

def classify(word):
    w=word.strip().casefold().replace("ё","е")
    for group,roots in ROOTS.items():
        if any(w.startswith(root) for root in roots): return group
    return None

def harvest(path, encoding="cp1251", maximum=200):
    """Stream local licensed dictionary, retain only bounded on-topic sample."""
    scanned=0
    words=set()
    with open(path,encoding=encoding,errors="replace") as f:
        for line in f:
            w=line.strip()
            if not w: continue
            scanned+=1
            if len(words)<maximum and classify(w): words.add(w.casefold())
    return scanned,sorted(words)

def objective(bits):
    # Transparent workplan-ranking heuristic, NOT physical-energy functional.
    k=sum(bits)
    v=-sum(x*y for x,y in zip(bits,VALUE))+12*(k-4)**2
    v-=sum(w*bits[i]*bits[j] for (i,j),w in SYNERGY.items())
    v+=10*bits[2]*(1-bits[1]) # NEC check needs Tmunu
    v+=10*bits[6]*(1-bits[1]) # source check needs Tmunu
    v+=8*bits[3]*(1-bits[6])  # QEI needs a source model
    return v

def qaoa_qasm(gammas=(0.02625879,-0.26193632),betas=(1.32439393,1.54310031)):
    # QUBO expression in x_i=(1-Z_i)/2
    linear=[-v-84 for v in VALUE]
    linear[2]+=10;linear[6]+=10;linear[3]+=8
    q={(i,j):24. for i in range(8) for j in range(i+1,8)}
    for (i,j),v in SYNERGY.items():q[i,j]-=v
    q[1,2]-=10;q[1,6]-=10;q[3,6]-=8
    z=[-linear[i]/2-sum(v/4 for (a,b),v in q.items() if i in (a,b))
       for i in range(8)]
    out=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[8];','creg c[8];']
    out.extend(f'h q[{i}];' for i in range(8))
    for gamma,beta in zip(gammas,betas):
        out.extend(f'rz({2*gamma*x:.11f}) q[{i}];' for i,x in enumerate(z))
        for (i,j),v in q.items():
            if abs(v) < 1e-12: continue
            out.extend((f'cx q[{i}],q[{j}];',f'rz({gamma*v/2:.11f}) q[{j}];',
                        f'cx q[{i}],q[{j}];'))
        out.extend(f'rx({2*beta:.11f}) q[{i}];' for i in range(8))
    out.append('measure q -> c;')
    return '\n'.join(out)+'\n'

def run(out,dict_path=None):
    out.mkdir(parents=True,exist_ok=True)
    n=5_000_000;total=pair_count(n)
    sample=['метрика','энергия','геометрия','вакуум','квантовый','неравенство',
            'пузырь','устойчивость','причинность','казимир','эксперимент',
            'прилив','солитон','измерение','сжатие','горизонт']
    actual=0
    if dict_path:
        actual,found=harvest(dict_path)
        sample=list(dict.fromkeys(sample+found))
    bridges=[{'a':a,'b':b,'types':[classify(a),classify(b)],
              'status':'hypothesis','verified_physics':False,'gates':GATES}
             for i,a in enumerate(sample) for b in sample[i+1:]
             if classify(a) and classify(b) and classify(a)!=classify(b)]
    workplans=sorted((objective(tuple(mask>>i&1 for i in range(8))),mask)
                     for mask in range(256))
    best_score,mask=workplans[0]
    addresses=[{'index':k,'pair':unrank_pair(k,n)}
               for k in (0,1,total//2,total-1)]
    assert all(rank_pair(*a['pair'],n)==a['index'] for a in addresses)
    result={
       'status':'LOCAL_CLASSICAL_PILOT_QASM_READY',
       'virtual_pairs':total,'min_index_qubits':(total-1).bit_length(),
       'dictionary_loaded':bool(dict_path),'dictionary_lines_scanned':actual,
       'hypothesis_count':len(bridges),'exact_workplans_scored':256,
       'best_plan':[TASKS[i] for i in range(8) if mask>>i&1],
       'best_score':best_score,'best_plan_score_is_physical_energy':False,
       'samples':addresses,'physical_ftl_verified':False,
       'quantum_cloud_job_submitted':False
    }
    (out/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    (out/'qaoa_workplan_8q.qasm').write_text(qaoa_qasm())
    (out/'hypotheses.json').write_text(json.dumps(bridges,ensure_ascii=False,indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,default=Path('topo-results'))
    p.add_argument('--dictionary-file',type=Path)
    a=p.parse_args()
    print(json.dumps(run(a.output,a.dictionary_file),ensure_ascii=False,indent=2))
