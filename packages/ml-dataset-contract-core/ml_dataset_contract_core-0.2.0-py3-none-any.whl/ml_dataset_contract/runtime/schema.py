from __future__ import annotations
from pathlib import Path
from typing import Dict, Type, Tuple, Any, Mapping
from decimal import Decimal
import yaml
from datetime import datetime, date, time

_PY_TYPES: Dict[str, Type[Any]] = {
    "float": float,
    "int": int,
    "str": str,
    "bool": bool,
    "datetime": datetime,
    "date": date,
    "time": time,
    "decimal": Decimal,
    "any": Any,
}

_SECTION_INPUTS = "inputs"
_SECTION_TARGETS = "targets"
_SECTION_RAW = "raw_tables"


class ContractSchema:
    def __init__(self, yaml_path: str | "os.PathLike[str]") -> None:
        self.path = Path(yaml_path)
        self._raw_tables, self._inputs, self._targets = self._load()

    @property
    def raw_tables(self) -> Dict[str, Dict[str, Type]]:
        return self._raw_tables

    @property
    def inputs(self) -> Dict[str, Type]:
        return self._inputs

    @property
    def targets(self) -> Dict[str, Type]:
        return self._targets

    def _load(
        self
    ) -> Tuple[Dict[str, Dict[str, Type]], Dict[str, Type], Dict[str, Type]]:
        with self.path.open(encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        if not {_SECTION_INPUTS, _SECTION_TARGETS} <= raw.keys():
            raise KeyError(
                f"YAML must contain '{_SECTION_INPUTS}' and "
                f"'{_SECTION_TARGETS}' sections"
            )

        raw_tables: Dict[str, Dict[str, Type]] = {
            table: self._convert(cols)
            for table, cols in raw.get(_SECTION_RAW, {}).items()
        }

        inputs = self._convert(raw[_SECTION_INPUTS])
        targets = self._convert(raw[_SECTION_TARGETS])
        return raw_tables, inputs, targets

    @staticmethod
    def _convert(raw_map: Dict[str, str]) -> Dict[str, Type]:
        unknown = set(raw_map.values()) - _PY_TYPES.keys()
        if unknown:
            raise ValueError(f"Unknown types in YAML: {unknown}")

        return {k: _PY_TYPES[v] for k, v in raw_map.items()}
