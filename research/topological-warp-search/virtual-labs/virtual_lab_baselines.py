"""QuantDeus NX-01: public baseline physics observables (not new FTL)."""
from math import pi,exp
C=299792458.
G=6.67430e-11
HBAR=1.054571817e-34
EV=1.602176634e-19
def redshift(height_m,g=9.80665): return g*height_m/C**2
def cassini_z(gamma_minus_one): return (gamma_minus_one-2.1e-5)/2.3e-5
def gw170817_allows(delta_vg_over_c): return -3e-15<=delta_vg_over_c<=7e-16
def ideal_casimir_pressure(gap_m): return -(pi*pi*HBAR*C)/(240*gap_m**4)
def kk_mode_1_eV(radius_m): return HBAR*C/(radius_m*EV)
def yukawa_force_fraction(r,lam,alpha=1): return alpha*(1+r/lam)*exp(-r/lam)
def physical_ftl_proven(candidate):
    # All numerical benchmarks are only necessary but far from sufficient.
    required=("derived_action","coupled_EOM","observer_NEC_WEC","QEI",
              "causality","null_geodesics","stable_source","experiment")
    return all(candidate.get(k) is True for k in required) and False  # no experimental FTL exists
if __name__=="__main__":
    print("GR clock at 33cm",redshift(.33))
    print("Cassini GR Z",cassini_z(0.))
    print("GW GR valid",gw170817_allows(0.))
    print("Ideal Casimir 100nm pressure",ideal_casimir_pressure(100e-9))
    print("KK S1 first mode for 1 micron",kk_mode_1_eV(1e-6))
    print("NO experimentally validated FTL",physical_ftl_proven({}))
