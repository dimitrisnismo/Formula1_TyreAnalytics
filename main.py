from lib2to3.pgen2 import driver
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import io


st.set_page_config(
    page_title="Formula 1 Data Analysis",
    page_icon="Images\\f1logo.png",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)
st.title("Formula 1 Tyre Analysis")
st.text(
    """

Data:
The data in this page have been retrieved from fastf1 python package. 
Races where containing at least one tyre or intermediate compound have 
been excluded.
Laps where the car in front is less than 1.1 seconds have been 
excluded.
Laps before and after pit stop have been exluded.
Laps where there is a red flag or VSC or SC have been excluded.
Lap Times have been cleaned based on IQR.Any lap time lower than
Q1-1.5*IQR or higher than  Q3+1.5*IQR have been excluded. 
Laps where the compound is na have been excluded
The number in the Compound  _1,_2,_3,_4 explain the number of set.For 
example if there are two sets of soft  tyres in a race the first
set of tyres is SOFT_1 


Data fields Description:
lapinseconds= Lap Times in seconds. 
tyredelta= difference lap by lap for lapinseconds

"""
)


def load_data():
    # Loading Data from Pickle in order to make it faster
    data = pd.read_pickle("data.pkl")
    return data


data = load_data()

# Race Filter
Race = data["Race"].unique()
race_choice = st.sidebar.selectbox("Select Race", Race)

# Driver Filter
Driver = data[data["Race"] == race_choice]["Driver"].unique()
driver_choice = st.sidebar.selectbox("Select Driver:", Driver, key=1)

# Creating a new column in the Data per Compound Type
data["TyreLife"] = data["TyreLife"].astype("int")
data["Compound_SMH"] = data.Compound.apply(lambda x: pd.Series(str(x).split("_")))[0]

# Compound smh filter
Compounds_smh = data["Compound_SMH"].unique()
selected_tyre = st.sidebar.multiselect(
    "Compound for F1 2021 Season",
    Compounds_smh,
    key=3,
    default=["SOFT", "MEDIUM", "HARD"],
)

# Colors for Tyres
domain = [
    "SOFT_1",
    "SOFT_2",
    "SOFT_3",
    "MEDIUM_1",
    "MEDIUM_2",
    "MEDIUM_3",
    "HARD_1",
    "HARD_2",
    "HARD_3",
]
range_ = [
    "#ff0000",
    "#960000",
    "#700000",
    "#e9ed00",
    "#adb000",
    "#7d8000",
    "#ffffff",
    "#b3b3b3",
    "#858585",
]
# Colors for Drivers
domain2 = [
    "HAM",
    "BOT",
    "VER",
    "PER",
    "NOR",
    "RIC",
    "LEC",
    "SAI",
    "ALO",
    "OCO",
    "RAI",
    "GIO",
    "VET",
    "STR",
    "GAS",
    "TSU",
    "MAZ",
    "MSC",
    "LAT",
    "RUS",
]
range_2 = [
    "#00d2be",
    "#00d2be",
    "#0600ef",
    "#0600ef",
    "#ff8700",
    "#ff8700",
    "#dc0000",
    "#dc0000",
    "#0090ff",
    "#0090ff",
    "#900000",
    "#900000",
    "#006f62",
    "#006f62",
    "#2b4562",
    "#2b4562",
    "#ffffff",
    "#ffffff",
    "#005aff",
    "#005aff",
]
# Colors for
domain3 = [
    "SOFT",
    "MEDIUM",
    "HARD",
]
range_3 = [
    "#ff0000",
    "#e9ed00",
    "#ffffff",
]

st.write(":heavy_minus_sign:" * 34)
st.subheader("F1 2021 Season")
st.text("Data for 2021 Season only. ")
st.altair_chart(
    alt.Chart(
        (
            data[(data["tyredelta"] < 9999) & data["Compound_SMH"].isin(selected_tyre)]
            .groupby(["Driver"])
            .mean()
        ).reset_index()
    )
    .mark_bar()
    .encode(
        alt.X("Driver", scale=alt.Scale(zero=False)),
        alt.Y("tyredelta"),
        color=alt.Color("Driver", scale=alt.Scale(domain=domain2, range=range_2)),
    )
    .properties(title="Avg LapTime Difference in seconds by Driver")
    .interactive()
    .configure_view(strokeWidth=0)
    .configure_view(strokeWidth=0),
    use_container_width=True,
)


