from __future__ import annotations
from typing import Dict, Optional, Callable, List
from interfaces import (
    IResourceManager, IProductionService, IConstructionService, IBuildingFactory
)
from repositories import BuildingRepository, ResourceRepository
from entities import (
    Resource, Building, ProducerBuilding, StorageBuilding
)

class ResourceManager(IResourceManager):
    def __init__(self, resource_repo: ResourceRepository):
        self._repo = resource_repo
        self._capacity: Dict[str, int] = {}
        for r in ['wood', 'stone', 'food', 'iron', 'energy', 'coal', 'sand', 'concrete', 'people', 'graduates', 'masters']:
            if self._repo.get(r) is None:
                self._repo.add(Resource(r, 0))
            
            if r == 'graduates':
                self._capacity[r] = 10
            elif r == 'masters':
                self._capacity[r] = 5
            else:
                self._capacity[r] = 100

    def add_resource(self, name: str, amount: int) -> None:
        res = self._repo.get(name)
        if res is None: return
        cap = self.get_capacity(name)
        res.amount = min(res.amount + amount, cap)

    def consume_resource(self, name: str, amount: int) -> bool:
        res = self._repo.get(name)
        if res is None or res.amount < amount:
            return False
        res.amount -= amount
        return True
    
    def has_resource(self, name: str, amount: int) -> bool:
        res = self._repo.get(name)
        return res is not None and res.amount >= amount

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

        if kind == 'school':
            return ProducerBuilding(self._next_id(), 'school', 
                                    produces={'graduates': 1}, 
                                    consumes={'people': 1, 'food': 1})
        if kind == 'library':
            return ProducerBuilding(self._next_id(), 'library', 
                                    produces={'graduates': 1}, 
                                    consumes={'people': 1, 'energy': 2})
        if kind == 'university':
            return ProducerBuilding(self._next_id(), 'university', 
                                    produces={'masters': 1}, 
                                    consumes={'graduates': 1, 'energy': 5})
        if kind == 'farm':
            return ProducerBuilding(self._next_id(), 'farm', produces={'food': 10})
        
        if kind == 'lumber_mill':
            return ProducerBuilding(self._next_id(), 'lumber_mill', produces={'wood': 5})
        
        if kind == 'coal_mine':
            # Вугілля потрібне для енергії
            return ProducerBuilding(self._next_id(), 'coal_mine', produces={'coal': 5}, consumes={'wood': 1})
            
        if kind == 'power_plant':
            # Енергія потрібна для заводів. Споживає вугілля.
            return ProducerBuilding(self._next_id(), 'power_plant', produces={'energy': 20}, consumes={'coal': 3})
            
        if kind == 'quarry':
            return ProducerBuilding(self._next_id(), 'quarry', produces={'stone': 5}, consumes={'energy': 1})
            
        if kind == 'mine':
            return ProducerBuilding(self._next_id(), 'mine', produces={'iron': 3}, consumes={'energy': 2})
            
        if kind == 'sand_quarry':
            return ProducerBuilding(self._next_id(), 'sand_quarry', produces={'sand': 5}, consumes={'energy': 1})
            
        if kind == 'concrete_factory':
            return ProducerBuilding(
                self._next_id(), 
                'concrete_factory', 
                produces={'concrete': 4}, 
                consumes={'stone': 2, 'sand': 2, 'energy': 5}
            )
            
        if kind == 'house':
            return ProducerBuilding(self._next_id(), 'house', produces={'people': 1}, consumes={'food': 2})

        if kind == 'warehouse':
            return StorageBuilding(
                self._next_id(),
                'warehouse',
                adds_capacity={'wood': 200, 'stone': 200, 'food': 200, 'iron': 100, 'coal': 100}
            )

        raise ValueError(f"Unknown building kind: {kind}")


