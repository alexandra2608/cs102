import pathlib
import random
import typing as tp

import pygame
from pygame.locals import *

Cell = tp.Tuple[int, int]
Cells = tp.List[int]
Grid = tp.List[Cells]


class GameOfLife:
    def __init__(
        self,
        size: tp.Tuple[int, int],
        randomize: bool = True,
        max_generations: tp.Optional[float] = float("inf"),
    ) -> None:
        # Размер клеточного поля
        self.rows, self.cols = size
        # Предыдущее поколение клеток
        self.prev_generation = self.create_grid()
        # Текущее поколение клеток
        self.curr_generation = self.create_grid(randomize=randomize)
        # Максимальное число поколений
        self.max_generations = max_generations
        # Текущее число поколений
        self.generations = 1

    def create_grid(self, randomize: bool = False) -> Grid:
        # Copy from previous assignment
        field = [
            [random.randint(0, 1) if randomize else 0 for j in range(self.cols)] for i in range(self.rows)
        ]

        return field

    def get_neighbours(self, cell: Cell) -> Cells:
        # Copy from previous assignment
        nei_list = []
        y, x = cell[0], cell[1]
        if 0 < y:
            nei_list.append(self.curr_generation[y - 1][x])
        if y < self.rows - 1:
            nei_list.append(self.curr_generation[y + 1][x])
        if x > 0:
            nei_list.append(self.curr_generation[y][x - 1])
        if x < self.cols - 1:
            nei_list.append(self.curr_generation[y][x + 1])
        if y > 0 and x > 0:
            nei_list.append(self.curr_generation[y - 1][x - 1])
        if y > 0 and x < self.cols - 1:
            nei_list.append(self.curr_generation[y - 1][x + 1])
        if y < self.rows - 1 and x > 0:
            nei_list.append(self.curr_generation[y + 1][x - 1])
        if y < self.rows - 1 and x < self.cols - 1:
            nei_list.append(self.curr_generation[y + 1][x + 1])
        return nei_list

    def get_next_generation(self) -> Grid:
        # Copy from previous assignment
        buffer = self.create_grid(randomize=False)
        field = self.curr_generation
        for y in range(self.rows):
            for x in range(self.cols):
                c = field[y][x]
                cc = (y, x)
                nei = self.get_neighbours(cc)
                nei_len = nei.count(1)
                if c == 0:
                    buffer[y][x] = 1 if nei_len == 3 else 0
                else:
                    buffer[y][x] = 1 if nei_len in (2, 3) else 0
        field = buffer
        # assert isinstance(field, object)
        return field

    def step(self) -> None:
        """
        Выполнить один шаг игры.
        """
        self.prev_generation = self.curr_generation
        getting_next_gen = self.get_next_generation()
        self.curr_generation = getting_next_gen

        self.generations += 1

    @property
    def is_max_generations_exceeded(self) -> bool:
        """
        Не превысило ли текущее число поколений максимально допустимое.
        """
        if self.max_generations and self.generations >= self.max_generations:
            return True
        return False

    @property
    def is_changing(self) -> bool:
        """
        Изменилось ли состояние клеток с предыдущего шага.
        """
        buffer = self.prev_generation
        field = self.curr_generation
        if field == buffer:
            return False
        else:
            return True

    @staticmethod
    def from_file(filename: pathlib.Path) -> "GameOfLife":
        """
        Прочитать состояние клеток из указанного файла.
        """
        grid = []
        with open(filename, "r") as f:
            grid = [[int(j) for j in i.strip()] for i in f]

        life = GameOfLife((len(grid), len(grid[0])))
        life.curr_generation = grid
        return life

    def save(self, filename: pathlib.Path) -> None:
        """
        Сохранить текущее состояние клеток в указанный файл.
        """
        with open(filename, "w+", encoding="utf-8") as f:
            for i in self.curr_generation:
                f.write("".join(map(str, i)) + "\n")
