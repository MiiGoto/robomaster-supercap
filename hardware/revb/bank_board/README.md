# Rev B バンク基板(案Y)

- `bank_board.kicad_sch`: 10S 2.7V 50F、セル毎TLV431+PNPクランプ、XT30、ヒューズ。仮設計。
- 生成: `tools/gen_sch/bank.py`(`KISCH_SYMDIR=hardware/revb/control_board python bank.py <出力>`)。
- ERC: エラー0、警告11(フットプリント未確定)。詳細は `docs/revb/bank_board.md`。
