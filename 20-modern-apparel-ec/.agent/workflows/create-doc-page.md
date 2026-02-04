---
description: ポータルサイトに新しいドキュメントページを追加するフロー
---

# Create Documentation Page Workflow

新しい解説ページを追加する際は、以下のステップを実行してください。

## Phase 1: Blueprint (構成案)
1.  **構成作成**: ユーザーの要望から、ページの構成案（Main Heading, Sub Sections）を提案する。
2.  **ファイル決定**: ファイルパス（例: `src/pages/docs/xxx.tsx`）を決定する。

## Phase 2: Construction (実装)
// turbo
1.  **スキル召喚**: `doc-ui-specialist` スキルを活用し、UIを実装する。
    *   **重要**: ここで必ず SKILL.md のカラーパレットとコンポーネントパターンを守ること。
2.  **ルーティング**: `App.tsx` またはルーター設定に新しいパスを追加する。

## Phase 3: Mobile Inspection (検証)
1.  **Rule Check**: 作成したコードが「Mobile First」ルール（Step 1で定義）を守れているか自己レビューする。
    *   `flex-col` (mobile) -> `md:flex-row` (desktop) のパターンになっているか？
2.  **報告**: 完了報告をする。