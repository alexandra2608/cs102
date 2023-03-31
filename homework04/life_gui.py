import pygame
from life import GameOfLife
from ui import UI


class GUI(UI):
    def __init__(self, life: GameOfLife, cell_size: int = 10, speed: int = 10) -> None:
        super().__init__(life)
        self.cell_size = cell_size

        self.width = self.life.rows * self.cell_size

        self.height = self.life.cols * self.cell_size

        # Устанавливаем размер окна

        self.screen_size = self.width, self.height

        # Создание нового окна

        self.screen = pygame.display.set_mode(self.screen_size)

        # Вычисляем количество ячеек по вертикали и горизонтали

        self.cell_width = self.width // self.cell_size

        self.cell_height = self.height // self.cell_size

        # Скорость протекания игры

        self.speed = speed

    def draw_lines(self) -> None:
        # Copy from previous assignment
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (0, y), (self.width, y))

    def draw_grid(self) -> None:
        # Copy from previous assignment
        y = 0
        for row in self.life.curr_generation:
            x = 0
            for cell in row:
                color = pygame.Color("green") if cell else pygame.Color("white")
                pygame.draw.rect(self.screen, color, (y, x, self.cell_size, self.cell_size))
                x += self.cell_size
            y += self.cell_size

    def run(self) -> None:
        # Copy from previous assignment
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption("Game of Life")

        self.screen.fill(pygame.Color("white"))
        self.grid = self.life.curr_generation
        running = True
        pause = False

        while running and self.life.is_changing and not self.life.is_max_generations_exceeded:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        pause = not pause
                elif pause:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        row = pygame.mouse.get_pos()[0] // self.cell_size
                        col = pygame.mouse.get_pos()[1] // self.cell_size
                        self.grid[row][col] = 0 if self.grid[row][col] == 1 else 1
            self.draw_lines()
            self.draw_grid()
            self.draw_lines()
            if not pause:
                self.life.step()
            self.grid = self.life.curr_generation
            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()


if __name__ == "__main__":
    gui = GUI(GameOfLife((40, 50), max_generations=50))
    gui.run()
