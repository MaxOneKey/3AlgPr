
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

    @property
    def id(self) -> int:
        return self._id

    @property
    def kind(self) -> str:
        return self._kind

    def summary(self) -> str:
        return f"#{self._id} [{self._kind}]"




class ProducerBuilding(Building):
    """Producer building generates resources per tick"""

    def __init__(self, id_: int, kind: str, produces: Dict[str, int], work_cost: int = 0):
        super().__init__(id_, kind)
        self.produces = produces
        self.work_cost = work_cost


class StorageBuilding(Building):
    """Storage building increases capacity"""

    def __init__(self, id_: int, kind: str, adds_capacity: Dict[str, int]):
        super().__init__(id_, kind)
        self.adds_capacity = adds_capacity


# small concrete types for clarity
class Farm(ProducerBuilding):
    def __init__(self, id_: int):
        super().__init__(id_, 'farm', produces={'food': 5})


class LumberMill(ProducerBuilding):
    def __init__(self, id_: int):
        super().__init__(id_, 'lumber_mill', produces={'wood': 4})


class House(ProducerBuilding):
    def __init__(self, id_: int):
        # houses produce 1 person per tick
        super().__init__(id_, 'house', produces={'people': 1})


class Apartament(ProducerBuilding):
    def __init__(self, id_: int):
        # apartaments produce more people than a single house
        super().__init__(id_, 'apartament', produces={'people': 3})


class CoalMine(ProducerBuilding):
    def __init__(self, id_: int):
        super().__init__(id_, 'coal_mine', produces={'coal': 8})
