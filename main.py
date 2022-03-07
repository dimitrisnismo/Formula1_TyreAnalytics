import streamlit as st
import pandas as pd
from tyre_analysis import create_race_data

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


st.write("Results:", data)
