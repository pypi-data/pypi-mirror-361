class Options(object):
    url_tile = ''
    url_routing = ''
    padding = 0.1
    zoom = 16
    output = 'map_with_route_clipped.png'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    line_width = 5
    marker_text='x'
    show_geodesic=True

    def __init__(self, url_tile, url_routing, padding=0.1, zoom=16, output='map_with_route_clipped.png'):
        self.url_tile = url_tile
        self.url_routing = url_routing
        self.padding = padding
        self.zoom = zoom
        self.output = output
    
    def valid(self):
        if self.url_tile != '' and self.url_routing != '':
            return True
        else:
            return False
        

"""
Построить объект

Параметры:
----------
url_tile: string - шаблон для получения тайлов
url_routing: string - шаблон для получения координат маршрута
padding: double - отступ маршрута от краёв
zoom: int - зум
output: string - выходной результат

Результат:
----------
Опции
"""
def make_options(url_tile, url_routing, padding=0.1, zoom=16, output='map_with_route_clipped.png'):
    options = Options(url_tile, url_routing, padding, zoom, output)
    return options