import pandas as pd
import numpy as np
from nominatim import Nominatim
import geocoder
import pickle 
import os
import re
from datetime import datetime, timedelta
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()


def datestr_to_datetime(datestr):
    for fmt in ["%m/%d/%y","%m/%d/%y %H:%M"]:
        try:
            return datetime.strptime(datestr, fmt)
        except ValueError:
            continue

def infer_duration_in_seconds(duration_description):
    text = str(duration_description).lower()
    for metric, secs in zip(["second", "s","segundo","minute","m","min","hour",  "h"],
                           [       1,   1,        1,      60, 60,   60,  3600, 3600]):
        regex = "\s*(\d+)\+?\s*{}s?".format(metric)
        res = re.findall(regex,text)
        if len(res)>0:
            return int(float(res[0]) * secs)
    return None

def get_end_time(start_time, seconds):
    if pd.isnull(seconds):
        return None
    else:
        return start_time + timedelta(seconds=seconds)



def geocode_lonlat(location_name):

    global georesults_cache
    global gi
    gi = gi + 1
    if gi % 10 == 0:
        print("Geocoding {}th row".format(gi))

    if location_name not in georesults_cache.keys():
        try:
            res = geocoder.google(location_name).latlng
        except Exception, e:
            print "query failed for {} with error {}".format(location_name, e)
            res = None
        georesults_cache[location_name]= res

    georesult1 = georesults_cache[location_name]
    if not georesult1 or len(georesult1)<2:
        print "Could not geocode {}".format(location_name)
        return None
    else:

        return georesult1[1], georesult1[0]


geolocator = Nominatim()
georesults_cache = pickle.load(open("cache_google.pickle","rb"))
gi = 0


df = pd.read_csv("raw_data.csv")

# 1. extract data regarding time
df["start_dt"] = df["datestr"].apply(datestr_to_datetime)
df["duration_secs"] = df["duration_description"].apply(infer_duration_in_seconds)
df["end_dt"] = df.apply(lambda x: get_end_time(x["start_dt"], x["duration_secs"]), axis=1)

percentage_parsed_duration = len(df[~pd.isnull(df.duration_secs)])*100.0/len(df)
print ("Could infer the duration for {} of the records".format(percentage_parsed_duration))

df = df.dropna()

# 2. extract data regarding location


df["location_name"] = df.apply(lambda x:  str(x["state"]) + " " + str(x["city"]), axis=1)
df["lon_lat"] = df["location_name"].apply(geocode_lonlat)

percentage_parsed_location = len(df[~pd.isnull(df.lon_lat)])*100.0/len(df)
print ("Could infer the location for {} of the records".format(percentage_parsed_location))
df = df.dropna()
df["lon"] = df["lon_lat"].apply(lambda x: x[0])
df["lat"] = df["lon_lat"].apply(lambda x: x[1])

df["shape"] = df["shape"].fillna("Unknown")
df["shape"] = df["shape"].apply(lambda x:x.lower())

#df[["start","end","lon","lat","Shape"]].dropna().to_csv("processed_qgis.csv",index=False)
del df["lon_lat"]
df.to_csv("processed.csv")
