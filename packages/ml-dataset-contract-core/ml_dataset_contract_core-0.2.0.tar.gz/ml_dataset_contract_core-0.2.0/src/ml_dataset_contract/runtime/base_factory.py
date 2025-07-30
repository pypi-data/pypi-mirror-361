from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from os import PathLike
from typing import Type
from .schema import ContractSchema
from .encoders import NaInfEncoder, DEFAULT_ENCODER


class ContractFactoryBase(ABC):
    """
    Базовый шаблон для класов фабрик.

    Читаем YAML (один раз) и предоставляем содержимое секций
    inputs и targets наследникам.

    Метод build() для генерации динамического класса.
    """

    def __init__(
        self,
        yaml_path: str | PathLike[str],
        *,
        prefix: str | None = None,
        encoder: NaInfEncoder = DEFAULT_ENCODER,
    ) -> None:
        self.schema  = ContractSchema(yaml_path)
        self.prefix  = prefix or Path(yaml_path).stem
        self.encoder = encoder

    @property
    def inputs(self):  return self.schema.inputs

    @property
    def targets(self): return self.schema.targets

    @abstractmethod
    def build(self) -> Type: ...
