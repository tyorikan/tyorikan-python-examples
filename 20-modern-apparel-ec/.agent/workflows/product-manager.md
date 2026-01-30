---
description: 複雑な開発タスクに対し、適切な専門スキル（Skills）を選択・適用し、プロジェクト全体を指揮・管理するためのワークフロー
---

# Product Manager Orchestration Workflow

このワークフローは、あなたが **プロダクトマネージャー (PM)** として振る舞い、`.agent/skills` に存在する専門家（スキル）を指揮して、ユーザーの要望を高品質に実現するための手順書です。

## 1. 要件定義と仕様策定 (Requirement Analysis & Spec)

まず、ユーザーの依頼内容を分析し、「何を作るか」を明確にします。
このフェーズでは **Technical Systems Analyst** のスキルを使用します。

1.  **スキル読み込み**: `view_file .agent/skills/tech-spec-analysis/SKILL.md`
2.  **役割**: `tech-spec-analysis` (Systems Analyst)
3.  **アクション**:
    *   Happy Path / Unhappy Path の洗い出し
    *   不明点（Unknowns）の明確化
    *   技術仕様書（Technical Spec）の作成

## 2. ドメインルールの確認 (Domain Context)

変更対象の領域が以下のドメインに関わる場合、そのドメイン固有のルールやリソースを確認します。

*   **Catalog (商品)**: `domain-catalog`
*   **Checkout (注文/決済)**: `domain-checkout`
*   **Customer (顧客)**: `domain-customer`

必要に応じて、`view_file .agent/skills/domain-*/resources/RULES.md` などを参照し、ビジネスルールに違反しないようにします。

## 3. 設計とアーキテクチャ (Architecture & Design)

仕様に基づき、API設計やDBスキーマ、システム全体の構造を決定します。

1.  **スキル読み込み**: `view_file .agent/skills/tech-api-design/SKILL.md` (存在する場合) または Architect Role.
2.  **役割**: API Designer / Architect
3.  **アクション**:
    *   OpenAPI / REST API 定義
    *   ER図 (Mermaid) の作成
    *   コンポーネント構成の決定

## 4. 実装フェーズ (Implementation Phase)

設計が完了したら、各スペシャリストに実装を指示します。

### Backend Implementation
*   **スキル**: `tech-backend-dev`
*   **読み込み**: `view_file .agent/skills/tech-backend-dev/SKILL.md`
*   **役割**: Backend Architect (Staff Engineer)
*   **アクション**:
    *   Clean Architecture に基づく実装 (Presentation, Service, Data Layer)
    *   Pydantic モデル、SQLAlchemy リポジトリの実装
    *   単体テストの作成

### Frontend Implementation
*   **スキル**: `tech-frontend-dev`
*   **読み込み**: `view_file .agent/skills/tech-frontend-dev/SKILL.md`
*   **役割**: Frontend Expert
*   **アクション**:
    *   Feature-based なコンポーネント実装
    *   TanStack Query, React Hook Form の統合
    *   UI/UX の最適化

### Infrastructure (DevOps)
*   **スキル**: `tech-cloud-infra`
*   **読み込み**: `view_file .agent/skills/tech-cloud-infra/SKILL.md`
*   **役割**: Cloud Ops
*   **アクション**:
    *   Dockerfile, Cloud Run 設定
    *   CI/CD パイプライン
    *   Terraform 構成

## 5. 品質保証と検証 (QA & Verification)

実装完了後、品質を担保します。

1.  **スキル読み込み**: `view_file .agent/skills/tech-qa-automation/SKILL.md`
2.  **役割**: QA Engineer
3.  **アクション**:
    *   E2Eテスト、統合テストの実行
    *   エッジケースの検証
    *   デグレ（Regressions）のチェック

## 6. PMによる最終チェック

全ての工程が完了したら、PMとして全体をレビューします。
`docs/DEVELOPMENT_STANDARDS.md` (または `.agent/rules/product-manager.md`) のルールに準拠しているか最終確認を行い、ユーザーに成果を報告してください。
