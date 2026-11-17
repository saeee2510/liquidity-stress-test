import unittest

from stress import metrics as m
from stress.scenarios import SCENARIOS, blend

BASE = SCENARIOS["Baseline"]
SEVERE = SCENARIOS["Severe: combined market and firm stress"]


class Metrics(unittest.TestCase):
    def test_baseline_lcr_matches_hand_calculation(self):
        # HQLA 10,000 + 1,700 + 500 = 12,200; outflows 10,600 funding + 600 draws = 11,200; inflows 2,500
        self.assertAlmostEqual(m.lcr(BASE), 12_200 / (11_200 - 2_500), places=6)

    def test_lcr_falls_as_stress_increases(self):
        values = [m.lcr(s) for s in SCENARIOS.values()]
        self.assertTrue(values[0] > values[1] > values[2])

    def test_inflow_cap_applies(self):
        scn = {**BASE, "inflow": {k: 50.0 for k in BASE["inflow"]}}
        out = m.outflows_30d(scn)
        self.assertAlmostEqual(m.lcr(scn), m.hqla_value(scn)[0] / (0.25 * out), places=6)

    def test_survival_shorter_under_severe_stress(self):
        self.assertLess(m.survival_days(SEVERE), m.survival_days(BASE))

    def test_blend_endpoints(self):
        self.assertAlmostEqual(m.lcr(blend(0)), m.lcr(BASE), places=9)
        self.assertAlmostEqual(m.lcr(blend(1)), m.lcr(SEVERE), places=9)

    def test_rag_thresholds(self):
        self.assertEqual(m.rag("LCR", 1.2), "Green")
        self.assertEqual(m.rag("LCR", 1.05), "Amber")
        self.assertEqual(m.rag("LCR", 0.9), "Red")


if __name__ == "__main__":
    unittest.main()
