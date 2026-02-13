---
description: カート機能のQAテストを実施します。商品ページから商品をカートに追加し、カートページで表示・数量変更・削除が正常に行えるかを確認します。QA担当者としてWebブラウザを実際に操作して一連のフローをテストします。
---

accept_criteria: |-
  - [ ] 商品詳細ページからカラーとサイズを選択し、「カートに追加」ボタンをクリックして商品が追加されること。
  - [ ] カートページに遷移し、追加した商品が正しく表示されていること（商品名、画像、選択カラー・サイズ、価格）。
  - [ ] カートページ内で商品の数量変更（+ / -）が行え、合計金額が正しく再計算されること。
  - [ ] カートページ内の削除ボタン（ゴミ箱アイコンなど）で商品をカートから削除できること。
  - [ ] カートが空になった場合に、空である旨のメッセージが表示されること。
  - [ ] 一連の操作中にコンソールエラーが発生しないこと。

workflow:
  - id: start_dev_servers
    description: フロントエンドとバックエンドのサーバーを起動します。
    actions:
      - tool: run_shell_command
        args:
          command: "make backend > /dev/null 2>&1 & cd frontend && npm run dev"
          description: "バックエンド（ポート8000）とフロントエンド（ポート5173）を起動します。"
      - tool: run_shell_command
        args:
          command: "timeout 30s bash -c 'until curl -s http://localhost:5173 > /dev/null; do sleep 1; done'"
          description: "フロントエンドサーバーが応答するまで待機します。"

  - id: check_top_page
    description: Webブラウザでトップページを開きます。
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

  - id: add_to_cart_from_product_page
    description: トップページの商品をクリックして詳細画面に遷移し、商品をカートに追加します。
    actions:
      - tool: click
        args:
          uid: "product-card-0" # 実際のスナップショットから適切な商品を選択
      - tool: wait
        args:
          seconds: 2
      - tool: click
        args:
          uid: "color-selector" # 適切なカラーを選択
      - tool: click
        args:
          uid: "size-selector" # 適切なサイズを選択
      - tool: click
        args:
          uid: "add-to-cart-button" # 「カートに追加」ボタン（またはそのアイコンのボタン）をクリック
      - tool: wait
        args:
          seconds: 2
      - tool: take_snapshot
        args: {}
    eval:
      - "商品詳細ページでカラー・サイズを選択しカートに追加した際、ボタンが成功の表示に変わったか確認してください。"
      - "コンソールエラーは発生していませんか？"

  - id: navigate_to_cart_and_verify
    description: カートページに遷移し、追加した商品が正しく表示されているか確認します。
    actions:
      - tool: new_page 
        args:
          url: "http://localhost:5173/cart"
      - tool: wait
        args:
          seconds: 2
      - tool: take_snapshot
        args: {}
    eval:
      - "追加した商品（商品名、画像、選択したカラー・サイズ、価格）が正しく表示されていますか？"
      - "合計金額は正しく計算されていますか？"

  - id: update_cart_quantity
    description: カート内の商品の数量を変更し、金額が再計算されることを確認します。
    actions:
      - tool: click
        args:
          uid: "quantity-plus-button" # 数量増加ボタン(+)をクリック
      - tool: wait
        args:
          seconds: 2
      - tool: take_snapshot
        args: {}
    eval:
      - "数量が増加し、それに応じて商品小計・合計金額が正しく更新されていますか？"

  - id: remove_item_from_cart
    description: カートから商品を削除し、空になることを確認します。
    actions:
      - tool: click
        args:
          uid: "delete-item-button" # ゴミ箱アイコンをクリック
      - tool: wait
        args:
          seconds: 2
      - tool: take_snapshot
        args: {}
    eval:
      - "商品がカートから削除され、「Your cart is empty」などのメッセージが表示されていますか？"
      - "小計や合計金額が0円または非表示になっていますか？"

  - id: qa_final_evaluation
    description: 一連のテスト結果をQA担当者として評価し、レポートします。
    eval:
      - "カートへの追加、表示、数量変更、削除の全機能が問題なく動作しましたか？"
      - "クリティカルなバグやUIの不具合（金額がNaNになる、アイテムが追加されないなど）はありましたか？"
    conclusion: "【承認】または【却下】の判定と、その理由を詳細に記述してください。修正が必要な場合は、具体的な修正箇所を指摘してください。"
