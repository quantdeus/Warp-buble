#!/usr/bin/env python3
"""NX-01: public-literature Krasnikov-tube benchmark + strict evidence gates.

Reimplements the Everett--Roman mid-tube T_tt radial diagnostic used by
QuantDeus's previous v11 archive. Geometric units G=c=1.
T_tt is a coordinate component, not an all-observer WEC/NEC evaluation.
No caps, coupled Einstein equations, QEI, or global null geodesics are solved.
"""
import numpy as np

SEED_FAMILIES=("tube_mass_shell","tube_irrotational_shift","tube_shell_shift")


def metric_seed(x,y,z,family,L=12.,R=2.,w=.45,lapse=.10,spatial=.12,shift=.55):
    """Smooth finite ADM ansatz. Construction history is not thereby established."""
    if family not in SEED_FAMILIES or min(L,R,w)<=0:
        raise ValueError("invalid family or geometric scale")
    window=.5*(np.tanh((x+L/2)/w)-np.tanh((x-L/2)/w))
    shell=window*.5*(1+np.tanh((R-np.hypot(y,z))/w))
    alpha=1+lapse*shell
    q=1+spatial*shell
    beta=np.array([-shift*shell,0.,0.])
    if family in ("tube_irrotational_shift","tube_shell_shift"):
        r2=y*y+z*z
        beta[1]=shift*shell*y/(R*R+r2)
        beta[2]=shift*shell*z/(R*R+r2)
    gamma=(q*q)*np.eye(3)
    g=np.zeros((4,4))
    g[1:,1:]=gamma
    g[0,1:]=g[1:,0]=gamma@beta
    g[0,0]=-alpha*alpha+beta@gamma@beta
    return g


def middle_tube(delta,rho,eps,D,nr=192):
    """Radial Everett--Roman 4D central-tube T_tt diagnostic (no end caps).

    delta>0, rho>0, eps>0, D>0; 2/delta is idealized post-construction
    Earth-clock *round-trip* ratio, not 1-way FTL verification.
    """
    if not (0<delta<2 and min(rho,eps,D)>0):
        raise ValueError("unphysical sampling inputs")
    r=rho*(np.arange(nr)+.5)/nr
    z=(rho-r)/eps
    tanh=np.tanh(z);sech2=1/np.cosh(z)**2
    k=1-(2-delta)*.5*(1+tanh)
    kp=(2-delta)*.5*sech2/eps
    kpp=(2-delta)*sech2*tanh/eps**2
    Ttt=(-4*(1+k)*kp/r+3*kp*kp-4*(1+k)*kpp)/(32*np.pi*(1+k)**2)
    negative_integral=float(np.sum(np.minimum(Ttt,0)*2*np.pi*r*rho/nr)*D)
    return {"roundtrip_ratio_ideal":2/delta,
            "min_coordinate_Ttt":float(np.min(Ttt)),
            "negative_mid_tube_integral":negative_integral,
            "status":"MIDTUBE_DIAGNOSTIC_ONLY",
            "NEC":"UNKNOWN","WEC":"UNKNOWN","QEI":"UNKNOWN",
            "null_roundtrip_geometry":"UNVERIFIED","physical_FTL":False}


def gate(summary):
    """No empirical/physical promotion from local signature or v_target."""
    required=("einstein_residual","all_observer_nec_wec_dec","QEI",
              "global_null_geodesics","causal_build","stability",
              "field_source","replicated_experiment")
    missing=[k for k in required if summary.get(k)!="PASS"]
    return {"required":required,"missing":missing,
            "physical_FTL_verified":False,
            "status":"INSUFFICIENT_EVIDENCE" if missing else "INDEPENDENT_REVIEW_REQUIRED"}
