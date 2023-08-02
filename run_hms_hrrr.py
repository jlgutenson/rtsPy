# native imports
from datetime import datetime, timezone, timedelta
import os
import shutil
import subprocess
import sys
import pathlib

# local imports
from data_retrieval_scripts.HRRR_QPF_Download import download

# third party imports

# variables that will change with different runs
# length of the simulation, in hours
simulation_length = 18
# path to folder where each hours MRMS data will be downloaded
name_of_gridded_directory = "hrrr_subhourly" # name of the directory storing each forecast
# path to the folder containing the Vortex install, the HEC tool for converted gridded data into DSS format
path_to_vortex_install = r"D:\Gutenson_RATES\TWDB-FIF-LRGVDC\2023\Scripts\build_hms_inputs\vortex-0.11.0"
# path to Jython executable
path_to_jython_install = r"C:\jython2.7.3\bin\jython.exe"
# area defining the geographic extent of the HEC-HMS model
hec_hms_clip_shp = r"D:\Gutenson_RATES\TWDB-FIF-LRGVDC\2023\1.2.2.2.2\Models\HEC_HMS_411beta16\1_RVD\1_HEC-HMS_Model\RVD_NAD8310171\gis\RVD_83_1\RVD_83_1.shp"
# DSS file to output the gridded meteorlogy data into
vortex_dss_file = "RVDJune2018_JLG_scripted_1.dss"
# type of meteorological data we're using
met_forcing = "HRRR"
# variable in the meteorlogy data containing precipitation
variables = 'Total_precipitation_surface_15_Minute_Accumulation'
# path to the directory containing the watershed's HEC-HMS model
hms_model_directory = r"C:\Users\Joseph Gutenson\Desktop\Gutenson_RATES\TWDB-FIF-LRGVDC\2023\1.2.2.2.2\Models\HEC_HMS_411beta16\1. RVD\1. HEC-HMS Model\RVD_NAD8310171"
# name of the HEC-HMS control file we're updating
hms_control_file_name = "June2018.control"
# the time-step of the HEC-HMS simulation, in minutes
hms_time_step = 15
# path to the directory containing HEC-HMS
hms_directory = r"D:\Gutenson_RATES\TWDB-FIF-LRGVDC\2023\Scripts\build_hms_inputs\HEC-HMS-4.11-beta.16"
# name of the hms project file 
hms_project_file = "RVD_NAD8310171.hms"
# name of the hms simulation to run
hms_run_name = "June 2018"


