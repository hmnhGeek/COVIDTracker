import streamlit as st
import pandas as pd
import requests, datetime
import altair as alt
import numpy as np

from util import get_line_chart

sidebar = st.sidebar

def create_data(json):
    data = []

    for i in j:
        d = {"country": i}
        d.update(j[i]["All"])
        data.append(d)

    return data

r = requests.get("https://covid-api.mmediagroup.fr/v1/cases")
j = r.json()

maindf = pd.DataFrame(create_data(j))
st.title("COVID Tracker")
st.dataframe(maindf)

col1, col2 = st.beta_columns(2)

col1.subheader("Top 10 in confirmed cases")
col1.bar_chart(maindf[["country", "confirmed"]].set_index("country").sort_values("confirmed").drop("Global").tail(10))
col2.subheader("Top 10 in deaths")
col2.bar_chart(maindf[["country", "deaths"]].set_index("country").sort_values("deaths").drop("Global").tail(10))

country = sidebar.selectbox(
    "Country",
    maindf["country"].unique()
)

if country:
    sd = sidebar.date_input(
        "Start Date",
        datetime.datetime.now() - datetime.timedelta(days=7)
    )
    ed = sidebar.date_input(
        "End Date",
        datetime.datetime.now()
    )

    sd = sd.strftime("%Y-%m-%d")
    ed = ed.strftime("%Y-%m-%d")

    d_range = pd.date_range(start=sd,end=ed)

    r1 = requests.get(f"https://covid-api.mmediagroup.fr/v1/history?country={country}&status=deaths")
    
    hist = dict(r1.json()["All"]["dates"])
    history = {}
    
    for record in hist:
        if record in d_range:
            history.update({record: hist[record]})

    confirmeddf = pd.DataFrame.from_dict(history, orient="index", columns=["Confirmed"])
    confirmeddf.index.name = "Date"
    confirmeddf.reset_index(inplace=True)

    st.subheader(f"Number of confirmed cases in {country}")
    st.write(get_line_chart(confirmeddf, "#ff0000", "Date", "Confirmed"))


    r1 = requests.get(f"https://covid-api.mmediagroup.fr/v1/history?country={country}&status=confirmed")
    hist = dict(r1.json()["All"]["dates"])
    history = {}
    
    for record in hist:
        if record in d_range:
            history.update({record: hist[record]})

    deaddf = pd.DataFrame.from_dict(history, orient="index", columns=["Deaths"])
    deaddf.index.name = "Date"
    deaddf.reset_index(inplace=True)

    st.subheader(f"Number of deaths in {country}")
    st.write(get_line_chart(deaddf, "gray", "Date", "Deaths"))