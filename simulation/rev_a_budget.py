"""Selected Rev A arithmetic; assumptions, not hardware performance prediction."""
from math import log
from pathlib import Path
import argparse
from component_budget import Candidate, point, precharge, bleed
from power_budget import BANKS,charge

SELECTED=Candidate(gate_v=12)  # Qg(max) at10V reused: optimistic at12V, flagged.
FREQUENCIES=(180e3,200e3)
def ntc_temperature(resistance, r25=10000, beta=3977):
    return 1/(1/298.15+log(resistance/r25)/beta)-273.15
def report():
    lines=['# Prototype Rev A selected-candidate calculations','',
           'ASSUMPTION — MUST VERIFY ON PROTOTYPE. CSD18540Q5B, XAL1510-223MED22uH,',
           'WSK25123L000FEA3mR; 180/200kHz. CSD18563Q5A /15uH alternatives remain in component_results.md.',
           'Same eta0.9, ESR0.18ohm, L tolerance0.8*bias0.8, hotRDS factor1.6, winding80C, tr+tf40ns.',
           'Driver12V; Qg53nC measured at10V reused as a LOWER-FIDELITY assumption, not a12V bound.',
           'Subtotal excludes core/Coss/Qrr/deadtime/aux/connector and bank ESR; no efficiency guarantee.',
           'Model is single-active-leg CCM; overlap/equal-rail modulation, startup and fault not modeled.','',
           '| fs kHz | bus / rest cap V | request W | delivered W | cap A | bus A | IL RMS / peak A | ripple App | loss subtotal W |',
           '|---|---|---|---|---|---|---|---|---|']
    for fs in FREQUENCIES:
        for bv in (22,26):
            for cv in (12,22.05):
                for power,limit in ((80,8),(120,12)):
                    p=point(SELECTED,bv,cv,power,limit,fs)
                    lines.append(f'| {fs/1000:.0f} | {bv}/{cv} | {power} | {p["output_w"]:.3f} | {p["cap_a"]:.3f} | {p["bus_a"]:.3f} | {p["il_rms_a"]:.3f}/{p["il_peak_a"]:.3f} | {p["ripple_a"]:.3f} | {p["subtotal_w"]:.3f} |')
    lines+=['','## 40W charge-input corner calculation','',
            '| Bus / rest cap V | Actual input W | Bus A | Signed cap A | Stored W | ESR W | Converter W |',
            '|---|---|---|---|---|---|---|']
    for bv in (22,26):
        for cv in (12,22.05):
            ch=charge(BANKS[0],cv,bv,40,8)
            assert abs(ch['input_w']-ch['stored_power_w']-ch['esr_loss_w']-ch['converter_loss_w'])<1e-9
            lines.append(f'| {bv}/{cv} | {ch["input_w"]:.3f} | {ch["bus_a"]:.3f} | {ch["cap_a"]:.3f} | {ch["stored_power_w"]:.3f} | {ch["esr_loss_w"]:.3f} | {ch["converter_loss_w"]:.3f} |')
    lines+=['','At22.05V rest ceiling this model stops charge; cell limits can stop earlier. Power conservation checked in W, signed capacitor charging current is negative.','']
    p=precharge(26,470e-6,100)
    d=bleed(BANKS[0].c_f*1.3,22.05,1,100)
    slow=bleed(BANKS[0].c_f*1.3,22.05,1,10000)
    lines+=['','## Sanity checks and proposed setting arithmetic','',
      f'- Local-link precharge100R/470uF/26V: I0={p["initial_a"]:.3f}A, P0={p["initial_w"]:.3f}W, resistor energy={p["resistor_energy_j"]:.5f}J, t95={p["time_s"]:.5f}s. Loads ignored.',
      f'- Dump100R, +30%C: initial={d["initial_w"]:.3f}W, energy to1V={d["dissipated_j"]:.3f}J, ideal time={d["time_s"]:.1f}s.1V is only proposed inspection/service investigation target.',
      f'- Permanent10k bleed +30%C: initial={slow["initial_w"]:.5f}W, time to1V={slow["time_s"]/3600:.2f}h; OFF is not safe.',
      '- Available nominal ideal useful energy950.5625J; +30%C1235.73125J. Stored total at22.05V1350.5625J nominal. External dump thermally rated separately.',
      '- 12A cell-bank ESR loss=25.92W initially; 2x aging51.84W.1s/30s pulse-only mean=0.864/1.728W, excludes normal current and all other losses.',
      '- WSK2512 1W70C rating is board/ambient dependent.3mR at12A=0.432W; modeled IL RMS≈12.02A gives≈0.433W. Pulse/derating are not yet accepted.',
      f'- IL comparator nominal threshold3.3*10k/(29.4k+10k)=0.83756V -> {3.3*10/39.4/.06:.4f}A with gain20/3mR. Not coordinated maximum fault current.',
      '- Port INA293A1/TLV3202 thresholds: BUS3.3*10/68.7/0.06=8.006A; CAP3.3*10/39.4/0.06=13.959A. Tolerance/offset/delay/overshoot unbudgeted; INA301 rejected for40V absmax versus45.4V TVS clamp.',
      '- Independent TLV4311.24V reference: bus OV221k/10k ->28.644V; bus UV154k/10k ->20.336V; bank OV172k/10k ->22.568V nominal. These are hardware backup proposals, distinct from operating window.',
      f'- Loaded voltage dividers including100k ADC drain: bus36V->{36/(1+66000/(1/(1/5100+1/100000))):.5f}V; cap24.3V->{24.3/(1+66000/(1/(1/6800+1/100000))):.5f}V. Clamp2.7V plus diode drop/mux3.6V need transient test.2uA off-leakage *100k=0.2V proposed bound.',
      '- Current midscale1.65V: BUSgain50 +-8A->0.45..2.85V; CAP/ILgain20 +-20A->0.45..2.85V; ideal12-bit steps5.37/13.43mA. Actual clamp/swing can reduce range.',
      f'- Approximate beta NTC trip including100k ADC load: FET/L->{ntc_temperature(1/(1/1740-1/100000)):.2f}C; BANK->{ntc_temperature(1/(1/3010-1/100000)):.2f}C. Mux OFF removes this load, so threshold is state-dependent; manufacturer R/T calibration and partial-power tests mandatory.',
      '- Fast IL shutdown estimate must include INA293 dynamic response, comparator, logic, latch/AND, driver/gate and Lmin. No guaranteed max latency is inferred from bandwidth or typical delays.',
      '- For a fault: excursion roughly Vfault/Lmin*tclear. At26V/14.08uH, 1us adds1.847A. This is NOT an accepted1us clearing time, and saturation worsens it.',
      '- Qg53nC / bootstrap effective200nF =0.265V charge droop before leakage/bias.470nF nominal needs DC-bias capacitance, duty/refresh and UVLO verification.',
      '- Aux Type3 ripple:12V300kHz, RA1M/CA1nF gives~20mV at24V;3.3V~301kHz, RA475k/CA1nF gives~20mV. CA exceeds10/(fs*RFB_parallel); CB100pF permits provisional settling >=270/52.5us. Datasheet equations only; stability not simulated.',
      '- Peak duration and repetition are adjustable assumptions; existing runtime calculations are not permission for those pulses.','']
    return '\n'.join(lines)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write-report',action='store_true');args=parser.parse_args()
    result=report()
    if args.write_report:Path(__file__).with_name('rev_a_results.md').write_text(result,encoding='utf-8')
    else:print(result)
