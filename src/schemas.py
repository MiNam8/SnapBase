from typing import Protocol

class HasNameAndId(Protocol):
    name: str
    id: int