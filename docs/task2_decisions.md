# Task 2 architecture proposal — human review pending

2026-10-03 JST。Confirmedは資料または依頼の確認、Assumptionは採用提案・計算条件、TBDは実機仕様・承認・未検証事項。詳細switching回路、部品購入、実機通電は行わない。

## Applicable competition evidence

対象はユーザー指定の2026 RMUL、哨兵・歩兵・英雄・エンジニア。開催地と種目選択はTBD。
公式hubのRMUL 2026アーカイブを直接閲覧し、掲載最新版が競技規則CN V1.2.0 (2026-01-09)、EN V1.2.0 (2026-01-13)、制作規則CN V1.3.0 (2026-02-09)であることを確認。RMUCの後期版や2027版を適用しない。URLとファイルhashは[references](../references.md)。会場補足・最新答疑は人間確認が必要。

| Evidence | Confirmed content | Design implication |
|---|---|---|
| 制作規則S5–7 / p14 | 底盤功率に寄与するbankは英雄・歩兵・哨兵のみ、1組、nominal ≤2000 J、measured ≤2200 J | エンジニア向け競技assistは許可されないため対象外。別の非底盤用途も許可を推測しない |
| 制作規則表2-6/7/8/10 | 指定4種の最大供電電圧30 V | 30 Vは競技上限。実busのnormal上限、surge、MOSFET定格ではない |
| 制作規則S141/145、p65–67 | 底盤電力の監視迂回禁止、他電源との分離、電源管理module入力22–26 V | nominal24 Vは範囲中心のAssumption。Chassis出力のdroop/surge・実operating rangeはTBD |
| 制作規則3.12/S184–189、p97–98 | bank→公式module→自作board、module CAN→CAN1、XT30 peak/continuous ≤15 A、検査lead≥100 mm、bank power port1つ | cap側instantaneous current制約。bus側電流定格と混同しない。tap/service pathの規則適合はレビュー |
| RMUL競技規則EN表3-2/3/4、p17–21 | 3V3: Hero100 W、Infantry power型90 W / HP型75 W、Sentry100 W | referee計測点のlimit。converter出力上限やcharge budgetそのものではない |
| EN表4-2、p38–39 | Infantry Matchは120 W | 3V3の値を混用しない。Engineer Challengeは別種目 |
| EN3.3.1.4、p30–31 | referee buffer60 J、10 Hz監視、枯渇時5秒遮断 | capacitor物理energyとは別。制御は遮断を尊重、capから底盤を継続供給しない |

charging budget = referee許容入力 − 実負荷 − aux損失 − 計測/応答余裕。実計測点接続・telemetry・会場仕様を確定するまでchargeの競技許容WはTBD。CAN bitrate/ID/terminationは公式moduleとrobot仕様に照合しTBD。

## Capacitor candidates and selected proposal

メーカー公式資料のみ。stock、cost、供給継続はTBD、購入なし。

| Cell candidate | C / rated V | DC ESR | Leakage | Current evidence | Temperature / size / mass | Life evidence |
|---|---|---|---|---|---|---|
| KYOCERA AVX SCCV40B506SRB | 50 F / 2.7 V, −10/+30% | max18 mΩ(10 ms),20 mΩ(5 s) | max75 µA/72 h | peak35.53 A、continuous TBD、peak時間は追加確認 | −40..65°C at2.7 V; 85°C at2.3 V;18×40 mm; mass TBD | Rev11:1000 h at65°C/rated V;500k cycles、終端C≥70%,ESR≤200% |
| Eaton HV1840-2R7606-R | 60 F / 2.7 V, family −10/+30% | 18 mΩ | 110 µA | 5.7 A continuous at15°C rise;38.9 A/1 s | −40..65°C;18×42 mm;13.63 g | family index:1000 h/65°C、500k cycles。PDF全文/版TBD、C70%/ESR200%はproduct page確認 |
| Eaton HV1860-2R7107-R | 100 F / 2.7 V, family −10/+30% | 12 mΩ | 260 µA | 11.2 A continuous at15°C rise;61.4 A/1 s | −40..65°C;18×61 mm;20 g | family寿命の全文/版TBD。条件外の寿命推定はしない |

