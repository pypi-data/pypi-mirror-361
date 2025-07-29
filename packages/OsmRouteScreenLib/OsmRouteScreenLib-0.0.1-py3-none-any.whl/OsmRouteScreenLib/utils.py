"""
Получение минимального значения

Параметры:
----------
coordinates: list[list[float]] - координаты

Результат:
----------
list[float]
"""
def get_min_value(coordinates: list[list[float]]):
    return [min([x[0] for x in coordinates]), min([x[1] for x in coordinates])]

"""
Получение максимального значения

Параметры:
----------
coordinates: list[list[float]] - координаты

Результат:
----------
list[float]
"""
def get_max_value(coordinates: list[list[float]]):
    return [max([x[0] for x in coordinates]), max([x[1] for x in coordinates])]