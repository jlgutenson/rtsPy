# built in imports
from datetime import datetime, timedelta, timezone

# third party imports
import requests
import json
import pandas as pd

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

            # where going to look one day one month, just in case the station is down
            start = current_time - timedelta(days=30)
            end = current_time
            target_time = current_time - timedelta(hours=2)

            start = start.strftime("%Y-%m-%d")
            end = end.strftime("%Y-%m-%d")

            # pull down list of stations and use the site name to find site id
            df = pd.read_csv("http://rths.us/getsites.cgi", sep='|')
            df = df[df['SiteName'].str.contains(station)]
            siteid = df.iloc[0]['SiteID']

            # RTHS URL
            url = "http://rths.us/"
            url_state = "graphcsv"
            url_config = "config.json"
            seriesid = "2032" # this is the varaible id
            title = "Water%20level%20in%20Surface%20Water%20using%20NAVD88"

            full_url = f"http://rths.us/?state=graphcsv&config={url_config}&from={start}&to={end}&seriesid={seriesid}&siteid={siteid}&title={title}"

            # read in data and set the time stamp as the index
            df = pd.read_csv(full_url).dropna()
            df['UTC Date'] = pd.to_datetime(df['UTC Date'], utc=True)
            df = df.reset_index().set_index('UTC Date')
            df = df.drop(['index'], axis=1)  
            df = df.dropna()
            
            try:
                # select the data we want to use in our model
                # find the last reported value assuming something is better than nothing
                s = df.iloc[df.index.get_indexer([target_time], method='nearest')]
                stage = s.values[0][0]
                streamflow = 6.31*(stage + 0.4)**1.79
                station_flow_dict[station] = streamflow
            except:
                station_flow_dict[station] = 0

    return station_flow_dict