class ConstructionService(IConstructionService):
    def __init__(self, resource_manager: IResourceManager, building_repo: BuildingRepository):
        self._rm = resource_manager
        self._buildings = building_repo

    def can_build(self, blueprint: Dict[str, int]) -> bool:
        for name, cost in blueprint.items():
            if not self._rm.has_resource(name, cost):
                return False
        return True

    def build(self, blueprint: Dict[str, int], build_fn: Callable[[], Building]) -> Optional[Building]:
        if not self.can_build(blueprint):
            return None
        for name, cost in blueprint.items():
            self._rm.consume_resource(name, cost)
        
        b = build_fn()
        self._buildings.add(b)
        
        if isinstance(b, StorageBuilding):
            for rname, inc in b.adds_capacity.items():
                self._rm.increase_capacity(rname, inc)
        return b
    
    def upgrade_building(self, building_id: int) -> tuple[bool, str]:
        buildings = [b for b in self._buildings.all() if b.id == building_id]
        if not buildings:
            return False, "Building not found"
        b = buildings[0]
        
        cost_wood = 20 * b.level
        cost_stone = 20 * b.level
        cost_concrete = 5 * b.level
        
        blueprint = {'wood': cost_wood, 'stone': cost_stone, 'concrete': cost_concrete}
        
        if not self.can_build(blueprint):
            return False, f"Need resources for upgrade: {blueprint}"
            
        for name, cost in blueprint.items():
            self._rm.consume_resource(name, cost)
            
        if isinstance(b, StorageBuilding):
            old_caps = b.adds_capacity
            b.upgrade()
            new_caps = b.adds_capacity
            for rname, val in new_caps.items():
                diff = val - old_caps.get(rname, 0)
                self._rm.increase_capacity(rname, diff)
        else:
            b.upgrade()
            
        return True, f"Upgraded {b.kind} to Level {b.level}"


class ProductionService(IProductionService):
    def __init__(self, building_repo: BuildingRepository, resource_manager: IResourceManager):
        self._buildings = building_repo
        self._rm = resource_manager

    def tick(self) -> None:
        """
        Головний цикл тіку.
        1. Споживання населенням їжі.
        2. Виробництво будівель (зі споживанням вхідних ресурсів).
        """
        people = self._rm.get_amount('people')
        if people > 0:
            food_needed = max(1, int(people * 0.2)) 
            if not self._rm.consume_resource('food', food_needed):
                self._rm.consume_resource('people', max(1, int(people * 0.1)))
                print(f"  [!] STARVATION: Not enough food. Population decreased.")

        for b in self._buildings.all():
            if isinstance(b, ProducerBuilding):
                self._process_producer(b)

    def _process_producer(self, b: ProducerBuilding) -> None:
        can_produce = True
        
        for rname, amount in b.consumes.items():
            if not self._rm.has_resource(rname, amount):
                can_produce = False
                break
        
        if can_produce:
            for rname, amount in b.consumes.items():
                self._rm.consume_resource(rname, amount)
            for rname, amount in b.produces.items():
                self._rm.add_resource(rname, amount)


class GameService:
    def __init__(self, rm, br, factory, constr, prod):
        self._rm = rm
        self._br = br
        self._factory = factory
        self._constr = constr
        self._prod = prod
        
        self._building_configs = {
            'living': {
                'house': {'wood': 20, 'stone': 10},
                'school': {'wood': 40, 'stone': 20},
                'library': {'wood': 20, 'stone': 50},
                'university': {'iron': 30, 'concrete': 20, 'energy': 10},
            },
            'industrial': {
                'power_plant': {'stone': 50, 'iron': 20, 'concrete': 10},
                'concrete_factory': {'stone': 50, 'iron': 20, 'energy': 10},
                'warehouse': {'wood': 50, 'stone': 50},
            },
            'mining': {
                'farm': {'wood': 10, 'stone': 5},
                'lumber_mill': {'wood': 10, 'stone': 10},
                'coal_mine': {'wood': 20, 'stone': 20},
                'quarry': {'wood': 20},
                'mine': {'wood': 50, 'stone': 50},
                'sand_quarry': {'wood': 10, 'stone': 10},
            }
        }

    def get_building_catalog(self) -> Dict[str, Dict[str, Dict[str, int]]]:
        """Повертає весь каталог будівель з категоріями та цінами"""
        return self._building_configs

    def build(self, kind: str) -> tuple[bool, str]:
        bp = None
        for cat_bldgs in self._building_configs.values():
            if kind in cat_bldgs:
                bp = cat_bldgs[kind]
                break
        
        if not bp:
            return False, f"Unknown blueprint for {kind}"

        if not self._rm.has_resource('people', 2):
             return False, "Not enough idle people (need 2) to build"
        
        b = self._constr.build(bp, lambda: self._factory.create(kind))
        if b is None:
            return False, f"Insufficient resources for {kind}: {bp}"
            
        return True, f"Built {b.summary()}"

    def upgrade(self, building_id: int) -> tuple[bool, str]:
        return self._constr.upgrade_building(building_id)

    def tick(self) -> None:
        self._prod.tick()
    
    def list_resources(self) -> Dict[str, int]:
        return {r.name: r.amount for r in self._rm._repo.all()}

    def list_buildings(self) -> List[Building]:
        return self._br.all()