st.altair_chart(
    (
        alt.Chart(
            (
                data[
                    (data["tyredelta"] < 9999)
                    & data["Compound_SMH"].isin(selected_tyre)
                ]
                .groupby(["Race"])
                .mean()
            ).reset_index()
        )
        .mark_bar()
        .encode(
            alt.X("Race", scale=alt.Scale(zero=False)),
            alt.Y("tyredelta"),
        )
        .properties(title="Avg LapTime Difference in seconds by Race")
        .interactive()
        .configure_view(strokeWidth=0)
    ),
    use_container_width=True,
)

st.altair_chart(
    (
        alt.Chart(
            (
                data[(data["tyredelta"] < 9999)].groupby(["Compound_SMH"]).mean()
            ).reset_index()
        )
        .mark_bar()
        .encode(
            alt.X("Compound_SMH", scale=alt.Scale(zero=False)),
            alt.Y("tyredelta"),
            color=alt.Color(
                "Compound_SMH", scale=alt.Scale(domain=domain3, range=range_3)
            ),
        )
        .properties(title="Avg LapTime Difference in seconds by Compound")
        .interactive()
        .configure_view(strokeWidth=0)
    ),
    use_container_width=True,
)


st.write(":heavy_minus_sign:" * 34)
st.subheader(race_choice + " Race Tyre Analysis")
st.text("Data for the selected Race")
# Base KPIS for race
col1_1, col1_2, col1_3 = st.columns(3)
col1_1.metric(
    "Fastest Lap",
    str(data[(data["Race"] == race_choice)]["lapinseconds"].min()) + " sec",
)
col1_2.metric(
    "Slowest Lap",
    str(data[(data["Race"] == race_choice)]["lapinseconds"].max()) + " sec",
)
col1_3.metric(
    "Avg Tyre Difference",
    str(
        round(
            data[(data["Race"] == race_choice) & (data["tyredelta"] < 9999)][
                "tyredelta"
            ].mean(),
            3,
        )
    )
    + " sec",
)

# Visualize Race Results
st.altair_chart(
    (
        alt.Chart(
            data[(data["Race"] == race_choice)][
                ["TyreLife", "Compound", "lapinseconds"]
            ]
            .groupby(["TyreLife", "Compound"])
            .mean()
            .reset_index()
        )
        .mark_line()
        .encode(
            alt.X("TyreLife", scale=alt.Scale(zero=False)),
            alt.Y("lapinseconds", scale=alt.Scale(zero=False)),
            color=alt.Color("Compound", scale=alt.Scale(domain=domain, range=range_)),
        )
        .properties(title="Avg LapTime in seconds by Compound ")
        .interactive()
        .configure_view(strokeWidth=0)
    ),
    use_container_width=True,
)

# Visualize average tyre difference
st.altair_chart(
    (
        alt.Chart(
            (
                data[(data["Race"] == race_choice) & (data["tyredelta"] < 9999)]
                .groupby(["Compound"])
                .mean()
            ).reset_index()
        )
        .mark_bar()
        .encode(
            alt.X("Compound", scale=alt.Scale(zero=False)),
            alt.Y("tyredelta"),
            color=alt.Color("Compound", scale=alt.Scale(domain=domain, range=range_)),
        )
        .properties(title="Avg LapTime Difference in seconds by Compound")
        .interactive()
        .configure_view(strokeWidth=0)
    ),
    use_container_width=True,
)


# Visualize average tyre difference per Driver
st.altair_chart(
    (
        alt.Chart(
            (
                data[(data["Race"] == race_choice) & (data["tyredelta"] < 9999)]
                .groupby(["Driver"])
                .mean()
            ).reset_index()
        )
        .mark_bar()
        .encode(
            alt.X("Driver", scale=alt.Scale(zero=False)),
            alt.Y("tyredelta"),
            color=alt.Color("Driver", scale=alt.Scale(domain=domain2, range=range_2)),
        )
        .properties(title="Avg LapTime Difference in seconds by Driver")
        .interactive()
        .configure_view(strokeWidth=0)
    ),
    use_container_width=True,
)

