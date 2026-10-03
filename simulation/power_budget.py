"""SI-unit, quasi-static budgets; no switching, thermal or safety certification."""
from dataclasses import dataclass, replace
from math import sqrt
from pathlib import Path
import argparse


@dataclass(frozen=True)
class Bank:
    name: str
    cells: int
    cell_f: float
    cell_rated_v: float
    cell_esr_ohm: float
    v_min: float
    v_max: float
    normal_a: float
    peak_a: float
    eta: float = 0.90  # Converter only, excludes bank ESR and auxiliary load.
    capacitance_factor: float = 1.0
    esr_factor: float = 1.0

    def __post_init__(self):
        if (self.cells < 1 or self.cells != int(self.cells) or
                self.cell_f <= 0 or self.cell_rated_v <= 0 or
                self.cell_esr_ohm < 0 or self.capacitance_factor <= 0 or
                self.esr_factor <= 0 or not 0 < self.eta < 1 or
                not 0 < self.v_min < self.v_max < self.cells*self.cell_rated_v or
                not 0 < self.normal_a <= self.peak_a < 15):
            raise ValueError('Invalid scenario; not an approved operating limit')

    @property
    def c_f(self):
        return self.cell_f / self.cells * self.capacitance_factor

    @property
    def r_ohm(self):
        return self.cells * self.cell_esr_ohm * self.esr_factor

    def energy_j(self, voltage):
        return 0.5 * self.c_f * voltage**2

    @property
    def usable_j(self):
        return self.energy_j(self.v_max)-self.energy_j(self.v_min)

    @property
    def rule_nominal_j(self):
        # Rating, NOT derated operating voltage, and NOT aged capacitance.
        return self.cells * 0.5*self.cell_f*self.cell_rated_v**2


BANKS = (
    Bank('A SCC50 / 9S', 9, 50, 2.7, .020, 12, 22.05, 8, 12),
    Bank('B HV60 / 7S', 7, 60, 2.7, .018, 8, 17.15, 5.7, 12),
    Bank('C HV100 / 4S', 4, 100, 2.7, .012, 5, 9.8, 11.2, 12),
)
BUS_V = (22.0, 24.0, 26.0)  # Source-input evidence; converter-terminal assumption.
NORMAL_OUTPUT_W = 80.0
PEAK_OUTPUT_W = 120.0
CHARGE_INPUT_W = 40.0


def discharge(bank, v_open, bus_v, requested_w, limit_a):
    """Lower-current stable root, clipped before ESR maximum power point."""
    if v_open <= 0 or bus_v <= 0 or requested_w < 0 or limit_a <= 0:
        raise ValueError('Positive volts/limit and nonnegative power required')
    r = bank.r_ohm
    stable_limit = min(limit_a, v_open/(2*r)) if r else limit_a
    available_w = bank.eta*stable_limit*(v_open-r*stable_limit)
    output_w = min(requested_w, available_w)
    terminal_w = output_w/bank.eta
    # Rationalized quadratic root avoids cancellation for small ESR/power.
    current = (2*terminal_w/(v_open+sqrt(max(0, v_open*v_open-4*r*terminal_w)))
               if terminal_w else 0)
    terminal_v = v_open-current*r
    esr_loss = current*current*r
    converter_loss = terminal_w-output_w
    return dict(cap_a=current, bus_a=output_w/bus_v, terminal_v=terminal_v,
                output_w=output_w, cap_power_w=v_open*current,
                esr_loss_w=esr_loss, converter_loss_w=converter_loss,
                limited=output_w < requested_w-1e-9)


def charge(bank, v_open, bus_v, input_w, limit_a):
    if v_open < 0 or bus_v <= 0 or input_w < 0 or limit_a <= 0:
        raise ValueError('Invalid charging point')
    available = bank.eta*input_w
    r = bank.r_ohm
    if not r and not v_open:
        raise ValueError('Ideal zero-volt charging has no finite power solution')
    current = (2*available/(v_open+sqrt(v_open*v_open+4*r*available))
               if available else 0)
    # Conservative bank terminal ceiling; per-cell protection can stop sooner.
    voltage_limit_a = max(0, (bank.v_max-v_open)/r) if r else (limit_a if v_open < bank.v_max else 0)
    current = min(current, limit_a, voltage_limit_a)
    actual_input = current*(v_open+current*r)/bank.eta
    return dict(cap_a=-current, bus_a=actual_input/bus_v,
                stored_power_w=v_open*current, esr_loss_w=current*current*r,
                converter_loss_w=actual_input*(1-bank.eta), input_w=actual_input,
                terminal_v=v_open+current*r)


