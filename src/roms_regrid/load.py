import numpy as np
import xarray as xr


class ROMSLoader:
    def __init__(self, catalog_entry):
        
        self._entry = catalog_entry

        self.fname_fmt = catalog_entry.fname
        self._time = catalog_entry.time
        self.standard_dim_names = dict(
            eta_rho='y',
            xi_rho='x',
            lat_rho='lat',
            lon_rho='lon')

    def __call__(self, index_or_year):
        if index_or_year > 1970:
            fname = self.get_fname_with_year(index_or_year)
        else:
            fname = self.get_fname_with_index(index_or_year)

        return self.load_netcdf(fname)

    def get_fname_with_index(self, i):
        
        fname = self.fname_fmt
        time = self._time

        time_range = np.arange(
            time.start, 
            time.end + time.step // 2,
            time.step)
        i = time_range[i]

        return fname.format(t=i)

    def get_fname_with_year(self, year):
        
        fname = self.fname_fmt
        time = self._time
        
        time_range = np.arange(
            time.start, 
            time.end + time.step // 2,
            time.step)

        assert year in time_range

        return fname.format(t=year)

    def load_netcdf(self, fname):
        
        ds = xr.open_dataset(fname, chunks={})

        subset = self._entry.get('subset', {})

        # overwrite standard names in default vars
        default_var_dict = {k: k for k in ds.data_vars} | self.standard_dim_names  
        # if standard names are given in yaml file's variables, then it will use those
        var_dict = self.standard_dim_names | self._entry.get('variables', default_var_dict)
        var_list = list(var_dict)

        ds = ds.isel(**subset)[var_list].rename(**var_dict)
        ds.attrs['source'] = fname

        return ds


def read_data_sources(fname):
    import yaml 
    import munch

    with open(fname) as fobj:
        data_info = yaml.safe_load(fobj)

    data_info = munch.munchify(data_info)

    return data_info