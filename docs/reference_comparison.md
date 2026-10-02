# Public design comparison

2026-10-03。R1–R4のURL・author・license・参照policyは [references](../references.md)。
**C** = 作者の公開READMEで確認(本projectで実測していない)。**A** = 本projectの分析上の仮定。**TBD** = 今回閲覧した範囲で未確認。TBDは機能不存在を意味しない。
4チームの設計を比較。R1は他チームの先行双方向案に影響を受けており、完全な系譜独立ではない。R4はbank/charger分離案として異なる構成を提供する。
third-party schematic/PCB/PDF/images/codeの取り込みなし。全protectionsをnetlistで追跡した監査ではない。

| Item | R1 ENTERPRIZE RM2023 | R2 PSP RM2024 | R3 SP_Ultra_CAP | R4 Purdue Electrical-System |
|---|---|---|---|---|
| capacitor configuration | TBD | TBD | TBD | C: bankをchargerから分離、series/parallel TBD |
| total capacitance | TBD | TBD | TBD | TBD |
| rated voltage | TBD: bank定格を確定できず | TBD | TBD | TBD |
| balancing method | TBD | TBD | TBD | C: bankにbalancing、方式TBD |
| charge topology | C: 四switch双方向buck-boost | C: 多相parallel四switchbuck-boost | C: 双方向buck-boost | C: STM32 controlled buck charger |
| discharge topology | C: 同じconverterを逆方向制御 | C: 同じ双方向stage | C: buck/boost mode切替 | TBD: assist path未確認 |
| bidirectional topology | C: 非絶縁四switch | C: 多相四switch | C: 双方向、詳細net TBD | TBD: bidirectionalとして扱わない |
| MOSFET arrangement | C: 二つのhalf bridge | C: 相ごと四switch、parallel detail TBD | TBD: exact配置未確認 | TBD: H-bridge表記の接続未監査 |
| gate driver | C: UCC27211、high side独立供給 | TBD | C: ADP3110A | TBD |
| inductor arrangement | C: flat-wire power inductor、exact layout TBD | TBD: 多相の配置未監査 | C: TMPC1707HP series、配置TBD | TBD |
| current sensing | C: shunt + INA186 | TBD | C: NCS210 amplifier | TBD |
| voltage sensing | C: conditioning circuit、exact input保護TBD | C: ADC reference差の警告 | C: voltage follower、NCS20282 | C: bank ADC、詳細TBD |
| temperature sensing | TBD | TBD | TBD | TBD |
| MCU | C: STM32F334 | C: STM32G474 | TBD: root READMEでは未確認 | C: STM32F334 charger |
| CAN | C: CAN status/control | C: CAN | C: 2 FDCAN | TBD |
| precharge | TBD | TBD | TBD | C: empty-bank current制限charger、connector precharge TBD |
| fuse | C: power board上 | TBD | TBD | TBD |
| reverse-current protection | TBD: FPWMで逆電流あり得る | TBD | TBD | TBD |
| overvoltage protection | TBD: independent path未確認 | TBD | C: input/output OVとの説明、独立性TBD | TBD |
| overcurrent protection | TBD: independent path未確認 | TBD | C: output OCとの説明、独立性TBD | TBD |
| undervoltage protection | TBD | TBD | C: input voltage drop保護との説明 | TBD |
| thermal protection | TBD | TBD | TBD | TBD |
| discharge / bleed path | TBD | TBD | TBD | TBD |
| cooling | C: aluminum power board | TBD | TBD: 専用cooling未確認 | TBD |
| PCB current path | C: high currentはpower boardから直接引出し | TBD | C: 6-layer、analog/powerとdigital配置を分離 | C: charger 4-layer、実電流path TBD |
| firmware architecture | C: ADC/PID current feedback、FPWM | C: user code/Cube生成部分を分離 | C: CAN・mode切替、diagramと実装差に注意 | C: bank firmwareなし、charger制御detail TBD |
| reported problems | C: inductor ripple、high-side供給過電圧リスク、軽負荷逆電流 | C: ADC referenceとfirmware不一致による複製時問題 | C: current linearity誤差、個体校正必要 | TBD: READMEはWIP/ship blocker表示 |
| license | C: GPL-3.0表示、BBS非商用記載との整合TBD | C: GPL-3.0、docs CC-BY-SA(version TBD)、hardware別scope TBD | C: MIT表示、asset scope再確認 | TBD: 明示root license未確認 |

## Why these architectures (our inference, not author performance validation)

**R1**: 四switchはbankがbusより上にも下にもなる場合を一つのstageで扱える。control/power board分離は熱とservice性を改善し、大電流をsignal connectorへ通さずに済む。high-side独立供給は長いON時間に利点があるが、gate supply自体の故障を増やす。最も参考になる構成説明。ただし保護を別途証明する必要がある。

**R2**: 多相parallelは電流分担とripple低減を狙う選択と推定。代わりに相間の校正、current-sharing、sensor数、fault時の残り相への負担が増える。初版から多相を必須にしない。ADC reference整合をproduction/configuration review項目にする。

**R3**: 単板統合は配線と容積を減らせる一方、switching noise・熱・auxiliary functionsの干渉を受けやすい。ground分離やbeadをそのまま模倣せずreturn currentを確認する。個体校正とsensor bandwidth/errorをclosed-loop設計の前提にする。

**R4**: bankとcharger分離は蓄電・balancingとcurrent-limited chargingを分担できる。assist制御・逆流・shutdownは別経路になるため、chargerだけで本projectの双方向要求を満たすとは判定しない。WIPをworking hardwareと読み替えない。

## Adoption boundary

採用するのは設計意図・比較軸・故障の教訓。回路値、reported power/効率、MOSFET/inductor定格は採用しない。
temperature、precharge、independent OV/OC、isolation、bleedがTBDのsourceは安全性を確認済みとしない。
本projectの候補比較とblock分析は [design_notes](design_notes.md)。
