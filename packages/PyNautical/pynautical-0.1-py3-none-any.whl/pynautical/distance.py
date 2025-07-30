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

def RL_DIST(lat1: float, lon1: float, lat2: float, lon2: float, radius_km: float = 6371.0) -> float:
    """
    Calculates the Rhumbline (loxodrome) distance between two points on a spherical Earth.

    Parameters:
        lat1 (float): Latitude of point A in degrees.
        lon1 (float): Longitude of point A in degrees.
        lat2 (float): Latitude of point B in degrees.
        lon2 (float): Longitude of point B in degrees.
        radius_km (float, optional): Radius of the spherical Earth in kilometers. Default is 6371.0.

    Returns:
        float: Rhumbline distance in nautical miles.
    """
    _validate_lat_lon(lat1, lon1, lat2, lon2)

    # Convert coordinates to radians
    lat1_rad: float = math.radians(lat1)
    lon1_rad: float = math.radians(lon1)
    lat2_rad: float = math.radians(lat2)
    lon2_rad: float = math.radians(lon2)

    # Latitude and longitude difference
    delta_lat: float = lat2_rad - lat1_rad
    delta_lon: float = lon2_rad - lon1_rad

    # Compute Mercator projection of latitudes directly
    tan_lat1: float = math.tan(math.pi / 4 + lat1_rad / 2)
    tan_lat2: float = math.tan(math.pi / 4 + lat2_rad / 2)

    # Projected latitude difference (used in Rhumbline formula)
    delta_proj: float = math.log(tan_lat2 / tan_lat1)

    # q accounts for latitude convergence at poles
    q: float = delta_lat / delta_proj if abs(delta_proj) > 1e-12 else math.cos(lat1_rad)

    # Adjust for crossing the antimeridian
    if abs(delta_lon) > math.pi:
        delta_lon = delta_lon - math.copysign(2 * math.pi, delta_lon)

    # Compute distance in kilometers (Earth radius ~ 6371 km), then convert to nautical miles
    distance_km: float = math.sqrt(delta_lat**2 + (q * delta_lon)**2) * radius_km
    return distance_km / 1.852  # meters to nautical miles