| Scenario | N / Ceq | Bank rated V | Designed operating V (Assumption) | ESR initial | E at rated / +30%C | Eusable nominal |
|---|---|---|---|---|---|---|
| A primary: SCC50 | 9 / 5.5556 F | 24.3 V | 12..22.05 V | 0.180 Ω (5 s maximum) | 1640.25 /2132.325 J | 950.5625 J |
| B alternative: HV60 | 7 / 8.5714 F | 18.9 V | 8..17.15 V | 0.126 Ω | 1530.9 /1990.17 J | 986.2393 J |
| C alternative: HV100 | 4 /25 F |10.8 V |5..9.8 V |0.048 Ω |1458 /1895.4 J |888 J |

採用提案Aは22 V近傍までbankを使え、同じpowerのcap電流をB/Cより抑えられる。continuous熱定格が未確認なので製品確定ではなく第一試作の検討案。Bは明記されたcontinuous5.7 Aが制約、Cは低電圧で15 A module制約が厳しい。いずれも容量公差最大をrated voltageで計算し2200 Jを下回るが、検査合格は実測が必要。ESR・容量は温度/寿命でも変化する。

cell normal ceiling2.45 VをAssumptionとする。2.7 Vとの差250 mVを、測定誤差・balancing残差・fault overshootの合計budgetに割り当てる。暫定各50 mVの計150 mVとして残100 mV、保証値ではない。85°C拡張定格2.3 Vとは両立しないので本案は65°C以下の定格域、運転tripはそこからsensor/lag marginを引いて決める(TBD)。bank nominal比較点18 V、normal max22.05 V、rated sum24.3 Vは別値。単一cellの2.7 Vが支配し、sum24.3 V以下だけで安全とはしない。Vmin12 Vに加えcell最小値監視が必須。service-safe voltage/energy/timeはTBD、検査1 Vとは区別する。

balancingは**IC-based per-cell switched passive shunt + cell monitor + independent OV charge inhibit**を採用提案。常時抵抗は単純だが漏れ差を吸収するほど常時損失が増える。active transferは低損失・高速だが追加switch/inductor故障点が多い。IC式passiveは閾値が明確でMCU停止中も保護可能な方式を要求する。ただし具体IC・精度・supply-off動作・shunt電流/抵抗はTBD、MCU指示だけでbalance/OVを担わせない。

## Converter decision and quadrants

**single-inductor, four-switch, non-inverting bidirectional synchronous buck-boost**をAssumptionの第一案として選ぶ。2つのhalf bridgeの間にinductor。22–26 V source inputとcap12–22.05 Vは端で重なり、Chassis droopは不明、charge時terminal VはESRで上昇する。全域でVbus>Vcapを保証できないので両方向buck/boostが必要。

| Alternative | Suitability / cost / complexity |
|---|---|
| 2-switch half bridge bidirectional buck/boost | bus>capが全条件で保証されるB/Cなら有力、FET2/L1/driver1で簡素。Aと未確認droopでは範囲保証不可 |
| unidirectional buck + boost separate | charging/assist別制御、FET/diode/L経路追加、回生切替/逆流保護が複雑 |
| selected 4-switch synchronous | FET4/L1/half-bridge driver2の概念。重なる電圧域と両方向を扱えるがshoot-through/遷移/ADC時刻が複雑 |

Bus→Cap: bus高ならbuck、bus低ならboost、境界では混合動作。受電側cap current/voltageを制御しreferee入力power budget優先。
Cap→Bus: cap低ならboost、cap高ならbuck。signed inductor currentを反転し、bus OVとassist power/currentを制限。
half bridgeを同期整流するが、具体PWM timing/gate波形は未設計。方向反転はramp→zero-current確認→Standby→再指令。regenは初号機では能動受入禁止、検知→inhibit/隔離要求。必要なbus吸収手段はrobot側仕様TBD。OFF時body diodeとshort FETの経路は独立disconnectが担う。

