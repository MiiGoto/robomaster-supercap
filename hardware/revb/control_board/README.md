# Rev B 制御基板(案Y)

- `charger.kicad_sch`: ブロック1(入力保護、直列PMOS、LM5176電力段)。仮設計。機能ごとの枠(A〜H)で整理済み。charger.pdfは確認用の出力。
- 生成: `tools/gen_sch/charger.py`(`python3 charger.py <出力先>`)。シンボルは `rev.kicad_sym` に同梱。
- 接続はネットラベルのみ(配線なし)。レイアウトは未整理。
- ERC(KiCad 9.0、2026-10-10): エラー0、警告4(FET4個のフットプリント名がライブラリに無い。未確定)。
- 未確認: ISNS+/-の極性、MODE(ヒカップ)、BIAS=NODE、UVLO値、FET/インダクタのフットプリント。
- 次のブロック: MCU(STM32G431)、電圧/電流計測、保護(OV比較器、PMOS_EN、CHG_INH)、補助電源。
