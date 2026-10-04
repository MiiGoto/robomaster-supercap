# Prototype Rev A — 2026-10-04 delegated decisions

ユーザーの委任に基づき、セル監視RAM設定・exact passive選定・外部ベンチ遮断アセンブリ・保護/熱/放電検証基準を[現行選定書](rev_a_design_freeze.md)へ確定した。選定はPrototype Assumption、実測検証は未実施。平均cap電流の初期上限9.5 A、OC約12 A、目標遮断0.5 µs、各link bulk6×470 µF、precharge timeout3 s。12 A/120 Wは後続の検証目標として保持。PCB placement/通電は開始しない。以下の2026-10-03以前の未選定表示は経緯記録であり、この選定書が優先する。

# Prototype Rev A — current status

2026-10-03 JST。**Current: Prototype Rev A schematic only.** Task2 architectureはユーザー採用承認済み。実機条件未確認は[Prototype envelope](../docs/prototype_rev_a_envelope.md)に明示した **ASSUMPTION — MUST VERIFY ON PROTOTYPE** として隔離し、詳細electrical schematicを作成した。部品/保護閾値はprototype候補で性能保証ではない。[現行review](../docs/rev_a_schematic_review.md)と[pinout](../docs/pinout.md)が現在の設計記録。PCB placement/routing、firmware、通電、120W使用許可、競技適合、Task4開始は未承認。以下の旧status/approval pending/skeleton-only記述はhistorical recordであり現在statusではない。

## Rev A selection supplement

CSD18540Q5B / UCC27282DRCR / XAL1510-223MED at200kHz selected as prototype candidates. Fast fronts are INA293A1 pairs, not INA301 (40V absmax vs45.4V SMBJ28A clamp conflict). Detailed current review and pin checks are in rev_a_schematic_review.md / pinout.md; old candidate-only statements below are historical.12V driver vs10V Qg model difference remains explicit.


## Historical records (preserved)

# Task 3 component review — conditional shortlist

2026-10-03 JST。採用承認は[gate](task3_review_gate.md)。以下はメーカー一次資料からの候補比較であり、定格freeze・発注BOM・回路完成ではない。surge/peak duty/coolingはユーザー回答「不明」のため、第一候補も条件付き。

## MOSFET

| Candidate | Datasheet evidence at25°C,10 V gate | Tradeoff / conditional choice |
|---|---|---|
| TI CSD18540Q5B | 60 V, RDS max2.2 mΩ, Qg typ41/max53 nC, Qgd typ6.7 nC, Qrr typ145 nC at30 V/28 A/300 A/µs; SON5×6 mm | 第一比較候補。低RDSで大電流conduction有利、Qg/Qrrが大きい。Qg/Qrrのtest条件は実回路と異なる |
| TI CSD18563Q5A | 60 V, RDS max6.8 mΩ, Qg typ15/max20 nC, Qgd typ2.9 nC, Qrr typ63 nC at30 V/18 A/300 A/µs; SON5×6 mm | 低Qgでdriver負荷が小さいが大電流ではconduction増。周波数・duty・冷却で再比較 |

