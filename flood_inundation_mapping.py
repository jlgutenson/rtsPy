# built-in imports
import os

# third party imports
import rasterio as rio


def with_max_wse(watershed, dem, max_wse, output_dir):
    """
    Estimates a simple maximum flood inundation map, as a geotiff, by taking a maximum coastal water surface elevation
    and substracting this value from each cell value in a DEM. Positive values can be considered inundated.

    Args:
        watershed (str): The name of the watershed where the flood inundation map is being generated.
        dem (str): A full path to the location of the digital elevation map (DEM) on which the flood inundation map will be based.
        max_wse (float): The value of the maximum water surface elevation at the outlet of the watershed.
        output_dir (str): The full path to where the resulting geotiff of flood inundation will be stored.

    Returns:
        str: flood_inundation_raster_path - This is a full-path to the resulting flood inundation map, expressed as a string.

    """

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