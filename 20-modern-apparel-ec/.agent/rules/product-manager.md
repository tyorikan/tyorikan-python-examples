# プロジェクト横断ルール

スキル（`.agent/skills/`）でカバーされない、プロジェクト全体に適用されるルールを定義する。

---

## データベース（Cloud Spanner）

- **主キー**: 単調増加する整数（Sequence, Timestamp 等）を PK 先頭にすることは禁止（ホットスポット回避）。UUIDv4（String 型）を使用する。
- **インターリーブ**: 親子関係（例: Orders → OrderItems）には Interleaving を使用し、結合パフォーマンスを最適化する。
- **インデックス**: `WHERE` 句で頻繁に使用されるカラムにはセカンダリインデックスを作成する。
- **SQL**: GoogleSQL（Standard SQL）ダイアレクト。配列型の操作には `UNNEST` を使用する。

---

## Git ワークフロー

### ブランチ戦略
- `main`: 本番稼働可能なコード。
- `feature/*`: 新機能開発用。
- `fix/*`: バグ修正用。

### コミットメッセージ（Conventional Commits）
- `feat: add user login`（機能追加）
- `fix: resolve payment timeout`（バグ修正）
- `docs: update API documentation`（ドキュメント更新）
- `refactor: clean up user service logic`（リファクタリング）

---

## 設計記録

- **ADR**: 重要な技術的決定は `docs/adr/` に Markdown で記録する（タイトル、ステータス、コンテキスト、決定事項、結果）。
- **ダイアグラム**: 設計図は Mermaid で記述する。
