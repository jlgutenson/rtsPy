# lifted from here and augmented to suit my needs:
# https://github.com/HydrologicEngineeringCenter/data-retrieval-scripts
import urllib.request
from datetime import datetime
import os

def download(download_directory, date, cycle, download_met_data):
    if download_met_data == True:
        if not os.path.isdir(os.path.split(download_directory)[0]):
            os.mkdir(os.path.split(download_directory)[0])
        if not os.path.isdir(download_directory):
            os.mkdir(download_directory)
        for hour in range(1, 19):
            url = "http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.{0}/conus/hrrr.t{1}z.wrfsubhf{2}.grib2".format(date, cycle, str(hour).zfill(2))
            print(url)
            filename = url.split("/")[-1]
            f = open(download_directory + os.sep + filename, 'wb')
            f.write(urllib.request.urlopen(url).read())
    else:
        pass
    return(download_directory)
