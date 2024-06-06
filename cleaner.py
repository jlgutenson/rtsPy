# native imports
import os
import time
from datetime import datetime, timezone, timedelta


def remove_old_forecasts(forecast_directory, watershed, forecast_filename, forecast_age_to_filter):
    """
    Pass this function a path and it will clear out forecasts of a certain age.

    """
    # list the stored forecasts in the forecast directory
    days = os.listdir(forecast_directory)

    # pull the current time in UTC
    current_time = datetime.now(timezone.utc).timestamp()

    # loop through folders and test age of forecast files
    for day in days:
        day_dir = os.path.join(forecast_directory, day)
        hours = os.listdir(day_dir)
        for hour in hours:
            day_and_hour_string = day + hour
            element = datetime.strptime(day_and_hour_string,"%Y%m%d%H")
            tuple = element.timetuple()
            forecast_time = time.mktime(tuple)
            forecast_age = current_time - forecast_time # forecast age in seconds
            forecast_age = forecast_age / 60 / 60 / 24
            if forecast_age >= forecast_age_to_filter:
                path_to_forecast = os.path.join(day_dir,hour,watershed,forecast_filename)
                if os.path.exists(path_to_forecast):
                    os.remove(path_to_forecast)

    return


if __name__ == "__main__":
    forecast_directory = "/mnt/d/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/Scripts/build_hms_inputs/hrrr_subhourly"
    watershed = "IBWC"
    forecast_filename = "Forecast_1.dss"
    forecast_age_to_filter = 30
    remove_old_forecasts(forecast_directory, watershed, forecast_filename, forecast_age_to_filter)