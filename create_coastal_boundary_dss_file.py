#Make TimeSeriesContainer, add values and times, then put
from hec.script import Plot, MessageBox
from hec.io import TimeSeriesContainer
from hec.heclib.dss import HecDss, DSSPathname
from hec.heclib.util import HecTime
import java
import sys
import ast
from datetime import datetime


if __name__ == "__main__":
    """
    This is a Jython 2.7 script that is utilizes HEC-DSSVue to create the DSS file that contains the stage boundary for inclusion in HEC-RAS. 
    The script uses HEC-DSSVue and Jython. Functions as a command line script. Currently works only for Ubuntu 20.04.

    Args:
        boundary_name (str): A representative name of the boundary or the name of the watershed for the outlet we're using (e.g., "IBWC").
        lat_of_boundary (float): The latitude of the boundary/outlet of the watershed (e.g., 26.467121).
        lon_of_boundary (float): The longitude of the boundary/outlet of the watershed (e.g., -97.393651).
        download_directory (str): The path to where the STOFS-3D Atlantic data will be downloaded and where outputs will be stored (e.g., "/mnt/d/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/Scripts/build_hms_inputs/stofs3d").
        download_stofs_data (bol): Tells the function whether or not to download the STOFS-3D Atlantic data from NOAA's servers (e.g., False).
        file_format (str): Let's the function know whether to download the STOFS-3D-Atlantic data in "grib2" or "netcdf" file format (e.g., "grib2").
        path_to_dssvue_install (str): Path to the main directory of the HEC-DSSVue installation (e.g., "/home/jlgutenson/hec-dssvue-3.3.26").
        path_to_jython_install (str): Path to the Jython jar file that is installed on the local machine (e.g., "/home/jlgutenson/jython-standalone-2.7.3.jar").
        cwd (str): Current working directory (cwd) or path to the location of the scripts being ran (e.g., "/mnt/d/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/Scripts/rtsPy").

        coastal_boundary_dss_path (str): The full path to the result DSS file that possesses the STOFS-3D Atlantic stage forecast in units of ft based upon the NAVD88 vertical reference.
        wse_list (list of float): List of float values in units of feet above NAVD88 from the STOFS-3D Atlantic forecast.
        date_string (str): Start date of forecast in strftime "%d%b%Y" format.
        time_string (str): The forecast cycle of the STOFS-3D forecast in UTC time. Currently set to 12. 
        station_id (str)= A representative name of the boundary or the name of the watershed for the outlet we're using (e.g., "IBWC").
    Returns:
        None

   """

    # pulled the start of this from 
    # https://github.com/HydrologicEngineeringCenter/DSSVue-Example-Scripts/tree/master/src
    num_args = len(sys.argv) - 1
    coastal_boundary_dss_path = str(sys.argv[1])
    wse_list = ast.literal_eval(sys.argv[2])
    date_string = str(sys.argv[3])
    time_string = str(sys.argv[4])
    station_id = str(sys.argv[5])
    time_step = 60 # we'll assume a constant 60 minutes for now

    if time_step == 60:
        time_step_string = "1HOUR"
    myDss = HecDss.open(coastal_boundary_dss_path)
    tsc = TimeSeriesContainer()
    tsc.fullName = "//{0}/STAGE//{1}/FORECAST/".format(station_id, time_step_string)
    start = HecTime(date_string, time_string)
    tsc.interval = time_step
    times = []
    for value in wse_list:
        times.append(start.value())
        start.add(tsc.interval)
    tsc.times = times
    tsc.values = wse_list
    tsc.numberValues = len(wse_list)
    tsc.units = "FT"
    tsc.type = "INST-VAL"
    myDss.put(tsc)
    print "Closing DSS File"
    myDss.close()