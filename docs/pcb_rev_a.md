# PCB routing complete — 2026-10-07

**Current: Prototype Rev A CAD routing complete.** KiCad10.0.6の正式PCBでnative未接続0、全DRC0 errors/0 warnings、schematic parity0、ERC0 errors/0 warningsを確認した。全331ネット／1524 net-assigned pad recordsの物理接続と、設計manifestの1478 pad/net assignmentsを照合済み。これはCAD接続・規則検証であり、製造リリース、通電許可、120 W性能、競技適合の承認ではない。

一般銅箔間隔0.20 mm、承認済み39 ICの同一部品内Pad/Pad0.15 mmを維持した。新たなDRC除外・No ERC・規則緩和はない。未コミットの`.kicad_pro`設定展開は保持し、functional commitに含めない。詳細は[配線完了記録](pcb_routing_completion.md)を現在の情報源とする。以下は過去時点の記録として保存する。

## Historical records (preserved)

# Routing checkpoint — 2026-10-04

**Routing incomplete.** 保存したPCBは電力7ネットの全パッド接続と、局所GND/一部信号配線を追加したcheckpoint。native未接続 **610本**（239 nets）、寸法・間隔DRC **0 errors/0 warnings**、schematic parity0。元の935本から325本を解消したが、配線完成/製造/通電/性能保証は意味しない。

現在の結果と残りを[配線作業記録](pcb_routing_completion.md)で確認する。以下は以前の経緯を含む。

# Approved fine-pitch clearance — 2026-10-04

ユーザーが同一fine-pitch部品内のパッド間0.15 mm、その他0.20 mm以上を明示承認した。39個の対象ICに同一referenceのPad/Pad例外を設定し、一般銅箔間隔0.20 mmを明示維持した。projectのhard floor0.15 mmは例外を許容するためで、一般ruleを0.15 mmへ緩めてはいない。

独立DRCテスト6件PASS：対象内0.15 mmは許容、0.14 mmは検出、非対象/別部品/pad-to-trackの0.19 mmは検出、非対象0.20 mmは許容。現行PCBの寸法・間隔DRC0 errors/0 warnings、schematic parity0。未配線はCLI報告499件／全ratsnest935本のままで、配線完成や製造承認を意味しない。

以前の自動承認拒否と218件の違反記録は以下に履歴として保持する。

## Historical records before this approval

# Prototype Rev A PCB engineering work

2026-10-04 JST. The user authorized placement/routing **without prior surge, OC latency, fuse/contactor, thermal or discharge measurements**. These are retained as assumptions and unmeasured validation items, not prerequisites for CAD work. Fabrication, energizing, guaranteed120 W operation and competition compliance are not asserted.

## Mechanical and routing envelope

**ASSUMPTION — MUST VERIFY ON PROTOTYPE.** Single bench board315×235 mm,1.6 mm nominal thickness, four copper layers, M3 holes3.2 mm at four corners. The external four AEV contactors, DDR supply, source/cell/fuse assemblies and chassis dump resistors do not fit on or belong to this PCB. This is a bench demonstrator, not a robot mounting envelope.

| Item | Engineering choice | Limitation |
|---|---|---|
| Layers |F.Cu local components/power and local power return;In1.Cu ground reference;In2.Cu and B.Cu signal routing candidates |Actual laminate/copper stackup and vendor process are not released;provisional In1.Cu signal cuts need review |
| Copper budget |Calculate outer70 um,inner35 um as fabrication assumptions |No copper-weight order or ampacity guarantee;board layer count alone does not define copper thickness |
| Default routing |0.25 mm signal,0.20 mm clearance;0.6/0.3 mm through-via |Existing project hard minimum0.20 mm preserved |
| Power target |3 mm trunk width,0.25 mm clearance |Pad necks,layer changes,return paths and via sharing must be audited separately;autorouting cannot establish current capacity |
| Auxiliary target |0.7 mm trunk for3.3 V,driver and actuator rails |Shared actuator segments must account for all four coil currents |
| Source interfaces |32 named solder wire lands;power candidates2 mm drill,low-energy0.9 mm drill |Fixture cable clamps provide strain relief;these are not keyed plug connectors. Polarity/continuity inspection essential |
| Switch nodes |Five In1.Cu copper/track keepouts around drain/IL switch regions |Not a validated EMI solution;keepout effects on returns must be reviewed |
| Protection |All previous hardware inhibit/latch/default-OFF paths retained |Physical trip delay,shoot-through containment and fault energy remain unmeasured |

## Placement decisions

Four converter MOSFETs and two half-bridge drivers are placed around the22 uH inductor. Bootstrap,gate resistors,gate clamps and mandatory pulldowns are nearby. Six electrolytics and two ceramics per link sit in the power region. Bus/cap/IL amplifiers are placed near their respective shunts. Hardware logic,controller,cell monitor,auxiliary converters,CAN and dump control occupy separate functional regions.

Shunt pads2/3 now use six dedicated `BUS/CAP/IL_KELVIN_P/M` nets. They must route to sensing inputs without carrying power current. Pads1/4 retain power nets;their internal relationship is the four-terminal resistor,not a PCB short. External components are explicitly `on_board=no`;each board/harness boundary net has an actual land.

The generated full-board top render was inspected for block separation and gross mechanical placement. This does not prove gate-loop inductance,clearance compliance,thermal suitability or routing quality. The generous board outline leaves room for review-driven moves and should not be presented as a miniaturized final product.

## Rule mismatch and approval review

Fine-pitch standard-library footprints include0.15 mm pad-to-pad gaps,which conflict with the existing0.20 mm hard minimum. A proposed hard minimum0.125 mm was rejected by automatic approval review because the specific margin change lacked approval. **No reduction was applied;no DRC exclusions were added.** Resolve through explicit review of process capability,package lands and the project's minimum rule before manufacture. Do not ignore these errors or reduce unrelated power clearances.

## Reproduction

Use KiCad10.0.6 bundled Python for PCB scripts and the newer workspace Python for the existing schematic generator. `build_rev_a_pcb.py` refuses overwriting populated boards unless its generated placement is explicitly rebuilt. Preserve later manual edits:do not blindly rerun generators. Then `refine_rev_a_placement.py`, `prepare_rev_a_routing.py`, offline Freerouting2.4.1, `import_rev_a_routing.py`, and actual KiCad DRC. Java25 and the router reside only under ignored `.local/pcb-tools`;no installer or system settings are modified. Analytics/API/MCP are disabled for routing. No public routing service receives the board.

Validation and remaining connections are recorded in [PCB validation](pcb_rev_a_validation.md). No Gerber/drill/fabrication release is produced.
