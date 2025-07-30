from __future__ import annotations
from typing import Dict, Type
from pydantic import BaseModel, Field, create_model
from .base_factory import ContractFactoryBase

class PydanticRawFactory(ContractFactoryBase):
    """
    Генерирует Pydantic-классы для каждой таблицы первичных данных.
    """
    def build(self) -> dict[str, Type[BaseModel]]:
        models = {}
        for tbl, fields in self.schema.raw_tables.items():
            models[tbl] = create_model(
                f"{self.prefix}_{tbl.title()}Row",
                __base__=BaseModel,
                __module__=__name__,
                **{k: (t, Field(...)) for k, t in fields.items()},
            )
        return models
