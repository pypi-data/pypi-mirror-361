"""ml_dataset_contract_tte package
* ``TteFeatureRow``          – инженерные признаки
* ``TteTargetRow``           – целевые метки
* ``TtePredictRequest``      – REST DTO для случая инженерных признаков
* ``TteRawPredictRequest``   – REST DTO для случая первичных признаков
* ``SessionsRow``            – строки таблицы *sessions*
* ``PurchasesRow``           – строки таблицы *purchases*
* ``_YAML``                  – pathlib.Path к исходному YAML‑файлу
"""

from importlib.resources import files
from typing import Dict, List

from ml_dataset_contract.runtime import (
    PydanticFeatureFactory,
    PydanticTargetFactory,
    PydanticRequestFactory,
    PydanticRawFactory,
    PydanticRawRequestFactory,
)

# ---------------------------------------------------------------------------
#  dataset.yml (расположен рядом с этим __init__.py)
# ---------------------------------------------------------------------------
_YAML = files(__name__).joinpath("dataset.yml")

# ---------------------------------------------------------------------------
#  Инженерные признаки / таргеты
# ---------------------------------------------------------------------------
TteFeatureRow = PydanticFeatureFactory(_YAML, prefix="Tte").build()
TteTargetRow = PydanticTargetFactory(_YAML, prefix="Tte").build()

TtePredictRequest = PydanticRequestFactory(
    _YAML, prefix="Tte", feature_cls=TteFeatureRow
).build()

# ---------------------------------------------------------------------------
#  Сырые таблицы (bronze‑layer) – по одному классу на таблицу
# ---------------------------------------------------------------------------
_RAW_MODELS: Dict[str, type] = PydanticRawFactory(_YAML, prefix="Tte").build()

# публикуем каждую модель как ``SessionsRow``, ``PurchasesRow`` и т.д.
globals().update(_RAW_MODELS)

# ---------------------------------------------------------------------------
#  REST‑DTO для случая «клиент шлёт сырые таблицы»
# ---------------------------------------------------------------------------
if _RAW_MODELS:
    TteRawPredictRequest = PydanticRawRequestFactory(
        _YAML, prefix="Tte", raw_cls_map=_RAW_MODELS
    ).build()
else:  # YAML не содержит ``raw_tables`` – сохраняем совместимость
    TteRawPredictRequest = None  # type: ignore

# ---------------------------------------------------------------------------
#  Экспортируемые символы – IDE / linters увидят, что доступно из пакета
# ---------------------------------------------------------------------------
__all__: List[str] = [
    "TteFeatureRow",
    "TteTargetRow",
    "TtePredictRequest",
    "_YAML",
]

# добавляем динамические классы сырых таблиц двумя способами:
#   1) имя таблицы в нижнем регистре  → ``sessions`` / ``purchases``
#   2) привычный CamelCase           → ``SessionsRow`` / ``PurchasesRow``
for _tbl_name, _cls in _RAW_MODELS.items():
    # sessions → globals()['sessions']
    globals()[_tbl_name] = _cls
    __all__.append(_tbl_name)

    # SessionsRow → globals()['SessionsRow']
    _camel = f"{_tbl_name.title()}Row"
    globals()[_camel] = _cls
    __all__.append(_camel)

# добавляем DTO для raw‑варианта (если он есть)
if TteRawPredictRequest is not None:
    __all__.append("TteRawPredictRequest")