## Voltage, current, power and thermal envelopes

source入力22/24/26 Vは公式範囲＋nominal仮定、converter端も同範囲とするのは計算Assumptionのみ。bank12/18/22.05 V、charge bus input40 W、assist bus output nominal80 W / requested peak120 W、converter efficiencyη=0.90(ESR/aux除外)を比較条件とする。実max currents/power/peak durationはTBD。
primary cap current clampはnormal8 A / peak12 AのAssumption。peak/continuous15 A module制約内でripple/計測誤差/停止overshootを配分するまで許可しない。AVX continuous currentは未保証なので8 Aも熱試験前のratingではない。

discharge: Pbus=η Icap(Vopen−Icap Rbank)、Ibus=Pbus/Vbus。
charge: η Pbus=Icap(Vopen+Icap Rbank)。converter損失はdischarge Pbus(1/η−1)、charge Pbus(1−η)。bank ESR損失I²Rは別に加算。
80 W assistは12 Vでnormal8 A制限により76.032 Wへderate。120 W要求は12 Vで必要14.088 A、peak12 A制限では106.272 Wに制限。22.05 Vの120 Wは約6.38 A。120 W bus currentは26 Vで4.615 A /22 Vで5.455 A。charge40 W bus currentは1.538..1.818 A、cap current約1.61..2.88 A。詳細は再生成可能な[model](../simulation/power_budget.py)と[results](../simulation/results.md)。4 cornersと両方向を出力する。

converterだけでも80 W出力時8.889 W、120 W時13.333 W、40 W充電時4 Wの損失を仮定。cap12 Aで25.92 W ESR熱、EOL ESR2倍なら51.84 Wとなり同電力継続は不可。semiconductor conduction/switching、L copper/core、shunt I²R、connector/contact I²R、auxを別途配賦し、合計の重複計上を避ける。暫定cooling評価budget:converter peak15 W + cap peak26 W + aux/connection未算出、steady-state許容値ではない。ambient/airflow/温度上昇/ピーク時間/thermal tripはTBD。機器定格からhotspot限界を逆算する。

## Power-stage requirements only

switching range100–200 kHzをAssumption。100 kHz側はswitch loss/EMI/settling負担が小さいがLが大きい。200 kHz側はripple/Lを減らせるがswitch lossと制御計算/ADC窓が厳しい。300 kHz以上は初号機で根拠不足。最終周波数はTask3以降。

L preliminary ripple absolute target3 A p-p。buck ΔI=Vlow(1−Vlow/Vhigh)/(Lf)、boost ΔI=Vlow(1−Vlow/Vhigh)/(Lf)。26→12 Vで分子6.462 V、100 kHzなら21.54 µH、200 kHzなら10.77 µH。よって**11–22 µHは探索域**であり全組合せ合格範囲ではない。4-switch境界・reverse・tolerance・saturation減少で再計算する。Ipeak=|ILavg|+ΔI/2、Irms≈sqrt(ILavg²+ΔI²/12)。12 A+3 Aなら13.5 A peak/12.031 A RMSの初期estimate(ILavg=cap avg近似、buck duty等で再評価)。Isatはhot/dc bias時のLを使いtrip current+delay di/dtを上回ること。DCRmax=allocated copper loss/Irms²、core損失・温度・サイズはTBD。module15 Aはinductor peakとは別測定点。

MOSFET:各port最大normal/surge/clamp overshootを含むstressからVDS要求を算出。40 V級は30 V競技上限から余裕10 Vしかなく未確定surgeでは承認不可。60 V級を比較出発点とするAssumption、最終ratingはsurge実測/clamp tolerance/絶縁設計後。Idの宣伝値でなくhot RDS(on)/SOA/package/PCB熱から許容currentを求める。RDSmax=conduction loss allocation/(Irms² duty)、Qgとdriver currentからswitch loss/timingを確認。pulse short energyとavalancheの常用不可。

