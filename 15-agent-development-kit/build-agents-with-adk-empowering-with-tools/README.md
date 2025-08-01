# Codelab: ADKによる階層型エージェントの構築

> このリポジトリは、Google Codelab [Build agents with ADK empowering with tools](https://codelabs.developers.google.com/devsite/codelabs/build-agents-with-adk-empowering-with-tools) の実装です。

このプロジェクトでは、GoogleのAgent Development Kit (ADK) を用いて、**階層型エージェント (Hierarchical Agents)** のアーキテクチャを実践的に学びます。

## コンセプト：階層型エージェントとは？

複雑な問題を解決するために、1人の万能なエージェントに全てを任せるのではなく、**司令塔となるエージェント**が、タスクに応じて**専門的なスキルを持つエージェントやツール**を適切に使い分ける設計思想です。

このアーキテクチャには、以下のような利点があります。

- **モジュール性**: 機能ごとにエージェントやツールが独立しているため、追加や修正が容易です。
- **専門性**: 各エージェントは特定のタスクに特化しているため、より高品質な応答が期待できます。
- **拡張性**: 新しいツールやスキルが必要になった場合でも、司令塔エージェントにそのツールを追加するだけで対応できます。

## プロジェクトの全体像

このプロジェクトでは、ユーザーからの様々な質問に答えるAIアシスタントを構築します。
司令塔である `root_agent` がユーザーの質問の意図を読み取り、最適な専門家（ツール/エージェント）にタスクを割り振ります。

```mermaid
graph TD
    A[User] --> B(root_agent: 司令塔);
    B -->|"リアルタイムな質問 (天気, ニュースなど)"| C{google_search_agent: 最新情報担当};
    B -->|"知識ベースの質問 (歴史, 文化など)"| D{langchain_wikipedia_tool: 歴史・文化研究者};
    B -->|"特定の計算 (為替レートなど)"| E[get_fx_rate 関数: 金融アナリスト];
```

## 登場する専門家たち（コンポーネント解説）

### 司令塔: `root_agent` (`personal_assistant/agent.py`)
ユーザーからの全ての指示を受け取るプロジェクトマネージャーです。「ユーザーの質問に日本語で答える」という総合的な目標を持ち、タスクの性質を見極めて、以下の専門家たちに仕事を依頼します。

### 最新情報担当: `google_search_agent` (`custom_agents.py`)
Google検索を専門に行うエージェントです。「今日の天気は？」「〇〇の営業時間は？」といった、常に変化するリアルタイムな情報の取得を得意としています。

### 歴史・文化研究者: `langchain_wikipedia_tool` (`third_party_tools.py`)
LangChainライブラリを経由してWikipediaの膨大な知識にアクセスするツールです。「日本の首都の歴史を教えて」といった、深く、網羅的な知識が求められる質問に答えます。

### 金融アナリスト: `get_fx_rate` 関数 (`custom_functions.py`)
外部APIを叩いて、特定の通貨間の為替レートを計算する専門家です。単純な関数ですが、`FunctionTool` としてエージェントに組み込むことで、強力なツールとして機能します。

## このCodelabから学べること

- ADKを使った基本的なエージェントの作成方法
- 複数のエージェントとツールを連携させる**階層型アーキテクチャ**の設計・実装
- ADK標準ツール (`google_search`) の使い方
- Pythonの**カスタム関数**をツールとしてエージェントに統合する方法
- **サードパーティライブラリ (LangChain)** をツールとして連携させるテクニック

## セットアップと実行方法

### 1. 依存関係のインストール

このプロジェクトでは `uv` を使用してパッケージを管理しています。
リポジトリのルートで以下のコマンドを実行してください。

```bash
# ai-agents-adk ディレクトリに移動
cd ai-agents-adk

# 依存関係をインストール
uv pip install -e .
```

### 2. エージェントの起動

ADKのWebインターフェースを使ってエージェントを起動します。
`ai-agents-adk` ディレクトリ内で、以下のコマンドを実行してください。

```bash
adk web
```

コマンドを実行すると、Webサーバーが起動し、ブラウザで対話画面が開きます。
そこで、`root_agent` を選択し、様々な質問を試してみてください。

**対話の例:**
- 「今日の東京の天気は？」(→ `google_search_agent` が呼ばれる)
- 「ドル円の為替レートを教えて」(→ `get_fx_rate` が呼ばれる)
- 「戦国時代の歴史について教えて」(→ `langchain_wikipedia_tool` が呼ばれる)