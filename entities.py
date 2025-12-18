from __future__ import annotations
from typing import Dict
from interfaces import IResource, IBuilding

class Resource(IResource):
    """Resource in the city"""
    def __init__(self, name: str, amount: int = 0):
        self._name = name
        self._amount = amount

    @property
    def name(self) -> str:
        return self._name

    @property
    def amount(self) -> int:
        return self._amount

    @amount.setter
    def amount(self, value: int) -> None:
        self._amount = value

    def __repr__(self) -> str:
        return f"{self._name}: {self._amount}"


class Building(IBuilding):
    """Base building"""
    def __init__(self, id_: int, kind: str):
        self._id = id_
        self._kind = kind
        self._level = 1

    @property
    def id(self) -> int:
        return self._id

    @property
    def kind(self) -> str:
        return self._kind
    
    @property
    def level(self) -> int:
        return self._level

    def upgrade(self) -> None:
        self._level += 1

    def summary(self) -> str:
        return f"#{self._id} [{self._kind}] (Lvl {self._level})"


class ProducerBuilding(Building):
    """
    Producer building generates resources
    """
    def __init__(self, id_: int, kind: str, produces: Dict[str, int], consumes: Dict[str, int] = None):
        super().__init__(id_, kind)
        self._base_produces = produces
        self._base_consumes = consumes or {}

    @property
    def produces(self) -> Dict[str, int]:
        multiplier = 1 + (self._level - 1) * 0.5
        return {k: int(v * multiplier) for k, v in self._base_produces.items()}

    @property
    def consumes(self) -> Dict[str, int]:
        multiplier = 1 + (self._level - 1) * 0.2
        return {k: int(v * multiplier) for k, v in self._base_consumes.items()}

    def summary(self) -> str:
        base = super().summary()
        prod_str = ", ".join([f"+{v} {k}" for k, v in self.produces.items()])
        cons_str = ", ".join([f"-{v} {k}" for k, v in self.consumes.items()])
        info = prod_str
        if cons_str:
            info += f" | {cons_str}"
        return f"{base} -> {info}"


class StorageBuilding(Building):
    """Storage building increases capacity based on level"""
    def __init__(self, id_: int, kind: str, adds_capacity: Dict[str, int]):
        super().__init__(id_, kind)
        self._base_capacity = adds_capacity

    @property
    def adds_capacity(self) -> Dict[str, int]:
        multiplier = self._level
        return {k: v * multiplier for k, v in self._base_capacity.items()}
