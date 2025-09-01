# 提案されるコマンド

## プロジェクトのセットアップ
- 仮想環境の作成: `uv init`
- 依存関係のインストール: `uv sync`

## プロジェクトの実行
- Dockerイメージのビルド: `docker build -t fastapi-app .`
- バックエンドサーバーの起動: `uv run python app.py` または `docker run -p 8888:8888 --env-file .env fastapi-app` (環境変数がある場合)
- フロントエンドの起動: `index.html`をブラウザで開く (VSCodeのLive Server拡張機能の使用を推奨)

## システムユーティリティコマンド (Windows PowerShell)
- ファイル一覧表示: `Get-ChildItem` または `ls`
- ディレクトリ移動: `Set-Location` または `cd`
- ファイル内容表示: `Get-Content` または `cat`
- ファイル検索: `Select-String` (grepに相当)
- ファイル検索 (再帰的): `Get-ChildItem -Recurse -File | Select-String -Pattern "検索パターン"`
