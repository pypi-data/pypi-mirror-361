import math
from typing import Any


class NaInfEncoder:
    """
    Преобразует:
      - NaN  -> None
      - +Inf -> inf_value
      - -Inf -> -inf_value
    """

    def __init__(self, inf_value: float = 9999):
        self.inf_value = inf_value

    def __call__(self, obj: Any) -> Any:
        if isinstance(obj, float):
            if math.isnan(obj):
                return None
            if math.isinf(obj):
                return self.inf_value if obj > 0 else -self.inf_value
            return obj
        if isinstance(obj, (list, tuple)):
            return [self(x) for x in obj]
        if isinstance(obj, dict):
            return {k: self(v) for k, v in obj.items()}
        return obj


DEFAULT_ENCODER: NaInfEncoder = NaInfEncoder()
