from pathlib import Path

import numpy as np

# Load data efficiently using pathlib
_mask_file = Path(__file__).parent / "global-land-mask-oc.npz"
_mask_data = np.load(_mask_file)
_mask = _mask_data["watermask"]
_lat = _mask_data["lat"]
_lon = _mask_data["lon"]

# Precompute step sizes for faster conversion
_LAT_STEP = (_lat[-1] - _lat[0]) / (_lat.size - 1)
_LON_STEP = (_lon[-1] - _lon[0]) / (_lon.size - 1)


def _validate_coords(lat, lon):
    """Validate latitude and longitude values."""
    lat = np.asarray(lat)
    lon = np.asarray(lon)

    if np.any((lat < -90) | (lat > 90)):
        raise ValueError("Latitude must be between -90 and 90 degrees")
    if np.any((lon < -180) | (lon > 180)):
        raise ValueError("Longitude must be between -180 and 180 degrees")

    return lat, lon


def _coord_to_index(coord, coord_range, step):
    """Convert coordinate to array index."""
    return ((coord - coord_range[0]) / step).astype(int)


def lat_to_index(lat):
    """Convert latitude to mask index."""
    lat, _ = _validate_coords(lat, 0)
    return _coord_to_index(np.clip(lat, _lat.min(), _lat.max()), _lat, _LAT_STEP)


def lon_to_index(lon):
    """Convert longitude to mask index."""
    _, lon = _validate_coords(0, lon)
    return _coord_to_index(np.clip(lon, _lon.min(), _lon.max()), _lon, _LON_STEP)


def is_ocean(lat, lon):
    """Return boolean array indicating if coordinates are in ocean."""
    lat_i = lat_to_index(lat)
    lon_i = lon_to_index(lon)
    return _mask[lat_i, lon_i]


def is_land(lat, lon):
    """Return boolean array indicating if coordinates are on land."""
    return np.logical_not(is_ocean(lat, lon))
