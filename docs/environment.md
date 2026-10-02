# Local environment

確認日: 2026-10-03 JST。既存global設定・PATH・認証は変更していない。

| 項目 | Status | 確認結果 |
|---|---|---|
| OS | Confirmed | Windows NT 10.0.26200.0。OS edition取得はsandboxアクセス拒否のためTBD |
| Git | Confirmed | 2.44.0.windows.1 |
| GitHub CLI | Confirmed | 2.102.0。PATH外の既存workspace local toolを使用 |
| gh auth | Confirmed | 既存keyring認証有効、HTTPS。tokenは保存・公開しない |
| KiCad GUI / CLI | Confirmed | 10.0.6、Program Files/KiCad/10.0/bin。9.0も存在、版未取得 |
| Python | Confirmed | bundled Python 3.12.14。PATH上のpython/pyは確認できず |
| STM32CubeIDE | Confirmed | 1.10.1 / 1.15.1ディレクトリあり。起動・project buildは未検証 |
| STM32CubeMX | Confirmed | 実行ファイルあり。version / 起動はTBD |
| STM32CubeProgrammer | Confirmed | CLI 2.17.0。実機接続は未試験 |
| C/C++ embedded | Confirmed | CubeIDE 1.15.1 bundled arm-none-eabi-gcc 12.3.1 (STM32 12.3.rel1) |
| host toolchain | TBD | PATH上のgcc/clang/cmake検出なし。全インストールの不存在を意味しない |
| Git existing settings | Confirmed | autocrlf=true、credential manager、既存global author設定あり。個人メールは公開しない |
| local repository | Confirmed | 新規独立git init -b main。authorはGitHub公開noreplyをlocal設定 |

親workspaceは別のGit repositoryで、既存の別プロジェクトとlocal toolsに未追跡項目があった。変更・stageしていない。
親のownership検査はコマンド単位のsafe.directoryで確認し、global例外を追加しない。
KiCad CLIはsandbox内でユーザー設定へのアクセス警告があったため、検証は既存ユーザー環境で実行する。
認証設定がsandboxから読めないためghは権限のある実行環境で使用する。認証方式の変更は行わない。
