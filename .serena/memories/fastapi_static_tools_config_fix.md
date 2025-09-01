FastAPIアプリケーションで`/static/tools_config`への404エラーを修正しました。

修正内容:
1. `app.py`に`/static/tools_config`エンドポイントを追加し、`tools_config.json`の内容を返すようにしました。
2. `app.py`のルーティングの優先順位を修正し、`/static/tools_config`エンドポイントが`app.mount`よりも先に処理されるようにしました。
3. `static/config.js`内の`loadToolsConfig()`関数が、`/static/tools_config`ではなく`/tools_config`エンドポイントを呼び出すように修正しました。

最終的な問題は、ブラウザのキャッシュが原因である可能性が高いため、ユーザーにはキャッシュのクリアまたはハードリロードを推奨しました。