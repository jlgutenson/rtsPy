#Make TimeSeriesContainer, add values and times, then put
from hec.script import Plot, MessageBox
from hec.io import TimeSeriesContainer
from hec.heclib.dss import HecDss, DSSPathname
from hec.heclib.util import HecTime
import java
import sys
import ast
from datetime import datetime

# pulled the start of this from 
# https://github.com/HydrologicEngineeringCenter/DSSVue-Example-Scripts/tree/master/src
"""
# list of gage IDs
gage_ids = ["08470200", "TWDB-03"]
# time step of the data, currently matches the simulation time-step
time_step = 15
# Date of the observation we're going to assimilate.
time_stamp = datetime(2023, 9, 5, 17, 0, 0)
"""

if __name__ == "__main__":

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