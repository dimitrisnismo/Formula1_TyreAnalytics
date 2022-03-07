import streamlit as st
import pandas as pd
import altair as alt
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

# data = create_race_data()
# data.to_pickle("data.pkl")
data = pd.read_pickle("data.pkl")

Race = data["Race"].unique()
race_choice = st.sidebar.selectbox("Select Race", Race)

Driver = data[data["Race"] == race_choice]["Driver"].unique()
driver_choice = st.sidebar.selectbox("Select Driver:", Driver)
data["TyreLife"] = data["TyreLife"].astype("int")

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

c1 = (
    alt.Chart(
        data[(data["Race"] == race_choice)][
            ["TyreLife", "Compound", "Rolling_lap_times"]
        ]
        .groupby(["TyreLife", "Compound"])
        .mean()
        .reset_index()
    )
    .mark_line()
    .encode(
        alt.X("TyreLife", scale=alt.Scale(zero=False)),
        alt.Y("Rolling_lap_times", scale=alt.Scale(zero=False)),
        color=alt.Color("Compound", scale=alt.Scale(domain=domain, range=range_)),
    )
    .properties(title="Selected Race Data ")
    .interactive()
)

st.altair_chart(c1, use_container_width=True)


c2 = (
    alt.Chart(
        data[(data["Race"] == race_choice) & (data["Driver"] == driver_choice)][
            ["TyreLife", "Compound", "Rolling_lap_times"]
        ]
        .groupby(["TyreLife", "Compound"])
        .mean()
        .reset_index()
    )
    .mark_line()
    .encode(
        alt.X("TyreLife", scale=alt.Scale(zero=False)),
        alt.Y("Rolling_lap_times", scale=alt.Scale(zero=False)),
        color=alt.Color("Compound", scale=alt.Scale(domain=domain, range=range_)),
    )
    .properties(title="Selected Driver and Race Data ")
    .interactive()
)
st.altair_chart(c2, use_container_width=True)

temp = data[(data["Race"] == race_choice) & (data["Driver"] == driver_choice)][
    [
        "Race",
        "LapNumber",
        "Compound",
        "TyreLife",
        "Team",
        "Driver",
        "lapinseconds",
        "Rolling_lap_times",
    ]
]
st.write(pd.DataFrame(temp))
# st.line_chart(
#     (
#         data[(data["Race"] == race_choice) & (data["Driver"] == driver_choice)][
#             ["Rolling_lap_times", "TyreLife", "Compound"]
#         ]
#         .groupby(["TyreLife", "Compound"])
#         .mean()
#     )
#     .reset_index()
#     .pivot(index="TyreLife", columns="Compound", values="Rolling_lap_times")
#     .reset_index()
# )
