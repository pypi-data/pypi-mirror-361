# ptools-base

P Test Platform Tools Base Lib

## How to install

pip install -U ptools-base

## How to write assert

```python
from ptools_base.tool import write_asserts
from ptools_base.schema import AssertSchema, AssertSchemaResultEnum

write_asserts(
    [
        AssertSchema(
            result=AssertSchemaResultEnum.SUCCESS,
            content="your assert content"
        ),
        AssertSchema(
            result=AssertSchemaResultEnum.FAILED,
            content="your assert content"
        ),
        AssertSchema(
            result=AssertSchemaResultEnum.SKIPPED,
            content="your assert content"
        )
    ]
)
```

## How to copy extra data

```python
from ptools_base.tool import copy_2_extra

# copy file to extra
file_path = "your file path"
copy_2_extra(file_path)

# copy dir to extra
dir_path = "your dir path"
copy_2_extra(dir_path)

```

## How to write env

```python
from ptools_base.schema import EnvSchema
from ptools_base.tool import write_envs

write_envs([EnvSchema(key="your env key", value="your env value")])

```
