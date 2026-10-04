# Prototype Rev A schematic review

2026-10-03 JST. **Prototype Rev A schematic only.** Architecture is adopted; prototype numeric settings are **ASSUMPTION — MUST VERIFY ON PROTOTYPE**, thresholds **PROVISIONAL — MUST VALIDATE**. Unknown physical conditions no longer prohibit drawing circuits. Energizing, 120 W operation, continuous thermal limits, final OC, service-safe time and interruption capability remain unapproved. No PCB placement/routing or firmware was performed.

## Selected candidates and reasons

| Block | Primary / alternative | Decision and limitations |
|---|---|---|
| MOSFET | CSD18540Q5B / CSD18563Q5A | 60 V both. Primary max25C RDS2.2mΩ vs6.8mΩ at10V, favors conduction at12A. Qg max53 vs20nC; Qrr typ145 vs63nC at different tests. Primary pays switching/driver losses. Hot multiplier1.6 is an assumption. SOA pulse conditions and actual VDS/VGS must be checked; 60V is not proved sufficient. SON5x6 needs thermal copper; datasheet package current is not board current. |
| Driver | UCC27282DRCR / UCC27211A | Primary DRC10+EP provides EN/interlock plus UVLO. Secondary needs additional enable/interlock design. 12V rail; external HI/LI AND kill, EN pull-down, independent rail11.23..13.64V backup window, HRTIM FLT1. Internal interlock does not replace timer deadtime. |
| Inductor | XAL1510-223MED / -153MED | Select22µH at200kHz (180–200 exploration). 100kHz worst ripple4.45App exceeds3App goal;200kHz2.23App under assumed14.08µH lower L.22µH DCRmax16mΩ, Isat18.7A at30% drop, thermal10.5/14A at20/40C rise.15µH lowers DCR12.4mΩ but increases ripple. Core loss and saturation at heat remain unmodeled. |
| Signed sensing | INA240A2 bus / A1 cap and IL, 3mΩ WSK25123L000FEA | REF1=3.3, REF2=GND gives1.65V zero. Kelvin four terminals,1W at70C conditional on mounting,1% resistance,3mΩ TCR75ppm/C. Ideal bus±8A, cap/IL±20A measurement; amplifier swing and settling narrow these. |
| Fast OC | INA293A1 opposing pairs on all3 shunts + TLV3202 | Six dedicated front ends, CM−4..110V; separate from INA240/ADC. INA301 was rejected:40V absolute CM max below SMBJ28A rated45.4V clamp. Thresholds bus±8.006A, cap/IL±13.959A nominal. No guaranteed fault clearing time from bandwidth. |
| Cell monitor | BQ7694204PFBR / BQ76952 | Primary3–10cells fits9S; alternative3–16 adds unused inputs. SPI/CRC, REG1 default3.3V, programmable autonomous cell protections/open-wire and internal switched-passive balancing. **Supercap-specific configuration is NOT implemented**; Li-ion defaults cannot protect2.7V cells. Readback/provisioning is a commissioning gate. |
| Temperature | NTCLE100E3103JB0 | Three10k/β3977 probes, MOSFET area/inductor/bank. Hardware hot/short/open windows plus ADC. Approximate loaded thresholds69.5C /53.7C; calibration, sensor lag and hotspot mapping mandatory. Probe header replaces fitted NTC. |
| Aux | LM5164DDAR x2 | Bus-fed12V driver and3.3V MCU,100V IC input (not board surge guarantee). Type3 ripple injection,300kHz class,68/47µH, PG outputs and supervisor. External actuator12V is a separate unresolved assembly supply, not the1A gate-bias regulator. |
| CAN | SN65HVD230DR |3.3V Classic CAN, RS default standby, selectable120Ω. ID/rate/timing/ESD system integration TBD. Does not bypass referee power cutoff. |

## Actual electrical power path

