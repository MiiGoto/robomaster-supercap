# Design notes — no final component values

以下は一般原理に基づく候補分析。採用・定格・loop設計はTBD。source固有の構成は [comparison](reference_comparison.md) と [references](../references.md)。

## Capacitor bank

検討入力: cell makerのsingle-cell許容電圧とderating、N series / M parallel、C tolerance、leakage、ESR vs温度/aging/frequency、continuous/pulse current、life、thermal、mounting、vent clearance、balancing、service discharge。

- 単一理想等価cap: `E = (1/2) C V²`。
- series: `1/Ceq = Σ(1/Ci)`。同一cell N個では `Ceq = Ccell/N`。
- 同一series stringをM並列なら `Cbank = M Ccell/N`。並列stringにもcurrent-sharingと個別fault pathがある。
- series ESRは和、同一string並列なら概ねstring ESR/M。接続抵抗・温度差・frequency依存を加える。
- 全energyは `Σ(1/2 Ci Vi²)`。balanced状態でのみ等価bank式との整合を単純化できる。
- usable ideal energy: `(1/2) Ceq (Vhi² - Vlo²)`。実際はconverter損失・ESR sag・UV marginを引く。
- loss: `P_ESR = Irms² ESR`、step sag: `ΔV ≈ I ESR`、ideal charge: `dV/dt = I/C`。
- seriesではchargeが同じでも `ΔVi = ΔQ/Ci` が異なる。leakage差はDC imbalanceを作る。bank total Vだけではcell OVを検出できない。
- nominal energy規則が耐圧基準なら動作電圧を下げただけでnominal capacityが減るとは扱わない。
- cell数・bank最大電圧・safe voltage/energyはhuman gateでTBD。mechanical retention、絶縁、cell tap short防護を同時に決める。

## Cell balancing

方式は排他的でない。IC-basedにはpassive shunt制御もactive transferも含まれる。

| Method | Complexity | Power loss | Speed | Reliability | Fault behavior / suitability |
|---|---|---|---|---|---|
| passive resistor | 低 | 常時Vi²/R、長期自己放電 | 小電流なら遅い | 単純だが熱・抵抗tol管理 | openでbalance喪失、shortでcell discharge/発熱。leakageばらつき対策候補、fast charge OV保護の代替不可 |
| active transfer | 高、switch/magnetics追加 | standbyと変換損失、抵抗より省energyの可能性 | 定格transfer current次第 | 制御・short pathsが増える | 誤制御で弱いcellへenergy集中、switch短絡。頻繁な高energy運用なら候補 |
| IC-based monitor/balance | 中〜高 | passive/active方式による | IC current/thermal制限次第 | 診断を集約、common-cause注意 | supply loss、tap断線、IC故障を検出。正確なcell監視と独立trip候補 |

balancingはOV protectionと別機能。温度とleakage最大差に対して充電速度に追従するか検証する。

## Topology versus voltage envelope

| Candidate | Voltage relationship / function | Advantages | Disadvantages | Control complexity | Expected component count |
|---|---|---|---|---|---|
| charge buck + separate assist boost | Vcap < Vbus全域を保証した場合の充電降圧・放電昇圧 | 方向ごと理解容易、機能分離 | 2 stageと交差path、voltage crossingに不適 | 中、2 controller/mode arbitration | 2 inductive stages、各switch/rectifier/保護 |
| two-switch bidirectional half-bridge | fixed high port=bus、low port=bank、Vcap < Vbusに十分margin | 少部品、charge buck / assist boostを同じLで | equality近傍・Vcap>Vbusに制約、diode path | 中、signed current/zero-cross/deadtime | half bridge 2 FET + L + driver、補助/遮断部品別 |
| four-switch bidirectional synchronous buck-boost | bankがbus上下に跨る範囲 | 両方向step-up/down、energy利用範囲広い | switching loss、driver数、mode移行の複雑さ | 高、2 bridge協調、current direction、fault timing | 4 FET + L + 2 half-bridge drivers、補助/遮断別 |

