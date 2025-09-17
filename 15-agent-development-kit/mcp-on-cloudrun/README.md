# MCP on Cloud Run

このリポジトリは、Gemini のツールとして利用できる MCP (Model Context Protocol) サーバーを Cloud Run にデプロイするためのサンプルです。

## 🚀 Cloud Runへのデプロイ

以下のコマンドを実行して、Cloud Run にデプロイします。

```bash
gcloud run deploy mcp-on-cloudrun \
  --source . \
  --region asia-northeast1 \
  --no-allow-unauthenticated
```

**注意:**
*   `--region` は、デプロイしたいリージョンに適宜変更してください。
*   `--no-allow-unauthenticated` フラグにより、このサービスは認証が必須となります。これにより、意図しない外部からのアクセスを防ぎます。

デプロイが成功すると、サービスのURLが表示されます。このURLは次のステップで利用します。

## 🤝 Gemini CLIとの連携

デプロイしたMCPサーバーを Gemini CLI のツールとして連携するには、`~/.gemini/settings.json` ファイルの `mcpServers` に以下の設定を追記します。

```json
{
  "mcpServers": {
    "mcp-on-cloudrun": {
      "httpUrl": "YOUR_CLOUD_RUN_SERVICE_URL",
      "headers": {
        "Authorization": "Bearer $(gcloud auth print-identity-token)"
      }
    }
  }
}
```

**設定のポイント:**
*   `mcp-on-cloudrun`: 任意の名前を設定できます。
*   `httpUrl`: 上記のデプロイで取得した Cloud Run サービスのURLに書き換えてください。
*   `headers.Authorization`: `gcloud` コマンドで取得したIDトークンを `Authorization` ヘッダーに設定することで、Cloud Run サービスへの認証を行います。

これで、Gemini CLI から Cloud Run 上のMCPサーバーをツールとして呼び出すことができるようになります。