BUS_RAW → candidate10A fuse/TVS → external NO isolation → (100Ω precharge NO path || NO bypass) → signed bus shunt → BUS_LINK.
Four CSD18540: AH D=BUS_LINK S=SW_NODE_A; AL D=SW_NODE_A S=GND; BH D=CAP_LINK S=SW_NODE_B; BL D=SW_NODE_B S=GND.
SW_NODE_A →3mΩ Kelvin IL shunt→22µH→SW_NODE_B. CAP_LINK → signed cap shunt→ cap precharge/bypass→external NO isolation→candidate15A fuse→9S bank.
Each link has470µF/63V bulk plus two2.2µF/100V1210 ceramic candidates; **bulk exact product/ripple capability is TBD**. External bank/cables/connectors/contacts are assembly boundaries, not a released onboard BOM.

Charge: bus→cap; when cap below bus, buck bus leg; if cap above bus, boost opposite leg. Assist reverses current and active-leg role. Near equal voltages requires reviewed modulation; no100% high-side hold with bootstrap. PWM details/control stability and regenerative acceptance are not implemented. Firmware must refuse unreviewed regen; diode/transient current still requires physical containment.

## Gate and protection circuits

Each driver has470nF bootstrap (effective≥200nF proposal),1µF+100nF supply decoupling,4.7Ω gate series resistors, mandatory10k G–S and15V clamp. DNI2.2Ω+diode separate turn-off and10Ω/1nF snubbers are tuning options; mandatory protection is never DNI.
Fast OC/current windows + independent bus/bank/driver voltage windows + three thermal windows + rail PG/supervisor + external200ms-typ watchdog + monitor DCHG/DDSG + commissioning valid + referee permit → combinational inhibit → SN74LVC1G74 asynchronous CLEAR → latched permit → four PWM AND gates and both driver EN. NRST clears latch. Explicit ARM rising edge required; fault disappearance does not rearm. Same fault enters PA12 HRTIM FLT1. Fast PWM input kill is primary; driver EN typ latency alone is not a short-circuit guarantee.
GPIO float/reset pulls requests LOW; unpowered driver output behavior and partial-rail logic must be measured. A watchdog heartbeat from an unconditional timer would hide crashes: future foreground firmware must qualify it with health/CAN lease. No firmware exists yet.
Shunts, references and rails are shared failure points. Local same-leg shoot-through can bypass port/IL shunts; interlock, deadtime and independently coordinated fuse/DC disconnect remain necessary. Comparator offsets, supply tolerance, recovery/blanking and current excursion are not yet a certified protection budget.

## Voltage / partial-power review

Bus/raw:2x33k top,5.1k bottom; cap/raw:2x33k,6.8k;4.7nF filtering.100k ADC-side drain loads dividers; use loaded transfer, not unloaded gain. Independent bus/bank-fed TLV4312.703V shunt clamp plus BAT54H clamps prevents intentional clamp to dead MCU VDD. Current/temp ADC channels also use TMUX1511 powered-off isolation.
TMUX1511 off protection is only≤3.6V; source/clamp diode tolerance and power sequences must stay below that. Max2µA off leakage times100k is0.2V estimate; measured injection into unpowered MCU and ADC error budget remain required. Source-powered SPI/ALERT also disconnect when either bank REG1 or MCU rail is missing; SN74LV1T34 shifts initial1.8V monitor MISO to3.3V. This is not galvanic isolation.

## Cell configuration contract

9S uses VC1..VC8 then VC10, VC9 tied VC8; enable mask0x02FF, unused channel9 disabled. Input taps each1k/1W and100nF adjacent filters. **Source-side harness resistors/short protection before the connector remain mandatory external work.** Simple raw taps are never MCU ADC connections.1k limits internal passive balancing; about1.2mA near2.45V cannot correct arbitrary charge mismatch at high charge current. Charge taper/inhibit and imbalance response required.
Before setting MON_CONFIG_VALID: configure/read back COV proposal2.55V, normal2.45V, CUV proposal1.2V (useful bank12V separately), channel mask, DCHG/DDSG ACTIVE-HIGH permits mapped to autonomous faults, SPI CRC, open-wire diagnosis and passive-balance constraints. Quantization/accuracy/hysteresis/delays require TRM-based implementation and test. OTP plan/power-cycle test TBD. DCHG/DDSG pull-down and invalid commissioning prevent arm; **GPIO-valid alone does not prove correct configuration**. SRP/SRN grounded, so BQ current protections cannot be relied on. TS dummy10k are commissioning options, not actual temperature probes; mask/control policy must explicitly use external thermal protection.
BQ minimum5V bank supply prevents normal startup from an empty bank. Dedicated energy-limited bank commissioning must precede normal use; resistor precharge is only for local links, not charging9S from0V.

