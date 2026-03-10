# Modern Apparel EC（Spanner + FastAPI + React）

アパレル EC サイトのサンプルアプリケーションです。  
**AI エージェント（Antigravity）によるアプリケーション開発のデモ**として、Skills・Rules・Workflows を活用した開発プロセスを体験できます。

---

## 技術スタック

| レイヤー | 技術 |
|---|---|
| **フロントエンド** | React 19, Vite, TypeScript, Tailwind CSS v3, TanStack Query, React Router, Lucide Icons |
| **バックエンド** | FastAPI (Python), Pydantic v2, uvicorn |
| **データベース** | Google Cloud Spanner（ローカル開発はエミュレータ） |
| **コンテナ** | Podman / Podman Compose（Docker 互換） |

---

## ディレクトリ構成

```
20-modern-apparel-ec/
├── .agent/                  # Antigravity 設定
│   ├── rules/               # エージェントのルール
│   │   ├── product-manager.md   # DB・Git・設計のプロジェクトルール
│   │   └── user_rules.md        # UI デザイン憲法（Mobile First 等）
│   ├── skills/              # エージェントの専門スキル（6種）
│   │   ├── analyzing-requirements/
│   │   ├── deploying-infrastructure/
│   │   ├── designing-api/
│   │   ├── developing-backend/
│   │   ├── developing-frontend/
│   │   └── testing-code/
│   └── workflows/           # 自動化ワークフロー（3種）
│       ├── cart-qa-basic.md     # カート機能の QA テスト
│       ├── create-doc-page.md   # ドキュメントページ作成
│       └── front-qa-basic.md    # フロントエンド基本 QA
├── backend/
│   ├── app/
│   │   ├── api/             # API エンドポイント（products, cart）
│   │   ├── db/              # Spanner 接続 & リポジトリ
│   │   ├── models/domain/   # ドメインモデル（product, cart, order, user）
│   │   ├── schemas/         # Pydantic スキーマ（product, cart）
│   │   ├── services/        # ビジネスロジック（product, cart）
│   │   └── main.py          # FastAPI アプリケーション
│   ├── scripts/             # DB セットアップスクリプト
│   │   ├── setup_db.sh      # DDL 適用 + シードデータ投入
│   │   ├── migrate.py       # DDL マイグレーション
│   │   ├── seed.py          # マスターデータ投入
│   │   └── master_data.json # 商品マスターデータ
│   ├── tests/               # テスト
│   ├── ddl.sql              # Spanner DDL（6テーブル）
│   └── requirements.txt     # Python 依存関係
├── frontend/
│   └── src/
│       ├── components/      # 共通コンポーネント（Layout, Header, Footer, Navbar, ProductCard）
│       ├── features/        # 機能別モジュール（home, catalog, products, cart）
│       ├── pages/           # ページコンポーネント（Home, Category, Product, docs/Authentication）
│       ├── App.tsx           # ルーティング定義
│       └── main.tsx          # エントリーポイント
├── docker-compose.yaml      # Spanner エミュレータ
├── Makefile                 # 開発タスクランナー
├── HANDSON.md               # ハンズオン資料
└── README.md                # このファイル
```

---

## ローカル開発

### 前提条件

- **Podman（または Docker）** — Spanner エミュレータ用
- **Python 3.10+** — バックエンド
- **Node.js 18+** — フロントエンド

### セットアップ & 起動

#### 1. Spanner エミュレータの起動

```bash
make spanner-up
```

> **Note**: 内部的に `podman-compose up -d` を実行します。Docker を使用している場合は `docker-compose up -d` に読み替えてください。

#### 2. データベースの初期化（初回のみ）

```bash
# バックエンド依存パッケージのインストール
pip install -r backend/requirements.txt

# DDL 適用 + シードデータ投入
make spanner-init
```

このコマンドは以下を実行します:
- `backend/scripts/migrate.py` — DDL（6テーブル: Users, Products, ProductVariants, Orders, OrderItems, CartItems）を適用
- `backend/scripts/seed.py` — `master_data.json` から商品データを投入

#### 3. バックエンドの起動

```bash
make backend
```

手動で起動する場合:
```bash
export SPANNER_EMULATOR_HOST=localhost:9010
export GOOGLE_CLOUD_PROJECT=test-project
export SPANNER_INSTANCE=test-instance
export SPANNER_DATABASE=test-database
cd backend && uvicorn app.main:app --reload
```

- API ドキュメント: http://localhost:8000/docs
- ヘルスチェック: http://localhost:8000/health

**主な API エンドポイント:**
| メソッド | パス | 説明 |
|---|---|---|
| GET | `/api/products` | 商品一覧取得 |
| GET | `/api/products/{id}` | 商品詳細取得 |
| POST | `/api/cart` | カートに追加 |
| GET | `/api/cart/{userId}` | カート内容取得 |

#### 4. フロントエンドの起動

```bash
# 初回のみ
cd frontend && npm install

# 起動
make frontend
```

- アプリケーション: http://localhost:5173

**主なページ:**
| パス | 説明 |
|---|---|
| `/` | トップページ（ヒーロー + 商品一覧） |
| `/category/:categoryId` | カテゴリ別商品一覧 |
| `/new` | 新着商品一覧 |
| `/products/:productId` | 商品詳細（カラー・サイズ選択、カート追加） |
| `/cart` | カートページ（数量変更・削除） |
| `/docs/authentication` | API 認証ドキュメント |

---

## テスト

```bash
# バックエンドのユニットテスト
PYTHONPATH=backend pytest backend/tests/test_products.py
```

---

## データベーススキーマ

Spanner DDL で以下の 6 テーブルを定義しています:

```
Users ──< CartItems（Interleaved）
Products ──< ProductVariants（Interleaved）
Orders ──< OrderItems（Interleaved）
```

- 主キーは UUIDv4（String 型）を使用（ホットスポット回避）
- 親子関係には Interleaving を使用してパフォーマンスを最適化
- 詳細は `backend/ddl.sql` を参照

---

## Antigravity（AI エージェント）について

このプロジェクトには `.agent/` ディレクトリに AI エージェントの設定が含まれています。詳細は [HANDSON.md](./HANDSON.md) を参照してください。
