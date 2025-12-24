from __future__ import annotations
from typing import Dict, Optional, Callable, List, Set
import random
from interfaces import (
    IResourceManager, IProductionService, IConstructionService, IBuildingFactory
)
from repositories import BuildingRepository, ResourceRepository
from entities import (
    Resource, Building, ProducerBuilding, StorageBuilding, WaterTower
)

class ResourceManager(IResourceManager):
    def __init__(self, resource_repo: ResourceRepository):
        self._repo = resource_repo
        self._capacity: Dict[str, int] = {}
        all_resources = [
            'wood', 'stone', 'food', 'iron', 'energy', 'coal', 'sand', 'concrete', 'people', 
            'graduates', 'masters', 'planks', 'water', 'fish', 'steel', 'research_points', 'ship',
            'gold'
        ]
        
        for r in all_resources:
            if self._repo.get(r) is None:
                self._repo.add(Resource(r, 0))
            
            if r == 'graduates':
                self._capacity[r] = 10
            elif r == 'masters':
                self._capacity[r] = 5
            elif r == 'ship':
                self._capacity[r] = 5
            elif r == 'gold':
                self._capacity[r] = 1000
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
        if kind == 'logistics_center':
            return Building(self._next_id(), 'logistics_center')

        if kind == 'park':
            return Building(self._next_id(), 'park')
        if kind == 'carpenter':
            return ProducerBuilding(self._next_id(), 'carpenter', produces={'planks': 1}, consumes={'wood': 1})
        if kind == 'water_tower':
            return WaterTower(self._next_id(), 'water_tower')
        if kind == 'port':
            return ProducerBuilding(self._next_id(), 'port', produces={'fish': 5}, consumes={'energy': 2})
        if kind == 'metallurgy_plant':
            return ProducerBuilding(self._next_id(), 'metallurgy_plant', produces={'steel': 1}, consumes={'iron': 1, 'coal': 1, 'energy': 5})
        if kind == 'science_lab':
            return ProducerBuilding(self._next_id(), 'science_lab', produces={'research_points': 1}, consumes={'planks': 1, 'energy': 3})
        if kind == 'library':
            return ProducerBuilding(self._next_id(), 'library', produces={'graduates': 1, 'research_points': 1}, consumes={'people': 1, 'energy': 2})

        if kind == 'school':
            return ProducerBuilding(self._next_id(), 'school', produces={'graduates': 1}, consumes={'people': 1, 'food': 1})
        if kind == 'university':
            return ProducerBuilding(self._next_id(), 'university', produces={'masters': 1}, consumes={'graduates': 1, 'energy': 5})
        if kind == 'farm':
            return ProducerBuilding(self._next_id(), 'farm', produces={'food': 10})
        if kind == 'lumber_mill':
            return ProducerBuilding(self._next_id(), 'lumber_mill', produces={'wood': 5})
        if kind == 'coal_mine':
            return ProducerBuilding(self._next_id(), 'coal_mine', produces={'coal': 5}, consumes={'wood': 1})
        if kind == 'power_plant':
            return ProducerBuilding(self._next_id(), 'power_plant', produces={'energy': 20}, consumes={'coal': 3})
        if kind == 'quarry':
            return ProducerBuilding(self._next_id(), 'quarry', produces={'stone': 5}, consumes={'energy': 1})
        if kind == 'mine':
            return ProducerBuilding(self._next_id(), 'mine', produces={'iron': 3}, consumes={'energy': 2})
        if kind == 'sand_quarry':
            return ProducerBuilding(self._next_id(), 'sand_quarry', produces={'sand': 5}, consumes={'energy': 1})
        if kind == 'concrete_factory':
            return ProducerBuilding(self._next_id(), 'concrete_factory', produces={'concrete': 4}, consumes={'stone': 2, 'sand': 2, 'energy': 5})
        if kind == 'house':
            return ProducerBuilding(self._next_id(), 'house', produces={'people': 1}, consumes={'food': 2})
        if kind == 'warehouse':
            return StorageBuilding(self._next_id(), 'warehouse', adds_capacity={'wood': 200, 'stone': 200, 'food': 200, 'iron': 100, 'coal': 100, 'planks': 100, 'steel': 50})

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
        
        if hasattr(b, 'adds_capacity'):
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
            
        old_caps = {}
        if hasattr(b, 'adds_capacity'):
            old_caps = b.adds_capacity

        b.upgrade()

        if hasattr(b, 'adds_capacity'):
            new_caps = b.adds_capacity
            for rname, val in new_caps.items():
                diff = val - old_caps.get(rname, 0)
                self._rm.increase_capacity(rname, diff)
            
        return True, f"Upgraded {b.kind} to Level {b.level}"


