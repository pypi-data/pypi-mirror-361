# ml_dataset_contract_core

Пакет ml_dataset_contract_core предназначен для создания собственных
легковесных контрактов данных, которые позволяют
синхронизировать описание входных признаков и целей между
разработкой, обучением и эксплуатацией модели.

Представляет следующие динамические классы:
- `FeatureRow` входные признаки;
- `TargetRow` целевые признаки;
- `PredictRequest` структура запроса к REST API сервера (например, Mlflow)
                   для инференса модели;
- '<TableName>Raw' таблицы с первичными данными;
- `RawPredictRequest` запрос к REST API для случая сырых данных.


## Установка

```shell
pip install ml_dataset_contract_core
```

## Создание и использование собственного контракта

### Создание собственного контракта

Например, ml_dataset_contract_tte

```
└── ml_dataset_contract_tte
    └── src
        ├── ml_dataset_contract_tte
                  ├── dataset.yml
                  ├── __init__.py
```

В файле `dataset.yml` определяем контракт данных
(входные и целевые признаки), например:
```yaml
inputs:
  expanding_tte_mean: float
  tte_lag_1: float

targets:
  tte: float
```

В `__init__.py` динамически создаем классы:
```python
from importlib.resources import files

from ml_dataset_contract.runtime import (
    PydanticFeatureFactory,
    PydanticTargetFactory,
    PydanticRequestFactory,
)

_YAML = files(__name__).joinpath("dataset.yml")

TteFeatureRow = PydanticFeatureFactory(_YAML, prefix="Tte").build()
TteTargetRow  = PydanticTargetFactory(_YAML, prefix="Tte").build()
TtePredictRequest = PydanticRequestFactory(
    _YAML, prefix="Tte", feature_cls=TteFeatureRow
).build()

__all__ = [
    "TteFeatureRow", "TteTargetRow", "TtePredictRequest", "_YAML"
]
```



### Использование собственного контракта

```python
from ml_dataset_contract_tte import (
    TteFeatureRow,
    TteTargetRow,
    TtePredictRequest,
)


sample_row__input = {
    "expanding_tte_mean": 1.1,
    "tte_lag_1": 1.2,
}
sample_row__target = {"tte": 1.3}

feature_row = TteFeatureRow(**sample_row__input)
print(f"{feature_row=}")

target_row = TteTargetRow(**sample_row__target)
print(f"{target_row=}")

request = TtePredictRequest(rows=[feature_row])
payload = request.to_split_json()
print(f"{payload}")
```
