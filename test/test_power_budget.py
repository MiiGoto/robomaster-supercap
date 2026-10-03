"""Analytic physics checks and energy conservation, not circuit validation."""
import sys
from pathlib import Path
import unittest
from dataclasses import replace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'simulation'))
from power_budget import BANKS, discharge, charge, runtime


class PhysicsChecks(unittest.TestCase):
    def test_series_and_rule_energy(self):
        a=BANKS[0]
        self.assertAlmostEqual(a.c_f,50/9)
        self.assertAlmostEqual(a.usable_j,950.5625)
        for b in BANKS:
            self.assertLessEqual(b.rule_nominal_j,2000)
            self.assertLessEqual(b.rule_nominal_j*1.3,2200)

    def test_power_both_directions_and_limits(self):
        for b in BANKS:
            for v in (b.v_min,b.v_max):
                d=discharge(b,v,22,120,b.peak_a)
                self.assertLessEqual(d['cap_a'],b.peak_a+1e-9)
                self.assertAlmostEqual(d['bus_a']*22,d['output_w'])
                self.assertAlmostEqual(v*d['cap_a'],d['output_w']+d['esr_loss_w']+d['converter_loss_w'])
                c=charge(b,v,26,40,b.normal_a)
                self.assertLessEqual(c['cap_a'],0)
                self.assertLessEqual(c['terminal_v'],b.v_max+1e-9)
                if v == b.v_max:
                    self.assertEqual(c['input_w'],0)
                self.assertAlmostEqual(c['input_w'],c['stored_power_w']+c['esr_loss_w']+c['converter_loss_w'])

    def test_zero_esr_analytic_runtime(self):
        b=replace(BANKS[0],cell_esr_ohm=0)
        t=runtime(b,20,12)
        self.assertAlmostEqual(t['duration_s'],b.eta*b.usable_j/20,places=7)

    def test_conservation_and_step_convergence(self):
        b=BANKS[0]
        coarse,fine=runtime(b,120,12,.004),runtime(b,120,12,.002)
        self.assertLess(abs(fine['conservation_error_j']),1e-7)
        self.assertLess(abs(coarse['duration_s']-fine['duration_s']),.002)
        self.assertLess(fine['output_j'],b.eta*b.usable_j)
        self.assertGreater(fine['limited_s'],0)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            replace(BANKS[0],eta=1)
        with self.assertRaises(ValueError):
            runtime(BANKS[0],0,12)
        with self.assertRaises(ValueError):
            discharge(BANKS[0],12,0,120,12)


if __name__=='__main__':
    unittest.main()
