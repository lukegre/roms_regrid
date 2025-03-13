from .load import (
    ROMSLoader, 
    read_data_sources)

from .regrid import ROMSRegridder
from .viz import plot_map
from textwrap import dedent as _dedent

print(
    _dedent("""
    A lightweight package to regrid ROMS data

    Functions:
      - read_data_sources -> catalog: reads data_sources.yaml that contains info to load ROMS data
      - ROMSLoader(catalog.entry) -> loader(year) -> ds_roms
      - ROMSRegridder(ds, res_out, bbox_out=[W,S,E,N]) -> regridder(ds_roms) -> ds_regridded
      - plot_map(ds_roms.pco2sea) -> fig, axs, img 

    """
))