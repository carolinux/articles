from  urllib import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
from itertools import chain
import pandas as pd
import re

def can_cast_as_dt(dateStr, fmt):
    try:
        datetime.strptime(dateStr, fmt)
        return True
    except:
        return False

def standardize_dt(dateStr):
    for fmt in ["%m/%d/%y","%m/%d/%y %H:%M"]:
        try:
            return datetime.strptime(dateStr, fmt)
        except ValueError:
            continue


def get_data_from_url(url):
    print "Processing {}".format(url)
    data = []
    source = BeautifulSoup(urlopen(url), "html5lib")
    for row in source('tr'):
        if not row('td'):
            continue # header row
        row_data = row('td')
        # parse the date string and convert it to standard format
        datetime = standardize_dt(row_data[0].text) 
        location = row_data[1].text
        location2 = row_data[1].text
        shape = row_data[3].text
        duration_descr = row_data[4].text
        data.append((datetime, location, location2, shape, duration_descr))
    return data

#def flatmap(f, items):
    #return chain.from_iterable(map(f, items))

def infer_duration_in_seconds(text):
    # try different regexps to extract the total seconds
    metric_text = ["second","s","Second","segundo","minute","m","min","Minute","hour","h","Hour"]
    metric_seconds = [1,1,1,1,60,60,60,3600,3600,3600]
    for metric,mult in zip(metric_text,metric_seconds):
        regex = "\s*(\d+)\+?\s*{}s?".format(metric)
        res = re.findall(regex,text)
        if len(res)>0:
            return int(float(res[0]) * mult)
    return None


base_url = "http://www.nuforc.org/webreports/"
index_url = "http://www.nuforc.org/webreports/ndxevent.html"

source = BeautifulSoup(urlopen(index_url), "html5lib")
monthly_urls = map(lambda x: (x.text,base_url+x['href']),source('a')) # get all the links 
monthly_urls = filter(lambda x: can_cast_as_dt(x[0],"%m/%Y") , monthly_urls)[:12] # get all the links that have a text like 06/2015

last_year_ufos = list(chain(*map(lambda x: get_data_from_url(x[1]), monthly_urls)))
ufos_df = pd.DataFrame(last_year_ufos, columns=["datestr","city","state","shape","duration_description"])
ufos_df["secs"] = ufos_df.duration_description.apply(infer_duration_in_seconds)
print len(ufos_df)
print len(ufos_df.dropna())
ufos_df.to_csv("test.csv",index=False)
