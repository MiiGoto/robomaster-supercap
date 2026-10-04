# Prototype Rev A validation record

2026-10-03 JST, schematic-only review. No physical prototype test, firmware execution, PCB placement, DRC change or performance acceptance.

| Check | Result | Scope / limits |
|---|---|---|
| KiCad10.0.6 schematic load / PDF export |15 pages, original package-box symbols and label-connected electrical wires |Hierarchy + representative auxiliary/controller drawings inspected; every schematic pin/net audited by export. Does not certify readability of every pin at full-sheet scale or dynamic operation. |
| ERC, report2026-10-03T20:15:57 |**Errors0, Warnings0** |467 actual non-flag components; not an empty skeleton. No No-ERC markers. Explicit unused pins use NC. |
| Existing project rule exclusions |global label once / four-point junction / SPICE model / footprint-filter mismatch ignored |Preexisting KiCad setting expansion preserved; no settings altered to suppress violations. Default-excluded checks are disclosed; netlist audit adds connectivity/pad-number review. |
| Real KiCad exported netlist |467 components,329 nets,1440 pin/net entries matched to original manifest |Rejects empty export, duplicate references and disconnected intended global nets. |
| Protection logic audit |25 independent inhibit inputs, unarmed/reset, four PWM outputs and contact permit |Boolean topology only, no analog response/latency/metastability/partial-power guarantee. Comparator thresholds are provisional. |
| Candidate footprint audit |All assigned library footprint pad sets match original symbol pin sets |22 external/candidate components deliberately have no footprint. Physical dimensions/tolerances, exact passive products, thermal lands and assembly orientation remain human-review gates. |
| Calculation tests |8 existing physics tests PASS |SI units, power/energy conservation, RC energy, ripple scaling, RMS/loss accounting, current limits and integration convergence; not switching simulation. New40W charge-corner report also asserts power conservation. |
| Publication audit |No detected secret/private-email/broken local links or unexpected candidate file types |Original project symbols/JSON/code only. No manufacturer PDFs/images or copied external schematic/PCB added; PDFs used locally are ignored. Manual provenance review completed for added original files; license grant for project still owner TBD. |
| User local configuration |.kicad_pro SHA256 F57C810156A5CC7BCFA1870017D52E1A7A21E563FB546BA8B99A5B5D11F136BB |Unchanged from start of this task, remains unstaged. |
| PCB |SHA256 B82172E9D8465485C0742FFB5424F7B47D347219CB7DAEC1D8A3D129AD94B657 |Unchanged empty board. No placement/routing/zone/outline updates. |

## Review corrections made

- Initial malformed generated instance nesting caused empty KiCad loads; those initial ERC results were rejected. Strict parsing/component-count checks and real export audit now prevent that false pass.
- Off-grid wires/labels and missing diagnostic endpoints were corrected, not hidden by No-ERC.
- Fault-clear logic pin assignment was corrected and tested with independent inhibit drops.
- INA30140V absolute input limit conflicted with TVS45.4V rated clamp; replaced port fast front ends with already selected INA293 plus external comparator windows.
- TMUX powered-off protection is3.6V, not the powered-on5.5V input range.100k drain replaced1M so2µA max off leakage gives0.2V estimate; loaded-divider/NTC arithmetic updated.
- Initial1.8V BQ MISO needs level translation; added bank-powered SN74LV1T34 and rail-qualified SPI switches.
- DCU logic packages use2.3x2mm/0.5mm pitch, not DGK3x3mm/0.65mm; corrected candidate footprints after package-dimension review.
- Contact commands now require latched permit, preventing automatic contact reclosure merely when fault inputs recover.

## Release blockers and next review

The schematic is reviewable but is not a fabrication/energizing release. Independently review original symbols, datasheet terminals, candidate land geometry, all body-diode paths and the shared-fault analysis. Complete external source/bank interruption assembly (actuator supply/coil budget/fuse coordination/manual disconnect/source tap protection), exact local capacitors/passives, BQ supercap provisioning/readback and MCU boot/reset configuration. Only after a reviewed low-energy test plan should surge/ringing, bootstrap, shutdown excursion, power-off injection, thermal duty and discharge/rebound be measured. **Task4 remains closed.**
