from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Union

@dataclass
class Operand:
    id: Optional[str] = None
    operand_type: Optional[str] = None
    variable: Optional[str] = None
    value: Optional[str] = None

    @property
    def operandType(self) -> Optional[str]:
        return self.operand_type

    @operandType.setter
    def operandType(self, val: Optional[str]):
        self.operand_type = val