# builtin imports
from datetime import datetime, timedelta, timezone

# third party imports
import pandas as pd

#http://rths.us/?state=graphcsv&config=config.json&from=2023-10-06%2000:00:00&to=2023-10-20%2000:00:00&seriesid=2032&title=Water%20level%20in%20Surface%20Water%20using%20NAVD88

# where going to look one day back in time
current_time = datetime.now(timezone.utc)
station = "TWDB 3" 
station_flow_dict = {}


if __name__ == "__main__":

    # where going to look one day back in time
    start = current_time - timedelta(days=7)
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
        streamflow = s.values[0][0]
        station_flow_dict[station] = streamflow
    except:
        station_flow_dict[station] = 0

    print(streamflow)