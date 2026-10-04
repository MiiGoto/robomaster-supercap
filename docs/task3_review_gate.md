# Prototype Rev A — current status

2026-10-03 JST。**Current: Prototype Rev A schematic only.** Task2 architectureはユーザー採用承認済み。実機条件未確認は[Prototype envelope](../docs/prototype_rev_a_envelope.md)に明示した **ASSUMPTION — MUST VERIFY ON PROTOTYPE** として隔離し、詳細electrical schematicを作成した。部品/保護閾値はprototype候補で性能保証ではない。[現行review](../docs/rev_a_schematic_review.md)と[pinout](../docs/pinout.md)が現在の設計記録。PCB placement/routing、firmware、通電、120W使用許可、競技適合、Task4開始は未承認。以下の旧status/approval pending/skeleton-only記述はhistorical recordであり現在statusではない。

## Current authorized schematic gate

User explicitly permits conservative prototype assumptions despite unknown physical conditions. Drawing detailed circuits is authorized and now implemented. This supersedes the historical hold on *schematic creation*. It does not waive measurement/human gates before energizing/full power, or approve component/thermal/isolation capability. External interruption assembly and monitor profile are still incomplete.


## Historical records (preserved)

# Task 3 review gate — architecture approved, physical envelope unknown

2026-10-03 JST。ユーザー回答「Task 2案を採用。実機条件は自由入力で指定する」を受領。9S・50 F/cell、Ceq=5.5556 F、Vcap=12–22.05 V、4-switch双方向buck-boost、STM32G474RE/LQFP64、high-side shunt、抵抗precharge、充電入力40 W、assist要求80/120 W、cap平均電流normal8 A/peak12 Aを**承認済み設計目標**とする。承認は部品の熱定格・実装・安全検証を意味しない。Task 2の「人間承認待ち」はこの範囲に限り本記録で置き換える。

## Missing requirements and effects

| Missing requirement | Influence | Reviewable calculation candidates; not limits |
|---|---|---|
| battery型番、converter端の実bus min/nom/max、regenとsurgeの電圧・時間・source impedance | VDS/TVS/DC-link/aux耐圧、UV、動作範囲、遮断energy | 22/24/26 Vは従来計算条件のみ。60 V MOSFET classを比較するがsurge envelopeが無いので適合判定しない |
| 120 W peakの継続秒数と最短繰返し間隔 | bank ESR・MOSFET・L・shunt・connectorの過渡温度、平均損失 | 1 s / 5 s、10 s / 30 s間隔の感度計算が可能。どれも使用許可ではない |
| 最高周囲温度、密閉/通風/強制冷却、mount条件 | thermal headroom、continuous current、derating、NTC threshold | 25/40/50°Cを比較点にできるが未指定。cell定格65°C以下という制約だけでは実ambientを決められない |
| service-safe V/energy、放電完了時間、local link容量・許容起動時間 | bleed/dump/precharge抵抗・pulse energy・検査との共存 | 比較はRC式で行い、値はTBD |
| fault source impedance、遮断時間、capport ripple/測定誤差 | fuse/DC interrupt、OC threshold、15 A瞬時制約 | 平均12 Aの承認を瞬時15 A適合と解釈しない |

添付Task 3 §1の「重要な項目がTBDのままで、power-stage ratingへ直接影響する場合は勝手に仮定して詳細回路を完成させない」に従う。実機条件についてユーザー回答「不明」を受領。上記条件が確認できるまで部品比較・計算・保護要求は進めるが、詳細switching回路の完成、部品定格freeze、通電可能という表示は保留。

## Current deliverables and resumption

- [部品比較](task3_component_review.md)と[損失・ripple計算](../simulation/component_results.md)は候補評価。購入BOMではない。
- KiCadは既存9-page architecture skeletonを維持。新規power symbol/net/footprintは未実装、Task 3 ERC/pin crosscheckは未実施。Task 2 ERCの0/0は実回路の検証ではない。
- PCB、firmware、購入、通電、Task 4、mainへのmergeは行わない。
- 未入力条件を受領後、実端envelope確認→部品/保護の定格coordination→詳細回路→pin/footprint照合→ERC→reviewの順でTask 3を再開する。

## Confirmed / Assumption / TBD

**Confirmed:** 上記Task 2案のユーザー採用承認、2026 RMUL対象、Task 2 base ddfb3b1を含むfeature/power-stage-schematic。

**Assumption:** converter端22–26 V、eta90%、100–200 kHz、ripple3 A p-p、計算用hot RDS factor・switching時間・L bias factor。

**TBD:** 実bus/surge、peak duty、ambient/cooling、cell連続熱定格、最終部品、保護閾値・遮断energy、RC容量/時間、service-safe基準、詳細回路と全検証。