def runtime(bank, requested_w, limit_a, dt_s=.002):
    """Fixed step energy integration, exact step bookkeeping to the lower cutoff.

    ESR modeled algebraically; open-circuit energy decreases by Vopen*I*dt.
    Last step shortened; clipping means output may fall below requested power.
    Leakage/auxiliary load ignored: durations are optimistic planning estimates.
    """
    if requested_w <= 0 or dt_s <= 0:
        raise ValueError('Positive power and timestep required')
    e, cutoff = bank.energy_j(bank.v_max), bank.energy_j(bank.v_min)
    elapsed = output = esr = converter = limited_time = 0.0
    while e > cutoff+1e-10:
        point = discharge(bank, sqrt(2*e/bank.c_f), 24, requested_w, limit_a)
        step = min(dt_s, (e-cutoff)/point['cap_power_w'])
        e -= point['cap_power_w']*step
        elapsed += step
        output += point['output_w']*step
        esr += point['esr_loss_w']*step
        converter += point['converter_loss_w']*step
        limited_time += step if point['limited'] else 0
    return dict(duration_s=elapsed, output_j=output, esr_j=esr,
                converter_j=converter, limited_s=limited_time,
                conservation_error_j=bank.usable_j-output-esr-converter)


def report():
    lines = ['# Initial power-budget results', '',
             '2026-10-03; generated by power_budget.py. All power/current limits are Assumption.',
             'Source-input 22–26 V is official; same range at converter terminals is unverified.',
             'η=90% excludes bank ESR/auxiliary; no transient/temperature model. Runtime is not a peak-duration rating.', '',
             '| Bank | Ceq F | Rated energy J | +30% rated J | Usable J | 80 W duration s | 120 W duration s |',
             '|---|---|---|---|---|---|---|']
    for b in BANKS:
        normal, peak = runtime(b, NORMAL_OUTPUT_W, b.normal_a), runtime(b, PEAK_OUTPUT_W, b.peak_a)
        lines.append(f'| {b.name} | {b.c_f:.6f} | {b.rule_nominal_j:.3f} | {b.rule_nominal_j*1.3:.3f} | {b.usable_j:.4f} | {normal["duration_s"]:.3f} | {peak["duration_s"]:.3f} |')
    lines += ['', 'Durations include current clipping: requested power is not guaranteed throughout.',
              '', '## Primary A: four corners, both power directions', '',
              '| Vbus V | Vcap open V | Request assist W | Delivered W | Icap A | Ibus A | ESR W | Converter W | Charge40W request Icap A | Charge actual Ibus A |',
              '|---|---|---|---|---|---|---|---|---|---|']
    a = BANKS[0]
    for bus in (BUS_V[0], BUS_V[-1]):
        for cap in (a.v_min, a.v_max):
            for power, limit in ((NORMAL_OUTPUT_W,a.normal_a),(PEAK_OUTPUT_W,a.peak_a)):
                d, c = discharge(a,cap,bus,power,limit), charge(a,cap,bus,CHARGE_INPUT_W,a.normal_a)
                lines.append(f'| {bus:g} | {cap:g} | {power:g} | {d["output_w"]:.3f} | {d["cap_a"]:.3f} | {d["bus_a"]:.3f} | {d["esr_loss_w"]:.3f} | {d["converter_loss_w"]:.3f} | {c["cap_a"]:.3f} | {c["bus_a"]:.3f} |')
    lines += ['', '## Primary A energy accounting', '',
              '| Condition | Duration s | Bus energy J | Bank ESR J | Converter loss J | Limited time s | Conservation error J |',
              '|---|---|---|---|---|---|---|']
    for label, b, p, limit in [('normal',a,80,a.normal_a),('peak request',a,120,a.peak_a),
                              ('aged sensitivity C70% / ESR200%',replace(a,capacitance_factor=.7,esr_factor=2),80,a.normal_a)]:
        t=runtime(b,p,limit)
        lines.append(f'| {label} | {t["duration_s"]:.3f} | {t["output_j"]:.3f} | {t["esr_j"]:.3f} | {t["converter_j"]:.3f} | {t["limited_s"]:.3f} | {t["conservation_error_j"]:.2e} |')
    lines += ['', 'Voltage versus remaining usable energy: V=sqrt(Vmin²+f(Vmax²−Vmin²)).',
              f'A: 0%={a.v_min:.3f} V, 50%={sqrt((a.v_min**2+a.v_max**2)/2):.3f} V, 100%={a.v_max:.3f} V.',
              'SOE=clip((V²−Vmin²)/(Vmax²−Vmin²),0,1). Unlike battery SOC it is an energy fraction.',
              'Estimate from resting/ESR-corrected voltage and calibrated C; cell constraints override aggregate SOE.',
              'Charging is clipped by bank terminal ceiling: at Vmax charging is OFF; per-cell limits can stop earlier.',
              'Charge runtime requires taper, cell balancing and referee budget; E/(ηP) is only a lower-bound planning estimate.', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args=parser.parse_args()
    if args.write_report:
        Path(__file__).with_name('results.md').write_text(report(),encoding='utf-8')
        print('Wrote simulation/results.md')
    else:
        print(report())
