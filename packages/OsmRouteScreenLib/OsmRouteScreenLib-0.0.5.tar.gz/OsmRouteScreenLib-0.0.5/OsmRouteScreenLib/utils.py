import geopy.distance

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

"""
Вывод дистанции маршрута

Параметры:
----------
coordinates: list[list[float]] - координаты
"""
def geodesic(coordinates: list[list[float]]):
    
    idx = 0
    lastValue = None
    arrayGeodesic = []

    for c in coordinates:
        if idx > 0:
            arrayGeodesic.append(geopy.distance.geodesic(lastValue, c).km)
        
        lastValue = c
        idx+=1

    return sum([x for x in arrayGeodesic])