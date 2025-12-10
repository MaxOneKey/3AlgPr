from container import build_container
from ui import ConsoleUI


def main():
    c = build_container()
    gs = c.resolve('game_service')
    ui = ConsoleUI(gs)
    ui.main_loop()


if __name__ == '__main__':
    main()
