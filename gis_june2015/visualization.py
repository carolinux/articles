df =pd.read_csv("ufo_data.csv")

# hour of day
df["hod"] = df["start"].apply(lambda x: x.hour)
df["hod"] = df["start"].apply(lambda x: x[-6:])
df.hod
df["hod"] = df["start"].apply(lambda x: x[-8:-6])
df.hod
df["hod"] = df["start"].apply(lambda x: int(x[-8:-6]))
df.hod.value_counts()

# shapes -> clean rare shapes into other
# histograms


#maybe something on basemap?