st.write(":heavy_minus_sign:" * 34)
st.subheader(driver_choice + " Tyre Analysis for Selected Race")
st.text("Analysis for the selected Race and Driver")
# Base KPIS for driver
col2_1, col2_2, col2_3 = st.columns(3)
col2_1.metric(
    "Fastest Lap",
    str(
        data[(data["Race"] == race_choice) & (data["Driver"] == driver_choice)][
            "lapinseconds"
        ].min()
    )
    + " sec",
)
col2_2.metric(
    "Slowest Lap",
    str(
        data[(data["Race"] == race_choice) & (data["Driver"] == driver_choice)][
            "lapinseconds"
        ].max()
    )
    + " sec",
)
col2_3.metric(
    "Avg Tyre Difference",
    str(
        round(
            data[
                (data["Race"] == race_choice)
                & (data["Driver"] == driver_choice)
                & (data["tyredelta"] < 9999)
            ]["tyredelta"].mean(),
            3,
        )
    )
    + " sec",
)


# Visualize race and selected driver Results
st.altair_chart(
    (
        alt.Chart(
            data[(data["Race"] == race_choice) & (data["Driver"] == driver_choice)][
                ["TyreLife", "Compound", "lapinseconds"]
            ]
            .groupby(["TyreLife", "Compound"])
            .mean()
            .reset_index()
        )
        .mark_line()
        .encode(
            alt.X("TyreLife", scale=alt.Scale(zero=False)),
            alt.Y("lapinseconds", scale=alt.Scale(zero=False)),
            color=alt.Color("Compound", scale=alt.Scale(domain=domain, range=range_)),
        )
        .properties(title="LapTimes ")
        .interactive()
        .configure_view(strokeWidth=0)
    ),
    use_container_width=True,
)


# Visualize average tyre difference
st.altair_chart(
    (
        alt.Chart(
            (
                data[
                    (data["Race"] == race_choice)
                    & (data["Driver"] == driver_choice)
                    & (data["tyredelta"] < 9999)
                ]
                .groupby(["Compound"])
                .mean()
            ).reset_index()
        )
        .mark_bar()
        .encode(
            alt.X("Compound", scale=alt.Scale(zero=False)),
            alt.Y("tyredelta"),
            color=alt.Color("Compound", scale=alt.Scale(domain=domain, range=range_)),
        )
        .properties(title="Avg LapTime Difference by Compound")
        .interactive()
        .configure_view(strokeWidth=0)
    ),
    use_container_width=True,
)

st.write(":heavy_minus_sign:" * 34)
st.subheader(driver_choice + " Tyre Analysis for Total Season")
st.text("Driver Analysis for 2021 Season")
# Visualize average tyre difference
st.altair_chart(
    (
        alt.Chart(
            (
                data[
                    # (data["Race"] == race_choice)
                    (data["Driver"] == driver_choice)
                    & (data["tyredelta"] < 9999)
                ]
                .groupby(["Race"])
                .mean()
            ).reset_index()
        )
        .mark_bar()
        .encode(
            alt.X("Race", scale=alt.Scale(zero=False)),
            alt.Y("tyredelta"),
            # color=alt.Color("Race", scale=alt.Scale(domain=domain, range=range_)),
        )
        .properties(title="Avg LapTime Difference by Race")
        .interactive()
        .configure_view(strokeWidth=0)
    ),
    use_container_width=True,
)

# Visualize average tyre difference
st.altair_chart(
    (
        alt.Chart(
            (
                data[
                    # (data["Race"] == race_choice)
                    (data["Driver"] == driver_choice)
                    & (data["tyredelta"] < 9999)
                ]
                .groupby(["Compound"])
                .mean()
            ).reset_index()
        )
        .mark_bar()
        .encode(
            alt.X("Compound", scale=alt.Scale(zero=False)),
            alt.Y("tyredelta"),
            color=alt.Color("Compound", scale=alt.Scale(domain=domain, range=range_)),
        )
        .properties(title="Avg LapTime Difference by Compound Total Season")
        .interactive()
        .configure_view(strokeWidth=0)
    ),
    use_container_width=True,
)
