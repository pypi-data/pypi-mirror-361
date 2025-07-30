# CI/CD 方針

## 概要

本プロジェクト `dbt-bq-sourcegen` は OSS として GitHub で公開するため、以下の方針で CI/CD パイプラインを整備する。

## 基本方針

- **シンプルかつ効果的**: 過度な自動化は避け、必要十分な品質保証を実現
- **開発者フレンドリー**: ローカル開発環境と CI 環境の一貫性を保つ
- **透明性**: すべての CI プロセスと結果を公開し、コントリビューターが理解しやすくする

## GitHub Actions ワークフロー

### 1. Pull Request チェック (`.github/workflows/ci.yml`)

PR 作成・更新時に実行される品質チェック。

#### 実行タイミング
- Pull Request の作成・更新時
- main ブランチへの push 時

#### ジョブ構成

##### 1.1 Lint & Format Check
```yaml
- Python 3.11, 3.12, 3.13 でのマトリックステスト
- uv を使用した依存関係のインストール
- ruff による lint チェック
- ruff による format チェック
- pyright による型チェック
```

##### 1.2 Test
```yaml
- Python 3.11, 3.12, 3.13 でのマトリックステスト
- pytest によるユニットテスト実行
- pytest-cov によるカバレッジ測定
- カバレッジレポートの生成とアップロード
```

##### 1.3 Build Check
```yaml
- パッケージビルドの確認
- インストール可能性の検証
```

### 2. リリース自動化 (`.github/workflows/release.yml`)

#### 実行タイミング
- `v*` タグのプッシュ時（例: `v0.1.0`）

#### ジョブ構成

##### 2.1 Build & Test
- CI ワークフローと同じテストを実行
- 全テスト合格を確認

##### 2.2 Publish to PyPI
```yaml
- Python パッケージのビルド (wheel, sdist)
- PyPI へのアップロード
- GitHub Release の作成
- リリースノートの自動生成
```

### 3. 定期チェック (`.github/workflows/scheduled.yml`)

#### 実行タイミング
- 毎週月曜日 UTC 00:00

#### 目的
- 依存関係の脆弱性チェック
- 最新の Python バージョンでの動作確認

## ブランチ保護ルール

### main ブランチ
- 直接 push を禁止
- PR 経由でのみマージ可能
- 以下のステータスチェックが必須:
  - Lint & Format Check (全 Python バージョン)
  - Test (全 Python バージョン)
  - Build Check
- 最新の状態でのマージを要求
- 管理者も例外なし

## セキュリティ

### シークレット管理
- `PYPI_API_TOKEN`: PyPI への公開用トークン（リポジトリシークレット）
- Dependabot によるセキュリティアップデートの自動作成

### 権限管理
- ワークフローは最小権限の原則に従う
- PyPI トークンはリリースワークフローのみアクセス可能

## ローカル開発との整合性

CI で実行されるコマンドはすべてローカルでも実行可能：

```bash
# 型チェック
uv run pyright src

# Lint
uv run ruff check src/

# Format
uv run ruff format src/ --check

# テスト
uv run pytest -v

# カバレッジ付きテスト
uv run pytest --cov=dbt_bq_sourcegen --cov-report=term-missing
```

## リリースプロセス

1. 機能開発は feature ブランチで実施
2. main ブランチへの PR を作成
3. CI チェックをすべてパス
4. コードレビュー後マージ
5. リリース時は以下を実行:
   ```bash
   # バージョンを更新 (pyproject.toml と __init__.py)
   # 変更をコミット
   git commit -m "Release v0.1.0"
   
   # タグを作成
   git tag v0.1.0
   git push origin main
   git push origin v0.1.0
   ```
6. GitHub Actions が自動的に PyPI へ公開

## 将来的な拡張

以下は必要に応じて追加を検討：

- **ドキュメント自動生成**: Sphinx/MkDocs によるドキュメントサイト
- **パフォーマンステスト**: 大規模スキーマでの動作確認
- **統合テスト**: 実際の BigQuery 環境でのテスト（要認証情報）
- **コードカバレッジ目標**: 80% 以上のカバレッジ維持
- **バッジ表示**: README への CI ステータス、カバレッジバッジ追加

## 実装チェックリスト

CI/CD 実装時の確認事項：

- [ ] `.github/workflows/ci.yml` の作成
- [ ] `.github/workflows/release.yml` の作成  
- [ ] `.github/workflows/scheduled.yml` の作成
- [ ] PyPI アカウントの作成と API トークンの取得
- [ ] GitHub リポジトリへのシークレット設定
- [ ] main ブランチの保護ルール設定
- [ ] Dependabot の有効化
- [ ] 初回リリースのテスト（v0.1.0）