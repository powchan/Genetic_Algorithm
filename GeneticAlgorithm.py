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

    def encode(self, x1: float, x2: float) -> int:
        """
        对数值组x1,x2进行编码
        :return:以整数表示的编码值
        """
        x1_int = int((10 ** self.precision) * x1) - self.x1_range[0]
        x2_int = int((10 ** self.precision) * x2) - self.x2_range[0]
        x1_code = x1_int << self.x2_bit_length
        x2_code = x2_int & ((1 << self.x2_bit_length) - 1)
        return x1_code + x2_code

    def decode(self, code) -> list[float]:
        """
        将编码解码成数值组x1,x2
        :param code: 编码值
        :return: 数值组[x1,x2]
        """
        x1_int = code >> self.x2_bit_length
        x2_int = code & ((1 << self.x2_bit_length) - 1)
        return [x1_int / (10 ** self.precision), x2_int / (10 ** self.precision)]

    def __init__(self, init_size: int, precision: int, x1_range: list[float], x2_range: list[float],
                 mutations_probability: float, evaluate: typing.Callable[[int, int], int]) -> None:
        """
        初始化遗传种群类，采用加权轮盘式的自然选择
        :param init_size: 初始种群数量，要求为偶数。如传入奇数，会将其+1
        :param prec: 精度值，为整数，表示精确到小数点后第几位
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
            self.population.append([random.randint(x1_range[0], x1_range[1]) * (10 ** self.precision),
                                    random.randint(x2_range[0], x2_range[1]) * (10 ** self.precision)])
        self.evaluate = evaluate

    def run(self, depth: int, version: bool = False) -> list[int]:
        """
        运行遗传算法
        :param depth: 遗传算法的搜索深度
        :param version: 是否显示每代的具体信息，默认不显示
        :return: 一个列表，包含当下最大值的详细信息：[x1,x2,value]
        """
        for i in range(depth):
            value = [self.evaluate(self.population[j][0], self.population[j][1])
                     for j in range(len(self.population))]
            if version:
                print(f"depth = {i}")
                for k in range(len(self.population)):
                    print(f"x1 = {round(self.population[k][0], self.precision)}, "
                          f"x2 = {round(self.population[k][1], self.precision)},\t"
                          f"value = {value[k]}")
                print("\n")
            chromosome = random.choices(self.population, weights=value, k=len(self.population))
            codes = [self.encode(c[0], c[1]) for c in chromosome]
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
            self.population = [self.decode(code) for code in sons_codes]

        max_index, max_value = max(enumerate([self.evaluate(p[0], p[1]) for p in self.population]))
        return [round(self.population[max_index][0], self.precision)
            , round(self.population[max_index][1], self.precision)
            , max_value]
