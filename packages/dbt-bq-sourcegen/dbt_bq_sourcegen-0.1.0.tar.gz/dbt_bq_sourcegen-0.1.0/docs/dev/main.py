"""
BigQueryのテーブル情報を元にsource.ymlのdescriptionを更新する
TODO:
  - source.ymlが無い場合は別途手かosmosisなどで用意する必要がある
  - その場合は https://github.com/syou6162/dbt-source-importer を使うかこのスクリプトを改修する
  - これ以上増えるなら色々分割する  現状テストもなにもない
"""

import click
import ruamel.yaml
from google.cloud import bigquery
from typing import Dict, Any
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


# ruamel.yamlを使ってyamlファイルを読み込む (jinja文字列も安全にload)
yaml = ruamel.yaml.YAML(typ="rt")
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.preserve_quotes = True  # クォートを保持
yaml.default_flow_style = False  # ブロックスタイルで出力
yaml.allow_unicode = True  # 日本語も文字列として扱う
yaml.sort_keys = False  # ソートしない
yaml.width = 4096  # 折り返しなし


def load_source_yml(source_yml_path: str) -> Dict[str, Any]:
    """source.ymlファイルの読み込み
    TODO: validateいれる
    """

    with open(source_yml_path, "r") as f:
        return yaml.load(f)


def get_table_info(
    client: bigquery.Client, source: Dict[str, Any], table: Dict[str, Any]
) -> bigquery.Table:
    """BigQueryからテーブル情報を取得"""
    dataset_id = source["schema"] if source["schema"] else source["name"]
    table_id = table["identifier"] if table["identifier"] else table["name"]
    table_ref = client.dataset(dataset_id).table(table_id)
    return client.get_table(table_ref)


def update_descriptions(table: Dict[str, Any], bq_table: bigquery.Table) -> None:
    """source_dataのdescriptionを更新
    同名のテーブルとカラムのdescriptionを更新する
    YAMLに定義されているテーブルとカラムのdescriptionを、
    BigQueryのテーブルスキーマ情報で上書き更新します。
    YAMLに存在しないカラムは追加します。
    """
    if table.get("description", "") == "":
        table["description"] = bq_table.description
        logger.info(
            f"Updated description for {table['name']}.description: {bq_table.description}"
        )

    updated_columns = []
    for field in bq_table.schema:
        column_found = False
        if table.get("columns", "") is not None:
            for column in table["columns"]:
                if (
                    column["name"] == field.name
                    and column.get("description", "") == ""
                    and field.description is not None
                ):
                    column["description"] = field.description
                    column_found = True
                    updated_columns.append(column)
                    logger.info(
                        f"Updated description for {column['name']}.description: {field.description}"
                    )
                    break
        if not column_found: # YAMLに存在しないカラムを追加
            new_column = {
                "name": field.name,
                "data_type": field.field_type,
                "description": field.description if field.description is not None else "",
            }
            updated_columns.append(new_column)
            logger.info(f"Added new column {new_column['name']} from BigQuery Schema")

    table['columns'] = updated_columns # 更新されたカラムリストで置き換える


def save_source_yml(source_yml_path: str, source_data: Dict[str, Any]) -> None:
    """更新したsource.ymlを保存"""
    with open(source_yml_path, "w", encoding="utf-8") as f:
        yaml.dump(source_data, f)


@click.command()
@click.option("--project-id", required=True, help="GCPプロジェクトID")
@click.argument("source_yml_path", type=click.Path(exists=True))
def main(project_id: str, source_yml_path: str):
    """source.ymlのdescriptionをBigQueryのテーブル情報から更新"""
    logger.info(f"Starting update process for {source_yml_path}")

    source_data = load_source_yml(source_yml_path)
    client = bigquery.Client(project=project_id)

    for source in source_data["sources"]:
        for table in source["tables"]:
            logger.info(f"Processing table: {table['name']}")
            try:
                bq_table = get_table_info(client, source, table)
                update_descriptions(table, bq_table)
            except Exception as e:
                logger.error(f"Failed to get table info: {e}")
                continue

    save_source_yml(source_yml_path, source_data)
    logger.info(f"Finished update process for {source_yml_path}")


if __name__ == "__main__":
    main()
