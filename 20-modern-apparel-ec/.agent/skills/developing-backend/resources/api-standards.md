# API 標準

## RESTful 設計
- 標準 HTTP メソッド: GET, POST, PUT, DELETE。
- 標準ステータスコード: 200, 201, 400, 401, 404, 500。
- URL 命名: ケバブケース、複数形の名詞（例: `/api/v1/products`）。

## リクエスト / レスポンス
- JSON 形式。キーは `snake_case`。
- 日付: ISO 8601 UTC。
- エラー: RFC 7807（Problem Details）。
