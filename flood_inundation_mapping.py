# built-in imports
import os

# third party imports
import rasterio as rio


def with_max_wse(watershed, dem, max_wse, output_dir):

    with rio.open(dem) as src:
        elevation_navd88_m = src.read(1, masked=True)
        profile = src.profile

    depth = max_wse - elevation_navd88_m
    depth[depth.mask] = profile["nodata"]

    flood_inundation_raster = f"flood_depth_m_{watershed}.tif"
    flood_inundation_raster_path = os.path.join(output_dir,flood_inundation_raster)

    with rio.open(flood_inundation_raster_path, 'w', **profile) as dst:
        dst.write(depth, 1,)

    return(flood_inundation_raster_path)