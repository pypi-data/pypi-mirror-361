import OsmRouteScreenLib.methods as m
import OsmRouteScreenLib.options as o

"""
Получение скриншота маршрута

Параметры:
----------
startPoint: tuple - начальная точка (широта-долгота)
endPoint: tuple - конечная точка (широта-долгота)
markers: double[][] - промежуточные метки (широта-долгота)
options: {} - дополнительные опции
"""
def get_route_screen_by_points(startPoint: tuple[float], endPoint: tuple[float], options: o.Options, markers: list[list[float]] = []) -> bool:

    if options.valid():
        return m.get_image_route_by_points(
            '{latitude},{longitude}'.format(
                latitude=startPoint[0],
                longitude=startPoint[1]
            ),
            '{latitude},{longitude}'.format(
                latitude=endPoint[0],
                longitude=endPoint[1]
            ),
            options,
            markers
        )
    
    print('[err]: options not valid')
    return False

"""
Получение скриншота маршрута

Параметры:
----------
coordinates: double[][] - координаты маршрута (широта-долгота)
markers: double[][] - промежуточные метки (широта-долгота)
options: {} - дополнительные опции
"""
def get_route_screen_by_coordinates(coordinates: list[list[float]], options: o.Options, markers: list[list[float]] = []) -> bool:
    if options.valid():
        return m.get_image_route_by_coordinates(
            coordinates,
            options,
            markers
        )
    
    print('[err]: options not valid')
    return False