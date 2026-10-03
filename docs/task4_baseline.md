# Task 4 baseline checks — skeleton only

2026-10-03 JST、KiCad CLI10.0.6。Task 3 base428ad10。詳細回路/placement未実装。

Schematic files=9; instance/object counts: symbol=0, wire=0, footprint=0, segment=0, via=0, gr_line=0.

## ERC / DRC

- ERC: Errors0 / Warnings0。9 sheets。部品instance/wireが無いためpin/net/rating検証ではない。
- ERC ignored checks: single-use global label、four-way junction、SPICE model、footprint filter。既存設定、今回marker/exclusion追加なし。
- DRC: invalid_outline error1、unconnected0、footprint errors0。Edge.Cuts外形未定義。
- 分類: A footprint/placementは対象不存在、B board rule/外形未定義1、C unrouted対象不存在、D outline/limits/placementは人間判断待ち。
- DRC ignored checks: courtyard missing、via endpoint centering、tuning geometry、footprint filter、footprint type。実footprint配置後に再レビュー必須。
- raw tool reportsは.local/task4/内のローカル生成物、公開repoへ追加しない。
- 既存.kicad_pro未コミット設定変更を保持・今回commitから除外。PCB/schematicファイル未変更。

## Existing model corner re-evaluation

bus22/26 V × bankopen12/22.05 V × request80/120 W ×100/200 kHzを評価。
eta90%、RDS hotfactor1.6、winding80°C、edge40 ns、L tolerance0.8 × assumed bias0.8はAssumption。
全範囲・charge/regen/overlap/fault/transientのworst-case保証ではない。

| Candidate | Max IL peak A | Max IL RMS A | Max cap avg A | Max bus avg A | Max FET conduction W | Max overlap W | Max gate W | Max L copper W | Max 3shunts W | Max subtotal W |
|---|---|---|---|---|---|---|---|---|---|---|
| CSD18540Q5B / 22 uH | 14.172 | 12.065 | 12.000 | 5.455 | 1.025 | 2.496 | 0.424 | 2.833 | 0.938 | 7.661 |
| CSD18540Q5B / 15 uH | 15.185 | 12.140 | 12.000 | 5.455 | 1.038 | 2.496 | 0.424 | 2.223 | 0.942 | 7.041 |
| CSD18563Q5A / 22 uH | 14.172 | 12.065 | 12.000 | 5.455 | 3.168 | 2.496 | 0.160 | 2.833 | 0.938 | 9.523 |

各列のmaximumは異なるoperating pointを含むため横一行の値を足さない。FET conductionはpathの2素子合計、単一device値ではない。
max cap/busは平均値、瞬時module電流と同義ではない。SW switchpeakはこのCCM近似ILpeakを参考にするがdeadtime/diode/recovery/overshootは未算入。
charge40 W model: capavg max2.876 A、busavg max1.818 A。maxbank時chargeOFF。
core/Coss/Qrr/deadtime/aux/connector未算入、totalconverterlossはTBD。候補定格を満たす判定はNot established。
bankESR12 A時25.92 W(initial)、agedESR2倍なら51.84 W。peak duty/ambient不明でtemperatureは算出不可。

## Scope status

8 existing calculation checks pass。単位・解析RC energy/time・frequency/ripple・energy conservationを確認、実回路の試験ではない。
symbol/footprint crosscheck、boarddimensions、部品座標、ratsnest、3D確認はNot performed。routing/Task 5に進まない。
