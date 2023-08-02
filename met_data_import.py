# third party Java modules
from mil.army.usace.hec.vortex.io import BatchImporter
from mil.army.usace.hec.vortex.geo import WktFactory
from mil.army.usace.hec.vortex.math import BatchSanitizer 

# native modules to add
import os
import shutil
import gzip
import sys

if __name__ == "__main__":
    """
    met_grib_dir = "D:/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/Scripts/build_hms_inputs/mrms_gage_corrected"
    clip_shp = "C:/Users/Joseph Gutenson/Desktop/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/1.2.2.2.2/Models/HEC_HMS_411beta16/1. RVD/Extrass/RVDWshed.shp"
    destination = "D:/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/1.2.2.2.2/Models/HEC_HMS_411beta16/1_RVD/1_HEC-HMS_Model/RVD_NAD8310171/RVDJune2018_JLG_scripted_1.dss"
    # parameters and set up for Vortex to create the dss file
    # documented here: https://github.com/HydrologicEngineeringCenter/Vortex/wiki/Batch-Import-Options
    variables = ['GaugeCorrQPE01H_altitude_above_msl']

    The actual command line arguments start from index 1.
    The first item in sys.argv is the name of the script itself (e.g., my_script.py).
    list of variables that we'll eventually convert to inputs in a function.
    """
    num_args = len(sys.argv) - 1
    met_grib_dir = sys.argv[1]
    met_grib_dir = met_grib_dir.replace('\\', '/')
    clip_shp = sys.argv[2]
    clip_shp = clip_shp.replace('\\', '/')
    destination = sys.argv[3]
    destination = destination.replace('\\', '/')
    variables = sys.argv[4]
    variables = [variables]
    met_forcing = sys.argv[5]

    # see if dss file already exists and if so, remove it
    if os.path.exists(destination):
        os.remove(destination)
    else:
        pass

    # list all grib files in the directory 
    in_files = os.listdir(met_grib_dir)

    # pair each grib file with its full path and pack into a list
    in_files_path = []
    for in_file in in_files:
        if met_forcing == "MRMS":
            if in_file.endswith("grib2.gz"):
                # decompress *.gz files
                in_file_full_path = os.path.join(met_grib_dir,in_file)
                with gzip.open(in_file_full_path, 'rb') as f_in:
                    out_file_full_path = in_file_full_path[:-3]
                    with open(out_file_full_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                in_files_path.append(out_file_full_path)
            else:
                pass
        elif met_forcing == "HRRR":
            # retrieve just the path to the destination file
            destination_dir = os.path.dirname(destination)
            temp_dss = os.path.join(destination_dir,"temp.dss")
            if in_file.endswith("grib2"):
                in_file_full_path = os.path.join(met_grib_dir,in_file)
                in_files_path.append(in_file_full_path)
            else:
                pass

    # sort the list of grib files, doesn't seem to make a difference
    in_files_path.sort()

    # GIS options that mimic Linda and Ivan's initial set-up in HEC-HMS
    geo_options = {
        'pathToShp': clip_shp,
        'targetCellSize': '2000',
        'targetWkt': WktFactory.shg(),
        'resamplingMethod': 'Bilinear',
    }

    # options that specify the composition of the DSS file
    write_options = {
        'partA': 'SHG',
        'partB': 'RVD',
        'partC': 'PRECIPITATION',
        'partF': met_forcing,
        'dataType': 'PER-CUM',
        'units': 'MM'
    }

    if met_forcing == "MRMS":
        myImport = BatchImporter.builder() \
                        .inFiles(in_files_path) \
                        .variables(variables) \
                        .geoOptions(geo_options) \
                        .destination(destination) \
                        .writeOptions(write_options) \
                        .build()

        myImport.process()
    elif met_forcing == "HRRR":
        myImport = BatchImporter.builder() \
                        .inFiles(in_files_path) \
                        .variables(variables) \
                        .geoOptions(geo_options) \
                        .destination(temp_dss) \
                        .writeOptions(write_options) \
                        .build()

        myImport.process()

    # make the HRRR zero values = 0 
    if met_forcing == "HRRR":
        myImport = BatchSanitizer.builder()\
        .pathToInput(temp_dss)\
        .selectAllVariables()\
        .minimumThreshold(0)\
        .minimumReplacementValue(0)\
        .destination(destination)\
        .writeOptions(write_options).build()

        myImport.process() 
