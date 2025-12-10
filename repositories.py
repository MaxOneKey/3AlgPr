from __future__ import annotations
from typing import Dict, List, Optional

from interfaces import IRepository
from entities import Building, Resource


class BuildingRepository(IRepository):
    def __init__(self):
        self._store: List[Building] = []

    def all(self) -> List[Building]:
        return list(self._store)

    def add(self, item: Building) -> None:
        self._store.append(item)


class ResourceRepository(IRepository):
    def __init__(self):
        self._store: Dict[str, Resource] = {}

    def all(self) -> List[Resource]:
        return list(self._store.values())

    def add(self, item: Resource) -> None:
        self._store[item.name] = item

    def get(self, name: str) -> Optional[Resource]:
        return self._store.get(name)