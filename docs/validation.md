# Task 1 validation

実施日: 2026-10-03 JST。KiCad 10.0.6 / Python 3.12.14 / Git 2.44.0。

| Check | Result | Limit |
|---|---|---|
| KiCad load and hierarchy export | root + 7 child、8 SVG pages出力成功 | graphic/text skeletonのみ |
| schematic ERC | 0 errors / 0 warnings | symbols/netsなし。実回路の安全・定格を証明しない |
| empty PCB DRC | 1 error: invalid_outline / Edge.Cutsなし、0 unconnected pads | 未設計boardの想定結果。DRC合格や製造可能とはしない |
| publication audit | tools/audit_publication.pyでcandidate files / reachable commitsを検査 | 自動検査だけで秘密・権利の不存在を保証しない |
| local Markdown links | audit時にrelative link存在確認 | external URL全数のlive availability検証ではない |
| source provenance | authored docs / own skeleton / own helper codeのみ | 外部PDF・画像・schematic・PCB・codeなし |
| firmware / real hardware | 未実施 | implementation / prototypeはscope外 |

CLI outputsとSVGはignored `.local/validation/`に保持し、OSのabsolute pathなどを公開しない。
ERC/DRC既定設定で無効なcheckもreportにある。保護を無効化してerrorを消す変更はしていない。
project生成scriptは既存targetを拒否する。通常のKiCad follow-up編集で再生成しない。

PUBLIC前の手動確認: file一覧とdiff、既知secret形式、個人email、private/proprietary URL・情報、third-party asset、license attributionを確認する。
公開commitはGitHub公開noreply authorを使い、既存global identityは変更しない。
本projectのlicenseはownerによる選択TBD。外部公開designのlicense整合が不明な場合は再利用しない。
