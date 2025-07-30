from __future__ import annotations
from typing import Type, Dict
from pydantic import BaseModel, Field, create_model
from .base_factory import ContractFactoryBase


class PydanticFeatureFactory(ContractFactoryBase):
    """
    Строит класс FeatureRow со входными признаками модели.
    """

    def build(self) -> Type[BaseModel]:
        fields: Dict[str, Type] = self.inputs
        return create_model(
            f"{self.prefix}_FeatureRow",
            __base__=BaseModel,
            __module__=__name__,
            **{k: (t, Field(...)) for k, t in fields.items()},
        )
