"""Candidate sensitivity calculations, SI units; not rating certification.

Single-leg buck/boost CCM approximation outside the overlap transition region.
Does not model PWM sequence, transients, Coss/Qrr/core/connector/aux losses.
Task 2 eta remains an independent planning input; do not add this loss budget
to Task 2 loss when summing system energy (that would double count).
"""
from dataclasses import dataclass
from math import sqrt, log
from pathlib import Path
import argparse

from power_budget import BANKS, discharge


@dataclass(frozen=True)
class Candidate:
    mosfet: str = 'CSD18540Q5B'
    rds_max_ohm: float = .0022  # 25 C, Vgs=10 V, datasheet maximum
    qg_c: float = 53e-9  # maximum at datasheet 10 V test conditions
    l_h: float = 22e-6
    dcr_max_ohm: float = .016  # XAL1510-223, 25 C
    l_tolerance_factor: float = .8  # -20% manufacturing tolerance
    l_bias_factor: float = .8  # sensitivity ONLY, not guaranteed DC-bias curve
    hot_rds_factor: float = 1.6  # sensitivity ONLY, not guaranteed thermal model
    copper_temp_c: float = 80  # assumed winding temperature, not predicted
    edge_sum_s: float = 40e-9  # assumed tr+tf; not datasheet RG=0 waveform
    gate_v: float = 10
    cap_shunt_ohm: float = .003
    bus_shunt_ohm: float = .003
    inductor_shunt_ohm: float = .003

    def __post_init__(self):
        positive = (self.rds_max_ohm, self.qg_c, self.l_h, self.dcr_max_ohm,
                    self.hot_rds_factor, self.edge_sum_s, self.gate_v,
                    self.cap_shunt_ohm, self.bus_shunt_ohm,
                    self.inductor_shunt_ohm)
        if (any(x <= 0 for x in positive) or
                not 0 < self.l_tolerance_factor <= 1 or
                not 0 < self.l_bias_factor <= 1 or self.copper_temp_c < 25):
            raise ValueError('Invalid sensitivity inputs')


def point(candidate, bus_v, cap_open_v, request_w, cap_limit_a, fs_hz):
    if fs_hz <= 0:
        raise ValueError('Positive frequency required')
    p = discharge(BANKS[0], cap_open_v, bus_v, request_w, cap_limit_a)
    low, high = sorted((bus_v, p['terminal_v']))
    leff = candidate.l_h*candidate.l_tolerance_factor*candidate.l_bias_factor
    duty = 1-low/high
    ripple = low*duty/(leff*fs_hz)
    # Conservatively assign converter input power across the lower rail.
    # Boost: IL=Icap. Buck: includes eta loss rather than equating IL to Icap.
    il_avg = p['output_w']/BANKS[0].eta/low
    il_rms = sqrt(il_avg**2+ripple**2/12)
    il_peak = il_avg+ripple/2
    rds_hot = candidate.rds_max_ohm*candidate.hot_rds_factor
    conduction = 2*il_rms**2*rds_hot  # two conducting FETs in the current path
    overlap = 2*.5*high*il_avg*candidate.edge_sum_s*fs_hz
    gate = 4*candidate.qg_c*candidate.gate_v*fs_hz  # all four switching assumption
    dcr_hot = candidate.dcr_max_ohm*(1+.00393*(candidate.copper_temp_c-25))
    winding = il_rms**2*dcr_hot
    shunts = (p['cap_a']**2*candidate.cap_shunt_ohm +
              p['bus_a']**2*candidate.bus_shunt_ohm +
              il_rms**2*candidate.inductor_shunt_ohm)
    subtotal = conduction+overlap+gate+winding+shunts
    return dict(**p, il_avg_a=il_avg, il_rms_a=il_rms, il_peak_a=il_peak,
                ripple_a=ripple, leff_h=leff, conduction_w=conduction,
                overlap_w=overlap, gate_w=gate, winding_w=winding,
                shunts_w=shunts, subtotal_w=subtotal,
                partial_eta=p['output_w']/(p['output_w']+subtotal))


