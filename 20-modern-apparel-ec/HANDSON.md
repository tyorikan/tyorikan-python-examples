# Antigravity Practice: Building a Developer Portal

このハンズオンでは、「**社内用開発者ポータルサイト (`/portal`) を構築する**」という具体的なミッションを通じて、Antigravity の3大要素（Skills, Rules, Workflows）がどのように連携し、開発を加速させるかを体験します。

---

## 🚀 Mission: 開発者ポータルを構築せよ

あなたのチームは、自社APIのドキュメントやガイドラインを掲載するポータルサイトを React + Tailwind CSS で構築することになりました。

**課題:**
通常の AI に頼むと、以下のような問題が起きがちです。
*   ページごとにデザインがバラバラになる。
*   スマホで見るとレイアウトが崩れている。
*   毎回「青色を使って」「見出しはこうして」と指示するのが面倒。

**解決策 (Antigravity Architecture):**
1.  **Rules**: 「モバイルファースト」などの鉄の掟を記憶させる。
2.  **Skills**: 「ドキュメントUIの専門家」を育て、デザインを統一する。
3.  **Workflows**: 「ページ作成フロー」を定義し、品質を担保する。

---

## Step 1: Rules - 鉄の掟（憲法）を定める

まず、エージェントが絶対に守るべき「憲法」を定義します。
これがなければ、エージェントは毎回ゼロベースで考え、ブレが生じます。

### 🛠 Action: ルールの確認と意識

あなたの `.agent/rules/user_rules.md` (またはメモリ) に、以下のようなルールが存在すると仮定（または追加）してください。

````markdown
# Developer Portal Design Constitution

1. **Mobile First**: 全てのUIはモバイル画面での表示を最優先する。PC表示はあくまで拡張である。
2. **Accessibility**: すべての画像には `alt` 属性を必須とする。
3. **Consistency**: 配色は Tailwind の `slate` をベースとし、ブランドカラーとして `indigo-600` を使用する。
```

> **Point**: このルールがあることで、あなたが「スマホ対応して」と言わなくても、エージェントは自動的に `w-full md:w-auto` のようなレスポンシブなクラスを提案するようになります。

---

## Step 2: Skills - 専門家 (Specialist) を雇う

次に、このプロジェクト専属の「UI職人」を育てます。
汎用的な React の知識に加えて、**「ポータルサイト特有のデザインパターン」** を教え込みます。

### 🛠 Action: `doc-ui-specialist` の作成

1.  `.agent/skills/doc-ui-specialist/` ディレクトリを作成します。
2.  その中に `SKILL.md` を作成します。

```markdown
---
name: doc-ui-specialist
description: Expert in building developer portal UIs using React & Tailwind. Focuses on readability and code presentation.
---

# Documentation UI Specialist Guidelines

あなたは開発者ポータルのUI実装を専門とするエンジニアです。
以下のガイドラインに従ってコンポーネントを設計・実装してください。

## 1. Color Palette
ポータルサイトは「読みやすさ」が命です。
*   **Background**: `bg-slate-50` (Main), `bg-white` (Card)
*   **Text**: `text-slate-900` (Headings), `text-slate-600` (Body)
*   **Accent**: `text-indigo-600` (Links)

## 2. Component Patterns

### Info Alert (情報アラート)
補足情報は以下のスタイルで統一してください。
```tsx
<div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r">
  <p className="font-bold text-blue-700">Note</p>
  <p className="text-sm text-blue-600">{content}</p>
</div>
```

### Code Block (コードブロック)
コードは `bg-slate-900` (`text-white`) で囲み、必ず `rounded-lg` を適用してください。

## 3. Behavior
*   新しいページを作る際は、必ず `<Layout>` コンポーネントでラップすること。
```

> **Point**: これでエージェントは「アラートを表示して」という指示だけで、上記の一貫したデザインコードを出力できるようになります。
````

---

## Step 3: Workflows - 工場ライン (Workflow) を作る

最後に、ページ作成作業を「流れ作業」にします。
思いつきで作るのではなく、**「設計 → UI適用 → 検証」** という正しい手順を強制します。

### 🛠 Action: `create-doc-page` ワークフローの作成

`.agent/workflows/create-doc-page.md` を作成します。

```markdown
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
```

> **Point**: ここが最大の学びです。ワークフローの中で **「どのフェーズでどのスキルを使うか」** を定義しています。これにより、作業の品質が均一化されます。

---

## Step 4: The Integration - 全てを動かす

準備は整いました。**Rules, Skills, Workflows** が全て揃った状態で、エージェントに指示を出してみましょう。

### 🎯 実行シナリオ
あなたは PM として、「API認証 (Authentication) の解説ページ」を作りたいと思っています。

### Golden Prompt

```text
/create-doc-page
「API認証 (Authentication)」についての解説ページを追加してください。
内容は以下の通り：
1. ヘッダーに `Authorization: Bearer <token>` が必要であること。
2. トークンがない場合は 401 エラーが返ること（これはInfo Alertで目立たせたい）。
3. cURL のリクエスト例を載せること。
```

### 🧠 エージェントの脳内で起きること（連携の可視化）

1.  **Workflow Activation**: `/create-doc-page` を検知し、ワークフローモードに入ります。
2.  **Phase 1 (Blueprint)**: 構成案を作成します。
3.  **Phase 2 (Construction)**:
    *   **Skill Loading**: ここで `doc-ui-specialist` を読み込みます。
    *   **Applying Skill**: ユーザーの「Info Alertで目立たせたい」という指示を、スキル内の `<div className="bg-blue-50...">` という具体的なコードパターンに変換します。
    *   **Applying Skill**: cURL コマンドを、スキルで定義された `bg-slate-900` のコードブロックで実装します。
4.  **Phase 3 (Rule Check)**:
    *   **Rule Enforcement**: 実装されたコードを、グローバルルールの「Mobile First」と照らし合わせます。「スマホで見た時に cURL の行がはみ出さないか？」などをチェックし、必要なら `overflow-x-auto` を追加します。

---

## Conclusion: Antigravity の真価

このハンズオンで体験したのは、単なるコード生成ではありません。

*   **Rules** が**品質のベースライン**を引き上げ、
*   **Skills** が**専門的なデザイン**を提供し、
*   **Workflows** が**間違いのないプロセス**を進行させました。

これらを組み合わせることで、あなたは「指示出し」の負担を最小限にしつつ、常に高品質なアウトプットを得ることができるようになります。
