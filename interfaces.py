from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Optional


class IRepository(ABC):
    @abstractmethod
    def all(self):
        ...

    @abstractmethod
    def add(self, item):
        ...


class IResource(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def amount(self) -> int:
        ...


class IBuilding(ABC):
    @property
    @abstractmethod
    def id(self) -> int:
        ...

    @property
    @abstractmethod
    def kind(self) -> str:
        ...

    @abstractmethod
    def summary(self) -> str:
        ...


class IProduction(ABC):
    @abstractmethod
    def tick(self) -> None:
        ...


class IPlayerAction(ABC):
    @abstractmethod
    def build(self, kind: str) -> tuple[bool, str]:
        ...


class ILogger(ABC):
    @abstractmethod
    def log(self, msg: str) -> None:
        ...


class IContainer(ABC):
    @abstractmethod
    def register_singleton(self, cls_or_name: str, instance) -> None:
        ...

    @abstractmethod
    def resolve(self, cls_or_name: str):
        ...


class IResourceManager(ABC):
    @abstractmethod
    def add_resource(self, name: str, amount: int) -> None:
        ...

    @abstractmethod
    def consume_resource(self, name: str, amount: int) -> bool:
        ...

    @abstractmethod
    def get_amount(self, name: str) -> int:
        ...

    @abstractmethod
    def get_capacity(self, name: str) -> int:
        ...

    @abstractmethod
    def increase_capacity(self, name: str, amount: int) -> None:
        ...


class IProductionService(ABC):
    @abstractmethod
    def tick(self) -> None:
        ...


class IConstructionService(ABC):
    @abstractmethod
    def can_build(self, blueprint: Dict[str, int]) -> bool:
        ...

    @abstractmethod
    def build(self, blueprint: Dict[str, int], build_fn: Callable[[], object]) -> Optional[object]:
        ...


class IBuildingFactory(ABC):
    @abstractmethod
    def create(self, kind: str):
        ...


class IGameUI(ABC):
    @abstractmethod
    def main_loop(self) -> None:
        ...