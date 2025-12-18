from __future__ import annotations
from typing import Dict, Optional, Callable, List

from interfaces import (
    IResourceManager,
    IProductionService,
    IConstructionService,
    IBuildingFactory,
)
from repositories import BuildingRepository, ResourceRepository
from entities import Resource, Building, ProducerBuilding, StorageBuilding, House, Apartament, CoalMine


class ResourceManager(IResourceManager):
    def __init__(self, resource_repo: ResourceRepository):
        self._repo = resource_repo
        # default capacities
        self._capacity: Dict[str, int] = {}
        for r in ['wood', 'stone', 'food', 'iron', 'energy', 'gold', 'coal', 'sand', 'concrete', 'people']:
            if self._repo.get(r) is None:
                self._repo.add(Resource(r, 0))
            self._capacity[r] = 100  # initial capacity

    def add_resource(self, name: str, amount: int) -> None:
        res = self._repo.get(name)
        if res is None:
            res = Resource(name, 0)
            self._repo.add(res)
            if name not in self._capacity:
                self._capacity[name] = 100
        # respect capacity
        new_amount = min(res.amount + amount, self._capacity[name])
        res.amount = new_amount

    def consume_resource(self, name: str, amount: int) -> bool:
        res = self._repo.get(name)
        if res is None:
            return False
        if res.amount < amount:
            return False
        res.amount -= amount
        return True

    def get_amount(self, name: str) -> int:
        res = self._repo.get(name)
        return res.amount if res else 0

    def get_capacity(self, name: str) -> int:
        return self._capacity.get(name, 0)

    def increase_capacity(self, name: str, amount: int) -> None:
        self._capacity[name] = self._capacity.get(name, 0) + amount


class BuildingFactory(IBuildingFactory):
    def __init__(self):
        self._id_counter = 0

    def _next_id(self) -> int:
        self._id_counter += 1
        return self._id_counter

    def create(self, kind: str) -> Building:
        if not kind or not kind.strip():
            raise ValueError("building kind must be a non-empty string")
        if kind == 'farm':
            return ProducerBuilding(self._next_id(), 'farm', produces={'food': 5})
        if kind == 'lumber_mill':
            return ProducerBuilding(self._next_id(), 'lumber_mill', produces={'wood': 4})
        if kind == 'house':
            return House(self._next_id())
        if kind == 'quarry':
            return ProducerBuilding(self._next_id(), 'quarry', produces={'stone': 3})
        if kind == 'mine':
            return ProducerBuilding(self._next_id(), 'mine', produces={'iron': 2})
        if kind == 'power_plant':
            return ProducerBuilding(self._next_id(), 'power_plant', produces={'energy': 10})
        if kind == 'coal_mine':
            return CoalMine(self._next_id())
        if kind == 'apartament':
            return Apartament(self._next_id())
        if kind == 'sand_quarry':
            return ProducerBuilding(self._next_id(), 'sand_quarry', produces={'sand': 5})
        if kind == 'concrete_factory':
            return ProducerBuilding(self._next_id(), 'concrete_factory', produces={'concrete': 2})
        if kind == 'warehouse':
            return StorageBuilding(
                self._next_id(),
                'warehouse',
                adds_capacity={'wood': 200, 'stone': 200, 'food': 200, 'iron': 100, 'coal': 100, 'sand': 200, 'concrete': 100},
            )
        if kind == 'market':
            return Building(self._next_id(), 'market')
        # default small producer
        return ProducerBuilding(self._next_id(), f'small_{kind}', produces={'food': 1})


class ConstructionService(IConstructionService):
    def __init__(self, resource_manager: IResourceManager, building_repo: BuildingRepository):
        self._rm = resource_manager
        self._buildings = building_repo

    def can_build(self, blueprint: Dict[str, int]) -> bool:
        for name, cost in blueprint.items():
            if self._rm.get_amount(name) < cost:
                return False
        return True

    def build(self, blueprint: Dict[str, int], build_fn: Callable[[], Building]) -> Optional[Building]:
        if not self.can_build(blueprint):
            return None
        # consume resources
        for name, cost in blueprint.items():
            ok = self._rm.consume_resource(name, cost)
            if not ok:
                return None
        b = build_fn()
        self._buildings.add(b)
        if isinstance(b, StorageBuilding):
            for rname, inc in b.adds_capacity.items():
                self._rm.increase_capacity(rname, inc)
        return b


class ProductionService(IProductionService):
    def __init__(self, building_repo: BuildingRepository, resource_manager: IResourceManager):
        self._buildings = building_repo
        self._rm = resource_manager

    def tick(self) -> None:
        for b in self._buildings.all():
            if isinstance(b, ProducerBuilding):
                for rname, amount in b.produces.items():
                    self._rm.add_resource(rname, amount)


class GameService:
    def __init__(
        self,
        rm: ResourceManager,
        br: BuildingRepository,
        factory: BuildingFactory,
        constr: ConstructionService,
        prod: ProductionService,
    ):
        self._rm = rm
        self._br = br
        self._factory = factory
        self._constr = constr
        self._prod = prod

    def list_resources(self) -> Dict[str, int]:
        return {r.name: r.amount for r in self._rm._repo.all()}

    def list_buildings(self) -> List[str]:
        return [b.summary() for b in self._br.all()]

    def build(self, kind: str) -> tuple[bool, str]:
        blueprints = {
            'farm': {'wood': 10, 'stone': 5, 'people': 1},
            'lumber_mill': {'wood': 5, 'stone': 5, 'people': 1},
            'quarry': {'wood': 5, 'stone': 10, 'people': 2},
            'mine': {'wood': 5, 'stone': 10, 'iron': 5, 'people': 3},
            'power_plant': {'stone': 10, 'iron': 10, 'people': 5},
            'warehouse': {'wood': 20, 'stone': 20, 'people': 1},
            'market': {'wood': 10, 'stone': 10, 'people': 2},
            'coal_mine': {'stone': 10, 'iron': 10, 'people': 3},
            'sand_quarry': {'stone': 15, 'iron': 5, 'energy': 10, 'people': 2},
            'concrete_factory': {'stone': 20, 'iron': 15, 'energy': 15, 'people': 3},
            'house': {'wood': 5, 'stone': 2},
            'apartament': {'wood': 15, 'stone': 10},
        }
        bp = blueprints.get(kind, {'wood': 5, 'people': 1})
        if not kind or not kind.strip():
            return False, "Cannot build: no building type specified"
        b = self._constr.build(bp, lambda: self._factory.create(kind))
        if b is None:
            return False, f"Cannot build {kind}: insufficient resources"
        return True, f"Built {b.summary()}"

    def tick(self) -> None:

        self._prod.tick()
