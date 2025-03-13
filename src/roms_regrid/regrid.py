import pathlib
import numpy as np
import xarray as xr
import xesmf
from loguru import logger


class ROMSRegridder:
    def __init__(self, ds_in, res_out=0.1, bbox_out=[-180, -80, -70, 67], method='bilinear', weights_dir='./data/weights/'):

        self.ds_in = ds_in
        self.res = res_out
        self.bbox = bbox_out
        self.weights_dir = weights_dir
        self.method = method

        self.ds_out = self.make_target_grid(self.res, self.bbox)
        self.regridder = self.make_regridder()
        
    def __call__(self, ds_roms, compute=False):
        from tqdm.dask import TqdmCallback

        ds = self.prep_roms_output(ds_roms)

        ds_out = self.regridder(ds, keep_attrs=True)
        
        if compute:
            with TqdmCallback():
                ds_out = ds_out.compute()
        return ds_out
            
    def make_regridder(self):
        
        Ny_in, Nx_in = self.ds_in.lat.shape
        Ny_out, Nx_out = self.ds_out.shape
        
        weights_fname = f"{self.method}_{Ny_in}x{Nx_in}_{Ny_out}x{Nx_out}.nc"
        weights_path = pathlib.Path(self.weights_dir) / weights_fname
        weights_path.parent.mkdir(exist_ok=True, parents=True)
    
        props = dict(
            ds_in=self.ds_in, 
            ds_out=self.ds_out, 
            method=self.method, 
            unmapped_to_nan=True)
        
        if weights_path.exists():
            logger.info(f"Loading existing weights: {weights_path}")
            props['filename'] = weights_path
            props['reuse_weights'] = True
        else:
            logger.info(f"Creating weights: {weights_path}")
    
        regridder = xesmf.Regridder(**props)
    
        if not weights_path.exists():
            regridder.to_netcdf(weights_path)
    
        return regridder

    @staticmethod
    def make_target_grid(res=0.1, bbox_WSEN=[-180, -80, -70, 67]):
    
        west, south, east, north = bbox_WSEN
        s = res / 2
        
        da = xr.DataArray(
            np.nan, 
            dims=('lat', 'lon'),
            coords=dict(
                lat=np.arange(south + s, north, res),
                lon=np.arange(west + s, east, res),
            )
        )
    
        return da

    def prep_roms_output(self, ds):
    
        if 's_rho' in ds.dims:
            ds = ds.isel(s_rho=-1)  # select surface variable

        rename = {k: k.replace('_rho', '') for k in ['lat_rho', 'lon_rho'] if k in ds.coords}
        ds = ds.rename(rename)  # required for xesmf
    
        return ds

    def estimate_resolution(self, regridded=False, return_plot=False):
        from .utils import compute_resolution
        from . import viz

        dist = compute_resolution(self.ds_in)

        if regridded:
            dist = self(dist)

        if return_plot:
            vmax = dist.max().compute().item()
            props = dict(levels=np.arange(0, vmax, 5), cmap='cividis_r')
            fig, ax, img = viz.plot_map(dist, **props)
            return ax
        else:
            return dist