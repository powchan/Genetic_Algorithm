# 遗传算法
import random
import typing


class GeneticAlgorithm:
    population = []

    def __init__(self, init_size: int, precision: int, x1_range: list[int], x2_range: list[int],
                 evaluate: typing.Callable[[int, int], int]) -> None:
        for i in range(init_size):
            self.population.append([random.randrange(x1_range[0], x1_range[1], precision),
                                    random.randrange(x2_range[0], x2_range[1], precision)])
            self.evaluate = evaluate

    def run(self, depth: int, version: bool = False) -> int:
        value = []
        for i in range(depth):
            value.append(self.evaluate(self, self.population[i][0]), self.population[i][1])
            chromosome = random.choices(self.population, weights=value, k=len(self.population))
