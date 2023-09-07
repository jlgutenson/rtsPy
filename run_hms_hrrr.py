# native imports
from datetime import datetime, timezone, timedelta
import os
import shutil
import subprocess
import sys
import pathlib

# local imports
from data_retrieval_scripts.HRRR_QPF_Download import download
from data_retrieval_scripts.pull_streamflow_data import get_data

def run(watershed,
        simulation_length,
        name_of_gridded_directory,
        path_to_vortex_install, 
        path_to_jython_install,
        hec_hms_clip_shp, 
        vortex_dss_file,
        met_forcing,
        variables,
        hms_model_directory, 
        hms_control_file_name,
        hms_time_step,
        hms_directory, 
        hms_project_file,
        hms_run_name,
        download_met_data,
        forecast,
        hms_forecast_name,
        hms_output_file,
        path_to_dssvue_install,
        station_assimilation_list):

    """
    # variables that will change with different runs
    # length of the simulation, in hours
    simulation_length = 18
    # path to folder where each hours HRRR data will be downloaded
    name_of_gridded_directory = "hrrr_subhourly" # name of the directory storing each forecast
    # path to the folder containing the Vortex install, the HEC tool for converted gridded data into DSS format
    path_to_vortex_install = "/home/vortex-0.11.0"
    # path to Jython executable
    path_to_jython_install = "/home/jython.jar"
    # area defining the geographic extent of the HEC-HMS model
    hec_hms_clip_shp = "/path/to/RVD_83_1.shp"
    # DSS file to output the gridded meteorlogy data into
    vortex_dss_file = "RVDJune2018_JLG_scripted_1.dss"
    # type of meteorological data we're using
    met_forcing = "HRRR"
    # variable in the meteorlogy data containing precipitation
    variables = 'Total_precipitation_surface_15_Minute_Accumulation'
    # path to the directory containing the watershed's HEC-HMS model
    hms_model_directory = "/hms_directory/RVD_NAD8310171"
    # name of the HEC-HMS control or forecast file we're updating
    hms_control_file_name = "June2018.control"
    # the time-step of the HEC-HMS simulation, in minutes
    hms_time_step = 15
    # path to the directory containing HEC-HMS
    hms_directory = "/hms_dir/HEC-HMS-4.11"
    # name of the hms project file 
    hms_project_file = "RVD_NAD8310171.hms"
    # name of the hms simulation to run
    hms_run_name = "June 2018"
    # do we need to download the met data to create the DSS file?
    download_met_data = True
    # do we need to run HEC-HMS as a forecast?
    forecast = True
    # name of the HMS forecast we're running
    hms_forecast_name = "Forecast 1"
    # Name of the DSS file that HEC-HMS will store outputs in
    hms_output_file = "Forecast_1.dss"
    # Where are we storing our DSSVue installation?
    path_to_dssvue_install = "/home/jlgutenson/hec-dssvue-3.3.26"
    # List of the gage stations that we're assimilating
    station_assimilation_list = ['TWDB-01']
    """

    # pull the current time in UTC
    current_time = datetime.now(timezone.utc)
    current_time_latency_two_hour = current_time - timedelta(hours=2)

    current_time_latency_two_hour_plus_17_hours = current_time_latency_two_hour + timedelta(hours=17)


    # directory to store the forecast
    date = current_time_latency_two_hour.strftime('%Y%m%d')
    cycle = current_time_latency_two_hour.strftime("%H")
    hrrr_directory = os.path.join(os.getcwd(), name_of_gridded_directory, date, cycle)

    
    # see if HRRR directory already exists and if so, remove it
    if os.path.exists(hrrr_directory) and download_met_data == True:
        shutil.rmtree(hrrr_directory)
        os.mkdir(hrrr_directory)
    else:
        pass

    # download the HRRR precip and point the script to the download folder
    hrrr_directory = download(hrrr_directory, date, cycle, download_met_data)

    # check to see if gridded DSS file exists and if so, remove it and copy over the new one
    if os.path.exists(os.path.join(hms_model_directory,vortex_dss_file)):          
        os.remove(os.path.join(hms_model_directory,vortex_dss_file))
    
    # also delete the temp.dss file if where running HRRR
        # check to see if gridded DSS file exists and if so, remove it and copy over the new one
    if os.path.exists(os.path.join(hms_model_directory,"temp.dss")) and met_forcing == "HRRR":          
        os.remove(os.path.join(hms_model_directory,"temp.dss"))

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


    elif sys.platform == 'linux' or sys.platform == 'linux2':
        # we're building the bat file that runs Vortex in Linux here
        print("Running Vortex on Linux.\n")
        vortex_file_name = "vortex_{0}{1}{2}{3}_{4}.sh".format(current_time_latency_two_hour.year, 
                                                               current_time_latency_two_hour.strftime("%m"),
                                                               current_time_latency_two_hour.strftime("%d"),
                                                               current_time_latency_two_hour.strftime("%H"),
                                                               watershed)
        vortex_file = os.path.join(hrrr_directory,vortex_file_name)
        with open(vortex_file, "w") as open_vortex_file:
            string_to_write = '#!/bin/bash'
            open_vortex_file.write(string_to_write)
            open_vortex_file.write('\n')

            string_to_write = 'VORTEX_HOME="{0}"\n'.format(str(path_to_vortex_install))
            open_vortex_file.write(string_to_write)

            string_to_write = 'export PATH="$VORTEX_HOME/bin:$VORTEX_HOME/bin/gdal:$PATH"'
            open_vortex_file.write(string_to_write)
            open_vortex_file.write('\n')

            string_to_write = 'export GDAL_DATA="$VORTEX_HOME/bin/gdal/gdal-data"' 
            open_vortex_file.write(string_to_write)
            open_vortex_file.write('\n')

            string_to_write = 'export PROJ_LIB="$VORTEX_HOME/bin/gdal/proj"'
            open_vortex_file.write(string_to_write)
            open_vortex_file.write('\n')

            string_to_write = 'JAVA_VORTEX_PATH="$VORTEX_HOME/jre/bin/java"' 
            open_vortex_file.write(string_to_write)
            open_vortex_file.write('\n')

            string_to_write = 'JAVA_VORTEX_LIB_PATH="$VORTEX_HOME/bin:$VORTEX_HOME/bin/gdal"'
            open_vortex_file.write(string_to_write)
            open_vortex_file.write('\n')

            string_to_write = 'CLASS_PATH="{0}:$VORTEX_HOME/lib/*"'.format(path_to_jython_install)
            open_vortex_file.write(string_to_write)
            open_vortex_file.write('\n')

            LD_LIBRARY_PATH = os.environ.get('LD_LIBRARY_PATH')
            if LD_LIBRARY_PATH==None:
                string_to_write = 'export LD_LIBRARY_PATH="$VORTEX_HOME/bin/gdal"'.format(LD_LIBRARY_PATH)
            else:
                string_to_write = 'export LD_LIBRARY_PATH="$VORTEX_HOME/bin/gdal:${0}"'.format(LD_LIBRARY_PATH)
            open_vortex_file.write(string_to_write)
            open_vortex_file.write('\n')

            string_to_write = '$JAVA_VORTEX_PATH -Xmx12g -Djava.library.path="$JAVA_VORTEX_LIB_PATH" -classpath "$CLASS_PATH" org.python.util.jython met_data_import.py "{0}" "{1}" "{2}" "{3}" "{4}" "{5}"\n'.format(hrrr_directory,
                                                                                                                                                                                                                hec_hms_clip_shp,
                                                                                                                                                                                                                vortex_dss_file_path,
                                                                                                                                                                                                                variables,
                                                                                                                                                                                                                met_forcing,
                                                                                                                                                                                                                watershed)
            open_vortex_file.write(string_to_write)
            open_vortex_file.close()

            # Open the subprocess without creating a new window
            process = subprocess.Popen(vortex_file, shell=True)
            stdout, stderr = process.communicate()


    # let's create the DSS file that HMS needs to assimilate our gage observations
    # we're doing this using the HEC-DSSVue software and Jython
    # the lines below are building a bash script that will then be ran
    print("Creating DSS file with HEC-DSSVue.")
    if len(station_assimilation_list) > 0:
        # this function will pull the observed streamflow from our assimilation gages
        station_flow_dict = get_data(station_assimilation_list, current_time)
        gage_dss_path = os.path.join(hms_model_directory,"stations_{0}.dss".format(watershed))
        # delete the old DSS file, they corrupt very easily otherwise
        if os.path.exists(gage_dss_path):          
            os.remove(gage_dss_path)
        if sys.platform == 'linux' or sys.platform == 'linux2':
            dss_file_name = "dss_{0}{1}{2}{3}_{4}.sh".format(current_time_latency_two_hour.year, 
                                                                current_time_latency_two_hour.strftime("%m"),
                                                                current_time_latency_two_hour.strftime("%d"),
                                                                current_time_latency_two_hour.strftime("%H"),
                                                                watershed)
            dss_file = os.path.join(hrrr_directory,dss_file_name)
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

                date_string = "{0}{1}{2}".format(current_time_latency_two_hour.strftime("%d"),current_time_latency_two_hour.strftime("%b").upper(),current_time_latency_two_hour.strftime("%Y"))
                time_string = "{0}00".format(current_time_latency_two_hour.strftime("%H"))

                string_to_write = '$JAVA_DSS_PATH -Xmx12g -Djava.library.path="$JAVA_DSS_LIB_PATH" -classpath "$CLASS_PATH" org.python.util.jython create_gage_dss_file.py "{0}" "{1}" "{2}" "{3}" "{4}" "{5}"'.format(gage_dss_path,
                                                                                                                                                                                                                       station_assimilation_list,
                                                                                                                                                                                                                       hms_time_step,
                                                                                                                                                                                                                       date_string,
                                                                                                                                                                                                                       time_string,
                                                                                                                                                                                                                       station_flow_dict)
                open_dss_file.write(string_to_write)
                open_dss_file.write('\n') 
                open_dss_file.close()
        # Open the subprocess without creating a new window
        process = subprocess.Popen(dss_file, shell=True)
        stdout, stderr = process.communicate()

    print("Updating the HEC-HMS forecast file.\n")
    # we just need to update the dates that are present in the forecast file
    hec_hms_forecast_file_path = os.path.join(hms_model_directory,"forecast",hms_control_file_name)
    # Read lines using readlines()
    open_file = open(hec_hms_forecast_file_path, 'r')
    Lines = open_file.readlines()
    open_file.close()
    # writing to file changing only the date in the forecast file
    open_file = open(hec_hms_forecast_file_path, 'w')
    for line in Lines:
        if "Start Date:" in line:
            line= "\tStart Date: {0} {1} {2}\n".format(str(current_time_latency_two_hour.strftime("%d")), 
                                                    str(current_time_latency_two_hour.strftime("%B")),
                                                    str(current_time_latency_two_hour.strftime("%Y")))
            open_file.writelines(line)
        elif "Start Time:" in line:
            line = "\tStart Time: {0}:00\n".format(str(current_time_latency_two_hour.strftime("%H")))
            open_file.writelines(line)
        elif "Forecast Date:" in line:
            line= "\tForecast Date: {0} {1} {2}\n".format(str(current_time.strftime("%d")), 
                                                    str(current_time.strftime("%B")),
                                                    str(current_time.strftime("%Y")))
            open_file.writelines(line)
        elif "Forecast Time:" in line:
            line = "\tForecast Time: {0}:00\n".format(str(current_time.strftime("%H")))
            open_file.writelines(line)
        elif "End Date:" in line:
            line= "\tEnd Date: {0} {1} {2}\n".format(str(current_time_latency_two_hour_plus_17_hours.strftime("%d")), 
                                                    str(current_time_latency_two_hour_plus_17_hours.strftime("%B")),
                                                    str(current_time_latency_two_hour_plus_17_hours.strftime("%Y")))
            open_file.writelines(line)
        elif "End Time:" in line:
            line = "\tEnd Time: {0}:00\n".format(str(current_time_latency_two_hour_plus_17_hours.strftime("%H")))
            open_file.writelines(line)
        else:
            open_file.writelines(line)
    open_file.close()

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
            string_to_write = r'{0} -J-Xmx12g -Djava.library.path={1}\bin;{1}\bin\gdal run_hms.py "{2}" "{3}" "{4}"'.format(path_to_jython_install,hms_directory,hms_project_path, hms_run_name, forecast)
            open_hms_file.write(string_to_write)
            open_hms_file.close()

            # Open the subprocess without creating a new window
            process = subprocess.Popen(hms_file, shell=True)
            stdout, stderr = process.communicate()
    
        # now, let's try to run HEC-HMS with Jython
    elif sys.platform == 'linux' or sys.platform == 'linux2':
        # we're building the bat file that runs HEC-HMS in Windows here
        print("Running HEC-HMS on Linux.\n")
        hms_file_name = "hechms_{0}{1}{2}{3}_{4}.sh".format(current_time_latency_two_hour.year, 
                                                            current_time_latency_two_hour.strftime("%m"),
                                                            current_time_latency_two_hour.strftime("%d"),
                                                            current_time_latency_two_hour.strftime("%H"),
                                                            watershed)
        hms_file = os.path.join(hrrr_directory,hms_file_name)
        with open(hms_file, "w") as open_hms_file:
            string_to_write = '#!/bin/bash'
            open_hms_file.write(string_to_write)
            open_hms_file.write('\n')
            string_to_write = 'export PATH="{0}/bin/gdal:$PATH"'.format(str(hms_directory))
            open_hms_file.write(string_to_write)
            open_hms_file.write('\n')
            string_to_write = 'HMS_DIR="{0}"'.format(str(hms_directory))
            open_hms_file.write(string_to_write)
            open_hms_file.write('\n')
            string_to_write = 'export GDAL_DATA="{0}/bin/gdal/gdal-data"'.format(str(hms_directory)) 
            open_hms_file.write(string_to_write)
            open_hms_file.write('\n')
            string_to_write = 'export PROJ_LIB="{0}/bin/gdal/proj"'.format(str(hms_directory))
            open_hms_file.write(string_to_write)
            open_hms_file.write('\n')
            string_to_write = 'JAVA_HMS_PATH="{0}/jre/bin/java"'.format(str(hms_directory)) 
            open_hms_file.write(string_to_write)
            open_hms_file.write('\n')
            string_to_write = 'export CLASSPATH="{0}/hms.jar:{0}/lib/*"'.format(str(hms_directory),path_to_jython_install)
            open_hms_file.write(string_to_write)
            open_hms_file.write('\n')
            hms_project_path = os.path.join(hms_model_directory,hms_project_file)
            string_to_write = '$JAVA_HMS_PATH -Xmx12g -Djava.library.path=$HMS_DIR/bin:$HMS_DIR/bin/gdal org.python.util.jython run_hms.py "{0}" "{1}" {3}'.format(hms_project_path, hms_forecast_name, path_to_jython_install, forecast)
            open_hms_file.write(string_to_write)
            open_hms_file.close()

            # Open the subprocess without creating a new window
            process = subprocess.Popen(hms_file, shell=True)
            stdout, stderr = process.communicate()

            # create a new results folder in the forecast directory and save our forecast
            where_to_store_results = os.path.join(hrrr_directory,watershed)
            if os.path.exists(os.path.join(where_to_store_results)):
                try:
                    os.remove(os.path.join(where_to_store_results,hms_output_file))
                except:
                    pass
            else:
                os.mkdir(where_to_store_results)
            path_to_results = os.path.join(hms_model_directory,hms_output_file)
            shutil.move(path_to_results, where_to_store_results)

    print("HEC-HMS simulation complete...\n")
    return(current_time_latency_two_hour, current_time_latency_two_hour_plus_17_hours, hrrr_directory)