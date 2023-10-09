
import urllib.request
from datetime import datetime, timezone, timedelta
import os
import time
import sys

def download(download_directory, date, cycle, download_met_data):
    """
    Downloads HRRR grib2 files from NOAA NOMADS.The original script was lifted from here and augmented to suit my needs: 
    https://github.com/HydrologicEngineeringCenter/data-retrieval-scripts

    Args:
        download_directory (str): The path to where the user has specified the forecasts will be downloaded (e.g., "/home/jlgutenson/rtsPy/hrrr_subhourly") 
        date (str): The date of the forecast being downloaded in '%Y%m%d' format. 
        cycle (str): The UTC cycle of the forecast "%H". 
        download_met_data (bool): Tells the script whether or not to proceed with the download (e.g., True).

    Returns:
        str: download_directory - Path to where the HRRR forecasts are being stored.

    """
    start_time = datetime.now(timezone.utc)
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
            running_time = 0
            while os.path.getsize(filepath) == 0 and running_time < 45:
                current_time = datetime.now(timezone.utc)
                difference = current_time-start_time
                running_time = difference.total_seconds()/60 # running time in minutes
                try:
                    f.write(urllib.request.urlopen(url,  timeout=120).read())
                    time.sleep(15) # in seconds         
                except:
                    print(f"Need to try redownloading {filename}")
                    time.sleep(5)
                    pass
            f.close()   
            # end the program if the download is taking too long
            if running_time >= 45:
                sys.exit("This download took too long, let's wait on the next forecast")
            # set the file permissions for the bash scripts
            execute_permission = 0o755
            # Set the execute permissions on the file
            os.chmod(filepath, execute_permission)
    else:
        pass
    return(download_directory)