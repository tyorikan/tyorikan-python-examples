---
name: developing-frontend
description: React TypeScript と Tailwind CSS でフロントエンドコンポーネントを構築する。UI、コンポーネント、フック、ページ、開発者ポータルのドキュメントページの作成・修正時に使用する。
---

# フロントエンド開発

## プロジェクト構造

```
frontend/src/
├── features/{domain}/
│   ├── components/   # 機能固有のコンポーネント
│   ├── api/          # API クライアントフック（TanStack Query）
│   └── hooks/        # カスタムフック
├── components/       # 共有 UI コンポーネントのみ
├── pages/            # ルートレベルのコンポーネント
└── App.tsx           # ルーティングを含むルート
```

## コンポーネント設計

- **Presentational**: 純粋関数。Props を受け取り、UI を返す。副作用なし。
- **Container**: 状態管理、データフェッチ、Presentational に Props を渡す。
- **Compound**: 複雑な UI に使用（例: `Select.Root`, `Select.Item`）。

## 状態管理

| 種類 | ツール |
|---|---|
| サーバー状態 | TanStack Query（キャッシュ、SWR） |
| グローバルクライアント状態 | Zustand（慎重に使用） |
| フォーム状態 | React Hook Form + Zod |

## スタイリング（Tailwind CSS）

- ユーティリティファースト: `flex`, `p-4` 等。
- デザイントークン: `text-primary`, `bg-muted`（`tailwind.config.ts` で定義）。
- マルチバリアントコンポーネント: `class-variance-authority (cva)` を使用。
- 新規ページは必ず `<Layout>` コンポーネントでラップする。
- デザインシステムの詳細: [resources/design-system.md](resources/design-system.md) を参照

## パフォーマンス

- 画像を最適化する。ファーストビュー以下は遅延ロードする。
- スケルトン/ローダー用の領域を確保する（CLS を防ぐ）。
- 重いライブラリ（Charts, Maps）は動的インポートする。

## アンチパターン

- ❌ 派生状態の計算に `useEffect` を使う（`useMemo` を使う）
- ❌ 3 階層以上の Prop Drilling（コンポジションまたは Context を使う）
- ❌ インラインスタイル（Tailwind を使う）
- ❌ 非セマンティック HTML（`<button>`, `<nav>`, `<main>` の代わりに `<div>` を使う）
