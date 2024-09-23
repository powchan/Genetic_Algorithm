# 遗传算法
import random
import typing


class GeneticAlgorithm:
    population = []
    precision = 1
    x1_bit_length = 0
    x2_bit_length = 0

    def __init__(self, init_size: int, precision: int, x1_range: list[int], x2_range: list[int],
                 evaluate: typing.Callable[[int, int], int]) -> None:
        """
        :param init_size: 初始种群数量，要求为偶数。如传入奇数，会将其+1
        :param precision: 精度值，必须为10**n或1en的格式且必须小于1
        :param x1_range:  [0]标识x1的最小值，[1]标识x1的最大值
        :param x2_range: [0]标识x2的最小值，[1]标识x2的最大值
        :param evaluate: 评估种群优劣的评估函数
        """
        if init_size % 2 != 0:
            init_size = init_size + 1
        for i in range(init_size):
            self.population.append([random.randrange(x1_range[0], x1_range[1], precision),
                                    random.randrange(x2_range[0], x2_range[1], precision)])
            self.evaluate = evaluate
            x1_bit_length = max(abs(x1_range[0]).bit_length(), abs(x1_range[1]).bit_length())
            x2_bit_length = max(abs(x2_range[0]).bit_length(), abs(x2_range[1]).bit_length())
            self.precision = precision

    def run(self, depth: int, version: bool = False) -> list[int]:
        """
        :param depth: 遗传算法的搜索深度
        :param version: 是否显示每代的具体信息，默认不显示
        :return: 一个列表，包含当下最大值的详细信息：[x1,x2,value]
        """
        for i in range(depth):
            value = [self.evaluate(self, self.population[j][0], self.population[j][1])
                     for j in range(len(self.population))]
            if version:
                print(f"depth = {depth}\n")
                for k in range(len(self.population)):
                    print(f"x1 = {self.population[k][0]}, x2 = {self.population[k][1]},\t"
                          f"value = {value[k]}\n")
                print("\n")
            chromosome = random.choices(self.population, weights=value, k=len(self.population))
            chromosome = [i / self.precision for i in chromosome]
            codes = [(i[0] << self.x2_bit_length) | i[1] for i in chromosome]
            sons_codes = []
            for j in range(0, len(codes), 2):
                father = codes[j]
                mother = codes[j + 1]
                change_digit = random.randint(0, self.x1_bit_length + self.x2_bit_length)
                son1 = ((father >> change_digit) << change_digit) | (mother & ((1 << change_digit) - 1))
                son2 = ((mother >> change_digit) << change_digit) | (father & ((1 << change_digit) - 1))
                sons_codes.append(son1)
                sons_codes.append(son2)
            self.population = []
            for code in sons_codes:
                son = [code >> self.x2_bit_length, code & ((1 << self.x2_bit_length) - 1)]
                self.population.append(son)

        max_index, max_value = max(enumerate([self.evaluate(p) for p in self.population]))
        return [self.population[max_index][0], self.population[max_index][1], max_value]
