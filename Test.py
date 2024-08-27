import numpy as np


def roulette_wheel_selection(probabilities, n):
    # 累积概率分布
    cumulative_probabilities = np.cumsum(probabilities)

    # 生成 n 个随机数
    random_numbers = np.random.rand(n)

    # 根据累积概率分布确定对应的下标
    indices = np.searchsorted(cumulative_probabilities, random_numbers)

    return indices


# 给定的概率值列表
probabilities = [0.50, 0.20, 0.15, 0.15]

# 将概率值归一化
probabilities = np.array(probabilities) / np.sum(probabilities)

# 设置循环次数 n
n = 100

# 获取生成的下标
indices = roulette_wheel_selection(probabilities, n)
print(indices)
# 输出每个下标出现的次数
counts = np.bincount(indices)
print(counts)
