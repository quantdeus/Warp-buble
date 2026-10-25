import importlib.util, pathlib, random, unittest
FILE=pathlib.Path(__file__).resolve().parents[1]/"search_pilot.py"
spec=importlib.util.spec_from_file_location("toposearch", FILE)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestTopoWarp(unittest.TestCase):
    def test_12t_exact_index(self):
        n=5_000_000
        total=12_499_997_500_000
        self.assertEqual(mod.pair_count(n),total)
        self.assertEqual((total-1).bit_length(),44)
        for k in [0,1,2,total//2,total-1]:
            self.assertEqual(mod.rank_pair(*mod.unrank_pair(k,n),n),k)
    def test_index_small_and_random(self):
        for n in [2,3,7,33]:
            self.assertEqual(len({mod.unrank_pair(i,n) for i in range(mod.pair_count(n))}),mod.pair_count(n))
        r=random.Random(20261025)
        for _ in range(3000):
            k=r.randrange(mod.pair_count(5_000_000))
            self.assertEqual(mod.rank_pair(*mod.unrank_pair(k,5_000_000),5_000_000),k)
    def test_objective_plans(self):
        self.assertEqual(len({tuple((k>>i)&1 for i in range(8)) for k in range(256)}),256)
        self.assertEqual(sum(mod.qaoa_qasm().count(x) for x in ["OPENQASM 2.0;"]),1)
    def test_not_physics(self):
        self.assertNotEqual(mod.classify("метрика"),mod.classify("энергия"))
        self.assertIsNone(mod.classify("непонятное"))
        self.assertTrue(all(k in mod.GATES for k in ["metric","energy_conditions","experiment"]))

if __name__=="__main__":unittest.main()
