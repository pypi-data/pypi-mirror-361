## Code Style

- 静的な構造体の定義はdataclassよりもpydanticを使用すること

## python implement

### uvコマンドを基本とすること

```bash
# package実行
uv run some-pkg

# script
uv run python src/foo.py

# test
uv run pytest -v
```

### 実装後はpyrightによる型チェックとruffによるcheckとformatを行うこと

```bash
# check types
uv run pyright src

# lint
uv run ruff check src/

# format
uv run ruff check src/ --select I --fix
uv run ruff format src/
```

## about project

`docs/dev/concept.md`を参照すること
