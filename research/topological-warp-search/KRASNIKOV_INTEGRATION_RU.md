# NX-01 · Krasnikov branch integration (25.10.2026)

**Status:** added research-only numerical controls; NO physically realizable FTL discovered. This directory is part of draft PR #6 and must not be merged without QA.

## Legacy QuantDeus cross-check

Previous QuantDeus research materials were inspected *read-only* (Dropbox Warp Synthesis v10/v11, and SubWarp v12). This PR **does not copy private archives or internal investor PDFs** into public GitHub.

The archive's 100,000,000 input specifications and 14,143,492 structurally accepted entries are historical **boundary-data scans**. None of those numbers is a count of solved Einstein--Maxwell--plasma configurations. The 200 Lorentzian signature checks are expected for a valid ADM decomposition (they are sanity checks, not verified matter sources).

The archive's three tube families are:

- `tube_mass_shell`
- `tube_irrotational_shift`
- `tube_shell_shift`

`krasnikov_tube_gate.py` reimplements two *independent numerical diagnostics* from the previous analysis: smooth 4D tube-inspired ADM metric ansatz and the Everett--Roman (1997) radial `T_tt` test on the central portion of a tube.

**Important:** The late-time central tube excludes end caps, dynamic construction, and quantum backreaction. A negative coordinate `T_tt` cannot replace an all-observer NEC/WEC test. The ideal `2/delta` ratio refers to a **round trip after construction**; it is not a proven one-way FTL outcome.

### What the hybrid search is allowed to do

1. Generate physical metric boundary specifications from morphology/topology.
2. Run exact classical Einstein/Maxwell/plasma/shell computations before any promotion.
3. Calculate pointwise/all-observer NEC/WEC/DEC, QEI, spacetime curvature, dynamic stability.
4. Integrate global null geodesics and verify causal *construction*, and CTC risk from paired tubes.
5. Supply only trustworthy numerical objective scores to a quantum optimizer (QAOA), with a classical control.

**Do not** multiply putative energy improvements of unrelated theories without one coupled field-equation solution. Preserve `UNKNOWN` as `UNKNOWN`; report QAOA resource use precisely. A proposed soliton or plasma term is an ansatz until its joint matter–metric equations are solved.

### How to run

```bash
pip install numpy
python -m unittest discover -s research/topological-warp-search/tests -v
python - <<'PY'
import sys
sys.path.insert(0, 'research/topological-warp-search')
from krasnikov_tube_gate import middle_tube, gate
print(middle_tube(delta=.2,rho=2,eps=.45,D=12))
print(gate({}))
PY
```

**References:** Everett & Roman, *Phys. Rev. D 56*, 2100 (1997), DOI [10.1103/PhysRevD.56.2100](https://doi.org/10.1103/PhysRevD.56.2100); Krasnikov, *Phys. Rev. D 67*, 104013 (2003); Celmaster & Rubin, arXiv:[2511.18251](https://arxiv.org/abs/2511.18251) (2025 preprint; criticism of Lentz WEC claims).

The user's separate *Helios-Soliton 2.0* concept is to be reviewed against these physical gates; its private budget and uploaded full text are not reproduced here.
