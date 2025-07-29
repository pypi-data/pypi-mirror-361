import io
import json
import urllib.request

from cairo import ImageSurface, FORMAT_ARGB32, Context

import mercantile
import OsmRouteScreenLib.options as o
import OsmRouteScreenLib.utils as u

"""
Получение подложки для карты

Параметры:
----------
west: float
south: float
east: float
north: float
options: Options

Результата:
----------
ImageSurface
"""
def get_map_layout(west: float, south: float, east: float, north: float, options: o.Options) -> ImageSurface:
    tiles = list(mercantile.tiles(west, south, east, north, options.zoom))

    min_x = min([t.x for t in tiles])
    min_y = min([t.y for t in tiles])
    max_x = max([t.x for t in tiles])
    max_y = max([t.y for t in tiles])

    tile_size = (256, 256)
    # создаем пустое изображение в которое как мозайку будем вставлять тайлы
    # для начала просто попробуем отобразить все четыре тайла в строчку
    map_image = ImageSurface(
        FORMAT_ARGB32,
        tile_size[0] * (max_x - min_x + 1),
        tile_size[1] * (max_y - min_y + 1)
    )

    ctx = Context(map_image)

    for t in tiles:
        url = options.url_tile.format(
            zoom=t.z,
            x=t.x,
            y=t.y
        )

        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': options.user_agent
            }
        )

        response = urllib.request.urlopen(req)

        img = ImageSurface.create_from_png(io.BytesIO(response.read()))

        ctx.set_source_surface(
            img,
            (t.x - min_x) * tile_size[0],
            (t.y - min_y) * tile_size[0]
        )
        ctx.paint()

    # расчитываем коэффициенты
    bounds = {
        "left": min([mercantile.xy_bounds(t).left for t in tiles]),
        "right": max([mercantile.xy_bounds(t).right for t in tiles]),
        "bottom": min([mercantile.xy_bounds(t) .bottom for t in tiles]),
        "top": max([mercantile.xy_bounds(t).top for t in tiles]),
    }

    # коэффициенты скалирования по оси x и y
    kx = map_image.get_width() / (bounds['right'] - bounds['left'])
    ky = map_image.get_height() / (bounds['top'] - bounds['bottom'])

    # пересчитываем размеры по которым будем обрезать
    left_top = mercantile.xy(west, north)
    right_bottom = mercantile.xy(east, south)
    offset_left = (left_top[0] - bounds['left']) * kx
    offset_top = (bounds['top'] - left_top[1]) * ky
    offset_right = (bounds['right'] - right_bottom[0]) * kx
    offset_bottom = (right_bottom[1] - bounds['bottom']) * ky

    # обрезанное изображение
    map_image_clipped = ImageSurface(
        FORMAT_ARGB32,
        map_image.get_width() - int(offset_left + offset_right),
        map_image.get_height() - int(offset_top + offset_bottom),
    )

    # вставляем кусок исходного изображения
    ctx = Context(map_image_clipped)
    ctx.set_source_surface(map_image, -offset_left, -offset_top)
    ctx.paint()

    return map_image_clipped

"""
Получение координат на основе точек маршрута

Параметры:
----------
startPoint: str - координаты начала (широта-долгота)
endPoint: str - координаты конца маршрута (широта-долгота)
options: Options - дополнительные параметры

Результаты:
-----------
list[list[float]]
"""
def get_driving_coordinates(startPoint: str, endPoint: str, options: o.Options) -> list[list[float]] | None:
    try:
        url = options.url_routing.format(
            startPoint=startPoint,
            endPoint=endPoint
        )

        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': options.user_agent
            }
        )

        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        return data['routes'][0]['geometry']['coordinates']
    except Exception as e:
        print('err: ' + str(e))
        return None

"""
Построение маршрута по точкам

Параметры:
----------
startPoint: str - координаты начала (широта-долгота)
endPoint: str - координаты конца маршрута (широта-долгота)
options: Options - дополнительные параметры
markers: list[list[float]] - метки (широта-долгота)
"""
def get_image_route_by_points(startPoint: str, endPoint: str, options: o.Options, markers: list[list[float]] = []):
    if markers == None:
        markers = []

    driving_coordinates = get_driving_coordinates(startPoint, endPoint, options)

    return get_image_route_by_coordinates(driving_coordinates, options, markers)

