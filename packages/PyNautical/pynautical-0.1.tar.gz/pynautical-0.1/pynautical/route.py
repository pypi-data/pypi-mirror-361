import math

def _validate_lat_lon(lat1: float, lon1: float, lat2: float, lon2: float) -> None:
    """
    Validates that latitude and longitude values are within the expected ranges.

    Parameters:
        lat1 (float): Latitude of the starting point in degrees. Range: [-90, 90]
        lon1 (float): Longitude of the starting point in degrees. Range: [-360, 360)
        lat2 (float): Latitude of the destination point in degrees. Range: [-90, 90]
        lon2 (float): Longitude of the destination point in degrees. Range: [-360, 360)

    Raises:
        ValueError: If any latitude or longitude is out of range.
    """
    for lat in [lat1, lat2]:
        if not (-90 <= lat <= 90):
            raise ValueError(f"Latitude {lat} out of range. Must be between -90 and 90 degrees.")
    for lon in [lon1, lon2]:
        if not (-360 <= lon <= 360):
            raise ValueError(f"Longitude {lon} out of range. Must be between -360 and 360 degrees.")

def RL_Slerp(lat1: float, lon1: float, lat2: float, lon2: float, f: float) -> tuple:
    """
    Interpolates a point along the rhumb line (loxodrome) between two geographic coordinates.

    The interpolation is performed linearly in the Mercator projection space
    to preserve constant compass bearing between the two points.

    Parameters:
        lat1 (float): Latitude of the start point in degrees.
        lon1 (float): Longitude of the start point in degrees.
        lat2 (float): Latitude of the end point in degrees.
        lon2 (float): Longitude of the end point in degrees.
        f (float): Interpolation factor (0.0=start, 1.0=end, <0 or >1 for extrapolation).

    Returns:
        tuple: Interpolated (latitude, longitude) in degrees.
    """
    _validate_lat_lon(lat1, lon1, lat2, lon2)

    # Ensure exact output for start or end point
    if f == 0.0:
        return lat1, lon1
    elif f == 1.0:
        return lat2, lon2
    
    # Convert input coordinates from degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lon1_rad = math.radians(lon1)
    lon2_rad = math.radians(lon2)

    # Normalize longitude difference to shortest direction
    delta_lon = lon2_rad - lon1_rad
    if delta_lon > math.pi:
        delta_lon -= 2 * math.pi
    elif delta_lon < -math.pi:
        delta_lon += 2 * math.pi

    # Mercator projection of latitudes
    y1 = math.log(math.tan(math.pi / 4 + lat1_rad / 2))
    y2 = math.log(math.tan(math.pi / 4 + lat2_rad / 2))

    # Linear interpolation in Mercator space
    interp_y = y1 + (y2 - y1) * f
    interp_lon_rad = lon1_rad + delta_lon * f

    # Inverse Mercator to get latitude in radians
    interp_lat_rad = 2 * math.atan(math.exp(interp_y)) - math.pi / 2

    # Convert to degrees
    interp_lat = math.degrees(interp_lat_rad)
    interp_lon = math.degrees(interp_lon_rad)

    # Normalize longitude to 0–360 degrees if necessary
    if interp_lon < 0 and (lon1 > 180 or lon2 > 180):
        interp_lon += 360.0

    return interp_lat, interp_lon

def GC_Slerp(lat1: float, lon1: float, lat2: float, lon2: float, f: float) -> tuple:
    """
    Interpolates a point along the great circle path between two geographic coordinates
    using spherical linear interpolation (slerp).

    Parameters:
        lat1 (float): Latitude of the start point in degrees.
        lon1 (float): Longitude of the start point in degrees.
        lat2 (float): Latitude of the end point in degrees.
        lon2 (float): Longitude of the end point in degrees.
        f (float): Interpolation factor (0.0=start, 1.0=end, <0 or >1 for extrapolation).

    Returns:
        tuple: Interpolated (latitude, longitude) in degrees.
    """
    _validate_lat_lon(lat1, lon1, lat2, lon2)

    # Ensure exact output for start or end point
    if f == 0.0:
        return lat1, lon1
    elif f == 1.0:
        return lat2, lon2
    
    # Convert input coordinates from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Check if 0-360 degree format should be preserved in output
    use_360_format = lon1 > 180 or lon2 > 180

    # Compute the central angle between the two points using the haversine formula
    delta_lon = lon2_rad - lon1_rad
    sin_delta_lat = math.sin((lat2_rad - lat1_rad) / 2.0)
    sin_delta_lon = math.sin(delta_lon / 2.0)
    a = sin_delta_lat ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * sin_delta_lon ** 2
    central_angle = 2 * math.asin(math.sqrt(a))

    if central_angle == math.pi:
        raise ValueError("The points are antipodal (on opposite sides of the globe)")
    if math.isnan(central_angle):
        raise ValueError("Invalid coordinates for great circle interpolation")

    # Compute interpolation weights using spherical linear interpolation
    weight_start = math.sin((1 - f) * central_angle) / math.sin(central_angle)
    weight_end = math.sin(f * central_angle) / math.sin(central_angle)

    # Interpolate in 3D Cartesian coordinates on the unit sphere
    x = weight_start * math.cos(lat1_rad) * math.cos(lon1_rad) + \
        weight_end * math.cos(lat2_rad) * math.cos(lon2_rad)
    y = weight_start * math.cos(lat1_rad) * math.sin(lon1_rad) + \
        weight_end * math.cos(lat2_rad) * math.sin(lon2_rad)
    z = weight_start * math.sin(lat1_rad) + weight_end * math.sin(lat2_rad)

    # Convert Cartesian coordinates back to geographic latitude and longitude
    interp_lat_rad = math.atan2(z, math.sqrt(x ** 2 + y ** 2))
    interp_lon_rad = math.atan2(y, x)

    # Convert results from radians back to degrees
    interp_lat = math.degrees(interp_lat_rad)
    interp_lon = math.degrees(interp_lon_rad)

    # Normalize longitude to 0–360 degrees if required
    if interp_lon < 0 and use_360_format:
        interp_lon += 360.0

    return interp_lat, interp_lon