## Body-diode and single-fault review

N-channel body diode is S→D. Healthy all-OFF bridge blocks steady positive rail-to-rail flow, but is not galvanic isolation and cannot extinguish arbitrary inductor/transient energy.

| Condition | Path / required response | Unresolved acceptance |
|---|---|---|
| A bus OFF, bank charged | Bus-fed aux dies, gate/contacts default OFF; bank monitor/LED/bleed remain. IL decay may feed link diode. | Leakage, contact welding, external interfaces and rebound measurement. |
| B bus ON, MCU OFF/reset | Requests pulled LOW, supervisor/latch inhibit; raw aux alive. | Floating/startup/glitch and monitor-permit power ordering. |
| C driver unpowered | EN/HI/LI low and G–S resistors discharge gates; no bootstrap refresh. | Miller turn-on, HS negative spike, discharge rate with unpowered IC. |
| D one FET short | High-side short connects that rail through L and opposite high-side body diode to other rail; low-side short grounds its node, opposite active high side can feed L short; same-leg complementary ON gives direct link short. | PWM cannot remove short. Source+bank external interruption and DC fuse coordination NOT approved. |
| E one FET open | Current commutates through remaining diode/avalanche paths; command/current disagreement should latch. | Diode heat/VDS spikes, detect latency, actual failed-open diode behavior. |
| F aux supply failure | Supervisor/PG/watchdog/window revoke PWM/contacts. Switched dump may become unavailable. | Permanent bleed + independent service tool, partial rail/backfeed, stuck driver and welded contact remain. |

## Precharge, discharge, isolation boundary

Separate local bus/cap470µF links each use100Ω AC05 candidate resistor and NO precharge contact, bypass NO contact, plus upstream NO isolation.26V ideal pulse0.159J,6.76W initial; ΔV<1V and1s timeout proposals. Contact feedback, pulse/cold/startup tests and software interlocks not implemented. Latched permission also gates all six contact commands: fault disappearance alone cannot reclose them. Startup arms the latch with MCU_GATE_REQUEST still LOW, then precharges, checks feedback and only finally requests PWM. Fault inhibits coils but welded bypass requires separate upstream isolation.
Permanent10k/1W bleed plus normally-OFF100Ω HS25 chassis dump MOSFET path, thermally qualified command. +30%C dump to1V≈37.2min,1752J; bleed≈62h. HS25 rating needs specified mounting/derating. Bus aux loss removes active dump. Bank-powered red LED does not work at1V: darkness is NOT safe. Meter every cell/link/bank, rebound and residual energy; service-safe criterion remains unapproved.
AEV14012 is only an external DC contactor candidate (120A catalog /12V coil), oversized and not a proven bidirectional interrupter for this assembly. Six contact instances require an external bus-derived ACTUATOR_12V supply whose coil budget/startup/UVLO and release are TBD; no such supply is implemented onboard. Flyback diode slows release. Fuse58V candidates have no approved I²t/breaking coordination. Manual source/bank service disconnect and branch faults need independent review. **These assembly boundaries prohibit fabrication/energizing release.**

## Validation record

See [pinout](pinout.md), [envelope](prototype_rev_a_envelope.md), [selected arithmetic](../simulation/rev_a_results.md).
KiCad10.0.6 real netlist/ERC, not empty-skeleton ERC: Errors0/Warnings0;467 exported components,329 nets,1440 pin/net matches and25 independent inhibit checks. Full evidence and limitations are in [validation record](rev_a_validation.md). No No-ERC markers. Explicit NC pins are intentional unused pins. PWR_FLAG only annotates source rails, not a safety bypass. All generated components have original symbol pin tables. Candidate footprint pad numbers audited against installed KiCad library; physical dimensions/land tolerance and every passive exact part remain independent-review gates.
Visual inspection of whole hierarchy and exact local supply/power/kill nets plus exported connectivity audit checks topology; this does not verify dynamic behavior. No PCB was edited. Firmware, monitor configuration image, external interruption assembly and thermal proof remain unfinished.
