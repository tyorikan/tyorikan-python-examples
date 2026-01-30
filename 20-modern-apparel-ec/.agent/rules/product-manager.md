# 開発標準・実装ルールガイドライン

このドキュメントは、**Modern Apparel EC** プロジェクトにおける開発標準、アーキテクチャ原則、およびコーディング規約を定義したものです。すべて開発者は、一貫性、保守性、拡張性を確保するために、これらのルールに従う必要があります。

---

## 1. アーキテクチャ原則 (Architectural Principles)

### 1.1 クリーンアーキテクチャ & ドメイン駆動設計 (DDD)
**Clean Architecture** のアプローチを採用し、ドメイン駆動設計 (DDD) の概念を取り入れます。
*   **Domain Layer (内側)**: 純粋なビジネスロジック、エンティティ、ユースケース。外部への依存を持ちません。
*   **Infrastructure Layer (外側)**: インターフェースの実装（DBアクセス、外部API）、フレームワーク固有のコード。
*   **依存性のルール**: 依存の方向は常に **内側** に向かいます。ドメイン層はデータベースやWebフレームワークについて何も知りません。

### 1.2 アーキテクチャ決定記録 (ADR)
重要な技術的決定は、**ADR** フォーマット（Markdown）を用いて `docs/adr/` に記録します。
*   **フォーマット**: タイトル、ステータス、コンテキスト、決定事項、結果（メリット・デメリット）。

### 1.3 ダイアグラム (Mermaid)
システム設計図（ER図、シーケンス図、フローチャート）は、Markdownファイル内に **Mermaid** を使用して記述します。

---

## 2. バックエンド開発 (FastAPI)

### 2.1 プロジェクト構成
関心事を分離したレイヤードアーキテクチャを採用します:
```
app/
├── api/            # API層 (ルーティング, 依存関係定義)
│   └── v1/
├── core/           # 設定, セキュリティ, ロギング
├── db/             # データベース接続 & 汎用リポジトリ
├── models/         # データベースモデル (SQLAlchemy/Spanner)
├── schemas/        # Pydantic Schemas (DTO)
└── services/       # ビジネスロジック層
```

### 2.2 コーディング規約
*   **Async/Await**: すべてのI/O操作（DB, APIコール）は **非同期** (`async def`) で実装します。
*   **型ヒント**: `typing` と `pydantic` を使用し、100%の型カバレッジを目指します。
*   **Pydantic V2**: Pydantic V2 の記法（例: `model_config = ConfigDict(...)`）を使用します。
*   **依存性の注入 (DI)**: サービスやDBへの依存は、FastAPIの `Depends` を使用して注入します。

### 2.3 API設計
*   **RESTful**: 標準的なREST規約に従います。
*   **レスポンス形式**: すべてのAPIレスポンスは以下のJSON構造に統一します:
    ```json
    {
      "success": true,
      "data": { ... },
      "meta": { "page": 1, "total": 100 },
      "error": null
    }
    ```
*   **OpenAPI**: ドキュメントはFastAPIによって自動生成されます。各エンドポイントには明確な説明（summary, description）を記述してください。

---

## 3. フロントエンド開発 (React)

### 3.1 プロジェクト構成 (Feature-Based)
技術種別ではなく、**ドメイン機能 (Feature)** 単位でコードを整理します:
```
src/
├── features/       # 機能モジュール
│   ├── auth/       # (components, hooks, api, types)
│   └── products/
├── components/     # 共通UIコンポーネント (Button, Input)
├── lib/            # 共通ユーティリティ (axios, cn)
└── hooks/          # 共通Hooks
```

### 3.2 コーディング規約
*   **TypeScript**: Strictモードを有効化。`any` 型の使用は禁止です。
*   **コンポーネント設計**:
    *   共通コンポーネントには **Atomic Design** の原則を適用します。
    *   スタイルのバリエーション管理には `class-variance-authority` (cva) を使用します。
    *   スタイリングには **Tailwind CSS** を使用します。
*   **状態管理**:
    *   **サーバー状態**: **TanStack Query** (React Query) を使用します。
    *   **フォーム状態**: **React Hook Form** + **Zod** (スキーマバリデーション) を使用します。
    *   **グローバルクライアント状態**: 原則使用せず、必要な場合のみ最小限の Context または Zustand を使用します。

---

## 4. データベース (Google Cloud Spanner)

### 4.1 スキーマ設計
*   **主キー (Primary Keys)**:
    *   **禁止**: 単調増加する整数（Sequence, Timestampなど）をPKの先頭にすること（ホットスポット回避のため）。
    *   **推奨**: UUIDv4（String型）または分散性のあるビジネスキー。
*   **インターリーブ**: 親子関係（例: Orders -> OrderItems）には **Interleaving** を使用し、結合パフォーマンスを最適化します。
*   **インデックス**: `WHERE` 句で頻繁に使用されるカラム（例: `Email`）にはセカンダリインデックスを作成します。

### 4.2 SQL標準
*   **GoogleSQL** (Standard SQL) ダイアレクトを使用します。
*   配列型の操作には `UNNEST` を使用します。

---

## 5. インフラ & DevOps

### 5.1 コンテナ化
*   **マルチステージビルド**: 本番用Dockerfileは、イメージサイズ最小化のために必ずマルチステージビルドを使用します。
*   **非特権ユーザー**: セキュリティのため、アプリケーションは非rootユーザーで実行します。

### 5.2 CI/CD
*   **GitHub Actions**:
    *   **CI**: Pull RequestごとにLint (Black, ESLint) とテスト (Pytest, Vitest) を実行します。
    *   **CD**: mainブランチへのマージ時に、`gcloud` または Terraform を介して Cloud Run へデプロイします。

### 5.3 Infrastructure as Code (IaC)
*   **Terraform**: すべてのクラウドリソース（Spanner, Cloud Run, IAM）は Terraform で定義・管理します。

---

## 6. Gitワークフロー

### 6.1 ブランチ戦略
*   `main`: 本番稼働可能なコード。
*   `feature/*`: 新機能開発用ブランチ。
*   `fix/*`: バグ修正用ブランチ。

### 6.2 コミットメッセージ
**Conventional Commits** に従ってください:
*   `feat: add user login` (機能追加)
*   `fix: resolve payment timeout` (バグ修正)
*   `docs: update API documentation` (ドキュメント更新)
*   `refactor: clean up user service logic` (リファクタリング)
