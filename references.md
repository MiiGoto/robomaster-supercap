# References and provenance

## Task 4 layout principles (access2026-10-03 JST)

| Source / author | Rights / use / difference |
|---|---|
| [SSZTAE5 Feb2017 / Vijay Choudhary, TI](https://www.ti.com/document-viewer/lit/html/SSZTAE5/GUID-1402DA8B-73DB-44B4-B203-A3AF307A6C45) | TI著作物、linkのみ。両port hotloop/dvdt/sense隔離の原理を参照。自作MCU/driver構成、layout未実装 |
| [SSZT533 Feb2019 / Youhao Xi, TI](https://www.ti.com/document-viewer/lit/html/SSZT533/GUID-8E8A4702-76CD-495F-A121-6F12027C6292) | TI著作物、linkのみ。gateとreturnの閉loop面積を参照。第三者画像/PCBデータをコピーしない |


## Task 3 manufacturer shortlist (2026-10-03 JST)

全てメーカー著作物、転載許諾は仮定せずURLと自作の比較・数値だけを記録。PDF/画像/schematic/PCBの公開repositoryコピーなし。利用目的は候補比較・計算で、メーカーreference回路の複製やvalidated設計の主張は行わない。

| Source / author | Revision / access | Use / difference from own design |
|---|---|---|
| [CSD18540Q5B / TI](https://www.ti.com/lit/ds/symlink/csd18540q5b.pdf) | SLPS488B Apr2017;2026-10-03 | RDS/Qg/Qrr/thermal候補根拠、own designのsurge/熱/PWM未確定 |
| [CSD18563Q5A / TI](https://www.ti.com/lit/ds/symlink/csd18563q5a.pdf) | SLPS444C Jan2016;2026-10-03 | 低Qg代替比較、同じdatasheet test条件を実動作としない |
| [UCC27282 / TI](https://www.ti.com/lit/ds/symlink/ucc27282.pdf) | SNVSAQ5B May2022;2026-10-03 | DRC EN/interlock/UVLO、独立HI/LI kill/disconnectが別途必要 |
| [UCC27211A / TI](https://www.ti.com/lit/ds/symlink/ucc27211a.pdf) | SLUSBL4D Jul2024;2026-10-03 | driver代替、外部EN/interlock要求はown design |
| [XAL1510 / Coilcraft](https://www.coilcraft.com/getmedia/cd1cef27-13f0-4568-8894-f7311475209b/xal1510.pdf) | Document947 revised05/04/26;2026-10-03 | 15/22µH DCR/Isat/Irms、DC bias/thermal適合は未確定 |
| [INA240 / TI](https://www.ti.com/lit/ds/symlink/ina240.pdf) | SBOS662C Dec2021;2026-10-03 | signed shunt amp、own designは別fast comparatorを要求 |
| [INA241A / TI product](https://www.ti.com/product/INA241A) | product page2026-10-03;datasheet版TBD | 高速代替比較のみ、PDF取得失敗につきpin/settling未照合 |


Accessed: **2026-10-03 JST**。外部ファイルのコピーなし。README/公開記事の限定的な調査で、schematic netlist/PCBを監査したものではない。
UnknownはTBD。以下のlicenseは対象sourceに限り、関連hardwareへの包括許諾とはしない。

| ID | Project / author / source URL | License / scope | 参考にした内容 | 自分の設計との違い |
|---|---|---|---|---|
| R1 | [RM2023-SuperCapacitor / HKUST ENTERPRIZE](https://github.com/hkustenterprize/RM2023-SuperCapacitor) / [BBS作者記事](https://bbs.robomaster.com/article/9452?source=8) | GitHub GPL-3.0表示。ただしBBSに隊間交流・非商用制限の記載があり整合TBD、再利用しない | 四switch双方向制御とcontrol/power分離の設計意図 | 本projectは独立fast trip・fault isolationを要求、定格は未決定 |
| R2 | [PSP_supercapacitor / Pacific Spirit・Great Lakes / wele0612](https://github.com/wele0612/PSP_supercapacitor) | repository GPL-3.0、文書CC-BY-SA表記(version TBD)、外部hardware scope TBD | 多相parallel、ADC基準とfirmware校正の一致 | 多相はまだ採用せず、校正不整合をsafety requirement化 |
| R3 | [SP_Ultra_CAP / Hebei University of Technology 山海Mas / Sirius-RX](https://github.com/Sirius-RX/SP_Ultra_CAP) | MIT表示、各assetへのscopeは再利用時確認 | single-board統合・mode切替・current calibration問題 | 必要telemetryと保護に限定し、UI/IMUを要求しない |
| R4 | [Electrical-System / PurdueRM](https://github.com/PurdueRM/Electrical-System) | rootで明示license未確認(TBD)、再利用不可として扱う | passive bankとSTM32 chargerの分割 | assistを含む双方向energy管理とshutdownを明示 |
| O1 | [RoboMaster公式hub / RMOC](https://bbs.robomaster.com/wiki/20204847) / [公式download](https://www.robomaster.com/zh-CN/resource/download/competition) | DJI著作物、転載しない | 適用規則の一次入口 | 本projectの数値確定は人間レビュー後 |
| O2 | [公式2026制作規則V1.3.0](https://bbs-web-static.robomaster.com/715e2519e5384666a5d13edda17c6b831770696773838/RoboMaster%202026%20%E6%9C%BA%E7%94%B2%E5%A4%A7%E5%B8%88%E9%AB%98%E6%A0%A1%E7%B3%BB%E5%88%97%E8%B5%9B%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%88%B6%E4%BD%9C%E8%A7%84%E8%8C%83%E6%89%8B%E5%86%8CV1.3.0%EF%BC%8820260209%EF%BC%89.pdf) / RMOC | ©2026 DJI、リンクのみ | S5–7、3.12、S184–189本文 | 最新版・対象への適用はTBD、規定値は部品定格でない |
| M1 | [STM32 migration AN5094 / STMicroelectronics](https://www.st.com/resource/en/application_note/an5094-migrating-between-stm32f334303-lines-and-stm32g431xxg474xxg491xx-microcontrollers-stmicroelectronics.pdf) | ST資料、リンクのみ | G474/F334のtimer/ADC/CAN比較 | exact MCU/package/pinsはTBD |
| M2 | [STM32F334 documentation / STMicroelectronics](https://www.st.com/en/microcontrollers-microprocessors/stm32f334/documentation.html) | ST資料、リンクのみ | DS9994/RM0364/errataへの入口 | 対象revisionの確認は選定時 |
| M3 | [STM32 digital power ecosystem / STMicroelectronics](https://www.st.com/content/st_com/ja/ecosystems/stm32-digital-power.html) | ST資料、リンクのみ | HRTIM/PWM同期制御の候補根拠 | evaluation boardの回路・定格を流用しない |

## Discovery-only pointers (not a specification authority)

- [2026 rule index](https://github.com/Fbnnkk/rm-battlescope/blob/main/docs/RMUC_2026_%E8%A7%84%E5%88%99%E4%B8%8E%E6%95%B0%E6%8D%AE%E7%B4%A2%E5%BC%95.md): 後続V2.0.0の存在を示す手がかりのみ。
- [CQU QIANLI resources](https://team.cquqian.li/museum/resources.html): V2.0.0制作規則、V2.2.0競技規則、2027資料の案内。PDF linkは404。これらの値を要求に使用しない。

調査は4チームの4設計で停止。R1が過去の他チーム設計から影響を受けているため完全な系譜独立ではないが、同一repositoryのfork4件ではない。R1とR2/R3の双方向案に対しR4の分離charger/bankを対比する。
BBSを入口として優先し、閲覧可能なGitHub作者資料で補完した。各sourceのauthor-reported performanceは独立検証していない。

## Task 2 verified evidence (2026-10-03 JST)

Task1 O2の「適用TBD」は本表のRMUL指定と公式アーカイブ確認で更新。第三者indexのRMUC後期版はRMULに適用しない。資料は.local/researchに調査用保存、gitignore対象で公開しない。以下はauthor/manufacturer著作物、redistribution license未確認のためlinkのみ。自作doc/modelは独立した要約/計算で回路転載なし。

| ID | Source / author / version | Use | Difference from our design |
|---|---|---|---|
| T2-O1 | [Official hub / RMOC](https://bbs.robomaster.com/wiki/20204847) → Archives→2026→RMUL | RMUL掲載最新版: CN rules1.2.0 / specs1.3.0 | 開催地補足・答疑はTBD |
| T2-O2 | [RMUL rules EN V1.2.0 20260113 / DJI](https://bbs-web-static.robomaster.com/bf8d1954e384499281310380b4a293b71768291609875/RoboMaster%202026%20University%20League%20Rule%20Manual%20V1.2.0%EF%BC%8820260113%EF%BC%89.pdf) | 3V3/Infantry Match区別、power limits、referee60J/10Hz | assist target80/120Wは独自計算Assumption、公式出力許可ではない |
| T2-O3 | [制作CN V1.3.0 20260209 / DJI](https://bbs-web-static.robomaster.com/0af874e7e10a4f9eb7c3c4872e47f03b1770636018010/RoboMaster%202026%20%E6%9C%BA%E7%94%B2%E5%A4%A7%E5%B8%88%E9%AB%98%E6%A0%A1%E7%B3%BB%E5%88%97%E8%B5%9B%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%88%B6%E4%BD%9C%E8%A7%84%E8%8C%83%E6%89%8B%E5%86%8CV1.3.0%EF%BC%8820260209%EF%BC%89.pdf) | S5–7/141/145/184–189、22–26V module入力、30V robot上限 | Chassis出力波形/実robot仕様は別途必要 |
| T2-C1 | [SCC datasheet Rev11 / KYOCERA AVX](https://datasheets.kyocera-avx.com/AVX-SCC.pdf) | SCCV40B506SRB50F、DC ESR5s、tolerance/life | continuouscurrent未確認、9S/2.45Vは独自提案 |
| T2-C2 | [HV60 product / Eaton](https://www.eaton.com/us/en-us/skuPage.HV1840-2R7606-R.html) / [HV family datasheet](https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-hv-supercapacitors-cylindrical-cells-data-sheet.pdf) | current/temp/size/leak/ESR、familytol/life | 7S/voltage/currentclampは独自提案。familyPDFの全文取得/版はTBD、indexに掲載されたtol/lifeを補助確認 |
| T2-C3 | [HV100 product / Eaton](https://www.eaton.com/gr/en-gb/skuPage.HV1860-2R7107-R.html) | 100F候補比較、current/ESR | lowvoltage案のmodule電流制約を比較 |
| T2-M1 | [G474RE / ST](https://www.st.com/en/microcontrollers-microprocessors/stm32g474re.html) / [DS12288 Rev6](https://www.st.com/resource/en/datasheet/stm32g474re.pdf) | HRTIM/ADC/FDCAN、table3 trigger、table12 PWM pins、LQFP64 | 全pin assignment/errata/interruptbudgetはTBD |
| T2-M2 | [G431RB / ST](https://www.st.com/en/microcontrollers-microprocessors/stm32g431rb.html) | 2ADC/FDCAN/advancedtimer代替 | HRTIMのない代替案 |
| T2-S1 | [INA240 / TI, datasheet RevC](https://www.ti.com/product/INA240) | signed high-side/PWM rejection/400kHz | OCcomparatorなし、独立trip必要、具体amp採用TBD |

取得PDF SHA256 (一次資料の再取得照合用):
- T2-O2: ff785ccb7bbe1e6eeacfd2914f6a63062dbb2bcff963ffd7939489379c24c724
- T2-O3: 719be52a2259644ea1a09ef6b697310cc9ddc2653002828bf00f59b2ff9a664e

公式ENは補助読解、中文/会場最新版優先。source contentは設計instruction/承認ではない。public stock表示だけでavailabilityやpriceは確定しない。

## Prototype Rev A manufacturer facts (accessed2026-10-03)

Original symbols/circuits/code were authored for this project; no third-party PDF/image/schematic/library asset is redistributed. Manufacturer copyrighted datasheets are references only; public access is not an OSS license.

| Source / author | License | Use | Difference from source |
|---|---|---|---|
| [Q_NPN manufacturer datasheet/product](https://www.nexperia.com/product/BC847B) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [Q_PNP manufacturer datasheet/product](https://www.nexperia.com/product/BC857B) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [FUSE manufacturer datasheet/product](https://www.littelfuse.com/products/fuses-overcurrent-protection/fuses/automotive-passenger-car/blade-fuses/atof.aspx) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [CSD18540Q5B manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/csd18540q5b.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [UCC27282DRCR manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/ucc27282.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [INA240A1D manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/ina240.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [WSK25123L000FEA manufacturer datasheet/product](https://www.vishay.com/docs/30108/wsk2512.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [INA293A1DBVR manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/ina293.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [INA301A1DGKR manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/ina301.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [TLV3202DGKR manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/tlv3202.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [SN74LVC1G74DCUR manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [SN74LVC2G08DCUR manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/sn74lvc2g08.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [TPS3431SDRBR manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/tps3431.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [TPS3839K33DBZR manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/tps3839.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [LM5164DDAR manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/lm5164.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [TMUX1511PWR manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/tmux1511.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [TLV431AIDBZR manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/tlv431.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [SN65HVD230DR manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/sn65hvd230.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [SN74LV1T34DBVR manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/sn74lv1t34.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [BQ7694204PFBR manufacturer datasheet/product](https://www.ti.com/lit/ds/symlink/bq76942.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [STM32G474RET6 manufacturer datasheet/product](https://www.st.com/resource/en/datasheet/stm32g474re.pdf) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [CONTACT manufacturer datasheet/product](https://industry.panasonic.com/global/en/products/control/relay/vehicle/number/aev14012) | Manufacturer copyright; no reuse license assumed | Pin/rating/package factual review | Own9S bidirectional prototype and safety chain; no copied assets |
| [TMUX1511 TI](https://www.ti.com/lit/ds/symlink/tmux1511.pdf) | TI copyright |3.6V off protection,2µA leakage bound |100k ADC drains and bank/bus clamp proposal |
| [SN74LV1T34 TI](https://www.ti.com/lit/ds/symlink/sn74lv1t34.pdf) | TI copyright |1.8→3.3V translation |BQ initial MISO translation |
| [NTCLE100E3 Vishay](https://www.vishay.com/docs/29049/ntcle100.pdf) | Vishay copyright |10k/β3977 probe |3 independent hotspot paths and tunable trip windows |
| [XAL1510 Coilcraft](https://www.coilcraft.com/getmedia/cd1cef27-13f0-4568-8894-f7311475209b/xal1510.pdf) | Coilcraft copyright |22/15µH ratings |200kHz candidate current calculation, no PCB copied |

## Delegated Rev A selections — accessed2026-10-04

Manufacturer sources below retain copyright;no reuse license assumed. Only original selection/configuration/calculation prose and factual part numbers are committed. No source PDF,image,schematic,library or PCB is copied. Author is the named manufacturer;differences are our9S supercap converter,external bench containment and prototype-only acceptance envelope.

| Source / author | Reviewed evidence | Use / difference |
|---|---|---|
| [BQ76942 TRM,Texas Instruments](https://www.ti.com/lit/ug/sluuby1b/sluuby1b.pdf) |SLUUBY1B April2022:data-memory address/format,pin polarity,9S mask,50.6mV thresholds |Original39-entryRAM profile;not Li-ion defaults or copied firmware |
| [Low-side FET application note,TI](https://www.ti.com/lit/an/sluaa84a/sluaa84a.pdf) |SLUAA84A:logical permits,FET_CTRL_EN,charge-pump disabled |External latch/PWM kill rather than external low-side pack FETs;CP tied BAT |
| [DCHG/DDSG mapping FAQ,TI](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1237508/faq-bq76952-do-the-dchg-and-ddsg-signals-on-the-bq769x2-follow-the-chg-and-dsg-fet-driver-pin-states) |Fast-output protection masks |Avoid undocumented250ms/1s mapping delays;still measure actual path |
| [MINI99758V,Littelfuse](https://www.littelfuse.com/assetdocs/littelfuse-datasheet-997-mini58v?assetguid=838cc4ad-f429-4185-a8e8-ccc70cd2b713) |58V/1000A interrupt,typical meltingI²t |10/15/5A assembly selections;no claim of guaranteed silicon coordination |
| [0FHM0002ZXJM,Littelfuse](https://www.littelfuse.com/ja-jp/products/fuses-overcurrent-protection/fuse-holders-fuse-blocks-accessories/fuse-holders/in-line-fuse-holders/mini-fhm/0fhm0002zxjm) |58V MINI holder family |External wiring,not PCB fuse land |
| [DDR-60,MEAN WELL](https://www.meanwell.com/Upload/PDF/DDR-60/DDR-60-SPEC.PDF) |2026-03-31 edition:pinout,input derating,inrush |12V actuator supply with24W reserved output,not gate bias rail |
| [AQZ202G,Panasonic](https://industry.panasonic.com/global/en/products/control/relay/photomos/number/aqz202g) |AC/DC PhotoMOS rating and input current |Low-current precharge;main contacts remain AEV14012 |
| [PhotoMOS power-series datasheet,Panasonic](https://industry.panasonic.com/ac/cdn/e/control/relay/photomos/catalog/semi_eng_pwr1a_aqz10_20.pdf) |AC/DC load pins3/4,input−1/+2 |Original physical pin table,no imported symbol |
| [EEUFR1J471,Panasonic](https://na.industrial.panasonic.com/products/capacitors/aluminum-electrolytic-capacitors/radial-lead-type/series/83367/model/83797) |470uF63V,1995mArms100kHz,12.5Dx25L,5mm pitch |Six parallel/link,ripple sharing allowance and increased precharge time |
| [MLCC component list,Murata](https://www.murata.com/-/media/webrenewal/tool/library/common-pdf/static-model/component-list-s-mlcc-2506.ashx?cvid=20250805040438000000&la=ko-kr) |Nominal ceramic selections/size/ratings |No nominal-C claim under DC bias;exact suffix stock unverified |
| [C1210C226K3RACTU,KEMET](https://search.kemet.com/download/specsheet/C1210C226K3RACTU) |22uF25V1210 |Aux output selection;stability must be tested |
| [C0805C104K5RACTU,KEMET](https://search.kemet.com/download/specsheet/C0805C104K5RACTU) |100nF50V0805 |Selected local bypass;no vendor library copied |
| [CRCW e3,Vishay](https://www.vishay.com/docs/20035/dcrcwe3.pdf) |Ordering codes,size,rated power/voltage |Original resistor MPN mapping;E96 feedback values909k/174k |
| [WSK2512,Vishay](https://www.vishay.com/docs/30108/wsk2512.pdf) |2023-12-11:3mR usesT2.21mm terminals |Corrects previousT1.19 assignment;four-terminal geometry check |
| [HS25 100R F,Ohmite](https://www.ohmite.com/catalog/hs-series/HS25_100R_F) |100ohm25W heat-sinkable product |External precharge/dump/tool resistor;not a PCB axial land |
| [HS mechanical/thermal documentation,Ohmite](https://www.ohmite.com/hs-aluminium-housed-resistors/) |Body dimensions and heatsink requirements;web electrical table has shifted columns |Product choice retained;PDF retrieval403 after bounded attempts. Do not treat malformed web table as a validated thermal-rating table |
| [6006 comparison,Blue Sea Systems](https://www.bluesea.com/products/compare/6004/6004200/6005200/6006/6006200) |48VDC/25A switching listing |Manual healthy/load-off isolation;not an emergency fault breaker |
| [5859 specification,Alpha Wire](https://www.alphawire.com/disteAPI/SpecPDF/DownloadProductSpecPdf?productPartNumber=5859) |14AWG/PTFE electrical/temp facts |Short bench wiring choice;no bundled-current guarantee or source document reproduction |