class ProductionService(IProductionService):
    def __init__(self, building_repo: BuildingRepository, resource_manager: IResourceManager):
        self._buildings = building_repo
        self._rm = resource_manager

    def tick(self) -> None:
        people = self._rm.get_amount('people')
        
        if people > 0:
            food_needed = max(1, int(people * 0.2)) 
            if not self._rm.consume_resource('food', food_needed):
                self._rm.consume_resource('people', max(1, int(people * 0.1)))
                print(f"  [!] STARVATION: Not enough food.")

        all_buidings_count = len(self._buildings.all())
        water_needed = all_buidings_count
        if water_needed > 0:
            if not self._rm.consume_resource('water', water_needed):
                print(f"  [!] DROUGHT: Not enough water (-{water_needed}).")
                if people > 0:
                     self._rm.consume_resource('people', 1)

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


class ResearchService:
    def __init__(self, resource_manager: IResourceManager):
        self._rm = resource_manager
        self._unlocked_techs: Set[str] = set()
        
        self._tech_tree = {
            'basic_logistics': {
                'cost': 10, 
                'unlocks_buildings': ['warehouse', 'carpenter'],
                'desc': 'Better storage and wood processing'
            },
            'fluid_mechanics': {
                'cost': 20,
                'unlocks_buildings': ['water_tower', 'port'],
                'desc': 'Pumps and towers for water management'
            },
            'metallurgy': {
                'cost': 50,
                'unlocks_buildings': ['coal_mine', 'mine', 'metallurgy_plant'],
                'desc': 'Mining and steel production'
            },
            'construction_ii': {
                'cost': 40,
                'unlocks_buildings': ['concrete_factory', 'sand_quarry'],
                'desc': 'Advanced materials (Concrete)'
            },
            'advanced_education': {
                'cost': 100,
                'unlocks_buildings': ['university', 'science_lab'],
                'desc': 'Higher learning and faster research'
            },
            'power_grid': {
                'cost': 80,
                'unlocks_buildings': ['power_plant'],
                'desc': 'Massive energy production'
            },
            'trade_logistics': {
                'cost': 60,
                'unlocks_buildings': ['logistics_center'],
                'desc': 'Unlock trading with other cities'
            }
        }
        
        self._base_buildings = {
            'house', 'park', 'farm', 'lumber_mill', 'quarry', 'school', 'library'
        }

    def get_available_techs(self) -> Dict[str, dict]:
        return {k: v for k, v in self._tech_tree.items() if k not in self._unlocked_techs}

    def is_building_unlocked(self, kind: str) -> bool:
        if kind in self._base_buildings:
            return True
        for tech in self._unlocked_techs:
            if kind in self._tech_tree[tech]['unlocks_buildings']:
                return True
        return False

    def research(self, tech_name: str) -> tuple[bool, str]:
        if tech_name in self._unlocked_techs:
            return False, "Already researched."
        
        tech = self._tech_tree.get(tech_name)
        if not tech:
            return False, "Unknown technology."
        
        cost = tech['cost']
        if not self._rm.has_resource('research_points', cost):
            return False, f"Need {cost} Research Points."
        
        self._rm.consume_resource('research_points', cost)
        self._unlocked_techs.add(tech_name)
        return True, f"Researched '{tech_name}'! Unlocked: {', '.join(tech['unlocks_buildings'])}"


class TradingService:
    def __init__(self, resource_manager: IResourceManager):
        self._rm = resource_manager
        
        self._base_prices = {
            'wood': 2, 'stone': 3, 'food': 2, 'coal': 4, 
            'iron': 5, 'planks': 5, 'fish': 3, 'steel': 15,
            'concrete': 10, 'water': 1
        }
        
        self._available_cities = ["Kyiv", "Lviv", "Odesa", "Kharkiv", "Dnipro", "Poltava", "Vinnytsia"]
        self._current_offers = {}
        self._active_cities = []
        
        self._regenerate_market()

    def _regenerate_market(self):
        self._active_cities = random.sample(self._available_cities, 3)
        self._current_offers = {}
        
        for city in self._active_cities:
            self._current_offers[city] = self._generate_city_offers()

    def _generate_city_offers(self) -> List[dict]:
        offers = []
        resources = list(self._base_prices.keys())
        
        buy_res = random.sample(resources, 4)
        for r in buy_res:
            base = self._base_prices[r]
            price = max(1, int(base * random.uniform(1.2, 1.6)))
            offers.append({
                'type': 'BUY_FROM_CITY',
                'resource': r,
                'price_gold': price,
                'amount': 10
            })

        sell_res = random.sample(resources, 4)
        for r in sell_res:
            base = self._base_prices[r]
            price = max(1, int(base * random.uniform(0.7, 1.0)))
            offers.append({
                'type': 'SELL_TO_CITY',
                'resource': r,
                'price_gold': price,
                'amount': 10
            })
            
        return offers

    def get_active_cities(self) -> List[str]:
        return self._active_cities

    def get_offers(self, city_name: str) -> List[dict]:
        return self._current_offers.get(city_name, [])

    def execute_trade(self, city_name: str, offer_index: int) -> tuple[bool, str]:
        offers = self.get_offers(city_name)
        if not offers or offer_index < 0 or offer_index >= len(offers):
            return False, "Invalid offer."

        offer = offers[offer_index]
        res = offer['resource']
        gold_price = offer['price_gold'] * offer['amount']
        amount = offer['amount']

        if offer['type'] == 'BUY_FROM_CITY':
            if not self._rm.has_resource('gold', gold_price):
                return False, f"Not enough Gold! Need {gold_price}."
            
            self._rm.consume_resource('gold', gold_price)
            self._rm.add_resource(res, amount)
            return True, f"Bought {amount} {res} for {gold_price} Gold."

        elif offer['type'] == 'SELL_TO_CITY':
            if not self._rm.has_resource(res, amount):
                return False, f"Not enough {res}! Need {amount}."
            
            self._rm.consume_resource(res, amount)
            self._rm.add_resource('gold', gold_price)
            return True, f"Sold {amount} {res} for {gold_price} Gold."
            
        return False, "Unknown trade type."


