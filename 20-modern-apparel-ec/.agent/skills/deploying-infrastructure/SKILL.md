---
name: deploying-infrastructure
description: Terraform による GCP インフラ管理、Cloud Run デプロイ、CI/CD パイプラインを担当する。デプロイ、クラウドリソースの設定、Dockerfile の作成、GitHub Actions のセットアップ時に使用する。
---

# インフラストラクチャ & デプロイ

## GCP スタック

| サービス | 用途 |
|---|---|
| Cloud Run | コンピューティング（オートスケーリング） |
| Cloud Spanner | データベース（リージョナル HA） |
| Memorystore (Redis) | キャッシュ |
| Cloud Storage | アセットストレージ |
| Secret Manager | シークレット管理（環境変数として注入） |

## IaC（Terraform）

- リモートステートは GCS バケットで管理し、ロック機能を有効にする。
- 標準リソースには検証済みモジュールを使用する。
- イミュータブルインフラ: コンテナはペットではなく家畜。

## CI/CD（GitHub Actions）

パイプライン: `Lint → Test → Build (Docker) → Push (Artifact Registry) → Deploy (Cloud Run)`

- PR プレビュー環境: `pr-123.run.app` に自動デプロイ。
- 本番タグ: SHA256 ダイジェストまたはセマンティックバージョン。`:latest` は禁止。

## オブザーバビリティ

- **ログ**: Cloud Logging（構造化 JSON）。
- **メトリクス**: Cloud Monitoring。5xx エラー率 > 1% でアラート。
- **トレーシング**: Cloud Trace。

## アンチパターン

- ❌ コンソールでの手動操作（ClickOps）— すべて Terraform で定義する
- ❌ Git にシークレットをハードコード — Secret Manager を使う
- ❌ 本番環境で `:latest` タグを使う
