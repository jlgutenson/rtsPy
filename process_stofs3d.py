# native imports
import os 
import math
import datetime
import time
import sys
import subprocess

# third party imports
import xarray as xr
import numpy as np
import urllib.request
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# label for boundary
boundary_name = "IBWC"

# example points to query
lat_of_boundary = 26.467121
lon_of_boundary = -97.393651

# download_directory
download_directory = "/mnt/d/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/Scripts/build_hms_inputs/stofs3d"

# should we download the data?
download_stofs_data = False

# download grib2 or netcdf versions. The NetCDF is higher resolution.
file_format = "grib2"

# where I've install DSSVue to create my DSS file
path_to_dssvue_install = "/home/jlgutenson/hec-dssvue-3.3.26"

# where is the Jython that DSSVue will use?
path_to_jython_install = "/home/jlgutenson/jython-standalone-2.7.3.jar"

# what is the cwd for the Jython script?
cwd = "/mnt/d/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/Scripts/build_hms_inputs"

def download(download_directory, date, cycle, download_stofs_data, file_format):
    # breakdown of the various stofs datasets can be found here:
    # https://noaa-nos-stofs3d-pds.s3.amazonaws.com/README.html
    if download_stofs_data == True:
        if not os.path.isdir(os.path.split(download_directory)[0]):
            os.mkdir(os.path.split(download_directory)[0])
        if not os.path.isdir(download_directory):
            os.mkdir(download_directory)
        if file_format == "grib2":
            for hour in range(0, 49):
                time_step = str(hour).zfill(2)
                url = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/stofs/prod/stofs_3d_atl.{date}/stofs_3d_atl.t{cycle}z.conus.east.f0{time_step}.grib2"
                print(url)
                filename = url.split("/")[-1]
                f = open(download_directory + os.sep + filename, 'wb')
                f.write(urllib.request.urlopen(url).read())
                f.close()            
                # set the file permissions for the bash scripts
                execute_permission = 0o755
                # Set the execute permissions on the file
                os.chmod(download_directory + os.sep + filename, execute_permission)
                time.sleep(2) # in seconds
        elif file_format == "netcdf":
            # stofs netcdfs are 
            url = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/stofs/prod/stofs_3d_atl.{date}/stofs_3d_atl.t{cycle}z.fields.out2d_forecast_day1.nc"
            print(url)
            filename = url.split("/")[-1]
            f = open(download_directory + os.sep + filename, 'wb')
            f.write(urllib.request.urlopen(url).read())
            f.close()            
            # set the file permissions for the bash scripts
            execute_permission = 0o755
            # Set the execute permissions on the file
            os.chmod(download_directory + os.sep + filename, execute_permission)
            time.sleep(2) # in seconds
            url = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/stofs/prod/stofs_3d_atl.{date}/stofs_3d_atl.t{cycle}z.fields.out2d_forecast_day2.nc"
            print(url)
            filename = url.split("/")[-1]
            f = open(download_directory + os.sep + filename, 'wb')
            f.write(urllib.request.urlopen(url).read())
            f.close()            
            # set the file permissions for the bash scripts
            execute_permission = 0o755
            # Set the execute permissions on the file
            os.chmod(download_directory + os.sep + filename, execute_permission)
    else:   
        pass
    return(download_directory)