数は概念stageで、parallel FET/phase、filter、sense、fuse、prechargeは含まない。
boost-onlyはcharge方向も含めた全機能を満たさず、buck-onlyも低bank電圧からbus assist不可。
非同期diode converterは一般に一方向。synchronous化は効率と双方向制御の可能性を与えるが、逆流防止を自動保証しない。
half bridgeはswitch構成であり、それ自体を独立したbuck/boostとは決めない。port関係・L接続・制御で機能が変わる。
single phase vs多相は別軸。最初にvoltage envelopeとfault isolationを決めてから比較する。

## Block design intent extraction

| Block / Function | Typical implementation | Advantages | Disadvantages | Common failure mode | RoboMaster suitability |
|---|---|---|---|---|---|
| buck / voltage reduction | switch + diode/L、またはsync half bridge | chargeに単純 | step-up不可 | switch shortでbankへbus直結 | Vcap下側だけの充電候補 |
| boost / voltage increase | L + low-side switch + rectifier | low capからassist | deep dischargeでcurrent増大 | switch short / output diode backfeed | bank下側の放電候補 |
| buck-boost / step up/down | 非反転four switchなど | voltage crossingに対応 | switchと制御増加 | mode切替shoot-through | envelope未知なら比較対象 |
| bidirectional buck-boost / reversible transfer | signed current feedback + sync bridges | 共通stageでenergy buffer | fault時2 sourceから供給 | current polarity誤認、gate fault | 有力、採用TBD |
| half bridge / PWM switching leg | complementary FET + deadtime driver | 同期switch基礎 | floating high-side供給 | 同時ON / bootstrap不足 | fault inputとdeadtime検証必須 |
| synchronous converter / loss reduction | diodeをcontrolled FETへ | conduction損失低減 | 軽負荷逆流・shoot-through | deadtime違反、stuck gate | current directionとhardware tripが条件 |
| input protection / polarity and fault boundary | fuse + isolation candidate + transient clamp | robot/sourceを保護 | DC interruption/熱/arc設計必要 | FET短絡、fuse未溶断 | bank側pathも別検討 |
| precharge / inrush control | resistor+bypass / active limiter / converter soft start | connector arcを抑制 | resistor熱とsequence増加 | bypass stuck、timeout無視 | 起動経路全部を検討 |
| sensing / observability | ADC conditioning + independent comparator candidate | 制御/diagnostics | noise/校正/common cause | open/stuck/reference mismatch | signed currentとcell監視重要 |
| safety / energy containment | independent inhibit + latch + isolation | MCU crashへ耐性 | common supply故障は残る | shared sensor/reference故障 | 必須要求、未実装 |
| discharge / service | passive bleed / controlled sink / removable service tool | OFF後のenergy低減 | 熱・time・bus loss依存 | resistor open、indicator消灯誤認 | 独立測定とlockoutが条件 |

## MCU candidates

| Candidate | ADC/PWM/fault | CAN / interfaces | Tradeoff |
|---|---|---|---|
| STM32G4、G474-class | HRTIM、PWM-triggered ADC、comparators/fault input候補 | FDCAN、UART、SPI/I2C | peripheral余裕、pin mux / package / errata / cost確認必要。G4全型番にHRTIMがあるとは仮定しない |
| STM32F334-class | HRTIM、ADC、comparator/op-amp候補 | Classic CAN、UART、SPI/I2C | 比較的少resource。memoryとloop timing余裕を評価 |

ST AN5094と各datasheet/errataを入口にする。temperature/current measurementはADC front-endとsystem設計で決まり、MCU内蔵temperatureはpower component temperatureの代替でない。
HRTIM fault tripもMCU/clock/supplyに依存するためexternal inhibitの代替とは断定しない。exact part/packageを選定しpin番号をdatasheetで確認する。

## Current sensing

Hallはmagnetic sensingの一方式。ここでmagnetic候補はAMR/TMR等を指し、製品の構造と絶縁を個別確認する。

