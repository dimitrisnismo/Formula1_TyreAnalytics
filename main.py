import pandas as pd
import numpy as np
import fastf1
import seaborn as sns
import matplotlib.pyplot as plt

sns.set()

fastf1.Cache.enable_cache(r"C:\Cachef1")  # replace with your cache directory

i = 1

race = fastf1.get_session(2021, i, "R")
laps = race.load_laps(with_telemetry=True)
laps = laps.sort_values(by=["Time"]).reset_index(drop=True)

##Add column with the delta between 2 cars in the beginning of the lap
laps["followingcar"] = laps["Time"] - laps["Time"].shift(1)

# Filter only cars where begin racing with soft Tyres
laps = pd.merge(
    laps,
    laps[(laps["Compound"] == "SOFT") & (laps["LapNumber"] == 1)][["Driver"]],
    on="Driver",
)

# Filter Dataframe where
# 1.there is no pit in or pit out in this lap
# 2.The track is Clear
# 3.there is no car ahead less than 1 second
# 4.Only Dry Tyres
# 5.Keeping only necessery Columns
laps = laps[
    (laps["PitOutTime"].isnull())
    & (laps["PitInTime"].isnull())
    & (laps["TrackStatus"] == "1")
    & (laps["followingcar"] > pd.Timedelta(1.1, unit="s"))
    & (laps["Compound"] != "INTERMEDIATE")
    & (laps["Compound"] != "WET")
][
    [
        "LapTime",
        "LapNumber",
        "Compound",
        "TyreLife",
        "Team",
        "Driver",
    ]
]

# Creating a column with the tyre delta between the laps
laps = laps.sort_values(by=["Driver", "LapNumber", "TyreLife", "Compound"]).reset_index(
    drop=True
)
laps["tyredelta"] = np.where(
    (laps["Driver"] == laps["Driver"].shift(1))
    & (laps["Compound"] == laps["Compound"].shift(1)),
    pd.to_timedelta(laps["LapTime"] - laps["LapTime"].shift(1)),
    pd.NaT,
)
laps["tyredelta"] = (laps["tyredelta"] / 1000).astype("int")

# Drop rows where there are containing na values
laps = laps.dropna()

# Calculating Lap Times in Seconds
laps["lapinseconds"] = laps["LapTime"] / np.timedelta64(1, "s")

# The Tyre Compounds
Compounds = ["SOFT", "MEDIUM", "HARD"]

##Clean lap Time per Compound
# For each compound using Quartile Analysis removing Outliers
# Using Rolling 5 lap Times in order to normalize data and to be easier to analyze
df = pd.DataFrame()
for compound in Compounds:
    df_compound = laps[laps["Compound"] == compound]
    Q1 = df_compound["lapinseconds"].quantile(0.25)
    Q3 = df_compound["lapinseconds"].quantile(0.75)
    IQR = Q3 - Q1
    df_compound = df_compound[
        ~(
            (df_compound["lapinseconds"] < (Q1 - 1.5 * IQR))
            | (df_compound["lapinseconds"] > (Q3 + 1.5 * IQR))
        )
    ]
    df_compound = (
        df_compound[["lapinseconds", "TyreLife"]]
        .groupby(["TyreLife"])
        .mean()
        .reset_index(drop=False)
    )
    df_compound["RollingLapTime"] = (
        df_compound["lapinseconds"]
        .rolling(window=5, min_periods=1)
        .mean()
        .fillna(df_compound["lapinseconds"])
    )
    df_compound["Compound"] = compound

    df = pd.concat([df, df_compound])


##Visualizing Results
pd.pivot_table(df, values="RollingLapTime", columns="Compound", index="TyreLife").plot(
    title=race.weekend.name
)
i = i + 1
# asdasf
