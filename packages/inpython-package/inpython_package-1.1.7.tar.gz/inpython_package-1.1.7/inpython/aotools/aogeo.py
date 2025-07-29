"""Always-On geocoding module

Content :
=========
    distance_calculation : Calculate distance between 2 points or multiple points on earth
    offset_calculation : Calculate one or more GPS coordinates from an initial point based on a given azimuth and distance
"""

import geopy.distance
from latlon import *


def distance_calculation(origin, coordinates):
    """Calculate distance between 2 points or multiple points on earth

    Usage :
    =======
        origin (tuple) : The origin from which we want to calculate distances
        coordinates (list) : Points used to calculate the distance

    Example :
    =========
        distance_calculation((52.2296756, 21.0122287), [(52.406374, 16.9251681), (52.606374, 16.5251681)])
        Output = [279.35290160430094, 308.0962131498814]
    """
    try:
        return [geopy.distance.geodesic(
            origin, coordinate).km for coordinate in coordinates]
    except Exception as e:
        raise e


def offset_calculation(origin, azimuths_and_distances):
    """ Calculate one or more GPS coordinates from an initial point based on a given azimuth and distance

    Usage :
    =======
        origin (tuple) : The origin from which we want to calculate offsets
        azimuths_and_distances (list) : List of azimuths and distances

    Example :
    =========
        offset_calculation((52.2296756, 21.0122287), [(0, 279.35290160430094), (50, 308.0962131498814)])
        Output = 54.739690349825885,21.01222870000001|53.95616765233316,24.60854517315002
    """
    try:
        origin = LatLon(Latitude(origin[0]), Longitude(origin[1]))
        points = [origin.offset(azim, dist)
                  for azim, dist in azimuths_and_distances]
        points = ["{0},{1}".format(point.lat, point.lon) for point in points]
        return "|".join(points)
    except Exception as e:
        raise e


if __name__ == "__main__":
    print("Hello from aogeo")
    print(distance_calculation(
        (52.2296756, 21.0122287), [(52.406374, 16.9251681), (52.606374, 16.5251681)]))
    print(offset_calculation((52.2296756, 21.0122287), [
          (0, 279.35290160430094), (50, 308.0962131498814)]))
