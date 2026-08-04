import utm

def geo_to_utm(lat, lon):
    """Converts lat/long in UTM coordinates

        Args : 
            lat and long in °
    """
    conversion_result = utm.from_latlon(lat, lon)
    utm_easting = conversion_result[0]
    utm_northing = conversion_result[1]

    return utm_easting, utm_northing