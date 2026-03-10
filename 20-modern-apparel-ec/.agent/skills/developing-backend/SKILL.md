---
name: developing-backend
description: Python FastAPI によるバックエンドコードを実装する。API エンドポイント、サービス、リポジトリ、Pydantic スキーマ、DB マイグレーションの作成・修正時に使用する。
---

# バックエンド開発

## プロジェクト構造

```
backend/app/
├── api/          # プレゼンテーション層: HTTP パース、バリデーション、委譲のみ
├── services/     # ビジネスロジック、トランザクション、オーケストレーション
├── db/
│   ├── models/   # SQLAlchemy ORM モデル
│   └── repositories/  # 純粋な CRUD、ビジネスロジック禁止
├── schemas/      # Pydantic v2 リクエスト/レスポンスモデル
└── main.py       # アプリエントリポイント、グローバルエラーハンドラ
```

## レイヤールール

1. **`api/`** → `services/` に依存。ここにビジネスロジックを書かない。
2. **`services/`** → `repositories/` に依存。概念的に DB 非依存にする。
3. **`db/repositories/`** → 純粋な SQL/ORM 操作のみ。ビジネスロジック禁止。
4. **`schemas/`** → Pydantic v2 バリデーション用。バリデータにビジネスロジックを書かない。

## 主要な規約

- **非同期**: すべての I/O は `await` する。`AsyncSession` を使用。
- **トランザクション**: `async with db.begin():` ブロックで管理。
- **N+1 問題**: リレーション取得時は必ず `selectinload()` を使う。
- **マイグレーション**: Alembic のみ。手動 DDL 禁止。
- **エラー処理**: リポジトリで `SQLAlchemyError` をキャッチ → `DomainError` に変換。`main.py` で HTTP ステータスにマッピング。
- **型ヒント**: `typing.Annotated` で 100% カバレッジ。
- **ORM モデルを直接フロントエンドに返さない** → 必ず `schemas/` の Pydantic モデルに変換する。

## アンチパターン

- ❌ Pydantic バリデータにビジネスロジックを書く
- ❌ ORM モデルを API レスポンスで直接返す
- ❌ グローバルなミュータブル状態（起動時設定を除く）
- ❌ CPU バウンドな処理でイベントループをブロック（Cloud Tasks にオフロードする）

## ドメイン知識

**価格ルール**: [resources/domain-rules.md](resources/domain-rules.md#価格) を参照
**在庫ポリシー**: [resources/domain-rules.md](resources/domain-rules.md#在庫) を参照
**チェックアウトフロー**: [resources/domain-rules.md](resources/domain-rules.md#チェックアウト) を参照
**顧客・認証**: [resources/domain-rules.md](resources/domain-rules.md#顧客) を参照
**API 標準**: [resources/api-standards.md](resources/api-standards.md) を参照
