"""Analytic physics checks; these do not validate hardware safety."""
import sys
from pathlib import Path
import unittest
from math import log
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'simulation'))
from component_budget import Candidate, point, precharge, bleed


class ComponentBudgetTests(unittest.TestCase):
    def test_ripple_frequency_and_rms(self):
        a = point(Candidate(), 26, 12, 120, 12, 100e3)
        b = point(Candidate(), 26, 12, 120, 12, 200e3)
        self.assertAlmostEqual(a['ripple_a'], 2*b['ripple_a'])
        self.assertAlmostEqual(a['il_rms_a']**2,
                               a['il_avg_a']**2+a['ripple_a']**2/12)
        self.assertAlmostEqual(a['output_w'], 106.272)
        self.assertGreater(a['il_peak_a'], a['cap_a'])

    def test_loss_units_and_accounting(self):
        p = point(Candidate(), 26, 12, 120, 12, 200e3)
        self.assertAlmostEqual(p['gate_w'], 4*53e-9*10*200e3)
        self.assertAlmostEqual(p['subtotal_w'], sum(p[k] for k in
            ('conduction_w', 'overlap_w', 'gate_w', 'winding_w', 'shunts_w')))
        self.assertTrue(0 < p['partial_eta'] < 1)

    def test_rc_energy_and_time(self):
        p = precharge(26, 470e-6, 100)
        self.assertAlmostEqual(p['resistor_energy_j'], .15886)
        self.assertAlmostEqual(p['time_s'], .047*log(20))
        # Stored link energy equals resistor dissipation for ideal empty-link RC.
        self.assertAlmostEqual(p['resistor_energy_j'], .5*470e-6*26**2)
        d = bleed(50/9, 22.05, 1, 100)
        self.assertAlmostEqual(d['dissipated_j'], (50/18)*(22.05**2-1))
        with self.assertRaises(ValueError):
            bleed(50/9, 22.05, 0, 100)


if __name__ == '__main__':
    unittest.main()
