import pandas as pd
from nominatim import Nominatim
import pickle 
import os
import sys
import re
import shutil 
from datetime import datetime, timedelta
import atexit

DEFAULT_DURATION=10 # seconds
DUMP="dump.file"
shutil.copyfile(DUMP, DUMP+".bak")
SHAPE = "shape"
LOCATION = "location"

results = pickle.load(open(DUMP,"rb")) if os.path.exists(DUMP) else {}
valid_keys=[]
for k,v in results.iteritems():
    if v is not None:
        valid_keys.append(k)
print "Already have results for {} ({} places)".format(valid_keys, len(valid_keys))
#sys.exit(0)
gi = 0

def infer_duration_in_seconds(text):
    text = str(text)
    for metric,mult in zip(["second","s","Second","segundo","minute","m","min","Minute","hour","h","Hour"],[1,1,1,1,60,60,60,3600,3600,3600]):
        regex = "\s*(\d+)\+?\s*{}s?".format(metric)
        res = re.findall(regex,text)
        if len(res)>0:
            return int(float(res[0]) * mult)
    return None

def save():
    global DUMP_FILE
    global results
    print "save file"
    pickle.dump(results, open(DUMP,"wb"))

atexit.register(save)
infer_duration_in_seconds.total = 0
infer_duration_in_seconds.unparsed = 0
infer_duration_in_seconds.unparseds= []
def geocode(g, name,col="lat"):
    global gi
    global results
    gi = gi + 1
    print gi,name 
    if name not in results.keys() or results[name] is None:
        try:
            res = g.query(name)
        except Exception, e:
            print "query failed for {} with error {}".format(name,e)
            res = None
        results[name]= res
    else:
        print "{} exists in keys".format(name)
    if results[name] is None or len(results[name])==0:
        print "no results for {}".format(name)
        return None
    else:
        print results[name][0][col]
        return results[name][0][col]

geolocator = Nominatim()

#print geolocator.query("Paris")
df = pd.read_csv(sys.argv[1])
df["dt"] = df.apply(lambda x:x["datestr"],axis=1)
df["start"] = df.dt.apply(lambda x: datetime.strptime(x,"%Y-%m-%d %H:%M:%S"))
df["duration_secs"] = df["duration"].apply(infer_duration_in_seconds)
df["end"] = df.apply(lambda x:x["start"]+timedelta(seconds=x["duration_secs"]),axis=1)
print df.head()
df[LOCATION] = df.apply(lambda x: str(x["state"])+" "+str(x["city"]), axis=1)
for col in ["lat","lon"]:
    df[col] = df[LOCATION].apply(lambda x: geocode(geolocator,x,col))
print df.head()
df[SHAPE] = df[SHAPE].fillna("Unknown")
df[SHAPE] = df[SHAPE].apply(lambda x:x.lower())
df[["start","end","lon","lat","Shape"]].dropna().to_csv("processed_qgis.csv",index=False)
df.to_csv("processed.csv")
