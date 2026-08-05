import utm
from PySide6.QtCore import QPointF

def geo_to_utm(lat, lon):
    conversion_result = utm.from_latlon(lat, lon)
    utm_easting = conversion_result[0]
    utm_northing = conversion_result[1]

    return utm_easting, utm_northing

def utm_to_geo(x, y, zoneNumber, zoneLetter):
    return utm.to_latlon(x, y, zoneNumber, zoneLetter)

def get_geo_zone(lat, lon):
    conversion_result = utm.from_latlon(lat, lon)
    zoneNumber = conversion_result[2]
    zoneLetter = conversion_result[3]

    return zoneNumber, zoneLetter

def utm_to_screen(pos, zoom, offset, center, screen_size):
    width = screen_size[0]
    height = screen_size[1]

    x = int(width/2 + (pos[0] - center[0]) * zoom + offset.x())
    y = int(height/2 - (pos[1] - center[1]) * zoom + offset.y())

    return x, y 

def screen_to_utm(pos, zoom, offset, center, screen_size):
    width = screen_size[0]
    height = screen_size[1]

    x = center[0] + (pos.x() - width/2 - offset.x()) / zoom
    y = center[1] - (pos.y() - height/2 - offset.y()) / zoom

    return QPointF(x,y)

def geo_to_screen(geo_pos, zoom, offset, center, screen_size):
    utm_pos = geo_to_utm(geo_pos[0], geo_pos[1])
    screen_pos = utm_to_screen(utm_pos, zoom, offset, center, screen_size)
    return QPointF(screen_pos[0], screen_pos[1])

def screen_to_geo(pos, zoom, offset, center, screen_size, zoneNumber, zoneLetter):
    utm_pos = screen_to_utm(pos, zoom, offset, center, screen_size)
    geo_pos = utm_to_geo(utm_pos.x(), utm_pos.y(), zoneNumber, zoneLetter)
    return geo_pos