from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class Parameter:
    name: str
    value_type: str
    required: bool = True

    @property
    def valueType(self) -> str:
        return self.value_type

    @valueType.setter
    def valueType(self, val: str):
        self.value_type = val
