import curses

from life import GameOfLife
from ui import UI


class Console(UI):
    def __init__(self, life: GameOfLife) -> None:
        super().__init__(life)

    def draw_borders(self, screen) -> None:
        screen.border("|", "|", "-", "-", "+", "+", "+", "+")

    def draw_grid(self, screen) -> None:
        for i, row in enumerate(self.life.curr_generation):
            for j, cell in enumerate(row):
                if cell == 1:
                    fill = "+"
                else:
                    fill = " "
                screen.addch(i + 1, j + 1, fill)

    def run(self) -> None:
        screen = curses.initscr()
        running = True
        while running:
            self.draw_grid(screen)
            self.draw_borders(screen)
            self.life.step()
            screen.refresh()
            curses.napms(100)
        curses.endwin()


if __name__ == "__main__":
    life = GameOfLife((24, 80), max_generations=100)
    ui = Console(life)
    ui.run()
