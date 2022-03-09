import pandas as pd
import numpy as np
import fastf1
import seaborn as sns
import matplotlib.pyplot as plt

# import streamlit as st

sns.set()

fastf1.Cache.enable_cache("C:\\Cachef1") 
 # replace with your cache directory
# List of Teams ['Alpine F1 Team', 'Mercedes', 'AlphaTauri', 'Alfa Romeo',
#        'Williams', 'Ferrari', 'Haas F1 Team', 'McLaren', 'Red Bull',
#        'Aston Martin']
# List of Drivers ['VER', 'HAM', 'BOT', 'LEC', 'GAS', 'RIC', 'NOR', 'SAI', 'ALO',
#        'STR', 'PER', 'GIO', 'TSU', 'RAI', 'RUS', 'OCO', 'LAT', 'MSC',
#        'MAZ', 'VET']


def load_race_data():
    df = pd.DataFrame()
    count = 1
    while count <= 22:
        race = fastf1.get_session(2021, count, "R")
        laps = race.load_laps(with_telemetry=True)
        laps["Race"] = race.weekend.name
        df = pd.concat([df, laps])
        count += 1
    return df


def remove_wet_races(data):
    wet_races = (
        data[["Race", "Compound", "Driver"]]
        .groupby(["Race", "Compound"])
        .count()
        .reset_index()
    )
    wet_races = pd.pivot_table(
        wet_races, index="Race", columns="Compound", values="Driver"
    ).reset_index()
    wet_races = wet_races.fillna(0)
    wet_races = wet_races[(wet_races["WET"] == 0) & (wet_races["INTERMEDIATE"] == 0)]
    data = pd.merge(data, wet_races[["Race"]], on="Race")
    data = data[data["Compound"] != "UNKNOWN"]
    return data


def add_difference_from_the_car_in_front(data):
    # Sort Values by Following Car
    data = data.sort_values(by=["Race", "Time"]).reset_index(drop=True)
    ##Add column with the delta between 2 cars in the beginning of the lap
    data["followingcar"] = data["Time"] - data["Time"].shift(1)
    return data


def filter_dataframe(data):
    # Filter Dataframe where
    # 1.there is no pit in or pit out in this lap
    # 2.The track is Clear
    # 3.there is no car ahead less than 1 second
    # 4.Only Dry Tyres
    # 5.Keeping only necessery Columns
    data = data[
        (data["PitOutTime"].isnull())
        & (data["PitInTime"].isnull())
        & (data["TrackStatus"] == "1")
        & (data["followingcar"] > pd.Timedelta(1.1, unit="s"))
    ][
        [
            "Race",
            "LapTime",
            "LapNumber",
            "Compound",
            "TyreLife",
            "Team",
            "Driver",
        ]
    ]
    return data


def add_tyre_time_difference(data):
    # Creating a column with the laptime delta between the laps
    data = pd.DataFrame(data)
    data = data.sort_values(
        by=["Race", "Driver", "LapNumber", "TyreLife", "Compound"]
    ).reset_index(drop=True)
    data["tyredelta"] = np.where(
        (data["Driver"] == data["Driver"].shift(1))
        & (data["Compound"] == data["Compound"].shift(1))
        & (data["Race"] == data["Race"].shift(1)),
        (data["lapinseconds"]) - (data["lapinseconds"].shift(1)),
        np.nan,
    )
    data["tyredelta"] = data["tyredelta"].fillna(9999)
    return data


def add_laptime_to_seconds(data):
    # Calculating Lap Times in Seconds
    data["lapinseconds"] = data["LapTime"] / np.timedelta64(1, "s")
    return data


def q1(x):
    return x.quantile(0.25)


def q3(x):
    return x.quantile(0.75)


def calculate_quartiles(data):
    f = {"lapinseconds": [q1, q3]}
    quartiles = (
        data[["Race", "Compound", "lapinseconds"]]
        .groupby(["Race", "Compound"])
        .agg(f)
        .reset_index()
    )
    quartiles.columns = ["Race", "Compound", "Q1", "Q3"]
    return quartiles


def clean_outlier_lap_times(data):
    # Clean Lap Times by Compound and per Race using Quartiles
    var = 1.5
    quartiles = calculate_quartiles(data)
    data = pd.merge(data, quartiles, on=["Race", "Compound"], how="left")
    data["IQR"] = data["Q3"] - data["Q1"]
    data = data[
        ~(
            (data["lapinseconds"] < (data["Q1"] - var * data["IQR"]))
            | (data["lapinseconds"] > (data["Q3"] + var * data["IQR"]))
        )
    ]
    data = data.drop(columns=["Q1", "Q3", "IQR"])
    return data


def remove_na_rows(data):
    # dropping row where containing na
    data = data.dropna()
    return data


def rolling_lap_times(data):
    data = data.reset_index(drop=True)
    data = data.sort_values(by=["Race", "Driver", "LapNumber", "Compound", "TyreLife"])
    data_temp = (
        (
            data.groupby(["Race", "Driver", "LapNumber", "Compound", "TyreLife"])
            .rolling(window=5, min_periods=1)
            .mean()
            .reset_index()
        )
        .fillna(data["lapinseconds"])
        .rename(columns={"lapinseconds": "Rolling_lap_times"})
    )

    data = pd.merge(
        data,
        data_temp[
            ["Race", "Driver", "LapNumber", "Compound", "TyreLife", "Rolling_lap_times"]
        ],
        on=["Race", "Driver", "LapNumber", "Compound", "TyreLife"],
        how="left",
        validate="1:1",
    )
    return data


def calculate_set_of_tyres(data):
    data["setoftyres"] = data.groupby(["Race", "Driver", "Compound"]).cumcount()
    data["setoftyres"] = np.where(
        (data["Race"] == data["Race"].shift(1))
        & (data["Driver"] == data["Driver"].shift(1))
        & (data["Compound"] == data["Compound"].shift(1))
        & (data["TyreLife"] > data["TyreLife"].shift(1)),
        0,
        1,
    )
    data["setoftyres"] = data.groupby(["Race", "Driver"])["setoftyres"].cumsum()
    data["setoftyres"] = data["setoftyres"].astype("str")
    data["Compound"] = data["Compound"] + "_" + data["setoftyres"]
    return data


def create_race_data():
    data = load_race_data()
    data = remove_wet_races(data)
    data = add_difference_from_the_car_in_front(data)
    data = filter_dataframe(data)
    data = add_laptime_to_seconds(data)
    data = clean_outlier_lap_times(data)
    data = remove_na_rows(data)
    data = add_tyre_time_difference(data)
    # data = rolling_lap_times(data)
    data = calculate_set_of_tyres(data)
    return data
