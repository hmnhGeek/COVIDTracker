import streamlit as st
import pandas as pd
import requests, datetime
import altair as alt
import numpy as np
import pydeck as pdk

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

    r1 = requests.get(f"https://covid-api.mmediagroup.fr/v1/history?country={country}&status=confirmed")
    
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


    r1 = requests.get(f"https://covid-api.mmediagroup.fr/v1/history?country={country}&status=deaths")
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

    r = requests.get(f"https://covid-api.mmediagroup.fr/v1/cases?country={country}")
    j = r.json()
    del j["All"]

    data = {"State": [], "Latitude": [], "Longitude": [], "Confirmed": [], "Recovered": [], "Deaths": [], "UpdateDateTime": []}

    for state in j:
        data["State"].append(state)
        data["Latitude"].append(j[state]['lat'])
        data["Longitude"].append(j[state]['long'])
        data["Confirmed"].append(j[state]['confirmed'])
        data["Recovered"].append(j[state]['recovered'])
        data["Deaths"].append(j[state]['deaths'])
        data["UpdateDateTime"].append(j[state]['updated'])

    df = pd.DataFrame(data)
    df.set_index("State", inplace=True)
    df["UpdateDateTime"] = pd.to_datetime(df["UpdateDateTime"]).dt.date
    try:
        df.drop(["Unknown"], inplace=True)
    except:
        pass

    if data["State"] != []:
        st.header("State-wise analysis")

        latlongdf = df.reset_index().rename(columns={"Longitude": "lon", "Latitude":"lat"})[['lat', 'lon']]
        latlongdf["lat"] = pd.to_numeric(latlongdf["lat"], errors='coerce')
        latlongdf["lon"] = pd.to_numeric(latlongdf["lon"], errors='coerce')
        
        st.subheader(f"Map of {country}")
        st.map(latlongdf)

        st.subheader("Cases state wise")
        st.bar_chart(df[["Confirmed", "Recovered"]], height=500)
        st.subheader("Deaths state wise")
        st.bar_chart(df[["Deaths"]], height=500)