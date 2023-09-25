# lifted from here and augmented to suit my needs:
# https://github.com/HydrologicEngineeringCenter/data-retrieval-scripts
import urllib.request
from datetime import datetime
import os
import time

def download(download_directory, date, cycle, download_met_data):
    if download_met_data == True:
        if not os.path.isdir(os.path.split(download_directory)[0]):
            os.mkdir(os.path.split(download_directory)[0])
        if not os.path.isdir(download_directory):
            os.mkdir(download_directory)
        url_list = []
        file_dict = {}
        need_to_finish_list = []
        # loop through the links until you download every file
        for hour in range(1, 19):
            url = "http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.{0}/conus/hrrr.t{1}z.wrfsubhf{2}.grib2".format(date, cycle, str(hour).zfill(2))
            print(url)
            url_list.append(url)
            filename = url.split("/")[-1]
            filepath = download_directory + os.sep + filename
            file_dict[url] = filepath
            f = open(filepath, 'wb')
            while os.path.getsize(filepath) == 0:
                try:
                    f.write(urllib.request.urlopen(url,  timeout=120).read())
                    time.sleep(15) # in seconds         
                except:
                    print(f"Need to try redownloading {filename}")
                    time.sleep(5)
                    pass
            # set the file permissions for the bash scripts
            execute_permission = 0o755
            # Set the execute permissions on the file
            os.chmod(filepath, execute_permission)
            f.close()   
        
    else:
        pass
    return(download_directory)