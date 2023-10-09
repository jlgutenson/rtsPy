import requests
import json

def get_data(station_assimilation_list, current_time):
    """
    Downloads data from RTHS stations for assimilation into HEC-HMS

    Args:
        station_assimilation_list (list): A list of stations to assimilate into the HEC-HMS simulation (e.g., ['TWDB-01']).
        current_time (timemstamp): A timestamp for the current time, in UTC. 

    Returns:
        dict: station_flow_dict - A dictionary indexed by the station ID and the most recent streamflow value

    """
    # the output of this is station_flow_dict that contains
    # all of the flows we'll use to initialize our model
    station_flow_dict = {}

    for station in station_assimilation_list:
        # this video really helped figure out how to do this:
        # https://www.youtube.com/watch?v=qxj7EXYeNls
        # had to hard code a lot of this to use the USIBWC data
        if station == "08470200":
            # getting the most recent streamflow from the USIBWC
            # this has tended to be about 2 hours behind the simulation time step but its a start
            day = current_time.strftime("%Y")
            month = current_time.strftime("%m")
            year = current_time.strftime("%d")
            url = 'https://waterdata.ibwc.gov/AQWebportal/Data/DatasetStats?dataset=6755&sort=Name-asc&page=1&pageSize=100&group=&filter=&interval=Latest&date={0}-{1}-{2}&endDate=&calendar=1&virtual=true'.format(day,month,year)
            response=requests.get(url, verify=False)
            json_data = response.json()
            streamflow_dict = dict(json_data)
            streamflow_data_list = streamflow_dict['Data']
            for streamflow_data in streamflow_data_list:
                # note that units are cms
                if streamflow_data['Name'] == '1 - Latest Discharge (cms)':
                    streamflow = streamflow_data['DisplayValue']
                    station_flow_dict[station] = streamflow
        
        else:
            # hard coding this for the time being
            station_flow_dict[station] = 1.00

    return station_flow_dict