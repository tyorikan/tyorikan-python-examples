---
name: designing-api
description: OpenAPI と Pydantic スキーマを使って RESTful API のコントラクトを設計する。新規エンドポイントの定義、リクエスト/レスポンス形式の変更、API 設計のレビュー時に使用する。
---

# API 設計

## 基本原則

1. **リソース指向**: 動詞（`/getUsers`）ではなく名詞（`/users`）。階層構造: `/users/{id}/orders`。
2. **ステートレス**: Bearer トークン認証。API ロジックのためのサーバーサイドセッション禁止。
3. **追加的進化**: 破壊的変更を行わない。バージョンプレフィックス: `/api/v1/...`。

## リクエスト設計

- **フィルタリング**: クエリパラメータで `GET /items?color=red`。ボディではなくクエリを使う。
- **ページネーション**: カーソルベース `?limit=20&page_token=...`（Spanner フレンドリー）。
- **部分更新**: スパースフィールドセットによる `PATCH`。

## レスポンス設計

- **エンベロープ**: デフォルトはベア（裸）。メタデータ（ページネーション等）がある場合のみエンベロープを使う。
- **エラー**: RFC 7807 形式:
  ```json
  {
    "type": "error:inventory-insufficient",
    "title": "Not enough inventory",
    "detail": "Requested 5, only 2 available.",
    "instance": "/orders/123"
  }
  ```

## OpenAPI ドキュメント

- すべてのエンドポイントに `summary` と `description` を記述する。
- すべてのスキーマフィールドに `example` を含める。

## リファレンス

Google Cloud API Design Guide (AIPs) がゴールデンスタンダード。
