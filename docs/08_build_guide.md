# ビルド手順書 (TikTok Toolkit)

本ドキュメントでは、`tiktok_toolkit` の実行ファイル (`tiktok.exe`) をビルドする手順について説明します。

## 前提条件

- Python がインストールされていること
- 必要なライブラリがインストールされていること (`pip install -r requirements.txt`)
- `PyInstaller` がインストールされていること

## ビルドコマンド

`tiktok_toolkit` ディレクトリ直下で以下のコマンドを実行してください。

```powershell
pyinstaller --noconfirm --onefile --windowed --name "tiktok" --distpath "./dist" --add-data "config.json;." --add-data "initial_settings.xlsx;." tiktok.py
```

### オプションの説明

- `--noconfirm`: 出力先ディレクトリが既に存在する場合に確認なしで上書きします。
- `--onefile`: 依存関係をすべて1つの `.exe` ファイルにまとめます。
- `--windowed`: 実行時にコマンドプロンプト（コンソールウィンドウ）を表示しません。
- `--name "tiktok"`: 出力ファイル名を `tiktok.exe` に指定します。
- `--distpath "./dist"`: ビルド生成物の出力先を `dist` ディレクトリに指定します。
- `--add-data "config.json;."`: `config.json` を実行ファイルに同梱します（Windows用の区切り文字 `;` を使用）。
- `--add-data "initial_settings.xlsx;."`: `initial_settings.xlsx` を実行ファイルに同梱します。

## 出力物

ビルドが成功すると、以下のパスに実行ファイルが生成されます。

`tiktok_toolkit/dist/tiktok.exe`

## トラブルシューティング

### ビルドエラーが発生する場合

1. `build` ディレクトリおよび `dist` ディレクトリを削除してから再度実行してください。
2. 仮想環境 (`venv` など) が有効になっているか確認してください。
3. `PyInstaller` のバージョンが古い場合はアップデートしてください: `pip install --upgrade pyinstaller`
