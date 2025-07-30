def to_nm(value: float, unit: str = "km") -> float:
    """
    Convert a given distance value to nautical miles (NM).

    Parameters:
        value (float): The distance value to be converted.
        unit (str): The unit of the input value. Supported units are:
                    - "km": kilometers (default)
                    - "m" : meters
                    - "mi": miles
                    - "yd": yards
                    - "ft": feet

    Returns:
        float: The equivalent distance in nautical miles.

    Raises:
        ValueError: If the specified unit is not supported.
    """
    unit = unit.lower()
    if unit == "km":
        return value / 1.852
    elif unit == "m":
        return value / 1852
    elif unit == "mi":
        return value / 1.150779448
    elif unit == "yd":
        return value / 2025.371829
    elif unit == "ft":
        return value / 6076.115486
    else:
        raise ValueError(f"Unsupported unit: {unit}")

def nm_to(value: float, unit: str = "km") -> float:
    """
    Convert a distance in nautical miles (NM) to another unit.

    Parameters:
        value (float): The distance in nautical miles.
        unit (str): The target unit. Supported units are:
                    - "km": kilometers (default)
                    - "m" : meters
                    - "mi": miles
                    - "yd": yards
                    - "ft": feet

    Returns:
        float: The converted distance in the specified unit.

    Raises:
        ValueError: If the specified unit is not supported.
    """
    unit = unit.lower()
    if unit == "km":
        return value * 1.852
    elif unit == "m":
        return value * 1852
    elif unit == "mi":
        return value * 1.150779448
    elif unit == "yd":
        return value * 2025.371829
    elif unit == "ft":
        return value * 6076.115486
    else:
        raise ValueError(f"Unsupported unit: {unit}")

def deg_to_dms(decimal_degrees: float, coord_type: str) -> tuple:
    """
    Convert decimal degrees to degrees, minutes, seconds (DMS) with direction.
    Longitude input will be wrapped into [-180, 180] if within [-360, 360].
    Latitude must be within [-90, 90].

    Parameters:
        decimal_degrees (float): The input angle in decimal degrees.
        coord_type (str): Coordinate type:
                          - 'lat' for latitude
                          - 'lon' for longitude

    Returns:
        tuple: A tuple (degrees, minutes, seconds, direction), where:
               - degrees (int): Absolute degree component.
               - minutes (int): Minute component (0~59).
               - seconds (float): Second component (0~59.999...).
               - direction (str): 'N' or 'S' for latitude; 'E' or 'W' for longitude.

    Raises:
        ValueError: If coord_type is invalid.
        ValueError: If latitude is outside [-90, 90].
        ValueError: If longitude is outside [-360, 360].
    """
    if coord_type not in ("lat", "lon"):
        raise ValueError("coord_type must be 'lat' or 'lon'.")

    if coord_type == "lat":
        if not (-90 <= decimal_degrees <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
    else:  # coord_type == "lon"
        if not (-360 <= decimal_degrees <= 360):
            raise ValueError("Longitude must be between -360 and 360 degrees.")
        # Wrap longitude into [-180, 180]
        if decimal_degrees > 180:
            decimal_degrees -= 360
        elif decimal_degrees < -180:
            decimal_degrees += 360

    abs_deg = abs(decimal_degrees)
    degrees = int(abs_deg)
    minutes = int((abs_deg - degrees) * 60)
    seconds = (abs_deg - degrees - minutes / 60) * 3600

    if coord_type == "lat":
        direction = 'N' if decimal_degrees >= 0 else 'S'
    else:
        direction = 'E' if decimal_degrees >= 0 else 'W'

    return degrees, minutes, seconds, direction

def dms_to_deg(degrees: int, minutes: int, seconds: float, direction: str) -> float:
    """
    Convert degrees, minutes, seconds (DMS) with direction to decimal degrees.
    Longitude result will be wrapped to [-180, 180].

    Parameters:
        degrees (int): Degree component (0~90 for latitude, 0~180 for longitude).
        minutes (int): Minute component (0~60).
        seconds (float): Second component (0~60).
        direction (str): Direction letter:
                         - 'N' or 'S' for latitude
                         - 'E' or 'W' for longitude

    Returns:
        float: Decimal degrees.
               - For latitude: Range is [-90, 90].
               - For longitude: Wrapped into [-180, 180].

    Raises:
        ValueError: If direction is invalid.
        ValueError: If degrees/minutes/seconds are out of valid ranges.
    """
    direction = direction.upper()
    if direction not in ('N', 'S', 'E', 'W'):
        raise ValueError("Direction must be one of 'N', 'S', 'E', or 'W'.")

    if direction in ('N', 'S'):
        if not (0 <= degrees <= 90):
            raise ValueError("Latitude degrees must be between 0 and 90.")
    else:
        if not (0 <= degrees <= 180):
            raise ValueError("Longitude degrees must be between 0 and 180.")

    if not (0 <= minutes <= 60):
        raise ValueError("Minutes must be between 0 and 60.")
    if not (0 <= seconds <= 60):
        raise ValueError("Seconds must be between 0 and 60.")

    decimal = degrees + minutes / 60 + seconds / 3600
    if direction in ('S', 'W'):
        decimal = -decimal

    # Wrap longitude result to [-180, 180]
    if direction in ('E', 'W'):
        if decimal > 180:
            decimal -= 360
        elif decimal < -180:
            decimal += 360

    return decimal