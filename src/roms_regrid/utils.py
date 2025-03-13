import xarray as xr
import numpy as np


def compute_resolution(ds):
    """
    Compute the spatial resolution for each grid cell in an xarray dataset with a curvilinear grid.
    
    Parameters:
        ds (xarray.Dataset): Dataset containing 2D latitude ('lat') and longitude ('lon') arrays.
    
    Returns:
        xarray.DataArray: Resolution in meters for each pixel.
    """
    from haversine import haversine_vector

    y, x = ds.lat.dims
    lat = ds['lat'].values.flatten()
    lon = (ds['lon'].values.flatten() - 180) % 360 - 180

    arr = np.c_[lat, lon]
    dist_flat = haversine_vector(arr[:-1], arr[1:])
    dist_flat = np.pad(dist_flat, (0, 1), constant_values=np.nan)
    dist = dist_flat.reshape(*ds.lat.shape)
    
    da_dist = xr.DataArray(
        data=dist,
        dims=(y, x), 
        coords={
            'lat': ds.lat, 
            'lon': ds.lon}, 
        attrs=dict(
            long_name='ROMS resolution estimate',
            units='km',
        )
    )

    threshold = da_dist.mean() + da_dist.std() * 5
    da_dist = da_dist.where(lambda x: x < threshold)
    
    return da_dist