if __name__ == '__main__':

    # pull the current time in UTC
    current_time = datetime.now(timezone.utc)
    current_time_latency_two_hour = current_time - timedelta(hours=2)

    current_time_latency_two_hour_plus_17_hours = current_time_latency_two_hour + timedelta(hours=17)


    # directory to store the forecast
    hrrr_directory = os.path.join(os.getcwd(),name_of_gridded_directory)
    
    # see if HRRR directory already exists and if so, remove it
    if os.path.exists(hrrr_directory):
        shutil.rmtree(hrrr_directory)
        os.mkdir(hrrr_directory)
    else:
        os.mkdir(hrrr_directory)

    # download the HRRR precip and point the script to the download folder
    hrrr_directory = download(hrrr_directory, current_time_latency_two_hour)

    # check to see if gridded DSS file exists and if so, remove it and copy over the new one
    if os.path.exists(os.path.join(hms_model_directory,vortex_dss_file)):          
        os.remove(os.path.join(hms_model_directory,vortex_dss_file))

    # now that we have our HRRR data, we need to create our DSS file
    # check what system you're using to see if I need a batch or sh file to run Vortex with Jython
    vortex_dss_file_path = os.path.join(hms_model_directory,vortex_dss_file)
    if sys.platform == 'win32':
        # we're building the bat file that runs Vortex in Windows here
        print("Running Vortex on Windows.\n")
        vortex_file_name = "vortex_{0}{1}{2}{3}.bat".format(current_time_latency_two_hour.year, 
                                                    current_time_latency_two_hour.strftime("%m"),
                                                    current_time_latency_two_hour.strftime("%d"),
                                                    current_time_latency_two_hour.strftime("%H"))
        vortex_file = os.path.join(hrrr_directory,vortex_file_name)
        with open(vortex_file, "w") as open_vortex_file:
            string_to_write = 'set "VORTEX_HOME={0}"\n'.format(str(path_to_vortex_install))
            open_vortex_file.write(string_to_write)
            string_to_write = r'set "PATH=%VORTEX_HOME%\bin;%VORTEX_HOME%\bin\gdal;%PATH%"'
            open_vortex_file.write(string_to_write)
            open_vortex_file.write('\n')
            string_to_write = r'set "GDAL_DATA=%VORTEX_HOME%\bin\gdal\gdal-data"' 
            open_vortex_file.write(string_to_write)
            open_vortex_file.write('\n')
            string_to_write = r'set "PROJ_LIB=%VORTEX_HOME%\bin\gdal\projlib"'
            open_vortex_file.write(string_to_write)
            open_vortex_file.write('\n')
            string_to_write = r'set "CLASSPATH=%VORTEX_HOME%\lib\*"'
            open_vortex_file.write(string_to_write)
            open_vortex_file.write('\n')
            string_to_write = '{0} -J-Xmx12g -Djava.library.path=%VORTEX_HOME%\\bin;%VORTEX_HOME%\\bin\gdal met_data_import.py "{1}" "{2}" "{3}" {4} "{5}"\n'.format(path_to_jython_install,hrrr_directory,hec_hms_clip_shp,vortex_dss_file_path,variables,met_forcing)
            open_vortex_file.write(string_to_write)
            open_vortex_file.close()

            # Open the subprocess without creating a new window
            process = subprocess.Popen(vortex_file, shell=True)
            stdout, stderr = process.communicate()


    # and also update our HEC-HMS control specifications
    # check if old control file exists and delete it accordingly
    if os.path.exists(os.path.join(hms_model_directory,hms_control_file_name)):
        os.remove(os.path.join(hms_model_directory,hms_control_file_name))
        
    print("Creating the HEC-HMS control file.\n")
    with open(os.path.join(hms_model_directory,hms_control_file_name), "w") as hms_control_file:
        hms_control_file.write("Control: {0}\n".format(hms_control_file_name[:-8]))
        hms_control_file.write("     Last Modified Date: 21 July 2023\n")
        hms_control_file.write("     Last Modified Time: 17:26:17\n")
        hms_control_file.write("     Version: 4.11\n")
        hms_control_file.write("     Time Zone ID: America/Chicago\n")
        hms_control_file.write("     Time Zone GMT Offset: -21600000\n")
        hms_control_file.write("     Start Date: {0} {1} {2}\n".format(str(current_time_latency_two_hour.strftime("%d")), 
                                                                       str(current_time_latency_two_hour.strftime("%B")),
                                                                       str(current_time_latency_two_hour.strftime("%Y"))))
        hms_control_file.write("     Start Time: {0}:00\n".format(str(current_time_latency_two_hour.strftime("%H"))))
        hms_control_file.write("     End Date: {0} {1} {2}\n".format(str(current_time_latency_two_hour_plus_17_hours.strftime("%d")), 
                                                                     str(current_time_latency_two_hour_plus_17_hours.strftime("%B")),
                                                                     str(current_time_latency_two_hour_plus_17_hours.strftime("%Y"))))
        hms_control_file.write("     End Time: {0}:00\n".format(str(current_time_latency_two_hour_plus_17_hours.strftime("%H")))) # this will be one hour behind
        hms_control_file.write("     Time Interval: {0}\n".format(str(15)))
        hms_control_file.write("End:")
        hms_control_file.close()

    # now, let's try to run HEC-HMS with Jython
    if sys.platform == 'win32':
        # we're building the bat file that runs HEC-HMS in Windows here
        print("Running HEC-HMS on Windows.\n")
        hms_file_name = "hechms_{0}{1}{2}{3}.bat".format(current_time_latency_two_hour.year, 
                                                    current_time_latency_two_hour.strftime("%m"),
                                                    current_time_latency_two_hour.strftime("%d"),
                                                    current_time_latency_two_hour.strftime("%H"))
        hms_file = os.path.join(hrrr_directory,hms_file_name)
        with open(hms_file, "w") as open_hms_file:
            string_to_write = r'set "PATH={0}\bin\gdal;%PATH%"'.format(str(hms_directory))
            open_hms_file.write(string_to_write)
            open_hms_file.write('\n')
            string_to_write = r'set "GDAL_DRIVER_PATH={0}\bin\gdal\gdalplugins"'.format(str(hms_directory))
            open_hms_file.write(string_to_write)
            open_hms_file.write('\n')
            string_to_write = r'set "GDAL_DATA={0}\bin\gdal\gdal-data"'.format(str(hms_directory)) 
            open_hms_file.write(string_to_write)
            open_hms_file.write('\n')
            string_to_write = r'set "PROJ_LIB={0}/bin\gdal\projlib"'.format(str(hms_directory))
            open_hms_file.write(string_to_write)
            open_hms_file.write('\n')
            string_to_write = r'set "CLASSPATH={0}\hms.jar;{0}\lib\*"'.format(str(hms_directory))
            open_hms_file.write(string_to_write)
            open_hms_file.write('\n')
            hms_project_path = os.path.join(hms_model_directory,hms_project_file)
            string_to_write = r'{0} -J-Xmx12g -Djava.library.path={1}\bin;{1}\bin\gdal run_hms.py "{2}" "{3}"'.format(path_to_jython_install,hms_directory,hms_project_path, hms_run_name)
            open_hms_file.write(string_to_write)
            open_hms_file.close()

            # Open the subprocess without creating a new window
            process = subprocess.Popen(hms_file, shell=True)
            stdout, stderr = process.communicate()

    print("HEC-HMS simulation complete...\n")