gate driver:half bridge2ch×2、高/低side、3.3 V logic互換、UVLO、出力OFF bias、external kill、dead-time/interlock、delay最大/ばらつきが必要。bootstrapは長いstatic ON/100%dutyでcharge維持できるか確認、不可ならcharge-pump/isolated biasを比較(TBD)。stuck-highをdriver ENだけで安全化しない。個別part選定はTask3、propagation delay budgetはOC clearing energyから逆算。

## MCU and measurement architecture

| Candidate | Evidence / decision |
|---|---|
| STM32G474RE, LQFP64 | 第一候補Assumption。HRTIM、5 ADC、FDCAN、comparator/advanced-timer break、DMAを利用。DS12288 Rev6。使わないUSB/crypto/external memoryは追加しない |
| STM32G431RB, LQFP64 | cost/simple案。2 ADC、advanced timers、FDCANあり、HRTIMなし。4-switchのADC窓/遷移自由度に余裕が少なく代替 |

I/O予算: PWM4、enable1、fault/break2、ADC8(bus/cap/3current/3temp)、cell monitor SPI4+alert1、CAN2、UART2、SWD2、precharge/disconnect/bleed制御4、feedback3、heartbeat1、spare4 =38 GPIO。reset/power/reference/crystalは別。LQFP64を基本、48pinはrouting余裕不足、100pinは現段階不要。DS table12でPA8/9/10/11のHRTIM A1/A2/B1/B2、LQFP64 pins42/43/44/45が存在することを確認。CANは別AF pinへ逃がし、全ADC/FLT/SPI/CANの重複なしpin assignmentとvoltage toleranceをTask3前に検証(TBD)。MCU family featureが全て同時にpackageへ出せるとは仮定しない。

outer supervisorはreferee input budget / bus voltage / cap energy / thermal limit、inner loopはsigned inductor current。hardware faultが両loopより優先。HRTIM/timer同期ADCでswitch edgeから離れた窓を設定、fast channelはtrigger+DMA、cell/tempは低速巡回。DS12288 Rev6 table3/p28にHRTIM→ADC conversion trigger、p32にtimer同期機能あり、詳細routing/latency/ISR周期はRM0440と実測で確認。MCU内comparatorはbreakへの補助経路、独立external OC latch/driver killの代用にしない。

currentは**high-side bidirectional shunt + amplifier**をbusとcap portに採用提案。ground returnを持ち上げずsigned powerを測れる。別のinductor shunt + PWM耐性front-endをinner loop用に用意。low-sideは安価だがreturn共通impedance/迂回問題、Hallは絶縁/低損失だがoffset・帯域・面積/cost、magnetic integratedはthermal drift/範囲が要確認。候補INA240の−4..80 V common-mode/400 kHzは十分条件ではなく、edge後settling・gain・phaseを確認する。fast tripはADC/INA240だけに依存せず別高速comparator path。shared shunt断線は残留共通故障。

measurement初期full-scale bus±8 A、cap/inductor±20 A (Assumption)。normal bus≈3.64 A/80W22V、cap≤8 A、peak≤12 A、fault current/latencyはTBD。rail saturationをfault扱い、fault thresholdはfull-scaleから決めない。12-bit理想LSBはbus3.91 mA/cap9.77 mA、精度ではない。ADC3.3 V referenceを提案し有効analog0.2..3.1 Vへheadroom、抵抗/gainは未決。

Vbus/capはdivider+RC+series protection+clamp、range0..36 V/0..27 Vを仮定、ADC fault/transient許容は別設計。理想LSB8.79/6.59 mV、精度budgetは≤0.5%reading目標Assumption、calibration/error/sampling loadで検証。cellは9ch differential monitorを要求、0..2.7 V正常/OVも計測できるrangeはTBD、error目標≤10 mV Assumption、open-wire診断/independent OVを必須。累積tapを直接MCU ADCへ入れない。

