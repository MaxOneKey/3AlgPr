from interfaces import IGameUI
from services import GameService


class ConsoleUI(IGameUI):
    def __init__(self, game_service: GameService):
        self._gs = game_service
        self._running = True

    def _print_header(self) -> None:
        print("=" * 50)
        print("CITY BUILDER DEMO — simple console UI")
        print("=" * 50)

    def _print_resources(self) -> None:
        print("Resources:")
        for name, amount in self._gs.list_resources().items():
            cap = self._gs._rm.get_capacity(name)
            print(f"  {name:8} : {amount:5} / {cap}")

    def _print_buildings(self) -> None:
        print("Buildings:")
        blds = self._gs.list_buildings()
        if not blds:
            print("  <no buildings>")
        for b in blds:
            print(" ", b)

    def _print_menu(self) -> None:
        print("\nOptions:")
        print("  1) Show resources")
        print("  2) Show buildings")
        print("  3) Build (type)")
        print("  4) Tick (advance production)")
        print("  5) Quick seed (add some resources)")
        print("  0) Exit")

    def main_loop(self) -> None:
        self._print_header()
        while self._running:
            self._print_menu()
            try:
                choice = input("Choose > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting...")
                return
            if choice == "1":
                self._print_resources()
            elif choice == "2":
                self._print_buildings()
            elif choice == "3":
                k = input("Enter building kind (farm, lumber_mill, quarry, mine, power_plant, warehouse, market, coal_mine, sand_quarry, concrete_factory, house, apartament): ").strip()
                ok, msg = self._gs.build(k)
                print(msg)
            elif choice == "4":
                print("Advancing 1 tick...")
                self._gs.tick()
                print("Tick complete.")
            elif choice == "5":
                self._gs._rm.add_resource('wood', 20)
                self._gs._rm.add_resource('stone', 20)
                self._gs._rm.add_resource('food', 10)
                self._gs._rm.add_resource('iron', 5)
                self._gs._rm.add_resource('people', 5)
                print("Added seed resources.")
            elif choice == "0":
                print("Goodbye.")
                self._running = False
            else:
                print("Unknown option.")