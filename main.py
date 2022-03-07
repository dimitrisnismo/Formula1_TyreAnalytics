import streamlit as st
import pandas as pd
import altair as alt

# from tyre_analysis import create_race_data

st.set_page_config(
    page_title="Formula 1 Data Analysis",
    page_icon="Images\\f1logo.png",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)
st.title("Formula 1 Tyre Analysis")

# data.to_pickle('data.pkl')
# data = create_race_data()
data = pd.read_pickle("data.pkl")
Driver = data["Driver"].unique()
# Team = data["Team"].unique()
Race = data["Race"].unique()

race_choice = st.sidebar.selectbox("Select Race", Race)
# team_choice = st.sidebar.selectbox("Select Team", Team)
driver_choice = st.sidebar.selectbox("Select Driver:", Driver)
data["TyreLife"] = data["TyreLife"].astype("int")


c = (
    alt.Chart(data[(data["Race"] == race_choice) & (data["Driver"] == driver_choice)])
    .mark_line()
    .encode(
        alt.X("TyreLife", scale=alt.Scale(zero=False)),
        alt.Y("Rolling_lap_times", scale=alt.Scale(zero=False)),
        color="Compound",
    )
)

st.altair_chart(c, use_container_width=True)

st.line_chart(
    (
        data[(data["Race"] == race_choice) & (data["Driver"] == driver_choice)][
            ["Rolling_lap_times", "TyreLife", "Compound"]
        ]
        .groupby(["TyreLife", "Compound"])
        .mean()
    )
    .reset_index()
    .pivot(index="TyreLife", columns="Compound", values="Rolling_lap_times")
    .reset_index()
)

st.write(
    "Results:",
    data[(data["Driver"] == driver_choice) & (data["Race"] == race_choice)][
        ["Race", "Driver", "LapNumber", "Compound", "TyreLife", "Rolling_lap_times"]
    ],
)
pd.pivot_table()
