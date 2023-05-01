import logging
from shapely.geometry import Polygon, Point
from math import radians, degrees, sin, cos, atan2, sqrt, pi


def create_geofence(filename):
    """
    Attempt to load in a geofence file and create a Polygon.

    Returns a function point which accepts a latitude and longitude, and returns True/False depending on whether
    the supplied lat/lon is within the geofence area.

    """

    _f = open(filename, 'r')

    coords = []

    for line in _f:
        if line.startswith('#'):
            continue

        try:
            _fields = line.split(',')
            _lat = float(_fields[0])
            _lon = float(_fields[1])

            if _lon > 180.0:
                _lon = _lon - 360.0

            coords.append( (_lat, _lon) )

        except Exception as e:
            logging.error(f"Geofence - error parsing line in file: {line}")
    
    logging.debug(f"Geofence - Coordinates: {str(coords)}")

    # Create the shapely polygon from the coordinates.
    _polygon = Polygon(coords)

    # Create the function which we will return for use in comparisons
    def within_bounds(lat, lon):
        _point = Point(lat, lon)

        return _polygon.contains(_point)
    
    return within_bounds


def position_info(listener, balloon):
    """
    Calculate and return information from 2 (lat, lon, alt) tuples

    Copyright 2012 (C) Daniel Richman; GNU GPL 3

    Returns a dict with:

     - angle at centre
     - great circle distance
     - distance in a straight line
     - bearing (azimuth or initial course)
     - elevation (altitude)

    Input and output latitudes, longitudes, angles, bearings and elevations are
    in degrees, and input altitudes and output distances are in meters.
    """

    # Earth:
    # radius = 6371000.0
    radius = 6364963.0  # Optimized for Australia :-)

    (lat1, lon1, alt1) = listener
    (lat2, lon2, alt2) = balloon

    lat1 = radians(lat1)
    lat2 = radians(lat2)
    lon1 = radians(lon1)
    lon2 = radians(lon2)

    # Calculate the bearing, the angle at the centre, and the great circle
    # distance using Vincenty's_formulae with f = 0 (a sphere). See
    # http://en.wikipedia.org/wiki/Great_circle_distance#Formulas and
    # http://en.wikipedia.org/wiki/Great-circle_navigation and
    # http://en.wikipedia.org/wiki/Vincenty%27s_formulae
    d_lon = lon2 - lon1
    sa = cos(lat2) * sin(d_lon)
    sb = (cos(lat1) * sin(lat2)) - (sin(lat1) * cos(lat2) * cos(d_lon))
    bearing = atan2(sa, sb)
    aa = sqrt((sa ** 2) + (sb ** 2))
    ab = (sin(lat1) * sin(lat2)) + (cos(lat1) * cos(lat2) * cos(d_lon))
    angle_at_centre = atan2(aa, ab)
    great_circle_distance = angle_at_centre * radius

    # Armed with the angle at the centre, calculating the remaining items
    # is a simple 2D triangley circley problem:

    # Use the triangle with sides (r + alt1), (r + alt2), distance in a
    # straight line. The angle between (r + alt1) and (r + alt2) is the
    # angle at the centre. The angle between distance in a straight line and
    # (r + alt1) is the elevation plus pi/2.

    # Use sum of angle in a triangle to express the third angle in terms
    # of the other two. Use sine rule on sides (r + alt1) and (r + alt2),
    # expand with compound angle formulae and solve for tan elevation by
    # dividing both sides by cos elevation
    ta = radius + alt1
    tb = radius + alt2
    ea = (cos(angle_at_centre) * tb) - ta
    eb = sin(angle_at_centre) * tb
    elevation = atan2(ea, eb)

    # Use cosine rule to find unknown side.
    distance = sqrt((ta ** 2) + (tb ** 2) - 2 * tb * ta * cos(angle_at_centre))

    # Give a bearing in range 0 <= b < 2pi
    if bearing < 0:
        bearing += 2 * pi

    return {
        "listener": listener,
        "balloon": balloon,
        "listener_radians": (lat1, lon1, alt1),
        "balloon_radians": (lat2, lon2, alt2),
        "angle_at_centre": degrees(angle_at_centre),
        "angle_at_centre_radians": angle_at_centre,
        "bearing": degrees(bearing),
        "bearing_radians": bearing,
        "great_circle_distance": great_circle_distance,
        "straight_distance": distance,
        "elevation": degrees(elevation),
        "elevation_radians": elevation,
    }


def create_radius_filter(centre_lat, centre_lon, radius_km):
    """
    Create a radius-based position filter.

    Returns a function which accepts lat,lon and returns True/False
    if the supplied position is within the radius.
    """

    def within_bounds(lat, lon):
        _pos1 = (centre_lat, centre_lon, 0)
        _pos2 = (lat, lon, 0)
        _pos_info = position_info(_pos1, _pos2)

        _range = _pos_info['great_circle_distance']

        if _range < (radius_km*1000):
            return True
        else:
            return False

    return within_bounds





if __name__ == "__main__":

    import sys

    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG,
    )

    _filename = sys.argv[1]

    position_filter = create_geofence(_filename)

    test_coords = [ [-34.0, 138.0], [0.0, 0.0], [40, 138.0], [52.7795, -167.62716666666665] ]
    for coord in test_coords:
        print(f"Coord {coord[0]}, {coord[1]} within geofence: {position_filter(coord[0], coord[1])}")

    
    radius_filter = create_radius_filter(-34.0, 138.0, 1000.0)


    test_coords = [ [-34.0, 138.0], [-34.1, 138.1], [0.0, 0.0], [40, 138.0] ]
    for coord in test_coords:
        print(f"Coord {coord[0]}, {coord[1]} within radius: {radius_filter(coord[0], coord[1])}")
