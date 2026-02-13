---
description: フロントエンドの標準的なUI上の遷移をテストします。QA担当者として、Webブラウザを実際に操作し、ユーザーの基本的な体験フローに問題がないかを確認・評価します。
---

accept_criteria: |-
  - [ ] トップページから商品詳細ページへの遷移が正常に行えること。
  - [ ] 商品詳細ページに商品の情報（画像、テキストなど）が正しく表示されること。
  - [ ] 商品詳細ページからカテゴリ一覧ページへの遷移が正常に行えること。
  - [ ] カテゴリ一覧ページに商品リストが正しく表示されること。
  - [ ] 上記の全行程で、ブラウザのコンソールに重大なエラー（404, 500, 未定義の変数エラー等）が表示されないこと。
  - [ ] 画像が正しくロードされ、リンク切れ（Broken Image）がないこと。
  - [ ] レイアウトが崩れておらず、レスポンシブデザインが機能していること。

workflow:
  - id: start_dev_server
    description: フロントエンドの開発サーバーを起動します。
    actions:
      - tool: run_shell_command
        args:
          command: "cd frontend && npm run dev"
          description: "フロントエンドの開発サーバーを起動します。バックグラウンドで実行し、通常ポート5173で待機します。"
      - tool: run_shell_command
        args:
          command: "timeout 30s bash -c 'until curl -s http://localhost:5173 > /dev/null; do sleep 1; done'"
          description: "サーバーが応答するまで最大30秒待機します。タイムアウトした場合はエラーとなります。"

  - id: check_top_page
    description: Webブラウザでトップページを開き、表示とエラーがないか確認します。
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
      - "トップページが正しく表示されているか確認してください。"
      - "ヒーローセクションや商品リストが表示されていますか？"
      - "DevToolsのコンソールを確認し、赤字のエラーログ（404 Not Found, Uncaught Exceptions等）が出ていないか厳密にチェックしてください。"

  - id: navigate_to_product_detail
    description: トップページの商品をクリックし、商品詳細ページへ遷移します。
    actions:
      - tool: click
        args:
          uid: "product-card-0" # 注意: 実際のUIDはスナップショットを確認して、最初の商品カード等の適切な要素を指定してください。
      - tool: wait
        args:
          seconds: 2
      - tool: take_snapshot
        args: {}
    eval:
      - "URLが `/products/{id}` のような詳細ページ形式に変化しましたか？"
      - "商品画像は表示されていますか？（壊れた画像アイコンになっていませんか？）"
      - "商品名、価格、説明文は読み取れますか？"
      - "コンソールにエラーは表示されていませんか？"

  - id: navigate_to_category_page
    description: 商品詳細ページから、ヘッダー等のナビゲーションを使ってカテゴリ一覧（例: MEN, WOMEN）へ移動します。
    actions:
      - tool: click
        args:
          uid: "navbar-category-men" # 注意: 実際のUIDはスナップショットを確認して、ヘッダー内の適切なカテゴリリンクを指定してください。
      - tool: wait
        args:
          seconds: 2
      - tool: take_snapshot
        args: {}
    eval:
      - "URLが `/categories/{category}` の形式に変化しましたか？"
      - "選択したカテゴリの商品一覧が表示されていますか？"
      - "商品カードのグリッド表示などは崩れていませんか？"
      - "コンソールエラーはありませんか？"

  - id: qa_final_evaluation
    description: 一連のテスト結果をQA担当者として評価し、レポートします。
    eval:
      - "クリティカルなバグ（画面が真っ白、操作不能、クラッシュ）はありましたか？"
      - "マイナーなバグ（レイアウトのズレ、テキストの誤字、軽微な表示崩れ）はありましたか？"
      - "UI/UXの観点で「使いにくい」「分かりにくい」と感じた点はありましたか？"
    conclusion: "【承認】または【却下】の判定と、その理由を詳細に記述してください。修正が必要な場合は、具体的な修正箇所を指摘してください。"