---
description: フロントエンドの標準的なUI上の遷移をテストします。QA担当者として、Webブラウザを実際に操作し、ユーザーの基本的な体験フローに問題がないかを確認・評価します。
---

accept_criteria: |-
  - [ ] トップページから商品詳細ページへの遷移が正常に行えること。
  - [ ] 商品詳細ページに商品の情報（画像、テキストなど）が正しく表示されること。
  - [ ] 商品詳細ページからカテゴリ一覧ページへの遷移が正常に行えること。
  - [ ] カテゴリ一覧ページに商品リストが正しく表示されること。
  - [ ] 上記の全行程で、重大なレイアウト崩れや機能不全が発生しないこと。

workflow:
  - id: start_dev_server
    description: フロントエンドの開発サーバーを起動します。
    actions:
      - tool: run_shell_command
        args:
          command: "cd frontend && npm run dev"
          description: "フロントエンドの開発サーバーを起動します。通常、`http://localhost:5173` でリッスンします。"

  - id: open_browser_and_check_top_page
    description: Webブラウザでトップページを開き、表示を確認します。
    actions:
      - tool: activate_skill
        args:
          name: "chrome-devtools"
      - tool: new_page
        args:
          url: "http://localhost:5173"
      - tool: take_snapshot
        args: {}
    eval:
      - "トップページがエラーなく表示され、ヒーローイメージや商品一覧のセクションが確認できるか？"
      - "コンソールに致命的なエラーが出ていないか？"

  - id: navigate_to_product_detail
    description: トップページの商品をクリックし、商品詳細ページへ遷移します。
    actions:
      - tool: click
        args:
          uid: "product-card-0" # 実際のuidはスナップショットから取得する
      - tool: take_snapshot
        args: {}
    eval:
      - "URLが商品詳細ページのパス（例: `/products/some-product-id`）に変わっているか？"
      - "商品の画像、名前、価格、説明文が正しく表示されているか？"
      - "レイアウトに大きな崩れはないか？"

  - id: navigate_to_category_page
    description: ヘッダーナビゲーションからカテゴリ一覧ページ（例: MEN）へ遷移します。
    actions:
      - tool: click
        args:
          uid: "navbar-men-link" # 実際のuidはスナップショットから取得する
      - tool: take_snapshot
        args: {}
    eval:
      - "URLがカテゴリページのパス（例: `/categories/men`）に変わっているか？"
      - "そのカテゴリに属する商品の一覧が表示されているか？"
      - "各商品のカードに画像、名前、価格が表示されているか？"
      - "レイアウトに大きな崩れはないか？"

  - id: final_evaluation
    description: QA担当者として、ここまでのテスト結果を総合的に評価します。
    eval:
      - "一連の画面遷移はスムーズで、ユーザー体験を損なう問題はなかったか？"
      - "表示されるデータ（商品情報など）は一貫性があり、信頼できるものか？"
      - "軽微な表示の乱れなど、修正を推奨する点はあるか？"
      - "総合的に見て、この基本フローはリリース可能な品質か？"
    conclusion: "QA評価をここに記述します。"