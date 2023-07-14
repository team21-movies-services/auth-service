from dataclasses import asdict, dataclass
from typing import Any


@dataclass()
class BaseDTO:
    def as_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Any:
        return cls(**data)
