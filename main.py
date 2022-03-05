import pandas as pd
import numpy as np
import fastf1
import seaborn as sns
import matplotlib.pyplot as plt

sns.set()

fastf1.Cache.enable_cache(r"C:\Cachef1")  # replace with your cache directory

i = 1
while i <= 50:
    race = fastf1.get_session(2021, i, "R")
    laps = race.load_laps(with_telemetry=True)
    laps = laps.sort_values(by=["Time"]).reset_index(drop=True)
    laps["followingcar"] = laps["Time"] - laps["Time"].shift(1)
    laps = laps[
        (laps["PitOutTime"].isnull())
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

    laps = laps.sort_values(
        by=["Driver", "LapNumber", "TyreLife", "Compound"]
    ).reset_index(drop=True)
    laps["tyredelta"] = np.where(
        (laps["Driver"] == laps["Driver"].shift(1))
        & (laps["Compound"] == laps["Compound"].shift(1)),
        pd.to_timedelta(laps["LapTime"] - laps["LapTime"].shift(1)),
        pd.NaT,
    )
    laps = laps.dropna()
    laps["tyredelta"] = (laps["tyredelta"] / 1000).astype("int")
    laps["lapinseconds"] = laps["LapTime"] / np.timedelta64(1, "s")
    Compounds = ["SOFT", "MEDIUM", "HARD"]

    df = pd.DataFrame()
    ##Clean lap Time per Compound
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

    pd.pivot_table(
        df, values="RollingLapTime", columns="Compound", index="TyreLife"
    ).plot(title=race.weekend.name)
    i = i + 1
# asdasf
