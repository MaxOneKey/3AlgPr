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
class IResearchService(ABC):
    @abstractmethod
    def get_available_techs(self) -> Dict[str, dict]: 
        ...
    
    @abstractmethod
    def is_building_unlocked(self, kind: str) -> bool: 
        ...
    
    @abstractmethod
    def research(self, tech_name: str) -> tuple[bool, str]: 
        ...


class ITradingService(ABC):
    @abstractmethod
    def get_active_cities(self) -> List[str]: 
        ...
    
    @abstractmethod
    def get_offers(self, city_name: str) -> List[dict]: 
        ...
    
    @abstractmethod
    def execute_trade(self, city_name: str, offer_index: int) -> tuple[bool, str]: 
        ...


class IRaidService(ABC):
    @abstractmethod
    def execute_raid(self) -> tuple[bool, str]: 
        ...


class IGameService(ABC):
    @abstractmethod
    def list_resources(self) -> Dict[str, int]: 
        ...

    @abstractmethod
    def list_buildings(self) -> List[IBuilding]: 
        ...

    @abstractmethod
    def get_building_catalog(self) -> Dict[str, Dict[str, Dict[str, int]]]: 
        ...

    @abstractmethod
    def list_research(self) -> Dict[str, dict]: 
        ...

    @abstractmethod
    def research_tech(self, tech_name: str) -> tuple[bool, str]: 
        ...

    @abstractmethod
    def build(self, kind: str) -> tuple[bool, str]: 
        ...

    @abstractmethod
    def build_ship(self) -> tuple[bool, str]: 
        ...

    @abstractmethod
    def upgrade(self, building_id: int) -> tuple[bool, str]: 
        ...

    @abstractmethod
    def tick(self) -> None: 
        ...

    @abstractmethod
    def get_trading_cities(self) -> List[str]: 
        ...

    @abstractmethod
    def get_city_offers(self, city: str) -> List[dict]: 
        ...

    @abstractmethod
    def trade(self, city: str, offer_idx: int) -> tuple[bool, str]: 
        ...

    @abstractmethod
    def raid(self) -> tuple[bool, str]: 
        ...
