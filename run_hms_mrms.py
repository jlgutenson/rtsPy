# native imports
from datetime import datetime, timezone, timedelta
import os
import shutil
import subprocess
import sys
import pathlib

# local imports
from data_retrieval_scripts.MRMS_QPE_Download import download

def run(simulation_length,
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
        download_met_data):

    # # variables that will change with different runs
    # # length of the simulation, in days
    # simulation_length = 7
    # # path to folder where each hours MRMS data will be downloaded
    # name_of_gridded_directory = "mrms_pass2" # name of the directory storing each forecast
    # # path to the folder containing the Vortex install, the HEC tool for converted gridded data into DSS format
    # path_to_vortex_install = r"D:\Gutenson_RATES\TWDB-FIF-LRGVDC\2023\Scripts\build_hms_inputs\vortex-0.11.0"
    # # path to Jython executable
    # path_to_jython_install = r"C:\jython2.7.3\bin\jython.exe"
    # # area defining the geographic extent of the HEC-HMS model
    # hec_hms_clip_shp = r"D:\Gutenson_RATES\TWDB-FIF-LRGVDC\2023\1.2.2.2.2\Models\HEC_HMS_411beta16\1_RVD\1_HEC-HMS_Model\RVD_NAD8310171\gis\RVD_83_1\RVD_83_1.shp"
    # # DSS file to output the gridded meteorlogy data into
    # vortex_dss_file = "RVDJune2018_JLG_scripted_1.dss"
    # # type of meteorological data we're using
    # met_forcing = "MRMS"
    # # variable in the meteorlogy data containing precipitation
    # variables = 'MultiSensor_QPE_01H_Pass2_altitude_above_msl'
    # # path to the directory containing the watershed's HEC-HMS model
    # hms_model_directory = r"C:\Users\Joseph Gutenson\Desktop\Gutenson_RATES\TWDB-FIF-LRGVDC\2023\1.2.2.2.2\Models\HEC_HMS_411beta16\1. RVD\1. HEC-HMS Model\RVD_NAD8310171"
    # # name of the HEC-HMS control file we're updating
    # hms_control_file_name = "June2018.control"
    # # the time-step of the HEC-HMS simulation, in minutes
    # hms_time_step = 15
    # # path to the directory containing HEC-HMS
    # hms_directory = r"D:\Gutenson_RATES\TWDB-FIF-LRGVDC\2023\Scripts\build_hms_inputs\HEC-HMS-4.11-beta.16"
    # # name of the hms project file 
    # hms_project_file = "RVD_NAD8310171.hms"
    # # name of the hms simulation to run
    # hms_run_name = "June 2018"
    # # do we need to download the met data to create the DSS file?
    # download_met_data = True

    # pull the current time in UTC
    current_time = datetime.now(timezone.utc)
    current_time_latency_one_hour = current_time - timedelta(hours=1)

    current_time_latency_one_week = current_time_latency_one_hour - timedelta(days=simulation_length)

    # make the directory to store the forecast
    date_directory = "{0}{1}{2}{3}".format(current_time_latency_one_hour.year, 
                                           current_time_latency_one_hour.strftime("%m"),
                                           current_time_latency_one_hour.strftime("%d"),
                                           current_time_latency_one_hour.strftime("%H"))
    mrms_directory = os.path.join(os.getcwd(),name_of_gridded_directory,date_directory)
    
    # determine if we're downloading the MRMS data. Don't want this to repeat for 
    # every watershed we run
    if download_met_data == True:
        # see if MRMS directory already exists and if so, remove it
        if os.path.exists(mrms_directory):
            shutil.rmtree(mrms_directory)
            os.mkdir(mrms_directory)
        else:
            os.mkdir(mrms_directory)

        # download the past week of MRMS precip
        # ideally these two dates would be an hour apart and 
        # we would initialize from the previous hour
        # that needs work though
        start = datetime(current_time_latency_one_week.year, current_time_latency_one_week.month,
                        current_time_latency_one_week.day, current_time_latency_one_week.hour, 0)
        end = datetime(current_time_latency_one_hour.year, current_time_latency_one_hour.month,
                        current_time_latency_one_hour.day, current_time_latency_one_hour.hour, 0)
        hour = timedelta(hours=1)
        download(start, end, hour, mrms_directory)
    else:
        pass

    # check to see if gridded DSS file exists and if so, remove it and copy over the new one
    if os.path.exists(os.path.join(hms_model_directory,vortex_dss_file)):          
        os.remove(os.path.join(hms_model_directory,vortex_dss_file))

    # now that we have our MRMS data, we need to create our DSS file
    # check what system you're using to see if I need a batch or sh file to run Vortex with Jython
    vortex_dss_file_path = os.path.join(hms_model_directory,vortex_dss_file)
    if sys.platform == 'win32':
        # we're building the bat file that runs Vortex in Windows here
        print("Running Vortex on Windows.\n")
        vortex_file_name = "vortex_{0}{1}{2}{3}.bat".format(current_time_latency_one_hour.year, 
                                                    current_time_latency_one_hour.strftime("%m"),
                                                    current_time_latency_one_hour.strftime("%d"),
                                                    current_time_latency_one_hour.strftime("%H"))
        vortex_file = os.path.join(mrms_directory,vortex_file_name)
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
            string_to_write = '{0} -J-Xmx12g -Djava.library.path=%VORTEX_HOME%\\bin;%VORTEX_HOME%\\bin\gdal met_data_import.py "{1}" "{2}" "{3}" {4} "{5}"\n'.format(path_to_jython_install,mrms_directory,hec_hms_clip_shp,vortex_dss_file_path,variables,met_forcing)
            open_vortex_file.write(string_to_write)
            open_vortex_file.close()

    elif sys.platform == 'linux' or sys.platform == 'linux2':
        # we're building the bat file that runs Vortex in Linux here
        print("Running Vortex on Linux.\n")
        vortex_file_name = "vortex_{0}{1}{2}{3}.sh".format(current_time_latency_one_hour.year, 
                                                           current_time_latency_one_hour.strftime("%m"),
                                                           current_time_latency_one_hour.strftime("%d"),
                                                           current_time_latency_one_hour.strftime("%H"))
        vortex_file = os.path.join(mrms_directory,vortex_file_name)
        with open(vortex_file, "w") as open_vortex_file:
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

            string_to_write = '$JAVA_VORTEX_PATH -Xmx12g -Djava.library.path="$JAVA_VORTEX_LIB_PATH" -classpath "$CLASS_PATH" org.python.util.jython met_data_import.py "{1}" "{2}" "{3}" {4} "{5}" \n'.format(path_to_vortex_install, mrms_directory, hec_hms_clip_shp, vortex_dss_file_path, variables,met_forcing, path_to_jython_install)
            open_vortex_file.write(string_to_write)
            open_vortex_file.close()

    # Open the subprocess without creating a new window
    process = subprocess.Popen(vortex_file, shell=True)
    stdout, stderr = process.communicate()

    # and also update our HEC-HMS control specifications
    # check if old control file exists and delete it accordingly
    if os.path.exists(os.path.join(hms_model_directory,hms_control_file_name)):
        os.remove(os.path.join(hms_model_directory,hms_control_file_name))
        
    print("\nCreating the HEC-HMS control file.\n")
    with open(os.path.join(hms_model_directory,hms_control_file_name), "w") as hms_control_file:
        hms_control_file.write("Control: {0}\n".format(hms_control_file_name[:-8]))
        hms_control_file.write("     Last Modified Date: 21 July 2023\n")
        hms_control_file.write("     Last Modified Time: 17:26:17\n")
        hms_control_file.write("     Version: 4.11\n")
        hms_control_file.write("     Time Zone ID: America/Chicago\n")
        hms_control_file.write("     Time Zone GMT Offset: -21600000\n")
        hms_control_file.write("     Start Date: {0} {1} {2}\n".format(str(current_time_latency_one_week.strftime("%d")), 
                                                                       str(current_time_latency_one_week.strftime("%B")),
                                                                       str(current_time_latency_one_week.strftime("%Y"))))
        hms_control_file.write("     Start Time: {0}:00\n".format(str(current_time_latency_one_week.strftime("%H"))))
        current_time_latency_two_hours = current_time_latency_one_hour - timedelta(hours=1)
        hms_control_file.write("     End Date: {0} {1} {2}\n".format(str(current_time_latency_two_hours.strftime("%d")), 
                                                                     str(current_time_latency_two_hours.strftime("%B")),
                                                                     str(current_time_latency_two_hours.strftime("%Y"))))
        hms_control_file.write("     End Time: {0}:00\n".format(str(current_time_latency_two_hours.strftime("%H")))) # this will be one hour behind
        hms_control_file.write("     Time Interval: {0}\n".format(str(15)))
        hms_control_file.write("End:")
        hms_control_file.close()

    # now, let's try to run HEC-HMS with Jython
    if sys.platform == 'win32':
        # we're building the bat file that runs HEC-HMS in Windows here
        print("Running HEC-HMS on Windows.\n")
        hms_file_name = "hechms_{0}{1}{2}{3}.bat".format(current_time_latency_one_hour.year, 
                                                    current_time_latency_one_hour.strftime("%m"),
                                                    current_time_latency_one_hour.strftime("%d"),
                                                    current_time_latency_one_hour.strftime("%H"))
        hms_file = os.path.join(mrms_directory,hms_file_name)
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

    # now, let's try to run HEC-HMS with Jython
    elif sys.platform == 'linux' or sys.platform == 'linux2':
        # we're building the bat file that runs HEC-HMS in Windows here
        print("Running HEC-HMS on Linux.\n")
        hms_file_name = "hechms_{0}{1}{2}{3}.sh".format(current_time_latency_one_hour.year, 
                                                    current_time_latency_one_hour.strftime("%m"),
                                                    current_time_latency_one_hour.strftime("%d"),
                                                    current_time_latency_one_hour.strftime("%H"))
        hms_file = os.path.join(mrms_directory,hms_file_name)
        with open(hms_file, "w") as open_hms_file:
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
            string_to_write = '$JAVA_HMS_PATH -Xmx12g -Djava.library.path=$HMS_DIR/bin:$HMS_DIR/bin/gdal org.python.util.jython run_hms.py "{0}" "{1}"'.format(hms_project_path, hms_run_name, path_to_jython_install)
            open_hms_file.write(string_to_write)
            open_hms_file.close()

    # Open the subprocess without creating a new window
    process = subprocess.Popen(hms_file, shell=True)
    stdout, stderr = process.communicate()

    print("HEC-HMS simulation complete...\n")

    return(current_time_latency_one_week, current_time_latency_two_hours, mrms_directory)