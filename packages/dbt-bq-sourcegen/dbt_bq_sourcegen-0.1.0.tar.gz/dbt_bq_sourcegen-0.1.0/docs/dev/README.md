# bq_source_importer

## 概要

Bigqueryのdescriptionをdbtのsource.ymlにimportする

## Usage

```bash
cd transform
python python_modules/bq_source_importer/main.py  --project-id sukuna-beta-staging models/dl/[your_source_yaml].yml 
```

注意点:
- すでにカラムが存在する前提
- yamlにdescriptionが記載されていたら上書きはしません
- なんかクォーテーションがダブルなったりシングルだったりなかったり安定しない
- data_typeがなぜかtypeになったりする
