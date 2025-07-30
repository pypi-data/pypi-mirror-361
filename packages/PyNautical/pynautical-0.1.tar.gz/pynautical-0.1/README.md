# PyNautical

[![PyPI version](https://img.shields.io/pypi/v/pynautical)](https://pypi.org/project/pynautical/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pynautical)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://choosealicense.com/licenses/mit/)

**PyNautical** is a lightweight Python library for performing core navigational and maritime calculations.

It offers a set of simple, stateless functions to handle:

- Unit conversion between nautical miles and other distance units
- Degree and DMS (degrees-minutes-seconds) coordinate conversions
- Rhumbline and great circle course (bearing) computations
- Distance measurement on both spherical and WGS84 ellipsoidal models
- Coordinate interpolation along rhumbline and great circle routes

Designed for clarity and portability:

- No external dependencies (uses only the Python standard library)
- Suitable for route planning, marine simulations, GIS tools, and education
- Easy to integrate into both small scripts and larger navigation systems
## Installation

### For Users

PyNautical requires Python 3.9 or newer. You can use the package manager [pip](https://pip.pypa.io/en/stable/) install the latest release of `pynautical` from PyPI:

```bash
  pip install pynautical
```

### For Developers

To install the latest development version from source:

```bash
  git clone https://github.com/s-w-chen/pynautical.git
  cd pynautical
  pip install -e .
```
## Function Reference

| Module | Function | Description | Return Type |
|:--:|:--:|--|:--:|
| `units` | `to_nm` | Convert distance from unit to nautical miles | `float` |
| `units` | `nm_to` | Convert nautical miles to specified unit | `float` |
| `units` | `deg_to_dms` | Convert decimal degrees to DMS tuple | `tuple` |
| `units` | `dms_to_deg` | Convert DMS (deg, min, sec) to decimal degrees | `float` |
| `course` | `RL_COG` | Calculate rhumbline course (bearing) | `float` |
| `course` | `GC_COG` | Calculate great circle initial bearing | `float` |
| `distance` | `RL_DIST` | Rhumbline distance (spherical model) | `float` |
| `distance` | `GC_DIST` | Great circle distance (spherical model) | `float` |
| `distance` | `RL_DIST_WGS84` | Rhumbline distance (WGS84 ellipsoid) | `float` |
| `distance` | `GC_DIST_WGS84` | Great circle distance (WGS84 ellipsoid) | `float` |
| `route` | `RL_Slerp` | Interpolate points along rhumbline route | `tuple` |
| `route` | `GC_Slerp` | Interpolate points along great circle route | `tuple` |

## Usage

Import functions from submodules as needed:

```python
# Unit conversion functions
from pynautical.units import to_nm, nm_to, deg_to_dms, dms_to_deg

# Course (bearing) calculations
from pynautical.course import RL_COG, GC_COG  # Course Over the Ground

# Distance calculations
from pynautical.distance import RL_DIST, GC_DIST              # Spherical model
from pynautical.distance import RL_DIST_WGS84, GC_DIST_WGS84  # WGS84 ellipsoidal model

# Route coordinate calculations
from pynautical.route import RL_Slerp, GC_Slerp  # Interpolated waypoints along the route
```

If re-exported through the package root, you may also:

```python
import pynautical
```

## Examples

### Unit Conversion

Convert between nautical miles and other distance units.

```python
from pynautical.units import to_nm, nm_to

# Convert 26 kilometers to nautical miles
nm = to_nm(26, unit="km")
# Output: 14.038876
print(nm)

# Convert 2 nautical miles to feet
meters = nm_to(2, unit="ft")
# Output: 12152.230972
print(meters)
```

### Coordinate Conversion

Convert between decimal degrees and degrees-minutes-seconds (DMS).

```python
from pynautical.units import deg_to_dms, dms_to_deg

# Convert 9.487 degrees latitude to DMS
dms = deg_to_dms(9.487, coord_type="lat")
# Output: (9, 29, 13.2, 'N')
print(dms)

# Convert 25°7'22.8" N to decimal degrees
decimal_deg = dms_to_deg(26, 2, 9.1, direction="N")
# Output: 26.035861
print(decimal_deg)
```

### Course Calculation

Calculate rhumbline bearings (constant heading) and great circle bearings (initial azimuth at departure).

```python
from pynautical.course import RL_COG, GC_COG

# Rhumbline course (bearing) from TWKEL(25.17, 121.75) to USLSA(33.71, -118.25)
rl_bearing = RL_COG(25.17, 121.75, 33.71, -118.25)
# Output: 85.321161
print(rl_bearing)

# Great circle initial course from TWKEL(25.17, 121.75) to USLSA(33.71, -118.25)
gc_bearing = GC_COG(25.17, 121.75, 33.71, -118.25)
# Output: 46.686927
print(gc_bearing)
```

### Distance Calculation

Compute rhumbline and great circle distances in nautical miles using spherical or WGS84 ellipsoidal models.

```python
from pynautical.distance import RL_DIST, RL_DIST_WGS84, GC_DIST, GC_DIST_WGS84

# Rhumbline distance (spherical) from TWKEL(25.17, 121.75) to USLSA(33.71, -118.25)
rl_dist = RL_DIST(25.17, 121.75, 33.71, -118.25)
# Output: 6285.925260
print(rl_dist)

# Rhumbline distance (WGS84) from TWKEL(25.17, 121.75) to USLSA(33.71, -118.25)
rl_dist_wgs84 = RL_DIST_WGS84(25.17, 121.75, 33.71, -118.25)
# Output: 6298.061801
print(rl_dist_wgs84)

# Great circle distance (spherical) from TWKEL(25.17, 121.75) to USLSA(33.71, -118.25)
gc_dist = GC_DIST(25.17, 121.75, 33.71, -118.25)
# Output: 5888.213488
print(gc_dist)

# Great circle distance (WGS84) from TWKEL(25.17, 121.75) to USLSA(33.71, -118.25)
gc_dist_wgs84 = GC_DIST_WGS84(25.17, 121.75, 33.71, -118.25)
# Output: 5898.666636
print(gc_dist_wgs84)
```

### Route Coordinate Interpolation

Interpolate intermediate points along rhumbline or great circle routes.

```python
from pynautical.route import RL_Slerp, GC_Slerp

# Interpolate 25% along the rhumbline path
rl_point = RL_Slerp(25.17, 121.75, 33.71, -118.25, f=0.25)
# Output: (27.371492, 151.750000)
print(rl_point)

# Interpolate halfway along the great circle path
gc_point = GC_Slerp(25.17, 121.75, 33.71, -118.25, f=0.5)
# Output: (48.386373, 177.575501)
print(gc_point)
```
## Future Plans

Future versions of PyNautical aim to extend beyond route and distance calculations.

A key planned feature is support for AIS (Automatic Identification System) message encoding and decoding, allowing the library to:

- Parse raw AIS messages into structured data
- Encode structured AIS data into standard AIS message formats
- Provide utility functions for common AIS message types

This will expand PyNautical's capabilities for use in maritime tracking, simulation, and data analysis.
## License

MIT License ([MIT](https://choosealicense.com/licenses/mit/))

Copyright (c) 2025 Sheng-Wen,Chen

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.