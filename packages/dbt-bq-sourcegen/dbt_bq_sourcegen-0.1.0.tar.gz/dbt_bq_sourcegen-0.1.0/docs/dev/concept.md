# コンセプト

## 機能

コマンド一発で以下が可能

- dbtのsource.ymlがなければ自動作成
- すでにある場合はテーブルやカラムの情報をリモート(bigquery)に合わせる

### イメージ

```bash
dbt-bq-sourcegen apply \
  --project-id your-project \
  --schema your_schema \
  --output  src_your_schema.yml
```

引数:

- project-id
  - 必須
  - str
  - Google cloudのprojectを指定
- schema
  - 必須
  - str
  - BigQueryのschemaを指定
- output
  - 必須
  - file(yaml)
  - 出力するdbt source形式のyamlファイル
- table_pattern
  - Optional
  - wildcard
  - テーブルを絞りたいときに指定する (e.g. `stg_*`)
- exclude
  - Optional
  - str
  - 除外したいテーブルの文字列

## 現状の課題

現在のmain.pyスクリプトの制限事項:
- source.ymlファイルが事前に存在している必要がある
- descriptionの更新のみで、テーブル構造の完全な同期ができない
- パッケージ化されていないため配布・インストールが困難
- テストがない

## 詳細仕様

### 主要機能

1. **source.yml自動生成機能**
   - BigQueryのデータセット情報から新規source.ymlを作成
   - 既存ファイルがない場合は自動で生成
   - 生成時にテーブル・カラムの完全な情報を取得

2. **既存source.yml更新機能**
   - テーブル追加: BigQueryに存在するが、YAMLに定義されていないテーブルを追加
   - テーブル削除: オプションでBigQueryに存在しないテーブルを削除（デフォルトは保持）
   - カラム同期: 
     - 新規カラムの追加
     - カラムのdata_type更新
     - description更新（空の場合のみ）
     - 削除されたカラムの処理（オプション）

3. **メタデータ取得**
   - テーブル名、説明
   - カラム名、データ型、説明
   - パーティション情報（将来的に）
   - クラスタリング情報（将来的に）

### CLI仕様

```bash
# apply
dbt-bq-sourcegen apply \
  --project-id your-project \
  --dataset your_dataset \
  --output models/staging/your_dataset/src_your_dataset.yml
```

### パッケージ構成

```
dbt-bq-sourcegen/
├── src/
│   └── dbt_bq_sourcegen/
│       ├── __init__.py
│       ├── cli.py                # CLIエントリーポイント
│       ├── typeos/                # 共通型構造
│       ├── logic/                # 純粋関数・ビジネスロジック層
│       │   ├── __init__.py
│       │   ├── schema_diff.py    # スキーマ差分計算
│       │   ├── source_builder.py # source構造生成
│       │   ├── merge_strategy.py # 更新戦略の定義
│       └── io/                   # 外部システムとの入出力層
│           ├── __init__.py
│           ├── bigquery.py       # BigQueryクライアント
│           ├── yaml_handler.py   # YAMLファイル読み書き
│           └── file_system.py    # ファイルシステム操作
├── tests/
│   ├── logic/
│   │   ├── test_schema_diff.py
│   │   ├── test_source_builder.py
│   │   └── test_merge_strategy.py
│   └── io/
│       ├── test_bigquery.py
│       └── test_yaml_handler.py
├── pyproject.toml
└── README.md
```

### 技術仕様

- **YAML処理**: ruamel.yaml（Jinja2記法を保持、フォーマット維持）
- **BigQuery接続**: google-cloud-bigquery
- **CLI**: Click
- **ログ**: loguru
- **データモデル**: Pydantic（バリデーション、型安全性）
- **エラーハンドリング**:
  - テーブルが見つからない場合はスキップしてログ出力
  - 接続エラー時は適切なメッセージ表示

### 出力フォーマット

```yaml
version: 2

sources:
  - name: your_dataset
    schema: your_dataset
    tables:
      - name: table1
        description: "テーブルの説明"
        columns:
          - name: id
            data_type: INT64
            description: "主キー"
          - name: created_at
            data_type: TIMESTAMP
            description: "作成日時"
```

出現する可能性のあるキーは
https://docs.getdbt.com/reference/source-properties
を参照

気になるところ

- updateする際は主要キー以外は消したり変更しない
  - 主要キー: columnの場合はname, data_type, description, tableの場合はname, description
- descriptionが空の場合はキーを省略せず、`description: ""`とする
- descriptionがある場合は文字数にかかわらず `|`のblock notationを用いる
  ```
  description: |
    foo
  ```
- table のdescriptionも取得する
  - ない場合はカラムと同様に省略せず空文字とする
- version:2 の下は1行空行があるとよい

### yaml周りのテスト項目

- ファイル存在する場合の更新
  - 既存のキーを削除していないか
  - 更新すべき場所だけを更新できているか
    - ローカルにいないテーブルやカラムがあったら追加
    - リモートに存在しないカラムは削除
    - リモートに存在しないテーブルはそのまま

## 開発

### Git/ブランチ関連

GitHub Flow

### バージョン管理

hatch

### package/project 管理

uv

### 実装スタイル

関数型とOOPのハイブリッド

#### logic層（純粋関数）

- 副作用を持たない純粋関数で実装
- 入力に対して常に同じ出力を返す
- 外部依存なし（BigQuery、ファイルシステムに依存しない）
- immutableなデータ構造を使用
- 型ヒントを徹底

例：

```python
# logic/schema_diff.py
from typing import List, Set, Tuple
from pydantic import BaseModel

class ColumnDiff(BaseModel):
    added: Set[str]
    removed: Set[str]
    modified: Set[str]
    
    class Config:
        frozen = True  # immutableにする

def calculate_column_diff(
    bq_columns: List[Column], 
    yaml_columns: List[Column]
) -> ColumnDiff:
    """BigQueryとYAMLのカラム差分を計算（純粋関数）"""
    # 副作用なし、同じ入力なら同じ出力
```

#### io層（副作用を扱う）

- クラスベースで実装
- 外部システムとの通信を担当
- エラーハンドリングを含む
- 依存性注入でテスト可能に

例：

```python
# io/bigquery.py
class BigQueryClient:
    def __init__(self, project_id: str):
        self.client = bigquery.Client(project=project_id)
    
    def get_dataset_schema(self, dataset_id: str) -> DatasetSchema:
        """BigQueryからスキーマ情報を取得"""
        # 外部システムとの通信
```

#### cli層（エントリーポイント）

- io層とlogic層を組み合わせて実行フローを構築
- ユーザー入力の処理
- エラーメッセージの表示

### 型チェッカー

pyright

### logging

- loguruを使う
- 標準出力に出力する
- 重要な出力は人間が見やすいようにデコレーションする
