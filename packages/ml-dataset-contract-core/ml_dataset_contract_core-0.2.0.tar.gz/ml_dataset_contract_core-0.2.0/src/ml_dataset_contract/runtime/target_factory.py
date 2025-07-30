from __future__ import annotations
from typing import Type, Dict
from pydantic import BaseModel, Field, create_model

from .base_factory import ContractFactoryBase


class PydanticTargetFactory(ContractFactoryBase):
    """
    Строит класс TargetRow с целевыми признаками модели.
    """

    def build(self) -> Type[BaseModel]:
        fields: Dict[str, Type] = self.targets
        return create_model(
            f"{self.prefix}_TargetRow",
            __base__=BaseModel,
            __module__=__name__,
            **{k: (t, Field(...)) for k, t in fields.items()},
        )