[CSD18540Q5B DS SLPS488B / Apr2017](https://www.ti.com/lit/ds/symlink/csd18540q5b.pdf) §§5.1–5.3はRθJC max0.8°C/W、RθJA max50°C/W(指定1in²/2oz銅箔)、minimum pad125°C/Wを区別する。package/siliconの大きなIDを基板のcontinuous許可値にしない。[CSD18563Q5A DS SLPS444C / Jan2016](https://www.ti.com/lit/ds/symlink/csd18563q5a.pdf) §§5.1–5.3と比較。熱・SOA・diode導通・avalancheの条件確認が必要。avalancheを定常surge吸収手段にしない。

RDSはmax25°Cを基にhot multiplier1.6を**感度仮定**として計算。温度の保証値ではない。switching時間40 nsも仮定で、DSのRG=0立上り時間を実機に流用しない。60 V候補の余裕はVDS実peak=bus/surge+Lstray di/dt+ringingで評価し、30 V競技上限との差だけで合格にしない。driver12 V案とRDS/Qgの10 V test条件の差も再計算する。symbol/footprint/pinは未実装・未照合。

## Gate drivers

| Candidate | Confirmed evidence | Suitability |
|---|---|---|
| UCC27282DRCR ×2 | 3 A halfbridge, VDD recommended5.5–16 V(nom12), input interlock, DRC10-pinだけEN、内部EN250 kΩ pull-down; EN disable typ1.5 µs | 第一比較候補。外部EN bias+killを追加。ENだけのfast OC停止は未保証。HS100 VとHB120 V absoluteを区別 |
| UCC27211ADRM ×2 | 3.7 A source/4.5 A sink, VDD8–17 V, UVLO8 V class、独立HI/LI、VSON8 | EN/interlockの追加外部設計が必要。出力電流の大きさだけで選定しない |

[UCC27282 SNVSAQ5B / May2022](https://www.ti.com/lit/ds/symlink/ucc27282.pdf) §§6.3,6.5,7.3.1, [UCC27211A SLUSBL4D / Jul2024](https://www.ti.com/lit/ds/symlink/ucc27211a.pdf) §§4–7を根拠とする。相互interlockはtimer deadtime設計の代用にならない。default OFFはEN/HI/LI external pull-down、MCU resetとaux UVLO、hardware latchで確保する要求。

OC comparator→latch→HI/LI強制LOW + timer fault、EN LOWを冗長経路とする案。入力killからgate-offまでの最大delay、blanking、comparator/common-mode、latch電源、MOSFET turnoffとdisconnect時間はTBD。driver stuck-highはこの経路でも止まらず両側DC interruptが必要。

bootstrapはCeff≥(Qg(max)+IHB·ton+leak·ton)/ΔV、DC bias/tolerance/UVLO marginを含む。Cの値は最大連続ON時間未確定のためTBD。4-switchの非switching-leg high-sideを100% ONする方式ではbootstrap refreshが必要で、常時ONを仮定しない。deadtime・gate resistor・GS抵抗・zener・DNI snubberは波形とfault budgetに基づき後で設計する。

## Inductor

| Candidate | Nominal / DCR max25°C | Isat / Irms25°C reference | Conditional use |
|---|---|---|---|
| XAL1510-223MED | 22 µH ±20%,16 mΩ | 18.7 A at30% L drop;10.5/14 A at20/40°C rise | 第一比較候補。ripple低減有利、12 A域でCu損失・温度上昇が課題 |
| XAL1510-153MED | 15 µH ±20%,12.4 mΩ | 23 A at30% L drop;13/18 A at20/40°C rise | 熱・saturation余裕を比較、ripple増加とのtradeoff |

[Coilcraft Document947 revised05/04/26](https://www.coilcraft.com/getmedia/cd1cef27-13f0-4568-8894-f7311475209b/xal1510.pdf) pp1–3。Irmsは指定温度上昇の参考値でabsolute maxではなくland/airflow依存。Isatはtyp25°Cの30%低下点。両方ともDC bias・温度curveを使い有効Lとhot saturationを確認しない限り採用確定しない。

計算はΔIL=Vlow(1−Vlow/Vhigh)/(L_eff fs)、IL_rms²=IL_avg²+ΔIL²/12。22 µHがtolerance−20%、さらに仮定bias−20%で14.08 µHになった場合、26 V bus/12 V open bank/12 Aでは100 kHzでripple4.344 A、ILpeak14.172 A、200 kHzで2.172 A/13.086 A。100 kHzならTask 2目標3 Aを超える。この数値はmodule端rippleとは同一ではない。100–200 kHzを維持し、L・PWM・link容量・OC latencyをまとめて再選定する。

## Current sensing review

第一比較候補INA240A1(cap/IL,gain20)、INA240A2(bus,gain50)。[SBOS662C / Dec2021](https://www.ti.com/lit/ds/symlink/ina240.pdf)はbidirectional、CM−4..80 V、VCC2.7..5.5 V、offset max25 µV、gain error max0.2%。400 kHz classでPWM settling/ADC apertureを確認する必要があり独立fast OC comparatorを内蔵しない。

代替[INA241A official product](https://www.ti.com/product/INA241A)はCM−5..110 V、1.1 MHz class、PWM rejectionあり。datasheet取得失敗のため版・full pin/settling/電源仕様の照合はTBDで、具体gain品番は確定しない。各群2候補で調査を停止する。

計算候補3 mΩ Kelvin shunt、Vref1.65 V、ADC3.3 V、出力使用域0.2–3.1 V。cap/IL gain20なら±24.17 A、20 Aで0.45–2.85 V、ideal12-bit13.43 mA/LSB。bus gain50なら±9.67 A、8 Aで0.45–2.85 V、5.37 mA/LSB。shuntは12 Aで0.432 W、IL ripple RMS分を追加。gain/shunt/ADC/reference誤差・hot drift・pulse overload・open/short faultは別budget、抵抗製品/定格/amp保証出力swingは未確定。amp rail到達は正常電流と区別してfault化する。

## Remaining detailed circuits

| Circuit | Next calculation / evidence needed before implementation |
|---|---|
| bus/cap divider | 実surge、ADC powered-off injection、STM32 acquisition/source impedance、R tolerance/temp、RC bandwidth。Task 2の0–36/27 Vは計算rangeで入力耐圧ではない |
| cell monitor/balance | 9S差動監視、open-wire、MCU非依存cell OV、電源断保護、tap保護、単一port規則適合。IC未選定 |
| NTC | MOSFET群/L/bank、NTC/Beta/精度、open/short判定、hotspot/lag、上限温度からerror budgetを引く。回路値TBD |
| aux | 12 V driver candidate +3.3 V logic案、Vin/surge、power sequence、rail budget、referee cut時backfeed防止。regulator未選定 |
| DC-link | capport ripple15 A適合、bulk ESR/ripple、ceramic effectiveC/DCbias、OV/surge/temperature、公式energyへの寄与を確認。製品/容量TBD |
| precharge | link容量、ΔV判定、許容起動時間、resistor pulse curve、bypass weld/open、reverse current isolation。RC感度計算は値の採用ではない |
| bleed/dump/service | 最大C/energy、要求時間・安全閾値、抵抗pulse/continuous、thermal inhibit、OFF時電源、voltage indication/rebound。抵抗値TBD |
| reverse/isolation/fuse | MOSFET bodydiode、両側source、DC fault currentとenergy、interrupt rating・fuse coordination。PWM OFFで絶縁できるとはしない |

## Loss accounting

[実行可能なモデル](../simulation/component_budget.py)と[生成結果](../simulation/component_results.md)を参照。半導体conduction、overlap、gate、L Cu、3shuntを別項目とする。core/Coss/Qrr/deadtime/connector/aux未算入なので小計は未算入損失がある参考値でありefficiency保証ではない。Task 2のeta lossへ小計を足すと二重計上になるため別モデルとして扱う。bank ESRは別で12 A時初期25.92 W、aging2倍なら51.84 W。peak秒数・繰返しと熱容量が必要。
