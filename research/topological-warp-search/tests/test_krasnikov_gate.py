import importlib.util
from pathlib import Path
import unittest
import numpy as np
F=Path(__file__).resolve().parents[1]/"krasnikov_tube_gate.py"
spec=importlib.util.spec_from_file_location("krasnikov_tube_gate",F)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


class TestKrasnikovGate(unittest.TestCase):
    def test_three_archival_families(self):
        for family in mod.SEED_FAMILIES:
            center=mod.metric_seed(0.,0.,0.,family)
            far=mod.metric_seed(10000.,0.,0.,family)
            eigen=np.linalg.eigvalsh(center)
            self.assertEqual(int(np.sum(eigen<0)),1)
            self.assertTrue(np.allclose(far,np.diag([-1,1,1,1]),atol=1.e-12))

    def test_coordinate_Ttt_is_not_WEC_proof(self):
        v=mod.middle_tube(.2,2.,.45,12.)
        self.assertLess(v["min_coordinate_Ttt"],0.)
        self.assertLess(v["negative_mid_tube_integral"],0.)
        self.assertEqual(v["WEC"],"UNKNOWN")
        self.assertFalse(v["physical_FTL"])

    def test_flat_case(self):
        g=mod.metric_seed(0.,0.,0.,"tube_mass_shell",lapse=0.,spatial=0.,shift=0.)
        self.assertTrue(np.allclose(g,np.diag([-1,1,1,1])))

    def test_no_false_promotion(self):
        self.assertFalse(mod.gate({"v_target":1.05,"local_signature":"PASS"})["physical_FTL_verified"])
        self.assertIn("QEI",mod.gate({})["missing"])


if __name__=="__main__":unittest.main()
