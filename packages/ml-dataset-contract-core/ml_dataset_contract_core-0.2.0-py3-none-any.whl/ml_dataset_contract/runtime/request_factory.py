"""ml_dataset_contract.runtime.request_factory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Фабрики, строящие Pydantic‑DTO для REST‑API:

* **PydanticRequestFactory**      – инженерные (готовые) признаки
* **PydanticRawRequestFactory**   – сырые таблицы (bronze‑layer)

Правки сведены к минимуму: изменён только блок сериализации в Raw‑варианте,
чтобы `model_dump_json()` сохранял поля вложенных моделей.
"""
from __future__ import annotations

from typing import Type, List, Any, Dict

from pydantic import BaseModel, model_validator, ConfigDict

from .base_factory import ContractFactoryBase
from .encoders import NaInfEncoder

###############################################################################
#  PredictRequest – инженераные признаки
###############################################################################

class PydanticRequestFactory(ContractFactoryBase):
    """Строит DTO‑класс ``PredictRequest`` под формат Mlflow Serve.

    Формат вывода метода ``to_split_json`` соответствует ``dataframe_split``.
    """

    def __init__(self, *args, feature_cls: Type[BaseModel], **kw) -> None:
        super().__init__(*args, **kw)
        self.feature_cls = feature_cls
        self._cols = list(self.inputs)

    # ---------------------------------------------------------------------
    #  Генерация класса
    # ---------------------------------------------------------------------
    def build(self) -> Type[BaseModel]:
        cols = self._cols
        enc = self.encoder
        FeatureRow = self.feature_cls

        class PredictRequest(BaseModel):
            rows: List[FeatureRow]
            model_config = {"json_encoders": {float: enc}}

            @model_validator(mode="after")
            def _no_empty(self):
                if not self.rows:
                    raise ValueError("rows can't be empty")
                return self

            # -------------------------------------------------------------
            #  Mlflow‑совместимый JSON
            # -------------------------------------------------------------
            def to_split_json(
                self, *, encoder: NaInfEncoder | None = None
            ) -> Dict[str, Any]:
                e = encoder or enc
                data = [[e(getattr(r, c)) for c in cols] for r in self.rows]
                return {"dataframe_split": {"columns": cols, "data": data}}

        PredictRequest.__name__ = f"{self.prefix}_PredictRequest"
        return PredictRequest

###############################################################################
#  RawPredictRequest – сырые таблицы
###############################################################################

class PydanticRawRequestFactory(ContractFactoryBase):
    """Строит DTO‑класс ``RawPredictRequest`` для набора сырых таблиц.

    Формат тела запроса::

        {
            "tables": {
                "sessions":  [{...}, {...}],
                "purchases": [{...}]
            }
        }
    """

    def __init__(self, *a, raw_cls_map: Dict[str, Type[BaseModel]], **kw):
        super().__init__(*a, **kw)
        self._raw_cls_map = raw_cls_map

    # ---------------------------------------------------------------------
    #  Генерация класса
    # ---------------------------------------------------------------------
    def build(self) -> Type[BaseModel]:
        cls_map = self._raw_cls_map

        class RawPredictRequest(BaseModel):
            # важный момент: Any + arbitrary_types_allowed → модели не схлопываются
            model_config = ConfigDict(arbitrary_types_allowed=True)
            tables: Dict[str, List[Any]]

            # ---------------------------------------------------------
            #  Валидация
            # ---------------------------------------------------------
            @model_validator(mode="after")
            def _validate_tables(self):
                expect = set(cls_map)
                got = set(self.tables)
                if expect - got:
                    raise ValueError(f"missing tables: {expect - got}")

                # Проверяем/конвертируем строки каждой таблицы
                for tbl_name, rows in self.tables.items():
                    expected_cls = cls_map[tbl_name]
                    for i, row in enumerate(rows):
                        # 1) уже нужная модель
                        if isinstance(row, expected_cls):
                            continue
                        # 2) dict → валидируем и преобразуем
                        if isinstance(row, dict):
                            rows[i] = expected_cls.model_validate(row)
                            continue
                        raise TypeError(
                            f"tables['{tbl_name}'][{i}] must be {expected_cls.__name__} "
                            f"or dict, not {type(row)}"
                        )
                return self

        RawPredictRequest.__name__ = f"{self.prefix}_RawPredictRequest"
        return RawPredictRequest
