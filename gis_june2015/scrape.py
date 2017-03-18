from datetime import datetime
from  urllib import urlopen

from bs4 import BeautifulSoup
import pandas as pd


def can_cast_as_dt(dateStr, fmt):
    try:
        datetime.strptime(dateStr, fmt)
        return True
    except:
        return False


def get_data_from_url(url):
    print "Processing {}".format(url)
    data = []
    source = BeautifulSoup(urlopen(url), "html5lib")
    for row in source('tr'):
        if len(row.select('td')) == 0:
            continue # header row has <th></th> children
        row_data = row.select('td')
        datestr = row_data[0].text
        location = row_data[1].text
        location2 = row_data[2].text
        shape = row_data[3].text
        duration_descr = row_data[4].text
        data.append((datestr, location, location2, shape, duration_descr))
    return data


base_url = "http://www.nuforc.org/webreports/"
index_url = "http://www.nuforc.org/webreports/ndxevent.html"

source = BeautifulSoup(urlopen(index_url), "html5lib")
# 1. get the urls for each monthly page
monthly_urls = []
for link in source.select("a"):
    link_text = link.text
    if can_cast_as_dt(link_text, "%m/%Y"): #link text is of the format 02/2015
        monthly_url = base_url + link['href']
        monthly_urls.append(monthly_url)


# 2. get the data for the last 12 months
last_year_data = []
for url in monthly_urls[:12]:
    monthly_data = get_data_from_url(url)
    last_year_data = last_year_data + monthly_data

# 3. turn raw data into dataframe and save to csv
ufos_df = pd.DataFrame(last_year_data, columns=["datestr", "city", "state", "shape", "duration_description"])
ufos_df.to_csv("raw_data.csv",index=False,encoding='utf-8')

