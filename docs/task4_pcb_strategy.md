# PCB engineering authorized — 2026-10-04

ユーザーがsurge・OC遮断時間・fuse/接触器協調・熱・放電時間の実測前にPCB配置/配線へ進むことを明示承認した。[現行PCB記録](pcb_rev_a.md)を優先する。未実測の項目はPrototype Assumptionとして保持し、製造/通電/性能保証にはしない。以下の「PCB未承認/開始しない」は過去時点の記録として残す。

## Historical records (preserved)

# Prototype Rev A — 2026-10-04 delegated decisions

ユーザーの委任に基づき、セル監視RAM設定・exact passive選定・外部ベンチ遮断アセンブリ・保護/熱/放電検証基準を[現行選定書](rev_a_design_freeze.md)へ確定した。選定はPrototype Assumption、実測検証は未実施。平均cap電流の初期上限9.5 A、OC約12 A、目標遮断0.5 µs、各link bulk6×470 µF、precharge timeout3 s。12 A/120 Wは後続の検証目標として保持。PCB placement/通電は開始しない。以下の2026-10-03以前の未選定表示は経緯記録であり、この選定書が優先する。

# Prototype Rev A — current status

2026-10-03 JST。**Current: Prototype Rev A schematic only.** Task2 architectureはユーザー採用承認済み。実機条件未確認は[Prototype envelope](../docs/prototype_rev_a_envelope.md)に明示した **ASSUMPTION — MUST VERIFY ON PROTOTYPE** として隔離し、詳細electrical schematicを作成した。部品/保護閾値はprototype候補で性能保証ではない。[現行review](../docs/rev_a_schematic_review.md)と[pinout](../docs/pinout.md)が現在の設計記録。PCB placement/routing、firmware、通電、120W使用許可、競技適合、Task4開始は未承認。以下の旧status/approval pending/skeleton-only記述はhistorical recordであり現在statusではない。

## Current scope

No board outline, placement, routing, zones or copper stackup change in Rev A. Candidate footprint assignment is schematic metadata only. Earlier PCB strategy remains a proposal; do not place until external containment and schematic review are accepted.


## Historical records (preserved)

# Task 4 PCB strategy — proposal before placement

[Review gate](task4_review.md)が未通過。これは将来placementのレビュー資料で、PCB fileへoutline/footprint/netclass/銅箔/routingを実装しない。

## Layer and stack proposal

| Option | Current/return/thermal | Signal / complexity / cost |
|---|---|---|
| 2-layer | 主要電流は短い外層銅箔、GND returnとsignalの競合、thermal面積制約 | 安価だがgate/ADC returnの連続性確保が難しい |
| 4-layer primary proposal | L1 power/local loops、L2 continuousreference、L3 aux/control distribution、L4 lowenergy signals/debug | return/shielding余裕、製造cost増。high currentを無条件に内層へ流さない |

4-layerをAssumptionの第一案とする。実stack/copper thickness/dielectric/manufacturerはTBD。現在PCB skeletonの2Cu-layer指定は未変更。局所SW_NODE下planeの扱いはdevice/layout推奨・寄生C/EMIとreturnの両面でレビューし、無根拠な全面GND splitやstarを作らない。