class GameService:
    def __init__(self, rm, br, factory, constr, prod, research, trading):
        self._rm = rm
        self._br = br
        self._factory = factory
        self._constr = constr
        self._prod = prod
        self._research = research
        self._trading = trading
        
        self._building_configs = {
            'living': {
                'house': {'wood': 20, 'stone': 10},
                'park': {'wood': 10},
                'school': {'wood': 40, 'stone': 20},
                'library': {'wood': 20, 'stone': 50},
                'university': {'iron': 30, 'concrete': 20, 'energy': 10},
            },
            'industrial': {
                'carpenter': {'wood': 20, 'stone': 10},
                'metallurgy_plant': {'stone': 50, 'concrete': 20, 'energy': 20},
                'science_lab': {'stone': 30, 'iron': 10, 'planks': 20},
                'power_plant': {'stone': 50, 'iron': 20, 'concrete': 10},
                'concrete_factory': {'stone': 50, 'iron': 20, 'energy': 10},
                'warehouse': {'wood': 50, 'stone': 50},
                'port': {'wood': 100, 'stone': 50, 'planks': 50},
                'logistics_center': {'wood': 100, 'stone': 100, 'planks': 50, 'concrete': 20}
            },
            'infrastructure': {
                'water_tower': {'stone': 20, 'iron': 10, 'planks': 10},
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

    def list_resources(self) -> Dict[str, int]:
        return {r.name: r.amount for r in self._rm._repo.all()}

    def list_buildings(self) -> List[Building]:
        return self._br.all()

    def get_building_catalog(self) -> Dict[str, Dict[str, Dict[str, int]]]:
        return self._building_configs

    def list_research(self) -> Dict[str, dict]:
        return self._research.get_available_techs()

    def research_tech(self, tech_name: str) -> tuple[bool, str]:
        return self._research.research(tech_name)

    def build(self, kind: str) -> tuple[bool, str]:
        if not self._research.is_building_unlocked(kind):
            return False, "Technology locked! Research it first."

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

    def build_ship(self) -> tuple[bool, str]:
        ports = [b for b in self._br.all() if b.kind == 'port']
        if not ports:
            return False, "You need a PORT to build ships!"
        
        cost = {'planks': 50, 'steel': 10, 'energy': 20}
        
        for r, amount in cost.items():
            if not self._rm.has_resource(r, amount):
                return False, f"Not enough resources for Ship: {cost}"
        
        for r, amount in cost.items():
            self._rm.consume_resource(r, amount)

        self._rm.add_resource('ship', 1)
        return True, "Ship launched successfully! (+1 Fleet)"

    def upgrade(self, building_id: int) -> tuple[bool, str]:
        return self._constr.upgrade_building(building_id)

    def tick(self) -> None:
        self._prod.tick()

    def get_trading_cities(self) -> List[str]:
        centers = [b for b in self._br.all() if b.kind == 'logistics_center']
        if not centers:
            return []
        return self._trading.get_active_cities()

    def get_city_offers(self, city: str) -> List[dict]:
        return self._trading.get_offers(city)

    def trade(self, city: str, offer_idx: int) -> tuple[bool, str]:
        centers = [b for b in self._br.all() if b.kind == 'logistics_center']
        if not centers:
            return False, "Build Logistics Center first!"
        return self._trading.execute_trade(city, offer_idx)
