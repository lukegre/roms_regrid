import matplotlib.pyplot as plt
import numpy as np

def plot_map(da, figwidth=8, **kwargs):
    if da.lon.ndim == 2:
        return plot_roms_curvilinear_map(da, figwidth=figwidth, **kwargs)
    elif da.lon.ndim == 1:
        return plot_regridded_map(da, figwidth=figwidth, **kwargs)


def plot_roms_curvilinear_map(da, figwidth=8, x_name='lon', y_name='lat', **kwargs):
    from cartopy import (
        crs as ccrs,
        feature as cfeature
    )

    center_lon = da[x_name].mean().compute().item()
    
    proj = ccrs.PlateCarree(center_lon)
    trans = ccrs.PlateCarree()
    
    fig, ax = plt.subplots(dpi=120, subplot_kw=dict(projection=proj))
    
    props = dict(x=x_name, y=y_name, robust=True, ax=ax, transform=trans) | kwargs
    img_data = da.plot.pcolormesh(**props)
    
    ax.add_feature(cfeature.LAND.with_scale('50m'), fc='0.9', zorder=2)
    
    ax.set_axis_off()

    fig = set_fig_aspect(fig, ax, figwidth)

    return fig, ax, img_data


def plot_regridded_map(da, figwidth=8, **kwargs):
    from cartopy import (
        crs as ccrs,
        feature as cfeature
    )

    proj = ccrs.PlateCarree()
    
    fig, ax = plt.subplots(dpi=120, subplot_kw=dict(projection=proj))

    props = dict(robust=True, ax=ax, transform=proj) | kwargs
    img = da.plot.imshow(**props)

    ax.add_feature(cfeature.LAND.with_scale('50m'), fc='0.9', zorder=2)

    ax.set_axis_off()

    fig = set_fig_aspect(fig, ax, figwidth)

    return fig, ax, img


def set_fig_aspect(fig, ax, width):
    
    r = ax.get_data_ratio() / 1.18  # account for colorbar 
    fig.set_figwidth(width)
    fig.set_figheight(width * r)

    fig.tight_layout()

    return fig
