# References and provenance

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
