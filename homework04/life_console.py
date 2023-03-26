import curses

from life import GameOfLife
from ui import UI


class Console(UI):
    def __init__(self, life: GameOfLife) -> None:
        super().__init__(life)

    def draw_borders(self, screen) -> None:
        """Отобразить рамку."""
        screen.border("|", "|", "-", "-", "+", "+", "+", "+")

    def draw_grid(self, screen) -> None:
        """Отобразить состояние клеток."""
        height = len(self.life.curr_generation)
        length = len(self.life.curr_generation[0])
        for i in range(height):
            for j in range(length):
                if self.life.curr_generation[i][j]:
                    screen.addstr(j + 1, i + 1, "*")
                else:
                    screen.addstr(j + 1, i + 1, " ")

    def run(self) -> None:
        screen = curses.initscr()
        curses.resizeterm(self.life.rows + 2, self.life.cols + 2)

        while self.life.is_changing and self.life.is_max_generations_exceeded == False:
            self.life.step()
            self.draw_borders(screen)
            self.draw_grid(screen)
            screen.refresh()
            curses.napms(400)
        curses.endwin()


"""if __name__ == "__main__":
    game = GameOfLife(max_generations=200)
    game_console = Console(game)
    game_console.run()"""
