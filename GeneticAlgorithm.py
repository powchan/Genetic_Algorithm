# 遗传算法
import random
import typing


class GeneticAlgorithm:
    population = []
    precision = 1
    x1_bit_length = 0
    x2_bit_length = 0
    x1_range = []
    x2_range = []

    def __encode(self, x1: float, x2: float) -> int:
        """
        对数值组x1,x2进行编码
        :return:以整数表示的编码值
        """
        x1_iv = x1 - self.x1_range[0]
        x2_iv = x2 - self.x2_range[0]
        x1_code = int(x1_iv) << self.x2_bit_length
        x2_code = int(x2_iv) & ((1 << self.x2_bit_length) - 1)
        return x1_code + x2_code

    def __decode(self, code) -> list[float]:
        """
        将编码解码成数值组x1,x2
        :param code: 编码值
        :return: 数值组[x1,x2]
        """
        x1 = (code >> self.x2_bit_length) + self.x1_range[0]
        x2 = (code & ((1 << self.x2_bit_length) - 1)) + self.x2_range[0]
        return [x1, x2]

    def __init__(self, init_size: int, precision: int, x1_range: list[float], x2_range: list[float],
                 mutations_probability: float, evaluate: typing.Callable[[float, float], float]) -> None:
        """
        初始化遗传种群类，采用加权轮盘式的自然选择
        :param init_size: 初始种群数量，要求为偶数。如传入奇数，会将其+1
        :param precision: 精度值，为整数，表示精确到小数点后第几位
        :param x1_range:  [0]标识x1的最小值，[1]标识x1的最大值
        :param x2_range: [0]标识x2的最小值，[1]标识x2的最大值
        :param mutations_probability: 突变的概率，应该为0~1之间的小数
        :param evaluate: 评估种群优劣的评估函数
        """
        if init_size % 2 != 0:
            init_size = init_size + 1
        self.precision = precision

        self.mutations_probability = mutations_probability
        x1_range = [int(i * (10 ** self.precision)) for i in x1_range]
        x2_range = [int(i * (10 ** self.precision)) for i in x2_range]
        self.x1_range = x1_range
        self.x2_range = x2_range

        self.x1_bit_length = abs(x1_range[0] - x1_range[1]).bit_length()
        self.x2_bit_length = abs(x2_range[0] - x2_range[1]).bit_length()

        for i in range(init_size):
            self.population.append([random.randint(x1_range[0], x1_range[1]),
                                    random.randint(x2_range[0], x2_range[1])])
        self.evaluate = evaluate

    def run(self, depth: int, version: bool = False) -> list[int]:
        """
        运行遗传算法
        :param depth: 遗传算法的搜索深度
        :param version: 是否显示每代的具体信息，默认不显示
        :return: 一个列表，包含当下最大值的详细信息：[x1,x2,value]
        """
        for i in range(depth):
            value = [self.evaluate(self.population[j][0] / (10 ** self.precision),
                                   self.population[j][1] / (10 ** self.precision))
                     for j in range(len(self.population))]
            if min(value) < 0:
                value = [(0 - min(value)) + v for v in value]
                min_value = min(value)
            else:
                min_value = 0

            if version:
                print(f"depth = {i}")
                for k in range(len(self.population)):
                    print(f"x1 = {round(self.population[k][0] / (10 ** self.precision), self.precision)}, "
                          f"x2 = {round(self.population[k][1] / (10 ** self.precision), self.precision)},\t"
                          f"value = {value[k] + min_value}")
                print("\n")
            chromosome = random.choices(self.population, weights=value, k=len(self.population))
            codes = [self.__encode(c[0], c[1]) for c in chromosome]
            sons_codes = []
            for j in range(0, len(codes), 2):
                father = codes[j]
                mother = codes[j + 1]
                change_digit = random.randint(0, self.x1_bit_length + self.x2_bit_length)
                son1 = ((father >> change_digit) << change_digit) | (mother & ((1 << change_digit) - 1))
                son2 = ((mother >> change_digit) << change_digit) | (father & ((1 << change_digit) - 1))
                if random.random() < self.mutations_probability:
                    mutations_digit = random.randint(0, son1.bit_length() - 1)
                    son1 = son1 ^ (1 << mutations_digit)
                if random.random() < self.mutations_probability:
                    mutations_digit = random.randint(0, son2.bit_length() - 1)
                    son2 = son2 ^ (1 << mutations_digit)
                sons_codes.append(son1)
                sons_codes.append(son2)
            self.population = [self.__decode(code) for code in sons_codes]
            for p in self.population:
                if p[0] > self.x1_range[1]:
                    p[0] = self.x1_range[1] - random.randint(0, 10 ** self.precision)
                if p[1] > self.x2_range[1]:
                    p[1] = self.x2_range[1] - random.randint(0, 10 ** self.precision)
        if version:
            print(f"depth = {depth}")
            for k in range(len(self.population)):
                v = self.evaluate(self.population[k][0] / (10 ** self.precision),
                                  self.population[k][1] / (10 ** self.precision))
                print(f"x1 = {round(self.population[k][0] / (10 ** self.precision), self.precision)}, "
                      f"x2 = {round(self.population[k][1] / (10 ** self.precision), self.precision)},\t"
                      f"value = {v}")
        max_index, max_value = max(
            enumerate([self.evaluate(p[0] / (10 ** self.precision), p[1] / (10 ** self.precision))
                       for p in self.population]), key=lambda x: x[1])
        return [round(self.population[max_index][0] / (10 ** self.precision), self.precision),
                round(self.population[max_index][1] / (10 ** self.precision), self.precision),
                max_value]

    def tournament_selection(self, k=3):
        # 进行k次锦标赛选择，返回被选中的个体
        selected = []
        for i in range(len(self.population)):
            tournament = random.sample(self.population, k)
            tournament_fitness = [self.evaluate(ind[0], ind[1]) for ind in tournament]
            winner = tournament[tournament_fitness.index(max(tournament_fitness))]
            selected.append(winner)
        return selected