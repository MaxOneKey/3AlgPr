from __future__ import annotations
from typing import Dict

from repositories import BuildingRepository, ResourceRepository
from services import (
    ResourceManager, BuildingFactory, ConstructionService, 
    ProductionService, GameService, ResearchService, TradingService, RaidService
)

class Container:
    def __init__(self):
        self._singletons: Dict[str, object] = {}

    def register_singleton(self, cls_or_name: str, instance) -> None:
        self._singletons[cls_or_name] = instance

    def resolve(self, cls_or_name: str):
        return self._singletons.get(cls_or_name)

def build_container() -> Container:
    c = Container()

    res_repo = ResourceRepository()
    bld_repo = BuildingRepository()
    c.register_singleton('resource_repo', res_repo)
    c.register_singleton('building_repo', bld_repo)

    rm = ResourceManager(res_repo)
    factory = BuildingFactory()
    constr = ConstructionService(rm, bld_repo)
    prod = ProductionService(bld_repo, rm)
    research = ResearchService(rm)
    trading = TradingService(rm)
    raid = RaidService(rm)  # <--- Додано

    c.register_singleton('resource_manager', rm)
    c.register_singleton('building_factory', factory)
    c.register_singleton('construction_service', constr)
    c.register_singleton('production_service', prod)
    c.register_singleton('research_service', research)
    c.register_singleton('trading_service', trading)
    c.register_singleton('raid_service', raid) # <--- Додано

    # Передаємо raid у GameService
    gs = GameService(rm, bld_repo, factory, constr, prod, research, trading, raid)
    c.register_singleton('game_service', gs)

    # Стартові ресурси
    rm.add_resource('wood', 20)
    rm.add_resource('stone', 20)
    rm.add_resource('food', 10)
    rm.add_resource('iron', 5)
    rm.add_resource('research_points', 5)
    rm.add_resource('gold', 50) 

    return c