def precharge(bus_v, c_link_f, resistance_ohm, fraction=.95):
    """Initially empty local link; no load, ideal supply/resistor. Not bank charge."""
    if min(bus_v, c_link_f, resistance_ohm) <= 0 or not 0 < fraction < 1:
        raise ValueError('Invalid RC scenario')
    return dict(initial_a=bus_v/resistance_ohm,
                initial_w=bus_v**2/resistance_ohm,
                resistor_energy_j=.5*c_link_f*bus_v**2,
                time_s=-resistance_ohm*c_link_f*log(1-fraction))


def bleed(c_f, from_v, to_v, resistance_ohm):
    if c_f <= 0 or resistance_ohm <= 0 or not 0 < to_v < from_v:
        raise ValueError('Invalid discharge scenario')
    return dict(initial_w=from_v**2/resistance_ohm,
                time_s=resistance_ohm*c_f*log(from_v/to_v),
                dissipated_j=.5*c_f*(from_v**2-to_v**2))


def report():
    lines = ['# Task 3 component sensitivity — not an approved rating', '',
             'Inputs: eta90% (Task 2), cap12–22.05 V, bus22/26 V, request80/120 W,',
             'cap clamps8/12 A, hot RDS factor1.6, winding80°C, tr+tf40 ns.',
             'L effective = nominal ×0.8 tolerance ×0.8 assumed DC bias.',
             'Neither temperature nor bias factor is predicted or guaranteed.', '',
             '| FET / L / fs | Bus / cap open / request | Output W | Cap A | IL rms / peak A | Ripple A pp | FET conduction / overlap / gate W | L Cu / shunts W | Subtotal W |',
             '|---|---|---|---|---|---|---|---|---|']
    candidates = (Candidate(), Candidate(l_h=15e-6, dcr_max_ohm=.0124),
                  Candidate(mosfet='CSD18563Q5A', rds_max_ohm=.0068, qg_c=20e-9))
    for c in candidates:
        for fs in (100e3, 200e3):
            for bus, cap in ((22, 22.05), (26, 12)):
                for request, limit in ((80, 8), (120, 12)):
                    p = point(c, bus, cap, request, limit, fs)
                    lines.append(f'| {c.mosfet} / {c.l_h*1e6:g} uH / {fs/1e3:g} kHz | '
                                 f'{bus} / {cap} / {request} | {p["output_w"]:.3f} | '
                                 f'{p["cap_a"]:.3f} | {p["il_rms_a"]:.3f} / {p["il_peak_a"]:.3f} | '
                                 f'{p["ripple_a"]:.3f} | {p["conduction_w"]:.3f} / '
                                 f'{p["overlap_w"]:.3f} / {p["gate_w"]:.3f} | '
                                 f'{p["winding_w"]:.3f} / {p["shunts_w"]:.3f} | {p["subtotal_w"]:.3f} |')
    lines += ['', 'Subtotal excludes core/Coss/Qrr/deadtime/connector/aux losses.',
              'Partial efficiency is an optimistic accounting result, not a converter target.',
              'Near-equal rail switching and startup/regen/short are outside this CCM model.',
              'Inductor ripple is not directly the capacitor-module port ripple; DC-link and PWM require separate validation.',
              '12 V / 120 W request is clipped to106.272 W before component loss assessment.', '',
              '## RC scenarios (Assumption, not component values)', '']
    for r in (47, 100):
        p = precharge(26, 470e-6, r)
        lines.append(f'- Empty local470 uF link,26 V,R={r} ohm: I0={p["initial_a"]:.3f} A, '
                     f'P0={p["initial_w"]:.3f} W,Eres={p["resistor_energy_j"]:.4f} J, '
                     f't95={p["time_s"]:.4f} s. Loads/parasitics/fault pulse not modeled.')
    for r in (100, 1000):
        p = bleed(BANKS[0].c_f, 22.05, 1, r)
        lines.append(f'- Bank22.05→1 V,R={r} ohm: P0={p["initial_w"]:.3f} W, '
                     f'E={p["dissipated_j"]:.3f} J,t={p["time_s"]:.1f} s. '
                     '1 V is inspection reference, not approved service-safe threshold.')
    return '\n'.join(lines)+'\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    output = report()
    if args.write_report:
        Path(__file__).with_name('component_results.md').write_text(output, encoding='utf-8')
    else:
        print(output)
