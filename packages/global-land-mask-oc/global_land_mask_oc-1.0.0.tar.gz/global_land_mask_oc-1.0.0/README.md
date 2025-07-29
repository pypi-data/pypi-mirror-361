# global-land-mask-oc
Global land mask for satellite ocean color remote sensing
# Installation
## via pip
```bash
pip install global-land-mask-oc
```
## via uv
```bash
uv add global-land-mask-oc
```

# Usage
## Single Point Check
```python
from global_land_mask_oc import globe
def check_if_land():
    lat = 40
    lon = -120
    is_on_land = globe.is_land(lat, lon)
    print("lat={}, lon={} is on land: {}".format(lat, lon, is_on_land))
```
## 2D Array Processing
```python
from global_land_mask_oc import globe

# Lat/lon
lat = np.linspace(32.533, 28.676, 1000)
lon = np.linspace(119.570, 123.266, 1002)

# Make a grid
lon_grid, lat_grid = np.meshgrid(lon, lat)

# Get whether the points are on land.
z = globe.is_land(lat_grid, lon_grid)
```

# Compare with global-land-mask
![](plot_globe_map_hangzhoubay.png)
global-land-mask-oc offers significant advantages over the original global-land-mask, including:
- Higher Resolution: Captures more detailed geographical features, ensuring accurate land identification even in complex coastal areas.​
- Included Lakes: Incorporates lake data, providing a more comprehensive representation of land-water boundaries for ocean color remote sensing.
# Reference
1. Mikelsons, K., Wang, M., Wang, X.-L. & Jiang, L. Global land mask for satellite ocean color remote sensing. Remote Sens. Environ. 257, 112356 (2021).
2. https://github.com/toddkarin/global-land-mask