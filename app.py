import streamlit as st
import pandas as pd
import requests, datetime
import altair as alt
import numpy as np
import pydeck as pdk

from util import get_line_chart

sidebar = st.sidebar
sidebar.title("Sidebar panel")

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

st.markdown(
    """Welcome to the COVID Tracker web application. This page allows you to analyse worldwide spread
        of the coronavirus. Here, you can find information about **number cases, deaths and recovered** for all
        countries in the world, plus, you could find information about the **vaccination drive**. 
        This application is created by ***Himanshu Sharma***. Visit https://github.com/hmnhGeek for more projects.
    """
)

col1, col2 = st.beta_columns(2)
col11, col22 = st.beta_columns(2)

col1.subheader("Top 10 in confirmed cases")
top_confirmed = maindf[["country", "confirmed"]].set_index("country").sort_values("confirmed").drop("Global").tail(10)
col1.write(alt.Chart(top_confirmed.reset_index()).mark_bar().encode(
    x=alt.X('country:O', sort=None),
    y='confirmed:Q',
    tooltip=["country", "confirmed"]
).interactive())

col2.subheader("Top 10 in deaths")
top_deaths = maindf[["country", "deaths"]].set_index("country").sort_values("deaths").drop("Global").tail(10)
col2.write(alt.Chart(top_deaths.reset_index()).mark_bar().encode(
    x=alt.X('country:O', sort=None),
    y='deaths:Q',
    tooltip=["country", "deaths"]
).interactive())

col11.subheader("Lowest 10 in confirmed cases")
low_confirmed = maindf[["country", "confirmed"]].set_index("country").sort_values("confirmed").drop("Global").head(10)
col11.write(alt.Chart(low_confirmed.reset_index()).mark_bar().encode(
    x=alt.X('country:O', sort=None),
    y='confirmed:Q',
    tooltip=["country", "confirmed"]
).interactive())

col22.subheader("Lowest 10 in deaths")
low_deaths = maindf[["country", "deaths"]].set_index("country").sort_values("deaths").drop("Global").head(10)
col22.write(alt.Chart(low_deaths.reset_index()).mark_bar().encode(
    x=alt.X('country:O', sort=None),
    y='deaths:Q',
    tooltip=["country", "deaths"]
).interactive())

r3 = requests.get("https://covid-api.mmediagroup.fr/v1/vaccines")
j3 = r3.json()

vaccine_data = {"State": [], "Administered": [], "People Vaccinated": [], "People Partially Vaccinated": [], "Population": []}

for i in j3:
    vaccine_data["State"].append(i)
    vaccine_data["Administered"].append(j3[i]["All"]["administered"])
    vaccine_data["People Vaccinated"].append(j3[i]["All"]["people_vaccinated"])    
    vaccine_data["People Partially Vaccinated"].append(j3[i]["All"]["people_partially_vaccinated"])   
    try:
        vaccine_data["Population"].append(j3[i]["All"]["population"])
    except:
        vaccine_data["Population"].append(None)

vaccine_df = pd.DataFrame(vaccine_data)
st.header("Vaccination data (World)")
st.dataframe(vaccine_df)
st.dataframe(vaccine_df.describe())

st.subheader("Top 10 countries in vaccination drive")
column1, column2, column3 = st.beta_columns(3)

column1.write(alt.Chart(vaccine_df.sort_values(by=["Administered"]).tail(10)).mark_bar().encode(
    x=alt.X('State:O', sort=None),
    y=alt.Y("Administered"),
    tooltip=["State", "Administered"]
))
column2.write(alt.Chart(vaccine_df.sort_values(by=["People Vaccinated"]).tail(10)).mark_bar().encode(
    x=alt.X('State:O', sort=None),
    y=alt.Y("People Vaccinated"),
    tooltip=["State", "People Vaccinated"]
))
column3.write(alt.Chart(vaccine_df.sort_values(by=["People Partially Vaccinated"]).tail(10)).mark_bar().encode(
    x=alt.X('State:O', sort=None),
    y=alt.Y("People Partially Vaccinated"),
    tooltip=["State", "People Partially Vaccinated"]
))

st.subheader("Countries with people only partially vaccinated")
st.dataframe(vaccine_df[(vaccine_df["People Vaccinated"] == 0) & (vaccine_df["People Partially Vaccinated"] != 0)].drop("People Vaccinated", axis=1))


country = sidebar.selectbox(
    "Country",
    ["None"]+maindf["country"].unique().tolist()
)

if country != "None":
    st.header(f"Analysis for {country}")

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

        st.subheader(f"Confirmed cases in states of {country}")
        st.write(alt.Chart(df[["Confirmed"]].reset_index()).mark_bar().encode(
            x=alt.X('State', sort=alt.SortField(field="Confirmed", order="descending")),
            y="Confirmed",
            tooltip=["State", "Confirmed"]
        ).properties(width=700, height=500))
        st.subheader(f"Recovered cases in states of {country}")
        st.write(alt.Chart(df[["Recovered"]].reset_index()).mark_bar().encode(
            x=alt.X('State', sort=alt.SortField(field="Recovered", order="descending")),
            y="Recovered",
            tooltip=["State", "Recovered"]
        ).properties(width=700, height=500))
        st.subheader(f"Deaths in states of {country}")
        st.write(alt.Chart(df[["Deaths"]].reset_index()).mark_bar().encode(
            x=alt.X('State', sort=alt.SortField(field="Deaths", order="descending")),
            y="Deaths",
            tooltip=["State", "Deaths"]
        ).properties(width=700, height=500))

        r4 = requests.get(f"https://covid-api.mmediagroup.fr/v1/vaccines?country={country}")
        j = r4.json()

        try:
            del j["All"]
        except: pass

        data = {"State": [], "Administered": []}
        for i in j:
            data["State"].append(i)
            data["Administered"].append(j[i]["administered"])

        vdf = pd.DataFrame(data)

        st.header(f"Vaccination analysis for {country}")
        st.subheader("Statistical analysis of the data")
        st.dataframe(vdf.describe().transpose())

        st.subheader(f"Vaccines administered in different states of {country}")
        st.write(alt.Chart(vdf.sort_values("Administered")).mark_bar().encode(
            x=alt.X('State', sort=alt.SortField(field="Administered", order="descending")),
            y=alt.Y("Administered"),
            tooltip=["State", "Administered"]
        ).properties(width=700, height=500))