温度はMOSFET群の最大hotspot代表1点、inductor1点、bank代表1点の3 NTC提案。全cellに付けずcell差/熱試験で増設判断。open/shortをfault、sensor lag/位置からtrip margin設定、温度値未確定。connectorはbringup熱測定し常設sensor必要性を再評価。

## Precharge, discharge and protection

**resistor path + normally-OFF main bypass/disconnect**をbus local DC linkのprecharge案とする。ΔV/current/time/bypass feedbackを確認して接続。bank側にもindependent normally-OFF isolation、同一single power port経由で小容量linkのΔV整合を行う。bank全体の0 V→動作域充電はcurrent-limited converter soft-charge、UVセルを通常assistへ入れない。controlled converterだけのprechargeは起動前diode/pathを管理できず初号機主方式にしない。dedicated controllerは信頼性増すが部品追加。R/path wattage/startup時間はTBD、Epre=1/2 Clink ΔV²、ΔV確認閾値から決める。

safe dischargeはlow-power permanent bleed + thermally permitted switched resistor discharge + keyed service discharge + bank-powered independent voltage indication。service toolはsingle power portを切離した状態で接続、追加bank power portを常設しない。検査pathと放電回路が公式energy測定に干渉しないことをレビュー。bleed断線/aux消失でもOFFをSafeと表示しない。Vsafe/Esafe/放電時間はTBD、cell全て/内部link残留/reboundを実測。discharge energy/thermal定格は最悪C/voltageで算出。熱fault時には自動dumpが危険を増すので禁止しservice lockout。

external OV/OC/UV supervision、driver UVLO、temperature safety、external watchdog/supply supervisor→hardware latch→driver kill + HRTIM fault/break。enableはexternal biasでOFF、reset/debug/crash/float時OFF。critical faultはsourceとbank両側disconnect要求、fuseはDC interrupt/let-through検証後の最終防護。通信loss時はramp停止できる健全条件以外即inhibit。referee Chassis cutoffはassist禁止に直結し、cap由来auxやcross-domain通信から給電を継続しない。isolation回路・閾値・fault latencyはTBD、詳細回路未実装。

## Fault classes and review gate

WARNING:温度approach、軽いbalance差→derate。
RECOVERABLE_FAULT:command timeout/CAN loss、通常UV、正常precharge未完了→inhibit、fresh command+self-test+明示rearm。
LATCHED_FAULT:cell/bank OV、OC trip、sensor invalid、driver fault、MCU watchdog、precharge timeout、discharge failure→hardware latch、原因確認後service clear。
CRITICAL_FAULT:MOSFET short/shoot-through、L saturation persistent trip、fire/PCB熱、isolation failure→両energy source切離し、再通電禁止。発生原因不明なら上位classへ昇格。threshold/timeと安全なclear手順はTBD。

Task3前に人間が確認:大会会場/種目、Engineer対象外、battery型番/Chassis端droop/surge/regen、referee断電尊重、cap製品/9cells/2.45 V margin、80/120 Wと8/12 A derating・熱/peak時間、4-switch topology、G474RE/LQFP64 pin feasibility、3shunts、precharge/isolation/service port適合、discharge閾値、部品定格。承認前に詳細回路へ進まない。

Cell monitorとbalancingはbank内部blockに置く。追加tap/monitor通信をrobotへ出す可否はS189に照らし公式確認TBD、許可を推測しない。

Energy tolerance: primary usableは−10%新品で855.5063 J、+30%で1235.7313 J。同じ電圧域でも個別cell制約で到達できない場合がある。current reserve15−12=3 Aはport ripple/誤差/latencyに使う暫定余裕、これを検証せずpeak12 Aを許可しない。
