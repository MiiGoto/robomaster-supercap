"""Selected assembly/protection bounds in SI units, not measured performance."""
from math import log
from pathlib import Path
from component_budget import Candidate,point

def calculate():
    cbank=50/9*1.3
    link_c=6*470e-6
    link_c_max=link_c*1.2+2*2.2e-6*1.1
    trip=3.288*10000/(35700+10000)/(.003*20)
    leff=22e-6*.8*.8
    delay=.5e-6
    # +-7% is a provisional aggregate error budget, not a measured calibration.
    max_fault=trip*1.07+48/leff*delay
    discharge_r=100*1.01
    discharge_s=cbank*discharge_r*log(22.05/1)
    contact_coil_a=4*.353*1.1
    points=[point(Candidate(gate_v=12),bus,cap,120,9.5,200e3)
            for bus in (22,26) for cap in (12,22.05)]
    assert max_fault<15
    assert discharge_s<2400
    assert 12/2/6*1.3 < 1.995*.8
    assert all(p['il_peak_a']<trip*.93 for p in points)
    return locals()

def report():
    d=calculate()
    return '\n'.join([
      '# Rev A selected protection / assembly limits','',
      '**ASSUMPTION — MUST VERIFY ON PROTOTYPE.** Calculations establish required test criteria, not shutdown, temperature or surge capability.','',
      f'- Six EEUFR1J471/link: {d["link_c"]*1e6:.1f}uF nominal; {d["link_c_max"]*1e6:.1f}uF worst including ceramic tolerance.100R1% t95 worst={101*d["link_c_max"]*log(20):.4f}s; energy at26V={.5*d["link_c_max"]*26**2:.4f}J. Startup timeout3s,delta-V<1V.',
      '- Bulk ripple bound IL/2=6Arms at12A:6parallel and1.3sharing factor gives1.3Arms/cap vs1.995Arms rating at100kHz.20% ripple derating target; verify200kHz multiplier and actual ripple/temperature.',
      f'- OC divider35.7k/10k,3.288V,gain20,3mR: nominal {d["trip"]:.5f}A. Provisional±7% budget; measured actual threshold must fit this interval.',
      f'- Required clearing delay<=0.5us, Vfault<=48V, measured L>=14.08uH through15A: peak bound {d["max_fault"]:.4f}A. Simple dI/dt bound excludes shoot-through/local short/saturation; these need fuse/source interruption. This demanding latency is UNPROVEN; failure requires redesign or tighter current envelope.',
      '- Initial cap average limit9.5A;12A remains eventual design goal. No operation is enabled by this offline model.',
      '',
      '| Bus / rest cap V | Requested / delivered W | Cap A | IL peak A | Partial board loss W |',
      '|---|---|---|---|---|',
      *[f'| {bus}/{cap} |120/{p["output_w"]:.3f} |{p["cap_a"]:.3f} |{p["il_peak_a"]:.3f} |{p["subtotal_w"]:.3f} |' for (bus,cap),p in zip([(22,12),(22,22.05),(26,12),(26,22.05)],d['points'])],
      '',
      f'- Four AEV14012 coils: max planning current {d["contact_coil_a"]:.4f}A,12V power {12*d["contact_coil_a"]:.3f}W. Reserve24W output including electronics; DDR-60L-12 input planning29W at83% efficiency. Referee-point total charge budget=40W+29W+2Wboard aux=71W planning ceiling,not a measured total or rule allowance.',
      '- MINI997 typical melting I2t10A93/15A270/5A25 A2s cannot be used as guaranteed maximum clearing energy. No semiconductor protection assertion from these values.',
      f'- Dump HS25 100R F(+1%),bank+30%C: time22.05->1V={d["discharge_s"]:.3f}s ({d["discharge_s"]/60:.3f}min); bank energy removed={.5*d["cbank"]*(22.05**2-1):.3f}J. Permanent bleed ignored here conservatively.40min acceptance target includes contact/path testing; imbalance and rebound separately checked.',
      '- Service condition: bank AND both local links<1V,every cell magnitude<0.5V,2min rebound check,total residual energy<4J,source isolated and independent meter check. This is a delegated prototype procedure target,not demonstrated safe-service capability.',
      '- Thermal criteria: ambient<=40C/open bench;software FET/L65C and bank50C stop,hardware backup≈69.5/53.7C. Verify hotspot-to-junction/winding lag;target FET junction<100C,winding<90C,bank<55C,connectors<60C. No continuous thermal power claimed.',''])

if __name__=='__main__':
    result=report()
    Path(__file__).with_name('rev_a_limits_results.md').write_text(result,encoding='utf-8')
    print('PASS: Rev A limit/energy/ripple/OC calculations; report written. Physical acceptance remains unverified.')
