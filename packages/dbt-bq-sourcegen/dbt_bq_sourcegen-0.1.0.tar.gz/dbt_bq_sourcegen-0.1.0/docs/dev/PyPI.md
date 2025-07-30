# PyPI公開方針と手順

## 概要

`dbt-bq-sourcegen`をPython Package Index (PyPI)に公開するための方針と手順を記載する。本プロジェクトはOSSとして公開され、`pip`または`uv`でインストール可能なパッケージとして配布する。

## 公開方針

### 基本方針

- **シンプルで使いやすい**: インストールから使用まで簡単に行える
- **標準的な構成**: Python パッケージングの標準的なプラクティスに従う
- **自動化**: リリースプロセスを可能な限り自動化し、人為的ミスを防ぐ
- **透明性**: バージョン管理とリリースノートを明確にする

### パッケージ名

- PyPI登録名: `dbt-bq-sourcegen`
- インストールコマンド: `pip install dbt-bq-sourcegen` または `uv add dbt-bq-sourcegen`

### バージョニング

[Semantic Versioning](https://semver.org/) に従う:
- MAJOR.MINOR.PATCH (例: 1.0.0)
- MAJOR: 後方互換性のない変更
- MINOR: 後方互換性のある機能追加
- PATCH: 後方互換性のあるバグ修正

## 事前準備

### 1. PyPIアカウントの作成

初めてPyPIを利用する場合:

1. [PyPI](https://pypi.org/) にアクセスし、アカウントを作成
2. メールアドレスの確認を完了
3. 2要素認証（2FA）を有効化（推奨）

### 2. APIトークンの生成

1. PyPIにログイン後、アカウント設定へ移動
2. "API tokens" セクションへ
3. "Add API token" をクリック
4. トークン名を設定（例: `dbt-bq-sourcegen-github-actions`）
5. スコープは "Entire account" または特定のプロジェクトを選択
6. 生成されたトークンを安全に保存

### 3. TestPyPIでのテスト（推奨）

本番環境へ公開する前にTestPyPIでテスト:

1. [TestPyPI](https://test.pypi.org/) にアカウント作成
2. 同様にAPIトークンを生成
3. テストパッケージをアップロード

## パッケージ構成

### 必要なファイル

```
dbt-bq-sourcegen/
├── src/
│   └── dbt_bq_sourcegen/
│       ├── __init__.py          # バージョン定義を含む
│       ├── cli.py
│       └── ...
├── tests/
├── pyproject.toml               # パッケージメタデータ
├── README.md                    # プロジェクト説明
├── LICENSE                      # ライセンスファイル
└── .gitignore
```

### pyproject.tomlの設定

現在の設定で以下の点を確認:

```toml
[project]
name = "dbt-bq-sourcegen"
dynamic = ["version"]
description = "Create or update dbt source YAML from BigQuery"
readme = "README.md"
authors = [{ name = "K-Oxon", email = "ko1011qfp@gmail.com" }]
requires-python = ">=3.11"
license = { text = "MIT" }  # ライセンスを追加
keywords = ["dbt", "bigquery", "yaml", "source"]  # 検索用キーワード
classifiers = [  # PyPIでの分類
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Build Tools",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]

[project.urls]
Homepage = "https://github.com/K-Oxon/dbt-bq-sourcegen"
Repository = "https://github.com/K-Oxon/dbt-bq-sourcegen"
Issues = "https://github.com/K-Oxon/dbt-bq-sourcegen/issues"
```

### バージョン管理

`src/dbt_bq_sourcegen/__init__.py` でバージョンを定義:

```python
__version__ = "0.1.0"
```

## ローカルでのビルドとテスト

### 1. ビルド

```bash
# パッケージのビルド
uv build

# 生成されるファイル:
# dist/
#   ├── dbt_bq_sourcegen-0.1.0-py3-none-any.whl
#   └── dbt_bq_sourcegen-0.1.0.tar.gz
```

### 2. ローカルインストールテスト

```bash
# 仮想環境を作成
uv venv test-env
source test-env/bin/activate  # Windowsの場合: test-env\Scripts\activate

# ビルドしたパッケージをインストール
uv pip install dist/dbt_bq_sourcegen-0.1.0-py3-none-any.whl

# 動作確認
dbt-bq-sourcegen --help
```

### 3. TestPyPIへのアップロード（初回推奨）

```bash
# twineのインストール（アップロード用ツール）
uv pip install twine

# TestPyPIへアップロード
twine upload --repository testpypi dist/*

# TestPyPIからインストールしてテスト
uv pip install --index-url https://test.pypi.org/simple/ dbt-bq-sourcegen
```

## 手動でのPyPI公開手順

### 1. クリーンビルド

```bash
# 既存のビルドを削除
rm -rf dist/

# 新規ビルド
uv build
```

### 2. PyPIへのアップロード

```bash
# 本番PyPIへアップロード
twine upload dist/*

# 認証情報を求められたら:
# Username: __token__
# Password: <生成したAPIトークン>
```

### 3. 確認

```bash
# PyPIからインストール可能か確認
uv pip install dbt-bq-sourcegen

# バージョン確認
dbt-bq-sourcegen --version
```

## GitHub ActionsによるPyPI公開自動化

### ワークフロー仕様 (`.github/workflows/release.yml`)

```yaml
name: Release to PyPI

on:
  push:
    tags:
      - "v*"  # v0.1.0のようなタグでトリガー

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v3
        
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          
      - name: Install dependencies
        run: |
          uv sync --all-extras
          
      - name: Run tests
        run: |
          uv run pytest -v
          
  build-and-publish:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v3
        
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          
      - name: Build package
        run: |
          uv build
          
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
          
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### GitHubシークレットの設定

1. GitHubリポジトリの Settings → Secrets and variables → Actions
2. "New repository secret" をクリック
3. Name: `PYPI_API_TOKEN`
4. Secret: PyPIで生成したAPIトークンを貼り付け
5. "Add secret" で保存

## リリース手順（GitHub Actions使用）

### 1. バージョン更新

```bash
# __init__.pyのバージョンを更新
# 例: __version__ = "0.1.0" → __version__ = "0.2.0"
```

### 2. 変更をコミット

```bash
git add src/dbt_bq_sourcegen/__init__.py
git commit -m "Bump version to 0.2.0"
git push origin main
```

### 3. タグ作成とプッシュ

```bash
# タグを作成
git tag v0.2.0

# タグをプッシュ（これがGitHub Actionsをトリガー）
git push origin v0.2.0
```

### 4. 自動リリースの確認

1. GitHubのActionsタブでワークフローの実行状況を確認
2. 成功したらPyPIでパッケージが公開されていることを確認
3. GitHub Releasesページでリリースノートを確認

## トラブルシューティング

### よくある問題

1. **パッケージ名の重複**
   - 別の名前を選択するか、既存パッケージのメンテナーに連絡

2. **認証エラー**
   - APIトークンが正しくコピーされているか確認
   - トークンの有効期限を確認

3. **ビルドエラー**
   - `pyproject.toml`の構文エラーをチェック
   - 必要なファイルがすべて含まれているか確認

4. **GitHub Actionsの失敗**
   - シークレットが正しく設定されているか確認
   - ワークフローファイルの構文をチェック

### デバッグ方法

```bash
# パッケージの内容を確認
tar -tzf dist/dbt_bq_sourcegen-*.tar.gz

# wheel ファイルの内容を確認
unzip -l dist/dbt_bq_sourcegen-*.whl

# メタデータの確認
twine check dist/*
```

## ベストプラクティス

1. **リリース前チェックリスト**
   - [ ] すべてのテストがパス
   - [ ] ドキュメントが最新
   - [ ] CHANGELOG.mdを更新
   - [ ] バージョン番号を更新

2. **セキュリティ**
   - APIトークンは絶対にコードにハードコードしない
   - `.gitignore`に`dist/`と`*.egg-info/`を含める

3. **ユーザビリティ**
   - READMEにインストール方法を明記
   - 依存関係を最小限に保つ
   - Python要件を明確にする

## 次のステップ

1. LICENSEファイルの作成（MITライセンスを推奨）
2. CHANGELOG.mdの作成
3. 詳細なREADME.mdの作成
4. 初回リリース（v0.1.0）のテスト
5. PyPIプロジェクトページのカスタマイズ