def RL_DIST_WGS84(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the Rhumbline distance between two points on the WGS84 ellipsoid.

    Parameters:
        lat1 (float): Latitude of point A in degrees.
        lon1 (float): Longitude of point A in degrees.
        lat2 (float): Latitude of point B in degrees.
        lon2 (float): Longitude of point B in degrees.

    Returns:
        float: Rhumbline distance in nautical miles.
    """
    _validate_lat_lon(lat1, lon1, lat2, lon2)

    a: float = 6378137.0  # WGS84 semi-major axis
    f: float = 1 / 298.257223563  # flattening
    e2: float = 2 * f - f ** 2  # eccentricity squared

    # Convert degrees to radians
    lat1_rad: float = math.radians(lat1)
    lon1_rad: float = math.radians(lon1)
    lat2_rad: float = math.radians(lat2)
    lon2_rad: float = math.radians(lon2)

    # Latitude and longitude difference
    delta_lat: float = lat2_rad - lat1_rad
    delta_lon: float = lon2_rad - lon1_rad
    mean_lat: float = (lat1_rad + lat2_rad) / 2

    # Radius of curvature in the prime vertical
    Rn: float = a / math.sqrt(1 - e2 * math.sin(mean_lat) ** 2)

    # Mercator projection of latitudes
    tan_lat1: float = math.tan(math.pi / 4 + lat1_rad / 2)
    tan_lat2: float = math.tan(math.pi / 4 + lat2_rad / 2)
    delta_proj: float = math.log(tan_lat2 / tan_lat1)

    # q correction factor
    q: float = delta_lat / delta_proj if abs(delta_proj) > 1e-12 else math.cos(lat1_rad)

    # Adjust longitude difference if crossing antimeridian
    if abs(delta_lon) > math.pi:
        delta_lon = delta_lon - math.copysign(2 * math.pi, delta_lon)

    # Rhumbline distance using Pythagorean formula on the ellipsoid
    distance_m: float = math.sqrt(delta_lat**2 + (q * delta_lon)**2) * Rn
    return distance_m / 1852  # meters to nautical miles

def GC_DIST(lat1: float, lon1: float, lat2: float, lon2: float, radius_km: float = 6371.0) -> float:
    """
    Calculates the Great Circle distance between two points on a spherical Earth.

    Parameters:
        lat1 (float): Latitude of point A in degrees.
        lon1 (float): Longitude of point A in degrees.
        lat2 (float): Latitude of point B in degrees.
        lon2 (float): Longitude of point B in degrees.
        radius_km (float, optional): Radius of the spherical Earth in kilometers. Default is 6371.0.

    Returns:
        float: Great Circle distance in nautical miles.
    """
    _validate_lat_lon(lat1, lon1, lat2, lon2)

    # Convert degrees to radians
    lat1_rad: float = math.radians(lat1)
    lon1_rad: float = math.radians(lon1)
    lat2_rad: float = math.radians(lat2)
    lon2_rad: float = math.radians(lon2)

    # Difference in coordinates
    delta_lat: float = lat2_rad - lat1_rad
    delta_lon: float = lon2_rad - lon1_rad

    # Haversine formula
    a: float = (math.sin(delta_lat / 2) ** 2 +
                math.cos(lat1_rad) * math.cos(lat2_rad) *
                math.sin(delta_lon / 2) ** 2)
    central_angle: float = 2 * math.asin(math.sqrt(a))

    # Handle special cases
    if central_angle == math.pi:
        raise ValueError("Points are antipodal")
    elif math.isnan(central_angle):
        raise ValueError("Could not compute great-circle distance")

    # Earth's radius ~6371 km, convert to nautical miles
    distance_km: float = central_angle * radius_km
    return distance_km / 1.852  # meters to nautical miles

def GC_DIST_WGS84(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the Great Circle (geodesic) distance between two points on the WGS84 ellipsoid
    using the Vincenty inverse formula.

    Parameters:
        lat1 (float): Latitude of point A in degrees.
        lon1 (float): Longitude of point A in degrees.
        lat2 (float): Latitude of point B in degrees.
        lon2 (float): Longitude of point B in degrees.

    Returns:
        float: Great Circle distance in nautical miles.
    """
    _validate_lat_lon(lat1, lon1, lat2, lon2)

    # WGS84 constants
    a: float = 6378137.0  # semi-major axis
    f: float = 1 / 298.257223563  # flattening
    b: float = (1 - f) * a        # semi-minor axis

    # Convert degrees to radians
    lat1_rad: float = math.radians(lat1)
    lon1_rad: float = math.radians(lon1)
    lat2_rad: float = math.radians(lat2)
    lon2_rad: float = math.radians(lon2)

    # Difference in longitude
    delta_lon: float = lon2_rad - lon1_rad

    # Reduced latitudes
    tan_u1: float = (1 - f) * math.tan(lat1_rad)
    tan_u2: float = (1 - f) * math.tan(lat2_rad)
    u1: float = math.atan(tan_u1)
    u2: float = math.atan(tan_u2)

    sin_u1: float = math.sin(u1)
    cos_u1: float = math.cos(u1)
    sin_u2: float = math.sin(u2)
    cos_u2: float = math.cos(u2)

    # Iterate Vincenty's formula
    lambda_val: float = delta_lon
    for _ in range(1000):
        sin_lambda: float = math.sin(lambda_val)
        cos_lambda: float = math.cos(lambda_val)

        sin_sigma: float = math.sqrt(
            (cos_u2 * sin_lambda) ** 2 +
            (cos_u1 * sin_u2 - sin_u1 * cos_u2 * cos_lambda) ** 2
        )
        if sin_sigma == 0:
            return 0.0  # coincident points

        cos_sigma: float = sin_u1 * sin_u2 + cos_u1 * cos_u2 * cos_lambda
        sigma: float = math.atan2(sin_sigma, cos_sigma)

        sin_alpha: float = cos_u1 * cos_u2 * sin_lambda / sin_sigma
        cos_sq_alpha: float = 1 - sin_alpha ** 2

        # Compute cos(2 * sigma_m)
        if cos_sq_alpha == 0:
            cos_2sigma_m: float = 0  # equatorial line
        else:
            cos_2sigma_m = cos_sigma - 2 * sin_u1 * sin_u2 / cos_sq_alpha

        # Correction term C
        C: float = f / 16 * cos_sq_alpha * (4 + f * (4 - 3 * cos_sq_alpha))

        lambda_prev: float = lambda_val
        lambda_val = delta_lon + (1 - C) * f * sin_alpha * (
            sigma + C * sin_sigma * (
                cos_2sigma_m + C * cos_sigma * (-1 + 2 * cos_2sigma_m ** 2)
            )
        )

        # Check convergence
        if abs(lambda_val - lambda_prev) < 1e-12:
            break
    else:
        raise ValueError("Vincenty formula did not converge")

    # Compute ellipsoidal corrections
    u_squared: float = cos_sq_alpha * (a ** 2 - b ** 2) / (b ** 2)
    A: float = 1 + u_squared / 16384 * (
        4096 + u_squared * (-768 + u_squared * (320 - 175 * u_squared))
    )
    B: float = u_squared / 1024 * (
        256 + u_squared * (-128 + u_squared * (74 - 47 * u_squared))
    )

    delta_sigma: float = B * sin_sigma * (
        cos_2sigma_m + B / 4 * (
            cos_sigma * (-1 + 2 * cos_2sigma_m ** 2) -
            B / 6 * cos_2sigma_m * (-3 + 4 * sin_sigma ** 2) *
            (-3 + 4 * cos_2sigma_m ** 2)
        )
    )

    distance_m: float = b * A * (sigma - delta_sigma)
    return distance_m / 1852  # meters to nautical miles