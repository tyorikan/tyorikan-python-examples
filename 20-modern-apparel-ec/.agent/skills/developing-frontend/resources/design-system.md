# デザインシステム

## タイポグラフィ
- フォント: "Inter", sans-serif。
- サイズ: `text-sm`（本文）、`text-xl`（見出し）。

## カラー（Tailwind）
- プライマリ: `slate-900`
- セカンダリ: `slate-600`
- アクセント: `indigo-600`
- デンジャー: `red-600`
- 背景: `bg-slate-50`（メイン）、`bg-white`（カード）
- テキスト: `text-slate-900`（見出し）、`text-slate-600`（本文）
- リンク: `text-indigo-600`

## コンポーネントパターン

### ボタン
`rounded-md`, `px-4`, `py-2`。`shadcn/ui` スタイルを使用。

### インプット
`border`, `rounded-md`, `focus:ring-2`。

### コードブロック
`bg-slate-900`, `text-white`, `rounded-lg`。

### 情報アラート
```tsx
<div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r">
  <p className="font-bold text-blue-700">Note</p>
  <p className="text-sm text-blue-600">{content}</p>
</div>
```
