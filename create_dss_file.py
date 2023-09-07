#Make TimeSeriesContainer, add values and times, then put
from hec.script import Plot, MessageBox
from hec.io import TimeSeriesContainer
from hec.heclib.dss import HecDss, DSSPathname
from hec.heclib.util import HecTime
import java
import sys
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

if time_step == 15:
  time_step_string = "15MIN"
for gage_id in gage_ids:
  myDss = HecDss.open("/mnt/d/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/Scripts/build_hms_inputs/test_dssvue.dss")
  tsc = TimeSeriesContainer()
  tsc.fullName = "//{0}/FLOW//{1}/GAGE/".format(gage_id,time_step_string)
  date_string = "{0}{1}{2}".format(time_stamp.strftime("%d"),time_stamp.strftime("%b").upper(),time_stamp.strftime("%Y"))
  time_string = "{0}00".format(time_stamp.strftime("%H"))
  start = HecTime(date_string, time_string)
  tsc.interval = time_step
  flows = [0.60]   
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