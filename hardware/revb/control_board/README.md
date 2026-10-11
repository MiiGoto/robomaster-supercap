# Rev B 制御基板(案Y)

- `charger.kicad_sch`: ブロック1(入力保護、直列PMOS、LM5176電力段)。仮設計。機能ごとの枠(A〜H)で整理済み。charger.pdfは確認用の出力。
- 生成: `tools/gen_sch/charger.py`(`python3 charger.py <出力先>`)。シンボルは `rev.kicad_sym` に同梱。
- 接続はネットラベルのみ(配線なし)。レイアウトは未整理。
- ERC(KiCad 9.0、2026-10-10): エラー0、警告4(FET4個のフットプリント名がライブラリに無い。未確定)。
- 未確認: ISNS+/-の極性、MODE(ヒカップ)、BIAS=NODE、UVLO値、FET/インダクタのフットプリント。
- 次のブロック: MCU(STM32G431)、電圧/電流計測、保護(OV比較器、PMOS_EN、CHG_INH)、補助電源。

## 更新(2026-10-10)
- `control.kicad_sch`: ブロック2(補助電源、STM32G431、計測、保護/イネーブル論理、CAN/UART)。`control_board.kicad_sch` が階層ルート。ERC 0 errors(コミット45ba58d)。
- 上の「次のブロック」は実施済み。残り: フットプリント確定、部品在庫確認、バンク基板との整合。

## 改訂(2026-10-11): 配線ありの回路図に描き直し
- 4シート構成: `power_input`(入力保護・直列PMOS・入力シャント・ISNSオフセット・INA240)、`buckboost`(LM5176・電力段・出力ノード・キャパシタ側電流)、`mcu`(補助3.3V・STM32G431・CAN・UART・LED)、`protect_sense`(分圧・基準・OV比較器・イネーブル論理)。ルートは `control_board.kicad_sch`。PDF: `control_board.pdf`。
- 生成: `tools/gen_sch/build2.py <出力先>`(kisch2.py: ワイヤ・電源シンボル描画、生成後にKiCadのネットリストと意図ネットを照合)。
- ERC(KiCad 9.0、2026-10-11): エラー0、警告0。
- 旧版(ラベルのみ)は `_superseded/` に移動。
- レビューで直した点: 2N7002の記号ピン(GDS→GSD、SOT-23でD/S逆だった)、電力FETの記号(3ピン→TDSON-8の8ピン対応)、FET耐圧40V→60V級、出力コンデンサ35V→50V、NODEにTVS追加、比較器にヒステリシス追加、EN_PMOS直列1k→4.7k、補助電源入力に10R追加、CAN終端(DNP)追加、ISNSオフセット回路(MCUのDACで入力電流上限を可変)追加、ICAP_SをPA4→PA6へ移動(PA4はDAC)。
- 未決: 充電電圧26.2Vか25.6V(バンク基板のクランプ下限との関係、docs/revb/bank_board.md)、電力FET型番、インダクタ・ヒューズ・電解の型番とフットプリント、CAN/審判UARTコネクタのピン配置、MODE抵抗の意味(データシート再確認)。

## 改訂(2026-10-11): 部品確定・基板(配置/配線)
- 部品はJLCPCBで在庫・価格を確認して選定(Basic/Preferred優先)。一覧: `jlcpcb_bom.csv`(59行、LCSC番号付き)。主な部品: 電力FET NTMFS5C670NL(C179626)×4、インダクタ SLO1365S100MTT 10uH(C242228)、ヒューズ 10A 1206、TVS SMBJ30A、XT30UPB-M(縦型)×3、小信号は0402。
- 定数変更: 出力 1.5M/47k = 26.33 V(Basic値)、UVLO 220k/15k ≈ 19.3 V、入力OV 150k/6.8k ≈ 28.8 V、ノードOV 100k/4.7k ≈ 27.8 V、電流検出 10→12 mΩ(谷/ピーク制限 ≈6.7 A/10 A)。CANはGH 2ピン(1=CANH, 2=CANL)。終端120RとSWDヘッダは未実装(DNP)。
- XT30のピン: AMASSフットプリントに合わせ **pin1 = −(GND)、pin2 = +** に修正。
- 基板 `control_board.kicad_pcb`: 68×57 mm(Taobao基板 69×58 mm 以内)、4層(F: 部品+電力パワープレーン、In1: GND、In2: 信号、B: 信号+GND)、片面実装、M3穴×3。
- 配線: 電力経路は銅箔ゾーン、信号はFreerouting+補助ルータ(`tools/gen_pcb/`)。KiCad 9.0 DRC(2026-10-11): エラー0、未配線0。警告154は主にライブラリ版との差異(フットプリントは旧ライブラリ版を埋め込み)とシルク重なり。
- 製造データ: `fab/control_board_gerber.zip`、`fab/jlcpcb_cpl.csv`、`jlcpcb_bom.csv`。**発注前にJLCPCBのプレビューで回転・極性(XT30、ダイオード、電解、IC1番ピン)を必ず確認すること。**
- 未検証・要確認: SO-8FL(FET)とSLO1365(インダクタ)は近い既存フットプリントを流用、CSLOPE 220p(Rcs 12 mΩで再計算)、ゲート配線が長い箇所あり(昇圧側)、ビア0.5/0.25 mmが42個(JLCの追加料金対象の可能性)。
