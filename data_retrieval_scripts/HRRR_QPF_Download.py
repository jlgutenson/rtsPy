# lifted from here and augmented to suit my needs:
# https://github.com/HydrologicEngineeringCenter/data-retrieval-scripts
import urllib.request
from datetime import datetime
import os

def download(download_directory, start_date):
    date = start_date.strftime('%Y%m%d')
    cycle = start_date.strftime("%H")
    destination = os.path.join(download_directory, date, cycle)
    if not os.path.isdir(os.path.split(destination)[0]):
        os.mkdir(os.path.split(destination)[0])
    if not os.path.isdir(destination):
        os.mkdir(destination)
    for hour in range(1, 19):
        url = "http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.{0}/conus/hrrr.t{1}z.wrfsubhf{2}.grib2".format(date, cycle, str(hour).zfill(2))
        print(url)
        filename = url.split("/")[-1]
        f = open(destination + os.sep + filename, 'wb')
        f.write(urllib.request.urlopen(url).read())
    return(destination)
