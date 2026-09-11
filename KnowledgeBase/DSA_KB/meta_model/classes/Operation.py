from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from .Parameter import Parameter


@dataclass
class Operation:
    name: str
    description: Optional[str] = None
    input: list[Parameter] = field(default_factory=list)
    output: Optional[Union[list[Parameter], Parameter]] = None