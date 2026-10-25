import math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from virtual_lab_baselines import *
class BaselineChecks(unittest.TestCase):
 def test_nist(self): self.assertTrue(math.isclose(redshift(.33),3.600751991825412e-17,rel_tol=1e-10))
 def test_cassini(self): self.assertLess(abs(cassini_z(0)),2)
 def test_gw(self):
  self.assertTrue(gw170817_allows(0));self.assertFalse(gw170817_allows(3e-15))
 def test_casimir_power(self): self.assertTrue(math.isclose(ideal_casimir_pressure(2e-7)/ideal_casimir_pressure(1e-7),1/16))
 def test_kk_scaling(self): self.assertTrue(math.isclose(kk_mode_1_eV(1e-6)/kk_mode_1_eV(2e-6),2))
 def test_no_ftl_proof(self): self.assertFalse(physical_ftl_proven({}))
