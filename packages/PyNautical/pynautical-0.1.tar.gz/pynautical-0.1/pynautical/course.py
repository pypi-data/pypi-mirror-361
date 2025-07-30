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

def RL_COG(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the constant course (Course Over the Ground) from start point to end point
    along the Rhumb Line (a line of constant direction).

    Parameters:
        lat1 (float): Latitude of the starting point in degrees [-90, 90].
        lon1 (float): Longitude of the starting point in degrees [0, 360).
        lat2 (float): Latitude of the destination point in degrees [-90, 90].
        lon2 (float): Longitude of the destination point in degrees [0, 360).

    Returns:
        float: Constant course in degrees measured clockwise from true north (0° to 360°).
    """
    _validate_lat_lon(lat1, lon1, lat2, lon2)

    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)

    # Normalize delta longitude to shortest direction across 180° meridian
    if dlon > math.pi:
        dlon -= 2 * math.pi
    elif dlon < -math.pi:
        dlon += 2 * math.pi

    # Compute difference in meridional parts (Mercator projection y-coordinates)
    try:
        dphi = math.log(math.tan(math.pi / 4 + lat2_rad / 2) / math.tan(math.pi / 4 + lat1_rad / 2))
    except ZeroDivisionError:
        dphi = 0.0  # Handle special case near poles

    # Calculate rhumb line course angle
    course = (math.degrees(math.atan2(dlon, dphi)) + 360) % 360

    return course

def GC_COG(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the initial course (Course Over the Ground) from start point to end point
    along the Great Circle route (shortest path on a sphere).

    Parameters:
        lat1 (float): Latitude of the starting point in degrees [-90, 90].
        lon1 (float): Longitude of the starting point in degrees [0, 360).
        lat2 (float): Latitude of the destination point in degrees [-90, 90].
        lon2 (float): Longitude of the destination point in degrees [0, 360).

    Returns:
        float: Initial course in degrees measured clockwise from true north (0° to 360°).
    """
    _validate_lat_lon(lat1, lon1, lat2, lon2)

    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon_rad = math.radians(lon2 - lon1)

    # Compute course using spherical trigonometry
    x = math.sin(dlon_rad) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad)

    initial_course = (math.degrees(math.atan2(x, y)) + 360) % 360

    return initial_course