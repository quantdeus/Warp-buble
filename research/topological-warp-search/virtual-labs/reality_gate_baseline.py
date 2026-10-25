"""Public small baseline for NX-01 Reality Gate; SI units, illustrative models."""
from math import exp,pi
from scipy.constants import c,G,hbar
def shift_gaussian(A=1e-6,L=1.,y=1.):
    if L<=0:raise ValueError("L>0")
    v=A*exp(-y*y/(2*L*L));return v,-y*v/L**2,(y*y/L**4-1/L**2)*v
def source_energy_density(A=1e-6,L=1.,y=1.):
    _,vp,_=shift_gaussian(A,L,y)
    return -(c**4/G)*vp*vp/(32*pi)
def nec_null_z(A=1e-6,L=1.,y=1.):
    _,vp,_=shift_gaussian(A,L,y)
    return -vp*vp/(16*pi)
def casimir_pressure(gap=100e-9):
    if gap<=0:raise ValueError("positive gap")
    return -(pi*pi*hbar*c)/(240*gap**4)
def casimir_ideal_energy(area=1e-4,gap=100e-9):
    if min(area,gap)<=0:raise ValueError("positive geometry")
    return -(pi*pi*hbar*c*area)/(720*gap**3)
def ideal_sphere_plane_PFA_force(sphere_R=100e-6,gap=100e-9):
    if min(sphere_R,gap)<=0:raise ValueError("positive geometry")
    return -(pi**3*hbar*c*sphere_R)/(360*gap**3)
if __name__=='__main__':
    print('toy geometric source [J/m3]',source_energy_density())
    print('ideal Casimir force [N]',ideal_sphere_plane_PFA_force())
    print('WARNING: numerical models, NOT experimental confirmation of FTL')
