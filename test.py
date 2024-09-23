from GeneticAlgorithm import GeneticAlgorithm
from math import *


def evaluate(x1, x2):
    return 21.5 + x1 * sin(4 * pi * x1) + x2 * sin(20 * pi * x2)


test = GeneticAlgorithm(10, 1e-6, [-3.0, 12.1], [4.1, 5.8], evaluate)
print("result = ", test.run(1000, True))
