# KiCad skeleton

Open `robomaster_supercap.kicad_pro` with KiCad 10.0.6。
rootと7 hierarchy pages: CONTROLLER / POWER_INPUT / SUPERCAP_BANK / POWER_STAGE / SENSING / CAN / SAFETY。
説明textのみ。部品、pin、electrical nets、MOSFET、driver、inductor、connector定格の実装なし。
PCBは空のplaceholder。outline、footprint、track、zoneなし。厚さ等のKiCad defaultは承認済み製造仕様ではない。
ERCはparser/hierarchy確認であり電気安全や配線の検証ではない。空boardのDRCはoutlineがない等の未実装結果をexpected limitationとして記録する。
generatorは新規targetのみ作成し既存fileがあれば拒否。通常編集はKiCadで行い、generator再実行で上書きしない。
