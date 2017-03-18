from matplotlib import pyplot as plt

import pandas as pd
import numpy as np

df = pd.read_csv("processed.csv", parse_dates=["start_dt","end_dt"])

# plot hour of day

df["hod"] = df["start_dt"].apply(lambda x: x.hour)
freqs_by_hod = df["hod"].value_counts().sort_index()
plt.plot(freqs_by_hod.index, freqs_by_hod.values)
plt.grid()
plt.title("Sightings by hour of day")
plt.show()

plt.grid()
plt.title("Sightings by hour of day")

# plot hour of day by month

def determine_season(mi):
    if mi in [12,1,2]:
        return "winter"
    if mi in [3,4,5]:
        return "spring"
    if mi in [6,7,8]:
        return "summer"
    return "autumn"

df["month"] = df["start_dt"].apply(lambda x: x.month)
df["season"] = df["month"].apply(determine_season)


colors = ["blue","green","red","brown"]
seasons = ["winter", "spring", "summer", "autumn"]

for color, season in zip(colors, seasons):
    sdf = df[df["season"]==season]
    freqs_by_hod = sdf["hod"].value_counts().sort_index()
    print len(sdf)*100.0/len(df), season
    pcts_by_hod = freqs_by_hod *100.0 / freqs_by_hod.sum() ## normalization
    plt.plot(pcts_by_hod.index, pcts_by_hod.values, label=season, color=color)

plt.legend(loc='upper left')
plt.show()

def get_marker(shape):
    if shape=="triangle":
        return "v"
    if shape=="circle" or shape=="sphere" or shape=="disk" or shape=="oval":
        return "o"

    if shape=="light":
        return "*"

    if shape=="rectangle":
        return "s"

    return "x"

# map plot
from mpl_toolkits.basemap import Basemap

map = Basemap(projection='mill',lon_0=0)

map.drawcoastlines()
map.drawcountries()
map.fillcontinents(color = 'coral')
map.drawmapboundary()



lons = df["lon"].values
lats = df["lat"].values

df["marker"] = df["shape"].apply(get_marker)
xs,ys = map(lons, lats)
for x,y,m in zip(xs,ys, df["marker"].values):
    map.plot(x, y, m, markersize=5) # here it varies the colour every time

plt.show()
















## monthly
color_idx = np.linspace(0, 1, 12)
for i,month in zip(color_idx, sorted(df["month"].unique())):
    monthly_df = df[df["month"]==month]
    freqs_by_hod = monthly_df["hod"].value_counts().sort_index()
    plt.plot(freqs_by_hod.index, freqs_by_hod.values, label=month, color=plt.cm.summer(i))

plt.legend(loc='upper left')
plt.show()




# shapes -> clean rare shapes into other
# histograms


#maybe something on basemap?



