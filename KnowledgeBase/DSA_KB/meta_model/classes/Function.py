from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from .Parameter import Parameter

@dataclass
class Function:
    id: str
    name: str
    input: list[Parameter] = field(default_factory=list)
    output: Optional[Union[Parameter, list[Parameter]]] = None
    description: Optional[str] = None