根拠: TI [critical high-di/dt loops](https://www.ti.com/document-viewer/lit/html/SSZTAE5/GUID-1402DA8B-73DB-44B4-B203-A3AF307A6C45)は両portの高速loopとdv/dt領域の管理、[gate drive/return](https://www.ti.com/document-viewer/lit/html/SSZT533/GUID-8E8A4702-76CD-495F-A121-6F12027C6292)はgateとreturnを近接してloop面積を抑える原理を参考にする。own MCU + discrete driver構成へ原理を適用する案で、LM517x layoutデータをコピーしない。

## Loop and adjacency requirements

- charge: VBUS protection/isolation→busleg→L→capleg→officialmodule→bank。dischargeは逆向き。PWM OFFのbodydiode pathは詳細netで別追跡。
- bus側commutation loop: localbus ceramic→bus HS/LS→localreturn。cap側もlocalcap ceramic→cap HS/LS→return。長いbank cableはlocal ceramicの代替にしない。
- 各driverは対応FET近傍。HO/HS、LO/source-return、bootstrap HB/HS、VDD decouplingの閉loopを短くし、MCUへの距離だけで配置しない。
- Lは両SWnode間を短くする位置を優先し、磁界/熱/重量からADC/CAN/clockと隔離。SW copperは必要以上に広げずthermalをdrain/source銅箔と分けて考える。
- shuntは実power pathに直列、senseはpower pad内側または4terminal sensepadから専用Kelvin pairでampへ。load current returnをsense/referenceへ共用しない。
- MCU/ADC/VREF zoneはSW/Lと分離、fault/break経路の遅延とsense取り回しを同時確認。ADC filterはacquisition条件に合わせる。
- CAN: MCU→transceiver→protection→connector。aux regulatorは第二のnoise source。dump/precharge resistorはcell/NTC/reference/MCUから熱分離。
- bankは機械条件未確定のためoff-board connector interfaceを検討する。bus/cap混同をkeying/housing/retentionで抑え、silkscreenだけに依存しない。

## Rule register (not assigned to empty nets)

| Planned class | Conceptual nets | Required rule source |
|---|---|---|
| POWER_HIGH | VBUS_PWR / VCAP_PWR / INDUCTOR_PWR / POWER_GND | RMS/peak/temperature、copper厚/area/neck/via、faultenergy |
| POWER_HIGH, local SW restriction | SW_NODE_A / SW_NODE_B | 上記 + dv/dt keepout、driver寄生loop |
| GATE | GATE_HA/LA/HB/LB + localreturn | pairloop、driverpin位置、gatecurrent、ringing |
| SENSE | BUS_V_SENSE/CAP_V_SENSE/CURRENT_SENSE/TEMP/VREF | Kelvin、ADC acquisition、noise/return連続性 |
| POWER_LOW | driver rail / +3V3 | auxiliarybudget/decoupling/drop/startup |
| SIGNAL / CAN | PWM/FAULT/BREAK/SWD、CANH/L | boardfab最小rule、timing/termination/ESD |

signal width/clearance、power width/clearance、via drill/pad/plating、edgeclearance、creepageはTBD。manufacturer manufacturing minimaは電気的安全clearanceではない。実max/surge、汚損/湿度/基板材/coat、適用規格が無いので一律数値を設定しない。IPC-2152本文を未検証のためIPC適合trace幅や温度riseを主張しない。

銅箔のohmic sanity checkは R=ρ·l/(w·t)、P=Irms²R、via barrelは A≈π·d·plating、R≈ρ·boardthickness/A。これだけで許容電流/温度を決めない。ρ25°C≈1.72e−8 ΩmをAssumptionとし、長20 mm・厚70 µm・幅5 mmならR≈0.983 mΩ、12 Aで0.142 W、幅2 mmなら2.457 mΩ/0.354 W。via finishedhole0.3 mm/plating25 µm/length1.6 mmならR≈1.17 mΩ、12 A単独なら0.168 W。電流sharing/neck/熱経路を含まないためvia個数・widthの採用値ではない。

## Thermal / mechanical / debug acceptance

FET損失を各HS/LS duty/commutation別に割当て、RθJC→package/銅箔/airflowを評価する。datasheet RθJAを実基板thermal modelとしてそのまま使わない。L winding/core、shunt、connectorcontact、aux、precharge pulse、dump全energyを別heat sourceとして監視。NTC位置は対象のtrend/hotspotlagを測定して決める。requires prototype thermal validation。

board size・outline・4点mount候補・部品座標・keepout距離・connector overhang・heightは未決定。footprint/part freezeとrobot envelope後に決める。未配置のためratsnest/3D collisionレビューはNot performed。

Testpoint計画: GND/+3V3/driver rail/VBUS/VCAP/sense/PWM/BREAK/FAULT。gate/SWはrated differential probeの安全な接触点を確保し、highsideにbench scopegroundを接続しない。debugとserviceで充電bankへ触れない配置を要求する。
