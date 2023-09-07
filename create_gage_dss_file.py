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
    gage_dss_path = str(sys.argv[1])
    station_ids = ast.literal_eval(sys.argv[2])
    time_step = int(sys.argv[3])
    date_string = str(sys.argv[4])
    time_string = str(sys.argv[5])
    station_flow_dict = ast.literal_eval(sys.argv[6])

    if time_step == 15:
        time_step_string = "15MIN"
    for station_id in station_ids:
        myDss = HecDss.open(gage_dss_path)
        tsc = TimeSeriesContainer()
        tsc.fullName = "//{0}/FLOW//{1}/GAGE/".format(station_id,time_step_string)
        start = HecTime(date_string, time_string)
        tsc.interval = time_step
        flows = [float(station_flow_dict[station_id])]
        times = []
        for value in flows:
            times.append(start.value())
            start.add(tsc.interval)
        tsc.times = times
        tsc.values = flows
        tsc.numberValues = len(flows)
        tsc.units = "CMS"
        tsc.type = "PER-AVER"
        myDss.put(tsc)
        print "Closing DSS File"
        myDss.close()