"""
Построение маршрута по координатам

Параметры:
----------
driving_coordinates: list[list[float]] - координаты
options: Options - дополнительные параметры
markers: list[list[float]] - метки (широта-долгота)
"""
def get_image_route_by_coordinates(driving_coordinates: list[list[float]], options: o.Options, markers: list[list[float]] = []):
    if markers == None:
        markers = []

    if driving_coordinates != None:
        geodesic = u.geodesic(driving_coordinates)

        min_value = u.get_min_value(driving_coordinates + markers)
        max_value = u.get_max_value(driving_coordinates + markers)

        # корректировка значения с учётом padding
        diff_value = max_value[0] - min_value[0]
            
        k = diff_value * options.padding
        ROUND_VALUE = 6
        min_value = [round(x-k, ROUND_VALUE) for x in min_value]
        max_value = [round(x+k, ROUND_VALUE) for x in max_value]

        west = min_value[0]
        south = min_value[1]
        east = max_value[0]
        north = max_value[1]

        map_image = get_map_layout(west, south, east, north, options)

        # рассчитываем координаты углов в веб-меркаоторе
        leftTop = mercantile.xy(west, north)
        rightBottom = mercantile.xy(east, south)

        # расчитываем коэффициенты
        kx = map_image.get_width() / (rightBottom[0] - leftTop[0])
        ky = map_image.get_height() / (rightBottom[1] - leftTop[1])

        # а теперь порисуем
        context = Context(map_image)

        context.set_font_size(10)
        context.set_source_rgba(0, 0, 0, 1)

        if len(markers) > 0:
            for c in markers:
                # gps в web-mercator
                x, y = mercantile.xy(c[0], c[1])
                # переводим x, y в координаты изображения
                x = (x - leftTop[0]) * kx
                y = (y - leftTop[1]) * ky
                context.move_to(x, y)
                context.show_text(options.marker_text)

        idx = 0

        for c in driving_coordinates[:2]:
            # gps в web-mercator
            x, y = mercantile.xy(c[0], c[1])
            # переводим x, y в координаты изображения
            x = (x - leftTop[0]) * kx
            y = (y - leftTop[1]) * ky
            if idx == 0:
                context.move_to(x, y)

            context.line_to(x, y)
            idx+=1

        # заливаем наш путь
        context.set_source_rgba(0, 0, 1, 0.5)  # синий, полупрозрачный
        context.set_line_width(options.line_width)  # ширина 5 пикселей
        context.stroke()

        for c in driving_coordinates[1:-1]:
            # gps в web-mercator
            x, y = mercantile.xy(c[0], c[1])
            # переводим x, y в координаты изображения
            x = (x - leftTop[0]) * kx
            y = (y - leftTop[1]) * ky
            context.line_to(x, y)

        # заливаем наш путь
        context.set_source_rgba(1, 0, 0, 0.5)  # красный, полупрозрачный
        context.set_line_width(options.line_width)  # ширина 5 пикселей
        context.stroke()

        lastX = None
        lastY = None

        for c in driving_coordinates[-2:]:
            # gps в web-mercator
            x, y = mercantile.xy(c[0], c[1])
            # переводим x, y в координаты изображения
            x = (x - leftTop[0]) * kx
            y = (y - leftTop[1]) * ky
            lastX = x
            lastY = y
            context.line_to(x, y)

        # заливаем наш путь
        context.set_source_rgba(0, 2, 0, 0.5)  # зелёный, полупрозрачный
        context.set_line_width(options.line_width)  # ширина 5 пикселей
        context.stroke()

        if options.show_geodesic:
            context.move_to(lastX, lastY)
            context.set_font_size(8)
            context.set_source_rgba(0, 0, 0, 1)
            context.show_text('{geodesic}'.format(geodesic=round(geodesic, 2)))

        # сохраняем результат
        with open(options.output, "wb") as f:
            map_image.write_to_png(f)

        print('info: ' + options.output)
        return True

    print('[err]: driving coordinates is null')
    return False