"""Physics search regressions; run with python -m unittest discover -s research/topological-warp-search/tests."""
import importlib.util
import math
from pathlib import Path
import unittest

SRC=Path(__file__).resolve().parents[1]/"physical_metric_search.py"
spec=importlib.util.spec_from_file_location("physical_metric_search",SRC)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class PhysicsGates(unittest.TestCase):
    def test_minkowski(self):
        for shape in ("quintic_C2","cubic_C1","cosine_C1"):
            self.assertEqual(m.evaluate(shape,6.,2.,0.)["eulerian_energy_J"],0.)
    def test_wec_negative(self):
        for shape in ("quintic_C2","cubic_C1","cosine_C1"):
            v=m.evaluate(shape,6.,2.,1.01)
            self.assertLess(v["eulerian_energy_J"],0)
            self.assertEqual(v["WEC"],"FAIL_EULERIAN_COUNTEREXAMPLE")
            self.assertFalse(v["physically_realizable_ftl"])
    def test_cubic_analytic(self):
        for R in (4.,6.,12.):
            for w in (1.,5.,12.):
                actual=m.evaluate("cubic_C1",R,w,1.)["radial_gradient_integral_m"]
                expected=6*R*R/(5*w)+6*R/5+12*w/35
                self.assertTrue(math.isclose(actual,expected,rel_tol=1.e-11))
    def test_beta_squared(self):
        small=m.evaluate("quintic_C2",6.,4.,.5)["eulerian_energy_J"]
        big=m.evaluate("quintic_C2",6.,4.,1.)["eulerian_energy_J"]
        self.assertAlmostEqual(big/small,4.)
    def test_c2_quintic_join(self):
        import numpy as np
        for x in (0.,1.):
            f,fp,fpp=m.shape("quintic_C2",np.array([x]))
            self.assertAlmostEqual(float(fp[0]),0.)
            self.assertAlmostEqual(float(fpp[0]),0.)
    def test_no_false_necessity(self):
        m.evaluate("quintic_C2",6.,12.,.9)["WEC"]=="FAIL_EULERIAN_COUNTEREXAMPLE"
        self.assertTrue(m.evaluate("quintic_C2",6.,12.,1.01)["NEC"]=="UNTESTED")

if __name__=="__main__":unittest.main()