if __name__ == "__main__":

    time_stamp_list = []
    wse_list = []

    # set the file permissions for the bash scripts
    execute_permission = 0o755

    #stofs3d output appears to upload to nomads by 1900z each day, so the September 19, 2023 forecast is available on September 19, 2023 at 1900z
    todays_date = datetime.datetime.utcnow()
    current_hour = todays_date.strftime("%-H")
    if int(current_hour) >= 19:
        date_to_use = todays_date
    else:
        date_to_use = todays_date - datetime.timedelta(days=1)

    date = date_to_use.strftime('%Y%m%d')

    # hour currently appears constant at 1200z
    cycle = 12

    download_directory = os.path.join(download_directory, date, str(cycle))

    download_directory = download(download_directory, date, cycle, download_stofs_data, file_format)

    if file_format == "grib2":

        grib_files = os.listdir(download_directory)

        # find the grid index if you haven't already
        find_index = True

        for file in grib_files:
            if file.endswith(".grib2"):
                grib_file = os.path.join(download_directory,file)

                x = lat_of_boundary
                y = lon_of_boundary + 360

                ds = xr.load_dataset(grib_file, engine='cfgrib')

                ds = ds.rename({'unknown':'water_level_m'})

                if find_index is True:

                    # Find the correct coordinate names for longitude and latitude
                    lon_coord_name = 'longitude'
                    lat_coord_name = 'latitude'

                    # Manually specify the longitude and latitude values
                    lon_values = np.array([x])
                    lat_values = np.array([y])

                    # Manually specify the latitude and longitude values
                    lon_values = x
                    lat_values = y

                    # Calculate the indices of the nearest grid point  
                    lon_degree_vals_numpy = ds[lon_coord_name].values
                    lat_degree_vals_numpy = ds[lat_coord_name].values
                    rad_factor = math.pi/180.0 # for trignometry, need angles in radians

                    # Read latitude from file into numpy arrays
                    latvals = lat_degree_vals_numpy * rad_factor
                    lat0_rad = lat_of_boundary * rad_factor

                    # Find nearest grid cell centroid using Haversine Distance
                    r = 6371 #radius of the earth in km
                    dlat = rad_factor * (lat_degree_vals_numpy - lat_of_boundary)
                    dlon = rad_factor * (lon_degree_vals_numpy - lon_of_boundary)
                    a = np.sin(dlat/2)**2 + np.cos(lat0_rad) * np.cos(latvals) * np.sin(dlon/2)**2
                    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
                    distance = c * r # in units of km
                    minindex_2d = np.unravel_index(distance.argmin(), distance.shape)

                    find_index = False


                # Use xarray's nearest-neighbor selection method
                selected_data = ds.water_level_m.sel(y = minindex_2d[0],x = minindex_2d[1])

                # Extract the selected time stamp, in nanoseconds
                # For some reason, the first time stamp is being read as 5 hours behind
                # So I've added 21600 seconds to the time stamp
                selected_time = datetime.datetime.fromtimestamp((selected_data.time.values.item()+selected_data.step.item())/(1e9)+21600)
                time_stamp_list.append(selected_time)

                # Extract the selected data value as a NumPy array
                selected_value = selected_data.values.item()
                wse_list.append(selected_value)

                print(f"Water level at {lat_of_boundary}, {lon_of_boundary}: {selected_value} meters at {selected_time}")
            time_stamp_array = np.array(time_stamp_list)
            wse_array = np.array(wse_list)
    elif file_format == "netcdf":
        # list the files in the download directory
        netcdf_files = os.listdir(download_directory)

        # make two list to store the resulting arrays
        time_stamp_list = []
        wse_list = []

        # find the grid index if you haven't already
        find_index = True

        for file in netcdf_files:
            if file.endswith(".nc"):
                netcdf_file = os.path.join(download_directory,file)

                x = lon_of_boundary
                y = lat_of_boundary

                ds = xr.load_dataset(netcdf_file, engine='netcdf4')

                # List of data variables you want to keep
                variables_to_keep = ['SCHISM_hgrid_node_x', 'SCHISM_hgrid_node_y', 'depth', 'elevation']

                # Use the drop_vars() method to remove unwanted variables
                ds = ds.drop_vars([var for var in ds.data_vars if var not in variables_to_keep])

                # Find the correct coordinate names for longitude and latitude
                lon_coord_name = 'SCHISM_hgrid_node_x'
                lat_coord_name = 'SCHISM_hgrid_node_y'

                # Manually specify the longitude and latitude values
                lon_values = np.array([x])
                lat_values = np.array([y])

                # Manually specify the latitude and longitude values
                lon_values = x
                lat_values = y

                # Calculate the indices of the nearest grid point  
                lon_degree_vals_numpy = ds[lon_coord_name].values
                lat_degree_vals_numpy = ds[lat_coord_name].values

                rad_factor = math.pi/180.0 # for trignometry, need angles in radians

                # Read latitude from file into numpy arrays
                latvals = lat_degree_vals_numpy * rad_factor
                lat0_rad = lat_of_boundary * rad_factor

                # Find nearest grid cell centroid using Haversine Distance
                r = 6371 #radius of the earth in km
                dlat = rad_factor * (lat_degree_vals_numpy - lat_of_boundary)
                dlon = rad_factor * (lon_degree_vals_numpy - lon_of_boundary)
                a = np.sin(dlat/2)**2 + np.cos(lat0_rad) * np.cos(latvals) * np.sin(dlon/2)**2
                c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
                distance = c * r # in units of km
                minindex_1d = distance.argmin()  # 1D index of minimum element
                closest_lat = lat_degree_vals_numpy[minindex_1d]
                closest_lon = lon_degree_vals_numpy[minindex_1d]
                

                # Define the conditions
                lon_condition = ds['SCHISM_hgrid_node_x'] == closest_lon
                lat_condition = ds['SCHISM_hgrid_node_y'] == closest_lat

                # Create a composite condition using logical operators
                composite_condition = lon_condition + lat_condition # You can use '&' for AND, '|' for OR

                # Use the composite condition to filter the dataset
                ds = ds.where(composite_condition, drop=True) 

                # store the data so we can combine it
                timevar = ds.time
                time_stamp_list.append(timevar.to_numpy())
                wse_data = ds.elevation
                wse_list.append(wse_data.values)

        time_stamp_array = np.concatenate((time_stamp_list[0], time_stamp_list[1]))
        wse_array = np.concatenate((wse_list[0], wse_list[1]))

    # create a plot of the time series to see what things look like
    plt.rcParams["figure.figsize"] = (10,7)
    plt.plot(time_stamp_array,wse_array)
    plt.xlabel("Time (UTC)")
    plt.ylabel("Water Surface Elevation (meters above NAVD88)")
    plt.savefig(os.path.join(download_directory,'wse_navd88.png'))

    # Converting numpy arrays to lists
    time_stamp_list = list(time_stamp_array)
    wse_list = list(wse_array*3.28084) # converting these values to feet

    # let's create the DSS file that HEC-RAS needs as a boundary condition
    # we're doing this using the HEC-DSSVue software and Jython
    # the lines below are building a bash script that will then be ran
    # had to install libgfortran5 to get this working on Ubuntu 20.04
    # sudo apt-get update 
    # sudo apt-get install libgfortran5
    print("Creating DSS file with HEC-DSSVue.")
    # this function will pull the observed streamflow from our assimilation gages
    coastal_boundary_dss_file = f"coastal_boundary_{boundary_name}.dss"
    coastal_boundary_dss_path = os.path.join(download_directory,coastal_boundary_dss_file)
    # delete the old DSS file, they corrupt very easily otherwise
    if os.path.exists(coastal_boundary_dss_path):          
        os.remove(coastal_boundary_dss_path)
    if sys.platform == 'linux' or sys.platform == 'linux2':
        dss_file_name = "coastal_boundary_{0}{1}{2}{3}_{4}.sh".format(date_to_use.year, 
                                                                     date_to_use.strftime("%m"),
                                                                     date_to_use.strftime("%d"),
                                                                     date_to_use.strftime("%H"),
                                                                     boundary_name)
        dss_file = os.path.join(download_directory,dss_file_name)
        with open(dss_file, "w") as open_dss_file:
            string_to_write = '#!/bin/bash'
            open_dss_file.write(string_to_write)
            open_dss_file.write('\n')

            string_to_write = 'DSS_HOME="{0}"\n'.format(str(path_to_dssvue_install))
            open_dss_file.write(string_to_write)

            string_to_write = 'export PATH="$DSS_HOME/lib:$PATH"'
            open_dss_file.write(string_to_write)
            open_dss_file.write('\n')

            string_to_write = 'JAVA_DSS_PATH="$DSS_HOME/java/jre/bin/java"' 
            open_dss_file.write(string_to_write)
            open_dss_file.write('\n')

            string_to_write = 'JAVA_DSS_LIB_PATH="$DSS_HOME/lib"'
            open_dss_file.write(string_to_write)
            open_dss_file.write('\n')

            string_to_write = 'CLASS_PATH="{0}:$DSS_HOME/jar/*"'.format(path_to_jython_install) 
            open_dss_file.write(string_to_write)
            open_dss_file.write('\n')

            date_string = "{0}{1}{2}".format(date_to_use.strftime("%d"),date_to_use.strftime("%b").upper(),date_to_use.strftime("%Y"))
            time_string = "{0}00".format(cycle+1)

            string_to_write = f'$JAVA_DSS_PATH -Xmx12g -Djava.library.path="$JAVA_DSS_LIB_PATH" -classpath "$CLASS_PATH" org.python.util.jython {cwd}/create_coastal_boundary_dss_file.py "{coastal_boundary_dss_path}" "{wse_list}" "{date_string}" "{time_string}" "{boundary_name}"'

            open_dss_file.write(string_to_write)
            open_dss_file.write('\n') 
            open_dss_file.close()
        # Open the subprocess without creating a new window
        # Set the execute permissions on the file
        os.chmod(dss_file, execute_permission)
        process = subprocess.Popen(dss_file, shell=True)
        stdout, stderr = process.communicate()