| Method | Bidirectional / bandwidth | Isolation / accuracy | Loss | Cost / area | Fault behavior |
|---|---|---|---|---|
| shunt + amplifier | offset referenceでsigned測定、PWM同期可。amp/filter bandwidth要設計 | 一般に非絶縁、offset/gain/temp/CMR影響 | I²R、hotspot | 低〜中、Kelvin配線とthermal面積 | shunt open、amp saturation、reference故障。fast comparator branch候補 |
| Hall | signed対応製品を選択、帯域は個別datasheet | 絶縁型もある、offset/drift/外部磁場影響 | conductor抵抗による | 中〜高、一般に大きめ | supply loss、offset、magnetic saturationを診断 |
| AMR/TMR等magnetic | signed対応/帯域は製品次第 | 絶縁はsensor方式だけでは保証されない | conductor loss、shunt不要の可能性 | 中〜高、geometry/磁気配置に依存 | 外部磁場、saturation、供給故障 |

制御senseとshort-circuit protectionの必要帯域は別。bus/bank/inductorどのpointを監視するかでpeak/average関係が変わる。

## Voltage and temperature sensing

bus Vはsource状態・OV・power計算、bank Vはenergy・converter envelope、cell Vはimbalance・OV/UVに必要。
series bankでbank totalのみの監視は不十分。per-cell monitorは要求として検討し方式/診断/independent tripをgateで決める。
ADCはdivider tolerance、RC settling、input range、transient clamp、series impedance、injection current、MCU unpowered時backfeed、tap断線/短絡、reference診断を設計する。回路値TBD。
firmware referenceと実装referenceを一致させ、校正versionを検証する。

MOSFETはjunction推定とpackage温度差、inductorはwinding/core hotspot、bankはESRと寿命の温度を評価する。
初期候補はpower-stage hotspot + bank。inductorとMOSFETを1 sensorで兼用する場合は両者の温度差/応答を実測し、保守的marginで保護できることが条件。
sensor open/shortは低温と誤認しない。fan failure/zero-airflowも評価。全箇所sensorを無条件必須としないが、未監視hotspotの根拠を記録する。

## Precharge / emergency discharge

large bankだけでなくbus decoupling、diode bypass、connector挿入時の充放電両方向ΔVを調べる。
候補: resistor + bypass、active current limiter、converter-controlled soft start。soft startはPWM開始前のbody-diode pathを抑えられる場合だけprecharge代替になる。
`I_initial ≈ ΔV/R`、`τ = RC`、単純なRC precharge抵抗の損失energyは概ね`1/2 C(ΔV)²`。bypass weldingとtimeoutを検出する。

bleedはpassive常時(確実だが自己放電)、controlled(省energyだがaux依存)、service tool(操作・定格・lockout依存)を比較。
理想resistor discharge: `V(t)=V0 exp(-t/RC)`、`t=RC ln(V0/Vsafe)`、`P_initial=V0²/R`。cell imbalanceと誘電吸収によるvoltage reboundを加える。
safe thresholdは感電だけでなく短絡energy・工具arc・cell状態を考慮しTBD。LED消灯を証明にしない。故障中の無条件緊急放電は熱/短絡を悪化させ得る。

## PCB high-current considerations (no layout yet)

- high-current pathを短くし、bank/source両方のfault pathを可視化する。
- switching current loopとgate loopを最小化し、sense returnをswitching returnから離す。
- power GND / signal GNDの名称分離だけでなく実際のreturnを追跡し、plane cutで迂回させない。
- shunt/current senseはKelvin connection、ADC参考GNDも計測点を管理する。
- thermal copper、via、MOSFET/inductor cooling、capacitor ESR熱を評価する。
- connectorはcontinuous/pulse、ambient、接触抵抗、wire、hot unplugを含めて定格を確認する。
- capacitor pathを大電流に対応させcell tapは短絡energyを制限。mount/振動/絶縁を同時レビューする。
- 銅厚・幅・via数・fuse ratingは要求とthermal/current試験前に決めない。
