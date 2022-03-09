from lib2to3.pgen2 import driver
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from fastf1.ergast import load

from tyre_analysis import create_race_data

# from tyre_analysis import create_race_data

st.set_page_config(
    page_title="Formula 1 Data Analysis",
    page_icon="Images\\f1logo.png",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)
st.title("Formula 1 Tyre Analysis")
@st.cache()
def load_data():
    data = create_race_data()
    return data

data=load_data()
# data.to_pickle("data.pkl")
# data = pd.read_pickle("data.pkl")

Race = data["Race"].unique()
race_choice = st.sidebar.selectbox("Select Race", Race)

Driver = data[data["Race"] == race_choice]["Driver"].unique()
driver_choice = st.sidebar.selectbox("Select Driver:", Driver)
data["TyreLife"] = data["TyreLife"].astype("int")


# race_choice = "Abu Dhabi Grand Prix"
# driver_choice = "ALO"


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


st.subheader("Race Tyre Analysis")
# Base KPIS for race
col3, col4, col5 = st.columns(3)
col3.metric(
    "Fastest Lap",
    str(data[(data["Race"] == race_choice)]["lapinseconds"].min()) + " sec",
)
col4.metric(
    "Slowest Lap",
    str(data[(data["Race"] == race_choice)]["lapinseconds"].max()) + " sec",
)
col5.metric(
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
c1 = (
    alt.Chart(
        data[(data["Race"] == race_choice)][["TyreLife", "Compound", "lapinseconds"]]
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
    .properties(title="Selected Race Data ")
    .interactive()
)

st.altair_chart(c1, use_container_width=True)

# Visualize average tyre difference
c3 = (
    alt.Chart(
        (
            data[
                (data["Race"] == race_choice)
                # & (data["Driver"] == driver_choice)
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
    .properties(title="Avg laptime Difference per Lap")
    .interactive()
    # .mark_text(
    #     align="left",
    #     baseline="middle",
    #     dx=3,  # Nudges text to right so it doesn't appear on top of the bar
    # )
    # .encode(text="tyredelta")
)


st.altair_chart(c3, use_container_width=True)
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

# Visualize average tyre difference per Driver
c7 = (
    alt.Chart(
        (
            data[
                (data["Race"] == race_choice)
                # & (data["Driver"] == driver_choice)
                & (data["tyredelta"] < 9999)
            ]
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
    .properties(title="Avg laptime Difference per Lap by Driver")
    .interactive()
    # .mark_text(
    #     align="left",
    #     baseline="middle",
    #     dx=3,  # Nudges text to right so it doesn't appear on top of the bar
    # )
    # .encode(text="tyredelta")
)


st.altair_chart(c7, use_container_width=True)


st.subheader("Driver Analysis for Selected Race")
# Base KPIS for driver
col1, col2, col3 = st.columns(3)
col1.metric(
    "Fastest Lap",
    str(
        data[(data["Race"] == race_choice) & (data["Driver"] == driver_choice)][
            "lapinseconds"
        ].min()
    )
    + " sec",
)
col2.metric(
    "Slowest Lap",
    str(
        data[(data["Race"] == race_choice) & (data["Driver"] == driver_choice)][
            "lapinseconds"
        ].max()
    )
    + " sec",
)
col3.metric(
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
c2 = (
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
    .properties(title="Selected Driver and Race Data ")
    .interactive()
)
st.altair_chart(c2, use_container_width=True)


# Visualize average tyre difference
c6 = (
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
    .properties(title="Avg laptime Difference per Lap")
    .interactive()
    # .mark_text(
    #     align="left",
    #     baseline="middle",
    #     dx=3,  # Nudges text to right so it doesn't appear on top of the bar
    # )
    # .encode(text="tyredelta")
)


st.altair_chart(c6, use_container_width=True)
