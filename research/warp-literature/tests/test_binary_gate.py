"""Offline QA for Star Trek -> FTL hypothesis binary branches."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("binary_gate", ROOT / "binary_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
registry = json.loads((ROOT / "trek-ftl-branches.json").read_text(encoding="utf-8"))

class BinaryWarpQATests(unittest.TestCase):
    def test_bibliography_all_eight_verified(self):
        self.assertEqual(registry["audit"]["matched"], 8)
        self.assertEqual(len(registry["citations"]), 8)
        self.assertTrue(all(c["sidekick"] == "matched" for c in registry["citations"]))

    def test_preprint_not_mislabeled_as_peer_reviewed(self):
        self.assertEqual(next(c for c in registry["citations"]
            if c["id"] == "le-2026")["publication_status"], "preprint")

    def test_all_candidates_have_eight_gates(self):
        gate.validate(registry)
        self.assertEqual(len(registry["candidates"]), 3)

    def test_alcubierre_formal_ftl_blocked_by_energy(self):
        c = next(c for c in registry["candidates"] if c["id"] == "alcubierre-1994")
        self.assertEqual(c["gates"]["formal_ftl"]["status"], "PASS")
        self.assertEqual(c["gates"]["energy_conditions"]["status"], "FAIL")
        self.assertEqual(gate.classify(c)["verdict"], "ENERGY_CONDITION_BARRIER")

    def test_fuchs_subluminal_not_ftl(self):
        c = next(c for c in registry["candidates"] if c["id"] == "fuchs-2024")
        self.assertEqual(c["gates"]["energy_conditions"]["status"], "PASS")
        self.assertEqual(gate.classify(c)["verdict"], "SUBLUMINAL_NOT_FTL")

    def test_star_trek_not_experimental_evidence(self):
        c = next(c for c in registry["candidates"] if c["id"] == "star-trek-warp")
        self.assertEqual(gate.classify(c)["verdict"], "METRIC_NOT_ESTABLISHED")

    def test_unknown_not_promoted_to_pass(self):
        c = next(c for c in registry["candidates"] if c["id"] == "star-trek-warp")
        self.assertGreater(gate.classify(c)["scientific_gates_unknown"], 0)
        self.assertFalse(gate.classify(c)["physical_ftl_verified"])

    def test_fake_pass_without_evidence_is_rejected(self):
        broken = copy.deepcopy(registry)
        broken["candidates"][0]["gates"]["metric"]["status"] = "PASS"
        with self.assertRaises(AssertionError):
            gate.report(broken)

    def test_never_announce_ftl_from_json_labels(self):
        synthesized = copy.deepcopy(registry["candidates"][1])
        for detail in synthesized["gates"].values():
            detail["status"] = "PASS"
            detail["evidence"] = ["alcubierre-1994"]
        result = gate.classify(synthesized)
        self.assertEqual(result["verdict"],
                         "REQUIRES_INDEPENDENT_EXPERIMENTAL_REVIEW")
        self.assertFalse(result["physical_ftl_verified"])

    def test_report_has_no_ftl_claim(self):
        result = gate.report(registry)
        self.assertFalse(result["physical_ftl_verified"])
        self.assertTrue(all(not c["physical_ftl_verified"]
                            for c in result["candidates"]))

if __name__ == "__main__":
    unittest.main()
