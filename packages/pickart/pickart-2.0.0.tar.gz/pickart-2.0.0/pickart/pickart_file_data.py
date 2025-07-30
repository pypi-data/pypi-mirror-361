from typing import Any
from dataclasses import dataclass, field


@dataclass
class PickartFileData:
    info: dict[str, Any] = field(default_factory=dict)
    palette: list[tuple] = field(default_factory=list)
    pixels: list[list] = field(default_factory=list)
