from interfaces import IGameUI
from services import GameService

class ConsoleUI(IGameUI):
    def __init__(self, game_service: GameService):
        self._gs = game_service
        self._running = True

    def _print_header(self) -> None:
        print("\n" + "=" * 60)
        print("ADVANCED CITY BUILDER — Trade, Logistics & Raids")
        print("=" * 60)

    def _print_resources(self) -> None:
        print("Resources:")
        res_list = self._gs.list_resources()
        i = 0
        for name, amount in res_list.items():
            cap = self._gs._rm.get_capacity(name)
            marker = "!" if amount == 0 and name in ['food', 'energy', 'water'] else " "
            if name == 'gold':
                print(f" [$] {name:15} : {amount:5} / {cap:<5}", end="")
            else:
                print(f" {marker} {name:15} : {amount:5} / {cap:<5}", end="")
            i += 1
            if i % 2 == 0: print() 
        print()

    def _print_buildings(self) -> None:
        print("Buildings:")
        blds = self._gs.list_buildings()
        if not blds:
            print("  <no buildings>")
        for b in blds:
            print(f"  ID:{b.id:<2} {b.summary()}")

    def _show_build_menu(self) -> None:
        catalog = self._gs.get_building_catalog()
        print("\n--- CONSTRUCTION MENU ---")
        for category, buildings in catalog.items():
            print(f"\n[{category.upper()}]")
            for b_name, costs in buildings.items():
                is_unlocked = self._gs._research.is_building_unlocked(b_name)
                if is_unlocked:
                    cost_str = ", ".join([f"{v} {k}" for k, v in costs.items()])
                    print(f"  > {b_name:18} | Cost: {cost_str}")
                else:
                    print(f"  X {b_name:18} | [LOCKED via Research]")
        print("-" * 60)

    def _show_research_menu(self) -> None:
        print("\n--- RESEARCH LABORATORY ---")
        rp = self._gs._rm.get_amount('research_points')
        print(f"Current Research Points (RP): {rp}")
        techs = self._gs.list_research()
        if not techs: print("  (No new technologies available)")
        for t_name, data in techs.items():
            cost = data['cost']
            desc = data['desc']
            unlocks = ", ".join(data['unlocks_buildings'])
            print(f"  > {t_name:18} (Cost: {cost} RP) | {desc}")
            print(f"      Unlocks: {unlocks}")
        print("-" * 60)

    def _show_trade_menu(self) -> None:
        cities = self._gs.get_trading_cities()
        if not cities:
            print("\n[!] Trading is unavailable.")
            print("    Requirements: 'trade_logistics' research AND 'logistics_center' building.")
            return

        print("\n--- GLOBAL MARKET (Logistics Center) ---")
        print("Your Gold:", self._gs._rm.get_amount('gold'))
        print("Available Cities:")
        for i, city in enumerate(cities):
            print(f"  {i+1}) {city}")
        
        print("0) Back")
        
        try:
            choice = input("Select City > ").strip()
            if choice == "0": return
            if choice.isdigit() and 1 <= int(choice) <= len(cities):
                city_name = cities[int(choice)-1]
                self._show_city_market(city_name)
            else:
                print("Invalid city.")
        except ValueError: pass

    def _show_city_market(self, city_name: str) -> None:
        while True:
            offers = self._gs.get_city_offers(city_name)
            print(f"\n--- MARKET: {city_name} ---")
            print("Your Gold:", self._gs._rm.get_amount('gold'))
            print(f"{'#':<3} {'Action':<15} {'Resource':<10} {'Amount':<8} {'Price (Total)':<15}")
            print("-" * 60)
            
            for i, off in enumerate(offers):
                if off['type'] == 'BUY_FROM_CITY':
                    action = "BUY (Import)"
                    price_str = f"-{off['price_gold']*off['amount']} Gold"
                else:
                    action = "SELL (Export)"
                    price_str = f"+{off['price_gold']*off['amount']} Gold"
                
                print(f"{i+1:<3} {action:<15} {off['resource']:<10} {off['amount']:<8} {price_str:<15}")

            print("0) Back")
            choice = input("Trade Action > ").strip()
            if choice == "0": break
            
            if choice.isdigit():
                idx = int(choice) - 1
                ok, msg = self._gs.trade(city_name, idx)
                print(f">> {msg}")
            else:
                print("Invalid option.")

    def _print_menu(self) -> None:
        print("-" * 60)
        print("1) Resources  2) Buildings  3) Build...")
        print("4) NEXT TICK  5) Cheat      6) UPGRADE Building")
        print("7) BUILD SHIP 8) RESEARCH   9) TRADE")
        print("10) RAID (Risk your fleet!)") 
        print("0) Exit")

    def main_loop(self) -> None:
        self._print_header()
        while self._running:
            self._print_menu()
            try:
                choice = input("Action > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting...")
                return
            
            if choice == "1": self._print_resources()
            elif choice == "2": self._print_buildings()
            elif choice == "3":
                self._show_build_menu()
                k = input("Type building name (or 'back'): ").strip().lower()
                if k != 'back':
                    ok, msg = self._gs.build(k)
                    print(f">> {msg}")
            elif choice == "4":
                print("Processing tick...")
                self._gs.tick()
                print("Done.")
                self._print_resources()
            elif choice == "5":
                rm = self._gs._rm
                for r in ['wood', 'stone', 'food', 'iron', 'energy', 'coal', 'sand', 'concrete', 'people', 'graduates', 'masters', 'planks', 'water', 'fish', 'steel', 'research_points', 'ship','gold']:
                    rm.add_resource(r, 100)
                print(">> Resources added.")
            elif choice == "6":
                bid = input("Enter Building ID: ").strip()
                if bid.isdigit():
                    ok, msg = self._gs.upgrade(int(bid))
                    print(f">> {msg}")
            elif choice == "7":
                ok, msg = self._gs.build_ship()
                print(f">> {msg}")
            elif choice == "8":
                self._show_research_menu()
                t = input("Type tech name to research (or 'back'): ").strip().lower()
                if t != 'back':
                    ok, msg = self._gs.research_tech(t)
                    print(f">> {msg}")
            elif choice == "9":
                self._show_trade_menu()
            elif choice == "10": 
                ok, msg = self._gs.raid()
                print(f">> {msg}")
            elif choice == "0":
                self._running = False
            else:
                print("Unknown option.")
