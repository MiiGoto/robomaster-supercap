# Verification plan

Task 1: 公開ファイル監査、Markdown link確認、KiCad load/ERCとskeleton構造確認。
実機試験はしていない。将来: enable float/reset/crash、hardware trip、ADC open/short/stuck、CAN timeout、precharge timeout、bus loss、放電後の再上昇を低energy条件から検証する。
requirement ID → procedure → acceptance value → measured result → reviewerのtraceabilityを維持する。閾値未承認の試験を合格としない。
